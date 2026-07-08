"""7-step sequential wealth prompt chain orchestrator."""
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from agents.llm_telemetry import record_llm_event
from agents.pii_masker import format_customer_facts_masked, mask_snapshot_for_llm, mask_text_for_llm
from agents.wealth_chain.auditor import merge_auditor_result, run_programmatic_checks
from agents.wealth_chain.cache import get_step1_cached, set_step1_cached
from agents.wealth_chain.mock_chain import build_mock_chain, prior_steps_json
from agents.wealth_chain.prompt_loader import render_prompt
from agents.wealth_chain.schemas import (
    AuditDecision,
    ChainMetadata,
    ChainState,
    Step1Output,
    Step2Output,
    Step3Output,
    Step4Output,
    Step5Output,
    Step6Output,
    Step7Output,
)

_CLIENT = None
MODEL = "claude-3-5-sonnet-20241022"
MAX_REVISE_LOOPS = 2

STEP_FILES = [
    "step1_wealth_analyst.md",
    "step2_goal_architect.md",
    "step3_portfolio_strategist.md",
    "step4_red_team.md",
    "step5_blue_team.md",
    "step6_wealth_avatar.md",
    "step7_master_auditor.md",
]

STEP_MODELS = [Step1Output, Step2Output, Step3Output, Step4Output, Step5Output, Step6Output, Step7Output]


def _get_client():
    global _CLIENT
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    if _CLIENT is None:
        from anthropic import AsyncAnthropic
        _CLIENT = AsyncAnthropic(api_key=api_key)
    return _CLIENT


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def _call_step(
    step_index: int,
  system_prompt: str,
    user_payload: str,
    customer_id: Optional[str],
) -> Optional[dict]:
    client = _get_client()
    if not client:
        return None
    try:
        message = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": user_payload}],
        )
        raw = message.content[0].text
        record_llm_event(f"wealth_chain_step_{step_index}", success=True, model=MODEL, customer_id=customer_id)
        return _parse_json_response(raw)
    except Exception as e:
        record_llm_event(
            f"wealth_chain_step_{step_index}",
            success=False,
            model=MODEL,
            error=str(e),
            customer_id=customer_id,
        )
        return None


def _build_context(
    snapshot: Dict[str, Any],
    signals: Dict[str, Any],
    recommendation: Dict[str, Any],
    product_catalog: str,
    state: ChainState,
    user_text: str,
) -> Dict[str, str]:
    masked_snap = mask_snapshot_for_llm(snapshot)
    return {
        "PYTHON_FACTS": format_customer_facts_masked(snapshot, signals),
        "CUSTOMER_SNAPSHOT": json.dumps(masked_snap, indent=2),
        "PRIOR_STEPS_JSON": prior_steps_json(state),
        "BANK_PRODUCT_CATALOG": product_catalog,
        "RULES_ENGINE_RECOMMENDATION": json.dumps(recommendation, indent=2),
        "USER_MESSAGE": mask_text_for_llm(user_text),
        "PROGRAMMATIC_CHECKS": "[]",
    }


async def _run_steps_llm(
    snapshot: Dict[str, Any],
    signals: Dict[str, Any],
    recommendation: Dict[str, Any],
    product_catalog: str,
    user_text: str,
    customer_id: str,
    fix_targets: Optional[List[int]] = None,
) -> ChainState:
    state = ChainState(plan_id=f"plan_{uuid.uuid4().hex[:12]}")
    fix_targets = fix_targets or list(range(1, 8))
    ctx = _build_context(snapshot, signals, recommendation, product_catalog, state, user_text)

    cached = get_step1_cached(customer_id, snapshot)
    if cached and 1 in fix_targets:
        state.step1 = Step1Output(**cached)
    elif 1 in fix_targets:
        prompt = render_prompt(STEP_FILES[0], **ctx)
        data = await _call_step(1, prompt, "Produce Step 1 JSON.", customer_id)
        if data:
            state.step1 = Step1Output(**data)
            set_step1_cached(customer_id, snapshot, state.step1.model_dump())

    for idx in range(2, 7):
        if idx not in fix_targets:
            continue
        ctx = _build_context(snapshot, signals, recommendation, product_catalog, state, user_text)
        prompt = render_prompt(STEP_FILES[idx - 1], **ctx)
        data = await _call_step(idx, prompt, f"Produce Step {idx} JSON.", customer_id)
        if data:
            model = STEP_MODELS[idx - 1]
            setattr(state, f"step{idx}", model(**data))

    checks, prog_conf = run_programmatic_checks(
        state, snapshot, signals, recommendation,
        [p["product_id"] for p in json.loads(product_catalog)] if product_catalog.startswith("[") else [],
    )
    ctx = _build_context(snapshot, signals, recommendation, product_catalog, state, user_text)
    ctx["PROGRAMMATIC_CHECKS"] = json.dumps([c.model_dump() for c in checks], indent=2)
    prompt = render_prompt(STEP_FILES[6], **ctx)
    data = await _call_step(7, prompt, "Produce Step 7 audit JSON.", customer_id)
    llm7 = Step7Output(**data) if data else None
    state.step7 = merge_auditor_result(checks, prog_conf, llm7)

    for i in range(1, 8):
        step = getattr(state, f"step{i}", None)
        if step:
            state.raw_steps[f"step{i}"] = step.model_dump()
    return state


# Plan store for GET /v1/wealth/plan/{id}
_PLAN_STORE: Dict[str, ChainState] = {}


def store_plan(state: ChainState) -> None:
    _PLAN_STORE[state.plan_id] = state
    if len(_PLAN_STORE) > 500:
        oldest = next(iter(_PLAN_STORE))
        _PLAN_STORE.pop(oldest, None)


def get_plan(plan_id: str) -> Optional[ChainState]:
    return _PLAN_STORE.get(plan_id)


async def run_wealth_chain(
    snapshot: Dict[str, Any],
    signals: Dict[str, Any],
    recommendation: Dict[str, Any],
    product_catalog: str,
    user_text: str,
    customer_id: str,
) -> Tuple[ChainState, ChainMetadata]:
    revise_loops = 0
    fix_targets: Optional[List[int]] = None
    state: Optional[ChainState] = None

    while revise_loops <= MAX_REVISE_LOOPS:
        client = _get_client()
        if client:
            state = await _run_steps_llm(
                snapshot, signals, recommendation, product_catalog,
                user_text, customer_id, fix_targets,
            )
        else:
            checks, _ = run_programmatic_checks(
                state or ChainState(),
                snapshot,
                signals,
                recommendation,
                [],
            )
            state = build_mock_chain(snapshot, signals, recommendation, user_text, checks)

        if not state.step7:
            checks, prog_conf = run_programmatic_checks(state, snapshot, signals, recommendation, [])
            state.step7 = merge_auditor_result(checks, prog_conf, None)

        decision = state.step7.decision
        if decision == AuditDecision.APPROVE or decision == AuditDecision.REJECT:
            break
        if decision == AuditDecision.REVISE and state.step7.fix_targets and revise_loops < MAX_REVISE_LOOPS:
            fix_targets = state.step7.fix_targets
            revise_loops += 1
            continue
        break

    store_plan(state)
    meta = ChainMetadata(
        confidence=state.step7.confidence if state.step7 else 0,
        decision=state.step7.decision.value if state.step7 else "reject",
        steps_completed=sum(1 for i in range(1, 8) if getattr(state, f"step{i}", None)),
        plan_id=state.plan_id,
        revise_loops=revise_loops,
        path="deep",
    )
    record_llm_event(
        "wealth_chain_complete",
        success=state.step7.decision != AuditDecision.REJECT if state.step7 else False,
        model=MODEL if _get_client() else "mock_chain",
        customer_id=customer_id,
        extra={"confidence": meta.confidence, "decision": meta.decision},
    )
    return state, meta

"""Deterministic chain outputs when LLM API is unavailable."""
import json
import uuid
from typing import Any, Dict, List

from agents.wealth_chain.schemas import (
    Allocation,
    AuditCheck,
    AuditDecision,
    ChainState,
    Nudge,
    ObjectionHandler,
    RedFlag,
    SmartGoal,
    Step1Output,
    Step2Output,
    Step3Output,
    Step4Output,
    Step5Output,
    Step6Output,
    Step7Output,
)


def _goals_from_snapshot(snapshot: Dict[str, Any]) -> List[SmartGoal]:
    goals = []
    for g in snapshot.get("goals", []):
        target = float(g.get("targetAmount", 1))
        current = float(g.get("currentAmount", 0))
        score = min(100.0, round((current / target) * 100, 1)) if target else 50.0
        goals.append(
            SmartGoal(
                goal_id=g.get("goalId", "goal_unknown"),
                name=g.get("name", "Goal"),
                target_amount=target,
                current_amount=current,
                target_date=g.get("targetDate", ""),
                monthly_sip_required=max(0, (target - current) / 24),
                feasibility_score=score,
            )
        )
    return goals


def build_mock_chain(
    snapshot: Dict[str, Any],
    signals: Dict[str, Any],
    recommendation: Dict[str, Any],
    user_text: str,
    programmatic_checks: List[AuditCheck],
) -> ChainState:
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    risk = snapshot.get("riskProfile", "Moderate")
    savings_rate = float(signals.get("savings_rate", 0.22))
    category_totals = signals.get("category_totals", {})

    red_flags = []
    if signals.get("dining_delta", 0) > 2000:
        red_flags.append(
            RedFlag(
                code="DINING_SPIKE",
                severity="medium",
                description="Dining spend increased vs prior month",
            )
        )
    if savings_rate < 0.1:
        red_flags.append(
            RedFlag(
                code="LOW_SAVINGS",
                severity="high",
                description="Savings rate below 10%",
            )
        )

    step1 = Step1Output(
        risk_profile=risk,
        income_stability="stable",
        red_flags=red_flags,
        category_breakdown={k: float(v) for k, v in category_totals.items()},
        savings_rate=savings_rate,
        summary=f"Customer shows {round(savings_rate*100,1)}% savings rate with {risk} risk profile.",
    )

    step2 = Step2Output(
        goals=_goals_from_snapshot(snapshot),
        goal_hierarchy_notes="Prioritise near-term goals with adequate emergency buffer.",
    )

    allocations = [
        Allocation(
            product_id="MF_HYBRID_001",
            product_name="Hybrid Equity Fund",
            allocation_pct=40.0,
            rationale="Moderate risk growth aligned to 2-3 year goals",
        ),
        Allocation(
            product_id="FD_HDFC_001",
            product_name="HDFC Fixed Deposit",
            allocation_pct=35.0,
            rationale="Capital preservation component",
        ),
        Allocation(
            product_id="SAVINGS_LIQUID",
            product_name="Liquid Savings",
            allocation_pct=25.0,
            rationale="Emergency liquidity buffer",
        ),
    ]
    if recommendation.get("reasonCode") == "DORMANT_FD_REALLOCATION":
        allocations[1].rationale = "Review dormant FD per rules engine"

    step3 = Step3Output(
        allocations=allocations,
        tax_notes=["Consider ELSS only for 3+ year horizons under Section 80C"],
        sebi_disclaimer="This is personalised information and guidance, not regulated investment advice.",
    )

    step4 = Step4Output(
        risks=["Market volatility on equity portion", "Goal timeline pressure on vacation fund"],
        portfolio_flaws=["FD concentration if dormant", "Vacation goal underfunded"],
        behavioral_traps=["Lifestyle creep from dining spend", "Delaying RM consult on big decisions"],
    )

    step5 = Step5Output(
        nudges=[
            Nudge(
                trigger="dining_delta_high",
                message="Weekday lunch spend is up — review if intentional",
                channel="in_app",
            )
        ],
        automation_rules=["Auto-sweep surplus above 3x expenses to liquid fund"],
        defense_protocols=["Maintain 3-6 month emergency fund", "Annual insurance review"],
    )

    script = (
        f"Aapne is mahine {round(savings_rate*100,1)}% bachaya — yeh acchi habit hai. "
        f"Aapke goals ko dekh kar main ek balanced mix suggest karti hoon. "
        "Koi bhi final investment decision ke liye aap apne RM se baat kar sakte hain."
    )
    if "plan" in user_text.lower() or "portfolio" in user_text.lower():
        script = (
            f"Based on your {risk} profile and {round(savings_rate*100,1)}% savings rate, "
            "I've prepared a balanced allocation across hybrid fund, FD, and liquid savings. "
            "This is guidance — your RM can confirm before any action."
        )

    step6 = Step6Output(
        avatar_script=script,
        objection_handlers=[
            ObjectionHandler(
                objection="Is this guaranteed?",
                response="No returns are guaranteed; I share historical ranges and risks only.",
            )
        ],
        disclosures=[step3.sebi_disclaimer, "Past performance does not guarantee future results."],
        language="hi" if any(w in user_text.lower() for w in ("theek", "kya", "aap", "hindi")) else "en",
    )

    passed = sum(1 for c in programmatic_checks if c.passed)
    confidence = round((passed / max(len(programmatic_checks), 1)) * 100, 1)
    decision = AuditDecision.APPROVE if confidence >= 85 else (
        AuditDecision.REVISE if confidence >= 70 else AuditDecision.REJECT
    )

    step7 = Step7Output(
        decision=decision,
        confidence=confidence,
        checks=programmatic_checks,
        fix_targets=[3, 6] if decision == AuditDecision.REVISE else [],
        customer_summary="Audited wealth plan ready for customer review.",
        rejection_reason="Confidence below threshold — escalate to RM" if decision == AuditDecision.REJECT else None,
    )

    state = ChainState(
        step1=step1,
        step2=step2,
        step3=step3,
        step4=step4,
        step5=step5,
        step6=step6,
        step7=step7,
        plan_id=plan_id,
        raw_steps={
            "step1": step1.model_dump(),
            "step2": step2.model_dump(),
            "step3": step3.model_dump(),
            "step4": step4.model_dump(),
            "step5": step5.model_dump(),
            "step6": step6.model_dump(),
            "step7": step7.model_dump(),
        },
    )
    return state


def prior_steps_json(state: ChainState) -> str:
    data = {}
    for i in range(1, 8):
        step = getattr(state, f"step{i}", None)
        if step is not None:
            data[f"step{i}"] = step.model_dump()
    return json.dumps(data, indent=2)

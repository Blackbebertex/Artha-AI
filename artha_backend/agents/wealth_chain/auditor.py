"""Programmatic Master Auditor checks (Step 7 pre-LLM validation)."""
import re
from typing import Any, Dict, List, Tuple

from agents.wealth_chain.schemas import AuditCheck, ChainState, Step3Output


def _extract_numbers(text: str) -> List[float]:
    nums = re.findall(r"[\d,]+\.?\d*", text.replace(",", ""))
    result = []
    for n in nums:
        try:
            result.append(float(n))
        except ValueError:
            pass
    return result


def run_programmatic_checks(
    state: ChainState,
    snapshot: Dict[str, Any],
    signals: Dict[str, Any],
    recommendation: Dict[str, Any],
    allowed_product_ids: List[str],
) -> Tuple[List[AuditCheck], float]:
    checks: List[AuditCheck] = []
    step1 = state.step1
    step3 = state.step3
    step4 = state.step4
    step5 = state.step5
    step6 = state.step6

    # 1. Portfolio vs risk profile
    risk = (step1.risk_profile if step1 else snapshot.get("riskProfile", "")).lower()
    equity_pct = 0.0
    if step3:
        for alloc in step3.allocations:
            if "equity" in alloc.product_name.lower() or "hybrid" in alloc.product_name.lower():
                equity_pct += alloc.allocation_pct
    risk_ok = (risk == "conservative" and equity_pct <= 40) or (
        risk in ("moderate", "growth") and equity_pct <= 70
    )
    checks.append(
        AuditCheck(
            name="portfolio_risk_alignment",
            passed=risk_ok,
            detail=f"Equity/hybrid allocation {equity_pct}% for {risk} profile",
        )
    )

    # 2. SIP coverage vs goals
    sip_ok = True
    if state.step2 and state.step2.goals:
        for g in state.step2.goals:
            if g.feasibility_score < 30 and g.monthly_sip_required > 0:
                sip_ok = False
    checks.append(
        AuditCheck(
            name="goal_sip_coverage",
            passed=sip_ok,
            detail="Goals with low feasibility flagged for SIP review",
        )
    )

    # 3. Blue covers Red
    blue_covers = True
    if step4 and step5:
        if step4.risks and not step5.defense_protocols:
            blue_covers = False
    checks.append(
        AuditCheck(
            name="blue_covers_red",
            passed=blue_covers,
            detail="Blue team defenses present for red team risks",
        )
    )

    # 4. Avatar numbers grounded
    grounded = True
    if step6:
        known = set(_extract_numbers(str(signals)))
        known.update(_extract_numbers(str(snapshot.get("savings", 0))))
        if step1:
            known.add(round(step1.savings_rate * 100, 1))
        avatar_nums = _extract_numbers(step6.avatar_script)
        for n in avatar_nums:
            if n > 1000 and n not in known and round(n, 1) not in known:
                grounded = False
                break
    checks.append(
        AuditCheck(
            name="avatar_number_grounding",
            passed=grounded,
            detail="Avatar script numbers traceable to facts",
        )
    )

    # 5. SEBI disclosure
    sebi_ok = False
    if step3 and step3.sebi_disclaimer:
        sebi_ok = True
    if step6 and step6.disclosures:
        sebi_ok = sebi_ok or any("advice" in d.lower() or "sebi" in d.lower() for d in step6.disclosures)
    checks.append(
        AuditCheck(name="sebi_disclosure", passed=sebi_ok, detail="SEBI positioning disclaimer present")
    )

    # 6. Cross-step contradictions
    no_contradiction = True
    if step3 and step1:
        total_alloc = sum(a.allocation_pct for a in step3.allocations)
        if total_alloc < 95 or total_alloc > 105:
            no_contradiction = False
    checks.append(
        AuditCheck(
            name="contradiction_scan",
            passed=no_contradiction,
            detail="Allocation totals and step consistency",
        )
    )

    # 7. CAGR optimism (short-term goals < 8% assumed return)
    cagr_ok = True
    if step3:
        for alloc in step3.allocations:
            if "11%" in alloc.rationale or "12%" in alloc.rationale:
                for g in (state.step2.goals if state.step2 else []):
                    if g.feasibility_score < 50:
                        cagr_ok = False
    checks.append(
        AuditCheck(name="cagr_optimism_filter", passed=cagr_ok, detail="No aggressive return assumptions on short goals")
    )

    # 8. Insurance gap
    insurance_ok = bool(step5 and any("insurance" in p.lower() for p in step5.defense_protocols))
    checks.append(
        AuditCheck(name="insurance_gap", passed=insurance_ok, detail="Term/health insurance review recommended")
    )

    # Rules engine consistency
    rules_ok = True
    if recommendation.get("reasonCode") and step3:
        reason = recommendation.get("reasonCode", "")
        if reason == "DORMANT_FD_REALLOCATION":
            rules_ok = any("fd" in a.rationale.lower() or "dormant" in a.rationale.lower() for a in step3.allocations)
    checks.append(
        AuditCheck(
            name="rules_engine_consistency",
            passed=rules_ok,
            detail=f"Aligns with rules engine: {recommendation.get('reasonCode', 'none')}",
        )
    )

    # Product catalog constraint
    catalog_ok = True
    if step3 and allowed_product_ids:
        for a in step3.allocations:
            if a.product_id not in allowed_product_ids:
                catalog_ok = False
    checks.append(
        AuditCheck(name="approved_products_only", passed=catalog_ok, detail="Allocations use bank catalog IDs")
    )

    passed_count = sum(1 for c in checks if c.passed)
    confidence = round((passed_count / len(checks)) * 100, 1)
    return checks, confidence


def merge_auditor_result(programmatic: List[AuditCheck], prog_confidence: float, llm_step7: Any = None):
    from agents.wealth_chain.schemas import AuditDecision, Step7Output

    if llm_step7 and isinstance(llm_step7, Step7Output):
        merged_confidence = round((prog_confidence + llm_step7.confidence) / 2, 1)
        decision = llm_step7.decision
        if merged_confidence >= 85:
            decision = AuditDecision.APPROVE
        elif merged_confidence >= 70:
            decision = AuditDecision.REVISE
        else:
            decision = AuditDecision.REJECT
        return Step7Output(
            decision=decision,
            confidence=merged_confidence,
            checks=programmatic + llm_step7.checks,
            fix_targets=llm_step7.fix_targets,
            customer_summary=llm_step7.customer_summary,
            rejection_reason=llm_step7.rejection_reason,
        )

    decision = AuditDecision.APPROVE if prog_confidence >= 85 else (
        AuditDecision.REVISE if prog_confidence >= 70 else AuditDecision.REJECT
    )
    return Step7Output(
        decision=decision,
        confidence=prog_confidence,
        checks=programmatic,
        fix_targets=[3, 6] if decision == AuditDecision.REVISE else [],
        customer_summary="Programmatic audit complete.",
        rejection_reason="Below confidence threshold" if decision == AuditDecision.REJECT else None,
    )

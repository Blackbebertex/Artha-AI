# Phase 6 — Security & Compliance Documentation

**Parent:** [10-security-zero-trust.md](../10-security-zero-trust.md)  
**Legacy Sources:** `phase_1_deliverables/06_compliance_policy_matrix.md`, `phase_1_deliverables/10_ai_guardrail_policy.md`

## Full Security Documentation

See [10-security-zero-trust.md](../10-security-zero-trust.md) for:

- 6.1 Authentication Design
- 6.2 Authorization Matrix
- 6.3 Security Controls
- 6.4 Data Protection
- 6.5 Zero Trust Architecture
- 6.6 Compliance Mapping (RBI AA, SEBI, DPDP, NIST AI RMF)
- 6.7 Threat Model

## Guardrail Policy Cross-Reference

| Policy (phase_1 doc) | Code Implementation | Gap |
| -------------------- | ------------------- | --- |
| Input Shield | compliance_guardrails.py | ✅ |
| Output Shield | compliance_guardrails.py | ✅ |
| PII Masking | Documented only | ❌ Not in ai_orchestrator.py |

## Red Team / Blue Team (mds phase_3)

| Team | Implementation | Doc Reference |
| ---- | -------------- | ------------- |
| Red Team | Manual test scenarios in mds/phase_3_09 | 14-qa-reliability-chaos.md |
| Blue Team | Guardrails + unit tests | test_real_compliance_guardrails |

## Compliance Positioning Statement

ARTHA AI provides **personalised information and guidance**, not regulated investment advice. Decisions requiring licensed advice are routed to human relationship managers or existing bank-authorised distribution flows.

`[OBSERVED: Blueprint Section 8, ai_orchestrator system prompt]`

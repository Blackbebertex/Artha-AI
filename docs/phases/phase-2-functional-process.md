# Phase 2 — Functional & Process Documentation

**Parent:** [05-functional-decomposition.md](../05-functional-decomposition.md), [06-process-flow-diagrams.md](../06-process-flow-diagrams.md)  
**Legacy Sources:** `mds/phase_2_mvp_build.md`, `mds/detailed_modules/phase_2_*`

## Module Build Status

| Module (mds) | Code Location | Status |
| ------------ | ------------- | ------ |
| Mobile module | artha_frontend/ | ✅ Demo shell |
| Gateway & session | main.py | ✅ Implemented |
| Consent service | services/consent_service.py | ✅ |
| Customer snapshot | services/customer_snapshot.py | ✅ |
| Behaviour engine | services/behaviour_engine.py | ✅ |
| Advisory engine | services/advisory_engine.py | ✅ |
| RAG knowledge base | agents/rag_knowledge_base.py | ✅ Keyword mode |
| AI orchestrator | agents/ai_orchestrator.py | ✅ |
| Compliance guardrails | agents/compliance_guardrails.py | ✅ |
| Avatar & voice | agents/avatar_voice.py | ✅ Mock visemes |
| RM handoff | services/rm_handoff.py | ✅ Console mock |
| Audit logging | services/audit_logger.py | ✅ |
| Service integration | main.py handle_message | ✅ |

## Detailed Tables

- Functional decomposition matrix → [05 §2.1](../05-functional-decomposition.md#21-functional-decomposition-matrix)
- State transitions → [05 §2.2](../05-functional-decomposition.md#22-state-transition-mapping)
- API-to-UI traceability → [05 §2.5](../05-functional-decomposition.md#25-api-to-ui-traceability-matrix)
- Process flow diagrams → [06](../06-process-flow-diagrams.md)
- Sequence diagrams → [06 §Sequence Diagrams](../06-process-flow-diagrams.md#sequence-diagrams)

## Integration Test Reference

`[OBSERVED: Blueprint Section 20 — recommended e2e test not yet in repo]`

Recommended test (from blueprint):
```python
# Assert DORMANT_FD_REALLOCATION on "how am I doing this month?"
# Partially covered by test_ai_orchestrator in test_services.py
```

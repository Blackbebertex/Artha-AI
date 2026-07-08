# Source Index — Legacy to Enterprise Documentation Mapping

**Purpose:** Traceability between pre-existing project artifacts and the `docs/` enterprise suite.

---

## Consolidation Map

| Legacy File | Enterprise Document(s) | Action |
| ----------- | ---------------------- | ------ |
| `ARTHA_AI_Blueprint.md` | 01, 04, 07, 12, 16 | Referenced; not moved (root canonical product doc) |
| `phase_0_deliverables/03_stakeholder_map.md` | 04, 17 | Consolidated into business architecture |
| `phase_0_deliverables/04_mvp_scope_document.md` | 02, 13 | Consolidated into gap analysis + SRS |
| `phase_0_deliverables/05_success_metrics.md` | 01, 13, 16 | Consolidated into executive summary |
| `phase_0_deliverables/07_project_governance.md` | 04, phases/phase-1 | Consolidated |
| `phase_0_deliverables/09_high_level_architecture.md` | 07, phases/phase-3 | Extended in C4 docs |
| `phase_1_deliverables/01_customer_journeys.md` | 05, 06 | Extended in functional decomposition |
| `phase_1_deliverables/02_personas.md` | 04 | Consolidated in business architecture |
| `phase_1_deliverables/03_data_dictionary.md` | 08, phases/phase-4 | Extended with full entity spec |
| `phase_1_deliverables/04_consent_flows.md` | 06, 10 | Extended in process flows + security |
| `phase_1_deliverables/06_compliance_policy_matrix.md` | 03, 10 | Extended in risk + security |
| `phase_1_deliverables/10_ai_guardrail_policy.md` | 12, 10 | Cross-referenced in AI architecture |
| `mds/phase_*.md` | phases/*, 17 | Roadmap input for action plan |
| `phase_4_5_ops/operations_runbook.md` | 14, 17 | Extended in QA/reliability |
| `phase_4_5_ops/docker-compose.yml` | 07, 09 | Referenced in C4 deployment |
| `artha_backend/requirements.txt` | 09 | Full dependency inventory |
| `artha_backend/data/cust_001.json` | 08 | Core entity exemplar |

---

## Code-to-Documentation Traceability

| Code Path | Primary Doc |
| --------- | ----------- |
| `artha_backend/main.py` | 05, 06, 07, 11 |
| `artha_backend/agents/ai_orchestrator.py` | 12 |
| `artha_backend/agents/rag_knowledge_base.py` | 12 |
| `artha_backend/agents/compliance_guardrails.py` | 10, 12 |
| `artha_backend/agents/avatar_voice.py` | 12 |
| `artha_backend/services/advisory_engine.py` | 05, 12 |
| `artha_backend/services/behaviour_engine.py` | 05, 08 |
| `artha_backend/services/audit_logger.py` | 10, 14 |
| `artha_backend/services/consent_service.py` | 10 |
| `artha_backend/services/rm_handoff.py` | 05, 06 |
| `artha_frontend/script.js` | 05, 11 |
| `artha_backend/tests/test_services.py` | 14 |

---

## Recommended Reading Order by Role

| Role | Documents |
| ---- | --------- |
| Executive / Investor | 01 → 02 → 16 → 17 |
| Solution Architect | 00 → 07 → 08 → 12 |
| Backend Engineer | 05 → 11 → 09 → 12 |
| Frontend Engineer | 05 → 11 → 06 |
| Security / Compliance | 00 → 03 → 10 → 12 |
| QA / SRE | 14 → 06 → 13 |
| AI Engineer | 00 → 12 → 10 |

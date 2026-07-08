# 17 — Immediate Action Plan

**Document ID:** ARTHA-DOC-17  
**Phase:** 13 — Action Plan and Handoff

---

## 13.1 Monday Morning Priorities (Top 5)

| # | Action | Owner | Effort | Impact |
| - | ------ | ----- | ------ | ------ |
| 1 | **Fix CI pipeline** — move `phase_4_5_ops/.github/workflows/ci_cd.yml` to `.github/workflows/` (or update root `python-app.yml` to run `python -m unittest discover -s artha_backend/tests`) | DevOps | 2 hours | Unblocks quality gate |
| 2 | **Implement PII masking** in `ai_orchestrator.py` before LLM calls | AI/Backend | 1 day | Unblocks compliance review |
| 3 | **Add LLM fallback telemetry** — log when keyword mock activates | Backend | 4 hours | Fixes Ghost Mode risk |
| 4 | **Wire Redis for sessions** — replace SESSION_HISTORIES dict | Platform | 2 days | Unblocks restart safety |
| 5 | **Export OpenAPI spec** to `docs/openapi.json` from running FastAPI | Backend | 1 hour | API contract truth |

---

## 13.2 30-60-90 Day Plan

| Period | Technical Goals | Business Goals | Risk Mitigation |
| ------ | --------------- | -------------- | --------------- |
| **30 days** | CI fix, PII masking, Redis sessions, integration tests, observability baseline (structured logs) | Compliance review of AI positioning | Close R-002, R-003, R-006, R-009 |
| **60 days** | PostgreSQL migration, pgvector RAG, JWT auth stub, AA sandbox integration, E2E Playwright tests | Single design partner bank identified | Close R-007, R-010; begin pilot prep |
| **90 days** | Kubernetes manifests, rate limiting, semantic guardrails, LLM eval harness in CI, CRM handoff API | Branch pilot UAT with 50 customers | Close R-004, R-008; human-in-the-loop review queue |

---

## 13.3 Stakeholder Handoff Matrix

| Role | Key Deliverables | Critical Context | Next Actions |
| ---- | ---------------- | ---------------- | ------------ |
| **CTO** | docs/07, docs/12, docs/17 | Monolith MVP; microservices are target | Approve 30-day hardening sprint |
| **Engineering Manager** | docs/05, docs/09, docs/14 | 12 unit tests; CI broken | Fix CI; assign Redis/Postgres stories |
| **Lead Developer** | artha_backend/, docs/11 | handle_message is compliance-critical path | PII masking PR; integration tests |
| **QA Lead** | docs/14, mds/phase_3 | Smoke tests defined; no E2E automation | Implement SM-01 to SM-12 in Playwright |
| **DevOps Engineer** | phase_4_5_ops/, docs/09 | Docker Compose works; no staging env | CI fix; staging environment |
| **CISO** | docs/03, docs/10 | Guardrails exist; auth is demo-only | Security review before pilot |
| **CFO** | docs/16 | Monetization inferred, not documented | Define pricing model with product |
| **AI Lead** | docs/12, phase_1/10 | Rules-before-LLM is invariant | Vector RAG + eval harness |
| **Legal/Compliance** | docs/03, docs/10, Blueprint §8 | SEBI boundary positioning documented | Formal opinion on advice vs. guidance |
| **Investors/Partners** | docs/01, docs/16 | MVP demo-ready; production needs 90 days | Schedule live demo with Section 11 script |

---

## Sprint Breakdown (30-Day)

### Week 1: Quality & Visibility
- Fix GitHub Actions test path
- Add structured JSON logging
- Export OpenAPI spec
- Document environment variables

### Week 2: Security & Compliance
- PII masking in orchestrator
- Consent check on snapshot endpoint
- Rate limiting middleware
- Security test plan execution

### Week 3: Infrastructure
- Redis session store
- PostgreSQL schema design
- Alembic migration from cust_001.json
- Docker Compose add Redis + Postgres

### Week 4: Testing & Hardening
- httpx integration tests for all endpoints
- Playwright E2E for demo script
- LLM fallback indicator in UI
- Compliance sign-off package

---

## Definition of Done (Pilot Ready)

- [ ] All SM-01 to SM-12 smoke tests automated in CI
- [ ] PII masked in all LLM prompts
- [ ] Sessions persist across restarts (Redis)
- [ ] Customer data in PostgreSQL with backup
- [ ] AA sandbox returning real consent flow
- [ ] Audit logs shipped to SIEM
- [ ] Legal sign-off on SEBI positioning
- [ ] SLO dashboards operational

---

## Lens Summary

| Lens | Action Driver |
| ---- | ------------- |
| **DOA** | Items 1–4 in Monday priorities are production blockers |
| **Red Team** | PII masking is P0 |
| **Ghost Mode** | Fallback telemetry is P0 |

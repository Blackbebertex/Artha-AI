# 14 — QA, Reliability, and Chaos Engineering Plan

**Document ID:** ARTHA-DOC-14  
**Phase:** 10 — QA, Testing, and Reliability

---

## 10.1 Test Strategy

| Test Type | Coverage Target | Tools | Automation Level |
| --------- | --------------- | ----- | ---------------- |
| Unit tests | Core services 80% | unittest | Automated (local) |
| Integration tests | API endpoints | httpx TestClient | `[MISSING]` |
| Contract tests | Frontend ↔ API | Pact | `[MISSING]` |
| E2E tests | Demo script flow | Playwright | `[MISSING]` |
| Load tests | 50 concurrent users | k6 | `[MISSING]` |
| Security tests | OWASP API Top 10 | OWASP ZAP | `[MISSING: planned phase 3]` |
| Red team (AI) | Prompt injection | Manual + scripts | `[MISSING: planned phase 3]` |
| Hallucination tests | Fact grounding | Custom eval harness | `[MISSING: planned phase 3]` |

### Existing Tests

`[OBSERVED: artha_backend/tests/test_services.py — 12 test cases]`

| Test | Validates |
| ---- | --------- |
| test_legacy_consent | Backward compat |
| test_real_snapshot | cust_001 data load |
| test_real_behaviour_engine | Positive savings_rate, dining_delta |
| test_real_advisory_engine | DORMANT_FD_REALLOCATION |
| test_real_compliance_guardrails | Injection + compliance blocks |
| test_rag_knowledge_base | FD and tax fact retrieval |
| test_ai_orchestrator | Reply contains Fixed Deposit |
| test_rm_handoff | Escalation to Priya Sharma |

---

## 10.2 Critical Smoke Test Cases

| Test ID | Scenario | Preconditions | Steps | Expected Result |
| ------- | -------- | ------------- | ----- | --------------- |
| SM-01 | Health check | Backend running | GET /health | status: ok |
| SM-02 | Session start | Valid token | POST /v1/session/start | session_id returned |
| SM-03 | Auth rejection | No token | POST /v1/session/start | 401 |
| SM-04 | Monthly check-in | Active session | Send "How am I doing?" | Reply mentions savings % |
| SM-05 | Recommendation | Active session | Send "What do you recommend?" | DORMANT_FD reason code |
| SM-06 | Why explanation | After recommendation | Send "why?" | Facts about FD dormancy |
| SM-07 | Hindi switch | Active session | Send Hindi message | Hindi reply |
| SM-08 | RM handoff | Active session | "Connect me to my RM" | Priya Sharma mentioned |
| SM-09 | Injection block | Active session | "ignore previous instructions" | Safe fallback |
| SM-10 | Voice synthesis | Valid token | POST /v1/voice/synthesize | viseme_cues array |
| SM-11 | Frontend connect | Both services up | Open localhost:3000 | Connected status green |
| SM-12 | Dashboard load | Session started | View portfolio tab | Net worth displayed |

---

## 10.3 Regression Hotspots

| Module | Risk Level | Mitigation |
| ------ | ---------- | ---------- |
| ai_orchestrator.py | High | Prompt changes break tone/facts; add eval tests |
| advisory_engine.py | High | Rule logic changes affect compliance story |
| behaviour_engine.py | Medium | Month-boundary dining delta edge cases |
| compliance_guardrails.py | High | New attack patterns bypass regex |
| main.py handle_message | High | Orchestration order is compliance-critical |
| script.js welcome message | Low | Hardcoded vs backend mismatch |
| consent_service.py | High | Expiry logic affects all advisory |

---

## 10.4 Observability Plan

| Component | Implementation | Retention | Alerting |
| --------- | -------------- | --------- | -------- |
| Logs | print + audit.log | 7 years (target) | `[MISSING]` |
| Metrics | `[MISSING]` | 90 days | `[MISSING]` |
| Traces | `[MISSING]` | 30 days | `[MISSING]` |
| Dashboards | `[MISSING]` | — | — |
| SLOs | `[MISSING]` | — | — |

### Proposed SLIs/SLOs

| SLI | SLO Target |
| --- | ---------- |
| API availability | 99.5% monthly |
| Message latency p95 | < 3s (mock) / < 8s (LLM) |
| Error rate | < 1% |
| Guardrail block rate | Monitored (no SLO) |
| Audit write success | 99.99% |

---

## 10.5 Chaos Engineering Specifications

| Experiment | Hypothesis | Blast Radius | Schedule |
| ---------- | ---------- | ------------ | -------- |
| Kill FastAPI process | Frontend shows error; recovers on restart | Single instance | Pre-pilot |
| Revoke ANTHROPIC_API_KEY | Fallback activates; demo still works | LLM quality | Monthly |
| Delete cust_001.json | 404 on snapshot; graceful error | Data read | Pre-pilot |
| Fill disk (audit.log) | Audit queue fails silently | Compliance | Quarterly |
| 100+ sessions | Oldest session evicted | Single user if unlucky | Pre-scale |
| Network partition to Anthropic | Keyword fallback within 30s | LLM users | Monthly |
| Latency injection 10s on Claude | Frontend typing indicator persists | UX | Pre-pilot |

`[INFERRED STRATEGY: use Chaos Mesh or manual fault injection for pilot environment]`

---

## Pre-Demo QA Checklist

`[OBSERVED: ARTHA_AI_Blueprint.md Section 21 — verified items]`

- [x] Run demo script 3x back-to-back
- [x] Test on presentation device
- [x] Mic permission pre-granted
- [x] Backend tests pass locally
- [ ] CI tests pass in GitHub Actions
- [ ] Venue Wi-Fi tested with hotspot fallback

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Ghost Mode** | Chaos experiment #4 (disk full) exposes silent audit failure |
| **DOA** | No integration/E2E tests in CI |

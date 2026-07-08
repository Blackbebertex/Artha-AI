# 13 — System Requirements Specification

**Document ID:** ARTHA-DOC-13  
**Phases:** 8–9 — System Requirements and Delivery Planning

---

## 8.1 Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
| -- | ----------- | -------- | ------------------- |
| FR-01 | System shall authenticate API requests via Bearer token | P0 | 401 returned for invalid/missing token |
| FR-02 | System shall create isolated conversation sessions | P0 | Unique session_id returned on start |
| FR-03 | System shall enforce data consent before advisory access | P0 | Consent denial message when consent invalid/expired |
| FR-04 | System shall provide 360° customer financial snapshot | P0 | Accounts, goals, transactions returned for cust_001 |
| FR-05 | System shall compute behavioural signals from transactions | P0 | savings_rate and dining_delta calculated dynamically |
| FR-06 | System shall generate reason-coded recommendations | P0 | DORMANT_FD_REALLOCATION fires for cust_001 test data |
| FR-07 | System shall generate natural language replies | P0 | Contextual reply referencing customer facts |
| FR-08 | System shall block prompt injection attempts | P0 | "ignore previous instructions" blocked |
| FR-09 | System shall block non-compliant output language | P0 | "guaranteed returns" blocked |
| FR-10 | System shall support RM escalation on request | P1 | Handoff to Priya Sharma with summary payload |
| FR-11 | System shall log all conversations to audit trail | P0 | audit.log entry with integrity_hash per message |
| FR-12 | System shall provide avatar voice viseme metadata | P1 | viseme_cues array returned from synthesize endpoint |
| FR-13 | Frontend shall display explainable recommendation cards | P1 | reasonCode and facts rendered in expandable card |
| FR-14 | Frontend shall detect Hindi/English language switch | P1 | Language chip updates; Hindi reply generated |
| FR-15 | System shall accept recommendation feedback | P2 | POST feedback logged to audit |

---

## 8.2 Non-Functional Requirements

| Category | Target | Measurement Method |
| -------- | ------ | ------------------ |
| Latency (mock mode) | p95 < 500ms | Load test on /v1/conversation/message |
| Latency (LLM mode) | p95 < 8s | Anthropic API timing |
| Throughput | 50 concurrent sessions | k6 load test |
| Availability | 99.5% (production target) | Uptime monitoring |
| Durability | Audit log persisted | Verify audit.log append |
| Scalability | 10K DAU (target) | Horizontal pod scaling |
| Accessibility | WCAG 2.1 AA (target) | axe audit on frontend |
| Maintainability | Module separation in monolith | Code review |
| Observability | Structured logs + metrics | `[GAP: not implemented]` |
| Portability | Docker containerized | docker-compose up succeeds |
| Security | OWASP API Top 10 mitigations | Security test phase |

---

## 8.3 Operational Requirements

| Requirement | Target | Implementation |
| ----------- | ------ | -------------- |
| Deployment frequency | Weekly (target) | CI/CD pipeline |
| Rollback time | < 15 minutes | Container image rollback |
| Backup frequency | Daily (target) | `[MISSING]` |
| Log retention | 7 years audit | `[MISSING: local file only]` |
| Alert response time | P1 < 15 min | `[MISSING: on-call]` |
| Health check interval | 30s | GET /health |

---

## 9.1 User Story Map

| Epic | Story | Acceptance Criteria | Priority | Dependencies |
| ---- | ----- | ------------------- | -------- | ------------ |
| Conversational Advisory | As Riya, I want a weekly check-in | Savings rate and SIP status in reply | P0 | FR-05, FR-07 |
| Conversational Advisory | As Riya, I want to know "why" for recommendations | Expandable facts card | P0 | FR-06, FR-13 |
| Multilingual | As Riya, I want to switch to Hindi mid-chat | Hindi reply without manual toggle | P1 | FR-14 |
| Compliance | As compliance, I need audit trail of all advice | audit.log with hashes | P0 | FR-11 |
| Escalation | As Riya, I want to talk to my RM | Handoff confirmation + summary | P1 | FR-10 |
| 360° View | As Riya, I want to see my portfolio | Dashboard with allocation | P0 | FR-04 |
| Spending Insight | As Riya, I want dining spend alerts | Delta shown in insights panel | P1 | FR-05 |
| Voice | As Riya, I want to hear Artha speak | TTS + viseme animation | P2 | FR-12 |

---

## 9.2 Sprint 0 Checklist

| Item | Status |
| ---- | ------ |
| Repository strategy defined | ✅ Monorepo-style (backend + frontend) |
| Coding standards documented | ⚠️ Partial (blueprint only) |
| Branching model selected | `[MISSING]` |
| CI/CD pipeline configured | ⚠️ Partial — tests path broken |
| Infrastructure provisioned | ⚠️ Docker Compose only |
| Secret management in place | ❌ Env vars only |
| Design system approved | ⚠️ CSS variables in style.css |
| API contracts aligned | ✅ Pydantic models in code |
| Monitoring baseline established | ❌ |
| QA environments available | ❌ Local only |

---

## 9.3 Delivery Roadmap

| Phase | Duration | Goals | Team Composition |
| ----- | -------- | ----- | ---------------- |
| MVP (current) | Complete | Demo-ready avatar advisor for Riya persona | Full-stack + AI |
| Stabilization | 3 months | Postgres, Redis, CI fix, PII masking, AA sandbox | Backend + DevOps + Compliance |
| Pilot | 6 months | Single-branch UAT, human-in-the-loop review | + RM ops + Legal |
| Scale | 12 months | Multi-language, RM dashboard, production HA | + SRE + Data platform |

`[OBSERVED: ARTHA_AI_Blueprint.md Section 10]`

---

## Lens Summary

| Lens | Gap |
| ---- | --- |
| **DOA** | NFR observability and backup requirements unmet |
| **Critic Kill** | Sprint 0 checklist ~50% complete |

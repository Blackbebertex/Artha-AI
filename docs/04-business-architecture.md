# 04 — Business Architecture

**Document ID:** ARTHA-DOC-04  
**Phase:** 0 — Business Architecture and Capability Mapping

---

## 0.1 Business Capability Model

| Capability | Description | Supporting Systems | Maturity | Business Impact |
| ---------- | ----------- | ------------------ | -------- | --------------- |
| Personalised Wealth Guidance | Conversational advisory grounded in customer data | AI Orchestrator, Advisory Engine, RAG | MVP | High — core differentiator |
| 360° Financial Visibility | Aggregated view across accounts/institutions | Customer Snapshot, AA (mock) | Prototype | High — trust foundation |
| Behavioural Financial Insight | Spending/savings pattern detection | Behaviour Engine | MVP | Medium — engagement driver |
| Goal Tracking & Progress | Monitor funding status vs. targets | Snapshot + Frontend dashboard | MVP | Medium — retention |
| Explainable Recommendations | Reason-coded, auditable suggestions | Advisory Engine, Rec Card UI | MVP | Critical — compliance |
| Regulatory Boundary Management | Distinguish guidance from licensed advice | Guardrails, RM Handoff | MVP | Critical — license risk |
| Consent & Data Governance | AA-style consent enforcement | Consent Service | MVP | Critical — legal |
| Multilingual Inclusion | Hindi/English code-switch | AI Orchestrator, Frontend detectLang | MVP | High — Tier-2/3 reach |
| Avatar Engagement | Voice + visual persona | Avatar Voice, Frontend visemes | Prototype | Medium — adoption |
| Compliance Audit | Immutable recommendation trail | Audit Logger | MVP | Critical — bank requirement |
| Human Advisor Escalation | RM handoff with context | RM Handoff Service | MVP | High — regulated decisions |

---

## 0.2 Capability-to-Application Mapping

| Business Capability | Application / Service | Owner | Criticality | Notes |
| ------------------- | --------------------- | ----- | ----------- | ----- |
| Personalised Guidance | `agents/ai_orchestrator.py` | AI Team | Critical | Claude + fallback |
| 360° Visibility | `services/customer_snapshot.py` | Data Team | Critical | JSON → Postgres path |
| Behavioural Insight | `services/behaviour_engine.py` | Analytics | High | Deterministic |
| Recommendations | `services/advisory_engine.py` | Advisory | Critical | Rules engine |
| Consent | `services/consent_service.py` | Compliance | Critical | Scope + expiry |
| Audit | `services/audit_logger.py` | Compliance | Critical | Local file today |
| RM Escalation | `services/rm_handoff.py` | Operations | High | Console mock |
| Customer UI | `artha_frontend/` | Frontend | High | Demo shell |
| API Gateway | `artha_backend/main.py` | Platform | Critical | FastAPI monolith |

---

## 0.3 Business Process Heat Map

| Process | Volume | Pain Point | Current Tooling | Automation Potential | Priority |
| ------- | ------ | ---------- | --------------- | -------------------- | -------- |
| Weekly financial check-in | High | RM capacity limits | Manual RM calls | Avatar conversation | P0 |
| Portfolio rebalancing advice | Medium | Generic robo-tools | Static questionnaires | Dynamic behaviour + rules | P0 |
| Spending anomaly detection | High | No connection to advice | Bank statements only | Behaviour engine nudges | P1 |
| Goal drift alerts | Medium | Push notification fatigue | None in MVP | Conversational alerts (roadmap) | P2 |
| Regulated advice decisions | Low | Compliance liability | Human RM | AI flags + handoff | P0 |
| Consent renewal | Low | Manual AA flow | Mock consent | Automated AA lifecycle | P1 |
| Complaint/dispute resolution | Low | No AI audit trail | Manual | Audit log + RM summary | P1 |
| Multilingual support | High | RM language limits | English-default apps | Auto language detect | P0 |

---

## 0.4 Wardley Map Positioning

| Component | Evolution Stage | Strategic Importance | Recommended Action |
| --------- | --------------- | -------------------- | ------------------ |
| FastAPI/HTTP API | Commodity | Low differentiation | Buy — standard |
| LLM (Claude) | Product | Medium | Rent API; evaluate fine-tuning later |
| Rules-based advisory engine | Custom-built | **High — moat** | Build — protect IP |
| Account Aggregator integration | Commodity (in India) | High enabler | Integrate — don't build |
| Keyword RAG knowledge base | Genesis/Custom | Medium | Evolve to vector RAG |
| Avatar TTS/visemes | Commodity | Low | Buy — cloud TTS APIs |
| Compliance guardrails | Custom-built | **High — moat** | Build + certify |
| In-memory session store | Commodity | Low | Buy — Redis |
| Audit logging | Commodity | Medium | Buy — managed SIEM |

---

## Personas (Consolidated from Phase 1)

| Persona | Profile | ARTHA Adaptation | Demo Status |
| ------- | ------- | ---------------- | ----------- |
| **Riya, 27** | First jobber, SIP investor, English chat | Primary demo persona (`cust_001`) | Built |
| **Suresh, 42** | Business owner, irregular income, Hindi/voice | Tone + cash-flow focus | Roadmap |
| **Lata, 61** | Retiree, fraud-wary, regional language | Voice-first, simple UX | Roadmap |

---

## Stakeholder Map

| Stakeholder | Interest | ARTHA Deliverable |
| ----------- | -------- | ----------------- |
| Retail banking customers | Personalised guidance | Avatar conversation |
| Relationship managers | Escalation queue + context | RM handoff payload |
| Compliance/Risk | Audit trail, advice boundary | Guardrails + audit log |
| Bank product/IT | Embeddable module | Frontend SDK path |
| Regulators (RBI/SEBI) | Consent, advice classification | AA + positioning docs |

`[OBSERVED: phase_0_deliverables/03_stakeholder_map.md, Blueprint Section 03]`

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Expose Idea** | Capabilities centre on trustable guidance, not trading |
| **10x** | Rules engine + compliance are the strategic build; LLM is commodity |
| **Wardley** | Invest in custom advisory + guardrails; rent LLM and AA |

# 18 — Assumptions and Inferred Strategies

**Document ID:** ARTHA-DOC-18  
**Audit Lenses:** All lenses synthesized

---

## Documented Assumptions

| ID | Assumption | Type | Confidence | Validation Path |
| -- | ---------- | ---- | ---------- | --------------- |
| AS-01 | Bank will embed ARTHA as WebView/SDK module, not standalone app | Business | High | Bank IT architecture review |
| AS-02 | Account Aggregator is the correct data integration path for India | Regulatory | High | AA sandbox integration test |
| AS-03 | Claude 3.5 Sonnet is acceptable for financial dialogue generation | Technical | Medium | Enterprise AI governance approval |
| AS-04 | Rules-before-LLM pattern satisfies compliance for "guidance" positioning | Regulatory | Medium | Legal counsel opinion |
| AS-05 | 8-turn conversation history is sufficient for check-in use cases | UX | Medium | User research with Riya persona |
| AS-06 | Keyword RAG is adequate for pilot with <20 product facts | Technical | High | Retrieval quality eval |
| AS-07 | Demo-token auth honestly represents future OAuth exchange | Technical | High | Document in all external materials |
| AS-08 | Priya Sharma as static RM is acceptable for demo | Operations | High | Replace with CRM routing at pilot |
| AS-09 | Browser TTS quality is acceptable for initial pilot | UX | Low | User acceptance testing |
| AS-10 | Single monolith can serve pilot scale (<1000 DAU) | Architecture | High | Load test validation |

---

## Inferred Strategies (Where Evidence Is Missing)

### Business Strategy

| Strategy | Rationale |
| -------- | --------- |
| **B2B2C licensing to banks** | Product embeds in bank app; bank owns customer relationship |
| **Land with one persona (Riya), expand to Suresh/Lata** | Blueprint persona strategy; reduces pilot complexity |
| **Compliance as sales enabler** | Indian banking judges and buyers prioritise regulatory awareness |

### Technical Strategy

| Strategy | Rationale |
| -------- | --------- |
| **Evolve monolith → services, not rewrite** | Module boundaries already exist in Python packages |
| **PostgreSQL + pgvector on same instance** | Already in requirements.txt; minimises infra sprawl |
| **Redis for sessions + rate limit counters** | Blueprint specifies Redis; not yet wired |
| **LangGraph evaluation at 6-month mark** | Current linear pipeline sufficient for MVP |
| **Green AI query routing** | Rules/mock for simple queries; LLM only for complex (see doc 15) |

### Security Strategy

| Strategy | Rationale |
| -------- | --------- |
| **Bank OAuth token exchange, not parallel login** | Blueprint Section 16; reduces KYC duplication |
| **Field-level encryption for PII at rest** | DPDP and RBI data norms |
| **WORM audit storage** | 7-year financial services retention standard |
| **Semantic guardrail layer above regex** | Red team findings on bypass risk |

### AI Strategy

| Strategy | Rationale |
| -------- | --------- |
| **Never let LLM select recommendations** | Compliance-critical invariant (ADR-001) |
| **Human-in-the-loop review queue before pilot** | Blueprint Section 10 phase 2 |
| **Eval harness in CI for hallucination regression** | mds phase_3 hallucination testing plan |
| **Surface offline/fallback mode to users** | Ghost Mode finding — transparency builds trust |

### Operational Strategy

| Strategy | Rationale |
| -------- | --------- |
| **Fix CI before any feature work** | False confidence is worse than no CI |
| **Chaos test audit log disk-full scenario** | Silent compliance failure is unacceptable |
| **Pre-generate demo audio for rehearsed script** | Blueprint Section 18 venue Wi-Fi mitigation |

---

## Contradictions Resolved

| Contradiction | Resolution |
| ------------- | ---------- |
| Blueprint says microservices; code is monolith | Document both: MVP monolith, target microservices (doc 07) |
| requirements.txt has Postgres; code uses JSON | Declared deps are target state; JSON is current state (doc 09) |
| Guardrail policy says PII masking; orchestrator sends full PII | Policy is target; implementation gap tracked as R-002 |
| phase_0 architecture lists multi-agent; code is linear | Aspirational architecture; not implemented (doc 12) |

---

## Market Standard Recommendations (No Repo Evidence)

| Area | Recommendation |
| ---- | -------------- |
| API versioning | Maintain `/v1/` for minimum 12 months after `/v2/` launch |
| Feature flags | LaunchDarkly or similar for gradual pilot rollout |
| Incident response | PagerDuty on-call for production pilot |
| Data residency | India region for all PII and financial data |
| Model cards | Document Claude model version, training cutoff, limitations |
| Bias testing | Evaluate advisory rules across personas for fairness |

---

## Lens Synthesis — Final Audit Verdict

| Dimension | Score | Verdict |
| --------- | ----- | ------- |
| Product vision | 9/10 | Clear, differentiated, well-documented |
| Architecture design | 8/10 | Sound patterns; honest about MVP simplification |
| Implementation completeness | 5/10 | Core loop works; infra deps unwired |
| Security & compliance | 4/10 | Foundation exists; critical gaps remain |
| Test & quality | 5/10 | Good unit tests; CI and E2E missing |
| AI governance | 6/10 | Rules-before-LLM strong; guardrails need upgrade |
| Production readiness | 3/10 | Demo-ready; not pilot-ready without 30-day plan |
| Documentation | 9/10 | Comprehensive after this audit suite |

**Overall:** ARTHA AI is a **credible, compliance-aware MVP** with a **clear path to pilot** if the 30-day priorities in [17-immediate-action-plan.md](17-immediate-action-plan.md) are executed. The architectural invariant — **deterministic facts before generative narration** — should be protected through all future scaling decisions.

---

## Glossary

| Term | Definition |
| ---- | ---------- |
| AA | Account Aggregator (RBI framework) |
| FIP | Financial Information Provider |
| FIU | Financial Information User |
| RAG | Retrieval-Augmented Generation |
| RM | Relationship Manager |
| SEBI | Securities and Exchange Board of India |
| DPDP | Digital Personal Data Protection Act, 2023 |
| DOA | Dead on Arrival (audit lens) |

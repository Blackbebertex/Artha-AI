# 02 — Gap Analysis

**Document ID:** ARTHA-DOC-02  
**Audit Lenses:** Autopsy, Critic Kill, DOA

---

## 1.1 Completeness Assessment

| Category | Check | Status | Gap Description |
| -------- | ----- | ------ | --------------- |
| Business | Clear objective defined | ✅ Pass | `[OBSERVED: Blueprint + MVP scope doc]` |
| Business | Monetization model documented | ⚠️ Partial | `[MISSING: explicit revenue model in repo]` |
| Architecture | ADRs exist | ❌ Fail | `[MISSING: no ADR files — inferred in doc 07]` |
| Security | Auth documented | ⚠️ Partial | Demo token only; JWT lib declared unused |
| Engineering | Error handling strategy | ⚠️ Partial | HTTP exceptions; no global handler |
| Engineering | Validation and retry logic | ⚠️ Partial | No retry on Anthropic API failure |
| Engineering | Rollback/compensation logic | ❌ Fail | `[MISSING: no saga/compensation]` |
| Operations | Observability standards | ❌ Fail | `[MISSING: no metrics/traces]` |
| Operations | Logging and alerting | ⚠️ Partial | Console + audit.log only |
| API | Schema and contract defined | ⚠️ Partial | Pydantic models in code; no OpenAPI export doc |
| Data | Normalization strategy | ❌ Fail | Single JSON file, no DB |
| Data | Indexing strategy | ❌ Fail | `[MISSING]` |
| Data | Lineage documented | ⚠️ Partial | Now in doc 08 |
| DevOps | Deployment architecture | ⚠️ Partial | Docker Compose exists; no K8s |
| DevOps | Environment promotion | ❌ Fail | `[MISSING: dev/staging/prod model]` |
| Governance | Dependency governance | ⚠️ Partial | requirements.txt pinned; no Dependabot |
| Quality | Test strategy defined | ⚠️ Partial | Unit tests only; mds reference broader plan |
| Reliability | SLOs/SLIs defined | ❌ Fail | `[MISSING]` |
| Resilience | Chaos testing approach | ❌ Fail | `[MISSING: planned in mds phase 3]` |
| AI | AI governance framework | ⚠️ Partial | Guardrail policy doc + regex implementation |
| Cloud | Multi-cloud exit strategy | ❌ Fail | `[MISSING]` |
| Sustainability | Carbon footprint considered | ❌ Fail | `[MISSING — addressed in doc 15]` |

**Overall completeness score:** ~42% production-ready / ~85% demo-ready

---

## 1.2 Consistency Validation

| Alignment Area | Status | Finding |
| -------------- | ------ | ------- |
| UI flows ↔ backend workflows | ✅ Aligned | Chat, snapshot, recommendations match |
| API contracts ↔ frontend | ⚠️ Gap | Frontend hardcodes welcome message; backend generates dynamically |
| Data model ↔ business rules | ✅ Aligned | FD dormancy rule matches cust_001 data |
| CI/CD ↔ deployment | ❌ Misaligned | Root `.github/workflows/python-app.yml` runs `pytest` at repo root; correct unittest workflow exists at `phase_4_5_ops/.github/workflows/ci_cd.yml` but GitHub only loads workflows from repo-root `.github/workflows/` |
| Dependencies ↔ system goals | ❌ Misaligned | sqlalchemy, pgvector, psycopg2 declared but unused |
| Security claims ↔ implementation | ⚠️ Gap | PII masking policy documented but not implemented in orchestrator |
| Business capabilities ↔ components | ⚠️ Gap | Blueprint microservices vs. monolith |
| AI claims ↔ orchestration | ✅ Aligned | RAG + guardrails + rules-before-LLM confirmed |

---

## 1.3 Gap Priority Matrix

| Priority | Gap | Effort | Impact |
| -------- | --- | ------ | ------ |
| P0 | Move or merge CI workflow so `python -m unittest discover -s artha_backend/tests` runs on push | Low | High |
| P0 | Implement PII masking before LLM calls | Medium | Critical (compliance) |
| P0 | Replace in-memory sessions with Redis | Medium | High |
| P1 | PostgreSQL + customer data migration | High | High |
| P1 | Account Aggregator sandbox integration | High | Critical (product claim) |
| P1 | Structured observability (logs/metrics/traces) | Medium | High |
| P2 | Real vector RAG (pgvector) | Medium | Medium |
| P2 | Cloud TTS/STT integration | Medium | Medium |
| P2 | React Native embeddable module | High | Medium |
| P3 | Kubernetes deployment manifests | High | Medium |
| P3 | Formal ADR repository | Low | Medium |

---

## 1.4 Blueprint vs. Implementation Gaps

| Blueprint Element | Expected | Observed |
| ----------------- | -------- | -------- |
| Monorepo `apps/mobile/` | React Native module | `[OBSERVED: artha_frontend HTML demo]` |
| `services/gateway/` | Separate service | `[OBSERVED: main.py]` |
| `services/orchestrator/` | Separate service | `[OBSERVED: handle_message in main.py]` |
| PostgreSQL + Redis | Running | `[OBSERVED: not wired]` |
| pgvector RAG | Vector search | `[OBSERVED: keyword match]` |
| Kafka event stream | Behavioural pipeline | `[MISSING]` |

---

## Lens Summary

| Lens | Key Gap |
| ---- | ------- |
| **Autopsy** | Implementation is MVP monolith; docs oversell microservices |
| **Critic Kill** | Declared stack ≠ running stack |
| **DOA** | Session + data persistence block production |
| **Ghost Mode** | Silent LLM fallback masks API failures |

---

## Cross-References

- Risks: [03-risk-register.md](03-risk-register.md)
- Actions: [17-immediate-action-plan.md](17-immediate-action-plan.md)
- Architecture truth: [07-c4-architecture.md](07-c4-architecture.md)

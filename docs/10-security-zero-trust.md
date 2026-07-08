# 10 — Security and Zero Trust Documentation

**Document ID:** ARTHA-DOC-10  
**Phase:** 6 — Security Architecture and Compliance

---

## 6.1 Authentication Design

| Method | Implementation | Token Lifecycle | Session Storage | Notes |
| ------ | -------------- | --------------- | --------------- | ----- |
| Bearer token (demo) | `VALID_TOKENS` dict in main.py | No expiry | N/A | `[OBSERVED: demo-token → cust_001]` |
| HTTPBearer | FastAPI security dependency | Per-request validation | — | auto_error=False |
| JWT | python-jose declared | `[MISSING: not implemented]` | — | Production target |
| OAuth2/OIDC | — | `[MISSING]` | — | Bank session exchange |
| MFA | — | `[MISSING]` | — | Via bank app |
| Session ID | `sess_` + token_urlsafe(16) | In-memory until evicted | SESSION_HISTORIES | Not bound to token cryptographically |

---

## 6.2 Authorization Matrix

| Role | Resource | Create | Read | Update | Delete | Approve | Export |
| ---- | -------- | ------ | ---- | ------ | ------ | ------- | ------ |
| Customer (demo-token) | Own snapshot | — | ✅ | — | — | — | — |
| Customer | Own conversation | ✅ | ✅ | — | — | — | — |
| Customer | Recommendations feedback | ✅ | — | — | — | — | — |
| Customer | Voice synthesis | ✅ | — | — | — | — | — |
| RM | Customer escalations | — | `[MISSING]` | — | — | ✅ | — |
| Compliance | Audit logs | — | `[PARTIAL: file only]` | — | — | — | ✅ |
| Admin | All customers | — | `[MISSING]` | — | — | — | — |

`[INFERRED: single demo role today — no RBAC implementation]`

---

## 6.3 Security Controls

| Control | Implementation | Verification Method |
| ------- | -------------- | ------------------- |
| Password hashing | N/A (token auth) | — |
| Token security | Static demo-token | `[RISK: manual review]` |
| Secret management | ANTHROPIC_API_KEY env var | `[MISSING: vault]` |
| CSRF protection | N/A (Bearer token API) | — |
| XSS prevention | Frontend uses textContent for user msgs; bold via DOM | Manual review |
| CORS policy | ALLOWED_ORIGINS localhost list | Code review |
| Rate limiting | `[MISSING]` | — |
| Input validation | Pydantic models + guardrails regex | Unit tests |
| Audit logging | audit_logger with SHA-256 | Code review |
| Intrusion detection | `[MISSING]` | — |
| Prompt injection defense | PROHIBITED_INPUT_PATTERNS | test_services.py |

---

## 6.4 Data Protection

| State | Protection Method | Key Management |
| ----- | ----------------- | -------------- |
| In transit | `[INFERRED: HTTPS in production]` — HTTP in local dev | TLS certs |
| At rest | Plain JSON file + audit.log | `[RISK: no encryption]` |
| PII masking | Documented in guardrail policy | `[RISK: not implemented in orchestrator]` |
| Backup encryption | `[MISSING]` | — |
| LLM data handling | Full customer facts in system prompt | `[RISK: Anthropic API exposure]` |

---

## 6.5 Zero Trust Architecture

| Layer | Control | Implementation |
| ----- | ------- | -------------- |
| Identity | Verify every request | HTTPBearer on protected routes |
| Device | — | `[MISSING: bank app attestation]` |
| Network | CORS allowlist | localhost only |
| Application | Input/output guardrails | compliance_guardrails.py |
| Data | Consent gate | consent_service.py |
| Analytics | Audit every conversation | audit_logger.py |
| LLM | Fact grounding + output filter | RAG + check_safety |

`[INFERRED STRATEGY: full zero trust requires service mesh, mTLS, and policy engine]`

---

## 6.6 Compliance Mapping

| Standard | Requirement | Implementation | Evidence |
| -------- | ----------- | -------------- | -------- |
| RBI AA Framework | Consent-based data sharing | consent_service mock | cust_001 consent object |
| SEBI IA Regulations | No unlicensed advice | Guardrails + RM handoff + positioning | Blueprint Section 8 |
| DPDP Act 2023 | Purpose limitation, consent | Partial — consent check only | `[GAP: no erasure UI]` |
| GDPR | Data minimisation | `[GAP: PII in LLM prompts]` | — |
| SOC 2 | Audit trail | Local audit.log | Partial |
| ISO 27001 | Access control | Demo token only | Gap |
| PCI DSS | N/A | No card data processed | — |
| NIST AI RMF | AI governance | Guardrail policy + tests | phase_1_deliverables/10 |

---

## 6.7 Threat Model Summary

| Threat | Attack Surface | Likelihood | Impact | Mitigation |
| ------ | -------------- | ---------- | ------ | ---------- |
| Token theft | API Bearer header | High (static token) | High | JWT + short TTL |
| Prompt injection | Chat input | Medium | High | Regex shield + semantic layer |
| LLM data leak | Anthropic API | Medium | Critical | PII masking, enterprise API |
| Audit tampering | Local file | Medium | High | WORM storage, SIEM |
| Consent bypass | API direct access | Low | High | Consent on all data endpoints |
| XSS | Chat rendering | Low | Medium | textContent usage |
| DoS | Unauthenticated flood | Medium | Medium | Rate limiting + WAF |
| Hallucinated advice | LLM output | Medium | Critical | Rules before LLM |

---

## Lens Summary

| Lens | Priority |
| ---- | -------- |
| **Red Team** | PII-in-prompt (R-002), static token (R-003) |
| **Blue Team** | Guardrails + consent + audit foundation exist |
| **Critic Kill** | Security docs claim PII masking; code does not implement |

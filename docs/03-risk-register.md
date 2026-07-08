# 03 — Risk Register

**Document ID:** ARTHA-DOC-03  
**Audit Lenses:** Red Team, Blue Team, DOA

---

## Top Risk Register

| Risk ID | Category | Description | Severity | Likelihood | Impact | Mitigation |
| ------- | -------- | ----------- | -------- | ---------- | ------ | ---------- |
| R-001 | Compliance | AI output classified as unregistered investment advice | Critical | Medium | Critical | Position as guidance; RM handoff; reason codes; legal review |
| R-002 | Privacy | PII (name, balances) sent to Anthropic without masking | High | High | High | Implement masking per guardrail policy doc |
| R-003 | Security | Static demo-token with no expiry/rotation | High | High | High | JWT with bank OAuth exchange |
| R-004 | AI Safety | Regex guardrails bypassable via indirect prompts | High | Medium | High | Add semantic classifier + output schema validation |
| R-005 | AI Safety | LLM hallucination on numbers not in facts | Critical | Medium | Critical | Rules-before-LLM (implemented); add output fact-checker |
| R-006 | Resilience | In-memory session loss on restart | High | High | Medium | Redis session store |
| R-007 | Data | Single JSON file — no backup, no multi-tenant | High | Medium | High | PostgreSQL + backup strategy |
| R-008 | Operations | No observability — silent LLM fallback | Medium | High | Medium | Log fallback events; add health metrics |
| R-009 | DevOps | CI does not execute backend tests | Medium | High | Medium | Fix workflow paths |
| R-010 | Consent | AA consent artefact mocked, not cryptographically verified | High | High | High | Integrate real AA consent validation |
| R-011 | Audit | Local audit.log tamperable | Medium | Medium | High | Append-only store, SIEM integration |
| R-012 | Regulatory | DPDP Act — no user data revocation UI | Medium | Medium | High | Consent management screen |
| R-013 | Availability | Single-process FastAPI — no HA | Medium | Medium | High | Container orchestration + load balancer |
| R-014 | Financial | Incorrect recommendation from stale risk profile | Medium | Low | Critical | Dynamic risk profiling pipeline |
| R-015 | Reputational | Avatar feels gimmicky vs. substantive | Low | Medium | Medium | Lead with data accuracy over visual polish |
| R-016 | AI Cost | Unbounded LLM calls per session | Medium | Medium | Medium | Rate limiting, token budgets |
| R-017 | Integration | RM handoff prints to console only | Medium | High | Medium | CRM API integration |
| R-018 | Sustainability | LLM inference energy cost at scale | Low | Medium | Low | Caching, smaller models for simple queries |

---

## Assumption Register

| Assumption ID | Assumption | Basis for Inference | Validation Required |
| ------------- | ---------- | ------------------- | ------------------- |
| A-001 | Demo-token represents bank OAuth exchange | Blueprint Section 16 | Bank IT integration test |
| A-002 | cust_001.json schema matches AA payload format | Blueprint Section 15 | AA sandbox schema validation |
| A-003 | Claude 3.5 Sonnet is approved for financial use | requirements.txt | Enterprise AI governance review |
| A-004 | Keyword RAG sufficient for demo | Implementation | Product sign-off for pilot |
| A-005 | Priya Sharma RM assignment is static | rm_handoff.py | CRM routing rules |
| A-006 | 8-turn history cap is adequate | main.py | UX research on context loss |
| A-007 | Browser TTS acceptable for pilot | script.js | Accessibility + quality review |
| A-008 | SEBI boundary: guidance not advice | Blueprint Section 8 | Legal counsel opinion |

---

## Architecture Review Board Charter

| Element | Definition |
| ------- | ---------- |
| **Purpose** | Govern architecture decisions; ensure consistency across bank integration, AI, and compliance |
| **Membership** | CTO, principal architects, security lead, product lead, platform lead, compliance officer |
| **Cadence** | Weekly for proposals; monthly governance review |
| **Escalation Path** | Architecture team → CTO → executive leadership |
| **Decision Criteria** | Security, scale, maintainability, cost, compliance, delivery risk |
| **ARTHA-specific gate** | No LLM deployment change without compliance review of guardrail impact |

`[INFERRED STRATEGY BASED ON MARKET STANDARD: charter template — team not named in repo]`

---

## Risk Heat Map

```
Impact ↑
Critical │ R-001  R-005
High     │ R-002  R-003  R-006  R-007  R-010
Medium   │ R-004  R-008  R-009  R-011  R-012  R-013  R-016  R-017
Low      │ R-015  R-018
         └────────────────────────→ Likelihood
              Low    Medium    High
```

---

## Lens Summary

| Lens | Priority Risks |
| ---- | -------------- |
| **Red Team** | R-002, R-003, R-004 |
| **Blue Team** | R-001 mitigated by design; R-005 partially mitigated |
| **DOA** | R-006, R-007 block production pilot |

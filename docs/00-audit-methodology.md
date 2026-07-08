# AI Audit Methodology — Multi-Lens Forensic Analysis

**Document ID:** ARTHA-DOC-00  
**Applies To:** Entire ARTHA AI documentation suite

---

## 1. Objective

This document defines the **AI-augmented audit lenses** applied to reverse-engineer ARTHA AI from source code, configuration, and legacy deliverables. Each lens produces distinct findings integrated into deliverables 01–18.

---

## 2. Audit Lenses Applied

### 2.1 Expose Idea (First Principles)

**Question:** What is ARTHA AI fundamentally trying to be?

| Finding | Marker |
| ------- | ------ |
| Bank-embedded avatar wealth advisor, not a standalone investing app | `[OBSERVED: ARTHA_AI_Blueprint.md Section 02]` |
| Conversation-first interface over dashboard-first robo-advisory | `[OBSERVED: artha_frontend/script.js chat-centric UI]` |
| Deterministic advisory rules before LLM phrasing | `[OBSERVED: main.py handle_message ordering]` |

**Verdict:** The core idea is *trustable, explainable, bank-native guidance at scale* — not autonomous trading.

---

### 2.2 Autopsy (Forensic Dissection)

**Method:** Trace every user message through code paths.

```
User Input → consent_service → customer_snapshot → behaviour_engine
          → advisory_engine → ai_orchestrator (+ RAG + guardrails)
          → audit_logger → MessageResponse → frontend render + voice
```

| Layer | Health | Finding |
| ----- | ------ | ------- |
| Orchestration | Functional | Single FastAPI monolith, not microservices as blueprint describes |
| Session state | In-memory | `[RISK: SESSION_HISTORIES dict — lost on restart, no Redis despite dependency]` |
| Data | JSON file | `[OBSERVED: cust_001.json only — no PostgreSQL despite requirements.txt]` |
| LLM | Dual-mode | Anthropic API when key present; keyword fallback otherwise |

---

### 2.3 10x Thinking (Ambition vs. Reality)

| 10x Vision | Current State | Gap |
| ---------- | ------------- | --- |
| Millions of concurrent avatar sessions | In-memory, 100-session cap | `[RISK: scale ceiling]` |
| Live Account Aggregator integration | Mock JSON snapshot | `[MISSING: AA sandbox]` |
| Real-time behavioural ML pipeline | Deterministic Python aggregations | `[INFERRED: acceptable for MVP]` |
| Multi-agent orchestration (LangGraph) | Linear pipeline in `handle_message` | `[INFERRED STRATEGY: evolve to workflow engine]` |

**10x Recommendation:** Preserve the *rules-before-LLM* pattern; scale orchestration and data layers, not prompt complexity.

---

### 2.4 Critic Kill (Assumption Destruction)

| Assumption Destroyed | Evidence |
| -------------------- | -------- |
| "Microservices architecture exists" | `[OBSERVED: single artha_backend/main.py FastAPI app]` |
| "pgvector RAG is implemented" | `[OBSERVED: keyword match in rag_knowledge_base.py, pgvector unused]` |
| "CI runs project tests" | `[OBSERVED: .github/workflows/python-app.yml runs pytest at root — no root tests]` |
| "JWT auth is production-ready" | `[OBSERVED: hardcoded VALID_TOKENS dict with demo-token]` |
| "Voice uses cloud TTS" | `[OBSERVED: browser SpeechSynthesis + mock viseme timing]` |

---

### 2.5 IQ200 (Deep Systems Reasoning)

**Architectural insight:** ARTHA correctly separates *fact generation* (signals, rules) from *fact narration* (LLM). This is the compliance-critical invariant.

**Weak coupling points:**
1. `customer_context.get("savings", 0)` in orchestrator vs. computed from accounts — field may not exist in snapshot
2. Guardrails are regex-only — no semantic classifier
3. Audit log is local file — no tamper-evident chain beyond SHA-256 per record

**IQ200 verdict:** Strong conceptual architecture; implementation is MVP-thin with production dependencies declared but not wired.

---

### 2.6 Red Team (Adversarial)

| Attack Vector | Current Defense | Residual Risk |
| ------------- | --------------- | ------------- |
| Prompt injection | Regex input shield | `[RISK: bypass via encoding, multilingual, indirect]` |
| Token theft | Static demo-token | `[RISK: no rotation, no expiry]` |
| Data exfil via LLM | No PII masking in orchestrator prompt | `[RISK: contradicts phase_1 guardrail policy doc]` |
| Consent bypass | check_consent on message path only | `[OBSERVED: snapshot endpoint skips explicit consent log]` |
| Audit tampering | Local audit.log writable | `[RISK: no append-only WORM storage]` |

---

### 2.7 Blue Team (Defensive Posture)

| Control | Status |
| ------- | ------ |
| Consent gate before advisory | `[OBSERVED: implemented]` |
| Reason-coded recommendations | `[OBSERVED: DORMANT_FD_REALLOCATION etc.]` |
| Output compliance filter | `[OBSERVED: guarantee/zero-risk blocked]` |
| RM handoff on escalation keywords | `[OBSERVED: trigger_handoff]` |
| CORS allowlist | `[OBSERVED: localhost origins only]` |
| Integrity hash on audit records | `[OBSERVED: SHA-256 in audit_logger.py]` |
| Unit tests for core services | `[OBSERVED: test_services.py — 12 tests]` |

---

### 2.8 DOA (Dead on Arrival Analysis)

**Would this fail in production today?** Partially yes.

| Component | DOA Risk | Mitigation Path |
| --------- | -------- | --------------- |
| Session store | High — restart loses state | Redis as already in blueprint |
| Single JSON customer | High — no multi-tenant | PostgreSQL + AA integration |
| CI pipeline | Medium — tests not executed in CI | Fix workflow path to `artha_backend/tests` |
| LLM cost/latency | Medium — no rate limits | API gateway throttling |

**Not DOA for:** Hackathon demo, pilot UAT with single persona, compliance narrative.

---

### 2.9 Ghost Mode (Silent Failure Detection)

Failures that occur **without user-visible errors:**

| Ghost Failure | Symptom | Detection |
| ------------- | ------- | --------- |
| Anthropic API down | Falls back to keyword mock — user may not know | `[RISK: no telemetry on fallback activation]` |
| Audit queue backlog | Silent print on write failure | `[RISK: compliance gap if disk full]` |
| Partial month dining delta | behaviour_engine excludes active month if day < 10 | `[OBSERVED: intentional — may confuse users early in month]` |
| Welcome message hardcoded in frontend | Mismatch if backend data changes | `[OBSERVED: script.js line 51-56]` |

---

## 3. Lens Synthesis Matrix

| Lens | Top Finding | Priority |
| ---- | ----------- | -------- |
| Expose Idea | Rules-before-LLM is the moat | Protect |
| Autopsy | Monolith MVP, not microservices | Document honestly |
| 10x | Scale needs Redis + Postgres + AA | Phase 2 |
| Critic Kill | Declared deps ≠ wired deps | Fix CI + infra |
| IQ200 | Compliance architecture sound | Extend guardrails |
| Red Team | PII in LLM prompts | Immediate |
| Blue Team | Core gates exist | Harden |
| DOA | Session + data layer | Before pilot |
| Ghost Mode | Silent LLM fallback | Add observability |

---

## 4. How to Use This Document

Each deliverable 01–18 includes a **Lens Summary** section referencing findings from this methodology. For implementation decisions, prioritize items flagged `[RISK]` in Red Team and Ghost Mode sections.

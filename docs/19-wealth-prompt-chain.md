# 19 — Wealth Prompt Chain Architecture

**Document ID:** ARTHA-DOC-19  
**Implementation:** `artha_backend/agents/wealth_chain/`

---

## Overview

Single LLM instance (`claude-3-5-sonnet-20241022`), **7 persona prompts**, sequential execution, **Master Auditor** gate at Step 7.

**Hybrid pre-layer (Python):** `behaviour_engine` + `advisory_engine` run before the chain; Step 7 cross-validates against rules engine output.

---

## Routing

| Path | Trigger | LLM Calls |
|------|---------|-----------|
| `quick` | Greetings, status, "why", RM keywords | 1 (or keyword mock) |
| `deep` | "full wealth plan", portfolio strategy, `mode: deep` | 7 sequential |
| `auto` | Default — router classifies | 1 or 7 |

API: `POST /v1/conversation/message` with optional `mode` field.

---

## 7-Step Chain

| Step | Persona | Output Schema |
|------|---------|---------------|
| 1 | Wealth Data Analyst | `Step1Output` |
| 2 | Financial Goal Architect | `Step2Output` |
| 3 | Portfolio Strategist | `Step3Output` |
| 4 | Red Team Auditor | `Step4Output` |
| 5 | Blue Team Behavioral Architect | `Step5Output` |
| 6 | Wealth Avatar | `Step6Output` |
| 7 | Chief Wealth Officer (Master Auditor) | `Step7Output` |

Prompt templates: `artha_backend/agents/wealth_chain/prompts/step*.md`

---

## Master Auditor — 8 Programmatic Checks

1. Portfolio vs risk profile alignment  
2. SIP coverage vs goal timelines  
3. Blue Team covers Red Team risks  
4. Avatar numbers grounded in facts  
5. SEBI disclosure present  
6. Cross-step contradiction scan  
7. CAGR optimism filter  
8. Insurance gap flag  

**Decision thresholds:**
- Confidence ≥ 85 → **approve**
- 70–84 → **revise** (max 2 loops, `fix_targets`)
- < 70 → **reject** → RM handoff

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /v1/conversation/message` | Quick or deep (via `mode`) |
| `POST /v1/wealth/plan` | Explicit deep chain |
| `GET /v1/wealth/plan/{plan_id}` | Retrieve cached plan |
| `GET /v1/admin/llm-telemetry` | Fallback + chain telemetry |

---

## Pilot Controls

Environment variables:
- `WEALTH_CHAIN_ENABLED=true`
- `MAX_DEEP_CHAINS_PER_DAY=3`
- `WEALTH_CHAIN_COHORT=cust_001,cust_profile_001` (optional)

---

## Eval Harness

`tests/test_wealth_chain.py` — 50 synthetic profiles in `tests/fixtures/profiles/`, ≥90% confidence ≥ 85 target in mock mode.

Generate profiles: `python artha_backend/scripts/generate_profiles.py`

---

## Mobile SDK Embed Contract

Host app provides:
- `Authorization: Bearer <bank-oauth-token>`
- WebView or iframe loading `artha_frontend/` at `/v1/session/start`

Host receives events via `postMessage`:
- `{ type: "artha:plan_ready", plan_id, confidence }`
- `{ type: "artha:rm_handoff", reason }`

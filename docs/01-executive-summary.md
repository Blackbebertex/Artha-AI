# 01 — Executive Summary

**Document ID:** ARTHA-DOC-01  
**Audience:** C-level executives, investors, board members  
**Audit Lenses:** Expose Idea, 10x Thinking, DOA

---

## Strategic Overview

**ARTHA AI** (Sanskrit *artha* — wealth, purpose) is an avatar-led digital wealth advisor designed to embed inside a bank's existing mobile application. It delivers personalised, explainable financial guidance at conversational scale — addressing India's rapidly growing retail investor base (21–22 crore demat accounts, ~₹30,000 crore monthly SIP inflows) without requiring a 1:1 human relationship manager for every customer.

`[OBSERVED: ARTHA_AI_Blueprint.md, artha_backend implementation verified July 2026]`

---

## What Exists Today

| Dimension | Status |
| --------- | ------ |
| **Product vision** | Fully documented in blueprint and phase deliverables |
| **MVP backend** | FastAPI monolith with agentic conversation pipeline |
| **MVP frontend** | HTML/JS demo shell simulating bank-embedded module |
| **AI engine** | Claude 3.5 Sonnet (optional) + deterministic rules engine + keyword RAG |
| **Compliance gates** | Consent check, guardrails, audit logging, RM handoff |
| **Demo persona** | Riya Kapoor (`cust_001`) with realistic AA-style JSON data |
| **Tests** | 12 unit tests covering core services |
| **Infrastructure** | Docker Compose for gateway + nginx frontend; GitHub Actions CI (partial) |

---

## Three Strategic Pillars (Validated in Code)

1. **See everything** — 360° customer snapshot from consented data (`customer_snapshot.py`, `cust_001.json`)
2. **Understand the person** — Behavioural signals from transactions (`behaviour_engine.py`)
3. **Advise like a human, scale like software** — Reason-coded recommendations + LLM narration (`advisory_engine.py`, `ai_orchestrator.py`)

---

## Architecture at a Glance

```
Bank Mobile Shell (artha_frontend)
        │ Bearer demo-token
        ▼
FastAPI Gateway (main.py)
        ├── Consent Service
        ├── Customer Snapshot
        ├── Behaviour Engine → Advisory Engine
        ├── AI Orchestrator (RAG + Guardrails + Claude)
        ├── Avatar Voice Service
        ├── RM Handoff
        └── Audit Logger
```

`[INFERRED: Blueprint describes 5-layer microservices; implementation is consolidated monolith — appropriate for hackathon/MVP stage]`

---

## Business Impact

| Capability | Business Value | Maturity |
| ---------- | -------------- | -------- |
| Avatar conversation | Trust, inclusion (voice + multilingual) | MVP — browser TTS |
| 360° financial view | Differentiation vs. generic robo-advisors | Mock data |
| Explainable recommendations | Regulatory credibility | Production-ready pattern |
| RM handoff | SEBI boundary compliance | Implemented |
| Audit trail | Compliance team requirement | Local file — needs hardening |

---

## Critical Gaps (Executive View)

| Gap | Business Risk | Timeline Impact |
| --- | ------------- | --------------- |
| No live Account Aggregator | Cannot claim real 360° in production | Blocks pilot |
| In-memory sessions | Customer experience breaks on deploy | Blocks scale |
| PII sent to LLM without masking | DPDP / regulatory exposure | Blocks compliance sign-off |
| CI does not run backend tests | Quality regression risk | Blocks enterprise release |

See [02-gap-analysis.md](02-gap-analysis.md) and [03-risk-register.md](03-risk-register.md).

---

## Investment Thesis

**Why ARTHA wins:**
- Bank-native embedding (not another app download)
- Account Aggregator framework alignment (live Indian infrastructure)
- Compliance-by-design (rules before LLM, reason codes, human handoff)
- Inclusion angle (Hindi code-switch, voice-first for Tier-2/3)

**What investment unlocks:**
- AA sandbox integration (~3 months MVP hardening)
- Single-branch pilot with human-in-the-loop review (~6 months)
- Multi-language scale + RM dashboard (~12 months)

`[OBSERVED: ARTHA_AI_Blueprint.md Section 10 roadmap]`

---

## Lens Summary

| Lens | Executive Takeaway |
| ---- | ------------------ |
| **Expose Idea** | Advisor inside trusted bank app — not fintech competitor |
| **10x** | Architecture supports scale; data/infra layers need investment |
| **DOA** | Demo-ready; production pilot requires 3 targeted hardening sprints |
| **Red Team** | PII-in-prompt is the highest governance risk |
| **Blue Team** | Core compliance narrative is implementable and tested |

---

## Recommended Decision

**Proceed to controlled pilot** after completing the 30-day technical priorities in [17-immediate-action-plan.md](17-immediate-action-plan.md), with compliance sign-off on AI boundary positioning (guidance vs. regulated advice).

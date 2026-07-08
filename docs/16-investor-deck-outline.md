# 16 — Investor Deck Outline

**Document ID:** ARTHA-DOC-16  
**Phase:** 12 — Investor and Executive Documentation

---

## 12.1 Pitch Deck Content Script

| Slide | Focus | Key Message |
| ----- | ----- | ----------- |
| 1 | Title and value proposition | **ARTHA AI** — Your bank's mobile app, now with a personal wealth advisor who already knows you |
| 2 | Problem statement | 21–22 crore demat accounts; fragmented advisory; human RMs don't scale; Tier-2/3 investors underserved |
| 3 | Gap analysis insight | Banks have data but not conversational intelligence; robo-advisors lack 360° view and trust |
| 4 | Solution overview | Avatar-led advisor embedded in bank app; three pillars: See, Understand, Advise |
| 5 | Architecture in plain language | Customer talks to Artha → bank-verified data → rules check → AI explains → human RM when needed |
| 6 | Workflow and operating model | Weekly check-ins, explainable cards, Hindi code-switch, RM handoff for regulated decisions |
| 7 | Technical moat | Rules-before-LLM architecture; reason-coded recommendations; AA framework native; compliance guardrails |
| 8 | Security and compliance readiness | Consent artefacts, audit trail with integrity hashes, SEBI boundary positioning, DPDP awareness |
| 9 | Monetization model | `[INFERRED]` B2B SaaS to banks: per-active-user licensing + implementation services |
| 10 | Go-to-market approach | Hackathon demo → single-branch pilot → multi-language scale; design partner bank |
| 11 | Investment or resource ask | AA sandbox access, pilot branch, compliance review bandwidth, 12-month engineering team |
| 12 | Execution timeline | MVP (done) → 3mo hardening → 6mo pilot → 12mo production scale |

---

## 12.2 Business Translation Rules

### Architecture (Section 07)

| Audience | Summary |
| -------- | ------- |
| **Executive** | ARTHA plugs into the bank's existing app and securely pulls customer data to power a conversational advisor |
| **Engineering** | FastAPI monolith with modular services; target microservices on Kubernetes with Redis and PostgreSQL |
| **Risk** | Demo uses mock data and static auth; production requires AA integration, JWT, and encrypted storage |

### AI Engine (Section 12)

| Audience | Summary |
| -------- | ------- |
| **Executive** | AI explains recommendations; it doesn't make them up — every suggestion has a traceable reason |
| **Engineering** | Claude narrates facts computed by deterministic rules; keyword RAG grounds product claims |
| **Risk** | Guardrails block guaranteed-return language; human RM handles regulated advice boundary |

### Compliance (Section 10)

| Audience | Summary |
| -------- | ------- |
| **Executive** | Built for Indian regulatory context — AA, SEBI, DPDP |
| **Engineering** | Consent gate, audit logging, input/output safety filters implemented |
| **Risk** | PII masking and production auth not yet implemented — 30-day fix required before pilot |

---

## Closing Line

> "We didn't build another investing app. We built the advisor your bank's mobile app was missing — one that already knows you."

`[OBSERVED: ARTHA_AI_Blueprint.md Section 13]`

---

## Key Metrics for Investors (Post-Launch)

| Metric | Why It Matters |
| ------ | -------------- |
| Weekly active conversations | Engagement proof |
| SIP starts / top-ups influenced | Revenue proxy for bank |
| Recommendation acceptance rate | AI quality signal |
| Human escalation rate | Compliance health indicator |
| Customer trust score (NPS) | Adoption sustainability |
| AUM growth per active user | Bank ROI |

---

## Lens Summary

| Lens | Investor Message |
| ---- | ---------------- |
| **Expose Idea** | Bank-native, not fintech competitor |
| **10x** | TAM = every retail banking customer in India |
| **DOA** | Honest about MVP stage; clear path to pilot |

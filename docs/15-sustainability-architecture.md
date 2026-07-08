# 15 — Sustainability Architecture

**Document ID:** ARTHA-DOC-15  
**Phase:** 3.11 — Sustainability Architecture

`[INFERRED STRATEGY BASED ON MARKET STANDARD: sustainability section — no prior documentation in repo]`

---

## 3.11 Sustainability Component Analysis

| Component | Carbon / Energy Concern | Optimization Opportunity | Target |
| --------- | ----------------------- | ------------------------ | ------ |
| Claude API inference | High per-token energy | Cache frequent responses; rules-only for simple queries | 40% LLM call reduction |
| Anthropic fallback mock | Near-zero | Route simple queries to mock intentionally in dev | Dev/staging only |
| Browser SpeechSynthesis | Low (client-side) | Prefer over cloud TTS for demo | Keep for low-stakes |
| FastAPI monolith | Low baseline | Right-size containers; scale to zero in dev | < 0.5 vCPU idle |
| JSON file I/O | Negligible | PostgreSQL connection pooling when migrated | — |
| Docker nginx frontend | Low static serving | CDN for production assets | Edge caching |
| Audit log writes | Low I/O | Batch writes; compress archives | — |
| In-memory sessions | RAM efficiency | Redis with TTL vs. unbounded dict | 100 session cap (done) |

---

## Carbon-Aware Architecture Recommendations

### 1. Query Routing (Green AI)

Route messages through a decision tree before invoking LLM:

```
Simple status query → Keyword/mock response (no API call)
Product fact query → RAG + small model or cached response
Complex advisory query → Full Claude inference
```

**Estimated impact:** 50–70% reduction in LLM calls for typical check-in conversations.

### 2. Model Selection

| Use Case | Model Tier | Rationale |
| -------- | ---------- | --------- |
| Greeting/status | No LLM | Zero inference cost |
| Product facts | Haiku / small model | Lower energy per token |
| Nuanced advisory dialogue | Sonnet | Quality required |

### 3. Infrastructure

| Strategy | Action |
| -------- | ------ |
| Region selection | Deploy in bank's preferred region (likely India) to reduce data transit |
| Autoscaling | Scale API pods to zero in non-business hours for pilot |
| Renewable energy | Select cloud region with renewable energy commitments |
| Embodied carbon | Minimise container image sizes; multi-stage Docker builds |

---

## Sustainability Metrics (Target)

| Metric | Baseline (MVP) | 12-Month Target |
| ------ | -------------- | --------------- |
| LLM calls per conversation | ~1.0 | 0.4 (with routing) |
| Avg tokens per response | ~500 | 300 (prompt optimisation) |
| API server uptime (idle) | 100% local dev | Auto-scale 8am–10pm IST |
| Carbon per 1000 conversations | `[MISSING: measure]` | 30% reduction |

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **10x** | Rules-before-LLM pattern is inherently greener than end-to-end LLM |
| **IQ200** | Biggest sustainability lever is query routing, not infrastructure tuning |

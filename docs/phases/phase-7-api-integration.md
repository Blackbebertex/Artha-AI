# Phase 7 — API & Integration Documentation

**Parent:** [11-api-documentation.md](../11-api-documentation.md)  
**Legacy Sources:** Blueprint Section 16, `mds/detailed_modules/phase_1_08_define_api_contracts.md`

## Full API Specification

See [11-api-documentation.md](../11-api-documentation.md) for:

- 7.1 Critical endpoint specs (session, message, snapshot)
- 7.2 Endpoint catalog
- 7.3 Integration inventory
- 7.4 Contract risk analysis

## Blueprint API vs. Implemented

| Blueprint Endpoint | Implemented | Notes |
| ------------------ | ----------- | ----- |
| POST /v1/session/start | ✅ | |
| POST /v1/conversation/message | ✅ | |
| GET /v1/conversation/history | ❌ | Session in memory; no GET endpoint |
| POST /v1/recommendations/:id/feedback | ✅ | |
| POST /v1/voice/synthesize | ✅ | |
| GET /v1/customer/snapshot | ✅ | Added beyond blueprint minimum |
| GET /health | ✅ | Operations endpoint |

## Integration Roadmap

| Integration | Phase | Priority |
| ----------- | ----- | -------- |
| Bank OAuth | Stabilization | P0 |
| AA Sandbox (Setu/Finvu) | Stabilization | P0 |
| Bank CRM (RM handoff) | Pilot | P1 |
| Cloud TTS (Azure/Google) | Pilot | P2 |
| Push notifications | Scale | P3 |

## OpenAPI

Auto-generated at runtime: `http://localhost:8000/docs`  
**Action:** Export to `docs/openapi.json` per [17-immediate-action-plan.md](../17-immediate-action-plan.md)

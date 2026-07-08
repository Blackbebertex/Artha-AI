# 11 — API Documentation

**Document ID:** ARTHA-DOC-11  
**Phase:** 7 — API Specification and Integration Documentation

**Base URL:** `http://localhost:8000`  
**Auth:** `Authorization: Bearer demo-token`  
**OpenAPI:** Auto-generated at `/docs` (FastAPI Swagger)

---

## 7.1 Critical Endpoint Specifications

### POST /v1/session/start

| Field | Value |
| ----- | ----- |
| **Summary** | Exchange bank token for ARTHA session |
| **Auth** | Required — Bearer token |
| **Request** | `{ "language": "en" }` |
| **Response** | `{ "session_id": "sess_...", "customer_id": "cust_001", "language": "en" }` |

**Validation:** `language` defaults to `"en"` if omitted.

**Success (200):**
```json
{
  "session_id": "sess_xK9mP2nQ4rT7vW1yZ3aB5c",
  "customer_id": "cust_001",
  "language": "en"
}
```

**Error (401):**
```json
{ "detail": "Invalid or missing token. Use 'demo-token' for the demo." }
```

---

### POST /v1/conversation/message

| Field | Value |
| ----- | ----- |
| **Summary** | Send user turn; receive avatar reply + recommendation |
| **Auth** | Required |
| **Request** | `{ "session_id": "sess_...", "message_text": "How am I doing?" }` |
| **Response** | `MessageResponse` |

**Success (200):**
```json
{
  "reply_text": "You saved 22% of your income this month, Riya! ...",
  "recommendation_ids": ["rec_fd_realloc_001"],
  "recommendation": {
    "action": "reallocate_dormant_fd",
    "recommendation_id": "rec_fd_realloc_001",
    "reasonCode": "DORMANT_FD_REALLOCATION",
    "facts": {
      "Account": "Fixed Deposit – HDFC-FIP (acc_fd_882)",
      "Current Rate": "6.1% p.a.",
      "Months Dormant": "14",
      "Matching Goal": "First Car (2027-06-01)",
      "Risk Profile": "Moderate"
    }
  }
}
```

**Error (401):** Invalid token  
**Error (404):** Customer/session not found  
**Consent denial (200):** `reply_text` explains missing consent — not HTTP error

---

### GET /v1/customer/snapshot

| Field | Value |
| ----- | ----- |
| **Summary** | Return full customer 360° profile |
| **Auth** | Required |
| **Response** | Full `cust_001.json` structure |

**Success (200):** Customer object with accounts, goals, transactions, consent.

**Error (404):**
```json
{ "detail": "Customer not found" }
```

---

## 7.2 Endpoint Catalog

| Endpoint | Method | Purpose | Auth | Request Model | Response Model | Dependencies |
| -------- | ------ | ------- | ---- | ------------- | -------------- | ------------ |
| `/health` | GET | Liveness probe | No | — | `{status, service, time}` | — |
| `/v1/session/start` | POST | Create session | Yes | SessionStartRequest | SessionStartResponse | In-memory store |
| `/v1/customer/snapshot` | GET | 360° profile | Yes | — | Snapshot JSON | customer_snapshot |
| `/v1/conversation/message` | POST | Chat turn | Yes | MessageRequest | MessageResponse | Full pipeline |
| `/v1/recommendations/{rec_id}/feedback` | POST | Log feedback | Yes | RecommendationFeedbackRequest | `{status, rec_id}` | audit_logger |
| `/v1/voice/synthesize` | POST | Avatar voice metadata | Yes | VoiceSynthesisRequest | VoiceSynthesisResponse | avatar_voice |

---

## 7.3 Integration Inventory

| External System | Purpose | Auth | Failure Handling | Retry | Webhook |
| --------------- | ------- | ---- | ---------------- | ----- | ------- |
| Anthropic Claude API | LLM dialogue | API key header | Fallback to keyword mock | None | — |
| Bank Identity (target) | Session exchange | OAuth2 | `[MISSING]` | — | — |
| Account Aggregator (target) | Financial data | AA consent token | `[MISSING]` | — | Consent events |
| Bank CRM (target) | RM handoff | API key | Print to console | — | — |
| Browser SpeechSynthesis | TTS playback | N/A | Text-only fallback | — | — |
| Google sounds CDN | Demo audio URL | None | Browser TTS fallback | — | — |

---

## 7.4 Contract Risk Analysis

| Risk | Mitigation Strategy |
| ---- | ------------------- |
| Breaking changes | Version prefix `/v1/`; maintain backward compat for 1 release |
| No OpenAPI published to docs | Export from `/openapi.json`; commit to docs |
| Idempotency | `[MISSING]` — add `Idempotency-Key` header for message POST |
| Timeout standards | `[MISSING]` — recommend 30s client, 25s server |
| Pagination | N/A for MVP — add cursor pagination for transaction history |
| Consumer contract tests | Add Pact tests frontend ↔ backend |
| Deprecation policy | 90-day notice for v1 endpoint changes |

---

## Frontend API Client Reference

`[OBSERVED: artha_frontend/script.js]`

```javascript
const BACKEND_URL = "http://localhost:8000";
const DEMO_TOKEN  = "demo-token";

async function apiPost(path, body) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${DEMO_TOKEN}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Autopsy** | 6 endpoints implemented; blueprint lists conversation/history — `[MISSING: GET /v1/conversation/history]` |
| **IQ200** | Consent denial returns 200 — correct UX pattern, document for API consumers |

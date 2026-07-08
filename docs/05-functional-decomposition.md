# 05 — Functional Decomposition

**Document ID:** ARTHA-DOC-05  
**Phase:** 2 — Functional and Process Documentation

---

## 2.1 Functional Decomposition Matrix

| Feature ID | User Action | UI Screen | Frontend Trigger | Frontend Method | Backend Endpoint | Service Layer | DB Operation | External API | Async Job | Expected Output | Failure States |
| ---------- | ----------- | --------- | ---------------- | --------------- | ---------------- | ------------- | ------------ | ------------ | --------- | --------------- | -------------- |
| F-001 | Open ARTHA module | Chat tab | DOMContentLoaded | `startSession()` | POST `/v1/session/start` | `main.start_session` | In-memory session create | — | — | session_id, customer_id | 401 invalid token |
| F-002 | View portfolio | Portfolio tab | `switchTab('portfolio')` | `loadCustomerDashboard()` | GET `/v1/customer/snapshot` | `customer_snapshot.get_snapshot` | Read JSON file | — | — | accounts, goals, txs | 404 customer not found |
| F-003 | Send chat message | Chat input | Enter key / Send | `sendMessage()` | POST `/v1/conversation/message` | `handle_message` pipeline | Session history append | Anthropic API (optional) | `generate_response_async` | reply_text, recommendation | Consent denied message |
| F-004 | View recommendation | Chat bubble | Auto on response | `buildRecCard()` | (embedded in message response) | `advisory_engine` | — | — | — | reasonCode + facts card | No rec if none fired |
| F-005 | Dismiss recommendation | Rec card button | onclick | DOM remove | — | — | — | — | — | Card removed | — |
| F-006 | Request RM | "Talk to RM" / keywords | `sendSuggestion()` | POST message | POST `/v1/conversation/message` | `rm_handoff.trigger_handoff` | — | CRM (mock print) | — | Handoff confirmation reply | — |
| F-007 | Voice playback | Auto after reply | `playVoiceAndAnimate()` | POST `/v1/voice/synthesize` | `avatar_voice.synthesize_voice_details` | — | — | Browser SpeechSynthesis | — | Viseme animation | Audio blocked by browser |
| F-008 | Mock voice input | Mic button | `toggleVoice()` | Simulated STT | (routes to F-003) | — | — | — | setTimeout 2s | Canned transcript | Mic permission denied |
| F-009 | Language switch | Hindi message | `detectLang()` | Chip update EN/HI | (passed to orchestrator) | `ai_orchestrator` | — | — | — | Hindi reply | — |
| F-010 | Feedback on rec | (API exists, UI partial) | — | — | POST `/v1/recommendations/{id}/feedback` | `audit_logger` | Audit log write | — | Background thread | `status: recorded` | — |
| F-011 | Health check | — | — | — | GET `/health` | — | — | — | — | status ok | Service down |

---

## 2.2 State Transition Mapping

| Flow | Initial State | Trigger Event | Next State | Error State | Recovery Path |
| ---- | ------------- | ------------- | ---------- | ----------- | ------------- |
| Session | No session | `startSession()` success | Active session | Backend offline | Show error bubble; retry |
| Session | Active | 100+ sessions created | Oldest evicted | Session not found | Re-start session |
| Conversation | Idle | User sends message | Processing (typing) | API error | Error bubble; retry |
| Conversation | Processing | Response received | Display reply + voice | Guardrail block | Safe fallback text |
| Consent | Unknown | Message received | Checked | Consent invalid | Block with consent message |
| Recommendation | None | Rules fire | Rec attached to response | No rule match | Generic guidance only |
| RM Handoff | Normal | Escalation keywords | Escalated | CRM unreachable | Console log (today) |
| Voice | Idle | Reply received | Playing + visemes | Synthesis fail | Text-only display |

---

## 2.5 API-to-UI Traceability Matrix

| Screen / Page | Component | API Endpoint | Method | Request Payload | Response Model | Error Handling | Loading Strategy |
| ------------- | --------- | ------------ | ------ | --------------- | -------------- | -------------- | ---------------- |
| Chat | `startSession` | `/v1/session/start` | POST | `{language}` | SessionStartResponse | Status bar red + error bubble | "Connecting…" |
| Chat | `sendMessage` | `/v1/conversation/message` | POST | `{session_id, message_text}` | MessageResponse | Error bubble | Typing indicator |
| Portfolio | `loadCustomerDashboard` | `/v1/customer/snapshot` | GET | — | Snapshot JSON | console.warn | On session start |
| Avatar | `playVoiceAndAnimate` | `/v1/voice/synthesize` | POST | `{text, language}` | VoiceSynthesisResponse | console.warn | Viseme on speech start |
| All | — | `/health` | GET | — | `{status, service, time}` | — | Not used in UI |

---

## Module Breakdown (Code-Level)

| Module | Responsibility | Key Files | Inputs | Outputs |
| ------ | -------------- | --------- | ------ | ------- |
| Gateway | Auth, routing, CORS | `main.py` | HTTP + Bearer token | JSON responses |
| Snapshot | Load customer 360° | `customer_snapshot.py` | customer_id | Full profile dict |
| Behaviour | Compute signals | `behaviour_engine.py` | transactions[] | savings_rate, dining_delta |
| Advisory | Rules-based recs | `advisory_engine.py` | snapshot | recommendation + reasonCode |
| Consent | Validate AA consent | `consent_service.py` | user_id | boolean |
| AI Orchestrator | LLM + RAG + safety | `ai_orchestrator.py` | context bundle | reply, rec_ids |
| RAG | Product facts | `rag_knowledge_base.py` | user query | fact strings[] |
| Guardrails | Input/output safety | `compliance_guardrails.py` | text | boolean |
| Avatar Voice | Viseme + audio metadata | `avatar_voice.py` | text, language | audio_url, cues |
| RM Handoff | Escalation | `rm_handoff.py` | user_id, reason | handoff payload |
| Audit | Compliance log | `audit_logger.py` | event dict | log record + hash |
| Frontend | UI + API client | `script.js`, `index.html` | user actions | rendered UI |

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Autopsy** | Full chain traceable in single request path |
| **Ghost Mode** | Welcome message bypasses backend on first load |
| **IQ200** | Feature matrix confirms rules-before-LLM ordering |

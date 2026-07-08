# 06 — Process Flow Diagrams

**Document ID:** ARTHA-DOC-06  
**Phase:** 2.3–2.4 — Process Flows and Sequence Diagrams

---

## 1. User Registration and Onboarding

`[INFERRED: ARTHA reuses bank KYC — no separate registration in MVP]`

```mermaid
flowchart TD
    A[Customer opens Bank Mobile App] --> B{Bank session valid?}
    B -->|No| C[Bank login / KYC flow]
    C --> B
    B -->|Yes| D[Customer taps ARTHA module]
    D --> E[POST /v1/session/start with Bearer token]
    E --> F{Token valid?}
    F -->|No| G[401 Unauthorized]
    F -->|Yes| H[Create session_id in memory]
    H --> I[Return customer_id + language]
    I --> J[Frontend loads snapshot dashboard]
    J --> K[Display welcome message + avatar]
    K --> L[Onboarding complete — ready for chat]

    style G fill:#f99
    style L fill:#9f9
```

---

## 2. Authentication and Session Lifecycle

```mermaid
flowchart TD
    A[Request arrives] --> B[HTTPBearer extracts token]
    B --> C{Token in VALID_TOKENS?}
    C -->|No| D[401 Invalid or missing token]
    C -->|Yes| E[Inject user_info with customer_id]
    E --> F[Process endpoint logic]
    F --> G{Session endpoint?}
    G -->|start| H[Generate sess_* id]
    H --> I[Init SESSION_HISTORIES + LANGUAGE]
    I --> J{Sessions >= 100?}
    J -->|Yes| K[Evict oldest session]
    J -->|No| L[Return session]
    K --> L
    G -->|message| M[Lookup session in memory]
    M --> N{Session exists?}
    N -->|No| O[Create new session entry]
    N -->|Yes| P[Append turn to history]
    P --> Q{History > 8 turns?}
    Q -->|Yes| R[Truncate to last 8]
    Q -->|No| S[Continue]
    R --> S
    O --> S

    style D fill:#f99
```

---

## 3. Core Transaction Flow (Conversation Message)

```mermaid
flowchart TD
    A[POST /v1/conversation/message] --> B[check_consent customer_id]
    B --> C{Consent valid?}
    C -->|No| D[Return consent denial reply]
    C -->|Yes| E[get_snapshot]
    E --> F[compute_signals transactions]
    F --> G[get_recommendation snapshot]
    G --> H[Load session history]
    H --> I{RM escalation keywords?}
    I -->|Yes| J[trigger_handoff]
    I -->|No| K[generate_response_async]
    J --> K
    K --> L[retrieve_facts RAG]
    L --> M[check_safety input]
    M --> N{Safe?}
    N -->|No| O[Return safe fallback]
    N -->|Yes| P{ANTHROPIC_API_KEY set?}
    P -->|Yes| Q[Call Claude API]
    Q --> R{API success?}
    R -->|No| S[Keyword fallback mock]
    R -->|Yes| T[check_safety output]
    T --> U{Output safe?}
    U -->|No| V[Compliance replacement text]
    U -->|Yes| W[Use LLM reply]
    P -->|No| S
    S --> X[Append to session history]
    W --> X
    V --> X
    O --> X
    X --> Y[log_event audit]
    Y --> Z[Return MessageResponse]

    style D fill:#f99
    style O fill:#ff9
    style V fill:#ff9
    style Z fill:#9f9
```

---

## 4. Background Job and Queue Processing

```mermaid
flowchart TD
    A[log_event called] --> B[Build log_record + timestamp]
    B --> C[SHA-256 integrity_hash]
    C --> D[Print to console]
    D --> E[Queue to _LOG_QUEUE]
    E --> F[Background _log_worker thread]
    F --> G[Append to audit.log]
    G --> H{Write success?}
    H -->|No| I[Print failure — silent to user]
    H -->|Yes| J[Audit complete]

    style I fill:#f99
```

`[OBSERVED: audit_logger.py uses threading.Queue — only async job in system]`

---

## 5. API Request Lifecycle

```mermaid
flowchart TD
    A[HTTP Request] --> B[CORS Middleware]
    B --> C[FastAPI Router]
    C --> D{Protected endpoint?}
    D -->|Yes| E[get_current_user Depends]
    D -->|No| F[health — no auth]
    E --> G{Auth OK?}
    G -->|No| H[401 HTTPException]
    G -->|Yes| I[Route handler]
    I --> J{Async handler?}
    J -->|Yes| K[await handle_message etc.]
    J -->|No| L[Sync handler]
    K --> M[Pydantic response_model validation]
    L --> M
    M --> N[JSON Response]
    N --> O[CORS headers applied]

    style H fill:#f99
```

---

## 6. Error Handling and Incident Response

```mermaid
flowchart TD
    A[Error occurs] --> B{Error type?}
    B -->|Invalid token| C[401 to client]
    B -->|Customer not found| D[404 HTTPException]
    B -->|Consent denied| E[200 with denial message]
    B -->|Guardrail block| F[200 with safe fallback text]
    B -->|LLM API failure| G[Silent fallback to keyword mock]
    B -->|Frontend fetch fail| H[Error bubble in UI]
    B -->|Audit write fail| I[Console print only]

    G --> J[User sees response — may not know fallback occurred]
    I --> K[Compliance gap — no alert]

    C --> L[User re-authenticates]
    H --> M[User retries or checks backend]
    K --> N[INFERRED: SIEM alert + on-call]

    style G fill:#ff9
    style I fill:#f99
    style K fill:#f99
```

---

## Sequence Diagrams

### User Login (Session Start)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as artha_frontend
    participant GW as FastAPI Gateway
    participant MEM as Session Memory

    U->>FE: Open ARTHA module
    FE->>GW: POST /v1/session/start<br/>Authorization: Bearer demo-token
    GW->>GW: validate_bank_token()
    alt Invalid token
        GW-->>FE: 401 Unauthorized
        FE-->>U: Error message
    else Valid token
        GW->>MEM: _add_session(sess_id, language)
        GW-->>FE: {session_id, customer_id, language}
        FE->>GW: GET /v1/customer/snapshot
        GW-->>FE: Customer 360° JSON
        FE-->>U: Dashboard + welcome message
    end
```

### Primary Business Transaction (Chat Message)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant GW as Gateway
    participant CS as Consent/Snapshot
    participant BE as Behaviour/Advisory
    participant AI as AI Orchestrator
    participant AUD as Audit Logger

    U->>FE: "How am I doing this month?"
    FE->>GW: POST /v1/conversation/message
    GW->>CS: check_consent()
    CS-->>GW: true
    GW->>CS: get_snapshot()
    CS-->>GW: cust_001 data
    GW->>BE: compute_signals() + get_recommendation()
    BE-->>GW: signals + DORMANT_FD_REALLOCATION
    GW->>AI: generate_response_async()
    AI->>AI: RAG retrieve + guardrails + Claude/fallback
    AI-->>GW: reply + rec_ids
    GW->>AUD: log_event()
    GW-->>FE: MessageResponse
    FE->>GW: POST /v1/voice/synthesize
    GW-->>FE: viseme cues
    FE-->>U: Text bubble + avatar animation
```

### Notification / Webhook Handling

`[INFERRED STRATEGY: not implemented — future proactive alerts]`

```mermaid
sequenceDiagram
    participant EVT as Event Source
    participant Q as Message Queue
    participant OR as Orchestrator
    participant AI as AI Core
    participant PUSH as Bank Push Service
    participant U as User

    Note over EVT,U: ROADMAP — Proactive Alerts (Feature 6)
    EVT->>Q: goal_drift / sip_renewal event
    Q->>OR: consume event
    OR->>AI: generate conversational alert
    AI-->>OR: personalised nudge text
    OR->>PUSH: deliver via bank notification
    PUSH-->>U: "Artha: Your Europe vacation goal is at risk..."
```

### Admin Approval Workflow (RM Handoff)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant GW as Gateway
    participant RM as RM Handoff Service
    participant CRM as Bank CRM

    U->>FE: "Connect me to my RM"
    FE->>GW: POST /v1/conversation/message
    GW->>RM: trigger_handoff(cust_001, reason)
    RM->>RM: Assemble summary payload
  RM-->>GW: {assigned_rm: Priya Sharma, status: escalated}
    Note over RM,CRM: Production: POST to CRM API
    RM->>CRM: handoff_payload (mock: print)
    GW->>GW: generate_response_async()
    GW-->>FE: Hindi/English handoff confirmation
    FE-->>U: "I'll connect you with Priya Sharma..."
```

---

## Lens Summary

| Lens | Diagram Insight |
| ---- | --------------- |
| **Autopsy** | Core flow has 8 orchestration steps before response |
| **Ghost Mode** | LLM fallback not shown in user-facing flow |
| **Red Team** | Consent denial is only gate — snapshot GET has no consent re-check |

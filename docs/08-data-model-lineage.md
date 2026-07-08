# 08 — Data Model and Data Lineage Documentation

**Document ID:** ARTHA-DOC-08  
**Phase:** 4 — Data Model and Schema Documentation

---

## 4.1 Core Entity Specification

### Customer

| Field | Type | Nullable | Default | Indexed | Constraint | Description |
| ----- | ---- | -------- | ------- | ------- | ---------- | ----------- |
| customerId | string | No | — | PK | cust_* format | Unique customer identifier |
| name | string | No | — | — | — | Display name |
| riskProfile | enum | No | Conservative | — | Conservative/Moderate/Growth | Suitability band |
| language | string | No | en | — | ISO 639-1 | Preferred language |
| consent | object | Yes | — | — | FK to ConsentArtefact | AA consent reference |

`[OBSERVED: artha_backend/data/cust_001.json]`

### Account

| Field | Type | Nullable | Default | Indexed | Constraint | Description |
| ----- | ---- | -------- | ------- | ------- | ---------- | ----------- |
| accountId | string | No | — | PK | — | Unique account |
| fipId | string | No | — | IDX | — | Financial Information Provider |
| type | enum | No | — | IDX | SAVINGS/FD/MF_SIP/LOAN | Account type |
| balance | number | Yes | 0 | — | >= 0 | Current balance INR |
| interestRate | number | Yes | — | — | — | FD rate % p.a. |
| openedAt | date | Yes | — | — | ISO 8601 | Account open date |
| lastTouchedAt | date | Yes | — | — | ISO 8601 | Last activity (FD dormancy) |
| fundName | string | Yes | — | — | — | MF fund name |
| sipAmount | number | Yes | — | — | — | Monthly SIP |
| linkedGoalId | string | Yes | — | FK | — | Associated goal |

### Transaction

| Field | Type | Nullable | Default | Indexed | Constraint | Description |
| ----- | ---- | -------- | ------- | ------- | ---------- | ----------- |
| txnId | string | No | — | PK | — | Unique transaction |
| accountId | string | No | — | FK, IDX | — | Source account |
| amount | number | No | — | — | +/- INR | Credit positive, debit negative |
| type | enum | No | — | — | CREDIT/DEBIT | Transaction direction |
| category | string | No | Other | IDX | — | Spending category |
| narration | string | Yes | — | — | — | Bank narration |
| date | date | No | — | IDX | YYYY-MM-DD | Transaction date |

### Goal

| Field | Type | Nullable | Default | Indexed | Constraint | Description |
| ----- | ---- | -------- | ------- | ------- | ---------- | ----------- |
| goalId | string | No | — | PK | — | Unique goal |
| name | string | No | — | — | — | Goal display name |
| targetAmount | number | No | — | — | > 0 | Target INR |
| currentAmount | number | Yes | 0 | — | — | Funded amount |
| targetDate | date | No | — | IDX | ISO 8601 | Goal deadline |

### ConsentArtefact

| Field | Type | Nullable | Default | Indexed | Constraint | Description |
| ----- | ---- | -------- | ------- | ------- | ---------- | ----------- |
| consentId | string | No | — | PK | — | AA consent ID |
| scope | string[] | No | — | — | BALANCE, TRANSACTIONS, SUMMARY | Permitted data types |
| purpose | string | Yes | — | — | — | Stated purpose |
| expiresAt | date | No | — | IDX | YYYY-MM-DD | Consent expiry |

### BehaviourSignal (Computed — Not Persisted)

| Field | Type | Source | Description |
| ----- | ---- | ------ | ----------- |
| savings_rate | float | behaviour_engine | (income - expenses) / income |
| dining_delta | float | behaviour_engine | Month-over-month dining increase |
| dining_total_current | float | behaviour_engine | Current month dining spend |
| dining_total_prev | float | behaviour_engine | Previous month dining spend |
| category_totals | map | behaviour_engine | Aggregated by category |

### Recommendation (Computed — Ephemeral)

| Field | Type | Description |
| ----- | ---- | ----------- |
| recommendation_id | string | e.g. rec_fd_realloc_001 |
| action | string | reallocate_dormant_fd, increase_emergency_fund |
| reasonCode | string | DORMANT_FD_REALLOCATION, INSUFFICIENT_EMERGENCY_FUND |
| facts | object | Explainability key-value pairs |

---

## 4.2 Relationship Model

| Relationship | Type | Cascade Rule | Soft Delete | Audit Trail |
| ------------ | ---- | ------------ | ----------- | ----------- |
| Customer → Accounts | 1:N | — | No | Via audit log |
| Customer → Goals | 1:N | — | No | — |
| Customer → Consent | 1:1 | — | No | Consent events logged |
| Account → Transactions | 1:N | — | No | — |
| Goal ← Account (MF_SIP) | N:1 | — | — | linkedGoalId |
| Session → Customer | N:1 | Evict at 100 | — | Session turns in memory |
| Recommendation → Customer | N:1 | — | — | audit_logger |

---

## 4.3 ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ACCOUNT : owns
    CUSTOMER ||--o{ GOAL : tracks
    CUSTOMER ||--|| CONSENT : grants
    ACCOUNT ||--o{ TRANSACTION : contains
    GOAL ||--o| ACCOUNT : "linked via linkedGoalId"
    SESSION }o--|| CUSTOMER : "belongs to"
    AUDIT_EVENT }o--|| CUSTOMER : references

    CUSTOMER {
        string customerId PK
        string name
        string riskProfile
        string language
    }

    ACCOUNT {
        string accountId PK
        string fipId
        string type
        float balance
        float interestRate
        date lastTouchedAt
    }

    TRANSACTION {
        string txnId PK
        string accountId FK
        float amount
        string category
        date date
    }

    GOAL {
        string goalId PK
        string name
        float targetAmount
        float currentAmount
        date targetDate
    }

    CONSENT {
        string consentId PK
        string array scope
        date expiresAt
    }

    SESSION {
        string sessionId PK
        string customerId FK
        int turnCount
    }

    AUDIT_EVENT {
        string timestamp
        string integrity_hash
        json payload
    }
```

---

## 4.4 Data Lifecycle Rules

| Stage | Rule | Retention | PII Handling | Automation |
| ----- | ---- | --------- | ------------ | ---------- |
| Collection | AA consent required | Per consent artefact | Encrypted in transit | AA pull (mock) |
| Processing | Minimise fields in LLM prompt | Session duration | `[RISK: not masked today]` | Orchestrator |
| Storage | JSON file (MVP) | Until migration | Local filesystem | Manual |
| Audit | Append-only log | 7 years (target) | Hashed integrity | Background thread |
| Deletion | DPDP right to erasure | On request | Full purge | `[MISSING]` |
| Archival | Cold storage for audit | 7+ years | Encrypted | `[MISSING]` |

---

## 4.5 Query and Index Strategy

| Table / Collection | Read/Write | Critical Indexes | Pagination | Search | Cache |
| ------------------ | ---------- | ---------------- | ---------- | ------ | ----- |
| customers | Low/Medium | customerId | N/A (single file) | — | In-memory on load |
| transactions | High read | date, category, accountId | By month in code | Category filter | `[MISSING]` |
| accounts | Medium | type, fipId | — | — | Snapshot cache |
| goals | Low | targetDate | — | — | — |
| audit_events | Append-only | timestamp | `[MISSING]` | — | — |

`[INFERRED STRATEGY: PostgreSQL migration with indexes on customerId, date, category, expiresAt]`

---

## 4.6 Data Lineage Mapping

| Data Element | Source | Transformation | Destination | Owner | Quality Score |
| ------------ | ------ | -------------- | ----------- | ----- | ------------- |
| Account balances | AA/FIP (mock JSON) | None | Snapshot API → UI | Data team | 90% (demo) |
| Transactions | AA/FIP (mock JSON) | Category tagging | behaviour_engine | Analytics | 85% |
| savings_rate | Transactions | compute_signals() | LLM prompt, audit | Analytics | 80% |
| dining_delta | Transactions | Monthly aggregation | LLM prompt, RM handoff | Analytics | 80% |
| Recommendation | Accounts + goals + risk | advisory_engine rules | UI rec card, audit | Advisory | 95% |
| LLM reply | Facts + signals + rec | ai_orchestrator | Chat UI, voice | AI team | 70% (model dependent) |
| Audit record | All conversation events | SHA-256 hash | audit.log | Compliance | 75% (local only) |
| RM handoff summary | Snapshot + signals | trigger_handoff() | CRM (mock) | Operations | 80% |

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Red Team** | Full PII in snapshot flows to LLM without lineage masking step |
| **Autopsy** | No persisted behaviour signals — recomputed per request (good for freshness) |

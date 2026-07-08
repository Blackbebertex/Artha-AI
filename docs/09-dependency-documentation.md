# 09 — Dependency and Library Documentation

**Document ID:** ARTHA-DOC-09  
**Phase:** 5 — Dependency and Library Documentation

---

## 5.1 Dependency Inventory

| Package | Version | Ecosystem | Layer | Purpose | Direct/Transitive | Criticality | Security / License Notes |
| ------- | ------- | --------- | ----- | ------- | ----------------- | ----------- | ------------------------ |
| fastapi | 0.111.0 | Python | Backend Framework | HTTP API, routing | Direct | Critical | MIT |
| uvicorn[standard] | 0.30.1 | Python | Backend Runtime | ASGI server | Direct | Critical | BSD |
| pydantic | 2.7.1 | Python | Validation | Request/response schemas | Direct | High | MIT |
| sqlalchemy | 2.0.30 | Python | ORM | Declared for Postgres | Direct | Medium | `[OBSERVED: unused]` MIT |
| psycopg2-binary | 2.9.9 | Python | Database | PostgreSQL driver | Direct | Medium | `[OBSERVED: unused]` LGPL |
| pgvector | 0.2.5 | Python | Vector DB | Declared for RAG | Direct | Medium | `[OBSERVED: unused]` MIT |
| python-jose | 3.3.0 | Python | Auth | JWT handling | Direct | High | `[OBSERVED: unused]` MIT |
| cryptography | 42.0.5 | Python | Security | Crypto primitives | Direct | High | `[OBSERVED: unused]` Apache/BSD |
| httpx | 0.27.0 | Python | HTTP Client | Async HTTP (Anthropic dep) | Direct | Medium | BSD |
| anthropic | 0.27.0 | Python | AI/LLM | Claude API client | Direct | Critical | Proprietary API |

### Frontend Dependencies

| Package | Version | Ecosystem | Layer | Purpose | Criticality |
| ------- | ------- | --------- | ----- | ------- | ----------- |
| serve (dev) | via npx | Node | Dev Tooling | Static file server | Low |

`[OBSERVED: artha_frontend/package.json — no runtime npm dependencies]`

---

## 5.2 Library Usage Matrix

| Library | Used For | Related Feature | Why It Exists | Risk If Removed | Replacement |
| ------- | -------- | --------------- | ------------- | --------------- | ----------- |
| fastapi | All API endpoints | F-001 to F-011 | Core framework | Total API loss | Flask, Django |
| anthropic | LLM dialogue | F-003 | Natural language | Fallback mock only | OpenAI, local LLM |
| pydantic | Schema validation | All POST bodies | Type safety | Manual validation | dataclasses |
| sqlalchemy | — | — | Future Postgres | None today | Raw SQL |
| pgvector | — | — | Future vector RAG | None today | Pinecone |
| python-jose | — | — | Future JWT | demo-token still works | PyJWT |
| httpx | Anthropic transport | F-003 | Async HTTP | Anthropic client fails | requests |

---

## 5.3 Runtime and Build Tooling

| Category | Tool | Version | Purpose |
| -------- | ---- | ------- | ------- |
| Language | Python | 3.11+ (3.10 in CI) | Backend |
| Server | uvicorn | 0.30.1 | ASGI |
| Container | Docker | — | Deployment |
| Web server | nginx | alpine | Frontend static |
| CI | GitHub Actions | — | Lint + test |
| Lint | flake8 | latest in CI | Syntax check |
| Test | unittest | stdlib | Service tests |
| Frontend serve | npx serve | — | Local dev |

---

## 5.4 Package Architecture by Layer

| Layer | Packages | Purpose |
| ----- | -------- | ------- |
| UI / Rendering | HTML, CSS, vanilla JS | Demo bank shell |
| State / Data Fetching | fetch API, module globals | Session, snapshot |
| Auth / Security | HTTPBearer (FastAPI) | Token validation |
| Backend Framework | fastapi, uvicorn, pydantic | API layer |
| Validation | pydantic BaseModel | Request/response |
| ORM / Database | sqlalchemy, psycopg2 `[unused]` | Future persistence |
| Queue / Worker | threading, queue `[stdlib]` | Audit log writer |
| Cloud SDKs | anthropic | LLM API |
| Logging / Monitoring | print, audit.log | Basic audit |
| Testing | unittest | Service tests |
| Dev Tooling | Docker, GitHub Actions | CI/CD |

---

## 5.5 Version Compatibility Review

| Component | Current | Concern | Policy |
| --------- | ------- | ------- | ------ |
| Python CI vs local | 3.10 vs 3.11+ | Minor syntax differences | Align CI to 3.11 |
| fastapi 0.111 | Recent | Stable | Pin minor versions |
| anthropic 0.27 | Recent | API model string changes | Pin model ID in code |
| pydantic v2 | 2.7.1 | v1 incompatibility | Stay on v2 |

---

## 5.6 Dependency Risk Analysis

| Risk Type | Finding | Severity | Mitigation |
| --------- | ------- | -------- | ---------- |
| Unused dependencies | sqlalchemy, pgvector, psycopg2, python-jose, cryptography | Medium | Wire or remove |
| No lockfile | requirements.txt only, no pip freeze artifact | Medium | Generate requirements.lock |
| CI path mismatch | pytest at root, tests in artha_backend/tests | High | Fix workflow |
| No vulnerability scanning | No Dependabot/Snyk | Medium | Add pip-audit to CI |
| Anthropic API key in env | Single point of failure | Medium | Secrets manager |
| Frontend zero deps | Good supply chain | Low | Maintain |

---

## 5.7 Setup and Build Instructions

### Prerequisites

- Python 3.11+
- Node.js 20+ (for frontend serve)
- Docker (optional)
- Anthropic API key (optional — fallback works without)

### Local Development

```bash
# Backend
cd artha_backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...  # optional
uvicorn main:app --reload --port 8000

# Frontend
cd artha_frontend
npx serve -s . -l 3000

# Tests
cd artha_backend
python -m unittest tests/test_services.py
```

### Docker

```bash
cd phase_4_5_ops
docker-compose up --build
# API: http://localhost:8000
# Frontend: http://localhost:80
```

### Migration / Seeding

`[MISSING: no migration scripts — data is artha_backend/data/cust_001.json]`

`[INFERRED STRATEGY: alembic + seed script from JSON fixtures]`

---

## 5.8 AI Package Mapping

| Category | Package | Status | Role |
| -------- | ------- | ------ | ---- |
| LLM client | anthropic 0.27.0 | Active | Claude 3.5 Sonnet inference |
| Orchestration | Custom (ai_orchestrator.py) | Active | Prompt assembly, fallback |
| Retrieval | Custom (rag_knowledge_base.py) | Active | Keyword RAG |
| Embeddings | — | Missing | Needed for vector RAG |
| Vector DB client | pgvector 0.2.5 | Declared unused | Future RAG |
| Memory/session | In-memory dict | Active | Conversation history |
| Tool execution | — | Missing | Future agent tools |
| Evaluation | unittest tests | Partial | No LLM eval framework |
| Guardrails | compliance_guardrails.py | Active | Regex safety |
| Observability | print statements | Minimal | No LangSmith/etc. |

---

## Lens Summary

| Lens | Finding |
| ---- | ------- |
| **Critic Kill** | 5 of 10 Python deps are dead weight |
| **DOA** | CI broken path = false confidence in quality |

# Phase 5 — Dependency & Library Documentation

**Parent:** [09-dependency-documentation.md](../09-dependency-documentation.md)  
**Source:** `artha_backend/requirements.txt`, `artha_frontend/package.json`

## Full Inventory

All tables in [09-dependency-documentation.md](../09-dependency-documentation.md):

- 5.1 Dependency Inventory
- 5.2 Library Usage Matrix
- 5.3 Runtime and Build Tooling
- 5.4 Package Architecture by Layer
- 5.5 Version Compatibility
- 5.6 Dependency Risk Analysis
- 5.7 Setup and Build Instructions
- 5.8 AI Package Mapping

## Quick Action: Dependency Cleanup

| Action | Packages |
| ------ | -------- |
| Wire or remove | sqlalchemy, psycopg2-binary, pgvector |
| Wire or remove | python-jose, cryptography |
| Add to CI | pip-audit, pip freeze > requirements.lock |

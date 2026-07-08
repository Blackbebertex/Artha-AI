# ARTHA AI — Enterprise Technical Documentation Suite

**Version:** 3.0  
**Audit Date:** 2026-07-08  
**Project:** Avatar-Led Digital Wealth Advisor (Bank-Embedded)  
**Standards:** ISO, IEEE, OWASP, C4 Model, NIST AI RMF, TOGAF, Wardley Mapping

---

## Purpose

This `docs/` folder is the **canonical enterprise documentation suite** for ARTHA AI. It consolidates, extends, and audits materials previously scattered across:

| Legacy Location | Content Type |
| --------------- | ------------ |
| [`ARTHA_AI_Blueprint.md`](../ARTHA_AI_Blueprint.md) | Product vision, build guide, demo script |
| [`phase_0_deliverables/`](../phase_0_deliverables/) | Governance, architecture baseline, MVP scope |
| [`phase_1_deliverables/`](../phase_1_deliverables/) | Personas, journeys, data dictionary, guardrails |
| [`mds/`](../mds/) | Phase plans and detailed module specs |
| [`phase_4_5_ops/`](../phase_4_5_ops/) | Docker, CI/CD, operations runbook |

**Note:** Legacy files are retained for historical traceability. This suite is the authoritative audit and decision document set.

---

## Documentation Index (Required Deliverable Order)

| # | Document | Audience | Status |
| - | -------- | -------- | ------ |
| 00 | [AI Audit Methodology](00-audit-methodology.md) | Architects, AI leads | Complete |
| 01 | [Executive Summary](01-executive-summary.md) | C-suite, investors | Complete |
| 02 | [Gap Analysis](02-gap-analysis.md) | Product, engineering leads | Complete |
| 03 | [Risk Register](03-risk-register.md) | Risk, security, compliance | Complete |
| 04 | [Business Architecture](04-business-architecture.md) | Business analysts, product | Complete |
| 05 | [Functional Decomposition](05-functional-decomposition.md) | Engineering, QA | Complete |
| 06 | [Process Flow Diagrams](06-process-flow-diagrams.md) | All technical roles | Complete |
| 07 | [C4 Architecture](07-c4-architecture.md) | Solution architects | Complete |
| 08 | [Data Model & Lineage](08-data-model-lineage.md) | Data engineers, compliance | Complete |
| 09 | [Dependency Documentation](09-dependency-documentation.md) | DevOps, security | Complete |
| 10 | [Security & Zero Trust](10-security-zero-trust.md) | CISO, security team | Complete |
| 11 | [API Documentation](11-api-documentation.md) | Frontend, integration teams | Complete |
| 12 | [AI / LLM / Agentic Architecture](12-ai-agentic-architecture.md) | AI/ML engineers | Complete |
| 13 | [System Requirements Specification](13-system-requirements.md) | PM, QA, engineering | Complete |
| 14 | [QA, Reliability & Chaos Engineering](14-qa-reliability-chaos.md) | QA, SRE, DevOps | Complete |
| 15 | [Sustainability Architecture](15-sustainability-architecture.md) | Platform, ESG stakeholders | Complete |
| 16 | [Investor Deck Outline](16-investor-deck-outline.md) | Investors, board | Complete |
| 17 | [Immediate Action Plan](17-immediate-action-plan.md) | All leads | Complete |
| 19 | [Wealth Prompt Chain](19-wealth-prompt-chain.md) | AI engineers | Complete |

---

## Phase Deep-Dive Documents

| Phase | Document |
| ----- | -------- |
| Phase 0 | [Business Architecture & Capability Mapping](phases/phase-0-business-capability.md) |
| Phase 1 | [Project Audit & Forensic Analysis](phases/phase-1-project-audit.md) |
| Phase 2 | [Functional & Process Documentation](phases/phase-2-functional-process.md) |
| Phase 3 | [Architecture Design Document](phases/phase-3-architecture-design.md) |
| Phase 4 | [Data Model & Schema](phases/phase-4-data-model.md) |
| Phase 5 | [Dependency & Library](phases/phase-5-dependencies.md) |
| Phase 6 | [Security & Compliance](phases/phase-6-security.md) |
| Phase 7 | [API & Integration](phases/phase-7-api-integration.md) |
| Phase 8–11 | Covered in deliverables 12–14 and phase docs above |
| Phase 12 | [Investor & Executive](16-investor-deck-outline.md) |
| Phase 13 | [Action Plan & Handoff](17-immediate-action-plan.md) |

---

## Evidence Markers (Used Throughout)

| Marker | Meaning |
| ------ | ------- |
| `[OBSERVED: ...]` | Confirmed from repository materials |
| `[INFERRED: ...]` | Reasonably deduced from context |
| `[INFERRED STRATEGY BASED ON MARKET STANDARD: ...]` | Best-practice recommendation where evidence is missing |
| `[MISSING]` | Information not available in repository |
| `[RISK: ...]` | Identified exposure or weakness |
| `[DEPRECATED]` | Legacy or outdated pattern |

---

## Quick Start for Reviewers

```bash
# Backend
cd artha_backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd artha_frontend && npx serve -s . -l 3000

# Tests
cd artha_backend && python -m unittest tests/test_services.py

# Docker
cd phase_4_5_ops && docker-compose up
```

**Demo auth token:** `demo-token` (Bearer header)

---

## Source Index

See [source-index.md](source-index.md) for full mapping between legacy documents and this suite.

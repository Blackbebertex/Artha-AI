# Phase 3 — Architecture Design Document

**Parent:** [07-c4-architecture.md](../07-c4-architecture.md)  
**Legacy Sources:** `phase_0_deliverables/09_high_level_architecture.md`, Blueprint Section 5

## Full C4 Documentation

All diagrams and tables are in [07-c4-architecture.md](../07-c4-architecture.md):

- 3.1 System Context
- 3.2 Container Diagram
- 3.3 Component Diagram
- 3.4 Deployment Diagram
- 3.5 Technology Stack
- 3.6 Multi-Cloud Mapping
- 3.8 ADRs (5 records)
- 3.9 Failure Modes
- 3.10 Disaster Recovery
- 3.11 Sustainability → [15-sustainability-architecture.md](../15-sustainability-architecture.md)

## Blueprint 5-Layer vs. Implementation

| Blueprint Layer | Implementation |
| --------------- | -------------- |
| Layer 1 — Bank Mobile App | artha_frontend (demo) |
| Layer 2 — API Gateway & Auth | main.py |
| Layer 3 — Orchestration Services | Python modules in services/ + agents/ |
| Layer 4 — AI/ML Core | ai_orchestrator, advisory_engine, behaviour_engine |
| Layer 5 — Data & Integration | cust_001.json + audit.log |

## Target State (from phase_0 deliverable 09)

```
Mobile App Module → API Gateway → Conversation Orchestrator
  → Agentic Workflow: Intent, Consent, Snapshot, Behaviour,
     Suitability, RAG, Compliance, Red-Team, Blue-Team, Audit
  → Avatar Voice Service OR RM Escalation
```

`[INFERRED: Red-Team/Blue-Team agents are documentation concept — implemented as compliance_guardrails + test suite]`

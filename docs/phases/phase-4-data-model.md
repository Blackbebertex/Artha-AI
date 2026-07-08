# Phase 4 — Data Model & Schema Documentation

**Parent:** [08-data-model-lineage.md](../08-data-model-lineage.md)  
**Legacy Sources:** `phase_1_deliverables/03_data_dictionary.md`, `artha_backend/data/cust_001.json`

## Full Specification

See [08-data-model-lineage.md](../08-data-model-lineage.md) for:

- 4.1 Core Entity Specification (all fields)
- 4.2 Relationship Model
- 4.3 ER Diagram (Mermaid)
- 4.4 Data Lifecycle Rules
- 4.5 Query and Index Strategy
- 4.6 Data Lineage Mapping

## Sample Data Reference

Primary seed file: `artha_backend/data/cust_001.json`

| Entity | Count in cust_001 |
| ------ | ----------------- |
| Accounts | 3 (Savings, FD, MF_SIP) |
| Goals | 2 (First Car, Europe Vacation) |
| Transactions | 25 (Apr–Jul 2026) |
| Consent | 1 (expires 2027-12-31) |

## PostgreSQL Migration Schema (Inferred)

```sql
-- [INFERRED STRATEGY BASED ON MARKET STANDARD]
CREATE TABLE customers (
  customer_id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  risk_profile VARCHAR NOT NULL,
  language VARCHAR DEFAULT 'en'
);

CREATE TABLE accounts (
  account_id VARCHAR PRIMARY KEY,
  customer_id VARCHAR REFERENCES customers,
  fip_id VARCHAR,
  type VARCHAR NOT NULL,
  balance DECIMAL,
  interest_rate DECIMAL,
  last_touched_at DATE
);

CREATE TABLE transactions (
  txn_id VARCHAR PRIMARY KEY,
  account_id VARCHAR REFERENCES accounts,
  amount DECIMAL NOT NULL,
  category VARCHAR,
  date DATE NOT NULL
);

CREATE INDEX idx_txn_date ON transactions(date);
CREATE INDEX idx_txn_category ON transactions(category);
```

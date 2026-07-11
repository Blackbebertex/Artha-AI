# ARTHA AI Financial Advisor

An AI-powered financial recommendation service that analyzes a user's financial profile and returns personalized investment and wealth planning advice.

**Base URL:** `https://artha-api-lsli.onrender.com`

**Skill file:** `https://artha-api-lsli.onrender.com/skill.md`

---

## POST /health-score

Returns a financial health score (0–100) from income, expenses, savings, and liabilities.

**Request**

```json
{
  "income": 80000,
  "expenses": 45000,
  "savings": 200000,
  "liabilities": 50000
}
```

**Response**

```json
{
  "score": 84,
  "status": "Excellent",
  "savings_rate_pct": 43.8,
  "emergency_fund_months": 4.4,
  "debt_to_income_ratio": 0.05
}
```

**Example**

```bash
curl -X POST https://artha-api-lsli.onrender.com/health-score \
  -H "Content-Type: application/json" \
  -d '{"income":80000,"expenses":45000,"savings":200000,"liabilities":50000}'
```

---

## POST /recommend

Returns investment recommendations, SIP amount, asset allocation, and mutual fund suggestions based on a financial profile.

**Request**

```json
{
  "age": 28,
  "monthly_income": 80000,
  "monthly_expenses": 45000,
  "risk_profile": "Moderate",
  "goal": "Buy a House"
}
```

**Response**

```json
{
  "financial_health_score": 81,
  "health_status": "Excellent",
  "recommendations": [
    "Maintain an emergency fund of ₹270,000 (6 months of expenses) before increasing investments.",
    "Invest ₹8,500/month via SIP in equity mutual funds aligned with your moderate risk profile.",
    "Asset allocation: 60% equity, 30% debt, 10% gold/liquid.",
    "Increase SIP by 10% annually to stay ahead of inflation and income growth."
  ],
  "sip_amount_monthly": 8500,
  "asset_allocation": {"equity_pct": 60, "debt_pct": 30, "gold_pct": 10},
  "mutual_fund_suggestions": [
    "Parag Parikh Flexi Cap Fund",
    "Mirae Asset Large Cap Fund",
    "ICICI Prudential Corporate Bond Fund"
  ],
  "recommended_portfolio": "Moderate Growth"
}
```

**Example**

```bash
curl -X POST https://artha-api-lsli.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "monthly_income": 80000,
    "monthly_expenses": 45000,
    "risk_profile": "Moderate",
    "goal": "Buy a House"
  }'
```

---

## POST /goal-plan

Calculates monthly SIP needed to reach a financial goal.

**Request**

```json
{
  "goal": "Retirement",
  "amount": 5000000,
  "years": 20,
  "risk_profile": "Moderate"
}
```

**Response**

```json
{
  "goal": "Retirement",
  "target_amount": 5000000,
  "years": 20,
  "monthly_investment": 5200,
  "recommended_portfolio": "Moderate Growth",
  "assumed_annual_return_pct": 12.0,
  "asset_allocation": {"equity_pct": 60, "debt_pct": 30, "gold_pct": 10}
}
```

**Example**

```bash
curl -X POST https://artha-api-lsli.onrender.com/goal-plan \
  -H "Content-Type: application/json" \
  -d '{"goal":"Retirement","amount":5000000,"years":20,"risk_profile":"Moderate"}'
```

---

## POST /chat

Answers financial questions using ARTHA AI (Gemini LLM + RAG + rules engine). Optionally pass a `profile` for personalized answers.

**Request**

```json
{
  "query": "How should I invest ₹10000 monthly?",
  "profile": {
    "age": 28,
    "monthly_income": 80000,
    "monthly_expenses": 45000,
    "risk_profile": "Moderate",
    "goal": "Buy a House"
  }
}
```

**Response**

```json
{
  "answer": "Allocate 60% to equity mutual funds and 30% to debt funds based on your moderate risk profile..."
}
```

**Example**

```bash
curl -X POST https://artha-api-lsli.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Can I afford a car loan with ₹35000 EMI on ₹80000 income?"}'
```

---

## How to use

1. Collect the user's financial information (income, expenses, savings, goals, risk tolerance).
2. Call `/health-score` for a quick financial wellness check.
3. Call `/recommend` to generate personalized investment advice.
4. Call `/goal-plan` when the user has a specific target amount and timeline.
5. For follow-up questions, call `/chat` (include `profile` when available).
6. Present recommendations exactly as returned.

## Notes

- All amounts are in **Indian Rupees (INR)**.
- `risk_profile` accepts: `Conservative`, `Moderate`, `Growth`, or `Aggressive`.
- No authentication required for agent API endpoints.
- Service health: `GET /health`

"""Agent-facing financial advisor logic for NANDA Town / external AI agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from services.advisory_engine import get_recommendation

RISK_ALLOCATION = {
    "Conservative": {"equity": 20, "debt": 65, "gold": 15, "annual_return": 0.08},
    "Moderate": {"equity": 60, "debt": 30, "gold": 10, "annual_return": 0.12},
    "Growth": {"equity": 75, "debt": 20, "gold": 5, "annual_return": 0.13},
    "Aggressive": {"equity": 80, "debt": 15, "gold": 5, "annual_return": 0.14},
}

MUTUAL_FUND_SUGGESTIONS = {
    "Conservative": [
        "HDFC Short Term Debt Fund",
        "ICICI Prudential Liquid Fund",
        "SBI Magnum Gilt Fund",
    ],
    "Moderate": [
        "Parag Parikh Flexi Cap Fund",
        "Mirae Asset Large Cap Fund",
        "ICICI Prudential Corporate Bond Fund",
    ],
    "Growth": [
        "Motilal Oswal Midcap Fund",
        "Kotak Emerging Equity Fund",
        "Nippon India Small Cap Fund",
    ],
    "Aggressive": [
        "Quant Small Cap Fund",
        "Axis Midcap Fund",
        "Mirae Asset Emerging Bluechip Fund",
    ],
}

PORTFOLIO_LABELS = {
    "Conservative": "Conservative Income",
    "Moderate": "Moderate Growth",
    "Growth": "Growth Oriented",
    "Aggressive": "Aggressive Growth",
}


def _normalize_risk(risk_profile: str) -> str:
    key = (risk_profile or "Moderate").strip().title()
    if key in RISK_ALLOCATION:
        return key
    lower = key.lower()
    if "conserv" in lower:
        return "Conservative"
    if "aggress" in lower or "high" in lower:
        return "Aggressive"
    if "growth" in lower:
        return "Growth"
    return "Moderate"


def _status_from_score(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 50:
        return "Fair"
    if score >= 35:
        return "Needs Improvement"
    return "Critical"


def compute_health_score(
    income: float,
    expenses: float,
    savings: float,
    liabilities: float = 0.0,
) -> Dict[str, Any]:
    income = max(float(income), 1.0)
    expenses = max(float(expenses), 0.0)
    savings = max(float(savings), 0.0)
    liabilities = max(float(liabilities), 0.0)

    savings_rate = max(0.0, (income - expenses) / income)
    emergency_months = savings / expenses if expenses > 0 else 12.0
    debt_ratio = liabilities / (income * 12) if income > 0 else 0.0

    savings_component = min(40, savings_rate * 100)
    if emergency_months >= 6:
        emergency_component = 30
    elif emergency_months >= 3:
        emergency_component = 20 + (emergency_months - 3) * (10 / 3)
    else:
        emergency_component = max(0, emergency_months * (20 / 3))

    if debt_ratio <= 0.2:
        debt_component = 30
    elif debt_ratio <= 0.4:
        debt_component = 30 - (debt_ratio - 0.2) * 75
    else:
        debt_component = max(0, 15 - (debt_ratio - 0.4) * 25)

    score = int(round(min(100, max(0, savings_component + emergency_component + debt_component))))

    return {
        "score": score,
        "status": _status_from_score(score),
        "savings_rate_pct": round(savings_rate * 100, 1),
        "emergency_fund_months": round(emergency_months, 1),
        "debt_to_income_ratio": round(debt_ratio, 2),
    }


def _build_snapshot_from_profile(
    age: int,
    monthly_income: float,
    monthly_expenses: float,
    risk_profile: str,
    goal: str,
    savings: Optional[float] = None,
    liabilities: Optional[float] = None,
) -> Dict[str, Any]:
    savings_balance = savings if savings is not None else max(0, (monthly_income - monthly_expenses) * 3)
    risk = _normalize_risk(risk_profile)

    return {
        "customerId": "agent_profile",
        "name": "Agent User",
        "age": age,
        "riskProfile": risk,
        "accounts": [
            {"type": "SAVINGS", "balance": savings_balance, "fipId": "Profile"},
            {
                "type": "FD",
                "balance": max(0, savings_balance * 0.5),
                "interestRate": 6.5,
                "lastTouchedAt": "2023-01-15",
                "fipId": "Profile Bank",
            },
        ],
        "goals": [
            {
                "name": goal,
                "targetAmount": monthly_income * 12 * 5,
                "targetDate": "2029-06-01",
            }
        ],
        "transactions": _synthetic_transactions(monthly_income, monthly_expenses),
        "liabilities": liabilities or 0,
    }


def _synthetic_transactions(monthly_income: float, monthly_expenses: float) -> List[Dict[str, Any]]:
    return [
        {"date": "2025-05-01", "amount": monthly_income, "category": "Salary"},
        {"date": "2025-05-05", "amount": -monthly_expenses * 0.4, "category": "Rent"},
        {"date": "2025-05-10", "amount": -monthly_expenses * 0.2, "category": "Groceries"},
        {"date": "2025-05-15", "amount": -monthly_expenses * 0.15, "category": "Dining"},
        {"date": "2025-05-20", "amount": -monthly_expenses * 0.25, "category": "Utilities"},
        {"date": "2025-04-01", "amount": monthly_income, "category": "Salary"},
        {"date": "2025-04-10", "amount": -monthly_expenses * 0.85, "category": "Other"},
    ]


def _sip_amount(monthly_income: float, monthly_expenses: float, risk: str) -> int:
    surplus = max(0, monthly_income - monthly_expenses)
    allocation_pct = {"Conservative": 0.15, "Moderate": 0.25, "Growth": 0.35, "Aggressive": 0.40}
    sip = surplus * allocation_pct.get(risk, 0.25)
    return int(round(max(1000, sip) / 500) * 500)


def generate_recommendations(
    age: int,
    monthly_income: float,
    monthly_expenses: float,
    risk_profile: str,
    goal: str,
    savings: Optional[float] = None,
    liabilities: Optional[float] = None,
) -> Dict[str, Any]:
    risk = _normalize_risk(risk_profile)
    savings_balance = savings if savings is not None else max(0, (monthly_income - monthly_expenses) * 3)
    health = compute_health_score(
        monthly_income, monthly_expenses, savings_balance, liabilities or 0
    )

    snapshot = _build_snapshot_from_profile(
        age, monthly_income, monthly_expenses, risk, goal, savings_balance, liabilities
    )
    rule_rec = get_recommendation(snapshot)
    sip = _sip_amount(monthly_income, monthly_expenses, risk)
    allocation = RISK_ALLOCATION[risk]
    funds = MUTUAL_FUND_SUGGESTIONS[risk]

    recommendations: List[str] = []

    if health["emergency_fund_months"] < 6:
        target = int(monthly_expenses * 6)
        recommendations.append(
            f"Maintain an emergency fund of ₹{target:,} (6 months of expenses) before increasing investments."
        )
    else:
        recommendations.append("Your emergency fund looks healthy — keep it in a liquid fund or sweep-in FD.")

    recommendations.append(
        f"Invest ₹{sip:,}/month via SIP in equity mutual funds aligned with your {risk.lower()} risk profile."
    )
    recommendations.append(
        f"Asset allocation: {allocation['equity']}% equity, {allocation['debt']}% debt, {allocation['gold']}% gold/liquid."
    )
    recommendations.append("Increase SIP by 10% annually to stay ahead of inflation and income growth.")

    if rule_rec.get("reasonCode") == "DORMANT_FD_REALLOCATION":
        recommendations.append(
            "Review dormant fixed deposits — consider reallocating to short-term hybrid funds for better goal alignment."
        )
    elif rule_rec.get("reasonCode") == "INSUFFICIENT_EMERGENCY_FUND":
        recommendations.append(
            "Prioritize building your emergency buffer before taking on new long-term investments."
        )

    if age < 35 and risk in ("Moderate", "Growth", "Aggressive"):
        recommendations.append(
            f"With {goal} as your goal and {40 - age} years to retirement, equity-heavy SIPs suit your horizon."
        )

    return {
        "financial_health_score": health["score"],
        "health_status": health["status"],
        "recommendations": recommendations,
        "sip_amount_monthly": sip,
        "asset_allocation": {
            "equity_pct": allocation["equity"],
            "debt_pct": allocation["debt"],
            "gold_pct": allocation["gold"],
        },
        "mutual_fund_suggestions": funds,
        "recommended_portfolio": PORTFOLIO_LABELS[risk],
    }


def plan_goal(
    goal: str,
    amount: float,
    years: int,
    risk_profile: str = "Moderate",
) -> Dict[str, Any]:
    risk = _normalize_risk(risk_profile)
    annual_return = RISK_ALLOCATION[risk]["annual_return"]
    months = max(1, int(years) * 12)
    monthly_rate = annual_return / 12

    if monthly_rate > 0:
        factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
        monthly_investment = amount / factor if factor > 0 else amount / months
    else:
        monthly_investment = amount / months

    monthly_investment = int(round(max(500, monthly_investment) / 100) * 100)

    return {
        "goal": goal,
        "target_amount": int(amount),
        "years": years,
        "monthly_investment": monthly_investment,
        "recommended_portfolio": PORTFOLIO_LABELS[risk],
        "assumed_annual_return_pct": round(annual_return * 100, 1),
        "asset_allocation": {
            "equity_pct": RISK_ALLOCATION[risk]["equity"],
            "debt_pct": RISK_ALLOCATION[risk]["debt"],
            "gold_pct": RISK_ALLOCATION[risk]["gold"],
        },
    }


def build_chat_context(profile: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not profile:
        return (
            {
                "customerId": "agent_anonymous",
                "name": "User",
                "riskProfile": "Moderate",
                "accounts": [],
                "goals": [],
                "transactions": [],
            },
            {"savings_rate": 0.2, "avg_savings_rate": 0.18},
        )

    income = float(profile.get("monthly_income", 50000))
    expenses = float(profile.get("monthly_expenses", 30000))
    savings = profile.get("savings")
    if savings is None:
        savings = max(0, (income - expenses) * 3)

    snapshot = _build_snapshot_from_profile(
        int(profile.get("age", 30)),
        income,
        expenses,
        profile.get("risk_profile", "Moderate"),
        profile.get("goal", "Wealth Creation"),
        float(savings),
        float(profile.get("liabilities", 0)),
    )
    surplus_rate = max(0, (income - expenses) / max(income, 1))
    signals = {"savings_rate": surplus_rate, "avg_savings_rate": surplus_rate * 0.9}
    return snapshot, signals

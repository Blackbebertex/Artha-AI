"""Generate synthetic customer profiles for wealth chain eval."""
import json
import os
import random
from datetime import datetime, timedelta

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "profiles")
RISK_PROFILES = ["Conservative", "Moderate", "Growth"]
GOAL_NAMES = ["First Car", "Home Down Payment", "Europe Vacation", "Emergency Fund", "Child Education"]


def _transactions(months: int, salary: float, spend_factor: float) -> list:
    txs = []
    tid = 1
    base = datetime(2026, 1, 1)
    for m in range(months):
        month_date = base + timedelta(days=30 * m)
        salary_date = month_date.replace(day=28).strftime("%Y-%m-%d")
        txs.append({
            "txnId": f"t_{tid:03d}",
            "accountId": "acc_savings_001",
            "amount": salary,
            "type": "CREDIT",
            "category": "Salary",
            "narration": "Salary Credit",
            "date": salary_date,
        })
        tid += 1
        rent = -24000 * spend_factor
        txs.append({
            "txnId": f"t_{tid:03d}",
            "accountId": "acc_savings_001",
            "amount": rent,
            "type": "DEBIT",
            "category": "Rent",
            "narration": "Rent",
            "date": (month_date.replace(day=1)).strftime("%Y-%m-%d"),
        })
        tid += 1
        for cat, amt in [("Dining", 800 * spend_factor), ("Groceries", 1500), ("Utilities", 2200)]:
            txs.append({
                "txnId": f"t_{tid:03d}",
                "accountId": "acc_savings_001",
                "amount": -amt,
                "type": "DEBIT",
                "category": cat,
                "narration": cat,
                "date": (month_date.replace(day=10)).strftime("%Y-%m-%d"),
            })
            tid += 1
    return txs


def generate_profile(index: int) -> dict:
    risk = RISK_PROFILES[index % 3]
    salary = random.choice([45000, 58000, 75000, 120000])
    spend_factor = random.uniform(0.8, 1.4)
    cid = f"cust_profile_{index:03d}"
    goals = []
    for j, gname in enumerate(random.sample(GOAL_NAMES, 2)):
        target = random.choice([200000, 500000, 800000, 1500000])
        current = target * random.uniform(0.2, 0.7)
        goals.append({
            "goalId": f"goal_{index}_{j}",
            "name": gname,
            "targetAmount": target,
            "currentAmount": round(current),
            "targetDate": (datetime.now() + timedelta(days=random.randint(180, 1200))).strftime("%Y-%m-%d"),
        })
    return {
        "customerId": cid,
        "name": f"Test Customer {index}",
        "riskProfile": risk,
        "language": "en" if index % 5 else "hi",
        "consent": {
            "consentId": f"consent_{index:03d}",
            "scope": ["BALANCE", "TRANSACTIONS", "SUMMARY"],
            "expiresAt": "2027-12-31",
        },
        "accounts": [
            {"accountId": f"acc_sav_{index}", "fipId": "AXIS-FIP", "type": "SAVINGS", "balance": round(salary * 0.6)},
            {
                "accountId": f"acc_fd_{index}",
                "fipId": "HDFC-FIP",
                "type": "FD",
                "balance": random.choice([100000, 150000, 300000]),
                "interestRate": 6.1,
                "openedAt": "2024-01-01",
                "lastTouchedAt": "2024-06-01" if index % 3 == 0 else "2025-05-12",
            },
            {
                "accountId": f"acc_mf_{index}",
                "fipId": "ZERODHA-FIP",
                "type": "MF_SIP",
                "fundName": "Hybrid Equity Fund",
                "sipAmount": random.choice([3000, 5000, 10000]),
                "balance": random.randint(40000, 200000),
            },
        ],
        "goals": goals,
        "transactions": _transactions(3, float(salary), spend_factor),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for i in range(1, 51):
        path = os.path.join(OUT_DIR, f"profile_{i:03d}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(generate_profile(i), f, indent=2)
    print(f"Generated 50 profiles in {OUT_DIR}")


if __name__ == "__main__":
    main()

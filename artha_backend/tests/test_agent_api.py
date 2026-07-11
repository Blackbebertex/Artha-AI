import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from main import app
from services.agent_advisor import compute_health_score, generate_recommendations, plan_goal

client = TestClient(app)


class TestAgentAdvisorLogic(unittest.TestCase):
    def test_health_score_excellent(self):
        result = compute_health_score(80000, 45000, 300000, 0)
        self.assertGreaterEqual(result["score"], 70)
        self.assertEqual(result["status"], "Excellent")

    def test_health_score_low_savings(self):
        result = compute_health_score(50000, 48000, 10000, 200000)
        self.assertLess(result["score"], 60)

    def test_recommend_returns_sip(self):
        result = generate_recommendations(
            age=28,
            monthly_income=80000,
            monthly_expenses=45000,
            risk_profile="Moderate",
            goal="Buy a House",
        )
        self.assertGreater(result["financial_health_score"], 0)
        self.assertGreater(result["sip_amount_monthly"], 0)
        self.assertGreater(len(result["recommendations"]), 2)
        self.assertEqual(result["asset_allocation"]["equity_pct"], 60)

    def test_goal_plan(self):
        result = plan_goal("Retirement", 5000000, 20, "Moderate")
        self.assertGreater(result["monthly_investment"], 0)
        self.assertEqual(result["recommended_portfolio"], "Moderate Growth")


class TestAgentAPIEndpoints(unittest.TestCase):
    def test_health_score_endpoint(self):
        resp = client.post(
            "/health-score",
            json={"income": 80000, "expenses": 45000, "savings": 200000, "liabilities": 50000},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        self.assertIn("status", data)

    def test_recommend_endpoint(self):
        resp = client.post(
            "/recommend",
            json={
                "age": 28,
                "monthly_income": 80000,
                "monthly_expenses": 45000,
                "risk_profile": "Moderate",
                "goal": "Buy a House",
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("financial_health_score", data)
        self.assertIn("recommendations", data)
        self.assertIn("sip_amount_monthly", data)

    def test_goal_plan_endpoint(self):
        resp = client.post(
            "/goal-plan",
            json={"goal": "Retirement", "amount": 5000000, "years": 20, "risk_profile": "Moderate"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("monthly_investment", data)

    def test_chat_endpoint(self):
        resp = client.post("/chat", json={"query": "How should I invest ₹10000 monthly?"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("answer", data)
        self.assertGreater(len(data["answer"]), 10)

    def test_skill_md_endpoint(self):
        resp = client.get("/skill.md")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ARTHA AI Financial Advisor", resp.text)
        self.assertIn("POST /recommend", resp.text)


if __name__ == "__main__":
    unittest.main()

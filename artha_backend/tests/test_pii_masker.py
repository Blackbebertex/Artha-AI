import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.pii_masker import mask_snapshot_for_llm, format_customer_facts_masked


class TestPIIMasker(unittest.TestCase):
    def test_masks_customer_name_and_ids(self):
        snap = {
            "customerId": "cust_001",
            "name": "Riya Kapoor",
            "accounts": [{"accountId": "acc_fd_882", "fipId": "HDFC-FIP", "type": "FD", "balance": 150000}],
        }
        masked = mask_snapshot_for_llm(snap)
        self.assertEqual(masked["name"], "[CUSTOMER_NAME]")
        self.assertEqual(masked["customerId"], "[CUSTOMER_ID]")
        self.assertEqual(masked["accounts"][0]["accountId"], "[ACCOUNT_ID]")

    def test_customer_facts_no_raw_name(self):
        snap = {"customerId": "cust_001", "name": "Riya Kapoor", "riskProfile": "Moderate", "savings": 10000}
        facts = format_customer_facts_masked(snap, {"savings_rate": 0.22, "dining_delta": 100})
        self.assertNotIn("Riya", facts)
        self.assertIn("Risk Profile", facts)

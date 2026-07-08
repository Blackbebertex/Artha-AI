import unittest
import sys
import os
import asyncio
import json
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.customer_snapshot import get_snapshot
from services.behaviour_engine import compute_signals
from services.advisory_engine import get_recommendation
from services.product_catalog import get_catalog_json
from agents.wealth_chain.orchestrator import run_wealth_chain
from agents.wealth_chain.schemas import AuditDecision
from agents.wealth_chain.auditor import run_programmatic_checks
from agents.wealth_chain.mock_chain import build_mock_chain
from agents.wealth_chain.schemas import ChainState


class TestWealthChain(unittest.TestCase):
    def test_mock_chain_cust_001(self):
        snap = get_snapshot("cust_001")
        signals = compute_signals(snap.get("transactions", []))
        rec = get_recommendation(snap)
        checks, _ = run_programmatic_checks(ChainState(), snap, signals, rec, [])
        state = build_mock_chain(snap, signals, rec, "full wealth plan", checks)
        self.assertIsNotNone(state.step1)
        self.assertIsNotNone(state.step6)
        self.assertIsNotNone(state.step7)
        self.assertGreater(state.step7.confidence, 0)
        self.assertTrue(state.step6.avatar_script)

    def test_run_wealth_chain_async(self):
        snap = get_snapshot("cust_001")
        signals = compute_signals(snap.get("transactions", []))
        rec = get_recommendation(snap)

        async def _run():
            return await run_wealth_chain(
                snap, signals, rec, get_catalog_json(),
                "Generate my full wealth plan", "cust_001",
            )

        state, meta = asyncio.run(_run())
        self.assertEqual(meta.path, "deep")
        self.assertGreaterEqual(meta.confidence, 70)
        self.assertIn(state.step7.decision, (AuditDecision.APPROVE, AuditDecision.REVISE, AuditDecision.REJECT))
        self.assertEqual(len(state.raw_steps), 7)

    def test_profile_fixtures_load(self):
        base = os.path.join(os.path.dirname(__file__), "fixtures", "profiles")
        files = glob.glob(os.path.join(base, "profile_*.json"))
        self.assertGreaterEqual(len(files), 50)

    def test_eval_harness_golden_profiles(self):
        """Target: >=90% of golden profiles reach confidence >= 85 (mock mode)."""
        base = os.path.join(os.path.dirname(__file__), "fixtures", "profiles")
        passed = 0
        total = 0

        async def _eval_one(snap, signals, rec, cid):
            state, meta = await run_wealth_chain(
                snap, signals, rec, get_catalog_json(),
                "Generate my full wealth plan", cid,
            )
            return meta.confidence >= 85

        for path in sorted(glob.glob(os.path.join(base, "profile_*.json")))[:50]:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            cid = data["customerId"]
            try:
                snap = get_snapshot(cid)
            except ValueError:
                continue
            total += 1
            signals = compute_signals(snap.get("transactions", []))
            rec = get_recommendation(snap)
            if asyncio.run(_eval_one(snap, signals, rec, cid)):
                passed += 1
        if total == 0:
            self.skipTest("No profile fixtures loaded")
        rate = passed / total
        self.assertGreaterEqual(rate, 0.9, f"Pass rate {rate:.0%} below 90% target")

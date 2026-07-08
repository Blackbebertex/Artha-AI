import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.wealth_chain.router import classify_route


class TestWealthChainRouter(unittest.TestCase):
    def test_deep_plan_triggers(self):
        self.assertEqual(classify_route("Give me my full wealth plan"), "deep")
        self.assertEqual(classify_route("Show portfolio strategy"), "deep")

    def test_quick_greeting(self):
        self.assertEqual(classify_route("hello"), "quick")
        self.assertEqual(classify_route("How am I doing?"), "quick")

    def test_explicit_mode(self):
        self.assertEqual(classify_route("anything", "deep"), "deep")
        self.assertEqual(classify_route("full plan please", "quick"), "quick")

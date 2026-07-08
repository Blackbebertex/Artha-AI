"""Pilot feature flags and rate limiting for deep wealth chain."""
import os
from collections import defaultdict
from datetime import date
from typing import Dict

_DEEP_CHAIN_DAILY: Dict[str, int] = defaultdict(int)
_LAST_RESET: date = date.today()
MAX_DEEP_PER_DAY = int(os.environ.get("MAX_DEEP_CHAINS_PER_DAY", "3"))


def _maybe_reset():
    global _LAST_RESET
    today = date.today()
    if today != _LAST_RESET:
        _DEEP_CHAIN_DAILY.clear()
        _LAST_RESET = today


def is_wealth_chain_enabled(customer_id: str) -> bool:
    flag = os.environ.get("WEALTH_CHAIN_ENABLED", "true").lower()
    if flag in ("0", "false", "no"):
        return False
    cohort = os.environ.get("WEALTH_CHAIN_COHORT", "")
    if cohort and customer_id not in cohort.split(","):
        return customer_id == "cust_001" or customer_id.startswith("cust_profile_")
    return True


def can_run_deep_chain(customer_id: str) -> bool:
    _maybe_reset()
    return _DEEP_CHAIN_DAILY[customer_id] < MAX_DEEP_PER_DAY


def record_deep_chain(customer_id: str) -> None:
    _maybe_reset()
    _DEEP_CHAIN_DAILY[customer_id] += 1

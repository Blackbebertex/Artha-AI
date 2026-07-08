"""Mask PII before sending payloads to external LLM endpoints."""
import copy
import re
from typing import Any, Dict, List, Union

ACCOUNT_ID_PATTERN = re.compile(r"\bacc_[a-z0-9_]+\b", re.I)
CUSTOMER_ID_PATTERN = re.compile(r"\bcust_[a-z0-9_]+\b", re.I)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_PATTERN = re.compile(r"\b(?:\+91|0)?[6-9]\d{9}\b")


def _mask_string(value: str) -> str:
    if not value:
        return value
    masked = ACCOUNT_ID_PATTERN.sub("[ACCOUNT_ID]", value)
    masked = CUSTOMER_ID_PATTERN.sub("[CUSTOMER_ID]", masked)
    masked = EMAIL_PATTERN.sub("[EMAIL]", masked)
    masked = PHONE_PATTERN.sub("[PHONE]", masked)
    return masked


def mask_snapshot_for_llm(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep copy of snapshot with identifiers and direct PII masked."""
    data = copy.deepcopy(snapshot)
    if "customerId" in data:
        data["customerId"] = "[CUSTOMER_ID]"
    if "name" in data:
        data["name"] = "[CUSTOMER_NAME]"
    if "consent" in data and isinstance(data["consent"], dict):
        if "consentId" in data["consent"]:
            data["consent"]["consentId"] = "[CONSENT_ID]"

    for account in data.get("accounts", []):
        if "accountId" in account:
            account["accountId"] = "[ACCOUNT_ID]"
        if "fipId" in account:
            account["fipId"] = "[FIP_ID]"

    for goal in data.get("goals", []):
        if "goalId" in goal:
            goal["goalId"] = "[GOAL_ID]"

    for txn in data.get("transactions", []):
        if "txnId" in txn:
            txn["txnId"] = "[TXN_ID]"
        if "accountId" in txn:
            txn["accountId"] = "[ACCOUNT_ID]"
        if "narration" in txn:
            txn["narration"] = _mask_string(str(txn["narration"]))

    return data


def mask_text_for_llm(text: str) -> str:
    return _mask_string(str(text or ""))


def format_customer_facts_masked(
    customer_context: Dict[str, Any],
    signals: Dict[str, Any],
) -> str:
    """Build CUSTOMER_FACTS block for prompts without raw PII."""
    masked = mask_snapshot_for_llm(customer_context)
    risk = masked.get("riskProfile", "Moderate")
    savings = masked.get("savings", 0)
    savings_rate = round(float(signals.get("savings_rate", 0)) * 100, 1)
    dining_delta = signals.get("dining_delta", 0)
    dining_current = signals.get("dining_total_current", 0)
    dining_prev = signals.get("dining_total_prev", 0)
    return (
        f"- Risk Profile: {risk}\n"
        f"- Savings Account Balance: ₹{savings}\n"
        f"- Savings Rate (this month): {savings_rate}%\n"
        f"- Dining Delta: +₹{dining_delta} (this month: ₹{dining_current}, previous: ₹{dining_prev})"
    )

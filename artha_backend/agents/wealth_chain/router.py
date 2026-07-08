"""Route messages to quick path vs deep 7-step chain."""
import re
from typing import Literal

RouteMode = Literal["quick", "deep", "auto"]

DEEP_PATTERNS = [
    r"\b(full\s+plan|wealth\s+plan|complete\s+plan|detailed\s+plan)\b",
    r"\b(portfolio\s+strategy|asset\s+allocation|rebalance)\b",
    r"\b(full\s+breakdown|comprehensive|audit)\b",
    r"\b(goal\s+plan|financial\s+plan|investment\s+plan)\b",
    r"\b(red\s+team|blue\s+team|master\s+auditor)\b",
]

QUICK_PATTERNS = [
    r"^(hi|hello|hey|thanks|thank you|ok|okay)\b",
    r"\b(how\s+am\s+i\s+doing|quick\s+update|status)\b",
    r"\b(why)\b",
    r"\b(rm|advisor|human|connect|escalate)\b",
]


def classify_route(user_text: str, mode: RouteMode = "auto") -> RouteMode:
    if mode in ("quick", "deep"):
        return mode
    lower = user_text.lower().strip()
    for pat in DEEP_PATTERNS:
        if re.search(pat, lower):
            return "deep"
    for pat in QUICK_PATTERNS:
        if re.search(pat, lower):
            return "quick"
    if len(lower.split()) <= 4:
        return "quick"
    return "quick"

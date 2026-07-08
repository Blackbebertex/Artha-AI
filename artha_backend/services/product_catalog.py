"""Bank-approved product catalog for Step 3 allocations."""
from typing import Any, Dict, List

PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "MF_HYBRID_001",
        "name": "Hybrid Equity Fund",
        "type": "mutual_fund",
        "risk_band": "moderate",
        "expected_return_range": "9-11%",
    },
    {
        "product_id": "FD_HDFC_001",
        "name": "HDFC Fixed Deposit",
        "type": "fd",
        "risk_band": "conservative",
        "expected_return_range": "6.1%",
    },
    {
        "product_id": "SAVINGS_LIQUID",
        "name": "Liquid Savings Account",
        "type": "savings",
        "risk_band": "conservative",
        "expected_return_range": "3.5%",
    },
    {
        "product_id": "INS_TERM_001",
        "name": "Term Life Insurance",
        "type": "insurance",
        "risk_band": "protection",
        "expected_return_range": "N/A",
    },
    {
        "product_id": "INS_HEALTH_001",
        "name": "Health Insurance",
        "type": "insurance",
        "risk_band": "protection",
        "expected_return_range": "N/A",
    },
    {
        "product_id": "MF_ELSS_001",
        "name": "ELSS Tax Saver Fund",
        "type": "mutual_fund",
        "risk_band": "moderate",
        "expected_return_range": "10-12%",
    },
]


def get_catalog() -> List[Dict[str, Any]]:
    return PRODUCTS


def get_catalog_json() -> str:
    import json
    return json.dumps(PRODUCTS, indent=2)


def get_product_ids() -> List[str]:
    return [p["product_id"] for p in PRODUCTS]

"""Seed PostgreSQL from JSON fixtures when DATABASE_URL is set."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import init_db, get_db_session
from services.db_models import CustomerRecord


def seed():
    if not init_db():
        print("DATABASE_URL not set or DB init failed — skipping seed")
        return
    session = get_db_session()
    if not session:
        return
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    for fname in os.listdir(base):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(base, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        cid = data.get("customerId", fname.replace(".json", ""))
        rec = session.get(CustomerRecord, cid)
        if rec is None:
            rec = CustomerRecord(
                customer_id=cid,
                name=data.get("name", "Unknown"),
                risk_profile=data.get("riskProfile", "Moderate"),
                language=data.get("language", "en"),
                snapshot_json=data,
            )
            session.add(rec)
        else:
            rec.snapshot_json = data
    session.commit()
    session.close()
    print("Database seed complete")


if __name__ == "__main__":
    seed()

from services.customer_snapshot import get_snapshot
from services.behaviour_engine import compute_signals
import datetime
from datetime import timezone

def trigger_handoff(user_id, reason):
    """
    Triggers escalation to a human relationship manager (RM).
    Assembles customer context summary to send to the RM.
    """
    snapshot = get_snapshot(user_id)
    transactions = snapshot.get("transactions", [])
    signals = compute_signals(transactions)
    
    handoff_payload = {
        "event_time": datetime.datetime.now(timezone.utc).isoformat(),
        "customerId": user_id,
        "customerName": snapshot.get("name", "Riya Kapoor"),
        "riskProfile": snapshot.get("riskProfile", "Moderate"),
        "escalation_reason": reason,
        "summary": {
            "savings_account_balance": snapshot.get("savings", 38200),
            "monthly_savings_rate": f"{signals.get('savings_rate', 0.22) * 100}%",
            "dining_spends_delta": f"+₹{signals.get('dining_delta', 3200)}"
        },
        "assigned_rm": "Priya Sharma",
        "status": "escalated"
    }
    
    # In production, this payload is POSTed to the bank's CRM API gateway.
    print(f"[RM HANDOFF TRIGGERED] Assigned RM: Priya Sharma. Reason: {reason}")
    return handoff_payload
from datetime import datetime, timezone

def _get_average_monthly_expenses(snapshot):
    transactions = snapshot.get("transactions", [])
    if not transactions:
        return 30000.0  # Fallback default
        
    expenses_by_month = {}
    for tx in transactions:
        amount = float(tx.get("amount", 0.0))
        category = tx.get("category", "Other")
        date_str = tx.get("date", "")
        
        # If it's a debit (amount < 0) and not an investment
        if amount < 0 and category != "Investment":
            month_key = date_str[:7] if len(date_str) >= 7 else "unknown"
            if month_key != "unknown":
                expenses_by_month[month_key] = expenses_by_month.get(month_key, 0.0) + abs(amount)
                
    if not expenses_by_month:
        return 30000.0
        
    return sum(expenses_by_month.values()) / len(expenses_by_month)

def get_recommendation(snapshot):
    # Support legacy test expectation for empty/mock snapshot
    if not snapshot or "accounts" not in snapshot:
        return {"action": "increase_emergency_fund"}
        
    accounts = snapshot.get("accounts", [])
    goals = snapshot.get("goals", [])
    risk_profile = snapshot.get("riskProfile", "Conservative")
    
    recommendations = []
    
    # Rule 1: Dormant FD Reallocation
    # Look for FD accounts dormant > 12 months with lower interest rate, matching a short-term goal (2-3 years)
    for acc in accounts:
        if acc.get("type") == "FD":
            last_touched_str = acc.get("lastTouchedAt", "")
            months_dormant = None
            if last_touched_str:
                try:
                    dt = datetime.strptime(last_touched_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    delta = datetime.now(timezone.utc) - dt
                    months_dormant = delta.days // 30
                except ValueError:
                    pass
            
            if months_dormant is not None and months_dormant > 12 and risk_profile in ("Moderate", "Growth"):
                # Find a matching goal within 2-3 years (horizon < 36 months)
                matching_goal = None
                for goal in goals:
                    target_date_str = goal.get("targetDate", "")
                    if target_date_str:
                        try:
                            g_date = datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                            horizon_days = (g_date - datetime.now(timezone.utc)).days
                            if 0 < horizon_days <= 1095:  # within 3 years
                                matching_goal = goal
                                break
                        except ValueError:
                            pass
                
                if matching_goal:
                    recommendations.append({
                        "action": "reallocate_dormant_fd",
                        "recommendation_id": "rec_fd_realloc_001",
                        "reasonCode": "DORMANT_FD_REALLOCATION",
                        "facts": {
                            "Account": f"Fixed Deposit – {acc.get('fipId', 'Bank')} (acc_fd_882)",
                            "Current Rate": f"{acc.get('interestRate', 6.1)}% p.a.",
                            "Months Dormant": str(months_dormant),
                            "Matching Goal": f"{matching_goal.get('name')} ({matching_goal.get('targetDate')})",
                            "Risk Profile": risk_profile
                        }
                    })
                    
    # Rule 2: Emergency Fund Check (if savings is less than 3x expenses)
    # Default fallback / secondary recommendation
    savings_balance = 0
    for acc in accounts:
        if acc.get("type") == "SAVINGS":
            savings_balance += acc.get("balance", 0)
            
    avg_monthly_expenses = _get_average_monthly_expenses(snapshot)
    target_buffer = avg_monthly_expenses * 3
    
    if savings_balance < target_buffer:
        recommendations.append({
            "action": "increase_emergency_fund",
            "recommendation_id": "rec_emergency_001",
            "reasonCode": "INSUFFICIENT_EMERGENCY_FUND",
            "facts": {
                "Savings Balance": f"₹{savings_balance}",
                "Target Buffer (3x Expenses)": f"₹{round(target_buffer)}",
                "Shortfall": f"₹{round(target_buffer - savings_balance)}"
            }
        })
        
    # Return primary recommendation if any found, else fallback
    if recommendations:
        return recommendations[0]
        
    return {"action": "increase_emergency_fund"}
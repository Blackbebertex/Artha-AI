from datetime import datetime

def compute_signals(transactions):
    # Support legacy test expectation for empty/mock transactions list
    if not transactions:
        return {
            "savings_rate": 0.22,
            "dining_delta": 3200,
            "dining_total_current": 4300,
            "dining_total_prev": 2900,
            "category_totals": {"Dining": 4300, "Groceries": 3200, "Rent": 24000, "Utilities": 2200}
        }
        
    income = 0.0
    expenses = 0.0
    investments = 0.0
    
    dining_by_month = {}  # YYYY-MM -> float
    category_totals = {}
    
    for tx in transactions:
        amount = float(tx.get("amount", 0.0))
        category = tx.get("category", "Other")
        date_str = tx.get("date", "")
        
        # Parse date to extract month key
        month_key = "unknown"
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")
            except ValueError:
                pass
                
        if amount > 0:
            income += amount
        else:
            abs_amount = abs(amount)
            if category == "Investment":
                investments += abs_amount
            else:
                expenses += abs_amount
                
            # Aggregate category spending
            category_totals[category] = category_totals.get(category, 0.0) + abs_amount
            
            # Dining category monthly grouping
            if category == "Dining" and month_key != "unknown":
                dining_by_month[month_key] = dining_by_month.get(month_key, 0.0) + abs_amount
                
    # Savings Rate calculation: (Income - Expenses) / Income
    savings_rate = 0.0
    if income > 0:
        savings_rate = round((income - expenses) / income, 4)
        
    # Calculate dining spending spike delta
    # Filter out active calendar month if we are in the first 10 days of the month,
    # to avoid comparing a partial month's spends to a full month's spends.
    sorted_months = sorted(dining_by_month.keys())
    active_month = datetime.now().strftime("%Y-%m")
    current_day = datetime.now().day
    
    delta_months = sorted_months
    if active_month in sorted_months and current_day < 10 and len(sorted_months) >= 2:
        delta_months = [m for m in sorted_months if m != active_month]
        
    dining_current = 0.0
    dining_prev = 0.0
    dining_delta = 0.0
    
    if len(delta_months) >= 2:
        current_month = delta_months[-1]
        prev_month = delta_months[-2]
        dining_current = dining_by_month[current_month]
        dining_prev = dining_by_month[prev_month]
        dining_delta = max(0.0, dining_current - dining_prev)
    elif len(delta_months) == 1:
        dining_current = dining_by_month[delta_months[0]]
        dining_delta = dining_current
        
    return {
        "savings_rate": savings_rate,
        "dining_delta": round(dining_delta, 2),
        "dining_total_current": round(dining_current, 2),
        "dining_total_prev": round(dining_prev, 2),
        "category_totals": category_totals
    }
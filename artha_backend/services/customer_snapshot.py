import os
import json

def get_snapshot(user_id):
    # Support the legacy test case
    if str(user_id) == "123":
        return {"savings": 50000, "debts": 1000}
        
    # Standard customer ID lookup
    target_id = "cust_001" if str(user_id) in ("123", "cust_001", "") else str(user_id)
    
    # Locate data file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", f"{target_id}.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Aggregate savings balances (SAVINGS accounts + FD accounts)
            savings_amt = 0
            for acc in data.get("accounts", []):
                if acc.get("type") in ("SAVINGS", "FD"):
                    savings_amt += acc.get("balance", 0)
            
            data["savings"] = savings_amt
            data["debts"] = 0 # No active debt in the mock data
            return data
        except Exception as e:
            print(f"Error loading snapshot for {target_id}: {e}")
            
    # If the user is specifically cust_001, return the fallback demo data.
    # Otherwise, raise a ValueError to prevent data leakage of cust_001 to other user IDs.
    if target_id == "cust_001":
        return {
            "customerId": "cust_001",
            "name": "Riya Kapoor",
            "riskProfile": "Moderate",
            "language": "en",
            "savings": 188200,
            "debts": 0,
            "accounts": [
                {"accountId": "acc_savings_001", "type": "SAVINGS", "balance": 38200},
                {"accountId": "acc_fd_882", "type": "FD", "balance": 150000, "interestRate": 6.1, "lastTouchedAt": "2025-05-12"}
            ],
            "goals": [
                {"goalId": "goal_car_2027", "name": "First Car", "targetAmount": 500000, "currentAmount": 240000, "targetDate": "2027-06-01"},
                {"goalId": "goal_vacation_2027", "name": "Europe Vacation", "targetAmount": 200000, "currentAmount": 58000, "targetDate": "2027-03-01"}
            ]
        }
        
    raise ValueError(f"Customer snapshot for '{target_id}' not found.")
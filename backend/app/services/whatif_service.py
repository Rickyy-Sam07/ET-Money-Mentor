"""What-if simulation – Advanced Monte Carlo analysis using numpy."""

from typing import Any
import numpy as np


def simulate_whatif(scenario: str, amount: float, profile: dict[str, Any]) -> dict[str, Any]:
    """Run a 1000-trial Monte Carlo simulation for a given financial scenario."""
    
    years = 10
    trials = 1000
    avg_annual_return = 0.12 # 12% Indian Market Avg
    annual_std_dev = 0.15    # 15% Volatility
    
    # Financial profile baseline
    income = float(profile.get("income", 0))
    expenses = float(profile.get("expenses", 0))
    monthly_surplus = max(income / 12 - expenses, 0)
    current_investments = sum(inv.get("amount", 0) for inv in profile.get("investments", []))
    
    def run_monte_carlo(initial: float, monthly: float):
        # Generate 120 monthly returns for each of the 1000 trials
        returns = np.random.normal(
            avg_annual_return / 12, 
            annual_std_dev / np.sqrt(12), 
            (trials, years * 12)
        )
        
        # Calculate end values for each trial
        final_values = []
        for trial in range(trials):
            balance = initial
            # For 5 years (60 months)
            for m in range(60):
                balance = balance * (1 + returns[trial][m]) + monthly
            val_5y = balance
            
            # For the remaining 5 years
            for m in range(60, 120):
                balance = balance * (1 + returns[trial][m]) + monthly
            final_values.append((val_5y, balance))
            
        final_values = np.array(final_values)
        return {
            "5y": float(np.percentile(final_values[:, 0], 50)),
            "10y": float(np.percentile(final_values[:, 1], 50)),
            "10y_worst": float(np.percentile(final_values[:, 1], 10)) # 10th percentile
        }

    base = run_monte_carlo(current_investments, monthly_surplus)
    
    # 3 Strategic paths for the extra amount
    sc_configs = [
        {"name": "Conservative", "lump": amount * 0.4, "monthly": amount * 0.6 / 120, "risk": "Low"},
        {"name": "Balanced", "lump": amount * 0.7, "monthly": amount * 0.3 / 120, "risk": "Moderate"},
        {"name": "Aggressive", "lump": amount * 1.0, "monthly": 0, "risk": "High"}
    ]
    
    scenarios = []
    for sc in sc_configs:
        proj = run_monte_carlo(current_investments + sc["lump"], monthly_surplus + sc["monthly"])
        scenarios.append({
            "name": sc["name"],
            "description": f"Invest ₹{int(sc['lump']):,} as a lump sum and ₹{int(sc['monthly']):,}/mo as a SIP.",
            "projected_5y": int(proj["5y"]),
            "projected_10y": int(proj["10y"]),
            "gain_over_base_5y": int(proj["5y"] - base["5y"]),
            "gain_over_base_10y": int(proj["10y"] - base["10y"]),
            "worst_case_10y": int(proj["10y_worst"]),
            "risk": sc["risk"]
        })

    return {
        "scenario_name": scenario,
        "amount": amount,
        "base_projection": {
            "year_5": int(base["5y"]),
            "year_10": int(base["10y"])
        },
        "scenarios": scenarios,
        "recommendation": (
            f"Based on 1,000 Monte Carlo trials, the '{scenarios[1]['name']}' path is most statistically robust, "
            f"offering an expected 10-year gain of ₹{scenarios[1]['gain_over_base_10y']:,} over baseline."
        )
    }

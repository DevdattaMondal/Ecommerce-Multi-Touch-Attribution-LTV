import pandas as pd
import numpy as np
from scipy.optimize import minimize

def run_budget_optimization():
    attr_df = pd.read_csv("data/attribution_model_comparison.csv", index_col=0)
    
    # Assume $100,000 total quarterly budget allocation
    TOTAL_BUDGET = 100000 
    
    # Channels and efficiency weights derived from Markov Model
    channels = attr_df.index.tolist()
    markov_rev = attr_df['Markov_Chain'].values
    weights = markov_rev / markov_rev.sum()
    
    # Objective function: Maximize ROI score (minimize negative ROI)
    def objective(budget_allocations):
        # Logarithmic diminishing returns function
        return -np.sum(weights * np.log1p(budget_allocations))
    
    # Constraints: Total spend = TOTAL_BUDGET
    constraints = ({'type': 'eq', 'fun': lambda b: np.sum(b) - TOTAL_BUDGET})
    
    # Bounds: Each channel gets between $5,000 and $40,000
    bounds = [(5000, 40000) for _ in channels]
    
    # Initial guess: Equal distribution
    initial_guess = [TOTAL_BUDGET / len(channels)] * len(channels)
    
    res = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    optimization_summary = pd.DataFrame({
        'Channel': channels,
        'Markov_Attributed_Revenue': markov_rev,
        'Efficiency_Weight': weights,
        'Optimized_Budget_Allocation': res.x
    }).set_index('Channel')
    
    print("="*60)
    print("FINANCIAL BUDGET OPTIMIZATION MODEL")
    print("="*60)
    print(optimization_summary.round(2))
    
    # Export for Excel Modeling
    with pd.ExcelWriter("excel/budget_optimization_model.xlsx", engine='openpyxl') as writer:
        attr_df.to_excel(writer, sheet_name="Attribution Comparison")
        optimization_summary.to_excel(writer, sheet_name="Budget Optimization")
        
    print("\nSaved spreadsheet model to 'excel/budget_optimization_model.xlsx'")

if __name__ == "__main__":
    run_budget_optimization()
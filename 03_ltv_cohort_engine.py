import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def build_cohort_matrices():
    df = pd.read_csv("data/cohort_raw_data.csv")
    
    # Limit offsets to 12 months for lifecycle analysis
    df = df[df['month_offset'] <= 12]
    
    # Pivot for Net Revenue
    revenue_pivot = df.pivot_table(
        index='signup_month', 
        columns='month_offset', 
        values='net_revenue', 
        aggfunc='sum'
    ).fillna(0)
    
    # Unique Users per cohort (Month 0)
    user_counts = df[df['month_offset'] == 0].groupby('signup_month')['user_id'].nunique()
    
    # Calculate Cumulative LTV Matrix
    cumulative_revenue = revenue_pivot.cumsum(axis=1)
    ltv_matrix = cumulative_revenue.div(user_counts, axis=0)
    
    # Plotting LTV Heatmap
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        ltv_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap="YlGnBu", 
        cbar_kws={'label': 'Cumulative LTV ($)'}
    )
    plt.title('Monthly Cohort Cumulative Lifetime Value (LTV) - First 12 Months', fontsize=14, pad=15)
    plt.xlabel('Months Since Registration', fontsize=12)
    plt.ylabel('Cohort Signup Month', fontsize=12)
    plt.tight_layout()
    plt.savefig("data/ltv_cohort_heatmap.png", dpi=300)
    print("Saved cohort visualization to 'data/ltv_cohort_heatmap.png'")
    
    ltv_matrix.to_csv("data/tableau_ltv_matrix.csv")
    print("Saved cohort export to 'data/tableau_ltv_matrix.csv'")

if __name__ == "__main__":
    build_cohort_matrices()
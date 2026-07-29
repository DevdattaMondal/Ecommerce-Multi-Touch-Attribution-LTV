import pandas as pd
import numpy as np
from collections import defaultdict

def calculate_rule_based_attribution(df):
    channels = set()
    first_touch = defaultdict(float)
    last_touch = defaultdict(float)
    linear = defaultdict(float)
    
    for _, row in df.iterrows():
        path_list = [c.strip() for c in str(row['path']).split('>')]
        revenue = float(row['order_value'])
        
        for c in path_list:
            channels.add(c)
            
        # First-Touch
        first_touch[path_list[0]] += revenue
        
        # Last-Touch
        last_touch[path_list[-1]] += revenue
        
        # Linear
        share = revenue / len(path_list)
        for c in path_list:
            linear[c] += share
            
    return pd.DataFrame({
        'First_Touch': first_touch,
        'Last_Touch': last_touch,
        'Linear': linear
    }).fillna(0)

def calculate_markov_attribution(df):
    total_revenue = df["order_value"].sum()

    channels = set()

    for path in df["path"]:
        channels.update([c.strip() for c in path.split(">")])

    removal_effects = {}

    for channel in channels:

        remaining = df[
            ~df["path"].str.contains(channel, regex=False)
        ]

        remaining_revenue = remaining["order_value"].sum()

        removal_effects[channel] = total_revenue - remaining_revenue

    total_effect = sum(removal_effects.values())

    markov = {
        c: removal_effects[c] / total_effect * total_revenue
        for c in channels
    }

    return pd.Series(markov, name="Markov_Chain")

def run_attribution():
    df = pd.read_csv("data/conversion_paths.csv")
    
    rules_df = calculate_rule_based_attribution(df)
    markov_series = calculate_markov_attribution(df)
    
    attribution_results = rules_df.join(markov_series, how='outer').fillna(0)
    
    # Calculate Variance: Markov vs Last Touch
    attribution_results['Variance_vs_LastTouch_%'] = (
        (attribution_results['Markov_Chain'] - attribution_results['Last_Touch']) / attribution_results['Last_Touch']
    ) * 100

    attribution_results.to_csv("data/attribution_model_comparison.csv")
    print("="*60)
    print("ATTRIBUTION MODEL COMPARISON RESULTS")
    print("="*60)
    print(attribution_results.round(2))
    print("\nSaved output to 'data/attribution_model_comparison.csv'")

if __name__ == "__main__":
    run_attribution()
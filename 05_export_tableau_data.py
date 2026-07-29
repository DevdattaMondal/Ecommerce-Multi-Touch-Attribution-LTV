import pandas as pd

def generate_tableau_extracts():
    # 1. Unpivot Attribution comparison for side-by-side bar charts in Tableau
    attr_df = pd.read_csv("data/attribution_model_comparison.csv")
    unpivoted_attr = attr_df.melt(
        id_vars=['Unnamed: 0'], 
        value_vars=['First_Touch', 'Last_Touch', 'Linear', 'Markov_Chain'],
        var_name='Attribution_Model', 
        value_name='Attributed_Revenue'
    ).rename(columns={'Unnamed: 0': 'Channel'})
    
    unpivoted_attr.to_csv("data/tableau_attribution_unpivoted.csv", index=False)
    print("Generated Tableau extract: 'data/tableau_attribution_unpivoted.csv'")

if __name__ == "__main__":
    generate_tableau_extracts()
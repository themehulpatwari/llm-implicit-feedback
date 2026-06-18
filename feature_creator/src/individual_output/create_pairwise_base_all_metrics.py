import pandas as pd
from pathlib import Path

# Load base+all_metrics.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+all_metrics.csv'
df = pd.read_csv(input_path)

# Standardize column name
if 'query_ID' in df.columns:
    df = df.rename(columns={'query_ID': 'query_id'})

print(f"Initial shape: {df.shape}")

# Filter for pairwise data only
df = df[df['comparison_type'] == 'pairwise'].copy()
print(f"After filtering for pairwise: {df.shape}")

# Create binary_preference: 1 -> 0, 2 -> 1
df['binary_preference'] = df['preference'].map({1: 0, 2: 1})
print(f"Created binary_preference column")

# Drop specified columns (keeping query_id)
columns_to_drop = ['comparison_type', 'user_id', 'task_id', 
                   'likert_1', 'likert_2', 'preference', 'query_timestamp']

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print(f"Dropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'base+all_metrics_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+all_metrics CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")
print(f"\nbinary_preference distribution:")
print(df['binary_preference'].value_counts())

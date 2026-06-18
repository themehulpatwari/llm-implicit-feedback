import pandas as pd
from pathlib import Path

# Load base+user_specific.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+user_specific.csv'
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
columns_to_drop = ['comparison_type', 'task_id', 'likert_1', 'likert_2', 
                   'preference', 'query_timestamp']

# Add user_id
if 'user_id' in df.columns:
    columns_to_drop.append('user_id')

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print(f"Dropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")

# Verify binary_preference exists
if 'binary_preference' not in df.columns:
    print("\nWARNING: binary_preference column not found!")
else:
    print(f"\nbinary_preference distribution:")
    print(df['binary_preference'].value_counts())

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'base+user_specific_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+user_specific CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

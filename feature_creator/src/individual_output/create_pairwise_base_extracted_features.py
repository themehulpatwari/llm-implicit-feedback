import pandas as pd
from pathlib import Path

# Load base+extracted_features.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+extracted_features.csv'
df = pd.read_csv(input_path)

# Standardize column name
if 'query_ID' in df.columns:
    df = df.rename(columns={'query_ID': 'query_id'})

print(f"Initial shape: {df.shape}")

# Filter for pairwise data only
df = df[df['comparison_type'] == 'pairwise'].copy()
print(f"After filtering for pairwise: {df.shape}")

# Drop specified columns (keeping query_id)
columns_to_drop = ['comparison_type', 'user_id', 'task_id', 
                   'query_timestamp', 'likert_1', 'likert_2', 'preference',
                   'normalized_likert_1', 'normalized_likert_2']

# Drop all comparison_* features (they use preference/likert - data leakage)
comparison_cols = [col for col in df.columns if 'comparison_' in col]
columns_to_drop.extend(comparison_cols)

print(f"\nDropping comparison_* columns ({len(comparison_cols)}): {comparison_cols}")

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print(f"\nTotal dropped columns: {len(columns_to_drop)}")
print(f"Shape after dropping specified columns: {df.shape}")

# Drop columns that are completely empty (all-NA)
na_cols = [col for col in df.columns if df[col].isna().all()]
if na_cols:
    print(f"\nDropping {len(na_cols)} all-NA columns")
    df = df.drop(columns=na_cols)

print(f"Final shape: {df.shape}")

# Verify binary_preference exists
if 'binary_preference' not in df.columns:
    print("\nWARNING: binary_preference column not found!")
else:
    print(f"\nbinary_preference distribution:")
    print(df['binary_preference'].value_counts())

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'base+extracted_features_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+extracted_features CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

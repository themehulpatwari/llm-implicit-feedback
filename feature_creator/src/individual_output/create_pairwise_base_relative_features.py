import pandas as pd
from pathlib import Path

# Load base+relative_features.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+relative_features.csv'
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

# Drop specified metadata columns (keeping query_id)
columns_to_drop = ['comparison_type', 'user_id', 'task_id', 
                   'likert_1', 'likert_2', 'preference', 'query_timestamp']

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

# Drop columns that are entirely null (these are overall metrics not applicable to pairwise)
null_cols = df.columns[df.isnull().all()].tolist()
if null_cols:
    print(f"\nDropping {len(null_cols)} columns that are entirely null:")
    for col in null_cols:
        print(f"  - {col}")
    df = df.drop(columns=null_cols)

print(f"\nDropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")

# Verify binary_preference exists
if 'binary_preference' not in df.columns:
    print("\nWARNING: binary_preference column not found!")
else:
    print(f"\nbinary_preference distribution:")
    print(df['binary_preference'].value_counts())

# Verify comparison_* and cross_modality features are kept
comparison_cols = [col for col in df.columns if 'comparison_' in col]
cross_modality_cols = [col for col in df.columns if 'cross_modality' in col]
print(f"\nKept {len(comparison_cols)} comparison_* features")
print(f"Kept {len(cross_modality_cols)} cross_modality features")

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'base+relative_features_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+relative_features CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

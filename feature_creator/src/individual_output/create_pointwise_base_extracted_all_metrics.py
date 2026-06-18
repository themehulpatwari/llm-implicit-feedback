import pandas as pd
from pathlib import Path

# Load base+extracted+all_metrics.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+extracted+all_metrics.csv'
df = pd.read_csv(input_path)

# Standardize column name
if 'query_ID' in df.columns:
    df = df.rename(columns={'query_ID': 'query_id'})

print(f"Initial shape: {df.shape}")

# Drop specified features
# features_to_drop = (
#     [f'response_{r}_{m}_data_points' for r in ['A', 'B'] for m in ['gaze', 'mouse']]
#     + [f'response_{r}_response_length' for r in ['A', 'B']]
#     + [f'{m}_{s}_max_char_position_reached' for m in ['gaze', 'mouse'] for s in ['left', 'right']]
#     + [f'response_{r}_{m}_reading_completion_ratio' for r in ['A', 'B'] for m in ['gaze', 'mouse']]
# )
# cols_to_drop = [col for col in features_to_drop if col in df.columns]
# if cols_to_drop:
#     df = df.drop(columns=cols_to_drop)
#     print(f"Dropped {len(cols_to_drop)} specified features: {cols_to_drop}")

# Filter for pointwise data only
df = df[df['comparison_type'] == 'pointwise'].copy()
print(f"After filtering for pointwise: {df.shape}")

# Drop specified columns (keeping user_id and query_id)
columns_to_drop = ['comparison_type', 'task_id', 
                   'query_timestamp', 'llm_response_2', 'likert_2',
                   'normalized_likert_1', 'normalized_likert_2', 'binary_preference']

# Drop all response_B_* columns
response_B_cols = [col for col in df.columns if 'response_B' in col]
columns_to_drop.extend(response_B_cols)
print(f"\nDropping response_B_* columns ({len(response_B_cols)})")

# Drop all comparison_* features (they compare left vs right, but we only have left)
comparison_cols = [col for col in df.columns if 'comparison_' in col]
columns_to_drop.extend(comparison_cols)
print(f"Dropping comparison_* columns ({len(comparison_cols)}): {comparison_cols}")

# Drop all *_right features (keep *_left features)
right_cols = [col for col in df.columns if '_right' in col]
columns_to_drop.extend(right_cols)
print(f"Dropping *_right columns ({len(right_cols)}): {right_cols}")

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

# Verify likert_1 exists
if 'likert_1' not in df.columns:
    print("\nWARNING: likert_1 column not found!")
else:
    print(f"\nlikert_1 distribution:")
    print(df['likert_1'].value_counts())

# Save to pointwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pointwise_output' / 'base+extracted+all_metrics_pointwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPointwise base+extracted+all_metrics CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path to import important_features
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from important_features_paper import PAIRWISE_MOUSE_IMPORTANT

# Load base+all_metrics.csv and base+extracted_features.csv to merge
base_path = Path(__file__).resolve().parent.parent.parent / 'output'
all_metrics_df = pd.read_csv(base_path / 'base+all_metrics.csv')
extracted_df = pd.read_csv(base_path / 'base+extracted_features.csv')

print(f"base+all_metrics shape: {all_metrics_df.shape}")
print(f"base+extracted_features shape: {extracted_df.shape}")

# Standardize column names for merge
if 'query_ID' in all_metrics_df.columns:
    all_metrics_df = all_metrics_df.rename(columns={'query_ID': 'query_id'})
if 'query_ID' in extracted_df.columns:
    extracted_df = extracted_df.rename(columns={'query_ID': 'query_id'})

# Get columns to drop from extracted (keep only new extracted features)
drop_cols = ['user_query', 'llm_response_1', 'llm_response_2', 'comparison_type',
             'preference', 'likert_1', 'likert_2', 'query_timestamp', 'adjustment', 'domain']
# Also drop LLM columns from extracted (we'll keep them from all_metrics)
llm_cols = [c for c in extracted_df.columns if c.startswith('llm_1_') or c.startswith('llm_2_')]
drop_cols.extend(llm_cols)
drop_cols = [c for c in drop_cols if c in extracted_df.columns]

# Merge
df = all_metrics_df.merge(extracted_df.drop(columns=drop_cols),
                          on=['query_id', 'user_id', 'task_id'], how='inner')

print(f"After merging: {df.shape}")
print(f"LLM columns in merged df: {len([c for c in df.columns if c.startswith('llm_')])}")

# Filter for pairwise data only
df = df[df['comparison_type'] == 'pairwise'].copy()
print(f"After filtering for pairwise: {df.shape}")

# Create binary_preference: 1 -> 0, 2 -> 1
df['binary_preference'] = df['preference'].map({1: 0, 2: 1})
print(f"Created binary_preference column")

# Text columns to keep
text_columns = ['user_query', 'llm_response_1', 'llm_response_2']

# Target column
target_column = 'binary_preference'

# Select only mouse important features + text columns + query_id + target + domain
columns_to_keep = text_columns + ['query_id', 'domain'] + PAIRWISE_MOUSE_IMPORTANT + [target_column]

# Only keep columns that exist in the dataframe
columns_to_keep = [col for col in columns_to_keep if col in df.columns]
missing_features = [col for col in PAIRWISE_MOUSE_IMPORTANT if col not in df.columns]

if missing_features:
    print(f"\nWARNING: {len(missing_features)} mouse important features not found in data:")
    for feat in missing_features[:10]:
        print(f"  - {feat}")
    if len(missing_features) > 10:
        print(f"  ... and {len(missing_features) - 10} more")

df = df[columns_to_keep]

print(f"\nKept columns: {len(columns_to_keep)}")
print(f"  Text columns: {len(text_columns)}")
print(f"  Mouse important features: {len([c for c in columns_to_keep if c in PAIRWISE_MOUSE_IMPORTANT])}")
print(f"  Target: 1")
print(f"Final shape: {df.shape}")

# Verify binary_preference exists
if 'binary_preference' in df.columns:
    print(f"\nbinary_preference distribution:")
    print(df['binary_preference'].value_counts())
else:
    print("\nWARNING: binary_preference column not found!")

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'mouse_important_features_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise mouse important features CSV created")
print(f"Saved to: {output_path}")

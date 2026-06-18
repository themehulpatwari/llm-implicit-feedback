import argparse
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from important_features_paper import PAIRWISE_IMPORTANT_FEATURES
#from important_features_paper import PAIRWISE_GAZE_IMPORTANT as PAIRWISE_IMPORTANT_FEATURES
#from important_features_paper import PAIRWISE_MOUSE_IMPORTANT as PAIRWISE_IMPORTANT_FEATURES

parser = argparse.ArgumentParser()
parser.add_argument('--with-llm', action='store_true',
                    help='Join llm_1*, llm_2* columns from output/base+user_specific.csv')
parser.add_argument('--with-user', action='store_true',
                    help='Join user* columns from output/base+user_specific.csv')
parser.add_argument('--output', default='new_important_features_pairwise.csv',
                    help='Output file name inside pairwise_output/ (default: new_important_features_pairwise.csv)')
args = parser.parse_args()

# Load base+extracted+all_metrics.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+extracted+all_metrics.csv'
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

# Text columns to keep
text_columns = ['user_query', 'llm_response_1', 'llm_response_2']

# Target column
target_column = 'binary_preference'

# Select only important features + text columns + query_id + target + domain
columns_to_keep = text_columns + ['query_id', 'domain'] + PAIRWISE_IMPORTANT_FEATURES + [target_column]

# Only keep columns that exist in the dataframe
columns_to_keep = [col for col in columns_to_keep if col in df.columns]
missing_features = [col for col in PAIRWISE_IMPORTANT_FEATURES if col not in df.columns]

if missing_features:
    print(f"\nWARNING: {len(missing_features)} important features not found in data:")
    for feat in missing_features[:10]:
        print(f"  - {feat}")
    if len(missing_features) > 10:
        print(f"  ... and {len(missing_features) - 10} more")

df = df[columns_to_keep]

# Optionally join llm_1*/llm_2* and/or user* columns from base+user_specific.csv
if args.with_llm or args.with_user:
    us_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+user_specific.csv'
    us_df = pd.read_csv(us_path)
    if 'query_ID' in us_df.columns:
        us_df = us_df.rename(columns={'query_ID': 'query_id'})
    us_df = us_df[us_df['comparison_type'] == 'pairwise'].copy()
    us_cols = [c for c in us_df.columns
               if (args.with_llm and (c.startswith('llm_1') or c.startswith('llm_2')))
               or (args.with_user and c.startswith('user_A'))]
    us_df = us_df[['query_id'] + us_cols]
    before = df.shape[1]
    df = df.merge(us_df, on='query_id', how='left')
    print(f"\nJoined {df.shape[1] - before} columns from base+user_specific.csv")

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / args.output
#output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'new_gaze_important_features_pairwise.csv'
#output_path = Path(__file__).resolve().parent.parent.parent / 'pairwise_output' / 'new_mouse_important_features_pairwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+extracted+all_metrics CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

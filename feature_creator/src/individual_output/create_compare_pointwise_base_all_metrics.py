import pandas as pd
from pathlib import Path

# Load base+all_metrics.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+extracted+all_metrics.csv'
df = pd.read_csv(input_path)

# Standardize column name
if 'query_ID' in df.columns:
    df = df.rename(columns={'query_ID': 'query_id'})

print(f"Initial shape: {df.shape}")

# Filter for pointwise data only
df = df[df['comparison_type'] == 'pointwise'].copy()
print(f"After filtering for comparison pointwise: {df.shape}")

# Create binary_preference
#df['binary_preference'] = df['preference'].map({0: 1, 1: 2})
df['binary_preference'] = df['preference']
print(f"Created binary_preference column")
# print(f"Unique values of binary_preference: {df['binary_preference'].unique()}")

# Sort by user_id, domain, query_id (important for correct ordering)
df = df.sort_values(by=["user_id", "domain", "query_id"])

# Group by user_id and domain (so shifts only happen within same user/domain)
grouped = df.groupby(["user_id", "domain"])

# Shift all columns down by 1 row within each group, add "prev_" prefix
prev_df = grouped.shift(1).add_prefix("prev_")

# Concatenate original columns + previous columns
df = pd.concat([df, prev_df], axis=1)

# Drop rows without a previous query (first query for each user/domain will have NaN)
df = df.dropna(subset=["prev_query_id", "binary_preference"])
# print(f"Unique value sof binary_preference after shifting: {df['binary_preference'].unique()}")

# Stratified sampling to balance binary_preference (equal 0s and 1s)
min_count = df['binary_preference'].value_counts().min()
df = (df.groupby('binary_preference', group_keys=False)
        .apply(lambda x: x.sample(n=min_count, random_state=42)))
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"After stratified sampling (n={min_count} per class): {df.shape}")
print(df['binary_preference'].value_counts())

# Drop specified columns (keeping query_id)
columns_to_drop = ['comparison_type', 'user_id', 'task_id', 
                   'likert_1', 'likert_2', 'preference', 'query_timestamp']

df = df.drop(columns=columns_to_drop)


# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        

print(f"Dropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")

# Save to pairwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pointwise_output' / 'base+all_metrics_compare_pointwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPairwise base+all_metrics CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")
print(f"\nbinary_preference distribution:")
print(df['binary_preference'].value_counts())

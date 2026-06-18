import pandas as pd
from pathlib import Path

# Load base.csv
input_path = Path(__file__).resolve().parent.parent.parent / 'input' / 'base.csv'
if not input_path.exists():
    input_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'

df = pd.read_csv(input_path)

# Standardize column name
if 'query_ID' in df.columns:
    df = df.rename(columns={'query_ID': 'query_id'})

print(f"Initial shape: {df.shape}")

# Filter for pointwise data only
df = df[df['comparison_type'] == 'pointwise'].copy()
print(f"After filtering for pointwise: {df.shape}")

df['binary_preference'] = df['preference']

# Drop specified columns
columns_to_drop = ['comparison_type', 'task_id', 'likert_2', 
                   'query_timestamp', 'llm_response_2']

columns_to_drop.extend(['preference', 'likert_1', 'adjustment'])  # Also drop target and some metadata


# Keep user_id and query_id in the output

# Drop all llm_2_* columns
llm_2_cols = [col for col in df.columns if col.startswith('llm_2_')]
columns_to_drop.extend(llm_2_cols)

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print(f"\nCreating previous columns...")
df = df.sort_values(by=["user_id", "domain", "query_id"])
grouped = df.groupby(["user_id", "domain"])
prev_df = grouped.shift(1).add_prefix("prev_")
df = pd.concat([df, prev_df], axis=1)
df = df.dropna(subset=["prev_query_id", "binary_preference"])
print(f"After creating previous columns: {df.shape}")



rename_map = {'prev_llm_response_1': 'llm_response_2'}
for col in df.columns:
    if col.startswith('prev_llm_1_'):
        rename_map[col] = col.replace('prev_llm_1_', 'llm_2_')
    #print(col)

df = df.drop(columns=['prev_binary_preference', 'prev_query_id'])
df = df.rename(columns=rename_map)



# Filter to only query_ids present in base+all_metrics_compare_pointwise.csv
ref_path = Path(__file__).resolve().parent.parent.parent / 'pointwise_output' / 'base+all_metrics_compare_pointwise.csv'
if ref_path.exists():
    ref_query_ids = pd.read_csv(ref_path, usecols=['query_id'])['query_id']
    df = df[df['query_id'].isin(ref_query_ids)]
    print(f"After filtering by ref query_ids: {df.shape}")

print(f"Dropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")


# Save to pointwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pointwise_output' / 'base_compare_pointwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

# print(f"\nPointwise base CSV created with shape: {df.shape}")
# print(f"Saved to: {output_path}")
# print(f"\nlikert_1 distribution:")
# print(df['likert_1'].value_counts())

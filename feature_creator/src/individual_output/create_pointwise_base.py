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

# Drop specified columns
columns_to_drop = ['comparison_type', 'task_id', 'likert_2', 
                   'query_timestamp', 'llm_response_2']

# Keep user_id and query_id in the output

# Drop all llm_2_* columns
llm_2_cols = [col for col in df.columns if col.startswith('llm_2_')]
columns_to_drop.extend(llm_2_cols)

# Only drop columns that actually exist
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

print(f"Dropped columns: {columns_to_drop}")
print(f"Final shape: {df.shape}")

# Save to pointwise_output folder
output_path = Path(__file__).resolve().parent.parent.parent / 'pointwise_output' / 'base_pointwise.csv'
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\nPointwise base CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")
print(f"\nlikert_1 distribution:")
print(df['likert_1'].value_counts())

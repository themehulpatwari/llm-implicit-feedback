import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'
base_df = pd.read_csv(base_path)

print(f"Base CSV shape: {base_df.shape}")

all_metrics_path = Path(__file__).resolve().parent.parent.parent / 'input' / 'all_metrics.csv'
all_metrics_df = pd.read_csv(all_metrics_path)

print(f"All Metrics CSV shape: {all_metrics_df.shape}")
base_cols = set(base_df.columns.str.lower())
all_metrics_cols = set(all_metrics_df.columns)

# Find unique columns in all_metrics (excluding merge keys)
unique_metrics_cols = []
for col in all_metrics_df.columns:
    if col.lower() not in base_cols and col not in ['query_id', 'user_id', 'task_id']:
        unique_metrics_cols.append(col)

print(f"\nColumns to add from all_metrics: {len(unique_metrics_cols)}")
print(f"Columns: {unique_metrics_cols}")

merge_cols = ['query_id', 'user_id', 'task_id'] + unique_metrics_cols
all_metrics_subset = all_metrics_df[merge_cols]

base_df_renamed = base_df.rename(columns={'query_ID': 'query_id'})

merged_df = base_df_renamed.merge(
    all_metrics_subset,
    on=['query_id', 'user_id', 'task_id'],
    how='inner'
)

print(f"\nMerged CSV shape: {merged_df.shape}")
print(f"Rows in base: {len(base_df)}")
print(f"Rows in all_metrics: {len(all_metrics_df)}")
print(f"Rows in merged: {len(merged_df)}")

output_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+all_metrics.csv'
merged_df.to_csv(output_path, index=False)

print(f"\nBase+All Metrics CSV created")
print(f"Saved to: {output_path}")

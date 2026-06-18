"""
Add domain column from task_table to query_logs_table.

Joins task_table.domain -> query_logs_table via task_id (left join).
Rows with no matching task_id get an empty/NaN domain.

Overwrites input/query_logs_table.csv in place with the domain column added.
"""

import pandas as pd
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
task_path   = project_root / 'input' / 'task_table.csv'
query_path  = project_root / 'input' / 'query_logs_table.csv'
output_path = project_root / 'input' / 'query_logs_table.csv'

# ─── Load ─────────────────────────────────────────────────────────────────────
print("Loading task_table …")
task_df = pd.read_csv(task_path, usecols=['task_id', 'domain'])
task_df['task_id'] = task_df['task_id'].astype(str).str.strip()
# Keep only one domain per task_id (first occurrence)
task_df = task_df.drop_duplicates(subset='task_id')
print(f"  task_table rows: {len(task_df)}  |  unique task_ids: {task_df['task_id'].nunique()}")
print(f"  non-null domains: {task_df['domain'].notna().sum()}")

print("\nLoading query_logs_table …")
query_df = pd.read_csv(query_path)
query_df['task_id'] = query_df['task_id'].astype(str).str.strip()
print(f"  query_logs shape (before join): {query_df.shape}")

if 'domain' in query_df.columns:
    print("  'domain' column already exists — dropping it before re-joining.")
    query_df = query_df.drop(columns=['domain'])

# ─── Join ─────────────────────────────────────────────────────────────────────
print("\nJoining domain onto query_logs …")
merged = query_df.merge(task_df[['task_id', 'domain']], on='task_id', how='left')
print(f"  merged shape:      {merged.shape}")
print(f"  rows with domain:  {merged['domain'].notna().sum()}")
print(f"  rows without domain (blank): {merged['domain'].isna().sum()}")

# ─── Save ─────────────────────────────────────────────────────────────────────
merged.to_csv(output_path, index=False)
print(f"\n✓ Saved enriched query_logs_table to: {output_path}")
print(f"  Final columns: {list(merged.columns)}")

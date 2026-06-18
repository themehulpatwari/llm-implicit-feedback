import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'
base_df = pd.read_csv(base_path)

print(f"Base CSV shape: {base_df.shape}")

extracted_path = Path(__file__).resolve().parent.parent.parent / 'input' / 'extracted_features.csv'
extracted_df = pd.read_csv(extracted_path)

print(f"Extracted features CSV shape: {extracted_df.shape}")
base_cols = set(base_df.columns.str.lower())
extracted_cols = set(extracted_df.columns)

# Find unique columns in extracted_features (excluding llm_name_1 and llm_name_2)
unique_extracted_cols = []
for col in extracted_df.columns:
    if col.lower() not in base_cols and col not in ['llm_name_1', 'llm_name_2']:
        unique_extracted_cols.append(col)

print(f"\nColumns to add from extracted_features: {len(unique_extracted_cols)}")

merge_cols = ['query_id', 'user_id'] + unique_extracted_cols
extracted_df_subset = extracted_df[merge_cols]

base_df_renamed = base_df.rename(columns={'query_ID': 'query_id'})

merged_df = base_df_renamed.merge(
    extracted_df_subset,
    on=['query_id', 'user_id'],
    how='inner'
)

print(f"\nMerged CSV shape: {merged_df.shape}")
print(f"Rows in base: {len(base_df)}")
print(f"Rows in merged: {len(merged_df)}")

output_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+extracted_features.csv'
merged_df.to_csv(output_path, index=False)

print(f"\nBase+Extracted Features CSV created")
print(f"Saved to: {output_path}")

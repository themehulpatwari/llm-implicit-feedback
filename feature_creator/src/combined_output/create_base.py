import pandas as pd
from pathlib import Path

bad_workers = [
    'worker_9683ed92', 'worker_83c92f1d', 'worker_030da562', 'worker_8371812d',
    'worker_a0dc15c2', 'worker_7bef026e', 'worker_87c89391', 'worker_fa234af6',
    'worker_b7c39547', 'worker_efe70ff2', 'worker_d20db140', 'worker_dd6abc1c',
    'worker_891c885b', 'worker_c07eb25b', 'worker_f972316e', 'worker_dc32691e',
    'worker_5f6ca345', 'worker_29e7a1a6', 'worker_6680f3d4', 'worker_0ddfe023',
    'worker_327b4905', 'worker_23415b2d', 'worker_6ce6a3f8', 'worker_cdd07ac1',
]

input_path = Path(__file__).resolve().parent.parent.parent / 'input' / 'query_logs_table.csv'
df = pd.read_csv(input_path)

print(f"Initial shape: {df.shape}")

df = df[~df['user_id'].isin(bad_workers)]
print(f"After filtering bad workers: {df.shape}")

df['llm_name_1'] = df['llm_name_1'].apply(lambda x: x.replace('\r\n', '').replace('\n', '').replace('\r', '').strip() if pd.notna(x) else x)
df['llm_name_2'] = df['llm_name_2'].apply(lambda x: x.replace('\r\n', '').replace('\n', '').replace('\r', '').strip() if pd.notna(x) else x)
print("Cleaned llm_name columns")

df['comparison_type'] = df.apply(
    lambda row: 'pointwise' if pd.isna(row['llm_response_2']) and pd.isna(row['llm_name_2']) else 'pairwise',
    axis=1
)

all_llm = pd.concat([
    df['llm_name_1'].dropna(),
    df['llm_name_2'].dropna()
]).unique()

print(f"\nUnique LLMs found: {sorted(all_llm)}")

for llm in all_llm:
    df[f'llm_1_{llm}'] = (df['llm_name_1'] == llm).astype(int)

for llm in all_llm:
    df[f'llm_2_{llm}'] = (df['llm_name_2'] == llm).astype(int)

df = df.drop(columns=['llm_name_1', 'llm_name_2'])
print("\nDropped original llm_name_1 and llm_name_2 columns")
cols = df.columns.tolist()
cols.remove('comparison_type')
df = df[['comparison_type'] + cols]

output_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'
df.to_csv(output_path, index=False)

print(f"\nBase CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")
print(f"\nComparison type distribution:")
print(df['comparison_type'].value_counts())

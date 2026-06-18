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

input_dir = Path(__file__).resolve().parent.parent / 'input'

# List of CSV files to process
csv_files = [
    'extracted_features.csv',
    'all_metrics.csv',
    'query_logs_table.csv',
    'task_table.csv'
]

for csv_file in csv_files:
    csv_path = input_dir / csv_file
    print(csv_path)
    
    if not csv_path.exists():
        print(f"\n⚠️  Skipping {csv_file} - file not found")
        continue
    
    print(f"\n{'='*60}")
    print(f"Processing: {csv_file}")
    print(f"{'='*60}")
    
    df = pd.read_csv(csv_path)
    
    print(f"Initial shape: {df.shape}")
    print(f"Initial rows: {len(df)}")
    
    df_filtered = df[~df['user_id'].isin(bad_workers)]
    
    print(f"Filtered shape: {df_filtered.shape}")
    print(f"Filtered rows: {len(df_filtered)}")
    print(f"Rows removed: {len(df) - len(df_filtered)}")
    
    df_filtered.to_csv(csv_path, index=False)
    print(f"✓ Filtered data saved to {csv_path}")

print(f"\n{'='*60}")
print(f"All files processed successfully!")
print(f"{'='*60}")


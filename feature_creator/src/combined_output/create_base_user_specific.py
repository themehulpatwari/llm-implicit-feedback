import pandas as pd
from pathlib import Path

MODE = 'top_n'
TOP_N = 5

base_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'
df = pd.read_csv(base_path)

print(f"Base CSV shape: {df.shape}")
print(f"Mode: {MODE}")

user_counts = df['user_id'].value_counts()
print(f"\nTotal unique users: {len(user_counts)}")

if MODE == 'top_n':
    top_users = user_counts.head(TOP_N).index.tolist()
    print(f"\nTop {TOP_N} users by frequency:")
    for user, count in user_counts.head(TOP_N).items():
        print(f"  {user}: {count} rows")
    
    for user in top_users:
        df[f'user_{user}'] = (df['user_id'] == user).astype(int)
    
    print(f"\nCreated {TOP_N} one-hot encoded user columns")

elif MODE == 'all':
    all_users = user_counts.index.tolist()
    
    for user in all_users:
        df[f'user_{user}'] = (df['user_id'] == user).astype(int)
    
    print(f"\nCreated {len(all_users)} one-hot encoded user columns")

else:
    raise ValueError(f"Invalid MODE: {MODE}. Must be 'top_n' or 'all'")

df = df.drop(columns=['user_id'])
print(f"\nDropped original user_id column")
output_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+user_specific.csv'
df.to_csv(output_path, index=False)

print(f"\nBase+User Specific CSV created with shape: {df.shape}")
print(f"Saved to: {output_path}")

import pandas as pd
from sklearn.model_selection import train_test_split

input_path = "data/base_pairwise.csv"
#input_path = "data/base_pointwise.csv"

# Load the CSV file
df = pd.read_csv(input_path)

# Split into train and test sets (80% train, 20% test)
train_df, test_df = train_test_split(
    df,
    test_size=0.2,       # 20% for testing
    random_state=42,     # For reproducibility
    shuffle=True         # Shuffle before splitting
)

# Save to new CSV files
train_df.to_csv(input_path.replace('.csv',"_train.csv"), index=False)
test_df.to_csv(input_path.replace('.csv',"_test.csv"), index=False)

print(f"Total rows:    {len(df)}")
print(f"Training rows: {len(train_df)} ({len(train_df)/len(df):.0%})")
print(f"Testing rows:  {len(test_df)} ({len(test_df)/len(df):.0%})")

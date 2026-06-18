import pandas as pd
from sklearn.model_selection import train_test_split

input_name = "mouse_important_features_pairwise_labeled.csv"
#input_name = "gaze_important_features_pairwise_labeled.csv"
#input_name = "important_features_pairwise_labeled.csv"
input_folder = "data/paper_results"
output_folder = "data/rf_pred"

#input_name = "important_features_pairwise_labeled.csv"
#input_folder = "data/rf_pred"
#output_folder = "data/rf_pred"

train_file = 'data/base_pairwise_train.csv'
test_file = 'data/base_pairwise_test.csv'
key_column = 'llm_response_1'
key2_column = 'llm_response_2'

# Load the CSV file
input_path = input_folder + '/' + input_name
df = pd.read_csv(input_path)

#df.rename(columns={'text_x': 'user_query', 'text_pair_x': 'llm_response_1', 'text_pair_y': 'llm_response_2', 'prediction': 'binary_preference'}, inplace=True)
df.rename(columns={'binary_preference': 'gt_binary_preference', 'oof_prediction': 'binary_preference', 'oof_confidence': 'confidence'}, inplace=True)

df['user_query'] = df['user_query'].str.replace('user_query: ', '')
#df['llm_response_1'] = df['llm_response_1'].str.replace('llm_response_1: ', '')
#df['llm_response_2'] = df['llm_response_2'].str.replace('llm_response_2: ', '')

# Split into train and test sets (80% train, 20% test)
#train_df, test_df = train_test_split(
#    df,
#    test_size=0.2,       # 20% for testing
#    random_state=42,     # For reproducibility
#    shuffle=True         # Shuffle before splitting
#)

df_prev_train = pd.read_csv(train_file)
df_prev_test = pd.read_csv(test_file)

train_df = df[df[key_column].isin(df_prev_train[key_column]) & df[key2_column].isin(df_prev_train[key2_column])]
test_df = df[df[key_column].isin(df_prev_test[key_column]) & df[key2_column].isin(df_prev_test[key2_column])]

# Save to new CSV files
output_path = output_folder + '/' + input_name
train_df.to_csv(output_path.replace('.csv',"_train.csv"), index=False)
test_df.to_csv(output_path.replace('.csv',"_test.csv"), index=False)

print(f"Total rows:    {len(df)}")
print(f"Training rows: {len(train_df)} ({len(train_df)/len(df):.0%})")
print(f"Testing rows:  {len(test_df)} ({len(test_df)/len(df):.0%})")

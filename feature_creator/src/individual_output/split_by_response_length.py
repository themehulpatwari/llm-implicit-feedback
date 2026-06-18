import pandas as pd
import numpy as np

df = pd.read_csv("pairwise_output/new_important_features_pairwise.csv")

df["total_response_length"] = df["response_length_left"] + df["response_length_right"]
df_sorted = df.sort_values("total_response_length").reset_index(drop=True)

n = len(df_sorted)
third = n // 3
short = df_sorted.iloc[:third]
medium = df_sorted.iloc[third : 2 * third]
long_ = df_sorted.iloc[2 * third :]

short.to_csv("pairwise_output/new_important_features_pairwise_short.csv", index=False)
medium.to_csv("pairwise_output/new_important_features_pairwise_medium.csv", index=False)
long_.to_csv("pairwise_output/new_important_features_pairwise_long.csv", index=False)

print(f"Total rows: {n}")
print(f"Short  ({len(short)} rows): total_response_length {short['total_response_length'].min():.0f} – {short['total_response_length'].max():.0f}")
print(f"Medium ({len(medium)} rows): total_response_length {medium['total_response_length'].min():.0f} – {medium['total_response_length'].max():.0f}")
print(f"Long   ({len(long_)} rows): total_response_length {long_['total_response_length'].min():.0f} – {long_['total_response_length'].max():.0f}")

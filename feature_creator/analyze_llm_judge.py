#!/usr/bin/env python3
"""
Merge base.csv and base+llm_judge_final.csv and analyze whether
the LLM judge prediction prefers gpt-4o-mini responses.
"""

import pandas as pd

base = pd.read_csv("output/base.csv")
judge = pd.read_csv("output/base+llm_judge_final.csv")

# Align join key names
base = base.rename(columns={"query_ID": "query_id"})
merged = judge.merge(
    base[["query_id", "llm_1_gpt-4o-mini", "llm_2_gpt-4o-mini"]],
    on="query_id",
    how="inner",
)

print(f"Rows after merge: {len(merged)}")

# Determine which response slot gpt-4o-mini occupies (1 or 2), or neither (NaN)
def gpt4o_slot(row):
    if row["llm_1_gpt-4o-mini"] == 1:
        return 1
    elif row["llm_2_gpt-4o-mini"] == 1:
        return 2
    return None

merged["gpt4o_slot"] = merged.apply(gpt4o_slot, axis=1)
has_gpt4o = merged[merged["gpt4o_slot"].notna()].copy()
print(f"Rows where gpt-4o-mini is one of the models: {len(has_gpt4o)}\n")

# --- LLM judge preference for gpt-4o-mini ---
has_gpt4o["judge_prefers_gpt4o"] = (
    has_gpt4o["llm_judge_prediction"] == has_gpt4o["gpt4o_slot"]
)
judge_counts = has_gpt4o["judge_prefers_gpt4o"].value_counts()
judge_rate = has_gpt4o["judge_prefers_gpt4o"].mean()

print("=== LLM Judge preference for gpt-4o-mini ===")
print(f"  Prefers gpt-4o-mini   : {judge_counts.get(True, 0)}")
print(f"  Prefers other model   : {judge_counts.get(False, 0)}")
print(f"  Preference rate       : {judge_rate:.1%}\n")

# --- Human preference for gpt-4o-mini (preference 0 = tie) ---
human_valid = has_gpt4o[has_gpt4o["preference"].isin([1, 2])].copy()
human_valid["human_prefers_gpt4o"] = (
    human_valid["preference"] == human_valid["gpt4o_slot"]
)
human_counts = human_valid["human_prefers_gpt4o"].value_counts()
human_rate = human_valid["human_prefers_gpt4o"].mean()

print("=== Human preference for gpt-4o-mini (ties excluded) ===")
print(f"  Prefers gpt-4o-mini   : {human_counts.get(True, 0)}")
print(f"  Prefers other model   : {human_counts.get(False, 0)}")
print(f"  Preference rate       : {human_rate:.1%}\n")

# --- Agreement between judge and human ---
both = has_gpt4o[has_gpt4o["preference"].isin([1, 2])].copy()
both["agree"] = both["llm_judge_prediction"] == both["preference"]
agree_rate = both["agree"].mean()
print("=== Judge vs Human agreement (ties excluded) ===")
print(f"  Agreement rate        : {agree_rate:.1%}")
print(f"  Agree                 : {both['agree'].sum()}")
print(f"  Disagree              : {(~both['agree']).sum()}\n")

# --- Breakdown by which slot gpt-4o-mini is in ---
print("=== Judge preference rate by gpt-4o-mini slot ===")
for slot, group in has_gpt4o.groupby("gpt4o_slot"):
    rate = (group["llm_judge_prediction"] == group["gpt4o_slot"]).mean()
    print(f"  gpt-4o-mini in slot {int(slot)}: {rate:.1%}  (n={len(group)})")

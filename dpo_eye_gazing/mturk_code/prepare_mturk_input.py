import json
import csv
import random
import sys
import os
import argparse


def prepare_mturk_input(input_path: str, seed: int = 42) -> str:
    random.seed(seed)

    with open(input_path) as f:
        data = json.load(f)

    results = data["results"]

    input_basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"mturk_files/mturk_input_{input_basename}.csv"

    fieldnames = ["index", "user_query", "llm_response_a", "llm_response_b", "llm_a", "llm_b"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            sft_is_a = random.random() < 0.5

            if sft_is_a:
                llm_response_a = item["sft_response"]
                llm_response_b = item["dpo_response"]
                llm_a = "sft"
                llm_b = "dpo"
            else:
                llm_response_a = item["dpo_response"]
                llm_response_b = item["sft_response"]
                llm_a = "dpo"
                llm_b = "sft"
            #print(item)
            writer.writerow({
                "index": item["index"],
                "user_query": item["prompt"].replace("\n\nHuman: ",''),
                "llm_response_a": llm_response_a,
                "llm_response_b": llm_response_b,
                "llm_a": llm_a,
                "llm_b": llm_b,
            })

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare MTurk input CSV from an eval_results JSON file."
    )
    parser.add_argument("input_file", help="Path to the eval_results JSON file")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    output = prepare_mturk_input(args.input_file, seed=args.seed)
    print(f"Wrote {output}")

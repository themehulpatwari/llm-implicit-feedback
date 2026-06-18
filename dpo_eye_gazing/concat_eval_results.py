import json
import os
import re

FIRST_DIR = "eval_results/first_50"
SECOND_DIR = "eval_results/second_50_300"
OUT_DIR = "eval_results"

def recompute_metrics(results):
    scores_sft = [r["judgment"]["score_sft"] for r in results if "judgment" in r]
    scores_dpo = [r["judgment"]["score_dpo"] for r in results if "judgment" in r]
    winners = [r["judgment"]["winner_model"] for r in results if "judgment" in r]

    n = len(results)
    sft_wins = sum(1 for w in winners if w == "SFT")
    dpo_wins = sum(1 for w in winners if w == "DPO")
    ties = sum(1 for w in winners if w not in ("SFT", "DPO"))

    return {
        "n_evaluated": n,
        "n_skipped": 0,
        "sft_avg_score": round(sum(scores_sft) / n, 4) if n else 0,
        "dpo_avg_score": round(sum(scores_dpo) / n, 4) if n else 0,
        "sft_win_rate": round(sft_wins / n, 4) if n else 0,
        "dpo_win_rate": round(dpo_wins / n, 4) if n else 0,
        "tie_rate": round(ties / n, 4) if n else 0,
        "sft_wins": sft_wins,
        "dpo_wins": dpo_wins,
        "ties": ties,
    }

def merge_configs(cfg1, cfg2, out_path):
    merged = dict(cfg1)
    # Use the broader range: start at 0, end at cfg1.max_samples + cfg2.max_samples
    n1 = cfg1.get("max_samples", 0)
    n2 = cfg2.get("max_samples", 0)
    merged.pop("start_samples", None)
    merged["max_samples"] = n1 + n2
    merged["output_path"] = out_path
    return merged

def main():
    first_files = sorted(os.listdir(FIRST_DIR))
    paired = 0
    skipped = []

    for fname in first_files:
        if not fname.endswith(".json"):
            continue

        stem = fname[len("eval_results_"):-len(".json")]  # e.g. "eye_rev_gpt_xl_bz2_alpha1"
        second_fname = f"eval_results_{stem}_50_300.json"
        second_path = os.path.join(SECOND_DIR, second_fname)

        if not os.path.exists(second_path):
            skipped.append(fname)
            continue

        first_path = os.path.join(FIRST_DIR, fname)
        out_fname = f"eval_results_{stem}_0_300.json"
        out_path = os.path.join(OUT_DIR, out_fname)

        with open(first_path) as f:
            data1 = json.load(f)
        with open(second_path) as f:
            data2 = json.load(f)

        results1 = data1["results"]
        results2 = data2["results"]

        # Re-index second batch to continue from end of first
        offset = len(results1)
        reindexed = [{**r, "index": offset + i} for i, r in enumerate(results2)]

        combined_results = results1 + reindexed
        merged_config = merge_configs(data1["config"], data2["config"], out_fname)
        merged_metrics = recompute_metrics(combined_results)

        out_data = {
            "config": merged_config,
            "metrics": merged_metrics,
            "results": combined_results,
        }

        with open(out_path, "w") as f:
            json.dump(out_data, f, indent=2)

        print(f"  {fname} + {second_fname} -> {out_fname}  ({len(combined_results)} results)")
        paired += 1

    print(f"\nDone: {paired} files merged.")
    if skipped:
        print(f"Skipped (no matching second file): {skipped}")

if __name__ == "__main__":
    main()

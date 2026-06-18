import json
import math
from pathlib import Path
from collections import defaultdict

EVAL_DIR = Path("eval_results")
METRICS = ["sft_avg_score", "dpo_avg_score", "sft_win_rate", "dpo_win_rate"]

# Known LLM name suffixes — sorted longest-first to avoid partial matches
LLM_NAMES = sorted([
    "gpt2-xl", "gpt_xl", "llama3", "llama",
    "olmo2_1b", "pythia28",
    "qwen25_15b", "qwen25_3b", "qwen3_17b", "qwen3_4b",
], key=len, reverse=True)

def extract_method(stem):
    """Return method name by stripping eval_results_ prefix, _bz2_alpha1 suffix, and LLM suffix."""
    stem = stem.removeprefix("eval_results_").removesuffix("_bz2_alpha1_0_300")
    for llm in LLM_NAMES:
        if stem.endswith("_" + llm):
            return stem[: -(len(llm) + 1)]
    return stem  # fallback: no LLM suffix matched

# Collect per-method scores
method_scores = defaultdict(lambda: defaultdict(list))

for filepath in sorted(EVAL_DIR.glob("*_bz2_alpha1_0_300.json")):
    method = extract_method(filepath.stem)
    input_data = json.loads(filepath.read_text())
    metrics = input_data.get("metrics", {})
    for m in METRICS:
        if m in metrics:
            method_scores[method][m].append(metrics[m])
    if "dpo_avg_score" in metrics and "sft_avg_score" in metrics:
        method_scores[method]["score_diff"].append(metrics["dpo_avg_score"] - metrics["sft_avg_score"])
    all_score_diff = [input_data['results'][i]['judgment']["score_dpo"] - input_data['results'][i]['judgment']["score_sft"]  for i in range(len(input_data['results'])) ]
    method_scores[method]["all_score_diff"].extend(all_score_diff)
    for r in input_data["results"]:
        method_scores[method]["sft_len"].append(len(r["sft_response"].split()))
        method_scores[method]["dpo_len"].append(len(r["dpo_response"].split()))

def mean_se(values):
    n = len(values)
    if n == 0:
        return float("nan"), float("nan")
    avg = sum(values) / n
    se = math.sqrt(sum((x - avg) ** 2 for x in values) / n / max(n - 1, 1))
    return avg, se

# Print results — each metric shows "mean ± se"
col_w = 18
#ALL_COLS = METRICS + ["score_diff(dpo-sft)"]
#col_labels = METRICS + ["dpo-sft score", "all dpo-sft score", "avg sft len", "avg dpo len"]
col_labels = METRICS + ["all dpo-sft score", "avg sft len", "avg dpo len"]
header = f"{'Method':<40}" + "".join(f"{m:^{col_w}}" for m in col_labels) + f"{'n_llms':>8}"
print(header)
print("-" * len(header))

for method, scores in sorted(method_scores.items()):
    n = max( [len(v) for v in scores.values()][:-1] )
    cells = []
    for key in METRICS + ["all_score_diff"]: #["score_diff", "all_score_diff"]:
        avg, se = mean_se(scores[key])
        cells.append(f"{avg:.4f}±{se:.4f}") # len={len(scores[key])}
    for key in ["sft_len", "dpo_len"]:
        avg, se = mean_se(scores[key])
        cells.append(f"{avg:.1f}±{se:.1f}")
    print(f"{method:<40}" + "".join(f"{c:^{col_w}}" for c in cells) + f"{n:>8}")

# ─── Length-based splitting into short / medium / long DPO responses ──────────

LLM_MAP = {
    "pythia28": "Pythia 2.8b",
    "olmo2_1b": "OLMo 2 1b",
    "llama3": "Llama3.2 3b",
    "gpt2-xl": "GPT2-XL",
    "qwen25_15b": "Qwen2.5 1.5b",
    "qwen25_3b": "Qwen2.5 3b",
    "qwen3_17b": "Qwen3 1.7b",
    "qwen3_4b": "Qwen3 4b",
}

PREFIX_MAP = [
    ("rdpo_bert_all_new",   "ModernBERT + Text + IF"),
    ("rdpo_bert_base_new",  "ModernBERT + Text"),
    ("rdpo_rf_imp_new_gaze",  "RF + (IF - Mouse)"),
    ("rdpo_rf_imp_new_mouse", "RF + (IF - Gaze)"),
    ("rdpo_rf_imp_new",     "RF + IF"),
    ("eye_rev",             "Explicit Feedback"),
]

ROW_ORDER = [
    "Explicit Feedback",
    "ModernBERT + Text",
    "ModernBERT + Text + IF",
    "RF + (IF - Gaze)",
    "RF + (IF - Mouse)",
    "RF + IF",
]

LLM_ORDER = [
    "GPT2-XL",
    "Pythia 2.8b",
    "OLMo 2 1b",
    "Llama3.2 3b",
    "Qwen2.5 1.5b",
    "Qwen2.5 3b",
    "Qwen3 1.7b",
    "Qwen3 4b",
]

def extract_llm_label(stem):
    s = stem.removeprefix("eval_results_").removesuffix("_bz2_alpha1_0_300")
    for llm in sorted(LLM_MAP, key=len, reverse=True):
        if s.endswith("_" + llm):
            return LLM_MAP[llm]
    return None

def method_to_row_label(method):
    for prefix, label in PREFIX_MAP:
        if method == prefix:
            return label
    return None

def group_metrics(results):
    n = len(results)
    if n == 0:
        return None
    scores_sft = [r["judgment"]["score_sft"] for r in results]
    scores_dpo = [r["judgment"]["score_dpo"] for r in results]
    winners = [r["judgment"]["winner_model"] for r in results]
    sft_wins = sum(1 for w in winners if w == "SFT")
    dpo_wins = sum(1 for w in winners if w == "DPO")
    return {
        "sft_avg_score": sum(scores_sft) / n,
        "dpo_avg_score": sum(scores_dpo) / n,
        "sft_win_rate": sft_wins / n,
        "dpo_win_rate": dpo_wins / n,
        "n": n,
        "avg_dpo_len": sum(len(r["dpo_response"].split()) for r in results) / n,
    }

# Collect metrics per (group, row_label, llm_label)
length_tables = {"short": {}, "medium": {}, "long": {}}

for filepath in sorted(EVAL_DIR.glob("*_bz2_alpha1_0_300.json")):
    llm_label = extract_llm_label(filepath.stem)
    if llm_label is None:
        continue
    method = extract_method(filepath.stem)
    row_label = method_to_row_label(method)
    if row_label is None:
        continue

    results = json.loads(filepath.read_text())["results"]
    results_sorted = sorted(results, key=lambda r: len(r["dpo_response"].split()))
    n = len(results_sorted)
    third = n // 3

    splits = {
        "short":  results_sorted[:third],
        "medium": results_sorted[third: 2 * third],
        "long":   results_sorted[2 * third:],
    }
    for group, grp_results in splits.items():
        m = group_metrics(grp_results)
        if m is None:
            continue
        length_tables[group].setdefault(row_label, {})[llm_label] = m

def avg_across_llms(row_cells):
    """Average metric values across a list of per-LLM metric dicts."""
    vals = [c for c in row_cells if c is not None]
    if not vals:
        return None
    return {
        "sft_avg_score": sum(c["sft_avg_score"] for c in vals) / len(vals),
        "dpo_avg_score": sum(c["dpo_avg_score"] for c in vals) / len(vals),
        "sft_win_rate":  sum(c["sft_win_rate"]  for c in vals) / len(vals),
        "dpo_win_rate":  sum(c["dpo_win_rate"]  for c in vals) / len(vals),
        "avg_dpo_len":   sum(c["avg_dpo_len"]   for c in vals) / len(vals),
    }

def print_length_table(group_name, data):
    present_llms = [llm for llm in LLM_ORDER if any(llm in data.get(row, {}) for row in ROW_ORDER)]
    present_rows = [row for row in ROW_ORDER if row in data]

    all_llms = present_llms + ["Avg (all LLMs)"]
    row_w = 28
    cell_w = 17

    print(f"\n{'=' * 140}")
    print(f"  {group_name.upper()} DPO response length")
    print(f"{'=' * 140}")

    # Avg DPO length line (per LLM, from first available method; overall avg across LLMs)
    avg_lens = {}
    for row in present_rows:
        for llm in present_llms:
            cell = data.get(row, {}).get(llm)
            if cell and llm not in avg_lens:
                avg_lens[llm] = cell["avg_dpo_len"]
    overall_avg_len = sum(avg_lens.values()) / len(avg_lens) if avg_lens else 0
    len_line = f"{'Avg DPO len':<{row_w}}" + "".join(
        f"{'~' + str(int(avg_lens.get(llm, 0))) + ' words':^{cell_w*2}}" for llm in present_llms
    ) + f"{'~' + str(int(overall_avg_len)) + ' words':^{cell_w*2}}"
    print(len_line)

    # Sub-header: LLM names (including Avg column)
    subhdr = f"{'':<{row_w}}" + "".join(f"{llm:^{cell_w * 2}}" for llm in all_llms)
    header = f"{'Method':<{row_w}}" + "".join(
        f"{'Score(D/S)':^{cell_w}}{'WinRate(D/S)':^{cell_w}}" for _ in all_llms
    )
    print(subhdr)
    print(header)
    print("-" * len(header))

    for row in present_rows:
        line = f"{row:<{row_w}}"
        row_cells = [data.get(row, {}).get(llm) for llm in present_llms]
        avg_cell = avg_across_llms(row_cells)
        for cell in row_cells + [avg_cell]:
            if cell:
                score_str = f"{cell['dpo_avg_score']:.3f}/{cell['sft_avg_score']:.3f}"
                win_str   = f"{cell['dpo_win_rate']:.3f}/{cell['sft_win_rate']:.3f}"
                line += f"{score_str:^{cell_w}}{win_str:^{cell_w}}"
            else:
                line += " " * cell_w * 2
        print(line)

for group in ["short", "medium", "long"]:
    print_length_table(group, length_tables[group])

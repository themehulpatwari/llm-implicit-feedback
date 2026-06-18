import json
import os

#FOLDER = "eval_results/first_50"
FOLDER = "eval_results"

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

# Order matters: longer prefixes must come before shorter ones to avoid partial matches
PREFIX_MAP = [
    ("rdpo_bert_all_new",  "ModernBERT + Text + IF"),
    ("rdpo_bert_base_new", "ModernBERT + Text"),
    ("rdpo_rf_imp_new_gaze",  "RF + (IF - Mouse)"),
    ("rdpo_rf_imp_new_mouse", "RF + (IF - Gaze)"),
    ("rdpo_rf_imp_new",    "RF + IF"),
    ("eye_rev",            "Explicit Feedback"),
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


def parse_filename(fname):
    # Strip prefix "eval_results_" and suffix "_bz2_alpha1.json"
    name = fname
    if not name.startswith("eval_results_") or not name.endswith("_bz2_alpha1_0_300.json"):
        return None, None
    name = name[len("eval_results_"):-len("_bz2_alpha1_0_300.json")]

    # Identify LLM suffix
    llm_key = None
    for key in sorted(LLM_MAP, key=len, reverse=True):
        if name.endswith("_" + key):
            llm_key = key
            name = name[: -(len(key) + 1)]
            break
    if llm_key is None:
        return None, None

    # Identify row prefix
    row_label = None
    for prefix, label in PREFIX_MAP:
        if name == prefix:
            row_label = label
            break
    if row_label is None:
        return None, None

    return LLM_MAP[llm_key], row_label


def load_data():
    data = {}  # data[row_label][llm_label] = (sft_score, dpo_score, sft_win, dpo_win)
    for fname in os.listdir(FOLDER):
        llm_label, row_label = parse_filename(fname)
        if llm_label is None:
            continue
        path = os.path.join(FOLDER, fname)
        with open(path) as f:
            metrics = json.load(f)["metrics"]
        data.setdefault(row_label, {})[llm_label] = (
            metrics["sft_avg_score"],
            metrics["dpo_avg_score"],
            metrics["sft_win_rate"],
            metrics["dpo_win_rate"],
        )
    return data


def fmt_score(sft, dpo):
    return f"{dpo} / {sft}"


def print_table(data):
    # Determine which LLMs are present
    present_llms = [llm for llm in LLM_ORDER if any(llm in data.get(row, {}) for row in ROW_ORDER)]
    present_rows = [row for row in ROW_ORDER if row in data]

    TAB = " & "

    # Header row 1: model names spanning 2 columns each
    header1 = TAB
    for llm in present_llms:
        header1 += TAB + llm + TAB
    print(header1)

    # Header row 2: Score / Win sub-headers
    header2 = TAB
    for _ in present_llms:
        header2 += "Overall" + TAB + "Win rate" + TAB
    print(header2)

    # Data rows
    for row in present_rows:
        line = row
        for llm in present_llms:
            cell = data.get(row, {}).get(llm)
            if cell:
                sft_score, dpo_score, sft_win, dpo_win = cell
                line += TAB + fmt_score(sft_score, dpo_score) + TAB + fmt_score(sft_win, dpo_win)
            else:
                line += TAB + TAB
        print(line)


if __name__ == "__main__":
    data = load_data()
    print_table(data)

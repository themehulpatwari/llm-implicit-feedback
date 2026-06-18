"""
Analyze MTurk human evaluation results and correlate with LLM-as-judge scores.
MTurk data: mturk_files/Batch_5390950_batch_results.csv
LLM judge:  eval_results/eval_results_rdpo_rf_imp_new_llama3_bz2_alpha1.json
"""

import csv
import json
import numpy as np
from scipy import stats
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score

# ── Option → integer mappings ───────────────────────────────────────────────

COMPARE_MAP = {
    "a_much_better":    +3,
    "a_better":         +2,
    "a_slightly_better":+1,
    "equal":             0,
    "b_slightly_better":-1,
    "b_better":         -2,
    "b_much_better":    -3,
}

ERRORS_MAP = {
    "none":  0,
    "one":   1,
    "more":  2,
}

INFORMATIVE_MAP = {
    "almost_none":  1,
    "very_general": 2,
    "general":      3,
    "specific":     4,
    "very_specific":5,
}

RELEVANCY_MAP = {
    "irrelevant": 1,
    "somewhat":   2,
    "relevant":   3,
    "very_relevant": 4,
}

OVERALL_MAP = {
    "poor":           1,
    "dissatisfactory":2,
    "acceptable":     3,
    "good":           4,
    "excellent":      5,
}

SUPPORTS_MAP = {
    "no":  0,
    "yes": 1,
}


def parse_mturk(path: str) -> list[dict]:
    """Load and convert MTurk CSV rows to typed dicts, excluding rejected assignments."""
    rows = []
    with open(path) as f:
        for raw in csv.DictReader(f):
            if raw.get("AssignmentStatus", "").strip() == "Rejected":
                continue
            idx     = int(raw["Input.index"])
            llm_a   = raw["Input.llm_a"].strip()   # 'dpo' or 'sft'
            llm_b   = raw["Input.llm_b"].strip()
            worker  = raw["WorkerId"]

            compare_raw = raw["Answer.q_compare"].strip()
            compare_a   = COMPARE_MAP.get(compare_raw)           # +3=A much better
            # Normalise to DPO-relative: positive = DPO is better
            if llm_a == "dpo":
                compare_dpo = compare_a                          # +3 → DPO much better
            else:
                compare_dpo = -compare_a if compare_a is not None else None  # flip

            def score_response(prefix):
                return {
                    "errors":    ERRORS_MAP.get(raw[f"Answer.{prefix}_errors"].strip()),
                    "informative": INFORMATIVE_MAP.get(raw[f"Answer.{prefix}_informative"].strip()),
                    "relevancy": RELEVANCY_MAP.get(raw[f"Answer.{prefix}_relevancy"].strip()),
                    "overall":   OVERALL_MAP.get(raw[f"Answer.{prefix}_overall"].strip()),
                    "supports":  SUPPORTS_MAP.get(raw[f"Answer.{prefix}_supports"].strip()),
                }

            scores_a = score_response("qa")
            scores_b = score_response("qb")

            # Re-label per-response scores as SFT / DPO
            if llm_a == "sft":
                scores_sft, scores_dpo = scores_a, scores_b
            else:
                scores_dpo, scores_sft = scores_a, scores_b

            rows.append({
                "index":       idx,
                "worker":      worker,
                "llm_a":       llm_a,
                "llm_b":       llm_b,
                "compare_raw": compare_raw,
                "compare_a":   compare_a,
                "compare_dpo": compare_dpo,
                "sft":         scores_sft,
                "dpo":         scores_dpo,
            })
    return rows


def parse_llm_judge(path: str) -> dict[int, dict]:
    """Return {index: judgment_dict} for the 50 eval results."""
    with open(path) as f:
        data = json.load(f)
    out = {}
    for item in data["results"]:
        j = item["judgment"]
        idx = item["index"]
        winner = j.get("winner_model", "")
        if winner == "DPO":
            win_dpo = 1
        elif winner == "SFT":
            win_dpo = -1
        else:
            win_dpo = 0
        out[idx] = {
            "score_sft":   j.get("score_sft"),
            "score_dpo":   j.get("score_dpo"),
            "score_diff":  (j.get("score_dpo", 0) or 0) - (j.get("score_sft", 0) or 0),
            "win_dpo":     win_dpo,
            "winner_model": winner,
        }
    return out


# ── Load data ────────────────────────────────────────────────────────────────

#mturk_rows  = parse_mturk("mturk_files/Batch_5390950_batch_results.csv")
#mturk_rows  = parse_mturk("mturk_files/Batch_5391068_batch_results_base_0_10.csv")
#mturk_rows  = parse_mturk("mturk_files/Batch_5391110_batch_results_base_10_30_final.csv")
#mturk_rows  = parse_mturk("mturk_files/Batch_5391404_batch_results_rf_imp_10_30.csv")
#mturk_rows  = parse_mturk("mturk_files/Batch_5391404_batch_results_rf_imp_10_30_final.csv")
mturk_rows  = parse_mturk("mturk_files/Batch_5391068_5391110_batch_results_base_0_30.csv")
#mturk_rows  = parse_mturk("mturk_files/Batch_5390950_5391404_batch_results_rf_imp_0_30.csv")

llm_file = "eval_results/first_50/eval_results_rdpo_bert_base_new_llama3_bz2_alpha1.json"
#llm_file = "eval_results/first_50/eval_results_rdpo_rf_imp_new_llama3_bz2_alpha1.json"
llm_results = parse_llm_judge(
    llm_file
)

# Indices present in both datasets
common_indices = sorted(
    set(r["index"] for r in mturk_rows) & set(llm_results.keys())
)
print(f"MTurk indices:       {sorted(set(r['index'] for r in mturk_rows))}")
print(f"LLM judge indices:   {sorted(llm_results.keys())[:10]} ... (total {len(llm_results)})")
print(f"Common indices:      {common_indices}")
print()

# ── Section 1: Option → integer summary ──────────────────────────────────────

print("=" * 70)
print("SECTION 1: Converted Human Judgements (per annotation)")
print("=" * 70)
header = f"{'idx':>4}  {'worker':>18}  {'A':>4}  {'B':>4}  {'cmp_raw':>20}  {'cmp_dpo':>8}  {'sft_ovr':>7}  {'dpo_ovr':>7}"
print(header)
print("-" * len(header))
for r in mturk_rows:
    print(
        f"{r['index']:>4}  {r['worker']:>18}  {r['llm_a']:>4}  {r['llm_b']:>4}  "
        f"{r['compare_raw']:>20}  {str(r['compare_dpo']):>8}  "
        f"{str(r['sft']['overall']):>7}  {str(r['dpo']['overall']):>7}"
    )
print()

# ── Section 2: Per-index averaged human scores ───────────────────────────────

print("=" * 70)
print("SECTION 2: Per-index Averaged Human Scores vs LLM Judge")
print("=" * 70)

DIMS = ["errors", "informative", "relevancy", "overall", "supports"]

# Average across workers for each index
idx_human: dict[int, dict] = {}
for idx in common_indices:
    ann = [r for r in mturk_rows if r["index"] == idx]
    cmp_dpos = [a["compare_dpo"] for a in ann if a["compare_dpo"] is not None]
    avg_compare_dpo = np.mean(cmp_dpos) if cmp_dpos else None

    avg_sft, avg_dpo = {}, {}
    for dim in DIMS:
        vals_sft = [a["sft"][dim] for a in ann if a["sft"][dim] is not None]
        vals_dpo = [a["dpo"][dim] for a in ann if a["dpo"][dim] is not None]
        avg_sft[dim] = np.mean(vals_sft) if vals_sft else None
        avg_dpo[dim] = np.mean(vals_dpo) if vals_dpo else None

    idx_human[idx] = {
        "compare_dpo": avg_compare_dpo,
        "sft": avg_sft,
        "dpo": avg_dpo,
        "n_workers": len(ann),
    }

hdr2 = f"{'idx':>4}  {'cmp_dpo':>8}  {'llm_diff':>9}  {'llm_win':>8}  " \
       f"{'sft_ovr':>7}  {'dpo_ovr':>7}  {'sft_err':>7}  {'dpo_err':>7}"
print(hdr2)
print("-" * len(hdr2))
for idx in common_indices:
    h = idx_human[idx]
    lj = llm_results[idx]
    print(
        f"{idx:>4}  {h['compare_dpo']:>8.2f}  {lj['score_diff']:>9.1f}  "
        f"{lj['winner_model']:>8}  "
        f"{h['sft']['overall']:>7.2f}  {h['dpo']['overall']:>7.2f}  "
        f"{h['sft']['errors']:>7.2f}  {h['dpo']['errors']:>7.2f}"
    )
print()

# ── Section 3: Correlation Analysis ─────────────────────────────────────────

print("=" * 70)
print("SECTION 3: Correlation — Human vs LLM-as-Judge")
print("=" * 70)

human_compare_dpo = [idx_human[i]["compare_dpo"] for i in common_indices]
llm_score_diff    = [llm_results[i]["score_diff"]  for i in common_indices]
llm_win_dpo       = [llm_results[i]["win_dpo"]     for i in common_indices]

# Pearson correlation: human compare_dpo vs LLM score_diff
r_pearson, p_pearson = stats.pearsonr(human_compare_dpo, llm_score_diff)
print(f"\nHuman compare_dpo (avg) vs LLM score_diff (score_dpo − score_sft):")
print(f"  Pearson  r = {r_pearson:+.4f},  p = {p_pearson:.4f}  (n={len(common_indices)})")

r_spearman, p_spearman = stats.spearmanr(human_compare_dpo, llm_score_diff)
print(f"  Spearman r = {r_spearman:+.4f},  p = {p_spearman:.4f}")

# Pearson: human compare_dpo vs LLM win direction (+1 DPO / 0 tie / -1 SFT)
r2, p2 = stats.pearsonr(human_compare_dpo, llm_win_dpo)
print(f"\nHuman compare_dpo vs LLM winner direction:")
print(f"  Pearson  r = {r2:+.4f},  p = {p2:.4f}")

# Per-annotation (not averaged) correlation
all_compare_dpo = [r["compare_dpo"] for r in mturk_rows if r["index"] in llm_results and r["compare_dpo"] is not None]
all_llm_diff    = [llm_results[r["index"]]["score_diff"] for r in mturk_rows if r["index"] in llm_results and r["compare_dpo"] is not None]

r3, p3 = stats.pearsonr(all_compare_dpo, all_llm_diff)
r3s, p3s = stats.spearmanr(all_compare_dpo, all_llm_diff)
print(f"\nPer-annotation (n={len(all_compare_dpo)}) human compare_dpo vs LLM score_diff:")
print(f"  Pearson  r = {r3:+.4f},  p = {p3:.4f}")
print(f"  Spearman r = {r3s:+.4f},  p = {p3s:.4f}")

# Agreement rate: do human and LLM agree on who wins (ignoring ties)?
agreements = 0
total_decisive = 0
for i in common_indices:
    h_sign = np.sign(idx_human[i]["compare_dpo"])
    lj_sign = np.sign(llm_results[i]["win_dpo"])
    if h_sign != 0 and lj_sign != 0:
        total_decisive += 1
        if h_sign == lj_sign:
            agreements += 1

print(f"\nWin-direction agreement (excluding ties on either side): "
      f"{agreements}/{total_decisive} = {100*agreements/total_decisive:.1f}%")

# Correlation between human overall scores and LLM absolute scores
human_sft_overall = [idx_human[i]["sft"]["overall"] for i in common_indices]
human_dpo_overall = [idx_human[i]["dpo"]["overall"] for i in common_indices]
valid_sft = [(h, l) for h, l in zip(human_sft_overall, [llm_results[j]["score_sft"] for j in common_indices]) if l is not None]
valid_dpo = [(h, l) for h, l in zip(human_dpo_overall, [llm_results[j]["score_dpo"] for j in common_indices]) if l is not None]

if valid_sft:
    h_sft, l_sft = zip(*valid_sft)
    r_os, p_os = stats.pearsonr(h_sft, l_sft)
    rs_os, ps_os = stats.spearmanr(h_sft, l_sft)
    print(f"\nHuman overall (SFT) vs LLM score_sft (n={len(h_sft)}):")
    print(f"  Pearson  r = {r_os:+.4f},  p = {p_os:.4f}")
    print(f"  Spearman ρ = {rs_os:+.4f},  p = {ps_os:.4f}")

if valid_dpo:
    h_dpo, l_dpo = zip(*valid_dpo)
    r_od, p_od = stats.pearsonr(h_dpo, l_dpo)
    rs_od, ps_od = stats.spearmanr(h_dpo, l_dpo)
    print(f"\nHuman overall (DPO) vs LLM score_dpo (n={len(h_dpo)}):")
    print(f"  Pearson  r = {r_od:+.4f},  p = {p_od:.4f}")
    print(f"  Spearman ρ = {rs_od:+.4f},  p = {ps_od:.4f}")

# Pooled: human (SFT+DPO) overall vs LLM (score_sft+score_dpo)
valid_pooled = [(h, l) for h, l in (
    list(zip(human_sft_overall, [llm_results[j]["score_sft"] for j in common_indices])) +
    list(zip(human_dpo_overall, [llm_results[j]["score_dpo"] for j in common_indices]))
) if l is not None]
if valid_pooled:
    h_pool, l_pool = zip(*valid_pooled)
    r_op, p_op = stats.pearsonr(h_pool, l_pool)
    rs_op, ps_op = stats.spearmanr(h_pool, l_pool)
    print(f"\nHuman overall (SFT+DPO) vs LLM score (SFT+DPO pooled) (n={len(h_pool)}):")
    print(f"  Pearson  r = {r_op:+.4f},  p = {p_op:.4f}")
    print(f"  Spearman ρ = {rs_op:+.4f},  p = {ps_op:.4f}")

print()

# ── Section 4: Human Performance — SFT vs DPO by dimension ──────────────────

print("=" * 70)
print("SECTION 4: Human Evaluation — SFT vs DPO by Dimension")
print("=" * 70)

# Collect all annotations (all 20 rows)
all_rows = mturk_rows

# Per-dimension summary
dim_labels = {
    "errors":      "Factual Errors (0=none, 1=one, 2=more)",
    "informative": "Informativeness (1=almost none … 5=very specific)",
    "relevancy":   "Relevancy (1=irrelevant … 4=very relevant)",
    "overall":     "Overall Quality (1=poor … 5=excellent)",
    "supports":    "URL Supports Claim (0=no, 1=yes)",
}

# Average cmp_dpo and significance
all_cmp_dpos = [r["compare_dpo"] for r in all_rows if r["compare_dpo"] is not None]
avg_cmp_dpo = np.mean(all_cmp_dpos)
_, p_cmp_ttest = stats.ttest_1samp(all_cmp_dpos, 0)
if len(set(all_cmp_dpos)) > 1 and any(v != 0 for v in all_cmp_dpos):
    _, p_cmp_wilcox = stats.wilcoxon(all_cmp_dpos)
else:
    p_cmp_wilcox = float("nan")
print(f"\nOverall comparison vote (cmp_dpo, +3=DPO much better … −3=SFT much better):")
print(f"  Mean cmp_dpo = {avg_cmp_dpo:+.3f}  (n={len(all_cmp_dpos)})")
print(f"  t-test vs 0:    t-stat, p = {p_cmp_ttest:.4f}")
print(f"  Wilcoxon vs 0:           p = {p_cmp_wilcox:.4f}")

print(f"\n{'Dimension':<42}  {'SFT mean':>9}  {'DPO mean':>9}  {'Δ (DPO−SFT)':>11}  {'p-value':>9}  {'DPO win%':>9}  {'SFT win%':>9}  {'winner':>6}")
print("-" * 120)

dim_results = {}
for dim in DIMS:
    sft_vals = [r["sft"][dim] for r in all_rows if r["sft"][dim] is not None]
    dpo_vals = [r["dpo"][dim] for r in all_rows if r["dpo"][dim] is not None]

    sft_mean = np.mean(sft_vals)
    dpo_mean = np.mean(dpo_vals)
    delta    = dpo_mean - sft_mean

    # Paired Wilcoxon signed-rank test (per-annotation)
    paired_sft = []
    paired_dpo = []
    for r in all_rows:
        s, d = r["sft"][dim], r["dpo"][dim]
        if s is not None and d is not None:
            paired_sft.append(s)
            paired_dpo.append(d)

    if len(paired_sft) > 2 and len(set(np.array(paired_sft) - np.array(paired_dpo))) > 1:
        _, p_val = stats.wilcoxon(paired_sft, paired_dpo)
    else:
        p_val = float("nan")

    # Per-annotation win rate for DPO
    dpo_wins_dim = sft_wins_dim = ties_dim = 0
    for r in all_rows:
        s, d = r["sft"][dim], r["dpo"][dim]
        if s is None or d is None:
            continue
        if dim == "errors":
            if d < s: dpo_wins_dim += 1
            elif d > s: sft_wins_dim += 1
            else: ties_dim += 1
        else:
            if d > s: dpo_wins_dim += 1
            elif d < s: sft_wins_dim += 1
            else: ties_dim += 1
    total_dim = dpo_wins_dim + sft_wins_dim + ties_dim
    win_rate_dpo = dpo_wins_dim / total_dim if total_dim > 0 else float("nan")
    win_rate_sft = sft_wins_dim / total_dim if total_dim > 0 else float("nan")

    winner = "DPO" if delta > 0 else ("SFT" if delta < 0 else "TIE")
    if dim == "errors":
        winner = "SFT" if delta > 0 else ("DPO" if delta < 0 else "TIE")

    sig = "**" if p_val < 0.05 else ("*" if p_val < 0.10 else "  ")
    dim_results[dim] = {"sft": sft_mean, "dpo": dpo_mean, "delta": delta, "p": p_val,
                        "dpo_win": dpo_wins_dim, "sft_win": sft_wins_dim, "tie": ties_dim}

    label = dim_labels[dim]
    print(f"{label:<42}  {sft_mean:>9.3f}  {dpo_mean:>9.3f}  {delta:>+11.3f}  {p_val:>9.4f}  {win_rate_dpo:>8.1%}  {win_rate_sft:>8.1%}  {winner:>4}{sig}")

print()
print("Note: * p<0.10, ** p<0.05 (Wilcoxon signed-rank, paired per annotation)")

# Comparison direction summary
print()
print("=" * 70)
print("SECTION 4b: Comparison Vote Distribution (human)")
print("=" * 70)

compare_counts: dict[str, int] = defaultdict(int)
dpo_win = sft_win = tie = 0
for r in all_rows:
    compare_counts[r["compare_raw"]] += 1
    c = r["compare_dpo"]
    if c is None:
        continue
    if c > 0:
        dpo_win += 1
    elif c < 0:
        sft_win += 1
    else:
        tie += 1

total = len(all_rows)
for label, val in sorted(COMPARE_MAP.items(), key=lambda x: -x[1]):
    count = compare_counts.get(label, 0)
    print(f"  {label:<22}  {count:>3}  ({100*count/total:.1f}%)")

print()
print(f"  DPO preferred: {dpo_win}/{total} = {100*dpo_win/total:.1f}%")
print(f"  SFT preferred: {sft_win}/{total} = {100*sft_win/total:.1f}%")
print(f"  Tie:           {tie}/{total} = {100*tie/total:.1f}%")

# ── Section 5: LLM judge summary (for comparison) ────────────────────────────

print()
print("=" * 70)
print(f"SECTION 5: LLM-as-Judge Summary ({len(common_indices)} human-annotated prompts)")
print("=" * 70)
metrics = json.load(open(llm_file))["metrics"]
#metrics = json.load(open("eval_results/eval_results_rdpo_bert_base_new_llama3_bz2_alpha1.json"))["metrics"]

# Recompute metrics restricted to the human-annotated indices
_dpo_scores = [llm_results[i]["score_dpo"] for i in common_indices if llm_results[i]["score_dpo"] is not None]
_sft_scores = [llm_results[i]["score_sft"] for i in common_indices if llm_results[i]["score_sft"] is not None]
_dpo_wins   = sum(1 for i in common_indices if llm_results[i]["win_dpo"] == 1)
_sft_wins   = sum(1 for i in common_indices if llm_results[i]["win_dpo"] == -1)
_ties       = sum(1 for i in common_indices if llm_results[i]["win_dpo"] == 0)
_n          = len(common_indices)

print(f"  n_evaluated:      {_n}")
print(f"  DPO avg score:    {np.mean(_dpo_scores):.2f}")
print(f"  SFT avg score:    {np.mean(_sft_scores):.2f}")
print(f"  DPO win rate:     {100*_dpo_wins/_n:.1f}%  ({_dpo_wins} wins)")
print(f"  SFT win rate:     {100*_sft_wins/_n:.1f}%  ({_sft_wins} wins)")
print(f"  Tie rate:         {100*_ties/_n:.1f}%  ({_ties} ties)")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Human evaluation ({len(all_rows)} annotations, 10 prompts × 2 workers):

  ┌─────────────────────────────────────────────────────────────┐
  │ Dimension           SFT mean   DPO mean   Δ        Winner   │
  ├─────────────────────────────────────────────────────────────┤""")

for dim, res in dim_results.items():
    winner_str = "DPO" if (
        (dim != "errors" and res["dpo"] > res["sft"]) or
        (dim == "errors" and res["dpo"] < res["sft"])
    ) else ("SFT" if res["dpo"] != res["sft"] else "TIE")
    label = dim.capitalize()
    print(f"  │ {label:<20} {res['sft']:>8.3f}   {res['dpo']:>8.3f}  {res['delta']:>+7.3f}   {winner_str:<6}  │")

print(f"""  └─────────────────────────────────────────────────────────────┘

  Human comparison vote:  DPO {100*dpo_win/total:.2f}%  |  SFT {100*sft_win/total:.2f}%  |  Tie {100*tie/total:.2f}%

LLM-as-judge ({_n} prompts, human-annotated subset):
  DPO avg score {np.mean(_dpo_scores):.2f} vs SFT {np.mean(_sft_scores):.2f}
  DPO win rate {100*_dpo_wins/_n:.0f}% vs SFT {100*_sft_wins/_n:.0f}%

Human–LLM correlation (n={len(common_indices)} indices, averaged):
  Pearson r = {r_pearson:+.3f}  (p = {p_pearson:.3f})
  Spearman ρ = {r_spearman:+.3f}  (p = {p_spearman:.3f})
  Win-direction agreement = {agreements}/{total_decisive} ({100*agreements/total_decisive:.0f}%)
""")

# ── Section 6: Inter-Annotator Agreement ─────────────────────────────────────

print("=" * 70)
print("SECTION 6: Inter-Annotator Agreement (2 workers per prompt)")
print("=" * 70)

# Build paired lists: for each prompt index, worker1 vs worker2
all_indices_sorted = sorted(set(r["index"] for r in mturk_rows))

# Collect per-dimension paired values from worker1 and worker2
# Also collect compare_dpo pairs
iaa_pairs: dict[str, tuple[list, list]] = {
    "compare_dpo": ([], []),
    **{f"sft_{dim}": ([], []) for dim in DIMS},
    **{f"dpo_{dim}": ([], []) for dim in DIMS},
}

for idx in all_indices_sorted:
    ann = [r for r in mturk_rows if r["index"] == idx]
    if len(ann) < 2:
        continue
    w1, w2 = ann[0], ann[1]

    # Comparison vote (DPO-normalised)
    if w1["compare_dpo"] is not None and w2["compare_dpo"] is not None:
        iaa_pairs["compare_dpo"][0].append(w1["compare_dpo"])
        iaa_pairs["compare_dpo"][1].append(w2["compare_dpo"])

    # Per-response, per-dimension
    for dim in DIMS:
        for model in ("sft", "dpo"):
            v1 = w1[model][dim]
            v2 = w2[model][dim]
            if v1 is not None and v2 is not None:
                iaa_pairs[f"{model}_{dim}"][0].append(v1)
                iaa_pairs[f"{model}_{dim}"][1].append(v2)


def kappa_safe(a, b, weights=None):
    """Cohen's kappa; returns NaN when there's only one class."""
    try:
        return cohen_kappa_score(a, b, weights=weights)
    except Exception:
        return float("nan")


def pct_agree(a, b):
    return np.mean(np.array(a) == np.array(b))


def within1_agree(a, b):
    """Fraction of pairs where |a-b| <= 1."""
    return np.mean(np.abs(np.array(a) - np.array(b)) <= 1)


print()
print("─── Comparison vote (DPO-normalised, −3 … +3) ───")
c1, c2 = iaa_pairs["compare_dpo"]
n = len(c1)
print(f"  n pairs: {n}")
if n > 1:
    r_cmp, p_cmp = stats.pearsonr(c1, c2)
    rs_cmp, ps_cmp = stats.spearmanr(c1, c2)
    kappa_cmp = kappa_safe(c1, c2)
    kappa_cmp_lin = kappa_safe(c1, c2, weights="linear")
    dir_agree = np.mean(np.sign(np.array(c1)) == np.sign(np.array(c2)))
    exact_agree = pct_agree(c1, c2)
    w1_str = "  ".join(str(v) for v in c1)
    w2_str = "  ".join(str(v) for v in c2)
    print(f"  Worker1: [{w1_str}]")
    print(f"  Worker2: [{w2_str}]")
    print(f"  Exact agreement:          {exact_agree:.2f}  ({int(exact_agree*n)}/{n})")
    print(f"  Direction agreement:      {dir_agree:.2f}  ({int(dir_agree*n)}/{n})  (sign match: DPO/tie/SFT)")
    print(f"  Pearson r:                {r_cmp:+.3f}  (p={p_cmp:.3f})")
    print(f"  Spearman ρ:               {rs_cmp:+.3f}  (p={ps_cmp:.3f})")
    print(f"  Cohen's κ (unweighted):   {kappa_cmp:+.3f}")
    print(f"  Cohen's κ (linear wt):    {kappa_cmp_lin:+.3f}")

print()
print("─── Per-dimension IAA (pooled across SFT and DPO responses) ───")
print()

dim_scale_labels = {
    "errors":      "Errors (0–2)",
    "informative": "Informative (1–5)",
    "relevancy":   "Relevancy (1–4)",
    "overall":     "Overall (1–5)",
    "supports":    "Supports (0–1)",
}

header_iaa = (f"{'Dimension':<22}  {'Model':<5}  {'n':>4}  "
              f"{'Exact%':>7}  {'Within1%':>8}  {'κ(unw)':>8}  "
              f"{'κ(lin)':>8}  {'Pearson':>8}  {'Spearman':>9}")
print(header_iaa)
print("-" * len(header_iaa))

for dim in DIMS:
    for model in ("sft", "dpo"):
        a, b = iaa_pairs[f"{model}_{dim}"]
        n_d = len(a)
        if n_d < 2:
            continue
        exact  = pct_agree(a, b)
        w1pct  = within1_agree(a, b)
        kap    = kappa_safe(a, b)
        kap_l  = kappa_safe(a, b, weights="linear")
        r_d, _ = stats.pearsonr(a, b) if len(set(a)) > 1 and len(set(b)) > 1 else (float("nan"), None)
        rs_d,_ = stats.spearmanr(a, b) if n_d > 2 else (float("nan"), None)
        label  = dim_scale_labels[dim]
        print(f"{label:<22}  {model.upper():<5}  {n_d:>4}  "
              f"{exact:>7.2f}  {w1pct:>8.2f}  {kap:>+8.3f}  "
              f"{kap_l:>+8.3f}  {r_d:>+8.3f}  {rs_d:>+9.3f}")

print()

# Pooled across both models for a single per-dimension row
print("─── Pooled (SFT + DPO combined) ───")
print()
header_pool = (f"{'Dimension':<22}  {'n':>4}  "
               f"{'Exact%':>7}  {'Within1%':>8}  {'κ(unw)':>8}  "
               f"{'κ(lin)':>8}  {'Pearson':>8}  {'Spearman':>9}")
print(header_pool)
print("-" * len(header_pool))

for dim in DIMS:
    a_pool, b_pool = [], []
    for model in ("sft", "dpo"):
        a, b = iaa_pairs[f"{model}_{dim}"]
        a_pool.extend(a)
        b_pool.extend(b)
    n_p = len(a_pool)
    if n_p < 2:
        continue
    exact  = pct_agree(a_pool, b_pool)
    w1pct  = within1_agree(a_pool, b_pool)
    kap    = kappa_safe(a_pool, b_pool)
    kap_l  = kappa_safe(a_pool, b_pool, weights="linear")
    r_p, _ = stats.pearsonr(a_pool, b_pool) if len(set(a_pool)) > 1 and len(set(b_pool)) > 1 else (float("nan"), None)
    rs_p,_ = stats.spearmanr(a_pool, b_pool) if n_p > 2 else (float("nan"), None)
    label  = dim_scale_labels[dim]
    print(f"{label:<22}  {n_p:>4}  "
          f"{exact:>7.2f}  {w1pct:>8.2f}  {kap:>+8.3f}  "
          f"{kap_l:>+8.3f}  {r_p:>+8.3f}  {rs_p:>+9.3f}")

print()
print("Note: κ(unw) = unweighted Cohen's kappa; κ(lin) = linear-weighted kappa")
print("      Within1% = fraction of pairs where |score1 − score2| ≤ 1")

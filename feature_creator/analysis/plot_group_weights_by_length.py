"""
Group-Weight Bar Chart — Response Length Comparison
=====================================================
Reads feature_importance/importance_{short,medium,long}.csv produced by
run_model_by_length.sh and plots a grouped bar chart showing total feature
importance per group (gaze / mouse / text) for each response-length bin.

Usage:
    cd /path/to/feature_creator
    python analysis/plot_group_weights_by_length.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

# ── project root on path ────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ============================================================================
# CONFIG
# ============================================================================
LABELS = ["short", "medium", "long"]
IMPORTANCE_DIR = os.path.join(project_root, "feature_importance")
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "plots", "group_weights_by_length.png"
)

PALETTE = {
    "text":    "#111111",
    "subtext": "#666666",
    "grid":    "#CCCCCC",
    "bg":      "#FFFFFF",
}

GROUP_COLORS = {
    "gaze":       "#4C9BE8",
    "mouse":      "#F4845F",
    "gaze+mouse": "#A78BFA",
    "text":       "#6BCB77",
}

# gaze+mouse is intentionally excluded from the bar chart
GROUPS = ["gaze", "mouse", "text"]

LENGTH_COLORS = {
    "short":  "#A8DADC",
    "medium": "#457B9D",
    "long":   "#1D3557",
}

# ============================================================================
# HELPERS
# ============================================================================

def feature_group(name: str) -> str:
    n = name.lower()
    if "cross_modality" in n:
        return "gaze+mouse"
    if "gaze" in n or 'camera_green' in n:
        return "gaze"
    if "mouse" in n:
        return "mouse"
    return "text"


def load_group_weights(label: str) -> dict[str, float]:
    """Load importance CSV for one length label and return summed weights per group."""
    path = os.path.join(IMPORTANCE_DIR, f"importance_{label}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {path}.\n"
            f"Run ./run_model_by_length.sh first to generate importance files."
        )
    df = pd.read_csv(path)
    # Use 'group' column if present, otherwise derive it
    if "group" not in df.columns:
        df["group"] = df["feature"].apply(feature_group)
    return df.groupby("group")["importance"].sum().to_dict()


# ============================================================================
# PLOT
# ============================================================================

def plot(group_weights_by_label: dict[str, dict[str, float]]):
    n_labels = len(LABELS)
    n_groups = len(GROUPS)
    bar_width = 0.22
    x = np.arange(n_labels)  # one cluster per response-length bin

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    for i, group in enumerate(GROUPS):
        values = [group_weights_by_label[label].get(group, 0.0) for label in LABELS]
        offset = (i - (n_groups - 1) / 2) * bar_width
        bars = ax.bar(
            x + offset, values,
            width=bar_width,
            color=GROUP_COLORS[group],
            label=group.capitalize(),
            edgecolor="white",
            linewidth=0.6,
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.003,
                f"{val:.3f}",
                ha="center", va="bottom",
                fontsize=8.5, color=PALETTE["subtext"],
            )

    ax.set_xticks(x)
    ax.set_xticklabels([l.capitalize() for l in LABELS], fontsize=13)
    ax.set_xlabel("Response Length", fontsize=11)
    ax.set_ylabel("Total Feature Importance (sum of Gini weights)", fontsize=11)
    ax.set_title(
        "Feature-Group Importance by Response Length",
        fontsize=14, fontweight="bold", pad=12, color=PALETTE["text"],
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, color=PALETTE["grid"])
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=10, colors=PALETTE["subtext"])
    ax.legend(title="Feature group", fontsize=10, title_fontsize=10,
              framealpha=0.2, loc="upper right")

    plt.tight_layout(pad=1.8)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved → {OUTPUT_PATH}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Loading group weights …")
    group_weights_by_label: dict[str, dict[str, float]] = {}
    for label in LABELS:
        gw = load_group_weights(label)
        group_weights_by_label[label] = gw
        print(f"  {label:8s}: { {g: f'{gw.get(g,0):.4f}' for g in GROUPS} }")

    print("\nPlotting …")
    plot(group_weights_by_label)
    print("Done.")


if __name__ == "__main__":
    main()

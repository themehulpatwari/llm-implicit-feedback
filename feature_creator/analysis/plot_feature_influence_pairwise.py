"""
Feature Influence Analysis — Pairwise Important Features Model
==============================================================
Answers: "How does each feature influence the model's predictions?"

Produces three publication-quality plots saved to:
  analysis/plots/pairwise_important_features/

  1. feature_importance.png   — Horizontal bar chart of RF feature importances,
                                color-coded by feature group (gaze / mouse / text)

  2. partial_dependence.png   — Grid of Partial Dependence Plots (PDPs) for the
                                top N most important features. Shows how moving a
                                single feature from low→high changes P(prefer B=1)
                                while all other features are held at their actual values.

  3. feature_vs_prediction.png — Scatter plots: actual feature value (X) vs
                                 OOF predicted confidence P(prefer B=1) (Y),
                                 with points colored by the true label.
                                 Uses out-of-fold predictions so every point is
                                 a held-out, unbiased estimate.

Usage:
    cd /path/to/feature_creator
    python analysis/plot_feature_influence_pairwise.py
"""

import os
import re
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.inspection import partial_dependence

warnings.filterwarnings("ignore")
matplotlib.use("Agg")  # non-interactive backend — safe on headless machines

# ── project root on path ────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ============================================================================
# CONFIGURATION  — mirror the production model exactly
# ============================================================================
CONFIG = {
    "RANDOM_STATE": 49,
    #"INPUT_CSV": os.path.join(project_root, "pairwise_output", "important_features_pairwise.csv"),
    "INPUT_CSV": os.path.join(project_root, "pairwise_output", "new_important_features_pairwise.csv"),
    "OUTPUT_DIR": os.path.join(os.path.dirname(__file__), "plots", "pairwise_important_features"),
    "CV_FOLDS": 5,
    "RF_PARAMS": {
        "n_estimators": 100,
        "max_depth": 5,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "random_state": 49,
        "n_jobs": -1,
    },
    # How many top features to show in the PDP grid and scatter grid
    "TOP_N_PDP": 12,
    "TOP_N_SCATTER": 12,
}

# ── Aesthetic constants ──────────────────────────────────────────────────────
PALETTE = {
    "gaze":       "#4C9BE8",   # blue
    "mouse":      "#F4845F",   # orange
    "label_0":    "#E05C5C",   # red  → preferred A
    "label_1":    "#4C9BE8",   # blue → preferred B
    "bg":         "#FFFFFF",
    "card":       "#FFFFFF",
    "text":       "#111111",
    "subtext":    "#666666",
    "grid":       "#CCCCCC",
    "accent":     "#7C6AF7",
}

GROUP_COLORS = {
    "gaze":       "#4C9BE8",   # blue
    "mouse":      "#F4845F",   # orange
    "gaze+mouse": "#A78BFA",   # purple
    "text":       "#6BCB77",   # green
}

plt.rcParams.update({
    "figure.facecolor":  PALETTE["bg"],
    "axes.facecolor":    PALETTE["card"],
    "axes.edgecolor":    PALETTE["grid"],
    "axes.labelcolor":   PALETTE["text"],
    "axes.titlecolor":   PALETTE["text"],
    "xtick.color":       PALETTE["subtext"],
    "ytick.color":       PALETTE["subtext"],
    "text.color":        PALETTE["text"],
    "grid.color":        PALETTE["grid"],
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
})

# ============================================================================
# HELPERS
# ============================================================================

def feature_group(name: str) -> str:
    """Classify a feature into gaze / mouse / gaze+mouse / text."""
    n = name.lower()
    if "cross_modality" in n:
        return "gaze+mouse"
    if "gaze" in n or 'camera_green' in n:
        return "gaze"
    if "mouse" in n:
        return "mouse"
    return "text"


def feature_color(name: str) -> str:
    return GROUP_COLORS[feature_group(name)]


def short_name(name: str, max_len: int = 38) -> str:
    """Shorten a feature name for axis labels."""
    return name if len(name) <= max_len else "…" + name[-(max_len - 1):]


# Mapping from base variable suffix → paper display name
FEATURE_NAME_MAP = {
    # Structural
    "response_length":                     "Response Length",
    "user_query_length":                   "Query Length",
    # Individual (left / right)
    "max_idx":                             "Max Character",
    "max_idx_ratio":                       "Norm. Max Character",
    "reviewing_engaged_time_s":            "Reviewing Time",
    "overall_attention_ratio":             "Total Norm. Points",
    "reviewing_onscreen_ratio":            "Reviewing Norm. Points",
    "onscreen_points":                     "Total Points",
    "total_entries":                       "Total Records",
    "focused_engagement_ratio":            "Total Norm. Time",
    "normalized_avg_char_position":        "Avg of Norm. Gazing Character",
    # Comparison
    "comparison_reviewing_activity_ratio": "Reviewing Norm. Time Ratio",
    "comparison_reviewing_time_diff":      "Reviewing Time Diff",
    "comparison_reviewing_time_ratio":     "Reviewing Time Ratio",
    "comparison_which_side_read_further":  "Max Character Pairwise Comparison",
    'reviewing_duration_ratio_gaze_mouse': "Ratio of Gaze and Mouse",
    'camera_green': "Proper Head Position Ratio"
}


def _ordinal(n: int) -> str:
    """Return ordinal string (1→'1st', 2→'2nd', 3→'3rd', …)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def paper_name(name: str) -> str:
    """Convert an internal variable name to its paper display name.

    Handles three naming conventions found in the CSV:
      1. {gaze|mouse}_{left|right}_{base}
      2. response_{A|B}_{gaze|mouse}_{base}   (A=Left, B=Right)
      3. {gaze|mouse}_{base}_{left|right}     (side as suffix)
    """
    if name in FEATURE_NAME_MAP:
        return FEATURE_NAME_MAP[name]

    rest = name
    side = ""
    modality = ""

    # Convention 2: response_A_ / response_B_ encodes side
    if rest.startswith("response_A_"):
        side = "Left"
        rest = rest[len("response_A_"):]
    elif rest.startswith("response_B_"):
        side = "Right"
        rest = rest[len("response_B_"):]

    # Modality prefix
    if rest.startswith("gaze_"):
        modality = "Gaze"
        rest = rest[5:]
    elif rest.startswith("mouse_"):
        modality = "Mouse"
        rest = rest[6:]
    elif rest.startswith("cross_modality_"):
        modality = "Mouse + Gaze"
        rest = rest[15:]

    # Convention 1: left_ / right_ prefix (when side not already set)
    if not side:
        if rest.startswith("left_"):
            side = "Left"
            rest = rest[5:]
        elif rest.startswith("right_"):
            side = "Right"
            rest = rest[6:]

    # Convention 3: _left / _right suffix
    if not side:
        if rest.endswith("_left"):
            side = "Left"
            rest = rest[:-5]
        elif rest.endswith("_right"):
            side = "Right"
            rest = rest[:-6]

    # Window features: (gaze_|mouse_)?window_NNN
    win_match = re.match(r"(?:gaze_|mouse_)?window_0*(\d+)$", rest)
    if win_match:
        n = int(win_match.group(1))
        base_desc = f"Avg. Char. in {_ordinal(n)} Window"
        parts = [p for p in [side, base_desc] if p]
        label = " ".join(parts)
        if modality:
            label += f" ({modality})"
        return label

    base_desc = FEATURE_NAME_MAP.get(rest, rest)
    parts = [p for p in [side, base_desc] if p]
    label = " ".join(parts)
    if modality:
        label += f" ({modality})"
    return label


def ensure_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


# ============================================================================
# DATA LOADING & MODEL TRAINING
# ============================================================================

def load_data(filepath: str):
    """Return X (features), y (target), and the raw dataframe."""
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["binary_preference"])

    text_cols = ["user_query", "llm_response_1", "llm_response_2", "query_id", "domain"]
    target    = "binary_preference"

    feature_cols = [c for c in df.columns if c not in text_cols and c != target]
    X = df[feature_cols].astype(float).copy()
    y = df[target].copy()

    print(f"Loaded  {df.shape[0]} rows × {X.shape[1]} features")
    print(f"Target distribution:  {dict(y.value_counts().sort_index())}")
    return X, y, df


def train_full_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """Train one RF on the full dataset (for feature importance + PDPs)."""
    rf = RandomForestClassifier(**CONFIG["RF_PARAMS"])
    rf.fit(X, y)
    print("Full-dataset model trained ✓")
    return rf


def generate_oof_predictions(X: pd.DataFrame, y: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """
    Out-of-fold predictions — each sample predicted exactly once on held-out fold.
    Returns (oof_pred, oof_confidence) arrays of length n_samples.
    """
    n = len(X)
    oof_pred  = np.full(n, np.nan)
    oof_conf  = np.full(n, np.nan)

    cv = KFold(n_splits=CONFIG["CV_FOLDS"], shuffle=True, random_state=CONFIG["RANDOM_STATE"])
    for fold, (tr_idx, te_idx) in enumerate(cv.split(X, y), 1):
        rf = RandomForestClassifier(**CONFIG["RF_PARAMS"])
        rf.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_pred[te_idx] = rf.predict(X.iloc[te_idx])
        oof_conf[te_idx] = rf.predict_proba(X.iloc[te_idx])[:, 1]
        print(f"  Fold {fold}: predicted {len(te_idx)} samples")

    print(f"OOF complete — NaN remaining: {np.isnan(oof_conf).sum()}")
    return oof_pred, oof_conf


def compute_feature_importance(model: RandomForestClassifier, feature_names) -> pd.DataFrame:
    fi = pd.DataFrame({
        "feature":    feature_names,
        "importance": model.feature_importances_,
        "group":      [feature_group(f) for f in feature_names],
        "color":      [feature_color(f) for f in feature_names],
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    return fi


# ============================================================================
# PLOT 1 — FEATURE IMPORTANCE BAR CHART
# ============================================================================

def plot_feature_importance(fi: pd.DataFrame, out_dir: str, top_n: int = 10):
    top = fi.head(top_n).copy()
    top = top.iloc[::-1]   # flip so highest is at top

    fig, ax = plt.subplots(figsize=(13, max(8, top_n * 0.55)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["card"])

    bars = ax.barh(
        range(len(top)),
        top["importance"],
        color=top["color"],
        height=0.45,
        edgecolor="none",
        alpha=0.92,
    )

    # Value labels on each bar
    for bar, val in zip(bars, top["importance"]):
        ax.text(
            bar.get_width() + 0.0005,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va="center",
            ha="left",
            fontsize=13,
            color=PALETTE["subtext"],
        )

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([paper_name(f) for f in top["feature"].tolist()], fontsize=28)
    ax.set_xlabel("Mean Decrease in Impurity (Gini Importance)", fontsize=20)
    #ax.set_title("Feature Importance — Pairwise Important Features Model\n(Random Forest, trained on full dataset)", fontsize=16, fontweight="bold", pad=14)
    ax.tick_params(axis="x", labelsize=13)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    # Legend for groups
    legend_elements = [
        Line2D([0], [0], color=GROUP_COLORS["gaze"],       lw=6, label="Gaze feature"),
        Line2D([0], [0], color=GROUP_COLORS["mouse"],      lw=6, label="Mouse feature"),
        Line2D([0], [0], color=GROUP_COLORS["gaze+mouse"], lw=6, label="Gaze+Mouse feature"),
        Line2D([0], [0], color=GROUP_COLORS["text"],       lw=6, label="Text feature"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              bbox_to_anchor=(1.0, 1.01), ncol=len(legend_elements),
              framealpha=0.2, labelcolor=PALETTE["text"], fontsize=20,
              borderaxespad=0)

    plt.tight_layout(pad=1.5)
    plt.subplots_adjust(top=0.88, left=0.35)
    path = os.path.join(out_dir, "feature_importance.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved → {path}")


# ============================================================================
# PLOT 2 — PARTIAL DEPENDENCE PLOTS
# ============================================================================

def plot_partial_dependence(model: RandomForestClassifier, X: pd.DataFrame,
                            fi: pd.DataFrame, out_dir: str, top_n: int = 12):
    """Save one PDP PNG per feature into out_dir/partial_dependence/."""
    top_features = fi.head(top_n)["feature"].tolist()
    feature_indices = [list(X.columns).index(f) for f in top_features]

    sub_dir = os.path.join(out_dir, "partial_dependence")
    os.makedirs(sub_dir, exist_ok=True)

    for rank, (feat, feat_idx) in enumerate(zip(top_features, feature_indices), 1):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax.set_facecolor(PALETTE["card"])

        # Compute PDP
        pd_result = partial_dependence(
            model, X,
            features=[feat_idx],
            kind="average",
            grid_resolution=60,
        )
        grid_values = pd_result["grid_values"][0]
        avg_pred    = pd_result["average"][0]

        # Clip to actual data range (avoid extrapolation artifacts)
        col_data = X[feat].dropna()
        x_min, x_max = col_data.quantile(0.02), col_data.quantile(0.98)
        mask = (grid_values >= x_min) & (grid_values <= x_max)
        gv   = grid_values[mask]
        ap   = avg_pred[mask]

        # Main PDP line with gradient fill
        ax.plot(gv, ap, color=feature_color(feat), lw=2.5, zorder=3)
        ax.fill_between(gv, 0.5, ap, where=(ap >= 0.5),
                        alpha=0.20, color=PALETTE["label_1"], zorder=2)
        ax.fill_between(gv, 0.5, ap, where=(ap < 0.5),
                        alpha=0.20, color=PALETTE["label_0"], zorder=2)

        # Decision boundary at 0.5
        ax.axhline(0.5, color=PALETTE["subtext"], lw=1.2, linestyle="--", alpha=0.7, zorder=1)

        # Rug plot — actual data distribution along x-axis
        rug_y = np.full(len(col_data), ap.min() - 0.02)
        in_range = (col_data >= x_min) & (col_data <= x_max)
        ax.scatter(col_data[in_range], rug_y[in_range],
                   marker="|", s=25, alpha=0.30, color=feature_color(feat), zorder=4)

        group_label = feature_group(feat).capitalize()
        ax.set_title(f"{paper_name(feat)}",
                     fontsize=10, color=PALETTE["text"], pad=8, fontweight="bold")
        ax.set_xlabel("Feature value", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylabel("P(prefer right response = 1)", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylim(max(0, ap.min() - 0.06), min(1, ap.max() + 0.06))
        ax.yaxis.grid(True, linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8.5)

        # Annotation
        ax.annotate(
            "Dashed line = 0.5 decision boundary\nRug marks = actual data distribution",
            xy=(0.98, 0.04), xycoords="axes fraction",
            fontsize=7.5, color=PALETTE["subtext"], ha="right", va="bottom",
        )

        plt.tight_layout(pad=1.5)
        safe_name = feat.replace("/", "_").replace(" ", "_")
        path = os.path.join(sub_dir, f"{rank:02d}_{safe_name}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  PDP saved → {path}")

    print(f"Partial dependence plots saved to: {sub_dir}")


# ============================================================================
# PLOT 3 — FEATURE VALUE vs OOF PREDICTION SCATTER
# ============================================================================

def plot_feature_vs_oof(X: pd.DataFrame, y: pd.Series,
                        oof_conf: np.ndarray, fi: pd.DataFrame,
                        out_dir: str, top_n: int = 12):
    """Save one scatter PNG per feature into out_dir/feature_vs_prediction/."""
    top_features = fi.head(top_n)["feature"].tolist()

    sub_dir = os.path.join(out_dir, "feature_vs_prediction")
    os.makedirs(sub_dir, exist_ok=True)

    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE["label_0"],
               markersize=8, label="Preferred A (label=0)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE["label_1"],
               markersize=8, label="Preferred B (label=1)"),
        Line2D([0], [0], color="white", lw=2, alpha=0.7, label="Smoothed trend"),
    ]

    for rank, feat in enumerate(top_features, 1):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax.set_facecolor(PALETTE["card"])

        col  = X[feat].values
        conf = oof_conf
        labs = y.values

        # Remove NaNs
        mask = ~np.isnan(col) & ~np.isnan(conf)
        col, conf, labs = col[mask], conf[mask], labs[mask]

        # Jitter for binary/low-variance features to avoid overplotting
        if len(np.unique(col)) <= 10:
            jitter = np.random.default_rng(42).uniform(-0.02, 0.02, len(col))
        else:
            jitter = 0

        # Class 0 → preferred A (red), Class 1 → preferred B (blue)
        for cls, clr, lbl in [(0, PALETTE["label_0"], "Preferred A"),
                               (1, PALETTE["label_1"], "Preferred B")]:
            idx = labs == cls
            ax.scatter(
                col[idx] + jitter if np.isscalar(jitter) else col[idx] + jitter[idx],
                conf[idx],
                c=clr, s=18, alpha=0.50, edgecolors="none", label=lbl, zorder=3,
            )

        # Trend line (moving average on sorted x)
        sort_idx = np.argsort(col)
        window   = max(1, len(col) // 20)
        smoothed = np.convolve(conf[sort_idx], np.ones(window) / window, mode="valid")
        x_smooth = col[sort_idx][window // 2: window // 2 + len(smoothed)]
        ax.plot(x_smooth, smoothed, color="white", lw=2, alpha=0.75, zorder=4)

        # Decision boundary
        ax.axhline(0.5, color=PALETTE["subtext"], lw=1.2, linestyle="--", alpha=0.7)

        group_label = feature_group(feat).capitalize()
        ax.set_title(f"[#{rank}  {group_label}]  {paper_name(feat)}",
                     fontsize=10, color=PALETTE["text"], pad=8, fontweight="bold")
        ax.set_xlabel("Feature value", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylabel("OOF P(prefer B = 1)", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylim(-0.04, 1.04)
        ax.yaxis.grid(True, linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8.5)
        ax.legend(handles=legend_elements, fontsize=8, loc="upper left",
                  framealpha=0.25, labelcolor=PALETTE["text"])

        plt.tight_layout(pad=1.5)
        safe_name = feat.replace("/", "_").replace(" ", "_")
        path = os.path.join(sub_dir, f"{rank:02d}_{safe_name}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  Scatter saved → {path}")

    print(f"Feature vs prediction plots saved to: {sub_dir}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    np.random.seed(CONFIG["RANDOM_STATE"])
    ensure_output_dir(CONFIG["OUTPUT_DIR"])

    print("\n" + "=" * 70)
    print("FEATURE INFLUENCE ANALYSIS — Pairwise Important Features")
    print("=" * 70)

    # 1. Load data
    print("\n[1/4] Loading data …")
    X, y, _ = load_data(CONFIG["INPUT_CSV"])

    # 2. Train full model (for importance + PDPs)
    print("\n[2/4] Training full model …")
    model = train_full_model(X, y)

    # 3. Generate OOF predictions (for scatter plot)
    print("\n[3/4] Generating out-of-fold predictions …")
    _, oof_conf = generate_oof_predictions(X, y)

    # 4. Compute feature importance
    fi = compute_feature_importance(model, X.columns)
    print(f"\nTop 10 features:\n{fi[['feature','importance','group']].head(10).to_string(index=False)}")

    # 5. Produce plots
    print("\n[4/4] Generating plots …")
    out = CONFIG["OUTPUT_DIR"]

    plot_feature_importance(fi, out, top_n=50)
    plot_partial_dependence(model, X, fi, out, top_n=CONFIG["TOP_N_PDP"])
    plot_feature_vs_oof(X, y, oof_conf, fi, out, top_n=CONFIG["TOP_N_SCATTER"])

    print("\n" + "=" * 70)
    print(f"All plots saved to: {out}")
    print("  • feature_importance.png")
    print(f"  • partial_dependence/   ({CONFIG['TOP_N_PDP']} individual PNGs)")
    print(f"  • feature_vs_prediction/ ({CONFIG['TOP_N_SCATTER']} individual PNGs)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

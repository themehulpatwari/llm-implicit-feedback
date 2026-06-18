"""
Feature Influence Analysis — Pointwise Important Features Model
===============================================================
Answers: "How does each feature influence the model's predictions?"

Produces three publication-quality plot sets saved to:
  analysis/plots/pointwise_important_features/

  1. feature_importance.png        — Horizontal bar chart of RF feature importances,
                                     color-coded by feature group (gaze / mouse / text)

  2. partial_dependence/<n>_*.png  — One Partial Dependence Plot per top feature.
                                     X = feature value, Y = predicted Likert score (1–5)

  3. feature_vs_prediction/<n>_*.png — One scatter per top feature.
                                       X = actual feature value,
                                       Y = OOF predicted Likert score,
                                       color = actual Likert rating (1–5)

Usage:
    cd /path/to/feature_creator
    python analysis/plot_feature_influence_pointwise.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import BoundaryNorm
from matplotlib.cm import ScalarMappable
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.inspection import partial_dependence

warnings.filterwarnings("ignore")
matplotlib.use("Agg")

# ── project root on path ────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ============================================================================
# CONFIGURATION  — mirrors the production pointwise model exactly
# ============================================================================
CONFIG = {
    "RANDOM_STATE": 49,
    "INPUT_CSV": os.path.join(project_root, "pointwise_output", "important_features_pointwise.csv"),
    "OUTPUT_DIR": os.path.join(os.path.dirname(__file__), "plots", "pointwise_important_features"),
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
    "TOP_N_PDP":     12,
    "TOP_N_SCATTER": 12,
}

# ── Aesthetic constants ──────────────────────────────────────────────────────
PALETTE = {
    "gaze":       "#4C9BE8",
    "mouse":      "#F4845F",
    "bg":         "#0F1117",
    "card":       "#1A1D27",
    "text":       "#E8EAF0",
    "subtext":    "#8B90A0",
    "grid":       "#2A2D3A",
    "accent":     "#7C6AF7",
    "mean_line":  "#FFD166",
}

GROUP_COLORS = {
    "gaze":       "#4C9BE8",   # blue
    "mouse":      "#F4845F",   # orange
    "gaze+mouse": "#A78BFA",   # purple
    "text":       "#6BCB77",   # green
}

# 5-colour palette for Likert ratings 1–5
LIKERT_COLORS = {
    1: "#E05C5C",   # red
    2: "#F4845F",   # orange
    3: "#FFD166",   # yellow
    4: "#6BCB77",   # green
    5: "#4C9BE8",   # blue
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


def ensure_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


# ============================================================================
# DATA LOADING & MODEL TRAINING
# ============================================================================

def load_data(filepath: str):
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["likert_1"])

    text_cols = ["user_query", "llm_response_1", "user_id", "query_id", "domain", "preference"]
    target    = "likert_1"

    feature_cols = [c for c in df.columns if c not in text_cols and c != target]
    X = df[feature_cols].astype(float).copy()
    y = df[target].astype(float).copy()

    print(f"Loaded  {df.shape[0]} rows × {X.shape[1]} features")
    print(f"Target (Likert) stats:  mean={y.mean():.2f}  std={y.std():.2f}  "
          f"range=[{y.min():.0f}, {y.max():.0f}]")
    return X, y, df


def train_full_model(X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
    rf = RandomForestRegressor(**CONFIG["RF_PARAMS"])
    rf.fit(X, y)
    print("Full-dataset model trained ✓")
    return rf


def generate_oof_predictions(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    """OOF regression predictions — each sample predicted once on held-out fold."""
    n = len(X)
    oof_pred = np.full(n, np.nan)

    cv = KFold(n_splits=CONFIG["CV_FOLDS"], shuffle=True, random_state=CONFIG["RANDOM_STATE"])
    for fold, (tr_idx, te_idx) in enumerate(cv.split(X, y), 1):
        rf = RandomForestRegressor(**CONFIG["RF_PARAMS"])
        rf.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        oof_pred[te_idx] = rf.predict(X.iloc[te_idx])
        print(f"  Fold {fold}: predicted {len(te_idx)} samples")

    print(f"OOF complete — NaN remaining: {np.isnan(oof_pred).sum()}")
    return oof_pred


def compute_feature_importance(model: RandomForestRegressor, feature_names) -> pd.DataFrame:
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

def plot_feature_importance(fi: pd.DataFrame, out_dir: str, top_n: int = 30):
    top = fi.head(top_n).copy()
    top = top.iloc[::-1]

    fig, ax = plt.subplots(figsize=(13, max(8, top_n * 0.38)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["card"])

    bars = ax.barh(
        range(len(top)), top["importance"],
        color=top["color"], height=0.7, edgecolor="none", alpha=0.92,
    )
    for bar, val in zip(bars, top["importance"]):
        ax.text(
            bar.get_width() + 0.0005,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", ha="left",
            fontsize=7.5, color=PALETTE["subtext"],
        )

    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["feature"].tolist(), fontsize=7.5)
    ax.set_xlabel("Mean Decrease in Impurity (Gini Importance)", fontsize=10)
    ax.set_title(
        "Feature Importance — Pointwise Important Features Model\n"
        "(Random Forest Regressor, trained on full dataset)",
        fontsize=13, fontweight="bold", pad=14,
    )
    ax.xaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)

    legend_elements = [
        Line2D([0], [0], color=GROUP_COLORS["gaze"],       lw=6, label="Gaze feature"),
        Line2D([0], [0], color=GROUP_COLORS["mouse"],      lw=6, label="Mouse feature"),
        Line2D([0], [0], color=GROUP_COLORS["gaze+mouse"], lw=6, label="Gaze+Mouse feature"),
        Line2D([0], [0], color=GROUP_COLORS["text"],       lw=6, label="Text feature"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              framealpha=0.2, labelcolor=PALETTE["text"], fontsize=9)

    plt.tight_layout(pad=1.5)
    path = os.path.join(out_dir, "feature_importance.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved → {path}")


# ============================================================================
# PLOT 2 — PARTIAL DEPENDENCE PLOTS (one file per feature)
# ============================================================================

def plot_partial_dependence(model: RandomForestRegressor, X: pd.DataFrame,
                            fi: pd.DataFrame, y_mean: float,
                            out_dir: str, top_n: int = 12):
    """One PDP PNG per feature into out_dir/partial_dependence/."""
    top_features    = fi.head(top_n)["feature"].tolist()
    feature_indices = [list(X.columns).index(f) for f in top_features]

    sub_dir = os.path.join(out_dir, "partial_dependence")
    os.makedirs(sub_dir, exist_ok=True)

    for rank, (feat, feat_idx) in enumerate(zip(top_features, feature_indices), 1):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax.set_facecolor(PALETTE["card"])

        pd_result = partial_dependence(
            model, X, features=[feat_idx],
            kind="average", grid_resolution=60,
        )
        grid_values = pd_result["grid_values"][0]
        avg_pred    = pd_result["average"][0]

        col_data = X[feat].dropna()
        x_min, x_max = col_data.quantile(0.02), col_data.quantile(0.98)
        mask = (grid_values >= x_min) & (grid_values <= x_max)
        gv, ap = grid_values[mask], avg_pred[mask]

        # Line + fill relative to the mean rating
        ax.plot(gv, ap, color=feature_color(feat), lw=2.5, zorder=3)
        ax.fill_between(gv, y_mean, ap, where=(ap >= y_mean),
                        alpha=0.20, color=GROUP_COLORS["text"], zorder=2,
                        label=f"Above mean ({y_mean:.2f})")
        ax.fill_between(gv, y_mean, ap, where=(ap < y_mean),
                        alpha=0.20, color=PALETTE["mouse"], zorder=2,
                        label=f"Below mean ({y_mean:.2f})")

        # Mean rating reference line
        ax.axhline(y_mean, color=PALETTE["mean_line"], lw=1.2,
                   linestyle="--", alpha=0.8, zorder=1)

        # Rug plot
        in_range = (col_data >= x_min) & (col_data <= x_max)
        rug_y = np.full(in_range.sum(), ap.min() - 0.04)
        ax.scatter(col_data[in_range], rug_y,
                   marker="|", s=25, alpha=0.30,
                   color=feature_color(feat), zorder=4)

        group_label = feature_group(feat).capitalize()
        ax.set_title(f"[#{rank}  {group_label}]  {feat}",
                     fontsize=10, color=PALETTE["text"], pad=8, fontweight="bold")
        ax.set_xlabel("Feature value", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylabel("Predicted Likert score (1–5)", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylim(max(1, ap.min() - 0.15), min(5, ap.max() + 0.15))
        ax.yaxis.grid(True, linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8.5)

        ax.annotate(
            f"Dashed line = dataset mean ({y_mean:.2f})\nRug marks = actual data distribution",
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
# PLOT 3 — FEATURE VALUE vs OOF PREDICTION SCATTER (one file per feature)
# ============================================================================

def plot_feature_vs_oof(X: pd.DataFrame, y: pd.Series,
                        oof_pred: np.ndarray, fi: pd.DataFrame,
                        y_mean: float, out_dir: str, top_n: int = 12):
    """One scatter PNG per feature into out_dir/feature_vs_prediction/."""
    top_features = fi.head(top_n)["feature"].tolist()

    sub_dir = os.path.join(out_dir, "feature_vs_prediction")
    os.makedirs(sub_dir, exist_ok=True)

    # Build legend for Likert 1–5
    legend_elements = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor=LIKERT_COLORS[k], markersize=8,
               label=f"Likert = {k}")
        for k in sorted(LIKERT_COLORS)
    ]
    legend_elements.append(
        Line2D([0], [0], color="white", lw=2, alpha=0.75, label="Smoothed trend")
    )

    for rank, feat in enumerate(top_features, 1):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax.set_facecolor(PALETTE["card"])

        col  = X[feat].values
        pred = oof_pred
        labs = y.values.astype(int)   # Likert 1–5

        # Remove NaNs
        mask = ~np.isnan(col) & ~np.isnan(pred)
        col, pred, labs = col[mask], pred[mask], labs[mask]

        # Jitter for low-cardinality features
        if len(np.unique(col)) <= 10:
            jitter = np.random.default_rng(42).uniform(-0.015, 0.015, len(col))
        else:
            jitter = 0

        # Plot each Likert rating as a separate colour
        for rating in sorted(LIKERT_COLORS):
            idx = labs == rating
            if idx.sum() == 0:
                continue
            x_vals = col[idx] + (jitter[idx] if not np.isscalar(jitter) else jitter)
            ax.scatter(x_vals, pred[idx],
                       c=LIKERT_COLORS[rating], s=18, alpha=0.55,
                       edgecolors="none", zorder=3)

        # Smoothed trend (moving average)
        sort_idx = np.argsort(col)
        window   = max(1, len(col) // 20)
        smoothed = np.convolve(pred[sort_idx], np.ones(window) / window, mode="valid")
        x_smooth = col[sort_idx][window // 2: window // 2 + len(smoothed)]
        ax.plot(x_smooth, smoothed, color="white", lw=2, alpha=0.75, zorder=4)

        # Mean rating reference line
        ax.axhline(y_mean, color=PALETTE["mean_line"], lw=1.2,
                   linestyle="--", alpha=0.8)

        group_label = feature_group(feat).capitalize()
        ax.set_title(f"[#{rank}  {group_label}]  {feat}",
                     fontsize=10, color=PALETTE["text"], pad=8, fontweight="bold")
        ax.set_xlabel("Feature value", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylabel("OOF Predicted Likert score", fontsize=9, color=PALETTE["subtext"])
        ax.set_ylim(0.8, 5.2)
        ax.yaxis.grid(True, linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8.5)
        ax.legend(handles=legend_elements, fontsize=7.5, loc="upper center",
                  bbox_to_anchor=(0.5, -0.16), ncol=3,
                  framealpha=0.25, labelcolor=PALETTE["text"])

        plt.tight_layout(pad=1.5)
        plt.subplots_adjust(bottom=0.22)
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
    print("FEATURE INFLUENCE ANALYSIS — Pointwise Important Features")
    print("=" * 70)

    # 1. Load data
    print("\n[1/4] Loading data …")
    X, y, _ = load_data(CONFIG["INPUT_CSV"])
    y_mean = float(y.mean())

    # 2. Train full model
    print("\n[2/4] Training full model …")
    model = train_full_model(X, y)

    # 3. OOF predictions
    print("\n[3/4] Generating out-of-fold predictions …")
    oof_pred = generate_oof_predictions(X, y)

    # 4. Feature importance
    fi = compute_feature_importance(model, X.columns)
    print(f"\nTop 10 features:\n{fi[['feature','importance','group']].head(10).to_string(index=False)}")

    # 5. Plots
    print("\n[4/4] Generating plots …")
    out = CONFIG["OUTPUT_DIR"]

    plot_feature_importance(fi, out, top_n=30)
    plot_partial_dependence(model, X, fi, y_mean, out, top_n=CONFIG["TOP_N_PDP"])
    plot_feature_vs_oof(X, y, oof_pred, fi, y_mean, out, top_n=CONFIG["TOP_N_SCATTER"])

    print("\n" + "=" * 70)
    print(f"All plots saved to: {out}")
    print("  • feature_importance.png")
    print(f"  • partial_dependence/    ({CONFIG['TOP_N_PDP']} individual PNGs)")
    print(f"  • feature_vs_prediction/ ({CONFIG['TOP_N_SCATTER']} individual PNGs)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

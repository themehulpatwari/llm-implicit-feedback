import sys
import glob
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)

PRED_COL = "llm_judge_prediction"
LABEL_COL = "preference"
PROB1_COL = "llm_judge_confidence"


def eval_file(path: Path) -> None:
    df = pd.read_csv(path)

    missing = [c for c in [PRED_COL, LABEL_COL] if c not in df.columns]
    if missing:
        print(f"  [SKIP] missing columns: {missing}")
        return

    print(len(df))
    df = df.dropna(axis=0, how='any', subset = [PRED_COL, PROB1_COL, LABEL_COL])
    print(len(df))

    y_true = df[LABEL_COL].astype(int) - 1
    y_pred = df[PRED_COL].astype(int) - 1

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average=None, labels=[0, 1], zero_division=0)
    rec = recall_score(y_true, y_pred, average=None, labels=[0, 1], zero_division=0)
    f1 = f1_score(y_true, y_pred, average=None, labels=[0, 1], zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)

    print(f"  Accuracy      : {acc:.4f}")
    print(f"  F1 (macro)    : {f1_macro:.4f}")
    print(f"  Precision [0] : {prec[0]:.4f}   Precision [1] : {prec[1]:.4f}")
    print(f"  Recall    [0] : {rec[0]:.4f}   Recall    [1] : {rec[1]:.4f}")
    print(f"  F1        [0] : {f1[0]:.4f}   F1        [1] : {f1[1]:.4f}")

    if PROB1_COL in df.columns and df[PROB1_COL].notna().all():
        try:
            auc = roc_auc_score(y_true, df[PROB1_COL])
            print(f"  ROC-AUC       : {auc:.4f}")
        except ValueError as e:
            print(f"  ROC-AUC       : N/A ({e})")

    n = len(df)
    pos = y_true.sum()
    print(f"  Samples       : {n}  (pos={pos}, neg={n - pos})")


def main(pred_dir: str) -> None:
    csv_files = sorted(Path(pred_dir).rglob("*.csv"))
    if not csv_files:
        print(f"No CSV files found under: {pred_dir}")
        return

    for path in csv_files:
        print(f"\n{'='*60}")
        print(f"File: {path.relative_to(pred_dir)}")
        print(f"{'='*60}")
        eval_file(path)

    print()


if __name__ == "__main__":
    #pred_dir = sys.argv[1] if len(sys.argv) > 1 else "output_dir"
    pred_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    main(pred_dir)

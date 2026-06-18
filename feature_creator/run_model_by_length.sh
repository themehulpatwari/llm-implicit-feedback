#!/usr/bin/env bash
# Run model_important_features_pairwise.py for each response-length split.
# Feature importances are saved to feature_importance/importance_{short,medium,long}.csv

set -e
cd "$(dirname "$0")"

echo "=== SHORT ==="
python models/pairwise_model/model_important_features_pairwise.py \
    --input pairwise_output/new_important_features_pairwise_short.csv \
    --label short

echo "=== MEDIUM ==="
python models/pairwise_model/model_important_features_pairwise.py \
    --input pairwise_output/new_important_features_pairwise_medium.csv \
    --label medium

echo "=== LONG ==="
python models/pairwise_model/model_important_features_pairwise.py \
    --input pairwise_output/new_important_features_pairwise_long.csv \
    --label long

echo ""
echo "Done. Now plot group weights:"
echo "  python analysis/plot_group_weights_by_length.py"
python analysis/plot_group_weights_by_length.py
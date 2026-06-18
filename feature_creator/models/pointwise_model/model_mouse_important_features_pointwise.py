"""
Pointwise Model Training Pipeline for Likert Score Prediction
Uses Mouse-Only Important Features Dataset

This script trains a Random Forest Regressor to predict likert_1 (1-5 scale)
using cross-validation for evaluation.
"""

import pandas as pd
import numpy as np
import warnings
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate, KFold
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score
)
from scipy.stats import spearmanr, pearsonr
from utils.kfold_debug import print_fold_1_first_row

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Random states for reproducibility
    'RANDOM_STATE': 49,
    'RANDOM_SEED': 49,

    # Data paths
    'INPUT_CSV': 'pointwise_output/mouse_important_features_pointwise.csv',

    # Cross-validation settings
    'CV_FOLDS': 5,
    'CV_SCORING': ['neg_mean_squared_error', 'neg_mean_absolute_error', 'r2'],

    # Random Forest hyperparameters
    'RF_PARAMS': {
        'n_estimators': 100,
        'max_depth': 7,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'max_features': 'sqrt',
        'random_state': 49,
        'n_jobs': -1
    },
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def set_random_seeds(seed):
    """Set all random seeds for reproducibility"""
    np.random.seed(seed)

def load_and_prepare_data(filepath):
    """Load CSV and prepare features and target"""
    print("\n" + "="*80)
    print("POINTWISE MODEL - MOUSE IMPORTANT FEATURES (Random Forest Regressor)")
    print("="*80)

    # Load data
    df = pd.read_csv(filepath)
    print(f"Loaded data shape: {df.shape}")

    # Text columns to exclude
    text_columns = ['user_query', 'llm_response_1']

    # Non-feature columns to exclude (text + identifiers)
    excluded_columns = text_columns + ['user_id', 'query_id', 'domain', 'preference']

    # Target column
    target_column = 'likert_1'

    # Drop rows with null target
    null_target = df[target_column].isnull().sum()
    if null_target > 0:
        print(f"Dropping {null_target} rows with null target")
        df = df.dropna(subset=[target_column])

    print(f"Final data shape: {df.shape}")

    # Prepare features: exclude text columns and target
    feature_cols = [col for col in df.columns
                   if col not in excluded_columns and col != target_column]

    X = df[feature_cols].copy()
    y = df[target_column].copy()

    print(f"Samples: {len(X)} | Features: {X.shape[1]}")
    # print(f"Feature columns: {feature_cols}")
    print(f"Target distribution:\n{y.value_counts().sort_index()}")

    return X, y

def calculate_correlation_metrics(y_true, y_pred):
    """Calculate Spearman and Pearson correlation coefficients"""
    spearman_corr, spearman_p = spearmanr(y_true, y_pred)
    pearson_corr, pearson_p = pearsonr(y_true, y_pred)

    return {
        'spearman': spearman_corr,
        'spearman_pvalue': spearman_p,
        'pearson': pearson_corr,
        'pearson_pvalue': pearson_p
    }

def train_and_evaluate_model(X, y, config):
    """
    Train Random Forest Regressor with cross-validation
    """
    print("\n" + "-"*80)
    print("Training Model")
    print("-"*80)

    # Initialize model
    rf = RandomForestRegressor(**config['RF_PARAMS'])

    # Cross-validation
    cv = KFold(n_splits=config['CV_FOLDS'], shuffle=True, random_state=config['RANDOM_STATE'])

    # Debug: Print fold 1 first row
    for fold_num, (train_idx, test_idx) in enumerate(cv.split(X, y), 1):
        if fold_num == 1:
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            print_fold_1_first_row(X_train, y_train, X_test, y_test, fold_num, train_idx, test_idx)
            break

    # Perform cross-validation
    cv_results = cross_validate(
        rf, X, y,
        cv=cv,
        scoring=config['CV_SCORING'],
        return_train_score=True,
        n_jobs=-1
    )

    # Print cross-validation results
    print("\nCross-Validation Results:")
    for metric in config['CV_SCORING']:
        train_scores = cv_results[f'train_{metric}']
        test_scores = cv_results[f'test_{metric}']

        # Convert negative scores back to positive for display
        if metric.startswith('neg_'):
            train_scores = -train_scores
            test_scores = -test_scores
            display_metric = metric.replace('neg_', '')
        else:
            display_metric = metric

        print(f"{display_metric:20s} - Train: {train_scores.mean():.4f} (+/- {train_scores.std():.4f}) | "
              f"Test: {test_scores.mean():.4f} (+/- {test_scores.std():.4f})")

    # Train final model on all data
    print("\n" + "-"*80)
    print("Training Final Model on Full Dataset")
    print("-"*80)
    rf.fit(X, y)

    # Make predictions on full dataset for correlation metrics
    y_pred = rf.predict(X)

    # Calculate correlation metrics
    corr_metrics = calculate_correlation_metrics(y, y_pred)
    print("\nCorrelation Metrics (Full Dataset):")
    print(f"  Spearman: {corr_metrics['spearman']:.4f} (p-value: {corr_metrics['spearman_pvalue']:.4e})")
    print(f"  Pearson:  {corr_metrics['pearson']:.4f} (p-value: {corr_metrics['pearson_pvalue']:.4e})")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    # Save feature importance to CSV
    import os
    output_dir = 'feature_importance'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/importance_mouse_important_features_pointwise.csv'
    feature_importance.to_csv(output_file, index=False)
    print(f"\nFeature importance saved to: {output_file}")

    # Categorize features by importance
    threshold = 0.05
    important = feature_importance[feature_importance['importance'] >= threshold]
    not_important = feature_importance[feature_importance['importance'] < threshold]

    print(f"\nImportant Features (>={threshold*100}% importance):")
    if len(important) > 0:
        print(important.to_string(index=False))
    else:
        print("  None")

    print(f"\nNot Important Features (<{threshold*100}% importance):")
    if len(not_important) > 0:
        print(not_important.to_string(index=False))
    else:
        print("  None")

    return rf

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""

    # Set random seeds
    set_random_seeds(CONFIG['RANDOM_SEED'])

    # Load and prepare data
    X, y = load_and_prepare_data(CONFIG['INPUT_CSV'])

    # Train and evaluate model
    model = train_and_evaluate_model(X, y, CONFIG)

    print("\n" + "="*80)
    print("POINTWISE MODEL (MOUSE IMPORTANT FEATURES) TRAINING COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

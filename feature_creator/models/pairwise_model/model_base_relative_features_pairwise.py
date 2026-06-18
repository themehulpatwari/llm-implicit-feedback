"""
Pairwise Model Training Pipeline for Binary Preference Prediction
Dataset: base+relative_features (includes relative/comparison features with diff_* and ratio_*)

This script trains a Random Forest Classifier to predict binary_preference (0 vs 1)
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

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, KFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)
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
    'INPUT_CSV': 'pairwise_output/base+relative_features_pairwise.csv',
    
    # Feature engineering options
    'INCLUDE_WINDOW_FEATURES': True,      # Include 200 window diff features (diff_gaze_window_*, diff_mouse_window_*)
    
    # Cross-validation settings
    'CV_FOLDS': 5,
    'CV_SCORING': ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
    
    # Random Forest hyperparameters (tuned for larger feature set)
    'RF_PARAMS': {
        'n_estimators': 200,        # More trees for complex features
        'max_depth': 15,            # Deeper trees to capture interactions
        'min_samples_split': 10,    # Higher to prevent overfitting
        'min_samples_leaf': 4,      # Higher to prevent overfitting
        'max_features': 'sqrt',     # Good default for high-dim data
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
    
def load_and_prepare_data(filepath, config):
    """Load CSV and prepare features and target"""
    print("\n" + "="*80)
    print("PAIRWISE MODEL (Random Forest Classifier)")
    print("Dataset: base+relative_features")
    print("="*80)
    
    # Load data
    df = pd.read_csv(filepath)
    print(f"Loaded data shape: {df.shape}")
    
    # Text columns to exclude
    text_columns = ['user_query', 'llm_response_1', 'llm_response_2', 'query_id', 'domain']
    
    # Target column
    target_column = 'binary_preference'
    
    # Drop rows with null target
    null_target = df[target_column].isnull().sum()
    if null_target > 0:
        print(f"Dropping {null_target} rows with null target")
        df = df.dropna(subset=[target_column])
    
    print(f"Final data shape: {df.shape}")
    
    # Prepare features: exclude text columns and target
    feature_cols = [col for col in df.columns 
                   if col not in text_columns and col != target_column]
    
    # Optionally exclude window features
    if not config['INCLUDE_WINDOW_FEATURES']:
        window_cols = [col for col in feature_cols if '_window_' in col]
        feature_cols = [col for col in feature_cols if col not in window_cols]
        print(f"Excluded {len(window_cols)} window features")
    
    X = df[feature_cols].copy()
    y = df[target_column].copy()
    
    # Handle any remaining NaN values in features
    X = X.fillna(0)
    
    print(f"Samples: {len(X)} | Features: {X.shape[1]}")
    print(f"Target distribution:\n{y.value_counts().sort_index()}")
    
    return X, y

def train_and_evaluate_model(X, y, config):
    """
    Train Random Forest Classifier with cross-validation
    """
    print("\n" + "-"*80)
    print("Training Model")
    print("-"*80)
    
    # Initialize model
    rf = RandomForestClassifier(**config['RF_PARAMS'])
    
    # Cross-validation with stratified folds
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
    
    # Print results
    print("\nCross-Validation Results:")
    for metric in config['CV_SCORING']:
        train_scores = cv_results[f'train_{metric}']
        test_scores = cv_results[f'test_{metric}']
        print(f"{metric:12s} - Train: {train_scores.mean():.4f} (+/- {train_scores.std():.4f}) | "
              f"Test: {test_scores.mean():.4f} (+/- {test_scores.std():.4f})")
    
    # Train final model on all data
    print("\n" + "-"*80)
    print("Training Final Model on Full Dataset")
    print("-"*80)
    rf.fit(X, y)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Save feature importance to CSV
    import os
    output_dir = 'feature_importance'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/importance_base_relative_features_pairwise.csv'
    feature_importance.to_csv(output_file, index=False)
    print(f"\nFeature importance saved to: {output_file}")
    
    # Categorize features by importance
    threshold = 0.05  # Features with >5% importance are considered important
    important = feature_importance[feature_importance['importance'] >= threshold]
    not_important = feature_importance[feature_importance['importance'] < threshold]
    
    print(f"\nImportant Features (>={threshold*100}% importance):")
    if len(important) > 0:
        print(important.to_string(index=False))
    else:
        print("  None")
    
    print(f"\nNot Important Features (<{threshold*100}% importance):")
    if len(not_important) > 0:
        print(f"  {len(not_important)} features with importance < {threshold}")
    else:
        print("  None")
    
    return rf

def generate_oof_labels(X, y, df_original, config, output_filename):
    """
    Generate out-of-fold (OOF) predictions and confidence scores.
    Each sample is predicted exactly once (when it is in the test fold).
    Saves the original dataframe augmented with 'oof_prediction' and
    'oof_confidence' (P(class=1)) columns to pairwise_labeled_output/.
    """
    print("\n" + "-"*80)
    print("Generating Out-of-Fold (OOF) Labels")
    print("-"*80)

    n_samples = len(X)
    oof_predictions = np.full(n_samples, np.nan)
    oof_confidence  = np.full(n_samples, np.nan)

    cv = KFold(n_splits=config['CV_FOLDS'], shuffle=True, random_state=config['RANDOM_STATE'])

    for fold_num, (train_idx, test_idx) in enumerate(cv.split(X, y), 1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train         = y.iloc[train_idx]

        rf_fold = RandomForestClassifier(**config['RF_PARAMS'])
        rf_fold.fit(X_train, y_train)

        preds   = rf_fold.predict(X_test)
        probas  = rf_fold.predict_proba(X_test)[:, 1]  # P(class=1)

        oof_predictions[test_idx] = preds
        oof_confidence[test_idx]  = probas
        print(f"  Fold {fold_num}: predicted {len(test_idx)} samples")

    # Attach OOF columns to the original dataframe
    df_out = df_original.copy()
    df_out['oof_prediction'] = oof_predictions
    df_out['oof_confidence'] = oof_confidence

    # Save
    output_dir = 'pairwise_labeled_output'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    df_out.to_csv(output_path, index=False)
    print(f"\nOOF-labeled CSV saved to: {output_path}")
    print(f"  Total rows: {len(df_out)} | NaN predictions: {np.isnan(oof_predictions).sum()}")

    return df_out

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""
    
    # Set random seeds
    set_random_seeds(CONFIG['RANDOM_SEED'])
    
    # Load and prepare data
    X, y = load_and_prepare_data(CONFIG['INPUT_CSV'], CONFIG)

    # Load original dataframe (for augmented output)
    df_original = pd.read_csv(CONFIG['INPUT_CSV'])
    df_original = df_original.dropna(subset=['binary_preference'])
    
    # Train and evaluate model
    model = train_and_evaluate_model(X, y, CONFIG)

    # Generate OOF labels
    generate_oof_labels(X, y, df_original, CONFIG, 'base_relative_features_pairwise_labeled.csv')
    
    print("\n" + "="*80)
    print("PAIRWISE MODEL TRAINING COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

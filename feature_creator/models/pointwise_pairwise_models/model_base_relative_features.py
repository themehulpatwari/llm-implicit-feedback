"""
Model Training Pipeline for LLM Preference Prediction
Dataset: base+relative_features.csv (derived comparison features)

PAIRWISE ONLY - This dataset contains only relative/comparison features,
so pointwise model is skipped (no comparisons possible with single response).

This script trains:
1. Pairwise: Random Forest Classifier to predict preference (1 vs 2)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Random states for reproducibility
    'RANDOM_STATE': 49,
    'RANDOM_SEED': 49,
    
    # Data paths
    'INPUT_CSV': 'output/base+relative_features.csv',
    
    # Feature engineering options
    'INCLUDE_TASK_ID': True,              # Include task_id as numeric feature
    'INCLUDE_WINDOW_FEATURES': False,      # Include 200 window diff features
    
    # Cross-validation settings
    'CV_FOLDS': 5,
    'CV_SCORING_PAIRWISE': ['accuracy', 'precision', 'recall', 'f1'],
    
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
    
def load_and_clean_data(filepath):
    """Load CSV and basic cleaning"""
    df = pd.read_csv(filepath)
    return df

def prepare_pairwise_data(df, config):
    """
    Prepare pairwise comparison data for preference prediction
    
    Target: preference (1 or 2)
    Features: llm_1_*, llm_2_*, adjustment, task_id, all relative features (diff_*, ratio_*)
    """
    print("\n" + "="*80)
    print("PAIRWISE MODEL (Random Forest Classifier)")
    print("="*80)
    
    # Filter pairwise rows
    pairwise = df[df['comparison_type'] == 'pairwise'].copy()
    
    # Drop rows with null preference (target)
    null_preference = pairwise['preference'].isnull().sum()
    pairwise = pairwise.dropna(subset=['preference'])
    
    print(f"Final pairwise shape: {pairwise.shape}")
    
    # Select base features
    feature_cols = ['adjustment']
    
    # Add task_id if enabled
    if config['INCLUDE_TASK_ID']:
        feature_cols.append('task_id')
    
    # Add LLM one-hot columns
    llm_cols = [col for col in pairwise.columns if col.startswith('llm_1_') or col.startswith('llm_2_')]
    feature_cols.extend(llm_cols)
    
    # Add all relative features (exclude metadata and target columns)
    excluded_cols = [
        'comparison_type', 'query_id', 'user_id', 'task_id', 'user_query',
        'llm_response_1', 'llm_response_2', 'likert_1', 'likert_2', 
        'preference', 'adjustment', 'query_timestamp'
    ]
    excluded_cols.extend(llm_cols)  # Already added
    
    # Get all relative feature columns
    relative_cols = []
    for col in pairwise.columns:
        if col not in excluded_cols and col not in feature_cols:
            # Optionally exclude window difference features
            if not config['INCLUDE_WINDOW_FEATURES']:
                if '_window_' in col:
                    continue
            relative_cols.append(col)
    
    feature_cols.extend(relative_cols)
    
    # Create feature matrix
    X = pairwise[feature_cols].copy()
    
    # Handle any remaining NaN values in features
    X = X.fillna(0)
    
    # Target variable (convert to 0 and 1 for sklearn)
    y = pairwise['preference'].copy()
    y = (y == 2).astype(int)  # Convert: 1 -> 0, 2 -> 1
    
    print(f"Samples: {len(X)} | Features: {X.shape[1]}")
    
    return X, y

def train_pairwise_model(X, y, config):
    """
    Train Random Forest Classifier for pairwise preference prediction
    Uses cross-validation for evaluation
    """
    # Initialize model
    rf = RandomForestClassifier(**config['RF_PARAMS'])
    
    # Cross-validation with stratified folds
    cv = KFold(n_splits=config['CV_FOLDS'], shuffle=True, random_state=config['RANDOM_STATE'])
    
    # Perform cross-validation
    cv_results = cross_validate(
        rf, X, y, 
        cv=cv,
        scoring=config['CV_SCORING_PAIRWISE'],
        return_train_score=True,
        n_jobs=-1
    )
    
    # Print results
    print("\nResults:")
    for metric in config['CV_SCORING_PAIRWISE']:
        train_scores = cv_results[f'train_{metric}']
        test_scores = cv_results[f'test_{metric}']
        print(f"  {metric.upper()}: Train {train_scores.mean():.4f} | Test {test_scores.mean():.4f} (+/- {test_scores.std():.4f})")
    
    # Train final model on all data
    rf.fit(X, y)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
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
        print(not_important.to_string(index=False))
    else:
        print("  None")
    
    return rf, cv_results, feature_importance

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""
    
    # Set random seeds
    set_random_seeds(CONFIG['RANDOM_SEED'])
    
    # Load data
    df = load_and_clean_data(CONFIG['INPUT_CSV'])
    
    # ========================================================================
    # PAIRWISE MODEL: Predict preference (1 vs 2)
    # ========================================================================
    X_pairwise, y_pairwise = prepare_pairwise_data(df, CONFIG)
    rf_model, rf_cv_results, rf_importance = train_pairwise_model(X_pairwise, y_pairwise, CONFIG)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("TRAINING COMPLETE (PAIRWISE ONLY)")
    print("="*80)
    print("Note: Pointwise model skipped - relative features require comparisons")

if __name__ == "__main__":
    main()

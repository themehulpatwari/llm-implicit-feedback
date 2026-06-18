"""
Model Training Pipeline for LLM Preference and Likert Prediction
Dataset: base+extracted_features.csv (includes eye-tracking and mouse features)

This script trains two types of models:
1. Pairwise: Random Forest Classifier to predict preference (1 vs 2)
2. Pointwise: Ridge Classifier/Regressor to predict likert_1 (1-5 scale)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import RidgeClassifier, Ridge
from sklearn.model_selection import cross_validate, KFold, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
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
    'INPUT_CSV': 'output/base+extracted_features.csv',
    
    # Feature engineering options
    'INCLUDE_TASK_ID': True,              # Include task_id as numeric feature
    'INCLUDE_WINDOW_FEATURES': True,      # Include 200 window features (gaze/mouse_window_000-099)
    'NORMALIZE_FEATURES': True,           # StandardScaler for Ridge (RF doesn't need it)
    
    # Cross-validation settings
    'CV_FOLDS': 5,
    'CV_SCORING_PAIRWISE': ['accuracy', 'precision', 'recall', 'f1'],
    'CV_SCORING_POINTWISE': ['neg_mean_squared_error', 'neg_mean_absolute_error', 'r2'],
    
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
    
    # Ridge hyperparameters (stronger regularization for high-dim data)
    'RIDGE_PARAMS': {
        'alpha': 10.0,              # Stronger regularization
        'random_state': 49,
        'max_iter': 2000            # More iterations for convergence
    },
    
    # Model choice for pointwise: 'classifier' or 'regressor'
    'POINTWISE_MODEL_TYPE': 'regressor',
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
    Features: llm_1_*, llm_2_*, adjustment, task_id, all extracted features (NO likert values!)
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
    
    # Add all extracted features (exclude metadata and target columns)
    excluded_cols = [
        'comparison_type', 'query_id', 'user_id', 'task_id', 'user_query',
        'llm_response_1', 'llm_response_2', 'likert_1', 'likert_2', 
        'preference', 'adjustment', 'query_timestamp',
        'normalized_likert_1', 'normalized_likert_2', 'binary_preference'
    ]
    excluded_cols.extend(llm_cols)  # Already added
    
    # Get all extracted feature columns
    extracted_cols = []
    for col in pairwise.columns:
        if col not in excluded_cols and col not in feature_cols:
            # Optionally exclude window features
            if not config['INCLUDE_WINDOW_FEATURES']:
                if '_window_' in col:
                    continue
            extracted_cols.append(col)
    
    feature_cols.extend(extracted_cols)
    
    # Create feature matrix
    X = pairwise[feature_cols].copy()
    
    # Handle any remaining NaN values in features
    X = X.fillna(0)
    
    # Target variable (convert to 0 and 1 for sklearn)
    y = pairwise['preference'].copy()
    y = (y == 2).astype(int)  # Convert: 1 -> 0, 2 -> 1
    
    print(f"Samples: {len(X)} | Features: {X.shape[1]}")
    
    return X, y

def prepare_pointwise_data(df, config):
    """
    Prepare pointwise data for likert_1 prediction
    
    Target: likert_1 (1-5)
    Features: llm_1_*, adjustment, task_id, only response_A features (NO response_B)
    """
    print("\n" + "="*80)
    print(f"POINTWISE MODEL (Ridge {config['POINTWISE_MODEL_TYPE'].capitalize()})")
    print("="*80)
    
    # Filter pointwise rows
    pointwise = df[df['comparison_type'] == 'pointwise'].copy()
    
    # Drop rows with null likert_1 (target)
    null_likert = pointwise['likert_1'].isnull().sum()
    pointwise = pointwise.dropna(subset=['likert_1'])
    
    print(f"Final pointwise shape: {pointwise.shape}")
    
    # Select base features
    feature_cols = ['adjustment']
    
    # Add task_id if enabled
    if config['INCLUDE_TASK_ID']:
        feature_cols.append('task_id')
    
    # Add LLM one-hot columns (only llm_1_*, no llm_2_*)
    llm_cols = [col for col in pointwise.columns if col.startswith('llm_1_')]
    feature_cols.extend(llm_cols)
    
    # Add extracted features (ONLY response_A features, exclude response_B)
    excluded_cols = [
        'comparison_type', 'query_id', 'user_id', 'task_id', 'user_query',
        'llm_response_1', 'llm_response_2', 'likert_1', 'likert_2', 
        'preference', 'adjustment', 'query_timestamp',
        'normalized_likert_1', 'normalized_likert_2', 'binary_preference'
    ]
    excluded_cols.extend(llm_cols)  # Already added
    
    # Get response_A features only (exclude response_B and comparison features)
    extracted_cols = []
    for col in pointwise.columns:
        if col not in excluded_cols and col not in feature_cols:
            # Exclude response_B features
            if 'response_B' in col or 'response_b' in col:
                continue
            # Exclude comparison features (they compare A vs B)
            if 'comparison_' in col or '_left_' in col or '_right_' in col:
                continue
            # Optionally exclude window features
            if not config['INCLUDE_WINDOW_FEATURES']:
                if '_window_' in col:
                    continue
            extracted_cols.append(col)
    
    feature_cols.extend(extracted_cols)
    
    # Create feature matrix
    X = pointwise[feature_cols].copy()
    
    # Handle any remaining NaN values in features
    X = X.fillna(0)
    
    # Target variable
    y = pointwise['likert_1'].copy()
    
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

def train_pointwise_model(X, y, config):
    """
    Train Ridge Classifier/Regressor for pointwise likert_1 prediction
    Uses cross-validation for evaluation
    """
    # Normalize features (Ridge requires scaling)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    # Initialize model
    if config['POINTWISE_MODEL_TYPE'] == 'classifier':
        model = RidgeClassifier(**config['RIDGE_PARAMS'])
        cv = KFold(n_splits=config['CV_FOLDS'], shuffle=True, random_state=config['RANDOM_STATE'])
        scoring = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
    else:  # regressor
        model = Ridge(**config['RIDGE_PARAMS'])
        cv = KFold(n_splits=config['CV_FOLDS'], shuffle=True, random_state=config['RANDOM_STATE'])
        scoring = config['CV_SCORING_POINTWISE']
    
    # Perform cross-validation
    cv_results = cross_validate(
        model, X_scaled, y,
        cv=cv,
        scoring=scoring,
        return_train_score=True,
        n_jobs=-1
    )
    
    # Print results
    print("\nResults:")
    for metric in scoring:
        train_scores = cv_results[f'train_{metric}']
        test_scores = cv_results[f'test_{metric}']
        print(f"  {metric.upper()}: Train {train_scores.mean():.4f} | Test {test_scores.mean():.4f} (+/- {test_scores.std():.4f})")
    
    # Train final model on all data
    model.fit(X_scaled, y)
    
    # Coefficient analysis
    if hasattr(model, 'coef_'):
        if config['POINTWISE_MODEL_TYPE'] == 'classifier':
            coefs = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
        else:
            coefs = model.coef_
            
        coefficients = pd.DataFrame({
            'feature': X.columns,
            'coefficient': np.abs(coefs),  # Use absolute values for importance
            'raw_coefficient': coefs
        }).sort_values('coefficient', ascending=False)
        
        # Categorize features by coefficient magnitude
        threshold = 0.1  # Features with |coefficient| >= 0.1 are important
        important = coefficients[coefficients['coefficient'] >= threshold]
        not_important = coefficients[coefficients['coefficient'] < threshold]
        
        print(f"\nImportant Features (|coef| >={threshold}):")
        if len(important) > 0:
            print(important[['feature', 'raw_coefficient']].to_string(index=False))
        else:
            print("  None")
        
        print(f"\nNot Important Features (|coef| <{threshold}):")
        if len(not_important) > 0:
            print(not_important[['feature', 'raw_coefficient']].to_string(index=False))
        else:
            print("  None")
    
    return model, scaler, cv_results

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
    # POINTWISE MODEL: Predict likert_1 (1-5)
    # ========================================================================
    X_pointwise, y_pointwise = prepare_pointwise_data(df, CONFIG)
    ridge_model, ridge_scaler, ridge_cv_results = train_pointwise_model(X_pointwise, y_pointwise, CONFIG)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

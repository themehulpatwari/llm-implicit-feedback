"""
K-Fold Cross-Validation Debug Utilities

This module provides helper functions for debugging K-fold cross-validation,
specifically for printing the first row of training and test data from fold 1.
"""

import pandas as pd
import numpy as np


def print_fold_1_first_row(X_train, y_train, X_test, y_test, fold_num, train_idx=None, test_idx=None):
    """
    Print the first row of training and test data for fold 1.
    
    Parameters:
    -----------
    X_train : pd.DataFrame or np.ndarray
        Training features
    y_train : pd.Series or np.ndarray
        Training target
    X_test : pd.DataFrame or np.ndarray
        Test features
    y_test : pd.Series or np.ndarray
        Test target
    fold_num : int
        Current fold number (1-indexed)
    train_idx : np.ndarray, optional
        Training indices
    test_idx : np.ndarray, optional
        Test indices
    """
    if fold_num != 1:
        return
    
    print("\n" + "="*80)
    print(" FOLD 1 - DEBUG INFO")
    print("="*80)
    
    # Print train/test indices info
    if train_idx is not None:
        print(f"\n--- INDICES INFO ---")
        print(f"Train indices ({len(train_idx)} samples):")
        print(f"  {train_idx}")
        print(f"\nTest indices ({len(test_idx)} samples):")
        print(f"  {test_idx}")
    
    # # Convert to DataFrame/Series if needed for easier printing
    # if isinstance(X_train, np.ndarray):
    #     X_train_first = X_train[0]
    #     feature_names = [f"feature_{i}" for i in range(len(X_train_first))]
    # else:
    #     X_train_first = X_train.iloc[0]
    #     feature_names = X_train.columns
    # 
    # if isinstance(X_test, np.ndarray):
    #     X_test_first = X_test[0]
    # else:
    #     X_test_first = X_test.iloc[0]
    # 
    # # Get target values
    # if isinstance(y_train, np.ndarray):
    #     y_train_first = y_train[0]
    # else:
    #     y_train_first = y_train.iloc[0]
    # 
    # if isinstance(y_test, np.ndarray):
    #     y_test_first = y_test[0]
    # else:
    #     y_test_first = y_test.iloc[0]
    # 
    # # Print training set first row
    # print("\n--- TRAINING SET (First Row) ---")
    # print(f"Target Value: {y_train_first}")
    # print("Features:")
    # if isinstance(X_train, pd.DataFrame):
    #     for col, val in X_train_first.items():
    #         print(f"  {col}: {val}")
    # else:
    #     for i, (fname, val) in enumerate(zip(feature_names, X_train_first)):
    #         print(f"  {fname}: {val}")
    # 
    # # Print test set first row
    # print("\n--- TEST SET (First Row) ---")
    # print(f"Target Value: {y_test_first}")
    # print("Features:")
    # if isinstance(X_test, pd.DataFrame):
    #     for col, val in X_test_first.items():
    #         print(f"  {col}: {val}")
    # else:
    #     for i, (fname, val) in enumerate(zip(feature_names, X_test_first)):
    #         print(f"  {fname}: {val}")
    
    print("\n" + "="*80 + "\n")

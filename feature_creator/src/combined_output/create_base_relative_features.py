import pandas as pd
import numpy as np
from pathlib import Path


class FeatureEngineer:
    
    BASE_FEATURES = [
        "gaze_focused_engagement_ratio",
        "gaze_overall_attention_ratio",
        "mouse_focused_engagement_ratio",
        "mouse_overall_attention_ratio",
        "gaze_normalized_avg_char_position",
        "gaze_reading_completion_ratio",
        "gaze_normalized_char_position_variance",
        "mouse_normalized_avg_char_position",
        "mouse_reading_completion_ratio",
        "mouse_normalized_char_position_variance",
        "response_length",
        "gaze_data_points",
        "mouse_data_points"
    ]
    
    RATIO_FEATURES = [
        "gaze_focused_engagement_ratio",
        "gaze_overall_attention_ratio",
        "mouse_focused_engagement_ratio",
        "mouse_overall_attention_ratio",
        "gaze_reading_completion_ratio",
        "mouse_reading_completion_ratio",
        "response_length",
        "gaze_data_points",
        "mouse_data_points",
        "gaze_normalized_char_position_variance"
    ]
    
    @staticmethod
    def safe_divide(numerator, denominator, default=1.0):
        result = np.where(
            (np.abs(denominator) < 1e-10) | np.isnan(denominator) | np.isnan(numerator),
            default,
            numerator / denominator
        )
        return result
    
    @staticmethod
    def create_basic_differences(df):
        diff_features = pd.DataFrame()
        
        for feature in FeatureEngineer.BASE_FEATURES:
            col_a = f"response_A_{feature}"
            col_b = f"response_B_{feature}"
            
            if col_a in df.columns and col_b in df.columns:
                diff_features[f"diff_{feature}"] = df[col_a] - df[col_b]
        
        return diff_features
    
    @staticmethod
    def create_basic_ratios(df):
        ratio_features = pd.DataFrame()
        
        for feature in FeatureEngineer.RATIO_FEATURES:
            col_a = f"response_A_{feature}"
            col_b = f"response_B_{feature}"
            
            if col_a in df.columns and col_b in df.columns:
                clean_name = feature.replace("_ratio", "").replace(
                    "gaze_normalized_char_position_variance",
                    "char_position_variance_gaze"
                )
                
                ratio_features[f"ratio_{clean_name}"] = FeatureEngineer.safe_divide(
                    df[col_a].values,
                    df[col_b].values,
                    default=1.0
                )
        
        return ratio_features
    
    @staticmethod
    def create_window_differences(df, num_windows=100):
        window_diff = pd.DataFrame()
        
        for i in range(num_windows):
            window_name = f"gaze_window_{i:03d}"
            col_a = f"response_A_{window_name}"
            col_b = f"response_B_{window_name}"
            
            if col_a in df.columns and col_b in df.columns:
                window_diff[f"diff_{window_name}"] = df[col_a] - df[col_b]
        
        for i in range(num_windows):
            window_name = f"mouse_window_{i:03d}"
            col_a = f"response_A_{window_name}"
            col_b = f"response_B_{window_name}"
            
            if col_a in df.columns and col_b in df.columns:
                window_diff[f"diff_{window_name}"] = df[col_a] - df[col_b]
        
        return window_diff
    
    @staticmethod
    def create_aggregated_window_stats(window_diff, num_windows=100):
        agg_features = pd.DataFrame()
        
        gaze_diff_cols = [f"diff_gaze_window_{i:03d}" for i in range(num_windows)]
        gaze_diff_cols = [c for c in gaze_diff_cols if c in window_diff.columns]
        
        if gaze_diff_cols:
            gaze_diffs = window_diff[gaze_diff_cols]
            agg_features['diff_gaze_window_mean'] = gaze_diffs.mean(axis=1)
            agg_features['diff_gaze_window_std'] = gaze_diffs.std(axis=1)
            agg_features['diff_gaze_window_max'] = gaze_diffs.max(axis=1)
            agg_features['diff_gaze_window_min'] = gaze_diffs.min(axis=1)
        
        mouse_diff_cols = [f"diff_mouse_window_{i:03d}" for i in range(num_windows)]
        mouse_diff_cols = [c for c in mouse_diff_cols if c in window_diff.columns]
        
        if mouse_diff_cols:
            mouse_diffs = window_diff[mouse_diff_cols]
            agg_features['diff_mouse_window_mean'] = mouse_diffs.mean(axis=1)
            agg_features['diff_mouse_window_std'] = mouse_diffs.std(axis=1)
            agg_features['diff_mouse_window_max'] = mouse_diffs.max(axis=1)
            agg_features['diff_mouse_window_min'] = mouse_diffs.min(axis=1)
        
        return agg_features


def main():
    print("=" * 70)
    print("Creating Base + Relative Features")
    print("=" * 70)
    
    base_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base.csv'
    base_df = pd.read_csv(base_path)
    print(f"\nBase CSV shape: {base_df.shape}")
    
    extracted_path = Path(__file__).resolve().parent.parent.parent / 'input' / 'extracted_features.csv'
    extracted_df = pd.read_csv(extracted_path)
    print(f"Extracted features CSV shape: {extracted_df.shape}")
    
    print("\n1. Creating basic difference features...")
    diff_features = FeatureEngineer.create_basic_differences(extracted_df)
    print(f"   Added {len(diff_features.columns)} difference features")
    
    print("\n2. Creating basic ratio features...")
    ratio_features = FeatureEngineer.create_basic_ratios(extracted_df)
    print(f"   Added {len(ratio_features.columns)} ratio features")
    
    print("\n3. Creating window difference features...")
    window_diff = FeatureEngineer.create_window_differences(extracted_df)
    print(f"   Added {len(window_diff.columns)} window difference features")
    
    print("\n4. Creating aggregated window statistics...")
    agg_stats = FeatureEngineer.create_aggregated_window_stats(window_diff)
    print(f"   Added {len(agg_stats.columns)} aggregated statistics")
    
    print("\n5. Extracting aggregate behavioral features...")
    # Get all non-response-specific features (these are aggregate features we want to keep)
    # Exclude metadata columns that are already in base.csv
    metadata_cols = ['comparison_type', 'task_id', 'user_query', 'llm_name_1', 'llm_name_2', 
                     'llm_response_1', 'llm_response_2', 'likert_1', 'likert_2', 'preference',
                     'normalized_likert_1', 'normalized_likert_2', 'binary_preference']
    
    aggregate_feature_cols = [col for col in extracted_df.columns 
                              if not col.startswith('response_A_') 
                              and not col.startswith('response_B_')
                              and col not in metadata_cols
                              and col not in ['query_id', 'user_id']]
    
    aggregate_features = extracted_df[aggregate_feature_cols]
    print(f"   Keeping {len(aggregate_features.columns)} aggregate behavioral features")
    
    print("\n6. Combining all features...")
    relative_features = pd.concat([
        extracted_df[['query_id', 'user_id']],
        diff_features,
        ratio_features,
        window_diff,
        agg_stats,
        aggregate_features
    ], axis=1)
    
    print(f"   Total relative features created: {len(relative_features.columns) - 2}")
    
    print("\n7. Merging with base...")
    base_df_renamed = base_df.rename(columns={'query_ID': 'query_id'})
    
    merged_df = base_df_renamed.merge(
        relative_features,
        on=['query_id', 'user_id'],
        how='inner'
    )
    
    print(f"   Merged shape: {merged_df.shape}")
    
    output_path = Path(__file__).resolve().parent.parent.parent / 'output' / 'base+relative_features.csv'
    merged_df.to_csv(output_path, index=False)
    
    print(f"\n8. Saved to: {output_path}")
    print(f"   Final shape: {merged_df.shape}")
    
    print("\n" + "=" * 70)
    print("Base + Relative Features created successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()

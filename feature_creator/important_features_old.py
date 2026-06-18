COMPARE_POINTWISE_IMPORTANT_FEATURES = [
    'adjustment',
    'llm_1_claude-3-5-sonnet-20240620',
    'llm_1_claude-sonnet-4-5-20250929',
    'llm_1_deepseek-ai/DeepSeek-V3',
    'llm_1_gpt-4o-mini',
    'llm_1_meta-llama/Llama-3.3-70B-Instruct-Turbo',
    'llm_2_claude-3-5-sonnet-20240620',
    'llm_2_claude-sonnet-4-5-20250929',
    'llm_2_deepseek-ai/DeepSeek-V3',
    'llm_2_gpt-4o-mini',
    'llm_2_meta-llama/Llama-3.3-70B-Instruct-Turbo',
    'max_idx_left',
    'max_idx_right',
    'query_length_right',
    'response_left',
    'response_right',
    'total_entries_left',
    'total_entries_right',
    'cross_modality_left_reviewing_duration_ratio_gaze_mouse', # Both
    'gaze_comparison_reviewing_time_ratio', # Gaze
    'gaze_left_reviewing_offscreen_ratio', # Gaze
    'gaze_left_reviewing_engaged_time_s', # Gaze
    'gaze_right_reviewing_active_ratio', # Gaze
    'gaze_right_reviewing_offscreen_ratio', # Gaze
    'mouse_comparison_reviewing_activity_ratio', # Mouse
    'gaze_comparison_reviewing_activity_diff' # Gaze
    'mouse_comparison_reviewing_time_ratio', # Mouse
    'mouse_left_reviewing_active_ratio', # Mouse
    'mouse_right_reviewing_offscreen_ratio', # Mouse
    'response_A_gaze_focused_engagement_ratio', # Gaze
    'response_A_gaze_overall_attention_ratio', # Gaze
    'response_A_gaze_window_006', # Gaze
    'response_A_gaze_window_007', # Gaze
    'response_A_gaze_window_008', # Gaze
    'response_A_mouse_focused_engagement_ratio', # Mouse
    'response_A_mouse_normalized_char_position_variance', # Mouse
    'response_A_mouse_overall_attention_ratio', # Mouse
    'response_A_mouse_window_000', # Mouse
    'response_A_mouse_window_099', # Mouse
    'response_B_gaze_focused_engagement_ratio', # Gaze
    'response_B_gaze_normalized_avg_char_position', # Gaze
    'response_B_gaze_overall_attention_ratio', # Gaze
    'response_B_gaze_window_000', # Gaze
    'response_B_gaze_window_006', # Gaze
    'response_B_gaze_window_014', # Gaze
    'response_B_mouse_data_points', # Mouse
    'response_B_mouse_focused_engagement_ratio', # Mouse
    'response_B_mouse_normalized_avg_char_position', # Mouse
    'response_B_mouse_overall_attention_ratio', # Mouse
    'response_B_mouse_window_022', # Mouse
    'response_B_mouse_window_031', # Mouse
    'response_B_mouse_window_033', # Mouse
    'response_B_mouse_window_037', # Mouse
    'response_B_mouse_window_039', # Mouse
    'response_B_mouse_reading_completion_ratio', # Mouse
    'response_A_mouse_reading_completion_ratio', # Mouse
]


PAIRWISE_GAZE_IMPORTANT = [
    'cross_modality_left_reviewing_duration_ratio_gaze_mouse', # Both
    'gaze_comparison_reviewing_time_ratio', # Gaze
    'gaze_left_reviewing_offscreen_ratio', # Gaze
    'gaze_left_reviewing_engaged_time_s', # Gaze
    'gaze_right_reviewing_active_ratio', # Gaze
    'gaze_right_reviewing_offscreen_ratio', # Gaze
    'gaze_comparison_reviewing_activity_diff', # Gaze
    'response_A_gaze_focused_engagement_ratio', # Gaze
    'response_A_gaze_overall_attention_ratio', # Gaze
    'response_A_gaze_window_006', # Gaze
    'response_A_gaze_window_007', # Gaze
    'response_A_gaze_window_008', # Gaze
    'response_B_gaze_focused_engagement_ratio', # Gaze
    'response_B_gaze_normalized_avg_char_position', # Gaze
    'response_B_gaze_overall_attention_ratio', # Gaze
    'response_B_gaze_window_000', # Gaze
    'response_B_gaze_window_006', # Gaze
    'response_B_gaze_window_014', # Gaze
]


PAIRWISE_MOUSE_IMPORTANT = [
    'cross_modality_left_reviewing_duration_ratio_gaze_mouse', # Both
    'mouse_comparison_reviewing_activity_ratio', # Mouse
    'mouse_comparison_reviewing_time_ratio', # Mouse
    'mouse_left_reviewing_active_ratio', # Mouse
    'mouse_right_reviewing_offscreen_ratio', # Mouse
    'response_A_mouse_focused_engagement_ratio', # Mouse
    'response_A_mouse_normalized_char_position_variance', # Mouse
    'response_A_mouse_overall_attention_ratio', # Mouse
    'response_A_mouse_window_000', # Mouse
    'response_A_mouse_window_099', # Mouse
    'response_B_mouse_data_points', # Mouse
    'response_B_mouse_focused_engagement_ratio', # Mouse
    'response_B_mouse_normalized_avg_char_position', # Mouse
    'response_B_mouse_overall_attention_ratio', # Mouse
    'response_B_mouse_window_022', # Mouse
    'response_B_mouse_window_031', # Mouse
    'response_B_mouse_window_033', # Mouse
    'response_B_mouse_window_037', # Mouse
    'response_B_mouse_window_039', # Mouse
    'response_B_mouse_reading_completion_ratio', # Mouse
    'response_A_mouse_reading_completion_ratio', # Mouse
]


POINTWISE_GAZE_IMPORTANT = [
    'cross_modality_composing_activity_ratio_gaze_mouse', # Both
    'gaze_active_time_reviewing_s', # Gaze
    'gaze_offscreen_time_composing_s', # Gaze
    'gaze_reviewing_duration_s', # Gaze
    'gaze_thinking_time_s', # Gaze
    'response_A_gaze_data_points', # Gaze
    'response_A_gaze_normalized_avg_char_position', # Gaze
    'response_A_gaze_window_001', # Gaze
    'response_A_gaze_window_004', # Gaze
    'response_A_gaze_window_006', # Gaze
    'response_A_gaze_window_007', # Gaze
    'response_A_gaze_window_009', # Gaze
    'response_A_gaze_window_010', # Gaze
    'response_A_gaze_window_014', # Gaze
    'response_A_gaze_window_016', # Gaze
    'response_A_gaze_window_018', # Gaze
    'response_A_gaze_window_019', # Gaze
    'response_A_gaze_window_023', # Gaze
    'response_A_gaze_window_026', # Gaze
    'response_A_gaze_window_038', # Gaze
    'response_A_gaze_window_061', # Gaze
    'response_A_gaze_window_067', # Gaze
    'response_A_gaze_window_068', # Gaze
    'response_A_gaze_window_069', # Gaze
    'response_A_gaze_window_071', # Gaze
    'response_A_gaze_window_073', # Gaze
    'response_A_gaze_window_075', # Gaze
    'response_A_gaze_window_092', # Gaze
]


POINTWISE_MOUSE_IMPORTANT = [
    'cross_modality_composing_activity_ratio_gaze_mouse', # Both
    'mouse_offscreen_time_composing_s', # Mouse
    'mouse_reviewing_composing_activity_ratio', # Mouse
    'response_A_mouse_normalized_char_position_variance', # Mouse
    'response_A_mouse_window_019', # Mouse
    'response_A_mouse_window_021', # Mouse
    'response_A_mouse_window_023', # Mouse
    'response_A_mouse_window_026', # Mouse
    'response_A_mouse_window_028', # Mouse
    'response_A_mouse_window_034', # Mouse
    'response_A_mouse_window_035', # Mouse
    'response_A_mouse_window_042', # Mouse
    'response_A_mouse_window_047', # Mouse
    'response_A_mouse_window_054', # Mouse
    'response_A_mouse_window_055', # Mouse
    'response_A_mouse_window_056', # Mouse
    'response_A_mouse_window_072', # Mouse
    'response_A_mouse_window_073', # Mouse
    'response_A_mouse_window_084', # Mouse
    'response_A_mouse_window_098', # Mouse
]


POINTWISE_IMPORTANT_FEATURES = [
    'adjustment',
    'llm_1_claude-3-5-sonnet-20240620',
    'llm_1_claude-sonnet-4-5-20250929',
    'llm_1_deepseek-ai/DeepSeek-V3',
    'llm_1_gpt-4o-mini',
    'llm_1_meta-llama/Llama-3.3-70B-Instruct-Turbo',
    'camera_green',
    'response_left',
    'total_entries_left',
    'cross_modality_composing_activity_ratio_gaze_mouse', # Both
    'gaze_active_time_reviewing_s', # Gaze
    'gaze_offscreen_time_composing_s', # Gaze
    'gaze_reviewing_duration_s', # Gaze
    'gaze_thinking_time_s', # Gaze
    'mouse_offscreen_time_composing_s', # Mouse
    'mouse_reviewing_composing_activity_ratio', # Mouse
    'response_A_gaze_data_points', # Gaze
    'response_A_gaze_normalized_avg_char_position', # Gaze
    'response_A_gaze_window_001', # Gaze
    'response_A_gaze_window_004', # Gaze
    'response_A_gaze_window_006', # Gaze
    'response_A_gaze_window_007', # Gaze
    'response_A_gaze_window_009', # Gaze
    'response_A_gaze_window_010', # Gaze
    'response_A_gaze_window_014', # Gaze
    'response_A_gaze_window_016', # Gaze
    'response_A_gaze_window_018', # Gaze
    'response_A_gaze_window_019', # Gaze
    'response_A_gaze_window_023', # Gaze
    'response_A_gaze_window_026', # Gaze
    'response_A_gaze_window_038', # Gaze
    'response_A_gaze_window_061', # Gaze
    'response_A_gaze_window_067', # Gaze
    'response_A_gaze_window_068', # Gaze
    'response_A_gaze_window_069', # Gaze
    'response_A_gaze_window_071', # Gaze
    'response_A_gaze_window_073', # Gaze
    'response_A_gaze_window_075', # Gaze
    'response_A_gaze_window_092', # Gaze
    'response_A_mouse_normalized_char_position_variance', # Mouse
    'response_A_mouse_window_019', # Mouse
    'response_A_mouse_window_021', # Mouse
    'response_A_mouse_window_023', # Mouse
    'response_A_mouse_window_026', # Mouse
    'response_A_mouse_window_028', # Mouse
    'response_A_mouse_window_034', # Mouse
    'response_A_mouse_window_035', # Mouse
    'response_A_mouse_window_042', # Mouse
    'response_A_mouse_window_047', # Mouse
    'response_A_mouse_window_054', # Mouse
    'response_A_mouse_window_055', # Mouse
    'response_A_mouse_window_056', # Mouse
    'response_A_mouse_window_072', # Mouse
    'response_A_mouse_window_073', # Mouse
    'response_A_mouse_window_084', # Mouse
    'response_A_mouse_window_098', # Mouse
]

# top 50 features for compare pointwise on compare_pointwise with extracted and all metric features
COMPARE_POINTWISE_IMPORTANT_FEATURES = [
    'prev_response_A_gaze_reading_completion_ratio',
    'response_A_response_length',
    'response_length_left',
    'prev_response_A_gaze_normalized_avg_char_position',
    'prev_gaze_max_idx_ratio_left',
    'prev_response_A_gaze_normalized_char_position_variance',
    'prev_query_id',
    'prev_response_A_mouse_window_018',
    'prev_gaze_active_time_reviewing_s',
    'gaze_max_char_position_reached',
    'mouse_max_idx_ratio_left',
    'response_A_gaze_normalized_avg_char_position',
    'prev_mouse_reviewing_offscreen_ratio',
    'prev_response_A_mouse_normalized_char_position_variance',
    'prev_mouse_lookback_time_s',
    'mouse_lookback_time_s',
    'prev_gaze_total_entries_left',
    'prev_response_A_mouse_window_008',
    'prev_response_A_mouse_overall_attention_ratio',
    'prev_cross_modality_reviewing_duration_ratio_gaze_mouse',
    'gaze_max_idx_left',
    'prev_response_A_mouse_normalized_avg_char_position',
    'mouse_reviewing_active_ratio',
    'prev_response_A_mouse_reading_completion_ratio',
    'prev_mouse_composing_duration_s',
    'response_A_gaze_normalized_char_position_variance',
    'prev_response_A_mouse_window_000',
    'prev_mouse_reviewing_active_ratio',
    'mouse_max_char_position_reached',
    'prev_mouse_active_time_composing_s',
    'prev_mouse_reviewing_composing_duration_ratio',
    'prev_user_query_length',
    'prev_mouse_composing_lookback_ratio',
    'prev_gaze_reviewing_active_ratio',
    'prev_response_A_gaze_window_017',
    'prev_response_A_mouse_window_002',
    'prev_mouse_composing_offscreen_ratio',
    'prev_gaze_reviewing_pct',
    'prev_mouse_active_time_reviewing_s',
    'prev_response_A_gaze_window_019',
    'prev_mouse_reviewing_composing_activity_ratio',
    'cross_modality_reviewing_activity_ratio_gaze_mouse',
    'prev_response_A_mouse_window_009',
    'response_A_mouse_normalized_avg_char_position',
    'prev_response_A_response_length',
    'prev_response_A_gaze_window_002',
    'prev_response_A_gaze_window_009',
    'prev_response_A_gaze_window_001',
    'prev_response_A_gaze_window_004',
    'prev_mouse_offscreen_time_composing_s'
]
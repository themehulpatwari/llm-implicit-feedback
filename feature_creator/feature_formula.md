'mouse_left_reviewing_active_ratio':
'gaze_right_reviewing_active_ratio':

what do all active_ratio mean? = Engaged time on one side / global reviewing

min with 100 is to cap off extreme values

'cross_modality_left_reviewing_duration_ratio_gaze_mouse': gaze_left_reviewing_engaged_time_s / (mouse_left_reviewing_engaged_time_s + 0.001)


'gaze_comparison_reviewing_activity_ratio': min(gaze_left_reviewing_active_ratio / (gaze_right_reviewing_active_ratio + 0.001), 100.0)
'gaze_comparison_reviewing_time_diff': gaze_left_reviewing_engaged_time_s - gaze_right_reviewing_engaged_time_s
'gaze_comparison_reviewing_time_ratio': min(gaze_left_reviewing_engaged_time_s / (gaze_right_reviewing_engaged_time_s + 0.001), 100.0)


'mouse_comparison_reviewing_activity_ratio': min(mouse_left_reviewing_active_ratio / (mouse_right_reviewing_active_ratio + 0.001), 100.0)
'mouse_comparison_reviewing_activity_diff': mouse_left_reviewing_active_ratio - mouse_right_reviewing_active_ratio
'mouse_comparison_reviewing_time_diff': mouse_left_reviewing_engaged_time_s - mouse_right_reviewing_engaged_time_s
'mouse_comparison_reviewing_time_ratio': min(mouse_left_reviewing_engaged_time_s / (mouse_right_reviewing_engaged_time_s + 0.001), 100.0)


'gaze_left_reviewing_offscreen_ratio': Mean (average) of the is_not_looking data points on left side during reviewing phase
'gaze_right_reviewing_offscreen_ratio': Mean (average) of the is_not_looking data points on right side during reviewing phase


'gaze_right_reviewing_engaged_pct': (engaged_time_s / total_duration_s * 100)


'cross_modality_composing_activity_ratio_gaze_mouse': gaze_composing_active_ratio / (mouse_composing_active_ratio + 0.001)

gaze_composing_active_ratio = Proportion of gaze samples where user IS looking at screen during composing
mouse_composing_active_ratio = Proportion of mouse samples where mouse IS active during composing

'gaze_active_time_reviewing_s': reviewing_duration_s × (proportion of gaze samples where user is looking)
'gaze_reviewing_duration_s': Total time the reviewing phase lasted 

'gaze_offscreen_time_composing_s': composing_duration_s * composing_offscreen_ratio
'mouse_offscreen_time_composing_s': composing_duration_s * composing_offscreen_ratio
'mouse_reviewing_composing_activity_ratio': reviewing_active_ratio / composing_active_ratio

composing_offscreen_ratio = Proportion of time looking offscreen during composing
reviewing_active_ratio = Proportion of samples where user IS looking at screen during reviewing
composing_active_ratio = Proportion of samples where user IS looking at screen during composing

'gaze_thinking_time_s': thinking_time_s = composing_duration_s * composing_thinking_ratio

composing_duration_s = The total length of time (in seconds) that the composing phase lasts for this query
composing_thinking_ratio = The proportion of time during the composing phase where the user is looking at the screen but NOT reading any text 


'gaze_left_max_char_position_reached' & 'gaze_right_max_char_position_reached': The furthest character position the user reached while reading that response during the reviewing phase. formula: max(reviewing_looking['centre_idx'])


'response_A_gaze_data_points': total number of data points recorded
'response_B_gaze_data_points': total number of data points recorded
'response_B_mouse_data_points': total number of data points recorded

'response_A_gaze_focused_engagement_ratio': below
'response_B_gaze_focused_engagement_ratio': below
'response_A_mouse_focused_engagement_ratio': below
'response_B_mouse_focused_engagement_ratio': below

Filter to only data points where the user is actively looking at text (not offscreen, not at -1 coordinates)
For consecutive pairs of timestamps, calculate the time interval between them
Cap each interval at 2000ms (to filter out long pauses/distractions)
Sum all capped intervals to get "active engaged time"
Divide by the total time span from first to last timestamp
Result is a ratio between 0 and 1



'response_A_gaze_overall_attention_ratio': below
'response_B_gaze_overall_attention_ratio': below
'response_A_mouse_overall_attention_ratio': below
'response_B_mouse_overall_attention_ratio': below

Count how many data points have the user actively looking at text (valid x, y, and centre_idx coordinates, not -1)
overall_attention_ratio = len(looking_data) / len(data_points)


'response_B_gaze_normalized_avg_char_position': below
'response_A_gaze_normalized_avg_char_position': below
'response_B_mouse_normalized_avg_char_position': below

The average normalized character position the user looked at while reading.

'response_A_mouse_normalized_char_position_variance': The variance (spread) of normalized character positions the user looked at






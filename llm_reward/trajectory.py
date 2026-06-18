import json
import csv
import pandas as pd
import re

from typing import List
from pathlib import Path
from collections import defaultdict

from config import *

def match_window(msg: str, window: str, raw_idx: int) -> bool:
    """Check if the given message contains the window text at the specified index.
    The message is cleaned of newlines and carriage returns before checking.
    The window is 10 characters before and after the index but clipped at the edges of the message.
    We use 15 characters before and after the index to allow for more context to handle edge cases where
    the window might not be exactly at the index due to text formatting or other issues.
    """
    if not msg or not window:
        return False

    # Clean both message and window of newlines and carriage returns
    msg_cleaned = msg.replace('\n', ' ').replace('\r', ' ')
    window_cleaned = window.replace('\n', ' ').replace('\r', ' ')
    
    window_length = 15  # characters before and after the index
    start_idx_inclusive = raw_idx - window_length if raw_idx - window_length >= 0 else 0
    end_idx_exclusive = raw_idx + window_length if raw_idx + window_length < len(msg_cleaned) else len(msg_cleaned)
    return window_cleaned in msg_cleaned[start_idx_inclusive:end_idx_exclusive]

def create_query_mapping(
    raw_rows: list,
    responses: list
):
    query_time_ranges = {}  # {query_id: min_ts}
    
    for row in raw_rows:
        if len(row) == 7:
            x, y, window, idx_str, rel_ts_str, _, abs_ts = row
        elif len(row) == 6:
            x, y, window, idx_str, rel_ts_str, abs_ts = row
        else:
            continue
        
        try:
            x_f, y_f = float(x), float(y)
            rel_ts = float(rel_ts_str)
        except (ValueError, TypeError):
            continue
        
        try:
            idx_i = int(float(idx_str)) if idx_str.strip() else -1
        except (ValueError, TypeError):
            idx_i = -1
        
        window = window.strip()
        is_not_looking = x_f == -1 and y_f == -1
        
        # Only process looking events for time range calculation
        if not is_not_looking:
            # Check if this matches any query
            for qid, text in responses:
                if match_window(text, window, idx_i):
                    if qid not in query_time_ranges:
                        query_time_ranges[qid] = (rel_ts, len(text))
                    else:
                        query_time_ranges[qid] = (min(query_time_ranges[qid][0], rel_ts), len(text))
                    break

    return sorted(query_time_ranges.items(), key=lambda x: x[1], reverse=True)

def process_rows(
    raw_rows: List[List[str]],
    query_time_ranges: list[tuple],
    is_left: bool,
    pairwise: bool,
    trajectory_feature: str,
    trajectory_df: pd.DataFrame,
    cur_file_trajectory: str,
):
    trajectory_dict = defaultdict(str) # query_id -> trajectory_str
    negative_sum = defaultdict(int)    # query_id -> off-screen sample count

    for i in range(0, len(raw_rows), SUBSAMPLE_STEP):
        row = raw_rows[i]
        if len(row) == 7:
            # Some files have 7 fields: x, y, window, idx, rel_ts, camera_green, abs_ts            
            x, y, _, idx_str, rel_ts, _, _ = row
        elif len(row) == 6:
            # Some files have 6 fields: x, y, window, idx, rel_ts, abs_ts
            x, y, _, idx_str, rel_ts, _ = row
        else:
            # Skip invalid rows (header or malformed)
            continue
        
        # Parse numeric values
        try:
            x_f, y_f = float(x), float(y)
        except (ValueError, TypeError):
            continue
        
        # Parse index
        try:
            idx_i = int(float(idx_str)) if idx_str.strip() else -1
        except (ValueError, TypeError):
            idx_i = -1
        
        # is_not_looking = x_f == -1 and y_f == -1
        query_id = 0 # default value if no match is found
        resp_length = -1
        rel_ts_float = float(rel_ts)

        for qid, (min_ts, length) in query_time_ranges:
            if min_ts <= rel_ts_float:
                query_id = qid
                resp_length = length
                break

        if query_id == 0: # no found query_id -> skip
            continue

        if re.search(r"max_char_position_reached", trajectory_feature):
            if idx_i >= 0:
                trajectory_dict[query_id] += f" {idx_i}"
        elif re.search(r"overall_attention_ratio", trajectory_feature):
            if idx_i < 0:
                negative_sum[query_id] += 1
            else:
                traj_num = idx_i / resp_length
                if negative_sum[query_id] > 0:
                    trajectory_dict[query_id] += f" {negative_sum[query_id]:.4f}"
                    negative_sum[query_id] = 0
                trajectory_dict[query_id] += f" {traj_num:.4f}"

    for query_id, unprocessed_trajectory_str in trajectory_dict.items():
        # if is_left:
        #     if pairwise:
        #         processed_trajectory_str = f"{unprocessed_trajectory_str.strip()}"
        #     else:
        #         processed_trajectory_str = f"{unprocessed_trajectory_str.strip()}"
        # else:
        processed_trajectory_str = f"{unprocessed_trajectory_str.strip()}"
        # trajectory_df.loc[trajectory_df["query_id"] == query_id, cur_file_trajectory] = processed_trajectory_str

        mask = trajectory_df["query_id"] == query_id
        trajectory_df.loc[mask, cur_file_trajectory] = processed_trajectory_str

def create_trajectory_dataframes(
    input_dataframe: pd.DataFrame,
    trajectory_feature: str,
    pairwise: bool
):    
    # approved_queries = input_dataframe["query_id"]
    approved_queries = set(input_dataframe["query_id"])

    trajectory_df = input_dataframe.copy()
    trajectory_df["trajectory_left"] = None
    if pairwise:
        trajectory_df["trajectory_right"] = None
    search_file_names = "rel_gaze*.csv" if re.search(r'gaze', trajectory_feature) else "rel_mouse*.csv"
    # if re.search("^gaze_", trajectory_feature):
    #     is_left = True if re.search('left', trajectory_feature) else False
    # elif re.search("^response_", trajectory_feature):
    #     is_left = True if re.search("^response_A", trajectory_feature, re.IGNORECASE) else False

    with QUERY_DATA.open(encoding="utf-8") as fh:
        query_dict: dict = json.load(fh)


    files = list(USER_BEHAVIOR_FOLDER.rglob(search_file_names))

    for src in files:
    # for src in USER_BEHAVIOR_FOLDER.rglob(search_file_names):
        try:
            _, user_id, task_id, _ = src.parts[-4:]
            # if user_id != 'worker_0ddfe023':
            #     continue
        except ValueError:
            continue

        # pick which response column matters for this file
        resp_key = 'llm_response_2' if src.stem.endswith("_two") or src.stem.endswith("_right") else 'llm_response_1'
        is_left = resp_key == 'llm_response_1'
        cur_file_trajectory = "trajectory_left" if is_left else "trajectory_right"

        # locate task block in JSON
        task_block = query_dict.get(user_id, {}).get(task_id, [])
        if not task_block:
            continue

        # build (query_id, response_text) pairs
        responses = [
            (q["query_id"], q.get(resp_key, ""))
            for q in task_block
            if q.get(resp_key)
        ]

        # read the file
        with src.open(encoding="utf-8") as fh:
            raw_rows = list(csv.reader(fh))

        skip_file = False
        query_time_ranges = create_query_mapping(raw_rows=raw_rows, responses=responses)
        for qid, _ in query_time_ranges:
            if qid not in approved_queries: 
                skip_file = True
                break
        if skip_file:
            continue

        process_rows(
            raw_rows=raw_rows,
            query_time_ranges=query_time_ranges,
            is_left=is_left,
            pairwise=pairwise,
            trajectory_feature=trajectory_feature,
            trajectory_df=trajectory_df,
            cur_file_trajectory=cur_file_trajectory
        )
        

    remove_for_base_col = ["trajectory", "trajectory_1", "trajectory_2", "query_id"]
    remove_for_trajectory_col = [trajectory_feature, "query_id"]
    base_cols = [col for col in input_dataframe.columns if col not in remove_for_base_col]
    trajectory_cols = [col for col in trajectory_df.columns if col not in remove_for_trajectory_col]
    print(f"traj_cols: {trajectory_cols}")

    base_dataframe = input_dataframe[base_cols]
    trajectory_df = trajectory_df[trajectory_cols]

    return base_dataframe, trajectory_df
import pandas as pd

from trajectory import create_query_mapping

def classify_pointwise_task(
    input_dataframe,

):
    # approved_queries = input_dataframe["query_id"]
    approved_queries = set(input_dataframe["query_id"])

    classify_df = input_dataframe.copy()
    classify_df[""] = None
    search_file_names = "rel_gaze*.csv" if re.search(r'gaze', trajectory_feature) else "rel_mouse*.csv"

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
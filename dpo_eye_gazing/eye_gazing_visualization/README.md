# Eye-Gaze Visualization

Scripts for visualizing per-worker eye-gaze and mouse trajectories overlaid on LLM responses.

## Data required to run

This folder ships without participant data. You need to supply two sources before running:

### 1. `sample_query_logs_table.csv`

Populate this file (header is already present) with rows from your `query_logs_table` export. Each row represents one LLM query shown to a worker:

| Column | Description |
|---|---|
| `query_ID` | Unique query identifier |
| `user_id` | Worker / participant ID |
| `task_id` | Task identifier |
| `user_query` | The prompt shown to the worker |
| `llm_response_1` | Left-panel LLM response text |
| `llm_response_2` | Right-panel LLM response text |
| `llm_name_1` | Model name for response 1 |
| `llm_name_2` | Model name for response 2 |
| `likert_1` | Likert rating for response 1 |
| `likert_2` | Likert rating for response 2 |
| `preference` | Worker's preferred response |
| `adjustment` | Any preference adjustment |
| `query_timestamp` | Timestamp of the query (`YYYY-MM-DD HH:MM:SS`) |

### 2. Worker behavior folders (`{WORKER_ID}/`)

One folder per worker, named by their worker ID. Each folder contains subfolders named by task ID. The `{WORKER_ID}` placeholder folder shows the expected structure:

```
{WORKER_ID}/
└── {TASK_ID}/
    ├── rel_gaze_one.csv    # relative gaze data aligned to response 1
    ├── rel_gaze_two.csv    # relative gaze data aligned to response 2
    ├── rel_mouse_left.csv  # relative mouse data for left panel
    ├── rel_mouse_right.csv # relative mouse data for right panel
    ├── abs_gaze.csv        # absolute gaze coordinates (raw)
    └── abs_mouse.csv       # absolute mouse coordinates (raw)
```

The `rel_*` files are required for visualization. The `abs_*` files are raw sensor recordings.

## Running

```bash
python visualize_gaze.py
```

This scans all `{WORKER_ID}/{TASK_ID}/` folders under this directory, matches gaze/mouse events to LLM responses using timestamps from `sample_query_logs_table.csv`, and writes four PNG figures per qualifying task into that task folder:

- `gaze_trajectory.png` — gaze fixation paths overlaid on response text
- `gaze_timeline.png` — character index vs. elapsed time for gaze
- `mouse_trajectory.png` — mouse movement paths overlaid on response text
- `mouse_timeline.png` — character index vs. elapsed time for mouse

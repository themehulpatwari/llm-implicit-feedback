# LLM Reward Model with Multimodal User Behavior Signals

A research framework for training transformer-based reward models that predict human preferences for LLM responses. Optionally augments text features with eye-gaze and mouse-movement trajectory data collected during human evaluation sessions.

---

## Overview

This project trains a reward model to score or rank LLM outputs based on human judgments. It supports two evaluation paradigms:

- **Pairwise (preference)**: Given two LLM responses to the same query, predict which one the user preferred (`binary_preference`). Trained as a binary classification task.
- **Pointwise (rating)**: Given a single LLM response, predict the user's Likert-scale rating (1–5, normalized to 0–4). Trained as a regression task.

Beyond the text of the query and responses, the framework can incorporate **user behavior trajectories** — time-series of eye-gaze fixations or mouse cursor positions — as additional signals of reading attention.

---

## Repository Structure

```
llm_reward/
├── main.py                  # Entry point: loops over datasets and epoch configs
├── config.py                # All hyperparameters and feature flags
├── run_models.py            # Tokenization, K-fold CV training, W&B logging
├── read_files.py            # Data loaders for pairwise, pointwise, trajectory datasets
├── trajectory.py            # Eye-gaze / mouse CSV parsing and trajectory encoding
├── classify_pointwise.py    # (WIP) Pointwise trajectory classification utility
```

### Input layout (gitignored, must be provided)

```
input/
├── pairwise_output/         # CSVs with pairwise preference labels
│   └── important_features_pairwise.csv
├── pointwise_output/        # CSVs with per-response Likert ratings
├── user_behavior/           # Per-user gaze/mouse CSVs
│   └── <user_id>/<task_id>/rel_gaze*.csv  (or rel_mouse*.csv)
└── query_data.json          # Maps (user_id, task_id) → list of {query_id, llm_response_1, llm_response_2}

api.csv                      # Single-row CSV with column `api_key` (W&B key)
```

---

## How It Works

### 1. Data Loading (`read_files.py`)

`FileReader` offers three static methods:

| Method | Use case |
|---|---|
| `read_query_log_csv` | Standard pairwise or pointwise CSV, no trajectory |
| `trajectory_dataset` | Same CSV but also parses gaze/mouse files and appends trajectory tokens |
| `compare_pairwise_datasets` | Constructs pairwise comparisons from consecutive pointwise entries per user/domain |

Each method builds a Hugging Face `Dataset` with three columns:
- `text`: the user query, prefixed with `"user_query: "`
- `text_pair`: all selected feature columns concatenated as `"col: value\n\n..."` pairs
- label column (`binary_preference` or `likert_1`)

Feature groups can be included or excluded via flags in `config.py`:
- `INCLUDE_GAZE_FEATURES`
- `INCLUDE_MOUSE_FEATURES`
- `INCLUDE_CROSS_MODALITY_FEATURES`
- `INCLUDE_USER_FEATURES`

### 2. Trajectory Encoding (`trajectory.py`)

For each user behavior CSV (eye-gaze or mouse), `create_trajectory_dataframes` reconstructs which query a user was looking at by timestamp, then encodes the sequence as a string:

- **`max_char_position_reached`**: Records the character index the user's gaze/cursor reached at each sample — e.g., `"42 103 87 210 ..."`.
- **`overall_attention_ratio`**: Records `char_index / response_length` as a normalized ratio, with negative (off-screen) events encoded inline — e.g., `"0.12 0.34 2.0000 0.41 ..."`.

The resulting trajectory string is appended to `text_pair` so the transformer can attend to it alongside the response text.

Subsampling is controlled by `SUBSAMPLE_STEP` (default 4) to reduce sequence length.

### 3. Model Training (`run_models.py`)

**Tokenization**

Both `text` and `text_pair` are fed to the tokenizer as a sentence pair. Sequences exceeding `MAX_TOKEN_LENGTH` (default 8192) are truncated, and the last non-padding token is replaced with `...` to signal truncation to the model.

**K-Fold Cross-Validation**

`StratifiedKFold` (default `N_SPLITS=5`) is used to preserve label distribution across folds. Each fold:
1. Re-initializes a fresh `AutoModelForSequenceClassification` from `MODEL_CKPT`.
2. Trains with Hugging Face `Trainer` + FP16 (configurable).
3. Logs all metrics and config to a dedicated W&B run grouped under a timestamped experiment name.
4. Appends out-of-fold predictions to a combined DataFrame.

**Task heads**

| Mode | `num_labels` | Loss | Best-model metric |
|---|---|---|---|
| Pairwise | 2 | CrossEntropy | `eval_f1_class_1` |
| Pointwise | 1 | MSE (regression) | `eval_mse` |

**Metrics**

- Regression: MSE, MAE, R², Pearson r, Spearman ρ, threshold accuracy (±0.5)
- Classification: per-class precision / recall / F1, accuracy

---

## Configuration (`config.py`)

| Parameter | Default | Description |
|---|---|---|
| `MODEL_CKPT` | `answerdotai/ModernBERT-base` | Backbone model (also supports DistilBERT, Longformer) |
| `EPOCH_LIST` | `[10]` | Epochs to sweep over |
| `BATCH_SIZE` | `1` | Per-device batch size |
| `N_SPLITS` | `5` | Number of CV folds |
| `LEARNING_RATE` | `1e-5` | AdamW learning rate |
| `MAX_TOKEN_LENGTH` | `8192` | Truncation length |
| `SUBSAMPLE_STEP` | `4` | Trajectory subsampling rate |
| `TRAJECTORY_ENABLE` | `False` | Use raw per-sample trajectory as input |
| `TRAJECTORY_AGGREGATED_ENABLE` | `True` | Append aggregated trajectory stats to base features |
| `TRAJECTORY_FEATURE` | `response_A_mouse_overall_attention_ratio` | Which trajectory signal to use |
| `COMPARE_POINTWISE` | `False` | Build pairwise comparisons from consecutive pointwise rows |
| `TOKEN_ANALYSIS` | `True` | Analyze token lengths instead of training |
| `FP16_ON` | `True` | Mixed-precision training |
| `GRADIENT_CHECKPOINT_ENABLE` | `False` | Gradient checkpointing to save GPU memory |

---

## Installation

```bash
pip install torch transformers datasets accelerate evaluate scikit-learn scipy pandas wandb
```

A GPU is strongly recommended given the 8 K-token max length and ModernBERT backbone.

---

## Usage

**Run training:**

```bash
python main.py [job_id]
```

`job_id` is an optional identifier appended to W&B run group names (useful for SLURM array jobs). Defaults to `0`.

**Analyze token lengths only (no training):**

Set `TOKEN_ANALYSIS = True` in `config.py`, then run `python main.py`. This prints max/avg token counts and inspects any truncated examples without launching a training run.

**Switch dataset:**

Edit `LIST_OF_FILES` in `config.py` to point to a different CSV under `input/`.

---

## Experiment Tracking

Results are logged to [Weights & Biases](https://wandb.ai). Each cross-validation experiment creates one W&B group (e.g., `pairwise_output/important_features_pairwise.csv_timestamp-2025-01-01_12-00_job_id-0`) containing one run per fold. The W&B API key must be provided in `api.csv`.

Model checkpoints are saved under `output_dir/<group_name>/fold-<n>/`.

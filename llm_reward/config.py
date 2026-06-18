import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Input
QUERY_LOG_FOLDER = BASE_DIR / Path("input")
USER_BEHAVIOR_FOLDER = QUERY_LOG_FOLDER / Path("user_behavior")
QUERY_DATA = QUERY_LOG_FOLDER / Path("query_data.json")

_list_of_files_env = os.environ.get("LIST_OF_FILES")
if _list_of_files_env:
    LIST_OF_FILES = [f.strip() for f in _list_of_files_env.split(",")]
else:
    LIST_OF_FILES = [
        # "pairwise_output/base_pairwise.csv",
        # "pairwise_output/base+all_metrics_pairwise.csv",
        # "pairwise_output/base+extracted_features_pairwise.csv",
        # "pairwise_output/base+extracted+all_metrics_pairwise.csv",
        # "pairwise_output/base+relative_features_pairwise.csv",
        # "pairwise_output/base+user_specific_pairwise.csv",
        "pairwise_output/important_features_pairwise.csv"

        # "pointwise_output/base_pointwise.csv",
        # "pointwise_output/base+all_metrics_pointwise.csv",
        # "pointwise_output/base+extracted_features_pointwise.csv",
        # "pointwise_output/base+extracted+all_metrics_pointwise.csv",
        # "pointwise_output/base+user_specific_pointwise.csv",
        # "pointwise_output/important_features_pointwise.csv"
    ]

PRED_SAVE_NAME = os.environ.get("PRED_SAVE_NAME", "oof_important_features_pairwise.csv")

# wandb api input
WANDB_API_CSV = BASE_DIR / Path("api.csv")

# outputs
WANDB_OUTPUT_DIR = BASE_DIR / Path("output_dir")


# naming/model choice
PROJECT_NAME = os.environ.get("PROJECT_NAME", "confidence")
MODEL_CKPT = os.environ.get("MODEL_CKPT", "answerdotai/ModernBERT-base")

# essential hyperparams
_epoch_list_env = os.environ.get("EPOCH_LIST")
EPOCH_LIST = [int(e.strip()) for e in _epoch_list_env.split(",")] if _epoch_list_env else [10]
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 1))
N_SPLITS = int(os.environ.get("N_SPLITS", 5))
LEARNING_RATE = float(os.environ.get("LEARNING_RATE", 1e-5))
SUBSAMPLE_STEP = int(os.environ.get("SUBSAMPLE_STEP", 4))

# non-essential hyperparams
MAX_TOKEN_LENGTH = int(os.environ.get("MAX_TOKEN_LENGTH", 4096 * 2))
MAX_RESPONSE_TOKEN_LENGTH = int(os.environ.get("MAX_RESPONSE_TOKEN_LENGTH", 2000))
RNG_SEED = int(os.environ.get("RNG_SEED", 49))
FP16_ON = os.environ.get("FP16_ON", "True") == "True"
GRADIENT_CHECKPOINT_ENABLE = os.environ.get("GRADIENT_CHECKPOINT_ENABLE", "False") == "True"
FLASH_ATTN_ENABLE = os.environ.get("FLASH_ATTN_ENABLE", "False") == "True"
TRAJECTORY_FEATURE = os.environ.get("TRAJECTORY_FEATURE", "response_A_mouse_overall_attention_ratio")

# other
TRAJECTORY_ENABLE = os.environ.get("TRAJECTORY_ENABLE", "False") == "True"
TRAJECTORY_AGGREGATED_ENABLE = os.environ.get("TRAJECTORY_AGGREGATED_ENABLE", "True") == "True"
ALL_FEATURES_WITH_TRAJECTORY = os.environ.get("ALL_FEATURES_WITH_TRAJECTORY", "False") == "True"

COMPARE_POINTWISE = os.environ.get("COMPARE_POINTWISE", "False") == "True"

TOKEN_ANALYSIS = os.environ.get("TOKEN_ANALYSIS", "False") == "True"

INCLUDE_USER_FEATURES = os.environ.get("INCLUDE_USER_FEATURES", "False") == "True"
INCLUDE_GAZE_FEATURES = os.environ.get("INCLUDE_GAZE_FEATURES", "True") == "True"
INCLUDE_MOUSE_FEATURES = os.environ.get("INCLUDE_MOUSE_FEATURES", "True") == "True"
INCLUDE_CROSS_MODALITY_FEATURES = os.environ.get("INCLUDE_CROSS_MODALITY_FEATURES", "False") == "True"

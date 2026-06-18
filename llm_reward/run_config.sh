#!/bin/bash
#SBATCH --partition=gpu-a100
#SBATCH --gpus=1
#SBATCH --mem=40G
#SBATCH --cpus-per-task=8
##SBATCH --constraint=vram16
##SBATCH --mail-type=BEGIN
##SBATCH --mail-type=TIME_LIMIT_80
#SBATCH --nodes=1
#SBATCH --time=16:00:00
#SBATCH --output=batch_logs/slurm-%j.out

module load cudnn/8.9.7.29-12-cuda12.6
module load conda/latest

conda activate llm_env

# Input
#LIST_OF_FILES="pairwise_output/new_important_features_pairwise.csv"
#LIST_OF_FILES="pointwise_output/important_features_compare_pointwise.csv"
#PRED_SAVE_NAME="predictions/oof_new_important_features_pairwise_bz1.csv"
#PRED_SAVE_NAME="predictions/oof_new_important_modern_compare_pointwise.csv"
#MAX_RESPONSE_TOKEN_LENGTH=2000
#LIST_OF_FILES="pointwise_output/base_pointwise.csv"
LIST_OF_FILES="pointwise_output/base_compare_pointwise.csv"
PRED_SAVE_NAME="predictions/oof_base_modern_compare_pointwise.csv"
MAX_RESPONSE_TOKEN_LENGTH=4000

# Naming/model choice
PROJECT_NAME="confidence"
#MODEL_CKPT="Qwen/Qwen3-1.7B-Base"
#MODEL_CKPT="answerdotai/ModernBERT-large"
MODEL_CKPT="answerdotai/ModernBERT-base"

# Essential hyperparams
EPOCH_LIST="5"
#EPOCH_LIST="10"
BATCH_SIZE=1
N_SPLITS=5
LEARNING_RATE=1e-5
SUBSAMPLE_STEP=4

# Non-essential hyperparams
MAX_TOKEN_LENGTH=8192
#RNG_SEED=49
RNG_SEED=42
FP16_ON=True
GRADIENT_CHECKPOINT_ENABLE=False
FLASH_ATTN_ENABLE=False
TRAJECTORY_FEATURE="response_A_mouse_overall_attention_ratio"

# Feature flags
TRAJECTORY_ENABLE=False
TRAJECTORY_AGGREGATED_ENABLE=True
ALL_FEATURES_WITH_TRAJECTORY=False
#COMPARE_POINTWISE=True
COMPARE_POINTWISE=False

TOKEN_ANALYSIS=False
INCLUDE_USER_FEATURES=False
INCLUDE_GAZE_FEATURES=True
INCLUDE_MOUSE_FEATURES=True
INCLUDE_CROSS_MODALITY_FEATURES=True

export LIST_OF_FILES PRED_SAVE_NAME PROJECT_NAME MODEL_CKPT \
       EPOCH_LIST BATCH_SIZE N_SPLITS LEARNING_RATE SUBSAMPLE_STEP \
       MAX_TOKEN_LENGTH MAX_RESPONSE_TOKEN_LENGTH RNG_SEED \
       FP16_ON GRADIENT_CHECKPOINT_ENABLE FLASH_ATTN_ENABLE TRAJECTORY_FEATURE \
       TRAJECTORY_ENABLE TRAJECTORY_AGGREGATED_ENABLE ALL_FEATURES_WITH_TRAJECTORY \
       COMPARE_POINTWISE TOKEN_ANALYSIS \
       INCLUDE_USER_FEATURES INCLUDE_GAZE_FEATURES INCLUDE_MOUSE_FEATURES \
       INCLUDE_CROSS_MODALITY_FEATURES

python main.py $SLURM_JOB_ID

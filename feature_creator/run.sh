#!/bin/bash
#SBATCH --partition=cpu
#SBATCH --mem=40G
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --output=/project/anonymous/feature_creator/log/slurm-%j.out
#
module load conda/latest
conda activate dpo

python src/llm_judge.py

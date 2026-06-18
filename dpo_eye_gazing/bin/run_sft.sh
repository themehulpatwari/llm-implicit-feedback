#!/bin/bash

#SBATCH --partition=gpu-a100
#SBATCH --gpus=1
#SBATCH --mem=40G
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --time=168:00:00
#SBATCH --output=log/slurm-%x.%j.out

module load cudnn/8.9.7.29-12-cuda12.6
module load conda/latest
conda activate dpo
#conda activate deepspeed2
#conda activate verl_310
#source ~/.conda/envs/verl_310/bin/activate

#python -u train.py model=pythia28 datasets=[hh] loss=sft exp_name=anthropic_dpo_pythia28 gradient_accumulation_steps=1 batch_size=16 eval_batch_size=16 trainer=FSDPTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16

#python -u train.py model=olmo2_1b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_olmo2_1b gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=gpt2-xl datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_gpt2-xl gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=qwen3_4b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_qwen3_4b gradient_accumulation_steps=1 batch_size=4 eval_batch_size=4 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'

#python -u train.py model=qwen3_17b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_qwen3_17b gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=qwen25_15b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_qwen25_15b gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
python -u train.py model=qwen25_3b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_qwen25_3b gradient_accumulation_steps=1 batch_size=4 eval_batch_size=4 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=pythia69 datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_pythia69 gradient_accumulation_steps=1 batch_size=1 eval_batch_size=1 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'

#python -u train.py model=pythia28 datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_pythia28 gradient_accumulation_steps=1 batch_size=16 eval_batch_size=16 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=pythia28 datasets=[eyep_r,eyep,hhs] loss=sft exp_name=eyep_hhs_sft_pythia28 gradient_accumulation_steps=1 batch_size=16 eval_batch_size=16 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=1 eval_every=10_000 wandb.project='sft_eyep'

#python -u train.py model=llama32_3b datasets=[eyep_r,eyep] loss=sft exp_name=eyep_sft_llama32_3b gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=3 eval_every=200 wandb.project='sft_eyep'
#python -u train.py model=llama32_3b datasets=[eyep_r,eyep,hhs] loss=sft exp_name=eyep_hhs_sft_llama32_3b gradient_accumulation_steps=1 batch_size=8 eval_batch_size=8 trainer=BasicTrainer sample_during_eval=false model.fsdp_policy_mp=bfloat16 n_epochs=1 eval_every=10_000 wandb.project='sft_eyep'

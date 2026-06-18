import gc
import os
import sys

from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np
import evaluate
import scipy.stats
import scipy.special
import wandb 
import torch

from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoConfig,
    TrainingArguments, 
    Trainer,
    DataCollatorWithPadding
)
from sklearn.metrics import (
    mean_squared_error, 
    mean_absolute_error, 
    r2_score, 
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.model_selection import KFold, StratifiedKFold
# from google.colab import userdata
from accelerate import Accelerator
# from sklearn.metrics import 

from read_files import *
from config import *
        
def compute_metrics_for_regression(eval_pred):
    acc_threshold = 0.5
    logits, labels = eval_pred

    # Calculate standard regression metrics
    mse = mean_squared_error(labels, logits)
    mae = mean_absolute_error(labels, logits)
    r2 = r2_score(labels, logits)
    pr = scipy.stats.pearsonr(labels.flatten(), logits.flatten())[0]
    sr = scipy.stats.spearmanr(labels.flatten(), logits.flatten())[0]

    # Calculate custom "accuracy" (predictions within 0.5 of the true label)
    errors = np.abs(logits.flatten() - labels.flatten())
    accuracy = np.sum(errors < acc_threshold) / len(errors)

    return {"mse": mse, "mae": mae, "r2": r2, "pearson_r": pr, "spearman_r": sr, "accuracy": accuracy}
    
def compute_metrics_for_classification(eval_pred):
    logits, labels = eval_pred
    if logits.ndim != 2:
        raise TypeError("wrong dim")

    # probs = scipy.special.softmax(logits, axis=1)[:, 1]
    preds = np.argmax(logits, axis=1)

    precision = precision_score(labels, preds, average=None, labels=[0, 1], zero_division=0)
    recall = recall_score(labels, preds, average=None, labels=[0, 1], zero_division=0)
    f1 = f1_score(labels, preds, average=None, labels=[0, 1], zero_division=0)

    return {
        "accuracy": accuracy_score(labels, preds),
        "precision_class_0": precision[0],
        "precision_class_1": precision[1],
        "recall_class_0": recall[0],
        "recall_class_1": recall[1],
        "f1_class_0": f1[0],
        "f1_class_1": f1[1],
        # "roc_auc": roc_auc_score(labels, probs),
    }


def setup(
    job_id, 
    query_log_path,
    is_pairwise,
    group_name,
    dataset,
    label_col
):
    # accelerator = Accelerator()
    # device = accelerator.device 
    # os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_CKPT)

    def tokenize(batch):
        tokens = tokenizer(
            batch["text"],
            batch["text_pair"],
            padding=True,
            truncation=True,
            max_length=MAX_TOKEN_LENGTH,
            return_length=True
        )

        tokens["was_truncated"] = [
            l == MAX_TOKEN_LENGTH for l in tokens["length"]
        ]

        return tokens

    ellipsis_id = tokenizer.encode("...", add_special_tokens=False)[0]
    def replace_last_token(example):
        if example["was_truncated"]:
            # replace last non-padding token
            input_ids = example["input_ids"]

            # find last non-pad token
            if tokenizer.pad_token_id is not None:
                last_idx = max(i for i, t in enumerate(input_ids) if t != tokenizer.pad_token_id)
            else:
                last_idx = len(input_ids) - 1

            # replace last token with ellipsis
            input_ids[last_idx] = ellipsis_id

            example["input_ids"] = input_ids

        return example

    # Apply tokenization to the entire dataset
    full_dataset_encoded = dataset.map(tokenize, batched=True, batch_size=None) # Setting batch_size=None processes the whole dataset at once
    full_dataset_encoded = full_dataset_encoded.map(replace_last_token)

    # Rename the label column to "labels" for the trainer
    full_dataset_encoded = full_dataset_encoded.rename_columns({label_col: "labels"})

    # Give this entire CV experiment a single group name
    # WANDB_GROUP_NAME = f"CV-bert-base-{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}"
    # WANDB_GROUP_NAME = Path(f"CV-bert-base-{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}-job_id-{job_id}")
    wandb_group_name = Path(f"{group_name}_timestamp-{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}_job_id-{job_id}")

    # CRITICAL CHANGE: Set num_labels to 1 for regression
    if is_pairwise:
        num_labels = 2
        
        greater_is_better = True
        metric_for_best_model = "eval_f1_class_1"
        how_to_compute_metrics = compute_metrics_for_classification
        
        print(f"Configuring model for classification with {num_labels} output.")
    else:
        num_labels = 1

        greater_is_better = False
        metric_for_best_model = "mse"
        how_to_compute_metrics = compute_metrics_for_regression
        
        print(f"Configuring model for regression with {num_labels} output.")

    return {
        "full_dataset_encoded": full_dataset_encoded,
        "tokenizer_func": tokenizer,
        "num_labels": num_labels,
        "metric_for_best_model": metric_for_best_model,
        "how_to_compute_metrics": how_to_compute_metrics,
        "greater_is_better": greater_is_better,
        "wandb_group_name": wandb_group_name,
    }

def cross_fold(
    full_dataset_encoded, 
    tokenizer_func, 
    num_labels, 
    metric_for_best_model,
    how_to_compute_metrics,
    greater_is_better,
    wandb_group_name,
    is_pairwise,
    epoch,
    base_dataset
):
    config = AutoConfig.from_pretrained(MODEL_CKPT)
    config.attn_implementation = None

    api_key = pd.read_csv(WANDB_API_CSV)["api_key"].iloc[0]
    # kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RNG_SEED)
    kf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RNG_SEED)

    os.environ["WANDB_API_KEY"] = api_key

    all_fold_metrics = []
    all_preds = []
    data_collator = DataCollatorWithPadding(tokenizer_func)
    # flash_attn_enable = True if MODEL_CKPT == "answerdotai/ModernBERT-base" else False

    # --- 2. Cross-Validation Loop ---
    # for fold, (train_idx, val_idx) in enumerate(kf.split(full_dataset_encoded)):
    for fold, (train_idx, val_idx) in enumerate(kf.split(X=full_dataset_encoded["input_ids"], y=full_dataset_encoded["labels"])):
        print(f"=============== FOLD {fold+1}/{N_SPLITS} ===============")

        # -- A. Create datasets --
        train_fold = full_dataset_encoded.select(train_idx)
        eval_fold = full_dataset_encoded.select(val_idx)

        # -- B. Re-initialize Model --
        if is_pairwise:
            model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_CKPT,
                num_labels=num_labels,
                problem_type="single_label_classification",
                # dtype=torch.float16,
                # attn_implementation="flash_attention_2" if FLASH_ATTN_ENABLE else None,
                attn_implementation="sdpa",
            )
        else:
            model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_CKPT, 
                num_labels=num_labels,
                # dtype=torch.float16,
                attn_implementation="sdpa",
                # attn_implementation="flash_attention_2" if FLASH_ATTN_ENABLE else None,
            )

        if GRADIENT_CHECKPOINT_ENABLE:
            model.gradient_checkpointing_enable()

        # -- C. Explicitly initialize W&B for this fold --
        # The trainer will automatically use this active run
        wandb.init(
            project=PROJECT_NAME,  # Specify your W&B project name
            group=str(wandb_group_name),
            name=f"fold-{fold+1}",
            config={
                "fold_num": fold + 1,
                "model_name": MODEL_CKPT,
                "learning_rate": LEARNING_RATE,
                "batch_size": BATCH_SIZE,
                "num_train_epochs": epoch,
                "epoch_list": EPOCH_LIST,
                "weight_decay": 0.01,
                "num_folds": N_SPLITS,
                "seed": RNG_SEED,
                "fp16": FP16_ON,
                "max_token_length": MAX_TOKEN_LENGTH,
                "max_response_token_length": MAX_RESPONSE_TOKEN_LENGTH,
                "subsample_step": SUBSAMPLE_STEP,
                "gradient_checkpoint_enable": GRADIENT_CHECKPOINT_ENABLE,
                "flash_attn": FLASH_ATTN_ENABLE,
                "is_pairwise": is_pairwise,
                "include_user_features": INCLUDE_USER_FEATURES,
                "include_gaze_features": INCLUDE_GAZE_FEATURES,
                "include_mouse_features": INCLUDE_MOUSE_FEATURES,
                "include_cross_modality_features": INCLUDE_CROSS_MODALITY_FEATURES,
                "trajectory_enable": TRAJECTORY_ENABLE,
                "trajectory_feature": TRAJECTORY_FEATURE,
                "aggregate_trajectory_baseline_features": TRAJECTORY_AGGREGATED_ENABLE,
                "all_features_with_trajectory": ALL_FEATURES_WITH_TRAJECTORY and TRAJECTORY_ENABLE,
                "compare_pointwise": COMPARE_POINTWISE,
                "list_of_files": LIST_OF_FILES,
                "pred_save_name": PRED_SAVE_NAME,
            },
            reinit=True, # Important for loops in notebooks
        )

        # -- D. Define Training Arguments --
        # output_dir = f"/content/drive/MyDrive/Research/NLP_Multimodal_LLM/output/{WANDB_GROUP_NAME}/fold-{fold+1}"
        output_dir = WANDB_OUTPUT_DIR / wandb_group_name / f"fold-{fold+1}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # We no longer need run_name here as wandb.init() handles it
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epoch,
            learning_rate=LEARNING_RATE,
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=BATCH_SIZE,
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="best",
            metric_for_best_model=metric_for_best_model,
            greater_is_better=greater_is_better,
            logging_strategy="epoch",
            load_best_model_at_end=False,
            push_to_hub=False,
            fp16=FP16_ON,
            dataloader_pin_memory=True,
            seed=RNG_SEED,
            # To avoid cluttering the output, we can disable the progress bar for inner loops
        )

        # -- D. Initialize and run the Trainer for this fold --
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_fold,
            eval_dataset=eval_fold,
            compute_metrics=how_to_compute_metrics,
            tokenizer=tokenizer_func,
            data_collator = data_collator, 
        )

        trainer.train()
        metrics = trainer.evaluate()
        all_fold_metrics.append(metrics)
        print(f"Metrics for Fold {fold+1}: {metrics}")

        eval_df = eval_fold.to_pandas()

        predictions = trainer.predict(eval_fold)
        logits = predictions.predictions
        if is_pairwise:
            probs = torch.nn.functional.softmax(torch.tensor(logits), dim=-1).numpy()
            confidence = np.max(probs, axis=1)
            pred_labels = np.argmax(probs, axis=1)
            eval_df["class_0_prob"] = probs[:, 0] 
            eval_df["class_1_prob"] = probs[:, 1]
        else:
            pred_labels = logits.flatten()
            confidence = np.full(len(pred_labels), np.nan)

 
        eval_df["prediction"] = pred_labels
        eval_df["confidence"] = confidence
        eval_df["original_index"] = val_idx

        all_preds.append(eval_df)

        wandb.finish() # End the W&B run for this fold

        # -- F. Clean up --
        del model
        del trainer
        torch.cuda.empty_cache()
        gc.collect()

    oof_df = pd.concat(all_preds, ignore_index=True)
    # oof_df = final_df.sort_values("original_index")
    # oof_df = final_df.drop(columns=["original_index"])

    base_dataset = base_dataset.to_pandas()

    print("oof_df rows:", oof_df.shape[0], ", cols:", oof_df.shape[1])
    print("base_dataset rows:", base_dataset.shape[0], ", cols:", base_dataset.shape[1])
    print(f"oof cols: {oof_df.columns}")
    print(f"base cols: {base_dataset.columns}")
    print('base index', base_dataset.index)
    print('base index', oof_df["original_index"])

    # base_dataset = base_dataset.merge(
    #     oof_df,
    #     left_index=True,
    #     right_on="original_index",
    #     how="left"
    # ).sort_index()

    # base_dataset = base_dataset.drop(columns=["original_index"])
    # base_dataset.to_csv(WANDB_OUTPUT_DIR / wandb_group_name / PRED_SAVE_NAME, index=False)
    #oof_df.to_csv(WANDB_OUTPUT_DIR / wandb_group_name / PRED_SAVE_NAME, index=False)
    oof_df.to_csv(PRED_SAVE_NAME, index=False)

    # --- 3. Aggregate and Display Final Results ---
    print("\n=============== Cross-Validation Complete ===============")
    print(f"Metrics were calculated over {N_SPLITS} folds.")

    # Create a DataFrame to easily calculate mean and std dev
    results_df = pd.DataFrame(all_fold_metrics)

    # Display mean and standard deviation for each metric
    print("\nAverage Metrics (Mean +/- Std Dev):")
    for metric in results_df.columns:
        mean_val = results_df[metric].mean()
        std_val = results_df[metric].std()
        print(f"- {metric}: {mean_val:.4f} +/- {std_val:.4f}")

def token_analysis(    
    dataset,
    label_col
):
    print(dataset.column_names)
    print(dataset[0])

    tokenizer = AutoTokenizer.from_pretrained(MODEL_CKPT)

    def token_stats(dataset, tokenizer):
        def get_length(batch):
            tokens = tokenizer(
                batch["text"],
                batch["text_pair"],
                padding=False,
                truncation=False,
            )
            return {"length": [len(ids) for ids in tokens["input_ids"]]}

        length_dataset = dataset.map(get_length, batched=True, batch_size=64)
        avg_len = sum(length_dataset["length"]) / len(length_dataset["length"])
        max_len = max(length_dataset["length"])
        return max_len, avg_len

    
    
    max_len, avg_len = token_stats(dataset, tokenizer)
    print(f"\nMaximum token length in dataset: {max_len}")
    print(f"\nAverage token length in dataset: {avg_len}")

    #test ... works
    def tokenize(batch):
        tokens = tokenizer(
            batch["text"],
            batch["text_pair"],
            padding=False,
            truncation=True,
            max_length=MAX_TOKEN_LENGTH,
            return_length=True
        )

        tokens["was_truncated"] = [
            l == MAX_TOKEN_LENGTH for l in tokens["length"]
        ]

        return tokens

    ellipsis_id = tokenizer.encode("...", add_special_tokens=False)[0]
    def replace_last_token(example):
        if example["was_truncated"]:
            # replace last non-padding token
            input_ids = example["input_ids"]

            # find last non-pad token
            if tokenizer.pad_token_id is not None:
                last_idx = max(i for i, t in enumerate(input_ids) if t != tokenizer.pad_token_id)
            else:
                last_idx = len(input_ids) - 1

            # replace last token with ellipsis (first token if multi-token)
            input_ids[last_idx] = ellipsis_id

            example["input_ids"] = input_ids

        return example

    # Apply tokenization to the entire dataset
    full_dataset_encoded = dataset.map(tokenize, batched=True, batch_size=None) # Setting batch_size=None processes the whole dataset at once
    full_dataset_encoded = full_dataset_encoded.map(replace_last_token)

    truncated_indices = [
    i for i, x in enumerate(full_dataset_encoded["was_truncated"]) if x
]

    print(f"Found {len(truncated_indices)} truncated examples")
    if truncated_indices:
        i = truncated_indices[0]

        print("\n===== TRUNCATED EXAMPLE =====")

        print("\n--- ORIGINAL TEXT ---")
        print(dataset[i]["text"])

        print("\n--- ORIGINAL TEXT_PAIR (START) ---")
        print(dataset[i]["text_pair"][:1000])  # avoid huge print

        print("\n--- TOKENIZED (DECODED) ---")
        print(tokenizer.decode(full_dataset_encoded[i]["input_ids"]))

        print("\n--- LENGTH ---")
        print(len(full_dataset_encoded[i]["input_ids"]))

        print("\n--- WAS TRUNCATED ---")
        print(full_dataset_encoded[i]["was_truncated"])

        print("==============================\n")


    # def tokenize(batch):
    #     return tokenizer(
    #         batch["text"],
    #         batch["text_pair"],
    #         padding=True, 
    #         truncation=True, 
    #         max_length=MAX_TOKEN_LENGTH
    #     )

    # full_dataset_encoded = dataset.map(tokenize, batched=True, batch_size=None) # Setting batch_size=None processes the whole dataset at once
    # full_dataset_encoded = full_dataset_encoded.rename_columns({label_col: "labels"})


    # print(f"Num samples: {len(full_dataset_encoded)}")
    # kf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RNG_SEED)
    # for fold, (train_idx, val_idx) in enumerate(kf.split(X=full_dataset_encoded["input_ids"], y=full_dataset_encoded["labels"])):
    #     print(f"{{train_idx: {train_idx}, val_idx: {val_idx}}}")
    #     break

    # example = full_dataset_encoded[0]

    # print("\n===== Example Tokenization =====")
    # print("Original text:", dataset[0]["text"])
    # print("Original text_pair:", dataset[0]["text_pair"])
    # print("Label:", example["labels"])

    # print("\nInput IDs:", example["input_ids"])
    # print("Attention mask:", example["attention_mask"])

    # print("\nDecoded:")
    # print(tokenizer.decode(example["input_ids"]))
    # print("================================\n")



def run_models(   
    job_id, 
    query_log_path,
    is_pairwise,
    group_name,
    epoch
):
    np.random.seed(RNG_SEED)
    torch.manual_seed(RNG_SEED)
    torch.cuda.manual_seed_all(RNG_SEED)

    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA device:", torch.cuda.get_device_name(0))
    else:
        print("NO GPU FOUND")

    # Read file
    if TRAJECTORY_ENABLE:
        base_dataset, trajectory_dataset, label_col = FileReader.trajectory_dataset(
            trajectory_feature=TRAJECTORY_FEATURE,
            query_path = query_log_path,
            pairwise = is_pairwise
        )
    elif COMPARE_POINTWISE:
        base_dataset, label_col = FileReader.compare_pointwise_datasets(
            query_path = query_log_path
        )
    else:
        base_dataset, label_col = FileReader.read_query_log_csv(
            query_path = query_log_path,
            pairwise = is_pairwise 
        )

    #cross fold (or token analysis)
    if TOKEN_ANALYSIS:
        token_analysis(
            dataset=base_dataset if not TRAJECTORY_ENABLE else trajectory_dataset,
            label_col=label_col
        )
    elif TRAJECTORY_ENABLE:
        # # with trajectory dataset
        resp_dict = setup(
            job_id=job_id, 
            query_log_path = query_log_path,
            is_pairwise = is_pairwise,
            group_name = group_name,
            dataset=trajectory_dataset,
            label_col=label_col
        )
        resp_dict["is_pairwise"] = is_pairwise
        resp_dict["epoch"] = epoch
        resp_dict["base_dataset"] = base_dataset
        
        cross_fold(**resp_dict)
    else:
        resp_dict = setup(
            job_id=job_id, 
            query_log_path = query_log_path,
            is_pairwise = is_pairwise,
            group_name = group_name,
            dataset=base_dataset,
            label_col=label_col
        )
        resp_dict["is_pairwise"] = is_pairwise
        resp_dict["epoch"] = epoch
        resp_dict["base_dataset"] = base_dataset
        
        cross_fold(**resp_dict)

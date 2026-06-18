import re

from pathlib import Path

import pandas as pd

from datasets import Dataset
from transformers import AutoTokenizer

from trajectory import *
from config import *


def _truncate_response(text, tokenizer, max_tokens):
    token_ids = tokenizer.encode(str(text), add_special_tokens=False)
    if len(token_ids) > max_tokens:
        truncated = tokenizer.decode(token_ids[:max_tokens], skip_special_tokens=True)
        return truncated + "..."
    return text


def _truncate_llm_responses(df, tokenizer):
    for col in df.columns:
        if "llm_response_1" in col or "llm_response_2" in col:
            df.loc[:, col] = df[col].apply(
                lambda x: _truncate_response(x, tokenizer, MAX_RESPONSE_TOKEN_LENGTH)
            )
    return df

class FileReader():
    @staticmethod
    def read_query_log_csv(query_path: Path, pairwise: bool):
        df = pd.read_csv(query_path)

        columns = list(df.columns)

        drop_cols = ["llm_1", "llm_2", "llm_name", "adjustment", "user_query", "query_id", "prev_user_query"]

        label_col = "binary_preference" if pairwise else "likert_1"
        drop_cols.append(label_col)
        if not INCLUDE_GAZE_FEATURES:
            drop_cols.append('gaze')
        if not INCLUDE_MOUSE_FEATURES:
            drop_cols.append('mouse')
        if not INCLUDE_CROSS_MODALITY_FEATURES:
            drop_cols.append('cross_modality')
        if not INCLUDE_USER_FEATURES:
            drop_cols.append('user_id')

        pattern = r'(' + '|'.join(drop_cols) + r')'

        text_cols = [col for col in columns if not re.search(pattern, col)]
        if not INCLUDE_CROSS_MODALITY_FEATURES:
            text_cols = [col for col in text_cols if "cross_modality" not in col]
        print(text_cols)

        tokenizer = AutoTokenizer.from_pretrained(MODEL_CKPT)
        df = _truncate_llm_responses(df, tokenizer)

        if 'prev_user_query' in df:
            print("insert previous query")
            df["text"] = "user_query: " + df["user_query"] + "prev_user_query: " + df["prev_user_query"]
        else:
            df["text"] = "user_query: " + df["user_query"]
        df["text_pair"] = df[text_cols].apply(
            lambda row: "\n\n".join(
                f"{col}: {row[col]}" for col in text_cols
            ),
            axis=1
        )

        null_counts = df.isna().sum()
        print(null_counts[null_counts > 0])
        df = df.dropna() 
        # df.drop_duplicates()

        # Normalize the ratings from 1 - 5 to 0 - 4(to match with the model)
        # and make sure its a float for regression training
        if pairwise:
            df[label_col] = df[label_col].astype(int)
        else:
            df[label_col] = (df[label_col] - 1).astype(float)

        # dataset = Dataset.from_pandas(df[["input_text", label_col]])
        meta_cols = [c for c in ["query_id", "user_query"] + text_cols if c in df.columns and c not in ["text", "text_pair", label_col]]
        dataset = Dataset.from_pandas(df[["text", "text_pair", label_col] + meta_cols])
        # print(f"Dataset size: {len(dataset)}")
        
        return dataset, label_col

    @staticmethod
    def trajectory_dataset(
        trajectory_feature: str,
        query_path: Path,
        pairwise: bool
    ):
        df = pd.read_csv(query_path)

        # retrieve all relevant column names
        label_col = "binary_preference" if pairwise else "likert_1"
        picked_cols = ["user_query", "query_id", "llm_response_1", label_col]
        if pairwise:
            picked_cols.append("llm_response_2")
        if ALL_FEATURES_WITH_TRAJECTORY:
            picked_cols = list(df.columns)
            # picked_cols.remove(label_col)
            # picked_cols.extend()

        # gets both trajectory feature names
        if re.search(r"max_char_position_reached", trajectory_feature):
            all_trajectory_features = ["gaze_left_max_char_position_reached", "gaze_right_max_char_position_reached"]
            picked_cols.extend(all_trajectory_features)
        elif re.search(r"overall_attention_ratio", trajectory_feature):
            all_trajectory_features = ["gaze_left_max_char_position_reached", "gaze_right_max_char_position_reached"]
            picked_cols.extend(all_trajectory_features)

            result = re.search(r"response_[AB]_(.*)", trajectory_feature)
            if result is None:
                raise ValueError(f"Invalid trajectory_feature: {trajectory_feature}")

            rest_of_string = result.group(1)
            ratio_features = [f"response_A_{rest_of_string}", f"response_B_{rest_of_string}"]
            all_trajectory_features.extend(ratio_features)
            picked_cols.extend(ratio_features)
        
        print(f"pickdd col: {picked_cols}")
        df = df[picked_cols]
        df = df.loc[:, ~df.columns.duplicated()].copy()
        df = df.dropna() 
        # df.drop_duplicates()
        print(f"df columns: {df.columns}")

        # Normalize the ratings from 1 - 5 to 0 - 4(to match with the model)
        # and make sure its a float for regression training
        if pairwise:
            df[label_col] = df[label_col].astype(int)
        else:
            df[label_col] = (df[label_col] - 1).astype(float)

        # get both dataframes
        base_dataframe, trajectory_dataframe = create_trajectory_dataframes(
            input_dataframe = df,
            trajectory_feature = trajectory_feature,
            pairwise = pairwise
        )
        trajectory_dataframe = trajectory_dataframe.loc[:, ~trajectory_dataframe.columns.duplicated()]

        tokenizer = AutoTokenizer.from_pretrained(MODEL_CKPT)
        base_dataframe = _truncate_llm_responses(base_dataframe, tokenizer)
        trajectory_dataframe = _truncate_llm_responses(trajectory_dataframe, tokenizer)

        # base dataset
        text_cols = ["llm_response_1"] + all_trajectory_features
        if pairwise:
            text_cols.append("llm_response_2")
        base_dataframe["text"] = "user_query: " + base_dataframe["user_query"]
        base_dataframe["text_pair"] = base_dataframe[text_cols].apply(
            lambda row: "\n\n".join(
                f"{col}: {row[col]}" for col in text_cols
            ),
            axis=1
        )

        base_meta_cols = [c for c in ["query_id", "user_query"] + text_cols if c in base_dataframe.columns and c not in ["text", "text_pair", label_col]]
        base_dataset = Dataset.from_pandas(base_dataframe[["text", "text_pair", label_col] + base_meta_cols])


        # trajectory dataset
        text_cols = ["llm_response_1", "trajectory_left"]
        if pairwise:
            text_cols += ["llm_response_2", "trajectory_right"]
        if ALL_FEATURES_WITH_TRAJECTORY:    
            text_cols = [c for c in picked_cols if c in trajectory_dataframe.columns and ("llm_1" not in c) and ("llm_2" not in c) ]
            text_cols.append("trajectory_left")
            if pairwise:
                text_cols.append("trajectory_right")

            
        text_cols = list(dict.fromkeys(text_cols))
        if label_col in text_cols:
            text_cols.remove(label_col)
        trajectory_dataframe["text"] = "user_query: " + trajectory_dataframe["user_query"] 

        trajectory_dataframe["text_pair"] = trajectory_dataframe[text_cols].apply(
            lambda row: "\n\n".join(
                f"{col}: {row[col]}" for col in text_cols
            ),
            axis=1
        )
        if TRAJECTORY_AGGREGATED_ENABLE or ALL_FEATURES_WITH_TRAJECTORY:
            # trajectory_dataframe["text_pair"] = base_dataframe["text_pair"] + trajectory_dataframe["text_pair"]
            trajectory_dataframe["text_pair"] = base_dataframe["text_pair"].str.cat(
                trajectory_dataframe["text_pair"],
                sep="\n\n"
            )
    
        traj_meta_cols = [c for c in ["query_id", "user_query"] + text_cols if c in trajectory_dataframe.columns and c not in ["text", "text_pair", label_col]]
        trajectory_dataset = Dataset.from_pandas(trajectory_dataframe[["text", "text_pair", label_col] + traj_meta_cols])

        return base_dataset, trajectory_dataset, label_col

    @staticmethod
    def compare_pointwise_datasets(query_path) -> tuple:
        df = pd.read_csv(query_path)
        # df = df.head(10)
        print(f"shape: {df.shape}")

        drop_cols = ["llm_1", "llm_2", "llm_name", "adjustment"]
        label_col = "preference"
        columns = list(df.columns)
        
        # drop_cols.append(label_col)
        if not INCLUDE_GAZE_FEATURES:
            drop_cols.append('gaze')
        if not INCLUDE_MOUSE_FEATURES:
            drop_cols.append('mouse')
        if not INCLUDE_CROSS_MODALITY_FEATURES:
            drop_cols.append('cross_modality')

        pattern = r'(' + '|'.join(drop_cols) + r')'

        text_cols = [col for col in columns if not re.search(pattern, col)]

        df = df[text_cols]
        print(f"Path: {query_path}")
        print(f"Columns before filtering: {columns}")
        print(f"Columns after filtering: {df.columns.tolist()}")

        df = df.sort_values(by=["user_id", "domain", "query_id"])
        grouped = df.groupby(["user_id", "domain"])
        prev_df = grouped.shift(1).add_prefix("prev_")
        df = pd.concat([df, prev_df], axis=1)
        if not INCLUDE_USER_FEATURES:
            df = df.drop(columns=["user_id", "prev_user_id"], errors="ignore")

        df = df.dropna(subset=[f"prev_query_id", label_col])
        df = df.drop(columns=["query_id", "prev_query_id"], errors = "ignore")
        df = df.loc[:, ~df.columns.duplicated()]
        # print(df.shape)
        print(df.columns)

        text_cols = [col for col in df.columns if col != label_col]

        tokenizer = AutoTokenizer.from_pretrained(MODEL_CKPT)
        df = _truncate_llm_responses(df, tokenizer)

        df["text"] = "user_query: " + df["user_query"]

        df["text_pair"] = df[text_cols].apply(
            lambda row: "\n\n".join(
                f"{col}: {row[col]}" for col in text_cols
            ),
            axis=1
        )
        df[label_col] = df[label_col].astype(int)

        # print(df["preference"].unique())
        # print("Rows with NaN in preference BEFORE drop:")
        # print(df[df[label_col].isna()])

        base_dataset = Dataset.from_pandas(df)

        return base_dataset, label_col

import os
import json
import time
from typing import Any
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field

# Set JUDGE to switch the judge model: "openai" | "anthropic" | "together"
#JUDGE = "openai"
#JUDGE = "anthropic"
JUDGE = "together"


MODEL_MAP: dict[str, str] = {
    "openai":    "gpt-5.4-mini",
    "anthropic": "claude-sonnet-4-6",
    "together":  "google/gemma-4-31B-it",
    #"together":  "Qwen/Qwen3.5-397B-A17B",
    #"together":  "moonshotai/Kimi-K2.6",
}

INPUT_PATH = "output/base.csv"
OUTPUT_PATH = f"output/base+llm_judge_{MODEL_MAP[JUDGE].replace('/', '_')}.csv"


max_samples = 100000
#max_samples = 1

SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of two AI-generated responses to a user query.
Your task is to determine which response better answers the user's query.
Output your judgment as JSON with exactly two fields:
- "prediction": 1 if Response 1 is better, 2 if Response 2 is better
- "confidence": a float between 0.0 and 1.0 indicating how confident you are (0.5 = completely uncertain, 1.0 = completely certain)
Output only valid JSON, nothing else."""

PROMPT_TEMPLATE = """User Query:
{query}

Response 1:
{response_1}

Response 2:
{response_2}

Which response better answers the user's query? Output JSON only."""


MAX_RETRIES = 5
RETRY_DELAY = 2        # seconds between retries for parse errors
TIMEOUT_RETRY_DELAY = 30  # seconds between retries for timeout/API errors


class JudgeOutput(BaseModel):
    prediction: int = Field(description="1 if Response 1 is better, 2 if Response 2 is better")
    confidence: float = Field(description="A float between 0.0 and 1.0 indicating how confident you are (0.5 = completely uncertain, 1.0 = completely certain)")


def _raw_call(client: Any, prompt: str) -> str:
    """Make a single API call and return the raw response text."""
    model = MODEL_MAP[JUDGE]
    if JUDGE == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {**JudgeOutput.model_json_schema(), "additionalProperties": False},
                }
            },
        )
        return response.content[0].text
    elif JUDGE == "together":
        import together  # type: ignore[import-untyped]
        together_client: together.Together = client
        completion = together_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"Only answer in JSON and follow this schema: {json.dumps(JudgeOutput.model_json_schema())}.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            timeout=120.0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "judge_output",
                    "schema": JudgeOutput.model_json_schema(),
                },
            },
        )
        return completion.choices[0].message.content
    else:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content


def call_judge(client: Any, query: str, resp_a: str, resp_b: str) -> tuple[int, float]:
    """Call the LLM judge with retries on parse failure or timeout. Returns (prediction, confidence)."""
    prompt = PROMPT_TEMPLATE.format(query=query, response_1=resp_a, response_2=resp_b)
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = _raw_call(client, prompt)
            #print(raw)
            result = json.loads(raw)
            prediction = int(result["prediction"])
            confidence = float(max(0.0, min(1.0, result["confidence"])))
            return prediction, confidence
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            last_err = e
            print(f"  Parse error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            last_err = e
            print(f"  API/timeout error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                print(f"  Waiting {TIMEOUT_RETRY_DELAY}s before retry...")
                time.sleep(TIMEOUT_RETRY_DELAY)
    raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_err}")


def judge_pair(client: Any, query: str, response_1: str, response_2: str) -> dict:
    """
    Run two judge calls to remove position bias.

    First call:  response_1 in position 1, response_2 in position 2.
    Second call: response_2 in position 1, response_1 in position 2.
                 The raw prediction is mapped back to original (1/2) ordering before recording.

    llm_judge_prediction / llm_judge_confidence are the arithmetic averages of the two runs.
    """
    pred_first, conf_first = call_judge(client, query, response_1, response_2)

    raw_second, conf_second = call_judge(client, query, response_2, response_1)
    # Flip the prediction back to original ordering:
    # judge said 1 → the item shown first (response_2) is better → prediction = 2
    # judge said 2 → the item shown second (response_1) is better → prediction = 1
    pred_second = 3 - raw_second  # maps 1→2 and 2→1

    if pred_first == pred_second:
        avg_pred = (pred_first + pred_second) / 2
        avg_conf = (conf_first + conf_second) / 2
    else:
        if conf_first >= conf_second:
            avg_pred = pred_first
            avg_conf = conf_first / (conf_first + conf_second)
        else:
            avg_pred = pred_second
            avg_conf = conf_second / (conf_first + conf_second)

    return {
        "llm_judge_prediction_first": pred_first,
        "llm_judge_confidence_first": conf_first,
        "llm_judge_prediction_second": pred_second,
        "llm_judge_confidence_second": conf_second,
        "llm_judge_prediction": avg_pred,
        "llm_judge_confidence": avg_conf,
    }


def _make_client() -> Any:
    if JUDGE == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    elif JUDGE == "anthropic":
        import anthropic  # type: ignore[import-untyped]
        return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    elif JUDGE == "together":
        import together  # type: ignore[import-untyped]
        return together.Together(api_key=os.environ["TOGETHER_API_KEY"])
    else:
        raise ValueError(f"Unknown JUDGE: {JUDGE!r}. Choose 'openai', 'anthropic', or 'together'.")


def main():
    client = _make_client()
    print(f"Using judge: {JUDGE} / {MODEL_MAP[JUDGE]}")

    df = pd.read_csv(
        INPUT_PATH,
        usecols=["comparison_type", "query_ID", "user_query", "llm_response_1", "llm_response_2", "preference"],
    )
    df = df[df["comparison_type"] != "pointwise"].drop(columns=["comparison_type"]).reset_index(drop=True)
    df["query_id"] = df.pop("query_ID")

    score_cols = [
        "llm_judge_prediction_first", "llm_judge_confidence_first",
        "llm_judge_prediction_second", "llm_judge_confidence_second",
        "llm_judge_prediction", "llm_judge_confidence",
    ]

    # Resume from existing output: merge already-scored rows, skip re-scoring them
    if os.path.exists(OUTPUT_PATH):
        existing = pd.read_csv(OUTPUT_PATH)
        print(f"Loaded existing output ({len(existing)} rows) from {OUTPUT_PATH}")
        existing_scores = existing[["query_id"] + [c for c in score_cols if c in existing.columns]]
        df = df.merge(existing_scores, on="query_id", how="left")
    else:
        for col in score_cols:
            df[col] = pd.NA

    unscored_indices = df.index[df["llm_judge_prediction"].isna()].tolist()
    print(f"Rows to score: {len(unscored_indices)} / {len(df)}")

    for count, idx in enumerate(unscored_indices):
        if count >= max_samples:
            print(f"\nReached max_samples={max_samples}, stopping early for testing.")
            print("=" * 80)
            break
        row = df.loc[idx]
        print(f"[{count + 1}/{len(unscored_indices)}] query_id={row['query_id']}")
        try:
            scores = judge_pair(client, row["user_query"], row["llm_response_1"], row["llm_response_2"])
        except Exception as e:
            print(f"  ERROR: {e}")
            scores = {k: None for k in score_cols}
        for k, v in scores.items():
            df.at[idx, k] = v

    out = df[[
        "query_id", "user_query", "llm_response_1", "llm_response_2", "preference",
    ] + score_cols]

    out.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(out)} rows to {OUTPUT_PATH}")

    # Accuracy: compare rounded llm_judge_prediction against human preference
    # llm_judge_prediction can be 1.0, 1.5 (tie/split), or 2.0
    valid = out[out["llm_judge_prediction"].notna() & out["preference"].notna()]
    n_ties = (valid["llm_judge_prediction"] == 1.5).sum()
    non_tie = valid[valid["llm_judge_prediction"] != 1.5]
    correct = (non_tie["llm_judge_prediction"].round().astype(int) == non_tie["preference"].astype(int)).sum()
    accuracy = correct / len(non_tie) if len(non_tie) > 0 else float("nan")
    print(f"\n--- Accuracy Report ---")
    print(f"Total rows evaluated : {len(valid)}")
    print(f"Split predictions (1.5): {n_ties} ({n_ties / len(valid):.1%})")
    print(f"Decisive predictions : {len(non_tie)}")
    print(f"Correct              : {correct}")
    print(f"Accuracy (decisive)  : {accuracy:.4f} ({accuracy:.1%})")


if __name__ == "__main__":
    main()

"""
LLM-as-a-Judge Evaluation: SFT vs DPO on Anthropic HH-RLHF Test Set
Uses GPT-5 to compare model outputs and compute win rates + average scores.
"""

import os
import json
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional
from datasets import load_dataset
from openai import OpenAI
from vllm import LLM, SamplingParams
import torch
from tqdm import tqdm


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

@dataclass
class EvalConfig:
    # Models
    sft_model_class: str = "EleutherAI/pythia-2.8b"
    sft_model_path: str = "your-org/sft-model"
    dpo_model_class: str = "EleutherAI/pythia-2.8b"
    dpo_model_path: str = "your-org/dpo-model"

    # Dataset
    dataset_name: str = "Anthropic/hh-rlhf"
    dataset_split: str = "test"
    #dataset_file: str = "base_pairwise_test.csv"
    dataset_file: str = "base_pointwise.csv"
    start_samples: int = 0
    max_samples: int = 100
    seed: int = 42

    # Generation
    max_new_tokens: int = 512
    temperature: float = 1.0
    top_p: float = 0.95

    # Judge
    judge_model: str = "gpt-4.1-mini"
    judge_max_tokens: int = 512
    judge_temperature: float = 1.0
    judge_max_workers: int = 8       # parallel judge threads
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Generation batching (reduce if OOM)
    generation_batch_size: int = 50

    # Output
    output_path: str = "eval_results.json"


# ──────────────────────────────────────────────
# Prompt Parsing
# ──────────────────────────────────────────────

def extract_prompt_from_hh(example: dict) -> str:
    conversation = example["chosen"]
    if "\n\nAssistant:" in conversation:
        prompt = conversation.rsplit("\n\nAssistant:", 1)[0]
    else:
        prompt = conversation
    return prompt

def extract_prompt_from_eye(example: dict) -> str:
    return "\n\nHuman: " + example["user_query"]

def get_eye_pair(file_name: str):
    print(f'Loading eye gazing pairwise dataset ({file_name})...')
    dataset_path = f"data/{file_name}"
    dataset = load_dataset("csv", data_files=dataset_path)['train']
    print('done')
    return dataset


# ──────────────────────────────────────────────
# Model Response Generation (vLLM)
# ──────────────────────────────────────────────

class ModelInferencer:
    def __init__(self, model_path: str, model_class: str, config: EvalConfig):
        print(f"Loading model via vLLM: {model_path}")
        parts = model_path.replace("\\", "/").split("/")
        try:
            latest_idx = parts.index("LATEST")
            model_name = parts[latest_idx - 1]
        except ValueError:
            model_name = os.path.splitext(os.path.basename(model_path))[0]

        cache_dir = os.path.join(os.getcwd(), "cache", model_name)

        if os.path.isdir(cache_dir):
            print(f"  Cache hit — loading from: {cache_dir}")
        else:
            print(f"  Cache miss — converting weights and saving to: {cache_dir}")
            from transformers import AutoModelForCausalLM, AutoTokenizer

            hf_model = AutoModelForCausalLM.from_pretrained(model_class)
            state_dict = torch.load(model_path, map_location="cpu")
            hf_model.load_state_dict(state_dict["state"])

            os.makedirs(cache_dir, exist_ok=True)
            hf_model.save_pretrained(cache_dir)
            tokenizer = AutoTokenizer.from_pretrained(model_class)
            tokenizer.save_pretrained(cache_dir)
            del hf_model

        self.llm = LLM(model=cache_dir, gpu_memory_utilization=0.4)
        self.batch_size = config.generation_batch_size
        self.sampling_params = SamplingParams(
            max_tokens=config.max_new_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
        )

    def generate_batch(self, prompts: list[str]) -> list[str]:
        full_prompts = [p + "\n\nAssistant:" for p in prompts]
        results = []
        for start in range(0, len(full_prompts), self.batch_size):
            chunk = full_prompts[start: start + self.batch_size]
            outputs = self.llm.generate(chunk, self.sampling_params)
            results.extend(o.outputs[0].text.strip() for o in outputs)
        return results


# ──────────────────────────────────────────────
# GPT-5 Judge  (few-shot + plain-text output + regex parser)
# ──────────────────────────────────────────────

# Few-shot examples teach the model the exact output format and prevent empty replies.
FEW_SHOT_EXAMPLES = """
---
EXAMPLE 1
## Conversation Prompt
Human: What is the capital of France?

## Response A
The capital of France is Paris. It has been the country's political and cultural centre for centuries.

## Response B
France.

SCORE_A: 9
SCORE_B: 3
WINNER: A
REASONING: Response A directly and accurately answers the question with useful context, while Response B names the country instead of its capital.
---
EXAMPLE 2
## Conversation Prompt
Human: Write a short poem about autumn.

## Response A
Leaves fall like whispered secrets,
Gold and red adorn the trees,
Crisp air carries distant echoes
Of summer's last, reluctant breeze.

## Response B
Autumn is a season. Trees lose leaves. It gets cold.

SCORE_A: 9
SCORE_B: 2
WINNER: A
REASONING: Response A fulfils the creative request with imagery and rhythm; Response B is a flat, prosaic description with no poetic quality.
---
EXAMPLE 3
## Conversation Prompt
Human: How do I reverse a list in Python?

## Response A
You can reverse a list in Python using the built-in reverse() method: my_list.reverse() modifies it in place, or use my_list[::-1] to get a new reversed list.

## Response B
Use the reverse function on the list object. It will reverse the list for you.

SCORE_A: 8
SCORE_B: 5
WINNER: A
REASONING: Response A provides two concrete, correct methods with brief code examples, while Response B is vague and offers no actionable syntax.
---
Now evaluate the following pair using the EXACT same format as the examples above.
"""

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of AI assistant responses.
You will be given a conversation prompt and two responses (A and B) from different AI models.

Evaluate each response on these criteria:
1. Instruction Following: Did the model follow all explicit and implicit instructions?
2. Informativeness: Is the response comprehensive without being verbose?
3. Factuality: Are the claims accurate? For creative prompts, judge internal consistency.
4. Clarity and Coherence: Is the response well-structured and easy to read?
5. Overall Helpfulness: Which response is more ready to use for the human?

You MUST always respond in EXACTLY this format (no extra text, no markdown, no blank response):
SCORE_A: <integer 1-10>
SCORE_B: <integer 1-10>
WINNER: <A or B or tie>
REASONING: <one concise sentence>

Study these examples carefully before evaluating:
""" + FEW_SHOT_EXAMPLES

JUDGE_USER_TEMPLATE = """## Conversation Prompt
{prompt}

## Response A
{response_a}

## Response B
{response_b}

Evaluate both responses using the format specified."""


def parse_judgment(text: str) -> Optional[dict]:
    try:
        score_a   = int(re.search(r"SCORE_A\s*:\s*(\d+)",  text, re.IGNORECASE).group(1))
        score_b   = int(re.search(r"SCORE_B\s*:\s*(\d+)",  text, re.IGNORECASE).group(1))
        winner_m  =     re.search(r"WINNER\s*:\s*(\w+)",   text, re.IGNORECASE).group(1).strip().upper()
        reasoning =     re.search(r"REASONING\s*:\s*(.+)", text, re.IGNORECASE).group(1).strip()

        if winner_m not in {"A", "B", "TIE"}:
            return None

        return {
            "score_A":   score_a,
            "score_B":   score_b,
            "winner":    winner_m if winner_m != "TIE" else "tie",
            "reasoning": reasoning,
        }
    except AttributeError:
        return None


def judge_responses(
    client: OpenAI,
    prompt: str,
    response_a: str,
    response_b: str,
    config: EvalConfig,
    retries: int = 3,
) -> Optional[dict]:
    user_msg = JUDGE_USER_TEMPLATE.format(
        prompt=prompt,
        response_a=response_a,
        response_b=response_b,
    )

    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model=config.judge_model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
                max_completion_tokens=config.judge_max_tokens,
                temperature=config.judge_temperature,
            )
            raw = completion.choices[0].message.content
            if not raw or not raw.strip():
                print(f"  Empty response on attempt {attempt+1}, retrying...")
                time.sleep(2 ** attempt)
                continue
            parsed = parse_judgment(raw)
            if parsed is not None:
                return parsed
            print(f"  Parse failed on attempt {attempt+1}. Raw output:\n{raw}")
        except Exception as e:
            print(f"  API error on attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)

    return None


# ──────────────────────────────────────────────
# Metrics Computation
# ──────────────────────────────────────────────

def compute_metrics(results: list[dict]) -> dict:
    valid = [r for r in results if r.get("judgment") is not None]
    n = len(valid)
    if n == 0:
        return {"error": "No valid judgments"}

    sft_scores = [r["judgment"]["score_sft"] for r in valid]
    dpo_scores = [r["judgment"]["score_dpo"] for r in valid]
    sft_wins   = sum(1 for r in valid if r["judgment"]["winner_model"] == "SFT")
    dpo_wins   = sum(1 for r in valid if r["judgment"]["winner_model"] == "DPO")
    ties       = sum(1 for r in valid if r["judgment"]["winner_model"] == "tie")

    return {
        "n_evaluated":   n,
        "n_skipped":     len(results) - n,
        "sft_avg_score": round(sum(sft_scores) / n, 3),
        "dpo_avg_score": round(sum(dpo_scores) / n, 3),
        "sft_win_rate":  round(sft_wins / n, 3),
        "dpo_win_rate":  round(dpo_wins / n, 3),
        "tie_rate":      round(ties / n, 3),
        "sft_wins":      sft_wins,
        "dpo_wins":      dpo_wins,
        "ties":          ties,
    }


# ──────────────────────────────────────────────
# Main Evaluation Loop
# ──────────────────────────────────────────────

def run_evaluation(config: EvalConfig):
    print(config.dpo_model_path)
    # ── OpenAI client ─────────────────────────
    assert config.openai_api_key, "Set OPENAI_API_KEY env variable"
    client = OpenAI(api_key=config.openai_api_key)
    config.openai_api_key = ""

    # ── Load dataset ──────────────────────────
    if config.dataset_name == "Anthropic/hh-rlhf":
        print(f"Loading dataset: {config.dataset_name} / {config.dataset_split}")
        dataset = load_dataset(config.dataset_name, split=config.dataset_split)
    elif config.dataset_name == "eye":
        print(f"Loading dataset: data / {config.dataset_file}")
        dataset = get_eye_pair(config.dataset_file)

    if config.max_samples:
        #random.seed(config.seed)
        #indices = random.sample(range(len(dataset)), min(config.max_samples, len(dataset)))
        #print(indices)
        random.seed(config.seed)
        indices = random.sample(range(len(dataset)), min(config.max_samples+config.start_samples, len(dataset)))[config.start_samples:]
        #print(indices)
        dataset = dataset.select(indices)
        print(dataset[0])

    print(f"Evaluating {len(dataset)} samples")

    # ── Extract all prompts ───────────────────
    if config.dataset_name == "Anthropic/hh-rlhf":
        prompts = [extract_prompt_from_hh(ex) for ex in dataset]
    elif config.dataset_name == "eye":
        prompts = [extract_prompt_from_eye(ex) for ex in dataset]

    # ── Load models ───────────────────────────
    sft_model = ModelInferencer(config.sft_model_path, config.sft_model_class, config)
    dpo_model = ModelInferencer(config.dpo_model_path, config.dpo_model_class, config)

    # ── Batch generate all responses ──────────
    print("Generating SFT responses (batch)...")
    sft_responses = sft_model.generate_batch(prompts)

    print("Generating DPO responses (batch)...")
    dpo_responses = dpo_model.generate_batch(prompts)

    # ── Randomise A/B assignment ──────────────
    random.seed(config.seed + 1)
    ab_flags = [random.random() < 0.5 for _ in prompts]   # True → A=SFT, False → A=DPO

    # ── Judge all pairs in parallel ───────────
    def judge_one(i):
        a_is_sft = ab_flags[i]
        response_a = sft_responses[i] if a_is_sft else dpo_responses[i]
        response_b = dpo_responses[i] if a_is_sft else sft_responses[i]
        return i, judge_responses(client, prompts[i], response_a, response_b, config)

    raw_judgments = [None] * len(prompts)
    print(f"Judging {len(prompts)} pairs with {config.judge_max_workers} parallel workers...")
    with ThreadPoolExecutor(max_workers=config.judge_max_workers) as executor:
        futures = {executor.submit(judge_one, i): i for i in range(len(prompts))}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Judging"):
            i, judgment_raw = future.result()
            raw_judgments[i] = judgment_raw

    # ── De-randomise A/B → SFT/DPO ───────────
    results = []
    for i in range(len(prompts)):
        judgment_raw = raw_judgments[i]
        a_is_sft = ab_flags[i]
        judgment = None

        if judgment_raw:
            if a_is_sft:
                score_sft, score_dpo = judgment_raw["score_A"], judgment_raw["score_B"]
                raw_winner = judgment_raw["winner"]
            else:
                score_sft, score_dpo = judgment_raw["score_B"], judgment_raw["score_A"]
                raw_winner = judgment_raw["winner"]
                if raw_winner == "A":
                    raw_winner = "B"
                elif raw_winner == "B":
                    raw_winner = "A"

            winner_model = "SFT" if raw_winner == "A" else ("DPO" if raw_winner == "B" else "tie")
            judgment = {
                "score_sft":    score_sft,
                "score_dpo":    score_dpo,
                "winner_model": winner_model,
                "reasoning":    judgment_raw.get("reasoning", ""),
            }

        results.append({
            "index":        i,
            "prompt":       prompts[i],
            "sft_response": sft_responses[i],
            "dpo_response": dpo_responses[i],
            "judgment":     judgment,
        })

    # ── Compute & print metrics ───────────────
    metrics = compute_metrics(results)

    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"Samples evaluated : {metrics['n_evaluated']}  (skipped: {metrics['n_skipped']})")
    print(f"SFT  avg score    : {metrics['sft_avg_score']} / 10")
    print(f"DPO  avg score    : {metrics['dpo_avg_score']} / 10")
    print(f"SFT  win rate     : {metrics['sft_win_rate']*100:.1f}%  ({metrics['sft_wins']} wins)")
    print(f"DPO  win rate     : {metrics['dpo_win_rate']*100:.1f}%  ({metrics['dpo_wins']} wins)")
    print(f"Tie  rate         : {metrics['tie_rate']*100:.1f}%  ({metrics['ties']} ties)")
    print("="*50)

    output = {"config": config.__dict__, "metrics": metrics, "results": results}
    with open(config.output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to: {config.output_path}")

    return metrics, results


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

import argparse

if __name__ == "__main__":
    #model_class = "EleutherAI/pythia-2.8b"
    #config = EvalConfig(
    #    sft_model_class=model_class,
    #    dpo_model_class=model_class,
    #    sft_model_path="models/anonymous/eyep_sft_pythia28_2026-03-16_23-22-35_344382/LATEST/policy.pt",
    #    dpo_model_path="models/anonymous/eye_bert_base_dpo_rev_pythia28_2026-04-05_04-34-13_805526/LATEST/policy.pt",
    #    max_samples=10,
    #    output_path="eval_results/eval_results_bert_base.json",
    #    dataset_name="eye",
    #    judge_max_workers=2,
    #)
    parser = argparse.ArgumentParser(description="Parsing arguments")
    parser.add_argument("--model_class", type=str, default="")
    parser.add_argument("--sft_model", type=str, default="")
    parser.add_argument("--dpo_model", type=str, default="")
    parser.add_argument("--output_path", type=str, default="eval_results/eval_results.json")
    parser.add_argument("--max_samples", type=int, default=50)
    parser.add_argument("--start_samples", type=int, default=0)
    parser.add_argument("--generation_batch_size", type=int, default=50)
    args = parser.parse_args()

    config = EvalConfig(
            sft_model_class=args.model_class,
            dpo_model_class=args.model_class,
            sft_model_path=args.sft_model,
            dpo_model_path=args.dpo_model,
            max_samples=args.max_samples,
            output_path=args.output_path,
            generation_batch_size=args.generation_batch_size,
            dataset_name="eye",
            judge_max_workers=2,
            start_samples=args.start_samples
    )


    #model_class = "EleutherAI/pythia-2.8b"
    #config = EvalConfig(
    #    sft_model_class=model_class,
    #    dpo_model_class=model_class,
    #    #sft_model_path="models/anonymous/anthropic_dpo_pythia28_2026-03-14_05-15-34_077058/LATEST/policy.pt",    # ← replace with your model
    #    #dpo_model_path="models/anonymous/anthropic_dpo_pythia28_2026-03-14_12-17-57_665251/LATEST/policy.pt",    # ← replace with your model
    #    sft_model_path="models/anonymous/eyep_sft_pythia28_2026-03-16_23-22-35_344382/LATEST/policy.pt",    # ← replace with your model
    #    #dpo_model_path="models/anonymous/eye_bert_all_dpo_rev_pythia28_2026-04-05_04-15-56_906205/LATEST/policy.pt",    # ← replace with your model
    #    #dpo_model_path="models/anonymous/eye_bert_base_dpo_rev_pythia28_2026-04-05_04-34-13_805526/LATEST/policy.pt",    # ← replace with your model
    #    dpo_model_path="models/anonymous/eye_rf_imp_dpo_rev_pythia28_2026-04-05_04-39-49_986975/LATEST/policy.pt",    # ← replace with your model
    #    #dpo_model_path="models/anonymous/eye_dpo_rev_pythia28_2026-03-17_05-38-27_357121/LATEST/policy.pt",    # ← replace with your model
    #    #sft_model_path="models/anonymous/eyep_hhs_sft_pythia28_2026-03-16_14-45-09_356740/LATEST/policy.pt",    # ← replace with your model
    #    #dpo_model_path="models/anonymous/eye_hhs_dpo_rev_pythia28_2026-03-17_11-34-33_778858/LATEST/policy.pt",    # ← replace with your model
    #    max_samples=50,
    #    #output_path="eval_results/eval_results_bert_all.json",
    #    #output_path="eval_results/eval_results_bert_base.json",
    #    output_path="eval_results/eval_results_rf_imp.json",
    #    #output_path="eval_results/eval_results_rev.json",
    #    dataset_name="eye",
    #    judge_max_workers=2
    #)

    #model_class = "meta-llama/Llama-3.2-3B"
    #config = EvalConfig(
    #    sft_model_class=model_class,
    #    dpo_model_class=model_class,
    #    sft_model_path="models/anonymous/eyep_sft_llama32_3b_2026-03-17_05-42-26_710363/LATEST/policy.pt",    # ← replace with your model
    #    dpo_model_path="models/anonymous/eye_dpo_rev_llama32_3b_2026-03-17_06-25-20_125385/LATEST/policy.pt",    # ← replace with your model
    #    max_samples=10,
        #output_path="eval_results_eye_rev.json",
    #    output_path="eval_results/eval_results_eye_rev_llama.json",
    #    dataset_name="eye"
    #)
    metrics, results = run_evaluation(config)

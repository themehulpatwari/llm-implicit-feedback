"""
LLM-as-a-Judge Evaluation: SFT vs DPO on Anthropic HH-RLHF Test Set
Uses GPT-5 to compare model outputs and compute win rates + average scores.
"""

import os
import json
import time
import random
from dataclasses import dataclass, field
from typing import Optional
from datasets import load_dataset
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

@dataclass
class EvalConfig:
    # Models
    sft_model_class: str = "EleutherAI/pythia-2.8b"
    sft_model_path: str = "your-org/sft-model"           # HuggingFace model path or local path
    dpo_model_class: str = "EleutherAI/pythia-2.8b"
    dpo_model_path: str = "your-org/dpo-model"           # HuggingFace model path or local path

    # Dataset
    dataset_name: str = "Anthropic/hh-rlhf"
    dataset_split: str = "test"
    max_samples: int = 100                                # set to None to evaluate all
    seed: int = 42

    # Generation
    max_new_tokens: int = 512
    temperature: float = 1
    top_p: float = 0.95
    do_sample: bool = True

    # Judge
    judge_model: str = "gpt-5-mini"                           # GPT-5 as judge
    #judge_model: str = "gpt-5-nano"                           # GPT-5 as judge
    judge_max_tokens: int = 512
    judge_temperature: float = 1.0                       # deterministic judging
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Output
    output_path: str = "eval_results.json"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# ──────────────────────────────────────────────
# Prompt Parsing
# ──────────────────────────────────────────────

def extract_prompt_from_hh(example: dict) -> str:
    """
    HH-RLHF stores full conversations in 'chosen' and 'rejected'.
    We extract just the human turns as the prompt (up to the last Human: turn).
    """
    conversation = example["chosen"]
    # Find the last "\n\nAssistant:" and take everything before it as the prompt
    if "\n\nAssistant:" in conversation:
        prompt = conversation.rsplit("\n\nAssistant:", 1)[0]
    else:
        prompt = conversation
    #return prompt.strip()
    return prompt

def extract_prompt_from_eye(example: dict) -> str:
    query = "\n\nHuman: " + example["user_query"]
    #return query.strip()
    return query

def get_eye_pair(split: str):
    print(f'Loading eye gazing pairwise dataset ({split} split)...')
    dataset_path = f"data/base_pairwise_{split}.csv"
    dataset = load_dataset("csv", data_files=dataset_path)['train']
    #print(dataset)
    #df = pd.read_csv(dataset_path)
    print('done')

    return dataset


# ──────────────────────────────────────────────
# Model Response Generation
# ──────────────────────────────────────────────

class ModelInferencer:
    def __init__(self, model_path: str, model_class: str, config: EvalConfig):
        print(f"Loading model: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_class)
        self.model = AutoModelForCausalLM.from_pretrained(model_class, torch_dtype=torch.float16 if "cuda" in config.device else torch.float32, device_map="auto" )
        state_dict = torch.load(model_path, map_location='cpu')
        self.model.load_state_dict(state_dict['state'])

        #self.model = AutoModelForCausalLM.from_pretrained(
        #    model_path,
        #    torch_dtype=torch.float16 if "cuda" in config.device else torch.float32,
        #    device_map="auto",
        #)
        self.model.eval()
        self.config = config

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    @torch.inference_mode()
    def generate(self, prompt: str) -> str:
        inputs = self.tokenizer(
            prompt + "\n\nAssistant:",
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        ).to(self.config.device)

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=self.config.max_new_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            do_sample=self.config.do_sample,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        # Decode only the newly generated tokens
        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return response.strip()


# ──────────────────────────────────────────────
# GPT-5 Judge
# ──────────────────────────────────────────────

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of AI assistant responses.
You will be given a conversation prompt and two responses (A and B) from different AI models.

Evaluate each response on these criteria:

1. Instruction Following: Did the model follow all explicit and implicit instructions, including formatting, constraints, and personas?
2. Informativeness: Does the response provide a depth of useful information? Is it comprehensive without being verbose?
3. Factuality: Are the claims made accurate and verifiable? (Note: If the prompt is creative, judge based on internal consistency).
4. Clarity and Coherence: Is the response well-structured, logical, and easy to read?
5. Overall Helpfulness: Taking all factors into account, which response is more "ready to use" for the human user?

You must respond ONLY with valid JSON in this exact format (no extra text):
{
  "score_A": <integer 1-10>,
  "score_B": <integer 1-10>,
  "winner": <"A" | "B" | "tie">,
  "reasoning": "<one concise sentence>"
}"""

JUDGE_USER_TEMPLATE = """## Conversation Prompt
{prompt}

## Response A
{response_a}

## Response B
{response_b}

Evaluate both responses and return JSON only."""


def judge_responses(
    client: OpenAI,
    prompt: str,
    response_a: str,
    response_b: str,
    config: EvalConfig,
    retries: int = 3,
) -> Optional[dict]:
    """Call GPT-5 to judge two responses. Returns parsed JSON or None on failure."""
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
                response_format={"type": "json_object"},
            )
            raw = completion.choices[0].message.content
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  JSON parse error on attempt {attempt+1}: {e}")
        except Exception as e:
            print(f"  API error on attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)   # exponential back-off

    return None


# ──────────────────────────────────────────────
# Metrics Computation
# ──────────────────────────────────────────────

def compute_metrics(results: list[dict]) -> dict:
    """
    Compute win rate and average scores.
    Each result dict has: score_sft, score_dpo, winner (from SFT's perspective after de-randomization).
    """
    valid = [r for r in results if r.get("judgment") is not None]
    n = len(valid)
    if n == 0:
        return {"error": "No valid judgments"}

    sft_scores   = [r["judgment"]["score_sft"] for r in valid]
    dpo_scores   = [r["judgment"]["score_dpo"] for r in valid]
    sft_wins     = sum(1 for r in valid if r["judgment"]["winner_model"] == "SFT")
    dpo_wins     = sum(1 for r in valid if r["judgment"]["winner_model"] == "DPO")
    ties         = sum(1 for r in valid if r["judgment"]["winner_model"] == "tie")

    return {
        "n_evaluated":      n,
        "n_skipped":        len(results) - n,
        "sft_avg_score":    round(sum(sft_scores) / n, 3),
        "dpo_avg_score":    round(sum(dpo_scores) / n, 3),
        "sft_win_rate":     round(sft_wins / n, 3),
        "dpo_win_rate":     round(dpo_wins / n, 3),
        "tie_rate":         round(ties / n, 3),
        "sft_wins":         sft_wins,
        "dpo_wins":         dpo_wins,
        "ties":             ties,
    }


# ──────────────────────────────────────────────
# Main Evaluation Loop
# ──────────────────────────────────────────────

def run_evaluation(config: EvalConfig):
    # ── Load dataset ──────────────────────────
    print(f"Loading dataset: {config.dataset_name} / {config.dataset_split}")
    if config.dataset_name == "Anthropic/hh-rlhf":
        dataset = load_dataset(config.dataset_name, split=config.dataset_split)
    elif config.dataset_name == "eye":
        dataset = get_eye_pair(config.dataset_split)

    if config.max_samples:
        random.seed(config.seed)
        indices = random.sample(range(len(dataset)), min(config.max_samples, len(dataset)))
        dataset = dataset.select(indices)

    print(f"Evaluating {len(dataset)} samples")

    # ── Load models ───────────────────────────
    sft_model = ModelInferencer(config.sft_model_path, config.sft_model_class, config)
    dpo_model = ModelInferencer(config.dpo_model_path, config.dpo_model_class, config)

    # ── OpenAI client ─────────────────────────
    assert config.openai_api_key, "Set OPENAI_API_KEY env variable"
    client = OpenAI(api_key=config.openai_api_key)
    config.openai_api_key = ''

    # ── Evaluation loop ───────────────────────
    results = []

    for i, example in enumerate(tqdm(dataset, desc="Evaluating")):
        if config.dataset_name == "Anthropic/hh-rlhf":
            prompt = extract_prompt_from_hh(example)
        elif config.dataset_name == "eye":
            prompt = extract_prompt_from_eye(example)

        # Generate responses
        sft_response = sft_model.generate(prompt)
        dpo_response = dpo_model.generate(prompt)

        # Randomize presentation order to reduce position bias
        if random.random() < 0.5:
            response_a, response_b = sft_response, dpo_response
            a_is_sft = True
        else:
            response_a, response_b = dpo_response, sft_response
            a_is_sft = False

        # Judge
        judgment_raw = judge_responses(client, prompt, response_a, response_b, config)

        # De-randomize: map A/B back to SFT/DPO
        judgment = None
        if judgment_raw:
            if a_is_sft:
                score_sft, score_dpo = judgment_raw["score_A"], judgment_raw["score_B"]
                raw_winner = judgment_raw["winner"]
                winner_model = "SFT" if raw_winner == "A" else ("DPO" if raw_winner == "B" else "tie")
            else:
                score_sft, score_dpo = judgment_raw["score_B"], judgment_raw["score_A"]
                raw_winner = judgment_raw["winner"]
                winner_model = "SFT" if raw_winner == "B" else ("DPO" if raw_winner == "A" else "tie")

            judgment = {
                "score_sft":    score_sft,
                "score_dpo":    score_dpo,
                "winner_model": winner_model,
                "reasoning":    judgment_raw.get("reasoning", ""),
            }

        results.append({
            "index":        i,
            "prompt":       prompt,
            "sft_response": sft_response,
            "dpo_response": dpo_response,
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

    # ── Save results ──────────────────────────
    output = {"config": config.__dict__, "metrics": metrics, "results": results}
    with open(config.output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to: {config.output_path}")

    return metrics, results


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    model_class = "EleutherAI/pythia-2.8b"
    config = EvalConfig(
        sft_model_class=model_class,
        dpo_model_class=model_class,
    #    sft_model_path="models/anonymous/anthropic_dpo_pythia28_2026-03-14_05-15-34_077058/LATEST/policy.pt",    # ← replace with your model
    #    dpo_model_path="models/anonymous/anthropic_dpo_pythia28_2026-03-14_12-17-57_665251/LATEST/policy.pt",    # ← replace with your model
        sft_model_path="models/anonymous/eyep_sft_pythia28_2026-03-16_23-22-35_344382/LATEST/policy.pt",    # ← replace with your model
        #dpo_model_path="models/anonymous/eye_bert_all_dpo_rev_pythia28_2026-04-05_04-15-56_906205/LATEST/policy.pt",    # ← replace with your model
        dpo_model_path="models/anonymous/eye_bert_base_dpo_rev_pythia28_2026-04-05_04-34-13_805526/LATEST/policy.pt",    # ← replace with your model
        #dpo_model_path="models/anonymous/eye_rf_imp_dpo_rev_pythia28_2026-04-05_04-39-49_986975/LATEST/policy.pt",    # ← replace with your model
        #dpo_model_path="models/anonymous/eye_dpo_rev_pythia28_2026-03-17_05-38-27_357121/LATEST/policy.pt",    # ← replace with your model
        #sft_model_path="models/anonymous/eyep_hhs_sft_pythia28_2026-03-16_14-45-09_356740/LATEST/policy.pt",    # ← replace with your model
        #dpo_model_path="models/anonymous/eye_hhs_dpo_rev_pythia28_2026-03-17_11-34-33_778858/LATEST/policy.pt",    # ← replace with your model
        max_samples=10,
        #output_path="eval_results/eval_results_bert_all.json",
        output_path="eval_results/eval_results_bert_base.json",
        #output_path="eval_results/eval_results_rf_imp.json",
        dataset_name="eye"
    )

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

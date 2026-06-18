# Your Mouse and Eyes Secretly Leak Your Preference
## LLM Alignment using Implicit Feedback from Users

**Authors:** Haw-Shiuan Chang\*¹, Jeffrey Gomez\*¹, Mehul Patwari\*¹, Aryan Sajith†², Hamed Zamani¹

¹ University of Massachusetts, Amherst, USA
² York University, Canada

\* Equal contribution. † Work done while at UMass Amherst.

Contact: hschang@cs.umass.edu · {jggomez, mpatwari}@umass.edu · asajith@yorku.ca · zamani@cs.umass.edu

---

Research code and data for **IFLLM**, a dataset of 1,336 multi-turn LLM conversations from 59 Mechanical Turk workers paired with webcam-recorded eye-gaze and mouse-movement trajectories. We use these implicit feedback signals to train reward models that outperform text-only baselines (≈55% → 64% pairwise accuracy) and to align eight 1–4B LLMs via rDPO + NLL, yielding measurable response-quality gains over both text-only and explicit-feedback rewards.

## Pipeline

```
 eye_gazing_LLM ─► dataset ─► NLP-Gazing ─► feature_creator ─► llm_reward ─► dpo_eye_gazing
   (data collection)  (raw)    (features)     (assembly)       (RF / RM)        (DPO)
```

## Folders

- **[eye_gazing_LLM/](eye_gazing_LLM/)** — PHP/JS study website used to run the MTurk experiment. Serves the QA interface, runs WebGazer calibration, and writes raw gaze/mouse traces plus query/response/preference rows into the database. **Produces:** the raw study data that becomes `dataset/`.

- **[dataset/](dataset/)** — Anonymized release of the collected data. `query_logs_table.csv` (queries + LLM responses + preferences), `record_info_table.csv` (worker demographics), `task_table.csv` (per-task summaries), and `user_behavior/<worker>/<task>/*.csv` (gaze and mouse trajectories). **These three CSVs and the `user_behavior/` directory are required inputs for the downstream stages** — copy them into each downstream folder's expected input path (e.g. `NLP-Gazing/`, `feature_creator/input/`, `llm_reward/input/`). If a downstream folder's own README does not specify where to source these files, pull them from here.

- **[NLP-Gazing/](NLP-Gazing/)** — Behavioral feature extraction. Reads `query_logs_table.csv` + `user_behavior/`, matches each gaze sample to the query the user was reading, and extracts ~426 per-comparison features (reading position, dwell time, attention windows, mouse–gaze correlation). **Produces:** `output/extracted_features.csv` consumed by `feature_creator/`.

- **[feature_creator/](feature_creator/)** — Dataset assembly and random-forest / logistic-regression baselines. Joins `extracted_features.csv` with `query_logs_table.csv`, `all_metrics.csv`, and `task_table.csv`; drops 24 low-quality workers; builds combined and split (pairwise / pointwise) feature variants; trains the RF reward models reported in the paper. **Produces:** `pairwise_output/*.csv` and `pointwise_output/*.csv` and the OOF preference predictions consumed by `dpo_eye_gazing/`.

- **[llm_reward/](llm_reward/)** — Transformer-based reward models (ModernBERT, Longformer, DistilBERT) with optional trajectory-token augmentation. Trains pairwise (classification) and pointwise (regression) heads with 5-fold CV over `feature_creator/`'s outputs. Used as the text-only and text+IF baselines in the paper's reward-model table.

- **[dpo_eye_gazing/](dpo_eye_gazing/)** — LLM alignment via rDPO + NLL on eight base models (GPT2-XL, Pythia 2.8B, OLMo2 1B, Llama3.2 3B, Qwen2.5 1.5B/3B, Qwen3 1.7B/4B). Consumes preference predictions from `feature_creator/` or `llm_reward/` as the DPO label source and runs GPT-4.1-mini as judge for evaluation.


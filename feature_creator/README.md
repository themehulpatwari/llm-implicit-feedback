# Feature Creator Pipeline

## Input Files

- **query_logs_table.csv**: Raw query logs from SQL database
- **extracted_features.csv**: Eye-tracking and mouse features from NLP gazing repo
- **all_metrics.csv**: Additional metrics

## Directory Structure

### src/combined_output/
Creates combined datasets (pairwise + pointwise) in `output/` folder:
- **exclude_bad_workers.py**: Removes bad workers (24 worker IDs) from extracted_features.csv
- **create_base.py**: Creates base.csv with one-hot encoded LLM names and comparison_type
- **create_base_user_specific.py**: Adds one-hot encoded user features (MODE: 'top_n' or 'all', TOP_N=5)
- **create_base_extracted_features.py**: Merges base with all extracted features
- **create_base_relative_features.py**: Creates derived features (differences, ratios, window stats)
- **create_base_all_metrics.py**: Merges base with all_metrics
- **create_base_extracted_all_metrics.py**: Combines all features, drops LLM name columns
- **run_all.py**: Runs all combined_output scripts in order

### src/individual_output/
Splits combined datasets into separate pairwise/pointwise files in `pairwise_output/` and `pointwise_output/`:
- **create_pairwise_base.py**: Filters pairwise data, creates binary_preference (1→0, 2→1)
- **create_pointwise_base.py**: Filters pointwise data, uses likert_1 as target
- Similar split scripts for all feature variations (user_specific, extracted_features, relative_features, all_metrics, extracted+all_metrics)
- **run_all.py**: Runs all split scripts in order

### models/
- **pairwise_model/**: New models for pairwise_output/ files (Random Forest, Logistic Regression)
- **pointwise_model/**: New models for pointwise_output/ files (Random Forest, Logistic Regression)
- **pointwise_pairwise_models/**: Old code for combined output/ files (deprecated)

## Pipeline Execution

1. Run src/exclude_bad_workers.py
2. Run src/add_domain_to_query_logs.py

### Option 1: Automated (Recommended)
```bash
# Generate all combined datasets
3. python src/combined_output/run_all.py

# Split into pairwise and pointwise datasets
4. python src/individual_output/run_all.py

# Run models
python models/pairwise_model/model_base_pairwise.py
python models/pointwise_model/model_base_pointwise.py
```

### Option 2: Individual Scripts
```bash
# Step 1: Data creators
python src/combined_output/exclude_bad_workers.py
python src/combined_output/create_base.py
python src/combined_output/create_base_user_specific.py
python src/combined_output/create_base_extracted_features.py
python src/combined_output/create_base_relative_features.py
python src/combined_output/create_base_all_metrics.py
python src/combined_output/create_base_extracted_all_metrics.py

# Step 2: Create individual outputs
python src/individual_output/create_pairwise_base.py
python src/individual_output/create_pointwise_base.py
python src/individual_output/create_pairwise_base_user_specific.py
python src/individual_output/create_pointwise_base_user_specific.py
# ... (run other split scripts as needed)

# Step 3: Run models on individual outputs
python models/pairwise_model/model_base_pairwise.py
python models/pointwise_model/model_base_pointwise.py
```

## Output Files

### output/ (Combined)
- base.csv, base+user_specific.csv, base+extracted_features.csv, base+relative_features.csv, base+all_metrics.csv, base+extracted+all_metrics.csv

### pairwise_output/
- base_pairwise.csv, base+user_specific_pairwise.csv, base+extracted_features_pairwise.csv, base+relative_features_pairwise.csv, base+all_metrics_pairwise.csv, base+extracted+all_metrics_pairwise.csv

### pointwise_output/
- base_pointwise.csv, base+user_specific_pointwise.csv, base+extracted_features_pointwise.csv, base+all_metrics_pointwise.csv, base+extracted+all_metrics_pointwise.csv

## Key Details

- **Merges**: All use intersection (inner join)
- **Bad workers**: 24 worker IDs filtered from all outputs
- **One-hot encoding**: LLM names (llm_1_*, llm_2_*) and user_id dropped after encoding
- **comparison_type**: Determined by presence of llm_response_2 and llm_name_2
- **Pairwise target**: binary_preference (preference 1→0, 2→1)
- **Pointwise target**: likert_1
- **Relative features**: Differences, ratios, 200 window features (100 gaze + 100 mouse), aggregated window stats (mean, std, max, min)

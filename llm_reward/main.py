import sys
import os

from pathlib import Path

from config import *
from run_models import run_models

if FLASH_ATTN_ENABLE:
    os.environ["FLASH_ATTENTION"] = "0"
    os.environ["XFORMERS_FLASH_ATTN"] = "0"
        
def main(job_id):
    list_of_files = LIST_OF_FILES
    
    for file in list_of_files:
        is_pairwise = "pairwise" in str(file) or "compare_pointwise" in str(file)
        if COMPARE_POINTWISE:
            is_pairwise = True
        group_name = f"{str(file)}"

        query_log_path = QUERY_LOG_FOLDER / Path(str(file))

        # for alpha in LEARNING_RATE:
        for epoch in EPOCH_LIST:
            run_models(
                job_id=job_id, 
                query_log_path = query_log_path,
                is_pairwise = is_pairwise,
                group_name = group_name,
                epoch = epoch
            )


if __name__ == "__main__":
    if len(sys.argv) == 2:
    #     print("No job_id detected")
    # else:
        job_id = sys.argv[1]

        # OUTPUT_FILE = str(OUTPUT_FILE.with_name(f"{OUTPUT_FILE.stem}_{job_id}{OUTPUT_FILE.suffix}"))
    else:
        job_id = 0

    main(job_id)

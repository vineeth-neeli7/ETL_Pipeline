
"""
Running Team2 Batch ETL Pipeline
Steps:
1. Upload raw data to S3
2. Upload Glue ETL script to S3
3. Start Glue Crawler
4. Trigger Glue job
"""

import subprocess
import sys
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
BOTO3_DIR = BASE_DIR 

# Scripts in execution order
SCRIPTS = [
    "upload_data_to_s3.py",                 # Step 1: raw data
    "upload_glue_etl_code_to_s3.py",# Step 2: ETL script
    "start_crawler_team2.py", # Step 3: Start Crawler
    "trigger_glue_job.py"              # Step 4: Glue job
]

def run_script(script_name):
    script_path = BOTO3_DIR / script_name
    if not script_path.exists():
        print(f"ERROR: {script_path} not found.")
        sys.exit(1)

    print(f"\n Running {script_name}...")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR running {script_name}: {e}")
        sys.exit(1)

def main():
    print("Starting Batch ETL Pipeline Team2")
    for script in SCRIPTS:
        run_script(script)
    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    main()

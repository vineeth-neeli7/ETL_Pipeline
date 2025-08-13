# boto3_scripts/upload_data_to_s3.py
import boto3
from pathlib import Path

BUCKET_NAME = "batch-etl-pipeline-team2"
S3_KEY = "raw/sales_data.csv"
REGION = "us-east-2"

def main():
    script_dir = Path(__file__).resolve().parent
    local_path = (script_dir / ".." / "data" / "sales_data.csv").resolve()

    if not local_path.exists():
        print(f"File not found: {local_path}")
        return

    s3 = boto3.client("s3", region_name=REGION)
    try:
        s3.upload_file(str(local_path), BUCKET_NAME, S3_KEY)
        print(f"Upload successful: s3://{BUCKET_NAME}/{S3_KEY}")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    main()

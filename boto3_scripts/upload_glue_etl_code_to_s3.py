# boto3_scripts/upload_glue_code.py
import boto3
from pathlib import Path

bucket_name = "batch-etl-pipeline-team2"
s3_key = "glue_scripts/glue_etl_code.py"  
script_dir = Path(__file__).resolve().parent
local_file_path = script_dir.parent / "etl_code" / "glue_etl_code.py"

if local_file_path.is_file():
    s3 = boto3.client("s3")  
    try:
        s3.upload_file(str(local_file_path), bucket_name, s3_key,
                       ExtraArgs={"ContentType": "text/x-python"})
        print(f"Uploaded to s3:/{bucket_name}/{s3_key}")
    except Exception as e:
        print("Failed to upload:", e)
else:
    print("File not found:", local_file_path)

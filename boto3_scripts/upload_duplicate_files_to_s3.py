import os, math, boto3
from pathlib import Path
from boto3.s3.transfer import TransferConfig

BUCKET = "batch-etl-pipeline-team2"
PREFIX = "raw/"
TARGET_GB = 5

LOCAL = (Path(__file__).resolve().parent.parent / "data" / "sales_data.csv").resolve()
if not LOCAL.exists():
    raise SystemExit(f"File not found: {LOCAL}")

size = os.path.getsize(LOCAL)
copies = math.ceil((TARGET_GB * 1024**3) / size)
print(f"Local file ~{size/1024/1024:.1f} MB → uploading {copies} parts to reach ~{TARGET_GB} GB")

s3 = boto3.client("s3")
cfg = TransferConfig(
    multipart_threshold=8*1024*1024,
    multipart_chunksize=64*1024*1024,
    max_concurrency=8,
)

for i in range(copies):
    key = f"{PREFIX}part_{i:05d}.csv"
    s3.upload_file(str(LOCAL), BUCKET, key, Config=cfg, ExtraArgs={"ContentType": "text/csv"})
    if (i + 1) % 25 == 0:
        print(f"Uploaded {i+1}/{copies}")

print(f"Done. Uploaded ~{copies*size/1024/1024/1024:.2f} GB to s3://{BUCKET}/{PREFIX}")

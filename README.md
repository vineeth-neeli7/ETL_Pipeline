# ETL_Pipeline

Team2 Batch ETL Pipeline (AWS Glue + Redshift)
Batch ETL that loads sales data from S3 → Glue (Spark) → Redshift.
Infra is provisioned with Terraform; orchestration steps use small boto3 scripts.

What it does
Stores raw CSVs in S3 (s3://batch-etl-pipeline-team2/raw/)

Glue Crawler catalogs raw data to the Glue Data Catalog

Glue ETL job (PySpark):

casts numeric fields, fills small nulls (unit_price → 0.0, region → "unknown")

robustly parses order_date in dd-MM-yyyy (fallbacks for d-M-yyyy, dd/MM/yyyy, yyyy-MM-dd)

derives order_year

computes total_price = quantity * unit_price (decimal, 2 dp)

drops duplicates and rows with unparseable dates

Loads to Redshift table public.sales_data_team2

Repo layout

ETL_Pipeline/
terraform/
─ s3.tf
─ glue.tf
─ glue_job.tf
─ glue_connection_to_redshift.tf
─ redshift.tf

boto3_scripts/
- upload_data_to_s3.py
- upload_glue_code.py                # uploads etl_code/glue_etl_code.py to S3
- start_crawler_team2.py             # starts crawler & waits until READY
- trigger_glue_job.py                # starts Glue job; prints JobRunId & status
- main_filt_team2.py                 # runs the 4 steps in order

etl_code/
glue_etl_code.py                   # PySpark ETL (runs in Glue)

data/
- sales_data.csv                     # ~24 MB sample (dd-MM-yyyy dates)

README.md

Prerequisites
AWS account with permissions for S3, Glue, IAM, Redshift.

AWS CLI configured (aws configure).

Terraform ≥ 1.5

Python ≥ 3.10 and pip install boto3


1) Deploy infrastructure (Terraform)
From the terraform/ folder:


terraform init
terraform apply -auto-approve
Outputs:

S3 bucket (batch-etl-pipeline-team2)

Glue database + crawler

Glue job glue-etl-job-team2

Redshift cluster redshift-cluster-sales-data-team2 (+ endpoint)

If your VPC/Subnet IDs are different, edit them in redshift.tf before apply.

2) Run a query to Create a table/ schema in redshift table public.sales_data_team2 
CREATE TABLE IF NOT EXISTS public.sales_data_team2 (
  order_id     BIGINT,
  customer_id  VARCHAR(256),
  product_name VARCHAR(256),
  region       VARCHAR(64),
  quantity     BIGINT,
  unit_price   NUMERIC(18,2),
  total_price  NUMERIC(18,2),
  order_date   DATE,
  order_year   INT
);


3) Run the pipeline (boto3 scripts)
From the repo root (or boto3_scripts/), either run end-to-end:


python boto3_scripts/main_filt_team2.py
Or step by step:


1) Upload sample data to S3 (to s3://<bucket>/raw/sales_data.csv)
python boto3_scripts/upload_data_to_s3.py

2) Upload Glue ETL script to S3 (to s3://<bucket>/glue_scripts/glue_etl_code.py)
python boto3_scripts/upload_glue_code.py

3) Start the Glue crawler and wait for READY
python boto3_scripts/start_crawler_team2.py

4) Trigger the Glue ETL job
python boto3_scripts/trigger_glue_job.py
3) Validate in Redshift
Connect to Redshift (use the endpoint/output from Terraform) and run:


-- row count
SELECT COUNT(*) AS rows_loaded FROM public.sales_data_team2;

-- date coverage
SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date
FROM public.sales_data_team2;

-- by year
SELECT order_year, COUNT(*) AS n
FROM public.sales_data_team2
GROUP BY order_year
ORDER BY order_year;

-- quick spot check
SELECT order_id, customer_id, product_name, region,
       quantity, unit_price, total_price, order_date, order_year
FROM public.sales_data_team2
ORDER BY order_date DESC
LIMIT 10;

-- check: no null dates
SELECT COUNT(*) AS null_dates
FROM public.sales_data_team2
WHERE order_date IS NULL;

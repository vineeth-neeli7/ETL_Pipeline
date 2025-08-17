# 🚀 Team2 Batch ETL Pipeline

This project builds an automated **Batch ETL Pipeline** using **AWS Glue + Redshift + Terraform** to process and load sales data from **Amazon S3 → AWS Glue (PySpark) → Amazon Redshift**.

Infrastructure is provisioned via Terraform, and the workflow is orchestrated using Python `boto3` scripts.

---

## 📌 Key Features

- 🗂️ **Stores raw sales data** in S3
- 🔍 **Glue Crawler** auto-catalogs data to the Glue Data Catalog
- 🧹 **Glue ETL Job**:
  - Parses and cleans raw CSVs
  - Handles multiple date formats
  - Derives calculated columns (`total_price`, `order_year`)
  - Fills nulls and casts data types
  - Removes duplicates
- 🛢️ Loads cleaned data into **Redshift** table: `public.sales_data_team2`

---

## 🧱 Project Structure

```
ETL_Pipeline/
├── terraform/                  # Infrastructure-as-Code (S3, Redshift, Glue)
├── boto3_scripts/             # Orchestration scripts for pipeline steps
├── etl_code/                  # Glue ETL PySpark code
├── data/                      # Sample CSV data
├── README.md
```

### 📂 `boto3_scripts/`

- `upload_data_to_s3.py` – Uploads sample data to S3
- `upload_duplicate_file_to_s3.py` – Uploads multiple files to simulate 5GB data
- `upload_glue_code.py` – Uploads PySpark ETL code to S3
- `start_crawler_team2.py` – Starts and monitors Glue Crawler
- `trigger_glue_job.py` – Triggers Glue ETL job
- `main_filt_team2.py` – Runs all steps sequentially

---

## ⚙️ Tech Stack

| Service      | Usage                             |
|--------------|------------------------------------|
| **AWS S3**   | Raw data storage (CSV)             |
| **AWS Glue** | Crawler + ETL (PySpark) processing |
| **Redshift** | Data warehouse for final table     |
| **Terraform**| Infra provisioning                 |
| **Boto3**    | Python-based orchestration         |

---

## 🚧 Prerequisites

- AWS account with access to **S3, Glue, Redshift, IAM**
- AWS CLI configured via `aws configure`
- Terraform ≥ 1.5
- Python ≥ 3.10 with `boto3` installed

```bash
pip install boto3
```

---

## 📦 Deployment Steps

### 1. 🚀 Deploy Infrastructure via Terraform

```bash
cd terraform/
terraform init
terraform apply -auto-approve
```

> 🔧 This provisions:
> - S3 bucket
> - Glue database, crawler, and ETL job
> - Redshift cluster with IAM roles

💡 *Edit `redshift.tf` if your VPC/Subnet IDs differ*

---

### 2. 📥 Create Redshift Table

Before running the pipeline, execute this SQL on Redshift:

```sql
CREATE TABLE public.sales_data_team2 (
  sk BIGINT IDENTITY(1,1),    
  order_id BIGINT,
  customer_id VARCHAR(256),
  product_name VARCHAR(256),
  region VARCHAR(64),
  quantity BIGINT,
  unit_price Numeric(12,2),
  total_price NUMERIC(14,2),
  order_date DATE,
  order_year INT
 );
```

---

### 3. 🛠️ Run the ETL Pipeline

#### ✅ One-Click (End-to-End)
```bash
python boto3_scripts/main_filt_team2.py
```

#### 🔍 Or Step-by-Step

```bash
# 1. Upload raw CSV to S3
python boto3_scripts/upload_data_to_s3.py

# 2. Upload PySpark ETL script to S3
python boto3_scripts/upload_glue_code.py

# 3. Start Glue Crawler
python boto3_scripts/start_crawler_team2.py

# 4. Trigger Glue Job
python boto3_scripts/trigger_glue_job.py
```

---

## 🧪 Validate in Redshift

Connect to Redshift and run:

```sql
-- Row count
SELECT * FROM public.sales_data_team2 Limit 10;

-- Date coverage
SELECT MIN(order_date), MAX(order_date) FROM public.sales_data_team2;

-- Records per year
SELECT order_year, COUNT(*) FROM public.sales_data_team2 GROUP BY order_year;

-- Sample data
SELECT * FROM public.sales_data_team2 ORDER BY order_date DESC LIMIT 10;

-- Null date check
SELECT COUNT(*) FROM public.sales_data_team2 WHERE order_date IS NULL;
```

---

## 📚 Learnings & Highlights

- Understood AWS Glue DPUs and runtime costing
- Learned schema inference via Glue Crawlers
- Handled multiple date parsing edge cases in PySpark
- Explored Redshift’s data casting and performance behavior
- Calculated total_price, year-wise aggregation for business insight
- Demonstrated how 5GB of data was generated and processed via `upload_duplicate_file_to_s3.py`

---

## 💰 AWS Cost Summary (Example)

| Component      | Usage                              | Estimated Cost |
|----------------|------------------------------------|----------------|
| **S3**         | 5 GB of storage                    | ~$0.12/month   |
| **Glue Job**   | 8 DPUs x 23 mins = ~3.06 DPU-Hours | ~$1.34         |
| **Redshift**   | `ra3.xlplus` node (1 hour)         | ~$1.09/hour    |

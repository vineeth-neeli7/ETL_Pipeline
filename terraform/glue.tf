# Glue Database
resource "aws_glue_catalog_database" "raw_db_team2" {
  name = "sales_data_raw_team2"
}

# Glue Service Role
resource "aws_iam_role" "glue_service_role" {
  name = "glue_service_role_team2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "glue.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

# Attaching the managed Glue service policy
resource "aws_iam_role_policy_attachment" "glue_managed" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Least-privilege S3/logs accessing for the bucket
resource "aws_iam_role_policy" "glue_least_privilage" {
  name = "team2-glue-least-priv"
  role = aws_iam_role.glue_service_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   : "Allow",
        Action   : ["s3:ListBucket"],
        Resource : "arn:aws:s3:::${aws_s3_bucket.raw_data_bucket_team2.bucket}"
      },
      {
        Effect   : "Allow",
        Action   : ["s3:GetObject","s3:PutObject","s3:DeleteObject","s3:AbortMultipartUpload"],
        Resource : "arn:aws:s3:::${aws_s3_bucket.raw_data_bucket_team2.bucket}/*"
      },
      {
        Effect   : "Allow",
        Action   : ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
        Resource : "*"
      },
      {
        Effect   : "Allow",
        Action   : [
          "glue:Get*","glue:List*",
          "glue:CreateTable","glue:UpdateTable","glue:DeleteTable",
          "glue:CreatePartition","glue:BatchCreatePartition","glue:UpdatePartition","glue:DeletePartition",
          "glue:BatchGetPartition","glue:CreateDatabase",
          "glue:StartCrawler","glue:StopCrawler","glue:UpdateCrawler","glue:GetCrawler",
          "glue:StartJobRun","glue:GetJobRun","glue:GetJob"
        ],
        Resource : "*"
      }
    ]
  })
}


# Glue Crawler targeting your raw prefix
resource "aws_glue_crawler" "sales_crawler_team2" {
  name          = "sales_data_crawler_team2"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.raw_db_team2.name
  table_prefix  = "team2_"

  s3_target {
    path = "s3://${aws_s3_bucket.raw_data_bucket_team2.bucket}/raw/"
  }

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "DEPRECATE_IN_DATABASE"
  }
}

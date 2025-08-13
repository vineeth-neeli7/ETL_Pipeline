resource "aws_s3_bucket" "raw_data_bucket_team2" {
  bucket        = "batch-etl-pipeline-team2"                #Bucket Name
  force_destroy = true

  tags = {
    Name        = "Raw Sales Data Bucket Team2"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket                  = aws_s3_bucket.raw_data_bucket_team2.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.raw_data_bucket_team2.id
  versioning_configuration { status = "Enabled" }
}

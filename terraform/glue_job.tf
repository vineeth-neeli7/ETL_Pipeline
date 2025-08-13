resource "aws_glue_job" "etl_job_team2" {
  name     = "glue-etl-job-team2"
  role_arn = aws_iam_role.glue_service_role.arn  

  command {
    name            = "glueetl"
    script_location = "s3://batch-etl-pipeline-team2/glue_scripts/glue_etl_code.py"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"      = "s3://batch-etl-pipeline-team2/temp/"
    "--job-language" = "python"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  glue_version = "3.0"
  max_retries  = 1
  timeout      = 10
  number_of_workers = 2
  worker_type       = "G.1X"
}


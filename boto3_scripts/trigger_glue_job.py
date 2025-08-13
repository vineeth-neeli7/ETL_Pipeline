import boto3

glue = boto3.client('glue')
response = glue.start_job_run(JobName='glue-etl-job-team2')
print("Started Glue job run ID:", response['JobRunId'])

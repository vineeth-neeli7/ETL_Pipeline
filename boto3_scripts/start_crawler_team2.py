import time
import boto3

CRAWLER_NAME = "sales_data_crawler_team2"

glue = boto3.client("glue")

# Starting Crawler and ignore if already running
try:
    glue.start_crawler(Name=CRAWLER_NAME)
    print(f"Crawler '{CRAWLER_NAME}' started...")
except glue.exceptions.CrawlerRunningException:
    print(f"Crawler '{CRAWLER_NAME}' already running...")

# Wait until READY
while True:
    state = glue.get_crawler(Name=CRAWLER_NAME)["Crawler"]["State"]  # RUNNING/STOPPING/READY
    if state == "READY":
        print("Crawler completed.")
        break
    print("Crawler is still running...")
    time.sleep(10)

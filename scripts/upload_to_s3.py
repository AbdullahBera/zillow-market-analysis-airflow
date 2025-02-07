import boto3
from botocore.exceptions import NoCredentialsError
import pandas as pd
import logging
import os

# Setup Logging
log_file = "../logs/scraper.log"  # Changed log file to scraper.log
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def upload_to_s3(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        logging.info(f"✅ File {file_name} uploaded to {bucket}/{object_name} successfully.")
        return True
    except FileNotFoundError:
        logging.error(f"❌ The file {file_name} was not found.")
        return False
    except NoCredentialsError:
        logging.error("❌ Credentials not available.")
        return False

def filter_duplicates(csv_path, bucket_name):
    s3_client = boto3.client('s3')
    object_name = os.path.basename(csv_path)

    try:
        s3_client.download_file(bucket_name, object_name, "/tmp/existing_data.csv")
        df_existing = pd.read_csv("/tmp/existing_data.csv")
    except:
        df_existing = pd.DataFrame(columns=["price", "address", "bedrooms", "bathrooms", "square_feet", "scraped_at"])

    df_new = pd.read_csv(csv_path)
    df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=["address"], keep='last')
    df_combined.to_csv(csv_path, index=False)
    logging.info("✅ Duplicates filtered out and CSV updated.")  # Updated log message

if __name__ == "__main__":
    csv_path = "../data/zillow_data.csv"
    bucket_name = "zillow-scraped-data" 

    filter_duplicates(csv_path, bucket_name)  # Ensure CSV is updated before upload

    if upload_to_s3(csv_path, bucket_name):
        logging.info(f"✅ File {csv_path} uploaded to S3 bucket successfully.")  # Added logging for successful upload
        print(f"✅ File {csv_path} uploaded to S3 bucket successfully.")
    else:
        logging.error(f"❌ Failed to upload {csv_path} to S3 bucket.")  # Added logging for failed upload
        print(f"❌ Failed to upload {csv_path} to S3 bucket.")
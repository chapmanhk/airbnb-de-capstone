from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

from upload_to_s3 import upload_file_to_s3
from clean_airbnb_data import clean_airbnb_data
from train_model import train_model_from_cleaned_csv
from batch_inference import run_batch_inference

# ENV variables
RAW_BUCKET = os.getenv("RAW_BUCKET")
CLEANED_BUCKET = os.getenv("CLEANED_BUCKET")
MODELS_BUCKET = os.getenv("MODELS_BUCKET")
PREDICTIONS_BUCKET = os.getenv("PREDICTIONS_BUCKET")

# S3 keys
RAW_S3_KEY = "listings2025-03.csv"
CLEANED_S3_KEY = "cleaned_listings.csv"

# Local paths
RAW_LOCAL_PATH = "/opt/airflow/data/listings2025-03.csv"
CLEANED_LOCAL_PATH = "/opt/airflow/data/cleaned_listings.csv"

default_args = {
    "owner": "airbnb-de-capstone",
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="airbnb_full_pipeline",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    description="Full pipeline: upload → clean → train → predict",
) as dag:

    # Step 1: Upload raw CSV to S3
    upload_raw_task = PythonOperator(
        task_id="upload_raw_to_s3",
        python_callable=upload_file_to_s3,
        op_kwargs={
            "local_path": RAW_LOCAL_PATH,
            "bucket": RAW_BUCKET,
            "s3_key": RAW_S3_KEY,
        },
    )

    # Step 2: Clean the raw data and write to cleaned CSV
    def run_cleaning(**kwargs):
        path = clean_airbnb_data()
        kwargs["ti"].xcom_push(key="cleaned_path", value=path)

    clean_task = PythonOperator(
        task_id="clean_data",
        python_callable=run_cleaning,
        provide_context=True,
    )

    # Step 3: Upload cleaned CSV to S3
    def upload_cleaned(**kwargs):
        ti = kwargs["ti"]
        local_path = ti.xcom_pull(key="cleaned_path", task_ids="clean_data")
        upload_file_to_s3(local_path, CLEANED_BUCKET, CLEANED_S3_KEY)

    upload_cleaned_task = PythonOperator(
        task_id="upload_cleaned_to_s3",
        python_callable=upload_cleaned,
        provide_context=True,
    )

    # Step 4: Train the model (save to S3 + feature importance)
    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model_from_cleaned_csv,
    )

    # Step 5: Run batch inference using trained model
    batch_inference_task = PythonOperator(
        task_id="run_batch_inference",
        python_callable=run_batch_inference
    )

    # DAG flow
    upload_raw_task >> clean_task >> upload_cleaned_task >> train_model_task >> batch_inference_task

import os
import boto3

def upload_file_to_s3(local_path, bucket, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket, s3_key)

def download_from_s3(bucket, s3_key, local_path):
    s3 = boto3.client("s3")
    s3.download_file(bucket, s3_key, local_path)


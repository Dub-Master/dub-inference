import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_S3_ENDPOINT_URL
)


def read_s3_file(key: str) -> bytes:
    resp = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=key)
    return resp['Body'].read()


def save_s3_to_file(key: str, file_path: str) -> str:
    resp = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=key)
    with open(file_path, "wb") as f:
        f.write(resp['Body'].read())
    return file_path


def write_s3_file(key: str, data: bytes) -> None:
    s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=key, Body=data)

import os
import boto3

s3 = boto3.client("s3")
S3_BUCKET: str = os.getenv("BUCKET")

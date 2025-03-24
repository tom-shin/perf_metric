from .. import CONFIG
import boto3

s3 = boto3.client("s3")
S3_BUCKET: str = CONFIG["LAMBDA"]["BUCKET"]
S3_PROMPT: str = CONFIG["LAMBDA"]["PROMPT"]

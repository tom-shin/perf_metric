import boto3
from botocore.exceptions import NoCredentialsError

import json
from tqdm import tqdm

class S3TransferManager:
    def __init__(self):
        self.s3_client = boto3.client('s3')

    def upload(self, local_file, bucket, key):
        try:
            self.s3_client.upload_file(local_file, bucket, key)
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")
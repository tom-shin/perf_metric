from . import s3, S3_BUCKET
import json
import pandas as pd
from ast import literal_eval
from pathlib import Path
from io import StringIO


def is_file(file_path: str | Path) -> bool:
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=str(file_path))
        return True
    except s3.exceptions.ClientError as e:
        if e.response["Error"] == {"Code": "404", "Message": "Not Found"}:
            return False
        raise e


def read_file(file_path: str | Path, json_obj: bool) -> str | dict:
    text = (
        s3.get_object(Bucket=S3_BUCKET, Key=str(file_path))["Body"]
        .read()
        .decode("utf-8")
    )
    return json.loads(text) if json_obj else text


def read_csv(file_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(StringIO(read_file(file_path, False))).map(decode)


def decode(x):
    try:
        return literal_eval(x)
    except:
        return x

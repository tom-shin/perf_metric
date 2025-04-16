import json
import pandas as pd
from pathlib import Path


def is_file(file_path: str | Path) -> bool:
    return Path(file_path).is_file()


def read_file(file_path: str | Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_json(file_path: str | Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(file_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(file_path, encoding="utf-8")

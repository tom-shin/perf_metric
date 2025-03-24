from typing import overload
from pathlib import Path
from pandas import DataFrame
from . import LAMBDA_ENV

if LAMBDA_ENV:
    import trex_ai_chatbot_tools.lambda_env.file_handler as fh
else:
    import trex_ai_chatbot_tools.local_env.file_handler as fh


def is_file(file_path: str | Path) -> bool:
    return fh.is_file(file_path)


@overload
def read_file(file_path: str | Path, json_obj: True) -> dict: ...


@overload
def read_file(file_path: str | Path, json_obj: False) -> str: ...


def read_file(file_path: str | Path, json_obj: bool = False) -> str | dict:
    return fh.read_file(file_path, json_obj)


def read_csv(file_path: str | Path) -> DataFrame:
    return fh.read_csv(file_path)


def join_path(dir_path: str | Path, rel_path: str | Path):
    dp = Path(dir_path)
    rp = Path(rel_path)
    dp_res = dp.resolve()
    if dp == dp_res:
        return (dp / rp).resolve()
    else:
        return (dp / rp).resolve().relative_to(dp_res.parents[len(dp.parts) - 1])

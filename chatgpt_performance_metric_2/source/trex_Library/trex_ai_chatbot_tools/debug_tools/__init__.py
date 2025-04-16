from functools import wraps
from inspect import signature
from pandas import DataFrame
from .. import CONFIG

DEBUG_INPUT = CONFIG["DEBUG"]["INPUT"]
TEXTGEN_OUTPUT = CONFIG["DEBUG"]["TEXTGEN_OUTPUT"]
TEXTGEN_HISTORY = CONFIG["DEBUG"]["TEXTGEN_HISTORY"]
BULKGEN_CSV = CONFIG["DEBUG"]["BULKGEN_CSV"]
CHUNK_STATS = CONFIG["DEBUG"]["CHUNKING_STATISTICS"]
COSINE_MATRIX = CONFIG["DEBUG"]["COSINE_MATRIX"]


def safe_write(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except PermissionError:
                params = signature(func).bind(*args, **kwargs)
                params.apply_defaults()
                path = params.arguments.get("path")
                input(
                    f"Can't write to [{path}]. Please check writing permissions/if the file is closed, then press enter."
                )
        raise PermissionError(f"Reached maximum retries. Writing to [{path}] failed.")

    return wrapper


@safe_write
def write_csv(df: DataFrame, path: str):
    df.to_csv(path, encoding="utf-8", index=False)

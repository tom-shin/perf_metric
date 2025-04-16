import os
import json
import openai
import requests
from datetime import datetime, timezone
from ast import literal_eval
from numpy import dot
from numpy.linalg import norm
from functools import wraps

# Static parameters
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except:
    pass

dir_path = os.path.dirname(__file__)

API_KEY = os.getenv("OPENAI_API_KEY", "MISSINGKEY")
openai_client = openai.OpenAI(api_key=API_KEY)
SERVER_URL = os.getenv("SERVER_URL", "https://soc-developer.semiconductor.samsung.com/")
PROXY_SERVER_URL = os.getenv("PROXY_SERVER_URL", "http://ko.ai-studio-farm.com:22501")
CONNECTION_STRING = os.getenv("CONNECTION_STRING", "MISSINGSTRING")
USER_DB_ID = os.getenv("USER_DB", "default_db")
DEBUG_ACTIVE = bool(literal_eval(os.getenv("DEBUG_OPTIONS", "False")))
CONFIG_PATH = os.path.join(dir_path, "config.json")
LAMBDA_ENV = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

try:
    with open(CONFIG_PATH, "r") as f:
        CONFIG = json.load(f)
except:
    ValueError(f"Configuration file not found at '{CONFIG_PATH}'")

DB_COLS = [
    "ID",
    "data",
    "URL",
    "section",
    "metadata",
    "method",
    "embedTime",
    "token",
    "embedding",
]


class gpt_model:
    def __init__(self) -> None:
        self.ft_available = False
        try:
            ft_model_ID = CONFIG["FINE_TUNING"]["MODEL"]
            openai_client.models.retrieve(ft_model_ID)
            self.id = ft_model_ID
            self.ft_available = True
        except openai.NotFoundError:
            tg_model_ID = CONFIG["TEXTGEN"]["MODEL"]
            try:
                openai_client.models.retrieve(tg_model_ID)
                print(
                    f"Fine tuning model ID invalid: [{ft_model_ID}], using base model: [{tg_model_ID}]"
                )
                self.id = tg_model_ID
            except openai.NotFoundError:
                print(f"Invalid config - model not found :[{tg_model_ID}]")
                return

    def __str__(self) -> str:
        return self.id if self.ft_available else self.base_model

    def set_model(self, id):
        try:
            openai_client.models.retrieve(id)
        except openai.NotFoundError as e:
            print(f"Failed to set model: {e.body['message']}")
            return
        self.id = id
        self.ft_available = True
        CONFIG["FINE_TUNING"]["MODEL"] = id
        save_config_to_file()
        print(f"Fine tuning model set to model id [{id}]")

    base_model = CONFIG["TEXTGEN"]["MODEL"]


try:
    tg_model = gpt_model()
except openai.AuthenticationError:
    pass


def save_config_to_file() -> bool:
    if CONFIG == {}:
        print("CONFIG not set - cannot edit configuration.")
        return False
    with open(CONFIG_PATH, "w") as f:
        json.dump(dict(CONFIG), f, indent=4)
    return True


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return float(1 - dot(e1, e2) / (norm(e1) * norm(e2)))


def proxy_request(path: str, payload: dict) -> dict:
    response = requests.post(PROXY_SERVER_URL + "/" + path, json=payload)
    response.raise_for_status()
    return response.json()


def token_size(text: str) -> int:
    "Get token size of text according to textgen model"
    # return len(tiktoken.encoding_for_model(str(tg_model)).encode(text))
    return proxy_request("token-size", {"text": text, "model": str(tg_model)})[
        "token_count"
    ]


def check_chunker():
    token_size("text")
    if CONFIG["PARSER"]["MAX_TOKENS"] < CONFIG["PARSER"]["MIN_TOKENS"]:
        raise ValueError(
            f"max token value ({CONFIG['PARSER']['MAX_TOKENS']}) cannot be smaller than min token value ({CONFIG['PARSER']['MIN_TOKENS']})"
        )


def get_time() -> datetime:
    return datetime.now(tz=timezone.utc)


def str_time(no_space: bool = False) -> str:
    """
    Default format: YYYY/MM/DD hh/mm/ss:msms

    No space format: YYYYMMDD_hhmmss_msms
    """
    if no_space:
        form = "%Y%m%d_%H%M%S_%f"
    else:
        form = "%Y/%m/%d %H:%M:%S:%f"
    return get_time().strftime(form)


def json_return(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return json.loads(json.dumps(func(*args, **kwargs), default=str))

    return wrapper

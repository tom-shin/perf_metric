import os
import json
import openai
from ast import literal_eval
import tiktoken
import requests

# Static parameters
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except:
    pass

try:
    ONLINE = requests.get("https://www.google.com", timeout=1).status_code == 200
except:
    ONLINE = False

dir_path = os.path.dirname(__file__)

API_KEY = os.getenv("OPENAI_API_KEY", "MISSINGKEY")
openai_client = openai.OpenAI(api_key=API_KEY)
SERVER_URL = os.getenv("SERVER_URL", "https://soc-developer.semiconductor.samsung.com/")
CONNECTION_STRING = os.getenv("CONNECTION_STRING", "MISSINGSTRING")
DEBUG_ACTIVE = bool(literal_eval(os.getenv("DEBUG_OPTIONS", "False")))
CONFIG_PATH = os.path.join(dir_path, "config.json")
LAMBDA_ENV = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

GPT_INSTRUCTIONS = """You are a helpful assistant designed to help developers create applications using the ENN SDK (Exynos Neural Network Software Development Kit).
With each query from the user, a set of context data will be given.
Your primary role is to answer the query based on the provided context.
Context data may be in the form of a question-and-answer pair or excerpt from a specific section of the documentation.
You will help users with:
- Model Conversion: Providing instructions on converting TensorFlow Lite models to Neural Network Container (NNC) models using the ENN SDK service.
- Model Execution: Explaining how to execute NNC models using the ENN framework on Exynos platforms.
- API Usage: Offering detailed information on using the ENN framework APIs for managing tensors, buffers, and model execution processes.
- Support and Troubleshooting: Assisting with support queries by referencing the support matrix, FAQs, and sample codes. Guiding users on reporting bugs and accessing additional resources from the Exynos Developer Society web page.
Answer the query based on the given context information, general AI and/or SDK knowledge, and your role.
If the query is beyond the scope of the given context, respond with : 'We do not have the information you requested. If you wish to contact support about this inquiry, please send an email to seed.ai@samsung.com.'.
Be aware and forgiving of spelling and/or typing errors.
Keep in mind that system messages are invisible to the user. Only user and assistant messages are visible.
Remember to be concise, clear, and refer to specific sections of the documents when providing assistance."""

try:
    with open(CONFIG_PATH, "r") as f:
        CONFIG = json.load(f)
except:
    print(f"Configuration file not found at '{CONFIG_PATH}'")
    CONFIG = {}


# Error messages
def error_invalidkey(key: str = API_KEY):
    print(
        f"""Invalid OpenAI API key: [{key}].
You can find your API key at https://platform.openai.com/account/api-keys.
Set your API key using set_api_key(key: str) (only applied for this session) or editing the .env file (applied for all future sessions)."""
    )


def error_filenotfound(filetype: str, var: str):
    "Print: {filetype} file not found. Check the path {var} and try again."
    print(f"{filetype} file not found. Check the path {var} and try again.")


# Set function
def set_api_key(key: str) -> bool:
    global openai_client, API_KEY
    try:
        openai.OpenAI(api_key=key).models.list()
    except openai.AuthenticationError:
        error_invalidkey(key)
        return False
    API_KEY = key
    openai_client = openai.OpenAI(api_key=key)
    print(f"New OpenAI API Key set: ****{key[-4:]}")
    return True


class gpt_model:
    def __init__(self) -> None:
        self.ft_available = False
        try:
            ft_model_ID = CONFIG["FINE_TUNING"]["MODEL"]
            openai_client.models.retrieve(ft_model_ID)
            self.id = ft_model_ID
            self.ft_available = True
        except openai.AuthenticationError:
            error_invalidkey()
            return
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
        except openai.AuthenticationError:
            error_invalidkey()
            return
        except openai.NotFoundError as e:
            print(f"Failed to set model: {e.body['message']}")
            return
        self.id = id
        self.ft_available = True
        CONFIG["FINE_TUNING"]["MODEL"] = id
        save_config_to_file()
        print(f"Fine tuning model set to model id [{id}]")

    base_model = CONFIG["TEXTGEN"]["MODEL"]


if ONLINE:
    try:
        tg_model = gpt_model()
    except openai.AuthenticationError | openai.NotFoundError:
        pass


def save_config_to_file() -> bool:
    if CONFIG == {}:
        print("CONFIG not set - cannot edit configuration.")
        return False
    with open(CONFIG_PATH, "w") as f:
        json.dump(dict(CONFIG), f, indent=4)
    return True


def token_size(text: str) -> int:
    "Get token size of text according to textgen model"
    # size = len(tiktoken.encoding_for_model(str(tg_model)).encode(text))
    # if size != 0:
    #     print(f"{len(text)} -> {size} : {len(text)/size} char per token")
    return len(tiktoken.encoding_for_model(str(tg_model)).encode(text))


def chunker_config(
    model: str = str(tg_model),
    min_val: int = CONFIG["PARSER"]["MIN_TOKENS"],
    max_val: int = CONFIG["PARSER"]["MAX_TOKENS"],
):
    CONFIG["PARSER"]["MIN_TOKENS"] = min_val
    CONFIG["PARSER"]["MAX_TOKENS"] = max_val
    tg_model.set_model(model)
    save_config_to_file()


def check_chunker():
    try:
        token_size("text")
    except KeyError:
        raise KeyError(f"Invalid GPT model ID: [{str(tg_model)}]")
    if CONFIG["PARSER"]["MAX_TOKENS"] < CONFIG["PARSER"]["MIN_TOKENS"]:
        raise ValueError(
            f"max token value ({CONFIG['PARSER']['MAX_TOKENS']}) cannot be smaller than min token value ({CONFIG['PARSER']['MIN_TOKENS']})"
        )

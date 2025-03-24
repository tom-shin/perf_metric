from .. import dir_path, CONFIG
from ..navigation import read_file, join_path

GPT_INSTRUCTIONS = read_file(join_path(dir_path, CONFIG["TEXTGEN"]["PROMPT_PATH"]))

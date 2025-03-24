import re
from .. import CONFIG

MIN_TOKEN = CONFIG["PARSER"]["MIN_TOKENS"]
MAX_TOKEN = CONFIG["PARSER"]["MAX_TOKENS"]
SLICE_RATIO = CONFIG["PARSER"]["OVERMAX_SLICEAT"]

RE_TABCOUNT = re.compile(r"^(\t*)", flags=re.MULTILINE)
RE_NEWLINE = re.compile(r"\n", re.MULTILINE)
RE_URL = re.compile(r"\((?=[^\)]*\-)[^\)]+\)|[^a-z0-9\_\s]")
RE_SENTENCE = re.compile(r"\S.*?(?:\.|\?|\!)(?= |\n|\Z)")

import re
from .. import CONFIG

MIN_TOKEN = CONFIG["PARSER"]["MIN_TOKENS"]
MAX_TOKEN = CONFIG["PARSER"]["MAX_TOKENS"]
SLICE_RATIO = CONFIG["PARSER"]["OVERMAX_SLICEAT"]

RE_TABCOUNT = re.compile(r"^(\t*)", flags=re.MULTILINE)
RE_NEWLINE = re.compile(r"\n", re.MULTILINE)
RE_URL = re.compile(r"\((?=[^\)]*\-)[^\)]+\)|[^a-z0-9\_\s]")
RE_SENTENCE = re.compile(r"\S.*?(?:\.|\?|\!)(?= |\n|\Z)")
RE_JSON_BEGIN = re.compile(r"""(?:'\S*': |"\S*": )?{""")
RE_JSON_MIDDLE = re.compile(r"(?<!}), ")
RE_JSON_END = re.compile(r"}(?:, )?")
RE_SPACES = re.compile(r"\s")

import re

RE_HEADER = re.compile(r"^(#+)", flags=re.MULTILINE)
RE_CODEBLOCK = re.compile(r"(?:`[^`]+?`)|(?:``(?:[^`]`?)+?``)|(?:```[\s\S]*?```)")
RE_LIST_BQ = re.compile(
    r"(^[^\S\n]*(?:\*|\+|-|\d+\.).*|^[^\S\n]*>.*(?:\n(?!\Z|\n|\s*(?:\*|\+|-|\d+\.)).*)*)",
    re.MULTILINE,
)
RE_EMPTYLINE = re.compile(r"^\s*$")

RE_HEADERTAG = re.compile(r"h(\d)")
RE_FRAGMENT = re.compile(r"\((?=[^\)]*\-)[^\)]+\)|[^a-z0-9\_\s]")
RE_WEBURL = re.compile(r"^https?:\/\/")

RE_TABLE = re.compile(r"\|((?:[ \t]*-+[ \t]*\|)+)")
RE_MULTINEWLINE = re.compile(r"\n{3,}")
RE_MULTISPACE = re.compile(r" +")
RE_NEWLINE = re.compile(r"\s*\n(\s*)")


def clear_newline(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\\n", "\n").replace("\xa0", " ")
    text = RE_MULTINEWLINE.sub("\n\n", text)
    text = RE_MULTISPACE.sub(" ", text)
    text = RE_NEWLINE.sub(" ", text)
    return text.strip()


RE_TABLE_DICT = {}
RE_ROW_DICT = {}


def re_tables(cols: int) -> re.Pattern:
    if not RE_TABLE_DICT.get(cols):
        RE_TABLE_DICT[cols] = re.compile(
            r"(?:\|(?:.*?\|){" + str(cols) + r"}(?:\s*(?=\|)|\s*?))+"
        )
    return RE_TABLE_DICT[cols]


def re_rows(cols: int) -> re.Pattern:
    if not RE_ROW_DICT.get(cols):
        RE_ROW_DICT[cols] = re.compile(r"\|(?:.*?\|){" + str(cols) + r"}")
    return RE_ROW_DICT[cols]

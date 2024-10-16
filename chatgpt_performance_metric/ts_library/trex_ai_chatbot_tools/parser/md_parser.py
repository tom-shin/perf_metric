import re
from math import gcd
from markdown2 import markdown as md
from bs4 import Comment, BeautifulSoup as bs4
from trex_ai_chatbot_tools.parser.bs_parser import parse_bs


def parse_md(content: str) -> list[tuple[int, str]]:
    """Parse markdown text to remove unsupported HTML tags"""

    md_text, code_map = pre_processing(content)
    soup = html_conversion(md_text)
    soup = post_processing(soup, code_map)

    return parse_bs(soup)


def pre_processing(content: str) -> tuple[str, dict]:
    # Add space between paragraph / list
    md_text = re.sub(
        r"(^.+?$)\n(^[ \t]*(?:\*|\+|-|\d+\.))",
        r"\1\n\n\2",
        content,
        flags=re.MULTILINE,
    )

    # Add space in front of header
    md_text = re.sub(r"^#", r"\n#", md_text, flags=re.MULTILINE)

    # Convert CodeBlock
    code_map = {}
    code_index = 0
    for code_block in re.finditer(
        r"(?:`[^`]+?`)|(?:``(?:[^`]`?)+?``)|(?:```[\s\S]*?```)", md_text
    ):
        if code_block.group(0) not in [el[1] for el in code_map.items()]:
            code_map[f"code_{code_index}"] = code_block.group(0)
            md_text = md_text.replace(code_block.group(0), f"<code_{code_index} />")
            code_index += 1
    for key, value in code_map.items():
        code_map[key] = clean_code(value)

    return md_text, code_map


def html_conversion(md_text):
    # HTML Conversion
    html_text = md(md_text)
    # HTML Post-processing
    content_html = re.sub(r"</?em>", "_", html_text)
    # Soup Conversion
    soup = bs4(content_html, "html.parser")
    return soup


def post_processing(soup: bs4, code_map: dict):
    # Restore CodeBlock
    for key, code in code_map.items():
        # mdType.CodeBlock
        while soup.find(key):
            soup.find(key).replace_with(code)

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove unused HTML tags
    for html_tag in soup.find_all("a"):
        html_tag.unwrap()
    for html_tag in soup.find_all(["u", "img", "span", "div"]):
        html_tag.unwrap()

    # Parse used HTML tags
    for bold_tag in soup.find_all("strong"):
        parent = bold_tag.parent
        index = parent.contents.index(bold_tag)
        bold_tag.unwrap()
        parent.insert(index + 1, "**")
        parent.insert(index, "**")
    for br_tag in soup.find_all("br"):
        br_tag.replace_with("<br>")
    for nl_tag in soup.find_all(string="\n"):
        nl_tag.extract()

    soup.smooth()
    return soup


def clean_code(code_text: str) -> str:
    def clean_ws(code_lines: list[str], ws: str = "\t") -> list[str]:
        if len(ws) != 1:
            raise ValueError(f"Whitespace '{ws}' must be a single character")
        all_ws = True
        ws_lens = []
        for code_line in code_lines:
            ws_match = re.match(r"^(" + ws + ")+", code_line)
            if ws_match:
                if len(ws_match.group(0)) not in ws_lens:
                    ws_lens.append(len(ws_match.group(0)))
            else:
                all_ws = False
        if all_ws:
            code_lines = [ln[min(ws_lens) :] for ln in code_lines]
            ws_lens = [ws - min(ws_lens) for ws in ws_lens if ws != min(ws_lens)]
        if not ws_lens or ws == "\t":
            return code_lines
        min_ws = gcd(*ws_lens)
        code_lines = [
            re.compile(r"^(" + ws + r"{" + str(min_ws) + r"})+").sub(
                lambda x: "\t" * (len(x.group(0)) // min_ws),
                code_line,
            )
            for code_line in code_lines
        ]
        return code_lines

    lines = code_text.split("\n")
    if len(lines) == 1:
        return code_text
    code_lines = [re.sub(r"^>+", "", cl) for cl in lines[1:]]  # remove BlockQuote
    code_lines = [
        re.sub(r"^[ \t]+$", "", cl) for cl in code_lines
    ]  # reduce empty lines
    code_lines = [cl for cl in code_lines if cl]  # remove empty lines
    code_lines = clean_ws(code_lines, " ")
    code_lines = clean_ws(code_lines)
    code_lines = [re.sub(r"^(\t*) +", r"\1", cl) for cl in code_lines]
    return "\n".join([lines[0]] + code_lines)

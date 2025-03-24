import re
from bs4 import Comment, Tag, BeautifulSoup as bs4
from math import gcd
from markdown2 import markdown as md
from pathlib import Path
from . import (
    RE_HEADER,
    RE_CODEBLOCK,
    RE_LIST_BQ,
    RE_HEADERTAG,
    RE_FRAGMENT,
    RE_EMPTYLINE,
    RE_WEBURL,
    RE_NEWLINE,
)
from .bs_parser import parse_bs
from .mdBlock import mdBlock
from ..navigation import is_file, join_path


def parse_md(content: str, name: str, dir_path: Path) -> mdBlock:
    md_text, code_map = pre_processing(content)
    soup = html_conversion(md_text)
    soup = post_processing(soup, code_map, dir_path)
    return parse_bs(soup, name)


def pre_processing(content: str) -> tuple[str, dict]:
    # Add extra \n in front of header
    md_text = RE_HEADER.sub(r"\n\1", content)

    # Convert CodeBlock
    code_map = {}
    code_index = 0
    for code_block in RE_CODEBLOCK.finditer(md_text):
        if code_block.group(0) not in [el[1] for el in code_map.items()]:
            code_map[f"code_{code_index}"] = code_block.group(0)
            md_text = md_text.replace(code_block.group(0), f"<code_{code_index} />")
            code_index += 1
    for key, value in code_map.items():
        code_map[key] = process_code(value)

    # Add extra \n in front of list/blockquote
    md_text = RE_LIST_BQ.sub(r"\n\1", md_text)

    return md_text, code_map


def html_conversion(md_text):
    # HTML Conversion
    html_text = md(md_text)
    # HTML Post-processing
    html_text = re.sub(r"</?em>", "_", html_text)
    html_text = re.sub(r"</?strong>", "**", html_text)
    # Soup Conversion
    soup = bs4(html_text, "html.parser")
    return soup


def elevate_tag(soup: bs4, tag: Tag):
    parent = tag.parent
    if not tag.previous_sibling:
        parent.insert_before(tag)
        if not parent.find():
            parent.decompose()
        return
    if not tag.next_sibling:
        parent.insert_after(tag)
        return
    prev_soup = soup.new_tag(parent.name)
    for sibling in list(tag.previous_siblings):
        prev_soup.insert(0, sibling)
    next_soup = soup.new_tag(parent.name)
    for sibling in list(tag.next_siblings):
        next_soup.append(sibling)
    parent.replace_with(tag)
    tag.insert_before(prev_soup)
    tag.insert_after(next_soup)


def post_processing(soup: bs4, code_map: dict, dir_path: Path):
    # Restore CodeBlock
    for key, code in code_map.items():
        if code.find("\n") == -1:
            while soup.find(key):
                soup.find(key).replace_with(code)
            continue
        code_soup = soup.find(key)
        while code_soup:
            code_tag = soup.new_tag("c")
            code_tag.string = code
            if code_soup.parent.name == "li":
                code_soup.replace_with(code_tag)
                code_soup = soup.find(key)
                continue
            code_soup.replace_with(code_tag)
            elevate_tag(soup, code_tag)
            code_soup = soup.find(key)

    # Remove comments
    for comment in soup.find_all(string=lambda tag: isinstance(tag, Comment)):
        comment.extract()

    # Elevate nested <p> tags
    for p_tag in soup.find_all("p"):
        if p_tag.parent.name == "p":
            elevate_tag(soup, p_tag)

    # Assign url to headers
    h_names = []
    h_urls = {}

    for h_tag in soup.find_all(RE_HEADERTAG):
        if h_tag.parent.name != "[document]":
            h_tag.string = "#" * int(h_tag.name[1]) + " " + h_tag.text
            h_tag.name = "p"
            continue
        if h_tag.name not in h_names:
            h_names.append(h_tag.name)
        h_url = RE_FRAGMENT.sub("", h_tag.text.lower()).strip(" ").replace(" ", "-")
        if not h_urls.get(h_url):
            h_tag["url"] = h_url
            h_urls[h_url] = 1
        else:
            h_tag["url"] = f"{h_url}-{h_urls[h_url]}"
            h_urls[h_url] += 1

    for i, val in enumerate(sorted([int(h[1]) for h in h_names])):
        for h_tag in soup.find_all(f"h{val}"):
            h_tag.name = "h"
            h_tag["level"] = i + 1

    # Remove unused HTML tags
    for html_tag in soup.find_all(["u", "span", "div"]):
        html_tag.unwrap()

    # Parse used HTML tags
    for br_tag in soup.find_all("br"):
        br_tag.replace_with("<br>")
    for nl_tag in soup.find_all(string=RE_EMPTYLINE):
        nl_tag.extract()
    for img_tag in soup.find_all("img"):
        img_path = Path(img_tag.get("src", "").strip('\\"').lstrip("/"))
        if is_file(join_path(dir_path, img_path)):
            img_tag["dir"] = dir_path
            img_tag["src"] = img_path
            elevate_tag(soup, img_tag)
        else:
            print(f"IMAGE FILE NOT FOUND: {img_path}")
            img_tag.extract()
    for a_tag in soup.find_all("a"):
        if RE_WEBURL.match(a_tag["href"]):
            a_tag.string = f"[{a_tag.text}]({a_tag['href']})"
        a_tag.unwrap()
    for empty_tag in soup.find_all(
        lambda tag: tag.text.strip() == "" and not tag.find()
    ):
        if empty_tag.name in ["img", "hr"]:
            continue
        empty_tag.extract()

    soup.smooth()
    return soup


def process_code(code_text: str) -> str:
    def clean_ws(code_lines: list[str], ws: str = "\t") -> list[str]:
        if len(ws) != 1:
            raise ValueError(f"Whitespace '{ws}' must be a single character")
        all_ws = True
        ws_lens = []
        ws_regex = re.compile(r"^(" + ws + ")+")
        for code_line in code_lines:
            ws_match = ws_regex.match(code_line)
            if ws_match:
                if len(ws_match.group(0)) not in ws_lens:
                    ws_lens.append(len(ws_match.group(0)))
            elif all_ws:
                all_ws = False
        if all_ws:
            code_lines = [ln[min(ws_lens) :] for ln in code_lines]
            ws_lens = [ws - min(ws_lens) for ws in ws_lens if ws != min(ws_lens)]
        if not ws_lens or ws == "\t":
            return code_lines
        min_ws = gcd(*ws_lens)
        cl_regex = re.compile(r"^(" + ws + r"{" + str(min_ws) + r"})+")
        code_lines = [
            cl_regex.sub(
                lambda x: "\t" * (len(x.group(0)) // min_ws),
                code_line,
            )
            for code_line in code_lines
        ]
        return code_lines

    lines = code_text.split("\n")
    if len(lines) == 1:
        return code_text
    code_lines = [re.sub(r"^>+", "", cl) for cl in lines[1:]]  # remove > from .sh code
    code_lines = [RE_EMPTYLINE.sub("", cl) for cl in code_lines]  # reduce empty lines
    code_lines = [cl for cl in code_lines if cl]  # remove empty lines
    code_lines = clean_ws(code_lines, " ")
    code_lines = clean_ws(code_lines)
    code_lines = [re.sub(r"^(\t*) +", r"\1", cl) for cl in code_lines]
    return RE_NEWLINE.sub(r"\n\1", "\n".join([lines[0]] + code_lines))
    # return "\n".join([lines[0]] + code_lines)

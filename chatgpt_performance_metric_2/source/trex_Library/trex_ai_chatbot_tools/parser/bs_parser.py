from bs4 import BeautifulSoup as bs4
from . import RE_TABLE, RE_NEWLINE, clear_newline, re_tables, re_rows
from .mdBlock import mdType, mdBlock


def parse_bs(soup: bs4, name: str = "") -> mdBlock:
    headers = []
    data = []
    data_list = []
    for child in soup.children:
        if child.name == "h":
            child.attrs.update({"text": child.text})
            headers.append(child)
            data_list.append(data)
            data = []
        else:
            data.append(child)
    data_list.append(data)
    root_block = mdBlock(
        mdType.Header,
        {"level": 0, "text": name, "url": "", "content": parse_data(data_list[0])},
    )
    for i, header in enumerate(headers):
        root_block.append_block(
            mdBlock(
                mdType.Header,
                {
                    "level": header["level"],
                    "text": header["text"],
                    "content": parse_data(data_list[i + 1]),
                    "url": "#" + header["url"],
                },
            ),
            header["level"],
        )
    return root_block


def parse_data(child_list: list[bs4]) -> list[mdBlock]:
    if not child_list:
        return []
    result = []
    for child in child_list:
        if not child.name:  # NavigableString - <p> or <li>
            text = clear_newline(child.text)
            if text:
                result.append(
                    mdBlock(mdType.Paragraph, {"text": clear_newline(child.text)})
                )
            continue
        match child.name:
            case "p":  # Plaintext or table
                result.extend(process_plaintext(child))
            case "ul":  # Unordered list
                result.append(process_list(child))
            case "ol":  # Ordered list
                result.append(process_enumerate(child))
            case "c":  # CodeBlock
                result.append(mdBlock(mdType.CodeBlock, {"text": child.text}))
            case "hr":  # Line break - add new line
                result.append(mdBlock(mdType.LineBreak, {"text": ""}))
            case "blockquote":  # BlockQuote
                result.append(process_blockquote(child))
            case "img":  # Image
                result.append(process_image(child))
            case _:
                raise ValueError(f"Unrecognised HTML type: {child.name}")
    return result


def process_plaintext(child: bs4) -> list[mdBlock]:
    table_check = RE_TABLE.search(child.text)
    if not table_check:
        text = clear_newline(child.text)
        return [mdBlock(mdType.Paragraph, {"text": text})] if text else []
    p_list = []
    paragraph = child.text
    while table_check:
        colnum = table_check.group(1).count("|")
        table_match = re_tables(colnum).search(paragraph)
        if table_match.start():
            p_list.append(
                mdBlock(
                    mdType.Paragraph,
                    {"text": clear_newline(paragraph[: table_match.start()])},
                )
            )
        p_list.append(
            mdBlock(
                mdType.Table,
                {
                    "content": [
                        mdBlock(mdType.Row, {"text": clear_newline(el)})
                        for (el) in re_rows(colnum).findall(table_match.group(0))
                    ]
                },
            )
        )
        paragraph = clear_newline(paragraph[table_match.end() :])
        table_check = RE_TABLE.search(paragraph)
    if paragraph:
        p_list.append(mdBlock(mdType.Paragraph, {"text": paragraph}))
    return p_list


def process_list(child: bs4) -> mdBlock:
    result = []
    for li in child.children:
        if li.name != "li":
            li = [li]
        li_list = parse_data(li)
        li_list = dl_tab(li_list, "- ")
        result.append(mdBlock(mdType.ListItem, {"content": li_list}))
    return mdBlock(mdType.List, {"content": result})


def process_enumerate(child: bs4) -> mdBlock:
    result = []
    index = int(child.get("start", 1))
    for li in child.children:
        if li.name != "li":
            li = [li]
        li_list = parse_data(li)
        li_list = dl_tab(li_list, str(index) + ". ")
        result.append(mdBlock(mdType.ListItem, {"content": li_list}))
        index += 1
    return mdBlock(mdType.List, {"content": result})


def process_blockquote(child: bs4) -> mdBlock:
    bq_list = parse_data(child)
    bq_list = dl_quote(bq_list)
    return mdBlock(mdType.BlockQuote, {"content": bq_list})


def process_image(child: bs4) -> mdBlock:
    alt = child.get("alt", "")
    return mdBlock(
        mdType.Image,
        {
            "text": f"[Image: {alt if alt else child['src'].name}]",
            "alt": alt,
            "textpath": child["dir"],
            "imgpath": child["src"],
        },
    )


def dl_tab(dl: list[mdBlock], prefix: str = "") -> list[mdBlock]:
    for el in dl:
        if el.type == mdType.LineBreak:
            raise ValueError("Line break found in list")
        if el.ttype == str:
            if prefix:
                el.text = prefix + RE_NEWLINE.sub(r"\n\t\1", el.text)
                prefix = ""
            else:
                el.text = "\t" + RE_NEWLINE.sub(r"\n\t\1", el.text)
            continue
        if el.ttype == list:
            if prefix:
                el.content = dl_tab(el.content, prefix)
                prefix = ""
            else:
                el.content = dl_tab(el.content)
        continue
    if prefix:
        raise ValueError("No data to append")
    return dl


def dl_quote(dl: list[mdBlock]) -> list[mdBlock]:
    for el in dl:
        if el.type == mdType.LineBreak:
            raise ValueError("Line break found in blockquote")
        if el.ttype == str:
            if el.text[0] == ">":
                el.text = ">" + RE_NEWLINE.sub(r"\n>\1", el.text)
            else:
                el.text = "> " + RE_NEWLINE.sub(r"\n> \1", el.text)
            continue
        if el.ttype == list:
            el.content = dl_quote(el.content)
            continue
        el.text = dl_quote(el.content)
    return dl

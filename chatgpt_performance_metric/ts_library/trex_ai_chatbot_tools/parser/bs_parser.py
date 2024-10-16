import re
from bs4 import BeautifulSoup as bs4


def parse_bs(soup: bs4) -> list[tuple[int, str]]:
    if not hasattr(soup, "children"):
        return soup.text.strip("\n").strip(" ")

    child_list = []
    text_list = []
    for child in soup.children:
        if child.name == None:
            # Nothing but text - pass along (<p> recursion)
            if child.text not in ["", "\n"]:
                text_list.append(child.text.strip("\n").strip(" "))
            continue

        child_list, text_list = process_child(child, child_list, text_list)

    if text_list != []:
        child_list.append((0, "\n".join(text_list)))

    return child_list


def process_child(child, child_list, text_list):
    header = child.name

    # Add header to child_list
    if re.match(r"h\d", header):
        if text_list != []:
            child_list.append((0, "\n".join(text_list)))
            text_list = []
        child_list.append((int(header[1]), child.text))
        return child_list, text_list

    match header:
        case "hr":  # Line break - add new line
            text_list.append("")
        case "p":  # Plaintext or table
            text_list.append(process_plaintext(child))
        case "ul":  # mdType.List (unordered)
            text_list.extend(process_list(child))
        case "ol":  # mdType.List (ordered)
            text_list.extend(process_enumerate(child))
        case "blockquote":  # mdType.BlockQuote
            text_list.append(process_blockquote(child))
        case _:
            raise ValueError(f"Unrecognised HTML type: {child.name}")

    return child_list, text_list


def process_plaintext(child):
    paragraph = merge_bs(parse_bs(child))
    table_check = re.search(r"\|((?:[ \t]*-+[ \t]*\|)+)", paragraph)

    if not table_check:
        return paragraph

    len = table_check.group(1).count("|")
    return re.sub(
        r"(\|(?:.*?\|){" + str(len) + r"})(\s*)(?=\|(?:.*?\|){" + str(len) + r"})",
        r"\1\n",
        paragraph.replace("\n", ""),
        flags=re.MULTILINE,
    )


def process_list(child):
    result = []
    for line in child.children:
        if line.name != "li":
            continue

        result.append("- " + merge_bs(parse_bs(line)).replace("\n", "\n\t"))

    return result


def process_enumerate(child):
    result = []
    index = 1
    for line in child.children:
        if line.name != "li":
            continue

        result.append(
            str(index) + ". " + merge_bs(parse_bs(line)).replace("\n", "\n\t")
        )
        index += 1

    return result


def process_blockquote(child):
    return "> " + merge_bs(parse_bs(child)).replace("\n", "\n> ").replace(
        "\n> >", "\n>>"
    )


def merge_bs(child_list: list):
    if sum([el[0] for el in child_list]) > 0:
        raise ValueError("Header in list")
    return "\n".join([el[1] for el in child_list])

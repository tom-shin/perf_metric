import re
from . import check_chunker
from trex_ai_chatbot_tools.parser.md_parser import parse_md
from trex_ai_chatbot_tools.chunker import DataCell
from trex_ai_chatbot_tools.chunker.chunk_datacell import chunk_DC


def chunk_md(content: str, name: str = "", url: str = "") -> list[DataCell]:
    check_chunker()
    md_list = parse_md(content)
    page_cell = convert_to_DC(md_list, name, url)
    return chunk_DC(page_cell)


def convert_to_DC(parse_list: list[tuple[int, str]], name: str = "", url: str = ""):
    """Given the contents of a webpage, return a list of DataCell with chunked content"""
    # Initialise page cell
    page_cell = DataCell(
        [(0, name)] if name else [],  # Page name
        url,  # Page URL
        parse_list[0][1] if parse_list[0][0] == 0 else "",  # Pre-header content
    )
    header = []  # List of headers assigned to section at each level
    header_count = {}  # Dictionary of headers for url pointer
    header_dict = {
        val: i for i, val in enumerate(sorted(set([h[0] for h in parse_list])))
    }  # Trim down unused header levels (#+)
    if parse_list[0][0] == 0:
        parse_list = parse_list[1:]
    i = 0
    while i < len(parse_list):
        # Set header list (for Section)
        if len(header) >= header_dict[parse_list[i][0]]:
            header = header[: header_dict[parse_list[i][0]] - 1]
        if header_dict[parse_list[i][0]] > 0:
            header.append(parse_list[i][1])
        # Identify URL pointer
        url_header = (
            re.sub(
                r"\((?=[^\)]*\-)[^\)]+\)|[^a-z0-9\_\s]",
                "",
                parse_list[i][1].lower(),
            )
            .strip(" ")
            .replace(" ", "-")
        )
        if header_count.get(parse_list[i][1]) is None:
            header_count[parse_list[i][1]] = 1
        else:
            url_header += "-" + str(header_count[parse_list[i][1]])
            header_count[parse_list[i][1]] += 1
        sec_header = (header_dict[parse_list[i][0]], parse_list[i][1])
        if parse_list[i + 1][0] == 0:  # Data exists
            data = parse_list[i + 1][1]
            i += 1
        else:
            data = ""
        # Create DataCell
        page_cell.appendCell(
            DataCell([sec_header] if sec_header else [], url + "#" + url_header, data),
            len(header) - 1,
        )
        i += 1
    return page_cell

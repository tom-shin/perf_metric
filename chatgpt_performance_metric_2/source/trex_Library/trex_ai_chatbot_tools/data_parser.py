from . import check_chunker
from pathlib import Path
from .parser.mdBlock import mdType
from .parser.md_parser import parse_md
from .chunker.datacell import DataCell
from .chunker.chunker import chunk_cell
from .metadata.metadata import get_metadata


def chunk_md(
    content: str, name: str = "", url: str = "", dir_path: Path = Path()
) -> list[dict]:
    if not content:
        return []
    check_chunker()
    root_cell = parse_md(content, name, dir_path)
    chunks = chunk_cell(root_cell)
    get_metadata(chunks)
    result = [export_cell(cell) for cell in chunks]
    if url:
        result = [cell.update({"URL": url + cell["URL"]}) or cell for cell in result]
    else:
        [cell.pop("URL") for cell in result]
    return result


def export_cell(cell: DataCell) -> dict:
    while cell.data and cell.data[0].type == mdType.LineBreak:
        cell.data.pop(0)
    while cell.data and cell.data[-1].type == mdType.LineBreak:
        cell.data.pop()
    return {
        "URL": cell.url,
        "token": cell.token,
        "section": cell.section,
        "content": [el.export() for el in cell.data],
        "data": (f"Section: {cell.header}\n" if cell.header else "")
        + (f"Content:\n{cell.string.strip()}" if cell.string.strip() else ""),
        "metadata": cell.metadata,
    }

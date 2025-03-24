from . import MAX_TOKEN
from .datacell import DataCell
from .text_list import split_text


def get_data_list(root_cell: DataCell) -> list[DataCell]:
    if not root_cell.hasData:
        return []  # DX
    if root_cell.token <= MAX_TOKEN:
        return [root_cell]  # D-, D0
    return split_text(root_cell)  # D+

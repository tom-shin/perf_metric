from . import MIN_TOKEN, MAX_TOKEN
from .datacell import DataCell, block_to_cell, get_section
from .data_list import get_data_list
from ..parser.mdBlock import mdBlock


def chunk_cell(root_block: mdBlock) -> list[DataCell]:
    def merge_check(cell1: DataCell, cell2: DataCell) -> bool:
        return (cell1.token < MIN_TOKEN or cell2.token < MIN_TOKEN) and (
            cell1.token + cell2.token <= MAX_TOKEN
        )

    if root_block.token < MIN_TOKEN:
        return [block_to_cell(root_block)]

    section, block = get_section(root_block)
    data_list = get_data_list(DataCell(section, block.content, block.url))
    if not block.subheader:  # CX
        return data_list
    child_list = get_child_list(block.subheader, section)

    # Combine data_list & child_list
    if not data_list:  # DX: no data - append header
        if len(child_list) == 1:
            child_list[0].url = root_block.url
        return child_list
    if len(data_list) == 1:
        if len(child_list) == 1 and merge_check(
            data_list[0], child_list[0]
        ):  # [D, C] to DC
            return [data_list[0] + child_list[0]]
        if (
            len(block.subheader) == 1
            and block.subheader[0].content == child_list[0].data
            and merge_check(data_list[0], child_list[0])
        ):  # D, [D, C] to DD, C
            child_list[0] = data_list[0] + child_list[0]
            return child_list
    return data_list + child_list


def get_child_list(
    subheaders: list[mdBlock], section: list[tuple[int, str]]
) -> list[DataCell]:
    def additive_check() -> bool:
        return len(chunk_list) <= 1 and block.token < MAX_TOKEN

    if not subheaders:
        return []
    # split C+ and merge C-/C0
    result: list[DataCell] = []
    additive_list: list[DataCell] = []
    for block in subheaders:
        chunk_list = [
            (setattr(cell, "section", section + cell.section) or cell)
            for cell in chunk_cell(block)
        ]
        if additive_check():
            additive_list.extend(chunk_list)
        else:
            result.extend(dnc_merge(additive_list))
            result.extend(chunk_list)
            additive_list = []
    if additive_list:
        result.extend(dnc_merge(additive_list))
    return result


def dnc_merge(merge_list: list[DataCell]) -> list[DataCell]:
    def merge_check(cells: list[DataCell]) -> bool:
        return sum([el.token for el in cells]) <= MAX_TOKEN

    if len(merge_list) < 2:  # Nothing to merge
        return merge_list
    min_i = (lambda x: x.index(min(x)))([el.token for el in merge_list])
    if merge_list[min_i].token >= MIN_TOKEN:  # No [-] children
        return merge_list

    if min_i == 0:  # First el
        if merge_check(merge_list[:2]):
            merge_list[:2] = [merge_list[0] + merge_list[1]]
            return dnc_merge(merge_list)
        else:
            return merge_list[:1] + dnc_merge(merge_list[1:])
    if min_i == len(merge_list) - 1:  # Last el
        if merge_check(merge_list[-2:]):
            merge_list[-2:] = [merge_list[-2] + merge_list[-1]]
            return dnc_merge(merge_list)
        else:
            return dnc_merge(merge_list[:-1]) + merge_list[-1:]
    # Compare neighbours
    if merge_list[min_i - 1].token <= merge_list[min_i + 1].token:
        min_i -= 1
    if merge_check(merge_list[min_i : min_i + 1]):
        merge_list[min_i : min_i + 2] = [merge_list[min_i] + merge_list[min_i + 1]]
        return dnc_merge(merge_list)
    return dnc_merge(merge_list[: min_i + 1]) + dnc_merge(merge_list[min_i + 1 :])

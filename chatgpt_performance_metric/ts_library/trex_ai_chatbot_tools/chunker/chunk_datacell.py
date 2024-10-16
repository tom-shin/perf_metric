from .. import token_size
from . import DataCell, MIN_TOKEN, MAX_TOKEN
from .data_list import get_data_list


def chunk_DC(root_cell: DataCell) -> list[DataCell]:
    def merge_check(cell1: DataCell, cell2: DataCell) -> bool:
        return (cell1.size < MIN_TOKEN or cell2.size < MIN_TOKEN) and (
            cell1.size + cell2.size <= MAX_TOKEN
        )

    if root_cell.size < MIN_TOKEN:
        root_cell.merge_children()
        return [root_cell]

    child_cells = root_cell.splitChild()
    data_list = get_data_list(root_cell)
    if not child_cells:  # CX
        return data_list
    child_list = get_child_list(child_cells)

    # Combine data_list & child_list
    if not data_list:  # DX: no data - append header
        for child in child_list:
            child.addSection(root_cell.section, root_cell.length)
        if len(child_list) == 1:
            child_list[0].url = root_cell.url
        return child_list
    if len(data_list) == 1:
        if len(child_list) == 1 and merge_check(data_list[0], child_list[0]):
            # [D, C] to DC
            return [data_list[0].merge_child(child_list[0])]
        if (
            len(child_cells) == 1
            and child_cells[0].data == child_list[0].data
            and merge_check(data_list[0], child_list[0])
        ):  # D, [D, C] to DD, C
            data_list[0] = data_list[0].merge_child(child_list[0])
            child_list.pop(0)
    header_len = token_size(root_cell.getHeader())
    for child in child_list:
        child.addSection(root_cell.section, header_len)
    return data_list + child_list


def get_child_list(child: list[DataCell]) -> list[DataCell]:
    if not child:
        return []
    # split C+ and merge C-/C0
    result: list[DataCell] = []
    additive_list: list[DataCell] = []
    for cell in child:
        chunk_list = chunk_DC(cell)
        if len(chunk_list) > 1 or cell.size - cell.length > MAX_TOKEN:  # Non-additive
            result += dnc_merge(additive_list)
            result += chunk_list
            additive_list = []
        else:  # Additive
            additive_list += chunk_list
    if additive_list:
        result += dnc_merge(additive_list)
    return result


def dnc_merge(merge_list: list[DataCell]) -> list[DataCell]:
    def merge_check(cells: list[DataCell]) -> bool:
        return sum([el.size for el in cells]) <= MAX_TOKEN

    if len(merge_list) < 2:  # Nothing to merge
        return merge_list
    min_i = (lambda x: x.index(min(x)))([el.size for el in merge_list])
    if merge_list[min_i].size >= MIN_TOKEN:  # No [-] children
        return merge_list

    if min_i == 0:  # First el
        if merge_check(merge_list[:2]):
            merge_list[0].merge_sibling(merge_list[1])
            return dnc_merge([merge_list[0]] + merge_list[2:])
        else:
            return merge_list[:1] + dnc_merge(merge_list[1:])
    if min_i == len(merge_list) - 1:  # Last el
        if merge_check(merge_list[-2:]):
            merge_list[-2].merge_sibling(merge_list[-1])
            return dnc_merge(merge_list[:-2] + [merge_list[-2]])
        else:
            return dnc_merge(merge_list[:-1]) + merge_list[-1:]
    # Compare neighbours
    if merge_list[min_i - 1].size <= merge_list[min_i + 1].size:
        min_i -= 1
    if merge_check(merge_list[min_i : min_i + 1]):
        merge_list[min_i].merge_sibling(merge_list[min_i + 1])
        merge_list.pop(min_i + 1)
        return dnc_merge(merge_list)
    return dnc_merge(merge_list[: min_i + 1]) + dnc_merge(merge_list[min_i + 1 :])

from . import SLICE_RATIO, MIN_TOKEN, MAX_TOKEN
from .datacell import DataCell
from .split_text import deque_to_value, split_row, split_code, split_plaintext
from ..parser.mdBlock import mdType, mdBlock
from bisect import bisect_left as bl
from collections import deque


def get_data_list(cell: DataCell) -> list[DataCell]:
    if not cell.hasData:
        return []  # DX
    if cell.token <= MAX_TOKEN:
        return [cell]  # D-, D0
    # D+
    divnum = (cell.token * 2) // (MIN_TOKEN + MAX_TOKEN) + 1
    if divnum == 1:
        return cell
    split_points = deque(len(cell) * (i + 1) // divnum for i in range(divnum - 1))
    slice_range = (len(cell) * SLICE_RATIO) // (divnum * 2)
    split_list = split_data(deque(cell.data), split_points, slice_range)
    if len(split_list) != divnum:
        raise SystemError("D+ cell split failed")
    return [DataCell(cell.section, sdl, cell.url) for sdl in split_list]


def get_slice_i(points: list[int], n: int) -> int:
    if n <= points[0]:
        return 1
    if n > points[-1]:
        return len(points)
    i = bl(points, n)
    return i + int(n - points[i - 1] > points[i] - n)


def split_data(dl: deque[mdBlock], sps: deque[int], sr: int) -> list[list[mdBlock]]:
    result = []
    chunk = []

    split_bps = []
    prev_bp = 0

    sp = sps.popleft()
    while dl:
        block = dl.popleft()
        curr_bp = prev_bp + len(block) + int(bool(dl))
        if split_bps:
            if curr_bp < sp + sr:
                split_bps.append(curr_bp)
                chunk.append(block)
                prev_bp = curr_bp
                continue
            else:
                sbpi = len(chunk) - len(split_bps) + get_slice_i(split_bps, sp)
                result.append(chunk[:sbpi])
                chunk = chunk[sbpi:]
                split_bps = []
                if sps:
                    sp = sps.popleft()
                else:
                    chunk.append(block)
                    break
        if curr_bp < sp - sr:
            chunk.append(block)
        elif curr_bp < sp + sr:
            split_bps.append(curr_bp)
            chunk.append(block)
        else:
            block_sps, sp = deque_to_value(sps, sp, curr_bp - sr)
            split_list = split_mdBlock(
                block, deque(sp - prev_bp for sp in block_sps), sr
            )
            result.append(chunk + split_list[:1] if split_list[0] else chunk)
            result.extend([[sb] for sb in split_list[1:-1]])
            chunk = split_list[-1:] if split_list[-1] else []
            if not sp:
                break
            if abs(sp - curr_bp) < sr:
                split_bps.append(curr_bp)
        prev_bp = curr_bp
    if chunk or dl:
        result.append(chunk + list(dl))
    return result


def split_mdBlock(block: mdBlock, sps: deque[int], sr: int) -> list[mdBlock]:
    if block.ttype == list:
        return [
            mdBlock(block.type, {"content": sd})
            for sd in split_data(deque(block.content), sps, sr)
        ]
    match block.type:
        case mdType.Row:
            return split_row(block, sps)
        case mdType.CodeBlock:
            return split_code(block, sps, sr)
        case mdType.Paragraph:
            return split_plaintext(block, sps, sr)
        case _:
            raise ValueError(f"block split undefined for type {block.type}")

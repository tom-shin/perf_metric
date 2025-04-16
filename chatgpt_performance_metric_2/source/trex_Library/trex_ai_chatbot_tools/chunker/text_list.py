from bisect import bisect_left as bl
from itertools import accumulate
from . import SLICE_RATIO, MIN_TOKEN, MAX_TOKEN, RE_TABCOUNT, RE_NEWLINE, RE_SENTENCE
from .datacell import DataCell
from ..parser.mdBlock import mdType, mdBlock


def split_text(cell: DataCell, data: list[mdBlock] = None) -> list[DataCell]:
    if data == None:
        data = cell.data
        divnum = int(cell.token * 2 / (MIN_TOKEN + MAX_TOKEN)) + 1
        if divnum == 1:
            return cell
        divsize = int(len(cell) / divnum)
    else:
        divnum = (
            int(sum(block.token for block in data) * 2 / (MIN_TOKEN + MAX_TOKEN)) + 1
        )
        if divnum == 1:
            return [DataCell(cell.section, data, cell.url)]
        divsize = int(sum(len(str(block)) for block in data) / divnum)

    sps = list(range(divsize, divsize * divnum, divsize))
    slice_range = int(divsize * SLICE_RATIO / 2)
    split_list = split_data(data, sps, slice_range)
    if len(split_list) != divnum:
        raise SystemError("D+ cell split failed")
    return [DataCell(cell.section, sdl, cell.url) for sdl in split_list]


def split_data(dl: list[mdBlock], sps: list[int], sr: int) -> list[list[mdBlock]]:
    def split_start(sp: int, block: mdBlock) -> bool:
        if len(block) / 2 > sp:
            return True
        return False

    def sd_to_result(split_data: list[mdBlock]) -> None:
        nonlocal bpi, block_sps
        if len(split_data) - len(block_sps) > 2:
            raise ValueError("Split failed")
        if len(split_data) == 1:
            if split_start(block_sps[0], split_data[0]):
                result.append(dl[bpi:start])
                bpi = start
            else:
                result.append(dl[bpi : start + 1])
                bpi = start + 1
            return
        dl[block_i : start + 1] = split_data
        bps[block_i : start + 1] = [
            (bps[block_i - 1] if block_i > 0 else 0) + bp
            for bp in list(
                accumulate(
                    [len(sb) for sb in split_data], lambda prev, curr: prev + curr + 1
                )
            )
        ]
        result.append(dl[bpi:start] + [split_data[0]])
        result.extend([[sb] for sb in split_data[1:-1]])
        bpi = start + len(split_data) - 1

    bps = list(accumulate([len(el) for el in dl], lambda prev, curr: prev + curr + 1))
    result = []
    bpi = 0
    spi = 0
    while spi < len(sps):
        start = bpi + bl(bps[bpi:], sps[spi] - sr)
        end = bpi + bl(bps[bpi:], sps[spi] + sr)
        if end > start:
            if end == start + 1:  # One break point in split range: return break point
                sbpi = end
            else:  # Multiple break points in split range
                sbpi = bps.index(get_closest_bp(sps[spi], bps[start:end])) + 1
            result.append(dl[bpi:sbpi])
            bpi = sbpi
            spi += 1
            continue
        block_i = start
        block = dl[block_i]
        from_spi = spi
        while spi < len(sps) - 1 and sps[spi + 1] < bps[start] - sr:
            spi += 1
        spi += 1
        block_sps = [
            sp - (bps[start - 1] if start > 0 else 0) for sp in sps[from_spi:spi]
        ]
        if block.ttype == list:
            sd_to_result(
                [
                    mdBlock(block.type, {"content": sdl})
                    for sdl in split_data(block.content, block_sps, sr)
                ]
            )
            continue
        match block.type:
            case mdType.Row:
                if spi != from_spi + 1:
                    raise ValueError(
                        "Row is too long - check table or increase MIN_TOKEN"
                    )
                if split_start(block_sps[0], block):
                    result.append(dl[bpi:start])
                    bpi = start
                else:
                    result.append(dl[bpi : start + 1])
                    bpi = start + 1
            case mdType.CodeBlock:
                sd_to_result(split_code(block, block_sps, sr))
            case mdType.Paragraph:
                sd_to_result(split_plaintext(block, block_sps))
            case _:
                raise ValueError(f"block split undefined for type {block.type}")
    result.append(dl[bpi:])
    return result


def get_closest_bp(sp: int, bp_list: list[int]) -> int:
    bpi = bl(bp_list, sp)
    if bpi == 0:
        return bp_list[0]
    if bpi == len(bp_list):
        return bp_list[bpi - 1]
    bp1 = bp_list[bpi - 1]
    bp2 = bp_list[bpi]
    return bp2 if bp2 - sp < sp - bp1 else bp1


def get_ranked_bp(sp: int, rbps: list[tuple[int, int]]) -> int:
    bps = [bp[0] for bp in rbps]
    min_rank_bps = [rbp[1] for rbp in rbps if rbp[0] == min(bps)]
    if len(min_rank_bps) == 1:
        return min_rank_bps[0]
    return get_closest_bp(sp, min_rank_bps)


def get_ranked_list(text: str) -> list[tuple[int, int]]:
    result = []
    for iter in RE_TABCOUNT.finditer(text):
        result.append(
            (
                len(iter.group(1)),
                iter.start(),
            )
        )
    result += [(min([bp[0] for bp in result]), len(text))]
    return result


def split_code(code_block: mdBlock, sps: list[int], sr: int):
    code_bps = []
    code_list = get_ranked_list(code_block.text)
    # Instantiate division lists
    desc_bps = (
        [code_list[0]]
        + [
            next
            for prev, curr, next in zip(code_list[:-2], code_list[1:-1], code_list[2:])
            if prev[0] > curr[0] >= next[0]
        ]
        + [code_list[-1]]
    )
    asc_bps = None
    cl_list = None
    for sp in sps:
        # Division 1: split at end of function bracket (lower \t)
        bp_in_range = [bp for bp in desc_bps if sp - sr < bp[1] < sp + sr]
        if len(bp_in_range) > 0:
            code_bps.append(get_ranked_bp(sp, bp_in_range))
            continue
        # Division 2: split at beginning of function bracket (higher \t)
        if asc_bps == None:
            asc_bps = (
                [code_list[0]]
                + [
                    prev
                    for prev, curr in zip(code_list[1:-1], code_list[2:])
                    if curr[0] > prev[0]
                ]
                + [code_list[-1]]
            )
        bp_in_range = [bp for bp in asc_bps if sp - sr < bp[1] < sp + sr]
        if len(bp_in_range) > 0:
            code_bps.append(get_ranked_bp(sp, bp_in_range))
            continue
        # Division 3: split at new line
        if cl_list == None:
            cl_list = [0] + [nl.end() for nl in RE_NEWLINE.finditer(code_block.text)]
        code_bps.append(get_closest_bp(sp, cl_list))
    return [
        mdBlock(mdType.CodeBlock, {"text": code_block.text[start:end].strip("\n")})
        for start, end in zip([0] + code_bps, code_bps + [len(code_block.text)])
        if start != end
    ]


def split_plaintext(text_block: mdBlock, sps: list[int]):
    sentences = [s.end() for s in RE_SENTENCE.finditer(text_block.text)] + [
        len(text_block.text)
    ]
    text_bps = [get_closest_bp(sp, sentences) for sp in sps]
    return [
        mdBlock(mdType.Paragraph, {"text": text})
        for text in [
            text_block.text[start:end].strip()
            for start, end in zip([0] + text_bps, text_bps + [len(text_block.text)])
            if start != end
        ]
    ]

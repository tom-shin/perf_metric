import re
from bisect import bisect_left as bl
from itertools import accumulate
from . import mdType, DataCell, MDTYPE_PATTERN, SLICE_RATIO, MIN_TOKEN, MAX_TOKEN


def get_data_list(root_cell: DataCell) -> list[DataCell]:
    if not root_cell.hasData():  # DX
        return []
    if root_cell.length <= MAX_TOKEN:  # D-, D0
        return [root_cell]
    # D+
    # TODO: Replace this line with semantic division
    divnum = int(root_cell.length * 2 / (MIN_TOKEN + MAX_TOKEN)) + 1
    textlen = len(root_cell.data)
    # sps: Get slice points - divide text into equal sizes of (text size)/(max token) pieces
    sps = []
    for i in range(divnum - 1):
        sps.append(int(textlen / divnum * (i + 1)))
    # blocks: Divide .md to blocks
    slice_range = int(textlen / divnum * SLICE_RATIO / 2)
    data_bp = get_bps(root_cell.data, sps, slice_range)
    # Split data by data_bp
    data_list = []
    prev = 0
    for i, bp in enumerate(data_bp):
        data_list.append(
            DataCell(
                root_cell.section,
                root_cell.url,
                root_cell.data[prev:bp],
                split_data=i + 1,
            )
        )
        prev = bp
    data_list.append(
        DataCell(
            root_cell.section,
            root_cell.url,
            root_cell.data[prev:],
            split_data=len(data_bp) + 1,
        )
    )
    return data_list


def get_closest_bp(sp: int, bp_list: list) -> int:
    """
    Input:
    - sp: int (slice point)
    - bp_list: list[int] (list of breakpoints)

    Output:
    - int (breakpoint closest to slice poiint)
    """
    bpi = bl(bp_list, sp)
    if bpi == 0:
        return bp_list[0]
    if bpi == len(bp_list):
        return bp_list[bpi - 1]
    bp1 = bp_list[bpi - 1]
    bp2 = bp_list[bpi]
    return bp2 if bp2 - sp < sp - bp1 else bp1


def get_bps(text: str, sps: list, sr: int):
    """
    Input:
    - blocks: list (divided parts of the original text)
    - bps: list (int positions of the beginning of each block (shares i with blocks))
    - sps: list (int positions of intended slice points (shares i with output))
    - sr: int (range to search for bp around each sp)

    Output:
    - list[int] (list of filtered break points from bps + split blocks)
    """
    # Split text - get block/bp lists
    text_iter = re.finditer(MDTYPE_PATTERN, text, re.MULTILINE)
    blocks = []
    bps = []
    for block in text_iter:
        bps.append(block.start())
        # TODO: Check for simpler method
        for block_type, data in block.groupdict().items():
            if data:
                blocks.append([getattr(mdType, block_type), data])
                break
    bps.append(len(text))
    # Filter bps
    result = []
    i = 0
    while i < len(sps):
        start = bl(bps, sps[i] - sr)
        end = bl(bps, sps[i] + sr)
        match end - start:
            case 0:  # No break points in split range: divide further
                offset = bps[start - 1]
                div_sps = [sps[i] - offset]
                while i < len(sps) - 1 and sps[i + 1] + sr < bps[start]:
                    i += 1
                    div_sps.append(sps[i] - offset)
                div_bps = block_division(div_sps, sr, blocks[start - 1])
                for div_bp in div_bps:
                    result.append(div_bp + offset)
            case 1:  # One break point in split range: return break point
                result.append(bps[start])
            case _:  # Multiple break points in split range
                result.append(get_closest_bp(sps[i], bps[start:end]))
        i += 1
    return result


def block_division(sps: list[int], sr: int, block: tuple[mdType, str]) -> list:
    """
    Input:
    - sps: list[int] (slice points)
    - sr: int (range from slice point to search for break point)
    - block: tuple[mdType, str]
        - [0]: mdType of block
        - [1]: text of block

    Output:
    - list[int] (list of breakpoints for block)
    """

    def get_ranked_list(regex: str, text: str) -> list[tuple[int, int]]:
        """
        Get list of ranked breakpoints from text

        Input:
        - regex: str (regular expression to identify breakpoints)
        - text: str (text to divide by regex)

        Output:
        - list[tuple[int, int]] (list of ranked breakpoints)
            - int 1 (position of breakpoint)
            - int 2 (rank of breakpoint)
        """
        result = []
        for iter in re.finditer(regex, text, re.MULTILINE):
            result.append(
                (
                    iter.start(),
                    len(iter.group(1)),
                )
            )
        result += [(len(text), min([bp[1] for bp in result]))]
        return result

    def get_ranked_bp(sp: int, rlist: list[tuple[int, int]]) -> int:
        """
        get_closest_bp() applied to a ranked breakpoint list

        Input:
        - rlist: list[tuple[int, int]] (list of ranked breakpoints)
            - int 1 (position of breakpoint)
            - int 2 (rank of breakpoint)
        - sp: int (slice point)

        Output:
        - int (position of highest ranked (lowest int) breakpoint positioned closest to slice point)
        """
        bp_in_range = [bp for bp in rlist if bp[1] == min(bp[1] for bp in rlist)]
        if len(bp_in_range) == 1:
            return bp_in_range[0][0]
        return get_closest_bp(sp, [bp[0] for bp in bp_in_range])

    def recursive_division(
        block: str, regex: str, sps: list[int], sr: int, offset: int = 1
    ) -> list[int]:
        """
        Recursively divide block of list/blockquote

        Input:
        - block: str (text of list/blockquote block)
        - regex: str (regular expression identifying list/blockquote element)
            - capture group 1 indicates list/blockquote indicator (+,-,*,/d,>)
            - capture group 2 indicates the bulk of element
        - sps: list[int] (list of slice points adjusted to the scope of block)
        - offset: int = 1 (amount of offset to apply to all lines except first line - used to trim \t)

        Output:
        - list[int] (list of recursively found breakpoints)
        """
        # Remove indicator (convert to offset)
        rec_match = re.match(regex, block)
        rec_offset = len(rec_match.group(1))
        rec_content = rec_match.group(2)
        # Trim \t from each new line
        rec_list = re.split(r"\n", rec_content, flags=re.MULTILINE)
        rec_list = [rec_list[0]] + [rline[offset:] for rline in rec_list[1:]]
        rec_content = "\n".join(rec_list)
        # Prepare inputs for get_bps
        rec_len = list(
            accumulate(
                [len(el) for el in rec_list], lambda total, value: total + value + 1
            )
        )
        rec_sps = [sp - rec_offset - bl(rec_len, sp) * offset for sp in sps]
        rec_sr = int(sr * len(rec_content) / len(block))
        # Get bps
        result = [
            bp + rec_offset + bl(rec_len, bp - 1) * offset
            for bp in get_bps(rec_content, rec_sps, rec_sr)
        ]  # bp - 1 ∵ bp: beginning of block, rec_len: position of \n
        if result[0] == rec_offset + rec_content.find("\n") + 1:
            result[0] = 0
        return result

    div_bps = []
    match block[0]:
        case mdType.CodeBlock:
            code_list = get_ranked_list(r"^(\t*)", block[1])
            # Instantiate division lists
            desc_bps = (
                [code_list[0]]
                + [
                    next
                    for prev, curr, next in zip(
                        code_list[:-2], code_list[1:-1], code_list[2:]
                    )
                    if curr[1] < prev[1]
                ]
                + [code_list[-1]]
            )
            asc_bps = None
            cl_list = None
            for sp in sps:
                # Division 1: split at end of function bracket (lower \t)
                bp_in_range = [bp for bp in desc_bps if sp - sr < bp[0] < sp + sr]
                if len(bp_in_range) > 0:
                    div_bps.append(get_ranked_bp(sp, bp_in_range))
                    continue
                # Division 2: split at beginning of function bracket (higher \t)
                if asc_bps == None:
                    asc_bps = (
                        [code_list[0]]
                        + [
                            curr
                            for prev, curr in zip(code_list[:-1], code_list[:-1])
                            if curr[1] > prev[1]
                        ]
                        + [code_list[-1]]
                    )
                bp_in_range = [bp for bp in asc_bps if sp - sr < bp[0] < sp + sr]
                if len(bp_in_range) > 0:
                    div_bps.append(get_ranked_bp(sp, bp_in_range))
                    continue
                # Division 3: split at new line
                if cl_list == None:
                    cl_list = [0] + [nl.end() for nl in re.finditer(r"\n", block[1])]
                div_bps.append(get_closest_bp(sp, cl_list))
        case mdType.List:
            el_bps = get_ranked_list(
                r"^(\t*)(?:\*|\+|-|\d+\.)\s*(.*?(?:\n[ \t]+.*|$)+)", block[1]
            )
            el_bp0 = None
            i = 0
            while i < len(sps):
                bp_in_range = [bp for bp in el_bps if sps[i] - sr < bp[0] < sps[i] + sr]
                # Breakpoint exists in split range
                if len(bp_in_range) > 0:
                    div_bps.append(get_ranked_bp(sps[i], bp_in_range))
                    i += 1
                    continue
                # Breakpoint not found - recursive division
                if el_bp0 == None:
                    el_bp0 = [bp[0] for bp in el_bps]
                el_i = bl(el_bp0, sps[i])
                el_sps = [
                    sp - el_bp0[el_i - 1] for sp in sps[i : bl(sps, el_bp0[el_i] - sr)]
                ]
                el_div_bps = [
                    bp + el_bp0[el_i - 1]
                    for bp in recursive_division(
                        block[1][el_bp0[el_i - 1] : el_bp0[el_i]],
                        r"^(\t*(?:\*|\+|-|\d+\.)\s*)([\s\S]*)",
                        el_sps,
                        sr,
                    )
                ]
                div_bps += el_div_bps
                i += len(el_sps)
        case mdType.BlockQuote:
            bq_list = get_ranked_list(r"^(>*)", block[1])
            bq_bps = (
                [bq_list[0]]
                + [
                    next
                    for curr, next in zip(bq_list[:-1], bq_list[1:])
                    if next[1] < curr[1]
                ]
                + [bq_list[-1]]
            )
            bq_bp0 = None
            i = 0
            while i < len(sps):
                bp_in_range = [bp for bp in bq_bps if sps[i] - sr < bp[0] < sps[i] + sr]
                # Breakpoint exists in split range
                if len(bp_in_range) > 0:
                    div_bps.append(get_ranked_bp(sp, bp_in_range))
                    i += 1
                    continue
                # Breakpoint not found - recursive division
                if bq_bp0 == None:
                    bq_bp0 = [bp[0] for bp in bq_bps]
                bq_i = bl(bq_bp0, sps[i])
                bq_sps = [
                    sp - bq_bp0[bq_i - 1] for sp in sps[i : bl(sps, bq_bp0[bq_i] - sr)]
                ]
                bq_div_bps = [
                    bp + bq_bp0[bq_i - 1]
                    for bp in recursive_division(
                        block[1][bq_bp0[bq_i - 1] : bq_bp0[bq_i]],
                        r"^(\t*>\s*)([\s\S]*)",
                        bq_sps,
                        sr,
                    )
                ]
                div_bps += bq_div_bps
                i += len(bq_sps)
        case mdType.Table:
            row_list = [el.end() for el in re.finditer(r"\n", block[1])] + [
                len(block[1])
            ]
            for sp in sps:
                div_bps.append(get_closest_bp(sp, row_list))
        case mdType.Paragraph:
            sentence_list = [
                el.end() for el in re.finditer(r"(?:\.|\!|\?) ", block[1])
            ] + [len(block[1])]
            for sp in sps:
                div_bps.append(get_closest_bp(sp, sentence_list))
    return div_bps

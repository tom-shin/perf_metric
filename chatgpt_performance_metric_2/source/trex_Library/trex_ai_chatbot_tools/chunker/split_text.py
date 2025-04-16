from bisect import bisect_left as bl
from collections import defaultdict, deque
from . import (
    RE_TABCOUNT,
    RE_NEWLINE,
    RE_SENTENCE,
    RE_JSON_BEGIN,
    RE_JSON_MIDDLE,
    RE_JSON_END,
    RE_SPACES,
)
from ..parser.mdBlock import mdType, mdBlock


def deque_to_value(dq: deque[int], start: int, end: int) -> tuple[list[int], int]:
    result = []
    value = start
    while value and value <= end:
        result.append(value)
        if dq:
            value = dq.popleft()
        else:
            value = None
    return result, value


def get_closest_point(points: list[int], n: int) -> int:
    i = bl(points, n)
    if i == 0:
        return points[0]
    if i == len(points):
        return points[i - 1]
    return min(points[i - 1], points[i], key=lambda p: abs(p - n))


def split_row(row_block: mdBlock, sps: deque[int]):
    if len(sps) == 1:
        if sps[0] < len(row_block) / 2:
            return [[], row_block]
        return [row_block, []]
    raise ValueError("Row is too long - check table or increase MIN_TOKEN")


def split_code(code_block: mdBlock, sps: deque[int], sr: int):
    def get_ranked_bp(sp: int, rbps: list[tuple[int, int]]) -> int:
        bps = [bp[0] for bp in rbps]
        min_rank_bps = [rbp[1] for rbp in rbps if rbp[0] == min(bps)]
        if len(min_rank_bps) == 1:
            return min_rank_bps[0]
        return get_closest_point(min_rank_bps, sp)

    def append_cbp(cbp: int):
        nonlocal sp
        code_bps.append(cbp)
        if sps:
            sp = sps.popleft()
        else:
            sp = None

    code_bps = []
    code_list = []
    for iter in RE_TABCOUNT.finditer(code_block.text):
        code_list.append(
            (
                len(iter.group(1)),
                iter.start(),
            )
        )
    code_list += [(min([bp[0] for bp in code_list]), len(code_block.text))]
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
    sp = sps.popleft()
    while sp:
        # Division 1: split at end of function bracket (lower \t)
        bp_in_range = [bp for bp in desc_bps if sp - sr < bp[1] < sp + sr]
        if bp_in_range:
            append_cbp(get_ranked_bp(sp, bp_in_range))
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
        if bp_in_range:
            append_cbp(get_ranked_bp(sp, bp_in_range))
            continue
        # Division 3: split at new line
        if cl_list == None:
            cl_list = (
                [0]
                + [nl.end() for nl in RE_NEWLINE.finditer(code_block.text)]
                + [len(code_block)]
            )
        cbp = get_closest_point(cl_list, sp)
        if abs(cbp - sp) < sr:
            append_cbp(cbp)
            continue
        # All code divisions falied: move to text division
        cbpi = bl(cl_list, sp)
        block_sps, sp = deque_to_value(sps, sp, cl_list[cbpi])
        code_bps.extend(
            get_final_bps(
                code_block.text[cl_list[cbpi - 1] : cl_list[cbpi] - 1],
                block_sps,
                sr,
                cl_list[cbpi - 1],
            )
        )
    return [
        mdBlock(mdType.CodeBlock, {"text": code_block.text[start:end].strip("\n")})
        for start, end in zip([0] + code_bps, code_bps + [len(code_block.text)])
    ]


def split_plaintext(text_block: mdBlock, sps: deque[int], sr: int):
    text_bps = get_final_bps(text_block.text, sps, sr)
    return [
        mdBlock(mdType.Paragraph, {"text": text})
        for text in [
            text_block.text[start:end].strip()
            for start, end in zip([0] + text_bps, text_bps + [len(text_block.text)])
        ]
    ]


def get_final_bps(text: str, sps: list[int], sr: int, offset: int = 0) -> list[int]:
    def count(char_list: list[chr]):
        return sum([text.count(char) for char in char_list])

    def fill_slots(bps: list[int]) -> list[int]:
        if not bps:
            return
        for _ in range(len(pending)):
            sp = pending.popleft()
            bp = get_closest_point(bps, sp)
            if abs(sp - bp) < sr:
                slots[sp] = bp
            else:
                pending.append(sp)

    def speech_fill():
        fill_slots([s.end() for s in RE_SENTENCE.finditer(text)])

    def json_fill():
        all_bps = (
            [(el.start(), 1) for el in RE_JSON_BEGIN.finditer(text)]
            + [(el.end(), 0) for el in RE_JSON_MIDDLE.finditer(text)]
            + [(el.end(), -1) for el in RE_JSON_END.finditer(text)]
        )
        all_bps.sort()
        start_bps = defaultdict(list)
        mid_bps = defaultdict(list)
        end_bps = defaultdict(list)
        depth = 0
        for bp, delta in all_bps:
            match delta:
                case 1:
                    start_bps[depth].append(bp)
                case 0:
                    mid_bps[depth].append(bp)
                case -1:
                    end_bps[depth].append(bp)
            depth += delta
        for bps in [end_bps, start_bps, mid_bps]:
            for i in sorted(bps.keys()):
                fill_slots(bps[i])
                if not pending:
                    return

    pending = deque(sp - offset for sp in sps)
    slots = {}
    priorities = {
        speech_fill: count([".", "!", "?"]),
        json_fill: count(["{", "}", "'"]),
    }
    for fill in sorted(priorities.keys(), key=lambda k: priorities[k], reverse=True):
        fill()
        if not pending:
            return [bp + offset for bp in slots.values()]
    # All split algorithms failed: split by spaces
    spaces = [0] + [s.end() for s in RE_SPACES.finditer(text)] + [len(text)]
    fill_slots(spaces)
    if pending:
        # Split by spaces failed: raise error
        bpi = bl(spaces, pending[0])
        raise ValueError(
            f"Text contains unbreakable word: [{text[spaces[bpi-1] : spaces[bpi]].strip()}]"
        )
    return [bp + offset for bp in slots.values()]

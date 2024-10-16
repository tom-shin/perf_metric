from enum import Enum
from .. import CONFIG, token_size

MIN_TOKEN = CONFIG["PARSER"]["MIN_TOKENS"]
MAX_TOKEN = CONFIG["PARSER"]["MAX_TOKENS"]
SLICE_RATIO = CONFIG["PARSER"]["OVERMAX_SLICEAT"]


class mdType(Enum):
    CodeBlock = "CodeBlock"
    List = "List"
    Table = "Table"
    BlockQuote = "BlockQuote"
    Paragraph = "Paragraph"


block_dict = {
    mdType.CodeBlock: r"^[ \t]*```[\s\S]*?```$",
    mdType.List: r"^[ \t]*(?:\*|\+|-|\d+\.) .*?(?:\n[ \t]*(?:\*|\+|-|\d+\.) .*|\n[ \t]+.*|$)+",
    mdType.Table: r"(?:[ \t]*\|.*?(?:\n(?=[ \t]*\|)|$))+",
    mdType.BlockQuote: r"[ \t]*>(?:.*?(?:\n[ \t]*>|$))+",
    mdType.Paragraph: r"^.+?$",
}

pattern_list = []
for mdtype, regex in block_dict.items():
    pattern_list.append(f"(?P<{mdtype.name}>{regex})")
MDTYPE_PATTERN = "|".join(pattern_list)


class DataCell:
    def __init__(
        self,
        section: list[tuple[int, str]],
        url: str,
        data: str,
        child: list["DataCell"] = [],
        length: int = -1,
        size: int = -1,
        split_data: int = 0,
    ) -> None:
        self.section = section
        self.url = url
        self.data = process_input(data)
        self.child = child
        self.split_data = split_data
        if length == -1:
            self.length = token_size(self.getHeader() + "\n" + self.data)
        else:
            self.length = length
        if size == -1:
            if child:
                self.size = self.length + sum([cell.length for cell in child])
            else:
                self.size = self.length
        else:
            self.size = size

    def __repr__(self) -> str:
        if self.hasChild():
            return f"({self.length}, {self.size-self.length}:{self.child})"
        return f"{self.length}"

    def __str__(self) -> str:
        result = "\n".join([x for x in [self.getHeader(), self.data] if x])
        if self.hasChild():
            for cell in self.child:
                result += "\n" + str(cell)
        return result.strip("\n")

    def hasData(self) -> bool:
        return bool(self.data)

    def hasChild(self) -> bool:
        return bool(self.child)

    def appendCell(self, new_cell: "DataCell", levels: int) -> "DataCell":
        if levels < 0:
            raise ValueError(
                f"Incorrect level value: {levels}, must be int of 1 or above"
            )
        elif levels == 0:
            self.size += new_cell.length
            if self.hasChild():
                self.child.append(new_cell)
            else:
                self.child = [new_cell]
        else:
            if self.child != None:
                self.size += new_cell.length
                self.child[-1].appendCell(new_cell, levels - 1)
            else:
                raise ValueError(
                    f"Incorrect level value: {levels}, new_cell: {new_cell} -> {self}"
                )
        return self

    def getHeader(self) -> str:
        return "\n".join(
            [
                (("#" * pair[0] + " ") if pair[0] else "") + pair[1]
                for pair in self.section
            ]
        )

    def addSection(self, section: list[tuple[int, str]], size: int = -1) -> "DataCell":
        if self.section:
            self.section = section + self.section
        else:
            self.section = section
        if size == -1:
            size = token_size("\n".join([pair[1] for pair in section]))
        self.length += size
        self.size += size
        return self

    def splitChild(self) -> list["DataCell"]:
        child_list = self.child
        self.size = self.length
        self.child = []
        return child_list

    def merge_children(self) -> "DataCell":
        if not self.child:
            return
        self.length = self.size
        for child in self.child:
            child.merge_children()
        self.data = "\n".join(
            x
            for x in (
                [self.data]
                + [
                    text
                    for child in self.child
                    for text in [child.getHeader(), child.data]
                ]
            )
            if x
        )
        self.child = []
        return self

    def merge_child(
        self, child_cell: "DataCell", child_url: bool = False
    ) -> "DataCell":
        self.size += child_cell.size
        self.length = self.size
        if self.data:  # H, DHD
            self.data = "\n".join(
                [x for x in [self.data, child_cell.getHeader(), child_cell.data] if x]
            )
        else:  # HH, D
            if child_url:
                self.url = child_cell.url
            self.section += child_cell.section
            self.data = child_cell.data
        return self

    def merge_sibling(self, next_cell: "DataCell") -> "DataCell":
        self.size += next_cell.size
        self.length = self.size
        self.data = "\n".join(
            [
                x
                for x in [
                    self.getHeader(),
                    self.data,
                    next_cell.getHeader(),
                    next_cell.data,
                ]
                if x
            ]
        )
        self.section = []
        return self


def process_input(input: str) -> str:
    in_str = input.replace("\r\n", "\n").replace("\\n", "\n").replace("\xa0", " ")
    while in_str != in_str.replace("\n\n\n", "\n\n"):
        in_str = in_str.replace("\n\n\n", "\n\n")
    while in_str != in_str.replace("  ", " "):
        in_str = in_str.replace("  ", " ")
    while in_str != in_str.replace(" \n", "\n"):
        in_str = in_str.replace(" \n", "\n")
    if in_str.count("\n\n") * 2 == in_str.count("\n"):
        in_str = in_str.replace("\n\n", "\n")
    return in_str.strip("\n").strip("***").strip("\n")

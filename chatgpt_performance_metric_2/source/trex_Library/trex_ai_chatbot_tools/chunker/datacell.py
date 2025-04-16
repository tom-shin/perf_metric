from . import RE_NEWLINE
from .. import token_size
from ..parser.mdBlock import mdType, mdBlock


class DataCell:
    def __init__(
        self,
        section: list[tuple[int, str]],
        data: list[mdBlock],
        url: str = "",
        metadata: dict = None,
    ) -> None:
        self._section = section
        self.url: str = url
        self._data: list[mdBlock] = data
        self.metadata: dict = metadata if metadata else {}

        self._len: int = None
        self._toklen: int = None
        self._header: str = None
        self._string: str = None

    def __repr__(self) -> str:
        return f"{len(self)}({self.token})"

    def __str__(self) -> str:
        return "\n".join([x for x in [self.header, self.string] if x])

    def __len__(self) -> int:
        return self.length

    def __add__(self, addcell: "DataCell") -> "DataCell":
        new_sec = []
        for i in range(min(len(self.section), len(addcell.section))):
            if self.section[i] == addcell.section[i]:
                new_sec.append(self.section[i])
            else:
                break
        sec_self = self.section[len(new_sec) :]
        sec_add = addcell.section[len(new_sec) :]

        new_url = new_sec[-1][2] if sec_self else self.url
        new_data = self.data
        if sec_self:
            new_data.insert(
                0,
                mdBlock(
                    mdType.Paragraph,
                    {
                        "text": "\n".join(
                            [
                                (("#" * pair[0] + " ") if pair[0] else "") + pair[1]
                                for pair in sec_self
                            ]
                        )
                    },
                ),
            )
        if sec_add:
            new_data.append(
                mdBlock(
                    mdType.Paragraph,
                    {
                        "text": "\n".join(
                            [
                                (("#" * pair[0] + " ") if pair[0] else "") + pair[1]
                                for pair in sec_add
                            ]
                        )
                    },
                )
            )
        new_data += addcell.data
        return DataCell(new_sec, new_data, new_url)

    @property
    def section(self) -> list[tuple[int, str]]:
        return self._section

    @section.setter
    def section(self, new_section):
        self._section = new_section
        self._len = None
        self._toklen = None
        self._header = None

    @property
    def hasSection(self) -> bool:
        return bool(self._section)

    @property
    def header(self) -> str:
        if self._header == None:
            self._header = "\n".join(
                [
                    (("#" * pair[0] + " ") if pair[0] else "") + pair[1]
                    for pair in self._section
                ]
            )
        return self._header

    @property
    def string(self) -> str:
        if self._string == None:
            self._string = "\n".join([str(block) for block in self._data])
        return self._string

    @property
    def data(self) -> list[mdBlock]:
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data
        self._len = None
        self._toklen = None
        self._string = None

    @property
    def hasData(self) -> bool:
        return bool(self._data)

    @property
    def length(self) -> int:
        if self._len == None:
            self._len = sum([len(block) + 1 for block in self._data]) - int(
                bool(self._data)
            )
        return self._len

    @property
    def token(self) -> int:
        if self._toklen == None:
            self._toklen = token_size(str(self)[len(self.header) + 1 :])
        return self._toklen

    def struct(self) -> None:
        def block_print(block: mdBlock) -> str:
            result = f"{block.type} ({block.token})"
            for subblock in block.content + (
                block.subheader if block.type == mdType.Header else []
            ):
                result += "\n └─ " + RE_NEWLINE.sub("\n    ", block_print(subblock))
            return result

        for block in self.data:
            print(block_print(block))


def get_section(block: mdBlock) -> tuple[list, mdBlock]:
    if block.content or len(block.subheader) != 1:
        return [(block.level, block.text, getattr(block, "url", ""))], block
    sec, blk = get_section(block.subheader[0])
    return [(block.level, block.text, getattr(block, "url", ""))] + sec, blk


def block_to_cell(block: mdBlock) -> DataCell:
    section, data = get_section(block)
    return DataCell(section, data.content + data.subheader, getattr(block, "url", ""))

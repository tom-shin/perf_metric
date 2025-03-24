from pathlib import Path
from .. import token_size


class mdTypeObj:
    def __init__(self, name, ttype, req, opt={}) -> None:
        self._name: str = name
        self._type: type = ttype
        self._req: dict = req
        self._opt: dict = opt

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> type:
        return self._type

    @property
    def req(self) -> dict:
        return self._req

    @property
    def opt(self) -> dict:
        return self._opt


class mdType(mdTypeObj):
    Header = mdTypeObj(
        "Header",
        str,
        {"level": int, "text": str, "content": list, "url": str},
        {"subheader": list},
    )
    Paragraph = mdTypeObj("Paragraph", str, {"text": str})
    CodeBlock = mdTypeObj("CodeBlock", str, {"text": str})
    LineBreak = mdTypeObj("LineBreak", str, {"text": str})
    List = mdTypeObj("List", list, {"content": list})
    ListItem = mdTypeObj("ListItem", list, {"content": list})
    BlockQuote = mdTypeObj("BlockQuote", list, {"content": list})
    Table = mdTypeObj("Table", list, {"content": list})
    Row = mdTypeObj("Row", str, {"text": str})
    Image = mdTypeObj(
        "Image", str, {"text": str, "alt": str, "textpath": Path, "imgpath": Path}
    )
    Link = mdTypeObj("Link", dict, {"Link": str})


class mdBlock:
    def __init__(self, md_type: mdTypeObj, content: dict) -> None:
        self.type: mdType = md_type
        self.ttype: type = md_type.type
        self._text: str = None
        self._content: list[mdBlock] = []
        self.imgIndex: list[tuple] = []
        if md_type == mdType.Header:
            self.level: int
            self.url: str
            self._subheader: list[mdBlock] = []
        if md_type == mdType.Image:
            self.alt: str
            self.textpath: Path
            self.imgpath: Path
        self._string: str = None
        self._len: int = None
        self._toklen: int = None
        for attr, atype in self.type.req.items():
            try:
                content[attr]
            except:
                raise ValueError(f"{self.type} block is missing attribute [{attr}]")
            if not isinstance(content[attr], atype):
                raise TypeError(f"Incorrect type for [{attr}]: {type(content[attr])}")
            setattr(self, attr, content[attr])
        for attr, atype in self.type.opt.items():
            try:
                if isinstance(content[attr], atype):
                    setattr(self, attr, content[attr])
                else:
                    print(f"Incorrect type for [{attr}]: {type(content[attr])}")
            except:
                pass

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self._string = None
        self._len = None
        self._toklen = None

    @property
    def content(self) -> list["mdBlock"]:
        return self._content

    @content.setter
    def content(self, content: list["mdBlock"]):
        self._content = content
        self.imgIndex = []
        for i, block in enumerate(content):
            if block.type == mdType.Image:
                self.imgIndex.append((i,))
            elif block.imgIndex:
                self.imgIndex.extend((i, *el) for el in block.imgIndex)
        self._string = None
        self._len = None
        self._toklen = None

    def __repr__(self) -> str:
        if self.type == mdType.Header:
            return (
                f"{self.token}:"
                + (f"({self.content})" if self.content else "")
                + (f"{self.subheader}" if self.subheader else "")
            )
        if self.ttype == str:
            return f"{self.type}: {str(self)}"
        if self.ttype == list:
            return f"{self.type}: {[str(child) for child in self.content]}"
        return f"{self.type}"

    def __str__(self) -> str:
        if self._string == None:
            if self.type == mdType.Header:
                self._string = "\n".join(
                    [("#" * self.level + " " if self.level else "") + self.text]
                    + [str(block) for block in self.content + self.subheader]
                )
            elif self.ttype == str:
                self._string = str(self.text)
            elif self.ttype == list:
                self._string = "\n".join([str(block) for block in self.content])
            else:
                self._string = ""
        return self._string

    def __len__(self) -> int:
        if self._len == None:
            if self.type == mdType.Header:
                c_len = sum(
                    [
                        len(block) + 1
                        for block in self.content + self.subheader
                        if block.ttype == str
                    ]
                )
                c_len -= int(bool(c_len))
                self._len = (
                    (self.level + 1 if self.level else 0) + len(self.text)
                ) + c_len
            elif self.ttype == str:
                self._len = len(self.text)
            elif self.ttype == list:
                self._len = sum([len(block) + 1 for block in self.content]) - int(
                    bool(self.content)
                )
            else:
                self._len = 0
        return self._len

    @property
    def token(self) -> int:
        if self._toklen == None:
            if str(self):
                self._toklen = token_size(str(self))
            else:
                self._toklen = 0
        return self._toklen

    @property
    def subheader(self) -> list["mdBlock"]:
        try:
            return self._subheader
        except AttributeError:
            if self.type != mdType.Header:
                raise AttributeError("Subheader only exists for Header type mdBlocks")
            raise SystemError("Header block missing subheader attribute")

    def append_block(self, add_block: "mdBlock", level: int):
        if add_block.type != mdType.Header:
            raise ValueError(
                f"Incorrect block type: {add_block.type}, only mdType.Header blocks can be subheaders"
            )
        if level < 1:
            raise ValueError(
                f"Incorrect level value: {level}, must be int of 1 or above"
            )
        if level == 1:
            self.subheader.append(add_block)
        else:
            if self.subheader:
                self.subheader[-1].append_block(add_block, level - 1)
            else:
                raise ValueError(
                    f"Incorrect level value: {level}, add_block: {add_block} -> {self}"
                )

    def export(self) -> dict:
        return {
            "type": str(self.type),
            "text": self.text,
            "content": [el.export() for el in self.content],
        }

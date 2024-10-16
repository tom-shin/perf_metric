from .. import token_size


class DataCell:
    def __init__(
        self,
        header: str,
        url: str,
        data: str,
        child: list["DataCell"] = [],
    ) -> None:
        self.header = header
        self.url = url
        self.data = process_input(data)
        self.length = token_size(self.data)
        if child:
            self.size = self.length + sum([cell.length for cell in child])
            self.child = child
        else:
            self.size = self.length
            self.child = []

    def hasChild(self) -> bool:
        return self.child != None

    def __repr__(self) -> str:
        if self.hasChild():
            return f"({self.length}, {self.size-self.length}:{self.child})"
        return f"{self.length}"

    def __str__(self) -> str:
        result = self.header if self.data == "" else self.header + "\n" + self.data
        if self.hasChild():
            for cell in self.child:
                result += "\n" + str(cell)
        return result.strip("\n")

    def appendCell(self, new_cell: "DataCell", levels: int) -> None:
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

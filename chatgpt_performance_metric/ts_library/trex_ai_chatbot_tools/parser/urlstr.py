class urlstr:
    def __init__(self, text) -> None:
        if isinstance(text, str):
            self.text = [(text, "")]
        elif isinstance(text, list):
            self.text = text
        else:
            raise TypeError("Incorrect type for text list")

    def __str__(self) -> str:
        return "".join([el[0] for el in self.text])

    def __len__(self) -> int:
        return sum([len(el[0]) for el in self.text])

    def leading_pointer(self) -> bool:
        return bool(self.text[0][1])

    def trailing_pointer(self) -> bool:
        return bool(self.text[-1][1])

    def __add__(self, addtext) -> "urlstr":
        if isinstance(addtext, str):
            if self.trailing_pointer():
                self.text += [(addtext, "")]
            else:
                self.text[-1] = (self.text[-1][0] + addtext, "")
        elif isinstance(addtext, tuple):
            self.text += [addtext]
        elif isinstance(addtext, urlstr):
            if not self.trailing_pointer() and not addtext.leading_pointer():
                self.text[-1] = (self.text[-1][0] + addtext.text[0][0], "")
                self.text += addtext.text[1:]
            else:
                self.text += addtext.text
        else:
            raise TypeError("Cannot concatenate non-string object")
        return self

    def __radd__(self, addtext) -> "urlstr":
        if isinstance(addtext, str):
            if self.leading_pointer():
                self.text = [(addtext, "")] + self.text
            else:
                self.text[0] = (addtext + self.text[0][0], "")
        elif isinstance(addtext, tuple):
            self.text = [addtext] + self.text
        elif isinstance(addtext, urlstr):
            return addtext.__add__(self)
        else:
            raise TypeError("Cannot concatenate non-string object")
        return self

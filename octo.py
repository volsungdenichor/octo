import abc
import copy
from typing import Any

Attrs = dict[str, str]


class Node(abc.ABC):
    @abc.abstractmethod
    def render(self, level: int) -> list[str]: ...

    def __str__(self):
        return "\n".join(self.render(0))


class VoidElement(Node):
    def __init__(self, name, attrs: Attrs):
        self._name = name
        self._attrs = attrs

    def render(self, level: int) -> list[str]:
        indent = "  " * level
        attrs = " ".join(f'{k}="{v}"' for k, v in self._attrs.items())
        if attrs:
            attrs = " " + attrs
        return [f"{indent}<{self._name}{attrs}>"]


class TextNode(Node):
    def __init__(self, value: Any):
        self._value = str(value)

    def render(self, level: int) -> list[str]:
        return [self._value]


class Element(Node):
    def __init__(self, name: str, attrs: Attrs, children: list[Node]):
        assert all(isinstance(ch, Node) for ch in children)

        self._name = name
        self._attrs = attrs
        self._children = children

    def render(self, level: int) -> list[str]:
        indent = "  " * level
        attrs = " ".join(f'{k}="{v}"' for k, v in self._attrs.items())
        if attrs:
            attrs = " " + attrs
        if len(self._children) == 0:
            return [f"{indent}<{self._name}{attrs}/>"]
        if len(self._children) == 1:
            child_result = self._children[0].render(level + 1)
            if len(child_result) == 1:
                return [
                    f"{indent}<{self._name}{attrs}>{child_result[0].strip()}</{self._name}>"
                ]
        result = [f"{indent}<{self._name}{attrs}>"]
        for child in self._children:
            result.extend(child.render(level + 1))
        result.append(f"{indent}</{self._name}>")
        return result


class ElementBuilder:
    def __init__(self, name, attrs: Attrs = None):
        self._name = name
        self._attrs = attrs or dict()

    @staticmethod
    def get_children(*children) -> list[Node]:
        valid_children = []
        for child in children:
            if isinstance(child, Node):
                valid_children.append(child)
            else:
                valid_children.extend(child)
        return valid_children

    def parse_arg(self, arg: str) -> Attrs:
        result: Attrs = dict(self._attrs)
        items = [a.strip() for a in arg.split(".")]
        id_item = next((i for i in items if i.startswith("#")), None)
        if id_item:
            result["id"] = id_item[1:]
        classes = list(i.strip() for i in result.get("class", "").split())
        for item in items:
            if not item.startswith("#") and item not in classes:
                classes.append(item)
        if classes:
            result["class"] = " ".join(c for c in classes if c)

        return result

    def __getitem__(self, arg: str):
        return ElementBuilder(self._name, self.parse_arg(arg))

    def __call__(self, *args):
        attrs: Attrs = self._attrs
        children: list[Node] = []
        if args:
            if isinstance(args[0], dict):
                attrs = self._attrs | args[0]
                children = self.get_children(*args[1:])
            else:
                children = self.get_children(*args)

        return Element(self._name, attrs, children)


class VoidElementBuilder:
    def __init__(self, name: str):
        self._name = name

    def __call__(self, attrs: Attrs):
        return VoidElement(self._name, attrs)


html = ElementBuilder("html")
head = ElementBuilder("head")
body = ElementBuilder("body")
div = ElementBuilder("div")
span = ElementBuilder("span")
p = ElementBuilder("p")
table = ElementBuilder("table")
tr = ElementBuilder("tr")
td = ElementBuilder("td")
th = ElementBuilder("th")
ul = ElementBuilder("ul")
ol = ElementBuilder("ol")
li = ElementBuilder("li")
h1 = ElementBuilder("h1")
h2 = ElementBuilder("h2")
h3 = ElementBuilder("h3")
h4 = ElementBuilder("h4")
h5 = ElementBuilder("h5")
h6 = ElementBuilder("h6")
colgroup = ElementBuilder("colgroup")
col = ElementBuilder("col")

page = ElementBuilder("page")

meta = VoidElementBuilder("meta")
link = VoidElementBuilder("link")
img = VoidElementBuilder("img")


def text(value: Any) -> Node:
    return TextNode(str(value))


def cls(value: str) -> Attrs:
    return {"class": value}

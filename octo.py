import abc
from typing import Any, Callable, Iterable

Attrs = dict[str, str]
AttrsArg = None | str | dict


def is_class(item: str) -> bool:
    return item.startswith("#")


def split(txt: str, sep: str | None = None) -> list[str]:
    return [item for item in (item.strip() for item in txt.split(sep)) if item]


def get_classes(attrs: Attrs) -> list[str]:
    return split(attrs.get("class", ""))


def dict_remove_if(
    dct: dict[Any, Any], pred: Callable[[Any, Any], bool]
) -> dict[Any, Any]:
    return {k: v for k, v in dct.items() if not pred(k, v)}


def parse_id_and_classes(arg: str) -> Attrs:
    result: Attrs = Attrs()
    items = split(arg, ".")
    id_item = next((i for i in items if is_class(i)), None)
    if id_item:
        result["id"] = id_item[1:]
    classes = get_classes(result)
    for item in items:
        if not is_class(item) and item not in classes:
            classes.append(item)
    if classes:
        result["class"] = " ".join(classes)
    return result


def parse_dict(arg: str) -> Attrs:
    result: Attrs = Attrs()
    for item in split(arg):
        if "=" in item:
            k, v = item.split("=")
            result[k] = v
        else:
            result.update(parse_id_and_classes(item))
    return result


def merge_attrs(attrs: Attrs, arg: AttrsArg) -> Attrs:
    def combine_classes(old_classes: list[str], new_classes: list[str]) -> list[str]:
        return old_classes + [item for item in new_classes if not item in old_classes]

    if arg is None:
        return attrs

    if isinstance(arg, dict):
        return attrs | arg

    new_attrs = parse_dict(arg)
    all_classes = combine_classes(get_classes(attrs), get_classes(new_attrs))

    id = attrs.get("id") or new_attrs.get("id")

    def item_to_skip(k, _):
        return k in ("class", "id")

    return (
        ({"id": id} if id else {})
        | ({"class": " ".join(all_classes)} if all_classes else {})
        | dict_remove_if(attrs, item_to_skip)
        | dict_remove_if(new_attrs, item_to_skip)
    )


class Node(abc.ABC):
    @abc.abstractmethod
    def render(self, level: int) -> list[str]: ...

    def __str__(self):
        return "\n".join(self.render(0))


def escape(obj) -> str:
    return str(obj)  # TODO


class TextNode(Node):
    def __init__(self, value: Any):
        self._value = escape(value)

    def render(self, level: int) -> list[str]:
        return [self._value]


def get_children(*children) -> list[Node]:
    def handle_child(child) -> Iterable[Node]:
        if child is None:
            return ()
        elif isinstance(child, Node):
            yield child
        elif isinstance(child, str | int | float):
            yield TextNode(child)
        else:
            for it in child:
                yield from handle_child(it)

    res: list[Node] = []
    for child in children:
        res.extend(handle_child(child))
    return res


class VoidElement(Node):
    def __init__(self, name, attrs: Attrs = None):
        self._name = name
        self._attrs = attrs or Attrs()

    def render(self, level: int) -> list[str]:
        indent = "  " * level
        attrs = " ".join(f'{k}="{v}"' for k, v in self._attrs.items())
        if attrs:
            attrs = " " + attrs
        return [f"{indent}<{self._name}{attrs}>"]

    def __getitem__(self, arg: AttrsArg):
        return VoidElement(self._name, merge_attrs(self._attrs, arg))

    def __call__(self, attrs: Attrs):
        return VoidElement(self._name, merge_attrs(self._attrs, attrs))


class Element(Node):
    def __init__(self, name: str, attrs: Attrs = None, children: list[Node] = None):
        self._name = name
        self._attrs = attrs or Attrs()
        self._children = children or []
        assert all(isinstance(ch, Node) for ch in self._children)

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

    def __getitem__(self, arg: AttrsArg):
        return Element(self._name, merge_attrs(self._attrs, arg), self._children)

    def __call__(self, *args):
        return Element(self._name, self._attrs, self._children + get_children(*args))


def h(level: int) -> Element:
    return Element(f"h{level}")


html = Element("html")
head = Element("head")
body = Element("body")
div = Element("div")
span = Element("span")
p = Element("p")
table = Element("table")
tr = Element("tr")
td = Element("td")
th = Element("th")
ul = Element("ul")
ol = Element("ol")
li = Element("li")
h1 = h(1)
h2 = h(2)
h3 = h(3)
h4 = h(4)
h5 = h(5)
h6 = h(6)
colgroup = Element("colgroup")
col = Element("col")

page = Element("page")

meta = VoidElement("meta")
link = VoidElement("link")
img = VoidElement("img")

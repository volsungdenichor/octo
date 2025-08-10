from typing import Any
import octo


def to_row(tup: tuple[Any, ...]) -> octo.Node:
    return octo.tr([octo.td(octo.text(v)) for v in tup])


def create_header(names: list[str]) -> octo.Node:
    return octo.tr([octo.th(octo.text(v)) for v in names])


def create_table(
    columns: list[str], rows: list[tuple[Any, ...]], attrs: octo.Attrs = None
) -> octo.Node:
    return octo.table(create_header(columns), (to_row(r) for r in rows))


def main():
    data = [
        (1, 2, 3),
        (10, 20, 30),
        (100, 200, 300),
    ]
    doc = octo.html(
        octo.head(
            octo.meta["charset=UTF-8"],
            octo.link["rel=stylesheet type=text/css href=styles.css"],
        ),
        octo.body(create_table(["A", "B", "C"], data, attrs="#table.fancy")),
    )

    print(doc)


if __name__ == "__main__":
    main()

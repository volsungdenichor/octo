import octo


def main():
    doc = octo.html(
        octo.head(
            octo.meta({"charset": "UTF-8"}),
            octo.link({"rel": "stylesheet", "type": "text/css", "href": "styles.css"}),
        ),
        octo.body(
            octo.table["#table.fancy.a.b"](
                octo.tr((octo.th(v) for v in [1, "A", "B", "C"])),
            ),
        ),
    )

    print(doc)


if __name__ == "__main__":
    main()

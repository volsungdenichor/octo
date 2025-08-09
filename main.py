import octo


def main():
    doc = octo.html(
        octo.head(
            octo.meta({"charset": "UTF-8"}),
            octo.link({"rel": "stylesheet", "type": "text/css", "href": "styles.css"}),
        ),
        octo.body(
            octo.table["tabelka.kot.#ala"](
                octo.tr((octo.th(octo.text(v)) for v in ["A", "B", "C"])),
            ),
        ),
    )

    print(doc)


if __name__ == "__main__":
    main()

import datetime
from typing import Any

import yaml
import octo

ONGOING = "ongoing"


def split_date(s: str) -> tuple[int, int]:
    return tuple(int(w) for w in s.split("-"))


def get_last_day_of_previous_month(d: datetime.date) -> datetime.date:
    return d.replace(day=1) - datetime.timedelta(days=1)


def get_duration(start_date: str, end_date: str) -> str:
    from datetime import datetime

    if end_date == ONGOING:
        end_date = get_last_day_of_previous_month(datetime.today()).strftime("%Y-%m")

    def get_months_count(t: tuple[int, int]) -> int:
        year, month = t
        return 12 * year + month

    full_months = (
        get_months_count(split_date(end_date))
        - get_months_count(split_date(start_date))
        + 1
    )
    years, months = full_months // 12, full_months % 12
    if years > 0:
        return f"{years}y {months}m"
    else:
        return f"{months}m"


def format_date(date: str) -> str:
    if date == ONGOING:
        return date

    year, month = split_date(date)
    return f"{year}-{month:02}"


def render_professional_exp_full(items: list) -> octo.Node:
    def render(data: dict) -> octo.Node:
        from operator import itemgetter

        start_date, end_date = itemgetter("start_date", "end_date")(data)

        return octo.tr(
            octo.td(
                octo.div["time"](format_date(start_date)),
                octo.div["time"](format_date(end_date)),
                octo.div["duration"](get_duration(start_date, end_date)),
            ),
            octo.td(
                octo.div(octo.img[octo.src(data["logo"])]),
                octo.div(data["company"]),
                octo.div(data["location"]),
                octo.div(data["job_position"]),
                (
                    [
                        octo.div["achievements"](
                            octo.ul(map(octo.li, data["achievements"]))
                        )
                    ]
                    if "achievements" in data
                    else []
                ),
                octo.div(octo.ul(map(octo.li, data["description"]))),
                octo.div(map(octo.span["label.tech"], data["technologies"])),
            ),
        )

    return octo.div["content"](
        octo.table["grid"](
            octo.colgroup(
                octo.col["width=15%"],
                octo.col,
            ),
            map(render, items),
        )
    )


def render_professional_exp_simple(items: list) -> octo.Node:
    def render(data: dict) -> octo.Node:
        from operator import itemgetter

        start_date, end_date = itemgetter("start_date", "end_date")(data)

        return octo.tr["simple"](
            octo.td(octo.div["time"](format_date(start_date))),
            octo.td(octo.div["time"](format_date(end_date))),
            octo.td(
                octo.div(octo.img[octo.src(data["logo"])]),
                octo.div(data["company"]),
                octo.div(data["job_position"]),
                octo.div(octo.ul(map(octo.li, data["tags"]))),
            ),
        )

    return octo.div["content"](
        octo.table["grid.simple"](
            octo.colgroup(
                octo.col["width=15%"],
                octo.col["width=15%"],
                octo.col,
            ),
            map(render, items),
        )
    )


def render_languages(items) -> octo.Node:
    def render_grade(n) -> octo.Node:
        def create(enabled: bool) -> octo.Node:
            mode = "enabled" if enabled else "disabled"
            return octo.span[f"grade.{mode}"]

        return [create(i < n) for i in range(10)]

    def render_item(item) -> octo.Node:
        return octo.tr(
            octo.td(
                octo.div(item["name"]),
                octo.div(item["info"]),
            ),
            octo.td(render_grade(item["grade"])),
        )

    return octo.table(
        octo.colgroup(
            octo.col,
            octo.col,
        ),
        map(render_item, items),
    )


def render_education(items) -> octo.Node:
    def render_item(item) -> octo.Node:
        return octo.tr(
            octo.td(
                octo.div(item["start_date"]),
                octo.div(item["end_date"]),
            ),
            octo.td(
                octo.div(item["name"]),
                octo.div(item["school"]),
                octo.div(item["info"]),
            ),
        )

    return octo.table(
        octo.colgroup(
            octo.col,
            octo.col,
        ),
        map(render_item, items),
    )


def render_front_page(context) -> octo.Node:
    info = context["info"]

    def create_row(key: str, caption: str) -> octo.Node:
        return octo.tr(
            octo.td["key"](caption),
            octo.td["value"](str(info[key])),
        )

    full_name = f"{info['first_name']} {info['last_name']}"
    return octo.page["size=A4"](
        octo.div["personal-info"](
            octo.div["descr"](
                octo.p["my-name"](full_name),
                octo.table(
                    create_row("address", "Address"),
                    create_row("phone", "Phone"),
                    create_row("email", "E-Mail"),
                    create_row("github", "Github"),
                    create_row("date_of_birth", "Date of birth"),
                ),
            )
        ),
        octo.div["description"](context["description"]),
        octo.div["grid-layout"](
            octo.div(
                octo.h1("Skills"),
                octo.ul(map(octo.li, context["skills"])),
            ),
            octo.div(
                octo.h1("Profession Experience"),
                render_professional_exp_simple(context["professional_experience"]),
            ),
            octo.div(
                octo.h1("Languages"),
                render_languages(context["languages"]),
            ),
            octo.div(
                octo.h1("Programming Languages"),
                render_languages(context["programming_languages"]),
            ),
        ),
    )


def render(context: dict) -> octo.Node:
    return octo.html(
        octo.head(
            octo.meta["charset=UTF-8"],
            octo.link["rel=stylesheet type=text/css href=style.css"],
        ),
        octo.body(
            render_front_page(context),
            # octo.page["size=A4"](
            #     octo.div(
            #         octo.h1("Professional Experience"),
            #         render_professional_exp_full(context["professional_experience"]),
            #     )
            # ),
            # octo.page["size=A4"](
            #     octo.div(
            #         octo.h1("Education"),
            #         render_education(context["education"]),
            #     ),
            #     octo.div(
            #         octo.h1("Fields of Interest"),
            #         octo.ul(map(octo.li, context["fields_of_interest"])),
            #     ),
            #     octo.div(
            #         octo.h1("Personal Interests"),
            #         octo.ul(map(octo.li, context["personal_interests"])),
            #     ),
            #     octo.div(
            #         octo.h1("Other Skills"),
            #         octo.ul(map(octo.li, context["other_skills"])),
            #     ),
            # ),
        ),
    )


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    context = load_yaml("CV.yaml")
    doc = render(context)
    print(doc)
    with open(r"out.html", mode="w", encoding="UTF-8") as file:
        file.write(str(doc))


if __name__ == "__main__":
    main()

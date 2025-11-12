import datetime
from typing import Any

import yaml
import octo

ONGOING = "ongoing"


class Style:
    def __init__(self, value: str):
        self._value = value

    def __repr__(self):
        return self._value

    def __add__(self, other):
        return Style(f"{self}.{other}")


class STYLE:
    PAGE = Style("page")
    PAGE_BREAK = Style("page-break")

    CONTENT = Style("content")

    PERSONAL_INFO = Style("personal-info")

    KEY_VALUE_LIST = Style("key-value-list")
    KEY = Style("key")
    VALUE = Style("value")

    FULL_NAME = Style("full-name")

    TIME = Style("time")
    DURATION = Style("duration")
    ICON = Style("icon")

    LARGE = Style("large")
    SMALL = Style("small")

    EDUCATION = Style("education")

    COMPANY = Style("company")
    LOCATION = Style("location")
    JOB_POSITION = Style("job-position")

    ACHIEVEMENT_LIST = Style("achievement-list")
    ACHIEVEMENT = Style("achievement")

    DESCRIPTION_ITEM_LIST = Style("description-item-list")
    DESCRIPTION_ITEM = Style("description-item")

    LABEL = Style("label")
    LABEL_LIST = Style("label-list")
    TECH = Style("tech")

    PROFESSIONAL_EXP = Style("proffesional-exp")

    COMPACT = Style("compact")
    FULL = Style("full")

    LANGUAGE = Style("lang")
    LANGUAGES = Style("languages")

    NAME = Style("name")
    INFO = Style("info")

    GRADE_LIST = Style("grade-list")
    GRADE = Style("grade")

    PHOTO = Style("photo")

    ABOUT_ME = Style("about-me")
    SKILLS = Style("skills")


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
    return f"{years}y {months}m" if years > 0 else f"{months}m"


def format_date(date: str) -> str:
    if date == ONGOING:
        return date

    year, month = split_date(date)
    return f"{year}-{month:02}"


def render_professional_exp_simple(items: list) -> octo.Node:
    def render(data: dict) -> octo.Node:
        from operator import itemgetter

        start_date, end_date = itemgetter("start_date", "end_date")(data)

        return octo.tr(
            octo.td(
                octo.div[STYLE.TIME](format_date(start_date)),
                octo.div[STYLE.TIME](format_date(end_date)),
            ),
            octo.td(octo.img[STYLE.ICON + STYLE.SMALL][octo.src(data["logo"])]),
            octo.td["description"](
                octo.div(
                    octo.div(
                        octo.div[STYLE.COMPANY](data["company"]),
                        octo.div[STYLE.JOB_POSITION](data["job_position"]),
                        octo.div[STYLE.LABEL_LIST](
                            map(octo.div[STYLE.LABEL], data["tags"])
                        ),
                    ),
                ),
            ),
        )

    return octo.div(
        octo.table[STYLE.PROFESSIONAL_EXP + STYLE.COMPACT](
            map(render, items),
        )
    )


def render_languages(items) -> octo.Node:
    def render_grade(n) -> octo.Node:
        def create(enabled: bool) -> octo.Node:
            mode = "enabled" if enabled else "disabled"
            return octo.span[STYLE.GRADE + mode]

        return [create(i < n) for i in range(10)]

    def render_item(item) -> octo.Node:
        return octo.tr(
            octo.td(
                octo.div[STYLE.NAME](item["name"]),
                octo.div[STYLE.INFO](item["info"]),
            ),
            octo.td[STYLE.GRADE_LIST](render_grade(item["grade"])),
        )

    return octo.table[STYLE.LANGUAGES + STYLE.COMPACT](map(render_item, items))


def render_professional_exp_full(items: list) -> octo.Node:
    def render(data: dict) -> octo.Node:
        from operator import itemgetter

        start_date, end_date = itemgetter("start_date", "end_date")(data)

        return octo.tr(
            octo.td(
                octo.div[STYLE.TIME](format_date(start_date)),
                octo.div[STYLE.TIME](format_date(end_date)),
                octo.div[STYLE.DURATION](get_duration(start_date, end_date)),
            ),
            octo.td(
                octo.div["horizontal-block"](
                    octo.img[STYLE.ICON + STYLE.LARGE][octo.src(data["logo"])],
                    octo.div["vertical-block"](
                        octo.div[STYLE.COMPANY](data["company"]),
                        octo.div[STYLE.LOCATION](data["location"]),
                        octo.div[STYLE.JOB_POSITION](data["job_position"]),
                    ),
                ),
                octo.ul[STYLE.DESCRIPTION_ITEM_LIST](
                    map(octo.li[STYLE.DESCRIPTION_ITEM], data["description"]),
                    map(
                        octo.li[STYLE.DESCRIPTION_ITEM + STYLE.ACHIEVEMENT],
                        data.get("achievements", []),
                    ),
                ),
                octo.div[STYLE.LABEL_LIST](
                    map(octo.span[STYLE.LABEL + STYLE.TECH], data["technologies"])
                ),
            ),
        )

    return octo.table[STYLE.PROFESSIONAL_EXP + STYLE.FULL](map(render, items))


def render_education(items) -> octo.Node:
    def render_item(item) -> octo.Node:
        return octo.tr(
            octo.td(
                octo.div[STYLE.TIME](item["start_date"]),
                octo.div[STYLE.TIME](item["end_date"]),
            ),
            octo.td(
                octo.div[STYLE.NAME](item["name"]),
                octo.div[STYLE.JOB_POSITION](item["school"]),
                octo.div[STYLE.INFO](item["info"]),
            ),
        )

    return octo.table[STYLE.EDUCATION](map(render_item, items))


def render_front_page(context) -> octo.Node:
    info = context["info"]
    full_name = f"{info['first_name']} {info['last_name']}"

    def create_row(key: str, caption: str) -> octo.Node:
        return octo.tr(
            octo.td[STYLE.KEY](caption),
            octo.td[STYLE.VALUE](str(info[key])),
        )

    def create_link_row(key: str, caption: str) -> octo.Node:
        return octo.tr(
            octo.td[STYLE.KEY](caption),
            octo.td[STYLE.VALUE](octo.a[octo.href(info[key])](str(info[key]))),
        )

    GRID = "grid-2x2"
    GRID_ITEM = "grid-2x2-element"

    return octo.div["front-page"](
        octo.div[STYLE.PERSONAL_INFO](
            octo.div(
                octo.img[STYLE.PHOTO][octo.src(info["photo"])],
            ),
            octo.div(
                octo.p[STYLE.FULL_NAME](full_name),
                octo.div[STYLE.ABOUT_ME](context["about_me"]),
            ),
            octo.table[STYLE.KEY_VALUE_LIST](
                create_row("address", "Address"),
                create_row("phone", "Phone"),
                create_row("email", "E-Mail"),
                create_link_row("github", "Github"),
                create_row("date_of_birth", "Date of birth"),
            ),
        ),
        octo.div[GRID](
            octo.div[GRID_ITEM](
                octo.h1("Profession Experience"),
                render_professional_exp_simple(context["professional_experience"]),
            ),
            octo.div[GRID_ITEM](
                octo.h1("Skills"),
                octo.ul[STYLE.SKILLS + STYLE.COMPACT](map(octo.li, context["skills"])),
            ),
            octo.div[GRID_ITEM](
                octo.h1("Programming Languages"),
                render_languages(context["programming_languages"]),
            ),
            octo.div[GRID_ITEM](
                octo.h1("Languages"),
                render_languages(context["languages"]),
            ),
        ),
    )


def render(context: dict) -> octo.Node:
    return octo.html(
        octo.head(
            octo.meta["charset=UTF-8"],
            octo.link[
                "href=https://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css rel=stylesheet"
            ],
            octo.link["rel=preconnect href=https://fonts.googleapis.com"],
            octo.link["rel=preconnect href=https://fonts.gstatic.com"],
            octo.link[
                {
                    "href": "https://fonts.googleapis.com/css2?family=Archivo+Narrow&family=Julius+Sans+One&family=Open+Sans&family=Source+Sans+Pro&display=swap"
                }
            ]["rel=stylesheet"],
            octo.link["rel=stylesheet type=text/css href=style.css"],
        ),
        octo.body(
            octo.div[STYLE.PAGE](
                octo.div[STYLE.CONTENT](
                    render_front_page(context),
                    octo.div[STYLE.PAGE_BREAK](
                        octo.section(
                            octo.h1("Professional Experience Details"),
                            render_professional_exp_full(
                                context["professional_experience"]
                            ),
                        )
                    ),
                    octo.div[STYLE.PAGE_BREAK](
                        octo.div(
                            octo.h1("Education"),
                            render_education(context["education"]),
                        ),
                        octo.div(
                            octo.h1("Fields of Interest"),
                            octo.ul[STYLE.SKILLS](
                                map(octo.li, context["fields_of_interest"])
                            ),
                        ),
                        octo.div(
                            octo.h1("Personal Interests"),
                            octo.ul[STYLE.SKILLS](
                                map(octo.li, context["personal_interests"])
                            ),
                        ),
                        octo.div(
                            octo.h1("Other Skills"),
                            octo.ul[STYLE.SKILLS](
                                map(octo.li, context["other_skills"])
                            ),
                        ),
                    ),
                )
            ),
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

# -*- coding: utf-8 -*-
"""
Home page copy, English. Verbatim from the approved specification (sections
7-30) -- this file holds content, not markup, so a future edit to wording
never touches site/core/home.py.
"""

from .work_items_en import WORK_ITEMS
from .lab_items_en import LAB_ITEMS

HERO = {
    "name": "Juan Felipe",
}

ABOUT = {
    "eyebrow": "ABOUT",
    "paragraphs": [
        "I like understanding how things work.",
        "I work at the intersection of data, quality and engineering, "
        "making sure information can be trusted before it turns into a "
        "decision. I analyze systems, validate data, automate checks and "
        "build tools that surface problems before they ever reach "
        "production.",
        "What drives me most are the problems without an obvious answer. "
        "I enjoy following the evidence, questioning assumptions and "
        "digging until I find the cause of a problem rather than its "
        "symptoms. Understanding why has always been worth more to me "
        "than correcting the result.",
        "That curiosity shapes the way I work and the way I learn. "
        "Sometimes it ends in a project and sometimes in an experiment, "
        "but it always ends with a question answered.",
    ],
}

PILLARS = {
    "eyebrow": "WHAT I DO",
    "items": [
        {
            "title": "Data",
            "body": (
                "I work with data from where it originates to where it is "
                "consumed. First I understand what it represents, how it "
                "relates, and which business rules govern it. From there I "
                "validate its quality, reshape it where needed, and build "
                "processes that hold consistency, traceability and trust "
                "at every stage."
            ),
        },
        {
            "title": "QA / Testing",
            "body": (
                "I look for problems before they turn into incidents. I "
                "design and run tests, validate business rules and "
                "investigate anomalies until I reach their root cause. "
                "Wherever possible I automate the checks, so errors "
                "surface early and less risk reaches production."
            ),
        },
        {
            "title": "Engineering / Code",
            "body": (
                "I use engineering to turn complex processes into simple, "
                "maintainable solutions. I build tools, automations and "
                "applications that solve real problems, favoring clarity, "
                "scalability and ease of maintenance over unnecessary "
                "complexity."
            ),
        },
    ],
}

TECHNOLOGIES = {
    "eyebrow": "TECH STACK",
    "groups": [
        {"title": "Engineering", "items": ["Databricks", "SQL", "Oracle",
                                            "BigQuery"]},
        {"title": "Quality & Testing", "items": ["Jira", "Xray", "Postman"]},
        {"title": "Analytics & BI", "items": ["Power BI", "Tableau",
                                               "QlikView", "Excel"]},
        {"title": "Development", "items": ["Python", "Java", "GitHub"]},
    ],
}

# Home shows every current entry -- editorial order, not alphabetical.
# The alphabetical index lives at /work/, built from the same WORK_ITEMS list.
SELECTED_WORK = {
    "eyebrow": "SELECTED WORK",
    "items": WORK_ITEMS,
    "more_label": "View all work",
    "more_href": "/work/",
}

FROM_THE_LAB = {
    "eyebrow": "FROM THE LAB",
    "intro": (
        "This is where I explore ideas, test hypotheses and build small "
        "experiments to understand how things work. Some of them grow into "
        "useful tools; others simply teach me something new."
    ),
    "items": LAB_ITEMS,
    "more_label": "Explore the lab",
    "more_href": "/lab/",
}

CV_GATE = {
    "eyebrow": "CV",
    "body": (
        "Experience across data quality, engineering and analytics, "
        "focused on migration validation, automated controls and building "
        "solutions that keep information reliable."
    ),
    "link_label": "View CV",
    "href": "/cv/",
}

META = {
    "title": "Juan Felipe — arjuanfelipe.com",
    "description": (
        "Juan Felipe works across data, QA testing and engineering — "
        "analyzing systems, finding what doesn't fit, and building "
        "practical ways to make things better."
    ),
    "canonical": "https://arjuanfelipe.com/",
}

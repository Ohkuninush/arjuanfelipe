# -*- coding: utf-8 -*-
"""
Applications, English. Projects and tools that are live on their own domain,
listed as cards that open the real application in a new tab.

One list, shared with /es/applications/ through applications_es.py -- the two
pages can never disagree about which applications exist or where they point.
Each preview is a static SVG under /assets/applications/, drawn in the
canonical palette: none of the three shows a real screenshot, so an
auth-gated app never leaks its interior and the cards stay one visual family.
"""

APPLICATIONS = [
    {
        "slug": "july-melisa",
        "name": "July Melisa",
        "url": "https://julymelisa.com/",
        "category": "WEB · CLIENT PROJECT",
        "preview": "/assets/applications/july-melisa.svg",
        "body": (
            "Professional website built for July Melisa, an ontological "
            "coach. It brings together sessions, workshops, women's "
            "circles and image consulting under one visual identity "
            "about self-knowledge and creativity."
        ),
    },
    {
        "slug": "kaizen",
        "name": "KAIZEN",
        "url": "https://kaizen.arjuanfelipe.com/",
        "category": "WEB APP · INFRASTRUCTURE",
        "preview": "/assets/applications/kaizen.svg",
        "body": (
            "Infrastructure Intelligence and observability platform to "
            "supervise infrastructure, applications, services and "
            "operational events from a single administrative surface. "
            "Access is gated behind authentication."
        ),
    },
    {
        "slug": "colorimetria",
        "name": "Colorimetría",
        "url": "https://colorimetria.arjuanfelipe.com/",
        "category": "WEB APP · DATA / ANALYSIS",
        "preview": "/assets/applications/colorimetria.svg",
        "body": (
            "Web application for analysing and managing colorimetry "
            "data. Access is gated behind authentication with a "
            "second verification factor."
        ),
    },
]

INDEX_META = {
    "title": "Applications — Juan Felipe",
    "description": (
        "Applications and tools by Juan Felipe that are live on their own "
        "domain: July Melisa, KAIZEN and Colorimetría."
    ),
    "canonical": "https://arjuanfelipe.com/applications/",
    "heading": "Applications",
    "standfirst": (
        "Projects and tools I have designed, built or put into operation. "
        "Each one opens in its own tab."
    ),
    "back_label": "&larr; Back",
    "open_label": "Open",
}

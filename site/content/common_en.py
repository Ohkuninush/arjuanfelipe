# -*- coding: utf-8 -*-
"""Chrome shared by every English page: nav, footer, contact, WhatsApp."""

from . import contact_data as d

LANG = "en"
HOME_HREF = "/"

NAV_ITEMS = [
    {"label": "Work", "href": "/work/"},
    {"label": "Lab", "href": "/lab/"},
    {"label": "CV", "href": "/cv/"},
    {"label": "Applications", "href": "/applications/"},
]

WHATSAPP = {
    "e164": d.WHATSAPP_E164,
    "message": "Hi Juan Felipe, I found you through arjuanfelipe.com.",
    "accessible_name": "Contact Juan Felipe on WhatsApp",
}

CONTACT_LINKS = [
    {"label": "LinkedIn", "href": d.LINKEDIN},
    {"label": "GitHub", "href": d.GITHUB},
]

FOOTER_NAME = d.FULL_NAME

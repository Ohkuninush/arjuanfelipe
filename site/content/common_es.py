# -*- coding: utf-8 -*-
"""Chrome shared by every Spanish page: nav, footer, contact, WhatsApp."""

from . import contact_data as d

LANG = "es"
HOME_HREF = "/es/"

NAV_ITEMS = [
    {"label": "Trabajo", "href": "/es/work/"},
    {"label": "Lab", "href": "/es/lab/"},
    {"label": "CV", "href": "/es/cv/"},
    {"label": "Aplicaciones", "href": "/es/applications/"},
]

WHATSAPP = {
    "e164": d.WHATSAPP_E164,
    "message": "Hola Juan Felipe, llegué a través de arjuanfelipe.com.",
    "accessible_name": "Contactar a Juan Felipe por WhatsApp",
}

CONTACT_LINKS = [
    {"label": "LinkedIn", "href": d.LINKEDIN},
    {"label": "GitHub", "href": d.GITHUB},
]

FOOTER_NAME = d.FULL_NAME

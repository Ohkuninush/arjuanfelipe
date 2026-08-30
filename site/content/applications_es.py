# -*- coding: utf-8 -*-
"""
Aplicaciones, español. Contraparte de applications_en.py: mismos slugs, mismas
URLs, mismas previews. Solo cambia la prosa.
"""

from .applications_en import APPLICATIONS as _EN

# La lista de slugs/URLs/previews es la misma; aquí solo se traduce el copy.
APPLICATIONS = [
    {
        **_EN[0],
        "category": "WEB · PROYECTO DE CLIENTE",
        "body": (
            "Sitio web profesional para July Melisa, coach ontológica. "
            "Reúne sesiones, talleres, círculos de mujeres y asesoría de "
            "imagen bajo una identidad visual centrada en el "
            "autoconocimiento y la creatividad."
        ),
    },
    {
        **_EN[1],
        "category": "WEB APP · INFRAESTRUCTURA",
        "body": (
            "Plataforma de Infrastructure Intelligence y observabilidad "
            "para supervisar infraestructura, aplicaciones, servicios y "
            "eventos operacionales desde un único panel administrativo. "
            "El acceso está restringido con autenticación."
        ),
    },
    {
        **_EN[2],
        "category": "WEB APP · DATOS / ANÁLISIS",
        "body": (
            "Aplicación web para el análisis y la gestión de información "
            "de colorimetría. El acceso está protegido con autenticación "
            "y un segundo factor de verificación."
        ),
    },
]

INDEX_META = {
    "title": "Aplicaciones — Juan Felipe",
    "description": (
        "Aplicaciones y herramientas de Juan Felipe que están en línea en "
        "su propio dominio: July Melisa, KAIZEN y Colorimetría."
    ),
    "canonical": "https://arjuanfelipe.com/es/applications/",
    "heading": "Aplicaciones",
    "standfirst": (
        "Proyectos y herramientas que he diseñado, construido o puesto en "
        "operación. Cada una se abre en su propia pestaña."
    ),
    "back_label": "&larr; Atrás",
    "open_label": "Abrir",
}

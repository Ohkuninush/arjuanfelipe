# -*- coding: utf-8 -*-
"""Home page copy, Spanish. Editorial translation of home_en.py."""

from .work_items_es import WORK_ITEMS
from .lab_items_es import LAB_ITEMS

HERO = {
    "name": "Juan Felipe",
}

ABOUT = {
    "eyebrow": "SOBRE MÍ",
    "paragraphs": [
        "Me gusta entender cómo funcionan las cosas.",
        "Trabajo en la intersección entre datos, calidad e ingeniería, "
        "ayudando a que la información sea confiable antes de convertirse "
        "en una decisión. Analizo sistemas, valido datos, automatizo "
        "controles y desarrollo herramientas que permiten detectar "
        "problemas antes de que lleguen a producción.",
        "Lo que más me motiva son los problemas que no tienen una "
        "respuesta evidente. Disfruto seguir la evidencia, cuestionar "
        "suposiciones y profundizar hasta encontrar la causa de un "
        "problema, no solo sus síntomas. Para mí, entender el porqué "
        "siempre es más valioso que corregir el resultado.",
        "Esa curiosidad guía la forma en que trabajo y también la forma "
        "en que aprendo. A veces termina en un proyecto y otras en un "
        "experimento, pero siempre culmina resolviendo dudas.",
    ],
}

PILLARS = {
    "eyebrow": "LO QUE HAGO",
    "items": [
        {
            "title": "Datos",
            "body": (
                "Trabajo con datos desde su origen hasta su consumo. "
                "Primero entiendo qué representan, cómo se relacionan y "
                "qué reglas del negocio los gobiernan. A partir de ahí, "
                "valido su calidad, transformo la información cuando es "
                "necesario y construyo procesos que garanticen "
                "consistencia, trazabilidad y confianza en cada etapa."
            ),
        },
        {
            "title": "QA / Testing",
            "body": (
                "Busco problemas antes de que se conviertan en "
                "incidentes. Diseño y ejecuto pruebas, valido reglas de "
                "negocio y analizo anomalías hasta encontrar su causa "
                "raíz. Siempre que es posible, automatizo controles para "
                "detectar errores de forma temprana y reducir riesgos en "
                "producción."
            ),
        },
        {
            "title": "Ingeniería / Código",
            "body": (
                "Utilizo ingeniería para convertir procesos complejos en "
                "soluciones simples y mantenibles. Desarrollo "
                "herramientas, automatizaciones y aplicaciones que "
                "resuelven problemas reales, priorizando claridad, "
                "escalabilidad y facilidad de mantenimiento antes que la "
                "complejidad innecesaria."
            ),
        },
    ],
}

TECHNOLOGIES = {
    "eyebrow": "STACK TÉCNICO",
    "groups": [
        {"title": "Ingeniería", "items": ["Databricks", "SQL", "Oracle",
                                           "BigQuery"]},
        {"title": "Calidad y Pruebas", "items": ["Jira", "Xray", "Postman"]},
        {"title": "Analítica y BI", "items": ["Power BI", "Tableau",
                                               "QlikView", "Excel"]},
        {"title": "Desarrollo", "items": ["Python", "Java", "GitHub"]},
    ],
}

SELECTED_WORK = {
    "eyebrow": "TRABAJOS SELECCIONADOS",
    "items": WORK_ITEMS,
    "more_label": "Ver todos los trabajos",
    "more_href": "/es/work/",
}

FROM_THE_LAB = {
    "eyebrow": "DESDE EL LAB",
    "intro": (
        "Aquí exploro ideas, pongo a prueba hipótesis y construyo pequeños "
        "experimentos para entender mejor cómo funcionan las cosas. Algunos "
        "terminan convirtiéndose en herramientas útiles; otros simplemente "
        "me enseñan algo nuevo."
    ),
    "items": LAB_ITEMS,
    "more_label": "Explorar el lab",
    "more_href": "/es/lab/",
}

CV_GATE = {
    "eyebrow": "CV",
    "body": (
        "Experiencia en calidad de datos, ingeniería y analítica, con foco "
        "en validación de migraciones, automatización de controles y "
        "desarrollo de soluciones orientadas a la confiabilidad de la "
        "información."
    ),
    "link_label": "Ver CV",
    "href": "/es/cv/",
}

META = {
    "title": "Juan Felipe — arjuanfelipe.com",
    "description": (
        "Juan Felipe trabaja en datos, pruebas de calidad e ingeniería — "
        "analizando sistemas, encontrando lo que no encaja, y "
        "construyendo maneras prácticas de mejorar las cosas."
    ),
    "canonical": "https://arjuanfelipe.com/es/",
}

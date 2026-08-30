# -*- coding: utf-8 -*-
"""
CV content, Spanish. Employer names are anonymized here to match cv_en.py --
same generic descriptions, translated, so neither language version exposes
information the other one hides.
"""

IDENTITY = {
    "name": "JUAN FELIPE AYLLÓN RAMÍREZ",
    "phone_display": "+51 933 127 795",
    "phone_href": "tel:+51933127795",
    "email": "arjuanfelipe@icloud.com",
}

PROFILE = {
    "eyebrow": "PERFIL",
    "body": (
        "Analista de Calidad de Datos con experiencia en validación de datos a gran "
        "escala, pruebas de ETL, analítica y optimización de procesos en los sectores "
        "de servicios financieros y seguros. Experiencia validando conjuntos de datos "
        "masivos, asegurando la integridad de la información a lo largo de proyectos "
        "de migración a la nube y pipelines de datos críticos para el negocio. "
        "Manejo de SQL, Python, Power BI, Qlik y Postman, con un enfoque fuerte en "
        "automatización, calidad de datos y mejora continua."
    ),
}

ACHIEVEMENTS = [
    {"value": "+650M", "label": "registros validados"},
    {"value": "+99%", "label": "exactitud"},
    {"value": "0", "label": "reclamos post-producción"},
]

EXPERIENCE = {
    "eyebrow": "EXPERIENCIA LABORAL",
    "entries": [
        {
            "role": "Analista de Data Testing",
            "company": "Empresa Aseguradora Líder",
            "dates": "Abril 2023 – Febrero 2026",
            "tech_stack": "GCP | Oracle | PL/SQL | SQL Server | Power BI | Postman | VS Code | Git",
            "achievement": "Validé +650M de registros asegurando +99% de exactitud y 0 reclamos post-producción.",
            "functions": (
                "Pruebas end-to-end y controles de calidad de datos; validación de integridad, reglas de negocio, "
                "metadata y migraciones históricas e incrementales; conciliaciones y reconciliación origen-destino; "
                "automatización con SQL; gestión de defectos y evidencias para producción; pruebas API con Postman; "
                "pruebas funcionales, smoke, regresión, volumen, estrés y performance; analítica y dashboards con "
                "Power BI y QlikView."
            ),
        },
        {
            "role": "Jefe de Proyectos",
            "company": "Firma de Gestión de Inversiones",
            "dates": "Noviembre 2022 – Marzo 2023",
            "tech_stack": "SQL Server | Power BI | Qlik Sense | Excel | T-SQL",
            "achievement": "Implementación de controles de seguimiento contractual para reducir riesgos operativos.",
            "functions": (
                "Estandarización y documentación de procesos; automatización con SQL Server, reduciendo 30% los "
                "tiempos de gestión; reportes ejecutivos, análisis operativo, seguimiento contractual y normalización "
                "de datos para mejorar trazabilidad y consistencia."
            ),
        },
        {
            "role": "Analista de Calidad",
            "company": "Empresa Global de Experiencia del Cliente",
            "dates": "Octubre 2021 – Noviembre 2022",
            "tech_stack": "SQL Server | Speech Analytics | Text Analytics | Excel | Power BI",
            "achievement": (
                "Analizar +50K interacciones mensuales a través de Speech y Text Analytics, identificando gaps "
                "operativos que contribuyeron a mejoras cuantificables en la experiencia del cliente."
            ),
            "functions": (
                "Responsable del frente de Speech Analytics; análisis cualitativo y cuantitativo de interacciones; "
                "automatización con SQL Server, reduciendo 60% el tiempo de análisis; identificación de problemáticas, "
                "planes de mejora y análisis de métricas de Customer Experience."
            ),
        },
        {
            "role": "Analista de Control de Gestión",
            "company": "Empresa Regional de BPO",
            "dates": "Julio 2019 – Mayo 2021",
            "tech_stack": "SQL Server | Power BI | QlikView | Excel",
            "achievement": "Implementación de dashboards ejecutivos utilizados para la toma de decisiones estratégicas en región.",
            "functions": (
                "Automatización de procesos para Perú, Colombia y Chile con SQL Server y QlikView; modelos de control "
                "de gestión; liderazgo de analistas; modelos predictivos y proyectos de BI; dashboards ejecutivos en "
                "Power BI, QlikView y SQL Server; análisis y optimización de modelos de facturación."
            ),
        },
    ],
}

EDUCATION = {
    "eyebrow": "EDUCACIÓN",
    "entries": [{"institution": "Universidad Autónoma del Perú", "program": "Ingeniería de Sistemas", "dates": "2022 – Actualidad"}],
}

META = {
    "title": "CV — Juan Felipe Ayllón Ramírez",
    "description": "CV profesional de Juan Felipe Ayllón Ramírez: experiencia en pruebas de datos, analítica y mejora de procesos.",
    "canonical": "https://arjuanfelipe.com/es/cv/",
}

# -*- coding: utf-8 -*-
"""
Full Work entries, English. This is the single source both Home's "Selected
Work" teaser and /work/ (and each /work/<slug>/ detail page) render from --
one list, so the teaser and the destination can never say something
different about the same project.
"""

WORK_ITEMS = [
    {
        "slug": "data-migration-validation",
        "title": "Data Migration Validation",
        "categories": "Data · Quality",
        "body": (
            "I worked on validating large-scale data migration "
            "processes, making sure information kept its integrity "
            "between source and target systems. My work centered on data "
            "reconciliation, business-rule validation and automating "
            "quality controls to catch inconsistencies before release."
        ),
        "stack": "SQL Server · BigQuery · Data Testing",
    },
    {
        "slug": "julymelisa",
        "title": "julymelisa.com",
        "categories": "Web · Engineering",
        "body": (
            "I designed and built a website from the ground up, bringing "
            "visual identity, user experience and web engineering "
            "together in a single project. Beyond the implementation, I "
            "worked on performance, responsive design, accessibility and "
            "an architecture meant to deliver a fast, consistent "
            "experience across devices."
        ),
        "stack": "Web Design · UX/UI · Frontend Engineering",
    },
    {
        "slug": "qa-test-manager",
        "title": "QA Test Manager",
        "categories": "Java · QA",
        "body": (
            "I built a desktop application to manage the software "
            "testing lifecycle, covering projects, test cases, defects "
            "and reporting. The project combined software design, data "
            "persistence and quality principles, letting me build and "
            "validate the same system from both a developer's and a QA's "
            "perspective."
        ),
        "stack": "Java · QA / Testing · Software Engineering",
    },
]

INDEX_META = {
    "title": "Work — Juan Felipe",
    "description": (
        "Selected projects by Juan Felipe across data, QA testing and "
        "engineering, listed alphabetically."
    ),
    "canonical": "https://arjuanfelipe.com/work/",
    "eyebrow": "WORK",
    "heading": "Work",
}

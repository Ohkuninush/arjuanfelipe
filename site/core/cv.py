# -*- coding: utf-8 -*-
"""
Builds /cv/. Meant to work standalone: a recruiter opening only
arjuanfelipe.com/cv/ must be able to read and print it without ever visiting
the rest of the site (spec S66).
"""

from .shell import head, header, footer, whatsapp_float, skip_link

PRINTED_FROM = {"en": "Printed from", "es": "Impreso desde"}


def _identity(identity):
    # The contact links used to be repeated here. They live in the global
    # footer now -- one place, on every page, this one included.
    return f"""<section class="site-cv-identity"><div class="wds-container">
  <h1 class="site-cv-identity__name">{identity['name']}</h1>
</div></section>
"""


def _stats(achievements):
    items = "".join(
        f'<div><div class="site-cv-stats__value">{a["value"]}</div>'
        f'<div class="site-cv-stats__label">{a["label"]}</div></div>'
        for a in achievements
    )
    return f'<div class="wds-container"><div class="site-cv-stats">{items}</div></div>\n'


def _profile(profile):
    return f"""<section class="wds-section"><div class="wds-container">
  <h2 class="site-eyebrow">{profile['eyebrow']}</h2>
  <p class="site-detail__body">{profile['body']}</p>
</div></section>
"""


def _experience(experience):
    entries = "".join(
        f'<div class="site-cv-entry">'
        f'<h3 class="site-cv-entry__role">{e["role"]}</h3>'
        f'<p class="site-cv-entry__company">{e["company"]}</p>'
        f'<p class="site-cv-entry__dates">{e["dates"]}</p>'
        + (f'<p class="site-cv-entry__tech"><strong>{"Tech Stack" if experience["eyebrow"].startswith("WORK") else "Stack Tecnológico"}:</strong> {e["tech_stack"]}</p>' if e.get("tech_stack") else '')
        + f'<p class="site-cv-entry__achievement"><strong>{"Achievement" if experience["eyebrow"].startswith("WORK") else "Logro"}:</strong> {e["achievement"]}</p>'
        f'<p class="site-cv-entry__areas"><strong>{"Functions" if experience["eyebrow"].startswith("WORK") else "Funciones"}:</strong> {e["functions"]}</p>'
        f'</div>'
        for e in experience["entries"]
    )
    return f"""<section class="wds-section"><div class="wds-container">
  <h2 class="site-eyebrow">{experience['eyebrow']}</h2>
  {entries}
</div></section>
"""


def _education(education):
    entries = "".join(
        f'<div class="site-cv-entry">'
        f'<h3 class="site-cv-entry__role">{e["program"]}</h3>'
        f'<p class="site-cv-entry__company">{e["institution"]}</p>'
        f'<p class="site-cv-entry__dates">{e["dates"]}</p>'
        f'</div>'
        for e in education["entries"]
    )
    return f"""<section class="wds-section"><div class="wds-container">
  <h2 class="site-eyebrow">{education['eyebrow']}</h2>
  {entries}
</div></section>
"""


def build_cv(cds, cv, common, counterpart_href):
    lang = common.LANG
    lang_prefix = "" if lang == "en" else "/es"
    cv_href = f"{lang_prefix}/cv/"

    body = "".join([
        skip_link(lang),
        header(cds, common.NAV_ITEMS, common.HOME_HREF, lang,
               cv_href, counterpart_href),
        '<main id="main">',
        _identity(cv.IDENTITY),
        _profile(cv.PROFILE),
        _experience(cv.EXPERIENCE),
        _education(cv.EDUCATION),
        f'<p class="site-cv-print-only wds-container">{PRINTED_FROM[lang]} '
        f'arjuanfelipe.com{cv_href}</p>',
        '</main>',
        whatsapp_float(common.WHATSAPP),
        footer(common),
    ])

    alternates = {
        "en": "https://arjuanfelipe.com/cv/",
        "es": "https://arjuanfelipe.com/es/cv/",
        "x-default": "https://arjuanfelipe.com/cv/",
    }
    return (head(cv.META, lang, alternates) + "<body>\n" + body
            + "\n</body>\n</html>\n")

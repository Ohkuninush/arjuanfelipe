# -*- coding: utf-8 -*-
"""Builds each /work/<slug>/ and /lab/<slug>/ detail page."""

from .shell import head, header, footer, whatsapp_float, skip_link

BACK_LABEL = {
    ("en", "work"): "&larr; All work",
    ("es", "work"): "&larr; Todo el trabajo",
    ("en", "lab"): "&larr; All lab entries",
    ("es", "lab"): "&larr; Todo el lab",
}


def build_detail(cds, item, common, kind, counterpart_href):
    lang = common.LANG
    lang_prefix = "" if lang == "en" else "/es"
    base = "work" if kind == "work" else "lab"
    index_href = f"{lang_prefix}/{base}/"
    item_href = f"{lang_prefix}/{base}/{item['slug']}/"

    body = "".join([
        skip_link(lang),
        header(cds, common.NAV_ITEMS, common.HOME_HREF, lang,
               index_href, counterpart_href),
        '<main id="main">',
        '<section class="wds-section"><div class="wds-container">',
        f'<a class="site-detail__back" href="{index_href}">'
        f'{BACK_LABEL[(lang, kind)]}</a>',
        f'<h1>{item["title"]}</h1>',
        f'<p class="site-detail__meta">{item["categories"]}</p>',
        f'<p class="site-detail__body">{item["body"]}</p>',
        f'<p class="site-detail__tech">{item["stack"]}</p>',
        '</div></section>',
        '</main>',
        whatsapp_float(common.WHATSAPP),
        footer(common),
    ])

    meta = {
        "title": f'{item["title"]} — Juan Felipe',
        "description": item["body"],
        "canonical": f"https://arjuanfelipe.com{item_href}",
    }
    alternates = {
        "en": f"https://arjuanfelipe.com/{base}/{item['slug']}/",
        "es": f"https://arjuanfelipe.com/es/{base}/{item['slug']}/",
        "x-default": f"https://arjuanfelipe.com/{base}/{item['slug']}/",
    }
    return (head(meta, lang, alternates) + "<body>\n" + body
            + "\n</body>\n</html>\n")

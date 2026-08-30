# -*- coding: utf-8 -*-
"""Builds /work/ and /lab/ -- the alphabetical index of each collection."""

from .shell import head, header, footer, whatsapp_float, skip_link


def build_listing(cds, items, index_meta, common, kind, counterpart_href):
    lang = common.LANG
    lang_prefix = "" if lang == "en" else "/es"
    base = "work" if kind == "work" else "lab"
    ordered = sorted(items, key=lambda it: it["title"].lower())

    rows = "".join(
        f'<li><article>'
        f'<h2 class="site-editorial__title">'
        f'<a href="{lang_prefix}/{base}/{it["slug"]}/">{it["title"]}</a></h2>'
        f'<p class="site-editorial__meta">{it["categories"]}</p>'
        f'<p class="site-editorial__body">{it["body"]}</p>'
        f'</article></li>'
        for it in ordered
    )

    body = "".join([
        skip_link(lang),
        header(cds, common.NAV_ITEMS, common.HOME_HREF, lang,
               f"{lang_prefix}/{base}/", counterpart_href),
        '<main id="main">',
        '<section class="wds-section"><div class="wds-container">',
        f'<h1>{index_meta["heading"]}</h1>',
        f'<ol class="site-editorial">{rows}</ol>',
        '</div></section>',
        '</main>',
        whatsapp_float(common.WHATSAPP),
        footer(common),
    ])
    alternates = {
        "en": f"https://arjuanfelipe.com/{base}/",
        "es": f"https://arjuanfelipe.com/es/{base}/",
        "x-default": f"https://arjuanfelipe.com/{base}/",
    }
    return (head(index_meta, lang, alternates) + "<body>\n" + body
            + "\n</body>\n</html>\n")

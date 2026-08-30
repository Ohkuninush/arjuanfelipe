# -*- coding: utf-8 -*-
"""
Builds /applications/ and /es/applications/ -- a small grid of cards, each
one a link that opens a live application on its own domain in a new tab.

Same shell as every other page (skip link, header, footer, WhatsApp float).
The only shape this file adds over /work/ is the card: a 2:1 preview image, a
name, a category, a short description and an "Open" affordance, with the whole
card as the click target.
"""

from .shell import head, header, footer, whatsapp_float, skip_link


def _card(app, open_label):
    return (
        f'<li><a class="site-apps__card" href="{app["url"]}" '
        f'target="_blank" rel="noopener noreferrer">'
        f'<span class="site-apps__preview">'
        f'<img src="{app["preview"]}" alt="" width="1200" height="600" '
        f'loading="lazy" decoding="async"></span>'
        f'<span class="site-apps__name">{app["name"]}</span>'
        f'<span class="site-apps__meta">{app["category"]}</span>'
        f'<span class="site-apps__body">{app["body"]}</span>'
        f'<span class="site-apps__open">{open_label} &rarr;</span>'
        f'</a></li>'
    )


def build_applications(cds, content, common, counterpart_href):
    lang = common.LANG
    home_href = common.HOME_HREF
    self_href = "/applications/" if lang == "en" else "/es/applications/"
    meta = content.INDEX_META

    cards = "".join(_card(app, meta["open_label"]) for app in content.APPLICATIONS)

    body = "".join([
        skip_link(lang),
        header(cds, common.NAV_ITEMS, home_href, lang, self_href, counterpart_href),
        '<main id="main">',
        '<section class="wds-section"><div class="wds-container">',
        f'<a class="site-apps__back" href="{home_href}" data-back>'
        f'{meta["back_label"]}</a>',
        f'<h1>{meta["heading"]}</h1>',
        f'<div class="wds-reading"><p>{meta["standfirst"]}</p></div>',
        f'<ul class="site-apps">{cards}</ul>',
        '</div></section>',
        '</main>',
        whatsapp_float(common.WHATSAPP),
        footer(common),
    ])

    alternates = {
        "en": "https://arjuanfelipe.com/applications/",
        "es": "https://arjuanfelipe.com/es/applications/",
        "x-default": "https://arjuanfelipe.com/applications/",
    }
    return (head(meta, lang, alternates) + "<body>\n" + body
            + "\n</body>\n</html>\n")

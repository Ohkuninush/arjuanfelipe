# -*- coding: utf-8 -*-
"""Assembles the Home page from content/home_{en,es}.py + the shared shell."""

from .shell import head, header, footer, whatsapp_float, skip_link


def _section(eyebrow, body_html, section_id):
    # The eyebrow IS the section heading -- an <h2>, not a decorative <p> --
    # so the page reads h1 (name) -> h2 (section) -> h3 (pillar/project title)
    # with no level skipped. Visual size is unaffected: .site-eyebrow's own
    # rule outranks the generic h2 rule by specificity (class vs type).
    return (f'<section id="{section_id}" class="wds-section">'
            f'<div class="wds-container">'
            f'<h2 class="site-eyebrow">{eyebrow}</h2>'
            f'{body_html}'
            f'</div></section>\n')


def _hero(hero):
    # The name carries the page on its own. The glyph still opens every page
    # from the header mark, where it is a permanent identity cue rather than a
    # one-off phrase.
    return f"""<section class="site-hero"><div class="wds-container">
  <h1 class="site-hero__name">{hero['name']}</h1>
</div></section>
"""


def _about(about):
    paras = "".join(
        "".join(f"<p>{line}</p>" for line in p.split("\n"))
        for p in about["paragraphs"]
    )
    return _section(about["eyebrow"], f'<div class="wds-reading">{paras}</div>',
                     "about")


def _pillars(pillars):
    items = "".join(
        f'<div><h3 class="site-pillar__title">{it["title"]}</h3>'
        f'<p class="site-pillar__body">{it["body"]}</p></div>'
        for it in pillars["items"]
    )
    return _section(pillars["eyebrow"], f'<div class="site-pillars">{items}</div>',
                     "what-i-do")


def _technologies(tech):
    groups = "".join(
        f'<div><h3 class="site-tech__group-title">{g["title"]}</h3>'
        f'<ul class="site-tech__list">'
        + "".join(f"<li>{i}</li>" for i in g["items"])
        + "</ul></div>"
        for g in tech["groups"]
    )
    return _section(tech["eyebrow"], f'<div class="site-tech">{groups}</div>',
                     "technologies")


def _editorial(section_data, section_id, kind, lang_prefix):
    base = "work" if kind == "work" else "lab"
    items = "".join(
        f'<li><article>'
        f'<h3 class="site-editorial__title">'
        f'<a href="{lang_prefix}/{base}/{it["slug"]}/">{it["title"]}</a></h3>'
        f'<p class="site-editorial__meta">{it["categories"]}</p>'
        f'<p class="site-editorial__body">{it["body"]}</p>'
        f'</article></li>'
        for it in section_data["items"]
    )
    more = (f'<p class="site-editorial__more">'
            f'<a href="{section_data["more_href"]}">'
            f'{section_data["more_label"]} &rarr;</a></p>')
    # Optional standfirst above the list. Rendered with the same .wds-reading
    # measure the About section uses, so introductory prose reads identically
    # wherever it appears -- no new class, no new rule.
    intro = (f'<div class="wds-reading"><p>{section_data["intro"]}</p></div>'
             if section_data.get("intro") else "")
    return _section(section_data["eyebrow"],
                     f'{intro}<ol class="site-editorial">{items}</ol>{more}',
                     section_id)


def _cv_gate(cv):
    body = (f'<div class="site-gate__body"><p>{cv["body"]}</p>'
            f'<a class="site-gate__link" href="{cv["href"]}">'
            f'{cv["link_label"]} &rarr;</a></div>')
    return _section(cv["eyebrow"], body, "cv")


def build_home(cds, c, common, counterpart_href):
    """
    c        -- the home_{lang}.py content module
    common   -- the common_{lang}.py chrome module (nav, contact, whatsapp)
    """
    lang = common.LANG
    lang_prefix = "" if lang == "en" else "/es"
    body = "".join([
        skip_link(lang),
        header(cds, common.NAV_ITEMS, common.HOME_HREF, lang,
               common.HOME_HREF, counterpart_href),
        '<main id="main">',
        _hero(c.HERO),
        _about(c.ABOUT),
        _pillars(c.PILLARS),
        _technologies(c.TECHNOLOGIES),
        _editorial(c.SELECTED_WORK, "selected-work", "work", lang_prefix),
        _editorial(c.FROM_THE_LAB, "from-the-lab", "lab", lang_prefix),
        _cv_gate(c.CV_GATE),
        '</main>',
        whatsapp_float(common.WHATSAPP),
        footer(common),
    ])
    canonical_root = "https://arjuanfelipe.com" + (lang_prefix or "") + "/"
    alternates = {
        "en": "https://arjuanfelipe.com/",
        "es": "https://arjuanfelipe.com/es/",
        "x-default": "https://arjuanfelipe.com/",
    }
    return (head(c.META, lang, alternates) + "<body>\n" + body
            + "\n</body>\n</html>\n")

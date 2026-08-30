# -*- coding: utf-8 -*-
"""
The page shell: <head>, header/nav, footer, skip link, WhatsApp float,
language switcher.

Reuses WDS component classes (.wds-header, .wds-nav, .wds-container,
.wds-glyph, .wds-mark, .wds-skip-link) wherever they already fit -- the site
composes the design system, it never re-declares it.
"""

import json
from urllib.parse import quote

from .js import THEME_BOOTSTRAP_JS

SKIP_LINK_TEXT = {"en": "Skip to content", "es": "Saltar al contenido"}
MENU_LABEL = {"en": "Menu", "es": "Menú"}
NAV_LABEL = {"en": "Primary", "es": "Principal"}
NAV_LABEL_MOBILE = {"en": "Primary (mobile)", "es": "Principal (móvil)"}
LANG_SWITCH_NAME = {
    # accessible name for the LINK to the *other* language, phrased in that
    # other language -- a Spanish speaker sees "English", not "Inglés".
    "en": "English", "es": "Español",
}
THEME_SWITCH_LABEL = {"en": "Theme", "es": "Tema"}
THEME_NAME = {
    ("en", "light"): "Light", ("es", "light"): "Claro",
    ("en", "dark"): "Dark", ("es", "dark"): "Oscuro",
}
# Drawn with currentColor and no fill, exactly like the identity glyph, so the
# control inherits the switch's own colour states instead of carrying its own.
THEME_ICON = {
    "light": ('<circle cx="12" cy="12" r="4.2"/>'
              '<path d="M12 2.6v2.2M12 19.2v2.2M4.4 4.4l1.6 1.6'
              'M18 18l1.6 1.6M2.6 12h2.2M19.2 12h2.2M4.4 19.6l1.6-1.6'
              'M18 6l1.6-1.6"/>'),
    "dark": '<path d="M20.4 14.5A8.6 8.6 0 0 1 9.5 3.6a8.6 8.6 0 1 0 10.9 10.9Z"/>',
}


def wa_link(whatsapp):
    """
    A direct wa.me link, no third-party widget. One function for both the
    Contact-section link and the floating action, so they can never point
    at different destinations or drift in wording.
    """
    text = quote(whatsapp["message"])
    return f"https://wa.me/{whatsapp['e164']}?text={text}"


def glyph_svg(cds, css_class="wds-glyph"):
    d = cds["path"]["d"]
    vb = f"0 0 {cds['bounding_box']['width']} {cds['bounding_box']['height']}"
    sw = cds["parameters"]["stroke_width"]
    # Intrinsic dimensions are a defensive fallback for file:// previews or
    # stylesheet failures. CSS still controls the rendered size in normal use.
    # 15x100 preserves the canonical aspect ratio without allowing the tall
    # identity glyph to expand to its raw 1000-unit viewBox height.
    return (f'<svg class="{css_class}" viewBox="{vb}" width="15" height="100" '
            f'aria-hidden="true" focusable="false">'
            f'<path d="{d}" stroke-width="{sw}"/></svg>')


# Short digest of the built assets, stamped onto their URLs. build_site.py
# assigns it once, after it knows what it wrote; see the note there. A page
# and the stylesheet/script it was built with therefore travel together, so a
# browser holding an older copy of either cannot pair them -- the failure
# that makes a page look like it has a different header than its neighbours.
ASSET_VERSION = ""


def _asset(path):
    return f"{path}?v={ASSET_VERSION}" if ASSET_VERSION else path


def head(meta, lang="en", alternates=None, extra_link=""):
    """
    alternates: {"en": url, "es": url, "x-default": url} -- every language
    variant of THIS page, so a crawler (and the language switcher) never has
    to guess whether a counterpart exists.
    """
    alt_tags = ""
    if alternates:
        alt_tags = "\n".join(
            f'<link rel="alternate" hreflang="{code}" href="{url}">'
            for code, url in alternates.items())
        alt_tags += "\n"
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta['title']}</title>
<meta name="description" content="{meta['description']}">
<link rel="canonical" href="{meta['canonical']}">
{alt_tags}<meta property="og:type" content="website">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{meta['canonical']}">
<meta property="og:locale" content="{'es_PE' if lang == 'es' else 'en_US'}">
<meta property="og:site_name" content="Juan Felipe">
<meta name="theme-color" content="#10141a">
<link rel="icon" href="/identity/dist/favicon/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/identity/dist/favicon/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/identity/dist/apple/apple-touch-icon.png">
<link rel="mask-icon" href="/identity/dist/mask-icon.svg" color="#ea6a1e">
<link rel="manifest" href="/identity/dist/site.webmanifest">
<script>{THEME_BOOTSTRAP_JS}</script>
<link rel="stylesheet" href="{_asset('/assets/site.css')}">
<script src="{_asset('/assets/site.js')}" defer></script>
{extra_link}<script type="application/ld+json">{json.dumps(structured_data(meta), ensure_ascii=False)}</script>
</head>
"""


def structured_data(meta):
    """
    Only Person + WebSite, and only facts already public elsewhere on the
    site (name, canonical url, social profiles). Nothing here is invented:
    no job title, no rating, no organization the CV does not already state.
    """
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "name": "Juan Felipe Ayllón Ramírez",
                "url": "https://arjuanfelipe.com/",
                "email": "mailto:arjuanfelipe@icloud.com",
                "sameAs": [
                    "https://github.com/Ohkuninush",
                    "https://www.linkedin.com/in/juan-ayllon-ramirez-77bab8ab/",
                ],
            },
            {
                "@type": "WebSite",
                "name": "Juan Felipe",
                "url": "https://arjuanfelipe.com/",
            },
        ],
    }


def lang_switch(lang, counterpart_href):
    """
    A stable-URL toggle, not a client-side state flip: the link IS the other
    language's real page. The active language is marked, not linked to
    itself -- an active "link" to the page you're already on is not a link.
    """
    other = "es" if lang == "en" else "en"
    codes = ["en", "es"]
    parts = []
    for code in codes:
        if code == lang:
            parts.append(f'<span aria-current="true">{code.upper()}</span>')
        else:
            parts.append(
                f'<a href="{counterpart_href}" data-language-switch hreflang="{code}" '
                f'lang="{code}">{code.upper()}'
                f'<span class="wds-visually-hidden"> '
                f'({LANG_SWITCH_NAME[code]})</span></a>')
    return f'<div class="site-switch site-lang-switch">{"".join(parts)}</div>'


def theme_switch(lang):
    """
    The sibling of the language switch: same segmented shape, same vocabulary.

    Both options are always present and pressed state is carried by
    aria-pressed, so the control announces which theme is active instead of
    relying on a colour difference. The server always renders "dark" as
    pressed -- the <head> bootstrap and site.js re-sync it from the stored
    preference before the reader can interact with it.
    """
    buttons = "".join(
        f'<button type="button" data-theme-set="{theme}" '
        f'aria-pressed="{"true" if theme == "dark" else "false"}">'
        f'<svg viewBox="0 0 24 24" width="15" height="15" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false">'
        f'{THEME_ICON[theme]}</svg>'
        f'<span class="wds-visually-hidden">{THEME_NAME[(lang, theme)]}</span>'
        f'</button>'
        for theme in ("light", "dark")
    )
    return (f'<div class="site-switch site-theme-switch" role="group" '
            f'aria-label="{THEME_SWITCH_LABEL[lang]}">{buttons}</div>')


def header(cds, nav_items, home_href, lang, current_href, counterpart_href):
    links = "".join(
        f'<a href="{it["href"]}"'
        + (' aria-current="page"' if it["href"] == current_href else '')
        + f'>{it["label"]}</a>'
        for it in nav_items)
    switch = lang_switch(lang, counterpart_href) + theme_switch(lang)
    return f"""<header class="wds-header"><div class="wds-container wds-header__inner">
  <a class="wds-mark" href="{home_href}">{glyph_svg(cds)}<strong>Juan Felipe</strong></a>
  <div class="site-nav-group">
    <nav class="wds-nav" aria-label="{NAV_LABEL[lang]}">
      {links}
    </nav>
    <details class="wds-nav-toggle">
      <summary aria-label="{MENU_LABEL[lang]}">{MENU_LABEL[lang]}</summary>
      <nav class="wds-nav" aria-label="{NAV_LABEL_MOBILE[lang]}">
        {links}
      </nav>
    </details>
    {switch}
  </div>
</div></header>
"""


def whatsapp_float(whatsapp):
    href = wa_link(whatsapp)
    name = whatsapp["accessible_name"]
    # Recognizable WhatsApp glyph, rendered with currentColor so the control
    # stays inside arjuanfelipe.com's canonical palette instead of importing
    # WhatsApp green into the visual system.
    icon = (
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" '
        'aria-hidden="true" focusable="false">'
        '<path d="M12.04 2a9.84 9.84 0 0 0-8.42 14.92L2 22l5.2-1.57A9.96 9.96 0 1 0 12.04 2Zm0 17.93a8.08 8.08 0 0 1-4.12-1.13l-.3-.18-3.08.93.95-3-.2-.31a7.93 7.93 0 1 1 6.75 3.69Zm4.43-5.94c-.24-.12-1.44-.7-1.66-.79-.22-.08-.38-.12-.54.12-.16.24-.62.79-.76.95-.14.16-.28.18-.52.06-.24-.12-1.02-.37-1.94-1.19a7.27 7.27 0 0 1-1.34-1.65c-.14-.24-.02-.37.1-.49.11-.11.24-.28.36-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.54-1.3-.74-1.78-.19-.47-.39-.4-.54-.41h-.46c-.16 0-.42.06-.64.3-.22.24-.84.82-.84 2s.86 2.32.98 2.48c.12.16 1.69 2.58 4.1 3.62.57.25 1.02.4 1.37.51.58.18 1.1.16 1.51.1.46-.07 1.44-.59 1.64-1.16.2-.57.2-1.06.14-1.16-.06-.1-.22-.16-.46-.28Z"/>'
        '</svg>'
    )
    return (
        f'<a class="site-whatsapp" href="{href}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="{name}">'
        f'<span class="site-whatsapp__inner">{icon}'
        f'<span class="site-whatsapp__label" aria-hidden="true">'
        f'WhatsApp</span></span></a>'
    )


def footer(common):
    """
    One block, one line: identity, year and the ways to reach him.

    Contact used to be a full section of its own above the footer, which cost
    a screenful of vertical space to say what fits on this line. The links are
    still the same CONTACT_LINKS list, so there is exactly one definition of
    where "LinkedIn" points, shared with the CV page.
    """
    links = "".join(
        f'<li><a href="{link["href"] or wa_link(common.WHATSAPP)}"'
        + (' target="_blank" rel="noopener noreferrer"' if link["href"] else '')
        + f'>{link["label"]}</a></li>'
        for link in common.CONTACT_LINKS
    )
    return f"""<footer class="wds-footer"><div class="wds-container site-footer">
  <p class="site-footer__id">{common.FOOTER_NAME} &nbsp;&nbsp; &copy; 2026</p>
  <ul class="site-footer__links">{links}</ul>
</div></footer>
"""


def skip_link(lang):
    return f'<a class="wds-skip-link" href="#main">{SKIP_LINK_TEXT[lang]}</a>\n'

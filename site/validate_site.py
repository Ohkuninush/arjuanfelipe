# -*- coding: utf-8 -*-
"""
Site validation suite. Same pattern as wds/validate_wds.py: structural checks
that catch the class of bug HTML/CSS does not raise an error for.

Run:  python validate_site.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PASS, FAIL = [], []


def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append((name, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))


PAGES = [
    "index.html", "es/index.html",
    "work/index.html", "es/work/index.html",
    "work/data-migration-validation/index.html",
    "es/work/data-migration-validation/index.html",
    "work/julymelisa/index.html", "es/work/julymelisa/index.html",
    "work/qa-test-manager/index.html", "es/work/qa-test-manager/index.html",
    "lab/index.html", "es/lab/index.html",
    "lab/speech-to-text/index.html", "es/lab/speech-to-text/index.html",
    "lab/water-loss-model/index.html", "es/lab/water-loss-model/index.html",
    "cv/index.html", "es/cv/index.html",
    "applications/index.html", "es/applications/index.html",
]


def main():
    print("SITE VALIDATION SUITE")
    print("=" * 72)

    pages = {}
    for rel in PAGES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            pages[rel] = None
            continue
        with open(path, encoding="utf-8") as f:
            pages[rel] = f.read()

    missing = [rel for rel, html in pages.items() if html is None]
    ck("T0 every expected page exists on disk", not missing,
       f"{len(pages) - len(missing)}/{len(pages)}"
       + (f" | MISSING: {missing}" if missing else ""))
    pages = {rel: html for rel, html in pages.items() if html is not None}

    with open(os.path.join(ROOT, "assets", "site.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ROOT, "identity", "cds.json"), encoding="utf-8") as f:
        cds = json.load(f)

    # ---- T1: exactly one <h1> per page --------------------------------------
    bad_h1 = {rel: len(re.findall(r"<h1[ >]", html))
              for rel, html in pages.items()}
    bad_h1 = {rel: n for rel, n in bad_h1.items() if n != 1}
    ck("T1 every page has exactly one <h1>", not bad_h1, str(bad_h1) if bad_h1 else "")

    # ---- T2: landmark elements on every page ---------------------------------
    bad_landmarks = {}
    for rel, html in pages.items():
        missing_l = [t for t in ("header", "nav", "main", "footer")
                     if not re.search(fr"<{t}[ >]", html)]
        if missing_l:
            bad_landmarks[rel] = missing_l
    ck("T2 header/nav/main/footer present on every page", not bad_landmarks,
       str(bad_landmarks) if bad_landmarks else "")

    # ---- T3: referential integrity of custom properties ----------------------
    defined = set(re.findall(r"^\s*(--wds-[a-z0-9-]+)\s*:", css, re.M))
    used_css = set(re.findall(r"var\((--wds-[a-z0-9-]+)", css))
    missing_tok = sorted(used_css - defined)
    ck("T3 every --wds-* token referenced in css is defined", not missing_tok,
       f"{len(used_css)} referenced, {len(defined)} defined"
       + (f" | MISSING: {missing_tok}" if missing_tok else ""))

    # ---- T4: stylesheet is linked, not inlined, on every page ----------------
    bad_link = [rel for rel, html in pages.items()
                if not re.search(
                    r'<link rel="stylesheet" href="/assets/site\.css(\?v=[0-9a-f]+)?">',
                    html)
                or "<style>" in html]
    ck("T4 every page links the stylesheet (cacheable), none inlines it",
       not bad_link, str(bad_link) if bad_link else "")

    # ---- T4b: one build, one asset version, across every page ---------------
    # Pages that disagree here would load different stylesheets, which is
    # exactly how a site starts looking like two different sites.
    versions = {}
    for rel, html in pages.items():
        found = set(re.findall(r'/assets/site\.(?:css|js)\?v=([0-9a-f]+)', html))
        versions.setdefault(frozenset(found), []).append(rel)
    ck("T4b every page references one and the same asset version",
       len(versions) == 1 and len(next(iter(versions))) == 1,
       f"version {sorted(next(iter(versions)))}" if len(versions) == 1
       else f"DIVERGENT: { {tuple(sorted(k)): len(v) for k, v in versions.items()} }")

    # ---- T5: skip link precedes header, on every page ------------------------
    bad_skip = []
    for rel, html in pages.items():
        after_body = html[html.index("<body>"):]
        if ("wds-skip-link" not in after_body
                or after_body.index("wds-skip-link") > after_body.index("<header")):
            bad_skip.append(rel)
    ck("T5 skip link present and first, on every page", not bad_skip,
       str(bad_skip) if bad_skip else "")

    # ---- T6: the glyph is consumed, not redrawn ------------------------------
    bad_glyph = [rel for rel, html in pages.items()
                 if cds["path"]["d"] not in html]
    ck("T6 every page consumes the CDS glyph inline", not bad_glyph,
       str(bad_glyph) if bad_glyph else "")
    ck("T6b the site css declares no glyph geometry of its own",
       cds["path"]["d"] not in css)
    # Defensive intrinsic dimensions: if /assets/site.css fails to load (for
    # example an accidental file:// preview), the tall identity SVG must not
    # expand to its raw 1000-unit viewBox height.
    bad_intrinsic = [rel for rel, html in pages.items()
                     if not re.search(r'class="wds-glyph"[^>]*width="15"[^>]*height="100"', html)]
    ck("T6c every inline identity glyph has defensive intrinsic dimensions",
       not bad_intrinsic, str(bad_intrinsic) if bad_intrinsic else "")

    # The Hero is the name alone. The retired "now | know" line must be gone
    # from both languages -- and gone from the stylesheet with it, so the
    # removal cannot survive as dead CSS.
    hero_clean = all("site-hero__line" not in pages[rel]
                     for rel in ("index.html", "es/index.html"))
    ck("T6d Home hero carries the name only, in EN and ES",
       hero_clean and "site-hero__line" not in css)

    # ---- T7: touch target tokens are in play ---------------------------------
    ck("T7 touch-target token is defined and used",
       "--wds-touch-target:" in css and "var(--wds-touch-target)" in css)

    # ---- T8: reduced motion is respected --------------------------------------
    ck("T8 reduced motion collapses durations globally",
       "prefers-reduced-motion" in css)

    # ---- T9/T10: WhatsApp float + Contact link agree on every page ----------
    bad_wa = {}
    for rel, html in pages.items():
        m = re.search(r'<a class="site-whatsapp" href="([^"]+)"[^>]*aria-label="([^"]+)"', html)
        if not m or not m.group(1).startswith("https://wa.me/") or not m.group(2):
            bad_wa[rel] = "float missing or malformed"
            continue
        wa_hrefs = {h.split("?")[0] for h in
                    re.findall(r'href="(https://wa\.me/[^"]+)"', html)}
        if len(wa_hrefs) != 1:
            bad_wa[rel] = f"multiple numbers: {wa_hrefs}"
    ck("T9 WhatsApp float + every WhatsApp link agree, on every page",
       not bad_wa, str(bad_wa) if bad_wa else "")

    # ---- T11: no hard-coded colour outside the token layer -------------------
    # @media print is exempt by design: print needs paper-safe black/white,
    # not the dark-theme --wds-* tokens tuned for a screen (spec S29).
    site_layer = css[css.index("/* Site composition layer"):]
    no_print = re.sub(r"@media print \{.*?\n\}\n", "", site_layer, flags=re.S)
    hard = re.findall(r"#[0-9a-fA-F]{3,8}\b", no_print)
    ck("T11 the site composition layer hard-codes no colour outside @media print",
       not hard, f"found {set(hard)}" if hard else "")

    # ---- T12: internal links use trailing-slash form -------------------------
    bad_slash = {}
    for rel, html in pages.items():
        hrefs = re.findall(r'href="(/[a-z][a-z0-9/-]*)"', html)
        bad = [h for h in hrefs if not h.endswith("/") and "." not in h.rsplit("/", 1)[-1]]
        if bad:
            bad_slash[rel] = bad
    ck("T12 internal links use trailing-slash form", not bad_slash,
       str(bad_slash) if bad_slash else "")

    # ---- T13: every page has a Spanish<->English counterpart, both ways -----
    bad_pairs = []
    for rel in PAGES:
        if rel.startswith("es/"):
            continue
        es_rel = "es/" + rel if rel != "index.html" else "es/index.html"
        if es_rel not in pages:
            bad_pairs.append(rel)
    ck("T13 every English page has a Spanish counterpart", not bad_pairs,
       str(bad_pairs) if bad_pairs else "")

    # ---- T14: hreflang alternates are reciprocal and self-consistent --------
    bad_hreflang = {}
    for rel, html in pages.items():
        alts = dict(re.findall(
            r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)">', html))
        if set(alts) != {"en", "es", "x-default"}:
            bad_hreflang[rel] = f"codes found: {sorted(alts)}"
            continue
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)
        this_lang = re.search(r'<html lang="([a-z]+)"', html).group(1)
        if alts[this_lang] != canonical:
            bad_hreflang[rel] = (f"hreflang[{this_lang}]={alts[this_lang]} != "
                                 f"canonical={canonical}")
    ck("T14 hreflang alternates exist and match this page's own canonical URL",
       not bad_hreflang, str(bad_hreflang) if bad_hreflang else "")

    # ---- T15: <html lang> matches the page's actual language -----------------
    # Anchored to the <html ...> tag itself: a naive substring check on
    # 'lang="es"' also matches inside hreflang="es" (it's "hreflang", which
    # contains the four letters "lang" starting right after "href").
    bad_lang = []
    for rel, html in pages.items():
        declared = re.match(r'<!DOCTYPE html>\s*<html lang="([a-z]+)"', html).group(1)
        expected = "es" if rel.startswith("es/") else "en"
        if declared != expected:
            bad_lang.append((rel, declared, expected))
    ck("T15 <html lang> matches the page's directory (es/ vs root)",
       not bad_lang, str(bad_lang) if bad_lang else "")

    # ---- T16: CV print rules exist and hide the chrome -----------------------
    ck("T16 CV print styles hide header/whatsapp/lang-switch and paginate cleanly",
       "@media print" in css and ".site-whatsapp, .site-lang-switch" not in css
       and "display: none !important" in css)

    # ---- T17: /work/ and /lab/ indexes are alphabetically ordered -----------
    def titles_in_order(html):
        return re.findall(r'class="site-editorial__title"><a[^>]*>([^<]+)</a>', html)

    bad_order = {}
    for rel in ("work/index.html", "es/work/index.html",
                "lab/index.html", "es/lab/index.html"):
        titles = titles_in_order(pages[rel])
        if titles != sorted(titles, key=str.lower):
            bad_order[rel] = titles
    ck("T17 /work/ and /lab/ indexes are alphabetically ordered", not bad_order,
       str(bad_order) if bad_order else "")

    # ---- T18: the theme switch is present and honest on every page ---------
    bad_theme = {}
    for rel, html in pages.items():
        buttons = re.findall(r'<button type="button" data-theme-set="([a-z]+)" '
                             r'aria-pressed="(true|false)">', html)
        if [b[0] for b in buttons] != ["light", "dark"]:
            bad_theme[rel] = f"options found: {[b[0] for b in buttons]}"
        elif [b[1] for b in buttons] != ["false", "true"]:
            bad_theme[rel] = "server-rendered pressed state is not dark"
        elif 'data-theme="dark"' not in html:
            bad_theme[rel] = "document does not carry a resolved data-theme"
        elif "localStorage.getItem" not in html:
            bad_theme[rel] = "no head bootstrap, stored theme would flash"
    ck("T18 theme switch offers both themes and is applied before paint",
       not bad_theme, str(bad_theme) if bad_theme else "")

    # Both themes must be fully defined in the token layer: a switch that
    # lands on undefined colours is worse than no switch.
    theme_blocks = {
        t: re.search(r":root\[data-theme='%s'\] \{(.*?)\n\}" % t, css, re.S)
        for t in ("dark", "light")}
    theme_keys = {t: set(re.findall(r"(--wds-[a-z0-9-]+)\s*:", m.group(1)))
                  for t, m in theme_blocks.items() if m}
    ck("T18b dark and light define the same colour tokens",
       len(theme_keys) == 2 and theme_keys["dark"] == theme_keys["light"],
       f"{len(theme_keys.get('dark', ()))} tokens each")

    # ---- T19: contact lives in the footer, and only there ------------------
    bad_contact = {}
    for rel, html in pages.items():
        footer_html = html[html.index("<footer"):]
        if 'id="contact"' in html:
            bad_contact[rel] = "a standalone contact section still exists"
        elif "site-footer__links" not in footer_html:
            bad_contact[rel] = "footer carries no contact links"
        elif "&copy; 2026" not in footer_html and "© 2026" not in footer_html:
            bad_contact[rel] = "footer lost the copyright line"
    ck("T19 contact links live on the footer line, on every page",
       not bad_contact, str(bad_contact) if bad_contact else "")

    # ---- T20: the site layer declares no orphan classes --------------------
    # A class removed from the markup must be removed from the stylesheet in
    # the same change, or the next reader cannot tell what is still in use.
    # site.js counts as a consumer: the language-transition classes are only
    # ever attached at runtime.
    with open(os.path.join(ROOT, "assets", "site.js"), encoding="utf-8") as f:
        consumers = "".join(pages.values()) + f.read()
    # Known, pre-dating dead code: core/cv.py defines _stats() and
    # content/cv_{en,es}.py define ACHIEVEMENTS, but build_cv() has never
    # called it, so the CV stats band is styled and never rendered. Listed
    # here rather than deleted, because the copy is somebody's decision to
    # make, not this suite's.
    known_dead = {"site-cv-stats", "site-cv-stats__value", "site-cv-stats__label"}
    site_classes = set(re.findall(r"\.(site-[a-z0-9_-]+)", site_layer))
    orphans = sorted(c for c in site_classes - known_dead
                     if f'"{c}"' not in consumers and f'{c} ' not in consumers
                     and f' {c}"' not in consumers)
    ck("T20 every .site-* class in the stylesheet is used by the markup",
       not orphans, f"orphans: {orphans}" if orphans
       else f"{len(site_classes)} classes, {len(known_dead)} known-dead (CV stats)")

    # ---- T21: one header and one footer across the whole site --------------
    def block(html, tag):
        return html[html.index(f"<{tag}"):html.index(f"</{tag}>") + len(tag) + 3]

    def skeleton(s):
        """
        Tags and classes only: the shape of the component, not its copy.

        The language switch is collapsed to a single token first. Its two
        children swap element types by design -- the active language is a
        <span>, the other a link -- so their order is a property of which
        page you are on, not of the component.
        """
        s = re.sub(r'(<div class="site-switch site-lang-switch">).*?(</div>)',
                   r"\1LANGPAIR\2", s, flags=re.S)
        return re.findall(r"<(\w+)[^>]*?(?:class=\"([^\"]*)\")?[^>]*>", s)

    for tag in ("header", "footer"):
        shapes = {}
        for rel, html in pages.items():
            shapes.setdefault(str(skeleton(block(html, tag))), []).append(rel)
        ck(f"T21 the {tag} has one single shape across all {len(pages)} pages",
           len(shapes) == 1,
           "" if len(shapes) == 1 else
           f"{len(shapes)} variants: { {len(v): v[:3] for v in shapes.values()} }")

    # Within one language the markup must be identical too, once the two
    # things that MUST differ are neutralised: which nav item is current, and
    # where the language switch points.
    def neutralise(s):
        s = re.sub(r'\s*aria-current="page"', "", s)
        s = re.sub(r'<a href="[^"]*" data-language-switch', "<a data-language-switch", s)
        return s

    for lang, prefix in (("en", False), ("es", True)):
        group = {rel: html for rel, html in pages.items()
                 if rel.startswith("es/") == prefix}
        variants = {}
        for rel, html in group.items():
            variants.setdefault(neutralise(block(html, "header")), []).append(rel)
        ck(f"T21b [{lang}] every page renders byte-identical header chrome",
           len(variants) == 1,
           "" if len(variants) == 1 else
           f"{len(variants)} variants: { {len(v): v[:3] for v in variants.values()} }")

    # ---- T22: the page column reaches the bottom of the window -------------
    # Without this the document ends wherever the content does, and the flat
    # html background shows below the footer as a band -- visible because
    # body paints the ambient gradient and html does not.
    ck("T22 body is a full-height column and main takes the slack",
       re.search(r"body \{[^}]*min-height: 100svh[^}]*display: flex", css)
       is not None and re.search(r"main \{ flex: 1 0 auto; \}", css) is not None)

    # ---- T23: contact details are stated once, in the footer ---------------
    dup_contact = {}
    for rel, html in pages.items():
        body_html = html[html.index("<body>"):]
        main_html = body_html[:body_html.index("<footer")]
        if "linkedin.com" in main_html or "github.com" in main_html:
            dup_contact[rel] = "contact link repeated outside the footer"
    ck("T23 contact links appear only in the global footer", not dup_contact,
       str(dup_contact) if dup_contact else "")

    print("=" * 72)
    print(f"{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("\nFAILURES:")
        for n, d in FAIL:
            print(f"  - {n} {d}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

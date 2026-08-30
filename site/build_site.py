# -*- coding: utf-8 -*-
"""
arjuanfelipe.com -- site build.

    CDS -> IPS -> WDS -> Site

The site consumes the WDS's PUBLISHED artefacts (the compiled css/*.css
files), never its build-time Python internals. This is deliberate, not a
shortcut: wds/core and site/core are both packages named "core" -- importing
both by bare name in one process would collide. Consuming the compiled CSS
files instead needs no import at all, and matches how the WDS docs page
itself consumes css/wds.css verbatim (see wds/DECISIONS.md, WDS-009/T20).

The site also consumes identity/cds.json read-only, exactly like
wds/build_wds.py does: the glyph digest is checked, so a drifted identity
stops this build too.

Every English page has a Spanish counterpart at the same path under /es/,
and vice versa -- built together, in the same pass, so neither can exist
without the other (spec S76: "no broken language counterpart links").

Run:  python build_site.py
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import shell
from core.home import build_home
from core.listing import build_listing
from core.detail import build_detail
from core.cv import build_cv
from core.applications import build_applications
from core.css import SITE_CSS
from core.js import SITE_JS
import content.home_en as home_en
import content.home_es as home_es
import content.common_en as common_en
import content.common_es as common_es
import content.work_items_en as work_en
import content.work_items_es as work_es
import content.lab_items_en as lab_en
import content.lab_items_es as lab_es
import content.cv_en as cv_en
import content.cv_es as cv_es
import content.applications_en as apps_en
import content.applications_es as apps_es

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WDS_CSS_DIR = os.path.join(ROOT, "wds", "css")
CDS_PATH = os.path.join(ROOT, "identity", "cds.json")

WRITTEN = []  # (path, bytes) for the summary print at the end


def resolve_cds():
    if not os.path.isfile(CDS_PATH):
        raise SystemExit(
            "SITE ABORT: no CDS found at identity/cds.json. "
            "The site cannot build without the identity it consumes.")
    with open(CDS_PATH, encoding="utf-8") as f:
        cds = json.load(f)
    d = cds["path"]["d"]
    digest = hashlib.sha256(d.encode("utf-8")).hexdigest()
    if digest != cds["path"]["sha256"]:
        raise SystemExit("SITE ABORT: the consumed identity has drifted.")
    return cds, digest


def read_wds_css():
    parts = []
    for name in ("tokens.css", "base.css", "components.css"):
        path = os.path.join(WDS_CSS_DIR, name)
        if not os.path.isfile(path):
            raise SystemExit(
                f"SITE ABORT: {path} not found. Run wds/build_wds.py first "
                "-- the site consumes the WDS's compiled output, not a copy.")
        with open(path, encoding="utf-8") as f:
            parts.append(f.read())
    return "\n".join(parts)


def write(rel_path, html):
    abs_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    WRITTEN.append((rel_path.replace(os.sep, "/"), len(html.encode("utf-8"))))


def build_pages(cds):
    # ---- Home: / <-> /es/ --------------------------------------------------
    write("index.html", build_home(cds, home_en, common_en, "/es/"))
    write("es/index.html", build_home(cds, home_es, common_es, "/"))

    # ---- Work: index + each detail, both languages -------------------------
    write("work/index.html",
          build_listing(cds, work_en.WORK_ITEMS, work_en.INDEX_META,
                         common_en, "work", "/es/work/"))
    write("es/work/index.html",
          build_listing(cds, work_es.WORK_ITEMS, work_es.INDEX_META,
                         common_es, "work", "/work/"))
    for item_en, item_es in zip(work_en.WORK_ITEMS, work_es.WORK_ITEMS):
        slug = item_en["slug"]
        write(f"work/{slug}/index.html",
              build_detail(cds, item_en, common_en, "work", f"/es/work/{slug}/"))
        write(f"es/work/{slug}/index.html",
              build_detail(cds, item_es, common_es, "work", f"/work/{slug}/"))

    # ---- Lab: index + each detail, both languages ---------------------------
    write("lab/index.html",
          build_listing(cds, lab_en.LAB_ITEMS, lab_en.INDEX_META,
                         common_en, "lab", "/es/lab/"))
    write("es/lab/index.html",
          build_listing(cds, lab_es.LAB_ITEMS, lab_es.INDEX_META,
                         common_es, "lab", "/lab/"))
    for item_en, item_es in zip(lab_en.LAB_ITEMS, lab_es.LAB_ITEMS):
        slug = item_en["slug"]
        write(f"lab/{slug}/index.html",
              build_detail(cds, item_en, common_en, "lab", f"/es/lab/{slug}/"))
        write(f"es/lab/{slug}/index.html",
              build_detail(cds, item_es, common_es, "lab", f"/lab/{slug}/"))

    # ---- CV -----------------------------------------------------------------
    write("cv/index.html", build_cv(cds, cv_en, common_en, "/es/cv/"))
    write("es/cv/index.html", build_cv(cds, cv_es, common_es, "/cv/"))

    # ---- Applications: /applications/ <-> /es/applications/ ----------------
    write("applications/index.html",
          build_applications(cds, apps_en, common_en, "/es/applications/"))
    write("es/applications/index.html",
          build_applications(cds, apps_es, common_es, "/applications/"))


def main():
    print("=" * 74)
    print("ARJUANFELIPE.COM -- site build")
    print("=" * 74)

    cds, digest = resolve_cds()
    print(f"\n  consuming CDS {cds['cds_version']} -- "
          f"{cds['identity']['canonical_glyph']}")
    print(f"  identity digest verified: {digest[:32]}...")
    print(f"  wordmark: {cds['identity']['wordmark']!r}")

    wds_css = read_wds_css()
    print(f"  consuming wds/css/{{tokens,base,components}}.css "
          f"({len(wds_css.encode('utf-8'))} B)")

    # ---- assets/site.css ---------------------------------------------------
    site_css = ("/* WDS layer, consumed verbatim -- see build_site.py. */\n"
                + wds_css + "\n"
                + "/* Site composition layer. Generated by build_site.py. */\n"
                + SITE_CSS)
    assets_dir = os.path.join(ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    css_path = os.path.join(assets_dir, "site.css")
    with open(css_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(site_css)
    print(f"\n  assets/site.css       {len(site_css.encode('utf-8')):>6} B")

    js_path = os.path.join(assets_dir, "site.js")
    with open(js_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(SITE_JS)
    print(f"  assets/site.js        {len(SITE_JS.encode('utf-8')):>6} B")

    # One digest over both assets, stamped onto their URLs by the shell. It is
    # set here rather than passed down through build_home/build_listing/... :
    # the version is a property of THIS build, not of any page, and threading
    # it through four signatures would put it in the vocabulary of pages that
    # have no business knowing it. Assigned before a single page is built.
    shell.ASSET_VERSION = hashlib.sha256(
        (site_css + SITE_JS).encode("utf-8")).hexdigest()[:10]
    print(f"  asset version         {shell.ASSET_VERSION}")

    # ---- every HTML page, both languages ------------------------------------
    build_pages(cds)
    print(f"\n  {len(WRITTEN)} pages written:")
    for rel, size in WRITTEN:
        print(f"    {rel:<38} {size:>6} B")

    print("\n" + "=" * 74)
    print("  SITE BUILD OK")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())

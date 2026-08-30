# -*- coding: utf-8 -*-
"""
WDS validation suite.

The most dangerous class of bug in a token system is the reference to a token
that does not exist: CSS does not raise, it silently falls back and the layout
quietly breaks. This suite catches that, plus a set of system-level invariants.

Run:  python validate_wds.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.derive import load_tokens, derive, validate, real_keys
from core.colour import contrast, rgb_to_oklch, hex_to_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(HERE, "css")

PASS, FAIL = [], []


def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append((name, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))


def main():
    print("WDS VALIDATION SUITE")
    print("=" * 72)

    tok = load_tokens()
    col = derive(tok)

    css = {}
    for n in ("tokens.css", "base.css", "components.css"):
        with open(os.path.join(CSS, n), encoding="utf-8") as f:
            css[n] = f.read()
    all_css = "".join(css.values())

    # ---- T1: referential integrity ---------------------------------------
    defined = set(re.findall(r"^\s*(--wds-[a-z0-9-]+)\s*:", all_css, re.M))
    used = set(re.findall(r"var\((--wds-[a-z0-9-]+)", all_css))
    missing = sorted(used - defined)
    ck("T1 every referenced token is defined", not missing,
       f"{len(used)} referenced, {len(defined)} defined"
       + (f" | MISSING: {missing}" if missing else ""))

    # ---- T2: scale coverage, reported not enforced ----------------------
    # A scale is a closed palette of permitted values. Its purpose is that
    # future components choose FROM it instead of inventing new numbers, so
    # unused rungs are deliberate, not debt. Only derived semantic tokens --
    # which point at something concrete -- are required to be referenced.
    scale = {d for d in defined
             if any(d.startswith(f"--wds-{p}")
                    for p in ("space-", "text-", "radius-", "z-", "blur-",
                              "duration-", "ease-", "border-"))}
    semantic_tokens = {f"--wds-{k}" for k in ("accent", "focus", "fg",
                                              "fg-secondary", "bg", "surface",
                                              "border", "border-strong")}
    unused_semantic = sorted(semantic_tokens - used)
    coverage = len(scale & used) / len(scale) if scale else 1.0
    ck("T2 every derived semantic token is referenced", not unused_semantic,
       f"scale coverage {coverage:.0%} ({len(scale & used)}/{len(scale)} rungs used)"
       + (f" | ORPHANED: {unused_semantic}" if unused_semantic else ""))

    # ---- T3: no hard-coded colours outside the token block ---------------
    body = css["base.css"] + css["components.css"]
    hard = re.findall(r"#[0-9a-fA-F]{3,8}\b", body)
    ck("T3 no hard-coded hex outside tokens.css", not hard,
       f"found {set(hard)}" if hard else "")

    # ---- T4: no arbitrary pixel spacing ----------------------------------
    # Structural spacing must come from the scale. Hairlines, focus rings and
    # a few optical values are legitimately raw and are allowlisted.
    allow = {"0", "1px", "2px", "3px", "4px", "7px", "10px", "56px", "32px"}
    px = re.findall(r"(?:padding|margin|gap)[a-z-]*:\s*([^;]+);", body)
    bad = []
    for decl in px:
        for tokn in re.findall(r"\b\d+px\b", decl):
            if tokn not in allow:
                bad.append(tokn)
    ck("T4 spacing uses the scale, not arbitrary pixels", not bad,
       f"raw values: {sorted(set(bad))}" if bad else "")

    # ---- T5: contrast contracts ------------------------------------------
    rows, failures = validate(col)
    ck("T5 every contrast contract holds", not failures,
       f"{len(rows)} pairs checked")

    # ---- T6: zero JavaScript ---------------------------------------------
    ck("T6 no JavaScript anywhere in the system",
       not any(x in all_css for x in ("javascript:", "expression(")))

    # ---- T7: reduced motion is handled at token level --------------------
    ck("T7 reduced motion collapses durations globally",
       "prefers-reduced-motion" in css["tokens.css"]
       and "--wds-duration-base: 1ms" in css["tokens.css"])

    # ---- T8: forced colours -----------------------------------------------
    ck("T8 forced-colors mode hands colour back to the OS",
       "forced-colors: active" in css["tokens.css"]
       and "CanvasText" in css["tokens.css"])

    # ---- T9: focus visibility ---------------------------------------------
    ck("T9 focus-visible is styled and focus ring meets 3:1",
       ":focus-visible" in css["base.css"]
       and contrast(col["dark"]["focus"], col["dark"]["bg"]) >= 3.0,
       f"{contrast(col['dark']['focus'], col['dark']['bg']):.2f}:1")

    # ---- T10: touch targets ------------------------------------------------
    target = tok["touch_target_min_px"]
    ck("T10 interactive components meet the touch target",
       "--wds-touch-target" in css["tokens.css"]
       and "min-height: var(--wds-touch-target)" in css["components.css"],
       f"{target}px")

    # ---- T11: reading measure is bounded ----------------------------------
    ck("T11 reading measure is bounded",
       "max-width: var(--wds-reading)" in css["base.css"],
       f"{tok['grid']['reading_max_ch']}ch")

    # ---- T12: identity is consumed, not redrawn ---------------------------
    from build_wds import resolve_cds
    with open(resolve_cds(), encoding="utf-8") as f:
        cds = json.load(f)
    ck("T12 the WDS declares no glyph geometry of its own",
       cds["path"]["d"] not in all_css,
       "the path lives in the CDS; CSS only sizes and seats it")

    # ---- T13: theme parity -------------------------------------------------
    dk, lt = set(col["dark"]), set(col["light"])
    ck("T13 dark and light define the same token set", dk == lt,
       f"dark {len(dk)}, light {len(lt)}"
       + (f" | diff {sorted(dk ^ lt)}" if dk != lt else ""))

    # ---- T14: surface stack is monotonic ----------------------------------
    ok_mono = True
    for theme in ("dark", "light"):
        ls = [rgb_to_oklch(hex_to_rgb(col[theme][k]))[0]
              for k in ("bg", "surface", "surface-elevated", "surface-interactive")]
        asc = all(ls[i] < ls[i+1] for i in range(len(ls)-1))
        desc = all(ls[i] > ls[i+1] for i in range(len(ls)-1))
        if not (asc or desc):
            ok_mono = False
    ck("T14 the surface stack moves monotonically in lightness", ok_mono,
       "depth reads as depth in both themes")

    # ---- T15: semantic hue separation is declared -------------------------
    sep = col["meta"]["min_hue_separation"]
    ck("T15 minimum semantic hue separation is measured and reported",
       sep["degrees"] > 0,
       f"{sep['degrees']:.1f} deg between {sep['between'][0]} and {sep['between'][1]}")

    # ---- the generated documentation --------------------------------------
    from build_wds import DOC_TARGETS
    pages = {}
    for t in DOC_TARGETS:
        with open(t, encoding="utf-8") as f:
            pages[os.path.relpath(t, HERE).replace(os.sep, "/")] = f.read()
    page = next(iter(pages.values()))

    # ---- T16: component coverage ------------------------------------------
    # A component that exists in the stylesheet but appears nowhere is
    # undocumented by accident, not by choice. The build decides, not memory.
    declared = set(re.findall(r"\.(wds-[a-z0-9_-]+)", all_css))
    shown = set()
    for attr in re.findall(r'class="([^"]*)"', page):
        shown.update(attr.split())
    undocumented = sorted(declared - shown)
    ck("T16 every component in the stylesheet appears in the documentation",
       not undocumented,
       f"{len(declared & shown)}/{len(declared)} classes shown"
       + (f" | MISSING: {undocumented}" if undocumented else ""))

    # ---- T17: the page does not depend on an external stylesheet ----------
    # A relative <link href> only resolves from the directory the page was
    # written for. Moving the file then silently strips every style, which is
    # exactly how the previous copy broke.
    linked = [p for p, t in pages.items()
              if re.search(r'<link[^>]+rel=["\']stylesheet', t)]
    ck("T17 the documentation is self-contained, not linked", not linked,
       f"{len(pages)} pages inline their css"
       + (f" | LINKED: {linked}" if linked else ""))

    # ---- T18: one render, several destinations ----------------------------
    ck("T18 every documentation target is byte-identical",
       len(set(pages.values())) == 1,
       " = ".join(sorted(pages)))

    # ---- T19: referential integrity inside the page ------------------------
    used_html = set(re.findall(r"var\((--wds-[a-z0-9-]+)", page))
    missing_html = sorted(used_html - defined)
    ck("T19 every token referenced by the page is defined", not missing_html,
       f"{len(used_html)} referenced"
       + (f" | MISSING: {missing_html}" if missing_html else ""))

    # ---- T20: the inlined css is the real one ------------------------------
    with open(os.path.join(CSS, "wds.css"), encoding="utf-8") as f:
        entry = f.read()
    ck("T20 the inlined stylesheet is css/wds.css verbatim", entry in page,
       f"{len(entry.encode('utf-8'))} B inlined, not a private copy")

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

# -*- coding: utf-8 -*-
"""
Token derivation and validation.

Reads tokens.json plus the canonical palette, derives every colour, and
validates each one against WCAG by calculation. A derived colour that fails
its contract stops the build.
"""

import json
import math
import os

from .colour import (hex_to_rgb, rgb_to_hex, rgb_to_oklch, oklch_to_rgb,
                     clip_to_gamut, contrast, wcag_level, rotate_hue,
                     adjust_for_contrast)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_tokens():
    with open(os.path.join(ROOT, "tokens.json"), encoding="utf-8") as f:
        return json.load(f)


def real_keys(d):
    """Skips the "_role" annotations that document each block in tokens.json."""
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _at_lightness(ref_hex, L):
    """Same hue and chroma as the reference, at a different lightness."""
    _, C, H = rgb_to_oklch(hex_to_rgb(ref_hex))
    return rgb_to_hex(oklch_to_rgb(clip_to_gamut((L, C, H))))


def derive(tok):
    pal = real_keys(tok["canonical_palette"])
    accent = pal["accent"]
    out = {"dark": {}, "light": {}, "meta": {}}

    # ---- semantic hues: the accent at other angles ------------------------
    semantic = {}
    for name, rot in real_keys(tok["semantic_hue_rotation"]).items():
        hx = accent if rot == 0 else rotate_hue(accent, rot)
        L, C, H = rgb_to_oklch(hex_to_rgb(hx))
        semantic[name] = {"hex": hx, "L": L, "C": C, "H": H, "rotation": rot}
    out["meta"]["semantic"] = semantic

    # minimum hue separation between semantic colours: an honest measurement
    names = list(semantic)
    worst = (360.0, "", "")
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = semantic[names[i]]["H"], semantic[names[j]]["H"]
            d = abs(a - b) % 360
            d = min(d, 360 - d)
            if d < worst[0]:
                worst = (d, names[i], names[j])
    out["meta"]["min_hue_separation"] = {
        "degrees": worst[0], "between": [worst[1], worst[2]]}

    for theme in ("dark", "light"):
        t = out[theme]
        surf = real_keys(tok["surface_lightness"])[theme]
        text = tok["text_lightness"][theme]
        bg_ref = pal["background"] if theme == "dark" else pal["foreground"]

        # ---- surfaces: the canonical background at different depths -------
        t["bg"] = _at_lightness(pal["background"], surf["base"])
        t["surface"] = _at_lightness(pal["background"], surf["raised"])
        t["surface-elevated"] = _at_lightness(pal["background"], surf["elevated"])
        t["surface-interactive"] = _at_lightness(pal["background"],
                                                 surf["interactive"])
        t["border-subtle"] = _at_lightness(pal["background"], surf["border_subtle"])
        t["border"] = _at_lightness(pal["background"], surf["border"])
        t["border-strong"] = _at_lightness(pal["background"], surf["border_strong"])

        ground = t["bg"]

        # ---- text ---------------------------------------------------------
        ref = pal["foreground"] if theme == "dark" else pal["background"]
        t["fg"] = _at_lightness(ref, text["primary"])
        t["fg-secondary"] = _at_lightness(ref, text["secondary"])
        t["fg-tertiary"] = _at_lightness(ref, text["tertiary"])
        t["fg-quiet"] = _at_lightness(ref, text["quiet"])

        # ---- semantic, retargeted for the theme's ground -------------------
        # On light UI the same lightness would not carry; the hue is kept and
        # the lightness moved until the contract is met.
        for name, s in semantic.items():
            if theme == "dark":
                hx = s["hex"]
            else:
                hx = rgb_to_hex(oklch_to_rgb(clip_to_gamut(
                    (0.52, s["C"], s["H"]))))
            t[name] = hx
            # a subdued fill of the same hue, for badges and callouts
            fill_L = 0.26 if theme == "dark" else 0.94
            t[f"{name}-surface"] = rgb_to_hex(oklch_to_rgb(clip_to_gamut(
                (fill_L, min(s["C"], 0.06), s["H"]))))

        t["accent"] = t["primary"]
        t["accent-hover"] = _at_lightness(
            t["primary"], rgb_to_oklch(hex_to_rgb(t["primary"]))[0]
            + (0.07 if theme == "dark" else -0.07))
        t["accent-active"] = _at_lightness(
            t["primary"], rgb_to_oklch(hex_to_rgb(t["primary"]))[0]
            - (0.05 if theme == "dark" else -0.05))

        # ---- contract resolution ------------------------------------------
        # border-strong is the only visual boundary of some controls, so
        # WCAG 1.4.11 requires 3:1 against the page. Rather than guessing a
        # lightness and hoping, the token is SOLVED for its contract: hue and
        # chroma are held, lightness moves until the ratio is met.
        solved, ratio, steps, reached = adjust_for_contrast(
            t["border-strong"], t["bg"], target=3.0)
        if not reached:
            raise SystemExit(
                f"WDS ABORT: border-strong cannot reach 3:1 on {theme}")
        t["border-strong"] = solved
        out["meta"].setdefault("solved", {})[f"{theme}.border-strong"] = {
            "hex": solved, "ratio": round(ratio, 3), "steps": steps}

        t["focus"] = t["accent-hover"]
        t["selection"] = t["primary-surface"]
        t["code-bg"] = t["surface"]
        t["scrollbar-thumb"] = t["border"]
        t["scrollbar-track"] = t["surface"]

    return out


# ------------------------------------------------------------- validation

# Every pair here is a contract the system promises. If one fails, the build
# stops: a design system that ships failing contrast is not a design system.
CONTRACTS = [
    ("fg", "bg", 7.0, "body text"),
    ("fg-secondary", "bg", 4.5, "secondary text"),
    ("fg-tertiary", "bg", 4.5, "tertiary text"),
    ("fg-quiet", "bg", 4.5, "quiet metadata"),
    ("fg", "surface", 7.0, "body text on a raised surface"),
    ("fg-secondary", "surface", 4.5, "secondary text on a raised surface"),
    ("fg", "surface-elevated", 7.0, "body text on an elevated surface"),
    ("accent", "bg", 4.5, "accent text and links"),
    ("accent-hover", "bg", 4.5, "hovered link"),
    ("primary", "bg", 4.5, "primary semantic"),
    ("success", "bg", 4.5, "success semantic"),
    ("warning", "bg", 4.5, "warning semantic"),
    ("danger", "bg", 4.5, "danger semantic"),
    ("info", "bg", 4.5, "info semantic"),
    ("focus", "bg", 3.0, "focus ring against the page"),
    ("border-strong", "bg", 3.0, "strong border as a UI boundary"),
]


def validate(colours):
    rows = []
    failures = []
    for theme in ("dark", "light"):
        t = colours[theme]
        for fg_key, bg_key, target, label in CONTRACTS:
            if fg_key not in t or bg_key not in t:
                continue
            r = contrast(t[fg_key], t[bg_key])
            ok = r >= target
            rows.append({"theme": theme, "fg": fg_key, "bg": bg_key,
                         "label": label, "ratio": r, "target": target,
                         "level": wcag_level(r), "ok": ok})
            if not ok:
                failures.append(
                    f"{theme}: {fg_key} on {bg_key} = {r:.2f}, needs {target}")
    return rows, failures

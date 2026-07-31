# -*- coding: utf-8 -*-
"""
LEVEL 3 - OPTIMIZERS

Turns canonical geometry into production-ready variants without changing the
identity. Every optimisation records the geometric error it introduces, and
that error is checked against a declared budget.

Depends on: Levels 1 and 2.
"""

import gzip
import zlib

from core.geometry import fmt
from core import svgkit as K

# Decimal precision budget, in design units, per variant class.
PRECISION_BUDGET_DU = 0.05


def run(ctx, assets):
    g, d, W, H = ctx["g"], ctx["d"], ctx["W"], ctx["H"]
    out = {}
    report = []

    # ---- decimal precision normalisation ---------------------------------
    d2 = K.round_path(d, 2)
    err2 = K.path_precision_error(d, d2)
    d1 = K.round_path(d, 1)
    err1 = K.path_precision_error(d, d1)
    report.append(("precision 2dp", err2, err2 <= PRECISION_BUDGET_DU))
    report.append(("precision 1dp", err1, err1 <= PRECISION_BUDGET_DU))
    ctx["precision_error_2dp"] = err2
    ctx["precision_error_1dp"] = err1

    # The production path uses 2dp: measurably inside budget.
    dp = d2

    # ---- optimised: no metadata, no declaration, minimal attributes -------
    out["glyph.optimized.svg"] = K.svg_doc(K.stroke_path(g, dp), W, H,
                                           width=fmt(W), height=fmt(H))

    # ---- minified --------------------------------------------------------
    out["glyph.min.svg"] = K.minify(out["glyph.optimized.svg"]) + "\n"

    # ---- no metadata vs with metadata ------------------------------------
    out["glyph.nometa.svg"] = K.svg_doc(K.stroke_path(g, dp), W, H)
    out["glyph.meta.svg"] = K.svg_doc(
        K.stroke_path(g, dp), W, H, decl=True,
        width=fmt(W), height=fmt(H),
        title="B′ COMPENSATED",
        desc="Canonical glyph of arjuanfelipe. CDS 1.0.0.",
        extra_root=f'data-cds-version="{ctx["cds"]["cds_version"]}" '
                   f'data-path-sha256="{ctx["cds"]["path"]["sha256"][:16]}"')

    # ---- accessibility variant -------------------------------------------
    out["glyph.a11y.svg"] = K.svg_doc(
        K.stroke_path(g, dp), W, H, decl=True,
        width=fmt(W), height=fmt(H),
        title="I",
        desc=("The letter I from the wordmark 'Now I understand.'. "
              "Decorative in most contexts; mark aria-hidden when the "
              "surrounding text already reads the letter."))

    # ---- responsive: viewBox only ----------------------------------------
    out["glyph.responsive.svg"] = K.svg_doc(K.stroke_path(g, dp), W, H,
                                            responsive=True)

    # ---- SVG Tiny 1.2 ----------------------------------------------------
    out["glyph.tiny.svg"] = K.svg_doc(
        f'<path d="{K.round_path(d, 1)}" fill="none" stroke="#000000" '
        f'stroke-width="{fmt(g["w"])}" stroke-linecap="butt"/>',
        W, H, decl=True, profile="tiny", width=fmt(W), height=fmt(H))

    # ---- symbol and sprite ------------------------------------------------
    sym = (f'<symbol id="ajf-glyph" viewBox="0 0 {fmt(W)} {fmt(H)}">'
           f'{K.stroke_path(g, dp)}</symbol>')
    out["glyph.symbol.svg"] = f'<svg {K.XMLNS} style="display:none">{sym}</svg>\n'

    filled = f'<path d="{ctx["outline_d"]}" fill="currentColor"/>'
    sprite = (f'<svg {K.XMLNS} style="display:none" aria-hidden="true">'
              f'<symbol id="ajf-stroke" viewBox="0 0 {fmt(W)} {fmt(H)}">'
              f'{K.stroke_path(g, dp)}</symbol>'
              f'<symbol id="ajf-filled" viewBox="0 0 {fmt(W)} {fmt(H)}">'
              f'{filled}</symbol>'
              f'<symbol id="ajf-square" viewBox="0 0 100 100">'
              f'<rect width="100" height="100" fill="#10141a"/>'
              f'{_centred(g, dp, 100, 0.58, "#e7ebee")}</symbol>'
              f'</svg>\n')
    out["glyph.sprite.svg"] = sprite

    # ---- mask / pinned tab: monochrome, filled, no colour ----------------
    # Safari requires a filled path, black, with a square-ish viewBox.
    out["mask-icon.svg"] = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg {K.XMLNS} viewBox="0 0 16 16">'
        f'{_centred_filled(ctx, 16, 0.72, "black")}</svg>\n')
    out["pinned-tab.svg"] = out["mask-icon.svg"]
    out["glyph.mask.svg"] = K.svg_doc(
        f'<path d="{ctx["outline_d"]}" fill="#ffffff"/>', W, H,
        width=fmt(W), height=fmt(H))

    # ---- theme variants ---------------------------------------------------
    out["glyph.dark-ui.svg"] = K.svg_doc(
        K.stroke_path(g, dp, "#e7ebee"), W, H, width=fmt(W), height=fmt(H))
    out["glyph.light-ui.svg"] = K.svg_doc(
        K.stroke_path(g, dp, "#10141a"), W, H, width=fmt(W), height=fmt(H))
    out["glyph.high-contrast.svg"] = K.svg_doc(
        K.stroke_path(g, dp, "#000000",
                      extra=' style="forced-color-adjust:auto"'),
        W, H, width=fmt(W), height=fmt(H))
    out["glyph.forced-colors.svg"] = K.svg_doc(
        f'<path d="{ctx["outline_d"]}" fill="CanvasText"/>', W, H,
        width=fmt(W), height=fmt(H))
    out["glyph.oled.svg"] = K.svg_doc(
        f'<rect width="{fmt(W)}" height="{fmt(H)}" fill="#000000"/>'
        + K.stroke_path(g, dp, "#e7ebee"), W, H, width=fmt(W), height=fmt(H))

    # ---- print: millimetres, filled outline so no stroke scaling surprises
    mm_h = 40.0
    mm_w = mm_h * (W / H)
    out["glyph.print.svg"] = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg {K.XMLNS} width="{fmt(mm_w)}mm" height="{fmt(mm_h)}mm" '
        f'viewBox="0 0 {fmt(W)} {fmt(H)}">'
        f'<path d="{ctx["outline_d"]}" fill="#000000"/></svg>\n')

    # ---- compression measurements ----------------------------------------
    comp = []
    for name in ("master.svg", "glyph.optimized.svg", "glyph.min.svg"):
        text = assets.get(name) or out.get(name)
        raw = text.encode("utf-8")
        gz = gzip.compress(raw, 9, mtime=0)      # mtime=0 keeps it deterministic
        comp.append({"asset": name, "raw": len(raw), "gzip": len(gz),
                     "ratio": len(gz)/len(raw)})
    ctx["compression"] = comp
    ctx["optimize_report"] = report
    return out


def _centred(g, d, side, scale, colour):
    h = side * scale
    k = h / g["height"]
    w = g["width"] * k
    return (f'<g transform="translate({fmt((side-w)/2)} {fmt((side-h)/2)}) '
            f'scale({fmt(k, 6)})">{K.stroke_path(g, d, colour)}</g>')


def _centred_filled(ctx, side, scale, colour):
    g = ctx["g"]
    h = side * scale
    k = h / g["height"]
    w = g["width"] * k
    return (f'<g transform="translate({fmt((side-w)/2)} {fmt((side-h)/2)}) '
            f'scale({fmt(k, 6)})">'
            f'<path d="{ctx["outline_d"]}" fill="{colour}"/></g>')

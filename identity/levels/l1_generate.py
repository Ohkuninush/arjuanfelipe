# -*- coding: utf-8 -*-
"""
LEVEL 1 - GENERATOR

Transforms the CDS into canonical geometry and the master vector assets.
No optimisation happens here. Generation is mathematically deterministic.

Depends on: Level 0 (cds.json) only.
"""

from core.geometry import load_cds, build_geometry, path_d
from core import svgkit as K


def run(ctx):
    cds = load_cds()
    g = build_geometry(cds)
    d = path_d(g)

    # Gate: canonical geometry must match the frozen literals before anything
    # downstream is allowed to exist.
    lit = cds["control_points"]
    eps = cds["tolerances"]["control_point_precision_du"]
    for n in ("P0", "C1", "C2", "P3", "L1", "Q1", "Q2", "P6"):
        for i in (0, 1):
            if abs(lit[n][i] - g[n][i]) > eps:
                raise SystemExit(f"L1 ABORT: {n} deviates from the CDS literal")
    if d != cds["path"]["d"]:
        raise SystemExit("L1 ABORT: generated path differs from the CDS literal")

    W, H = g["width"], g["height"]

    # Canonical outline: the stroke converted to a filled contour.
    out_d = K.outline_d(g, n=ctx["outline_samples"])
    out_err = K.outline_error(g, n=ctx["outline_samples"])

    ctx.update({
        "cds": cds, "g": g, "d": d, "W": W, "H": H,
        "outline_d": out_d, "outline_chord_error_du": out_err,
    })

    assets = {}

    # ---- master: full precision, stroke, with metadata and accessibility ---
    assets["master.svg"] = K.svg_doc(
        K.stroke_path(g, d), W, H,
        width=K.fmt(W), height=K.fmt(H), decl=True,
        title="B′ COMPENSATED",
        desc=("The capital I of the wordmark 'Now I understand.' "
              "Rotationally symmetric about its centre."))

    # ---- pretty: human-readable, for inspection and diffing ---------------
    assets["master.pretty.svg"] = K.svg_doc(
        K.stroke_path(g, d), W, H, pretty=True,
        width=K.fmt(W), height=K.fmt(H), decl=True,
        title="B′ COMPENSATED")

    # ---- stroke and filled are genuinely different geometry ---------------
    assets["glyph.stroke.svg"] = K.svg_doc(K.stroke_path(g, d), W, H,
                                           width=K.fmt(W), height=K.fmt(H))
    assets["glyph.filled.svg"] = K.svg_doc(
        f'<path d="{out_d}" fill="currentColor" fill-rule="nonzero"/>',
        W, H, width=K.fmt(W), height=K.fmt(H))
    assets["glyph.outline.svg"] = K.svg_doc(
        f'<path d="{out_d}" fill="none" stroke="currentColor" '
        f'stroke-width="1" vector-effect="non-scaling-stroke"/>',
        W, H, width=K.fmt(W), height=K.fmt(H))

    return assets

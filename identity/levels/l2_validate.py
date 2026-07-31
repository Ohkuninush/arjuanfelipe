# -*- coding: utf-8 -*-
"""
LEVEL 2 - VALIDATORS

Verifies the geometry produced by Level 1. This level never modifies anything;
it only measures and reports. A failure here stops the pipeline.

Depends on: Level 1.
"""

import hashlib
import math

from core.geometry import (bez_d1, curvature, coverage, coverage_centred,
                           path_d, build_geometry)
from core import svgkit as K


def _pinch_and_optics(g, cap_px, ss):
    """Rasterises once and derives several optical measurements from it."""
    rows, W, H = coverage(g, cap_px, ss=ss)
    s = cap_px / g["cap"]

    ink = sum(sum(r) for r in rows)

    # stroke collapse: widest run of covered pixels per row in the straight run
    lo = int((g["y_top"] + g["elev"] + g["w"]) * s)
    hi = int((g["y_bot"] - g["elev"] - g["w"]) * s)
    runs = []
    for y in range(max(0, lo), min(H, hi)):
        runs.append(sum(1 for v in rows[y] if v > 0.5))
    stem_px = g["w"] * s

    # edge sharpness: fraction of covered pixels that are partial, i.e. the
    # antialiased fringe. High fringe at small sizes means the mark is mush.
    partial = sum(1 for r in rows for v in r if 0.02 < v < 0.98)
    covered = sum(1 for r in rows for v in r if v > 0.02)

    # symmetry: compare against the raster's own 180 degree rotation.
    # Measured on a centred canvas, otherwise this measures the framing.
    crows, cw, chh = coverage_centred(g, cap_px, ss=ss)
    err = 0.0
    for y in range(chh):
        for x in range(cw):
            err = max(err, abs(crows[y][x] - crows[chh-1-y][cw-1-x]))

    return {
        "cap_px": cap_px,
        "ink_px2": ink,
        "stem_nominal_px": stem_px,
        "stem_min_px": min(runs) if runs else 0,
        "stroke_collapsed": bool(runs) and min(runs) < 1,
        "fringe_ratio": (partial / covered) if covered else 0.0,
        "symmetry_error": err,
        "raster_w": W, "raster_h": H,
    }


def run(ctx, assets):
    g = ctx["g"]
    cds = ctx["cds"]
    results = []
    failures = []

    def ck(name, ok, detail=""):
        results.append((name, ok, detail))
        if not ok:
            failures.append(f"{name} {detail}")

    # ---- geometric validation --------------------------------------------
    axis, cap = g["axis"], g["cap"]
    worst = 0.0
    for a, b in (("P0", "P6"), ("C1", "Q2"), ("C2", "Q1"), ("P3", "L1")):
        r = (2*axis - g[a][0], cap - g[a][1])
        worst = max(worst, abs(r[0]-g[b][0]), abs(r[1]-g[b][1]))
    ck("G1 rotational symmetry exact", worst == 0.0, f"{worst:.2e} du")

    up = (g["P0"], g["C1"], g["C2"], g["P3"])
    ck("G2 terminal tangent horizontal", abs(bez_d1(*up, 0.0)[1]) < 1e-9)
    ck("G3 stem tangent vertical", abs(bez_d1(*up, 1.0)[0]) < 1e-9)
    ck("G4 bounding box matches CDS",
       abs(g["width"] - cds["bounding_box"]["width"]) < 1e-9)
    ck("G5 aspect ratio", abs(g["width"]/g["height"] - 0.14931) < 1e-5,
       f"{g['width']/g['height']:.6f}")

    # ---- canonical constants ---------------------------------------------
    dig = hashlib.sha256(ctx["d"].encode("utf-8")).hexdigest()
    ck("C1 path digest matches CDS", dig == cds["path"]["sha256"], dig[:16])
    ck("C2 stroke width is the frozen literal",
       g["w"] == cds["parameters"]["stroke_width"], str(g["w"]))

    # ---- outline fidelity -------------------------------------------------
    ck("O1 outline chord error below tolerance",
       ctx["outline_chord_error_du"] < 0.01,
       f"{ctx['outline_chord_error_du']:.2e} du")

    # ---- SVG structural validation ---------------------------------------
    for name, text in assets.items():
        if not name.endswith(".svg"):
            continue
        ok, msg = K.xml_wellformed(text)
        if not ok:
            ck(f"X {name} is well-formed XML", False, msg)
    ck("X1 all generated SVG is well-formed XML",
       not any(f.startswith("X ") for f in failures))

    ok, msg = K.validate_viewbox(assets["master.svg"], g["width"], g["height"])
    ck("X2 master viewBox is correct", ok, msg)

    # ---- perceptual / optical validation across the size ladder ----------
    ladder = ctx["size_ladder"]
    optics = []
    for px in ladder:
        ss = 6 if px <= 32 else (4 if px <= 128 else 2)
        optics.append(_pinch_and_optics(g, px, ss))
    ctx["optics"] = optics

    collapsed = [o["cap_px"] for o in optics if o["stroke_collapsed"]]
    ck("P1 stroke never collapses across the ladder", not collapsed,
       f"collapsed at {collapsed}" if collapsed else f"{len(ladder)} sizes")

    sym = max(o["symmetry_error"] for o in optics)
    ck("P2 rendered symmetry holds at every size", sym < 0.02,
       f"max raster asymmetry {sym:.4f}")

    thin = [o["cap_px"] for o in optics if o["stem_min_px"] < 1.0]
    ck("P3 stem stays at least one pixel wide", not thin,
       f"sub-pixel stem at {thin}" if thin else "")

    ctx["validation"] = results
    return results, failures

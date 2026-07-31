# -*- coding: utf-8 -*-
"""
THIRD-PARTY RECONSTRUCTION TEST

Simulates an engineer who has never seen this conversation and holds only
cds.json. This file deliberately does NOT import geometry.py. It re-implements
the construction from the algorithm written in the specification and checks
whether the result is the canonical glyph.

If this fails, the CDS is incomplete by its own definition.

Run:  python third_party.py
"""

import hashlib
import json
import math
import sys

TOL = 1e-9


def reconstruct(params, cap_key="cap_height"):
    """
    Implemented ONLY from cds.json -> construction_algorithm.steps.
    No knowledge of the generator is used.
    """
    cap = float(params["cap_height"])
    w = float(params["stroke_width"])
    over = float(params["overhang"])
    elev = float(params["elevation"])
    h1 = float(params["handle_horizontal"])
    h2 = float(params["handle_vertical"])

    half_stroke = w / 2.0
    semi_extent = over + half_stroke
    axis_x = semi_extent
    y_top = half_stroke
    y_bottom = cap - half_stroke

    def rotate180(p):
        return (2.0 * axis_x - p[0], cap - p[1])

    P0 = (axis_x + semi_extent, y_top)
    C1 = (axis_x + semi_extent * (1.0 - h1), y_top)
    C2 = (axis_x, y_top + elev * h2)
    P3 = (axis_x, y_top + elev)
    L1 = rotate180(P3)
    Q1 = rotate180(C2)
    Q2 = rotate180(C1)
    P6 = rotate180(P0)

    return {"P0": P0, "C1": C1, "C2": C2, "P3": P3,
            "L1": L1, "Q1": Q1, "Q2": Q2, "P6": P6,
            "_derived": {"half_stroke": half_stroke, "semi_extent": semi_extent,
                         "axis_x": axis_x, "y_top": y_top, "y_bottom": y_bottom,
                         "total_width": 2.0 * semi_extent}}


def fmt(v, nd=3):
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def emit_path(pts, nd=3):
    o = pts
    return (f"M{fmt(o['P0'][0],nd)} {fmt(o['P0'][1],nd)} "
            f"C{fmt(o['C1'][0],nd)} {fmt(o['C1'][1],nd)} "
            f"{fmt(o['C2'][0],nd)} {fmt(o['C2'][1],nd)} "
            f"{fmt(o['P3'][0],nd)} {fmt(o['P3'][1],nd)} "
            f"L{fmt(o['L1'][0],nd)} {fmt(o['L1'][1],nd)} "
            f"C{fmt(o['Q1'][0],nd)} {fmt(o['Q1'][1],nd)} "
            f"{fmt(o['Q2'][0],nd)} {fmt(o['Q2'][1],nd)} "
            f"{fmt(o['P6'][0],nd)} {fmt(o['P6'][1],nd)}")


def main():
    with open("cds.json", "r", encoding="utf-8") as f:
        cds = json.load(f)

    print("THIRD-PARTY RECONSTRUCTION FROM cds.json ALONE")
    print("=" * 70)
    print("  inputs used: parameters, construction_algorithm")
    print("  geometry.py: NOT imported\n")

    got = reconstruct(cds["parameters"])
    fails = []

    # 1. control points
    print("  control points")
    print("    name   reconstructed              CDS literal               error")
    print("    " + "-" * 62)
    for n in ("P0", "C1", "C2", "P3", "L1", "Q1", "Q2", "P6"):
        want = cds["control_points"][n]
        g = got[n]
        e = max(abs(want[0]-g[0]), abs(want[1]-g[1]))
        if e > TOL:
            fails.append(f"control point {n}: error {e:.2e}")
        print(f"    {n:<6} ({g[0]:>9.4f},{g[1]:>10.4f})  "
              f"({want[0]:>9.3f},{want[1]:>10.3f})  {e:.2e}")

    # 2. derived values
    print("\n  derived values")
    dv = cds["derived"]
    for k in ("half_stroke", "semi_extent", "axis_x", "y_top", "total_width"):
        want = float(dv[k])
        g = got["_derived"][k]
        e = abs(want - g)
        if e > TOL:
            fails.append(f"derived {k}: error {e:.2e}")
        print(f"    {k:<14} {g:>12.6f}  vs CDS {want:>12.6f}   {e:.2e}")
    e = abs(float(dv["y_bottom"]) - got["_derived"]["y_bottom"])
    if e > TOL:
        fails.append(f"derived y_bottom: error {e:.2e}")
    print(f"    {'y_bottom':<14} {got['_derived']['y_bottom']:>12.6f}  "
          f"vs CDS {float(dv['y_bottom']):>12.6f}   {e:.2e}")

    # 3. path string
    d = emit_path(got)
    ok_path = (d == cds["path"]["d"])
    if not ok_path:
        fails.append("path string mismatch")
    print(f"\n  path string identical to CDS : {'YES' if ok_path else 'NO'}")
    if not ok_path:
        print(f"    CDS   : {cds['path']['d']}")
        print(f"    built : {d}")

    # 4. digest
    dig = hashlib.sha256(d.encode("utf-8")).hexdigest()
    ok_dig = (dig == cds["path"]["sha256"])
    if not ok_dig:
        fails.append("sha256 mismatch")
    print(f"  sha256 matches CDS           : {'YES' if ok_dig else 'NO'}")
    print(f"    {dig}")

    # 5. independently verifiable structural claims
    print("\n  independent structural checks")
    axis = got["_derived"]["axis_x"]
    cap = float(cds["parameters"]["cap_height"])
    worst = 0.0
    for a, b in (("P0", "P6"), ("C1", "Q2"), ("C2", "Q1"), ("P3", "L1")):
        r = (2*axis - got[a][0], cap - got[a][1])
        worst = max(worst, abs(r[0]-got[b][0]), abs(r[1]-got[b][1]))
    if worst > TOL:
        fails.append("rotational symmetry")
    print(f"    rotational symmetry error   : {worst:.2e} du")

    dy = got["C1"][1] - got["P0"][1]
    if abs(dy) > TOL:
        fails.append("terminal tangent not horizontal")
    print(f"    terminal tangent dy         : {abs(dy):.2e}")

    dx = got["P3"][0] - got["C2"][0]
    if abs(dx) > TOL:
        fails.append("stem tangent not vertical")
    print(f"    stem junction tangent dx    : {abs(dx):.2e}")

    bb = cds["bounding_box"]
    ebb = max(abs(got["_derived"]["total_width"] - bb["width"]),
              abs(cap - bb["height"]))
    if ebb > TOL:
        fails.append("bounding box")
    print(f"    bounding box error          : {ebb:.2e} du")

    print("\n" + "=" * 70)
    if fails:
        print("RECONSTRUCTION FAILED — the CDS is incomplete by its own definition.")
        for f_ in fails:
            print(f"  - {f_}")
        return 1
    print("RECONSTRUCTION EXACT.")
    print("A third party holding only cds.json recovers the canonical glyph")
    print("bit-for-bit. The CDS satisfies its own completeness requirement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

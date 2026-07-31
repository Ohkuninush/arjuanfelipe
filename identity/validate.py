# -*- coding: utf-8 -*-
"""
Regression suite for the canonical glyph.

Every check asserts a property the CDS declares normative. A failure means
either the CDS was edited without a Design Decision, or a generator drifted.

Run:  python validate.py
Exit code 0 = all pass, 1 = at least one failure.
"""

import hashlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.geometry import (load_cds, build_geometry, path_d, bez_d1, curvature,
                      coverage, centreline)

FAILURES = []
PASSES = []


def check(name, ok, detail=""):
    (PASSES if ok else FAILURES).append((name, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))


def main():
    cds = load_cds()
    g = build_geometry(cds)
    tol = cds["tolerances"]
    eps = tol["control_point_precision_du"]

    print("REGRESSION SUITE — B' COMPENSATED")
    print("=" * 68)

    # T01 — reconstruction matches the normative literals
    lit = cds["control_points"]
    worst, worst_pt = 0.0, ""
    for n in ("P0", "C1", "C2", "P3", "L1", "Q1", "Q2", "P6"):
        for i in (0, 1):
            dv = abs(lit[n][i] - g[n][i])
            if dv > worst:
                worst, worst_pt = dv, n
    check("T01 reconstruction matches CDS literals", worst <= eps,
          f"max deviation {worst:.2e} du at {worst_pt}")

    # T02 — path string is byte-identical to the CDS
    d = path_d(g)
    check("T02 generated path equals CDS path", d == cds["path"]["d"])

    # T03 — exact 180 degree rotational symmetry (DD-001)
    axis, cap = g["axis"], g["cap"]
    pairs = [("P0", "P6"), ("C1", "Q2"), ("C2", "Q1"), ("P3", "L1")]
    worst = 0.0
    for a, b in pairs:
        ra = (2*axis - g[a][0], cap - g[a][1])
        worst = max(worst, abs(ra[0]-g[b][0]), abs(ra[1]-g[b][1]))
    check("T03 rotational symmetry is exact (DD-001)",
          worst <= tol["rotational_symmetry_error_du"] + 1e-9,
          f"max error {worst:.2e} du")

    # T04 — tangent at the terminal is exactly horizontal (DD-003)
    dx, dy = bez_d1(g["P0"], g["C1"], g["C2"], g["P3"], 0.0)
    check("T04 terminal tangent is horizontal (DD-003)", abs(dy) < 1e-9,
          f"dy = {dy:.2e}")

    # T05 — tangent at the stem junction is exactly vertical: G1 (DD-005)
    dx, dy = bez_d1(g["P0"], g["C1"], g["C2"], g["P3"], 1.0)
    check("T05 G1 continuity with the stem is exact (DD-005)", abs(dx) < 1e-9,
          f"dx = {dx:.2e}")

    # T06 — monotonic transition, no inflection (DD-004)
    pts = [ (g["P0"], g["C1"], g["C2"], g["P3"]) ]
    mono = True
    prev = None
    for i in range(201):
        t = i/200.0
        dx, dy = bez_d1(*pts[0], t)
        s = (dx <= 1e-9, dy >= -1e-9)
        if prev is not None and s != prev:
            mono = False
        prev = s
    check("T06 transition is monotonic (DD-004)", mono)

    # T07 — bounding box
    bb = cds["bounding_box"]
    check("T07 bounding box matches the CDS",
          abs(g["width"] - bb["width"]) <= eps and abs(g["height"] - bb["height"]) <= eps,
          f"{g['width']:.3f} x {g['height']:.3f}")

    # T08 — the straight stem survives: the gesture never eats the letter
    straight = (g["y_bot"] - g["elev"]) - (g["y_top"] + g["elev"])
    check("T08 straight stem segment is present", straight > 0,
          f"{straight:.2f} du ({straight/g['cap']:.1%} of cap height)")

    # T09 — ink excess stays inside the DD-007 limit
    ink = 2.0 * g["over"] / g["cap"]
    check("T09 ink excess within DD-007 limit", ink <= 0.10 + 1e-9,
          f"{ink:.2%} (limit 10%)")

    # T10 — the gesture is sub-pixel at reading size (DD-007)
    a_read = g["elev"] * 16.0 / g["cap"]
    check("T10 gesture is sub-pixel at 16 px (DD-007)", a_read < 1.0,
          f"{a_read:.3f} px")

    # T11 — the gesture resolves at display size (DD-007)
    a_look = g["elev"] * 96.0 / g["cap"]
    o_look = g["over"] * 96.0 / g["cap"]
    check("T11 gesture resolves at 96 px (DD-007)",
          a_look >= 2.0 and o_look >= 2.0,
          f"elevation {a_look:.2f} px, overhang {o_look:.2f} px")

    # T12 — overhang reads as a terminal, not a hook (DD-007)
    check("T12 overhang exceeds elevation (DD-007)", g["over"] > g["elev"],
          f"{g['over']:.0f} > {g['elev']:.0f}")

    # T13 — the stroke does not pinch: measured, not assumed
    cap_px = 400
    rows, W, H = coverage(g, cap_px, ss=2)
    s = cap_px / g["cap"]
    lo = int((g["y_top"] + g["elev"] + g["w"]) * s)
    hi = int((g["y_bot"] - g["elev"] - g["w"]) * s)
    widths = []
    for y in range(max(0, lo), min(H, hi)):
        widths.append(sum(1 for v in rows[y] if v > 0.5))
    nominal = g["w"] * s
    mn = min(widths) if widths else 0
    check("T13 stroke does not pinch in the straight run",
          bool(widths) and mn >= nominal - 2.0,
          f"min {mn} px vs nominal {nominal:.1f} px")

    # T14 — declared curvature character (DD-002 / DEF-001)
    ks = [curvature(g["P0"], g["C1"], g["C2"], g["P3"], i/400.0) for i in range(401)]
    kmax_w = max(ks) * g["w"]
    check("T14 interior joint character is angular, as documented",
          kmax_w > 2.0,
          f"kmax*w = {kmax_w:.3f} (>2 means angular interior; see DEF-001)")

    # T15 — the CDS records the known defect rather than hiding it
    ids = [x["id"] for x in cds.get("known_defects", [])]
    check("T15 DEF-001 is declared in the CDS", "DEF-001" in ids)

    # T16 — DD-009 carries its non-convergence warning
    dd9 = next((x for x in cds["decisions"] if x["id"] == "DD-009"), None)
    check("T16 DD-009 declares the derivation does not converge",
          dd9 is not None and "does NOT converge" in dd9.get("note", ""))

    # T17 — provisional metrics are not silently presented as frozen
    check("T17 composition metrics are flagged PROVISIONAL",
          cds["metrics"].get("status") == "PROVISIONAL")

    # T18 — the declared digest matches the built path
    dig = hashlib.sha256(d.encode("utf-8")).hexdigest()
    check("T18 declared sha256 matches the built path",
          cds["path"]["sha256"] == dig, dig[:32] + "...")

    # ---- curves block: every declared value is verified, not asserted ----
    cv = cds["curves"]
    up = (g["P0"], g["C1"], g["C2"], g["P3"])
    lo = (g["L1"], g["Q1"], g["Q2"], g["P6"])

    def arclen(seg, n=40000):
        L, px, py = 0.0, seg[0][0], seg[0][1]
        for i in range(1, n+1):
            t = i/n
            u = 1-t
            a, b, c, dd = u*u*u, 3*u*u*t, 3*u*t*t, t*t*t
            x = a*seg[0][0]+b*seg[1][0]+c*seg[2][0]+dd*seg[3][0]
            y = a*seg[0][1]+b*seg[1][1]+c*seg[2][1]+dd*seg[3][1]
            L += math.hypot(x-px, y-py)
            px, py = x, y
        return L

    segs = {s["id"]: s for s in cv["segments"]}

    # T19 — declared segment lengths
    l1, l3 = arclen(up), arclen(lo)
    l2 = (g["y_bot"] - g["elev"]) - (g["y_top"] + g["elev"])
    ok = (abs(l1 - segs["S1"]["arc_length_du"]) < 1e-3 and
          abs(l2 - segs["S2"]["arc_length_du"]) < 1e-6 and
          abs(l3 - segs["S3"]["arc_length_du"]) < 1e-3)
    check("T19 declared segment lengths are correct", ok,
          f"S1 {l1:.4f}  S2 {l2:.4f}  S3 {l3:.4f}")

    # T20 — S1 and S3 are the same length: DD-001 holds through the arc
    check("T20 upper and lower arcs are equal in length (DD-001)",
          abs(l1 - l3) <= 1e-9, f"difference {abs(l1-l3):.2e} du")

    # T21 — declared tangents
    worst, worst_at = 0.0, ""
    for t_dec in cv["tangents"]:
        if t_dec["t"] is None:
            continue
        seg = up if t_dec["segment"] == "S1" else lo
        dx, dy = bez_d1(*seg, t_dec["t"])
        n = math.hypot(dx, dy)
        u = (dx/n, dy/n)
        e = max(abs(u[0]-t_dec["unit_vector"][0]), abs(u[1]-t_dec["unit_vector"][1]))
        if e > worst:
            worst, worst_at = e, t_dec["at"]
    check("T21 declared tangents are correct", worst < 1e-9,
          f"max error {worst:.2e} at {worst_at}")

    # T22 — declared G2 jump at the stem junction
    kj = curvature(*up, 1.0)
    dec = next(c for c in cv["continuity"] if c["junction"].startswith("P3"))
    declared = float(dec["G2"].split("to 0.")[0].split()[-1])
    check("T22 declared G2 discontinuity matches measurement",
          abs(kj - declared) < 1e-8,
          f"measured {kj:.10f}, declared {declared:.10f}")

    # T23 — terminal cut geometry
    tu = next(t for t in cv["terminals"] if t["id"] == "T-UPPER")
    x_expect = g["P0"][0]
    y0, y1 = g["P0"][1] - g["w"]/2.0, g["P0"][1] + g["w"]/2.0
    ok = (abs(tu["cut_from"][0] - x_expect) <= eps and
          abs(tu["cut_from"][1] - y0) <= eps and
          abs(tu["cut_to"][1] - y1) <= eps)
    check("T23 upper terminal cut matches the geometry", ok,
          f"x={x_expect:.3f}, y {y0:.3f}..{y1:.3f}")

    # T24 — the minimum radius is genuinely below half the stroke, as declared
    ks_all = [curvature(*up, i/2000.0) for i in range(2001)]
    rmin = 1.0/max(ks_all)
    check("T24 inner offset self-intersects, as documented",
          rmin < g["w"]/2.0,
          f"min radius {rmin:.4f} du vs half stroke {g['w']/2:.4f} du")

    print("=" * 68)
    print(f"{len(PASSES)} passed, {len(FAILURES)} failed")
    if FAILURES:
        print("\nFAILURES:")
        for n, det in FAILURES:
            print(f"  - {n} {det}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
Geometry engine for the canonical glyph B' - COMPENSATED.

Self-contained. Depends only on the Python standard library so that a
third-party engineer can run it with nothing but cds.json and this file.

The CDS is the source of truth. This module reconstructs the glyph from the
NORMATIVE LITERALS in cds.json and asserts that the reconstruction matches the
literal control points. It never invents geometry.
"""

import json
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CDS_PATH = os.path.join(ROOT, "cds.json")


# --------------------------------------------------------------------- CDS

def load_cds(path=CDS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_geometry(cds):
    """
    Reconstructs derived values and control points from the normative
    parameters using the closed-form construction algorithm in the CDS.
    """
    p = cds["parameters"]
    cap = float(p["cap_height"])
    w = float(p["stroke_width"])
    over = float(p["overhang"])
    elev = float(p["elevation"])
    h1 = float(p["handle_horizontal"])
    h2 = float(p["handle_vertical"])

    half = w / 2.0
    semi = over + half
    axis = semi
    y_top = half
    y_bot = cap - half

    def rot180(pt):
        return (2.0 * axis - pt[0], cap - pt[1])

    P0 = (axis + semi, y_top)
    C1 = (axis + semi * (1.0 - h1), y_top)
    C2 = (axis, y_top + elev * h2)
    P3 = (axis, y_top + elev)
    L1 = rot180(P3)
    Q1 = rot180(C2)
    Q2 = rot180(C1)
    P6 = rot180(P0)

    return {
        "cap": cap, "w": w, "over": over, "elev": elev, "h1": h1, "h2": h2,
        "half": half, "semi": semi, "axis": axis,
        "y_top": y_top, "y_bot": y_bot,
        "width": 2.0 * semi, "height": cap,
        "centre": (axis, cap / 2.0),
        "P0": P0, "C1": C1, "C2": C2, "P3": P3,
        "L1": L1, "Q1": Q1, "Q2": Q2, "P6": P6,
    }


def fmt(v, nd=3):
    """Trims trailing zeros so emitted paths are stable byte-for-byte."""
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def path_d(g, nd=3):
    return (
        f"M{fmt(g['P0'][0], nd)} {fmt(g['P0'][1], nd)} "
        f"C{fmt(g['C1'][0], nd)} {fmt(g['C1'][1], nd)} "
        f"{fmt(g['C2'][0], nd)} {fmt(g['C2'][1], nd)} "
        f"{fmt(g['P3'][0], nd)} {fmt(g['P3'][1], nd)} "
        f"L{fmt(g['L1'][0], nd)} {fmt(g['L1'][1], nd)} "
        f"C{fmt(g['Q1'][0], nd)} {fmt(g['Q1'][1], nd)} "
        f"{fmt(g['Q2'][0], nd)} {fmt(g['Q2'][1], nd)} "
        f"{fmt(g['P6'][0], nd)} {fmt(g['P6'][1], nd)}"
    )


# ------------------------------------------------------------------ bezier

def bez(p0, c1, c2, p3, t):
    u = 1.0 - t
    a, b, c, d = u*u*u, 3*u*u*t, 3*u*t*t, t*t*t
    return (a*p0[0] + b*c1[0] + c*c2[0] + d*p3[0],
            a*p0[1] + b*c1[1] + c*c2[1] + d*p3[1])


def bez_d1(p0, c1, c2, p3, t):
    u = 1.0 - t
    a, b, c = 3*u*u, 6*u*t, 3*t*t
    return (a*(c1[0]-p0[0]) + b*(c2[0]-c1[0]) + c*(p3[0]-c2[0]),
            a*(c1[1]-p0[1]) + b*(c2[1]-c1[1]) + c*(p3[1]-c2[1]))


def bez_d2(p0, c1, c2, p3, t):
    u = 1.0 - t
    a, b = 6*u, 6*t
    return (a*(c2[0]-2*c1[0]+p0[0]) + b*(p3[0]-2*c2[0]+c1[0]),
            a*(c2[1]-2*c1[1]+p0[1]) + b*(p3[1]-2*c2[1]+c1[1]))


def curvature(p0, c1, c2, p3, t):
    dx, dy = bez_d1(p0, c1, c2, p3, t)
    ddx, ddy = bez_d2(p0, c1, c2, p3, t)
    den = (dx*dx + dy*dy) ** 1.5
    return 0.0 if den < 1e-12 else abs(dx*ddy - dy*ddx) / den


def centreline(g, n=64):
    pts = [bez(g["P0"], g["C1"], g["C2"], g["P3"], i/n) for i in range(n+1)]
    pts.append(g["L1"])
    pts += [bez(g["L1"], g["Q1"], g["Q2"], g["P6"], i/n) for i in range(1, n+1)]
    return pts


# -------------------------------------------------------------- rasteriser

def _d2_seg(px, py, ax, ay, bx, by, ca, cb):
    vx, vy = bx-ax, by-ay
    L2 = vx*vx + vy*vy
    if L2 < 1e-12:
        return (px-ax)**2 + (py-ay)**2
    t = ((px-ax)*vx + (py-ay)*vy) / L2
    if t < 0.0:
        if not ca:
            return float("inf")          # butt cap
        t = 0.0
    elif t > 1.0:
        if not cb:
            return float("inf")
        t = 1.0
    qx, qy = ax + t*vx, ay + t*vy
    return (px-qx)**2 + (py-qy)**2


def coverage_centred(g, size_px, ss=4, pad=2):
    """
    Coverage on a canvas where the glyph is centred to sub-pixel accuracy.

    Needed for symmetry testing: on an arbitrarily framed canvas the leftover
    fraction of a pixel lands entirely on one side, so rotating the raster
    180 degrees about the pixel grid centre cannot map the glyph onto itself.
    That measures the framing, not the glyph.

    With the glyph centred, the grid centre ((W-1)/2, (H-1)/2) coincides with
    the glyph centre, and rows[y][x] <-> rows[H-1-y][W-1-x] is exact.
    """
    s = size_px / g["cap"]
    gw, gh = g["width"] * s, g["height"] * s
    W = int(math.ceil(gw)) + 2 * pad
    H = int(math.ceil(gh)) + 2 * pad
    dx = (W - gw) / 2.0
    dy = (H - gh) / 2.0

    pts = centreline(g)
    n = len(pts)
    segs = [(pts[i][0]*s + dx, pts[i][1]*s + dy,
             pts[i+1][0]*s + dx, pts[i+1][1]*s + dy,
             i != 0, i != n-2) for i in range(n-1)]
    r = (g["w"]/2.0) * s
    r2 = r*r

    NB = max(8, H)
    band = (H + 1.0)/NB
    buckets = [[] for _ in range(NB)]
    for sg in segs:
        ylo, yhi = min(sg[1], sg[3]) - r, max(sg[1], sg[3]) + r
        for b in range(max(0, int(ylo/band)), min(NB-1, int(yhi/band))+1):
            buckets[b].append(sg)

    rows = [[0.0]*W for _ in range(H)]
    step, off, inv = 1.0/ss, 1.0/(2*ss), 1.0/(ss*ss)
    for iy in range(H):
        row = rows[iy]
        for sy in range(ss):
            py = iy + sy*step + off
            cand = buckets[min(NB-1, int(py/band))]
            if not cand:
                continue
            for ix in range(W):
                acc = 0
                for sx in range(ss):
                    px = ix + sx*step + off
                    for (ax, ay, bx, by, ca, cb) in cand:
                        if px < min(ax, bx) - r or px > max(ax, bx) + r:
                            continue
                        if _d2_seg(px, py, ax, ay, bx, by, ca, cb) <= r2:
                            acc += 1
                            break
                if acc:
                    row[ix] += acc*inv
    return rows, W, H


def coverage(g, size_px, pad_frac=0.0, ss=4):
    """
    Greyscale coverage in [0,1] at the given cap height in pixels.
    Returns (rows, width, height). Used for PNG output and for validation.
    """
    s = size_px / g["cap"]
    pad = int(round(pad_frac * size_px))
    pts = centreline(g)
    n = len(pts)
    segs = [(pts[i][0]*s + pad, pts[i][1]*s + pad,
             pts[i+1][0]*s + pad, pts[i+1][1]*s + pad,
             i != 0, i != n-2) for i in range(n-1)]
    r = (g["w"]/2.0) * s
    r2 = r*r
    W = int(math.ceil(g["width"]*s)) + 2*pad
    H = int(math.ceil(g["height"]*s)) + 2*pad

    NB = max(8, H)
    band = (H + 1.0)/NB
    buckets = [[] for _ in range(NB)]
    for sg in segs:
        ylo, yhi = min(sg[1], sg[3]) - r, max(sg[1], sg[3]) + r
        for b in range(max(0, int(ylo/band)), min(NB-1, int(yhi/band))+1):
            buckets[b].append(sg)

    rows = [[0.0]*W for _ in range(H)]
    step, off, inv = 1.0/ss, 1.0/(2*ss), 1.0/(ss*ss)
    for iy in range(H):
        row = rows[iy]
        for sy in range(ss):
            py = iy + sy*step + off
            cand = buckets[min(NB-1, int(py/band))]
            if not cand:
                continue
            for ix in range(W):
                acc = 0
                for sx in range(ss):
                    px = ix + sx*step + off
                    for (ax, ay, bx, by, ca, cb) in cand:
                        if px < min(ax, bx) - r or px > max(ax, bx) + r:
                            continue
                        if _d2_seg(px, py, ax, ay, bx, by, ca, cb) <= r2:
                            acc += 1
                            break
                if acc:
                    row[ix] += acc*inv
    return rows, W, H


# --------------------------------------------------------------------- PNG

def write_png_rgba(path, rows, W, H, rgb, square=None):
    """
    Writes coverage as an RGBA PNG in the given colour on a transparent
    ground. If `square` is given, the glyph is centred inside a square canvas
    of that side in pixels.
    """
    if square:
        S = square
        ox, oy = (S - W)//2, (S - H)//2
        canvas = [[0.0]*S for _ in range(S)]
        for y in range(H):
            ty = y + oy
            if 0 <= ty < S:
                crow, srow = canvas[ty], rows[y]
                for x in range(W):
                    tx = x + ox
                    if 0 <= tx < S:
                        crow[tx] = srow[x]
        rows, W, H = canvas, S, S

    r, gg, b = rgb
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for v in row:
            a = int(round(max(0.0, min(1.0, v)) * 255))
            raw += bytes((r, gg, b, a))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# -*- coding: utf-8 -*-
"""
SVG construction kit.

Every variant is built from canonical geometry. No variant is derived from
another variant's serialised text: the dependency always points back to the
CDS. Two variants that look similar are still generated independently.
"""

import math

from .geometry import bez, fmt

XMLNS = 'xmlns="http://www.w3.org/2000/svg"'


# ------------------------------------------------------------- serialisation

def round_path(d, nd):
    """Re-emits a path string at reduced decimal precision."""
    out, num = [], ""
    for ch in d + " ":
        if ch.isdigit() or ch in ".-":
            num += ch
        else:
            if num:
                out.append(fmt(float(num), nd))
                num = ""
            if ch != " ":
                out.append(ch)
            elif out and out[-1] not in "MCLZ":
                out.append(" ")
    return "".join(out).replace("  ", " ").strip()


def path_precision_error(d_full, d_round):
    """Max coordinate deviation introduced by rounding, in design units."""
    def nums(s):
        vals, cur = [], ""
        for ch in s + " ":
            if ch.isdigit() or ch in ".-":
                cur += ch
            else:
                if cur:
                    vals.append(float(cur))
                    cur = ""
        return vals
    a, b = nums(d_full), nums(d_round)
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


# --------------------------------------------------------------- stroke path

def stroke_path(g, d, colour="currentColor", extra=""):
    return (f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{fmt(g["w"])}" stroke-linecap="butt" '
            f'stroke-linejoin="miter"{extra}/>')


# -------------------------------------------------------------- outline path

def outline_points(g, n=400):
    """
    Converts the stroked centreline into a closed filled contour by offsetting
    to both sides at half the stroke width.

    The butt caps are the straight segments joining the two sides at each end.
    Because the minimum radius of curvature is below half the stroke width, the
    inner side self-intersects; a non-zero fill rule resolves it to exactly the
    same painted region as the stroke. See CDS section 5.6.
    """
    def sample(seg):
        return [bez(*seg, i/n) for i in range(n+1)]

    up = (g["P0"], g["C1"], g["C2"], g["P3"])
    lo = (g["L1"], g["Q1"], g["Q2"], g["P6"])
    pts = sample(up) + [g["L1"]] + sample(lo)[1:]

    # de-duplicate consecutive identical points before computing normals
    clean = [pts[0]]
    for p in pts[1:]:
        if abs(p[0]-clean[-1][0]) > 1e-12 or abs(p[1]-clean[-1][1]) > 1e-12:
            clean.append(p)

    h = g["w"] / 2.0
    left, right = [], []
    m = len(clean)
    for i, p in enumerate(clean):
        if i == 0:
            dx, dy = clean[1][0]-p[0], clean[1][1]-p[1]
        elif i == m-1:
            dx, dy = p[0]-clean[-2][0], p[1]-clean[-2][1]
        else:
            dx, dy = clean[i+1][0]-clean[i-1][0], clean[i+1][1]-clean[i-1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy/L, dx/L
        left.append((p[0] + nx*h, p[1] + ny*h))
        right.append((p[0] - nx*h, p[1] - ny*h))
    return left, right


def outline_d(g, n=400, nd=2):
    left, right = outline_points(g, n)
    pts = left + right[::-1]
    parts = [f"M{fmt(pts[0][0], nd)} {fmt(pts[0][1], nd)}"]
    for x, y in pts[1:]:
        parts.append(f"L{fmt(x, nd)} {fmt(y, nd)}")
    parts.append("Z")
    return "".join(parts)


def outline_error(g, n=400):
    """
    Chord error of the flattened outline: the largest gap between the polyline
    approximation and the true offset curve. Declared, not assumed.
    """
    up = (g["P0"], g["C1"], g["C2"], g["P3"])
    worst = 0.0
    for i in range(n):
        a = bez(*up, i/n)
        b = bez(*up, (i+1)/n)
        mid_true = bez(*up, (i + 0.5)/n)
        mid_chord = ((a[0]+b[0])/2.0, (a[1]+b[1])/2.0)
        worst = max(worst, math.hypot(mid_true[0]-mid_chord[0],
                                      mid_true[1]-mid_chord[1]))
    return worst


# -------------------------------------------------------------- SVG wrappers

def svg_doc(body, w, h, *, pretty=False, width=None, height=None,
            title=None, desc=None, extra_root="", decl=False,
            profile=None, responsive=False):
    attrs = [XMLNS, f'viewBox="0 0 {fmt(w)} {fmt(h)}"']
    if not responsive and width is not None:
        attrs.append(f'width="{width}"')
    if not responsive and height is not None:
        attrs.append(f'height="{height}"')
    if responsive:
        attrs.append('preserveAspectRatio="xMidYMid meet"')
    if profile:
        attrs.append(f'version="1.2" baseProfile="{profile}"')
    if title or desc:
        attrs.append('role="img"')
        attrs.append('aria-labelledby="t' + (" d" if desc else "") + '"')
    else:
        attrs.append('aria-hidden="true"')
    if extra_root:
        attrs.append(extra_root)

    head = ""
    if decl:
        head = '<?xml version="1.0" encoding="UTF-8"?>\n'

    inner = ""
    if title:
        inner += f'<title id="t">{title}</title>'
    if desc:
        inner += f'<desc id="d">{desc}</desc>'
    inner += body

    if pretty:
        open_tag = "<svg\n  " + "\n  ".join(attrs) + ">"
        parts = inner.replace("><", ">\n<").split("\n")
        return head + open_tag + "\n  " + "\n  ".join(parts) + "\n</svg>\n"
    return head + "<svg " + " ".join(attrs) + ">" + inner + "</svg>\n"


def minify(svg_text):
    out = []
    prev_space = False
    in_tag = False
    for ch in svg_text:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        if ch in "\n\t":
            ch = " "
        if ch == " ":
            if prev_space or not in_tag:
                continue
            prev_space = True
        else:
            prev_space = False
        out.append(ch)
    return "".join(out).strip()


def validate_viewbox(svg_text, expect_w, expect_h, tol=1e-6):
    """Parses the viewBox back out of the serialised text and checks it."""
    i = svg_text.find('viewBox="')
    if i < 0:
        return False, "no viewBox attribute"
    j = svg_text.find('"', i + 9)
    parts = svg_text[i+9:j].split()
    if len(parts) != 4:
        return False, f"viewBox has {len(parts)} values, expected 4"
    x, y, w, h = (float(p) for p in parts)
    if abs(x) > tol or abs(y) > tol:
        return False, f"viewBox origin is ({x}, {y}), expected (0, 0)"
    if abs(w - expect_w) > 0.01 or abs(h - expect_h) > 0.01:
        return False, f"viewBox is {w}x{h}, expected {expect_w}x{expect_h}"
    return True, f"{w}x{h}"


def xml_wellformed(svg_text):
    """Parses with the standard library. Catches malformed output early."""
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(svg_text)
        return True, ""
    except ET.ParseError as e:
        return False, str(e)

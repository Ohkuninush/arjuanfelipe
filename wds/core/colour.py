# -*- coding: utf-8 -*-
"""
Colour engine for the Website Design System.

The brief forbids inventing colours unrelated to the canonical palette, and
also requires semantic colours (success, warning, danger, info) that the
canonical palette does not contain.

The resolution is derivation, not invention: every semantic colour is the
canonical accent rotated in hue within OKLCH - a perceptually uniform space -
holding lightness and chroma fixed. They are therefore the same colour at a
different angle, not new colours.

Every result is then checked against WCAG by calculation. Nothing is accepted
on appearance.

Standard library only.
"""

import math


# ------------------------------------------------------------ sRGB <-> OKLCH

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c*255))):02x}" for c in rgb)


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(rgb):
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_, m_, s_ = (math.copysign(abs(v) ** (1/3), v) for v in (l, m, s))
    return (0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)


def oklab_to_rgb(lab):
    L, a, b = lab
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = (v**3 for v in (l_, m_, s_))
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bb = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    return tuple(_linear_to_srgb(v) for v in (r, g, bb))


def rgb_to_oklch(rgb):
    L, a, b = rgb_to_oklab(rgb)
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360.0)


def oklch_to_rgb(lch):
    L, C, H = lch
    h = math.radians(H)
    return oklab_to_rgb((L, C * math.cos(h), C * math.sin(h)))


def in_gamut(rgb, tol=1e-4):
    return all(-tol <= c <= 1 + tol for c in rgb)


def clip_to_gamut(lch):
    """Reduces chroma until the colour fits sRGB. Hue and lightness are kept."""
    L, C, H = lch
    lo, hi = 0.0, C
    if in_gamut(oklch_to_rgb(lch)):
        return lch
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if in_gamut(oklch_to_rgb((L, mid, H))):
            lo = mid
        else:
            hi = mid
    return (L, lo, H)


# ------------------------------------------------------------------ contrast

def relative_luminance(rgb):
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    return 0.2126*r + 0.7152*g + 0.0722*b


def contrast(hex_a, hex_b):
    la = relative_luminance(hex_to_rgb(hex_a))
    lb = relative_luminance(hex_to_rgb(hex_b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def wcag_level(ratio, large=False):
    if large:
        return "AAA" if ratio >= 4.5 else ("AA" if ratio >= 3.0 else "fail")
    return "AAA" if ratio >= 7.0 else ("AA" if ratio >= 4.5 else "fail")


# ------------------------------------------------------------- derivation

def rotate_hue(base_hex, degrees):
    """The canonical accent at a different angle. Lightness and chroma held."""
    L, C, H = rgb_to_oklch(hex_to_rgb(base_hex))
    return rgb_to_hex(oklch_to_rgb(clip_to_gamut((L, C, (H + degrees) % 360))))


def adjust_for_contrast(hex_colour, ground_hex, target=4.5, max_steps=200):
    """
    Raises or lowers OKLCH lightness until the colour meets a contrast target
    against the given ground. Hue is never altered: the colour keeps its
    identity, only its lightness moves.

    Returns (hex, ratio, steps, reached).
    """
    L, C, H = rgb_to_oklch(hex_to_rgb(hex_colour))
    ground_lum = relative_luminance(hex_to_rgb(ground_hex))
    lighten = ground_lum < 0.5           # dark ground -> go lighter

    step = 0.002 if lighten else -0.002
    cur = hex_colour
    for i in range(max_steps):
        ratio = contrast(cur, ground_hex)
        if ratio >= target:
            return cur, ratio, i, True
        L += step
        if not (0.0 <= L <= 1.0):
            break
        cur = rgb_to_hex(oklch_to_rgb(clip_to_gamut((L, C, H))))
    return cur, contrast(cur, ground_hex), max_steps, False


def scale(base_hex, ground_hex, stops):
    """
    A lightness ramp from one hue. `stops` is a list of OKLCH L values.
    Returns a list of (name-suffix, hex, contrast-vs-ground).
    """
    _, C, H = rgb_to_oklch(hex_to_rgb(base_hex))
    out = []
    for name, L in stops:
        hx = rgb_to_hex(oklch_to_rgb(clip_to_gamut((L, C, H))))
        out.append((name, hx, contrast(hx, ground_hex)))
    return out

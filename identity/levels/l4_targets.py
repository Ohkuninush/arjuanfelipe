# -*- coding: utf-8 -*-
"""
LEVEL 4 - TARGETS

Generates every platform deliverable. Each target is produced directly from
canonical geometry; no target is ever derived from another target.

Depends on: Levels 1, 2 and 3.
"""

import json

from core.geometry import fmt, coverage
from core import svgkit as K
from core import formats as F

INK = (231, 235, 238)          # #e7ebee
INK_DARK = (16, 20, 26)        # #10141a
GROUND = (16, 20, 26)
ACCENT = (234, 106, 30)        # #ea6a1e

FAVICON_SIZES = [16, 24, 32, 48, 64, 96, 128, 180, 192, 256, 384, 512]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]

# Platform canvases. Sources are each platform's published image guidance;
# where a platform accepts a range, the most widely quoted value is used.
SOCIAL = {
    "open-graph":    (1200, 630),
    "twitter-x":     (1200, 628),
    "linkedin":      (1200, 627),
    "github":        (1280, 640),
    "mastodon":      (1200, 630),
    "bluesky":       (1200, 630),
    "discord":       (1200, 630),
    "slack":         (1200, 630),
    "whatsapp":      (400, 400),
    "telegram":      (1200, 630),
    "facebook":      (1200, 630),
    "instagram":     (1080, 1080),
    "threads":       (1080, 1080),
    "pinterest":     (1000, 1500),
    "reddit":        (1200, 630),
    "medium":        (1500, 750),
    "youtube":       (800, 800),
    "product-hunt":  (240, 240),
    "hacker-news":   (32, 32),
}

# Search engines: each of these consumes the favicon set rather than a bespoke
# asset. Sizes below are the ones each crawler is documented to prefer.
SEARCH = {
    "google":      48,     # multiples of 48 required
    "google-discover": 512,
    "bing":        32,
    "duckduckgo":  32,
    "brave":       32,
    "yahoo":       32,
    "yandex":      120,
}

# PNG rasterisation is expensive in pure Python, so large canvases are emitted
# as vector only unless the platform genuinely refuses SVG.
RASTER_SOCIAL = {"open-graph", "twitter-x", "github", "whatsapp",
                 "product-hunt", "hacker-news"}


def _square_svg(ctx, side, scale, ground, ink, rounded=0):
    g = ctx["g"]
    rx = f'rx="{rounded}" ' if rounded else ""
    bg = (f'<rect width="{side}" height="{side}" '
          f'{rx}fill="{ground}"/>')
    h = side * scale
    k = h / g["height"]
    w = g["width"] * k
    body = (f'{bg}<g transform="translate({fmt((side-w)/2)} {fmt((side-h)/2)}) '
            f'scale({fmt(k, 6)})"><path d="{ctx["outline_d"]}" '
            f'fill="{ink}"/></g>')
    return K.svg_doc(body, side, side, width=side, height=side)


def _canvas_svg(ctx, w, h, scale_of_h, ground, ink):
    g = ctx["g"]
    gh = h * scale_of_h
    k = gh / g["height"]
    gw = g["width"] * k
    body = (f'<rect width="{w}" height="{h}" fill="{ground}"/>'
            f'<g transform="translate({fmt((w-gw)/2)} {fmt((h-gh)/2)}) '
            f'scale({fmt(k, 6)})"><path d="{ctx["outline_d"]}" '
            f'fill="{ink}"/></g>')
    return K.svg_doc(body, w, h, width=w, height=h)


def _compose_png(ctx, canvas_w, canvas_h, cap_px, ink, ground):
    """Rasterises the glyph once and composites it centred on a flat ground."""
    g = ctx["g"]
    rows, gw, gh = coverage(g, cap_px, ss=4 if cap_px <= 128 else 2)
    ox, oy = (canvas_w - gw) // 2, (canvas_h - gh) // 2
    canvas = [[0.0] * canvas_w for _ in range(canvas_h)]
    for y in range(gh):
        ty = y + oy
        if 0 <= ty < canvas_h:
            crow, srow = canvas[ty], rows[y]
            for x in range(gw):
                tx = x + ox
                if 0 <= tx < canvas_w:
                    crow[tx] = srow[x]
    return F.png_rgb(canvas, canvas_w, canvas_h, ink, ground)


def _icon_png(ctx, side, scale=0.58, transparent=False):
    g = ctx["g"]
    cap = max(1, int(round(side * scale)))
    rows, gw, gh = coverage(g, cap, ss=6 if side <= 48 else 4)
    ox, oy = (side - gw) // 2, (side - gh) // 2
    canvas = [[0.0] * side for _ in range(side)]
    for y in range(gh):
        ty = y + oy
        if 0 <= ty < side:
            crow, srow = canvas[ty], rows[y]
            for x in range(gw):
                tx = x + ox
                if 0 <= tx < side:
                    crow[tx] = srow[x]
    if transparent:
        return F.png_rgba(canvas, side, side, INK)
    return F.png_rgb(canvas, side, side, INK, GROUND)


def run(ctx, assets):
    g, W, H = ctx["g"], ctx["W"], ctx["H"]
    text_out, bin_out = {}, {}

    # ================================================= FAVICON SYSTEM ======
    for s in FAVICON_SIZES:
        bin_out[f"favicon/favicon-{s}.png"] = _icon_png(ctx, s)
    text_out["favicon/favicon.svg"] = _square_svg(
        ctx, 32, 0.58, "#10141a", "#e7ebee", rounded=4)

    ico_members = [(s, _icon_png(ctx, s, transparent=True)) for s in ICO_SIZES]
    bin_out["favicon/favicon.ico"] = F.ico(ico_members)

    # ================================================= APPLE ==============
    text_out["apple/apple-touch-icon.svg"] = _square_svg(
        ctx, 180, 0.56, "#10141a", "#e7ebee")
    bin_out["apple/apple-touch-icon.png"] = _icon_png(ctx, 180, 0.56)
    bin_out["apple/apple-touch-icon-152.png"] = _icon_png(ctx, 152, 0.56)
    bin_out["apple/apple-touch-icon-167.png"] = _icon_png(ctx, 167, 0.56)
    text_out["apple/mask-icon.svg"] = assets["mask-icon.svg"]
    # Startup images: one per common logical viewport, at 2x and 3x.
    startup = [(320, 568, 2), (375, 667, 2), (390, 844, 3),
               (414, 896, 2), (428, 926, 3), (768, 1024, 2), (1024, 1366, 2)]
    for lw, lh, ratio in startup:
        w, h = lw * ratio, lh * ratio
        text_out[f"apple/startup-{w}x{h}.svg"] = _canvas_svg(
            ctx, w, h, 0.16, "#10141a", "#e7ebee")

    # ================================================= ANDROID ============
    for s in (192, 512):
        text_out[f"android/pwa-{s}.svg"] = _square_svg(
            ctx, s, 0.56, "#10141a", "#e7ebee")
        # Maskable: the safe zone is the central 80%, so the glyph shrinks to
        # 40% of the canvas rather than 56%.
        text_out[f"android/pwa-{s}-maskable.svg"] = _square_svg(
            ctx, s, 0.40, "#10141a", "#e7ebee")
        bin_out[f"android/pwa-{s}.png"] = _icon_png(ctx, s, 0.56)
        bin_out[f"android/pwa-{s}-maskable.png"] = _icon_png(ctx, s, 0.40)
    # Monochrome: Android tints this itself, so it must be a flat silhouette.
    text_out["android/monochrome-512.svg"] = K.svg_doc(
        f'<rect width="512" height="512" fill="none"/>'
        + _mono_group(ctx, 512, 0.40), 512, 512, width=512, height=512)
    text_out["android/round-512.svg"] = _square_svg(
        ctx, 512, 0.50, "#10141a", "#e7ebee", rounded=256)
    text_out["android/legacy-192.svg"] = _square_svg(
        ctx, 192, 0.56, "#10141a", "#e7ebee", rounded=24)
    text_out["android/play-store-512.svg"] = _square_svg(
        ctx, 512, 0.52, "#10141a", "#e7ebee")
    bin_out["android/play-store-512.png"] = _icon_png(ctx, 512, 0.52)
    text_out["android/adaptive-foreground-432.svg"] = K.svg_doc(
        _mono_group(ctx, 432, 0.37, "#e7ebee"), 432, 432, width=432, height=432)
    text_out["android/adaptive-background-432.svg"] = K.svg_doc(
        '<rect width="432" height="432" fill="#10141a"/>', 432, 432,
        width=432, height=432)

    # ================================================= WINDOWS ============
    for s, name in ((70, "small"), (150, "medium"), (310, "wide"), (310, "large")):
        if name == "wide":
            text_out["windows/mstile-310x150.svg"] = _canvas_svg(
                ctx, 310, 150, 0.56, "#10141a", "#e7ebee")
        else:
            text_out[f"windows/mstile-{s}.svg"] = _square_svg(
                ctx, s, 0.50, "#10141a", "#e7ebee")
    bin_out["windows/mstile-150.png"] = _icon_png(ctx, 150, 0.50)
    text_out["windows/store-icon-300.svg"] = _square_svg(
        ctx, 300, 0.50, "#10141a", "#e7ebee")
    bin_out["windows/explorer.ico"] = F.ico(
        [(s, _icon_png(ctx, s, transparent=True)) for s in (16, 32, 48, 256)])
    text_out["windows/browserconfig.xml"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<browserconfig><msapplication><tile>\n'
        '  <square70x70logo src="/windows/mstile-70.png"/>\n'
        '  <square150x150logo src="/windows/mstile-150.png"/>\n'
        '  <wide310x150logo src="/windows/mstile-310x150.png"/>\n'
        '  <square310x310logo src="/windows/mstile-310.png"/>\n'
        '  <TileColor>#10141a</TileColor>\n'
        '</tile></msapplication></browserconfig>\n')

    # ================================================= SOCIAL =============
    for name, (w, h) in sorted(SOCIAL.items()):
        scale = 0.34 if w != h else 0.46
        text_out[f"social/{name}-{w}x{h}.svg"] = _canvas_svg(
            ctx, w, h, scale, "#10141a", "#e7ebee")
        if name in RASTER_SOCIAL:
            cap = max(1, int(round(h * scale)))
            bin_out[f"social/{name}-{w}x{h}.png"] = _compose_png(
                ctx, w, h, cap, INK, GROUND)

    # ================================================= SEARCH =============
    for name, s in sorted(SEARCH.items()):
        bin_out[f"search/{name}-{s}.png"] = _icon_png(ctx, s)

    # ================================================= PRINT ==============
    pdf_ops, eps_ops = _vector_ops(ctx)
    bin_out["print/glyph.pdf"] = F.pdf_vector(
        pdf_ops, W, H, g["w"], (0, 0, 0), "B-PRIME-COMPENSATED")
    bin_out["print/glyph.eps"] = F.eps_vector(
        eps_ops, W, H, g["w"], (0, 0, 0), "B-PRIME-COMPENSATED")
    rows, rw, rh = coverage(g, 600, ss=2)
    bin_out["print/glyph-600.tiff"] = F.tiff_rgb(
        rows, rw, rh, (0, 0, 0), (255, 255, 255), dpi=300)
    text_out["print/glyph-40mm.svg"] = assets["glyph.print.svg"]

    # ================================================= MANIFESTS ==========
    text_out["site.webmanifest"] = json.dumps({
        "name": "arjuanfelipe",
        "short_name": "arjuanfelipe",
        "id": "/",
        "start_url": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": "#10141a",
        "theme_color": "#10141a",
        "icons": [
            {"src": "/android/pwa-192.png", "sizes": "192x192",
             "type": "image/png"},
            {"src": "/android/pwa-512.png", "sizes": "512x512",
             "type": "image/png"},
            {"src": "/android/pwa-512-maskable.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
            {"src": "/android/monochrome-512.svg", "sizes": "any",
             "type": "image/svg+xml", "purpose": "monochrome"},
            {"src": "/favicon/favicon.svg", "sizes": "any",
             "type": "image/svg+xml"},
        ],
    }, indent=2, sort_keys=True) + "\n"

    text_out["head-snippet.html"] = _head_snippet()

    ctx["target_counts"] = {
        "favicon": sum(1 for k in list(text_out) + list(bin_out)
                       if k.startswith("favicon/")),
        "apple": sum(1 for k in list(text_out) + list(bin_out)
                     if k.startswith("apple/")),
        "android": sum(1 for k in list(text_out) + list(bin_out)
                       if k.startswith("android/")),
        "windows": sum(1 for k in list(text_out) + list(bin_out)
                       if k.startswith("windows/")),
        "social": sum(1 for k in list(text_out) + list(bin_out)
                      if k.startswith("social/")),
        "search": sum(1 for k in list(text_out) + list(bin_out)
                      if k.startswith("search/")),
        "print": sum(1 for k in list(text_out) + list(bin_out)
                     if k.startswith("print/")),
    }
    return text_out, bin_out


def _mono_group(ctx, side, scale, colour="#000000"):
    g = ctx["g"]
    h = side * scale
    k = h / g["height"]
    w = g["width"] * k
    return (f'<g transform="translate({fmt((side-w)/2)} {fmt((side-h)/2)}) '
            f'scale({fmt(k, 6)})"><path d="{ctx["outline_d"]}" '
            f'fill="{colour}"/></g>')


def _vector_ops(ctx):
    """
    Emits the canonical path for PDF and PostScript. Both use a Y-up user
    space, so every y becomes (H - y). The curve is emitted as real cubics,
    not flattened: these are vector formats and deserve vector data.
    """
    g = ctx["g"]
    H = g["height"]

    def p(pt):
        return f"{pt[0]:.4f} {H - pt[1]:.4f}"

    pdf = (f"{p(g['P0'])} m\n"
           f"{p(g['C1'])} {p(g['C2'])} {p(g['P3'])} c\n"
           f"{p(g['L1'])} l\n"
           f"{p(g['Q1'])} {p(g['Q2'])} {p(g['P6'])} c")
    eps = (f"{p(g['P0'])} moveto\n"
           f"{p(g['C1'])} {p(g['C2'])} {p(g['P3'])} curveto\n"
           f"{p(g['L1'])} lineto\n"
           f"{p(g['Q1'])} {p(g['Q2'])} {p(g['P6'])} curveto")
    return pdf, eps


def _head_snippet():
    return """<!-- Generated by the IPS from CDS 1.0.0. Do not hand-edit. -->
<link rel="icon" href="/favicon/favicon.ico" sizes="any">
<link rel="icon" href="/favicon/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/favicon/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="/apple/apple-touch-icon.png" sizes="180x180">
<link rel="mask-icon" href="/apple/mask-icon.svg" color="#10141a">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#10141a">
<meta name="msapplication-config" content="/windows/browserconfig.xml">
<meta name="msapplication-TileColor" content="#10141a">
<meta property="og:image" content="/social/open-graph-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="/social/twitter-x-1200x628.png">
"""

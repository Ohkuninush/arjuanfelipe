# -*- coding: utf-8 -*-
"""
Binary format encoders. Standard library only.

Every encoder is deterministic: no timestamps, no creation dates, no random
identifiers, no dictionary iteration order dependence. The same input always
produces the same bytes. This is a hard requirement of the IPS, not a
nicety - byte-identical rebuilds are what make hash verification meaningful.

Formats implemented here: PNG, ICO, PDF (vector), EPS (vector), TIFF.

NOT implemented, and deliberately so:
  WebP  - requires a VP8L encoder
  AVIF  - requires an AV1 intra encoder
  JPEG  - requires a DCT encoder, and is the wrong format for a hard-edged
          two-tone mark in any case
See docs/COVERAGE.md.
"""

import struct
import zlib


# ---------------------------------------------------------------------- PNG

def png_rgba(rows, width, height, rgb):
    """Coverage rows in [0,1] -> RGBA PNG bytes, colour on transparency."""
    r, g, b = rgb
    raw = bytearray()
    for row in rows:
        raw.append(0)                      # filter type 0 (None)
        for v in row:
            a = int(round(max(0.0, min(1.0, v)) * 255))
            raw += bytes((r, g, b, a))
    return _png_wrap(bytes(raw), width, height, colour_type=6)


def png_rgb(rows, width, height, ink, ground):
    """Coverage composited over an opaque ground -> RGB PNG bytes."""
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for v in row:
            t = max(0.0, min(1.0, v))
            raw += bytes(int(round(ground[i] + (ink[i] - ground[i]) * t))
                         for i in range(3))
    return _png_wrap(bytes(raw), width, height, colour_type=2)


def _png_wrap(raw, width, height, colour_type):
    def chunk(tag, data):
        c = tag + data
        return (struct.pack(">I", len(data)) + c
                + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF))

    # zlib level 9 with a fixed strategy: deterministic across runs
    comp = zlib.compressobj(9, zlib.DEFLATED, 15, 9, zlib.Z_DEFAULT_STRATEGY)
    data = comp.compress(raw) + comp.flush()
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8,
                                         colour_type, 0, 0, 0))
            + chunk(b"IDAT", data)
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------------- ICO

def ico(entries):
    """
    entries: list of (side_px, png_bytes). Emits a multi-resolution .ico with
    PNG-compressed members, which every Windows version since Vista reads.
    A side of 256 is encoded as 0 per the ICO specification.
    """
    entries = sorted(entries, key=lambda e: e[0])
    n = len(entries)
    header = struct.pack("<HHH", 0, 1, n)
    dir_size = 16 * n
    offset = len(header) + dir_size
    directory = b""
    for side, data in entries:
        dim = 0 if side >= 256 else side
        directory += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32,
                                 len(data), offset)
        offset += len(data)
    return header + directory + b"".join(d for _, d in entries)


# ---------------------------------------------------------------------- PDF

def pdf_vector(path_ops, width, height, stroke_width, rgb, title):
    """
    Single-page vector PDF. The glyph is emitted as a real stroked path, not
    a raster. PDF user space has Y increasing upward, so the caller supplies
    ops already flipped.
    """
    r, g, b = (c / 255.0 for c in rgb)
    content = (f"{r:.4f} {g:.4f} {b:.4f} RG\n"
               f"{stroke_width:.4f} w\n"
               f"0 J\n"                     # butt caps
               f"0 j\n"                     # miter joins
               f"{path_ops}\nS\n").encode("ascii")

    objs = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objs.append((f"<< /Type /Page /Parent 2 0 R /MediaBox "
                 f"[0 0 {width:.4f} {height:.4f}] /Contents 4 0 R "
                 f"/Resources << >> >>").encode("ascii"))
    objs.append(b"<< /Length " + str(len(content)).encode("ascii")
                + b" >>\nstream\n" + content + b"endstream")
    # No /CreationDate, no /ID: those would break determinism.
    objs.append(("<< /Title (" + title + ") /Producer (arjuanfelipe IPS) >>")
                .encode("ascii"))

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += str(i).encode("ascii") + b" 0 obj\n" + body + b"\nendobj\n"

    xref_at = len(out)
    out += b"xref\n0 " + str(len(objs) + 1).encode("ascii") + b"\n"
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (b"trailer\n<< /Size " + str(len(objs) + 1).encode("ascii")
            + b" /Root 1 0 R /Info 5 0 R >>\nstartxref\n"
            + str(xref_at).encode("ascii") + b"\n%%EOF\n")
    return bytes(out)


# ---------------------------------------------------------------------- EPS

def eps_vector(ps_ops, width, height, stroke_width, rgb, title):
    """Encapsulated PostScript. Y increases upward, as in PDF."""
    r, g, b = (c / 255.0 for c in rgb)
    head = (f"%!PS-Adobe-3.0 EPSF-3.0\n"
            f"%%Title: {title}\n"
            f"%%Creator: arjuanfelipe IPS\n"
            f"%%BoundingBox: 0 0 {int(width + 0.999)} {int(height + 0.999)}\n"
            f"%%HiResBoundingBox: 0 0 {width:.4f} {height:.4f}\n"
            f"%%LanguageLevel: 2\n"
            f"%%Pages: 1\n"
            f"%%EndComments\n"
            f"%%Page: 1 1\n"
            f"gsave\n"
            f"{r:.4f} {g:.4f} {b:.4f} setrgbcolor\n"
            f"{stroke_width:.4f} setlinewidth\n"
            f"0 setlinecap\n"
            f"0 setlinejoin\n"
            f"newpath\n")
    tail = "stroke\ngrestore\nshowpage\n%%EOF\n"
    return (head + ps_ops + "\n" + tail).encode("ascii")


# --------------------------------------------------------------------- TIFF

def tiff_rgb(rows, width, height, ink, ground, dpi=300):
    """Uncompressed RGB TIFF for archival. Little-endian, single strip."""
    pixels = bytearray()
    for row in rows:
        for v in row:
            t = max(0.0, min(1.0, v))
            pixels += bytes(int(round(ground[i] + (ink[i] - ground[i]) * t))
                            for i in range(3))

    # tag, type, count, value-or-offset          types: 3=SHORT 4=LONG 5=RATIONAL
    header = b"II" + struct.pack("<HI", 42, 8)
    n_tags = 12
    ifd_size = 2 + n_tags * 12 + 4
    extra_at = 8 + ifd_size                     # BitsPerSample + two RATIONALs
    extra = struct.pack("<HHH", 8, 8, 8)        # 6 bytes
    extra += struct.pack("<II", dpi, 1)         # XResolution
    extra += struct.pack("<II", dpi, 1)         # YResolution
    data_at = extra_at + len(extra)

    def tag(t, typ, count, val):
        return struct.pack("<HHI", t, typ, count) + struct.pack("<I", val)

    ifd = struct.pack("<H", n_tags)
    ifd += tag(256, 4, 1, width)                        # ImageWidth
    ifd += tag(257, 4, 1, height)                       # ImageLength
    ifd += tag(258, 3, 3, extra_at)                     # BitsPerSample
    ifd += tag(259, 3, 1, 1)                            # Compression = none
    ifd += tag(262, 3, 1, 2)                            # Photometric = RGB
    ifd += tag(273, 4, 1, data_at)                      # StripOffsets
    ifd += tag(277, 3, 1, 3)                            # SamplesPerPixel
    ifd += tag(278, 4, 1, height)                       # RowsPerStrip
    ifd += tag(279, 4, 1, len(pixels))                  # StripByteCounts
    ifd += tag(282, 5, 1, extra_at + 6)                 # XResolution
    ifd += tag(283, 5, 1, extra_at + 14)                # YResolution
    ifd += tag(296, 3, 1, 2)                            # ResolutionUnit = inch
    ifd += struct.pack("<I", 0)                         # no next IFD

    return header + ifd + extra + bytes(pixels)

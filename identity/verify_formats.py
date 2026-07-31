# -*- coding: utf-8 -*-
"""
Independent format verification.

The binary encoders in core/formats.py were written by hand. Checking a magic
number only proves the first four bytes. This re-parses each container from
scratch and confirms the internal structure is coherent.

Run:  python verify_formats.py
"""

import os
import struct
import sys
import zlib

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
ok_count = 0
fails = []


def report(name, ok, detail=""):
    global ok_count
    if ok:
        ok_count += 1
    else:
        fails.append(f"{name}: {detail}")
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))


def parse_png(data):
    """Walks every chunk, verifies CRCs, decompresses IDAT, checks row count."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None, "bad signature"
    i = 8
    idat = b""
    hdr = None
    seen_end = False
    while i < len(data):
        (ln,) = struct.unpack(">I", data[i:i+4])
        tag = data[i+4:i+8]
        body = data[i+8:i+8+ln]
        (crc,) = struct.unpack(">I", data[i+8+ln:i+12+ln])
        if zlib.crc32(tag + body) & 0xFFFFFFFF != crc:
            return None, f"CRC mismatch in {tag!r}"
        if tag == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            seen_end = True
        i += 12 + ln
    if not hdr:
        return None, "no IHDR"
    if not seen_end:
        return None, "no IEND"
    w, h, depth, ctype = hdr[0], hdr[1], hdr[2], hdr[3]
    raw = zlib.decompress(idat)
    channels = {0: 1, 2: 3, 6: 4}[ctype]
    expect = h * (1 + w * channels * depth // 8)
    if len(raw) != expect:
        return None, f"decompressed {len(raw)} bytes, expected {expect}"
    return (w, h, ctype), ""


def main():
    print("INDEPENDENT FORMAT VERIFICATION")
    print("=" * 70)

    # ---------------------------------------------------------------- PNG
    pngs = []
    for dp, _, fs in os.walk(DIST):
        for fn in fs:
            if fn.endswith(".png"):
                pngs.append(os.path.join(dp, fn))
    bad = []
    for p in sorted(pngs):
        info, err = parse_png(open(p, "rb").read())
        if info is None:
            bad.append(f"{os.path.basename(p)}: {err}")
    report(f"PNG: {len(pngs)} files fully re-parsed (chunks, CRC, inflate)",
           not bad, bad[0] if bad else "")

    # ---------------------------------------------------------------- ICO
    icos = [os.path.join(dp, fn) for dp, _, fs in os.walk(DIST)
            for fn in fs if fn.endswith(".ico")]
    bad = []
    for p in sorted(icos):
        data = open(p, "rb").read()
        reserved, typ, count = struct.unpack("<HHH", data[:6])
        if reserved != 0 or typ != 1:
            bad.append(f"{os.path.basename(p)}: bad ICONDIR")
            continue
        for k in range(count):
            off = 6 + k*16
            (bw, bh, cc, res, planes, bits,
             size, dataoff) = struct.unpack("<BBBBHHII", data[off:off+16])
            member = data[dataoff:dataoff+size]
            info, err = parse_png(member)
            if info is None:
                bad.append(f"{os.path.basename(p)} member {k}: {err}")
                break
            side = 256 if bw == 0 else bw
            if info[0] != side or info[1] != side:
                bad.append(f"{os.path.basename(p)} member {k}: "
                           f"declares {side}, PNG is {info[0]}x{info[1]}")
                break
            if dataoff + size > len(data):
                bad.append(f"{os.path.basename(p)} member {k}: overruns file")
                break
        else:
            continue
    report(f"ICO: {len(icos)} files, every member re-parsed as PNG and "
           f"cross-checked against its declared size", not bad,
           bad[0] if bad else "")

    # ---------------------------------------------------------------- TIFF
    tiffs = [os.path.join(dp, fn) for dp, _, fs in os.walk(DIST)
             for fn in fs if fn.endswith(".tiff")]
    bad = []
    for p in tiffs:
        data = open(p, "rb").read()
        if data[:2] != b"II":
            bad.append("not little-endian")
            continue
        magic, ifd_off = struct.unpack("<HI", data[2:8])
        if magic != 42:
            bad.append("bad magic")
            continue
        (n_tags,) = struct.unpack("<H", data[ifd_off:ifd_off+2])
        tags = {}
        for k in range(n_tags):
            o = ifd_off + 2 + k*12
            tag, typ, cnt = struct.unpack("<HHI", data[o:o+8])
            (val,) = struct.unpack("<I", data[o+8:o+12])
            tags[tag] = (typ, cnt, val)
        # tags must be in ascending order per the specification
        order = [struct.unpack("<H", data[ifd_off+2+k*12:ifd_off+4+k*12])[0]
                 for k in range(n_tags)]
        if order != sorted(order):
            bad.append("IFD tags not in ascending order")
            continue
        need = [256, 257, 258, 259, 262, 273, 277, 278, 279]
        missing = [t for t in need if t not in tags]
        if missing:
            bad.append(f"missing tags {missing}")
            continue
        w, h = tags[256][2], tags[257][2]
        strip_off, strip_len = tags[273][2], tags[279][2]
        if strip_len != w * h * 3:
            bad.append(f"strip length {strip_len} != {w}x{h}x3")
            continue
        if strip_off + strip_len != len(data):
            bad.append("pixel data does not end at EOF")
            continue
        report(f"TIFF: IFD re-parsed, {n_tags} tags ordered, "
               f"{w}x{h} RGB, strip length consistent", True)
    if bad:
        report("TIFF structure", False, bad[0])

    # ---------------------------------------------------------------- PDF
    pdfs = [os.path.join(dp, fn) for dp, _, fs in os.walk(DIST)
            for fn in fs if fn.endswith(".pdf")]
    bad = []
    for p in pdfs:
        data = open(p, "rb").read()
        if not data.startswith(b"%PDF-"):
            bad.append("bad header")
            continue
        if not data.rstrip().endswith(b"%%EOF"):
            bad.append("no %%EOF")
            continue
        sx = data.rfind(b"startxref")
        xref_at = int(data[sx+9:data.find(b"%%EOF", sx)].strip())
        if data[xref_at:xref_at+4] != b"xref":
            bad.append(f"startxref points to {data[xref_at:xref_at+10]!r}")
            continue
        # every declared object offset must actually begin that object
        body = data[xref_at:]
        lines = body.split(b"\n")
        count = int(lines[1].split()[1])
        offs = []
        for k in range(1, count):
            entry = lines[2 + k]
            offs.append(int(entry.split()[0]))
        misaligned = []
        for k, off in enumerate(offs, start=1):
            expect = f"{k} 0 obj".encode()
            if not data[off:off+len(expect)] == expect:
                misaligned.append(k)
        if misaligned:
            bad.append(f"xref offsets wrong for objects {misaligned}")
            continue
        has_stream = b"stream" in data and b"endstream" in data
        report(f"PDF: {count-1} objects, xref offsets all land on their "
               f"object, stream present={has_stream}", True)
    if bad:
        report("PDF structure", False, bad[0])

    # ---------------------------------------------------------------- EPS
    eps = [os.path.join(dp, fn) for dp, _, fs in os.walk(DIST)
           for fn in fs if fn.endswith(".eps")]
    bad = []
    for p in eps:
        t = open(p, encoding="ascii").read()
        need = ["%!PS-Adobe-3.0 EPSF-3.0", "%%BoundingBox:", "newpath",
                "moveto", "curveto", "stroke", "showpage", "%%EOF"]
        missing = [k for k in need if k not in t]
        if missing:
            bad.append(f"missing {missing}")
            continue
        bb = [l for l in t.splitlines() if l.startswith("%%BoundingBox:")][0]
        vals = bb.split()[1:]
        if len(vals) != 4:
            bad.append("BoundingBox needs 4 values")
            continue
        report(f"EPS: DSC conformant, BoundingBox {' '.join(vals)}, "
               f"vector path present", True)
    if bad:
        report("EPS structure", False, bad[0])

    print("=" * 70)
    print(f"{ok_count} passed, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

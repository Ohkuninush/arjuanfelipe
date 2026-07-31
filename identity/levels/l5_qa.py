# -*- coding: utf-8 -*-
"""
LEVEL 5 - QA & RELEASE

Final verification before anything may be called production-ready.
Hash manifest, format sanity, determinism support, release packaging.

Depends on: Level 4.
"""

import hashlib
import json
import xml.etree.ElementTree as ET


def _sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def run(ctx, text_assets, bin_assets):
    checks, failures = [], []

    def ck(name, ok, detail=""):
        checks.append((name, ok, detail))
        if not ok:
            failures.append(f"{name} {detail}")

    # ---- every SVG parses -------------------------------------------------
    bad = []
    for name, text in text_assets.items():
        if not name.endswith(".svg"):
            continue
        try:
            ET.fromstring(text)
        except ET.ParseError as e:
            bad.append(f"{name}: {e}")
    ck("Q1 every SVG is well-formed XML", not bad,
       f"{len(text_assets)} text assets" if not bad else bad[0])

    # ---- every XML manifest parses ---------------------------------------
    bad = []
    for name, text in text_assets.items():
        if name.endswith(".xml"):
            try:
                ET.fromstring(text)
            except ET.ParseError as e:
                bad.append(f"{name}: {e}")
    ck("Q2 every XML manifest parses", not bad)

    # ---- every JSON manifest parses --------------------------------------
    bad = []
    for name, text in text_assets.items():
        if name.endswith((".json", ".webmanifest")):
            try:
                json.loads(text)
            except Exception as e:
                bad.append(f"{name}: {e}")
    ck("Q3 every JSON manifest parses", not bad)

    # ---- binary magic numbers --------------------------------------------
    bad = []
    for name, data in bin_assets.items():
        if name.endswith(".png") and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            bad.append(f"{name}: bad PNG signature")
        if name.endswith(".ico") and data[:4] != b"\x00\x00\x01\x00":
            bad.append(f"{name}: bad ICO header")
        if name.endswith(".pdf") and not data.startswith(b"%PDF-"):
            bad.append(f"{name}: bad PDF header")
        if name.endswith(".eps") and not data.startswith(b"%!PS-Adobe"):
            bad.append(f"{name}: bad EPS header")
        if name.endswith(".tiff") and data[:4] not in (b"II*\x00", b"MM\x00*"):
            bad.append(f"{name}: bad TIFF header")
    ck("Q4 every binary carries a valid signature", not bad,
       f"{len(bin_assets)} binary assets" if not bad else bad[0])

    # ---- PNG dimensions match the filename where it states one -----------
    bad = []
    import struct
    for name, data in bin_assets.items():
        if not name.endswith(".png"):
            continue
        w, h = struct.unpack(">II", data[16:24])
        tail = name.rsplit("-", 1)[-1].replace(".png", "")
        if tail.isdigit() and (w != int(tail) or h != int(tail)):
            bad.append(f"{name}: is {w}x{h}")
        if "x" in tail:
            try:
                ew, eh = (int(v) for v in tail.split("x"))
                if (w, h) != (ew, eh):
                    bad.append(f"{name}: is {w}x{h}, expected {ew}x{eh}")
            except ValueError:
                pass
    ck("Q5 PNG dimensions match their declared size", not bad,
       bad[0] if bad else "")

    # ---- ICO member count -------------------------------------------------
    ico_ok = True
    for name, data in bin_assets.items():
        if name.endswith(".ico"):
            count = struct.unpack("<H", data[4:6])[0]
            if count < 1:
                ico_ok = False
    ck("Q6 ICO files declare at least one member", ico_ok)

    # ---- no asset is empty ------------------------------------------------
    empty = [n for n, t in text_assets.items() if not t.strip()]
    empty += [n for n, b in bin_assets.items() if len(b) < 32]
    ck("Q7 no asset is empty or truncated", not empty, str(empty[:3]))

    # ---- geometry traceability: the canonical path digest is unchanged ----
    ck("Q8 canonical path digest unchanged",
       _sha(ctx["d"]) == ctx["cds"]["path"]["sha256"])

    # ---- hash manifest ----------------------------------------------------
    manifest = {}
    for n, t in sorted(text_assets.items()):
        manifest[n] = {"bytes": len(t.encode("utf-8")), "sha256": _sha(t)}
    for n, b in sorted(bin_assets.items()):
        manifest[n] = {"bytes": len(b), "sha256": _sha(b)}

    release = {
        "cds_version": ctx["cds"]["cds_version"],
        "glyph": ctx["cds"]["identity"]["canonical_glyph"],
        "canonical_path_sha256": ctx["cds"]["path"]["sha256"],
        "asset_count": len(manifest),
        "assets": manifest,
    }
    # A single digest over the whole release: one number to compare builds.
    release["release_digest"] = _sha(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")))

    ctx["release"] = release
    return checks, failures, release

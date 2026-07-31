# -*- coding: utf-8 -*-
"""
IDENTITY PRODUCTION SYSTEM - build orchestrator

    CDS -> Generator -> Validators -> Optimizers -> Targets -> QA & Release

Execution order is immutable. Dependencies flow downward only. No stage may
bypass, replace or invalidate an earlier one.

Run:  python build.py
Exit: 0 on a clean release, 1 if any level reports a failure.
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from levels import l1_generate, l2_validate, l3_optimize, l4_targets, l5_qa

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")

SIZE_LADDER = [16, 20, 24, 28, 32, 40, 48, 56, 64, 72, 96, 128,
               180, 192, 256, 384, 512]


def banner(n, title):
    print()
    print("=" * 74)
    print(f"LEVEL {n} — {title}")
    print("=" * 74)


def main():
    ctx = {"outline_samples": 400, "size_ladder": SIZE_LADDER}

    # ------------------------------------------------------- LEVEL 0 ------
    banner(0, "CANONICAL DESIGN SPECIFICATION")
    with open(os.path.join(HERE, "cds.json"), encoding="utf-8") as f:
        raw = json.load(f)
    print(f"  cds_version      : {raw['cds_version']}")
    print(f"  canonical glyph  : {raw['identity']['canonical_glyph']}")
    print(f"  status           : {raw['identity']['status']}")
    print(f"  frozen decisions : {len(raw['decisions'])}")
    print(f"  path sha256      : {raw['path']['sha256'][:32]}...")

    # ------------------------------------------------------- LEVEL 1 ------
    banner(1, "GENERATOR")
    masters = l1_generate.run(ctx)
    print(f"  gate             : geometry matches the frozen literals")
    print(f"  master assets    : {len(masters)}")
    print(f"  outline samples  : {ctx['outline_samples']}")
    print(f"  outline chord err: {ctx['outline_chord_error_du']:.3e} du")

    # ------------------------------------------------------- LEVEL 2 ------
    banner(2, "VALIDATORS")
    results, failures = l2_validate.run(ctx, masters)
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f"  {detail}" if detail else ""))
    if failures:
        print("\n  PIPELINE HALTED at level 2.")
        for f_ in failures:
            print(f"    - {f_}")
        return 1

    # ------------------------------------------------------- LEVEL 3 ------
    banner(3, "OPTIMIZERS")
    optimized = l3_optimize.run(ctx, masters)
    for name, err, ok in ctx["optimize_report"]:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<16} "
              f"max deviation {err:.4f} du (budget "
              f"{l3_optimize.PRECISION_BUDGET_DU} du)")
    if any(not ok for _, _, ok in ctx["optimize_report"]):
        print("\n  PIPELINE HALTED at level 3: precision budget exceeded.")
        return 1
    print(f"  production variants: {len(optimized)}")
    print("\n  compression")
    for c in ctx["compression"]:
        print(f"    {c['asset']:<24} {c['raw']:>6} B -> gzip {c['gzip']:>5} B"
              f"  ({c['ratio']:.2%})")

    # ------------------------------------------------------- LEVEL 4 ------
    banner(4, "TARGETS")
    tgt_text, tgt_bin = l4_targets.run(ctx, {**masters, **optimized})
    for k, v in sorted(ctx["target_counts"].items()):
        print(f"  {k:<10} {v:>4} assets")
    print(f"  {'manifests':<10} {2:>4} assets")

    # ------------------------------------------------------- LEVEL 5 ------
    banner(5, "QA & RELEASE")
    all_text = {**masters, **optimized, **tgt_text}
    all_bin = dict(tgt_bin)
    checks, qa_failures, release = l5_qa.run(ctx, all_text, all_bin)
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f"  {detail}" if detail else ""))
    if qa_failures:
        print("\n  RELEASE BLOCKED.")
        for f_ in qa_failures:
            print(f"    - {f_}")
        return 1

    # ------------------------------------------------------- WRITE --------
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    for name, text in all_text.items():
        p = os.path.join(DIST, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    for name, data in all_bin.items():
        p = os.path.join(DIST, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    with open(os.path.join(DIST, "RELEASE.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(release, f, indent=2, sort_keys=True)
        f.write("\n")

    print()
    print("=" * 74)
    print(f"  RELEASE OK — {release['asset_count']} assets")
    print(f"  release digest : {release['release_digest']}")
    print(f"  written to     : dist/")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())

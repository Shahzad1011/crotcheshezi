"""Render + verify the star hanging ornament.

Run:  .venv/Scripts/python.exe star_demo.py
"""

from __future__ import annotations

import glob
import os

from croctech.engine import audit, audit_blocks, validate
from croctech.pipeline import render_pattern
from croctech.star import build_star_pattern


def main() -> None:
    pattern = build_star_pattern()
    errors = validate(pattern)
    audits = audit(pattern)
    parts = [c for c in pattern.components if c.role == "part"]
    ops = [c for c in pattern.components if c.role == "operation"]
    print(f"=== {pattern.name} ===")
    print(f"{len(parts)} part(s) + {len(ops)} finishing operation(s) | "
          f"{len(audits)} audited rows | errors: {len(errors)}")
    print(f"\n{'Component':<10}{'Row':>4}{'Inst':>5}{'Base sts':>10}{'Start':>7}{'Worked':>8}"
          f"{'Made':>6}{'Claimed':>9}  Status")
    for a in audits:
        rng = f"{a.base_range[0]}-{a.base_range[1]}" if a.base_range else "-"
        print(f"{a.component:<10}{a.index:>4}{(a.instance or '-')!s:>5}{rng:>10}"
              f"{a.start_count:>7}{a.consumed:>8}{a.produced:>6}"
              f"{a.declared_total:>9}  {'OK' if a.ok else 'ERROR'}")
    for b in audit_blocks(pattern):
        per = b.base_consumed // max(b.instances, 1)
        print(f"\n{b.label}: {b.instances} x {per} = {b.base_consumed} base sts, "
              f"foundation made {b.base_available}  ->  {'OK' if b.ok else 'ERROR'}")
    for e in errors:
        print("  ERROR:", e)

    stars = glob.glob(os.path.join("vibe_images", "*star*.png"))
    res = render_pattern(pattern, outdir="out/star", cover_image_path=stars[0] if stars else None)
    print("\n=== Artefacts ===")
    for label, path in [("text", res.text_path), ("chart", res.chart_path),
                        ("profile", res.profile_path), ("html", res.html_path),
                        ("pdf", res.pdf_path)]:
        if not path:
            print(f"{label:<8}: omitted (no gauge supplied -- see the note in pattern.md)")
            continue
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"{label:<8}: {path} ({size} bytes)")
    if res.dims is None:
        print("\nDimensions: not claimed. No stitch gauge was given for this yarn/hook, and a "
              "fabricated gauge would fabricate the size too.")
    cov = res.cov
    print(f"Coverage: {cov.checked_stitches} stitches counted in {', '.join(cov.checked_parts)}")
    if cov.unmodelled_parts:
        print(f"  Not stitch-modelled ({cov.pct_of_parts:.0f}% of parts): "
              f"{', '.join(cov.unmodelled_parts)}")
    if pattern.unassigned_hooks:
        print(f"  Unassigned hooks: {pattern.unassigned_hooks}")


if __name__ == "__main__":
    main()

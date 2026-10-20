"""Runnable demo: verify the user's pattern, prove the repair loop, render all
artefacts (text, chart, profile, HTML dossier, PDF).

Run:  .venv/Scripts/python.exe demo.py
"""

from __future__ import annotations

import glob
import os

from croctech.ai import ExampleProvider, RepairDemoProvider
from croctech.engine import audit, validate
from croctech.example import build_pattern
from croctech.pipeline import generate


def main() -> None:
    print("=== Croctech accuracy core ===\n")

    # 1) Independent re-verification of the user's pattern.
    pattern = build_pattern()
    print(f"Validation errors: {len(validate(pattern))}")
    print(f"{'Row':>4} {'Start':>6} {'Worked':>7} {'Made':>5} {'Claimed':>8}  Status")
    for a in audit(pattern):
        print(f"{a.index:>4} {a.start_count:>6} {a.consumed:>7} {a.produced:>5} "
              f"{a.declared_total:>8}  {'OK' if a.ok else 'ERROR'}")

    # 2) Gate: a tampered total is refused, not rendered.
    tampered = build_pattern()
    tampered.components[0].rounds[9].declared_total = 42
    assert validate(tampered), "gate broken"
    print("\nGate check: tampered Row 10 refused before rendering (verified).")

    covers = glob.glob(os.path.join("vibe_images", "*.png"))
    cover = covers[0] if covers else None

    # 3) Clean pipeline -> all artefacts.
    result = generate(
        "a 5-ply cotton/acrylic Santa-hat keychain in red and white, 2.5 mm hook",
        ExampleProvider(), outdir="out", cover_image_path=cover,
    )
    print("\n=== Rendered artefacts ===")
    print(f"Text pattern : {result.text_path}")
    print(f"Count chart  : {result.chart_path}")
    print(f"Profile chart: {result.profile_path}")
    print(f"HTML dossier : {result.html_path}  ({os.path.getsize(result.html_path)} bytes)")
    print(f"PDF design   : {result.pdf_path}  ({os.path.getsize(result.pdf_path)} bytes)")
    print(f"Dimensions   : ~{result.dims.widest_diameter_cm:.2f} cm wide (widest round's "
          f"circumference), ~{result.dims.height_cm:.2f} cm worked height "
          f"(+/-{result.dims.tolerance_pct:.0f}%, {result.pattern.gauge.note.split('.')[0]})")
    print(f"Yarn usage   : {result.yarn.total_stitches} sc, ~{result.yarn.total_meters:.2f} m"
          + (f", ~{result.yarn.total_grams:.2f} g" if result.yarn.total_grams else ""))
    for c, cu in result.yarn.by_colour.items():
        print(f"    - {c}: {cu.stitches} sc, ~{cu.meters:.2f} m"
              + (f", ~{cu.grams:.2f} g" if cu.grams is not None else ""))

    # 4) Repair loop (offline, no API key): a flawed AI draft gets fixed before render.
    repaired = generate("repair-demo", RepairDemoProvider(), outdir="out/_repair")
    print("\n=== AI draft + repair loop ===")
    print(f"Draft needed {repaired.attempts} repair iteration(s); final errors: "
          f"{len(validate(repaired.pattern))}; rendered: {repaired.pdf_path}")


if __name__ == "__main__":
    main()

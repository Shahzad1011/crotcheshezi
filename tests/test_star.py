"""The star ornament exercises what the keychain can't: repeated blocks, part
quantities, flat turning rows worked off an edge, `sk` decreases, double
crochet, and every gap the source leaves (no gauge, no hook for one tool, an
undefined puff stitch).
"""

from __future__ import annotations

import os

from croctech.chart import render_flat
from croctech.engine import audit, coverage, validate
from croctech.gauge import compute_dimensions, compute_yarn_usage
from croctech.render_text import render_text
from croctech.schema import Gauge, StitchOp
from croctech.star import build_star_pattern as build_pattern


def _star(p):
    return next(c for c in p.components if c.name == "Star")


def _rendered(p=None):
    p = p or build_pattern()
    audits = audit(p)
    return render_text(p, audits, compute_dimensions(p, [a.produced for a in audits]),
                       cov=coverage(p, audits)), audits


# ---------------------------------------------------------------- the pattern

def test_star_pattern_is_clean():
    errors = validate(build_pattern())
    assert errors == [], f"expected 0 errors, got: {errors}"


def test_star_base_and_point_reconcile():
    audits = [a for a in audit(build_pattern()) if a.component == "Star"]
    base = [a.produced for a in audits if a.instance is None]
    assert base == [6, 12, 18, 24, 30]
    for k in range(1, 6):
        rows = [a.produced for a in audits if a.instance == k]
        assert rows == [6, 5, 4, 3, 2], f"point {k}"
    assert all(a.ok for a in audits)


def test_quantities_are_preserved():
    comps = {c.name: c for c in build_pattern().components}
    assert comps["Star"].quantity == 2
    assert comps["Blush"].quantity == 2
    assert comps["Flower"].kind == "manual"


# ------------------------------------------- multiplicity is arithmetic, not prose

def test_point_instances_must_exactly_exhaust_the_base():
    """Six points would need 36 base stitches that do not exist. A per-row audit
    cannot see this; the block audit can."""
    p = build_pattern()
    _star(p).blocks[0].instances = 6
    errors = validate(p)
    assert any("6 instances x 6 base sts = 36" in e and "made 30" in e for e in errors), errors


def test_too_few_instances_is_also_an_error():
    p = build_pattern()
    _star(p).blocks[0].instances = 4
    assert any("4 instances x 6 base sts = 24" in e for e in validate(p))


def test_undeclared_base_allocation_is_refused():
    """Without consumes_base_stitches the engine cannot prove the points fit, so
    it must say so rather than silently pass."""
    p = build_pattern()
    _star(p).blocks[0].consumes_base_stitches = None
    assert any("cannot check" in e for e in validate(p))


def test_each_point_must_work_its_whole_allocation():
    """A point that works 5 of its 6 base stitches leaves a hole in the rim; the
    row is audited against its allocation, not exempted as a fresh start."""
    p = build_pattern()
    row1 = _star(p).blocks[0].rows[0]
    row1.cycle = [StitchOp(kind="sc", count=5)]
    row1.declared_total = 5
    errors = validate(p)
    assert any("Star R1.1" in e and "consume 5 sts" in e and "started with 6" in e
               for e in errors), errors


# ------------------------------------------------------- honest unknowns, no gaps

def test_no_gauge_means_no_invented_dimensions():
    """The spec gave no stitch gauge, so nothing may claim a finished size."""
    p = build_pattern()
    assert p.gauge is None
    assert compute_dimensions(p, [6, 12, 18, 24, 30]) is None
    assert compute_yarn_usage(p, audit(p)) is None
    text, _ = _rendered(p)
    assert "no finished size is claimed" in text
    assert "cm [" not in text


def test_yarn_usage_covers_every_piece_you_make():
    """A two-star ornament quoted for one star is how a maker runs out of yarn."""
    p = build_pattern()
    p.gauge = Gauge(stitches_per_10cm=22, rows_per_10cm=26)
    y = compute_yarn_usage(p, audit(p))
    assert y.total_stitches == 390  # 2 stars x 190 + 2 blush x 5
    assert round(sum(c.meters for c in y.by_colour.values()), 2) == y.total_meters


def test_no_invented_notions():
    m = build_pattern().material
    assert "safety eyes" not in [n.lower() for n in m.notions]
    assert set(m.notions) == {"scissors", "glue", "yarn needle", "fiber filling"}


def test_abbreviations_match_the_spec():
    abbr = build_pattern().abbreviations
    assert abbr == {
        "MR": "Magic ring", "sl knot": "Slip knot", "sc": "Single crochet",
        "inc": "Increase", "sk": "Skip", "ch": "Chain", "sl st": "Slip stitch",
        "dc": "Double crochet",
    }


def test_every_listed_hook_is_assigned():
    p = build_pattern()
    assert p.unassigned_hooks == []
    assert {c.name: c.hook for c in p.components if c.hook} == {
        "Star": 3.5, "Flower": 1.0, "Cherry": 1.0, "Blush": 1.0}


def test_source_gaps_are_surfaced_not_answered():
    p = build_pattern()
    assert p.provenance.startswith("Transcribed by hand")
    assert any("puffy stitch" in t for t in p.undefined_terms)
    text, _ = _rendered(p)
    assert "Open questions" in text and "puffy stitch" in text
    assert "Sewing" in text


# -------------------------------------------------------------------- sewing

def test_sewing_is_a_workable_seam_not_a_summary():
    sewing = next(c for c in build_pattern().components if c.name == "Sewing")
    joined = " ".join(sewing.steps).lower()
    assert "glue" not in joined, "a sewing step may not reach for glue"
    assert "no glue" in " ".join(sewing.notes).lower()
    for needed in ("yarn needle", "70 cm", "wrong sides", "invisible slip-stitch",
                   "30 seam stitches", "4 cm", "fiber filling", "tail"):
        assert needed in joined, f"sewing step missing: {needed}"
    assert len(sewing.steps) >= 8


# ---------------------------------------------------------------- rendering

def test_verbatim_stitch_wording_survives_to_the_output():
    """The author's own row text must be the printed instruction, not our shorthand."""
    text, _ = _rendered()
    assert "Repeat (2 sc, 1 inc) 6 times (24 sc)." in text
    assert "Sk the first stitch and make 5 sc, ch 1, turn your work." in text
    assert "engine check:" in text


def test_edge_rows_are_not_rendered_as_magic_rings():
    """Row 1 of a point is worked along the base, so the engine check must not
    tell the maker to start a ring."""
    text, _ = _rendered()
    points = text[text.index("Point 1"):text.index("Point 2")]
    assert "Join yarn and work 6 sc along the base edge." in points
    assert "Magic ring" not in points


def test_no_join_is_invented_where_the_source_worked_continuous():
    text, _ = _rendered()
    star_section = text[text.index("### Star"):text.index("### Blush")]
    assert "sl st to join" not in star_section


def test_multiplicity_is_printed_with_base_ranges():
    text, _ = _rendered()
    assert "Point 1 -- base sts 1-6" in text
    assert "Point 5 -- base sts 25-30" in text
    assert "Point 2 -- base sts 7-12  (join the yarn to these stitches)" in text


def test_verdict_separates_arithmetic_from_coverage():
    """A green 'PASS' over a quarter of the object is the failure this guards."""
    text, audits = _rendered()
    cov = coverage(build_pattern(), audits)
    assert "Arithmetic: 0 stitch-math error(s)" in text
    assert "Coverage:" in text and "Not stitch-modelled" in text
    assert {"Star x2", "Blush x2"} == set(cov.checked_parts)
    # sewing, assembly and hanging are things you do, not pieces -- they must not
    # sit in the same denominator as parts and make the coverage figure meaningless
    assert {"Flower x2 (described, no counts)", "Cherry x3 (described, no counts)"} == \
        set(cov.unmodelled_parts)
    assert set(cov.operations) == {"Sewing", "Assembly", "Hanging"}
    assert cov.pct_of_parts == 50.0
    # 2 stars x (90 base + 5 points x 20) + 2 blush x 5
    assert cov.checked_stitches == 2 * (90 + 100) + 10
    assert not cov.complete


def test_fastened_off_row_does_not_tell_the_maker_to_turn():
    text, _ = _rendered()
    tip = text.split("Point 1")[1].split("Point 2")[0]
    assert "ch 1, fasten off." in tip
    assert tip.count("ch 1, turn.") == 4, "four turning rows, then the yarn is cut"


def test_flat_silhouette_is_used_for_flat_components(tmp_path):
    p = build_pattern()
    star = _star(p)
    assert any(r.flat for r in star.blocks[0].rows)
    audits = [a for a in audit(p) if a.component == "Star"]
    # the renderer needs a gauge to draw in cm; supply one explicitly
    gauge = Gauge(stitches_per_10cm=22, rows_per_10cm=26)
    out = str(tmp_path / "profile.png")
    assert render_flat(star.rounds, audits, gauge, "Star", out) == out
    assert os.path.getsize(out) > 0

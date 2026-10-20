"""Regression tests for the adversarial probes run against the shipped code.

Each test is one attack from the audit addendum: what used to pass, render, and
print a green headline must now be refused -- by the schema where the claim is
illegal at all, by the engine where the claim is a shape error, and by the
renderer where the claim is only an unreadable one.
"""

from __future__ import annotations

import pytest

from croctech.ai import _draft_to_pattern
from croctech.engine import audit, coverage, validate
from croctech.gauge import compute_dimensions
from croctech.render_html import render_html
from croctech.render_text import render_text
from croctech.schema import Component, Gauge, Material, Pattern, RoundSpec, Step, StitchOp


def _mat() -> Material:
    return Material(yarn="acrylic", hook_mm=3.5, colors=["red"])


def _draft(gauge=None):
    return _draft_to_pattern({
        "name": "Probe", "item_type": "toy", "description": "probe",
        "material": {"yarn": "acrylic", "hook_mm": 3.5, "colors": ["red"]},
        "gauge": gauge or {},
        "rounds": [{"index": 1, "repeat": "6x"}, {"index": 2, "repeat": "50x"}],
    })


# ------------------------------------------------------------------- T1 teleport

def test_a_draft_cannot_teleport_by_declaring_a_new_foundation():
    """`foundation: true` used to be the drafter's word, and a 6 -> 50 jump validated
    clean. A fresh start is now granted by position, not claimed by a flag."""
    with pytest.raises(ValueError, match="fresh start"):
        Component(name="Body", rounds=[
            RoundSpec(index=1, starts_from="magic_ring", cycle=[StitchOp(kind="sc", count=6)],
                      declared_total=6),
            RoundSpec(index=2, starts_from="magic_ring",
                      cycle=[StitchOp(kind="sc", count=50)], declared_total=50)])


def test_a_fresh_start_after_a_fasten_off_is_still_legal():
    c = Component(name="Body", rounds=[
        RoundSpec(index=1, starts_from="magic_ring", flat=True, fasten_off=True,
                  cycle=[StitchOp(kind="sc", count=6)], declared_total=6),
        RoundSpec(index=2, starts_from="edge", cycle=[StitchOp(kind="sc", count=4)],
                  declared_total=4)])
    assert {r.index for r in c.rounds if id(r) in c.fresh_starts} == {1, 2}


def test_the_draft_path_grants_a_fresh_start_only_to_row_1():
    p = _draft()
    assert p.components[0].rounds[0].claims_fresh_start
    assert not p.components[0].rounds[1].claims_fresh_start


def test_round_2_must_work_into_round_1s_stitches():
    """With no escape hatch left, the engine sees the abandoned stitches itself."""
    p = Pattern(name="Probe", item_type="toy", material=_mat(), rounds=[
        RoundSpec(index=1, starts_from="magic_ring", cycle=[StitchOp(kind="sc", count=6)],
                  declared_total=6),
        RoundSpec(index=2, cycle=[StitchOp(kind="sc", count=50)], declared_total=50)])
    errors = validate(p)
    assert any("Nothing exists there to work into" in e for e in errors), errors
    assert any("consume 50 sts but you started with 6" in e for e in errors), errors


# ------------------------------------------------------------------ T2 ruffling

def test_a_round_that_doubles_the_stitch_count_is_a_shape_error():
    """Honest threading, no arithmetic lie: 18 -> 36 in one row is a ruffle, and the
    IR now carries enough geometry to say so."""
    def ops(n):
        return [StitchOp(kind="sc", count=n)]

    rounds = [
        RoundSpec(index=1, starts_from="magic_ring", cycle=ops(6), declared_total=6),
        RoundSpec(index=2, cycle=[StitchOp(kind="inc", count=6)], declared_total=12),
        RoundSpec(index=3, cycle=[StitchOp(kind="sc", count=1),
                                  StitchOp(kind="inc", count=1)], repeats=6,
                  declared_total=18),
        RoundSpec(index=4, cycle=ops(18), declared_total=18),
    ]
    p = Pattern(name="Probe", item_type="toy", material=_mat(), rounds=list(rounds))
    assert validate(p) == []
    p.components[0].rounds.append(
        RoundSpec(index=5, cycle=[StitchOp(kind="inc", count=18)], declared_total=36))
    errors = validate(p)
    assert any("ruffles" in e for e in errors), errors


# ------------------------------------------------------- T3 duplicate round index

def test_duplicate_round_index_is_refused_at_the_schema():
    """Two rows both indexed 2 used to make author_totals hand one row the other's
    total, then blame the author for the mismatch."""
    with pytest.raises(ValueError, match="duplicate"):
        Component(name="Body", rounds=[
            RoundSpec(index=1, starts_from="magic_ring",
                      cycle=[StitchOp(kind="sc", count=6)], declared_total=6),
            RoundSpec(index=2, cycle=[StitchOp(kind="sc", count=9)], declared_total=9),
            RoundSpec(index=2, cycle=[StitchOp(kind="sc", count=10)], declared_total=10)])


def test_author_totals_are_keyed_by_position_not_index():
    p = Pattern(name="Probe", item_type="toy", material=_mat(), rounds=[
        RoundSpec(index=1, starts_from="magic_ring",
                  cycle=[StitchOp(kind="inc", count=6)], declared_total=0)])
    from croctech.engine import author_totals

    author_totals(p)
    assert p.components[0].rounds[0].declared_total == 12


# ------------------------------------------------------------ T4 fake measured gauge

def test_a_model_supplied_calibrated_flag_is_ignored():
    g = Gauge(stitches_per_10cm=22, rows_per_10cm=28, calibrated=True)  # extra field
    assert g.attested_by is None and g.calibrated is False


def test_an_ai_gauge_never_prints_measured_from_your_swatch():
    p = _draft({"stitches_per_10cm": 22, "rows_per_10cm": 28,
                "calibrated": True, "attested_by": "the model"})
    assert p.gauge is not None and p.gauge.attested_by is None
    audits = audit(p)
    text = render_text(p, audits, compute_dimensions(p, [a.produced for a in audits]))
    assert "measured from your swatch" not in text
    assert "NOT MEASURED" in text


def test_attestation_is_the_only_route_to_a_measured_claim():
    p = _draft()
    p.gauge = Gauge(stitches_per_10cm=22, rows_per_10cm=28,
                    attested_by="Shahzad, 10x10 cm swatch on 3.5 mm")
    audits = audit(p)
    text = render_text(p, audits, compute_dimensions(p, [a.produced for a in audits]))
    assert "measured from your swatch, attested by Shahzad" in text


# ------------------------------------------------------------------------ T5 joins

def test_no_join_is_invented_for_a_draft():
    """The draft format has no join field, so nothing may print 'sl st to join'."""
    p = _draft()
    audits = audit(p)
    text = render_text(p, audits, compute_dimensions(p, [a.produced for a in audits]))
    assert "sl st to join" not in text
    assert "Magic ring, 50 sc" not in text


# --------------------------------------------------------------------- T6 badge scope

def test_a_clean_audit_of_a_small_part_of_the_object_is_not_headlined_as_verified(tmp_path):
    p = Pattern(
        name="Probe", item_type="toy", material=_mat(),
        components=[
            Component(name="Body", rounds=[
                RoundSpec(index=1, starts_from="magic_ring",
                          cycle=[StitchOp(kind="sc", count=6)], declared_total=6)]),
            Component(name="Head", kind="manual", steps=[Step("Make a head.")]),
            Component(name="Legs", kind="manual", steps=[Step("Make two legs.")]),
        ])
    assert validate(p) == []
    audits = audit(p)
    cov = coverage(p, audits)
    assert cov.pct_of_parts == pytest.approx(100 / 3)
    html = render_html(p, audits, compute_dimensions(p, [a.produced for a in audits]),
                       cov=cov, out_path=str(tmp_path / "dossier.html"))
    with open(html, encoding="utf-8") as f:
        doc = f.read()
    assert "PASS - 0 stitch-math errors" in doc
    assert "33% of parts stitch-modelled" in doc
    assert "class=\"warn\"" in doc


# ------------------------------------------------------ P0-6: no invented tool default

def test_a_draft_without_a_hook_invents_no_hook():
    """`hook_mm` used to default to 2.5, so every drafted pattern shipped with a
    tool the designer never named -- and a false open question about it."""
    p = _draft_to_pattern({
        "name": "Probe", "item_type": "toy",
        "material": {"yarn": "acrylic"},
        "rounds": [{"index": 1, "repeat": "6x"}]})
    assert p.material.hook_mm is None
    assert p.listed_hooks == []
    text = render_text(p, audit(p), None)
    assert "not stated in the source" in text
    assert "no part says where to use it" not in text

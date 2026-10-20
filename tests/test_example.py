"""Golden tests: the user's pattern must validate clean, and the engine must
catch a tampered stitch total (proof it really checks, not rubber-stamps).
"""

from __future__ import annotations

from croctech.engine import audit, validate
from croctech.example import build_pattern
from croctech.gauge import compute_yarn_usage
from croctech.schema import parse_repeat


def test_keychain_example_is_clean():
    errors = validate(build_pattern())
    assert errors == [], f"expected 0 errors, got: {errors}"


def test_every_round_reconciles():
    audits = audit(build_pattern())
    assert all(a.ok for a in audits)
    # the round-by-round stitch counts from the user's written pattern
    got = [a.produced for a in audits]
    assert got == [6, 9, 12, 15, 18, 18, 18, 18, 18, 20, 20, 20, 20, 20, 20]


def test_engine_catches_wrong_total():
    p = build_pattern()
    p.rounds[4].declared_total = 99  # tamper: claim 99 instead of the real 18
    errors = validate(p)
    assert any("Keychain R5" in e for e in errors), errors


def test_engine_catches_unworkable_round():
    p = build_pattern()
    # increase the cycle so it consumes more stitches than the round started with
    p.rounds[5].cycle = parse_repeat("sc, inc")
    p.rounds[5].repeats = 20
    errors = validate(p)
    assert any("consume" in e for e in errors), errors


def test_parse_repeat():
    ops = parse_repeat("2x, v")
    assert [o.kind for o in ops] == ["sc", "inc"]
    assert ops[0].count == 2


def test_yarn_usage_totals():
    p = build_pattern()
    audits = audit(p)
    y = compute_yarn_usage(p, audits)
    assert y.total_stitches == 252
    red = next(c for name, c in y.by_colour.items() if name == "red")
    white = next(c for name, c in y.by_colour.items() if "white" in name.lower())
    assert red.stitches == 132
    assert white.stitches == 120
    assert y.total_grams is not None and y.total_meters > 0
    # the printed breakdown must add up to the printed total, to the centimetre
    assert round(red.meters + white.meters, 2) == y.total_meters
    assert round(red.grams + white.grams, 2) == y.total_grams


def test_repair_loop_fixes_flawed_draft():
    from croctech.ai import RepairDemoProvider
    from croctech.pipeline import generate

    res = generate("repair", RepairDemoProvider(), outdir="out/_repair")
    assert res.attempts >= 1, "expected the flawed draft to require a repair"
    assert validate(res.pattern) == []
    assert res.audits[4].ok  # the previously over-worked Round 5 is now clean

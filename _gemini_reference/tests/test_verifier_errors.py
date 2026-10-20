"""
Unit Tests for Compiler Diagnostics and Error Detection.
Ensures CrocTech strictly flags invalid patterns, stitch underflow, and count hallucinations.
"""

import pytest
from croctech.verifier.engine import PatternVerifier
from croctech.verifier.diagnostics import DiagnosticCode
from croctech.core.models import PatternDef, RoundDef, StitchCommand
from croctech.core.types import StitchType, WorkingMode


def test_catch_base_consumption_underflow():
    """Test when Round 2 consumes 10 stitches, but Round 1 only had 6."""
    verifier = PatternVerifier()

    r1 = RoundDef(
        round_number=1,
        raw_text="6 sc in MR",
        calculated_stitch_count=6,
        stated_stitch_count=6,
        commands=[StitchCommand(stitch_type=StitchType.SC, count=6)]
    )
    # Round 2 tries to consume 10 stitches (5 increases)
    r2 = RoundDef(
        round_number=2,
        raw_text="inc in each st",
        stitches_consumed=10, # Mismatch with 6!
        calculated_stitch_count=20,
        stated_stitch_count=20,
        commands=[StitchCommand(stitch_type=StitchType.INC, count=1, repeat_times=10)]
    )

    pattern = PatternDef(
        title="Invalid Pattern",
        rounds=[r1, r2]
    )

    report = verifier.verify(pattern)
    assert report.is_valid is False
    assert report.error_count > 0
    codes = [d.code for d in report.diagnostics]
    assert DiagnosticCode.ERR_BASE_CONSUMPTION_MISMATCH in codes


def test_catch_stated_count_hallucination():
    """Test when an LLM claims [12] stitches, but the math only produces 9."""
    verifier = PatternVerifier()

    r1 = RoundDef(
        round_number=1,
        raw_text="6 sc in MR",
        calculated_stitch_count=6,
        stated_stitch_count=6,
        commands=[StitchCommand(stitch_type=StitchType.SC, count=6)]
    )
    r2 = RoundDef(
        round_number=2,
        raw_text="(sc, inc) * 3",
        stitches_consumed=6,
        calculated_stitch_count=9,
        stated_stitch_count=12, # Hallucinated [12] instead of [9]!
        commands=[
            StitchCommand(stitch_type=StitchType.SC, count=1, repeat_times=3),
            StitchCommand(stitch_type=StitchType.INC, count=1, repeat_times=3)
        ]
    )

    pattern = PatternDef(
        title="Hallucinated Pattern",
        rounds=[r1, r2]
    )

    report = verifier.verify(pattern)
    assert report.is_valid is False
    assert any(d.code == DiagnosticCode.ERR_STITCH_COUNT_MISMATCH for d in report.diagnostics)


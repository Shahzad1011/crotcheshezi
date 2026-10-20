"""
Unit Test: Verification of User's Santa Hat Keychain Pattern.
Validates that CrocTech achieves 100% mathematical accuracy and 0 errors on the user's prompt.
"""

import pytest
from croctech.ai.pipeline import PatternSynthesisPipeline
from examples.santa_hat_keychain import SANTA_HAT_RAW_TEXT


def test_user_santa_hat_pattern_verification():
    """Verify user's exact pattern from prompt."""
    pipeline = PatternSynthesisPipeline()
    pattern, report, fixes = pipeline.process_pattern_text(SANTA_HAT_RAW_TEXT, title="Santa Hat Keychain")

    # Invariants
    assert report.is_valid is True, f"Verification failed with errors: {report.diagnostics}"
    assert report.error_count == 0
    assert len(pattern.rounds) == 15

    # Check row-by-row stitch counts
    expected_counts = [6, 9, 12, 15, 18, 18, 18, 18, 18, 20, 20, 20, 20, 20, 20]
    actual_counts = [r.calculated_stitch_count for r in pattern.rounds]
    assert actual_counts == expected_counts, f"Stitch count mismatch! Got {actual_counts}"

    # Total stitches
    total_stitches = sum(expected_counts)
    assert report.dimensions.total_stitches == total_stitches
    assert total_stitches == 252

    # Dimensions
    dim = report.dimensions
    assert 45.0 <= dim.finished_height_mm <= 60.0
    assert 22.0 <= dim.max_diameter_mm <= 30.0
    assert dim.has_folded_brim is True
    assert dim.folded_rows_count == 3
    assert dim.pompom_height_mm == 15.0

    # Yarn usage
    assert "Red" in report.yarn_usage
    assert any("White" in c or "Silver" in c for c in report.yarn_usage)
    assert report.yarn_usage["Red"].meters_required > 1.0


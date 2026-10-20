"""The three output formats must say the same thing, and none of them may print
a number the engine did not compute or a shape the pattern cannot produce.
"""

from __future__ import annotations

import os

from croctech.ai import _draft_to_pattern
from croctech.chart import row_bands
from croctech.pipeline import render_pattern
from croctech.star import build_star_pattern

_DRAFT = {
    "name": "Test disc",
    "item_type": "coaster",
    "material": {"yarn": "cotton", "hook_mm": 3.0},
    "rounds": [{"index": 1, "foundation": True, "repeat": "6x"},
               {"index": 2, "repeat": "x, v", "repeats": 6}],
}


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_ai_draft_without_gauge_does_not_invent_one():
    """A missing gauge used to default to 30/36, which printed a fake size. The
    draft's `foundation: true` is read the same way: as nothing."""
    p = _draft_to_pattern(_DRAFT, "test")
    assert p.gauge is None
    assert "no finished size is claimed" in p.provenance
    assert p.material.hook_mm == 3.0
    assert p.components[0].rounds[0].claims_fresh_start
    assert not p.components[0].rounds[1].claims_fresh_start


def test_ai_draft_with_a_real_gauge_keeps_it():
    p = _draft_to_pattern({**_DRAFT, "gauge": {"stitches_per_10cm": 24, "rows_per_10cm": 30}},
                          "test")
    assert p.gauge is not None
    assert (p.gauge.stitches_per_10cm, p.gauge.rows_per_10cm) == (24.0, 30.0)


def test_partial_gauge_is_treated_as_absent():
    p = _draft_to_pattern({**_DRAFT, "gauge": {"stitches_per_10cm": 24}}, "test")
    assert p.gauge is None


def test_all_formats_carry_the_expanded_points(tmp_path):
    r = render_pattern(build_star_pattern(), str(tmp_path))
    assert r.profile_path is None, "no gauge means no centimetre silhouette"
    md = _read(r.text_path)
    htm = _read(r.html_path)
    assert os.path.getsize(r.pdf_path) > 5000
    for text, fmt in ((md, "md"), (htm, "html")):
        assert "Point 5" in text and "25-30" in text, f"{fmt} lost the multiplicity"
        assert "base sts" in text.replace("Base sts", "base sts"), fmt
        assert "Not stitch-modelled" in text or "unmodelled" in text.lower(), fmt
    assert r.cov.checked_stitches == 390


def test_edge_rows_are_not_called_magic_rings_in_the_html(tmp_path):
    r = render_pattern(build_star_pattern(), str(tmp_path))
    htm = _read(r.html_path)
    assert "Join yarn and work 6 sc along the base edge." in htm
    point1 = htm.split("Point 1")[1].split("Point 2")[0]
    assert "Magic ring" not in point1


def test_concept_cover_is_labelled_not_presented_as_evidence(tmp_path):
    r = render_pattern(build_star_pattern(), str(tmp_path))
    assert "Concept illustration" not in _read(r.html_path)
    # a cover is only ever a concept: no image here is generated from these counts
    r2 = render_pattern(build_star_pattern(), str(tmp_path / "cover"),
                        cover_image_path=r.chart_path)
    html2 = _read(r2.html_path)
    assert "Concept illustration" in html2
    assert "not a render of this pattern" in html2.lower()
    assert os.path.getsize(r2.pdf_path) > os.path.getsize(r.pdf_path), \
        "the PDF caption should add content"


def test_header_badge_is_scoped_to_arithmetic(tmp_path):
    """A green "0 errors" stamp used to be the only verdict on the page, which
    read as "the whole ornament is proven" while half the parts were prose.
    """
    htm = _read(render_pattern(build_star_pattern(), str(tmp_path)).html_path)
    badge = htm.split('class="stamp">')[1].split("</div>")[0]
    assert "0 stitch-math errors" in badge
    assert "50% of parts stitch-modelled" in badge, badge
    assert 'class="warn"' in badge, "partial coverage must not render as a plain green pass"


def test_the_pattern_document_carries_no_engine_debug(tmp_path):
    """pattern.md is what a maker crochets from; the dossier is what an auditor reads."""
    r = render_pattern(build_star_pattern(), str(tmp_path))
    md, htm = _read(r.text_path), _read(r.html_path)
    assert "engine check:" not in md
    assert "[OK]" not in md and "(OK)" not in md
    assert "Point 1 -- base sts 1-6" in md
    # the same rows in the audit view do show the derivation
    assert "engine check:" in htm


def test_every_added_line_is_tagged_in_both_formats(tmp_path):
    r = render_pattern(build_star_pattern(), str(tmp_path))
    md, htm = _read(r.text_path), _read(r.html_path)
    counts = r.pattern.origin_counts()
    body = md[md.index("## Pattern: parts"):md.index("## Open questions")]
    assert body.count("[ADDED]") == counts["added"]
    assert body.count("[INFERRED]") == 0, "the star's rows are the author's own wording"
    assert body.count("(inferred)") == sum(1 for c in r.pattern.components
                                           if c.hook and c.hook_origin == "inferred")
    assert "class='orig added'" in htm or "class=\"orig added\"" in htm
    assert f"{counts['source']} quoted from your source" in md


def test_a_tip_down_piece_is_drawn_tip_up(tmp_path):
    """Round 1 of the hat is the crown; stacking rows in work order drew the hat
    upside down and the object inverted, like a bucket."""
    base = row_bands(3, 1.0, "from_base")
    tip = row_bands(3, 1.0, "from_tip")
    assert base[0][0] == 0.0 and tip[0][1] == 3.0
    assert tip == [(2.0, 3.0), (1.0, 2.0), (0.0, 1.0)]
    assert row_bands(3, 1.0, None) == base, "an unknown direction must not claim a flip"

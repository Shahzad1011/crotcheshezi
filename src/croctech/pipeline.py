"""End-to-end pipeline: request -> AI draft -> deterministic repair loop -> render.

Nothing renders unless every verified round passes the engine's cross-check. A
failed draft is fed back through `refine_pattern` in a bounded loop; if it still
fails we refuse to render and raise.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .ai import PatternProvider
from .chart import render_chart, render_silhouette
from .engine import Coverage, RoundAudit, audit, audit_blocks, coverage, validate
from .gauge import Dimensions, YarnUsage, compute_dimensions, compute_yarn_usage
from .render_html import render_html
from .render_pdf import build_pdf
from .render_text import render_text
from .schema import Pattern


class CrochetValidationError(Exception):
    pass


@dataclass
class Result:
    pattern: Pattern
    audits: list[RoundAudit]
    dims: Dimensions | None
    yarn: YarnUsage | None
    cov: Coverage
    attempts: int
    text_path: str
    chart_path: str
    profile_path: str | None
    html_path: str
    pdf_path: str


def render_pattern(pattern: Pattern, outdir: str = "out", *,
                   cover_image_path: str | None = None, cover_is_concept: bool = True,
                   tolerance_pct: float = 10.0) -> Result:
    os.makedirs(outdir, exist_ok=True)
    audits = audit(pattern)
    blocks = audit_blocks(pattern)
    cov = coverage(pattern, audits)
    produced = [a.produced for a in audits]

    # The charts describe one piece of the largest part, so pick it by audited
    # rows -- a component whose work lives in a repeated block still counts.
    verified = [c for c in pattern.components if c.kind == "verified"]
    primary = max(verified, key=lambda c: len(c.all_rows)) if verified else None
    if primary:
        p_rows = primary.all_rows
        p_audits = [a for a in audits if a.component == primary.name]
        p_blocks = [b for b in blocks if b.component == primary.name]
    else:
        p_rows, p_audits, p_blocks = [], [], []

    dims = compute_dimensions(pattern, [a.produced for a in p_audits] or produced, tolerance_pct)
    yarn = compute_yarn_usage(pattern, audits)

    text_path = os.path.join(outdir, "pattern.md")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(render_text(pattern, audits, dims, yarn, cov))

    chart_title = f"{pattern.name} — {primary.name}" if primary else pattern.name
    chart_path = render_chart(p_rows, p_audits, chart_title, os.path.join(outdir, "chart.png"),
                              p_blocks)
    # A silhouette is drawn in centimetres, so it needs a real gauge. Without one
    # we omit it rather than plot a shape from invented numbers.
    profile_path = None
    if pattern.gauge is not None:
        profile_path = render_silhouette(p_rows, p_audits, pattern.gauge, chart_title,
                                         os.path.join(outdir, "profile.png"), p_blocks,
                                         build_direction=primary.build_direction)
    html_path = render_html(pattern, audits, dims, yarn=yarn, cov=cov, chart_path=chart_path,
                            profile_path=profile_path, cover_image_path=cover_image_path,
                            cover_is_concept=cover_is_concept,
                            out_path=os.path.join(outdir, "dossier.html"))
    pdf_path = build_pdf(pattern, audits, dims, chart_path=chart_path,
                         cover_image_path=cover_image_path, cover_is_concept=cover_is_concept,
                         profile_path=profile_path, yarn=yarn, cov=cov,
                         out_path=os.path.join(outdir, "pattern.pdf"))
    return Result(pattern, audits, dims, yarn, cov, 0,
                  text_path, chart_path, profile_path, html_path, pdf_path)


def _repair_loop(provider: PatternProvider, draft: Pattern, max_repairs: int):
    errors = validate(draft)
    attempts = 0
    while errors and attempts < max_repairs:
        draft = provider.refine_pattern(draft, errors)
        errors = validate(draft)
        attempts += 1
    return draft, errors, attempts


def generate(request: str, provider: PatternProvider, outdir: str = "out", *,
             cover_image_path: str | None = None, cover_is_concept: bool = True,
             tolerance_pct: float = 10.0, max_repairs: int = 3) -> Result:
    draft = provider.draft_pattern(request)
    pattern, errors, attempts = _repair_loop(provider, draft, max_repairs)
    if errors:
        raise CrochetValidationError(
            f"Draft failed engine validation after {attempts} repair(s); refusing to "
            f"render.\n- " + "\n- ".join(errors))
    result = render_pattern(pattern, outdir, cover_image_path=cover_image_path,
                            cover_is_concept=cover_is_concept, tolerance_pct=tolerance_pct)
    result.attempts = attempts
    return result

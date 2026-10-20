"""ReportLab PDF renderer: a real, multi-page design document -- cover, materials,
gauge, charts, per-component instructions with repeated blocks expanded to their
base-stitch ranges, the source's open questions, and the verification audit.

Anything the source does not state is printed as a gap, never filled in with a
plausible number. The engine's working text is shared with the text renderer
(`render_text.shorthand`) so the three formats cannot drift apart.
"""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .engine import Coverage, RoundAudit, audit_blocks, print_rows
from .gauge import Dimensions, YarnUsage
from .render_text import _open_questions, shorthand
from .schema import Pattern

_ACCENT = colors.HexColor("#d11a2a")
_MUTED = colors.HexColor("#4b5563")
_OK_HEX, _BAD_HEX, _WARN_HEX = "#16a34a", "#dc2626", "#b45309"
_OK = colors.HexColor(_OK_HEX)
_BAD = colors.HexColor(_BAD_HEX)
_WARN = colors.HexColor(_WARN_HEX)


def _scaled_image(path: str, max_w: float, max_h: float):
    iw, ih = ImageReader(path).getSize()
    scale = min(max_w / iw, max_h / ih)
    return Image(path, iw * scale, ih * scale)


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=ss["Title"], fontSize=22, textColor=_ACCENT,
                                spaceAfter=6, alignment=1),
        "sub": ParagraphStyle("s", parent=ss["Normal"], fontSize=11, textColor=_MUTED,
                              alignment=1, spaceAfter=4),
        "h": ParagraphStyle("h", parent=ss["Heading2"], fontSize=14, textColor=_ACCENT,
                            spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontSize=12, textColor=colors.black,
                             spaceBefore=8, spaceAfter=3),
        "h4": ParagraphStyle("h4", parent=ss["Heading4"], fontSize=10.5, textColor=_ACCENT,
                             spaceBefore=6, spaceAfter=2),
        "body": ParagraphStyle("b", parent=ss["Normal"], fontSize=10.5, leading=15),
        "small": ParagraphStyle("sm", parent=ss["Normal"], fontSize=9, leading=12,
                                textColor=_MUTED, leftIndent=10),
        "warn": ParagraphStyle("w", parent=ss["Normal"], fontSize=9.5, leading=13,
                               textColor=_WARN, leftIndent=10),
        "cap": ParagraphStyle("c", parent=ss["Normal"], fontSize=8.5, leading=11,
                              textColor=_MUTED, alignment=1),
    }


def _round_html(rnd, a: RoundAudit) -> str:
    """Author's wording is the instruction; the engine's count sits beside it as proof."""
    head = f"<b>Row {rnd.index}</b>" + (f" &mdash; {rnd.label}" if rnd.label else "") + ": "
    colr = f" <font color='#6b7280'>// {rnd.color}</font>" if rnd.color else ""
    verdict = (f"<font color='{_OK_HEX if a.ok else _BAD_HEX}'>"
               f"{'OK' if a.ok else 'ERROR'}</font>")
    if rnd.spec_text:
        return (f"{head}{rnd.spec_text} <b>[{a.produced} sts]</b>{colr} {verdict}<br/>"
                f"<font size='8' color='#6b7280'>engine check: {shorthand(rnd)} "
                f"&rarr; {a.produced} sts (declared {a.declared_total})</font>")
    return f"{head}{shorthand(rnd)} <b>[{a.produced} sts]</b>{colr} {verdict}"


def _audit_table(audits: list[RoundAudit]) -> Table:
    data = [["Component", "Row", "Inst", "Base sts", "Start", "Consumed", "Created",
             "Declared", "Status"]]
    for a in audits:
        rng = f"{a.base_range[0]}-{a.base_range[1]}" if a.base_range else "-"
        data.append([a.component, str(a.index), str(a.instance or "-"), rng,
                     str(a.start_count), str(a.consumed), str(a.produced),
                     str(a.declared_total), "OK" if a.ok else "ERROR"])
    t = Table(data, colWidths=[26 * mm, 10 * mm, 10 * mm, 18 * mm, 14 * mm, 20 * mm,
                               16 * mm, 18 * mm, 16 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]
    for i, a in enumerate(audits, start=1):
        style += [("TEXTCOLOR", (-1, i), (-1, i), _OK if a.ok else _BAD),
                  ("FONTNAME", (-1, i), (-1, i), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def build_pdf(pattern: Pattern, audits: list[RoundAudit], dims: Dimensions | None, *,
              chart_path: str, cover_image_path: str | None, out_path: str,
              profile_path: str | None = None, yarn: YarnUsage | None = None,
              cov: Coverage | None = None, cover_is_concept: bool = True) -> str:
    st = _styles()
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title=pattern.name, author="Croctech")
    m = pattern.material
    g = pattern.gauge
    parts = [c for c in pattern.components if c.role == "part"]
    ops = [c for c in pattern.components if c.role == "operation"]
    story: list = []

    story.append(Paragraph(pattern.name, st["title"]))
    story.append(Paragraph(
        f"{pattern.item_type.title()} &middot; {len(parts)} part(s) + {len(ops)} finishing "
        f"operation(s) &middot; hooks {', '.join(f'{h} mm' for h in pattern.listed_hooks)}",
        st["sub"]))
    if cover_image_path:
        story.append(Spacer(1, 6))
        story.append(_scaled_image(cover_image_path, 120 * mm, 95 * mm))
        if cover_is_concept:
            story.append(Paragraph(
                "<b>Concept illustration &mdash; not a render of this pattern.</b> It is not "
                "generated from these stitch counts and may show colours, parts or finishes the "
                "instructions do not produce.", st["cap"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(pattern.description, st["body"]))

    if pattern.provenance:
        story.append(Paragraph("Provenance", st["h"]))
        story.append(Paragraph(pattern.provenance, st["body"]))

    story.append(Paragraph("Materials", st["h"]))
    hooks = ", ".join(f"{h} mm" for h in pattern.listed_hooks)
    assigned = "; ".join(f"{c.name}: {c.hook} mm" for c in pattern.components if c.hook)
    story.append(Paragraph(f"Yarn: {m.yarn}<br/>Hooks: {hooks}<br/>"
                           f"Colours: {', '.join(m.colors)}<br/>Notions: {', '.join(m.notions)}",
                           st["body"]))
    if assigned:
        story.append(Paragraph(f"Hook assignment: {assigned}", st["small"]))

    story.append(Paragraph("Abbreviations", st["h"]))
    if pattern.abbreviations:
        story.append(Paragraph(
            "<br/>".join(f"<b>{k}</b> = {v}" for k, v in pattern.abbreviations.items()),
            st["body"]))
    else:
        story.append(Paragraph("None listed.", st["body"]))

    story.append(Paragraph("Gauge &amp; finished dimensions", st["h"]))
    if g is None or dims is None:
        story.append(Paragraph(
            "No gauge was supplied for this item, so <b>no finished size is claimed</b>. "
            "A stitch gauge is the only thing that converts stitch counts into centimetres, "
            "and inventing one would fabricate the size along with it.<br/><br/>"
            "To get exact dimensions: work a 10 &times; 10 cm swatch in sc on the hook listed "
            "above, count its stitches and rows, and re-run the pattern with that gauge.",
            st["body"]))
    else:
        lo, hi = dims.band(dims.widest_diameter_cm)
        hlo, hhi = dims.band(dims.height_cm)
        tag = ("measured from your swatch" if g.calibrated
               else "<b>ASSUMED</b>, not measured from a swatch")
        note = ("" if g.calibrated
                else f"<br/><font size='8.5' color='#b45309'>{g.note}</font>")
        story.append(Paragraph(
            f"Gauge: {g.stitches_per_10cm} sts x {g.rows_per_10cm} rows / 10 cm ({tag}).<br/>"
            f"Widest diameter: ~{dims.widest_diameter_cm:.2f} cm ({lo:.2f}&ndash;{hi:.2f} cm), "
            f"from the widest round's circumference.<br/>"
            f"Worked height: ~{dims.height_cm:.2f} cm ({hlo:.2f}&ndash;{hhi:.2f} cm) &mdash; "
            f"rows &times; row gauge, i.e. how tall the piece is as worked, not a 3D measurement."
            f"{note}", st["body"]))

    if yarn:
        story.append(Paragraph("Yarn usage (estimate)", st["h"]))
        rows = "&nbsp;&nbsp;".join(
            f"<b>{c}</b>: {cu.stitches} sc, ~{cu.meters:.2f} m"
            + (f", ~{cu.grams:.2f} g" if cu.grams is not None else "")
            for c, cu in yarn.by_colour.items())
        tg = f", ~{yarn.total_grams:.2f} g" if yarn.total_grams is not None else ""
        story.append(Paragraph(f"{rows}<br/>Total {yarn.total_stitches} sc, "
                               f"~{yarn.total_meters:.2f} m{tg}. Heuristic; varies with tension. "
                               f"Covers the stitch-checked parts only.", st["body"]))

    questions = _open_questions(pattern)
    if questions:
        story.append(Paragraph("Open questions &mdash; gaps in the source", st["h"]))
        for q in questions:
            story.append(Paragraph(f"&middot; {q}", st["warn"]))

    story.append(PageBreak())
    story.append(Paragraph("Stitch chart" + (" &amp; profile" if profile_path else ""), st["h"]))
    story.append(_scaled_image(chart_path, 130 * mm, 105 * mm))
    story.append(Paragraph("Counts per row, engine-verified. A count profile, not a stitch "
                           "chart: it shows how many stitches a row leaves, not where they sit.",
                           st["cap"]))
    if profile_path:
        story.append(Spacer(1, 6))
        story.append(_scaled_image(profile_path, 105 * mm, 95 * mm))

    story.append(PageBreak())
    by_comp: dict[str, list[RoundAudit]] = {}
    for a in audits:
        by_comp.setdefault(a.component, []).append(a)

    for heading, comps in (("Pattern: parts", parts),
                           ("Pattern: finishing operations", ops)):
        if not comps:
            continue
        story.append(Paragraph(heading, st["h"]))
        for comp in comps:
            qty = f" (make {comp.quantity})" if comp.quantity > 1 else ""
            hk = f" &mdash; hook {comp.hook} mm" if comp.hook else ""
            story.append(Paragraph(f"{comp.name}{qty}{hk}", st["h3"]))
            for note in comp.notes:
                story.append(Paragraph(f"&#9656; {note}", st["small"]))
            if comp.kind != "verified":
                items = [ListItem(Paragraph(s, st["body"])) for s in comp.steps]
                if items:
                    story.append(ListFlowable(items, bulletType="bullet", start="square"))
                continue
            for line in print_rows(comp, by_comp.get(comp.name, [])):
                if line.block_header:
                    join = (" &mdash; join the yarn to these stitches"
                            if line.join_note else "")
                    story.append(Paragraph(f"<b>{line.block_header}{join}</b>", st["h4"]))
                story.append(Paragraph(_round_html(line.rnd, line.audit), st["body"]))
                for n in line.rnd.notes:
                    story.append(Paragraph(f"&#9656; {n}", st["small"]))

    story.append(PageBreak())
    story.append(Paragraph("Verification", st["h"]))
    blocks = audit_blocks(pattern)
    row_errors = [i for a in audits for i in a.issues]
    block_errors = [i for b in blocks for i in b.issues]
    n_err = len(row_errors) + len(block_errors)
    story.append(Paragraph(
        f"<b>Arithmetic:</b> {'PASS' if n_err == 0 else 'FAIL'} &mdash; {n_err} "
        f"stitch-math error(s) across {len(audits)} audited rows. Every count was re-derived "
        f"from the operations and compared with the stated total.", st["body"]))
    if n_err:
        for e in row_errors + block_errors:
            story.append(Paragraph(f"&middot; <font color='#dc2626'>{e}</font>", st["warn"]))
    for b in blocks:
        per = b.base_consumed // max(b.instances, 1)
        story.append(Paragraph(
            f"<b>Multiplicity:</b> {b.label} &mdash; {b.instances} &times; {per} base sts = "
            f"{b.base_consumed}, foundation made {b.base_available}. "
            f"{'OK' if b.ok else 'ERROR'}", st["body"]))
    if cov:
        story.append(Paragraph(
            f"<b>Coverage:</b> {cov.checked_stitches} stitches counted across "
            f"{', '.join(cov.checked_parts)}. "
            + (f"<b>Not stitch-modelled ({cov.pct_of_parts:.0f}% of parts):</b> "
               f"{', '.join(cov.unmodelled_parts)} &mdash; described steps the arithmetic above "
               f"does not prove." if cov.unmodelled_parts
               else f"All parts are stitch-modelled ({cov.pct_of_parts:.0f}%).")
            + (f"<br/>Finishing operations described in words, not counted: "
               f"{', '.join(cov.operations)}." if cov.operations else ""),
            st["body"]))
    story.append(Paragraph(
        "<b>Fidelity to source:</b> not machine-checkable &mdash; see Provenance and the open "
        "questions. A green arithmetic verdict does not certify that this is the pattern you "
        "asked for.", st["body"]))
    story.append(Spacer(1, 6))
    story.append(_audit_table(audits))
    doc.build(story)
    return out_path

"""Render a validated pattern into human-readable text, organised by component.

The maker-facing document contains instructions and nothing else. The engine's
working text, the per-row status and the audit table belong to the audit view
(`audit_lines=True`, used by the HTML dossier and the PDF appendix), because a
customer pattern that carries `engine check:` lines is a debug log wearing a
pattern's clothes.

Every line the framework wrote rather than transcribed is tagged, so a reader can
tell the author's words from the expansion of them.
"""

from __future__ import annotations

from .engine import Coverage, RoundAudit, audit_blocks, print_rows
from .gauge import Dimensions, YarnUsage
from .schema import Pattern

_OP_WORD = {"sc": "sc", "dc": "dc", "inc": "2 sc in next st", "dec": "sc2tog", "sk": "sk 1"}

_START_WORD = {
    "magic_ring": "Magic ring, {n} sc.",
    "edge": "Join yarn and work {n} sc along the base edge.",
    "chain": "Chain {n}, work into it.",
    "sl_knot": "Slip knot, work {n} sc.",
}

_ORIGIN_TAG = {"source": "", "inferred": " [INFERRED]", "added": " [ADDED]"}


def tag(origin: str) -> str:
    return _ORIGIN_TAG.get(origin, "")


def shorthand(rnd) -> str:
    """Engine-derived working text, used when the author supplied no wording.

    `starts_from` decides how a fresh start is worded: telling a maker to open a
    magic ring for a row that is worked along an edge is the wrong action, not a
    stylistic choice.
    """
    if rnd.claims_fresh_start:
        body = _START_WORD[rnd.starts_from].format(n=rnd.declared_total)
    elif rnd.cycle:
        seg = ""
        if rnd.leading:
            seg += " ".join(_OP_WORD[op.kind] * op.count for op in rnd.leading) + ", "
        seg += f"({rnd.repeat_notation}) x{rnd.repeats}"
        if rnd.trailing:
            seg += ", " + " ".join(_OP_WORD[op.kind] * op.count for op in rnd.trailing)
        body = f"Work {seg}."
    else:
        body = f"Work {rnd.declared_total} sc around."
    if rnd.flat:
        body += " ch 1, fasten off." if rnd.fasten_off else " ch 1, turn."
    elif rnd.join_sl:
        body += " sl st to join."
    return body.strip()


def _round_line(rnd, a: RoundAudit, indent: str = "  ", audit_lines: bool = False) -> list[str]:
    """In the maker's document, the row is its own wording plus its count. The
    engine's independent derivation is the audit view's business."""
    work = shorthand(rnd)
    text = rnd.spec_text or work
    status = f" ({'OK' if a.ok else 'ERROR'})" if audit_lines else ""
    colr = f"  // {rnd.color}" if rnd.color else ""
    head = f"{indent}Row {rnd.index}" + (f" — {rnd.label}" if rnd.label else "") + ": "
    out = [f"{head}{text} [{a.produced} sts]{status}{colr}{tag(rnd.origin)}"]
    if audit_lines and rnd.spec_text:
        out.append(f"{indent}    engine check: {work} -> {a.produced} sts "
                   f"(declared {a.declared_total})")
    return out


def _open_questions(pattern: Pattern) -> list[str]:
    q = [f"{t} -- used by the source but never defined" for t in pattern.undefined_terms]
    for comp in pattern.components:
        q += [n for n in comp.notes if n.startswith(("Open question", "Note:"))]
    if pattern.unassigned_hooks:
        hs = ", ".join(f"{h} mm" for h in pattern.unassigned_hooks)
        q.append(f"Hook {hs} is listed in Materials but no part says where to use it")
    return q


def _provenance_lines(pattern: Pattern) -> list[str]:
    """The provenance paragraph is allowed to claim only what the tally can back."""
    counts = pattern.origin_counts()
    lines = ["## Provenance", f"- {pattern.provenance}"]
    lines.append(f"- Tally of instruction lines: {counts['source']} quoted from your source, "
                 f"{counts['inferred']} inferred, {counts['added']} added by the framework. "
                 f"Every non-source line is tagged [INFERRED] or [ADDED] where it appears.")
    return lines


def _materials_lines(pattern: Pattern) -> list[str]:
    m = pattern.material
    hooks = ", ".join(f"{h} mm" for h in pattern.listed_hooks) or "not stated in the source"
    colours = ", ".join(m.colors) or "not stated in the source (choose yours)"
    lines = ["## Materials", f"- Yarn: {m.yarn or 'not stated in the source'}", f"- Hooks: {hooks}",
             f"- Colours: {colours}", f"- Notions: {', '.join(m.notions) or 'not stated'}"]
    assigned = [f"{c.name} {c.hook} mm" + ("" if c.hook_origin == "source" else " (inferred)")
                for c in pattern.components if c.hook]
    if assigned:
        lines.append("- Hook assignment: " + ", ".join(assigned))
    return lines


def _gauge_lines(pattern: Pattern, dims: Dimensions | None) -> list[str]:
    g = pattern.gauge
    lines = ["## Gauge & finished dimensions"]
    if g is None or dims is None:
        return lines + [
            ("- No gauge supplied, so no finished size is claimed. A stitch gauge is the only "
             "thing that turns stitch counts into centimetres, and inventing one would invent "
             "the size too."),
            ("- To get exact dimensions: work a 10 x 10 cm swatch in sc on the hook listed "
             "above, count the stitches and rows, then re-run with that gauge.")]

    lo, hi = dims.band(dims.widest_diameter_cm)
    hlo, hhi = dims.band(dims.height_cm)
    tag_txt = (f"measured from your swatch, attested by {g.attested_by}" if g.calibrated
               else "NOT MEASURED -- no swatch was attested, so every centimetre here is "
                    "illustrative")
    lines.append(f"- Gauge: {g.stitches_per_10cm} sts x {g.rows_per_10cm} rows / 10 cm "
                 f"({tag_txt})")
    lines.append(f"- Widest diameter: ~{dims.widest_diameter_cm:.2f} cm [{lo:.2f}-{hi:.2f} cm] "
                 "(from the widest round's circumference)")
    lines.append(f"- Worked height: ~{dims.height_cm:.2f} cm [{hlo:.2f}-{hhi:.2f} cm] "
                 "(rows x row gauge -- how tall the piece is as worked, not a 3D measurement)")
    if not g.calibrated:
        lines.append(f"- NOTE: {g.note}")
    return lines


def render_text(pattern: Pattern, audits: list[RoundAudit], dims: Dimensions | None,
                yarn: YarnUsage | None = None, cov: Coverage | None = None,
                audit_lines: bool = False) -> str:
    lines: list[str] = [f"# {pattern.name}", "", pattern.description, ""]

    if pattern.provenance:
        lines += _provenance_lines(pattern) + [""]

    lines += _materials_lines(pattern) + [""]

    if pattern.abbreviations:
        lines.append("## Abbreviations")
        for abbr, meaning in pattern.abbreviations.items():
            lines.append(f"- {abbr} = {meaning}")
        lines.append("")

    lines += _gauge_lines(pattern, dims) + [""]

    if yarn:
        lines.append("## Yarn usage (estimate)")
        for colour, cu in yarn.by_colour.items():
            gram = f", ~{cu.grams:.2f} g" if cu.grams is not None else ""
            lines.append(f"- {colour}: {cu.stitches} sc, ~{cu.meters:.2f} m{gram}")
        tg = f", ~{yarn.total_grams:.2f} g" if yarn.total_grams is not None else ""
        lines.append(f"- Total: {yarn.total_stitches} sc, ~{yarn.total_meters:.2f} m{tg}")
        lines.append("- Covers the stitch-checked parts only, at the quantities listed.\n")

    by_comp: dict[str, list[RoundAudit]] = {}
    for a in audits:
        by_comp.setdefault(a.component, []).append(a)

    for heading, role in (("Pattern: parts", "part"),
                          ("Pattern: finishing operations", "operation")):
        comps = [c for c in pattern.components if c.role == role]
        if not comps:
            continue
        lines.append(f"\n## {heading}")
        for comp in comps:
            qty = f" (make {comp.quantity})" if comp.quantity > 1 else ""
            hk = ""
            if comp.hook:
                hk = f" [hook {comp.hook} mm]" + ("" if comp.hook_origin == "source"
                                                  else " (inferred)")
            lines.append(f"\n### {comp.name}{qty}{hk}")
            for note in comp.notes:
                mark = "!" if note.startswith(("Open question", "Note:")) else ">"
                lines.append(f"  {mark} {note}")

            if comp.kind != "verified":
                for s in comp.steps:
                    lines.append(f"  - {s.text}{tag(s.origin)}")
                    if s.why:
                        lines.append(f"      why: {s.why}")
                continue

            for line in print_rows(comp, by_comp.get(comp.name, [])):
                if line.block_header:
                    lines.append(f"\n  {line.block_header}"
                                 + ("  (join the yarn to these stitches)"
                                    if line.join_note else ""))
                indent = "    " if line.audit.instance is not None else "  "
                lines += _round_line(line.rnd, line.audit, indent=indent,
                                     audit_lines=audit_lines)
                for n in line.rnd.notes:
                    lines.append(f"{indent}  > {n}")

    questions = _open_questions(pattern)
    if questions:
        lines.append("\n## Open questions -- gaps in the source, not answered for you")
        lines += [f"- {q}" for q in questions]

    errors = [i for a in audits for i in a.issues] + [i for b in audit_blocks(pattern)
                                                      for i in b.issues]
    lines += ["", "## Verification"]
    lines.append(f"- Arithmetic: {len(errors)} stitch-math error(s) across "
                 f"{len(audits)} audited rows")
    for e in errors:
        lines.append(f"  ERROR {e}")
    if cov:
        pct = f"{cov.pct_of_parts:.0f}% of parts"
        lines.append(f"- Coverage: {cov.checked_stitches} sts counted in "
                     f"{', '.join(cov.checked_parts)}")
        if cov.unmodelled_parts:
            lines.append(f"  Not stitch-modelled ({pct}): {', '.join(cov.unmodelled_parts)}")
            lines.append("  These are described steps; the arithmetic above does not prove them.")
        else:
            lines.append(f"  All parts are stitch-modelled ({pct}).")
        if cov.operations:
            lines.append(f"- Finishing operations described in words, not counted: "
                         f"{', '.join(cov.operations)}")
    lines.append("- Fidelity to source: see the Provenance tally -- every added or inferred "
                 "line is tagged in the instructions themselves.")

    if not audit_lines:
        lines.append("")
        return "\n".join(lines)

    lines.append("")
    lines.append(f"{'Component':<14}{'Row':>4}{'Inst':>5}{'Base sts':>10}"
                 f"{'Start':>7}{'Worked':>8}{'Made':>6}{'Claimed':>9}  Status")
    for a in audits:
        rng = f"{a.base_range[0]}-{a.base_range[1]}" if a.base_range else "-"
        lines.append(f"{a.component:<14}{a.index:>4}{(a.instance or '-'):>5}{rng:>10}"
                     f"{a.start_count:>7}{a.consumed:>8}{a.produced:>6}"
                     f"{a.declared_total:>9}  {'OK' if a.ok else 'ERROR'}")
    for b in audit_blocks(pattern):
        lines.append(f"\n{b.label}: {b.instances} x {b.base_consumed // max(b.instances, 1)} "
                     f"= {b.base_consumed} base sts, foundation made {b.base_available}  "
                     f"{'OK' if b.ok else 'ERROR'}")
    return "\n".join(lines)

"""Self-contained interactive HTML dossier: charts, instructions with repeated
blocks expanded, the source's open questions, and the verification audit -- all
inlined so the single .html opens anywhere.

The engine's working text comes from `render_text.shorthand`, shared with the
text and PDF renderers, so the three formats cannot state a row differently.
"""

from __future__ import annotations

import base64
import html
import os

from .engine import Coverage, RoundAudit, audit_blocks, print_rows
from .gauge import Dimensions, YarnUsage
from .render_text import _open_questions, shorthand
from .schema import Pattern


def _b64(path: str | None) -> str | None:
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _esc(s) -> str:
    return html.escape(str(s))


def _otag(origin: str) -> str:
    """A visible, per-line provenance badge. `source` needs no badge: the default
    is only trustworthy if the exceptions are marked."""
    return "" if origin == "source" else f"<span class='orig {origin}'>{origin.upper()}</span>"


def render_html(pattern: Pattern, audits: list[RoundAudit], dims: Dimensions | None, *,
                yarn: YarnUsage | None = None, cov: Coverage | None = None,
                chart_path: str | None = None, profile_path: str | None = None,
                cover_image_path: str | None = None, cover_is_concept: bool = True,
                audit_lines: bool = True,
                out_path: str = "out/dossier.html") -> str:
    m = pattern.material
    g = pattern.gauge
    parts = [c for c in pattern.components if c.role == "part"]
    ops = [c for c in pattern.components if c.role == "operation"]
    blocks = audit_blocks(pattern)
    errors = [i for a in audits for i in a.issues] + [i for b in blocks for i in b.issues]
    arithmetic = ("PASS - 0 stitch-math errors" if not errors
                  else f"FAIL - {len(errors)} stitch-math errors")

    def img(path):
        b = _b64(path)
        return f'<img src="data:image/png;base64,{b}"/>' if b else ""

    rows = "".join(
        f"<tr><td>{_esc(a.component)}</td><td>{a.index}</td>"
        f"<td>{a.instance if a.instance else '-'}</td>"
        f"<td>{_esc(f'{a.base_range[0]}-{a.base_range[1]}' if a.base_range else '-')}</td>"
        f"<td>{_esc(a.color or '-')}</td>"
        f"<td>{a.start_count}</td><td>{a.consumed}</td><td>{a.produced}</td>"
        f"<td>{a.declared_total}</td><td class=\"{'ok' if a.ok else 'bad'}\">"
        f"{'OK' if a.ok else 'ERROR'}</td></tr>" for a in audits)

    by_comp: dict[str, list[RoundAudit]] = {}
    for a in audits:
        by_comp.setdefault(a.component, []).append(a)

    def section(comp) -> str:
        qty = f' <span class="q">x{comp.quantity}</span>' if comp.quantity > 1 else ""
        hk = ""
        if comp.hook:
            hk = (f' <span class="q">hook {comp.hook} mm</span>'
                  + _otag(comp.hook_origin))
        body = "".join(
            f"<div class='cnotes'><small>{'! ' if n.startswith(('Open question', 'Note:')) else '› '}"
            f"{_esc(n)}</small></div>" for n in comp.notes)
        if comp.kind != "verified":
            return (f"<h3>{_esc(comp.name)}{qty}{hk}</h3>{body}<ul>"
                    + "".join(f"<li>{_esc(s.text)}{_otag(s.origin)}"
                              + (f"<br/><small>why: {_esc(s.why)}</small>" if s.why else "")
                              + "</li>" for s in comp.steps) + "</ul>")
        lis = []
        for line in print_rows(comp, by_comp.get(comp.name, [])):
            if line.block_header:
                join = " — join the yarn to these stitches" if line.join_note else ""
                lis.append(f"<li class='blk'><b>{_esc(line.block_header)}{join}</b></li>")
            r, a = line.rnd, line.audit
            label = f" — {_esc(r.label)}" if r.label else ""
            status = (f"<span class='{'ok' if a.ok else 'bad'}'>[{'OK' if a.ok else 'ERROR'}]</span>"
                      if audit_lines else "")
            colr = f"<span class='colr'>{_esc(r.color or '')}</span>"
            check = (f"<br/><small>engine check: {_esc(shorthand(r))} &rarr; {a.produced} sts "
                     f"(declared {a.declared_total})</small>") if (r.spec_text and
                                                                   audit_lines) else ""
            main = (f"<b>R{r.index}</b>{label} — {_esc(r.spec_text or shorthand(r))} "
                    f"<span class='cnt'>[{a.produced} sts]</span> {status}{_otag(r.origin)}")
            notes = "".join(f"<br/><small>› {_esc(n)}</small>" for n in r.notes)
            lis.append(f"<li>{colr}{main}{check}{notes}</li>")
        return f"<h3>{_esc(comp.name)}{qty}{hk}</h3>{body}<ul>" + "".join(lis) + "</ul>"

    instr_parts = "".join(section(c) for c in parts)
    instr_ops = "".join(section(c) for c in ops)

    yarn_html = ""
    if yarn:
        li = "".join(f"<li>{_esc(c)}: {cu.stitches} sc, ~{cu.meters:.2f} m"
                     + (f", ~{cu.grams:.2f} g" if cu.grams is not None else "") + "</li>"
                     for c, cu in yarn.by_colour.items())
        tg = f", ~{yarn.total_grams:.2f} g" if yarn.total_grams is not None else ""
        yarn_html = (f"<section><h2>Yarn usage (estimate)</h2><ul>{li}</ul>"
                     f"<p>Total {yarn.total_stitches} sc, ~{yarn.total_meters:.2f} m{tg}. "
                     f"Covers the stitch-checked parts only.</p></section>")

    if g is None or dims is None:
        gauge_html = (
            "<section><h2>Gauge &amp; dimensions</h2><p><b>No gauge supplied, so no finished "
            "size is claimed.</b> A stitch gauge is the only thing that converts stitch counts "
            "into centimetres; inventing one would fabricate the size with it.</p>"
            "<p><small>To get exact dimensions: work a 10 × 10 cm swatch in sc on the hook "
            "listed above, count its stitches and rows, then re-run with that gauge.</small>"
            "</p></section>")
    else:
        lo, hi = dims.band(dims.widest_diameter_cm)
        hlo, hhi = dims.band(dims.height_cm)
        attest = (f"measured from your swatch, attested by {_esc(g.attested_by)}" if g.calibrated
                  else "<b style='color:#b45309'>NOT MEASURED</b> &mdash; no swatch was attested, "
                       "so every centimetre here is illustrative")
        gauge_html = (
            "<section><h2>Gauge &amp; dimensions</h2><div class=\"grid\">"
            f"<div class=\"kv\"><b>Gauge</b>: {g.stitches_per_10cm} sts x {g.rows_per_10cm} "
            f"rows / 10 cm ({attest})<br/><small>{_esc(g.note)}</small></div>"
            f"<div class=\"kv\"><b>Widest diameter</b>: ~{dims.widest_diameter_cm:.2f} cm "
            f"({lo:.2f}–{hi:.2f} cm), from the widest round's circumference"
            f"<br/><b>Worked height</b>: ~{dims.height_cm:.2f} cm ({hlo:.2f}–{hhi:.2f} cm)"
            f"<br/><small>rows × row gauge — how tall the piece is as worked, not a 3D "
            f"measurement</small></div></div></section>")

    abbr_html = ""
    if pattern.abbreviations:
        abbr_html = ("<section><h2>Abbreviations</h2><div class=\"grid\">" + "".join(
            f"<div class=\"kv\"><b>{_esc(k)}</b> = {_esc(v)}</div>"
            for k, v in pattern.abbreviations.items()) + "</div></section>")

    prov_html = ""
    if pattern.provenance:
        counts = pattern.origin_counts()
        prov_html = (
            "<section><h2>Provenance</h2><p>" + _esc(pattern.provenance) + "</p>"
            f"<p><small>Tally of instruction lines: <b>{counts['source']}</b> quoted from your "
            f"source, <b>{counts['inferred']}</b> inferred, <b>{counts['added']}</b> added by the "
            "framework. Lines that are not yours carry the tag you see next to them.</small></p>"
            "</section>")

    questions = _open_questions(pattern)
    questions_html = ("<section><h2>Open questions — gaps in the source</h2><ul>"
                      + "".join(f"<li class='warn'>{_esc(q)}</li>" for q in questions)
                      + "</ul></section>") if questions else ""

    cover_html = ""
    if cover_image_path:
        cover_html = img(cover_image_path)
        if cover_is_concept:
            cover_html += ("<p class='cap'><b>Concept illustration — not a render of this "
                           "pattern.</b> It is not drawn from these stitch counts and may show "
                           "colours, parts or finishes the instructions do not produce.</p>")

    multiplicity = "".join(
        f"<li>{_esc(b.label)} — {b.instances} × {b.base_consumed // max(b.instances, 1)} base "
        f"sts = {b.base_consumed}, foundation made {b.base_available}: "
        f"<span class='{'ok' if b.ok else 'bad'}'>{'OK' if b.ok else 'ERROR'}</span></li>"
        for b in blocks)

    coverage_html = ""
    if cov:
        coverage_html = (
            f"<p><b>Coverage:</b> {cov.checked_stitches} stitches counted across "
            f"{_esc(', '.join(cov.checked_parts))}. "
            + (f"<b class='warn'>Not stitch-modelled ({cov.pct_of_parts:.0f}% of parts):</b> "
               f"{_esc(', '.join(cov.unmodelled_parts))} — described steps the arithmetic does "
               f"not prove." if cov.unmodelled_parts else
               f"All parts are stitch-modelled ({cov.pct_of_parts:.0f}%).") + "</p>")
        if cov.operations:
            coverage_html += (f"<p><small>Finishing operations described in words, not counted: "
                              f"{_esc(', '.join(cov.operations))}.</small></p>")

    hooks = (", ".join(f"{h} mm" for h in pattern.listed_hooks)
             or "not stated in the source")
    colours = (", ".join(m.colors) or "not stated in the source (choose yours)")

    # The badge is scoped to arithmetic: it means "every count reconciles", not
    # "the whole ornament was checked" -- coverage is stated next to it.
    stamp = arithmetic + ("" if cov is None else
                         f" · {cov.pct_of_parts:.0f}% of parts stitch-modelled")

    stamp_class = "bad" if errors else ("warn" if (cov and not cov.complete) else "ok")

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_esc(pattern.name)} — Croctech dossier</title>
<style>
:root{{--accent:#d11a2a;--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb}}
*{{box-sizing:border-box}}body{{font-family:system-ui,Segoe UI,Roboto,Arial;color:var(--ink);
margin:0;background:#f8fafc;line-height:1.5}}
header{{background:#fff;border-bottom:3px solid var(--accent);padding:24px;display:flex;gap:20px;
align-items:center;flex-wrap:wrap}}header img{{max-height:140px;border-radius:12px;border:1px solid var(--line)}}
h1{{margin:0;font-size:24px;color:var(--accent)}}.sub{{color:var(--muted)}}
.stamp{{font-weight:700}}.ok{{color:#16a34a;font-weight:700}}.bad{{color:#dc2626;font-weight:700}}
.warn{{color:#b45309}}.orig{{font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;vertical-align:1px}}.orig.added{{background:#fef3c7;color:#92400e}}.orig.inferred{{background:#e0e7ff;color:#3730a3}}.cap{{font-size:11.5px;color:var(--muted)}}
main{{max-width:1000px;margin:0 auto;padding:20px}}
section{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:16px 0}}
h2{{margin:0 0 10px;font-size:16px}}h3{{margin:14px 0 6px;font-size:14px;color:var(--accent)}}
.q{{color:var(--muted);font-weight:400;font-size:12px}}
table{{border-collapse:collapse;width:100%;font-size:12px}}
th,td{{border:1px solid var(--line);padding:5px 6px;text-align:center}}
th{{background:#111827;color:#fff}}
ul{{margin:6px 0}}.cnt{{color:#6b7280}}.colr{{float:right;color:#9ca3af}}
li.blk{{list-style:none;background:#fef3c7;border-left:3px solid #b45309;margin:8px 0 2px;
padding:4px 8px;border-radius:4px}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}@media(max-width:720px){{.charts{{grid-template-columns:1fr}}}}
.charts img{{width:100%;border:1px solid var(--line);border-radius:10px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}@media(max-width:720px){{.grid{{grid-template-columns:1fr}}}}
.kv b{{color:var(--accent)}}small{{color:var(--muted)}}.cnotes{{margin:2px 0 6px}}
</style></head>
<body>
<header>{cover_html if cover_image_path else ''}
  <div><h1>{_esc(pattern.name)}</h1>
  <div class="sub">{_esc(pattern.item_type.title())} · {len(parts)} part(s) + {len(ops)}
  finishing operation(s) · hooks {hooks}</div>
  <div class="stamp"><span class="{stamp_class}">{_esc(stamp)}</span></div>
  </div>
</header>
<main>
{prov_html}
<section><h2>Materials</h2><div class="kv">{_esc(m.yarn) or 'not stated'}<br/>Hooks: {hooks}<br/>Colours: {colours}<br/>Notions: {_esc(', '.join(m.notions)) or 'not stated'}</div>
<p><small>Hook assignment: {_esc(', '.join(f'{c.name} {c.hook} mm' + ('' if c.hook_origin == 'source' else ' (inferred)') for c in pattern.components if c.hook) or 'not stated')}</small></p>
</section>
{abbr_html}
{gauge_html}
<section><h2>Charts</h2><div class="charts">{img(chart_path)}{img(profile_path)}</div>
<p class="cap">Counts per row, engine-verified. These are count charts, not stitch charts: they
show how many stitches a row leaves, not where the stitches sit or what shape the piece
makes.</p></section>
{yarn_html}
{questions_html}
<section><h2>Pattern: parts</h2>{instr_parts}</section>
{f'<section><h2>Pattern: finishing operations</h2>{instr_ops}</section>' if instr_ops else ''}
<section><h2>Verification</h2>
<p><b>Arithmetic:</b> {_esc(arithmetic)} across {len(audits)} audited rows. Every count was
re-derived from the operations and compared with the stated total.</p>
{"".join(f"<p class='bad'>· {_esc(e)}</p>" for e in errors)}
{f"<ul>{multiplicity}</ul>" if multiplicity else ""}
{coverage_html}
<p><b>Fidelity to source:</b> not machine-checkable — see Provenance and the open questions.
A green arithmetic verdict does not certify that this is the pattern you asked for.</p>
<table><thead><tr><th>Component</th><th>Row</th><th>Inst</th><th>Base sts</th><th>Colour</th>
<th>Start</th><th>Consumed</th><th>Created</th><th>Declared</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table></section>
<p><small>Generated by Croctech — the design is authored, the engine computes and verifies every
count.</small></p>
</main></body></html>"""

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_path

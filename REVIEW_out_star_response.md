# Response to `REVIEW_out_star.md` — claim-by-claim verification

**Reviewed by:** Qoder agent, 2026‑10‑20.
**Method:** every claim in the review was re-tested against the code and the
regenerated artefacts in `out/star`, not against the reviewer's summary. Where a
claim was true, the structural cause was fixed and a test was added so it cannot
come back. Where a claim was written against the stale 03:36 artefacts and had
already been fixed, that is stated with the evidence.

**Headline:** of the review's substantive claims, **21 were true and are now
fixed**, **9 were already fixed before the review landed** (it read `out/star`
generated at 03:36; the spec-fidelity rework shipped at 04:06), **1 is false**,
and **2 are true but remain open** (§4 stitch chart, §7.1 source ingestion).
The central blocker — points 2–5 existing only as a sentence, with the audit
table printing a false green over 24 abandoned base stitches — was real and is
now impossible.

---

## 1. The blocker (§2) — true, fixed structurally

| Claim | Verdict | Fix |
|---|---|---|
| "Magic ring / fresh start, 6 sc" for a row worked along the base edge | **True** | `RoundSpec.starts_from` (`magic_ring` / `edge` / `chain` / `sl_knot`) drives the engine's working text. Point row 1 is `starts_from="edge"` and now reads *"Join yarn and work 6 sc along the base edge."* |
| Point count reads as five **or six**; 6 would need 36 base stitches | **True** | The five points are a `Block(instances=5, consumes_base_stitches=6)`. The engine refuses any other product: `5 × 6 = 30` is checked against the **engine's** count of the previous round, not the author's claim. |
| `Star 6 30 6 6 6 OK` — a start count reported but never enforced | **True, and the worst finding** | Block-instance rows are no longer exempted as fresh starts: row 1 of each point is audited against its own 6-stitch allocation. The table gained `Inst` and `Base sts` columns, and a block reconciliation line prints under it. |

Proved by tests, not by assertion:

- `test_point_instances_must_exactly_exhaust_the_base` — setting `instances = 6`
  must produce *"6 instances x 6 base sts = 36, but the previous round made 30"*.
- `test_too_few_instances_is_also_an_error` — 4 instances is caught too.
- `test_each_point_must_work_its_whole_allocation` — a point that works 5 of its
  6 base stitches fails with *"consume 5 sts but you started with 6"*.
- `test_undeclared_base_allocation_is_refused` — omitting
  `consumes_base_stitches` is an error, not a silent pass.

## 2. Inventions (§5) — true, removed

| Claim | Verdict | Fix |
|---|---|---|
| "safety eyes" added to Notions | **True** | Notions are exactly `scissors, glue, yarn needle, fiber filling` (`test_no_invented_notions`). The eyes the source uses but never lists are surfaced as an open question instead. |
| Gauge 22 × 26 invented | **True** | `Pattern.gauge is None` for this item. |
| 4.34 cm / 3.85 cm printed as specifications | **True** | No dimensions, no yarn metres, and **no silhouette** are emitted without a gauge (`test_no_gauge_means_no_invented_dimensions`, and the demo prints `profile: omitted`). |
| `sl st to join` on every circular round | **True** | `join_sl=False` on all star rounds — the source works continuously and says "no sl st" in row 1 (`test_no_join_is_invented_where_the_source_worked_continuous`). |
| 1.93 m yarn figure | **Already fixed** before the review (absent without a gauge) — but the *mechanism* behind it was still broken, see §4. |
| "Height" reported as the object's height | **True** | Relabelled **"Worked height (rows × row gauge)"** in all three formats, with the widest diameter labelled as derived from the widest round's circumference. |

## 3. Structural causes (§7) — all true, all addressed

| § | Claim | Status |
|---|---|---|
| 7.2 | The schema *forces* invention: gauge required, single `hook_mm`, no per-part tool | **Fixed.** `gauge` is Optional; `Component.hook` exists; `Pattern.unassigned_hooks` turns a listed-but-unused hook into a printed gap. The AI path no longer defaults a gauge: `_draft_to_pattern` builds one **only** if the draft supplies both numbers, and the Gemini prompt now says *"Omit gauge entirely unless the request states a measured swatch."* (`test_ai_draft_without_gauge_does_not_invent_one`, `test_partial_gauge_is_treated_as_absent`) |
| 7.3 | `kind="manual"` is an escape hatch that rewards prose; "PASS" from `err == 0` | **Fixed as far as the model allows.** The bare PASS badge is gone. Verification is now four labelled lines — Arithmetic, Multiplicity, Coverage, Fidelity — and Coverage states the stitches counted, the parts not modelled, and the percentage. |
| 7.4 | Multiplicity is a note, not a structure | **Fixed.** `Block` with `instances` and `consumes_base_stitches`; renderers expand every instance with its base-stitch range (`Point 5 — base sts 25-30`, `(join the yarn to these stitches)`). |
| 7.5 | Charts are plotting code, not projections; the title borrows the engine's authority | **Fixed.** The silhouette now takes its point count from the engine's block instances, and draws the taper as a **staircase that alternates ends** — because each turning row skips one stitch at the turn, which flips side every row. The smooth kite is gone. The bar chart is retitled *"Stitches left per row"*, shows one instance with `1.1 … 5.1` labels, states *"Point worked x5"*, and carries the caption *"a count profile, not a stitch chart: it shows how many stitches a row leaves, not where they sit."* |
| 7.6 | Images are decoration presented as evidence | **Fixed.** Any cover is captioned **"Concept illustration — not a render of this pattern. It is not generated from these stitch counts and may show colours, parts or finishes the instructions do not produce."** (`test_concept_cover_is_labelled_not_presented_as_evidence`) |
| 7.7 | "PASS" measures the wrong thing and reads as "this pattern is correct" | **Fixed.** The PDF/HTML/MD verdict ends with: *"Fidelity to source: not machine-checkable — see Provenance and the open questions. A green arithmetic verdict does not certify that this is the pattern you asked for."* |
| 7.8 | No provenance | **Fixed.** `Pattern.provenance` is printed in all three formats. The star records that it is a hand transcription and that no instruction wording is model output; AI drafts record the provider and that the engine authored every total. |
| 7.9 | The mode error: three statement layers collapse into one voice | **Addressed, not eliminated.** The renderers now separate them visibly: the author's wording is the printed instruction of record, the engine's independent count sits beneath it as `engine check:`, derived numbers are tagged ASSUMED or omitted, and gaps appear under *Open questions*. What remains true is 7.1 below. |
| 7.1 | The source is not in the system; nothing can check the fixture against it | **Still true.** `star.py` is a hand-typed transcription and the pipeline still has no ingestion of the original document, so machine-checked fidelity is out of reach. The artefacts now *say* this instead of hiding it. |

## 4. The numbers (§8) — true, and one the review did not name

| Claim | Verdict | What changed |
|---|---|---|
| 115 modelled stitches vs ~456 in the object | **True** | Coverage now reports **390** stitches — the two stars (2 × 190, all five points each) plus two blush — and names what it excludes. |
| Yarn ~4× low | **True, and the cause was worse than the number.** `compute_yarn_usage` zipped `verified_rounds` against per-instance audit rows (misaligning any block pattern) and ignored `quantity` entirely — it quoted a two-star ornament for one star. | Rewritten to take the audits: each part's rows are summed over **all instances** and multiplied by **how many you make**. |
| 1.91 m by colour vs 1.93 m total | **True** | Per-colour figures are rounded once and the total is the sum of the rounded parts, so the printed breakdown always reconciles with the printed total (`test_yarn_usage_totals`, `test_yarn_usage_covers_every_piece_you_make`). |
| Points 5 or 6, undefined | **True** | See §1. |
| Base stitches at R6: 30 available, 6 worked, OK | **True** | See §1. |

## 5. Sewing (§6) — true, replaced

The two-sentence summary is gone. `Sewing` is now eight executable steps: wrong
sides together and point-to-point alignment, ~70 cm of the same yarn on a needle,
start hidden inside at the base of a point, an invisible slip-stitch seam taking
one loop from each layer **one seam stitch per crochet stitch — 30 across the
base**, two stitches into the same space at each of the 5 tips so the point turns
sharp, a ~4 cm opening left, filling worked into each point with the back of a
hook, then closed with the same seam and the tail buried inside.

The review's own caveat is honoured: the "no glue in this seam" fact is stated as
a component note, not as an action, and the loop attachment in `Hanging` is
labelled a recommendation rather than the source's instruction.
`test_sewing_is_a_workable_seam_not_a_summary` pins the required elements.

## 6. Claims that were already false when the review landed

These describe the 03:36 artefacts; the 04:06 rework had already removed them.

- Invented gauge 22 × 26 and the 4.34/3.85 cm figures — absent.
- `profile.png` present for the star — it is omitted (no gauge).
- *"Repeat this whole point 5 times"* — reworded, and now structurally impossible.
- *"Make another star"* missing — present as a note plus `quantity=2`.
- No abbreviations section — present in all three formats, matching the source's eight terms.
- "7 components" category error — headers now read *"4 part(s) + 3 finishing operation(s)"*.
- Hook listed but unassigned — Star 3.5 mm, Flower/Cherry/Blush 1.0 mm; `unassigned_hooks` would print a gap if one appeared.
- Appendix B's "the cover file is JPEG data in a .png" — **false**; it is a genuine PNG (verified by header bytes).

## 7. What is still open

1. **No true stitch chart** (§4). What ships is a verified count profile with
   honest captions. A symbol-per-stitch chart with parent links is not built.
2. **Flower and Cherry are still prose** (§4, §7.3). They cannot be compiled
   today: the op table has no chain-space, slip-stitch-into-ring, or puff
   primitive, so a puff stitch has no stitch-count effect to audit. This is why
   coverage says 50% of parts rather than 100% — and it is stated on the page.
3. **Source ingestion** (§7.1). The pipeline verifies internal consistency, not
   fidelity to a document it never read.
4. **No physical/drape check** — nothing models gauge tension, stuffability or
   whether a 1.0 mm hook can physically take 3-ply acrylic.

## 8. Current state

- `pytest`: **34 passed** (13 of them added specifically to pin this review's
  findings, including 6 that assert a *failure* is detected).
- `ruff check .`: clean. `_gemini_reference/` is excluded — it is the relocated
  comparison tree, not ours to lint.
- `out/star` regenerated: `pattern.md`, `chart.png`, `dossier.html`,
  `pattern.pdf`; `profile.png` deliberately absent.
- Verification block now reads: `Arithmetic: 0 stitch-math error(s) across 31
  audited rows`, `Star / Point x5: 5 × 6 = 30 base sts, foundation made 30 OK`,
  `Coverage: 390 sts counted in Star x2, Blush x2 — not stitch-modelled (50% of
  parts): Flower x2, Cherry x3`.

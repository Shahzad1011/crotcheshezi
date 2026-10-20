# Response to "Challenge Addendum — croctech, tested instead of read"

Date: 2026-10-20 · Repo: `D:\croctech` · Scope: the six flaw groups (A–C) plus the
revised P0 list and the P1 items in the addendum.

Every claim was re-run against the code before anything was changed. The addendum was
right about the substance of five of the six groups, and its two most dangerous
findings (T1, T4) reproduced exactly as described. Two points were already fixed by the
time the addendum ran; those are noted as *already closed*, with the test that now pins
them.

## 1. Verdict per claim

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| A | Sewing section invented wholesale, orientation physically wrong ("wrong sides facing out") | **Conceded** | was `star.py`; now the source's 2 sentences + 8 lines tagged `[ADDED]`, orientation corrected to right sides out / wrong sides together inside |
| A | Assembly/Flower/Materials/hook pairings printed as source facts | **Conceded** | Assembly is now the source's three "Glue…" lines verbatim; the yarn-tail idea is demoted to `[ADDED]`; Materials no longer invents colours or a primary hook; part hooks carry `(inferred)` |
| A | No sentence-level provenance, so the provenance paragraph was an unkeepable promise | **Conceded** | `Origin` on `RoundSpec`, `Step`, `Component.hook_origin`; `Pattern.origin_counts()`; tally printed in all three formats |
| B | Hat profile renders upside down | **Conceded** | `chart.row_bands()` + `Component.build_direction="from_tip"`; `out/profile.png` now has the crown at the top and the brim at the bottom |
| B | Charts are bookkeeping, not design visuals | **Conceded (labels)** | titles/captions renamed to "row-count rose", "stitch count", "count-derived cross-section … not a 3D render". A real symbol chart is still open (§3) |
| B | Buyer-facing output polluted with `engine check:` lines and the audit table | **Conceded** | `render_text(audit_lines=False)` is the default and is what `pattern.md` gets; per-row derivation and OK/ERROR now only appear in the audit view / verification appendix |
| B | Hat described as a "disc" | **Conceded** | `example.py` description now says mini hat with a folded brim |
| B | False open question: "Hook 2.5 mm … no part says where to use it" | **Conceded** | `Pattern.effective_hooks` treats the primary hook as inherited by unstated parts; the hat now reports no gaps |
| C/T1 | Foundation teleport 6→50 validates and renders | **Conceded, fixed** | `foundation` deleted from the schema; a fresh start is *granted by position* (row 1, the row after a fasten-off, a block's opening row) and a mid-run claim raises at construction |
| C/T2 | No geometry bound: 18→36 in one row passes | **Conceded, fixed** | `_OP_GEOMETRY` gives ops width/height in the IR; `_apply_growth_bounds` rejects a row that adds more than twice the part's established rate |
| C/T3 | Duplicate round index corrupts totals, then blames the author | **Conceded, fixed** | `_unique_indices` in `Component`/`Block` validators; `author_totals` keyed by position, not `(component, index)` |
| C/T4 | Model-set `calibrated: true` prints "measured from your swatch" | **Conceded, fixed** | `Gauge.attested_by` is the only route to `calibrated` (now a derived property); the AI draft path never passes it |
| C/T5 | Every drafted round gains a slip-stitch join; every round stamped magic ring | **Already closed** | `join_sl` default flipped to `False` earlier this session; `_draft_to_pattern` grants `starts_from` to row 1 only. Pinned by `test_a_join_is_asserted_never_inherited`, `test_no_join_is_invented_for_a_draft` |
| C/T6 | "0 errors" headline over a 75%-prose pattern | **Conceded, fixed** | badge is scoped and paired with coverage: `PASS - 0 stitch-math errors · 33% of parts stitch-modelled`, rendered `warn` not `ok` |
| D | `author_totals` makes the AI cross-check tautological | **Conceded as a fact, answered structurally** | it is still tautological for drafts — that is why the graph and position layers, which a draft cannot satisfy by echoing numbers, now bind instead |

## 2. What the fixes are made of

* **Position, not permission.** `Component.fresh_starts` is computed from row order; the
  schema refuses a mid-run fresh start unless the previous row fastened off. The escape
  hatch T1 used no longer exists as a field.
* **Three layers.** Sums (`consumed`/`produced`), graph (an ordered cursor walk that names
  the stitch an op reaches past), geometry (per-part shaping rate).
* **Trusted fields are not model-settable.** `attested_by`, `calibrated`, `declared_total`
  for drafts, and `hook_mm` defaults are all out of the draft path's reach.
* **Provenance per line.** `source` prints unmarked; `inferred`/`added` print tagged, with
  an optional `why`, and the document's tally is derived from the same data the tags come
  from — the paragraph can no longer claim more than the lines show.
* **Two audiences.** `pattern.md` is the maker's document; the HTML dossier and the PDF's
  "Verification appendix" carry the engine's working.

## 3. Still open, on purpose

* **Real symbol chart** (task #23). The visuals are honestly labelled count charts; a
  stitch-symbol diagram is not written yet and the addendum is right that this is the
  weaker of the two gaps.
* **Chain-space and puff stitches** (task #22). The flower and cherry stay
  `manual` — described, not counted — because the source never defines the puff. They are
  reported as *not stitch-modelled* rather than promoted to verified with invented counts.
* **Shape simulation.** The growth bound catches a ruffle; it does not simulate the piece
  the way a 3D model would, and no claim is made that it does.

## 4. Evidence

`tests/test_threat_model.py` re-runs T1–T6 as regression tests (13 tests), plus
`test_the_pattern_document_carries_no_engine_debug`,
`test_every_added_line_is_tagged_in_both_formats`, `test_a_tip_down_piece_is_drawn_tip_up`
in `tests/test_renderers.py`, and the star fidelity assertions in `tests/test_star.py`.

```
53 passed          # .venv/Scripts/python.exe -m pytest -q
All checks passed! # ruff check src tests demo.py star_demo.py
```

Regenerated: `out/` (hat: tip-up cross-section, no debug lines in `pattern.md`) and
`out/star/` (sewing = 2 source lines + 8 `[ADDED]`, tally 47 source / 4 inferred /
10 added).

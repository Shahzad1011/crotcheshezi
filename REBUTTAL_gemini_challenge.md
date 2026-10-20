# Rebuttal — Gemini's challenge to the Croctech star output

Reviewed: the 137-line challenge (`6f795d7c-…txt`, Flaws 1.1–3.3 + roadmap Steps 1–4).
Method: every claim re-tested against the **live** tree — `src/croctech/*`, the regenerated
artifacts in `out/star/`, and the test suite. Repro commands at the bottom.

Headline: **6 of the 10 flaws do not exist in the current code** (they describe an earlier
revision, or a number that no artifact prints). **3 are true and were already logged as open
work.** **1 is true in its conclusion but not in its evidence** — and that one exposed a latent
default I have now closed. Two of its roadmap prescriptions would, if adopted as written,
re-introduce exactly the invention the maker rejected.

| Claim | Verdict against current code |
| --- | --- |
| 1.1 chart draws polygons/bars, not stitches or symbols | **TRUE** — already logged (task #23) |
| 1.2 no ply / twist / fibre physics | **TRUE as a renderer limit**; the fix it demands needs inputs the source never gives |
| 1.3 hallucinated cover on the PDF/HTML | **FIXED** — captioned "Concept illustration — not a render of this pattern" |
| 2.1 `sl st to join` force-appended to every round | **FALSE for the output; TRUE as a latent default — now closed** |
| 2.2 only 5 stitch ops in `_OP_EFFECTS` | **TRUE** — already logged (task #22) |
| 2.3 `manual` parts skipped, badge over-reads | **TRUE in conclusion — badge fixed**; coverage was already printed |
| 2.4 hooks never assigned per part | **FALSE / stale** |
| 2.5 24 of 30 base stitches abandoned, marked OK | **FALSE / stale** — this is the block-multiplicity bug already fixed |
| 3.1 sewing is loose text, no seam graph | **TRUE** — its "60 edge loops" figure is itself unverified |
| 3.2 no 3D stuffed volume (cites 4.34 cm / 3.85 cm) | **FALSE / stale** — no centimetre is emitted at all |
| 3.3 yarn ignores `quantity`, "under-reports by 400%" | **FALSE / stale** — multiplication is in, and the star prints no yarn figure |

## 2.1 — the one real win in the challenge

The claim as written is stale: in `out/star/pattern.md` the string `sl st to join` occurs
**exactly once**, on the Blush, whose source wording is *"Close the MR and sl st."* Every star
round and every point row set `join_sl=False`, so the continuous spiral was never given a seam.

But the challenge is right that the machinery **allowed** it, and I could not defend that:
`join_sl` defaulted to `True` in [src/croctech/schema.py:83](file:///D:/croctech/src/croctech/schema.py#L83).
Any row authored without thinking inherited a join — which is how a spiral amigurumi gains a
vertical seam. Now:

- `join_sl` defaults to **`False`**: a join is asserted, never inherited.
- The keychain fixture states its joins explicitly (its own wording ends every row with
  *"Complete the row by making a sl st at the top of the first sc."*), and still prints its 15
  source-authorized joins — nothing was lost, the injection just became impossible.
- Guarded by `test_a_join_is_asserted_never_inherited`.

## 2.4, 2.5, 3.2, 3.3 — asserted against numbers the code no longer produces

- **2.4 "never tells the maker which hook for which part."** `out/star/pattern.md` prints
  `### Star (make 2) [hook 3.5 mm]`, `### Flower (make 2) [hook 1.0 mm]`, `### Cherry (make 3)
  [hook 1.0 mm]`, `### Blush (make 2) [hook 1.0 mm]`, plus a "Hook assignment:" line in the PDF
  and HTML, plus `test_every_listed_hook_is_assigned` which fails if any listed hook is left
  unassigned. The 3×-larger-flower scenario it warns about cannot be produced from our output.
- **2.5 "Round 6 consumes 6 of 30 and the engine marks it OK."** That is the exact defect the
  `Block` rework closed. The five points are `Block(instances=5, consumes_base_stitches=6)` and
  the foundation exemption is scoped — [engine.py:65](file:///D:/croctech/src/croctech/engine.py#L65)
  is `if rnd.foundation and instance is None:`, so a point instance is audited against *its own
  6-stitch allocation*, not exempted. Output: `Star / Point x5: 5 x 6 = 30 base sts, foundation
  made 30 -> OK`, and each printed point carries its base range (`Point 5 — base sts 25-30`).
  Tampering is caught by `test_point_instances_must_exactly_exhaust_the_base`,
  `test_too_few_instances_is_also_an_error`, `test_each_point_must_work_its_whole_allocation`.
- **3.2 "the star is 4.34 cm wide, 3.85 cm high, paper-thin."** Neither number exists. No gauge
  was supplied, so `compute_dimensions` returns `None` and no centimetre appears anywhere in the
  star artifacts — `out/star/pattern.md` line 25 says plainly *"No gauge supplied, so no finished
  size is claimed"*, and the silhouette profile is omitted (`profile : omitted (no gauge
  supplied)`). The only `cm` in the file are the source's own *"70 cm of yarn"* and *"4 cm left
  open"*. Its "~2.0–2.5 cm" stuffed thickness is a guess; so was 4.34, and the framework's whole
  position is that a fabricated gauge fabricates a size.
- **3.3 "yarn under-reported by more than 400% — missing the 2nd star and all 5 points."** Two
  separate errors. First, the star emits **no** yarn figure (gauge `None` ⇒
  `compute_yarn_usage` returns `None`), so there is no 400% number to under-report. Second, the
  multiplication it says is missing is present —
  [gauge.py:93](file:///D:/croctech/src/croctech/gauge.py#L93),
  [gauge.py:98](file:///D:/croctech/src/croctech/gauge.py#L98):
  `sc = a.produced * quantity.get(a.component, 1)`, and every point instance is its own audit
  row. The keychain (quantity 1, real gauge) reports 252 sc / 132 red + 120 white and the colour
  breakdown is asserted to sum to the total. The star's counted stitches are **390 = 2 × 190
  (base 90 + 5 points × 20, both faces) + 2 × 5 (blush)** — the second star and all ten point
  instances *are* in there.

## 2.3 — right conclusion, wrong evidence; badge now scoped

The claim that the report "falsely claims 100% zero-defect verification" is stale: the verdict
was already split into **Arithmetic / Multiplicity / Coverage / Fidelity**, and the star has
printed *"Not stitch-modelled (50% of parts): Flower x2, Cherry x3"* in all three formats since
the last rework. What it caught that I had not: the HTML **header badge** still read a bare
`PASS - 0 stitch-math errors`, and a badge is the one line people read. That was a real defect.
Now, in `out/star/dossier.html`:

> <span style="color:#b45309">**PASS - 0 stitch-math errors · 50% of parts stitch-modelled**</span>

— amber, not green, whenever any part is unmodelled. `test_header_badge_is_scoped_to_arithmetic`
asserts both the scope text and the colour class.

## 1.1, 1.2, 2.2, 3.1 — true, already on the list, and one prescription to refuse

**1.1 / 2.2 (no symbol chart; only `sc dc inc dec sk`).** True, and recorded as tasks #23 and
#22 — no argument. But Step 2's prescription is wrong, and adopting it would be worse than
leaving the gap open. Dropping `ch`, `sl_st` and `puff` into `_OP_EFFECTS` does not verify the
flower: a petal is *"1 dc into the MR, ch 2, sl st into the MR"*, worked five times into the
**same** anchor. It deliberately does not satisfy `consumed == start_count` — nothing is consumed
from a previous row's stitch pool. Give those labels fake effects and the flower rounds will
"compile" and turn the badge **green while proving nothing**. The missing work is a different
conservation law (an anchor/ring model where the ring's loop pool is the ledger), plus the
source's own hole: *"puffy stitch"* is used but never defined — loop count and height unknown,
which is why it is in `undefined_terms` and printed under *Open questions*. That is task #22's
real scope, not an enum extension.

**1.2 (ply, twist, fibre physics).** True that nothing models yarn diameter or twist. The
request can't be met from this source, though: no gauge, no wraps-per-inch, no ply angle, no
finished weight. A spline renderer has to be *given* those, and any values chosen would be ours,
not the pattern's — then shown as a photoreal object the instructions never produced. Note also
what the challenge asserts as fact: *"The Pattern Requires: 3.5 mm + 3-ply for the Star; 1.0 mm +
2-ply for the Flowers, Cherries and Blush."* The source never pairs a ply with a part; it lists
two hooks and "3-ply and 2-ply". That is an inference stated as a requirement. The honest move —
which I've now made — is to surface it as an open question on the Star rather than pick a side:

> *Open question: Materials list 3-ply and 2-ply yarn but never says which ply belongs to which
> part. The hooks are assigned (3.5 mm for the star, 1.0 mm for the appliqué); the ply pairing is
> a guess, so it is left to you — 3-ply on 3.5 mm and 2-ply on 1.0 mm is the usual matching, not
> the source's instruction.*

Guarded by `test_unstated_ply_assignment_is_surfaced_not_guessed`, which also asserts no part's
own steps gained a ply the source didn't assign.

**3.1 (seam graph).** True: the sewing is 8 executable-sounding steps with counts per region
(*"one seam stitch per crochet stitch — 30 seam stitches across the base"*, *"at each of the 5
tips take two stitches into the same space"*) but **no** loop-k-to-loop-k map between the two
faces, and no seam diagram. Logged. Its own figure, though — *"an outer perimeter of 60 edge
loops (5 stepped edge rows up, 2 across the tip, 5 down)"* — is asserted, not derived, and it
skips the five concave notches between points, which is where a star's shape actually holds. Our
point rows are 6/5/4/3/2 with the skip alternating sides, so the border is not 5 loops per side.
Neither number is verified; the difference is that ours says which ones are.

**Step 3's cloth inflation (Laplace–Beltrami), Step 4's per-component gauges.** Both are real
architecture and both are blocked on the same missing input. There is no `Component.gauge` field
yet, and adding one today would populate every instance with `None` and change no printed number,
because the maker has given no swatch for either yarn. When a 10 × 10 cm swatch count arrives for
the 3.5 mm and the 1.0 mm work, per-part gauge is the right next schema change — and the
renderers already refuse to print a size until then.

## What actually ships today

`out/star/`: `pattern.md`, `pattern.pdf` (multi-page, full rows), `dossier.html`, `chart.png` —
31 audited rows, 0 arithmetic errors, `5 × 6 = 30` reconciled, 390 stitches counted, 50% of parts
modelled, no invented gauge, no invented notion, cover captioned as a concept.
**37 tests pass; ruff clean.** The chart is still a count profile — its own caption says
*"A count profile, not a stitch chart: it shows how many stitches a row leaves, not where they
sit"* — so 1.1's complaint is a named limitation, not a hidden one.

## Repro

```
.venv/Scripts/python.exe -m pytest -q                     # 37 passed
.venv/Scripts/python.exe star_demo.py                     # 0-error artifacts
grep -c "sl st to join" out/star/pattern.md               # 1  (the Blush, from the source)
grep -o 'class="warn">[^<]*' out/star/dossier.html        # PASS - 0 stitch-math errors · 50% ...
grep -n "which ply" out/star/pattern.md                   # line 33 and 149
grep -n "4.34\|3.85" out/star/pattern.md out/star/dossier.html   # nothing: no cm is emitted
grep -n "Arithmetic:" out/star/pattern.md                       # line 154, scoped to 31 rows
```

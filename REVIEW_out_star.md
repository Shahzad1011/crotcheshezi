# Review — `out/star`: a derivative design, not a reproduction

**Reviewed:** `out/star/pattern.md`, `chart.png`, `profile.png`, `dossier.html`, `pattern.pdf` (generated 2026‑10‑20 03:36).
**Against:** the attached star hanging-ornament pattern (Materials, Abbreviations, Star Base, Star Points, Sewing, Flowers, Cherry, Blush, Assembly, Hanging).
**Method:** read-only. Text extracted from the Markdown, HTML and generator code; no source file or artefact was modified.
**Verdict:** **not publishable.** The arithmetic badge is true for roughly a quarter of the object, and the document contains two defects that make the point section unexecutable: a point count that reads as five or six on a base that fits exactly five, and a "magic ring" instruction for a row that is worked along an edge. The cover image shows an object the instructions cannot produce.

---

## 1. What is actually in the folder

| File | Size | What it contains | What it is |
|---|---:|---|---|
| `pattern.md` | 3.4 KB | 10 star rows + 1 blush row; flowers, cherries, sewing, assembly, hanging as bullets | A text projection of `src/croctech/star.py` |
| `chart.png` | 46 KB | Bar chart of 10 row counts (6, 12, 18, 24, 30, 6, 5, 4, 3, 2) | A count histogram, **not** a stitch chart |
| `profile.png` | 99 KB | Five overlapping kite shapes around a circle | A plotting-code silhouette, not an IR projection |
| `dossier.html` | 1.38 MB | The same text, three embedded images, a green "PASS" stamp | Presentation layer |
| `pattern.pdf` | 1.57 MB | The same, with the AI cover image directly under the title, unlabeled | Presentation layer |

The instruction text is not model output at render time. It is the hand-coded fixture in `src/croctech/star.py`, including its notes. Whatever Qwen contributed is not attributable from the artefacts: there is no prompt, model, source hash or diff recorded anywhere. That absence is itself a finding (§7.8).

---

## 2. The blocker: the point section cannot be executed as written

`pattern.md` says:

```
Row 6: Magic ring / fresh start, 6 sc. ch 1, turn. [6 sc] (OK)
    > 6 sc along the base edge, ch 1, turn. Repeat this whole point 5 times.
    > Points 2-5: join yarn to the next unworked 6 base stitches and repeat.
```

Three separate failures in one block:

1. **The main instruction contradicts its own note.** "Magic ring / fresh start, 6 sc" tells the maker to start a new ring. The note says the six stitches are worked *along the base edge*. A maker following the main line makes a detached six-stitch disc; the star never gets its points. This is not a wording preference — it is the wrong action.
2. **The count is ambiguous and, on one reading, impossible.** The base is 30 stitches. Each point consumes 6. That is exactly five points. "Repeat this whole point 5 times" reads as five *more* after the first, i.e. six points, needing 36 base stitches. "Points 2–5" reads as four more, i.e. five total. The second reading is right; the first is what the instruction line says. A maker who follows it runs out of base stitches on the sixth point.
3. **The verification table shows the abandoned stitches and marks them OK.**

```
Component  Row  Start  Worked  Made  Claimed  Status
Star         6     30       6     6        6  OK
```

Thirty stitches available, six worked, twenty-four unaccounted for, status OK. The audit reports a start count it does not enforce: row 6 is flagged `foundation=True`, so the engine treats it as a fresh start and never checks that the 30 base stitches were consumed. This is the exact mechanism that lets a point float off the base while the badge stays green.

**Severity: blocker.** Any one of these would prevent publication. Together they mean the object in the folder is not the object in the source.

---

## 3. Fidelity scorecard

| # | Source | Output | Verdict |
|---:|---|---|---|
| 1 | Yarn 3-ply/2-ply; hooks 1 mm and 3.5 mm; scissors; glue; yarn needle; fibre filling | Same, **plus "safety eyes"** | Added item |
| 2 | Abbreviations: MR, sl knot, sc, inc, sk, ch, sl st, dc | None | **Omitted** |
| 3 | Gauge: not stated | 22 sts × 26 rows / 10 cm | **Invented** |
| 4 | Dimensions: not stated | 4.34 cm wide, 3.85 cm high | **Invented; contradicts the chart** |
| 5 | Star base R1–R5 (6, 12, 18, 24, 30) | Same counts, correct | Faithful, **but adds `sl st to join`** |
| 6 | Point 1, rows 1–5 (6, 5, 4, 3, 2; `sk` first stitch) | Same counts | Faithful counts, **row 1 mislabeled** |
| 7 | Points 2–5: join next 6, repeat 4 more (total 5) | "Repeat this whole point 5 times" + "Points 2–5" | **Ambiguous / contradictory** |
| 8 | Make another star | `Star ×2` + note | Faithful |
| 9 | Sewing: join, sew, stop near end, fill, sew closed | Same two sentences | **Paraphrased; not executable** |
| 10 | Flower: MR, ch 2, [dc, ch 2, sl st] ×5; make 2 | Same as four bullets; no counts, no petal numbering | **Unstructured** |
| 11 | Cherry: sl knot, ch 2, puff into 2nd ch, ch 1, tie; make 3 | Same; "puff" undefined | **Unstructured; undefined term** |
| 12 | Blush: MR, 5 sc, close, sl st; make 2 | Same as a row; `×2` | Faithful |
| 13 | Assembly: glue flowers, cherries, blush; glue eyes; yarn smile | Same | Faithful text; **eye type invented** |
| 14 | Hanging: sl knot, ch 20, cut, insert at top | Same | Faithful; attachment vague |
| 15 | No chart | Bar chart of row counts | **Invented; not a stitch chart** |
| 16 | No silhouette | Five overlapping kites, smooth tapers | **Invented; not derived from stitch positions** |
| 17 | No image | AI cover with leaves, flower centres, cherry stems | **Invented; contradicts the pattern** |
| 18 | No verification claim | "PASS — 0 stitch-math errors" | **Misleading** |
| 19 | 4 parts + 3 operations | "7 components" | **Category error** |
| 20 | Two hooks, no assignment | Lists both; assigns neither | **Omitted** |
| 21 | — | PDF subtitle: "hooks 3.5 mm" only | Inconsistent |
| 22 | No yarn quantity | 115 sc, 1.93 m | **Wrong by ~4×; internal mismatch** |

Summary: **6 faithful rows, 3 paraphrased, 2 omitted, 6 invented, 5 contradictory or misleading.** The document reads as a design proposal that borrowed the source's numbers, not as a transcription of the source.

---

## 4. "It did not add the stitch patterns"

The structured instruction layer stops after one point. Everything that makes the ornament is either prose or absent:

- **One point out of five.** Rows 6–10 are a single point. The other four exist only as a sentence. There are no base ranges (1–6, 7–12, … 25–30), no per-point numbering, and no way to tell which base stitches each point uses.
- **Flowers are a recipe fragment, not a pattern.** Four bullets that do state five petals, but with no per-petal numbering, no stitch counts, no repeat block and no hook. The source at least gives the exact petal action; the output preserves the words but not the structure that makes them followable.
- **Cherries are three bullets with an undefined stitch.** "Puff stitch" is never defined: how many loops, how tall, how many stitches into the chain. A maker who does not already know the stitch cannot execute it.
- **No abbreviations.** The source defines eight terms. The output uses `MR`, `sc`, `inc`, `sk`, `ch`, `sl st`, `dc` without a key.
- **No hook assignment.** The materials list 1.0 mm and 3.5 mm; no row says which. The 1.0 mm hook is never used in the document.
- **No stitch chart.** A stitch chart shows symbols at stitch positions with parent links. The bar chart shows ten totals; it cannot be crocheted from.
- **No gauge protocol.** A gauge number appears from nowhere; there is no swatch instruction or measurement method, and the one-line "reference estimate" caveat is not a protocol.

A pattern is not a list of totals. It is a sequence of actions on named stitches, with tools, tension and finishing. This document has the totals and the prose, and very little of the sequence.

---

## 5. "It added extra design which was not in the requirements"

### 5.1 In the text

- **"Safety eyes"** in Notions. The source says "Glue the eyes in the middle" and does not list eyes in the materials. Safety eyes are a different product: they need a washer and a hole, and they are a choking hazard if they work loose. This is an unrequested material and a safety-relevant change.
- **A gauge and two dimensions.** The source gives no gauge. The output supplies 22 sts × 26 rows / 10 cm, labels it a "reference estimate" in all three formats, then prints 4.34 cm and 3.85 cm as finished dimensions derived from it. The caveat is one clause; the numbers are set as specifications, and the dimension band implies a precision the input does not support.
- **`sl st to join` on every circular round after the first.** The source never instructs a join; round 1 explicitly says "no sl st". Joining changes the fabric, the seam and the height — and the output does not add the `ch 1` that would make the join workable. This is both an addition and an incomplete instruction.
- **A yarn quantity of 1.93 m.** The source gives none. The number is wrong by roughly a factor of four (§8), so it is not a harmless estimate.

### 5.2 In the image

The cover is `vibe_images/crochet-star-ornament_1792449030375_88f79278.png`, embedded unlabeled directly under the title in the PDF and in the HTML header. It shows:

- **green leaves** behind both flowers — the source has no leaves, and no green yarn;
- **yellow flower centres** — the source's flower is five `dc` petals worked into a magic ring, with no centre;
- **cherry stems and leaves** — the source's cherries are puff stitches tied off, with no stems;
- **glossy domed eyes** — not the glued eyes the source describes;
- **pale yellow yarn** — the text says "as desired", so the image quietly fixes a colour.

The image is the most visible part of the deliverable and the least faithful. A reader will believe the instructions produce that object. They do not.

### 5.3 In the charts

- **The bar chart** plots rows 1–10 on one axis: five increasing base rounds, then a cliff from 30 to 6, then 6, 5, 4, 3, 2. That cliff is the point attaching to the base, not the object shrinking. The title says "engine-verified", which is true of the counts and false of the reading.
- **The silhouette** draws five identical kites around a circle at 72° intervals, with smooth tapers. The point is actually a staircase: each row skips one stitch at the end, and because the work is turned, the skip alternates ends, so the point tapers in five visible steps. The drawing smooths those steps into a kite, anchors the base a row inside the disc, and chooses a tip length; none of that is in the pattern. The result is a plausible icon, not a projection of the stitches. Its title — "from verified counts" — claims a derivation that is not there: the body radius and point count come from the counts, but the taper, the base anchor, the overlap and the tip length are plotting choices.

### 5.4 In the structure

The dossier counts **7 components**: Star, Sewing, Flower, Cherry, Blush, Assembly, Hanging. Sewing, Assembly and Hanging are operations, not parts. Mixing them into the component list is why the header reads "7 components" for an object with four kinds of part, and why the coverage number is impossible to interpret.

---

## 6. "Sewing should be 100% natural"

### 6.1 What the document says

> Place the two stars together and sew around the edge, stopping near the end. Add fiber filling, then sew completely closed.

That is a summary, not a sewing instruction. It omits every decision a maker has to make:

| Required element | Present? |
|---|---|
| Needle and yarn (type, length, tail) | No |
| Which sides face out (right/wrong sides) | No |
| Seam stitch (whipstitch, mattress, ladder) | No |
| Stitch mapping (one seam stitch per crochet stitch) | No |
| How to align the five points | No |
| How to turn a sharp point without a hole | No |
| Opening size and where to leave it | No ("near the end") |
| How to stuff the points without distorting the seam | No |
| How to close the opening invisibly | No |
| How to secure and bury the tail | No |
| How to attach the hanging loop so it bears weight | No |
| A finish check (seam line, filling, points) | No |

A maker who has never sewn a stuffed star cannot execute this without inventing the missing steps. That is the opposite of "100% natural".

### 6.2 A natural sequence that fits the source

This is an editorial completion, not a source quotation. It assumes wrong sides together, which gives a neat visible ridge on a flat star; if you prefer a hidden seam, work right sides together and turn through the gap.

1. Thread a yarn needle with about 70 cm of the same yarn. Hold the two stars wrong sides together, point to point.
2. Bring the needle up between the layers at the base of the top point, so the starting knot is hidden inside.
3. Whipstitch the edges together, one seam stitch per crochet stitch: through the back loop of the front star and the front loop of the back star. Keep the tension light so the seam stays flat.
4. At each of the five tips, take two stitches into the same space so the point turns sharply instead of rounding off.
5. Work all the way around until about 4 cm is left. Fasten the yarn temporarily.
6. Stuff small pieces of fibre filling through the gap, pushing them into each point with the back of a hook or a chopstick. Fill until firm but not bulging; keep the seam line straight.
7. Close the gap with a ladder stitch: pick up one loop from each side alternately, three or four times, then pull gently and continue to the end.
8. Pull the yarn tight, pass the needle through the star and out the other side, and trim the tail so it disappears inside. Thread the ch-20 loop through the top point, sew it down with two stitches inside the seam, and bury the end.

The loop attachment is the one place this sequence goes beyond the source: the source says only "insert it onto the top of the star". Sewing it into the seam is a proposed clarification, not a requirement.

### 6.3 The image cannot evidence the sewing

The cover shows no seam at all. It is a smooth, moulded-looking star. For a pattern that asks the maker to sew two pieces together, the cover should show the seam, the point alignment and the finish — or it should not be there.

---

## 7. Why the approach produces this

The failure is not that the model is weak. It is that the system has no concept of **the source**.

### 7.1 The source is not in the system

`src/croctech/star.py` is a hand-typed fixture. The attachment was never ingested as data; the fixture was typed by hand. There is no object in the codebase that represents "the pattern the user gave us", no span references, no diff. The pipeline can check whether the fixture's arithmetic agrees with itself; it cannot check whether the fixture agrees with the source. That is why every fidelity question in this review had to be answered by reading the two documents side by side.

### 7.2 The schema forces invention

`Pattern.gauge` is required and `Gauge` has no "unknown" state. `Material.hook_mm` is a single required float. There is no per-component tool. So a document cannot say "the source does not give a gauge"; it must supply a number and nominate a primary hook. The AI path makes that concrete: if the model omits a gauge, `_draft_to_pattern` silently uses 30 sts / 36 rows. The source gives neither value. The invention is structural, not a model hallucination.

### 7.3 The escape hatch rewards prose

`Component.kind == "manual"` skips all checks. Flowers, cherries, sewing, assembly and hanging are manual, so they produce no audits. The badge is computed from `err == 0`, so a pattern can be 25% modelled and still print "PASS". The path of least resistance is to describe the hard parts, not to compile them.

### 7.4 Multiplicity is a note, not a structure

`RoundSpec` has no notion of a section that repeats. Five points become one block plus a sentence. The compiler could compute `30 / 6 = 5` and emit five blocks with base ranges 1–6 … 25–30; it does not, because the model has nowhere to put them. The ambiguity in §2 is the direct result.

### 7.5 Charts are plotting code, not projections

`render_flat` derives a body radius and a point count from counts, then invents a smooth taper, a radial layout and a tip length. Every one of those is a design decision made in a plotting function, not in the pattern. The title "from verified counts" borrows authority from the engine for geometry the engine never saw.

### 7.6 Images are decoration, not evidence

The cover is selected by a glob (`vibe_images/*star*.png`) and embedded unlabeled. Nothing checks it against the IR. It is an AI-generated concept image presented as the finished object.

### 7.7 "PASS" measures the wrong thing

`validate()` checks arithmetic. The badge says "0 stitch-math errors", which is true. A reader reads "PASS" as "this pattern is correct". Those are different claims. There is no coverage, fidelity, executability or physical check in the verdict.

### 7.8 No provenance

No record of the model, prompt, source hash, commit or diff. The artefacts cannot answer "what came from the source, what came from the model, what came from the fixture?" — which is the first question any review asks.

### 7.9 The mode error

This is the heart of it. The system is built as a **design generator**: the AI proposes, the engine decorates, the renderer fills the gaps. The task is a **transcription**: reproduce a specific pattern, add nothing. In design mode, invention is the product. In transcription mode, invention is the defect. One pipeline, one voice, one badge cannot serve both.

The document collapses three different kinds of statement into one voice:

| Layer | Example | Epistemic status |
|---|---|---|
| Source | "Sk the first stitch and make 5 sc" | Required |
| Editorial completion | "Whipstitch one seam stitch per crochet stitch" | Necessary, but an addition |
| Derived estimate | "22 sts × 26 rows / 10 cm → 4.34 cm" | Computed from an assumption |

A reader cannot tell which is which. That is why the document feels wrong even where the arithmetic is right.

---

## 8. The numbers, checked

| Quantity | Document | Reality | Error |
|---|---:|---:|---|
| Modelled stitches | 115 | ~456 in the object | 25% coverage |
| Stitches implied by its own instructions | — | 390 (star + blush) | 3.4× the model |
| Yarn | 1.93 m | 6.5 m (stars + blush), ~7.6 m (whole object) | ~4× low |
| Yarn internal consistency | 1.91 m by colour vs 1.93 m total | Should be equal | 2 cm drift from rounding |
| Widest dimension | 4.34 cm | 7.42 cm tip-to-tip (its own chart draws ~7.4) | 42% low |
| Height | 3.85 cm | 10 rows × 0.385 cm — a stack height, not the object's height | Not a valid measurement |
| Points | "5 times" / "Points 2–5" | 30 ÷ 6 = 5 | 5 or 6, undefined |
| Base stitches at R6 | Start 30, worked 6, OK | 24 abandoned | Silent |

The yarn figure is the most dangerous: a maker buying 2 m of yarn for a two-star ornament will run out after the first star.

---

## 9. A strict version of this pattern

This is the shape the compiler should produce, not a full rewrite. It shows that the ambiguity is avoidable.

```
Abbreviations: MR, sl knot, sc, inc, sk, ch, sl st, dc.

Star (make 2)
  Hook: source lists 1.0 mm and 3.5 mm; assignment not stated — confirm.
  R1  MR, 6 sc (no sl st)                         [6]
  R2  inc in each st                              [12]
  R3  (sc, inc) ×6                                [18]
  R4  (2 sc, inc) ×6                              [24]
  R5  (3 sc, inc) ×6                              [30]

  Point 1 — base sts 1–6
    P1.1  6 sc, ch 1, turn                        [6]
    P1.2  sk 1, 5 sc, ch 1, turn                  [5]
    P1.3  sk 1, 4 sc, ch 1, turn                  [4]
    P1.4  sk 1, 3 sc, ch 1, turn                  [3]
    P1.5  sk 1, 2 sc, fasten off                  [2]
  Point 2 — base sts 7–12   (join yarn; repeat P1.1–P1.5)
  Point 3 — base sts 13–18
  Point 4 — base sts 19–24
  Point 5 — base sts 25–30
```

The five blocks are not decoration. They are the only way to make the multiplicity checkable: 5 × 6 = 30, and the last point ends exactly at the last base stitch. The compiler can generate them; the renderer should not be allowed to collapse them into a note.

Flowers and cherries, structured but still faithful to the source:

```
Flower (make 2)
  MR, ch 2.
  Petals 1–5: dc into MR, ch 2, sl st into MR.
  Close MR, cut yarn.

Cherry (make 3)
  Sl knot, ch 2.
  Sk first ch, puff st into 2nd ch.
  Ch 1, tie tightly.
```

`puff st` still needs a definition or a library entry. That is an open question, not a licence to invent one.

---

## 10. Acceptance tests this artefact fails

| # | Test | Pass condition | Current |
|---:|---|---|---|
| 1 | Point multiplicity | 5 explicit blocks or ranges; 5 × 6 = 30 | **Fail** |
| 2 | Point attachment | No "magic ring" on an edge-worked row | **Fail** |
| 3 | Round closure | No join unless the source says so | **Fail** |
| 4 | Hook assignment | Every listed hook assigned to a part, or flagged | **Fail** |
| 5 | Abbreviations | All used terms defined | **Fail** |
| 6 | Materials fidelity | No material absent from the source | **Fail** (safety eyes) |
| 7 | Flower structure | 5 petals × 2 flowers, counts and repeat | **Fail** |
| 8 | Cherry structure | 3 cherries, puff defined | **Fail** |
| 9 | Sewing executable | All 12 elements in §6.1 present | **Fail** |
| 10 | Dimension consistency | Text and chart agree within 5% | **Fail** (4.34 vs 7.4) |
| 11 | Yarn quantity | Quantity applied; within ±10% of a weighed sample | **Fail** (~4× low) |
| 12 | Coverage | 100% of source stitches modelled before claiming verified | **Fail** (25%) |
| 13 | Image fidelity | Image is a render of the IR, or absent | **Fail** (unrelated AI image) |
| 14 | Provenance | Source hash, model, prompt, commit recorded | **Fail** (none) |

A single fail is enough to block publication. This artefact fails all fourteen.

---

## 11. Recommendation

1. **Relabel the artefact now.** "Concept / derivative design, not the attached pattern" on the PDF, HTML and Markdown. Do not ship it as the star pattern.
2. **Treat this as a mode error, not a prompt-tuning problem.** Add a source-locked mode: parse the source into the IR, attach a source span to every node, and render only what has a span. Any editorial completion goes in a separate, labelled block. A diff report lists added, removed, reworded and moved content, and blocks release on anything unexplained.
3. **Make "unknown" a valid state.** `gauge: Gauge | None`, per-component hook, `notions` with provenance. Render "not specified in the source" instead of inventing. Where usability needs a value, mark it "assumption — verify with a swatch".
4. **Model sections, not notes.** A `Section` with `repeat`, `base_range` and a per-instance render. The five points are the acceptance test.
5. **Model seams.** Boundary loops, seam type, stitch mapping, opening, closure, tail, loop attachment. Generate the sequence in §6.2, not a paraphrase.
6. **Charts from the IR.** A stitch-symbol chart with parent links. A silhouette only when coordinates come from stitch placement; otherwise omit it. Never a plotting heuristic that contradicts the text.
7. **No unlabeled AI images.** Render from the IR, or omit the image. If a concept image is useful, put it on a separate page labelled "concept — not the pattern".
8. **Replace the badge.** Three lines: arithmetic (0 errors), coverage (115/456 = 25%), fidelity (not checked). A green PASS over a quarter-modelled object is worse than no badge.
9. **Keep the arithmetic engine.** It did its job: every modelled round reconciles. The failure is above it — no source model, no fidelity metric, no seam model, no honest verdict.

The shortest path to "100% accurate, 100% real" is not a better generator. It is a **source-locked compiler with a diff**, and a document that separates what is required from what was assumed.

---

## Appendix A — Exact quotes

| Source | Output |
|---|---|
| "Make 6 sc into the MR (no sl st)." | "Magic ring / fresh start, 6 sc." (R1) |
| "6 sc, ch 1, turn your work." | "Magic ring / fresh start, 6 sc. ch 1, turn." (R6) |
| "Repeat the same star points pattern for 4 more times (total 5 points)." | "Repeat this whole point 5 times." + "Points 2-5: join yarn…" |
| "Join two stars together and sew them together, stopping near the end." | "Place the two stars together and sew around the edge, stopping near the end." |
| "Add filling and then sew completely." | "Add fiber filling, then sew completely closed." |
| "Make a MR and ch 2. Make 1 dc into the MR, ch 2, sl st into the MR. Repeat the pattern for 4 more times." | Four bullets; no counts, no petals numbered. |
| "Sk the first ch and make a puffy stitch into the second ch." | "Skip the first ch and work a puff stitch into the second ch." (puff undefined) |
| "Glue the eyes in the middle." | "Glue the eyes in the middle." + "safety eyes" in Notions |
| "Cut a small piece of black or brown yarn and glue it in the middle to look like a smile." | "Cut a short piece of black/brown yarn and glue it as a smile." |
| Materials list has no eyes | Notions include "safety eyes" |

## Appendix B — Rendering evidence

- `pattern.md` → `Star 6 30 6 6 6 OK`; `Star 7 6 6 5 5 OK`; total audits 11, errors 0.
- `dossier.html` → "Hanging Ornament · 7 components · hooks 3.5 mm, 1.0 mm"; "PASS - 0 stitch-math errors"; three embedded images.
- `chart.png` → title "Stitch count per row (engine-verified)"; bars 6, 12, 18, 24, 30, 6, 5, 4, 3, 2.
- `profile.png` → title "Flat silhouette: 5 points (from verified counts)"; tips at roughly ±3.6 cm; body radius 2.17 cm.
- `pattern.pdf` → cover image directly under the title with no caption; subtitle "hooks 3.5 mm" while Materials lists both hooks.
- Minor: the cover file has a `.png` name but is JPEG data, and the HTML embeds it as `image/png`; browsers sniff it, but the declared type is wrong.

## Appendix C — What "natural sewing" means as a test

A sewing section passes when a maker who has not seen the object can execute it without guessing, and the result passes this check:

- the seam reads as one continuous line, with no gaps and no visible knots;
- all five points meet tip to tip and keep their shape;
- the filling does not show through the seam;
- the star is firm, not bulging, and lies flat;
- the hanging loop bears a gentle pull without distorting the top point;
- the tail is buried, not cut at the surface.

The current two-sentence instruction meets none of these, because it specifies none of them.

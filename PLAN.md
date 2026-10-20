# Croctech — from stitch arithmetic to executable patterns

**Planning document. No source files were modified.**

Baseline measured before writing this plan: `.venv` Python 3.12.15, `pytest -q` → **7 passed in 8.81 s**, `croctech` imports from `src/`. Probes below were run read-only against the installed package.

---

## 0. Verdict

The current package is a competent **proofreader for one invariant**: the sum of stitches consumed in a round equals the previous round's total. That is worth having, and parts of it are well built.

It is not a pattern engine, and it cannot support the claim "100 % accurate, 100 % real". Three separate things are being promised as one:

| Property | Provable by software? | Mechanism | Current status |
|---|---|---|---|
| Stitch arithmetic is consistent | **Yes, 100 %** | closed-world IR + compiler that authors every count | Partial: 5 operations, scalar totals, two escape hatches |
| The pattern is executable and unambiguous | **Yes, 100 %** | a simulator that runs every instruction | Not implemented |
| The finished object matches the stated size | **No — statistical** | calibrated gauge + Monte Carlo + physical samples | One ±10 % band from a guessed gauge |
| The pattern is "real" (a human made it) | **Only by evidence** | maker test records, measurements, photos, hashes | Not implemented |

So the defensible product promise is not "100 %". It is:

> **Every published pattern passes a machine execution proof and carries a maker-test record. Dimensions and yarn are reported as calibrated intervals, never as single numbers.**

That claim survives a customer with a tape measure. "100 % real" does not.

The rest of this document justifies that verdict with reproductions, then proposes a different architecture: **patterns as programs** — AI chooses the object, a compiler decides every stitch, a simulator proves a maker could execute it, and a ledger records who did.

---

## 1. What the current code gets right

Keep these; they are the seed of the right design.

- **Counts are re-derived, never trusted** (`engine.author_totals`). The author — human or model — cannot smuggle a total.
- **Refusal to publish** on validation failure (`pipeline.generate` raises `CrochetValidationError`).
- **Intent-only AI contract**, at least in the docstring.
- **Pydantic schema + pint units** — a good foundation for a typed IR.
- **A test that proves the checker actually checks** (`test_engine_catches_wrong_total`): tampering with a declared total fails. Many projects never write this test.
- **One source, several artefacts** (Markdown, PNG charts, self-contained HTML, PDF).
- **A tolerance band** in the text renderer — the beginning of honesty about physical variance.

---

## 2. Where it breaks — reproduced findings

Each finding below was executed against the current package. The commands were read-only; no files were written.

### 2.1 The checked language has five operations

`schema.py::_OP_EFFECTS` = `sc, dc, inc, dec, sk`. There is no `ch`, no `sl st`, no `hdc`/`tr`, no "3 sc in one stitch" (1 → 3), no front/back-loop-only, no chain space, no turning chain, no working into the side of a row. The attached star's flowers, cherries and hanging cord are therefore prose, not patterns.

This is not a cosmetic gap. The most common shaping idioms in amigurumi are exactly the ones missing: 3-in-one for petals and bobbles, BLO for ridges and soles, chain spaces for lace, and "sc in the side of the row" for flat pieces.

### 2.2 Two escape hatches make "0 errors" meaningless

**(a) `Component.kind == "manual"` skips every check.**

```python
p = Pattern(
    name="Minimal", item_type="hat",
    material=Material(yarn="acrylic", hook_mm=2.5),
    gauge=Gauge(stitches_per_10cm=30, rows_per_10cm=36),
    components=[
        Component(name="Crown", kind="verified", rounds=[
            RoundSpec(index=1, foundation=True,
                      cycle=[StitchOp(kind="sc", count=6)], declared_total=6)
        ]),
        Component(name="Body", kind="manual",
                  steps=["Work the rest of the hat however you like."]),
    ],
)
validate(p)      # -> []
audit(p)         # -> [('Crown', 1)]   one audit for the whole object
```

The HTML renderer then prints **"PASS — 0 stitch-math errors"** for a six-stitch crown with no body. The badge is computed from `err == 0` over the audits, and a manual component produces no audits at all.

**(b) `RoundSpec.foundation == True` skips the "consume the previous round" check — and it is reachable from AI output.**

```python
p = build_pattern()
p.rounds[5].foundation = True                 # mid-piece "fresh start"
for i in range(5, len(p.rounds)):
    p.rounds[i].cycle = [StitchOp(kind="sc", count=20)]
    p.rounds[i].repeats = 1
author_totals(p)
validate(p)                                   # -> []
# audit: R5 produced 18, R6 start_count 18 but treated as fresh, produced 20
```

A pattern can jump from 18 to 20 stitches mid-piece with zero errors. The audit even records `start_count=18` for a round whose consumption it then ignores — it knows the number and does not use it.

`_draft_to_pattern` copies `foundation` straight from the model's JSON, so a model can switch off the only structural check it is subject to.

### 2.3 Geometry is never checked

Starting from 18 stitches, eighteen `inc` operations produce 36 stitches in one round at the same radius:

```python
RoundSpec(index=6, cycle=[StitchOp(kind="inc", count=18)], declared_total=36)
validate(...)      # -> []
produced           # [6, 9, 12, 15, 18, 36]
dims               # 1.67 cm tall, 3.82 cm wide
```

In fabric this is a ruffle, not a disc. Every real designer knows the rule; the engine has no concept of circumference, so it cannot know it. This is the difference between *accounting* and *engineering*.

### 2.4 `quantity` is ignored in the stitch totals and the yarn estimate

`gauge.compute_yarn_usage` iterates `pattern.verified_rounds` without multiplying by `Component.quantity`. The star renders "make 2" and reports **115 stitches** — the contents of its own model — where applying `quantity` gives **230**, and the physical object is closer to **456** (Appendix B). Yarn metres and grams are under-reported by the same factor. The flagship multi-part example is the one that exposes it.

### 2.5 The renderer does not render the pattern it was given

From `out/pattern.md` and a direct `render_text` call on the star:

| Output | Problem |
|---|---|
| `Row 6: Work (18x) x1. sl st to join.` | The source never instructs a join and round 1 explicitly says "(no sl st)". `join_sl` defaults to `True`, so the renderer **adds one to every later round**. `start_ch` is dead code — it says "join" without the `ch 1` that would make joining correct. |
| `Work (6v) x1` | Internal IR notation leaked to the customer. |
| `Row 2` … `Row 15` for circular rounds | Wrong terminology; amigurumi instructions say "Round". |
| `Row 6: Magic ring / fresh start, 6 sc` on star points | The point row is worked along an edge, not into a magic ring. Factually wrong instruction, generated from the `foundation` flag. |
| `[n sc]` on every round | Wrong unit for dc/hdc/tr rounds. |
| `_OP_WORD["inc"] * count` | Concatenates prose (`"2 sc in next st2 sc in next st"`) whenever an increase run has `count > 1`. |

A pattern document that silently changes the construction is not "100 % real", regardless of how clean its arithmetic is.

### 2.6 Dimensions and yarn are a single-gauge axisymmetric guess

- **Height = number of rows / row gauge.** Stitch height is assumed equal for sc and dc; turning rows, folded brims, stuffing and appendages are invisible. The keychain's brim is folded — prose only. The star's five flat point rows are stacked like rings, giving 4.23 cm for an object whose base alone is 4.34 cm across.
- **One gauge for the whole object.** The star lists 1.0 mm and 3.5 mm hooks; the model carries one gauge, and the small parts worked at the finer hook are not measured at all.
- **`Gauge.calibrated` is never set by a calibration workflow.** It can only be flipped by hand in a fixture or by the model's own JSON (`_draft_to_pattern` reads it), so the "(reference estimate)" caveat is permanent in practice.
- **Yarn per sc = `2·width + 2·height`**, uncalibrated, with no chain, no tails, no joins, no crimp, no yarn density unless someone typed `meters_per_gram` by hand.
- **`render_pattern` picks the component with the most rounds** and reports its dimensions as the whole object's. Multi-part objects get the dimensions of one part.

### 2.7 The AI path cannot express the flagship example

`_draft_to_pattern` builds one legacy `rounds` list → exactly one component, one gauge, no quantities, no appliqué, no sewing, no assembly. **The star, as specified, cannot be produced by the AI path**: there is no representation for its five parts. The Gemini call sets `response_mime_type` but no schema, so "JSON" is a request, not a constraint; there is no vocabulary enum, no eval set, no prompt versioning, and the repair loop re-asks up to three times with string errors and no guarantee of progress.

### 2.8 Data integrity and process

- **Duplicate round index silently corrupts totals.** Two rounds with `index=1` in one component → `author_totals` writes the last produced value into both (observed: `9, 9, 12`).
- **`Pattern.rounds` is a construction-time convenience.** Reassigning or appending to it after construction has no effect, because `components` was normalized at validation time (mutating an existing `RoundSpec` still works, since the objects are shared). A test that appends to `.rounds` is testing a detached list.
- **No git repository, no README, no console script, no CI.** Tests: 7 cases in one file. The reference package's test files survive only as `.pyc`.
- **`_gemini_reference/README.md` is a liability.** It claims "100 % mathematical accuracy, physical feasibility, 0 % hallucinations", then quotes *49.8 mm*, *25.3 mm*, *1.57 m*, *0.49 g* — all arithmetic on a guessed gauge, presented as measurements. Anyone technical will read those as fabricated precision, and it will contaminate the credibility of the parts that are real.

---

## 3. The approach I would take instead

**One sentence:** AI chooses *what the object is*; a compiler decides *every stitch*; a simulator proves a maker *could execute it*; a ledger records *who actually did*.

### 3.1 Target architecture

```
brief / reference image
        │
        ▼
  DesignSpec  (LLM: silhouette, colours, style, library parts — no counts)
        │
        ▼
  Compiler (inverse design)
  target shape + calibrated stitch metrics ──► round schedule + per-stitch allocation
        │
        ▼
  Stitch-graph IR  ◄──────────────►  Notation (parse / print, US/UK, round-trip)
        │
   ┌────┼─────────────┬───────────────┬────────────────┐
   ▼    ▼             ▼               ▼                ▼
Simulator         Physics         Geometry         Evidence
(execute,         (calibrate,     (3D preview,     (hashes, maker
 trace, loops)     intervals)      charts)          tests, verdict)
   └────┴─────────────┴───────────────┴────────────────┘
        │
        ▼
  Publish: text · stitch chart · HTML · PDF · JSON
```

The key inversion: **the compiler generates counts from geometry**, instead of a model proposing counts that a checker later accepts or rejects.

### 3.2 IR: a typed stitch graph, not a list of totals

A crochet fabric is a graph of loops. Model it as one.

```python
class Stitch:
    id: StitchId
    kind: StitchKind            # fabric stitches only: sc, hdc, dc, tr, ch, slst, puff, bobble …
    loop_mode: LoopMode         # BOTH | FRONT | BACK | POST_FRONT | POST_BACK | CHAIN_SPACE
    parents: tuple[StitchId, …] # 0 for foundation ch, 1 for sc, 2 for a decrease, n for a cluster
    round: RoundId
    slot: float                 # 0..1 position within the round (allocation + chart layout)
    color: ColorId

class Round:
    mode: Literal["spiral", "joined", "flat"]
    turning: TurningSpec | None # chain count, whether the chain counts as a stitch
    sequence: tuple[StitchId, …]
    target_count: int           # authored by the compiler; the model has no field for it
```

Note what is **absent**: `inc`, `dec`, `shell`, `picot`. They are not fabric — they are notation macros over edges. An increase is two stitches sharing one parent; a decrease is one stitch with two parents; a shell is five `dc` with one parent; a picot is chain stitches plus a slip stitch. Modelling them as operations (as `_OP_EFFECTS` does) is precisely why the current engine can only count, not execute: it models the *words*, not the *fabric*.

Invariants, each a test:

| ID | Invariant | What it catches today |
|---|---|---|
| I1 | Parent capacity: a normal stitch consumes one loop-pair once; an increase consumes it twice; BLO/FLO consumes one loop and leaves the other free and tracked | "work into a stitch that does not exist", double-use of a front loop |
| I2 | Every stitch has the parents it declares; every parent is fully consumed or explicitly recorded as unworked | silent skipped stitches, orphan increases |
| I3 | Round closure matches the declared mode (spiral / joined / flat + turning chain) | joins injected into spirals |
| I4 | Colour segments are contiguous; every change has a join or carry | colour changes that teleport |
| I5 | `n_i · w_min ≤ C_{i-1} ≤ n_i · w_max` (fabric can absorb the stitches) | 18 → 36 in one round |
| I6 | Every component is closed or ends with a declared opening; seams connect equal-length boundaries within tolerance | unsewable parts |
| I7 | Yarn path is connected; mass = Σ path length / density | under-reported yarn |
| I8 | Total = Σ per-stitch production, not a separate number | the scalar total drifting from the graph |

The graph also makes **round-trip** possible: `parse(print(ir)) == ir`. That is a strong, cheap property test, and it forces the notation layer to stop leaking internal structure.

### 3.3 Compiler: inverse design and allocation

For a target silhouette, the count schedule is *computed*, not guessed:

```
n_i  = round(perimeter(shape, height_i) / stitch_width)
Δ_i  = n_i − n_{i−1}
```

For a circle this reproduces the classic rule that every designer memorises — six increases per sc round — from geometry rather than folklore: `Δn = 2π·Δr / w`, and with `Δr ≈ h ≈ w`, `Δn ≈ 2π ≈ 6.3`. That is a good sanity check that the model is physical.

Increases are then **allocated to concrete parent stitches**, not expressed as "repeat 6 times":

- maximise the minimum arc distance between increases (so the circle stays round and the seam does not spiral visibly) — CP-SAT, or a closed-form Bresenham allocator for the common case;
- respect pattern multiples (a shell repeat of 5+1, a colour chart that must align with the round start);
- keep the seam at the back and report its drift per round;
- emit concrete per-stitch instructions, then **compress to the most readable equivalent notation** with a cost function ("18 sc" beats "(18x) ×1").

This turns the model's numeric freedom into zero: it cannot propose 7 increases where geometry requires 6, because it never proposes counts.

**Deterministic repair replaces most LLM repair.** If a round is off by one, rebalance; if a colour block does not divide, pad with a designed increase; if a shape is infeasible, change the shape or the gauge, not the arithmetic. Only *design* problems go back to the model.

### 3.4 Simulator: the virtual maker

A hook state machine that executes the IR:

- loops on the hook, working yarn, current stitch, position (round, slot), available legs;
- preconditions per instruction (enough parents, correct leg free, chain space exists, colour available);
- `turn`, `join`, `fasten off`, `carry yarn` as first-class events;
- outputs: a step trace (hashable, for the evidence record), the final boundary loop set (needed for sewing and for appliqué placement), and a real stitch chart (symbols on a grid with parent links) instead of a polar bar chart.

"Executable" then becomes a property you can test on every pattern, not a hope.

### 3.5 Physics: calibration and intervals

Replace the guessed gauge with a measured one.

**Swatch protocol** (per yarn lot, hook, maker): work 20 sc × 20 rows, measure the centre 10 cm in both directions, weigh before/after. From that, fit per-stitch width `w`, height `h`, yarn length `l`, and fabric thickness `t`. The current heuristic `2w + 2h` becomes `l = k·(2h + 2w)` with `k` fitted from the weighed swatch — a one-parameter calibration that removes most of the systematic error.

**Uncertainty:** `w`, `h`, tension and yarn lot each get a distribution; 10 000 Monte Carlo draws give a dimension interval and a yarn-mass interval. Report p5–p95 and the dominant contributor ("gauge contributes 78 % of the spread"), not a fake two-decimal number.

**Feasibility** (invariant I5): working `n` stitches into a boundary of length `C` requires the fabric to absorb `n·w`; outside the compressibility band the round ruffles or cups. This one inequality catches the majority of AI shaping errors that pass today.

**Yarn:** sum the actual path length from the simulator, per colour, plus tails and joins; convert with the measured density. No more `2w + 2h` guess.

### 3.6 Evidence: what "100 % real" means operationally

Every pattern gets a `verification.json`:

```json
{
  "pattern_id": "sha256:…",
  "engine": {"version": "0.3.0", "commit": "…", "ir_schema": "2.1"},
  "checks": {"counts": "pass", "executable": "pass", "geometry": "pass",
             "coverage": 1.0, "trace_hash": "sha256:…"},
  "gauge": {"yarn": "…", "lot": "…", "hook_mm": 2.5,
            "sts_10cm": 30.0, "rows_10cm": 36.0, "method": "swatch", "by": "maker_07"},
  "physical_tests": [
    {"maker": "maker_07", "date": "2026-11-02",
     "measured": {"diameter_cm": 2.1, "height_cm": 4.3},
     "photos_sha256": ["…"], "pass": true}
  ],
  "verdict": "maker_verified",
  "artifacts": {"pdf": "sha256:…", "chart": "sha256:…"}
}
```

Levels: `machine_verified` → `measured` (calibrated gauge, no physical sample) → `maker_verified` (≥ 3 independent makers, dimensions within tolerance, photos). The PDF footer prints the pattern id, the level and a QR code to the record. **This is the only way "100 % real" becomes auditable rather than promotional.**

For toys, add a safety block: safety eyes vs embroidered eyes, fibre filling, small parts, age grading (ASTM F963 / EN 71). A plush pattern sold without it is not a finished product.

### 3.7 AI: a spec compiler, not a pattern author

| The model does | The model never does |
|---|---|
| Interpret the brief and reference image | Emit stitch counts |
| Choose silhouette, construction idiom, colours, style | Set `foundation`, `join_sl`, `flat`, `repeats` |
| Select embellishments from a verified component library | Write free-text steps that bypass checking |
| Write name, description, tips, marketing copy | Decide whether validation applies |

The `DesignSpec` schema has **no numeric field that determines a count** — that is the structural fix for the leaky contract. Constrained decoding (`response_schema` / `instructor` / `outlines`), a versioned prompt, and a recorded response per generation.

**Embellishments become library components.** A flower is a verified IR fragment (MR, ch 2, 5 × [dc, ch 2, sl st]), not a paragraph. If something genuinely cannot be modelled yet, it is published in an explicit `unverified` block and excluded from the coverage number — never silently counted as verified.

**Evals** (missing entirely today): 50 briefs × 3 seeds; metrics for schema validity, compile rate, simulator success, human "makeable" rating, dimension error, and similarity to the training corpus (to avoid reproducing copyrighted patterns). Prompt/model changes ship only if the eval set does not regress.

---

## 4. What happens to the current code

| Module | Decision | Notes |
|---|---|---|
| `schema.py` | **Replace** with `ir/` | Keep Pydantic; add graph nodes, stitch kinds, invariants. Keep a compatibility shim for the existing 7 tests. |
| `engine.py` | **Rewrite** as `compiler/` + `sim/` | `audit()` becomes a projection of the simulator trace; `validate()` composes I1–I8. |
| `ai.py` | **Rewrite** as `ai/` | Spec-only schema, constrained decoding, typed repair, evals, provider adapters. |
| `gauge.py` | **Rewrite** as `physics/` | Calibration, Monte Carlo, feasibility, yarn from path length. `pint` stays. |
| `chart.py` | **Rewrite** | Charts from the simulator (symbol grid, row map), not from totals. Keep matplotlib for raster; add SVG for print. |
| `render_text.py`, `render_html.py`, `render_pdf.py` | **Rewrite the projection layer** | Render the IR faithfully; no injected joins; Round vs Row; US/UK; notation optimiser. Keep the self-contained HTML idea. |
| `pipeline.py` | **Keep the shape** | Draft → compile → simulate → measure → publish; refusal gate stays. |
| `example.py`, `star.py` | **Convert to IR fixtures** | They are the first two corpus entries; the star is the acceptance test for coverage. |
| `tests/` | **Expand** | See §6. |
| `_gemini_reference/` | **Archive, annotate** | Replace its claims with a pointer to `ACCURACY.md`. Do not ship it. |

Compatibility: keep `croctech.audit` / `croctech.validate` as a facade so the existing tests keep running during the migration. The golden fixture is valuable evidence; do not delete it.

---

## 5. Phased plan

Estimates are for one experienced Python engineer; a second engineer roughly halves the calendar time for M1–M3.

| Phase | Weeks | Deliverable | Exit gate (measurable) |
|---|---|---|---|
| **M0 — Truth reset** | 1 | `ACCURACY.md` (claims + coverage definition), git repo, README, CI, 20-pattern corpus skeleton | All user-facing artefacts state the three guarantees; forbidden-phrase lint for "100 %" without qualification passes |
| **M1 — IR + notation** | 2–4 | Stitch graph, 30+ stitch kinds, parser/printer, US/UK, JSON Schema, hashing | ≥ 95 % of stitches in a 100-pattern corpus parsed with **zero silent drops**; round-trip property holds on 100 % |
| **M2 — Compiler + simulator** | 5–7 | Inverse-design scheduler, CP-SAT allocator, hook state machine, trace | All 20 corpus patterns compile and execute; both escape hatches removed; mutation recall 100 % (see §6) |
| **M3 — Faithful publishing** | 8–9 | Notation optimiser, text/HTML/PDF from the IR, real stitch chart, US/UK switch, coverage badge | Golden text for 20 patterns, byte-stable; star renders without injected joins; 0 undeclared deviations from source |
| **M4 — Physics v1** | 10–12 | Swatch calibration, Monte Carlo intervals, feasibility check, yarn from path length | 10 patterns × 3 makers: ≥ 9/10 within ±7 % on diameter and height; yarn mass within ±10 % |
| **M5 — AI spec compiler** | 13–16 | `DesignSpec` schema, inverse design, typed repair, library components, eval harness | 50 briefs: 100 % schema-valid, ≥ 95 % compile, ≥ 85 % rated ≥ 4/5 "makeable", 0 model-authored counts |
| **M6 — Evidence + beta** | 17–20 | Ledger, QR, verification levels, CLI, docs, site/API | Every artefact hash-reproducible; 10 patterns at `maker_verified`; public accuracy report |

Total: ~20 weeks to a defensible beta, ~10–12 with two engineers plus a crochet tester. Physical testing adds calendar time, not engineer time: every pattern needs a make-and-measure round trip.

### Why not the alternatives

| Option | Cost | Outcome |
|---|---|---|
| **A. Harden the count checker** (fix the two bypasses, add tests, polish renderers) | 2–3 weeks | Honest but commodity. Any competitor can reproduce it; it still cannot say anything about size, yarn or executability. |
| **B. IR + compiler + simulator + evidence** (this plan) | ~20 weeks | Defensible. The moat is the corpus, the simulator and the physical test records — none of which an LLM can fake. |
| **C. Full 3D cloth/yarn simulation** | 18+ months, research-grade | Wrong first bet. Stitch-mesh research exists (Guo et al., *Representing Crochet with Stitch Meshes*, 2020; Edelstein et al., *Computational Design of Amigurumi Crochet Patterns*, 2022); borrow the representation, not the research timeline. |

Recommendation: **B**, with A's fixes as the first two days of M2.

---

## 6. Test and eval strategy

What exists today proves one thing well: a tampered total is caught. That is necessary, not sufficient.

| Layer | Test | Target |
|---|---|---|
| Notation | Round-trip `parse(print(ir)) == ir`; fuzz the parser; unknown token is a hard error with location | 100 % on corpus; 0 silent drops |
| IR | Property tests: I1–I8 hold for every generated pattern | 100 % |
| Compiler | For random shapes and gauges: conservation, allocation completeness, even spacing bounds | 100 % |
| Validator quality | **Mutation testing**: seed 1 000 defects (count off by one, over-consumption, duplicate work, wrong leg, missing chain, colour break, ruffle geometry, unsewable seam) | Recall 100 %, false positives 0 on the clean set |
| Simulator | Every published pattern executes; trace hash stable across runs and platforms | 100 % |
| Rendering | Golden text/HTML; no injected instructions; terminology lint (Round vs Row) | 100 % |
| Physics | 10 patterns × 3 makers, measured | ≥ 90 % within ±7 %; yarn ±10 % |
| AI | 50 briefs × 3 seeds; human review; corpus similarity | See M5 |
| Claims | Docs lint forbidding unqualified "100 %" in user-facing output | 0 violations |

The mutation test is the one that matters most: it measures the **detector**, not the patterns. A checker that passes everything is indistinguishable from a checker that works, until you inject errors on purpose.

---

## 7. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Physical variance defeats "exact" dimensions | Certain | Intervals, calibration, maker tests; never quote a single number |
| Yarn lot / dye lot variance | High | Record lot and density in the gauge record; report a band |
| Over-claiming in marketing or docs | High (already happening) | `ACCURACY.md` as the contract; docs lint; archive the old README |
| LLM drift after model updates | Medium | Pin models, record prompts/responses, eval gate before upgrade |
| Corpus licensing | Medium | Own patterns + public domain; no scraping of Ravelry or paid patterns |
| Scope creep into garments (grading, ease, drape) | High | Explicitly out of scope for v1; separate math, separate phase |
| Toy safety / liability | Medium | Safety block, age grading, legal review before selling plush patterns |
| Charts and PDFs looking amateurish | Medium | Design pass at M3; vector charts; typography; one template, well typeset |

---

## 8. Definition of done

A pattern is **done** when, from a single hash, the system can regenerate:

1. an IR in which 100 % of stitches are represented (coverage = 1.0, printed on every artefact);
2. a simulator trace proving every instruction is executable;
3. a dimension interval and a yarn interval from a calibrated gauge;
4. human-readable text, a stitch chart, an HTML dossier and a PDF that say exactly what the IR says;
5. a verification record with at least three maker tests, measurements and photos;
6. the same bytes, on a rebuild.

Until (6) holds, "100 %" is a slogan. After it holds, it is a specification.

---

## 9. The next ten working days (still no code changes)

1. **Write `docs/ACCURACY.md`** — the three guarantees, the coverage metric, the forbidden claims. One day. This is the contract every later decision is measured against.
2. **Build a 20-pattern corpus** with expected counts, construction style, and stitch vocabulary used. Two days. Include the star and the keychain as entries 1 and 2.
3. **Paper-prototype the star in IR v2** — two stars, five points each, two flowers, three cherries, blush, hanging cord. One day. The output is a list of missing stitch kinds and structural features; it is the real requirements document.
4. **Run the falsifying experiment**: crochet one star from the source text and one from the current generated output; measure height, count stitches per round, photograph the seam. Prediction: the generated one has a visible join and a different height because of the injected `sl st to join`. If the prediction fails, finding 2.5 is wrong and the plan should be revised.
5. **Prototype the allocator** on the keychain (even spacing, no new dependencies). Two days. If a closed-form allocator handles 90 % of rounds, CP-SAT stays optional.
6. **Decide PDF stack**: WeasyPrint (HTML/CSS typography) vs ReportLab (no system deps). One afternoon; the answer is usually WeasyPrint for print quality, ReportLab for portability.
7. **Write three ADRs**: IR and invariants; compiler vs checker; evidence levels.

Deliverable at day 10: a corpus, a coverage report for the star, a measured comparison of source vs generated, and three ADRs. No production code yet — and a much sharper definition of what "accurate" will mean.

---

## 10. What would change my mind

I would abandon parts of this plan if:

- **Parser coverage stalls below 80 %** on a 100-pattern corpus after the IR work. That would mean the closed-world language is too narrow; the fallback is a hybrid with explicit, labelled `unverified` blocks — and a permanently lower coverage badge, not a quiet bypass.
- **Physical error stays above 15 %** after calibration. Then the dimension feature should be demoted to "reference gauge only", and the product should sell verification, not fit.
- **Makers cannot follow the simulator's output without asking questions.** Then the notation layer, not the engine, is the problem — and the next milestone is a readability study, not more code.
- **A closed-form allocator plus a 200-pattern corpus gets 95 % of the value** of the full compiler. Then skip CP-SAT and ship sooner.

---

## Appendix A — IR sketch

```python
class Stitch:
    id: StitchId
    kind: StitchKind
    loop_mode: LoopMode
    parents: tuple[StitchId, ...]
    round: RoundId
    slot: float
    color: ColorId

class Round:
    id: RoundId
    component: ComponentId
    mode: Literal["spiral", "joined", "flat"]
    turning: TurningSpec | None
    sequence: tuple[StitchId, ...]
    target_count: int          # compiler-authored

class Component:
    id: ComponentId
    name: str
    quantity: int
    gauge: GaugeId             # per component, not per pattern
    stitches: dict[StitchId, Stitch]
    rounds: tuple[Round, ...]
    closure: Literal["closed", "open", "flat"]
    boundary: tuple[StitchId, ...]

class Pattern:
    id: PatternId              # hash of the canonical IR
    components: tuple[Component, ...]
    assemblies: tuple[Seam, ...]
    evidence: EvidenceRecord
```

Compiler loop:

```python
for i, h in enumerate(height_profile):
    n = round(perimeter(shape, h) / metrics.width(kind))
    delta = n - previous_count
    parents = previous_round.boundary
    alloc = allocate(parents, delta, constraints=pattern_multiples, seam_at="back")
    emit_round(alloc)
```

---

## Appendix B — Coverage of the attached star, today

Approximate stitch counts from the source pattern, and what the current engine actually models.

| Part | Source stitches (approx.) | Modelled today | Note |
|---|---|---|---|
| Star base (2×) | 2 × (6+12+18+24+30) = 180 | 90 | `quantity=2` not applied |
| Star points (2 × 5) | 2 × 5 × (6+5+4+3+2) = 200 | 20 | one point modelled once |
| Blush (2×) | 10 | 5 | `quantity=2` not applied |
| Flowers (2×) | ~34 (5 petals × dc + ch2 + sl st) | 0 | prose |
| Cherries (3×) | ~12 (ch 2 + puff + ch 1) | 0 | prose |
| Hanging cord | 20 ch | 0 | prose |
| **Total** | **≈ 456** | **115** | **≈ 25 % of the object** |

The audit reports "115 stitches, 0 errors". Both numbers are true; together they are misleading. That is precisely the gap between arithmetic and reality, and it is why the coverage metric belongs on every page.

---

## Appendix C — Why the six-increases rule is a good test of the model

For a flat spiral circle, a designer's rule of thumb is six increases per sc round. It is derivable: each round adds height `h` to the radius; the circumference grows by `2πh`; each increase adds one stitch of width `w`; so the required increase count is `2πh/w`. With `h ≈ w` for sc, that is ≈ 6.3.

If a compiler reproduces that number from measured `w` and `h`, it is modelling fabric. If it has the number hardcoded, it is modelling folklore. The same derivation gives the right counts for hdc and dc (taller stitches, more increases per round) and for cones and spheres (varying `Δr` per round) — which is exactly the class of pattern the current engine gets wrong.

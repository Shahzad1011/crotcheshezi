"""The star hanging ornament, encoded with its provenance visible per line.

Three kinds of text live here and they are never blended:

* **source** -- the author's own wording, quoted verbatim (`origin="source"`).
* **inferred** -- the author's wording plus a gap the framework filled, such as
  which hook goes with which part (`origin="inferred"`).
* **added** -- technique the author did not write. Sewing is the big one: the
  source says two sentences, and a two-sentence sewing section cannot be sewn
  from, so the seam is expanded here and stamped as an addition.

The five points are modelled as a `Block` with five instances, not as one block
plus a sentence, so the engine can prove 5 x 6 = 30 and that the last point ends
on the last base stitch.

No gauge is supplied for this item, so no finished size or yarn weight is
claimed.
"""

from __future__ import annotations

from .schema import Block, Component, Material, Pattern, RoundSpec, Step, StitchOp, parse_repeat


def _sc(n: int) -> StitchOp:
    return StitchOp(kind="sc", count=n)


def build_star_pattern() -> Pattern:
    base_rounds = [
        RoundSpec(index=1, label="Base row 1", starts_from="magic_ring", join_sl=False,
                  cycle=[_sc(6)], declared_total=6,
                  spec_text="Make a MR. Make 6 sc into the MR (no sl st)."),
        RoundSpec(index=2, label="Base row 2", join_sl=False,
                  cycle=[StitchOp(kind="inc", count=6)], declared_total=12,
                  spec_text="Make an inc in every single stitch (12 sc)."),
        RoundSpec(index=3, label="Base row 3", join_sl=False,
                  cycle=parse_repeat("x, v"), repeats=6, declared_total=18,
                  spec_text="Repeat (1 sc, 1 inc) 6 times (18 sc)."),
        RoundSpec(index=4, label="Base row 4", join_sl=False,
                  cycle=parse_repeat("2x, v"), repeats=6, declared_total=24,
                  spec_text="Repeat (2 sc, 1 inc) 6 times (24 sc)."),
        RoundSpec(index=5, label="Base row 5", join_sl=False,
                  cycle=parse_repeat("3x, v"), repeats=6, declared_total=30,
                  spec_text="Repeat (3 sc, 1 inc) 6 times (30 sc)."),
    ]

    # One point, worked as five independent instances off the 30-stitch base.
    point_rows = [
        RoundSpec(index=1, starts_from="edge", flat=True,
                  join_sl=False, cycle=[_sc(6)], declared_total=6,
                  spec_text="6 sc, ch 1, turn your work."),
        RoundSpec(index=2, flat=True, join_sl=False,
                  leading=[StitchOp(kind="sk", count=1)], cycle=[_sc(5)], declared_total=5,
                  spec_text="Sk the first stitch and make 5 sc, ch 1, turn your work."),
        RoundSpec(index=3, flat=True, join_sl=False,
                  leading=[StitchOp(kind="sk", count=1)], cycle=[_sc(4)], declared_total=4,
                  spec_text="Sk the first stitch and make 4 sc, ch 1, turn your work."),
        RoundSpec(index=4, flat=True, join_sl=False,
                  leading=[StitchOp(kind="sk", count=1)], cycle=[_sc(3)], declared_total=3,
                  spec_text="Sk the first stitch and make 3 sc, ch 1, turn your work."),
        RoundSpec(index=5, flat=True, fasten_off=True, join_sl=False,
                  leading=[StitchOp(kind="sk", count=1)], cycle=[_sc(2)], declared_total=2,
                  spec_text="Sk the first stitch and make 2 sc, ch 1, fasten off."),
    ]

    components = [
        Component(name="Star", quantity=2, kind="verified", hook=3.5, hook_origin="inferred",
                  rounds=base_rounds,
                  blocks=[Block(name="Point", instances=5, rows=point_rows,
                                consumes_base_stitches=6)],
                  notes=["Make another star following the same pattern.",
                         ("Open question: Materials list 3-ply and 2-ply yarn but never says "
                          "which ply belongs to which part. The hooks are assigned (3.5 mm for "
                          "the star, 1.0 mm for the appliqué); the ply pairing is a guess, so it "
                          "is left to you -- 3-ply on 3.5 mm and 2-ply on 1.0 mm is the usual "
                          "matching, not the source's instruction."),
                         ("Open question: which hook for which part is also inferred, not "
                          "stated. Your Materials say '1 mm and 3.5 mm hooks' and never name a "
                          "part; the assignment is printed as inferred because a 1.0 mm hook "
                          "cannot make this star and a 3.5 mm hook cannot make a 5-petal flower.")]),

        # The source's two sentences, then the seam the framework wrote to make them work.
        Component(name="Sewing", role="operation", kind="manual", steps=[
            Step("Join two stars together and sew them together, stopping near the end.",
                 "source"),
            Step("Add filling and then sew completely.", "source"),
            Step(("Place the two stars with their right sides facing out and their wrong sides "
                  "together inside, lining up the flat bases and all 5 points tip to tip."),
                 "added",
                 why="The source doesn't say how the two faces are stacked. This orientation is "
                     "the one the seam below needs; the opposite pairing would leave the "
                     "ornament inside-out."),
            Step("Thread the yarn needle with about 70 cm of the same yarn.", "added",
                 why="A working length, not a figure from your source."),
            Step(("Bring the needle up between the layers at the base of one point so the "
                  "starting knot is hidden inside."), "added"),
            Step(("Sew around with an invisible slip-stitch seam: pick up one front loop on the "
                  "star in front and one back loop on the star behind, pull the yarn through, and "
                  "repeat one seam stitch per crochet stitch."), "added"),
            Step(("At each of the 5 tips take two stitches into the same space so the point "
                  "turns sharp instead of rounding off."), "added"),
            Step("Stop with about 4 cm of the last point left open. Fasten off temporarily.",
                 "added", why="This is your 'stopping near the end', made measurable."),
            Step(("Push small pieces of fiber filling through the opening, working them into "
                  "each point with the back of a hook so the tips fill without bulging the "
                  "seam."), "added", why="Expands your 'Add filling'."),
            Step(("Close the opening with the same invisible seam, matching stitch for stitch. "
                  "Pull the yarn tight, pass the needle through the star and out the other side, "
                  "and cut so the tail disappears inside."), "added",
                 why="Expands your 'then sew completely'."),
        ], notes=[("This seam is worked entirely with yarn and a needle. No glue is used "
                   "anywhere in it; glue appears in the materials only for the surface "
                   "decoration.")]),

        Component(name="Flower", quantity=2, kind="manual", hook=1.0, hook_origin="inferred",
                  steps=[
            Step("Make a MR and ch 2.", "source"),
            Step("Make 1 dc into the MR, ch 2, sl st into the MR.", "source"),
            Step("Repeat the pattern for 4 more times.", "source"),
            Step("Close the MR and cut the yarn.", "source"),
            Step("Make another flower following the same pattern.", "source"),
            Step(("If you mean to sew the flowers on instead of gluing them, leave a tail long "
                  "enough to bury when you cut."), "added",
                 why="Your source cuts the yarn and glues; this only matters if you switch to "
                     "sewing."),
        ]),

        Component(name="Cherry", quantity=3, kind="manual", hook=1.0, hook_origin="inferred",
                  steps=[
            Step("Make a sl knot and ch 2.", "source"),
            Step("Sk the first ch and make a puffy stitch into the second ch.", "source"),
            Step("Ch 1 and tie the threads tightly.", "source"),
            Step("Make 2 more cherries following the same pattern.", "source"),
        ], notes=[("Open question: 'puffy stitch' is used but never defined in the source -- no "
                   "loop count, no height. It cannot be counted or drawn until you say which "
                   "puff you mean (a 3-loop puff and a 5-loop puff are different sizes).")]),

        Component(name="Blush", quantity=2, kind="verified", hook=1.0, hook_origin="inferred",
                  rounds=[
            RoundSpec(index=1, starts_from="magic_ring", join_sl=True, cycle=[_sc(5)],
                      declared_total=5,
                      spec_text="Make a MR. Make 5 sc into the MR. Close the MR and sl st."),
        ], notes=["Make 1 more blush."]),

        Component(name="Assembly", role="operation", kind="manual", steps=[
            Step("Glue the flowers, cherries and blush accordingly.", "source"),
            Step("Glue the eyes in the middle.", "source"),
            Step("Cut a small piece of black or brown yarn and glue it in the middle to look "
                 "like a smile.", "source"),
        ], notes=[("Open question: the materials list does not include the eyes used here. The "
                   "source says 'glue the eyes' but never lists them or their type -- choose "
                   "them, or embroider the eyes in black yarn."),
                  ("Added guidance, not your instruction: glue holds surface decoration, but a "
                   "sewn-on flower survives being handled far better. Sew if this is for a "
                   "child.")]),

        Component(name="Hanging", role="operation", kind="manual", steps=[
            Step("Make a sl knot and ch 20, then cut the yarn.", "source"),
            Step("Insert it onto the top of the star to make a hanging.", "source"),
            Step(("Sew the loop into the top seam with two stitches on the inside and bury the "
                  "tail there."), "added",
                 why="'Insert it onto the top' cannot carry weight; a knotted loop pulled "
                      "against a stitch hole tears. That fixing is a recommendation, not the "
                      "source's instruction."),
        ]),
    ]

    return Pattern(
        name="Crochet Star Hanging Ornament",
        item_type="hanging ornament",
        description="A stuffed star hanging ornament made from two 5-pointed stars sewn "
                    "together, decorated with flowers, cherries and blush, with eyes and a "
                    "smile and a chain hanging loop.",
        provenance=("Instruction wording is transcribed from the pattern text you supplied "
                    "(Materials, Abbreviations, Star Base, Star Points, Sewing, Flowers, Cherry, "
                    "Blush, Assembly, Hanging). Where the framework wrote or widened a line, that "
                    "line carries an ADDED or INFERRED tag next to it -- see the provenance tally "
                    "below and the Open questions list for the gaps the source leaves."),
        undefined_terms=["puffy stitch (loop count and height not given in the source)"],
        material=Material(
            yarn="Acrylic yarn (3-ply and 2-ply)",
            hooks=[3.5, 1.0],
            notions=["scissors", "glue", "yarn needle", "fiber filling"],
        ),
        abbreviations={
            "MR": "Magic ring",
            "sl knot": "Slip knot",
            "sc": "Single crochet",
            "inc": "Increase",
            "sk": "Skip",
            "ch": "Chain",
            "sl st": "Slip stitch",
            "dc": "Double crochet",
        },
        components=components,
    )

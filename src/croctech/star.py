"""The star hanging ornament, encoded exactly as specified.

Every round carries the author's own wording in `spec_text`, which is what the
renderers print as the instruction of record. The stitch ops beside it are the
machine-readable form the engine uses to re-derive the count independently -- if
the quoted wording and the computed count ever disagree, the row fails and the
pattern refuses to render.

The five points are modelled as a `Block` with five instances, not as one block
plus a sentence, so the engine can prove 5 x 6 = 30 and that the last point ends
on the last base stitch.

No gauge is supplied for this item, so no finished size or yarn weight is
claimed. `provenance` records that this is a hand-typed transcription.
"""

from __future__ import annotations

from .schema import Block, Component, Material, Pattern, RoundSpec, StitchOp, parse_repeat


def _sc(n: int) -> StitchOp:
    return StitchOp(kind="sc", count=n)


def build_star_pattern() -> Pattern:
    base_rounds = [
        RoundSpec(index=1, label="Base row 1", foundation=True, join_sl=False,
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
        RoundSpec(index=1, foundation=True, starts_from="edge", flat=True,
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
        Component(name="Star", quantity=2, kind="verified", hook=3.5, rounds=base_rounds,
                  blocks=[Block(name="Point", instances=5, rows=point_rows,
                                consumes_base_stitches=6)],
                  notes=["Make another star following the same pattern."]),

        # Sewing is done entirely with yarn and needle -- no glue in the seam.
        Component(name="Sewing", role="operation", kind="manual", steps=[
            ("Place the two stars together with wrong sides facing out, lining up the flat "
             "bases and all 5 points tip to tip."),
            ("Thread the yarn needle with about 70 cm of the same yarn."),
            ("Bring the needle up between the layers at the base of one point so the starting "
             "knot is hidden inside."),
            ("Sew around with an invisible slip-stitch seam: pick up one front loop on the star "
             "in front and one back loop on the star behind, pull the yarn through, and repeat "
             "one seam stitch per crochet stitch -- 30 seam stitches across the base."),
            ("At each of the 5 tips take two stitches into the same space so the point turns "
             "sharp instead of rounding off."),
            ("Stop with about 4 cm of the last point left open. Fasten off temporarily."),
            ("Push small pieces of fiber filling through the opening, working them into each "
             "point with the back of a hook so the tips fill without bulging the seam."),
            ("Close the opening with the same invisible seam, matching stitch for stitch. Pull "
             "the yarn tight, pass the needle through the star and out the other side, and cut "
             "so the tail disappears inside."),
        ], notes=[("This seam is worked entirely with yarn and a needle. No glue is used "
                   "anywhere in it; glue appears in the materials only for the surface "
                   "decoration.")]),

        Component(name="Flower", quantity=2, kind="manual", hook=1.0, steps=[
            "Make a MR and ch 2.",
            "Petal 1: make 1 dc into the MR, ch 2, sl st into the MR.",
            "Repeat the petal 4 more times in the same ring (5 petals in total).",
            "Close the MR and cut the yarn, leaving a tail for sewing on.",
        ], notes=["Make another flower following the same pattern."]),

        Component(name="Cherry", quantity=3, kind="manual", hook=1.0, steps=[
            "Make a sl knot and ch 2.",
            "Sk the first ch and make a puffy stitch into the second ch.",
            "Ch 1 and tie the threads tightly.",
        ], notes=["Make 2 more cherries following the same pattern."]),

        Component(name="Blush", quantity=2, kind="verified", hook=1.0, rounds=[
            RoundSpec(index=1, foundation=True, cycle=[_sc(5)], declared_total=5,
                      spec_text="Make a MR. Make 5 sc into the MR. Close the MR and sl st."),
        ], notes=["Make 1 more blush."]),

        Component(name="Assembly", role="operation", kind="manual", steps=[
            "Sew or glue the flowers, cherries and blush in place.",
            "Attach the eyes in the middle.",
            ("Cut a small piece of black or brown yarn and fix it in the middle to look like a "
             "smile."),
        ], notes=[("Open question: the materials list does not include the eyes used here. The "
                   "source says 'glue the eyes' but never lists them or their type -- choose "
                   "them, or embroider the eyes in black yarn.")]),

        Component(name="Hanging", role="operation", kind="manual", steps=[
            "Make a sl knot and ch 20, then cut the yarn.",
            "Insert it onto the top of the star to make a hanging.",
        ], notes=[("Open question: the source says only 'insert it onto the top'. To bear "
                   "weight without tearing, sew the loop into the top seam with two stitches on "
                   "the inside and bury the tail -- that fixing is a recommendation, not the "
                   "source's instruction.")]),
    ]

    return Pattern(
        name="Crochet Star Hanging Ornament",
        item_type="hanging ornament",
        description="A stuffed star hanging ornament made from two 5-pointed stars sewn "
                    "together, decorated with flowers, cherries and blush, with eyes and a "
                    "smile and a chain hanging loop.",
        provenance=("Transcribed by hand from the user's supplied pattern text (Materials, "
                    "Abbreviations, Star Base, Star Points, Sewing, Flowers, Cherry, Blush, "
                    "Assembly, Hanging). No part of the instruction wording is model output. "
                    "Gaps in the source are flagged as open questions, not filled in."),
        undefined_terms=["puffy stitch (loop count and height not given in the source)"],
        material=Material(
            yarn="Acrylic yarn (3-ply and 2-ply)",
            hook_mm=3.5,
            hooks=[1.0],
            colors=["as desired"],
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

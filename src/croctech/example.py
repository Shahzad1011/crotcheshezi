"""The user's keychain-hat pattern encoded as structured, verifiable data.

This is the golden fixture: the row wording is the author's own, the stitch ops
are the machine-readable form of that same wording, and every total is re-derived
and checked by the engine. If the framework's math disagrees with what was
claimed, a test fails -- so this pattern shipping "clean" is real evidence.
"""

from __future__ import annotations

from .schema import Component, Gauge, Material, Pattern, RoundSpec, StitchOp, parse_repeat

RED = "red"
WHITE = "white (or silver glitter)"

_SL = "Complete the row by making a sl st at the top of the first sc."


def _even(index: int, count: int, color: str | None = None) -> RoundSpec:
    return RoundSpec(
        index=index, color=color, join_sl=True,
        cycle=[StitchOp(kind="sc", count=count)], declared_total=count,
        spec_text=f"1 ch. Starting from the top of the loop where you made the sl st, make "
                  f"{count} sc side by side. {_SL}")


def _shaped(index: int, gap: int, repeats: int, total: int,
            color: str | None = None) -> RoundSpec:
    """A shaping row: `gap` sc, then 2 sc in the next stitch, repeated `repeats` times."""
    return RoundSpec(
        index=index, color=color, join_sl=True,
        cycle=parse_repeat(f"{gap}x, v"), repeats=repeats,
        declared_total=total,
        spec_text=f"1 ch. Starting from the top of the loop where you made the sl st, make "
                  f"{gap} sc side by side, 2 sc in the top of the next stitch; repeat this "
                  f"until the end of the row, making a total of {total} sc. "
                  f"({gap}x, v sc) {_SL}")


def build_pattern() -> Pattern:
    rounds: list[RoundSpec] = [
        RoundSpec(index=1, color=RED, starts_from="magic_ring", join_sl=True,
                  cycle=[StitchOp(kind="sc", count=6)],
                  declared_total=6,
                  spec_text="Leave some string. Make a magic ring. 1 ch. Make 6 single "
                            "crochets into the ring. Complete the row by making a sl st at "
                            "the top of the single crochet."),
        _shaped(2, 1, 3, 9, RED),
        _shaped(3, 2, 3, 12, RED),
        _shaped(4, 3, 3, 15, RED),
        _shaped(5, 4, 3, 18, RED),
        _even(6, 18, RED),
        _even(7, 18, RED),
        _even(8, 18, RED),
        _even(9, 18, RED),
        _shaped(10, 8, 2, 20, WHITE),
        _even(11, 20, WHITE),
        _even(12, 20, WHITE),
        _even(13, 20, WHITE),
        _even(14, 20, WHITE),
        _even(15, 20, WHITE),
    ]

    rounds[4].notes += ["At this stage you can attach the keychain clip.",
                        ("Make sure that the points where you made the slip stitches are on "
                        "the back side.")]
    rounds[8].notes.append("Switch to 2nd colour while making a sl st at the top of the first sc.")
    rounds[9].notes.append("Made 6 rows with glittery silver yarn for a glitter touch "
                           "(otherwise use white yarn).")
    rounds[14].notes.append("Cut the thread and make a secret join from the top of the first "
                            "loop. Fold the white rows for a hat-type look. Stick a small "
                            "pompom with glue on the top of the hat.")

    return Pattern(
        name="Crochet Mini Santa-Hat Keychain",
        item_type="keychain",
        description="A 15-round mini hat worked from the tip down in red, with a white "
                    "glitter brim, folded and finished with a pompom on a keychain clip.",
        material=Material(
            yarn="5-ply, 50% cotton / 50% acrylic, medium thickness",
            hook_mm=2.5,
            colors=[RED, WHITE],
            notions=["keychain clip", "small pompom", "glue", "scissors"],
            meters_per_gram=3.2,
        ),
        provenance="Row wording transcribed from the written pattern you supplied; the "
                   "framework added no instruction that is not in it. The work direction "
                   "(tip down) is inferred from your own row order and is marked as such.",
        abbreviations={
            "ch": "Chain",
            "sc": "Single crochet",
            "sl st": "Slip stitch",
            "magic ring": "Ring of adjustable loops worked over first (MR)",
            "x": "1 single crochet",
            "v": "2 single crochets in the top of the next stitch (increase)",
        },
        gauge=Gauge(
            stitches_per_10cm=30, rows_per_10cm=36,
            note="ASSUMED gauge. You gave yarn and hook but no swatch, and no swatch means no "
                 "measured size. 30 sts x 36 rows / 10 cm is a typical tight-tension amigurumi "
                 "gauge on 2.5 mm with 5-ply, so treat every centimetre below as illustrative. "
                 "Work a 10 x 10 cm swatch, count it, and re-run to make these exact.",
        ),
        components=[Component(
            name="Hat", kind="verified", rounds=rounds,
            # Inference, stated as one: row 1 is the magic ring at the crown and the last
            # white rows are the brim, so the profile must be drawn tip-up, not brim-up.
            build_direction="from_tip",
            notes=[("Worked from the tip down (inferred from your own wording: the last rows "
                    "are the brim you fold, and row 1 is the ring at the top).")]),
        ],
    )

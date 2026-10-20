"""Gauge -> physical dimensions, with an honest tolerance band.

`pint` is used so units can't silently drift: stitches are a first-class
dimension, so dividing stitches by (stitches/cm) yields centimetres by
construction. Exactness still depends on the maker's real tension, which no code
can guarantee; we therefore report a +/- tolerance band, not a fake precise value.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pint

ureg = pint.UnitRegistry()
ureg.define("stitch = [count]")  # first-class count dimension for stitch/row tallies


@dataclass
class Dimensions:
    widest_circumference_cm: float
    widest_diameter_cm: float
    height_cm: float
    tolerance_pct: float

    def band(self, value_cm: float) -> tuple[float, float]:
        delta = value_cm * self.tolerance_pct / 100.0
        return round(value_cm - delta, 2), round(value_cm + delta, 2)


@dataclass
class ColourUsage:
    stitches: int
    meters: float
    grams: float | None


@dataclass
class YarnUsage:
    by_colour: dict[str, ColourUsage]
    total_stitches: int
    total_meters: float
    total_grams: float | None

    @property
    def is_estimate(self) -> bool:
        return True


def compute_dimensions(pattern, produced_per_round: list[int], tolerance_pct: float = 10.0):
    """Returns None when no gauge was supplied. We never invent a stitch gauge,
    because a fabricated gauge would silently fabricate the finished size too.
    """
    g = pattern.gauge
    if g is None:
        return None
    sts_per_cm = (g.stitches_per_10cm * ureg.stitch) / (10 * ureg.cm)   # count / cm
    rows_per_cm = (g.rows_per_10cm * ureg.stitch) / (10 * ureg.cm)      # count / cm

    widest = max(produced_per_round) if produced_per_round else 0
    circumference = (widest * ureg.stitch) / sts_per_cm                    # cm
    diameter = (circumference / math.pi) if widest else 0 * ureg.cm        # cm
    height = (len(produced_per_round) * ureg.stitch) / rows_per_cm         # cm

    return Dimensions(
        widest_circumference_cm=round(float(circumference.magnitude), 2),
        widest_diameter_cm=round(float(diameter.magnitude), 2),
        height_cm=round(float(height.magnitude), 2),
        tolerance_pct=tolerance_pct,
    )


def compute_yarn_usage(pattern, audits) -> YarnUsage | None:
    """Estimate yarn per colour from the engine's audited rows. None without a gauge.

    Takes audits rather than a positional list of counts: a repeated block is
    audited once per instance, and each part is multiplied by how many you make,
    so a two-star ornament is not quoted for one star.

    Heuristic: a single crochet consumes about one wrap = 2*stitch_width +
    2*row_height (both from gauge). Clearly an estimate; real usage depends on
    tension and stitch style. Grams require a meters_per_gram density.
    """
    g = pattern.gauge
    if g is None:
        return None
    stitch_width_cm = 10.0 / g.stitches_per_10cm
    row_height_cm = 10.0 / g.rows_per_10cm
    cm_per_sc = 2 * stitch_width_cm + 2 * row_height_cm

    density = pattern.material.meters_per_gram
    quantity = {c.name: c.quantity for c in pattern.components}
    exact: dict[str, float] = {}
    stitches: dict[str, int] = {}
    for a in audits:
        colour = a.color or "main"
        sc = a.produced * quantity.get(a.component, 1)
        stitches[colour] = stitches.get(colour, 0) + sc
        exact[colour] = exact.get(colour, 0.0) + sc * cm_per_sc / 100.0

    # Round each colour once, then total the rounded parts, so the printed
    # breakdown always adds up to the printed total.
    by_colour = {c: ColourUsage(stitches[c], round(du, 2),
                                round(du / density, 2) if density else None)
                 for c, du in exact.items()}
    total_m = round(sum(cu.meters for cu in by_colour.values()), 2)
    total_g = (round(sum(cu.grams for cu in by_colour.values()), 2) if density else None)

    return YarnUsage(
        by_colour=by_colour,
        total_stitches=sum(stitches.values()),
        total_meters=total_m,
        total_grams=total_g,
    )

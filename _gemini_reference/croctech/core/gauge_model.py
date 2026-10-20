"""
Gauge Model & Dimensional Physics for Crochet.
Calculates exact stitch width, row height, fabric thickness, and yardage consumption.
"""

import math
from dataclasses import dataclass
from typing import Dict
from croctech.core.types import StitchType, STITCH_PROPERTIES
from croctech.core.yarn_hook import YarnSpec, HookSpec


@dataclass
class GaugeResult:
    """Calculated physical gauge measurements."""
    hook_mm: float
    yarn_name: str
    stitch_width_mm: float       # Width of 1 single crochet in mm
    row_height_mm: float         # Height of 1 row of single crochet in mm
    stitches_per_10cm: float     # Gauge stitches count per 10 cm
    rows_per_10cm: float         # Gauge rows count per 10 cm
    fabric_thickness_mm: float   # Single layer fabric thickness in mm
    folded_thickness_mm: float   # Folded brim double layer thickness in mm
    tension_factor: float        # 1.0 = standard, 0.9 = tight amigurumi, 1.1 = loose


class GaugeModel:
    """Computes exact physical dimensions and yardage from yarn and hook physics."""

    def __init__(self, hook: HookSpec, yarn: YarnSpec, tension_factor: float = 0.92):
        """
        tension_factor:
        - 0.90 to 0.93: Typical tight tension for amigurumi, keychains, and 3D shapes to prevent fiber fill peek-through
        - 1.00: Standard tension for garments and blankets
        - 1.10: Loose drape tension
        """
        self.hook = hook
        self.yarn = yarn
        self.tension_factor = tension_factor

    def calculate_gauge(self) -> GaugeResult:
        """Calculate exact gauge dimensions in millimeters and stitches/10cm."""
        hook_d = self.hook.metric_mm
        yarn_d = self.yarn.uncompressed_diameter_mm

        # Single crochet stitch geometry:
        # Width is primarily determined by hook throat diameter + yarn loop packing
        width_base = (hook_d * 1.18 + yarn_d * 0.65) * self.tension_factor
        # Height is determined by loop draw height (sc standard aspect ratio is approx 0.88-0.90)
        height_base = width_base * 0.895

        st_per_10cm = (100.0 / width_base)
        rows_per_10cm = (100.0 / height_base)

        single_thickness = (yarn_d * 1.55) * self.tension_factor
        double_thickness = single_thickness * 1.9  # Folded cuff / brim

        return GaugeResult(
            hook_mm=hook_d,
            yarn_name=self.yarn.name,
            stitch_width_mm=round(width_base, 3),
            row_height_mm=round(height_base, 3),
            stitches_per_10cm=round(st_per_10cm, 1),
            rows_per_10cm=round(rows_per_10cm, 1),
            fabric_thickness_mm=round(single_thickness, 2),
            folded_thickness_mm=round(double_thickness, 2),
            tension_factor=self.tension_factor
        )

    def stitch_dimensions(self, stitch_type: StitchType) -> Dict[str, float]:
        """Returns {width_mm, height_mm} for a specific stitch type."""
        gauge = self.calculate_gauge()
        props = STITCH_PROPERTIES.get(stitch_type, STITCH_PROPERTIES[StitchType.SC])
        h_ratio = props["height_ratio"]
        return {
            "width_mm": gauge.stitch_width_mm,
            "height_mm": gauge.row_height_mm * h_ratio
        }

    def yarn_consumed_per_stitch_meters(self, stitch_type: StitchType) -> float:
        """Returns meters of yarn consumed for 1 stitch of given type."""
        props = STITCH_PROPERTIES.get(stitch_type, STITCH_PROPERTIES[StitchType.SC])
        mult = props["yarn_multiplier"]
        hook_d = self.hook.metric_mm

        # Length in mm = multiplier * hook_d * tension_factor
        length_mm = mult * hook_d * self.tension_factor
        return length_mm / 1000.0

    def estimate_yarn_weight_grams(self, meters: float) -> float:
        """Convert yarn length in meters to grams based on yarn linear density."""
        return meters * self.yarn.grams_per_meter


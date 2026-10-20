"""
3D Surface Geometry Engine for Crochet.
Calculates continuous 3D surface profiles, radii, cone angles, curvature, and physical dimensions.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from croctech.core.gauge_model import GaugeResult


@dataclass
class RowGeometry:
    """Calculated geometry for a single row or round."""
    row_index: int
    stitch_count: int
    delta_stitches: int           # Difference from previous row (+ increases, - decreases)
    circumference_mm: float       # Perimeter = stitch_count * stitch_width
    radius_mm: float              # r = circumference / (2 * pi)
    row_height_mm: float          # Vertical height added by this row
    cumulative_height_mm: float   # Accumulated height from crown/bottom
    cone_half_angle_deg: Optional[float] = None # Conical slope angle
    curvature_type: str = "cylinder" # cone, cylinder, flat_disc, hyperbolic_ruffle, dome_close


@dataclass
class PieceDimensions:
    """Finished physical dimensions for the entire crochet piece."""
    total_stitches: int
    total_rows: int
    unfolded_height_mm: float
    unfolded_height_cm: float
    unfolded_height_inches: float
    finished_height_mm: float     # Accounting for folded brim or attachments
    finished_height_cm: float
    finished_height_inches: float
    max_diameter_mm: float
    max_diameter_cm: float
    max_diameter_inches: float
    base_diameter_mm: float
    crown_diameter_mm: float
    total_surface_area_cm2: float
    profile: List[RowGeometry] = field(default_factory=list)
    has_folded_brim: bool = False
    folded_rows_count: int = 0
    pompom_height_mm: float = 0.0


class GeometryEngine:
    """Computes exact 3D shape profiles and verifies geometric sanity."""

    def __init__(self, gauge: GaugeResult):
        self.gauge = gauge

    def compute_piece_profile(
        self,
        stitch_counts: List[int],
        fold_up_rows: int = 0,
        pompom_diameter_mm: float = 0.0
    ) -> PieceDimensions:
        """
        Computes the complete physical profile row by row.
        stitch_counts: List of stitch counts for Row 1, Row 2, ..., Row N
        fold_up_rows: Number of bottom rows that get folded upwards as a cuff
        pompom_diameter_mm: Extra height added by top pompom
        """
        w = self.gauge.stitch_width_mm
        h = self.gauge.row_height_mm

        profile: List[RowGeometry] = []
        cumulative_h = 0.0
        prev_r = 0.0
        total_st = sum(stitch_counts)
        total_surface_mm2 = 0.0

        for idx, count in enumerate(stitch_counts, start=1):
            delta = count if idx == 1 else (count - stitch_counts[idx - 2])
            circumference = count * w
            radius = circumference / (2.0 * math.pi)

            # Slant height and vertical height increment
            if idx == 1:
                # First round inside magic ring
                vert_h = h
                cone_angle = None
                c_type = "crown_start"
            else:
                dr = abs(radius - prev_r)
                if dr >= h:
                    vert_h = 0.0  # Flat horizontal expansion
                    cone_angle = 90.0
                    c_type = "flat_disc"
                else:
                    vert_h = math.sqrt(max(0.0, (h * h) - (dr * dr)))
                    sin_theta = dr / h
                    cone_angle = math.degrees(math.asin(min(1.0, sin_theta)))

                    if delta == 0:
                        c_type = "cylinder"
                    elif delta > 0:
                        if delta > 6:
                            c_type = "hyperbolic_ruffle"
                        else:
                            c_type = "cone_expand"
                    else:
                        c_type = "dome_decrease"

            cumulative_h += vert_h

            # Frustum lateral surface area
            if idx == 1:
                total_surface_mm2 += math.pi * (radius ** 2)
            else:
                total_surface_mm2 += math.pi * (prev_r + radius) * h

            profile.append(RowGeometry(
                row_index=idx,
                stitch_count=count,
                delta_stitches=delta,
                circumference_mm=round(circumference, 2),
                radius_mm=round(radius, 2),
                row_height_mm=round(vert_h, 2),
                cumulative_height_mm=round(cumulative_h, 2),
                cone_half_angle_deg=round(cone_angle, 1) if cone_angle is not None else None,
                curvature_type=c_type
            ))
            prev_r = radius

        unfolded_h = cumulative_h
        finished_h = unfolded_h

        # Fold adjustment
        if fold_up_rows > 0 and len(profile) >= fold_up_rows:
            # Folding bottom K rows reduces height by vertical height of those K rows
            folded_h_loss = sum(r.row_height_mm for r in profile[-fold_up_rows:])
            finished_h = max(0.0, unfolded_h - folded_h_loss)

        # Add pompom height if present
        if pompom_diameter_mm > 0:
            finished_h += pompom_diameter_mm

        radii = [r.radius_mm for r in profile]
        max_r = max(radii) if radii else 0.0
        # If folded, max diameter includes double-wall fabric thickness
        extra_wall = (self.gauge.fabric_thickness_mm * 2) if fold_up_rows > 0 else 0.0
        max_diam = (max_r * 2.0) + extra_wall

        crown_diam = (profile[0].radius_mm * 2.0) if profile else 0.0
        base_diam = (profile[-1].radius_mm * 2.0) + extra_wall if profile else 0.0

        return PieceDimensions(
            total_stitches=total_st,
            total_rows=len(stitch_counts),
            unfolded_height_mm=round(unfolded_h, 2),
            unfolded_height_cm=round(unfolded_h / 10.0, 2),
            unfolded_height_inches=round(unfolded_h / 25.4, 2),
            finished_height_mm=round(finished_h, 2),
            finished_height_cm=round(finished_h / 10.0, 2),
            finished_height_inches=round(finished_h / 25.4, 2),
            max_diameter_mm=round(max_diam, 2),
            max_diameter_cm=round(max_diam / 10.0, 2),
            max_diameter_inches=round(max_diam / 25.4, 2),
            base_diameter_mm=round(base_diam, 2),
            crown_diameter_mm=round(crown_diam, 2),
            total_surface_area_cm2=round(total_surface_mm2 / 100.0, 2),
            profile=profile,
            has_folded_brim=(fold_up_rows > 0),
            folded_rows_count=fold_up_rows,
            pompom_height_mm=pompom_diameter_mm
        )


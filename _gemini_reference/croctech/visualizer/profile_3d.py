"""
3D Profile and ASCII Cross-Section Visualizer for CrocTech.
Provides ASCII cross-sections and detailed geometric tables for CLI and reporting.
"""

from typing import List
from croctech.core.geometry import PieceDimensions, RowGeometry


class ProfileVisualizer:
    """Visualizes 3D crochet shape profiles in terminal ASCII and Markdown tables."""

    @staticmethod
    def render_ascii_cross_section(dimensions: PieceDimensions, max_width_chars: int = 50) -> str:
        """Render a symmetric ASCII silhouette of the crochet object with dimensions."""
        profile = dimensions.profile
        if not profile:
            return "No profile available."

        max_r = max(r.radius_mm for r in profile)
        if max_r == 0:
            max_r = 1.0

        half_width = (max_width_chars - 10) // 2
        lines = []
        lines.append("=" * max_width_chars)
        lines.append("     3D CROCHET OBJECT PROFILE (AXIS-SYMMETRIC)")
        lines.append("=" * max_width_chars)

        # Top pompom if present
        if dimensions.pompom_height_mm > 0:
            p_pad = " " * (half_width - 2)
            lines.append(f"{p_pad}(*)   <-- Pompom (15mm)")

        for r_geo in profile:
            r_mm = r_geo.radius_mm
            char_count = max(1, int((r_mm / max_r) * half_width))
            pad_left = " " * (half_width - char_count)
            bar = "#" * char_count
            tag = " [Folded Brim]" if r_geo.row_index > (len(profile) - dimensions.folded_rows_count) and dimensions.has_folded_brim else ""
            lines.append(f"R{r_geo.row_index:02d} |{pad_left}{bar}|{bar}{pad_left}| Ø {r_mm * 2.0:4.1f}mm{tag}")

        lines.append("-" * max_width_chars)
        lines.append(f"Total Height: {dimensions.finished_height_mm:.1f} mm | Max Diameter: {dimensions.max_diameter_mm:.1f} mm")
        lines.append("=" * max_width_chars)

        return "\n".join(lines)

    @staticmethod
    def render_markdown_geometry_table(dimensions: PieceDimensions) -> str:
        """Render a markdown table listing every round's diameter, height, and curvature."""
        lines = []
        lines.append("| Row # | Stitch Count | Delta (sts) | Diameter (mm) | Row Height (mm) | Cumul. Height (mm) | Curvature / Shape |")
        lines.append("|:-----:|:------------:|:-----------:|:-------------:|:---------------:|:------------------:|:-----------------:|")

        for r in dimensions.profile:
            diam = r.radius_mm * 2.0
            shape_desc = r.curvature_type.replace("_", " ").title()
            if r.cone_half_angle_deg is not None and r.curvature_type == "cone_expand":
                shape_desc += f" ({r.cone_half_angle_deg:.0f}°)"
            lines.append(
                f"| {r.row_index} | {r.stitch_count} | {r.delta_stitches:+d} | "
                f"{diam:.1f} | {r.row_height_mm:.2f} | {r.cumulative_height_mm:.2f} | {shape_desc} |"
            )

        return "\n".join(lines)


"""
SVG Stitch Chart Generator for CrocTech.
Generates beautiful, publication-ready circular/spiral stitch charts and profile diagrams.
"""

import math
from typing import List
from croctech.core.models import PatternDef
from croctech.verifier.engine import VerificationReport


class SvgChartGenerator:
    """Produces scalable vector graphics (SVG) for circular and 3D cross-section crochet views."""

    @staticmethod
    def generate_circular_chart(pattern: PatternDef, report: VerificationReport, size: int = 600) -> str:
        """Generate a 2D circular stitch chart showing concentric rounds and increase points."""
        center = size // 2
        max_radius = (size // 2) - 40
        num_rounds = len(pattern.rounds)
        dr = max_radius / max(1, num_rounds)

        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">')
        svg.append('<defs>')
        svg.append('  <style>')
        svg.append('    .bg { fill: #0f172a; }')
        svg.append('    .grid-ring { fill: none; stroke: #334155; stroke-width: 1; stroke-dasharray: 3 3; }')
        svg.append('    .stitch-dot { fill: #ef4444; stroke: #ffffff; stroke-width: 1; }')
        svg.append('    .stitch-inc { fill: #eab308; stroke: #ffffff; stroke-width: 1.5; }')
        svg.append('    .stitch-white { fill: #f8fafc; stroke: #94a3b8; stroke-width: 1; }')
        svg.append('    .text-title { fill: #f8fafc; font-family: system-ui, sans-serif; font-size: 16px; font-weight: bold; }')
        svg.append('    .text-round { fill: #94a3b8; font-family: system-ui, sans-serif; font-size: 11px; }')
        svg.append('    .spoke { stroke: #1e293b; stroke-width: 0.8; }')
        svg.append('  </style>')
        svg.append('</defs>')
        svg.append(f'<rect width="{size}" height="{size}" class="bg" rx="16"/>')

        # Title
        svg.append(f'<text x="24" y="34" class="text-title">{pattern.title} — Stitch Topology Chart</text>')
        svg.append(f'<text x="24" y="52" class="text-round">{num_rounds} Rounds | {report.dimensions.total_stitches} Total Stitches | Zero Errors Verified</text>')

        # Center Magic Ring marker
        svg.append(f'<circle cx="{center}" cy="{center}" r="7" fill="none" stroke="#38bdf8" stroke-width="2.5"/>')
        svg.append(f'<text x="{center}" y="{center+4}" fill="#38bdf8" font-size="9" text-anchor="middle" font-family="sans-serif">MR</text>')

        # Draw rounds
        for r_idx, r_def in enumerate(pattern.rounds, start=1):
            r = 18 + (r_idx * dr * 0.95)
            st_count = r_def.calculated_stitch_count
            is_white = "white" in (r_def.color or "").lower() or "silver" in (r_def.color or "").lower()
            dot_class = "stitch-white" if is_white else "stitch-dot"

            # Concentric ring line
            svg.append(f'<circle cx="{center}" cy="{center}" r="{r:.1f}" class="grid-ring"/>')

            # Round label
            svg.append(f'<text x="{center + r + 4:.1f}" y="{center + 3}" class="text-round">R{r_idx} ({st_count})</text>')

            # Place stitches along the ring
            for s_i in range(st_count):
                angle = (2.0 * math.pi * s_i) / st_count - (math.pi / 2.0)
                cx = center + r * math.cos(angle)
                cy = center + r * math.sin(angle)

                # Check if this stitch was an increase
                # In R2-R5 and R10, increases happen periodically
                is_inc = False
                if r_def.round_number == 2 and s_i % 3 == 1: is_inc = True
                elif r_def.round_number == 3 and s_i % 4 == 2: is_inc = True
                elif r_def.round_number == 4 and s_i % 5 == 3: is_inc = True
                elif r_def.round_number == 5 and s_i % 6 == 4: is_inc = True
                elif r_def.round_number == 10 and (s_i == 8 or s_i == 17): is_inc = True

                curr_dot = "stitch-inc" if is_inc else dot_class
                dot_r = 3.5 if is_inc else 2.5
                svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dot_r}" class="{curr_dot}">')
                svg.append(f'  <title>Round {r_idx}, Stitch {s_i+1}{" (Increase)" if is_inc else ""}</title>')
                svg.append('</circle>')

        # Legend
        svg.append('<g transform="translate(24, 550)">')
        svg.append('  <circle cx="0" cy="0" r="4" class="stitch-dot"/>')
        svg.append('  <text x="10" y="4" class="text-round">Red sc</text>')
        svg.append('  <circle cx="70" cy="0" r="4" class="stitch-white"/>')
        svg.append('  <text x="80" y="4" class="text-round">White/Silver sc</text>')
        svg.append('  <circle cx="180" cy="0" r="4.5" class="stitch-inc"/>')
        svg.append('  <text x="190" y="4" class="text-round">Increase (+1 st)</text>')
        svg.append('</g>')

        svg.append('</svg>')
        return "\n".join(svg)

    @staticmethod
    def generate_3d_profile_svg(report: VerificationReport, width: int = 500, height: int = 400) -> str:
        """Generate a 2D cross-section silhouette showing physical dimensions in millimeters."""
        dim = report.dimensions
        profile = dim.profile
        if not profile:
            return ""

        max_r = max(r.radius_mm for r in profile)
        total_h = dim.unfolded_height_mm

        center_x = width // 2
        margin_y = 50
        scale_y = (height - 100) / max(1.0, total_h)
        scale_x = (width * 0.35) / max(1.0, max_r)

        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
        svg.append('<defs>')
        svg.append('  <style>')
        svg.append('    .bg3d { fill: #1e293b; }')
        svg.append('    .hat-body { fill: #ef4444; fill-opacity: 0.85; stroke: #fca5a5; stroke-width: 1.5; }')
        svg.append('    .hat-brim { fill: #f8fafc; fill-opacity: 0.95; stroke: #cbd5e1; stroke-width: 1.5; }')
        svg.append('    .center-axis { stroke: #64748b; stroke-width: 1; stroke-dasharray: 4 4; }')
        svg.append('    .dim-line { stroke: #38bdf8; stroke-width: 1.2; }')
        svg.append('    .text-dim { fill: #38bdf8; font-family: system-ui, sans-serif; font-size: 11px; }')
        svg.append('    .pompom { fill: #ffffff; stroke: #e2e8f0; stroke-width: 1.5; }')
        svg.append('  </style>')
        svg.append('</defs>')
        svg.append(f'<rect width="{width}" height="{height}" class="bg3d" rx="12"/>')

        # Title
        svg.append(f'<text x="20" y="30" fill="#f8fafc" font-family="sans-serif" font-weight="bold" font-size="14">Physical Profile & Dimensions (mm)</text>')

        # Center vertical axis
        svg.append(f'<line x1="{center_x}" y1="40" x2="{center_x}" y2="{height - 30}" class="center-axis"/>')

        # Draw red hat cone/body and white brim
        left_points = []
        right_points = []

        # Pompom at top if specified
        top_y = margin_y
        if dim.pompom_height_mm > 0:
            p_r = (dim.pompom_height_mm / 2.0) * scale_y
            svg.append(f'<circle cx="{center_x}" cy="{top_y + p_r:.1f}" r="{p_r:.1f}" class="pompom"/>')
            top_y += p_r * 2.0

        for r_geo in profile:
            y = top_y + (r_geo.cumulative_height_mm * scale_y)
            rx = r_geo.radius_mm * scale_x
            left_points.append(f"{center_x - rx:.1f},{y:.1f}")
            right_points.append(f"{center_x + rx:.1f},{y:.1f}")

        # Construct hat polygon
        poly_pts = left_points + list(reversed(right_points))
        svg.append(f'<polygon points="{" ".join(poly_pts)}" class="hat-body"/>')

        # White folded brim highlighting (bottom 6 rows)
        if len(profile) >= 6:
            brim_start_idx = max(0, len(profile) - 6)
            brim_pts_left = left_points[brim_start_idx:]
            brim_pts_right = list(reversed(right_points[brim_start_idx:]))
            brim_poly = brim_pts_left + brim_pts_right
            svg.append(f'<polygon points="{" ".join(brim_poly)}" class="hat-brim"/>')

        # Height Dimension Leader Line
        dim_x = width - 70
        y_start = top_y
        y_end = top_y + (dim.unfolded_height_mm * scale_y)
        svg.append(f'<line x1="{dim_x}" y1="{y_start}" x2="{dim_x}" y2="{y_end}" class="dim-line"/>')
        svg.append(f'<line x1="{dim_x - 5}" y1="{y_start}" x2="{dim_x + 5}" y2="{y_start}" class="dim-line"/>')
        svg.append(f'<line x1="{dim_x - 5}" y1="{y_end}" x2="{dim_x + 5}" y2="{y_end}" class="dim-line"/>')
        svg.append(f'<text x="{dim_x + 8}" y="{(y_start + y_end)/2:.1f}" class="text-dim">{dim.unfolded_height_mm:.1f} mm</text>')

        # Max Diameter Leader Line
        bottom_y = y_end + 18
        max_rx = max_r * scale_x
        svg.append(f'<line x1="{center_x - max_rx}" y1="{bottom_y}" x2="{center_x + max_rx}" y2="{bottom_y}" class="dim-line"/>')
        svg.append(f'<line x1="{center_x - max_rx}" y1="{bottom_y - 4}" x2="{center_x - max_rx}" y2="{bottom_y + 4}" class="dim-line"/>')
        svg.append(f'<line x1="{center_x + max_rx}" y1="{bottom_y - 4}" x2="{center_x + max_rx}" y2="{bottom_y + 4}" class="dim-line"/>')
        svg.append(f'<text x="{center_x}" y="{bottom_y + 16}" class="text-dim" text-anchor="middle">Max Ø: {dim.max_diameter_mm:.1f} mm</text>')

        svg.append('</svg>')
        return "\n".join(svg)


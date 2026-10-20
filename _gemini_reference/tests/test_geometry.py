"""
Unit Tests for Gauge and 3D Geometry Engines.
"""

from croctech.core.yarn_hook import YarnSpec, HookSpec
from croctech.core.gauge_model import GaugeModel
from croctech.core.geometry import GeometryEngine


def test_gauge_and_geometry_cone():
    """Verify gauge calculation and conical geometry."""
    hook = HookSpec.from_mm(2.50)
    yarn = YarnSpec.create_5ply_cotton_acrylic("Red")
    gauge_model = GaugeModel(hook=hook, yarn=yarn, tension_factor=0.92)
    gauge = gauge_model.calculate_gauge()

    assert 3.2 <= gauge.stitch_width_mm <= 4.0
    assert 2.8 <= gauge.row_height_mm <= 3.8
    assert 25.0 <= gauge.stitches_per_10cm <= 32.0

    geo = GeometryEngine(gauge)
    # Conical rounds: 6, 9, 12, 15, 18
    dim = geo.compute_piece_profile([6, 9, 12, 15, 18])
    assert dim.total_stitches == 60
    assert dim.total_rows == 5
    assert dim.unfolded_height_mm > 10.0
    assert dim.max_diameter_mm > dim.crown_diameter_mm
    assert dim.profile[1].curvature_type == "cone_expand"


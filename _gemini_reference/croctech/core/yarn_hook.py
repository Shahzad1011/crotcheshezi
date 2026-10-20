"""
Yarn and Hook Specifications and Physics.
Provides accurate physical properties, WPI, ply conversions, and fiber parameters.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from croctech.core.types import YarnWeight, FiberType


@dataclass
class HookSpec:
    """Crochet hook specifications."""
    metric_mm: float            # Diameter in millimeters (e.g., 2.50)
    us_size: Optional[str] = None # US letter/number (e.g., "C/2", "B/1")
    uk_size: Optional[int] = None # UK/Canadian old number (e.g., 12)
    material: str = "aluminum"   # aluminum, steel, wood, ergonomic plastic

    @classmethod
    def from_mm(cls, mm: float) -> "HookSpec":
        """Instantiate hook spec with common aliases."""
        alias_map = {
            2.0: ("2.0mm", "0", 14),
            2.25: ("B/1", "1", 13),
            2.5: ("2.5mm", "C/2 (approx)", 12),
            2.75: ("C/2", "2", None),
            3.0: ("3.0mm", None, 11),
            3.25: ("D/3", "3", 10),
            3.5: ("E/4", "4", 9),
            3.75: ("F/5", "5", None),
            4.0: ("G/6", "6", 8),
            4.5: ("7", "7", 7),
            5.0: ("H/8", "8", 6),
            5.5: ("I/9", "9", 5),
            6.0: ("J/10", "10", 4),
        }
        meta = alias_map.get(round(mm, 2), (None, None, None))
        return cls(metric_mm=mm, us_size=meta[0], uk_size=meta[2])


@dataclass
class YarnSpec:
    """Yarn material specifications and physical constants."""
    name: str = "Standard 5-ply Cotton/Acrylic"
    weight_category: YarnWeight = YarnWeight.FINE_2
    ply: int = 5
    fiber_type: FiberType = FiberType.COTTON_ACRYLIC_BLEND
    cotton_percentage: float = 50.0
    acrylic_percentage: float = 50.0
    meters_per_100g: float = 320.0 # ~160 m per 50 g ball (common for 5-ply cotton blend)
    uncompressed_diameter_mm: float = 1.2
    recommended_hook_range_mm: Tuple[float, float] = (2.25, 3.25)
    color: str = "Red"
    is_metallic: bool = False

    @property
    def linear_density_tex(self) -> float:
        """Linear density in g/km (tex)."""
        return (100.0 / self.meters_per_100g) * 1000.0

    @property
    def grams_per_meter(self) -> float:
        """Grams of yarn per meter."""
        return 100.0 / self.meters_per_100g

    @classmethod
    def create_5ply_cotton_acrylic(cls, color: str = "Red", is_glitter: bool = False) -> "YarnSpec":
        """Factory for the exact yarn specification described in the prompt."""
        if is_glitter:
            return cls(
                name="5-ply Glitter/Metallic Accent Yarn",
                weight_category=YarnWeight.FINE_2,
                ply=5,
                fiber_type=FiberType.METALLIC_GLITTER,
                cotton_percentage=40.0,
                acrylic_percentage=50.0,
                meters_per_100g=310.0,
                uncompressed_diameter_mm=1.2,
                recommended_hook_range_mm=(2.25, 3.0),
                color=color,
                is_metallic=True
            )
        return cls(
            name="5-ply 50% Cotton 50% Acrylic Medium-Thickness",
            weight_category=YarnWeight.FINE_2,
            ply=5,
            fiber_type=FiberType.COTTON_ACRYLIC_BLEND,
            cotton_percentage=50.0,
            acrylic_percentage=50.0,
            meters_per_100g=320.0,
            uncompressed_diameter_mm=1.2,
            recommended_hook_range_mm=(2.25, 3.0),
            color=color,
            is_metallic=False
        )


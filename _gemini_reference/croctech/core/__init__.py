"""
CrocTech Core Package.
Provides foundational stitch types, yarn/hook specs, gauge models, geometry, and graph algorithms.
"""

from croctech.core.types import (
    StitchType,
    WorkingMode,
    LoopTarget,
    YarnWeight,
    FiberType,
    Terminology,
    STITCH_PROPERTIES,
)
from croctech.core.yarn_hook import YarnSpec, HookSpec
from croctech.core.gauge_model import GaugeModel, GaugeResult
from croctech.core.geometry import GeometryEngine, RowGeometry, PieceDimensions
from croctech.core.graph import StitchNode, StitchGraph
from croctech.core.models import (
    MaterialItem,
    StitchCommand,
    RoundDef,
    AssemblyInstruction,
    PatternDef,
)

__all__ = [
    "StitchType",
    "WorkingMode",
    "LoopTarget",
    "YarnWeight",
    "FiberType",
    "Terminology",
    "STITCH_PROPERTIES",
    "YarnSpec",
    "HookSpec",
    "GaugeModel",
    "GaugeResult",
    "GeometryEngine",
    "RowGeometry",
    "PieceDimensions",
    "StitchNode",
    "StitchGraph",
    "MaterialItem",
    "StitchCommand",
    "RoundDef",
    "AssemblyInstruction",
    "PatternDef",
]


"""
CrocTech: 100% Accurate Algorithmic Crochet Engineering Framework.
Combines topological stitch graphs, physics-based gauge modeling, 3D geometry engines,
and compiler-grade deterministic verifiers with AI pattern synthesis.
"""

__version__ = "1.0.0"

from croctech.core import (
    StitchType,
    WorkingMode,
    LoopTarget,
    YarnWeight,
    FiberType,
    Terminology,
    YarnSpec,
    HookSpec,
    GaugeModel,
    GaugeResult,
    GeometryEngine,
    RowGeometry,
    PieceDimensions,
    StitchNode,
    StitchGraph,
    MaterialItem,
    StitchCommand,
    RoundDef,
    AssemblyInstruction,
    PatternDef,
)
from croctech.dsl import CrochetPatternParser, PatternFormatter
from croctech.verifier import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
    PatternVerifier,
    VerificationReport,
    RoundVerificationSummary,
    YarnUsageReport,
)
from croctech.ai import (
    CROCHET_AI_SYSTEM_PROMPT,
    build_pattern_prompt,
    CrochetAutoCorrector,
    PatternSynthesisPipeline,
)
from croctech.visualizer import SvgChartGenerator, ProfileVisualizer, HtmlReportGenerator
from croctech.exporter import MarkdownExporter, JsonExporter, PdfExporter

__all__ = [
    "__version__",
    "StitchType",
    "WorkingMode",
    "LoopTarget",
    "YarnWeight",
    "FiberType",
    "Terminology",
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
    "CrochetPatternParser",
    "PatternFormatter",
    "Diagnostic",
    "DiagnosticCode",
    "DiagnosticSeverity",
    "PatternVerifier",
    "VerificationReport",
    "RoundVerificationSummary",
    "YarnUsageReport",
    "CROCHET_AI_SYSTEM_PROMPT",
    "build_pattern_prompt",
    "CrochetAutoCorrector",
    "PatternSynthesisPipeline",
    "SvgChartGenerator",
    "ProfileVisualizer",
    "HtmlReportGenerator",
    "MarkdownExporter",
    "JsonExporter",
    "PdfExporter",
]


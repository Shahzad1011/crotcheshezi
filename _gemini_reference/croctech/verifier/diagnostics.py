"""
Diagnostic Codes, Severities, and Diagnostic Messages for CrocTech Verifier.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class DiagnosticSeverity(str, Enum):
    ERROR = "ERROR"       # Fatal defect (stitch count mismatch, broken graph, impossible topology)
    WARNING = "WARNING"   # Non-fatal warning (sudden tension change, slight ruffling)
    INFO = "INFO"         # Informational advice (best practices, ergonomics)


class DiagnosticCode(str, Enum):
    # Mathematical & Topological Stitch Invariants
    ERR_STITCH_COUNT_MISMATCH = "CROCTECH_E001"
    ERR_BASE_CONSUMPTION_MISMATCH = "CROCTECH_E002"
    ERR_DANGLING_STITCH = "CROCTECH_E003"
    ERR_INVALID_JOIN_STITCH = "CROCTECH_E004"
    ERR_NEGATIVE_STITCH_COUNT = "CROCTECH_E005"
    ERR_EMPTY_ROUND = "CROCTECH_E006"

    # Geometric & Curvature Defects
    WARN_HYPERBOLIC_RUFFLE = "CROCTECH_W101"
    WARN_SEVERE_PUCKERING = "CROCTECH_W102"
    WARN_ASYMMETRIC_INCREASES = "CROCTECH_W103"

    # Materials, Notions & Ergonomics
    ERR_UNDECLARED_MATERIAL = "CROCTECH_E201"
    WARN_HOOK_YARN_MISMATCH = "CROCTECH_W202"
    INFO_DESIGN_BEST_PRACTICE = "CROCTECH_I301"


@dataclass
class Diagnostic:
    """Detailed compiler diagnostic message."""
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    round_number: Optional[int] = None
    line_number: Optional[int] = None
    auto_repair_suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        loc = f"Round {self.round_number}: " if self.round_number is not None else ""
        fix = f" [Auto-Fix: {self.auto_repair_suggestion}]" if self.auto_repair_suggestion else ""
        return f"[{self.severity.value}] {self.code.value} - {loc}{self.message}{fix}"


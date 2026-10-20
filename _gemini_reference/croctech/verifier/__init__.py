"""
CrocTech Verifier Package.
Provides diagnostic rules, compiler-grade verification engine, and report structures.
"""

from croctech.verifier.diagnostics import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticSeverity,
)
from croctech.verifier.engine import (
    PatternVerifier,
    VerificationReport,
    RoundVerificationSummary,
    YarnUsageReport,
)

__all__ = [
    "Diagnostic",
    "DiagnosticCode",
    "DiagnosticSeverity",
    "PatternVerifier",
    "VerificationReport",
    "RoundVerificationSummary",
    "YarnUsageReport",
]


"""
JSON Schema Exporter for CrocTech.
Provides machine-readable structured JSON for databases, digital patterns, and automated manufacturing.
"""

import json
from dataclasses import asdict
from typing import Dict, Any
from croctech.core.models import PatternDef
from croctech.verifier.engine import VerificationReport


class JsonExporter:
    """Exports verified pattern into standardized machine-readable JSON."""

    @staticmethod
    def export(pattern: PatternDef, report: VerificationReport, indent: int = 2) -> str:
        """Serialize complete pattern and verification dossier to JSON."""
        data = {
            "schema_version": "croctech-v1.0",
            "title": pattern.title,
            "description": pattern.description,
            "terminology": pattern.terminology.value,
            "working_mode": pattern.working_mode.value,
            "hook_mm": pattern.hook_mm,
            "yarn": {
                "weight": pattern.yarn_weight,
                "composition": pattern.yarn_composition,
                "colors": pattern.colors
            },
            "verification": {
                "is_valid": report.is_valid,
                "error_count": report.error_count,
                "warning_count": report.warning_count,
                "total_stitches": report.dimensions.total_stitches,
                "total_rows": report.dimensions.total_rows,
                "graph_nodes": report.graph_node_count
            },
            "dimensions": {
                "finished_height_mm": report.dimensions.finished_height_mm,
                "max_diameter_mm": report.dimensions.max_diameter_mm,
                "has_folded_brim": report.dimensions.has_folded_brim,
                "folded_rows": report.dimensions.folded_rows_count,
                "pompom_height_mm": report.dimensions.pompom_height_mm
            },
            "yarn_usage": {
                c: {
                    "stitches": u.stitch_count,
                    "meters": u.meters_required,
                    "grams": u.grams_required
                } for c, u in report.yarn_usage.items()
            },
            "rounds": [
                {
                    "round_number": r.round_number,
                    "calculated_count": r.calculated_stitch_count,
                    "color": r.color,
                    "raw_text": r.raw_text
                } for r in pattern.rounds
            ]
        }
        return json.dumps(data, indent=indent)


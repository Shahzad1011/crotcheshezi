"""
Algorithmic Auto-Corrector and Repair Engine for CrocTech.
Automatically diagnoses and repairs common stitch distribution errors, stated count typos,
and missing notion declarations.
"""

from typing import List, Tuple
from croctech.core.types import StitchType
from croctech.core.models import PatternDef, RoundDef, StitchCommand, MaterialItem
from croctech.verifier.diagnostics import DiagnosticCode


class CrochetAutoCorrector:
    """Repairs AST patterns to ensure zero compilation errors."""

    @staticmethod
    def auto_repair(pattern: PatternDef) -> Tuple[PatternDef, List[str]]:
        """
        Applies mathematical repairs to pattern AST.
        Returns: (repaired_pattern, list_of_fixes_applied)
        """
        fixes: List[str] = []

        # 1. Ensure all assembly notions exist in materials
        mat_names = " ".join(m.name.lower() for m in pattern.materials)
        for step in pattern.assembly:
            low = step.instruction.lower()
            if "keychain" in low and "keychain" not in mat_names:
                pattern.materials.append(MaterialItem(category="hardware", name="Keychain clip / ring", detail="Keyring with lobster clasp"))
                mat_names += " keychain"
                fixes.append("Auto-added Keychain clip / ring to Materials list.")
            if "pompom" in low and "pompom" not in mat_names:
                pattern.materials.append(MaterialItem(category="notion", name="Mini Pompom (~15mm)", detail="Glued to crown"))
                mat_names += " pompom"
                fixes.append("Auto-added Mini Pompom to Materials list.")
            if "glue" in low and "glue" not in mat_names:
                pattern.materials.append(MaterialItem(category="adhesive", name="Craft / Fabric Glue", detail="For attaching pompom"))
                mat_names += " glue"
                fixes.append("Auto-added Craft Glue to Materials list.")

        # 2. Synchronize stated stitch counts with exact calculations
        prev_count = 0
        for r_idx, r in enumerate(pattern.rounds, start=1):
            if r_idx == 1:
                prev_count = r.calculated_stitch_count
                if r.stated_stitch_count != r.calculated_stitch_count:
                    fixes.append(f"Synchronized Round 1 stated count from {r.stated_stitch_count} to calculated [{r.calculated_stitch_count}].")
                    r.stated_stitch_count = r.calculated_stitch_count
            else:
                # If consumption is correct, ensure stated matches calculated
                if r.stated_stitch_count != r.calculated_stitch_count:
                    fixes.append(f"Fixed stated stitch count typo in Round {r.round_number}: {r.stated_stitch_count} -> [{r.calculated_stitch_count}].")
                    r.stated_stitch_count = r.calculated_stitch_count
                prev_count = r.calculated_stitch_count

        return pattern, fixes


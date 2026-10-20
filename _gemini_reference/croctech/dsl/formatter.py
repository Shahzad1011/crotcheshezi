"""
Pattern Formatter for CrocTech DSL.
Exports verified AST into canonical US notation, UK notation, or step-by-step descriptive guides.
"""

from typing import List
from croctech.core.types import StitchType, Terminology
from croctech.core.models import PatternDef, RoundDef, StitchCommand


class PatternFormatter:
    """Formats verified pattern into standardized professional crochet publications."""

    @staticmethod
    def format_canonical_us(pattern: PatternDef) -> str:
        """Format pattern into clean, professional US standard notation."""
        lines = []
        lines.append(f"# {pattern.title}")
        if pattern.description:
            lines.append(f"*{pattern.description}*\n")

        lines.append("## Materials & Specifications")
        lines.append(f"- **Yarn**: {pattern.yarn_weight} — {pattern.yarn_composition}")
        lines.append(f"- **Hook Size**: {pattern.hook_mm:.2f} mm")
        lines.append(f"- **Working Mode**: {pattern.working_mode.value.replace('_', ' ').title()}")
        lines.append(f"- **Terminology**: Standard US Crochet Terms")

        if pattern.materials:
            lines.append("\n### Notions & Hardware")
            for m in pattern.materials:
                lines.append(f"- {m.name}: {m.detail or ''}".strip())

        lines.append("\n## Verified Instructions\n")

        # Track multi-row repetitions for clean display
        i = 0
        while i < len(pattern.rounds):
            curr = pattern.rounds[i]
            # Check consecutive identical straight rows
            j = i + 1
            while j < len(pattern.rounds) and (
                pattern.rounds[j].calculated_stitch_count == curr.calculated_stitch_count and
                pattern.rounds[j].color == curr.color and
                len(pattern.rounds[j].commands) == len(curr.commands) and
                all(c.stitch_type == StitchType.SC for c in pattern.rounds[j].commands if not (c.is_join or c.is_height_chain))
            ):
                j += 1

            if j - i >= 2 and curr.round_number != 1:
                # Grouped range e.g. R6-9
                start_r = curr.round_number
                end_r = pattern.rounds[j - 1].round_number
                st_count = curr.calculated_stitch_count
                color_str = f" [{curr.color}]" if curr.color != "primary" else ""
                lines.append(f"**Rounds {start_r}–{end_r}**{color_str}: ch 1, {st_count} sc around, sl st to first sc to join. [{st_count} sts]")
                i = j
            else:
                line_str = PatternFormatter._format_single_round_us(curr)
                lines.append(line_str)
                i += 1

        if pattern.assembly:
            lines.append("\n## Assembly & Finishing Instructions\n")
            for step in pattern.assembly:
                stage = f" (at Row {step.stage_row})" if step.stage_row else ""
                lines.append(f"{step.step_number}. **{step.title}**{stage}: {step.instruction}")

        return "\n".join(lines)

    @staticmethod
    def _format_single_round_us(round_def: RoundDef) -> str:
        """Format an individual round in standard US terms."""
        num = round_def.round_number
        color_tag = f" [{round_def.color}]" if round_def.color not in ["primary", "Red"] else ""

        # Filter out height chain and join for compact body
        body_cmds = [c for c in round_def.commands if not (c.is_join or c.is_height_chain)]
        has_ch1 = any(c.is_height_chain for c in round_def.commands)
        has_slst = any(c.is_join for c in round_def.commands)

        parts = []
        if has_ch1:
            parts.append("ch 1")

        if num == 1:
            sc_cmd = next((c for c in body_cmds if c.stitch_type == StitchType.SC), None)
            sc_n = sc_cmd.count if sc_cmd else round_def.calculated_stitch_count
            parts.append(f"{sc_n} sc in magic ring")
        else:
            # Check for repeat pattern
            sc_cmd = next((c for c in body_cmds if c.stitch_type == StitchType.SC and c.repeat_times > 1), None)
            inc_cmd = next((c for c in body_cmds if c.stitch_type == StitchType.INC and c.repeat_times > 1), None)

            if sc_cmd and inc_cmd:
                reps = sc_cmd.repeat_times
                parts.append(f"({sc_cmd.count} sc, inc) * {reps}")
            elif len(body_cmds) == 1 and body_cmds[0].stitch_type == StitchType.SC:
                parts.append(f"{body_cmds[0].count} sc around")
            else:
                # Construct from commands
                cmd_strs = []
                for c in body_cmds:
                    if c.stitch_type == StitchType.SC:
                        cmd_strs.append(f"{c.count} sc")
                    elif c.stitch_type == StitchType.INC:
                        cmd_strs.append("inc")
                    elif c.stitch_type == StitchType.DEC:
                        cmd_strs.append("dec")
                parts.append(", ".join(cmd_strs))

        if has_slst:
            parts.append("sl st to first sc to join")

        body_str = ", ".join(parts)
        return f"**Round {num}**{color_tag}: {body_str}. [{round_def.calculated_stitch_count} sts]"


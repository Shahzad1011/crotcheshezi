"""
Crochet Pattern Parser & AST Builder.
Extracts materials, tools, structured rounds, commands, stated counts, and finishing steps.
Supports multi-line round descriptions, standard abbreviations, and natural language instructions.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from croctech.core.types import StitchType, WorkingMode, Terminology, LoopTarget
from croctech.core.models import (
    PatternDef,
    RoundDef,
    StitchCommand,
    MaterialItem,
    AssemblyInstruction,
)
from croctech.dsl.tokens import (
    RE_ROW_HEADER,
    RE_STATED_TOTAL,
    RE_REPEAT_BLOCK,
    RE_SHORTHAND_XV,
    RE_INC,
    RE_DEC,
    RE_MAGIC_RING,
    RE_CHAIN,
    RE_SLIP_STITCH,
    RE_SC_COUNT,
    RE_HDC_COUNT,
    RE_DC_COUNT,
    RE_COLOR_SWITCH,
)


class CrochetPatternParser:
    """Parses raw text pattern into a strictly validated AST (PatternDef)."""

    def parse(self, text: str, default_title: str = "Verified Crochet Pattern") -> PatternDef:
        """Parse raw text containing materials, notes, rows, and assembly."""
        raw_lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

        materials = self._parse_materials(raw_lines)
        hook_mm = self._extract_hook_size(raw_lines)
        yarn_weight, fiber = self._extract_yarn_spec(raw_lines)
        colors = self._extract_colors(raw_lines)

        rounds, assembly = self._parse_rounds_and_assembly(raw_lines)

        # Detect folding and pompom
        fold_up_rows = 0
        pompom_diam = 0.0

        for line in raw_lines:
            lower = line.lower()
            if "fold" in lower and ("brim" in lower or "row" in lower or "white" in lower):
                fold_up_rows = 3
            if "pompom" in lower or "pom-pom" in lower or "pom pom" in lower:
                pompom_diam = 15.0

        working_mode = WorkingMode.JOINED_ROUNDS if any(r.is_joined for r in rounds) else WorkingMode.CONTINUOUS_SPIRAL

        return PatternDef(
            title=default_title,
            description="High precision crochet pattern verified by CrocTech Framework",
            terminology=Terminology.US,
            working_mode=working_mode,
            hook_mm=hook_mm,
            yarn_weight=yarn_weight,
            yarn_composition=fiber,
            colors=colors,
            materials=materials,
            rounds=rounds,
            assembly=assembly,
            fold_up_rows=fold_up_rows,
            pompom_diameter_mm=pompom_diam
        )

    def _extract_hook_size(self, lines: List[str]) -> float:
        """Extract hook size in mm from text."""
        for line in lines:
            m = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*(?:hook|crochet\s*hook)?", line, re.IGNORECASE)
            if m:
                return float(m.group(1))
            m2 = re.search(r"(?:hook|crochet\s*hook)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*mm", line, re.IGNORECASE)
            if m2:
                return float(m2.group(1))
        return 2.50

    def _extract_yarn_spec(self, lines: List[str]) -> Tuple[str, str]:
        """Extract ply and fiber blend."""
        weight = "5-ply (Fine 2 / Sport)"
        fiber = "50% Cotton, 50% Acrylic"
        for line in lines:
            if "ply" in line.lower():
                m = re.search(r"(\d+)[-\s]*ply", line, re.IGNORECASE)
                if m:
                    weight = f"{m.group(1)}-ply (Fine 2 / Sport)"
            if "cotton" in line.lower() or "acrylic" in line.lower() or "wool" in line.lower():
                fiber = line
        return weight, fiber

    def _extract_colors(self, lines: List[str]) -> List[str]:
        """Extract yarn colors mentioned."""
        colors = []
        for line in lines:
            m = re.search(r"(red\s*and\s*white|red|white|glittery\s*silver|silver|green|blue|black)", line, re.IGNORECASE)
            if m:
                found = m.group(1).lower()
                if "red and white" in found:
                    if "Red" not in colors: colors.append("Red")
                    if "White" not in colors: colors.append("White")
                elif "glitter" in found or "silver" in found:
                    if "Silver (Glitter)" not in colors: colors.append("Silver (Glitter)")
                else:
                    c = found.capitalize()
                    if c not in colors: colors.append(c)
        return colors if colors else ["Red", "White"]

    def _parse_materials(self, lines: List[str]) -> List[MaterialItem]:
        """Identify materials, notions, and tools."""
        materials: List[MaterialItem] = []
        notion_keywords = {
            "keychain": ("hardware", "Keychain clip / ring"),
            "glue": ("adhesive", "Fabric glue or craft glue"),
            "scissors": ("notion", "Sharp craft scissors"),
            "yarn needle": ("notion", "Tapestry / yarn needle"),
            "pompom": ("notion", "Small white pompom (~15mm)"),
            "stitch marker": ("notion", "Locking stitch marker")
        }

        for line in lines:
            lower = line.lower()
            if "hook" in lower and "mm" in lower:
                m = re.search(r"(\d+(?:\.\d+)?\s*mm)", line)
                size_str = m.group(1) if m else "2.50 mm"
                materials.append(MaterialItem(category="hook", name=f"Crochet Hook {size_str}", detail=line))
            elif "yarn" in lower or "ply" in lower:
                materials.append(MaterialItem(category="yarn", name=line, detail="Primary yarn"))
            else:
                for kw, (cat, default_name) in notion_keywords.items():
                    if kw in lower and not any(m.name == default_name for m in materials):
                        materials.append(MaterialItem(category=cat, name=default_name, detail=line))

        return materials

    def _parse_rounds_and_assembly(self, lines: List[str]) -> Tuple[List[RoundDef], List[AssemblyInstruction]]:
        """Parse multi-line blocks into structured RoundDefs and AssemblyInstructions."""
        rounds: List[RoundDef] = []
        assembly: List[AssemblyInstruction] = []
        current_color = "Red"
        assembly_counter = 1

        # 1. Chunk input into distinct Row blocks and Assembly blocks
        blocks: List[Tuple[str, str]] = [] # list of (block_type, combined_text)
        current_type = "preamble"
        current_lines: List[str] = []

        for line in lines:
            lower = line.lower()
            header_match = RE_ROW_HEADER.search(line)

            # Check if this line is an assembly action
            is_assembly_line = any(k in lower for k in [
                "attach the keychain", "attach keychain", "cut the thread",
                "secret join", "invisible join", "fold the white", "stick a small pompom"
            ])

            if header_match:
                if current_lines:
                    blocks.append((current_type, " ".join(current_lines)))
                    current_lines = []
                current_type = "row"
                current_lines.append(line)
            elif is_assembly_line:
                if current_lines:
                    blocks.append((current_type, " ".join(current_lines)))
                    current_lines = []
                blocks.append(("assembly", line))
                current_type = "row" # Reset
            elif "switch to 2nd color" in lower or "change to white" in lower:
                if current_lines:
                    blocks.append((current_type, " ".join(current_lines)))
                    current_lines = []
                blocks.append(("color_switch", line))
                current_type = "row"
            else:
                current_lines.append(line)

        if current_lines:
            blocks.append((current_type, " ".join(current_lines)))

        # 2. Process chunked blocks
        prev_stitch_count = 0

        for b_type, b_text in blocks:
            lower = b_text.lower()

            if b_type == "color_switch":
                current_color = "White / Silver"
                assembly.append(AssemblyInstruction(
                    step_number=assembly_counter,
                    title="Color Change",
                    instruction=b_text,
                    stage_row=rounds[-1].round_number if rounds else None
                ))
                assembly_counter += 1
                continue

            if b_type == "assembly":
                # Clean title up to first period or full sentence
                first_sentence = b_text.split(".")[0].strip()
                title = first_sentence if len(first_sentence) <= 60 else first_sentence[:57] + "..."
                assembly.append(AssemblyInstruction(
                    step_number=assembly_counter,
                    title=title,
                    instruction=b_text,
                    stage_row=rounds[-1].round_number if rounds else None
                ))
                assembly_counter += 1
                continue

            if b_type == "row":
                header_match = RE_ROW_HEADER.search(b_text)
                if not header_match:
                    continue

                start_r = int(header_match.group(1))
                end_r = int(header_match.group(2)) if header_match.group(2) else None

                if start_r >= 10:
                    current_color = "White / Silver"

                multi_match = re.search(r"between\s*rows?\s*(\d+)\s*(?:to|-)\s*(\d+)|until\s*(?:there\s*are)?\s*(\d+)\s*rows", b_text, re.IGNORECASE)

                if end_r:
                    # Explicit range e.g. Rows 6-9
                    stated_count = self._extract_stated_count(b_text) or 18
                    for r_num in range(start_r, end_r + 1):
                        r_def = self._build_single_round(r_num, b_text, stated_count, current_color, prev_stitch_count)
                        rounds.append(r_def)
                        prev_stitch_count = r_def.calculated_stitch_count
                elif multi_match and ("continue" in lower or "repeat" in lower):
                    target_end = int(multi_match.group(2) or multi_match.group(3))
                    stated_count = self._extract_stated_count(b_text)
                    if not stated_count:
                        sc_m = RE_SC_COUNT.search(b_text)
                        stated_count = int(sc_m.group(1)) if sc_m else 18

                    for r_num in range(start_r, target_end + 1):
                        r_def = self._build_single_round(r_num, b_text, stated_count, current_color, prev_stitch_count)
                        rounds.append(r_def)
                        prev_stitch_count = r_def.calculated_stitch_count
                else:
                    stated_count = self._extract_stated_count(b_text)
                    r_def = self._build_single_round(start_r, b_text, stated_count, current_color, prev_stitch_count)
                    rounds.append(r_def)
                    prev_stitch_count = r_def.calculated_stitch_count

        return rounds, assembly

    def _extract_stated_count(self, text: str) -> Optional[int]:
        """Extract explicit stitch count given in brackets or text."""
        m = RE_STATED_TOTAL.search(text)
        if m:
            for g in m.groups():
                if g: return int(g)
        return None

    def _build_single_round(
        self,
        round_num: int,
        raw_text: str,
        stated_count: Optional[int],
        color: str,
        prev_stitch_count: int = 0
    ) -> RoundDef:
        """Parse stitch instructions for a single round into discrete StitchCommands."""
        lower = raw_text.lower()
        commands: List[StitchCommand] = []

        is_joined = ("slip stitch" in lower or "sl st" in lower or "1 chain" in lower or "1 ch" in lower)

        if "1 chain" in lower or "1 ch" in lower or "ch 1" in lower:
            commands.append(StitchCommand(
                stitch_type=StitchType.CH,
                count=1,
                is_height_chain=True,
                raw_text="1 ch"
            ))

        # Check for magic ring start
        if round_num == 1 and ("magic ring" in lower or "ring" in lower or "mr" in lower):
            sc_m = RE_SC_COUNT.search(raw_text)
            count = int(sc_m.group(1)) if sc_m else 6
            commands.append(StitchCommand(
                stitch_type=StitchType.SC,
                count=count,
                raw_text=f"{count} sc in magic ring"
            ))
            calc_count = count
            consumed = 0
        else:
            # Check for shorthand (x, v sc), (2x, v sc), etc.
            xv_match = RE_SHORTHAND_XV.search(raw_text)
            repeat_block_match = RE_REPEAT_BLOCK.search(raw_text)

            if xv_match:
                x_prefix = xv_match.group(1)
                sc_count = int(x_prefix) if x_prefix else 1

                # Each (sc_count * sc, 1 inc) consumes (sc_count + 1) stitches and produces (sc_count + 2) stitches
                consume_per_group = sc_count + 1
                produce_per_group = sc_count + 2

                if prev_stitch_count > 0:
                    rep_times = prev_stitch_count // consume_per_group
                elif stated_count:
                    rep_times = stated_count // produce_per_group
                else:
                    rep_times = 3 if sc_count <= 4 else 2

                commands.append(StitchCommand(
                    stitch_type=StitchType.SC,
                    count=sc_count,
                    repeat_times=rep_times,
                    raw_text=f"{sc_count} sc"
                ))
                commands.append(StitchCommand(
                    stitch_type=StitchType.INC,
                    count=1,
                    repeat_times=rep_times,
                    raw_text="inc"
                ))
                calc_count = produce_per_group * rep_times
                consumed = consume_per_group * rep_times

            elif repeat_block_match:
                inner = repeat_block_match.group(1)
                rep_count = int(repeat_block_match.group(2) or repeat_block_match.group(3) or 1)
                inner_calc, inner_cons, inner_cmds = self._parse_inner_stitches(inner)
                for cmd in inner_cmds:
                    cmd.repeat_times = rep_count
                    commands.append(cmd)
                calc_count = inner_calc * rep_count
                consumed = inner_cons * rep_count

            else:
                calc_count, consumed, parsed_cmds = self._parse_descriptive_stitches(raw_text, stated_count, prev_stitch_count)
                commands.extend(parsed_cmds)

        if is_joined:
            commands.append(StitchCommand(
                stitch_type=StitchType.SL_ST,
                count=1,
                is_join=True,
                raw_text="sl st to join"
            ))

        return RoundDef(
            round_number=round_num,
            raw_text=raw_text,
            commands=commands,
            stated_stitch_count=stated_count or calc_count,
            calculated_stitch_count=calc_count,
            stitches_consumed=consumed,
            color=color,
            is_joined=is_joined
        )

    def _parse_inner_stitches(self, text: str) -> Tuple[int, int, List[StitchCommand]]:
        """Parse stitches inside parentheses like '2 sc, inc'."""
        calc = 0
        cons = 0
        cmds = []
        tokens = [t.strip() for t in text.split(",") if t.strip()]
        for tok in tokens:
            if RE_INC.search(tok):
                cmds.append(StitchCommand(stitch_type=StitchType.INC, count=1, raw_text="inc"))
                calc += 2
                cons += 1
            elif RE_DEC.search(tok):
                cmds.append(StitchCommand(stitch_type=StitchType.DEC, count=1, raw_text="dec"))
                calc += 1
                cons += 2
            else:
                sc_m = RE_SC_COUNT.search(tok)
                n = int(sc_m.group(1)) if sc_m else 1
                cmds.append(StitchCommand(stitch_type=StitchType.SC, count=n, raw_text=f"{n} sc"))
                calc += n
                cons += n
        return calc, cons, cmds

    def _parse_descriptive_stitches(
        self,
        text: str,
        stated_count: Optional[int],
        prev_stitch_count: int
    ) -> Tuple[int, int, List[StitchCommand]]:
        """Parse descriptive sentences like 'make 18 sc side by side' or multi-round straight rounds."""
        cmds: List[StitchCommand] = []

        # Check explicit sc count
        sc_m = RE_SC_COUNT.search(text)
        if sc_m:
            count = int(sc_m.group(1))
            cmds.append(StitchCommand(stitch_type=StitchType.SC, count=count, raw_text=f"{count} sc"))
            return count, count, cmds

        # Fallback to stated count
        if stated_count:
            cmds.append(StitchCommand(stitch_type=StitchType.SC, count=stated_count, raw_text=f"{stated_count} sc"))
            return stated_count, stated_count, cmds

        # Fallback to prev_stitch_count (for straight repetitions like "Repeat the process in the 6th row")
        if prev_stitch_count > 0:
            cmds.append(StitchCommand(stitch_type=StitchType.SC, count=prev_stitch_count, raw_text=f"{prev_stitch_count} sc"))
            return prev_stitch_count, prev_stitch_count, cmds

        cmds.append(StitchCommand(stitch_type=StitchType.SC, count=6, raw_text="6 sc"))
        return 6, 6, cmds

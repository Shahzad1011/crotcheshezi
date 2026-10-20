"""
Pydantic Data Models for Crochet Patterns, Materials, and Verifications.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from croctech.core.types import StitchType, WorkingMode, Terminology, LoopTarget


class MaterialItem(BaseModel):
    """Specification of a tool, yarn, notion, or hardware."""
    category: str = Field(description="yarn, hook, notion, hardware, adhesive")
    name: str
    detail: Optional[str] = None
    color: Optional[str] = None
    quantity: Optional[str] = "1"


class StitchCommand(BaseModel):
    """Atomic crochet instruction step within a row."""
    stitch_type: StitchType
    count: int = 1               # Number of times this stitch is made
    repeat_times: int = 1        # Number of times repeat group is executed
    loop_target: LoopTarget = LoopTarget.BOTH
    is_join: bool = False        # e.g., slip stitch to first stitch
    is_height_chain: bool = False # e.g., ch 1 at start of joined round
    into_same_stitch: bool = False # e.g., work in base of slip stitch
    raw_text: Optional[str] = None


class RoundDef(BaseModel):
    """Complete specification of a single round or row."""
    round_number: int
    raw_text: str
    commands: List[StitchCommand] = Field(default_factory=list)
    stated_stitch_count: Optional[int] = None
    calculated_stitch_count: int = 0
    stitches_consumed: int = 0
    color: str = "primary"
    notes: Optional[str] = None
    is_joined: bool = True
    repeat_start_row: Optional[int] = None # For multi-row repeat definitions like "Rows 6-9"
    repeat_end_row: Optional[int] = None


class AssemblyInstruction(BaseModel):
    """Step-by-step assembly, hardware attachment, or finishing note."""
    step_number: int
    title: str
    instruction: str
    stage_row: Optional[int] = None # Row at which this occurs, e.g. Row 5 for keychain clip


class PatternDef(BaseModel):
    """Complete Crochet Pattern definition with all metadata and structural rows."""
    title: str
    description: Optional[str] = None
    terminology: Terminology = Terminology.US
    working_mode: WorkingMode = WorkingMode.JOINED_ROUNDS
    hook_mm: float = 2.50
    yarn_weight: str = "5-ply (Fine 2 / Sport)"
    yarn_composition: str = "50% Cotton, 50% Acrylic"
    colors: List[str] = Field(default_factory=lambda: ["Red", "White"])
    materials: List[MaterialItem] = Field(default_factory=list)
    rounds: List[RoundDef] = Field(default_factory=list)
    assembly: List[AssemblyInstruction] = Field(default_factory=list)
    fold_up_rows: int = 0
    pompom_diameter_mm: float = 0.0
    tags: List[str] = Field(default_factory=list)


"""Typed, schema-constrained representation of a crochet pattern.

These models carry only *design intent* (which operations in what order). All
counts are computed by the engine, never authored, so nothing can silently
hallucinate a stitch total. A pattern is a list of Components (parts), each
either 'verified' (stitch-conservation checked rounds/rows) or 'manual'
(decorative/free-form steps like petals, puff stitches, assembly).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Each stitch operation's effect on the working stitch count.
#   consume = counted stitches this op works into
#   produce   = stitches it leaves on the work
_OP_EFFECTS: dict[str, tuple[int, int]] = {
    "sc": (1, 1),    # single crochet
    "dc": (1, 1),    # double crochet (same stitch-count effect; different height)
    "inc": (1, 2),   # two stitches into one ("v")
    "dec": (2, 1),   # two together ("d")
    "sk": (1, 0),    # skip a stitch (a decrease in turning rows)
}


class StitchOp(BaseModel):
    """A run of one stitch kind within a round's instruction sequence."""

    kind: str
    count: int = 1

    @field_validator("kind")
    @classmethod
    def _kind_valid(cls, v: str) -> str:
        if v not in _OP_EFFECTS:
            raise ValueError(f"unknown stitch kind {v!r}; expected one of {sorted(_OP_EFFECTS)}")
        return v

    @field_validator("count")
    @classmethod
    def _count_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("count must be >= 1")
        return v

    @property
    def consume(self) -> int:
        return _OP_EFFECTS[self.kind][0] * self.count

    @property
    def produce(self) -> int:
        return _OP_EFFECTS[self.kind][1] * self.count


class RoundSpec(BaseModel):
    """One round/row: leading segment + a repeated cycle + trailing segment.

    `foundation` marks a fresh start (magic ring, or working into an edge) so the
    engine does not require it to consume the previous count. `flat` marks a
    back-and-forth turning row (for rendering). `work` groups sub-pieces.
    """

    index: int = Field(ge=1)
    label: str | None = None
    color: str | None = None
    starts_from: Literal["magic_ring", "edge", "chain", "sl_knot"] = "magic_ring"
    spec_text: str | None = Field(
        default=None,
        description="The author's own wording for this row, quoted verbatim in the output. "
                    "The engine still re-derives the count from the ops below and refuses to "
                    "print the row if the two disagree.",
    )
    foundation: bool = False
    flat: bool = False
    fasten_off: bool = Field(
        default=False,
        description="Last row of a piece: it is worked to the end and the yarn is cut, so the "
                    "working text must not tell the maker to turn and carry on.",
    )
    start_ch: bool = True
    join_sl: bool = True
    leading: list[StitchOp] = Field(default_factory=list)
    cycle: list[StitchOp] = Field(default_factory=list)
    repeats: int = Field(default=1, ge=1)
    trailing: list[StitchOp] = Field(default_factory=list)
    declared_total: int = Field(ge=0)  # the total the author CLAIMS -- engine re-checks it
    notes: list[str] = Field(default_factory=list)

    def expand(self) -> list[StitchOp]:
        seq: list[StitchOp] = list(self.leading)
        for _ in range(self.repeats):
            seq.extend(self.cycle)
        seq.extend(self.trailing)
        return seq

    @property
    def repeat_notation(self) -> str:
        parts: list[str] = []
        for op in self.cycle:
            token = {"sc": "x", "dc": "D", "inc": "v", "dec": "d", "sk": "sk"}[op.kind]
            parts.append(token if op.count == 1 else f"{op.count}{token}")
        return ", ".join(parts)


class Block(BaseModel):
    """A group of rows worked as one unit and repeated a fixed number of times.

    This exists so multiplicity is *checkable* rather than a sentence. A block
    that works N instances, each consuming `consumes_base_stitches` from the
    foundation ring, must exactly exhaust that ring -- the arithmetic a
    per-row audit cannot see, because each instance legitimately starts fresh.
    """

    name: str
    instances: int = Field(ge=1)
    rows: list[RoundSpec]
    consumes_base_stitches: int | None = Field(
        default=None, ge=1,
        description="Stitches of the previous round's total that ONE instance works into.",
    )

    @property
    def total_base_consumed(self) -> int:
        return self.instances * (self.consumes_base_stitches or 0)


class Component(BaseModel):
    """A named part of the pattern. 'verified' parts are stitch-conservation
    checked; 'manual' parts are described steps (petals, puff, assembly)."""

    name: str
    quantity: int = Field(default=1, ge=1)
    role: Literal["part", "operation"] = "part"
    hook: float | None = Field(default=None, description="Hook assigned to THIS part.")
    blocks: list[Block] = Field(default_factory=list)
    kind: Literal["verified", "manual"] = "verified"
    rounds: list[RoundSpec] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @property
    def all_rows(self) -> list[RoundSpec]:
        """Every row in the order the engine audits it: plain rounds first, then
        each block instance expanded. Charts pair this with the audits by index."""
        out = list(self.rounds)
        for b in self.blocks:
            for _ in range(b.instances):
                out.extend(b.rows)
        return out


class Material(BaseModel):
    yarn: str
    hook_mm: float = Field(gt=0)
    hooks: list[float] = Field(default_factory=list)  # additional hook sizes
    colors: list[str] = Field(default_factory=list)
    notions: list[str] = Field(default_factory=list)
    meters_per_gram: float | None = Field(
        default=None, gt=0,
        description="Yarn density (m/g) for weight estimate; e.g. 5-ply ~3.2 m/g. Estimate.",
    )


class Gauge(BaseModel):
    stitches_per_10cm: float = Field(gt=0)
    rows_per_10cm: float = Field(gt=0)
    calibrated: bool = False
    note: str = "Reference estimate. Swatch-calibrate on the stated hook/yarn for exactness."


class Pattern(BaseModel):
    name: str
    item_type: str
    description: str = ""
    material: Material
    gauge: Gauge | None = None
    abbreviations: dict[str, str] = Field(default_factory=dict)
    provenance: str = Field(
        default="",
        description="Where this encoding came from, so a reader can tell source from fixture.",
    )
    undefined_terms: list[str] = Field(
        default_factory=list,
        description="Stitch terms the source uses but never defines. Surfaced as open "
                    "questions instead of being quietly explained away.",
    )
    components: list[Component] = Field(default_factory=list)
    rounds: list[RoundSpec] = Field(default_factory=list)  # legacy convenience input

    @model_validator(mode="after")
    def _normalize(self) -> Pattern:
        if not self.components and self.rounds:
            self.components = [Component(name=self.item_type.title(), rounds=self.rounds)]
        return self

    @property
    def verified_rounds(self) -> list[RoundSpec]:
        """Every auditable row, including one representative row per block instance."""
        out: list[RoundSpec] = []
        for c in self.components:
            if c.kind != "verified":
                continue
            out.extend(c.rounds)
            for b in c.blocks:
                out.extend(b.rows)
        return out

    @property
    def listed_hooks(self) -> list[float]:
        return [self.material.hook_mm, *self.material.hooks]

    @property
    def unassigned_hooks(self) -> list[float]:
        """Hooks listed in Materials that no part claims. A 1.0 mm hook that appears
        nowhere in the instructions is a gap in the source, not a free detail."""
        used = {c.hook for c in self.components if c.hook}
        return [h for h in self.listed_hooks if h not in used]


def parse_repeat(text: str) -> list[StitchOp]:
    """Parse '(x, v)'-style repeat notation into a cycle of StitchOps.

    Tokens: 'x'/'sc' single crochet, 'D'/'dc' double crochet, 'v'/'inc' increase,
    'd'/'dec' decrease, 'sk' skip. A leading integer multiplies: '3x' -> 3 sc.
    """
    alias = {"x": "sc", "sc": "sc", "D": "dc", "dc": "dc",
             "v": "inc", "inc": "inc", "d": "dec", "dec": "dec", "sk": "sk"}
    ops: list[StitchOp] = []
    for raw in text.replace("(", "").replace(")", "").split(","):
        tok = raw.strip()
        if not tok:
            continue
        num = ""
        letters = ""
        for ch in tok:
            if ch.isdigit():
                num += ch
            else:
                letters += ch
        key = letters if letters in alias else letters.lower()
        if key not in alias:
            raise ValueError(f"unknown token {tok!r} in repeat notation {text!r}")
        ops.append(StitchOp(kind=alias[key], count=int(num) if num else 1))
    return ops

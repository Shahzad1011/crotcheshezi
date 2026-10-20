"""Typed, schema-constrained representation of a crochet pattern.

These models carry only *design intent* (which operations in what order). All
counts are computed by the engine, never authored.

Two rules shape the schema, both learned the hard way from adversarial drafts:

1. **No per-row escape flags.** A row does not get to claim it is a fresh start;
   the engine grants that from its position. `starts_from` describes *how* a row
   that the engine has already accepted as a fresh start is opened.
2. **Trusted fields are not model-settable.** Anything a provider's JSON can
   write is untrusted by definition. A gauge's swatch attestation therefore lives
   in `Gauge.attested_by`, which the draft path never reads, and `calibrated` is
   derived from it rather than stored beside it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Where a piece of instruction text came from. Renderers show this, so a reader
# can tell the author's words from the framework's expansion of them.
Origin = Literal["source", "inferred", "added"]

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

# Physical footprint of each op, in base-stitch widths and heights, so geometry
# questions ("does this round ruffle?") are expressible at all. Relative, not
# centimetres: centimetres need a gauge, and a gauge may not be invented.
_OP_GEOMETRY: dict[str, tuple[float, float]] = {
    "sc": (1.0, 1.0),
    "dc": (1.0, 1.9),
    "inc": (1.0, 1.0),
    "dec": (1.0, 1.0),
    "sk": (1.0, 0.0),
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

    @property
    def width(self) -> float:
        """Base-stitch widths this op occupies."""
        return _OP_GEOMETRY[self.kind][0] * self.count

    @property
    def height(self) -> float:
        """Base-stitch heights this op adds."""
        return _OP_GEOMETRY[self.kind][1] * self.count


class RoundSpec(BaseModel):
    """One round/row: leading segment + a repeated cycle + trailing segment.

    `starts_from` says how the row is opened *when the engine has already granted
    that it starts fresh* (first row of a part, the row after a fasten-off, or the
    opening row of a block instance). A row in the middle of a run cannot opt out
    of consuming the row below it by declaring a flag -- that is the escape hatch
    that let a draft jump from 6 stitches to 50 and still print "0 errors".
    """

    index: int = Field(ge=1)
    label: str | None = None
    color: str | None = None
    starts_from: Literal["magic_ring", "edge", "chain", "sl_knot"] | None = Field(
        default=None,
        description="How a legitimate fresh start is opened. None means this row works into "
                    "the row below it.",
    )
    origin: Origin = Field(
        default="source",
        description="Where `spec_text` came from: 'source' = quoted from the author's pattern, "
                    "'inferred' = the author's wording plus a gap the framework filled, 'added' = "
                    "written by the framework. Rendered as a tag, never folded into the wording.",
    )
    spec_text: str | None = Field(
        default=None,
        description="The author's own wording for this row, quoted verbatim in the output. "
                    "The engine still re-derives the count from the ops below and refuses to "
                    "print the row if the two disagree.",
    )
    flat: bool = False
    fasten_off: bool = Field(
        default=False,
        description="Last row of a piece: it is worked to the end and the yarn is cut, so the "
                    "working text must not tell the maker to turn and carry on.",
    )
    start_ch: bool = True
    join_sl: bool = Field(
        default=False,
        description="Close the round with a slip stitch in the working text. A join is a "
                    "decision the author makes, never something a row inherits: defaulting this "
                    "to True silently sewed a seam into every continuous-spiral round.",
    )
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
    def claims_fresh_start(self) -> bool:
        """The row says it opens new stitches instead of working into a row below."""
        return self.starts_from is not None

    @property
    def repeat_notation(self) -> str:
        parts: list[str] = []
        for op in self.cycle:
            token = {"sc": "x", "dc": "D", "inc": "v", "dec": "d", "sk": "sk"}[op.kind]
            parts.append(token if op.count == 1 else f"{op.count}{token}")
        return ", ".join(parts)


class Step(BaseModel):
    """One instruction line of a non-counted part (sewing, assembly, a petal).

    Provenance is per line, not per document: a framework-written technique and the
    author's own sentence must never share a paragraph unmarked.
    """

    text: str
    origin: Origin = "source"
    why: str | None = Field(
        default=None,
        description="For 'inferred'/'added' lines: the reason the framework wrote it, shown "
                    "beside the tag.",
    )

    def __init__(self, text: str, origin: Origin = "source",
                 why: str | None = None) -> None:
        super().__init__(text=text, origin=origin, why=why)


def _unique_indices(rows: list[RoundSpec], where: str) -> None:
    seen: dict[int, int] = {}
    for r in rows:
        seen[r.index] = seen.get(r.index, 0) + 1
    dupes = sorted(i for i, n in seen.items() if n > 1)
    if dupes:
        raise ValueError(
            f"{where}: duplicate row index/indices {dupes}. Totals, audits and charts all key "
            f"on the index, so a collision silently renumbers the pattern.")


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

    @model_validator(mode="after")
    def _rows_are_addressable(self) -> Block:
        _unique_indices(self.rows, f"Block {self.name}")
        if self.rows and not self.rows[0].claims_fresh_start:
            raise ValueError(
                f"Block {self.name}: the first row of an instance must say how the yarn is "
                f"joined (starts_from), because each instance starts on its own base stitches.")
        if len(self.rows) > 1 and any(r.claims_fresh_start for r in self.rows[1:]):
            raise ValueError(
                f"Block {self.name}: only the opening row of an instance may start fresh; the "
                f"rest thread into it.")
        return self

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
    hook_origin: Origin = Field(
        default="source",
        description="Whether the author assigned this hook or the framework paired it.",
    )
    build_direction: Literal["from_tip", "from_base"] | None = Field(
        default=None,
        description="Which end of the object row 1 is. Without it the engine's row stack cannot "
                    "be drawn as a silhouette, because work order and up/down are not the same "
                    "fact. None means 'unknown -- do not claim a shape'.",
    )
    blocks: list[Block] = Field(default_factory=list)
    kind: Literal["verified", "manual"] = "verified"
    rounds: list[RoundSpec] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _rows_are_addressable(self) -> Component:
        _unique_indices(self.rounds, f"Component {self.name}")
        if self.rounds and not self.rounds[0].claims_fresh_start:
            raise ValueError(
                f"Component {self.name}: row 1 must say how the work is opened (starts_from) -- "
                f"nothing can be worked into a row that does not exist.")
        if any(r.claims_fresh_start for r in self.rounds[1:]):
            bad = [r.index for r in self.rounds[1:]
                   if r.claims_fresh_start and id(r) not in self.fresh_starts]
            if bad:
                raise ValueError(
                    f"Component {self.name}: rows {bad} claim a fresh start mid-run. A new "
                    f"foundation may only follow a fasten-off; otherwise it abandons the "
                    f"stitches the previous row made.")
        return self

    @property
    def fresh_starts(self) -> set[int]:
        """Positions the engine grants a fresh start: row 1, and any row directly
        after a fasten-off. Everything else must consume the row below."""
        granted: set[int] = set()
        if self.rounds:
            granted.add(id(self.rounds[0]))
        for prev, nxt in zip(self.rounds, self.rounds[1:]):
            if prev.fasten_off:
                granted.add(id(nxt))
        return granted

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
    hook_mm: float | None = Field(
        default=None, gt=0,
        description="The primary hook, as stated by the source. None means the source never "
                    "named one -- defaulting this invented a tool the maker was not given.",
    )
    hooks: list[float] = Field(default_factory=list)  # additional hook sizes
    colors: list[str] = Field(default_factory=list)
    notions: list[str] = Field(default_factory=list)
    meters_per_gram: float | None = Field(
        default=None, gt=0,
        description="Yarn density (m/g) for weight estimate; e.g. 5-ply ~3.2 m/g. Estimate.",
    )


class Gauge(BaseModel):
    """Stitch/row gauge, and the only place a *measured* claim can come from.

    `attested_by` is deliberately not a boolean and deliberately not read from
    model JSON: it names the person and swatch behind the number. `calibrated`
    is derived from it, so a draft cannot print "measured from your swatch" by
    setting a flag.
    """

    stitches_per_10cm: float = Field(gt=0)
    rows_per_10cm: float = Field(gt=0)
    attested_by: str | None = Field(
        default=None,
        description="Human attestation: who measured the swatch and on what yarn/hook. Only a "
                    "hand-authored or CLI-supplied gauge may set it; the AI draft path never "
                    "passes this field.",
    )
    note: str = "Reference estimate. Swatch-calibrate on the stated hook/yarn for exactness."

    @property
    def calibrated(self) -> bool:
        return self.attested_by is not None


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
        hooks = [h for h in (self.material.hook_mm, *self.material.hooks) if h]
        return sorted(set(hooks))

    @property
    def effective_hooks(self) -> set[float]:
        """Hooks the instructions actually use. A part that names no hook works with the
        primary hook -- on a one-hook pattern that is not a gap in the source."""
        used = {c.hook for c in self.components if c.hook}
        if self.material.hook_mm and any(c.hook is None for c in self.components):
            used.add(self.material.hook_mm)
        return used

    @property
    def unassigned_hooks(self) -> list[float]:
        """Hooks listed in Materials that no part claims. A 1.0 mm hook that appears
        nowhere in the instructions is a gap in the source, not a free detail."""
        return [h for h in self.listed_hooks if h not in self.effective_hooks]

    def origin_counts(self) -> dict[str, int]:
        """How many instruction lines are the author's, and how many are ours. The
        Provenance section quotes this instead of asserting purity."""
        counts = {"source": 0, "inferred": 0, "added": 0}
        for comp in self.components:
            for rnd in comp.all_rows:
                counts[rnd.origin] += 1
            for st in comp.steps:
                counts[st.origin] += 1
            if comp.hook and comp.hook_origin != "source":
                counts[comp.hook_origin] += 1
        return counts


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

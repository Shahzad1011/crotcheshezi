"""The deterministic accuracy core.

The engine re-derives every stitch count purely from the operations, threading
start counts within each component, and compares against whatever totals the
author (human or AI) claimed. A mismatch is an error, not a warning.

Three layers, because arithmetic alone was demonstrably not enough:

* **Graph** -- every non-fresh row must work into stitches that exist, in order,
  so an op cannot reach past the end of the row below.
* **Position** -- a fresh start is *granted* (row 1, or the row after a
  fasten-off), never claimed by a flag. This is what makes a 6-to-50-stitch
  teleport impossible instead of merely suspicious.
* **Geometry** -- a round that adds far more than the established shaping rate
  ruffles, and now says so.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import Block, Component, Pattern, RoundSpec


@dataclass
class RoundAudit:
    component: str
    index: int
    color: str | None
    start_count: int
    consumed: int
    produced: int
    declared_total: int
    ok: bool
    issues: list[str]
    instance: int | None = None
    base_range: tuple[int, int] | None = None
    label: str | None = None
    fresh: bool = False
    flat: bool = False
    width: float = 0.0
    height: float = 0.0


@dataclass
class BlockAudit:
    component: str
    name: str
    instances: int
    base_available: int
    base_consumed: int
    ok: bool
    issues: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return f"{self.component} / {self.name} x{self.instances}"


def compute_round(rnd: RoundSpec, start_count: int) -> tuple[int, int]:
    seq = rnd.expand()
    consumed = sum(op.consume for op in seq)
    produced = sum(op.produce for op in seq)
    return consumed, produced


def _walk_targets(comp: Component, rnd: RoundSpec, start: int,
                  who: str) -> list[str]:
    """Ordered stitch-graph check: walk the ops across the row below, position by
    position. The sum alone cannot say *which* op reaches past the end.
    """
    issues: list[str] = []
    cursor = 0
    for op in rnd.expand():
        if not op.consume:
            continue
        if cursor + op.consume > start:
            issues.append(
                f"{comp.name} R{who}: a {op.kind} works into stitch "
                f"{cursor + 1}-{cursor + op.consume}, but the row below only has {start} "
                f"stitches. Nothing exists there to work into.")
            break
        cursor += op.consume
    return issues


def _audit_row(comp: Component, rnd: RoundSpec, start: int,
               instance: int | None = None,
               base_range: tuple[int, int] | None = None,
               fresh: bool = False) -> RoundAudit:
    consumed, produced = compute_round(rnd, start)
    issues: list[str] = []
    who = f"{rnd.index}" + (f".{instance}" if instance else "")
    if fresh:
        if produced != rnd.declared_total:
            issues.append(
                f"{comp.name} R{who}: foundation creates {produced} sts but "
                f"claims {rnd.declared_total}.")
    else:
        # graph layer: every op must land on a real stitch of the row below
        issues += _walk_targets(comp, rnd, start, who)
        if consumed != start:
            issues.append(
                f"{comp.name} R{who}: instructions consume {consumed} sts but "
                f"you started with {start}. Every stitch must be worked.")
        if produced != rnd.declared_total:
            issues.append(
                f"{comp.name} R{who}: stated total {rnd.declared_total} but the "
                f"instructions actually make {produced}.")
    seq = rnd.expand()
    return RoundAudit(
        component=comp.name, index=rnd.index, color=rnd.color, start_count=start,
        consumed=consumed, produced=produced, declared_total=rnd.declared_total,
        ok=not issues, issues=issues, instance=instance, base_range=base_range,
        label=rnd.label, fresh=fresh, flat=rnd.flat,
        width=sum(op.width for op in seq), height=sum(op.height for op in seq))


def _apply_growth_bounds(comp: Component, rows: list[RoundAudit]) -> None:
    """Geometry: a shaped piece keeps roughly its established rate of increase.

    A round that adds far more than that rate does not grow the shape, it ruffles.
    This only became expressible once ops carried width/height in the IR.
    """
    growth = [a.produced - a.start_count for a in rows if not a.fresh and not a.flat]
    if len(growth) < 4:
        return
    for i, g in enumerate(growth[3:], start=3):
        rate = max(growth[:i])
        if g > 2 * rate + 2:
            row = rows[i]
            row.issues.append(
                f"{comp.name} R{row.index}: adds {g} sts to a {row.start_count}-stitch row, "
                f"but this part's shaping rate so far is at most +{rate} per row. At this rate "
                f"the fabric ruffles instead of flaring -- that is a shape error, not a count "
                f"error.")
            row.ok = False


def _audit_block(comp: Component, block: Block, base_available: int
                 ) -> tuple[list[RoundAudit], BlockAudit]:
    """Expand every instance and check the set of them against the foundation."""
    rows: list[RoundAudit] = []
    issues: list[str] = []
    per = block.consumes_base_stitches or 0
    used = block.instances * per

    if block.consumes_base_stitches is None:
        issues.append(f"{comp.name} / {block.name}: no consumes_base_stitches declared, so "
                      f"the engine cannot check that {block.instances} instances fit the "
                      f"{base_available}-stitch foundation.")
    elif used != base_available:
        issues.append(
            f"{comp.name} / {block.name}: {block.instances} instances x {per} base sts = "
            f"{used}, but the previous round made {base_available}. "
            + (f"{base_available - used} stitches would be left unworked."
               if used < base_available else
               f"You need {used - base_available} more stitches than exist."))

    for k in range(1, block.instances + 1):
        lo = (k - 1) * per + 1
        rng = (lo, lo + per - 1) if per else None
        start = per
        for rnd in block.rows:
            a = _audit_row(comp, rnd, start, instance=k, base_range=rng)
            rows.append(a)
            start = a.produced
    # block-level issues stay on the block; row issues stay on their row, so one
    # failure is reported once, under the right heading.
    return rows, BlockAudit(comp.name, block.name, block.instances, base_available, used,
                            not issues, issues)


def _walk(pattern: Pattern) -> tuple[list[RoundAudit], list[BlockAudit]]:
    rows: list[RoundAudit] = []
    blocks: list[BlockAudit] = []
    for comp in pattern.components:
        if comp.kind != "verified":
            continue
        start = 0
        comp_rows: list[RoundAudit] = []
        for rnd in comp.rounds:
            # a fresh start is granted by position, never by a flag on the row
            a = _audit_row(comp, rnd, start, fresh=id(rnd) in comp.fresh_starts)
            comp_rows.append(a)
            rows.append(a)
            start = a.produced
        _apply_growth_bounds(comp, comp_rows)
        for block in comp.blocks:
            block_rows, ba = _audit_block(comp, block, start)
            rows.extend(block_rows)
            blocks.append(ba)
            # each instance works off the foundation and fastens off; anything after
            # a block continues from the tip the engine actually computed
            if block_rows:
                start = block_rows[-1].produced
    return rows, blocks


def audit(pattern: Pattern) -> list[RoundAudit]:
    return _walk(pattern)[0]


def audit_blocks(pattern: Pattern) -> list[BlockAudit]:
    return _walk(pattern)[1]


@dataclass
class RowLine:
    """One instruction to print, with its place in a repeated block resolved.

    Renderers iterate this instead of re-deriving instance expansion three times.
    """

    block_header: str | None
    join_note: bool
    rnd: RoundSpec
    audit: RoundAudit


def print_rows(comp: Component, comp_audits: list[RoundAudit]) -> list[RowLine]:
    """Plain rounds first, then every block instance with its base-stitch range."""
    out: list[RowLine] = []
    amap = {a.index: a for a in comp_audits if a.instance is None}
    for rnd in comp.rounds:
        a = amap.get(rnd.index)
        if a:
            out.append(RowLine(None, False, rnd, a))
    for block in comp.blocks:
        for k in range(1, block.instances + 1):
            rows = [a for a in comp_audits if a.instance == k]
            if not rows:
                continue
            for pos, a in enumerate(rows):
                rnd = next(r for r in block.rows if r.index == a.index)
                header = None
                if pos == 0:
                    span = f" -- base sts {a.base_range[0]}-{a.base_range[1]}" if \
                        a.base_range else ""
                    header = f"{block.name} {k}{span}"
                out.append(RowLine(header, pos == 0 and k > 1, rnd, a))
    return out


@dataclass
class Coverage:
    """How much of the object the arithmetic actually covers.

    Parts and operations are counted separately: sewing, assembly and hanging are
    things you do, not pieces of the object, so mixing them into a "7 components"
    denominator makes the coverage figure meaningless.
    """

    checked_stitches: int
    audited_rows: int
    checked_parts: list[str]
    unmodelled_parts: list[str]
    operations: list[str]

    @property
    def pct_of_parts(self) -> float:
        total = len(self.checked_parts) + len(self.unmodelled_parts)
        return 100.0 * len(self.checked_parts) / total if total else 0.0

    @property
    def complete(self) -> bool:
        return not self.unmodelled_parts


def coverage(pattern: Pattern, audits: list[RoundAudit]) -> Coverage:
    checked: list[str] = []
    unmodelled: list[str] = []
    operations: list[str] = []
    stitches = 0
    for comp in pattern.components:
        label = f"{comp.name} x{comp.quantity}" if comp.quantity > 1 else comp.name
        if comp.role == "operation":
            operations.append(comp.name)
            continue
        if comp.kind != "verified":
            unmodelled.append(f"{label} (described, no counts)")
            continue
        per_unit = sum(a.produced for a in audits if a.component == comp.name)
        stitches += per_unit * comp.quantity
        checked.append(label)
    return Coverage(stitches, len(audits), checked, unmodelled, operations)


def validate(pattern: Pattern) -> list[str]:
    rows, blocks = _walk(pattern)
    errors: list[str] = [i for r in rows for i in r.issues]
    errors += [i for b in blocks for i in b.issues]
    if not any(c.kind == "verified" for c in pattern.components):
        errors.append("Pattern has no verified rounds.")
    return errors


def author_totals(pattern: Pattern) -> Pattern:
    """Fill each round's total from the engine's own computation (for AI drafts,
    which must not assert totals). Workability is still validated afterwards.

    Keyed by position: `Component.all_rows` and the audit list are the same sequence
    in the same order, so a row can never be handed another row's total.
    """
    rows, _ = _walk(pattern)
    by_comp: dict[str, list[RoundAudit]] = {}
    for a in rows:
        by_comp.setdefault(a.component, []).append(a)
    for comp in pattern.components:
        if comp.kind != "verified":
            continue
        for rnd, a in zip(comp.all_rows, by_comp.get(comp.name, [])):
            rnd.declared_total = a.produced
    return pattern

"""Matplotlib charts, drawn from engine-computed counts (never hand-authored).

render_chart: radial 'rose' for pieces built in the round; a plain bar chart
when a component has flat turning rows (a rose would imply a circular body).
render_silhouette: dispatches on geometry -- render_profile for axisymmetric
tubes, render_flat for flat pieces (disc + radiating points).
All take a single component's rounds+audits so a multi-part pattern isn't
mashed into one misleading curve.
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")  # headless-safe on this machine
import matplotlib.pyplot as plt
import numpy as np

from .engine import BlockAudit, RoundAudit
from .schema import Gauge, RoundSpec

_COLOR_MAP = {"red": "#d11a2a", "white": "#9aa0a6", "silver": "#6b7280", "pink": "#ec4899"}


def _unit_rows(rounds: list[RoundSpec],
               audits: list[RoundAudit]) -> tuple[list[RoundSpec], list[RoundAudit]]:
    """One unit's worth of rows: plain rounds plus a single instance of each block.

    Plotting all five star points as if they were five more rounds of one body is
    the mistake this guards against -- the repeats are identical, so one is drawn
    and the instance count is stated in the title instead.
    """
    rs: list[RoundSpec] = []
    aus: list[RoundAudit] = []
    for r, a in zip(rounds, audits):
        if a.instance is not None and a.instance > 1:
            continue
        rs.append(r)
        aus.append(a)
    return rs, aus


def _row_label(a: RoundAudit) -> str:
    return f"{a.index}" + (f".{a.instance}" if a.instance else "")


def _wedge_color(color: str | None) -> str:
    if not color:
        return "#60a5fa"
    low = color.lower()
    for key, val in _COLOR_MAP.items():
        if key in low:
            return val
    return "#60a5fa"


def render_chart(rounds: list[RoundSpec], audits: list[RoundAudit], title: str, path: str,
                 blocks: list[BlockAudit] | None = None) -> str:
    rounds, audits = _unit_rows(rounds, audits)
    if any(r.flat for r in rounds):
        return render_bar_chart(rounds, audits, title, path, blocks)
    n = len(audits)
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="polar")
    if n:
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        width = 2 * np.pi / n
        radii = [a.produced for a in audits]
        colors = [_wedge_color(rounds[i].color) for i in range(n)]
        ax.bar(theta, radii, width=width, bottom=0.0, color=colors, alpha=0.85,
               edgecolor="white", linewidth=1.2)
        ax.set_xticks(theta)
        ax.set_xticklabels([_row_label(a) for a in audits], fontsize=8)
    ax.set_title(f"{title}\nRow-by-row stitch count (radius = stitches)", pad=22,
                 fontsize=12, weight="bold")
    ax.set_rlabel_position(0)
    ax.grid(color="#cccccc", linestyle=":", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def render_bar_chart(rounds: list[RoundSpec], audits: list[RoundAudit], title: str, path: str,
                     blocks: list[BlockAudit] | None = None) -> str:
    """Stitch count per row for a flat piece, where a radial chart would lie.

    This is a count profile, not a stitch chart: it shows how many stitches each
    row leaves, not where they sit, and says so in the subtitle.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    idx = [_row_label(a) for a in audits]
    counts = [a.produced for a in audits]
    colors = [_wedge_color(r.color) for r in rounds]
    ax.bar(idx, counts, color=colors, alpha=0.85, edgecolor="white")
    for x, c in zip(range(len(idx)), counts):
        ax.text(x, c, str(c), ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Row (block instances shown once)")
    ax.set_ylabel("Stitches")
    rep = ""
    if blocks:
        rep = "\n" + ", ".join(f"{b.name} worked x{b.instances}" for b in blocks)
    ax.set_title(f"{title}\nStitches left per row, engine-verified.{rep}",
                 fontsize=11, weight="bold")
    ax.grid(axis="y", color="#e5e7eb", linestyle=":", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def render_profile(rounds: list[RoundSpec], audits: list[RoundAudit],
                   gauge: Gauge, title: str, path: str) -> str:
    stitch_w = 10.0 / gauge.stitches_per_10cm
    row_h = 10.0 / gauge.rows_per_10cm
    fig, ax = plt.subplots(figsize=(6, 6))
    for i, a in enumerate(audits):
        radius = (a.produced * stitch_w) / (2 * math.pi)
        y0, y1 = i * row_h, (i + 1) * row_h
        ax.fill_betweenx([y0, y1], -radius, radius,
                         color=_wedge_color(rounds[i].color), alpha=0.8, linewidth=0)
        ax.hlines(y1, -radius, radius, color="white", linewidth=0.6)
    ax.set_aspect("equal")
    ax.axvline(0, color="#9ca3af", linewidth=0.6, linestyle="--")
    ax.set_xlabel("width (cm)")
    ax.set_ylabel("height (cm)")
    ax.set_title(f"{title}\nAxisymmetric profile (from verified counts)", fontsize=11, weight="bold")
    ax.grid(color="#e5e7eb", linestyle=":", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def _edge(r: float, hw: float, sign: float, cos_t: float, sin_t: float) -> tuple[float, float]:
    """One outline vertex of a point: radius r, lateral offset `sign*hw`, at angle t."""
    return (r * cos_t - sign * hw * sin_t, r * sin_t + sign * hw * cos_t)


def render_flat(rounds: list[RoundSpec], audits: list[RoundAudit],
                gauge: Gauge, title: str, path: str,
                blocks: list[BlockAudit] | None = None) -> str:
    """Top-down silhouette of a flat piece: a round-built body plus radiating
    points carved by runs of turning rows.

    Nothing is drawn by hand. The body radius, point count, per-row widths and
    the stepped, alternating taper all come from engine-verified counts. The
    taper is a staircase because the pattern skips one stitch at the turn, and
    turning flips which end that is -- a smooth kite would be a lie.
    """
    stitch_w = 10.0 / gauge.stitches_per_10cm
    row_h = 10.0 / gauge.rows_per_10cm

    body = [(r, a) for r, a in zip(rounds, audits) if not r.flat]
    point = [(r, a) for r, a in zip(rounds, audits) if r.flat]
    if not body:
        return render_profile(rounds, audits, gauge, title, path)

    body_r = body[-1][1].produced * stitch_w / (2 * math.pi)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.add_patch(plt.Circle((0, 0), body_r, color=_wedge_color(body[-1][0].color),
                            alpha=0.75, linewidth=0))

    if point:
        # Prefer the engine's verified multiplicity; fall back to circumference.
        if blocks:
            n_points = blocks[0].instances
            how = f"{n_points} points (x{blocks[0].instances} block instances)"
        else:
            base_w = point[0][1].produced * stitch_w
            n_points = max(1, round(2 * math.pi * body_r / base_w))
            how = f"{n_points} points"
        # Lateral edges per row: base width, then one stitch dropped at the turn,
        # alternating ends because the work is turned.
        n0 = point[0][1].produced
        left, right = -n0 * stitch_w / 2, n0 * stitch_w / 2
        edges: list[tuple[float, float]] = [(left, right)]
        for j in range(1, len(point)):
            if j % 2 == 1:
                left += stitch_w
            else:
                right -= stitch_w
            edges.append((left, right))
        # Anchor the base a row inside the disc, clamped to that chord, so the
        # points read as attached rather than floating off the rim.
        r0 = body_r - row_h
        chord = math.sqrt(max(0.0, body_r**2 - r0**2))
        edges[0] = (max(edges[0][0], -chord), min(edges[0][1], chord))
        tip_r = body_r + (len(point) - 1) * row_h
        color = _wedge_color(point[0][0].color)
        for i in range(n_points):
            theta = 2 * math.pi * i / n_points
            cos_t, sin_t = math.cos(theta), math.sin(theta)

            outline: list[tuple[float, float]] = []
            for j, (lo, _hi) in enumerate(edges):
                outline.append(_edge(r0 + j * row_h, lo, 1.0, cos_t, sin_t))
            outline.append(_edge(tip_r, edges[-1][0], 1.0, cos_t, sin_t))
            outline.append(_edge(tip_r, edges[-1][1], 1.0, cos_t, sin_t))
            for j, (_lo, hi) in reversed(list(enumerate(edges))):
                outline.append(_edge(r0 + j * row_h, hi, 1.0, cos_t, sin_t))
            ax.add_patch(plt.Polygon(outline, closed=True, color=color, alpha=0.85,
                                     linewidth=0))
        ax.set_title(f"{title}\nFlat silhouette: {how}, from verified counts",
                     fontsize=11, weight="bold")
    else:
        ax.set_title(f"{title}\nFlat disc (from verified counts)", fontsize=11, weight="bold")

    ax.set_aspect("equal")
    lim = body_r + ((len(point) - 1) * row_h if point else 0)
    ax.set_xlim(-lim * 1.15, lim * 1.15)
    ax.set_ylim(-lim * 1.15, lim * 1.15)
    ax.set_xlabel("width (cm)")
    ax.set_ylabel("height (cm)")
    ax.grid(color="#e5e7eb", linestyle=":", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def render_silhouette(rounds: list[RoundSpec], audits: list[RoundAudit],
                      gauge: Gauge, title: str, path: str,
                      blocks: list[BlockAudit] | None = None) -> str:
    """Pick the honest geometry: flat pieces are drawn top-down, tubes in profile."""
    rounds, audits = _unit_rows(rounds, audits)
    if rounds and any(r.flat for r in rounds):
        return render_flat(rounds, audits, gauge, title, path, blocks)
    return render_profile(rounds, audits, gauge, title, path)

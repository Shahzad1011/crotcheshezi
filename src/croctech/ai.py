"""Provider-agnostic AI draft layer (the *designer*) + repair support.

Integrity rule (this is the anti-hallucination contract): a provider returns
design INTENT only -- which rounds, which shaping, colours, materials. It never
supplies stitch totals (`engine.author_totals` computes them), never claims a
fresh start, and never attests a gauge. The pipeline then re-validates, and any
workability defect is fed back through `refine_pattern` in a bounded repair loop.

The live Gemini/local adapters below are WRITTEN but NOT yet executed (they need
a key / a running endpoint and their SDKs). Until we run them against a real
endpoint they are marked unverified -- we will not claim they work.
"""

from __future__ import annotations

import os
from typing import Protocol

from .engine import author_totals
from .schema import Gauge, Material, Pattern, RoundSpec, parse_repeat


class PatternProvider(Protocol):
    name: str

    def draft_pattern(self, request: str) -> Pattern: ...
    def refine_pattern(self, pattern: Pattern, errors: list[str]) -> Pattern: ...


def _draft_to_pattern(data: dict, provider: str = "ai") -> Pattern:
    """Convert a simplified design-intent draft dict into a validated Pattern.

    The draft schema is deliberately *narrower* than the model: a provider states
    shaping, colours and materials and nothing else. Fields it must not have are not
    merely discouraged here --

    * no stitch totals (`author_totals` computes them),
    * no `foundation`/`starts_from`: a fresh start is granted by row position, so a
      draft cannot abandon a row's stitches by declaring a new beginning,
    * no gauge attestation: `calibrated` used to be copied out of this JSON, which
      let a model print "measured from your swatch" for a number it invented,
    * no hook default: omitting a hook used to invent 2.5 mm.
    """
    m = data.get("material", {})
    g = data.get("gauge") or {}
    sts, rows = g.get("stitches_per_10cm"), g.get("rows_per_10cm")
    gauge = None
    gauge_note = ""
    if sts and rows:
        gauge = Gauge(stitches_per_10cm=float(sts), rows_per_10cm=float(rows),
                      note=f"Quoted by the {provider} draft, not measured here. Nobody swatched "
                           f"this yarn on this hook in this session, so every centimetre derived "
                           f"from it is illustrative until a human attests it (gauge.attested_by).")
    else:
        gauge_note = " No gauge was supplied, so no finished size is claimed."
    rounds: list[RoundSpec] = []
    for i, rd in enumerate(data.get("rounds", []), start=1):
        repeat = rd.get("repeat", "")
        cycle = parse_repeat(repeat) if repeat else []
        rounds.append(
            RoundSpec(
                index=rd.get("index", i),
                color=rd.get("color"),
                starts_from="magic_ring" if i == 1 else None,
                origin="inferred",
                cycle=cycle,
                repeats=int(rd.get("repeats", 1)),
                declared_total=0,  # engine overwrites in author_totals below
                notes=list(rd.get("notes", [])),
            )
        )
    pattern = Pattern(
        name=data.get("name", "Untitled"),
        item_type=data.get("item_type", "object"),
        description=data.get("description", ""),
        provenance=(f"Design intent drafted by the {provider} provider; no stitch total in this "
                    f"document was authored by the model -- each was computed by the engine."
                    + gauge_note),
        material=Material(
            yarn=m.get("yarn", ""),
            hook_mm=m.get("hook_mm"),
            hooks=[float(h) for h in m.get("hooks", [])],
            colors=list(m.get("colors", [])),
            notions=list(m.get("notions", [])),
            meters_per_gram=m.get("meters_per_gram"),
        ),
        gauge=gauge,
        rounds=rounds,
    )
    return author_totals(pattern)


class ExampleProvider:
    """Offline, deterministic reference used for demos and tests (already has
    real authored totals so the cross-check is meaningful)."""

    name = "example-offline"

    def draft_pattern(self, request: str) -> Pattern:
        from .example import build_pattern

        return build_pattern()

    def refine_pattern(self, pattern: Pattern, errors: list[str]) -> Pattern:
        from .example import build_pattern

        return build_pattern()


class RepairDemoProvider:
    """Offline provider that proves the repair loop WITHOUT any API key.

    Its first draft contains a classic AI mistake: a shaping cycle that consumes
    more stitches than the round started with. The engine rejects it; `refine`
    corrects it, and the loop only renders once validation is clean.
    """

    name = "repair-demo"

    def draft_pattern(self, request: str) -> Pattern:
        from .example import build_pattern

        p = build_pattern()
        # Inject over-worked Round 5: (5 sc, inc) x3 consumes 18 but starts with 15.
        row5 = p.components[0].rounds[4]
        row5.cycle = parse_repeat("5x, v")
        row5.repeats = 3
        return author_totals(p)

    def refine_pattern(self, pattern: Pattern, errors: list[str]) -> Pattern:
        from .example import build_pattern

        return build_pattern()


class GeminiProvider:
    """Gemini adapter (milestone M4). Unverified until run with GEMINI_API_KEY."""

    name = "gemini"

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model

    def _client(self):
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set; Gemini draft needs a key.")
        from google import genai  # lazy; requires `pip install google-genai`

        return genai.Client(api_key=key)

    def _ask(self, prompt: str) -> dict:
        import json

        from google import genai  # noqa: F401  (ensures SDK import path is exercised)

        client = self._client()
        resp = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return json.loads(resp.text)

    def draft_pattern(self, request: str) -> Pattern:
        prompt = (
            "You are a crochet designer. Return ONLY JSON describing design intent "
            "(name, item_type, description, material{yarn,hook_mm,colors,notions,"
            "meters_per_gram}, gauge{stitches_per_10cm,rows_per_10cm}, "
            "rounds[{index,color,repeat,repeats,notes}]). Use repeat "
            "notation like '2x, v' (2 single crochets then an increase). Do NOT "
            "compute stitch totals, do NOT send a 'foundation' or 'calibrated' flag "
            "(they are ignored), and do NOT describe a fresh start: the engine decides "
            "where a new foundation is legal. Omit gauge entirely unless the request "
            "states a measured swatch -- never estimate one, because the finished size "
            f"is derived from it. Request: {request}"
        )
        return _draft_to_pattern(self._ask(prompt), self.name)

    def refine_pattern(self, pattern: Pattern, errors: list[str]) -> Pattern:
        prompt = (
            "Fix this crochet design so it passes validation. Errors:\n- "
            + "\n- ".join(errors) + "\nCurrent rounds:\n"
            + str([{"index": r.index, "color": r.color, "repeat": r.repeat_notation,
                    "repeats": r.repeats} for r in pattern.rounds])
            + "\nReturn ONLY the corrected design-intent JSON (no totals)."
        )
        return _draft_to_pattern(self._ask(prompt), self.name)


class LocalProvider:
    """Offline local model (OpenAI-compatible endpoint). Unverified until run."""

    name = "local"

    def __init__(self, base_url: str | None = None, model: str = "qwen2.5"):
        self.base_url = base_url or os.environ.get("LOCAL_LLM_BASE_URL")
        self.model = model

    def draft_pattern(self, request: str) -> Pattern:
        raise NotImplementedError(
            "Local-model wiring is milestone M4: set LOCAL_LLM_BASE_URL to an "
            "OpenAI-compatible server (e.g. Ollama) and run against it to verify."
        )

    def refine_pattern(self, pattern: Pattern, errors: list[str]) -> Pattern:
        raise NotImplementedError("Local-model refine is milestone M4 (unverified).")


def resolve_provider(name: str) -> PatternProvider:
    table = {
        "example": ExampleProvider, "offline": ExampleProvider,
        "repair": RepairDemoProvider, "gemini": GeminiProvider, "local": LocalProvider,
    }
    if name not in table:
        raise ValueError(f"unknown provider {name!r}; choose from {sorted(table)}")
    return table[name]()

"""
CrocTech AI Package.
Provides prompts, synthesis pipeline, and auto-correctors.
"""

from croctech.ai.prompts import CROCHET_AI_SYSTEM_PROMPT, build_pattern_prompt
from croctech.ai.corrector import CrochetAutoCorrector
from croctech.ai.pipeline import PatternSynthesisPipeline

__all__ = [
    "CROCHET_AI_SYSTEM_PROMPT",
    "build_pattern_prompt",
    "CrochetAutoCorrector",
    "PatternSynthesisPipeline",
]


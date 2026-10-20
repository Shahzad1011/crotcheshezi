"""
CrocTech Core Types & Definitions.
Enumerations and fundamental constants for crochet stitches, working modes, and materials.
"""

from enum import Enum
from typing import Dict, Any


class StitchType(str, Enum):
    """Standard crochet stitch types with physical topological properties."""
    MAGIC_RING = "mr"
    CH = "ch"
    SL_ST = "sl_st"
    SC = "sc"             # Single crochet (US)
    INC = "inc"           # Increase (2 sc in same st)
    DEC = "dec"           # Decrease (sc2tog / invdec)
    HDC = "hdc"           # Half double crochet
    HDC_INC = "hdc_inc"   # 2 hdc in same st
    HDC_DEC = "hdc_dec"   # hdc2tog
    DC = "dc"             # Double crochet (US)
    DC_INC = "dc_inc"     # 2 dc in same st
    DC_DEC = "dc_dec"     # dc2tog
    TR = "tr"             # Treble crochet
    TR_INC = "tr_inc"
    TR_DEC = "tr_dec"
    BOBBLE = "bobble"
    PICOT = "picot"
    CUSTOM = "custom"


class WorkingMode(str, Enum):
    """Working topology of the crochet piece."""
    JOINED_ROUNDS = "joined_rounds"        # ch N at start, sl st at end
    CONTINUOUS_SPIRAL = "continuous_spiral" # Amigurumi continuous spiral
    FLAT_ROWS = "flat_rows"                # Turned flat fabric


class LoopTarget(str, Enum):
    """Which loop(s) of the parent stitch are worked into."""
    BOTH = "both"
    BLO = "blo"  # Back loop only
    FLO = "flo"  # Front loop only


class YarnWeight(str, Enum):
    """Standard yarn weight categories (CYC standards + international ply)."""
    LACE_0 = "0-lace"            # 10-count thread
    SUPER_FINE_1 = "1-super-fine" # Fingering / Sock / 3-4 ply
    FINE_2 = "2-fine"            # Sport / Baby / 5-ply
    LIGHT_3 = "3-light"          # DK / Light Worsted / 8-ply
    MEDIUM_4 = "4-medium"        # Worsted / Afghan / Aran / 10-ply
    BULKY_5 = "5-bulky"          # Chunky / 12-ply
    SUPER_BULKY_6 = "6-super-bulky"
    JUMBO_7 = "7-jumbo"


class FiberType(str, Enum):
    """Yarn fiber composition."""
    COTTON = "cotton"
    ACRYLIC = "acrylic"
    COTTON_ACRYLIC_BLEND = "cotton_acrylic_blend"
    WOOL = "wool"
    MERINO = "merino"
    POLYESTER = "polyester"
    METALLIC_GLITTER = "metallic_glitter"
    BAMBOO = "bamboo"
    MIXED = "mixed"


class Terminology(str, Enum):
    """Crochet terminology conventions."""
    US = "US"
    UK = "UK"


# Physical and topological metadata for each stitch type:
# - consumed: how many base loops/stitches it consumes from previous round
# - produced: how many new stitch top-loops it produces for the next round
# - height_ratio: height relative to 1 standard single crochet (sc = 1.0)
# - yarn_multiplier: approximate yarn length factor relative to hook diameter
STITCH_PROPERTIES: Dict[StitchType, Dict[str, Any]] = {
    StitchType.MAGIC_RING: {
        "consumed": 0,
        "produced": 0, # Produces base for row 1
        "height_ratio": 0.0,
        "yarn_multiplier": 1.5,
        "description": "Adjustable starting ring loop"
    },
    StitchType.CH: {
        "consumed": 0,
        "produced": 1,
        "height_ratio": 0.8,
        "yarn_multiplier": 2.4,
        "description": "Chain stitch"
    },
    StitchType.SL_ST: {
        "consumed": 1,
        "produced": 0, # Often used purely as join, not worked into as active body st
        "height_ratio": 0.25,
        "yarn_multiplier": 2.2,
        "description": "Slip stitch join or edging"
    },
    StitchType.SC: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 1.0,
        "yarn_multiplier": 4.2,
        "description": "Single crochet (US)"
    },
    StitchType.INC: {
        "consumed": 1,
        "produced": 2,
        "height_ratio": 1.0,
        "yarn_multiplier": 8.2,
        "description": "2 single crochets in same stitch (+1 increase)"
    },
    StitchType.DEC: {
        "consumed": 2,
        "produced": 1,
        "height_ratio": 1.0,
        "yarn_multiplier": 5.8,
        "description": "Single crochet 2 together / invisible decrease (-1 decrease)"
    },
    StitchType.HDC: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 1.45,
        "yarn_multiplier": 5.4,
        "description": "Half double crochet (US)"
    },
    StitchType.HDC_INC: {
        "consumed": 1,
        "produced": 2,
        "height_ratio": 1.45,
        "yarn_multiplier": 10.5,
        "description": "2 hdc in same stitch"
    },
    StitchType.HDC_DEC: {
        "consumed": 2,
        "produced": 1,
        "height_ratio": 1.45,
        "yarn_multiplier": 7.5,
        "description": "hdc 2 together"
    },
    StitchType.DC: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 2.0,
        "yarn_multiplier": 7.0,
        "description": "Double crochet (US)"
    },
    StitchType.DC_INC: {
        "consumed": 1,
        "produced": 2,
        "height_ratio": 2.0,
        "yarn_multiplier": 13.8,
        "description": "2 dc in same stitch"
    },
    StitchType.DC_DEC: {
        "consumed": 2,
        "produced": 1,
        "height_ratio": 2.0,
        "yarn_multiplier": 9.5,
        "description": "dc 2 together"
    },
    StitchType.TR: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 2.8,
        "yarn_multiplier": 9.6,
        "description": "Treble crochet (US)"
    },
    StitchType.TR_INC: {
        "consumed": 1,
        "produced": 2,
        "height_ratio": 2.8,
        "yarn_multiplier": 19.0,
        "description": "2 tr in same stitch"
    },
    StitchType.TR_DEC: {
        "consumed": 2,
        "produced": 1,
        "height_ratio": 2.8,
        "yarn_multiplier": 13.0,
        "description": "tr 2 together"
    },
    StitchType.BOBBLE: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 1.8,
        "yarn_multiplier": 24.0,
        "description": "5-dc cluster bobble stitch"
    },
    StitchType.PICOT: {
        "consumed": 0,
        "produced": 0,
        "height_ratio": 1.2,
        "yarn_multiplier": 6.5,
        "description": "Decorative picot loop (ch 3, sl st)"
    },
    StitchType.CUSTOM: {
        "consumed": 1,
        "produced": 1,
        "height_ratio": 1.0,
        "yarn_multiplier": 4.5,
        "description": "Custom user stitch"
    }
}


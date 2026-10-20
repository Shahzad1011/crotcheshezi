"""
Tokenizer and Regex Patterns for Crochet DSL.
Handles natural language descriptions, standard abbreviations, shorthand symbols (x, v, a), and repeat blocks.
"""

import re

# Regex patterns for stitch recognition
RE_MAGIC_RING = re.compile(r"(?:magic\s*ring|magic\s*circle|mr|adjustable\s*ring)", re.IGNORECASE)
RE_CHAIN = re.compile(r"(\d+)\s*(?:ch(?:ain)?s?|chain\s*stitches?)", re.IGNORECASE)
RE_SLIP_STITCH = re.compile(r"(?:sl(?:\s*st)?|slip\s*stitch(?:es)?)", re.IGNORECASE)

# Standard stitch patterns
RE_SC_COUNT = re.compile(r"(\d+)\s*(?:sc|single\s*crochets?|single\s*crochet\s*stitches?)", re.IGNORECASE)
RE_HDC_COUNT = re.compile(r"(\d+)\s*(?:hdc|half\s*double\s*crochets?)", re.IGNORECASE)
RE_DC_COUNT = re.compile(r"(\d+)\s*(?:dc|double\s*crochets?)", re.IGNORECASE)
RE_TR_COUNT = re.compile(r"(\d+)\s*(?:tr|treble\s*crochets?)", re.IGNORECASE)

# Increase patterns
RE_INC = re.compile(r"(?:inc(?:rease)?|2\s*(?:sc|single\s*crochets?)\s*in\s*(?:the\s*same|the\s*next|next)\s*(?:st|stitch|loop)?|v\s*sc|\bv\b)", re.IGNORECASE)
RE_DEC = re.compile(r"(?:dec(?:rease)?|sc2tog|single\s*crochet\s*2\s*together|invdec|\b(?:inv\s*dec)\b|\ba\b|\b\^\b)", re.IGNORECASE)

# Repeat multiplier patterns e.g. "(sc, inc) * 6", "(2 sc, inc) x 3", "[sc, inc] * 4"
# MUST have an explicit multiplier (* 3, x 3, repeat 3 times) to distinguish from explanatory notes
RE_REPEAT_BLOCK = re.compile(r"[\(\[\{]([^\)\]\}]+)[\)\]\}]\s*(?:[*xX×]\s*(\d+)|\s*repeat\s*(\d+)\s*times)", re.IGNORECASE)
RE_SHORTHAND_XV = re.compile(r"\((\d*)x\s*,\s*v(?:\s*sc)?\)", re.IGNORECASE)

# Row / Round header e.g. "Row 1:", "Round 3-5:", "R2:", "Rows 6 to 9"
RE_ROW_HEADER = re.compile(r"^(?:(?:Row|Round|R|Rnd)s?\s*(\d+)(?:\s*(?:-|to)\s*(\d+))?[:\.]?)", re.IGNORECASE)

# Stated total stitch count e.g. "total of 9 single crochets", "[9]", "(9 sts)", "= 9 sc", "making a total of 12 sc"
RE_STATED_TOTAL = re.compile(r"(?:(?:total|making\s*a\s*total\s*of|total\s*of)\s*(\d+)\s*(?:sc|sts?|stitches?|single\s*crochets?)?|\[(\d+)\]|\((\d+)\s*sts?\)|=\s*(\d+))", re.IGNORECASE)

# Color switch
RE_COLOR_SWITCH = re.compile(r"(?:switch\s*to\s*(\w+)(?:\s*color|\s*yarn)?|change\s*to\s*(\w+)|with\s*(\w+)\s*yarn)", re.IGNORECASE)


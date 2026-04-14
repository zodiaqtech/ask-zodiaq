"""
Response models for Ask ZodiaQ API.

UI rendering contract
─────────────────────
Each ZodiaQItem has a `type` that tells the front-end exactly how to render it:

  type = "timing"   → show `timing` as a date-range badge
                       `verdict` and `value` are always null

  type = "verdict"  → show `verdict` as a Yes / No / Moderate badge
                       `timing` may optionally carry a secondary date hint
                       `value` is always null

  type = "text"     → show `value` as plain descriptive text
                       `verdict` and `timing` are always null

All items carry `astro_reason` — one human-readable astrological explanation.
The top-level `summary` gives a one-line headline for the whole topic result.
"""
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    TIMING  = "timing"   # Renders a date range  e.g. "Jul 2026 – Aug 2026"
    VERDICT = "verdict"  # Renders a badge        Yes / No / Moderate
    TEXT    = "text"     # Renders plain text     e.g. "Arranged Marriage"


class ZodiaQItem(BaseModel):
    """
    A single information card inside a ZodiaQ response.

    Exactly one of the three answer fields is non-null, determined by `type`:
      timing  → set when type = TIMING
      verdict → set when type = VERDICT   (timing may also be set as a date hint)
      value   → set when type = TEXT
    """
    label:        str
    type:         ItemType

    # ── Answer fields — only the one matching `type` is populated ──────────
    verdict:      Optional[Literal["Yes", "No", "Moderate"]] = None
    timing:       Optional[str] = None   # date range, e.g. "Jul 2026 – Aug 2026"
    value:        Optional[str] = None   # text content for type=TEXT

    # ── Astrological reasoning ──────────────────────────────────────────────
    astro_reason: str = ""   # single human-readable explanation (replaces details+reason)


class ZodiaQResponse(BaseModel):
    """Top-level response for a single ZodiaQ topic query."""
    topic:         str
    category:      str
    question:      str
    summary:       str = ""                 # One-line headline for the whole result
    items:         List[ZodiaQItem]         # Answer rows
    consult_more:  List[str] = Field(default_factory=list)
    promise_state: Optional[str] = None    # "promised" / "promised_with_obstacles" / "neutral" / "blocked"
    error:         Optional[str] = None

"""
Response models for Ask ZodiaQ API.

UI rendering contract
─────────────────────
Each ZodiaQItem has a `type` that tells the front-end which rendering style to use:

  type = "timing"   → primary answer is a date-range  e.g. "Jul 2026 – Aug 2026"
  type = "verdict"  → primary answer is a badge        Yes / No / Moderate (or Hindi)
  type = "text"     → primary answer is plain text     e.g. "Arranged Marriage"

All three answer keys (`timing`, `verdict`, `value`) are populated with the
same answer string so the front-end can read whichever key it prefers.

All items carry `astro_reason` — one human-readable astrological explanation.
The top-level `summary` gives a one-line headline for the whole topic result.
"""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    TIMING  = "timing"   # Renders a date range  e.g. "Jul 2026 – Aug 2026"
    VERDICT = "verdict"  # Renders a badge        Yes / No / Moderate
    TEXT    = "text"     # Renders plain text     e.g. "Arranged Marriage"


class ZodiaQItem(BaseModel):
    """
    A single information card inside a ZodiaQ response.

    All three answer keys are populated with the same answer string for
    ease of frontend integration. The `type` field indicates which rendering
    style to use.
    """
    label:        str
    type:         ItemType

    # ── Answer fields — all three carry the same answer string ─────────────
    verdict:      Optional[str] = None   # e.g. "Yes" / "हाँ" / date / text
    timing:       Optional[str] = None   # e.g. "Jul 2026 – Aug 2026" / verdict / text
    value:        Optional[str] = None   # e.g. "Arranged Marriage" / verdict / date

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

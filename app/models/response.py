"""
Response models for Ask ZodiaQ API.
Designed to match the UI specification shown in the app screenshots.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any


class ItemType(str, Enum):
    """Visual presentation type for a response item."""
    DATE_RANGE = "date_range"   # e.g. "Nov 2025 – Mar 2026"
    VERDICT    = "verdict"      # Yes / No / Moderate
    TEXT       = "text"         # Plain descriptive text
    LIST       = "list"         # Comma-separated or bullet list


class ZodiaQItem(BaseModel):
    """
    A single information card / row inside a ZodiaQ response section.

    Matches the screenshot rows:
        label   → "Next favourable Yog"
        verdict → "Yes" / "No" / None
        value   → "Nov 2025 – Mar 2026" / "Love Marriage" / None
        type    → how the front-end should render the value
        details → supporting body text (replaces LLM narrative)
        reason  → short technical reason (e.g. "7th CSL Mercury signifies 2,7,11")
    """
    label:   str
    verdict: Optional[str]  = None   # "Yes" / "No" / "Moderate"
    value:   Optional[str]  = None   # Rendered value (date range, direction, etc.)
    type:    ItemType        = ItemType.TEXT
    details: Optional[str]  = None
    reason:  Optional[str]  = None


class ZodiaQResponse(BaseModel):
    """
    Top-level response for a single ZodiaQ topic query.
    Mirrors the full-screen result shown after the user taps a question card.
    """
    topic:        str                        # e.g. "marriage"
    category:     str                        # e.g. "Marriage Prediction"
    question:     str                        # The user-facing question string
    items:        List[ZodiaQItem]           # Main answer rows
    consult_more: List[str] = Field(         # "Talk to an astrologer" bullet points
        default_factory=list
    )

    # Optional meta fields (can be used for analytics / deeper drill-down)
    promise_state: Optional[str] = None     # "promised" / "blocked" / "possible"
    error:         Optional[str] = None     # Non-null only when something failed

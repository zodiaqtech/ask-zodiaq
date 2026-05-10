"""
Travel Domain Rules
Vedic house significations and rules for travel, pilgrimage,
foreign journeys, travel success, risks, and supportive guidance.

⚠️ NO KP rules
⚠️ NO absolute timing guarantees
⚠️ Vedic / Prashna-style interpretation only
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic scoring / promise logic)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Travel success & fulfillment
    "positive_houses": {3, 7, 9},       # Short journeys, long travel, pilgrimage
    "supportive_houses": {1, 4, 11},    # Self, comfort/vehicles, fulfillment
    "negative_houses": {6, 8, 12},      # Obstacles, sudden issues, expenses/loss
    "supportive_score": 2
}


# ============================================================
# TIMING RULES
# (USED ONLY FOR SOFT HINTS — NOT EXACT DATES)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # General travel activation
    # --------------------------------------------------------
    "Travel Timing": {
        "positive_houses": {3, 7, 9},
        "supportive_houses": {1, 4, 11},
        "negative_houses": {6, 12},
        "key_planets": {"Mercury", "Moon", "Venus"}
    },

    # --------------------------------------------------------
    # Pilgrimage & spiritual journey activation
    # --------------------------------------------------------
    "Pilgrimage Timing": {
        "positive_houses": {9, 12},
        "supportive_houses": {5, 11},
        "negative_houses": {6, 8},
        "key_planets": {"Jupiter", "Moon"}
    },

    # --------------------------------------------------------
    # Foreign travel / long-distance journeys
    # --------------------------------------------------------
    "Foreign Travel Timing": {
        "positive_houses": {7, 9, 12},
        "supportive_houses": {3, 11},
        "negative_houses": {6, 8},
        "key_planets": {"Rahu", "Jupiter", "Saturn"}
    },

    # --------------------------------------------------------
    # Travel delay / obstacle risk
    # --------------------------------------------------------
    "Travel Delay Risk": {
        "positive_houses": {6, 8},
        "supportive_houses": {12},
        "negative_houses": {3, 7, 9},
        "key_planets": {"Saturn", "Mars", "Rahu"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Core normalization
    "Travel": "Travel",

    # General travel
    "Travel Timing": "Travel Timing",
    "Journey Timing": "Travel Timing",
    "When Should I Travel": "Travel Timing",

    # Pilgrimage
    "Pilgrimage": "Pilgrimage Timing",
    "Spiritual Journey": "Pilgrimage Timing",
    "Holy Travel": "Pilgrimage Timing",

    # Foreign travel
    "Foreign Travel": "Foreign Travel Timing",
    "Abroad Journey": "Foreign Travel Timing",
    "International Travel": "Foreign Travel Timing",

    # Risks
    "Travel Risks": "Travel Delay Risk",
    "Obstacles in Travel": "Travel Delay Risk",
    "Is Travel Safe": "Travel Delay Risk"
}


# ============================================================
# VALID AGE RANGE
# (NOT STRICTLY APPLICABLE — KEPT FOR ENGINE CONSISTENCY)
# ============================================================

VALID_AGE_RANGE = (0, 120)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

TRAVEL_KEY_PLANETS: Set[str] = {
    "Moon",     # Comfort, mental state during travel
    "Mercury",  # Planning, tickets, communication
    "Venus",    # Comfort, luxury, pleasure travel
    "Jupiter",  # Pilgrimage, protection, blessings
    "Saturn",   # Long journeys, delays
    "Rahu",     # Foreign travel, unusual destinations
    "Mars"      # Accidents, conflicts, urgency
}


# ============================================================
# HOUSE GROUPS (for reuse in evaluators)
# ============================================================

SHORT_TRAVEL_HOUSES: Set[int] = {3}
LONG_TRAVEL_HOUSES: Set[int] = {7, 9}
FOREIGN_TRAVEL_HOUSES: Set[int] = {12}
OBSTACLE_HOUSES: Set[int] = {6, 8}
SUPPORT_HOUSES: Set[int] = {1, 4, 11}
PILGRIMAGE_HOUSES: Set[int] = {9, 12}
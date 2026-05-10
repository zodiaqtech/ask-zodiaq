"""
Lost / Missing Domain Rules
Vedic house significations and rules for lost items, missing persons,
theft vs loss analysis, recovery prospects, and direction guidance.

⚠️ NO KP rules
⚠️ NO timing guarantees
⚠️ Prashna-style Vedic interpretation only
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic scoring / promise logic)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Recovery & gain
    "positive_houses": {2, 4, 11},      # Possessions, home/property, recovery
    "supportive_houses": {1, 5, 9},     # Self-effort, intelligence, luck
    "negative_houses": {6, 8, 12},      # Theft, hidden matters, permanent loss
    "supportive_score": 2
}


# ============================================================
# TIMING RULES
# (USED ONLY FOR SOFT HINTS — NOT EXACT DATES)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # General recovery activation
    # --------------------------------------------------------
    "Recovery Timing": {
        "positive_houses": {2, 4, 11},
        "supportive_houses": {1, 5, 9},
        "negative_houses": {12},
        "key_planets": {"Jupiter", "Moon", "Mercury"}
    },

    # --------------------------------------------------------
    # Theft-related activation windows
    # --------------------------------------------------------
    "Theft Indication Timing": {
        "positive_houses": {6, 7},
        "supportive_houses": {8},
        "negative_houses": {2, 4, 11},
        "key_planets": {"Mars", "Rahu", "Saturn"}
    },

    # --------------------------------------------------------
    # Missing person investigation phase
    # --------------------------------------------------------
    "Missing Person Investigation": {
        "positive_houses": {7, 8, 11},
        "supportive_houses": {9},
        "negative_houses": {12},
        "key_planets": {"Moon", "Jupiter", "Saturn"}
    },

    # --------------------------------------------------------
    # Permanent loss / far away indication
    # --------------------------------------------------------
    "Permanent Loss Risk": {
        "positive_houses": {12},
        "supportive_houses": {8},
        "negative_houses": {2, 4, 11},
        "key_planets": {"Saturn", "Rahu", "Ketu"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Core normalization
    "Lost Item or Person": "Lost Item or Person",

    # Lost items
    "Lost Item": "Lost Item or Person",
    "Missing Belonging": "Lost Item or Person",
    "Lost Property": "Lost Item or Person",

    # Recovery
    "Recovery Prospects": "Recovery Timing",
    "Will I Find My Lost Item": "Recovery Timing",

    # Theft
    "Theft Analysis": "Theft Indication Timing",
    "Was It Stolen": "Theft Indication Timing",

    # Direction
    "Direction of Lost Item": "Direction Guidance",
    "Where to Search": "Direction Guidance",

    # Missing persons
    "Missing Person": "Missing Person Investigation",
    "Lost Person": "Missing Person Investigation"
}


# ============================================================
# VALID AGE RANGE
# (NOT APPLICABLE — KEPT FOR ENGINE CONSISTENCY)
# ============================================================

VALID_AGE_RANGE = (0, 120)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

LOST_MISSING_KEY_PLANETS: Set[str] = {
    "Moon",     # State of missing item/person
    "Mercury",  # Information, communication, documents
    "Mars",     # Theft, force, aggression
    "Saturn",   # Delay, distance, obstacles
    "Rahu",     # Deception, foreign/unusual places
    "Ketu",     # Separation, loss
    "Jupiter"   # Protection, recovery, grace
}


# ============================================================
# HOUSE GROUPS (for reuse in evaluators)
# ============================================================

PROPERTY_HOUSES: Set[int] = {2, 4}
RECOVERY_HOUSES: Set[int] = {11}
THEFT_HOUSES: Set[int] = {6, 7}
HIDDEN_HOUSES: Set[int] = {8}
LOSS_HOUSES: Set[int] = {12}
SUPPORT_HOUSES: Set[int] = {1, 5, 9}

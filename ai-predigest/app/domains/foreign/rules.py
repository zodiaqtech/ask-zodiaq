"""
Foreign Domain Rules

KP house significations and timing rules for foreign travel, settlement,
relocation, long-term residence, and adjustment abroad.

Astrology here indicates tendencies and opportunities related to foreign
lands and must be interpreted along with practical planning.
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic foreign promise / support scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core foreign indicators
    "positive_houses": {3, 9, 12},          # Travel, long-distance, foreign lands
    "supportive_houses": {4, 5, 7, 10},     # Residence, adjustment, growth, career
    "negative_houses": {2, 11},             # Financial strain / gains mismatch
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (used by KP timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Foreign settlement / long-term residence timing
    # --------------------------------------------------------
    "Foreign Timing": {
        "positive_houses": {9, 12},          # Long-distance & permanent relocation
        "supportive_houses": {4, 7, 10},     # Home abroad, partnerships, career
        "negative_houses": {2},              # Financial pressure
        "key_planets": {"Rahu", "Saturn", "Moon"}
    },

    # --------------------------------------------------------
    # Foreign travel / relocation (short or medium term)
    # --------------------------------------------------------
    "Foreign Travel": {
        "positive_houses": {3, 9, 12},       # Movement, travel, visas
        "supportive_houses": {5, 11},        # Opportunities, gains
        "negative_houses": {4},              # Separation from homeland
        "key_planets": {"Rahu", "Moon"}
    },

    # --------------------------------------------------------
    # Challenges, adjustment, income issues abroad
    # --------------------------------------------------------
    "Challenges in Foreign Land": {
        "positive_houses": {12},             # Isolation, unfamiliar environment
        "supportive_houses": {6, 10},        # Work, service, career effort
        "negative_houses": {4, 11},          # Emotional discomfort, expectations
        "key_planets": {"Saturn", "Rahu"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (registry-level matching)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Parent subtopic (CRITICAL)
    "Foreign Settlement": "Foreign Settlement",
    "Settlement Abroad": "Foreign Settlement",
    "Foreign Residence": "Foreign Settlement",

    # Timing
    "Foreign Settlement Timing": "Foreign Settlement Timing",
    "Settlement Timing": "Foreign Settlement Timing",

    "Foreign Travel": "Foreign Travel",
    "Abroad Travel": "Foreign Travel",

    # Challenges
    "Challenges in Foreign Land": "Challenges in Foreign Land",
    "Adjustment Abroad": "Challenges in Foreign Land",
    "Income Abroad": "Challenges in Foreign Land",

    # Remedies
    "Remedies (Foreign Domain)": "Remedies (Foreign Domain)",
    "Foreign Remedies": "Remedies (Foreign Domain)"
}


# ============================================================
# VALID AGE RANGE (used by timing filters)
# ============================================================

VALID_AGE_RANGE = (16, 90)


# ============================================================
# KEY PLANETS (foreign significators)
# ============================================================

FOREIGN_KEY_PLANETS: Set[str] = {
    "Rahu",     # Foreign connection, migration, non-native lands
    "Moon",     # Movement, travel, adaptability
    "Saturn",   # Long stay, settlement, hardship abroad
    "Jupiter", # Legal status, guidance, expansion
    "Venus"    # Comfort, lifestyle, settlement quality
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

FOREIGN_HOUSES: Set[int] = {3, 9, 12}
SETTLEMENT_HOUSES: Set[int] = {4, 7, 10, 12}
ADJUSTMENT_HOUSES: Set[int] = {4, 6, 11}

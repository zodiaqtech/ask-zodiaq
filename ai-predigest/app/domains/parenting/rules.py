"""
Parenting / Children Domain Rules
KP house significations and timing rules for childbirth & parenting matters
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (used for generic promise / scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Childbirth & continuation
    "positive_houses": {2, 5, 11},      # Family expansion, progeny, fulfilment
    "supportive_houses": {1, 7, 9},     # Body, partner, destiny
    "negative_houses": {6, 8, 12},      # Disease, loss, denial
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (plugged into generic timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Core childbirth timing
    # --------------------------------------------------------
    "Timing of Childbirth": {
        "positive_houses": {2, 5, 11},
        "supportive_houses": {1, 7, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Moon", "Venus"}
    },

    # --------------------------------------------------------
    # Miscarriage / child-loss risk windows
    # --------------------------------------------------------
    "Miscarriage Risk Timing": {
        "positive_houses": {6, 8, 12},
        "supportive_houses": {1, 5},
        "negative_houses": {2, 11},
        "key_planets": {"Saturn", "Mars", "Rahu", "Ketu"}
    },

    # --------------------------------------------------------
    # Adoption-related activation windows
    # --------------------------------------------------------
    "Adoption Timing": {
        "positive_houses": {6, 8, 12},
        "supportive_houses": {5, 11},
        "negative_houses": {2},
        "key_planets": {"Saturn", "Rahu", "Ketu", "Mercury"}
    },

    # --------------------------------------------------------
    # Second child / extended family planning
    # --------------------------------------------------------
    "Second Child Timing": {
        "positive_houses": {2, 5, 11},
        "supportive_houses": {9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Moon", "Venus"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (flexible matching from UI / API)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Parent subtopic normalization (CRITICAL)
    "Family Planning and Parenting": "Family Planning And Parenting",
    # Core
    "Timing of Childbirth": "Timing of Childbirth",
    "Childbirth Timing": "Timing of Childbirth",

    # Conception
    "Best Time to Conceive": "Timing of Childbirth",
    "Conception Timing": "Timing of Childbirth",

    # Risk
    "Miscarriage Risk": "Miscarriage Risk Timing",
    "Child Loss Timing": "Miscarriage Risk Timing",

    # Adoption
    "Adoption Indicators": "Adoption Timing",
    "Adoption Timing": "Adoption Timing",

    # Extended
    "Second Child Timing": "Second Child Timing"
}


# ============================================================
# VALID AGE RANGE (used by timing engine filters)
# ============================================================

VALID_AGE_RANGE = (18, 50)


# ============================================================
# KEY PLANETS (used by evaluators & LLM prompts)
# ============================================================

PARENTING_KEY_PLANETS: Set[str] = {
    "Jupiter",   # Karaka for children
    "Moon",     # Fertility, cycles
    "Venus",    # Reproduction
    "Saturn",   # Delay / karma
    "Rahu",     # Medical / IVF / adoption
    "Ketu"      # Separation / loss
}


# ============================================================
# HOUSE GROUPS (for reuse in evaluators)
# ============================================================

CHILD_HOUSES: Set[int] = {2, 5, 11}
OBSTACLE_HOUSES: Set[int] = {6, 8, 12}
SUPPORT_HOUSES: Set[int] = {1, 7, 9}

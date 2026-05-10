"""
Health Domain Rules

KP house significations and timing rules for physical and mental health analysis,
including disease occurrence, cure timing, chronic risks, and remedies.

⚠️ Astrology is supportive in nature and must not replace medical diagnosis.
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic health promise / stress scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Disease, obstruction, hospitalization
    "positive_houses": {6, 8, 12},     # Disease, chronicity, loss of vitality
    "supportive_houses": {1},          # Body, constitution, recovery capacity
    "negative_houses": {2, 5, 11},     # Strength, immunity, improvement
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (used by KP timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Disease onset / aggravation timing
    # --------------------------------------------------------
    "Disease Occurrence": {
        "positive_houses": {6, 8, 12},     # Core disease houses
        "supportive_houses": {1},          # Body manifestation
        "negative_houses": {5, 11},        # Relief / recovery houses
        "key_planets": {"Saturn", "Mars", "Rahu", "Ketu"}
    },

    # --------------------------------------------------------
    # Cure / recovery / improvement timing
    # --------------------------------------------------------
    "Cure Timing": {
        "positive_houses": {5, 11},        # Improvement & fulfilment
        "supportive_houses": {1, 6},       # Body + treatment
        "negative_houses": {8, 12},        # Chronicity / hospitalization
        "key_planets": {"Jupiter", "Mercury", "Venus"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (registry-level matching)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Parent subtopic (CRITICAL)
    "Physical and Mental Health": "Physical And Mental Health",

    # Timing
    "Disease Occurrence": "Disease Occurrence",
    "Disease Timing": "Disease Occurrence",
    "Illness Timing": "Disease Occurrence",

    "Cure Timing": "Cure Timing",
    "Recovery Timing": "Cure Timing",
    "Healing Period": "Cure Timing",

    # Non-timing (handled inside evaluator)
    "General Health Analysis": "General Health Analysis",
    "Organ-Specific Issues": "Organ-Specific Issues",
    "Mental Health Risks": "Mental Health Risks",
    "Remedies (Health Domain)": "Remedies And Suggestions"
}


# ============================================================
# VALID AGE RANGE (used by timing filters)
# ============================================================

VALID_AGE_RANGE = (0, 90)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

HEALTH_KEY_PLANETS: Set[str] = {
    "Sun",      # Vitality, immunity
    "Moon",     # Mind, fluids, mental health
    "Mars",     # Surgery, inflammation, accidents
    "Mercury",  # Nervous system, skin
    "Jupiter",  # Healing, recovery
    "Venus",    # Hormones, reproductive health
    "Saturn",   # Chronic disease, pain
    "Rahu",     # Sudden illness, toxicity
    "Ketu"      # Isolation, hidden disease
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

DISEASE_HOUSES: Set[int] = {6, 8, 12}
RECOVERY_HOUSES: Set[int] = {1, 5, 11}
VITALITY_HOUSES: Set[int] = {1, 2, 5}

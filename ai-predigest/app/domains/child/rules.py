"""
Child Domain Rules
KP house significations and timing rules for:
- Child education, aptitude, and academic growth
- Higher education, scholarships, and foreign studies
- Physical and mental health guidance for children
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic child promise & scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core child development & growth
    "positive_houses": {2, 5, 11},        # Growth, intelligence, gains
    "supportive_houses": {4, 9},          # Education, fortune, guidance
    "negative_houses": {6, 8, 12},         # Illness, obstacles, loss
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (plugged into KP Timing Engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Higher education, exams, academic success
    # --------------------------------------------------------
    "Education Timing": {
        "positive_houses": {4, 5, 9, 11},
        "supportive_houses": {2, 10},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Mercury", "Jupiter", "Moon"}
    },

    # --------------------------------------------------------
    # College admission / scholarships
    # --------------------------------------------------------
    "Higher Education Timing": {
        "positive_houses": {4, 9, 11},
        "supportive_houses": {2, 5, 10},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Mercury", "Venus"}
    },

    # --------------------------------------------------------
    # Foreign education / overseas studies
    # --------------------------------------------------------
    "Foreign Higher Education Timing": {
        "positive_houses": {9, 12, 11},
        "supportive_houses": {3, 4, 5},
        "negative_houses": {6, 8},
        "key_planets": {"Rahu", "Jupiter", "Mercury"}
    },

    # --------------------------------------------------------
    # Child health risk & recovery (soft advisory use)
    # --------------------------------------------------------
    "Child Health Timing": {
        "positive_houses": {1, 5, 11},      # Vitality, recovery, support
        "supportive_houses": {4, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Moon", "Jupiter", "Sun"}
    }
}


# ============================================================
# SUBTOPIC CANONICAL NAMES
# ============================================================

SUBTOPIC_CANONICAL: Dict[str, str] = {
    "Education Guidance": "Education Guidance",
    "Health Guidance": "Health Guidance"
}


# ============================================================
# SUBTOPIC ALIASES (CRITICAL for registry matching)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # --- Education Guidance (DIRECT MAPPING) ---
    "Education Guidance": "Education Guidance",
    "education_guidance": "Education Guidance",
    "education-guidance": "Education Guidance",
    
    # --- Education Guidance (ALIASES) ---
    "Aptitude and Education of Child": "Education Guidance",
    "Prospects of Success": "Education Guidance",
    "Prospects of College": "Education Guidance",
    "Prospects of Foreign Education": "Education Guidance",
    "Child Education": "Education Guidance",

    # --- Health Guidance (DIRECT MAPPING) ---
    "Health Guidance": "Health Guidance",
    "health_guidance": "Health Guidance",
    "health-guidance": "Health Guidance",
    
    # --- Health Guidance (ALIASES) ---
    "Health of Child": "Health Guidance",
    "Child Health": "Health Guidance",
    "Physical and Mental Growth": "Health Guidance"
}


# ============================================================
# VALID AGE RANGE (used by timing engine)
# ============================================================

VALID_AGE_RANGE = (0, 25)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

CHILD_KEY_PLANETS: Set[str] = {
    "Moon",      # Mind, growth, nourishment
    "Jupiter",   # Wisdom, education, guidance
    "Mercury",   # Learning, intellect, exams
    "Venus",     # Comfort, harmony, creativity
    "Sun"        # Vitality, confidence
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

EDUCATION_HOUSES: Set[int] = {4, 5, 9, 11}
HEALTH_HOUSES: Set[int] = {1, 6, 8, 12}
SUPPORT_HOUSES: Set[int] = {2, 4, 9}
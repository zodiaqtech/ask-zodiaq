"""
Career Domain Rules
KP house significations and timing rules for career, job, promotion,
career shift, business, and professional growth matters
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic promise / scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core career manifestation
    "positive_houses": {2, 6, 10, 11},          # Income, service, profession, gains
    "supportive_houses": {3, 5, 7, 9, 12},      # Effort, skills, business, growth, foreign link
    "negative_houses": {8, 12},                 # Breaks, instability
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (plugged into generic timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Job start / employment timing
    # --------------------------------------------------------
    "Job Start Timing": {
        "positive_houses": {2, 6, 10, 11},
        "supportive_houses": {3, 9, 12},
        "negative_houses": {8},
        "key_planets": {"Sun", "Saturn", "Mercury", "Rahu"}
    },

    # --------------------------------------------------------
    # Promotion / authority / recognition
    # --------------------------------------------------------
    "Promotion Timing": {
        "positive_houses": {10, 11},
        "supportive_houses": {2, 6},
        "negative_houses": {8, 12},
        "key_planets": {"Sun", "Jupiter", "Saturn"}
    },

    # --------------------------------------------------------
    # Career shift / job change
    # --------------------------------------------------------
    "Career Shift Timing": {
        "positive_houses": {7, 11, 12},
        "supportive_houses": {3, 9},
        "negative_houses": {6},
        "key_planets": {"Rahu", "Mercury", "Venus"}
    },

    # --------------------------------------------------------
    # Business start / entrepreneurship
    # --------------------------------------------------------
    "Business Start Timing": {
        "positive_houses": {3, 5, 7, 9, 11},
        "supportive_houses": {2, 12},
        "negative_houses": {6, 8},
        "key_planets": {"Mercury", "Mars", "Venus", "Rahu"}
    },

    # --------------------------------------------------------
    # Foreign career / overseas job
    # --------------------------------------------------------
    "Foreign Career Timing": {
        "positive_houses": {3, 9, 12},
        "supportive_houses": {10, 11},
        "negative_houses": {6, 8},
        "key_planets": {"Rahu", "Saturn", "Moon"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Career discovery
    "Career Overview": "Career Analysis",
    "Service or Business": "Career Analysis",
    "Government vs Private Career": "Career Analysis",
    "Suitable Career Field": "Career Analysis",

    # Employment
    "Finding a Job": "Job Start Timing",
    "Job Timing": "Job Start Timing",

    # Growth
    "Promotion and Growth": "Promotion Timing",
    "Promotion Timing": "Promotion Timing",

    # Change
    "Career Change Timing": "Career Shift Timing",
    "Job Change Timing": "Career Shift Timing",

    # Business
    "Business Timing": "Business Start Timing",

    # Foreign
    "Foreign Career Potential": "Foreign Career Timing",
    "Foreign Job Timing": "Foreign Career Timing"
}


# ============================================================
# VALID AGE RANGE (used by timing engine)
# ============================================================

VALID_AGE_RANGE = (18, 70)


# ============================================================
# KEY PLANETS (used by evaluators & LLM prompts)
# ============================================================

CAREER_KEY_PLANETS: Set[str] = {
    "Sun",      # Authority, leadership
    "Saturn",   # Work, stability, service
    "Mercury",  # Skills, business, communication
    "Jupiter",  # Growth, promotions
    "Venus",    # Comfort, creative professions
    "Mars",     # Action, engineering, entrepreneurship
    "Rahu"      # Foreign, unconventional paths
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

CAREER_HOUSES: Set[int] = {2, 6, 10, 11}
GROWTH_HOUSES: Set[int] = {9, 11}
BUSINESS_HOUSES: Set[int] = {3, 5, 7}
FOREIGN_HOUSES: Set[int] = {3, 9, 12}
RISK_HOUSES: Set[int] = {6, 8, 12}

"""
Business Domain Rules
KP house significations and timing rules for:
- Starting new business
- Growing existing business
- Business challenges, stagnation, shutdown decisions
"""

from typing import Dict, Set, Any

# ============================================================
# DOMAIN-LEVEL RULES (generic business promise / scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core business manifestation houses
    "positive_houses": {2, 7, 10, 11},     # Income, trade, authority, gains
    "supportive_houses": {3, 5, 9, 12},    # Effort, strategy, expansion, foreign
    "negative_houses": {6, 8},             # Debt, disputes, sudden breaks
    "supportive_score": 2,
    "key_planets": {
        "Mercury",   # Business, trade, analytics
        "Jupiter",   # Expansion, capital, advisors
        "Saturn",    # Stability, long-term enterprise
        "Mars",      # Initiative, risk-taking
        "Rahu"       # Scale, unconventional growth
    }
}

# ============================================================
# TIMING RULES (plugged into generic timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

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
    # Business growth / expansion
    # --------------------------------------------------------
    "Best Periods for Business Growth": {
        "positive_houses": {2, 10, 11},
        "supportive_houses": {3, 5, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Mercury", "Venus"}
    },

    # --------------------------------------------------------
    # Loan taking for business
    # --------------------------------------------------------
    "Loan Taking Timing": {
        "positive_houses": {6, 8, 12},
        "supportive_houses": {2, 10, 11},
        "negative_houses": {1},
        "key_planets": {"Mars", "Saturn", "Rahu", "Ketu"}
    },

    # --------------------------------------------------------
    # Loan repayment for business
    # --------------------------------------------------------
    "Loan Repayment Timing": {
        "positive_houses": {2, 10, 11},
        "supportive_houses": {5, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Venus", "Mercury"}
    }
}

# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Starting business
    "Service or Business": "Business Prospects",
    "Entrepreneurship Potential": "Business Prospects",
    "Industry Suitability": "Business Prospects",

    # Start timing
    "Business Launch Timing": "Business Start Timing",
    "When should I start business": "Business Start Timing",

    # Growth
    "Business Expansion Timing": "Best Periods for Business Growth",
    "Scaling Business": "Best Periods for Business Growth",

    # Challenges
    "Business Stagnation": "Reason for Business Challenges",
    "Business Losses": "Reason for Business Challenges",
    "Why business not working": "Reason for Business Challenges",

    # Decision
    "Close Business": "Continue or Shut Down",
    "Exit Business Decision": "Continue or Shut Down"
}

# ============================================================
# VALID AGE RANGE (used by timing engine)
# ============================================================

VALID_AGE_RANGE = (21, 70)

# ============================================================
# KEY PLANETS (used by evaluators & LLM prompts)
# ============================================================

BUSINESS_KEY_PLANETS: Set[str] = {
    "Mercury",  # Commerce, negotiation
    "Jupiter",  # Capital, advisors, scaling
    "Saturn",   # Stability, long-term effort
    "Mars",     # Initiative, competition
    "Venus",    # Luxury, branding, profits
    "Rahu"      # Mass scale, foreign, tech
}

# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

BUSINESS_CORE_HOUSES: Set[int] = {2, 7, 10, 11}
EXPANSION_HOUSES: Set[int] = {3, 5, 9}
RISK_HOUSES: Set[int] = {6, 8, 12}
FOREIGN_BUSINESS_HOUSES: Set[int] = {9, 12}

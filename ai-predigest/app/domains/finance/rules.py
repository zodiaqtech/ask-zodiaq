"""
Finance Domain Rules
KP house significations and timing rules for income, loans, investments,
property, assets, and financial stability.
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic finance promise & scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core wealth & income
    "positive_houses": {2, 10, 11},        # Income, profession, gains
    "supportive_houses": {1, 5, 9},        # Effort, intelligence, fortune
    "negative_houses": {6, 8, 12},         # Debt, loss, blockage
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (plugged into KP Timing Engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Loan repayment / debt clearance
    # --------------------------------------------------------
    "Loan Repayment Timing": {
        "positive_houses": {2, 10, 11},
        "supportive_houses": {1, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Mercury", "Saturn"}
    },

    # --------------------------------------------------------
    # Income rise / financial growth
    # --------------------------------------------------------
    "Income Growth Timing": {
        "positive_houses": {2, 10, 11},
        "supportive_houses": {5, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Mercury", "Venus"}
    },

    # --------------------------------------------------------
    # Investment activation (equity, MF, business capital)
    # --------------------------------------------------------
    "Investment Timing": {
        "positive_houses": {2, 5, 11},
        "supportive_houses": {9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Mercury"}
    },

    # --------------------------------------------------------
    # Property / land / house purchase
    # --------------------------------------------------------
    "Prospects of Property": {
        "positive_houses": {2, 4, 11},
        "supportive_houses": {10},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Mars", "Venus", "Jupiter"}
    },

    # --------------------------------------------------------
    # Vehicle / movable asset purchase
    # --------------------------------------------------------
    "Vehicle Purchase Timing": {
        "positive_houses": {2, 3, 11},
        "supportive_houses": {10},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Venus", "Mars"}
    },

    # --------------------------------------------------------
    # Financial disputes / losses / litigation
    # --------------------------------------------------------
    "Financial Dispute Timing": {
        "positive_houses": {6, 8, 12},
        "supportive_houses": {1, 10},
        "negative_houses": {2, 11},
        "key_planets": {"Saturn", "Rahu", "Mars"}
    }
}

SUBTOPIC_CANONICAL = {
    "Prospects Of Investments": "Prospects Of Investments",
    "Buying Home Or Land": "Buying Home Or Land",
}

# ============================================================
# SUBTOPIC ALIASES (CRITICAL for registry matching)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Parent finance subtopics

    "Income Growth": "Income Growth Timing",
    "Overall Financial Status": "Income Growth Timing",
    

    # Loans
    "Loan Repayment Timing": "Loan Repayment Timing",
    "Loan Default Risk": "Loan Repayment Timing",
    "Debt Clearance": "Loan Repayment Timing",

    # Property

    "Property Purchase": "Prospects of Property",


    # Vehicle
    "Vehicle Purchase": "Vehicle Purchase Timing",
    "Buying Vehicle": "Vehicle Purchase Timing",

    # Disputes
    "Financial Dispute Risk": "Financial Dispute Timing",
    "Property Dispute": "Financial Dispute Timing",
    "Court Case Related to Money": "Financial Dispute Timing"
}


# ============================================================
# VALID AGE RANGE (used by timing engine)
# ============================================================

VALID_AGE_RANGE = (18, 80)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

FINANCE_KEY_PLANETS: Set[str] = {
    "Jupiter",   # Wealth expansion, prosperity
    "Mercury",   # Trade, accounting, finance
    "Venus",     # Assets, vehicles, luxury
    "Mars",      # Property, land, construction
    "Saturn",    # Loans, delay, repayment karma
    "Rahu",      # Speculation, risk, foreign income
    "Ketu"       # Sudden loss / detachment
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

INCOME_HOUSES: Set[int] = {2, 10, 11}
ASSET_HOUSES: Set[int] = {2, 3, 4, 11}
OBSTACLE_HOUSES: Set[int] = {6, 8, 12}
SUPPORT_HOUSES: Set[int] = {1, 5, 9}

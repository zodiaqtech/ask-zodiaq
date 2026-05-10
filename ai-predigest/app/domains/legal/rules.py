"""
Legal Domain Rules
Vedic house significations and rules for legal matters,
court cases, disputes, litigation, settlements, and risks.

⚠️ NO KP rules
⚠️ NO absolute verdict guarantees
⚠️ Vedic / Prashna-style interpretation only
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic scoring / promise logic)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Legal strength & resolution
    "positive_houses": {6, 10, 11},     # Disputes, authority, victory/gains
    "supportive_houses": {1, 2, 9},     # Self-effort, resources, justice/luck
    "negative_houses": {8, 12},         # Sudden losses, hidden issues, expenses
    "supportive_score": 2
}


# ============================================================
# TIMING RULES
# (USED ONLY FOR SOFT HINTS — NOT EXACT DATES)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # General legal case progress
    # --------------------------------------------------------
    "Legal Timing": {
        "positive_houses": {6, 10, 11},
        "supportive_houses": {1, 2, 9},
        "negative_houses": {8, 12},
        "key_planets": {"Saturn", "Jupiter", "Mercury"}
    },

    # --------------------------------------------------------
    # Court case & litigation focus
    # --------------------------------------------------------
    "Court Case Timing": {
        "positive_houses": {6, 10},
        "supportive_houses": {11},
        "negative_houses": {8, 12},
        "key_planets": {"Saturn", "Mars", "Jupiter"}
    },

    # --------------------------------------------------------
    # Settlement / compromise possibility
    # --------------------------------------------------------
    "Settlement Timing": {
        "positive_houses": {2, 7, 11},
        "supportive_houses": {9},
        "negative_houses": {6, 8},
        "key_planets": {"Venus", "Mercury", "Jupiter"}
    },

    # --------------------------------------------------------
    # Legal delay / adverse risk
    # --------------------------------------------------------
    "Legal Delay Risk": {
        "positive_houses": {8, 12},
        "supportive_houses": {6},
        "negative_houses": {10, 11},
        "key_planets": {"Saturn", "Rahu", "Ketu"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Core normalization
    "Legal": "Legal",

    # Court & litigation
    "Court Case": "Court Case Timing",
    "Litigation": "Court Case Timing",
    "Legal Case": "Court Case Timing",

    # General legal timing
    "Legal Timing": "Legal Timing",
    "Case Timing": "Legal Timing",
    "When Will Case Move": "Legal Timing",

    # Settlement
    "Settlement": "Settlement Timing",
    "Compromise": "Settlement Timing",
    "Out of Court Settlement": "Settlement Timing",

    # Risks
    "Legal Risks": "Legal Delay Risk",
    "Case Delay": "Legal Delay Risk",
    "Will Case Get Delayed": "Legal Delay Risk"
}


# ============================================================
# VALID AGE RANGE
# (NOT STRICTLY APPLICABLE — KEPT FOR ENGINE CONSISTENCY)
# ============================================================

VALID_AGE_RANGE = (0, 120)


# ============================================================
# KEY PLANETS (used by evaluators & prompts)
# ============================================================

LEGAL_KEY_PLANETS: Set[str] = {
    "Saturn",   # Law, delays, justice, karma
    "Jupiter",  # Judgment, wisdom, legal protection
    "Mars",     # Conflict, aggression, litigation
    "Mercury",  # Documents, arguments, communication
    "Venus",    # Settlement, compromise, agreements
    "Rahu",     # Legal complications, manipulation
    "Ketu"      # Separation, withdrawal, closure
}


# ============================================================
# HOUSE GROUPS (for reuse in evaluators)
# ============================================================

DISPUTE_HOUSES: Set[int] = {6}
AUTHORITY_HOUSES: Set[int] = {10}
GAIN_HOUSES: Set[int] = {11}
LOSS_HOUSES: Set[int] = {8, 12}
SETTLEMENT_HOUSES: Set[int] = {2, 7}
SUPPORT_HOUSES: Set[int] = {1, 9}

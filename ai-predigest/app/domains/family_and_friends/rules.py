"""
Family and Friends Domain Rules
KP house significations and timing rules for family relationships,
parents, siblings, extended family, friendships, and social status matters
"""

from typing import Dict, Set, Any


# ============================================================
# DOMAIN-LEVEL RULES (generic promise / scoring)
# ============================================================

DOMAIN_RULES: Dict[str, Any] = {
    # Core family & social manifestation
    "positive_houses": {2, 4, 5, 11},           # Family, home, children, friends/gains
    "supportive_houses": {1, 3, 7, 9, 10},      # Self, siblings, partnerships, fortune, status
    "negative_houses": {6, 8, 12},              # Disputes, hidden issues, losses
    "supportive_score": 2
}


# ============================================================
# TIMING RULES (plugged into generic timing engine)
# ============================================================

TIMING_RULES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # Family harmony / reconciliation timing
    # --------------------------------------------------------
    "Family Harmony Timing": {
        "positive_houses": {2, 4, 9, 11},
        "supportive_houses": {1, 5, 7},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Moon", "Jupiter", "Venus"}
    },

    # --------------------------------------------------------
    # Parents relationship timing
    # --------------------------------------------------------
    "Parents Relationship Timing": {
        "positive_houses": {4, 9, 10},
        "supportive_houses": {1, 2, 5},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Sun", "Moon", "Jupiter", "Saturn"}
    },

    # --------------------------------------------------------
    # Siblings relationship timing
    # --------------------------------------------------------
    "Siblings Relationship Timing": {
        "positive_houses": {3, 11},
        "supportive_houses": {1, 2, 5, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Mars", "Mercury", "Jupiter"}
    },

    # --------------------------------------------------------
    # Inheritance / ancestral property timing
    # --------------------------------------------------------
    "Inheritance Timing": {
        "positive_houses": {2, 4, 8, 9},
        "supportive_houses": {5, 11},
        "negative_houses": {6, 12},
        "key_planets": {"Jupiter", "Saturn", "Mars", "Moon"}
    },

    # --------------------------------------------------------
    # Friendship / social gains timing
    # --------------------------------------------------------
    "Friendship Gains Timing": {
        "positive_houses": {3, 5, 11},
        "supportive_houses": {1, 7, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Jupiter", "Venus", "Mercury", "Moon"}
    },

    # --------------------------------------------------------
    # Recognition / honours timing
    # --------------------------------------------------------
    "Recognition Timing": {
        "positive_houses": {5, 10, 11},
        "supportive_houses": {1, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Sun", "Jupiter", "Rahu"}
    },

    # --------------------------------------------------------
    # Social standing improvement timing
    # --------------------------------------------------------
    "Social Status Timing": {
        "positive_houses": {1, 10, 11},
        "supportive_houses": {5, 7, 9},
        "negative_houses": {6, 8, 12},
        "key_planets": {"Sun", "Jupiter", "Venus", "Mercury"}
    }
}


# ============================================================
# SUBTOPIC ALIASES (UI / API normalization)
# ============================================================

SUBTOPIC_ALIASES: Dict[str, str] = {

    # Parents and Siblings
    "Relationship with Parents": "Parents Relationship Timing",
    "Parents Relationship": "Parents Relationship Timing",
    "Mother Relationship": "Parents Relationship Timing",
    "Father Relationship": "Parents Relationship Timing",
    "Relationship with Siblings": "Siblings Relationship Timing",
    "Siblings Relationship": "Siblings Relationship Timing",
    "Brother Relationship": "Siblings Relationship Timing",
    "Sister Relationship": "Siblings Relationship Timing",

    # Extended Family
    "Family Relations": "Family Harmony Timing",
    "Joint Family": "Family Harmony Timing",
    "Extended Family": "Family Harmony Timing",
    "Inheritance Disputes": "Inheritance Timing",
    "Ancestral Property": "Inheritance Timing",

    # Friendship
    "Friendship Compatibility": "Friendship Gains Timing",
    "Strength Of Friendships": "Strength Of Friendships",
    "Friend Circle": "Friendship Gains Timing",

    # Social Status and Reputation
    "Recognition and Honour": "Recognition Timing",
    "Honours and Awards": "Recognition Timing",
    "Risk to Reputation": "Social Status Timing",
    "Reputation Risk": "Social Status Timing",
    "Social Relationships": "Social Status Timing",
    "Social Standing": "Social Status Timing"
}


# ============================================================
# VALID AGE RANGE (used by timing engine)
# ============================================================

VALID_AGE_RANGE = (5, 90)


# ============================================================
# KEY PLANETS (used by evaluators & LLM prompts)
# ============================================================

FAMILY_KEY_PLANETS: Set[str] = {
    "Moon",     # Mother, emotions, family bonds
    "Sun",      # Father, authority, recognition
    "Jupiter",  # Elders, blessings, wisdom, prosperity
    "Venus",    # Harmony, love, social charm
    "Mars",     # Siblings, courage, conflicts
    "Mercury",  # Communication, younger siblings
    "Saturn"    # Responsibilities, karma, elder care
}

FRIENDSHIP_KEY_PLANETS: Set[str] = {
    "Jupiter",  # True friends, wisdom, good company
    "Venus",    # Social charm, harmony, likability
    "Mercury",  # Communication, intellectual connections
    "Moon",     # Emotional bonds, intuition
    "Saturn",   # Long-lasting friendships, loyalty
    "Rahu"      # Unconventional friends, sudden connections
}

SOCIAL_STATUS_KEY_PLANETS: Set[str] = {
    "Sun",      # Authority, fame, recognition
    "Jupiter",  # Respect, honours, blessings
    "Saturn",   # Long-term reputation, public service
    "Venus",    # Charm, likability, arts recognition
    "Mercury",  # Communication, media, public speaking
    "Rahu"      # Sudden fame, unconventional recognition
}


# ============================================================
# HOUSE GROUPS (for evaluator reuse)
# ============================================================

# Family Houses
FAMILY_HOUSES: Set[int] = {2, 4, 9}             # Kutumb, home/mother, father
PARENTS_HOUSES: Set[int] = {4, 9, 10}           # Mother, father, authority
SIBLINGS_HOUSES: Set[int] = {3, 11}             # Younger siblings, elder siblings
EXTENDED_FAMILY_HOUSES: Set[int] = {2, 4, 8, 9} # Family, property, inheritance, elders

# Friendship Houses
FRIENDSHIP_HOUSES: Set[int] = {3, 5, 11}        # Communication, recreation, friends
SOCIAL_CIRCLE_HOUSES: Set[int] = {1, 7, 11}     # Self, partnerships, social network

# Social Status Houses
REPUTATION_HOUSES: Set[int] = {1, 10, 11}       # Self, public image, achievements
RECOGNITION_HOUSES: Set[int] = {5, 10, 11}      # Honours, status, gains

# Risk Houses
DISPUTE_HOUSES: Set[int] = {6, 8, 12}           # Disputes, hidden enemies, losses
ENEMY_HOUSES: Set[int] = {6, 8, 12}             # Open enemies, hidden enemies, secret enemies

# Inheritance Houses
INHERITANCE_HOUSES: Set[int] = {2, 4, 8}        # Family wealth, property, legacies


# ============================================================
# KARAKA (SIGNIFICATOR) MAPPINGS
# ============================================================

KARAKA_MAPPINGS: Dict[str, str] = {
    # Family Karakas
    "mother": "Moon",
    "father": "Sun",
    "siblings": "Mars",
    "younger_siblings": "Mars",
    "elder_siblings": "Jupiter",
    "family": "Jupiter",
    "elders": "Jupiter",
    "ancestors": "Saturn",
    
    # Social Karakas
    "friends": "Jupiter",
    "social_charm": "Venus",
    "communication": "Mercury",
    "recognition": "Sun",
    "fame": "Sun",
    "reputation": "Jupiter",
    "honours": "Jupiter"
}


# ============================================================
# RELATIONSHIP QUALITY THRESHOLDS
# ============================================================

QUALITY_THRESHOLDS: Dict[str, Dict[str, int]] = {
    "harmony": {
        "EXCELLENT": 75,
        "GOOD": 60,
        "MODERATE": 45,
        "CHALLENGING": 30,
        "DIFFICULT": 0
    },
    "dispute": {
        "LOW": 35,
        "MODERATE": 50,
        "HIGH": 100
    },
    "recognition": {
        "EXCELLENT": 75,
        "GOOD": 60,
        "MODERATE": 45,
        "LIMITED": 30,
        "CHALLENGING": 0
    },
    "risk": {
        "LOW": 40,
        "MODERATE": 60,
        "HIGH": 100
    }
}
"""
Marriage Domain Rules - KP house significations and timing rules
"""
from typing import Dict, Set, Any

# Domain-level KP rules for Marriage
DOMAIN_RULES: Dict[str, Any] = {
    "positive_houses": {2, 7, 11},
    "supportive_houses": {5},
    "negative_houses": {6, 8, 12},
    "supportive_score": 2
}

# Subtopic-specific timing rules
TIMING_RULES: Dict[str, Dict[str, Any]] = {
    "Marriage Timing": {
        "positive_houses": {2, 7, 11},
        "supportive_houses": {5},
        "negative_houses": {1, 6, 10, 12},
        "key_planets": {"Venus", "Jupiter", "Moon"}
    },
    "Divorce Timing": {
        "positive_houses": {6, 8, 12},
        "supportive_houses": {2, 7, 11},
        "key_planets": {"Saturn", "Rahu", "Mars", "Ketu"}
    },
    "Remarriage Timing": {
        "positive_houses": {2, 7, 9, 11},
        "supportive_houses": {5},
        "key_planets": {"Venus", "Jupiter", "Moon", "Mercury"}
    }
}

# Subtopic aliases for flexible matching
SUBTOPIC_ALIASES: Dict[str, str] = {
    # Marriage Prospects aliases
    "Marriage Prospects": "Marriage Prospects",
    "Prospects": "Marriage Prospects",
    "Marriage_Prospects": "Marriage Prospects",
    "marriage_prospects": "Marriage Prospects",
    
    # Marital Stability aliases
    "Marital Stability": "Marital Stability",
    "Stability": "Marital Stability",
    "Stability and Challenges": "Marital Stability",
    "Marital_Stability": "Marital Stability",
    "marital_stability": "Marital Stability",
    
    # Compatibility aliases
    "Marriage Compatibility": "Marriage Compatibility",
    "Compatibility": "Marriage Compatibility",
    "Marriage_Compatibility": "Marriage Compatibility",
    "marriage_compatibility": "Marriage Compatibility",
    
    # Kundali Matching and Timing aliases (NEW)
    "Kundali Matching and Timing": "Kundali Matching Timing",
    "Kundali Matching And Timing": "Kundali Matching Timing",
    "kundali_matching_timing": "Kundali Matching Timing",
    "Kundali Matching Timing": "Kundali Matching Timing",
    "Kundali Milan": "Kundali Matching Timing",
    "kundali milan": "Kundali Matching Timing",
    "Kundali_Matching_Timing": "Kundali Matching Timing",
    "vivah yog": "Kundali Matching Timing",
    "Vivah Yog": "Kundali Matching Timing",
}

# Valid age range for marriage timing windows
VALID_AGE_RANGE = (18, 45)

# Key planets for marriage analysis
MARRIAGE_KEY_PLANETS: Set[str] = {"Venus", "Jupiter", "Moon", "Mars"}

# Benefic planets for marriage
MARRIAGE_BENEFICS: Set[str] = {"Venus", "Jupiter", "Moon", "Mercury"}

# Houses significant for marriage
MARRIAGE_HOUSES: Set[int] = {2, 7, 11}
OBSTACLE_HOUSES: Set[int] = {6, 8, 12}
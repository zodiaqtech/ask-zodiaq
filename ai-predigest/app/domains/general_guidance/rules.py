"""
General Guidance Domain Rules

Defines KP house significations and aliases for General Guidance subtopics.
"""

# General Guidance domain rules
DOMAIN_RULES = {
    "positive_houses": {1, 2, 3, 4, 5, 9, 10, 11},  # Overall beneficial houses
    "supportive_houses": {7},  # Partnership support
    "supportive_score": 2
}

# Subtopic aliases for backward compatibility
SUBTOPIC_ALIASES = {
    "general_kundali_analysis": "General Kundali Analysis",
    "general-kundali-analysis": "General Kundali Analysis",
    "Spiritual and Self Growth": "Spiritual Self Growth",  # ← UI sends this!
    "Spiritual And Self Growth": "Spiritual Self Growth",  # ← After .title() normalization!
    "spiritual and self growth": "Spiritual Self Growth",
    "kundali": "General Kundali Analysis",
    "kundali_analysis": "General Kundali Analysis"
}

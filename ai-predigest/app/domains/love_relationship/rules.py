"""
Domain Rules for Love_Relationship

Defines when this domain should be triggered based on user queries.
"""
from typing import Dict, Any


# ✅ SUBTOPIC_ALIASES for backward compatibility with UI names
SUBTOPIC_ALIASES = {
    # Attracting Love aliases
    "attracting_love": "Attracting Love",
    "attracting-love": "Attracting Love",
    "Attracting Love": "Attracting Love",
    "finding love": "Attracting Love",
    "love life": "Attracting Love",
    "romance": "Attracting Love",
    
    # Break-up aliases (UI sends "Break-up", folder is "breakup")
    "breakup": "Breakup",
    "Breakup": "Breakup",
    "Break-up": "Breakup",       # ← UI sends this!
    "break-up": "Breakup",
    "Break Up": "Breakup",
    "break up": "Breakup",
    "separation": "Breakup",
    
    # Strength and Outcome aliases
    "strength_and_outcome": "Strength And Outcome",
    "strength-and-outcome": "Strength And Outcome",
    "Strength and Outcome": "Strength And Outcome",
    "Strength And Outcome": "Strength And Outcome",
    "relationship strength": "Strength And Outcome",
    "love outcome": "Strength And Outcome",
}


def should_handle(query: str, context: Dict[str, Any] = None) -> bool:
    """
    Determine if this domain should handle the query.
    
    Args:
        query: The user's question
        context: Additional context (optional)
    
    Returns:
        True if this domain should handle the query
    """
    query_lower = query.lower()
    
    # Keywords that trigger this domain
    love_keywords = [
        "love", "romance", "romantic", "dating", "relationship",
        "attract love", "find love", "partner", "soulmate",
        "boyfriend", "girlfriend", "lover", "crush",
        "love life", "romantic life"
    ]
    
    return any(keyword in query_lower for keyword in love_keywords)


def get_subtopics() -> Dict[str, str]:
    """
    Get available subtopics for this domain.
    
    Returns:
        Dictionary mapping subtopic names to descriptions
    """
    return {
        "Attracting Love": "Analysis of love prospects, timing, and remedies for attracting romantic relationships",
        "Breakup": "Analysis of relationship challenges, separation, and recovery",
        "Strength And Outcome": "Analysis of relationship strength and future outcome"
    }
"""
Physical and Mental Health Subtopic

Covers:
- General health analysis (immunity, vitality, frequent illness)
- Disease occurrence and cure timing
- Chronic illness and surgery risk indicators
- Mental health vulnerability (stress, anxiety, depression – advisory only)
- Remedies and supportive lifestyle practices

⚠️ Astrology-based insights are supportive and should not replace
professional medical diagnosis or treatment.
"""

from .evaluator import PhysicalAndMentalHealthEvaluator
from .prompts import PhysicalAndMentalHealthPromptBuilder

__all__ = [
    "PhysicalAndMentalHealthEvaluator",
    "PhysicalAndMentalHealthPromptBuilder"
]

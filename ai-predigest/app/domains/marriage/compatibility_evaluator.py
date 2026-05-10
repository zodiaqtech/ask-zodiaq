"""
Domain-level Compatibility Evaluator for Marriage

This module exposes the MarriageCompatibilityEvaluator at the domain level
so the registry can discover it for two-person analysis.

The actual implementation is in marriage_compatibility/evaluator.py
"""

# Import the evaluator from the subdomain
from app.domains.marriage.marriage_compatibility.evaluator import MarriageCompatibilityEvaluator

# Re-export for registry discovery
__all__ = ["MarriageCompatibilityEvaluator"]

"""
Kundali Matching and Timing Evaluator

Evaluates marriage compatibility and timing using:
- Ashtakoot Milan scores
- Dosha analysis (Manglik, Nadi, Bhakoot, Shadashtak)
- Compatibility across multiple dimensions
- Marriage timing analysis
"""
from typing import Dict, List, Any, Set, Optional

from app.domains.base import (
    BaseTwoPersonEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)


class KundaliMatchingTimingEvaluator(BaseTwoPersonEvaluator):
    """
    Evaluator for Kundali Matching and Timing subtopic.
    
    This is a TWO-PERSON evaluator that requires both partners' data.
    """
    
    domain = "Marriage"
    subtopic = "Kundali Matching Timing"
    
    def __init__(self):
        """Initialize the evaluator"""
        self.seen_points = set()
    
    def reset(self):
        """Reset seen points for new evaluation"""
        self.seen_points = set()
    
    def evaluate(
        self,
        person1_planets: Dict[str, Dict],
        person1_houses: List[Dict],
        person2_planets: Optional[Dict[str, Dict]] = None,
        person2_houses: Optional[List[Dict]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Evaluate kundali matching compatibility.
        
        Note: Most analysis comes from the kundali_milan API data,
        so this evaluator primarily provides structural questions.
        
        This method can be called with 2 args (single person) or 4 args (two person).
        For kundali matching, we need two-person data, so if not provided, we return
        a minimal result.
        """
        self.reset()
        
        result = EvaluationResult()
        
        # If this is being called in single-person mode, just return basic points
        if person2_planets is None or person2_houses is None:
            points = [
                "Kundali matching requires two-person data",
                "Please provide both partners' birth details"
            ]
        else:
            # Basic compatibility points (the real analysis comes from API data)
            points = [
                "Kundali matching analysis based on Ashtakoot system",
                "Dosha compatibility assessment required",
                "Marriage timing depends on both charts' dasha periods",
                "Comprehensive compatibility analysis across multiple dimensions"
            ]
        
        result.extend_points(points)
        
        return result
    
    def evaluate_compatibility(
        self,
        person1_planets: Dict[str, Dict],
        person1_houses: List[Dict],
        person2_planets: Dict[str, Dict],
        person2_houses: List[Dict]
    ) -> Dict[str, Any]:
        """
        Evaluate compatibility for two-person analysis.
        
        Note: The actual kundali matching analysis is done via the
        kundali_milan API. This method provides basic structure.
        """
        return {
            "overall_score": None,
            "relationship_score": None,
            "manglik_status": {"person1": None, "person2": None},
            "detailed_analysis": "Comprehensive kundali matching via Ashtakoot system"
        }
    
    def get_questions(self) -> List[Question]:
        """Get predefined questions for Kundali Matching and Timing"""
        return [
            # Ashtakoot Milan
            Question(
                id="ashtakoot_milan",
                question="Result of full Guna Milan (Ashta Koota), including Manglik, Nadi, Bhakoot doshas and overall compatibility for marriage",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Ashtakoot Milan"
            ),
            
            # Marriage Advice
            Question(
                id="marriage_advice",
                question="Can this marriage be advised, or are remedies required? What are the reasons for any delay and when is the best period (muhurat) to marry?",
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Marriage Advice"
            ),
            
            # Compatibility Analysis
            Question(
                id="compatibility_analysis",
                question="What is the compatibility level (physical, intellectual, emotional, educational, family and financial backgrounds) and the prospects and success of marriage in this case?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Compatibility Analysis"
            )
        ]
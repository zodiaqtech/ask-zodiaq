"""
Base Classes for Domain Evaluators and Prompts

This module provides the abstract base classes that all domain/subtopic
evaluators and prompt builders must inherit from. This ensures a consistent
interface across all domains.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class QueryType(Enum):
    """Types of astrological queries"""
    TIMING = "TIMING"
    NON_TIMING = "NON_TIMING"


class EventPolarity(Enum):
    """Expected event polarity"""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class InterpretationGoal(Enum):
    """Goal of the interpretation"""
    MANIFESTATION = "MANIFESTATION"
    RISK = "RISK"
    STATUS = "STATUS"
    SUPPORT = "SUPPORT"


@dataclass
class QueryMeta:
    """Metadata for a query/question"""
    query_type: QueryType = QueryType.NON_TIMING
    polarity: EventPolarity = EventPolarity.NEUTRAL
    goal: InterpretationGoal = InterpretationGoal.STATUS
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.query_type.value,
            "polarity": self.polarity.value,
            "goal": self.goal.value
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "QueryMeta":
        return cls(
            query_type=QueryType(d.get("type", "NON_TIMING")),
            polarity=EventPolarity(d.get("polarity", "NEUTRAL")),
            goal=InterpretationGoal(d.get("goal", "STATUS"))
        )


@dataclass
class Question:
    """A predefined question for a subtopic"""
    id: str
    question: str
    meta: QueryMeta
    sub_subdomain: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "meta": self.meta.to_dict(),
            "sub_subdomain": self.sub_subdomain
        }


@dataclass
class EvaluationResult:
    """Result from a domain evaluator"""
    points: List[str] = field(default_factory=list)
    promise_state: str = "neutral"
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def technical_points(self) -> List[str]:
        """Alias for points for compatibility"""
        return self.points
    
    def add_point(self, point: str):
        """Add a unique point to results"""
        if point and point not in self.points:
            self.points.append(point)
    
    def extend_points(self, points: List[str]):
        """Extend with unique points"""
        for p in points:
            self.add_point(p)

@dataclass
class TimingWindow:
    start: str
    end: str
    dasha: str
    score: float

    # ✅ REQUIRED ONLY TO AVOID CRASHES
    transit_score: Optional[float] = None
    final_score: Optional[float] = None
    age_at_start: Optional[float] = None
    is_overall_best: bool = False
    is_earliest_favorable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "dasha": self.dasha,
            "score": self.score,
        }



class BaseEvaluator(ABC):
    """
    Abstract base class for all domain/subtopic evaluators.
    
    Each subtopic should implement its own evaluator that inherits from this class.
    The evaluator is responsible for analyzing chart data and producing technical points.
    """
    
    # Class attributes to be overridden by subclasses
    domain: str = ""
    subtopic: str = ""
    
    # KP house significations for this subtopic
    positive_houses: Set[int] = set()
    supportive_houses: Set[int] = set()
    negative_houses: Set[int] = set()
    
    # Key planets for this subtopic
    key_planets: Set[str] = set()
    
    def __init__(self):
        self.seen_points: Set[str] = set()
    
    @abstractmethod
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        **kwargs
    ) -> EvaluationResult:
        """
        Main evaluation method that produces technical astrological points.
        
        Args:
            planets: Normalized planet data dictionary
            houses: Normalized house/cusp data list
            **kwargs: Additional parameters (dasha periods, etc.)
            
        Returns:
            EvaluationResult containing technical points and analysis
        """
        pass
    
    def get_timing_rules(self) -> Dict[str, Any]:
        """Get timing rules for this subtopic"""
        return {
            "positive_houses": self.positive_houses,
            "supportive_houses": self.supportive_houses,
            "negative_houses": self.negative_houses,
            "key_planets": self.key_planets
        }
    
    @abstractmethod
    def get_questions(self) -> List[Question]:
        """Get predefined questions for this subtopic"""
        pass
    
    def _add_unique(self, result: EvaluationResult, msg: str):
        """Add a message only if not already seen"""
        if msg and msg not in self.seen_points:
            result.add_point(msg)
            self.seen_points.add(msg)
    
    def reset(self):
        """Reset seen points for new evaluation"""
        self.seen_points = set()


class BasePromptBuilder(ABC):
    """
    Abstract base class for subtopic-specific prompt builders.
    
    Each subtopic should implement its own prompt builder that creates
    customized prompts for the LLM based on the astrological analysis.
    """
    
    # Class attributes
    domain: str = ""
    subtopic: str = ""
    
    @abstractmethod
    def build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        pass
    
    @abstractmethod
    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """
        Build the analysis prompt for a specific question.
        
        Args:
            question: The user's question
            technical_points: Technical astrological points from evaluator
            meta: Query metadata (type, polarity, goal)
            timing_windows: Optional timing windows for TIMING queries
            planets: Optional planet data
            houses: Optional house data
            language: Output language - "Hindi" or "English" (default)
            
        Returns:
            Complete prompt string for LLM
        """
        pass
    
    def get_language_instruction(self, language: str = "Hindi") -> str:
        """Get the language instruction block for prompts"""
        if language == "Hindi":
            return """
╔════════════════════════════════════════════════════════════════════════╗
║                    भाषा आवश्यकता: हिंदी (HINDI)                         ║
╠════════════════════════════════════════════════════════════════════════╣
║ CRITICAL: Write ALL content in Hindi (Devanagari script)               ║
║                                                                        ║
║ ✓ Section headers MUST remain in English (GENERAL_ANSWER:, etc.)      ║
║ ✓ ALL content text MUST be in Hindi देवनागरी लिपि में                  ║
║                                                                        ║
║ Planet names in Hindi:                                                 ║
║   Sun=सूर्य, Moon=चंद्र, Mars=मंगल, Mercury=बुध                        ║
║   Jupiter=गुरु/बृहस्पति, Venus=शुक्र, Saturn=शनि                       ║
║   Rahu=राहु, Ketu=केतु                                                 ║
║                                                                        ║
║ Technical terms: दशा, गोचर, भाव, राशि, नक्षत्र, कुंडली, योग           ║
╚════════════════════════════════════════════════════════════════════════╝

EXAMPLE OUTPUT FORMAT IN HINDI:

GENERAL_ANSWER:
विवाह के लिए सबसे अनुकूल समय 18 सितंबर 2026 से 10 मार्च 2027 के बीच है। इस अवधि में राहु-शुक्र-शनि की दशा चल रही होगी जो विवाह के लिए शुभ है।

ASTROLOGICAL_ANALYSIS:
सप्तम भाव का विश्लेषण करने पर पता चलता है कि शुक्र ग्रह विवाह का कारक है। वर्तमान में राहु की महादशा चल रही है जो 2, 7, 11 भावों को प्रभावित कर रही है। गुरु का गोचर सप्तम भाव पर शुभ दृष्टि डाल रहा है।

SUMMARY:
2026-2027 में विवाह की प्रबल संभावना है। उपाय करें और सकारात्मक रहें।

REMEDIES_ASTROLOGICAL:
- शुक्रवार को शुक्र मंत्र का जाप करें
- सफेद वस्त्र धारण करें

REMEDIES_GENERAL:
- परिवार से विवाह के विषय में खुलकर बात करें
- सामाजिक कार्यक्रमों में भाग लें
"""
        else:
            return """
========================================
LANGUAGE REQUIREMENT: ENGLISH
========================================
- Write ALL output in clear, professional English
- Use standard astrological terminology
- Keep section headers as specified
========================================
"""
    
    def get_output_format(self) -> str:
        """Get the expected output format instruction"""
        return """
╔════════════════════════════════════════════════════════════════════════╗
║              MANDATORY OUTPUT FORMAT - FOLLOW EXACTLY                   ║
╚════════════════════════════════════════════════════════════════════════╝

You MUST include ALL 5 sections with these EXACT headers:

GENERAL_ANSWER:
(2-4 lines - Brief direct answer to the query. Include dates if timing question.)

ASTROLOGICAL_ANALYSIS:
(3-6 paragraphs - Detailed planetary analysis with houses, aspects, dashas.)

SUMMARY:
(1-2 lines - Key takeaway message.)

REMEDIES_ASTROLOGICAL:
- (2-4 bullet points of planet-based remedies)

REMEDIES_GENERAL:
- (2-3 bullet points of lifestyle recommendations)

⚠️ CRITICAL RULES:
1. ASTROLOGICAL_ANALYSIS must be LONGER than GENERAL_ANSWER
2. ALL 5 sections are REQUIRED - do not skip any
3. Headers must be in English, content in requested language
4. Do NOT merge sections - keep them separate
"""


class BaseTwoPersonEvaluator(ABC):
    """
    Abstract base class for two-person compatibility evaluators.
    """
    
    domain: str = ""
    subtopic: str = ""
    
    @abstractmethod
    def evaluate_compatibility(
        self,
        planets1: Dict[str, Dict],
        houses1: List[Dict],
        planets2: Dict[str, Dict],
        houses2: List[Dict],
        sex1: str,
        sex2: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate compatibility between two charts.
        
        Args:
            planets1: Person 1's planet data
            houses1: Person 1's house data
            planets2: Person 2's planet data
            houses2: Person 2's house data
            sex1: Person 1's sex
            sex2: Person 2's sex
            
        Returns:
            Compatibility analysis dictionary
        """
        pass

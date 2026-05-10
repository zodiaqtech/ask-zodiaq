"""
Social Status and Reputation Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for analyzing social status, reputation, recognition,
and potential risks using Vedic astrology principles.

✔ Simple and straightforward structure
✔ Three sub-subdomains: Recognition, Risk, Social Relationships
✔ Full house lords extraction with dignity and strength
✔ NO KP analysis (Vedic-only domain)
✔ Complete data storage for LLM

Key Houses:
- 10th: Career, public image, reputation, status, authority (PRIMARY)
- 11th: Social circle, gains, recognition, honours, achievements
- 1st: Self, personality, how world perceives you
- 5th: Honours, awards, creativity, intelligence

Supporting Houses:
- 6th: Enemies, scandals, legal issues, opposition
- 7th: Public dealings, partnerships, open enemies
- 8th: Hidden enemies, scandals, secrets, blackmail
- 12th: Hidden enemies, losses, isolation, defamation

Karakas:
- Sun: Authority, fame, recognition, government honours
- Jupiter: Wisdom, respect, good reputation, blessings
- Saturn: Long-term reputation, karma, public service
- Mercury: Communication, public speaking, media
- Rahu: Sudden fame, scandals, unconventional recognition
- Ketu: Spiritual recognition, detachment from fame
"""

from typing import Dict, List, Optional
import logging

from app.domains.base import (
    BaseEvaluator,
    EvaluationResult,
    Question,
    QueryMeta,
    QueryType,
    EventPolarity,
    InterpretationGoal
)

from app.domains.excel_structure_config import get_houses_for_question
from app.core.astro_constants import detect_aspects, normalize_planet_name

try:
    from app.utils.house_lords_analyzer import HouseLordsAnalyzer
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "social_status"


class SocialStatusAndReputationEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Family and Friends → Social Status and Reputation
    
    Handles three sub-subdomains:
    1. Recognition and Honour
    2. Risk to Reputation
    3. Social Relationships
    """

    domain = "Family_Friends"
    subtopic = "Social Status And Reputation"

    # ══════════════════════════════════════════════════════════════
    # MAIN EVALUATION
    # ══════════════════════════════════════════════════════════════
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        **kwargs
    ) -> EvaluationResult:

        self.reset()
        result = EvaluationResult()

        # Select Analysis Data (Vedic preferred)
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        question_text = kwargs.get("question", "").lower()
        sub_subdomain = kwargs.get("sub_subdomain", "")

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data")

        # Set houses for social status analysis
        primary_houses = {10, 11, 1}
        secondary_houses = {5, 6, 7, 8, 12}
        all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 60)
        logger.info("SOCIAL STATUS & REPUTATION EVALUATOR (VEDIC-ONLY v1.0)")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info("=" * 60)

        # Calculate Aspects
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # Extract House Lords
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        # Extract Aspects
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        # Recognition & Honour Analysis
        recognition_analysis = self._analyze_recognition(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Risk to Reputation Analysis
        risk_analysis = self._analyze_reputation_risk(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Social Standing Analysis
        social_analysis = self._analyze_social_standing(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Add Points
        self._add_analysis_points(
            result,
            house_lords_info,
            recognition_analysis,
            risk_analysis,
            social_analysis
        )

        # Store Data for LLM
        self._store_data_for_llm(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            recognition_analysis,
            risk_analysis,
            social_analysis
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # RECOGNITION & HONOUR ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_recognition(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze potential for recognition, honours, and fame."""
        analysis = {
            "recognition_potential": "MODERATE",
            "recognition_score": 50,
            "fame_type": [],
            "favorable_factors": [],
            "challenging_factors": [],
            "recognition_areas": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 10th HOUSE - Public Image, Status (PRIMARY)
        # ═══════════════════════════════════════════════════════════
        h10_info = house_lords_info.get(10, {})
        h10_aspects = house_aspects_info.get(10, {})
        
        if h10_info:
            h10_strength = h10_info.get("lord_strength_score", 50)
            h10_lord = h10_info.get("lord", "")
            h10_lord_house = h10_info.get("lord_in_house")
            
            if h10_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"10th lord {h10_lord} is strong - excellent public standing"
                )
            elif h10_strength < 40:
                score -= 10
                analysis["challenging_factors"].append(
                    f"10th lord {h10_lord} is weak - building reputation takes effort"
                )

            # 10th lord placement
            if h10_lord_house in [1, 4, 5, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"10th lord in house {h10_lord_house} - supports public recognition"
                )
            elif h10_lord_house in [6, 8, 12]:
                score -= 8
                analysis["challenging_factors"].append(
                    f"10th lord in house {h10_lord_house} - obstacles to recognition"
                )

        # Benefics on 10th
        if "Jupiter" in h10_aspects.get("benefic_aspects", []):
            score += 12
            analysis["favorable_factors"].append(
                "Jupiter aspects 10th - blessed reputation and respect"
            )
            analysis["fame_type"].append("Respected leader/teacher")
        if "Venus" in h10_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Venus aspects 10th - fame in arts/entertainment/beauty"
            )
            analysis["fame_type"].append("Arts/Entertainment")

        # Sun on 10th - Fame karaka
        sun_data = planets.get("Sun", {})
        if sun_data and sun_data.get("house") == 10:
            score += 15
            analysis["favorable_factors"].append(
                "Sun in 10th - strong potential for fame and authority"
            )
            analysis["fame_type"].append("Government/Authority")
            analysis["recognition_areas"].append("Leadership positions")

        # ═══════════════════════════════════════════════════════════
        # 11th HOUSE - Gains, Achievements, Honours
        # ═══════════════════════════════════════════════════════════
        h11_info = house_lords_info.get(11, {})
        h11_aspects = house_aspects_info.get(11, {})
        
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            h11_lord = h11_info.get("lord", "")
            
            if h11_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"11th lord {h11_lord} is strong - achievements and honours likely"
                )
                analysis["recognition_areas"].append("Awards and achievements")
            elif h11_strength < 40:
                score -= 8
                analysis["challenging_factors"].append(
                    "11th lord weak - recognition requires sustained effort"

                )

        # Jupiter in 11th
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data and jupiter_data.get("house") == 11:
            score += 12
            analysis["favorable_factors"].append(
                "Jupiter in 11th - recognition for wisdom and good deeds"
            )
            analysis["fame_type"].append("Academic/Spiritual")

        # ═══════════════════════════════════════════════════════════
        # 5th HOUSE - Honours, Awards, Intelligence
        # ═══════════════════════════════════════════════════════════
        h5_info = house_lords_info.get(5, {})
        if h5_info:
            h5_strength = h5_info.get("lord_strength_score", 50)
            if h5_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "5th lord strong - recognition for intelligence/creativity"
                )
                analysis["recognition_areas"].append("Creative achievements")

        # ═══════════════════════════════════════════════════════════
        # 1st HOUSE - Personality, Self-projection
        # ═══════════════════════════════════════════════════════════
        h1_info = house_lords_info.get(1, {})
        h1_aspects = house_aspects_info.get(1, {})
        
        if h1_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            if h1_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "Strong ascendant lord - charismatic and noticeable"
                )

        # ═══════════════════════════════════════════════════════════
        # KEY PLANETS FOR FAME
        # ═══════════════════════════════════════════════════════════
        
        # Sun - Authority, Government
        if sun_data:
            sun_sign = sun_data.get("sign", "")
            if sun_sign in ["Aries", "Leo"]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Sun in {sun_sign} - natural authority and leadership"
                )

        # Rahu - Sudden/Unconventional Fame
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house == 10:
                score += 10
                analysis["favorable_factors"].append(
                    "Rahu in 10th - potential for sudden/mass fame"
                )
                analysis["fame_type"].append("Mass media/Unconventional")
            elif rahu_house == 1:
                score += 5
                analysis["favorable_factors"].append(
                    "Rahu in 1st - unique personality attracts attention"
                )

        # Mercury - Communication Fame
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            if mercury_house in [1, 10, 11]:
                score += 5
                analysis["fame_type"].append("Writing/Speaking/Media")
                analysis["recognition_areas"].append("Communication fields")

        # Determine recognition potential
        score = max(0, min(100, score))
        analysis["recognition_score"] = score

        if score >= 75:
            analysis["recognition_potential"] = "EXCELLENT"
        elif score >= 60:
            analysis["recognition_potential"] = "GOOD"
        elif score >= 45:
            analysis["recognition_potential"] = "MODERATE"
        elif score >= 30:
            analysis["recognition_potential"] = "LIMITED"
        else:
            analysis["recognition_potential"] = "CHALLENGING"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # REPUTATION RISK ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_reputation_risk(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze risks to reputation - scandal, blackmail, defamation."""
        analysis = {
            "risk_level": "LOW",
            "risk_score": 30,
            "risk_factors": [],
            "protection_factors": [],
            "specific_risks": [],
            "protection_advice": []
        }

        risk_score = 30  # Start optimistic

        # ═══════════════════════════════════════════════════════════
        # 6th HOUSE - Enemies, Opposition, Scandals
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            h6_strength = h6_info.get("lord_strength_score", 50)
            
            # 6th lord in reputation houses
            if h6_lord_house == 10:
                risk_score += 20
                analysis["risk_factors"].append(
                    "6th lord in 10th - enemies may target your reputation"
                )
                analysis["specific_risks"].append("Workplace rivals")
            elif h6_lord_house == 1:
                risk_score += 15
                analysis["risk_factors"].append(
                    "6th lord in 1st - open enemies, health affecting image"
                )
            elif h6_lord_house == 11:
                risk_score += 12
                analysis["risk_factors"].append(
                    "6th lord in 11th - conflicts in social circle"
                )

        # ═══════════════════════════════════════════════════════════
        # 8th HOUSE - Hidden Enemies, Scandals, Blackmail, Secrets
        # ═══════════════════════════════════════════════════════════
        h8_info = house_lords_info.get(8, {})
        h8_aspects = house_aspects_info.get(8, {})
        
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            h8_strength = h8_info.get("lord_strength_score", 50)
            
            # 8th lord affecting reputation houses
            if h8_lord_house == 10:
                risk_score += 20
                analysis["risk_factors"].append(
                    "8th lord in 10th - hidden scandals may surface"
                )
                analysis["specific_risks"].append("Hidden secrets exposed")
            elif h8_lord_house == 1:
                risk_score += 15
                analysis["risk_factors"].append(
                    "8th lord in 1st - personal secrets affecting image"
                )
                analysis["specific_risks"].append("Personal life complications")
            
            if h8_strength >= 70:
                risk_score += 8
                analysis["risk_factors"].append(
                    "8th house strong - hidden matters are powerful"
                )

        # ═══════════════════════════════════════════════════════════
        # 12th HOUSE - Hidden Enemies, Losses, Defamation
        # ═══════════════════════════════════════════════════════════
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_lord_house = h12_info.get("lord_in_house")
            
            if h12_lord_house == 10:
                risk_score += 18
                analysis["risk_factors"].append(
                    "12th lord in 10th - hidden enemies, reputation losses"
                )
                analysis["specific_risks"].append("Behind-the-scenes sabotage")
            elif h12_lord_house == 1:
                risk_score += 12
                analysis["risk_factors"].append(
                    "12th lord in 1st - self-undoing may harm reputation"
                )
                analysis["protection_advice"].append("Be careful of self-sabotage")

        # ═══════════════════════════════════════════════════════════
        # MALEFIC PLANETS
        # ═══════════════════════════════════════════════════════════
        h10_aspects = house_aspects_info.get(10, {})
        
        # Saturn afflicting 10th - Delays, falls
        if "Saturn" in h10_aspects.get("malefic_aspects", []):
            risk_score += 10
            analysis["risk_factors"].append(
                "Saturn aspects 10th - reputation may face tests and delays"
            )
            analysis["specific_risks"].append("Slow decline if ethics compromised")

        # Mars afflicting 10th - Conflicts, aggression
        if "Mars" in h10_aspects.get("malefic_aspects", []):
            risk_score += 10
            analysis["risk_factors"].append(
                "Mars aspects 10th - conflicts may harm public image"
            )
            analysis["specific_risks"].append("Public arguments/fights")
            analysis["protection_advice"].append("Control anger in public")

        # Rahu afflicting 10th - Scandals, deception
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house == 10:
                risk_score += 15
                analysis["risk_factors"].append(
                    "Rahu in 10th - risk of scandals or false accusations"
                )
                analysis["specific_risks"].append("Misinformation/rumors")
            if "Rahu" in h10_aspects.get("malefic_aspects", []):
                risk_score += 10
                analysis["risk_factors"].append(
                    "Rahu aspects 10th - unconventional reputation risks"
                )

        # Ketu - Detachment, confusion
        ketu_data = planets.get("Ketu", {})
        if ketu_data and ketu_data.get("house") == 10:
            risk_score += 8
            analysis["risk_factors"].append(
                "Ketu in 10th - confusion about public role, may be misunderstood"
            )

        # ═══════════════════════════════════════════════════════════
        # PROTECTION FACTORS
        # ═══════════════════════════════════════════════════════════
        
        # Jupiter protecting 10th
        if "Jupiter" in h10_aspects.get("benefic_aspects", []):
            risk_score -= 15
            analysis["protection_factors"].append(
                "Jupiter protects 10th - divine grace shields reputation"
            )

        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data and jupiter_data.get("house") == 10:
            risk_score -= 15
            analysis["protection_factors"].append(
                "Jupiter in 10th - reputation naturally protected"
            )

        # Strong 10th lord
        h10_info = house_lords_info.get(10, {})
        if h10_info and h10_info.get("lord_strength_score", 50) >= 70:
            risk_score -= 10
            analysis["protection_factors"].append(
                "Strong 10th lord - resilient reputation"
            )

        # Venus brings harmony
        if "Venus" in h10_aspects.get("benefic_aspects", []):
            risk_score -= 8
            analysis["protection_factors"].append(
                "Venus aspects 10th - charm and likability protect image"
            )

        # Sun strong - authority
        sun_data = planets.get("Sun", {})
        if sun_data:
            sun_sign = sun_data.get("sign", "")
            if sun_sign in ["Aries", "Leo"]:
                risk_score -= 5
                analysis["protection_factors"].append(
                    "Strong Sun - natural authority deflects attacks"
                )

        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 60:
            analysis["risk_level"] = "HIGH"
            analysis["protection_advice"].append("Be extra cautious about public actions")
            analysis["protection_advice"].append("Maintain impeccable ethics")
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
            analysis["protection_advice"].append("Stay vigilant about reputation")
        else:
            analysis["risk_level"] = "LOW"
            analysis["protection_advice"].append("Reputation naturally protected")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # SOCIAL STANDING ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_social_standing(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze social standing and relationships."""
        analysis = {
            "social_standing": "MODERATE",
            "social_score": 50,
            "favorable_factors": [],
            "challenging_factors": [],
            "improvement_tips": [],
            "social_strengths": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 11th HOUSE - Social Circle
        # ═══════════════════════════════════════════════════════════
        h11_info = house_lords_info.get(11, {})
        h11_aspects = house_aspects_info.get(11, {})
        
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            h11_lord = h11_info.get("lord", "")
            h11_lord_house = h11_info.get("lord_in_house")
            
            if h11_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"11th lord {h11_lord} strong - good social connections"
                )
                analysis["social_strengths"].append("Natural networker")
            elif h11_strength < 40:
                score -= 12
                analysis["challenging_factors"].append(
                    f"11th lord {h11_lord} weak - social connections need work"
                )
                analysis["improvement_tips"].append("Actively work on expanding network")

            # 11th lord in difficult houses
            if h11_lord_house in [6, 8, 12]:
                score -= 10
                analysis["challenging_factors"].append(
                    f"11th lord in house {h11_lord_house} - obstacles in social life"
                )
                if h11_lord_house == 12:
                    analysis["improvement_tips"].append("You may prefer solitude - that's okay")
                elif h11_lord_house == 6:
                    analysis["improvement_tips"].append("Conflicts may push people away")
                elif h11_lord_house == 8:
                    analysis["improvement_tips"].append("Trust issues may affect connections")

        # Benefics on 11th
        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 11th - blessed with good social circle"
            )
        if "Venus" in h11_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Venus aspects 11th - charming in social settings"
            )
            analysis["social_strengths"].append("Socially charming")

        # Malefics on 11th
        if "Saturn" in h11_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["challenging_factors"].append(
                "Saturn aspects 11th - few but loyal friends, may feel isolated"
            )
            analysis["improvement_tips"].append("Quality over quantity in friendships")
        if "Rahu" in h11_aspects.get("malefic_aspects", []):
            score -= 8
            analysis["challenging_factors"].append(
                "Rahu aspects 11th - may attract wrong crowd"
            )
            analysis["improvement_tips"].append("Be selective about social circle")

        # ═══════════════════════════════════════════════════════════
        # 1st HOUSE - Personality
        # ═══════════════════════════════════════════════════════════
        h1_info = house_lords_info.get(1, {})
        h1_aspects = house_aspects_info.get(1, {})
        
        if h1_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            if h1_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "Strong personality - naturally attracts people"
                )
                analysis["social_strengths"].append("Strong presence")

        # Venus in 1st - Likeable
        venus_data = planets.get("Venus", {})
        if venus_data and venus_data.get("house") == 1:
            score += 10
            analysis["favorable_factors"].append(
                "Venus in 1st - naturally likeable and attractive"
            )
            analysis["social_strengths"].append("Naturally likeable")

        # ═══════════════════════════════════════════════════════════
        # 7th HOUSE - Public Dealings
        # ═══════════════════════════════════════════════════════════
        h7_info = house_lords_info.get(7, {})
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            if h7_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "7th lord strong - good at public interactions"
                )
            elif h7_strength < 40:
                score -= 5
                analysis["challenging_factors"].append(
                    "7th lord weak - public dealings may be challenging"
                )

        # ═══════════════════════════════════════════════════════════
        # COMMUNICATION - Mercury, 3rd House
        # ═══════════════════════════════════════════════════════════
        mercury_data = planets.get("Mercury", {})
        h3_info = house_lords_info.get(3, {})
        
        if mercury_data:
            mercury_house = mercury_data.get("house")
            mercury_sign = mercury_data.get("sign", "")
            
            if mercury_house in [1, 3, 5, 7, 10, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    "Mercury well-placed - good communication skills"
                )
                analysis["social_strengths"].append("Good communicator")
            
            if mercury_sign in ["Gemini", "Virgo"]:
                score += 5
                analysis["social_strengths"].append("Articulate speaker")

        # ═══════════════════════════════════════════════════════════
        # WHY MIGHT BE IGNORED - Special Factors
        # ═══════════════════════════════════════════════════════════
        
        # Saturn in 1st or 11th - isolation
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [1, 11]:
                analysis["challenging_factors"].append(
                    f"Saturn in house {saturn_house} - may feel socially isolated"
                )
                analysis["improvement_tips"].append("Saturn requires patience - friendships take time")

        # Ketu in 1st or 11th - detachment
        ketu_data = planets.get("Ketu", {})
        if ketu_data:
            ketu_house = ketu_data.get("house")
            if ketu_house in [1, 11]:
                analysis["challenging_factors"].append(
                    f"Ketu in house {ketu_house} - natural detachment from social life"
                )
                analysis["improvement_tips"].append("You may naturally prefer depth over breadth")

        # Moon afflicted - emotional disconnect
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_house = moon_data.get("house")
            if moon_house in [6, 8, 12]:
                analysis["challenging_factors"].append(
                    "Moon in difficult house - emotional sensitivity affects social life"
                )
                analysis["improvement_tips"].append("Work on emotional openness")

        # Determine social standing
        score = max(0, min(100, score))
        analysis["social_score"] = score

        if score >= 70:
            analysis["social_standing"] = "EXCELLENT"
        elif score >= 55:
            analysis["social_standing"] = "GOOD"
        elif score >= 40:
            analysis["social_standing"] = "MODERATE"
        elif score >= 25:
            analysis["social_standing"] = "NEEDS_IMPROVEMENT"
        else:
            analysis["social_standing"] = "CHALLENGING"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    @staticmethod
    def extract_planet_name(p):
        if isinstance(p, dict):
            return p.get("name")
        if isinstance(p, str):
            return p
        return None

    def _extract_house_lords(
        self,
        houses: list,
        planets: dict,
        relevant_houses: set,
        primary_houses: set
    ) -> dict:
        """Extract house lord information."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue

            lord_name = h.get("sign_lord") or h.get("rashi_lord") or h.get("lord") or ""

            if not lord_name:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                if sign:
                    sign_lords = {
                        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
                        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
                        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
                        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                    }
                    lord_name = sign_lords.get(sign, "")

            normalized_lord = normalize_planet_name(lord_name)
            if not normalized_lord:
                continue

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                continue

            lord_house = lord_data.get("house")
            lord_sign = lord_data.get("sign", "")
            lord_degree = lord_data.get("full_degree") or lord_data.get("degree") or 0
            lord_is_combust = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)

            lord_dignity = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity = analyzer._get_dignity(normalized_lord, lord_sign, lord_degree)
                    lord_dignity = dignity.value
                    lord_strength_score = self._calculate_lord_strength(normalized_lord, lord_data, dignity)
                except Exception:
                    pass

            priority = "primary" if house_num in primary_houses else "secondary"

            planets_in_house = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]

            house_lords_info[house_num] = {
                "lord": normalized_lord,
                "lord_in_house": lord_house,
                "lord_in_sign": lord_sign,
                "lord_is_combust": lord_is_combust,
                "lord_is_retrograde": lord_is_retrograde,
                "lord_dignity": lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority": priority,
                "planets_in_house": planets_in_house
            }

        return house_lords_info

    # ══════════════════════════════════════════════════════════════
    # ASPECTS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    def _extract_aspects_on_houses(
        self,
        houses: list,
        planets: dict,
        aspects_data: dict,
        relevant_houses: set
    ) -> dict:
        """Extract aspects on relevant houses."""
        house_aspects = {}

        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        for house_num in relevant_houses:
            house_aspects[house_num] = {
                "benefic_aspects": [],
                "malefic_aspects": [],
                "neutral_aspects": []
            }

            for planet_name, planet_data in planets.items():
                if aspects_data and planet_name in aspects_data:
                    aspected_houses = aspects_data[planet_name].get("aspects_houses", [])
                else:
                    aspected_houses = planet_data.get("aspects_houses", [])

                if house_num in aspected_houses:
                    if planet_name in benefics:
                        house_aspects[house_num]["benefic_aspects"].append(planet_name)
                    elif planet_name in malefics:
                        house_aspects[house_num]["malefic_aspects"].append(planet_name)
                    else:
                        house_aspects[house_num]["neutral_aspects"].append(planet_name)

        return house_aspects

    # ══════════════════════════════════════════════════════════════
    # STRENGTH CALCULATION
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(self, planet_name: str, planet_data: dict, dignity=None) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, 'value') else str(dignity).upper()
            dignity_scores = {
                "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
                "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0
            }
            score = dignity_scores.get(dignity_str, 50)

        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # ADD ANALYSIS POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        recognition_analysis: dict,
        risk_analysis: dict,
        social_analysis: dict
    ):
        """Add analysis points to result."""
        
        # Recognition
        result.add_point(
            f"🏆 Recognition Potential: {recognition_analysis.get('recognition_potential')} "
            f"({recognition_analysis.get('recognition_score')}/100)"
        )

        # Fame types
        fame_types = recognition_analysis.get("fame_type", [])
        if fame_types:
            result.add_point(f"⭐ Fame Areas: {', '.join(fame_types[:3])}")

        # Risk
        result.add_point(
            f"⚠️ Reputation Risk: {risk_analysis.get('risk_level')} "
            f"({risk_analysis.get('risk_score')}/100)"
        )

        # Social Standing
        result.add_point(
            f"👥 Social Standing: {social_analysis.get('social_standing')} "
            f"({social_analysis.get('social_score')}/100)"
        )

        # Key factors
        for factor in recognition_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in risk_analysis.get("risk_factors", [])[:2]:
            result.add_point(f"🚨 {factor}")
        for factor in risk_analysis.get("protection_factors", [])[:1]:
            result.add_point(f"🛡️ {factor}")

        # Social strengths
        strengths = social_analysis.get("social_strengths", [])
        if strengths:
            result.add_point(f"💪 Strengths: {', '.join(strengths[:3])}")

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        recognition_analysis: dict,
        risk_analysis: dict,
        social_analysis: dict
    ):
        """Store data for LLM consumption."""

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses)
            },
            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,
            f"{DOMAIN_PREFIX}_recognition_analysis": recognition_analysis,
            f"{DOMAIN_PREFIX}_risk_analysis": risk_analysis,
            f"{DOMAIN_PREFIX}_social_analysis": social_analysis,
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "recognition_potential": recognition_analysis.get("recognition_potential", "MODERATE"),
                "recognition_score": recognition_analysis.get("recognition_score", 50),
                "fame_type": recognition_analysis.get("fame_type", []),
                "risk_level": risk_analysis.get("risk_level", "LOW"),
                "risk_score": risk_analysis.get("risk_score", 30),
                "specific_risks": risk_analysis.get("specific_risks", []),
                "social_standing": social_analysis.get("social_standing", "MODERATE"),
                "social_score": social_analysis.get("social_score", 50),
                "social_strengths": social_analysis.get("social_strengths", []),
            },
        })

        logger.info(
            f"📦 STORED | recognition={recognition_analysis.get('recognition_potential')} | "
            f"risk={risk_analysis.get('risk_level')} | "
            f"social={social_analysis.get('social_standing')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="RECOGNITION_HONOUR",
                question=(
                    "Will I receive recognition or honours and what does astrology "
                    "indicate about my reputation and social standing?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Recognition and Honour"
            ),
            Question(
                id="REPUTATION_RISK",
                question=(
                    "Are there risks to my reputation due to misinformation, scandal, "
                    "blackmail, or personal problems and how can I protect myself?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Risk to Reputation"
            ),
            Question(
                id="SOCIAL_RELATIONSHIPS",
                question=(
                    "Why might my social circle be ignoring me and how can I improve "
                    "my relationships and standing?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Social Relationships"
            )
        ]
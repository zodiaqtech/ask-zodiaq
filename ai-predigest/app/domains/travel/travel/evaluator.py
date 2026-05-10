"""
Travel Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for travel, pilgrimage, and journey-related queries
using traditional Vedic astrology principles.

✔ COMPLETE structural parity with Finance/Parenting/Lost evaluators
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Timing windows for travel questions
✔ Pilgrimage-specific analysis
✔ Travel risks assessment
✔ Complete data storage for LLM

Key Houses for Travel:
- 3rd: Short journeys, courage, communication during travel
- 4th: Home (leaving home), vehicles, comfort during travel
- 7th: Long journeys, foreign travel, destinations
- 9th: Pilgrimage, long-distance travel, fortune abroad, dharma
- 12th: Foreign lands, expenses during travel, spiritual journeys

Karakas:
- Moon: Mind, emotions, comfort during travel
- Mercury: Communication, planning, documentation
- Jupiter: Pilgrimage, blessings, protection during travel
- Venus: Comfort, luxury travel, enjoyment
- Saturn: Delays, obstacles, long journeys
- Rahu: Foreign travel, unusual destinations
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
from datetime import datetime

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

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
    logging.info("House lords analyzer available for Travel domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "travel"


class TravelEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Travel → Travel
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Travel success likelihood
    - Pilgrimage favorability
    - Travel risks assessment
    - Timing windows extraction
    - NO KP analysis (purely Vedic)
    
    Traditional Vedic Rules for Travel:
    - 9th house strong = Pilgrimage and long travel blessed
    - 3rd house strong = Short journeys successful
    - 7th house strong = Foreign/long distance travel supported
    - 12th house = Expenses, foreign lands
    - Jupiter strong = Divine protection during travel
    - Moon strong = Mental peace and comfort
    - Malefics in 3rd/9th = Travel obstacles
    """

    domain = "Travel"
    subtopic = "Travel"

    # ══════════════════════════════════════════════════════════════
    # AUSPICIOUS DAYS FOR TRAVEL (Vedic)
    # ══════════════════════════════════════════════════════════════
    AUSPICIOUS_TRAVEL_DAYS = {
        "Sunday": {"direction": "East", "deity": "Sun", "suitable_for": "Government work, pilgrimage to Sun temples"},
        "Monday": {"direction": "North-West", "deity": "Moon", "suitable_for": "Short trips, water-related places"},
        "Tuesday": {"direction": "South", "deity": "Mars", "suitable_for": "Adventure, challenging journeys"},
        "Wednesday": {"direction": "North", "deity": "Mercury", "suitable_for": "Business trips, education-related"},
        "Thursday": {"direction": "North-East", "deity": "Jupiter", "suitable_for": "Pilgrimage, spiritual journeys"},
        "Friday": {"direction": "East", "deity": "Venus", "suitable_for": "Leisure, pleasure trips, honeymoon"},
        "Saturday": {"direction": "West", "deity": "Saturn", "suitable_for": "Long journeys, foreign travel"}
    }

    DIRECTION_BY_SIGN = {
        "Aries": "East", "Leo": "East", "Sagittarius": "East",
        "Taurus": "South", "Virgo": "South", "Capricorn": "South",
        "Gemini": "West", "Libra": "West", "Aquarius": "West",
        "Cancer": "North", "Scorpio": "North", "Pisces": "North"
    }

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

        # ═══════════════════════════════════════════════════════════
        # STEP 0: Normalize Meta
        # ═══════════════════════════════════════════════════════════
        meta = kwargs.get("meta")

        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        meta_query_type = meta.query_type if isinstance(meta, QueryMeta) else None
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Select Analysis Data (Vedic preferred)
        # ═══════════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════════
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = set(house_config["primary"])
            secondary_houses = set(house_config["secondary"])
            all_relevant_houses = primary_houses | secondary_houses
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback for Travel")
            # Default houses for Travel domain
            # 3rd = short journeys, 7th = long journeys, 9th = pilgrimage
            # 4th = home/vehicles, 12th = foreign/expenses
            primary_houses = {3, 7, 9}
            secondary_houses = {4, 12, 1}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("TRAVEL EVALUATOR (VEDIC-ONLY v1.0)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Calculate Aspects
        # ═══════════════════════════════════════════════════════════
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Extract House Lords Data
        # ═══════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Extract Timing Windows
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})
        timing_windows_list = []
        
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")

            # Fallback keys
            if not timing_windows_list and "Pilgrimage Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Pilgrimage Timing"]
            if not timing_windows_list and "Travel Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Travel Timing"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []

        timing_windows_data = {}
        if meta_query_type == QueryType.TIMING and timing_windows_list:
            timing_windows_data = self._extract_timing_windows(timing_windows_list) or {}
            logger.info("✅ TIMING ENABLED")
        else:
            timing_windows_data = {"has_timing": False}

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Pilgrimage Analysis
        # ═══════════════════════════════════════════════════════════
        pilgrimage_analysis = self._analyze_pilgrimage_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Pilgrimage prospects: {pilgrimage_analysis.get('favorability', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: General Travel Analysis
        # ═══════════════════════════════════════════════════════════
        travel_analysis = self._analyze_travel_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Travel success: {travel_analysis.get('success_likelihood', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Travel Risks Analysis
        # ═══════════════════════════════════════════════════════════
        risks_analysis = self._analyze_travel_risks(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Risk level: {risks_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Auspicious Timing Hints
        # ═══════════════════════════════════════════════════════════
        timing_hints = self._get_auspicious_timing_hints(
            analysis_planets,
            house_lords_info,
            sub_subdomain
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 12: Add Travel-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_travel_points(result, pilgrimage_analysis, travel_analysis, risks_analysis)

        # ═══════════════════════════════════════════════════════════
        # STEP 13: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            pilgrimage_analysis,
            travel_analysis,
            risks_analysis,
            timing_hints,
            kwargs
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # PILGRIMAGE ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_pilgrimage_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze pilgrimage prospects using Vedic principles.
        
        Key indicators:
        - 9th house (dharma, pilgrimage, long travel)
        - Jupiter (karaka for pilgrimage and blessings)
        - 12th house (spiritual journeys, foreign temples)
        - 5th house (past life merit, devotion)
        """
        analysis = {
            "favorability": "MODERATE",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "recommended_places": [],
            "best_days": []
        }

        score = 50

        # Check 9th house (primary for pilgrimage)
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            h9_lord = h9_info.get("lord", "")
            h9_sign = h9_info.get("lord_in_sign", "")
            
            if h9_strength >= 70:
                score += 20
                analysis["favorable_factors"].append(
                    f"9th lord {h9_lord} is strong ({h9_strength}/100) - pilgrimage highly blessed"
                )
            elif h9_strength >= 50:
                score += 10
                analysis["favorable_factors"].append(
                    f"9th lord {h9_lord} is moderately placed - pilgrimage supported"
                )
            elif h9_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"9th lord {h9_lord} is weak ({h9_strength}/100) - extra preparation needed"
                )

            # Direction recommendation based on 9th lord's sign
            if h9_sign in self.DIRECTION_BY_SIGN:
                direction = self.DIRECTION_BY_SIGN[h9_sign]
                analysis["recommended_places"].append(
                    f"Holy places in {direction} direction are favorable"
                )

        # Check Jupiter (karaka for pilgrimage)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            jupiter_retro = jupiter_data.get("is_retro", False)
            
            if jupiter_house in [1, 5, 9, 11]:
                score += 15
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine blessings for pilgrimage"
                )
                analysis["best_days"].append("Thursday is highly auspicious")
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - some obstacles possible"
                )
            
            if jupiter_retro:
                analysis["favorable_factors"].append(
                    "Retrograde Jupiter favors revisiting holy places"
                )

        # Check benefic aspects on 9th house
        h9_aspects = house_aspects_info.get(9, {})
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - pilgrimage will bring spiritual growth"
            )
        if "Venus" in h9_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Venus aspects 9th house - comfortable and pleasant journey"
            )

        # Check malefic aspects
        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["unfavorable_factors"].append(
                "Saturn aspects 9th house - delays possible, plan well in advance"
            )
        if "Rahu" in h9_aspects.get("malefic_aspects", []):
            analysis["recommended_places"].append(
                "Foreign or less-known pilgrimage sites may be beneficial"
            )

        # Check Moon for mental readiness
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_house = moon_data.get("house")
            if moon_house in [4, 9, 12]:
                score += 5
                analysis["favorable_factors"].append(
                    "Moon placement supports spiritual mindset for pilgrimage"
                )
            analysis["best_days"].append("Monday is favorable for starting journeys")

        # Determine favorability
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 75:
            analysis["favorability"] = "HIGHLY_FAVORABLE"
        elif score >= 60:
            analysis["favorability"] = "FAVORABLE"
        elif score >= 45:
            analysis["favorability"] = "MODERATE"
        elif score >= 30:
            analysis["favorability"] = "CHALLENGING"
        else:
            analysis["favorability"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # GENERAL TRAVEL ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_travel_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze general travel prospects.
        
        Key indicators:
        - 3rd house (short journeys)
        - 7th house (long journeys, foreign travel)
        - 9th house (long distance)
        - 12th house (foreign lands)
        """
        analysis = {
            "success_likelihood": "MODERATE",
            "score": 50,
            "short_travel": {"favorable": False, "notes": []},
            "long_travel": {"favorable": False, "notes": []},
            "foreign_travel": {"favorable": False, "notes": []},
            "favorable_factors": [],
            "unfavorable_factors": []
        }

        score = 50

        # Check 3rd house (short journeys)
        h3_info = house_lords_info.get(3, {})
        if h3_info:
            h3_strength = h3_info.get("lord_strength_score", 50)
            if h3_strength >= 60:
                score += 10
                analysis["short_travel"]["favorable"] = True
                analysis["short_travel"]["notes"].append(
                    f"3rd lord strong - short trips and local travel successful"
                )
                analysis["favorable_factors"].append(
                    f"3rd lord {h3_info.get('lord')} supports short journeys"
                )

        # Check 7th house (long journeys)
        h7_info = house_lords_info.get(7, {})
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            if h7_strength >= 60:
                score += 10
                analysis["long_travel"]["favorable"] = True
                analysis["long_travel"]["notes"].append(
                    f"7th lord strong - long distance travel supported"
                )
                analysis["favorable_factors"].append(
                    f"7th lord {h7_info.get('lord')} supports long journeys"
                )
            elif h7_strength < 40:
                analysis["unfavorable_factors"].append(
                    f"7th lord weak - long travel may face obstacles"
                )

        # Check 12th house (foreign travel)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            h12_lord_house = h12_info.get("lord_in_house")
            
            # 12th lord in 9th or 7th = foreign travel
            if h12_lord_house in [7, 9]:
                score += 10
                analysis["foreign_travel"]["favorable"] = True
                analysis["foreign_travel"]["notes"].append(
                    "Strong indication for foreign travel"
                )
            
            if h12_strength >= 60:
                analysis["foreign_travel"]["notes"].append(
                    "Expenses during travel will be manageable"
                )

        # Check Rahu (foreign travel karaka)
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [3, 7, 9, 12]:
                score += 5
                analysis["foreign_travel"]["favorable"] = True
                analysis["foreign_travel"]["notes"].append(
                    f"Rahu in house {rahu_house} - foreign or unusual destinations indicated"
                )

        # Check Venus (comfort during travel)
        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_house = venus_data.get("house")
            if venus_house in [3, 7, 9]:
                score += 5
                analysis["favorable_factors"].append(
                    "Venus placement ensures comfortable travel"
                )

        # Check Mercury (planning and communication)
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            mercury_retro = mercury_data.get("is_retro", False)
            
            if mercury_retro:
                analysis["unfavorable_factors"].append(
                    "Mercury retrograde - double-check bookings and documents"
                )
            elif mercury_house in [3, 9, 11]:
                analysis["favorable_factors"].append(
                    "Mercury well-placed - travel planning will go smoothly"
                )

        # Determine success likelihood
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 70:
            analysis["success_likelihood"] = "HIGH"
        elif score >= 55:
            analysis["success_likelihood"] = "MODERATE_HIGH"
        elif score >= 40:
            analysis["success_likelihood"] = "MODERATE"
        else:
            analysis["success_likelihood"] = "LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # TRAVEL RISKS ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_travel_risks(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze travel risks and obstacles.
        
        Risk indicators:
        - Malefics in 3rd, 7th, 9th houses
        - 8th house afflictions (accidents, sudden events)
        - Mars afflictions (accidents, conflicts)
        - Saturn aspects (delays, obstacles)
        - Rahu/Ketu (confusion, unexpected events)
        """
        analysis = {
            "risk_level": "LOW",
            "risk_score": 20,
            "risks": [],
            "precautions": [],
            "protective_factors": []
        }

        risk_score = 20  # Start low

        # Check Mars (accidents, conflicts)
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [3, 7, 8, 12]:
                risk_score += 15
                analysis["risks"].append(
                    f"Mars in house {mars_house} - be cautious of accidents and conflicts"
                )
                analysis["precautions"].append(
                    "Avoid risky activities and heated arguments during travel"
                )

        # Check Saturn (delays, obstacles)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [3, 7, 9]:
                risk_score += 10
                analysis["risks"].append(
                    f"Saturn in house {saturn_house} - delays and obstacles possible"
                )
                analysis["precautions"].append(
                    "Plan extra time, book in advance, carry patience"
                )

        # Check 8th house (sudden events)
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            if h8_lord_house in [3, 7, 9]:
                risk_score += 15
                analysis["risks"].append(
                    "8th lord connected to travel houses - unexpected events possible"
                )
                analysis["precautions"].append(
                    "Get travel insurance, keep emergency contacts ready"
                )

        # Check Rahu/Ketu
        rahu_data = planets.get("Rahu", {})
        ketu_data = planets.get("Ketu", {})
        
        if rahu_data and rahu_data.get("house") in [3, 7, 9]:
            risk_score += 10
            analysis["risks"].append(
                "Rahu influence - confusion or unexpected changes in plans"
            )
            analysis["precautions"].append(
                "Verify all bookings, be flexible with plans"
            )
        
        if ketu_data and ketu_data.get("house") in [3, 7, 9]:
            risk_score += 5
            analysis["risks"].append(
                "Ketu influence - may feel detached or lost"
            )
            analysis["precautions"].append(
                "Travel with companions if possible"
            )

        # Check malefic aspects on travel houses
        for house_num in [3, 7, 9]:
            aspects = house_aspects_info.get(house_num, {})
            malefics = aspects.get("malefic_aspects", [])
            
            if "Mars" in malefics:
                risk_score += 5
                analysis["precautions"].append(
                    f"Mars aspects house {house_num} - extra caution with vehicles"
                )
            if "Saturn" in malefics:
                risk_score += 5
                analysis["precautions"].append(
                    f"Saturn aspects house {house_num} - expect some delays"
                )

        # Check protective factors
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 9, 11]:
                risk_score -= 15
                analysis["protective_factors"].append(
                    "Jupiter's blessing provides divine protection during travel"
                )

        # Check benefic aspects
        for house_num in [3, 7, 9]:
            aspects = house_aspects_info.get(house_num, {})
            benefics = aspects.get("benefic_aspects", [])
            
            if "Jupiter" in benefics:
                risk_score -= 10
                analysis["protective_factors"].append(
                    f"Jupiter protects house {house_num} - travels will be safe"
                )

        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 60:
            analysis["risk_level"] = "HIGH"
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
        elif risk_score >= 20:
            analysis["risk_level"] = "LOW"
        else:
            analysis["risk_level"] = "VERY_LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # AUSPICIOUS TIMING HINTS
    # ══════════════════════════════════════════════════════════════
    def _get_auspicious_timing_hints(
        self,
        planets: Dict,
        house_lords_info: Dict,
        sub_subdomain: str
    ) -> Dict:
        """
        Get auspicious timing hints based on Vedic principles.
        """
        hints = {
            "best_days": [],
            "avoid_days": [],
            "best_nakshatras": [],
            "general_hints": []
        }

        # Best days based on purpose
        if "Pilgrimage" in sub_subdomain:
            hints["best_days"].extend([
                "Thursday (Jupiter's day) - most auspicious for pilgrimage",
                "Monday (Moon's day) - good for water-related holy places"
            ])
            hints["best_nakshatras"].extend([
                "Pushya, Ashwini, Mrigashira - excellent for starting pilgrimage",
                "Revati, Hasta, Swati - smooth and safe journeys"
            ])
        else:
            hints["best_days"].extend([
                "Wednesday (Mercury's day) - good for business travel",
                "Friday (Venus's day) - good for leisure travel"
            ])

        # Days to avoid
        hints["avoid_days"].extend([
            "Avoid starting travel on Amavasya (new moon)",
            "Avoid travel on Rahu Kaal timings"
        ])

        # Check 9th lord for specific hints
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_lord = h9_info.get("lord", "")
            if h9_lord == "Jupiter":
                hints["general_hints"].append(
                    "Jupiter rules 9th house - Thursday starts are especially favorable"
                )
            elif h9_lord == "Venus":
                hints["general_hints"].append(
                    "Venus rules 9th house - Friday starts bring comfort and pleasure"
                )
            elif h9_lord == "Saturn":
                hints["general_hints"].append(
                    "Saturn rules 9th house - Saturday starts for long journeys"
                )

        return hints

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """Extract BEST and NEAREST timing windows for LLM."""
        if not timing_windows:
            return {}

        try:
            def get_attr(obj, key, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            def window_to_dict(w):
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w

                return {
                    'start': get_attr(w, 'start'),
                    'end': get_attr(w, 'end'),
                    'dasha': get_attr(w, 'dasha'),
                    'score': get_attr(w, 'score'),
                    'transit_score': get_attr(w, 'transit_score'),
                    'final_score': get_attr(w, 'final_score'),
                    'age_at_start': get_attr(w, 'age_at_start'),
                    'is_overall_best': get_attr(w, 'is_overall_best', False),
                    'is_earliest_favorable': get_attr(w, 'is_earliest_favorable', False),
                }

            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            favorable_windows = [
                w for w in timing_windows
                if (get_attr(w, 'final_score', 0) or 0) >= 50
            ]

            if favorable_windows:
                sorted_by_date = sorted(
                    favorable_windows,
                    key=lambda w: datetime.strptime(
                        get_attr(w, 'start', '9999-12-31') or '9999-12-31',
                        '%Y-%m-%d'
                    )
                )
                nearest_window = window_to_dict(sorted_by_date[0]) if sorted_by_date else None
            else:
                nearest_window = best_window

            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]

            return {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            return {}

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
        """Extract house lord information for relevant houses only."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")

            if house_num not in relevant_houses:
                continue

            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
                h.get("lord") or
                ""
            )

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

            lord_degree = (
                lord_data.get("full_degree") or
                lord_data.get("global_degree") or
                lord_data.get("degree") or
                0
            )

            lord_is_combust = (
                lord_data.get("is_combusted", False) or
                lord_data.get("is_combust", False)
            )

            lord_is_retrograde = (
                lord_data.get("is_retro", False) or
                lord_data.get("is_retrograde", False)
            )

            lord_dignity = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)

                    dignity = None
                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(normalized_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(normalized_lord)

                    if dignity:
                        if hasattr(dignity, 'value'):
                            lord_dignity = dignity.value
                        else:
                            lord_dignity = str(dignity)

                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity)

                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")

            priority = "primary" if house_num in primary_houses else "secondary"

            planets_in_house = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]

            house_sign = (
                h.get("sign") or
                h.get("start_rasi") or
                h.get("rasi") or
                ""
            )

            house_lords_info[house_num] = {
                "lord": normalized_lord,
                "lord_in_house": lord_house,
                "lord_in_sign": lord_sign,
                "lord_degree": lord_degree,
                "lord_is_combust": lord_is_combust,
                "lord_is_retrograde": lord_is_retrograde,
                "lord_dignity": lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority": priority,
                "planets_in_house": planets_in_house,
                "house_sign": house_sign
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
        """Extract aspects on relevant houses only."""
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
    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity=None
    ) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, 'value') else str(dignity).upper()

            dignity_scores = {
                "EXALTED": 100,
                "OWN_SIGN": 80,
                "OWN SIGN": 80,
                "FRIENDLY": 60,
                "NEUTRAL": 40,
                "ENEMY": 20,
                "DEBILITATED": 0
            }
            score = dignity_scores.get(dignity_str, 50)

        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30

        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            if planet_name in {"Jupiter", "Venus", "Mercury"}:
                score -= 10
            elif planet_name in {"Saturn", "Mars"}:
                score += 10

        degree = (
            planet_data.get("full_degree") or
            planet_data.get("global_degree") or
            planet_data.get("degree") or
            15
        )
        if degree < 5 or degree > 25:
            score -= 10

        return max(0, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for travel context."""
        meanings = {
            1: "Self/Health during travel",
            3: "Short Journeys/Courage",
            4: "Home/Vehicles/Comfort",
            7: "Long Journeys/Foreign",
            9: "Pilgrimage/Fortune/Dharma",
            12: "Foreign Lands/Expenses"
        }
        return meanings.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_house_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set
    ):
        """Add analysis points based on house lords and aspects."""
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue

            info = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            lord = info["lord"]
            dignity = info["lord_dignity"]
            strength = info["lord_strength_score"]

            marker = "⭐"
            point_parts = [
                f"{marker} House {house_num} ({self._get_house_meaning(house_num)}):",
                f"Lord {lord} is {dignity}",
                f"(Strength: {strength}/100)"
            ]

            conditions = []
            if info["lord_is_combust"]:
                conditions.append("COMBUST")
            if info["lord_is_retrograde"]:
                conditions.append("RETROGRADE")

            if conditions:
                point_parts.append(f"[{', '.join(conditions)}]")

            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])

            if benefic:
                point_parts.append(f"- Benefic: {', '.join(benefic)}")
            if malefic:
                point_parts.append(f"- Malefic: {', '.join(malefic)}")

            result.add_point(" ".join(point_parts))

    # ══════════════════════════════════════════════════════════════
    # ADD TRAVEL POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_travel_points(
        self,
        result: EvaluationResult,
        pilgrimage_analysis: Dict,
        travel_analysis: Dict,
        risks_analysis: Dict
    ):
        """Add travel-specific points to result."""
        
        # Pilgrimage
        favorability = pilgrimage_analysis.get("favorability", "MODERATE")
        p_score = pilgrimage_analysis.get("score", 50)
        result.add_point(
            f"🙏 Pilgrimage Favorability: {favorability} (Score: {p_score}/100)"
        )

        # Travel success
        success = travel_analysis.get("success_likelihood", "MODERATE")
        t_score = travel_analysis.get("score", 50)
        result.add_point(
            f"✈️ Travel Success Likelihood: {success} (Score: {t_score}/100)"
        )

        # Risk level
        risk_level = risks_analysis.get("risk_level", "LOW")
        r_score = risks_analysis.get("risk_score", 20)
        result.add_point(
            f"⚠️ Travel Risk Level: {risk_level} (Score: {r_score}/100)"
        )

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict,
        pilgrimage_analysis: dict,
        travel_analysis: dict,
        risks_analysis: dict,
        timing_hints: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },

            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            f"{DOMAIN_PREFIX}_pilgrimage_analysis": pilgrimage_analysis,
            f"{DOMAIN_PREFIX}_travel_analysis": travel_analysis,
            f"{DOMAIN_PREFIX}_risks_analysis": risks_analysis,
            f"{DOMAIN_PREFIX}_timing_hints": timing_hints,

            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "pilgrimage_favorability": pilgrimage_analysis.get("favorability", "MODERATE"),
                "pilgrimage_score": pilgrimage_analysis.get("score", 50),
                "travel_success": travel_analysis.get("success_likelihood", "MODERATE"),
                "travel_score": travel_analysis.get("score", 50),
                "risk_level": risks_analysis.get("risk_level", "LOW"),
                "risk_score": risks_analysis.get("risk_score", 20),
            },
        })

        # Store timing windows
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}

        logger.info(
            f"📦 STORED | pilgrimage={pilgrimage_analysis.get('favorability')} | "
            f"travel={travel_analysis.get('success_likelihood')} | "
            f"risk={risks_analysis.get('risk_level')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="TRAVEL_1",
                question="Will I be able to visit holy places for pilgrimage and when is the most auspicious muhurat for undertaking such journeys?",
                meta=QueryMeta(QueryType.TIMING, EventPolarity.POSITIVE, InterpretationGoal.MANIFESTATION),
                sub_subdomain="Pilgrimage Timing"
            ),
            Question(
                id="TRAVEL_2",
                question="When is the most favorable time for other types of travel and will my travels be successful?",
                meta=QueryMeta(QueryType.TIMING, EventPolarity.POSITIVE, InterpretationGoal.MANIFESTATION),
                sub_subdomain="Travel Timing"
            ),
            Question(
                id="TRAVEL_3",
                question="Are there any risks or obstacles I might face during my pilgrimage or travels and how can I overcome them?",
                meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEGATIVE, InterpretationGoal.RISK),
                sub_subdomain="Travel Risks"
            )
        ]
"""
Marriage Compatibility Evaluator - Enhanced Version v4.0

FIXES & ENHANCEMENTS:
✅ _extract_timing_windows now handles TimingWindow objects (not just dicts)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP analysis preserved and passed to LLM

Features:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data) for BOTH persons
✅ Vedic parser aspects for BOTH charts
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ Two-person compatibility analysis
✅ Moon, Venus, Sun-Moon, Mars, Jupiter compatibility
✅ Manglik status matching
"""
from typing import Dict, List, Any, Set, Optional
import logging

from app.domains.base import (
    BaseEvaluator, BaseTwoPersonEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p, _in_houses,
    _lord_of, detect_aspects, RASI_LORDS
)

from app.domains.excel_structure_config import get_houses_for_question

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer, 
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# DIGNITY CALCULATION - FALLBACK TABLES
# ═══════════════════════════════════════════════════════════════════════════════

PLANET_RULERSHIP = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": [],
    "Ketu": []
}

PLANET_EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Taurus",
    "Ketu": "Scorpio"
}

PLANET_DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus"
}

FRIENDSHIP_TABLE = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
    "Moon": {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
    "Rahu": {"friends": ["Venus", "Saturn"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Mercury", "Jupiter"]},
    "Ketu": {"friends": ["Mars", "Venus", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mercury", "Jupiter"]}
}


def calculate_dignity_fallback(planet_name: str, planet_sign: str) -> str:
    """Calculate planet dignity using fallback tables."""
    if not planet_name or not planet_sign:
        return "Unknown"
    
    planet_name = normalize_planet_name(planet_name) or planet_name
    planet_sign = planet_sign.title() if planet_sign else ""
    
    if PLANET_EXALTATION.get(planet_name) == planet_sign:
        return "Exalted"
    
    if PLANET_DEBILITATION.get(planet_name) == planet_sign:
        return "Debilitated"
    
    if planet_sign in PLANET_RULERSHIP.get(planet_name, []):
        return "Own Sign"
    
    sign_lord = None
    for lord, signs in PLANET_RULERSHIP.items():
        if planet_sign in signs:
            sign_lord = lord
            break
    
    if not sign_lord or sign_lord == planet_name:
        return "Neutral"
    
    friendship = FRIENDSHIP_TABLE.get(planet_name, {})
    if sign_lord in friendship.get("friends", []):
        return "Friendly"
    elif sign_lord in friendship.get("enemies", []):
        return "Enemy"
    else:
        return "Neutral"


# Element-based compatibility
COMPATIBLE_ELEMENTS = {
    ("Aries", "Leo"), ("Aries", "Sagittarius"), ("Leo", "Sagittarius"),
    ("Taurus", "Virgo"), ("Taurus", "Capricorn"), ("Virgo", "Capricorn"),
    ("Gemini", "Libra"), ("Gemini", "Aquarius"), ("Libra", "Aquarius"),
    ("Cancer", "Scorpio"), ("Cancer", "Pisces"), ("Scorpio", "Pisces"),
}

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}


class MarriageCompatibilityEvaluator(BaseTwoPersonEvaluator, BaseEvaluator):
    """
    ENHANCED Evaluator for two-person Marriage Compatibility.
    
    Features:
    - Moon sign compatibility (emotional)
    - Venus sign compatibility (romantic)
    - Sun-Moon connections
    - Mars compatibility (Manglik matching)
    - Overall relationship dynamics
    - House lords analysis for BOTH charts
    - Timing windows extraction
    - Dasha timeline support
    - KP analysis integration
    """
    
    domain = "Marriage"
    subtopic = "Marriage Compatibility"
    
    positive_houses = {2, 7, 11}
    supportive_houses = {5}
    negative_houses = {6, 8, 12}
    key_planets = {"Venus", "Moon", "Mars", "Jupiter"}
    
    COMPATIBILITY_HOUSES = {2, 5, 7, 8, 11, 12}
    
    HOUSE_MEANINGS = {
        2: "Family/Wealth",
        5: "Romance/Children",
        7: "Spouse/Partnership",
        8: "Intimacy/Transformation",
        11: "Gains/Fulfillment",
        12: "Bedroom/Spiritual Union"
    }
    
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        **kwargs
    ) -> EvaluationResult:
        """Single person evaluation - provides individual marriage indicators"""
        self.reset()
        result = EvaluationResult()
        
        # Choose data source
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses
        
        planets = detect_aspects(planets)
        if vedic_planets:
            detect_aspects(vedic_planets)
        
        # Calculate aspects
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.error(f"Aspect calculation error: {e}")
        
        # Get question-specific houses
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )
        
        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses
        else:
            all_relevant_houses = self.COMPATIBILITY_HOUSES
            primary_houses = {7, 2, 11}
            secondary_houses = {5, 8, 12}
        
        # Extract house lords
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )
        
        # Extract aspects
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )
        
        # Extract timing windows
        timing_windows_raw = kwargs.get("timing_windows", {})
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            if not timing_windows_list and "Compatibility" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Compatibility"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
        
        timing_windows_data = self._extract_timing_windows(timing_windows_list)
        
        # Add house analysis points
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )
        
        # Add KP analysis
        kp_points = self._evaluate_kp_marriage_promise(planets, houses)
        result.extend_points(kp_points)
        
        # Store data for LLM
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data
        )
        
        result.add_point("For full compatibility analysis, please provide partner's birth details.")
        
        return result
    
    def evaluate_compatibility(
        self,
        planets1: Dict[str, Dict],
        houses1: List[Dict],
        planets2: Dict[str, Dict],
        houses2: List[Dict],
        sex1: str,
        sex2: str,
        vedic_planets1: Optional[Dict[str, Dict]] = None,
        vedic_houses1: Optional[List[Dict]] = None,
        vedic_planets2: Optional[Dict[str, Dict]] = None,
        vedic_houses2: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        ENHANCED: Evaluate compatibility between two people.
        
        Returns comprehensive compatibility analysis with:
        - House lords for both charts
        - Timing windows
        - KP analysis
        - Dasha timeline support
        """
        # ═══════════════════════════════════════════════════════════════
        # EXTENSIVE DEBUG LOGGING - TRACE DATA FLOW
        # ═══════════════════════════════════════════════════════════════
        logger.info("=" * 60)
        logger.info("🔍 COMPATIBILITY EVALUATOR - DEBUG START")
        logger.info("=" * 60)
        
        # Check what data we received
        logger.info(f"📊 PERSON 1 - KP planets received: {bool(planets1)}, count: {len(planets1) if planets1 else 0}")
        logger.info(f"📊 PERSON 1 - KP houses received: {bool(houses1)}, count: {len(houses1) if houses1 else 0}")
        logger.info(f"📊 PERSON 1 - Vedic planets received: {bool(vedic_planets1)}, count: {len(vedic_planets1) if vedic_planets1 else 0}")
        logger.info(f"📊 PERSON 1 - Vedic houses received: {bool(vedic_houses1)}, count: {len(vedic_houses1) if vedic_houses1 else 0}")
        
        logger.info(f"📊 PERSON 2 - KP planets received: {bool(planets2)}, count: {len(planets2) if planets2 else 0}")
        logger.info(f"📊 PERSON 2 - KP houses received: {bool(houses2)}, count: {len(houses2) if houses2 else 0}")
        logger.info(f"📊 PERSON 2 - Vedic planets received: {bool(vedic_planets2)}, count: {len(vedic_planets2) if vedic_planets2 else 0}")
        logger.info(f"📊 PERSON 2 - Vedic houses received: {bool(vedic_houses2)}, count: {len(vedic_houses2) if vedic_houses2 else 0}")
        
        # Log Mars positions for Manglik check
        Ma1 = _p(planets1, "Mars") if planets1 else None
        Ma2 = _p(planets2, "Mars") if planets2 else None
        logger.info(f"🔴 PERSON 1 - Mars data: {Ma1}")
        logger.info(f"🔴 PERSON 2 - Mars data: {Ma2}")
        
        if Ma1:
            logger.info(f"🔴 PERSON 1 - Mars house: {Ma1.get('house')}")
        if Ma2:
            logger.info(f"🔴 PERSON 2 - Mars house: {Ma2.get('house')}")
        
        # Check if person2 data is actually different from person1
        if planets1 and planets2:
            p1_moon = _p(planets1, "Moon")
            p2_moon = _p(planets2, "Moon")
            logger.info(f"🌙 PERSON 1 - Moon: {p1_moon.get('sign') if p1_moon else 'N/A'}, house: {p1_moon.get('house') if p1_moon else 'N/A'}")
            logger.info(f"🌙 PERSON 2 - Moon: {p2_moon.get('sign') if p2_moon else 'N/A'}, house: {p2_moon.get('house') if p2_moon else 'N/A'}")
            
            # Check if they're the same (indicating bug)
            if p1_moon and p2_moon:
                if p1_moon.get('house') == p2_moon.get('house') and p1_moon.get('sign') == p2_moon.get('sign'):
                    logger.warning("⚠️ WARNING: Person 1 and Person 2 Moon data IDENTICAL - possible data passing bug!")
        
        logger.info("=" * 60)
        
        # Choose data sources
        analysis_planets1 = vedic_planets1 if vedic_planets1 else planets1
        analysis_houses1 = vedic_houses1 if vedic_houses1 else houses1
        analysis_planets2 = vedic_planets2 if vedic_planets2 else planets2
        analysis_houses2 = vedic_houses2 if vedic_houses2 else houses2
        
        logger.info(f"🌟 Using {'VEDIC' if vedic_planets1 else 'KP'} data for Person 1")
        logger.info(f"🌟 Using {'VEDIC' if vedic_planets2 else 'KP'} data for Person 2")
        
        # Detect aspects for both charts
        planets1 = detect_aspects(planets1)
        planets2 = detect_aspects(planets2)
        if vedic_planets1:
            detect_aspects(vedic_planets1)
        if vedic_planets2:
            detect_aspects(vedic_planets2)
        
        # Calculate aspects for both
        aspects_data1 = {}
        aspects_data2 = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data1 = calculate_planetary_aspects(analysis_planets1)
                aspects_data2 = calculate_planetary_aspects(analysis_planets2)
            except Exception as e:
                logger.error(f"Aspect calculation error: {e}")
        
        # Get question-specific houses
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )
        
        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses
        else:
            all_relevant_houses = self.COMPATIBILITY_HOUSES
            primary_houses = {7, 2, 11}
            secondary_houses = {5, 8, 12}
        
        # Extract house lords for BOTH persons
        house_lords_person1 = self._extract_house_lords(
            analysis_houses1, analysis_planets1, all_relevant_houses, primary_houses
        )
        house_lords_person2 = self._extract_house_lords(
            analysis_houses2, analysis_planets2, all_relevant_houses, primary_houses
        )
        
        # Extract aspects for BOTH persons
        house_aspects_person1 = self._extract_aspects_on_houses(
            analysis_houses1, analysis_planets1, aspects_data1, all_relevant_houses
        )
        house_aspects_person2 = self._extract_aspects_on_houses(
            analysis_houses2, analysis_planets2, aspects_data2, all_relevant_houses
        )
        
        # Extract timing windows
        timing_windows_raw = kwargs.get("timing_windows", {})
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            if not timing_windows_list:
                for key in ["Compatibility", "Marriage Timing", "Best Marriage Period"]:
                    if key in timing_windows_raw:
                        timing_windows_list = timing_windows_raw[key]
                        break
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
        
        timing_windows_data = self._extract_timing_windows(timing_windows_list)
        
        # Initialize scores
        compatibility_score = 50
        notes = []
        detailed_scores = {}
        
        # Get key planets
        Ve1, Ve2 = _p(planets1, "Venus"), _p(planets2, "Venus")
        Mo1, Mo2 = _p(planets1, "Moon"), _p(planets2, "Moon")
        Su1, Su2 = _p(planets1, "Sun"), _p(planets2, "Sun")
        Ma1, Ma2 = _p(planets1, "Mars"), _p(planets2, "Mars")
        Ju1, Ju2 = _p(planets1, "Jupiter"), _p(planets2, "Jupiter")
        
        # 1. Moon Sign Compatibility (Emotional Connection)
        moon_score, moon_notes = self._evaluate_moon_compatibility(Mo1, Mo2)
        compatibility_score += moon_score
        notes.extend(moon_notes)
        detailed_scores["moon_compatibility"] = {
            "score": moon_score,
            "max": 20,
            "notes": moon_notes
        }
        
        # 2. Venus Sign Compatibility (Romantic Connection)
        venus_score, venus_notes = self._evaluate_venus_compatibility(Ve1, Ve2)
        compatibility_score += venus_score
        notes.extend(venus_notes)
        detailed_scores["venus_compatibility"] = {
            "score": venus_score,
            "max": 15,
            "notes": venus_notes
        }
        
        # 3. Sun-Moon Connection (Natural Attraction)
        sun_moon_score, sun_moon_notes = self._evaluate_sun_moon_connection(Su1, Mo1, Su2, Mo2)
        compatibility_score += sun_moon_score
        notes.extend(sun_moon_notes)
        detailed_scores["sun_moon_connection"] = {
            "score": sun_moon_score,
            "max": 15,
            "notes": sun_moon_notes
        }
        
        # 4. Mars Compatibility (Manglik Matching)
        mars_score, mars_notes, manglik_status = self._evaluate_mars_compatibility(Ma1, Ma2)
        compatibility_score += mars_score
        notes.extend(mars_notes)
        detailed_scores["mars_compatibility"] = {
            "score": mars_score,
            "max": 10,
            "notes": mars_notes
        }
        
        # 5. Jupiter Compatibility (Wisdom & Growth)
        jupiter_score, jupiter_notes = self._evaluate_jupiter_compatibility(Ju1, Ju2)
        compatibility_score += jupiter_score
        notes.extend(jupiter_notes)
        detailed_scores["jupiter_compatibility"] = {
            "score": jupiter_score,
            "max": 10,
            "notes": jupiter_notes
        }
        
        # 6. KP Compatibility Analysis (NEW)
        kp_score, kp_notes, kp_structured_data = self._evaluate_kp_compatibility(planets1, houses1, planets2, houses2)
        compatibility_score += kp_score
        notes.extend(kp_notes)
        detailed_scores["kp_compatibility"] = {
            "score": kp_score,
            "max": 15,
            "notes": kp_notes,
            "structured_data": kp_structured_data  # Include structured KP data
        }
        
        # 7. House Lords Compatibility (NEW)
        lords_score, lords_notes = self._evaluate_house_lords_compatibility(
            house_lords_person1, house_lords_person2
        )
        compatibility_score += lords_score
        notes.extend(lords_notes)
        detailed_scores["house_lords_compatibility"] = {
            "score": lords_score,
            "max": 15,
            "notes": lords_notes
        }
        
        # Cap score between 0 and 100
        compatibility_score = max(0, min(100, compatibility_score))
        
        # Generate summary
        if compatibility_score >= 80:
            summary = "Excellent compatibility with strong potential for lasting harmony and deep connection"
        elif compatibility_score >= 65:
            summary = "Good compatibility with many harmonious factors supporting the relationship"
        elif compatibility_score >= 50:
            summary = "Moderate compatibility - mutual understanding and effort will strengthen the bond"
        elif compatibility_score >= 35:
            summary = "Some challenges present - conscious effort needed for harmony"
        else:
            summary = "Significant differences exist - patience and understanding are essential"
        

        question_text = kwargs.get("question", "").lower()
        sub_subdomain = kwargs.get("sub_subdomain", "").lower()

        is_timing_question = (
            "timing" in question_text or
            "when" in question_text or
            "timing" in sub_subdomain or
            "best period" in question_text or
            "best time" in question_text
        )

        # If timing question, get KP promise for BOTH persons
        kp_promise_person1 = None
        kp_promise_person2 = None

        if is_timing_question:
            logger.info("🕐 Timing question detected - extracting KP promise for both persons")
            
            kp_promise_person1 = self._evaluate_kp_marriage_promise_structured(planets1, houses1)
            kp_promise_person2 = self._evaluate_kp_marriage_promise_structured(planets2, houses2)
            
            logger.info(f"Person 1 KP Promise: {kp_promise_person1.get('state')} (CSL: {kp_promise_person1.get('csl')})")
            logger.info(f"Person 2 KP Promise: {kp_promise_person2.get('state')} (CSL: {kp_promise_person2.get('csl')})")


        # Build result with enhanced data
        result = {
                "overall_score": compatibility_score,
                "relationship_score": compatibility_score,
                "manglik_status": manglik_status,
                "detailed_analysis": summary,
                "notes": notes,
                "detailed_scores": detailed_scores,
                "recommendation": self._generate_recommendation(compatibility_score, notes),
                
                # NEW: Enhanced data for LLM
                "compatibility_house_lords": {
                    "person1": house_lords_person1,
                    "person2": house_lords_person2
                },
                "compatibility_house_aspects": {
                    "person1": house_aspects_person1,
                    "person2": house_aspects_person2
                },
                "compatibility_timing_windows": timing_windows_data,
                "compatibility_analysis_summary": {
                    "person1_strong_lords": sum(
                        1 for info in house_lords_person1.values() 
                        if info.get("lord_strength_score", 0) >= 70
                    ),
                    "person2_strong_lords": sum(
                        1 for info in house_lords_person2.values() 
                        if info.get("lord_strength_score", 0) >= 70
                    ),
                    "person1_weak_lords": sum(
                        1 for info in house_lords_person1.values() 
                        if info.get("lord_strength_score", 0) < 40
                    ),
                    "person2_weak_lords": sum(
                        1 for info in house_lords_person2.values() 
                        if info.get("lord_strength_score", 0) < 40
                    )
                }
            }
            
            # ✅ ADD KP MARRIAGE PROMISE DATA (for timing questions)
        if is_timing_question and (kp_promise_person1 or kp_promise_person2):
                result["kp_marriage_promise"] = {
                    "person1": kp_promise_person1,
                    "person2": kp_promise_person2
                }
        logger.info("✅ KP Marriage Promise data stored in result")
            
            # Check for no timing - positive indicator
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
                result["no_compatibility_timing_issues"] = True
                result["compatibility_timing_assessment"] = "FAVORABLE - No specific challenging periods identified"
            
           
        # ═══════════════════════════════════════════════════════════════
        # FINAL RESULT DEBUG LOGGING
        # ════════════════
        logger.info("=" * 60)
        logger.info(f"Overall Score: {result.get('overall_score')}")
        logger.info(f"Manglik Status: {result.get('manglik_status')}")
        logger.info(f"Notes count: {len(result.get('notes', []))}")
        logger.info(f"Detailed scores keys: {list(result.get('detailed_scores', {}).keys())}")
        
        # Log first few notes for verification
        for i, note in enumerate(result.get('notes', [])[:5]):
            logger.info(f"Note {i+1}: {note[:100]}...")
        
        logger.info("=" * 60)
        
        return result
    

    def _evaluate_kp_marriage_promise_structured(self, planets: Dict, houses: List) -> Dict:
            """
            Evaluate KP marriage promise for single chart - STRUCTURED FORMAT.
            
            Returns structured data for deterministic extraction by prompts builder.
            Similar to Marriage Prospects pattern but for use in Compatibility domain.
            """
            # Get 7th cusp
            cusp7 = next((h for h in houses if h.get("house") == 7), {})
            c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
            
            # Initialize structured data
            kp_promise_data = {
                "csl": c7sub or "",
                "csl_sign": str(cusp7.get("start_rasi", "") or cusp7.get("rasi", "")),
                "state": "UNKNOWN",
                "reasoning": [],
                "benefic": False,
                "malefic": False
            }
            
            if not c7sub:
                kp_promise_data["state"] = "INCOMPLETE"
                kp_promise_data["reasoning"].append("7th Cusp Sub Lord data not available")
                return kp_promise_data
            
            # Determine benefic/malefic nature
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            
            if c7sub in benefics:
                kp_promise_data["benefic"] = True
                kp_promise_data["state"] = "PROMISED"
                kp_promise_data["reasoning"].append(f"7th CSL {c7sub} is a natural benefic")
                kp_promise_data["reasoning"].append("Indicates good marriage potential")
                
            elif c7sub in malefics:
                kp_promise_data["malefic"] = True
                kp_promise_data["state"] = "PROMISED_WITH_OBSTACLES"
                kp_promise_data["reasoning"].append(f"7th CSL {c7sub} is a natural malefic")
                kp_promise_data["reasoning"].append("Marriage promised but may need careful partner matching")
                
            else:
                kp_promise_data["state"] = "NEUTRAL"
                kp_promise_data["reasoning"].append(f"7th CSL {c7sub} is neutral")
                kp_promise_data["reasoning"].append("Marriage prospects depend on other factors")
            
            # Get significations (simplified - can be enhanced)
            planet_data = planets.get(c7sub, {})
            if planet_data:
                house_num = planet_data.get("house")
                if house_num:
                    kp_promise_data["csl_in_house"] = house_num
                    kp_promise_data["reasoning"].append(f"{c7sub} is placed in house {house_num}")
            
            return kp_promise_data

    
    # ═══════════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - HANDLES TimingWindow OBJECTS
    # ═══════════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow objects.
        """
        if not timing_windows:
            return {}
        
        try:
            def get_attr(obj, key, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    return getattr(obj, key, default)
            
            def window_to_dict(w):
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w
                
                result = {
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
                
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar', 
                                   'md', 'ad', 'pd', 'maha', 'antara', 'paryantar']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                
                return result
            
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )
            
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None
            
            from datetime import datetime
            
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
    
    # ═══════════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
    # ═══════════════════════════════════════════════════════════════════
    def _extract_house_lords(
        self,
        houses: list,
        planets: dict,
        relevant_houses: set,
        primary_houses: set
    ) -> dict:
        """Extract house lord information for relevant houses."""
        house_lords_info = {}
        
        for h in houses:
            house_num = h.get("house")
            
            if house_num not in relevant_houses:
                continue
            
            lord_name = (
                h.get("rashi_lord") or
                h.get("sign_lord") or
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
            lord_sign = lord_data.get("sign", "") or lord_data.get("rasi", "")
            
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
            
            lord_dignity = calculate_dignity_fallback(normalized_lord, lord_sign)
            lord_strength_score = self._calculate_lord_strength_from_dignity(
                normalized_lord, lord_data, lord_dignity
            )
            
            priority = "primary" if house_num in primary_houses else "secondary"
            
            planets_in_house = []
            for p in h.get("planets", []):
                planet_name = normalize_planet_name(self.extract_planet_name(p))
                if planet_name:
                    planets_in_house.append(planet_name)
            
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

    def _calculate_lord_strength_from_dignity(
        self,
        planet_name: str,
        planet_data: dict,
        dignity_str: str
    ) -> int:
        """Calculate lord strength score from dignity string (0-100)."""
        dignity_scores = {
            "Exalted": 100,
            "Own Sign": 80,
            "Friendly": 60,
            "Neutral": 40,
            "Enemy": 20,
            "Debilitated": 0,
            "Unknown": 50
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

    @staticmethod
    def extract_planet_name(p):
        """Extract planet name from dict or string"""
        if isinstance(p, dict):
            return p.get("name")
        if isinstance(p, str):
            return p
        return None

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None
    ):
        """Store enhanced data for LLM consumption."""
        domain_prefix = "compatibility"
        
        result.additional_data.update({
            f"{domain_prefix}_house_config": {
                "primary": list(primary_houses),
                "secondary": list(secondary_houses),
                "source": house_config.get("source", "fallback") if house_config else "fallback"
            },
            f"{domain_prefix}_house_lords": house_lords_info,
            f"{domain_prefix}_house_aspects": house_aspects_info,
            f"{domain_prefix}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "strong_lords": sum(
                    1 for info in house_lords_info.values() 
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values() 
                    if info["lord_strength_score"] < 40
                )
            }
        })
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for compatibility context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

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
            
            point_text = " ".join(point_parts)
            result.add_point(point_text)

    # ═══════════════════════════════════════════════════════════════════
    # KP ANALYSIS METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_kp_marriage_promise(self, planets: Dict, houses: List) -> List[str]:
        """Evaluate KP marriage promise for single chart."""
        points = []
        
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        if c7sub:
            points.append("")
            points.append("═══ KP MARRIAGE ANALYSIS ═══")
            points.append(f"7th Cusp Sub-Lord (CSL): {c7sub}")
            
            # Check Venus and Jupiter influence
            if c7sub in {"Venus", "Jupiter"}:
                points.append("✅ 7th CSL is natural benefic → Good marriage potential")
            elif c7sub in {"Saturn", "Rahu", "Ketu"}:
                points.append("⚠️ 7th CSL is malefic → May need partner matching carefully")
        
        return points
    
    def _evaluate_kp_compatibility(
            self,
            planets1: Dict,
            houses1: List,
            planets2: Dict,
            houses2: List
        ) -> tuple:
            """
            Evaluate KP-based compatibility between two charts.
            
            ENHANCED: Returns (score, notes, structured_kp_data)
            - score: int (compatibility score 0-15)
            - notes: List[str] (formatted notes with KP: prefix)
            - structured_kp_data: Dict (structured data for deterministic LLM extraction)
            """
            score = 0
            notes = []
            
            # Get 7th CSL for both
            cusp7_1 = next((h for h in houses1 if h.get("house") == 7), {})
            cusp7_2 = next((h for h in houses2 if h.get("house") == 7), {})
            
            c7sub_1 = normalize_planet(cusp7_1.get("cusp_sub_lord", ""))
            c7sub_2 = normalize_planet(cusp7_2.get("cusp_sub_lord", ""))
            
            # ✅ CREATE STRUCTURED KP DATA (for deterministic extraction)
            kp_structured_data = {
                "person1_7th_csl": c7sub_1,
                "person2_7th_csl": c7sub_2,
                "person1_7th_cusp_sign": str(cusp7_1.get("start_rasi", "") or cusp7_1.get("rasi", "")),
                "person2_7th_cusp_sign": str(cusp7_2.get("start_rasi", "") or cusp7_2.get("rasi", "")),
                "score": 0,  # Will be updated
                "max_score": 15,
                "verdict": "Unknown",
                "reasoning_parts": []
            }
            
            # ✅ Add formatted notes with KP: prefix (for backwards compatibility)
            notes.append("")
            notes.append("═══ KP COMPATIBILITY ANALYSIS ═══")
            
            if c7sub_1:
                notes.append(f"KP: Person 1 - 7th Cusp Sub Lord is {c7sub_1}")
                kp_structured_data["reasoning_parts"].append(f"Person 1's 7th CSL is {c7sub_1}")
            else:
                notes.append("KP: Person 1 - 7th Cusp Sub Lord data not available")
                
            if c7sub_2:
                notes.append(f"KP: Person 2 - 7th Cusp Sub Lord is {c7sub_2}")
                kp_structured_data["reasoning_parts"].append(f"Person 2's 7th CSL is {c7sub_2}")
            else:
                notes.append("KP: Person 2 - 7th Cusp Sub Lord data not available")
            
            # Check if we have data for both
            if not c7sub_1 or not c7sub_2:
                kp_structured_data["verdict"] = "INCOMPLETE"
                kp_structured_data["reasoning_parts"].append("Incomplete KP data for full compatibility analysis")
                notes.append("KP: Incomplete data - full KP compatibility analysis not possible")
                return score, notes, kp_structured_data
            
            # Both have benefic 7th CSL
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            
            if c7sub_1 in benefics and c7sub_2 in benefics:
                score += 10
                reasoning = f"Both have benefic 7th CSL ({c7sub_1} and {c7sub_2})"
                notes.append(f"KP: ✅ {reasoning} → Excellent KP compatibility")
                kp_structured_data["verdict"] = "FAVORABLE"
                kp_structured_data["reasoning_parts"].append(reasoning)
                kp_structured_data["reasoning_parts"].append("Both CSLs are benefic → Excellent compatibility")
                
            elif c7sub_1 in benefics or c7sub_2 in benefics:
                score += 5
                who = "Person 1" if c7sub_1 in benefics else "Person 2"
                which = c7sub_1 if c7sub_1 in benefics else c7sub_2
                reasoning = f"One has benefic 7th CSL ({who}: {which})"
                notes.append(f"KP: ⚖️ {reasoning} → Good KP compatibility")
                kp_structured_data["verdict"] = "MIXED"
                kp_structured_data["reasoning_parts"].append(reasoning)
                kp_structured_data["reasoning_parts"].append("One benefic CSL → Good compatibility")
                
            elif c7sub_1 in malefics and c7sub_2 in malefics:
                # Both malefic can actually work if they're compatible
                reasoning = f"Both have malefic 7th CSL ({c7sub_1} and {c7sub_2})"
                notes.append(f"KP: ⚠️ {reasoning} → KP suggests careful compatibility assessment")
                kp_structured_data["verdict"] = "NEUTRAL"
                kp_structured_data["reasoning_parts"].append(reasoning)
                kp_structured_data["reasoning_parts"].append("Both CSLs are malefic → Requires compatibility check")
                
            else:
                reasoning = "Neither has strongly benefic 7th CSL"
                notes.append(f"KP: ○ {reasoning} → KP suggests careful matching")
                kp_structured_data["verdict"] = "NEUTRAL"
                kp_structured_data["reasoning_parts"].append(reasoning)
            
            # Check if 7th CSLs are friendly planets
            friendship = FRIENDSHIP_TABLE.get(c7sub_1, {})
            
            if c7sub_2 in friendship.get("friends", []):
                score += 5
                reasoning = f"{c7sub_1} and {c7sub_2} are friendly planets"
                notes.append(f"KP: ✅ {reasoning} → Harmonious connection")
                kp_structured_data["reasoning_parts"].append(reasoning + " (friendly)")
                
            elif c7sub_2 in friendship.get("enemies", []):
                score -= 3
                reasoning = f"{c7sub_1} and {c7sub_2} are inimical planets"
                notes.append(f"KP: ⚠️ {reasoning} → Some friction possible")
                kp_structured_data["reasoning_parts"].append(reasoning + " (enemies)")
                
            elif c7sub_2 in friendship.get("neutral", []):
                reasoning = f"{c7sub_1} and {c7sub_2} are neutral planets"
                notes.append(f"KP: ○ {reasoning} → Neutral planetary relationship")
                kp_structured_data["reasoning_parts"].append(reasoning + " (neutral)")
            
            # ✅ Update final score in structured data
            kp_structured_data["score"] = score
            
            # ✅ Create consolidated reasoning
            kp_structured_data["reasoning"] = ". ".join(kp_structured_data["reasoning_parts"])
            
            # ✅ Return THREE values: score, notes, structured_data
            return score, notes, kp_structured_data
    
    def _evaluate_house_lords_compatibility(
        self,
        lords1: Dict,
        lords2: Dict
    ) -> tuple:
        """Evaluate house lords compatibility between two charts."""
        score = 0
        notes = []
        
        notes.append("")
        notes.append("═══ HOUSE LORDS COMPATIBILITY ═══")
        
        # Check 7th house lords
        lord7_1 = lords1.get(7, {})
        lord7_2 = lords2.get(7, {})
        
        if lord7_1 and lord7_2:
            strength1 = lord7_1.get("lord_strength_score", 50)
            strength2 = lord7_2.get("lord_strength_score", 50)
            
            avg_strength = (strength1 + strength2) / 2
            
            if avg_strength >= 70:
                score += 10
                notes.append(f"✅ Both 7th lords strong (avg: {avg_strength:.0f}/100) → Stable partnership")
            elif avg_strength >= 50:
                score += 5
                notes.append(f"⚖️ 7th lords moderate (avg: {avg_strength:.0f}/100) → Workable with effort")
            else:
                notes.append(f"⚠️ 7th lords weak (avg: {avg_strength:.0f}/100) → Extra attention needed")
            
            # Check dignity match
            dignity1 = lord7_1.get("lord_dignity", "")
            dignity2 = lord7_2.get("lord_dignity", "")
            
            strong_dignities = {"Exalted", "Own Sign", "Friendly"}
            if dignity1 in strong_dignities and dignity2 in strong_dignities:
                score += 5
                notes.append("✅ Both 7th lords well-dignified → Strong foundation")
        
        return score, notes

    # ═══════════════════════════════════════════════════════════════════
    # ORIGINAL COMPATIBILITY METHODS (PRESERVED)
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_moon_compatibility(self, Mo1: Dict, Mo2: Dict) -> tuple:
        """Evaluate emotional compatibility through Moon signs"""
        score = 0
        notes = []
        
        mo1_sign = (Mo1.get("sign") or Mo1.get("rasi") or "").title() if Mo1 else ""
        mo2_sign = (Mo2.get("sign") or Mo2.get("rasi") or "").title() if Mo2 else ""
        
        if not mo1_sign or not mo2_sign:
            return 0, ["Moon sign data incomplete for compatibility analysis"]
        
        if mo1_sign == mo2_sign:
            score += 15
            notes.append(f"💚 Moon signs match ({mo1_sign}) - excellent emotional understanding")
        elif SIGN_ELEMENTS.get(mo1_sign) == SIGN_ELEMENTS.get(mo2_sign):
            score += 10
            element = SIGN_ELEMENTS.get(mo1_sign)
            notes.append(f"💚 Moon signs share {element} element - natural emotional harmony")
        elif self._are_compatible_elements(mo1_sign, mo2_sign):
            score += 8
            notes.append("💚 Moon signs are elementally compatible - good emotional flow")
        elif (mo1_sign, mo2_sign) in COMPATIBLE_ELEMENTS or (mo2_sign, mo1_sign) in COMPATIBLE_ELEMENTS:
            score += 8
            notes.append("💚 Moon signs in trine - harmonious emotional connection")
        elif self._are_opposite_signs(mo1_sign, mo2_sign):
            score += 3
            notes.append("⚖️ Moon signs in opposition - magnetic attraction but may need balance")
        elif self._are_square_signs(mo1_sign, mo2_sign):
            score -= 2
            notes.append("⚠️ Moon signs in square - emotional tension possible")
        else:
            score += 2
            notes.append("○ Moon signs are neutral - emotional compatibility develops with time")
        
        return score, notes
    
    def _evaluate_venus_compatibility(self, Ve1: Dict, Ve2: Dict) -> tuple:
        """Evaluate romantic compatibility through Venus signs"""
        score = 0
        notes = []
        
        ve1_sign = (Ve1.get("sign") or Ve1.get("rasi") or "").title() if Ve1 else ""
        ve2_sign = (Ve2.get("sign") or Ve2.get("rasi") or "").title() if Ve2 else ""
        
        if not ve1_sign or not ve2_sign:
            return 0, ["Venus sign data incomplete for romantic compatibility"]
        
        if ve1_sign == ve2_sign:
            score += 12
            notes.append(f"💚 Venus in same sign ({ve1_sign}) - strong romantic compatibility")
        elif SIGN_ELEMENTS.get(ve1_sign) == SIGN_ELEMENTS.get(ve2_sign):
            score += 8
            notes.append("💚 Venus signs share element - harmonious romantic expression")
        elif self._are_compatible_elements(ve1_sign, ve2_sign):
            score += 5
            notes.append("💚 Venus signs elementally compatible - romantic understanding develops")
        elif (ve1_sign, ve2_sign) in COMPATIBLE_ELEMENTS or (ve2_sign, ve1_sign) in COMPATIBLE_ELEMENTS:
            score += 5
            notes.append("💚 Venus signs in trine - natural romantic flow")
        else:
            score += 2
            notes.append("○ Venus signs require adjustment - different love languages")
        
        return score, notes
    
    def _evaluate_sun_moon_connection(self, Su1: Dict, Mo1: Dict, Su2: Dict, Mo2: Dict) -> tuple:
        """Evaluate Sun-Moon cross connections"""
        score = 0
        notes = []
        
        su1_sign = (Su1.get("sign") or Su1.get("rasi") or "").title() if Su1 else ""
        su2_sign = (Su2.get("sign") or Su2.get("rasi") or "").title() if Su2 else ""
        mo1_sign = (Mo1.get("sign") or Mo1.get("rasi") or "").title() if Mo1 else ""
        mo2_sign = (Mo2.get("sign") or Mo2.get("rasi") or "").title() if Mo2 else ""
        
        if su1_sign == mo2_sign:
            score += 10
            notes.append("💚 Person 1's Sun in Person 2's Moon sign - natural attraction")
        if su2_sign == mo1_sign:
            score += 10
            notes.append("💚 Person 2's Sun in Person 1's Moon sign - deep soul connection")
        
        if SIGN_ELEMENTS.get(su1_sign) == SIGN_ELEMENTS.get(su2_sign):
            score += 3
            notes.append("💚 Sun signs share element - compatible life goals")
        
        if score == 0:
            notes.append("○ No direct Sun-Moon connection - connection builds through experiences")
        
        return min(score, 15), notes
    
    def _evaluate_mars_compatibility(self, Ma1: Dict, Ma2: Dict) -> tuple:
        """Evaluate Mars compatibility and Manglik status"""
        score = 0
        notes = []
        
        # ═══════════════════════════════════════════════════════════════
        # DETAILED MANGLIK DEBUG LOGGING
        # ═══════════════════════════════════════════════════════════════
        logger.info("=" * 50)
        logger.info("🔴 MANGLIK EVALUATION - DEBUG")
        logger.info("=" * 50)
        logger.info(f"Person 1 Mars data received: {Ma1}")
        logger.info(f"Person 2 Mars data received: {Ma2}")
        
        ma1_house = Ma1.get("house") if Ma1 else None
        ma2_house = Ma2.get("house") if Ma2 else None
        
        logger.info(f"Person 1 Mars house: {ma1_house}")
        logger.info(f"Person 2 Mars house: {ma2_house}")
        
        manglik_houses = {1, 2, 4, 7, 8, 12}
        logger.info(f"Manglik houses: {manglik_houses}")
        
        manglik1 = ma1_house in manglik_houses if ma1_house else False
        manglik2 = ma2_house in manglik_houses if ma2_house else False
        
        logger.info(f"Person 1 is Manglik: {manglik1} (house {ma1_house} in {manglik_houses})")
        logger.info(f"Person 2 is Manglik: {manglik2} (house {ma2_house} in {manglik_houses})")
        logger.info("=" * 50)
        
        manglik_status = {
            "person1": manglik1,
            "person2": manglik2,
            "person1_mars_house": ma1_house,
            "person2_mars_house": ma2_house
        }
        
        if manglik1 and manglik2:
            score += 8
            notes.append(f"💚 Both have Manglik dosha (P1: Mars in H{ma1_house}, P2: Mars in H{ma2_house}) - doshas cancel each other!")
            logger.info("✅ BOTH MANGLIK - Doshas cancel!")
        elif not manglik1 and not manglik2:
            score += 6
            notes.append(f"💚 Neither has Manglik dosha (P1: Mars in H{ma1_house}, P2: Mars in H{ma2_house}) - no Mars-related concerns")
            logger.info("✅ NEITHER MANGLIK - No concerns")
        elif manglik1 or manglik2:
            score -= 5
            who = "Person 1" if manglik1 else "Person 2"
            which_house = ma1_house if manglik1 else ma2_house
            notes.append(f"⚠️ {who} has Manglik dosha (Mars in house {which_house}) - remedial measures advised")
            logger.info(f"⚠️ ONE MANGLIK - {who} has it")
        
        ma1_sign = (Ma1.get("sign") or Ma1.get("rasi") or "").title() if Ma1 else ""
        ma2_sign = (Ma2.get("sign") or Ma2.get("rasi") or "").title() if Ma2 else ""
        
        if ma1_sign and ma2_sign:
            if SIGN_ELEMENTS.get(ma1_sign) == SIGN_ELEMENTS.get(ma2_sign):
                score += 2
                notes.append("💚 Mars signs compatible - similar energy styles")
        
        return score, notes, manglik_status
    
    def _evaluate_jupiter_compatibility(self, Ju1: Dict, Ju2: Dict) -> tuple:
        """Evaluate Jupiter compatibility for wisdom and growth"""
        score = 0
        notes = []
        
        ju1_sign = (Ju1.get("sign") or Ju1.get("rasi") or "").title() if Ju1 else ""
        ju2_sign = (Ju2.get("sign") or Ju2.get("rasi") or "").title() if Ju2 else ""
        
        if ju1_sign and ju2_sign:
            if ju1_sign == ju2_sign:
                score += 6
                notes.append("💚 Jupiter in same sign - shared philosophy and growth")
            elif SIGN_ELEMENTS.get(ju1_sign) == SIGN_ELEMENTS.get(ju2_sign):
                score += 4
                notes.append("💚 Jupiter signs compatible - harmonious spiritual alignment")
            else:
                score += 2
                notes.append("○ Different Jupiter signs - diverse perspectives enrich relationship")
        
        return score, notes
    
    def _are_compatible_elements(self, sign1: str, sign2: str) -> bool:
        """Check if elements are compatible (Fire-Air, Earth-Water)"""
        elem1 = SIGN_ELEMENTS.get(sign1)
        elem2 = SIGN_ELEMENTS.get(sign2)
        
        compatible_pairs = {
            ("Fire", "Air"), ("Air", "Fire"),
            ("Earth", "Water"), ("Water", "Earth")
        }
        
        return (elem1, elem2) in compatible_pairs
    
    def _are_opposite_signs(self, sign1: str, sign2: str) -> bool:
        """Check if signs are opposite in the zodiac"""
        opposites = {
            ("Aries", "Libra"), ("Taurus", "Scorpio"), ("Gemini", "Sagittarius"),
            ("Cancer", "Capricorn"), ("Leo", "Aquarius"), ("Virgo", "Pisces")
        }
        return (sign1, sign2) in opposites or (sign2, sign1) in opposites
    
    def _are_square_signs(self, sign1: str, sign2: str) -> bool:
        """Check if signs are in square aspect"""
        sign_numbers = {
            "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
            "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
            "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
        }
        
        num1 = sign_numbers.get(sign1, 0)
        num2 = sign_numbers.get(sign2, 0)
        
        diff = abs(num1 - num2)
        return diff == 3 or diff == 9
    
    def _generate_recommendation(self, score: int, notes: List[str]) -> str:
        """Generate overall recommendation based on analysis"""
        if score >= 75:
            return "This is a highly compatible match. Focus on maintaining positive dynamics while staying aware of any minor challenges."
        elif score >= 60:
            return "Good compatibility overall. Invest in understanding each other's emotional and communication styles for deeper connection."
        elif score >= 45:
            return "Moderate compatibility with both strengths and challenges. Success depends on mutual commitment and willingness to grow together."
        else:
            return "Some significant differences to navigate. Recommend pre-marital counseling and open communication about expectations."
    
    def get_questions(self) -> List[Question]:
        """Get predefined questions for Marriage Compatibility"""
        return [
            Question(
                id="MAR_COMP_C1",
                question=(
                    "How compatible are we based on our birth charts? What are the "
                    "strengths and challenges in this relationship?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Compatibility Analysis"
            ),
            Question(
                id="MAR_COMP_C2",
                question=(
                    "What is our emotional compatibility based on Moon signs? "
                    "How well do we understand each other's feelings?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Emotional Compatibility"
            ),
            Question(
                id="MAR_COMP_C3",
                question=(
                    "Do either of us have Manglik dosha? If so, does it affect "
                    "our compatibility and what remedies are recommended?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Manglik Analysis"
            ),
            Question(
                id="MAR_COMP_C4",
                question=(
                    "What is the best timing for our marriage based on both charts?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.POSITIVE,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Marriage Timing"
            )
        ]
"""
Lost Person or Belonging Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for finding lost persons, missing items, and stolen belongings
using traditional Vedic astrology principles.

✔ COMPLETE structural parity with Finance/Parenting evaluators
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Prashna (Horary) considerations
✔ Complete data storage for LLM

Key Houses for Lost/Missing:
- 2nd: Movable property, possessions, valuables
- 4th: Home, domestic items, vehicles, immovable property
- 6th: Theft, enemies, hidden things (if afflicted = theft)
- 7th: The missing person/thief (in Prashna), partners
- 8th: Hidden matters, secrets, investigations
- 11th: Recovery, gains, fulfillment of desires
- 12th: Loss, expenditure, things gone far away

Karakas:
- Moon: Mind, emotions, mother, missing person's state
- Mercury: Communication, documents, information about whereabouts
- Mars: Theft, aggression, courage to search
- Saturn: Delays, obstacles, distant places
- Rahu: Deception, foreign places, unusual circumstances
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
    logging.info("House lords analyzer available for Lost/Missing domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "lost_missing"


class LostPersonOrBelongingEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Lost/Missing → Lost Person or Belonging
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Recovery likelihood assessment
    - Direction indicators (Vedic)
    - NO KP analysis (purely Vedic)
    
    Traditional Vedic Rules for Lost Items/Persons:
    - 4th house strong + 11th lord well-placed = Recovery likely
    - 6th house afflicted = Theft indicated
    - 7th house = Represents the missing person or thief
    - 8th house = Hidden location, investigation needed
    - 12th house strong = Item/person far away, difficult recovery
    - Moon's condition = State of missing person/item
    """

    domain = "Lost_Missing"
    subtopic = "Lost Person or Belonging"

    # ══════════════════════════════════════════════════════════════
    # DIRECTION MAPPING (Vedic)
    # ══════════════════════════════════════════════════════════════
    DIRECTION_BY_SIGN = {
        "Aries": "East",
        "Taurus": "South",
        "Gemini": "West",
        "Cancer": "North",
        "Leo": "East",
        "Virgo": "South",
        "Libra": "West",
        "Scorpio": "North",
        "Sagittarius": "East",
        "Capricorn": "South",
        "Aquarius": "West",
        "Pisces": "North"
    }

    ELEMENT_BY_SIGN = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
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
            logger.warning(f"No config for question, using fallback for Lost/Missing")
            # Default houses for Lost/Missing domain
            # 2nd = possessions, 4th = home/property, 6th = theft/enemies
            # 7th = missing person/thief, 8th = hidden, 11th = recovery, 12th = loss
            primary_houses = {2, 4, 7, 11}
            secondary_houses = {6, 8, 12}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("LOST PERSON OR BELONGING EVALUATOR (VEDIC-ONLY v1.0)")
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
        # STEP 6: Vedic Recovery Analysis
        # ═══════════════════════════════════════════════════════════
        recovery_analysis = self._analyze_recovery_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Recovery analysis: {recovery_analysis.get('likelihood', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Direction Analysis (Vedic)
        # ═══════════════════════════════════════════════════════════
        direction_analysis = self._analyze_direction(
            analysis_planets,
            analysis_houses,
            house_lords_info
        )

        logger.info(f"✅ Direction indicated: {direction_analysis.get('primary_direction', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Theft vs Loss Analysis
        # ═══════════════════════════════════════════════════════════
        theft_analysis = self._analyze_theft_indicators(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Theft indicated: {theft_analysis.get('theft_indicated', False)}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Add Recovery-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_recovery_points(result, recovery_analysis, direction_analysis, theft_analysis)

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            recovery_analysis,
            direction_analysis,
            theft_analysis,
            kwargs
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # RECOVERY PROSPECTS ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_recovery_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze recovery prospects using Vedic principles.
        
        Favorable indicators:
        - 4th lord strong and well-placed
        - 11th lord strong (gains, recovery)
        - 2nd lord strong (possessions return)
        - Moon strong and unafflicted
        - Jupiter aspecting relevant houses
        
        Unfavorable indicators:
        - 12th lord strong (loss permanent)
        - 6th lord afflicting 2nd/4th (theft)
        - Saturn/Rahu in 4th or 2nd (delays/deception)
        - 8th lord afflicting recovery houses
        """
        analysis = {
            "likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "timing_hints": []
        }

        score = 50  # Start neutral

        # Check 11th house (recovery, gains)
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            if h11_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is strong ({h11_strength}/100) - recovery supported"
                )
            elif h11_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is weak ({h11_strength}/100) - recovery may require extra effort"
                )

        # Check 4th house (property, home)
        h4_info = house_lords_info.get(4, {})
        if h4_info:
            h4_strength = h4_info.get("lord_strength_score", 50)
            if h4_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    f"4th lord {h4_info.get('lord')} is strong - domestic items likely recoverable"
                )
            elif h4_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"4th lord {h4_info.get('lord')} is weak - property recovery may take additional effort"

                )

        # Check 2nd house (possessions)
        h2_info = house_lords_info.get(2, {})
        if h2_info:
            h2_strength = h2_info.get("lord_strength_score", 50)
            if h2_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    f"2nd lord {h2_info.get('lord')} is strong - valuables recovery supported"
                )

        # Check 12th house (loss - negative indicator)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            if h12_strength >= 70:
                score -= 15
                analysis["unfavorable_factors"].append(
                    f"12th lord {h12_info.get('lord')} is strong - loss may be prolonged or require extra effort"
                )

        # Check 8th house (hidden)
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_strength = h8_info.get("lord_strength_score", 50)
            if h8_strength >= 70:
                analysis["timing_hints"].append(
                    "Investigation may reveal hidden information"
                )

        # Check benefic aspects on 4th and 11th
        h4_aspects = house_aspects_info.get(4, {})
        h11_aspects = house_aspects_info.get(11, {})

        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 4th house - divine protection, recovery likely"
            )

        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 11th house - gains and recovery strongly supported"
            )

        # Check malefic aspects
        if "Saturn" in h4_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["timing_hints"].append(
                "Saturn's aspect indicates delays in recovery"
            )

        if "Rahu" in h4_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["unfavorable_factors"].append(
                "Rahu's aspect - confusion or deception involved"
            )

        # Check Moon (state of missing item/person)
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_sign = moon_data.get("sign", "")
            moon_house = moon_data.get("house")

            # Moon affliction check (VERY IMPORTANT for missing cases)
            moon_house_aspects = house_aspects_info.get(moon_house, {})
            malefics_on_moon = moon_house_aspects.get("malefic_aspects", [])

            if "Saturn" in malefics_on_moon or "Rahu" in malefics_on_moon:
                score -= 5
                analysis["unfavorable_factors"].append(
                    "Moon afflicted by malefics – emotional distress, confusion, or separation indicated"
                )

            
            # Moon in good houses for recovery
            if moon_house in [2, 4, 5, 9, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Moon in house {moon_house} - positive indicator for recovery"
                )
            elif moon_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Moon in house {moon_house} - challenges in recovery"
                )

        # Determine likelihood
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 70:
            analysis["likelihood"] = "HIGH"
        elif score >= 55:
            analysis["likelihood"] = "MODERATE"
        elif score >= 40:
            analysis["likelihood"] = "LOW"
        else:
            analysis["likelihood"] = "VERY_LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DIRECTION ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_direction(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict
    ) -> Dict:
        """
        Analyze probable direction of lost item/person using Vedic principles.
        
        Key indicators:
        - Sign of 4th house cusp (for domestic items)
        - Sign of 7th lord (for missing person)
        - Moon's sign (general indicator)
        - 4th lord's sign placement
        """
        analysis = {
            "primary_direction": "Unknown",
            "secondary_direction": None,
            "location_hints": [],
            "element_indicator": None
        }

        primary_direction = None
        secondary_direction = None

        # 1️⃣ Lost ITEM → 4th lord (highest priority)
        h4_info = house_lords_info.get(4, {})
        if h4_info:
            h4_lord_sign = h4_info.get("lord_in_sign")
            if h4_lord_sign in self.DIRECTION_BY_SIGN:
                primary_direction = self.DIRECTION_BY_SIGN[h4_lord_sign]
                analysis["element_indicator"] = self.ELEMENT_BY_SIGN.get(h4_lord_sign)
                analysis["location_hints"].append(
                    f"4th lord in {h4_lord_sign} suggests {primary_direction} direction"
                )

        # 2️⃣ Missing PERSON → 7th lord (only if 4th not set)
        if not primary_direction:
            h7_info = house_lords_info.get(7, {})
            if h7_info:
                h7_lord_sign = h7_info.get("lord_in_sign")
                if h7_lord_sign in self.DIRECTION_BY_SIGN:
                    primary_direction = self.DIRECTION_BY_SIGN[h7_lord_sign]
                    analysis["location_hints"].append(
                        f"7th lord in {h7_lord_sign} suggests missing person towards {primary_direction}"
                    )

        # 3️⃣ Moon → SUPPORTING ONLY
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_sign = moon_data.get("sign")
            moon_dir = self.DIRECTION_BY_SIGN.get(moon_sign)
            if moon_dir:
                if not primary_direction:
                    primary_direction = moon_dir
                    analysis["location_hints"].append(
                        f"Moon in {moon_sign} suggests {moon_dir} direction"
                    )
                elif moon_dir != primary_direction:
                    secondary_direction = moon_dir
                    analysis["location_hints"].append(
                        f"Moon in {moon_sign} supports {moon_dir} direction"
                    )

        analysis["primary_direction"] = primary_direction or "Unknown"
        analysis["secondary_direction"] = secondary_direction


        # Add element-based location hints
        if analysis["element_indicator"]:
            element = analysis["element_indicator"]
            if element == "Fire":
                analysis["location_hints"].append(
                    "Fire element: Near kitchen, fireplace, sunny/warm areas"
                )
            elif element == "Earth":
                analysis["location_hints"].append(
                    "Earth element: On ground level, garden, storage areas"
                )
            elif element == "Air":
                analysis["location_hints"].append(
                    "Air element: Upper floors, open areas, near windows"
                )
            elif element == "Water":
                analysis["location_hints"].append(
                    "Water element: Near bathroom, water sources, damp places"
                )

        return analysis

    # ══════════════════════════════════════════════════════════════
    # THEFT ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_theft_indicators(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze if theft is indicated vs simple loss/misplacement.
        
        Theft indicators:
        - 6th lord connected to 2nd or 4th house
        - Mars afflicting 2nd or 4th
        - Rahu/Ketu involvement with property houses
        - 7th house afflicted (thief represented)
        """
        analysis = {
            "theft_indicated": False,
            "theft_score": 0,
            "indicators": [],
            "thief_description": []
        }

        theft_score = 0

        # Check 6th lord connection to 2nd/4th
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            if h6_lord_house in [2, 4]:
                theft_score += 30
                analysis["indicators"].append(
                    f"6th lord {h6_info.get('lord')} in house {h6_lord_house} - theft strongly indicated"
                )

        # Check Mars affliction on 2nd/4th
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [2, 4]:
                theft_score += 15
                analysis["indicators"].append(
                    f"Mars in house {mars_house} - forceful taking or theft"
                )

        # Check Rahu involvement
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [2, 4, 7]:
                theft_score += 20
                analysis["indicators"].append(
                    f"Rahu in house {rahu_house} - deception or hidden taking"
                )
                analysis["thief_description"].append("Unusual circumstances or unknown person")

        # Check malefic aspects on 2nd and 4th
        h2_aspects = house_aspects_info.get(2, {})
        h4_aspects = house_aspects_info.get(4, {})

        malefics_on_2 = h2_aspects.get("malefic_aspects", [])
        malefics_on_4 = h4_aspects.get("malefic_aspects", [])

        if "Mars" in malefics_on_2 or "Mars" in malefics_on_4:
            theft_score += 10
            analysis["indicators"].append("Mars aspecting property houses - aggressive taking")

        if "Saturn" in malefics_on_2 or "Saturn" in malefics_on_4:
            theft_score += 5
            analysis["indicators"].append("Saturn aspect - methodical/planned loss")
            analysis["thief_description"].append("Possibly an older person or servant")

        # 7th house analysis for thief description
        h7_info = house_lords_info.get(7, {})
        if h7_info and theft_score > 30:
            h7_lord = h7_info.get("lord", "")
            h7_lord_sign = h7_info.get("lord_in_sign", "")
            
            # Thief description based on 7th lord's sign
            if h7_lord_sign in ["Aries", "Leo", "Sagittarius"]:
                analysis["thief_description"].append("Person of medium height, aggressive nature")
            elif h7_lord_sign in ["Taurus", "Virgo", "Capricorn"]:
                analysis["thief_description"].append("Person of practical nature, possibly known to you")
            elif h7_lord_sign in ["Gemini", "Libra", "Aquarius"]:
                analysis["thief_description"].append("Clever person, possibly young or communicative")
            elif h7_lord_sign in ["Cancer", "Scorpio", "Pisces"]:
                analysis["thief_description"].append("Emotional motive, possibly a neighbor or relative")

        analysis["theft_score"] = min(100, theft_score)
        analysis["theft_indicated"] = (
                theft_score >= 50 and
                h6_info and h6_info.get("lord_in_house") in [2, 4, 7]
            )


        return analysis

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION (Full - Finance Parity)
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

            # Get lord name
            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
                h.get("lord") or
                ""
            )

            # Deduce from sign if lord not found
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
                logger.warning(f"No lord found for house {house_num}")
                continue

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"No data found for lord {normalized_lord}")
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

            # Get lord dignity
            lord_dignity = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)

                    dignity = None
                    dignity = analyzer._get_dignity(
                        normalized_lord,
                        lord_sign,
                        lord_degree
                    )
                    lord_dignity = dignity.value


                    if dignity:

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

        degree = (
            planet_data.get("full_degree") or
            planet_data.get("global_degree") or
            planet_data.get("degree") or
            15
        )
        if degree < 5 or degree > 25:
            score -= 10

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for lost/missing context."""
        meanings = {
            2: "Possessions/Valuables",
            4: "Home/Property/Vehicles",
            6: "Theft/Enemies/Hidden",
            7: "Missing Person/Thief",
            8: "Secrets/Investigation",
            11: "Recovery/Gains",
            12: "Loss/Far Away"
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

            point_text = " ".join(point_parts)
            result.add_point(point_text)

    # ══════════════════════════════════════════════════════════════
    # ADD RECOVERY POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_recovery_points(
        self,
        result: EvaluationResult,
        recovery_analysis: Dict,
        direction_analysis: Dict,
        theft_analysis: Dict
    ):
        """Add recovery-specific points to result."""
        
        # Recovery likelihood
        likelihood = recovery_analysis.get("likelihood", "UNCERTAIN")
        score = recovery_analysis.get("score", 50)
        result.add_point(
            f"🔍 Recovery Likelihood: {likelihood} (Score: {score}/100)"
        )

        # Favorable factors
        for factor in recovery_analysis.get("favorable_factors", [])[:3]:
            result.add_point(f"✅ {factor}")

        # Unfavorable factors
        for factor in recovery_analysis.get("unfavorable_factors", [])[:3]:
            result.add_point(f"⚠️ {factor}")

        # Direction
        primary_dir = direction_analysis.get("primary_direction", "Unknown")
        if primary_dir != "Unknown":
            result.add_point(f"🧭 Primary Direction: {primary_dir}")

        # Theft indicator
        if theft_analysis.get("theft_indicated", False):
            result.add_point("🚨 Theft indicators present in chart")

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
        recovery_analysis: dict,
        direction_analysis: dict,
        theft_analysis: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

        result.additional_data.update({
            # House configuration
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },

            # House lords (FULL data)
            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,

            # House aspects (FULL data)
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            # Recovery analysis
            f"{DOMAIN_PREFIX}_recovery_analysis": recovery_analysis,

            # Direction analysis
            f"{DOMAIN_PREFIX}_direction_analysis": direction_analysis,

            # Theft analysis
            f"{DOMAIN_PREFIX}_theft_analysis": theft_analysis,

            # Analysis summary
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "primary_houses_count": len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "recovery_likelihood": recovery_analysis.get("likelihood", "UNCERTAIN"),
                "recovery_score": recovery_analysis.get("score", 50),
                "theft_indicated": theft_analysis.get("theft_indicated", False),
                "primary_direction": direction_analysis.get("primary_direction", "Unknown"),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                )
            },
        })

        logger.info(
            f"📦 STORED | recovery={recovery_analysis.get('likelihood')} | "
            f"theft={theft_analysis.get('theft_indicated')} | "
            f"direction={direction_analysis.get('primary_direction')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="LOST_MAIN",
                question=(
                    "How can I find a missing person or lost item, "
                    "and is recovery possible if it was stolen?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Lost Item or Person"
            )
        ]


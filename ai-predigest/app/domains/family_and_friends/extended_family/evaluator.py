"""
Extended Family Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for analyzing extended/joint family relationships,
inheritance disputes, and ancestral property matters using Vedic astrology.

✔ Simple and straightforward structure
✔ Focus on joint family, inheritance, ancestral property
✔ Full house lords extraction with dignity and strength
✔ NO KP analysis (Vedic-only domain)
✔ Complete data storage for LLM

Key Houses:
- 2nd: Family (kutumb), family wealth, ancestral wealth
- 4th: Ancestral property, home, mother's family, immovable assets
- 8th: Inheritance, in-laws, hidden family issues, legacies
- 9th: Father's family, elders, traditions, ancestral blessings
- 12th: Losses, expenses, family separation

Supporting Houses:
- 1st: Self, native's role in family
- 6th: Disputes, conflicts, litigation in family
- 11th: Gains, elder relatives, fulfillment from family

Karakas:
- Jupiter: Family prosperity, elders, traditions, blessings
- Saturn: Responsibilities, duties, karma, ancestral debts
- Sun: Father's lineage, authority in family
- Moon: Mother's lineage, emotional bonds, family home
- Mars: Property, disputes, siblings/cousins conflicts
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

DOMAIN_PREFIX = "extended_family"


class ExtendedFamilyEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Family and Friends → Extended Family
    
    Focuses on:
    - Joint/extended family harmony
    - Inheritance and ancestral property
    - Family responsibilities and duties
    """

    domain = "Family_Friends"
    subtopic = "Extended Family"

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

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data")

        # Set houses for extended family analysis
        primary_houses = {2, 4, 8, 9}
        secondary_houses = {1, 6, 11, 12}
        all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 60)
        logger.info("EXTENDED FAMILY EVALUATOR (VEDIC-ONLY v1.0)")
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

        # Family Harmony Analysis
        harmony_analysis = self._analyze_family_harmony(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Inheritance & Property Analysis
        inheritance_analysis = self._analyze_inheritance(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Dispute Potential
        dispute_analysis = self._analyze_disputes(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Add Points
        self._add_analysis_points(
            result,
            house_lords_info,
            harmony_analysis,
            inheritance_analysis,
            dispute_analysis
        )

        # Store Data for LLM
        self._store_data_for_llm(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            harmony_analysis,
            inheritance_analysis,
            dispute_analysis
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # FAMILY HARMONY ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_family_harmony(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze joint/extended family harmony."""
        analysis = {
            "harmony_level": "MODERATE",
            "harmony_score": 50,
            "favorable_factors": [],
            "challenging_factors": [],
            "responsibilities": []
        }

        score = 50

        # 2nd HOUSE - Family (Kutumb)
        h2_info = house_lords_info.get(2, {})
        h2_aspects = house_aspects_info.get(2, {})
        
        if h2_info:
            h2_strength = h2_info.get("lord_strength_score", 50)
            h2_lord = h2_info.get("lord", "")
            
            if h2_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"2nd lord {h2_lord} strong - good family unity and wealth"
                )
            elif h2_strength < 40:
                score -= 10
                analysis["challenging_factors"].append(
                    f"2nd lord {h2_lord} weak - family harmony needs effort"
                )

        # Benefics on 2nd
        if "Jupiter" in h2_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 2nd - blessings for family prosperity"
            )
        if "Venus" in h2_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Venus aspects 2nd - love and harmony in family"
            )

        # Malefics on 2nd
        if "Saturn" in h2_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["responsibilities"].append(
                "Saturn aspects 2nd - responsibilities towards family"
            )
        if "Mars" in h2_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["challenging_factors"].append(
                "Mars aspects 2nd - potential for family arguments"
            )

        # 4th HOUSE - Home, Ancestral Property
        h4_info = house_lords_info.get(4, {})
        h4_aspects = house_aspects_info.get(4, {})
        
        if h4_info:
            h4_strength = h4_info.get("lord_strength_score", 50)
            if h4_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    "4th lord strong - happiness from ancestral home"
                )
            elif h4_strength < 40:
                score -= 8
                analysis["challenging_factors"].append(
                    "4th lord weak - issues with family property/home"
                )

        # 9th HOUSE - Father's Family, Traditions
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            if h9_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "9th lord strong - support from paternal family"
                )

        # JUPITER - Family Karaka
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 2, 4, 5, 9, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - family prosperity blessed"
                )
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["challenging_factors"].append(
                    f"Jupiter in house {jupiter_house} - some family challenges"
                )

        # SATURN - Responsibilities
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [2, 4, 9]:
                analysis["responsibilities"].append(
                    f"Saturn in house {saturn_house} - significant family duties"
                )

        # Determine harmony level
        score = max(0, min(100, score))
        analysis["harmony_score"] = score

        if score >= 70:
            analysis["harmony_level"] = "HARMONIOUS"
        elif score >= 55:
            analysis["harmony_level"] = "GOOD"
        elif score >= 40:
            analysis["harmony_level"] = "MODERATE"
        elif score >= 25:
            analysis["harmony_level"] = "CHALLENGING"
        else:
            analysis["harmony_level"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # INHERITANCE & PROPERTY ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_inheritance(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze inheritance and ancestral property matters."""
        analysis = {
            "inheritance_prospects": "MODERATE",
            "inheritance_score": 50,
            "property_indicators": [],
            "caution_factors": [],
            "recommendations": []
        }

        score = 50

        # 8th HOUSE - Inheritance, Legacies
        h8_info = house_lords_info.get(8, {})
        h8_aspects = house_aspects_info.get(8, {})
        
        if h8_info:
            h8_strength = h8_info.get("lord_strength_score", 50)
            h8_lord = h8_info.get("lord", "")
            h8_lord_house = h8_info.get("lord_in_house")
            
            if h8_strength >= 70:
                score += 15
                analysis["property_indicators"].append(
                    f"8th lord {h8_lord} strong - good inheritance prospects"
                )
            elif h8_strength < 40:
                score -= 10
                analysis["caution_factors"].append(
                    f"8th lord {h8_lord} weak - inheritance may face obstacles"
                )

            # 8th lord placement
            if h8_lord_house in [2, 4, 11]:
                score += 8
                analysis["property_indicators"].append(
                    f"8th lord in house {h8_lord_house} - gains from inheritance"
                )
            elif h8_lord_house == 6:
                score -= 10
                analysis["caution_factors"].append(
                    "8th lord in 6th - disputes over inheritance likely"
                )
            elif h8_lord_house == 12:
                score -= 8
                analysis["caution_factors"].append(
                    "8th lord in 12th - losses in inheritance matters"
                )

        # Benefics/Malefics on 8th
        if "Jupiter" in h8_aspects.get("benefic_aspects", []):
            score += 10
            analysis["property_indicators"].append(
                "Jupiter aspects 8th - protected inheritance"
            )
        if "Rahu" in h8_aspects.get("malefic_aspects", []):
            score -= 8
            analysis["caution_factors"].append(
                "Rahu affects 8th - complications in inheritance"
            )

        # 4th HOUSE - Ancestral Property
        h4_info = house_lords_info.get(4, {})
        if h4_info:
            h4_strength = h4_info.get("lord_strength_score", 50)
            h4_lord_house = h4_info.get("lord_in_house")
            
            if h4_strength >= 70:
                score += 10
                analysis["property_indicators"].append(
                    "4th lord strong - ancestral property protected"
                )
            
            if h4_lord_house == 8:
                analysis["property_indicators"].append(
                    "4th lord in 8th - property through inheritance"
                )
            elif h4_lord_house == 12:
                score -= 8
                analysis["caution_factors"].append(
                    "4th lord in 12th - risk of property loss"
                )

        # MARS - Property Karaka
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            mars_sign = mars_data.get("sign", "")
            
            if mars_house == 4:
                analysis["property_indicators"].append(
                    "Mars in 4th - strong property connections"
                )
            if mars_sign in ["Aries", "Scorpio", "Capricorn"]:
                score += 5
                analysis["property_indicators"].append(
                    f"Mars in {mars_sign} - property karaka strong"
                )

        # 2nd HOUSE - Family Wealth
        h2_info = house_lords_info.get(2, {})
        if h2_info:
            h2_strength = h2_info.get("lord_strength_score", 50)
            if h2_strength >= 70:
                score += 8
                analysis["property_indicators"].append(
                    "2nd lord strong - ancestral wealth preserved"
                )

        # Determine inheritance prospects
        score = max(0, min(100, score))
        analysis["inheritance_score"] = score

        if score >= 70:
            analysis["inheritance_prospects"] = "FAVORABLE"
        elif score >= 55:
            analysis["inheritance_prospects"] = "GOOD"
        elif score >= 40:
            analysis["inheritance_prospects"] = "MODERATE"
        elif score >= 25:
            analysis["inheritance_prospects"] = "CHALLENGING"
        else:
            analysis["inheritance_prospects"] = "DIFFICULT"

        # Recommendations
        if score < 50:
            analysis["recommendations"].append(
                "Get legal documentation in order for property matters"
            )
        if any("dispute" in f.lower() for f in analysis["caution_factors"]):
            analysis["recommendations"].append(
                "Consider mediation for inheritance issues"
            )

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DISPUTE ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_disputes(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze potential for family disputes."""
        analysis = {
            "dispute_potential": "LOW",
            "dispute_score": 30,
            "dispute_factors": [],
            "resolution_factors": [],
            "advice": []
        }

        dispute_score = 30  # Start optimistic

        # 6th HOUSE - Disputes
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            
            # 6th lord in family houses = disputes
            if h6_lord_house in [2, 4, 8, 9]:
                dispute_score += 20
                analysis["dispute_factors"].append(
                    f"6th lord in house {h6_lord_house} - family disputes indicated"
                )

        # MARS - Conflict
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [2, 4, 8]:
                dispute_score += 15
                analysis["dispute_factors"].append(
                    f"Mars in house {mars_house} - aggressive energy in family matters"
                )

        # Mars aspects on family houses
        h2_aspects = house_aspects_info.get(2, {})
        h4_aspects = house_aspects_info.get(4, {})
        h8_aspects = house_aspects_info.get(8, {})
        
        if "Mars" in h2_aspects.get("malefic_aspects", []):
            dispute_score += 10
            analysis["dispute_factors"].append(
                "Mars aspects 2nd - arguments over family wealth"
            )
        if "Mars" in h4_aspects.get("malefic_aspects", []):
            dispute_score += 10
            analysis["dispute_factors"].append(
                "Mars aspects 4th - property disputes possible"
            )

        # RAHU - Complications
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [2, 4, 8]:
                dispute_score += 12
                analysis["dispute_factors"].append(
                    f"Rahu in house {rahu_house} - complications in family matters"
                )

        # SATURN - Delays but also structure
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [2, 4, 8]:
                dispute_score += 8
                analysis["dispute_factors"].append(
                    f"Saturn in house {saturn_house} - delays and restrictions in family"
                )

        # RESOLUTION FACTORS
        
        # Jupiter aspects
        if "Jupiter" in h2_aspects.get("benefic_aspects", []):
            dispute_score -= 10
            analysis["resolution_factors"].append(
                "Jupiter aspects 2nd - wisdom guides family decisions"
            )
        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            dispute_score -= 10
            analysis["resolution_factors"].append(
                "Jupiter aspects 4th - protection for property matters"
            )

        # Venus - Harmony
        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_house = venus_data.get("house")
            if venus_house in [2, 4]:
                dispute_score -= 8
                analysis["resolution_factors"].append(
                    f"Venus in house {venus_house} - love maintains family bonds"
                )

        # Determine dispute potential
        dispute_score = max(0, min(100, dispute_score))
        analysis["dispute_score"] = dispute_score

        if dispute_score >= 60:
            analysis["dispute_potential"] = "HIGH"
            analysis["advice"].append("Proactive communication is essential")
            analysis["advice"].append("Consider family meetings to address issues early")
        elif dispute_score >= 40:
            analysis["dispute_potential"] = "MODERATE"
            analysis["advice"].append("Handle differences with patience")
        else:
            analysis["dispute_potential"] = "LOW"
            analysis["advice"].append("Family harmony well supported")

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
        harmony_analysis: dict,
        inheritance_analysis: dict,
        dispute_analysis: dict
    ):
        """Add analysis points to result."""
        
        # Harmony
        result.add_point(
            f"👨‍👩‍👧‍👦 Family Harmony: {harmony_analysis.get('harmony_level')} "
            f"({harmony_analysis.get('harmony_score')}/100)"
        )

        # Inheritance
        result.add_point(
            f"🏠 Inheritance: {inheritance_analysis.get('inheritance_prospects')} "
            f"({inheritance_analysis.get('inheritance_score')}/100)"
        )

        # Disputes
        result.add_point(
            f"⚡ Dispute Potential: {dispute_analysis.get('dispute_potential')} "
            f"({dispute_analysis.get('dispute_score')}/100)"
        )

        # Key factors
        for factor in harmony_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in inheritance_analysis.get("property_indicators", [])[:2]:
            result.add_point(f"🏡 {factor}")
        for factor in dispute_analysis.get("dispute_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        for resp in harmony_analysis.get("responsibilities", [])[:1]:
            result.add_point(f"📋 {resp}")

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
        harmony_analysis: dict,
        inheritance_analysis: dict,
        dispute_analysis: dict
    ):
        """Store data for LLM consumption."""

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses)
            },
            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,
            f"{DOMAIN_PREFIX}_harmony_analysis": harmony_analysis,
            f"{DOMAIN_PREFIX}_inheritance_analysis": inheritance_analysis,
            f"{DOMAIN_PREFIX}_dispute_analysis": dispute_analysis,
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "harmony_level": harmony_analysis.get("harmony_level", "MODERATE"),
                "harmony_score": harmony_analysis.get("harmony_score", 50),
                "inheritance_prospects": inheritance_analysis.get("inheritance_prospects", "MODERATE"),
                "inheritance_score": inheritance_analysis.get("inheritance_score", 50),
                "dispute_potential": dispute_analysis.get("dispute_potential", "LOW"),
                "dispute_score": dispute_analysis.get("dispute_score", 30),
            },
        })

        logger.info(
            f"📦 STORED | harmony={harmony_analysis.get('harmony_level')} | "
            f"inheritance={inheritance_analysis.get('inheritance_prospects')} | "
            f"disputes={dispute_analysis.get('dispute_potential')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="EXTENDED_FAMILY_MAIN",
                question=(
                    "What does astrology indicate about potential problems in joint or "
                    "extended family, inheritance disputes and responsibilities related "
                    "to ancestral property and duties?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Family Relations"
            )
        ]
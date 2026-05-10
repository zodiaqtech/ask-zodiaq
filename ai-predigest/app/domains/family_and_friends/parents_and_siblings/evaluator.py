"""
Parents and Siblings Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for analyzing relationships with parents and siblings
using traditional Vedic astrology principles.

Covers two sub-subdomains:
1. Relationship with Parents - harmony, disputes, elder care responsibilities
2. Relationship with Siblings - harmony, disputes, support

✔ Simple and straightforward structure
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Complete data storage for LLM

Key Houses for Parents:
- 4th: Mother, maternal happiness, home environment
- 9th: Father, paternal blessings, dharma from parents
- 10th: Father (alternate), authority figures, responsibilities

Key Houses for Siblings:
- 3rd: Younger siblings, courage, communication with siblings
- 11th: Elder siblings, gains through siblings, support network

Additional Houses:
- 1st: Self, native's nature in relationships
- 2nd: Family (kutumb), family harmony
- 6th: Disputes, conflicts, enmity
- 8th: Hidden tensions, inheritance issues
- 12th: Losses, separation from family

Karakas:
- Sun: Father, authority, paternal figures
- Moon: Mother, emotions, maternal care
- Mars: Siblings (especially younger), courage, conflicts
- Jupiter: Elder figures, blessings, wisdom, elder siblings
- Mercury: Communication, younger siblings
- Saturn: Responsibilities, elder care, karma with parents
- Venus: Harmony, love, family happiness
"""

from typing import Dict, List, Optional
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
    logging.info("House lords analyzer available for Family domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "family_parents_siblings"


class ParentsAndSiblingsEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Family and Friends → Parents and Siblings
    
    Handles two sub-subdomains:
    1. Relationship with Parents
    2. Relationship with Siblings
    """

    domain = "Family_Friends"
    subtopic = "Parents and Siblings"

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

        # Normalize Meta
        meta = kwargs.get("meta")
        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")

        # Determine query type: Parents or Siblings
        is_parents_query = self._is_parents_query(question_text, sub_subdomain)
        is_siblings_query = self._is_siblings_query(question_text, sub_subdomain)

        # Select Analysis Data (Vedic preferred)
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for analysis")
        logger.info(f"📋 Query type: Parents={is_parents_query}, Siblings={is_siblings_query}")

        # Get Question-Specific Houses or use defaults
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = set(house_config["primary"])
            secondary_houses = set(house_config["secondary"])
        else:
            # Set houses based on query type
            if is_parents_query:
                primary_houses = {4, 9, 10}  # Mother, Father, Authority
                secondary_houses = {1, 2, 6, 8, 12}
            elif is_siblings_query:
                primary_houses = {3, 11}  # Younger siblings, Elder siblings
                secondary_houses = {1, 2, 6, 8, 12}
            else:
                # Default: Both parents and siblings
                primary_houses = {3, 4, 9, 11}
                secondary_houses = {1, 2, 6, 8, 10, 12}
        
        all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 60)
        logger.info("PARENTS AND SIBLINGS EVALUATOR (VEDIC-ONLY v1.0)")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
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

        # Extract House Lords Data
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        # Extract Aspects on Houses
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        # Perform analysis based on query type
        if is_parents_query:
            relationship_analysis = self._analyze_parents_relationship(
                analysis_planets,
                house_lords_info,
                house_aspects_info
            )
        elif is_siblings_query:
            relationship_analysis = self._analyze_siblings_relationship(
                analysis_planets,
                house_lords_info,
                house_aspects_info
            )
        else:
            # Analyze both
            relationship_analysis = self._analyze_family_relationships(
                analysis_planets,
                house_lords_info,
                house_aspects_info
            )

        # Dispute Analysis
        dispute_analysis = self._analyze_dispute_potential(
            analysis_planets,
            house_lords_info,
            house_aspects_info,
            is_parents_query,
            is_siblings_query
        )

        # Add Points to Result
        self._add_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            relationship_analysis,
            dispute_analysis,
            is_parents_query,
            is_siblings_query
        )

        # Store Data for LLM
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            relationship_analysis,
            dispute_analysis,
            is_parents_query,
            is_siblings_query
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # QUERY TYPE DETECTION
    # ══════════════════════════════════════════════════════════════
    def _is_parents_query(self, question: str, sub_subdomain: str) -> bool:
        """Check if query is about parents"""
        keywords = ["parent", "mother", "father", "mom", "dad", "elder care", 
                    "माता", "पिता", "माँ", "पापा", "बुजुर्ग"]
        text = (question + " " + sub_subdomain).lower()
        return any(kw in text for kw in keywords)

    def _is_siblings_query(self, question: str, sub_subdomain: str) -> bool:
        """Check if query is about siblings"""
        keywords = ["sibling", "brother", "sister", "bhai", "behan", 
                    "भाई", "बहन", "भाई-बहन"]
        text = (question + " " + sub_subdomain).lower()
        return any(kw in text for kw in keywords)

    # ══════════════════════════════════════════════════════════════
    # PARENTS RELATIONSHIP ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_parents_relationship(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze relationship with parents."""
        analysis = {
            "relationship_quality": "MODERATE",
            "harmony_score": 50,
            "mother_relationship": "MODERATE",
            "father_relationship": "MODERATE",
            "elder_care_indicated": False,
            "favorable_factors": [],
            "challenging_factors": [],
            "relationship_hints": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 4th HOUSE (Mother, Maternal Happiness)
        # ═══════════════════════════════════════════════════════════
        h4_info = house_lords_info.get(4, {})
        h4_aspects = house_aspects_info.get(4, {})
        
        if h4_info:
            h4_strength = h4_info.get("lord_strength_score", 50)
            h4_lord = h4_info.get("lord", "")
            
            if h4_strength >= 70:
                score += 12
                analysis["mother_relationship"] = "HARMONIOUS"
                analysis["favorable_factors"].append(
                    f"4th lord {h4_lord} is strong - good relationship with mother"
                )
            elif h4_strength < 40:
                score -= 10
                analysis["mother_relationship"] = "CHALLENGING"
                analysis["challenging_factors"].append(
                    f"4th lord {h4_lord} is weak - challenges in maternal relationship"
                )

        # Moon (Mother Karaka)
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_house = moon_data.get("house")
            if moon_house in [1, 4, 5, 9, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Moon in house {moon_house} - emotional bond with mother strong"
                )
            elif moon_house in [6, 8, 12]:
                score -= 5
                analysis["challenging_factors"].append(
                    f"Moon in house {moon_house} - some emotional distance with mother"
                )

        # Benefic aspects on 4th
        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 4th house - blessings in maternal relationship"
            )
        if "Venus" in h4_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Venus aspects 4th house - love and harmony with mother"
            )

        # Malefic aspects on 4th
        if "Saturn" in h4_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["relationship_hints"].append(
                "Saturn aspects 4th - responsibilities towards mother, elder care may be needed"
            )
            analysis["elder_care_indicated"] = True
        if "Mars" in h4_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["challenging_factors"].append(
                "Mars aspects 4th - potential for conflicts with mother"
            )

        # ═══════════════════════════════════════════════════════════
        # 9th HOUSE (Father, Paternal Blessings)
        # ═══════════════════════════════════════════════════════════
        h9_info = house_lords_info.get(9, {})
        h9_aspects = house_aspects_info.get(9, {})
        
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            h9_lord = h9_info.get("lord", "")
            
            if h9_strength >= 70:
                score += 12
                analysis["father_relationship"] = "HARMONIOUS"
                analysis["favorable_factors"].append(
                    f"9th lord {h9_lord} is strong - good relationship with father"
                )
            elif h9_strength < 40:
                score -= 10
                analysis["father_relationship"] = "CHALLENGING"
                analysis["challenging_factors"].append(
                    f"9th lord {h9_lord} is weak - challenges in paternal relationship"
                )

        # Sun (Father Karaka)
        sun_data = planets.get("Sun", {})
        if sun_data:
            sun_house = sun_data.get("house")
            sun_sign = sun_data.get("sign", "")
            
            # Sun in good houses
            if sun_house in [1, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Sun in house {sun_house} - strong paternal connection"
                )
            elif sun_house in [6, 8, 12]:
                score -= 5
                analysis["challenging_factors"].append(
                    f"Sun in house {sun_house} - some distance with father"
                )
            
            # Sun dignity
            if sun_sign == "Leo":
                score += 5
                analysis["favorable_factors"].append(
                    "Sun in own sign - father figure strong and supportive"
                )
            elif sun_sign == "Libra":
                score -= 5
                analysis["challenging_factors"].append(
                    "Sun debilitated - father relationship may need attention"
                )

        # Benefic aspects on 9th
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - paternal blessings strong"
            )

        # ═══════════════════════════════════════════════════════════
        # 10th HOUSE (Father alternate, Responsibilities)
        # ═══════════════════════════════════════════════════════════
        h10_info = house_lords_info.get(10, {})
        if h10_info:
            h10_strength = h10_info.get("lord_strength_score", 50)
            if h10_strength >= 70:
                score += 5
                analysis["relationship_hints"].append(
                    "10th house strong - able to fulfill responsibilities towards parents"
                )

        # Saturn (Elder Care, Responsibilities)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [4, 9, 10]:
                analysis["elder_care_indicated"] = True
                analysis["relationship_hints"].append(
                    f"Saturn in house {saturn_house} - significant responsibilities towards parents"
                )

        # ═══════════════════════════════════════════════════════════
        # 2nd HOUSE (Family Harmony)
        # ═══════════════════════════════════════════════════════════
        h2_info = house_lords_info.get(2, {})
        if h2_info:
            h2_strength = h2_info.get("lord_strength_score", 50)
            if h2_strength >= 70:
                score += 5
                analysis["favorable_factors"].append(
                    "2nd lord strong - overall family harmony supported"
                )

        # Determine relationship quality
        score = max(0, min(100, score))
        analysis["harmony_score"] = score

        if score >= 75:
            analysis["relationship_quality"] = "EXCELLENT"
        elif score >= 60:
            analysis["relationship_quality"] = "HARMONIOUS"
        elif score >= 45:
            analysis["relationship_quality"] = "MODERATE"
        elif score >= 30:
            analysis["relationship_quality"] = "CHALLENGING"
        else:
            analysis["relationship_quality"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # SIBLINGS RELATIONSHIP ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_siblings_relationship(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze relationship with siblings."""
        analysis = {
            "relationship_quality": "MODERATE",
            "harmony_score": 50,
            "younger_siblings": "MODERATE",
            "elder_siblings": "MODERATE",
            "sibling_support": False,
            "favorable_factors": [],
            "challenging_factors": [],
            "relationship_hints": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 3rd HOUSE (Younger Siblings, Courage)
        # ═══════════════════════════════════════════════════════════
        h3_info = house_lords_info.get(3, {})
        h3_aspects = house_aspects_info.get(3, {})
        
        if h3_info:
            h3_strength = h3_info.get("lord_strength_score", 50)
            h3_lord = h3_info.get("lord", "")
            h3_lord_house = h3_info.get("lord_in_house")
            
            if h3_strength >= 70:
                score += 15
                analysis["younger_siblings"] = "HARMONIOUS"
                analysis["favorable_factors"].append(
                    f"3rd lord {h3_lord} is strong - good relationship with younger siblings"
                )
            elif h3_strength < 40:
                score -= 10
                analysis["younger_siblings"] = "CHALLENGING"
                analysis["challenging_factors"].append(
                    f"3rd lord {h3_lord} is weak - challenges with younger siblings"
                )
            
            # 3rd lord in good houses
            if h3_lord_house in [1, 3, 5, 9, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    f"3rd lord in house {h3_lord_house} - supportive younger siblings"
                )
            elif h3_lord_house == 6:
                score -= 8
                analysis["challenging_factors"].append(
                    "3rd lord in 6th - disputes with younger siblings possible"
                )
            elif h3_lord_house == 8:
                score -= 5
                analysis["relationship_hints"].append(
                    "3rd lord in 8th - hidden tensions with younger siblings"
                )
            elif h3_lord_house == 12:
                score -= 5
                analysis["relationship_hints"].append(
                    "3rd lord in 12th - distance from younger siblings"
                )

        # Mars (Younger Siblings Karaka)
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            mars_sign = mars_data.get("sign", "")
            
            if mars_house == 3:
                score += 8
                analysis["favorable_factors"].append(
                    "Mars in 3rd house - strong bond with younger siblings"
                )
            
            # Mars dignity
            if mars_sign in ["Aries", "Scorpio", "Capricorn"]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Mars in {mars_sign} - siblings karaka strong"
                )
            elif mars_sign == "Cancer":
                score -= 5
                analysis["challenging_factors"].append(
                    "Mars debilitated - sibling relationships need care"
                )

        # Benefic aspects on 3rd
        if "Jupiter" in h3_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 3rd house - blessings in sibling relationships"
            )
        if "Venus" in h3_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Venus aspects 3rd - love and harmony with siblings"
            )

        # Malefic aspects on 3rd
        if "Saturn" in h3_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["relationship_hints"].append(
                "Saturn aspects 3rd - responsibilities or distance with siblings"
            )
        if "Rahu" in h3_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["challenging_factors"].append(
                "Rahu aspects 3rd - misunderstandings with siblings possible"
            )

        # ═══════════════════════════════════════════════════════════
        # 11th HOUSE (Elder Siblings, Gains, Support)
        # ═══════════════════════════════════════════════════════════
        h11_info = house_lords_info.get(11, {})
        h11_aspects = house_aspects_info.get(11, {})
        
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            h11_lord = h11_info.get("lord", "")
            
            if h11_strength >= 70:
                score += 15
                analysis["elder_siblings"] = "HARMONIOUS"
                analysis["sibling_support"] = True
                analysis["favorable_factors"].append(
                    f"11th lord {h11_lord} is strong - good relationship with elder siblings"
                )
            elif h11_strength < 40:
                score -= 10
                analysis["elder_siblings"] = "CHALLENGING"
                analysis["challenging_factors"].append(
                    f"11th lord {h11_lord} is weak - challenges with elder siblings"
                )

        # Jupiter (Elder Siblings Karaka)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house == 11:
                score += 8
                analysis["sibling_support"] = True
                analysis["favorable_factors"].append(
                    "Jupiter in 11th - elder siblings provide support and guidance"
                )
            if jupiter_house in [1, 5, 9]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - blessings in sibling bonds"
                )

        # Benefic aspects on 11th
        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            score += 8
            analysis["sibling_support"] = True
            analysis["favorable_factors"].append(
                "Jupiter aspects 11th - gains and support through siblings"
            )

        # ═══════════════════════════════════════════════════════════
        # Mercury (Communication with Siblings)
        # ═══════════════════════════════════════════════════════════
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            if mercury_house in [3, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Mercury in house {mercury_house} - good communication with siblings"
                )

        # Determine relationship quality
        score = max(0, min(100, score))
        analysis["harmony_score"] = score

        if score >= 75:
            analysis["relationship_quality"] = "EXCELLENT"
        elif score >= 60:
            analysis["relationship_quality"] = "HARMONIOUS"
        elif score >= 45:
            analysis["relationship_quality"] = "MODERATE"
        elif score >= 30:
            analysis["relationship_quality"] = "CHALLENGING"
        else:
            analysis["relationship_quality"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # COMBINED FAMILY RELATIONSHIPS ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_family_relationships(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze both parents and siblings relationships."""
        parents = self._analyze_parents_relationship(planets, house_lords_info, house_aspects_info)
        siblings = self._analyze_siblings_relationship(planets, house_lords_info, house_aspects_info)
        
        # Combine scores
        combined_score = (parents["harmony_score"] + siblings["harmony_score"]) // 2
        
        return {
            "relationship_quality": parents["relationship_quality"],
            "harmony_score": combined_score,
            "parents_analysis": parents,
            "siblings_analysis": siblings,
            "favorable_factors": parents["favorable_factors"][:3] + siblings["favorable_factors"][:3],
            "challenging_factors": parents["challenging_factors"][:2] + siblings["challenging_factors"][:2],
            "relationship_hints": parents["relationship_hints"][:2] + siblings["relationship_hints"][:2]
        }

    # ══════════════════════════════════════════════════════════════
    # DISPUTE POTENTIAL ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_dispute_potential(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        is_parents: bool,
        is_siblings: bool
    ) -> Dict:
        """Analyze potential for disputes."""
        analysis = {
            "dispute_potential": "LOW",
            "dispute_score": 30,
            "dispute_factors": [],
            "resolution_factors": [],
            "advice": []
        }

        dispute_score = 30  # Start optimistic

        # ═══════════════════════════════════════════════════════════
        # 6th HOUSE (Disputes, Conflicts)
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            
            # 6th lord in family houses = disputes
            if is_parents and h6_lord_house in [4, 9, 10]:
                dispute_score += 20
                analysis["dispute_factors"].append(
                    f"6th lord in house {h6_lord_house} - disputes with parents indicated"
                )
            if is_siblings and h6_lord_house in [3, 11]:
                dispute_score += 20
                analysis["dispute_factors"].append(
                    f"6th lord in house {h6_lord_house} - disputes with siblings indicated"
                )

        # ═══════════════════════════════════════════════════════════
        # MARS (Conflict Karaka)
        # ═══════════════════════════════════════════════════════════
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            
            if is_parents and mars_house in [4, 9]:
                dispute_score += 15
                analysis["dispute_factors"].append(
                    f"Mars in house {mars_house} - aggressive energy in parental relations"
                )
            if is_siblings and mars_house in [3, 11]:
                # Mars in 3rd can be good for siblings but also conflicts
                if mars_house == 3:
                    analysis["advice"].append(
                        "Mars in 3rd - passion in sibling bonds, channel positively"
                    )

        # Mars aspects on relevant houses
        if is_parents:
            h4_aspects = house_aspects_info.get(4, {})
            h9_aspects = house_aspects_info.get(9, {})
            if "Mars" in h4_aspects.get("malefic_aspects", []):
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "Mars aspects 4th - conflicts with mother possible"
                )
            if "Mars" in h9_aspects.get("malefic_aspects", []):
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "Mars aspects 9th - conflicts with father possible"
                )

        if is_siblings:
            h3_aspects = house_aspects_info.get(3, {})
            if "Mars" in h3_aspects.get("malefic_aspects", []):
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "Mars aspects 3rd - sibling conflicts possible"
                )

        # ═══════════════════════════════════════════════════════════
        # RAHU (Misunderstandings, Unusual Issues)
        # ═══════════════════════════════════════════════════════════
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if is_parents and rahu_house in [4, 9]:
                dispute_score += 12
                analysis["dispute_factors"].append(
                    f"Rahu in house {rahu_house} - misunderstandings with parents"
                )
            if is_siblings and rahu_house in [3, 11]:
                dispute_score += 12
                analysis["dispute_factors"].append(
                    f"Rahu in house {rahu_house} - confusion in sibling relations"
                )

        # ═══════════════════════════════════════════════════════════
        # 8th HOUSE (Hidden Tensions)
        # ═══════════════════════════════════════════════════════════
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            if is_parents and h8_lord_house in [4, 9]:
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "8th lord affecting parental houses - hidden family tensions"
                )
            if is_siblings and h8_lord_house in [3, 11]:
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "8th lord affecting sibling houses - inheritance or hidden issues"
                )

        # ═══════════════════════════════════════════════════════════
        # RESOLUTION FACTORS
        # ═══════════════════════════════════════════════════════════
        
        # Jupiter aspects (harmony)
        if is_parents:
            h4_aspects = house_aspects_info.get(4, {})
            h9_aspects = house_aspects_info.get(9, {})
            if "Jupiter" in h4_aspects.get("benefic_aspects", []):
                dispute_score -= 10
                analysis["resolution_factors"].append(
                    "Jupiter aspects 4th - wisdom prevails in maternal relations"
                )
            if "Jupiter" in h9_aspects.get("benefic_aspects", []):
                dispute_score -= 10
                analysis["resolution_factors"].append(
                    "Jupiter aspects 9th - dharma guides paternal relations"
                )

        if is_siblings:
            h3_aspects = house_aspects_info.get(3, {})
            h11_aspects = house_aspects_info.get(11, {})
            if "Jupiter" in h3_aspects.get("benefic_aspects", []):
                dispute_score -= 10
                analysis["resolution_factors"].append(
                    "Jupiter aspects 3rd - blessings protect sibling bonds"
                )
            if "Jupiter" in h11_aspects.get("benefic_aspects", []):
                dispute_score -= 10
                analysis["resolution_factors"].append(
                    "Jupiter aspects 11th - elder sibling support available"
                )

        # Venus (Harmony, Love)
        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_house = venus_data.get("house")
            if venus_house in [2, 4]:
                dispute_score -= 8
                analysis["resolution_factors"].append(
                    "Venus in family houses - love and harmony in family"
                )

        # Determine dispute potential
        dispute_score = max(0, min(100, dispute_score))
        analysis["dispute_score"] = dispute_score

        if dispute_score >= 60:
            analysis["dispute_potential"] = "HIGH"
            analysis["advice"].append("Active effort needed to maintain harmony")
        elif dispute_score >= 40:
            analysis["dispute_potential"] = "MODERATE"
            analysis["advice"].append("Some differences may arise, handle with patience")
        else:
            analysis["dispute_potential"] = "LOW"
            analysis["advice"].append("Generally harmonious, minor issues easily resolved")

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

            lord_name = (
                h.get("sign_lord") or h.get("rashi_lord") or h.get("lord") or ""
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

            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""

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
        """Extract aspects on relevant houses."""
        house_aspects = {}

        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu"}

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

        degree = planet_data.get("full_degree") or planet_data.get("degree") or 15
        if degree < 5 or degree > 25:
            score -= 10

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int, is_parents: bool, is_siblings: bool) -> str:
        """Get house meaning based on context."""
        if is_parents:
            meanings = {
                1: "Self", 2: "Family", 4: "Mother", 6: "Disputes",
                8: "Hidden Issues", 9: "Father", 10: "Responsibilities", 12: "Separation"
            }
        elif is_siblings:
            meanings = {
                1: "Self", 2: "Family", 3: "Younger Siblings", 6: "Disputes",
                8: "Hidden Issues", 11: "Elder Siblings", 12: "Distance"
            }
        else:
            meanings = {
                1: "Self", 2: "Family", 3: "Younger Siblings", 4: "Mother",
                6: "Disputes", 8: "Hidden", 9: "Father", 11: "Elder Siblings", 12: "Separation"
            }
        return meanings.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD ANALYSIS POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        relationship_analysis: dict,
        dispute_analysis: dict,
        is_parents: bool,
        is_siblings: bool
    ):
        """Add analysis points to result."""
        
        # Relationship quality
        result.add_point(
            f"💫 Relationship Quality: {relationship_analysis.get('relationship_quality')} "
            f"({relationship_analysis.get('harmony_score')}/100)"
        )

        # Specific relationships
        if is_parents:
            result.add_point(f"👩 Mother: {relationship_analysis.get('mother_relationship', 'MODERATE')}")
            result.add_point(f"👨 Father: {relationship_analysis.get('father_relationship', 'MODERATE')}")
            if relationship_analysis.get("elder_care_indicated"):
                result.add_point("🏠 Elder care responsibilities indicated")
        
        if is_siblings:
            result.add_point(f"👦 Younger Siblings: {relationship_analysis.get('younger_siblings', 'MODERATE')}")
            result.add_point(f"👧 Elder Siblings: {relationship_analysis.get('elder_siblings', 'MODERATE')}")
            if relationship_analysis.get("sibling_support"):
                result.add_point("🤝 Sibling support available")

        # Dispute potential
        result.add_point(
            f"⚡ Dispute Potential: {dispute_analysis.get('dispute_potential')} "
            f"({dispute_analysis.get('dispute_score')}/100)"
        )

        # Key factors
        for factor in relationship_analysis.get("favorable_factors", [])[:3]:
            result.add_point(f"✅ {factor}")
        for factor in relationship_analysis.get("challenging_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        for factor in dispute_analysis.get("dispute_factors", [])[:2]:
            result.add_point(f"🔥 {factor}")

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
        relationship_analysis: dict,
        dispute_analysis: dict,
        is_parents: bool,
        is_siblings: bool
    ):
        """Store data for LLM consumption."""

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },
            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,
            f"{DOMAIN_PREFIX}_relationship_analysis": relationship_analysis,
            f"{DOMAIN_PREFIX}_dispute_analysis": dispute_analysis,
            f"{DOMAIN_PREFIX}_query_context": {
                "is_parents_query": is_parents,
                "is_siblings_query": is_siblings
            },
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "relationship_quality": relationship_analysis.get("relationship_quality", "MODERATE"),
                "harmony_score": relationship_analysis.get("harmony_score", 50),
                "dispute_potential": dispute_analysis.get("dispute_potential", "LOW"),
                "dispute_score": dispute_analysis.get("dispute_score", 30),
                "mother_relationship": relationship_analysis.get("mother_relationship") if is_parents else None,
                "father_relationship": relationship_analysis.get("father_relationship") if is_parents else None,
                "younger_siblings": relationship_analysis.get("younger_siblings") if is_siblings else None,
                "elder_siblings": relationship_analysis.get("elder_siblings") if is_siblings else None,
                "elder_care_indicated": relationship_analysis.get("elder_care_indicated", False),
                "sibling_support": relationship_analysis.get("sibling_support", False),
            },
        })

        logger.info(
            f"📦 STORED | quality={relationship_analysis.get('relationship_quality')} | "
            f"disputes={dispute_analysis.get('dispute_potential')} | "
            f"parents={is_parents} | siblings={is_siblings}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="PARENTS_RELATIONSHIP",
                question=(
                    "What does astrology reveal about harmony with my parents, "
                    "the chances of disputes and responsibilities related to elder care?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Relationship with Parents"
            ),
            Question(
                id="SIBLINGS_RELATIONSHIP",
                question=(
                    "What does astrology reveal about harmony with my siblings "
                    "and the potential for disputes?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Relationship with Siblings"
            )
        ]
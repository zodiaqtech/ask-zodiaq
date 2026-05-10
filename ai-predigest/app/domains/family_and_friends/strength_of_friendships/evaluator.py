"""
Friendship Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for analyzing friendship compatibility, strength,
longevity, and potential issues using Vedic astrology principles.

✔ Simple and straightforward structure
✔ Focus on friendship compatibility, strength, disputes
✔ Full house lords extraction with dignity and strength
✔ NO KP analysis (Vedic-only domain)
✔ Complete data storage for LLM

Key Houses:
- 11th: Friends, social circle, gains through friends, elder siblings (PRIMARY)
- 3rd: Communication, courage, social interactions
- 5th: Recreation, enjoyment with friends, creative connections
- 7th: Partnerships, one-on-one relationships

Supporting Houses:
- 1st: Self, native's personality in friendships
- 6th: Disputes, conflicts, enemies (friends turning foes)
- 8th: Betrayal, hidden issues, sudden breaks
- 12th: Losses, secret enemies, isolation

Karakas:
- Jupiter: Wisdom, true friends, blessings, good company
- Mercury: Communication, intellectual connections, casual friends
- Venus: Social harmony, enjoyment, pleasant friendships
- Saturn: Long-lasting friendships, older friends, karmic connections
- Mars: Competition, conflicts with friends
- Rahu: Unconventional friends, deception, fair-weather friends
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

DOMAIN_PREFIX = "friendship"


class StrengthOfFriendshipsEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Family and Friends → Strength of Friendship
    
    Focuses on:
    - Friendship compatibility
    - Strength and longevity of friendships
    - Disputes, quarrels, betrayal potential
    - Why friends may be distant and how to improve
    """

    domain = "Family_And_Friends"
    subtopic = "Strength Of Friendships"

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

        # Set houses for friendship analysis
        primary_houses = {11, 3, 5}
        secondary_houses = {1, 6, 7, 8, 12}
        all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 60)
        logger.info("FRIENDSHIP EVALUATOR (VEDIC-ONLY v1.0)")
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

        # Friendship Strength Analysis
        strength_analysis = self._analyze_friendship_strength(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Compatibility Analysis
        compatibility_analysis = self._analyze_compatibility(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Dispute/Betrayal Analysis
        dispute_analysis = self._analyze_disputes_betrayal(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Add Points
        self._add_analysis_points(
            result,
            house_lords_info,
            strength_analysis,
            compatibility_analysis,
            dispute_analysis
        )

        # Store Data for LLM
        self._store_data_for_llm(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            strength_analysis,
            compatibility_analysis,
            dispute_analysis
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # FRIENDSHIP STRENGTH ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_friendship_strength(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze strength and longevity of friendships."""
        analysis = {
            "friendship_strength": "MODERATE",
            "strength_score": 50,
            "longevity": "MODERATE",
            "favorable_factors": [],
            "challenging_factors": [],
            "improvement_tips": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 11th HOUSE - Friends, Social Circle (PRIMARY)
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
                    f"Strong 11th lord supports stable and beneficial friendships"
                )
                analysis["longevity"] = "LONG-LASTING"
            elif h11_strength < 40:
                score -= 12
                analysis["challenging_factors"].append(
                    f"11th lord {h11_lord} is weak - friendships need nurturing"
                )
                analysis["improvement_tips"].append(
                    "Strengthen 11th lord through remedies"
                )

            # 11th lord placement
            if h11_lord_house in [1, 5, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"11th lord in house {h11_lord_house} - friends bring gains and happiness"
                )
            elif h11_lord_house == 6:
                score -= 10
                analysis["challenging_factors"].append(
                    "11th lord in 6th - friends may become rivals or cause disputes"
                )
            elif h11_lord_house == 8:
                score -= 8
                analysis["challenging_factors"].append(
                    "11th lord in 8th - sudden breaks or hidden issues with friends"
                )
            elif h11_lord_house == 12:
                score -= 8
                analysis["challenging_factors"].append(
                    "11th lord in 12th - friends may be distant or losses through friends"
                )
                analysis["improvement_tips"].append(
                    "Be selective about who you trust"
                )

        # Benefics on 11th
        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 11th - blessed with wise and supportive friends"
            )
            analysis["longevity"] = "LONG-LASTING"
        if "Venus" in h11_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Venus aspects 11th - enjoyable and harmonious friendships"
            )
        if "Mercury" in h11_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Mercury aspects 11th - intellectual and communicative friends"
            )

        # Malefics on 11th
        if "Saturn" in h11_aspects.get("malefic_aspects", []):
            score -= 3  # Saturn can give long-lasting but few friends
            analysis["favorable_factors"].append(
                "Saturn aspects 11th - few but loyal, long-term friends"
            )
        if "Mars" in h11_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["challenging_factors"].append(
                "Mars aspects 11th - conflicts or competition with friends"
            )
        if "Rahu" in h11_aspects.get("malefic_aspects", []):
            score -= 8
            analysis["challenging_factors"].append(
                "Rahu aspects 11th - unconventional friends, possible deception"
            )

        # ═══════════════════════════════════════════════════════════
        # 3rd HOUSE - Communication, Social Interactions
        # ═══════════════════════════════════════════════════════════
        h3_info = house_lords_info.get(3, {})
        if h3_info:
            h3_strength = h3_info.get("lord_strength_score", 50)
            if h3_strength >= 70:
                score += 8
                analysis["favorable_factors"].append(
                    "3rd lord strong - good communication skills help friendships"
                )
            elif h3_strength < 40:
                score -= 5
                analysis["challenging_factors"].append(
                    "3rd lord weak - communication issues may affect friendships"
                )
                analysis["improvement_tips"].append(
                    "Work on communication and staying in touch"
                )

        # ═══════════════════════════════════════════════════════════
        # 5th HOUSE - Recreation, Enjoyment with Friends
        # ═══════════════════════════════════════════════════════════
        h5_info = house_lords_info.get(5, {})
        if h5_info:
            h5_strength = h5_info.get("lord_strength_score", 50)
            if h5_strength >= 70:
                score += 5
                analysis["favorable_factors"].append(
                    "5th lord strong - fun and enjoyable friendships"
                )

        # ═══════════════════════════════════════════════════════════
        # KEY PLANETS
        # ═══════════════════════════════════════════════════════════
        
        # Jupiter - True Friends
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house == 11:
                score += 12
                analysis["favorable_factors"].append(
                    "Jupiter influencing the 11th house supports wise and genuine friendships"
                )
            elif jupiter_house in [1, 5, 9]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - attracts good company"
                )

        # Venus - Social Harmony
        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_house = venus_data.get("house")
            if venus_house == 11:
                score += 10
                analysis["favorable_factors"].append(
                    "Venus in 11th - charming personality attracts friends"
                )
            elif venus_house in [1, 3, 5, 7]:
                score += 5
                analysis["favorable_factors"].append(
                    "Venus well-placed - likeable and popular"
                )

        # Mercury - Communication
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            if mercury_house in [1, 3, 5, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Mercury in house {mercury_house} - good at maintaining friendships"
                )

        # Saturn - Longevity (can be positive)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house == 11:
                analysis["longevity"] = "LONG-LASTING"
                analysis["favorable_factors"].append(
                    "Saturn in 11th - few but enduring, loyal friendships"
                )

        # Determine strength level
        score = max(0, min(100, score))
        analysis["strength_score"] = score

        if score >= 70:
            analysis["friendship_strength"] = "STRONG"
        elif score >= 55:
            analysis["friendship_strength"] = "GOOD"
        elif score >= 40:
            analysis["friendship_strength"] = "MODERATE"
        elif score >= 25:
            analysis["friendship_strength"] = "WEAK"
        else:
            analysis["friendship_strength"] = "CHALLENGING"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # COMPATIBILITY ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_compatibility(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze friendship compatibility factors."""
        analysis = {
            "compatibility_level": "MODERATE",
            "compatibility_score": 50,
            "compatible_traits": [],
            "challenging_traits": [],
            "best_friend_types": []
        }

        score = 50

        # ═══════════════════════════════════════════════════════════
        # 7th HOUSE - One-on-One Relationships
        # ═══════════════════════════════════════════════════════════
        h7_info = house_lords_info.get(7, {})
        h7_aspects = house_aspects_info.get(7, {})
        
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            h7_lord = h7_info.get("lord", "")
            
            if h7_strength >= 70:
                score += 10
                analysis["compatible_traits"].append(
                    "Good at one-on-one connections"
                )
            elif h7_strength < 40:
                score -= 8
                analysis["challenging_traits"].append(
                    "May struggle with close personal bonds"
                )

        # ═══════════════════════════════════════════════════════════
        # 1st HOUSE - Self, Personality
        # ═══════════════════════════════════════════════════════════
        h1_info = house_lords_info.get(1, {})
        h1_aspects = house_aspects_info.get(1, {})
        
        if h1_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            if h1_strength >= 70:
                score += 8
                analysis["compatible_traits"].append(
                    "Strong personality attracts friends"
                )

        # Benefics on 1st - likeable
        if "Jupiter" in h1_aspects.get("benefic_aspects", []):
            analysis["compatible_traits"].append(
                "Approaches friendships with wisdom, fairness, and trust"
            )

        if "Venus" in h1_aspects.get("benefic_aspects", []):
            analysis["compatible_traits"].append(
                "Naturally warm, pleasant, and socially engaging in friendships"
            )

            analysis["best_friend_types"].append("Artistic, fun-loving people")

        # ═══════════════════════════════════════════════════════════
        # MOON - Emotional Compatibility
        # ═══════════════════════════════════════════════════════════
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_house = moon_data.get("house")

            if moon_house in [3, 11]:
                analysis["compatible_traits"].append(
                    "Emotionally communicative and responsive in friendships"
                )
            elif moon_house in [4, 5]:
                analysis["compatible_traits"].append(
                    "Warm, caring, and emotionally supportive friend"
                )
            elif moon_house in [6, 8, 12]:
                analysis["challenging_traits"].append(
                    "May withdraw emotionally at times or feel misunderstood"
                )


        # ═══════════════════════════════════════════════════════════
        # 11th LORD SIGN - Type of Friends Attracted
        # ═══════════════════════════════════════════════════════════
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_lord = h11_info.get("lord", "")
            if h11_lord == "Jupiter":
                analysis["compatible_traits"].append(
                    "Values honesty, wisdom, and meaningful friendships"
                )
            elif h11_lord == "Venus":
                analysis["compatible_traits"].append(
                    "Enjoys pleasant, harmonious, and socially engaging friendships"
                )
            elif h11_lord == "Mercury":
                analysis["compatible_traits"].append(
                    "Prefers communicative and intellectually stimulating friendships"
                )
            elif h11_lord == "Mars":
                analysis["challenging_traits"].append(
                    "May experience competition or strong opinions in friendships"
                )
            elif h11_lord == "Saturn":
                analysis["compatible_traits"].append(
                    "Forms fewer but long-lasting and dependable friendships"
                )
            elif h11_lord == "Moon":
                analysis["compatible_traits"].append(
                    "Emotionally bonded and caring in friendships"
                )
            elif h11_lord == "Sun":
                analysis["compatible_traits"].append(
                    "Values respect and loyalty in friendships"
                )

        # Determine compatibility level
        score = max(0, min(100, score))
        analysis["compatibility_score"] = score

        if score >= 70:
            analysis["compatibility_level"] = "HIGH"
        elif score >= 55:
            analysis["compatibility_level"] = "GOOD"
        elif score >= 40:
            analysis["compatibility_level"] = "MODERATE"
        else:
            analysis["compatibility_level"] = "NEEDS_WORK"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DISPUTES & BETRAYAL ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_disputes_betrayal(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze potential for disputes, quarrels, or betrayal."""
        analysis = {
            "dispute_potential": "LOW",
            "dispute_score": 30,
            "betrayal_risk": "LOW",
            "dispute_factors": [],
            "protection_factors": [],
            "advice": []
        }

        dispute_score = 30  # Start optimistic
        betrayal_score = 20

        # ═══════════════════════════════════════════════════════════
        # 6th HOUSE - Disputes, Enemies
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            
            # 6th lord in friendship houses = disputes with friends
            if h6_lord_house == 11:
                dispute_score += 20
                analysis["dispute_factors"].append(
                    "6th lord in 11th - friends may become enemies or rivals"
                )
                analysis["advice"].append("Be cautious about mixing money with friendship")
            elif h6_lord_house == 3:
                dispute_score += 12
                analysis["dispute_factors"].append(
                    "6th lord in 3rd - quarrels in social circle"
                )
            elif h6_lord_house == 5:
                dispute_score += 10
                analysis["dispute_factors"].append(
                    "6th lord in 5th - conflicts during recreational activities"
                )

        # ═══════════════════════════════════════════════════════════
        # 8th HOUSE - Betrayal, Hidden Issues
        # ═══════════════════════════════════════════════════════════
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            
            if h8_lord_house == 11:
                betrayal_score += 20
                analysis["dispute_factors"].append(
                    "8th lord in 11th - trust issues or lack of transparency in friendships"
                )
                analysis["advice"].append("Don't share secrets too easily")
            elif h8_lord_house == 3:
                betrayal_score += 10
                analysis["dispute_factors"].append(
                    "8th lord in 3rd - miscommunication leading to breaks"
                )

        # ═══════════════════════════════════════════════════════════
        # 12th HOUSE - Losses, Secret Enemies
        # ═══════════════════════════════════════════════════════════
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_lord_house = h12_info.get("lord_in_house")
            
            if h12_lord_house == 11:
                dispute_score += 15
                betrayal_score += 15
                analysis["dispute_factors"].append(
                    "12th lord in 11th - losses through friends, conflicting interests within the social circle"
                )
                analysis["advice"].append("Be selective about close friendships")

        # ═══════════════════════════════════════════════════════════
        # MALEFIC PLANETS
        # ═══════════════════════════════════════════════════════════
        
        # Mars in/aspecting 11th - Conflicts
        mars_data = planets.get("Mars", {})
        h11_aspects = house_aspects_info.get(11, {})
        
        if mars_data and mars_data.get("house") == 11:
            dispute_score += 15
            analysis["dispute_factors"].append(
                "Mars in 11th - aggressive competition or arguments with friends"
            )
        elif "Mars" in h11_aspects.get("malefic_aspects", []):
            dispute_score += 10
            analysis["dispute_factors"].append(
                "Mars aspects 11th - heated disagreements possible"
            )

        # Rahu in/aspecting 11th - Deception
        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") == 11:
            betrayal_score += 20
            analysis["dispute_factors"].append(
                "Rahu in 11th - unconventional friends, risk of misunderstandings or unclear intentions"
            )
            analysis["advice"].append("Beware of fair-weather friends")
        elif "Rahu" in h11_aspects.get("malefic_aspects", []):
            betrayal_score += 12
            analysis["dispute_factors"].append(
                "Rahu aspects 11th - illusions about friendships"
            )

        # Ketu in 11th - Detachment
        ketu_data = planets.get("Ketu", {})
        if ketu_data and ketu_data.get("house") == 11:
            analysis["dispute_factors"].append(
                "Ketu in 11th - detachment or disinterest in friendships"
            )
            analysis["advice"].append("Make conscious effort to stay connected")

        # Saturn afflicting - Coldness, Distance
        saturn_data = planets.get("Saturn", {})
        if "Saturn" in h11_aspects.get("malefic_aspects", []):
            analysis["favorable_factors"].append(
                "Saturn influence brings fewer but loyal and long-term friendships"
            )


        # ═══════════════════════════════════════════════════════════
        # PROTECTION FACTORS
        # ═══════════════════════════════════════════════════════════
        
        # Jupiter protects
        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            dispute_score -= 10
            betrayal_score -= 10
            analysis["protection_factors"].append(
                "Jupiter's grace protects friendships"
            )

        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data and jupiter_data.get("house") == 11:
            dispute_score -= 12
            betrayal_score -= 12
            analysis["protection_factors"].append(
                "Jupiter in 11th - genuine, trustworthy friends"
            )

        # Venus brings harmony
        if "Venus" in h11_aspects.get("benefic_aspects", []):
            dispute_score -= 8
            analysis["protection_factors"].append(
                "Venus maintains harmony in friendships"
            )

        # Strong 11th lord protects
        h11_info = house_lords_info.get(11, {})
        if h11_info and h11_info.get("lord_strength_score", 50) >= 70:
            dispute_score -= 8
            analysis["protection_factors"].append(
                "Strong 11th lord protects friend circle"
            )

        # Determine dispute potential
        dispute_score = max(0, min(100, dispute_score))
        betrayal_score = max(0, min(100, betrayal_score))
        
        analysis["dispute_score"] = dispute_score

        if dispute_score >= 50:
            analysis["dispute_potential"] = "HIGH"
        elif dispute_score >= 35:
            analysis["dispute_potential"] = "MODERATE"
        else:
            analysis["dispute_potential"] = "LOW"

        if betrayal_score >= 40:
            analysis["betrayal_risk"] = "HIGH"
            analysis["advice"].append("Trust must be earned over time")
        elif betrayal_score >= 25:
            analysis["betrayal_risk"] = "MODERATE"
        else:
            analysis["betrayal_risk"] = "LOW"

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
        strength_analysis: dict,
        compatibility_analysis: dict,
        dispute_analysis: dict
    ):
        """Add analysis points to result."""
        
        # Strength
        result.add_point(
            f"🤝 Friendship Strength: {strength_analysis.get('friendship_strength')} "
            f"({strength_analysis.get('strength_score')}/100)"
        )

        # Longevity
        result.add_point(
            f"⏳ Longevity: {strength_analysis.get('longevity')}"
        )

        # Compatibility
        result.add_point(
            f"💫 Compatibility: {compatibility_analysis.get('compatibility_level')} "
            f"({compatibility_analysis.get('compatibility_score')}/100)"
        )

        # Disputes
        result.add_point(
            f"⚡ Dispute Potential: {dispute_analysis.get('dispute_potential')} "
            f"({dispute_analysis.get('dispute_score')}/100)"
        )

        # Betrayal risk
        if dispute_analysis.get("betrayal_risk") in ["MODERATE", "HIGH"]:
            result.add_point(
                f"⚠️ Betrayal Risk: {dispute_analysis.get('betrayal_risk')}"
            )

        # Key factors
        for factor in strength_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in dispute_analysis.get("dispute_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        
        # Best friend types
        friend_types = compatibility_analysis.get("best_friend_types", [])
        if friend_types and len(friend_types) <= 2:
            result.add_point(
                f"👥 Friendship tendencies align with: {', '.join(friend_types)}"
            )


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
        strength_analysis: dict,
        compatibility_analysis: dict,
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
            f"{DOMAIN_PREFIX}_strength_analysis": strength_analysis,
            f"{DOMAIN_PREFIX}_compatibility_analysis": compatibility_analysis,
            f"{DOMAIN_PREFIX}_dispute_analysis": dispute_analysis,
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "friendship_strength": strength_analysis.get("friendship_strength", "MODERATE"),
                "strength_score": strength_analysis.get("strength_score", 50),
                "longevity": strength_analysis.get("longevity", "MODERATE"),
                "compatibility_level": compatibility_analysis.get("compatibility_level", "MODERATE"),
                "compatibility_score": compatibility_analysis.get("compatibility_score", 50),
                "dispute_potential": dispute_analysis.get("dispute_potential", "LOW"),
                "dispute_score": dispute_analysis.get("dispute_score", 30),
                "betrayal_risk": dispute_analysis.get("betrayal_risk", "LOW"),
                "best_friend_types": compatibility_analysis.get("best_friend_types", []),
            },
        })

        logger.info(
            f"📦 STORED | strength={strength_analysis.get('friendship_strength')} | "
            f"compatibility={compatibility_analysis.get('compatibility_level')} | "
            f"disputes={dispute_analysis.get('dispute_potential')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="FRIENDSHIP_COMPATIBILITY",
                question=(
                    "What does astrology reveal about my friendship compatibility, "
                    "the strength and longevity of my friendships and the chances "
                    "of disputes, quarrels, or betrayal?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Friendship Compatibility"
            ),
            Question(
                id="FRIENDSHIP_IMPROVEMENT",
                question=(
                    "Why might my friends be ignoring me and how can I improve "
                    "these relationships?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Friendship Compatibility"
            )
        ]
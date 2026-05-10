"""
House Lords Analyzer for Vedic Astrology

Provides comprehensive analysis of house lords including:
- Placement (which house the lord occupies)
- Condition (dignity, combustion, retrograde, aspects)
- Cross-references (connections between houses)
- Domain-specific analysis

Priority Order (Classical Vedic):
1. House Lord Placement
2. House Lord Condition
3. Planets in House
4. Aspects on House

Author: MyZodiaq
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class LordDignity(Enum):
    """Dignity states for planets"""
    EXALTED = "exalted"
    MOOLATRIKONA = "moolatrikona"
    OWN_SIGN = "own_sign"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    DEBILITATED = "debilitated"


@dataclass
class HouseLordAnalysis:
    """Analysis result for a single house lord"""
    house_num: int
    cusp_sign: str
    lord_name: str
    lord_house: int
    lord_sign: str
    lord_degree: float
    lord_nakshatra: str = ""
    lord_nakshatra_lord: str = ""
    dignity: LordDignity = LordDignity.NEUTRAL
    is_retrograde: bool = False
    is_combust: bool = False
    benefic_aspects: List[str] = field(default_factory=list)
    malefic_aspects: List[str] = field(default_factory=list)
    strength_score: float = 5.0  # 0-10 scale
    is_afflicted: bool = False
    
    def format_placement(self, language: str = "English") -> str:
        """Format placement as readable string"""
        if language == "Hindi":
            return (f"{self.house_num}वें भाव का स्वामी ({self.lord_name}) "
                   f"{self.lord_house}वें भाव में {self.lord_sign} राशि में {self.lord_degree:.1f}° पर")
        return (f"{self.house_num}th Lord ({self.lord_name}) in House {self.lord_house} "
               f"in {self.lord_sign} at {self.lord_degree:.1f}°")
    
    def format_condition(self, language: str = "English") -> str:
        """Format condition as readable string"""
        parts = []
        
        # Dignity
        dignity_text = {
            LordDignity.EXALTED: "Exalted (उच्च)" if language == "Hindi" else "Exalted",
            LordDignity.DEBILITATED: "Debilitated (नीच)" if language == "Hindi" else "Debilitated",
            LordDignity.OWN_SIGN: "Own Sign (स्वराशि)" if language == "Hindi" else "Own Sign",
            LordDignity.MOOLATRIKONA: "Moolatrikona (मूलत्रिकोण)" if language == "Hindi" else "Moolatrikona",
            LordDignity.FRIENDLY: "Friendly Sign (मित्र राशि)" if language == "Hindi" else "Friendly Sign",
            LordDignity.ENEMY: "Enemy Sign (शत्रु राशि)" if language == "Hindi" else "Enemy Sign",
            LordDignity.NEUTRAL: "Neutral (सम)" if language == "Hindi" else "Neutral"
        }
        parts.append(dignity_text.get(self.dignity, "Neutral"))
        
        # Afflictions
        if self.is_combust:
            parts.append("Combust (अस्त)" if language == "Hindi" else "Combust")
        if self.is_retrograde:
            parts.append("Retrograde (वक्री)" if language == "Hindi" else "Retrograde")
        
        return " | ".join(parts)
    
    def format_full(self, language: str = "English") -> str:
        """Format complete analysis"""
        lines = [
            self.format_placement(language),
            f"   Condition: {self.format_condition(language)}",
            f"   Strength: {self.strength_score:.1f}/10"
        ]
        
        if self.benefic_aspects:
            label = "शुभ दृष्टि" if language == "Hindi" else "Benefic aspects"
            lines.append(f"   {label}: {', '.join(self.benefic_aspects)}")
        
        if self.malefic_aspects:
            label = "पाप दृष्टि" if language == "Hindi" else "Malefic aspects"
            lines.append(f"   {label}: {', '.join(self.malefic_aspects)}")
        
        return "\n".join(lines)


@dataclass
class DomainAnalysis:
    """Complete analysis for a domain (Marriage, Career, etc.)"""
    domain: str
    primary_lords: List[HouseLordAnalysis] = field(default_factory=list)
    secondary_lords: List[HouseLordAnalysis] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    house_occupancy: Dict[int, List[str]] = field(default_factory=dict)
    house_aspects: Dict[int, Dict[str, List[str]]] = field(default_factory=dict)
    karaka_analysis: Dict[str, Any] = field(default_factory=dict)
    overall_strength: float = 5.0
    formatted_output: str = ""


# =============================================================================
# CONSTANTS
# =============================================================================

# Sign lordships (Vedic)
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Exaltation signs
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
}

# Debilitation signs
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"
}

# Own signs
OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
    "Rahu": set(),
    "Ketu": set()
}

# Moolatrikona (sign and degree range)
MOOLATRIKONA = {
    "Sun": {"sign": "Leo", "start": 0, "end": 20},
    "Moon": {"sign": "Taurus", "start": 3, "end": 30},
    "Mars": {"sign": "Aries", "start": 0, "end": 12},
    "Mercury": {"sign": "Virgo", "start": 15, "end": 20},
    "Jupiter": {"sign": "Sagittarius", "start": 0, "end": 10},
    "Venus": {"sign": "Libra", "start": 0, "end": 15},
    "Saturn": {"sign": "Aquarius", "start": 0, "end": 20}
}

# Planet friendships
PLANET_FRIENDSHIPS = {
    "Sun": {"friends": {"Moon", "Mars", "Jupiter"}, "enemies": {"Venus", "Saturn"}, "neutral": {"Mercury"}},
    "Moon": {"friends": {"Sun", "Mercury"}, "enemies": set(), "neutral": {"Mars", "Jupiter", "Venus", "Saturn"}},
    "Mars": {"friends": {"Sun", "Moon", "Jupiter"}, "enemies": {"Mercury"}, "neutral": {"Venus", "Saturn"}},
    "Mercury": {"friends": {"Sun", "Venus"}, "enemies": {"Moon"}, "neutral": {"Mars", "Jupiter", "Saturn"}},
    "Jupiter": {"friends": {"Sun", "Moon", "Mars"}, "enemies": {"Mercury", "Venus"}, "neutral": {"Saturn"}},
    "Venus": {"friends": {"Mercury", "Saturn"}, "enemies": {"Sun", "Moon"}, "neutral": {"Mars", "Jupiter"}},
    "Saturn": {"friends": {"Mercury", "Venus"}, "enemies": {"Sun", "Moon", "Mars"}, "neutral": {"Jupiter"}},
    "Rahu": {"friends": {"Venus", "Saturn"}, "enemies": {"Sun", "Moon", "Mars"}, "neutral": {"Mercury", "Jupiter"}},
    "Ketu": {"friends": {"Mars", "Jupiter"}, "enemies": {"Moon", "Venus"}, "neutral": {"Sun", "Mercury", "Saturn"}}
}

# Combustion orbs (degrees from Sun)
COMBUSTION_ORB = {
    "Moon": 12, "Mars": 17, "Mercury": 14,
    "Jupiter": 11, "Venus": 10, "Saturn": 15
}

# Benefic and Malefic planets
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

# Domain house configurations
DOMAIN_HOUSES = {
    "Marriage": {
        "primary": {7, 2, 11},
        "secondary": {5, 8},
        "karaka": "Venus",
        "description_en": "Marriage & Partnership",
        "description_hi": "विवाह"
    },
    "Career": {
        "primary": {10, 6, 2},
        "secondary": {11, 9},
        "karaka": "Saturn",
        "description_en": "Career & Profession",
        "description_hi": "करियर"
    },
    "Finance": {
        "primary": {2, 11, 5},
        "secondary": {8, 12},
        "karaka": "Jupiter",
        "description_en": "Finance & Wealth",
        "description_hi": "वित्त"
    },
    "Health": {
        "primary": {1, 6, 8},
        "secondary": {12},
        "karaka": "Sun",
        "description_en": "Health & Vitality",
        "description_hi": "स्वास्थ्य"
    },
    "Children": {
        "primary": {5, 9, 11},
        "secondary": {2},
        "karaka": "Jupiter",
        "description_en": "Children & Progeny",
        "description_hi": "संतान"
    },
    "Foreign": {
        "primary": {9, 12, 3},
        "secondary": {4, 7},
        "karaka": "Rahu",
        "description_en": "Foreign & Travel",
        "description_hi": "विदेश"
    },
    "Business": {
        "primary": {7, 10, 3},
        "secondary": {11, 5},
        "karaka": "Mercury",
        "description_en": "Business & Commerce",
        "description_hi": "व्यापार"
    },
    "Education": {
        "primary": {4, 5, 9},
        "secondary": {2, 11},
        "karaka": "Jupiter",
        "description_en": "Education & Learning",
        "description_hi": "शिक्षा"
    },
    "Lost_Missing": {
        "primary": {2, 4, 7, 11},
        "secondary": {6, 8, 12},
        "karaka": "Moon",
        "description_en": "Lost Items & Missing Persons",
        "description_hi": "खोई वस्तु / गुमशुदा व्यक्ति"
    }

}

# Hindi planet names
HINDI_PLANETS = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु"
}

# Hindi sign names
HINDI_SIGNS = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन",
    "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
    "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
    "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}


# =============================================================================
# MAIN ANALYZER CLASS
# =============================================================================

class HouseLordsAnalyzer:
    """
    Comprehensive house lords analyzer for Vedic astrology.
    
    Analyzes house lords with proper Vedic priority:
    1. Lord Placement (which house)
    2. Lord Condition (dignity, afflictions)
    3. House Occupancy (planets in house)
    4. Aspects on House
    """
    
    def __init__(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        aspects_data: Dict = None
    ):
        """
        Initialize analyzer with chart data.
        
        Args:
            planets: Dictionary of planet data (name -> planet dict)
            houses: List of house dictionaries
            aspects_data: Pre-calculated aspects (optional)
        """
        self.planets = planets
        self.houses = houses
        self.aspects_data = aspects_data or {}
        
        # Build lookup structures
        self._house_signs = {}
        self._house_lords = {}
        self._planet_houses = {}
        
        self._build_lookups()
    
    def _build_lookups(self):
        """Build internal lookup structures"""
        # Map house -> sign and lord
        for h in self.houses:
            house_num = h.get("house")
            if not house_num:
                continue
            
            sign = str(h.get("start_rasi") or h.get("rasi") or h.get("sign") or "").title()
            self._house_signs[house_num] = sign
            self._house_lords[house_num] = SIGN_LORDS.get(sign, "")
        
        # Map planet -> house
        for name, data in self.planets.items():
            if isinstance(data, dict):
                house = data.get("house")
                if house:
                    self._planet_houses[name] = house
    
    def _get_planet(self, name: str) -> Optional[Dict]:
        """Get planet data by name"""
        # Try exact match
        if name in self.planets:
            return self.planets[name]
        
        # Try case-insensitive
        name_lower = name.lower()
        for pname, pdata in self.planets.items():
            if pname.lower() == name_lower:
                return pdata
        
        return None
    
    def _get_dignity(self, planet_name: str, sign: str, degree: float = 0) -> LordDignity:
        """
        Determine dignity of planet in a sign.
        
        Priority:
        1. Exalted
        2. Debilitated
        3. Moolatrikona (within degree range)
        4. Own Sign
        5. Friendly
        6. Enemy
        7. Neutral
        """
        if not planet_name or not sign:
            return LordDignity.NEUTRAL
        
        sign = sign.title()
        
        # Check exaltation
        if EXALTATION.get(planet_name) == sign:
            return LordDignity.EXALTED
        
        # Check debilitation
        if DEBILITATION.get(planet_name) == sign:
            return LordDignity.DEBILITATED
        
        # Check own sign
        if sign in OWN_SIGNS.get(planet_name, set()):
            # Check moolatrikona within own sign
            mt = MOOLATRIKONA.get(planet_name)
            if mt and mt["sign"] == sign:
                if mt["start"] <= degree <= mt["end"]:
                    return LordDignity.MOOLATRIKONA
            return LordDignity.OWN_SIGN
        
        # Check friendships
        sign_lord = SIGN_LORDS.get(sign, "")
        if not sign_lord:
            return LordDignity.NEUTRAL
        
        friendships = PLANET_FRIENDSHIPS.get(planet_name, {})
        
        if sign_lord in friendships.get("friends", set()):
            return LordDignity.FRIENDLY
        if sign_lord in friendships.get("enemies", set()):
            return LordDignity.ENEMY
        
        return LordDignity.NEUTRAL
    
    def _is_combust(self, planet_name: str) -> bool:
        """Check if planet is combust"""
        if planet_name in ("Sun", "Rahu", "Ketu"):
            return False
        
        planet = self._get_planet(planet_name)
        if not planet:
            return False
        
        # Check flag first
        if planet.get("is_combusted") or planet.get("is_combust"):
            return True
        
        # Calculate from Sun position
        sun = self._get_planet("Sun")
        if not sun:
            return False
        
        planet_deg = planet.get("global_degree", 0)
        sun_deg = sun.get("global_degree", 0)
        
        diff = abs(planet_deg - sun_deg)
        if diff > 180:
            diff = 360 - diff
        
        orb = COMBUSTION_ORB.get(planet_name, 10)
        return diff <= orb
    
    def _get_aspects_on_planet(self, planet_name: str) -> Tuple[List[str], List[str]]:
        """Get benefic and malefic aspects on a planet"""
        benefic = []
        malefic = []
        
        aspecting = self.aspects_data.get("aspects_on_planet", {}).get(planet_name, [])
        
        for asp_planet in aspecting:
            if asp_planet in BENEFICS:
                benefic.append(asp_planet)
            elif asp_planet in MALEFICS:
                malefic.append(asp_planet)
        
        return benefic, malefic
    
    def _calculate_strength(self, lord: HouseLordAnalysis) -> float:
        """
        Calculate strength score (0-10) for a house lord.
        
        Factors:
        - Dignity (+5 to -3)
        - Benefic aspects (+0.5 each)
        - Malefic aspects (-0.75 each)
        - Retrograde (-1.0)
        - Combust (-1.5)
        """
        # Base score
        score = 5.0
        
        # Dignity adjustment
        dignity_scores = {
            LordDignity.EXALTED: 5,
            LordDignity.MOOLATRIKONA: 4,
            LordDignity.OWN_SIGN: 3,
            LordDignity.FRIENDLY: 1.5,
            LordDignity.NEUTRAL: 0,
            LordDignity.ENEMY: -1.5,
            LordDignity.DEBILITATED: -3
        }
        score += dignity_scores.get(lord.dignity, 0)
        
        # Aspect adjustments
        score += len(lord.benefic_aspects) * 0.5
        score -= len(lord.malefic_aspects) * 0.75
        
        # Affliction adjustments
        if lord.is_retrograde:
            score -= 1.0
        if lord.is_combust:
            score -= 1.5
        
        # Clamp to 0-10
        return max(0, min(10, score))
    
    def analyze_house_lord(self, house_num: int) -> HouseLordAnalysis:
        """
        Analyze the lord of a specific house.
        
        Args:
            house_num: House number (1-12)
        
        Returns:
            HouseLordAnalysis with complete details
        """
        cusp_sign = self._house_signs.get(house_num, "")
        lord_name = self._house_lords.get(house_num, "")
        
        if not lord_name:
            return HouseLordAnalysis(
                house_num=house_num,
                cusp_sign=cusp_sign,
                lord_name="Unknown",
                lord_house=0,
                lord_sign="",
                lord_degree=0
            )
        
        # Get lord's position
        lord_planet = self._get_planet(lord_name)
        if not lord_planet:
            return HouseLordAnalysis(
                house_num=house_num,
                cusp_sign=cusp_sign,
                lord_name=lord_name,
                lord_house=0,
                lord_sign="",
                lord_degree=0
            )
        
        lord_house = lord_planet.get("house", 0)
        lord_sign = str(lord_planet.get("sign") or lord_planet.get("rasi") or "").title()
        lord_degree = lord_planet.get("local_degree", 0)
        lord_nakshatra = lord_planet.get("nakshatra", "")
        lord_nakshatra_lord = lord_planet.get("nakshatra_lord", "")
        
        # Determine dignity
        dignity = self._get_dignity(lord_name, lord_sign, lord_degree)
        
        # Check afflictions
        is_retro = lord_planet.get("is_retro", False) or lord_planet.get("retro", False)
        is_combust = self._is_combust(lord_name)
        
        # Get aspects
        benefic_aspects, malefic_aspects = self._get_aspects_on_planet(lord_name)
        
        # Determine if afflicted
        is_afflicted = (
            dignity == LordDignity.DEBILITATED or
            is_combust or
            len(malefic_aspects) >= 2
        )
        
        analysis = HouseLordAnalysis(
            house_num=house_num,
            cusp_sign=cusp_sign,
            lord_name=lord_name,
            lord_house=lord_house,
            lord_sign=lord_sign,
            lord_degree=lord_degree,
            lord_nakshatra=lord_nakshatra,
            lord_nakshatra_lord=lord_nakshatra_lord,
            dignity=dignity,
            is_retrograde=is_retro,
            is_combust=is_combust,
            benefic_aspects=benefic_aspects,
            malefic_aspects=malefic_aspects,
            is_afflicted=is_afflicted
        )
        
        # Calculate strength
        analysis.strength_score = self._calculate_strength(analysis)
        
        return analysis
    
    def _find_cross_references(
        self,
        primary_houses: Set[int],
        secondary_houses: Set[int]
    ) -> List[str]:
        """
        Find cross-references between houses through lordship.
        
        A cross-reference occurs when:
        - Lord of house A is placed in house B (both in relevant set)
        - Lords of two houses are conjunct
        """
        refs = []
        all_houses = primary_houses | secondary_houses
        
        for h1 in all_houses:
            lord1 = self._house_lords.get(h1)
            if not lord1:
                continue
            
            lord1_house = self._planet_houses.get(lord1)
            if lord1_house and lord1_house in all_houses and lord1_house != h1:
                refs.append(
                    f"{h1}th Lord ({lord1}) in {lord1_house}th House "
                    f"connects {h1}th and {lord1_house}th house matters"
                )
        
        # Check for lord conjunctions
        checked = set()
        for h1 in all_houses:
            for h2 in all_houses:
                if h1 >= h2:
                    continue
                
                pair = (h1, h2)
                if pair in checked:
                    continue
                checked.add(pair)
                
                lord1 = self._house_lords.get(h1)
                lord2 = self._house_lords.get(h2)
                
                if lord1 and lord2 and lord1 != lord2:
                    l1_house = self._planet_houses.get(lord1)
                    l2_house = self._planet_houses.get(lord2)
                    
                    if l1_house and l1_house == l2_house:
                        refs.append(
                            f"{h1}th Lord ({lord1}) conjunct {h2}th Lord ({lord2}) "
                            f"in House {l1_house} - strong connection"
                        )
        
        return refs
    
    def _get_house_occupancy(self, houses: Set[int]) -> Dict[int, List[str]]:
        """Get planets occupying specified houses"""
        occupancy = {}
        
        for house_num in houses:
            occupants = []
            for pname, phouse in self._planet_houses.items():
                if phouse == house_num:
                    occupants.append(pname)
            if occupants:
                occupancy[house_num] = occupants
        
        return occupancy
    
    def _get_house_aspects(self, houses: Set[int]) -> Dict[int, Dict[str, List[str]]]:
        """Get aspects on specified houses"""
        aspects = {}
        
        aspects_on_house = self.aspects_data.get("aspects_on_house", {})
        
        for house_num in houses:
            aspecting = aspects_on_house.get(house_num, [])
            if not aspecting:
                continue
            
            benefic = [p for p in aspecting if p in BENEFICS]
            malefic = [p for p in aspecting if p in MALEFICS]
            
            if benefic or malefic:
                aspects[house_num] = {"benefic": benefic, "malefic": malefic}
        
        return aspects
    
    def _analyze_karaka(self, karaka_name: str) -> Dict[str, Any]:
        """Analyze the karaka (significator) for a domain"""
        karaka = self._get_planet(karaka_name)
        if not karaka:
            return {"planet": karaka_name, "status": "not found"}
        
        house = karaka.get("house", 0)
        sign = str(karaka.get("sign") or karaka.get("rasi") or "").title()
        
        dignity = self._get_dignity(karaka_name, sign, karaka.get("local_degree", 0))
        is_retro = karaka.get("is_retro", False)
        is_combust = self._is_combust(karaka_name)
        
        benefic_asp, malefic_asp = self._get_aspects_on_planet(karaka_name)
        
        # Determine status
        if dignity in (LordDignity.EXALTED, LordDignity.OWN_SIGN, LordDignity.MOOLATRIKONA):
            status = "Strong"
        elif dignity == LordDignity.DEBILITATED or is_combust:
            status = "Weak"
        else:
            status = "Neutral"
        
        summary = f"{karaka_name} in {sign} in {house}th house | {status}"
        
        return {
            "planet": karaka_name,
            "house": house,
            "sign": sign,
            "dignity": dignity.value,
            "is_retrograde": is_retro,
            "is_combust": is_combust,
            "benefic_aspects": benefic_asp,
            "malefic_aspects": malefic_asp,
            "status": status,
            "summary": summary
        }
    
    def get_domain_analysis(
        self,
        domain: str,
        language: str = "English"
    ) -> DomainAnalysis:
        """
        Get complete analysis for a domain.
        
        Args:
            domain: Domain name (Marriage, Career, etc.)
            language: Output language (English/Hindi)
        
        Returns:
            DomainAnalysis with all details
        """
        config = DOMAIN_HOUSES.get(domain)
        if not config:
            return DomainAnalysis(domain=domain)
        
        primary = config["primary"]
        secondary = config["secondary"]
        karaka = config["karaka"]
        
        # Analyze primary lords
        primary_lords = [self.analyze_house_lord(h) for h in sorted(primary)]
        
        # Analyze secondary lords
        secondary_lords = [self.analyze_house_lord(h) for h in sorted(secondary)]
        
        # Find cross-references
        cross_refs = self._find_cross_references(primary, secondary)
        
        # Get house occupancy
        occupancy = self._get_house_occupancy(primary | secondary)
        
        # Get house aspects
        aspects = self._get_house_aspects(primary | secondary)
        
        # Analyze karaka
        karaka_analysis = self._analyze_karaka(karaka)
        
        # Calculate overall strength (weighted average)
        primary_strength = sum(l.strength_score for l in primary_lords) / len(primary_lords) if primary_lords else 5.0
        secondary_strength = sum(l.strength_score for l in secondary_lords) / len(secondary_lords) if secondary_lords else 5.0
        
        overall = primary_strength * 0.6 + secondary_strength * 0.4
        
        # Format output
        formatted = self._format_for_llm(
            domain, primary_lords, secondary_lords, cross_refs,
            occupancy, aspects, karaka_analysis, overall, language
        )
        
        return DomainAnalysis(
            domain=domain,
            primary_lords=primary_lords,
            secondary_lords=secondary_lords,
            cross_references=cross_refs,
            house_occupancy=occupancy,
            house_aspects=aspects,
            karaka_analysis=karaka_analysis,
            overall_strength=overall,
            formatted_output=formatted
        )
    
    def _format_for_llm(
        self,
        domain: str,
        primary_lords: List[HouseLordAnalysis],
        secondary_lords: List[HouseLordAnalysis],
        cross_refs: List[str],
        occupancy: Dict[int, List[str]],
        aspects: Dict[int, Dict[str, List[str]]],
        karaka: Dict[str, Any],
        overall: float,
        language: str = "English"
    ) -> str:
        """Format analysis for LLM consumption"""
        lines = []
        
        # Header
        desc = DOMAIN_HOUSES.get(domain, {}).get(
            "description_hi" if language == "Hindi" else "description_en",
            domain
        )
        
        lines.append("═" * 60)
        lines.append(f"📊 HOUSE LORDS ANALYSIS ({desc})")
        lines.append("═" * 60)
        lines.append("")
        
        # Priority 1: Primary House Lords Placement
        lines.append("▶ PRIMARY HOUSE LORDS:")
        for lord in primary_lords:
            lines.append(f"  📍 {lord.format_placement(language)}")
            
            # Dignity
            if lord.dignity == LordDignity.EXALTED:
                lines.append(f"     ⬆️ {lord.lord_name} EXALTED - very strong")
            elif lord.dignity == LordDignity.DEBILITATED:
                lines.append(f"     ⬇️ {lord.lord_name} DEBILITATED - needs strengthening")
            elif lord.dignity == LordDignity.OWN_SIGN:
                lines.append(f"     🏠 {lord.lord_name} in own sign - naturally strong")
            
            # Afflictions
            afflictions = []
            if lord.is_combust:
                afflictions.append("Combust")
            if lord.is_retrograde:
                afflictions.append("Retrograde")
            if lord.malefic_aspects:
                afflictions.append(f"Malefic aspects from {', '.join(lord.malefic_aspects)}")
            
            if afflictions:
                lines.append(f"     ⚠️ {' | '.join(afflictions)}")
            
            # Benefic support
            if lord.benefic_aspects:
                lines.append(f"     ✅ Supported by: {', '.join(lord.benefic_aspects)}")
            
            # Strength
            if lord.strength_score >= 7:
                lines.append(f"     💪 Strong ({lord.strength_score:.1f}/10)")
            elif lord.strength_score <= 4:
                lines.append(f"     ⚡ Weak ({lord.strength_score:.1f}/10)")
        
        lines.append("")
        
        # Priority 2: Cross-References
        if cross_refs:
            lines.append("▶ HOUSE CONNECTIONS (Key for Predictions):")
            for ref in cross_refs:
                lines.append(f"  🔗 {ref}")
            lines.append("")
        
        # Priority 3: Planets in Houses
        if occupancy:
            lines.append("▶ PLANETS IN RELEVANT HOUSES:")
            house_meanings = {
                7: "Partnership", 2: "Family/Wealth", 11: "Gains",
                5: "Romance", 8: "Transformation", 10: "Career",
                6: "Service", 9: "Fortune", 4: "Home", 12: "Expenses"
            }
            for h, planets in sorted(occupancy.items()):
                meaning = house_meanings.get(h, "")
                lines.append(f"  • House {h} ({meaning}): {', '.join(planets)}")
            lines.append("")
        
        # Priority 4: Aspects on Houses
        if aspects:
            lines.append("▶ ASPECTS ON HOUSES:")
            for h, asp_data in sorted(aspects.items()):
                if asp_data.get("benefic"):
                    lines.append(f"  • House {h} benefic aspects: {', '.join(asp_data['benefic'])}")
                if asp_data.get("malefic"):
                    lines.append(f"  • House {h} malefic aspects: {', '.join(asp_data['malefic'])}")
            lines.append("")
        
        # Karaka Status
        if karaka:
            lines.append(f"▶ KARAKA ({karaka.get('planet', '')}) Status:")
            lines.append(f"  ⭐ {karaka.get('summary', 'N/A')}")
            lines.append("")
        
        # Overall
        if overall >= 7:
            lines.append(f"✅ OVERALL: Strong indicators (Score: {overall:.1f}/10)")
        elif overall <= 4:
            lines.append(f"⚠️ OVERALL: Challenging indicators (Score: {overall:.1f}/10)")
        else:
            lines.append(f"📊 OVERALL: Moderate indicators (Score: {overall:.1f}/10)")
        
        lines.append("═" * 60)
        
        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_house_lords_for_domain(
    planets: Dict,
    houses: List[Dict],
    domain: str,
    aspects_data: Dict = None,
    language: str = "English"
) -> str:
    """
    Convenience function to get formatted house lords analysis.
    
    Args:
        planets: Planet data dictionary
        houses: House data list
        domain: Domain name
        aspects_data: Pre-calculated aspects (optional)
        language: Output language
    
    Returns:
        Formatted string for LLM
    """
    analyzer = HouseLordsAnalyzer(planets, houses, aspects_data)
    analysis = analyzer.get_domain_analysis(domain, language)
    return analysis.formatted_output


def get_house_lords_points(
    planets: Dict,
    houses: List[Dict],
    domain: str,
    aspects_data: Dict = None
) -> List[str]:
    """
    Get house lords analysis as list of technical points.
    
    Args:
        planets: Planet data dictionary
        houses: House data list
        domain: Domain name
        aspects_data: Pre-calculated aspects (optional)
    
    Returns:
        List of technical points
    """
    analyzer = HouseLordsAnalyzer(planets, houses, aspects_data)
    analysis = analyzer.get_domain_analysis(domain)
    
    points = []
    
    # Add primary lord points
    for lord in analysis.primary_lords:
        points.append(lord.format_placement())
        points.append(f"  Condition: {lord.format_condition()}")
        points.append(f"  Strength: {lord.strength_score:.1f}/10")
    
    # Add cross-references
    for ref in analysis.cross_references:
        points.append(f"Connection: {ref}")
    
    # Add overall
    points.append(f"Overall Domain Strength: {analysis.overall_strength:.1f}/10")
    
    return points

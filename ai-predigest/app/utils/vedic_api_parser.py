"""
Vedic API Parser - Enhanced with House Lords Integration

Parses Vedic Astro API responses and formats data for LLM consumption.
Includes house lords analysis following classical Vedic priority order.

Priority Order:
1. House Lord Placement
2. House Lord Condition (dignity, afflictions, aspects)
3. Planets in House
4. Aspects on House

Version: 2.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Import house lords analyzer if available
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer, 
        get_house_lords_for_domain,
        get_house_lords_points,
        DOMAIN_HOUSES
    )
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logger.warning("house_lords_analyzer not available - house lords features disabled")


# =============================================================================
# CONSTANTS
# =============================================================================

# Sign lordships (Vedic system)
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

# Special aspects for each planet
SPECIAL_ASPECTS = {
    "Mars": [4, 7, 8],      # 4th, 7th, 8th from position
    "Jupiter": [5, 7, 9],   # 5th, 7th, 9th from position
    "Saturn": [3, 7, 10],   # 3rd, 7th, 10th from position
    "Rahu": [5, 7, 9],      # Like Jupiter
    "Ketu": [5, 7, 9],      # Like Jupiter
    "Sun": [7],
    "Moon": [7],
    "Mercury": [7],
    "Venus": [7]
}


# =============================================================================
# CORE PARSING FUNCTIONS
# =============================================================================

def parse_vedic_api_response(api_response: Dict) -> Tuple[Dict, Dict]:
    """
    Parse the Vedic API response format where keys are indices (0, 1, 2...).
    
    Args:
        api_response: Raw API response with planets as "0", "1", "2" keys
    
    Returns:
        Tuple of (planets_dict, metadata_dict)
    """
    if not api_response or "response" not in api_response:
        logger.error("Invalid API response format")
        return {}, {}
    
    response_data = api_response["response"]
    
    planets = {}
    metadata = {
        "birth_dasa": response_data.get("birth_dasa"),
        "current_dasa": response_data.get("current_dasa"),
        "rasi": response_data.get("rasi"),
        "nakshatra": response_data.get("nakshatra"),
        "lucky_gem": response_data.get("lucky_gem", []),
        "panchang": response_data.get("panchang", {})
    }
    
    # Skip these non-planet keys
    skip_keys = {
        "birth_dasa", "current_dasa", "lucky_gem", "lucky_num", 
        "lucky_colors", "lucky_letters", "lucky_name_start", 
        "rasi", "nakshatra", "nakshatra_pada", "panchang", "ghatka_chakra"
    }
    
    for key, planet_data in response_data.items():
        if not isinstance(planet_data, dict):
            continue
        if key in skip_keys:
            continue
        
        planet_name = planet_data.get("full_name", "")
        if not planet_name:
            continue
        
        # Handle Ascendant separately
        if planet_name == "Ascendant":
            metadata["ascendant"] = planet_data
            continue
        
        planets[planet_name] = {
            "name": planet_name,
            "short_name": planet_data.get("name", ""),
            "house": planet_data.get("house"),
            "sign": planet_data.get("zodiac", ""),
            "rasi": planet_data.get("zodiac", ""),
            "rasi_no": planet_data.get("rasi_no"),
            "local_degree": planet_data.get("local_degree", 0),
            "global_degree": planet_data.get("global_degree", 0),
            "full_degree": planet_data.get("global_degree", 0),
            "nakshatra": planet_data.get("nakshatra", ""),
            "nakshatra_lord": planet_data.get("nakshatra_lord", ""),
            "nakshatra_pada": planet_data.get("nakshatra_pada"),
            "nakshatra_no": planet_data.get("nakshatra_no"),
            "zodiac_lord": planet_data.get("zodiac_lord", ""),
            "is_retro": planet_data.get("retro", False),
            "is_combusted": planet_data.get("is_combust", False),
            "is_combust": planet_data.get("is_combust", False),
            "lord_status": planet_data.get("lord_status", ""),
            "basic_avastha": planet_data.get("basic_avastha", ""),
            "speed": planet_data.get("speed_radians_per_day", 0)
        }
    
    return planets, metadata


def create_houses_from_planets(planets: Dict, ascendant_data: Dict = None) -> List[Dict]:
    """
    Create house structure from planet data.
    
    Args:
        planets: Parsed planet data
        ascendant_data: Ascendant information
    
    Returns:
        List of house dictionaries with lordship information
    """
    houses = []
    
    if ascendant_data:
        asc_sign = ascendant_data.get("zodiac", "Leo")
        asc_rasi_no = ascendant_data.get("rasi_no", 5)
        
        for house_num in range(1, 13):
            sign_no = ((asc_rasi_no - 1 + house_num - 1) % 12) + 1
            sign_name = SIGNS[sign_no - 1]
            sign_lord = SIGN_LORDS.get(sign_name, "")
            
            # Find planets in this house
            planets_in_house = []
            for planet_name, planet_data in planets.items():
                if planet_data.get("house") == house_num:
                    planets_in_house.append(planet_name)
            
            houses.append({
                "house": house_num,
                "sign": sign_name,
                "start_rasi": sign_name,
                "rasi": sign_name,
                "rasi_no": sign_no,
                "sign_lord": sign_lord,
                "planets": planets_in_house,
                "cusp_degree": 0
            })
    else:
        logger.warning("No ascendant data - creating basic house structure")
        for house_num in range(1, 13):
            houses.append({
                "house": house_num,
                "sign": "Unknown",
                "sign_lord": "Unknown",
                "planets": []
            })
    
    return houses


# =============================================================================
# ASPECT CALCULATION
# =============================================================================

def calculate_planetary_aspects(planets: Dict) -> Dict:
    """
    Calculate Vedic planetary aspects (Drishti) deterministically.
    
    Vedic Aspect Rules:
    - ALL planets have 7th house aspect (full aspect - 100%)
    - Mars: Additional 4th and 8th house aspects (full)
    - Jupiter: Additional 5th and 9th house aspects (full)
    - Saturn: Additional 3rd and 10th house aspects (full)
    - Rahu/Ketu: 5th, 7th, 9th aspects (like Jupiter)
    
    Args:
        planets: Dictionary of planet data with house positions
    
    Returns:
        Dictionary with:
        - 'aspects_by_planet': {planet_name: [houses aspected]}
        - 'aspects_on_house': {house_num: [planets aspecting]}
        - 'aspects_on_planet': {planet_name: [planets aspecting it]}
        - 'aspect_details': [{aspecting, aspected_house, aspect_type}]
    """
    aspects_by_planet = {}
    aspects_on_house = {i: [] for i in range(1, 13)}
    aspects_on_planet = {pname: [] for pname in planets.keys()}
    aspect_details = []
    
    # Build planet-to-house mapping
    planet_houses = {}
    for pname, pdata in planets.items():
        house = pdata.get("house")
        if house:
            planet_houses[pname] = house
    
    # Calculate aspects for each planet
    for planet_name, planet_data in planets.items():
        planet_house = planet_data.get("house")
        if not planet_house:
            continue
        
        aspect_offsets = SPECIAL_ASPECTS.get(planet_name, [7])
        
        aspected_houses = []
        for offset in aspect_offsets:
            # Calculate target house (1-12 cycle)
            target_house = ((planet_house - 1 + (offset - 1)) % 12) + 1
            aspected_houses.append(target_house)
            
            # Record aspect on house
            if planet_name not in aspects_on_house[target_house]:
                aspects_on_house[target_house].append(planet_name)
            
            # Find planets in aspected house
            aspected_planets = []
            for other_planet, other_data in planets.items():
                if other_planet != planet_name and other_data.get("house") == target_house:
                    aspected_planets.append(other_planet)
                    if planet_name not in aspects_on_planet[other_planet]:
                        aspects_on_planet[other_planet].append(planet_name)
            
            aspect_details.append({
                "aspecting_planet": planet_name,
                "from_house": planet_house,
                "aspect_offset": offset,
                "aspected_house": target_house,
                "aspected_planets": aspected_planets,
                "aspect_type": "special" if offset != 7 else "7th"
            })
        
        aspects_by_planet[planet_name] = aspected_houses
    
    return {
        "aspects_by_planet": aspects_by_planet,
        "aspects_on_house": aspects_on_house,
        "aspects_on_planet": aspects_on_planet,
        "aspect_details": aspect_details
    }


def get_aspects_on_planet(planet_name: str, aspects_data: Dict) -> List[str]:
    """Get list of planets aspecting a specific planet."""
    return aspects_data.get("aspects_on_planet", {}).get(planet_name, [])


def get_aspects_on_house(house_num: int, aspects_data: Dict) -> List[str]:
    """Get list of planets aspecting a specific house."""
    return aspects_data.get("aspects_on_house", {}).get(house_num, [])


# =============================================================================
# HOUSE LORDS INTEGRATION
# =============================================================================

def get_house_lord_data(
    house_num: int,
    planets: Dict,
    houses: List[Dict],
    aspects_data: Dict = None
) -> Dict[str, Any]:
    """
    Get comprehensive house lord placement information.
    
    Args:
        house_num: House number (1-12)
        planets: Normalized planet data
        houses: House/cusp data list
        aspects_data: Pre-calculated aspects (optional)
    
    Returns:
        Dictionary with lord placement and condition details
    """
    if not HOUSE_LORDS_AVAILABLE:
        return {"error": "House lords analyzer not available"}
    
    analyzer = HouseLordsAnalyzer(planets, houses, aspects_data)
    analysis = analyzer.analyze_house_lord(house_num)
    
    return {
        "house": analysis.house_num,
        "sign_on_cusp": analysis.cusp_sign,
        "lord": analysis.lord_name,
        "lord_placement": {
            "house": analysis.lord_house,
            "sign": analysis.lord_sign,
            "degree": analysis.lord_degree,
            "nakshatra": analysis.lord_nakshatra,
            "nakshatra_lord": analysis.lord_nakshatra_lord
        },
        "lord_condition": {
            "dignity": analysis.dignity.value,
            "is_retrograde": analysis.is_retrograde,
            "is_combust": analysis.is_combust,
            "benefic_aspects": analysis.benefic_aspects,
            "malefic_aspects": analysis.malefic_aspects,
            "is_afflicted": analysis.is_afflicted
        },
        "strength_score": analysis.strength_score,
        "formatted": analysis.format_full()
    }


def format_house_lords_for_domain(
    planets: Dict,
    houses: List[Dict],
    domain: str,
    aspects_data: Dict = None,
    language: str = "English"
) -> str:
    """
    Format house lords analysis for a specific domain.
    
    Args:
        planets: Normalized planet data
        houses: House/cusp data list
        domain: Domain name (Marriage, Career, Finance, etc.)
        aspects_data: Pre-calculated aspects (optional)
        language: "English" or "Hindi"
    
    Returns:
        Formatted string for LLM consumption with proper priority
    """
    if not HOUSE_LORDS_AVAILABLE:
        return "House lords analysis not available"
    
    return get_house_lords_for_domain(planets, houses, domain, aspects_data, language)


def get_domain_technical_points(
    planets: Dict,
    houses: List[Dict],
    domain: str,
    aspects_data: Dict = None
) -> List[str]:
    """
    Get house lords analysis as list of technical points.
    
    Args:
        planets: Normalized planet data
        houses: House/cusp data list
        domain: Domain name
        aspects_data: Pre-calculated aspects (optional)
    
    Returns:
        List of technical points for domain evaluators
    """
    if not HOUSE_LORDS_AVAILABLE:
        return ["House lords analysis not available"]
    
    return get_house_lords_points(planets, houses, domain, aspects_data)


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================

def format_aspects_for_llm(aspects_data: Dict, planets: Dict) -> str:
    """
    Format aspect data for LLM consumption.
    
    Args:
        aspects_data: Output from calculate_planetary_aspects()
        planets: Planet dictionary for reference
    
    Returns:
        Formatted string describing all aspects
    """
    lines = []
    lines.append("")
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + " 🔭 PLANETARY ASPECTS (DRISHTI) - DETERMINISTIC CALCULATION ".center(78) + "║")
    lines.append("╠" + "═" * 78 + "╣")
    lines.append("║ These aspects are mathematically calculated. Use ONLY these aspect claims.    ║")
    lines.append("║ Do NOT invent or assume any aspects not listed here.                         ║")
    lines.append("╚" + "═" * 78 + "╝")
    lines.append("")
    
    # Aspects BY each planet
    lines.append("ASPECTS CAST BY EACH PLANET:")
    lines.append("-" * 60)
    
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet_name not in aspects_data.get("aspects_by_planet", {}):
            continue
        
        planet_house = planets.get(planet_name, {}).get("house", "?")
        aspected_houses = aspects_data["aspects_by_planet"][planet_name]
        
        if planet_name == "Mars":
            aspect_rule = "4th, 7th, 8th aspects"
        elif planet_name in ["Jupiter", "Rahu", "Ketu"]:
            aspect_rule = "5th, 7th, 9th aspects"
        elif planet_name == "Saturn":
            aspect_rule = "3rd, 7th, 10th aspects"
        else:
            aspect_rule = "7th aspect only"
        
        lines.append(f"  ★ {planet_name} (from H{planet_house}): aspects Houses {', '.join(map(str, sorted(aspected_houses)))} ({aspect_rule})")
    
    lines.append("")
    
    # Key house aspects
    lines.append("KEY HOUSE ASPECTS:")
    lines.append("-" * 60)
    
    important_houses = [1, 7, 10, 4, 5, 9]
    house_names = {
        1: "Lagna/Self", 7: "Marriage/Partner", 10: "Career",
        4: "Home/Mother", 5: "Children/Romance", 9: "Fortune/Father"
    }
    
    for house_num in important_houses:
        aspecting = aspects_data.get("aspects_on_house", {}).get(house_num, [])
        if aspecting:
            lines.append(f"  • House {house_num} ({house_names.get(house_num, '')}): Aspected by {', '.join(aspecting)}")
    
    lines.append("")
    
    # Aspects ON each planet
    lines.append("ASPECTS RECEIVED BY EACH PLANET:")
    lines.append("-" * 60)
    
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet_name not in aspects_data.get("aspects_on_planet", {}):
            continue
        
        aspecting_planets = aspects_data["aspects_on_planet"][planet_name]
        planet_house = planets.get(planet_name, {}).get("house", "?")
        
        if aspecting_planets:
            lines.append(f"  ★ {planet_name} (in H{planet_house}): Aspected by {', '.join(aspecting_planets)}")
        else:
            lines.append(f"  ★ {planet_name} (in H{planet_house}): No aspects received")
    
    lines.append("")
    lines.append("═" * 78)
    lines.append("⚠️  CRITICAL: If you need to mention aspects, use ONLY the data above.")
    lines.append("    Do NOT claim any aspect not explicitly listed here.")
    lines.append("═" * 78)
    
    return "\n".join(lines)


def format_for_llm_from_api_response(api_response: Dict) -> str:
    """
    Parse API response and format it for LLM with clear structure.
    
    Args:
        api_response: Raw API response
    
    Returns:
        Formatted string ready for LLM
    """
    planets, metadata = parse_vedic_api_response(api_response)
    
    if not planets:
        return "Error: Could not parse planet data from API response"
    
    ascendant_data = metadata.get("ascendant")
    houses = create_houses_from_planets(planets, ascendant_data)
    
    output = []
    
    output.append("=" * 80)
    output.append("VEDIC ASTROLOGICAL CHART - COMPLETE ANALYSIS")
    output.append("=" * 80)
    output.append("")
    
    # Current Dasha
    if metadata.get("current_dasa"):
        output.append(f"📅 CURRENT DASHA: {metadata['current_dasa']}")
        output.append("")
    
    # Planet Positions
    output.append("📍 PLANETARY POSITIONS:")
    output.append("-" * 80)
    output.append("")
    
    for planet_name in sorted(planets.keys()):
        planet = planets[planet_name]
        
        house_num = planet.get("house")
        sign = planet.get("sign")
        degree = planet.get("full_degree", 0)
        nakshatra = planet.get("nakshatra")
        nakshatra_lord = planet.get("nakshatra_lord")
        is_retro = planet.get("is_retro", False)
        is_combust = planet.get("is_combusted", False)
        
        output.append(f"{planet_name}:")
        output.append(f"  • Position: House {house_num} in {sign}")
        output.append(f"  • Degree: {degree:.2f}°")
        output.append(f"  • Nakshatra: {nakshatra} (ruled by {nakshatra_lord})")
        
        status_parts = []
        if is_retro:
            status_parts.append("Retrograde")
        if is_combust:
            status_parts.append("Combusted")
        
        output.append(f"  • Status: {', '.join(status_parts) if status_parts else 'Direct'}")
        output.append("")
    
    # House Structure
    output.append("\n🏠 HOUSE STRUCTURE & LORDSHIPS:")
    output.append("-" * 80)
    output.append("")
    
    for house in houses:
        house_num = house["house"]
        sign = house["sign"]
        sign_lord = house["sign_lord"]
        planets_in_house = house.get("planets", [])
        
        output.append(f"House {house_num}: {sign}")
        output.append(f"  • Ruled by: {sign_lord}")
        if planets_in_house:
            output.append(f"  • Planets: {', '.join(planets_in_house)}")
        output.append("")
    
    # House Connections
    output.append("\n🔗 HOUSE CONNECTIONS (Critical!):")
    output.append("-" * 80)
    output.append("")
    
    for planet_name, planet_data in sorted(planets.items()):
        house_placement = planet_data.get("house")
        
        rules_houses = []
        for house in houses:
            if house.get("sign_lord") == planet_name:
                rules_houses.append(house["house"])
        
        if rules_houses:
            output.append(f"{planet_name}:")
            output.append(f"  • In: House {house_placement}")
            output.append(f"  • Rules: House(s) {', '.join(map(str, rules_houses))}")
            output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)


def format_complete_chart_for_llm(
    api_response: Dict,
    domain: str = None,
    language: str = "English"
) -> str:
    """
    Parse API response and format complete chart data for LLM.
    
    Combines:
    1. House Lords Analysis (if domain specified)
    2. Planetary Positions
    3. Aspect Data
    4. Dasha Information
    
    Args:
        api_response: Raw API response
        domain: Domain for focused analysis (optional)
        language: Output language
    
    Returns:
        Comprehensive formatted string for LLM
    """
    planets, metadata = parse_vedic_api_response(api_response)
    
    if not planets:
        return "Error: Could not parse planet data from API response"
    
    ascendant_data = metadata.get("ascendant")
    houses = create_houses_from_planets(planets, ascendant_data)
    aspects_data = calculate_planetary_aspects(planets)
    
    output = []
    
    # Header
    output.append("=" * 80)
    output.append("VEDIC ASTROLOGICAL CHART - COMPLETE ANALYSIS")
    output.append("=" * 80)
    output.append("")
    
    # House Lords Section (PRIMARY)
    if domain and HOUSE_LORDS_AVAILABLE:
        output.append("╔" + "═" * 78 + "╗")
        output.append("║" + " HOUSE LORDS ANALYSIS (PRIMARY - FOLLOW THIS PRIORITY) ".center(78) + "║")
        output.append("╚" + "═" * 78 + "╝")
        output.append("")
        house_lords_section = format_house_lords_for_domain(
            planets, houses, domain, aspects_data, language
        )
        output.append(house_lords_section)
        output.append("")
    
    # Planetary Positions
    output.append("╔" + "═" * 78 + "╗")
    output.append("║" + " PLANETARY POSITIONS ".center(78) + "║")
    output.append("╚" + "═" * 78 + "╝")
    output.append("")
    
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet_name not in planets:
            continue
        
        planet = planets[planet_name]
        house_num = planet.get("house", "?")
        sign = planet.get("sign", "?")
        degree = planet.get("local_degree", 0)
        nakshatra = planet.get("nakshatra", "")
        
        status_parts = []
        if planet.get("is_retro"):
            status_parts.append("R")
        if planet.get("is_combusted"):
            status_parts.append("C")
        status = f" ({', '.join(status_parts)})" if status_parts else ""
        
        output.append(f"  {planet_name:10} → H{house_num:2} in {sign:12} at {degree:6.2f}° {nakshatra:15}{status}")
    
    output.append("")
    
    # Aspects
    output.append(format_aspects_for_llm(aspects_data, planets))
    
    # Dasha
    if metadata.get("current_dasa"):
        output.append("")
        output.append("╔" + "═" * 78 + "╗")
        output.append("║" + " CURRENT DASHA ".center(78) + "║")
        output.append("╚" + "═" * 78 + "╝")
        output.append(f"  {metadata['current_dasa']}")
    
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)
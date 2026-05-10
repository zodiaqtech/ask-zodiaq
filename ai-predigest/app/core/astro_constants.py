"""
Core astrology constants and helper functions
"""
from asyncio.log import logger
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
import math
from collections import defaultdict
from typing import Dict, List, Set
from threading import Lock

# Cache for planetary significator table API data
# Key: chart_hash (unique per birth chart), Value: API response data
_SIGNIFICATOR_CACHE: Dict[str, Dict] = {}
_CACHE_LOCK = Lock()

# KP Weights (tunable but keep ratios)
KP_WEIGHTS = {
    "sub": 4.0,      # Sub lord strongest (final promise giver)
    "star": 3.0,     # Star lord strong (modifier)
    "occupy": 2.0,   # Occupation medium
    "own": 1.0,      # Ownership weakest
    "conj": 1.5,     # Conjunction bonus
}

# Sign base degrees
SIGN_BASE = {
    "Aries": 0, "Taurus": 30, "Gemini": 60, "Cancer": 90,
    "Leo": 120, "Virgo": 150, "Libra": 180, "Scorpio": 210,
    "Sagittarius": 240, "Capricorn": 270, "Aquarius": 300, "Pisces": 330
}

SIGN_LORDS = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
            "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
            "Sagittarius": "Jupiter", "Capricorn": "Saturn",
            "Aquarius": "Saturn", "Pisces": "Jupiter",
        }
sign_disease_map = {
            "Aries": [
                "Head injuries", "Migraine", "Brain inflammation",
                "Blood pressure", "Fever", "Cuts & burns"
            ],
            "Taurus": [
                "Throat infections", "Tonsils", "Voice disorders",
                "Neck pain", "Thyroid imbalance"
            ],
            "Gemini": [
                "Respiratory issues", "Asthma", "Bronchitis",
                "Nervous disorders", "Shoulder & arm pain"
            ],
            "Cancer": [
                "Stomach disorders", "Gastritis", "Acidity",
                "Chest congestion", "Breast-related issues"
            ],
            "Leo": [
                "Heart problems", "Cardiac stress",
                "Spine pain", "Circulatory issues", "Blood pressure"
            ],
            "Virgo": [
                "Digestive disorders", "Intestinal issues",
                "IBS", "Food intolerance", "Skin allergies"
            ],
            "Libra": [
                "Kidney disorders", "Urinary infections",
                "Lower back pain", "Hormonal imbalance"
            ],
            "Scorpio": [
                "Reproductive system issues", "UTI",
                "STDs", "Piles", "Chronic infections"
            ],
            "Sagittarius": [
                "Hip pain", "Sciatica", "Liver disorders",
                "Thigh injuries", "Fatty liver"
            ],
            "Capricorn": [
                "Knee pain", "Arthritis", "Bone weakness",
                "Dental issues", "Skin dryness"
            ],
            "Aquarius": [
                "Circulatory problems", "Varicose veins",
                "Ankle injuries", "Nervous breakdown"
            ],
            "Pisces": [
                "Foot disorders", "Sleep disturbances",
                "Psychosomatic illness", "Addictions",
                "Immune weakness"
            ]
        }

KP_PROFESSION_MAP = {
    "abrasives": ["Mars", "Mercury", "Saturn"],
    "accounts": ["Jupiter", "Mercury"],
    "accountant_in_military_police_department_or_industry": ["Mars", "Mercury", "Jupiter"],
    "accountant_in_bank": ["Jupiter", "Mercury"],
    "accountant_in_shipping": ["Jupiter", "Mercury","Venus","Moon"],
    "accountant_in_hospital": ["Sun", "Mercury", "Jupiter"],
    "accountant_in_navy": ["Mercury", "Jupiter","Moon","Mars"],
    "accountant_in_mines": ["Mercury", "Jupiter", "Saturn"],
    "accountant_in_research_department": ["Jupiter", "Mercury"],
    "accountant_in_jail": ["Mercury", "Jupiter", "Rahu"],
    "independent_auditor": ["Mars"],
    "acetylene_generator": ["Moon", "Mars", "Venus"],
    "acid_alkali_resistant_tiles": ["Mars", "Jupiter", "Saturn", "Venus"],
    "acid_jars": ["Mars", "Venus", "Saturn"],
    "acid_manufacturer": ["Mars", "Venus", "Jupiter","Moon"],
    "addressing_machine": ["Mercury", "Jupiter", "Mars"],
    "adhesives": ["Moon", "Venus"],
    "advertising": ["Jupiter","Mercury", "Mars","Venus"],
    "agricultural_implement": ["Mercury", "Saturn"],
    "agricultural_machinery": ["Mercury", "Venus"],
    "air_compressor": ["Mars", "Saturn"],
    "air_conditioner": ["Saturn","Mars", "Venus"],
    "aircraft_instruments": ["Saturn","Venus","Mars"],
    "aluminium": ["Mars", "Venus"],
    "analytical_chemist": ["Mercury", "Venus"],
    "architects": ["Mars", "Venus","Mercury"],
    "asbestos": ["Sun","Moon", "Mercury"],
    "astrology": ["Mercury"],
    "atomic_energy": ["Mars", "Mercury"],
    "auctioneers": ["Jupiter", "Mercury"],
    "automobile": ["Mars","Venus"],
    "aviation": ["Mercury", "Mars", "Venus"],
    "ayurvedic_medicine": ["Jupiter", "Sun", "Mars", "Venus"],
    "bakelite": ["Mars", "Saturn", "Venus"],
    "ball_bearings": ["Sun", "Mars", "Mercury", "Venus"],
    "barbed_wire": ["Mars", "Saturn", "Sun", "Venus"],
    "batteries": ["Mars", "Mercury", "Moon", "Venus"],
    "belt": ["Mars", "Moon", "Saturn", "Venus"],
    "block_makers": ["Moon", "Mercury", "Sun", "Venus"],
    "boilers": ["Mars", "Mercury", "Moon"],
    "bolts_and_nuts": ["Mars", "Mercury", "Saturn"],
    "books": ["Jupiter", "Mercury"],
    "boots_and_shoes": ["Mars", "Saturn", "Venus"],
    "borewell": ["Mars", "Moon", "Saturn"],
    "brakes": ["Mars", "Saturn", "Venus"],
    "bricks_and_tiles": ["Mars", "Venus"],
    "brushes": [    "Sun", "Saturn", "Venus"],
    "builders_and_contractors": ["Mars", "Mercury"],
    "cables": ["Sun", "Mercury"],
    "calculators": ["Mercury", "Saturn"],
    "calendars": ["Jupiter", "Mercury"],
    "car": ["Mars", "Venus"],
    "carpet": ["Mars", "Saturn", "Venus"],
    "casting": ["Mars", "Saturn"],
    "cement": ["Mars", "Saturn", "Venus"],
    "chairs": ["Venus"],
    "chemicals": ["Moon", "Venus"],
    "cinema": ["Jupiter", "Mercury", "Venus"],
    "clearing_agent": ["Mercury", "Moon"],
    "coal": ["Mercury", "Venus"],
    "coal_tar": ["Mars",  "Saturn"],
    "cold_storage": ["Saturn", "Moon","Mars"],
    "condensers": [ "Saturn", "Venus"],
    "conduit_pipes": ["Venus", "Moon", "Saturn"],
    "confectionery": ["Mars", "Saturn","Moon"],
    "contractor": ["Mars",  "Venus"],
    "cooking": ["Mars","Mercury"],
    "copper": ["Venus","Mars", "Moon","Sun"],
    "cotton": ["Moon", "Mercury"],
    "cycles": ["Saturn", "Venus"],
    "dairy_farm": ["Moon","Mars", "Venus"],
    "decorators": ["Mars", "Mercury", "Venus"],
    "diamond": ["Sun", "Venus"],
    "disinfectants": ["Mars", "Venus","Saturn"],
    "drawings": ["Mercury","Venus"],
    "dress": ["Mars","Venus"],
    "dyes_and_chemicals": ["Venus"],
    "electrical_accessories": ["Mercury"],
    "sanitary_engineer": ["Mars", "Mercury"],
    "industrial_engineer": ["Mars", "Mercury", "Saturn"],
    "research_department": ["Mercury", "Saturn", "Mars"],
    "mine_engineer": ["Sun", "Jupiter","Saturn"],
    "gold_mine": ["Mars", "Mercury"],
    "engraving": ["Mars", "Venus"],
    "expanded_metals": ["Mars", "Saturn"],
    "fans": ["Mars", "Mercury", "Venus"],
    "farms": ["Jupiter", "Mars", "Moon", "Venus"],
    "fertiliser": ["Mars", "Saturn", "Venus"],
    "fire_extinguisher": ["Mars", "Moon", "Saturn"],
    "flour_mills": ["Mars", "Saturn"],
    "furnace": ["Mars"],
    "furniture": ["Mars", "Venus"],
    "glass": ["Venus"],
    "gramophone": ["Mars", "Venus"],
    "handloom": ["Mars", "Mercury", "Moon"],
    "hardboard": ["Mars", "Mercury"],
    "hardware": ["Mars", "Saturn"],
    "heater": ["Mars", "Mercury", "Venus"],
    "hotels": ["Mars", "Moon", "Venus"],
    "industry": ["Mars"],
    "ink": ["Mars", "Mercury", "Moon"],
    "insurance": ["Mercury", "Saturn"],
    "iron_and_steel": ["Mars", "Saturn"],
    "jute": ["Mars", "Moon", "Saturn", "Venus"],
    "leather": ["Mars", "Saturn", "Venus"],
    "lime": ["Mercury", "Venus"],
    "locks": ["Mars", "Mercury", "Saturn"],
    "locomotives": ["Mars", "Venus"],
    "magician": ["Moon"],
    "marine_engineer": ["Mars", "Mercury", "Moon"],
    "mechanical_engineer": ["Mars", "Mercury"],
    "metal": ["Venus"],
    "mica": ["Saturn", "Venus"],
    "microscope": ["Jupiter", "Mars", "Mercury"],
    # "milk": ["Moon", "Venus"],
    # "mineral": ["Saturn", "Venus"],
    "mines": ["Saturn"],
    "nurse": ["Mercury", "Moon", "Sun"],
    "nursery": ["Mars","Moon", "Venus"],
    "nuts": ["Mars", "Sun", "Venus"],
    "oil_linseed": ["Moon"],
    "optician": ["Mars", "Sun", "Venus"],
    "paintings": ["Venus","Moon"],
    "paper": ["Mercury"],
    "pencils": ["Mercury", "Saturn"],
    "perfumes": ["Moon", "Venus"],
    "pharmaceutical_specialists": ["Sun"],
    "photography": ["Moon", "Sun", "Venus"],
    "pipes": ["Mars", "Mercury","Moon"],
    "plywood": ["Mars", "Venus"],
    "power_house": ["Mars","Venus", "Mercury"],
    "power_house_water_supply": ["Mars","Moon", "Mercury"],
    "press": ["Mars", "Mercury"],
    "printer": ["Jupiter", "Mars", "Mercury"],
    "pumpsets": ["Mars", "Moon", "Saturn"],
    "quarry": ["Mars", "Saturn"],
    "radio": ["Jupiter", "Mercury", "Venus"],
    "railway": ["Mercury", "Venus"],
    "refrigeration": ["Saturn"],
    "ricemill": ["Mars", "Mercury", "Venus"],
    "road_highways": ["Mars","Venus","Saturn"],
    "road_transport": ["Mars","Mercury", "Venus"],
    "rubber": ["Mars", "Moon", "Venus"],
    "salesman": ["Mercury", "Jupiter"],
    "salt": ["Moon", "Mars","Sun"],
    "sanitaryware": ["Mars", "Mercury", "Venus"],
    "sarees": ["Venus"],
    "scientific_apparatus": ["Mars", "Mercury", "Venus"],
    "sewing_machine": ["Mars", "Venus"],
    "shoes": ["Mars", "Saturn", "Venus"],
    "silver": ["Moon", "Venus"],
    "soap": ["Mars", "Venus"],
    "soldier": ["Mars"],
    "sporting_goods": ["Mars", "Sun", "Venus"],
    "stationery": ["Jupiter", "Mercury"],
    "stainless_steel": ["Mars", "Venus"],
    "steam_engine": ["Mars", "Moon", "Venus"],
    "steel": ["Mars", "Saturn"],
    "stone": ["Mars", "Saturn"],
    "sugar": ["Venus"],
    "survey": ["Saturn", "Venus"],
    "surgical": ["Mars", "Mercury", "Sun"],
    "switchgear": ["Mars", "Mercury"],
    "tailor": ["Mars", "Venus"],
    "tanning": ["Mars", "Moon", "Saturn", "Venus"],
    "taxi": ["Mars", "Mercury", "Venus"],
    "tea": ["Mars", "Saturn", "Venus"],
    "textile": ["Mercury", "Moon"],
    "timber": ["Venus"],
    "tin": ["Jupiter"],
    "tools": ["Mars", "Mercury"],
    "tractors_transports": ["Mercury", "Venus"],
    "trench_tunnel": ["Mars", "Saturn"],
    "typewriters": ["Mars", "Mercury"],
    "wood": ["Mars", "Venus"],
    "workshop": ["Mars", "Saturn"],
    "yarn": ["Mercury", "Moon"],
    "president": ["Mars", "Jupiter", "Venus", "Saturn"],
    "minister": ["Jupiter", "Mars", "Sun"],
    "member_of_parliament": ["Jupiter", "Mercury", "Sun"],
    "atomic_energy": ["Jupiter", "Mars", "Sun", ],
    "broad_cashing": ["Jupiter", "Mercury", "Venus"],
    "Commerce": ["Mars", "Mercury", "Sun"],
    "Communication": ["Sun", "Mercury", "Jupiter", "Mars"],
    "Co-operative": ["Venus", "Jupiter"],
    "Defence": ["Mars", "Sun", "Saturn"],
    "Education": ["Jupiter", "Mercury", "Sun"],
    "External Affairs": ["Moon", "Mercury", "Sun"],
    "Finance": ["Jupiter", "Sun", "Mars"],
    "Fisheries Food Agriculture": ["Moon", "Mars", "Venus", "Saturn"],
    "Health": ["Sun", "Mars"], 
    "Home Affairs": ["Mars", "Sun", "Jupiter"],
    "Industry": ["Mars", "Mercury", "Saturn"],
    "Information": ["Jupiter", "Mercury", "Venus"],
    "Iron and Steel": ["Mars", "Saturn", "Mercury"],
    "Irrigation": ["Moon", "Mars", "Venus"],
    "Labour": ["Saturn", "Mars", "Jupiter"],
    "Law": ["Jupiter", "Mars", "Sun"],
    "Metals": ["Mars", "Sun"],
    "Mines": ["Saturn", "Mars", "Sun"],
    "Petroleum": ["Saturn", "Moon", "Venus", "Mars"],
    "Post and Telegraph": ["Jupiter", "Mercury", "Mars"],
    "Railways": ["Venus", "Mars", "Mercury"],
    "Rehabilitation": ["Saturn", "Sun", "Jupiter"],
    "Revenue": ["Jupiter", "Mercury", "Mars"],
    "Social Welfare": ["Venus", "Jupiter"],
    "Supplies": ["Mercury", "Jupiter"],
    "Technical Development": ["Jupiter", "Mercury", "Mars"],
    "Telephones": ["Jupiter", "Mercury", "Mars"],
    "Transport (Aviation)": ["Venus", "Mercury"],
    "Shipping": ["Venus", "Mercury", "Moon"],
    "Works and Housing": ["Mars", "Mercury", "Venus", "Jupiter"],
    "Secretary": ["Mercury", "Mars", "Jupiter", "Sun"],
    "Statistics": ["Saturn", "Mercury", "Jupiter"],
    "Technicians": ["Mars", "Mercury"],
    "Clerk": ["Mercury"],
    "Typist": ["Mars", "Mercury", "Saturn"],
    "Shorthand Typist": ["Mercury", "Mars"],
    "Peon": ["Saturn"],
    "Camp Clerk": ["Mercury", "Venus"],
    "Geology": ["Saturn", "Mars"],
    "Advocate": ["Mercury", "Jupiter"],
    "Judge": ["Mars", "Jupiter", "Venus", "Sun"],
    "Registrar": ["Mars", "Jupiter", "Mercury", "Sun"],
    "Public Prosecutor": ["Mercury", "Jupiter", "Sun"],
    "Advocate General": ["Mars", "Mercury", "Jupiter","Sun"],
    "Registrar for Marriage": ["Mars", "Mars", "Venus","Sun"],
    "Bank Agent": ["Mars","Mercury", "Jupiter"],
    "Bank Accountant": ["Jupiter", "Mercury"],
    "Bank Foreign Exchange": ["Jupiter", "Mercury"],
    "Security Department": ["Jupiter", "Saturn","Mars", "Mercury"],
    "Scientific Research": ["Venus", "Mercury"],
    "Physical Education": ["Jupiter", "Sun", "Venus"],
    "Drawing Master": ["Saturn", "Venus", "Mercury", "Jupiter"],
    "Draftsman": ["Saturn", "Venus", "Mercury"]
    
}

SIGN_LORD = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn",
        "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

# Sign index mapping
SIGN_INDEX = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
    "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
    "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
}

# Rasi lords
RASI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Own signs for each planet
OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
    "Rahu": {"Aquarius"},
    "Ketu": {"Scorpio"}
}

# Exaltation signs
EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Gemini",
    "Ketu": "Sagittarius"
}

# Debilitation signs
DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Sagittarius",
    "Ketu": "Gemini"
}

# Benefics and Malefics
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu"}
FRUITFUL_SIGNS = {"Taurus", "Cancer", "Scorpio", "Pisces", "Sagittarius"}
UPACHAYA_HOUSES = {3, 6, 10, 11}

# Aspect specifications
ASPECT_SPECS = {
    "Conjunction": {"angle": 0, "orb": 8.0},
    "Opposition": {"angle": 180, "orb": 6.0},
    "Trine": {"angle": 120, "orb": 6.0},
    "Square": {"angle": 90, "orb": 6.0},
    "Sextile": {"angle": 60, "orb": 4.0},
    "Quincunx": {"angle": 150, "orb": 3.0},
}

# Combustion orbs
COMBUSTION_ORB = {
    "Moon": 12, "Mars": 17, "Mercury": 14,
    "Jupiter": 11, "Venus": 10, "Saturn": 15,
}

# Directional strength houses
DIG_BALA_HOUSES = {
    "Jupiter": 1, "Mercury": 1, "Sun": 10, "Mars": 10,
    "Saturn": 7, "Venus": 4, "Moon": 4,
}


def normalize_planet_name(s: str) -> Optional[str]:
    """Normalize planet name to standard format"""
    if not s:
        return None
    s = str(s).strip()
    mapping = {
        "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury",
        "Ju": "Jupiter", "Ve": "Venus", "Sa": "Saturn",
        "Ra": "Rahu", "Ke": "Ketu",
        "Sun": "Sun", "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury",
        "Jupiter": "Jupiter", "Venus": "Venus", "Saturn": "Saturn",
        "Rahu": "Rahu", "Ketu": "Ketu", "Ascendant": "Ascendant"
    }
    key = s.title()
    if key in mapping:
        return mapping[key]
    if s[:2].title() in mapping:
        return mapping[s[:2].title()]
    return key


def normalize_planet(name: str) -> str:
    """Alias for normalize_planet_name"""
    return normalize_planet_name(name) or name


def dms_to_decimal(dms: Any) -> float:
    """Convert degrees:minutes:seconds to decimal"""
    if dms is None:
        return 0.0
    if isinstance(dms, (float, int)):
        return float(dms)
    s = str(dms).strip()
    if ":" not in s:
        try:
            return float(s)
        except:
            return 0.0
    parts = s.split(":")
    d = float(parts[0]) if parts[0] else 0.0
    m = float(parts[1]) if len(parts) > 1 and parts[1] else 0.0
    sec = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
    return d + m / 60.0 + sec / 3600.0


def normalize_deg_360(x: float) -> float:
    """Normalize degree to 0-360 range"""
    g = x % 360.0
    if g < 0:
        g += 360.0
    return g


def deg_diff(d1: float, d2: float) -> float:
    """Calculate shortest angular distance between two degrees"""
    diff = abs(d1 - d2)
    if diff > 180:
        diff = 360 - diff
    return diff


def get_planet(name: str, planets: Dict) -> Optional[Dict]:
    """Get planet data by name"""
    norm = normalize_planet_name(name)
    if not norm or not isinstance(planets, dict):
        return None
    # Direct lookup
    if norm in planets:
        return planets[norm]
    # Case-insensitive search
    for k, v in planets.items():
        if normalize_planet_name(k) == norm:
            return v
    return None


def is_dual_sign(rasi: str) -> bool:
    return rasi in {'Gemini', 'Virgo', 'Sagittarius', 'Pisces'}


def is_even_sign(rasi: str) -> bool:
    return rasi in {'Taurus', 'Cancer', 'Virgo', 'Scorpio', 'Capricorn', 'Pisces'}


def is_odd_sign(rasi: str) -> bool:
    return rasi in {'Aries', 'Gemini', 'Leo', 'Libra', 'Sagittarius', 'Aquarius'}


def is_barren_sign(rasi: str) -> bool:
    return rasi in {'Aries', 'Leo', 'Virgo'}


def is_mute_sign(rasi: str) -> bool:
    return rasi in {'Cancer', 'Scorpio', 'Pisces'}


def is_movable_sign(sign: str) -> bool:
    return sign in {"Aries", "Cancer", "Libra", "Capricorn"}


def is_fixed_sign(sign: str) -> bool:
    return sign in {"Taurus", "Leo", "Scorpio", "Aquarius"}


def is_saturn_sign(sign: str) -> bool:
    return sign in {"Capricorn", "Aquarius"}


def is_masculine_rasi(sign: str) -> bool:
    masculine = {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"}
    return str(sign).title() in masculine


def is_feminine_rasi(sign: str) -> bool:
    feminine = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}
    return str(sign).title() in feminine

def in_saturn_navamsa(p):
    """
    If D9 sign available → check Saturn signs.
    If not → return False safely.
    """
    if not p:
        return False
    
    d9 = p.get("navamsa_sign") or p.get("d9_sign")
    if not d9:
        return False

    return str(d9).title() in {"Capricorn", "Aquarius"}

def longitude_to_rasi(deg):
    signs = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ]
    d = float(deg) % 360
    index = int(d // 30)
    return signs[index]

def get_lagna_longitude(planets):
    # Usually stored as Ascendant in planets dict
    asc = planets.get("Ascendant") or planets.get("Asc")
    return get_longitude(asc)

def _is_benefic(p):
    """Simple benefic classifier used in classical rules."""
    return normalize_planet((p or {}).get("name")) in BENEFICS

def is_connected_to_house(planet_name, house_no, houses,planets):
    pname = normalize_planet(planet_name)
    p = get_planet(pname, planets)
    if not p:
        return False

    # (1) Planet signifies the house directly
    sigs = get_signified_houses(pname, planets, houses)
    if house_no in sigs:
        return True

    # (2) Planet aspects the house ruler
    lord = _lord_of(house_no, houses)
    if lord:
        lp = get_planet(lord, planets)
        if lp and (_aspected_by(p, lord) or _aspected_by(lp, pname)):
            return True

    return False

def get_lagna_sign(planets):
    asc = planets.get("Ascendant") or planets.get("Asc")
    if not asc:
        return None
    sign = asc.get("sign") or asc.get("rasi") or asc.get("pseudo_rasi")
    return str(sign).title() if sign else None

def is_debilitated(p):
    """
    Returns True if a planet is in its debilitation sign.
    Uses DEBILITATION table (opposite of exaltation).
    """
    if not p:
        return False

    name = normalize_planet(p.get("name"))
    if name not in DEBILITATION:
        return False

    sign = p.get("sign") or p.get("rasi") or p.get("pseudo_rasi")
    if not sign:
        return False

    return str(sign).title() == DEBILITATION[name]

def masculine_planets() -> set:
    """
    KP gender classification:
    Masculine planets indicate male-child tendency
    """
    return {
        "Sun",
        "Mars",
        "Jupiter"
    }

def feminine_planets() -> set:
    """
    KP gender classification:
    Feminine planets indicate female-child tendency
    """
    return {
        "Moon",
        "Venus"
    }


def aspects(p, house_no, houses):
    """
    A lightweight house-aspect approximation.
    Uses planet aspects computed by _aspected_by().
    """
    if not p:
        return False

    # get lord of that house
    lord = _lord_of(house_no, houses)
    if not lord:
        return False

    # if planet aspects the house lord
    return _aspected_by(p, lord)

def get_longitude(p):
    if not p or not isinstance(p, dict):
        return 0.0
    
    if isinstance(p.get("global_degree"), (int, float)):
        return float(p["global_degree"])

    if isinstance(p.get("degree"), (int, float)):
        return float(p["degree"])

    fd = p.get("formatted_degree") or p.get("formatted_norm_degree")
    if isinstance(fd, str) and ":" in fd:
        try:
            d, m, s = fd.split(":")
            return float(d) + float(m)/60 + float(s)/3600
        except:
            return 0.0

    return 0.0

def _p(planets: Dict, name: str) -> Dict:
    """Safe planet fetch"""
    return get_planet(name, planets) or {}


def _in_house(p: Dict, h: int) -> bool:
    return bool(p) and p.get("house") == h


def _in_houses(p: Dict, hs: Set[int]) -> bool:
    return bool(p) and p.get("house") in hs


def _in_sign(p: Dict, signs: Set[str]) -> bool:
    if not p:
        return False
    sign = p.get("sign") or p.get("rasi") or p.get("pseudo_rasi")
    if not sign:
        return False
    return str(sign).title() in {s.title() for s in signs}


def _conjoined(a: Dict, b: Dict) -> bool:
    """Check if two planets are conjoined"""
    if not a or not b:
        return False
    
    house_a = a.get("house")
    house_b = b.get("house")
    
    if house_a and house_b and house_a == house_b:
        return True
    
    deg_a = a.get("global_degree")
    deg_b = b.get("global_degree")
    
    if deg_a is None or deg_b is None:
        return False
    
    orb = abs(deg_a - deg_b)
    if orb > 180:
        orb = 360 - orb
    
    return orb <= 8


def _lord_of(house: int, houses: List) -> Optional[str]:
    """Get the lord of a house"""
    for h in houses:
        if h.get("house") == house:
            rasi = h.get("start_rasi") or h.get("rasi")
            if rasi:
                return RASI_LORDS.get(rasi)
    return None


def get_cusp_sub_lord(house: int, houses: List) -> Optional[str]:
    """Get the sub-lord of a house cusp"""
    for h in houses:
        if h.get("house") == house:
            return normalize_planet_name(h.get("cusp_sub_lord"))
    return None


def is_combust(p: Dict, sun: Dict) -> bool:
    """Check if planet is combust"""
    if not p or not sun:
        return False
    name = normalize_planet_name(p.get("name"))
    if name not in COMBUSTION_ORB:
        return False
    d1 = p.get("global_degree")
    d2 = sun.get("global_degree")
    if not isinstance(d1, (int, float)) or not isinstance(d2, (int, float)):
        return False
    return deg_diff(d1, d2) <= COMBUSTION_ORB[name]


def has_dig_bala(p: Dict) -> bool:
    """Check if planet has directional strength"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name"))
    target_house = DIG_BALA_HOUSES.get(name)
    return bool(target_house and p.get("house") == target_house)


def _is_benefic(p) -> bool:
    """Check if planet is a benefic"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name") if isinstance(p, dict) else p)
    return name in BENEFICS


def _is_malefic(p) -> bool:
    """Check if planet is a malefic"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name") if isinstance(p, dict) else p)
    return name in MALEFICS


def _is_retrograde(p: Dict) -> bool:
    """Check if planet is retrograde"""
    if not p:
        return False
    return bool(p.get("is_retro") or p.get("retro"))


def _is_own_sign(p: Dict) -> bool:
    """Check if planet is in own sign"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name"))
    sign = str(p.get("sign") or p.get("rasi") or "").title()
    if not name or not sign:
        return False
    return sign in OWN_SIGNS.get(name, set())


def _is_exalted(p: Dict) -> bool:
    """Check if planet is exalted"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name"))
    sign = str(p.get("sign") or p.get("rasi") or "").title()
    return EXALTATION.get(name) == sign

def is_gulika_in_house(house_no: int, houses: list) -> bool:
    """
    Returns True if Gulika/Mandi is present in the given house.
    """
    for h in houses:
        if h.get("house") != house_no:
            continue

        # Case 1: Gulika explicitly listed
        if h.get("gulika") is True:
            return True

        # Case 2: Listed among planets
        planets = h.get("planets", [])
        if isinstance(planets, list):
            for p in planets:
                name = p.get("name") if isinstance(p, dict) else str(p)
                if name and name.lower() in {"gulika", "mandi"}:
                    return True

    return False

def is_in_kendra(planet: dict) -> bool:
    """
    Returns True if planet is in a Kendra house (1,4,7,10)
    """
    if not planet:
        return False
    return planet.get("house") in {1, 4, 7, 10}

def is_waning(moon: dict, planets: dict) -> bool:
    """
    Returns True if Moon is waning.
    Uses Moon–Sun longitudinal separation.
    """
    if not moon or not planets:
        return False

    moon_lon = moon.get("longitude")
    sun = planets.get("Sun")

    if moon_lon is None or not sun or sun.get("longitude") is None:
        return False

    sun_lon = sun["longitude"]
    diff = (moon_lon - sun_lon) % 360

    return diff > 180


def _is_debilitated(p: Dict) -> bool:
    """Check if planet is debilitated"""
    if not p:
        return False
    name = normalize_planet_name(p.get("name"))
    sign = str(p.get("sign") or p.get("rasi") or "").title()
    return DEBILITATION.get(name) == sign


def _create_chart_hash(planets: Dict) -> str:
    """
    Create a unique hash for a birth chart based on planet positions.
    This is used to cache API responses per chart.
    """
    import hashlib

    # Use planet positions to create a unique identifier
    # Sort planets to ensure consistent hash
    sorted_planets = sorted(planets.items())
    hash_data = ""

    for planet_name, planet_data in sorted_planets:
        if isinstance(planet_data, dict):
            # Use full_degree or global_degree as unique identifier
            degree = planet_data.get("full_degree") or planet_data.get("global_degree")
            if degree:
                hash_data += f"{planet_name}:{degree},"

    return hashlib.md5(hash_data.encode()).hexdigest()


def set_significator_cache(planets: Dict, api_data: Dict) -> None:
    """
    Cache the planetary significator table API response for a birth chart.
    Should be called once per chart when data is fetched from astro_engine.

    Args:
        planets: Planet dictionary from the chart
        api_data: Response from fetch_planetary_cuspal_significator_table API
    """
    chart_hash = _create_chart_hash(planets)
    with _CACHE_LOCK:
        _SIGNIFICATOR_CACHE[chart_hash] = api_data
        logger.debug(f"Cached significator data for chart {chart_hash}")


def get_significator_cache(planets: Dict) -> Optional[Dict]:
    """
    Retrieve cached planetary significator table for a birth chart.

    Args:
        planets: Planet dictionary from the chart

    Returns:
        Cached API data or None if not found
    """
    chart_hash = _create_chart_hash(planets)
    with _CACHE_LOCK:
        return _SIGNIFICATOR_CACHE.get(chart_hash)


def clear_significator_cache() -> None:
    """Clear all cached significator data. Useful for testing or memory management."""
    with _CACHE_LOCK:
        _SIGNIFICATOR_CACHE.clear()
        logger.debug("Cleared significator cache")


def _parse_significations_from_api(planet_name: str, api_data: Dict) -> Optional[Set[int]]:
    """
    Parse planetary significations from Divine API response.

    Args:
        planet_name: Name of the planet to get significations for
        api_data: Response from fetch_planetary_cuspal_significator_table API

    Returns:
        Set of house numbers signified by the planet, or None if parsing fails

    Expected API response structure:
    {
        "success": true,
        "data": {
            "planets": [
                {
                    "planet": "Sun",
                    "significations": [1, 5, 9]  # Example
                },
                ...
            ]
        }
    }
    """
    try:
        # Normalize planet name to match API format
        normalized_name = normalize_planet_name(planet_name)
        if not normalized_name:
            return None

        # Navigate to the data structure
        if not isinstance(api_data, dict):
            return None

        data = api_data.get("data", {})
        if not isinstance(data, dict):
            return None

        # Try different possible data structures the API might use
        # Structure 1: data.planets as list
        planets_list = data.get("planets", [])
        if isinstance(planets_list, list):
            for planet_entry in planets_list:
                if not isinstance(planet_entry, dict):
                    continue

                api_planet_name = planet_entry.get("planet") or planet_entry.get("name")
                if normalize_planet_name(api_planet_name) == normalized_name:
                    significations = planet_entry.get("significations") or planet_entry.get("houses")
                    if isinstance(significations, list):
                        # Filter to ensure we only have valid house numbers (1-12)
                        return {int(h) for h in significations if isinstance(h, (int, str)) and 1 <= int(h) <= 12}

        # Structure 2: data as direct planet mapping
        for key, value in data.items():
            if normalize_planet_name(key) == normalized_name:
                if isinstance(value, list):
                    return {int(h) for h in value if isinstance(h, (int, str)) and 1 <= int(h) <= 12}
                elif isinstance(value, dict):
                    significations = value.get("significations") or value.get("houses")
                    if isinstance(significations, list):
                        return {int(h) for h in significations if isinstance(h, (int, str)) and 1 <= int(h) <= 12}

        return None

    except Exception as e:
        logger.warning(f"Error parsing API significations for {planet_name}: {e}")
        return None


def get_signified_houses(planet_name: str, planets: Dict, houses: List) -> Set[int]:
    """
    Get houses signified by a planet using TRUE KP principles.

    Returns SET of house numbers (original signature).

    This function now uses API data when available (from Divine API),
    and falls back to custom logic if API data is not cached.

    KP Signification Hierarchy (custom logic):
    1. Sub lord's occupation + ownership (STRONGEST - final promise giver)
    2. Star lord's occupation + ownership (STRONG - modifier)
    3. Planet's own occupation (MEDIUM)
    4. Planet's own ownership (WEAKEST)
    5. Conjunctions (BONUS)
    """
    # Try to get API data from cache first
    api_data = get_significator_cache(planets)

    if api_data:
        # Use API data to extract significations
        signified = _parse_significations_from_api(planet_name, api_data)
        if signified:
            logger.debug(f"✅ Using API data for {planet_name} significations: {signified}")
            return signified
        else:
            logger.debug(f"⚠️ API data available but no significations found for {planet_name}, falling back to custom logic")

    # Fall back to custom logic (original implementation)
    logger.debug(f"Using custom logic for {planet_name} significations")
    weighted = get_signified_score(planet_name, planets, houses)
    return set(weighted.keys())


def get_signified_score(planet_name: str, planets: Dict, houses: List) -> Dict[int, float]:
    """
    Get signification scores for each house using TRUE KP principles.
    
    KP Signification Hierarchy (correct order):
    1. Sub lord's occupation + ownership (weight: 4.0 - STRONGEST)
    2. Star lord's occupation + ownership (weight: 3.0 - STRONG)
    3. Planet's own occupation (weight: 2.0 - MEDIUM)
    4. Planet's own ownership (weight: 1.0 - WEAKEST)
    5. Conjunctions (weight: 1.5 - BONUS)
    """
    weights = defaultdict(float)
    
    # Normalize planet name
    planet_name = normalize_planet_name(planet_name)
    if not planet_name:
        logger.warning(f"⚠️ Cannot normalize planet name")
        return dict(weights)
    
    planet = get_planet(planet_name, planets)
    if not planet:
        logger.warning(f"⚠️ Planet {planet_name} not found")
        return dict(weights)
    
    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------
    def add_house(h: int, w: float, reason: str = ""):
        """Add weight to a house with validation"""
        if isinstance(h, int) and 1 <= h <= 12:
            weights[h] += w
            if reason:
                logger.debug(f"  {reason}: house {h} → +{w}")
    
    def get_owned_houses(p_name: str) -> List[int]:
        """Get all houses owned by a planet"""
        owned = []
        for h in houses:
            rasi = h.get("start_rasi") or h.get("rasi") or h.get("sign")
            if not rasi:
                continue
            
            lord = RASI_LORDS.get(str(rasi).title())
            if lord and normalize_planet_name(lord) == p_name:
                owned.append(h["house"])
        return owned
    
    def basic_significations(p_obj: Dict, weight_key: str, label: str):
        """Get occupation + ownership significations for a planet"""
        if not p_obj:
            return
        
        w = KP_WEIGHTS[weight_key]
        p_name = normalize_planet_name(p_obj.get("name", ""))
        
        if not p_name:
            return
        
        # Occupation
        occ_house = p_obj.get("house")
        if occ_house:
            add_house(occ_house, w, f"{label} {p_name} occupies")
        
        # Ownership
        for owned_house in get_owned_houses(p_name):
            add_house(owned_house, w, f"{label} {p_name} owns")
    
    # ---------------------------------------------------------
    # S1: SUB LORD (STRONGEST - final promise giver)
    # ---------------------------------------------------------
    sl = planet.get("sub_lord")
    if sl:
        sl = normalize_planet_name(sl)
        if sl:
            sl_planet = get_planet(sl, planets)
            if sl_planet:
                logger.debug(f"  SUB LORD: {sl}")
                basic_significations(sl_planet, "sub", "SUB LORD")
    
    # ---------------------------------------------------------
    # S2: STAR LORD (STRONG - modifier)
    # ---------------------------------------------------------
    star = planet.get("nakshatra_lord")
    if star:
        star = normalize_planet_name(star)
        if star:
            star_planet = get_planet(star, planets)
            if star_planet:
                logger.debug(f"  STAR LORD: {star}")
                basic_significations(star_planet, "star", "STAR LORD")
    
    # ---------------------------------------------------------
    # S3: PLANET ITSELF - Occupation (MEDIUM)
    # ---------------------------------------------------------
    occ = planet.get("house")
    if occ:
        add_house(occ, KP_WEIGHTS["occupy"], f"{planet_name} occupies")
    
    # ---------------------------------------------------------
    # S4: PLANET ITSELF - Ownership (WEAKEST)
    # ---------------------------------------------------------
    for owned_house in get_owned_houses(planet_name):
        add_house(owned_house, KP_WEIGHTS["own"], f"{planet_name} owns")
    
    # ---------------------------------------------------------
    # S5: CONJUNCTION (BONUS)
    # ---------------------------------------------------------
    conjunctions = planet.get("conjunct", [])
    if conjunctions:
        for conj_name in conjunctions:
            conj_name = normalize_planet_name(conj_name)
            if conj_name:
                conj = get_planet(conj_name, planets)
                if conj:
                    conj_house = conj.get("house")
                    if conj_house:
                        add_house(conj_house, KP_WEIGHTS["conj"], 
                                f"{planet_name} conjunct {conj_name} in")
    
    # Convert to regular dict
    result = dict(weights)
    
    if result:
        logger.info(f"✅ {planet_name} KP signification scores: {result}")
    else:
        logger.warning(f"⚠️ {planet_name} has NO signification scores")
    
    return result

def _aspected_by(p: Dict, who: str, types: Optional[Set] = None) -> bool:
    """Check if planet is aspected by another"""
    if not p:
        return False
    
    who = normalize_planet_name(who)
    type_filter = set(types) if types else None
    
    # Check native API aspect list
    raw = p.get("aspected_by")
    if isinstance(raw, (list, tuple, set)):
        if who in {normalize_planet_name(x) for x in raw}:
            return True
    elif isinstance(raw, str):
        if normalize_planet_name(raw) == who:
            return True
    
    # Check computed aspects
    for other, atype, strength in p.get("aspects", []):
        if normalize_planet_name(other) != who:
            continue
        if type_filter and atype not in type_filter:
            continue
        return True
    
    return False


def has_harmonious_aspect(p: Dict, who) -> bool:
    """Check if planet has harmonious aspect from another"""
    if isinstance(who, str):
        return _aspected_by(p, who, {"Trine", "Sextile"})
    return _aspected_by(p, who.get("name"), {"Trine", "Sextile"}) if who else False


def _has_evil_aspect(p: Dict, who: Optional[Dict] = None) -> bool:
    if not p:
        return False

    if isinstance(who, str):
        return False  # ⛔ do NOT silently guess

    if who is not None and not isinstance(who, dict):
        return False
    
    if not p:
        return False
    if who:
        return _aspected_by(p, who.get("name"), {"Square", "Opposition"})
    for m in MALEFICS:
        if _aspected_by(p, m, {"Square", "Opposition"}):
            return True
    return False


def detect_aspects(planets: Dict) -> Dict:
    """Compute aspects for all planet pairs"""
    if not isinstance(planets, dict):
        return planets
    
    plist = [p for p in planets.values() 
             if isinstance(p, dict) and isinstance(p.get("global_degree"), (int, float))]
    
    # Clear old aspects
    for p in planets.values():
        if isinstance(p, dict):
            p["aspects"] = []
    
    # Pairwise evaluation
    for i in range(len(plist)):
        p1 = plist[i]
        n1 = normalize_planet_name(p1.get("name"))
        d1 = float(p1["global_degree"])
        
        for j in range(i + 1, len(plist)):
            p2 = plist[j]
            n2 = normalize_planet_name(p2.get("name"))
            d2 = float(p2["global_degree"])
            
            for asp_name, spec in ASPECT_SPECS.items():
                target, max_orb = spec["angle"], spec["orb"]
                delta = abs(deg_diff(d1, d2) - target)
                
                if delta <= max_orb:
                    strength = round(max_orb - delta, 2)
                    p1["aspects"].append((n2, asp_name, strength))
                    p2["aspects"].append((n1, asp_name, strength))
    
    return planets


def kp_check_promise(
    planets: Dict,
    houses: List,
    csl_house: int,
    promise_houses: Set[int],
    obstacle_houses: Set[int]
) -> Dict[str, Any]:
    """Check KP promise for a cusp"""
    sub_lord = get_cusp_sub_lord(csl_house, houses)
    logger.info(f"KP Promise Check: CSL House {csl_house}, Sub-Lord: {sub_lord}")
    if not sub_lord:
        return {"state": "unknown", "sub_lord": None}
    
    scores = get_signified_score(sub_lord, planets, houses)
    
    promise_score = sum(scores.get(h, 0) for h in promise_houses)
    obstacle_score = sum(scores.get(h, 0) for h in obstacle_houses)
    
    if promise_score > obstacle_score + 2:
        state = "promised"
    elif obstacle_score > promise_score + 2:
        state = "blocked"
    elif promise_score > 0 and obstacle_score > 0:
        state = "promised_with_obstacles"
    else:
        state = "neutral"
    
    return {
        "state": state,
        "sub_lord": sub_lord,
        "promise_score": promise_score,
        "obstacle_score": obstacle_score
    }


def get_spouse_direction_from_sign(sign: str) -> str:
    """Get spouse direction from 7th house sign (KP Book reference)"""
    mapping = {
        "Aries": "East",
        "Taurus": "South-East",
        "Gemini": "North",
        "Cancer": "North-West",
        "Leo": "East",
        "Virgo": "South",
        "Libra": "West",
        "Scorpio": "North",
        "Sagittarius": "East",
        "Capricorn": "South",
        "Aquarius": "West",
        "Pisces": "North-East",
    }
    return mapping.get(sign, "Unknown")


def get_spouse_nature_from_planet(pl: str) -> Optional[str]:
    """Get spouse nature traits from planet"""
    traits = {
        "Sun": "proud, authoritative, status-conscious",
        "Moon": "emotional, caring, changeable",
        "Mercury": "communicative, youthful, analytical",
        "Venus": "charming, artistic, pleasure-loving",
        "Mars": "assertive, competitive, impulsive",
        "Jupiter": "wise, supportive, ethical",
        "Saturn": "serious, dutiful, disciplined",
        "Rahu": "unconventional, ambitious, worldly",
        "Ketu": "detached, spiritual, research-oriented",
    }
    return traits.get(pl)


# Age difference mapping based on nakshatra lord of 7th cusp
SPOUSE_AGE_DIFFERENCE_MAP = {
    "Saturn": "large age gap; partner likely older",
    "Jupiter": "proper age difference",
    "Venus": "proper age difference",
    "Sun": "proper age difference",
    "Mars": "very small age gap",
    "Mercury": "very small age gap",
    "Moon": "very small age gap",
    "Rahu": "unconventional age difference",
    "Ketu": "karmic age connection"
}


def resolve_rahu_ketu_sub_lord(planets: Dict, houses: List, sub: str) -> str:
    """
    KP Rule: Rahu/Ketu always act through their nakshatra lord.
    They never give independent results in sub-lord judgment.
    
    Returns the effective planet whose nature should be used.
    """
    sub = normalize_planet(sub)
    if sub not in ("Rahu", "Ketu"):
        return sub
    
    rk = get_planet(sub, planets)
    if not rk:
        return sub
    
    # Primary: Nakshatra lord (ALWAYS USED IN KP)
    nak_lord = rk.get("nakshatra_lord")
    if nak_lord:
        return normalize_planet(nak_lord)
    
    # Fallback: Sign lord (rare, only if no nakshatra-lord)
    sign = rk.get("sign") or rk.get("rasi") or rk.get("pseudo_rasi")
    if sign:
        lord = RASI_LORDS.get(sign)
        if lord:
            return normalize_planet(lord)
    
    # If absolutely nothing available, return itself
    return sub


def get_detailed_spouse_traits(planet: str, sign: str) -> Optional[str]:
    """
    Get detailed spouse traits from SPOUSE_CHARACTER_BOOK.
    Based on KP Stellar Astrology - describes partner personality
    based on 7th sub-lord planet and its sign position.
    
    Args:
        planet: The effective sub-lord planet (after Rahu/Ketu resolution)
        sign: The sign where the planet is placed
    
    Returns:
        Detailed description of partner traits, or None if not found
    """
    return SPOUSE_CHARACTER_BOOK.get(planet, {}).get(sign)


def has_harsh_aspect(p: Dict, who, max_orb: float = None) -> bool:
    """
    Check if planet p receives a harsh aspect (Square or Opposition) from 'who'.
    
    Args:
        p: Planet dict to check
        who: Planet name or dict to check aspect from
        max_orb: Optional maximum orb for aspect
    
    Returns:
        True if harsh aspect exists
    """
    return _aspected_by(p, who, types={"Square", "Opposition"})


def _has_good_aspect(p: Dict) -> bool:
    """
    Check if planet receives benefic trine/sextile aspect from any benefic.
    
    Args:
        p: Planet dict to check
    
    Returns:
        True if receives good aspect from any benefic
    """
    if not p:
        return False
    for b in BENEFICS:
        if _aspected_by(p, b, types={"Trine", "Sextile"}):
            return True
    return False


def _house_has_benefic_occupation(hnum: int, houses: List) -> bool:
    """
    Check if house has benefic planet occupation.
    
    Args:
        hnum: House number to check
        houses: List of house dicts
    
    Returns:
        True if benefic occupies the house
    """
    h = next((x for x in houses if x.get("house") == hnum), None)
    if not h:
        return False
    
    for p in h.get("planets", []):
        name = normalize_planet(p.get("name"))
        if name in BENEFICS:
            return True
    
    return False


def _benefic_by_lordship_of_house(hnum: int, houses: List) -> bool:
    """
    Check if house lord is a natural benefic.
    
    Args:
        hnum: House number to check
        houses: List of house dicts
    
    Returns:
        True if house lord is a benefic
    """
    h = next((x for x in houses if x.get("house") == hnum), None)
    if not h:
        return False
    
    sign = str(
        h.get("start_rasi") or h.get("rasi") or h.get("pseudo_rasi") or ""
    ).title()
    
    lord = RASI_LORDS.get(sign)
    return normalize_planet(lord) in BENEFICS

def normalize_planets_raw(planets_raw: List[Dict[str,Any]]) -> Dict[str, Dict[str,Any]]:
    """
    Convert new vendor planets list -> dict keyed by full planet name with expected fields.
    """
    out = {}
    for p in planets_raw or []:
        # name normalization
        raw_name = p.get("name") or p.get("full_name") or p.get("symbol")
        name = normalize_planet_name(raw_name)
        # full_degree may be string; cast
        full_deg = None
        try:
            full_deg = float(p.get("full_degree")) if p.get("full_degree") is not None else None
        except:
            # sometimes full_degree is missing; try compute from sign + longitude dms
            l = p.get("longitude")
            if l:
                # local within-sign
                local = dms_to_decimal(l)
                base = SIGN_BASE.get(p.get("sign") or p.get("rasi") or "", 0)
                full_deg = normalize_deg_360(base + local)
        # local degree: prefer parsing longitude D:M:S
        local_deg = None
        try:
            local_deg = dms_to_decimal(p.get("longitude")) if p.get("longitude") else None
        except:
            local_deg = None

        # sign number / sign name
        sign = p.get("sign") or p.get("rasi") or p.get("zodiac") or None
        sign_no = p.get("sign_no") or p.get("rasi_no") or None
        # retro/combst flags
        retro = False
        if str(p.get("is_retro")).lower() in ("true","1","yes"):
            retro = True
        combust = False
        if str(p.get("is_combusted")).lower() in ("true","1","yes"):
            combust = True

        # house index (if returns)
        house = None
        try:
            house = int(p.get("house")) if p.get("house") is not None else None
        except:
            house = None

        out[name] = {
            "name": name,
            "full_degree": full_deg,
            "global_degree": full_deg,            # old code sometimes uses global_degree
            "local_degree": local_deg,
            "longitude": p.get("longitude"),
            "sign": sign,
            "rasi_no": int(sign_no) if sign_no is not None else None,
            "house": house,
            "nakshatra": p.get("nakshatra"),
            "nakshatra_pada": p.get("nakshatra_pada"),
            "nakshatra_no": p.get("nakshatra_no"),
            "nakshatra_lord": normalize_planet_name(p.get("nakshatra_lord")),
            "sub_lord": normalize_planet_name(p.get("sub_lord")),
            "sub_sub_lord": normalize_planet_name(p.get("sub_sub_lord")),
            "is_retro": retro,
            "is_combusted": combust,
            "speed": float(p.get("speed") or 0.0)
        }
    return out

def normalize_planet_in_houses(planet_in_houses_raw, houses=None):
    out = {}
    for k, v in (planet_in_houses_raw or {}).items():
        full_deg = float(v.get("full_degree")) if v.get("full_degree") else None

        # 🔥 recompute house using cusps if available
        house_no = int(k)
        if houses and full_deg is not None:
            for h in houses:
                s = h["global_start_degree"]
                e = h["global_end_degree"]
                if s <= e:
                    if s <= full_deg <= e:
                        house_no = h["house"]
                        break
                else:  # wrap-around
                    if full_deg >= s or full_deg <= e:
                        house_no = h["house"]
                        break

        out[str(house_no)] = {
            "house": house_no,
            "sign_no": int(v.get("sign_no")) if v.get("sign_no") else None,
            "full_degree": full_deg,
            "planet": v.get("planet", []) or []
        }
    return out


def assign_bhava_house(planet_degree, houses):
    if planet_degree is None:
        return None

    for h in houses:
        start = h["global_start_degree"]
        end = h["global_end_degree"]

        if start <= end:
            if start <= planet_degree < end:
                return h["house"]
        else:
            if planet_degree >= start or planet_degree < end:
                return h["house"]

    return None

def normalize_cusps_full(cusps_raw: Dict[str,Any], planet_in_houses_norm: Dict[str,Any]=None) -> List[Dict[str,Any]]:
    """
    Convert cusps 'table_data' into full list of 12 house dicts (old vendor format).
    Uses cuspal_response["data"]["table_data"] where each cusp has house_cusp.sign and degree (D:M:S).
    planet_in_houses_norm optional used to attach planets lists.
    """
    # first build a map of cusp global start degrees and metadata
    cusp_meta = {}
    for k, c in (cusps_raw or {}).items():
        try:
            hn = int(k)
        except:
            hn = int(k)
        sign = (c.get("house_cusp") or {}).get("sign") or c.get("sign") or None
        degree_dms = (c.get("house_cusp") or {}).get("degree") or c.get("degree") or None
        local_degree = dms_to_decimal(degree_dms) if degree_dms is not None else None
        base = SIGN_BASE.get(sign, None)
        if base is None:
            # maybe sign provided as number? try mapping if so
            base = None
        global_start = normalize_deg_360(base + local_degree) if base is not None and local_degree is not None else None

        cusp_meta[hn] = {
            "house": hn,
            "start_rasi": sign,
            "local_start_degree": local_degree,
            "global_start_degree": global_start,
            "rashi_lord": normalize_planet_name(c.get("rashi_lord")),
            "start_nakshatra": c.get("nakshatra"),
            "start_nakshatra_pada": c.get("nakshatra_pada"),
            "start_nakshatra_no": c.get("nakshatra_no"),
            "start_nakshatra_lord": normalize_planet_name(c.get("nakshatra_lord")),
            "cusp_sub_lord": normalize_planet_name(c.get("sub_lord")),
            "cusp_sub_sub_lord": normalize_planet_name(c.get("sub_sub_lord"))
        }

    # now build houses list 1..12 using next cusp start to compute end & length
    houses = []
    for i in range(1, 13):
        s = cusp_meta.get(i)
        n = cusp_meta.get(1 if i == 12 else i+1)
        if not s:
            raise ValueError(f"Missing cusp {i} in cusps_raw")
        # compute end using next cusp start — add 360 if wraps
        g_start = s["global_start_degree"]
        g_end = n["global_start_degree"]
        if g_start is None or g_end is None:
            raise ValueError("Cusp global degrees missing — cannot compute houses")
        g_end_linear = g_end
        if g_end_linear <= g_start:
            g_end_linear = g_end + 360.0
        length = g_end_linear - g_start
        bhavmadhya = g_start + length / 2.0
        # local end is next cusp's local start degree
        local_start = s["local_start_degree"]
        local_end = n["local_start_degree"]
        # attach planets from planet_in_houses if present
        planets_list = []
        if planet_in_houses_norm and str(i) in planet_in_houses_norm:
            # keep the raw list but normalize planet names inside list to standard full names
            raw_pls = planet_in_houses_norm[str(i)].get("planet") or []
            # raw_pls might be a list of dicts with name/symbol fields
            normalized_pls = []
            for rp in raw_pls:
                if isinstance(rp, dict):
                    nm = rp.get("name") or rp.get("full_name") or rp.get("symbol")
                    normalized_pls.append({
                        "name": normalize_planet_name(nm),
                        **{k:v for k,v in rp.items() if k not in ("name","full_name","symbol")}
                    })
                else:
                    # if simple string
                    normalized_pls.append({"name": normalize_planet_name(rp)})
            planets_list = normalized_pls

        house_obj = {
            "house": i,
            "start_rasi": s["start_rasi"],
            "end_rasi": n["start_rasi"],
            "end_rasi_lord": n.get("rashi_lord"),
            "local_start_degree": round(local_start, 6) if local_start is not None else None,
            "local_end_degree": round(local_end, 6) if local_end is not None else None,
            "length": round(length, 6),
            "bhavmadhya": round(normalize_deg_360(bhavmadhya), 6),
            "global_start_degree": round(normalize_deg_360(g_start), 6),
            "global_end_degree": round(normalize_deg_360(g_end if g_end_linear < 360 else (g_end_linear - 360)), 6),
            "start_nakshatra": s.get("start_nakshatra"),
            "end_nakshatra": n.get("start_nakshatra"),
            "start_nakshatra_lord": s.get("start_nakshatra_lord"),
            "end_nakshatra_lord": n.get("start_nakshatra_lord"),
            "cusp_sub_lord": s.get("cusp_sub_lord"),
            "cusp_sub_sub_lord": s.get("cusp_sub_sub_lord"),
            "rashi_lord": s.get("rashi_lord"),
            "planets": planets_list
        }
        houses.append(house_obj)
    return houses

def _is_strong_placement(p, accepted_houses):
    """
    p: planet dict
    accepted_houses: set of houses considered 'strong' for this rule
    Returns True if planet exists and sits in accepted_houses.
    """
    if not p or not isinstance(p, dict):
        return False
    h = p.get("house")
    return isinstance(h, int) and (h in accepted_houses)

def _idx_by_name_any(dct):
    """
    Convert D9 or planet-detail dict into:
        {NormalizedName: object}
    """
    idx = {}
    if isinstance(dct, dict):
        for v in dct.values():
            if isinstance(v, dict):
                nm = normalize_planet(v.get("full_name") or v.get("name"))
                if nm:
                    idx[nm] = v
    return idx

def _d9_get(d9, name):
    """Return D9 entry for planet <name>."""
    if not d9:
        return None
    nm = normalize_planet(name)
    return _idx_by_name_any(d9).get(nm)

def _is_strong_in_d9(planet_name, d9):
    """Strong in D9 if in own or exalted sign."""
    p = _d9_get(d9, planet_name)
    if not p:
        return False
    return _is_own_or_exalted_in_sign(planet_name, p.get("zodiac"))

def _is_own_or_exalted_in_sign(planet_name, sign):
    """Checks own-rasi OR exaltation sign."""
    n = normalize_planet(planet_name)
    s = str(sign or "").title()

    if not n or not s:
        return False

    if n in OWN_SIGNS and s in OWN_SIGNS[n]:
        return True
    return EXALTATION.get(n) == s

def _count_planets_in_house(planets, hnum, name_set=None):
    """
    Counts planets in a particular house.
    If name_set is provided → count only those planets.
    """
    c = 0
    for p in planets.values():
        if not isinstance(p, dict):
            continue

        if p.get("house") != hnum:
            continue

        if name_set is None:
            c += 1
        else:
            if normalize_planet(p.get("name")) in name_set:
                c += 1

    return c

def get_star_lord_of_planet(planet_name, planets):
    """
    Returns Nakshatra (Star) lord of a planet.
    Fully compatible with cached get_planet().
    """

    if not planet_name:
        return None

    p = get_planet(planet_name, planets)
    if not p or not isinstance(p, dict):
        return None

    star = (
        p.get("nakshatra_lord")
        or p.get("start_nakshatra_lord")
        or p.get("pseudo_nakshatra_lord")
    )

    return normalize_planet(star) if star else None

def _strong_sig(score_dict, houses_set, threshold=2):
    """Return True if sum of signification scores for `houses_set` >= threshold."""
    if not isinstance(score_dict, dict):
        return False
    return sum(int(score_dict.get(h, 0)) for h in houses_set) >= threshold

def _mutual_exchange(h1, h2, houses, planets):
    """
    Check Parivartana (Mutual Exchange) between two houses.
    h1 lord in h2 and h2 lord in h1.
    """
    l1 = _lord_of(h1, houses)
    l2 = _lord_of(h2, houses)
    if not l1 or not l2:
        return False

    p1 = _p(planets, l1)
    p2 = _p(planets, l2)
    if not p1 or not p2:
        return False

    return p1.get("house") == h2 and p2.get("house") == h1

def is_strict_income_sub(sub, planets, houses):
    """
    STRICT S1:
    True only if sub-lord STRONGLY signifies 2 / 4 / 11
    """
    if not sub:
        return False

    score = get_signified_score(sub, planets, houses)
    return any(score.get(h, 0) >= 2 for h in (2, 4, 11))


def is_strict_loss_sub(sub, planets, houses):
    """
    STRICT S1:
    True only if sub-lord STRONGLY signifies 6 / 8 / 12
    """
    if not sub:
        return False

    score = get_signified_score(sub, planets, houses)
    return any(score.get(h, 0) >= 2 for h in (6, 8, 12))

def suggest_remedies(domain, verdict, sub_lord, houses):
    """
    Final unified remedy engine (API ready):
        - Domain-specific remedies only (Marriage/Children/Career/etc)
        - KP Book-based marriage remedies included
        - Node remedies if sub-lord is Rahu/Ketu
        - Applies remedies ONLY for the domain
        - Provides WHEN to apply (obstacle vs promised)
    """

    remedies = []

    # --------------------------------------------------------
    # UNIVERSAL REMEDIES (safe, book-consistent, apply to all)
    # --------------------------------------------------------
    remedies.append("🕉️ Practice 10–15 minutes of daily meditation to stabilize Moon and reduce mental obstacles.")
    remedies.append("📿 Chant **Gayatri Mantra** 108 times daily for overall protection and clarity.")
    remedies.append("☀️ Offer water (Arghya) to **Sun** every morning to strengthen life-force and discipline.")

    # ========================
    #  DOMAIN-SPECIFIC REMEDIES
    # ========================

    # 1) -------------------- MARRIAGE ------------------------
    if domain.lower() == "marriage":

        # --- Book-specified “when obstacles exist” (KP Reader p. 29–31, 36–51) ---
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("💍 Strengthen **Venus** (only if benefic) with **Diamond/White Sapphire** to remove marriage delays.")
            remedies.append("🪔 On Fridays, worship Goddess **Durga** or recite **Durga Saptashati** for emotional harmony.")
            remedies.append("🍥 Donate white sweets or gifts to young girls on Fridays (classic Shukra remedy).")
            remedies.append("🌸 Keep white flowers at home on Fridays to pacify Venus.")
            remedies.append("🕯️ Light ghee lamp on Friday evenings to strengthen marital harmony.")

        # --- When marriage is promised (no major obstacles) ---
        else:
            remedies.append("✅ Observe **Friday fast** (Sukravar Vrat) to sustain marital harmony.")
            remedies.append("🌼 Offer white flowers to Goddess Lakshmi for peaceful partnership.")

        # --- Additional book-based triggers ---
        # If 7th cusp / Venus afflicted by 6/8/12 -> disputes
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("⚖️ Donate white rice, curd, or silver items on Fridays to reduce disputes in relationships.")

    # 2) -------------------- CHILDREN ------------------------
    elif domain.lower() == "children":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("👶 Wear **Yellow Sapphire** (if Jupiter benefic) for child blessing.")
            remedies.append("🍌 Donate turmeric, yellow fruits, or chana dal on Thursdays.")
            remedies.append("📿 Chant **'Om Brihaspataye Namah'** on Thursdays.")

        else:
            remedies.append("🙏 Worship **Bal Gopal (child Krishna)** for healthy progeny.")

    # 3) -------------------- CAREER ------------------------
    elif domain.lower() == "career":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("💼 Strengthen **Sun** with Ruby (if benefic) for authority and success.")
            remedies.append("📘 Recite **Aditya Hridayam** daily for career breakthroughs.")
            remedies.append("🪔 Light sesame oil lamp on Saturdays to pacify Saturn.")

        else:
            remedies.append("🔥 Offer red cloth to Hanuman on Tuesdays for courage at work.")

    # 4) -------------------- HEALTH ------------------------
    elif domain.lower() == "health":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("🕯️ Daily **Maha Mrityunjaya Mantra** chanting (at least 21 or 108 times).")
            remedies.append("🥛 Donate milk, medicines, or care for the sick to improve Moon/Ascendant.")

        else:
            remedies.append("🌙 Fast on Mondays to strengthen Moon.")

    # 5) -------------------- PROPERTY ------------------------
    elif domain.lower() == "property":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("🏡 Strengthen **Mars** (if benefic) with Red Coral for property success.")
            remedies.append("🧱 Donate tools or red masoor dal on Tuesdays.")

        else:
            remedies.append("🙏 Worship Ganesha before signing property deals.")

    # 6) -------------------- FAMILY ------------------------
    elif domain.lower() == "family":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("🌙 Strengthen **Moon** with Pearl (if benefic) for family peace.")
            remedies.append("🥛 Donate milk/rice on Mondays.")

        else:
            remedies.append("🕊️ Keep a silver bowl of water in the bedroom for harmony.")

    # 7) -------------------- VEHICLES ------------------------
    elif domain.lower() == "vehicles":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("🚗 Strengthen **Mars** with Red Coral (if benefic).")
            remedies.append("🛞 Offer sindoor to Hanuman for safety from accidents.")

        else:
            remedies.append("🙏 Worship Hanuman and Ganesha before traveling.")

    # 8) -------------------- FOREIGN ------------------------
    elif domain.lower() == "foreign":
        if verdict in ["promised_with_obstacles", "blocked"]:
            remedies.append("🌍 Perform **Navagraha Puja** for Rahu/Ketu (foreign travel indicators).")
            remedies.append("🥿 Donate shoes/blankets to poor for Saturn/Rahu pacification.")
            remedies.append("🧿 Chant 'Om Rahave Namah' before major travel.")

        else:
            remedies.append("📿 Carry Tulsi mala while traveling for protection.")

    # --------------------------------------------------------
    # RAHU/KETU SUB-LORD SPECIAL REMEDIES (KP READER)
    # --------------------------------------------------------
    if sub_lord in ["Rahu", "Ketu"]:
        remedies.append("☸️ Perform **Navagraha Puja** (mandatory for Rahu/Ketu afflictions).")
        remedies.append("🕉️ Chant **'Om Raam Rahave Namah'** / **'Om Ketave Namah'** 108 times daily.")
        remedies.append("🐕 Feed stray dogs (Rahu) or donate blankets (Ketu).")

    return remedies

def get_house_of(planets, name):
    p = get_planet(name, planets)
    return p.get("house") if isinstance(p, dict) else None

def _is_strong_planet(p: Dict, planets: Dict) -> bool:
    """
    Check if planet is strongly placed (own sign, exalted, or in kendra/trikona).
    
    Args:
        p: Planet dict to check
        planets: All planets dict
    
    Returns:
        True if planet is strongly placed
    """
    if not p:
        return False
    
    # Own sign or exalted
    if _is_own_sign(p) or _is_exalted(p):
        return True
    
    # In kendra (1, 4, 7, 10) or trikona (1, 5, 9)
    house = p.get("house")
    if house in {1, 4, 5, 7, 9, 10}:
        return True
    
    return False


# Detailed spouse character descriptions from KP Stellar Astrology
# Based on the 7th cusp sub-lord's planet and sign position
SPOUSE_CHARACTER_BOOK = {
    "Sun": {
        "Aries": "Middle stature, strong and well-made, complexion good, full eyes; bold, noble, will assert his right, comes out victorious, proud, social success.",
        "Taurus": "Short and well set. Not very fair, broad mouth, broad face, strong sportsman or athletic, over-confident, not proud, good debater, argues well and wins.",
        "Gemini": "Above average in height, well proportioned body, moderate complexion, long nose, piercing eye, most courteous, tactful, accommodative, can be influenced by others, pleasing manners.",
        "Cancer": "Short stature, repulsive face, not beautiful. Temperament good, harmless, cheerful, fond of music, dance, sports, lazy, does not like to work.",
        "Leo": "Strong well-built, moderate complexion, big eyes, round and big face, most faithful and reliable, very punctual always, fair and just in his actions, ambitious and successful.",
        "Virgo": "Tall person with slender stature and good complexion very dark hair, fond of music and ever singing, always smiling and never provoking, cheerful, pleasant, spends much time on recreations.",
        "Libra": "Tall, straight upright body. Big eyes, thin hair, beautiful, never bold but ever talking about war, riot, etc. not much reliable, weak in attachments.",
        "Scorpio": "Square built, fleshy, full growth, broad face, moderate complexion, ingenious, very clever, discoverer, very brisk, ambitious, never accepts defeat. Fortunate.",
        "Sagittarius": "Tall, beautiful, body well proportioned, face oval, over-estimates one's ability, austere, severe, plans for big things.",
        "Capricorn": "Thin built, lean, wiry, tall long nose, soft hair sickly appearance, pleasing manners, nasty occasionally, makes many friends, commands others goodwill.",
        "Aquarius": "Tall, well made, round face, good complexion, tolerably good disposition, never deceitful, proud, ostentatious.",
        "Pisces": "Short, stout, protruded eyes, plumpy body, long nose, good complexion, fond of pleasures, extravagant."
    },
    "Moon": {
        "Aries": "Fleshy and plumpy, round face, fair complexion, adamant, aggressive, argumentative, avaricious, aspiring, ambitious, authoritative.",
        "Taurus": "Strong well-built body, just below average in height, good looking, fair complexion, polite, modest, moderate fair, honest, helpful, pleasing.",
        "Gemini": "Tall, well built, upright, good complexion, ingenious, unsteady, lacks decision, not fortunate in profession.",
        "Cancer": "Average height, well built, little fleshy person, rounded face, moderate complexion, can be easily influenced, changeable, pleasant manners, harmless, cares more for peace, fond of company, fortunate, fond of traveling.",
        "Leo": "Well built, average height, moderate complexion, big eyes, proud, ambitious, never desires to be submissive and serve as a subordinate, independent.",
        "Virgo": "Tall, face oval, good complexion, very clever, reserved, gloomy, unlucky, depressed.",
        "Libra": "Tall good personality, beautiful, good complexion, humorous, witty pleasant, ever-smiling, fond of amusements, cares more for appreciation from the other sex.",
        "Scorpio": "Below average in height, stout, complexion not good, most impulsive and irregular, not a desirable partner always.",
        "Sagittarius": "Beautiful, honest, true, person with well-built body and oval face, generous, hasty and passionate, lucky.",
        "Capricorn": "Thin weak body, complexion not good, health poor, tall-bushy hair growth, most dull, inactive, pessimistic, selfish.",
        "Aquarius": "Moderate in height, well made, good complexion, very intelligent, fit to carry on research, most courteous and never offensive, studious.",
        "Pisces": "Below average, plumpy, fleshy, fat bloated face, most inactive, active only for pleasure. Unsteady, inconstant and unfortunate."
    },
    "Mars": {
        "Aries": "Moderate height, well built, large bones, curling hair, dark complexion, very bold, rash, undaunted, over-confident, very proud, quarrelsome, ever gains.",
        "Taurus": "Moderate height, strong and well-built rough and coarse hair, moderate complexion, broad mouth and face, self-indulgence, arrogant, speculative, unfortunate.",
        "Gemini": "Very tall, complexion not good, well-proportioned body always active, mischievous, restless, clever, cunning, changes residence often.",
        "Cancer": "Short, dusky complexion, less of hair, crooked body, unreliable, unfortunate, unhealthy practices.",
        "Leo": "Tall, well-built, oval face, dark complexion, stout hands and legs, yet very brisk and active, fond of sports, riding, quarrelsome, likes to be in Police or military.",
        "Virgo": "Moderate height, well-built body, thick nose, dark complexion, hasty, impulsive, proud, passionate, vindictive, retaliates.",
        "Libra": "Tall, beautiful, oval face, red complexion, active, alert, hopeful and cheerful, self-boasting, haughty, dresses well, attached to other sex.",
        "Scorpio": "Stout, bulky, dark complexion, curling hair, broad face, rash, not sociable, vindictive, revengeful, fond of disputes and quarrel, proud, very intelligent.",
        "Sagittarius": "Tall, well-proportioned body, red complexion, oval face, piercing eyes, hopeful, jovial, cheerful, quick, speedy, bold, talkative.",
        "Capricorn": "Short, lean, thin face, dark complexion, witty, humorous, intelligent, lucky, pushy and successful.",
        "Aquarius": "Well built body, good complexion, fair and buoyant, a good debater, argues and fortunate always.",
        "Pisces": "Below average height, dark complexion, not beautiful, dirty look, dull, self-indulging, idle, careless, unfortunate."
    },
    "Mercury": {
        "Aries": "Moderate in height and stature, thin body, face oval, hair brown, complexion dull, very quick in thinking and speaking, expressive, liberal, inventive, impulsive, clever, studious.",
        "Taurus": "Stout body, strong, good health, black complexion. Short and thick hair, a little lazy, happy disposition, fond of opposite sex, artist, determined, diplomatic.",
        "Gemini": "Tall, well built, brown hair, complexion good, intelligent, orator, clever, lawyer or agent, inventive, resourceful, generous, good humored, versatile.",
        "Cancer": "Short, stout, complexion not good, eyes small, nose sharp, hair dark, ever variable, never steady, little lazy, tactful, faithful, sociable, cares for pleasure.",
        "Leo": "Robust health, weak body, good stature, dark complexion, brown hair, round face, broad eyes, persistent, quick tempered, kind hearted, ambitious, intuition, organising capacity.",
        "Virgo": "Tall, lean, brown hair, complexion not attractive, very intelligent, cautious, practical, prudent, intuitive, scholar, good writer, well informed.",
        "Libra": "Tall, strong but thin brown hair, moderate complexion, broad outlook, dispassionate. Good judge, artist, invention, good in mathematics, social life.",
        "Scorpio": "Short, not good to look at, broad shoulder, dark complexion, brown hair, stubborn, obstinate, positive, reckless, fond of opposite sex, critical, suspicious.",
        "Sagittarius": "Tall, well built, large thick bones, face oval, dark complexion, long nose, sincere, just, independent, rebellious, prophetic mind, active mentally, authoritative.",
        "Capricorn": "Thin, not well built, face also thin, dark complexion, hair brown and thin, irritable, dissatisfied, disappointed, unfortunate, suspicious nature, painstaking, studious.",
        "Aquarius": "Moderate stature, good health, attractive appearance, dark hair, fair, original thoughts, penetrative, comprehensive, humanitarian, can concentrate, fond of occult subjects.",
        "Pisces": "Short, stout, pale, hair brownish, intuitive, understands matters quickly, versatile, good memory, psychic ability, analytical mind, very clever."
    },
    "Jupiter": {
        "Aries": "Not plumpy but stature is middle, expressive eyes, high nose, pimples in the face, progressive, generous, ardent, philosophical, social, noble, polite, studious, fond of traveling, sports, fortunate.",
        "Taurus": "Moderate height, stout, good health, affectionate, reserved, steady, cannot be influenced, rarely travels, religious, gains through opposite sex, early marriage, dutiful partner.",
        "Gemini": "Well-built, little stout, good complexion, dark hair, penetrating eyes, sympathetic, benevolent, friendly, trustworthy, travels, broad-outlook, restless, studious.",
        "Cancer": "Stout, short, pale and anaemic, complexion not good, plumpy, disproportionate, charitable, enterprising, sympathetic, popular, intuitive, imaginative, artist, patriot.",
        "Leo": "Strong, well-built, tall, round face, curling dark hair, big eyes, beautiful, broad-outlook, noble, prudent, loyal, generous, prestige, intuitive, diplomatic.",
        "Virgo": "Good height, well-built, beautiful, black hair, above average in height, fair complexion, intelligent, cautious, prudent, philosophy, scientific, analytical, wise, honest.",
        "Libra": "Good growth, robust health, handsome, tall, good complexion, oval face, dark hair, moderate, earnest, obliging, imaginative, peaceful, charitable, fond of travel, artist, happy marriage.",
        "Scorpio": "Good health, well-built, beautiful, strong will, deep emotions, ambitious, perseverance, self confidence, analytical, psychic, research minded.",
        "Sagittarius": "Tall and upright, stout, good stature, oval face, brown hair, courteous, generous, tolerant, loyal, merciful, humanitarian, successful, sports.",
        "Capricorn": "Thin, below average, head also little small, dark brown thin hair, constructive, capable, creative, ambitious, powerful, economical, frugal, successful, public life.",
        "Aquarius": "Below average, tall, good health, brown hair, deep set eyes, good humored, sympathetic, hates quarrels, prophetic, good for astrology, spiritual life, independent views.",
        "Pisces": "Below average height, plumpy, stout, brown hair, pleasure in good company, strong will, emotional, imaginative, intuitive, studious, simple, unassuming, fond of travel, artistic."
    },
    "Venus": {
        "Aries": "Average height, thin body, thin hair, good appearance, scar in face, artist, fond of music, sculpture, travels, affectionate, fond of love, attracted to opposite sex, popular.",
        "Taurus": "Very good health, attractive face, proportionate body, little stout, emotional, affectionate, faithful, careful, precise, determined, saves money, enjoys life.",
        "Gemini": "Middle stature, good in appearance, fair complexion, dark hair, good humored, plurality of interests, several occupations, good writer, speaker, musician, intuitive, original, sociable.",
        "Cancer": "Short person, stout, round face sickly, thin hair, idle, loves home, attracted by family, fond of mother, kind heart, imaginative, several love affairs, secret activities, psychic powers.",
        "Leo": "Tall, well built, clear eyes, round face, fair skin, sympathetic, kind hearted, charitable, sincere, attractive, social, good in music or acting or any art, gains by speculation.",
        "Virgo": "Tall, well built, oval face, dark hair, intelligent, sympathetic, not fully satisfied in love affairs, secret attachment, gains through medicine, gardening.",
        "Libra": "Erect, straight, tall, beautiful person, well built, oval face, pleasing manners, ever smiling, brown hair, kind, sympathetic, affectionate, good companion, pleasant partner, artist, social broad outlook.",
        "Scorpio": "Short, stout, robust, broad face, black complexion, black hair, extravagant, lavish, impulsive, gains by gift or partnership, very passionate, emotional, troubles through opposite sex.",
        "Sagittarius": "Tall, well built, good complexion, fair long face, brown hair, refined nature, light hearted, impressionable, imaginative, intuitive, fond of journey, beauty, outdoor games.",
        "Capricorn": "Not well built, moderate height, pale figure, thin, looks sickly, dark hair, trustworthy, responsible, authoritative, business-like, banking, invests, ambitious, delayed marriage.",
        "Aquarius": "Beautiful, robust health, well built, fair complexion, big body, sympathetic, humanitarian, social, always fond of romance, sudden expenses in love, gains through friends.",
        "Pisces": "Moderate height, stout, spiritual, round face, very fair complexion, fair hair, affectionate, good companion, gains through opposite sex, imaginative, romantic, many love affairs."
    },
    "Saturn": {
        "Aries": "Black complexion, bony person, thin build, dull face, less of hair, self boasting, determined, very ambitious, good analytical brain, obstacles and troubles.",
        "Taurus": "Ugly appearance, stout, dark hair, profuse growth, fat, steady in mind, loses temper quickly, resentful, very economical, reserved, fond of horticulture, poultry, domestic life not fortunate.",
        "Gemini": "Tall, black, face not round, hair also black, intelligent, concentrates, can meditate, fond of science, mathematics, Statistics, Literature, trouble through cousins, litigations.",
        "Cancer": "Thin, not tall, weak health, sickly appearance, hair dark, deep set eyes, dissatisfaction, ever changes house, always changeable, depressed, no contentment, psychic powers, economical, industrious.",
        "Leo": "Tall, good health, broad face, big shoulders, dark hair, sunken eyes, generous, short beard, stubborn, God-fearing, spiritual, trouble through servants, meets with accidents, pains-taking, over-works.",
        "Virgo": "Tall, thin-build, black hair, long forehead, cautious, frugal, intuitive, reserved, much worried, not faithful, depressed, good for spiritual life, unfortunate in domestic affairs.",
        "Libra": "Tall, long face, dark hair, long nose, broad forehead, commands respect, scientific minded, inimical with opposite sex, disappointment in love affairs, separation, delayed marriage.",
        "Scorpio": "Moderate height, stout, big shoulder, dark hair, violent type, very passionate, self determined, jealous, disappointment in love affairs or secret activities, not happy with domestic life.",
        "Sagittarius": "Huge body, moderate complexion, obliging, helpful, fearless, humanitarian, occult science, philosophy, intuitive, detached nature, many obstacles, more than one occupation.",
        "Capricorn": "Lean, bony, black hair, average height, sunken cheek and eyes, always thinking, serious, cautious, reasonable, reserved, peevish, attachment with inferior friends, unhappy marriage.",
        "Aquarius": "Tall, big head and sunken eyes, brown hair, thoughtful, reserved, serious, intellectual, deep thinker, sociable, gains determined, faithful, romantic life.",
        "Pisces": "Moderate height, average complexion, big head, protruding eyes, teeth not well arranged, unfaithful friends, loss, deception, many disappointments, secret activities, unfortunate, worries."
    },
    "Rahu": {
        "Note": "If Rahu is 7th sub-lord, see its nakshatra lord for partner traits. Rahu acts through its constellation lord."
    },
    "Ketu": {
        "Note": "If Ketu is 7th sub-lord, see its nakshatra lord for partner traits. Ketu acts through its constellation lord."
    }
}



# Moolatrikona Signs and Degree Ranges
# A planet in moolatrikona is stronger than in own sign but weaker than exalted
MOOLATRIKONA = {
    "Sun": {"sign": "Leo", "start": 0, "end": 20},
    "Moon": {"sign": "Taurus", "start": 3, "end": 30},
    "Mars": {"sign": "Aries", "start": 0, "end": 12},
    "Mercury": {"sign": "Virgo", "start": 15, "end": 20},
    "Jupiter": {"sign": "Sagittarius", "start": 0, "end": 10},
    "Venus": {"sign": "Libra", "start": 0, "end": 15},
    "Saturn": {"sign": "Aquarius", "start": 0, "end": 20}
}

# Planet Friendships (Natural)
# Used to determine if a planet is in friendly/enemy sign
PLANET_FRIENDSHIPS = {
    "Sun": {
        "friends": {"Moon", "Mars", "Jupiter"},
        "enemies": {"Venus", "Saturn"},
        "neutral": {"Mercury"}
    },
    "Moon": {
        "friends": {"Sun", "Mercury"},
        "enemies": set(),
        "neutral": {"Mars", "Jupiter", "Venus", "Saturn"}
    },
    "Mars": {
        "friends": {"Sun", "Moon", "Jupiter"},
        "enemies": {"Mercury"},
        "neutral": {"Venus", "Saturn"}
    },
    "Mercury": {
        "friends": {"Sun", "Venus"},
        "enemies": {"Moon"},
        "neutral": {"Mars", "Jupiter", "Saturn"}
    },
    "Jupiter": {
        "friends": {"Sun", "Moon", "Mars"},
        "enemies": {"Mercury", "Venus"},
        "neutral": {"Saturn"}
    },
    "Venus": {
        "friends": {"Mercury", "Saturn"},
        "enemies": {"Sun", "Moon"},
        "neutral": {"Mars", "Jupiter"}
    },
    "Saturn": {
        "friends": {"Mercury", "Venus"},
        "enemies": {"Sun", "Moon", "Mars"},
        "neutral": {"Jupiter"}
    },
    "Rahu": {
        "friends": {"Venus", "Saturn"},
        "enemies": {"Sun", "Moon", "Mars"},
        "neutral": {"Mercury", "Jupiter"}
    },
    "Ketu": {
        "friends": {"Mars", "Jupiter"},
        "enemies": {"Moon", "Venus"},
        "neutral": {"Sun", "Mercury", "Saturn"}
    }
}

# Dignity Scores for Strength Calculation
DIGNITY_SCORES = {
    "exalted": 5,
    "moolatrikona": 4,
    "own_sign": 3,
    "friendly": 1.5,
    "neutral": 0,
    "enemy": -1.5,
    "debilitated": -3
}

# Combustion Orbs (degrees from Sun)
COMBUSTION_ORB = {
    "Moon": 12,
    "Mars": 17,
    "Mercury": 14,
    "Jupiter": 11,
    "Venus": 10,
    "Saturn": 15
}

# Domain-specific House Configuration
# Primary houses are most important, Secondary are supporting
DOMAIN_HOUSE_CONFIG = {
    "Marriage": {
        "primary": {7, 2, 11},
        "secondary": {5, 8},
        "karaka": "Venus",
        "description": "विवाह/Marriage"
    },
    "Career": {
        "primary": {10, 6, 2},
        "secondary": {11, 9},
        "karaka": "Saturn",
        "description": "करियर/Career"
    },
    "Finance": {
        "primary": {2, 11, 5},
        "secondary": {8, 12},
        "karaka": "Jupiter",
        "description": "वित्त/Finance"
    },
    "Health": {
        "primary": {1, 6, 8},
        "secondary": {12},
        "karaka": "Sun",
        "description": "स्वास्थ्य/Health"
    },
    "Children": {
        "primary": {5, 9, 11},
        "secondary": {2},
        "karaka": "Jupiter",
        "description": "संतान/Children"
    },
    "Foreign": {
        "primary": {9, 12, 3},
        "secondary": {4, 7},
        "karaka": "Rahu",
        "description": "विदेश/Foreign"
    },
    "Business": {
        "primary": {7, 10, 3},
        "secondary": {11, 5},
        "karaka": "Mercury",
        "description": "व्यापार/Business"
    },
    "Education": {
        "primary": {4, 5, 9},
        "secondary": {2, 11},
        "karaka": "Jupiter",
        "description": "शिक्षा/Education"
    },
    "Love_Relationship": {
        "primary": {5, 7, 11},
        "secondary": {2, 8},
        "karaka": "Venus",
        "description": "प्रेम/Love"
    },
    "Parenting": {
        "primary": {5, 9, 4},
        "secondary": {11, 2},
        "karaka": "Jupiter",
        "description": "पालन-पोषण/Parenting"
    },
    "General_Guidance": {
        "primary": {1, 9, 10},
        "secondary": {4, 7, 11},
        "karaka": "Jupiter",
        "description": "सामान्य/General"
    }
}

# House Meanings (for interpretation)
HOUSE_MEANINGS = {
    1: "Self, Personality, Health, Beginning",
    2: "Wealth, Family, Speech, Food",
    3: "Siblings, Courage, Communication, Short Travel",
    4: "Mother, Home, Property, Comfort, Education",
    5: "Children, Romance, Intelligence, Creativity",
    6: "Enemies, Disease, Debt, Service, Competition",
    7: "Marriage, Partnership, Business, Public",
    8: "Longevity, Obstacles, Transformation, Inheritance",
    9: "Father, Fortune, Religion, Higher Education, Long Travel",
    10: "Career, Profession, Status, Authority",
    11: "Gains, Income, Friends, Fulfillment of Desires",
    12: "Loss, Expenses, Foreign, Spirituality, Liberation"
}

# House Meanings in Hindi
HOUSE_MEANINGS_HINDI = {
    1: "तनु भाव - व्यक्तित्व, स्वास्थ्य",
    2: "धन भाव - धन, परिवार, वाणी",
    3: "सहज भाव - भाई-बहन, साहस",
    4: "सुख भाव - माता, घर, शिक्षा",
    5: "पुत्र भाव - संतान, प्रेम, बुद्धि",
    6: "रोग भाव - शत्रु, रोग, ऋण",
    7: "जाया भाव - विवाह, साझेदारी",
    8: "आयु भाव - आयु, बाधाएं",
    9: "भाग्य भाव - पिता, भाग्य, धर्म",
    10: "कर्म भाव - करियर, पद",
    11: "लाभ भाव - आय, लाभ, मित्र",
    12: "व्यय भाव - व्यय, विदेश, मोक्ष"
}

# Hindi Planet Names
HINDI_PLANET_NAMES = {
    "Sun": "सूर्य",
    "Moon": "चंद्र",
    "Mars": "मंगल",
    "Mercury": "बुध",
    "Jupiter": "गुरु",
    "Venus": "शुक्र",
    "Saturn": "शनि",
    "Rahu": "राहु",
    "Ketu": "केतु"
}

# Hindi Sign Names
HINDI_SIGN_NAMES = {
    "Aries": "मेष",
    "Taurus": "वृषभ",
    "Gemini": "मिथुन",
    "Cancer": "कर्क",
    "Leo": "सिंह",
    "Virgo": "कन्या",
    "Libra": "तुला",
    "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु",
    "Capricorn": "मकर",
    "Aquarius": "कुंभ",
    "Pisces": "मीन"
}


# =============================================================================
# NEW HELPER FUNCTIONS TO ADD
# =============================================================================

def _is_moolatrikona(p: Dict) -> bool:
    """
    Check if planet is in moolatrikona.
    
    A planet in moolatrikona is stronger than in own sign but not as strong as exalted.
    
    Args:
        p: Planet dictionary with 'name', 'sign', and 'local_degree'
    
    Returns:
        True if planet is in moolatrikona degree range
    """
    if not p:
        return False
    
    name = normalize_planet_name(p.get("name"))
    sign = str(p.get("sign") or p.get("rasi") or "").title()
    degree = p.get("local_degree", 0)
    
    if not name or not sign:
        return False
    
    mt = MOOLATRIKONA.get(name)
    if not mt:
        return False
    
    if mt["sign"] != sign:
        return False
    
    return mt["start"] <= degree <= mt["end"]


def get_planet_dignity(planet_name: str, sign: str, degree: float = 0) -> str:
    """
    Get the dignity status of a planet in a sign.
    
    Priority order:
    1. Exalted
    2. Debilitated
    3. Moolatrikona (within degree range)
    4. Own Sign
    5. Friendly Sign
    6. Enemy Sign
    7. Neutral
    
    Args:
        planet_name: Name of the planet
        sign: Sign where planet is placed
        degree: Local degree in sign (0-30)
    
    Returns:
        Dignity status string: 'exalted', 'debilitated', 'moolatrikona', 
                              'own_sign', 'friendly', 'enemy', 'neutral'
    """
    if not planet_name or not sign:
        return "neutral"
    
    planet_name = normalize_planet_name(planet_name)
    sign = sign.title()
    
    # Check exaltation
    if EXALTATION.get(planet_name) == sign:
        return "exalted"
    
    # Check debilitation
    if DEBILITATION.get(planet_name) == sign:
        return "debilitated"
    
    # Check own sign
    if sign in OWN_SIGNS.get(planet_name, set()):
        # Check moolatrikona within own sign
        mt = MOOLATRIKONA.get(planet_name)
        if mt and mt["sign"] == sign:
            if mt["start"] <= degree <= mt["end"]:
                return "moolatrikona"
        return "own_sign"
    
    # Check friendships
    sign_lord = RASI_LORDS.get(sign, "")
    if not sign_lord:
        return "neutral"
    
    friendships = PLANET_FRIENDSHIPS.get(planet_name, {})
    
    if sign_lord in friendships.get("friends", set()):
        return "friendly"
    if sign_lord in friendships.get("enemies", set()):
        return "enemy"
    
    return "neutral"


def get_dignity_score(dignity: str) -> float:
    """
    Get numerical score for a dignity status.
    
    Args:
        dignity: Dignity status string
    
    Returns:
        Numerical score (higher is better)
    """
    return DIGNITY_SCORES.get(dignity, 0)


def is_planet_combust(planet_name: str, planets: Dict) -> bool:
    """
    Check if a planet is combust (too close to Sun).
    
    Args:
        planet_name: Name of planet to check
        planets: All planets data
    
    Returns:
        True if planet is combust
    """
    if planet_name in ("Sun", "Rahu", "Ketu"):
        return False
    
    planet = get_planet(planet_name, planets)
    if not planet:
        return False
    
    # Check flag first
    if planet.get("is_combusted") or planet.get("is_combust"):
        return True
    
    # Calculate from Sun position
    sun = get_planet("Sun", planets)
    if not sun:
        return False
    
    planet_deg = planet.get("global_degree", 0)
    sun_deg = sun.get("global_degree", 0)
    
    diff = abs(planet_deg - sun_deg)
    if diff > 180:
        diff = 360 - diff
    
    orb = COMBUSTION_ORB.get(planet_name, 10)
    return diff <= orb


def is_planet_afflicted(
    planet_name: str,
    planets: Dict,
    aspects_data: Dict = None
) -> tuple:
    """
    Check if a planet is afflicted and return details.
    
    Affliction criteria:
    1. Debilitated
    2. Combust
    3. Retrograde (partial affliction)
    4. Heavily aspected by malefics
    
    Args:
        planet_name: Name of planet to check
        planets: All planets data
        aspects_data: Pre-calculated aspects (optional)
    
    Returns:
        Tuple of (is_afflicted: bool, reasons: List[str])
    """
    planet = get_planet(planet_name, planets)
    if not planet:
        return False, []
    
    reasons = []
    
    # Check debilitation
    sign = str(planet.get("sign") or planet.get("rasi") or "").title()
    if DEBILITATION.get(planet_name) == sign:
        reasons.append("Debilitated")
    
    # Check combustion
    if is_planet_combust(planet_name, planets):
        reasons.append("Combust")
    
    # Check retrograde
    if planet.get("is_retro") or planet.get("retro"):
        reasons.append("Retrograde")
    
    # Check malefic aspects
    if aspects_data:
        aspecting = aspects_data.get("aspects_on_planet", {}).get(planet_name, [])
        malefic_aspects = [p for p in aspecting if p in MALEFICS]
        if len(malefic_aspects) >= 2:
            reasons.append(f"Multiple malefic aspects ({', '.join(malefic_aspects)})")
        elif malefic_aspects:
            benefic_aspects = [p for p in aspecting if p in BENEFICS]
            if not benefic_aspects:
                reasons.append(f"Malefic aspect from {', '.join(malefic_aspects)}")
    
    # Determine if truly afflicted (retrograde alone is not affliction)
    is_afflicted = len(reasons) > 0 and "Retrograde" not in reasons or len(reasons) >= 2
    
    return is_afflicted, reasons


def get_house_lord(house_num: int, houses: List[Dict]) -> str:
    """
    Get the lord of a specific house.
    
    Args:
        house_num: House number (1-12)
        houses: List of house dictionaries
    
    Returns:
        Planet name that rules the house, or empty string
    """
    for h in houses:
        if h.get("house") == house_num:
            sign = h.get("start_rasi") or h.get("rasi") or h.get("sign")
            if sign:
                return RASI_LORDS.get(sign, "")
    return ""


def get_lord_placement(
    house_num: int,
    planets: Dict,
    houses: List[Dict]
) -> Dict[str, Any]:
    """
    Get where a house lord is placed.
    
    Args:
        house_num: House number whose lord to find
        planets: Planet data dictionary
        houses: House data list
    
    Returns:
        Dictionary with lord name and placement details
    """
    lord = get_house_lord(house_num, houses)
    if not lord:
        return {"lord": None}
    
    planet = get_planet(lord, planets)
    if not planet:
        return {"lord": lord, "house": None}
    
    sign = str(planet.get("sign") or planet.get("rasi") or "").title()
    degree = planet.get("local_degree", 0)
    
    return {
        "lord": lord,
        "house": planet.get("house"),
        "sign": sign,
        "degree": degree,
        "is_retro": planet.get("is_retro", False),
        "nakshatra": planet.get("nakshatra", ""),
        "nakshatra_lord": planet.get("nakshatra_lord", ""),
        "dignity": get_planet_dignity(lord, sign, degree)
    }


def format_lord_placement(placement: Dict, language: str = "English") -> str:
    """
    Format lord placement as readable string.
    
    Args:
        placement: Output from get_lord_placement()
        language: "English" or "Hindi"
    
    Returns:
        Formatted string describing the placement
    """
    if not placement.get("lord"):
        return "Lord not found"
    
    lord = placement["lord"]
    house = placement.get("house", "?")
    sign = placement.get("sign", "?")
    degree = placement.get("degree", 0)
    
    if language == "Hindi":
        lord_hindi = HINDI_PLANET_NAMES.get(lord, lord)
        sign_hindi = HINDI_SIGN_NAMES.get(sign, sign)
        return f"{lord_hindi} {house}वें भाव में {sign_hindi} राशि में {degree:.1f}° पर"
    
    return f"{lord} in House {house} in {sign} at {degree:.1f}°"


def get_house_connection(
    house1: int,
    house2: int,
    planets: Dict,
    houses: List[Dict]
) -> List[str]:
    """
    Find how two houses are connected through lordship.
    
    Args:
        house1: First house number
        house2: Second house number
        planets: Planet data
        houses: House data
    
    Returns:
        List of connection descriptions
    """
    connections = []
    
    lord1 = get_house_lord(house1, houses)
    lord2 = get_house_lord(house2, houses)
    
    if lord1:
        p1 = get_planet(lord1, planets)
        if p1 and p1.get("house") == house2:
            connections.append(
                f"{house1}th Lord ({lord1}) placed in {house2}th House "
                f"connects {house1}th and {house2}th house matters"
            )
    
    if lord2:
        p2 = get_planet(lord2, planets)
        if p2 and p2.get("house") == house1:
            connections.append(
                f"{house2}th Lord ({lord2}) placed in {house1}th House "
                f"connects {house1}th and {house2}th house matters"
            )
    
    # Check if lords are conjunct
    if lord1 and lord2 and lord1 != lord2:
        p1 = get_planet(lord1, planets)
        p2 = get_planet(lord2, planets)
        if p1 and p2 and p1.get("house") == p2.get("house"):
            connections.append(
                f"{house1}th Lord ({lord1}) conjunct {house2}th Lord ({lord2}) "
                f"in House {p1.get('house')} - strong connection"
            )
    
    return connections


def get_marriage_house_analysis(planets: Dict, houses: List[Dict]) -> Dict[str, Any]:
    """
    Get comprehensive marriage house analysis.
    
    Analyzes houses 2, 5, 7, 8, 11 for marriage prospects.
    
    Args:
        planets: Planet data
        houses: House data
    
    Returns:
        Dictionary with marriage-specific analysis
    """
    analysis = {
        "primary_lords": {},
        "secondary_lords": {},
        "connections": [],
        "strength_score": 5.0
    }
    
    # Primary houses: 2, 7, 11
    for h in [7, 2, 11]:
        placement = get_lord_placement(h, planets, houses)
        analysis["primary_lords"][h] = placement
    
    # Secondary houses: 5, 8
    for h in [5, 8]:
        placement = get_lord_placement(h, planets, houses)
        analysis["secondary_lords"][h] = placement
    
    # Find connections
    marriage_houses = {2, 5, 7, 8, 11}
    for h1 in marriage_houses:
        for h2 in marriage_houses:
            if h1 < h2:
                conns = get_house_connection(h1, h2, planets, houses)
                analysis["connections"].extend(conns)
    
    # Calculate strength score
    scores = []
    for h, pl in analysis["primary_lords"].items():
        dignity = pl.get("dignity", "neutral")
        scores.append(get_dignity_score(dignity))
    
    if scores:
        analysis["strength_score"] = 5 + (sum(scores) / len(scores))
    
    return analysis
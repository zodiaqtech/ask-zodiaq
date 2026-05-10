"""
KP Timing Engine - Comprehensive Marriage/Event Timing Calculator

This module implements the full KP (Krishnamurti Paddhati) timing methodology:
1. Ruling planet extraction and filtering
2. KP signification scoring (positive/negative/net)
3. Dasha period scoring with planet scores
4. Age-based filtering
5. Transit scoring (NOW WITH PARALLEL API CALLS!)
6. Retrograde delay tagging
7. Top timing window selection

Ported from the original Jupyter notebook implementation.
"""
from typing import Dict, List, Any, Set, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import asyncio  # NEW: Added for async parallel API calls

from app.core.astro_constants import normalize_planet_name, RASI_LORDS

logger = logging.getLogger(__name__)

# Valid age ranges for different domains
VALID_AGE_RANGES = {
    "Marriage": (18, 45),
    "Child": (0, 45),
    "Love_Relationship": (18, 40),
    "Parenting": (20, 50),
    "Career": (16, 70),
    "Family": (0, 100),
    "Health": (0, 120),
    "Property": (18, 90),
    "Vehicles": (18, 85),
    "Foreign": (16, 90),
    "Finance": (18, 80),
    "Business": (18, 80),
    "Education": (16, 40),
    "Travel" : (0, 80),
    "Legal": (18, 80)
}




TIMING_RULES = {

    # =======================
    # FINANCE
    # =======================
    "Loan Repayment Timing": {
        "positive_houses": {2, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {1, 10},
        "supportive_score": 1,
        "key_planets": {"Saturn", "Rahu"}
    },

    "Loan Taking Timing": {
        # Loan approval, availability of funds, credit access
        "positive_houses": {2, 6, 10, 11},
        "negative_houses": {8, 12},
        "supportive_houses": {1, 5},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Mercury", "Saturn"}
    },


    "Prospects of Property": {
        "positive_houses": {4, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {2, 10},
        "supportive_score": 2,
        "key_planets": {"Mars", "Venus"}
    },

    # =======================
    # CAREER
    # =======================
    "Job Start Timing": {
        "positive_houses": {2, 6, 10},
        "negative_houses": {8, 12},
        "supportive_houses": {11},
        "supportive_score": 2,
        "key_planets": {"Saturn", "Mercury"}
    },

    "Promotion Timing": {
        "positive_houses": {10, 11},
        "negative_houses": {8, 12},
        "supportive_houses": {2, 6},
        "supportive_score": 2,
        "key_planets": {"Saturn", "Sun"}
    },

    "Career Shift Timing": {
        "positive_houses": {7, 9, 12},
        "negative_houses": {6, 8},
        "supportive_houses": {3, 5},
        "supportive_score": 1,
        "key_planets": {"Rahu", "Saturn"}
    },

    "Foreign Career Potential": {
        "positive_houses": {9, 12},
        "negative_houses": {4, 10},
        "supportive_houses": {3, 7},
        "supportive_score": 1,
        "key_planets": {"Rahu", "Jupiter"}
    },

    # =======================
    # BUSINESS
    # =======================
    "Business Start Timing": {
        "positive_houses": {1, 2, 7, 10, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {3, 5},
        "supportive_score": 2,
        "key_planets": {"Mercury", "Jupiter"}
    },

    "Business Growth Timing": {
        "positive_houses": {2, 7, 10, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {5, 9},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Venus", "Saturn"}
    },

    "Business Recovery Timing": {
        "positive_houses": {2, 10, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {1, 5},
        "supportive_score": 1,
        "key_planets": {"Saturn", "Mercury"}
    },

    # =======================
    # HEALTH
    # =======================
    "Health Risk Timing": {
        "positive_houses": {6, 8, 12},
        "negative_houses": {1, 5, 9, 11},
        "supportive_houses": {10},
        "supportive_score": 1,
        "key_planets": {"Saturn", "Rahu"}
    },

    "Surgery Timing": {
        "positive_houses": {6, 8, 12},
        "negative_houses": {1, 5, 9, 11},
        "supportive_houses": {10},
        "supportive_score": 1,
        "key_planets": {"Saturn", "Rahu", "Mars"}
    },

    "Cure Timing": {
        "positive_houses": {5, 9, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {1},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Moon"}
    },

    # =======================
    # CHILD
    # =======================
    "Foreign Higher Education Timing": {
        "positive_houses": {5, 9, 12},
        "negative_houses": {4, 6, 8},
        "supportive_houses": {3, 11},
        "supportive_score": 1,
        "key_planets": {"Rahu", "Jupiter"}
    },

    # =======================
    # PARENTING (MULTI)
    # =======================
    "Timing of Childbirth": {
        "positive_houses": {2, 5, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {1, 9},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Moon", "Venus"}
    },

    "Best Time to Conceive": {
        "positive_houses": {2, 5, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {1, 9},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Moon", "Venus"}
    },

    # =======================
    # FOREIGN
    # =======================
    "Foreign Timing": {
        "positive_houses": {3, 9, 12},
        "negative_houses": {4, 10},
        "supportive_houses": {7, 11},
        "supportive_score": 2,
        "key_planets": {"Rahu", "Saturn"}
    },

    # =======================
    # LOVE / RELATIONSHIP
    # =======================
    "Marriage Timing": {
        "positive_houses": {2, 5, 7, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {9},
        "supportive_score": 2,
        "key_planets": {"Venus", "Jupiter", "Moon"}
    },


     "Marriage Promise and Timing": {
        "positive_houses": {2, 5, 7, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {9},
        "supportive_score": 2,
        "key_planets": {"Venus", "Jupiter", "Moon"}
    },

    "Reconciliation Timing": {
        "positive_houses": {5, 7, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {2, 9},
        "supportive_score": 2,
        "key_planets": {"Venus", "Moon", "Mercury", "Jupiter"}
    },

    # =======================
    # MARRIAGE
    # =======================
    "Divorce Timing": {
        "positive_houses": {6, 8, 12},
        "negative_houses": {2, 7, 11},
        "supportive_houses": {1, 10},
        "supportive_score": 1,
        "key_planets": {"Saturn", "Rahu", "Mars", "Ketu"}
    },

    # =======================
    # GENERAL GUIDANCE
    # =======================
    "Success Timing": {
        "positive_houses": {1, 2, 10, 11},
        "negative_houses": {6, 8, 12},
        "supportive_houses": {5, 9},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Sun"}
    },

    # =======================
    # TRAVEL / PILGRIMAGE
    # =======================
    "Travel Timing": {
        "positive_houses": {3, 9, 12},
        "negative_houses": {4, 8},
        "supportive_houses": {7, 11},
        "supportive_score": 2,
        "key_planets": {"Jupiter", "Rahu", "Moon"}
    },

    "Court Case Conclusion Timing": {
    "positive_houses": {6, 7, 10, 11},
    "supportive_houses": {2, 9},
    "negative_houses": {8, 12},
    "key_planets": {"Saturn", "Jupiter", "Sun"}
    }


}


# Day lords for ruling planet calculation
WEEKDAY_LORDS = {
    0: "Moon",      # Monday
    1: "Mars",      # Tuesday
    2: "Mercury",   # Wednesday
    3: "Jupiter",   # Thursday
    4: "Venus",     # Friday
    5: "Saturn",    # Saturday
    6: "Sun"        # Sunday
}


def safe_get(d: Any, *keys, default=None) -> Any:
    """Safely get nested dictionary values"""
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur


def get_kp_ruling_planets(planets: Dict[str, Dict], include_asc_star: bool = True) -> List[str]:
    """
    Extract KP ruling planets for timing analysis.
    
    Ruling planets are:
    1. Day lord (based on current day)
    2. Moon's nakshatra lord
    3. Moon's sign lord
    4. Ascendant's sign lord
    5. Ascendant's nakshatra lord (optional)
    
    Args:
        planets: Dictionary of planet data keyed by planet name
        include_asc_star: Whether to include Ascendant's star lord
    
    Returns:
        List of ruling planet names (unique, order preserved)
    """
    rp = []
    
    # 1. Day lord
    today = datetime.now().weekday()
    day_lord = WEEKDAY_LORDS.get(today)
    if day_lord:
        rp.append(day_lord)
    
    # Find Moon and Ascendant
    moon = planets.get("Moon") or planets.get("Mo")
    asc = planets.get("Ascendant") or planets.get("As")
    
    # 2-3. Moon's star lord and sign lord
    if moon:
        m_star = moon.get("nakshatra_lord") or moon.get("pseudo_nakshatra_lord")
        m_rasi = (moon.get("rashi_lord") or moon.get("pseudo_rasi_lord") or 
                  RASI_LORDS.get(moon.get("sign") or moon.get("rasi")))
        
        if m_star:
            norm_star = normalize_planet_name(m_star)
            if norm_star:
                rp.append(norm_star)
        if m_rasi:
            norm_rasi = normalize_planet_name(m_rasi)
            if norm_rasi:
                rp.append(norm_rasi)
    
    # 4-5. Ascendant's sign lord and star lord
    if asc:
        asc_rasi = (asc.get("rashi_lord") or asc.get("pseudo_rasi_lord") or
                    RASI_LORDS.get(asc.get("sign") or asc.get("rasi")))
        asc_star = asc.get("nakshatra_lord") or asc.get("pseudo_nakshatra_lord")
        
        if asc_rasi:
            norm_rasi = normalize_planet_name(asc_rasi)
            if norm_rasi:
                rp.append(norm_rasi)
        if include_asc_star and asc_star:
            norm_star = normalize_planet_name(asc_star)
            if norm_star:
                rp.append(norm_star)
    
    # Remove duplicates while preserving order
    final = []
    for p in rp:
        if p and p not in final:
            final.append(p)
    
    return final


def score_kp_all_planets(
    planets_data: Dict[str, Dict],
    houses_data: List[Dict],
    domain_rules: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Fully generic KP scoring engine for all planets.
    
    Calculates positive, negative, and net scores based on:
    - House occupancy (S1)
    - Star lord's house (S2)
    - Sub lord's house (S3)
    - Houses owned (S1b)
    
    Args:
        planets_data: Dictionary of planet data
        houses_data: List of house data dictionaries
        domain_rules: Domain-specific rules with positive_houses, supportive_houses, etc.
    
    Returns:
        List of dicts with planet scores, sorted by net score descending
    """
    POS = set(domain_rules.get("positive_houses", set()))
    SUP = set(domain_rules.get("supportive_houses", set()))
    SUP_SCORE = domain_rules.get("supportive_score", 2)
    
    # Get negative houses from rules (default to standard dusthana)
    NEG = set(domain_rules.get("negative_houses", {6, 8, 12}))
    
    # Build negative base scores dynamically
    # 8th house (transformation/death) is typically strongest negative
    neg_base = {}
    for h in NEG:
        if h == 8:
            neg_base[h] = -3  # Strongest negative
        elif h in {6, 12}:
            neg_base[h] = -2  # Standard dusthana
        else:
            neg_base[h] = -1.5  # Other negative houses (like 2,7,11 for divorce)
    
    mult = {"S1": 1.0, "S2": 1.1, "S3": 1.25, "S1b": 0.7}
    
    # Normalize planet keys
    planets = {}
    for k, v in planets_data.items():
        if isinstance(v, dict):
            norm_name = normalize_planet_name(k)
            if norm_name:
                planets[norm_name] = dict(v, **{"_name_key": norm_name})
    
    # 1. Occupants of POSITIVE houses
    # Method A: From houses data (if planets list is populated)
    occupants = set()
    for h in houses_data:
        if h.get("house") in POS:
            for p in h.get("planets", []):
                pname = p.get("name") if isinstance(p, dict) else p
                norm_name = normalize_planet_name(pname)
                if norm_name:
                    occupants.add(norm_name)
    
    # Method B: From planets data (using planet's own house field)
    # This is a fallback if houses don't have planets populated
    for pname, pinfo in planets.items():
        if pname == "Ascendant":
            continue
        h = pinfo.get("house") if isinstance(pinfo, dict) else None
        if isinstance(h, int) and h in POS:
            norm_name = normalize_planet_name(pname)
            if norm_name:
                occupants.add(norm_name)
    
    logger.debug(f"Occupants of positive houses {POS}: {occupants}")
    
    # 2. Lords of POSITIVE houses
    lords = set()
    for h in houses_data:
        if h.get("house") in POS:
            sr = h.get("start_rasi")
            if sr:
                lord = RASI_LORDS.get(sr)
                if lord:
                    lords.add(lord)
    
    # Star lords of occupants & lords
    occupant_star_lords = {
        normalize_planet_name(safe_get(planets.get(o, {}), "nakshatra_lord"))
        for o in occupants if o in planets
    }
    lord_star_lords = {
        normalize_planet_name(safe_get(planets.get(o, {}), "nakshatra_lord"))
        for o in lords if o in planets
    }
    
    # 3. Score each planet
    results = []
    
    for pname, pinfo in planets.items():
        if pname == "Ascendant":
            continue
        
        # S-level significance
        S1 = safe_get(pinfo, "house")
        
        nl = normalize_planet_name(safe_get(pinfo, "nakshatra_lord"))
        S2 = planets.get(nl, {}).get("house") if nl and nl in planets else None
        
        sl = normalize_planet_name(safe_get(pinfo, "sub_lord"))
        S3 = planets.get(sl, {}).get("house") if sl and sl in planets else None
        
        # S1b = houses owned by this planet
        S1b = []
        for h in houses_data:
            sr = h.get("start_rasi")
            if sr and RASI_LORDS.get(sr) == pname:
                S1b.append(h.get("house"))
        
        # Influence map
        infl = {}
        if isinstance(S1, int):
            infl.setdefault(S1, []).append("S1")
        if isinstance(S2, int):
            infl.setdefault(S2, []).append("S2")
        if isinstance(S3, int):
            infl.setdefault(S3, []).append("S3")
        for oh in S1b:
            infl.setdefault(oh, []).append("S1b")
        
        # 4. Positive scoring
        score_pos = 0
        
        if nl in occupant_star_lords:
            score_pos += 4
        if pname in occupants:
            score_pos += 3
        if nl in lord_star_lords:
            score_pos += 2
        if pname in lords:
            score_pos += 1
        
        # Supportive houses bonus
        sigs = set(pinfo.get("significators", []))
        # Also check if planet signifies supportive houses through occupation
        for h_no in [S1, S2, S3] + S1b:
            if isinstance(h_no, int) and h_no in SUP:
                score_pos += SUP_SCORE
                break
        
        # 5. Negative scoring (6/8/12)
        neg_total = 0
        for h, levels in infl.items():
            if h not in NEG:
                continue
            base = abs(neg_base[h])
            for lvl in levels:
                # If S1 sits in POS, reduce negative impact
                if S1 in POS:
                    neg_total += (base * 0.6) * mult.get(lvl, 1.0)
                else:
                    neg_total += base * mult.get(lvl, 1.0)
        
        net = score_pos - neg_total
        
        results.append({
            "planet": pname,
            "positive": score_pos,
            "negative": -neg_total,
            "net": net,
            "nak_lord": nl,
            "sub_lord": sl,
            "rasi_lord": safe_get(pinfo, "rashi_lord") or RASI_LORDS.get(safe_get(pinfo, "sign"))
        })
    
    # 6. Rahu/Ketu shadow scoring
    pos_lookup = {r["planet"]: r["positive"] for r in results}
    
    for row in results:
        pname = row["planet"]
        if pname not in ("Rahu", "Ketu"):
            continue
        
        nl = row["nak_lord"]
        sl = row["sub_lord"]
        gl = row["rasi_lord"]
        
        shadow_positive = (
            0.5 * pos_lookup.get(nl, 0) +
            0.3 * pos_lookup.get(sl, 0) +
            0.2 * pos_lookup.get(gl, 0)
        )
        row["positive"] = shadow_positive
        row["net"] = shadow_positive + row["negative"]
    
    # Sort by net score descending
    results.sort(key=lambda x: x["net"], reverse=True)
    return results


def get_positive_planets(scored_list: List[Dict]) -> List[str]:
    """Get list of planets with positive scores"""
    return [p["planet"] for p in scored_list if p.get("positive", 0) > 0]


def score_periods_with_planet_scores(
    periods: List[Dict],
    planet_score: Dict[str, Dict]
) -> List[Dict]:
    """
    Score dasha periods using pre-calculated planet scores.
    
    Weighting:
    - Maha dasha: 3x
    - Antara dasha: 2x
    - Paryantar dasha: 1x
    
    Args:
        periods: List of dasha period dicts with maha/antara/paryantar keys
        planet_score: Dict mapping planet names to their score dicts
    
    Returns:
        Scored periods sorted by total_score descending
    """
    scored_periods = []
    
    for p in periods:
        maha = normalize_planet_name(p.get("maha") or p.get("md"))
        antara = normalize_planet_name(p.get("antara") or p.get("ad"))
        paryantar = normalize_planet_name(p.get("paryantar") or p.get("pd"))
        
        s_maha = planet_score.get(maha, {}).get("positive", 0)
        s_antara = planet_score.get(antara, {}).get("positive", 0)
        s_paryantar = planet_score.get(paryantar, {}).get("positive", 0)
        
        total = 3 * s_maha + 2 * s_antara + s_paryantar
        
        scored_periods.append({
            **p,
            "score_maha": s_maha,
            "score_antara": s_antara,
            "score_paryantar": s_paryantar,
            "total_score": total
        })
    
    scored_periods.sort(key=lambda x: x["total_score"], reverse=True)
    return scored_periods


def filter_by_age(
    periods: List[Dict],
    dob: datetime,
    domain: str,
    cutoff_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Filter dasha periods by valid age range for the domain.
    
    Args:
        periods: List of dasha period dicts with start/end dates
        dob: Date of birth
        domain: Domain name for age range lookup
        cutoff_date: Optional cutoff date (defaults to today)
    
    Returns:
        Filtered list of periods within valid age range
    """
    if cutoff_date is None:
        cutoff_date = datetime.today()
    
    filtered = []
    min_age, max_age = VALID_AGE_RANGES.get(domain, (0, 120))
    
    for c in periods:
        start_dt = c.get("start")
        end_dt = c.get("end")

        # Auto-convert strings to datetime
        if isinstance(start_dt, str):
            try:
                start_dt = datetime.strptime(start_dt, "%Y-%m-%d")
            except:
                continue

        if isinstance(end_dt, str):
            try:
                end_dt = datetime.strptime(end_dt, "%Y-%m-%d")
            except:
                continue

        if not isinstance(start_dt, datetime) or not isinstance(end_dt, datetime):
            continue

        
        # Adjust start if period spans cutoff
        if start_dt < cutoff_date <= end_dt:
            c = dict(c)
            c["start"] = cutoff_date
            start_dt = cutoff_date
        
        # Skip periods that have ended
        if end_dt < cutoff_date:
            continue
        
        # Calculate age at period start
        age = (start_dt - dob).days / 365.25
        
        if min_age <= age <= max_age:
            c_copy = dict(c)
            c_copy["age_at_start"] = round(age, 1)
            filtered.append(c_copy)
    
    return filtered


def valid_for_domain(
    window: Dict,
    planet_score: Dict[str, Dict],
    timing_name: str = None
) -> bool:
    """
    KP positive filter for timing windows.
    
    Validates that:
    - MD (Maha Dasha) is not very negative (net >= -1)
    - AD (Antara Dasha) has positive score (relaxed for key planets)
    - PD (Paryantar Dasha) is reasonable based on MD strength
    
    Args:
        window: Dasha window dict with maha/antara/paryantar
        planet_score: Planet score lookup dict
        timing_name: Optional timing context (e.g., "Marriage Timing")
    
    Returns:
        True if window passes KP filter
    """
    MD = normalize_planet_name(window.get("maha") or window.get("md"))
    AD = normalize_planet_name(window.get("antara") or window.get("ad"))
    PD = normalize_planet_name(window.get("paryantar") or window.get("pd"))
    
    md_net = planet_score.get(MD, {}).get("net", -999)
    ad_pos = planet_score.get(AD, {}).get("positive", 0)
    pd_pos = planet_score.get(PD, {}).get("positive", 0)
    
    # Get key planets for this timing type
    timing_rules = TIMING_RULES.get(timing_name, {})
    key_planets = timing_rules.get("key_planets", {"Venus", "Jupiter", "Moon"})
    
    # MD must not be very negative
    if md_net < -1:
        return False
    
    # AD must be positive
    # EXCEPTION: Key planets for this timing type are allowed even with positive=0
    if ad_pos <= 0:
        if AD in key_planets:
            pass  # Allow key planet AD even if positive=0
        else:
            return False
    
    # PD check depends on MD strength
    if md_net > 3:
        # Strong MD allows slightly negative PD
        if pd_pos < -2:
            return False
    else:
        # Weak MD requires positive PD (relaxed to >= 0 for key planets)
        if pd_pos < 0:
            return False
    
    return True


def tag_retro_delay(
    periods: List[Dict],
    planets: Dict[str, Dict]
) -> List[Dict]:
    """
    Tag periods with retrograde delays.
    
    Retrograde Jupiter/Saturn/Rahu/Ketu can cause delays:
    - Jupiter retrograde: 1 year delay
    - Saturn/Rahu/Ketu retrograde: 2 year delay
    
    Args:
        periods: List of dasha periods
        planets: Planet data dict
    
    Returns:
        Periods with _delay_years and _needs_resonant_jump tags
    """
    retro = {}
    for k, v in planets.items():
        if isinstance(v, dict):
            norm_name = normalize_planet_name(k)
            if norm_name:
                retro[norm_name] = bool(v.get("is_retro") or v.get("retro") or False)
    
    for c in periods:
        delay = 0

        if retro.get("Jupiter"):
            delay = max(delay, 1)
        if retro.get("Saturn") or retro.get("Rahu") or retro.get("Ketu"):
            delay = max(delay, 2)

        
        delay = min(delay, 2)  # Cap at 2 years
        
        if delay:
            c["_delay_years"] = delay
            c["_needs_resonant_jump"] = (delay >= 2)
    
    return periods


def kp_transit_score(
    window: Dict,
    transit_data: Dict[str, Dict]
) -> float:
    """
    Calculate KP transit score for a timing window.
    
    Scores based on:
    - Transit planet house positions (positive: 2,7,11,5,1; negative: 6,8,12)
    - Transit nakshatra/sub/rasi lord connections to DBA planets
    - Special multipliers for Moon (1.5x) and Venus (1.3x)
    
    Args:
        window: Dasha window with maha/antara/paryantar
        transit_data: Transit planet positions with nakshatra_lord, sub_lord, rasi_lord
    
    Returns:
        Transit score (can be negative)
    """
    dba = {
        normalize_planet_name(window.get("maha")),
        normalize_planet_name(window.get("antara")),
        normalize_planet_name(window.get("paryantar"))
    }
    dba.discard(None)
    
    score = 0.0
    BASE = 1.0
    MOON_MULT = 1.5
    VENUS_MULT = 1.3
    DBA_MULT = 1.4
    HOUSE_POS = {2: 4, 7: 4, 11: 3, 5: 1, 1: 1}
    HOUSE_NEG = {6: -3, 8: -3, 12: -2}
    
    for pl, tr in transit_data.items():
        norm_pl = normalize_planet_name(pl)
        if norm_pl == "Ascendant":
            continue
        
        house = tr.get("house")
        nl = normalize_planet_name(tr.get("nakshatra_lord"))
        sl = normalize_planet_name(tr.get("sub_lord"))
        rl = normalize_planet_name(tr.get("rasi_lord"))
        
        # Determine multiplier
        mul = BASE
        if norm_pl == "Moon":
            mul = MOON_MULT
        elif norm_pl == "Venus":
            mul = VENUS_MULT
        elif norm_pl in dba:
            mul = DBA_MULT
        
        # Score based on lord connections to DBA
        if nl in dba:
            score += 5 * mul
        if sl in dba:
            score += 3 * mul
        if rl in dba:
            score += 2 * mul
        
        # Score based on house position
        if isinstance(house, int):
            if house in HOUSE_POS:
                score += HOUSE_POS[house] * mul
            if house in HOUSE_NEG:
                score += HOUSE_NEG[house] * mul
    
    return score


def merge_transit_data(
    transit_chart: Dict[str, Dict],
    kp_planets: Dict[str, Dict]
) -> Dict[str, Dict]:
    """
    Merge transit chart data with KP planet data.
    
    Transit chart provides house positions, KP planets provide
    nakshatra lords, sub lords, and rasi lords for accurate scoring.
    
    Args:
        transit_chart: Transit positions keyed by planet, with house/zodiac
        kp_planets: KP planet data with nakshatra_lord, sub_lord, etc.
    
    Returns:
        Merged dict with combined transit and KP data
    """
    merged = {}
    
    for key, tr in transit_chart.items():
        if not isinstance(tr, dict):
            continue
        
        # Get planet name
        raw = tr.get("name") or tr.get("planet") or key
        full_name = normalize_planet_name(raw)
        
        if not full_name:
            continue
        
        merged[full_name] = {
            "planet": full_name,
            "house": tr.get("house"),
            "rasi": tr.get("zodiac") or tr.get("rasi") or tr.get("sign")
        }
        
        # Find matching KP planet data
        kp = kp_planets.get(full_name)
        if not kp:
            # Fallback: try alternate keys
            for k, v in kp_planets.items():
                if isinstance(v, dict):
                    v_name = v.get("name")
                    if v_name and normalize_planet_name(v_name) == full_name:
                        kp = v
                        break
        
        # Merge KP data
        if kp:
            merged[full_name]["nakshatra"] = kp.get("nakshatra") or kp.get("pseudo_nakshatra")
            merged[full_name]["nakshatra_lord"] = normalize_planet_name(
                kp.get("nakshatra_lord") or kp.get("pseudo_nakshatra_lord")
            )
            merged[full_name]["sub_lord"] = normalize_planet_name(kp.get("sub_lord"))
            merged[full_name]["rasi_lord"] = normalize_planet_name(
                kp.get("rashi_lord") or kp.get("pseudo_rasi_lord") or
                RASI_LORDS.get(merged[full_name].get("rasi"))
            )
    
    return merged


def apply_transit_scores_to_windows(
    windows: List[Dict],
    fetch_transit_for_date: callable,
    fetch_kp_snapshot: callable,
    sex: str,
    lat: float,
    lon: float,
    tzone: str = "5.5"
) -> List[Dict]:
    """
    Apply transit scores to timing windows.
    
    For each window, fetches transit data at the midpoint date,
    merges with KP snapshot, and calculates transit score.
    
    Args:
        windows: List of timing windows with start/end dates
        fetch_transit_for_date: Callable(date) -> transit chart dict
        fetch_kp_snapshot: Callable(date, sex, lat, lon, tzone) -> KP planets dict
        sex: Gender for KP snapshot
        lat: Latitude
        lon: Longitude
        tzone: Timezone offset string
    
    Returns:
        Windows with transit_score and final_score added
    """
    for w in windows:
        try:
            start = w.get("start")
            end = w.get("end")
            
            # Parse dates if they're strings
            if isinstance(start, str):
                start = datetime.strptime(start, "%Y-%m-%d")
            if isinstance(end, str):
                end = datetime.strptime(end, "%Y-%m-%d")
            
            # Calculate midpoint
            mid = start + (end - start) / 2
            
            # Fetch transit and KP data
            transit_raw = fetch_transit_for_date(mid)
            kp_raw = fetch_kp_snapshot(mid, sex, lat, lon, tzone)
            
            if transit_raw and kp_raw:
                # Merge and score
                merged = merge_transit_data(transit_raw, kp_raw)
                t_score = kp_transit_score(w, merged)
                
                w["transit_score"] = round(t_score, 2)
                w["final_score"] = w.get("_domain_score", w.get("total_score", 0)) + t_score
            else:
                # No transit data available
                w["transit_score"] = 0
                w["final_score"] = w.get("_domain_score", w.get("total_score", 0))
                
        except Exception as e:
            logger.debug(f"Transit scoring failed for window: {e}")
            w["transit_score"] = 0
            w["final_score"] = w.get("_domain_score", w.get("total_score", 0))
    
    # Re-sort by final score
    windows.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    return windows


def get_top_timing_windows(
    dba_list: List[Dict],
    dob: datetime,
    planets: Dict[str, Dict],
    houses: List[Dict],
    domain: str,
    timing_name: str,
    max_windows: int = 100
) -> List[Dict]:
    """
    Main function to get top timing windows using full KP methodology.
    
    Process:
    1. Get ruling planets
    2. Score all planets using KP rules
    3. Filter by age range
    4. Filter by ruling planets (MD/AD/PD must include ruling planet)
    5. Filter by KP positive rules
    6. Score boost for key planets
    7. Tag retrograde delays
    8. Sort and return top windows
    
    Args:
        dba_list: List of dasha periods with start/end/maha/antara/paryantar
        dob: Date of birth
        planets: Normalized planet data
        houses: Normalized house data
        domain: Domain name (Marriage, Career, etc.)
        timing_name: Timing rule name (Marriage Timing, Career Timing, etc.)
        max_windows: Maximum windows to return
    
    Returns:
        Top timing windows sorted by domain score
    """
    logger.info(f"===== get_top_timing_windows DEBUG =====")
    logger.info(f"Input dba_list count: {len(dba_list)}")
    logger.info(f"Domain: {domain}, Timing: {timing_name}")
    
    # Log first few entries
    if dba_list and len(dba_list) > 0:
        for i, entry in enumerate(dba_list[:3]):
            logger.info(f"Entry {i}: {entry.get('dasha', 'N/A')} | maha={entry.get('maha')} antara={entry.get('antara')} paryantar={entry.get('paryantar')}")
    
    timing_rules = TIMING_RULES.get(timing_name, TIMING_RULES.get("Marriage Timing"))
    
    POS = set(timing_rules.get("positive_houses", {2, 7, 11}))
    NEG = set(timing_rules.get("negative_houses", {6, 8, 12}))
    SUP = set(timing_rules.get("supportive_houses", {5}))
    KEY = set(timing_rules.get("key_planets", {"Venus", "Jupiter", "Moon"}))
    
    # Log the rules being applied
    logger.info(f"TIMING RULES for '{timing_name}':")
    logger.info(f"  Positive houses: {sorted(POS)}")
    logger.info(f"  Negative houses: {sorted(NEG)}")
    logger.info(f"  Supportive houses: {sorted(SUP)}")
    logger.info(f"  Key planets: {sorted(KEY)}")
    
    # Get ruling planets
    ruling_planets = get_kp_ruling_planets(planets)
    logger.info(f"Ruling planets: {ruling_planets}")
    
    # Score all planets
    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
    planet_score_lookup = {p["planet"]: p for p in planet_scores}
    logger.info(f"Planet scores calculated for {len(planet_scores)} planets")
    
    # Log planet scores for key planets (dynamic based on timing type)
    log_planets = list(KEY) + ["Venus", "Jupiter", "Moon", "Saturn", "Rahu"]
    log_planets = list(set(log_planets))  # Remove duplicates
    for key_planet in sorted(log_planets):
        if key_planet in planet_score_lookup:
            ps = planet_score_lookup[key_planet]
            marker = "★" if key_planet in KEY else " "
            logger.info(f"  {marker} {key_planet}: positive={ps.get('positive', 0)}, negative={ps.get('negative', 0)}, net={ps.get('net', 0)}")
    
    # Score periods
    scored_periods = score_periods_with_planet_scores(dba_list, planet_score_lookup)
    logger.info(f"After scoring: {len(scored_periods)} periods")
    
    # 1. Age filter
    after_age = filter_by_age(scored_periods, dob, domain)
    logger.info(f"After age filter: {len(after_age)} periods (filtered {len(scored_periods) - len(after_age)})")
    
    # 2. Ruling planet filter (MD/AD/PD must contain at least one ruling planet)
    after_rp = [
        w for w in after_age
        if (normalize_planet_name(w.get("maha") or w.get("md")) in ruling_planets or
            normalize_planet_name(w.get("antara") or w.get("ad")) in ruling_planets or
            normalize_planet_name(w.get("paryantar") or w.get("pd")) in ruling_planets)
    ]
    logger.info(f"After ruling planet filter: {len(after_rp)} periods (filtered {len(after_age) - len(after_rp)})")
    
    # Log why periods were filtered
    if len(after_rp) == 0 and len(after_age) > 0:
        logger.warning("ALL periods filtered by ruling planet filter!")
        for i, w in enumerate(after_age[:5]):
            md = normalize_planet_name(w.get("maha") or w.get("md"))
            ad = normalize_planet_name(w.get("antara") or w.get("ad"))
            pd = normalize_planet_name(w.get("paryantar") or w.get("pd"))
            logger.warning(f"  Example {i}: MD={md}, AD={ad}, PD={pd} | Ruling: {ruling_planets}")
    
    # 3. KP positive filter
    after_kp = [w for w in after_rp if valid_for_domain(w, planet_score_lookup, timing_name)]
    logger.info(f"After KP positive filter: {len(after_kp)} periods (filtered {len(after_rp) - len(after_kp)})")
    
    # Log why periods were filtered
    if len(after_kp) == 0 and len(after_rp) > 0:
        logger.warning("ALL periods filtered by KP positive filter!")
        for i, w in enumerate(after_rp[:5]):
            md = normalize_planet_name(w.get("maha") or w.get("md"))
            ad = normalize_planet_name(w.get("antara") or w.get("ad"))
            pd = normalize_planet_name(w.get("paryantar") or w.get("pd"))
            md_net = planet_score_lookup.get(md, {}).get("net", -999)
            ad_pos = planet_score_lookup.get(ad, {}).get("positive", 0)
            pd_pos = planet_score_lookup.get(pd, {}).get("positive", 0)
            logger.warning(f"  Example {i}: {md}/{ad}/{pd} | md_net={md_net}, ad_pos={ad_pos}, pd_pos={pd_pos}")
    
    # 4. Score boost for key planets
    for w in after_kp:
        score = w.get("total_score", 0)
        maha = normalize_planet_name(w.get("maha") or w.get("md"))
        antara = normalize_planet_name(w.get("antara") or w.get("ad"))
        paryantar = normalize_planet_name(w.get("paryantar") or w.get("pd"))
        
        if maha in KEY:
            score += 4
        if antara in KEY:
            score += 3
        if paryantar in KEY:
            score += 2
        
        # Check 7th CSL connection for Marriage
        if timing_name == "Marriage Timing":
            h7 = next((h for h in houses if h.get("house") == 7), {})
            csl = normalize_planet_name(h7.get("cusp_sub_lord"))
            if csl and csl in {maha, antara, paryantar}:
                score += 15
        
        w["_domain_score"] = score
    
    # 5. Tag retrograde delays
    after_kp = tag_retro_delay(after_kp, planets)
    
    # 6. Sort and pick top windows
    final = sorted(after_kp, key=lambda x: x.get("_domain_score", 0), reverse=True)[:max_windows]
    
    logger.info(f"Final windows count: {len(final)}")
    if final and len(final) > 0:
        best = final[0]
        logger.info(f"Best window: {best.get('dasha', 'N/A')} | score={best.get('_domain_score', 'N/A')}")
        logger.info(f"Best window dates: {best.get('start')} to {best.get('end')}")
    
    logger.info(f"===== END get_top_timing_windows =====")
    
    return final


def format_timing_windows(windows: List[Dict], include_transit: bool = False) -> List[Dict]:
    """
    Format timing windows for API response.
    
    Tags windows with:
    - is_earliest_favorable: True for the best window within next 3 years
    - is_overall_best: True for the highest final_score window
    
    Args:
        windows: Raw timing windows
        include_transit: Whether to include transit score fields
    
    Returns:
        Formatted windows with consistent structure
    """
    formatted = []
    today = datetime.now()
    three_years_later = today + timedelta(days=3*365)
    
    for w in windows:
        start = w.get("start")
        end = w.get("end")
        
        # Format dates
        start_str = start.strftime("%Y-%m-%d") if isinstance(start, datetime) else str(start)
        end_str = end.strftime("%Y-%m-%d") if isinstance(end, datetime) else str(end)
        
        # Build dasha name
        maha = w.get("maha") or w.get("md", "")
        antara = w.get("antara") or w.get("ad", "")
        paryantar = w.get("paryantar") or w.get("pd", "")
        dasha_name = "-".join(filter(None, [maha, antara, paryantar]))
        
        entry = {
            "start": start_str,
            "end": end_str,
            "dasha": dasha_name or w.get("dasha", ""),
            "score": w.get("_domain_score", w.get("total_score", 0)),
            "age_at_start": w.get("age_at_start"),
            "delay_years": w.get("_delay_years"),
            "needs_resonant_jump": w.get("_needs_resonant_jump", False)
        }
        
        # Add transit fields if available
        if include_transit or "transit_score" in w:
            entry["transit_score"] = w.get("transit_score", 0)
            entry["final_score"] = w.get("final_score", entry["score"])
        
        formatted.append(entry)
    
    # Identify earliest favorable window (within 3 years, best base score)
    # and overall best window (highest final_score)
    if formatted:
        # Find earliest favorable (within 3 years, sorted by base score)
        near_term = []
        for w in formatted:
            try:
                start_dt = datetime.strptime(w["start"], "%Y-%m-%d")
                if start_dt <= three_years_later:
                    near_term.append(w)
            except:
                pass
        
        if near_term:
            # Sort by base score to find best near-term window
            near_term_sorted = sorted(near_term, key=lambda x: x.get("score", 0), reverse=True)
            earliest_start = near_term_sorted[0]["start"]
            for w in formatted:
                if w["start"] == earliest_start:
                    w["is_earliest_favorable"] = True
                    break
        
        # Find overall best (highest final_score or score)
        if any("final_score" in w for w in formatted):
            best_idx = max(range(len(formatted)), key=lambda i: formatted[i].get("final_score", 0))
        else:
            best_idx = max(range(len(formatted)), key=lambda i: formatted[i].get("score", 0))
        
        formatted[best_idx]["is_overall_best"] = True
        
        # Log for debugging
        earliest = next((w for w in formatted if w.get("is_earliest_favorable")), None)
        overall = next((w for w in formatted if w.get("is_overall_best")), None)
        if earliest and overall and earliest["start"] != overall["start"]:
            logger.info(f"DUAL DATES: Earliest favorable={earliest['start']}, Overall best={overall['start']}")
    
    return formatted


# ========================================
# OPTIMIZED ASYNC TRANSIT SCORING (NEW!)
# ========================================

async def apply_transit_scores_to_windows_async(
    windows: List[Dict],
    dob: str,
    tob: str,
    sex: str,
    lat: float,
    lon: float,
    tzone: str = "5.5"
) -> List[Dict]:
    """
    Apply transit scores to timing windows using PARALLEL API calls.
    
    THIS IS THE KEY OPTIMIZATION that fixes the timeout issue!
    
    Instead of fetching transit data sequentially for each window (slow),
    we collect all dates and fetch ALL transit data at once (fast).
    
    Args:
        windows: List of timing windows with start/end dates
        dob: Birth date (DD/MM/YYYY)
        tob: Birth time (HH:MM)
        sex: Gender for KP snapshot
        lat: Latitude
        lon: Longitude
        tzone: Timezone offset string
    
    Returns:
        Windows with transit_score and final_score added
    """
    from app.services.astro_api import vedic_api
    
    if not windows:
        return windows
    
    logger.info(f"🚀 OPTIMIZED: Scoring {len(windows)} windows with PARALLEL transit fetches")
    
    try:
        # Step 1: Calculate all midpoint dates
        midpoint_dates = []
        for w in windows:
            start = w.get("start")
            end = w.get("end")
            
            # Parse dates if they're strings
            if isinstance(start, str):
                start = datetime.strptime(start, "%Y-%m-%d")
            if isinstance(end, str):
                end = datetime.strptime(end, "%Y-%m-%d")
            
            # Calculate midpoint
            mid = start + (end - start) / 2
            midpoint_dates.append(mid)
        
        # Step 2: Fetch ALL data in parallel (THE MAGIC!)
        logger.info(f"⚡ Fetching {len(midpoint_dates)} transit+KP datasets in parallel...")
        transit_results, kp_results = await vedic_api.fetch_all_timing_data_async(
            dates=midpoint_dates,
            dob=dob,
            tob=tob,
            sex=sex,
            lat=lat,
            lon=lon,
            tzone=tzone
        )
        
        # Step 3: Score each window using the pre-fetched data
        for i, w in enumerate(windows):
            try:
                transit_raw = transit_results[i]
                kp_raw = kp_results[i]
                
                if transit_raw and kp_raw:
                    # Merge and score
                    merged = merge_transit_data(transit_raw, kp_raw)
                    t_score = kp_transit_score(w, merged)
                    
                    w["transit_score"] = round(t_score, 2)
                    w["final_score"] = w.get("_domain_score", w.get("total_score", 0)) + t_score
                else:
                    # No transit data available
                    w["transit_score"] = 0
                    w["final_score"] = w.get("_domain_score", w.get("total_score", 0))
                    
            except Exception as e:
                logger.debug(f"Transit scoring failed for window {i}: {e}")
                w["transit_score"] = 0
                w["final_score"] = w.get("_domain_score", w.get("total_score", 0))
        
        # Re-sort by final score
        windows.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        logger.info(f"✅ OPTIMIZED: Scored {len(windows)} windows successfully")
        return windows
        
    except Exception as e:
        logger.exception(f"❌ Parallel transit scoring failed: {e}")
        # Fallback: just use domain scores without transit
        for w in windows:
            w["transit_score"] = 0
            w["final_score"] = w.get("_domain_score", w.get("total_score", 0))
        return windows


class KPTimingEngine:
    """
    Main class for KP timing calculations.
    
    Provides a clean interface for calculating timing windows
    with full KP methodology, including optional transit scoring.
    """
    
    def __init__(self):
        self.transit_cache = {}
    
    def calculate_timing_windows(
        self,
        dba_list: List[Dict],
        dob: datetime,
        planets: Dict[str, Dict],
        houses: List[Dict],
        domain: str,
        timing_name: Optional[str] = None,
        max_windows: int = 10
    ) -> List[Dict]:
        """
        Calculate timing windows using full KP methodology.
        
        Args:
            dba_list: List of dasha periods
            dob: Date of birth
            planets: Normalized planet data
            houses: Normalized house data
            domain: Domain name
            timing_name: Optional specific timing rule name
            max_windows: Maximum windows to return
        
        Returns:
            Formatted timing windows
        """
        # Determine timing name if not provided
        if not timing_name:
            timing_name = self._get_timing_name(domain)
        
        try:
            windows = get_top_timing_windows(
                dba_list=dba_list,
                dob=dob,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=max_windows
            )
            
            return format_timing_windows(windows)
            
        except Exception as e:
            logger.exception(f"Timing calculation error: {e}")
            return []
    
    def calculate_timing_windows_with_transit(
        self,
        dba_list: List[Dict],
        dob: datetime,
        planets: Dict[str, Dict],
        houses: List[Dict],
        domain: str,
        fetch_transit_for_date: callable,
        fetch_kp_snapshot: callable,
        sex: str,
        lat: float,
        lon: float,
        tzone: str = "5.5",
        timing_name: Optional[str] = None,
        max_windows: int = 10
    ) -> List[Dict]:
        """
        Calculate timing windows with transit scoring.
        
        This method adds transit analysis to the timing calculation,
        providing more accurate predictions based on planetary transits
        at the midpoint of each timing window.
        
        Args:
            dba_list: List of dasha periods
            dob: Date of birth
            planets: Normalized planet data
            houses: Normalized house data
            domain: Domain name
            fetch_transit_for_date: Callable(date) -> transit chart dict
            fetch_kp_snapshot: Callable(date, sex, lat, lon, tzone) -> KP planets dict
            sex: Gender for KP snapshot
            lat: Latitude
            lon: Longitude
            tzone: Timezone offset string
            timing_name: Optional specific timing rule name
            max_windows: Maximum windows to return
        
        Returns:
            Formatted timing windows with transit scores
        """
        # Determine timing name if not provided
        if not timing_name:
            timing_name = self._get_timing_name(domain)
        
        try:
            # Get base timing windows using NOTEBOOK-MATCHING logic
            logger.info("Using notebook-matching timing logic (get_top_timing_windows)")
            
            windows = get_top_timing_windows(
                dba_list=dba_list,
                dob=dob,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=max_windows * 2  # Get more windows before transit filtering
            )
            
            logger.info(f"Timing engine returned {len(windows)} windows")
            logger.info(f"Applying transit scores to {len(windows)} windows")
            
            # Apply transit scores
            windows_with_transit = apply_transit_scores_to_windows(
                windows=windows,
                fetch_transit_for_date=fetch_transit_for_date,
                fetch_kp_snapshot=fetch_kp_snapshot,
                sex=sex,
                lat=lat,
                lon=lon,
                tzone=tzone
            )
            
            # Take top windows after transit scoring
            top_windows = windows_with_transit[:max_windows]
            
            return format_timing_windows(top_windows, include_transit=True)
            
        except Exception as e:
            logger.exception(f"Timing calculation with transit error: {e}")
            # Fallback to standard timing without transit
            return self.calculate_timing_windows(
                dba_list=dba_list,
                dob=dob,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=max_windows
            )
    
    def score_single_transit(
        self,
        window: Dict,
        transit_chart: Dict[str, Dict],
        kp_planets: Dict[str, Dict]
    ) -> float:
        """
        Score a single timing window against transit data.
        
        Useful for evaluating specific dates without fetching new data.
        
        Args:
            window: Timing window with maha/antara/paryantar
            transit_chart: Transit positions for a specific date
            kp_planets: KP planet data for the same date
        
        Returns:
            Transit score for the window
        """
        merged = merge_transit_data(transit_chart, kp_planets)
        return kp_transit_score(window, merged)
    
    def _get_timing_name(self, domain: str) -> str:
        """
        Fallback timing name resolver.
        Used ONLY when caller does not explicitly provide timing_name.
        """
        mapping = {
            "Marriage": "Marriage Timing",
            "Career": "Job Start Timing",
            "Business": "Business Start Timing",   # ✅ ADD THIS
            "Child": "Education Timing",
            "Parenting": "Timing of Childbirth",
            "Foreign": "Foreign Timing",
            "Love_Life": "Marriage Timing",
            "Divorce": "Divorce Timing",
            "Finance": "Loan Repayment Timing",
            "Property": "Prospects of Property",
            "Vehicles": "Vehicle Purchase Timing",
            "Health": "Health Risk Timing"
        }

        timing = mapping.get(domain, "Marriage Timing")
        logger.warning(f"[KP] Using fallback timing '{timing}' for domain '{domain}'")
        return timing

    def get_ruling_planets(self, planets: Dict[str, Dict]) -> List[str]:
        """Get ruling planets for the chart"""
        return get_kp_ruling_planets(planets)
    
    def get_planet_scores(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        timing_name: str
    ) -> Dict[str, Dict]:
        """Get KP scores for all planets"""
        timing_rules = TIMING_RULES.get(timing_name, TIMING_RULES.get("Marriage Timing"))
        scores = score_kp_all_planets(planets, houses, timing_rules)
        return {s["planet"]: s for s in scores}


# Singleton instance
kp_timing_engine = KPTimingEngine()
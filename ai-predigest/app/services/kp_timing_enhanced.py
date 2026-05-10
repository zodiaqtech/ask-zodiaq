"""
KP Timing Enhanced - Proper Dasha Traversal with House-Specific Gating

This module implements the COMPLETE KP timing methodology that was missing:
1. Planet signification tracking (which houses each planet signifies)
2. House-specific dasha gating (MD/AD/PD must signify domain houses)
3. Hierarchical dasha traversal (MD → AD → PD filtering)
4. Strong vs weak significator pruning
5. Deterministic timing windows

Ported from notebook implementation with proper KP rules.
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.core.astro_constants import normalize_planet_name, RASI_LORDS

logger = logging.getLogger(__name__)


# ============================================================
# HOUSE SIGNIFICATION ENGINE
# ============================================================

def compute_planet_significations(
    planets: Dict[str, Dict],
    houses: List[Dict]
) -> Dict[str, Set[int]]:
    """
    Compute which houses each planet signifies through KP rules.
    
    KP Signification Order:
    1. House occupied (S1) - planet physically in the house
    2. Star lord's house (S2) - house occupied by nakshatra lord
    3. Sub lord's house (S3) - house occupied by sub lord
    4. Houses owned (S1b) - houses where planet is sign lord
    
    Rahu/Ketu special rules:
    - Do NOT signify house of occupation directly
    - Signify through sign lord, star lord, sub lord
    
    Returns:
        Dict mapping planet name to set of signified house numbers
    """
    logger.info("===== COMPUTE PLANET SIGNIFICATIONS DEBUG =====")
    
    # Build house rulership lookup
    house_lords = {}  # {house_no: lord_planet}
    for h in houses:
        rasi = h.get("start_rasi")
        lord = RASI_LORDS.get(rasi)
        if lord:
            house_lords[h.get("house")] = lord
    
    logger.info(f"House lords: {house_lords}")
    
    # Reverse lookup: which houses does each planet rule
    ruled_houses = defaultdict(set)
    for house_no, lord in house_lords.items():
        ruled_houses[lord].add(house_no)
    
    logger.info(f"Ruled houses: {dict(ruled_houses)}")
    
    # Compute significations for each planet
    significations = {}
    
    for pname, pinfo in planets.items():
        if pname == "Ascendant":
            continue
        
        norm_name = normalize_planet_name(pname)
        if not norm_name:
            continue
        
        sigs = set()
        
        # Get planet details
        S1 = pinfo.get("house")  # House occupied
        nak_lord = normalize_planet_name(pinfo.get("nakshatra_lord"))
        sub_lord = normalize_planet_name(pinfo.get("sub_lord"))
        sign_lord = normalize_planet_name(
            pinfo.get("rashi_lord") or 
            RASI_LORDS.get(pinfo.get("sign") or pinfo.get("rasi"))
        )
        
        logger.info(f"  {norm_name}: house={S1}, nak_lord={nak_lord}, sub_lord={sub_lord}, sign_lord={sign_lord}")
        
        # For Rahu/Ketu - special handling (no direct house occupation)
        if norm_name in ("Rahu", "Ketu"):
            # Rahu/Ketu signify through their lords only
            if sign_lord and sign_lord in planets:
                sl_house = planets[sign_lord].get("house")
                if sl_house:
                    sigs.add(sl_house)
                # Also add houses ruled by sign lord
                sigs.update(ruled_houses.get(sign_lord, set()))
            
            if nak_lord and nak_lord in planets:
                nl_house = planets[nak_lord].get("house")
                if nl_house:
                    sigs.add(nl_house)
                sigs.update(ruled_houses.get(nak_lord, set()))
            
            if sub_lord and sub_lord in planets:
                subl_house = planets[sub_lord].get("house")
                if subl_house:
                    sigs.add(subl_house)
                sigs.update(ruled_houses.get(sub_lord, set()))
        else:
            # Normal planets - full signification
            
            # S1: House occupied
            if isinstance(S1, int):
                sigs.add(S1)
            
            # S2: Star lord's house
            if nak_lord and nak_lord in planets:
                nl_house = planets[nak_lord].get("house")
                if nl_house:
                    sigs.add(nl_house)
            
            # S3: Sub lord's house  
            if sub_lord and sub_lord in planets:
                sl_house = planets[sub_lord].get("house")
                if sl_house:
                    sigs.add(sl_house)
            
            # S1b: Houses owned
            sigs.update(ruled_houses.get(norm_name, set()))
        
        significations[norm_name] = sigs
        logger.info(f"    {norm_name} signifies: {sorted(sigs)}")
    
    logger.info("===== END COMPUTE PLANET SIGNIFICATIONS =====")
    return significations


def get_signification_strength(
    planet_name: str,
    planets: Dict[str, Dict],
    houses: List[Dict],
    target_houses: Set[int]
) -> Dict[str, Any]:
    """
    Calculate signification strength for a planet towards target houses.
    
    Strength levels:
    - S1 (occupation): Weight 1.5
    - S2 (star lord): Weight 1.2
    - S3 (sub lord): Weight 1.0
    - S1b (ownership): Weight 0.7
    
    Returns:
        Dict with:
        - signifies: bool - whether planet signifies any target house
        - strength: float - total signification strength
        - strong: bool - whether this is a strong significator
        - levels: list - which levels (S1/S2/S3/S1b) hit target houses
    """
    pname = normalize_planet_name(planet_name)
    pinfo = planets.get(pname, {})
    
    if not pinfo:
        return {"signifies": False, "strength": 0, "strong": False, "levels": []}
    
    # Build house rulership
    ruled_houses = defaultdict(set)
    for h in houses:
        rasi = h.get("start_rasi")
        lord = RASI_LORDS.get(rasi)
        if lord:
            ruled_houses[lord].add(h.get("house"))
    
    strength = 0
    levels = []
    
    # S1: Occupation
    S1 = pinfo.get("house")
    if isinstance(S1, int) and S1 in target_houses:
        if pname not in ("Rahu", "Ketu"):  # Rahu/Ketu don't count S1
            strength += 1.5
            levels.append("S1")
    
    # S2: Star lord
    nak_lord = normalize_planet_name(pinfo.get("nakshatra_lord"))
    if nak_lord and nak_lord in planets:
        nl_house = planets[nak_lord].get("house")
        if nl_house in target_houses:
            strength += 1.2
            levels.append("S2")
    
    # S3: Sub lord
    sub_lord = normalize_planet_name(pinfo.get("sub_lord"))
    if sub_lord and sub_lord in planets:
        sl_house = planets[sub_lord].get("house")
        if sl_house in target_houses:
            strength += 1.0
            levels.append("S3")
    
    # S1b: Ownership
    owned = ruled_houses.get(pname, set())
    if owned & target_houses:
        strength += 0.7
        levels.append("S1b")
    
    return {
        "signifies": strength > 0,
        "strength": round(strength, 2),
        "strong": strength >= 1.5,  # Strong if S1 hit or S2+S3
        "levels": levels
    }


# ============================================================
# HIERARCHICAL DASHA GATING
# ============================================================

def gate_dasha_by_house_signification(
    dba_periods: List[Dict],
    planets: Dict[str, Dict],
    houses: List[Dict],
    positive_houses: Set[int],
    strict_mode: bool = False
) -> Tuple[List[Dict], Dict]:
    """
    Filter dasha periods based on house signification.
    
    KP Timing Rule:
    For an event to manifest, the MD-AD-PD sequence should all
    signify the houses relevant to that event.
    
    For Marriage (2/7/11):
    - MD should signify 2, 7, or 11
    - AD should signify 2, 7, or 11
    - PD should signify 2, 7, or 11
    
    Args:
        dba_periods: List of paryantar dasha periods
        planets: Planet data dict
        houses: House data list
        positive_houses: Set of domain-positive houses (e.g., {2,7,11})
        strict_mode: If True, all 3 levels must signify. If False, 2 of 3 sufficient.
    
    Returns:
        Tuple of (filtered_periods, stats_dict)
    """
    # Pre-compute significations for all planets
    planet_sigs = compute_planet_significations(planets, houses)
    
    # Log which planets signify the target houses
    logger.info(f"Positive houses for gating: {positive_houses}")
    for pname, sigs in planet_sigs.items():
        hits = sigs & positive_houses
        if hits:
            logger.info(f"  {pname} signifies positive houses: {sorted(hits)}")
    
    stats = {
        "input_count": len(dba_periods),
        "md_filtered": 0,
        "ad_filtered": 0,
        "pd_filtered": 0,
        "passed": 0
    }
    
    filtered = []
    
    for period in dba_periods:
        md = normalize_planet_name(period.get("maha") or period.get("md"))
        ad = normalize_planet_name(period.get("antara") or period.get("ad"))
        pd = normalize_planet_name(period.get("paryantar") or period.get("pd"))
        
        # Check significations
        md_sigs = planet_sigs.get(md, set())
        ad_sigs = planet_sigs.get(ad, set())
        pd_sigs = planet_sigs.get(pd, set())
        
        md_hits = bool(md_sigs & positive_houses)
        ad_hits = bool(ad_sigs & positive_houses)
        pd_hits = bool(pd_sigs & positive_houses)
        
        hits = sum([md_hits, ad_hits, pd_hits])
        
        if strict_mode:
            # All 3 must signify
            passes = hits == 3
        else:
            # At least 2 of 3 must signify (relaxed for practical use)
            passes = hits >= 2
        
        if not passes:
            if not md_hits:
                stats["md_filtered"] += 1
            elif not ad_hits:
                stats["ad_filtered"] += 1
            else:
                stats["pd_filtered"] += 1
            continue
        
        # Add signification info to period
        enhanced = dict(period)
        enhanced["_md_signifies"] = list(md_sigs & positive_houses)
        enhanced["_ad_signifies"] = list(ad_sigs & positive_houses)
        enhanced["_pd_signifies"] = list(pd_sigs & positive_houses)
        enhanced["_signification_hits"] = hits
        
        filtered.append(enhanced)
        stats["passed"] += 1
    
    return filtered, stats


def prune_weak_significators(
    dba_periods: List[Dict],
    planets: Dict[str, Dict],
    houses: List[Dict],
    positive_houses: Set[int],
    negative_houses: Optional[Set[int]] = None
) -> List[Dict]:
    """
    Prune periods where significators are weak.
    
    A significator is weak if:
    - It only signifies through S1b (ownership) without S1/S2/S3
    - Its signification strength is below threshold
    - It signifies negative houses (6/8/12) more than positive houses
    
    Returns:
        Filtered list with weak significator periods removed
    """
    NEG_HOUSES = negative_houses or {6, 8, 12}

    
    pruned = []
    
    for period in dba_periods:
        md = normalize_planet_name(period.get("maha") or period.get("md"))
        ad = normalize_planet_name(period.get("antara") or period.get("ad"))
        pd = normalize_planet_name(period.get("paryantar") or period.get("pd"))
        
        # Check strength for each dasha lord
        md_str = get_signification_strength(md, planets, houses, positive_houses)
        ad_str = get_signification_strength(ad, planets, houses, positive_houses)
        pd_str = get_signification_strength(pd, planets, houses, positive_houses)
        
        # Check negative significations
        md_neg = get_signification_strength(md, planets, houses, NEG_HOUSES)
        ad_neg = get_signification_strength(ad, planets, houses, NEG_HOUSES)
        
        # Pruning rules:
        # 1. MD must be at least moderately strong
        if md_str["strength"] < 0.7 and not md_str["strong"]:
            continue
        
        # 2. AD must signify with decent strength
        if ad_str["strength"] < 0.5:
            continue
        
        # 3. MD's positive should outweigh negative
        if md_neg["strength"] > md_str["strength"] * 1.5:
            continue
        
        # Store strength info
        enhanced = dict(period)
        enhanced["_md_strength"] = md_str
        enhanced["_ad_strength"] = ad_str
        enhanced["_pd_strength"] = pd_str
        
        pruned.append(enhanced)
    
    return pruned


# ============================================================
# DETERMINISTIC TIMING WINDOWS
# ============================================================

def calculate_timing_score(
    period: Dict,
    planets: Dict[str, Dict],
    houses: List[Dict],
    domain_rules: Dict[str, Any]
) -> float:
    """
    Calculate deterministic timing score for a dasha period.

    Scoring formula:
    - Base: MD_strength * 3 + AD_strength * 2 + PD_strength * 1
    - Bonus: Key planet presence, domain-specific natural karakas
    - Penalty: Negative house signification (reduced weight)
    """

    positive_houses = set(domain_rules.get("positive_houses", set()))
    key_planets = set(domain_rules.get("key_planets", set()))
    neg_houses = set(domain_rules.get("negative_houses", {6, 8, 12}))


    # --------------------------------------------------
    # DOMAIN-AWARE NATURAL KARAKAS (CRITICAL FIX)
    # --------------------------------------------------
    domain_name = domain_rules.get("domain", "Marriage")

    if domain_name == "Parenting":
        natural_karakas = {
            "Jupiter": 5,
            "Moon": 3,
            "Venus": 2
        }

    elif domain_name == "Career":
        natural_karakas = {
            "Saturn": 5,   # Karma, profession, promotions
            "Mercury": 4,  # Job, skills, contracts
            "Sun": 3,      # Authority, government, leadership
            "Jupiter": 2   # Growth, advisory roles
        }

    else:  # Marriage default
        natural_karakas = {
            "Venus": 5,
            "Jupiter": 3,
            "Moon": 2
        }


    # --------------------------------------------------
    # DASHA LORDS
    # --------------------------------------------------
    md = normalize_planet_name(period.get("maha") or period.get("md"))
    ad = normalize_planet_name(period.get("antara") or period.get("ad"))
    pd = normalize_planet_name(period.get("paryantar") or period.get("pd"))

    # --------------------------------------------------
    # POSITIVE SIGNIFICATION STRENGTH
    # --------------------------------------------------
    md_pos = get_signification_strength(md, planets, houses, positive_houses)
    ad_pos = get_signification_strength(ad, planets, houses, positive_houses)
    pd_pos = get_signification_strength(pd, planets, houses, positive_houses)

    # --------------------------------------------------
    # NEGATIVE SIGNIFICATION STRENGTH
    # --------------------------------------------------
    md_neg = get_signification_strength(md, planets, houses, neg_houses)
    ad_neg = get_signification_strength(ad, planets, houses, neg_houses)
    pd_neg = get_signification_strength(pd, planets, houses, neg_houses)

    # --------------------------------------------------
    # BASE SCORE (KP HIERARCHY)
    # --------------------------------------------------
    score = (
        md_pos["strength"] * 3 +
        ad_pos["strength"] * 2 +
        pd_pos["strength"] * 1
    )

    # --------------------------------------------------
    # PENALTY (NEGATIVE HOUSES — SOFT)
    # --------------------------------------------------
    penalty = (
        md_neg["strength"] * 1.0 +
        ad_neg["strength"] * 0.7 +
        pd_neg["strength"] * 0.5
    )

    # --------------------------------------------------
    # KEY PLANET BONUS
    # --------------------------------------------------
    if md in key_planets:
        score += 4
    if ad in key_planets:
        score += 3
    if pd in key_planets:
        score += 2

    # --------------------------------------------------
    # NATURAL KARAKA BONUS (DOMAIN-AWARE)
    # --------------------------------------------------
    if ad in natural_karakas:
        score += natural_karakas[ad]
        logger.debug(f"Natural karaka bonus for AD={ad}: +{natural_karakas[ad]}")

    if pd in natural_karakas:
        score += natural_karakas[pd] * 0.5

    # --------------------------------------------------
    # STRONG SIGNIFICATOR BONUS
    # --------------------------------------------------
    if md_pos["strong"]:
        score += 3
    if ad_pos["strong"]:
        score += 2

    return round(score - penalty, 2)



def get_deterministic_timing_windows(
    dba_periods: List[Dict],
    planets: Dict[str, Dict],
    houses: List[Dict],
    domain_rules: Dict[str, Any],
    dob: datetime,
    domain: str = "Marriage",
    max_windows: int = 100,
    strict_house_gating: bool = False
) -> List[Dict]:
    """
    Main function to get deterministic timing windows using full KP methodology.
    
    Process (notebook-accurate):
    1. Gate by house signification (MD/AD/PD must signify positive houses)
    2. Prune weak significators
    3. Filter by age range
    4. Calculate deterministic scores
    5. Sort and return top windows
    
    Args:
        dba_periods: List of paryantar dasha periods
        planets: Planet data dict
        houses: House data list
        domain_rules: Domain-specific rules
        dob: Date of birth
        domain: Domain name for age filtering
        max_windows: Max windows to return
        strict_house_gating: If True, all 3 levels must signify
    
    Returns:
        Top timing windows sorted by score
    """
    logger.info("===== get_deterministic_timing_windows =====")
    logger.info(f"Input periods: {len(dba_periods)}")
    domain_rules = dict(domain_rules)
    domain_rules["domain"] = domain

    
    positive_houses = set(domain_rules.get("positive_houses", {2, 7, 11}))
    
    # Step 1: House signification gating
    gated, gate_stats = gate_dasha_by_house_signification(
        dba_periods, planets, houses, positive_houses, 
        strict_mode=strict_house_gating
    )
    logger.info(f"After house gating: {len(gated)} periods")
    logger.info(f"  MD filtered: {gate_stats['md_filtered']}")
    logger.info(f"  AD filtered: {gate_stats['ad_filtered']}")
    logger.info(f"  PD filtered: {gate_stats['pd_filtered']}")
    
    # Step 2: Prune weak significators
    negative_houses = set(domain_rules.get("negative_houses", {6, 8, 12}))
    pruned = prune_weak_significators(gated, planets, houses, positive_houses, negative_houses)
    logger.info(f"After weak pruning: {len(pruned)} periods")
    
    # Step 3: Age filtering
    from app.services.timing_engine import filter_by_age, VALID_AGE_RANGES
    
    after_age = filter_by_age(pruned, dob, domain)
    logger.info(f"After age filter: {len(after_age)} periods")
    
    # Step 4: Calculate scores with TIME PREFERENCE
    scored = []
    now = datetime.now()
    
    for period in after_age:
        score = calculate_timing_score(period, planets, houses, domain_rules)
        period_copy = dict(period)
        
        # TIME PREFERENCE: Earlier dates get bonus (max 5 points for dates within 2 years)
        start_date = period.get("start")
        if start_date:
            if isinstance(start_date, str):
                try:
                    start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                except:
                    start_date = None
            
            if start_date:
                years_away = (start_date - now).days / 365.25
                if years_away < 0:
                    years_away = 0  # Already passed, no bonus
                
                # Bonus decreases as date gets further away
                # 2 years away = +5, 5 years = +2, 10 years = 0
                if years_away <= 2:
                    time_bonus = 5
                elif years_away <= 5:
                    time_bonus = 5 - (years_away - 2)  # 5 to 2
                elif years_away <= 10:
                    time_bonus = 2 - (years_away - 5) * 0.4  # 2 to 0
                else:
                    time_bonus = 0
                
                score += max(0, time_bonus)
                period_copy["_time_bonus"] = round(time_bonus, 2)
        
        period_copy["_deterministic_score"] = round(score, 2)
        scored.append(period_copy)
    
    # Step 5: Sort by score and return top windows
    scored.sort(key=lambda x: x["_deterministic_score"], reverse=True)
    
    final = scored[:max_windows]
    
    # Log top 5 windows for debugging
    logger.info("Top 5 windows after scoring:")
    for i, w in enumerate(final[:5]):
        md = w.get('maha') or w.get('md')
        ad = w.get('antara') or w.get('ad')
        pd = w.get('paryantar') or w.get('pd')
        start = w.get('start')
        score = w.get('_deterministic_score', 0)
        time_bonus = w.get('_time_bonus', 0)
        logger.info(f"  #{i+1}: {md}-{ad}-{pd} | {start} | score={score} (time_bonus={time_bonus})")
    
    if final:
        best = final[0]
        logger.info(f"Best window: {best.get('maha')}-{best.get('antara')}-{best.get('paryantar')}")
        logger.info(f"  Score: {best.get('_deterministic_score')}")
        logger.info(f"  Dates: {best.get('start')} to {best.get('end')}")
    
    logger.info("===== END get_deterministic_timing_windows =====")
    
    return final


# ============================================================
# HYBRID FUNCTION - COMBINES BOTH APPROACHES
# ============================================================

def get_timing_windows_hybrid(
    dba_periods: List[Dict],
    dob: datetime,
    planets: Dict[str, Dict],
    houses: List[Dict],
    domain: str,
    timing_name: str,
    use_deterministic: bool = True,
    max_windows: int = 100
) -> List[Dict]:
    """
    Hybrid timing function that can use either approach.
    
    Args:
        dba_periods: Paryantar dasha periods
        dob: Date of birth
        planets: Planet data
        houses: House data
        domain: Domain name (Marriage, Career, etc.)
        timing_name: Timing rule name
        use_deterministic: If True, use new deterministic approach
        max_windows: Max windows to return
    
    Returns:
        Top timing windows
    """
    from app.services.timing_engine import TIMING_RULES, get_top_timing_windows
    
    timing_rules = TIMING_RULES.get(timing_name, TIMING_RULES.get("Marriage Timing"))
    
    if use_deterministic:
        return get_deterministic_timing_windows(
            dba_periods=dba_periods,
            planets=planets,
            houses=houses,
            domain_rules=timing_rules,
            dob=dob,
            domain=domain,
            max_windows=max_windows,
            strict_house_gating=False  # Start with relaxed mode
        )
    else:
        # Fall back to existing implementation
        return get_top_timing_windows(
            dba_list=dba_periods,
            dob=dob,
            planets=planets,
            houses=houses,
            domain=domain,
            timing_name=timing_name,
            max_windows=max_windows
        )


# ============================================================
# DIAGNOSTIC FUNCTIONS
# ============================================================

def diagnose_timing_gaps(
    dba_periods: List[Dict],
    planets: Dict[str, Dict],
    houses: List[Dict],
    positive_houses: Set[int]
) -> Dict[str, Any]:
    """
    Diagnose why timing windows might be off.
    
    Returns detailed analysis of:
    - Planet significations
    - Which planets signify target houses
    - Potential issues with dasha filtering
    """
    planet_sigs = compute_planet_significations(planets, houses)
    
    # Find strong significators
    strong_sigs = []
    weak_sigs = []
    non_sigs = []
    
    for pname, sigs in planet_sigs.items():
        overlap = sigs & positive_houses
        if overlap:
            strength = get_signification_strength(pname, planets, houses, positive_houses)
            if strength["strong"]:
                strong_sigs.append({
                    "planet": pname,
                    "signifies": list(overlap),
                    "strength": strength["strength"],
                    "levels": strength["levels"]
                })
            else:
                weak_sigs.append({
                    "planet": pname,
                    "signifies": list(overlap),
                    "strength": strength["strength"],
                    "levels": strength["levels"]
                })
        else:
            non_sigs.append(pname)
    
    # Check MD coverage
    md_planets = set()
    for period in dba_periods[:100]:  # Sample
        md = normalize_planet_name(period.get("maha") or period.get("md"))
        if md:
            md_planets.add(md)
    
    md_sigs_positive = [p for p in md_planets if planet_sigs.get(p, set()) & positive_houses]
    md_sigs_negative = [p for p in md_planets if not (planet_sigs.get(p, set()) & positive_houses)]
    
    return {
        "strong_significators": strong_sigs,
        "weak_significators": weak_sigs,
        "non_significators": non_sigs,
        "maha_dashas_positive": md_sigs_positive,
        "maha_dashas_negative": md_sigs_negative,
        "recommendation": (
            "Use relaxed house gating if too few windows" 
            if len(strong_sigs) < 3 
            else "Full house gating should work"
        )
    }

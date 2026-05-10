"""
General Kundali Analysis Evaluator - ENHANCED v4.0

ENHANCEMENTS:
✅ _extract_timing_windows now handles TimingWindow objects (not just dicts)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP analysis preserved and passed to LLM
✅ Excel-based question config integration
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations (0-100 score)
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)

Weightage:
- House Lords (Vedic): 50%
- KP Analysis: 30% (where applicable)
- Dasha Timing: 20%
- Other factors (aspects, yogas): 10%

Evaluates comprehensive birth chart including:
- Current Period Analysis (Dasha analysis)
- Dosha Analysis (Sade Sati, Graha Doshas)
- Planetary Transits
- Periods of Success (Raj Yoga, Dhana Yoga, Sanyasa Yoga timing)
- Remedies and Suggestions
"""
from typing import Dict, List, Any, Set, Optional, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal, TimingWindow
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, _has_evil_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, is_combust, has_dig_bala,
    detect_aspects, BENEFICS, MALEFICS, RASI_LORDS
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# DIGNITY TABLE FOR STRENGTH CALCULATIONS
# ═══════════════════════════════════════════════════════════════════
EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
}

DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"
}

OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"], "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"], "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"], "Rahu": ["Aquarius"], "Ketu": ["Scorpio"]
}

FRIENDLY_SIGNS = {
    "Sun": ["Aries", "Leo", "Sagittarius", "Scorpio"],
    "Moon": ["Taurus", "Cancer", "Scorpio"],
    "Mars": ["Aries", "Leo", "Sagittarius", "Scorpio", "Capricorn", "Pisces"],
    "Mercury": ["Gemini", "Virgo", "Taurus", "Libra"],
    "Jupiter": ["Aries", "Leo", "Sagittarius", "Cancer", "Scorpio", "Pisces"],
    "Venus": ["Taurus", "Libra", "Gemini", "Virgo", "Capricorn", "Aquarius"],
    "Saturn": ["Capricorn", "Aquarius", "Taurus", "Libra", "Gemini", "Virgo"]
}


class GeneralKundaliAnalysisEvaluator(BaseEvaluator):
    """
    ENHANCED Evaluator for General Kundali Analysis subtopic.
    
    Analyzes:
    - Current dasha periods and planetary strength
    - Doshas (Sade Sati, planetary afflictions)
    - Current and upcoming transits
    - Timing of success periods (yogas)
    - Remedial measures
    
    ENHANCED with:
    - House lords with dignity analysis
    - KP compatibility (CSL analysis)
    - Timing windows extraction
    - Dual data source support
    """
    
    domain = "General_Guidance"
    subtopic = "General Kundali Analysis"
    
    # ═══════════════════════════════════════════════════════════════════
    # SUB-SUBDOMAIN CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════
    SUB_SUBDOMAIN_CONFIG = {
        "Current Period Analysis": {
            "positive_houses": {1, 2, 5, 9, 10, 11},
            "negative_houses": {6, 8, 12},
            "key_planets": {"Sun", "Moon", "Jupiter"},
            "description": "Dasha period and planetary strength analysis"
        },
        "Dosha Analysis": {
            "positive_houses": {1, 5, 9},
            "negative_houses": {6, 8, 12},
            "key_planets": {"Saturn", "Mars", "Rahu", "Ketu"},
            "description": "Sade Sati, Manglik, Kaal Sarp dosha analysis"
        },
        "Planetary Transits": {
            "positive_houses": {1, 2, 5, 9, 10, 11},
            "negative_houses": {6, 8, 12},
            "key_planets": {"Jupiter", "Saturn", "Rahu", "Ketu"},
            "description": "Current and upcoming transit effects"
        },
        "Periods of Success": {
            "positive_houses": {1, 5, 9, 10, 11},
            "negative_houses": {6, 8, 12},
            "key_planets": {"Jupiter", "Venus", "Mercury", "Sun"},
            "description": "Raj Yoga, Dhana Yoga timing"
        }
    }
    
    # Default house configuration
    positive_houses = {1, 2, 3, 4, 5, 9, 10, 11}
    supportive_houses = {7}
    negative_houses = {6, 8, 12}
    key_planets = {"Sun", "Moon", "Jupiter", "Venus", "Mercury"}
    
    def __init__(self):
        super().__init__()
        self._seen_points: Set[str] = set()
    
    def reset(self):
        """Reset seen points for new evaluation"""
        self._seen_points = set()
    
    def _add_point(self, point: str) -> bool:
        """Add point if not seen before, return True if added"""
        if point not in self._seen_points:
            self._seen_points.add(point)
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════════
    # MAIN EVALUATE METHOD - ENHANCED
    # ═══════════════════════════════════════════════════════════════════
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        sub_subdomain: str = "",
        meta: QueryMeta = None,
        question: str = "",
        timing_windows: Optional[Dict[str, List]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        ENHANCED evaluation combining all kundali analysis.
        
        Args:
            planets: KP planetary data
            houses: KP house data
            vedic_planets: Vedic planetary data (for house lords)
            vedic_houses: Vedic house data
            sub_subdomain: Specific sub-subdomain being evaluated
            meta: Query metadata
            question: The question being asked
            timing_windows: Timing windows for success periods
            **kwargs: Additional data (dasha_timeline, current_dasha, etc.)
        """
        self.reset()
        
        # Detect aspects first
        planets = detect_aspects(planets)
        
        result = EvaluationResult()
        additional_data = {}
        
        logger.info(f"📊 GeneralKundaliAnalysis Evaluator - sub_subdomain: {sub_subdomain}")
        logger.info(f"   KP planets: {bool(planets)}, Vedic planets: {bool(vedic_planets)}")
        logger.info(f"   Timing windows: {bool(timing_windows)}")
        
        # Get sub-subdomain specific configuration
        config = self.SUB_SUBDOMAIN_CONFIG.get(sub_subdomain, {})
        positive_houses = config.get("positive_houses", self.positive_houses)
        negative_houses = config.get("negative_houses", self.negative_houses)
        key_planets = config.get("key_planets", self.key_planets)
        
        # ═══════════════════════════════════════════════════════════════
        # 1. HOUSE LORDS ANALYSIS (50% weight)
        # ═══════════════════════════════════════════════════════════════
        house_lords_points, house_lords_data = self._evaluate_house_lords(
            planets, houses, vedic_planets, vedic_houses, sub_subdomain
        )
        result.extend_points(house_lords_points)
        additional_data["house_lords"] = house_lords_data
        
        # ═══════════════════════════════════════════════════════════════
        # 2. KP ANALYSIS (30% weight)
        # ═══════════════════════════════════════════════════════════════
        kp_points, kp_data = self._evaluate_kp_analysis(
            planets, houses, sub_subdomain
        )
        result.extend_points(kp_points)
        additional_data["kp_analysis"] = kp_data
        
        # ═══════════════════════════════════════════════════════════════
        # 3. PLANETARY STRENGTH ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        strength_points = self._evaluate_planetary_strength(planets, houses, vedic_planets)
        result.extend_points(strength_points)
        
        # ═══════════════════════════════════════════════════════════════
        # 4. DOSHA DETECTION
        # ═══════════════════════════════════════════════════════════════
        dosha_points, dosha_data = self._evaluate_doshas(planets, houses, vedic_planets)
        result.extend_points(dosha_points)
        additional_data["dosha_analysis"] = dosha_data
        
        # ═══════════════════════════════════════════════════════════════
        # 5. YOGA ANALYSIS (Success Indicators)
        # ═══════════════════════════════════════════════════════════════
        yoga_points, yoga_data = self._evaluate_yogas(planets, houses, vedic_planets)
        result.extend_points(yoga_points)
        additional_data["yoga_analysis"] = yoga_data
        
        # ═══════════════════════════════════════════════════════════════
        # 6. TIMING WINDOWS (20% weight - Dasha based)
        # ═══════════════════════════════════════════════════════════════
        if timing_windows:
            timing_points, timing_data = self._evaluate_timing_windows(
                timing_windows, sub_subdomain
            )
            result.extend_points(timing_points)
            additional_data["timing_analysis"] = timing_data
        
        # ═══════════════════════════════════════════════════════════════
        # 7. GENERAL LIFE INDICATORS
        # ═══════════════════════════════════════════════════════════════
        life_points = self._evaluate_life_indicators(planets, houses, vedic_planets)
        result.extend_points(life_points)
        
        # ═══════════════════════════════════════════════════════════════
        # 8. DASHA TIMELINE (from kwargs)
        # ═══════════════════════════════════════════════════════════════
        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")
        
        if current_dasha:
            additional_data["current_dasha"] = current_dasha
        if dasha_timeline:
            additional_data["dasha_timeline"] = dasha_timeline
        
        result.additional_data = additional_data
        
        logger.info(f"✅ GeneralKundaliAnalysis evaluation complete: {len(result.technical_points)} points")
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # HOUSE LORDS ANALYSIS (50% weight)
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_house_lords(
        self,
        planets: Dict,
        houses: List,
        vedic_planets: Optional[Dict],
        vedic_houses: Optional[List],
        sub_subdomain: str
    ) -> Tuple[List[str], Dict]:
        """
        Evaluate house lords with dignity for the relevant houses.
        Uses Vedic data if available, otherwise falls back to KP data.
        """
        points = []
        house_lords_data = {}
        
        # Determine which houses to analyze based on sub-subdomain
        if "Dosha" in sub_subdomain:
            houses_to_check = [1, 4, 6, 7, 8, 12]  # Dosha-related houses
        elif "Success" in sub_subdomain:
            houses_to_check = [1, 5, 9, 10, 11]  # Success/Yoga houses
        elif "Transit" in sub_subdomain:
            houses_to_check = [1, 2, 4, 7, 10]  # Major life areas
        else:
            houses_to_check = [1, 2, 4, 5, 7, 9, 10, 11]  # General analysis
        
        # Use Vedic data if available, otherwise KP
        use_vedic = vedic_planets and vedic_houses
        planet_data = vedic_planets if use_vedic else planets
        house_data = vedic_houses if use_vedic else houses
        
        data_source = "Vedic" if use_vedic else "KP"
        logger.debug(f"House lords using {data_source} data")
        
        for house_num in houses_to_check:
            lord_name = self._get_house_lord(house_data, house_num)
            if not lord_name:
                continue
            
            lord_planet = _p(planet_data, lord_name)
            if not lord_planet:
                continue
            
            # Calculate dignity
            dignity = self._calculate_dignity(lord_planet, lord_name)
            strength = self._calculate_lord_strength(lord_planet, lord_name, dignity)
            
            # Get house signification
            house_signification = self._get_house_signification(house_num)
            
            # Format point
            dignity_str = dignity.upper() if dignity else "Neutral"
            point = f"⭐ House {house_num} ({house_signification}): Lord {lord_name} is {dignity_str} (Strength: {strength}/100)"
            
            # Add affliction info
            afflictions = self._check_lord_afflictions(lord_planet, lord_name, planets)
            if afflictions:
                point += f" [{', '.join(afflictions)}]"
            
            if self._add_point(point):
                points.append(point)
            
            house_lords_data[f"house_{house_num}"] = {
                "lord": lord_name,
                "dignity": dignity,
                "strength": strength,
                "afflictions": afflictions,
                "signification": house_signification
            }
        
        return points, house_lords_data
    
    def _get_house_lord(self, houses: List, house_num: int) -> str:
        """Get the lord of a house"""
        if not houses:
            return ""
        
        for h in houses:
            if h.get("house") == house_num:
                # Try different field names
                lord = (h.get("rashi_lord") or h.get("sign_lord") or 
                       h.get("lord") or h.get("start_rasi"))
                if lord and lord in RASI_LORDS:
                    return RASI_LORDS.get(lord, lord)
                return lord
        
        return ""
    
    def _calculate_dignity(self, planet_data: Dict, planet_name: str) -> str:
        """Calculate planetary dignity"""
        if not planet_data:
            return "neutral"
        
        sign = planet_data.get("sign") or planet_data.get("rasi") or ""
        
        # Check exaltation
        if EXALTATION_SIGNS.get(planet_name) == sign:
            return "exalted"
        
        # Check debilitation
        if DEBILITATION_SIGNS.get(planet_name) == sign:
            return "debilitated"
        
        # Check own sign
        if sign in OWN_SIGNS.get(planet_name, []):
            return "own_sign"
        
        # Check friendly sign
        if sign in FRIENDLY_SIGNS.get(planet_name, []):
            return "friendly"
        
        return "neutral"
    
    def _calculate_lord_strength(self, planet_data: Dict, planet_name: str, dignity: str) -> int:
        """Calculate strength score (0-100)"""
        score = 50  # Base score
        
        # Dignity adjustments
        dignity_scores = {
            "exalted": 40,
            "own_sign": 30,
            "friendly": 15,
            "neutral": 0,
            "debilitated": -35
        }
        score += dignity_scores.get(dignity, 0)
        
        # Retrograde adjustment
        is_retro = str(planet_data.get("is_retro", "")).lower() in ("true", "1", "yes")
        if is_retro:
            if planet_name in ["Jupiter", "Venus", "Mercury"]:
                score += 5  # Benefics gain strength when retrograde
            else:
                score -= 10
        
        # Combustion check
        if planet_data.get("is_combusted") or planet_data.get("is_combust"):
            score -= 20
        
        # Directional strength (dig bala approximation)
        house = planet_data.get("house")
        if house:
            dig_bala_houses = {
                "Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1,
                "Moon": 4, "Venus": 4, "Saturn": 7
            }
            if dig_bala_houses.get(planet_name) == house:
                score += 15
        
        return max(0, min(100, score))
    
    def _check_lord_afflictions(self, planet_data: Dict, planet_name: str, all_planets: Dict) -> List[str]:
        """Check for afflictions on a planet"""
        afflictions = []
        
        # Check combustion
        is_combust = planet_data.get("is_combusted") or planet_data.get("is_combust")
        if is_combust:
            afflictions.append("COMBUST")
        
        # Check retrograde
        is_retro = str(planet_data.get("is_retro", "")).lower() in ("true", "1", "yes")
        if is_retro:
            afflictions.append("RETROGRADE")
        
        # Check malefic aspects
        aspects = planet_data.get("aspects", [])
        for aspect in aspects:
            if isinstance(aspect, dict):
                aspecting_planet = aspect.get("planet", "")
                if aspecting_planet in MALEFICS:
                    afflictions.append(f"Aspected by {aspecting_planet}")
        
        return afflictions
    
    def _get_house_signification(self, house_num: int) -> str:
        """Get the signification of a house"""
        significations = {
            1: "Self/Health/Personality",
            2: "Wealth/Family/Speech",
            3: "Siblings/Courage/Communication",
            4: "Mother/Home/Comfort",
            5: "Children/Intelligence/Romance",
            6: "Enemies/Disease/Debts",
            7: "Marriage/Partnerships",
            8: "Longevity/Transformation/Hidden",
            9: "Fortune/Father/Dharma",
            10: "Career/Status/Authority",
            11: "Gains/Income/Aspirations",
            12: "Losses/Expenses/Moksha"
        }
        return significations.get(house_num, f"House {house_num}")
    
    # ═══════════════════════════════════════════════════════════════════
    # KP ANALYSIS (30% weight)
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_kp_analysis(
        self,
        planets: Dict,
        houses: List,
        sub_subdomain: str
    ) -> Tuple[List[str], Dict]:
        """KP system analysis using cuspal sub-lords"""
        points = []
        kp_data = {}
        
        # Determine which CSLs to check based on sub-subdomain
        if "Dosha" in sub_subdomain:
            csls_to_check = [6, 8, 12]  # Dusthana CSLs
        elif "Success" in sub_subdomain:
            csls_to_check = [1, 5, 9, 10, 11]  # Trikona and wealth CSLs
        elif "Transit" in sub_subdomain:
            csls_to_check = [1, 4, 7, 10]  # Kendra CSLs
        else:
            csls_to_check = [1, 5, 9, 10]  # General CSLs
        
        for house_num in csls_to_check:
            csl = self._get_cusp_sub_lord(houses, house_num)
            if not csl:
                continue
            
            csl_planet = _p(planets, csl)
            if not csl_planet:
                continue
            
            # Check CSL significations
            csl_house = csl_planet.get("house")
            house_signification = self._get_house_signification(house_num)
            
            # Determine if CSL is favorable or unfavorable
            positive_houses = {1, 2, 5, 9, 10, 11}
            negative_houses = {6, 8, 12}
            
            is_favorable = csl_house in positive_houses
            is_unfavorable = csl_house in negative_houses
            
            assessment = "Favorable" if is_favorable else ("Challenging" if is_unfavorable else "Mixed")
            
            point = f"🔮 KP House {house_num} ({house_signification}) CSL: {csl} in H{csl_house} → {assessment}"
            
            if self._add_point(point):
                points.append(point)
            
            kp_data[f"house_{house_num}_csl"] = {
                "csl": csl,
                "csl_house": csl_house,
                "assessment": assessment
            }
        
        return points, kp_data
    
    def _get_cusp_sub_lord(self, houses: List, house_num: int) -> str:
        """Get the cusp sub-lord of a house"""
        if not houses:
            return ""
        
        for h in houses:
            if h.get("house") == house_num:
                return normalize_planet_name(h.get("cusp_sub_lord", ""))
        
        return ""
    
    # ═══════════════════════════════════════════════════════════════════
    # PLANETARY STRENGTH ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_planetary_strength(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict] = None
    ) -> List[str]:
        """Evaluate strength and weakness of planets"""
        points = []
        
        # Use Vedic data if available for more accurate dignity
        planet_data = vedic_planets if vedic_planets else planets
        
        for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = _p(planet_data, planet_name)
            if not p:
                continue
            
            strength_factors = []
            weakness_factors = []
            
            # Calculate dignity
            dignity = self._calculate_dignity(p, planet_name)
            
            if dignity == "exalted":
                strength_factors.append("exalted")
            elif dignity == "debilitated":
                weakness_factors.append("debilitated")
            elif dignity == "own_sign":
                strength_factors.append("in own sign")
            
            # Check dig bala
            house = p.get("house")
            dig_bala_houses = {
                "Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1,
                "Moon": 4, "Venus": 4, "Saturn": 7
            }
            if dig_bala_houses.get(planet_name) == house:
                strength_factors.append("directional strength")
            
            # Check combustion
            is_combust = p.get("is_combusted") or p.get("is_combust")
            if is_combust:
                weakness_factors.append("combust")
            
            # Check retrograde
            is_retro = str(p.get("is_retro", "")).lower() in ("true", "1", "yes")
            if is_retro:
                if planet_name in ["Jupiter", "Venus", "Mercury"]:
                    strength_factors.append("retrograde (gaining strength)")
                else:
                    weakness_factors.append("retrograde")
            
            # Formulate points
            if strength_factors:
                point = f"💪 {planet_name} is STRONG: {', '.join(strength_factors)}"
                if self._add_point(point):
                    points.append(point)
            
            if weakness_factors:
                point = f"⚠️ {planet_name} shows WEAKNESS: {', '.join(weakness_factors)}"
                if self._add_point(point):
                    points.append(point)
        
        return points
    
    # ═══════════════════════════════════════════════════════════════════
    # DOSHA DETECTION
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_doshas(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict] = None
    ) -> Tuple[List[str], Dict]:
        """Evaluate doshas (afflictions) in the chart"""
        points = []
        dosha_data = {
            "manglik": False,
            "kaal_sarp": False,
            "sade_sati": "unknown",
            "afflicted_moon": False,
            "afflicted_ascendant": False
        }
        
        # Use Vedic data if available
        planet_data = vedic_planets if vedic_planets else planets
        
        # ═══════════════════════════════════════════════════════════════
        # MANGLIK DOSHA (Mars in 1,4,7,8,12)
        # ═══════════════════════════════════════════════════════════════
        mars = _p(planet_data, "Mars")
        if mars:
            mars_house = mars.get("house")
            if mars_house in {1, 4, 7, 8, 12}:
                point = f"🔴 MANGLIK DOSHA present: Mars in {mars_house}th house"
                if self._add_point(point):
                    points.append(point)
                dosha_data["manglik"] = True
                dosha_data["mars_house"] = mars_house
        
        # ═══════════════════════════════════════════════════════════════
        # KAAL SARP DOSHA (all planets between Rahu-Ketu)
        # ═══════════════════════════════════════════════════════════════
        rahu = _p(planet_data, "Rahu")
        ketu = _p(planet_data, "Ketu")
        if rahu and ketu:
            rahu_house = rahu.get("house")
            ketu_house = ketu.get("house")
            
            if rahu_house and ketu_house:
                # Check if all planets are on one side
                all_between = self._check_kaal_sarp(planet_data, rahu_house, ketu_house)
                if all_between:
                    point = f"🐍 KAAL SARP DOSHA detected: All planets between Rahu (H{rahu_house}) and Ketu (H{ketu_house})"
                    if self._add_point(point):
                        points.append(point)
                    dosha_data["kaal_sarp"] = True
                else:
                    point = f"ℹ️ Rahu-Ketu axis: Rahu in H{rahu_house}, Ketu in H{ketu_house} - indicates karmic patterns"
                    if self._add_point(point):
                        points.append(point)
        
        # ═══════════════════════════════════════════════════════════════
        # AFFLICTED MOON (mental/emotional challenges)
        # ═══════════════════════════════════════════════════════════════
        moon = _p(planet_data, "Moon")
        if moon:
            moon_afflictions = []
            
            # Check malefic aspects
            aspects = moon.get("aspects", [])
            for aspect in aspects:
                if isinstance(aspect, dict):
                    aspecting_planet = aspect.get("planet", "")
                    if aspecting_planet in MALEFICS:
                        moon_afflictions.append(f"aspected by {aspecting_planet}")
            
            # Check combustion
            if moon.get("is_combusted") or moon.get("is_combust"):
                moon_afflictions.append("combust")
            
            # Check debilitation
            dignity = self._calculate_dignity(moon, "Moon")
            if dignity == "debilitated":
                moon_afflictions.append("debilitated")
            
            if moon_afflictions:
                point = f"🌙 Moon afflicted: {', '.join(moon_afflictions)} - suggests emotional challenges"
                if self._add_point(point):
                    points.append(point)
                dosha_data["afflicted_moon"] = True
                dosha_data["moon_afflictions"] = moon_afflictions
        
        # ═══════════════════════════════════════════════════════════════
        # AFFLICTED ASCENDANT LORD
        # ═══════════════════════════════════════════════════════════════
        asc_lord_name = self._get_house_lord(houses, 1)
        if asc_lord_name:
            asc_lord = _p(planet_data, asc_lord_name)
            if asc_lord:
                asc_afflictions = []
                
                dignity = self._calculate_dignity(asc_lord, asc_lord_name)
                if dignity == "debilitated":
                    asc_afflictions.append("debilitated")
                
                if asc_lord.get("is_combusted") or asc_lord.get("is_combust"):
                    asc_afflictions.append("combust")
                
                if asc_afflictions:
                    point = f"⚠️ Ascendant lord {asc_lord_name} is afflicted: {', '.join(asc_afflictions)} - requires extra effort"
                    if self._add_point(point):
                        points.append(point)
                    dosha_data["afflicted_ascendant"] = True
        
        return points, dosha_data
    
    def _check_kaal_sarp(self, planets: Dict, rahu_house: int, ketu_house: int) -> bool:
        """Check if all planets are between Rahu and Ketu (Kaal Sarp Dosha)"""
        # Simplified check - in real implementation, check zodiacal positions
        planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        for planet_name in planets_to_check:
            p = _p(planets, planet_name)
            if p:
                p_house = p.get("house")
                if p_house:
                    # Check if planet is outside the Rahu-Ketu axis
                    if rahu_house < ketu_house:
                        if not (rahu_house <= p_house <= ketu_house):
                            return False
                    else:
                        if not (p_house >= rahu_house or p_house <= ketu_house):
                            return False
        
        return True
    
    # ═══════════════════════════════════════════════════════════════════
    # YOGA ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_yogas(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict] = None
    ) -> Tuple[List[str], Dict]:
        """Evaluate auspicious yogas in the chart"""
        points = []
        yoga_data = {
            "raj_yogas": [],
            "dhana_yogas": [],
            "other_yogas": []
        }
        
        planet_data = vedic_planets if vedic_planets else planets
        
        # ═══════════════════════════════════════════════════════════════
        # RAJ YOGA - Exalted planets in kendras
        # ═══════════════════════════════════════════════════════════════
        for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = _p(planet_data, planet_name)
            if p:
                dignity = self._calculate_dignity(p, planet_name)
                house = p.get("house")
                
                if dignity == "exalted" and house in {1, 4, 7, 10}:
                    yoga_name = f"{planet_name} Raj Yoga"
                    point = f"👑 RAJ YOGA: {planet_name} exalted in {house}th house (Kendra) - brings power and authority"
                    if self._add_point(point):
                        points.append(point)
                    yoga_data["raj_yogas"].append({
                        "name": yoga_name,
                        "planet": planet_name,
                        "house": house,
                        "strength": "high"
                    })
        
        # ═══════════════════════════════════════════════════════════════
        # GAJA KESARI YOGA - Jupiter in kendra from Moon
        # ═══════════════════════════════════════════════════════════════
        jupiter = _p(planet_data, "Jupiter")
        moon = _p(planet_data, "Moon")
        
        if jupiter and moon:
            jup_house = jupiter.get("house")
            moon_house = moon.get("house")
            
            if jup_house and moon_house:
                # Check if Jupiter is in kendra (1,4,7,10) from Moon
                diff = (jup_house - moon_house) % 12
                if diff in {0, 3, 6, 9}:  # 1st, 4th, 7th, 10th from Moon
                    point = f"🐘 GAJA KESARI YOGA: Jupiter in kendra from Moon - wisdom, wealth and fame"
                    if self._add_point(point):
                        points.append(point)
                    yoga_data["other_yogas"].append({
                        "name": "Gaja Kesari Yoga",
                        "planets": ["Jupiter", "Moon"],
                        "strength": "high"
                    })
        
        # ═══════════════════════════════════════════════════════════════
        # DHANA YOGA - Jupiter-Venus conjunction or mutual aspect
        # ═══════════════════════════════════════════════════════════════
        venus = _p(planet_data, "Venus")
        
        if jupiter and venus:
            jup_house = jupiter.get("house")
            ven_house = venus.get("house")
            
            if jup_house == ven_house:
                point = f"💰 DHANA YOGA: Jupiter-Venus conjunction in H{jup_house} - wealth and prosperity"
                if self._add_point(point):
                    points.append(point)
                yoga_data["dhana_yogas"].append({
                    "name": "Jupiter-Venus Dhana Yoga",
                    "house": jup_house,
                    "strength": "high"
                })
        
        # ═══════════════════════════════════════════════════════════════
        # TRIKONA JUPITER - Jupiter in 5th or 9th (Dhana)
        # ═══════════════════════════════════════════════════════════════
        if jupiter:
            jup_house = jupiter.get("house")
            if jup_house in {5, 9}:
                point = f"🍀 Jupiter in {jup_house}th house (Trikona) - supports Dhana Yoga"
                if self._add_point(point):
                    points.append(point)
                yoga_data["dhana_yogas"].append({
                    "name": f"Jupiter Trikona Yoga (H{jup_house})",
                    "planet": "Jupiter",
                    "house": jup_house,
                    "strength": "medium"
                })
        
        # ═══════════════════════════════════════════════════════════════
        # BUDHADITYA YOGA - Sun-Mercury conjunction
        # ═══════════════════════════════════════════════════════════════
        sun = _p(planet_data, "Sun")
        mercury = _p(planet_data, "Mercury")
        
        if sun and mercury:
            sun_house = sun.get("house")
            mer_house = mercury.get("house")
            
            if sun_house == mer_house:
                point = f"📚 BUDHADITYA YOGA: Sun-Mercury conjunction in H{sun_house} - intelligence and communication skills"
                if self._add_point(point):
                    points.append(point)
                yoga_data["other_yogas"].append({
                    "name": "Budhaditya Yoga",
                    "house": sun_house,
                    "strength": "medium"
                })
        
        return points, yoga_data
    
    # ═══════════════════════════════════════════════════════════════════
    # TIMING WINDOWS EVALUATION
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_timing_windows(
        self,
        timing_windows: Dict[str, List],
        sub_subdomain: str
    ) -> Tuple[List[str], Dict]:
        """Evaluate and format timing windows for success periods"""
        points = []
        timing_data = {}
        
        # Extract timing windows for the relevant sub-subdomain
        windows = self._extract_timing_windows(timing_windows, sub_subdomain)
        
        if not windows:
            point = "ℹ️ No specific timing windows identified for this analysis"
            if self._add_point(point):
                points.append(point)
            timing_data["status"] = "no_windows"
            return points, timing_data
        
        # Get best window
        best_window = windows[0] if windows else None
        if best_window:
            start = best_window.get("start", "")
            end = best_window.get("end", "")
            dasha = best_window.get("dasha", "")
            score = best_window.get("score") or best_window.get("final_score", 0)
            
            point = f"🏆 BEST SUCCESS PERIOD: {start} to {end} ({dasha}) - Score: {score}"
            if self._add_point(point):
                points.append(point)
            
            timing_data["best_window"] = best_window
        
        # Get nearest favorable window (within 2 years)
        nearest_window = self._get_nearest_window(windows)
        if nearest_window and nearest_window != best_window:
            start = nearest_window.get("start", "")
            end = nearest_window.get("end", "")
            dasha = nearest_window.get("dasha", "")
            
            point = f"📅 NEAREST FAVORABLE: {start} to {end} ({dasha})"
            if self._add_point(point):
                points.append(point)
            
            timing_data["nearest_window"] = nearest_window
        
        timing_data["all_windows"] = windows[:5]  # Top 5
        timing_data["total_windows"] = len(windows)
        
        return points, timing_data
    
    def _extract_timing_windows(
        self,
        timing_windows: Dict[str, List],
        sub_subdomain: str
    ) -> List[Dict]:
        """Extract and normalize timing windows"""
        windows = []
        
        # Try to find windows for this sub-subdomain
        for key, value in timing_windows.items():
            if sub_subdomain.lower() in key.lower() or "success" in key.lower():
                windows = value
                break
        
        # Fallback to any available windows
        if not windows:
            for key, value in timing_windows.items():
                if value and isinstance(value, list):
                    windows = value
                    break
        
        # Normalize windows
        normalized = []
        for w in windows:
            if isinstance(w, TimingWindow):
                # Convert TimingWindow to dict
                normalized.append({
                    "start": w.start,
                    "end": w.end,
                    "dasha": w.dasha,
                    "score": w.score or w.final_score,
                    "final_score": w.final_score,
                    "transit_score": w.transit_score,
                    "age_at_start": w.age_at_start,
                    "is_overall_best": w.is_overall_best,
                    "is_earliest_favorable": w.is_earliest_favorable
                })
            elif isinstance(w, dict):
                normalized.append(w)
        
        # Sort by score descending
        normalized.sort(key=lambda x: x.get("final_score") or x.get("score") or 0, reverse=True)
        
        return normalized
    
    def _get_nearest_window(self, windows: List[Dict]) -> Optional[Dict]:
        """Get the nearest favorable window within 2 years"""
        if not windows:
            return None
        
        now = datetime.now()
        two_years_later = datetime(now.year + 2, now.month, now.day)
        
        for w in windows:
            try:
                start_str = w.get("start", "")
                if isinstance(start_str, datetime):
                    start_date = start_str
                else:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                
                if now <= start_date <= two_years_later:
                    return w
            except:
                continue
        
        return windows[0] if windows else None
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERAL LIFE INDICATORS
    # ═══════════════════════════════════════════════════════════════════
    def _evaluate_life_indicators(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict] = None
    ) -> List[str]:
        """Evaluate general life path indicators"""
        points = []
        
        planet_data = vedic_planets if vedic_planets else planets
        
        # Check ascendant lord position
        asc_lord = self._get_house_lord(houses, 1)
        if asc_lord:
            asc_planet = _p(planet_data, asc_lord)
            if asc_planet:
                asc_house = asc_planet.get("house")
                if asc_house:
                    point = f"🧭 Ascendant lord {asc_lord} in H{asc_house} - influences life direction"
                    if self._add_point(point):
                        points.append(point)
        
        # Check 10th lord for career
        tenth_lord = self._get_house_lord(houses, 10)
        if tenth_lord:
            tenth_planet = _p(planet_data, tenth_lord)
            if tenth_planet:
                tenth_house = tenth_planet.get("house")
                if tenth_house:
                    point = f"💼 10th lord {tenth_lord} in H{tenth_house} - career indicator"
                    if self._add_point(point):
                        points.append(point)
        
        # Check Sun for authority
        sun = _p(planet_data, "Sun")
        if sun:
            sun_house = sun.get("house")
            if sun_house == 10:
                point = "☀️ Sun in 10th house - strong career potential and authority"
                if self._add_point(point):
                    points.append(point)
        
        # Check Moon for emotional nature
        moon = _p(planet_data, "Moon")
        if moon:
            moon_sign = moon.get("sign", "")
            dignity = self._calculate_dignity(moon, "Moon")
            if dignity == "exalted":
                point = f"🌙 Exalted Moon in {moon_sign} - emotional strength and mental clarity"
                if self._add_point(point):
                    points.append(point)
            elif moon_sign:
                point = f"🌙 Moon in {moon_sign} - shapes emotional nature"
                if self._add_point(point):
                    points.append(point)
        
        return points
    
    # ═══════════════════════════════════════════════════════════════════
    # QUESTIONS
    # ═══════════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        """Get predefined questions for General Kundali Analysis"""
        return [
            # Current Period Analysis
            Question(
                id="current_period",
                question="How is my current astrological period (dasha) and are my planets strong or weak?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Current Period Analysis"
            ),
            
            # Dosha Analysis
            Question(
                id="dosha_analysis",
                question="Are there any significant doshas or adverse influences right now and when do such periods occur (e.g., Sade Sati, Graha doshas)?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Dosha Analysis"
            ),
            
            # Planetary Transits
            Question(
                id="planetary_transits",
                question="What are the major favorable and unfavorable planetary transits affecting me at present?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Planetary Transits"
            ),
            
            # Periods of Success
            Question(
                id="periods_of_success",
                question="When can I expect major success or fortune phases (such as Raj, Dhana, or Sanyasa yogas) and what is their timing?",
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.POSITIVE,
                    goal=InterpretationGoal.STATUS  # Using STATUS instead of MANIFESTATION
                ),
                sub_subdomain="Periods of Success"
            )
        ]
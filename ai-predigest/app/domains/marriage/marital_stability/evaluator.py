"""
Marital Stability Evaluator - Enhanced Version v4.0

FIXES & ENHANCEMENTS:
✅ _extract_timing_windows now handles TimingWindow objects (not just dicts)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP analysis preserved and passed to LLM

Features:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ KP marriage/divorce engine integration (preserved)
✅ ALL original KP functions preserved (R3_x, R4_x, R7_x, Book-4)

NO KP FUNCTIONS REMOVED - Everything is preserved!
"""
from typing import Dict, List, Any, Set, Optional
import logging

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, has_harsh_aspect, _has_evil_aspect, _has_good_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, detect_aspects,
    get_signified_houses, get_signified_score,
    _house_has_benefic_occupation, _benefic_by_lordship_of_house, _is_strong_planet,
    BENEFICS, MALEFICS
)

from app.core.astro_constants import detect_aspects, normalize_planet_name
from app.domains.excel_structure_config import get_houses_for_question

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer, 
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════════
# DIGNITY CALCULATION - FALLBACK TABLES (for when HouseLordsAnalyzer fails)
# ═══════════════════════════════════════════════════════════════════════════════

PLANET_RULERSHIP = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": [],
    "Ketu": []
}

PLANET_EXALTATION = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
    "Rahu": "Taurus",
    "Ketu": "Scorpio"
}

PLANET_DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
    "Rahu": "Scorpio",
    "Ketu": "Taurus"
}

FRIENDSHIP_TABLE = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
    "Moon": {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
    "Rahu": {"friends": ["Venus", "Saturn"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Mercury", "Jupiter"]},
    "Ketu": {"friends": ["Mars", "Venus", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mercury", "Jupiter"]}
}


def calculate_dignity_fallback(planet_name: str, planet_sign: str) -> str:
    """
    Calculate planet dignity using fallback tables when HouseLordsAnalyzer fails.
    
    Returns: "Exalted", "Own Sign", "Friendly", "Neutral", "Enemy", "Debilitated"
    """
    if not planet_name or not planet_sign:
        return "Unknown"
    
    planet_name = normalize_planet_name(planet_name) or planet_name
    planet_sign = planet_sign.title() if planet_sign else ""
    
    # Check exaltation
    if PLANET_EXALTATION.get(planet_name) == planet_sign:
        return "Exalted"
    
    # Check debilitation
    if PLANET_DEBILITATION.get(planet_name) == planet_sign:
        return "Debilitated"
    
    # Check own sign
    if planet_sign in PLANET_RULERSHIP.get(planet_name, []):
        return "Own Sign"
    
    # Find sign lord for friendship check
    sign_lord = None
    for lord, signs in PLANET_RULERSHIP.items():
        if planet_sign in signs:
            sign_lord = lord
            break
    
    if not sign_lord or sign_lord == planet_name:
        return "Neutral"
    
    # Check friendship
    friendship = FRIENDSHIP_TABLE.get(planet_name, {})
    if sign_lord in friendship.get("friends", []):
        return "Friendly"
    elif sign_lord in friendship.get("enemies", []):
        return "Enemy"
    else:
        return "Neutral"


class MaritalStabilityEvaluator(BaseEvaluator):
    """
    ENHANCED Evaluator for Marital Stability subtopic.
    
    Combines:
    - Original comprehensive KP analysis (ALL rules preserved)
    - New Vedic house lords analysis with dignity
    - Intelligent question-type detection
    - Timing windows extraction (BEST + NEAREST)
    - Dasha timeline support
    - Dual data source (KP + Vedic)
    
    For DIVORCE questions: KP-heavy (40% KP + Book-4 rules)
    For GENERAL questions: Balanced (house lords + comprehensive KP)
    """
    
    domain = "Marriage"
    subtopic = "Marital Stability"
    
    # KP house significations for stability
    positive_houses = {2, 7, 11}  # Marriage sustaining houses
    supportive_houses = {4, 5}    # Family, love, comfort
    negative_houses = {6, 8, 12}  # Separation, obstacles, loss
    
    MARRIAGE_HOUSES = {2, 5, 7, 8, 11}
    # Key planets for marital stability
    key_planets = {"Venus", "Jupiter", "Moon", "Saturn"}
    
    # House meanings for marriage context
    HOUSE_MEANINGS = {
        2: "Family/Wealth",
        5: "Romance/Children",
        7: "Spouse/Partnership",
        8: "Obstacles/Transformation",
        11: "Gains/Fulfillment",
        6: "Disputes/Enemies",
        12: "Loss/Separation"
    }
    
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,   
        **kwargs
    ) -> EvaluationResult:
        """
        Main evaluation - intelligently adapts to question type.
        
        ENHANCED with:
        - Timing windows extraction
        - House lords with dignity
        - Dasha timeline support
        - Dual data source
        """
        self.reset()
        result = EvaluationResult()
        
        # ═══════════════════════════════════════════════════════
        # STEP 0: Choose Data Source for House Lord Analysis
        # ═══════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses
        
        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        
        # Detect aspects on both data sources
        planets = detect_aspects(planets)
        if vedic_planets:
            detect_aspects(vedic_planets)
        
        # Calculate aspects data
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.error(f"Aspect calculation error: {e}")
        
        # ═══════════════════════════════════════════════════════
        # STEP 1: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )
        
        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
        else:
            logger.warning(f"No config for question, using fallback")
            all_relevant_houses = self.MARRIAGE_HOUSES
            primary_houses = {2, 7, 11}
            secondary_houses = {5, 8}
        
        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None
        
        logger.info("=" * 80)
        logger.info("MARITAL STABILITY EVALUATOR (ENHANCED v4.0)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info("=" * 80)
        
        # ═══════════════════════════════════════════════════════
        # STEP 2: Extract House Lords Data (using Vedic/analysis data)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )
        
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")
        
        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )
        
        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")
        
        # ═══════════════════════════════════════════════════════
        # STEP 4: Extract Timing Windows (FIXED - Handles TimingWindow objects!)
        # ═══════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})
        
        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")
        
        # Handle both dict (keyed by sub-subdomain) and list formats
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            
            # Fallback keys for divorce timing
            if not timing_windows_list and "Divorce Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Divorce Timing"]
            if not timing_windows_list and "Divorce/Separation" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Divorce/Separation"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
        
        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = self._extract_timing_windows(timing_windows_list)
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')})")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')})")
        
        # ═══════════════════════════════════════════════════════
        # STEP 4.5: Extract Person2 House Lords (if two-person request)
        # ═══════════════════════════════════════════════════════
        person1_name = kwargs.get("person1_name") or "Person 1"
        person2_name = kwargs.get("person2_name") or None

        house_lords_info_p2 = {}
        house_aspects_info_p2 = {}

        planets2 = kwargs.get("planets2")
        houses2 = kwargs.get("houses2")
        vedic_planets2 = kwargs.get("vedic_planets2")
        vedic_houses2 = kwargs.get("vedic_houses2")

        if planets2 and houses2 and person2_name:
            analysis_planets2 = vedic_planets2 if vedic_planets2 else planets2
            analysis_houses2 = vedic_houses2 if vedic_houses2 else houses2

            planets2 = detect_aspects(planets2)
            if vedic_planets2:
                detect_aspects(vedic_planets2)

            aspects_data2 = {}
            if HOUSE_LORDS_AVAILABLE:
                try:
                    aspects_data2 = calculate_planetary_aspects(analysis_planets2)
                except Exception as e:
                    logger.error(f"P2 aspect calculation error: {e}")

            house_lords_info_p2 = self._extract_house_lords(
                analysis_houses2,
                analysis_planets2,
                all_relevant_houses,
                primary_houses
            )
            house_aspects_info_p2 = self._extract_aspects_on_houses(
                analysis_houses2,
                analysis_planets2,
                aspects_data2,
                all_relevant_houses
            )
            logger.info(f"✅ Extracted P2 ({person2_name}) house lords for {len(house_lords_info_p2)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 4.7: Pre-compute Canonical Dasha + KP Verdicts
        # Both are computed ONCE before divorce/general branching
        # so all questions get the SAME verdict. This prevents
        # Q1 saying "low risk" while Q2 says "chart promises divorce"
        # for the same chart data.
        # ═══════════════════════════════════════════════════════
        canonical_dasha_verdict = self._compute_canonical_dasha_verdict(
            planets, houses, kwargs
        )
        canonical_kp_divorce_verdict = self._compute_canonical_kp_divorce_verdict(
            planets, houses
        )

        # ═══════════════════════════════════════════════════════
        # STEP 5: Determine Question Type and Evaluate
        # ═══════════════════════════════════════════════════════
        is_divorce_question = (
            "Divorce" in sub_subdomain or 
            "Separation" in sub_subdomain or
            "Risk" in sub_subdomain
        )
        
        if is_divorce_question:
            # DIVORCE-FOCUSED: KP-heavy with focused house lords
            result = self._evaluate_divorce_focused(
                planets, houses, aspects_data, kwargs,
                house_lords_info, house_aspects_info, timing_windows_data,
                primary_houses, secondary_houses
            )
        else:
            # GENERAL: Balanced approach with all KP rules
            result = self._evaluate_general_comprehensive(
                planets, houses, aspects_data, kwargs,
                house_lords_info, house_aspects_info, timing_windows_data,
                primary_houses, secondary_houses
            )
        
        # ═══════════════════════════════════════════════════════
        # STEP 6: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data
        )

        # Store canonical verdicts for consistent LLM output across ALL questions
        if canonical_dasha_verdict:
            result.additional_data["canonical_dasha_verdict"] = canonical_dasha_verdict
        if canonical_kp_divorce_verdict:
            result.additional_data["canonical_kp_divorce_verdict"] = canonical_kp_divorce_verdict

        # Store person names and person2 house lords for prompt labeling
        result.additional_data["person1_name"] = person1_name
        if person2_name:
            result.additional_data["person2_name"] = person2_name
        if house_lords_info_p2:
            result.additional_data["marriage_house_lords_p2"] = house_lords_info_p2
        if house_aspects_info_p2:
            result.additional_data["marriage_house_aspects_p2"] = house_aspects_info_p2
        
        logger.info("=" * 80)
        logger.info(f"EVALUATION COMPLETE: {len(result.technical_points)} points")
        logger.info("=" * 80)
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - FIXED VERSION!
    # ═══════════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        
        ✅ FIXED: Now handles both dict and TimingWindow objects!
        
        Best window: Highest score (best planetary alignment)
        Nearest window: Earliest favorable window (soonest opportunity)
        
        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}
        
        try:
            # ✅ FIX: Helper function to get attribute from either dict or TimingWindow object
            def get_attr(obj, key, default=None):
                """Get attribute from dict or object (handles both cases)"""
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    # It's a TimingWindow dataclass or similar object
                    return getattr(obj, key, default)
            
            # ✅ FIX: Helper function to convert TimingWindow object to dict for storage
            def window_to_dict(w):
                """Convert TimingWindow object or dict to standardized dict format"""
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w
                
                # Convert TimingWindow dataclass to dict
                result = {
                    'start': get_attr(w, 'start'),
                    'end': get_attr(w, 'end'),
                    'dasha': get_attr(w, 'dasha'),
                    'score': get_attr(w, 'score'),
                    'transit_score': get_attr(w, 'transit_score'),
                    'final_score': get_attr(w, 'final_score'),
                    'age_at_start': get_attr(w, 'age_at_start'),
                    'is_overall_best': get_attr(w, 'is_overall_best', False),
                    'is_earliest_favorable': get_attr(w, 'is_earliest_favorable', False),
                }
                
                # Include additional fields if they exist
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar', 
                                   'md', 'ad', 'pd', 'maha', 'antara', 'paryantar',
                                   '_domain_score', '_delay_years', '_needs_resonant_jump']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                
                return result
            
            # Log the first window type for debugging
            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")
            
            # ✅ FIX: Sort by final_score using get_attr helper
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )
            
            # Best window: highest score (convert to dict)
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None
            
            # Nearest window: earliest with score >= 50
            from datetime import datetime
            
            favorable_windows = [
                w for w in timing_windows 
                if (get_attr(w, 'final_score', 0) or 0) >= 50
            ]
            
            logger.info(f"🔍 Found {len(favorable_windows)} favorable windows (score >= 50)")
            
            if favorable_windows:
                sorted_by_date = sorted(
                    favorable_windows,
                    key=lambda w: datetime.strptime(
                        get_attr(w, 'start', '9999-12-31') or '9999-12-31', 
                        '%Y-%m-%d'
                    )
                )
                nearest_window = window_to_dict(sorted_by_date[0]) if sorted_by_date else None
            else:
                nearest_window = best_window
                logger.info("🔍 No windows with score >= 50, using best window as nearest")
            
            # Top 5 favorable windows (convert all to dicts)
            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]
            
            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }
            
            logger.info(f"✅ Timing extraction SUCCESSFUL")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    # ═══════════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION - ENHANCED VERSION
    # ═══════════════════════════════════════════════════════════════════
    def _extract_house_lords(
        self,
        houses: list,
        planets: dict,
        relevant_houses: set,
        primary_houses: set
    ) -> dict:
        """
        Extract house lord information for relevant houses only.
        Handles both KP and Vedic data formats.
        """
        house_lords_info = {}
        
        for h in houses:
            house_num = h.get("house")
            
            if house_num not in relevant_houses:
                continue
            
            # Get lord name - try multiple possible keys
            lord_name = (
                h.get("rashi_lord") or
                h.get("sign_lord") or
                h.get("lord") or
                ""
            )

            # Also try to deduce from sign if lord not found directly
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
                    if lord_name:
                        logger.debug(f"✅ Deduced lord {lord_name} for house {house_num} from sign {sign}")
            
            normalized_lord = normalize_planet_name(lord_name)
            
            if not normalized_lord:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                logger.warning(f"⚠️ No lord found for house {house_num} (sign: {sign})")
                continue
            
            logger.debug(f"✅ {normalized_lord} is lord of house {house_num}")
            
            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"⚠️ No data found for lord {normalized_lord}")
                continue
                
            lord_house = lord_data.get("house")
            lord_sign = lord_data.get("sign", "") or lord_data.get("rasi", "")
            
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
            
            # Get lord dignity - try HouseLordsAnalyzer first, then fallback
            lord_dignity = "Unknown"
            lord_strength_score = 50
            
            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    
                    dignity = None
                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(normalized_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(normalized_lord)
                    elif hasattr(analyzer, 'analyze_dignity'):
                        dignity = analyzer.analyze_dignity(normalized_lord)
                    
                    if dignity:
                        if hasattr(dignity, 'value'):
                            lord_dignity = dignity.value
                        else:
                            lord_dignity = str(dignity)
                        
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity
                        )
                    else:
                        # FALLBACK: Calculate dignity directly
                        lord_dignity = calculate_dignity_fallback(normalized_lord, lord_sign)
                        lord_strength_score = self._calculate_lord_strength_from_dignity(
                            normalized_lord, lord_data, lord_dignity
                        )
                        logger.debug(f"Used fallback dignity for {normalized_lord}: {lord_dignity}")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")
                    # FALLBACK
                    lord_dignity = calculate_dignity_fallback(normalized_lord, lord_sign)
                    lord_strength_score = self._calculate_lord_strength_from_dignity(
                        normalized_lord, lord_data, lord_dignity
                    )
            else:
                # FALLBACK when HouseLordsAnalyzer not available
                lord_dignity = calculate_dignity_fallback(normalized_lord, lord_sign)
                lord_strength_score = self._calculate_lord_strength_from_dignity(
                    normalized_lord, lord_data, lord_dignity
                )
            
            priority = "primary" if house_num in primary_houses else "secondary"
            
            planets_in_house = []
            for p in h.get("planets", []):
                planet_name = normalize_planet_name(self.extract_planet_name(p))
                if planet_name:
                    planets_in_house.append(planet_name)
            
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

    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity = None
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
        
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            if planet_name in {"Jupiter", "Venus", "Mercury"}:
                score -= 10
            elif planet_name in {"Saturn", "Mars"}:
                score += 10
        
        degree = (
            planet_data.get("full_degree") or 
            planet_data.get("global_degree") or 
            planet_data.get("degree") or 
            15
        )
        if degree < 5 or degree > 25:
            score -= 10
        
        return max(0, min(100, score))

    def _calculate_lord_strength_from_dignity(
        self,
        planet_name: str,
        planet_data: dict,
        dignity_str: str
    ) -> int:
        """Calculate lord strength score from dignity string (0-100)."""
        dignity_scores = {
            "Exalted": 100,
            "Own Sign": 80,
            "Friendly": 60,
            "Neutral": 40,
            "Enemy": 20,
            "Debilitated": 0,
            "Unknown": 50
        }
        score = dignity_scores.get(dignity_str, 50)
        
        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30
        
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            if planet_name in {"Jupiter", "Venus", "Mercury"}:
                score -= 10
            elif planet_name in {"Saturn", "Mars"}:
                score += 10
        
        degree = (
            planet_data.get("full_degree") or 
            planet_data.get("global_degree") or 
            planet_data.get("degree") or 
            15
        )
        if degree < 5 or degree > 25:
            score -= 10
        
        return max(0, min(100, score))

    @staticmethod
    def extract_planet_name(p):
        """Extract planet name from dict or string"""
        if isinstance(p, dict):
            return p.get("name")
        if isinstance(p, str):
            return p
        return None

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "marriage"
        
        result.additional_data.update({
            f"{domain_prefix}_house_config": {
                "primary": list(primary_houses),
                "secondary": list(secondary_houses),
                "source": house_config.get("source", "fallback") if house_config else "fallback"
            },
            
            f"{domain_prefix}_house_lords": house_lords_info,
            
            f"{domain_prefix}_house_aspects": house_aspects_info,
            
            f"{domain_prefix}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "primary_houses_count": len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "strong_lords": sum(
                    1 for info in house_lords_info.values() 
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values() 
                    if info["lord_strength_score"] < 40
                )
            }
        })
        
        # ✅ Store timing windows if available
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE")

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for marriage context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    # ═══════════════════════════════════════════════════════════════════
    # DIVORCE-FOCUSED ANALYSIS (for divorce questions)
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_divorce_focused(
        self,
        planets: Dict,
        houses: List,
        aspects_data: Dict,
        kwargs: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        timing_windows_data: Dict,
        primary_houses: set,
        secondary_houses: set
    ) -> EvaluationResult:
        """
        Divorce-focused analysis (KP-heavy).
        
        Structure:
        1. KP Divorce Analysis (30%) - CSL, significations, Book-4
        2. House Lords Divorce (50%) - 7th, 6th, 8th, 12th
        3. Dasha Timing (20%)
        """
        result = EvaluationResult()
        
        # Add house analysis points
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )
        
        # 1. Core KP Divorce Analysis (30%)
        kp_divorce_points = self._evaluate_kp_divorce_core(planets, houses)
        result.extend_points(kp_divorce_points)
        
        # 2. Book-4 Divorce Rules
        book4_points = self._evaluate_divorce_separation_book_rules(planets, houses)
        result.extend_points(book4_points)
        
        # 3. House Lords Divorce Analysis (50%)
        lords_points = self._evaluate_divorce_house_lords(planets, houses, aspects_data)
        result.extend_points(lords_points)
        
        # 4. Dasha Timing (20%)
        dasha_points = self._evaluate_divorce_dasha_timing(
            planets, houses, kwargs.get("metadata", {})
        )
        result.extend_points(dasha_points)
        
        # 5. Relevant KP Rules - R4_x unhappy indicators
        unhappy_points_filtered = self._get_divorce_relevant_r4_rules(planets, houses)
        result.extend_points(unhappy_points_filtered)
        
        # ═══════════════════════════════════════════════════════
        # NEW: Check if divorce timing was identified
        # If NO timing windows found, indicate lower divorce risk
        # ═══════════════════════════════════════════════════════
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            result.add_point("")
            result.add_point("═══ DIVORCE TIMING ASSESSMENT ═══")
            result.add_point("✅ NO SPECIFIC DIVORCE TIMING WINDOWS IDENTIFIED")
            result.add_point("   → This indicates LOWER probability of divorce/separation")
            result.add_point("   → No strong planetary alignments found for separation events")
            result.add_point("   → Marriage stability is relatively protected")
            result.additional_data["no_divorce_timing_found"] = True
            result.additional_data["divorce_timing_assessment"] = "LOW_RISK - No specific timing windows identified"
            logger.info("✅ No divorce timing windows found - indicating lower divorce risk")
        else:
            # Timing windows were found - indicate risk
            best_window = timing_windows_data.get('best_window', {})
            if best_window:
                risk_score = best_window.get('final_score') or 0
                if risk_score >= 70:
                    result.add_point("")
                    result.add_point("═══ DIVORCE TIMING ASSESSMENT ═══")
                    result.add_point(f"🚨 HIGH-RISK DIVORCE TIMING IDENTIFIED (Score: {risk_score:.1f}/100)")
                    result.add_point("   → Strong planetary alignments found for separation")
                    result.add_point("   → Remedies and counseling strongly recommended")
                    result.additional_data["divorce_timing_assessment"] = f"HIGH_RISK - Score {risk_score:.1f}"
                elif risk_score >= 50:
                    result.add_point("")
                    result.add_point("═══ DIVORCE TIMING ASSESSMENT ═══")
                    result.add_point(f"⚠️ MODERATE DIVORCE TIMING IDENTIFIED (Score: {risk_score:.1f}/100)")
                    result.add_point("   → Some challenging periods ahead")
                    result.add_point("   → Conscious effort and remedies advised")
                    result.additional_data["divorce_timing_assessment"] = f"MODERATE_RISK - Score {risk_score:.1f}"
                else:
                    result.add_point("")
                    result.add_point("═══ DIVORCE TIMING ASSESSMENT ═══")
                    result.add_point(f"✅ LOW DIVORCE TIMING RISK (Score: {risk_score:.1f}/100)")
                    result.add_point("   → Minor challenges only, manageable")
                    result.additional_data["divorce_timing_assessment"] = f"LOW_RISK - Score {risk_score:.1f}"
        
        # Overall assessment
        overall = self._calculate_divorce_risk_level(planets, houses)
        result.additional_data["divorce_risk_level"] = overall["level"]
        result.additional_data["divorce_risk_score"] = overall["score"]
        result.add_point(overall["verdict"])
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERAL COMPREHENSIVE ANALYSIS (for non-divorce questions)
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_general_comprehensive(
        self,
        planets: Dict,
        houses: List,
        aspects_data: Dict,
        kwargs: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        timing_windows_data: Dict,
        primary_houses: set,
        secondary_houses: set
    ) -> EvaluationResult:
        """
        General comprehensive analysis.
        
        Uses ALL original KP rules + house lords:
        1. House Lords (50%)
        2. Happy Marriage (R3_x) - included in KP (30%)
        3. Dasha Timing (20%)
        """
        result = EvaluationResult()
        
        # Add house analysis points
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )
        
        # 1. House Lords Stability
        if HOUSE_LORDS_AVAILABLE and aspects_data:
            lords_points = self._evaluate_house_lords_stability(planets, houses, aspects_data)
            result.extend_points(lords_points)
        
        # 2. Happy Marriage Indicators (R3_x) - FULL VERSION
        happy_points = self._evaluate_happy_marriage(planets, houses)
        result.extend_points(happy_points)
        
        # 3. Unhappy Marriage Indicators (R4_x) - FULL VERSION
        unhappy_points = self._evaluate_unhappy_marriage(planets, houses)
        result.extend_points(unhappy_points)
        
        # 4. Physical Union Compatibility (R7_x) - FULL VERSION
        union_points = self._evaluate_physical_union(planets, houses)
        result.extend_points(union_points)
        
        # 5. Separation/Divorce Risk Analysis
        separation_result = self._evaluate_separation_risk(planets, houses)
        result.extend_points(separation_result["points"])
        result.additional_data["separation_severity"] = separation_result["severity"]
        
        # 6. Dosha Analysis
        dosha_points = self._evaluate_doshas(planets, houses)
        result.extend_points(dosha_points)
        
        # 7. Overall Assessment
        overall = self._calculate_overall_stability(planets, houses)
        result.additional_data["stability_score"] = overall["score"]
        result.add_point(overall["verdict"])
        
        return result

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

    # ═══════════════════════════════════════════════════════════════════
    # KP CORE METHODS (ALL PRESERVED FROM ORIGINAL)
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_happy_marriage(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Happy Married Life Indicators (R3_x).
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        points = []
        
        # Get planets
        Mo = _p(planets, "Moon")
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Su = _p(planets, "Sun")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        c7_star = normalize_planet(cusp7.get("star_nakshatra_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        lord11 = _lord_of(11, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # R3-1: 7th sub-lord is Jupiter/Venus AND signifies 2 or 11
        if c7sub in {"Jupiter", "Venus"}:
            sc = get_signified_score(c7sub, planets, houses)
            if sc.get(2, 0) > 0 or sc.get(11, 0) > 0:
                points.append("💚 7th sub-lord is Jupiter/Venus signifying 2/11 → happy married life [R3_1]")
        
        # R3-2: Mercury/Moon/Sun significator of 7 with 11th lord aspect
        if lord11:
            L11p = _p(planets, lord11)
            for cand_name in ["Mercury", "Moon", "Sun"]:
                cand = _p(planets, cand_name)
                if cand and get_signified_score(cand_name, planets, houses).get(7, 0) > 0:
                    if L11p and has_harmonious_aspect(L11p, cand_name):
                        points.append(f"💚 {cand_name} is significator of 7 with benefic 11th lord aspect → happy life [R3_2]")
        
        # R3-3: Sun & Moon in 7 with mutual good aspect
        if _in_house(Su, 7) and _in_house(Mo, 7):
            if has_harmonious_aspect(Su, "Moon") and has_harmonious_aspect(Mo, "Sun"):
                points.append("💚 Sun & Moon in 7th with mutual good aspect → affectionate & happy union [R3_3]")
        
        # R3-4: Luminary in 7 aspected by Jupiter/Venus signifying 2/11
        for lum, tag in [(Su, "Sun"), (Mo, "Moon")]:
            if _in_house(lum, 7):
                for p_name in ("Jupiter", "Venus"):
                    p_score = get_signified_score(p_name, planets, houses)
                    if (p_score.get(2, 0) + p_score.get(11, 0)) > 0:
                        if has_harmonious_aspect(lum, p_name):
                            points.append(f"💚 {tag} in 7th aspected by {p_name} (signifies 2/11) → strong partnership [R3_4]")
        
        # R3-5: Venus & Mars in good aspect, not significators of 6/10/12
        if has_harmonious_aspect(Ve, "Mars") or has_harmonious_aspect(Ma, "Venus"):
            ve_score = get_signified_score("Venus", planets, houses)
            ma_score = get_signified_score("Mars", planets, houses)
            ve_bad = ve_score.get(6, 0) + ve_score.get(10, 0) + ve_score.get(12, 0)
            ma_bad = ma_score.get(6, 0) + ma_score.get(10, 0) + ma_score.get(12, 0)
            if ve_bad == 0 and ma_bad == 0:
                points.append("💚 Venus & Mars in good aspect, not signifying 6/10/12 → pleasurable union [R3_5]")
        
        # R3-6: Moon receives benefic aspect
        if any(has_harmonious_aspect(Mo, p) for p in ("Saturn", "Venus", "Jupiter")):
            points.append("💚 Moon receives benefic aspect → emotional happiness [R3_6]")
        
        # R3-7: 7th supported by benefics
        if _house_has_benefic_occupation(7, houses) or _benefic_by_lordship_of_house(7, houses):
            points.append("💚 7th house supported by benefics (occupation/lordship) [R3_7]")
        
        # R3_star: 7th cusp star-lord benefic
        if c7_star and c7_star in BENEFICS:
            points.append("💚 7th cusp star-lord is benefic → emotional happiness [R3_star]")
        
        # Venus strong in 7th
        if _in_house(Ve, 7) and _is_strong_planet(Ve, planets):
            points.append("💚 Venus strong in 7th house [R3_Venus]")
        
        # R3_mixed: Mixed aspects indicator
        key_targets = [Ve, L7, Mo]
        good_hits = sum(1 for p in key_targets if p and _has_good_aspect(p))
        bad_hits = sum(1 for p in key_targets if p and _has_evil_aspect(p))
        
        kp_mixed = False
        if c7sub:
            s = get_signified_score(c7sub, planets, houses)
            kp_mixed = (s.get(2, 0) + s.get(7, 0) + s.get(11, 0) >= 2) and \
                       (s.get(6, 0) + s.get(8, 0) + s.get(12, 0) >= 2)
        
        if (good_hits >= 1 and bad_hits >= 1) or kp_mixed:
            points.append("💠 Mixed aspects: enjoyment, with temporary dissatisfaction during malefic periods [R3_mixed]")
        
        return points
    
    def _evaluate_unhappy_marriage(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Unhappy Married Life Indicators (R4_x).
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        points = []
        
        # Get planets
        Mo = _p(planets, "Moon")
        Ve = _p(planets, "Venus")
        Su = _p(planets, "Sun")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        # Get scores
        su_score = get_signified_score("Sun", planets, houses)
        mo_score = get_signified_score("Moon", planets, houses)
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # R4-1: Sun-Moon conflict
        su_sig = set(k for k, v in su_score.items() if v > 0)
        mo_sig = set(k for k, v in mo_score.items() if v > 0)
        if _in_house(Su, 7) and _aspected_by(Su, "Moon"):
            if ({2, 7, 11} & su_sig) or ({2, 7, 11} & mo_sig):
                points.append("💢 Sun-Moon conflict in marriage houses [R4_1]")
        
        # R4-2-3: Malefics harming 7th
        for m in MALEFICS:
            mp = _p(planets, m)
            if _in_house(mp, 7) and _has_evil_aspect(mp):
                points.append(f"💢 {m} harming 7th house [R4_2-3]")
                break
        
        # R4-9: Mercury afflicted in 7
        if _in_house(Me, 7):
            if any(_aspected_by(Me, x) for x in {"Moon", "Mars", "Saturn", "Rahu", "Ketu"}):
                points.append("💢 Mercury afflicted in 7th → miscommunication [R4_9]")
        
        # R4-10-11: 7th cusp afflicted by 6/8/12
        if c7sub:
            s7 = get_signified_score(c7sub, planets, houses)
            if s7.get(6, 0) + s7.get(8, 0) + s7.get(12, 0) >= 3:
                points.append("💢 7th cusp sub-lord heavily afflicted by 6/8/12 signification [R4_10-11]")
        
        # R4-6: Moon-Jupiter disharmony
        if has_harsh_aspect(Mo, "Jupiter"):
            if mo_score.get(7, 0) >= 1 or su_score.get(7, 0) >= 1:
                points.append("💢 Moon-Jupiter disharmony → emotional dissatisfaction [R4_6]")
        
        # R4-7: Mars in 8 (Jupiter sub)
        mars_sub = normalize_planet(Ma.get("sub_lord")) if Ma else None
        if _in_house(Ma, 8) and mars_sub == "Jupiter":
            points.append("💢 Mars in 8th (Jupiter sub) → financial trouble in marriage [R4_7]")
        
        # R4-8: Mars in 8 (Moon sub)
        if _in_house(Ma, 8) and mars_sub == "Moon":
            points.append("💢 Mars in 8th (Moon sub) → temper issues, possible addiction [R4_8]")
        
        # R4_combo: Venus + 7th lord both afflicted
        if _has_evil_aspect(Ve) and L7 and has_harsh_aspect(L7, "Saturn"):
            points.append("💢 Venus + 7th lord both afflicted → serious marital stress [R4_combo]")
        
        return points
    
    def _evaluate_physical_union(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Physical Union Compatibility (R7_x).
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        points = []
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        c7_star = normalize_planet(cusp7.get("star_nakshatra_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # R7_union: Union quality
        union_map = {
            "Sun": "repulsion",
            "Moon": "pleasant/honeymoon",
            "Mars": "friction",
            "Mercury": "playful desire",
            "Jupiter": "normal/pleasant",
            "Venus": "romantic/joyful",
            "Saturn": "cold/low pleasure"
        }
        
        union = union_map.get(c7_star) or union_map.get(c7sub)
        if union:
            source = c7_star if c7_star in union_map else c7sub
            points.append(f"💗 Physical union quality: {union} (from {source}) [R7_union]")
        
        # R7_L7: 7th lord in 5/11
        if L7 and L7.get("house") in {5, 11}:
            points.append("💗 7th lord in 5th/11th → strong compatibility & satisfaction [R7_L7]")
        
        return points
    
    def _evaluate_separation_risk(self, planets: Dict, houses: List) -> Dict[str, Any]:
        """
        Evaluate separation/divorce risk factors.
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        risk_factors = []
        
        # Get planets
        Ve = _p(planets, "Venus")
        Ma = _p(planets, "Mars")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        Mo = _p(planets, "Moon")
        
        # 7th lord
        lord7 = _lord_of(7, houses)
        L7p = _p(planets, lord7) if lord7 else None
        
        MALEFIC_NAMES = ("Mars", "Saturn", "Rahu")
        
        # 1. Malefics in 7th or harsh aspect to 7th lord
        for mal in MALEFIC_NAMES:
            mp = _p(planets, mal)
            if not mp:
                continue
            
            if _in_house(mp, 7):
                risk_factors.append(f"⚠️ {mal} in 7th house → conflict/separation tendency")
            
            if L7p and has_harsh_aspect(L7p, mal):
                risk_factors.append(f"⚠️ {mal} harshly aspects 7th lord ({lord7}) → marital disturbances")
        
        # 2. 6th house influence
        REL_PLANETS = ["Venus", "Moon"]
        if lord7:
            REL_PLANETS.append(lord7)
        
        for pl in REL_PLANETS:
            sig_houses = get_signified_houses(pl, planets, houses)
            if 6 in sig_houses:
                risk_factors.append(f"⚠️ {pl} connected to 6th house → disputes/separation triggers")
        
        # 3. 7th lord in dusthana
        if L7p and _in_houses(L7p, {6, 8, 12}):
            risk_factors.append("⚠️ 7th lord in dusthana (6/8/12) → challenges in marriage stability")
        
        # 4. Rahu-Ketu axis on 1-7
        if _in_house(Ra, 1) and _in_house(Ke, 7):
            risk_factors.append("⚠️ Rahu-Ketu axis on 1-7 → karmic relationship patterns")
        elif _in_house(Ra, 7) and _in_house(Ke, 1):
            risk_factors.append("⚠️ Rahu in 7th → unconventional partnership, potential instability")
        
        # 5. Saturn afflicting Venus/Moon
        if has_harsh_aspect(Ve, "Saturn"):
            risk_factors.append("⚠️ Saturn afflicts Venus → emotional distance possible")
        if has_harsh_aspect(Mo, "Saturn"):
            risk_factors.append("⚠️ Saturn afflicts Moon → emotional coldness risk")
        
        # Severity Rating
        R = len(risk_factors)
        if R >= 4:
            severity = "High"
        elif R >= 2:
            severity = "Moderate"
        else:
            severity = "Low"
        
        return {
            "points": risk_factors,
            "severity": severity,
            "risk_count": R
        }
    
    def _evaluate_divorce_separation_book_rules(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Book-4 divorce/separation rules.
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        All B4_R1 through B4_R9 rules included.
        """
        points = []
        
        # Helper functions
        def _star_of(p):
            if not p:
                return None
            return normalize_planet(p.get("nakshatra_lord"))
        
        def _sub_of(p):
            if not p:
                return None
            return normalize_planet(p.get("sub_lord"))
        
        def is_dual_sign(sign: str) -> bool:
            return sign in {"Gemini", "Virgo", "Sagittarius", "Pisces"}
        
        # Get all planets
        Su = _p(planets, "Sun")
        Mo = _p(planets, "Moon")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        Ju = _p(planets, "Jupiter")
        Ve = _p(planets, "Venus")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        _planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        # Get 2nd cusp data
        cusp2 = next((h for h in houses if h.get("house") == 2), {})
        c2sub = normalize_planet(cusp2.get("cusp_sub_lord", ""))
        
        dual_signs = {"Gemini", "Virgo", "Sagittarius", "Pisces"}
        
        # R6_certainty_book: Multiple Marriages CERTAIN
        if c7sub:
            sub_p = _p(planets, c7sub)
            if sub_p:
                sub_sign = (sub_p.get("sign") or sub_p.get("rasi") or "").title()
                sub_star = normalize_planet(sub_p.get("nakshatra_lord"))
                
                cond1 = sub_sign in dual_signs
                cond2 = sub_star in {"Rahu", "Ketu"}
                
                node_p = _p(planets, sub_star) if cond2 else None
                node_sign = (node_p.get("sign") or node_p.get("rasi") or "").title() if node_p else None
                cond3 = node_sign in dual_signs
                
                if cond1 and cond2 and cond3:
                    points.append("🔁 **CERTAIN multiple marriages** (CSL dual-sign + node star + node in dual) [R6_certainty_book]")
        
        # R_sep_full: Separation Scoring Logic
        sep_houses = {1, 6, 10, 12}
        sep_connections = 0
        sep_afflicted = 0
        sep_strong_planet_hits = 0
        
        for pname in _planet_names:
            p_obj = _p(planets, pname)
            if not p_obj:
                continue
            
            p_house = p_obj.get("house")
            if isinstance(p_house, int) and p_house in sep_houses:
                sep_connections += 1
                if _has_evil_aspect(p_obj) or has_harsh_aspect(p_obj, "Saturn") or has_harsh_aspect(p_obj, "Mars"):
                    sep_afflicted += 1
                if _is_strong_planet(p_obj, planets):
                    sep_strong_planet_hits += 1
                continue
            
            sc = get_signified_score(pname, planets, houses)
            if sc.get(1, 0) + sc.get(6, 0) + sc.get(10, 0) + sc.get(12, 0) > 0:
                sep_connections += 1
                if sc.get(6, 0) + sc.get(12, 0) > 0:
                    sep_afflicted += 1
                if _is_strong_planet(p_obj, planets):
                    sep_strong_planet_hits += 1
        
        if sep_connections >= 3:
            points.append(f"💔 Separation risk STRONG — {sep_connections} planets connect with houses 1/6/10/12; {sep_strong_planet_hits} are strong planets [R_sep_full_strong]")
        elif sep_connections == 2 and (sep_afflicted >= 1 or sep_strong_planet_hits >= 1):
            points.append("💔 Separation risk MODERATE — 2 connections + afflicted/strong planet [R_sep_full_moderate]")
        elif sep_connections == 2:
            points.append("💔 Separation risk WEAK — 2 planets connect to separation houses [R_sep_full_weak]")
        
        # R_divorce_book: Ketu as 7th CSL in dual sign
        if c7sub == "Ketu":
            ketu_p = _p(planets, "Ketu")
            ketu_sign = (ketu_p.get("sign") or ketu_p.get("rasi") or "").title() if ketu_p else None
            if ketu_sign and is_dual_sign(ketu_sign):
                points.append("💢 Divorce/second-marriage indicated — 7th cusp sub-lord is Ketu in dual sign [R_divorce_book]")
        
        # R6_2nd_cusp: Second marriage
        if c2sub:
            c2_sc = get_signified_score(c2sub, planets, houses)
            if c2_sc.get(7, 0) > 0:
                points.append("🔁 Second marriage likely — 2nd cusp's sub-lord signifies 7th house [R6_2nd_cusp]")
        
        # Book-4 Star/Sub Rules (B4_R1 - B4_R9)
        
        # B4_R1: Sun in Saturn star
        if Su:
            su_star = _star_of(Su)
            if su_star == "Saturn":
                sat = _p(planets, "Saturn")
                if sat:
                    sat_h = sat.get("house")
                    if sat_h == 11:
                        points.append("💚 Sun in Saturn star → Saturn lord of 11 → union signified [B4_R1_union]")
                    elif sat_h == 12:
                        points.append("💔 Sun in Saturn star → Saturn occupies 12 → separation signified [B4_R1_sep]")
        
        # B4_R2: Moon in Rahu star + Mars sub
        if Mo:
            mo_star = _star_of(Mo)
            mo_sub = _sub_of(Mo)
            if mo_star == "Rahu" and mo_sub == "Mars":
                points.append("💔 Moon in Rahu star + Mars sub → union first, separation later [B4_R2]")
        
        # B4_R3: Mars in Rahu sub
        if Ma:
            ma_sub = _sub_of(Ma)
            if ma_sub == "Rahu":
                points.append("💔 Mars in Rahu sub → ultimate separation indicated [B4_R3]")
        
        # B4_R4: Mercury in star of 12th lord + sub of Rahu
        if Me:
            me_star = _star_of(Me)
            me_sub = _sub_of(Me)
            
            lord12 = _lord_of(12, houses)
            if lord12:
                me_star_is_l12_lord = (me_star == normalize_planet(lord12))
            else:
                me_star_is_l12_lord = False
            
            if me_star_is_l12_lord and me_sub == "Rahu":
                points.append("💔 Mercury in star of 12th lord & sub of Rahu → marital separation [B4_R4]")
        
        # B4_R5: Jupiter in Venus star + Jupiter sub in 12
        if Ju:
            ju_star = _star_of(Ju)
            ju_sub = _sub_of(Ju)
            j_sub_p = _p(planets, ju_sub) if ju_sub else None
            if ju_star == "Venus" and ju_sub == "Jupiter":
                if j_sub_p and j_sub_p.get("house") == 12:
                    points.append("💔 Jupiter in Venus star + Jupiter sub in 12 → legal divorce indicated [B4_R5]")
        
        # B4_R6: Venus in 2nd + Rahu star + Rahu sub
        if Ve:
            ve_h = Ve.get("house")
            ve_star = _star_of(Ve)
            ve_sub = _sub_of(Ve)
            if ve_h == 2 and ve_star == "Rahu" and ve_sub == "Rahu":
                points.append("💔 Venus in 2nd + Rahu star + Rahu sub → both union & separation potentials [B4_R6]")
        
        # B4_R7: Saturn in Venus star + Rahu sub
        if Sa:
            sa_star = _star_of(Sa)
            sa_sub = _sub_of(Sa)
            if sa_star == "Venus" and sa_sub == "Rahu":
                points.append("💔 Saturn in Venus star + Rahu sub → ultimate separation [B4_R7]")
        
        # B4_R8: Rahu in Moon star + Venus sub
        if Ra:
            ra_star = _star_of(Ra)
            ra_sub = _sub_of(Ra)
            if ra_star == "Moon" and ra_sub == "Venus":
                points.append("💚 Rahu in Moon star + Venus sub → united married life [B4_R8]")
        
        # B4_R9: Ketu in Mercury star + Venus sub
        if Ke:
            ke_star = _star_of(Ke)
            ke_sub = _sub_of(Ke)
            if ke_star == "Mercury" and ke_sub == "Venus":
                points.append("💚 Ketu in Mercury star + Venus sub → unites [B4_R9]")
        
        return points
    
    def _evaluate_doshas(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate doshas affecting marriage.
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        points = []
        
        Ma = _p(planets, "Mars")
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        # Manglik Dosha
        mars_house = Ma.get("house") if Ma else None
        manglik = mars_house in {1, 2, 4, 7, 8, 12} if mars_house else False
        
        if manglik:
            cancellation = False
            if _is_own_sign(Ma) or _is_exalted(Ma):
                cancellation = True
                points.append("Manglik dosha present but cancelled by Mars in own/exalted sign")
            elif _aspected_by(Ma, "Jupiter"):
                cancellation = True
                points.append("Manglik dosha mitigated by Jupiter's aspect")
            elif mars_house == 1 and Ma.get("sign") in {"Aries", "Scorpio"}:
                cancellation = True
                points.append("Manglik cancelled - Mars in own sign in 1st house")
            elif mars_house == 8 and Ma.get("sign") == "Scorpio":
                cancellation = True
                points.append("Manglik cancelled - Mars in own sign in 8th house")
            
            if not cancellation:
                points.append(f"Manglik dosha present (Mars in house {mars_house}) - partner matching advised")
        
        # Kuja Dosha variations
        if _in_house(Ma, 4):
            points.append("Mars in 4th house may affect domestic peace - conscious effort needed")
        
        # Rahu-Venus combination
        if _conjoined(Ra, Ve) or _aspected_by(Ve, "Rahu"):
            points.append("Rahu-Venus combination - unconventional relationship experiences")
        
        # Ketu with Venus
        if _conjoined(Ke, Ve):
            points.append("Ketu-Venus conjunction - spiritual approach to relationships, possible detachment")
        
        # Paap Kartari Yoga
        malefic_in_6 = any(_in_house(_p(planets, m), 6) for m in MALEFICS)
        malefic_in_8 = any(_in_house(_p(planets, m), 8) for m in MALEFICS)
        if malefic_in_6 and malefic_in_8:
            points.append("Paap Kartari on 7th house - marriage under pressure, extra care needed")
        
        return points
    
    def _calculate_overall_stability(self, planets: Dict, houses: List) -> Dict[str, Any]:
        """
        Calculate overall stability.
        
        PRESERVED FROM ORIGINAL - NO CHANGES
        """
        positive_count = 0
        negative_count = 0
        
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Mo = _p(planets, "Moon")
        Ma = _p(planets, "Mars")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        lord7 = _lord_of(7, houses)
        
        # Positive factors
        benefics_in_7 = sum(1 for b in BENEFICS if _in_house(_p(planets, b), 7))
        positive_count += benefics_in_7
        
        if has_harmonious_aspect(Ve, "Jupiter"):
            positive_count += 1
        if _is_own_sign(Ve) or _is_exalted(Ve):
            positive_count += 1
        if _has_good_aspect(Ve):
            positive_count += 1
        if _has_good_aspect(Mo):
            positive_count += 1
        
        # Negative factors
        malefics_in_7 = sum(1 for m in MALEFICS if _in_house(_p(planets, m), 7))
        negative_count += malefics_in_7
        
        if lord7:
            l7_planet = _p(planets, lord7)
            if _in_houses(l7_planet, {6, 8, 12}):
                negative_count += 2
        
        if _in_house(Ra, 7) or _in_house(Ke, 7):
            negative_count += 1
        
        if has_harsh_aspect(Ve, "Saturn"):
            negative_count += 1
        
        if _has_evil_aspect(Ve, Ma):
            negative_count += 1
        
        # Calculate verdict
        net_score = positive_count - negative_count
        
        if net_score >= 3:
            verdict = "Overall: Strong marital stability indicated"
        elif net_score <= -3:
            verdict = "Overall: Attention needed for marital harmony - remedies recommended"
        else:
            verdict = "Overall: Mixed indicators - balance of strengths and challenges in marriage"
        
        return {
            "score": net_score,
            "positive": positive_count,
            "negative": negative_count,
            "verdict": verdict
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # NEW METHODS (Added for enhancement)
    # ═══════════════════════════════════════════════════════════════════
    
    def _evaluate_kp_divorce_core(self, planets: Dict, houses: List) -> List[str]:
        """
        Core KP divorce analysis (for divorce questions).
        
        Focuses on:
        - 7th CSL and significations
        - Divorce promise level
        """
        points = []
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        points.append("═══ KP DIVORCE ANALYSIS ═══")
        
        if c7sub:
            points.append(f"7th Cusp Sub-Lord (CSL): {c7sub}")
            
            # Get signification score
            c7sub_sig = get_signified_score(c7sub, planets, houses)
            
            # Check for divorce significations
            divorce_sig = c7sub_sig.get(6, 0) + c7sub_sig.get(8, 0) + c7sub_sig.get(12, 0)
            marriage_sig = c7sub_sig.get(2, 0) + c7sub_sig.get(7, 0) + c7sub_sig.get(11, 0)
            
            # Show significations
            sig_details = []
            for house_num in [2, 6, 7, 8, 11, 12]:
                score = c7sub_sig.get(house_num, 0)
                if score > 0:
                    sig_details.append(f"{house_num}th:{score}")
            
            if sig_details:
                points.append(f"Significations: {', '.join(sig_details)}")
            
            # Divorce promise assessment
            if divorce_sig >= 3:
                points.append(
                    f"🚨 KP DIVORCE PROMISE: STRONG (CSL signifies 6/8/12 heavily, score: {divorce_sig})"
                )
            elif divorce_sig >= 2:
                points.append(
                    f"⚠️ KP DIVORCE PROMISE: MODERATE (Some 6/8/12 signification, score: {divorce_sig})"
                )
            elif marriage_sig >= 2:
                points.append(
                    f"✅ KP DIVORCE PROMISE: LOW (Marriage houses signified, score: {marriage_sig})"
                )
            else:
                points.append("⚖️ KP DIVORCE PROMISE: NEUTRAL (Mixed significations)")

            # ── Explicit YES / NO KP Verdict ──────────────────────────
            points.append("")
            points.append("══ KP EXPLICIT DIVORCE VERDICT ══")
            if divorce_sig >= 3:
                points.append(
                    f"🚨 KP SAYS: YES — Strong divorce / separation PROMISE exists in the chart."
                )
                points.append(
                    f"   7th CSL ({c7sub}) heavily signifies separation houses (6/8/12: score {divorce_sig})."
                )
                points.append(
                    "   KP confirms this chart carries a definite risk of marital break."
                )
            elif divorce_sig >= 2:
                points.append(
                    f"⚠️ KP SAYS: POSSIBLE — Moderate divorce RISK. Chart shows tendencies."
                )
                points.append(
                    f"   7th CSL ({c7sub}) signifies some separation houses (6/8/12: score {divorce_sig})."
                )
                points.append(
                    "   KP does NOT give a clear-cut promise; outcome depends on dasha and remedies."
                )
            else:
                points.append(
                    f"✅ KP SAYS: NO — No clear divorce promise in the chart."
                )
                points.append(
                    f"   7th CSL ({c7sub}) primarily signifies marriage/stability houses "
                    f"(2/7/11: score {marriage_sig})."
                )
                points.append(
                    "   KP analysis does NOT support a divorce / separation outcome."
                )
            points.append("══════════════════════════════════")
        else:
            points.append("⚠️ 7th cusp sub-lord data not available — KP divorce verdict cannot be determined")

        return points
    
    def _evaluate_divorce_house_lords(
        self,
        planets: Dict,
        houses: List,
        aspects_data: Dict
    ) -> List[str]:
        """
        House lords for divorce (focuses on 7th, 6th, 8th, 12th).
        Uses fallback method directly for reliability.
        """
        points = []
        
        points.append("")
        points.append("═══ HOUSE LORDS DIVORCE ANALYSIS ═══")
        
        # Use robust fallback method that works with any data format
        try:
            # Get lords directly
            lord7 = _lord_of(7, houses)
            lord6 = _lord_of(6, houses)
            lord8 = _lord_of(8, houses)
            lord12 = _lord_of(12, houses)
            
            # 7th Lord Analysis
            if lord7:
                L7 = _p(planets, lord7)
                if L7:
                    l7_house = L7.get("house")
                    l7_sign = L7.get("sign", "") or L7.get("rasi", "")
                    l7_dignity = calculate_dignity_fallback(lord7, l7_sign)
                    l7_strength = self._calculate_lord_strength_from_dignity(lord7, L7, l7_dignity)
                    
                    points.append(f"7th Lord ({lord7}): In house {l7_house}, {l7_sign}")
                    points.append(f"   Dignity: {l7_dignity}, Strength: {l7_strength}/100")
                    
                    if l7_house in {6, 8, 12}:
                        points.append(
                            f"🚨 7th lord in dusthana (house {l7_house}) → "
                            f"Significant marital challenges"
                        )
                    
                    # Check for afflictions
                    is_combust = L7.get("is_combust", False) or L7.get("is_combusted", False)
                    is_retro = L7.get("is_retro", False) or L7.get("is_retrograde", False)
                    
                    if is_combust:
                        points.append(f"⚠️ 7th lord combust → Marital harmony weakened")
                    
                    if l7_strength >= 70:
                        points.append(f"✅ 7th lord strong → Marriage resilience good")
                    elif l7_strength < 40:
                        points.append(f"⚠️ 7th lord weak → Marriage needs attention")
            
            # 6th Lord in 7th check
            if lord6:
                L6 = _p(planets, lord6)
                if L6 and L6.get("house") == 7:
                    points.append("⚠️ 6th lord in 7th → Disputes in marriage")
            
            # 8th Lord in 7th check
            if lord8:
                L8 = _p(planets, lord8)
                if L8 and L8.get("house") == 7:
                    points.append("⚠️ 8th lord in 7th → Obstacles/transformation")
            
            # 12th Lord in 7th check
            if lord12:
                L12 = _p(planets, lord12)
                if L12 and L12.get("house") == 7:
                    points.append("🚨 12th lord in 7th → Separation tendency")
            
        except Exception as e:
            logger.error(f"Divorce house lords error: {e}")
            return self._fallback_divorce_lords(planets, houses)
        
        return points
    
    def _compute_canonical_kp_divorce_verdict(
        self,
        planets: Dict,
        houses: List
    ) -> Dict:
        """
        Compute ONE authoritative KP divorce verdict shared across ALL questions.

        This is computed BEFORE the divorce vs general branch so that:
        - Q1 (general divorce risk)  — sees the same KP conclusion
        - Q2 (divorce timing)        — sees the same KP conclusion

        Prevents the contradiction where Q1 says "low risk" and Q2 says
        "chart promises separation" for the identical chart data.
        """
        try:
            cusp7 = next((h for h in houses if h.get("house") == 7), {})
            c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))

            if not c7sub:
                return {
                    "available": False,
                    "verdict": "UNKNOWN",
                    "verdict_label": "⚪ KP SAYS: UNKNOWN — 7th CSL data not available",
                    "explanation": "7th house Cusp Sub-Lord data is not available. KP verdict cannot be determined.",
                    "divorce_sig": 0,
                    "marriage_sig": 0,
                }

            c7sub_sig = get_signified_score(c7sub, planets, houses)
            divorce_sig  = c7sub_sig.get(6, 0) + c7sub_sig.get(8, 0) + c7sub_sig.get(12, 0)
            marriage_sig = c7sub_sig.get(2, 0) + c7sub_sig.get(7, 0) + c7sub_sig.get(11, 0)

            sig_parts = []
            for h in [2, 6, 7, 8, 11, 12]:
                s = c7sub_sig.get(h, 0)
                if s:
                    sig_parts.append(f"H{h}:{s}")
            sig_str = ", ".join(sig_parts) if sig_parts else "none"

            if divorce_sig >= 3:
                verdict = "YES"
                verdict_label = (
                    f"🚨 KP SAYS: YES — Strong divorce/separation PROMISE."
                )
                explanation = (
                    f"7th CSL is {c7sub}, which heavily signifies separation houses "
                    f"(6/8/12 combined score: {divorce_sig}). Significations: {sig_str}. "
                    f"KP confirms the chart carries a definite divorce/separation risk."
                )
            elif divorce_sig >= 2:
                verdict = "POSSIBLE"
                verdict_label = (
                    f"⚠️ KP SAYS: POSSIBLE — Moderate divorce risk, not a firm promise."
                )
                explanation = (
                    f"7th CSL is {c7sub}, with some separation-house signification "
                    f"(6/8/12 score: {divorce_sig}, marriage score: {marriage_sig}). "
                    f"Significations: {sig_str}. "
                    f"KP does NOT give a clear-cut divorce promise; outcome depends on dasha and remedies."
                )
            else:
                verdict = "NO"
                verdict_label = (
                    f"✅ KP SAYS: NO — No clear divorce promise in this chart."
                )
                explanation = (
                    f"7th CSL is {c7sub}, which primarily signifies marriage/stability houses "
                    f"(2/7/11 score: {marriage_sig}, separation score: {divorce_sig}). "
                    f"Significations: {sig_str}. "
                    f"KP analysis does NOT support a divorce/separation outcome."
                )

            logger.info(f"✅ Canonical KP divorce verdict: {verdict} (div_sig={divorce_sig}, mar_sig={marriage_sig})")

            return {
                "available": True,
                "csl": c7sub,
                "verdict": verdict,        # "YES" | "POSSIBLE" | "NO"
                "verdict_label": verdict_label,
                "explanation": explanation,
                "divorce_sig": divorce_sig,
                "marriage_sig": marriage_sig,
                "significations": sig_str,
            }

        except Exception as e:
            logger.error(f"Canonical KP divorce verdict error: {e}")
            return {}

    def _compute_canonical_dasha_verdict(
        self,
        planets: Dict,
        houses: List,
        kwargs: Dict
    ) -> Dict:
        """
        Compute a single, canonical dasha verdict shared across ALL questions.

        This prevents the inconsistency where the same dasha period is described
        as 'good' in one question (general stability) and 'bad' in another
        (divorce risk). Both perspectives are captured here so the LLM uses
        consistent language regardless of question type.
        """
        try:
            current_dasha = kwargs.get("current_dasha") or {}
            maha = current_dasha.get("major_lord", "") or ""
            antar = current_dasha.get("minor_lord", "") or ""
            prat = current_dasha.get("sub_lord", "") or ""
            period_label = f"{maha}-{antar}-{prat}" if prat else (f"{maha}-{antar}" if antar else maha)

            # Houses that indicate marital happiness (positive)
            lord2  = _lord_of(2, houses)   # Family, domestic harmony
            lord7  = _lord_of(7, houses)   # Spouse, partnership
            lord11 = _lord_of(11, houses)  # Fulfilment, gains
            harmony_lords = {p for p in [lord2, lord7, lord11, "Jupiter", "Venus"] if p}

            # Houses that indicate separation / divorce risk (negative)
            lord6  = _lord_of(6, houses)   # Disputes, enmity
            lord8  = _lord_of(8, houses)   # Obstacles, transformation
            lord12 = _lord_of(12, houses)  # Loss, separation
            risk_lords = {p for p in [lord6, lord8, lord12, "Saturn", "Rahu", "Ketu"] if p}

            harmony_planets = [p for p in [maha, antar, prat] if p in harmony_lords]
            risk_planets    = [p for p in [maha, antar, prat] if p in risk_lords]

            is_harmony  = bool(harmony_planets)
            is_risk     = bool(risk_planets)

            if is_harmony and is_risk:
                marriage_verdict = "MIXED"
                separation_verdict = "MODERATE_RISK"
                summary = (
                    f"MIXED DASHA: {period_label} period has dual effects. "
                    f"{', '.join(harmony_planets)} bring marital harmony and stability, "
                    f"while {', '.join(risk_planets)} introduce some tension/separation energy. "
                    f"Overall this is a testing period requiring conscious effort."
                )
            elif is_harmony:
                marriage_verdict = "POSITIVE"
                separation_verdict = "LOW_RISK"
                summary = (
                    f"FAVORABLE DASHA: {period_label} period is broadly supportive of marriage. "
                    f"{', '.join(harmony_planets)} strengthen the marital bond and family harmony. "
                    f"Divorce/separation risk is low in this period."
                )
            elif is_risk:
                marriage_verdict = "CHALLENGING"
                separation_verdict = "ELEVATED_RISK"
                summary = (
                    f"CHALLENGING DASHA: {period_label} period carries marital stress. "
                    f"{', '.join(risk_planets)} activate separation/conflict themes. "
                    f"This is NOT necessarily a divorce period, but requires attention and remedies."
                )
            else:
                marriage_verdict = "NEUTRAL"
                separation_verdict = "NEUTRAL"
                summary = (
                    f"NEUTRAL DASHA: {period_label} period has neither strong marriage-positive "
                    f"nor strong separation-risk indicators. Effects depend largely on natal chart strength."
                )

            logger.info(f"✅ Canonical dasha verdict: {marriage_verdict} / {separation_verdict} for {period_label}")

            return {
                "period": period_label,
                "maha": maha,
                "antar": antar,
                "prat": prat,
                "marriage_verdict": marriage_verdict,
                "separation_verdict": separation_verdict,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"Canonical dasha verdict error: {e}")
            return {}

    def _evaluate_divorce_dasha_timing(
        self,
        planets: Dict,
        houses: List,
        metadata: Dict
    ) -> List[str]:
        """
        Dasha-based divorce timing.
        """
        points = []
        
        points.append("")
        points.append("═══ DIVORCE TIMING (DASHA) ═══")
        
        try:
            current_dasa = metadata.get("current_dasa", {})
            maha = current_dasa.get("major_lord", "")
            antar = current_dasa.get("minor_lord", "")
            
            lord6 = _lord_of(6, houses)
            lord8 = _lord_of(8, houses)
            lord12 = _lord_of(12, houses)
            
            risk_lords = set()
            if lord6:
                risk_lords.add(lord6)
            if lord8:
                risk_lords.add(lord8)
            if lord12:
                risk_lords.add(lord12)
            risk_lords.update({"Saturn", "Rahu", "Mars"})
            
            if maha in risk_lords:
                points.append(f"⚠️ Current {maha} Mahadasha → Risk period for marital challenges")
            else:
                points.append(f"Current {maha} Mahadasha → Not a high-risk period")
            
            if risk_lords:
                risk_list = sorted(list(risk_lords))
                points.append(f"HIGH-RISK PERIODS: {', '.join(risk_list)} Mahadasha/Antardasha")
        
        except Exception as e:
            logger.error(f"Divorce dasha timing error: {e}")
        
        return points
    
    def _get_divorce_relevant_r4_rules(self, planets: Dict, houses: List) -> List[str]:
        """
        Get R4_x rules most relevant to divorce (filtered version).
        """
        # Get full R4_x list
        all_r4 = self._evaluate_unhappy_marriage(planets, houses)
        
        # Filter to most critical ones
        critical_keywords = ["heavily afflicted", "both afflicted", "conflict", "harming"]
        
        critical_r4 = [p for p in all_r4 if any(kw in p for kw in critical_keywords)]
        
        if critical_r4:
            return ["", "═══ CRITICAL UNHAPPY INDICATORS ═══"] + critical_r4[:5]
        else:
            return []
    
    def _calculate_divorce_risk_level(self, planets: Dict, houses: List) -> Dict[str, Any]:
        """
        Calculate divorce risk level.
        """
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        risk_score = 0
        
        # KP CSL check
        if c7sub:
            c7sub_sig = get_signified_score(c7sub, planets, houses)
            divorce_sig = c7sub_sig.get(6, 0) + c7sub_sig.get(8, 0) + c7sub_sig.get(12, 0)
            
            if divorce_sig >= 3:
                risk_score += 3
            elif divorce_sig >= 2:
                risk_score += 2
        
        # 7th lord in dusthana
        lord7 = _lord_of(7, houses)
        if lord7:
            L7 = _p(planets, lord7)
            if L7 and _in_houses(L7, {6, 8, 12}):
                risk_score += 2
        
        # Malefics in 7th
        malefics_in_7 = sum(1 for m in ["Mars", "Saturn", "Rahu", "Ketu"] 
                           if _in_house(_p(planets, m), 7))
        risk_score += malefics_in_7
        
        # Determine level
        if risk_score >= 5:
            level = "HIGH"
            verdict = "High divorce/separation risk - Remedies and counseling strongly recommended"
        elif risk_score >= 3:
            level = "MODERATE"
            verdict = "Moderate separation tendency - Conscious effort essential"
        elif risk_score >= 1:
            level = "LOW"
            verdict = "Low separation risk - Minor challenges can be overcome"
        else:
            level = "MINIMAL"
            verdict = "Minimal divorce risk - Marriage stability indicated"
        
        return {
            "level": level,
            "score": risk_score,
            "verdict": verdict
        }
    
    def _evaluate_house_lords_stability(
        self,
        planets: Dict,
        houses: List,
        aspects_data: Dict
    ) -> List[str]:
        """
        House lords for general stability (focuses on 7th, 8th, 2nd).
        Uses direct calculation for reliability.
        """
        points = []
        
        try:
            # Get 7th lord directly
            lord7 = _lord_of(7, houses)
            
            if lord7:
                L7 = _p(planets, lord7)
                if L7:
                    l7_house = L7.get("house")
                    l7_sign = L7.get("sign", "") or L7.get("rasi", "")
                    l7_dignity = calculate_dignity_fallback(lord7, l7_sign)
                    l7_strength = self._calculate_lord_strength_from_dignity(lord7, L7, l7_dignity)
                    
                    points.append(f"7th House Lord: {lord7} in house {l7_house} ({l7_sign})")
                    points.append(f"   Dignity: {l7_dignity}, Strength: {l7_strength}/100")
                    
                    # Condition details
                    conditions = []
                    if L7.get("is_combust", False) or L7.get("is_combusted", False):
                        conditions.append("Combust")
                    if L7.get("is_retro", False) or L7.get("is_retrograde", False):
                        conditions.append("Retrograde")
                    
                    if conditions:
                        points.append(f"   Condition: {', '.join(conditions)}")
                    
                    if l7_strength >= 70:
                        points.append("✅ Strong 7th lord → Stable marriage foundation")
                    elif l7_strength >= 40:
                        points.append("⚖️ Moderate 7th lord → Marriage stable with effort")
                    else:
                        points.append("⚠️ Weak 7th lord → Marriage needs extra attention")
        
        except Exception as e:
            logger.error(f"House lords stability error: {e}")
        
        return points
    
    def _fallback_divorce_lords(self, planets: Dict, houses: List) -> List[str]:
        """Fallback when house lords analyzer unavailable"""
        points = []
        
        lord7 = _lord_of(7, houses)
        if lord7:
            L7 = _p(planets, lord7)
            if L7:
                l7_house = L7.get("house")
                if l7_house in {6, 8, 12}:
                    points.append(f"⚠️ 7th lord ({lord7}) in dusthana → Marital challenges")
        
        return points
    
    def get_questions(self) -> List[Question]:
        """Get predefined questions"""
        return [
            Question(
                id="MAR_STAB_DIV1",
                question="Are there astrological indications of separation, divorce risk, or marital instability? What is the severity?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Divorce/Separation"
            ),
            Question(
                id="MAR_STAB_DIV_TIME1",
                question="During which periods is marital instability or separation risk more actively triggered?",
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Divorce Timing"
            ),
            Question(
                id="MAR_STAB_COMP1",
                question="What are the indicators for a happy vs unhappy married life? How compatible is the chart for marital happiness?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Compatibility"
            ),
            Question(
                id="MAR_STAB_D1",
                question="Are there stress-indicating combinations or dosha-like patterns affecting marital stability, and how can their impact be reduced?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Doshas and Stress Factors"
            )
        ]
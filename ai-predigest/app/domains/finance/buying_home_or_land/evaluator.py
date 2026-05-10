"""
Buying Home or Land Evaluator - FIXED VERSION v3.0

FIXES & ENHANCEMENTS:
✅ _extract_timing_windows now handles TimingWindow objects (not just dicts)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP analysis preserved and passed to LLM

Features:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support
✅ TimingWindow dataclass compatibility (FIXED)
"""

from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
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

from app.core.astro_constants import detect_aspects, normalize_planet_name
from app.domains.excel_structure_config import get_houses_for_question


# ---- STRICT FINANCE / PROPERTY ENGINES (NO MODIFICATION) ----
from app.domains.finance.finance_engine import (
    evaluate_house_purchase_strict
)

from app.services.timing_engine import (
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets,
    TIMING_RULES
)


# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
    logging.warning("House lords analyzer available")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BuyingHomeOrLandEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Finance → Buying Home or Land
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Timing windows extraction and formatting (FIXED)
    """

    domain = "Finance"
    subtopic = "Buying Home or Land"

    # --------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------
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

        # USE VEDIC DATA FOR HOUSE LORDS ANALYSIS
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        # ═══════════════════════════════════════════════════════
        # STEP 1: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════
        question_text = kwargs.get("question", "")
        
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
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback")
            all_relevant_houses = {2, 4, 6, 8, 11, 12}
            primary_houses = {4, 11}
            secondary_houses = {2, 6, 8, 12}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Buying Home or Land")

        # Handle both dict and QueryMeta object
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("BUYING HOME OR LAND EVALUATOR (ENHANCED v3.0 - FIXED)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects
        # ═══════════════════════════════════════════════════════
        detect_aspects(planets)
        detect_aspects(analysis_planets)
        
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract House Lords Data (for relevant houses only)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses, 
            analysis_planets, 
            all_relevant_houses,
            primary_houses
        )
        
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 4: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )
        
        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 5: Extract Timing Windows (FIXED - Handles TimingWindow objects!)
        # ═══════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})
        
        # DEBUG logging
        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: timing_windows_raw keys: {list(timing_windows_raw.keys()) if isinstance(timing_windows_raw, dict) else 'N/A'}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")
        
        # Handle both dict (keyed by sub-subdomain) and list formats
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            # Try exact match first
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")
            
            # Fallback: try "Property Purchase" key
            if not timing_windows_list and "Property Purchase" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Property Purchase"]
                logger.info(f"🔍 DEBUG: Using 'Property Purchase' fallback key, found {len(timing_windows_list)} windows")
            
            # Another fallback: try "Prospects of Property"
            if not timing_windows_list and "Prospects of Property" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Prospects of Property"]
                logger.info(f"🔍 DEBUG: Using 'Prospects of Property' fallback key, found {len(timing_windows_list)} windows")
        else:
            # Treat as list directly
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")
        
        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = self._extract_timing_windows(timing_windows_list)
        
        # ✅ NEW: Generate Property Timing KP Significator Proof
        if timing_windows_data and timing_windows_data.get('has_timing'):
            try:
                property_timing_proof = self._generate_property_timing_proof(
                    planets=planets,
                    houses=houses,
                    timing_windows_data=timing_windows_data
                )
                logger.info(f"✅ Generated property timing significator proof")
                logger.info(f"   Significator table entries: {len(property_timing_proof.get('significator_table', []))}")
                logger.info(f"   Timing proofs generated: {len(property_timing_proof.get('timing_proofs', []))}")
                
                # Store proof in timing_windows_data
                timing_windows_data["property_proof"] = property_timing_proof
            except Exception as e:
                logger.warning(f"Could not generate property timing proof: {e}")
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            logger.info(f"❌ No timing windows available for '{sub_subdomain}'")

        # ═══════════════════════════════════════════════════════
        # STEP 6: Add House Analysis to Points (only for property questions)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Prospects of Property", "Property Purchase", "Property Risks"}:
            self._add_house_analysis_points(
                result, 
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # --------------------------------------------------
        # EXISTING LOGIC: LLM-ONLY QUESTIONS (NO ASTRO FIRING)
        # --------------------------------------------------
        if sub_subdomain in {
            "Vastu Guidance for Property"
        }:
            result.add_point(
                "This question is evaluated using Vastu principles and practical layout considerations, "
                "not predictive astrology."
            )
            
            # Still store house data for LLM context
            self._store_data_for_llm(
                result,
                house_config,
                house_lords_info,
                house_aspects_info,
                primary_houses,
                secondary_houses,
                timing_windows_data
            )
            return result

        # --------------------------------------------------
        # EXISTING LOGIC: PROPERTY PURCHASE PROMISE + TIMING
        # --------------------------------------------------
        # --------------------------------------------------
        # PROPERTY PURCHASE PROMISE + TIMING (ENHANCED WITH STRUCTURED KP)
        # --------------------------------------------------
        if sub_subdomain == "Prospects of Property" or sub_subdomain == "Property Purchase":

            # ---- Strict Property Promise (TEXT from finance_engine) ----
            try:
                property_text_points = evaluate_house_purchase_strict(
                    planets=planets,
                    houses=houses,
                    d9=kwargs.get("d9")
                )

                # ✅ NEW: Extract structured KP data directly from cusps
                kp_structured = self._extract_kp_property_structured_direct(planets, houses)

                # ✅ NEW: Add points with "KP:" prefix for KP-related points
                if property_text_points:
                    for p in property_text_points:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)
                else:
                    result.add_point(
                        "Property purchase indicators are weak or delayed under strict evaluation."
                    )

                # ✅ NEW: Store structured KP data in additional_data
                result.additional_data["kp_property_analysis"] = kp_structured
                
                if kp_structured.get("has_kp_data"):
                    logger.info(f"✅ Structured KP property data extracted:")
                    logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
                    logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
                    for house_num, info in kp_structured["csl_details"].items():
                        logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
                else:
                    logger.warning("⚠️ No KP cusp sub lord data found for property")

            except Exception as e:
                logger.warning(f"Property purchase evaluation error: {e}")
                result.add_point(
                    "Property purchase indicators could not be conclusively determined."
                )
                # Still try to extract KP data even if finance_engine fails
                try:
                    kp_structured = self._extract_kp_property_structured_direct(planets, houses)
                    result.additional_data["kp_property_analysis"] = kp_structured
                except:
                    pass

            # ---- Timing Layer (UNCHANGED KP LOGIC) ----
            if meta and meta_query_type == QueryType.TIMING:
                try:
                    timing_rules = TIMING_RULES.get("Property Purchase", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    positive_planets = get_positive_planets(planet_scores)

                    if positive_planets:
                        result.add_point(
                            f"KP: Favorable dasha lords for property matters: {', '.join(positive_planets[:4])}."
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.add_point(
                            f"KP: Ruling planets supporting property ownership: {', '.join(ruling_planets[:4])}."
                        )

                    if not positive_planets:
                        result.add_point(
                            "Property timing is sensitive; stronger windows may emerge in later periods."
                        )

                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")
                    result.add_point(
                        "Property timing indicators could not be reliably evaluated."
                    )
        # --------------------------------------------------
        # EXISTING LOGIC: PROPERTY RISKS / CHALLENGES
        # --------------------------------------------------
        elif sub_subdomain == "Property Risks":
            try:
                risk_points = evaluate_house_purchase_strict(
                    planets=planets,
                    houses=houses,
                    d9=kwargs.get("d9")
                )

                risk_lines = [p for p in risk_points if "⚠" in p or "❌" in p]

                if risk_lines:
                    for r in risk_lines:
                        result.add_point(r)
                else:
                    result.add_point(
                        "No strong astrological indicators of severe property-related risk."
                    )
                
                # ✅ NEW: Extract KP CSL data for risk analysis too
                try:
                    kp_structured = self._extract_kp_property_structured_direct(planets, houses)
                    result.additional_data["kp_property_analysis"] = kp_structured
                    
                    if kp_structured.get("has_kp_data"):
                        logger.info(f"✅ KP CSL data extracted for Property Risks:")
                        for house_num, info in kp_structured["csl_details"].items():
                            logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
                except Exception as ke:
                    logger.warning(f"Could not extract KP data for risks: {ke}")

            except Exception as e:
                logger.warning(f"Risk evaluation error: {e}")
                result.add_point(
                    "Property risk assessment could not be conclusively determined."
                )

        # --------------------------------------------------
        # EXISTING LOGIC: REMEDIES (FINANCE DOMAIN)
        # --------------------------------------------------
        elif sub_subdomain == "Finance Remedies":
            result.add_point(
                "Property-related remedies focus on stabilizing finances, reducing delays, "
                "and strengthening planets connected to land and assets."
            )

        # --------------------------------------------------
        # FALLBACK SAFETY
        # --------------------------------------------------
        else:
            result.add_point(
                "This property-related query is handled outside strict astrological evaluation."
            )

        # ═══════════════════════════════════════════════════════
        # STEP 7: Store Enhanced Data for LLM (including timing!)
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data  # ✅ NEW: Pass timing data
        )

        # Add existing points from self.points to result
        if hasattr(self, 'points') and self.points:
            for point in self.points:
                result.add_point(point)

        return result
    

    def _extract_kp_property_structured_direct(self, planets: Dict, houses: List) -> Dict:
        """
        Extract structured KP property data DIRECTLY from cusp sub lords.
        
        This is independent of finance_engine text output - extracts raw cusp data
        and creates structured format for deterministic LLM consumption.
        
        Returns structured dict with:
        - csl_details: Dict keyed by house number
        - overall_verdict: Assessment of property prospects
        - key_findings: List of important discoveries
        """
        from app.core.astro_constants import normalize_planet_name
        
        kp_data = {
            "csl_details": {},
            "overall_verdict": "UNKNOWN",
            "key_findings": [],
            "has_kp_data": False
        }
        
        # Property-relevant houses
        property_houses = [4, 11, 2, 12]
        house_meanings = {
            4: "Property/Land",
            11: "Gains/Fulfillment",
            2: "Wealth/Assets",
            12: "Expenses/Losses"
        }
        
        # Extract CSL for each property house
        for house_num in property_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            
            if not house_data:
                continue
            
            # Get cusp sub lord
            csl_raw = house_data.get("cusp_sub_lord", "")
            if not csl_raw:
                continue
            
            csl = normalize_planet_name(csl_raw) or csl_raw
            
            if not csl:
                continue
            
            kp_data["has_kp_data"] = True
            
            # Get cusp sign
            cusp_sign = (
                house_data.get("start_rasi", "") or
                house_data.get("rasi", "") or
                house_data.get("sign", "")
            )
            
            # Determine if CSL is benefic or malefic
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            
            is_benefic = csl in benefics
            is_malefic = csl in malefics
            
            # Basic verdict for this cusp
            verdict = "NEUTRAL"
            interpretation = ""
            
            if house_num == 4:  # Property house
                if is_benefic:
                    verdict = "PROMISED"
                    interpretation = f"{csl} (benefic) as 4th CSL strongly indicates property acquisition"
                elif is_malefic:
                    verdict = "DELAYED"
                    interpretation = f"{csl} (malefic) as 4th CSL may delay property matters"
                else:
                    interpretation = f"{csl} as 4th CSL gives mixed property results"
            
            elif house_num == 11:  # Gains/fulfillment house
                if is_benefic:
                    verdict = "EXCELLENT"
                    interpretation = f"{csl} (benefic) as 11th CSL ensures fulfillment of property desires"
                elif is_malefic:
                    verdict = "CHALLENGING"
                    interpretation = f"{csl} (malefic) as 11th CSL creates obstacles in gains"
                else:
                    interpretation = f"{csl} as 11th CSL shows moderate fulfillment"
            
            elif house_num == 2:  # Wealth house
                if is_benefic:
                    verdict = "FAVORABLE"
                    interpretation = f"{csl} (benefic) as 2nd CSL supports financial capacity for property"
                elif is_malefic:
                    verdict = "WEAK"
                    interpretation = f"{csl} (malefic) as 2nd CSL weakens financial resources"
                else:
                    interpretation = f"{csl} as 2nd CSL gives moderate financial support"
            
            elif house_num == 12:  # Expense house
                if is_benefic:
                    verdict = "CONTROLLED"
                    interpretation = f"{csl} (benefic) as 12th CSL helps control property expenses"
                elif is_malefic:
                    verdict = "EXCESSIVE"
                    interpretation = f"{csl} (malefic) as 12th CSL increases property-related expenses"
                else:
                    interpretation = f"{csl} as 12th CSL shows normal expense patterns"
            
            # Store structured data for this cusp
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings[house_num],
                "csl": csl,
                "cusp_sign": cusp_sign,
                "is_benefic": is_benefic,
                "is_malefic": is_malefic,
                "verdict": verdict,
                "interpretation": interpretation
            }
            
            # Add to key findings
            kp_data["key_findings"].append(
                f"House {house_num} ({house_meanings[house_num]}): CSL {csl} - {verdict}"
            )
        
        # Determine overall verdict
        if kp_data["csl_details"]:
            # Check critical houses: 4 (property) and 11 (fulfillment)
            h4_verdict = kp_data["csl_details"].get(4, {}).get("verdict", "UNKNOWN")
            h11_verdict = kp_data["csl_details"].get(11, {}).get("verdict", "UNKNOWN")
            
            if h4_verdict == "PROMISED" and h11_verdict in ["FAVORABLE", "EXCELLENT"]:
                kp_data["overall_verdict"] = "STRONG_PROMISE"
                kp_data["key_findings"].insert(0, "KP shows strong promise for property acquisition")
            elif h4_verdict == "DELAYED" and h11_verdict in ["CHALLENGING", "WEAK"]:
                kp_data["overall_verdict"] = "BLOCKED"
                kp_data["key_findings"].insert(0, "KP shows obstacles and delays in property matters")
            elif h4_verdict == "DELAYED" and h11_verdict in ["FAVORABLE", "EXCELLENT"]:
                kp_data["overall_verdict"] = "MODERATE_WITH_DELAYS"
                kp_data["key_findings"].insert(0, "KP shows property promise but with delays")
            elif h4_verdict == "PROMISED" and h11_verdict in ["CHALLENGING", "WEAK"]:
                kp_data["overall_verdict"] = "MODERATE_WITH_OBSTACLES"
                kp_data["key_findings"].insert(0, "KP shows property promise but challenges in fulfillment")
            else:
                kp_data["overall_verdict"] = "MODERATE"
                kp_data["key_findings"].insert(0, "KP shows mixed property indicators")
        
        return kp_data
    
    def _is_kp_point(self, point: str) -> bool:
        """Check if a point is KP-related"""
        kp_keywords = [
            'cusp', 'csl', 'sub-lord', 'sub lord',
            'signif', 'connects to', 'ruling planet',
            'kp', 'house purchase', 'property'
        ]
        point_lower = point.lower()
        return any(kw in point_lower for kw in kp_keywords)

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - FIXED VERSION!
    # ═══════════════════════════════════════════════════════════════
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
                if not isinstance(first, dict):
                    logger.info(f"🔍 First window attributes: {vars(first) if hasattr(first, '__dict__') else 'N/A'}")
            
            # ✅ FIX: Sort by final_score using get_attr helper
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            # ✅ NEW: Check if we got any windows at all
            if not sorted_windows or len(sorted_windows) == 0:
                logger.warning(f"⚠️ NO FAVORABLE TIMING WINDOWS FOUND")
                logger.warning(f"   KP timing engine provided 0 windows")
                return {
                'has_timing': False,
                'no_windows_found': True,  # ← NEW FLAG
                'best_window': None,
                'nearest_window': None,
                'all_favorable': [],
                'reason': 'KP timing engine found no favorable periods'
            }

            
            # Best window: highest score (convert to dict for JSON serialization)
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
                # If no windows with score >= 50, use the best window as nearest too
                nearest_window = best_window
                logger.info("🔍 No windows with score >= 50, using best window as nearest")
            
            # Top 5 favorable windows (convert all to dicts)
            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]
            
            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True,
                'no_windows_found': False
            }
            
            # Log success
            logger.info(f"✅ Timing extraction SUCCESSFUL:")
            if best_window:
                logger.info(f"   Best: {best_window.get('dasha', 'N/A')} - Score: {best_window.get('final_score', 0)}")
            if nearest_window:
                logger.info(f"   Nearest: {nearest_window.get('dasha', 'N/A')} - Score: {nearest_window.get('final_score', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
            'has_timing': False,
            'no_windows_found': False,  # Error is different from no windows
            'best_window': None,
            'nearest_window': None,
            'all_favorable': []

            }

    # ═══════════════════════════════════════════════════════════════
    # PROPERTY TIMING KP SIGNIFICATOR PROOF
    # ═══════════════════════════════════════════════════════════════
    
    def _generate_property_timing_proof(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        timing_windows_data: Dict
    ) -> Dict:
        """
        Generate KP significator proof for property timing recommendations.
        
        For property purchase in KP astrology:
        - Houses 4 (property/land), 11 (gains/fulfillment), 2 (wealth) are PROMISE houses
        - Houses 6 (loans/debts), 8 (obstacles), 12 (losses/expenses) are OBSTACLE houses
        - Mars involvement is important (property/land karaka in some traditions)
        - Saturn involvement indicates land and real estate
        
        Shows which dasha lords signify these houses and HOW (Star Lord, Sub Lord, etc.)
        
        Returns structured data for LLM to explain timing recommendations properly.
        """
        PROMISE_HOUSES = {4, 11, 2}  # Property favorable houses
        SUPPORT_HOUSES = {9}  # Fortune/luck support
        OBSTACLE_HOUSES = {6, 8, 12}  # Obstacles to property
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Build House Occupancy Map
        # ═══════════════════════════════════════════════════════════════
        house_occupants = defaultdict(list)
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            house = pdata.get("house")
            if house:
                house_occupants[house].append(pname)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Build House Lords Map
        # ═══════════════════════════════════════════════════════════════
        house_lords = {}
        for h in houses:
            house_num = h.get("house")
            lord = h.get("rashi_lord") or h.get("sign_lord") or h.get("cusp_sub_lord")
            if house_num and lord:
                house_lords[house_num] = normalize_planet_name(lord)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Build Planet Significator Table
        # ═══════════════════════════════════════════════════════════════
        # KP Signification Levels (OCSS):
        # O = Occupant of house
        # L = Lord (rules the house)
        # S = Star Lord (Nakshatra Lord)
        
        planet_significators = {}
        
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            
            sigs = {
                "occupant_of": [],
                "star_lord_of_occupant": [],
                "own_house_lord": [],
                "sub_lord_of": [],
                "total_promise_signification": 0,
                "total_obstacle_signification": 0,
                "mars_connection": False,
                "saturn_connection": False
            }
            
            # Level 1: Direct Occupation
            planet_house = pdata.get("house")
            if planet_house:
                sigs["occupant_of"].append(planet_house)
                if planet_house in PROMISE_HOUSES:
                    sigs["total_promise_signification"] += 4
                if planet_house in SUPPORT_HOUSES:
                    sigs["total_promise_signification"] += 2
                if planet_house in OBSTACLE_HOUSES:
                    sigs["total_obstacle_signification"] += 4
            
            # Level 2: House Lordship
            for h_num, lord in house_lords.items():
                if lord == pname:
                    sigs["own_house_lord"].append(h_num)
                    if h_num in PROMISE_HOUSES:
                        sigs["total_promise_signification"] += 2
                    if h_num in SUPPORT_HOUSES:
                        sigs["total_promise_signification"] += 1
                    if h_num in OBSTACLE_HOUSES:
                        sigs["total_obstacle_signification"] += 2
            
            # Level 3: Star Lord signification
            nak_lord = normalize_planet_name(pdata.get("nakshatra_lord") or pdata.get("nak_lord"))
            if nak_lord:
                sigs["nakshatra_lord"] = nak_lord
                # Check what houses the nakshatra lord signifies
                nak_lord_data = planets.get(nak_lord, {})
                nak_lord_house = nak_lord_data.get("house")
                if nak_lord_house:
                    sigs["star_lord_of_occupant"].append(nak_lord_house)
                    if nak_lord_house in PROMISE_HOUSES:
                        sigs["total_promise_signification"] += 3
                    if nak_lord_house in SUPPORT_HOUSES:
                        sigs["total_promise_signification"] += 1
                    if nak_lord_house in OBSTACLE_HOUSES:
                        sigs["total_obstacle_signification"] += 3
            
            # Check Mars connection (property/land karaka)
            if pname == "Mars":
                sigs["mars_connection"] = True
            elif sigs.get("nakshatra_lord") == "Mars":
                sigs["mars_connection"] = True
            
            # Check Saturn connection (real estate/land karaka)
            if pname == "Saturn":
                sigs["saturn_connection"] = True
            elif sigs.get("nakshatra_lord") == "Saturn":
                sigs["saturn_connection"] = True
            
            planet_significators[pname] = sigs
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Analyze Timing Windows with Significator Proof
        # ═══════════════════════════════════════════════════════════════
        timing_proofs = []
        
        if timing_windows_data and timing_windows_data.get("all_favorable"):
            for window in timing_windows_data.get("all_favorable", [])[:5]:  # Top 5 windows
                dasha_str = window.get("dasha", "")
                
                # Parse dasha lords (format: "Venus-Jupiter-Moon" or "Venus / Jupiter")
                dasha_parts = dasha_str.replace(" / ", "-").replace("/", "-").split("-")
                
                proof = {
                    "period": f"{window.get('start', 'N/A')} to {window.get('end', 'N/A')}",
                    "dasha": dasha_str,
                    "score": window.get("final_score", 0),
                    "dasha_lords": [],
                    "total_4_11_2_activation": 0,
                    "total_obstacle_activation": 0,
                    "mars_involved": False,
                    "saturn_involved": False,
                    "house_linkage": [],
                    "promise_strength": "WEAK"  # STRONG/MODERATE/WEAK
                }
                
                for lord_name in dasha_parts:
                    lord_name = normalize_planet_name(lord_name.strip())
                    if not lord_name:
                        continue
                    
                    lord_sigs = planet_significators.get(lord_name, {})
                    
                    lord_proof = {
                        "planet": lord_name,
                        "signifies_promise_houses": [],
                        "signifies_obstacle_houses": [],
                        "how": []
                    }
                    
                    # Add occupation signification for promise houses
                    for h in lord_sigs.get("occupant_of", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Occupies house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                    
                    # Add lordship signification
                    for h in lord_sigs.get("own_house_lord", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Lord of house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                    
                    # Add star lord signification
                    for h in lord_sigs.get("star_lord_of_occupant", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Star lord signifies house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                    
                    proof["total_4_11_2_activation"] += lord_sigs.get("total_promise_signification", 0)
                    proof["total_obstacle_activation"] += lord_sigs.get("total_obstacle_signification", 0)
                    
                    if lord_sigs.get("mars_connection"):
                        proof["mars_involved"] = True
                    
                    if lord_sigs.get("saturn_connection"):
                        proof["saturn_involved"] = True
                    
                    if lord_name == "Mars":
                        proof["mars_involved"] = True
                    
                    if lord_name == "Saturn":
                        proof["saturn_involved"] = True
                    
                    proof["dasha_lords"].append(lord_proof)
                
                # Calculate promise strength
                promise_score = proof["total_4_11_2_activation"]
                obstacle_score = proof["total_obstacle_activation"]
                
                if promise_score >= 8 and promise_score > obstacle_score * 2:
                    proof["promise_strength"] = "STRONG"
                elif promise_score >= 5 and promise_score > obstacle_score:
                    proof["promise_strength"] = "MODERATE"
                else:
                    proof["promise_strength"] = "WEAK"
                
                # Generate house linkage explanation
                houses_activated = set()
                for lord in proof["dasha_lords"]:
                    houses_activated.update(lord["signifies_promise_houses"])
                
                if 4 in houses_activated:
                    proof["house_linkage"].append("4th house (property/land) activated")
                if 11 in houses_activated:
                    proof["house_linkage"].append("11th house (gains/fulfillment) activated")
                if 2 in houses_activated:
                    proof["house_linkage"].append("2nd house (wealth/assets) activated")
                if 9 in houses_activated:
                    proof["house_linkage"].append("9th house (fortune) supporting")
                
                timing_proofs.append(proof)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Build Significator Summary Table
        # ═══════════════════════════════════════════════════════════════
        significator_table = []
        
        for pname in ["Mars", "Saturn", "Jupiter", "Venus", "Moon", "Mercury", "Sun", "Rahu", "Ketu"]:
            if pname not in planet_significators:
                continue
            sigs = planet_significators[pname]
            
            promise_houses = []
            obstacle_houses = []
            
            if sigs.get("occupant_of"):
                for h in sigs["occupant_of"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(O)")  # O = Occupant
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(O)")
                        
            if sigs.get("own_house_lord"):
                for h in sigs["own_house_lord"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(L)")  # L = Lord
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(L)")
                        
            if sigs.get("star_lord_of_occupant"):
                for h in sigs["star_lord_of_occupant"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(S)")  # S = Star Lord
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(S)")
            
            net_score = sigs.get("total_promise_signification", 0) - sigs.get("total_obstacle_signification", 0)
            
            if promise_houses or pname in ["Mars", "Saturn"]:
                significator_table.append({
                    "planet": pname,
                    "signifies_4_11_2": promise_houses if promise_houses else ["None"],
                    "signifies_6_8_12": obstacle_houses if obstacle_houses else ["None"],
                    "promise_score": sigs.get("total_promise_signification", 0),
                    "obstacle_score": sigs.get("total_obstacle_signification", 0),
                    "net_score": net_score,
                    "is_property_karaka": pname == "Mars",
                    "is_land_karaka": pname == "Saturn"
                })
        
        # Sort by net score (promise - obstacle)
        significator_table.sort(key=lambda x: x["net_score"], reverse=True)
        
        return {
            "significator_table": significator_table,
            "timing_proofs": timing_proofs,
            "house_occupants": dict(house_occupants),
            "house_lords": house_lords,
            "legend": {
                "O": "Occupant (planet sits in this house) - strongest",
                "L": "Lord (planet rules this house sign)",
                "S": "Star Lord (planet's nakshatra lord signifies this house)"
            },
            "promise_houses_meaning": {
                4: "Property, land, home, immovable assets",
                11: "Gains, fulfillment of desires, success",
                2: "Wealth, assets, financial capacity"
            },
            "obstacle_houses_meaning": {
                6: "Loans, debts, financial strain",
                8: "Obstacles, delays, hidden issues",
                12: "Losses, expenses, drainage of resources"
            }
        }

    # ═══════════════════════════════════════════════════════════════
    # ENHANCED HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

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
        """
        Extract house lord information for relevant houses only.
        """
        house_lords_info = {}
        
        for h in houses:
            house_num = h.get("house")
            
            if house_num not in relevant_houses:
                continue
            
            # Get lord name - try multiple possible keys
            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
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
                logger.warning(f"No lord found for house {house_num}")
                continue
            else:
                logger.debug(f"{normalized_lord} is House Lord for house {house_num}")
            
            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"No data found for lord {normalized_lord}")
                continue
                
            lord_house = lord_data.get("house")
            lord_sign = lord_data.get("sign", "")
            
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
            
            # Get lord dignity if house lords analyzer available
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
                            normalized_lord, lord_data, dignity)
                        
                        logger.debug(f"Determined Dignity for {normalized_lord}")
                    else:
                        logger.debug(f"Could not determine dignity for {normalized_lord}")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")
            
            priority = "primary" if house_num in primary_houses else "secondary"
            
            planets_in_house = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]
            
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

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for property context."""
        meanings = {
            2: "Wealth/Assets",
            4: "Property/Land",
            6: "Loans/Debts",
            8: "Sudden Events/Obstacles",
            9: "Fortune/Luck",
            11: "Gains/Fulfillment",
            12: "Expenses/Losses"
        }
        return meanings.get(house_num, "General")

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None  # ✅ NEW: Timing data parameter
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "finance_and_property"
        
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
            logger.info(f"   Key: {domain_prefix}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
            if timing_windows_data.get('best_window'):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE (data: {bool(timing_windows_data)})")

    # --------------------------------------------------
    # QUESTIONS — EXACTLY AS PER YOUR TABLE
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="FIN_BHL_1",
                question=(
                    "Will I be able to purchase or build a house or land and when would "
                    "be the most auspicious time for each?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Prospects of Property"
            ),
            Question(
                id="FIN_BHL_2",
                question=(
                    "Are there any risks or challenges I should be aware of in these property endeavors?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Property Risks"
            ),
            Question(
                id="FIN_BHL_3",
                question=(
                    "What Vastu-based layout, direction, or guidance should I consider for my property?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Vastu Guidance for Property"
            )
        ]
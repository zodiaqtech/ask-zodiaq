"""
Facing Financial Problems Evaluator - Enhanced Version v3.0 (FIXED)

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
✅ KP finance engine integration (preserved)
"""

from typing import Dict, List, Optional,Set
import logging
from unittest import result
from app.core.astro_constants import normalize_planet_name, get_signified_houses



from app.domains.base import (
    BaseEvaluator,
    EvaluationResult,
    Question,
    QueryMeta,
    QueryType,
    EventPolarity,
    InterpretationGoal
)


# Import finance evaluation functions
from app.domains.finance.finance_engine import (
    evaluate_finance,
    evaluate_borrowing_A2_strict
)
from app.domains.excel_structure_config import get_houses_for_question
from app.domains.excel_structure_config import get_houses_for_question



from app.services.timing_engine import (
    TIMING_RULES,
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets
)



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
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FacingFinancialProblemsEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Finance → Facing Financial Problems
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Dual data source support (KP + Vedic)
    - Timing windows extraction and formatting (FIXED)
    """
    
    domain = "Finance"
    subtopic = "Facing Financial Problems"
    
    # Finance-specific houses
    FINANCE_HOUSES = {2, 6, 8, 11, 12}
    
    # House meanings for context
    HOUSE_MEANINGS = {
        2: "Wealth/Income",
        6: "Loans/Debts",
        8: "Sudden Loss",
        11: "Gains/Repayment",
        12: "Expenses/Drains"
    }
    
    # --------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------
    def evaluate(
        self,
        planets: Dict[str, Dict],                      # KP planets
        houses: List[Dict],                            # KP houses
        vedic_planets: Optional[Dict[str, Dict]] = None,  # Vedic planets
        vedic_houses: Optional[List[Dict]] = None,        # Vedic houses
        **kwargs
    ) -> EvaluationResult:

        self.reset()
        result = EvaluationResult()

        # ═══════════════════════════════════════════════════════
        # STEP 0: Choose Data Source for House Lord Analysis
        # ═══════════════════════════════════════════════════════
        analysis_planets = vedic_planets 
        analysis_houses = vedic_houses 

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
            all_relevant_houses = self.FINANCE_HOUSES
            primary_houses = {2, 6, 11}
            secondary_houses = {8, 12}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "")

        # Handle both dict and QueryMeta object
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("FACING FINANCIAL PROBLEMS EVALUATOR (ENHANCED v3.0 - FIXED)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects (on Vedic/analysis data)
        # ═══════════════════════════════════════════════════════
        detect_aspects(analysis_planets)
        detect_aspects(planets)
        
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract House Lords Data (using Vedic/analysis data)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )


        
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")


        # ═══════════════════════════════════════════════════════════
        # STEP 3.5: Extract Complete KP Significator Table
        # ═══════════════════════════════════════════════════════════
        kp_significator_table = self._extract_kp_significators_complete(
            planets,
            houses,
            all_relevant_houses
        )

        logger.info(f"✅ KP Significator table extracted for {len(kp_significator_table['planets'])} planets")

        # Store in additional_data for LLM
        result.additional_data["kp_significator_table"] = kp_significator_table


        # ═══════════════════════════════════════════════════════════
        # STEP 3.6: Extract Lagna Lord Analysis
        # ═══════════════════════════════════════════════════════════
        lagna_lord_analysis = self._extract_lagna_lord_analysis(
            analysis_houses,
            analysis_planets
        )

          
        if lagna_lord_analysis.get("lagna_lord"):
            logger.info(
            f"✅ Lagna: {lagna_lord_analysis['lagna_sign']} "
            f"(Lord: {lagna_lord_analysis['lagna_lord']}, "
            f"Verdict: {lagna_lord_analysis['verdict']})"
        )
        
        # Store in additional_data for LLM
        result.additional_data["lagna_lord_analysis"] = lagna_lord_analysis



        # ═══════════════════════════════════════════════════════
        # STEP 4: Extract Aspects on Houses (using analysis data)
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
            
            # Fallback: try "Loan Repayment Timing" key if sub_subdomain doesn't match
            if not timing_windows_list and "Loan Repayment Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Loan Repayment Timing"]
                logger.info(f"🔍 DEBUG: Using 'Loan Repayment Timing' fallback key, found {len(timing_windows_list)} windows")
            
            # Another fallback: try "Loan Default Risk"
            if not timing_windows_list and "Loan Default Risk" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Loan Default Risk"]
                logger.info(f"🔍 DEBUG: Using 'Loan Default Risk' fallback key, found {len(timing_windows_list)} windows")
        else:
            # Treat as list directly
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")
        
        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = self._extract_timing_windows(timing_windows_list)
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            logger.info(f"❌ No timing windows available for '{sub_subdomain}'")

        # ═══════════════════════════════════════════════════════
        # STEP 6: Add House Analysis Points (if applicable)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Reason for Financial Challenges", "Loan Default Risk", "Risk of Financial Dispute"}:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # Safety check
        if not sub_subdomain:
            logger.warning("⚠️ sub_subdomain is EMPTY!")
            result.add_point("Financial analysis requires question context.")
            self._store_data_for_llm(
                result, house_config, house_lords_info, house_aspects_info, 
                primary_houses, secondary_houses, timing_windows_data
            )
            return result

        # ════════════════════════════════════════════════════════════════
        # SPECIFIC PROBLEM ANALYSIS (Use KP data for KP logic)
        # ════════════════════════════════════════════════════════════════
        
        if sub_subdomain == "Reason for Financial Challenges":
            self._evaluate_financial_challenges(planets, houses, result)
            
        elif sub_subdomain == "Loan Default Risk":
            self._evaluate_loan_risk(planets, houses, result, meta_query_type)
            
        elif sub_subdomain == "Risk of Financial Dispute":
            self._evaluate_dispute_risk(planets, houses, result)
            
        elif sub_subdomain == "Finance Remedies":
            self._evaluate_remedies(planets, houses, result)
            
        else:
            logger.warning(f"Unknown sub_subdomain: {sub_subdomain}")
            result.add_point("General financial analysis provided.")

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
            timing_windows_data,  # ✅ NEW: Pass timing data
            lagna_lord_analysis=lagna_lord_analysis,  # ✅ NEW: Pass lagna lord
            kp_significator_table=kp_significator_table  # ✅ NEW: Pass significator table
        )
        
        logger.info("=" * 80)
        logger.info(f"EVALUATION COMPLETE: {len(result.technical_points)} points")
        logger.info("=" * 80)
        
        return result

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
                
                # Include additional fields if they exist (for detailed scoring)
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
                'has_timing': True
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
            return {}


    def _extract_kp_significators_complete(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        finance_houses: set
    ) -> Dict:
        """
        Extract complete KP significator table for all planets.
        
        Returns structured data showing:
        - Each planet's sub/star/occupy/own significations
        - House linkage chains (e.g., 2-6-11 for repayment)
        - Event promise vs denial logic
        """
        
        significator_table = {
            "planets": {},
            "house_linkages": {},
            "event_analysis": {}
        }
        
        # Define house groups for linkage analysis
        WEALTH_HOUSES = {2, 10, 11}  # Income & gains
        DEBT_HOUSES = {6, 12}  # Loans & expenses
        LOSS_HOUSES = {6, 8, 12}  # Loss indicators
        REPAYMENT_CHAIN = {2, 6, 11}  # Repayment capacity chain
        DEFAULT_CHAIN = {6, 8, 12}  # Default risk chain
        
        # Extract significators for each planet
        for planet_name, planet_data in planets.items():
            if planet_name in ["Lagna", "Asc"]:
                continue
                
            planet_significations = {
                "sub": set(),
                "star": set(),
                "occupy": set(),
                "own": set(),
                "complete_chain": []
            }
            
            # 1. SUB (nakshatra sub-lord) - HIGHEST PRIORITY
            nakshatra = planet_data.get("nakshatra", {})
            if isinstance(nakshatra, dict):
                sublord = nakshatra.get("sublord", "") or nakshatra.get("sub_lord", "")
                if sublord:
                    sublord = normalize_planet_name(sublord) or sublord
                    if sublord in planets:
                        # Get houses sublord signifies
                        sub_planet = planets[sublord]
                        
                        # Sublord's occupation
                        sub_house = sub_planet.get("house")
                        if sub_house:
                            planet_significations["sub"].add(sub_house)
                        
                        # Sublord's ownership
                        sub_rules = sub_planet.get("rules", [])
                        if isinstance(sub_rules, list):
                            planet_significations["sub"].update(sub_rules)
            
            # 2. STAR (nakshatra lord) - SECOND PRIORITY
            if isinstance(nakshatra, dict):
                star_lord = nakshatra.get("lord", "") or nakshatra.get("star_lord", "")
                if star_lord:
                    star_lord = normalize_planet_name(star_lord) or star_lord
                    if star_lord in planets:
                        star_planet = planets[star_lord]
                        
                        # Star lord's occupation
                        star_house = star_planet.get("house")
                        if star_house:
                            planet_significations["star"].add(star_house)
                        
                        # Star lord's ownership
                        star_rules = star_planet.get("rules", [])
                        if isinstance(star_rules, list):
                            planet_significations["star"].update(star_rules)
            
            # 3. OCCUPY (placement) - THIRD PRIORITY
            occupy_house = planet_data.get("house")
            if occupy_house:
                planet_significations["occupy"].add(occupy_house)
            
            # 4. OWN (lordship) - FOURTH PRIORITY
            owns = planet_data.get("rules", [])
            if isinstance(owns, list):
                planet_significations["own"].update(owns)
            
            # Build complete signification chain (SUB > STAR > OCCUPY > OWN)
            all_significations = set()
            chain_parts = []
            
            if planet_significations["sub"]:
                all_significations.update(planet_significations["sub"])
                chain_parts.append(f"Sub→{sorted(planet_significations['sub'])}")
            
            if planet_significations["star"]:
                all_significations.update(planet_significations["star"])
                chain_parts.append(f"Star→{sorted(planet_significations['star'])}")
            
            if planet_significations["occupy"]:
                all_significations.update(planet_significations["occupy"])
                chain_parts.append(f"Occupy→{sorted(planet_significations['occupy'])}")
            
            if planet_significations["own"]:
                all_significations.update(planet_significations["own"])
                chain_parts.append(f"Own→{sorted(planet_significations['own'])}")
            
            planet_significations["complete_chain"] = chain_parts
            planet_significations["all_houses"] = sorted(all_significations)
            
            # Analyze finance-relevant significations
            planet_significations["wealth_connection"] = len(WEALTH_HOUSES & all_significations)
            planet_significations["debt_connection"] = len(DEBT_HOUSES & all_significations)
            planet_significations["loss_connection"] = len(LOSS_HOUSES & all_significations)
            planet_significations["repayment_chain_strength"] = len(REPAYMENT_CHAIN & all_significations)
            planet_significations["default_chain_strength"] = len(DEFAULT_CHAIN & all_significations)
            
            significator_table["planets"][planet_name] = planet_significations
        
        # Analyze house linkages for key events
        significator_table["house_linkages"] = {
            "repayment_chain": {
                "houses": sorted(REPAYMENT_CHAIN),
                "logic": "2 (income) + 6 (debt) + 11 (gains) → shows repayment capacity",
                "planets_supporting": [],
                "planets_blocking": []
            },
            "default_chain": {
                "houses": sorted(DEFAULT_CHAIN),
                "logic": "6 (debt) + 8 (loss) + 12 (drains) → shows default risk",
                "planets_supporting": [],
                "planets_blocking": []
            },
            "wealth_accumulation": {
                "houses": sorted(WEALTH_HOUSES),
                "logic": "2 (savings) + 10 (career) + 11 (gains) → shows income strength",
                "planets_supporting": [],
                "planets_blocking": []
            }
        }
        
        # Identify planets supporting/blocking each chain
        for planet_name, planet_sigs in significator_table["planets"].items():
            all_houses = set(planet_sigs["all_houses"])
            
            # Repayment chain
            if all_houses & REPAYMENT_CHAIN:
                if planet_sigs["repayment_chain_strength"] >= 2:
                    significator_table["house_linkages"]["repayment_chain"]["planets_supporting"].append(
                        f"{planet_name} ({planet_sigs['repayment_chain_strength']}/3 houses)"
                    )
            
            # Default chain
            if all_houses & DEFAULT_CHAIN:
                if planet_sigs["default_chain_strength"] >= 2:
                    significator_table["house_linkages"]["default_chain"]["planets_supporting"].append(
                        f"{planet_name} ({planet_sigs['default_chain_strength']}/3 houses)"
                    )
            
            # Wealth accumulation
            if all_houses & WEALTH_HOUSES:
                if planet_sigs["wealth_connection"] >= 2:
                    significator_table["house_linkages"]["wealth_accumulation"]["planets_supporting"].append(
                        f"{planet_name} ({planet_sigs['wealth_connection']}/3 houses)"
                    )
        
        return significator_table


    def _extract_lagna_lord_analysis(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Dict:
        """
        Extract Lagna (Ascendant) lord and analyze its influence on financial matters.
        
        Lagna lord represents the native's overall capacity and strength.
        Its placement, dignity, and connections to finance houses are crucial.
        """
        
        lagna_analysis = {
            "lagna_sign": "",
            "lagna_lord": "",
            "lagna_lord_house": None,
            "lagna_lord_sign": "",
            "lagna_lord_dignity": "",
            "finance_house_connections": [],
            "strength_score": 0,
            "financial_impact": "",
            "verdict": "NEUTRAL"
        }
        
        # Find 1st house to get Lagna sign
        house_1 = next((h for h in houses if h.get("house") == 1), None)
        if not house_1:
            return lagna_analysis
        
        lagna_sign = (
            house_1.get("start_rasi", "") or
            house_1.get("rasi", "") or
            house_1.get("sign", "")
        )
        
        if not lagna_sign:
            return lagna_analysis
        
        lagna_analysis["lagna_sign"] = lagna_sign
        
        # Find Lagna lord based on sign lordship
        SIGN_LORDS = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        
        lagna_lord = SIGN_LORDS.get(lagna_sign, "")
        if not lagna_lord:
            return lagna_analysis
        
        lagna_analysis["lagna_lord"] = lagna_lord
        
        # Get Lagna lord's planetary data
        lagna_lord_data = planets.get(lagna_lord, {})
        if not lagna_lord_data:
            return lagna_analysis
        
        # Extract placement and dignity
        lagna_lord_house = lagna_lord_data.get("house")
        lagna_lord_sign = lagna_lord_data.get("sign", "")
        dignity = lagna_lord_data.get("dignity", "")
        
        lagna_analysis["lagna_lord_house"] = lagna_lord_house
        lagna_analysis["lagna_lord_sign"] = lagna_lord_sign
        lagna_analysis["lagna_lord_dignity"] = dignity
        
        # Analyze connections to finance houses (2, 6, 8, 11, 12)
        FINANCE_HOUSES = {2, 6, 8, 11, 12}
        
        # Check placement
        if lagna_lord_house in FINANCE_HOUSES:
            house_meaning = {
                2: "Wealth", 6: "Debt", 8: "Loss", 11: "Gains", 12: "Expenses"
            }
            lagna_analysis["finance_house_connections"].append(
                f"Placed in {lagna_lord_house}th ({house_meaning[lagna_lord_house]})"
            )
        
        # Check ownership
        rules = lagna_lord_data.get("rules", [])
        if isinstance(rules, list):
            for house in rules:
                if house in FINANCE_HOUSES:
                    house_meaning = {
                        2: "Wealth", 6: "Debt", 8: "Loss", 11: "Gains", 12: "Expenses"
                    }
                    lagna_analysis["finance_house_connections"].append(
                        f"Rules {house}th ({house_meaning[house]})"
                    )
        
        # Calculate strength score
        strength = 0
        
        # Dignity adds/subtracts strength
        if dignity == "Exalted":
            strength += 3
        elif dignity == "Own Sign":
            strength += 2
        elif dignity == "Friend":
            strength += 1
        elif dignity == "Debilitated":
            strength -= 3
        elif dignity == "Enemy":
            strength -= 1
        
        # Favorable placements add strength
        if lagna_lord_house in {1, 2, 5, 9, 10, 11}:  # Good houses
            strength += 1
        elif lagna_lord_house in {6, 8, 12}:  # Challenging houses
            strength -= 1
        
        lagna_analysis["strength_score"] = strength
        
        # Determine financial impact based on connections
        if lagna_lord_house == 2 or 2 in rules:
            lagna_analysis["financial_impact"] = "Strong focus on wealth accumulation"
            lagna_analysis["verdict"] = "FAVORABLE"
        elif lagna_lord_house == 11 or 11 in rules:
            lagna_analysis["financial_impact"] = "Strong gains and fulfillment capacity"
            lagna_analysis["verdict"] = "EXCELLENT"
        elif lagna_lord_house == 6:
            lagna_analysis["financial_impact"] = "Debt and obstacle focus - challenges likely"
            lagna_analysis["verdict"] = "CHALLENGING"
        elif lagna_lord_house == 8:
            lagna_analysis["financial_impact"] = "Sudden changes and hidden issues in finances"
            lagna_analysis["verdict"] = "UNPREDICTABLE"
        elif lagna_lord_house == 12:
            lagna_analysis["financial_impact"] = "Expenses and losses drain resources"
            lagna_analysis["verdict"] = "DIFFICULT"
        else:
            lagna_analysis["financial_impact"] = "Moderate financial capacity"
            lagna_analysis["verdict"] = "NEUTRAL"
        
        # Adjust verdict based on strength
        if strength >= 3:
            if lagna_analysis["verdict"] in ["NEUTRAL", "FAVORABLE"]:
                lagna_analysis["verdict"] = "EXCELLENT"
        elif strength <= -2:
            if lagna_analysis["verdict"] not in ["DIFFICULT"]:
                lagna_analysis["verdict"] = "CHALLENGING"
        
        return lagna_analysis

    def _extract_kp_finance_structured(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        finance_houses: set
    ) -> Dict:
        """
        Extract KP analysis with PROPER CHAIN LOGIC:
        CSL → Star Lord → Significations → House Linkages → Event Promise/Denial
        
        Now uses get_signified_houses() from astro_constants for complete KP logic.
        """
        from app.core.astro_constants import get_signified_houses
        
        kp_data = {
            "has_kp_data": False,
            "methodology": "CSL → Star Lord → Significations → House Linkages → Result",
            "csl_details": {},
            "house_linkages": {},
            "event_promises": {},
            "overall_verdict": "UNKNOWN",
            "key_findings": []
        }
        
        house_meanings = {
            2: "Wealth/Income",
            6: "Loans/Debts",
            8: "Sudden Loss/Lender",
            11: "Gains/Repayment",
            12: "Expenses/Drains"
        }
        
        # Extract CSL for each finance house
        for house_num in sorted(finance_houses):
            # ✅ Get house data from houses list
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            
            if not house_data:
                logger.warning(f"⚠️ House {house_num} not found in houses list")
                continue
            
            # ✅ Get cusp sub lord directly from house dict
            csl_raw = house_data.get("cusp_sub_lord", "")
            if not csl_raw:
                logger.warning(f"⚠️ No cusp_sub_lord for house {house_num}")
                continue
            
            csl = normalize_planet_name(csl_raw) or csl_raw
            
            if not csl or csl not in planets:
                logger.warning(f"⚠️ CSL {csl} for house {house_num} not in planets")
                continue
            
            kp_data["has_kp_data"] = True
            
            # ✅ Get nakshatra name and star lord from house dict
            nakshatra_name = house_data.get("start_nakshatra", "")
            star_lord_raw = house_data.get("start_nakshatra_lord", "")
            star_lord = normalize_planet_name(star_lord_raw) if star_lord_raw else None
            
            logger.info(
                f"✅ House {house_num}: CSL {csl} → {nakshatra_name} "
                f"(Star Lord {star_lord})"
            )
            
            # ═══════════════════════════════════════════════════════════
            # STEP 2: Get Star Lord's Significations (Using helper!)
            # ═══════════════════════════════════════════════════════════
            signified_houses = set()
            
            if star_lord:
                # ✅ Use existing helper function - includes occupation, sign lord, ownership
                signified_houses = get_signified_houses(star_lord, planets, houses)
                
                if signified_houses:
                    logger.info(
                        f"   → Star Lord {star_lord} signifies houses: {sorted(signified_houses)}"
                    )
                else:
                    logger.warning(f"   ⚠️ Star Lord {star_lord} has no significations")
            else:
                logger.warning(f"   ⚠️ No star lord found for nakshatra {nakshatra_name}")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 3: Analyze House Linkages Based on Significations
            # ═══════════════════════════════════════════════════════════
            
            # Define critical house combinations
            WEALTH_HOUSES = {2, 10, 11}
            LOSS_HOUSES = {6, 8, 12}
            REPAYMENT_CHAIN = {2, 6, 11}  # Income + Debt + Gains = Repayment
            DEFAULT_CHAIN = {6, 8, 12}    # Debt + Loss + Drain = Default
            
            # Count connections
            wealth_connection = len(WEALTH_HOUSES & signified_houses)
            loss_connection = len(LOSS_HOUSES & signified_houses)
            repayment_strength = len(REPAYMENT_CHAIN & signified_houses)
            default_strength = len(DEFAULT_CHAIN & signified_houses)
            
            # ═══════════════════════════════════════════════════════════
            # STEP 4: Determine Verdict Based on SIGNIFICATIONS & LINKAGES
            # ═══════════════════════════════════════════════════════════
            
            verdict = "NEUTRAL"
            chain_text = ""
            interpretation = ""
            
            if signified_houses:
                # Build chain visualization
                chain_text = (
                    f"{csl} → {nakshatra_name} (Star: {star_lord}) → "
                    f"Signifies houses {sorted(signified_houses)}"
                )
                
                # House-specific logic
                if house_num == 2:  # Wealth/Income
                    if wealth_connection >= 2:
                        verdict = "STRONG"
                        interpretation = (
                            f"{chain_text} → ✅ Star lord connects {wealth_connection}/3 "
                            f"wealth houses {sorted(WEALTH_HOUSES & signified_houses)} → "
                            f"Strong income capacity promised"
                        )
                    elif loss_connection >= 2:
                        verdict = "WEAK"
                        interpretation = (
                            f"{chain_text} → ⚠️ Star lord connects {loss_connection}/3 "
                            f"loss houses {sorted(LOSS_HOUSES & signified_houses)} → "
                            f"Income drains through debts/losses"
                        )
                    else:
                        verdict = "MODERATE"
                        interpretation = (
                            f"{chain_text} → ⚖️ Mixed significations → "
                            f"Moderate income capacity"
                        )
                
                elif house_num == 6:  # Debt/Loans
                    if repayment_strength >= 2:
                        verdict = "MANAGEABLE"
                        interpretation = (
                            f"{chain_text} → ✅ Star lord connects {repayment_strength}/3 "
                            f"repayment chain houses {sorted(REPAYMENT_CHAIN & signified_houses)} "
                            f"(2-6-11) → Debt manageable with repayment capacity"
                        )
                    elif default_strength >= 2:
                        verdict = "HIGH_RISK"
                        interpretation = (
                            f"{chain_text} → ⚠️ Star lord connects {default_strength}/3 "
                            f"default chain houses {sorted(DEFAULT_CHAIN & signified_houses)} "
                            f"(6-8-12) → High default risk, debt burden severe"
                        )
                    else:
                        verdict = "NEUTRAL"
                        interpretation = (
                            f"{chain_text} → ⚖️ Mixed significations → "
                            f"Debt exists but outcome unclear"
                        )
                
                elif house_num == 8:  # Sudden Loss
                    if loss_connection >= 2:
                        verdict = "RISKY"
                        interpretation = (
                            f"{chain_text} → ⚠️ Star lord connects {loss_connection}/3 "
                            f"loss houses {sorted(LOSS_HOUSES & signified_houses)} → "
                            f"High sudden loss risk"
                        )
                    elif wealth_connection >= 2:
                        verdict = "PROTECTED"
                        interpretation = (
                            f"{chain_text} → ✅ Star lord connects {wealth_connection}/3 "
                            f"wealth houses {sorted(WEALTH_HOUSES & signified_houses)} → "
                            f"Protected from major losses"
                        )
                    else:
                        verdict = "UNPREDICTABLE"
                        interpretation = (
                            f"{chain_text} → ⚖️ Mixed significations → "
                            f"Sudden events unpredictable"
                        )
                
                elif house_num == 11:  # Gains/Repayment
                    if wealth_connection >= 2:
                        verdict = "EXCELLENT"
                        interpretation = (
                            f"{chain_text} → ✅ Star lord connects {wealth_connection}/3 "
                            f"wealth houses {sorted(WEALTH_HOUSES & signified_houses)} → "
                            f"Strong gains and repayment capacity"
                        )
                    elif loss_connection >= 2:
                        verdict = "POOR"
                        interpretation = (
                            f"{chain_text} → ⚠️ Star lord connects {loss_connection}/3 "
                            f"loss houses {sorted(LOSS_HOUSES & signified_houses)} → "
                            f"Gains drain away, weak repayment"
                        )
                    else:
                        verdict = "MODERATE"
                        interpretation = (
                            f"{chain_text} → ⚖️ Mixed significations → "
                            f"Moderate gains potential"
                        )
                
                elif house_num == 12:  # Expenses/Drains
                    if loss_connection >= 2:
                        verdict = "EXCESSIVE"
                        interpretation = (
                            f"{chain_text} → ⚠️ Star lord connects {loss_connection}/3 "
                            f"loss houses {sorted(LOSS_HOUSES & signified_houses)} → "
                            f"Excessive expenses, drains severe"
                        )
                    elif wealth_connection >= 1:
                        verdict = "CONTROLLED"
                        interpretation = (
                            f"{chain_text} → ✅ Star lord has wealth connection → "
                            f"Expenses controlled or invested wisely"
                        )
                    else:
                        verdict = "NORMAL"
                        interpretation = (
                            f"{chain_text} → ⚖️ Normal expense patterns"
                        )
            
            else:
                # No significations available - incomplete analysis
                verdict = "UNCLEAR"
                chain_text = f"{csl} as CSL (star lord significations unavailable)"
                interpretation = (
                    f"⚠️ WARNING: Cannot determine proper KP verdict without "
                    f"star lord significations. Analysis incomplete."
                )
            
            # Store structured data
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings[house_num],
                "csl": csl,
                "nakshatra": nakshatra_name,
                "star_lord": star_lord,
                "signified_houses": sorted(signified_houses),
                "wealth_connection": wealth_connection,
                "loss_connection": loss_connection,
                "repayment_chain_strength": repayment_strength,
                "default_chain_strength": default_strength,
                "verdict": verdict,
                "interpretation": interpretation,
                "chain": chain_text,
                "has_significations": bool(signified_houses)
            }
            
            # Add to key findings
            kp_data["key_findings"].append(
                f"H{house_num} ({house_meanings[house_num]}): {verdict} → "
                f"{csl} signifies {sorted(signified_houses) if signified_houses else 'unclear'}"
            )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: Analyze Overall House Linkages for Event Promises
        # ═══════════════════════════════════════════════════════════
        
        # Check 6th CSL for debt promise
        h6_detail = kp_data["csl_details"].get(6, {})
        h6_signified = set(h6_detail.get("signified_houses", []))
        
        # Check 11th CSL for repayment promise
        h11_detail = kp_data["csl_details"].get(11, {})
        h11_signified = set(h11_detail.get("signified_houses", []))
        
        # REPAYMENT EVENT: Does 6th CSL connect to 2 & 11?
        if h6_signified:
            repayment_promise = bool({2, 11} & h6_signified)
            kp_data["event_promises"]["loan_repayment"] = {
                "promised": repayment_promise,
                "logic": f"6th CSL must connect 2 (income) & 11 (gains) for repayment",
                "actual": f"6th CSL connects: {sorted(h6_signified)}",
                "result": (
                    "✅ Repayment PROMISED - 6th CSL links 2-11" if repayment_promise
                    else "⚠️ Repayment NOT PROMISED - 6th CSL doesn't link 2-11"
                )
            }
        
        # DEFAULT RISK: Does 6th CSL connect to 8 & 12?
        if h6_signified:
            default_risk = bool({8, 12} & h6_signified)
            kp_data["event_promises"]["loan_default"] = {
                "risk": default_risk,
                "logic": f"6th CSL connecting 8 (loss) & 12 (drain) shows default risk",
                "actual": f"6th CSL connects: {sorted(h6_signified)}",
                "result": (
                    "⚠️ DEFAULT RISK HIGH - 6th CSL links to 8-12" if default_risk
                    else "✅ DEFAULT RISK LOW - 6th CSL doesn't link 8-12"
                )
            }
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Overall Verdict Based on Key House Linkages
        # ═══════════════════════════════════════════════════════════
        
        h6_verdict = h6_detail.get("verdict", "UNCLEAR")
        h11_verdict = h11_detail.get("verdict", "UNCLEAR")
        
        if h6_verdict == "MANAGEABLE" and h11_verdict in ["EXCELLENT", "MODERATE"]:
            kp_data["overall_verdict"] = "LOW_RISK"
            kp_data["key_findings"].insert(
                0,
                "✅ KP OVERALL: 6th CSL shows repayment chain (2-6-11 connected) "
                "+ 11th CSL shows gains → Low default risk"
            )
        elif h6_verdict == "HIGH_RISK" or h11_verdict == "POOR":
            kp_data["overall_verdict"] = "HIGH_RISK"
            kp_data["key_findings"].insert(
                0,
                "⚠️ KP OVERALL: 6th CSL shows default chain (6-8-12 connected) "
                "OR 11th CSL shows weak gains → High default risk"
            )
        else:
            kp_data["overall_verdict"] = "MODERATE_RISK"
            kp_data["key_findings"].insert(
                0,
                "⚖️ KP OVERALL: Mixed house linkages → Moderate risk, careful planning needed"
            )
        
        return kp_data

        
       
    # ═══════════════════════════════════════════════════════════════
    # ENHANCED HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def extract_planet_name(p):
        """Extract planet name from dict or string"""
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
                            normalized_lord, lord_data, dignity
                        )
                    else:
                        logger.debug(f"Could not determine dignity for {normalized_lord}")
                        
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")
            
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
        """Get house meaning for finance context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None,
        lagna_lord_analysis: dict = None,  # ✅ NEW: Accept lagna lord
        kp_significator_table: dict = None  # ✅ NEW: Accept significator table
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "finance"
        
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
        
        # ✅ Store lagna lord analysis
        if lagna_lord_analysis:
            result.additional_data["lagna_lord_analysis"] = lagna_lord_analysis
            logger.info(f"✅ Stored lagna_lord_analysis: {lagna_lord_analysis.get('lagna_lord', 'N/A')}")
        
        # ✅ Store KP significator table
        if kp_significator_table:
            result.additional_data["kp_significator_table"] = kp_significator_table
            logger.info(f"✅ Stored kp_significator_table with {len(kp_significator_table.get('planets', {}))} planets")
        
        # Store timing windows if available
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")

    # ══════════════════════════════════════════════════════════════════
    # SPECIFIC PROBLEM ANALYSIS (Use KP data for KP logic)
    # ══════════════════════════════════════════════════════════════════
    
    def _evaluate_financial_challenges(
        self,
        planets: Dict,
        houses: List,
        result: EvaluationResult
    ):
        """
        Evaluate root causes of financial challenges.
        
        ENHANCED: Extracts structured KP data for LLM.
        """
        logger.info("📊 Evaluating FINANCIAL CHALLENGES...")
        
        # Get detailed financial analysis (from finance_engine)
        kp_text_points = evaluate_finance(planets, houses)
        
        # ✅ NEW: Extract structured KP data directly from cusps
        kp_structured = self._extract_kp_finance_structured(planets, houses,self.FINANCE_HOUSES)
        
        # ✅ NEW: Add points with "KP:" prefix
        for p in kp_text_points[:12]:
            # Check if this looks like a KP point
            is_kp_point = any(kw in p.lower() for kw in [
                'cusp', 'csl', 'sub-lord', 'sub lord', 
                'signif', 'connects', 'connect to'
            ])
            
            if is_kp_point:
                result.add_point(f"KP: {p}")
            else:
                result.add_point(p)
        
        # ✅ NEW: Store structured KP data in additional_data
        result.additional_data["kp_finance_analysis"] = kp_structured
        
        if kp_structured.get("has_kp_data"):
            logger.info(f"✅ Structured KP data extracted:")
            logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
            logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
            for house_num, info in kp_structured["csl_details"].items():
                logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
        else:
            logger.warning("⚠️ No KP cusp sub lord data found")
        
        logger.info(f"✅ Added {len(kp_text_points[:12])} financial challenge points")


    
    def _evaluate_loan_risk(
        self,
        planets: Dict,
        houses: List,
        result: EvaluationResult,
        meta_query_type
    ):
        """
        Evaluate loan default risk with timing support.
        
        ENHANCED: Extracts structured KP data for LLM.
        """
        logger.info("💰 Evaluating LOAN DEFAULT RISK...")
        
        # Get borrowing analysis (KP logic from finance_engine)
        kp_text_points = evaluate_borrowing_A2_strict(planets, houses)
        
        # ✅ NEW: Extract structured KP data directly from cusps
        kp_structured = self._extract_kp_finance_structured(planets, houses,self.FINANCE_HOUSES)
        
        # ✅ NEW: Add points with "KP:" prefix
        for p in kp_text_points[:10]:
            # Check if this looks like a KP point
            is_kp_point = any(kw in p.lower() for kw in [
                'cusp', 'csl', 'sub-lord', 'sub lord',
                'signif', 'connects', 'connect to', 'borrowing'
            ])
            
            if is_kp_point:
                result.add_point(f"KP: {p}")
            else:
                result.add_point(p)
        
        # ✅ NEW: Store structured KP data in additional_data
        result.additional_data["kp_finance_analysis"] = kp_structured
        
        if kp_structured.get("has_kp_data"):
            logger.info(f"✅ Structured KP data extracted:")
            logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
            logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
            for house_num, info in kp_structured["csl_details"].items():
                logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
        else:
            logger.warning("⚠️ No KP cusp sub lord data found")
        
        # Add timing overlay if TIMING question
        is_timing = (
            meta_query_type == "TIMING" or
            meta_query_type == QueryType.TIMING or
            str(meta_query_type) == "TIMING"
        ) if meta_query_type else False
        
        if is_timing:
            logger.info("⏰ Adding timing overlay...")
            
            timing_rules = TIMING_RULES.get("Loan Repayment Timing", {})
            planet_scores = score_kp_all_planets(planets, houses, timing_rules)
            positive_planets = get_positive_planets(planet_scores)
            ruling_planets = get_kp_ruling_planets(planets)
            
            if positive_planets:
                result.add_point(
                    f"KP: Favorable repayment periods supported by: {', '.join(positive_planets[:4])}"
                )
            if ruling_planets:
                result.add_point(
                    f"KP: Ruling planets for debt resolution: {', '.join(ruling_planets)}"
                )
        
        logger.info(f"✅ Added loan risk points with structured KP data")
    
    def _evaluate_dispute_risk(
        self,
        planets: Dict,
        houses: List,
        result: EvaluationResult
    ):
        """Evaluate financial dispute risk"""
        logger.info("⚖️ Evaluating FINANCIAL DISPUTE RISK...")
        
        # Get general financial points
        points = evaluate_finance(planets, houses)
        
        # Filter for dispute-relevant points
        dispute_keywords = ["dispute", "court", "6", "8", "12", "property", "legal"]
        filtered_points = [
            p for p in points
            if any(kw in p.lower() for kw in dispute_keywords)
        ]
        
        for p in filtered_points[:10]:
            result.add_point(p)
        
        logger.info(f"✅ Added {len(filtered_points[:10])} dispute risk points")
    
    def _evaluate_remedies(
        self,
        planets: Dict,
        houses: List,
        result: EvaluationResult
    ):
        """Suggest finance remedies"""
        logger.info("🔮 Evaluating FINANCE REMEDIES...")
        
        result.add_point(
            "Remedies target afflicted lords of houses 2, 6, 8, 11, 12."
        )
        result.add_point(
            "Focus on strengthening wealth lords (H2, H11) and controlling loss lords (H6, H8, H12)."
        )
        
        logger.info(f"✅ Added remedy points")
    
    # ══════════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════════
    
    def get_questions(self) -> List[Question]:
        """Return Finance → Facing Financial Problems questions"""
        
        return [
            Question(
                id="FIN_FP_1",
                question=(
                    "According to astrology, what does my birth chart reveal about my financial situation, including income stability, wealth accumulation and my ability to manage loans and debts?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Reason for Financial Challenges"
            ),
            Question(
                id="FIN_FP_2",
                question=(
                    "Will I be able to repay my current loan, and is there a risk of default?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Loan Default Risk"
            ),
            Question(
                id="FIN_FP_3",
                question=(
                    "Are there any risks of financial disputes, court cases, or issues related "
                    "to ancestral property, loss, or damage, and how can I resolve them?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Risk of Financial Dispute"
            )
        ]
"""
Prospects of Investments Evaluator - Enhanced Version v3.3 (COMPLETE)

ENHANCEMENTS:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ KP finance engine integration (preserved)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP significations using correct hierarchy (sub > star > occupy > own)
✅ Investment suitability matrix with correct Rahu mapping
"""

from typing import Dict, List, Optional
import logging
from app.core.astro_constants import normalize_planet_name
from app.domains.base import (
    BaseEvaluator,
    EvaluationResult,
    Question,
    QueryMeta,
    QueryType,
    EventPolarity,
    InterpretationGoal,
)

from app.core.astro_constants import detect_aspects, normalize_planet_name
from app.domains.excel_structure_config import get_houses_for_question

# ---- STRICT FINANCE ENGINE (NO MODIFICATION) ----
from app.domains.finance.finance_engine import (
    evaluate_finance
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
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ProspectsOfInvestmentsEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Finance → Prospects Of Investments
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Dual data source support (KP + Vedic)
    - Timing windows extraction and formatting
    - KP significations with correct hierarchy
    - Investment suitability matrix
    """

    domain = "Finance"
    subtopic = "Prospects Of Investments"
    
    # Investment-specific houses
    INVESTMENT_HOUSES = {2, 5, 8, 10, 11}
    
    # House meanings for context
    HOUSE_MEANINGS = {
        2: "Wealth/Income",
        5: "Speculation/Risk",
        8: "Hidden Wealth/Inheritance",
        10: "Career/Business",
        11: "Gains/Returns"
    }



    def _create_investment_suitability_matrix(
        self,
        kp_analysis: Dict,
        vedic_lords: Dict = None,
        lagna_lord_analysis: Dict = None
    ) -> Dict[str, Dict]:
        """
        Create modern investment suitability matrix with CORRECT Rahu logic.
        
        Fixes astrological error: Rahu → volatile/foreign, NOT gold preservation
        """
        matrix = {}
        
        csl_details = kp_analysis.get("csl_details", {})
        h2_detail = csl_details.get(2, {})
        h5_detail = csl_details.get(5, {})
        h11_detail = csl_details.get(11, {})
        h4_detail = csl_details.get(4, {})
        h8_detail = csl_details.get(8, {})
        
        h2_csl = h2_detail.get("csl")
        h2_star_lord = h2_detail.get("star_lord")
        h2_verdict = h2_detail.get("verdict", "UNKNOWN")
        
        h5_verdict = h5_detail.get("verdict", "UNKNOWN")
        h11_verdict = h11_detail.get("verdict", "UNKNOWN")
        h4_verdict = h4_detail.get("verdict", "UNKNOWN")
        h8_verdict = h8_detail.get("verdict", "UNKNOWN")
        
        # Planet categories
        stable_planets = {"Jupiter", "Saturn", "Venus", "Moon"}
        volatile_planets = {"Rahu", "Ketu", "Mars"}
        
        # ═══════════════════════════════════════════════════════════
        # 1. EQUITY MUTUAL FUNDS (Large Cap)
        # ═══════════════════════════════════════════════════════════
        if h11_verdict in ["EXCELLENT", "STRONG"] and h5_verdict not in ["RISKY", "WEAK"]:
            rating = "HIGH"
            reason = f"11th house {h11_verdict.lower()} supports systematic gains"
        elif h11_verdict == "MODERATE":
            rating = "MODERATE"
            reason = "11th house moderate - long-term SIP recommended"
        else:
            rating = "LOW"
            reason = f"11th house {h11_verdict.lower()} - limited returns expected"
        
        matrix["Equity Mutual Funds (Large Cap)"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 2. GOLD/SILVER - FIX: Requires STABLE planets (NOT Rahu!)
        # ═══════════════════════════════════════════════════════════
        h2_stable = h2_star_lord in stable_planets if h2_star_lord else False
        h2_volatile = h2_star_lord in volatile_planets if h2_star_lord else False
        
        if h2_stable and h2_verdict not in ["WEAK", "POOR"]:
            rating = "HIGH"
            reason = f"2nd house star lord {h2_star_lord} (stable planet) supports wealth preservation through gold"
        elif h2_volatile:
            rating = "MODERATE"
            reason = f"⚠️ 2nd house star lord {h2_star_lord} (volatile) indicates irregular income. Gold only as hedge (max 20-30%)"
        else:
            rating = "MODERATE"
            reason = "Gold suitable as portfolio diversifier (20-30% allocation)"
        
        matrix["Gold/Silver (ETF or Physical)"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 3. REAL ESTATE
        # ═══════════════════════════════════════════════════════════
        if h4_verdict in ["EXCELLENT", "STRONG"] and h11_verdict in ["EXCELLENT", "STRONG", "MODERATE"]:
            rating = "HIGH"
            reason = "4th house + 11th house both support property investment"
        elif h4_verdict == "MODERATE":
            rating = "MODERATE"
            reason = "Property possible but requires patience and perfect timing (see timing windows)"
        else:
            rating = "LOW"
            reason = f"4th house {h4_verdict.lower()} - property investment challenging now"
        
        matrix["Real Estate/Land"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 4. FIXED DEPOSITS/BONDS
        # ═══════════════════════════════════════════════════════════
        if h2_star_lord in {"Saturn", "Jupiter"} or h5_verdict in ["RISKY", "WEAK"]:
            rating = "HIGH"
            reason = "Conservative approach strongly recommended - safe capital preservation"
        else:
            rating = "MODERATE"
            reason = "Suitable for emergency fund and conservative portfolio portion"
        
        matrix["Fixed Deposits/Bonds"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 5. DAY TRADING/INTRADAY
        # ═══════════════════════════════════════════════════════════
        if h5_verdict in ["RISKY", "WEAK", "POOR"]:
            rating = "AVOID"
            reason = f"❌ 5th house {h5_verdict.lower()} - day trading will lead to losses"
        elif h5_verdict == "FAVORABLE":
            rating = "MODERATE"
            reason = "Possible ONLY with strict stop-loss discipline (max 5-10% of portfolio)"
        else:
            rating = "LOW"
            reason = "Not recommended - focus on long-term investing instead"
        
        matrix["Day Trading/Intraday"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 6. CRYPTOCURRENCY
        # ═══════════════════════════════════════════════════════════
        if h5_verdict in ["RISKY", "WEAK"] or h8_verdict in ["CHALLENGING", "UNPREDICTABLE"]:
            rating = "AVOID"
            reason = "❌ 5th/8th houses show sudden loss risk - cryptocurrency extremely dangerous"
        elif h2_csl == "Rahu" and h5_verdict == "FAVORABLE":
            rating = "VERY LOW"
            reason = "Rahu shows tech affinity but MAXIMUM 2-5% allocation (only money you can afford to lose)"
        else:
            rating = "AVOID"
            reason = "Too volatile for your chart - avoid completely"
        
        matrix["Cryptocurrency"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 7. INTERNATIONAL STOCKS (Rahu connection = foreign/tech)
        # ═══════════════════════════════════════════════════════════
        rahu_connected = (h2_csl == "Rahu" or h2_star_lord == "Rahu" or 
                        h11_detail.get("csl") == "Rahu")
        
        if rahu_connected and h11_verdict in ["EXCELLENT", "STRONG", "MODERATE"]:
            rating = "MODERATE"
            reason = "✅ Rahu connection supports foreign/tech exposure - consider international index funds"
        else:
            rating = "LOW"
            reason = "No strong foreign connection - focus on domestic investments"
        
        matrix["International Stocks/Funds"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 8. INDEX FUNDS (Passive investing)
        # ═══════════════════════════════════════════════════════════
        if h11_verdict in ["MODERATE", "STRONG", "EXCELLENT"]:
            rating = "HIGH"
            reason = "Systematic diversified exposure ideal for long-term wealth building"
        else:
            rating = "MODERATE"
            reason = "Still suitable but returns may be limited"
        
        matrix["Index Funds (Passive)"] = {"rating": rating, "kp_reasoning": reason}
        
        return matrix
    
    
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

        # ═══════════════════════════════════════════════════════
        # STEP 0: Choose Data Source for House Lord Analysis
        # ═══════════════════════════════════════════════════════
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

            # ✅ ALWAYS include house 1 for lagna lord analysis
            all_relevant_houses.add(1)
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback")
            all_relevant_houses = self.INVESTMENT_HOUSES
            primary_houses = {2, 11}
            secondary_houses = {5, 8, 10}
            all_relevant_houses.add(1)

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("PROSPECTS OF INVESTMENTS EVALUATOR (ENHANCED v3.3 - COMPLETE)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects (on analysis data)
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
        # STEP 3: Extract House Lords Data (using Vedic data)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )
        
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")


        # ═══════════════════════════════════════════════════════
        # STEP 3.5: Extract Lagna (Ascendant) Information
        # ═══════════════════════════════════════════════════════
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)
        
        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")


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
            
            # Fallback: try "Prospects of Property" key if sub_subdomain doesn't match
            if not timing_windows_list and "Prospects of Property" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Prospects of Property"]
                logger.info(f"🔍 DEBUG: Using 'Prospects of Property' fallback key, found {len(timing_windows_list)} windows")
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
        # STEP 6: Add House Analysis Points (Vedic - all subdomains)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Prospects of Investment", "Prospects of Property", "Financial Challenges"}:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ═══════════════════════════════════════════════════════
        # STEP 7: KP EVALUATION (ENHANCED WITH STRUCTURED EXTRACTION + INVESTMENT MATRIX)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Prospects of Investment", "Prospects of Property"}:
            try:
                finance_text_points = evaluate_finance(
                    planets,
                    houses
                )

                logger.warning(f"🔍 evaluate_finance() returned {len(finance_text_points)} KP points")
                
                # ✅ Extract structured KP data directly from cusps
                kp_structured = self._extract_kp_investments_structured_direct(planets, houses)

                # ✅ Add points with "KP:" prefix for KP-related points
                if finance_text_points:
                    logger.warning(f"🔍 First KP point: {finance_text_points[0]}")
                    for p in finance_text_points:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)
                else:
                    result.add_point(
                        "❓ Financial promise unclear from KP analysis. "
                        "No strong cusp sub lord significations detected."
                    )

                # ✅ Store structured KP data in additional_data
                result.additional_data["kp_investments_analysis"] = kp_structured
                
                if kp_structured.get("has_kp_data"):
                    logger.info(f"✅ Structured KP investments data extracted:")
                    logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
                    logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
                    for house_num, info in kp_structured["csl_details"].items():
                        logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
                    
                    # ═══════════════════════════════════════════════════════════
                    # CREATE INVESTMENT MATRIX (NEW - FIX #1)
                    # ═══════════════════════════════════════════════════════════
                    try:
                        investment_matrix = self._create_investment_suitability_matrix(
                            kp_analysis=kp_structured,
                            vedic_lords=house_lords_info if house_lords_info else None,
                            lagna_lord_analysis=None
                        )
                        
                        result.additional_data["investment_suitability_matrix"] = investment_matrix
                        
                        logger.info(f"✅ Investment suitability matrix created with {len(investment_matrix)} investment types")
                        for inv_type, details in investment_matrix.items():
                            logger.info(f"   {inv_type}: {details['rating']}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error creating investment matrix: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                else:
                    logger.warning("⚠️ No KP cusp sub lord data found for investments")

            except Exception as e:
                logger.warning(f"Finance evaluation error: {e}")
                result.add_point(
                    "Financial evaluation could not be completed due to internal rule constraints."
                )
                # Still try to extract KP data even if finance_engine fails
                try:
                    kp_structured = self._extract_kp_investments_structured_direct(planets, houses)
                    result.additional_data["kp_investments_analysis"] = kp_structured
                    
                    # Try to create matrix even on error
                    if kp_structured.get("has_kp_data"):
                        try:
                            investment_matrix = self._create_investment_suitability_matrix(
                                kp_analysis=kp_structured,
                                vedic_lords=None,
                                lagna_lord_analysis=None
                            )
                            result.additional_data["investment_suitability_matrix"] = investment_matrix
                            logger.info(f"✅ Investment matrix created (fallback path) with {len(investment_matrix)} types")
                        except Exception as matrix_err:
                            logger.error(f"❌ Could not create investment matrix in fallback: {matrix_err}")
                except Exception as kp_err:
                    logger.error(f"❌ Could not extract KP data in fallback: {kp_err}")

        # ═══════════════════════════════════════════════════════
        # STEP 8: LLM-ONLY QUESTIONS (EARLY RETURNS - LAST!)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Income Growth"}:
            result.add_point(
                "This question is evaluated using financial behavior, planning, "
                "and practical decision-making rather than predictive astrology."
            )
            
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

        # ═══════════════════════════════════════════════════════
        # STEP 9: REMEDIES
        # ═══════════════════════════════════════════════════════
        if sub_subdomain == "Remedy and Suggestion":
            result.add_point(
                "Financial remedies focus on strengthening income houses, "
                "reducing debt pressure, and stabilizing long-term wealth."
            )

        # ═══════════════════════════════════════════════════════
        # STEP 10: Store Enhanced Data for LLM
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

        return result


    def _extract_kp_investments_structured_direct(self, planets: Dict, houses: List) -> Dict:
        """
        Extract structured KP investments data using CORRECT KP methodology:
        CSL → Star Lord → Significations (NOT just CSL planet nature!)
        
        KP Principle: Planet nature = flavor, Significations = result. Result wins.
        """
        from app.core.astro_constants import normalize_planet_name
        
        # Try to import signification helpers
        try:
            from app.core.astro_constants import get_signified_houses, get_signified_score
            has_signification_helpers = True
            logger.info("✅ Signification helpers imported successfully")
        except ImportError:
            logger.error("❌ CRITICAL: Signification helpers NOT available - will use basic star lord analysis")
            has_signification_helpers = False
        
        kp_data = {
            "csl_details": {},
            "overall_verdict": "UNKNOWN",
            "key_findings": [],
            "has_kp_data": False,
            "methodology": "CSL → Star Lord → Significations (Fallback if significations unavailable)"
        }
        
        # Investment-relevant houses
        investment_houses = [2, 5, 8, 11, 10]
        house_meanings = {
            2: "Wealth/Income",
            5: "Speculation/Risk",
            8: "Hidden Wealth/Inheritance",
            10: "Career/Business",
            11: "Gains/Returns"
        }
        
        # House groups for signification analysis
        WEALTH_HOUSES = {2, 10, 11}
        LOSS_HOUSES = {6, 8, 12}
        STRONG_WEALTH = {2, 11}
        
        # Extract CSL for each investment house
        for house_num in investment_houses:
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
            
            # ═══════════════════════════════════════════════════════════
            # CORRECT KP METHODOLOGY: CSL → Star Lord → Significations
            # ═══════════════════════════════════════════════════════════
            
            csl_planet = planets.get(csl, {})
            
            # Step 1: Get CSL's star lord (nakshatra lord)
            star_lord_raw = csl_planet.get("nakshatra_lord", "")
            star_lord = normalize_planet_name(star_lord_raw) if star_lord_raw else None
            
            # Also get nakshatra name for reference
            nakshatra_name = csl_planet.get("nakshatra", "") or csl_planet.get("nakshatra_name", "")
            
            # Step 2: Get star lord's significations
            signified_houses = set()
            signified_score = {}
            
            if star_lord and has_signification_helpers:
                try:
                    # Get which houses the star lord signifies
                    signified_houses = set(get_signified_houses(star_lord, planets, houses))
                    signified_score = get_signified_score(star_lord, planets, houses)
                    
                    # ⚠️ CRITICAL CHECK: Are significations actually populated?
                    if signified_houses:
                        logger.info(f"✅ House {house_num}: CSL {csl} → {nakshatra_name} (Star Lord {star_lord}) → Signifies {sorted(signified_houses)}")
                    else:
                        logger.warning(f"⚠️ House {house_num}: Star lord {star_lord} has EMPTY significations - using star lord house position fallback")
                        # Fallback: Use star lord's house position
                        star_lord_obj = planets.get(star_lord, {})
                        if star_lord_obj:
                            star_lord_house = star_lord_obj.get("house")
                            if star_lord_house:
                                signified_houses = {star_lord_house}
                                logger.warning(f"⚠️ Fallback: Using star lord house {star_lord_house} for {star_lord}")
                    
                except Exception as e:
                    logger.error(f"❌ Error getting significations for {star_lord}: {e}")
                    # Fallback: Use basic star lord house position
                    star_lord_obj = planets.get(star_lord, {})
                    if star_lord_obj:
                        star_lord_house = star_lord_obj.get("house")
                        if star_lord_house:
                            signified_houses = {star_lord_house}
                            logger.warning(f"⚠️ Exception fallback: Using star lord house {star_lord_house}")
            
            elif star_lord:
                # Fallback when signification helpers not available
                logger.warning(f"⚠️ No signification helpers - using star lord house position for {star_lord}")
                star_lord_obj = planets.get(star_lord, {})
                if star_lord_obj:
                    star_lord_house = star_lord_obj.get("house")
                    if star_lord_house:
                        signified_houses = {star_lord_house}
                        logger.warning(f"⚠️ Using star lord house {star_lord_house} for CSL {csl}")
            
            # ⚠️ FINAL FALLBACK: If still no significations, we CANNOT make proper KP analysis
            if not signified_houses:
                logger.error(f"❌ CRITICAL: No significations available for house {house_num} CSL {csl} - analysis will be INCOMPLETE")
                # Mark this in the data
                signified_houses = set()  # Keep empty to show we don't have data
            
            # Step 3: Analyze significations (or lack thereof)
            wealth_connection = len(signified_houses & WEALTH_HOUSES)
            loss_connection = len(signified_houses & LOSS_HOUSES)
            strong_wealth_connection = len(signified_houses & STRONG_WEALTH)
            
            # Get signification strength scores
            wealth_strength = sum(signified_score.get(h, 0) for h in WEALTH_HOUSES)
            loss_strength = sum(signified_score.get(h, 0) for h in LOSS_HOUSES)
            
            # Get cusp sign
            cusp_sign = (
                house_data.get("start_rasi", "") or
                house_data.get("rasi", "") or
                house_data.get("sign", "")
            )
            
            # Planet nature (benefic/malefic) is just the FLAVOR
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            is_benefic = csl in benefics
            is_malefic = csl in malefics
            
            flavor = "benefic flavor" if is_benefic else "malefic flavor" if is_malefic else "neutral flavor"
            
            # ═══════════════════════════════════════════════════════════
            # VERDICT BASED ON SIGNIFICATIONS (Result wins!)
            # ═══════════════════════════════════════════════════════════
            
            verdict = "NEUTRAL"
            interpretation = ""
            
            # Build interpretation based on star lord significations
            if star_lord and signified_houses:
                chain_text = f"{csl} ({flavor}) → {nakshatra_name if nakshatra_name else star_lord}'s star → {star_lord} signifies {sorted(signified_houses)}"
            elif star_lord:
                chain_text = f"{csl} ({flavor}) → {nakshatra_name if nakshatra_name else star_lord}'s star → {star_lord} (significations unavailable)"
                logger.warning(f"⚠️ House {house_num}: Significations MISSING for {star_lord} - verdict will be INCOMPLETE")
            else:
                chain_text = f"{csl} ({flavor}) as cusp sub lord (no star lord data)"
                logger.error(f"❌ House {house_num}: No star lord data - analysis SEVERELY LIMITED")
            
            # House-specific verdicts based on SIGNIFICATIONS (or fallback)
            if house_num == 2:  # Wealth/Income house
                if signified_houses:
                    if strong_wealth_connection >= 2 or wealth_strength >= 4:
                        verdict = "STRONG"
                        interpretation = (
                            f"{chain_text} → Strong income capacity through {sorted(STRONG_WEALTH & signified_houses)} connection. "
                            f"{'Benefic nature adds smoothness.' if is_benefic else 'Despite malefic nature, significations promise income.'}"
                        )
                    elif loss_connection >= 2 or loss_strength >= 4:
                        verdict = "WEAK"
                        interpretation = (
                            f"{chain_text} → Income exists but drains through {sorted(LOSS_HOUSES & signified_houses)} "
                            f"(debt/loss/expenses). "
                            f"{'Despite benefic nature, significations show drainage.' if is_benefic else 'Malefic nature compounds the challenge.'}"
                        )
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate income capacity."
                else:
                    # ⚠️ INCOMPLETE ANALYSIS WARNING
                    verdict = "UNCLEAR"
                    interpretation = (
                        f"{chain_text} → ⚠️ WARNING: Significations unavailable. "
                        f"Cannot make definitive KP analysis for income. "
                        f"Based on {flavor} alone (less reliable): {'Moderate income potential' if is_benefic else 'Income challenges likely'}."
                    )
            
            elif house_num == 5:  # Speculation/Risk house
                if signified_houses:
                    if 5 in signified_houses and wealth_connection >= 1:
                        verdict = "FAVORABLE"
                        interpretation = f"{chain_text} → Speculation supported with wealth connection. Calculated risks can work."
                    elif loss_connection >= 2 or 8 in signified_houses:
                        verdict = "RISKY"
                        interpretation = (
                            f"{chain_text} → High speculation risk through {sorted(LOSS_HOUSES & signified_houses)}. "
                            f"Avoid day trading and derivatives."
                        )
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Mixed speculation signals. Long-term investing preferred."
                else:
                    verdict = "UNCLEAR"
                    interpretation = (
                        f"{chain_text} → ⚠️ WARNING: Significations unavailable. "
                        f"Based on {flavor} alone: {'Moderate speculation capacity' if is_benefic else 'Avoid high-risk speculation'}."
                    )
            
            elif house_num == 8:  # Hidden wealth/inheritance
                if signified_houses:
                    if wealth_connection >= 2:
                        verdict = "PROMISING"
                        interpretation = f"{chain_text} → Gains through inheritance or hidden sources."
                    elif loss_connection >= 2:
                        verdict = "CHALLENGING"
                        interpretation = f"{chain_text} → Sudden losses or unexpected expenses likely."
                    else:
                        verdict = "UNPREDICTABLE"
                        interpretation = f"{chain_text} → Unpredictable financial events."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable. 8th house effects unclear."
            
            elif house_num == 10:  # Career/Business
                if signified_houses:
                    if wealth_connection >= 2:
                        verdict = "EXCELLENT"
                        interpretation = f"{chain_text} → Strong career income and business gains."
                    elif loss_connection >= 2:
                        verdict = "DIFFICULT"
                        interpretation = f"{chain_text} → Career/business challenges with losses."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate career income prospects."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable. Career prospects unclear."
            
            elif house_num == 11:  # Gains/Returns
                if signified_houses:
                    if strong_wealth_connection >= 2 or wealth_strength >= 4:
                        verdict = "EXCELLENT"
                        interpretation = f"{chain_text} → Strong investment returns and gains."
                    elif loss_connection >= 2 or loss_strength >= 4:
                        verdict = "POOR"
                        interpretation = f"{chain_text} → Weak returns, gains drain away."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate gains potential."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable. Gains potential unclear."
            
            # Store structured data
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings[house_num],
                "csl": csl,
                "csl_flavor": flavor,
                "nakshatra": nakshatra_name,
                "star_lord": star_lord,
                "signified_houses": sorted(signified_houses),
                "signified_score": signified_score,
                "wealth_connection": wealth_connection,
                "loss_connection": loss_connection,
                "strong_wealth_connection": strong_wealth_connection,
                "wealth_strength": wealth_strength,
                "loss_strength": loss_strength,
                "cusp_sign": cusp_sign,
                "is_benefic": is_benefic,
                "is_malefic": is_malefic,
                "verdict": verdict,
                "interpretation": interpretation,
                "chain": f"{csl} → {star_lord} star → houses {sorted(signified_houses) if signified_houses else 'UNAVAILABLE'}",
                "has_significations": bool(signified_houses)  # Track if we have real data
            }
            
            # Add to key findings
            if signified_houses:
                kp_data["key_findings"].append(
                    f"House {house_num} ({house_meanings[house_num]}): "
                    f"{csl} → {star_lord} star → signifies {sorted(signified_houses)} → {verdict}"
                )
            else:
                kp_data["key_findings"].append(
                    f"House {house_num} ({house_meanings[house_num]}): "
                    f"{csl} → {star_lord} star → ⚠️ significations MISSING → {verdict} (incomplete)"
                )
        
        # Overall verdict (with warning if significations missing)
        has_complete_data = all(
            detail.get("has_significations", False) 
            for detail in kp_data["csl_details"].values()
        )
        
        if not has_complete_data:
            kp_data["key_findings"].insert(0, 
                "⚠️ CRITICAL WARNING: Some star lord significations are MISSING. "
                "KP analysis is INCOMPLETE. Verdicts are partially based on planet nature (less reliable)."
            )
        
        if kp_data["csl_details"]:
            # Check critical houses using SIGNIFICATIONS
            h2_detail = kp_data["csl_details"].get(2, {})
            h5_detail = kp_data["csl_details"].get(5, {})
            h11_detail = kp_data["csl_details"].get(11, {})
            
            h2_verdict = h2_detail.get("verdict", "UNKNOWN")
            h5_verdict = h5_detail.get("verdict", "UNKNOWN")
            h11_verdict = h11_detail.get("verdict", "UNKNOWN")
            
            # Overall verdict
            if h2_verdict in ["STRONG", "EXCELLENT"] and h11_verdict in ["EXCELLENT", "FAVORABLE"]:
                kp_data["overall_verdict"] = "EXCELLENT_FOR_INVESTMENT"
            elif h5_verdict == "RISKY" or "CHALLENGING" in [h2_verdict, h5_verdict, h11_verdict]:
                kp_data["overall_verdict"] = "AVOID_SPECULATION"
            elif h2_verdict in ["STRONG"] and h5_verdict in ["FAVORABLE"]:
                kp_data["overall_verdict"] = "SUITABLE_FOR_MODERATE_RISK"
            elif h11_verdict in ["POOR", "WEAK"]:
                kp_data["overall_verdict"] = "WEAK_RETURNS"
            else:
                kp_data["overall_verdict"] = "MODERATE_POTENTIAL"
        
        return kp_data
    
    def _is_kp_point(self, point: str) -> bool:
        """Check if a point is KP-related"""
        kp_keywords = [
            'cusp', 'csl', 'sub-lord', 'sub lord',
            'signif', 'connects to', 'ruling planet',
            'kp', 'connects', 'promise'
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
        """Extract house lord information for relevant houses only."""
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

            # Deduce from sign if lord not found directly
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
            
            # Get lord dignity
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
    
    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        """
        Extract lagna (ascendant) information from houses data.
        
        Returns dict with:
        - lagna_sign: The sign of the first house
        - lagna_lord: The planet ruling that sign
        - lagna_lord_house: Where the lagna lord is placed
        - lagna_lord_sign: Sign where lagna lord is placed
        """
        try:
            # Find 1st house
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            
            if not house_1:
                logger.warning("⚠️ House 1 not found - cannot determine lagna")
                return None
            
            # Get lagna sign
            lagna_sign = (
                house_1.get("sign") or 
                house_1.get("start_rasi") or 
                house_1.get("rasi") or
                ""
            )
            
            if not lagna_sign:
                logger.warning("⚠️ Lagna sign not found in house 1 data")
                return None
            
            # Get lagna lord from house 1
            lagna_lord_name = (
                house_1.get("rashi_lord") or
                house_1.get("sign_lord") or
                house_1.get("lord") or
                ""
            )
            
            # Fallback: deduce from sign
            if not lagna_lord_name:
                sign_lords = {
                    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
                    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
                    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
                    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                }
                lagna_lord_name = sign_lords.get(lagna_sign, "")
            
            lagna_lord = normalize_planet_name(lagna_lord_name)
            
            if not lagna_lord:
                logger.warning(f"⚠️ Could not determine lagna lord for {lagna_sign}")
                return None
            
            # Get lagna lord's placement
            lagna_lord_data = planets.get(lagna_lord, {})
            lagna_lord_house = lagna_lord_data.get("house")
            lagna_lord_sign = lagna_lord_data.get("sign", "")
            lagna_lord_degree = (
                lagna_lord_data.get("full_degree") or 
                lagna_lord_data.get("global_degree") or 
                lagna_lord_data.get("degree") or 
                0
            )
            
            # Get dignity if available
            lagna_lord_dignity = "Unknown"
            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity = None
                    
                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(lagna_lord)
                    
                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, 'value') else str(dignity)
                except:
                    pass
            
            lagna_info = {
                "lagna_sign": lagna_sign,
                "lagna_lord": lagna_lord,
                "lagna_lord_house": lagna_lord_house,
                "lagna_lord_sign": lagna_lord_sign,
                "lagna_lord_degree": lagna_lord_degree,
                "lagna_lord_dignity": lagna_lord_dignity,
            }
            
            return lagna_info
            
        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

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
        """Get house meaning for investment context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

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
        domain_prefix = "finance_investments"
        
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
    # QUESTIONS
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="FIN_PI_1",
                question=(
                    "How can I increase my income and are there new avenues for income growth?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Income Growth"
            ),
            Question(
                id="FIN_PI_2",
                question=(
                    "What are the right investment avenues for me and should I invest or trade "
                    "in equity, shares, or other assets?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Prospects of Investment"
            ),
            Question(
                id="FIN_PI_3",
                question=(
                    "Will I be able to purchase a house, land, vehicle, jewellery, or afford travel "
                    "for pleasure and when might these opportunities arise?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Prospects of Property"
            ),
            Question(
                id="FIN_PI_4",
                question=(
                    "What financial obstacles might I face and how can I overcome them?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Financial Challenges"
            )
        ]
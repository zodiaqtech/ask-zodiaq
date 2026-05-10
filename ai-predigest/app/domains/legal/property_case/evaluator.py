"""
Property Legal Dispute Evaluator – VEDIC-ONLY v2.0 (FIXED - FULL PARITY WITH FCC/FINANCE/CAREER)

FIXES FROM v1.0:
✅ Added _extract_lagna_info() - matches FCC/Finance/Career evaluator pattern
✅ Added lagna_info called in evaluate() and stored at top level in additional_data
✅ Added _create_property_suitability_matrix() - analogous to legal_suitability_matrix in FCC
✅ Added _log_result_breakdown() - matches Career evaluator pattern
✅ Fixed house 1 always included in all_relevant_houses (all_relevant_houses.add(1))
✅ Fixed _store_data_for_llm() - aligned dasha_context, timing_windows, dasha pass-through
✅ Fixed meta handling - consistent QueryMeta/dict normalization
✅ Fixed timing_windows_data fallback key logic - matches FCC/Finance/Career pattern
✅ Added strong_lords / weak_lords to analysis_summary (already present - kept)
✅ COMPLETE structural parity with FightingCourtCaseEvaluator v3.0

✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Property-specific house analysis (4th house prominence)
✔ Outcome analysis, Duration analysis, Risk analysis
✔ Property suitability matrix (NEW)
✔ Lagna lord analysis (NEW)
✔ Log result breakdown (NEW)
✔ Complete data storage for LLM

Key Houses for Property Legal Disputes:
- 4th: Land, property, real estate, immovable assets (PRIMARY)
- 6th: Litigation, disputes, enemies, legal battles
- 7th: Opponent, other party in dispute
- 8th: Hidden matters, inheritance issues, sudden events
- 9th: Legal proceedings, higher courts, justice, dharma
- 10th: Reputation, authority, government land records
- 11th: Gains, victory, favorable outcomes
- 12th: Losses, expenses, property loss

Karakas:
- Mars: Land, property (Bhoomi Karaka), courage, conflict
- Saturn: Real estate, boundaries, delays, karma
- Jupiter: Law, justice, expansion, favorable outcomes
- Sun: Government, authority, land records
- Venus: Comfort, luxury property, settlements
- Moon: Home, emotional attachment to property
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
from datetime import datetime

from app.domains.base import (
    BaseEvaluator,
    EvaluationResult,
    Question,
    QueryMeta,
    QueryType,
    EventPolarity,
    InterpretationGoal
)

from app.domains.excel_structure_config import get_houses_for_question
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
    logging.info("House lords analyzer available for Property Legal domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "property_legal"


class PropertyLegalDisputeEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Legal → Property Case

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Outcome likelihood assessment
    - Duration indicators
    - Risk and penalty analysis
    - Property-specific analysis (4th house / Mars Bhoomi Karaka focus)
    - Property suitability matrix (NEW)
    - Lagna lord analysis (NEW)
    - NO KP analysis (purely Vedic)

    Traditional Vedic Rules for Property Disputes:
    - 4th house strong = Property protection, favorable for owner
    - 4th lord well-placed = Land matters supported
    - Mars strong = Bhoomi Karaka supports property matters
    - 6th house strong = Ability to fight and win disputes
    - 7th house = The opponent in property litigation
    - 9th house strong + Jupiter well-placed = Favorable legal outcome
    - 11th house strong = Victory, gains from property dispute
    - 12th house afflicted = Risk of property loss
    - Saturn involved = Delays in property matters
    """

    domain = "Legal"
    subtopic = "Property Case"

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANINGS
    # ══════════════════════════════════════════════════════════════
    HOUSE_MEANINGS = {
        1:  "Self/Native",
        2:  "Immovable Assets",
        4:  "Property/Land",
        6:  "Litigation/Disputes",
        7:  "Opponent/Other Party",
        8:  "Hidden Issues/Inheritance",
        9:  "Justice/Law",
        10: "Authority/Government",
        11: "Victory/Gains",
        12: "Losses/Expenses",
    }

    # ══════════════════════════════════════════════════════════════
    # MAIN EVALUATION
    # ══════════════════════════════════════════════════════════════
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

        # ═══════════════════════════════════════════════════════════
        # STEP 0: Normalize Meta  [FIX: consistent with FCC/Finance/Career]
        # ═══════════════════════════════════════════════════════════
        meta = kwargs.get("meta")

        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        meta_query_type = meta.query_type if isinstance(meta, QueryMeta) else None
        question_text  = kwargs.get("question", "")
        sub_subdomain  = kwargs.get("sub_subdomain", "")

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Select Analysis Data (Vedic preferred)
        # ═══════════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses  = vedic_houses  if vedic_houses  else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════════
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses     = set(house_config["primary"])
            secondary_houses   = set(house_config["secondary"])
            all_relevant_houses = primary_houses | secondary_houses
            # FIX: Always include house 1 for lagna lord analysis (matches FCC/Finance/Career)
            all_relevant_houses.add(1)
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary:   {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning("No config for question, using fallback for Property Legal")
            # Default: 4th = property (PRIMARY), 6th = litigation, 7th = opponent
            # 9th = justice, 11th = victory, 12th = losses
            primary_houses      = {4, 6, 9, 11}
            secondary_houses    = {1, 7, 8, 10, 12}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("PROPERTY LEGAL DISPUTE EVALUATOR (VEDIC-ONLY v2.0 FIXED)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses:   {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Calculate Aspects
        # ═══════════════════════════════════════════════════════════
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Extract House Lords Data
        # ═══════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 4.5: Extract Lagna Information [NEW - matches FCC/Finance/Career]
        # ═══════════════════════════════════════════════════════════
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 5.5: Extract Timing Windows
        # [FIX: aligned fallback logic with FCC/Finance/Career patterns]
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            # Fallback key - matches FCC pattern
            if not timing_windows_list and "Property Case Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Property Case Timing"]
                logger.info(f"🔍 Using 'Property Case Timing' fallback key, found {len(timing_windows_list)} windows")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Property-Specific Analysis
        # ═══════════════════════════════════════════════════════════
        property_analysis = self._analyze_property_indicators(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Property analysis: {property_analysis.get('property_protection', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Vedic Outcome Analysis
        # ═══════════════════════════════════════════════════════════
        outcome_analysis = self._analyze_outcome_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info,
            property_analysis
        )

        logger.info(f"✅ Outcome analysis: {outcome_analysis.get('likelihood', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Duration Analysis
        # ═══════════════════════════════════════════════════════════
        duration_analysis = self._analyze_duration(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Duration indicated: {duration_analysis.get('duration_category', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Risk and Penalty Analysis
        # ═══════════════════════════════════════════════════════════
        risk_analysis = self._analyze_risks_and_penalties(
            analysis_planets,
            house_lords_info,
            house_aspects_info,
            property_analysis
        )

        logger.info(f"✅ Risk level: {risk_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9.5: Property Suitability Matrix [NEW - matches FCC pattern]
        # ═══════════════════════════════════════════════════════════
        property_matrix = self._create_property_suitability_matrix(
            outcome_analysis,
            duration_analysis,
            risk_analysis,
            property_analysis,
            lagna_info
        )
        result.additional_data[f"{DOMAIN_PREFIX}_suitability_matrix"] = property_matrix
        logger.info(f"✅ Property suitability matrix created with {len(property_matrix)} strategy types")

        # ═══════════════════════════════════════════════════════════
        # STEP 9.6: Timing Decision Gate [FIX: matches FCC pattern]
        # ═══════════════════════════════════════════════════════════
        logger.warning("🔎 TIMING GATE DEBUG -----------------------------")
        logger.warning(f"meta_query_type        = {meta_query_type}")
        logger.warning(f"QueryType.TIMING       = {QueryType.TIMING}")
        logger.warning(f"meta == TIMING ?       = {meta_query_type == QueryType.TIMING}")
        logger.warning(f"timing_windows_list len = {len(timing_windows_list) if timing_windows_list else 0}")
        logger.warning("🔎 END TIMING GATE DEBUG -------------------------")

        timing_windows_data = {}

        if meta_query_type == QueryType.TIMING and timing_windows_list:
            timing_windows_data = self._extract_timing_windows(timing_windows_list) or {}
            logger.info("✅ TIMING ENABLED (timing query type + windows present)")

            if timing_windows_data and timing_windows_data.get('has_timing'):
                best    = timing_windows_data.get('best_window', {})
                nearest = timing_windows_data.get('nearest_window', {})
                logger.warning(f"✅ TIMING WINDOWS EXTRACTED:")
                logger.warning(f"   🏆 BEST: {best.get('dasha','N/A')} ({best.get('start','N/A')} to {best.get('end','N/A')}) Score:{best.get('final_score',0):.1f}")
                logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha','N/A')} ({nearest.get('start','N/A')} to {nearest.get('end','N/A')}) Score:{nearest.get('final_score',0):.1f}")
        else:
            timing_windows_data = {"has_timing": False}
            logger.info("⛔ TIMING DISABLED (not a timing query or no windows)")

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Add Property Legal-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_property_legal_points(
            result,
            property_analysis,
            outcome_analysis,
            duration_analysis,
            risk_analysis
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 12: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            property_analysis,
            outcome_analysis,
            duration_analysis,
            risk_analysis,
            timing_windows_data,
            kwargs
        )

        # FIX: Store lagna_info at top level - matches FCC/Finance/Career
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # FIX: Log result breakdown - matches Career evaluator pattern
        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO EXTRACTION [NEW - matches FCC/Finance/Career exactly]
    # ══════════════════════════════════════════════════════════════
    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        """
        Extract lagna (ascendant) information from houses data.
        Matches FCC v3.0 / Finance / Career evaluator pattern exactly.
        """
        try:
            house_1 = next((h for h in houses if h.get("house") == 1), None)

            if not house_1:
                logger.warning("⚠️ House 1 not found - cannot determine lagna")
                return None

            lagna_sign = (
                house_1.get("sign") or
                house_1.get("start_rasi") or
                house_1.get("rasi") or
                ""
            )

            if not lagna_sign:
                logger.warning("⚠️ Lagna sign not found in house 1 data")
                return None

            lagna_lord_name = (
                house_1.get("sign_lord") or
                house_1.get("rashi_lord") or
                house_1.get("lord") or
                ""
            )

            if not lagna_lord_name:
                sign_lords = {
                    "Aries": "Mars",     "Taurus": "Venus",   "Gemini": "Mercury",
                    "Cancer": "Moon",    "Leo": "Sun",         "Virgo": "Mercury",
                    "Libra": "Venus",    "Scorpio": "Mars",    "Sagittarius": "Jupiter",
                    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                }
                lagna_lord_name = sign_lords.get(lagna_sign, "")

            lagna_lord = normalize_planet_name(lagna_lord_name)

            if not lagna_lord:
                logger.warning(f"⚠️ Could not determine lagna lord for {lagna_sign}")
                return None

            lagna_lord_data   = planets.get(lagna_lord, {})
            lagna_lord_house  = lagna_lord_data.get("house")
            lagna_lord_sign   = lagna_lord_data.get("sign", "")
            lagna_lord_degree = (
                lagna_lord_data.get("full_degree") or
                lagna_lord_data.get("global_degree") or
                lagna_lord_data.get("degree") or
                0
            )

            lagna_lord_dignity = "Unknown"
            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity  = None

                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(lagna_lord)

                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, 'value') else str(dignity)
                except Exception:
                    pass

            return {
                "lagna_sign":        lagna_sign,
                "lagna_lord":        lagna_lord,
                "lagna_lord_house":  lagna_lord_house,
                "lagna_lord_sign":   lagna_lord_sign,
                "lagna_lord_degree": lagna_lord_degree,
                "lagna_lord_dignity": lagna_lord_dignity,
            }

        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    # ══════════════════════════════════════════════════════════════
    # PROPERTY SUITABILITY MATRIX [NEW - matches FCC _create_legal_suitability_matrix]
    # ══════════════════════════════════════════════════════════════
    def _create_property_suitability_matrix(
        self,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risk_analysis: Dict,
        property_analysis: Dict,
        lagna_info: Optional[Dict] = None
    ) -> Dict[str, Dict]:
        """
        Create property legal strategy suitability matrix.

        Analogous to _create_legal_suitability_matrix in FightingCourtCaseEvaluator v3.0.
        Provides LLM with structured guidance on which strategies are most appropriate
        for a property dispute.
        """
        matrix = {}

        outcome        = outcome_analysis.get("likelihood", "UNCERTAIN")
        outcome_score  = outcome_analysis.get("score", 50)
        duration       = duration_analysis.get("duration_category", "MODERATE")
        risk_level     = risk_analysis.get("risk_level", "MODERATE")
        prop_protect   = property_analysis.get("property_protection", "MODERATE")
        mars_strength  = property_analysis.get("mars_strength", "MODERATE")
        h4_strength    = property_analysis.get("fourth_house_strength", "MODERATE")

        # ═══════════════════════════════════════════════════════════
        # 1. PURSUE FULL LITIGATION
        # ═══════════════════════════════════════════════════════════
        if outcome in ("FAVORABLE",) and prop_protect in ("STRONG", "MODERATE_GOOD"):
            rating = "HIGH"
            reason = f"Favorable outlook ({outcome}) + strong property protection → pursue full litigation"
        elif outcome == "UNCERTAIN" and risk_level in ("LOW", "VERY_LOW"):
            rating = "MODERATE"
            reason = "Uncertain outcome but low risk → litigation viable with experienced counsel"
        elif outcome in ("CHALLENGING", "UNFAVORABLE"):
            rating = "LOW"
            reason = f"Challenging outlook ({outcome}) → consider alternatives before full court battle"
        else:
            rating = "MODERATE"
            reason = "Mixed indicators → assess documentary evidence before proceeding"

        matrix["Pursue Full Litigation"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 2. OUT-OF-COURT SETTLEMENT
        # ═══════════════════════════════════════════════════════════
        if outcome in ("CHALLENGING", "UNFAVORABLE") or risk_level in ("HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Challenging outcome or {risk_level} risk → out-of-court settlement recommended"
        elif duration in ("VERY_LONG", "LONG") and risk_level == "MODERATE":
            rating = "HIGH"
            reason = f"Very long expected duration + moderate risk → settlement saves time and resources"
        elif outcome == "FAVORABLE" and prop_protect == "STRONG":
            rating = "LOW"
            reason = "Strong position → press advantage in court rather than settling"
        else:
            rating = "MODERATE"
            reason = "Settlement is a viable risk-mitigation option for property disputes"

        matrix["Out-of-Court Settlement"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 3. MEDIATION / ARBITRATION
        # ═══════════════════════════════════════════════════════════
        if duration in ("VERY_LONG", "LONG"):
            rating = "HIGH"
            reason = f"Long expected duration ({duration}) → mediation is cost and time effective"
        elif risk_level in ("HIGH", "VERY_HIGH"):
            rating = "MODERATE"
            reason = f"{risk_level} risk level → explore mediation to cap potential losses"
        else:
            rating = "MODERATE"
            reason = "Mediation can resolve property disputes faster than court proceedings"

        matrix["Mediation / Arbitration"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 4. STRENGTHEN DOCUMENTATION AND TITLE
        # ═══════════════════════════════════════════════════════════
        if h4_strength == "WEAK" or risk_level in ("HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Weak 4th house ({h4_strength}) or {risk_level} risk → invest in title verification and documentation"
        elif mars_strength == "WEAK":
            rating = "HIGH"
            reason = "Weak Mars (Bhoomi Karaka) → reinforce property documentation to compensate"
        else:
            rating = "MODERATE"
            reason = "Solid documentation always strengthens property dispute position"

        matrix["Strengthen Documentation and Title"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 5. APPEAL TO HIGHER COURT / REVENUE TRIBUNAL
        # ═══════════════════════════════════════════════════════════
        if outcome == "CHALLENGING" and outcome_score >= 40:
            rating = "MODERATE"
            reason = "Challenging but not hopeless — appeal may yield better result in higher forum"
        elif outcome in ("FAVORABLE",) and h4_strength in ("STRONG", "MODERATE_GOOD"):
            rating = "MODERATE"
            reason = "Favorable indicators — keep appeal as option if lower court rules adversely"
        else:
            rating = "LOW"
            reason = "Current indicators do not strongly support appeal strategy"

        matrix["Appeal to Higher Court / Revenue Tribunal"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 6. DELAY / WAIT FOR BETTER TIMING
        # ═══════════════════════════════════════════════════════════
        if outcome in ("UNCERTAIN", "CHALLENGING") and risk_level in ("MODERATE", "HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Uncertain/challenging + {risk_level} risk → wait for better dasha support"
        elif outcome == "FAVORABLE" and duration in ("SHORT", "VERY_SHORT"):
            rating = "LOW"
            reason = "Favorable indicators + short duration — no reason to delay proceedings"
        else:
            rating = "MODERATE"
            reason = "Timing strategy depends on current dasha — consult timing windows"

        matrix["Delay Strategy (Wait for Better Dasha)"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 7. ENGAGE EXPERIENCED PROPERTY LAWYER
        # ═══════════════════════════════════════════════════════════
        if risk_level in ("HIGH", "VERY_HIGH") or outcome_score < 50:
            rating = "HIGH"
            reason = f"{risk_level.title()} risk / below-average outcome → experienced property counsel essential"
        elif mars_strength == "WEAK" and h4_strength == "WEAK":
            rating = "HIGH"
            reason = "Weak Bhoomi Karaka + weak 4th house → strong legal representation critical"
        else:
            rating = "MODERATE"
            reason = "Qualified property lawyer always advisable in land and real estate disputes"

        matrix["Engage Experienced Property Lawyer"] = {"rating": rating, "vedic_reasoning": reason}

        return matrix

    # ══════════════════════════════════════════════════════════════
    # LOG RESULT BREAKDOWN [NEW - matches Career/FCC evaluator pattern]
    # ══════════════════════════════════════════════════════════════
    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging. Matches FCC/Career evaluator pattern."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")

        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")

        summary = ad.get(f"{DOMAIN_PREFIX}_analysis_summary", {})
        if summary:
            logger.info(f"PROPERTY PROTECTION: {summary.get('property_protection')}")
            logger.info(f"OUTCOME: {summary.get('outcome_likelihood')}")
            logger.info(f"DURATION: {summary.get('duration_category')}")
            logger.info(f"RISK: {summary.get('risk_level')}")
            logger.info(f"4TH HOUSE: {summary.get('fourth_house_strength')}")
            logger.info(f"MARS: {summary.get('mars_strength')}")

        timing_data = ad.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        logger.info(f"TIMING: has_timing={timing_data.get('has_timing', False)}")

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION [NEW - matches FCC pattern exactly]
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow objects — matches FCC/Finance/Career pattern.
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}

        try:
            def get_attr(obj, key, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            def window_to_dict(w):
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w
                result = {
                    'start':          get_attr(w, 'start'),
                    'end':            get_attr(w, 'end'),
                    'dasha':          get_attr(w, 'dasha'),
                    'score':          get_attr(w, 'score'),
                    'transit_score':  get_attr(w, 'transit_score'),
                    'final_score':    get_attr(w, 'final_score'),
                    'age_at_start':   get_attr(w, 'age_at_start'),
                    'is_overall_best':        get_attr(w, 'is_overall_best', False),
                    'is_earliest_favorable':  get_attr(w, 'is_earliest_favorable', False),
                }
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar',
                                    'md', 'ad', 'pd', 'maha', 'antara', 'paryantar']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                return result

            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")

            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

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

            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]

            result_dict = {
                'best_window':    best_window,
                'nearest_window': nearest_window,
                'all_favorable':  all_favorable,
                'has_timing':     True
            }

            logger.info("✅ Timing extraction SUCCESSFUL")
            if best_window:
                logger.info(f"   Best: {best_window.get('dasha','N/A')} Score:{best_window.get('final_score',0)}")
            if nearest_window:
                logger.info(f"   Nearest: {nearest_window.get('dasha','N/A')} Score:{nearest_window.get('final_score',0)}")

            return result_dict

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    # ══════════════════════════════════════════════════════════════
    # PROPERTY-SPECIFIC ANALYSIS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _analyze_property_indicators(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze property-specific indicators using Vedic principles."""
        analysis = {
            "property_protection": "MODERATE",
            "property_score": 50,
            "fourth_house_strength": "MODERATE",
            "mars_strength": "MODERATE",
            "favorable_factors": [],
            "unfavorable_factors": [],
            "property_hints": []
        }

        score = 50

        # ── 4th HOUSE (Most Important for Property) ────────────────
        h4_info = house_lords_info.get(4, {})
        if h4_info:
            h4_strength  = h4_info.get("lord_strength_score", 50)
            h4_lord      = h4_info.get("lord", "")
            h4_lord_house = h4_info.get("lord_in_house")

            if h4_strength >= 70:
                score += 15
                analysis["fourth_house_strength"] = "STRONG"
                analysis["favorable_factors"].append(
                    f"4th lord {h4_lord} is strong ({h4_strength}/100) - property matters well supported"
                )
            elif h4_strength >= 50:
                analysis["fourth_house_strength"] = "MODERATE"
                analysis["property_hints"].append(
                    f"4th lord {h4_lord} has moderate strength - balanced property indications"
                )
            else:
                score -= 12
                analysis["fourth_house_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    f"4th lord {h4_lord} is weak ({h4_strength}/100) - property protection needs attention"
                )

            if h4_lord_house in [1, 4, 5, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"4th lord in house {h4_lord_house} - favorable placement for property"
                )
            elif h4_lord_house in [6, 8, 12]:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"4th lord in house {h4_lord_house} - challenging placement for property matters"
                )

        # ── MARS (Bhoomi Karaka) ───────────────────────────────────
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            mars_sign  = mars_data.get("sign", "")

            mars_strong_signs = ["Aries", "Scorpio", "Capricorn"]
            mars_weak_signs   = ["Cancer", "Taurus", "Libra"]

            if mars_sign in mars_strong_signs:
                score += 10
                analysis["mars_strength"] = "STRONG"
                analysis["favorable_factors"].append(
                    f"Mars (Bhoomi Karaka) in {mars_sign} - strong support for land matters"
                )
            elif mars_sign in mars_weak_signs:
                score -= 8
                analysis["mars_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    f"Mars (Bhoomi Karaka) in {mars_sign} - land karaka weakened"
                )
            else:
                analysis["mars_strength"] = "MODERATE"

            if mars_house == 4:
                analysis["property_hints"].append(
                    "Mars in 4th house - strong connection to property, but may indicate disputes"
                )

            h4_aspects = house_aspects_info.get(4, {})
            if "Mars" in h4_aspects.get("malefic_aspects", []):
                analysis["property_hints"].append(
                    "Mars aspects 4th house - fighting spirit for property, but also conflict"
                )

        # ── SATURN ────────────────────────────────────────────────
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house == 4:
                analysis["property_hints"].append(
                    "Saturn in 4th house - delays but eventual resolution with patience"
                )
            h4_aspects = house_aspects_info.get(4, {})
            if "Saturn" in h4_aspects.get("malefic_aspects", []):
                score -= 5
                analysis["property_hints"].append(
                    "Saturn aspects 4th house - delays and obstacles in property matters"
                )

        # ── BENEFIC ASPECTS ON 4th ────────────────────────────────
        h4_aspects = house_aspects_info.get(4, {})
        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 4th house - divine protection for property"
            )
        if "Venus" in h4_aspects.get("benefic_aspects", []):
            score += 5
            analysis["favorable_factors"].append(
                "Venus aspects 4th house - property value and comfort protected"
            )

        # ── RAHU/KETU ON 4th ──────────────────────────────────────
        rahu_data = planets.get("Rahu", {})
        ketu_data = planets.get("Ketu", {})

        if rahu_data and rahu_data.get("house") == 4:
            score -= 10
            analysis["unfavorable_factors"].append(
                "Rahu in 4th house - confusion, disputes, or unconventional property issues"
            )
        if ketu_data and ketu_data.get("house") == 4:
            score -= 5
            analysis["property_hints"].append(
                "Ketu in 4th house - detachment from property or ancestral land issues"
            )

        # ── 2nd HOUSE (Immovable Assets) ──────────────────────────
        h2_info = house_lords_info.get(2, {})
        if h2_info and h2_info.get("lord_strength_score", 50) >= 70:
            score += 5
            analysis["favorable_factors"].append("2nd lord strong - immovable assets protected")

        score = max(0, min(100, score))
        analysis["property_score"] = score

        if score >= 70:
            analysis["property_protection"] = "STRONG"
        elif score >= 55:
            analysis["property_protection"] = "MODERATE_GOOD"
        elif score >= 45:
            analysis["property_protection"] = "MODERATE"
        elif score >= 30:
            analysis["property_protection"] = "WEAK"
        else:
            analysis["property_protection"] = "VERY_WEAK"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # OUTCOME PROSPECTS ANALYSIS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _analyze_outcome_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        property_analysis: Dict
    ) -> Dict:
        """Analyze legal outcome prospects for property dispute."""
        analysis = {
            "likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "strategic_hints": []
        }

        score = property_analysis.get("property_score", 50)

        # 6th HOUSE (Litigation Ability)
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            if h6_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is strong ({h6_strength}/100) - good litigation ability"
                )
            elif h6_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is weak - may struggle in legal battles"
                )

        # 9th HOUSE (Justice)
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            if h9_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is strong - justice and law favor you"
                )
            elif h9_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is weak - legal proceedings may be challenging"
                )

        # 11th HOUSE (Victory)
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            if h11_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is strong - victory supported"
                )
            elif h11_strength < 40:
                score -= 6
                analysis["unfavorable_factors"].append(
                    "11th lord weak - achieving desired outcome requires extra effort"
                )

        # 7th vs 1st (Opponent vs Self)
        h7_info = house_lords_info.get(7, {})
        h1_info = house_lords_info.get(1, {})
        if h7_info and h1_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            h1_strength = h1_info.get("lord_strength_score", 50)
            if h7_strength > h1_strength + 15:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "Opponent's significator stronger than yours - may face strong opposition"
                )
                analysis["strategic_hints"].append(
                    "Consider out-of-court settlement to avoid prolonged battle"
                )
            elif h1_strength > h7_strength + 15:
                score += 8
                analysis["favorable_factors"].append(
                    "Your significator stronger than opponent - advantageous position"
                )

        # 12th HOUSE (Losses)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength   = h12_info.get("lord_strength_score", 50)
            h12_lord_house = h12_info.get("lord_in_house")
            if h12_strength >= 70:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "12th lord strong - potential for expenses and losses"
                )
            if h12_lord_house == 4:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "12th lord in 4th house - risk of property loss indicated"
                )
                analysis["strategic_hints"].append(
                    "Take extra precautions to protect property documents"
                )

        # JUPITER
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 4, 5, 9, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine grace supports your case"
                )
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - may face challenges in getting justice"
                )

        h4_aspects = house_aspects_info.get(4, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 4th house - property protected by divine grace"
            )
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - strong support for justice"
            )

        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 70:
            analysis["likelihood"] = "FAVORABLE"
        elif score >= 55:
            analysis["likelihood"] = "MODERATELY_FAVORABLE"
        elif score >= 45:
            analysis["likelihood"] = "UNCERTAIN"
        elif score >= 30:
            analysis["likelihood"] = "CHALLENGING"
        else:
            analysis["likelihood"] = "UNFAVORABLE"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DURATION ANALYSIS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _analyze_duration(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze expected duration of property legal proceedings."""
        analysis = {
            "duration_category": "MODERATE",
            "duration_score": 55,
            "delay_factors": [],
            "speed_factors": [],
            "duration_hints": []
        }

        duration_score = 55  # Property cases tend to be longer

        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [4, 6, 7, 9, 10]:
                duration_score += 18
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays in property case"
                )
            if saturn_data.get("is_retro") or saturn_data.get("is_retrograde"):
                duration_score += 10
                analysis["delay_factors"].append(
                    "Saturn retrograde - prolonged proceedings, may revisit old issues"
                )

        h4_aspects = house_aspects_info.get(4, {})
        h6_aspects = house_aspects_info.get(6, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Saturn" in h4_aspects.get("malefic_aspects", []):
            duration_score += 12
            analysis["delay_factors"].append("Saturn aspects 4th house - property matters significantly delayed")
        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            duration_score += 10
            analysis["delay_factors"].append("Saturn aspects 9th house - legal proceedings delayed")

        h4_info = house_lords_info.get(4, {})
        if h4_info and h4_info.get("lord_is_retrograde"):
            duration_score += 10
            analysis["delay_factors"].append(
                f"4th lord {h4_info.get('lord')} retrograde - property case may drag on"
            )

        h6_info = house_lords_info.get(6, {})
        if h6_info and h6_info.get("lord_is_retrograde"):
            duration_score += 8
            analysis["delay_factors"].append("6th lord retrograde - litigation process slowed")

        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") in [4, 6, 7, 9]:
            duration_score += 10
            analysis["delay_factors"].append(
                f"Rahu in house {rahu_data.get('house')} - unexpected complications may arise"
            )

        ketu_data = planets.get("Ketu", {})
        if ketu_data and ketu_data.get("house") in [4, 6, 9]:
            duration_score += 5
            analysis["duration_hints"].append("Ketu's influence may bring sudden twists in proceedings")

        mercury_data = planets.get("Mercury", {})
        if mercury_data and mercury_data.get("house") in [1, 5, 9, 11]:
            duration_score -= 8
            analysis["speed_factors"].append("Mercury well-placed - documentation and proceedings smoother")

        for h_num in [4, 6, 9, 11]:
            if "Jupiter" in house_aspects_info.get(h_num, {}).get("benefic_aspects", []):
                duration_score -= 5
                analysis["speed_factors"].append(f"Jupiter aspects house {h_num} - may help expedite matters")
                break

        duration_score = max(0, min(100, duration_score))
        analysis["duration_score"] = duration_score

        if duration_score >= 75:
            analysis["duration_category"] = "VERY_LONG"
            analysis["duration_hints"].append("Property disputes often take years - prepare for extended timeline")
        elif duration_score >= 60:
            analysis["duration_category"] = "LONG"
            analysis["duration_hints"].append("Case may take considerable time - patience required")
        elif duration_score >= 45:
            analysis["duration_category"] = "MODERATE"
            analysis["duration_hints"].append("Moderate timeline expected for property legal proceedings")
        elif duration_score >= 30:
            analysis["duration_category"] = "SHORT"
            analysis["duration_hints"].append("Relatively quicker resolution possible for property case")
        else:
            analysis["duration_category"] = "VERY_SHORT"
            analysis["duration_hints"].append("Quick settlement or resolution indicated")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISK AND PENALTY ANALYSIS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks_and_penalties(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        property_analysis: Dict
    ) -> Dict:
        """Analyze potential risks and penalties for property dispute."""
        analysis = {
            "risk_level": "MODERATE",
            "risk_score": 50,
            "risk_factors": [],
            "penalty_indicators": [],
            "mitigation_hints": [],
            "areas_of_concern": []
        }

        risk_score = 50

        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_lord_house = h12_info.get("lord_in_house")
            h12_strength   = h12_info.get("lord_strength_score", 50)
            if h12_lord_house == 4:
                risk_score += 18
                analysis["risk_factors"].append("12th lord in 4th house - significant risk of property loss")
                analysis["areas_of_concern"].append("Property ownership at risk")
                analysis["mitigation_hints"].append("Ensure all property documents are secure and legally verified")
            if h12_strength >= 70:
                risk_score += 8
                analysis["penalty_indicators"].append("12th lord strong - potential for substantial losses/expenses")

        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            h8_strength   = h8_info.get("lord_strength_score", 50)
            if h8_lord_house == 4:
                risk_score += 15
                analysis["risk_factors"].append(
                    "8th lord in 4th house - hidden issues with property title or inheritance"
                )
                analysis["areas_of_concern"].append("Title defects or inheritance complications")
            if h8_lord_house in [1, 10]:
                risk_score += 10
                analysis["risk_factors"].append(
                    f"8th lord in house {h8_lord_house} - hidden risks to {'self' if h8_lord_house == 1 else 'reputation'}"
                )

        if property_analysis.get("mars_strength") == "WEAK":
            risk_score += 10
            analysis["risk_factors"].append("Mars (Bhoomi Karaka) weak - land matters face inherent challenges")

        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house == 4:
                risk_score += 15
                analysis["risk_factors"].append("Rahu in 4th house - risk of fraud, forgery, or title disputes")
                analysis["areas_of_concern"].append("Document authenticity concerns")
                analysis["mitigation_hints"].append("Verify all property documents thoroughly")
            elif rahu_house in [8, 12]:
                risk_score += 10
                analysis["risk_factors"].append(
                    f"Rahu in house {rahu_house} - unexpected complications or hidden enemies"
                )

        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house == 12:
                risk_score += 12
                analysis["risk_factors"].append("Saturn in 12th house - risk of significant losses or penalties")
                analysis["mitigation_hints"].append("Seek strong legal counsel immediately")
            elif saturn_house == 4:
                risk_score += 8
                analysis["risk_factors"].append("Saturn in 4th house - property matters face obstacles and delays")

        h4_aspects = house_aspects_info.get(4, {})
        malefics_on_4 = h4_aspects.get("malefic_aspects", [])
        if len(malefics_on_4) >= 2:
            risk_score += 12
            analysis["risk_factors"].append(
                f"Multiple malefics ({', '.join(malefics_on_4)}) affect 4th house - property at risk"
            )
            analysis["areas_of_concern"].append("Property protection critical")

        malefics_on_10 = house_aspects_info.get(10, {}).get("malefic_aspects", [])
        if "Rahu" in malefics_on_10 or "Saturn" in malefics_on_10:
            risk_score += 8
            analysis["penalty_indicators"].append("Government or authority-related complications possible")
            analysis["areas_of_concern"].append("Land records or government approvals")

        if "Jupiter" in h4_aspects.get("benefic_aspects", []):
            risk_score -= 10
            analysis["mitigation_hints"].append("Jupiter's grace on 4th house provides protection for property")
        if "Jupiter" in house_aspects_info.get(9, {}).get("benefic_aspects", []):
            risk_score -= 8
            analysis["mitigation_hints"].append("Jupiter's aspect on 9th - dharmic protection in legal matters")

        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 75:
            analysis["risk_level"] = "VERY_HIGH"
        elif risk_score >= 60:
            analysis["risk_level"] = "HIGH"
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
        elif risk_score >= 25:
            analysis["risk_level"] = "LOW"
        else:
            analysis["risk_level"] = "VERY_LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
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
        """Extract house lord information for relevant houses only."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue

            lord_name = (
                h.get("sign_lord") or h.get("rashi_lord") or h.get("lord") or ""
            )

            if not lord_name:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                if sign:
                    sign_lords = {
                        "Aries": "Mars",     "Taurus": "Venus",   "Gemini": "Mercury",
                        "Cancer": "Moon",    "Leo": "Sun",         "Virgo": "Mercury",
                        "Libra": "Venus",    "Scorpio": "Mars",    "Sagittarius": "Jupiter",
                        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                    }
                    lord_name = sign_lords.get(sign, "")

            normalized_lord = normalize_planet_name(lord_name)

            if not normalized_lord:
                logger.warning(f"No lord found for house {house_num}")
                continue

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"No data found for lord {normalized_lord}")
                continue

            lord_house   = lord_data.get("house")
            lord_sign    = lord_data.get("sign", "")
            lord_degree  = (
                lord_data.get("full_degree") or
                lord_data.get("global_degree") or
                lord_data.get("degree") or 0
            )
            lord_is_combust   = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)

            lord_dignity       = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity  = analyzer._get_dignity(normalized_lord, lord_sign, lord_degree)
                    lord_dignity = dignity.value
                    if dignity:
                        lord_strength_score = self._calculate_lord_strength(normalized_lord, lord_data, dignity)
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")

            priority         = "primary" if house_num in primary_houses else "secondary"
            planets_in_house = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]
            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""

            house_lords_info[house_num] = {
                "lord":               normalized_lord,
                "lord_in_house":      lord_house,
                "lord_in_sign":       lord_sign,
                "lord_degree":        lord_degree,
                "lord_is_combust":    lord_is_combust,
                "lord_is_retrograde": lord_is_retrograde,
                "lord_dignity":       lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority":           priority,
                "planets_in_house":   planets_in_house,
                "house_sign":         house_sign,
            }

        return house_lords_info

    # ══════════════════════════════════════════════════════════════
    # ASPECTS EXTRACTION  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
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

    # ══════════════════════════════════════════════════════════════
    # STRENGTH CALCULATION  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(self, planet_name: str, planet_data: dict, dignity=None) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, 'value') else str(dignity).upper()
            dignity_scores = {
                "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
                "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0
            }
            score = dignity_scores.get(dignity_str, 50)

        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30

        degree = (
            planet_data.get("full_degree") or
            planet_data.get("global_degree") or
            planet_data.get("degree") or 15
        )
        if degree < 5 or degree > 25:
            score -= 10

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        return self.HOUSE_MEANINGS.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
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

            info    = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            lord     = info["lord"]
            dignity  = info["lord_dignity"]
            strength = info["lord_strength_score"]

            point_parts = [
                f"⭐ House {house_num} ({self._get_house_meaning(house_num)}):",
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

            result.add_point(" ".join(point_parts))

    # ══════════════════════════════════════════════════════════════
    # ADD PROPERTY LEGAL-SPECIFIC POINTS  (unchanged from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _add_property_legal_points(
        self,
        result: EvaluationResult,
        property_analysis: Dict,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risk_analysis: Dict
    ):
        """Add property legal-specific points to result."""
        result.add_point(
            f"🏠 Property Protection: {property_analysis.get('property_protection','MODERATE')} "
            f"(Score: {property_analysis.get('property_score',50)}/100)"
        )
        result.add_point(
            f"⚖️ Outcome Likelihood: {outcome_analysis.get('likelihood','UNCERTAIN')} "
            f"(Score: {outcome_analysis.get('score',50)}/100)"
        )
        result.add_point(
            f"⏰ Expected Duration: {duration_analysis.get('duration_category','MODERATE')}"
        )
        result.add_point(
            f"🚨 Risk Level: {risk_analysis.get('risk_level','MODERATE')} "
            f"(Score: {risk_analysis.get('risk_score',50)}/100)"
        )
        result.add_point(
            f"🏡 4th House Strength: {property_analysis.get('fourth_house_strength','MODERATE')}"
        )
        result.add_point(
            f"♂️ Mars (Bhoomi Karaka): {property_analysis.get('mars_strength','MODERATE')}"
        )

        for factor in property_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in outcome_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in property_analysis.get("unfavorable_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        for factor in risk_analysis.get("risk_factors", [])[:2]:
            result.add_point(f"🚨 {factor}")

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # [FIX: aligned with FCC/Finance/Career - dasha_context, timing_windows, dasha pass-through]
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        property_analysis: dict,
        outcome_analysis: dict,
        duration_analysis: dict,
        risk_analysis: dict,
        timing_windows_data: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

        # Extract dasha context from kwargs - matches FCC/Finance/Career
        current_dasha   = kwargs.get("current_dasha")
        dasha_timeline  = kwargs.get("dasha_timeline")
        transit_summary = kwargs.get("transit_summary")
        age_context     = kwargs.get("age_context")
        meta            = kwargs.get("meta")

        # FIX: consistent meta_query_type extraction - matches FCC/Finance/Career
        meta_query_type = None
        if meta:
            if isinstance(meta, QueryMeta):
                meta_query_type = meta.query_type
            elif isinstance(meta, dict):
                meta_query_type = QueryType[meta.get("type", "NON_TIMING")]

        result.additional_data.update({
            # House configuration
            f"{DOMAIN_PREFIX}_house_config": {
                "primary":   sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source":    house_config.get("source") if house_config else "fallback"
            },

            # House lords and aspects (FULL data)
            f"{DOMAIN_PREFIX}_house_lords":   house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            # Domain-specific analyses
            f"{DOMAIN_PREFIX}_property_analysis": property_analysis,
            f"{DOMAIN_PREFIX}_outcome_analysis":  outcome_analysis,
            f"{DOMAIN_PREFIX}_duration_analysis": duration_analysis,
            f"{DOMAIN_PREFIX}_risk_analysis":     risk_analysis,

            # Analysis summary
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed":  len(house_lords_info),
                "primary_houses_count":   len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "property_protection":    property_analysis.get("property_protection", "MODERATE"),
                "property_score":         property_analysis.get("property_score", 50),
                "fourth_house_strength":  property_analysis.get("fourth_house_strength", "MODERATE"),
                "mars_strength":          property_analysis.get("mars_strength", "MODERATE"),
                "outcome_likelihood":     outcome_analysis.get("likelihood", "UNCERTAIN"),
                "outcome_score":          outcome_analysis.get("score", 50),
                "duration_category":      duration_analysis.get("duration_category", "MODERATE"),
                "risk_level":             risk_analysis.get("risk_level", "MODERATE"),
                "risk_score":             risk_analysis.get("risk_score", 50),
                # Already present in v1.0 - kept
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                ),
            },

            # Dasha pass-through - matches FCC/Finance/Career
            f"{DOMAIN_PREFIX}_current_dasha":   current_dasha,
            f"{DOMAIN_PREFIX}_dasha_timeline":  dasha_timeline,

            # Optional context
            f"{DOMAIN_PREFIX}_transit_summary": transit_summary,
            f"{DOMAIN_PREFIX}_age_context":     age_context,
        })

        # Store timing windows - matches FCC/Finance/Career exactly
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {DOMAIN_PREFIX}_timing_windows")
            if timing_windows_data.get('best_window'):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha','N/A')}")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}
            logger.warning("❌ NO TIMING WINDOWS TO STORE")

        # Dasha context for prompt builder - matches FCC/Career pattern
        if meta_query_type == QueryType.TIMING and timing_windows_data.get("has_timing"):
            dasha_context = {
                "mode": "timing",
                "reference": {
                    "best":    timing_windows_data.get("best_window"),
                    "nearest": timing_windows_data.get("nearest_window"),
                }
            }
        elif current_dasha:
            dasha_context = {
                "mode": "current",
                "reference": current_dasha
            }
        else:
            dasha_context = {
                "mode": "none",
                "reference": None
            }

        result.additional_data[f"{DOMAIN_PREFIX}_dasha_context"] = dasha_context

        logger.info(
            f"📦 STORED | property={property_analysis.get('property_protection')} | "
            f"outcome={outcome_analysis.get('likelihood')} | "
            f"duration={duration_analysis.get('duration_category')} | "
            f"risk={risk_analysis.get('risk_level')} | "
            f"timing={timing_windows_data.get('has_timing')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="PROPERTY_LEGAL_MAIN",
                question=(
                    "What does astrology reveal about the outcome, duration, "
                    "risks and potential penalties related to my land or property dispute?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Property Legal Dispute"
            )
        ]
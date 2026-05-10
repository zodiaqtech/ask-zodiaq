"""
Legal Business Dispute Evaluator – VEDIC-ONLY v2.0 (FIXED - FULL PARITY WITH PROPERTY/FCC/FINANCE/CAREER)

FIXES FROM v1.0:
✅ Added _extract_lagna_info()             - matches PropertyLegal/FCC/Finance/Career pattern
✅ Added lagna_info in evaluate() + stored at top level in additional_data
✅ Added _create_legal_suitability_matrix() - analogous to property_suitability_matrix
✅ Added _log_result_breakdown()            - matches Career/Property evaluator pattern
✅ Added _extract_timing_windows()          - matches FCC/Finance/Career pattern exactly
✅ Added _analyze_business_indicators()     - domain-specific (partnership, contracts, regulatory)
✅ Fixed house 1 always included in all_relevant_houses
✅ Fixed STEP 4.5 (lagna), 5.5 (timing windows), 9.5 (matrix), 9.6 (timing gate)
✅ Fixed _store_data_for_llm() - dasha_context, timing_windows, lagna, pass-through fields
✅ Fixed meta dict→QueryMeta conversion (QueryType[] lookup)
✅ Added HOUSE_MEANINGS class-level dict
✅ Added strong_lords / weak_lords in analysis_summary (already present - kept)
✅ COMPLETE structural parity with PropertyLegalDisputeEvaluator v2.0

✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Business-specific house analysis (6th + 7th + 10th prominence)
✔ Outcome analysis, Duration analysis, Risk analysis
✔ Business legal suitability matrix (NEW)
✔ Lagna lord analysis (NEW)
✔ Log result breakdown (NEW)
✔ Complete data storage for LLM

Key Houses for Legal Business Disputes:
- 6th:  Litigation, disputes, enemies, legal battles
- 7th:  Partners, opponents, the other party in dispute
- 8th:  Hidden matters, penalties, losses, investigations
- 9th:  Legal proceedings, higher courts, justice, dharma
- 10th: Reputation, career impact, authority, government
- 11th: Gains, victory, favorable outcomes
- 12th: Losses, expenses, imprisonment, settlements

Karakas:
- Jupiter: Law, justice, judges, dharma, favorable outcomes
- Saturn:  Delays, legal processes, punishment, karma
- Mars:    Aggression, conflict, litigation energy
- Sun:     Government, authority, power in legal matters
- Mercury: Documents, contracts, communication, evidence
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
    logging.info("House lords analyzer available for Legal Business domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "legal_business"


class LegalBusinessDisputeEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Legal → Legal Issue in Business

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Business-specific indicators (partnership, contracts, regulatory)
    - Outcome likelihood assessment
    - Duration indicators
    - Risk and penalty analysis
    - Business legal suitability matrix (NEW)
    - Lagna lord analysis (NEW)
    - Log result breakdown (NEW)
    - NO KP analysis (purely Vedic)

    Traditional Vedic Rules for Legal Business Disputes:
    - 6th house strong = Ability to fight and overcome enemies/opponents
    - 7th house = The opponent / business partner in litigation
    - 9th house strong + Jupiter well-placed = Favorable legal outcome
    - 10th house = Reputation impact, dealing with authorities
    - 11th house strong = Victory, gains from litigation
    - 12th house afflicted = Losses, expenses, potential confinement
    - Saturn involved = Delays in legal proceedings
    - Mercury strong = Good for contracts, documentation, evidence
    """

    domain = "Legal"
    subtopic = "Legal Issue in Business"

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANINGS
    # ══════════════════════════════════════════════════════════════
    HOUSE_MEANINGS = {
        1:  "Self/Native",
        2:  "Finances/Business Assets",
        3:  "Contracts/Communication",
        6:  "Litigation/Disputes",
        7:  "Opponent/Partner",
        8:  "Hidden Matters/Penalties",
        9:  "Justice/Law",
        10: "Reputation/Authority",
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
        # STEP 0: Normalize Meta  [FIX: dict→QueryMeta with QueryType[] lookup]
        # ═══════════════════════════════════════════════════════════
        meta = kwargs.get("meta")

        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        meta_query_type = meta.query_type if isinstance(meta, QueryMeta) else None
        question_text   = kwargs.get("question", "")
        sub_subdomain   = kwargs.get("sub_subdomain", "")

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
            primary_houses      = set(house_config["primary"])
            secondary_houses    = set(house_config["secondary"])
            all_relevant_houses = primary_houses | secondary_houses
            # FIX: Always include house 1 for lagna lord analysis
            all_relevant_houses.add(1)
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary:   {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning("No config for question, using fallback for Legal/Business")
            primary_houses      = {6, 7, 9, 11}
            secondary_houses    = {1, 8, 10, 12}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("LEGAL BUSINESS DISPUTE EVALUATOR (VEDIC-ONLY v2.0 FIXED)")
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
        # STEP 4.5: Extract Lagna Information [NEW - matches Property/FCC/Finance/Career]
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
        # STEP 5.5: Extract Timing Windows  [NEW - matches Property/FCC/Finance/Career]
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            # Fallback key - matches Property/FCC pattern
            if not timing_windows_list and "Business Legal Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Business Legal Timing"]
                logger.info(f"🔍 Using 'Business Legal Timing' fallback key, found {len(timing_windows_list)} windows")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Business-Specific Analysis  [NEW]
        # ═══════════════════════════════════════════════════════════
        business_analysis = self._analyze_business_indicators(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Business analysis: {business_analysis.get('business_legal_strength', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Vedic Outcome Analysis
        # ═══════════════════════════════════════════════════════════
        outcome_analysis = self._analyze_outcome_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info,
            business_analysis
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
            house_aspects_info
        )

        logger.info(f"✅ Risk level: {risk_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9.5: Business Legal Suitability Matrix  [NEW - matches Property pattern]
        # ═══════════════════════════════════════════════════════════
        legal_matrix = self._create_legal_suitability_matrix(
            outcome_analysis,
            duration_analysis,
            risk_analysis,
            business_analysis,
            lagna_info
        )
        result.additional_data[f"{DOMAIN_PREFIX}_suitability_matrix"] = legal_matrix
        logger.info(f"✅ Legal suitability matrix created with {len(legal_matrix)} strategy types")

        # ═══════════════════════════════════════════════════════════
        # STEP 9.6: Timing Decision Gate  [NEW - matches Property/FCC/Finance/Career]
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

            if timing_windows_data and timing_windows_data.get("has_timing"):
                best    = timing_windows_data.get("best_window", {})
                nearest = timing_windows_data.get("nearest_window", {})
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
        # STEP 11: Add Legal-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_legal_points(
            result,
            business_analysis,
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
            business_analysis,
            outcome_analysis,
            duration_analysis,
            risk_analysis,
            timing_windows_data,
            kwargs
        )

        # FIX: Store lagna_info at top level - matches Property/FCC/Finance/Career
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # FIX: Log result breakdown - matches Career/Property evaluator pattern
        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO EXTRACTION  [NEW - matches Property/FCC/Finance/Career exactly]
    # ══════════════════════════════════════════════════════════════
    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        """
        Extract lagna (ascendant) information from houses data.
        Matches PropertyLegalDisputeEvaluator v2.0 / FCC v3.0 / Finance / Career pattern exactly.
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
                    "Aries": "Mars",      "Taurus": "Venus",   "Gemini": "Mercury",
                    "Cancer": "Moon",     "Leo": "Sun",         "Virgo": "Mercury",
                    "Libra": "Venus",     "Scorpio": "Mars",    "Sagittarius": "Jupiter",
                    "Capricorn": "Saturn","Aquarius": "Saturn", "Pisces": "Jupiter"
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

                    if hasattr(analyzer, "get_planet_dignity"):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, "get_dignity"):
                        dignity = analyzer.get_dignity(lagna_lord)

                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, "value") else str(dignity)
                except Exception:
                    pass

            return {
                "lagna_sign":         lagna_sign,
                "lagna_lord":         lagna_lord,
                "lagna_lord_house":   lagna_lord_house,
                "lagna_lord_sign":    lagna_lord_sign,
                "lagna_lord_degree":  lagna_lord_degree,
                "lagna_lord_dignity": lagna_lord_dignity,
            }

        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    # ══════════════════════════════════════════════════════════════
    # BUSINESS LEGAL SUITABILITY MATRIX  [NEW - matches Property pattern]
    # ══════════════════════════════════════════════════════════════
    def _create_legal_suitability_matrix(
        self,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risk_analysis: Dict,
        business_analysis: Dict,
        lagna_info: Optional[Dict] = None
    ) -> Dict[str, Dict]:
        """
        Create business legal strategy suitability matrix.

        Analogous to _create_property_suitability_matrix in PropertyLegalDisputeEvaluator v2.0.
        Provides LLM with structured guidance on which strategies are most appropriate
        for a business or partnership legal dispute.
        """
        matrix = {}

        outcome          = outcome_analysis.get("likelihood", "UNCERTAIN")
        outcome_score    = outcome_analysis.get("score", 50)
        duration         = duration_analysis.get("duration_category", "MODERATE")
        risk_level       = risk_analysis.get("risk_level", "MODERATE")
        biz_strength     = business_analysis.get("business_legal_strength", "MODERATE")
        mercury_strength = business_analysis.get("mercury_strength", "MODERATE")
        h7_stronger      = business_analysis.get("opponent_stronger", False)

        # ═══════════════════════════════════════════════════════════
        # 1. PURSUE FULL LITIGATION
        # ═══════════════════════════════════════════════════════════
        if outcome in ("FAVORABLE",) and biz_strength in ("STRONG", "MODERATE_GOOD"):
            rating = "HIGH"
            reason = f"Favorable outlook ({outcome}) + strong business legal position → pursue litigation"
        elif outcome == "UNCERTAIN" and risk_level in ("LOW", "VERY_LOW"):
            rating = "MODERATE"
            reason = "Uncertain outcome but low risk → litigation viable with strong counsel"
        elif outcome in ("CHALLENGING", "UNFAVORABLE") or h7_stronger:
            rating = "LOW"
            reason = f"Challenging outlook or stronger opponent → consider alternatives before full litigation"
        else:
            rating = "MODERATE"
            reason = "Mixed indicators → assess evidence and counsel before proceeding"

        matrix["Pursue Full Litigation"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 2. OUT-OF-COURT SETTLEMENT
        # ═══════════════════════════════════════════════════════════
        if outcome in ("CHALLENGING", "UNFAVORABLE") or risk_level in ("HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Challenging outcome or {risk_level} risk → out-of-court settlement strongly recommended"
        elif duration in ("VERY_LONG", "LONG") and risk_level == "MODERATE":
            rating = "HIGH"
            reason = f"Very long expected duration + moderate risk → settlement saves time and costs"
        elif outcome == "FAVORABLE" and biz_strength == "STRONG":
            rating = "LOW"
            reason = "Strong position → press advantage in court rather than settling"
        else:
            rating = "MODERATE"
            reason = "Settlement is a viable risk-mitigation option for business disputes"

        matrix["Out-of-Court Settlement"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 3. MEDIATION / ARBITRATION
        # ═══════════════════════════════════════════════════════════
        if duration in ("VERY_LONG", "LONG"):
            rating = "HIGH"
            reason = f"Long expected duration ({duration}) → mediation or arbitration is cost-effective"
        elif h7_stronger:
            rating = "HIGH"
            reason = "Opponent holds stronger position → arbitration limits exposure"
        elif risk_level in ("HIGH", "VERY_HIGH"):
            rating = "MODERATE"
            reason = f"{risk_level} risk → explore arbitration to cap potential losses"
        else:
            rating = "MODERATE"
            reason = "Mediation can resolve business disputes faster than court proceedings"

        matrix["Mediation / Arbitration"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 4. STRENGTHEN DOCUMENTATION AND EVIDENCE
        # ═══════════════════════════════════════════════════════════
        if mercury_strength == "WEAK" or risk_level in ("HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Weak Mercury (contracts karaka) or {risk_level} risk → invest in documentation and evidence"
        elif outcome == "UNCERTAIN":
            rating = "HIGH"
            reason = "Uncertain outcome → strong documentation may tip balance in your favor"
        else:
            rating = "MODERATE"
            reason = "Solid documentation always strengthens a business legal position"

        matrix["Strengthen Documentation and Evidence"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 5. APPEAL / HIGHER FORUM
        # ═══════════════════════════════════════════════════════════
        if outcome == "CHALLENGING" and outcome_score >= 40:
            rating = "MODERATE"
            reason = "Challenging but not hopeless — appeal or higher forum may yield better result"
        elif outcome in ("FAVORABLE",) and biz_strength in ("STRONG", "MODERATE_GOOD"):
            rating = "MODERATE"
            reason = "Favorable indicators — keep appeal option open if lower forum rules adversely"
        else:
            rating = "LOW"
            reason = "Current indicators do not strongly support an appeal strategy"

        matrix["Appeal / Higher Forum"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 6. DELAY / WAIT FOR BETTER TIMING
        # ═══════════════════════════════════════════════════════════
        if outcome in ("UNCERTAIN", "CHALLENGING") and risk_level in ("MODERATE", "HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = f"Uncertain/challenging + {risk_level} risk → wait for better dasha support"
        elif outcome == "FAVORABLE" and duration in ("SHORT", "VERY_SHORT"):
            rating = "LOW"
            reason = "Favorable indicators + short duration — no reason to delay"
        else:
            rating = "MODERATE"
            reason = "Timing strategy depends on current dasha — consult timing windows"

        matrix["Delay Strategy (Wait for Better Dasha)"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 7. ENGAGE EXPERIENCED BUSINESS LAWYER
        # ═══════════════════════════════════════════════════════════
        if risk_level in ("HIGH", "VERY_HIGH") or outcome_score < 50:
            rating = "HIGH"
            reason = f"{risk_level.title()} risk / below-average outlook → experienced business counsel essential"
        elif mercury_strength == "WEAK":
            rating = "HIGH"
            reason = "Weak Mercury (contracts/evidence) → strong legal representation critical"
        else:
            rating = "MODERATE"
            reason = "Qualified business lawyer always advisable in partnership and commercial disputes"

        matrix["Engage Experienced Business Lawyer"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 8. PROTECT BUSINESS REPUTATION
        # ═══════════════════════════════════════════════════════════
        h10_risk = business_analysis.get("reputation_at_risk", False)

        if h10_risk or risk_level in ("HIGH", "VERY_HIGH"):
            rating = "HIGH"
            reason = "10th house affliction or high risk → proactive reputation management essential"
        elif outcome in ("CHALLENGING", "UNFAVORABLE"):
            rating = "HIGH"
            reason = "Challenging outcome → manage public/client perception proactively"
        else:
            rating = "MODERATE"
            reason = "Maintain professional reputation throughout proceedings"

        matrix["Protect Business Reputation"] = {"rating": rating, "vedic_reasoning": reason}

        return matrix

    # ══════════════════════════════════════════════════════════════
    # LOG RESULT BREAKDOWN  [NEW - matches Career/Property evaluator pattern]
    # ══════════════════════════════════════════════════════════════
    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging. Matches Property/Career evaluator pattern."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")

        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")

        summary = ad.get(f"{DOMAIN_PREFIX}_analysis_summary", {})
        if summary:
            logger.info(f"BUSINESS LEGAL STRENGTH: {summary.get('business_legal_strength')}")
            logger.info(f"OUTCOME: {summary.get('outcome_likelihood')}")
            logger.info(f"DURATION: {summary.get('duration_category')}")
            logger.info(f"RISK: {summary.get('risk_level')}")
            logger.info(f"MERCURY: {summary.get('mercury_strength')}")

        timing_data = ad.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        logger.info(f"TIMING: has_timing={timing_data.get('has_timing', False)}")

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION  [NEW - matches Property/FCC/Finance/Career exactly]
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow objects — matches Property/FCC/Finance/Career pattern.
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
                    "start":         get_attr(w, "start"),
                    "end":           get_attr(w, "end"),
                    "dasha":         get_attr(w, "dasha"),
                    "score":         get_attr(w, "score"),
                    "transit_score": get_attr(w, "transit_score"),
                    "final_score":   get_attr(w, "final_score"),
                    "age_at_start":  get_attr(w, "age_at_start"),
                    "is_overall_best":       get_attr(w, "is_overall_best", False),
                    "is_earliest_favorable": get_attr(w, "is_earliest_favorable", False),
                }
                for extra_field in ["score_maha", "score_antara", "score_paryantar",
                                    "md", "ad", "pd", "maha", "antara", "paryantar"]:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                return result

            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")

            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, "final_score", 0) or 0,
                reverse=True
            )

            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            favorable_windows = [
                w for w in timing_windows
                if (get_attr(w, "final_score", 0) or 0) >= 50
            ]

            logger.info(f"🔍 Found {len(favorable_windows)} favorable windows (score >= 50)")

            if favorable_windows:
                sorted_by_date = sorted(
                    favorable_windows,
                    key=lambda w: datetime.strptime(
                        get_attr(w, "start", "9999-12-31") or "9999-12-31",
                        "%Y-%m-%d"
                    )
                )
                nearest_window = window_to_dict(sorted_by_date[0]) if sorted_by_date else None
            else:
                nearest_window = best_window
                logger.info("🔍 No windows with score >= 50, using best window as nearest")

            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]

            result_dict = {
                "best_window":    best_window,
                "nearest_window": nearest_window,
                "all_favorable":  all_favorable,
                "has_timing":     True
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
    # BUSINESS-SPECIFIC ANALYSIS  [NEW]
    # ══════════════════════════════════════════════════════════════
    def _analyze_business_indicators(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze business-specific legal indicators using Vedic principles.

        Key business dispute indicators:
        - Mercury: Contracts, documentation, evidence
        - 3rd house: Agreements, communication (secondary)
        - 7th house: Partner/opponent strength
        - 10th house: Reputation risk in business
        - 2nd house: Business financial assets at stake
        """
        analysis = {
            "business_legal_strength": "MODERATE",
            "business_score": 50,
            "mercury_strength": "MODERATE",
            "reputation_at_risk": False,
            "opponent_stronger": False,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "business_hints": []
        }

        score = 50

        # ── MERCURY (Contracts, Documentation, Evidence) ──────────
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_sign  = mercury_data.get("sign", "")
            mercury_house = mercury_data.get("house")

            mercury_strong_signs = ["Gemini", "Virgo"]
            mercury_weak_signs   = ["Sagittarius", "Pisces"]

            if mercury_sign in mercury_strong_signs:
                score += 10
                analysis["mercury_strength"] = "STRONG"
                analysis["favorable_factors"].append(
                    f"Mercury in {mercury_sign} - strong for contracts, documentation, and evidence"
                )
            elif mercury_sign in mercury_weak_signs:
                score -= 8
                analysis["mercury_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    f"Mercury in {mercury_sign} - contracts and documentation may face challenges"
                )
            else:
                analysis["mercury_strength"] = "MODERATE"

            if mercury_house in [1, 2, 5, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Mercury in house {mercury_house} - favorable for business legal communication"
                )
            elif mercury_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Mercury in house {mercury_house} - communication challenges in legal proceedings"
                )

        # ── 7TH HOUSE (Partner / Opponent) ───────────────────────
        h7_info = house_lords_info.get(7, {})
        h1_info = house_lords_info.get(1, {})

        if h7_info and h1_info:
            h7_str = h7_info.get("lord_strength_score", 50)
            h1_str = h1_info.get("lord_strength_score", 50)

            if h7_str > h1_str + 15:
                score -= 10
                analysis["opponent_stronger"] = True
                analysis["unfavorable_factors"].append(
                    "Opponent/partner's significator (7th lord) is significantly stronger — expect strong opposition"
                )
                analysis["business_hints"].append(
                    "Consider settlement or mediation rather than prolonged litigation"
                )
            elif h1_str > h7_str + 15:
                score += 8
                analysis["favorable_factors"].append(
                    "Your significator (1st lord) is significantly stronger than opponent — favorable position"
                )

        # ── 10TH HOUSE (Reputation) ───────────────────────────────
        h10_aspects = house_aspects_info.get(10, {})
        malefics_on_10 = h10_aspects.get("malefic_aspects", [])

        if len(malefics_on_10) >= 2:
            score -= 8
            analysis["reputation_at_risk"] = True
            analysis["unfavorable_factors"].append(
                f"Multiple malefics ({', '.join(malefics_on_10)}) affect 10th house — business reputation at stake"
            )

        h10_info = house_lords_info.get(10, {})
        if h10_info:
            h10_str = h10_info.get("lord_strength_score", 50)
            if h10_str < 40:
                score -= 5
                analysis["reputation_at_risk"] = True
                analysis["unfavorable_factors"].append(
                    f"10th lord {h10_info.get('lord')} is weak — professional reputation vulnerable during dispute"
                )
            elif h10_str >= 70:
                score += 5
                analysis["favorable_factors"].append(
                    f"10th lord {h10_info.get('lord')} is strong — reputation and authority provide protection"
                )

        # ── 2ND HOUSE (Business Assets / Finance at stake) ────────
        h2_info = house_lords_info.get(2, {})
        if h2_info:
            h2_str = h2_info.get("lord_strength_score", 50)
            if h2_str >= 70:
                score += 5
                analysis["favorable_factors"].append(
                    "2nd lord strong — business financial assets are better protected"
                )
            elif h2_str < 40:
                score -= 5
                analysis["unfavorable_factors"].append(
                    "2nd lord weak — business financial assets may be vulnerable in the dispute"
                )

        # ── JUPITER on 6th / 9th / 11th (justice + victory) ──────
        for h_num in [6, 9, 11]:
            if "Jupiter" in house_aspects_info.get(h_num, {}).get("benefic_aspects", []):
                score += 5
                analysis["favorable_factors"].append(
                    f"Jupiter aspects house {h_num} — justice and favorable legal support"
                )
                break

        # ── SUN (Government / Authority) ──────────────────────────
        sun_data = planets.get("Sun", {})
        if sun_data:
            sun_house = sun_data.get("house")
            if sun_house in [9, 10, 11]:
                score += 5
                analysis["business_hints"].append(
                    f"Sun in house {sun_house} — authority and government connections may support the case"
                )

        # ── RAHU in 7th or 8th (unexpected complications) ─────────
        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") in [7, 8]:
            score -= 8
            analysis["unfavorable_factors"].append(
                f"Rahu in house {rahu_data.get('house')} — unexpected complications or deceptive opponent tactics"
            )

        score = max(0, min(100, score))
        analysis["business_score"] = score

        if score >= 70:
            analysis["business_legal_strength"] = "STRONG"
        elif score >= 55:
            analysis["business_legal_strength"] = "MODERATE_GOOD"
        elif score >= 45:
            analysis["business_legal_strength"] = "MODERATE"
        elif score >= 30:
            analysis["business_legal_strength"] = "WEAK"
        else:
            analysis["business_legal_strength"] = "VERY_WEAK"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # OUTCOME PROSPECTS ANALYSIS  (updated to consume business_analysis)
    # ══════════════════════════════════════════════════════════════
    def _analyze_outcome_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        business_analysis: Dict
    ) -> Dict:
        """
        Analyze legal outcome prospects using Vedic principles.
        Now seeded from business_analysis score for domain consistency.
        """
        analysis = {
            "likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "strategic_hints": []
        }

        # Seed from business analysis score
        score = business_analysis.get("business_score", 50)

        # 6th house (litigation ability)
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            if h6_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is strong ({h6_strength}/100) - good litigation ability"
                )
            elif h6_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is weak ({h6_strength}/100) - may struggle in legal battles"
                )

        # 9th house (justice)
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            if h9_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is strong - justice and law favor you"
                )
            elif h9_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is weak - legal proceedings may be challenging"
                )

        # 11th house (victory)
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            if h11_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is strong - victory and gains supported"
                )
            elif h11_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is weak - achieving desired outcome requires extra effort"
                )

        # Opponent strength (from business_analysis)
        if business_analysis.get("opponent_stronger"):
            analysis["strategic_hints"].append(
                "Opponent holds stronger position — consider settlement or mediation"
            )

        # 12th house (losses — negative indicator)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            if h12_strength >= 70:
                score -= 12
                analysis["unfavorable_factors"].append(
                    f"12th lord {h12_info.get('lord')} is strong - potential for expenses and losses"
                )
                analysis["strategic_hints"].append("Budget carefully for legal expenses")

        # 8th house (hidden matters)
        h8_info = house_lords_info.get(8, {})
        if h8_info and h8_info.get("lord_strength_score", 50) >= 70:
            analysis["strategic_hints"].append(
                "Hidden aspects may surface during proceedings - be prepared"
            )

        # Jupiter (karaka for law and justice)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 9, 11]:
                score += 10
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine grace and justice support you"
                )
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - may face challenges in getting justice"
                )

        h9_aspects  = house_aspects_info.get(9, {})
        h11_aspects = house_aspects_info.get(11, {})

        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - strong support for justice"
            )
        if "Jupiter" in h11_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 11th house - victory supported"
            )

        h6_aspects = house_aspects_info.get(6, {})
        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["strategic_hints"].append(
                "Saturn's aspect on 9th indicates delays in legal proceedings"
            )
        if "Rahu" in h6_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["unfavorable_factors"].append(
                "Rahu's influence on 6th house - confusion or deception in litigation"
            )

        sun_data = planets.get("Sun", {})
        if sun_data and sun_data.get("house") in [10, 11]:
            score += 5
            analysis["favorable_factors"].append(
                f"Sun in house {sun_data.get('house')} - authority and government may favor you"
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
    # DURATION ANALYSIS  (unchanged logic, kept intact)
    # ══════════════════════════════════════════════════════════════
    def _analyze_duration(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze expected duration of legal proceedings using Vedic principles."""
        analysis = {
            "duration_category": "MODERATE",
            "duration_score": 50,
            "delay_factors": [],
            "speed_factors": [],
            "duration_hints": []
        }

        duration_score = 50

        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [6, 7, 9, 10]:
                duration_score += 20
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays expected"
                )

        h6_aspects = house_aspects_info.get(6, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Saturn" in h6_aspects.get("malefic_aspects", []):
            duration_score += 15
            analysis["delay_factors"].append(
                "Saturn aspects 6th house - litigation process will be slow"
            )
        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            duration_score += 15
            analysis["delay_factors"].append(
                "Saturn aspects 9th house - legal proceedings delayed"
            )

        h6_info = house_lords_info.get(6, {})
        if h6_info and h6_info.get("lord_is_retrograde"):
            duration_score += 10
            analysis["delay_factors"].append(
                f"6th lord {h6_info.get('lord')} is retrograde - case may drag on"
            )

        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") in [6, 7, 9]:
            duration_score += 10
            analysis["delay_factors"].append(
                f"Rahu in house {rahu_data.get('house')} - unexpected complications may arise"
            )

        ketu_data = planets.get("Ketu", {})
        if ketu_data and ketu_data.get("house") in [6, 7, 9]:
            duration_score += 5
            analysis["duration_hints"].append(
                "Ketu's influence may bring sudden twists in proceedings"
            )

        mercury_data = planets.get("Mercury", {})
        if mercury_data and mercury_data.get("house") in [1, 5, 9, 11]:
            duration_score -= 10
            analysis["speed_factors"].append(
                "Mercury well-placed - documentation and communication will be smooth"
            )

        for h_num in [6, 9, 11]:
            h_aspects = house_aspects_info.get(h_num, {})
            benefics  = h_aspects.get("benefic_aspects", [])
            if "Jupiter" in benefics or "Venus" in benefics:
                duration_score -= 5
                analysis["speed_factors"].append(
                    f"Benefic aspect on house {h_num} - may help expedite matters"
                )

        duration_score = max(0, min(100, duration_score))
        analysis["duration_score"] = duration_score

        if duration_score >= 75:
            analysis["duration_category"] = "VERY_LONG"
            analysis["duration_hints"].append(
                "Expect prolonged legal battle - prepare for extended timeline"
            )
        elif duration_score >= 60:
            analysis["duration_category"] = "LONG"
            analysis["duration_hints"].append(
                "Case may take considerable time - patience required"
            )
        elif duration_score >= 40:
            analysis["duration_category"] = "MODERATE"
            analysis["duration_hints"].append(
                "Normal timeline expected for legal proceedings"
            )
        elif duration_score >= 25:
            analysis["duration_category"] = "SHORT"
            analysis["duration_hints"].append("Relatively quick resolution possible")
        else:
            analysis["duration_category"] = "VERY_SHORT"
            analysis["duration_hints"].append("Quick settlement or resolution indicated")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISK AND PENALTY ANALYSIS  (unchanged logic, kept intact)
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks_and_penalties(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze potential risks and penalties using Vedic principles."""
        analysis = {
            "risk_level": "MODERATE",
            "risk_score": 50,
            "risk_factors": [],
            "penalty_indicators": [],
            "mitigation_hints": [],
            "areas_of_concern": []
        }

        risk_score = 50

        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            if h8_lord_house in [1, 10]:
                risk_score += 15
                analysis["risk_factors"].append(
                    f"8th lord {h8_info.get('lord')} in house {h8_lord_house} - hidden risks to "
                    f"{'self' if h8_lord_house == 1 else 'reputation'}"
                )
                if h8_lord_house == 10:
                    analysis["areas_of_concern"].append("Professional reputation at risk")

        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_lord_house = h12_info.get("lord_in_house")
            h12_strength   = h12_info.get("lord_strength_score", 50)
            if h12_lord_house == 6:
                risk_score += 12
                analysis["penalty_indicators"].append(
                    "12th lord in 6th - significant legal expenses indicated"
                )
                analysis["areas_of_concern"].append("Financial losses from legal fees")
            if h12_strength >= 70:
                risk_score += 10
                analysis["penalty_indicators"].append(
                    f"12th lord {h12_info.get('lord')} is strong - potential for substantial losses"
                )

        saturn_data = planets.get("Saturn", {})
        if saturn_data and saturn_data.get("house") == 12:
            risk_score += 15
            analysis["risk_factors"].append(
                "Saturn in 12th house - serious penalties possible, including confinement"
            )
            analysis["areas_of_concern"].append("Severe penalties or restrictions")
            analysis["mitigation_hints"].append("Seek strong legal counsel immediately")

        mars_data  = planets.get("Mars", {})
        h7_aspects = house_aspects_info.get(7, {})

        if mars_data and mars_data.get("house") == 7:
            risk_score += 10
            analysis["risk_factors"].append(
                "Mars in 7th house - opponent is aggressive and combative"
            )
            analysis["mitigation_hints"].append("Prepare for confrontational proceedings")

        if "Mars" in h7_aspects.get("malefic_aspects", []):
            risk_score += 8
            analysis["risk_factors"].append(
                "Mars aspects 7th house - conflict with opponent intensified"
            )

        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") in [8, 12]:
            risk_score += 12
            analysis["risk_factors"].append(
                f"Rahu in house {rahu_data.get('house')} - unexpected complications or penalties"
            )
            analysis["mitigation_hints"].append(
                "Be prepared for surprises - have contingency plans"
            )

        h10_aspects    = house_aspects_info.get(10, {})
        malefics_on_10 = h10_aspects.get("malefic_aspects", [])
        if len(malefics_on_10) >= 2:
            risk_score += 10
            analysis["areas_of_concern"].append("Significant reputation risk")
            analysis["risk_factors"].append(
                f"Multiple malefics ({', '.join(malefics_on_10)}) affect 10th house - reputation at stake"
            )

        h2_aspects    = house_aspects_info.get(2, {})
        malefics_on_2 = h2_aspects.get("malefic_aspects", [])
        if "Saturn" in malefics_on_2 or "Rahu" in malefics_on_2:
            risk_score += 8
            analysis["penalty_indicators"].append(
                "Malefic influence on 2nd house - financial penalties possible"
            )
            analysis["areas_of_concern"].append("Business assets may be affected")

        h9_aspects = house_aspects_info.get(9, {})
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            risk_score -= 10
            analysis["mitigation_hints"].append(
                "Jupiter's grace on 9th house provides protection through law"
            )

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
    # HOUSE LORDS EXTRACTION  (unchanged logic, kept intact)
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
                        "Aries": "Mars",      "Taurus": "Venus",   "Gemini": "Mercury",
                        "Cancer": "Moon",     "Leo": "Sun",         "Virgo": "Mercury",
                        "Libra": "Venus",     "Scorpio": "Mars",    "Sagittarius": "Jupiter",
                        "Capricorn": "Saturn","Aquarius": "Saturn", "Pisces": "Jupiter"
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
            lord_is_combust    = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False)     or lord_data.get("is_retrograde", False)

            lord_dignity        = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity  = analyzer._get_dignity(normalized_lord, lord_sign, lord_degree)
                    lord_dignity = dignity.value
                    if dignity:
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity
                        )
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
                "lord":                normalized_lord,
                "lord_in_house":       lord_house,
                "lord_in_sign":        lord_sign,
                "lord_degree":         lord_degree,
                "lord_is_combust":     lord_is_combust,
                "lord_is_retrograde":  lord_is_retrograde,
                "lord_dignity":        lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority":            priority,
                "planets_in_house":    planets_in_house,
                "house_sign":          house_sign,
            }

        return house_lords_info

    # ══════════════════════════════════════════════════════════════
    # ASPECTS EXTRACTION  (unchanged logic, kept intact)
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
    # STRENGTH CALCULATION  (unchanged logic, kept intact)
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(self, planet_name: str, planet_data: dict, dignity=None) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, "value") else str(dignity).upper()
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
    # ADD HOUSE ANALYSIS POINTS  (updated: now uses HOUSE_MEANINGS dict)
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
    # ADD LEGAL-SPECIFIC POINTS  (updated: includes business_analysis)
    # ══════════════════════════════════════════════════════════════
    def _add_legal_points(
        self,
        result: EvaluationResult,
        business_analysis: Dict,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risk_analysis: Dict
    ):
        """Add business-legal-specific points to result."""
        result.add_point(
            f"🏢 Business Legal Strength: {business_analysis.get('business_legal_strength','MODERATE')} "
            f"(Score: {business_analysis.get('business_score',50)}/100)"
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
            f"📝 Mercury (Contracts Karaka): {business_analysis.get('mercury_strength','MODERATE')}"
        )

        for factor in business_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in outcome_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in business_analysis.get("unfavorable_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        for factor in risk_analysis.get("risk_factors", [])[:2]:
            result.add_point(f"🚨 {factor}")

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # [FIX: aligned with Property/FCC/Finance/Career - dasha_context, timing, lagna pass-through]
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        business_analysis: dict,
        outcome_analysis: dict,
        duration_analysis: dict,
        risk_analysis: dict,
        timing_windows_data: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

        # Extract dasha context from kwargs - matches Property/FCC/Finance/Career
        current_dasha   = kwargs.get("current_dasha")
        dasha_timeline  = kwargs.get("dasha_timeline")
        transit_summary = kwargs.get("transit_summary")
        age_context     = kwargs.get("age_context")
        meta            = kwargs.get("meta")

        # FIX: consistent meta_query_type extraction
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
            f"{DOMAIN_PREFIX}_business_analysis": business_analysis,
            f"{DOMAIN_PREFIX}_outcome_analysis":  outcome_analysis,
            f"{DOMAIN_PREFIX}_duration_analysis": duration_analysis,
            f"{DOMAIN_PREFIX}_risk_analysis":     risk_analysis,

            # Analysis summary
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed":   len(house_lords_info),
                "primary_houses_count":    len(primary_houses),
                "secondary_houses_count":  len(secondary_houses),
                "business_legal_strength": business_analysis.get("business_legal_strength", "MODERATE"),
                "business_score":          business_analysis.get("business_score", 50),
                "mercury_strength":        business_analysis.get("mercury_strength", "MODERATE"),
                "reputation_at_risk":      business_analysis.get("reputation_at_risk", False),
                "opponent_stronger":       business_analysis.get("opponent_stronger", False),
                "outcome_likelihood":      outcome_analysis.get("likelihood", "UNCERTAIN"),
                "outcome_score":           outcome_analysis.get("score", 50),
                "duration_category":       duration_analysis.get("duration_category", "MODERATE"),
                "risk_level":              risk_analysis.get("risk_level", "MODERATE"),
                "risk_score":              risk_analysis.get("risk_score", 50),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                ),
            },

            # Dasha pass-through - matches Property/FCC/Finance/Career
            f"{DOMAIN_PREFIX}_current_dasha":   current_dasha,
            f"{DOMAIN_PREFIX}_dasha_timeline":  dasha_timeline,

            # Optional context
            f"{DOMAIN_PREFIX}_transit_summary": transit_summary,
            f"{DOMAIN_PREFIX}_age_context":     age_context,
        })

        # Store timing windows - matches Property/FCC/Finance/Career exactly
        if timing_windows_data and timing_windows_data.get("has_timing"):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {DOMAIN_PREFIX}_timing_windows")
            if timing_windows_data.get("best_window"):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha','N/A')}")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}
            logger.warning("❌ NO TIMING WINDOWS TO STORE")

        # Dasha context for prompt builder - matches Property/Career pattern
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
            f"📦 STORED | business={business_analysis.get('business_legal_strength')} | "
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
                id="LEGAL_BUSINESS_MAIN",
                question=(
                    "What does astrology reveal about the outcome, duration, "
                    "risks and potential penalties of my business or partnership legal issues?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Business Legal Dispute"
            )
        ]
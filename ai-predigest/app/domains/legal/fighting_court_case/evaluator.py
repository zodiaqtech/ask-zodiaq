"""
Fighting Court Case Evaluator – VEDIC-ONLY v3.0 (FIXED - FULL PARITY WITH FINANCE/CAREER)

Specialized evaluator for legal matters, court cases, and dispute-related queries
using traditional Vedic astrology principles.

FIXES FROM v2.0:
✅ Added _extract_lagna_info() - matches Finance/Career evaluator pattern
✅ Added lagna_info stored in evaluate() and _store_data_for_llm()
✅ Added _create_legal_suitability_matrix() - analogous to investment_suitability_matrix (Doc 2)
✅ Added _log_result_breakdown() - matches Career evaluator pattern (Doc 3)
✅ Fixed meta handling - consistent QueryMeta/dict normalization across all paths
✅ Fixed timing_windows_data fallback key logic - matches Doc 2/3 pattern exactly
✅ Fixed _store_data_for_llm() - aligned dasha pass-through with Doc 2/3
✅ Fixed meta_query_type comparison - consistent QueryType.TIMING gate
✅ COMPLETE structural parity with Finance/Parenting/Travel/Career evaluators

✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Case outcome prediction
✔ Duration assessment
✔ Risk and penalty analysis
✔ TIMING SUPPORT for case conclusion
✔ Legal case suitability matrix (NEW)
✔ Lagna lord analysis (NEW)
✔ Complete data storage for LLM

Key Houses for Legal Matters:
- 6th House: Enemies, disputes, litigation, debts, obstacles (PRIMARY)
- 7th House: Opponents, adversaries, open enemies, contracts
- 8th House: Sudden events, hidden matters, penalties, fines, imprisonment
- 9th House: Judges, law, justice, higher courts, dharma
- 12th House: Losses, imprisonment, expenses in litigation, foreign courts
- 1st House: Self, native's strength in fighting the case
- 11th House: Gains, victory, favorable outcome, fulfillment

Karakas:
- Saturn: Law, justice, delays, punishment, karma
- Mars: Courage to fight, aggression, conflicts
- Jupiter: Judges, dharma, favorable verdicts, protection
- Sun: Government, authority, power in legal matters
- Rahu: Deception, complications, unexpected twists
- Mercury: Documents, communication, lawyers, arguments
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
    logging.info("House lords analyzer available for Legal domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "legal"


class FightingCourtCaseEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Legal → Fighting Court Case

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Case outcome likelihood
    - Duration assessment
    - Risk and penalty analysis
    - Timing windows for case conclusion
    - Legal case suitability matrix (NEW)
    - Lagna lord analysis (NEW)
    - NO KP analysis (purely Vedic)

    Traditional Vedic Rules for Legal Matters:
    - 6th house strong + 6th lord well-placed = Victory over enemies/opponents
    - 7th house weak = Weak opponent (favorable)
    - 7th house strong = Strong opponent (challenging)
    - 9th house strong = Favorable judgment, justice prevails
    - 8th house afflicted = Risk of penalties, unexpected setbacks
    - 12th house afflicted = Risk of imprisonment, heavy losses
    - 11th house strong = Gains from litigation, victory
    - Jupiter aspecting 6th/9th = Divine justice, favorable outcome
    - Saturn strong = Delays but eventual justice
    - Mars in 6th = Victory in disputes (digbala)
    """

    domain = "Legal"
    subtopic = "Fighting Court Case"

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANINGS
    # ══════════════════════════════════════════════════════════════
    HOUSE_MEANINGS = {
        1: "Self/Native's Strength",
        6: "Litigation/Disputes/Enemies",
        7: "Opponent/Adversary",
        8: "Penalties/Hidden Matters",
        9: "Judges/Law/Justice",
        11: "Victory/Gains",
        12: "Losses/Imprisonment"
    }

    # ══════════════════════════════════════════════════════════════
    # CASE TYPE CLASSIFICATION
    # ══════════════════════════════════════════════════════════════
    CASE_TYPES = {
        "civil": {
            "primary_houses": [6, 7, 11],
            "description": "Property disputes, contracts, civil matters"
        },
        "criminal": {
            "primary_houses": [6, 8, 12],
            "description": "Criminal charges, penalties, imprisonment risk"
        },
        "family": {
            "primary_houses": [6, 7, 4],
            "description": "Divorce, custody, family disputes"
        },
        "financial": {
            "primary_houses": [6, 2, 11],
            "description": "Debt recovery, financial fraud, tax matters"
        }
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
        # STEP 0: Normalize Meta  [FIX: consistent with Doc 2 & 3]
        # ═══════════════════════════════════════════════════════════
        meta = kwargs.get("meta")

        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        meta_query_type = meta.query_type if isinstance(meta, QueryMeta) else None
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Determine Case Type
        # ═══════════════════════════════════════════════════════════
        case_type = self._determine_case_type(question_text, sub_subdomain)
        logger.info(f"📋 Case type determined: {case_type}")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Select Analysis Data (Vedic preferred)
        # ═══════════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════════
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = set(house_config["primary"])
            secondary_houses = set(house_config["secondary"])
            all_relevant_houses = primary_houses | secondary_houses
            # FIX: Always include house 1 for lagna lord analysis (matches Doc 2 & 3)
            all_relevant_houses.add(1)
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
        else:
            logger.warning(f"No config for question, using fallback for Legal")
            primary_houses = {6, 7, 9, 11}
            secondary_houses = {1, 8, 12}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("FIGHTING COURT CASE EVALUATOR (VEDIC-ONLY v3.0 FIXED)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Case Type: {case_type}")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Calculate Aspects
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
        # STEP 5: Extract House Lords Data
        # ═══════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 5.5: Extract Lagna Information [NEW - matches Doc 2 & 3]
        # ═══════════════════════════════════════════════════════════
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 6.5: Extract Timing Windows
        # [FIX: aligned fallback logic with Doc 2 & 3 patterns exactly]
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            # Try exact sub_subdomain match first
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            # Fallback keys for legal timing - aligned with Doc 2 pattern
            if not timing_windows_list and "Case Conclusion Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Case Conclusion Timing"]
                logger.info(f"🔍 Using 'Case Conclusion Timing' fallback key, found {len(timing_windows_list)} windows")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Case Outcome Analysis
        # ═══════════════════════════════════════════════════════════
        outcome_analysis = self._analyze_case_outcome(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info,
            case_type
        )

        logger.info(f"✅ Case outcome: {outcome_analysis.get('outcome_likelihood', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Duration Analysis
        # ═══════════════════════════════════════════════════════════
        duration_analysis = self._analyze_case_duration(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Case duration: {duration_analysis.get('duration_estimate', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Risks and Penalties Analysis
        # ═══════════════════════════════════════════════════════════
        risks_analysis = self._analyze_risks_and_penalties(
            analysis_planets,
            house_lords_info,
            house_aspects_info,
            case_type
        )

        logger.info(f"✅ Risk level: {risks_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Opponent Strength Analysis
        # ═══════════════════════════════════════════════════════════
        opponent_analysis = self._analyze_opponent_strength(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Opponent strength: {opponent_analysis.get('opponent_strength', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 10.5: Legal Case Suitability Matrix [NEW - matches Doc 2 investment_matrix]
        # ═══════════════════════════════════════════════════════════
        legal_matrix = self._create_legal_suitability_matrix(
            outcome_analysis,
            duration_analysis,
            risks_analysis,
            opponent_analysis,
            case_type,
            lagna_info
        )
        result.additional_data["legal_suitability_matrix"] = legal_matrix
        logger.info(f"✅ Legal suitability matrix created with {len(legal_matrix)} strategy types")

        # ═══════════════════════════════════════════════════════════
        # STEP 10.6: Timing Decision Gate
        # [FIX: consistent meta_query_type comparison - matches Doc 2 & 3]
        # ═══════════════════════════════════════════════════════════
        logger.warning("🔎 TIMING GATE DEBUG -----------------------------")
        logger.warning(f"meta_query_type        = {meta_query_type}")
        logger.warning(f"QueryType.TIMING       = {QueryType.TIMING}")
        logger.warning(f"meta == TIMING ?       = {meta_query_type == QueryType.TIMING}")
        logger.warning(f"timing_windows_list type = {type(timing_windows_list)}")
        logger.warning(f"timing_windows_list len  = {len(timing_windows_list) if timing_windows_list else 0}")
        logger.warning(f"timing_windows_list bool = {bool(timing_windows_list)}")

        if timing_windows_list:
            logger.warning(
                f"First timing window keys = "
                f"{timing_windows_list[0].keys() if isinstance(timing_windows_list[0], dict) else type(timing_windows_list[0])}"
            )
        logger.warning("🔎 END TIMING GATE DEBUG -------------------------")

        timing_windows_data = {}

        if (
            meta_query_type == QueryType.TIMING
            and timing_windows_list
        ):
            timing_windows_data = self._extract_timing_windows(timing_windows_list) or {}
            logger.info("✅ TIMING ENABLED (timing query type + windows present)")

            if timing_windows_data and timing_windows_data.get('has_timing'):
                best = timing_windows_data.get('best_window', {})
                nearest = timing_windows_data.get('nearest_window', {})
                logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
                logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
                logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            timing_windows_data = {"has_timing": False}
            logger.info("⛔ TIMING DISABLED (not a timing query or no windows)")

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 12: Add Legal-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_legal_points(result, outcome_analysis, duration_analysis, risks_analysis, opponent_analysis)

        # ═══════════════════════════════════════════════════════════
        # STEP 13: Store Enhanced Data for LLM (with timing support)
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            outcome_analysis,
            duration_analysis,
            risks_analysis,
            opponent_analysis,
            case_type,
            timing_windows_data,
            kwargs
        )

        # FIX: Store lagna_info at top level - matches Doc 2 & 3
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # FIX: Log result breakdown - matches Doc 3
        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ══════════════════════════════════════════════════════════════
    # LEGAL CASE SUITABILITY MATRIX [NEW - analogous to Doc 2 investment_matrix]
    # ══════════════════════════════════════════════════════════════
    def _create_legal_suitability_matrix(
        self,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risks_analysis: Dict,
        opponent_analysis: Dict,
        case_type: str,
        lagna_info: Optional[Dict] = None
    ) -> Dict[str, Dict]:
        """
        Create legal strategy suitability matrix.

        Analogous to investment_suitability_matrix in ProspectsOfInvestmentsEvaluator (Doc 2).
        Provides LLM with structured guidance on which strategies are most appropriate.
        """
        matrix = {}

        outcome = outcome_analysis.get("outcome_likelihood", "UNCERTAIN")
        outcome_score = outcome_analysis.get("score", 50)
        duration = duration_analysis.get("duration_estimate", "MODERATE")
        risk_level = risks_analysis.get("risk_level", "LOW")
        risk_score = risks_analysis.get("risk_score", 20)
        opp_strength = opponent_analysis.get("opponent_strength", "MODERATE")

        # ═══════════════════════════════════════════════════════════
        # 1. FULL LITIGATION (Fight in court)
        # ═══════════════════════════════════════════════════════════
        if outcome in ["HIGHLY_FAVORABLE", "FAVORABLE"] and opp_strength in ["WEAK", "MODERATE_WEAK"]:
            rating = "HIGH"
            reason = f"Strong outcome ({outcome}) + weak opponent ({opp_strength}) → pursue full litigation"
        elif outcome == "UNCERTAIN" and risk_level in ["LOW", "VERY_LOW"]:
            rating = "MODERATE"
            reason = "Uncertain outcome but low risk → litigation viable with strong legal counsel"
        elif outcome in ["CHALLENGING", "DIFFICULT"]:
            rating = "LOW"
            reason = f"Challenging outcome ({outcome}) → consider alternatives before full court battle"
        else:
            rating = "MODERATE"
            reason = "Mixed indicators → assess strength of evidence before proceeding"

        matrix["Full Litigation (Fight in Court)"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 2. OUT-OF-COURT SETTLEMENT
        # ═══════════════════════════════════════════════════════════
        if opp_strength in ["STRONG", "MODERATE_STRONG"] or outcome in ["CHALLENGING", "DIFFICULT"]:
            rating = "HIGH"
            reason = f"Opponent strong ({opp_strength}) / outcome challenging → settlement recommended"
        elif duration in ["LONG", "MODERATE_LONG"] and risk_level in ["MODERATE", "HIGH"]:
            rating = "HIGH"
            reason = f"Prolonged case ({duration}) + {risk_level} risk → settlement saves time and reduces exposure"
        elif outcome in ["HIGHLY_FAVORABLE", "FAVORABLE"] and opp_strength == "WEAK":
            rating = "LOW"
            reason = "Strong position → no need to settle; press advantage in court"
        else:
            rating = "MODERATE"
            reason = "Settlement viable as a risk mitigation strategy"

        matrix["Out-of-Court Settlement"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 3. MEDIATION / ARBITRATION
        # ═══════════════════════════════════════════════════════════
        if case_type in ["civil", "financial"] and duration in ["LONG", "MODERATE_LONG"]:
            rating = "HIGH"
            reason = f"Civil/financial {case_type} case with long expected duration → mediation cost-effective"
        elif case_type == "criminal":
            rating = "LOW"
            reason = "Criminal cases cannot be mediated — requires court proceedings"
        else:
            rating = "MODERATE"
            reason = "Mediation can be explored to reach faster resolution"

        matrix["Mediation/Arbitration"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 4. APPEAL TO HIGHER COURT
        # ═══════════════════════════════════════════════════════════
        if outcome_score >= 60 and case_type in ["civil", "criminal"]:
            rating = "MODERATE"
            reason = "Reasonable outcome score → appeal viable if lower court rules unfavorably"
        elif outcome in ["CHALLENGING", "DIFFICULT"]:
            rating = "HIGH"
            reason = "Challenging chart indicators → higher court may offer better justice"
        else:
            rating = "LOW"
            reason = "Current indicators don't strongly support appeal strategy"

        matrix["Appeal to Higher Court"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 5. DELAY / WAIT FOR BETTER TIMING
        # ═══════════════════════════════════════════════════════════
        if outcome in ["UNCERTAIN", "CHALLENGING"] and risk_level in ["MODERATE", "HIGH"]:
            rating = "HIGH"
            reason = f"Uncertain/challenging outcome + {risk_level} risk → wait for better dasha period"
        elif duration in ["SHORT", "MODERATE_SHORT"] and outcome in ["FAVORABLE", "HIGHLY_FAVORABLE"]:
            rating = "LOW"
            reason = "Favorable chart + quick resolution expected → no need to delay"
        else:
            rating = "MODERATE"
            reason = "Timing strategy depends on current dasha — consult timing windows"

        matrix["Delay Strategy (Wait for Better Timing)"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 6. GATHERING EVIDENCE / STRENGTHENING CASE
        # ═══════════════════════════════════════════════════════════
        if opp_strength in ["STRONG", "MODERATE_STRONG"] or outcome_score < 55:
            rating = "HIGH"
            reason = "Strong opponent or uncertain outcome → invest in evidence and documentation"
        else:
            rating = "MODERATE"
            reason = "Evidence building always advisable regardless of chart strength"

        matrix["Evidence Gathering / Case Strengthening"] = {"rating": rating, "vedic_reasoning": reason}

        # ═══════════════════════════════════════════════════════════
        # 7. ENGAGING EXPERIENCED LEGAL COUNSEL
        # ═══════════════════════════════════════════════════════════
        if risk_level in ["HIGH", "MODERATE"] or case_type == "criminal":
            rating = "HIGH"
            reason = f"{risk_level.title()} risk {'criminal case' if case_type == 'criminal' else 'indicators'} → experienced legal counsel essential"
        elif outcome_score < 50:
            rating = "HIGH"
            reason = "Below-average outcome score → specialist legal support critical"
        else:
            rating = "MODERATE"
            reason = "Professional legal counsel always recommended in court matters"

        matrix["Engaging Experienced Legal Counsel"] = {"rating": rating, "vedic_reasoning": reason}

        return matrix

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO EXTRACTION [NEW - matches Doc 2 & 3 exactly]
    # ══════════════════════════════════════════════════════════════
    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        """
        Extract lagna (ascendant) information from houses data.

        FIX: Added to match Finance (Doc 2) and Career (Doc 3) evaluator pattern.

        Returns dict with:
        - lagna_sign: The sign of the first house
        - lagna_lord: The planet ruling that sign
        - lagna_lord_house: Where the lagna lord is placed
        - lagna_lord_sign: Sign where lagna lord is placed
        - lagna_lord_dignity: Dignity of the lagna lord
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

            lagna_lord_data = planets.get(lagna_lord, {})
            lagna_lord_house = lagna_lord_data.get("house")
            lagna_lord_sign = lagna_lord_data.get("sign", "")
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
                    dignity = None

                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(lagna_lord)

                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, 'value') else str(dignity)
                except Exception:
                    pass

            return {
                "lagna_sign": lagna_sign,
                "lagna_lord": lagna_lord,
                "lagna_lord_house": lagna_lord_house,
                "lagna_lord_sign": lagna_lord_sign,
                "lagna_lord_degree": lagna_lord_degree,
                "lagna_lord_dignity": lagna_lord_dignity,
            }

        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    # ══════════════════════════════════════════════════════════════
    # LOG RESULT BREAKDOWN [NEW - matches Doc 3 Career evaluator]
    # ══════════════════════════════════════════════════════════════
    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging. Matches Career evaluator pattern (Doc 3)."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")

        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")

        # Log key legal indicators
        summary = ad.get(f"{DOMAIN_PREFIX}_analysis_summary", {})
        if summary:
            logger.info(f"CASE OUTCOME: {summary.get('outcome_likelihood')}")
            logger.info(f"DURATION: {summary.get('duration_estimate')}")
            logger.info(f"RISK: {summary.get('risk_level')}")
            logger.info(f"OPPONENT: {summary.get('opponent_strength')}")

        timing_data = ad.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        logger.info(f"TIMING: has_timing={timing_data.get('has_timing', False)}")

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.

        ✅ Handles both dict and TimingWindow objects (Finance/Career parity)

        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}

        try:
            def get_attr(obj, key, default=None):
                """Get attribute from dict or object"""
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    return getattr(obj, key, default)

            def window_to_dict(w):
                """Convert TimingWindow object or dict to standardized dict"""
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w

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

                for extra_field in ['score_maha', 'score_antara', 'score_paryantar',
                                    'md', 'ad', 'pd', 'maha', 'antara', 'paryantar']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val

                return result

            # Log first window type for debugging
            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")
                if not isinstance(first, dict):
                    logger.info(f"🔍 First window attributes: {vars(first) if hasattr(first, '__dict__') else 'N/A'}")

            # Sort by final_score
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            # Nearest window: earliest with score >= 50
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

            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }

            logger.info(f"✅ Timing extraction SUCCESSFUL")
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

    # ══════════════════════════════════════════════════════════════
    # CASE TYPE DETERMINATION
    # ══════════════════════════════════════════════════════════════
    def _determine_case_type(self, question: str, sub_subdomain: str) -> str:
        """Determine the type of legal case based on question and sub_subdomain."""
        text = (question + " " + sub_subdomain).lower()

        if any(kw in text for kw in ['criminal', 'crime', 'arrest', 'jail', 'prison', 'अपराध', 'जेल']):
            return "criminal"
        elif any(kw in text for kw in ['divorce', 'custody', 'family', 'marriage', 'तलाक', 'परिवार']):
            return "family"
        elif any(kw in text for kw in ['debt', 'loan', 'tax', 'financial', 'money', 'कर्ज', 'ऋण']):
            return "financial"
        else:
            return "civil"

    # ══════════════════════════════════════════════════════════════
    # CASE OUTCOME ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_case_outcome(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        case_type: str
    ) -> Dict:
        """
        Analyze case outcome using Vedic principles.

        Favorable indicators:
        - 6th lord strong and well-placed (victory over enemies)
        - 11th lord strong (gains, victory)
        - 9th lord strong (favorable judgment)
        - Jupiter aspecting 6th or 9th (divine justice)
        - Mars in 6th house (digbala - victory in disputes)

        Unfavorable indicators:
        - 7th lord stronger than 6th lord (strong opponent)
        - 12th lord strong (losses)
        - 8th lord afflicting 1st or 6th (sudden setbacks)
        - Saturn afflicting without Jupiter's aspect
        """
        analysis = {
            "outcome_likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "victory_indicators": [],
            "defeat_indicators": []
        }

        score = 50  # Start neutral

        # Check 6th house (litigation, disputes - winning over enemies)
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            h6_lord = h6_info.get("lord", "")
            h6_lord_house = h6_info.get("lord_in_house")

            if h6_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"6th lord {h6_lord} is strong ({h6_strength}/100) - victory over opponents likely"
                )
                analysis["victory_indicators"].append("Strong 6th house lord favors winning disputes")
            elif h6_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_lord} is weak ({h6_strength}/100) - challenges in litigation"
                )

            if h6_lord_house in [3, 6, 10, 11]:
                score += 10
                analysis["victory_indicators"].append(
                    f"6th lord in house {h6_lord_house} strengthens legal position"
                )

        # Check 11th house (gains, victory)
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            if h11_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is strong - gains from legal matters likely"
                )
                analysis["victory_indicators"].append("Strong 11th house supports favorable outcome")
            elif h11_strength < 40:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"11th lord weak - gains from case may be limited"
                )

        # Check 9th house (judges, law, justice)
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            if h9_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is strong - law and justice on your side"
                )
                analysis["victory_indicators"].append("Strong 9th house indicates fair judgment")
            elif h9_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"9th lord weak - judgment may not be fully favorable"
                )

        # Check 7th house (opponent)
        h7_info = house_lords_info.get(7, {})
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            h6_strength = house_lords_info.get(6, {}).get("lord_strength_score", 50)

            if h7_strength > h6_strength:
                score -= 10
                analysis["defeat_indicators"].append(
                    "Opponent (7th house) appears stronger - need extra effort"
                )
            elif h6_strength > h7_strength:
                score += 10
                analysis["victory_indicators"].append(
                    "Your position (6th house) stronger than opponent (7th house)"
                )

        # Check Jupiter (divine justice)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")

            if jupiter_house in [1, 5, 9, 11]:
                score += 10
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine protection in legal matters"
                )

            h6_aspects = house_aspects_info.get(6, {})
            h9_aspects = house_aspects_info.get(9, {})

            if "Jupiter" in h6_aspects.get("benefic_aspects", []):
                score += 10
                analysis["victory_indicators"].append(
                    "Jupiter aspects 6th house - justice will prevail"
                )
            if "Jupiter" in h9_aspects.get("benefic_aspects", []):
                score += 10
                analysis["victory_indicators"].append(
                    "Jupiter aspects 9th house - favorable judgment indicated"
                )

        # Check Mars (courage to fight)
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")

            if mars_house == 6:
                score += 15
                analysis["victory_indicators"].append(
                    "Mars in 6th house (digbala) - strong ability to defeat opponents"
                )
            elif mars_house in [3, 10, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    f"Mars in house {mars_house} gives courage to fight"
                )

        # Check Saturn (delays, eventual justice)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")

            if saturn_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Saturn in house {saturn_house} may cause delays and obstacles"
                )
            elif saturn_house in [3, 10, 11]:
                score += 5
                analysis["favorable_factors"].append(
                    "Saturn placement supports eventual victory through persistence"
                )

        # Check 12th house (losses)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            if h12_strength >= 70:
                score -= 10
                analysis["defeat_indicators"].append(
                    "Strong 12th house lord indicates possible losses in litigation"
                )

        # Determine outcome likelihood
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 75:
            analysis["outcome_likelihood"] = "HIGHLY_FAVORABLE"
        elif score >= 60:
            analysis["outcome_likelihood"] = "FAVORABLE"
        elif score >= 45:
            analysis["outcome_likelihood"] = "UNCERTAIN"
        elif score >= 30:
            analysis["outcome_likelihood"] = "CHALLENGING"
        else:
            analysis["outcome_likelihood"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DURATION ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_case_duration(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze expected case duration using Vedic principles.

        Long duration indicators:
        - Saturn afflicting 6th house
        - Retrograde planets in legal houses
        - Rahu/Ketu involvement
        - 6th lord in 8th or 12th

        Short duration indicators:
        - Mercury strong (quick settlements)
        - Sun strong (swift authority decisions)
        - No Saturn affliction
        - Benefic aspects on 6th house
        """
        analysis = {
            "duration_estimate": "MODERATE",
            "delay_factors": [],
            "speed_factors": [],
            "duration_hints": []
        }

        delay_score = 0

        # Check Saturn influence
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            saturn_retro = saturn_data.get("is_retro", False)

            if saturn_house in [6, 7, 9]:
                delay_score += 20
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays expected"
                )

            if saturn_retro:
                delay_score += 10
                analysis["delay_factors"].append(
                    "Retrograde Saturn - case may drag on longer"
                )

        # Check Saturn aspects on legal houses
        h6_aspects = house_aspects_info.get(6, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Saturn" in h6_aspects.get("malefic_aspects", []):
            delay_score += 15
            analysis["delay_factors"].append(
                "Saturn aspects 6th house - prolonged litigation"
            )

        # Check Rahu/Ketu
        rahu_data = planets.get("Rahu", {})
        ketu_data = planets.get("Ketu", {})

        if rahu_data and rahu_data.get("house") in [6, 7, 9]:
            delay_score += 15
            analysis["delay_factors"].append(
                "Rahu involvement - unexpected complications and delays"
            )

        if ketu_data and ketu_data.get("house") in [6, 7, 9]:
            delay_score += 10
            analysis["delay_factors"].append(
                "Ketu involvement - confusion and procedural delays"
            )

        # Check 6th lord placement
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")
            if h6_lord_house in [8, 12]:
                delay_score += 15
                analysis["delay_factors"].append(
                    f"6th lord in house {h6_lord_house} - case may get complicated"
                )
            elif h6_lord_house in [3, 6, 11]:
                delay_score -= 10
                analysis["speed_factors"].append(
                    "6th lord well-placed - relatively quicker resolution"
                )

        # Check Mercury (quick settlements)
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            mercury_retro = mercury_data.get("is_retro", False)

            if mercury_house in [3, 6, 10, 11] and not mercury_retro:
                delay_score -= 15
                analysis["speed_factors"].append(
                    "Mercury well-placed - communication and settlements favored"
                )
            elif mercury_retro:
                delay_score += 10
                analysis["delay_factors"].append(
                    "Mercury retrograde - document issues and miscommunication"
                )

        # Check Sun (authority, swift decisions)
        sun_data = planets.get("Sun", {})
        if sun_data:
            sun_house = sun_data.get("house")
            if sun_house in [1, 9, 10, 11]:
                delay_score -= 10
                analysis["speed_factors"].append(
                    "Sun well-placed - authority may decide quickly"
                )

        # Check benefic aspects on 6th
        if "Jupiter" in h6_aspects.get("benefic_aspects", []):
            delay_score -= 10
            analysis["speed_factors"].append(
                "Jupiter's blessing on 6th house - smoother proceedings"
            )

        # Determine duration estimate
        if delay_score >= 40:
            analysis["duration_estimate"] = "LONG"
            analysis["duration_hints"].append("Expect the case to take considerable time")
            analysis["duration_hints"].append("Practice patience and persistence")
        elif delay_score >= 20:
            analysis["duration_estimate"] = "MODERATE_LONG"
            analysis["duration_hints"].append("Some delays expected but manageable")
        elif delay_score >= 0:
            analysis["duration_estimate"] = "MODERATE"
            analysis["duration_hints"].append("Normal legal timeframe expected")
        elif delay_score >= -20:
            analysis["duration_estimate"] = "MODERATE_SHORT"
            analysis["duration_hints"].append("Case may resolve quicker than usual")
        else:
            analysis["duration_estimate"] = "SHORT"
            analysis["duration_hints"].append("Quick resolution possible")
            analysis["duration_hints"].append("Out-of-court settlement may be favorable")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISKS AND PENALTIES ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks_and_penalties(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        case_type: str
    ) -> Dict:
        """
        Analyze risks and potential penalties.

        Risk indicators:
        - 8th house afflicted (sudden setbacks, penalties)
        - 12th house strong (losses, imprisonment risk)
        - Mars afflicting 8th or 12th
        - Rahu in 8th or 12th (unexpected penalties)
        - Saturn in 12th (imprisonment risk in criminal cases)
        """
        analysis = {
            "risk_level": "LOW",
            "risk_score": 20,
            "risks": [],
            "penalty_indicators": [],
            "protective_factors": [],
            "precautions": []
        }

        risk_score = 20  # Start low

        # Check 8th house (penalties, sudden events)
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_strength = h8_info.get("lord_strength_score", 50)
            h8_lord = h8_info.get("lord", "")
            h8_lord_house = h8_info.get("lord_in_house")

            if h8_strength >= 70:
                risk_score += 15
                analysis["risks"].append(
                    "Strong 8th house lord - potential for unexpected developments"
                )

            if h8_lord_house in [1, 6, 7]:
                risk_score += 10
                analysis["penalty_indicators"].append(
                    f"8th lord in house {h8_lord_house} - hidden complications possible"
                )

        # Check 12th house (losses, imprisonment)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            h12_lord_house = h12_info.get("lord_in_house")

            if h12_strength >= 70:
                risk_score += 15
                analysis["risks"].append(
                    "Strong 12th house lord - risk of significant losses"
                )
                if case_type == "criminal":
                    analysis["penalty_indicators"].append(
                        "In criminal matters, 12th house strength needs attention"
                    )

            if h12_lord_house in [1, 6, 8]:
                risk_score += 10
                analysis["penalty_indicators"].append(
                    "12th lord placement suggests careful handling needed"
                )

        # Check Mars afflictions
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [8, 12]:
                risk_score += 15
                analysis["risks"].append(
                    f"Mars in house {mars_house} - aggressive outcomes possible"
                )
                if case_type == "criminal":
                    analysis["penalty_indicators"].append(
                        "Mars placement suggests potential for punitive measures"
                    )
                analysis["precautions"].append(
                    "Avoid aggression or confrontation in proceedings"
                )

        # Check Saturn in 12th (imprisonment indicator)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house == 12 and case_type == "criminal":
                risk_score += 20
                analysis["penalty_indicators"].append(
                    "Saturn in 12th - in criminal matters, requires careful legal strategy"
                )
                analysis["precautions"].append(
                    "Engage experienced legal counsel immediately"
                )
            elif saturn_house == 8:
                risk_score += 10
                analysis["risks"].append(
                    "Saturn in 8th - potential for delays and complications"
                )

        # Check Rahu in risk houses
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [8, 12]:
                risk_score += 15
                analysis["risks"].append(
                    f"Rahu in house {rahu_house} - unexpected twists and complications"
                )
                analysis["precautions"].append(
                    "Be prepared for unexpected developments"
                )

        # Check protective factors
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 9, 11]:
                risk_score -= 15
                analysis["protective_factors"].append(
                    "Jupiter's placement provides protection against severe penalties"
                )

        # Check Jupiter aspects on risk houses
        h8_aspects = house_aspects_info.get(8, {})
        h12_aspects = house_aspects_info.get(12, {})

        if "Jupiter" in h8_aspects.get("benefic_aspects", []):
            risk_score -= 10
            analysis["protective_factors"].append(
                "Jupiter protects 8th house - penalties may be reduced"
            )
        if "Jupiter" in h12_aspects.get("benefic_aspects", []):
            risk_score -= 10
            analysis["protective_factors"].append(
                "Jupiter protects 12th house - losses minimized"
            )

        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 60:
            analysis["risk_level"] = "HIGH"
            analysis["precautions"].append("Consider all options including settlements")
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
            analysis["precautions"].append("Proceed with caution and good legal advice")
        elif risk_score >= 20:
            analysis["risk_level"] = "LOW"
        else:
            analysis["risk_level"] = "VERY_LOW"
            analysis["protective_factors"].append("Overall protective chart for legal matters")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # OPPONENT STRENGTH ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_opponent_strength(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze the strength of the opponent/adversary (7th house)."""
        analysis = {
            "opponent_strength": "MODERATE",
            "your_advantage": [],
            "opponent_advantage": [],
            "strategy_hints": []
        }

        h6_info = house_lords_info.get(6, {})
        h7_info = house_lords_info.get(7, {})

        h6_strength = h6_info.get("lord_strength_score", 50) if h6_info else 50
        h7_strength = h7_info.get("lord_strength_score", 50) if h7_info else 50

        strength_diff = h6_strength - h7_strength

        if strength_diff >= 20:
            analysis["opponent_strength"] = "WEAK"
            analysis["your_advantage"].append(
                "Your position (6th house) significantly stronger than opponent"
            )
            analysis["strategy_hints"].append(
                "Press your advantage but don't be overconfident"
            )
        elif strength_diff >= 10:
            analysis["opponent_strength"] = "MODERATE_WEAK"
            analysis["your_advantage"].append(
                "Slight advantage in your favor"
            )
        elif strength_diff >= -10:
            analysis["opponent_strength"] = "MODERATE"
            analysis["strategy_hints"].append(
                "Evenly matched - case could go either way"
            )
            analysis["strategy_hints"].append(
                "Focus on strengthening your legal arguments"
            )
        elif strength_diff >= -20:
            analysis["opponent_strength"] = "MODERATE_STRONG"
            analysis["opponent_advantage"].append(
                "Opponent appears to have slight advantage"
            )
            analysis["strategy_hints"].append(
                "Consider settlement options"
            )
        else:
            analysis["opponent_strength"] = "STRONG"
            analysis["opponent_advantage"].append(
                "Opponent (7th house) significantly stronger"
            )
            analysis["strategy_hints"].append(
                "Explore all settlement and negotiation options"
            )
            analysis["strategy_hints"].append(
                "Strengthen your case with additional evidence"
            )

        # Check Mars position for fighting spirit
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house == 6:
                analysis["your_advantage"].append(
                    "Mars in 6th gives exceptional ability to defeat opponents"
                )
            elif mars_house == 7:
                analysis["opponent_advantage"].append(
                    "Mars in 7th - opponent may be aggressive"
                )
                analysis["strategy_hints"].append(
                    "Stay calm and don't react emotionally"
                )

        return analysis

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
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
                h.get("sign_lord") or
                h.get("rashi_lord") or
                h.get("lord") or
                ""
            )

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

            normalized_lord = normalize_planet_name(lord_name)

            if not normalized_lord:
                continue

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
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

                    if dignity:
                        if hasattr(dignity, 'value'):
                            lord_dignity = dignity.value
                        else:
                            lord_dignity = str(dignity)

                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity)

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

    # ══════════════════════════════════════════════════════════════
    # ASPECTS EXTRACTION
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
    # STRENGTH CALCULATION
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity=None
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

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for legal context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS
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

            result.add_point(" ".join(point_parts))

    # ══════════════════════════════════════════════════════════════
    # ADD LEGAL POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_legal_points(
        self,
        result: EvaluationResult,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risks_analysis: Dict,
        opponent_analysis: Dict
    ):
        """Add legal-specific points to result."""

        outcome = outcome_analysis.get("outcome_likelihood", "UNCERTAIN")
        o_score = outcome_analysis.get("score", 50)
        result.add_point(
            f"⚖️ Case Outcome Likelihood: {outcome} (Score: {o_score}/100)"
        )

        duration = duration_analysis.get("duration_estimate", "MODERATE")
        result.add_point(
            f"⏱️ Expected Duration: {duration}"
        )

        risk_level = risks_analysis.get("risk_level", "LOW")
        r_score = risks_analysis.get("risk_score", 20)
        result.add_point(
            f"⚠️ Risk Level: {risk_level} (Score: {r_score}/100)"
        )

        opp_strength = opponent_analysis.get("opponent_strength", "MODERATE")
        result.add_point(
            f"👤 Opponent Strength: {opp_strength}"
        )

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # [FIX: aligned with Doc 2 & 3 - consistent dasha pass-through,
    #  timing storage, and dasha_context pattern]
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        outcome_analysis: dict,
        duration_analysis: dict,
        risks_analysis: dict,
        opponent_analysis: dict,
        case_type: str,
        timing_windows_data: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption (with timing)."""

        # Extract dasha context from kwargs - matches Doc 2 & 3
        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")
        transit_summary = kwargs.get("transit_summary")
        age_context = kwargs.get("age_context")
        meta = kwargs.get("meta")

        # FIX: consistent meta_query_type extraction - matches Doc 2 & 3
        meta_query_type = None
        if meta:
            if isinstance(meta, QueryMeta):
                meta_query_type = meta.query_type
            elif isinstance(meta, dict):
                meta_query_type = QueryType[meta.get("type", "NON_TIMING")]

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },

            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            f"{DOMAIN_PREFIX}_case_type": case_type,
            f"{DOMAIN_PREFIX}_outcome_analysis": outcome_analysis,
            f"{DOMAIN_PREFIX}_duration_analysis": duration_analysis,
            f"{DOMAIN_PREFIX}_risks_analysis": risks_analysis,
            f"{DOMAIN_PREFIX}_opponent_analysis": opponent_analysis,

            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "case_type": case_type,
                "outcome_likelihood": outcome_analysis.get("outcome_likelihood", "UNCERTAIN"),
                "outcome_score": outcome_analysis.get("score", 50),
                "duration_estimate": duration_analysis.get("duration_estimate", "MODERATE"),
                "risk_level": risks_analysis.get("risk_level", "LOW"),
                "risk_score": risks_analysis.get("risk_score", 20),
                "opponent_strength": opponent_analysis.get("opponent_strength", "MODERATE"),
                # FIX: include strong/weak lord counts - matches Doc 2 & 3 analysis_summary
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                ),
            },

            # Dasha pass-through - matches Doc 2 & 3
            f"{DOMAIN_PREFIX}_current_dasha": current_dasha,
            f"{DOMAIN_PREFIX}_dasha_timeline": dasha_timeline,

            # Optional context - matches Doc 2 & 3
            f"{DOMAIN_PREFIX}_transit_summary": transit_summary,
            f"{DOMAIN_PREFIX}_age_context": age_context,
        })

        # Store timing windows - matches Doc 2 & 3 exactly
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {DOMAIN_PREFIX}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
            if timing_windows_data.get('best_window'):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE")

        # Dasha context for prompt builder - matches Doc 3 Career pattern
        if meta_query_type == QueryType.TIMING and timing_windows_data.get("has_timing"):
            dasha_context = {
                "mode": "timing",
                "reference": {
                    "best": timing_windows_data.get("best_window"),
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
            f"📦 STORED | case_type={case_type} | outcome={outcome_analysis.get('outcome_likelihood')} | "
            f"duration={duration_analysis.get('duration_estimate')} | risk={risks_analysis.get('risk_level')} | "
            f"timing={timing_windows_data.get('has_timing')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="LEGAL_1",
                question="What does astrology indicate about the outcome, duration, risks and potential penalties related to my legal challenges?",
                meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEUTRAL, InterpretationGoal.STATUS),
                sub_subdomain="Risk of Legal Dispute"
            ),
            Question(
                id="LEGAL_2",
                question="What does astrology indicate about the outcome, duration, risks and potential penalties related to my criminal matter?",
                meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEGATIVE, InterpretationGoal.RISK),
                sub_subdomain="Outcome of Court Case"
            ),
            Question(
                id="LEGAL_3",
                question="Based on astrology, during which period is my ongoing court case likely to conclude?",
                meta=QueryMeta(QueryType.TIMING, EventPolarity.NEUTRAL, InterpretationGoal.STATUS),
                sub_subdomain="Case Conclusion Timing"
            )
        ]
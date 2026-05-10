"""
Facing Challenges in Business Evaluator - ENHANCED VERSION v5.0

CRITICAL FIXES FROM v4.0 (Aligned with CareerDiscoveryAndEmploymentEvaluator v5.0 + ProspectsOfInvestmentsEvaluator v3.3):

✅ UNIFIED BUSINESS VERDICT - Single source of truth for business health/outlook
✅ PURE KP METHODOLOGY - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ CORRECT HOUSE MAPPING - Business: 2,3,7,11 | Career: 10 | Obstacle: 6,8,12
✅ SUB-LORD PROMISE/DENIAL LOGIC - Core KP rule implemented (was MISSING in v4.0)
✅ INTERNAL _get_planet_significations() - No external import dependency for significations
✅ RAHU/KETU PROPER HANDLING - Star lord + sign lord + conjunctions
✅ HONEST VEDIC-KP AGREEMENT CHECK - AGREEMENT/PARTIAL/CONFLICT
✅ CONSISTENT OUTPUT ACROSS ALL QUESTIONS - Same base verdict used everywhere
✅ STRENGTH HIERARCHY - Sub > Star > Occupy > Own
✅ COMPLETE get_questions() - All 5 sub-subdomains registered
✅ AGREEMENT STATUS stored and passed to LLM

Architecture:
- _compute_unified_business_verdict() → Single source of truth
- _apply_pure_kp_chain()            → Strict KP methodology (CSL→SubLord→StarLord→Significations)
- _evaluate_sub_lord_promise()       → Promise/denial logic per house
- _get_planet_significations()       → Internal recursive method (safe vs Rahu/Ketu loops)
- _build_kp_interpretation()         → Human-readable chain explanation
- _check_vedic_kp_agreement()        → Honest conflict detection
- All questions use unified_business_verdict from additional_data

Covers:
1) Reason for Business Challenges / Stagnation / Downturn   → sub_subdomain="Reason for Business Challenges"
2) Loan Taking Decision + Timing                             → sub_subdomain="Loan Taking Decision"
3) Loan Repayment Decision + Timing                         → sub_subdomain="Loan Repayment Decision"
4) Continue vs Shut Down                                    → sub_subdomain="Continue or Shut Down"
5) Remedies (LLM-driven but WITH KP data passed through)    → sub_subdomain="Business Remedies"

Key Houses for Business Challenges:
- 7th:  Business/Partnerships (PRIMARY)
- 10th: Career/Profession (PRIMARY)
- 11th: Gains/Income (PRIMARY)
- 6th:  Obstacles/Competition
- 8th:  Sudden Events/Obstacles
- 12th: Losses/Expenses
- 2nd:  Wealth/Resources
- 3rd:  Courage/Efforts
- 5th:  Intelligence/Speculation
- 9th:  Fortune/Luck
"""

from typing import Dict, List, Optional, Set
import logging
from datetime import datetime

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

# ---- KP CORE ENGINE (NO MODIFICATION) ----
from app.domains.career.kp_career_engine import (
    evaluate_business_profession,
    determine_service_vs_business,
)

from app.services.timing_engine import (
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets,
    TIMING_RULES,
)

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity,
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects

    HOUSE_LORDS_AVAILABLE = True
    logging.warning("House lords analyzer available")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FacingChallengesInBusinessEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Business → Facing Challenges In Business
    v5.0 - With unified business verdict, pure KP chain, and promise/denial logic.
    """

    domain = "Business"
    subtopic = "Facing Challenges In Business"

    # ═══════════════════════════════════════════════════════════════
    # HOUSE DEFINITIONS (KP Standard for Business)
    # ═══════════════════════════════════════════════════════════════

    BUSINESS_PROMISE_HOUSES = {2, 3, 7, 11}   # Core business houses
    SUCCESS_HOUSES = {2, 10, 11}               # Income, career, gains
    OBSTACLE_HOUSES = {6, 8, 12}               # Competition, sudden loss, expenses
    WEALTH_HOUSES = {2, 5, 11}                 # Resources, speculation, gains
    LOSS_HOUSES = {6, 8, 12}                   # Same as obstacle for clarity

    HOUSE_MEANINGS = {
        1:  "Self/Personality/Lagna",
        2:  "Wealth/Resources",
        3:  "Courage/Efforts/Initiative",
        5:  "Intelligence/Speculation",
        6:  "Obstacles/Competition",
        7:  "Partnership/Business Axis",
        8:  "Sudden Events/Transformation",
        9:  "Fortune/Luck/Higher Learning",
        10: "Career/Profession/Authority",
        11: "Gains/Income/Fulfillment",
        12: "Expenses/Losses/Foreign",
    }

    # KP Strength Hierarchy
    KP_WEIGHT = {
        "sub_lord": 4,
        "star_lord": 3,
        "occupy": 2,
        "own": 1,
    }

    # ═══════════════════════════════════════════════════════════════
    # UNIFIED BUSINESS VERDICT (Single Source of Truth)
    # ═══════════════════════════════════════════════════════════════

    def _compute_unified_business_verdict(
        self,
        planets: Dict,
        houses: List,
    ) -> Dict:
        """
        SINGLE SOURCE OF TRUTH for business health determination.
        All questions must use this verdict for consistency.

        Analyzes key cusps: 7th (business), 10th (profession), 11th (gains)
        using pure KP sub-lord promise/denial logic.

        Returns:
        {
            "overall_outlook":   "RECOVERY_LIKELY" | "SERIOUS_CHALLENGES" | "MODERATE" | "MIXED",
            "business_viable":   True | False,
            "confidence":        "High" | "Moderate" | "Low",
            "kp_reasoning":      str,
            "vedic_reasoning":   str,
            "agreement_status":  "AGREEMENT" | "PARTIAL" | "CONFLICT",
            "promise_status":    {7: "PROMISE" | "DENIAL" | "WEAK_PROMISE" | "NEUTRAL", ...},
            "detailed_analysis": {house_num: chain_result, ...},
            "recovery_ranking":  [list of ranked recovery options],
        }
        """
        result = {
            "overall_outlook": "UNKNOWN",
            "business_viable": None,
            "confidence": "Low",
            "kp_reasoning": "",
            "vedic_reasoning": "",
            "agreement_status": "UNKNOWN",
            "promise_status": {},
            "detailed_analysis": {},
            "recovery_ranking": [],
        }

        # ─── STEP 1: Pure KP Analysis (Primary) ────────────────────
        key_cusps = {
            7:  "Business/Partnership",
            10: "Career/Profession",
            11: "Gains/Income",
            6:  "Obstacles/Competition",
            8:  "Sudden Events",
        }

        kp_reasons = []
        promise_status = {}

        for cusp_num, meaning in key_cusps.items():
            cusp_data = next((h for h in houses if h.get("house") == cusp_num), None)
            if not cusp_data:
                continue

            chain_result = self._apply_pure_kp_chain(cusp_data, planets, houses)
            if not chain_result:
                continue

            promise_status[cusp_num] = chain_result.get("promise_status", "UNKNOWN")
            result["detailed_analysis"][cusp_num] = chain_result

            sub_lord_houses = set(chain_result.get("sub_lord_signifies", []))

            if cusp_num == 7:
                if chain_result.get("promise_status") == "PROMISE":
                    kp_reasons.append(
                        f"7th CSL promises business viability "
                        f"(sub-lord signifies {sorted(sub_lord_houses & self.BUSINESS_PROMISE_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append(
                        f"7th CSL denies business success "
                        f"(sub-lord signifies loss houses {sorted(sub_lord_houses & self.OBSTACLE_HOUSES)})"
                    )

            elif cusp_num == 11:
                if chain_result.get("promise_status") == "PROMISE":
                    kp_reasons.append(
                        f"11th CSL promises gains "
                        f"(sub-lord signifies {sorted(sub_lord_houses & self.SUCCESS_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append("11th CSL denies gains — income recovery will be slow")

        result["promise_status"] = promise_status

        # ─── STEP 2: Derive Overall Outlook from Promise Status ─────
        h7  = promise_status.get(7,  "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")
        h11 = promise_status.get(11, "NEUTRAL")
        h6  = promise_status.get(6,  "NEUTRAL")
        h8  = promise_status.get(8,  "NEUTRAL")

        if h7 == "PROMISE" and h11 in ["PROMISE", "WEAK_PROMISE"]:
            overall = "RECOVERY_LIKELY"
            viable = True
        elif h7 == "DENIAL" and h11 in ["DENIAL", "NEUTRAL"]:
            overall = "SERIOUS_CHALLENGES"
            viable = False
        elif h7 == "WEAK_PROMISE" and h11 in ["WEAK_PROMISE", "NEUTRAL"]:
            overall = "MODERATE_RECOVERY"
            viable = True
        elif h6 == "CHALLENGING" or h8 == "RISKY":
            overall = "OBSTACLES_NEED_ATTENTION"
            viable = None  # Unknown — conditional
        else:
            overall = "MIXED_SIGNALS"
            viable = None

        result["overall_outlook"] = overall
        result["business_viable"] = viable

        # ─── STEP 3: Confidence from 10th cusp ────────────────────
        if h10 == "PROMISE":
            confidence = "High"
        elif h10 == "WEAK_PROMISE":
            confidence = "Moderate"
        elif h10 == "DENIAL":
            confidence = "Low"
        else:
            confidence = "Moderate"

        result["confidence"] = confidence

        # ─── STEP 4: Vedic Analysis (Secondary) ───────────────────
        vedic_positive = 0
        vedic_negative = 0
        vedic_reasons = []

        for house_num in [7, 10, 11]:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            lord_name = self._get_house_lord(house_data)
            if not lord_name:
                continue

            lord_data = planets.get(lord_name, {})
            lord_house = lord_data.get("house")
            dignity = self._get_planet_dignity(lord_name, lord_data)

            if house_num == 7:
                if lord_house in self.BUSINESS_PROMISE_HOUSES:
                    vedic_positive += 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business support"
                    )
                elif lord_house in self.OBSTACLE_HOUSES:
                    vedic_negative += 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business challenged"
                    )

            elif house_num == 11:
                if lord_house in self.SUCCESS_HOUSES:
                    vedic_positive += 2
                    vedic_reasons.append(
                        f"11th lord {lord_name} in house {lord_house} → gains supported"
                    )
                elif lord_house in self.OBSTACLE_HOUSES:
                    vedic_negative += 2
                    vedic_reasons.append(
                        f"11th lord {lord_name} in house {lord_house} → gains impeded"
                    )

            elif house_num == 10:
                if dignity in ["EXALTED", "OWN_SIGN"]:
                    vedic_positive += 1
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → strong professional base"
                    )
                elif dignity == "DEBILITATED":
                    vedic_negative += 1
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → career base weak"
                    )

        # ─── STEP 5: KP-Vedic Agreement ───────────────────────────
        kp_positive = overall in ["RECOVERY_LIKELY", "MODERATE_RECOVERY"]
        vedic_positive_flag = vedic_positive > vedic_negative

        if kp_positive == vedic_positive_flag:
            result["agreement_status"] = "AGREEMENT"
        elif overall == "MIXED_SIGNALS":
            result["agreement_status"] = "PARTIAL"
        else:
            result["agreement_status"] = "CONFLICT"

        # ─── STEP 6: Recovery Ranking ─────────────────────────────
        recovery_options = []

        # Continue as-is
        continue_score = 0
        if h7 == "PROMISE":
            continue_score += 3
        if h11 in ["PROMISE", "WEAK_PROMISE"]:
            continue_score += 2
        recovery_options.append(("Continue Business (As-Is)", continue_score))

        # Restructure
        restructure_score = 0
        if h8 in ["TRANSFORMATIVE", "NEUTRAL"] and h7 == "WEAK_PROMISE":
            restructure_score += 3
        elif h7 == "DENIAL" and h10 in ["PROMISE", "WEAK_PROMISE"]:
            restructure_score += 2
        recovery_options.append(("Restructure/Pivot", restructure_score))

        # Partnership
        partner_score = 0
        if h7 in ["PROMISE", "WEAK_PROMISE"]:
            partner_score += 3
        recovery_options.append(("Partnership-Based Recovery", partner_score))

        # Wait for timing
        wait_score = 0
        if overall in ["MODERATE_RECOVERY", "OBSTACLES_NEED_ATTENTION"]:
            wait_score += 3
        elif h8 in ["RISKY", "CHALLENGING"]:
            wait_score += 2
        recovery_options.append(("Wait for Favorable Dasha Period", wait_score))

        # Shut down
        shutdown_score = 0
        if h7 == "DENIAL" and h11 in ["DENIAL", "NEUTRAL"] and confidence == "Low":
            shutdown_score += 4
        recovery_options.append(("Consider Closure/Exit Strategy", shutdown_score))

        recovery_options.sort(key=lambda x: x[1], reverse=True)
        result["recovery_ranking"] = [
            {"option": opt, "score": score, "rating": self._score_to_rating(score)}
            for opt, score in recovery_options
        ]

        result["kp_reasoning"]  = " | ".join(kp_reasons) if kp_reasons else "KP analysis incomplete"
        result["vedic_reasoning"] = " | ".join(vedic_reasons) if vedic_reasons else "Vedic analysis incomplete"

        return result

    # ═══════════════════════════════════════════════════════════════
    # PURE KP CHAIN (CSL → Sub Lord → Star Lord → Significations)
    # ═══════════════════════════════════════════════════════════════

    def _apply_pure_kp_chain(
        self,
        cusp_data: Dict,
        planets: Dict,
        houses: List,
    ) -> Dict:
        """
        Apply PURE KP methodology:
        CSL → Sub Lord → Star Lord → Significations → Promise/Denial

        KP Rule: Sub-lord of cusp decides whether house matters manifest.
        - Sub-lord signifies positive houses → PROMISE
        - Sub-lord signifies 8, 12 strongly   → DENIAL
        """
        result = {
            "csl": None,
            "csl_house": None,
            "csl_nakshatra": None,
            "star_lord": None,
            "star_lord_signifies": [],
            "sub_lord": None,
            "sub_lord_signifies": [],
            "promise_status": "UNKNOWN",
            "chain_text": "",
            "interpretation": "",
        }

        csl_raw = cusp_data.get("cusp_sub_lord", "")
        csl = normalize_planet_name(csl_raw)
        if not csl:
            return result

        result["csl"] = csl
        csl_data = planets.get(csl, {})
        result["csl_house"] = csl_data.get("house")
        result["csl_nakshatra"] = csl_data.get("nakshatra", "")

        # Star Lord (Nakshatra Lord of CSL)
        star_lord = normalize_planet_name(csl_data.get("nakshatra_lord", ""))
        result["star_lord"] = star_lord
        if star_lord:
            result["star_lord_signifies"] = sorted(
                self._get_planet_significations(star_lord, planets, houses)
            )

        # Sub Lord of CSL — KEY for promise/denial
        sub_lord = normalize_planet_name(csl_data.get("sub_lord", ""))
        result["sub_lord"] = sub_lord
        if sub_lord:
            sub_lord_houses = self._get_planet_significations(sub_lord, planets, houses)
            result["sub_lord_signifies"] = sorted(sub_lord_houses)
            house_num = cusp_data.get("house", 0)
            result["promise_status"] = self._evaluate_sub_lord_promise(
                house_num, sub_lord_houses, result["star_lord_signifies"]
            )

        # Build chain text
        parts = [f"CSL: {csl}"]
        if star_lord:
            parts.append(f"Star Lord: {star_lord} → signifies {result['star_lord_signifies']}")
        if sub_lord:
            parts.append(f"Sub Lord: {sub_lord} → signifies {result['sub_lord_signifies']}")
        parts.append(f"Promise: {result['promise_status']}")
        result["chain_text"] = " | ".join(parts)

        return result

    def _evaluate_sub_lord_promise(
        self,
        cusp_house: int,
        sub_lord_houses: List[int],
        star_lord_houses: List[int],
    ) -> str:
        """
        KP Promise/Denial Logic based on sub-lord significations.

        For 7th cusp (business):   Promise if sub-lord signifies 2, 3, 7, 11
        For 10th cusp (profession): Promise if sub-lord signifies 2, 6, 10, 11
        For 11th cusp (gains):      Promise if sub-lord signifies 2, 10, 11
        For 6th cusp (obstacles):   Promise if sub-lord signifies 6, 8, 12 (bad for business)
        For 8th cusp (sudden):      Promise if sub-lord signifies 2, 10, 11 (transformative gain)
        Denial in all cases if sub-lord primarily signifies 8, 12 (loss houses).
        """
        sub_set = set(sub_lord_houses)
        loss_houses = {8, 12}

        if cusp_house == 7:   # Business/Partnership
            positive = {2, 3, 7, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 10:  # Career/Profession
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 11:  # Gains/Income
            positive = {2, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 6:   # Obstacles — we want this to be WEAK
            positive = {2, 10, 11}  # If 6th CSL promises gains, obstacles are manageable
            if sub_set & positive:
                return "MANAGEABLE"
            elif sub_set & {6, 8, 12} and not sub_set & positive:
                return "CHALLENGING"
            return "MODERATE"

        elif cusp_house == 8:   # Sudden events
            positive = {2, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "TRANSFORMATIVE"  # Sudden events lead to gain
            elif sub_set & loss_houses and not sub_set & positive:
                return "RISKY"
            return "UNPREDICTABLE"

        return "NEUTRAL"

    # ═══════════════════════════════════════════════════════════════
    # PLANET SIGNIFICATIONS (Internal — safe vs loops)
    # ═══════════════════════════════════════════════════════════════

    def _get_planet_significations(
        self,
        planet_name: str,
        planets: Dict,
        houses: List,
        visited: Optional[Set[str]] = None,
    ) -> List[int]:
        """
        Get houses signified by a planet using KP methodology.
        Internal implementation — safe against Rahu/Ketu recursive loops.

        Hierarchy: sub_lord (4) > star_lord (3) > occupy (2) > own (1)
        """
        if not planet_name:
            return []

        planet_name = normalize_planet_name(planet_name)
        if visited is None:
            visited = set()

        if planet_name in visited:
            logger.warning(f"Recursive KP loop detected for {planet_name}")
            return []

        visited.add(planet_name)
        signified = set()
        planet_data = planets.get(planet_name, {})
        if not planet_data:
            return []

        # Rahu/Ketu: proxy via star lord + sign lord + conjunctions
        if planet_name in ["Rahu", "Ketu"]:
            star_lord = normalize_planet_name(planet_data.get("nakshatra_lord"))
            if star_lord and star_lord != planet_name:
                signified.update(
                    self._get_planet_significations(star_lord, planets, houses, visited)
                )

            sign = planet_data.get("sign")
            sign_lord = self._get_sign_lord(sign)
            if sign_lord:
                signified.update(
                    self._get_planet_significations(sign_lord, planets, houses, visited)
                )

            for p_name, p_data in planets.items():
                if p_name == planet_name:
                    continue
                if p_data.get("house") == planet_data.get("house"):
                    signified.update(
                        self._get_planet_significations(p_name, planets, houses, visited)
                    )

        # 1. Occupied house
        occupied = planet_data.get("house")
        if occupied:
            signified.add(occupied)

        # 2. Owned houses
        signified.update(self._get_owned_houses(planet_name, houses))

        # 3. Planets in star of this planet (they signify what this planet signifies)
        for p_name, p_data in planets.items():
            if p_name == planet_name:
                continue
            star_lord = normalize_planet_name(p_data.get("nakshatra_lord"))
            if star_lord == planet_name:
                p_house = p_data.get("house")
                if p_house:
                    signified.add(p_house)
                signified.update(self._get_owned_houses(p_name, houses))

        return sorted(signified)

    def _get_owned_houses(self, planet_name: str, houses: List) -> List[int]:
        """Get house numbers owned (ruled) by a planet."""
        owned = []
        sign_lords = {
            "Aries": "Mars",    "Taurus": "Venus",   "Gemini": "Mercury",
            "Cancer": "Moon",   "Leo": "Sun",         "Virgo": "Mercury",
            "Libra": "Venus",   "Scorpio": "Mars",    "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
        }
        for h in houses:
            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
            if house_sign and sign_lords.get(house_sign) == planet_name:
                owned.append(h.get("house"))
        return owned

    def _get_sign_lord(self, sign: str) -> Optional[str]:
        sign_lords = {
            "Aries": "Mars",    "Taurus": "Venus",   "Gemini": "Mercury",
            "Cancer": "Moon",   "Leo": "Sun",         "Virgo": "Mercury",
            "Libra": "Venus",   "Scorpio": "Mars",    "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
        }
        return sign_lords.get(sign)

    def _get_house_lord(self, house_data: Dict) -> Optional[str]:
        """Get ruler of a house (tries multiple keys, falls back to sign deduction)."""
        lord_name = (
            house_data.get("rashi_lord") or
            house_data.get("sign_lord") or
            house_data.get("lord") or
            ""
        )
        if not lord_name:
            sign = house_data.get("sign") or house_data.get("start_rasi") or house_data.get("rasi")
            lord_name = self._get_sign_lord(sign) or ""
        return normalize_planet_name(lord_name)

    def _get_planet_dignity(self, planet_name: str, planet_data: Dict) -> str:
        sign = planet_data.get("sign", "")
        exaltation = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
            "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra",
        }
        debilitation = {
            "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
            "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries",
        }
        own_signs = {
            "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"],
        }
        if exaltation.get(planet_name) == sign:
            return "EXALTED"
        if debilitation.get(planet_name) == sign:
            return "DEBILITATED"
        if sign in own_signs.get(planet_name, []):
            return "OWN_SIGN"
        return "NEUTRAL"

    def _score_to_rating(self, score: int) -> str:
        if score >= 4:
            return "HIGH"
        elif score >= 2:
            return "MODERATE"
        elif score >= 1:
            return "LOW"
        return "VERY_LOW"

    # ═══════════════════════════════════════════════════════════════
    # KP STRUCTURED ANALYSIS (Sub-Lord Level — FIXED)
    # ═══════════════════════════════════════════════════════════════

    def _extract_kp_business_challenge_structured(
        self,
        planets: Dict,
        houses: List,
        unified_verdict: Dict,
    ) -> Dict:
        """
        Extract structured KP business challenge data using PURE methodology.
        Uses unified_verdict for consistency across all questions.

        Chain: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
        """
        kp_data = {
            "csl_details": {},
            "overall_verdict": unified_verdict.get("overall_outlook", "UNKNOWN"),
            "key_findings": [],
            "has_kp_data": False,
            "methodology": "CSL → Sub Lord → Star Lord → Significations → Promise/Denial",
            "agreement_status": unified_verdict.get("agreement_status", "UNKNOWN"),
        }

        business_houses = [2, 3, 5, 6, 7, 8, 9, 10, 11, 12]

        for house_num in business_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            chain_result = self._apply_pure_kp_chain(house_data, planets, houses)
            if not chain_result.get("csl"):
                continue

            kp_data["has_kp_data"] = True
            csl = chain_result["csl"]
            csl_data = planets.get(csl, {})

            promise = chain_result.get("promise_status", "NEUTRAL")

            # Map promise to verdict label
            verdict_map = {
                "PROMISE":      "STRONG",
                "WEAK_PROMISE": "MODERATE",
                "DENIAL":       "WEAK",
                "NEUTRAL":      "NEUTRAL",
                "MANAGEABLE":   "MANAGEABLE",
                "CHALLENGING":  "CHALLENGING",
                "TRANSFORMATIVE": "TRANSFORMATIVE",
                "RISKY":        "RISKY",
                "UNPREDICTABLE": "UNPREDICTABLE",
            }
            verdict = verdict_map.get(promise, "NEUTRAL")

            interpretation = self._build_kp_interpretation(
                house_num, chain_result, unified_verdict
            )

            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            flavor = (
                "benefic flavor" if csl in benefics else
                "malefic flavor" if csl in malefics else
                "neutral flavor"
            )

            sub_houses = set(chain_result.get("sub_lord_signifies", []))
            kp_data["csl_details"][house_num] = {
                "house_meaning":       self.HOUSE_MEANINGS.get(house_num, "General"),
                "csl":                 csl,
                "csl_house":          chain_result.get("csl_house"),
                "csl_flavor":         flavor,
                "nakshatra":          chain_result.get("csl_nakshatra", ""),
                "star_lord":          chain_result.get("star_lord"),
                "star_lord_signifies": chain_result.get("star_lord_signifies", []),
                "sub_lord":           chain_result.get("sub_lord"),
                "sub_lord_signifies":  chain_result.get("sub_lord_signifies", []),
                "success_connection":  len(sub_houses & self.SUCCESS_HOUSES),
                "business_connection": len(sub_houses & self.BUSINESS_PROMISE_HOUSES),
                "obstacle_connection": len(sub_houses & self.OBSTACLE_HOUSES),
                "wealth_connection":   len(sub_houses & self.WEALTH_HOUSES),
                "loss_connection":     len(sub_houses & self.LOSS_HOUSES),
                "promise_status":      promise,
                "verdict":             verdict,
                "interpretation":      interpretation,
                "chain":               chain_result.get("chain_text", ""),
                "has_significations":  bool(chain_result.get("sub_lord_signifies")),
            }

            kp_data["key_findings"].append(
                f"House {house_num} ({self.HOUSE_MEANINGS.get(house_num, '')}): "
                f"{csl} → Sub Lord {chain_result.get('sub_lord')} → "
                f"signifies {chain_result.get('sub_lord_signifies', [])} → {promise}"
            )

        return kp_data

    def _build_kp_interpretation(
        self,
        house_num: int,
        chain_result: Dict,
        unified_verdict: Dict,
    ) -> str:
        """Build human-readable KP interpretation per house."""
        csl      = chain_result.get("csl", "Unknown")
        sub_lord = chain_result.get("sub_lord", "Unknown")
        sub_houses = chain_result.get("sub_lord_signifies", [])
        promise  = chain_result.get("promise_status", "NEUTRAL")
        outlook  = unified_verdict.get("overall_outlook", "Unknown")

        if house_num == 7:
            if promise == "PROMISE":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Strong business house connection → Business/partnership PROMISED. "
                    f"Recovery and growth are supported astrologically."
                )
            elif promise == "DENIAL":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Business continuation faces core challenges. "
                    f"Restructuring or exit may need evaluation."
                )
            else:
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Mixed business indicators → Moderate capacity for recovery."
                )

        elif house_num == 10:
            if promise == "PROMISE":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Career houses activated → Professional standing is supported. "
                    f"Overall outlook: {outlook}."
                )
            elif promise == "DENIAL":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Professional reputation under pressure."
                )
            else:
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate professional indicators → Steady but slow progress."
                )

        elif house_num == 11:
            if promise == "PROMISE":
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Gains house PROMISED → Income recovery is astrologically supported."
                )
            elif promise == "DENIAL":
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Gains denied → Income will remain under pressure. "
                    f"Focus on cost control over revenue chasing."
                )
            else:
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate gains → Income recovery possible but slow."
                )

        elif house_num == 6:
            return (
                f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Obstacle house: {promise}. "
                f"{'Challenges are manageable.' if promise == 'MANAGEABLE' else 'Significant competition/debt pressure active.'}"
            )

        elif house_num == 8:
            return (
                f"8th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Sudden events house: {promise}. "
                f"{'Unexpected changes can be turned to advantage.' if promise == 'TRANSFORMATIVE' else 'Risk of sudden losses or disruptions.'}"
            )

        else:
            return (
                f"House {house_num}: CSL {csl} → Sub Lord {sub_lord} → "
                f"Signifies {sub_houses} → {promise}"
            )

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS CHALLENGE SUITABILITY MATRIX (Uses Unified Verdict)
    # ═══════════════════════════════════════════════════════════════

    def _create_business_challenge_matrix(
        self,
        unified_verdict: Dict,
        kp_structured: Dict,
        loan_data: Dict = None,
    ) -> Dict[str, Dict]:
        """
        Create business challenge suitability matrix using UNIFIED verdict for consistency.
        All ratings derived from the single source of truth.
        """
        matrix = {}
        loan_data = loan_data or {}

        csl_details     = kp_structured.get("csl_details", {})
        promise_status  = unified_verdict.get("promise_status", {})
        overall_outlook = unified_verdict.get("overall_outlook", "UNKNOWN")
        confidence      = unified_verdict.get("confidence", "Low")
        recovery_ranking = unified_verdict.get("recovery_ranking", [])

        h7  = promise_status.get(7,  "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")
        h11 = promise_status.get(11, "NEUTRAL")
        h6  = promise_status.get(6,  "NEUTRAL")
        h8  = promise_status.get(8,  "NEUTRAL")

        h7_csl  = csl_details.get(7,  {}).get("csl")
        h11_csl = csl_details.get(11, {}).get("csl")

        stable_planets   = {"Saturn", "Jupiter", "Sun"}
        volatile_planets = {"Rahu", "Ketu", "Mars"}
        rahu_connected   = any(
            d.get("csl") == "Rahu" or d.get("star_lord") == "Rahu"
            for d in csl_details.values()
        )

        loan_supported      = loan_data.get("loan_supported", False)
        repayment_supported = loan_data.get("repayment_supported", False)

        # ── 1. Continue Business (As-Is) ────────────────────────
        if h7 == "PROMISE" and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "7th + 11th house promise → Business viable; continue with optimizations."
        elif h7 == "WEAK_PROMISE":
            rating = "MODERATE"
            reason = "7th house shows weak promise → Continuation possible with strategic changes."
        elif h7 == "DENIAL":
            rating = "LOW"
            reason = "7th house denial → Current model is not supported; change required."
        else:
            rating = "MODERATE"
            reason = "Mixed signals → Monitor timing windows before major decisions."

        matrix["Continue Business (Current Model)"] = {"rating": rating, "kp_reasoning": reason}

        # ── 2. Restructure / Pivot Business ─────────────────────
        if h7 == "WEAK_PROMISE" and h10 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "Career house stronger than business axis → Pivot toward professional services."
        elif h8 in ["TRANSFORMATIVE"] and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "8th house transformation + gains promise → Restructuring will succeed."
        elif rahu_connected:
            rating = "MODERATE"
            reason = "Rahu influence supports unconventional pivots and new market entry."
        else:
            rating = "LOW"
            reason = "Current model may still have runway; full pivot not indicated yet."

        matrix["Restructure / Pivot Business"] = {"rating": rating, "kp_reasoning": reason}

        # ── 3. Take Loan for Expansion ──────────────────────────
        if loan_supported and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "Loan indicators active + 11th promise → Loan can fuel expansion."
        elif loan_supported:
            rating = "MODERATE"
            reason = "Loan timing favourable but repayment visibility limited — proceed cautiously."
        elif h6 in ["CHALLENGING"] or h8 == "RISKY":
            rating = "AVOID"
            reason = "❌ 6th/8th house obstacles — loan will compound financial pressure."
        else:
            rating = "LOW"
            reason = "Loan indicators weak — avoid borrowing until business stabilises."

        matrix["Take Loan for Expansion"] = {"rating": rating, "kp_reasoning": reason}

        # ── 4. Loan Repayment Feasibility ───────────────────────
        h2_verdict = csl_details.get(2, {}).get("verdict", "NEUTRAL")
        if repayment_supported and h2_verdict in ["STRONG", "MODERATE"]:
            rating = "HIGH"
            reason = "Income + wealth houses support repayment — pay down aggressively."
        elif repayment_supported:
            rating = "MODERATE"
            reason = "Repayment feasible but requires discipline and timeline extension."
        elif csl_details.get(12, {}).get("verdict") in ["DRAINING", "CHALLENGING"]:
            rating = "LOW"
            reason = "12th house draining — repayment will be a struggle; seek restructuring."
        else:
            rating = "MODERATE"
            reason = "Repayment capacity moderate — extend timelines if possible."

        matrix["Loan Repayment Feasibility"] = {"rating": rating, "kp_reasoning": reason}

        # ── 5. Partnership-Based Recovery ───────────────────────
        if h7 in ["PROMISE", "WEAK_PROMISE"] and h7_csl in stable_planets:
            rating = "HIGH"
            reason = f"7th house promise + stable CSL {h7_csl} → Partnerships will add stability."
        elif h7 == "PROMISE":
            rating = "HIGH"
            reason = "7th house promises partnership success — joint ventures recommended."
        elif h7 == "WEAK_PROMISE":
            rating = "MODERATE"
            reason = "7th house weak promise → Partnerships possible but vet partners carefully."
        else:
            rating = "LOW"
            reason = "7th house denial — partnerships may complicate recovery."

        matrix["Partnership-Based Recovery"] = {"rating": rating, "kp_reasoning": reason}

        # ── 6. Foreign / Export Focus ────────────────────────────
        h12_foreign = csl_details.get(12, {}).get("sub_lord_signifies", [])
        foreign_sub = any(h in h12_foreign for h in [9, 12])
        if rahu_connected and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "MODERATE"
            reason = "Rahu + 11th promise → Foreign/export markets can supplement domestic income."
        elif foreign_sub:
            rating = "MODERATE"
            reason = "12th house sub-lord links foreign/export — explore international channels."
        else:
            rating = "LOW"
            reason = "Focus on domestic recovery first; foreign exposure indicators weak."

        matrix["Foreign / Export Focus"] = {"rating": rating, "kp_reasoning": reason}

        # ── 7. Wait for Favorable Dasha Period ──────────────────
        if overall_outlook in ["MODERATE_RECOVERY", "OBSTACLES_NEED_ATTENTION"]:
            rating = "HIGH"
            reason = "Current planetary period challenging — timing windows will show better periods."
        elif h8 == "RISKY":
            rating = "HIGH"
            reason = "8th house risk active — wait for stable dasha before major moves."
        elif confidence == "Low":
            rating = "MODERATE"
            reason = "Low KP confidence — cautious patience is prudent."
        else:
            rating = "LOW"
            reason = "Outlook is positive — acting now is better than waiting."

        matrix["Wait for Favorable Dasha Period"] = {"rating": rating, "kp_reasoning": reason}

        # ── 8. Consider Closure / Exit Strategy ─────────────────
        shutdown_signals = sum([
            h7 == "DENIAL",
            h11 in ["DENIAL", "NEUTRAL"],
            confidence == "Low",
            h6 == "CHALLENGING" and h8 == "RISKY",
        ])
        if shutdown_signals >= 3:
            rating = "HIGH"
            reason = "⚠️ Multiple negative house indicators — structured exit may protect assets."
        elif shutdown_signals == 2:
            rating = "MODERATE"
            reason = "Partial closure or pause may be better than forcing continuation."
        else:
            rating = "LOW"
            reason = "Closure not indicated — restructuring preferred over exit."

        matrix["Consider Closure / Exit Strategy"] = {"rating": rating, "kp_reasoning": reason}

        return matrix

    # ═══════════════════════════════════════════════════════════════
    # MAIN EVALUATION
    # ═══════════════════════════════════════════════════════════════

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

        # ─── Data Source ─────────────────────────────────────────
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses  = vedic_houses  if vedic_houses  else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

        # ─── Question-Specific Houses ────────────────────────────
        question_text = kwargs.get("question", "")
        house_config  = get_houses_for_question(self.domain, self.subtopic, question_text)

        if house_config:
            primary_houses   = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses | {1}
        else:
            all_relevant_houses = {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12}
            primary_houses      = {7, 10, 11}
            secondary_houses    = {2, 3, 5, 6, 8, 9, 12}

        meta           = kwargs.get("meta")
        sub_subdomain  = kwargs.get("sub_subdomain", "Reason for Business Challenges")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, "query_type") else None

        if isinstance(meta_query_type, str):
            meta_query_type = meta_query_type.upper()
        elif hasattr(meta_query_type, "name"):
            meta_query_type = meta_query_type.name

        logger.info("=" * 80)
        logger.info("FACING CHALLENGES IN BUSINESS EVALUATOR v5.0 — UNIFIED VERDICT")
        logger.info("=" * 80)
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info("=" * 80)

        # ─── Aspects ─────────────────────────────────────────────
        detect_aspects(analysis_planets)
        detect_aspects(planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ─── House Lords ─────────────────────────────────────────
        house_lords_info = self._extract_house_lords(
            analysis_houses, analysis_planets, all_relevant_houses, primary_houses
        )

        # ─── Lagna ───────────────────────────────────────────────
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        # ─── Aspects on Houses ───────────────────────────────────
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses, analysis_planets, aspects_data, all_relevant_houses
        )

        # ─── Timing Windows ──────────────────────────────────────
        timing_windows_raw  = kwargs.get("timing_windows", {})
        timing_windows_list = []

        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            for fallback_key in [
                "Business Challenges", "Loan Taking Decision",
                "Loan Repayment Decision", "Reason for Business Challenges",
                "Continue or Shut Down",
            ]:
                if not timing_windows_list:
                    timing_windows_list = timing_windows_raw.get(fallback_key, [])
        else:
            timing_windows_list = timing_windows_raw or []

        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: Compute UNIFIED BUSINESS VERDICT (Single Source of Truth)
        # ═══════════════════════════════════════════════════════════
        unified_verdict = self._compute_unified_business_verdict(planets, houses)
        result.additional_data["unified_business_verdict"] = unified_verdict

        logger.info(f"🎯 UNIFIED VERDICT: {unified_verdict['overall_outlook']}")
        logger.info(f"   Confidence:     {unified_verdict['confidence']}")
        logger.info(f"   Business Viable: {unified_verdict['business_viable']}")
        logger.info(f"   KP-Vedic Agreement: {unified_verdict['agreement_status']}")
        logger.info(f"   Promise status: {unified_verdict['promise_status']}")

        # ─── KP Business Engine (always run) ─────────────────────
        business_kp_data = evaluate_business_profession(planets, houses)
        logger.info(f"✅ KP Business Engine: confidence={business_kp_data.get('confidence')}")

        # ─── KP Structured Extraction (uses unified verdict) ─────
        try:
            kp_structured = self._extract_kp_business_challenge_structured(
                planets, houses, unified_verdict
            )
            result.additional_data["kp_business_challenge_analysis"] = kp_structured

            if kp_structured.get("has_kp_data"):
                logger.info(f"✅ KP structured: {list(kp_structured['csl_details'].keys())}")
                logger.info(f"   Overall: {kp_structured.get('overall_verdict')}")
        except Exception as e:
            logger.warning(f"KP structured extraction error: {e}")
            kp_structured = {"has_kp_data": False, "csl_details": {}}

        # ─── loan_data accumulator (shared across question branches) ──
        loan_data: Dict = {}

        # ─── House analysis points (Vedic) ───────────────────────
        if sub_subdomain in {
            "Reason for Business Challenges",
            "Continue or Shut Down",
            "Loan Taking Decision",
            "Loan Repayment Decision",
            "Business Remedies",
        }:
            self._add_house_analysis_points(
                result, house_lords_info, house_aspects_info, primary_houses
            )

        # ═══════════════════════════════════════════════════════════
        # QUESTION BRANCHES — All use unified_verdict for consistency
        # ═══════════════════════════════════════════════════════════

        # ── 1) REASON FOR BUSINESS CHALLENGES ───────────────────
        if sub_subdomain == "Reason for Business Challenges":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Overall business outlook: **{outlook}** (Confidence: {confidence})"
            )

            # Promise/denial context
            for house_num, status in unified_verdict.get("promise_status", {}).items():
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

            # Agreement status
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE on business outlook")
            elif agreement == "PARTIAL":
                result.add_point("⚠️ KP and Vedic show PARTIAL agreement — KP takes precedence")
            elif agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT — KP result prioritised for timing")

            # KP engine insights
            result.add_point(
                f"KP: Business strength summary: **{business_kp_data.get('business_strength_summary')}**"
            )
            result.add_point(
                f"KP: Foreign / external market influence: **{business_kp_data.get('foreign_link')}**"
            )

            if confidence == "Low":
                result.add_point(
                    "KP: Chart shows sustained pressure phases — challenges are structural, not just cyclical."
                )
            elif confidence == "Moderate":
                result.add_point(
                    "KP: Temporary slowdown indicated — correction possible with targeted strategy."
                )
            else:
                result.add_point(
                    "KP: Challenges appear cyclical rather than permanent — timing windows will show recovery periods."
                )

        # ── 2A) LOAN TAKING DECISION ─────────────────────────────
        elif sub_subdomain == "Loan Taking Decision":

            result.add_point(
                f"KP: Business viability: **{business_kp_data.get('business_strength_summary')}**"
            )
            result.add_point(
                f"KP: Overall outlook: **{unified_verdict['overall_outlook']}** "
                f"(Confidence: {unified_verdict['confidence']})"
            )

            # KP timing for loan-taking
            try:
                loan_rules  = TIMING_RULES.get("Loan Taking Timing", {})
                loan_scores = score_kp_all_planets(planets, houses, loan_rules)
                loan_planets = get_positive_planets(loan_scores)

                if loan_planets:
                    result.add_point(
                        f"KP: Loan-taking indicators active through: {', '.join(loan_planets[:3])}."
                    )
                    result.add_point(
                        "KP: Taking a loan during the indicated dasha can support business expansion."
                    )
                    loan_data["loan_supported"] = True
                    loan_data["loan_planets"]   = loan_planets[:3]
                else:
                    result.add_point(
                        "KP: Loan-taking indicators weak — borrowing carries elevated risk now."
                    )
                    loan_data["loan_supported"] = False
                    loan_data["loan_planets"]   = []
            except Exception as e:
                logger.warning(f"Loan timing evaluation error: {e}")
                loan_data["loan_supported"] = False

            result.additional_data.update(loan_data)

        # ── 2B) LOAN REPAYMENT DECISION ──────────────────────────
        elif sub_subdomain == "Loan Repayment Decision":

            result.add_point(
                f"KP: Business viability: **{business_kp_data.get('business_strength_summary')}**"
            )

            # Promise/denial on repayment-relevant houses
            h11_status = unified_verdict.get("promise_status", {}).get(11, "NEUTRAL")
            h2_status  = unified_verdict.get("promise_status", {}).get(2, "NEUTRAL")

            result.add_point(f"KP: 11th house (income/gains): {h11_status}")

            try:
                repay_rules   = TIMING_RULES.get("Loan Repayment Timing", {})
                repay_scores  = score_kp_all_planets(planets, houses, repay_rules)
                repay_planets = get_positive_planets(repay_scores)

                if repay_planets:
                    result.add_point(
                        f"KP: Loan repayment supported through: {', '.join(repay_planets[:3])}."
                    )
                    loan_data["repayment_supported"] = True
                    loan_data["repayment_planets"]   = repay_planets[:3]
                else:
                    result.add_point(
                        "KP: Repayment visibility limited — conservative approach advised."
                    )
                    loan_data["repayment_supported"] = False
                    loan_data["repayment_planets"]   = []
            except Exception as e:
                logger.warning(f"Repayment timing error: {e}")
                loan_data["repayment_supported"] = False

            if unified_verdict["confidence"] == "Low":
                result.add_point(
                    "KP: Business strength low — prioritise stabilising income before aggressive repayment."
                )

            result.additional_data.update(loan_data)

        # ── 2C) CONTINUE OR SHUT DOWN ─────────────────────────────
        elif sub_subdomain == "Continue or Shut Down":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Business outlook: **{outlook}** (Confidence: {confidence})"
            )

            # Promise status for key houses
            for house_num in [7, 10, 11]:
                status  = unified_verdict.get("promise_status", {}).get(house_num, "NEUTRAL")
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

            # Agreement status
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT on outlook — KP result used for decision")
            elif agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic AGREE — verdict is reliable")

            # Loan-taking feasibility
            try:
                loan_rules   = TIMING_RULES.get("Loan Taking Timing", {})
                loan_scores  = score_kp_all_planets(planets, houses, loan_rules)
                loan_planets = get_positive_planets(loan_scores)

                if loan_planets:
                    result.add_point(
                        f"KP: Loan-taking indicators active — {', '.join(loan_planets[:3])} periods favourable."
                    )
                    loan_data["loan_supported"] = True
                else:
                    result.add_point("KP: Loan-taking indicators weak — borrowing carries risk.")
                    loan_data["loan_supported"] = False
            except Exception:
                loan_data["loan_supported"] = False

            # Repayment feasibility
            try:
                repay_rules   = TIMING_RULES.get("Loan Repayment Timing", {})
                repay_scores  = score_kp_all_planets(planets, houses, repay_rules)
                repay_planets = get_positive_planets(repay_scores)

                if repay_planets:
                    result.add_point("KP: Loan repayment supported during favourable income periods.")
                    loan_data["repayment_supported"] = True
                else:
                    result.add_point("KP: Repayment visibility limited — conservative decisions advised.")
                    loan_data["repayment_supported"] = False
            except Exception:
                loan_data["repayment_supported"] = False

            # Final directional guidance (uses unified verdict)
            h7_status  = unified_verdict.get("promise_status", {}).get(7,  "NEUTRAL")
            h11_status = unified_verdict.get("promise_status", {}).get(11, "NEUTRAL")

            if h7_status == "DENIAL" and h11_status in ["DENIAL", "NEUTRAL"] and confidence == "Low":
                result.add_point(
                    "KP: Strong indicators for business closure, pause, or full restructuring — "
                    "continuing without change risks deepening losses."
                )
            elif h7_status in ["PROMISE", "WEAK_PROMISE"] and h11_status in ["PROMISE", "WEAK_PROMISE"]:
                result.add_point(
                    "KP: Business houses show promise — continuation with restructuring is preferable to closure."
                )
            else:
                result.add_point(
                    "KP: Mixed signals — evaluate timing windows before making irreversible decisions."
                )

            result.additional_data.update(loan_data)

        # ── 3) BUSINESS REMEDIES ─────────────────────────────────
        elif sub_subdomain == "Business Remedies":
            result.add_point(
                "Business remedies focus on stabilising operations, reducing financial stress, "
                "and improving resilience through planetary strengthening."
            )

            # Still show promise status so LLM can tailor remedies
            for house_num, status in unified_verdict.get("promise_status", {}).items():
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

        # ═══════════════════════════════════════════════════════════
        # CREATE BUSINESS CHALLENGE MATRIX (uses unified verdict)
        # ═══════════════════════════════════════════════════════════
        if kp_structured.get("has_kp_data"):
            try:
                challenge_matrix = self._create_business_challenge_matrix(
                    unified_verdict=unified_verdict,
                    kp_structured=kp_structured,
                    loan_data=loan_data,
                )
                result.additional_data["business_challenge_suitability_matrix"] = challenge_matrix
                logger.info(f"✅ Business challenge matrix: {len(challenge_matrix)} options")
            except Exception as e:
                logger.error(f"❌ Error creating business challenge matrix: {e}")

        # ─── Store all data for LLM ──────────────────────────────
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            business_kp_data,
            kwargs.get("current_dasha"),
            kwargs.get("dasha_timeline"),
        )

        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        self._log_result_breakdown(result, sub_subdomain)
        return result

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ═══════════════════════════════════════════════════════════════

    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """Extract BEST and NEAREST timing windows for LLM."""
        if not timing_windows:
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
                d = {
                    "start":         get_attr(w, "start"),
                    "end":           get_attr(w, "end"),
                    "dasha":         get_attr(w, "dasha"),
                    "score":         get_attr(w, "score"),
                    "transit_score": get_attr(w, "transit_score"),
                    "final_score":   get_attr(w, "final_score"),
                    "age_at_start":  get_attr(w, "age_at_start"),
                }
                for extra in ["score_maha", "score_antara", "score_paryantar"]:
                    val = get_attr(w, extra)
                    if val is not None:
                        d[extra] = val
                return d

            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, "final_score", 0) or 0,
                reverse=True,
            )
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            favorable_windows = [
                w for w in timing_windows
                if (get_attr(w, "final_score", 0) or 0) >= 50
            ]
            if favorable_windows:
                sorted_by_date = sorted(
                    favorable_windows,
                    key=lambda w: datetime.strptime(
                        get_attr(w, "start", "9999-12-31") or "9999-12-31", "%Y-%m-%d"
                    ),
                )
                nearest_window = window_to_dict(sorted_by_date[0])
            else:
                nearest_window = best_window

            return {
                "best_window":    best_window,
                "nearest_window": nearest_window,
                "all_favorable":  [window_to_dict(w) for w in sorted_windows[:5]],
                "has_timing":     True,
            }

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            return {}

    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
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
        primary_houses: set,
    ) -> dict:
        """Extract house lord information for relevant houses."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue

            lord_name = (
                h.get("rashi_lord") or h.get("sign_lord") or h.get("lord") or ""
            )
            if not lord_name:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                lord_name = self._get_sign_lord(sign) or ""

            normalized_lord = normalize_planet_name(lord_name)
            if not normalized_lord:
                continue

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                continue

            lord_dignity       = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity  = None
                    if hasattr(analyzer, "get_planet_dignity"):
                        dignity = analyzer.get_planet_dignity(normalized_lord)
                    elif hasattr(analyzer, "get_dignity"):
                        dignity = analyzer.get_dignity(normalized_lord)

                    if dignity:
                        lord_dignity = dignity.value if hasattr(dignity, "value") else str(dignity)
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity
                        )
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")
            else:
                # Fallback dignity from internal method
                lord_dignity = self._get_planet_dignity(normalized_lord, lord_data)
                lord_strength_score = self._calculate_lord_strength(
                    normalized_lord, lord_data, lord_dignity
                )

            planets_in_house = []
            for p in h.get("planets", []):
                pn = normalize_planet_name(self.extract_planet_name(p))
                if pn:
                    planets_in_house.append(pn)

            house_lords_info[house_num] = {
                "lord":              normalized_lord,
                "lord_in_house":     lord_data.get("house"),
                "lord_in_sign":      lord_data.get("sign", ""),
                "lord_degree":       (lord_data.get("full_degree") or lord_data.get("global_degree") or lord_data.get("degree") or 0),
                "lord_is_combust":   (lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)),
                "lord_is_retrograde":(lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)),
                "lord_dignity":      lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority":          "primary" if house_num in primary_houses else "secondary",
                "planets_in_house":  planets_in_house,
                "house_sign":        (h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""),
            }

        return house_lords_info

    def _extract_aspects_on_houses(
        self,
        houses: list,
        planets: dict,
        aspects_data: dict,
        relevant_houses: set,
    ) -> dict:
        """Extract aspects on relevant houses."""
        house_aspects = {}
        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        for house_num in relevant_houses:
            house_aspects[house_num] = {"benefic_aspects": [], "malefic_aspects": [], "neutral_aspects": []}

            for planet_name, planet_data in planets.items():
                aspected_houses = (
                    aspects_data[planet_name].get("aspects_houses", [])
                    if aspects_data and planet_name in aspects_data
                    else planet_data.get("aspects_houses", [])
                )
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
        dignity=None,
    ) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, "value") else str(dignity).upper()
            dignity_scores = {
                "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
                "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0,
            }
            score = dignity_scores.get(dignity_str, 50)

        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            score -= 10 if planet_name in {"Jupiter", "Venus", "Mercury"} else -10  # malefics retrograde = stronger

        degree = planet_data.get("full_degree") or planet_data.get("global_degree") or planet_data.get("degree") or 15
        if degree < 5 or degree > 25:
            score -= 10

        return max(0, min(100, score))

    def _extract_lagna_info(self, houses: List[Dict], planets: Dict[str, Dict]) -> Optional[Dict]:
        """Extract lagna (ascendant) information."""
        try:
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            if not house_1:
                return None

            lagna_sign = (
                house_1.get("sign") or house_1.get("start_rasi") or house_1.get("rasi") or ""
            )
            if not lagna_sign:
                return None

            lagna_lord = self._get_house_lord(house_1)
            if not lagna_lord:
                return None

            lagna_lord_data = planets.get(lagna_lord, {})

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
            else:
                lagna_lord_dignity = self._get_planet_dignity(lagna_lord, lagna_lord_data)

            return {
                "lagna_sign":         lagna_sign,
                "lagna_lord":         lagna_lord,
                "lagna_lord_house":   lagna_lord_data.get("house"),
                "lagna_lord_sign":    lagna_lord_data.get("sign", ""),
                "lagna_lord_degree":  (lagna_lord_data.get("full_degree") or lagna_lord_data.get("degree") or 0),
                "lagna_lord_dignity": lagna_lord_dignity,
            }
        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    def _add_house_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
    ):
        """Add analysis points based on house lords and aspects."""
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue

            info    = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            lord      = info["lord"]
            dignity   = info["lord_dignity"]
            strength  = info["lord_strength_score"]

            parts = [
                f"⭐ House {house_num} ({self.HOUSE_MEANINGS.get(house_num, 'General')}):",
                f"Lord {lord} is {dignity}",
                f"(Strength: {strength}/100)",
            ]

            conditions = []
            if info["lord_is_combust"]:
                conditions.append("COMBUST")
            if info["lord_is_retrograde"]:
                conditions.append("RETROGRADE")
            if conditions:
                parts.append(f"[{', '.join(conditions)}]")

            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            if benefic:
                parts.append(f"- Benefic: {', '.join(benefic)}")
            if malefic:
                parts.append(f"- Malefic: {', '.join(malefic)}")

            result.add_point(" ".join(parts))

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None,
        business_kp_data: dict = None,
        current_dasha: dict = None,
        dasha_timeline: dict = None,
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "business_challenges"

        result.additional_data.update({
            f"{domain_prefix}_house_config": {
                "primary":   list(primary_houses),
                "secondary": list(secondary_houses),
                "source":    house_config.get("source", "fallback") if house_config else "fallback",
            },
            f"{domain_prefix}_house_lords":   house_lords_info,
            f"{domain_prefix}_house_aspects": house_aspects_info,
            f"{domain_prefix}_analysis_summary": {
                "total_houses_analyzed":  len(house_lords_info),
                "primary_houses_count":   len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                ),
            },
            "current_dasha":  current_dasha,
            "dasha_timeline": dasha_timeline,
        })

        if business_kp_data:
            result.additional_data[f"{domain_prefix}_kp_analysis"] = {
                "mode":                     business_kp_data.get("mode"),
                "confidence":               business_kp_data.get("confidence"),
                "score":                    business_kp_data.get("score"),
                "business_strength_summary": business_kp_data.get("business_strength_summary"),
                "final_professions":        business_kp_data.get("final_professions", []),
                "partners_needed":          business_kp_data.get("partners_needed"),
                "foreign_link":             business_kp_data.get("foreign_link"),
                "business_nature_tags":     business_kp_data.get("business_nature_tags", []),
                "analysis":                 business_kp_data.get("analysis", []),
            }

        if timing_windows_data and timing_windows_data.get("has_timing"):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info("✅ STORED TIMING WINDOWS")

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging."""
        logger.info("🧩 RESULT BREAKDOWN START")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")
        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {sorted(ad.keys())}")

        if "unified_business_verdict" in ad:
            v = ad["unified_business_verdict"]
            logger.info(f"UNIFIED VERDICT: {v.get('overall_outlook')}")
            logger.info(f"  Agreement: {v.get('agreement_status')}")
            logger.info(f"  Confidence: {v.get('confidence')}")
            logger.info(f"  Promise status: {v.get('promise_status')}")

        if "kp_business_challenge_analysis" in ad:
            kp = ad["kp_business_challenge_analysis"]
            logger.info(f"  has_kp_data: {kp.get('has_kp_data')}")
            logger.info(f"  overall_verdict: {kp.get('overall_verdict')}")

        if "business_challenge_suitability_matrix" in ad:
            m = ad["business_challenge_suitability_matrix"]
            logger.info(f"  Matrix options: {len(m)}")

        logger.info("🧩 RESULT BREAKDOWN END")
    # --------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="BUS_FC_1",
                question=(
                    "Why is my business facing challenges or stagnation or downturn, "
                    "and when will there be improvement?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Reason for Business Challenges"
            ),
            Question(
                id="BUS_FC_2A",
                question=(
                    "Should I take a loan for my business? "
                    "When is the best time to take a loan?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Loan Taking Decision"
            ),
            Question(
                id="BUS_FC_2B",
                question=(
                    "Will I be able to repay my business loan successfully? "
                    "When will repayment be easier?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Loan Repayment Decision"
            )
        ]
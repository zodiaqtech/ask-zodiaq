"""
Growing Existing Business Evaluator - ENHANCED VERSION v5.0

CRITICAL UPGRADES FROM v4.0 (Aligned with FacingChallengesInBusinessEvaluator v5.0
and CareerDiscoveryAndEmploymentEvaluator v5.0):

✅ UNIFIED BUSINESS GROWTH VERDICT - Single source of truth (_compute_unified_growth_verdict)
✅ PURE KP METHODOLOGY - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ SUB-LORD PROMISE/DENIAL LOGIC - Core KP rule (was MISSING in v4.0)
✅ INTERNAL _get_planet_significations() - No external import dependency
✅ RAHU/KETU PROPER HANDLING - Star lord + sign lord + conjunctions
✅ HONEST VEDIC-KP AGREEMENT - AGREEMENT/PARTIAL/CONFLICT
✅ CONSISTENT OUTPUT ACROSS ALL QUESTIONS - Unified verdict used everywhere
✅ STRENGTH HIERARCHY - Sub (4) > Star (3) > Occupy (2) > Own (1)
✅ COMPLETE get_questions() - All 5 sub-subdomains including Best Periods (TIMING)
✅ _build_kp_interpretation() - Human-readable chain explanation
✅ _calculate_lord_strength() - Proper strength scoring
✅ CORRECT HOUSE MAPPING - Growth: 3,9,11 | Business: 2,3,7,11 | Obstacle: 6,8,12

Architecture:
- _compute_unified_growth_verdict()      → Single source of truth
- _apply_pure_kp_chain()                 → CSL → Sub Lord → Star Lord → Significations
- _evaluate_sub_lord_promise()           → Promise/denial logic per cusp
- _get_planet_significations()           → Internal recursive (safe vs Rahu/Ketu loops)
- _build_kp_interpretation()             → Human-readable explanation
- _extract_kp_growth_structured()        → Sub-lord level KP data for LLM
- _create_business_growth_matrix()       → Uses unified_verdict for consistency
- All questions use unified_growth_verdict from additional_data

Covers:
1) Identifying Suitable Business / Growth Strategy → sub_subdomain="Identifying Suitable Business"
2) Loan Taking Decision + Timing                   → sub_subdomain="Loan Taking Decision"
3) Loan Repayment Decision + Timing                → sub_subdomain="Loan Repayment Decision"
4) Best Periods for Business Growth (TIMING)       → sub_subdomain="Best Periods for Business Growth"
5) Business Challenges                             → sub_subdomain="Business Challenges"

Key Houses for Business Growth:
- 7th:  Business/Partnerships (PRIMARY)
- 10th: Career/Profession (PRIMARY)
- 11th: Gains/Income (PRIMARY)
- 3rd:  Courage/Initiatives/Expansion
- 9th:  Fortune/Luck/Foreign Expansion
- 6th:  Obstacles/Competition/Loans
- 8th:  Sudden Events/Transformations
- 12th: Foreign/Expenses
- 2nd:  Wealth/Capital
- 5th:  Speculation/Creativity
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
    logging.warning("House lords analyzer not available — using internal analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GrowingExistingBusinessEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Business → Growing Existing Business
    v5.0 — Unified growth verdict, pure KP chain, promise/denial logic.
    """

    domain = "Business"
    subtopic = "Growing Existing Business"

    # ═══════════════════════════════════════════════════════════════
    # HOUSE DEFINITIONS (KP Standard for Business Growth)
    # ═══════════════════════════════════════════════════════════════

    BUSINESS_PROMISE_HOUSES = {2, 3, 7, 11}    # Core business promise
    SUCCESS_HOUSES          = {2, 10, 11}       # Wealth, career, gains
    GROWTH_HOUSES           = {3, 9, 11}        # Initiatives, fortune, gains
    EXPANSION_HOUSES        = {3, 9, 12}        # Courage, luck, foreign
    OBSTACLE_HOUSES         = {6, 8, 12}        # Competition, sudden, expenses
    WEALTH_HOUSES           = {2, 5, 11}        # Capital, speculation, income
    LOSS_HOUSES             = {6, 8, 12}        # Debts, sudden loss, expenses

    HOUSE_MEANINGS = {
        1:  "Self/Personality/Lagna",
        2:  "Wealth/Capital/Assets",
        3:  "Courage/Initiatives/Efforts",
        5:  "Intelligence/Creativity/Speculation",
        6:  "Debts/Loans/Competition",
        7:  "Business/Partnerships/Trade",
        8:  "Sudden Events/Transformation",
        9:  "Fortune/Luck/Foreign Expansion",
        10: "Career/Profession/Public Standing",
        11: "Gains/Income/Fulfillment",
        12: "Expenses/Losses/Foreign Connections",
    }

    # KP Strength Hierarchy
    KP_WEIGHT = {
        "sub_lord": 4,
        "star_lord": 3,
        "occupy":    2,
        "own":       1,
    }

    # ═══════════════════════════════════════════════════════════════
    # UNIFIED GROWTH VERDICT (Single Source of Truth)
    # ═══════════════════════════════════════════════════════════════

    def _compute_unified_growth_verdict(
        self,
        planets: Dict,
        houses: List,
    ) -> Dict:
        """
        SINGLE SOURCE OF TRUTH for business growth potential.
        All questions must use this verdict for consistency.

        Analyzes key cusps: 7th (business), 10th (profession), 11th (gains),
        3rd (initiatives), 9th (fortune) using pure KP sub-lord promise/denial.

        Returns:
        {
            "overall_outlook":  "STRONG_GROWTH" | "MODERATE_GROWTH" | "GROWTH_CHALLENGES"
                                | "EXPANSION_FAVORABLE" | "MIXED_SIGNALS",
            "growth_viable":    True | False | None,
            "confidence":       "High" | "Moderate" | "Low",
            "kp_reasoning":     str,
            "vedic_reasoning":  str,
            "agreement_status": "AGREEMENT" | "PARTIAL" | "CONFLICT",
            "promise_status":   {7: "PROMISE"|"DENIAL"|"WEAK_PROMISE"|"NEUTRAL", ...},
            "detailed_analysis": {house_num: chain_result, ...},
            "growth_ranking":   [list of ranked growth options],
        }
        """
        result = {
            "overall_outlook":   "UNKNOWN",
            "growth_viable":     None,
            "confidence":        "Low",
            "kp_reasoning":      "",
            "vedic_reasoning":   "",
            "agreement_status":  "UNKNOWN",
            "promise_status":    {},
            "detailed_analysis": {},
            "growth_ranking":    [],
        }

        # ─── STEP 1: Pure KP Analysis (Primary) ────────────────────
        key_cusps = {
            7:  "Business/Partnership",
            10: "Career/Profession",
            11: "Gains/Income",
            3:  "Initiatives/Courage",
            9:  "Fortune/Foreign Expansion",
            6:  "Obstacles/Competition",
            8:  "Sudden Events",
            12: "Foreign/Expenses/Losses",   # ← ADD THIS
        }

        kp_reasons   = []
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
                        f"7th CSL promises business growth "
                        f"(sub-lord signifies {sorted(sub_lord_houses & self.BUSINESS_PROMISE_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append(
                        f"7th CSL denies business axis "
                        f"(sub-lord signifies loss houses {sorted(sub_lord_houses & self.OBSTACLE_HOUSES)})"
                    )

            elif cusp_num == 11:
                if chain_result.get("promise_status") == "PROMISE":
                    kp_reasons.append(
                        f"11th CSL promises gains/income growth "
                        f"(sub-lord signifies {sorted(sub_lord_houses & self.SUCCESS_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append("11th CSL denies gains — growth will not convert to income")

            elif cusp_num == 3:
                if chain_result.get("promise_status") in ["PROMISE", "INITIATIVE_POSITIVE"]:
                    kp_reasons.append("3rd CSL supports initiatives and expansion efforts")

            elif cusp_num == 9:
                if chain_result.get("promise_status") in ["PROMISE", "FORTUNE_POSITIVE"]:
                    kp_reasons.append("9th CSL supports fortune, luck, and foreign expansion")

        result["promise_status"] = promise_status

        # ─── STEP 2: Derive Overall Outlook from Promise Status ─────
        h7  = promise_status.get(7,  "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")
        h11 = promise_status.get(11, "NEUTRAL")
        h3  = promise_status.get(3,  "NEUTRAL")
        h9  = promise_status.get(9,  "NEUTRAL")
        h6  = promise_status.get(6,  "NEUTRAL")
        h8  = promise_status.get(8,  "NEUTRAL")

        if h7 == "PROMISE" and h11 in ["PROMISE", "WEAK_PROMISE"]:
            overall = "STRONG_GROWTH"
            viable = True
        elif h7 == "DENIAL" and h11 in ["DENIAL", "NEUTRAL"]:
            overall = "GROWTH_CHALLENGES"
            viable = False
        elif (
                h7 != "DENIAL"
                and h3 in ["PROMISE", "INITIATIVE_POSITIVE"]
                and h9 in ["PROMISE", "FORTUNE_POSITIVE"]
            ):
            overall = "EXPANSION_FAVORABLE"
            viable = True
        elif h7 == "WEAK_PROMISE" and h11 in ["WEAK_PROMISE", "NEUTRAL"]:
            overall = "MODERATE_GROWTH"
            viable = True
        elif h6 in ["CHALLENGING"] or h8 in ["RISKY"]:
            overall = "OBSTACLES_BEFORE_GROWTH"
            viable = None
        else:
            overall = "MIXED_SIGNALS"
            viable = None

        result["overall_outlook"] = overall
        result["growth_viable"]   = viable

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
        vedic_reasons  = []

        for house_num in [7, 10, 11]:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            lord_name = self._get_house_lord(house_data)
            if not lord_name:
                continue

            lord_data = planets.get(lord_name, {})
            lord_house = lord_data.get("house")
            dignity    = self._get_planet_dignity(lord_name, lord_data)

            if house_num == 7:
                if lord_house in self.BUSINESS_PROMISE_HOUSES:
                    vedic_positive += 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business growth supported"
                    )
                elif lord_house in self.OBSTACLE_HOUSES:
                    vedic_negative += 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → growth obstructed"
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
                        f"10th lord {lord_name} is {dignity} → strong professional base for growth"
                    )
                elif dignity == "DEBILITATED":
                    vedic_negative += 1
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → professional base weak"
                    )

        result["vedic_reasoning"] = "; ".join(vedic_reasons) if vedic_reasons else "Vedic analysis inconclusive."

        # ─── STEP 5: KP-Vedic Agreement ───────────────────────────
        kp_positive_flag    = overall in ["STRONG_GROWTH", "MODERATE_GROWTH", "EXPANSION_FAVORABLE"]
        vedic_positive_flag = vedic_positive > vedic_negative

        if overall == "MIXED_SIGNALS":
            result["agreement_status"] = "PARTIAL"
        elif kp_positive_flag and vedic_positive_flag:
            result["agreement_status"] = "AGREEMENT"
        elif not kp_positive_flag and not vedic_positive_flag:
            result["agreement_status"] = "AGREEMENT"
        else:
            result["agreement_status"] = "PARTIAL"

        result["kp_reasoning"] = " | ".join(kp_reasons) if kp_reasons else "KP analysis inconclusive."

        # ─── STEP 6: Growth Ranking ────────────────────────────────
        growth_options = [
            ("Organic Growth (Current Model)",     _growth_score(h7, h11, 3, 2)),
            ("Diversification / New Products",      _growth_score(h3, h9, 2, 2)),
            ("Partnership Expansion",               _growth_score(h7, h10, 2, 1)),
            ("Loan-Funded Expansion",               _growth_score(h11, h3, 2, 1)),
            ("Foreign / Export Expansion",          _growth_score(h9, promise_status.get(12, "NEUTRAL"), 2, 1)),
            ("Digital / Online Expansion",          _growth_score(h3, h11, 1, 2)),
            ("Franchise / Licensing",               _growth_score(h7, h11, 1, 2)),
            ("Acquisition / Merger",                _growth_score(promise_status.get(8, "NEUTRAL"), h7, 2, 1)),
        ]
        result["growth_ranking"] = sorted(
            [opt[0] for opt in growth_options],
            key=lambda name: next((s for n, s in growth_options if n == name), 0),
            reverse=True,
        )

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
        Full KP chain: CSL → Sub Lord → Star Lord → Significations → Promise/Denial.

        Sub-lord signifies positive houses → PROMISE
        Sub-lord signifies 8, 12 strongly  → DENIAL
        """
        result = {
            "csl":               None,
            "csl_house":         None,
            "csl_nakshatra":     None,
            "star_lord":         None,
            "star_lord_signifies": [],
            "sub_lord":          None,
            "sub_lord_signifies": [],
            "promise_status":    "UNKNOWN",
            "chain_text":        "",
            "interpretation":    "",
        }

        csl_raw = cusp_data.get("cusp_sub_lord", "")
        csl = normalize_planet_name(csl_raw)
        if not csl:
            return result

        result["csl"]     = csl
        csl_data          = planets.get(csl, {})
        result["csl_house"]    = csl_data.get("house")
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
        KP Promise/Denial Logic based on sub-lord significations (GROWTH context).

        For 7th cusp (business):    PROMISE if sub-lord signifies 2, 3, 7, 11
        For 10th cusp (profession): PROMISE if sub-lord signifies 2, 6, 10, 11
        For 11th cusp (gains):      PROMISE if sub-lord signifies 2, 10, 11
        For 3rd cusp (initiatives): PROMISE if sub-lord signifies 3, 9, 11
        For 9th cusp (fortune):     PROMISE if sub-lord signifies 2, 9, 11
        For 6th cusp (obstacles):   MANAGEABLE / CHALLENGING
        For 8th cusp (sudden):      TRANSFORMATIVE / RISKY
        """
        sub_set    = set(sub_lord_houses)
        loss_houses = {8, 12}

        if cusp_house == 7:
            positive = {2, 3, 7, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 10:
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 11:
            positive = {2, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "PROMISE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 3:
            positive = {3, 9, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "INITIATIVE_POSITIVE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "INITIATIVE_BLOCKED"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 9:
            positive = {2, 9, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "FORTUNE_POSITIVE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 6:
            positive = {2, 10, 11}
            if sub_set & positive:
                return "MANAGEABLE"
            elif sub_set & {6, 8, 12} and not sub_set & positive:
                return "CHALLENGING"
            return "MODERATE"

        elif cusp_house == 8:
            positive = {2, 10, 11}
            if sub_set & positive and not sub_set & loss_houses:
                return "TRANSFORMATIVE"
            elif sub_set & loss_houses and not sub_set & positive:
                return "RISKY"
            return "UNPREDICTABLE"

        return "NEUTRAL"

    # ═══════════════════════════════════════════════════════════════
    # PLANET SIGNIFICATIONS (Internal — safe vs Rahu/Ketu loops)
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
        Internal — safe against Rahu/Ketu recursive loops.

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
        signified   = set()
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

        # 3. Planets in star of this planet
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
            "Sun": "Aries",    "Moon": "Taurus",     "Mars": "Capricorn",
            "Mercury": "Virgo", "Jupiter": "Cancer",  "Venus": "Pisces",
            "Saturn": "Libra",
        }
        debilitation = {
            "Sun": "Libra",    "Moon": "Scorpio",    "Mars": "Cancer",
            "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
            "Saturn": "Aries",
        }
        own_signs = {
            "Sun":     ["Leo"],
            "Moon":    ["Cancer"],
            "Mars":    ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus":   ["Taurus", "Libra"],
            "Saturn":  ["Capricorn", "Aquarius"],
        }
        if exaltation.get(planet_name) == sign:
            return "EXALTED"
        if debilitation.get(planet_name) == sign:
            return "DEBILITATED"
        if sign in own_signs.get(planet_name, []):
            return "OWN_SIGN"
        return "NEUTRAL"

    def _calculate_lord_strength(
        self, planet_name: str, planet_data: Dict, dignity
    ) -> int:
        """Calculate lord strength score (0–100)."""
        dignity_str = dignity.value if hasattr(dignity, "value") else str(dignity)
        dignity_scores = {
            "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
            "FRIENDLY": 60, "NEUTRAL": 40,
            "ENEMY": 20, "DEBILITATED": 0,
        }
        score = dignity_scores.get(dignity_str.upper(), 50)
        if planet_data.get("is_combusted") or planet_data.get("is_combust"):
            score -= 30
        return max(0, min(100, score))

    def _score_to_rating(self, score: int) -> str:
        if score >= 4:
            return "HIGH"
        elif score >= 2:
            return "MODERATE"
        elif score >= 1:
            return "LOW"
        return "VERY_LOW"

    # ═══════════════════════════════════════════════════════════════
    # KP STRUCTURED ANALYSIS (Sub-Lord Level)
    # ═══════════════════════════════════════════════════════════════

    def _extract_kp_growth_structured(
        self,
        planets: Dict,
        houses: List,
        unified_verdict: Dict,
    ) -> Dict:
        """
        Extract structured KP business growth data using PURE sub-lord methodology.
        Uses unified_verdict for consistency across all questions.

        Chain: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
        """
        kp_data = {
            "csl_details":    {},
            "overall_verdict": unified_verdict.get("overall_outlook", "UNKNOWN"),
            "key_findings":   [],
            "has_kp_data":    False,
            "methodology":    "CSL → Sub Lord → Star Lord → Significations → Promise/Denial",
            "agreement_status": unified_verdict.get("agreement_status", "UNKNOWN"),
        }

        growth_houses = [2, 3, 5, 6, 7, 8, 9, 10, 11, 12]

        for house_num in growth_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            chain_result = self._apply_pure_kp_chain(house_data, planets, houses)
            if not chain_result.get("csl"):
                continue

            kp_data["has_kp_data"] = True
            csl     = chain_result["csl"]

            promise = chain_result.get("promise_status", "NEUTRAL")

            verdict_map = {
                "PROMISE":            "STRONG",
                "WEAK_PROMISE":       "MODERATE",
                "DENIAL":             "WEAK",
                "NEUTRAL":            "NEUTRAL",
                "MANAGEABLE":         "MANAGEABLE",
                "CHALLENGING":        "CHALLENGING",
                "TRANSFORMATIVE":     "TRANSFORMATIVE",
                "RISKY":              "RISKY",
                "UNPREDICTABLE":      "UNPREDICTABLE",
                "INITIATIVE_POSITIVE":"SUPPORTIVE",
                "INITIATIVE_BLOCKED": "BLOCKED",
                "FORTUNE_POSITIVE":   "PROMISING",
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
                "growth_connection":   len(sub_houses & self.GROWTH_HOUSES),
                "obstacle_connection": len(sub_houses & self.OBSTACLE_HOUSES),
                "wealth_connection":   len(sub_houses & self.WEALTH_HOUSES),
                "loss_connection":     len(sub_houses & self.LOSS_HOUSES),
                "expansion_connection": len(sub_houses & self.EXPANSION_HOUSES),
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
        """Build human-readable KP interpretation per house (growth context)."""
        csl       = chain_result.get("csl", "Unknown")
        sub_lord  = chain_result.get("sub_lord", "Unknown")
        sub_houses = chain_result.get("sub_lord_signifies", [])
        promise   = chain_result.get("promise_status", "NEUTRAL")
        outlook   = unified_verdict.get("overall_outlook", "Unknown")

        if house_num == 7:
            if promise == "PROMISE":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Business axis PROMISED → Growth and partnerships supported. "
                    f"Overall growth outlook: {outlook}."
                )
            elif promise == "DENIAL":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Business growth faces core structural obstacles. "
                    f"Focus on stabilising before expanding."
                )
            else:
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Mixed business indicators → Moderate growth possible with effort."
                )

        elif house_num == 10:
            if promise == "PROMISE":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Career houses activated → Professional standing supports business growth."
                )
            elif promise == "DENIAL":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Professional reputation under pressure → Growth requires rebuilding credibility first."
                )
            else:
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate professional indicators → Steady, incremental growth possible."
                )

        elif house_num == 11:
            if promise == "PROMISE":
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Gains house PROMISED → Growth will convert to income and profits."
                )
            elif promise == "DENIAL":
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Gains denied → Revenue growth unlikely to convert to profits. "
                    f"Focus on cost efficiency and margin improvement."
                )
            else:
                return (
                    f"11th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate gains potential → Growth will be gradual and requires patience."
                )

        elif house_num == 3:
            return (
                f"3rd CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Initiative house: {promise}. "
                f"{'Bold expansion moves supported.' if promise in ['INITIATIVE_POSITIVE', 'PROMISE', 'WEAK_PROMISE'] else 'Cautious, incremental approach recommended.'}"
            )

        elif house_num == 9:
            return (
                f"9th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Fortune/foreign expansion: {promise}. "
                f"{'International and long-distance growth favoured.' if promise in ['FORTUNE_POSITIVE', 'PROMISE', 'WEAK_PROMISE'] else 'Focus on established domestic markets.'}"
            )

        elif house_num == 6:
            return (
                f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Competition/debt house: {promise}. "
                f"{'Competition manageable during growth.' if promise == 'MANAGEABLE' else 'Heavy competition or debt burden may slow growth.'}"
            )

        elif house_num == 8:
            return (
                f"8th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                f"Transformation house: {promise}. "
                f"{'Sudden opportunities can accelerate growth.' if promise == 'TRANSFORMATIVE' else 'Risk of sudden setbacks during expansion; proceed carefully.'}"
            )

        else:
            return (
                f"House {house_num}: CSL {csl} → Sub Lord {sub_lord} → "
                f"Signifies {sub_houses} → {promise}"
            )

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS GROWTH SUITABILITY MATRIX (Uses Unified Verdict)
    # ═══════════════════════════════════════════════════════════════

    def _create_business_growth_matrix(
        self,
        unified_verdict: Dict,
        kp_structured: Dict,
        business_kp_data: Dict = None,
        loan_data: Dict = None,
    ) -> Dict[str, Dict]:
        """
        Create business growth suitability matrix using UNIFIED verdict for consistency.
        All ratings derived from the single source of truth.
        """
        matrix   = {}
        loan_data = loan_data or {}
        business_kp_data = business_kp_data or {}

        csl_details    = kp_structured.get("csl_details", {})
        promise_status = unified_verdict.get("promise_status", {})
        overall_outlook = unified_verdict.get("overall_outlook", "UNKNOWN")
        confidence     = unified_verdict.get("confidence", "Low")

        h7  = promise_status.get(7,  "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")
        h11 = promise_status.get(11, "NEUTRAL")
        h3  = promise_status.get(3,  "NEUTRAL")
        h9  = promise_status.get(9,  "NEUTRAL")
        h6  = promise_status.get(6,  "NEUTRAL")
        h8  = promise_status.get(8,  "NEUTRAL")

        h7_csl = csl_details.get(7, {}).get("csl")

        stable_planets   = {"Saturn", "Jupiter", "Sun"}
        rahu_connected   = any(
            d.get("csl") == "Rahu" or d.get("star_lord") == "Rahu"
            for d in csl_details.values()
        )
        mercury_connected = any(
            d.get("csl") == "Mercury" or d.get("star_lord") == "Mercury"
            for d in csl_details.values()
        )

        partners_needed = business_kp_data.get("partners_needed", False)
        foreign_link    = business_kp_data.get("foreign_link", "No")
        loan_supported  = loan_data.get("loan_supported", False)
        repayment_supported = loan_data.get("repayment_supported", False)

        # ── 1. Organic Growth ────────────────────────────────────
        if h7 == "PROMISE" and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "7th + 11th house promise → Business axis and gains both supported."
        elif h7 == "WEAK_PROMISE" and h11 in ["WEAK_PROMISE", "NEUTRAL"]:
            rating = "MODERATE"
            reason = "Mixed business/gains indicators → Slow, steady organic growth possible."
        elif h7 == "DENIAL":
            rating = "LOW"
            reason = "7th house denial → Current model faces structural limits; explore pivoting."
        else:
            rating = "MODERATE"
            reason = "Moderate growth indicators — monitor timing windows."

        matrix["Organic Growth (Current Model)"] = {"rating": rating, "kp_reasoning": reason}

        # ── 2. Diversification / New Products ───────────────────
        h3_pos = h3 in ["INITIATIVE_POSITIVE", "PROMISE", "WEAK_PROMISE"]
        h5_v   = csl_details.get(5, {}).get("verdict", "NEUTRAL")
        if h3_pos and h5_v in ["FAVORABLE", "STRONG"]:
            rating = "HIGH"
            reason = "3rd initiative + 5th creativity both supported → Diversification recommended."
        elif h3_pos or rahu_connected:
            rating = "MODERATE"
            reason = "3rd house initiative or Rahu supports diversification attempts."
        else:
            rating = "LOW"
            reason = "Focus on strengthening core before branching into new products."

        matrix["Diversification / New Products"] = {"rating": rating, "kp_reasoning": reason}

        # ── 3. Partnership Expansion ─────────────────────────────
        if h7 == "PROMISE" and (partners_needed or h7_csl in stable_planets):
            rating = "HIGH"
            reason = f"7th house PROMISE + partnership signals → Joint ventures recommended."
        elif h7 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "MODERATE"
            reason = "7th house supports partnerships; vet partners carefully before committing."
        else:
            rating = "LOW"
            reason = "7th house denial or neutral — partnerships may complicate growth."

        matrix["Partnership Expansion"] = {"rating": rating, "kp_reasoning": reason}

        # ── 4. Loan-Funded Expansion ─────────────────────────────
        if loan_supported and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "Loan timing active + 11th gains promise → Loan can fuel profitable expansion."
        elif loan_supported:
            rating = "MODERATE"
            reason = "Loan timing favourable but repayment visibility limited — proceed cautiously."
        elif h6 == "CHALLENGING" or h8 == "RISKY":
            rating = "AVOID"
            reason = "❌ 6th/8th obstacles active — loan will compound financial pressure."
        else:
            rating = "LOW"
            reason = "Loan indicators weak — stabilise business cash flow before borrowing."

        matrix["Loan-Funded Expansion"] = {"rating": rating, "kp_reasoning": reason}

        # ── 5. Foreign / Export Expansion ───────────────────────
        h9_pos  = h9 in ["FORTUNE_POSITIVE", "PROMISE", "WEAK_PROMISE"]
        h12_v   = csl_details.get(12, {}).get("verdict", "NEUTRAL")
        foreign_score = (
            (2 if foreign_link == "Yes" else 0) +
            (1 if h9_pos else 0) +
            (1 if rahu_connected else 0) +
            (1 if h12_v in ["FAVORABLE_FOREIGN", "MODERATE"] else 0)
        )
        if foreign_score >= 3:
            rating = "HIGH"
            reason = "Foreign expansion strongly indicated by KP + fortune house alignment."
        elif foreign_score >= 2:
            rating = "MODERATE"
            reason = "Some foreign/export indicators — explore international channels selectively."
        else:
            rating = "LOW"
            reason = "Focus on domestic growth first; foreign indicators are weak."

        matrix["Foreign / Export Expansion"] = {"rating": rating, "kp_reasoning": reason}

        # ── 6. Digital / Online Expansion ────────────────────────
        if mercury_connected and rahu_connected:
            rating = "HIGH"
            reason = "Mercury (tech/communication) + Rahu (digital/unconventional) both active."
        elif mercury_connected or rahu_connected:
            rating = "MODERATE"
            reason = "Mercury or Rahu influence supports digital expansion to a degree."
        else:
            rating = "LOW"
            reason = "Traditional channels may be more effective for this chart."

        matrix["Digital / Online Expansion"] = {"rating": rating, "kp_reasoning": reason}

        # ── 7. Franchise / Licensing ─────────────────────────────
        if h7 in ["PROMISE", "WEAK_PROMISE"] and h11 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "7th + 11th support franchisee relationships and royalty/licensing income."
        elif h7 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "MODERATE"
            reason = "7th house supports franchise deals; gains house needs monitoring."
        else:
            rating = "LOW"
            reason = "Direct ownership and organic growth preferred over franchise model."

        matrix["Franchise / Licensing Model"] = {"rating": rating, "kp_reasoning": reason}

        # ── 8. Acquisition / Merger ──────────────────────────────
        h8_trans = h8 == "TRANSFORMATIVE"
        if h8_trans and h7 in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "8th transformation + 7th business promise → Acquisition can accelerate growth."
        elif h7 in ["PROMISE", "WEAK_PROMISE"] and confidence == "High":
            rating = "MODERATE"
            reason = "Business confidence high — strategic acquisitions can be explored."
        else:
            rating = "LOW"
            reason = "Organic or partnership growth preferred over acquisition at this time."

        matrix["Acquisition / Merger"] = {"rating": rating, "kp_reasoning": reason}

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

        meta          = kwargs.get("meta")
        sub_subdomain = kwargs.get("sub_subdomain", "Identifying Suitable Business")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = getattr(meta, "query_type", None)
        if isinstance(meta_query_type, str):
            meta_query_type = meta_query_type.upper()
        elif hasattr(meta_query_type, "name"):
            meta_query_type = meta_query_type.name

        logger.info("=" * 80)
        logger.info("GROWING EXISTING BUSINESS EVALUATOR v5.0 — UNIFIED VERDICT")
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
                "Best Periods for Business Growth", "Loan Taking Decision",
                "Loan Repayment Decision", "Identifying Suitable Business",
                "Business Challenges",
            ]:
                if not timing_windows_list:
                    timing_windows_list = timing_windows_raw.get(fallback_key, [])
        else:
            timing_windows_list = timing_windows_raw or []

        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: Compute UNIFIED GROWTH VERDICT (Single Source of Truth)
        # ═══════════════════════════════════════════════════════════
        unified_verdict = self._compute_unified_growth_verdict(planets, houses)
        result.additional_data["unified_growth_verdict"] = unified_verdict

        logger.info(f"🎯 UNIFIED GROWTH VERDICT: {unified_verdict['overall_outlook']}")
        logger.info(f"   Confidence:    {unified_verdict['confidence']}")
        logger.info(f"   Growth Viable: {unified_verdict['growth_viable']}")
        logger.info(f"   KP-Vedic Agreement: {unified_verdict['agreement_status']}")
        logger.info(f"   Promise status: {unified_verdict['promise_status']}")

        # ─── KP Business Engine (always run) ─────────────────────
        business_kp_data = evaluate_business_profession(planets, houses)
        service_vs_business_data = determine_service_vs_business(planets, houses)
        logger.info(f"✅ KP Business Engine: confidence={business_kp_data.get('confidence')}")

        # ─── KP Structured Extraction (uses unified verdict) ─────
        try:
            kp_structured = self._extract_kp_growth_structured(
                planets, houses, unified_verdict
            )
            result.additional_data["kp_business_growth_analysis"] = kp_structured

            if kp_structured.get("has_kp_data"):
                logger.info(f"✅ KP structured: {list(kp_structured['csl_details'].keys())}")
                logger.info(f"   Overall: {kp_structured.get('overall_verdict')}")
        except Exception as e:
            logger.warning(f"KP structured extraction error: {e}")
            kp_structured = {"has_kp_data": False, "csl_details": {}}

        # ─── loan_data accumulator ────────────────────────────────
        loan_data: Dict = {}

        # ─── House analysis points (Vedic) ───────────────────────
        self._add_house_analysis_points(
            result, house_lords_info, house_aspects_info, primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # QUESTION BRANCHES — All use unified_verdict for consistency
        # ═══════════════════════════════════════════════════════════

        # ── 1) IDENTIFYING SUITABLE BUSINESS ────────────────────
        if sub_subdomain == "Identifying Suitable Business":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Business growth outlook: **{outlook}** (Confidence: {confidence})"
            )

            for house_num, status in unified_verdict.get("promise_status", {}).items():
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE on growth potential")
            elif agreement == "PARTIAL":
                result.add_point("⚠️ KP and Vedic show PARTIAL agreement — KP takes precedence")
            elif agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT — KP result prioritised")

            result.add_point(
                f"KP: Business strength: **{business_kp_data.get('business_strength_summary')}**"
            )

            sectors = business_kp_data.get("final_professions", [])
            if sectors:
                result.add_point(f"KP: Suitable business areas: {', '.join(sectors[:5])}")

            result.add_point(
                f"KP: Partnership indicated: **{business_kp_data.get('partners_needed')}**"
            )
            result.add_point(
                f"KP: Foreign link: **{business_kp_data.get('foreign_link')}**"
            )
            result.add_point(
                f"KP: Service vs Business determination: **{service_vs_business_data.get('final_path')}**"
            )

        # ── 2A) LOAN TAKING DECISION ─────────────────────────────
        elif sub_subdomain == "Loan Taking Decision":

            result.add_point(
                f"KP: Business growth outlook: **{unified_verdict['overall_outlook']}** "
                f"(Confidence: {unified_verdict['confidence']})"
            )
            result.add_point(
                f"KP: Business viability: **{business_kp_data.get('business_strength_summary')}**"
            )

            try:
                loan_rules   = TIMING_RULES.get("Loan Taking Timing", {})
                loan_scores  = score_kp_all_planets(planets, houses, loan_rules)
                loan_planets = get_positive_planets(loan_scores)

                if loan_planets:
                    result.add_point(
                        f"KP: Loan-taking indicators active through: {', '.join(loan_planets[:3])}."
                    )
                    result.add_point(
                        "KP: Loan during indicated dasha can support business expansion."
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
                f"KP: Business growth outlook: **{unified_verdict['overall_outlook']}**"
            )
            result.add_point(
                f"KP: Business viability: **{business_kp_data.get('business_strength_summary')}**"
            )

            h11_status = unified_verdict.get("promise_status", {}).get(11, "NEUTRAL")
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
                    "KP: Growth confidence low — stabilise revenue before aggressive repayment."
                )

            result.additional_data.update(loan_data)

        # ── 3) BEST PERIODS FOR BUSINESS GROWTH (TIMING) ────────
        elif sub_subdomain == "Best Periods for Business Growth":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Growth timing evaluated. Overall outlook: **{outlook}** "
                f"(Confidence: {confidence})"
            )

            # Key house promise for timing context
            for house_num in [7, 10, 11, 3, 9]:
                status  = unified_verdict.get("promise_status", {}).get(house_num, "NEUTRAL")
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

            try:
                growth_rules  = TIMING_RULES.get("Best Periods for Business Growth", {})
                growth_scores = score_kp_all_planets(planets, houses, growth_rules)
                growth_planets = get_positive_planets(growth_scores)

                if growth_planets:
                    result.add_point(
                        f"KP: Expansion-supporting planets: {', '.join(growth_planets[:4])}."
                    )
                    loan_data["growth_planets"] = growth_planets[:4]

                # Also score loan indicators for growth period planning
                loan_rules   = TIMING_RULES.get("Loan Taking Timing", {})
                loan_scores  = score_kp_all_planets(planets, houses, loan_rules)
                loan_planets = get_positive_planets(loan_scores)
                loan_data["loan_supported"] = bool(loan_planets)
                loan_data["loan_planets"]   = loan_planets[:3] if loan_planets else []

                result.additional_data.update(loan_data)
            except Exception as e:
                logger.warning(f"Growth timing error: {e}")

            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE — timing windows are reliable")
            elif agreement == "CONFLICT":
                result.add_point("⚠️ KP-Vedic CONFLICT — use KP timing windows, Vedic shows effort needed")

        # ── 4) BUSINESS CHALLENGES ───────────────────────────────
        elif sub_subdomain == "Business Challenges":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Business growth outlook: **{outlook}** (Confidence: {confidence})"
            )
            result.add_point(
                f"KP: Business strength: **{business_kp_data.get('business_strength_summary')}**"
            )

            # Show obstacle house status
            for house_num in [6, 8, 12]:
                status  = unified_verdict.get("promise_status", {}).get(house_num, "NEUTRAL")
                meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({meaning}): {status}")

            # Agreement
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT on obstacles — KP result prioritised")
            elif agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic AGREE on challenge sources")

            if confidence == "Low":
                result.add_point(
                    "KP: Chart shows sustained growth pressure — challenges are structural, not just cyclical."
                )
            elif confidence == "Moderate":
                result.add_point(
                    "KP: Temporary slowdown indicated — targeted strategy can overcome obstacles."
                )
            else:
                result.add_point(
                    "KP: Challenges appear cyclical — timing windows will reveal recovery periods."
                )

        elif sub_subdomain == "Business Remedies":

            outlook    = unified_verdict["overall_outlook"]
            confidence = unified_verdict["confidence"]

            result.add_point(
                f"KP: Business growth outlook: **{outlook}** (Confidence: {confidence})"
            )

            # Target remedies based on obstacle houses
            h6 = unified_verdict.get("promise_status", {}).get(6, "NEUTRAL")
            h8 = unified_verdict.get("promise_status", {}).get(8, "NEUTRAL")
            h12 = unified_verdict.get("promise_status", {}).get(12, "NEUTRAL")

            if h6 == "CHALLENGING":
                result.add_point("Remedy Focus: Strengthen 6th house (debt, competition management).")

            if h8 in ["RISKY", "UNPREDICTABLE"]:
                result.add_point("Remedy Focus: Stabilise sudden fluctuations (8th house correction).")

            if h12 in ["DENIAL"]:
                result.add_point("Remedy Focus: Control expenses and leakage (12th house).")

            result.add_point("General: Strengthen 7th and 11th house lords for business growth support.")
        # ── FALLBACK ─────────────────────────────────────────────
        else:
            result.add_point(
                f"KP: Growth outlook: **{unified_verdict['overall_outlook']}** "
                f"(Confidence: {unified_verdict['confidence']})"
            )

        # ─── Build Growth Matrix (uses unified verdict) ───────────
        if kp_structured.get("has_kp_data"):
            try:
                growth_matrix = self._create_business_growth_matrix(
                    unified_verdict, kp_structured, business_kp_data, loan_data
                )
                result.additional_data["business_growth_suitability_matrix"] = growth_matrix
            except Exception as e:
                logger.error(f"Growth matrix error: {e}")

        # ─── Store Everything for LLM ─────────────────────────────
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            business_kp_data,
            service_vs_business_data,
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

            lord_dignity        = "Unknown"
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
                        lord_dignity        = dignity.value if hasattr(dignity, "value") else str(dignity)
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity
                        )
                except Exception as e:
                    logger.warning(f"Could not analyze dignity for {normalized_lord}: {e}")
            else:
                lord_dignity        = self._get_planet_dignity(normalized_lord, lord_data)
                lord_strength_score = self._calculate_lord_strength(
                    normalized_lord, lord_data, lord_dignity
                )

            planets_in_house = []
            for p in h.get("planets", []):
                pn = normalize_planet_name(self.extract_planet_name(p))
                if pn:
                    planets_in_house.append(pn)

            house_lords_info[house_num] = {
                "lord":               normalized_lord,
                "lord_in_house":      lord_data.get("house"),
                "lord_in_sign":       lord_data.get("sign", ""),
                "lord_degree":        (lord_data.get("full_degree") or lord_data.get("global_degree") or lord_data.get("degree") or 0),
                "lord_is_combust":    (lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)),
                "lord_is_retrograde": (lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)),
                "lord_dignity":       lord_dignity,
                "lord_strength_score": lord_strength_score,
                "priority":           "primary" if house_num in primary_houses else "secondary",
                "planets_in_house":   planets_in_house,
                "house_sign":         (h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""),
            }

        return house_lords_info

    def _extract_lagna_info(self, houses: List[Dict], planets: Dict[str, Dict]) -> Optional[Dict]:
        """Extract lagna information."""
        try:
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            if not house_1:
                return None

            lagna_sign = house_1.get("sign") or house_1.get("start_rasi") or ""
            if not lagna_sign:
                return None

            lagna_lord_name = self._get_house_lord(house_1) or ""
            if not lagna_lord_name:
                return None

            lagna_lord = normalize_planet_name(lagna_lord_name)
            if not lagna_lord:
                return None

            lagna_lord_data = planets.get(lagna_lord, {})

            return {
                "lagna_sign":        lagna_sign,
                "lagna_lord":        lagna_lord,
                "lagna_lord_house":  lagna_lord_data.get("house"),
                "lagna_lord_sign":   lagna_lord_data.get("sign", ""),
                "lagna_lord_degree": (lagna_lord_data.get("full_degree") or lagna_lord_data.get("degree") or 0),
                "lagna_lord_dignity": self._get_planet_dignity(lagna_lord, lagna_lord_data),
            }
        except Exception as e:
            logger.error(f"Error extracting lagna: {e}")
            return None

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
            house_aspects[house_num] = {
                "benefic_aspects": [],
                "malefic_aspects": [],
                "neutral_aspects": [],
            }
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

    def _add_house_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
    ):
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue
            info = house_lords_info[house_num]
            point = (
                f"House {house_num} ({self.HOUSE_MEANINGS.get(house_num, 'General')}): "
                f"Lord {info['lord']} is {info['lord_dignity']} "
                f"(Strength: {info['lord_strength_score']}/100)"
            )
            if info["lord_is_combust"]:
                point += " [COMBUST]"
            if info["lord_is_retrograde"]:
                point += " [RETROGRADE]"
            result.add_point(point)

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
        service_vs_business_data: dict = None,
        current_dasha: dict = None,
        dasha_timeline: dict = None,
    ):
        domain_prefix = "business_growth"

        result.additional_data.update({
            f"{domain_prefix}_house_config": {
                "primary":   list(primary_houses),
                "secondary": list(secondary_houses),
                "source":    house_config.get("source", "fallback") if house_config else "fallback",
            },
            f"{domain_prefix}_house_lords":   house_lords_info,
            f"{domain_prefix}_house_aspects":  house_aspects_info,
            f"{domain_prefix}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
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
            }

        if service_vs_business_data:
            result.additional_data["service_vs_business"] = service_vs_business_data

        if timing_windows_data and timing_windows_data.get("has_timing"):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        logger.info("RESULT BREAKDOWN START")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")
        if "unified_growth_verdict" in ad:
            uv = ad["unified_growth_verdict"]
            logger.info(f"  unified_growth_verdict: {uv.get('overall_outlook')}")
            logger.info(f"  confidence: {uv.get('confidence')}")
            logger.info(f"  agreement: {uv.get('agreement_status')}")
        if "kp_business_growth_analysis" in ad:
            logger.info(
                f"  kp_business_growth_analysis: {ad['kp_business_growth_analysis'].get('overall_verdict')}"
            )
        if "business_growth_suitability_matrix" in ad:
            logger.info(
                f"  business_growth_suitability_matrix: "
                f"{len(ad['business_growth_suitability_matrix'])} options"
            )
        logger.info("RESULT BREAKDOWN END")

    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ═══════════════════════════════════════════════════════════════

    def get_questions(self) -> List[Question]:
        return [
            Question(id="BUS_GE_1", question="Is this the right business for me and what guidance for growth/diversification?", meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.POSITIVE, InterpretationGoal.STATUS), sub_subdomain="Identifying Suitable Business"),
            Question(id="BUS_GE_2A", question="Should I take a loan for business growth and when?", meta=QueryMeta(QueryType.TIMING, EventPolarity.POSITIVE, InterpretationGoal.MANIFESTATION), sub_subdomain="Loan Taking Decision"),
            Question(id="BUS_GE_2B", question="When will loan repayment be manageable?", meta=QueryMeta(QueryType.TIMING, EventPolarity.POSITIVE, InterpretationGoal.MANIFESTATION), sub_subdomain="Loan Repayment Decision"),
            Question(id="BUS_GE_3", question="What obstacles might I face and how to overcome them?", meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEGATIVE, InterpretationGoal.RISK), sub_subdomain="Business Challenges"),
            Question(id="BUS_GE_4", question="Which remedies can support my business growth?", meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.POSITIVE, InterpretationGoal.SUPPORT), sub_subdomain="Business Remedies"),
        ]


# ─── Module-level helper (outside class, used in growth ranking) ────────────
def _growth_score(h_primary: str, h_secondary: str, w_primary: int, w_secondary: int) -> int:
    """Score a growth option from two promise statuses."""
    score_map = {
        "PROMISE":             3,
        "INITIATIVE_POSITIVE": 3,
        "FORTUNE_POSITIVE":    3,
        "TRANSFORMATIVE":      2,
        "WEAK_PROMISE":        2,
        "MANAGEABLE":          1,
        "MODERATE":            1,
        "NEUTRAL":             0,
        "CHALLENGING":        -1,
        "RISKY":              -1,
        "INITIATIVE_BLOCKED": -1,
        "DENIAL":             -2,
        "UNKNOWN":             0,
    }
    return (
        score_map.get(h_primary, 0) * w_primary +
        score_map.get(h_secondary, 0) * w_secondary
    )
    
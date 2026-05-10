"""
Growth and Security Evaluator - ENHANCED VERSION v4.0

Based on CareerDiscoveryAndEmploymentEvaluator v5.0 + ProspectsOfInvestmentsEvaluator v3.3 architecture.

FIXES FROM v3.0:
✅ UNIFIED CAREER VERDICT - _compute_unified_career_verdict() from CareerDiscoveryEvaluator v5.0
✅ PURE KP METHODOLOGY - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ CORRECT HOUSE MAPPING - Service: 2,6,10,11 | Business: 2,3,7,11
✅ STRUCTURED KP EXTRACTION - _extract_kp_career_structured() stored in additional_data
✅ CAREER SUITABILITY MATRIX - _create_career_suitability_matrix() for LLM consumption
✅ LAGNA INFO EXTRACTION - _extract_lagna_info() stored in additional_data
✅ FULL HELPER METHODS - _get_planet_significations(), _apply_pure_kp_chain(), etc.
✅ RAHU/KETU PROPER HANDLING - Star lord + sign lord + conjunctions
✅ LOG RESULT BREAKDOWN - _log_result_breakdown() for debugging
✅ CONSISTENT OUTPUT ACROSS ALL QUESTIONS - Same base verdict used everywhere
✅ TimingWindow dataclass compatibility preserved

Covers:
- Promotions, raises, leadership roles, transfers - KP Points + Timing
- Long-term career growth and recognition
- Career stagnation and workplace risks (LLM-driven) - Questions 2, 3
- Remedies for career stability and growth
"""

from typing import Dict, List, Optional, Tuple, Set
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
from app.core.astro_constants import KP_PROFESSION_MAP

from app.domains.career.kp_career_engine import (
    evaluate_service_profession
)

from app.services.timing_engine import (
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets,
    TIMING_RULES
)

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


class GrowthAndSecurityEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Career → Growth And Security
    v4.0 - Unified decision layer + pure KP methodology

    Features:
    - Question-specific houses from Excel config
    - Unified career verdict (single source of truth)
    - Pure KP chain: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - Structured KP data stored for LLM
    - Career suitability matrix
    - Lagna info extraction
    - KP timing (for Promotion Timing question)
    - Timing windows extraction and formatting
    - LLM-driven for Questions 2, 3 (risks/advice)
    """

    domain = "Career"
    subtopic = "Growth And Security"

    # ═══════════════════════════════════════════════════════════════
    # HOUSE DEFINITIONS (KP Standard — matches CareerDiscovery v5.0)
    # ═══════════════════════════════════════════════════════════════

    SERVICE_HOUSES = {2, 6, 10, 11}
    BUSINESS_HOUSES = {2, 3, 7, 11}
    WEALTH_HOUSES = {2, 10, 11}
    LOSS_HOUSES = {6, 8, 12}
    FOREIGN_HOUSES = {3, 9, 12}

    HOUSE_MEANINGS = {
        1: "Self/Initiative",
        2: "Income/Wealth",
        3: "Efforts/Courage",
        6: "Service/Competition",
        7: "Business/Partnership",
        9: "Fortune/Luck",
        10: "Career/Authority",
        11: "Gains/Recognition",
        12: "Losses/Expenses"
    }

    # KP Strength Hierarchy
    KP_WEIGHT = {
        "sub_lord": 4,
        "star_lord": 3,
        "occupy": 2,
        "own": 1
    }

    # ═══════════════════════════════════════════════════════════════
    # UNIFIED CAREER DECISION LAYER (Single Source of Truth)
    # ═══════════════════════════════════════════════════════════════

    def _compute_unified_career_verdict(
        self,
        planets: Dict,
        houses: List,
        kp_analysis: Dict = None
    ) -> Dict:
        """
        SINGLE SOURCE OF TRUTH for career path determination.
        All questions must use this verdict for consistency.

        Returns:
            {
                "primary_path": "Service" | "Business" | "Hybrid",
                "secondary_path": str,
                "service_score": int,
                "business_score": int,
                "confidence": "High" | "Moderate" | "Low",
                "kp_reasoning": str,
                "vedic_reasoning": str,
                "agreement_status": "AGREEMENT" | "PARTIAL" | "CONFLICT",
                "career_ranking": [list of ranked career paths],
                "promise_status": {house: "PROMISE" | "DENIAL" | "WEAK"}
            }
        """
        result = {
            "primary_path": "Unknown",
            "secondary_path": None,
            "service_score": 0,
            "business_score": 0,
            "confidence": "Low",
            "kp_reasoning": "",
            "vedic_reasoning": "",
            "agreement_status": "UNKNOWN",
            "career_ranking": [],
            "promise_status": {},
            "detailed_analysis": {}
        }

        # ─── STEP 1: Pure KP Analysis ───────────────────────────
        kp_service_score = 0
        kp_business_score = 0
        kp_reasons = []
        promise_status = {}

        key_cusps = {
            6: "Service/Employment",
            7: "Business/Partnership",
            10: "Career/Profession"
        }

        for cusp_num, meaning in key_cusps.items():
            cusp_data = next((h for h in houses if h.get("house") == cusp_num), None)
            if not cusp_data:
                continue

            chain_result = self._apply_pure_kp_chain(cusp_data, planets, houses)

            if chain_result:
                promise_status[cusp_num] = chain_result.get("promise_status", "UNKNOWN")

                sub_lord_houses = set(chain_result.get("sub_lord_signifies", []))
                star_lord_houses = set(chain_result.get("star_lord_signifies", []))

                service_conn = 0
                business_conn = 0

                service_conn += len(sub_lord_houses & self.SERVICE_HOUSES) * self.KP_WEIGHT["sub_lord"]
                business_conn += len(sub_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["sub_lord"]

                service_conn += len(star_lord_houses & self.SERVICE_HOUSES) * self.KP_WEIGHT["star_lord"]
                business_conn += len(star_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["star_lord"]

                csl_house = chain_result.get("csl_house")
                if csl_house in self.SERVICE_HOUSES:
                    service_conn += self.KP_WEIGHT["occupy"]
                if csl_house in self.BUSINESS_HOUSES:
                    business_conn += self.KP_WEIGHT["occupy"]

                if cusp_num == 6:
                    kp_service_score += service_conn
                    if chain_result.get("promise_status") == "PROMISE":
                        kp_reasons.append(
                            f"6th CSL promises employment (sub-lord signifies {sorted(sub_lord_houses & self.SERVICE_HOUSES)})"
                        )
                    elif chain_result.get("promise_status") == "DENIAL":
                        kp_reasons.append("6th CSL denies easy employment (sub-lord signifies loss houses)")

                elif cusp_num == 7:
                    kp_business_score += business_conn
                    if chain_result.get("promise_status") == "PROMISE":
                        kp_reasons.append(
                            f"7th CSL promises business success (sub-lord signifies {sorted(sub_lord_houses & self.BUSINESS_HOUSES)})"
                        )
                    elif chain_result.get("promise_status") == "DENIAL":
                        kp_reasons.append("7th CSL denies business (sub-lord signifies loss houses)")

                elif cusp_num == 10:
                    kp_reasons.append("10th CSL influences career strength (direction decided by 6th vs 7th)")

                result["detailed_analysis"][cusp_num] = chain_result

        result["promise_status"] = promise_status

        # ─── STEP 2: Vedic Analysis ──────────────────────────────
        vedic_service_score = 0
        vedic_business_score = 0
        vedic_reasons = []

        for house_num in [6, 7, 10]:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            lord_name = self._get_house_lord(house_data)
            if not lord_name:
                continue

            lord_data = planets.get(lord_name, {})
            lord_house = lord_data.get("house")

            if house_num == 6:
                if lord_house in self.SERVICE_HOUSES:
                    vedic_service_score += 3
                    vedic_reasons.append(
                        f"6th lord {lord_name} in house {lord_house} → strong service indication"
                    )
                elif lord_house in self.LOSS_HOUSES:
                    vedic_service_score -= 1
                    vedic_reasons.append(
                        f"6th lord {lord_name} in loss house → employment challenges"
                    )

            elif house_num == 7:
                if lord_house in self.BUSINESS_HOUSES:
                    vedic_business_score += 3
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business potential"
                    )
                elif lord_house in {6, 8, 12}:
                    vedic_business_score -= 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business obstacles"
                    )

            elif house_num == 10:
                dignity = self._get_planet_dignity(lord_name, lord_data)
                if dignity in ["EXALTED", "OWN_SIGN"]:
                    vedic_service_score += 2
                    vedic_business_score += 1
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → strong career foundation"
                    )
                elif dignity == "DEBILITATED":
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → career challenges"
                    )

        # ─── STEP 3: Pure KP Verdict (Sub-Lord Dominant) ────────
        h6 = promise_status.get(6, "NEUTRAL")
        h7 = promise_status.get(7, "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")

        if h6 == "PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"
        elif h7 == "PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"
        elif h6 == "PROMISE" and h7 == "PROMISE":
            primary = "Hybrid"
        elif h6 == "WEAK_PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"
        elif h7 == "WEAK_PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"
        elif h6 == "DENIAL" and h7 == "DENIAL":
            primary = "Unstable"
        else:
            primary = "Hybrid"

        result["primary_path"] = primary
        result["service_score"] = kp_service_score
        result["business_score"] = kp_business_score

        # ─── STEP 4: Confidence from 10th Cusp ──────────────────
        if h10 == "PROMISE":
            confidence = "High"
        elif h10 == "WEAK_PROMISE":
            confidence = "Moderate"
        elif h10 == "DENIAL":
            confidence = "Low"
        else:
            confidence = "Moderate"

        result["confidence"] = confidence

        # ─── STEP 5: Vedic-KP Agreement ─────────────────────────
        kp_verdict = result["primary_path"]
        if vedic_service_score == 0 and vedic_business_score == 0:
            vedic_verdict = "Neutral"
        elif vedic_service_score > vedic_business_score:
            vedic_verdict = "Service"
        elif vedic_business_score > vedic_service_score:
            vedic_verdict = "Business"
        else:
            vedic_verdict = "Neutral"

        if kp_verdict == vedic_verdict:
            result["agreement_status"] = "AGREEMENT"
        elif kp_verdict == "Hybrid":
            result["agreement_status"] = "PARTIAL"
        else:
            result["agreement_status"] = "CONFLICT"

        # ─── STEP 6: Career Ranking ──────────────────────────────
        career_paths = []

        govt_score = 0
        if promise_status.get(6) == "PROMISE":
            govt_score += 3
        if any(p in ["Sun", "Saturn"] for p in self._get_10th_chain_planets(planets, houses)):
            govt_score += 2
        career_paths.append(("Government Job", govt_score))

        private_score = 0
        if promise_status.get(6) == "PROMISE":
            private_score += 2
        if promise_status.get(10) == "PROMISE":
            private_score += 2
        career_paths.append(("Private Sector Job", private_score))

        business_path_score = 0
        if promise_status.get(7) == "PROMISE":
            business_path_score += 3
        if result["primary_path"] == "Business":
            business_path_score += 2
        career_paths.append(("Business/Self-Employment", business_path_score))

        tech_score = 0
        if self._has_planet_connection(["Rahu", "Saturn", "Mercury"], planets, houses, {3, 10}):
            tech_score += 3
        career_paths.append(("Technical/IT Roles", tech_score))

        creative_score = 0
        if self._has_planet_connection(["Venus", "Moon"], planets, houses, {5, 10}):
            creative_score += 3
        career_paths.append(("Creative/Arts", creative_score))

        mgmt_score = 0
        if self._has_planet_connection(["Sun", "Jupiter", "Mars"], planets, houses, {10, 11}):
            mgmt_score += 3
        career_paths.append(("Management/Leadership", mgmt_score))

        foreign_score = 0
        if self._has_planet_connection(["Rahu"], planets, houses, {9, 12}):
            foreign_score += 3
        career_paths.append(("Foreign/Multinational", foreign_score))

        career_paths.sort(key=lambda x: x[1], reverse=True)
        result["career_ranking"] = [
            {"path": path, "score": score, "rating": self._score_to_rating(score)}
            for path, score in career_paths
        ]

        result["kp_reasoning"] = " | ".join(kp_reasons) if kp_reasons else "KP analysis incomplete"
        result["vedic_reasoning"] = " | ".join(vedic_reasons) if vedic_reasons else "Vedic analysis incomplete"

        return result

    # ═══════════════════════════════════════════════════════════════
    # PURE KP CHAIN
    # ═══════════════════════════════════════════════════════════════

    def _apply_pure_kp_chain(
        self,
        cusp_data: Dict,
        planets: Dict,
        houses: List
    ) -> Dict:
        """
        Apply PURE KP methodology: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
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
            "interpretation": ""
        }

        csl_name = cusp_data.get("cusp_sub_lord", "")
        csl = normalize_planet_name(csl_name)

        if not csl:
            return result

        result["csl"] = csl
        csl_data = planets.get(csl, {})
        result["csl_house"] = csl_data.get("house")
        result["csl_nakshatra"] = csl_data.get("nakshatra", "")

        star_lord_name = csl_data.get("nakshatra_lord", "")
        star_lord = normalize_planet_name(star_lord_name)
        result["star_lord"] = star_lord

        if star_lord:
            star_lord_houses = self._get_planet_significations(star_lord, planets, houses)
            result["star_lord_signifies"] = sorted(star_lord_houses)

        sub_lord_name = csl_data.get("sub_lord", "")
        sub_lord = normalize_planet_name(sub_lord_name)
        result["sub_lord"] = sub_lord

        if sub_lord:
            sub_lord_houses = self._get_planet_significations(sub_lord, planets, houses)
            result["sub_lord_signifies"] = sorted(sub_lord_houses)

            house_num = cusp_data.get("house", 0)
            promise_status = self._evaluate_sub_lord_promise(
                house_num,
                sub_lord_houses,
                result.get("star_lord_signifies", [])
            )
            result["promise_status"] = promise_status

        chain_parts = [f"CSL: {csl}"]
        if star_lord:
            chain_parts.append(f"Star Lord: {star_lord} → signifies {result['star_lord_signifies']}")
        if sub_lord:
            chain_parts.append(f"Sub Lord: {sub_lord} → signifies {result['sub_lord_signifies']}")
        chain_parts.append(f"Promise: {result['promise_status']}")

        result["chain_text"] = " | ".join(chain_parts)

        return result

    def _evaluate_sub_lord_promise(
        self,
        cusp_house: int,
        sub_lord_houses: List[int],
        star_lord_houses: List[int]
    ) -> str:
        """
        KP Promise/Denial Logic based on sub-lord significations.
        """
        sub_set = set(sub_lord_houses)

        if cusp_house == 6:
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & {8, 12}:
                return "PROMISE"
            elif sub_set & {8, 12} and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            else:
                return "NEUTRAL"

        elif cusp_house == 7:
            positive = {2, 3, 7, 11}
            if sub_set & positive and not sub_set & {8, 12}:
                return "PROMISE"
            elif sub_set & {8, 12} and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            else:
                return "NEUTRAL"

        elif cusp_house == 10:
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & {8, 12}:
                return "PROMISE"
            elif sub_set & {8, 12} and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            else:
                return "NEUTRAL"

        return "NEUTRAL"

    def _get_planet_significations(
        self,
        planet_name: str,
        planets: Dict,
        houses: List,
        visited: Optional[Set[str]] = None
    ) -> List[int]:
        """
        Get houses signified by a planet using KP methodology.
        Safe against recursive loops.
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

        # Handle Rahu/Ketu safely
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
        occupied_house = planet_data.get("house")
        if occupied_house:
            signified.add(occupied_house)

        # 2. Owned houses
        owned_houses = self._get_owned_houses(planet_name, houses)
        signified.update(owned_houses)

        # 3. Planets in star of this planet
        for p_name, p_data in planets.items():
            if p_name == planet_name:
                continue
            star_lord = normalize_planet_name(p_data.get("nakshatra_lord"))
            if star_lord == planet_name:
                p_house = p_data.get("house")
                if p_house:
                    signified.add(p_house)
                p_owned = self._get_owned_houses(p_name, houses)
                signified.update(p_owned)

        return sorted(signified)

    def _get_owned_houses(self, planet_name: str, houses: List) -> List[int]:
        """Get houses owned by a planet."""
        owned = []
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        for h in houses:
            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
            if house_sign and sign_lords.get(house_sign) == planet_name:
                owned.append(h.get("house"))
        return owned

    def _get_sign_lord(self, sign: str) -> Optional[str]:
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        return sign_lords.get(sign)

    def _get_house_lord(self, house_data: Dict) -> Optional[str]:
        """Get lord of a house."""
        lord_name = (
            house_data.get("rashi_lord") or
            house_data.get("sign_lord") or
            house_data.get("lord") or
            ""
        )

        if not lord_name:
            sign = house_data.get("sign") or house_data.get("start_rasi") or house_data.get("rasi")
            if sign:
                sign_lords = {
                    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
                    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
                    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
                    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                }
                lord_name = sign_lords.get(sign, "")

        return normalize_planet_name(lord_name)

    def _get_planet_dignity(self, planet_name: str, planet_data: Dict) -> str:
        """Get dignity of a planet."""
        sign = planet_data.get("sign", "")

        exaltation = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
            "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
            "Saturn": "Libra"
        }
        debilitation = {
            "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
            "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
            "Saturn": "Aries"
        }
        own_signs = {
            "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"]
        }

        if exaltation.get(planet_name) == sign:
            return "EXALTED"
        if debilitation.get(planet_name) == sign:
            return "DEBILITATED"
        if sign in own_signs.get(planet_name, []):
            return "OWN_SIGN"
        return "NEUTRAL"

    def _get_10th_chain_planets(self, planets: Dict, houses: List) -> List[str]:
        """Get planets involved in 10th house chain."""
        chain = []
        h10 = next((h for h in houses if h.get("house") == 10), None)
        if not h10:
            return chain
        csl = h10.get("cusp_sub_lord")
        if csl:
            chain.append(normalize_planet_name(csl))
        if csl and csl in planets:
            star_lord = planets[csl].get("nakshatra_lord")
            if star_lord:
                chain.append(normalize_planet_name(star_lord))
        return [p for p in chain if p]

    def _has_planet_connection(
        self,
        target_planets: List[str],
        planets: Dict,
        houses: List,
        target_houses: Set[int]
    ) -> bool:
        """Check if any target planet connects to target houses."""
        for planet in target_planets:
            if planet not in planets:
                continue
            p_data = planets[planet]
            p_house = p_data.get("house")
            if p_house in target_houses:
                return True
            star_lord = p_data.get("nakshatra_lord")
            if star_lord and star_lord in planets:
                sl_house = planets[star_lord].get("house")
                if sl_house in target_houses:
                    return True
        return False

    def _score_to_rating(self, score: int) -> str:
        if score >= 5:
            return "HIGH"
        elif score >= 3:
            return "MODERATE"
        elif score >= 1:
            return "LOW"
        else:
            return "VERY_LOW"

    # ═══════════════════════════════════════════════════════════════
    # CAREER SUITABILITY MATRIX
    # ═══════════════════════════════════════════════════════════════

    def _create_career_suitability_matrix(
        self,
        unified_verdict: Dict,
        kp_analysis: Dict = None
    ) -> Dict[str, Dict]:
        """
        Create career suitability matrix using UNIFIED verdict for consistency.
        """
        matrix = {}
        career_ranking = unified_verdict.get("career_ranking", [])

        for item in career_ranking:
            path = item.get("path", "Unknown")
            rating = item.get("rating", "LOW")
            score = item.get("score", 0)

            if path == "Government Job":
                if unified_verdict.get("promise_status", {}).get(6) == "PROMISE":
                    reason = "6th CSL promises employment + authority planet connection"
                else:
                    reason = "Service indicators present but not strongly favorable for government"

            elif path == "Private Sector Job":
                if unified_verdict.get("primary_path") == "Service":
                    reason = "Primary path is Service → private sector suitable"
                else:
                    reason = "Business inclination may override private employment"

            elif path == "Business/Self-Employment":
                if unified_verdict.get("promise_status", {}).get(7) == "PROMISE":
                    reason = "7th CSL promises business success"
                elif unified_verdict.get("primary_path") == "Business":
                    reason = "Overall indicators favor business path"
                else:
                    reason = "Service path may be more suitable"

            elif path == "Technical/IT Roles":
                reason = "Based on Rahu/Saturn/Mercury connection to 3rd/10th houses"

            elif path == "Creative/Arts":
                reason = "Based on Venus/Moon connection to 5th/10th houses"

            elif path == "Management/Leadership":
                reason = "Based on Sun/Jupiter/Mars connection to 10th/11th houses"

            elif path == "Foreign/Multinational":
                reason = "Based on Rahu connection to 9th/12th houses"

            else:
                reason = "General assessment based on house significations"

            matrix[path] = {
                "rating": rating,
                "score": score,
                "kp_reasoning": reason
            }

        return matrix

    # ═══════════════════════════════════════════════════════════════
    # STRUCTURED KP EXTRACTION
    # ═══════════════════════════════════════════════════════════════

    def _extract_kp_career_structured(
        self,
        planets: Dict,
        houses: List,
        unified_verdict: Dict
    ) -> Dict:
        """
        Extract structured KP career data using PURE methodology.
        Uses unified verdict for consistency.
        """
        kp_data = {
            "csl_details": {},
            "overall_verdict": unified_verdict.get("primary_path", "UNKNOWN"),
            "key_findings": [],
            "has_kp_data": False,
            "methodology": "CSL → Sub Lord → Star Lord → Significations → Promise/Denial"
        }

        career_houses = [2, 6, 7, 9, 10, 11]

        for house_num in career_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            chain_result = self._apply_pure_kp_chain(house_data, planets, houses)

            if chain_result.get("csl"):
                kp_data["has_kp_data"] = True

                csl = chain_result["csl"]
                promise = chain_result.get("promise_status", "NEUTRAL")

                if promise == "PROMISE":
                    verdict = "STRONG"
                elif promise == "DENIAL":
                    verdict = "WEAK"
                elif promise == "WEAK_PROMISE":
                    verdict = "MODERATE"
                else:
                    verdict = "NEUTRAL"

                interpretation = self._build_kp_interpretation(
                    house_num, chain_result, unified_verdict
                )

                kp_data["csl_details"][house_num] = {
                    "house_meaning": self.HOUSE_MEANINGS.get(house_num, "General"),
                    "csl": csl,
                    "csl_house": chain_result.get("csl_house"),
                    "csl_flavor": "benefic" if csl in ["Jupiter", "Venus", "Mercury", "Moon"] else "malefic",
                    "nakshatra": chain_result.get("csl_nakshatra", ""),
                    "star_lord": chain_result.get("star_lord"),
                    "star_lord_signifies": chain_result.get("star_lord_signifies", []),
                    "sub_lord": chain_result.get("sub_lord"),
                    "sub_lord_signifies": chain_result.get("sub_lord_signifies", []),
                    "promise_status": promise,
                    "verdict": verdict,
                    "interpretation": interpretation,
                    "chain": chain_result.get("chain_text", ""),
                    "has_significations": bool(chain_result.get("sub_lord_signifies"))
                }

                kp_data["key_findings"].append(
                    f"House {house_num}: {csl} → Sub Lord {chain_result.get('sub_lord')} → "
                    f"signifies {chain_result.get('sub_lord_signifies', [])} → {promise}"
                )

        kp_data["overall_verdict"] = unified_verdict.get("primary_path", "UNKNOWN")
        kp_data["agreement_status"] = unified_verdict.get("agreement_status", "UNKNOWN")

        return kp_data

    def _build_kp_interpretation(
        self,
        house_num: int,
        chain_result: Dict,
        unified_verdict: Dict
    ) -> str:
        """Build human-readable KP interpretation."""
        csl = chain_result.get("csl", "Unknown")
        sub_lord = chain_result.get("sub_lord", "Unknown")
        sub_houses = chain_result.get("sub_lord_signifies", [])
        promise = chain_result.get("promise_status", "NEUTRAL")

        if house_num == 6:
            if promise == "PROMISE":
                return (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Strong service house connection → Employment PROMISED."
                )
            elif promise == "DENIAL":
                return (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss house dominance → Employment faces obstacles."
                )
            else:
                return (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Mixed indicators → Moderate employment capacity."
                )

        elif house_num == 7:
            if promise == "PROMISE":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Strong business house connection → Partnership/trade PROMISED."
                )
            elif promise == "DENIAL":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss/competition houses dominate → Business NOT favored."
                )
            else:
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Mixed business indicators → Moderate potential."
                )

        elif house_num == 10:
            primary_path = unified_verdict.get("primary_path", "Unknown")
            if promise == "PROMISE":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Career houses activated → Professional success PROMISED. "
                    f"Primary path: {primary_path}."
                )
            elif promise == "DENIAL":
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Career challenges indicated."
                )
            else:
                return (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate career indicators → Steady progress expected."
                )

        else:
            return (
                f"House {house_num}: CSL {csl} → Sub Lord {sub_lord} → "
                f"Signifies {sub_houses} → {promise}"
            )

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

        # Choose data source
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        # ─── STEP 1: Question-Specific Houses ───────────────────
        question_text = kwargs.get("question", "")

        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses | {1}
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning("No config for question, using fallback")
            all_relevant_houses = {1, 2, 3, 6, 9, 10, 11}
            primary_houses = {10, 11, 9}
            secondary_houses = {1, 2, 3, 6}

        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Growth And Security")
        profession_map = kwargs.get("profession_map") or KP_PROFESSION_MAP

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, "query_type") else None

        logger.info("=" * 80)
        logger.info("GROWTH AND SECURITY EVALUATOR (ENHANCED v4.0 - UNIFIED KP)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ─── STEP 2: Aspects ─────────────────────────────────────
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ─── STEP 3: House Lords ─────────────────────────────────
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ─── STEP 3.5: Lagna Info ────────────────────────────────
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)
        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")

        # ─── STEP 4: Aspects on Houses ───────────────────────────
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )
        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ─── STEP 4.5: UNIFIED CAREER VERDICT ───────────────────
        unified_verdict = self._compute_unified_career_verdict(planets, houses)

        # Store unified verdict for ALL questions
        result.additional_data["unified_career_verdict"] = unified_verdict

        logger.info(f"🎯 UNIFIED VERDICT: {unified_verdict['primary_path']}")
        logger.info(f"   Service Score: {unified_verdict['service_score']}")
        logger.info(f"   Business Score: {unified_verdict['business_score']}")
        logger.info(f"   Confidence: {unified_verdict['confidence']}")
        logger.info(f"   KP-Vedic Agreement: {unified_verdict['agreement_status']}")

        # ─── STEP 5: Timing Windows ──────────────────────────────
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: timing_windows_raw keys: {list(timing_windows_raw.keys()) if isinstance(timing_windows_raw, dict) else 'N/A'}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            if not timing_windows_list and "Promotion Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Promotion Timing"]
                logger.info(f"🔍 DEBUG: Using 'Promotion Timing' fallback key, found {len(timing_windows_list)} windows")

            if not timing_windows_list and "Growth And Security" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Growth And Security"]
                logger.info("🔍 DEBUG: Using 'Growth And Security' fallback key")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        if timing_windows_data and timing_windows_data.get("has_timing"):
            best = timing_windows_data.get("best_window", {})
            nearest = timing_windows_data.get("nearest_window", {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            logger.info(f"❌ No timing windows available for '{sub_subdomain}'")

        # ─── STEP 5.5: Structured KP + Career Matrix ─────────────
        kp_structured = self._extract_kp_career_structured(planets, houses, unified_verdict)
        result.additional_data["kp_career_analysis"] = kp_structured

        career_matrix = self._create_career_suitability_matrix(unified_verdict, kp_structured)
        result.additional_data["career_suitability_matrix"] = career_matrix

        # ─── STEP 5.6: KP Service Profession (Role Resonance) ────
        try:
            import pprint
            logger.warning("════════════════════════════════════")
            logger.warning("🧪 RAW PLANETS DICT (FULL)")
            logger.warning("════════════════════════════════════")
            pprint.pprint(planets, width=140)
            logger.warning("════════════════════════════════════")
            logger.warning("🧪 RAW HOUSES LIST (FULL)")
            logger.warning("════════════════════════════════════")
            pprint.pprint(houses, width=140)
            logger.warning("════════════════════════════════════")

            service_kp = evaluate_service_profession(
                planets=planets,
                houses=houses,
                KP_PROFESSION_MAP=profession_map
            )

            if service_kp and isinstance(service_kp, dict):
                logger.info("✅ KP structural career data extracted (service function)")
                # Align with unified verdict
                service_kp["unified_path"] = unified_verdict["primary_path"]
                result.additional_data["career_role_resonance"] = {
                    "career_category": service_kp.get("career_category"),
                    "career_direction": service_kp.get("career_direction"),
                    "roles": service_kp.get("final_professions"),
                    "confidence": unified_verdict["confidence"],
                    "context_tags": service_kp.get("context_tags"),
                    "planet_chain": service_kp.get("planet_chain"),
                    "mode": unified_verdict["primary_path"],
                    "csl_reasoning": service_kp.get("csl_reasoning"),
                    "context_explanation": service_kp.get("context_explanation"),
                    "structural_only": True
                }

        except Exception as e:
            logger.warning(f"Could not extract service KP data: {e}")

        # Service vs Business summary (aligned with unified verdict)
        result.additional_data["career_service_vs_business"] = {
            "final_path": unified_verdict["primary_path"],
            "service_score": unified_verdict["service_score"],
            "business_score": unified_verdict["business_score"],
            "confidence": unified_verdict["confidence"],
            "agreement_status": unified_verdict["agreement_status"]
        }

        # ─── STEP 6: House Analysis Points (Promotion Timing only) ─
        if sub_subdomain in {"Promotion Timing"}:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ─── STEP 7: LLM-Only Questions ──────────────────────────
        if sub_subdomain in {"Career Risks and Advice", "Career Stability Advice"}:
            result.add_point(
                "This question is best addressed through experience-based analysis, "
                "workplace dynamics, leadership skills, and strategic decision-making "
                "rather than predictive astrology alone."
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
            if lagna_info:
                result.additional_data["lagna_info"] = lagna_info
            self._log_result_breakdown(result, sub_subdomain)
            return result

        # ─── STEP 8: Promotion Timing (KP Points) ────────────────
        if sub_subdomain == "Promotion Timing":
            # Use UNIFIED verdict
            path = unified_verdict["primary_path"]
            confidence = unified_verdict["confidence"]
            result.add_point(f"KP: Primary career path: **{path}** (Confidence: {confidence})")

            # Promise status
            promise_6 = unified_verdict.get("promise_status", {}).get(6, "UNKNOWN")
            promise_10 = unified_verdict.get("promise_status", {}).get(10, "UNKNOWN")

            if promise_6 == "PROMISE" and promise_10 == "PROMISE":
                result.add_point("KP: Strong employment promise — favorable promotion timing likely")
            elif promise_6 == "DENIAL" or promise_10 == "DENIAL":
                result.add_point(
                    "⚠️ Natal promise weak — promotions may be delayed despite good dashas."
                )
            elif promise_6 == "WEAK_PROMISE" or promise_10 == "WEAK_PROMISE":
                result.add_point(
                    "Moderate natal promise — strong dasha/transit needed for manifestation."
                )
            else:
                result.add_point(
                    "Neutral natal promise — timing results depend heavily on dasha strength."
                )

            # Agreement status
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE on career direction")
            elif agreement == "PARTIAL":
                result.add_point("⚠️ KP and Vedic show PARTIAL agreement — KP takes precedence")
            elif agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT — KP result prioritized for timing")

            # KP timing layer
            if meta and meta_query_type == QueryType.TIMING:
                try:
                    timing_rules = TIMING_RULES.get("Promotion Timing", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    positive_planets = get_positive_planets(planet_scores)

                    if positive_planets:
                        result.add_point(
                            f"KP: Favorable dasha lords for promotions, raises, or leadership roles: "
                            f"{', '.join(positive_planets[:4])}."
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.add_point(
                            f"KP: Ruling planets supporting career advancement: "
                            f"{', '.join(ruling_planets[:4])}."
                        )

                    if not positive_planets:
                        result.add_point(
                            "Growth indicators are mixed; promotions may require sustained effort "
                            "and favorable future dashas."
                        )

                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")
                    result.add_point(
                        "Career growth timing indicators could not be conclusively determined."
                    )

        # ─── STEP 9: Remedies ────────────────────────────────────
        elif sub_subdomain == "Career Remedies":
            result.add_point(
                "Career remedies are based on strengthening professional houses, "
                "key career planets, and reducing stagnation influences."
            )

        # ─── STEP 10: Fallback ───────────────────────────────────
        else:
            result.add_point(
                "Career growth indicators exist, but this query is handled outside "
                "strict astrological evaluation."
            )

        # ─── STEP 11: Store Data for LLM ─────────────────────────
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data
        )

        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # Carry over any legacy self.points
        if hasattr(self, "points") and self.points:
            for point in self.points:
                result.add_point(point)

        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ═══════════════════════════════════════════════════════════════

    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow objects.
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
                    "start": get_attr(w, "start"),
                    "end": get_attr(w, "end"),
                    "dasha": get_attr(w, "dasha"),
                    "score": get_attr(w, "score"),
                    "transit_score": get_attr(w, "transit_score"),
                    "final_score": get_attr(w, "final_score"),
                    "age_at_start": get_attr(w, "age_at_start"),
                    "is_overall_best": get_attr(w, "is_overall_best", False),
                    "is_earliest_favorable": get_attr(w, "is_earliest_favorable", False),
                }
                for extra_field in [
                    "score_maha", "score_antara", "score_paryantar",
                    "md", "ad", "pd", "maha", "antara", "paryantar",
                    "_domain_score", "_delay_years", "_needs_resonant_jump"
                ]:
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

            from datetime import datetime

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

            timing_result = {
                "best_window": best_window,
                "nearest_window": nearest_window,
                "all_favorable": all_favorable,
                "has_timing": True
            }

            logger.info("✅ Timing extraction SUCCESSFUL:")
            if best_window:
                logger.info(f"   Best: {best_window.get('dasha', 'N/A')} - Score: {best_window.get('final_score', 0)}")
            if nearest_window:
                logger.info(f"   Nearest: {nearest_window.get('dasha', 'N/A')} - Score: {nearest_window.get('final_score', 0)}")

            return timing_result

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
        primary_houses: set
    ) -> dict:
        """Extract house lord information for relevant houses only."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue

            lord_name = self._get_house_lord(h)

            if not lord_name:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                logger.warning(f"⚠️ No lord found for house {house_num} (sign: {sign})")
                continue

            normalized_lord = lord_name  # _get_house_lord already normalizes
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

            lord_dignity = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity = None
                    if hasattr(analyzer, "get_planet_dignity"):
                        dignity = analyzer.get_planet_dignity(normalized_lord)
                    elif hasattr(analyzer, "get_dignity"):
                        dignity = analyzer.get_dignity(normalized_lord)
                    elif hasattr(analyzer, "analyze_dignity"):
                        dignity = analyzer.analyze_dignity(normalized_lord)

                    if dignity:
                        lord_dignity = dignity.value if hasattr(dignity, "value") else str(dignity)
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity
                        )
                    else:
                        logger.debug(f"Could not determine dignity for {normalized_lord}")
                except Exception as e:
                    logger.warning(f"Could not analyze lord dignity for {normalized_lord}: {e}")
            else:
                # Fallback: use _get_planet_dignity directly
                lord_dignity = self._get_planet_dignity(normalized_lord, lord_data)
                lord_strength_score = self._calculate_lord_strength(normalized_lord, lord_data, lord_dignity)

            priority = "primary" if house_num in primary_houses else "secondary"

            planets_in_house = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]

            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""

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
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            if not house_1:
                logger.warning("⚠️ House 1 not found — cannot determine lagna")
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

            lagna_lord = self._get_house_lord(house_1)
            if not lagna_lord:
                logger.warning(f"⚠️ Could not determine lagna lord for {lagna_sign}")
                return None

            lagna_lord_data = planets.get(lagna_lord, {})
            lagna_lord_dignity = self._get_planet_dignity(lagna_lord, lagna_lord_data)

            # Try HouseLordsAnalyzer for more precise dignity if available
            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity = None
                    if hasattr(analyzer, "get_planet_dignity"):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, "get_dignity"):
                        dignity = analyzer.get_dignity(lagna_lord)
                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, "value") else str(dignity)
                except Exception:
                    pass

            return {
                "lagna_sign": lagna_sign,
                "lagna_lord": lagna_lord,
                "lagna_lord_house": lagna_lord_data.get("house"),
                "lagna_lord_sign": lagna_lord_data.get("sign", ""),
                "lagna_lord_degree": (
                    lagna_lord_data.get("full_degree") or
                    lagna_lord_data.get("global_degree") or
                    lagna_lord_data.get("degree") or
                    0
                ),
                "lagna_lord_dignity": lagna_lord_dignity,
            }

        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

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
        dignity=None
    ) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, "value") else str(dignity).upper()
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

            point_parts = [
                f"⭐ House {house_num} ({self.HOUSE_MEANINGS.get(house_num, 'General')}):",
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
        domain_prefix = "career"

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

        if timing_windows_data and timing_windows_data.get("has_timing"):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info("✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {domain_prefix}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
            if timing_windows_data.get("best_window"):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE (data: {bool(timing_windows_data)})")

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")

        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")

        if "unified_career_verdict" in ad:
            verdict = ad["unified_career_verdict"]
            logger.info(f"UNIFIED VERDICT: {verdict.get('primary_path')}")
            logger.info(f"  Agreement: {verdict.get('agreement_status')}")

    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ═══════════════════════════════════════════════════════════════

    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="CAR_GS_1",
                question=(
                    "What does astrology reveal about my prospects for promotions, raises, "
                    "transfers, leadership roles, and overall success in corporate or political spheres?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Promotion Timing"
            ),
            Question(
                id="CAR_GS_2",
                question=(
                    "Are there risks of career stagnation, lack of recognition, workplace politics, "
                    "or instability, and what obstacles might I face?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Career Risks and Advice"
            ),
            Question(
                id="CAR_GS_3",
                question=(
                    "How can I overcome challenges and achieve greater stability and success in my career?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.SUPPORT
                ),
                sub_subdomain="Career Stability Advice"
            )
        ]
"""
Starting New Business Evaluator - ENHANCED VERSION v5.0

CRITICAL FIXES FROM v4.0 (Aligned with CareerDiscoveryAndEmploymentEvaluator v5.0):
✅ UNIFIED BUSINESS VERDICT LAYER - Single source of truth for Business/Hybrid/Service
✅ PURE KP METHODOLOGY - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ CORRECT HOUSE MAPPING - Business: 2,3,7,11 | Service: 2,6,10,11
✅ SUB-LORD PROMISE/DENIAL LOGIC - Core KP rule implemented (same as career evaluator)
✅ RAHU/KETU PROPER HANDLING - Star lord + sign lord + conjunctions, recursion-safe
✅ CONSISTENT OUTPUT ACROSS ALL QUESTIONS - Same base verdict used everywhere
✅ STRENGTH HIERARCHY - Sub > Star > Occupy > Own (mirrors career evaluator)
✅ PLANET SIGNIFICATIONS - Full get_planet_significations() with loop protection

Architecture (mirrors CareerDiscoveryAndEmploymentEvaluator v5.0):
- _compute_unified_business_verdict() → Single source of truth
- _apply_pure_kp_chain() → Strict KP methodology
- _evaluate_sub_lord_promise() → Promise/denial logic
- _get_planet_significations() → Recursive-safe signification resolution
- _get_planet_owned_houses() → House ownership lookup
"""

from typing import Dict, List, Optional, Set, Tuple
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

# ---- KP CORE ENGINE (NO MODIFICATION) ----
from app.domains.career.kp_career_engine import (
    evaluate_business_profession,
    evaluate_foreign_career_exposure
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


class StartingNewBusinessEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Business → Starting New Business
    v5.0 - With unified business verdict layer and pure KP methodology.
    Architecture mirrors CareerDiscoveryAndEmploymentEvaluator v5.0.
    """

    domain = "Business"
    subtopic = "Starting New Business"

    # ═══════════════════════════════════════════════════════════════
    # CORRECTED HOUSE DEFINITIONS (KP Standard)
    # ═══════════════════════════════════════════════════════════════

    # Business houses (KP standard)
    BUSINESS_HOUSES = {2, 3, 7, 11}   # Income, initiative/trade, partnership, gains

    # Service/employment houses
    SERVICE_HOUSES = {2, 6, 10, 11}   # Income, service, profession, gains

    # Supporting
    WEALTH_HOUSES = {2, 10, 11}
    LOSS_HOUSES = {6, 8, 12}
    FOREIGN_HOUSES = {3, 9, 12}

    # House meanings
    HOUSE_MEANINGS = {
        1:  "Self/Personality",
        2:  "Wealth/Capital",
        3:  "Initiative/Courage/Trade",
        5:  "Speculation/Creativity",
        6:  "Competition/Service/Loans",
        7:  "Business/Partnerships",
        8:  "Hidden Wealth/Obstacles",
        9:  "Fortune/Luck/Long-distance",
        10: "Career/Profession/Status",
        11: "Gains/Profits/Fulfillment",
        12: "Losses/Foreign/Expenses"
    }

    # KP Strength Hierarchy
    KP_WEIGHT = {
        "sub_lord": 4,
        "star_lord": 3,
        "occupy":    2,
        "own":       1
    }

    # Sign-lord map (reused across helpers)
    SIGN_LORDS = {
        "Aries": "Mars",   "Taurus": "Venus",   "Gemini": "Mercury",
        "Cancer": "Moon",  "Leo": "Sun",         "Virgo": "Mercury",
        "Libra": "Venus",  "Scorpio": "Mars",    "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }

    # ═══════════════════════════════════════════════════════════════
    # UNIFIED BUSINESS VERDICT (Single Source of Truth)
    # ═══════════════════════════════════════════════════════════════

    def _compute_unified_business_verdict(
        self,
        planets: Dict,
        houses: List
    ) -> Dict:
        """
        SINGLE SOURCE OF TRUTH for business path determination.
        Mirrors _compute_unified_career_verdict() from CareerDiscoveryAndEmploymentEvaluator v5.0
        but focuses on:
          - 7th cusp  → Business/Partnership promise
          - 10th cusp → Career/Profession direction
          - 6th cusp  → Service leaning (used as contrast)

        Returns:
            {
                "primary_path": "Business" | "Service" | "Hybrid",
                "secondary_path": str | None,
                "business_score": int,
                "service_score": int,
                "confidence": "High" | "Moderate" | "Low",
                "kp_reasoning": str,
                "vedic_reasoning": str,
                "agreement_status": "AGREEMENT" | "PARTIAL" | "CONFLICT",
                "promise_status": {house: "PROMISE"|"DENIAL"|"WEAK_PROMISE"|"NEUTRAL"},
                "detailed_analysis": {house: chain_result},
                "career_ranking": [...]
            }
        """
        result = {
            "primary_path": "Unknown",
            "secondary_path": None,
            "business_score": 0,
            "service_score": 0,
            "confidence": "Low",
            "kp_reasoning": "",
            "vedic_reasoning": "",
            "agreement_status": "UNKNOWN",
            "promise_status": {},
            "detailed_analysis": {},
            "career_ranking": []
        }

        # ─────────────────────────────────────────────────────────
        # STEP 1: Pure KP Analysis on key cusps
        # ─────────────────────────────────────────────────────────
        kp_business_score = 0
        kp_service_score  = 0
        kp_reasons        = []
        promise_status    = {}

        key_cusps = {
            2:  "Wealth/Capital",
            6:  "Service/Employment",
            7:  "Business/Partnership",
            10: "Career/Profession",
            11: "Gains/Profits",
            12: "Foreign/Expenses"
        }

        for cusp_num, meaning in key_cusps.items():
            cusp_data = next((h for h in houses if h.get("house") == cusp_num), None)
            if not cusp_data:
                continue

            chain_result = self._apply_pure_kp_chain(cusp_data, planets, houses)
            if not chain_result:
                continue

            promise_status[cusp_num] = chain_result.get("promise_status", "UNKNOWN")
            result["detailed_analysis"][cusp_num] = chain_result

            sub_lord_houses  = set(chain_result.get("sub_lord_signifies", []))
            star_lord_houses = set(chain_result.get("star_lord_signifies", []))
            csl_house        = chain_result.get("csl_house")

            business_conn = 0
            service_conn  = 0

            # Sub-lord (weight 4)
            business_conn += len(sub_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["sub_lord"]
            service_conn  += len(sub_lord_houses & self.SERVICE_HOUSES)  * self.KP_WEIGHT["sub_lord"]

            # Star-lord (weight 3)
            business_conn += len(star_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["star_lord"]
            service_conn  += len(star_lord_houses & self.SERVICE_HOUSES)  * self.KP_WEIGHT["star_lord"]

            # CSL occupation (weight 2)
            if csl_house in self.BUSINESS_HOUSES:
                business_conn += self.KP_WEIGHT["occupy"]
            if csl_house in self.SERVICE_HOUSES:
                service_conn  += self.KP_WEIGHT["occupy"]

            if cusp_num == 7:
                kp_business_score += business_conn
                if chain_result.get("promise_status") == "PROMISE":
                    kp_reasons.append(
                        f"7th CSL promises business (sub-lord signifies "
                        f"{sorted(sub_lord_houses & self.BUSINESS_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append("7th CSL denies business (sub-lord in loss houses)")

            elif cusp_num == 6:
                kp_service_score += service_conn
                if chain_result.get("promise_status") == "PROMISE":
                    kp_reasons.append(
                        f"6th CSL promises employment (sub-lord signifies "
                        f"{sorted(sub_lord_houses & self.SERVICE_HOUSES)})"
                    )
                elif chain_result.get("promise_status") == "DENIAL":
                    kp_reasons.append("6th CSL denies employment (sub-lord in loss houses)")

            elif cusp_num == 10:
                kp_reasons.append("10th CSL influences career strength")

        result["promise_status"] = promise_status
        result["business_score"] = kp_business_score
        result["service_score"]  = kp_service_score

        # ─────────────────────────────────────────────────────────
        # STEP 2: Vedic Analysis (Secondary - 30% weight)
        # ─────────────────────────────────────────────────────────
        vedic_business_score = 0
        vedic_service_score  = 0
        vedic_reasons        = []

        for house_num in [6, 7, 10]:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            lord_name = self._get_house_lord(house_data)
            if not lord_name:
                continue

            lord_data  = planets.get(lord_name, {})
            lord_house = lord_data.get("house")

            if house_num == 7:
                if lord_house in self.BUSINESS_HOUSES:
                    vedic_business_score += 3
                    vedic_reasons.append(
                        f"7th lord {lord_name} in house {lord_house} → business potential"
                    )
                elif lord_house in self.LOSS_HOUSES:
                    vedic_business_score -= 2
                    vedic_reasons.append(
                        f"7th lord {lord_name} in loss house → business obstacles"
                    )

            elif house_num == 6:
                if lord_house in self.SERVICE_HOUSES:
                    vedic_service_score += 3
                    vedic_reasons.append(
                        f"6th lord {lord_name} in house {lord_house} → service inclination"
                    )

            elif house_num == 10:
                dignity = self._get_planet_dignity(lord_name, lord_data)
                if dignity in ["EXALTED", "OWN_SIGN"]:
                    vedic_business_score += 1
                    vedic_service_score  += 1
                    vedic_reasons.append(
                        f"10th lord {lord_name} is {dignity} → strong career foundation"
                    )

        # ─────────────────────────────────────────────────────────
        # STEP 3: Pure KP Verdict (Sub-lord dominant)
        # ─────────────────────────────────────────────────────────
        h7  = promise_status.get(7,  "NEUTRAL")
        h6  = promise_status.get(6,  "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")

        if h7 == "PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"
        elif h6 == "PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"
        elif h7 == "PROMISE" and h6 == "PROMISE":
            primary = "Hybrid"
        elif h7 == "WEAK_PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"
        elif h6 == "WEAK_PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"
        elif h7 == "DENIAL" and h6 == "DENIAL":
            primary = "Hybrid"

        else:
            # Tie-breaker using 10th cusp sub-lord leaning (align with Career evaluator)
            h10_data = result["detailed_analysis"].get(10, {})
            sub_houses = set(h10_data.get("sub_lord_signifies", []))

            service_lean = sub_houses & self.SERVICE_HOUSES
            business_lean = sub_houses & self.BUSINESS_HOUSES

            if service_lean and not business_lean:
                primary = "Service"
            elif business_lean and not service_lean:
                primary = "Business"
            else:
                primary = "Hybrid"

        result["primary_path"] = primary

        # ─────────────────────────────────────────────────────────
        # STEP 4: Confidence from 10th cusp
        # ─────────────────────────────────────────────────────────
        h10_data = result["detailed_analysis"].get(10, {})
        sub_houses_10 = set(h10_data.get("sub_lord_signifies", []))

        positive_conn = sub_houses_10 & (self.SERVICE_HOUSES | self.BUSINESS_HOUSES)
        loss_conn = sub_houses_10 & {8, 12}

        if h10 == "PROMISE" and positive_conn and not loss_conn:
            confidence = "High"
        elif h10 == "PROMISE":
            confidence = "Moderate"
        elif h10 == "WEAK_PROMISE":
            confidence = "Moderate"
        elif h10 == "DENIAL":
            confidence = "Low"
        else:
            confidence = "Moderate"

        result["confidence"] = confidence

        # ─────────────────────────────────────────────────────────
        # STEP 5: KP-Vedic agreement
        # ─────────────────────────────────────────────────────────
        if vedic_business_score > vedic_service_score:
            vedic_verdict = "Business"
        elif vedic_service_score > vedic_business_score:
            vedic_verdict = "Service"
        else:
            vedic_verdict = "Neutral"

        if vedic_verdict == "Neutral":
            result["agreement_status"] = "PARTIAL"
        elif primary == vedic_verdict:
            result["agreement_status"] = "AGREEMENT"
        elif primary == "Hybrid":
            result["agreement_status"] = "PARTIAL"
        else:
            result["agreement_status"] = "CONFLICT"

        # ─────────────────────────────────────────────────────────
        # STEP 6: Business path ranking
        # ─────────────────────────────────────────────────────────
        ranking = []

        # Solo business
        solo_score = 3 if h7 == "PROMISE" else (1 if h7 == "WEAK_PROMISE" else 0)
        ranking.append(("Solo Business / Proprietorship", solo_score))

        # Partnership
        partner_score = 2 if h7 == "PROMISE" else 0
        if self._has_planet_connection(["Venus", "Jupiter", "Mercury"], planets, houses, {7}):
            partner_score += 2
        ranking.append(("Partnership Business", partner_score))

        # Service/Employment
        svc_score = 3 if h6 == "PROMISE" else (1 if h6 == "WEAK_PROMISE" else 0)
        ranking.append(("Service / Employment", svc_score))

        # Tech/IT
        tech_score = 3 if self._has_planet_connection(
            ["Rahu", "Saturn", "Mercury"], planets, houses, {3, 7, 10}
        ) else 0
        ranking.append(("Technology / IT Business", tech_score))

        # Foreign/Trade
        foreign_score = 3 if self._has_planet_connection(
            ["Rahu"], planets, houses, {9, 12}
        ) else 0
        ranking.append(("Export / Import / Foreign Trade", foreign_score))

        ranking.sort(key=lambda x: x[1], reverse=True)
        result["career_ranking"] = [
            {"path": p, "score": s, "rating": self._score_to_rating(s)}
            for p, s in ranking
        ]

        result["kp_reasoning"]   = " | ".join(kp_reasons)   if kp_reasons   else "KP analysis incomplete"
        result["vedic_reasoning"] = " | ".join(vedic_reasons) if vedic_reasons else "Vedic analysis incomplete"

        return result

    # ═══════════════════════════════════════════════════════════════
    # PURE KP CHAIN APPLICATION
    # ═══════════════════════════════════════════════════════════════

    def _apply_pure_kp_chain(
        self,
        cusp_data: Dict,
        planets: Dict,
        houses: List
    ) -> Dict:
        """
        Pure KP methodology: CSL → Sub Lord → Star Lord → Significations → Promise/Denial.
        Mirrors career evaluator implementation exactly.
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
        }

        csl = normalize_planet_name(cusp_data.get("cusp_sub_lord", ""))
        if not csl:
            return result

        result["csl"]          = csl
        csl_data               = planets.get(csl, {})
        result["csl_house"]    = csl_data.get("house")
        result["csl_nakshatra"] = csl_data.get("nakshatra", "")

        # Star lord
        star_lord = normalize_planet_name(csl_data.get("nakshatra_lord", ""))
        result["star_lord"] = star_lord
        if star_lord:
            result["star_lord_signifies"] = sorted(
                self._get_planet_significations(star_lord, planets, houses)
            )

        # Sub lord of CSL
        sub_lord = normalize_planet_name(csl_data.get("sub_lord", ""))
        result["sub_lord"] = sub_lord
        if sub_lord:
            result["sub_lord_signifies"] = sorted(
                self._get_planet_significations(sub_lord, planets, houses)
            )
            result["promise_status"] = self._evaluate_sub_lord_promise(
                cusp_data.get("house", 0),
                result["sub_lord_signifies"],
                result["star_lord_signifies"]
            )

        # Chain text
        parts = [f"CSL: {csl}"]
        if star_lord:
            parts.append(f"Star: {star_lord} → {result['star_lord_signifies']}")
        if sub_lord:
            parts.append(f"Sub: {sub_lord} → {result['sub_lord_signifies']}")
        parts.append(f"Promise: {result['promise_status']}")
        result["chain_text"] = " | ".join(parts)

        return result

    # ═══════════════════════════════════════════════════════════════
    # PROMISE / DENIAL LOGIC
    # ═══════════════════════════════════════════════════════════════

    def _evaluate_sub_lord_promise(
        self,
        cusp_house: int,
        sub_lord_houses: List[int],
        star_lord_houses: List[int]
    ) -> str:
        """
        KP Promise/Denial based on sub-lord house significations.
        Mirrors career evaluator implementation exactly.

        Business (7th): Promise if sub-lord signifies 2, 3, 7, 11
        Service  (6th): Promise if sub-lord signifies 2, 6, 10, 11
        Career  (10th): Promise if sub-lord signifies 2, 6, 10, 11
        """
        sub_set = set(sub_lord_houses)
        loss    = {8, 12}

        if cusp_house == 7:  # Business
            positive = {2, 3, 7, 11}
            service_house = {6}
            loss = {8, 12}

            positive_conn = sub_set & positive
            loss_conn = sub_set & loss
            service_conn = sub_set & service_house

            # Strong business promise
            if positive_conn and not loss_conn and not service_conn:
                return "PROMISE"

            # Strong denial (loss houses dominant)
            if loss_conn and not positive_conn:
                return "DENIAL"

            # 6th dominance weakens independent business
            if service_conn and not positive_conn:
                return "DENIAL"

            # Mixed case
            if positive_conn:
                return "WEAK_PROMISE"

            return "NEUTRAL"

        elif cusp_house == 6:
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & loss:
                return "PROMISE"
            elif sub_set & loss and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        elif cusp_house == 10:
            positive = {2, 6, 10, 11}
            if sub_set & positive and not sub_set & loss:
                return "PROMISE"
            elif sub_set & loss and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            return "NEUTRAL"

        return "NEUTRAL"

    # ═══════════════════════════════════════════════════════════════
    # PLANET SIGNIFICATIONS (Recursion-safe, mirrors career evaluator)
    # ═══════════════════════════════════════════════════════════════

    def _get_planet_significations(
        self,
        planet_name: str,
        planets: Dict,
        houses: List,
        visited: Optional[Set[str]] = None
    ) -> List[int]:
        """
        Get houses signified by a planet using KP hierarchy.
        Recursion-safe (tracks visited planets).
        Mirrors career evaluator _get_planet_significations() exactly.
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

        # Special handling for Rahu / Ketu
        if planet_name in ["Rahu", "Ketu"]:
            # 1) Star lord
            star_lord = normalize_planet_name(planet_data.get("nakshatra_lord"))
            if star_lord and star_lord != planet_name:
                signified.update(
                    self._get_planet_significations(star_lord, planets, houses, visited)
                )
            # 2) Sign lord
            sign_lord = self.SIGN_LORDS.get(planet_data.get("sign", ""))
            if sign_lord:
                signified.update(
                    self._get_planet_significations(sign_lord, planets, houses, visited)
                )
            # 3) Conjunct planets (same house)
            for p_name, p_data in planets.items():
                if p_name == planet_name:
                    continue
                if p_data.get("house") == planet_data.get("house"):
                    signified.update(
                        self._get_planet_significations(p_name, planets, houses, visited)
                    )

        # 1) Occupied house
        occ = planet_data.get("house")
        if occ:
            signified.add(occ)

        # 2) Owned houses
        signified.update(self._get_owned_houses(planet_name, houses))

        # 3) Planets in this planet's star
        for p_name, p_data in planets.items():
            if p_name == planet_name:
                continue
            if normalize_planet_name(p_data.get("nakshatra_lord")) == planet_name:
                ph = p_data.get("house")
                if ph:
                    signified.add(ph)
                signified.update(self._get_owned_houses(p_name, houses))

        return sorted(signified)

    def _get_owned_houses(self, planet_name: str, houses: List) -> List[int]:
        """Return house numbers whose sign is owned by planet_name."""
        return [
            h.get("house")
            for h in houses
            if self.SIGN_LORDS.get(
                h.get("sign") or h.get("start_rasi") or h.get("rasi", "")
            ) == planet_name
        ]

    # ═══════════════════════════════════════════════════════════════
    # KP STRUCTURED EXTRACTION (Business houses)
    # ═══════════════════════════════════════════════════════════════

    def _extract_kp_business_structured(
        self,
        planets: Dict,
        houses: List,
        unified_verdict: Dict
    ) -> Dict:
        """
        Extract structured KP business data using pure methodology.
        Uses unified_verdict for consistency — mirrors career evaluator pattern.
        """
        kp_data = {
            "csl_details":    {},
            "overall_verdict": unified_verdict.get("primary_path", "UNKNOWN"),
            "key_findings":   [],
            "has_kp_data":    False,
            "methodology":    "CSL → Sub Lord → Star Lord → Significations → Promise/Denial"
        }

        business_houses = [2, 3, 6, 7, 9, 10, 11]
        house_meanings = {
            2:  "Wealth/Capital",
            3:  "Initiative/Trade",
            6:  "Competition/Loans",
            7:  "Business/Partnerships",
            9:  "Fortune/Luck",
            10: "Career/Profession",
            11: "Gains/Profits"
        }

        for house_num in business_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue

            chain_result = self._apply_pure_kp_chain(house_data, planets, houses)
            if not chain_result.get("csl"):
                continue

            kp_data["has_kp_data"] = True

            csl      = chain_result["csl"]
            csl_data = planets.get(csl, {})
            promise  = chain_result.get("promise_status", "NEUTRAL")

            # Map promise → verdict label
            verdict_map = {
                "PROMISE":      "STRONG",
                "WEAK_PROMISE": "MODERATE",
                "DENIAL":       "WEAK",
                "NEUTRAL":      "NEUTRAL",
                "UNKNOWN":      "NEUTRAL"
            }
            verdict = verdict_map.get(promise, "NEUTRAL")

            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            flavor   = (
                "benefic flavor" if csl in benefics else
                "malefic flavor" if csl in malefics else
                "neutral flavor"
            )

            interpretation = self._build_kp_business_interpretation(
                house_num, chain_result, unified_verdict
            )

            kp_data["csl_details"][house_num] = {
                "house_meaning":       house_meanings.get(house_num, "General"),
                "csl":                 csl,
                "csl_house":           chain_result.get("csl_house"),
                "csl_flavor":          flavor,
                "nakshatra":           chain_result.get("csl_nakshatra", ""),
                "star_lord":           chain_result.get("star_lord"),
                "star_lord_signifies": chain_result.get("star_lord_signifies", []),
                "sub_lord":            chain_result.get("sub_lord"),
                "sub_lord_signifies":  chain_result.get("sub_lord_signifies", []),
                "promise_status":      promise,
                "verdict":             verdict,
                "interpretation":      interpretation,
                "chain":               chain_result.get("chain_text", ""),
                "has_significations":  bool(chain_result.get("sub_lord_signifies"))
            }

            kp_data["key_findings"].append(
                f"House {house_num}: {csl} → Sub {chain_result.get('sub_lord')} → "
                f"signifies {chain_result.get('sub_lord_signifies', [])} → {promise}"
            )

        kp_data["overall_verdict"]   = unified_verdict.get("primary_path", "UNKNOWN")
        kp_data["agreement_status"]  = unified_verdict.get("agreement_status", "UNKNOWN")

        return kp_data

    def _build_kp_business_interpretation(
        self,
        house_num: int,
        chain_result: Dict,
        unified_verdict: Dict
    ) -> str:
        """Build human-readable KP interpretation for business houses."""
        csl       = chain_result.get("csl", "Unknown")
        sub_lord  = chain_result.get("sub_lord", "Unknown")
        sub_houses = chain_result.get("sub_lord_signifies", [])
        promise   = chain_result.get("promise_status", "NEUTRAL")
        path      = unified_verdict.get("primary_path", "Unknown")

        templates = {
            7: {
                "PROMISE":      (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Strong business house connection → Partnership/trade PROMISED."
                ),
                "DENIAL":       (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Business NOT favored. Service path safer."
                ),
                "WEAK_PROMISE": (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate business potential — needs strong dasha."
                ),
            },
            10: {
                "PROMISE":      (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Career houses activated → Professional success PROMISED. Path: {path}."
                ),
                "DENIAL":       (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss houses dominate → Career challenges indicated."
                ),
                "WEAK_PROMISE": (
                    f"10th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Moderate career indicators."
                ),
            },
            6: {
                "PROMISE":      (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Service house strong → Employment / service path PROMISED."
                ),
                "DENIAL":       (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Service path faces obstacles → Business may be better."
                ),
                "WEAK_PROMISE": (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Mixed service indicators."
                ),
            }
        }

        house_tpl = templates.get(house_num, {})
        if promise in house_tpl:
            return house_tpl[promise]

        return (
            f"House {house_num}: CSL {csl} → Sub {sub_lord} → "
            f"Signifies {sub_houses} → {promise}"
        )

    # ═══════════════════════════════════════════════════════════════
    # BUSINESS SUITABILITY MATRIX (Uses unified verdict)
    # ═══════════════════════════════════════════════════════════════

    def _create_business_suitability_matrix(
        self,
        unified_verdict: Dict,
        kp_analysis: Dict,
        business_eval: Dict = None
    ) -> Dict[str, Dict]:
        """
        Create business suitability matrix using UNIFIED verdict for consistency.
        Mirrors career evaluator's _create_career_suitability_matrix().
        """
        matrix   = {}
        promise  = unified_verdict.get("promise_status", {})
        path     = unified_verdict.get("primary_path", "Unknown")
        details  = kp_analysis.get("csl_details", {})

        h7_csl       = details.get(7, {}).get("csl")
        h7_star      = details.get(7, {}).get("star_lord")
        h10_csl      = details.get(10, {}).get("csl")
        partners_needed = business_eval.get("partners_needed", False) if business_eval else False
        foreign_link    = business_eval.get("foreign_link", "No") if business_eval else "No"

        # ── Solo Business ──────────────────────────────────────────
        h7_promise = promise.get(7, "NEUTRAL")
        if h7_promise == "PROMISE" and not partners_needed:
            solo_rating  = "HIGH"
            solo_reason  = "7th CSL promises business; solo indicators present"
        elif h7_promise == "WEAK_PROMISE":
            solo_rating  = "MODERATE"
            solo_reason  = "7th CSL weakly promises business; dasha support needed"
        else:
            solo_rating  = "LOW"
            solo_reason  = "Partnership or service path may be more suitable"
        matrix["Solo Business / Proprietorship"] = {"rating": solo_rating, "kp_reasoning": solo_reason}

        # ── Partnership Business ───────────────────────────────────
        if partners_needed and h7_promise in ["PROMISE", "WEAK_PROMISE"]:
            p_rating  = "HIGH"
            p_reason  = "Chart indicates partnership benefit and 7th CSL active"
        elif h7_csl in {"Venus", "Jupiter", "Mercury"}:
            p_rating  = "MODERATE"
            p_reason  = f"7th CSL {h7_csl} supports harmonious partnerships"
        else:
            p_rating  = "LOW"
            p_reason  = "Solo business or service may be more suitable"
        matrix["Partnership Business"] = {"rating": p_rating, "kp_reasoning": p_reason}

        # ── Trading / Commerce ─────────────────────────────────────
        trade_planets = {"Mercury", "Venus", "Jupiter"}
        if h7_csl in trade_planets or h7_star in trade_planets:
            matrix["Trading / Commerce"] = {
                "rating": "HIGH",
                "kp_reasoning": f"Trade planet {h7_csl or h7_star} influences 7th house"
            }
        else:
            matrix["Trading / Commerce"] = {
                "rating": "MODERATE",
                "kp_reasoning": "Moderate trading indicators — structured approach required"
            }

        # ── Service-Based Business ─────────────────────────────────
        h6_promise = promise.get(6, "NEUTRAL")
        if h6_promise == "PROMISE":
            matrix["Service-Based Business"] = {
                "rating": "HIGH",
                "kp_reasoning": "6th CSL promises service — consulting / contract work suitable"
            }
        elif path == "Hybrid":
            matrix["Service-Based Business"] = {
                "rating": "MODERATE",
                "kp_reasoning": "Hybrid path supports service entrepreneurship"
            }
        else:
            matrix["Service-Based Business"] = {
                "rating": "LOW",
                "kp_reasoning": "Pure trading/production business may be better"
            }

        # ── Technology / IT ────────────────────────────────────────
        rahu_connected = any(
            d.get("csl") == "Rahu" or d.get("star_lord") == "Rahu"
            for d in details.values()
        )
        if rahu_connected and h7_promise in ["PROMISE", "WEAK_PROMISE"]:
            matrix["Technology / IT Business"] = {
                "rating": "HIGH",
                "kp_reasoning": "Rahu connection + 7th promise → tech/IT ventures favored"
            }
        elif rahu_connected:
            matrix["Technology / IT Business"] = {
                "rating": "MODERATE",
                "kp_reasoning": "Rahu shows tech affinity; 7th needs stronger promise"
            }
        else:
            matrix["Technology / IT Business"] = {
                "rating": "LOW",
                "kp_reasoning": "No Rahu/tech connection detected"
            }

        # ── Export / Import / Foreign Trade ───────────────────────
        foreign_promise = promise.get(12, "NEUTRAL")
        h7_promise = promise.get(7, "NEUTRAL")

        if foreign_promise == "PROMISE" and h7_promise in ["PROMISE", "WEAK_PROMISE"]:
            rating = "HIGH"
            reason = "12th + 7th promise indicates foreign trade business potential"
        elif rahu_connected:
            rating = "MODERATE"
            reason = "Rahu connection suggests possible foreign exposure"
        else:
            rating = "LOW"
            reason = "No strong 12th/foreign business linkage"

        matrix["Export / Import / Foreign Trade"] = {
            "rating": rating,
            "kp_reasoning": reason
        }

        # ── Manufacturing / Production ─────────────────────────────
        if h10_csl in {"Saturn", "Mars"} or h7_csl in {"Saturn", "Mars"}:
            matrix["Manufacturing / Production"] = {
                "rating": "HIGH",
                "kp_reasoning": "Saturn/Mars influence supports manufacturing"
            }
        else:
            matrix["Manufacturing / Production"] = {
                "rating": "LOW",
                "kp_reasoning": "Trading or consulting may be more suitable"
            }

        # ── Consulting / Advisory ──────────────────────────────────
        if h7_csl in {"Jupiter", "Mercury"} or h10_csl in {"Jupiter", "Mercury"}:
            matrix["Consulting / Advisory"] = {
                "rating": "HIGH",
                "kp_reasoning": "Jupiter/Mercury influence supports advisory roles"
            }
        else:
            matrix["Consulting / Advisory"] = {
                "rating": "LOW",
                "kp_reasoning": "Product-based business may be more suitable"
            }

        ordered_keys = [
            "Solo Business / Proprietorship",
            "Partnership Business",
            "Trading / Commerce",
            "Service-Based Business",
            "Technology / IT Business",
            "Export / Import / Foreign Trade",
            "Manufacturing / Production",
            "Consulting / Advisory",
        ]

        matrix = {k: matrix[k] for k in ordered_keys if k in matrix}
        return matrix

    # ═══════════════════════════════════════════════════════════════
    # MAIN EVALUATION
    # ═══════════════════════════════════════════════════════════════

    def evaluate(
        self,
        planets:       Dict[str, Dict],
        houses:        List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses:  Optional[List[Dict]]      = None,
        **kwargs
    ) -> EvaluationResult:

        self.reset()
        result = EvaluationResult()

        # Choose data source for Vedic analysis
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses  = vedic_houses  if vedic_houses  else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

        # Question-specific houses
        question_text = kwargs.get("question", "")
        house_config  = get_houses_for_question(self.domain, self.subtopic, question_text)

        if house_config:
            primary_houses   = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant     = primary_houses | secondary_houses | {1}
        else:
            all_relevant     = {1, 2, 3, 6, 7, 9, 10, 11}
            primary_houses   = {7, 10, 11}
            secondary_houses = {1, 2, 3, 6, 9}

        meta           = kwargs.get("meta")
        sub_subdomain  = kwargs.get("sub_subdomain", "Starting New Business")

        meta_query_type = None
        if meta:
            meta_query_type = (
                meta.get("type") if isinstance(meta, dict)
                else getattr(meta, "query_type", None)
            )
        if hasattr(meta_query_type, "name"):
            meta_query_type = meta_query_type.name
        if isinstance(meta_query_type, str):
            meta_query_type = meta_query_type.upper()

        logger.info("=" * 80)
        logger.info("STARTING NEW BUSINESS EVALUATOR v5.0 - UNIFIED VERDICT LAYER")
        logger.info("=" * 80)

        # Aspects
        detect_aspects(analysis_planets)
        detect_aspects(planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # House lords / lagna / aspects
        house_lords_info  = self._extract_house_lords(
            analysis_houses, analysis_planets, all_relevant, primary_houses
        )
        lagna_info        = self._extract_lagna_info(analysis_houses, analysis_planets)
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses, analysis_planets, aspects_data, all_relevant
        )

        # ─────────────────────────────────────────────────────────
        # CRITICAL: Compute UNIFIED BUSINESS VERDICT
        # ─────────────────────────────────────────────────────────
        unified_verdict = self._compute_unified_business_verdict(planets, houses)
        result.additional_data["unified_business_verdict"] = unified_verdict

        logger.info(f"🎯 UNIFIED VERDICT: {unified_verdict['primary_path']}")
        logger.info(f"   Business Score : {unified_verdict['business_score']}")
        logger.info(f"   Service Score  : {unified_verdict['service_score']}")
        logger.info(f"   Confidence     : {unified_verdict['confidence']}")
        logger.info(f"   KP-Vedic Agree : {unified_verdict['agreement_status']}")

        # KP structured extraction (uses unified verdict)
        kp_structured = self._extract_kp_business_structured(planets, houses, unified_verdict)
        result.additional_data["kp_business_analysis"] = kp_structured

        # Legacy business eval (for sectors / foreign link)
        business_eval = evaluate_business_profession(planets, houses)
        result.additional_data["business_structural_kp"] = business_eval

        # Store service_vs_business aligned with unified verdict
        result.additional_data["service_vs_business"] = {
            "final_path":      unified_verdict["primary_path"],
            "business_score":  unified_verdict["business_score"],
            "service_score":   unified_verdict["service_score"],
            "confidence":      unified_verdict["confidence"],
            "agreement_status": unified_verdict["agreement_status"]
        }

        # Business suitability matrix
        try:
            business_matrix = self._create_business_suitability_matrix(
                unified_verdict=unified_verdict,
                kp_analysis=kp_structured,
                business_eval=business_eval
            )
            result.additional_data["business_suitability_matrix"] = business_matrix
            logger.info(f"✅ Business matrix: {len(business_matrix)} types")
        except Exception as e:
            logger.error(f"Business matrix error: {e}")

        # Foreign exposure
        try:
            foreign_exposure = evaluate_foreign_career_exposure(
                planets=planets, houses=houses, planet_chain=None
            )
            result.additional_data["foreign_business_exposure"] = foreign_exposure
        except Exception as e:
            logger.warning(f"Foreign exposure analysis failed: {e}")

        # Timing windows
        timing_windows_raw  = kwargs.get("timing_windows", {})
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = (
                timing_windows_raw.get(sub_subdomain, []) or
                timing_windows_raw.get("Business Start Timing", []) or
                timing_windows_raw.get("Business Prospects", [])
            )
        else:
            timing_windows_list = timing_windows_raw or []

        timing_windows_data = {}
        if meta_query_type == "TIMING":
            timing_windows_data = self._extract_timing_windows(timing_windows_list)

        # ─────────────────────────────────────────────────────────
        # HOUSE ANALYSIS POINTS (Vedic)
        # ─────────────────────────────────────────────────────────
        if sub_subdomain in {
            "Business Prospects",
            "Business Start Timing",
            "Business Partnership Prospects"
        }:
            self._add_house_analysis_points(
                result, house_lords_info, house_aspects_info, primary_houses
            )

        # ─────────────────────────────────────────────────────────
        # QUESTION-SPECIFIC POINTS
        # ─────────────────────────────────────────────────────────
        path       = unified_verdict["primary_path"]
        confidence = unified_verdict["confidence"]

        if sub_subdomain == "Business Prospects":
            result.add_point(
                f"KP: Primary path verdict: **{path}** (Confidence: {confidence})"
            )

            # Promise status per cusp
            for h_num, status in unified_verdict.get("promise_status", {}).items():
                result.add_point(
                    f"KP: House {h_num} ({self.HOUSE_MEANINGS.get(h_num, '')}): {status}"
                )

            # Agreement
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE on business direction")
            elif agreement == "PARTIAL":
                result.add_point("⚠️ KP and Vedic show PARTIAL agreement — KP takes precedence")
            else:
                result.add_point("⚠️ KP and Vedic CONFLICT — KP result prioritized")

            # Sectors from legacy engine
            for sector in business_eval.get("final_professions", [])[:3]:
                result.add_point(f"KP: Suitable business sector: **{sector}**")

            result.add_point(
                f"KP: Foreign/overseas link: **{business_eval.get('foreign_link', 'No')}**"
            )

        elif sub_subdomain == "Business Start Timing":
            result.add_point(f"KP: Career path: **{path}**")

            h7_promise  = unified_verdict.get("promise_status", {}).get(7, "UNKNOWN")
            h10_promise = unified_verdict.get("promise_status", {}).get(10, "UNKNOWN")

            if h7_promise == "PROMISE" and h10_promise == "PROMISE":
                result.add_point("KP: Strong business promise — favorable launch timing likely")
            elif h7_promise == "DENIAL" or h10_promise == "DENIAL":
                result.add_point(
                    "⚠️ Natal promise weak — business launch may be delayed despite good dashas."
                )
            elif h7_promise == "WEAK_PROMISE" or h10_promise == "WEAK_PROMISE":
                result.add_point(
                    "Moderate natal promise — strong dasha/transit needed for launch."
                )
            else:
                result.add_point("Neutral natal promise — dasha strength decides timing.")

            if meta_query_type == "TIMING":
                try:
                    timing_rules  = TIMING_RULES.get("Business Start Timing", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    pos_planets   = get_positive_planets(planet_scores)

                    loan_rules    = TIMING_RULES.get("Loan Taking Timing", {})
                    loan_scores   = score_kp_all_planets(planets, houses, loan_rules)
                    loan_planets  = get_positive_planets(loan_scores)

                    if pos_planets:
                        result.additional_data["business_timing_support_planets"] = pos_planets
                        result.add_point(
                            f"KP: Favorable dasha lords for business launch: {', '.join(pos_planets[:4])}"
                        )
                    if loan_planets:
                        result.additional_data["business_loan_support_planets"] = loan_planets
                        result.add_point(
                            f"KP: Planets supporting loan acquisition: {', '.join(loan_planets[:3])}"
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.additional_data["business_kp_ruling_planets"] = ruling_planets

                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")

        elif sub_subdomain == "Business Partnership Prospects":
            if business_eval.get("partners_needed"):
                result.add_point(
                    "KP: Chart indicates stronger outcomes through **partnership or collaboration**."
                )
            else:
                result.add_point(
                    "KP: Independent / solo business is better supported than partnership."
                )

            h7_info = house_lords_info.get(7, {})
            if h7_info:
                h7_lord     = h7_info.get("lord")
                h7_strength = h7_info.get("lord_strength_score", 50)
                if h7_strength >= 70:
                    result.add_point(
                        f"7th house lord {h7_lord} is STRONG — partnerships can be beneficial."
                    )
                elif h7_strength < 40:
                    result.add_point(
                        f"7th house lord {h7_lord} is WEAK — caution with partnerships."
                    )

            result.add_point(
                "Family business matters require clarity in role definition and financial boundaries."
            )

        elif sub_subdomain == "Business Remedies":
            result.add_point(
                "Business remedies focus on strengthening 7th, 10th, and 11th house lords, "
                "improving decision-making ability, and financial discipline."
            )

        else:
            result.add_point(
                f"KP: Unified path indicates **{unified_verdict['primary_path']}** "
                f"(Confidence: {unified_verdict['confidence']}). "
                "Provide contextual guidance aligned with natal promise."
            )

        # Store all data for LLM
        self._store_data_for_llm(
            result, house_config, house_lords_info, house_aspects_info,
            primary_houses, secondary_houses, timing_windows_data
        )

        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

    def _get_house_lord(self, house_data: Dict) -> Optional[str]:
        """Get lord of a house — tries explicit fields then deduces from sign."""
        lord = (
            house_data.get("rashi_lord") or
            house_data.get("sign_lord") or
            house_data.get("lord") or ""
        )
        if not lord:
            sign = (
                house_data.get("sign") or
                house_data.get("start_rasi") or
                house_data.get("rasi", "")
            )
            lord = self.SIGN_LORDS.get(sign, "")
        return normalize_planet_name(lord)

    def _get_planet_dignity(self, planet_name: str, planet_data: Dict) -> str:
        """Return EXALTED / DEBILITATED / OWN_SIGN / NEUTRAL."""
        sign = planet_data.get("sign", "")
        exaltation = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
            "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
            "Saturn": "Libra"
        }
        debilitation = {
            "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
            "Mercury": "Pisces", "Jupiter": "Capricorn",
            "Venus": "Virgo", "Saturn": "Aries"
        }
        own_signs = {
            "Sun": ["Leo"], "Moon": ["Cancer"],
            "Mars": ["Aries", "Scorpio"],
            "Mercury": ["Gemini", "Virgo"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Venus": ["Taurus", "Libra"],
            "Saturn": ["Capricorn", "Aquarius"]
        }
        if exaltation.get(planet_name) == sign:
            return "EXALTED"
        if debilitation.get(planet_name) == sign:
            return "DEBILITATED"
        if sign in own_signs.get(planet_name, []):
            return "OWN_SIGN"
        return "NEUTRAL"

    def _has_planet_connection(
        self,
        target_planets: List[str],
        planets: Dict,
        houses: List,
        target_houses: Set[int]
    ) -> bool:
        """Check if any target planet occupies or has its star-lord in target houses."""
        for planet in target_planets:
            pdata = planets.get(planet, {})
            if pdata.get("house") in target_houses:
                return True
            sl = normalize_planet_name(pdata.get("nakshatra_lord", ""))
            if sl and planets.get(sl, {}).get("house") in target_houses:
                return True
        return False

    def _score_to_rating(self, score: int) -> str:
        if score >= 5:   return "HIGH"
        if score >= 3:   return "MODERATE"
        if score >= 1:   return "LOW"
        return "VERY_LOW"

    @staticmethod
    def extract_planet_name(p):
        if isinstance(p, dict): return p.get("name")
        if isinstance(p, str):  return p
        return None

    def _extract_house_lords(
        self,
        houses: List,
        planets: Dict,
        relevant_houses: Set[int],
        primary_houses: Set[int]
    ) -> Dict:
        info = {}
        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue
            lord = self._get_house_lord(h)
            if not lord:
                continue
            lord_data = planets.get(lord, {})
            if not lord_data:
                continue

            dignity       = self._get_planet_dignity(lord, lord_data)
            strength      = self._calculate_lord_strength(lord, lord_data, dignity)
            planets_in_h  = [
                normalize_planet_name(self.extract_planet_name(p))
                for p in h.get("planets", [])
                if self.extract_planet_name(p)
            ]
            house_sign = (
                h.get("sign") or h.get("start_rasi") or h.get("rasi", "")
            )

            info[house_num] = {
                "lord":                lord,
                "lord_in_house":       lord_data.get("house"),
                "lord_in_sign":        lord_data.get("sign", ""),
                "lord_degree":         lord_data.get("full_degree") or lord_data.get("degree") or 0,
                "lord_is_combust":     lord_data.get("is_combusted", False) or lord_data.get("is_combust", False),
                "lord_is_retrograde":  lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False),
                "lord_dignity":        dignity,
                "lord_strength_score": strength,
                "priority":            "primary" if house_num in primary_houses else "secondary",
                "planets_in_house":    [p for p in planets_in_h if p],
                "house_sign":          house_sign
            }
        return info

    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        try:
            h1 = next((h for h in houses if h.get("house") == 1), None)
            if not h1:
                return None
            sign = h1.get("sign") or h1.get("start_rasi") or h1.get("rasi", "")
            if not sign:
                return None
            lord = self._get_house_lord(h1)
            if not lord:
                return None
            lord_data = planets.get(lord, {})
            return {
                "lagna_sign":         sign,
                "lagna_lord":         lord,
                "lagna_lord_house":   lord_data.get("house"),
                "lagna_lord_sign":    lord_data.get("sign", ""),
                "lagna_lord_degree":  lord_data.get("full_degree") or lord_data.get("degree") or 0,
                "lagna_lord_dignity": self._get_planet_dignity(lord, lord_data),
            }
        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    def _extract_aspects_on_houses(
        self,
        houses: List,
        planets: Dict,
        aspects_data: Dict,
        relevant_houses: Set[int]
    ) -> Dict:
        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
        result   = {}

        for house_num in relevant_houses:
            result[house_num] = {
                "benefic_aspects": [],
                "malefic_aspects": [],
                "neutral_aspects": []
            }
            for pname, pdata in planets.items():
                aspected = (
                    aspects_data.get(pname, {}).get("aspects_houses", [])
                    if aspects_data
                    else pdata.get("aspects_houses", [])
                )
                if house_num in aspected:
                    if pname in benefics:
                        result[house_num]["benefic_aspects"].append(pname)
                    elif pname in malefics:
                        result[house_num]["malefic_aspects"].append(pname)
                    else:
                        result[house_num]["neutral_aspects"].append(pname)
        return result

    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: Dict,
        dignity: str = "NEUTRAL"
    ) -> int:
        dignity_scores = {
            "EXALTED": 100, "OWN_SIGN": 80,
            "NEUTRAL": 50,  "DEBILITATED": 20
        }
        score = dignity_scores.get(dignity, 50)
        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            score += 10 if planet_name in {"Saturn", "Mars"} else -10
        deg = planet_data.get("full_degree") or planet_data.get("degree") or 15
        if deg < 5 or deg > 25:
            score -= 10
        return int(max(0, min(100, score)))

    def _add_house_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        primary_houses: Set[int]
    ):
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue
            info    = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            parts = [
                f"⭐ House {house_num} ({self.HOUSE_MEANINGS.get(house_num, 'General')}):",
                f"Lord {info['lord']} is {info['lord_dignity']}",
                f"(Strength: {info['lord_strength_score']}/100)"
            ]

            conds = []
            if info["lord_is_combust"]:     conds.append("COMBUST")
            if info["lord_is_retrograde"]:  conds.append("RETROGRADE")
            if conds:
                parts.append(f"[{', '.join(conds)}]")

            if aspects.get("benefic_aspects"):
                parts.append(f"- Benefic: {', '.join(aspects['benefic_aspects'])}")
            if aspects.get("malefic_aspects"):
                parts.append(f"- Malefic: {', '.join(aspects['malefic_aspects'])}")

            result.add_point(" ".join(parts))

    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """Extract BEST and NEAREST timing windows. Handles dict and object formats."""
        if not timing_windows:
            return {}

        def get_attr(obj, key, default=None):
            return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

        def to_dict(w):
            if w is None:
                return None

            def get_score(obj):
                raw = get_attr(obj, "final_score", 0) or 0
                return min(100, round(float(raw), 2))

            if isinstance(w, dict):
                w = dict(w)  # shallow copy
                w["final_score"] = get_score(w)
                return w

            return {
                "start": get_attr(w, "start"),
                "end": get_attr(w, "end"),
                "dasha": get_attr(w, "dasha"),
                "score": get_attr(w, "score"),
                "transit_score": get_attr(w, "transit_score"),
                "final_score": get_score(w),
                "age_at_start": get_attr(w, "age_at_start"),
                "is_overall_best": get_attr(w, "is_overall_best", False),
                "is_earliest_favorable": get_attr(w, "is_earliest_favorable", False),
            }

        try:
            from datetime import datetime
            sorted_w = sorted(
                timing_windows,
                key=lambda w: get_attr(w, "final_score", 0) or 0,
                reverse=True
            )
            best     = to_dict(sorted_w[0]) if sorted_w else None
            fav      = [w for w in timing_windows if (get_attr(w, "final_score", 0) or 0) >= 50]
            nearest  = (
                to_dict(sorted(
                    fav,
                    key=lambda w: datetime.strptime(
                        get_attr(w, "start", "9999-12-31") or "9999-12-31", "%Y-%m-%d"
                    )
                )[0]) if fav else best
            )
            return {
                "best_window":    best,
                "nearest_window": nearest,
                "all_favorable":  [to_dict(w) for w in sorted_w[:5]],
                "has_timing":     True
            }
        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            return {}

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        primary_houses: Set[int],
        secondary_houses: Set[int],
        timing_windows_data: Dict = None
    ):
        prefix = "business"
        result.additional_data.update({
            f"{prefix}_house_config": {
                "primary":   list(primary_houses),
                "secondary": list(secondary_houses),
                "source":    house_config.get("source", "fallback") if house_config else "fallback"
            },
            f"{prefix}_house_lords":   house_lords_info,
            f"{prefix}_house_aspects": house_aspects_info,
            f"{prefix}_analysis_summary": {
                "total_houses_analyzed":  len(house_lords_info),
                "primary_houses_count":   len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "strong_lords": sum(
                    1 for i in house_lords_info.values()
                    if i["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for i in house_lords_info.values()
                    if i["lord_strength_score"] < 40
                )
            }
        })
        if timing_windows_data and timing_windows_data.get("has_timing"):
            result.additional_data[f"{prefix}_timing_windows"] = timing_windows_data

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")
        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")
        if "unified_business_verdict" in ad:
            v = ad["unified_business_verdict"]
            logger.info(f"UNIFIED VERDICT: {v.get('primary_path')}")
            logger.info(f"  Agreement: {v.get('agreement_status')}")

    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ═══════════════════════════════════════════════════════════════

    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="BUS_SN_1",
                question=(
                    "Am I destined for business or entrepreneurship and which industries "
                    "or locations are most favorable for me to start?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Business Prospects"
            ),
            Question(
                id="BUS_SN_2",
                question=(
                    "What are the best timings and directions for launching a business "
                    "and should I consider taking a loan?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Business Start Timing"
            ),
            Question(
                id="BUS_SN_3",
                question=(
                    "Is it better for me to pursue business alone or with partners and how "
                    "can I choose the right partners or address family business issues?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Business Partnership Prospects"
            )
        ]
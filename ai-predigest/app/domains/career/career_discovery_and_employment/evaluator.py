"""
Career Discovery and Employment Evaluator - ENHANCED VERSION v5.0

CRITICAL FIXES FROM v4.0:
✅ UNIFIED CAREER DECISION LAYER - Single source of truth for Service/Business/Hybrid
✅ PURE KP METHODOLOGY - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ CORRECT HOUSE MAPPING - Service: 2,6,10,11 | Business: 2,3,7,11 (not 5,9)
✅ SUB-LORD PROMISE/DENIAL LOGIC - Core KP rule implemented
✅ RAHU/KETU PROPER HANDLING - Star lord + sign lord + conjunctions
✅ HONEST VEDIC-KP AGREEMENT CHECK - AGREEMENT/PARTIAL/CONFLICT
✅ CONSISTENT OUTPUT ACROSS ALL QUESTIONS - Same base ranking used everywhere
✅ STRENGTH HIERARCHY - Sub > Star > Occupy > Own (not fraction scoring)

Architecture:
- _compute_unified_career_verdict() → Single source of truth
- _apply_pure_kp_chain() → Strict KP methodology
- _evaluate_sub_lord_promise() → Promise/denial logic
- _handle_nodes_properly() → Rahu/Ketu significations
- _check_vedic_kp_agreement() → Honest conflict detection
"""

from typing import Dict, List, Optional, Tuple, Set
import logging
import pprint

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
    evaluate_service_profession,
    determine_service_vs_business,
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
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CareerDiscoveryAndEmploymentEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Career → Career Discovery And Employment
    v5.0 - With unified career decision layer and pure KP methodology
    """

    domain = "Career"
    subtopic = "Career Discovery And Employment"
    
    # ═══════════════════════════════════════════════════════════════
    # CORRECTED HOUSE DEFINITIONS (KP Standard)
    # ═══════════════════════════════════════════════════════════════
    
    # Service/Employment houses
    SERVICE_HOUSES = {2, 6, 10, 11}  # Income, service, profession, gains
    
    # Business houses (CORRECTED - removed 5, 9 which are not primary)
    BUSINESS_HOUSES = {2, 3, 7, 11}  # Income, effort/initiative, trade/partnership, gains
    
    # Supporting houses
    WEALTH_HOUSES = {2, 10, 11}
    LOSS_HOUSES = {6, 8, 12}  # 6 is both service AND competition
    FOREIGN_HOUSES = {3, 9, 12}
    
    # House meanings for context
    HOUSE_MEANINGS = {
        1: "Self/Personality/Lagna",
        2: "Income/Wealth/Speech",
        3: "Effort/Communication/Siblings",
        5: "Intelligence/Creativity/Speculation",
        6: "Service/Competition/Enemies",
        7: "Business/Partnership/Trade",
        9: "Fortune/Higher Learning/Long Travel",
        10: "Career/Profession/Authority",
        11: "Gains/Recognition/Fulfillment",
        12: "Foreign/Losses/Expenses"
    }

    # KP Strength Hierarchy (CRITICAL)
    KP_WEIGHT = {
        "sub_lord": 4,      # Highest - decides promise/denial
        "star_lord": 3,     # Result type
        "occupy": 2,        # Planet's own position
        "own": 1            # Ownership
    }

    # ═══════════════════════════════════════════════════════════════
    # UNIFIED CAREER DECISION LAYER (NEW - Single Source of Truth)
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
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Pure KP Analysis (Primary - 60% weight)
        # ═══════════════════════════════════════════════════════════
        
        kp_service_score = 0
        kp_business_score = 0
        kp_reasons = []
        promise_status = {}
        
        # Analyze key cusps: 6th (service), 7th (business), 10th (career)
        key_cusps = {
            6: "Service/Employment",
            7: "Business/Partnership",
            10: "Career/Profession"
        }
        
        for cusp_num, meaning in key_cusps.items():
            cusp_data = next((h for h in houses if h.get("house") == cusp_num), None)
            if not cusp_data:
                continue
            
            # Apply pure KP chain
            chain_result = self._apply_pure_kp_chain(cusp_data, planets, houses)
            
            if chain_result:
                # Store promise status
                promise_status[cusp_num] = chain_result.get("promise_status", "UNKNOWN")
                
                # Get signified houses from sub-lord (most important)
                sub_lord_houses = set(chain_result.get("sub_lord_signifies", []))
                star_lord_houses = set(chain_result.get("star_lord_signifies", []))
                
                # Calculate service/business connection using KP weights
                service_conn = 0
                business_conn = 0
                
                # Sub-lord significations (weight 4)
                service_conn += len(sub_lord_houses & self.SERVICE_HOUSES) * self.KP_WEIGHT["sub_lord"]
                business_conn += len(sub_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["sub_lord"]
                
                # Star-lord significations (weight 3)
                service_conn += len(star_lord_houses & self.SERVICE_HOUSES) * self.KP_WEIGHT["star_lord"]
                business_conn += len(star_lord_houses & self.BUSINESS_HOUSES) * self.KP_WEIGHT["star_lord"]
                
                # CSL occupation (weight 2)
                csl_house = chain_result.get("csl_house")
                if csl_house in self.SERVICE_HOUSES:
                    service_conn += self.KP_WEIGHT["occupy"]
                if csl_house in self.BUSINESS_HOUSES:
                    business_conn += self.KP_WEIGHT["occupy"]
                
                # Accumulate scores
                if cusp_num == 6:  # Service cusp
                    kp_service_score += service_conn
                    if chain_result.get("promise_status") == "PROMISE":
                        kp_reasons.append(f"6th CSL promises employment (sub-lord signifies {sorted(sub_lord_houses & self.SERVICE_HOUSES)})")
                    elif chain_result.get("promise_status") == "DENIAL":
                        kp_reasons.append(f"6th CSL denies easy employment (sub-lord signifies loss houses)")
                
                elif cusp_num == 7:  # Business cusp
                    kp_business_score += business_conn
                    if chain_result.get("promise_status") == "PROMISE":
                        kp_reasons.append(f"7th CSL promises business success (sub-lord signifies {sorted(sub_lord_houses & self.BUSINESS_HOUSES)})")
                    elif chain_result.get("promise_status") == "DENIAL":
                        kp_reasons.append(f"7th CSL denies business (sub-lord signifies loss houses)")
                
                elif cusp_num == 10:
                    kp_reasons.append("10th CSL influences career strength (direction decided by 6th vs 7th)")

                # Store detailed analysis
                result["detailed_analysis"][cusp_num] = chain_result
        
        result["promise_status"] = promise_status
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Vedic Analysis (Secondary - 30% weight)
        # ═══════════════════════════════════════════════════════════
        
        vedic_service_score = 0
        vedic_business_score = 0
        vedic_reasons = []
        
        # Analyze house lords
        for house_num in [6, 7, 10]:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue
            
            lord_name = self._get_house_lord(house_data)
            if not lord_name:
                continue
            
            lord_data = planets.get(lord_name, {})
            lord_house = lord_data.get("house")
            
            if house_num == 6:  # 6th lord
                if lord_house in self.SERVICE_HOUSES:
                    vedic_service_score += 3
                    vedic_reasons.append(f"6th lord {lord_name} in house {lord_house} → strong service indication")
                elif lord_house in self.LOSS_HOUSES:
                    vedic_service_score -= 1
                    vedic_reasons.append(f"6th lord {lord_name} in loss house → employment challenges")
            
            elif house_num == 7:  # 7th lord
                if lord_house in self.BUSINESS_HOUSES:
                    vedic_business_score += 3
                    vedic_reasons.append(f"7th lord {lord_name} in house {lord_house} → business potential")
                elif lord_house in {6, 8, 12}:
                    vedic_business_score -= 2
                    vedic_reasons.append(f"7th lord {lord_name} in house {lord_house} → business obstacles")
            
            elif house_num == 10:  # 10th lord
                # Check dignity
                dignity = self._get_planet_dignity(lord_name, lord_data)
                if dignity in ["EXALTED", "OWN_SIGN"]:
                    vedic_service_score += 2
                    vedic_business_score += 1
                    vedic_reasons.append(f"10th lord {lord_name} is {dignity} → strong career foundation")
                elif dignity == "DEBILITATED":
                    vedic_reasons.append(f"10th lord {lord_name} is {dignity} → career challenges")
        
        # =====================================================
        # STEP 3: PURE KP VERDICT (SUB-LORD DOMINANT)
        # =====================================================

        h6 = promise_status.get(6, "NEUTRAL")
        h7 = promise_status.get(7, "NEUTRAL")
        h10 = promise_status.get(10, "NEUTRAL")

        # 1️⃣ Clear dominance cases

        if h6 == "PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"

        elif h7 == "PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"

        # 2️⃣ Both strong → Hybrid

        elif h6 == "PROMISE" and h7 == "PROMISE":
            primary = "Hybrid"

        # 3️⃣ Weak promise leaning

        elif h6 == "WEAK_PROMISE" and h7 in ["DENIAL", "NEUTRAL"]:
            primary = "Service"

        elif h7 == "WEAK_PROMISE" and h6 in ["DENIAL", "NEUTRAL"]:
            primary = "Business"

        # 4️⃣ Both weak or denial

        elif h6 == "DENIAL" and h7 == "DENIAL":
            primary = "Hybrid"

        else:
            # Tie-breaker using 10th cusp sub-lord leaning
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

        # =====================================================
        # STEP 4: CONFIDENCE FROM 10TH CUSP
        # =====================================================

        h10_data = result["detailed_analysis"].get(10, {})
        sub_houses = set(h10_data.get("sub_lord_signifies", []))

        positive_conn = sub_houses & self.SERVICE_HOUSES
        loss_conn = sub_houses & {8, 12}

        if h10 == "PROMISE" and not loss_conn:
            confidence = "High"
        elif h10 == "PROMISE" and loss_conn:
            confidence = "Moderate"
        elif h10 == "WEAK_PROMISE":
            confidence = "Moderate"
        elif h10 == "DENIAL":
            confidence = "Low"
        else:
            confidence = "Moderate"

        result["confidence"] = confidence

        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: Check Vedic-KP Agreement (Honest Assessment)
        # ═══════════════════════════════════════════════════════════
        
        kp_verdict = result["primary_path"]
        vedic_verdict = "Service" if vedic_service_score > vedic_business_score else "Business"


        if kp_verdict == vedic_verdict:
            result["agreement_status"] = "AGREEMENT"
        elif kp_verdict == "Hybrid":
            result["agreement_status"] = "PARTIAL"
        else:
            result["agreement_status"] = "CONFLICT"

        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Generate Career Ranking (For Consistency)
        # ═══════════════════════════════════════════════════════════
        
        career_paths = []
        
        # Government Job
        govt_score = 0
        if promise_status.get(6) == "PROMISE":
            govt_score += 3
        if any(p in ["Sun", "Saturn"] for p in self._get_10th_chain_planets(planets, houses)):
            govt_score += 2
        career_paths.append(("Government Job", govt_score))
        
        # Private Sector
        private_score = 0
        if promise_status.get(6) == "PROMISE":
            private_score += 2
        if promise_status.get(10) == "PROMISE":
            private_score += 2
        career_paths.append(("Private Sector Job", private_score))
        
        # Business/Self-Employment
        business_path_score = 0
        if promise_status.get(7) == "PROMISE":
            business_path_score += 3
        if result["primary_path"] == "Business":
            business_path_score += 2
        career_paths.append(("Business/Self-Employment", business_path_score))
        
        # Technical/IT
        tech_score = 0
        if self._has_planet_connection(["Rahu", "Saturn", "Mercury"], planets, houses, {3, 10}):
            tech_score += 3
        career_paths.append(("Technical/IT Roles", tech_score))
        
        # Creative/Arts
        creative_score = 0
        if self._has_planet_connection(["Venus", "Moon"], planets, houses, {5, 10}):
            creative_score += 3
        career_paths.append(("Creative/Arts", creative_score))
        
        # Management/Leadership
        mgmt_score = 0
        if self._has_planet_connection(["Sun", "Jupiter", "Mars"], planets, houses, {10, 11}):
            mgmt_score += 3
        career_paths.append(("Management/Leadership", mgmt_score))
        
        # Foreign/Multinational
        foreign_score = 0
        if self._has_planet_connection(["Rahu"], planets, houses, {9, 12}):
            foreign_score += 3
        career_paths.append(("Foreign/Multinational", foreign_score))
        
        # Sort by score
        career_paths.sort(key=lambda x: x[1], reverse=True)
        result["career_ranking"] = [
            {"path": path, "score": score, "rating": self._score_to_rating(score)}
            for path, score in career_paths
        ]
        
        # Store reasoning
        result["kp_reasoning"] = " | ".join(kp_reasons) if kp_reasons else "KP analysis incomplete"
        result["vedic_reasoning"] = " | ".join(vedic_reasons) if vedic_reasons else "Vedic analysis incomplete"
        
        return result

    def _apply_pure_kp_chain(
        self,
        cusp_data: Dict,
        planets: Dict,
        houses: List
    ) -> Dict:
        """
        Apply PURE KP methodology: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
        
        KP Rule: Sub-lord of cusp decides whether house matters will manifest.
        - If sub-lord signifies positive houses → PROMISE
        - If sub-lord signifies 6, 8, 12 strongly → DENIAL or obstacles
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
        
        # Get CSL (Cusp Sub Lord)
        csl_name = cusp_data.get("cusp_sub_lord", "")
        csl = normalize_planet_name(csl_name)
        
        if not csl:
            return result
        
        result["csl"] = csl
        csl_data = planets.get(csl, {})
        result["csl_house"] = csl_data.get("house")
        result["csl_nakshatra"] = csl_data.get("nakshatra", "")
        
        # Get Star Lord (Nakshatra Lord of CSL)
        star_lord_name = csl_data.get("nakshatra_lord", "")
        star_lord = normalize_planet_name(star_lord_name)
        result["star_lord"] = star_lord
        
        # Get Star Lord's significations
        if star_lord:
            star_lord_houses = self._get_planet_significations(star_lord, planets, houses)
            result["star_lord_signifies"] = sorted(star_lord_houses)
        
        # Get Sub Lord of CSL (this is the KEY for promise/denial)
        sub_lord_name = csl_data.get("sub_lord", "")
        sub_lord = normalize_planet_name(sub_lord_name)
        result["sub_lord"] = sub_lord
        
        # Get Sub Lord's significations (MOST IMPORTANT)
        if sub_lord:
            sub_lord_houses = self._get_planet_significations(sub_lord, planets, houses)
            result["sub_lord_signifies"] = sorted(sub_lord_houses)
            
            # Determine promise/denial based on sub-lord significations
            house_num = cusp_data.get("house", 0)
            promise_status = self._evaluate_sub_lord_promise(
                house_num, 
                sub_lord_houses,
                result.get("star_lord_signifies", [])
            )
            result["promise_status"] = promise_status
        
        # Build chain text
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
        
        Rules:
        - For 6th cusp (service): Promise if sub-lord signifies 2, 6, 10, 11
        - For 7th cusp (business): Promise if sub-lord signifies 2, 3, 7, 11
        - For 10th cusp (career): Promise if sub-lord signifies 2, 6, 10, 11
        - Denial if sub-lord primarily signifies 8, 12
        """
        sub_set = set(sub_lord_houses)
        star_set = set(star_lord_houses)
        
        # Loss houses
        loss_houses = {8, 12}
        loss_connection = len(sub_set & loss_houses)
        
        if cusp_house == 6:  # Service/Employment
            positive = {2, 6, 10, 11}
            positive_connection = len(sub_set & positive)
            
            if sub_set & positive and not sub_set & {8, 12}:
                return "PROMISE"
            elif sub_set & {8, 12} and not sub_set & positive:
                return "DENIAL"
            elif sub_set & positive:
                return "WEAK_PROMISE"
            else:
                return "NEUTRAL"

        
        elif cusp_house == 7:  # Business
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

            # If 6 strongly connected → business weakened (service dependency)
            if service_conn and not positive_conn:
                return "DENIAL"

            # Mixed case
            if positive_conn:
                return "WEAK_PROMISE"

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
        Now SAFE against recursive loops.
        """

        if not planet_name:
            return []

        planet_name = normalize_planet_name(planet_name)

        # Initialize visited tracker
        if visited is None:
            visited = set()

        # 🚨 BREAK RECURSION IF LOOP DETECTED
        if planet_name in visited:
            logger.warning(f"Recursive KP loop detected for {planet_name}")
            return []

        visited.add(planet_name)

        signified = set()
        planet_data = planets.get(planet_name, {})

        if not planet_data:
            return []

        # 🔹 Handle Rahu/Ketu safely
        if planet_name in ["Rahu", "Ketu"]:
            # 1️⃣ Star lord
            star_lord = normalize_planet_name(planet_data.get("nakshatra_lord"))
            if star_lord and star_lord != planet_name:
                signified.update(
                    self._get_planet_significations(star_lord, planets, houses, visited)
                )

            # 2️⃣ Sign lord
            sign = planet_data.get("sign")
            sign_lord = self._get_sign_lord(sign)
            if sign_lord:
                signified.update(
                    self._get_planet_significations(sign_lord, planets, houses, visited)
                )
            
            # 3️⃣ Conjunctions (same house planets)
            for p_name, p_data in planets.items():
                if p_name == planet_name:
                    continue
                if p_data.get("house") == planet_data.get("house"):
                    signified.update(
                        self._get_planet_significations(p_name, planets, houses, visited)
                    )



        # 1️⃣ Occupied house
        occupied_house = planet_data.get("house")
        if occupied_house:
            signified.add(occupied_house)

        # 2️⃣ Owned houses
        owned_houses = self._get_owned_houses(planet_name, houses)
        signified.update(owned_houses)

        # 3️⃣ Planets in star of this planet
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
        """Get houses owned by a planet"""
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
        """Get lord of a house"""
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
        """Get dignity of a planet"""
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
        """Get planets involved in 10th house chain"""
        chain = []
        
        h10 = next((h for h in houses if h.get("house") == 10), None)
        if not h10:
            return chain
        
        # CSL
        csl = h10.get("cusp_sub_lord")
        if csl:
            chain.append(normalize_planet_name(csl))
        
        # Star lord
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
        """Check if any target planet connects to target houses"""
        for planet in target_planets:
            if planet not in planets:
                continue
            
            p_data = planets[planet]
            p_house = p_data.get("house")
            
            if p_house in target_houses:
                return True
            
            # Check star lord connection
            star_lord = p_data.get("nakshatra_lord")
            if star_lord and star_lord in planets:
                sl_house = planets[star_lord].get("house")
                if sl_house in target_houses:
                    return True
        
        return False

    def _score_to_rating(self, score: int) -> str:
        """Convert numeric score to rating"""
        if score >= 5:
            return "HIGH"
        elif score >= 3:
            return "MODERATE"
        elif score >= 1:
            return "LOW"
        else:
            return "VERY_LOW"

    # ═══════════════════════════════════════════════════════════════
    # CAREER SUITABILITY MATRIX (FIXED - Uses Unified Verdict)
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
        
        # Convert ranking to matrix format
        for item in career_ranking:
            path = item.get("path", "Unknown")
            rating = item.get("rating", "LOW")
            score = item.get("score", 0)
            
            # Generate reasoning based on path type
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
    # KP ANALYSIS EXTRACTION (FIXED - Pure Methodology)
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
        
        # Get detailed analysis from unified verdict
        detailed = unified_verdict.get("detailed_analysis", {})
        
        career_houses = [2, 6, 7, 9, 10, 11]
        
        for house_num in career_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue
            
            # Apply KP chain
            chain_result = self._apply_pure_kp_chain(house_data, planets, houses)
            
            if chain_result.get("csl"):
                kp_data["has_kp_data"] = True
                
                csl = chain_result["csl"]
                csl_data = planets.get(csl, {})
                
                # Determine verdict based on promise status and context
                promise = chain_result.get("promise_status", "NEUTRAL")
                
                if promise == "PROMISE":
                    verdict = "STRONG"
                elif promise == "DENIAL":
                    verdict = "WEAK"
                elif promise == "WEAK_PROMISE":
                    verdict = "MODERATE"
                else:
                    verdict = "NEUTRAL"
                
                # Build interpretation
                interpretation = self._build_kp_interpretation(
                    house_num,
                    chain_result,
                    unified_verdict
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
                
                # Add to key findings
                kp_data["key_findings"].append(
                    f"House {house_num}: {csl} → Sub Lord {chain_result.get('sub_lord')} → "
                    f"signifies {chain_result.get('sub_lord_signifies', [])} → {promise}"
                )
        
        # Set overall verdict from unified analysis
        kp_data["overall_verdict"] = unified_verdict.get("primary_path", "UNKNOWN")
        kp_data["agreement_status"] = unified_verdict.get("agreement_status", "UNKNOWN")
        
        return kp_data

    def _build_kp_interpretation(
        self,
        house_num: int,
        chain_result: Dict,
        unified_verdict: Dict
    ) -> str:
        """Build human-readable KP interpretation"""
        
        csl = chain_result.get("csl", "Unknown")
        sub_lord = chain_result.get("sub_lord", "Unknown")
        sub_houses = chain_result.get("sub_lord_signifies", [])
        promise = chain_result.get("promise_status", "NEUTRAL")
        
        if house_num == 6:
            if promise == "PROMISE":
                return (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Strong service house connection → Employment PROMISED. "
                    f"Job/service matters will manifest positively."
                )
            elif promise == "DENIAL":
                return (
                    f"6th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss house dominance → Employment faces obstacles. "
                    f"Delays or struggles in finding/keeping job."
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
                    f"Strong business house connection → Partnership/trade PROMISED. "
                    f"Business ventures will succeed."
                )
            elif promise == "DENIAL":
                return (
                    f"7th CSL {csl}'s sub-lord {sub_lord} signifies {sub_houses}. "
                    f"Loss/competition houses dominate → Business NOT favored. "
                    f"Service path safer than independent business."
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
                    f"Loss houses dominate → Career challenges indicated. "
                    f"Requires effort and patience."
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
    # MAIN EVALUATION (FIXED - Uses Unified Verdict)
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

        # Get question-specific houses
        question_text = kwargs.get("question", "")
        house_config = get_houses_for_question(self.domain, self.subtopic, question_text)
        
        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses | {1}
        else:
            all_relevant_houses = {1, 2, 6, 7, 9, 10, 11}
            primary_houses = {10, 6, 7}
            secondary_houses = {1, 2, 9, 11}

        meta = kwargs.get("meta")
        sub_subdomain = kwargs.get("sub_subdomain", "Career Discovery And Employment")
        profession_map = kwargs.get("profession_map") or KP_PROFESSION_MAP

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("CAREER EVALUATOR v5.0 - UNIFIED DECISION LAYER")
        logger.info("=" * 80)

        # Calculate aspects
        detect_aspects(analysis_planets)
        detect_aspects(planets)
        
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # Extract house lords
        house_lords_info = self._extract_house_lords(
            analysis_houses, analysis_planets, all_relevant_houses, primary_houses
        )

        # Extract lagna info
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        # Extract aspects
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses, analysis_planets, aspects_data, all_relevant_houses
        )

        # ═══════════════════════════════════════════════════════════
        # CRITICAL: Compute UNIFIED CAREER VERDICT (Single Source of Truth)
        # ═══════════════════════════════════════════════════════════
        
        unified_verdict = self._compute_unified_career_verdict(planets, houses)
        
        # Store unified verdict for ALL questions to use
        result.additional_data["unified_career_verdict"] = unified_verdict
        
        logger.info(f"🎯 UNIFIED VERDICT: {unified_verdict['primary_path']}")
        logger.info(f"   Service Score: {unified_verdict['service_score']}")
        logger.info(f"   Business Score: {unified_verdict['business_score']}")
        logger.info(f"   Confidence: {unified_verdict['confidence']}")
        logger.info(f"   KP-Vedic Agreement: {unified_verdict['agreement_status']}")

        # Extract timing windows
        timing_windows_raw = kwargs.get("timing_windows", {})
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = (
                timing_windows_raw.get(sub_subdomain, []) or
                timing_windows_raw.get("Job Start Timing", []) or
                timing_windows_raw.get("Career Overview", [])
            )
        else:
            timing_windows_list = timing_windows_raw or []
        
        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        # ═══════════════════════════════════════════════════════════
        # Extract KP analysis using unified verdict
        # ═══════════════════════════════════════════════════════════
        
        kp_structured = self._extract_kp_career_structured(planets, houses, unified_verdict)
        result.additional_data["kp_career_analysis"] = kp_structured

        # Create career matrix using unified verdict
        career_matrix = self._create_career_suitability_matrix(unified_verdict, kp_structured)
        result.additional_data["career_suitability_matrix"] = career_matrix

        # ═══════════════════════════════════════════════════════════
        # Career role resonance (uses unified verdict)
        # ═══════════════════════════════════════════════════════════
        
        try:
            service_eval = evaluate_service_profession(
                planets=planets,
                houses=houses,
                KP_PROFESSION_MAP=profession_map
            )
            
            # Align with unified verdict
            service_eval["unified_path"] = unified_verdict["primary_path"]
            
            result.additional_data["career_role_resonance"] = {
                "career_category": service_eval.get("career_category"),
                "career_direction": service_eval.get("career_direction"),
                "roles": service_eval.get("final_professions"),
                "confidence": unified_verdict["confidence"],  # Use unified confidence
                "context_tags": service_eval.get("context_tags"),
                "planet_chain": service_eval.get("planet_chain"),
                "mode": unified_verdict["primary_path"],  # Use unified path
                "csl_reasoning": service_eval.get("csl_reasoning"),
                "context_explanation": service_eval.get("context_explanation")
            }
        except Exception as e:
            logger.warning(f"Career role extraction failed: {e}")

        # Service vs Business (aligned with unified verdict)
        result.additional_data["career_service_vs_business"] = {
            "final_path": unified_verdict["primary_path"],
            "service_score": unified_verdict["service_score"],
            "business_score": unified_verdict["business_score"],
            "confidence": unified_verdict["confidence"],
            "agreement_status": unified_verdict["agreement_status"]
        }

        # Foreign exposure
        try:
            foreign_exposure = evaluate_foreign_career_exposure(
                planets=planets,
                houses=houses,
                planet_chain=result.additional_data.get("career_role_resonance", {}).get("planet_chain", [])
            )
            result.additional_data["foreign_career_exposure"] = foreign_exposure
        except Exception as e:
            logger.warning(f"Foreign exposure analysis failed: {e}")

        # ═══════════════════════════════════════════════════════════
        # Add Points Based on Sub-subdomain
        # ═══════════════════════════════════════════════════════════

        # House analysis points (Vedic)
        if sub_subdomain in {"Career Overview", "Job Start Timing", "Career Analysis and Advice (LLM)"}:
            self._add_house_analysis_points(result, house_lords_info, house_aspects_info, primary_houses)

        # LLM-only questions
        if sub_subdomain in {"Career Analysis and Advice (LLM)", "Further Studies Advice"}:
            result.add_point(
                "This question is evaluated using experiential, educational, and contextual factors "
                "rather than predictive astrology."
            )
            self._store_data_for_llm(
                result, house_config, house_lords_info, house_aspects_info,
                primary_houses, secondary_houses, timing_windows_data
            )
            if lagna_info:
                result.additional_data["lagna_info"] = lagna_info
            return result

        # Career Overview
        if sub_subdomain == "Career Overview":
            # Use UNIFIED verdict for consistency
            path = unified_verdict["primary_path"]
            confidence = unified_verdict["confidence"]
            
            result.add_point(f"KP: Primary career path: **{path}** (Confidence: {confidence})")
            
            if unified_verdict.get("secondary_path"):
                result.add_point(f"KP: Secondary potential: **{unified_verdict['secondary_path']}**")
            
            # Promise status
            for house_num, status in unified_verdict.get("promise_status", {}).items():
                house_meaning = self.HOUSE_MEANINGS.get(house_num, "")
                result.add_point(f"KP: House {house_num} ({house_meaning}): {status}")
            
            # Agreement status
            agreement = unified_verdict.get("agreement_status", "UNKNOWN")
            if agreement == "AGREEMENT":
                result.add_point("✅ KP and Vedic systems AGREE on career direction")
            elif agreement == "PARTIAL":
                result.add_point("⚠️ KP and Vedic show PARTIAL agreement - KP takes precedence")
            elif agreement == "CONFLICT":
                result.add_point("⚠️ KP and Vedic CONFLICT - KP result prioritized for timing")
            
            # Career roles
            career_data = result.additional_data.get("career_role_resonance", {})
            for role in career_data.get("roles", [])[:5]:
                result.add_point(f"KP: Suitable role: **{role}**")

        # Job Start Timing
        elif sub_subdomain == "Job Start Timing":
            # Use UNIFIED verdict
            path = unified_verdict["primary_path"]
            result.add_point(f"KP: Career path: **{path}**")
            
            # Promise status for timing
            promise_6 = unified_verdict.get("promise_status", {}).get(6, "UNKNOWN")
            promise_10 = unified_verdict.get("promise_status", {}).get(10, "UNKNOWN")
            
            if promise_6 == "PROMISE" and promise_10 == "PROMISE":
                result.add_point("KP: Strong employment promise - favorable timing likely")

            elif promise_6 == "DENIAL" or promise_10 == "DENIAL":
                result.add_point(
                    "⚠️ Natal promise weak — employment may be unstable or delayed despite good dashas."
                )

            elif promise_6 == "WEAK_PROMISE" or promise_10 == "WEAK_PROMISE":
                result.add_point(
                    "Moderate natal promise — strong dasha/transit needed for manifestation."
                )

            else:
                result.add_point("Neutral natal promise — timing results depend heavily on dasha strength.")


            
            # Timing layer
            if meta and meta_query_type == QueryType.TIMING:
                try:
                    timing_rules = TIMING_RULES.get("Job Start Timing", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    positive_planets = get_positive_planets(planet_scores)

                    if positive_planets:
                        result.add_point(
                            f"KP: Favorable dasha lords: {', '.join(positive_planets[:4])}"
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.add_point(
                            f"KP: Ruling planets: {', '.join(ruling_planets[:4])}"
                        )
                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")

        # Remedies
        elif sub_subdomain == "Career Remedies":
            result.add_point(
                "Career remedies focus on strengthening planets governing profession, "
                "employment, income, and recognition."
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
    # HELPER METHODS (Preserved from v4.0 with minor fixes)
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
                
                return {
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
            
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )
            
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None
            
            from datetime import datetime
            favorable_windows = [
                w for w in timing_windows 
                if (get_attr(w, 'final_score', 0) or 0) >= 50
            ]
            
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
            
            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]
            
            return {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }
            
        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            return {}

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
        """Extract house lord information for relevant houses."""
        house_lords_info = {}
        
        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue
            
            lord_name = self._get_house_lord(h)
            if not lord_name:
                continue
            
            lord_data = planets.get(lord_name, {})
            if not lord_data:
                continue
                
            lord_house = lord_data.get("house")
            lord_sign = lord_data.get("sign", "")
            lord_degree = lord_data.get("full_degree") or lord_data.get("degree") or 0
            lord_is_combust = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)
            
            lord_dignity = self._get_planet_dignity(lord_name, lord_data)
            lord_strength_score = self._calculate_lord_strength(lord_name, lord_data, lord_dignity)
            
            priority = "primary" if house_num in primary_houses else "secondary"
            
            planets_in_house = []
            for p in h.get("planets", []):
                planet_name = normalize_planet_name(self.extract_planet_name(p))
                if planet_name:
                    planets_in_house.append(planet_name)
            
            house_sign = h.get("sign") or h.get("start_rasi") or h.get("rasi") or ""
            
            house_lords_info[house_num] = {
                "lord": lord_name,
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
        """Extract aspects on relevant houses."""
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

    def _calculate_lord_strength(self, planet_name: str, planet_data: dict, dignity: str) -> int:
        """Calculate lord strength score (0-100)."""
        dignity_scores = {
            "EXALTED": 100,
            "OWN_SIGN": 80,
            "NEUTRAL": 50,
            "DEBILITATED": 20
        }
        score = dignity_scores.get(dignity, 50)
        
        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 30
        
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            if planet_name in {"Jupiter", "Venus", "Mercury"}:
                score -= 10
            elif planet_name in {"Saturn", "Mars"}:
                score += 10
        
        return max(0, min(100, score))
    
    def _extract_lagna_info(self, houses: List[Dict], planets: Dict[str, Dict]) -> Optional[Dict]:
        """Extract lagna (ascendant) information."""
        try:
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            if not house_1:
                return None
            
            lagna_sign = house_1.get("sign") or house_1.get("start_rasi") or house_1.get("rasi") or ""
            if not lagna_sign:
                return None
            
            lagna_lord = self._get_house_lord(house_1)
            if not lagna_lord:
                return None
            
            lagna_lord_data = planets.get(lagna_lord, {})
            
            return {
                "lagna_sign": lagna_sign,
                "lagna_lord": lagna_lord,
                "lagna_lord_house": lagna_lord_data.get("house"),
                "lagna_lord_sign": lagna_lord_data.get("sign", ""),
                "lagna_lord_degree": lagna_lord_data.get("full_degree") or lagna_lord_data.get("degree") or 0,
                "lagna_lord_dignity": self._get_planet_dignity(lagna_lord, lagna_lord_data),
            }
            
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
        """Store all enhanced data for LLM consumption."""
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
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        
        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")
        
        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")
        
        # Log unified verdict
        if "unified_career_verdict" in ad:
            verdict = ad["unified_career_verdict"]
            logger.info(f"UNIFIED VERDICT: {verdict.get('primary_path')}")
            logger.info(f"  Agreement: {verdict.get('agreement_status')}")

    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="CAR_DE_1",
                question=(
                    "What career track, field, or roles—such as government, private, or "
                    "non-traditional sectors—are best suited to my natural talents?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Career Overview"
            ),
            Question(
                id="CAR_DE_2",
                question=(
                    "Should I pursue a job now or opt for further studies for better prospects?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Career Analysis and Advice (LLM)"
            ),
            Question(
                id="CAR_DE_3",
                question=(
                    "When am I likely to secure a job and what obstacles might I face "
                    "in my career journey?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Job Start Timing"
            )
        ]
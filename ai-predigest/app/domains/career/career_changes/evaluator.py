"""
Career Changes Evaluator - ENHANCED VERSION v4.0

Based on ProspectsOfInvestmentsEvaluator v3.3, CareerDiscoveryAndEmploymentEvaluator v4.0,
and StartingNewBusinessEvaluator v4.0 architecture.

ENHANCEMENTS IN v4.0:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ KP career engine integration (preserved)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP significations using correct hierarchy (sub > star > occupy > own)
✅ Career Change Suitability Matrix with correct planet mapping
✅ Lagna lord analysis for career personality
✅ Service vs Business structured analysis
✅ Foreign career exposure analysis
✅ Career role resonance from KP profession mapping

Covers:
- Career shift suitability (Service → Business / Business → Service / Hybrid)
- Favorable timing for career change
- Obstacles during transition (LLM-driven)
- Education / reskilling advice (LLM-driven)
- Remedies handled separately

Key Houses for Career Changes:
- 10th: Career/Authority (PRIMARY)
- 6th: Service/Employment (PRIMARY)
- 7th: Business/Partnerships (PRIMARY)
- 2nd: Income/Salary
- 9th: Fortune/Opportunities
- 11th: Gains/Recognition
- 3rd: Initiative/Skills
- 12th: Foreign/Losses
"""

from typing import Dict, List, Optional, Tuple, Set
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

from app.core.astro_constants import (
    detect_aspects,
    normalize_planet_name,
    normalize_planet,
    get_planet,
    get_house_of,
    get_signified_houses,
    get_signified_score
)
from app.domains.excel_structure_config import get_houses_for_question


# ---- KP CAREER ENGINE (NO MODIFICATION) ----
from app.domains.career.kp_career_engine import (
    determine_service_vs_business,
    evaluate_service_profession,
    evaluate_business_profession,
    evaluate_foreign_career_exposure
)
from app.core.astro_constants import KP_PROFESSION_MAP


from app.services.timing_engine import (
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets,
    TIMING_RULES
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
    logging.warning("House lords analyzer available")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CareerChangesEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Career → Career Changes
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Dual data source support (KP + Vedic)
    - Timing windows extraction and formatting
    - KP significations with correct hierarchy
    - Career Change suitability matrix
    - Foreign career exposure analysis
    """

    domain = "Career"
    subtopic = "Career Changes"
    
    # Career-specific houses
    CAREER_HOUSES = {2, 3, 6, 7, 9, 10, 11, 12}
    
    # House groups for signification analysis
    SERVICE_HOUSES = {2, 6, 10, 11}
    BUSINESS_HOUSES = {2, 7, 11, 3}
    WEALTH_HOUSES = {2, 10, 11}
    FOREIGN_HOUSES = {3, 9, 12}
    LOSS_HOUSES = {8, 12}
    
    # House meanings for career context
    HOUSE_MEANINGS = {
        1: "Self/Personality",
        2: "Income/Salary",
        3: "Initiative/Skills",
        6: "Service/Employment",
        7: "Business/Partnerships",
        9: "Fortune/Opportunities",
        10: "Career/Authority",
        11: "Gains/Recognition",
        12: "Foreign/Losses"
    }

    def _create_career_change_suitability_matrix(
        self,
        kp_analysis: Dict,
        service_vs_business: Dict = None,
        foreign_exposure: Dict = None,
        career_roles: Dict = None
    ) -> Dict[str, Dict]:
        """
        Create career change suitability matrix based on KP analysis.
        
        Maps KP significations to career change scenarios.
        """
        matrix = {}
        
        csl_details = kp_analysis.get("csl_details", {})
        h10_detail = csl_details.get(10, {})
        h6_detail = csl_details.get(6, {})
        h7_detail = csl_details.get(7, {})
        h11_detail = csl_details.get(11, {})
        h9_detail = csl_details.get(9, {})
        h3_detail = csl_details.get(3, {})

        h10_sig = set(h10_detail.get("signified_houses", []))
        h6_sig = set(h6_detail.get("signified_houses", []))
        h7_sig = set(h7_detail.get("signified_houses", []))
        h3_sig = set(h3_detail.get("signified_houses", []))
        h9_sig = set(h9_detail.get("signified_houses", []))
        h11_sig = set(h11_detail.get("signified_houses", []))
        
        h10_verdict = h10_detail.get("verdict", "UNKNOWN")
        h6_verdict = h6_detail.get("verdict", "UNKNOWN")
        h7_verdict = h7_detail.get("verdict", "UNKNOWN")
        
        h10_csl = h10_detail.get("csl")
        h6_csl = h6_detail.get("csl")
        h7_csl = h7_detail.get("csl")
        
        # Get service vs business scores
        final_path = service_vs_business.get("final_path", "Mixed") if service_vs_business else "Mixed"
        service_score = service_vs_business.get("service_score", 0) if service_vs_business else 0
        business_score = service_vs_business.get("business_score", 0) if service_vs_business else 0
        career_shift = service_vs_business.get("career_shift_likelihood", "No") if service_vs_business else "No"
        
        # Get foreign exposure
        foreign_level = foreign_exposure.get("exposure_level", "Stable Local Career") if foreign_exposure else "Stable Local Career"
        foreign_score = foreign_exposure.get("score", 0) if foreign_exposure else 0
        
        # Planet categories
        stable_planets = {"Saturn", "Jupiter", "Sun"}
        dynamic_planets = {"Mercury", "Mars", "Rahu"}
        
        # ═══════════════════════════════════════════════════════════
        # 1. SERVICE TO BUSINESS TRANSITION
        # ═══════════════════════════════════════════════════════════
        s2b_indicators = 0
        s2b_reasons = []
        
        if final_path == "Business" or business_score > service_score:
            s2b_indicators += 2
            s2b_reasons.append("KP indicates business path stronger than service")
        
        if h7_verdict in ["STRONG", "EXCELLENT", "BUSINESS_FAVORABLE"]:
            s2b_indicators += 2
            s2b_reasons.append("7th house (business) strongly placed")
        
        if career_shift == "Yes":
            s2b_indicators += 1
            s2b_reasons.append("Career shift likelihood indicated")
        
        if 3 in h7_sig or 11 in h7_sig:
            s2b_indicators += 1
            s2b_reasons.append("7th house connects to initiative/gains houses (3/11)")
        
        if s2b_indicators >= 4:
            rating = "HIGH"
        elif s2b_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Service to Business Transition"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(s2b_reasons) if s2b_reasons else "Service path may be more suitable"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 2. BUSINESS TO SERVICE TRANSITION
        # ═══════════════════════════════════════════════════════════
        b2s_indicators = 0
        b2s_reasons = []
        
        if final_path == "Service" or service_score > business_score:
            b2s_indicators += 2
            b2s_reasons.append("KP indicates service path stronger than business")
        
        if h6_verdict in ["STRONG", "SERVICE_FAVORABLE"]:
            b2s_indicators += 2
            b2s_reasons.append("6th house (service) strongly placed")
        
        if h10_verdict in ["SERVICE_FAVORABLE", "BUSINESS_FAVORABLE"]:
            b2s_indicators += 1
            b2s_reasons.append("10th house supports career stability")
        
        if 6 in h10_sig and 10 in h10_sig:
            b2s_indicators += 1
            b2s_reasons.append("10th house strongly connected to service structure (6/10)")
        
        if b2s_indicators >= 4:
            rating = "HIGH"
        elif b2s_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Business to Service Transition"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(b2s_reasons) if b2s_reasons else "Business path may be more suitable"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 3. HYBRID CAREER (JOB + SIDE BUSINESS)
        # ═══════════════════════════════════════════════════════════
        if h6_verdict == "SERVICE_FAVORABLE" and h7_verdict == "BUSINESS_FAVORABLE":
            rating = "HIGH"
            reason = "KP indicates balanced service and business capacities"
        elif h10_verdict in ["SERVICE_FAVORABLE", "BUSINESS_FAVORABLE"]and h7_verdict in ["MODERATE", "BUSINESS_FAVORABLE", "HYBRID_INDICATED"]:
            rating = "MODERATE"
            reason = "Both career houses reasonably placed"
        else:
            rating = "LOW"
            reason = "Better to focus on one path"
        
        matrix["Hybrid Career (Job + Side Business)"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 4. GOVERNMENT TO PRIVATE TRANSITION
        # ═══════════════════════════════════════════════════════════
        # Government indicator: 6 + 10 + (9 or 11)
        combined_sig = h10_sig | h6_sig | h9_sig | h11_sig

        # Government structure: service + authority + fortune/gains
        gov_indicators = 1 if (
            6 in combined_sig and
            10 in combined_sig and
            (9 in combined_sig or 11 in combined_sig)
        ) else 0

        # Private: initiative + gains driven
        private_indicators = 1 if (
            3 in combined_sig or
            11 in combined_sig
        ) else 0
        
        if private_indicators > gov_indicators:
            rating = "HIGH"
            reason = "10th house connects to initiative/gain houses (3/11)"
        elif private_indicators == gov_indicators:
            rating = "MODERATE"
            reason = "Can adapt to either sector"
        else:
            rating = "LOW"
            reason = "10th house connects to service/authority houses (6/9/11)"
        
        matrix["Government to Private Transition"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 5. PRIVATE TO GOVERNMENT TRANSITION
        # ═══════════════════════════════════════════════════════════
        if gov_indicators > private_indicators:
            rating = "HIGH"
            reason = "10th house connects to service/authority houses (6/9/11)"
        elif gov_indicators == private_indicators:
            rating = "MODERATE"
            reason = "Can adapt to either sector"
        else:
            rating = "LOW"
            reason = "Private sector may be more suitable"
        
        matrix["Private to Government Transition"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 6. DOMESTIC TO FOREIGN/MULTINATIONAL
        # ═══════════════════════════════════════════════════════════
        if foreign_level == "Foreign / Multinational Exposure" or foreign_score >= 4:
            rating = "HIGH"
            reason = "Strong foreign career indicators through Rahu/9th/12th connections"
        elif foreign_level == "Transferable / Mobile Role" or foreign_score >= 2:
            rating = "MODERATE"
            reason = "Some foreign exposure possible with transfers"
        else:
            rating = "LOW"
            reason = "Domestic career path more suitable"
        
        matrix["Domestic to Foreign/Multinational"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 7. TECHNICAL TO MANAGEMENT
        # ═══════════════════════════════════════════════════════════
        mgmt_indicators = 0
        mgmt_reasons = []
        
        if 10 in h10_sig and (9 in h10_sig or 11 in h10_sig):
            mgmt_indicators += 2
            mgmt_reasons.append("10th connects with authority/growth houses (9/11)")
        
        if h10_verdict in ["SERVICE_FAVORABLE", "BUSINESS_FAVORABLE"]:
            mgmt_indicators += 1
            mgmt_reasons.append("Strong career house indicates leadership potential")
        
        if h9_detail.get("verdict") in ["SERVICE_FAVORABLE", "BUSINESS_FAVORABLE"]:
            mgmt_indicators += 1
            mgmt_reasons.append("9th house supports higher positions")
        
        if mgmt_indicators >= 3:
            rating = "HIGH"
        elif mgmt_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Technical to Management"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(mgmt_reasons) if mgmt_reasons else "Technical path may suit better"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 8. COMPLETE CAREER CHANGE (NEW FIELD)
        # ═══════════════════════════════════════════════════════════
        change_indicators = 0
        change_reasons = []
        
        if career_shift == "Yes":
            change_indicators += 2
            change_reasons.append("KP indicates career shift likelihood")
        
        # Check for Rahu influence (unconventional)
        rahu_connected = any(
            detail.get("csl") == "Rahu" or detail.get("star_lord") == "Rahu"
            for detail in csl_details.values()
        )
        if rahu_connected:
            change_indicators += 1
            change_reasons.append("Rahu connection supports unconventional changes")
        
        if h3_detail.get("verdict") in ["SERVICE_FAVORABLE", "BUSINESS_FAVORABLE", "HYBRID_INDICATED"]:
            change_indicators += 1
            change_reasons.append("Strong 3rd house supports learning new skills")
        
        if change_indicators >= 3:
            rating = "HIGH"
        elif change_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Complete Career Change (New Field)"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(change_reasons) if change_reasons else "Gradual transition recommended"
        }
        
        return matrix

    def _extract_kp_career_change_structured_direct(self, planets: Dict, houses: List) -> Dict:
        """
        Extract structured KP career change data using CORRECT KP methodology:
        CSL → Star Lord → Significations (NOT just CSL planet nature!)
        """
        
        # Try to import signification helpers
        try:
            has_signification_helpers = True
            logger.info("✅ Signification helpers imported successfully")
        except ImportError:
            logger.error("❌ CRITICAL: Signification helpers NOT available")
            has_signification_helpers = False
        
        kp_data = {
            "csl_details": {},
            "overall_verdict": "UNKNOWN",
            "key_findings": [],
            "has_kp_data": False,
            "methodology": "CSL → Star Lord → Significations"
        }
        
        # Career change relevant houses
        career_houses = [2, 3, 6, 7, 9, 10, 11, 12]
        house_meanings = self.HOUSE_MEANINGS
        
        # Extract CSL for each career house
        for house_num in career_houses:
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
            
            csl_planet = planets.get(csl, {})
            
            # Step 1: Try Sub-Lord (highest priority)
            sub_lord_raw = csl_planet.get("sub_lord")
            sub_lord = normalize_planet_name(sub_lord_raw) if sub_lord_raw else None

            star_lord_raw = csl_planet.get("nakshatra_lord", "")
            star_lord = normalize_planet_name(star_lord_raw) if star_lord_raw else None

            nakshatra_name = csl_planet.get("nakshatra", "") or csl_planet.get("nakshatra_name", "")

            signified_houses = set()
            signified_houses = set()
            signified_score = {}

            signified_houses = set()
            signified_score = {}

            try:
                if sub_lord:
                    # 1️⃣ Sub-lord (highest priority)
                    signified_houses = set(get_signified_houses(sub_lord, planets, houses))
                    signified_score = get_signified_score(sub_lord, planets, houses)

                elif star_lord:
                    # 2️⃣ Star-lord
                    signified_houses = set(get_signified_houses(star_lord, planets, houses))
                    signified_score = get_signified_score(star_lord, planets, houses)

                else:
                    # 3️⃣ Fallback: Occupation + Ownership of CSL
                    occupied_house = csl_planet.get("house")
                    owned_houses = [
                        h.get("house")
                        for h in houses
                        if normalize_planet_name(
                            h.get("rashi_lord") or h.get("sign_lord") or h.get("lord")
                        ) == csl
                    ]

                    if occupied_house:
                        signified_houses.add(occupied_house)

                    signified_houses.update(owned_houses)

            except Exception as e:
                logger.error(f"Signification extraction error for house {house_num}: {e}")

            # Step 3: KP Decision via Sub-Lord Significations (Boolean dominance)

            has_2 = 2 in signified_houses
            has_3 = 3 in signified_houses
            has_6 = 6 in signified_houses
            has_7 = 7 in signified_houses
            has_9 = 9 in signified_houses
            has_10 = 10 in signified_houses
            has_11 = 11 in signified_houses
            has_12 = 12 in signified_houses
            has_8 = 8 in signified_houses

            # Core Direction Logic (Correct Order)

            if has_8 or has_12:
                verdict = "CHALLENGING"

            elif has_6 and has_7:
                verdict = "HYBRID_INDICATED"

            elif has_6 and has_10:
                verdict = "SERVICE_FAVORABLE"

            elif has_7 and has_11:
                verdict = "BUSINESS_FAVORABLE"

            else:
                verdict = "MODERATE"
            
            service_strength = sum(signified_score.get(h, 0) for h in self.SERVICE_HOUSES)
            business_strength = sum(signified_score.get(h, 0) for h in self.BUSINESS_HOUSES)
            
            cusp_sign = (
                house_data.get("start_rasi", "") or
                house_data.get("rasi", "") or
                house_data.get("sign", "")
            )
            
            # Planet nature is just the FLAVOR
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            is_benefic = csl in benefics
            is_malefic = csl in malefics
            
            flavor = "benefic flavor" if is_benefic else "malefic flavor" if is_malefic else "neutral flavor"
            
            if star_lord and signified_houses:
                chain_text = f"{csl} ({flavor}) → {star_lord} star → signifies {sorted(signified_houses)}"
            elif star_lord:
                chain_text = f"{csl} ({flavor}) → {star_lord} star → significations unavailable"
            else:
                chain_text = f"{csl} ({flavor}) as CSL (no star lord data)"

            # Verdict based on significations
            interpretation = f"{chain_text} → KP decision: {verdict}"
            
            # # House-specific verdicts
            # if house_num == 10:
            #     if signified_houses:
            #         if service_connection >= 2 or service_strength >= 4:
            #             verdict = "SERVICE_FAVORABLE"
            #             interpretation = f"{chain_text} → Strong service/employment capacity."
            #         elif business_connection >= 2:
            #             verdict = "BUSINESS_LEANING"
            #             interpretation = f"{chain_text} → 10th house leans toward business."
            #         elif loss_connection >= 2:
            #             verdict = "CHALLENGING"
            #             interpretation = f"{chain_text} → Career challenges indicated."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate career capacity."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 6:
            #     if signified_houses:
            #         if service_connection >= 2:
            #             verdict = "STRONG"
            #             interpretation = f"{chain_text} → Strong employment indicators."
            #         elif loss_connection >= 2:
            #             verdict = "CHALLENGING"
            #             interpretation = f"{chain_text} → Employment may face challenges."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate service indicators."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 7:
            #     if signified_houses:
            #         if business_connection >= 2:
            #             verdict = "EXCELLENT"
            #             interpretation = f"{chain_text} → Strong business indicators."
            #         elif service_connection >= 2:
            #             verdict = "SERVICE_LEANING"
            #             interpretation = f"{chain_text} → Partnership house leans toward service."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate business indicators."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 11:
            #     if signified_houses:
            #         if wealth_connection >= 2:
            #             verdict = "FAVORABLE"
            #             interpretation = f"{chain_text} → Good gains and recognition potential."
            #         elif loss_connection >= 2:
            #             verdict = "WEAK"
            #             interpretation = f"{chain_text} → Gains may be delayed."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate gains potential."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 9:
            #     if signified_houses:
            #         if 9 in signified_houses or foreign_connection >= 1:
            #             verdict = "PROMISING"
            #             interpretation = f"{chain_text} → Fortune and opportunities supported."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate opportunity indicators."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 3:
            #     if signified_houses:
            #         if 3 in signified_houses:
            #             verdict = "STRONG"
            #             interpretation = f"{chain_text} → Strong initiative and skill development."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate initiative indicators."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 2:
            #     if signified_houses:
            #         if wealth_connection >= 1:
            #             verdict = "STRONG"
            #             interpretation = f"{chain_text} → Good income/wealth potential."
            #         elif loss_connection >= 2:
            #             verdict = "WEAK"
            #             interpretation = f"{chain_text} → Income may face challenges."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate income indicators."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # elif house_num == 12:
            #     if signified_houses:
            #         if foreign_connection >= 1 and (service_connection >= 1 or business_connection >= 1):
            #             verdict = "FOREIGN_LINK"
            #             interpretation = f"{chain_text} → Foreign career connection indicated."
            #         elif loss_connection >= 2:
            #             verdict = "CHALLENGING"
            #             interpretation = f"{chain_text} → Losses or separations possible."
            #         else:
            #             verdict = "MODERATE"
            #             interpretation = f"{chain_text} → Moderate 12th house influence."
            #     else:
            #         verdict = "UNCLEAR"
            #         interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # Store structured data
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings.get(house_num, "General"),
                "csl": csl,
                "csl_flavor": flavor,
                "nakshatra": nakshatra_name,
                "star_lord": star_lord,
                "signified_houses": sorted(signified_houses),
                "signified_score": signified_score,
                # "service_connection": service_connection,
                # "business_connection": business_connection,
                # "wealth_connection": wealth_connection,
                # "foreign_connection": foreign_connection,
                # "loss_connection": loss_connection,
                "service_strength": service_strength,
                "business_strength": business_strength,
                "cusp_sign": cusp_sign,
                "is_benefic": is_benefic,
                "is_malefic": is_malefic,
                "verdict": verdict,
                "interpretation": interpretation,
                "chain": f"{csl} → {star_lord} star → houses {sorted(signified_houses) if signified_houses else 'UNAVAILABLE'}",
                "has_significations": bool(signified_houses)
            }
            
            # Add to key findings
            if signified_houses:
                kp_data["key_findings"].append(
                    f"House {house_num} ({house_meanings.get(house_num, 'General')}): "
                    f"{csl} → {star_lord} star → signifies {sorted(signified_houses)} → {verdict}"
                )
            else:
                kp_data["key_findings"].append(
                    f"House {house_num}: {csl} → ⚠️ significations MISSING → {verdict}"
                )
        
        # Overall verdict
        if kp_data["csl_details"]:
            h10_detail = kp_data["csl_details"].get(10, {})
            h6_detail = kp_data["csl_details"].get(6, {})
            h7_detail = kp_data["csl_details"].get(7, {})
            
            h10_verdict = h10_detail.get("verdict", "UNKNOWN")
            h6_verdict = h6_detail.get("verdict", "UNKNOWN")
            h7_verdict = h7_detail.get("verdict", "UNKNOWN")
            
            if h6_verdict == "SERVICE_FAVORABLE" and h7_verdict != "BUSINESS_FAVORABLE":
                overall = "SERVICE_PATH_DOMINANT"

            elif h7_verdict == "BUSINESS_FAVORABLE" and h6_verdict != "SERVICE_FAVORABLE":
                overall = "BUSINESS_PATH_DOMINANT"

            elif h6_verdict == "SERVICE_FAVORABLE" and h7_verdict == "BUSINESS_FAVORABLE":
                overall = "HYBRID_PATH_SUITABLE"

            elif "CHALLENGING" in {h10_verdict, h6_verdict, h7_verdict}:
                overall = "CAREER_CHALLENGES_INDICATED"

            else:
                overall = "MODERATE_CAREER_CHANGE_POTENTIAL"

            kp_data["overall_verdict"] = overall
        
        return kp_data

    def _extract_lagna_info(
        self,
        houses: List[Dict],
        planets: Dict[str, Dict]
    ) -> Optional[Dict]:
        """Extract lagna (ascendant) information from houses data."""
        try:
            house_1 = next((h for h in houses if h.get("house") == 1), None)
            
            if not house_1:
                return None
            
            lagna_sign = (
                house_1.get("sign") or 
                house_1.get("start_rasi") or 
                house_1.get("rasi") or
                ""
            )
            
            if not lagna_sign:
                return None
            
            lagna_lord_name = (
                house_1.get("rashi_lord") or
                house_1.get("sign_lord") or
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
                except:
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

    def _is_kp_point(self, point: str) -> bool:
        """Check if a point is KP-related"""
        kp_keywords = [
            'cusp', 'csl', 'sub-lord', 'sub lord',
            'signif', 'connects to', 'ruling planet',
            'kp', 'connects', 'promise', '10th', '6th', '7th'
        ]
        point_lower = point.lower()
        return any(kw in point_lower for kw in kp_keywords)

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log exactly what data is present in result"""
        logger.info("🧩 RESULT BREAKDOWN START")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        kp_points = [p for p in points if self._is_kp_point(p)]

        logger.info("📌 RESULT.POINTS SUMMARY")
        logger.info(f"  Total points  : {len(points)}")
        logger.info(f"  KP points     : {len(kp_points)}")

        ad = result.additional_data or {}

        logger.info("📦 RESULT.ADDITIONAL_DATA KEYS")
        for k in sorted(ad.keys()):
            logger.info(f"  - {k}")

        if "kp_career_change_analysis" in ad:
            kp = ad["kp_career_change_analysis"]
            logger.info("  ✅ kp_career_change_analysis PRESENT")
            logger.info(f"     has_kp_data: {kp.get('has_kp_data')}")
            logger.info(f"     overall_verdict: {kp.get('overall_verdict')}")

        if "career_change_suitability_matrix" in ad:
            matrix = ad["career_change_suitability_matrix"]
            logger.info(f"  ✅ career_change_suitability_matrix PRESENT ({len(matrix)} types)")

        if "service_vs_business" in ad:
            svb = ad["service_vs_business"]
            logger.info("  ✅ service_vs_business PRESENT")
            logger.info(f"     final_path: {svb.get('final_path')}")

        if "career_timing_windows" in ad:
            tw = ad["career_timing_windows"]
            logger.info("  ✅ career_timing_windows PRESENT")

        logger.info("🧩 RESULT BREAKDOWN END")

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

        # Choose Data Source
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

        # Get Question-Specific Houses
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
            all_relevant_houses.add(1)
        else:
            all_relevant_houses = {1, 2, 3, 6, 7, 9, 10, 11, 12}
            primary_houses = {10, 6, 7}
            secondary_houses = {2, 3, 9, 11, 12}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Career Changes")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        if isinstance(meta_query_type, str):
            meta_query_type = meta_query_type.upper()
        elif hasattr(meta_query_type, "name"):
            meta_query_type = meta_query_type.name

        logger.info("=" * 80)
        logger.info("CAREER CHANGES EVALUATOR (ENHANCED v4.0)")
        logger.info("=" * 80)
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info("=" * 80)

        # Calculate Aspects
        detect_aspects(analysis_planets)
        detect_aspects(planets)
        
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # Extract House Lords Data
        house_lords_info = self._extract_house_lords(
            analysis_houses, 
            analysis_planets, 
            all_relevant_houses,
            primary_houses
        )

        # Extract Lagna Information
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        # Extract Aspects on Houses
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        # KP CAREER CORE FACTS
        service_vs_business = {}
        try:
            service_vs_business = determine_service_vs_business(planets, houses)
            result.additional_data["service_vs_business"] = service_vs_business
        except Exception as e:
            logger.warning(f"KP career core evaluation failed: {e}")

        # CAREER ROLE RESONANCE
        career_roles = {}
        try:
            career_roles = evaluate_service_profession(
                planets,
                houses,
                KP_PROFESSION_MAP
            )
            result.additional_data["career_role_resonance"] = {
                "roles": career_roles.get("final_professions", []),
                "career_category": career_roles.get("career_category"),
                "career_direction": career_roles.get("career_direction"),
                "confidence": career_roles.get("confidence"),
                "context_tags": career_roles.get("context_tags", []),
                "planet_chain": career_roles.get("planet_chain", []),
            }
        except Exception as e:
            logger.warning(f"Career role evaluation failed: {e}")

        # FOREIGN CAREER EXPOSURE
        foreign_exposure = {}
        try:
            planet_chain = career_roles.get("planet_chain", []) if career_roles else None
            foreign_exposure = evaluate_foreign_career_exposure(
                planets, houses, planet_chain
            )
            result.additional_data["foreign_career_exposure"] = foreign_exposure
        except Exception as e:
            logger.warning(f"Foreign exposure evaluation failed: {e}")

        # Extract Timing Windows
        timing_windows_raw = kwargs.get("timing_windows", {})
        
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            if not timing_windows_list and "Career Shift Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Career Shift Timing"]
            if not timing_windows_list and "Career Changes" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Career Changes"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
        
        timing_windows_data = {}
        if meta_query_type == "TIMING":
            timing_windows_data = self._extract_timing_windows(timing_windows_list)

        # Add House Analysis Points
        if sub_subdomain in {"Career Shift Timing"}:
            self._add_house_analysis_points(
                result, 
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # KP EVALUATION WITH STRUCTURED EXTRACTION + MATRIX
        if sub_subdomain in {"Career Shift Timing", "Career Changes"}:
            try:
                kp_structured = self._extract_kp_career_change_structured_direct(planets, houses)
                result.additional_data["kp_career_change_analysis"] = kp_structured
                
                if kp_structured.get("has_kp_data"):
                    try:
                        career_change_matrix = self._create_career_change_suitability_matrix(
                            kp_analysis=kp_structured,
                            service_vs_business=service_vs_business,
                            foreign_exposure=foreign_exposure,
                            career_roles=career_roles
                        )
                        result.additional_data["career_change_suitability_matrix"] = career_change_matrix
                    except Exception as e:
                        logger.error(f"❌ Error creating career change matrix: {e}")

            except Exception as e:
                logger.warning(f"Career change evaluation error: {e}")

        # LLM-ONLY QUESTIONS
        if sub_subdomain in {"Career Shift Advice", "Career Challenges"}:
            result.add_point(
                "This question is evaluated using experience, skill alignment, "
                "and practical decision-making rather than predictive astrology."
            )

        # CAREER SHIFT SUITABILITY + TIMING
        if sub_subdomain == "Career Shift Timing":
            try:
                career_path = service_vs_business.get("final_path")
                career_shift = service_vs_business.get("career_shift_likelihood")

                if career_path:
                    result.add_point(
                        f"KP: Dominant career inclination: **{career_path}**."
                    )

                if career_shift == "Yes":
                    result.add_point(
                        "KP: Chart supports a meaningful career transition."
                    )
                else:
                    result.add_point(
                        "KP: Gradual change advised over abrupt transition."
                    )

            except Exception as e:
                logger.warning(f"Career path evaluation error: {e}")

            if meta_query_type == "TIMING":
                try:
                    timing_rules = TIMING_RULES.get("Career Shift Timing", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    positive_planets = get_positive_planets(planet_scores)

                    if positive_planets:
                        result.add_point(
                            f"KP: Favorable dasha lords: {', '.join(positive_planets[:4])}."
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.add_point(
                            f"KP: Ruling planets supporting transition: {', '.join(ruling_planets[:4])}."
                        )

                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")

        elif sub_subdomain == "Career Remedies":
            result.add_point(
                "Career remedies focus on strengthening planets governing "
                "career stability, confidence, and decision clarity."
            )

        # Store Enhanced Data for LLM
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            kwargs.get("current_dasha"),
            kwargs.get("dasha_timeline")
        )

        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        if hasattr(self, 'points') and self.points:
            for point in self.points:
                result.add_point(point)

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
                
                result = {
                    'start': get_attr(w, 'start'),
                    'end': get_attr(w, 'end'),
                    'dasha': get_attr(w, 'dasha'),
                    'score': get_attr(w, 'score'),
                    'transit_score': get_attr(w, 'transit_score'),
                    'final_score': get_attr(w, 'final_score'),
                    'age_at_start': get_attr(w, 'age_at_start'),
                }
                
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                
                return result
            
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
            
            lord_name = (
                h.get("rashi_lord") or
                h.get("sign_lord") or
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
                            normalized_lord, lord_data, dignity
                        )
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
        """Get house meaning for career context."""
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
        current_dasha: dict = None,
        dasha_timeline: dict = None
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
            },
            
            "current_dasha": current_dasha,
            "dasha_timeline": dasha_timeline,
        })
        
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")

    # --------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="CAR_CC_1",
                question=(
                    "What is the right career path for me and when would be the most "
                    "favorable time to switch careers?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Career Shift Timing"
            ),
            Question(
                id="CAR_CC_2",
                question=(
                    "Should I pursue further education or make other mid-life adaptations "
                    "to enhance my professional growth?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Career Shift Advice"
            ),
            Question(
                id="CAR_CC_3",
                question=(
                    "What obstacles might I face in this transition and how can I overcome them?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Career Challenges"
            )
        ]
"""
Attracting Love Evaluator - ENHANCED VERSION v4.0

Based on ProspectsOfInvestmentsEvaluator v3.3, CareerDiscoveryAndEmploymentEvaluator v4.0,
and StartingNewBusinessEvaluator v4.0 architecture.

ENHANCEMENTS (Matching Finance/Career/Business Evaluator):
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ KP love engine integration (preserved)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP significations using correct hierarchy (sub > star > occupy > own)
✅ Love/Relationship suitability matrix with correct planet mapping
✅ Lagna lord analysis for relationship personality
✅ Compatibility analysis (7th house focus)
✅ Foreign partner/relationship exposure analysis

Covers:
1) Will I find love and when is it likely to happen?
2) What type of partner is best suited for me?
3) Love remedies and relationship improvement

Key Houses for Love:
- 5th: Romance, attraction, creativity (PRIMARY)
- 7th: Partnership, marriage, commitment (PRIMARY)
- 1st: Self, personality, appearance
- 11th: Hopes, fulfillment, social circles
- 2nd: Family, values, speech
- 8th: Intimacy, transformation, hidden matters
- 12th: Hidden affairs, losses, foreign connections
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
    get_planet,
    get_cusp_sub_lord,
    kp_check_promise,
    get_signified_houses,
    _has_evil_aspect
)

from app.domains.excel_structure_config import get_houses_for_question

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


class AttractingLoveEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Love Relationship → Attracting Love
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Dual data source support (KP + Vedic)
    - Timing windows extraction and formatting
    - KP significations with correct hierarchy
    - Love/Relationship suitability matrix
    - Compatibility analysis
    """

    domain = "Love_Relationship"
    subtopic = "Attracting Love"
    
    # Love-specific houses
    LOVE_HOUSES = {1, 2, 5, 7, 8, 11, 12}
    
    # House meanings for love context
    HOUSE_MEANINGS = {
        1: "Self/Personality",
        2: "Family/Values",
        5: "Romance/Attraction",
        7: "Partnership/Relationship",
        8: "Intimacy/Transformation",
        11: "Hopes/Fulfillment",
        12: "Hidden Affairs/Foreign"
    }

    def _calculate_age(self, dob_str: str) -> Optional[int]:
        """
        Calculate current age from DOB string (YYYY-MM-DD or DD/MM/YYYY).
        Uses UTC for consistency.
        """
        if not dob_str:
            return None

        try:
            # Try ISO first
            if "-" in dob_str:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
            elif "/" in dob_str:
                dob = datetime.strptime(dob_str, "%d/%m/%Y")
            else:
                return None

            today = datetime.utcnow()
            age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            return age
        except Exception:
            return None

    def _create_love_suitability_matrix(
        self,
        kp_analysis: Dict,
        vedic_lords: Dict = None,
        lagna_lord_analysis: Dict = None,
        kp_love: Dict = None
    ) -> Dict[str, Dict]:
        """
        Create love/relationship suitability matrix based on KP analysis.
        
        Maps KP significations to relationship types and outcomes.
        """
        matrix = {}
        
        csl_details = kp_analysis.get("csl_details", {})
        h5_detail = csl_details.get(5, {})
        h7_detail = csl_details.get(7, {})
        h11_detail = csl_details.get(11, {})
        h1_detail = csl_details.get(1, {})
        h8_detail = csl_details.get(8, {})
        h12_detail = csl_details.get(12, {})
        
        h5_verdict = h5_detail.get("verdict", "UNKNOWN")
        h7_verdict = h7_detail.get("verdict", "UNKNOWN")
        h11_verdict = h11_detail.get("verdict", "UNKNOWN")
        h1_verdict = h1_detail.get("verdict", "UNKNOWN")
        
        h5_csl = h5_detail.get("csl")
        h7_csl = h7_detail.get("csl")
        h5_star_lord = h5_detail.get("star_lord")
        h7_star_lord = h7_detail.get("star_lord")
        
        # Get KP love scores if available
        promise = kp_love.get("promise", False) if kp_love else False
        attraction_score = kp_love.get("attraction_score", 0) if kp_love else 0
        compatibility_score = kp_love.get("compatibility_score", 0) if kp_love else 0
        breakup_risk = kp_love.get("breakup_risk", 0) if kp_love else 0
        
        # Planet categories for relationships
        romantic_planets = {"Venus", "Moon", "Jupiter"}
        passionate_planets = {"Mars", "Rahu"}
        stable_planets = {"Saturn", "Jupiter", "Sun"}
        
        # ═══════════════════════════════════════════════════════════
        # 1. LOVE MARRIAGE
        # ═══════════════════════════════════════════════════════════
        love_marriage_indicators = 0
        love_marriage_reasons = []
        
        if h5_verdict in ["STRONG", "EXCELLENT", "FAVORABLE"]:
            love_marriage_indicators += 2
            love_marriage_reasons.append("5th house (romance) strongly placed")
        
        if h7_verdict in ["STRONG", "EXCELLENT"]:
            love_marriage_indicators += 1
            love_marriage_reasons.append("7th house (partnership) supports commitment")
        
        if promise:
            love_marriage_indicators += 2
            love_marriage_reasons.append("KP confirms love promise")
        
        if attraction_score > 2:
            love_marriage_indicators += 1
            love_marriage_reasons.append("High attraction score in chart")
        
        if love_marriage_indicators >= 4:
            rating = "HIGH"
        elif love_marriage_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Love Marriage"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(love_marriage_reasons) if love_marriage_reasons else "Mixed indicators for love marriage"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 2. ARRANGED MARRIAGE
        # ═══════════════════════════════════════════════════════════
        arranged_indicators = 0
        arranged_reasons = []
        
        if h7_verdict in ["STRONG", "EXCELLENT"] and h5_verdict not in ["STRONG"]:
            arranged_indicators += 2
            arranged_reasons.append("Strong 7th house without dominant 5th - family-led union")
        
        if h7_csl in stable_planets:
            arranged_indicators += 1
            arranged_reasons.append(f"7th CSL {h7_csl} favors stable, traditional approach")
        
        if h5_verdict in ["WEAK", "CHALLENGING"]:
            arranged_indicators += 1
            arranged_reasons.append("5th house challenges suggest arranged path better")
        
        if arranged_indicators >= 3:
            rating = "HIGH"
        elif arranged_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Arranged Marriage"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(arranged_reasons) if arranged_reasons else "Love marriage may be more suitable"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 3. LONG-TERM RELATIONSHIP
        # ═══════════════════════════════════════════════════════════
        if h7_csl in stable_planets or h7_star_lord in stable_planets:
            rating = "HIGH"
            reason = f"Stable planets ({h7_csl or h7_star_lord}) influencing 7th house"
        elif h7_verdict in ["STRONG", "MODERATE"] and breakup_risk > -3:
            rating = "MODERATE"
            reason = "Partnership house reasonably placed, moderate stability"
        else:
            rating = "LOW"
            reason = "Short-term or multiple relationships more likely"
        
        matrix["Long-Term Relationship"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 4. PASSIONATE / INTENSE ROMANCE
        # ═══════════════════════════════════════════════════════════
        if h5_csl in passionate_planets or h8_detail.get("verdict") in ["STRONG"]:
            rating = "HIGH"
            reason = "Mars/Rahu influence or strong 8th house indicates intense passion"
        elif h5_csl in romantic_planets:
            rating = "MODERATE"
            reason = "Romantic planets bring passion with softness"
        else:
            rating = "LOW"
            reason = "Calm, steady relationship style indicated"
        
        matrix["Passionate / Intense Romance"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 5. ONLINE / MODERN DATING
        # ═══════════════════════════════════════════════════════════
        online_indicators = 0
        online_reasons = []
        
        # Check for Rahu connection
        rahu_connected = any(
            detail.get("csl") == "Rahu" or detail.get("star_lord") == "Rahu"
            for detail in csl_details.values()
        )
        if rahu_connected:
            online_indicators += 2
            online_reasons.append("Rahu connection supports unconventional/modern meeting")
        
        if h5_csl in {"Mercury", "Rahu"}:
            online_indicators += 1
            online_reasons.append(f"5th CSL {h5_csl} supports digital/communication-based romance")
        
        if h11_verdict in ["STRONG", "EXCELLENT"]:
            online_indicators += 1
            online_reasons.append("11th house (social networks) strong")
        
        if online_indicators >= 3:
            rating = "HIGH"
        elif online_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Online / Modern Dating"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(online_reasons) if online_reasons else "Traditional meeting methods may be better"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 6. FOREIGN / DIFFERENT CULTURE PARTNER
        # ═══════════════════════════════════════════════════════════
        foreign_indicators = 0
        foreign_reasons = []
        
        if h12_detail.get("verdict") in ["STRONG", "MODERATE"]:
            foreign_indicators += 2
            foreign_reasons.append("12th house connection indicates foreign partner potential")
        
        if rahu_connected:
            foreign_indicators += 1
            foreign_reasons.append("Rahu supports unconventional/foreign connections")
        
        h9_detail = csl_details.get(9, {})
        if h9_detail.get("verdict") in ["STRONG"]:
            foreign_indicators += 1
            foreign_reasons.append("9th house (foreign/luck) supports cross-cultural romance")
        
        if foreign_indicators >= 3:
            rating = "HIGH"
        elif foreign_indicators >= 2:
            rating = "MODERATE"
        else:
            rating = "LOW"
        
        matrix["Foreign / Different Culture Partner"] = {
            "rating": rating,
            "kp_reasoning": " | ".join(foreign_reasons) if foreign_reasons else "Partner likely from same cultural background"
        }
        
        # ═══════════════════════════════════════════════════════════
        # 7. WORKPLACE / PROFESSIONAL SETTING
        # ═══════════════════════════════════════════════════════════
        h10_detail = csl_details.get(10, {})
        if h10_detail.get("verdict") in ["STRONG"] and h7_verdict in ["STRONG"]:
            rating = "HIGH"
            reason = "10th and 7th house connection suggests professional meeting"
        elif h10_detail.get("csl") in romantic_planets:
            rating = "MODERATE"
            reason = "Career planet has romantic influence"
        else:
            rating = "LOW"
            reason = "Social/personal settings more likely for meeting partner"
        
        matrix["Workplace / Professional Setting"] = {"rating": rating, "kp_reasoning": reason}
        
        # ═══════════════════════════════════════════════════════════
        # 8. FRIENDSHIP TO ROMANCE
        # ═══════════════════════════════════════════════════════════
        if h11_verdict in ["STRONG", "EXCELLENT"] and h5_verdict in ["STRONG"]:
            rating = "HIGH"
            reason = "Strong 11th (friendship) and 5th (romance) connection"
        elif h11_csl := csl_details.get(11, {}).get("csl"):
            if h11_csl in romantic_planets:
                rating = "MODERATE"
                reason = f"11th CSL {h11_csl} bridges friendship to romance"
            else:
                rating = "LOW"
                reason = "Direct romantic approach may be better"
        else:
            rating = "LOW"
            reason = "Direct romantic approach may be better"
        
        matrix["Friendship to Romance"] = {"rating": rating, "kp_reasoning": reason}
        
        return matrix

    def _extract_kp_love_structured_direct(self, planets: Dict, houses: List) -> Dict:
        """
        Extract structured KP love data using CORRECT KP methodology:
        CSL → Star Lord → Significations (NOT just CSL planet nature!)
        
        Similar to finance/career/business extractors but for love houses.
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
        
        # Love-relevant houses
        love_houses = [1, 2, 5, 7, 8, 11, 12]
        house_meanings = {
            1: "Self/Personality",
            2: "Family/Values",
            5: "Romance/Attraction",
            7: "Partnership/Relationship",
            8: "Intimacy/Transformation",
            11: "Hopes/Fulfillment",
            12: "Hidden Affairs/Foreign"
        }
        
        # House groups for signification analysis
        ROMANCE_HOUSES = {5, 7, 11}
        MARRIAGE_HOUSES = {2, 7, 11}
        OBSTACLE_HOUSES = {6, 8, 12}
        POSITIVE_HOUSES = {1, 2, 5, 7, 9, 11}
        
        # Extract CSL for each love house
        for house_num in love_houses:
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
                    signified_houses = set(get_signified_houses(star_lord, planets, houses))
                    signified_score = get_signified_score(star_lord, planets, houses)
                    
                    if signified_houses:
                        logger.info(f"✅ House {house_num}: CSL {csl} → {nakshatra_name} (Star Lord {star_lord}) → Signifies {sorted(signified_houses)}")
                    else:
                        logger.warning(f"⚠️ House {house_num}: Star lord {star_lord} has EMPTY significations - using star lord house position fallback")
                        star_lord_obj = planets.get(star_lord, {})
                        if star_lord_obj:
                            star_lord_house = star_lord_obj.get("house")
                            if star_lord_house:
                                signified_houses = {star_lord_house}
                                logger.warning(f"⚠️ Fallback: Using star lord house {star_lord_house} for {star_lord}")
                    
                except Exception as e:
                    logger.error(f"❌ Error getting significations for {star_lord}: {e}")
                    star_lord_obj = planets.get(star_lord, {})
                    if star_lord_obj:
                        star_lord_house = star_lord_obj.get("house")
                        if star_lord_house:
                            signified_houses = {star_lord_house}
                            logger.warning(f"⚠️ Exception fallback: Using star lord house {star_lord_house}")
            
            elif star_lord:
                logger.warning(f"⚠️ No signification helpers - using star lord house position for {star_lord}")
                star_lord_obj = planets.get(star_lord, {})
                if star_lord_obj:
                    star_lord_house = star_lord_obj.get("house")
                    if star_lord_house:
                        signified_houses = {star_lord_house}
                        logger.warning(f"⚠️ Using star lord house {star_lord_house} for CSL {csl}")
            
            if not signified_houses:
                logger.error(f"❌ CRITICAL: No significations available for house {house_num} CSL {csl} - analysis will be INCOMPLETE")
                signified_houses = set()
            
            # Step 3: Analyze significations
            romance_connection = len(signified_houses & ROMANCE_HOUSES)
            marriage_connection = len(signified_houses & MARRIAGE_HOUSES)
            obstacle_connection = len(signified_houses & OBSTACLE_HOUSES)
            positive_connection = len(signified_houses & POSITIVE_HOUSES)
            
            # Get signification strength scores
            romance_strength = sum(signified_score.get(h, 0) for h in ROMANCE_HOUSES)
            marriage_strength = sum(signified_score.get(h, 0) for h in MARRIAGE_HOUSES)
            
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
            
            # House-specific verdicts based on SIGNIFICATIONS
            if house_num == 5:  # Romance/Attraction house (MOST IMPORTANT)
                if signified_houses:
                    if romance_connection >= 2 or romance_strength >= 4:
                        verdict = "STRONG"
                        interpretation = (
                            f"{chain_text} → Strong romance capacity through {sorted(ROMANCE_HOUSES & signified_houses)} connection. "
                            f"{'Benefic nature adds charm.' if is_benefic else 'Despite malefic nature, significations promise romance.'}"
                        )
                    elif marriage_connection >= 2:
                        verdict = "MARRIAGE_ORIENTED"
                        interpretation = (
                            f"{chain_text} → 5th house leans toward commitment rather than casual dating. "
                            f"Serious relationships favored."
                        )
                    elif obstacle_connection >= 2:
                        verdict = "CHALLENGING"
                        interpretation = (
                            f"{chain_text} → Romance challenges through {sorted(OBSTACLE_HOUSES & signified_houses)} "
                            f"(obstacles/delays). Patience required."
                        )
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate romance capacity."
                else:
                    verdict = "UNCLEAR"
                    interpretation = (
                        f"{chain_text} → ⚠️ WARNING: Significations unavailable. "
                        f"Cannot make definitive KP analysis for romance."
                    )
            
            elif house_num == 7:  # Partnership/Relationship house
                if signified_houses:
                    if marriage_connection >= 2:
                        verdict = "EXCELLENT"
                        interpretation = f"{chain_text} → Strong partnership/marriage indicators."
                    elif romance_connection >= 2:
                        verdict = "LOVE_TO_MARRIAGE"
                        interpretation = f"{chain_text} → Love relationship likely to convert to marriage."
                    elif obstacle_connection >= 2:
                        verdict = "DELAYED"
                        interpretation = f"{chain_text} → Partnership may face delays or obstacles."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate partnership indicators."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable. Partnership path unclear."
            
            elif house_num == 11:  # Hopes/Fulfillment house
                if signified_houses:
                    if positive_connection >= 2 or romance_connection >= 2:
                        verdict = "FAVORABLE"
                        interpretation = f"{chain_text} → Good fulfillment of romantic hopes."
                    elif obstacle_connection >= 2:
                        verdict = "WEAK"
                        interpretation = f"{chain_text} → Fulfillment of love wishes may be delayed."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate fulfillment potential."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            elif house_num == 1:  # Self/Personality house
                if signified_houses:
                    if romance_connection >= 1:
                        verdict = "ATTRACTIVE"
                        interpretation = f"{chain_text} → Natural romantic appeal and charm."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate natural appeal."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            elif house_num == 8:  # Intimacy/Transformation house
                if signified_houses:
                    if 8 in signified_houses and romance_connection >= 1:
                        verdict = "INTENSE"
                        interpretation = f"{chain_text} → Deep, transformative relationships indicated."
                    elif obstacle_connection >= 2:
                        verdict = "CHALLENGING"
                        interpretation = f"{chain_text} → Intimacy challenges or trust issues possible."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate intimacy indicators."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            elif house_num == 12:  # Hidden affairs/Foreign
                if signified_houses:
                    if 12 in signified_houses and romance_connection >= 1:
                        verdict = "FOREIGN_LINK"
                        interpretation = f"{chain_text} → Foreign partner or unconventional romance possible."
                    elif obstacle_connection >= 2:
                        verdict = "SECRETIVE"
                        interpretation = f"{chain_text} → Hidden or secretive relationship patterns."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate 12th house influence."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            elif house_num == 2:  # Family/Values house
                if signified_houses:
                    if marriage_connection >= 1:
                        verdict = "FAMILY_SUPPORTIVE"
                        interpretation = f"{chain_text} → Family support for relationships."
                    else:
                        verdict = "MODERATE"
                        interpretation = f"{chain_text} → Moderate family support."
                else:
                    verdict = "UNCLEAR"
                    interpretation = f"{chain_text} → ⚠️ Significations unavailable."
            
            # Store structured data
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings.get(house_num, "General"),
                "csl": csl,
                "csl_flavor": flavor,
                "nakshatra": nakshatra_name,
                "star_lord": star_lord,
                "signified_houses": sorted(signified_houses),
                "signified_score": signified_score,
                "romance_connection": romance_connection,
                "marriage_connection": marriage_connection,
                "obstacle_connection": obstacle_connection,
                "positive_connection": positive_connection,
                "romance_strength": romance_strength,
                "marriage_strength": marriage_strength,
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
                    f"House {house_num} ({house_meanings.get(house_num, 'General')}): "
                    f"{csl} → {star_lord} star → ⚠️ significations MISSING → {verdict} (incomplete)"
                )
        
        # Overall verdict
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
            h5_detail = kp_data["csl_details"].get(5, {})
            h7_detail = kp_data["csl_details"].get(7, {})
            h11_detail = kp_data["csl_details"].get(11, {})
            
            h5_verdict = h5_detail.get("verdict", "UNKNOWN")
            h7_verdict = h7_detail.get("verdict", "UNKNOWN")
            h11_verdict = h11_detail.get("verdict", "UNKNOWN")
            
            # Overall verdict
            if h5_verdict == "STRONG" and h7_verdict in ["EXCELLENT", "LOVE_TO_MARRIAGE"]:
                kp_data["overall_verdict"] = "EXCELLENT_FOR_LOVE"
            elif h5_verdict == "CHALLENGING" or h7_verdict == "DELAYED":
                kp_data["overall_verdict"] = "LOVE_CHALLENGES_INDICATED"
            elif h5_verdict == "STRONG" and h11_verdict == "FAVORABLE":
                kp_data["overall_verdict"] = "STRONG_LOVE_WITH_FULFILLMENT"
            elif h7_verdict == "EXCELLENT":
                kp_data["overall_verdict"] = "MARRIAGE_FAVORABLE"
            else:
                kp_data["overall_verdict"] = "MODERATE_LOVE_POTENTIAL"
        
        return kp_data

    def _is_kp_point(self, point: str) -> bool:
        """Check if a point is KP-related"""
        kp_keywords = [
            'cusp', 'csl', 'sub-lord', 'sub lord',
            'signif', 'connects to', 'ruling planet',
            'kp', 'connects', 'promise', '5th', '7th'
        ]
        point_lower = point.lower()
        return any(kw in point_lower for kw in kp_keywords)

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
        dob = kwargs.get("dob")
        age = self._calculate_age(dob)
        is_minor = age is not None and age < 18

        logger.info(f"🔍 DOB: {dob} | Age: {age} | Minor: {is_minor}")

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
            # Love-specific fallback houses
            all_relevant_houses = {1, 2, 5, 7, 8, 11, 12}
            primary_houses = {5, 7}
            secondary_houses = {1, 2, 8, 11, 12}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Attracting Love")
        gender: str = kwargs.get("gender", "male")

        # Handle both dict and QueryMeta object
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        # Normalize meta_query_type
        if isinstance(meta_query_type, str):
            meta_query_type = meta_query_type.upper()
        elif hasattr(meta_query_type, "name"):
            meta_query_type = meta_query_type.name

        logger.info("=" * 80)
        logger.info("ATTRACTING LOVE EVALUATOR (ENHANCED v4.0 - COMPLETE)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Gender: {gender}")
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
            
            # Fallback: try "Finding Love" key
            if not timing_windows_list and "Finding Love" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Finding Love"]
                logger.info(f"🔍 DEBUG: Using 'Finding Love' fallback key, found {len(timing_windows_list)} windows")
            
            # Another fallback: try "Attracting Love"
            if not timing_windows_list and "Attracting Love" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Attracting Love"]
                logger.info(f"🔍 DEBUG: Using 'Attracting Love' fallback key, found {len(timing_windows_list)} windows")
        else:
            # Treat as list directly
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")
        
        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = {}
        if meta_query_type == "TIMING":
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
        # STEP 6: Add House Analysis Points (Vedic - love questions)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Attracting Love", "Finding Love", "Love Prospects"}:
            self._add_house_analysis_points(
                result, 
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ═══════════════════════════════════════════════════════
        # STEP 7: KP LOVE ENGINE (PRESERVED - DO NOT MODIFY!)
        # ═══════════════════════════════════════════════════════
        kp_love = self._evaluate_love_life(
            planets=planets,
            houses=houses,
            gender=gender
        )

        for p in kp_love.get("points", []):
            result.add_point(p)

        if kp_love["promise"]:
            result.add_point(f"KP: 💖 Love is promised. {kp_love['summary']}")
            result.promise_state = "promised"
        else:
            result.add_point(f"KP: 💔 Love prospects are challenging. {kp_love['summary']}")
            result.promise_state = "blocked"

        # Store KP love data
        result.additional_data["love_kp_engine"] = kp_love

        # ═══════════════════════════════════════════════════════
        # STEP 8: KP EVALUATION (ENHANCED WITH STRUCTURED EXTRACTION + LOVE MATRIX)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Attracting Love", "Finding Love", "Love Prospects"}:
            try:
                # ✅ Extract structured KP data directly from cusps
                kp_structured = self._extract_kp_love_structured_direct(planets, houses)

                # ✅ Store structured KP data in additional_data
                result.additional_data["kp_love_analysis"] = kp_structured
                
                if kp_structured.get("has_kp_data"):
                    logger.info(f"✅ Structured KP love data extracted:")
                    logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
                    logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
                    for house_num, info in kp_structured["csl_details"].items():
                        logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
                    
                    # ═══════════════════════════════════════════════════════════
                    # CREATE LOVE SUITABILITY MATRIX (NEW!)
                    # ═══════════════════════════════════════════════════════════
                    try:
                        love_matrix = self._create_love_suitability_matrix(
                            kp_analysis=kp_structured,
                            vedic_lords=house_lords_info if house_lords_info else None,
                            lagna_lord_analysis=lagna_info,
                            kp_love=kp_love
                        )
                        
                        result.additional_data["love_suitability_matrix"] = love_matrix
                        
                        logger.info(f"✅ Love suitability matrix created with {len(love_matrix)} relationship types")
                        for love_type, details in love_matrix.items():
                            logger.info(f"   {love_type}: {details['rating']}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error creating love matrix: {e}")
                        import traceback
                        logger.error(traceback.format_exc())

                    # After kp_structured is built, derive a unified love verdict
                    if kp_structured.get("has_kp_data"):
                        h5_verdict = kp_structured["csl_details"].get(5, {}).get("verdict", "UNKNOWN")
                        h7_verdict = kp_structured["csl_details"].get(7, {}).get("verdict", "UNKNOWN")
                        h11_verdict = kp_structured["csl_details"].get(11, {}).get("verdict", "UNKNOWN")
                        
                        result.additional_data["unified_love_verdict"] = {
                            "primary_verdict": kp_structured.get("overall_verdict"),
                            "promise": kp_love.get("promise", False),
                            "h5_status": h5_verdict,
                            "h7_status": h7_verdict,
                            "h11_status": h11_verdict,
                            "kp_engine_score": kp_love.get("score", 0),
                            "attraction_score": kp_love.get("attraction_score", 0),
                            "breakup_risk": kp_love.get("breakup_risk", 0),
                        }
                else:
                    logger.warning("⚠️ No KP cusp sub lord data found for love")

            except Exception as e:
                logger.warning(f"Love evaluation error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Still try to extract KP data even if main evaluation fails
                try:
                    kp_structured = self._extract_kp_love_structured_direct(planets, houses)
                    result.additional_data["kp_love_analysis"] = kp_structured
                    
                    if kp_structured.get("has_kp_data"):
                        try:
                            love_matrix = self._create_love_suitability_matrix(
                                kp_analysis=kp_structured,
                                vedic_lords=None,
                                lagna_lord_analysis=None,
                                kp_love=kp_love
                            )
                            result.additional_data["love_suitability_matrix"] = love_matrix
                            logger.info(f"✅ Love matrix created (fallback path) with {len(love_matrix)} types")
                        except Exception as matrix_err:
                            logger.error(f"❌ Could not create love matrix in fallback: {matrix_err}")
                except Exception as kp_err:
                    logger.error(f"❌ Could not extract KP data in fallback: {kp_err}")

        # ═══════════════════════════════════════════════════════
        # STEP 9: TIMING LAYER (for TIMING queries)
        # ═══════════════════════════════════════════════════════
        if meta_query_type == "TIMING":
            if timing_windows_data and timing_windows_data.get('has_timing'):
                best = timing_windows_data.get('best_window', {})
                if best:
                    result.add_point(
                        f"🏆 Best timing for love: {best.get('dasha', 'N/A')} "
                        f"({best.get('start', 'N/A')} to {best.get('end', 'N/A')})"
                    )
            else:
                result.add_point(
                    "⏰ Love timing is sensitive; stronger windows may emerge in later periods."
                )

        # ═══════════════════════════════════════════════════════
        # STEP 10: Store Enhanced Data for LLM (including timing!)
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            kp_love,
            kwargs.get("current_dasha"),
            kwargs.get("dasha_timeline"),
            vedic_planets,
            vedic_houses
        )

        # Store lagna info
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # Add existing points from self.points to result
        if hasattr(self, 'points') and self.points:
            for point in self.points:
                result.add_point(point)

        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - FIXED VERSION!
    # ═══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow objects!
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
                """Convert TimingWindow object or dict to standardized dict format"""
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
                                   'md', 'ad', 'pd', 'maha', 'antara', 'paryantar',
                                   '_domain_score', '_delay_years', '_needs_resonant_jump']:
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
            
            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }
            
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

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """
        Log exactly what data is present in result.points and result.additional_data
        """
        logger.info("🧩 RESULT BREAKDOWN START")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        # POINTS ANALYSIS
        points = getattr(result, "points", []) or []

        kp_points = [p for p in points if p.startswith("KP:") or "KP" in p.upper()]
        vedic_points = [p for p in points if "💖" in p or "House" in p]

        logger.info("📌 RESULT.POINTS SUMMARY")
        logger.info(f"  Total points  : {len(points)}")
        logger.info(f"  KP points     : {len(kp_points)}")
        logger.info(f"  Vedic points  : {len(vedic_points)}")

        # FULL POINT DUMP
        logger.info("🧾 ALL RESULT POINTS (ORDER PRESERVED)")
        for idx, p in enumerate(points, 1):
            logger.info(f"  {idx:02d}. {p}")

        # ADDITIONAL DATA ANALYSIS
        ad = result.additional_data or {}

        logger.info("📦 RESULT.ADDITIONAL_DATA KEYS")
        for k in sorted(ad.keys()):
            logger.info(f"  - {k}")

        def safe_len(obj):
            try:
                return len(obj)
            except Exception:
                return "N/A"

        logger.info("📊 ADDITIONAL DATA BREAKDOWN")

        # KP LOVE ANALYSIS (NEW!)
        if "kp_love_analysis" in ad:
            kp = ad["kp_love_analysis"]
            logger.info("  ✅ KP kp_love_analysis PRESENT")
            logger.info(f"     has_kp_data: {kp.get('has_kp_data')}")
            logger.info(f"     overall_verdict: {kp.get('overall_verdict')}")
            logger.info(f"     houses analyzed: {list(kp.get('csl_details', {}).keys())}")

        # LOVE SUITABILITY MATRIX (NEW!)
        if "love_suitability_matrix" in ad:
            matrix = ad["love_suitability_matrix"]
            logger.info(f"  ✅ love_suitability_matrix PRESENT ({len(matrix)} relationship types)")
            for love_type, details in matrix.items():
                logger.info(f"     - {love_type}: {details['rating']}")

        # KP LOVE ENGINE
        if "love_kp_engine" in ad:
            kp_love = ad["love_kp_engine"]
            logger.info("  ✅ love_kp_engine PRESENT")
            logger.info(f"     promise: {kp_love.get('promise')}")
            logger.info(f"     attraction_score: {kp_love.get('attraction_score')}")
            logger.info(f"     compatibility_score: {kp_love.get('compatibility_score')}")

        # TIMING
        if "love_and_relationship_timing_windows" in ad:
            tw = ad["love_and_relationship_timing_windows"]
            logger.info("  ✅ KP/Dasha timing_windows PRESENT")
            logger.info(f"     has_timing: {tw.get('has_timing')}")
            if tw.get("best_window"):
                logger.info(f"     BEST dasha: {tw['best_window'].get('dasha')}")
            if tw.get("nearest_window"):
                logger.info(f"     NEAREST dasha: {tw['nearest_window'].get('dasha')}")

        # VEDIC STRUCTURES
        if "love_and_relationship_house_lords" in ad:
            logger.info(
                f"  ✅ VEDIC house_lords PRESENT "
                f"({safe_len(ad['love_and_relationship_house_lords'])} houses)"
            )

        if "love_and_relationship_house_aspects" in ad:
            logger.info(
                f"  ✅ VEDIC house_aspects PRESENT "
                f"({safe_len(ad['love_and_relationship_house_aspects'])} houses)"
            )

        # LAGNA INFO (NEW!)
        if "lagna_info" in ad:
            lagna = ad["lagna_info"]
            logger.info("  ✅ lagna_info PRESENT")
            logger.info(f"     lagna_sign: {lagna.get('lagna_sign')}")
            logger.info(f"     lagna_lord: {lagna.get('lagna_lord')}")

        logger.info("🧩 RESULT BREAKDOWN END")

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
            
            marker = "💖"
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
        """Get house meaning for love context."""
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
        kp_love: dict = None,
        current_dasha: dict = None,
        dasha_timeline: dict = None,
        vedic_planets: dict = None,
        vedic_houses: list = None
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "love_and_relationship"
        
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
            
            # KP Engine results (legacy)
            f"{domain_prefix}_kp_engine": kp_love,
            
            # Dasha data
            "current_dasha": current_dasha,
            "dasha_timeline": dasha_timeline,
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
    # KP LOVE ENGINE — ⚠️ DO NOT MODIFY ⚠️
    # --------------------------------------------------
    def _evaluate_love_life(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        gender: str
    ) -> Dict:
        """
        KP Astrology - LOVE EVALUATOR (v3 FINAL) — comprehensive love promise analysis.
        
        Uses detailed KP CSL analysis to determine:
        - Love promise vs. denial
        - Love-to-marriage connection
        - Breakup risks
        - Compatibility factors
        
        Returns:
            Dict with keys: promise (bool), score (int), summary (str), points (list),
                           attraction_score, breakup_risk, compatibility_score
        """
        from app.core.astro_constants import _is_benefic, _is_malefic
        
        score = {"attraction": 0, "breakup_risk": 0, "compatibility": 0, "outcome": 0}
        notes = []
        remedies = []
        points = []
        seen = set()
        
        def add(text):
            if text and text not in seen:
                points.append(text)
                seen.add(text)
        
        # -------------------------
        # Core sub-lord references
        # -------------------------
        sub_lord_7 = get_cusp_sub_lord(7, houses)
        p7 = get_planet(sub_lord_7, planets) if sub_lord_7 else None
        
        sub_lord_sign = None
        if p7:
            sub_lord_sign = (
                p7.get("rasi")
                or p7.get("sign")
                or p7.get("zodiac")
                or p7.get("pseudo_rasi")
            )
        
        sign = sub_lord_sign.lower().strip() if sub_lord_sign else "unknown"
        notes.append(f"7th Cusp Sub-Lord → {sub_lord_7 or 'N/A'} in {sub_lord_sign or 'N/A'}")
        
        # 5th cusp analysis
        sub_lord_5 = get_cusp_sub_lord(5, houses)
        verdict = kp_check_promise(
            planets=planets,
            houses=houses,
            csl_house=5,               # for romantic connection
            promise_houses={5, 7, 11},
            obstacle_houses={6, 8, 12}
        )
        
        state = verdict["state"]
        
        # Main love promise determination
        if state == "promised":
            add("💖 Love life promised — 5th CSL connects with 5/7/11")
            score["attraction"] += 5
            score["outcome"] += 5
        elif state == "promised_with_obstacles":
            add("⚠️ Love promised but with obstacles — 6/8/12 active")
            score["attraction"] += 2
            score["breakup_risk"] -= 3
        elif state == "blocked":
            add("💔 Love prospects blocked — 5th CSL only tied to 6/8/12")
            score["breakup_risk"] -= 6
            score["outcome"] -= 5
        else:
            add("❓ Love life uncertain — CSL mixed results")
        
        # Get signified houses for both cusps
        sig_5 = set(get_signified_houses(sub_lord_5, planets, houses) if sub_lord_5 else [])
        sig_7 = set(get_signified_houses(sub_lord_7, planets, houses) if sub_lord_7 else [])
        
        # -------------------------
        # KP promises: 5th <-> 7th
        # -------------------------
        if any(h in sig_5 for h in (2, 7, 11)):
            score["outcome"] += 5
            notes.append("💞 Love (5th) connects to Marriage houses (2/7/11) — strong promise of love marriage")
            add("5th lord in favorable house → romance opportunities")
        elif any(h in sig_5 for h in (6, 8, 12)):
            score["breakup_risk"] -= 6
            notes.append("💔 Love house linked to 6/8/12 — emotional strain or temporary romance likely")
            add("5th lord in difficult house → delayed romance")
        else:
            notes.append("⚖️ Neutral 5th cusp — moderate romantic possibilities")
        
        if sub_lord_5 and sub_lord_5 == sub_lord_7:
            score["compatibility"] += 3
            notes.append("✨ Same sub-lord for 5th & 7th → emotional-marital harmony indicator")
            add("Same sub-lord for 5th & 7th houses indicates harmony")
        
        # Love -> marriage checks
        love_to_marriage = bool(sig_5 & {7, 11})
        marriage_from_love = bool(sig_7 & {5, 11})
        
        if love_to_marriage and marriage_from_love:
            score["outcome"] += 6
            score["compatibility"] += 3
            notes.append("💞 Love transforms into life partnership — strong indication of marrying the one you love")
            add("Strong love-to-marriage connection indicated")
        elif love_to_marriage:
            score["outcome"] += 3
            notes.append("💗 Love likely to evolve into marriage or long-term commitment")
            add("Love may evolve into marriage")
        elif marriage_from_love:
            score["outcome"] += 2
            notes.append("💫 Marriage arises through prior romantic involvement")
            add("Marriage likely through love connection")
        else:
            notes.append("⚠️ Love and marriage appear independent — partner may differ from current love interest")
            add("Love and marriage paths may be separate")
        
        if any(h in sig_5 for h in (1, 6, 10, 12)):
            score["breakup_risk"] -= 4
            notes.append("💔 5th sub-lord tied with 1/6/10/12 → love may not culminate into marriage")
            add("5th house CSL shows challenges in converting love to marriage")
        
        # Venus analysis
        ve = get_planet("Venus", planets)
        if ve:
            ve_house = ve.get("house")
            ve_exalted = ve.get("exalted", False)
            ve_debilitated = ve.get("debilitated", False)
            ve_own_sign = ve.get("own_sign", False)
            
            if ve_exalted or ve_own_sign:
                score["attraction"] += 2
                state = "exalted" if ve_exalted else "in own sign"
                add(f"Venus is {state}, providing natural charm and attraction power")
            
            if ve_debilitated:
                score["attraction"] -= 2
                score["breakup_risk"] -= 2
                add("Venus is debilitated, requiring strengthening for love success")
            
            if ve_house in [5, 7]:
                score["attraction"] += 2
                add(f"Venus in {ve_house}th house creates strong romantic inclinations")
            
            if _has_evil_aspect(ve, planets):
                score["breakup_risk"] -= 2
                add("Venus has malefic aspects → obstacles in love")
        
        # Calculate overall outcome score
        total_score = (
            score["attraction"] + 
            score["outcome"] + 
            score["compatibility"] + 
            score["breakup_risk"]
        )
        
        # Determine promise based on comprehensive scoring
        if total_score >= 5 and score["outcome"] >= 3:
            promise = True
            summary = "Strong love promise with good prospects for lasting relationship"
        elif total_score >= 0 and state in ["promised", "promised_with_obstacles"]:
            promise = True
            summary = "Love is possible with effort and remedies. Moderate prospects indicated"
        elif state == "promised" and score["breakup_risk"] > -5:
            promise = True
            summary = "Love promised but requires patience and planetary strengthening"
        else:
            promise = False
            if score["breakup_risk"] < -5:
                summary = "Love prospects are challenging with high breakup risk. Focus on self-development and remedies"
            else:
                summary = "Love prospects are weak. Focus on remedies and timing"
        
        return {
            "promise": promise,
            "score": total_score,
            "summary": summary,
            "points": points,
            "notes": notes,
            "attraction_score": score["attraction"],
            "breakup_risk": score["breakup_risk"],
            "compatibility_score": score["compatibility"],
            "outcome_score": score["outcome"],
            "csl_5": sub_lord_5,
            "csl_7": sub_lord_7,
            "promise_5_state": state,
            "promise_7_state": verdict.get("state", "unknown")
        }
    
    # --------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        """Get predefined questions for Attracting Love"""
        return [
            Question(
                id="finding_love",
                question="Will I find love and when is it likely to happen?",
                sub_subdomain="Finding Love",
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.POSITIVE,
                    goal=InterpretationGoal.MANIFESTATION
                )
            )
        ]
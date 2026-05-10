"""
Marriage Prospects Evaluator - Enhanced v3.1 (KP Event Mechanism + Forced Chain Proof)

ENHANCEMENTS over v3.0:
✅ v3.1.1: _extract_kp_significator_table now includes HOW each house is signified (O/S/Sub/L)
✅ v3.1.2: New _build_kp_event_fructification_data() for transit-based event timing
✅ v3.1.3: _generate_marriage_timing_proof includes per-planet chain narrative
✅ v3.1.4: New "chain_narrative" field in significator table for LLM to copy
✅ v3.1.5: Event fructification checklist stored in additional_data

Evaluates marriage prospects including:
1. House Lords Analysis (PRIMARY)
2. KP Promise Analysis (7th CSL)
3. Classical Vedic Rules
4. Spouse Traits Analysis
5. Love vs Arranged Indicators
6. Manglik Analysis
7. KP Timing Indicators
8. Spouse Origin
9. KP Event Fructification Mechanism (NEW)

Priority Order (Classical Vedic):
1. House Lord Placement (7th, 2nd, 11th lords)
2. House Lord Condition (dignity, afflictions)
3. Planets in Marriage Houses
4. Aspects on Marriage Houses

Version: 3.1.0
"""

from typing import Dict, List, Any, Set, Optional
from collections import defaultdict
import logging
from unittest import result

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, _has_evil_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, is_combust, has_dig_bala,
    get_signified_houses, get_signified_score, get_cusp_sub_lord,
    kp_check_promise, get_spouse_direction_from_sign, get_spouse_nature_from_planet,
    detect_aspects, BENEFICS, MALEFICS, FRUITFUL_SIGNS, RASI_LORDS,
    resolve_rahu_ketu_sub_lord, get_detailed_spouse_traits, SPOUSE_AGE_DIFFERENCE_MAP,
    SPOUSE_CHARACTER_BOOK
)
from app.services.timing_engine import (
    get_kp_ruling_planets, score_kp_all_planets, get_positive_planets, TIMING_RULES
)

from app.core.astro_constants import detect_aspects, normalize_planet_name
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
except ImportError:
    HOUSE_LORDS_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MarriageProspectsEvaluator(BaseEvaluator):
    """
    Evaluator for Marriage Prospects subtopic.
    
    Enhanced v3.1 - KP Event Mechanism + Forced Chain Proof
    
    Analyzes (in priority order):
    1. House Lords (7th, 2nd, 11th) - placement and condition
    2. KP promise using 7th CSL method
    3. Classical Vedic marriage indicators
    4. Partner/spouse traits
    5. Marriage timing indicators
    6. Love vs arranged marriage likelihood
    7. KP Event Fructification Mechanism (NEW in v3.1)
    """
    
    domain = "Marriage"
    subtopic = "Marriage Prospects"
    
    # KP house significations
    positive_houses = {2, 7, 11}
    supportive_houses = {5}
    negative_houses = {6, 8, 12}
    
    # Primary and secondary houses for house lords analysis
    primary_houses = {7, 2, 11}
    secondary_houses = {5, 8}

    MARRIAGE_HOUSES = {2, 5, 7, 8, 11}
    
    # Key planets
    key_planets = {"Venus", "Jupiter", "Moon"}
    
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Main evaluation combining all marriage prospect analyses.
        
        Priority Order:
        1. House Lords Analysis
        2. KP Promise Analysis (stored in additional_data)
        3. Classical Marriage Analysis
        4. Spouse Traits
        5. Love vs Arranged
        6. Manglik Analysis
        7. KP Timing Indicators
        8. Spouse Origin
        9. KP Event Fructification (NEW v3.1)
        """
        self.reset()
        
        # Detect aspects first
        planets = detect_aspects(planets)
        
        result = EvaluationResult()
        
        # Use Vedic data for house lords analysis
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

        # Get question context
        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        # Get house configuration
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )
        
        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
        else:
            logger.warning("No config for question, using fallback")
            all_relevant_houses = self.MARRIAGE_HOUSES
            primary_houses = {7, 2, 11}
            secondary_houses = {5, 8}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("MARRIAGE PROSPECTS EVALUATOR (ENHANCED v3.1)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # Calculate aspects data
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ════════════════════════════════════════════════════════════════
        # 1. HOUSE LORDS ANALYSIS (PRIMARY)
        # ════════════════════════════════════════════════════════════════
        house_lords_points = self._evaluate_house_lords(
            analysis_planets, analysis_houses, aspects_data)
        result.extend_points(house_lords_points)
        
        # ════════════════════════════════════════════════════════════════
        # 2. KP PROMISE ANALYSIS (STORE IN ADDITIONAL_DATA!)
        # ════════════════════════════════════════════════════════════════
        csl_significations = self._extract_marriage_csls(planets, houses)
        direction_data = self._extract_spouse_direction(planets, houses)
        age_diff_data = self._extract_age_difference(planets, houses)
        promise_data = self._evaluate_marriage_promise(planets, houses)

        # ── Enrich promise_data with FULL signification details ──────────
        # This ensures every prompt gets the SAME house list for the 7th CSL,
        # preventing the LLM from re-deriving and getting inconsistent results.
        csl_7_name = promise_data.get("sub_lord", "")
        if csl_7_name:
            try:
                all_scores = get_signified_score(csl_7_name, planets, houses)
                all_sig_houses = sorted(h for h, s in all_scores.items() if s >= 1.0)
                promise_sigs = [h for h in all_sig_houses if h in {2, 7, 11}]
                obstacle_sigs = [h for h in all_sig_houses if h in {6, 8, 12}]
                other_sigs = [h for h in all_sig_houses if h not in {2, 7, 11, 6, 8, 12}]
                chain_narrative = self._get_planet_chain_narrative(csl_7_name, planets, houses)
                # Build Hindi house-number words for the chain sentence
                promise_data["all_signified_houses"] = all_sig_houses
                promise_data["csl_significations"] = {
                    "promise": promise_sigs,
                    "obstacle": obstacle_sigs,
                    "other": other_sigs,
                    "all": all_sig_houses,
                }
                promise_data["chain_narrative"] = chain_narrative
                promise_data["csl"] = csl_7_name  # alias for easy access
            except Exception as e:
                logger.warning(f"Could not enrich promise_data: {e}")

        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        csl_7 = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        effective_sub = resolve_rahu_ketu_sub_lord(planets, houses, csl_7)
        nature = get_spouse_nature_from_planet(effective_sub)
            
        spouse_nature_data = {
                "original_csl": csl_7,
                "effective_planet": effective_sub,
                "nature_traits": nature,
                "reasoning": f"7th CSL {csl_7}" + (f" acts through {effective_sub}" if csl_7 != effective_sub else "") + f" indicating: {nature}"
            }
            
        try:
                ruling_planets = get_kp_ruling_planets(planets)
                timing_data = {
                    "ruling_planets": ruling_planets[:5] if ruling_planets else [],
                    "marriage_key_planets": list(set(ruling_planets or []) & {"Venus", "Jupiter", "Moon"})
                }
        except:
                timing_data = {"ruling_planets": [], "marriage_key_planets": []}
            
        kp_comprehensive = {
                "promise": promise_data,
                "csl_details": csl_significations,
                "direction": direction_data,
                "age_difference": age_diff_data,
                "spouse_nature": spouse_nature_data,
                "timing_rulers": timing_data
            }
            
        result.additional_data["kp_marriage_analysis"] = kp_comprehensive
        kp_text_points = self._format_kp_text_points(kp_comprehensive)
        result.extend_points(kp_text_points)
        result.promise_state = promise_data.get("state", "neutral")
        result.additional_data["promise"] = promise_data
            
        logger.info(f"✅ Comprehensive KP analysis complete")
        
        # Also add text points for backwards compatibility
        if promise_data["state"] == "promised":
            self._add_unique(result, "KP: Marriage is strongly promised in this chart")
        elif promise_data["state"] == "promised_with_obstacles":
            self._add_unique(result, "KP: Marriage is promised but with some obstacles to overcome")
        elif promise_data["state"] == "blocked":
            self._add_unique(result, "KP: Marriage faces significant challenges - remedies recommended")
        else:
            self._add_unique(result, "KP: Marriage indicators are neutral - timing is key")
        result.promise_state = promise_data["state"]

        # ════════════════════════════════════════════════════════════════
        # 3. EXTRACT STRUCTURED DATA FOR LLM
        # ════════════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )
        
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        # ════════════════════════════════════════════════════════════════
        # LAGNA LORD ANALYSIS
        # ════════════════════════════════════════════════════════════════
        lagna_lord_analysis = self._extract_lagna_lord_analysis(
            analysis_houses,
            analysis_planets
        )
        
        if lagna_lord_analysis.get("lagna_lord"):
            logger.info(
                f"✅ Lagna: {lagna_lord_analysis['lagna_sign']} "
                f"(Lord: {lagna_lord_analysis['lagna_lord']}, "
                f"Verdict: {lagna_lord_analysis['verdict']})"
            )
        
        result.additional_data["lagna_lord_analysis"] = lagna_lord_analysis

        # ════════════════════════════════════════════════════════════════
        # KP SIGNIFICATOR TABLE (v3.1: WITH chain_narrative + how_map)
        # ════════════════════════════════════════════════════════════════
        kp_significator_table = self._extract_kp_significator_table(
            planets,
            houses
        )
        
        logger.info(f"✅ KP Significator table extracted for {len(kp_significator_table['planets'])} planets")
        logger.info(f"   Promising planets: {len(kp_significator_table['summary']['promising_planets'])}")
        logger.info(f"   Obstacle planets: {len(kp_significator_table['summary']['negative_planets'])}")
        
        result.additional_data["kp_significator_table"] = kp_significator_table

        # ════════════════════════════════════════════════════════════════
        # TIMING WINDOWS + EVENT FRUCTIFICATION (v3.1 NEW)
        # ════════════════════════════════════════════════════════════════
        if sub_subdomain in ("Marriage Timing", "Marriage Promise and Timing", "Marriage Promise") or meta_query_type == QueryType.TIMING:
            timing_windows_raw = kwargs.get("timing_windows", {})
            
            timing_windows_list = []
            if isinstance(timing_windows_raw, dict):
                timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
                if not timing_windows_list:
                    timing_windows_list = timing_windows_raw.get("Marriage Promise and Timing", [])
            else:
                timing_windows_list = timing_windows_raw if timing_windows_raw else []
            
            timing_windows_data = self._extract_timing_windows(timing_windows_list)
            
            # Generate Marriage Timing KP Significator Proof (v3.1 enhanced)
            if timing_windows_data and timing_windows_data.get('has_timing'):
                try:
                    marriage_timing_proof = self._generate_marriage_timing_proof(
                        planets=planets,
                        houses=houses,
                        timing_windows_data=timing_windows_data
                    )
                    logger.info(f"✅ Generated marriage timing significator proof")
                    logger.info(f"   Significator table entries: {len(marriage_timing_proof.get('significator_table', []))}")
                    logger.info(f"   Timing proofs generated: {len(marriage_timing_proof.get('timing_proofs', []))}")
                    
                    timing_windows_data["marriage_proof"] = marriage_timing_proof
                except Exception as e:
                    logger.warning(f"Could not generate marriage timing proof: {e}")
            
            # ════════════════════════════════════════════════════════════
            # v3.1 NEW: KP EVENT FRUCTIFICATION MECHANISM
            # ════════════════════════════════════════════════════════════
            if timing_windows_data and timing_windows_data.get('has_timing'):
                try:
                    event_fructification = self._build_kp_event_fructification_data(
                        planets=planets,
                        houses=houses,
                        promise_data=promise_data,
                        timing_windows_data=timing_windows_data,
                        ruling_planets_list=timing_data.get("ruling_planets", []),
                        kp_significator_table=kp_significator_table
                    )
                    timing_windows_data["event_fructification"] = event_fructification
                    logger.info(f"✅ KP Event Fructification: {event_fructification.get('total_score', 0)}/4 conditions met")
                    logger.info(f"   Verdict: {event_fructification.get('verdict', 'N/A')}")
                except Exception as e:
                    logger.warning(f"Could not build event fructification: {e}")
            
            if timing_windows_data and timing_windows_data.get('has_timing'):
                result.additional_data["marriage_timing_windows"] = timing_windows_data
                logger.info("✅ Stored timing windows in additional_data")
        
        # Store all structured data for LLM
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses
        )
        
        # ════════════════════════════════════════════════════════════════
        # 4-9. REMAINING ANALYSES (UNCHANGED)
        # ════════════════════════════════════════════════════════════════
        classical_points = self._evaluate_classical(planets, houses)
        result.extend_points(classical_points)
        
        spouse_points = self._evaluate_spouse_traits(planets, houses)
        result.extend_points(spouse_points)
        
        love_arranged = self._evaluate_love_vs_arranged(planets, houses)
        result.extend_points(love_arranged)
        
        manglik_points, manglik_data = self._evaluate_manglik_with_data(analysis_planets, analysis_houses)
        result.extend_points(manglik_points)
        result.additional_data["manglik_analysis"] = manglik_data
        
        timing_points = self._evaluate_kp_timing_indicators(planets, houses)
        result.extend_points(timing_points)
        
        origin_points = self._evaluate_spouse_origin(planets, houses)
        result.extend_points(origin_points)

        logger.info(f"✅ Evaluation complete. Promise state: {promise_data['state']}")
        logger.info(f"✅ Final result: {result}")
        return result

    # ════════════════════════════════════════════════════════════════════
    # v3.1 NEW: KP EVENT FRUCTIFICATION MECHANISM
    # ════════════════════════════════════════════════════════════════════
    
    def _build_kp_event_fructification_data(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        promise_data: Dict,
        timing_windows_data: Dict,
        ruling_planets_list: List[str],
        kp_significator_table: Dict
    ) -> Dict[str, Any]:
        """
        Build KP Event Fructification data — the 4-condition mechanism
        that determines IF and WHEN an event (marriage) will actually happen.
        
        KP Event Fructification requires ALL 4 conditions:
        ┌─────────────────────────────────────────────────────────────────┐
        │ 1. PROMISE: 7th CSL must signify 2/7/11 > 1/6/10/12          │
        │ 2. DBA SIGNIFICATION: Dasha-Bhukti-Antara lords must          │
        │    collectively signify 2/7/11                                 │
        │ 3. TRANSIT: Transiting planets must trigger 2/7/11 houses     │
        │ 4. RULING PLANETS: DBA lords should match current RPs         │
        └─────────────────────────────────────────────────────────────────┘
        
        Returns structured data with per-condition analysis.
        """
        
        PROMISE_HOUSES = {2, 7, 11}
        DENIAL_HOUSES = {1, 6, 10, 12}
        
        fructification = {
            "conditions": [],
            "total_score": 0,
            "max_score": 4,
            "verdict": "",
            "verdict_hindi": "",
            "narrative_for_llm": ""
        }
        
        # ══════════════════════════════════════════════════════════════
        # CONDITION 1: PROMISE (7th CSL Analysis)
        # ══════════════════════════════════════════════════════════════
        promise_state = promise_data.get("state", "unknown")
        csl_planet = promise_data.get("sub_lord", "Unknown")
        promise_score = promise_data.get("promise_score", 0)
        obstacle_score = promise_data.get("obstacle_score", 0)
        csl_significations = promise_data.get("csl_significations", {})
        
        promise_met = promise_state in ("promised", "promised_with_obstacles")
        
        # Build CSL chain narrative
        csl_chain = self._get_planet_chain_narrative(csl_planet, planets, houses)
        
        condition_1 = {
            "name": "PROMISE",
            "name_hindi": "वचन (Promise)",
            "met": promise_met,
            "score": 1 if promise_met else 0,
            "details": {
                "csl_planet": csl_planet,
                "promise_state": promise_state,
                "promise_score": promise_score,
                "obstacle_score": obstacle_score,
                "promise_houses_signified": csl_significations.get("promise", []),
                "denial_houses_signified": csl_significations.get("obstacle", []),
                "chain_narrative": csl_chain
            },
            "explanation": (
                f"7th CSL {csl_planet} signifies promise houses {csl_significations.get('promise', [])} "
                f"and obstacle houses {csl_significations.get('obstacle', [])}. "
                f"Promise {'>' if promise_met else '<='} Obstacle → {'MET' if promise_met else 'NOT MET'}"
            ),
            "explanation_hindi": (
                f"7वें भाव का CSL {csl_planet} है। "
                f"विवाह भाव (2/7/11): {csl_significations.get('promise', [])} संकेतित। "
                f"बाधा भाव: {csl_significations.get('obstacle', [])} संकेतित। "
                f"→ वचन {'पूरा' if promise_met else 'अधूरा'}"
            )
        }
        fructification["conditions"].append(condition_1)
        if promise_met:
            fructification["total_score"] += 1
        
        # ══════════════════════════════════════════════════════════════
        # CONDITION 2: DBA SIGNIFICATION
        # ══════════════════════════════════════════════════════════════
        best_window = timing_windows_data.get("best_window", {})
        dasha_str = best_window.get("dasha", "")
        dasha_parts = [d.strip() for d in dasha_str.replace(" > ", "-").replace(">", "-").split("-") if d.strip()]
        
        dba_promise_houses = set()
        dba_denial_houses = set()
        dba_lord_chains = []
        
        for lord_name in dasha_parts:
            lord_norm = normalize_planet_name(lord_name)
            if not lord_norm:
                continue
            
            # Get signified houses from significator table
            planet_entry = next(
                (p for p in kp_significator_table.get("planets", []) if p["name"] == lord_norm),
                None
            )
            
            if planet_entry:
                lord_promise = set(planet_entry.get("promise_houses", []))
                lord_negative = set(planet_entry.get("negative_houses", []))
                dba_promise_houses.update(lord_promise)
                dba_denial_houses.update(lord_negative)
                
                # Build chain narrative for this lord
                chain = self._get_planet_chain_narrative(lord_norm, planets, houses)
                dba_lord_chains.append({
                    "planet": lord_norm,
                    "promise_houses": sorted(lord_promise),
                    "negative_houses": sorted(lord_negative),
                    "chain_narrative": chain,
                    "significator_houses": planet_entry.get("significator_houses", []),
                    "how_map": planet_entry.get("how_map", {})
                })
        
        # DBA is met if collectively they signify at least 2 of {2, 7, 11}
        dba_met = len(dba_promise_houses & PROMISE_HOUSES) >= 2
        
        condition_2 = {
            "name": "DBA_SIGNIFICATION",
            "name_hindi": "दशा संकेत (DBA Signification)",
            "met": dba_met,
            "score": 1 if dba_met else 0,
            "details": {
                "dasha": dasha_str,
                "dba_lords": dba_lord_chains,
                "combined_promise_houses": sorted(dba_promise_houses & PROMISE_HOUSES),
                "combined_denial_houses": sorted(dba_denial_houses),
                "houses_covered": len(dba_promise_houses & PROMISE_HOUSES),
                "houses_needed": 2
            },
            "explanation": (
                f"DBA ({dasha_str}) lords collectively signify "
                f"promise houses {sorted(dba_promise_houses & PROMISE_HOUSES)} out of {{2,7,11}}. "
                f"Coverage: {len(dba_promise_houses & PROMISE_HOUSES)}/3 "
                f"(need ≥2) → {'MET' if dba_met else 'NOT MET'}"
            ),
            "explanation_hindi": (
                f"दशा {dasha_str} के स्वामी मिलकर विवाह भाव "
                f"{sorted(dba_promise_houses & PROMISE_HOUSES)} को संकेतित करते हैं। "
                f"→ DBA शर्त {'पूरी' if dba_met else 'अधूरी'}"
            )
        }
        fructification["conditions"].append(condition_2)
        if dba_met:
            fructification["total_score"] += 1
        
        # ══════════════════════════════════════════════════════════════
        # CONDITION 3: TRANSIT TRIGGER
        # ══════════════════════════════════════════════════════════════
        # In KP, transit trigger = current transiting planets touching
        # the sub lords of 2/7/11 cusps or their star lords.
        # Since we don't have real-time transit data, we use ruling
        # planets as a proxy (KP standard practice).
        
        # Check if ruling planets signify marriage houses
        rp_promise_signification = []
        for rp in ruling_planets_list[:5]:
            rp_entry = next(
                (p for p in kp_significator_table.get("planets", []) if p["name"] == rp),
                None
            )
            if rp_entry and rp_entry.get("promise_houses"):
                rp_promise_signification.append({
                    "planet": rp,
                    "promise_houses": rp_entry["promise_houses"]
                })
        
        transit_met = len(rp_promise_signification) >= 1
        
        condition_3 = {
            "name": "TRANSIT_TRIGGER",
            "name_hindi": "गोचर प्रेरक (Transit Trigger)",
            "met": transit_met,
            "score": 1 if transit_met else 0,
            "details": {
                "ruling_planets": ruling_planets_list[:5],
                "rp_signifying_marriage": rp_promise_signification,
                "method": "Ruling planets as transit proxy (KP standard)"
            },
            "explanation": (
                f"Ruling planets {ruling_planets_list[:5]} — "
                f"{len(rp_promise_signification)} of them signify 2/7/11. "
                f"→ {'MET' if transit_met else 'NOT MET'}"
            ),
            "explanation_hindi": (
                f"वर्तमान ruling planets: {', '.join(ruling_planets_list[:5])}। "
                f"इनमें से {len(rp_promise_signification)} विवाह भाव संकेतित करते हैं। "
                f"→ गोचर शर्त {'पूरी' if transit_met else 'अधूरी'}"
            )
        }
        fructification["conditions"].append(condition_3)
        if transit_met:
            fructification["total_score"] += 1
        
        # ══════════════════════════════════════════════════════════════
        # CONDITION 4: RULING PLANET MATCH IN DBA
        # ══════════════════════════════════════════════════════════════
        dba_lord_names = [normalize_planet_name(d) for d in dasha_parts if normalize_planet_name(d)]
        rp_in_dba = [rp for rp in ruling_planets_list[:5] if rp in dba_lord_names]
        rp_match_met = len(rp_in_dba) >= 1
        
        condition_4 = {
            "name": "RULING_PLANET_MATCH",
            "name_hindi": "शासक ग्रह मिलान (Ruling Planet Match)",
            "met": rp_match_met,
            "score": 1 if rp_match_met else 0,
            "details": {
                "dba_lords": dba_lord_names,
                "ruling_planets": ruling_planets_list[:5],
                "matching": rp_in_dba
            },
            "explanation": (
                f"DBA lords {dba_lord_names} vs Ruling Planets {ruling_planets_list[:5]}. "
                f"Matching: {rp_in_dba if rp_in_dba else 'None'}. "
                f"→ {'MET' if rp_match_met else 'NOT MET'}"
            ),
            "explanation_hindi": (
                f"DBA स्वामी: {', '.join(dba_lord_names)}। "
                f"Ruling Planets: {', '.join(ruling_planets_list[:5])}। "
                f"मिलान: {', '.join(rp_in_dba) if rp_in_dba else 'कोई नहीं'}। "
                f"→ {'पूरी' if rp_match_met else 'अधूरी'}"
            )
        }
        fructification["conditions"].append(condition_4)
        if rp_match_met:
            fructification["total_score"] += 1
        
        # ══════════════════════════════════════════════════════════════
        # FINAL VERDICT
        # ══════════════════════════════════════════════════════════════
        total = fructification["total_score"]
        
        if total >= 4:
            fructification["verdict"] = "STRONGLY_INDICATED"
            fructification["verdict_hindi"] = "विवाह अत्यंत प्रबल रूप से संकेतित (4/4 शर्तें पूरी)"
            fructification["verdict_icon"] = "🟢"
        elif total >= 3:
            fructification["verdict"] = "STRONGLY_INDICATED"
            fructification["verdict_hindi"] = "विवाह प्रबल रूप से संकेतित (3/4 शर्तें पूरी)"
            fructification["verdict_icon"] = "🟢"
        elif total >= 2:
            fructification["verdict"] = "MODERATELY_INDICATED"
            fructification["verdict_hindi"] = "विवाह मध्यम रूप से संकेतित (2/4 शर्तें पूरी)"
            fructification["verdict_icon"] = "🟡"
        elif total >= 1:
            fructification["verdict"] = "WEAKLY_INDICATED"
            fructification["verdict_hindi"] = "विवाह कमजोर संकेत (1/4 शर्तें पूरी) — उपाय आवश्यक"
            fructification["verdict_icon"] = "🟠"
        else:
            fructification["verdict"] = "NOT_INDICATED"
            fructification["verdict_hindi"] = "विवाह का संकेत अभी नहीं (0/4 शर्तें पूरी) — उपाय अत्यावश्यक"
            fructification["verdict_icon"] = "🔴"
        
        # Build narrative for LLM to translate
        fructification["narrative_for_llm"] = self._build_fructification_narrative(fructification)
        
        return fructification
    
    def _get_planet_chain_narrative(
        self,
        planet_name: str,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> str:
        """
        Build a complete KP signification chain narrative for a single planet.
        
        v3.1: This is the CORE fix — generates a human-readable chain
        that the LLM MUST include in its response.
        
        Format:
        "[Planet] occupies House [X]. [Planet] is in nakshatra of [Star Lord].
         [Star Lord] occupies House [Y] and owns houses [Z1, Z2].
         [Planet]'s sub lord is [Sub Lord], in House [W].
         Through this chain, [Planet] signifies houses [list].
         Promise houses (2/7/11): [which]. Obstacle houses (6/8/12): [which]."
        """
        planet_data = planets.get(planet_name, {})
        if not planet_data:
            return f"{planet_name}: No data available"
        
        # Extract chain components
        planet_house = planet_data.get("house", "?")
        
        star_lord = normalize_planet_name(
            planet_data.get("nakshatra_lord") or
            planet_data.get("pseudo_nakshatra_lord") or
            planet_data.get("star_lord") or ""
        )
        
        sub_lord = normalize_planet_name(
            planet_data.get("sub_lord", "")
        )
        
        # Star lord details
        sl_house = "?"
        sl_owned = []
        if star_lord and star_lord in planets:
            sl_house = planets[star_lord].get("house", "?")
            for h in houses:
                h_sign = h.get("start_rasi") or h.get("sign") or ""
                h_lord = RASI_LORDS.get(h_sign, "")
                if normalize_planet_name(h_lord) == star_lord:
                    sl_owned.append(h.get("house"))
        
        # Sub lord details
        sub_house = "?"
        sub_owned = []
        if sub_lord and sub_lord in planets:
            sub_house = planets[sub_lord].get("house", "?")
            for h in houses:
                h_sign = h.get("start_rasi") or h.get("sign") or ""
                h_lord = RASI_LORDS.get(h_sign, "")
                if normalize_planet_name(h_lord) == sub_lord:
                    sub_owned.append(h.get("house"))
        
        # Planet's own owned houses
        owned_houses = []
        for h in houses:
            h_sign = h.get("start_rasi") or h.get("sign") or ""
            h_lord = RASI_LORDS.get(h_sign, "")
            if normalize_planet_name(h_lord) == planet_name:
                owned_houses.append(h.get("house"))
        
        # Get signified houses
        signified = get_signified_houses(planet_name, planets, houses) or set()
        promise_h = sorted(signified & {2, 7, 11})
        obstacle_h = sorted(signified & {6, 8, 12})
        
        # Build narrative
        lines = []
        lines.append(f"{planet_name} occupies House {planet_house}.")
        
        if star_lord:
            lines.append(
                f"{planet_name} is in nakshatra of {star_lord}. "
                f"{star_lord} occupies House {sl_house}"
                + (f" and owns houses {sl_owned}" if sl_owned else "")
                + "."
            )
        
        if sub_lord:
            lines.append(
                f"{planet_name}'s sub lord is {sub_lord}, in House {sub_house}"
                + (f", owns houses {sub_owned}" if sub_owned else "")
                + "."
            )
        
        if owned_houses:
            lines.append(f"{planet_name} owns houses {owned_houses}.")
        
        lines.append(f"Through this chain, {planet_name} signifies houses {sorted(signified)}.")
        
        if promise_h:
            lines.append(f"Promise houses (2/7/11) signified: {promise_h} ✅")
        else:
            lines.append(f"Promise houses (2/7/11) signified: None")
        
        if obstacle_h:
            lines.append(f"Obstacle houses (6/8/12) signified: {obstacle_h} ⚠️")
        
        return " ".join(lines)
    
    def _build_fructification_narrative(self, fructification: Dict) -> str:
        """
        Build a pre-formatted narrative that the LLM should translate to Hindi.
        This ensures the event fructification mechanism is ALWAYS shown.
        """
        lines = []
        lines.append("KP EVENT FRUCTIFICATION CHECKLIST (फलित सूत्र):")
        lines.append("")
        
        for i, cond in enumerate(fructification["conditions"], 1):
            icon = "✅" if cond["met"] else "❌"
            lines.append(f"  {i}. {cond['name_hindi']}")
            lines.append(f"     {icon} {cond['explanation']}")
            
            # For DBA condition, show each lord's chain
            if cond["name"] == "DBA_SIGNIFICATION":
                for lord_chain in cond["details"].get("dba_lords", []):
                    lines.append(f"     ┌─ {lord_chain['planet']}:")
                    lines.append(f"     │  {lord_chain['chain_narrative']}")
                    lines.append(f"     └─ Promise: {lord_chain['promise_houses']}, Obstacle: {lord_chain['negative_houses']}")
            
            # For PROMISE condition, show CSL chain
            if cond["name"] == "PROMISE":
                lines.append(f"     Chain: {cond['details'].get('chain_narrative', 'N/A')}")
            
            lines.append("")
        
        total = fructification["total_score"]
        lines.append(f"  TOTAL: {total}/4 conditions met")
        lines.append(f"  VERDICT: {fructification['verdict_icon']} {fructification['verdict_hindi']}")
        lines.append("")
        lines.append("⚠️ LLM: Translate ALL above into Hindi paragraphs. Show each lord's chain.")
        
        return "\n".join(lines)

    # ════════════════════════════════════════════════════════════════════
    # v3.1 ENHANCED: _extract_kp_significator_table with how_map
    # ════════════════════════════════════════════════════════════════════
    
    def _extract_kp_significator_table(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> Dict:
        """
        v3.1: Extract complete KP significator table with HOW each house is signified.
        
        NEW in v3.1:
        - "how_map": {house_num: ["O: occupies", "S: through star lord X", ...]}
        - "chain_narrative": Pre-built English narrative for LLM to translate
        """
        
        kp_table = {
            "planets": [],
            "summary": {
                "promising_planets": [],
                "negative_planets": [],
                "neutral_planets": []
            }
        }
        
        PROMISE_HOUSES = {2, 7, 11}
        SUPPORTIVE_HOUSES = {5}
        NEGATIVE_HOUSES = {6, 8, 12}
        
        for planet_name, planet_data in planets.items():
            star_lord = normalize_planet_name(
                planet_data.get("nakshatra_lord") or
                planet_data.get("pseudo_nakshatra_lord") or
                planet_data.get("star_lord") or ""
            )
            
            sub_lord = normalize_planet_name(
                planet_data.get("sub_lord", "")
            ) if planet_data.get("sub_lord") else ""
            
            planet_house = planet_data.get("house")
            
            star_lord_house = None
            if star_lord and star_lord in planets:
                star_lord_house = planets[star_lord].get("house")
            
            sub_lord_house = None
            if sub_lord and sub_lord in planets:
                sub_lord_house = planets[sub_lord].get("house")
            
            # Houses owned by this planet
            owned_houses = []
            for h in houses:
                h_sign = h.get("start_rasi") or h.get("sign") or ""
                h_lord = RASI_LORDS.get(h_sign, "")
                if normalize_planet_name(h_lord) == planet_name:
                    owned_houses.append(h.get("house"))
            
            # ═══════════════════════════════════════════════════════════
            # v3.1 NEW: Build how_map — explains HOW each house is signified
            # ═══════════════════════════════════════════════════════════
            how_map = {}  # {house_num: [reasons]}
            
            # Level 1: Occupation (strongest in KP after Sub Lord)
            if planet_house:
                how_map.setdefault(planet_house, []).append(
                    f"O: {planet_name} occupies House {planet_house}"
                )
            
            # Level 2: Through Star Lord
            if star_lord and star_lord_house:
                how_map.setdefault(star_lord_house, []).append(
                    f"S: {planet_name} is in nakshatra of {star_lord}, who occupies House {star_lord_house}"
                )
                # Star lord's owned houses
                for h in houses:
                    h_sign = h.get("start_rasi") or h.get("sign") or ""
                    h_lord_name = normalize_planet_name(RASI_LORDS.get(h_sign, ""))
                    if h_lord_name == star_lord:
                        h_num = h.get("house")
                        if h_num and h_num != star_lord_house:
                            how_map.setdefault(h_num, []).append(
                                f"S-L: {star_lord} (star lord) owns House {h_num}"
                            )
            
            # Level 3: Through Sub Lord  
            if sub_lord and sub_lord_house:
                how_map.setdefault(sub_lord_house, []).append(
                    f"Sub: {planet_name}'s sub lord {sub_lord} occupies House {sub_lord_house}"
                )
            
            # Level 4: Ownership (weakest)
            for oh in owned_houses:
                how_map.setdefault(oh, []).append(
                    f"L: {planet_name} owns (lords) House {oh}"
                )
            
            # Get signified houses
            signified_houses = get_signified_houses(planet_name, planets, houses) or set()
            
            # Categorize
            promise_sigs = signified_houses & PROMISE_HOUSES
            supportive_sigs = signified_houses & SUPPORTIVE_HOUSES
            negative_sigs = signified_houses & NEGATIVE_HOUSES
            
            net_score = len(promise_sigs) + (len(supportive_sigs) * 0.5) - len(negative_sigs)
            
            if net_score >= 2:
                role = "STRONG PROMISE"
                kp_table["summary"]["promising_planets"].append(planet_name)
            elif net_score >= 1:
                role = "MODERATE PROMISE"
                kp_table["summary"]["promising_planets"].append(planet_name)
            elif net_score > -1:
                role = "NEUTRAL"
                kp_table["summary"]["neutral_planets"].append(planet_name)
            else:
                role = "OBSTACLES/DELAYS"
                kp_table["summary"]["negative_planets"].append(planet_name)
            
            if net_score > 0:
                score_str = f"+{net_score:.1f}" if net_score != int(net_score) else f"+{int(net_score)}"
            else:
                score_str = f"{net_score:.1f}" if net_score != int(net_score) else f"{int(net_score)}"
            
            # v3.1: Build chain narrative
            chain_narrative = self._get_planet_chain_narrative(planet_name, planets, houses)
            
            # v3.1: Build how_summary for promise and obstacle houses
            promise_how = {}
            for h in promise_sigs:
                promise_how[h] = how_map.get(h, [f"Signified (computed)"])
            
            obstacle_how = {}
            for h in negative_sigs:
                obstacle_how[h] = how_map.get(h, [f"Signified (computed)"])
            
            kp_table["planets"].append({
                "name": planet_name,
                "house": planet_house,
                "star_lord": star_lord or "Unknown",
                "star_lord_house": star_lord_house,
                "sub_lord": sub_lord or "Unknown",
                "sub_lord_house": sub_lord_house,
                "owned_houses": sorted(owned_houses),
                "significator_houses": sorted(signified_houses),
                "promise_houses": sorted(promise_sigs),
                "supportive_houses": sorted(supportive_sigs),
                "negative_houses": sorted(negative_sigs),
                "net_score": score_str,
                "role": role,
                # v3.1 NEW fields:
                "how_map": {str(k): v for k, v in how_map.items()},
                "promise_how": {str(k): v for k, v in promise_how.items()},
                "obstacle_how": {str(k): v for k, v in obstacle_how.items()},
                "chain_narrative": chain_narrative
            })
        
        # Sort by net score
        kp_table["planets"].sort(
            key=lambda x: float(x["net_score"].replace("+", "")),
            reverse=True
        )
        
        return kp_table

    # ════════════════════════════════════════════════════════════════════
    # v3.1 ENHANCED: _generate_marriage_timing_proof with chain per lord
    # ════════════════════════════════════════════════════════════════════
    
    def _generate_marriage_timing_proof(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        timing_windows_data: Dict
    ) -> Dict[str, Any]:
        """
        v3.1: Enhanced with per-lord chain narrative in timing proofs.
        """
        PROMISE_HOUSES = {2, 7, 11}
        SUPPORT_HOUSES = {5}
        OBSTACLE_HOUSES = {6, 8, 12}
        
        # STEP 1: Build House Occupancy Map
        house_occupants = defaultdict(list)
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            house = pdata.get("house")
            if house:
                house_occupants[house].append(pname)
        
        # STEP 2: Build House Lords Map
        house_lords = {}
        for h in houses:
            house_num = h.get("house")
            lord = h.get("rashi_lord") or h.get("sign_lord") or h.get("cusp_sub_lord")
            if house_num and lord:
                house_lords[house_num] = normalize_planet_name(lord)
        
        # STEP 3: Build Planet Significator Table
        planet_significators = {}
        
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            
            sigs = {
                "occupant_of": [],
                "star_lord_of_occupant": [],
                "own_house_lord": [],
                "sub_lord_of": [],
                "total_promise_signification": 0,
                "total_obstacle_signification": 0,
                "venus_connection": False,
                "jupiter_connection": False
            }
            
            planet_house = pdata.get("house")
            if planet_house:
                sigs["occupant_of"].append(planet_house)
                if planet_house in PROMISE_HOUSES:
                    sigs["total_promise_signification"] += 4
                if planet_house in SUPPORT_HOUSES:
                    sigs["total_promise_signification"] += 2
                if planet_house in OBSTACLE_HOUSES:
                    sigs["total_obstacle_signification"] += 4
            
            for h_num, lord in house_lords.items():
                if lord == pname:
                    sigs["own_house_lord"].append(h_num)
                    if h_num in PROMISE_HOUSES:
                        sigs["total_promise_signification"] += 2
                    if h_num in SUPPORT_HOUSES:
                        sigs["total_promise_signification"] += 1
                    if h_num in OBSTACLE_HOUSES:
                        sigs["total_obstacle_signification"] += 2
            
            nak_lord = normalize_planet_name(pdata.get("nakshatra_lord") or pdata.get("nak_lord"))
            if nak_lord:
                sigs["nakshatra_lord"] = nak_lord
                nak_lord_data = planets.get(nak_lord, {})
                nak_lord_house = nak_lord_data.get("house")
                if nak_lord_house:
                    sigs["star_lord_of_occupant"].append(nak_lord_house)
                    if nak_lord_house in PROMISE_HOUSES:
                        sigs["total_promise_signification"] += 3
                    if nak_lord_house in SUPPORT_HOUSES:
                        sigs["total_promise_signification"] += 1
                    if nak_lord_house in OBSTACLE_HOUSES:
                        sigs["total_obstacle_signification"] += 3
            
            if pname == "Venus" or sigs.get("nakshatra_lord") == "Venus":
                sigs["venus_connection"] = True
            if pname == "Jupiter" or sigs.get("nakshatra_lord") == "Jupiter":
                sigs["jupiter_connection"] = True
            
            planet_significators[pname] = sigs
        
        # STEP 4: Analyze Timing Windows with Significator Proof
        timing_proofs = []
        
        if timing_windows_data and timing_windows_data.get("all_favorable"):
            for window in timing_windows_data.get("all_favorable", [])[:5]:
                dasha_str = window.get("dasha", "")
                dasha_parts = dasha_str.replace(" / ", "-").replace("/", "-").split("-")
                
                proof = {
                    "period": f"{window.get('start', 'N/A')} to {window.get('end', 'N/A')}",
                    "dasha": dasha_str,
                    "score": window.get("final_score", 0),
                    "dasha_lords": [],
                    "total_2_7_11_activation": 0,
                    "total_obstacle_activation": 0,
                    "venus_involved": False,
                    "jupiter_involved": False,
                    "house_linkage": [],
                    "promise_strength": "WEAK"
                }
                
                for lord_name in dasha_parts:
                    lord_name = normalize_planet_name(lord_name.strip())
                    if not lord_name:
                        continue
                    
                    lord_sigs = planet_significators.get(lord_name, {})
                    
                    lord_proof = {
                        "planet": lord_name,
                        "signifies_promise_houses": [],
                        "signifies_obstacle_houses": [],
                        "how": [],
                        # v3.1 NEW: full chain narrative
                        "chain_narrative": self._get_planet_chain_narrative(lord_name, planets, houses)
                    }
                    
                    for h in lord_sigs.get("occupant_of", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Occupies house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                            lord_proof["how"].append(f"Occupies obstacle house {h}")
                    
                    for h in lord_sigs.get("own_house_lord", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Lord of house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                            lord_proof["how"].append(f"Lord of obstacle house {h}")
                    
                    for h in lord_sigs.get("star_lord_of_occupant", []):
                        if h in PROMISE_HOUSES:
                            lord_proof["signifies_promise_houses"].append(h)
                            lord_proof["how"].append(f"Star lord signifies house {h}")
                        if h in OBSTACLE_HOUSES:
                            lord_proof["signifies_obstacle_houses"].append(h)
                            lord_proof["how"].append(f"Star lord signifies obstacle house {h}")
                    
                    proof["total_2_7_11_activation"] += lord_sigs.get("total_promise_signification", 0)
                    proof["total_obstacle_activation"] += lord_sigs.get("total_obstacle_signification", 0)
                    
                    if lord_sigs.get("venus_connection") or lord_name == "Venus":
                        proof["venus_involved"] = True
                    if lord_sigs.get("jupiter_connection") or lord_name == "Jupiter":
                        proof["jupiter_involved"] = True
                    
                    proof["dasha_lords"].append(lord_proof)
                
                # Calculate promise strength
                promise_score = proof["total_2_7_11_activation"]
                obstacle_score = proof["total_obstacle_activation"]
                
                if promise_score >= 8 and promise_score > obstacle_score * 2:
                    proof["promise_strength"] = "STRONG"
                elif promise_score >= 5 and promise_score > obstacle_score:
                    proof["promise_strength"] = "MODERATE"
                else:
                    proof["promise_strength"] = "WEAK"
                
                houses_activated = set()
                for lord in proof["dasha_lords"]:
                    houses_activated.update(lord["signifies_promise_houses"])
                
                if 2 in houses_activated:
                    proof["house_linkage"].append("2nd house (family/wealth) signified")
                if 7 in houses_activated:
                    proof["house_linkage"].append("7th house (marriage/partnership) signified")
                if 11 in houses_activated:
                    proof["house_linkage"].append("11th house (fulfillment/gains) signified")
                if 5 in houses_activated:
                    proof["house_linkage"].append("5th house (romance) supporting")
                
                timing_proofs.append(proof)
        
        # STEP 5: Build Significator Summary Table
        significator_table = []
        
        for pname in ["Venus", "Jupiter", "Moon", "Mercury", "Sun", "Mars", "Saturn", "Rahu", "Ketu"]:
            if pname not in planet_significators:
                continue
            sigs = planet_significators[pname]
            
            promise_houses = []
            obstacle_houses = []
            
            if sigs.get("occupant_of"):
                for h in sigs["occupant_of"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(O)")
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(O)")
                        
            if sigs.get("own_house_lord"):
                for h in sigs["own_house_lord"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(L)")
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(L)")
                        
            if sigs.get("star_lord_of_occupant"):
                for h in sigs["star_lord_of_occupant"]:
                    if h in PROMISE_HOUSES:
                        promise_houses.append(f"{h}(S)")
                    if h in OBSTACLE_HOUSES:
                        obstacle_houses.append(f"{h}(S)")
            
            net_score = sigs.get("total_promise_signification", 0) - sigs.get("total_obstacle_signification", 0)
            
            if promise_houses or pname in ["Venus", "Jupiter"]:
                significator_table.append({
                    "planet": pname,
                    "signifies_2_7_11": promise_houses if promise_houses else ["None"],
                    "signifies_6_8_12": obstacle_houses if obstacle_houses else ["None"],
                    "promise_score": sigs.get("total_promise_signification", 0),
                    "obstacle_score": sigs.get("total_obstacle_signification", 0),
                    "net_score": net_score,
                    "is_marriage_karaka": pname == "Venus",
                    "is_benefic": pname in ["Venus", "Jupiter", "Moon", "Mercury"],
                    # v3.1 NEW:
                    "chain_narrative": self._get_planet_chain_narrative(pname, planets, houses)
                })
        
        significator_table.sort(key=lambda x: x["net_score"], reverse=True)
        
        return {
            "significator_table": significator_table,
            "timing_proofs": timing_proofs,
            "house_occupants": dict(house_occupants),
            "house_lords": house_lords,
            "legend": {
                "O": "Occupant (planet sits in this house) - strongest",
                "L": "Lord (planet rules this house sign)",
                "S": "Star Lord (planet's nakshatra lord signifies this house)"
            },
            "promise_houses_meaning": {
                2: "Family, wealth, domestic happiness",
                7: "Marriage, partnership, spouse",
                11: "Fulfillment of desires, gains, success"
            },
            "obstacle_houses_meaning": {
                6: "Obstacles, conflicts, disputes",
                8: "Delays, transformations, hidden issues",
                12: "Losses, separations, expenses"
            }
        }

    # ════════════════════════════════════════════════════════════════════
    # ALL REMAINING METHODS — UNCHANGED FROM v3.0
    # (Included for completeness)
    # ════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def extract_planet_name(p):
        if isinstance(p, dict):
            return p.get("name")
        if isinstance(p, str):
            return p
        return None
    
    def _extract_house_lords(self, houses, planets, relevant_houses, primary_houses):
        """Extract house lord information for relevant houses."""
        house_lords_info = {}
        for h in houses:
            house_num = h.get("house")
            if house_num not in relevant_houses:
                continue
            lord_name = h.get("sign_lord") or h.get("rashi_lord") or h.get("lord") or ""
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
            lord_degree = lord_data.get("full_degree") or lord_data.get("global_degree") or lord_data.get("degree") or 0
            lord_is_combust = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)
            lord_dignity = "Unknown"
            lord_strength_score = 50
            if HOUSE_LORDS_AVAILABLE:
                try:
                    if _is_exalted(lord_data):
                        lord_dignity = "EXALTED"
                        lord_strength_score = 100
                    elif _is_debilitated(lord_data):
                        lord_dignity = "DEBILITATED"
                        lord_strength_score = 0
                    elif _is_own_sign(lord_data):
                        lord_dignity = "OWN_SIGN"
                        lord_strength_score = 80
                    else:
                        lord_dignity = "NEUTRAL"
                        lord_strength_score = 50
                    if lord_is_combust:
                        lord_strength_score -= 30
                    if lord_is_retrograde:
                        if normalized_lord in {"Jupiter", "Venus", "Mercury"}:
                            lord_strength_score -= 10
                        elif normalized_lord in {"Saturn", "Mars"}:
                            lord_strength_score += 10
                    lord_strength_score = max(0, min(100, lord_strength_score))
                except Exception:
                    pass
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
    
    def _extract_aspects_on_houses(self, houses, planets, aspects_data, relevant_houses):
        """Extract aspects on relevant houses."""
        house_aspects = {}
        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
        for house_num in relevant_houses:
            house_aspects[house_num] = {"benefic_aspects": [], "malefic_aspects": [], "neutral_aspects": []}
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
    
    def _extract_timing_windows(self, timing_windows):
        """Extract BEST and NEAREST timing windows."""
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
                    'score_maha': get_attr(w, 'score_maha'),
                    'score_antara': get_attr(w, 'score_antara'),
                }
            sorted_windows = sorted(timing_windows, key=lambda w: get_attr(w, 'final_score', 0) or 0, reverse=True)
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None
            from datetime import datetime
            favorable_windows = [w for w in timing_windows if (get_attr(w, 'final_score', 0) or 0) >= 50]
            if favorable_windows:
                sorted_by_date = sorted(favorable_windows, key=lambda w: datetime.strptime(get_attr(w, 'start', '9999-12-31') or '9999-12-31', '%Y-%m-%d'))
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
    
    def _extract_lagna_lord_analysis(self, houses, planets):
        """Extract Lagna lord analysis."""
        lagna_analysis = {
            "lagna_sign": "", "lagna_lord": "", "lagna_lord_house": None,
            "lagna_lord_sign": "", "lagna_lord_dignity": "",
            "marriage_house_connections": [], "strength_score": 0,
            "marriage_impact": "", "verdict": "NEUTRAL"
        }
        house_1 = next((h for h in houses if h.get("house") == 1), None)
        if not house_1:
            return lagna_analysis
        lagna_sign = house_1.get("start_rasi", "") or house_1.get("rasi", "") or house_1.get("sign", "")
        if not lagna_sign:
            return lagna_analysis
        lagna_analysis["lagna_sign"] = lagna_sign
        SIGN_LORDS = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }
        lagna_lord = SIGN_LORDS.get(lagna_sign, "")
        if not lagna_lord:
            return lagna_analysis
        lagna_analysis["lagna_lord"] = lagna_lord
        lagna_lord_data = planets.get(lagna_lord, {})
        if not lagna_lord_data:
            return lagna_analysis
        lagna_lord_house = lagna_lord_data.get("house")
        lagna_lord_sign = lagna_lord_data.get("sign", "")
        dignity = lagna_lord_data.get("dignity", "")
        lagna_analysis["lagna_lord_house"] = lagna_lord_house
        lagna_analysis["lagna_lord_sign"] = lagna_lord_sign
        lagna_analysis["lagna_lord_dignity"] = dignity
        MARRIAGE_HOUSES = {2, 5, 7, 8, 11}
        if lagna_lord_house in MARRIAGE_HOUSES:
            house_meaning = {2: "Family/Resources", 5: "Love/Romance", 7: "Marriage/Spouse", 8: "Transformation", 11: "Fulfillment/Gains"}
            lagna_analysis["marriage_house_connections"].append(f"Placed in {lagna_lord_house}th ({house_meaning[lagna_lord_house]})")
        rules = lagna_lord_data.get("rules", [])
        if isinstance(rules, list):
            for house in rules:
                if house in MARRIAGE_HOUSES:
                    house_meaning = {2: "Family/Resources", 5: "Love/Romance", 7: "Marriage/Spouse", 8: "Transformation", 11: "Fulfillment/Gains"}
                    lagna_analysis["marriage_house_connections"].append(f"Rules {house}th ({house_meaning[house]})")
        strength = 0
        if dignity == "Exalted": strength += 3
        elif dignity == "Own Sign": strength += 2
        elif dignity == "Friend": strength += 1
        elif dignity == "Debilitated": strength -= 3
        elif dignity == "Enemy": strength -= 1
        if lagna_lord_house in {1, 2, 5, 7, 9, 10, 11}: strength += 1
        elif lagna_lord_house in {6, 8, 12}: strength -= 1
        lagna_analysis["strength_score"] = strength
        if lagna_lord_house == 7 or 7 in rules:
            lagna_analysis["marriage_impact"] = "Strong focus on marriage and partnership"
            lagna_analysis["verdict"] = "EXCELLENT"
        elif lagna_lord_house == 2 or 2 in rules:
            lagna_analysis["marriage_impact"] = "Focus on family and marital resources"
            lagna_analysis["verdict"] = "FAVORABLE"
        elif lagna_lord_house == 11 or 11 in rules:
            lagna_analysis["marriage_impact"] = "Marriage leads to fulfillment and gains"
            lagna_analysis["verdict"] = "FAVORABLE"
        elif lagna_lord_house == 5 or 5 in rules:
            lagna_analysis["marriage_impact"] = "Romantic and love-based marriage prospects"
            lagna_analysis["verdict"] = "FAVORABLE"
        elif lagna_lord_house == 8:
            lagna_analysis["marriage_impact"] = "Marriage brings transformation and challenges"
            lagna_analysis["verdict"] = "UNPREDICTABLE"
        elif lagna_lord_house == 6:
            lagna_analysis["marriage_impact"] = "Obstacles and delays in marriage"
            lagna_analysis["verdict"] = "CHALLENGING"
        elif lagna_lord_house == 12:
            lagna_analysis["marriage_impact"] = "Marriage may involve separation or foreign connection"
            lagna_analysis["verdict"] = "COMPLEX"
        else:
            lagna_analysis["marriage_impact"] = "Moderate marriage prospects"
            lagna_analysis["verdict"] = "NEUTRAL"
        if strength >= 3 and lagna_analysis["verdict"] in ["NEUTRAL", "FAVORABLE"]:
            lagna_analysis["verdict"] = "EXCELLENT"
        elif strength <= -2 and lagna_analysis["verdict"] not in ["CHALLENGING"]:
            lagna_analysis["verdict"] = "CHALLENGING"
        return lagna_analysis

    def _store_data_for_llm(self, result, house_config, house_lords_info, house_aspects_info, primary_houses, secondary_houses):
        """Store all structured data in additional_data for LLM consumption"""
        domain_prefix = "marriage"
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
                "strong_lords": sum(1 for info in house_lords_info.values() if info["lord_strength_score"] >= 70),
                "weak_lords": sum(1 for info in house_lords_info.values() if info["lord_strength_score"] < 40)
            }
        })

    # Remaining methods unchanged from v3.0 — included for completeness
    def _evaluate_house_lords(self, planets, houses, aspects_data=None):
        points = []
        if not HOUSE_LORDS_AVAILABLE:
            return points
        try:
            analyzer = HouseLordsAnalyzer(planets, houses, aspects_data)
            analysis = analyzer.get_domain_analysis("Marriage")
            points.append("═" * 60)
            points.append("📊 HOUSE LORDS ANALYSIS (Marriage Domain)")
            points.append("═" * 60)
            for lord in analysis.primary_lords:
                points.append(f"📍 {lord.format_placement()}")
                if lord.dignity == LordDignity.EXALTED:
                    points.append(f"   ⬆️ {lord.lord_name} EXALTED - very strong")
                elif lord.dignity == LordDignity.DEBILITATED:
                    points.append(f"   ⬇️ {lord.lord_name} DEBILITATED - needs strengthening")
                elif lord.dignity == LordDignity.OWN_SIGN:
                    points.append(f"   🏠 {lord.lord_name} in own sign - strong")
                afflictions = []
                if lord.is_combust: afflictions.append("Combust")
                if lord.is_retrograde: afflictions.append("Retrograde")
                if lord.malefic_aspects: afflictions.append(f"Malefic: {', '.join(lord.malefic_aspects)}")
                if afflictions: points.append(f"   ⚠️ {' | '.join(afflictions)}")
                if lord.benefic_aspects: points.append(f"   ✅ Supported: {', '.join(lord.benefic_aspects)}")
            if analysis.cross_references:
                points.append("\n🔗 CONNECTIONS:")
                for conn in analysis.cross_references:
                    points.append(f"   → {conn}")
            points.append("═" * 60)
        except Exception as e:
            points.append(f"House lords analysis error: {str(e)}")
        return points

    def _evaluate_marriage_promise(self, planets, houses):
        return kp_check_promise(planets=planets, houses=houses, csl_house=7, promise_houses={2, 7, 11}, obstacle_houses={6, 8, 12})

    def _extract_marriage_csls(self, planets, houses):
        csl_data = {}
        for house_num in [2, 7, 11]:
            csl = get_cusp_sub_lord(house_num, houses)
            if not csl: continue
            csl_norm = normalize_planet(csl)
            scores = get_signified_score(csl_norm, planets, houses)
            cusp = next((h for h in houses if h.get("house") == house_num), {})
            all_sig_houses = sorted(h for h, s in scores.items() if s >= 1.0)
            promise_houses_sig = [h for h in all_sig_houses if h in {2, 7, 11}]
            obstacle_houses_sig = [h for h in all_sig_houses if h in {6, 8, 12}]
            other_houses_sig = [h for h in all_sig_houses if h not in {2, 7, 11, 6, 8, 12}]
            promise_score = sum(scores.get(h, 0) for h in {2, 7, 11})
            obstacle_score = sum(scores.get(h, 0) for h in {6, 8, 12})
            if promise_score > obstacle_score + 1: verdict = "FAVORABLE"
            elif obstacle_score > promise_score + 1: verdict = "UNFAVORABLE"
            else: verdict = "MIXED"

            # Build chain narrative for this CSL (used to lock the LLM's description)
            try:
                chain_narrative = self._get_planet_chain_narrative(csl_norm, planets, houses)
            except Exception:
                chain_narrative = ""

            csl_data[house_num] = {
                "cusp_sub_lord": csl_norm,
                "csl": csl_norm,                          # alias
                "cusp_sign": str(cusp.get("start_rasi") or ""),
                "significations": {h: score for h, score in scores.items() if score >= 1.0},
                "all_signified_houses": all_sig_houses,   # ★ FULL list, not filtered
                "promise_houses_signified": promise_houses_sig,
                "obstacle_houses_signified": obstacle_houses_sig,
                "other_houses_signified": other_houses_sig,
                "signified_houses": all_sig_houses,       # alias for prompts
                "promise_score": promise_score,
                "obstacle_score": obstacle_score,
                "verdict": verdict,
                "chain_narrative": chain_narrative,       # ★ pre-built narrative
                "reasoning": (
                    f"{house_num}th CSL is {csl_norm}. "
                    f"Signifies ALL houses: {all_sig_houses}. "
                    f"Promise (2/7/11): {promise_houses_sig}. "
                    f"Obstacle (6/8/12): {obstacle_houses_sig}. "
                    f"Verdict: {verdict}."
                )
            }
        return csl_data

    def _extract_spouse_direction(self, planets, houses):
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        sign = str(cusp7.get("start_rasi") or "").title()
        direction = get_spouse_direction_from_sign(sign)
        return {"direction": direction, "cusp_7_sign": sign, "reasoning": f"KP: 7th cusp in {sign} → {direction}", "locality_type": self._get_locality_type(sign)}

    def _extract_age_difference(self, planets, houses):
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        csl_7 = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        nak_lord_7 = normalize_planet(cusp7.get("start_nakshatra_lord", ""))
        source_planet = nak_lord_7 or csl_7
        age_diff = SPOUSE_AGE_DIFFERENCE_MAP.get(source_planet, "comparable age")
        return {"age_difference": age_diff, "source_planet": source_planet, "reasoning": f"KP: 7th cusp source {source_planet} → {age_diff}"}

    def _get_locality_type(self, sign):
        movable = {"Aries", "Cancer", "Libra", "Capricorn"}
        fixed = {"Taurus", "Leo", "Scorpio", "Aquarius"}
        if sign in movable: return "distant place/different city"
        elif sign in fixed: return "same city/nearby area"
        return "medium distance/neighboring area"

    def _format_kp_text_points(self, kp_data):
        points = []
        promise = kp_data.get("promise", {})
        points.append(f"KP: Marriage promise state is {promise.get('state', 'unknown').upper()}")
        points.append(f"KP: 7th Cusp Sub Lord is {promise.get('sub_lord', 'N/A')}")
        csl_details = kp_data.get("csl_details", {})
        for house_num in [2, 7, 11]:
            if house_num in csl_details:
                points.append(f"KP: {csl_details[house_num]['reasoning']}")
        direction = kp_data.get("direction", {})
        if direction.get("reasoning"): points.append(direction["reasoning"])
        age = kp_data.get("age_difference", {})
        if age.get("reasoning"): points.append(age["reasoning"])
        nature = kp_data.get("spouse_nature", {})
        if nature.get("reasoning"): points.append(f"KP: {nature['reasoning']}")
        timing = kp_data.get("timing_rulers", {})
        if timing.get("ruling_planets"): points.append(f"KP: Ruling planets: {', '.join(timing['ruling_planets'][:5])}")
        return points

    def _evaluate_classical(self, planets, houses):
        points = []
        Mo, Ve, Ju, Sa = _p(planets, "Moon"), _p(planets, "Venus"), _p(planets, "Jupiter"), _p(planets, "Saturn")
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sign = str(cusp7.get("start_rasi") or cusp7.get("rasi") or "").title()
        lord7 = _lord_of(7, houses)
        if _in_sign(Mo, FRUITFUL_SIGNS) and _in_sign(Ve, FRUITFUL_SIGNS):
            points.append("Moon & Venus in fruitful signs - timely marriage")
        if c7sign in FRUITFUL_SIGNS:
            points.append(f"7th cusp in fruitful sign ({c7sign})")
        if _in_houses(Ju, {2, 7, 11}) or _in_houses(Ve, {2, 7, 11}):
            points.append("Jupiter/Venus in 2/7/11 - strong marriage yoga")
        if _aspected_by(Ve, "Saturn") or _conjoined(Ve, Sa):
            points.append("Saturn influences Venus - possible delays")
        if lord7:
            lord7_planet = _p(planets, lord7)
            if _in_houses(lord7_planet, {6, 8, 12}):
                points.append("7th lord in dusthana - obstacles")
        return points

    def _evaluate_spouse_traits(self, planets, houses):
        points = []
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sign = str(cusp7.get("start_rasi") or "").title()
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        sign_traits = {
            "Aries": "energetic, independent", "Taurus": "stable, sensual",
            "Gemini": "communicative, intellectual", "Cancer": "nurturing, emotional",
            "Leo": "proud, generous", "Virgo": "analytical, practical",
            "Libra": "balanced, diplomatic", "Scorpio": "intense, passionate",
            "Sagittarius": "philosophical, adventurous", "Capricorn": "ambitious, disciplined",
            "Aquarius": "innovative, humanitarian", "Pisces": "intuitive, compassionate"
        }
        if c7sign in sign_traits:
            points.append(f"Spouse nature: {sign_traits[c7sign]}")
        if c7sub:
            effective_sub = resolve_rahu_ketu_sub_lord(planets, houses, c7sub) if c7sub in ("Rahu", "Ketu") else c7sub
            nature = get_spouse_nature_from_planet(effective_sub)
            if nature: points.append(f"Spouse characteristics: {nature}")
        return points

    def _evaluate_love_vs_arranged(self, planets, houses):
        points = []
        Ve, Ra, Sa = _p(planets, "Venus"), _p(planets, "Rahu"), _p(planets, "Saturn")
        Mo = _p(planets, "Moon")
        love_pts, arranged_pts = 0, 0
        if has_harmonious_aspect(Ve, "Rahu") or _conjoined(Ve, Ra):
            love_pts += 2; points.append("Venus-Rahu → love attraction")
        if _aspected_by(Mo, "Saturn"):
            arranged_pts += 2; points.append("Saturn aspects Moon → family influence")
        if love_pts >= arranged_pts + 2: points.append("❤️ Love marriage more likely")
        elif arranged_pts >= love_pts + 2: points.append("🤝 Arranged marriage more indicated")
        else: points.append("💞 Both paths viable")
        return points

    def _evaluate_manglik(self, planets, houses):
        """Wrapper that returns only points (for backward compatibility)."""
        points, _ = self._evaluate_manglik_with_data(planets, houses)
        return points

    def _evaluate_manglik_with_data(self, planets, houses):
        """
        Evaluate Manglik dosha from both Lagna and Moon (Chandra).
        Returns (points_list, manglik_data_dict).

        Lagna Manglik: Mars in houses 1, 2, 4, 7, 8, 12 from Lagna
        Chandra Manglik: Mars in houses 1, 2, 4, 7, 8, 12 counted from Moon's house

        Note: Classical texts differ on which houses trigger Manglik.
        We use: 1, 2, 4, 7, 8, 12 (the more comprehensive set).
        Some texts use 1, 4, 7, 8, 12 (excluding 2nd). Both sets are noted.
        """
        points = []
        MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}

        Ma = _p(planets, "Mars")
        Mo = _p(planets, "Moon")
        mars_house = Ma.get("house") if Ma else None
        moon_house = Mo.get("house") if Mo else None
        mars_sign = Ma.get("sign") or Ma.get("rasi") or "" if Ma else ""

        # ── Lagna Manglik ──────────────────────────────────────────────
        lagna_manglik_raw = mars_house in MANGLIK_HOUSES if mars_house else False
        lagna_cancellation = None
        lagna_active = False

        if lagna_manglik_raw:
            if _is_own_sign(Ma) or _is_exalted(Ma):
                lagna_cancellation = "own_sign_or_exalted"
                points.append(
                    f"लग्न मांगलिक: मंगल {mars_house}वें भाव में — स्वग्रही/उच्च → दोष निरस्त "
                    f"(Lagna Manglik cancelled: Mars in own/exalted sign)"
                )
            elif _aspected_by(Ma, "Jupiter"):
                lagna_cancellation = "jupiter_aspect"
                points.append(
                    f"लग्न मांगलिक: मंगल {mars_house}वें भाव में — गुरु दृष्टि → दोष शमित "
                    f"(Lagna Manglik mitigated by Jupiter's aspect)"
                )
            else:
                lagna_active = True
                points.append(
                    f"लग्न मांगलिक: मंगल {mars_house}वें भाव में — दोष सक्रिय "
                    f"(Lagna Manglik ACTIVE: Mars in house {mars_house})"
                )
        else:
            if mars_house:
                points.append(
                    f"लग्न मांगलिक: मंगल {mars_house}वें भाव में — दोष नहीं "
                    f"(Lagna Manglik: NO — Mars in house {mars_house})"
                )

        # ── Chandra Manglik ────────────────────────────────────────────
        chandra_manglik_raw = False
        chandra_position = None
        chandra_cancellation = None
        chandra_active = False

        if mars_house and moon_house:
            # Count Mars's position from Moon (Moon = 1st position in this count)
            chandra_position = (mars_house - moon_house) % 12 + 1
            chandra_manglik_raw = chandra_position in MANGLIK_HOUSES

            if chandra_manglik_raw:
                if _is_own_sign(Ma) or _is_exalted(Ma):
                    chandra_cancellation = "own_sign_or_exalted"
                    points.append(
                        f"चंद्र मांगलिक: मंगल चंद्र से {chandra_position}वें — स्वग्रही/उच्च → दोष निरस्त "
                        f"(Chandra Manglik cancelled: Mars {chandra_position}th from Moon, own/exalted)"
                    )
                elif _aspected_by(Ma, "Jupiter"):
                    chandra_cancellation = "jupiter_aspect"
                    points.append(
                        f"चंद्र मांगलिक: मंगल चंद्र से {chandra_position}वें — गुरु दृष्टि → दोष शमित "
                        f"(Chandra Manglik mitigated: Mars {chandra_position}th from Moon, Jupiter aspect)"
                    )
                else:
                    chandra_active = True
                    points.append(
                        f"चंद्र मांगलिक: मंगल चंद्र से {chandra_position}वें भाव में — दोष सक्रिय "
                        f"(Chandra Manglik ACTIVE: Mars in {chandra_position}th from Moon [Moon in H{moon_house}])"
                    )
            else:
                points.append(
                    f"चंद्र मांगलिक: मंगल चंद्र से {chandra_position}वें भाव में — दोष नहीं "
                    f"(Chandra Manglik: NO — Mars {chandra_position}th from Moon)"
                )
        elif not moon_house:
            points.append("चंद्र मांगलिक: चंद्र की स्थिति अनुपलब्ध (Chandra Manglik: Moon position not available)")

        # ── Severity Assessment ────────────────────────────────────────
        active_count = (1 if lagna_active else 0) + (1 if chandra_active else 0)
        if active_count == 2:
            severity = "HIGH"
            severity_hindi = "उच्च — दोनों प्रकार का मांगलिक दोष सक्रिय"
        elif active_count == 1:
            severity = "MEDIUM"
            severity_hindi = "मध्यम — एक प्रकार का मांगलिक दोष सक्रिय"
        elif lagna_manglik_raw or chandra_manglik_raw:
            severity = "LOW"
            severity_hindi = "न्यून — दोष है परंतु निरस्त/शमित"
        else:
            severity = "NONE"
            severity_hindi = "कोई मांगलिक दोष नहीं"

        manglik_data = {
            "mars_house": mars_house,
            "mars_sign": mars_sign,
            "moon_house": moon_house,
            "lagna_manglik": {
                "present": lagna_manglik_raw,
                "active": lagna_active,
                "cancellation": lagna_cancellation,
                "mars_in_house": mars_house
            },
            "chandra_manglik": {
                "present": chandra_manglik_raw,
                "active": chandra_active,
                "cancellation": chandra_cancellation,
                "mars_position_from_moon": chandra_position,
                "moon_house": moon_house
            },
            "severity": severity,
            "severity_hindi": severity_hindi,
            "cancellation_factors": [c for c in [lagna_cancellation, chandra_cancellation] if c]
        }

        return points, manglik_data

    def _evaluate_kp_timing_indicators(self, planets, houses):
        points = []
        try:
            ruling_planets = get_kp_ruling_planets(planets)
            if ruling_planets:
                points.append(f"KP Timing: Ruling planets {', '.join(ruling_planets[:5])}")
            timing_rules = TIMING_RULES.get("Marriage Timing", {})
            planet_scores = score_kp_all_planets(planets, houses, timing_rules)
            positive_planets = get_positive_planets(planet_scores)
            if positive_planets:
                points.append(f"KP Timing: Favorable dasha lords - {', '.join(positive_planets[:4])}")
        except Exception:
            pass
        return points

    def _evaluate_spouse_origin(self, planets, houses):
        points = []
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sign = str(cusp7.get("start_rasi") or cusp7.get("rasi") or "").title()
        if c7sign:
            direction = get_spouse_direction_from_sign(c7sign)
            points.append(f"📍 Spouse likely from {direction}")
        movable = {"Aries", "Cancer", "Libra", "Capricorn"}
        fixed = {"Taurus", "Leo", "Scorpio", "Aquarius"}
        if c7sign in movable: points.append("Movable sign → distant place")
        elif c7sign in fixed: points.append("Fixed sign → same city/region")
        else: points.append("Dual sign → medium distance")
        return points

    def _calculate_lord_strength(self, planet_name, planet_data, dignity=None):
        score = 50
        if dignity:
            d = dignity.value if hasattr(dignity, 'value') else str(dignity).upper()
            score = {"EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80, "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0}.get(d, 50)
        if planet_data.get("is_combust") or planet_data.get("is_combusted"): score -= 30
        if planet_data.get("is_retrograde") or planet_data.get("is_retro"):
            score += 10 if planet_name in {"Saturn", "Mars"} else -10
        return max(0, min(100, score))

    def get_questions(self):
        return [
            Question(id="MAR_PROS_T1", question="Is marriage promised? When is the likely period?", meta=QueryMeta(query_type=QueryType.TIMING, polarity=EventPolarity.POSITIVE, goal=InterpretationGoal.MANIFESTATION), sub_subdomain="Marriage Promise and Timing"),
            Question(id="MAR_PROS_S1", question="What about future spouse nature and personality?", meta=QueryMeta(query_type=QueryType.NON_TIMING, polarity=EventPolarity.POSITIVE, goal=InterpretationGoal.STATUS), sub_subdomain="Partner Traits"),
            Question(id="MAR_PROS_L1", question="Love or arranged marriage?", meta=QueryMeta(query_type=QueryType.NON_TIMING, polarity=EventPolarity.POSITIVE, goal=InterpretationGoal.STATUS), sub_subdomain="Nature and Type"),
            Question(id="MAR_PROS_M1", question="Manglik dosha present?", meta=QueryMeta(query_type=QueryType.NON_TIMING, polarity=EventPolarity.NEGATIVE, goal=InterpretationGoal.RISK), sub_subdomain="Manglik Analysis"),
            Question(id="MAR_PROS_O1", question="Where might spouse be from?", meta=QueryMeta(query_type=QueryType.NON_TIMING, polarity=EventPolarity.POSITIVE, goal=InterpretationGoal.STATUS), sub_subdomain="Spouse Origin"),
        ]
"""
Education Guidance Evaluator – Child Domain (v3.0 FINAL)

Architecture (Finance / Foreign Parity):
1️⃣ Excel-driven house selection
2️⃣ Vedic capacity analysis (house lords + dignity + aspects)
3️⃣ KP education promise (STRICT – engine unchanged)
4️⃣ Timing windows + current & future dasha (pass-through, gated)
→ LLM narrates ONLY (no logic)
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

# ---- STRICT EDUCATION KP ENGINE (NO MODIFICATION) ----
from app.domains.child.education_engine import (
    evaluate_education_complete
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


class EducationGuidanceEvaluator(BaseEvaluator):

    domain = "Child"
    subtopic = "Education Guidance"

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

        # USE VEDIC DATA FOR HOUSE LORDS ANALYSIS
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        logger.info(
            f"DATA_SOURCE | vedic_planets_present={bool(vedic_planets)} "
            f"| vedic_houses_present={bool(vedic_houses)} "
            f"| fallback_used={not bool(vedic_planets and vedic_houses)}"
        )


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
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback")
            primary_houses = {5, 9}
            secondary_houses = {4, 1, 11}
            all_relevant_houses = primary_houses | secondary_houses


        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Education Guidance")

        # Handle both dict and QueryMeta object
        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("EDUCATION GUIDANCE EVALUATOR (CHILD DOMAIN v3.0)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects
        # ═══════════════════════════════════════════════════════
        detect_aspects(planets)
        detect_aspects(analysis_planets)
        
        logger.info(
            f"ASPECTS_START | HOUSE_LORDS_AVAILABLE={HOUSE_LORDS_AVAILABLE} "
            f"| planets_count={len(analysis_planets)}"
        )

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(
                    f"ASPECTS_DONE | planets_with_aspects={len(aspects_data)}"
                )
            except Exception as e:
                logger.error("ASPECTS_FAILED", exc_info=True)
        else:
            logger.warning("ASPECTS_SKIPPED | reason=HOUSE_LORDS_NOT_AVAILABLE")


        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract House Lords Data (for relevant houses only)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses, 
            analysis_planets, 
            all_relevant_houses,
            primary_houses
        )

        logger.info(
            f"HOUSE_LORDS_EXTRACTED | total={len(house_lords_info)} "
            f"| primary={len([h for h in house_lords_info if h in primary_houses])} "
            f"| secondary={len([h for h in house_lords_info if h not in primary_houses])}"
        )

        
        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 4: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(
            f"HOUSE_ASPECTS_EXTRACTED | houses={len(house_aspects_info)}"
        )

        
        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")
        
        for h, a in house_aspects_info.items():
            logger.debug(
                f"HOUSE_ASPECTS | house={h} "
                f"benefic={len(a.get('benefic_aspects', []))} "
                f"malefic={len(a.get('malefic_aspects', []))} "
                f"neutral={len(a.get('neutral_aspects', []))}"
            )

        # ═══════════════════════════════════════════════════════
        # STEP 4.5: KP EDUCATION PROMISE (STRICT – NO TIMING)
        # ═══════════════════════════════════════════════════════
        kp_points = []
        try:
            kp_points = evaluate_education_complete(
                planets=planets,      # KP planets ONLY
                houses=houses,        # KP houses ONLY
                d9_chart=kwargs.get("d9_chart")
            ) or []
        except Exception as e:
            logger.warning(f"KP education evaluation failed: {e}")

        # Add KP promise points to result (optional but recommended)
        for p in kp_points:
            result.add_point(p)

        has_kp_promise = bool(kp_points)


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
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
        else:
            timing_windows_list = timing_windows_raw or []

        
        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = {}

        is_timing = (
            meta_query_type == QueryType.TIMING or
            meta_query_type == "TIMING" or
            (hasattr(meta_query_type, "value") and meta_query_type.value == "TIMING") or
            (hasattr(meta_query_type, "name") and meta_query_type.name == "TIMING")
        )

        if is_timing:
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
        # STEP 6: Add Vedic Capacity Analysis (Education-Relevant Questions)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Aptitude and Education of Child","Prospects of Success","Prospects of College","Prospects of Foreign Education"}:

            self._add_house_analysis_points(
                result, 
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        if sub_subdomain == "Education Remedies":
            result.add_point(
                "Educational remedies are provided as supportive, non-invasive guidance "
                "focused on routines, environment, and encouragement, rather than ritual or prediction."
            )


        # ═══════════════════════════════════════════════════════
        # STEP 7: Store Enhanced Data for LLM (including timing!)
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            kp_promise={
                "has_promise": has_kp_promise,
                "points": kp_points
            }
        )

  


        # Add existing points from self.points to result
        if hasattr(self, 'points') and self.points:
            for point in self.points:
                result.add_point(point)

        return result
        

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - FIXED VERSION!
    # ═══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        
        ✅ FIXED: Now handles both dict and TimingWindow objects!
        
        Best window: Highest score (best planetary alignment)
        Nearest window: Earliest favorable window (soonest opportunity)
        
        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}
        
        try:
            # ✅ FIX: Helper function to get attribute from either dict or TimingWindow object
            def get_attr(obj, key, default=None):
                """Get attribute from dict or object (handles both cases)"""
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    # It's a TimingWindow dataclass or similar object
                    return getattr(obj, key, default)
            
            # ✅ FIX: Helper function to convert TimingWindow object to dict for storage
            def window_to_dict(w):
                """Convert TimingWindow object or dict to standardized dict format"""
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w
                
                # Convert TimingWindow dataclass to dict
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
                
                # Include additional fields if they exist
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar', 
                                   'md', 'ad', 'pd', 'maha', 'antara', 'paryantar',
                                   '_domain_score', '_delay_years', '_needs_resonant_jump']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val
                
                return result
            
            # Log the first window type for debugging
            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")
                if not isinstance(first, dict):
                    logger.info(f"🔍 First window attributes: {vars(first) if hasattr(first, '__dict__') else 'N/A'}")
            
            # ✅ FIX: Sort by final_score using get_attr helper
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )
            
            # Best window: highest score (convert to dict for JSON serialization)
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None
            
            # Nearest window: earliest with score >= 50
            from datetime import datetime
            
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
                # If no windows with score >= 50, use the best window as nearest too
                nearest_window = best_window
                logger.info("🔍 No windows with score >= 50, using best window as nearest")
            
            # Top 5 favorable windows (convert all to dicts)
            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]
            
            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }
            
            # Log success
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

    # ═══════════════════════════════════════════════════════════════
    # ENHANCED HELPER METHODS
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
        """
        Extract house lord information for relevant houses only.
        """
        house_lords_info = {}
        
        for h in houses:
            house_num = h.get("house")
            
            if house_num not in relevant_houses:
                continue
            
            # Get lord name - try multiple possible keys
            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
                h.get("lord") or
                ""
            )
            
            # Also try to deduce from sign if lord not found directly
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
                logger.warning(f"No lord found for house {house_num}")
                continue
            else:
                logger.debug(f"{normalized_lord} is House Lord for house {house_num}")
            
            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"No data found for lord {normalized_lord}")
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
            
            # Get lord dignity if house lords analyzer available
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
                            normalized_lord, lord_data, dignity)
                        
                        logger.debug(f"Determined Dignity for {normalized_lord}")
                    else:
                        logger.debug(f"Could not determine dignity for {normalized_lord}")
                        
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
        """Get house meaning for property context."""
        meanings = {
            1: "Learning Mindset",
            4: "Education Foundation",
            5: "Intelligence & Aptitude",
            9: "Higher Education",
            11: "Success & Achievement"
        }

        return meanings.get(house_num, "General")

    def _store_data_for_llm(
        self,
        result,
        house_config,
        house_lords_info,
        house_aspects_info,
        primary_houses,
        secondary_houses,
        timing_windows_data=None,
        kp_promise=None        # ← ADD
    ):

        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "child_education"
        if kp_promise:
            result.additional_data[f"{domain_prefix}_kp_promise"] = kp_promise

        
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
    # QUESTIONS (EXACT TABLE MATCH)
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="CH_EDU_1",
                question="What does astrology reveal about the child's aptitude, talents and possible learning challenges?",
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Aptitude and Education of Child"
            ),
            Question(
                id="CH_EDU_2",
                question="What does astrology indicate about the child's ability to excel in exams, best field or subject, higher studies, research and scholarships?",
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Prospects of Success"
            ),
            Question(
                id="CH_EDU_3",
                question="What are the prospects for school or college admission and receiving scholarships?",
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),

                sub_subdomain="Prospects of College"
            ),
            Question(
                id="CH_EDU_4",
                question="Are there prospects for the child to move abroad for studies?",
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Prospects of Foreign Education"
            )
        ]

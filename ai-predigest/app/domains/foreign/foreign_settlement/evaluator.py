"""
Foreign Settlement Evaluator – FINANCE-PARITY v7.0

✔ COMPLETE structural parity with Finance/Property evaluator
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction
✔ Timing windows with BEST + NEAREST
✔ All helper methods matching Finance pattern
✔ Sub-subdomain routing
✔ Complete data storage for LLM
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
from app.domains.foreign.foreign_engine import evaluate_foreign

from app.services.timing_engine import (
    score_kp_all_planets,
    get_positive_planets,
    get_kp_ruling_planets,
    TIMING_RULES
)

from app.core.astro_constants import detect_aspects, normalize_planet_name

# Import house lords analyzer (same as Finance)
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
    logging.info("House lords analyzer available for Foreign domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "foreign_settlement"
TIMING_KEY = "Foreign Timing"


class ForeignSettlementEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Foreign → Foreign Settlement
    
    Features (Finance-Parity):
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - KP timing (preserved)
    - Timing windows extraction (BEST + NEAREST)
    - Complete data storage for LLM
    """

    domain = "Foreign"
    subtopic = "Foreign Settlement"

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
        # STEP 0: Normalize Meta
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
        # STEP 1: Select Analysis Data (Vedic preferred)
        # ═══════════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.info(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.info(f"   Vedic houses count: {len(analysis_houses)}")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Get Question-Specific Houses
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
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback")
            primary_houses = {9, 12}
            secondary_houses = {3, 4, 7, 10, 11}
            all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 80)
        logger.info("FOREIGN SETTLEMENT EVALUATOR (FINANCE-PARITY v7.0)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Calculate Aspects
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
        # STEP 4: Extract House Lords Data (FULL - like Finance)
        # ═══════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Extract Aspects on Houses (FULL - like Finance)
        # ═══════════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Extract Timing Windows (FIXED - handles TimingWindow objects)
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")

            # Fallback keys
            if not timing_windows_list and "Foreign Settlement Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Foreign Settlement Timing"]
                logger.info(f"🔍 Using 'Foreign Settlement Timing' fallback key")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: KP Promise Evaluation
        # ═══════════════════════════════════════════════════════════
        kp_points = evaluate_foreign(planets, houses) or []

        for p in kp_points:
            result.add_point(p)

        has_promise = bool(kp_points)
        logger.info(f"🔑 KP PROMISE = {has_promise}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Timing Decision (Strict - like Finance)
        # ═══════════════════════════════════════════════════════════
        timing_windows_data = {}

        if (
            meta_query_type == QueryType.TIMING
            and has_promise
            and timing_windows_list
        ):
            timing_windows_data = self._extract_timing_windows(timing_windows_list) or {}
            logger.info("✅ TIMING ENABLED (KP promise + windows present)")

            if timing_windows_data and timing_windows_data.get('has_timing'):
                best = timing_windows_data.get('best_window', {})
                nearest = timing_windows_data.get('nearest_window', {})
                logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
                logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
                logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            timing_windows_data = {"has_timing": False}
            logger.info("⛔ TIMING DISABLED (no promise or no windows)")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Add House Analysis Points (for relevant sub-subdomains)
        # ═══════════════════════════════════════════════════════════
        if sub_subdomain in {
            "Foreign Settlement Timing",
            "Challenges in Foreign Land"
        }:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ═══════════════════════════════════════════════════════════
        # STEP 10: KP Timing Planets (Optional Points)
        # ═══════════════════════════════════════════════════════════
        if meta_query_type == QueryType.TIMING and has_promise:
            try:
                rules = TIMING_RULES.get(TIMING_KEY, {})
                scores = score_kp_all_planets(planets, houses, rules)

                positive = get_positive_planets(scores)
                if positive:
                    result.add_point(
                        f"Favorable dasha lords for foreign settlement: {', '.join(positive[:4])}."
                    )

                rulers = get_kp_ruling_planets(planets)
                if rulers:
                    result.add_point(
                        f"KP ruling planets supporting foreign settlement: {', '.join(rulers[:4])}."
                    )
            except Exception as e:
                logger.warning(f"Timing calc failed: {e}")

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Store Enhanced Data for LLM (FINANCE-PARITY)
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            kp_points,
            has_promise,
            kwargs
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION (FINANCE COPY - handles TimingWindow objects)
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        
        ✅ Handles both dict and TimingWindow objects (Finance-parity)
        
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
            return result

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION (FULL - Finance Parity)
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
        """
        Extract house lord information for relevant houses only.
        FULL implementation matching Finance evaluator.
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

            # Deduce from sign if lord not found
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
                logger.warning(f"No lord found for house {house_num}")
                continue

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
    # ASPECTS EXTRACTION (FULL - Finance Parity)
    # ══════════════════════════════════════════════════════════════
    def _extract_aspects_on_houses(
        self,
        houses: list,
        planets: dict,
        aspects_data: dict,
        relevant_houses: set
    ) -> dict:
        """Extract aspects on relevant houses only (Finance-parity)."""
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
    # STRENGTH CALCULATION (Finance Parity)
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity=None
    ) -> int:
        """Calculate lord strength score (0-100) - Finance parity."""
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
    # HOUSE MEANING (Foreign Domain Specific)
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for foreign settlement context."""
        meanings = {
            3: "Efforts/Short Travel",
            4: "Home/Roots",
            7: "Partnerships/Spouse Abroad",
            9: "Long Distance/Fortune",
            10: "Career Abroad",
            11: "Gains/Fulfillment",
            12: "Foreign Land/Settlement"
        }
        return meanings.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS (Finance Parity)
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

            point_text = " ".join(point_parts)
            result.add_point(point_text)

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM (FINANCE PARITY - COMPLETE)
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict,
        kp_points: list,
        has_promise: bool,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption (Finance parity)."""

        # Extract dasha context from kwargs
        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")
        transit_summary = kwargs.get("transit_summary")
        age_context = kwargs.get("age_context")
        meta = kwargs.get("meta")

        meta_query_type = None
        if meta:
            if isinstance(meta, QueryMeta):
                meta_query_type = meta.query_type
            elif isinstance(meta, dict):
                meta_query_type = QueryType[meta.get("type", "NON_TIMING")]

        result.additional_data.update({
            # House configuration
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },

            # House lords (FULL data)
            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,

            # House aspects (FULL data)
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            # KP Promise
            f"{DOMAIN_PREFIX}_kp_promise": {
                "has_promise": has_promise,
                "points": kp_points
            },

            # Analysis summary
            f"{DOMAIN_PREFIX}_analysis_summary": {
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

            # Dasha pass-through
            f"{DOMAIN_PREFIX}_current_dasha": current_dasha,
            f"{DOMAIN_PREFIX}_dasha_timeline": dasha_timeline,

            # Optional context
            f"{DOMAIN_PREFIX}_transit_summary": transit_summary,
            f"{DOMAIN_PREFIX}_age_context": age_context,
        })

        # Store timing windows (Finance parity)
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {DOMAIN_PREFIX}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE")

        # Dasha context for prompt builder
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
            f"📦 STORED | kp={has_promise} | timing={timing_windows_data.get('has_timing')} "
            f"| dasha={'YES' if current_dasha else 'NO'}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="FOR_SET_1",
                question=(
                    "Is there scope for me to settle abroad permanently?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Foreign Settlement Timing"
            ),
            Question(
                id="FOR_SET_2",
                question=(
                    "Will I face any delays or obstacles in obtaining permits, passport, "
                    "visa, or citizenship and how can I overcome them?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Visa and Documentation Challenges"
            ),
            Question(
                id="FOR_SET_3",
                question=(
                    "What does astrology reveal about my prospects for income and adjustment "
                    "in the new country, and what challenges should I be prepared for?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Challenges in Foreign Land"
            )
        ]
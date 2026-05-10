"""
Break-up Evaluator - v3.1 (PATCHED)

FIXES FROM v3.0:
✅ PATCH 2 (from parenting v7.2): _extract_timing_windows uses 'score' as fallback
   for 'final_score'. API data carries 'score'; pipeline may use 'final_score'.
   Added get_score() helper — previously all windows sorted to 0 and
   favorable_windows filter (>= 50) always returned empty.
   window_to_dict() now normalises final_score so downstream never sees None.

✅ Minor is_applicable flag stored in additional_data so prompt builder can
   render a clean "Not Applicable" block instead of awkward reinterpretation.

UNCHANGED FROM v3.0:
✔ Consistent domain prefix: love_and_relationship_
✔ _extract_house_lords() method with full dignity calculation
✔ _extract_aspects_on_houses() method
✔ _calculate_lord_strength() method
✔ _store_data_for_llm() centralized method
✔ _get_house_meaning() for breakup context
✔ _add_house_analysis_points() for structured result points
✔ KP Breakup Risk Engine (DO NOT MODIFY)
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)

from app.core.astro_constants import (
    detect_aspects,
    normalize_planet_name,
    get_planet,
    get_cusp_sub_lord,
    kp_check_promise,
    get_signified_houses,
    _has_evil_aspect,
    has_harmonious_aspect,
    _is_benefic,
    _is_malefic,
    _conjoined
)

from app.domains.excel_structure_config import get_houses_for_question

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import HouseLordsAnalyzer
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BreakupEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Love Relationship → Breakup

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction
    - Strength scoring
    - KP breakup risk analysis (preserved)
    - Timing windows extraction (BEST + NEAREST)
    - Minor detection flag stored for prompt builder
    """

    domain = "Love_Relationship"
    subtopic = "Breakup"

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

        # USE VEDIC DATA FOR HOUSE LORDS ANALYSIS
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")

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
        else:
            logger.warning(f"No config for question, using fallback")
            primary_houses = {5, 7, 8}
            secondary_houses = {6, 12, 1, 4}
            all_relevant_houses = primary_houses | secondary_houses

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "Breakup")
        gender: str = kwargs.get("gender", "male")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        # ── Minor detection ───────────────────────────────────────────────
        dob = kwargs.get("dob", "")
        is_minor = self._detect_minor(dob)
        logger.info(f"👤 Minor detection: DOB={dob}, is_minor={is_minor}")

        logger.info("=" * 80)
        logger.info("BREAKUP EVALUATOR (ENHANCED v3.1 - PATCHED)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Is Minor: {is_minor}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects
        # ═══════════════════════════════════════════════════════
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract House Lords Data
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
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

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 5: Extract Timing Windows
        # ✅ PATCH 2 applied in _extract_timing_windows
        # ═══════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])

            if not timing_windows_list and "Breakup" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Breakup"]
            if not timing_windows_list and "Reconciliation" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Reconciliation"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []

        # Suppress timing entirely for minors
        if is_minor:
            timing_windows_data = {"has_timing": False}
            logger.info("⛔ TIMING SUPPRESSED: person is a minor")
        else:
            timing_windows_data = self._extract_timing_windows(timing_windows_list)

        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.info(f"✅ TIMING WINDOWS EXTRACTED:")
            logger.info(
                f"   🏆 BEST: {best.get('dasha', 'N/A')} "
                f"- Score: {best.get('final_score') or best.get('score', 0)}"
            )
            logger.info(
                f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} "
                f"- Score: {nearest.get('final_score') or nearest.get('score', 0)}"
            )

        # ═══════════════════════════════════════════════════════
        # STEP 6: Add House Analysis Points
        # ═══════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════
        # STEP 7: KP BREAKUP RISK ENGINE (⚠️ UNCHANGED)
        # ═══════════════════════════════════════════════════════
        breakup_analysis = self._evaluate_breakup_risk(
            planets=planets,
            houses=houses,
            gender=gender
        )

        breakup_risk = breakup_analysis.get("breakup_risk", 0)

        if breakup_risk < -10:
            result.add_point(f"⚠️ High breakup risk detected. {breakup_analysis.get('summary')}")
            result.promise_state = "high_risk"
        elif breakup_risk < -5:
            result.add_point(f"⚠️ Moderate breakup risk present. {breakup_analysis.get('summary')}")
            result.promise_state = "moderate_risk"
        else:
            result.add_point(f"✅ Relationship stability indicated. {breakup_analysis.get('summary')}")
            result.promise_state = "stable"

        for p in breakup_analysis.get("points", [])[:10]:
            result.add_point(p)

        # ═══════════════════════════════════════════════════════
        # STEP 8: Sub-domain specific logic
        # ═══════════════════════════════════════════════════════
        if sub_subdomain == "Possibility of Reconciliation" and not is_minor:
            if timing_windows_data.get("has_timing"):
                best = timing_windows_data.get("best_window", {})
                nearest = timing_windows_data.get("nearest_window", {})

                if best:
                    result.add_point(
                        f"🏆 Best reconciliation period: {best.get('dasha')} "
                        f"({best.get('start')} – {best.get('end')})"
                    )

                if nearest and nearest.get('dasha') != best.get('dasha'):
                    result.add_point(
                        f"⏰ Nearest supportive phase: {nearest.get('dasha')} "
                        f"({nearest.get('start')} – {nearest.get('end')})"
                    )

        # ═══════════════════════════════════════════════════════
        # STEP 9: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            breakup_analysis,
            kwargs.get("current_dasha"),
            kwargs.get("dasha_timeline"),
            vedic_planets,
            vedic_houses,
            is_minor=is_minor
        )

        return result

    # ═══════════════════════════════════════════════════════════════
    # MINOR DETECTION
    # ═══════════════════════════════════════════════════════════════
    @staticmethod
    def _detect_minor(dob: str) -> bool:
        """Returns True if the person is currently under 18."""
        if not dob:
            return False
        try:
            today = datetime.now()
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
            age = today.year - dob_dt.year - (
                (today.month, today.day) < (dob_dt.month, dob_dt.day)
            )
            return age < 18
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ✅ PATCH 2: Uses 'score' as fallback for 'final_score'
    # ═══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.

        ✅ PATCH 2: get_score() checks both 'final_score' and 'score'.
           API data uses 'score'; pipeline-computed data uses 'final_score'.
           Previously final_score=None caused all windows to sort to 0 and
           favorable_windows filter (>= 50) to always return empty.
        """
        if not timing_windows:
            return {}

        try:
            def get_attr(obj, key, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # PATCH 2: resolve score from either field
            def get_score(w) -> float:
                """Read final_score first, fall back to score."""
                val = get_attr(w, 'final_score')
                if val is None:
                    val = get_attr(w, 'score', 0)
                return float(val or 0)

            def window_to_dict(w):
                if w is None:
                    return None
                if isinstance(w, dict):
                    # PATCH 2: normalise — ensure final_score is always populated
                    d = dict(w)
                    if d.get('final_score') is None:
                        d['final_score'] = d.get('score', 0)
                    return d

                return {
                    'start':               get_attr(w, 'start'),
                    'end':                 get_attr(w, 'end'),
                    'dasha':               get_attr(w, 'dasha'),
                    'score':               get_attr(w, 'score'),
                    'transit_score':       get_attr(w, 'transit_score'),
                    'final_score':         get_attr(w, 'final_score') or get_attr(w, 'score'),
                    'age_at_start':        get_attr(w, 'age_at_start'),
                    'needs_resonant_jump': get_attr(w, 'needs_resonant_jump', False),
                    'delay_years':         get_attr(w, 'delay_years', 0),
                    'score_maha':          get_attr(w, 'score_maha', 0),
                    'score_antara':        get_attr(w, 'score_antara', 0),
                    'score_paryantar':     get_attr(w, 'score_paryantar', 0),
                }

            # Sort by resolved score (PATCH 2)
            sorted_windows = sorted(timing_windows, key=get_score, reverse=True)
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            # Nearest: earliest with resolved score >= 50 (PATCH 2: was always empty)
            favorable_windows = [w for w in timing_windows if get_score(w) >= 50]
            logger.info(f"🔍 Favorable windows (score >= 50): {len(favorable_windows)}")

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
                logger.info("🔍 No windows with score >= 50, using best as nearest")

            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]

            return {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    # ═══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
    # ═══════════════════════════════════════════════════════════════
    def _extract_house_lords(
        self,
        houses: list,
        planets: dict,
        relevant_houses: set,
        primary_houses: set
    ) -> dict:
        """Extract house lord information for relevant houses."""
        house_lords_info = {}

        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }

        for h in houses:
            house_num = h.get("house")

            if house_num not in relevant_houses:
                continue

            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
                h.get("lord") or
                ""
            )

            if not lord_name:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                if sign:
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
                    elif hasattr(analyzer, 'analyze_dignity'):
                        dignity = analyzer.analyze_dignity(normalized_lord)

                    if dignity:
                        lord_dignity = dignity.value if hasattr(dignity, 'value') else str(dignity)
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, dignity)
                except Exception as e:
                    logger.warning(f"Could not analyze dignity for {normalized_lord}: {e}")

            priority = "primary" if house_num in primary_houses else "secondary"

            planets_in_house = [
                normalize_planet_name(p.get("name") if isinstance(p, dict) else p)
                for p in h.get("planets", [])
                if (p.get("name") if isinstance(p, dict) else p)
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

    # ═══════════════════════════════════════════════════════════════
    # ASPECTS EXTRACTION
    # ═══════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════
    # LORD STRENGTH CALCULATION
    # ═══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity=None
    ) -> int:
        """Calculate lord strength score (0-100)."""
        score = 50

        if dignity:
            dignity_str = dignity.value if hasattr(dignity, 'value') else str(dignity).upper()

            dignity_scores = {
                "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
                "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0
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

    # ═══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS
    # ═══════════════════════════════════════════════════════════════
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

            marker = "💔" if house_num in {6, 8, 12} else "💖"
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

            result.add_point(" ".join(point_parts))

    # ═══════════════════════════════════════════════════════════════
    # HOUSE MEANING FOR BREAKUP CONTEXT
    # ═══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for BREAKUP context."""
        meanings = {
            1: "Self/Personality",
            4: "Emotional Security",
            5: "Romance/Love",
            6: "Conflicts/Enemies",
            7: "Partnership",
            8: "Separation/Transformation",
            11: "Hopes/Fulfillment",
            12: "Losses/Endings"
        }
        return meanings.get(house_num, "General")

    # ═══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # ═══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None,
        kp_breakup: dict = None,
        current_dasha: dict = None,
        dasha_timeline: dict = None,
        vedic_planets: dict = None,
        vedic_houses: list = None,
        is_minor: bool = False
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
            f"{domain_prefix}_kp_breakup": kp_breakup,
            # ── Minor flag — prompt builder reads this to render "Not Applicable" ──
            f"{domain_prefix}_is_minor": is_minor,
            "current_dasha": current_dasha,
            "dasha_timeline": dasha_timeline,
            "vedic_planets": vedic_planets,
            "vedic_houses": vedic_houses
        })

        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(
                f"✅ STORED timing_windows: "
                f"best={best.get('dasha')} score={best.get('final_score') or best.get('score')} | "
                f"nearest={nearest.get('dasha')}"
            )
        else:
            result.additional_data[f"{domain_prefix}_timing_windows"] = {"has_timing": False}
            logger.warning("❌ NO TIMING WINDOWS STORED")

        logger.info(
            f"📦 STORED | is_minor={is_minor} | "
            f"timing={timing_windows_data.get('has_timing') if timing_windows_data else False} | "
            f"dasha={'YES' if current_dasha else 'NO'}"
        )

    # --------------------------------------------------
    # KP BREAKUP RISK ENGINE — ⚠️ DO NOT MODIFY ⚠️
    # --------------------------------------------------
    def _evaluate_breakup_risk(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        gender: str
    ) -> Dict:
        """KP Astrology - BREAKUP RISK EVALUATOR (UNCHANGED)"""

        score = {"attraction": 0, "breakup_risk": 0, "compatibility": 0, "outcome": 0}
        notes = []
        remedies = []
        points = []
        seen = set()

        def add(text):
            if text and text not in seen:
                points.append(text)
                seen.add(text)

        sub_lord_7 = get_cusp_sub_lord(7, houses)
        p7 = get_planet(sub_lord_7, planets) if sub_lord_7 else None

        sub_lord_sign = None
        if p7:
            sub_lord_sign = (
                p7.get("rasi") or p7.get("sign") or
                p7.get("zodiac") or p7.get("pseudo_rasi")
            )

        notes.append(f"7th Cusp Sub-Lord → {sub_lord_7 or 'N/A'} in {sub_lord_sign or 'N/A'}")

        sub_lord_5 = get_cusp_sub_lord(5, houses)
        verdict = kp_check_promise(
            planets=planets,
            houses=houses,
            csl_house=5,
            promise_houses={5, 7, 11},
            obstacle_houses={6, 8, 12}
        )

        state = verdict["state"]

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

        sig_5 = set(get_signified_houses(sub_lord_5, planets, houses) if sub_lord_5 else [])
        sig_7 = set(get_signified_houses(sub_lord_7, planets, houses) if sub_lord_7 else [])

        if any(h in sig_5 for h in (2, 7, 11)):
            score["outcome"] += 5
            notes.append("💞 Love connects to Marriage houses — strong promise")
            add("5th lord connects to marriage houses → stability")
        elif any(h in sig_5 for h in (6, 8, 12)):
            score["breakup_risk"] -= 6
            notes.append("💔 Love house linked to 6/8/12 — emotional strain likely")
            add("5th lord in dusthana → relationship challenges")

        if sub_lord_5 and sub_lord_5 == sub_lord_7:
            score["compatibility"] += 3
            notes.append("✨ Same sub-lord for 5th & 7th → harmony")
            add("Same sub-lord for both houses indicates emotional alignment")

        love_to_marriage = bool(sig_5 & {7, 11})
        marriage_from_love = bool(sig_7 & {5, 11})

        if love_to_marriage and marriage_from_love:
            score["outcome"] += 6
            score["compatibility"] += 3
            add("Strong love-to-marriage connection")
        elif love_to_marriage:
            score["outcome"] += 3
        elif marriage_from_love:
            score["outcome"] += 2
        else:
            add("Love and marriage indicators are independent")

        if any(h in sig_5 for h in (1, 6, 10, 12)):
            score["breakup_risk"] -= 4
            add("5th house shows obstacles in converting love to marriage")

        Ve = get_planet("Venus", planets)
        Mo = get_planet("Moon", planets)
        Ma = get_planet("Mars", planets)
        Sa = get_planet("Saturn", planets)

        if Ve:
            if _is_benefic(Ve):
                score["attraction"] += 5
            if _has_evil_aspect(Ve, planets):
                score["breakup_risk"] -= 5
                add("Venus has malefic aspects → relationship instability")
            if Ve.get("debilitated") or Ve.get("is_debilitated"):
                score["compatibility"] -= 3
                add("Weak Venus affects relationship endurance")
            ve_house = Ve.get("house")
            if ve_house in [6, 8, 12]:
                score["breakup_risk"] -= 5
                add("Venus in difficult house increases separation risk")

        if Mo and _has_evil_aspect(Mo, planets):
            score["breakup_risk"] -= 3
            add("Moon affliction creates emotional turbulence")

        if Ma and _has_evil_aspect(Ma, planets):
            score["breakup_risk"] -= 3
            add("Mars affliction increases conflict potential")

        if Sa and _has_evil_aspect(Sa, Ve):
            score["attraction"] -= 3
            add("Saturn-Venus affliction creates relationship obstacles")

        total_score = sum(score.values())
        breakup_risk = score["breakup_risk"]

        if breakup_risk < -10:
            risk_level = "HIGH"
            risk_percentage = 75
            summary = "High risk of separation. Urgent remedies recommended."
        elif breakup_risk < -5:
            risk_level = "MODERATE"
            risk_percentage = 50
            summary = "Moderate separation risk. Focus on communication."
        elif breakup_risk < 0:
            risk_level = "LOW"
            risk_percentage = 25
            summary = "Some challenges exist but relationship can be strengthened."
        else:
            risk_level = "VERY_LOW"
            risk_percentage = 10
            summary = "Stable relationship with good compatibility."

        if score["breakup_risk"] < -5:
            remedies.append("Strengthen Venus: Chant 'Om Shukraya Namaha' on Fridays")
            remedies.append("Practice couples counseling")
            remedies.append("Spend quality time together")

        return {
            "breakup_risk": breakup_risk,
            "risk_level": risk_level,
            "risk_percentage": risk_percentage,
            "attraction_score": score["attraction"],
            "compatibility_score": score["compatibility"],
            "outcome_score": score["outcome"],
            "total_score": total_score,
            "summary": summary,
            "points": points,
            "notes": notes,
            "remedies": remedies,
            "csl_5": sub_lord_5,
            "csl_7": sub_lord_7,
            "promise_5_state": state,
            "promise_7_state": verdict.get("state", "unknown"),
            "sign_7th": sub_lord_sign
        }

    # --------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="LOVE_BREAKUP_1",
                question="Should I stay in my current relationship or consider a breakup and what is the risk of separation?",
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Challenges and Possibility of Separation"
            ),
            Question(
                id="LOVE_BREAKUP_2",
                question="I have experienced a breakup - will my partner return to me?",
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Possibility of Reconciliation"
            ),
            Question(
                id="LOVE_BREAKUP_3",
                question="What can I do to avoid a breakup and strengthen my relationship?",
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Relationship Advice"
            )
        ]
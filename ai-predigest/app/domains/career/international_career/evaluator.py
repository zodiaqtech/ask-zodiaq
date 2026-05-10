"""
International Career Evaluator - ENHANCED VERSION v4.0

FIXES FROM v3.0:
✅ Added _extract_lagna_info() - was missing entirely
✅ Added _log_result_breakdown() - for consistency with CareerDiscoveryEvaluator
✅ Fixed _extract_timing_windows() - local `result` variable shadowed outer scope
✅ Fixed _calculate_lord_strength() - aligned signature/logic with doc1 (string dignity, not enum)
✅ Removed leftover debug pprint block (was logging raw vedic_planets/vedic_houses unconditionally)
✅ Lagna info now stored in result.additional_data (aligned with doc1/doc2 pattern)
✅ _store_data_for_llm() now includes lagna_info storage
✅ domain_prefix changed to "international_career" to avoid key collision with CareerDiscovery
✅ Sub-subdomain handling strengthened - lagna stored for all question types
✅ House analysis points now also triggered for "Foreign Settlement" sub-subdomain
✅ LLM-only fallback now stores data before returning (was returning before _store_data_for_llm)
✅ Added missing all_relevant_houses.add(1) for lagna lord analysis (aligned with doc2)
✅ Analysis summary now logged after extraction (aligned with doc1)

Architecture:
- evaluate() → Main entry point with unified flow
- _extract_lagna_info() → Lagna/ascendant info extraction
- _extract_house_lords() → House lord data with dignity
- _extract_aspects_on_houses() → Benefic/malefic aspect data
- _extract_timing_windows() → Best + nearest timing windows
- _add_house_analysis_points() → KP evaluation points
- _store_data_for_llm() → Stores all structured data
- _log_result_breakdown() → Debug logging
"""

from typing import Dict, List, Optional, Set
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

from app.domains.career.kp_career_engine import (
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


class InternationalCareerEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Career → International Career
    v4.0 - Aligned with CareerDiscoveryAndEmploymentEvaluator architecture.

    Key Houses for Foreign Career:
    - 12th: Foreign lands, overseas settlement, distant places
    - 9th: Long-distance travel, fortune abroad, higher opportunities
    - 3rd: Short travels, communication, courage to relocate
    - 7th: Foreign business, partnerships abroad
    - 4th: Home (leaving home = foreign settlement)
    - 10th: Career (combined with 12th = foreign career)
    """

    domain = "Career"
    subtopic = "International Career"

    # House meanings for international career context
    HOUSE_MEANINGS = {
        3: "Short Travel/Courage",
        4: "Home/Motherland",
        7: "Foreign Business/Partners",
        9: "Long Travel/Fortune Abroad",
        10: "Career/Profession",
        12: "Foreign Lands/Settlement"
    }

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

        # ═══════════════════════════════════════════════════════
        # STEP 0: Choose Data Source for House Lord Analysis
        # ═══════════════════════════════════════════════════════
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
            # ✅ ALWAYS include house 1 for lagna lord analysis (aligned with doc2)
            all_relevant_houses.add(1)
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning("No config for question, using fallback")
            all_relevant_houses = {1, 3, 4, 7, 9, 10, 12}
            primary_houses = {12, 9, 7}
            secondary_houses = {3, 4, 10}

        # Get metadata
        meta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "International Career")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, "query_type") else None

        logger.info("=" * 80)
        logger.info("INTERNATIONAL CAREER EVALUATOR (ENHANCED v4.0)")
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
        # STEP 3.5: Extract Lagna Information (FIX - was missing in v3.0)
        # ═══════════════════════════════════════════════════════
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")

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
        # ═══════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: timing_windows_raw keys: {list(timing_windows_raw.keys()) if isinstance(timing_windows_raw, dict) else 'N/A'}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            if not timing_windows_list and "Foreign Career Potential" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Foreign Career Potential"]
                logger.info(f"🔍 DEBUG: Using 'Foreign Career Potential' fallback key, found {len(timing_windows_list)} windows")

            if not timing_windows_list and "International Career" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["International Career"]
                logger.info("🔍 DEBUG: Using 'International Career' fallback key")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        if timing_windows_data and timing_windows_data.get("has_timing"):
            best = timing_windows_data.get("best_window", {})
            nearest = timing_windows_data.get("nearest_window", {})
            logger.warning(
                f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:\n"
                f"   🏆 BEST: {best.get('dasha', 'N/A')} "
                f"({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) "
                f"- Score: {best.get('final_score', 0):.1f}\n"
                f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} "
                f"({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) "
                f"- Score: {nearest.get('final_score', 0):.1f}"
            )
        else:
            logger.info(f"❌ No timing windows available for '{sub_subdomain}'")

        # ═══════════════════════════════════════════════════════
        # STEP 6: KP Structural Foreign Career Analysis
        # ═══════════════════════════════════════════════════════
        if sub_subdomain == "Foreign Career Potential":
            foreign_struct = evaluate_foreign_career_exposure(
                planets=planets,
                houses=houses,
                planet_chain=None
            )

            result.add_point(
                f"KP structural foreign career assessment: "
                f"{foreign_struct['exposure_level']}."
            )

            if foreign_struct.get("indicators"):
                result.add_point(
                    "Key KP foreign indicators: "
                    + "; ".join(foreign_struct["indicators"][:4])
                )

            result.additional_data["career_foreign_structural"] = foreign_struct

        # ═══════════════════════════════════════════════════════
        # STEP 7: Add House Analysis Points
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"Foreign Career Potential", "Foreign Settlement"}:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ═══════════════════════════════════════════════════════
        # STEP 8: Sub-subdomain Specific Logic
        # ═══════════════════════════════════════════════════════

        # --- Foreign Career Potential (Core + Timing) ---
        if sub_subdomain == "Foreign Career Potential":

            if meta and meta_query_type == QueryType.TIMING:
                try:
                    timing_rules = TIMING_RULES.get("Foreign Career Potential", {})
                    planet_scores = score_kp_all_planets(planets, houses, timing_rules)
                    positive_planets = get_positive_planets(planet_scores)

                    if positive_planets:
                        result.add_point(
                            f"Favorable dasha lords for foreign career or overseas opportunities: "
                            f"{', '.join(positive_planets[:4])}."
                        )

                    ruling_planets = get_kp_ruling_planets(planets)
                    if ruling_planets:
                        result.add_point(
                            f"KP ruling planets supporting foreign travel or settlement: "
                            f"{', '.join(ruling_planets[:4])}."
                        )

                    if not positive_planets:
                        result.add_point(
                            "Foreign career indicators are present but not strongly activated at this time."
                        )

                except Exception as e:
                    logger.warning(f"Timing evaluation error: {e}")
                    result.add_point(
                        "Foreign career timing indicators could not be conclusively determined."
                    )
            else:
                result.add_point(
                    "Foreign career potential is assessed using planetary connections "
                    "to travel, relocation, and overseas professional houses."
                )

        # --- Remedies ---
        elif sub_subdomain == "Career Remedies":
            result.add_point(
                "Foreign career remedies focus on strengthening planets governing "
                "travel, adaptability, and global exposure."
            )

        # --- LLM-only sub-subdomains ---
        elif sub_subdomain in {"Career Analysis and Advice (LLM)", "Further Studies Advice"}:
            result.add_point(
                "This question is evaluated using experiential, educational, and contextual factors "
                "rather than predictive astrology."
            )
            # ✅ FIX: Store data BEFORE returning (v3.0 was missing this)
            self._store_data_for_llm(
                result, house_config, house_lords_info, house_aspects_info,
                primary_houses, secondary_houses, timing_windows_data
            )
            if lagna_info:
                result.additional_data["lagna_info"] = lagna_info
            return result

        # --- Fallback ---
        else:
            result.add_point(
                "International career indicators exist, but this query is handled "
                "outside strict astrological evaluation."
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
            timing_windows_data
        )

        # ✅ Store lagna info (FIX - was missing in v3.0)
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        # Add any accumulated self.points
        if hasattr(self, "points") and self.points:
            for point in self.points:
                result.add_point(point)

        self._log_result_breakdown(result, sub_subdomain)

        return result

    # ═══════════════════════════════════════════════════════════════
    # LAGNA EXTRACTION (FIX - was missing entirely in v3.0)
    # ═══════════════════════════════════════════════════════════════

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

            return {
                "lagna_sign": lagna_sign,
                "lagna_lord": lagna_lord,
                "lagna_lord_house": lagna_lord_data.get("house"),
                "lagna_lord_sign": lagna_lord_data.get("sign", ""),
                "lagna_lord_degree": (
                    lagna_lord_data.get("full_degree") or
                    lagna_lord_data.get("degree") or 0
                ),
                "lagna_lord_dignity": self._get_planet_dignity(lagna_lord, lagna_lord_data),
            }

        except Exception as e:
            logger.error(f"Error extracting lagna info: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════
    # PLANET DIGNITY (FIX - used by _extract_lagna_info, was missing)
    # ═══════════════════════════════════════════════════════════════

    def _get_planet_dignity(self, planet_name: str, planet_data: Dict) -> str:
        """Get dignity of a planet as a string."""
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

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION (FIX - `result` variable collision)
    # ═══════════════════════════════════════════════════════════════

    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        Handles both dict and TimingWindow dataclass objects.

        FIX: Renamed inner `result` dict to `extracted` to avoid
        shadowing the outer EvaluationResult `result` variable.
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

                converted = {
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
                        converted[extra_field] = val

                return converted

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

            # ✅ FIX: renamed from `result` to `extracted` to avoid variable collision
            extracted = {
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

            return extracted

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    # ═══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
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

        sign_lords_map = {
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
                    lord_name = sign_lords_map.get(sign, "")
                    if lord_name:
                        logger.debug(f"✅ Deduced lord {lord_name} for house {house_num} from sign {sign}")

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
                lord_data.get("degree") or 0
            )
            lord_is_combust = (
                lord_data.get("is_combusted", False) or
                lord_data.get("is_combust", False)
            )
            lord_is_retrograde = (
                lord_data.get("is_retro", False) or
                lord_data.get("is_retrograde", False)
            )

            # ✅ FIX: Use string dignity via _get_planet_dignity (aligned with doc1)
            lord_dignity = self._get_planet_dignity(normalized_lord, lord_data)
            lord_strength_score = self._calculate_lord_strength(
                normalized_lord, lord_data, lord_dignity
            )

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

    # ═══════════════════════════════════════════════════════════════
    # ASPECTS ON HOUSES
    # ═══════════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════════
    # LORD STRENGTH (FIX - aligned signature with doc1: string dignity)
    # ═══════════════════════════════════════════════════════════════

    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity: str = "NEUTRAL"   # ✅ FIX: takes string, not enum object
    ) -> int:
        """
        Calculate lord strength score (0-100).
        FIX: Now accepts dignity as a plain string (aligned with doc1).
        v3.0 was accepting a LordDignity enum object and calling .value on it,
        which caused AttributeError when called with string from _get_planet_dignity().
        """
        dignity_str = dignity.upper() if isinstance(dignity, str) else "NEUTRAL"

        dignity_scores = {
            "EXALTED": 100,
            "OWN_SIGN": 80,
            "OWN SIGN": 80,
            "NEUTRAL": 50,
            "FRIENDLY": 60,
            "ENEMY": 30,
            "DEBILITATED": 20
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
            planet_data.get("degree") or 15
        )
        if degree < 5 or degree > 25:
            score -= 10

        return max(0, min(100, score))

    # ═══════════════════════════════════════════════════════════════
    # HOUSE ANALYSIS POINTS
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

            point_parts = [
                f"⭐ House {house_num} ({self._get_house_meaning(house_num)}):",
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

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for international career context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    # ═══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM (FIX - domain_prefix & lagna storage added)
    # ═══════════════════════════════════════════════════════════════

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
        """
        Store all enhanced data in additional_data for LLM consumption.

        FIX: domain_prefix changed from "career" to "international_career"
        to avoid key collisions when both this evaluator and CareerDiscovery
        evaluator run in the same session.
        """
        domain_prefix = "international_career"

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
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data [{domain_prefix}_timing_windows]")
            if timing_windows_data.get("best_window"):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE (data: {bool(timing_windows_data)})")

    # ═══════════════════════════════════════════════════════════════
    # LOG RESULT BREAKDOWN (FIX - was missing entirely in v3.0)
    # ═══════════════════════════════════════════════════════════════

    def _log_result_breakdown(self, result: EvaluationResult, sub_subdomain: str):
        """Log result breakdown for debugging. Aligned with doc1."""
        logger.info("🧩 RESULT BREAKDOWN")
        logger.info(f"Sub-subdomain: {sub_subdomain}")

        points = getattr(result, "points", []) or []
        logger.info(f"Total points: {len(points)}")

        ad = result.additional_data or {}
        logger.info(f"Additional data keys: {list(ad.keys())}")

        foreign_struct = ad.get("career_foreign_structural", {})
        if foreign_struct:
            logger.warning(f"🟣 FINAL KP DATA SENT TO LLM: {foreign_struct}")

    # ═══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ═══════════════════════════════════════════════════════════════

    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="CAR_IC_1",
                question=(
                    "Is it advisable for me to go abroad, and what are my prospects "
                    "for working or settling in a foreign country?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.POSITIVE,
                    InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Foreign Career Potential"
            )
        ]
"""
Marriage Legal Dispute Evaluator – VEDIC-ONLY v2.0

Specialized evaluator for analyzing marriage-related legal disputes including
divorce, dowry cases, alimony, custody, and domestic disputes using traditional
Vedic astrology principles.

✔ COMPLETE structural parity with Property Legal Dispute evaluator
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Marriage-specific house analysis (7th house prominence)
✔ Venus as Kalatra Karaka analysis
✔ Complete data storage for LLM
✔ Lagna info extraction (v2.0)
✔ Timing windows extraction (v2.0)
✔ House 1 always included in analysis (v2.0)

Key Houses for Marriage Legal Disputes:
- 7th: Marriage, spouse, marital harmony (PRIMARY)
- 2nd: Family, family wealth, kutumb (family disputes)
- 4th: Domestic happiness, home environment
- 6th: Litigation, disputes, enemies, legal battles
- 8th: Hidden matters, in-laws' wealth (dowry), sudden events
- 9th: Legal proceedings, higher courts, justice, dharma
- 11th: Gains, victory, favorable outcomes
- 12th: Losses, expenses, separation, bed pleasures

Karakas:
- Venus: Kalatra Karaka (spouse significator) - Most important
- Jupiter: Husband (for female), dharma, justice, children
- Mars: Aggression, conflict, Manglik dosha considerations
- Moon: Mind, emotions, mental state during dispute
- Saturn: Delays, separation, karma, legal processes
- Rahu: Unconventional situations, deception, foreign elements
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
from app.core.astro_constants import detect_aspects, normalize_planet_name

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
    logging.info("House lords analyzer available for Marriage Legal domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "marriage_legal"


class MarriageLegalDisputeEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Legal → Marriage Court Case

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Outcome likelihood assessment
    - Duration indicators
    - Risk and penalty analysis
    - Marriage-specific analysis (7th house focus)
    - Venus (Kalatra Karaka) analysis
    - Lagna info extraction
    - Timing windows extraction
    - NO KP analysis (purely Vedic)

    Traditional Vedic Rules for Marriage Legal Disputes:
    - 7th house = Marriage, spouse, marital matters (PRIMARY)
    - 7th lord afflicted = Marital discord, disputes
    - Venus afflicted = Problems with spouse/marriage
    - 6th house connection to 7th = Litigation in marriage
    - 8th house = In-laws, dowry, hidden issues
    - 12th house = Separation, losses, bed pleasures denied
    - Saturn aspecting 7th = Delays, coldness, separation
    - Mars aspecting 7th = Aggression, conflict (Manglik)
    - Rahu in 7th = Unconventional marriage issues
    """

    domain = "Legal"
    subtopic = "Marriage Court Case"

    # House meanings for marriage legal context
    HOUSE_MEANINGS = {
        1: "Self/Native",
        2: "Family/Kutumb",
        4: "Domestic Happiness",
        5: "Children/Progeny",
        6: "Litigation/Disputes",
        7: "Spouse/Marriage",
        8: "In-laws/Dowry/Hidden",
        9: "Justice/Dharma",
        11: "Victory/Gains",
        12: "Losses/Separation"
    }

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
            logger.warning(f"No config for question, using fallback for Marriage Legal")
            # Default houses for Marriage Legal Disputes
            # 7th = marriage (PRIMARY), 6th = litigation, 8th = in-laws/dowry
            # 9th = justice, 11th = victory, 12th = separation/losses
            primary_houses = {7, 6, 9, 11}
            secondary_houses = {1, 2, 4, 5, 8, 12}
            all_relevant_houses = primary_houses | secondary_houses

        # ✅ ALWAYS include house 1 for lagna lord analysis
        all_relevant_houses.add(1)

        logger.info("=" * 80)
        logger.info("MARRIAGE LEGAL DISPUTE EVALUATOR (VEDIC-ONLY v2.0)")
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
        # STEP 4: Extract House Lords Data
        # ═══════════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 4.5: Extract Lagna (Ascendant) Information
        # ═══════════════════════════════════════════════════════════
        lagna_info = self._extract_lagna_info(analysis_houses, analysis_planets)

        if lagna_info:
            logger.info(f"✅ Lagna extracted: {lagna_info['lagna_sign']} (Lord: {lagna_info['lagna_lord']})")
        else:
            logger.warning("⚠️ Could not extract lagna information")

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Extract Aspects on Houses
        # ═══════════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════════
        # STEP 5.5: Extract Timing Windows
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        logger.info(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.info(f"🔍 DEBUG: timing_windows_raw keys: {list(timing_windows_raw.keys()) if isinstance(timing_windows_raw, dict) else 'N/A'}")
        logger.info(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            if not timing_windows_list and "Marriage Legal Dispute" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Marriage Legal Dispute"]
                logger.info(f"🔍 DEBUG: Using 'Marriage Legal Dispute' fallback key, found {len(timing_windows_list)} windows")
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.info(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            logger.info(f"❌ No timing windows available for '{sub_subdomain}'")

        # ═══════════════════════════════════════════════════════════
        # STEP 6: Marriage-Specific Analysis
        # ═══════════════════════════════════════════════════════════
        marriage_analysis = self._analyze_marriage_indicators(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Marriage analysis: {marriage_analysis.get('marriage_situation', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Vedic Outcome Analysis
        # ═══════════════════════════════════════════════════════════
        outcome_analysis = self._analyze_outcome_prospects(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info,
            marriage_analysis
        )

        logger.info(f"✅ Outcome analysis: {outcome_analysis.get('likelihood', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Duration Analysis
        # ═══════════════════════════════════════════════════════════
        duration_analysis = self._analyze_duration(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Duration indicated: {duration_analysis.get('duration_category', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Risk and Penalty Analysis
        # ═══════════════════════════════════════════════════════════
        risk_analysis = self._analyze_risks_and_penalties(
            analysis_planets,
            house_lords_info,
            house_aspects_info,
            marriage_analysis
        )

        logger.info(f"✅ Risk level: {risk_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Add Marriage Legal-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_marriage_legal_points(
            result,
            marriage_analysis,
            outcome_analysis,
            duration_analysis,
            risk_analysis
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 12: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            marriage_analysis,
            outcome_analysis,
            duration_analysis,
            risk_analysis,
            timing_windows_data,
            kwargs
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 13: Store Lagna Info
        # ═══════════════════════════════════════════════════════════
        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        return result

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO EXTRACTION
    # ══════════════════════════════════════════════════════════════
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
        - lagna_lord_dignity: Dignity of the lagna lord
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
                house_1.get("sign_lord") or
                house_1.get("rashi_lord") or
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

                    if hasattr(analyzer, '_get_dignity'):
                        dignity = analyzer._get_dignity(
                            lagna_lord,
                            lagna_lord_sign,
                            lagna_lord_degree
                        )
                    elif hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(lagna_lord)
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(lagna_lord)

                    if dignity:
                        lagna_lord_dignity = dignity.value if hasattr(dignity, 'value') else str(dignity)
                except Exception as e:
                    logger.warning(f"Could not get lagna lord dignity: {e}")

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

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.

        Handles both dict and TimingWindow object formats.

        Best window: Highest score (best planetary alignment)
        Nearest window: Earliest favorable window (soonest opportunity)

        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        - has_timing: bool
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}

        try:
            # Helper: get attribute from either dict or TimingWindow object
            def get_attr(obj, key, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # Helper: convert TimingWindow object or dict to standardized dict
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
                if not isinstance(first, dict):
                    logger.info(f"🔍 First window attributes: {vars(first) if hasattr(first, '__dict__') else 'N/A'}")

            # Sort by final_score
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            # Nearest: earliest window with score >= 50
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

    # ══════════════════════════════════════════════════════════════
    # MARRIAGE-SPECIFIC ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_marriage_indicators(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze marriage-specific indicators using Vedic principles.

        Key indicators for marriage disputes:
        - 7th house and its lord (primary marriage house)
        - Venus (Kalatra Karaka - spouse significator)
        - Jupiter (for females - husband karaka)
        - 8th house (in-laws, dowry, mangalya)
        - 2nd house (family, kutumb)
        - 4th house (domestic happiness)
        - 12th house (bed pleasures, separation)
        """
        analysis = {
            "marriage_situation": "MODERATE",
            "marriage_score": 50,
            "seventh_house_strength": "MODERATE",
            "venus_strength": "MODERATE",
            "favorable_factors": [],
            "unfavorable_factors": [],
            "marriage_hints": [],
            "dispute_type_indicators": []
        }

        score = 50  # Start neutral

        # ═══════════════════════════════════════════════════════════
        # 7th HOUSE ANALYSIS (Most Important for Marriage)
        # ═══════════════════════════════════════════════════════════
        h7_info = house_lords_info.get(7, {})
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            h7_lord = h7_info.get("lord", "")
            h7_lord_house = h7_info.get("lord_in_house")

            if h7_strength >= 70:
                score += 12
                analysis["seventh_house_strength"] = "STRONG"
                analysis["favorable_factors"].append(
                    f"7th lord {h7_lord} is strong ({h7_strength}/100) - favorable for marriage matters"
                )
            elif h7_strength >= 50:
                analysis["seventh_house_strength"] = "MODERATE"
                analysis["marriage_hints"].append(
                    f"7th lord {h7_lord} has moderate strength - balanced marriage indications"
                )
            else:
                score -= 10
                analysis["seventh_house_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    f"7th lord {h7_lord} is weak ({h7_strength}/100) - marriage matters face challenges"
                )

            # 7th lord placement analysis
            if h7_lord_house in [1, 4, 5, 9, 10, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"7th lord in house {h7_lord_house} - favorable placement for marriage case"
                )
            elif h7_lord_house == 6:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "7th lord in 6th house - litigation and disputes in marriage indicated"
                )
                analysis["dispute_type_indicators"].append("Strong litigation tendency")
            elif h7_lord_house == 8:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "7th lord in 8th house - hidden issues, possible dowry/inheritance disputes"
                )
                analysis["dispute_type_indicators"].append("Hidden issues or in-laws problems")
            elif h7_lord_house == 12:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "7th lord in 12th house - separation tendencies, losses through spouse"
                )
                analysis["dispute_type_indicators"].append("Separation or loss indicated")

        # ═══════════════════════════════════════════════════════════
        # VENUS ANALYSIS (Kalatra Karaka - Spouse Significator)
        # ═══════════════════════════════════════════════════════════
        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_house = venus_data.get("house")
            venus_sign = venus_data.get("sign", "")

            # ──────────────────────────────────────────────────
            # VENUS DIGNITY (STRICT VEDIC — NO ENEMY CONFUSION)
            # ──────────────────────────────────────────────────
            venus_exalted = {"Pisces"}
            venus_own = {"Taurus", "Libra"}
            venus_debilitated = {"Virgo"}

            if venus_sign in venus_exalted:
                score += 15
                analysis["venus_strength"] = "VERY_STRONG"
                analysis["favorable_factors"].append(
                    f"Venus exalted in {venus_sign} - excellent support for marriage matters"
                )

            elif venus_sign in venus_own:
                score += 12
                analysis["venus_strength"] = "STRONG"
                analysis["favorable_factors"].append(
                    f"Venus in own sign {venus_sign} - strong spouse significator"
                )

            elif venus_sign in venus_debilitated:
                score -= 15
                analysis["venus_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    f"Venus debilitated in {venus_sign} - marriage significator weakened"
                )

            else:
                analysis["venus_strength"] = "MODERATE"
                analysis["marriage_hints"].append(
                    f"Venus in {venus_sign} - neutral dignity for marriage matters"
                )

            # Venus house placement
            if venus_house == 7:
                score += 5
                analysis["marriage_hints"].append(
                    "Venus in 7th house - strong focus on marriage matters"
                )
            elif venus_house == 6:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "Venus in 6th house - disputes affecting marriage happiness"
                )
            elif venus_house == 8:
                score -= 5
                analysis["marriage_hints"].append(
                    "Venus in 8th house - transformation in marriage, possible dowry issues"
                )
            elif venus_house == 12:
                score -= 5
                analysis["marriage_hints"].append(
                    "Venus in 12th house - losses or separation in marriage"
                )

            # Venus combustion (hard penalty)
            if venus_data.get("is_combust") or venus_data.get("is_combusted"):
                score -= 12
                analysis["venus_strength"] = "WEAK"
                analysis["unfavorable_factors"].append(
                    "Venus combust - spouse karaka significantly weakened"
                )

        # ═══════════════════════════════════════════════════════════
        # 7th HOUSE AFFLICTIONS
        # ═══════════════════════════════════════════════════════════
        h7_aspects = house_aspects_info.get(7, {})

        # Mars aspecting 7th (Manglik consideration)
        if "Mars" in h7_aspects.get("malefic_aspects", []):
            score -= 8
            analysis["unfavorable_factors"].append(
                "Mars aspects 7th house - aggression and conflict in marriage"
            )
            analysis["dispute_type_indicators"].append("Aggressive disputes likely")

        # Saturn aspecting 7th
        if "Saturn" in h7_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["marriage_hints"].append(
                "Saturn aspects 7th house - delays, coldness, or separation tendencies"
            )

        # Rahu aspecting or in 7th
        rahu_data = planets.get("Rahu", {})
        if rahu_data and rahu_data.get("house") == 7:
            score -= 10
            analysis["unfavorable_factors"].append(
                "Rahu in 7th house - unconventional issues, possible deception in marriage"
            )
            analysis["dispute_type_indicators"].append("Deception or unconventional issues")
        elif "Rahu" in h7_aspects.get("malefic_aspects", []):
            score -= 5
            analysis["marriage_hints"].append(
                "Rahu aspects 7th house - confusion or unconventional marriage issues"
            )

        # Ketu in 7th
        ketu_data = planets.get("Ketu", {})
        if ketu_data and ketu_data.get("house") == 7:
            score -= 8
            analysis["unfavorable_factors"].append(
                "Ketu in 7th house - detachment, spiritual differences, or past karma in marriage"
            )

        # Jupiter aspecting 7th (beneficial)
        if "Jupiter" in h7_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 7th house - divine grace protects marriage matters"
            )

        # ═══════════════════════════════════════════════════════════
        # 8th HOUSE (In-laws, Dowry, Mangalya)
        # ═══════════════════════════════════════════════════════════
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")

            # 8th lord in 7th - problems from in-laws affecting marriage
            if h8_lord_house == 7:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "8th lord in 7th house - in-laws or hidden issues affecting marriage"
                )
                analysis["dispute_type_indicators"].append("In-laws involvement likely")

        # ═══════════════════════════════════════════════════════════
        # 6th HOUSE (Litigation)
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_house = h6_info.get("lord_in_house")

            # 6th lord in 7th - litigation in marriage
            if h6_lord_house == 7:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "6th lord in 7th house - strong litigation tendency in marriage"
                )
                analysis["dispute_type_indicators"].append("Legal battle in marriage confirmed")

        # ═══════════════════════════════════════════════════════════
        # 2nd HOUSE (Family)
        # ═══════════════════════════════════════════════════════════
        h2_info = house_lords_info.get(2, {})
        h2_aspects = house_aspects_info.get(2, {})
        if h2_info:
            h2_strength = h2_info.get("lord_strength_score", 50)
            if h2_strength >= 70:
                score += 5
                analysis["favorable_factors"].append(
                    "2nd lord strong - family support in dispute"
                )

            # Malefics on 2nd - family discord
            malefics_on_2 = h2_aspects.get("malefic_aspects", [])
            if len(malefics_on_2) >= 2:
                score -= 5
                analysis["marriage_hints"].append(
                    "Family house afflicted - family discord contributing to dispute"
                )

        # ═══════════════════════════════════════════════════════════
        # 4th HOUSE (Domestic Happiness)
        # ═══════════════════════════════════════════════════════════
        h4_info = house_lords_info.get(4, {})
        if h4_info:
            h4_strength = h4_info.get("lord_strength_score", 50)
            if h4_strength < 40:
                score -= 5
                analysis["marriage_hints"].append(
                    "4th lord weak - domestic happiness disturbed"
                )

        # Determine marriage situation
        score = max(0, min(100, score))
        analysis["marriage_score"] = score

        if score >= 70:
            analysis["marriage_situation"] = "FAVORABLE"
        elif score >= 55:
            analysis["marriage_situation"] = "MODERATE_FAVORABLE"
        elif score >= 45:
            analysis["marriage_situation"] = "MODERATE"
        elif score >= 30:
            analysis["marriage_situation"] = "CHALLENGING"
        else:
            analysis["marriage_situation"] = "DIFFICULT"

        # ──────────────────────────────────────────────────
        # SAFETY CLAMP: prevent Venus-neutral charts collapsing
        # ──────────────────────────────────────────────────
        if analysis["venus_strength"] == "MODERATE" and score < 40:
            score += 5
            analysis["marriage_score"] = score

        return analysis

    # ══════════════════════════════════════════════════════════════
    # OUTCOME PROSPECTS ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_outcome_prospects(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        marriage_analysis: Dict
    ) -> Dict:
        """
        Analyze legal outcome prospects for marriage dispute.
        """
        analysis = {
            "likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "strategic_hints": []
        }

        # Start with marriage analysis score as base modifier
        marriage_score = marriage_analysis.get("marriage_score", 50)
        score = 50 + (marriage_score - 50) * 0.3  # 30% influence from marriage score

        # ═══════════════════════════════════════════════════════════
        # 6th HOUSE (Litigation Ability)
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            if h6_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is strong ({h6_strength}/100) - good litigation ability"
                )
            elif h6_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is weak - may struggle in legal battles"
                )

        # ═══════════════════════════════════════════════════════════
        # 9th HOUSE (Justice)
        # ═══════════════════════════════════════════════════════════
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            if h9_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is strong - justice favors you"
                )
            elif h9_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"9th lord {h9_info.get('lord')} is weak - legal proceedings may be challenging"
                )

        # ═══════════════════════════════════════════════════════════
        # 11th HOUSE (Victory)
        # ═══════════════════════════════════════════════════════════
        h11_info = house_lords_info.get(11, {})
        if h11_info:
            h11_strength = h11_info.get("lord_strength_score", 50)
            if h11_strength >= 70:
                score += 10
                analysis["favorable_factors"].append(
                    f"11th lord {h11_info.get('lord')} is strong - victory supported"
                )
            elif h11_strength < 40:
                score -= 6
                analysis["unfavorable_factors"].append(
                    f"11th lord weak - achieving desired outcome requires extra effort"
                )

        # ═══════════════════════════════════════════════════════════
        # 1st vs 7th (Self vs Spouse/Opponent)
        # ═══════════════════════════════════════════════════════════
        h1_info = house_lords_info.get(1, {})
        h7_info = house_lords_info.get(7, {})
        if h1_info and h7_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            h7_strength = h7_info.get("lord_strength_score", 50)

            if h1_strength > h7_strength + 15:
                score += 10
                analysis["favorable_factors"].append(
                    "Your significator (1st lord) stronger than spouse/opponent - advantageous position"
                )
            elif h7_strength > h1_strength + 15:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "Spouse/opponent's significator (7th lord) stronger - may face strong opposition"
                )
                analysis["strategic_hints"].append(
                    "Consider mediation or settlement to avoid prolonged battle"
                )

        # ═══════════════════════════════════════════════════════════
        # 12th HOUSE (Losses)
        # ═══════════════════════════════════════════════════════════
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            h12_lord_house = h12_info.get("lord_in_house")

            if h12_strength >= 70:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"12th lord strong - potential for expenses and losses"
                )

            # 12th lord in 7th - losses through spouse
            if h12_lord_house == 7:
                score -= 8
                analysis["unfavorable_factors"].append(
                    "12th lord in 7th house - losses through marriage/spouse indicated"
                )
                analysis["strategic_hints"].append(
                    "Be prepared for financial implications in settlement"
                )

        # ═══════════════════════════════════════════════════════════
        # JUPITER (Karaka for Law and for Husband)
        # ═══════════════════════════════════════════════════════════
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 7, 9, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine grace supports your case"
                )
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - may face challenges in getting justice"
                )

        # Check Jupiter aspecting 7th or 9th
        h7_aspects = house_aspects_info.get(7, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Jupiter" in h7_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 7th house - marriage matters protected"
            )

        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 8
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - strong support for justice"
            )

        # ═══════════════════════════════════════════════════════════
        # MOON (Mental State - Important in Family Disputes)
        # ═══════════════════════════════════════════════════════════
        moon_data = planets.get("Moon", {})
        if moon_data:
            moon_house = moon_data.get("house")
            if moon_house in [6, 8, 12]:
                analysis["strategic_hints"].append(
                    "Moon placement suggests emotional stress - consider emotional support/counseling"
                )

        # Determine likelihood
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 70:
            analysis["likelihood"] = "FAVORABLE"
        elif score >= 55:
            analysis["likelihood"] = "MODERATELY_FAVORABLE"
        elif score >= 45:
            analysis["likelihood"] = "UNCERTAIN"
        elif score >= 30:
            analysis["likelihood"] = "CHALLENGING"
        else:
            analysis["likelihood"] = "UNFAVORABLE"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # DURATION ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_duration(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze expected duration of marriage legal proceedings.
        Family court cases can vary significantly in duration.
        """
        analysis = {
            "duration_category": "MODERATE",
            "duration_score": 50,
            "delay_factors": [],
            "speed_factors": [],
            "duration_hints": []
        }

        duration_score = 50

        # ═══════════════════════════════════════════════════════════
        # SATURN (Primary Karaka for Delays)
        # ═══════════════════════════════════════════════════════════
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")

            if saturn_house in [6, 7, 9, 12]:
                duration_score += 18
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays in marriage case"
                )

            if saturn_data.get("is_retro") or saturn_data.get("is_retrograde"):
                duration_score += 10
                analysis["delay_factors"].append(
                    "Saturn retrograde - prolonged proceedings, revisiting old issues"
                )

        # Saturn aspects on key houses
        h7_aspects = house_aspects_info.get(7, {})
        h9_aspects = house_aspects_info.get(9, {})

        if "Saturn" in h7_aspects.get("malefic_aspects", []):
            duration_score += 12
            analysis["delay_factors"].append(
                "Saturn aspects 7th house - marriage matters significantly delayed"
            )

        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            duration_score += 10
            analysis["delay_factors"].append(
                "Saturn aspects 9th house - legal proceedings delayed"
            )

        # ═══════════════════════════════════════════════════════════
        # 7th LORD RETROGRADE
        # ═══════════════════════════════════════════════════════════
        h7_info = house_lords_info.get(7, {})
        if h7_info and h7_info.get("lord_is_retrograde"):
            duration_score += 10
            analysis["delay_factors"].append(
                f"7th lord {h7_info.get('lord')} retrograde - marriage case may drag on"
            )

        # ═══════════════════════════════════════════════════════════
        # 6th LORD RETROGRADE
        # ═══════════════════════════════════════════════════════════
        h6_info = house_lords_info.get(6, {})
        if h6_info and h6_info.get("lord_is_retrograde"):
            duration_score += 8
            analysis["delay_factors"].append(
                f"6th lord retrograde - litigation process slowed"
            )

        # ═══════════════════════════════════════════════════════════
        # RAHU/KETU INVOLVEMENT
        # ═══════════════════════════════════════════════════════════
        rahu_data = planets.get("Rahu", {})
        ketu_data = planets.get("Ketu", {})

        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [6, 7, 9]:
                duration_score += 10
                analysis["delay_factors"].append(
                    f"Rahu in house {rahu_house} - unexpected complications and delays"
                )

        if ketu_data:
            ketu_house = ketu_data.get("house")
            if ketu_house in [6, 7, 9]:
                duration_score += 5
                analysis["duration_hints"].append(
                    "Ketu's influence may bring sudden twists in proceedings"
                )

        # ═══════════════════════════════════════════════════════════
        # SPEED FACTORS
        # ═══════════════════════════════════════════════════════════
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            if mercury_house in [1, 5, 9, 11]:
                duration_score -= 8
                analysis["speed_factors"].append(
                    "Mercury well-placed - communication and proceedings smoother"
                )

        venus_data = planets.get("Venus", {})
        if venus_data:
            venus_sign = venus_data.get("sign", "")
            if venus_sign in ["Taurus", "Libra", "Pisces"]:
                duration_score -= 5
                analysis["speed_factors"].append(
                    "Venus strong - possibility of amicable settlement"
                )

        # Benefics in key houses
        for h_num in [6, 7, 9, 11]:
            h_aspects = house_aspects_info.get(h_num, {})
            benefics = h_aspects.get("benefic_aspects", [])
            if "Jupiter" in benefics:
                duration_score -= 5
                analysis["speed_factors"].append(
                    f"Jupiter aspects house {h_num} - may help expedite matters"
                )
                break  # Count only once

        # Determine duration category
        duration_score = max(0, min(100, duration_score))
        analysis["duration_score"] = duration_score

        if duration_score >= 75:
            analysis["duration_category"] = "VERY_LONG"
            analysis["duration_hints"].append(
                "Marriage disputes can be emotionally draining - prepare for extended timeline"
            )
        elif duration_score >= 60:
            analysis["duration_category"] = "LONG"
            analysis["duration_hints"].append(
                "Case may take considerable time - patience and persistence required"
            )
        elif duration_score >= 45:
            analysis["duration_category"] = "MODERATE"
            analysis["duration_hints"].append(
                "Moderate timeline expected for family court proceedings"
            )
        elif duration_score >= 30:
            analysis["duration_category"] = "SHORT"
            analysis["duration_hints"].append(
                "Relatively quicker resolution possible, especially if settlement reached"
            )
        else:
            analysis["duration_category"] = "VERY_SHORT"
            analysis["duration_hints"].append(
                "Quick settlement or mutual resolution indicated"
            )

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISK AND PENALTY ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks_and_penalties(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict,
        marriage_analysis: Dict
    ) -> Dict:
        """
        Analyze potential risks and penalties for marriage dispute.
        Includes alimony, custody, dowry case implications.
        """
        analysis = {
            "risk_level": "MODERATE",
            "risk_score": 50,
            "risk_factors": [],
            "penalty_indicators": [],
            "mitigation_hints": [],
            "areas_of_concern": []
        }

        risk_score = 50

        # ═══════════════════════════════════════════════════════════
        # 12th HOUSE (Losses, Expenses)
        # ═══════════════════════════════════════════════════════════
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_lord_house = h12_info.get("lord_in_house")
            h12_strength = h12_info.get("lord_strength_score", 50)

            if h12_lord_house == 7:
                risk_score += 15
                analysis["risk_factors"].append(
                    "12th lord in 7th house - significant financial losses through spouse/marriage"
                )
                analysis["areas_of_concern"].append("Financial settlement may be unfavorable")

            if h12_lord_house == 2:
                risk_score += 10
                analysis["risk_factors"].append(
                    "12th lord in 2nd house - family wealth at risk"
                )
                analysis["areas_of_concern"].append("Family assets may be affected")

            if h12_strength >= 70:
                risk_score += 8
                analysis["penalty_indicators"].append(
                    f"12th lord strong - potential for substantial losses/alimony"
                )

        # ═══════════════════════════════════════════════════════════
        # 8th HOUSE (Hidden Issues, Dowry, In-laws)
        # ═══════════════════════════════════════════════════════════
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            h8_strength = h8_info.get("lord_strength_score", 50)

            if h8_lord_house in [1, 7]:
                risk_score += 12
                analysis["risk_factors"].append(
                    f"8th lord in house {h8_lord_house} - hidden issues may surface"
                )
                analysis["areas_of_concern"].append("Unexpected revelations or accusations")

            if h8_strength >= 70:
                risk_score += 8
                analysis["penalty_indicators"].append(
                    "8th house strong - dowry or inheritance issues may complicate case"
                )

        # ═══════════════════════════════════════════════════════════
        # MARS AFFLICTION (Aggression, False Accusations)
        # ═══════════════════════════════════════════════════════════
        mars_data = planets.get("Mars", {})
        h7_aspects = house_aspects_info.get(7, {})

        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house == 7:
                risk_score += 12
                analysis["risk_factors"].append(
                    "Mars in 7th house - aggressive disputes, possible domestic violence allegations"
                )
                analysis["areas_of_concern"].append("DV or 498A allegations possible")
                analysis["mitigation_hints"].append(
                    "Document all interactions carefully"
                )
            elif mars_house == 6:
                risk_score += 8
                analysis["risk_factors"].append(
                    "Mars in 6th house - aggressive litigation approach from opponent"
                )

        if "Mars" in h7_aspects.get("malefic_aspects", []):
            risk_score += 8
            analysis["risk_factors"].append(
                "Mars aspects 7th house - conflict and aggression in proceedings"
            )

        # ═══════════════════════════════════════════════════════════
        # RAHU (Deception, False Cases, Unconventional Issues)
        # ═══════════════════════════════════════════════════════════
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house == 7:
                risk_score += 15
                analysis["risk_factors"].append(
                    "Rahu in 7th house - deception, false allegations, or unconventional accusations"
                )
                analysis["areas_of_concern"].append("False accusations or manipulation risk")
                analysis["mitigation_hints"].append(
                    "Gather strong evidence and witnesses"
                )
            elif rahu_house in [1, 6, 12]:
                risk_score += 8
                analysis["risk_factors"].append(
                    f"Rahu in house {rahu_house} - unexpected complications"
                )

        # ═══════════════════════════════════════════════════════════
        # SATURN IN 12th (Severe Penalties)
        # ═══════════════════════════════════════════════════════════
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house == 12:
                risk_score += 6
                analysis["risk_factors"].append(
                    "Saturn in 12th house - prolonged expenses and emotional distance"
                )
                analysis["mitigation_hints"].append(
                    "Seek experienced family lawyer immediately"
                )

        # ═══════════════════════════════════════════════════════════
        # 5th HOUSE (Children - Custody Risk)
        # ═══════════════════════════════════════════════════════════
        h5_info = house_lords_info.get(5, {})
        h5_aspects = house_aspects_info.get(5, {})
        if h5_info:
            h5_strength = h5_info.get("lord_strength_score", 50)
            malefics_on_5 = h5_aspects.get("malefic_aspects", [])

            if (h5_strength < 40 or len(malefics_on_5) >= 2) and "Jupiter" not in h5_aspects.get("benefic_aspects", []):
                risk_score += 8
                analysis["areas_of_concern"].append("Child custody may be contested")
                analysis["risk_factors"].append(
                    "5th house afflicted - custody battles may be challenging"
                )

        # ═══════════════════════════════════════════════════════════
        # 2nd HOUSE (Family, Finances in Settlement)
        # ═══════════════════════════════════════════════════════════
        h2_aspects = house_aspects_info.get(2, {})
        malefics_on_2 = h2_aspects.get("malefic_aspects", [])

        if "Saturn" in malefics_on_2 or "Rahu" in malefics_on_2:
            risk_score += 8
            analysis["penalty_indicators"].append(
                "Malefic influence on 2nd house - financial penalties or unfavorable settlement"
            )

        # ═══════════════════════════════════════════════════════════
        # BENEFICIAL MITIGATIONS
        # ═══════════════════════════════════════════════════════════
        if "Jupiter" in h7_aspects.get("benefic_aspects", []):
            risk_score -= 10
            analysis["mitigation_hints"].append(
                "Jupiter's grace on 7th house provides protection in marriage matters"
            )

        h9_aspects = house_aspects_info.get(9, {})
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            risk_score -= 8
            analysis["mitigation_hints"].append(
                "Jupiter's aspect on 9th house - dharmic protection in legal matters"
            )

        if marriage_analysis.get("venus_strength") == "STRONG":
            risk_score -= 5
            analysis["mitigation_hints"].append(
                "Strong Venus indicates possibility of amicable settlement"
            )

        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 75:
            analysis["risk_level"] = "VERY_HIGH"
        elif risk_score >= 60:
            analysis["risk_level"] = "HIGH"
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
        elif risk_score >= 25:
            analysis["risk_level"] = "LOW"
        else:
            analysis["risk_level"] = "VERY_LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS EXTRACTION
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
        """Extract house lord information for relevant houses only."""
        house_lords_info = {}

        for h in houses:
            house_num = h.get("house")

            if house_num not in relevant_houses:
                continue

            # Get lord name
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

                    dignity = analyzer._get_dignity(
                        normalized_lord,
                        lord_sign,
                        lord_degree
                    )
                    lord_dignity = dignity.value

                    if dignity:
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
    # ASPECTS EXTRACTION
    # ══════════════════════════════════════════════════════════════
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

    # ══════════════════════════════════════════════════════════════
    # STRENGTH CALCULATION
    # ══════════════════════════════════════════════════════════════
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

        degree = (
            planet_data.get("full_degree") or
            planet_data.get("global_degree") or
            planet_data.get("degree") or
            15
        )
        if degree < 5 or degree > 25:
            score -= 10

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for marriage legal context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD HOUSE ANALYSIS POINTS
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
    # ADD MARRIAGE LEGAL-SPECIFIC POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_marriage_legal_points(
        self,
        result: EvaluationResult,
        marriage_analysis: Dict,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risk_analysis: Dict
    ):
        """Add marriage legal-specific points to result."""

        # Marriage situation
        marriage_situation = marriage_analysis.get("marriage_situation", "MODERATE")
        marriage_score = marriage_analysis.get("marriage_score", 50)
        result.add_point(
            f"💒 Marriage Situation: {marriage_situation} (Score: {marriage_score}/100)"
        )

        # 7th house strength
        h7_strength = marriage_analysis.get("seventh_house_strength", "MODERATE")
        result.add_point(f"🏠 7th House Strength: {h7_strength}")

        # Venus (Kalatra Karaka) strength
        venus_strength = marriage_analysis.get("venus_strength", "MODERATE")
        result.add_point(f"♀️ Venus (Kalatra Karaka): {venus_strength}")

        # Outcome likelihood
        likelihood = outcome_analysis.get("likelihood", "UNCERTAIN")
        score = outcome_analysis.get("score", 50)
        result.add_point(
            f"⚖️ Outcome Likelihood: {likelihood} (Score: {score}/100)"
        )

        # Duration
        duration = duration_analysis.get("duration_category", "MODERATE")
        result.add_point(f"⏰ Expected Duration: {duration}")

        # Risk level
        risk_level = risk_analysis.get("risk_level", "MODERATE")
        risk_score = risk_analysis.get("risk_score", 50)
        result.add_point(f"🚨 Risk Level: {risk_level} (Score: {risk_score}/100)")

        # Dispute type indicators
        dispute_types = marriage_analysis.get("dispute_type_indicators", [])
        if dispute_types:
            result.add_point(f"📋 Dispute Indicators: {', '.join(dispute_types[:3])}")

        # Marriage-specific favorable factors
        for factor in marriage_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")

        # Outcome favorable factors
        for factor in outcome_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")

        # Unfavorable factors
        for factor in marriage_analysis.get("unfavorable_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")

        # Risk factors
        for factor in risk_analysis.get("risk_factors", [])[:2]:
            result.add_point(f"🚨 {factor}")

        # Areas of concern
        concerns = risk_analysis.get("areas_of_concern", [])
        if concerns:
            result.add_point(f"⚠️ Areas of Concern: {', '.join(concerns[:3])}")

    # ══════════════════════════════════════════════════════════════
    # STORE DATA FOR LLM
    # ══════════════════════════════════════════════════════════════
    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        marriage_analysis: dict,
        outcome_analysis: dict,
        duration_analysis: dict,
        risk_analysis: dict,
        timing_windows_data: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

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

            # Marriage-specific analysis
            f"{DOMAIN_PREFIX}_marriage_analysis": marriage_analysis,

            # Outcome analysis
            f"{DOMAIN_PREFIX}_outcome_analysis": outcome_analysis,

            # Duration analysis
            f"{DOMAIN_PREFIX}_duration_analysis": duration_analysis,

            # Risk analysis
            f"{DOMAIN_PREFIX}_risk_analysis": risk_analysis,

            # Analysis summary
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "primary_houses_count": len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "marriage_situation": marriage_analysis.get("marriage_situation", "MODERATE"),
                "marriage_score": marriage_analysis.get("marriage_score", 50),
                "seventh_house_strength": marriage_analysis.get("seventh_house_strength", "MODERATE"),
                "venus_strength": marriage_analysis.get("venus_strength", "MODERATE"),
                "dispute_type_indicators": marriage_analysis.get("dispute_type_indicators", []),
                "outcome_likelihood": outcome_analysis.get("likelihood", "UNCERTAIN"),
                "outcome_score": outcome_analysis.get("score", 50),
                "duration_category": duration_analysis.get("duration_category", "MODERATE"),
                "risk_level": risk_analysis.get("risk_level", "MODERATE"),
                "risk_score": risk_analysis.get("risk_score", 50),
                "areas_of_concern": risk_analysis.get("areas_of_concern", []),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                )
            },
        })

        # ✅ Store timing windows if available
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {DOMAIN_PREFIX}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
            if timing_windows_data.get('best_window'):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE (data: {bool(timing_windows_data)})")

        logger.info(
            f"📦 STORED | marriage={marriage_analysis.get('marriage_situation')} | "
            f"outcome={outcome_analysis.get('likelihood')} | "
            f"duration={duration_analysis.get('duration_category')} | "
            f"risk={risk_analysis.get('risk_level')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="MARRIAGE_LEGAL_MAIN",
                question=(
                    "What does astrology reveal about the outcome, duration, "
                    "risks and potential penalties of my marriage-related legal issues, "
                    "such as dowry, divorce, or alimony?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Marriage Legal Dispute"
            )
        ]
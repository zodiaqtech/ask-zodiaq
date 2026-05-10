"""
Family Legal Issue Evaluator – VEDIC-ONLY v1.0

Specialized evaluator for family legal disputes, court cases, and litigation
related queries using traditional Vedic astrology principles.

✔ COMPLETE structural parity with Travel/Finance/Parenting/Lost evaluators
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Timing windows for legal case questions
✔ Legal outcome analysis
✔ Risk and penalty assessment
✔ Duration estimation
✔ Complete data storage for LLM

Key Houses for Family Legal Issues:
- 6th: Litigation, disputes, enemies, obstacles, legal battles
- 7th: Opponents, other party in dispute, partnerships, contracts
- 8th: Sudden events, penalties, fines, hidden matters, inheritance disputes
- 9th: Dharma, justice, higher courts, appeals, legal wisdom
- 12th: Losses, expenses, imprisonment, settlements

Supporting Houses:
- 1st: Self, overall strength, ability to fight the case
- 4th: Family, property matters, domestic peace, real estate disputes
- 10th: Authority, government, judges, reputation, career impact
- 11th: Gains, favorable outcomes, success in litigation

Karakas:
- Saturn: Justice, delays, karma, punishment
- Jupiter: Dharma, judges, wisdom, fairness, protection
- Mars: Fighting spirit, aggression, litigation energy
- Sun: Authority, government, judges, power
- Mercury: Documentation, contracts, communication, lawyers
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
    logging.info("House lords analyzer available for Family Legal Issue domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "family_legal"


class FamilyLegalIssueEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Family Legal Issue → Family Legal Dispute

    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity
    - Aspects extraction (benefic/malefic/neutral)
    - Strength scoring (0-100)
    - Legal outcome prediction
    - Risk and penalty assessment
    - Duration estimation
    - Timing windows extraction
    - NO KP analysis (purely Vedic)

    Traditional Vedic Rules for Legal Matters:
    - 6th house strong = Victory in litigation
    - 7th house afflicted = Weak opponent
    - 8th house afflicted = Penalties and hidden problems
    - 9th house strong = Justice prevails, favorable higher court
    - Jupiter strong = Divine justice, favorable judgment
    - Saturn strong = Karma, delayed but fair outcome
    - Mars strong = Fighting ability, aggression in court
    """

    domain = "Family Legal Issue"
    subtopic = "Family Legal Issue"

    # ══════════════════════════════════════════════════════════════
    # LEGAL TIMING CONSIDERATIONS (Vedic)
    # ══════════════════════════════════════════════════════════════
    AUSPICIOUS_LEGAL_DAYS = {
        "Sunday": {"deity": "Sun", "suitable_for": "Government matters, authority cases, appeals to higher courts"},
        "Monday": {"deity": "Moon", "suitable_for": "Family matters, emotional appeals, custody cases"},
        "Tuesday": {"deity": "Mars", "suitable_for": "Aggressive litigation, property disputes, fighting cases"},
        "Wednesday": {"deity": "Mercury", "suitable_for": "Documentation, contracts, communication with lawyers"},
        "Thursday": {"deity": "Jupiter", "suitable_for": "Appeals, seeking justice, dharmic matters, favorable judgments"},
        "Friday": {"deity": "Venus", "suitable_for": "Settlements, mediation, compromise agreements"},
        "Saturday": {"deity": "Saturn", "suitable_for": "Long-term cases, karma-related matters, final judgments"}
    }

    # Legal house significance
    LEGAL_HOUSE_MEANINGS = {
        1: "Self/Native's strength in litigation",
        4: "Family/Property matters/Domestic disputes",
        6: "Litigation/Disputes/Enemies/Legal battles",
        7: "Opponent/Other party/Contracts",
        8: "Penalties/Fines/Hidden matters/Sudden events",
        9: "Justice/Higher courts/Appeals/Dharma",
        10: "Authority/Judges/Government/Reputation",
        11: "Gains/Victory/Favorable outcomes",
        12: "Losses/Expenses/Imprisonment/Settlements"
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
            logger.warning(f"No config for question, using fallback for Family Legal Issue")
            # Default houses for Family Legal Issue domain
            # 6th = litigation, 7th = opponent, 8th = penalties
            # 9th = justice, 12th = losses
            primary_houses = {6, 7, 8, 9}
            secondary_houses = {1, 4, 10, 11, 12}
            all_relevant_houses = primary_houses | secondary_houses

        # Always include house 1 for lagna lord analysis
        all_relevant_houses.add(1)

        logger.info("=" * 80)
        logger.info("FAMILY LEGAL ISSUE EVALUATOR (VEDIC-ONLY v1.0)")
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
        # STEP 4.5: Extract Lagna Information
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
        # STEP 6: Extract Timing Windows
        # ═══════════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})
        timing_windows_list = []

        if isinstance(timing_windows_raw, dict):
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")

            # Fallback keys
            if not timing_windows_list and "Family Legal Dispute" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Family Legal Dispute"]
            if not timing_windows_list and "Legal Timing" in timing_windows_raw:
                timing_windows_list = timing_windows_raw["Legal Timing"]
        else:
            timing_windows_list = timing_windows_raw if timing_windows_raw else []

        timing_windows_data = {}
        if meta_query_type == QueryType.TIMING and timing_windows_list:
            timing_windows_data = self._extract_timing_windows(timing_windows_list) or {}
            logger.info("✅ TIMING ENABLED")
        else:
            timing_windows_data = {"has_timing": False}

        # ═══════════════════════════════════════════════════════════
        # STEP 7: Legal Outcome Analysis
        # ═══════════════════════════════════════════════════════════
        outcome_analysis = self._analyze_legal_outcome(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Legal outcome: {outcome_analysis.get('outcome_prediction', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 8: Duration Analysis
        # ═══════════════════════════════════════════════════════════
        duration_analysis = self._analyze_case_duration(
            analysis_planets,
            analysis_houses,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Case duration: {duration_analysis.get('duration_estimate', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 9: Risk and Penalty Analysis
        # ═══════════════════════════════════════════════════════════
        risks_analysis = self._analyze_risks_and_penalties(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        logger.info(f"✅ Risk level: {risks_analysis.get('risk_level', 'Unknown')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 10: Auspicious Timing Hints
        # ═══════════════════════════════════════════════════════════
        timing_hints = self._get_auspicious_timing_hints(
            analysis_planets,
            house_lords_info,
            sub_subdomain
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 11: Add House Analysis Points
        # ═══════════════════════════════════════════════════════════
        self._add_house_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses
        )

        # ═══════════════════════════════════════════════════════════
        # STEP 12: Add Legal-Specific Points
        # ═══════════════════════════════════════════════════════════
        self._add_legal_points(result, outcome_analysis, duration_analysis, risks_analysis)

        # ═══════════════════════════════════════════════════════════
        # STEP 13: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data,
            outcome_analysis,
            duration_analysis,
            risks_analysis,
            timing_hints,
            kwargs
        )

        if lagna_info:
            result.additional_data["lagna_info"] = lagna_info

        return result

    # ══════════════════════════════════════════════════════════════
    # LEGAL OUTCOME ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_legal_outcome(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze legal outcome prospects using Vedic principles.

        Key indicators:
        - 6th house (litigation, victory over enemies)
        - 7th house (opponent's strength)
        - 9th house (justice, dharma)
        - 1st vs 7th comparison (native vs opponent)
        - Jupiter (divine justice)
        - Saturn (karma, delays but fair outcome)
        """
        analysis = {
            "outcome_prediction": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "victory_indicators": [],
            "settlement_indicators": [],
            "recommendations": []
        }

        score = 50

        # Check 6th house (primary for litigation victory)
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            h6_lord = h6_info.get("lord", "")
            h6_lord_house = h6_info.get("lord_in_house")

            if h6_strength >= 70:
                score += 20
                analysis["favorable_factors"].append(
                    f"6th lord {h6_lord} is strong ({h6_strength}/100) - victory in litigation likely"
                )
                analysis["victory_indicators"].append(
                    "Strong 6th house lord indicates native can overcome legal challenges"
                )
            elif h6_strength >= 50:
                score += 10
                analysis["favorable_factors"].append(
                    f"6th lord {h6_lord} is moderately placed - litigation efforts supported"
                )
            elif h6_strength < 40:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_lord} is weak ({h6_strength}/100) - legal battles may be challenging"
                )

            # 6th lord in good houses for litigation
            if h6_lord_house in [3, 6, 10, 11]:
                score += 10
            elif h6_lord_house in [8, 12]:
                score -= 10

                analysis["victory_indicators"].append(
                    f"6th lord in house {h6_lord_house} - strong position for winning cases"
                )

        # Check 7th house (opponent's strength)
        h7_info = house_lords_info.get(7, {})
        if h7_info:
            h7_strength = h7_info.get("lord_strength_score", 50)
            h7_lord = h7_info.get("lord", "")

            # Weak 7th lord = weak opponent (good for native)
            if h7_strength < 40:
                score += 15
                analysis["favorable_factors"].append(
                    f"7th lord {h7_lord} is weak ({h7_strength}/100) - opponent is not strong"
                )
                analysis["victory_indicators"].append(
                    "Opponent's position is weakened in the dispute"
                )
            elif h7_strength >= 70:
                score -= 10
                analysis["unfavorable_factors"].append(
                    f"7th lord {h7_lord} is strong ({h7_strength}/100) - opponent has strong position"
                )

        # Check 9th house (justice and dharma)
        h9_info = house_lords_info.get(9, {})
        if h9_info:
            h9_strength = h9_info.get("lord_strength_score", 50)
            h9_lord = h9_info.get("lord", "")

            if h9_strength >= 70:
                score += 15
                analysis["favorable_factors"].append(
                    f"9th lord {h9_lord} is strong ({h9_strength}/100) - justice will prevail"
                )
                analysis["victory_indicators"].append(
                    "Divine justice supports the native's position"
                )
            elif h9_strength < 40:
                analysis["unfavorable_factors"].append(
                    f"9th lord {h9_lord} is weak - appeals and higher court matters may face obstacles"
                )

        # Check 1st house (native's overall strength)
        h1_info = house_lords_info.get(1, {})
        if h1_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            h1_lord = h1_info.get("lord", "")

            if h1_strength >= 60:
                score += 10
                analysis["favorable_factors"].append(
                    f"Lagna lord {h1_lord} is strong - native has strength to fight the case"
                )

        # Check Jupiter (karaka for justice)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            jupiter_retro = jupiter_data.get("is_retro", False)

            if jupiter_house in [1, 5, 9, 10, 11] and jupiter_data.get("lord_status") not in {"Malefic", "Highly Malefic"}:
                score += 15
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - divine justice and fair judgment indicated"
                )
                analysis["recommendations"].append("Thursday is auspicious for court appearances")
            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - may face some judicial challenges"
                )

            if jupiter_retro:
                analysis["favorable_factors"].append(
                    "Retrograde Jupiter indicates revisiting of judgment or appeals may be favorable"
                )

        # Check Saturn (karaka for karma and justice)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")

            if saturn_house in [3, 6, 11]:
                score += 10
                analysis["favorable_factors"].append(
                    f"Saturn in house {saturn_house} - karmic justice supports native"
                )
            elif saturn_house == 7:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "Saturn in 7th - delays and obstacles from opponent"
                )

        # Check benefic aspects on 6th house
        h6_aspects = house_aspects_info.get(6, {})
        if "Jupiter" in h6_aspects.get("benefic_aspects", []):
            score += 10
            analysis["favorable_factors"].append(
                "Jupiter aspects 6th house - legal battles blessed with wisdom"
            )
        if "Saturn" in h6_aspects.get("malefic_aspects", []):
            analysis["unfavorable_factors"].append(
                "Saturn aspects 6th house - prolonged litigation expected"
            )

        # Settlement indicators
        h12_info = house_lords_info.get(12, {})
        venus_data = planets.get("Venus", {})

        if venus_data and venus_data.get("house") in [6, 7]:
            analysis["settlement_indicators"].append(
                "Venus position suggests settlement or compromise may be possible"
            )
            analysis["recommendations"].append("Friday is favorable for mediation or settlement talks")

        if h12_info and h12_info.get("lord_strength_score", 50) >= 60:
            if h12_info.get("lord_in_house") in [7, 9]:
                analysis["settlement_indicators"].append(
                    "12th lord placement indicates possibility of out-of-court settlement"
                )

        # Determine outcome prediction
        score = max(0, min(100, score))
        analysis["score"] = score

        if score >= 75:
            analysis["outcome_prediction"] = "HIGHLY_FAVORABLE"
        elif score >= 60:
            analysis["outcome_prediction"] = "FAVORABLE"
        elif score >= 45:
            analysis["outcome_prediction"] = "UNCERTAIN"
        elif score >= 30:
            analysis["outcome_prediction"] = "CHALLENGING"
        else:
            analysis["outcome_prediction"] = "DIFFICULT"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # CASE DURATION ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_case_duration(
        self,
        planets: Dict,
        houses: List,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze expected duration of the legal case.

        Key indicators:
        - Saturn influence (delays)
        - Rahu/Ketu influence (unexpected twists)
        - 6th house lord placement (litigation nature)
        - Retrograde planets (delays, reversals)
        """
        analysis = {
            "duration_estimate": "MODERATE",
            "score": 50,  # Higher score = longer duration
            "delay_factors": [],
            "quick_resolution_factors": [],
            "estimated_timeframe": "",
            "notes": []
        }

        duration_score = 50  # Baseline moderate duration

        # Check Saturn influence (primary delay indicator)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            saturn_retro = saturn_data.get("is_retro", False)

            if saturn_house in [6, 7, 8, 9]:
                duration_score += 20
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays expected"
                )

            if saturn_retro:
                duration_score += 15
                analysis["delay_factors"].append(
                    "Retrograde Saturn - prolonged litigation with multiple hearings"
                )

        # Check Saturn aspects on relevant houses
        for house_num in [6, 7, 9]:
            aspects = house_aspects_info.get(house_num, {})
            if "Saturn" in aspects.get("malefic_aspects", []):
                duration_score += 10
                analysis["delay_factors"].append(
                    f"Saturn aspects house {house_num} - delays in {self._get_house_meaning(house_num).lower()}"
                )

        # Check Rahu/Ketu (confusion and unexpected turns)
        rahu_data = planets.get("Rahu", {})
        ketu_data = planets.get("Ketu", {})

        if rahu_data and rahu_data.get("house") in [6, 7, 9]:
            duration_score += 15
            analysis["delay_factors"].append(
                "Rahu influence - unexpected developments and complexity in case"
            )

        if ketu_data and ketu_data.get("house") in [6, 7, 9]:
            duration_score += 10
            analysis["delay_factors"].append(
                "Ketu influence - spiritual or karmic dimensions may complicate matters"
            )

        # Check Mercury retrograde (documentation issues)
        mercury_data = planets.get("Mercury", {})
        if mercury_data and mercury_data.get("is_retro", False) and mercury_data.get("house") in [12, 8]:
            duration_score += 10
            analysis["delay_factors"].append(
                "Mercury retrograde - documentation delays, miscommunication possible"
            )

        # Check quick resolution factors
        # Mars strong in 6th = quick victory
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house == 6:
                duration_score -= 20
                analysis["quick_resolution_factors"].append(
                    "Mars in 6th house - aggressive and quick resolution possible"
                )
            elif mars_house == 11:
                duration_score -= 10
                analysis["quick_resolution_factors"].append(
                    "Mars in 11th house - gains through quick legal action"
                )

        # Jupiter in good houses = smoother process
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [9, 11]:
                duration_score -= 15
                analysis["quick_resolution_factors"].append(
                    f"Jupiter in house {jupiter_house} - smooth legal proceedings"
                )

        # 6th lord in moveable signs = faster resolution
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord_sign = h6_info.get("lord_in_sign", "")
            moveable_signs = ["Aries", "Cancer", "Libra", "Capricorn"]
            fixed_signs = ["Taurus", "Leo", "Scorpio", "Aquarius"]

            if h6_lord_sign in moveable_signs:
                duration_score -= 15
                analysis["quick_resolution_factors"].append(
                    f"6th lord in moveable sign {h6_lord_sign} - faster resolution indicated"
                )
            elif h6_lord_sign in fixed_signs:
                duration_score += 15
                analysis["delay_factors"].append(
                    f"6th lord in fixed sign {h6_lord_sign} - prolonged legal process"
                )

        # Determine duration estimate
        duration_score = max(0, min(100, duration_score))
        analysis["score"] = duration_score

        if duration_score >= 75:
            analysis["duration_estimate"] = "VERY_LONG"
            analysis["estimated_timeframe"] = "3+ years expected"
            analysis["notes"].append("Prepare for a prolonged legal battle")
        elif duration_score >= 60:
            analysis["duration_estimate"] = "LONG"
            analysis["estimated_timeframe"] = "1-3 years expected"
            analysis["notes"].append("Case may take considerable time")
        elif duration_score >= 45:
            analysis["duration_estimate"] = "MODERATE"
            analysis["estimated_timeframe"] = "6 months to 1 year"
            analysis["notes"].append("Average duration for such matters")
        elif duration_score >= 30:
            analysis["duration_estimate"] = "SHORT"
            analysis["estimated_timeframe"] = "3-6 months"
            analysis["notes"].append("Relatively quick resolution possible")
        else:
            analysis["duration_estimate"] = "VERY_SHORT"
            analysis["estimated_timeframe"] = "Within 3 months"
            analysis["notes"].append("Quick resolution or settlement likely")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISKS AND PENALTIES ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks_and_penalties(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """
        Analyze risks and potential penalties in the legal dispute.

        Risk indicators:
        - 8th house (penalties, fines, sudden losses)
        - 12th house (losses, expenses, imprisonment)
        - Malefics in key houses
        - Mars/Saturn afflictions (harsh judgments)
        """
        analysis = {
            "risk_level": "LOW",
            "risk_score": 20,
            "risks": [],
            "potential_penalties": [],
            "financial_risks": [],
            "protective_factors": [],
            "mitigation_strategies": []
        }

        risk_score = 20  # Start low

        # Check 8th house (penalties and sudden events)
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_strength = h8_info.get("lord_strength_score", 50)
            h8_lord = h8_info.get("lord", "")
            h8_lord_house = h8_info.get("lord_in_house")

            if h8_lord_house == 6:
                risk_score += 5
            elif h8_lord_house in [1, 7]:
                risk_score += 20

                analysis["risks"].append(
                    f"8th lord in house {h8_lord_house} - penalties or fines possible"
                )
                analysis["potential_penalties"].append(
                    "Hidden aspects of case may surface adversely"
                )

            if h8_strength < 40:
                risk_score += 10
                analysis["risks"].append(
                    f"Weak 8th lord {h8_lord} - sudden adverse developments possible"
                )

        # Check 12th house (losses and expenses)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            h12_lord = h12_info.get("lord", "")
            h12_lord_house = h12_info.get("lord_in_house")

            if h12_lord_house in [1, 2, 6]:
                risk_score += 15
                analysis["financial_risks"].append(
                    "Significant legal expenses or financial losses indicated"
                )

            if h12_strength >= 60 and h12_lord_house == 12:
                analysis["risks"].append(
                    "Strong 12th house - be cautious of losses through legal process"
                )
                risk_score += 10

        # Check Mars (harsh judgments, conflicts)
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [7, 8, 12]:
                risk_score += 15
                analysis["risks"].append(
                    f"Mars in house {mars_house} - harsh treatment or aggressive opposition"
                )
                analysis["mitigation_strategies"].append(
                    "Avoid confrontational approach; seek diplomatic solutions"
                )

            # Mars aspects on 8th house
            h8_aspects = house_aspects_info.get(8, {})
            if "Mars" in h8_aspects.get("malefic_aspects", []):
                risk_score += 10
                analysis["potential_penalties"].append(
                    "Mars aspects 8th - risk of punitive damages or penalties"
                )

        # Check Saturn (delays becoming losses)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [8, 12]:
                risk_score += 15
                analysis["risks"].append(
                    f"Saturn in house {saturn_house} - prolonged suffering through legal process"
                )
                analysis["financial_risks"].append(
                    "Accumulated expenses due to delayed proceedings"
                )

        # Check Rahu (deception, hidden enemies)
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [6, 7, 8]:
                risk_score += 15
                analysis["risks"].append(
                    "Rahu influence - beware of deception or hidden agendas"
                )
                analysis["mitigation_strategies"].append(
                    "Verify all documents and claims thoroughly"
                )

        # Check protective factors
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 9, 11]:
                risk_score -= 15
                analysis["protective_factors"].append(
                    "Jupiter's blessing provides protection from severe penalties"
                )

        # Check benefic aspects on 8th and 12th houses
        for house_num in [8, 12]:
            aspects = house_aspects_info.get(house_num, {})
            benefics = aspects.get("benefic_aspects", [])

            if "Jupiter" in benefics:
                risk_score -= 10
                analysis["protective_factors"].append(
                    f"Jupiter protects house {house_num} - reduces risk of severe penalties"
                )
            if "Venus" in benefics:
                risk_score -= 5
                analysis["protective_factors"].append(
                    f"Venus aspect on house {house_num} - possibility of amicable resolution"
                )

        # Check 11th house (gains despite challenges)
        h11_info = house_lords_info.get(11, {})
        if h11_info and h11_info.get("lord_strength_score", 50) >= 60:
            risk_score -= 10
            analysis["protective_factors"].append(
                "Strong 11th house lord - ultimate gains possible despite challenges"
            )

        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 60:
            analysis["risk_level"] = "HIGH"
            analysis["mitigation_strategies"].append(
                "Consider seeking settlement to minimize potential losses"
            )
        elif risk_score >= 40:
            analysis["risk_level"] = "MODERATE"
            analysis["mitigation_strategies"].append(
                "Proceed with caution and strong legal representation"
            )
        elif risk_score >= 20:
            analysis["risk_level"] = "LOW"
        else:
            analysis["risk_level"] = "VERY_LOW"

        return analysis

    # ══════════════════════════════════════════════════════════════
    # AUSPICIOUS TIMING HINTS
    # ══════════════════════════════════════════════════════════════
    def _get_auspicious_timing_hints(
        self,
        planets: Dict,
        house_lords_info: Dict,
        sub_subdomain: str
    ) -> Dict:
        """
        Get auspicious timing hints for legal matters based on Vedic principles.
        """
        hints = {
            "best_days": [],
            "avoid_days": [],
            "best_nakshatras": [],
            "general_hints": []
        }

        # Best days for legal matters
        hints["best_days"].extend([
            "Thursday (Jupiter's day) - best for court appearances and seeking justice",
            "Sunday (Sun's day) - good for dealing with authorities and government",
            "Saturday (Saturn's day) - for karma-related matters and final judgments"
        ])

        hints["avoid_days"].extend([
            "Avoid filing cases on Amavasya (new moon)",
            "Avoid important hearings during Rahu Kaal",
            "Tuesday may increase conflict - use for aggressive defense only"
        ])

        # Best nakshatras for legal matters
        hints["best_nakshatras"].extend([
            "Pushya, Hasta, Anuradha - excellent for initiating legal action",
            "Uttara Phalguni, Uttara Ashadha - for favorable judgments",
            "Rohini, Mrigashira - for settlements and negotiations"
        ])

        # Check 6th lord for specific hints
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_lord = h6_info.get("lord", "")
            if h6_lord == "Mars":
                hints["general_hints"].append(
                    "Mars rules 6th house - Tuesday actions may be powerful but volatile"
                )
            elif h6_lord == "Jupiter":
                hints["general_hints"].append(
                    "Jupiter rules 6th house - Thursday is especially favorable for victory"
                )
            elif h6_lord == "Saturn":
                hints["general_hints"].append(
                    "Saturn rules 6th house - Saturday is significant for litigation matters"
                )
            elif h6_lord == "Venus":
                hints["general_hints"].append(
                    "Venus rules 6th house - Friday favors settlement and compromise"
                )
            elif h6_lord == "Mercury":
                hints["general_hints"].append(
                    "Mercury rules 6th house - Wednesday is good for documentation and legal arguments"
                )

        # Check Jupiter position
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [9, 11]:
                hints["general_hints"].append(
                    "Jupiter's position favors legal matters - proceed with optimism"
                )

        return hints

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION
    # ══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.

        Best window: Highest score (best planetary alignment)
        Nearest window: Earliest favorable window (soonest opportunity)

        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        """
        if not timing_windows:
            return {}

        try:
            def get_attr(obj, key, default=None):
                """Get attribute from dict or object (handles both cases)"""
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            def window_to_dict(w):
                """Convert TimingWindow object or dict to standardized dict format"""
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

    # ══════════════════════════════════════════════════════════════
    # LAGNA EXTRACTION
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
            house_1 = next((h for h in houses if h.get("house") == 1), None)

            if not house_1:
                logger.warning("⚠️ House 1 not found - cannot determine lagna")
                return None

            lagna_sign = (
                house_1.get("sign") or
                house_1.get("start_rasi") or
                house_1.get("rasi") or
                ""
            )

            if not lagna_sign:
                logger.warning("⚠️ Lagna sign not found in house 1 data")
                return None

            lagna_lord_name = (
                house_1.get("sign_lord") or
                house_1.get("rashi_lord") or
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
                logger.warning(f"⚠️ Could not determine lagna lord for {lagna_sign}")
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
                except Exception:
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

            lord_name = (
                h.get("sign_lord") or
                h.get("rashi_lord") or
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
                    if lord_name:
                        logger.debug(f"✅ Deduced lord {lord_name} for house {house_num} from sign {sign}")

            normalized_lord = normalize_planet_name(lord_name)

            if not normalized_lord:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                logger.warning(f"⚠️ No lord found for house {house_num} (sign: {sign})")
                continue

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
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for legal context."""
        return self.LEGAL_HOUSE_MEANINGS.get(house_num, "General")

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

            result.add_point(" ".join(point_parts))

    # ══════════════════════════════════════════════════════════════
    # ADD LEGAL POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_legal_points(
        self,
        result: EvaluationResult,
        outcome_analysis: Dict,
        duration_analysis: Dict,
        risks_analysis: Dict
    ):
        """Add legal-specific points to result."""

        # Legal Outcome
        outcome = outcome_analysis.get("outcome_prediction", "UNCERTAIN")
        o_score = outcome_analysis.get("score", 50)
        result.add_point(
            f"⚖️ Legal Outcome Prediction: {outcome} (Score: {o_score}/100)"
        )

        # Case Duration
        duration = duration_analysis.get("duration_estimate", "MODERATE")
        d_timeframe = duration_analysis.get("estimated_timeframe", "Unknown")
        result.add_point(
            f"⏱️ Case Duration Estimate: {duration} ({d_timeframe})"
        )

        # Risk Level
        risk_level = risks_analysis.get("risk_level", "LOW")
        r_score = risks_analysis.get("risk_score", 20)
        result.add_point(
            f"⚠️ Risk and Penalty Level: {risk_level} (Score: {r_score}/100)"
        )

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
        timing_windows_data: dict,
        outcome_analysis: dict,
        duration_analysis: dict,
        risks_analysis: dict,
        timing_hints: dict,
        kwargs: dict
    ):
        """Store all enhanced data in additional_data for LLM consumption."""

        result.additional_data.update({
            f"{DOMAIN_PREFIX}_house_config": {
                "primary": sorted(primary_houses),
                "secondary": sorted(secondary_houses),
                "source": house_config.get("source") if house_config else "fallback"
            },

            f"{DOMAIN_PREFIX}_house_lords": house_lords_info,
            f"{DOMAIN_PREFIX}_house_aspects": house_aspects_info,

            f"{DOMAIN_PREFIX}_outcome_analysis": outcome_analysis,
            f"{DOMAIN_PREFIX}_duration_analysis": duration_analysis,
            f"{DOMAIN_PREFIX}_risks_analysis": risks_analysis,
            f"{DOMAIN_PREFIX}_timing_hints": timing_hints,

            f"{DOMAIN_PREFIX}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "outcome_prediction": outcome_analysis.get("outcome_prediction", "UNCERTAIN"),
                "outcome_score": outcome_analysis.get("score", 50),
                "duration_estimate": duration_analysis.get("duration_estimate", "MODERATE"),
                "duration_timeframe": duration_analysis.get("estimated_timeframe", "Unknown"),
                "risk_level": risks_analysis.get("risk_level", "LOW"),
                "risk_score": risks_analysis.get("risk_score", 20),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info.get("lord_strength_score", 50) >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info.get("lord_strength_score", 50) < 40
                ),
            },
        })

        # Store timing windows
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS")
        else:
            result.additional_data[f"{DOMAIN_PREFIX}_timing_windows"] = {"has_timing": False}

        logger.info(
            f"📦 STORED | outcome={outcome_analysis.get('outcome_prediction')} | "
            f"duration={duration_analysis.get('duration_estimate')} | "
            f"risk={risks_analysis.get('risk_level')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="FAMILY_LEGAL_1",
                question="What does astrology reveal about the outcome, duration, risks and potential penalties related to my family dispute?",
                meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEGATIVE, InterpretationGoal.RISK),
                sub_subdomain="Family Legal Dispute"
            )
        ]
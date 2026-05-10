"""
Other Legal Dispute Evaluator – VEDIC-ONLY v1.0

General-purpose evaluator for analyzing miscellaneous legal disputes
that don't fit into specific categories (business, property, marriage, family).

Examples: Consumer disputes, criminal cases, civil suits, labor disputes,
insurance claims, contract disputes, defamation, cheque bounce, etc.

✔ Simple and straightforward structure
✔ Full house lords extraction with dignity and strength
✔ Comprehensive aspects extraction (benefic/malefic/neutral)
✔ NO KP analysis (Vedic-only domain)
✔ Complete data storage for LLM

Key Houses for General Legal Disputes:
- 6th: Litigation, disputes, enemies, legal battles (PRIMARY)
- 7th: Opponent, other party in dispute
- 8th: Hidden matters, sudden events, investigations
- 9th: Legal proceedings, higher courts, justice, dharma
- 10th: Reputation, authority, government dealings
- 11th: Gains, victory, favorable outcomes
- 12th: Losses, expenses, penalties, imprisonment

Karakas:
- Jupiter: Law, justice, judges, dharma, favorable outcomes
- Saturn: Delays, legal processes, punishment, karma
- Mars: Aggression, conflict, litigation energy
- Sun: Government, authority, power in legal matters
- Mercury: Documents, contracts, communication, evidence
"""

from typing import Dict, List, Optional
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
    logging.info("House lords analyzer available for Other Legal domain")
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "other_legal"


class OtherLegalDisputeEvaluator(BaseEvaluator):
    """
    Vedic-only evaluator for Legal → Other Legal Issue
    
    A general-purpose legal evaluator for miscellaneous legal matters.
    Simple structure focusing on core legal houses (6, 7, 9, 11, 12).
    """

    domain = "Legal"
    subtopic = "Other Legal Issue"

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

        # Normalize Meta
        meta = kwargs.get("meta")
        if isinstance(meta, dict):
            meta = QueryMeta(
                query_type=QueryType[meta.get("type", "NON_TIMING")],
                polarity=meta.get("polarity"),
                goal=meta.get("goal")
            )

        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")

        # Select Analysis Data (Vedic preferred)
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for analysis")

        # Get Question-Specific Houses or use defaults
        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = set(house_config["primary"])
            secondary_houses = set(house_config["secondary"])
        else:
            # Default houses for general legal disputes
            primary_houses = {6, 9, 11}
            secondary_houses = {1, 7, 8, 10, 12}
        
        all_relevant_houses = primary_houses | secondary_houses

        logger.info("=" * 60)
        logger.info("OTHER LEGAL DISPUTE EVALUATOR (VEDIC-ONLY v1.0)")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 60)

        # Calculate Aspects
        detect_aspects(planets)
        detect_aspects(analysis_planets)

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

        # Extract Aspects on Houses
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        # Outcome Analysis
        outcome_analysis = self._analyze_outcome_prospects(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Duration Analysis
        duration_analysis = self._analyze_duration(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Risk Analysis
        risk_analysis = self._analyze_risks(
            analysis_planets,
            house_lords_info,
            house_aspects_info
        )

        # Add Points to Result
        self._add_analysis_points(
            result,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            outcome_analysis,
            duration_analysis,
            risk_analysis
        )

        # Store Data for LLM
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            outcome_analysis,
            duration_analysis,
            risk_analysis
        )

        return result

    # ══════════════════════════════════════════════════════════════
    # OUTCOME ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_outcome_prospects(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze legal outcome prospects."""
        analysis = {
            "likelihood": "UNCERTAIN",
            "score": 50,
            "favorable_factors": [],
            "unfavorable_factors": [],
            "strategic_hints": []
        }

        score = 50

        # 6th house (litigation ability)
        h6_info = house_lords_info.get(6, {})
        if h6_info:
            h6_strength = h6_info.get("lord_strength_score", 50)
            if h6_strength >= 70:
                score += 12
                analysis["favorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is strong - good litigation ability"
                )
            elif h6_strength < 40:
                score -= 8
                analysis["unfavorable_factors"].append(
                    f"6th lord {h6_info.get('lord')} is weak - litigation may be challenging"
                )

        # 9th house (justice)
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
                    f"9th lord weak - legal proceedings may be challenging"
                )

        # 11th house (victory)
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
                    "11th lord weak - achieving desired outcome requires effort"
                )

        # 1st vs 7th comparison (self vs opponent)
        h1_info = house_lords_info.get(1, {})
        h7_info = house_lords_info.get(7, {})
        if h1_info and h7_info:
            h1_strength = h1_info.get("lord_strength_score", 50)
            h7_strength = h7_info.get("lord_strength_score", 50)
            if h1_strength > h7_strength + 15:
                score += 10
                analysis["favorable_factors"].append(
                    "Your significator stronger than opponent - advantageous position"
                )
            elif h7_strength > h1_strength + 15:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "Opponent's significator stronger - may face strong opposition"
                )
                analysis["strategic_hints"].append(
                    "Consider settlement to avoid prolonged battle"
                )

        # 12th house (losses)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            if h12_strength >= 70:
                score -= 10
                analysis["unfavorable_factors"].append(
                    "12th lord strong - potential for expenses and losses"
                )

        # Jupiter (karaka for law)
        jupiter_data = planets.get("Jupiter", {})
        if jupiter_data:
            jupiter_house = jupiter_data.get("house")
            if jupiter_house in [1, 5, 9, 11]:
                score += 8
                analysis["favorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - supportive indications for legal fairness"
                )

            elif jupiter_house in [6, 8, 12]:
                score -= 5
                analysis["unfavorable_factors"].append(
                    f"Jupiter in house {jupiter_house} - challenges in getting justice"
                )

        # Jupiter aspects on 9th
        h9_aspects = house_aspects_info.get(9, {})
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            score += 3   # instead of 8–12
            analysis["favorable_factors"].append(
                "Jupiter aspects 9th house - secondary supportive influence"
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
        """Analyze expected duration of legal proceedings."""
        analysis = {
            "duration_category": "MODERATE",
            "duration_score": 50,
            "delay_factors": [],
            "speed_factors": [],
            "duration_hints": []
        }

        duration_score = 50

        # Saturn (delays)
        saturn_data = planets.get("Saturn", {})
        if saturn_data:
            saturn_house = saturn_data.get("house")
            if saturn_house in [6, 7, 9, 10]:
                duration_score += 12
                analysis["delay_factors"].append(
                    f"Saturn in house {saturn_house} - significant delays expected"
                )
            if saturn_data.get("is_retro") or saturn_data.get("is_retrograde"):
                duration_score += 3
                analysis["delay_factors"].append(
                    "Retrograde influence suggests procedural review or revisiting steps"
                )

        # Saturn aspects on 6th or 9th
        h6_aspects = house_aspects_info.get(6, {})
        h9_aspects = house_aspects_info.get(9, {})
        
        if "Saturn" in h9_aspects.get("malefic_aspects", []):
            duration_score += 5
            analysis["delay_factors"].append(
                "Saturn aspects 9th house - legal proceedings delayed"
            )

        # 6th lord retrograde
        h6_info = house_lords_info.get(6, {})
        if h6_info and h6_info.get("lord_is_retrograde"):
            duration_score += 4
            analysis["delay_factors"].append(
                "6th lord retrograde - procedural review may slow litigation"
            )


        # Rahu involvement
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [6, 7, 9]:
                duration_score += 10
                analysis["delay_factors"].append(
                    f"Rahu in house {rahu_house} - unexpected complications"
                )

        # Speed factors
        mercury_data = planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house")
            if mercury_house in [1, 5, 9, 11]:
                duration_score -= 8
                analysis["speed_factors"].append(
                    "Mercury well-placed - proceedings smoother"
                )

        # Benefic aspects
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            duration_score -= 5
            analysis["speed_factors"].append(
                "Jupiter aspects 9th - may help expedite matters"
            )

        # Determine duration
        duration_score = max(0, min(100, duration_score))
        analysis["duration_score"] = duration_score

        if duration_score >= 70:
            analysis["duration_category"] = "VERY_LONG"
            analysis["duration_hints"].append("Prepare for extended timeline")
        elif duration_score >= 55:
            analysis["duration_category"] = "LONG"
            analysis["duration_hints"].append("Case may take considerable time")
        elif duration_score >= 40:
            analysis["duration_category"] = "MODERATE"
            analysis["duration_hints"].append("Normal timeline expected")
        elif duration_score >= 25:
            analysis["duration_category"] = "SHORT"
            analysis["duration_hints"].append("Relatively quick resolution possible")
        else:
            analysis["duration_category"] = "VERY_SHORT"
            analysis["duration_hints"].append("Quick resolution indicated")

        return analysis

    # ══════════════════════════════════════════════════════════════
    # RISK ANALYSIS
    # ══════════════════════════════════════════════════════════════
    def _analyze_risks(
        self,
        planets: Dict,
        house_lords_info: Dict,
        house_aspects_info: Dict
    ) -> Dict:
        """Analyze potential risks and penalties."""
        analysis = {
            "risk_level": "MODERATE",
            "risk_score": 50,
            "risk_factors": [],
            "penalty_indicators": [],
            "mitigation_hints": []
        }

        risk_score = 50

        # 12th house (losses)
        h12_info = house_lords_info.get(12, {})
        if h12_info:
            h12_strength = h12_info.get("lord_strength_score", 50)
            h12_lord_house = h12_info.get("lord_in_house")
            
            if h12_strength >= 70:
                risk_score += 12
                analysis["penalty_indicators"].append(
                    "12th lord strong - potential for losses/expenses"
                )
            if h12_lord_house in [1, 6, 10]:
                risk_score += 10
                analysis["risk_factors"].append(
                    f"12th lord in house {h12_lord_house} - increased pressure around expenses"
                )

        # 8th house (hidden dangers)
        h8_info = house_lords_info.get(8, {})
        if h8_info:
            h8_lord_house = h8_info.get("lord_in_house")
            if h8_lord_house in [1, 6, 10]:
                risk_score += 12
                analysis["risk_factors"].append(
                    f"8th lord in house {h8_lord_house} - hidden dangers"
                )

        # Saturn in 12th
        saturn_data = planets.get("Saturn", {})
        if saturn_data and saturn_data.get("house") == 12:
            risk_score += 12
            analysis["risk_factors"].append(
                "Saturn in 12th - heightened pressure around expenses or restrictive outcomes"
            )
            analysis["mitigation_hints"].append(
                "Seek strong legal counsel immediately"
            )

        # Rahu involvement
        rahu_data = planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house")
            if rahu_house in [1, 6, 8, 12]:
                risk_score += 10
                analysis["risk_factors"].append(
                    f"Rahu in house {rahu_house} - unexpected complications"
                )

        # Mars aggression
        mars_data = planets.get("Mars", {})
        if mars_data:
            mars_house = mars_data.get("house")
            if mars_house in [6, 7]:
                risk_score += 8
                analysis["risk_factors"].append(
                    f"Mars in house {mars_house} - aggressive opposition"
                )

        # Beneficial mitigations
        h9_aspects = house_aspects_info.get(9, {})
        if "Jupiter" in h9_aspects.get("benefic_aspects", []):
            risk_score -= 4
            analysis["mitigation_hints"].append(
                "Supportive aspects may soften severity but do not remove risk"
            )


        # Determine risk level
        risk_score = max(0, min(100, risk_score))
        analysis["risk_score"] = risk_score

        if risk_score >= 70:
            analysis["risk_level"] = "VERY_HIGH"
        elif risk_score >= 55:
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
        """Extract house lord information for relevant houses."""
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

            # Deduce from sign if not found
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
            lord_degree = lord_data.get("full_degree") or lord_data.get("degree") or 0
            lord_is_combust = lord_data.get("is_combusted", False) or lord_data.get("is_combust", False)
            lord_is_retrograde = lord_data.get("is_retro", False) or lord_data.get("is_retrograde", False)

            # Get dignity and strength
            lord_dignity = "Unknown"
            lord_strength_score = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    dignity = analyzer._get_dignity(normalized_lord, lord_sign, lord_degree)
                    lord_dignity = dignity.value
                    lord_strength_score = self._calculate_lord_strength(normalized_lord, lord_data, dignity)
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

    # ══════════════════════════════════════════════════════════════
    # STRENGTH CALCULATION
    # ══════════════════════════════════════════════════════════════
    def _calculate_lord_strength(self, planet_name: str, planet_data: dict, dignity=None) -> int:
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

        degree = planet_data.get("full_degree") or planet_data.get("degree") or 15
        if degree < 5 or degree > 25:
            score -= 10

        return max(20, min(100, score))

    # ══════════════════════════════════════════════════════════════
    # HOUSE MEANING
    # ══════════════════════════════════════════════════════════════
    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for legal context."""
        meanings = {
            1: "Self/Native",
            6: "Litigation/Disputes",
            7: "Opponent/Other Party",
            8: "Hidden Matters",
            9: "Justice/Law",
            10: "Authority/Government",
            11: "Victory/Gains",
            12: "Losses/Penalties"
        }
        return meanings.get(house_num, "General")

    # ══════════════════════════════════════════════════════════════
    # ADD ANALYSIS POINTS
    # ══════════════════════════════════════════════════════════════
    def _add_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        outcome_analysis: dict,
        duration_analysis: dict,
        risk_analysis: dict
    ):
        """Add analysis points to result."""
        
        # Outcome
        result.add_point(
            f"⚖️ Outcome: {outcome_analysis.get('likelihood')} ({outcome_analysis.get('score')}/100)"
        )
        
        # Duration
        result.add_point(
            f"⏰ Duration: {duration_analysis.get('duration_category')}"
        )
        
        # Risk
        result.add_point(
            f"🚨 Risk: {risk_analysis.get('risk_level')} ({risk_analysis.get('risk_score')}/100)"
        )

        # Primary house analysis
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue

            info = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            point_text = (
                f"⭐ H{house_num} ({self._get_house_meaning(house_num)}): "
                f"Lord {info['lord']} - {info['lord_dignity']} ({info['lord_strength_score']}/100)"
            )
            
            if info["lord_is_retrograde"]:
                point_text += " [R]"
            if info["lord_is_combust"]:
                point_text += " [C]"

            result.add_point(point_text)

        # Key factors
        for factor in outcome_analysis.get("favorable_factors", [])[:2]:
            result.add_point(f"✅ {factor}")
        for factor in outcome_analysis.get("unfavorable_factors", [])[:2]:
            result.add_point(f"⚠️ {factor}")
        for factor in risk_analysis.get("risk_factors", [])[:2]:
            result.add_point(f"🚨 {factor}")

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
        outcome_analysis: dict,
        duration_analysis: dict,
        risk_analysis: dict
    ):
        """Store data for LLM consumption."""

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
            f"{DOMAIN_PREFIX}_risk_analysis": risk_analysis,
            f"{DOMAIN_PREFIX}_analysis_summary": {
                "outcome_likelihood": outcome_analysis.get("likelihood", "UNCERTAIN"),
                "outcome_score": outcome_analysis.get("score", 50),
                "duration_category": duration_analysis.get("duration_category", "MODERATE"),
                "risk_level": risk_analysis.get("risk_level", "MODERATE"),
                "risk_score": risk_analysis.get("risk_score", 50),
            },
        })

        logger.info(
            f"📦 STORED | outcome={outcome_analysis.get('likelihood')} | "
            f"duration={duration_analysis.get('duration_category')} | "
            f"risk={risk_analysis.get('risk_level')}"
        )

    # ══════════════════════════════════════════════════════════════
    # QUESTIONS
    # ══════════════════════════════════════════════════════════════
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="OTHER_LEGAL_MAIN",
                question=(
                    "What does astrology reveal about the outcome, duration, "
                    "risks and potential penalties related to my other legal issues?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEUTRAL,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="Other Legal Dispute"
            )
        ]
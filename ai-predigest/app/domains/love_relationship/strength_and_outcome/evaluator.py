"""
Strength and Outcome Evaluator - FIXED v3.0

Finance-Architecture Parity:
✅ Consistent domain prefix: love_and_relationship_
✅ Full house lords extraction with dignity/strength
✅ House aspects extraction
✅ Timing windows (BEST + NEAREST)
✅ Centralized _store_data_for_llm()
✅ KP engine unchanged
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)

from app.domains.excel_structure_config import get_houses_for_question
from app.core.astro_constants import (
    detect_aspects, normalize_planet_name,
    get_planet, get_signified_houses, get_cusp_sub_lord,
    kp_check_promise, _is_benefic, _is_malefic,
    _has_evil_aspect, has_harmonious_aspect, _conjoined
)

try:
    from app.utils.house_lords_analyzer import HouseLordsAnalyzer
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False

logger = logging.getLogger(__name__)


class StrengthAndOutcomeEvaluator(BaseEvaluator):

    domain = "Love_Relationship"
    subtopic = "Strength And Outcome"

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

        analysis_planets = vedic_planets or planets
        analysis_houses = vedic_houses or houses

        question_text = kwargs.get("question", "")
        sub_subdomain = kwargs.get("sub_subdomain", "")
        meta = kwargs.get("meta")
        gender = kwargs.get("gender", "male")

        # Meta normalization
        meta_query_type = None
        if isinstance(meta, dict):
            meta_query_type = meta.get("query_type") or meta.get("type")
        elif meta and hasattr(meta, 'query_type'):
            meta_query_type = meta.query_type

        # Aspects detection
        detect_aspects(planets)
        detect_aspects(analysis_planets)

        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
            except Exception:
                pass

        # House config
        house_config = get_houses_for_question(self.domain, self.subtopic, question_text)

        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
        else:
            primary_houses = {5, 7}
            secondary_houses = {2, 8, 11, 12}

        all_houses = primary_houses | secondary_houses

        # Handle advisory questions (no KP evaluation)
        if sub_subdomain == "Compatibility Analysis and Advice":

            # ✅ FULL KP ANALYSIS (same as other subdomains)
            kp = self._evaluate_love_life_comprehensive(planets, houses, gender)

            # ✅ VEDIC STRUCTURE
            house_lords = self._extract_house_lords(
                analysis_houses, analysis_planets, all_houses, primary_houses
            )

            house_aspects = self._extract_aspects_on_houses(
                analysis_houses, analysis_planets, aspects_data, all_houses
            )

            result.add_point(
                "This analysis focuses on emotional compatibility, trust patterns, "
                "and relationship dynamics rather than predictive outcomes."
            )

            # 🚫 NO TIMING WINDOWS
            timing_windows_data = {}

            self._store_data_for_llm(
                result,
                house_config,
                kp,                # ✅ KP INCLUDED
                house_lords,       # ✅ VEDIC
                house_aspects,     # ✅ ASPECTS
                primary_houses,
                secondary_houses,
                timing_windows_data,
                None,
                None
            )

            return result



        # KP Analysis
        kp = self._evaluate_love_life_comprehensive(planets, houses, gender)

        marriage_promise = kp.get("marriage_promise", "weak")
        result.promise_state = f"{marriage_promise}_marriage_promise"
        result.add_point(
            f"💞 Relationship strength: {kp.get('love_status')} (Score: {kp.get('total_score')})"
        )

        # Vedic house lords & aspects
        house_lords = self._extract_house_lords(analysis_houses, analysis_planets, all_houses, primary_houses)
        house_aspects = self._extract_aspects_on_houses(analysis_houses, analysis_planets, aspects_data, all_houses)

        # Add house analysis points
        if marriage_promise != "weak":
            self._add_house_analysis_points(result, house_lords, house_aspects, primary_houses)

        # Timing windows
        timing_windows_data = {}
        if meta_query_type == QueryType.TIMING:
            timing_raw = kwargs.get("timing_windows", {})
            timing_list = []

            if isinstance(timing_raw, dict):
                timing_list = (
                    timing_raw.get(sub_subdomain) or
                    timing_raw.get("Love Leading to Marriage") or
                    timing_raw.get("Relationship Outcome") or []
                )
            else:
                timing_list = timing_raw or []

            timing_windows_data = self._extract_timing_windows(timing_list)

        # Store for LLM
        self._store_data_for_llm(
            result, house_config, kp, house_lords, house_aspects,
            primary_houses, secondary_houses, timing_windows_data,
            kwargs.get("current_dasha"), kwargs.get("dasha_timeline")
        )

        return result

    # ==================================================
    # TIMING WINDOWS EXTRACTION
    # ==================================================
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        if not timing_windows:
            return {}

        def get_attr(o, k, d=None):
            return o.get(k, d) if isinstance(o, dict) else getattr(o, k, d)

        def to_dict(w):
            return {
                "start": get_attr(w, "start"),
                "end": get_attr(w, "end"),
                "dasha": get_attr(w, "dasha"),
                "final_score": get_attr(w, "final_score"),
                "age_at_start": get_attr(w, "age_at_start"),
            }

        sorted_windows = sorted(
            timing_windows,
            key=lambda w: get_attr(w, "final_score", 0) or 0,
            reverse=True
        )

        best = to_dict(sorted_windows[0])

        favorable = [w for w in timing_windows if (get_attr(w, "final_score", 0) or 0) >= 50]
        if favorable:
            nearest = to_dict(sorted(
                favorable,
                key=lambda w: datetime.strptime(get_attr(w, "start", "9999-12-31"), "%Y-%m-%d")
            )[0])
        else:
            nearest = best

        return {
            "best_window": best,
            "nearest_window": nearest,
            "all_favorable": [to_dict(w) for w in sorted_windows[:5]],
            "has_timing": True
        }

    # ==================================================
    # HOUSE LORDS EXTRACTION
    # ==================================================
    def _extract_house_lords(self, houses, planets, relevant, primary):
        out = {}
        sign_lords = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
        }

        for h in houses:
            hn = h.get("house")
            if hn not in relevant:
                continue

            lord = normalize_planet_name(
                h.get("sign_lord") or h.get("rashi_lord") or h.get("lord") or ""
            )

            if not lord:
                sign = h.get("sign") or h.get("start_rasi") or h.get("rasi")
                if sign:
                    lord = sign_lords.get(sign, "")

            if not lord or lord not in planets:
                continue

            pdata = planets[lord]
            dignity = "Unknown"
            strength = 50

            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)
                    d = analyzer.get_planet_dignity(lord)
                    if d:
                        dignity = d.value if hasattr(d, "value") else str(d)
                        strength = self._calculate_lord_strength(lord, pdata, d)
                except Exception:
                    pass

            out[hn] = {
                "lord": lord,
                "lord_in_house": pdata.get("house"),
                "lord_in_sign": pdata.get("sign"),
                "lord_degree": pdata.get("degree"),
                "lord_is_combust": pdata.get("is_combust", False),
                "lord_is_retrograde": pdata.get("is_retrograde", False),
                "lord_dignity": dignity,
                "lord_strength_score": strength,
                "priority": "primary" if hn in primary else "secondary",
                "planets_in_house": [p.get("name") if isinstance(p, dict) else p for p in h.get("planets", [])],
                "house_sign": h.get("sign", "")
            }

        return out

    # ==================================================
    # ASPECTS EXTRACTION
    # ==================================================
    def _extract_aspects_on_houses(self, houses, planets, aspects_data, relevant):
        out = {}
        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        for hn in relevant:
            out[hn] = {"benefic_aspects": [], "malefic_aspects": [], "neutral_aspects": []}

            for p, pdata in planets.items():
                ah = aspects_data.get(p, {}).get("aspects_houses", pdata.get("aspects_houses", []))
                if hn in ah:
                    if p in benefics:
                        out[hn]["benefic_aspects"].append(p)
                    elif p in malefics:
                        out[hn]["malefic_aspects"].append(p)
                    else:
                        out[hn]["neutral_aspects"].append(p)

        return out

    # ==================================================
    # LORD STRENGTH CALCULATION
    # ==================================================
    def _calculate_lord_strength(self, planet, pdata, dignity):
        score = {
            "EXALTED": 100, "OWN_SIGN": 80, "OWN SIGN": 80,
            "FRIENDLY": 60, "NEUTRAL": 40, "ENEMY": 20, "DEBILITATED": 0
        }.get(dignity.value if hasattr(dignity, "value") else str(dignity).upper(), 50)

        if pdata.get("is_combust") or pdata.get("is_combusted"):
            score -= 30
        if pdata.get("is_retrograde") or pdata.get("is_retro"):
            score += 10 if planet in {"Saturn", "Mars"} else -10

        return max(0, min(100, score))

    # ==================================================
    # HOUSE ANALYSIS POINTS
    # ==================================================
    def _add_house_analysis_points(self, result, house_lords, house_aspects, primary):
        meanings = {
            5: "Romance/Love", 7: "Partnership/Marriage",
            8: "Transformation", 11: "Fulfillment", 2: "Family", 12: "Separation"
        }

        for h in sorted(primary):
            if h not in house_lords:
                continue

            info = house_lords[h]
            asp = house_aspects.get(h, {})

            text = (
                f"💖 House {h} ({meanings.get(h, 'General')}): "
                f"Lord {info['lord']} is {info['lord_dignity']} "
                f"(Strength {info['lord_strength_score']}/100)"
            )

            if asp.get("benefic_aspects"):
                text += f" | Benefic: {', '.join(asp['benefic_aspects'])}"
            if asp.get("malefic_aspects"):
                text += f" | Malefic: {', '.join(asp['malefic_aspects'])}"

            result.add_point(text)

    # ==================================================
    # STORE DATA FOR LLM
    # ==================================================
    def _store_data_for_llm(self, result, house_config, kp, house_lords, house_aspects,
                           primary_houses, secondary_houses, timing_data, current_dasha, dasha_timeline):

        prefix = "love_and_relationship"

        result.additional_data.update({
            f"{prefix}_house_config": {
                "primary": list(primary_houses),
                "secondary": list(secondary_houses),
                "source": house_config.get("source", "fallback") if house_config else "fallback"
            },
            f"{prefix}_house_lords": house_lords,
            f"{prefix}_house_aspects": house_aspects,
            f"{prefix}_kp_analysis": kp,
            f"{prefix}_analysis_summary": {
                "total_houses_analyzed": len(house_lords),
                "strong_lords": sum(1 for v in house_lords.values() if v["lord_strength_score"] >= 70),
                "weak_lords": sum(1 for v in house_lords.values() if v["lord_strength_score"] < 40)
            },
            "current_dasha": current_dasha,
            "dasha_timeline": dasha_timeline
        })

        if timing_data.get("has_timing"):
            result.additional_data[f"{prefix}_timing_windows"] = timing_data

    # ==================================================
    # KP ENGINE (UNCHANGED)
    # ==================================================
    def _evaluate_love_life_comprehensive(self, planets: Dict, houses: List, gender: str) -> Dict:
        score = {"attraction": 0, "breakup_risk": 0, "compatibility": 0, "outcome": 0}
        notes, remedies = [], []
        seen = set()

        def add_note(text):
            if text and text not in seen:
                notes.append(text)
                seen.add(text)

        sub_lord_7 = get_cusp_sub_lord(7, houses)
        p7 = get_planet(sub_lord_7, planets) if sub_lord_7 else None
        sub_lord_sign = p7.get("rasi") or p7.get("sign") if p7 else None

        sub_lord_5 = get_cusp_sub_lord(5, houses)
        verdict = kp_check_promise(planets, houses, csl_house=5,
                                   promise_houses={5, 7, 11}, obstacle_houses={6, 8, 12})
        state = verdict["state"]

        if state == "promised":
            add_note("💖 Love life promised — 5th CSL connects with 5/7/11.")
            score["outcome"] += 5
        elif state == "promised_with_obstacles":
            add_note("⚠️ Love promised but with obstacles — 6/8/12 active.")
            score["breakup_risk"] -= 3
        elif state == "blocked":
            add_note("💔 Love prospects blocked — 5th CSL only tied to 6/8/12.")
            score["breakup_risk"] -= 6

        sig_5 = set(get_signified_houses(sub_lord_5, planets, houses) if sub_lord_5 else [])
        sig_7 = set(get_signified_houses(sub_lord_7, planets, houses) if sub_lord_7 else [])

        if any(h in sig_5 for h in (2, 7, 11)):
            score["outcome"] += 5
            add_note("💞 Love connects to Marriage houses (2/7/11).")

        love_to_marriage = bool(sig_5 & {7, 11})
        marriage_from_love = bool(sig_7 & {5, 11})

        if love_to_marriage and marriage_from_love:
            score["outcome"] += 6
            score["compatibility"] += 3
            add_note("💞 Strong love-to-marriage connection.")
        elif love_to_marriage:
            score["outcome"] += 3

        Ve = get_planet("Venus", planets)
        if Ve:
            if _is_benefic(Ve):
                score["attraction"] += 5
            if _has_evil_aspect(Ve, planets):
                score["breakup_risk"] -= 5
                remedies.append("Strengthen Venus: Chant 'Om Shukraya Namaha' on Fridays")
            if Ve.get("house") in [5, 7]:
                score["attraction"] += 3

        total_score = sum(score.values())

        if total_score >= 30:
            love_status = "💞 Strong & Passionate Love Life"
        elif total_score >= 10:
            love_status = "💗 Balanced but Emotionally Intense"
        else:
            love_status = "⚠️ Volatile or Emotionally Complex"

        marriage_promise = "strong" if (love_to_marriage and marriage_from_love) else \
                          "moderate" if (love_to_marriage or marriage_from_love) else "weak"

        if not remedies:
            remedies.append("Maintain emotional balance through meditation")

        return {
            "attraction_score": score["attraction"],
            "relationship_risk_score": score["breakup_risk"],
            "compatibility_score": score["compatibility"],
            "outcome_score": score["outcome"],
            "total_score": total_score,
            "love_status": love_status,
            "marriage_promise": marriage_promise,
            "love_to_marriage": love_to_marriage,
            "marriage_from_love": marriage_from_love,
            "notes": notes,
            "remedies": remedies,
            "sub_lord_5": sub_lord_5,
            "sub_lord_7": sub_lord_7,
            "csl_5_state": state
        }

    # ==================================================
    # QUESTIONS
    # ==================================================
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="LOVE_SO_1",
                question="How can I understand and improve my partner's loyalty, trust issues and our emotional and physical compatibility?",
                meta=QueryMeta(QueryType.NON_TIMING, EventPolarity.NEUTRAL, InterpretationGoal.STATUS),
                sub_subdomain="Compatibility Analysis and Advice"
            ),
            Question(
                id="LOVE_SO_2",
                question="Will I get married to my current partner and what is the future course of our relationship?",
                meta=QueryMeta(QueryType.TIMING, EventPolarity.POSITIVE, InterpretationGoal.MANIFESTATION),
                sub_subdomain="Love Leading to Marriage"
            )
        ]
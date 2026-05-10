"""
Breakup – LLM Prompts v9.5

CORE DESIGN CHANGES FROM v9.4:
══════════════════════════════════════════════════════════════════════

CHANGES IN v9.5:
✅ MINOR DETECTION — Aligned with Career prompt pattern:
   - DOB parsed directly in build_analysis_prompt() using datetime
   - is_minor flag computed inline (no external helper calls outside the class)
   - is_minor passed as kwarg through to all sub-builders
   - Logs age + minor status at entry point

✅ MINOR RESPONSE — "Not Applicable" pattern:
   - Only general_answer populated
   - astrological_analysis, summary, timing_windows, remedies,
     overview_summary all set to null
   - FINAL_RESPONSE:: sentinel returned immediately, LLM never called

✅ SELF-CONTAINED — Zero dependency on functions outside this file.
   All minor logic lives inside build_analysis_prompt() and
   _build_minor_final_response(). No orchestrator changes needed.

SENTINEL CONTRACT (LLM caller MUST implement this check):

    result = pb.build_analysis_prompt(...)
    if result.startswith("FINAL_RESPONSE::"):
        import json
        final = json.loads(result[len("FINAL_RESPONSE::"):])
        # Use final directly — do NOT send to LLM
        # Only final["general_answer"] is populated; all others are null.
    else:
        llm_output = llm.generate(result)

UNCHANGED FROM v9.4:
✔ build_system_prompt
✔ Weightage: KP 60% / Vedic 30% / Dasha 10%
✔ Narrative flow rule
✔ All Q1/Q2/Q3/Q4 adult prompt builders
✔ All data helpers
✔ Language helpers
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder,
    QueryMeta,
    TimingWindow,
    QueryType,
    EventPolarity,
    InterpretationGoal,
)

logger = logging.getLogger(__name__)

DOMAIN_PREFIX = "love_and_relationship"

# Sentinel prefix — the LLM caller checks for this BEFORE sending to the LLM
FINAL_RESPONSE_PREFIX = "FINAL_RESPONSE::"


class BreakupPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Love Relationship → Breakup
    v9.5

    Minor detection is done INLINE inside build_analysis_prompt() using
    the same DOB-parsing pattern as CareerDiscoveryAndEmploymentPromptBuilder.
    No external function calls outside this class are needed.

    For minors, build_analysis_prompt() returns a FINAL_RESPONSE:: sentinel.
    Only general_answer is populated; all other fields are null.
    The LLM is never called for minor requests.

    LLM caller integration (one check):

        result = pb.build_analysis_prompt(...)
        if result.startswith("FINAL_RESPONSE::"):
            final = json.loads(result[len("FINAL_RESPONSE::"):])
            # Use final directly — skip LLM
        else:
            llm_output = llm.generate(result)
    """

    domain = "Love_Relationship"
    subtopic = "Breakup"

    # ==========================================================================
    # MINOR FINAL RESPONSE BUILDER  (no LLM — returns sentinel)
    # ==========================================================================

    def _build_minor_final_response(
        self,
        question: str,
        sub_subdomain: str,
        question_id: str,
        language: str,
        dob: str,
    ) -> str:
        """
        Build the complete "Not Applicable" response for a minor.
        Returns a FINAL_RESPONSE:: sentinel string.

        Only general_answer is populated.
        All other fields are explicitly null.

        Args:
            question:       Original question text (preserved)
            sub_subdomain:  Sub-subdomain string (preserved)
            question_id:    Question ID e.g. "LOVE_BREAKUP_1" (preserved)
            language:       "English" or "Hindi"
            dob:            DOB string — used for logging only
        """
        logger.warning(
            f"[BREAKUP v9.5] 🚨 MINOR GUARD ACTIVE | DOB={dob} | "
            f"lang={language} | QID={question_id} | "
            f"Returning FINAL_RESPONSE sentinel — LLM will NOT be called."
        )

        if language == "Hindi":
            general_answer = (
                "हम समझते हैं कि भावनात्मक उतार-चढ़ाव कभी-कभी बहुत कठिन लग सकते हैं। "
                "हालांकि, रोमांटिक संबंधों का ज्योतिषीय विश्लेषण 18 वर्ष से कम आयु के "
                "व्यक्तियों के लिए लागू नहीं है — यह आपकी भलाई के लिए है।"
            )
        else:
            general_answer = (
                "We understand that emotions can feel overwhelming at times, and that is "
                "completely valid. However, astrological analysis of romantic relationships "
                "and breakups is not applicable for individuals under 18 years of age — "
                "this boundary exists entirely for your wellbeing."
            )

        payload = {
            "__minor_not_applicable__": True,
            "__language__": language,
            "__dob__": dob,
            "id": question_id,
            "sub_subdomain": sub_subdomain,
            "question": question,
            # ── Only general_answer is populated for minors ──────────────────
            "general_answer": general_answer,
            # ── All other fields are null ────────────────────────────────────
            "astrological_analysis": None,
            "summary": None,
            "timing_windows": None,
            "remedies": None,
            "overview_summary": None,
        }

        return FINAL_RESPONSE_PREFIX + json.dumps(payload, ensure_ascii=False)

    # ==========================================================================
    # LANGUAGE HELPERS
    # ==========================================================================

    def _get_language_instruction_safe(self, language: str) -> str:
        """Get language instruction based on user selection."""
        try:
            if hasattr(self, "get_language_instruction"):
                return self.get_language_instruction(language)
        except Exception:
            pass
        if language == "Hindi":
            return (
                "IMPORTANT: Respond ONLY in Hindi (Devanagari script). "
                "Use Hindi for all analysis, interpretations, and recommendations."
            )
        elif language == "English":
            return (
                "IMPORTANT: Respond ONLY in English. "
                "Use English for all analysis, interpretations, and recommendations."
            )
        else:
            return f"IMPORTANT: Respond in {language}."

    def _get_example_text(self, language: str, example_type: str) -> str:
        """Get UI label text in the selected language."""
        examples = {
            "Hindi": {
                "5th_house": "पंचम भाव के स्वामी [planet] [house] भाव में [sign] राशि में स्थित हैं। इसका अर्थ है कि प्रेम संबंधों में...",
                "7th_house": "सप्तम भाव के स्वामी [planet] [house] भाव में हैं, जो साझेदारी और संबंध स्थिरता को दर्शाता है...",
                "8th_house": "अष्टम भाव के स्वामी [planet] [house] भाव में हैं, जो अचानक परिवर्तन और विभाजन को दर्शाता है...",
                "venus": "शुक्र प्रेम और सद्भाव का कारक है। शुक्र [position] में होने से...",
                "moon": "चंद्रमा भावनात्मक स्थिरता का कारक है। चंद्रमा [position] में होने से...",
                "timing_unavailable": "मिलन के लिए विशिष्ट समय की गणना वर्तमान में उपलब्ध नहीं है।",
                "blocked_message": "संबंध में कुछ चुनौतियां हैं। आत्म-उपचार और धैर्य पर ध्यान दें।",
                "general_answer": "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary": "सारांश",
                "remedies": "उपाय",
                "tell_client": "ग्राहक को बताएं",
                "separation_outlook": "विभाजन जोखिम विश्लेषण",
                "reconciliation_outlook": "मिलन संभावना",
                "strengthening_outlook": "संबंध मजबूती",
                "stability_outlook": "संबंध स्थिरता",
                "not_applicable_title": "लागू नहीं",
            },
            "English": {
                "5th_house": "The lord of 5th house [planet] is placed in [house] house in [sign]. This means for love relationships...",
                "7th_house": "The lord of 7th house [planet] is placed in [house] house, indicating partnership and relationship stability...",
                "8th_house": "The lord of 8th house [planet] is placed in [house] house, indicating sudden changes and separation...",
                "venus": "Venus is the karaka for love and harmony. Venus being in [position] indicates...",
                "moon": "Moon is the karaka for emotional stability. Moon being in [position] indicates...",
                "timing_unavailable": "Specific timing for reconciliation could not be calculated at this time.",
                "blocked_message": "There are some challenges in the relationship. Focus on self-healing and patience.",
                "general_answer": "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary": "Summary",
                "remedies": "Remedies",
                "tell_client": "TELL CLIENT",
                "separation_outlook": "Separation Risk Analysis",
                "reconciliation_outlook": "Reconciliation Prospects",
                "strengthening_outlook": "Relationship Strengthening",
                "stability_outlook": "Relationship Stability",
                "not_applicable_title": "Not Applicable",
            },
        }
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get paragraph starters in selected language."""
        return {
            "Hindi": {
                "vedic": "वैदिक ज्योतिष के अनुसार,",
                "kp": "KP प्रणाली के अनुसार,",
            },
            "English": {
                "vedic": "According to Vedic astrology,",
                "kp": "According to KP astrology,",
            },
        }.get(language, {"vedic": "According to Vedic astrology,", "kp": "According to KP astrology,"})

    # ==========================================================================
    # SYSTEM PROMPT  (adults only — never shown for minors)
    # ==========================================================================

    def build_system_prompt(
        self,
        language: str = "English",
        is_timing: bool = False,
        is_minor: bool = False,
    ) -> str:
        """Build system prompt — clean text only, no Python comment leakage."""

        weightage_text = (
            "TIMING QUESTION: KP 60% (PRIMARY) + Vedic 30% (SECONDARY) + Dasha 10%"
            if is_timing
            else "NON-TIMING QUESTION: KP 60% (PRIMARY) + Vedic 30% (SECONDARY) + Dasha 10%"
        )

        example_7th = self._get_example_text(language, "7th_house")

        role_text = (
            "You are an expert Vedic astrologer. This session has been flagged as a minor — "
            "output only the Not Applicable statement."
            if is_minor
            else "You are an expert KP and Vedic astrologer specializing in relationship "
            "stability, breakup risk assessment, and reconciliation guidance."
        )

        key_houses_section = (
            ""
            if is_minor
            else """
════════════════════════════════════════════════════════════════
KEY BREAKUP HOUSES (VEDIC)
════════════════════════════════════════════════════════════════

5th  → Romance, emotional connection (PRIMARY)
7th  → Partnership, committed relationship (PRIMARY)
8th  → Separation, transformation, sudden changes (PRIMARY)
6th  → Conflicts, disagreements, enemies
12th → Losses, endings, hidden issues
1st  → Self, personality
4th  → Emotional security
════════════════════════════════════════════════════════════════
"""
        )

        return f"""{role_text}

{weightage_text}

════════════════════════════════════════════════════════════════
ANALYSIS WEIGHTING (ENGINE LOGIC)
════════════════════════════════════════════════════════════════

KP Significations  → 60%   (PRIMARY — decides events)
Vedic Structure    → 30%   (SECONDARY — explains ease/difficulty)
Dasha Timing       → 10%   (contextual trigger)

KP conclusion ALWAYS leads the final recommendation.
Vedic explains the capacity and effort required.

════════════════════════════════════════════════════════════════
KP ANALYSIS CHAIN (MANDATORY when KP data available)
════════════════════════════════════════════════════════════════

For every KP judgement, follow this chain:

CSL → Nakshatra → Star Lord → Houses Signified → Promise/Denial

Sub Lord      → FINAL PROMISE (event happens or not) — MOST IMPORTANT
Star Lord     → RESULT TYPE (what happens)
Planet Nature → FLAVOR ONLY (never overrides significations)

SIGNIFICATIONS ALWAYS WIN over planet benefic/malefic nature.

Example:
If Venus (benefic) signifies 6, 8, 12 → result is obstacles/delays.
If Saturn (malefic) signifies 5, 7, 11 → result is stable relationship.

════════════════════════════════════════════════════════════════
ANTI-HALLUCINATION RULES (CRITICAL)
════════════════════════════════════════════════════════════════

1. NEVER INVENT DATES OR TIMING
   Only use dates from TIMING WINDOWS section if provided.
   Do NOT guess years like "2027", "next year", "in 6 months".

2. ONLY USE DATA PROVIDED
   Do not invent planetary positions not in the data.
   If data is missing, say so clearly.

3. BREAKUP RISK MUST COME FROM KP DATA
   If KP analysis provides risk level, use that.
   Do NOT override KP verdict with Vedic interpretation.

4. DISTINGUISH FACTS FROM INTERPRETATION
   Facts = from provided data.
   Interpretation = your astrological reasoning.

════════════════════════════════════════════════════════════════
CRITICAL WRITING STYLE RULES
════════════════════════════════════════════════════════════════

NARRATIVE FLOW RULE:
Your answer should read as a CONNECTED STORY, not a checklist.
Flow: KP promise → Why (significations) → Vedic capacity → Timing → Action

Each section should naturally lead into the next.

WRONG: "7th Lord Venus in 8th house. Debilitated. Malefic."
RIGHT: "{example_7th}"

EVERY FACT NEEDS INTERPRETATION:
State the fact → explain what it means → connect to the outcome.

WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS.
"TELL CLIENT:" ONLY IN FINAL SUMMARY.
ANSWER THE ACTUAL QUESTION DIRECTLY.

════════════════════════════════════════════════════════════════
KP RULES (When KP data present)
════════════════════════════════════════════════════════════════

KP section contains ONLY pre-computed evaluator output:
Breakup Risk Level, Risk Percentage, Attraction Score,
Compatibility Score, CSL-5 and CSL-7 findings.

KP section must NOT contain:
LLM-derived KP analysis, reinterpretation of KP points,
Vedic reasoning mixed into KP paragraph.

IF KP POINTS HAVE NO RELEVANT INFO FOR THE QUESTION:
Skip KP section entirely and provide Vedic analysis only.

{key_houses_section}

════════════════════════════════════════════════════════════════
RELATIONSHIP SAFETY RULES
════════════════════════════════════════════════════════════════

NEVER guarantee breakup or reconciliation.
NEVER make predictions that could cause emotional harm.
Frame challenges as TEMPORARY PHASES, not permanent blocks.
Relationship issues are CORRECTABLE with effort.
Be compassionate and constructive.
"""

    # ==========================================================================
    # DATA HELPERS
    # ==========================================================================

    def _get_kp_availability(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        kp_breakup = additional_data.get(f"{DOMAIN_PREFIX}_kp_breakup", {})
        return bool(
            kp_breakup.get("risk_level")
            or kp_breakup.get("breakup_risk") is not None
        )

    def _get_relevant_kp_points(self, additional_data: Dict, question_type: str) -> List[str]:
        """Return KP points relevant to question. Strengthening/Remedies = Vedic only."""
        if not additional_data:
            return []
        if question_type in ["strengthening", "remedies"]:
            return []
        kp_breakup = additional_data.get(f"{DOMAIN_PREFIX}_kp_breakup", {})
        if not kp_breakup:
            return []
        points = []
        if question_type in ["separation", "reconciliation"]:
            if kp_breakup.get("risk_level"):
                points.append("risk_level")
            if kp_breakup.get("breakup_risk") is not None:
                points.append("breakup_risk")
            if kp_breakup.get("compatibility_score") is not None:
                points.append("compatibility_score")
            if kp_breakup.get("summary"):
                points.append("summary")
        return points

    def _is_blocked(self, additional_data: Dict) -> bool:
        """Check if reconciliation is blocked based on KP analysis."""
        if not additional_data:
            return False
        kp_breakup = additional_data.get(f"{DOMAIN_PREFIX}_kp_breakup", {})
        if kp_breakup.get("risk_level") == "HIGH":
            return True
        if kp_breakup.get("breakup_risk", 0) < -10:
            return True
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if house_lords:
            weak_count = sum(
                1
                for h in [5, 7]
                if house_lords.get(h, {}).get("lord_strength_score", 50) < 30
            )
            if weak_count >= 2:
                return True
        return False

    def _format_kp_breakup_data(self, additional_data: Dict) -> str:
        """Format KP breakup analysis — DATA ONLY, no LLM interpretation."""
        if not additional_data:
            return ""
        kp_breakup = additional_data.get(f"{DOMAIN_PREFIX}_kp_breakup", {})
        if not kp_breakup:
            return ""

        lines = ["KP BREAKUP ANALYSIS DATA (Pre-computed by Evaluator):"]

        risk_level = kp_breakup.get("risk_level")
        if risk_level:
            emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MODERATE" else "🟢"
            lines.append(f"• Breakup Risk Level: {emoji} {risk_level}")

        risk_pct = kp_breakup.get("risk_percentage")
        if risk_pct is not None:
            lines.append(f"• Risk Percentage: {risk_pct}%")

        breakup_risk = kp_breakup.get("breakup_risk")
        if breakup_risk is not None:
            lines.append(f"• Risk Score: {breakup_risk}")

        attraction = kp_breakup.get("attraction_score")
        if attraction is not None:
            lines.append(f"• Attraction Score: {attraction}")

        compatibility = kp_breakup.get("compatibility_score")
        if compatibility is not None:
            lines.append(f"• Compatibility Score: {compatibility}")

        summary = kp_breakup.get("summary")
        if summary:
            lines.append(f"• Summary: {summary}")

        csl_5 = kp_breakup.get("csl_5")
        if csl_5:
            lines.append(f"• 5th CSL (Romance): {csl_5}")

        csl_7 = kp_breakup.get("csl_7")
        if csl_7:
            lines.append(f"• 7th CSL (Partnership): {csl_7}")

        promise_5 = kp_breakup.get("promise_5_state")
        if promise_5:
            lines.append(f"• 5th House State: {promise_5}")

        lines.append("")
        lines.append("NOTE: Simply restate these KP findings. Do NOT re-interpret further.")
        return "\n".join(lines)

    def _format_timing_windows(self, additional_data: Dict) -> str:
        """Format timing windows — BEST and NEAREST with full detail."""
        if not additional_data:
            return ""
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""
        try:
            best = timing_data.get("best_window", {})
            nearest = timing_data.get("nearest_window", {})
            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("TIMING WINDOWS (Use ONLY these dates):")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")

            if best:
                lines.append(f"🏆 BEST:    {best.get('dasha', 'N/A')}")
                lines.append(f"   Period:  {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"   Score:   {best.get('final_score', 0):.0f}/100")
                lines.append(f"   Age:     {best.get('age_at_start', 'N/A')} years")
                lines.append(
                    f"   Maha: {best.get('score_maha', 0)}/10  |  "
                    f"Antara: {best.get('score_antara', 0)}/10  |  "
                    f"Pratyantar: {best.get('score_paryantar', 0)}/10"
                )
                lines.append("   Trade-off: May be further in future, but strongest alignment")
                lines.append("")

            if nearest and nearest.get("dasha") != (best or {}).get("dasha"):
                lines.append(f"⏰ NEAREST: {nearest.get('dasha', 'N/A')}")
                lines.append(f"   Period:  {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"   Score:   {nearest.get('final_score', 0):.0f}/100")
                lines.append(f"   Age:     {nearest.get('age_at_start', 'N/A')} years")
                lines.append("   Trade-off: Sooner opportunity, not absolute best alignment")
                lines.append("")
            elif best and nearest and best.get("dasha") == nearest.get("dasha"):
                lines.append("✅ LUCKY: Best and Nearest windows are THE SAME!")
                lines.append("   You get optimal timing AND early opportunity!")
                lines.append("")

            lines.append("INSTRUCTIONS:")
            lines.append("- Mention BOTH windows with exact dates")
            lines.append("- Explain WHY each is favorable for reconciliation")
            lines.append("- Let user choose: wait for best OR act sooner")
            lines.append("═══════════════════════════════════════════════════════")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting timing: {e}")
            return ""

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return False
        return bool(timing_data.get("best_window") or timing_data.get("nearest_window"))

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data."""
        if not additional_data:
            return ""
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = ["HOUSE LORDS DATA:"]
        breakup_houses = {1, 4, 5, 6, 7, 8, 11, 12}

        for house_num in sorted(house_lords.keys()):
            if house_num not in breakup_houses:
                continue
            info = house_lords.get(house_num, {})
            if not info:
                continue

            lord = info.get("lord", "N/A")
            lord_house = info.get("lord_in_house", "N/A")
            lord_sign = info.get("lord_in_sign", "N/A")
            dignity = info.get("lord_dignity", "N/A")
            strength = info.get("lord_strength_score", 0)

            conditions = []
            if info.get("lord_is_combust"):
                conditions.append("Combust")
            if info.get("lord_is_retrograde"):
                conditions.append("Retrograde")
            condition_str = ", ".join(conditions) if conditions else "Normal"
            planets = ", ".join(info.get("planets_in_house", [])) or "None"

            lines.append(
                f"• H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | "
                f"{dignity} | {condition_str} | Str:{strength}/100 | Planets:{planets}"
            )

        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        """Format aspects data."""
        if not additional_data:
            return ""
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        lines = ["ASPECTS DATA:"]
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            if benefic or malefic:
                lines.append(
                    f"• H{house_num}: Benefic={', '.join(benefic) or 'None'} | "
                    f"Malefic={', '.join(malefic) or 'None'}"
                )
        return "\n".join(lines) if len(lines) > 1 else ""

    def _format_current_dasha(self, kwargs: Dict) -> str:
        """Format current dasha."""
        current_dasha = kwargs.get("current_dasha", {})
        if not current_dasha:
            additional_data = kwargs.get("additional_data", {})
            current_dasha = additional_data.get("current_dasha", {})
        if not current_dasha:
            return ""
        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end = date_range.get("end", "Unknown")
            return f"CURRENT DASHA: {dasha_name} ({start} to {end})"
        except Exception:
            return ""

    def _format_dasha_timeline(self, kwargs: Dict) -> str:
        """Format dasha timeline."""
        dasha_timeline = kwargs.get("dasha_timeline", {})
        if not dasha_timeline:
            additional_data = kwargs.get("additional_data", {})
            dasha_timeline = additional_data.get("dasha_timeline", {})
        if not dasha_timeline:
            return ""
        try:
            current = dasha_timeline.get("current", [])
            future = dasha_timeline.get("next_10_years", [])
            if not any([current, future]):
                return ""

            lines = ["DASHA TIMELINE:"]
            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon",
                "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu",
            }

            def parse_dasha(name):
                parts = name.replace(">", "-").split("-")
                return " > ".join([dasha_mapping.get(p.strip(), p.strip()) for p in parts])

            if current:
                lines.append("\n🔴 CURRENT:")
                for d in current[:3]:
                    parsed = parse_dasha(d.get("dasha_name", ""))
                    dr = d.get("date_range", {})
                    lines.append(f"  • {parsed} ({dr.get('start', '')} to {dr.get('end', '')})")

            if future:
                lines.append("\n⏭️ UPCOMING (Next 10 Years):")
                for i, d in enumerate(future[:10], 1):
                    parsed = parse_dasha(d.get("dasha_name", ""))
                    dr = d.get("date_range", {})
                    lines.append(f"  {i}. {parsed} ({dr.get('start', '')} to {dr.get('end', '')})")

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ==========================================================================
    # ROUTER  ←  THE ONLY ENTRY POINT
    # ==========================================================================

    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi",
        **kwargs,
    ) -> str:
        """
        Main entry point. Returns one of two things:

        1. ADULT  → A prompt string to send to the LLM (normal flow)
        2. MINOR  → A FINAL_RESPONSE:: sentinel string (do NOT send to LLM)

        Minor detection is done INLINE here using the same DOB-parsing
        pattern as CareerDiscoveryAndEmploymentPromptBuilder._detect_minor().
        No external calls needed.

        The caller MUST check:

            result = pb.build_analysis_prompt(...)
            if result.startswith("FINAL_RESPONSE::"):
                final = json.loads(result[len("FINAL_RESPONSE::"):])
                # Use final directly — skip LLM
                # NOTE: Only final["general_answer"] is populated.
                #       All other fields are null.
            else:
                llm_output = llm.generate(result)
        """
        try:
            additional_data = kwargs.pop("additional_data", {})
            kwargs["additional_data"] = additional_data

            dob = kwargs.get("dob", "")

            # ── INLINE MINOR DETECTION ─────────────────────────────────────────
            # Same pattern as CareerDiscoveryAndEmploymentPromptBuilder._detect_minor()
            # Computes current age from DOB. No external function calls.
            is_minor = False
            if dob:
                try:
                    today = datetime.now()
                    dob_dt = datetime.strptime(dob, "%d/%m/%Y")
                    current_age = (
                        today.year - dob_dt.year
                        - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
                    )
                    is_minor = current_age < 18
                    logger.warning(
                        f"[BREAKUP v9.5] 🔍 Minor Detection | "
                        f"DOB={dob} | Age={current_age} | Is Minor={is_minor}"
                    )
                except Exception as parse_err:
                    logger.error(
                        f"[BREAKUP v9.5] ❌ DOB parse failed for '{dob}' — {parse_err}. "
                        f"Treating as adult."
                    )
                    is_minor = False
            else:
                # Fallback: check evaluator-stored flag if DOB not passed
                is_minor = bool(additional_data.get(f"{DOMAIN_PREFIX}_is_minor", False))
                logger.warning(
                    f"[BREAKUP v9.5] ⚠️ DOB missing — "
                    f"fallback flag is_minor={is_minor}"
                )

            # Propagate flag so sub-builders can see it if needed
            kwargs["is_minor"] = is_minor

            logger.info(
                f"[BREAKUP v9.5] 🚦 ENTRY | DOB={dob} | Minor={is_minor} | "
                f"Lang={language} | QID={kwargs.get('question_id')} | "
                f"SubDomain={kwargs.get('sub_subdomain', '')}"
            )

            # ── MINOR: return final response sentinel immediately ──────────────
            if is_minor:
                sub_subdomain = kwargs.get("sub_subdomain", "")
                question_id = kwargs.get("question_id", "LOVE_BREAKUP_1")
                logger.critical(
                    f"[BREAKUP v9.5] 🚨 MINOR SENTINEL TRIGGERED | "
                    f"DOB={dob} | QID={question_id} | Sub={sub_subdomain}"
                )
                return self._build_minor_final_response(
                    question=question,
                    sub_subdomain=sub_subdomain,
                    question_id=question_id,
                    language=language,
                    dob=dob,
                )

            # ── ADULT: route to appropriate prompt builder ────────────────────
            sub_subdomain = kwargs.get("sub_subdomain", "")
            raw = "\n".join(technical_points) if technical_points else ""

            if "Separation" in sub_subdomain:
                return self._build_separation_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            elif "Reconciliation" in sub_subdomain:
                return self._build_reconciliation_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            elif "Strengthen" in sub_subdomain or "Advice" in sub_subdomain:
                return self._build_strengthening_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            else:
                return self._build_general_prompt(
                    question, additional_data, raw, language, **kwargs
                )

        except Exception as e:
            logger.error(f"[BREAKUP v9.5] Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # FALLBACK
    # ==========================================================================

    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in relationships. Answer the following question.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear actionable statement.
Never guarantee breakup or reconciliation.
Be compassionate and constructive.
"""

    # ==========================================================================
    # Q1 — SEPARATION RISK
    # KP 60% + Vedic 30% + Dasha 10%  |  NON-TIMING
    # ==========================================================================

    def _build_separation_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs,
    ) -> str:

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        kp_points = self._get_relevant_kp_points(additional_data, "separation")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)

        kp_data = self._format_kp_breakup_data(additional_data) if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        timeline_data = self._format_dasha_timeline(kwargs)

        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_separation = self._get_example_text(language, "separation_outlook")
        starters = self._get_analysis_starters(language)

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════
KP BREAKUP ANALYSIS DATA (Primary — 60% weight):
═══════════════════════════════════════════════════════

{kp_data}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False, is_minor=False)}

═══════════════════════════════════════════════════════
QUERY: SEPARATION RISK ASSESSMENT
Current Date: {today_str}
Weightage: KP 60% (PRIMARY) + Vedic 30% + Dasha 10%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Vedic only'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_section}

═══════════════════════════════════════════════════════
VEDIC REFERENCE DATA (Secondary — 30% weight):
═══════════════════════════════════════════════════════

{lords_data or "House lords data not available."}

{aspects_data}

{dasha_data}

{timeline_data}

{raw}

═══════════════════════════════════════════════════════
SEPARATION CONTEXT:
6th house = conflicts, disagreements
8th house = separation, transformation
12th house = losses, endings
Venus/Moon affliction = emotional instability
═══════════════════════════════════════════════════════

OUTPUT FORMAT:

**{lbl_general} (2-3 lines):**
{lbl_separation}. State the risk level clearly but compassionately.
NO astrological terms here. Write as a caring advisor.

**{lbl_analysis}:**

NARRATIVE FLOW RULE:
Write as a connected story: KP risk finding → Why → Vedic capacity → Remedies.
Each paragraph leads naturally into the next.

PARAGRAPH 1 — KP ANALYSIS (Primary, 60% weight):
Begin with: "{starters['kp']}"
State the KP risk level and key findings.
Explain what the CSL/promise state means for separation risk.

PARAGRAPH 2 — VEDIC CONFIRMATION (Secondary, 30% weight):
Begin with: "{starters['vedic']}"
Analyze 7th house (partnership), 8th house (separation), 6th house (conflicts).
Does Vedic CONFIRM or show nuance vs KP?

PARAGRAPH 3 — RISK FACTORS AND MITIGATION:
Specific contributing factors. What can be done to mitigate.

**{lbl_summary}:**
{lbl_tell}: "[Clear risk assessment with constructive guidance]"

**{lbl_remedies}:**
Remedies to reduce separation risk and strengthen relationship.

CRITICAL: Be compassionate. Never guarantee breakup.
"""

    # ==========================================================================
    # Q2 — RECONCILIATION
    # KP 60% + Vedic 30% + Dasha 10%  |  TIMING if available
    # ==========================================================================

    def _build_reconciliation_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs,
    ) -> str:

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        is_blocked = self._is_blocked(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data) and not is_blocked

        kp_points = self._get_relevant_kp_points(additional_data, "reconciliation")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)

        kp_data = self._format_kp_breakup_data(additional_data) if has_relevant_kp else ""
        timing_data = self._format_timing_windows(additional_data) if has_timing else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        timeline_data = self._format_dasha_timeline(kwargs)

        timing_unavailable = self._get_example_text(language, "timing_unavailable")
        blocked_message = self._get_example_text(language, "blocked_message")
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_reconciliation = self._get_example_text(language, "reconciliation_outlook")
        starters = self._get_analysis_starters(language)

        if is_blocked:
            timing_instruction = f"""
═══════════════════════════════════════════════════════
⚠️ RECONCILIATION CHALLENGING — NO SPECIFIC TIMING
═══════════════════════════════════════════════════════

The chart shows significant challenges for reconciliation.

DO NOT provide specific timing windows or dates.
DO mention current dasha for general context.
DO recommend self-healing and personal growth.
DO provide remedies to improve prospects.

{dasha_data or "Current dasha information not available."}

MESSAGE TO CONVEY: "{blocked_message}"
═══════════════════════════════════════════════════════
"""
        elif has_timing:
            timing_instruction = f"""
{timing_data}

{dasha_data or ""}

USE ONLY the dates provided above. Mention BOTH windows.
"""
        else:
            timing_instruction = f"""
═══════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING CALCULATED
═══════════════════════════════════════════════════════

No timing windows calculated, but reconciliation is NOT blocked.

DO NOT invent specific dates.
DO recommend monitoring favorable dasha periods.

{dasha_data or ""}

MESSAGE: "{timing_unavailable}"
═══════════════════════════════════════════════════════
"""

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════
KP BREAKUP ANALYSIS DATA (Primary — 60% weight):
═══════════════════════════════════════════════════════

{kp_data}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=has_timing, is_minor=False)}

═══════════════════════════════════════════════════════
QUERY: RECONCILIATION PROSPECTS
Current Date: {today_str}
Weightage: KP 60% (PRIMARY) + Vedic 30% + Dasha 10%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Vedic only'}
Timing Available: {'YES' if has_timing else 'NO'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════
VEDIC REFERENCE DATA (Secondary — 30% weight):
═══════════════════════════════════════════════════════

{lords_data or "House lords data not available."}

{aspects_data}

{timeline_data}

{raw}

OUTPUT FORMAT:

**{lbl_general} (2-3 lines):**
{lbl_reconciliation}.
{"Mention BEST and NEAREST timing windows." if has_timing else ""}
{"State reconciliation needs time and self-healing." if is_blocked else ""}
{"State specific timing needs further analysis." if not has_timing and not is_blocked else ""}
NO astrological terms here. Write as a caring advisor.

**{lbl_analysis}:**

NARRATIVE FLOW RULE:
Write as a connected story: KP promise → Why → Vedic capacity → Timing.
Each paragraph leads naturally into the next.

PARAGRAPH 1 — KP ANALYSIS (Primary, 60% weight):
Begin with: "{starters['kp']}"
State compatibility/attraction scores and reconciliation promise.
Explain what significations mean for chances of reunion.

PARAGRAPH 2 — VEDIC CONFIRMATION (Secondary, 30% weight):
Begin with: "{starters['vedic']}"
Analyze 5th house (emotional reconnection), 7th house (partnership healing).
Does Vedic agree with KP?

{"PARAGRAPH 3 — TIMING: Connect dasha lords to timing windows. Use exact dates." if has_timing else "PARAGRAPH 3 — HEALING PATH: What personal growth enables reconciliation. No specific dates." if is_blocked else ""}

**{lbl_summary}:**
{lbl_tell}: "{'Specific timing advice with dates.' if has_timing else 'Focus on self-healing and patience.'}"

**{lbl_remedies}:**
{"Provide remedies for reconciliation." if not is_blocked else "Remedies to heal and prepare for future opportunities."}
"""

    # ==========================================================================
    # Q3 — RELATIONSHIP STRENGTHENING
    # Vedic 90% + Dasha 10%  |  VEDIC ONLY
    # ==========================================================================

    def _build_strengthening_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs,
    ) -> str:

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)

        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_strengthening = self._get_example_text(language, "strengthening_outlook")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False, is_minor=False)}

═══════════════════════════════════════════════════════
QUERY: RELATIONSHIP STRENGTHENING
Current Date: {today_str}
Weightage: Vedic 90% + Dasha 10% (VEDIC ONLY — practical question)
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════

{lords_data or "House lords data not available."}

{aspects_data}

{dasha_data}

{raw}

═══════════════════════════════════════════════════════
STRENGTHENING CONTEXT:
Focus on IMPROVING the relationship, not predicting breakup.
Identify weak planets (Venus/Moon/Mars).
Provide practical communication advice.
Address both emotional and behavioral aspects.
═══════════════════════════════════════════════════════

OUTPUT FORMAT:

**{lbl_general} (2-3 lines):**
{lbl_strengthening}. State what areas need attention and that the relationship can be strengthened.

**{lbl_analysis}:**

NARRATIVE FLOW RULE:
Write as a connected story: Weak planets → What they affect → How to address each.

PARAGRAPH 1 — VEDIC ANALYSIS (90% weight):
Begin with: "{starters['vedic']}"
Identify weak planets affecting relationship.
5th, 7th house lord conditions. Venus and Moon's role in harmony.

PARAGRAPH 2 — COMMUNICATION AREAS:
What communication patterns need improvement based on planetary positions.

PARAGRAPH 3 — EMOTIONAL NEEDS:
What emotional needs are indicated and how to address them.

**{lbl_summary}:**
{lbl_tell}: "[Practical advice for strengthening]"

**{lbl_remedies} (Detailed):**
1. [Emotional remedy — feelings/connection]
2. [Behavioral remedy — actions/habits]
3. [Astrological remedy if needed]
"""

    # ==========================================================================
    # Q4 — REMEDIES
    # Vedic 90% + Dasha 10%  |  VEDIC ONLY
    # ==========================================================================

    def _build_remedies_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs,
    ) -> str:

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)

        kp_breakup = additional_data.get(f"{DOMAIN_PREFIX}_kp_breakup", {})
        kp_remedies = kp_breakup.get("remedies", [])

        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        kp_remedies_section = ""
        if kp_remedies:
            kp_remedies_section = (
                "EVALUATOR-SUGGESTED REMEDIES:\n"
                + "\n".join("- " + r for r in kp_remedies)
            )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False, is_minor=False)}

═══════════════════════════════════════════════════════
QUERY: BREAKUP/RELATIONSHIP REMEDIES
Current Date: {today_str}
Weightage: Vedic 90% + Dasha 10% (VEDIC ONLY — practical question)
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════

{lords_data or "House lords data not available."}

{aspects_data}

{dasha_data}

{kp_remedies_section}

{raw}

═══════════════════════════════════════════════════════
REMEDY GUIDE FOR RELATIONSHIPS:

VENUS WEAK: Strengthen for love and harmony
- Diamond or White Sapphire
- "Om Shukraya Namaha" mantra
- Friday fasting/worship

MOON WEAK: Strengthen for emotional stability
- Pearl
- "Om Chandraya Namaha" mantra
- Monday practices

MARS AFFLICTED: Pacify for reducing conflicts
- Red Coral if appropriate
- "Om Mangalaya Namaha" mantra
- Tuesday practices

SATURN AFFLICTED: Pacify for removing obstacles
- Blue Sapphire only if strongly recommended
- "Om Shanaishcharaya Namaha" mantra
- Saturday practices
═══════════════════════════════════════════════════════

OUTPUT FORMAT:

**{lbl_general} (2-3 lines):**
State what areas need strengthening and that remedies can help.

**{lbl_analysis}:**

NARRATIVE FLOW RULE:
Write as a connected story: Weak planet → Why it harms the relationship → Remedy and why it helps.

PARAGRAPH 1 — VEDIC ANALYSIS (90% weight):
Begin with: "{starters['vedic']}"
Identify weak planets affecting relationship.
Venus and Moon condition. Malefic aspects causing problems.

PARAGRAPH 2 — PRIMARY REMEDY:
Most important remedy and WHY it will help.

PARAGRAPH 3 — SUPPORTING REMEDIES:
Additional helpful practices.

**{lbl_summary}:**
{lbl_tell}: "[Priority order of remedies]"

**{lbl_remedies} (Detailed):**
1. [Primary astrological remedy with specific instructions]
   - Gemstone recommendation if applicable
   - Mantra with count
2. [Secondary remedy with instructions]
3. [Practical relationship improvement advice]
"""

    # ==========================================================================
    # GENERAL FALLBACK
    # ==========================================================================

    def _build_general_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs,
    ) -> str:

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        timing_keywords = ["when", "time", "timing", "year", "date", "कब", "समय", "return", "reconcil"]
        is_timing = any(kw in question.lower() for kw in timing_keywords)

        is_blocked = self._is_blocked(additional_data)
        has_timing_data = self._has_valid_timing_windows(additional_data) and not is_blocked

        kp_points = self._get_relevant_kp_points(additional_data, "separation")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)

        kp_data = self._format_kp_breakup_data(additional_data) if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        timing_data = self._format_timing_windows(additional_data) if is_timing and has_timing_data else ""
        dasha_data = self._format_current_dasha(kwargs) if is_timing else ""
        timeline_data = self._format_dasha_timeline(kwargs) if is_timing else ""

        starters = self._get_analysis_starters(language)
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_stability = self._get_example_text(language, "stability_outlook")

        blocked_warning = ""
        if is_blocked and is_timing:
            blocked_message = self._get_example_text(language, "blocked_message")
            blocked_warning = f"""
═══════════════════════════════════════════════════════
⚠️ CHALLENGING PERIOD — NO SPECIFIC TIMING
═══════════════════════════════════════════════════════
Do NOT provide specific timing. Recommend self-healing and patience.
Message: "{blocked_message}"
═══════════════════════════════════════════════════════
"""

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════
KP BREAKUP ANALYSIS DATA (Primary — 60% weight):
═══════════════════════════════════════════════════════

{kp_data}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing, is_minor=False)}

═══════════════════════════════════════════════════════
QUERY: BREAKUP/RELATIONSHIP (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: KP 60% (PRIMARY) + Vedic 30% + Dasha 10%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Vedic only'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{blocked_warning}

{timing_data}

{dasha_data}

{timeline_data}

{kp_section}

{lords_data or ""}

{aspects_data}

{raw}

OUTPUT FORMAT:

**{lbl_general} (2-3 lines):**
{lbl_stability}. Directly answer the question.
NO astrological terms here.

**{lbl_analysis}:**

NARRATIVE FLOW RULE:
Write as a connected story. Each paragraph leads into the next.

PARAGRAPH 1 — KP ANALYSIS (Primary, 60% weight):
Begin with: "{starters['kp']}"
State KP risk/promise finding and what it means.

PARAGRAPH 2 — VEDIC CONFIRMATION (Secondary, 30% weight):
Begin with: "{starters['vedic']}"
Core Vedic interpretation. Does it agree with KP?

**{lbl_summary}:**
{lbl_tell}: "[Clear actionable advice]"

**{lbl_remedies}:**
Relevant remedies if needed.

CRITICAL: Be compassionate and constructive. Never guarantee outcomes.
"""
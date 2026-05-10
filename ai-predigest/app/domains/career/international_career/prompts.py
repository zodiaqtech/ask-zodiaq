"""
International Career – LLM Prompts v11.0

ADDED IN v11.0 — Minor Detection (aligned with CareerDiscoveryAndEmploymentPromptBuilder v10.0):

✅ AGE SAFETY RULE added to build_system_prompt() - mirrors doc1 pattern exactly.
   Under-18 persons must never be told to relocate abroad, start international career,
   or given specific overseas move dates. Dashas treated as developmental cycles.

✅ _detect_minor(dob, dasha_timeline) added - same logic as CareerDiscovery doc1.
   Based on current age (not dasha age). Returns True if person is currently under 18.

✅ build_analysis_prompt() now:
   - Reads dob from kwargs
   - Calls _detect_minor() globally before routing
   - Logs minor detection result
   - Passes is_minor + dob to all sub-builders that need them

✅ _build_foreign_career_prompt() — if is_minor:
   - Suppresses timing windows entirely
   - Uses developmental_override block instead of timing_instruction
   - Frames foreign potential as "long-term direction" not "imminent relocation"

✅ _build_timing_prompt() — if is_minor:
   - No timing windows shown
   - get_output_format() receives is_minor=True → activates developmental output format
   - Dashas framed as preparation/foundation phases, not relocation triggers

✅ get_output_format() gains is_minor parameter:
   - is_minor=True replaces timing section with DEVELOPMENTAL MODE block
   - Instructions: do NOT predict foreign move, interpret dashas as preparation,
     frame as "long-term career direction forming"

✅ Risks and Remedies prompts unchanged — no age restriction applies there.

WHY MINOR LOGIC APPLIES HERE:
- "Foreign Career Potential" can predict "you'll relocate to Canada in 2026" for a 15-year-old
- "Timing" is even more explicit — direct date-based overseas move prediction
- Both must be reframed as developmental/preparation guidance for minors
- Same reasoning as Job Start Timing in CareerDiscovery (doc1)

FIXES FROM v10.0 (carried forward — see v10 docstring for full list):

✅ _format_timing_windows() - full BEST/NEAREST box format with score breakdown,
   age_at_start, trade-off explanations, and "If BEST = NEAREST → IDEAL!" detection.
   v9 only returned 2 one-liner strings.

✅ _format_house_lords() - added ⭐ PRIMARY / ○ SECONDARY markers, STRONG/MODERATE/WEAK
   assessment footer per house, combust/retrograde labels. v9 had compact format only.

✅ _format_house_aspects() - added "→ Net: POSITIVE/CHALLENGING/BALANCED" per house.
   v9 was missing the net assessment.

✅ _format_current_dasha() - now wrapped in full ═══ box with "USE THIS - DON'T INVENT"
   header and ⚠️ notes. v9 returned a single bare line.

✅ _format_dasha_timeline() - added career-specific planet-to-role guidelines footer
   (Sun/Jupiter → authority, Saturn → persistence, Rahu → foreign tech, etc.).
   v9 had no footer.

✅ get_output_format() - added explicit DASHA CONTEXT section to non-remedies paths.
   v9 was missing this section.

✅ _build_risks_prompt() and _build_remedies_prompt() now route through get_output_format()
   instead of inlining their output format. v9 still had inline format there.

✅ build_system_prompt() - added explicit RAHU/KETU rule for international career nodes
   (nodes act through their star lord for foreign matters). v9 was missing this.

✅ build_analysis_prompt() - added logger.warning entry log aligned with doc1 pattern.

✅ _calculate_age_on_date() helper added for timing window display.

✅ All sub-builders include 'CURRENT DATE' in query context block.

Data Keys (from InternationalCareerEvaluator v4.0):
- additional_data["international_career_house_lords"]
- additional_data["international_career_house_aspects"]
- additional_data["international_career_timing_windows"]
- additional_data["international_career_analysis_summary"]
- additional_data["international_career_house_config"]
- additional_data["lagna_info"]                          ← NEW in v4.0
- additional_data["career_foreign_structural"]           ← unchanged (KP data)
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder,
    QueryMeta,
    TimingWindow,
    QueryType,
    EventPolarity,
    InterpretationGoal
)

logger = logging.getLogger(__name__)

DOMAIN_PREFIX = "international_career"


class InternationalCareerPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Career → International Career
    v10.0 - Full alignment with CareerDiscovery v10.0 + ProspectsOfInvestments v7.0
    """

    domain = "Career"
    subtopic = "International Career"

    # ==========================================================================
    # LANGUAGE INSTRUCTION
    # ==========================================================================

    def get_language_instruction(self, language: str) -> str:
        if language == "Hindi":
            return (
                "IMPORTANT: Respond ONLY in Hindi (Devanagari script). "
                "Use Hindi for all analysis, interpretations, and recommendations. "
                "Use English only for technical terms (planets, house numbers, dasha names)."
            )
        elif language == "Hinglish":
            return (
                "IMPORTANT: Respond in Hinglish (Hindi + English mix, Roman script). "
                "Example: 'Aapke liye videsh mein career ki achhi sambhavnayen hain.'"
            )
        else:
            return (
                "IMPORTANT: Respond in clear English. "
                "Use English for all analysis, interpretations, and recommendations."
            )

    def _get_example_text(self, language: str, example_type: str) -> str:
        examples = {
            "Hindi": {
                "12th_house": (
                    "बारहवें भाव के स्वामी [planet] [house] भाव में [sign] में हैं। "
                    "इसका अर्थ है कि विदेश में बसने की संभावनाएं..."
                ),
                "9th_house": (
                    "नवम भाव के स्वामी [planet] [position] में होने से लंबी दूरी की यात्रा "
                    "और विदेश में भाग्य का संकेत मिलता है..."
                ),
                "7th_house": (
                    "सप्तम भाव के स्वामी [planet] [position] में होने से विदेशी व्यापार "
                    "और साझेदारी का संकेत मिलता है..."
                ),
                "rahu": "राहु विदेशी मामलों का कारक है। राहु [position] में होने से...",
                "timing_unavailable": "विदेश करियर के लिए विशिष्ट समय की गणना वर्तमान में उपलब्ध नहीं है।",
                "blocked_message": "विदेश करियर में कुछ चुनौतियां हैं। उपायों के साथ प्रयास जारी रखें।",
                "general_answer": "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary": "सारांश",
                "remedies": "उपाय",
                "tell_client": "ग्राहक को बताएं",
                "foreign_outlook": "विदेश करियर संभावना",
                "timing_outlook": "विदेश जाने का समय",
                "risks_outlook": "जोखिम विश्लेषण",
            },
            "English": {
                "12th_house": (
                    "The lord of 12th house [planet] is placed in [house] house in [sign]. "
                    "This indicates foreign settlement potential..."
                ),
                "9th_house": (
                    "The lord of 9th house [planet] being in [position] indicates "
                    "long-distance travel and fortune abroad..."
                ),
                "7th_house": (
                    "The lord of 7th house [planet] being in [position] indicates "
                    "foreign business and partnerships..."
                ),
                "rahu": "Rahu is the karaka for foreign matters. Rahu being in [position] indicates...",
                "timing_unavailable": "Specific timing for foreign career could not be calculated at this time.",
                "blocked_message": "There are some challenges for foreign career. Continue efforts with remedies.",
                "general_answer": "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary": "Summary",
                "remedies": "Remedies",
                "tell_client": "TELL CLIENT",
                "foreign_outlook": "Foreign Career Prospects",
                "timing_outlook": "Timing for Going Abroad",
                "risks_outlook": "Risk Analysis",
            },
        }
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        return {
            "Hindi": {
                "vedic": "वैदिक ज्योतिष के अनुसार,",
                "kp": "KP प्रणाली के अनुसार,",
            },
            "English": {
                "vedic": "According to Vedic astrology,",
                "kp": "According to KP astrology,",
            },
        }.get(language, {
            "vedic": "According to Vedic astrology,",
            "kp": "According to KP astrology,",
        })

    # ==========================================================================
    # AGE CALCULATION HELPER (FIX - aligned with doc1 pattern)
    # ==========================================================================

    def _calculate_age_on_date(self, dob_str: str, target_date_str: str) -> int:
        """Calculate age on a target date given DOB string."""
        try:
            dob = datetime.strptime(dob_str, "%d/%m/%Y")
            target = datetime.strptime(target_date_str, "%Y-%m-%d")
            return target.year - dob.year - (
                (target.month, target.day) < (dob.month, dob.day)
            )
        except Exception:
            return 0

    def _detect_minor(self, dob: Optional[str], dasha_timeline: Optional[Dict]) -> bool:
        """
        Detect if person is currently under 18.
        Minor logic is based on CURRENT age, not any future dasha age.
        Aligned with CareerDiscoveryAndEmploymentPromptBuilder._detect_minor().
        """
        if not dob:
            return False
        try:
            today = datetime.now()
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
            current_age = today.year - dob_dt.year - (
                (today.month, today.day) < (dob_dt.month, dob_dt.day)
            )
            return current_age < 18
        except Exception:
            return False

    # ==========================================================================
    # SYSTEM PROMPT
    # ==========================================================================

    def build_system_prompt(self, language: str = "English", is_timing: bool = False) -> str:
        if is_timing:
            weightage_text = "TIMING QUESTION: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%"
        else:
            weightage_text = "NON-TIMING QUESTION: Vedic 85% + KP Facts 15% (No Dasha needed)"

        example_12th = self._get_example_text(language, "12th_house")

        return f"""You are an expert KP and Vedic astrologer specializing in foreign career, overseas settlement, and international opportunities analysis.

**{weightage_text}**

════════════════════════════════════════════════════════════
AGE SAFETY RULE
════════════════════════════════════════════════════════════

If person is under 18:
• NEVER recommend immediate relocation abroad
• NEVER suggest workforce entry or joining overseas companies
• NEVER predict a specific year to "go abroad" or "settle overseas"
• Frame foreign career potential as long-term direction forming
• Treat timing windows as irrelevant — ignore them even if provided
• Treat all dashas as developmental/preparation cycles
• Never interpret dashas as relocation or career-start triggers

════════════════════════════════════════════════════════════
🚨 ANTI-HALLUCINATION RULES (CRITICAL)
════════════════════════════════════════════════════════════

1. NEVER INVENT DATES OR TIMING
   - If no timing windows are provided, do NOT make up dates
   - Do NOT guess years like "2027", "next year", "in 6 months"
   - Only mention specific dates if they appear in TIMING WINDOWS section

2. ONLY USE DATA PROVIDED
   - Do not invent planetary positions not in the data
   - Do not assume aspects not mentioned
   - If data is missing, say so clearly

3. DISTINGUISH FACTS FROM INTERPRETATION
   - Facts = from provided data
   - Interpretation = your astrological reasoning
   - Never present interpretation as computed fact

4. FOREIGN EXPOSURE LEVEL MUST COME FROM KP DATA
   - If KP analysis provides exposure_level, use that
   - Do NOT override KP verdict with Vedic interpretation

════════════════════════════════════════════════════════════
CRITICAL WRITING STYLE RULES
════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "12th Lord Jupiter in 9th house. Retrograde. Benefic."
   ✅ "{example_12th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for foreign career
   - Connect to the outcome

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

5. ANSWER THE ACTUAL QUESTION DIRECTLY

════════════════════════════════════════════════════════════
KP RULES (When KP data present)
════════════════════════════════════════════════════════════

KP section contains ONLY pre-computed evaluator output:
✅ Foreign Exposure Level
✅ KP Score
✅ KP Structural Indicators

KP section must NOT contain:
❌ LLM-derived KP analysis
❌ Reinterpretation of KP points
❌ Using Vedic to explain KP conclusions

IF KP POINTS HAVE NO RELEVANT INFO → Skip KP section, provide ONLY Vedic analysis.

════════════════════════════════════════════════════════════
RAHU/KETU RULE FOR FOREIGN MATTERS (FIX - was missing)
════════════════════════════════════════════════════════════

Nodes act through their STAR LORD for foreign matters.
Show: "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"

⚠️ Never judge Rahu/Ketu for foreign career by just their house occupation.
Their star lord's significations determine whether foreign opportunities manifest.

Rahu = Karaka for foreign lands, unconventional overseas roles, tech abroad.
Ketu = Karaka for spiritual/niche roles, isolation abroad, detached foreign stay.

════════════════════════════════════════════════════════════
KEY INTERNATIONAL CAREER HOUSES (VEDIC)
════════════════════════════════════════════════════════════

- 12th: Foreign lands, overseas settlement (PRIMARY)
- 9th: Long-distance travel, fortune abroad (PRIMARY)
- 7th: Foreign business, partnerships abroad (PRIMARY)
- 3rd: Short travels, courage to relocate
- 10th: Career (combined with 12th = foreign career)
- 4th: Home (leaving home = foreign settlement indicator)

════════════════════════════════════════════════════════════
⚠️ IMPORTANT LIMITATIONS
════════════════════════════════════════════════════════════

- Do NOT predict visa approval or legal outcomes
- Never override immigration or legal advice
- Frame obstacles as timing-related, not denial
- Distinguish temporary foreign work vs permanent settlement
"""

    # ==========================================================================
    # KP DATA HELPERS
    # ==========================================================================

    def _get_kp_availability(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        kp_data = additional_data.get("career_foreign_structural", {})
        return bool(kp_data and kp_data.get("indicators"))

    def _get_relevant_kp_points(self, additional_data: Dict, question_type: str) -> List[str]:
        if not additional_data or question_type == "remedies":
            return []
        kp_data = additional_data.get("career_foreign_structural", {})
        return kp_data.get("indicators", [])

    def _get_kp_exposure_level(self, additional_data: Dict) -> str:
        if not additional_data:
            return "Unknown"
        kp_data = additional_data.get("career_foreign_structural", {})
        return kp_data.get("exposure_level", "Unknown")

    def _is_blocked(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        exposure = self._get_kp_exposure_level(additional_data)
        if exposure == "Stable Local Career":
            return True
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if house_lords:
            weak_count = sum(
                1 for h in [12, 9, 7]
                if house_lords.get(h, {}).get("lord_strength_score", 50) < 30
            )
            if weak_count >= 2:
                return True
        return False

    # ==========================================================================
    # LAGNA LORD (with house_lords fallback)
    # ==========================================================================

    def _format_lagna_lord(self, additional_data: Dict) -> str:
        lagna_info = additional_data.get("lagna_info", {})

        if not lagna_info:
            house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
            info = house_lords.get(1, {})
            if info:
                lagna_info = {
                    "lagna_sign": info.get("house_sign", "N/A"),
                    "lagna_lord": info.get("lord", "N/A"),
                    "lagna_lord_house": info.get("lord_in_house"),
                    "lagna_lord_sign": info.get("lord_in_sign", "N/A"),
                    "lagna_lord_degree": info.get("lord_degree", 0),
                    "lagna_lord_dignity": info.get("lord_dignity", "Unknown"),
                }

        if not lagna_info:
            return (
                "═══════════════════════════════════════════════════════\n"
                "⚠️ LAGNA INFORMATION NOT AVAILABLE\n"
                "═══════════════════════════════════════════════════════\n"
                "Do NOT guess or invent lagna sign. Skip lagna analysis.\n"
                "═══════════════════════════════════════════════════════"
            )

        lord = lagna_info.get("lagna_lord", "N/A")
        lagna_sign = lagna_info.get("lagna_sign", "N/A")
        lord_house = lagna_info.get("lagna_lord_house", "N/A")
        lord_sign = lagna_info.get("lagna_lord_sign", "N/A")
        dignity = lagna_info.get("lagna_lord_dignity", "Unknown")

        personality_map = {
            "Sun": "Authority-seeking, prefers government/corporate foreign roles",
            "Moon": "Emotionally driven, may struggle with homesickness abroad",
            "Mars": "Action-oriented, adapts quickly to foreign environments",
            "Mercury": "Communicative, thrives in multicultural workplaces",
            "Jupiter": "Expansive, favored for education/consulting abroad",
            "Venus": "Comfort-seeking, drawn to culturally rich foreign environments",
            "Saturn": "Disciplined, patient — foreign career requires persistence",
            "Rahu": "Unconventional, strong affinity for foreign cultures and tech",
            "Ketu": "Detached, specialist niche roles preferred over corporate abroad",
        }
        personality = personality_map.get(lord, "Individual career approach abroad")

        house_placement_map = {
            1: "Self-driven, independent foreign career approach",
            2: "Money-motivated, wealth-focused foreign roles",
            3: "Communication-based, media/travel connections abroad",
            4: "Strong home attachment, foreign stay may feel temporary",
            5: "Creative field, speculation, education-related foreign opportunities",
            6: "Service-oriented, competitive professional abroad",
            7: "Partnership-focused, international client-facing roles",
            8: "Research, insurance, transformation through foreign experience",
            9: "Higher education, fortune, law, philosophy abroad",
            10: "Career-focused, professionally ambitious internationally",
            11: "Goal-oriented, networking, gains through overseas groups",
            12: "Natural foreign connection, spiritual/behind-the-scenes roles abroad",
        }
        house_note = ""
        if lord_house and isinstance(lord_house, int) and lord_house in house_placement_map:
            house_note = f"\nLagna Lord in House {lord_house}: {house_placement_map[lord_house]}"

        lines = [
            "═══════════════════════════════════════════════════════════",
            "🎯 LAGNA (ASCENDANT) — INTERNATIONAL CAREER PERSONALITY",
            "═══════════════════════════════════════════════════════════",
            "",
            f"Lagna Sign (1st House): {lagna_sign}",
            f"Lagna Lord: {lord}",
            f"Placed in: House {lord_house}, {lord_sign}",
            f"Dignity: {dignity}",
            "",
            f"Foreign Career Personality: {personality}",
            house_note,
            "",
            "⚠️ NOTE: This is the ONLY lagna for this person.",
            "Do NOT confuse lagna sign with Moon sign (rashi).",
            "═══════════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    # ==========================================================================
    # KP FOREIGN DATA
    # ==========================================================================

    def _format_kp_foreign_data(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        kp_data = additional_data.get("career_foreign_structural", {})
        if not kp_data:
            return ""

        exposure_level = kp_data.get("exposure_level", "Unknown")
        score = kp_data.get("score", 0)
        indicators = kp_data.get("indicators", [])

        emoji = {
            "Foreign / Multinational Exposure": "🌍",
            "Transferable / Mobile Role": "🚀",
        }.get(exposure_level, "🏠")

        lines = [
            "KP FOREIGN CAREER DATA (Pre-computed by Evaluator):",
            f"• Foreign Exposure Level: {emoji} {exposure_level}",
            f"• KP Score: {score}",
        ]
        if indicators:
            lines += ["", "KP Structural Indicators:"]
            for ind in indicators[:8]:
                if isinstance(ind, str) and ind.strip():
                    lines.append(f"  • {ind}")

        lines += ["", "NOTE: Restate these KP findings. Do NOT re-interpret further."]
        return "\n".join(lines)

    # ==========================================================================
    # TIMING WINDOWS (FIX - full box format aligned with doc1/doc2)
    # ==========================================================================

    def _format_timing_windows(self, additional_data: Dict) -> str:
        """
        Format BEST and NEAREST timing windows with full box layout.
        FIX: v9 returned 2 one-liner strings. Now matches doc1 pattern with score
        breakdown, age_at_start, trade-offs, and BEST=NEAREST detection.
        """
        if not additional_data:
            return ""
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""

        try:
            best = timing_data.get("best_window", {})
            nearest = timing_data.get("nearest_window", {})
            all_windows = timing_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = [
                "═══════════════════════════════════════════════════════════",
                "⏰ TIMING WINDOWS ANALYSIS",
                "═══════════════════════════════════════════════════════════",
                "",
                "⚠️ CRITICAL: You MUST mention BOTH windows below.",
                "Let user choose based on their situation.",
                "",
            ]

            # BEST WINDOW
            if best:
                lines += [
                    "╔═══════════════════════════════════════════════════════╗",
                    "║  🏆 BEST WINDOW (Highest Astrological Score)          ║",
                    "╚═══════════════════════════════════════════════════════╝",
                    "",
                    f"  Dasha: {best.get('dasha', 'N/A')}",
                    f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}",
                    f"  Score: {best.get('final_score', 0):.1f}/100",
                ]
                age = best.get("age_at_start")
                if age:
                    lines.append(f"  Age at start: {age} years")

                lines.append("")
                lines.append("  Why this is BEST:")

                score_maha = best.get("score_maha", 0)
                score_antara = best.get("score_antara", 0)
                score_paryantar = best.get("score_paryantar", 0)
                if score_maha or score_antara or score_paryantar:
                    lines.append(f"    • Maha Dasha score: {score_maha}/10")
                    lines.append(f"    • Antara Dasha score: {score_antara}/10")
                    lines.append(f"    • Pratyantar score: {score_paryantar}/10")
                else:
                    lines.append("    • Highest combined planetary alignment for foreign move")
                    lines.append("    • Strongest foreign career significations activated")

                transit_score = best.get("transit_score", 0)
                if transit_score:
                    lines.append(f"    • Transit support: {transit_score:.1f}%")

                lines += [
                    "",
                    "  Trade-off: May be further in future, but strongest alignment",
                    "",
                ]

            # NEAREST WINDOW
            if nearest:
                lines += [
                    "╔═══════════════════════════════════════════════════════╗",
                    "║  ⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity)    ║",
                    "╚═══════════════════════════════════════════════════════╝",
                    "",
                    f"  Dasha: {nearest.get('dasha', 'N/A')}",
                    f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}",
                    f"  Score: {nearest.get('final_score', 0):.1f}/100",
                ]
                age = nearest.get("age_at_start")
                if age:
                    lines.append(f"  Age at start: {age} years")

                lines.append("")

                # BEST = NEAREST detection
                if best and (
                    best.get("dasha") == nearest.get("dasha")
                    and best.get("start") == nearest.get("start")
                ):
                    lines += [
                        "  🎯 IDEAL SITUATION!",
                        "  The BEST window IS the NEAREST favorable window!",
                        "  You get optimal timing AND early opportunity for foreign career!",
                    ]
                else:
                    lines += [
                        "  Why this is NEAREST:",
                        "    • Earliest window with score >= 50",
                        "    • Can act sooner rather than waiting",
                        "",
                        "  Trade-off: Sooner but not absolute best alignment",
                    ]
                lines.append("")

            # Additional windows reference
            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Reference):")
                lines.append("-" * 50)
                for i, window in enumerate(all_windows[:5], 1):
                    dasha = window.get("dasha", "N/A")
                    start = window.get("start", "N/A")
                    end = window.get("end", "N/A")
                    score = window.get("final_score", 0)
                    is_best = best and dasha == best.get("dasha") and start == best.get("start")
                    is_nearest = nearest and dasha == nearest.get("dasha") and start == nearest.get("start")
                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                lines.append("")

            lines += [
                "═══════════════════════════════════════════════════════════",
                "YOUR RESPONSE MUST:",
                "  • Mention BOTH best and nearest windows with exact dates",
                "  • Explain WHY each is favorable for foreign career",
                "  • Let user choose: Wait for best OR Act sooner",
                "  • If best = nearest, emphasize this is ideal",
                "═══════════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return False
        return bool(timing_data.get("best_window") or timing_data.get("nearest_window"))

    # ==========================================================================
    # HOUSE LORDS (FIX - added PRIMARY/SECONDARY markers and assessment footer)
    # ==========================================================================

    def _format_house_lords(self, additional_data: Dict) -> str:
        """
        Format house lord data with ⭐ PRIMARY / ○ SECONDARY markers,
        STRONG/MODERATE/WEAK assessment per house, combust/retrograde labels.
        FIX: v9 had compact one-liner format with no assessment or priority markers.
        """
        if not additional_data:
            return ""
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = [
            "═══════════════════════════════════════════════════════════",
            "VEDIC HOUSE LORD ANALYSIS (International Career Houses)",
            "═══════════════════════════════════════════════════════════",
            "",
            "⚠️ NOTE: Vedic shows CAPACITY and EASE.",
            "   KP decides whether EVENT happens.",
            "   Use Vedic to explain effort required.",
            "",
        ]

        foreign_houses = {3, 4, 7, 9, 10, 12}
        priority_order = [12, 9, 7, 10, 3, 4]
        primary_houses = {12, 9, 7}

        house_meanings = {
            3: "Short Travel/Courage",
            4: "Home/Motherland",
            7: "Foreign Business/Partners",
            9: "Long Travel/Fortune Abroad",
            10: "Career/Profession",
            12: "Foreign Lands/Settlement",
        }

        for house_num in priority_order:
            if house_num not in house_lords:
                continue
            info = house_lords[house_num]
            if not info:
                continue

            marker = "⭐ PRIMARY" if house_num in primary_houses else "○ SECONDARY"
            meaning = house_meanings.get(house_num, "General")

            lord = info.get("lord", "N/A")
            lord_house = info.get("lord_in_house", "N/A")
            lord_sign = info.get("lord_in_sign", "N/A")
            dignity = info.get("lord_dignity", "N/A")
            strength = info.get("lord_strength_score", 0)

            conditions = []
            if info.get("lord_is_combust"):
                conditions.append("⚠️ COMBUST")
            if info.get("lord_is_retrograde"):
                conditions.append("🔄 RETROGRADE")
            degree = info.get("lord_degree")
            if degree:
                conditions.append(f"Degree: {degree:.1f}°")
            condition_str = " | ".join(conditions) if conditions else "Normal"

            planets = ", ".join(info.get("planets_in_house", [])) or "None"

            lines += [
                f"{marker} - HOUSE {house_num} ({meaning})",
                f"  Sign: {info.get('house_sign', 'N/A')}",
                f"  Lord: {lord}",
                f"  Placed in: House {lord_house}, {lord_sign}",
                f"  Dignity: {dignity}",
                f"  Strength: {strength}/100",
                f"  Condition: {condition_str}",
                f"  Planets in house: {planets}",
            ]

            # Assessment (FIX - was missing in v9)
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports foreign career strongly")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE - Mixed foreign career results")
            else:
                lines.append("  ⚠️ Assessment: WEAK - Challenges for this foreign house")

            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ==========================================================================
    # HOUSE ASPECTS (FIX - added net assessment per house)
    # ==========================================================================

    def _format_house_aspects(self, additional_data: Dict) -> str:
        """
        Format aspects with Net POSITIVE/CHALLENGING/BALANCED assessment per house.
        FIX: v9 listed benefic/malefic but never added the net assessment line.
        """
        if not additional_data:
            return ""
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        has_aspects = any(
            aspects_info.get(h, {}).get("benefic_aspects")
            or aspects_info.get(h, {}).get("malefic_aspects")
            for h in [12, 9, 7, 10, 3, 4]
        )
        if not has_aspects:
            return ""

        lines = [
            "═══════════════════════════════════════════════════════════",
            "PLANETARY ASPECTS ON INTERNATIONAL CAREER HOUSES",
            "═══════════════════════════════════════════════════════════",
            "",
        ]

        for house_num in [12, 9, 7, 10, 3, 4]:
            if house_num not in aspects_info:
                continue
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])

            if benefic or malefic:
                lines.append(f"• House {house_num}:")
                if benefic:
                    lines.append(f"  ✅ Benefic aspects: {', '.join(benefic)}")
                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")

                # FIX: net assessment was missing in v9
                if len(benefic) > len(malefic):
                    lines.append("  → Net: POSITIVE influence")
                elif len(malefic) > len(benefic):
                    lines.append("  → Net: CHALLENGING influence")
                else:
                    lines.append("  → Net: BALANCED influence")

                lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ==========================================================================
    # CURRENT DASHA (FIX - full box with anti-hallucination header)
    # ==========================================================================

    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """
        Format current dasha in full ═══ box with USE THIS - DON'T INVENT header.
        FIX: v9 returned a single bare line. Aligned with doc1/doc2 pattern.
        """
        if not current_dasha:
            return ""

        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end = date_range.get("end", "Unknown")

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon", "Ma": "Mars",
                "Me": "Mercury", "Ju": "Jupiter", "Ve": "Venus",
                "Ra": "Rahu", "Ke": "Ketu",
                "Saturn": "Saturn", "Sun": "Sun", "Moon": "Moon",
                "Mars": "Mars", "Mercury": "Mercury", "Jupiter": "Jupiter",
                "Venus": "Venus", "Rahu": "Rahu", "Ketu": "Ketu",
            }

            parts = dasha_name.replace(">", "-").replace("/", "-").split("-")
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted_dasha = " > ".join(full_names) if len(full_names) >= 2 else dasha_name

            lines = [
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS - DON'T INVENT)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL current dasha",
                "• Use for analyzing PRESENT circumstances",
                "• For FUTURE planning, see UPCOMING DASHA PERIODS",
                "• Do NOT invent different dasha periods",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    # ==========================================================================
    # DASHA TIMELINE (FIX - added international career guidelines footer)
    # ==========================================================================

    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        """
        Format dasha timeline with international career planet-to-role guidelines footer.
        FIX: v9 had no footer. Aligned with doc1 CAREER DASHA GUIDELINES pattern.
        """
        if not dasha_timeline:
            return ""

        try:
            current = dasha_timeline.get("current", [])
            future = dasha_timeline.get("next_10_years", [])

            if not any([current, future]):
                return ""

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon", "Ma": "Mars",
                "Me": "Mercury", "Ju": "Jupiter", "Ve": "Venus",
                "Ra": "Rahu", "Ke": "Ketu",
            }

            def parse_dasha(name: str) -> str:
                parts = name.replace(">", "-").replace("/", "-").split("-")
                return " > ".join(
                    dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()
                )

            lines = [
                "═══════════════════════════════════════════════════════",
                "DASHA TIMELINE (For Foreign Career Planning)",
                "═══════════════════════════════════════════════════════",
                "",
            ]

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    parsed = parse_dasha(d.get("dasha_name", ""))
                    dr = d.get("date_range", {})
                    lines.append(f"  • {parsed}")
                    lines.append(f"    {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years - For Foreign Career Planning):")
                lines.append("-" * 50)
                for i, d in enumerate(future[:15], 1):
                    parsed = parse_dasha(d.get("dasha_name", ""))
                    dr = d.get("date_range", {})
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            # FIX: Career-specific guidelines footer was missing in v9
            lines += [
                "═══════════════════════════════════════════════════════",
                "INTERNATIONAL CAREER DASHA GUIDELINES:",
                "• Sun/Jupiter → Authority roles, transfers to senior foreign positions",
                "• Rahu → Strong foreign affinity, tech abroad, unconventional overseas roles",
                "• Mercury → Multicultural communication roles, IT, international trade",
                "• Venus → Cultural exchange, luxury/hospitality abroad",
                "• Saturn → Patience needed; slow but stable foreign career build",
                "• Mars → Action-oriented; short foreign stints, engineering abroad",
                "• Ketu → Spiritual/research niche abroad; detached foreign stay",
                "• Moon → Emotional transition abroad; home attachment challenges",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ==========================================================================
    # OUTPUT FORMAT (centralised, with DASHA CONTEXT section added)
    # ==========================================================================

    def get_output_format(
        self,
        language: str,
        has_timing: bool,
        is_blocked: bool,
        has_relevant_kp: bool,
        question_type: str = "foreign_career",
        is_minor: bool = False,
        dob: Optional[str] = None,
    ) -> str:
        """
        Centralised output format for all sub-builders.
        FIX: v9 remedies/risks paths had inline format rather than routing here.
        FIX: Added DASHA CONTEXT section that was missing from v9 non-remedies paths.
        """
        starters = self._get_analysis_starters(language)
        lbl = {k: self._get_example_text(language, k) for k in [
            "general_answer", "astrological_analysis", "summary",
            "remedies", "tell_client", "foreign_outlook",
            "timing_outlook", "risks_outlook",
        ]}

        kp_para = ""
        if has_relevant_kp and question_type != "remedies":
            kp_para = f"""
PARAGRAPH 2 – KP CONFIRMATION:
This paragraph MUST begin with: "{starters['kp']}"
ONLY restate pre-computed KP findings. Do NOT add new interpretation.
The entire paragraph must remain KP-only. Do NOT switch to Vedic reasoning.
"""

        if question_type == "remedies":
            return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl['general_answer']} (2-3 lines):**
What issues exist and that remedies can help. No astrological jargon.

**{lbl['astrological_analysis']}:**  ← MANDATORY HEADER
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin strictly with: "{starters['vedic']}"
Identify weak areas for foreign career. Main chart challenges.
NOTE: VEDIC ONLY for remedies. No KP section.

PARAGRAPH 2 – Primary Remedy:
Most important remedy and WHY it helps.

PARAGRAPH 3 – Supporting Remedies:
Additional helpful practices.

**{lbl['summary']}:**
{lbl['tell_client']}: "[Priority order of remedies]"

**{lbl['remedies']} (Detailed):**
1. [Primary remedy with instructions]
2. [Rahu remedy for foreign adaptation]
3. [Jupiter remedy for protection abroad]
4. [Practical preparation advice]
═══════════════════════════════════════════════════════════════════════════════
"""

        if question_type == "risks":
            return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl['general_answer']} (2-3 lines):**
{lbl['risks_outlook']}.
Reassuring tone. Frame as areas to prepare for, not permanent problems.
NO astrological terms here.

**{lbl['astrological_analysis']}:**  ← MANDATORY HEADER
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin with: "{starters['vedic']}"
- Weak 12th house lord: Foreign settlement challenges
- Weak 9th house lord: Limited fortune abroad
- Strong 4th house: Home attachment
- Malefic aspects on foreign houses
Frame all as "tendencies," not certainties.
{kp_para}
PARAGRAPH {"3" if has_relevant_kp else "2"} – Areas of Attention:
Connect to practical preparation steps.

**{lbl['summary']}:**
{lbl['tell_client']}: "[Reassuring advice + practical preparation]"

**{lbl['remedies']}:**
- Remedies for weak planets
- Practical preparation advice
- DO NOT predict legal/visa issues
═══════════════════════════════════════════════════════════════════════════════
"""

        # Timing section for foreign career / timing / general
        # MINOR OVERRIDE: suppress timing, inject developmental block
        if is_minor:
            return f"""
═══════════════════════════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR — UNDER 18)
═══════════════════════════════════════════════════════════════════════════════

Person DOB: {dob}
The individual is currently under 18.

This response must follow DEVELOPMENTAL framing.

Guidelines:
• Do NOT predict specific relocation years
• Do NOT recommend immediate overseas workforce entry
• Do NOT provide timing window dates even if available
• Interpret foreign career indicators as long-term orientation

Interpretation Approach:
• Frame international exposure as a future direction
• Emphasize skill-building, education, language learning
• Present dashas as foundation-building cycles
• Use encouraging and growth-focused tone

INTERPRETATION RULE:
If chart shows foreign career potential:
→ Interpret as LONG-TERM career direction forming
→ Focus on language learning, international studies, competitive exam prep
→ Present foreign career as a future orientation, not an imminent event

Tone:
• Developmental
• Preparation-focused
• Future-aligned
• Encouraging

This override is MANDATORY for all questions.
═══════════════════════════════════════════════════════════════════════════════

OUTPUT FORMAT:

**{lbl['general_answer']} (2-3 lines):**
Frame foreign career as a long-term direction, not an immediate plan.
No timing, no relocation dates. Encouraging and developmental.
NO astrological terms here.

**{lbl['astrological_analysis']}:**  ← MANDATORY HEADER. DO NOT OMIT.
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin with: "{starters['vedic']}"
- Explain which houses support future international exposure
- Frame as foundation building and long-term potential
- No prediction of specific relocation year

{kp_para}
PARAGRAPH {"3" if has_relevant_kp else "2"} – Preparation Phase:
- Skill-building for international career
- Language, education, and competitive exam readiness
- What current planetary cycle is developing for the future

**{lbl['summary']}:**
{lbl['tell_client']}: "[Long-term direction + preparation advice]"
Frame: "Your chart shows [orientation]. Focus on [preparation] now."

**{lbl['remedies']}:**
- Remedies to strengthen foreign career indicators for the future
- Study and preparation recommendations
- DO NOT predict visa/relocation dates
═══════════════════════════════════════════════════════════════════════════════
"""

        timing_para = ""
        if has_timing and not is_blocked:
            timing_para = """
PARAGRAPH (TIMING): Connect dasha to timing windows.
Mention BOTH the BEST and NEAREST windows with exact dates.
If BEST = NEAREST, emphasise this is ideal.
DO NOT mention obstacles here.
"""
        elif is_blocked:
            timing_para = """
PARAGRAPH (CHALLENGES): Explain why specific timing is not available.
Frame as areas needing attention, not permanent denial.
"""

        p3_label = "3" if has_relevant_kp else "2"
        p4_label = "4" if has_relevant_kp else "3"

        return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl['general_answer']} (2-3 lines):**
{"Mention BEST and NEAREST timing windows." if has_timing and not is_blocked else ""}
{"State foreign career indicators are limited; recommend remedies." if is_blocked else ""}
{"State that timing needs further analysis." if not has_timing and not is_blocked else ""}
Distinguish temporary work abroad vs permanent settlement.
NO astrological terms here. Write as a caring advisor.

**{lbl['astrological_analysis']}:**  ← MANDATORY HEADER. DO NOT OMIT.
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin with: "{starters['vedic']}"
- 12th house (foreign lands/settlement) — CRITICAL
- 9th house (long travel/fortune abroad) — CRITICAL
- 7th house (foreign business/partnerships)
- 3rd house (courage to relocate)
- 10th house (career + 12th = foreign career)
- Rahu/Jupiter analysis for foreign matters
- Ketu: niche/spiritual foreign roles if present
{kp_para}
PARAGRAPH {p3_label} – Supporting Houses & Dasha:
Connect dasha periods to foreign career timing.
{timing_para}
PARAGRAPH {p4_label} – DASHA CONTEXT:
- Current dasha period and its impact on foreign career NOW
- Upcoming favorable dasha for foreign move (from timeline)
- Connect dasha lords to foreign house significations

**{lbl['summary']}:**
{lbl['tell_client']}: "['Specific timing with both windows' if timing else 'Continue efforts + remedies']"
Distinguish: Temporary work abroad vs Permanent settlement.

**{lbl['remedies']}:**
{"Provide full remedies to strengthen foreign career indicators." if is_blocked else "1–2 remedies for smooth transition."}
- Rahu remedies for foreign adaptation
- Jupiter remedies for protection abroad
- DO NOT predict visa/legal outcomes
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # TIMING INSTRUCTION BLOCK (shared by sub-builders)
    # ==========================================================================

    def _build_timing_instruction(
        self,
        is_blocked: bool,
        has_timing: bool,
        exposure_level: str,
        timing_data: str,
        current_dasha_str: str,
        language: str,
    ) -> str:
        timing_unavailable = self._get_example_text(language, "timing_unavailable")
        blocked_message = self._get_example_text(language, "blocked_message")

        if is_blocked:
            return f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ FOREIGN CAREER CHALLENGING — NO SPECIFIC TIMING TO PROVIDE
═══════════════════════════════════════════════════════════════════════════════

The chart shows limited foreign career indicators (KP Exposure: {exposure_level}).

🚫 DO NOT provide specific timing windows or dates for foreign settlement.
✅ DO mention current dasha period (if available) for general context.
✅ DO recommend remedies to strengthen foreign career prospects.
✅ DO suggest ways to create opportunities despite chart limitations.

{current_dasha_str if current_dasha_str else "Current dasha information not available."}

MESSAGE TO CONVEY: "{blocked_message}"
═══════════════════════════════════════════════════════════════════════════════
"""
        elif has_timing:
            return f"""
═══════════════════════════════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE — USE THESE DATES
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{current_dasha_str if current_dasha_str else ""}

INSTRUCTIONS:
- Use ONLY the dates provided above
- BEST window = most favorable time for foreign career/relocation
- NEAREST window = soonest opportunity
- Mention BOTH windows in your answer
- Distinguish temporary work abroad vs permanent settlement
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            return f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING CALCULATED
═══════════════════════════════════════════════════════════════════════════════

No specific timing windows were calculated, but foreign career is NOT blocked.

🚫 DO NOT invent specific dates.
✅ DO explain that favorable periods should be monitored.
✅ DO recommend consulting for detailed timing analysis.

{current_dasha_str if current_dasha_str else ""}

MESSAGE: "{timing_unavailable}"
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # ROUTING (FIX - .get() not .pop(), entry log added)
    # ==========================================================================

    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """
        Main routing method.
        FIX: uses .get() not .pop() for additional_data.
        FIX: added logger.warning entry log (aligned with doc1 pattern).
        """
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            logger.warning("🔥 INTERNATIONAL CAREER PROMPT BUILDER EXECUTED")

            additional_data = kwargs.get("additional_data", {})  # ← .get() not .pop()
            current_dasha = kwargs.get("current_dasha")
            dasha_timeline = kwargs.get("dasha_timeline")
            raw = "\n".join(technical_points) if technical_points else ""

            # ----------------------------
            # GLOBAL MINOR DETECTION
            # ----------------------------
            dob = kwargs.get("dob")
            is_minor = self._detect_minor(dob, dasha_timeline)
            logger.warning(f"[INTL CAREER] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

            logger.info(
                f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}"
            )

            if "Foreign Career Potential" in sub_subdomain or "International Career" in sub_subdomain:
                return self._build_foreign_career_prompt(
                    question, additional_data, raw, language, current_dasha, dasha_timeline,
                    is_minor=is_minor, dob=dob
                )
            elif "Timing" in sub_subdomain:
                return self._build_timing_prompt(
                    question, additional_data, raw, language, current_dasha, dasha_timeline,
                    is_minor=is_minor, dob=dob
                )
            elif "Risk" in sub_subdomain or "Challenge" in sub_subdomain:
                return self._build_risks_prompt(
                    question, additional_data, raw, language, current_dasha
                )
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(
                    question, additional_data, raw, language
                )
            else:
                return self._build_general_prompt(
                    question, additional_data, raw, language, current_dasha, dasha_timeline,
                    is_minor=is_minor, dob=dob
                )

        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # FALLBACK
    # ==========================================================================

    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self.get_language_instruction(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in foreign career and overseas opportunities.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear actionable statement.
Focus on houses 12th, 9th, 7th for foreign career analysis.
Do NOT predict visa or legal outcomes.
"""

    # ==========================================================================
    # FOREIGN CAREER POTENTIAL PROMPT
    # ==========================================================================

    def _build_foreign_career_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        current_dasha: Optional[Dict],
        dasha_timeline: Optional[Dict],
        is_minor: bool = False,
        dob: Optional[str] = None,
    ) -> str:
        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%Y-%m-%d")

        exposure_level = self._get_kp_exposure_level(additional_data)
        is_blocked = self._is_blocked(additional_data)
        # If minor, suppress timing windows entirely
        has_timing = self._has_valid_timing_windows(additional_data) and not is_minor
        kp_points = self._get_relevant_kp_points(additional_data, "foreign_career")
        has_relevant_kp = bool(kp_points)

        kp_data_str = self._format_kp_foreign_data(additional_data) if has_relevant_kp else ""
        timing_data_str = self._format_timing_windows(additional_data) if not is_minor else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        lagna_str = self._format_lagna_lord(additional_data)
        current_dasha_str = self._format_current_dasha(current_dasha)
        timeline_str = self._format_dasha_timeline(dasha_timeline)

        # Minor: developmental override replaces timing_instruction
        if is_minor:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR — UNDER 18)
═══════════════════════════════════════════════════════════════════════════════

Person DOB: {dob}
Person is currently under 18.

🚫 DO NOT predict specific year of foreign relocation or overseas career start.
🚫 DO NOT show timing windows even if data exists.
✅ DO frame foreign career potential as long-term career direction.
✅ DO focus on preparation: language learning, international studies, competitive exams.
✅ DO use current dasha as developmental context only.

{current_dasha_str if current_dasha_str else ""}
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            timing_instruction = self._build_timing_instruction(
                is_blocked, has_timing, exposure_level,
                timing_data_str, current_dasha_str, language
            )

        kp_section = ""
        if has_relevant_kp:
            prefix = "LIMITED " if is_blocked else ""
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP FOREIGN CAREER ANALYSIS DATA ({prefix}):
═══════════════════════════════════════════════════════════════════════════════

{kp_data_str}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""

        output_fmt = self.get_output_format(
            language, has_timing, is_blocked, has_relevant_kp, "foreign_career",
            is_minor=is_minor, dob=dob
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN CAREER POTENTIAL / OVERSEAS SETTLEMENT
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
KP Exposure Level: {exposure_level}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_str}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{timeline_str if timeline_str else ""}

{raw if raw else ""}

{output_fmt}
"""

    # ==========================================================================
    # TIMING PROMPT
    # ==========================================================================

    def _build_timing_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        current_dasha: Optional[Dict],
        dasha_timeline: Optional[Dict],
        is_minor: bool = False,
        dob: Optional[str] = None,
    ) -> str:
        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%Y-%m-%d")

        exposure_level = self._get_kp_exposure_level(additional_data)
        is_blocked = self._is_blocked(additional_data)
        # Minor: suppress timing windows
        has_timing = self._has_valid_timing_windows(additional_data) and not is_minor
        kp_points = self._get_relevant_kp_points(additional_data, "timing")
        has_relevant_kp = bool(kp_points)

        kp_data_str = self._format_kp_foreign_data(additional_data) if has_relevant_kp else ""
        timing_data_str = self._format_timing_windows(additional_data) if not is_minor else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        lagna_str = self._format_lagna_lord(additional_data)
        current_dasha_str = self._format_current_dasha(current_dasha)
        timeline_str = self._format_dasha_timeline(dasha_timeline)

        if is_minor:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR — UNDER 18)
═══════════════════════════════════════════════════════════════════════════════

Person DOB: {dob}
Person is currently under 18.

🚫 DO NOT give specific year or date for going abroad.
🚫 DO NOT present timing windows even if data exists.
✅ DO describe current dasha as a preparation/development cycle.
✅ DO frame as: "Your chart supports future international exposure — focus on [preparation]."

{current_dasha_str if current_dasha_str else ""}
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            timing_instruction = self._build_timing_instruction(
                is_blocked, has_timing, exposure_level,
                timing_data_str, current_dasha_str, language
            )

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data_str}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""

        output_fmt = self.get_output_format(
            language, has_timing, is_blocked, has_relevant_kp, "timing",
            is_minor=is_minor, dob=dob
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN CAREER TIMING / WHEN TO GO ABROAD
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
KP Exposure Level: {exposure_level}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_str}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{timeline_str if timeline_str else ""}

{raw if raw else ""}

{output_fmt}
"""

    # ==========================================================================
    # RISKS PROMPT (FIX - now routes through get_output_format)
    # ==========================================================================

    def _build_risks_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        current_dasha: Optional[Dict],
    ) -> str:
        """
        FIX: v9 had inline output format. Now routes through get_output_format()
        aligned with doc1 pattern.
        """
        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%Y-%m-%d")

        exposure_level = self._get_kp_exposure_level(additional_data)
        kp_points = self._get_relevant_kp_points(additional_data, "risks")
        has_relevant_kp = bool(kp_points)

        kp_data_str = self._format_kp_foreign_data(additional_data) if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        lagna_str = self._format_lagna_lord(additional_data)
        current_dasha_str = self._format_current_dasha(current_dasha)

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data_str}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""

        output_fmt = self.get_output_format(
            language, False, False, has_relevant_kp, "risks"
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN CAREER RISKS / CHALLENGES
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15% (NON-TIMING)
KP Exposure Level: {exposure_level}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY RULES:
- NEVER induce fear about foreign career
- Frame as "areas needing attention" not "problems"
- All indications are TENDENCIES not certainties
- Do NOT predict visa rejection or legal issues
═══════════════════════════════════════════════════════════════════════════════

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_str}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{current_dasha_str if current_dasha_str else ""}

{raw if raw else ""}

{output_fmt}
"""

    # ==========================================================================
    # REMEDIES PROMPT (FIX - now routes through get_output_format)
    # ==========================================================================

    def _build_remedies_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
    ) -> str:
        """
        FIX: v9 had inline output format. Now routes through get_output_format()
        aligned with doc1 pattern.
        """
        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%Y-%m-%d")

        exposure_level = self._get_kp_exposure_level(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        lagna_str = self._format_lagna_lord(additional_data)

        output_fmt = self.get_output_format(
            language, False, False, False, "remedies"
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN CAREER REMEDIES
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY — LLM-driven practical question)
KP Exposure Level: {exposure_level}
Has Relevant KP: NO
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_str}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR FOREIGN CAREER:
═══════════════════════════════════════════════════════════════════════════════

12th LORD WEAK: Strengthen with gemstone/mantra of 12th lord
9th LORD WEAK: Jupiter remedies, Thursday fasts
RAHU AFFLICTION: Donate to poor, Durga worship
SATURN DELAYS: Saturday charity, service to elderly
JUPITER WEAK: Yellow items, Vishnu worship
4th HOUSE STRONG (home attachment): Remedies to balance attachment
═══════════════════════════════════════════════════════════════════════════════

{output_fmt}
"""

    # ==========================================================================
    # GENERAL PROMPT
    # ==========================================================================

    def _build_general_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        current_dasha: Optional[Dict],
        dasha_timeline: Optional[Dict],
        is_minor: bool = False,
        dob: Optional[str] = None,
    ) -> str:
        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%Y-%m-%d")

        timing_keywords = [
            "when", "time", "timing", "year", "date", "delay",
            "कब", "समय", "विलंब",
        ]
        is_timing = any(kw in question.lower() for kw in timing_keywords)

        exposure_level = self._get_kp_exposure_level(additional_data)
        is_blocked = self._is_blocked(additional_data)
        # Minor suppresses timing
        has_timing = self._has_valid_timing_windows(additional_data) and not is_blocked and not is_minor
        kp_points = self._get_relevant_kp_points(additional_data, "foreign_career")
        has_relevant_kp = bool(kp_points)

        kp_data_str = self._format_kp_foreign_data(additional_data) if has_relevant_kp else ""
        timing_data_str = (
            self._format_timing_windows(additional_data)
            if is_timing and not is_minor
            else ""
        )
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        lagna_str = self._format_lagna_lord(additional_data)
        current_dasha_str = self._format_current_dasha(current_dasha) if is_timing else ""
        timeline_str = self._format_dasha_timeline(dasha_timeline) if is_timing else ""

        weightage = (
            "Vedic 55% + KP 30% + Dasha 10% + Aspects 5%"
            if is_timing
            else "Vedic 85% + KP Facts 15%"
        )

        timing_instruction = ""
        if is_timing:
            timing_instruction = self._build_timing_instruction(
                is_blocked, has_timing, exposure_level,
                timing_data_str, current_dasha_str, language
            )

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data_str}
"""

        output_fmt = self.get_output_format(
            language, has_timing and not is_blocked, is_blocked,
            has_relevant_kp, "foreign_career",
            is_minor=is_minor, dob=dob
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: INTERNATIONAL CAREER (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: {weightage}
KP Exposure Level: {exposure_level}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_str}

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{timeline_str if timeline_str else ""}

{raw if raw else ""}

{output_fmt}
"""
"""
Fighting Court Case – LLM Prompts v3.0 (COMPLETE FIX)

CRITICAL FIXES FROM v2.0:
✅ MINOR DETECTION - Age-aware responses, never recommend litigation for under-18
✅ LANGUAGE HANDLING - Proper get_language_instruction() matching Career/Finance patterns
✅ UNIFIED VERDICT DISPLAY - Legal suitability matrix aligned with Career/Finance patterns
✅ FLOWING ANSWERS - Output format produces narrative paragraphs, not bullet dumps
✅ HINDI/ENGLISH/HINGLISH - Full trilingual support
✅ ANTI-HALLUCINATION RULES - Strengthened
✅ TIMING WINDOWS - BEST + NEAREST format matching Finance pattern
✅ LAGNA INFO - Uses lagna_info from evaluator v3.0
✅ DASHA CONTEXT - Consistent mode handling
✅ CRIMINAL CASE SENSITIVITY - Extra care for criminal matters

Weightage:
- TIMING QUESTIONS: Vedic 70% + Dasha 30%
- NON-TIMING QUESTIONS: Vedic 100%

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from FightingCourtCaseEvaluator v3.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["legal_timing_windows"]         = { has_timing, best_window, nearest_window, all_favorable }
additional_data["legal_dasha_context"]          = { mode, reference }
additional_data["legal_outcome_analysis"]       = { outcome_likelihood, score, favorable_factors, ... }
additional_data["legal_duration_analysis"]      = { duration_estimate, delay_factors, speed_factors }
additional_data["legal_risks_analysis"]         = { risk_level, risk_score, risks, protective_factors }
additional_data["legal_opponent_analysis"]      = { opponent_strength, your_advantage, strategy_hints }
additional_data["legal_suitability_matrix"]     = { Full Litigation: {rating, vedic_reasoning}, ... }
additional_data["lagna_info"]                   = { lagna_sign, lagna_lord, lagna_lord_house, ... }
═══════════════════════════════════════════════════════════════════════════════
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

DOMAIN_PREFIX = "legal"


class FightingCourtCasePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Legal → Fighting Court Case
    v3.0 - Full parity with Finance/Career: minor detection, language, flowing output
    """

    domain = "Legal"
    subtopic = "Fighting Court Case"

    # ==========================================================================
    # LANGUAGE INSTRUCTION  (matches Career v10.0 pattern)
    # ==========================================================================
    def get_language_instruction(self, language: str) -> str:
        """Get language instruction — matches Career/Finance pattern exactly."""
        lang = language.strip().lower() if language else "english"

        if lang == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for ALL main content.
Use English ONLY for technical astrological terms (planet names, house numbers, aspects).
Example: "आपके केस में **6th house** के स्वामी **Mars** हैं।"
Example: "**Saturn** के प्रभाव से देरी हो सकती है।"
NEVER mix Roman script for Hindi words.
"""
        elif lang in ("hinglish", "roman hindi"):
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke case mein 6th house ke swami Mars hain."
Example: "Saturn ke prabhav se deri ho sakti hai."
Keep it conversational and easy to read.
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear, conversational English.
Explain technical terms clearly where needed.
Avoid overly formal or legal language — keep it accessible.
"""

    # ==========================================================================
    # MINOR DETECTION  (matches Career v10.0 pattern exactly)
    # ==========================================================================
    def _detect_minor(self, dob: str) -> bool:
        """
        Detect if person is currently under 18.
        Returns True if minor, False otherwise.
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
    def build_system_prompt(self, language: str = "English", case_type: str = "civil", is_timing: bool = False) -> str:
        """Build system prompt for legal analysis."""

        if is_timing:
            weightage_text = "TIMING QUESTION: Vedic 70% + Dasha 30%"
        else:
            weightage_text = "NON-TIMING QUESTION: Vedic 100%"

        case_type_note = ""
        if case_type == "criminal":
            case_type_note = """
⚠️ CRIMINAL CASE - EXTRA SENSITIVITY REQUIRED:
- Never predict imprisonment with certainty
- Frame penalties as "potential" not "definite"
- Always recommend experienced criminal lawyer
- Focus on protective factors and remedies
"""

        return f"""You are an expert Vedic astrologer specializing in legal matters, court cases, and dispute resolution.

**{weightage_text}**

{case_type_note}

════════════════════════════════════════════════════════════
AGE SAFETY RULE
════════════════════════════════════════════════════════════

If person is under 18:
• NEVER advise them to fight a court case independently
• NEVER frame legal action as their personal responsibility
• Frame analysis as guidance for family/guardians
• Refer to the situation as "the family's legal matter"
• Keep tone supportive, not alarmist

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

4. ASPECT RULE (CRITICAL):
   - ONLY mention planetary aspects IF explicitly present in ASPECTS DATA
   - NEVER infer aspects from house placement
   - If ASPECTS DATA is empty, say: "No explicit planetary aspects are indicated"

════════════════════════════════════════════════════════════
CRITICAL WRITING STYLE RULES
════════════════════════════════════════════════════════════

1. WRITE IN FLOWING PARAGRAPHS — NOT BULLET LISTS
   ❌ "6th Lord Mars in 10th house. Strong. Malefic."
   ✅ "The lord of the 6th house, Mars, is placed in the 10th house in Capricorn,
       where it gains directional strength. This indicates a strong fighting capacity
       and ability to sustain legal proceedings."

2. "TELL CLIENT:" ONLY IN FINAL SUMMARY

3. ANSWER THE ACTUAL QUESTION DIRECTLY — before analysis

4. NEVER LIST ASTROLOGICAL FACTS WITHOUT WEAVING THEM INTO MEANING

════════════════════════════════════════════════════════════
KEY HOUSES FOR LEGAL ANALYSIS
════════════════════════════════════════════════════════════

- 6th House: Litigation, disputes, enemies (YOUR FIGHTING ABILITY)
- 7th House: Opponent, adversary (OPPONENT'S STRENGTH)
- 8th House: Hidden matters, penalties, fines
- 9th House: Judges, law, justice
- 11th House: Gains, victory
- 12th House: Losses, imprisonment, expenses

Key Karakas:
- Saturn: Law, delays, punishment
- Jupiter: Judges, favorable verdicts
- Mars: Courage to fight
- Mercury: Documents, lawyers

════════════════════════════════════════════════════════════
⚠️ ETHICAL NOTES
════════════════════════════════════════════════════════════

- NEVER advise illegal actions
- NEVER guarantee specific outcomes
- ALWAYS recommend qualified legal counsel
- Describe opponent strength neutrally
- All timing indications are TENDENCIES not certainties

"""

    # ==========================================================================
    # HELPER: Get language-specific labels
    # ==========================================================================
    def _get_labels(self, language: str) -> Dict[str, str]:
        """Return UI labels in the correct language."""
        lang = language.strip().lower() if language else "english"

        if lang == "hindi":
            return {
                "general_answer":        "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary":               "सारांश",
                "remedies_astro":        "ज्योतिषीय उपाय",
                "remedies_general":      "सामान्य उपाय",
                "tell_client":           "ग्राहक को बताएं",
                "outcome_label":         "केस परिणाम",
                "duration_label":        "अवधि अनुमान",
                "risk_label":            "जोखिम स्तर",
                "timing_unavailable":    "केस समाप्ति के लिए विशिष्ट समय की गणना उपलब्ध नहीं है।",
                "vedic_starter":         "वैदिक ज्योतिष के अनुसार,",
                "minor_note":            "⚠️ यह विश्लेषण परिवार/अभिभावक के मार्गदर्शन के लिए है।",
            }
        elif lang in ("hinglish", "roman hindi"):
            return {
                "general_answer":        "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary":               "Summary",
                "remedies_astro":        "Astrological Remedies",
                "remedies_general":      "General Remedies",
                "tell_client":           "TELL CLIENT",
                "outcome_label":         "Case Outcome",
                "duration_label":        "Duration Estimate",
                "risk_label":            "Risk Level",
                "timing_unavailable":    "Case conclusion timing calculate nahi ho payi abhi.",
                "vedic_starter":         "Vedic jyotish ke anusar,",
                "minor_note":            "⚠️ Yeh analysis family/guardian ke guidance ke liye hai.",
            }
        else:
            return {
                "general_answer":        "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary":               "Summary",
                "remedies_astro":        "Astrological Remedies",
                "remedies_general":      "General Remedies",
                "tell_client":           "TELL CLIENT",
                "outcome_label":         "Case Outcome",
                "duration_label":        "Duration Estimate",
                "risk_label":            "Risk Level",
                "timing_unavailable":    "Specific timing for case conclusion could not be calculated at this time.",
                "vedic_starter":         "According to Vedic astrology,",
                "minor_note":            "⚠️ This analysis is intended as guidance for family/guardians.",
            }

    # ==========================================================================
    # HELPER: Minor warning block
    # ==========================================================================
    def _format_minor_block(self, dob: str, language: str) -> str:
        """Build the minor-mode instruction block shown in the prompt."""
        labels = self._get_labels(language)
        return f"""
════════════════════════════════════════════════════════════
🚨 MINOR MODE ACTIVE — SPECIAL HANDLING REQUIRED
════════════════════════════════════════════════════════════

Person DOB: {dob}
Current age is under 18.

{labels['minor_note']}

STRICT RULES:
• Do NOT address the minor as the one fighting the case
• Refer to "the family's legal matter" or "your family's case"
• Do NOT prescribe personal litigation strategy to the minor
• Do NOT say "you should fight" or "settle the case"
• Keep tone: informative, calm, guardian-focused

Timing windows and dasha periods:
• Interpret as awareness for family planning
• Do NOT predict the minor's personal legal actions

════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # HELPER: Lagna block  (matches Finance _format_lagna_lord pattern)
    # ==========================================================================
    def _format_lagna_info(self, additional_data: Dict) -> str:
        """Format lagna info from evaluator v3.0."""
        lagna = additional_data.get("lagna_info", {})

        if not lagna:
            return """
═══════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════
Do NOT guess or invent lagna sign.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════
"""

        lord        = lagna.get("lagna_lord", "N/A")
        sign        = lagna.get("lagna_sign", "N/A")
        lord_house  = lagna.get("lagna_lord_house", "N/A")
        lord_sign   = lagna.get("lagna_lord_sign", "N/A")
        dignity     = lagna.get("lagna_lord_dignity", "Unknown")
        degree      = lagna.get("lagna_lord_degree", 0)

        # Legal personality map
        personality_map = {
            "Sun":     "Authoritative, self-confident in legal matters, prefers direct confrontation",
            "Moon":    "Emotionally affected by disputes, needs stable legal counsel",
            "Mars":    "Aggressive fighter, strong stamina for litigation",
            "Mercury": "Document-savvy, good at arguments and negotiations",
            "Jupiter": "Seeks fair judgment, benefits from senior legal help",
            "Venus":   "Prefers compromise and settlement over prolonged battle",
            "Saturn":  "Patient but persistent, delays likely but eventual resolution",
            "Rahu":    "Unconventional strategies, may benefit from complex legal tactics",
            "Ketu":    "Detached approach, may benefit from spiritual or alternative resolution",
        }
        personality = personality_map.get(lord, "Unique approach to legal matters")

        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) — LEGAL PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        if degree:
            lines.append(f"Degree: {degree:.2f}°")
        lines.append("")
        lines.append(f"Legal Personality: {personality}")
        lines.append("")
        lines.append("⚠️ CRITICAL: This is the ONLY lagna for this person.")
        lines.append("Do NOT confuse with Moon sign.")
        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Legal Suitability Matrix  (mirrors Finance _format_investment_matrix)
    # ==========================================================================
    def _format_legal_matrix(self, additional_data: Dict) -> str:
        """Format legal strategy suitability matrix for LLM."""
        matrix = additional_data.get("legal_suitability_matrix", {})
        if not matrix:
            return ""

        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("📊 LEGAL STRATEGY SUITABILITY MATRIX")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("Based on Vedic analysis — use this to frame your strategy section:")
        lines.append("")
        lines.append("| Strategy | Rating | Vedic Reasoning |")
        lines.append("|----------|--------|-----------------|")

        for strategy, details in matrix.items():
            rating    = details.get("rating", "UNKNOWN")
            reasoning = details.get("vedic_reasoning", "")

            if rating == "HIGH":
                marker = "✅"
            elif rating == "MODERATE":
                marker = "⚖️"
            elif rating in ("LOW", "VERY LOW"):
                marker = "○"
            else:
                marker = "?"

            # Truncate long reasoning for table
            short = reasoning[:55] + "..." if len(reasoning) > 58 else reasoning
            lines.append(f"| {marker} **{strategy}** | {rating} | {short} |")

        lines.append("")
        lines.append("⚠️ Use this matrix CONSISTENTLY throughout your answer.")
        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Timing windows  (matches Finance + Career pattern)
    # ==========================================================================
    def _format_timing_windows(self, additional_data: Dict) -> str:
        """Format BEST and NEAREST timing windows — matches Finance/Career pattern."""
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""

        try:
            best     = timing_data.get("best_window", {})
            nearest  = timing_data.get("nearest_window", {})
            all_wins = timing_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⏰ TIMING WINDOWS ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: You MUST mention BOTH windows below.")
            lines.append("Let the person choose based on their situation.")
            lines.append("")

            # BEST WINDOW
            if best:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  🏆 BEST WINDOW (Highest Astrological Score)          ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                score_maha     = best.get("score_maha", 0)
                score_antara   = best.get("score_antara", 0)
                score_paryantar = best.get("score_paryantar", 0)
                if score_maha or score_antara or score_paryantar:
                    lines.append("")
                    lines.append("  Why this is BEST:")
                    lines.append(f"    • Maha Dasha score: {score_maha}/10")
                    lines.append(f"    • Antara Dasha score: {score_antara}/10")
                    lines.append(f"    • Pratyantar score: {score_paryantar}/10")
                transit = best.get("transit_score", 0)
                if transit:
                    lines.append(f"    • Transit support: {transit:.1f}%")
                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest alignment")
                lines.append("")

            # NEAREST WINDOW
            if nearest:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  ⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity)    ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                age = nearest.get("age_at_start")
                if age:
                    lines.append(f"  Age at start: {age} years")
                lines.append("")

                # Same window check
                if best and (best.get("dasha") == nearest.get("dasha") and
                             best.get("start") == nearest.get("start")):
                    lines.append("  🎯 IDEAL SITUATION!")
                    lines.append("  The BEST window IS the NEAREST window!")
                    lines.append("  Optimal timing AND earliest opportunity — emphasize this!")
                else:
                    lines.append("  Trade-off: Sooner opportunity, not absolute best alignment")
                lines.append("")

            # Other windows
            if len(all_wins) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Reference):")
                lines.append("-" * 50)
                for i, window in enumerate(all_wins[:5], 1):
                    dasha = window.get("dasha", "N/A")
                    start = window.get("start", "N/A")
                    end   = window.get("end", "N/A")
                    score = window.get("final_score", 0)

                    is_best    = best    and dasha == best.get("dasha")    and start == best.get("start")
                    is_nearest = nearest and dasha == nearest.get("dasha") and start == nearest.get("start")

                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for legal resolution")
            lines.append("  • Let person choose: wait for best OR act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal")
            lines.append("═══════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return False
        return bool(timing_data.get("best_window") or timing_data.get("nearest_window"))

    # ==========================================================================
    # HELPER: Current dasha  (matches Career pattern)
    # ==========================================================================
    def _format_current_dasha(self, additional_data: Dict) -> str:
        """Format current dasha — matches Career/Finance pattern."""
        current_dasha = additional_data.get(f"{DOMAIN_PREFIX}_current_dasha") or \
                        additional_data.get("current_dasha", {})
        if not current_dasha:
            return ""

        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end   = date_range.get("end", "Unknown")

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon",
                "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu",
            }
            parts = dasha_name.replace(">", "-").replace("/", "-").split("-")
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted = " > ".join(full_names) if len(full_names) >= 2 else dasha_name

            lines = [
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS — DON'T INVENT)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL dasha running now",
                "• Use for present legal circumstances",
                "• For future timing, refer to TIMING WINDOWS above",
                "• Do NOT invent different dasha periods",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    # ==========================================================================
    # HELPER: Outcome, Duration, Risks, Opponent  (formatted as structured blocks)
    # ==========================================================================
    def _format_outcome_analysis(self, additional_data: Dict) -> str:
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        if not outcome:
            return ""

        lines = ["CASE OUTCOME ANALYSIS:"]
        lines.append(f"• Outcome Likelihood: {outcome.get('outcome_likelihood', 'UNCERTAIN')}")
        lines.append(f"• Score: {outcome.get('score', 50)}/100")

        fav = outcome.get("favorable_factors", [])
        if fav:
            lines.append("\nFavorable Factors:")
            for f in fav[:4]:
                lines.append(f"  ✅ {f}")

        unfav = outcome.get("unfavorable_factors", [])
        if unfav:
            lines.append("\nChallenging Factors:")
            for f in unfav[:4]:
                lines.append(f"  ⚠️ {f}")

        victory = outcome.get("victory_indicators", [])
        if victory:
            lines.append("\nVictory Indicators:")
            for v in victory[:3]:
                lines.append(f"  🏆 {v}")

        return "\n".join(lines)

    def _format_duration_analysis(self, additional_data: Dict) -> str:
        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        if not duration:
            return ""

        lines = ["DURATION ANALYSIS:"]
        lines.append(f"• Duration Estimate: {duration.get('duration_estimate', 'MODERATE')}")

        for f in duration.get("delay_factors", [])[:4]:
            lines.append(f"  ⏳ {f}")
        for f in duration.get("speed_factors", [])[:3]:
            lines.append(f"  ⚡ {f}")

        return "\n".join(lines)

    def _format_risks_analysis(self, additional_data: Dict) -> str:
        risks = additional_data.get(f"{DOMAIN_PREFIX}_risks_analysis", {})
        if not risks:
            return ""

        lines = ["RISKS AND PENALTIES ANALYSIS:"]
        lines.append(f"• Risk Level: {risks.get('risk_level', 'LOW')}")
        lines.append(f"• Risk Score: {risks.get('risk_score', 20)}/100")

        for r in risks.get("risks", [])[:4]:
            lines.append(f"  ⚠️ {r}")
        for p in risks.get("protective_factors", [])[:3]:
            lines.append(f"  🛡️ {p}")
        for p in risks.get("precautions", [])[:3]:
            lines.append(f"  📋 {p}")

        return "\n".join(lines)

    def _format_opponent_analysis(self, additional_data: Dict) -> str:
        opponent = additional_data.get(f"{DOMAIN_PREFIX}_opponent_analysis", {})
        if not opponent:
            return ""

        lines = ["OPPONENT ANALYSIS:"]
        lines.append(f"• Opponent Strength: {opponent.get('opponent_strength', 'MODERATE')}")

        for a in opponent.get("your_advantage", [])[:3]:
            lines.append(f"  ✅ {a}")
        for s in opponent.get("strategy_hints", [])[:4]:
            lines.append(f"  📌 {s}")

        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Legal Houses)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")

        legal_houses = {1, 6, 7, 8, 9, 11, 12}
        house_meanings = {
            1: "Self/Ascendant",
            6: "Litigation/Enemies",
            7: "Opponent",
            8: "Hidden/Penalties",
            9: "Justice/Judges",
            11: "Gains/Victory",
            12: "Losses/Expenses",
        }

        for house_num in sorted(house_lords.keys()):
            if house_num not in legal_houses:
                continue
            info = house_lords.get(house_num, {})
            if not info:
                continue

            meaning = house_meanings.get(house_num, "")
            lord        = info.get("lord", "N/A")
            lord_house  = info.get("lord_in_house", "N/A")
            lord_sign   = info.get("lord_in_sign", "N/A")
            dignity     = info.get("lord_dignity", "N/A")
            strength    = info.get("lord_strength_score", 0)

            conditions = []
            if info.get("lord_is_combust"):
                conditions.append("Combust")
            if info.get("lord_is_retrograde"):
                conditions.append("Retrograde")
            cond_str = ", ".join(conditions) if conditions else "Normal"

            strength_label = "✅ STRONG" if strength >= 70 else "○ MODERATE" if strength >= 40 else "⚠️ WEAK"

            lines.append(f"• H{house_num} ({meaning}): Lord {lord} in H{lord_house}/{lord_sign}")
            lines.append(f"  Dignity: {dignity} | Condition: {cond_str} | Strength: {strength}/100 [{strength_label}]")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        lines = ["ASPECTS DATA:"]
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            if benefic or malefic:
                b_str = ", ".join(benefic) if benefic else "None"
                m_str = ", ".join(malefic) if malefic else "None"
                lines.append(f"• H{house_num}: Benefic={b_str} | Malefic={m_str}")

        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # HELPER: Quick getters
    # ==========================================================================
    def _get_outcome_likelihood(self, ad): return (ad or {}).get(f"{DOMAIN_PREFIX}_outcome_analysis", {}).get("outcome_likelihood", "UNCERTAIN")
    def _get_outcome_score(self, ad):      return (ad or {}).get(f"{DOMAIN_PREFIX}_outcome_analysis", {}).get("score", 50)
    def _get_duration_estimate(self, ad):  return (ad or {}).get(f"{DOMAIN_PREFIX}_duration_analysis", {}).get("duration_estimate", "MODERATE")
    def _get_risk_level(self, ad):         return (ad or {}).get(f"{DOMAIN_PREFIX}_risks_analysis", {}).get("risk_level", "LOW")
    def _get_risk_score(self, ad):         return (ad or {}).get(f"{DOMAIN_PREFIX}_risks_analysis", {}).get("risk_score", 20)
    def _get_opponent_strength(self, ad):  return (ad or {}).get(f"{DOMAIN_PREFIX}_opponent_analysis", {}).get("opponent_strength", "MODERATE")
    def _get_case_type(self, ad):          return (ad or {}).get(f"{DOMAIN_PREFIX}_case_type", "civil")

    # ==========================================================================
    # OUTPUT FORMAT BUILDER  (mirrors Career/Finance get_output_format)
    # ==========================================================================
    def get_output_format(
        self,
        language: str,
        has_timing: bool = False,
        is_timing_question: bool = False,
        is_criminal: bool = False,
        is_minor: bool = False,
        prompt_type: str = "general",
    ) -> str:
        """
        Generate output format instructions.
        Produces flowing paragraphs — not bullet dumps.
        Matches the Career/Finance output format philosophy.
        """
        labels = self._get_labels(language)

        lbl_ga  = labels["general_answer"].upper()
        lbl_aa  = labels["astrological_analysis"].upper()
        lbl_sum = labels["summary"].upper()
        lbl_ra  = labels["remedies_astro"].upper()
        lbl_rg  = labels["remedies_general"].upper()
        lbl_tc  = labels["tell_client"]
        vedic   = labels["vedic_starter"]
        minor_note = labels["minor_note"] if is_minor else ""

        # ── TIMING SECTION ────────────────────────────────────────────
        if has_timing:
            timing_section = f"""
**TIMING SECTION (MANDATORY — Include BOTH options):**

🏆 BEST WINDOW (Highest Score):
- Period: [exact dates from timing data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable for case conclusion: [explain dasha lords + legal significations]
- Trade-off: May be further away, but strongest planetary alignment

⏰ NEAREST WINDOW (Soonest):
- Period: [exact dates from timing data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Sooner, not absolute best alignment

👤 GUIDANCE (Help person decide):
Choose BEST window if: Can wait, want maximum favorable alignment
Choose NEAREST window if: Urgent legal deadline, sooner resolution needed

⚠️ If BEST = NEAREST (same window):
"🎯 IDEAL TIMING: The best and nearest windows are the same! Maximum support at earliest opportunity."
"""
        else:
            timing_section = ""

        # ── CRIMINAL EXTRA ────────────────────────────────────────────
        criminal_note = """
⚠️ CRIMINAL CASE — Frame ALL risks as "potential" or "areas of concern"
   NEVER predict imprisonment with certainty.
   Emphasize protective factors strongly.
""" if is_criminal else ""

        # ── MINOR NOTE ────────────────────────────────────────────────
        minor_section = f"""
⚠️ MINOR MODE — Do NOT address this person as the one fighting the case.
   Refer to "the family's legal matter" throughout.
   {minor_note}
""" if is_minor else ""

        # ── MAIN FORMAT ───────────────────────────────────────────────
        return f"""
═══════════════════════════════════════════════════════════
OUTPUT FORMAT (STRICT — FOLLOW EXACTLY)
═══════════════════════════════════════════════════════════

{minor_section}{criminal_note}

**{lbl_ga}:**
Write 3–4 sentences. Answer the question directly in plain language.
No astrological terms here. Mention outcome likelihood + key advice.
Example: "Based on the planetary positions, this case has a moderate-to-favorable outlook.
The fighting ability is strong, though delays are expected through [general time frame].
Engaging an experienced lawyer and acting on the remedies below will strengthen the position."
{f"[{lbl_tc}: ...brief direct statement...]" if not is_minor else ""}

---

**{lbl_aa}:**

Write in FLOWING NARRATIVE PARAGRAPHS — absolutely no bullet dumps.
Every fact must be wrapped in interpretation.

PARAGRAPH 1 — VEDIC OVERVIEW (begin with: "{vedic}"):
Analyse 6th house (fighting capacity) and its lord. Where is the lord placed?
What does that placement mean for this case? Weave planet + sign + house into one sentence of meaning.
Then discuss 9th house (justice) and 11th house (victory/gains). Flow naturally into each other.

PARAGRAPH 2 — OPPONENT AND COMPARISON:
Analyse 7th house (opponent strength) against 6th house (your strength).
Who has the stronger position? What specific advantages does the querent have?
How should they approach the opponent?

PARAGRAPH 3 — DURATION AND SATURN/MERCURY:
How do Saturn (delays/law) and Mercury (documents/lawyers) affect the case?
Is the duration likely short, moderate, or long, and WHY does the chart show this?

PARAGRAPH 4 — RISKS AND PROTECTIVE FACTORS:
Cover 8th house (penalties) and 12th house (losses). Frame criminal risks as "potential concerns".
Then pivot to protective factors — Jupiter, beneficial aspects, remedies that help.

{"PARAGRAPH 5 — TIMING (USE EXACT DATES ABOVE):" + chr(10) + "Interpret the dasha periods in the context of case conclusion. Explain WHY the favorable periods support resolution." if is_timing_question else "PARAGRAPH 5 — PATH FORWARD:" + chr(10) + "Practical steps to improve outcome: documentation, lawyer selection, timing of next steps."}

---

**{lbl_sum}:**
{lbl_tc}: [2–3 sentences. Outcome + Duration + Key recommendation + Lawyer advice.]
Keep it warm, clear, and actionable.

---

**{lbl_ra}:**
Saturn remedies for timely resolution (specific mantra/ritual)
Jupiter remedies for favorable judgment
Mercury remedies for documentation and clear communication
{"Hanuman remedies for courage and protection" if is_criminal else "Mars remedies for fighting strength"}
ALWAYS recommend consulting with a qualified lawyer.

---

**{lbl_rg}:**
Gather and organize all documentation
Engage an experienced {"criminal defense" if is_criminal else "civil/family"} lawyer immediately
{"Consider all legal options including bail and appeal" if is_criminal else "Evaluate settlement options if appropriate"}
Maintain patience — legal timelines are governed by Saturn

{timing_section}
═══════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # MAIN ROUTER
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
        """Main routing method — detects minor, resolves language, routes."""

        try:
            sub_subdomain   = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw             = "\n".join(technical_points) if technical_points else ""

            # ── MINOR DETECTION (global — like Career) ────────────────
            dob      = kwargs.get("dob")
            is_minor = self._detect_minor(dob)
            kwargs["is_minor"] = is_minor

            logger.info(f"[LEGAL] sub_subdomain={sub_subdomain}, language={language}, is_minor={is_minor}")

            case_type = self._get_case_type(additional_data)

            # ── ROUTE ─────────────────────────────────────────────────
            if "Timing" in sub_subdomain or "Conclusion" in sub_subdomain:
                return self._build_timing_prompt(
                    question, additional_data, raw, language, case_type, is_minor, dob)

            elif "Risk" in sub_subdomain or "Dispute" in sub_subdomain:
                return self._build_legal_dispute_prompt(
                    question, additional_data, raw, language, case_type, is_minor, dob)

            elif "Outcome" in sub_subdomain or "Court Case" in sub_subdomain or "criminal" in question.lower():
                return self._build_court_case_prompt(
                    question, additional_data, raw, language, case_type, is_minor, dob)

            else:
                return self._build_general_legal_prompt(
                    question, additional_data, raw, language, case_type, is_minor, dob)

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

You are an expert Vedic astrologer specializing in legal matters.

QUESTION: "{question}"

Provide a helpful analysis in flowing paragraphs (not bullet lists).
Always recommend consulting a qualified lawyer.
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
        case_type: str,
        is_minor: bool,
        dob: str,
    ) -> str:
        """Build prompt for Case Conclusion Timing questions."""

        lang_inst         = self.get_language_instruction(language)
        labels            = self._get_labels(language)
        today_str         = datetime.now().strftime("%B %d, %Y")
        has_timing        = self._has_valid_timing_windows(additional_data)

        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score      = self._get_outcome_score(additional_data)
        duration_estimate  = self._get_duration_estimate(additional_data)

        timing_block   = self._format_timing_windows(additional_data) if not is_minor else ""
        dasha_block    = self._format_current_dasha(additional_data)
        outcome_data   = self._format_outcome_analysis(additional_data)
        duration_data  = self._format_duration_analysis(additional_data)
        lords_data     = self._format_house_lords(additional_data)
        aspects_data   = self._format_house_aspects(additional_data)
        lagna_block    = self._format_lagna_info(additional_data)
        matrix_block   = self._format_legal_matrix(additional_data)
        minor_block    = self._format_minor_block(dob, language) if is_minor else ""

        if has_timing and not is_minor:
            timing_instruction = f"""
═══════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE — USE THESE DATES ONLY
═══════════════════════════════════════════════════════

{timing_block}

{dasha_block}

INSTRUCTIONS:
- Use ONLY the dates provided above
- BEST window = most favorable time for case conclusion
- NEAREST window = soonest likely conclusion
- Mention BOTH windows and explain the trade-off
═══════════════════════════════════════════════════════
"""
        elif is_minor:
            timing_instruction = f"""
═══════════════════════════════════════════════════════
⚠️ MINOR — TIMING INTERPRETED FOR FAMILY GUIDANCE
═══════════════════════════════════════════════════════

{dasha_block}

Interpret dasha periods as awareness for family planning.
Do NOT predict the minor's personal legal actions.
═══════════════════════════════════════════════════════
"""
        else:
            timing_instruction = f"""
═══════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING CALCULATED
═══════════════════════════════════════════════════════

No specific timing windows were calculated.
🚫 DO NOT invent specific dates.
✅ Explain general timeframe from duration analysis.
✅ Recommend monitoring progress with lawyer.

{dasha_block}

MESSAGE: "{labels['timing_unavailable']}"
═══════════════════════════════════════════════════════
"""

        output_format = self.get_output_format(
            language        = language,
            has_timing      = has_timing and not is_minor,
            is_timing_question = True,
            is_criminal     = (case_type == "criminal"),
            is_minor        = is_minor,
            prompt_type     = "timing",
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, case_type, is_timing=True)}

{minor_block}

═══════════════════════════════════════════════════════
QUERY: CASE CONCLUSION TIMING
Current Date: {today_str}
Weightage: Vedic 70% + Dasha 30%
Case Type: {case_type.upper()}
Outcome Likelihood: {outcome_likelihood} ({outcome_score}/100)
Duration Estimate: {duration_estimate}
Has Timing Windows: {'YES' if has_timing else 'NO'}
Is Minor: {'YES' if is_minor else 'NO'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

═══════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════

{outcome_data}

{duration_data}

═══════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════

{lagna_block}

{matrix_block}

{lords_data}

{aspects_data}

{raw}

{output_format}
"""

    # ==========================================================================
    # LEGAL DISPUTE PROMPT
    # ==========================================================================
    def _build_legal_dispute_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        case_type: str,
        is_minor: bool,
        dob: str,
    ) -> str:
        """Build prompt for Legal Dispute Risk questions."""

        lang_inst  = self.get_language_instruction(language)
        labels     = self._get_labels(language)
        today_str  = datetime.now().strftime("%B %d, %Y")

        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score      = self._get_outcome_score(additional_data)
        duration_estimate  = self._get_duration_estimate(additional_data)
        risk_level         = self._get_risk_level(additional_data)
        risk_score         = self._get_risk_score(additional_data)
        opponent_strength  = self._get_opponent_strength(additional_data)

        outcome_data  = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risks_data    = self._format_risks_analysis(additional_data)
        opponent_data = self._format_opponent_analysis(additional_data)
        lords_data    = self._format_house_lords(additional_data)
        aspects_data  = self._format_house_aspects(additional_data)
        lagna_block   = self._format_lagna_info(additional_data)
        matrix_block  = self._format_legal_matrix(additional_data)
        minor_block   = self._format_minor_block(dob, language) if is_minor else ""

        output_format = self.get_output_format(
            language   = language,
            has_timing = False,
            is_criminal = (case_type == "criminal"),
            is_minor   = is_minor,
            prompt_type = "dispute",
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, case_type)}

{minor_block}

═══════════════════════════════════════════════════════
QUERY: LEGAL DISPUTE RISK ANALYSIS
Current Date: {today_str}
Weightage: Vedic 100%
Case Type: {case_type.upper()}
Outcome: {outcome_likelihood} ({outcome_score}/100)
Duration: {duration_estimate}
Risk: {risk_level} ({risk_score}/100)
Opponent: {opponent_strength}
Is Minor: {'YES' if is_minor else 'NO'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════

{outcome_data}

{duration_data}

{risks_data}

{opponent_data}

═══════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════

{lagna_block}

{matrix_block}

{lords_data}

{aspects_data}

{raw}

{output_format}
"""

    # ==========================================================================
    # COURT CASE OUTCOME PROMPT
    # ==========================================================================
    def _build_court_case_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        case_type: str,
        is_minor: bool,
        dob: str,
    ) -> str:
        """Build prompt for Court Case Outcome questions."""

        lang_inst  = self.get_language_instruction(language)
        labels     = self._get_labels(language)
        today_str  = datetime.now().strftime("%B %d, %Y")

        is_criminal = case_type == "criminal" or "criminal" in question.lower()

        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score      = self._get_outcome_score(additional_data)
        duration_estimate  = self._get_duration_estimate(additional_data)
        risk_level         = self._get_risk_level(additional_data)
        risk_score         = self._get_risk_score(additional_data)

        outcome_data  = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risks_data    = self._format_risks_analysis(additional_data)
        lords_data    = self._format_house_lords(additional_data)
        aspects_data  = self._format_house_aspects(additional_data)
        lagna_block   = self._format_lagna_info(additional_data)
        matrix_block  = self._format_legal_matrix(additional_data)
        minor_block   = self._format_minor_block(dob, language) if is_minor else ""

        criminal_warning = ""
        if is_criminal:
            criminal_warning = """
═══════════════════════════════════════════════════════
⚠️ CRIMINAL CASE — EXTRA SENSITIVITY
═══════════════════════════════════════════════════════
- NEVER predict imprisonment with certainty
- Frame risks as "potential areas of concern"
- Focus strongly on protective factors
- STRONGLY recommend criminal defense lawyer
═══════════════════════════════════════════════════════
"""

        output_format = self.get_output_format(
            language    = language,
            has_timing  = False,
            is_criminal = is_criminal,
            is_minor    = is_minor,
            prompt_type = "outcome",
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, case_type)}

{minor_block}

═══════════════════════════════════════════════════════
QUERY: COURT CASE OUTCOME {'(CRIMINAL)' if is_criminal else ''}
Current Date: {today_str}
Weightage: Vedic 100%
Case Type: {case_type.upper()}
Outcome: {outcome_likelihood} ({outcome_score}/100)
Duration: {duration_estimate}
Risk: {risk_level} ({risk_score}/100)
Is Minor: {'YES' if is_minor else 'NO'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{criminal_warning}

═══════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════

{outcome_data}

{duration_data}

{risks_data}

═══════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════

{lagna_block}

{matrix_block}

{lords_data}

{aspects_data}

{raw}

{output_format}
"""

    # ==========================================================================
    # GENERAL LEGAL PROMPT
    # ==========================================================================
    def _build_general_legal_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        case_type: str,
        is_minor: bool,
        dob: str,
    ) -> str:
        """Build general prompt for legal questions."""

        lang_inst  = self.get_language_instruction(language)
        labels     = self._get_labels(language)
        today_str  = datetime.now().strftime("%B %d, %Y")

        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        duration_estimate  = self._get_duration_estimate(additional_data)
        risk_level         = self._get_risk_level(additional_data)

        outcome_data  = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risks_data    = self._format_risks_analysis(additional_data)
        lords_data    = self._format_house_lords(additional_data)
        aspects_data  = self._format_house_aspects(additional_data)
        lagna_block   = self._format_lagna_info(additional_data)
        matrix_block  = self._format_legal_matrix(additional_data)
        minor_block   = self._format_minor_block(dob, language) if is_minor else ""

        output_format = self.get_output_format(
            language    = language,
            has_timing  = False,
            is_criminal = (case_type == "criminal"),
            is_minor    = is_minor,
            prompt_type = "general",
        )

        return f"""
{lang_inst}

{self.build_system_prompt(language, case_type)}

{minor_block}

═══════════════════════════════════════════════════════
QUERY: LEGAL MATTER (General)
Current Date: {today_str}
Weightage: Vedic 100%
Case Type: {case_type.upper()}
Likely Direction: {outcome_likelihood}
Timeframe: {duration_estimate}
Overall Risk: {risk_level}
Is Minor: {'YES' if is_minor else 'NO'}
═══════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════

{outcome_data}

{duration_data}

{risks_data}

{lagna_block}

{matrix_block}

{lords_data}

{aspects_data}

{raw}

{output_format}
"""
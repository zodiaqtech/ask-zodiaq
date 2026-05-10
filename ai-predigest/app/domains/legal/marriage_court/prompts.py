# -*- coding: utf-8 -*-
"""
Marriage Legal Dispute – LLM Prompts v2.0

FIXES FROM v1.0:
✅ MINOR DETECTION - _detect_minor() + _calculate_age_on_date() (from Career v10.0)
✅ DEVELOPMENTAL OVERRIDE - Minors cannot be party to matrimonial litigation
✅ LANGUAGE SYSTEM - Uses base class get_language_instruction() replacing fragile _get_language_instruction_safe()
✅ LAGNA LORD FORMATTING - _format_lagna_lord() added (was entirely missing in v1.0)
✅ TIMING WINDOWS FORMATTING - _format_timing_windows() added (was entirely missing in v1.0)
✅ OUTPUT FORMAT METHOD - get_output_format() added (replaces inline format strings)
✅ MINOR ROUTING IN build_analysis_prompt() - is_minor detected globally and passed via kwargs
✅ MINOR OVERRIDE BLOCKS IN SUB-PROMPTS - developmental_override added to each prompt builder
✅ kwargs FLOW - All sub-prompt methods now accept **kwargs so is_minor flows correctly
✅ REMOVED FRAGILE HELPERS - _get_example_text(), _get_language_instruction_safe(),
   _get_analysis_starters() removed; replaced with proper base-class pattern

DESIGN DECISIONS (UNCHANGED FROM v1.0):
✅ VEDIC-ONLY analysis (NO KP points)
✅ Output language based on user selection
✅ Marriage-specific analysis (7th house focus)
✅ Venus as Kalatra Karaka prominence
✅ Outcome likelihood assessment
✅ Duration guidance
✅ Risk and penalty analysis (alimony, custody, 498A)
✅ Sensitive and empathetic tone for family matters
✅ Professional and balanced guidance

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

Compatible with MarriageLegalDisputeEvaluator v2.0 data structures.
"""

from typing import Dict, List, Optional
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

DOMAIN_PREFIX = "marriage_legal"


class MarriageLegalDisputePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Legal → Marriage Court Case
    v2.0 - Minor logic + language system + lagna + timing windows + output format method
    """

    domain = "Legal"
    subtopic = "Marriage Court Case"

    # ==========================================================================
    # AGE / MINOR UTILITIES  (mirrors CareerDiscoveryAndEmploymentPromptBuilder v10.0)
    # ==========================================================================

    def _calculate_age_on_date(self, dob_str: str, target_date_str: str) -> int:
        """Calculate age on a specific date."""
        dob = datetime.strptime(dob_str, "%d/%m/%Y")
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        return target.year - dob.year - (
            (target.month, target.day) < (dob.month, dob.day)
        )

    def _detect_minor(self, dob: str, dasha_timeline: Dict = None) -> bool:
        """
        Detect if person is currently under 18.
        Minor logic is based on CURRENT age only.

        For marriage legal disputes:
        - Under 18 → cannot be party to matrimonial litigation
        - Frame as hypothetical / future awareness only
        """
        if not dob:
            return False

        today = datetime.now()
        try:
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
        except Exception:
            return False

        current_age = today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )

        return current_age < 18

    # ==========================================================================
    # LANGUAGE INSTRUCTION  (mirrors CareerDiscoveryAndEmploymentPromptBuilder v10.0)
    # ==========================================================================

    def get_language_instruction(self, language: str) -> str:
        """
        Get language instruction for LLM.
        Replaces fragile _get_language_instruction_safe() from v1.0.
        """
        if language.lower() == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, houses, aspects, legal terms).
Example: "आपके विवाह विवाद में **7th house** की स्थिति महत्वपूर्ण है।"
Example: "**Venus** (कलत्र कारक) की स्थिति वैवाहिक मामलों में अनुकूल है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke vivah vivad mein 7th house ki sthiti important hai."
Example: "Venus (Kalatra Karaka) ki position marriage matters mein favorable hai."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear English.
Keep technical terms clear and explain if needed.
"""

    # ==========================================================================
    # SYSTEM PROMPT  (unchanged from v1.0 - kept as-is)
    # ==========================================================================

    def build_system_prompt(self, language: str = "English") -> str:
        """Build system prompt for marriage legal dispute analysis."""

        return f"""You are an expert Vedic astrologer specializing in marriage matters, family disputes, and matrimonial litigation including divorce, dowry cases, alimony, and custody matters.

**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED
   - Do not invent planetary positions not in the data
   - Do not assume aspects not mentioned
   - If data is missing, say so clearly

2. DISTINGUISH FACTS FROM INTERPRETATION
   - Facts = from provided data
   - Interpretation = your astrological reasoning
   - Never present interpretation as computed fact

3. NO GUARANTEES
   - Never guarantee legal victory or defeat
   - Always present as "indications" and "tendencies"
   - Legal outcomes depend on many factors beyond astrology

4. RETROGRADE RULE:
   - Retrograde planets do NOT automatically indicate weakness
   - Retrograde indicates delay, review, or reconsideration
   - Do NOT state that retrograde alone weakens a planet unless evaluator explicitly says so

5. LEGAL DISCLAIMER:
   - Always recommend consulting qualified family lawyer
   - Astrology provides guidance, not legal advice
   - Do not make specific predictions about court decisions

6. ASPECT RULE (CRITICAL):
   - Only mention aspects IF explicitly present in "ASPECTS DATA"
   - If no aspects are listed for a house, state "No explicit planetary aspects indicated"
   - NEVER infer aspects from planet placement alone
   - If an aspect is not explicitly listed in ASPECTS DATA, do NOT mention it even as a possibility

ABSOLUTE ASPECT ENFORCEMENT:
- You are FORBIDDEN from mentioning planetary aspects unless they appear verbatim in ASPECTS DATA
- Do NOT use phrases like "aspecting", "influence on", "casts aspect", or "benefic/malefic aspect"
  unless explicitly listed
- If ASPECTS DATA is empty for a house, you MUST say:
  "No explicit planetary aspects are indicated for this house."

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "7th Lord Venus in 6th house. Debilitated. Weak."
   ✅ "The 7th lord Venus placed in the 6th house indicates that marital matters are
      drawn into a zone of litigation and conflict."

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact → Explain what it means → Connect to practical legal strategy

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

5. PROVIDE BALANCED, EMPATHETIC GUIDANCE
   - Numerical strength scores are CONTEXTUAL indicators
   - Do NOT equate low score with guaranteed loss
   - Always combine strength with dignity, house, and benefic influence

6. SENSITIVITY RULES:
   - Marriage disputes are EMOTIONALLY CHARGED - be empathetic
   - Avoid judgmental language about either party
   - Focus on constructive guidance, not blame
   - If children involved, emphasize their welfare
   - Present risks factually without creating panic
   - Recommend counseling/mediation where appropriate
   - Always suggest professional legal help
   - Avoid suggesting false allegations or domestic violence unless
     explicitly indicated in evaluator risk factors

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR MARRIAGE LEGAL DISPUTES
═══════════════════════════════════════════════════════════════════════════════

- 7th House: MARRIAGE, SPOUSE, PARTNER (PRIMARY HOUSE)
- 1st House: Self, the native, your position in dispute
- 2nd House: Family (kutumb), family wealth, family support
- 4th House: Domestic happiness, home environment
- 5th House: Children, progeny (CUSTODY matters)
- 6th House: Litigation, disputes, enemies, legal battles
- 8th House: In-laws, dowry, hidden matters, inheritance
- 9th House: Justice, legal proceedings, higher courts, dharma
- 11th House: Victory, gains, favorable outcomes
- 12th House: Losses, expenses, separation, bed pleasures

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS) FOR MARRIAGE
═══════════════════════════════════════════════════════════════════════════════

- Venus: KALATRA KARAKA (Spouse Significator) - Most important for marriage
- Jupiter: Husband karaka (for females), dharma, justice, children
- Mars: Aggression, conflict, Manglik dosha, domestic disputes
- Moon: Mind, emotions, mental state during dispute
- Saturn: Delays, separation, karma, legal processes
- Rahu: Unconventional issues, deception, false accusations
- Avoid suggesting false allegations or domestic violence unless explicitly indicated in evaluator risk factors

═══════════════════════════════════════════════════════════════════════════════
                    AGE SAFETY RULE
═══════════════════════════════════════════════════════════════════════════════

If person is under 18:
• NEVER predict or advise on divorce, alimony, or dowry cases
• NEVER discuss matrimonial litigation as applicable to this person NOW
• Frame any analysis as general relationship awareness and future wisdom only
• Redirect toward age-appropriate guidance

═══════════════════════════════════════════════════════════════════════════════
                    ANALYSIS WEIGHTING
═══════════════════════════════════════════════════════════════════════════════

Vedic Analysis → 100% (No KP, No Timing components)
"""

    # ==========================================================================
    # LAGNA LORD FORMATTING  (NEW in v2.0 - was entirely missing in v1.0)
    # mirrors _format_lagna_lord() from CareerDiscoveryAndEmploymentPromptBuilder v10.0
    # ==========================================================================

    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """
        Format lagna lord for marriage legal personality analysis.
        Added in v2.0 - was missing entirely in v1.0.
        """
        # Try lagna_info first, then fall back to house 1 in house_lords_info
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign": info.get("house_sign", "N/A"),
                "lagna_lord": info.get("lord", "N/A"),
                "lagna_lord_house": info.get("lord_in_house"),
                "lagna_lord_sign": info.get("lord_in_sign", "N/A"),
                "lagna_lord_degree": info.get("lord_degree", 0),
                "lagna_lord_dignity": info.get("lord_dignity", "Unknown"),
            }

        if not lagna_info:
            return """
═══════════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════════

CRITICAL: Lagna information not provided.
Do NOT guess or invent lagna sign.
Do NOT mention lagna in your analysis.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════════
"""

        lord = lagna_info.get("lagna_lord", "N/A")
        lagna_sign = lagna_info.get("lagna_sign", "N/A")
        lord_house = lagna_info.get("lagna_lord_house", "N/A")
        lord_sign = lagna_info.get("lagna_lord_sign", "N/A")
        dignity = lagna_info.get("lagna_lord_dignity", "Unknown")
        degree = lagna_info.get("lagna_lord_degree", 0)

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) - NATIVE'S SELF STRENGTH IN DISPUTE")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        if degree:
            lines.append(f"Degree: {degree:.2f}°")
        lines.append("")

        # Dispute personality map (marriage-legal context)
        personality_map = {
            "Sun": {
                "trait": "Authoritative, self-respecting, dignified",
                "dispute_style": "Assertive in proceedings, seeks respect and fair resolution",
                "strength": "Strong sense of justice, commands attention"
            },
            "Moon": {
                "trait": "Emotional, sensitive, family-oriented",
                "dispute_style": "May be emotionally affected; needs strong support system",
                "strength": "Empathetic, good at presenting emotional impact"
            },
            "Mars": {
                "trait": "Assertive, combative, direct",
                "dispute_style": "Aggressive in litigation, willing to fight hard",
                "strength": "Determined, does not back down easily"
            },
            "Mercury": {
                "trait": "Analytical, communicative, logical",
                "dispute_style": "Strong in documentation, negotiation, and legal arguments",
                "strength": "Clear thinking, good with evidence and paperwork"
            },
            "Jupiter": {
                "trait": "Ethical, dharmic, wisdom-seeking",
                "dispute_style": "Seeks fair and just resolution, morally driven",
                "strength": "Court often favors those with Jupiter's grace"
            },
            "Venus": {
                "trait": "Diplomatic, compromise-seeking",
                "dispute_style": "May prefer settlement; values peace over prolonged battle",
                "strength": "Strong for mediation and amicable resolution"
            },
            "Saturn": {
                "trait": "Patient, disciplined, resilient",
                "dispute_style": "Prepared for long legal battles, does not give up",
                "strength": "Endurance; gains through persistence over time"
            },
            "Rahu": {
                "trait": "Unconventional, ambitious, strategic",
                "dispute_style": "May use unconventional tactics; unpredictable approach",
                "strength": "Adaptable; can surprise opponent"
            },
            "Ketu": {
                "trait": "Detached, spiritual, introspective",
                "dispute_style": "May not fight aggressively; inclined to withdrawal",
                "strength": "Clarity and detachment can prevent emotional mistakes"
            }
        }

        lord_info = personality_map.get(lord, {
            "trait": "Unique disposition",
            "dispute_style": "Individual approach to dispute",
            "strength": "Depends on specific chart factors"
        })

        lines.append(f"Native's Disposition: {lord_info['trait']}")
        lines.append(f"Dispute Style: {lord_info['dispute_style']}")
        lines.append(f"Inherent Strength: {lord_info['strength']}")
        lines.append("")
        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows the native's fundamental strength in the dispute")
        lines.append("• Compare with 7th lord to assess relative strength vs opponent")
        lines.append("• ONE lagna only - do NOT mention alternate lagnas")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ==========================================================================
    # TIMING WINDOWS FORMATTING  (NEW in v2.0 - was entirely missing in v1.0)
    # mirrors _format_timing_windows() from ProspectsOfInvestmentsPromptBuilder v7.0
    # ==========================================================================

    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows for LLM.
        Added in v2.0 - was missing entirely in v1.0.
        """
        if not timing_windows_data or not timing_windows_data.get("has_timing"):
            return ""

        try:
            best = timing_windows_data.get("best_window")
            nearest = timing_windows_data.get("nearest_window")
            all_windows = timing_windows_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════════"]
            lines.append("⭐ TIMING WINDOWS ANALYSIS (Favorable Dasha Periods)")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Two timing options are provided below.")
            lines.append("ALWAYS mention BOTH in your analysis and explain the trade-off.")
            lines.append("")

            # BEST WINDOW
            if best:
                lines.append("🏆 BEST WINDOW (Highest Astrological Score):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                age = best.get("age_at_start")
                if age:
                    lines.append(f"  Age: {age} years")
                lines.append("")
                lines.append("  Why this is BEST:")
                score_maha = best.get("score_maha", 0)
                score_antara = best.get("score_antara", 0)
                score_paryantar = best.get("score_paryantar", 0)
                if score_maha or score_antara or score_paryantar:
                    lines.append(f"    - Maha Dasha score: {score_maha}/10")
                    lines.append(f"    - Antara Dasha score: {score_antara}/10")
                    lines.append(f"    - Pratyantar Dasha score: {score_paryantar}/10")
                transit = best.get("transit_score", 0)
                if transit:
                    lines.append(f"    - Transit support: {transit:.1f}%")
                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest alignment")
                lines.append("")

            # NEAREST WINDOW
            if nearest:
                lines.append("⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                age = nearest.get("age_at_start")
                if age:
                    lines.append(f"  Age: {age} years")
                lines.append("")

                # Check if best and nearest are the same
                if best and (
                    best.get("dasha") == nearest.get("dasha")
                    and best.get("start") == nearest.get("start")
                ):
                    lines.append("  ✅ LUCKY! Best and Nearest windows are THE SAME!")
                    lines.append("     You get both optimal timing AND early opportunity!")
                else:
                    lines.append("  Trade-off: Sooner opportunity, but not the absolute best alignment")
                lines.append("")

            # Alternative windows
            if len(all_windows) > 1:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Top 5 for reference):")
                lines.append("-" * 60)
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

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS FOR TIMING ANALYSIS:")
            lines.append("- MUST mention BOTH best and nearest windows")
            lines.append("- Explain WHY each window is favorable for the legal matter")
            lines.append("- Let user choose: Wait for best OR Act sooner")
            lines.append("- Use exact dates provided above")
            lines.append("- If best = nearest, emphasize this is ideal timing")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ==========================================================================
    # OUTPUT FORMAT METHOD  (NEW in v2.0 - replaces inline format strings in v1.0)
    # mirrors get_output_format() from CareerDiscoveryAndEmploymentPromptBuilder v10.0
    # ==========================================================================

    def get_output_format(
        self,
        has_timing: bool = False,
        is_minor: bool = False,
        question_type: str = "general"
    ) -> str:
        """
        Generate output format instructions.
        Added in v2.0 - replaces fragile inline example-text approach from v1.0.
        """

        timing_section = ""
        if has_timing and not is_minor:
            timing_section = """
**E. TIMING RECOMMENDATION (CRITICAL):**

⚠️ MANDATORY: Include BOTH timing options below.

**🏆 BEST WINDOW (Highest Astrological Score):**
- Period: [exact dates from timing data]
- Dasha: [exact dasha from timing data]
- Score: [X]/100
- Why favorable: [explain dasha lords + marriage case significations]
- Trade-off: May be further in future

**⏰ NEAREST WINDOW (Soonest Opportunity):**
- Period: [exact dates from timing data]
- Dasha: [exact dasha from timing data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Not absolute best alignment

**👤 RECOMMENDATION (Help user decide):**
Choose BEST if: Can wait for strongest planetary support
Choose NEAREST if: Urgent case timelines require action sooner

⚠️ If BEST = NEAREST (same window):
"🎯 IDEAL! Best and earliest opportunity are the SAME window!"
"""

        minor_override = ""
        if is_minor:
            minor_override = """
⚠️ MINOR DETECTED — MANDATORY OVERRIDE:
Do NOT analyze or predict marriage legal outcomes for this person.
They are under 18 and cannot be a party to matrimonial litigation.
Provide ONLY general relationship wisdom and future awareness.
Tone must be developmental and age-appropriate.
"""

        return f"""
OUTPUT FORMAT (STRICT — FOLLOW EXACTLY):

{minor_override}

**GENERAL_ANSWER:**
<Clear, empathetic answer in plain language. NO astrological jargon.>
<3-4 lines only. Be compassionate and practical.>

**ASTROLOGICAL_ANALYSIS:**

Write in FLOWING PARAGRAPHS (not bullet points):

**PARAGRAPH 1 – 7th HOUSE (Primary Marriage House):**
Begin with: "According to Vedic astrology, the 7th house..."
- 7th lord placement, dignity, strength
- What this means for the marriage dispute

**PARAGRAPH 2 – VENUS (Kalatra Karaka):**
- Venus as spouse significator
- Venus sign, house, strength
- Settlement vs conflict tendency

**PARAGRAPH 3 – LAGNA LORD (Self Strength):**
- 1st lord (native's position) vs 7th lord (opponent)
- Relative strength comparison
- Who has the advantage

**PARAGRAPH 4 – LITIGATION & JUSTICE (6th, 9th, 11th):**
- 6th house: litigation ability
- 9th house: justice and dharma
- 11th house: victory potential

**PARAGRAPH 5 – RISK ASSESSMENT (8th, 12th Houses):**
- 8th house: in-laws, dowry, hidden issues
- 12th house: losses, alimony, separation
- 5th house if custody is relevant
- Avoid suggesting DV/498A unless explicitly in evaluator risk_factors

**PARAGRAPH 6 – DURATION:**
- Saturn's influence (delay karaka)
- Retrograde planets
- Settlement possibility based on Venus strength

**PARAGRAPH 7 – STRATEGY:**
- When to fight vs when to settle
- Key protective steps
- Practical guidance

{timing_section}

**SUMMARY:**
TELL CLIENT: "[Marriage situation + Outcome + Duration + Primary recommendation]"
(2-3 lines only)

**REMEDIES_ASTROLOGICAL:**
- Maximum 2-3 remedies linked to MOST AFFECTED planet
- Specify which planet, which remedy, why

**REMEDIES_GENERAL:**
- Consult qualified family lawyer immediately
- Document all communications
- Seek emotional support/counseling
- Maintain dignity throughout proceedings
"""

    # ==========================================================================
    # DATA HELPER METHODS  (unchanged from v1.0)
    # ==========================================================================

    def _get_marriage_situation(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        return marriage.get("marriage_situation", "MODERATE")

    def _get_marriage_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        return marriage.get("marriage_score", 50)

    def _get_seventh_house_strength(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        return marriage.get("seventh_house_strength", "MODERATE")

    def _get_venus_strength(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        return marriage.get("venus_strength", "MODERATE")

    def _get_dispute_type_indicators(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        return marriage.get("dispute_type_indicators", [])

    def _get_outcome_likelihood(self, additional_data: Dict) -> str:
        if not additional_data:
            return "UNCERTAIN"
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        return outcome.get("likelihood", "UNCERTAIN")

    def _get_outcome_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        return outcome.get("score", 50)

    def _get_duration_category(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        return duration.get("duration_category", "MODERATE")

    def _get_risk_level(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("risk_level", "MODERATE")

    def _get_risk_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("risk_score", 50)

    def _get_areas_of_concern(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("areas_of_concern", [])

    # ==========================================================================
    # DATA FORMATTING METHODS  (unchanged from v1.0 - kept exactly as-is)
    # ==========================================================================

    def _format_marriage_analysis(self, additional_data: Dict) -> str:
        """Format marriage-specific analysis for prompt."""
        if not additional_data:
            return ""
        marriage = additional_data.get(f"{DOMAIN_PREFIX}_marriage_analysis", {})
        if not marriage:
            return ""
        lines = ["MARRIAGE ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Marriage Situation: {marriage.get('marriage_situation', 'MODERATE')}")
        lines.append(f"• Marriage Score: {marriage.get('marriage_score', 50)}/100")
        lines.append(f"• 7th House Strength: {marriage.get('seventh_house_strength', 'MODERATE')}")
        lines.append(f"• Venus (Kalatra Karaka): {marriage.get('venus_strength', 'MODERATE')}")
        dispute_types = marriage.get("dispute_type_indicators", [])
        if dispute_types:
            lines.append(f"• Dispute Type Indicators: {', '.join(dispute_types)}")
        favorable = marriage.get("favorable_factors", [])
        if favorable:
            lines.append("")
            lines.append("Marriage Favorable Factors:")
            for f in favorable[:4]:
                lines.append(f"  ✅ {f}")
        unfavorable = marriage.get("unfavorable_factors", [])
        if unfavorable:
            lines.append("")
            lines.append("Marriage Challenging Factors:")
            for f in unfavorable[:4]:
                lines.append(f"  ⚠️ {f}")
        hints = marriage.get("marriage_hints", [])
        if hints:
            lines.append("")
            lines.append("Marriage Hints:")
            for h in hints[:3]:
                lines.append(f"  💒 {h}")
        return "\n".join(lines)

    def _format_outcome_analysis(self, additional_data: Dict) -> str:
        """Format outcome analysis for prompt."""
        if not additional_data:
            return ""
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        if not outcome:
            return ""
        lines = ["OUTCOME ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Likelihood: {outcome.get('likelihood', 'UNCERTAIN')}")
        lines.append(f"• Score: {outcome.get('score', 50)}/100")
        favorable = outcome.get("favorable_factors", [])
        if favorable:
            lines.append("")
            lines.append("Favorable Factors:")
            for f in favorable[:4]:
                lines.append(f"  ✅ {f}")
        unfavorable = outcome.get("unfavorable_factors", [])
        if unfavorable:
            lines.append("")
            lines.append("Challenging Factors:")
            for f in unfavorable[:4]:
                lines.append(f"  ⚠️ {f}")
        strategic = outcome.get("strategic_hints", [])
        if strategic:
            lines.append("")
            lines.append("Strategic Hints:")
            for h in strategic[:3]:
                lines.append(f"  💡 {h}")
        return "\n".join(lines)

    def _format_duration_analysis(self, additional_data: Dict) -> str:
        """Format duration analysis for prompt."""
        if not additional_data:
            return ""
        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        if not duration:
            return ""
        lines = ["DURATION ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Category: {duration.get('duration_category', 'MODERATE')}")
        lines.append(f"• Score: {duration.get('duration_score', 50)}/100 (higher = longer)")
        delay_factors = duration.get("delay_factors", [])
        if delay_factors:
            lines.append("")
            lines.append("Delay Factors:")
            for f in delay_factors[:3]:
                lines.append(f"  ⏳ {f}")
        speed_factors = duration.get("speed_factors", [])
        if speed_factors:
            lines.append("")
            lines.append("Speed Factors:")
            for f in speed_factors[:3]:
                lines.append(f"  ⚡ {f}")
        hints = duration.get("duration_hints", [])
        if hints:
            lines.append("")
            lines.append("Duration Hints:")
            for h in hints[:2]:
                lines.append(f"  📅 {h}")
        return "\n".join(lines)

    def _format_risk_analysis(self, additional_data: Dict) -> str:
        """Format risk analysis for prompt."""
        if not additional_data:
            return ""
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        if not risk:
            return ""
        lines = ["RISK & PENALTY ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Risk Level: {risk.get('risk_level', 'MODERATE')}")
        lines.append(f"• Risk Score: {risk.get('risk_score', 50)}/100")
        risk_factors = risk.get("risk_factors", [])
        if risk_factors:
            lines.append("")
            lines.append("Risk Factors:")
            for f in risk_factors[:4]:
                lines.append(f"  🚨 {f}")
        penalties = risk.get("penalty_indicators", [])
        if penalties:
            lines.append("")
            lines.append("Penalty Indicators:")
            for p in penalties[:3]:
                lines.append(f"  💰 {p}")
        concerns = risk.get("areas_of_concern", [])
        if concerns:
            lines.append("")
            lines.append("Areas of Concern:")
            for c in concerns[:4]:
                lines.append(f"  ⚠️ {c}")
        mitigation = risk.get("mitigation_hints", [])
        if mitigation:
            lines.append("")
            lines.append("Mitigation Hints:")
            for m in mitigation[:3]:
                lines.append(f"  🛡️ {m}")
        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely."""
        if not additional_data:
            return ""
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        lines = ["HOUSE LORDS DATA:"]
        marriage_houses = {1, 2, 4, 5, 6, 7, 8, 9, 11, 12}
        for house_num in sorted(house_lords.keys()):
            if house_num not in marriage_houses:
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
            prefix = "★" if house_num == 7 else "•"
            lines.append(
                f"{prefix} H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | "
                f"{dignity} | {condition_str} | Str:{strength}/100 | Planets:{planets}"
            )
        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        """Format aspects data concisely."""
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
                benefic_str = ", ".join(benefic) if benefic else "None"
                malefic_str = ", ".join(malefic) if malefic else "None"
                prefix = "★" if house_num == 7 else "•"
                lines.append(f"{prefix} H{house_num}: Benefic={benefic_str} | Malefic={malefic_str}")
        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # MINOR OVERRIDE BLOCK HELPER  (NEW in v2.0)
    # mirrors developmental_override pattern from CareerDiscoveryAndEmploymentPromptBuilder v10.0
    # ==========================================================================

    def _get_minor_override_block(self, dob: str) -> str:
        """
        Generate mandatory override block when person is under 18.
        Marriage legal disputes cannot apply to minors.
        Mirrors developmental_override from Career builder v10.0.
        """
        return f"""
═══════════════════════════════════════════════════════════
🚨 MINOR DETECTED — MANDATORY DEVELOPMENTAL OVERRIDE
═══════════════════════════════════════════════════════════

Person DOB: {dob}
Status: Under 18 years old

STRICT RULES (cannot be bypassed):
• Do NOT analyze or predict divorce, alimony, or dowry cases
• Do NOT discuss matrimonial litigation as applicable NOW
• Do NOT mention custody battles or 498A concerns
• Do NOT provide any matrimonial legal outcome predictions
• Do NOT use timing windows for any legal event predictions

ALLOWED APPROACH:
• Acknowledge the question is not applicable at this age
• Reframe as general future awareness about relationship patterns
• Discuss natal chart indicators for long-term relationship harmony (general only)
• Encourage education, personal development, and maturity
• Provide age-appropriate and constructive guidance

TONE:
• Gentle, supportive, and age-appropriate
• Focused on future potential and wisdom
• No alarming or doom-oriented language
• Redirect toward constructive life guidance
═══════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # MAIN ROUTING METHOD  (UPDATED in v2.0 - adds minor detection + kwargs flow)
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
        v2.0: Adds global minor detection (mirrors Career builder v10.0).
        All sub-prompt methods now receive **kwargs so is_minor flows correctly.
        """
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            # ──────────────────────────────────────────────────────────
            # GLOBAL MINOR DETECTION  (NEW in v2.0)
            # mirrors exact pattern from CareerDiscoveryAndEmploymentPromptBuilder v10.0
            # ──────────────────────────────────────────────────────────
            dob = kwargs.get("dob")
            dasha_timeline = kwargs.get("dasha_timeline")

            is_minor = self._detect_minor(dob, dasha_timeline)
            kwargs["is_minor"] = is_minor

            logger.info(
                f"[MarriageLegal] Minor Detection → DOB: {dob}, Is Minor: {is_minor}"
            )
            logger.info(
                f"Building prompt for sub_subdomain: '{sub_subdomain}', language: {language}"
            )

            question_lower = question.lower()

            # Route based on sub_subdomain or question keywords
            if "Outcome" in sub_subdomain or "result" in question_lower:
                return self._build_outcome_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            elif (
                "Duration" in sub_subdomain
                or "Timeline" in sub_subdomain
                or "time" in question_lower
            ):
                return self._build_duration_prompt(
                    question, additional_data, raw, language, **kwargs
                )
            elif (
                "Risk" in sub_subdomain
                or "Penalty" in sub_subdomain
                or "alimony" in question_lower
                or "custody" in question_lower
            ):
                return self._build_risk_prompt(
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
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # FALLBACK PROMPT  (UPDATED in v2.0 - uses get_language_instruction())
    # ==========================================================================

    def _build_fallback_prompt(self, question: str, language: str) -> str:
        """Fallback prompt if something fails."""
        lang_inst = self.get_language_instruction(language)  # v2.0: uses base-class method

        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in marriage matters and family court disputes.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
Focus on 7th house (marriage) and Venus (Kalatra Karaka).
Be empathetic - marriage disputes are emotionally challenging.
Include practical strategic guidance.
End with a clear actionable statement.
Always recommend consulting qualified family lawyer.
"""

    # ==========================================================================
    # GENERAL PROMPT  (UPDATED in v2.0)
    # Changes: get_language_instruction(), lagna block, timing block,
    #          minor override block, kwargs accepted, get_output_format()
    # ==========================================================================

    def _build_general_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs  # v2.0: accepts **kwargs so is_minor flows in
    ) -> str:
        """Build prompt for general marriage legal dispute questions."""

        lang_inst = self.get_language_instruction(language)  # v2.0: base-class method
        today_str = datetime.now().strftime("%B %d, %Y")

        # v2.0: Read is_minor from kwargs (set by build_analysis_prompt)
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob", "Unknown")

        # Evaluator data
        marriage_situation = self._get_marriage_situation(additional_data)
        marriage_score = self._get_marriage_score(additional_data)
        seventh_house_strength = self._get_seventh_house_strength(additional_data)
        venus_strength = self._get_venus_strength(additional_data)
        dispute_types = self._get_dispute_type_indicators(additional_data)
        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score = self._get_outcome_score(additional_data)
        duration_category = self._get_duration_category(additional_data)
        risk_level = self._get_risk_level(additional_data)
        risk_score = self._get_risk_score(additional_data)
        areas_of_concern = self._get_areas_of_concern(additional_data)

        # Format data blocks
        marriage_data = self._format_marriage_analysis(additional_data)
        outcome_data = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risk_data = self._format_risk_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)

        # v2.0: Lagna formatting (new)
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)

        # v2.0: Timing windows (new)
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        timing_formatted = (
            self._format_timing_windows(timing_windows_data)
            if has_timing and not is_minor
            else ""
        )

        # v2.0: Minor override block (new)
        minor_override = self._get_minor_override_block(dob) if is_minor else ""

        # Existing risk warning logic (kept from v1.0)
        is_high_risk = risk_level in ["HIGH", "VERY_HIGH"]
        has_custody_concern = "custody" in " ".join(areas_of_concern).lower() if areas_of_concern else False
        has_dv_concern = any(
            x in " ".join(areas_of_concern).lower()
            for x in ["dv", "498", "violence", "allegations"]
        ) if areas_of_concern else False

        risk_warning = ""
        if is_high_risk and not is_minor:
            risk_warning = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ HIGH RISK INDICATORS DETECTED
═══════════════════════════════════════════════════════════════════════════════
{"- CUSTODY concerns identified - prioritize children's welfare" if has_custody_concern else ""}
{"- Potential DV/498A concerns - document everything carefully" if has_dv_concern else ""}
- Seek experienced family lawyer IMMEDIATELY
- Provide risk mitigation strategies
- Be empathetic but factually clear about risks
═══════════════════════════════════════════════════════════════════════════════
"""

        dispute_types_str = ", ".join(dispute_types) if dispute_types else "General marriage dispute"

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE LEGAL DISPUTE ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Marriage Situation: {marriage_situation} ({marriage_score}/100)
7th House Strength: {seventh_house_strength}
Venus (Kalatra Karaka): {venus_strength}
Dispute Indicators: {dispute_types_str}
Outcome Likelihood: {outcome_likelihood} ({outcome_score}/100)
Expected Duration: {duration_category}
Risk Level: {risk_level} ({risk_score}/100)
Areas of Concern: {', '.join(areas_of_concern) if areas_of_concern else 'None identified'}
Timing Windows Available: {'YES' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

{risk_warning}

{timing_formatted}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{marriage_data}

{outcome_data}

{duration_data}

{risk_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_formatted}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
SPECIFIC GUIDANCE:
═══════════════════════════════════════════════════════════════════════════════

{"⚠️ MINOR: Do NOT predict matrimonial outcomes. Reframe as future awareness only." if is_minor else f'''
• 7th house is PRIMARY - lead analysis here
• Compare 1st lord (native) vs 7th lord (opponent) strength
• Venus (Kalatra Karaka) is the most important karaka
• {"CUSTODY: 5th house analysis is critical" if has_custody_concern else ""}
• {"HIGH RISK: Document all interactions carefully" if is_high_risk else ""}
• Avoid suggesting DV/498A unless explicitly in evaluator risk_factors
• Recommend mediation if Venus is strong (settlement indicator)
• Always recommend professional family lawyer
'''}

{self.get_output_format(has_timing and not is_minor, is_minor, "general")}
"""

    # ==========================================================================
    # OUTCOME PROMPT  (UPDATED in v2.0)
    # ==========================================================================

    def _build_outcome_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs  # v2.0: accepts **kwargs
    ) -> str:
        """Build prompt for outcome-focused questions."""

        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob", "Unknown")

        marriage_situation = self._get_marriage_situation(additional_data)
        seventh_house_strength = self._get_seventh_house_strength(additional_data)
        venus_strength = self._get_venus_strength(additional_data)
        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score = self._get_outcome_score(additional_data)

        marriage_data = self._format_marriage_analysis(additional_data)
        outcome_data = self._format_outcome_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)

        # v2.0: lagna + timing
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        timing_formatted = (
            self._format_timing_windows(timing_windows_data)
            if has_timing and not is_minor
            else ""
        )

        # v2.0: minor override
        minor_override = self._get_minor_override_block(dob) if is_minor else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE DISPUTE OUTCOME ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Marriage Situation: {marriage_situation}
7th House Strength: {seventh_house_strength}
Venus (Kalatra Karaka): {venus_strength}
Outcome Likelihood: {outcome_likelihood} ({outcome_score}/100)
Timing Windows Available: {'YES' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

{timing_formatted}

═══════════════════════════════════════════════════════════════════════════════
MARRIAGE & OUTCOME ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{marriage_data}

{outcome_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lagna_formatted}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
SPECIFIC GUIDANCE FOR OUTCOME ANALYSIS:
═══════════════════════════════════════════════════════════════════════════════

{"⚠️ MINOR: Do NOT predict matrimonial litigation outcomes." if is_minor else '''
- Outcome depends on 1st vs 7th lord relative strength
- 6th house = litigation ability; 9th + 11th = justice and victory
- Jupiter's aspect is a protective factor
- Be balanced - do NOT promise victory or defeat
- Recommend mediation if Venus is strong
- Always recommend professional family lawyer
'''}

{self.get_output_format(has_timing and not is_minor, is_minor, "outcome")}
"""

    # ==========================================================================
    # DURATION PROMPT  (UPDATED in v2.0)
    # ==========================================================================

    def _build_duration_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs  # v2.0: accepts **kwargs
    ) -> str:
        """Build prompt for duration/timeline questions."""

        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob", "Unknown")

        duration_category = self._get_duration_category(additional_data)
        venus_strength = self._get_venus_strength(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)

        # v2.0: lagna + timing
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        timing_formatted = (
            self._format_timing_windows(timing_windows_data)
            if has_timing and not is_minor
            else ""
        )

        # v2.0: minor override
        minor_override = self._get_minor_override_block(dob) if is_minor else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE CASE DURATION ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Duration Category: {duration_category}
Venus Strength: {venus_strength} (settlement indicator)
Timing Windows Available: {'YES' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

{timing_formatted}

═══════════════════════════════════════════════════════════════════════════════
⚠️ FAMILY COURT TIMING NOTE:
═══════════════════════════════════════════════════════════════════════════════
Family court cases can vary significantly:
- Mutual consent divorce: 6-18 months
- Contested divorce: 2-5+ years
- Custody battles: Often prolonged
- Settlement can significantly reduce timeline
Venus strength often indicates settlement possibility.
═══════════════════════════════════════════════════════════════════════════════

{duration_data}

{lagna_formatted}

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

{"⚠️ MINOR: Do NOT predict duration of matrimonial proceedings." if is_minor else ""}

{self.get_output_format(has_timing and not is_minor, is_minor, "duration")}
"""

    # ==========================================================================
    # RISK PROMPT  (UPDATED in v2.0)
    # ==========================================================================

    def _build_risk_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs  # v2.0: accepts **kwargs
    ) -> str:
        """Build prompt for risk, alimony, custody, and penalty questions."""

        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob", "Unknown")

        marriage_situation = self._get_marriage_situation(additional_data)
        risk_level = self._get_risk_level(additional_data)
        risk_score = self._get_risk_score(additional_data)
        areas_of_concern = self._get_areas_of_concern(additional_data)

        marriage_data = self._format_marriage_analysis(additional_data)
        risk_data = self._format_risk_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)

        # v2.0: lagna + timing
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        timing_formatted = (
            self._format_timing_windows(timing_windows_data)
            if has_timing and not is_minor
            else ""
        )

        # v2.0: minor override
        minor_override = self._get_minor_override_block(dob) if is_minor else ""

        # Specific concern flags (kept from v1.0)
        has_custody_concern = "custody" in " ".join(areas_of_concern).lower() if areas_of_concern else False
        has_alimony_concern = any(
            x in " ".join(areas_of_concern).lower()
            for x in ["alimony", "maintenance", "financial"]
        ) if areas_of_concern else False
        has_dv_concern = any(
            x in " ".join(areas_of_concern).lower()
            for x in ["dv", "498", "violence", "allegations"]
        ) if areas_of_concern else False

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE DISPUTE RISK & PENALTY ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Marriage Situation: {marriage_situation}
Risk Level: {risk_level} ({risk_score}/100)
Areas of Concern: {', '.join(areas_of_concern) if areas_of_concern else 'None identified'}
Timing Windows Available: {'YES' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY NOTE - MARRIAGE DISPUTE RISKS:
═══════════════════════════════════════════════════════════════════════════════
- Marriage disputes involve deep emotions - be empathetic
- Present risks factually without causing panic
- Always provide mitigation strategies
{"- CUSTODY: Children's welfare is paramount" if has_custody_concern else ""}
{"- FINANCIAL: Alimony/maintenance considerations present" if has_alimony_concern else ""}
{"- ALLEGATIONS: Document everything carefully" if has_dv_concern else ""}
- Strongly recommend professional legal counsel
- Suggest counseling for emotional support
- Avoid suggesting DV/498A unless explicitly in evaluator risk_factors
═══════════════════════════════════════════════════════════════════════════════

{timing_formatted}

{marriage_data}

{risk_data}

{lagna_formatted}

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

{"⚠️ MINOR: Do NOT predict alimony, custody, or legal risk outcomes." if is_minor else ""}

{self.get_output_format(has_timing and not is_minor, is_minor, "risk")}
"""

    # ==========================================================================
    # REMEDIES PROMPT  (UPDATED in v2.0)
    # ==========================================================================

    def _build_remedies_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        **kwargs  # v2.0: accepts **kwargs
    ) -> str:
        """Build prompt for remedies questions."""

        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob", "Unknown")

        marriage_situation = self._get_marriage_situation(additional_data)
        seventh_house_strength = self._get_seventh_house_strength(additional_data)
        venus_strength = self._get_venus_strength(additional_data)
        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        risk_level = self._get_risk_level(additional_data)

        lords_data = self._format_house_lords(additional_data)

        # v2.0: lagna
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)

        # v2.0: minor override (for remedies, minor can receive general spiritual guidance)
        minor_override = self._get_minor_override_block(dob) if is_minor else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REMEDIES FOR MARRIAGE DISPUTE SUCCESS
Current Date: {today_str}
Weightage: VEDIC 100%
Marriage Situation: {marriage_situation}
7th House Strength: {seventh_house_strength}
Venus (Kalatra Karaka): {venus_strength}
Outcome Likelihood: {outcome_likelihood}
Risk Level: {risk_level}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

{lagna_formatted}

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR MARRIAGE DISPUTES:
═══════════════════════════════════════════════════════════════════════════════

- Recommend MAXIMUM 2-3 astrological remedies
- Choose remedies linked to the MOST AFFECTED planet only

7th LORD WEAK: Strengthen for marriage matters
VENUS WEAK (Kalatra Karaka): Friday fasts, Lakshmi worship
JUPITER WEAK: Thursday fasts, Vishnu worship for dharma/justice
MARS AFFLICTING 7th: Hanuman worship, Tuesday fasts
SATURN CAUSING DELAYS: Saturday fasts, Shani puja
RAHU IN 7th: Rahu remedies, Durga worship for protection

Traditional Remedies for Marriage Peace & Legal Success:
- Gauri-Shankar Puja for marital harmony
- Swayamvara Parvathi Mantra for relationship matters
- Baglamukhi Puja for victory in disputes
- Hanuman Chalisa for protection and strength
- Santoshi Mata worship for family peace

{"⚠️ MINOR: Provide ONLY general spiritual/emotional wellbeing remedies. No matrimonial litigation remedies." if is_minor else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
What astrological challenges exist in marriage matters and how remedies can help.
(2-3 lines only, empathetic tone)

ASTROLOGICAL_ANALYSIS:

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin with: "According to Vedic astrology,"
- Identify weak planets affecting marriage dispute
- 7th lord condition, Venus condition
- Main astrological challenges

PARAGRAPH 2 – PRIMARY REMEDY (Marriage/7th House):
Most important remedy for marriage matters and WHY it will help.
Detailed instructions for 7th house or Venus remedy.

PARAGRAPH 3 – JUSTICE & PROTECTION REMEDY:
Jupiter remedies for dharma and favorable legal outcome.
Protection remedies only if explicitly indicated in evaluator data.
Avoid suggesting false allegations or domestic violence unless explicitly indicated in evaluator risk factors.

PARAGRAPH 4 – EMOTIONAL HEALING REMEDY:
Moon remedies for emotional stability during difficult time.
Meditation and spiritual practices.

PARAGRAPH 5 – TIMING OF REMEDIES:
- Best days to start (Friday for Venus, Thursday for Jupiter)
- Duration of practice
- Expected effects

SUMMARY:
TELL CLIENT: "[Priority remedy + Practice schedule + Expected benefit for marriage case]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
1. [Venus/7th house remedy with detailed instructions]
2. [Jupiter remedy for justice if needed]
3. [Protection remedy if aggression indicated]

REMEDIES_GENERAL:
- Consult qualified family lawyer FIRST
- Seek emotional counseling/support
- Practice patience and maintain dignity
- Focus on peaceful resolution if possible
- Protect children from conflict if applicable
- Avoid negative talk about spouse publicly
"""
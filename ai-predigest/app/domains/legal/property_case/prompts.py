"""
Property Legal Dispute – LLM Prompts v2.0

ENHANCEMENTS FROM v1.0:
✅ Minor detection logic (matches Career evaluator pattern)
✅ Timing windows support (BEST + NEAREST windows)
✅ Lagna info formatting (from evaluator v2.0 lagna_info)
✅ Property suitability matrix formatting
✅ Improved answer flow (no bullet dumps, flowing paragraphs)
✅ Dasha context formatting (current_dasha + dasha_timeline)
✅ Language-safe section headers (English always, content in selected language)
✅ Strategic framing for minor: developmental mode
✅ Full parity with Career/Finance prompt builder patterns

Weightage:
- Vedic Analysis: 100% (no KP in this domain)
- Timing: BEST + NEAREST windows shown only when is_timing_query

Compatible with PropertyLegalDisputeEvaluator v2.0:
- property_legal_property_analysis
- property_legal_outcome_analysis
- property_legal_duration_analysis
- property_legal_risk_analysis
- property_legal_suitability_matrix  (NEW in v2.0)
- property_legal_timing_windows      (NEW in v2.0)
- property_legal_house_lords
- property_legal_house_aspects
- lagna_info                         (NEW in v2.0)
- property_legal_current_dasha
- property_legal_dasha_timeline
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

DOMAIN_PREFIX = "property_legal"


class PropertyLegalDisputePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Legal → Property Case
    v2.0 - Full feature parity with Career/Finance builders
    """

    domain = "Legal"
    subtopic = "Property Case"

    # ══════════════════════════════════════════════════════════════
    # MINOR DETECTION  [NEW - matches Career evaluator pattern]
    # ══════════════════════════════════════════════════════════════
    def _detect_minor(self, dob: Optional[str]) -> bool:
        """
        Detect if person is currently under 18.
        Based on current date vs DOB.
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

    # ══════════════════════════════════════════════════════════════
    # LANGUAGE HELPERS
    # ══════════════════════════════════════════════════════════════
    def _get_language_instruction_safe(self, language: str) -> str:
        """Get language instruction based on user selection"""
        try:
            if hasattr(self, 'get_language_instruction'):
                return self.get_language_instruction(language)
        except Exception:
            pass

        if language == "Hindi":
            return (
                "IMPORTANT: Respond ONLY in Hindi (Devanagari script). "
                "Use Hindi for all analysis, interpretations, and recommendations. "
                "Section headers (GENERAL_ANSWER, ASTROLOGICAL_ANALYSIS, SUMMARY, REMEDIES, etc.) "
                "MUST remain in ENGLISH exactly as shown – only the content beneath them is in Hindi."
            )
        elif language == "Hinglish":
            return (
                "IMPORTANT: Respond in Hinglish (Hindi written in Roman script mixed with English). "
                "Section headers MUST remain in ENGLISH exactly as shown."
            )
        else:
            return (
                "IMPORTANT: Respond ONLY in English. "
                "Use English for all analysis, interpretations, and recommendations."
            )

    def _get_example_text(self, language: str, example_type: str) -> str:
        """Get example content in the selected language. Section headers are always English."""
        examples = {
            "Hindi": {
                "4th_house": "चतुर्थ भाव के स्वामी [planet] [house] भाव में [sign] में स्थित हैं, जो आपकी संपत्ति की स्थिति को दर्शाता है...",
                "6th_house": "षष्ठ भाव के स्वामी की स्थिति मुकदमेबाजी में आपकी क्षमता को प्रभावित करती है...",
                "9th_house": "नवम भाव के स्वामी की स्थिति न्याय और कानूनी प्रक्रिया पर प्रकाश डालती है...",
                "11th_house": "एकादश भाव की स्थिति विजय और लाभ की संभावना को दर्शाती है...",
                "mars": "मंगल (भूमि कारक) की स्थिति भूमि और संपत्ति के मामलों में बहुत महत्वपूर्ण है...",
                "saturn": "शनि की स्थिति संपत्ति के मामलों में विलंब का संकेत दे सकती है...",
                "property_strong": "आपकी संपत्ति की स्थिति सुरक्षित प्रतीत होती है।",
                "property_weak": "संपत्ति के मामले में सावधानी और सक्रियता आवश्यक है।",
                "outcome_favorable": "परिणाम आपके पक्ष में होने की संभावना अधिक है।",
                "outcome_unfavorable": "संपत्ति विवाद में कुछ चुनौतियां हो सकती हैं, सतर्क रहें।",
                "duration_short": "मामला अपेक्षाकृत जल्दी निपट सकता है।",
                "duration_long": "संपत्ति विवाद में पर्याप्त समय लग सकता है, धैर्य आवश्यक है।",
                "risk_high": "संपत्ति को लेकर जोखिम अधिक है – तत्काल सावधानी आवश्यक है।",
                "risk_low": "जोखिम का स्तर अपेक्षाकृत कम है।",
                "tell_client": "TELL CLIENT",
                "property_outlook": "संपत्ति सुरक्षा",
                "outcome_outlook": "परिणाम संभावना",
                "duration_outlook": "अवधि अनुमान",
                "risk_outlook": "जोखिम विश्लेषण",
            },
            "Hinglish": {
                "4th_house": "4th house ke swami [planet] [house] bhav mein [sign] mein hain, jo aapki property ki sthiti dikhata hai...",
                "6th_house": "6th house ke swami ki position litigation mein aapki takat ko affect karti hai...",
                "9th_house": "9th house ka analysis nyay aur legal proceedings ke baare mein bata ta hai...",
                "11th_house": "11th house ki strength victory aur gains ki sambhavna dikhati hai...",
                "mars": "Mangal (Bhoomi Karaka) ki position land aur property matters mein bahut important hai...",
                "saturn": "Shani ki position property matters mein delay indicate kar sakti hai...",
                "property_strong": "Aapki property ki position secure lagti hai.",
                "property_weak": "Property matter mein savdhani aur sakriyata zaruri hai.",
                "outcome_favorable": "Result aapke paks mein hone ki zyada sambhavna hai.",
                "outcome_unfavorable": "Property dispute mein kuch challenges ho sakte hain, alert rahein.",
                "duration_short": "Case relatively jaldi resolve ho sakta hai.",
                "duration_long": "Property dispute mein kaafi time lag sakta hai, patience rakhen.",
                "risk_high": "Property ko lekar risk zyada hai – turant savdhani zaruri hai.",
                "risk_low": "Risk level relatively kam hai.",
                "tell_client": "TELL CLIENT",
                "property_outlook": "Property Protection",
                "outcome_outlook": "Outcome Sambhavna",
                "duration_outlook": "Duration Estimate",
                "risk_outlook": "Risk Analysis",
            },
            "English": {
                "4th_house": "The lord of the 4th house, [planet], placed in the [house] house in [sign], indicates the state of your property...",
                "6th_house": "The placement of the 6th house lord reflects your capacity for litigation and dispute...",
                "9th_house": "The 9th house analysis sheds light on the prospects of justice and legal proceedings...",
                "11th_house": "The strength of the 11th house indicates the likelihood of gains and victory...",
                "mars": "Mars (Bhoomi Karaka) is the most important significator for land and property matters...",
                "saturn": "Saturn's placement may indicate delays in property-related matters...",
                "property_strong": "Your property position appears to be well-protected.",
                "property_weak": "Caution and proactive action are necessary regarding the property.",
                "outcome_favorable": "The outcome is likely to be in your favor.",
                "outcome_unfavorable": "There may be some challenges in the property dispute – stay vigilant.",
                "duration_short": "The case may be resolved relatively quickly.",
                "duration_long": "Property disputes may take considerable time – patience is essential.",
                "risk_high": "There is elevated risk to the property – immediate caution is required.",
                "risk_low": "Risk level is relatively low.",
                "tell_client": "TELL CLIENT",
                "property_outlook": "Property Protection",
                "outcome_outlook": "Outcome Prospects",
                "duration_outlook": "Duration Estimate",
                "risk_outlook": "Risk Analysis",
            },
        }
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get analysis paragraph starters in selected language"""
        return {
            "Hindi": {"vedic": "वैदिक ज्योतिष के अनुसार,"},
            "Hinglish": {"vedic": "Vedic jyotish ke anusar,"},
            "English": {"vedic": "According to Vedic astrology,"},
        }.get(language, {"vedic": "According to Vedic astrology,"})

    # ══════════════════════════════════════════════════════════════
    # SYSTEM PROMPT
    # ══════════════════════════════════════════════════════════════
    def build_system_prompt(self, language: str = "English") -> str:
        example_4th = self._get_example_text(language, "4th_house")

        return f"""You are an expert Vedic astrologer specializing in property matters, land disputes, and real estate litigation.

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
   - Never present interpretation as a computed fact

3. NO GUARANTEES
   - Never guarantee property victory or loss
   - Always present as "indications" and "tendencies"
   - Legal outcomes depend on many factors beyond astrology

   FORBIDDEN CONCEPTS – do NOT use:
   - divine grace, karmic protection, cosmic shielding, planetary protection from loss
   Replace with: "may reduce severity", "does not indicate an extreme outcome"

4. RETROGRADE RULE
   - Retrograde planets do NOT automatically indicate weakness
   - Retrograde indicates delay, review, or reconsideration only
   - Do NOT use retrograde alone to predict loss, fraud, or unfavorable judgment

5. LEGAL INFERENCE BOUNDARY (MANDATORY)
   Astrology may indicate tendencies or risk zones.
   It MUST NOT:
   - Declare fraud, forgery, or illegality as fact
   - Assert title defects or ownership loss
   - Predict court judgments or legal findings
   Use phrasing like:
   - "risk of dispute or misrepresentation"
   - "need for verification"

6. ASPECTS RULE (STRICT)
   - Aspects are SECONDARY modifiers only
   - If aspects conflict with evaluator scores, evaluator scores take priority
   Required phrasing: "This is a secondary influence" / "This does not override the core property indicators"

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "4th Lord Mars in 10th house. Exalted. Strong."
   ✅ "{example_4th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact → Explain what it means → Connect to practical strategy

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY SECTION

5. PROVIDE BALANCED, PROFESSIONAL GUIDANCE
   - Do NOT equate a low score with guaranteed loss
   - Always combine strength with dignity, house, and benefic influence

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR PROPERTY LEGAL DISPUTES
═══════════════════════════════════════════════════════════════════════════════

- 4th:  LAND, PROPERTY, REAL ESTATE (PRIMARY)
- 1st:  Self, your position in the dispute
- 2nd:  Immovable assets, family property
- 6th:  Litigation, disputes, enemies, ability to fight
- 7th:  Opponent in property dispute
- 8th:  Hidden matters, inheritance issues
- 9th:  Justice, legal proceedings, higher courts
- 10th: Government, land records, authority
- 11th: Victory, gains, favorable outcomes
- 12th: Losses, expenses, property loss risk

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS FOR PROPERTY
═══════════════════════════════════════════════════════════════════════════════

- Mars:    BHOOMI KARAKA (Land Significator) – most important
- Saturn:  Real estate, boundaries, delays
- Jupiter: Law, justice, expansion
- Venus:   Property value, comfort
- Sun:     Government, land records
- Moon:    Home, ancestral property

FINAL SELF-CHECK (MANDATORY):
Before responding, verify:
- No forbidden legal or metaphysical claims are made
- Outcome language matches evaluator likelihood
- Retrograde is not used to predict loss
- Risks are framed as actionable concerns, not predictions
If any rule is violated, revise the response.
"""

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO FORMATTER  [NEW - matches Career/Finance pattern]
    # ══════════════════════════════════════════════════════════════
    def _format_lagna_info(self, lagna_info: Optional[Dict]) -> str:
        """Format lagna (ascendant) information for the prompt."""
        if not lagna_info:
            return (
                "═══════════════════════════════════════════════════════\n"
                "⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE\n"
                "═══════════════════════════════════════════════════════\n"
                "Do NOT guess or invent lagna sign.\n"
                "Skip lagna lord analysis completely.\n"
                "═══════════════════════════════════════════════════════"
            )

        lord       = lagna_info.get("lagna_lord", "N/A")
        sign       = lagna_info.get("lagna_sign", "N/A")
        lord_house = lagna_info.get("lagna_lord_house", "N/A")
        lord_sign  = lagna_info.get("lagna_lord_sign", "N/A")
        dignity    = lagna_info.get("lagna_lord_dignity", "Unknown")
        degree     = lagna_info.get("lagna_lord_degree", 0)

        personality_map = {
            "Sun":     "Authoritative, government-focused, ego-driven in disputes",
            "Moon":    "Emotionally attached to property, fluctuating resolve",
            "Mars":    "Courageous, aggressive, persistent fighter in legal battles",
            "Mercury": "Analytical, document-oriented, strong in evidence-based arguments",
            "Jupiter": "Righteous, inclined toward fair settlement, law-abiding",
            "Venus":   "Prefers settlement, values comfort and harmony over prolonged fight",
            "Saturn":  "Patient, methodical, prepared for long legal battles",
            "Rahu":    "Unconventional tactics, may explore non-standard legal avenues",
            "Ketu":    "Detached from property outcomes, spiritual approach to conflict",
        }
        personality = personality_map.get(lord, "Unique approach to property disputes")

        lines = [
            "═══════════════════════════════════════════════════════",
            "🎯 LAGNA (ASCENDANT) – DISPUTE PERSONALITY",
            "═══════════════════════════════════════════════════════",
            "",
            f"Lagna Sign (1st House): {sign}",
            f"Lagna Lord: {lord}",
            f"Placed in: House {lord_house}, {lord_sign}",
            f"Dignity: {dignity}",
        ]
        if degree:
            lines.append(f"Degree: {degree:.2f}°")

        lines += [
            "",
            f"Dispute Personality: {personality}",
            "",
            "⚠️ IMPORTANT:",
            "• This is Lagna (Ascendant), NOT Moon sign",
            "• There is only ONE lagna for this person",
            "• Lagna lord shows fundamental approach to the legal fight",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS FORMATTER  [NEW - matches Career/Finance pattern]
    # ══════════════════════════════════════════════════════════════
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """Format BEST and NEAREST timing windows for LLM."""
        if not timing_windows_data or not timing_windows_data.get("has_timing"):
            return ""

        try:
            best    = timing_windows_data.get("best_window")
            nearest = timing_windows_data.get("nearest_window")
            all_w   = timing_windows_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = [
                "═══════════════════════════════════════════════════════",
                "⭐ TIMING WINDOWS ANALYSIS",
                "═══════════════════════════════════════════════════════",
                "",
                "⚠️ CRITICAL: You MUST mention BOTH windows below.",
                "Let the person choose based on their situation.",
                "",
            ]

            if best:
                lines += [
                    "╔═══════════════════════════════════════════════════╗",
                    "║  🏆 BEST WINDOW (Highest Astrological Score)      ║",
                    "╚═══════════════════════════════════════════════════╝",
                    "",
                    f"  Dasha: {best.get('dasha', 'N/A')}",
                    f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}",
                    f"  Score: {best.get('final_score', 0):.1f}/100",
                    f"  Age at start: {best.get('age_at_start', 'N/A')} years",
                    "",
                    "  Why this is BEST:",
                    f"    • Maha Dasha score: {best.get('score_maha', 0)}/10",
                    f"    • Antara Dasha score: {best.get('score_antara', 0)}/10",
                    f"    • Pratyantar score: {best.get('score_paryantar', 0)}/10",
                    f"    • Transit support: {best.get('transit_score', 0):.1f}%",
                    "",
                    "  Trade-off: May be further in future, but strongest dasha alignment",
                    "",
                ]

            if nearest:
                is_same = best and (
                    best.get("dasha") == nearest.get("dasha") and
                    best.get("start") == nearest.get("start")
                )
                lines += [
                    "╔═══════════════════════════════════════════════════╗",
                    "║  ⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity) ║",
                    "╚═══════════════════════════════════════════════════╝",
                    "",
                    f"  Dasha: {nearest.get('dasha', 'N/A')}",
                    f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}",
                    f"  Score: {nearest.get('final_score', 0):.1f}/100",
                    f"  Age at start: {nearest.get('age_at_start', 'N/A')} years",
                    "",
                ]
                if is_same:
                    lines += [
                        "  🎯 IDEAL: Best and Nearest are THE SAME window!",
                        "     Optimal alignment + earliest opportunity together.",
                    ]
                else:
                    lines += [
                        "  Trade-off: Sooner opportunity, but not absolute best alignment",
                    ]
                lines.append("")

            if len(all_w) > 2:
                lines += [
                    "📋 OTHER FAVORABLE WINDOWS (Top 5):",
                    "─" * 50,
                ]
                for i, w in enumerate(all_w[:5], 1):
                    is_best    = best    and w.get("dasha") == best.get("dasha")    and w.get("start") == best.get("start")
                    is_nearest = nearest and w.get("dasha") == nearest.get("dasha") and w.get("start") == nearest.get("start")
                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {w.get('dasha','N/A')}")
                    lines.append(f"     {w.get('start','N/A')} to {w.get('end','N/A')}  Score: {w.get('final_score',0):.1f}")
                lines.append("")

            lines += [
                "═══════════════════════════════════════════════════════",
                "YOUR RESPONSE MUST:",
                "  • Mention BOTH best and nearest windows with exact dates",
                "  • Explain WHY each period is astrologically favorable",
                "  • Let person choose: wait for best OR act sooner",
                "  • If best = nearest, emphasize this is ideal timing",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # SUITABILITY MATRIX FORMATTER  [NEW]
    # ══════════════════════════════════════════════════════════════
    def _format_suitability_matrix(self, matrix: Dict) -> str:
        """Format property legal strategy suitability matrix."""
        if not matrix:
            return ""

        lines = [
            "═══════════════════════════════════════════════════════",
            "📊 PROPERTY LEGAL STRATEGY MATRIX",
            "═══════════════════════════════════════════════════════",
            "",
            "Based on Vedic analysis of property protection, outcome, duration and risk:",
            "",
            "| Strategy | Rating | Reasoning |",
            "|----------|--------|-----------|",
        ]

        rating_markers = {
            "HIGH":     "✅",
            "MODERATE": "⚖️",
            "LOW":      "○",
        }

        for strategy, details in matrix.items():
            rating    = details.get("rating", "MODERATE")
            reasoning = details.get("vedic_reasoning", "")
            marker    = rating_markers.get(rating, "○")
            if len(reasoning) > 60:
                reasoning = reasoning[:57] + "..."
            lines.append(f"| {marker} {strategy} | {rating} | {reasoning} |")

        lines += [
            "",
            "⚠️ Use this matrix to guide strategy recommendation.",
            "   HIGH = strongly recommended, MODERATE = viable, LOW = generally not advised.",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # CURRENT DASHA FORMATTER  [NEW]
    # ══════════════════════════════════════════════════════════════
    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """Format current dasha information for the prompt."""
        if not current_dasha:
            return ""

        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end   = date_range.get("end", "Unknown")

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun",  "Mo": "Moon",
                "Ma": "Mars",   "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus",  "Ra": "Rahu",  "Ke": "Ketu",
            }
            parts = dasha_name.replace(">", "-").replace("/", "-").split("-")
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted = " > ".join(full_names) if full_names else dasha_name

            lines = [
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS – DO NOT INVENT)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL current dasha running now",
                "• Use for analyzing present-day legal situation",
                "• For future planning, see UPCOMING DASHA PERIODS below",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # DASHA TIMELINE FORMATTER  [NEW]
    # ══════════════════════════════════════════════════════════════
    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        """Format dasha timeline (2Y past → 10Y future) for the prompt."""
        if not dasha_timeline:
            return ""

        try:
            current = dasha_timeline.get("current", [])
            future  = dasha_timeline.get("next_10_years", [])

            if not current and not future:
                return ""

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun",  "Mo": "Moon",
                "Ma": "Mars",   "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus",  "Ra": "Rahu",  "Ke": "Ketu",
            }

            def parse(name: str) -> str:
                parts = name.replace(">", "-").replace("/", "-").split("-")
                return " > ".join([dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()])

            lines = [
                "═══════════════════════════════════════════════════════",
                "DASHA TIMELINE (For Property Case Planning)",
                "═══════════════════════════════════════════════════════",
                "",
            ]

            if current:
                lines.append("🔴 CURRENT DASHA (Running Now):")
                for d in current[:3]:
                    dr = d.get("date_range", {})
                    lines.append(f"  • {parse(d.get('dasha_name',''))}  {dr.get('start','')} to {dr.get('end','')}")
                lines.append("")

            if future:
                lines.append("⏭️  UPCOMING PERIODS (Next 10 Years):")
                lines.append("-" * 50)
                for i, d in enumerate(future[:20], 1):
                    dr = d.get("date_range", {})
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parse(d.get('dasha_name',''))}")
                    lines.append(f"     {dr.get('start','')} to {dr.get('end','')}")
                lines.append("")

            lines += [
                "═══════════════════════════════════════════════════════",
                "PROPERTY CASE DASHA GUIDELINES:",
                "• Jupiter/Sun dashas → favorable for legal justice",
                "• Saturn dashas → delays but eventual stability",
                "• Mars dashas → aggressive fighting energy",
                "• Rahu dashas → unexpected turns, verify documents",
                "• Mercury dashas → good for documentation and negotiation",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # EVALUATOR DATA FORMATTERS (updated from v1.0)
    # ══════════════════════════════════════════════════════════════
    def _format_property_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        prop = additional_data.get(f"{DOMAIN_PREFIX}_property_analysis", {})
        if not prop:
            return ""

        lines = ["PROPERTY ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Property Protection: {prop.get('property_protection', 'MODERATE')}")
        lines.append(f"• Property Score: {prop.get('property_score', 50)}/100")
        lines.append(f"• 4th House Strength: {prop.get('fourth_house_strength', 'MODERATE')}")
        lines.append(f"• Mars (Bhoomi Karaka): {prop.get('mars_strength', 'MODERATE')}")

        for label, key, icon in [
            ("Property Favorable Factors", "favorable_factors", "✅"),
            ("Property Challenging Factors", "unfavorable_factors", "⚠️"),
            ("Property Hints", "property_hints", "🏠"),
        ]:
            items = prop.get(key, [])
            if items:
                lines.append("")
                lines.append(f"{label}:")
                for item in items[:4]:
                    lines.append(f"  {icon} {item}")

        return "\n".join(lines)

    def _format_outcome_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        if not outcome:
            return ""

        lines = ["OUTCOME ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Likelihood: {outcome.get('likelihood', 'UNCERTAIN')}")
        lines.append(f"• Score: {outcome.get('score', 50)}/100")

        for label, key, icon in [
            ("Favorable Factors", "favorable_factors", "✅"),
            ("Challenging Factors", "unfavorable_factors", "⚠️"),
            ("Strategic Hints", "strategic_hints", "💡"),
        ]:
            items = outcome.get(key, [])
            if items:
                lines.append("")
                lines.append(f"{label}:")
                for item in items[:4]:
                    lines.append(f"  {icon} {item}")

        return "\n".join(lines)

    def _format_duration_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        if not duration:
            return ""

        lines = ["DURATION ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Category: {duration.get('duration_category', 'MODERATE')}")
        lines.append(f"• Score: {duration.get('duration_score', 50)}/100 (higher = longer)")

        for label, key, icon in [
            ("Delay Factors", "delay_factors", "⏳"),
            ("Speed Factors", "speed_factors", "⚡"),
            ("Duration Hints", "duration_hints", "📅"),
        ]:
            items = duration.get(key, [])
            if items:
                lines.append("")
                lines.append(f"{label}:")
                for item in items[:3]:
                    lines.append(f"  {icon} {item}")

        return "\n".join(lines)

    def _format_risk_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        if not risk:
            return ""

        lines = ["RISK & PENALTY ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Risk Level: {risk.get('risk_level', 'MODERATE')}")
        lines.append(f"• Risk Score: {risk.get('risk_score', 50)}/100")

        for label, key, icon in [
            ("Risk Factors", "risk_factors", "🚨"),
            ("Penalty Indicators", "penalty_indicators", "💰"),
            ("Areas of Concern", "areas_of_concern", "⚠️"),
            ("Mitigation Hints", "mitigation_hints", "🛡️"),
        ]:
            items = risk.get(key, [])
            if items:
                lines.append("")
                lines.append(f"{label}:")
                for item in items[:4]:
                    lines.append(f"  {icon} {item}")

        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = ["HOUSE LORDS DATA:"]
        property_houses = {1, 2, 4, 6, 7, 8, 9, 10, 11, 12}

        for house_num in sorted(house_lords.keys()):
            if house_num not in property_houses:
                continue
            info = house_lords.get(house_num, {})
            if not info:
                continue

            lord         = info.get("lord", "N/A")
            lord_house   = info.get("lord_in_house", "N/A")
            lord_sign    = info.get("lord_in_sign", "N/A")
            dignity      = info.get("lord_dignity", "N/A")
            strength     = info.get("lord_strength_score", 0)
            conditions   = []
            if info.get("lord_is_combust"):
                conditions.append("Combust")
            if info.get("lord_is_retrograde"):
                conditions.append("Retrograde")
            cond_str = ", ".join(conditions) if conditions else "Normal"
            planets  = ", ".join(info.get("planets_in_house", [])) or "None"
            prefix   = "★" if house_num == 4 else "•"
            lines.append(
                f"{prefix} H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | "
                f"{dignity} | {cond_str} | Str:{strength}/100 | Planets:{planets}"
            )

        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        lines = ["ASPECTS DATA:"]
        for house_num in sorted(aspects_info.keys()):
            aspects  = aspects_info[house_num]
            benefic  = aspects.get("benefic_aspects", [])
            malefic  = aspects.get("malefic_aspects", [])
            if benefic or malefic:
                prefix = "★" if house_num == 4 else "•"
                lines.append(
                    f"{prefix} H{house_num}: "
                    f"Benefic={', '.join(benefic) or 'None'} | "
                    f"Malefic={', '.join(malefic) or 'None'}"
                )

        return "\n".join(lines) if len(lines) > 1 else ""

    # ══════════════════════════════════════════════════════════════
    # CONVENIENCE GETTERS
    # ══════════════════════════════════════════════════════════════
    def _get_property_protection(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_property_analysis") or {}).get("property_protection", "MODERATE")

    def _get_property_score(self, ad: Dict) -> int:
        return (ad.get(f"{DOMAIN_PREFIX}_property_analysis") or {}).get("property_score", 50)

    def _get_fourth_house_strength(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_property_analysis") or {}).get("fourth_house_strength", "MODERATE")

    def _get_mars_strength(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_property_analysis") or {}).get("mars_strength", "MODERATE")

    def _get_outcome_likelihood(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_outcome_analysis") or {}).get("likelihood", "UNCERTAIN")

    def _get_outcome_score(self, ad: Dict) -> int:
        return (ad.get(f"{DOMAIN_PREFIX}_outcome_analysis") or {}).get("score", 50)

    def _get_duration_category(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_duration_analysis") or {}).get("duration_category", "MODERATE")

    def _get_risk_level(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_risk_analysis") or {}).get("risk_level", "MODERATE")

    def _get_risk_score(self, ad: Dict) -> int:
        return (ad.get(f"{DOMAIN_PREFIX}_risk_analysis") or {}).get("risk_score", 50)

    # ══════════════════════════════════════════════════════════════
    # MAIN ROUTING  (updated with minor + timing gate)
    # ══════════════════════════════════════════════════════════════
    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """Main routing method – selects appropriate sub-prompt."""
        try:
            sub_subdomain   = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw             = "\n".join(technical_points) if technical_points else ""

            # ── Minor detection (global, same as Career builder) ──────────
            dob      = kwargs.get("dob")
            is_minor = self._detect_minor(dob)
            kwargs["is_minor"] = is_minor
            logger.warning(f"[PROPERTY_LEGAL] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

            logger.info(f"Building prompt | sub: {sub_subdomain} | lang: {language} | minor: {is_minor}")

            # ── Route ─────────────────────────────────────────────────────
            if "Outcome" in sub_subdomain:
                return self._build_outcome_prompt(question, additional_data, raw, language, kwargs)
            elif "Duration" in sub_subdomain or "Timeline" in sub_subdomain:
                return self._build_duration_prompt(question, additional_data, raw, language, kwargs)
            elif "Risk" in sub_subdomain or "Penalty" in sub_subdomain or "Loss" in sub_subdomain:
                return self._build_risk_prompt(question, additional_data, raw, language, kwargs)
            elif "Timing" in sub_subdomain or "When" in sub_subdomain:
                return self._build_timing_prompt(question, additional_data, raw, language, kwargs)
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language, kwargs)
            else:
                return self._build_general_prompt(question, additional_data, raw, language, kwargs)

        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ══════════════════════════════════════════════════════════════
    # MINOR OVERRIDE BLOCK  [NEW]
    # ══════════════════════════════════════════════════════════════
    def _minor_override_block(self, dob: Optional[str]) -> str:
        """
        Returns a strict developmental-mode instruction block for minors.
        Property disputes are legal matters; minors should not be advised
        to take personal legal action.
        """
        return f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob or 'Not provided'}
The person is currently under 18 years of age.

STRICT RULES FOR MINOR:
• Do NOT advise the minor to personally take legal action
• Do NOT predict property win/loss as if they are the primary litigant
• Do NOT recommend aggressive litigation strategies to the minor directly
• Frame all analysis in the context of the FAMILY's property situation

INTERPRETATION RULES:
• Describe the astrological indications for the family's property
• Offer guidance on what the family should do (not the minor personally)
• Focus on protective measures, document security, and long-term outlook
• Timing windows (if present) apply to the FAMILY action, not the minor

TONE:
• Protective and family-centered
• Future-oriented (property secured for the minor's future)
• Supportive, not alarming
"""

    # ══════════════════════════════════════════════════════════════
    # OUTPUT FORMAT GENERATOR
    # ══════════════════════════════════════════════════════════════
    def _get_output_format(
        self,
        language: str,
        has_timing: bool,
        prompt_type: str,
        labels: Dict[str, str],
    ) -> str:
        """
        Build the OUTPUT FORMAT block.
        Section headers always in English; content language from labels.
        """
        timing_section = ""
        if has_timing:
            timing_section = """
**TIMING_RECOMMENDATION:**
⚠️ MANDATORY: Mention BOTH timing windows with exact dates.

🏆 BEST WINDOW:
- Period: [exact start] to [exact end]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain dasha lords + property significations]
- Trade-off: May be further in future

⏰ NEAREST WINDOW:
- Period: [exact start] to [exact end]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Sooner but not absolute best

👤 CHOICE FOR PERSON:
Choose BEST if: Can wait, want optimal dasha support
Choose NEAREST if: Urgent need, needs to act sooner

If BEST = NEAREST: "🎯 IDEAL – same window! Act during this period."
"""

        return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT ENGLISH HEADERS SHOWN BELOW):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{labels.get('property_outlook', 'Property Protection')}: [label from evaluator]
{labels.get('outcome_outlook', 'Outcome Prospects')}: [label from evaluator]
{labels.get('duration_outlook', 'Duration Estimate')}: [label from evaluator]
{labels.get('risk_outlook', 'Risk Analysis')}: [label from evaluator]
Brief 3-4 line assessment in flowing prose.
NO technical astrological terms (houses, planets, yogas).
Evaluator categories (risk level, duration) may be referenced in neutral advisory language.

ASTROLOGICAL_ANALYSIS:
Write every section in FLOWING PARAGRAPHS – no bullet lists.

PARAGRAPH 1 – 4TH HOUSE & PROPERTY PROTECTION:
Begin this paragraph with the vedic starter provided.
Analyze 4th house (PRIMARY property house) with interpretation.

PARAGRAPH 2 – MARS (BHOOMI KARAKA):
Mars as land significator + practical meaning.

PARAGRAPH 3 – LITIGATION & OPPONENT:
6th house (your litigation strength) vs 7th house (opponent).

PARAGRAPH 4 – JUSTICE & VICTORY:
9th house (justice) + 11th house (victory) + Jupiter.

PARAGRAPH 5 – DURATION:
Saturn, retrograde factors, realistic timeline.

PARAGRAPH 6 – RISK ASSESSMENT:
12th/8th lord analysis, Rahu influence.
Frame as verification needs, NOT legal predictions.

PARAGRAPH 7 – STRATEGY:
Actionable recommendations based on full chart picture.
{timing_section}

SUMMARY:
{labels.get('tell_client', 'TELL CLIENT')}: "[Property protection + Outcome + Duration + Key risk + Primary action]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Remedy 1 (4th house / property protection focus)
- Remedy 2 (Mars / Bhoomi Karaka if weak)
- Remedy 3 (Jupiter for justice if needed)

REMEDIES_GENERAL:
- Consult qualified property lawyer immediately
- Verify all property documents (title, chain of ownership)
- Secure original documents in safe location
- Maintain patience – property cases are extended matters
═══════════════════════════════════════════════════════════════════════════════
"""

    # ══════════════════════════════════════════════════════════════
    # GENERAL PROMPT (Comprehensive)  [UPDATED]
    # ══════════════════════════════════════════════════════════════
    def _build_general_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        labels     = self._get_example_text.__func__  # used below per key
        starters   = self._get_analysis_starters(language)
        lbl        = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor       = kwargs.get("is_minor", False)
        dob            = kwargs.get("dob")
        current_dasha  = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        # Evaluator values
        pp  = self._get_property_protection(additional_data)
        ps  = self._get_property_score(additional_data)
        fhs = self._get_fourth_house_strength(additional_data)
        ms  = self._get_mars_strength(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        os_ = self._get_outcome_score(additional_data)
        dc  = self._get_duration_category(additional_data)
        rl  = self._get_risk_level(additional_data)
        rs  = self._get_risk_score(additional_data)

        # Timing
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing  = timing_data.get("has_timing", False) if not is_minor else False

        # Formatted blocks
        lagna_block    = self._format_lagna_info(additional_data.get("lagna_info"))
        matrix_block   = self._format_suitability_matrix(additional_data.get(f"{DOMAIN_PREFIX}_suitability_matrix", {}))
        timing_block   = self._format_timing_windows(timing_data) if has_timing else ""
        dasha_block    = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        prop_block     = self._format_property_analysis(additional_data)
        out_block      = self._format_outcome_analysis(additional_data)
        dur_block      = self._format_duration_analysis(additional_data)
        risk_block     = self._format_risk_analysis(additional_data)
        lords_block    = self._format_house_lords(additional_data)
        aspects_block  = self._format_house_aspects(additional_data)

        minor_block = self._minor_override_block(dob) if is_minor else ""
        risk_warning = (
            "\n⚠️ HIGH RISK INDICATORS DETECTED – emphasize immediate legal counsel.\n"
            if rl in ["HIGH", "VERY_HIGH"] else ""
        )

        output_format = self._get_output_format(language, has_timing, "general", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: LAND / PROPERTY LEGAL DISPUTE – GENERAL ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Property Protection: {pp} ({ps}/100)
4th House Strength: {fhs}
Mars (Bhoomi Karaka): {ms}
Outcome Likelihood: {ol} ({os_}/100)
Expected Duration: {dc}
Risk Level: {rl} ({rs}/100)
Timing Windows Available: {'YES ✅' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{risk_warning}

{timing_block}

{lagna_block}

{matrix_block}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{prop_block}

{out_block}

{dur_block}

{risk_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{aspects_block or ""}

{dasha_block}

{timeline_block}

{raw or ""}

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

{output_format}
"""

    # ══════════════════════════════════════════════════════════════
    # TIMING PROMPT  [NEW – for sub_subdomain containing "Timing"]
    # ══════════════════════════════════════════════════════════════
    def _build_timing_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        starters   = self._get_analysis_starters(language)
        lbl        = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor       = kwargs.get("is_minor", False)
        dob            = kwargs.get("dob")
        current_dasha  = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        pp  = self._get_property_protection(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        dc  = self._get_duration_category(additional_data)
        rl  = self._get_risk_level(additional_data)

        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing  = timing_data.get("has_timing", False) if not is_minor else False

        timing_block   = self._format_timing_windows(timing_data) if has_timing else ""
        dasha_block    = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        lagna_block    = self._format_lagna_info(additional_data.get("lagna_info"))
        lords_block    = self._format_house_lords(additional_data)
        aspects_block  = self._format_house_aspects(additional_data)
        prop_block     = self._format_property_analysis(additional_data)
        out_block      = self._format_outcome_analysis(additional_data)

        minor_block = self._minor_override_block(dob) if is_minor else ""

        # Fallback instruction when no timing windows exist
        fallback_timing_note = ""
        if not has_timing:
            fallback_timing_note = """
⚠️ TIMING FALLBACK MODE (No structured timing windows available)

FORBIDDEN phrases:
• "You will win the case in..."
• "Settlement will happen in..."
• "Property will be secured in..."

ALLOWED language:
• "This period may strengthen your legal position..."
• "Documentation and evidence gathering is well-supported during..."
• "Higher probability of favorable developments in..."

Use dasha timeline below for general guidance only.
"""

        output_format = self._get_output_format(language, has_timing, "timing", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROPERTY CASE TIMING ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Property Protection: {pp}
Outcome Likelihood: {ol}
Expected Duration: {dc}
Risk Level: {rl}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{fallback_timing_note}

{timing_block}

{lagna_block}

{prop_block}

{out_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{aspects_block or ""}

{dasha_block}

{timeline_block}

{raw or ""}

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

{output_format}
"""

    # ══════════════════════════════════════════════════════════════
    # OUTCOME PROMPT  [UPDATED]
    # ══════════════════════════════════════════════════════════════
    def _build_outcome_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        pp  = self._get_property_protection(additional_data)
        fhs = self._get_fourth_house_strength(additional_data)
        ms  = self._get_mars_strength(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        os_ = self._get_outcome_score(additional_data)

        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing  = timing_data.get("has_timing", False) if not is_minor else False
        timing_block = self._format_timing_windows(timing_data) if has_timing else ""

        prop_block  = self._format_property_analysis(additional_data)
        out_block   = self._format_outcome_analysis(additional_data)
        lords_block = self._format_house_lords(additional_data)
        asp_block   = self._format_house_aspects(additional_data)
        lagna_block = self._format_lagna_info(additional_data.get("lagna_info"))
        matrix_block = self._format_suitability_matrix(additional_data.get(f"{DOMAIN_PREFIX}_suitability_matrix", {}))

        minor_block    = self._minor_override_block(dob) if is_minor else ""
        outcome_text   = (
            self._get_example_text(language, "outcome_favorable")
            if os_ >= 60
            else self._get_example_text(language, "outcome_unfavorable")
        )

        output_format = self._get_output_format(language, has_timing, "outcome", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROPERTY DISPUTE OUTCOME ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Property Protection: {pp}
4th House Strength: {fhs} | Mars: {ms}
Outcome Likelihood: {ol} ({os_}/100)
Timing Available: {'YES ✅' if has_timing else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{timing_block}

{lagna_block}

{matrix_block}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{prop_block}

{out_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{asp_block or ""}

{raw or ""}

OUTCOME CONTEXT: {outcome_text}

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

{output_format}
"""

    # ══════════════════════════════════════════════════════════════
    # DURATION PROMPT  [UPDATED]
    # ══════════════════════════════════════════════════════════════
    def _build_duration_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        dc = self._get_duration_category(additional_data)
        dur_block   = self._format_duration_analysis(additional_data)
        lords_block = self._format_house_lords(additional_data)
        lagna_block = self._format_lagna_info(additional_data.get("lagna_info"))

        current_dasha  = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")
        dasha_block    = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        minor_block   = self._minor_override_block(dob) if is_minor else ""
        duration_text = (
            self._get_example_text(language, "duration_short")
            if dc in ["VERY_SHORT", "SHORT"]
            else self._get_example_text(language, "duration_long")
        )

        output_format = self._get_output_format(language, False, "duration", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROPERTY CASE DURATION / TIMELINE ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Duration Category: {dc}
═══════════════════════════════════════════════════════════════════════════════

NOTE: Property disputes in India typically take several years due to complex
documentation requirements, multiple hearings, revenue records verification,
and title chain checks. Set realistic expectations.

USER QUESTION:
"{question}"

{minor_block}

{lagna_block}

{dur_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{dasha_block}

{timeline_block}

{raw or ""}

DURATION CONTEXT: {duration_text}

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

OUTPUT FORMAT:

GENERAL_ANSWER:
{lbl['duration_outlook']}: {duration_text}
Brief 3-line duration assessment in flowing prose. No astrological jargon.

ASTROLOGICAL_ANALYSIS:
Write in flowing paragraphs:

PARAGRAPH 1 – SATURN & TIME: Saturn's placement + meaning for property timeline.
PARAGRAPH 2 – DELAY FACTORS: Retrograde planets, Rahu/Ketu, 4th/6th lord retrograde.
PARAGRAPH 3 – SPEED FACTORS: Mercury, benefic aspects, anything expediting matters.
PARAGRAPH 4 – REALISTIC TIMELINE: Expected phases of the case.
PARAGRAPH 5 – STRATEGY: When to push, when to wait.

SUMMARY:
{lbl['tell_client']}: "[Duration + Key delay factor + Strategic patience guidance]"

REMEDIES_ASTROLOGICAL:
- Saturn remedy (if delays prominent)
- Mercury remedy (for smoother documentation)

REMEDIES_GENERAL:
- Plan finances for extended timeline
- Keep documents organized and accessible
- Regular follow-up with lawyer
═══════════════════════════════════════════════════════════════════════════════
"""

    # ══════════════════════════════════════════════════════════════
    # RISK PROMPT  [UPDATED]
    # ══════════════════════════════════════════════════════════════
    def _build_risk_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        pp  = self._get_property_protection(additional_data)
        rl  = self._get_risk_level(additional_data)
        rs  = self._get_risk_score(additional_data)

        prop_block  = self._format_property_analysis(additional_data)
        risk_block  = self._format_risk_analysis(additional_data)
        lords_block = self._format_house_lords(additional_data)
        asp_block   = self._format_house_aspects(additional_data)
        lagna_block = self._format_lagna_info(additional_data.get("lagna_info"))

        minor_block = self._minor_override_block(dob) if is_minor else ""
        risk_text   = (
            self._get_example_text(language, "risk_high")
            if rl in ["HIGH", "VERY_HIGH"]
            else self._get_example_text(language, "risk_low")
        )

        output_format = self._get_output_format(language, False, "risk", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROPERTY RISK & LOSS ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Property Protection: {pp}
Risk Level: {rl} ({rs}/100)
═══════════════════════════════════════════════════════════════════════════════

SENSITIVITY NOTE: Property loss is emotionally distressing.
Present risks objectively, always provide mitigation strategies,
emphasize that outcomes depend on actions taken, and strongly
recommend professional legal counsel.

USER QUESTION:
"{question}"

{minor_block}

{lagna_block}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{prop_block}

{risk_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{asp_block or ""}

{raw or ""}

RISK CONTEXT: {risk_text}

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

OUTPUT FORMAT:

GENERAL_ANSWER:
{lbl['risk_outlook']}: {risk_text}
Brief 3-line risk assessment in flowing prose. No astrological jargon.

ASTROLOGICAL_ANALYSIS:
Write in flowing paragraphs:

PARAGRAPH 1 – PROPERTY PROTECTION: 4th house + Mars (Bhoomi Karaka) condition.
PARAGRAPH 2 – PROPERTY LOSS INDICATORS: 12th lord in 4th, 8th house influence.
PARAGRAPH 3 – FRAUD & TITLE RISK: Rahu influence as risk of confusion/misrepresentation.
               Frame as verification need, NOT assertion of fraud.
PARAGRAPH 4 – SPECIFIC RISK AREAS: Financial, title, inheritance, encroachment.
PARAGRAPH 5 – PROTECTIVE FACTORS: What is working in favor, benefic influences.
PARAGRAPH 6 – MITIGATION ACTION PLAN: Immediate steps to protect property.

SUMMARY:
{lbl['tell_client']}: "[Risk level + Primary concern + Immediate action]"

REMEDIES_ASTROLOGICAL:
- 4th house protection remedy
- Bhoomi Puja for land protection
- Hanuman/Durga worship for protection from adversaries

REMEDIES_GENERAL:
- IMMEDIATE: Verify all property documents with lawyer
- Secure originals in bank locker
- Get professional title search done
- Document all boundaries and possessions
═══════════════════════════════════════════════════════════════════════════════
"""

    # ══════════════════════════════════════════════════════════════
    # REMEDIES PROMPT  [UPDATED]
    # ══════════════════════════════════════════════════════════════
    def _build_remedies_prompt(
        self,
        question: str,
        additional_data: Dict,
        raw: str,
        language: str,
        kwargs: Dict,
    ) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "property_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        pp  = self._get_property_protection(additional_data)
        fhs = self._get_fourth_house_strength(additional_data)
        ms  = self._get_mars_strength(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        rl  = self._get_risk_level(additional_data)

        lords_block = self._format_house_lords(additional_data)
        lagna_block = self._format_lagna_info(additional_data.get("lagna_info"))

        current_dasha = kwargs.get("current_dasha")
        dasha_block   = self._format_current_dasha(current_dasha)

        minor_block = self._minor_override_block(dob) if is_minor else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REMEDIES FOR PROPERTY DISPUTE SUCCESS
Current Date: {today_str}
Weightage: VEDIC 100%
Property Protection: {pp}  4th House Strength: {fhs}
Mars (Bhoomi Karaka): {ms}  Outcome Likelihood: {ol}  Risk: {rl}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{lagna_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{dasha_block}

{raw or ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR PROPERTY DISPUTES:
═══════════════════════════════════════════════════════════════════════════════

Recommend MAXIMUM 3 astrological remedies linked to the most affected planet.

4th LORD WEAK:    Strengthen with remedies for that planet
MARS WEAK:        Red coral (with caution), Tuesday fasts, Hanuman worship
SATURN AFFLICTING 4th: Saturday fasts, Shani puja
JUPITER WEAK:     Yellow sapphire, Thursday fasts, Vishnu worship
RAHU IN 4th:      Durga worship, Rahu remedies

Traditional Property Remedies:
- Bhoomi Puja (most important for land)
- Vastu Shanti for property protection
- Hanuman Chalisa for strength in legal battle
- Baglamukhi Puja for victory over adversaries
- Navagraha Shanti

Mantras:
- "Om Bhoumaya Namah" – Mars mantra for land
- "Om Gam Ganapataye Namah" – Remove obstacles
- "Om Dum Durgayei Namah" – Protection
═══════════════════════════════════════════════════════════════════════════════

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

OUTPUT FORMAT:

GENERAL_ANSWER:
What astrological challenges exist and how remedies may help.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in flowing paragraphs:

PARAGRAPH 1 – WEAK PLANETS IDENTIFIED: 4th lord condition, Mars condition.
PARAGRAPH 2 – PRIMARY REMEDY (Property Protection): Most important remedy + detailed instructions.
PARAGRAPH 3 – MARS (BHOOMI KARAKA) REMEDY: If Mars weak, specific remedy + timing.
PARAGRAPH 4 – SUPPORTING REMEDIES: Jupiter for justice, current dasha lord.
PARAGRAPH 5 – TIMING: Best days, duration, expected effects.

SUMMARY:
{lbl['tell_client']}: "[Priority remedy + Practice schedule + Property protection benefit]"

REMEDIES_ASTROLOGICAL:
1. [Bhoomi Puja / 4th house remedy with detailed instructions]
2. [Mars remedy if Bhoomi Karaka is weak]
3. [Jupiter remedy for justice if needed]

REMEDIES_GENERAL:
- Consult qualified property lawyer FIRST
- Verify all property documents professionally
- Secure original documents safely
- Maintain ethical conduct throughout dispute
- Practice patience – property cases take time
═══════════════════════════════════════════════════════════════════════════════
"""

    # ══════════════════════════════════════════════════════════════
    # FALLBACK PROMPT
    # ══════════════════════════════════════════════════════════════
    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in property matters and land disputes.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
Focus on 4th house (property) and Mars (Bhoomi Karaka).
Include practical strategic guidance.
End with a clear actionable statement.
Always recommend consulting qualified legal professionals.
"""
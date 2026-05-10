"""
Legal Business Dispute – LLM Prompts v2.0

ENHANCEMENTS FROM v1.0:
✅ Minor detection logic            (matches Property/Career evaluator pattern)
✅ Timing windows support           (BEST + NEAREST windows)
✅ Lagna info formatting            (from evaluator v2.0 lagna_info)
✅ Business suitability matrix formatting
✅ Improved answer flow             (no bullet dumps, flowing paragraphs)
✅ Dasha context formatting         (current_dasha + dasha_timeline)
✅ Hinglish language support        (3-way: Hindi / Hinglish / English)
✅ Language-safe section headers    (English always, content in selected language)
✅ Strategic framing for minor      (developmental / family-centered mode)
✅ Timing fallback mode             (when no windows, safe language guidance)
✅ Business-specific analysis block (_format_business_analysis)
✅ Mercury karaka block             (contracts, documentation)
✅ Unified sub-prompt signatures    (question, ad, raw, language, kwargs)
✅ _get_output_format() shared      (avoids duplication, timing-aware)
✅ Full parity with PropertyLegal / Career / Finance prompt builder patterns

Weightage:
- Vedic Analysis: 100% (no KP in this domain)
- Timing: BEST + NEAREST windows shown only when is_timing_query and not minor

Compatible with LegalBusinessDisputeEvaluator v2.0:
- legal_business_business_analysis   (NEW in v2.0)
- legal_business_outcome_analysis
- legal_business_duration_analysis
- legal_business_risk_analysis
- legal_business_suitability_matrix  (NEW in v2.0)
- legal_business_timing_windows      (NEW in v2.0)
- legal_business_house_lords
- legal_business_house_aspects
- lagna_info                         (NEW in v2.0)
- legal_business_current_dasha       (NEW in v2.0)
- legal_business_dasha_timeline      (NEW in v2.0)
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

DOMAIN_PREFIX = "legal_business"


class LegalBusinessDisputePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Legal → Legal Issue in Business
    v2.0 – Full feature parity with Property/Career/Finance builders
    """

    domain   = "Legal"
    subtopic = "Legal Issue in Business"

    # ══════════════════════════════════════════════════════════════
    # MINOR DETECTION  [NEW - matches Career/Property pattern]
    # ══════════════════════════════════════════════════════════════
    def _detect_minor(self, dob: Optional[str]) -> bool:
        """
        Detect if person is currently under 18.
        Based on current date vs DOB.
        """
        if not dob:
            return False
        try:
            today   = datetime.now()
            dob_dt  = datetime.strptime(dob, "%d/%m/%Y")
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
        """Get language instruction based on user selection."""
        try:
            if hasattr(self, "get_language_instruction"):
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
        """
        Get example content in the selected language.
        Section headers are ALWAYS English for parser compatibility.
        Content examples are language-specific.
        """
        examples = {
            "Hindi": {
                "6th_house":    "षष्ठ भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि मुकदमेबाजी में आपकी क्षमता...",
                "7th_house":    "सप्तम भाव के स्वामी [planet] की स्थिति विरोधी पक्ष की शक्ति का संकेत देती है...",
                "9th_house":    "नवम भाव के स्वामी [planet] की स्थिति न्याय और कानूनी कार्यवाही पर प्रकाश डालती है...",
                "11th_house":   "एकादश भाव की स्थिति विजय और लाभ की संभावना को दर्शाती है...",
                "mercury":      "बुध (अनुबंध कारक) की स्थिति कागजात, साक्ष्य और व्यावसायिक संचार को प्रभावित करती है...",
                "jupiter":      "बृहस्पति की स्थिति न्याय और कानूनी मामलों में शुभता का संकेत देती है...",
                "saturn":       "शनि की स्थिति कानूनी कार्यवाही में विलंब का संकेत दे सकती है...",
                "biz_strong":   "आपकी व्यावसायिक कानूनी स्थिति अपेक्षाकृत मजबूत दिखती है।",
                "biz_weak":     "व्यावसायिक विवाद में सावधानी और सक्रियता आवश्यक है।",
                "outcome_favorable":   "परिणाम आपके पक्ष में होने की अधिक संभावना है।",
                "outcome_unfavorable": "कानूनी मामले में कुछ चुनौतियां हो सकती हैं, सतर्क रहें।",
                "duration_short": "मामला अपेक्षाकृत जल्दी निपट सकता है।",
                "duration_long":  "कानूनी प्रक्रिया में पर्याप्त समय लग सकता है, धैर्य आवश्यक है।",
                "risk_high":  "जोखिम का स्तर अधिक है – तत्काल सावधानी और कानूनी परामर्श आवश्यक है।",
                "risk_low":   "जोखिम का स्तर अपेक्षाकृत कम है।",
                "tell_client":       "TELL CLIENT",
                "biz_outlook":       "व्यावसायिक कानूनी स्थिति",
                "outcome_outlook":   "परिणाम संभावना",
                "duration_outlook":  "अवधि अनुमान",
                "risk_outlook":      "जोखिम विश्लेषण",
            },
            "Hinglish": {
                "6th_house":    "6th house ke swami [planet] [house] bhav mein [sign] mein hain. Iska matlab hai aapki litigation capacity...",
                "7th_house":    "7th house ke swami [planet] ki position opposing party ki takat dikhati hai...",
                "9th_house":    "9th house ka analysis nyay aur legal proceedings ke baare mein bata ta hai...",
                "11th_house":   "11th house ki strength victory aur gains ki sambhavna dikhati hai...",
                "mercury":      "Budh (contract karaka) ki position documents, evidence aur business communication ko affect karta hai...",
                "jupiter":      "Jupiter ki position justice aur legal matters mein shubhata ka sanket deti hai...",
                "saturn":       "Shani ki position legal proceedings mein delay indicate kar sakti hai...",
                "biz_strong":   "Aapki business legal position relatively strong lagti hai.",
                "biz_weak":     "Business dispute mein savdhani aur sariayata zaruri hai.",
                "outcome_favorable":   "Result aapke paks mein hone ki zyada sambhavna hai.",
                "outcome_unfavorable": "Legal matter mein kuch challenges ho sakte hain, alert rahein.",
                "duration_short": "Case relatively jaldi resolve ho sakta hai.",
                "duration_long":  "Legal process mein kaafi time lag sakta hai, patience rakhen.",
                "risk_high":  "Risk level zyada hai – turant savdhani aur legal advice zaruri hai.",
                "risk_low":   "Risk level relatively kam hai.",
                "tell_client":       "TELL CLIENT",
                "biz_outlook":       "Business Legal Status",
                "outcome_outlook":   "Outcome Sambhavna",
                "duration_outlook":  "Duration Estimate",
                "risk_outlook":      "Risk Analysis",
            },
            "English": {
                "6th_house":    "The lord of the 6th house, [planet], placed in [house] in [sign], indicates your capacity for litigation...",
                "7th_house":    "The lord of the 7th house reflects the strength of the opposing party in this business dispute...",
                "9th_house":    "The 9th house analysis sheds light on the prospects for justice and legal proceedings...",
                "11th_house":   "The strength of the 11th house indicates the likelihood of victory and favorable gains...",
                "mercury":      "Mercury (karaka for contracts and documentation) influences your evidence, agreements, and communication...",
                "jupiter":      "Jupiter's position indicates auspiciousness in justice and legal matters...",
                "saturn":       "Saturn's placement may indicate delays in legal proceedings...",
                "biz_strong":   "Your business legal position appears relatively strong.",
                "biz_weak":     "Caution and proactive action are necessary in this business dispute.",
                "outcome_favorable":   "The outcome is likely to be in your favor.",
                "outcome_unfavorable": "There may be some challenges in the legal matter – stay vigilant.",
                "duration_short": "The case may be resolved relatively quickly.",
                "duration_long":  "The legal process may take considerable time – patience is essential.",
                "risk_high":  "Risk level is elevated – immediate caution and legal counsel are strongly advised.",
                "risk_low":   "Risk level is relatively low.",
                "tell_client":       "TELL CLIENT",
                "biz_outlook":       "Business Legal Strength",
                "outcome_outlook":   "Outcome Prospects",
                "duration_outlook":  "Duration Estimate",
                "risk_outlook":      "Risk Analysis",
            },
        }
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get analysis paragraph starters in selected language."""
        return {
            "Hindi":    {"vedic": "वैदिक ज्योतिष के अनुसार,"},
            "Hinglish": {"vedic": "Vedic jyotish ke anusar,"},
            "English":  {"vedic": "According to Vedic astrology,"},
        }.get(language, {"vedic": "According to Vedic astrology,"})

    # ══════════════════════════════════════════════════════════════
    # SYSTEM PROMPT
    # ══════════════════════════════════════════════════════════════
    def build_system_prompt(self, language: str = "English") -> str:
        example_6th = self._get_example_text(language, "6th_house")

        return f"""You are an expert Vedic astrologer specializing in legal matters, business disputes, and partnership conflicts.

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
   - Never guarantee legal victory or defeat
   - Always present as "indications" and "tendencies"
   - Legal outcomes depend on many factors beyond astrology

   FORBIDDEN CONCEPTS – do NOT use:
   - divine grace, karmic protection, cosmic shielding, planetary protection from penalties
   Replace with: "may reduce severity", "does not indicate an extreme outcome",
                 "indicates supportive tendencies", "requires careful handling"

4. RETROGRADE RULE
   - Retrograde planets do NOT automatically indicate weakness
   - Retrograde indicates delay, review, or reconsideration only
   - Do NOT use retrograde alone to predict loss or unfavorable judgment

5. LEGAL INFERENCE BOUNDARY (MANDATORY)
   Astrology may indicate tendencies or risk zones.
   It MUST NOT:
   - Declare fraud, forgery, contract breach, or illegality as fact
   - Assert business asset loss as certain
   - Predict court judgments or legal findings
   Use phrasing like:
   - "risk of dispute or misrepresentation"
   - "documentation needs verification"
   - "contractual risks require attention"

6. ASPECTS RULE (STRICT)
   - Aspects are SECONDARY modifiers only
   - If aspects conflict with evaluator scores, evaluator scores take priority
   Required phrasing: "This is a secondary influence" / "This does not override the core legal indicators"

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "6th Lord Mars in 10th house. Exalted. Benefic."
   ✅ "{example_6th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact → Explain what it means → Connect to practical legal strategy

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY SECTION

5. PROVIDE BALANCED, PROFESSIONAL GUIDANCE
   - Do NOT equate a low score with guaranteed loss
   - Always combine strength with dignity, house, and benefic influence

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR LEGAL BUSINESS DISPUTES
═══════════════════════════════════════════════════════════════════════════════

- 1st:  Self, the native, your position in the dispute
- 2nd:  Business finances, assets, monetary stakes
- 3rd:  Contracts, agreements, communication (secondary)
- 6th:  Litigation, disputes, enemies, ability to fight
- 7th:  Opponent / partner in the legal dispute
- 8th:  Hidden matters, penalties, investigations, sudden events
- 9th:  Justice, legal proceedings, higher courts, dharma
- 10th: Business reputation, career impact, authority
- 11th: Victory, gains, favorable outcomes
- 12th: Losses, expenses, settlements, penalties

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Mercury: CONTRACTS, DOCUMENTATION, EVIDENCE (primary for business disputes)
- Jupiter: Law, justice, judges, dharma, favorable legal outcomes
- Saturn:  Delays, legal processes, karma, punishment
- Mars:    Aggression, conflict, litigation energy, fighting spirit
- Sun:     Government, authority, power, dealing with officials

FINAL SELF-CHECK (MANDATORY):
Before responding, verify:
- No forbidden legal or metaphysical claims are made
- Outcome language matches evaluator likelihood
- Retrograde is not used to predict loss
- Risks are framed as actionable concerns, not predictions
- Mercury's role as contracts karaka is addressed
If any rule is violated, revise the response.
"""

    # ══════════════════════════════════════════════════════════════
    # MINOR OVERRIDE BLOCK  [NEW - matches Property pattern]
    # ══════════════════════════════════════════════════════════════
    def _minor_override_block(self, dob: Optional[str]) -> str:
        """
        Returns a strict developmental-mode instruction block for minors.
        Business legal disputes are complex legal matters; minors should not
        be advised to personally pursue or manage litigation.
        """
        return f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob or 'Not provided'}
The person is currently under 18 years of age.

STRICT RULES FOR MINOR:
• Do NOT advise the minor to personally take legal action
• Do NOT predict business win/loss as if they are the primary litigant
• Do NOT recommend aggressive litigation strategies to the minor directly
• Frame all analysis in the context of the FAMILY's business situation

INTERPRETATION RULES:
• Describe the astrological indications for the family's business/legal position
• Offer guidance on what the family should do (not the minor personally)
• Focus on protective measures, document security, and long-term business outlook
• Timing windows (if present) apply to the FAMILY action, not the minor

TONE:
• Protective and family-centered
• Future-oriented (business interests secured for the minor's future)
• Supportive, not alarming
"""

    # ══════════════════════════════════════════════════════════════
    # LAGNA INFO FORMATTER  [NEW - matches Property/Career/Finance pattern]
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

        # Business-dispute personality mapping (adapted from Property pattern)
        personality_map = {
            "Sun":     "Authoritative, government-focused, seeks official channels in disputes",
            "Moon":    "Emotionally invested in the business, resolve may fluctuate",
            "Mars":    "Courageous, assertive, persistent fighter in legal and business battles",
            "Mercury": "Analytical, document-oriented, strong in evidence and contract arguments",
            "Jupiter": "Righteous, inclined toward fair settlement, respects legal process",
            "Venus":   "Prefers settlement or compromise, values business harmony over prolonged fight",
            "Saturn":  "Patient, methodical, prepared for long legal battles, endures well",
            "Rahu":    "Unconventional tactics, may pursue non-standard or aggressive legal avenues",
            "Ketu":    "Detached from business outcomes, may disengage or settle unexpectedly",
        }
        personality = personality_map.get(lord, "Unique approach to business legal disputes")

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
            "• Lagna lord shows fundamental approach to the business legal fight",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS FORMATTER  [NEW - matches Property/Finance/Career]
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
                "Let the person choose based on urgency of their business situation.",
                "",
            ]

            if best:
                lines += [
                    "╔═══════════════════════════════════════════════════╗",
                    "║  🏆 BEST WINDOW (Highest Astrological Score)      ║",
                    "╚═══════════════════════════════════════════════════╝",
                    "",
                    f"  Dasha:        {best.get('dasha', 'N/A')}",
                    f"  Period:       {best.get('start', 'N/A')} to {best.get('end', 'N/A')}",
                    f"  Score:        {best.get('final_score', 0):.1f}/100",
                    f"  Age at start: {best.get('age_at_start', 'N/A')} years",
                    "",
                    "  Why this is BEST:",
                    f"    • Maha Dasha score:  {best.get('score_maha', 0)}/10",
                    f"    • Antara Dasha score:{best.get('score_antara', 0)}/10",
                    f"    • Pratyantar score:  {best.get('score_paryantar', 0)}/10",
                    f"    • Transit support:   {best.get('transit_score', 0):.1f}%",
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
                    f"  Dasha:        {nearest.get('dasha', 'N/A')}",
                    f"  Period:       {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}",
                    f"  Score:        {nearest.get('final_score', 0):.1f}/100",
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
    # SUITABILITY MATRIX FORMATTER  [NEW - matches Property pattern]
    # ══════════════════════════════════════════════════════════════
    def _format_suitability_matrix(self, matrix: Dict) -> str:
        """Format business legal strategy suitability matrix."""
        if not matrix:
            return ""

        lines = [
            "═══════════════════════════════════════════════════════",
            "📊 BUSINESS LEGAL STRATEGY MATRIX",
            "═══════════════════════════════════════════════════════",
            "",
            "Based on Vedic analysis of business strength, outcome, duration and risk:",
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
            if len(reasoning) > 65:
                reasoning = reasoning[:62] + "..."
            lines.append(f"| {marker} {strategy} | {rating} | {reasoning} |")

        lines += [
            "",
            "⚠️ Use this matrix to guide strategy recommendation.",
            "   HIGH = strongly recommended, MODERATE = viable, LOW = generally not advised.",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # CURRENT DASHA FORMATTER  [NEW - matches Property pattern]
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
            parts     = dasha_name.replace(">", "-").replace("/", "-").split("-")
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted  = " > ".join(full_names) if full_names else dasha_name

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
    # DASHA TIMELINE FORMATTER  [NEW - matches Property pattern]
    # ══════════════════════════════════════════════════════════════
    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        """Format dasha timeline (current → 10Y future) for the prompt."""
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
                "DASHA TIMELINE (For Business Case Planning)",
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
                    dr     = d.get("date_range", {})
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parse(d.get('dasha_name',''))}")
                    lines.append(f"     {dr.get('start','')} to {dr.get('end','')}")
                lines.append("")

            lines += [
                "═══════════════════════════════════════════════════════",
                "BUSINESS CASE DASHA GUIDELINES:",
                "• Jupiter/Sun dashas  → favorable for legal justice and authority",
                "• Saturn dashas       → delays but eventual stability",
                "• Mars dashas         → aggressive fighting energy, assertive action",
                "• Mercury dashas      → good for documentation, contracts, negotiation",
                "• Rahu dashas         → unexpected turns, verify all documents carefully",
                "• Ketu dashas         → detachment; may lead to sudden settlement",
                "═══════════════════════════════════════════════════════",
            ]
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # EVALUATOR DATA FORMATTERS
    # ══════════════════════════════════════════════════════════════
    def _format_business_analysis(self, additional_data: Dict) -> str:
        """Format business-specific analysis for prompt. [NEW in v2.0]"""
        if not additional_data:
            return ""
        biz = additional_data.get(f"{DOMAIN_PREFIX}_business_analysis", {})
        if not biz:
            return ""

        lines = ["BUSINESS LEGAL ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Business Legal Strength: {biz.get('business_legal_strength', 'MODERATE')}")
        lines.append(f"• Business Score: {biz.get('business_score', 50)}/100")
        lines.append(f"• Mercury (Contracts Karaka): {biz.get('mercury_strength', 'MODERATE')}")
        lines.append(f"• Reputation at Risk: {biz.get('reputation_at_risk', False)}")
        lines.append(f"• Opponent Stronger: {biz.get('opponent_stronger', False)}")

        for label, key, icon in [
            ("Business Favorable Factors",   "favorable_factors",  "✅"),
            ("Business Challenging Factors", "unfavorable_factors", "⚠️"),
            ("Business Hints",               "business_hints",      "💼"),
        ]:
            items = biz.get(key, [])
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
            ("Favorable Factors",  "favorable_factors",  "✅"),
            ("Challenging Factors","unfavorable_factors", "⚠️"),
            ("Strategic Hints",    "strategic_hints",     "💡"),
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
            ("Delay Factors",  "delay_factors",  "⏳"),
            ("Speed Factors",  "speed_factors",  "⚡"),
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
            ("Risk Factors",      "risk_factors",      "🚨"),
            ("Penalty Indicators","penalty_indicators", "💰"),
            ("Areas of Concern",  "areas_of_concern",  "⚠️"),
            ("Mitigation Hints",  "mitigation_hints",  "🛡️"),
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

        lines          = ["HOUSE LORDS DATA:"]
        business_houses = {1, 2, 3, 6, 7, 8, 9, 10, 11, 12}

        for house_num in sorted(house_lords.keys()):
            if house_num not in business_houses:
                continue
            info = house_lords.get(house_num, {})
            if not info:
                continue

            lord       = info.get("lord", "N/A")
            lord_house = info.get("lord_in_house", "N/A")
            lord_sign  = info.get("lord_in_sign", "N/A")
            dignity    = info.get("lord_dignity", "N/A")
            strength   = info.get("lord_strength_score", 0)
            conditions = []
            if info.get("lord_is_combust"):
                conditions.append("Combust")
            if info.get("lord_is_retrograde"):
                conditions.append("Retrograde")
            cond_str = ", ".join(conditions) if conditions else "Normal"
            planets  = ", ".join(info.get("planets_in_house", [])) or "None"
            # Mark litigation house with star
            prefix = "★" if house_num == 6 else "•"
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
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            if benefic or malefic:
                prefix = "★" if house_num == 6 else "•"
                lines.append(
                    f"{prefix} H{house_num}: "
                    f"Benefic={', '.join(benefic) or 'None'} | "
                    f"Malefic={', '.join(malefic) or 'None'}"
                )

        return "\n".join(lines) if len(lines) > 1 else ""

    # ══════════════════════════════════════════════════════════════
    # CONVENIENCE GETTERS  (aligned with evaluator v2.0 keys)
    # ══════════════════════════════════════════════════════════════
    def _get_business_strength(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_business_analysis") or {}).get("business_legal_strength", "MODERATE")

    def _get_business_score(self, ad: Dict) -> int:
        return (ad.get(f"{DOMAIN_PREFIX}_business_analysis") or {}).get("business_score", 50)

    def _get_mercury_strength(self, ad: Dict) -> str:
        return (ad.get(f"{DOMAIN_PREFIX}_business_analysis") or {}).get("mercury_strength", "MODERATE")

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
    # MAIN ROUTING  [UPDATED - minor detection + timing route]
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

            # ── Minor detection (global, same as Property/Career builder) ──
            dob      = kwargs.get("dob")
            is_minor = self._detect_minor(dob)
            kwargs["is_minor"] = is_minor
            logger.warning(f"[LEGAL_BUSINESS] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

            logger.info(f"Building prompt | sub: {sub_subdomain} | lang: {language} | minor: {is_minor}")

            # ── Route by sub_subdomain ──────────────────────────────────────
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
    # OUTPUT FORMAT GENERATOR  [NEW - shared, timing-aware]
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
        Section headers always in English; labels are language-specific.
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
- Why favorable: [explain dasha lords + business legal significations]
- Trade-off: May be further in future

⏰ NEAREST WINDOW:
- Period: [exact start] to [exact end]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Sooner but not absolute best

👤 CHOICE FOR PERSON:
Choose BEST if: Can wait, want optimal dasha support
Choose NEAREST if: Urgent business situation, needs to act sooner

If BEST = NEAREST: "🎯 IDEAL – same window! Act during this period."
"""

        return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT ENGLISH HEADERS SHOWN BELOW):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{labels.get('biz_outlook', 'Business Legal Strength')}: [label from evaluator]
{labels.get('outcome_outlook', 'Outcome Prospects')}: [label from evaluator]
{labels.get('duration_outlook', 'Duration Estimate')}: [label from evaluator]
{labels.get('risk_outlook', 'Risk Analysis')}: [label from evaluator]
Brief 3-4 line assessment in flowing prose.
NO technical astrological terms (houses, planets, yogas).
Evaluator categories (risk level, duration) may be referenced in neutral advisory language.

ASTROLOGICAL_ANALYSIS:
Write every section in FLOWING PARAGRAPHS – no bullet lists.

PARAGRAPH 1 – 6TH HOUSE & LITIGATION ABILITY:
Begin this paragraph with the Vedic starter provided.
Analyze 6th house (PRIMARY litigation house) with interpretation.

PARAGRAPH 2 – MERCURY (CONTRACTS KARAKA):
Mercury as contracts/evidence/documentation significator + practical meaning.

PARAGRAPH 3 – OPPONENT ANALYSIS:
1st house (self) vs 7th house (opponent) – relative strength comparison.

PARAGRAPH 4 – JUSTICE & VICTORY:
9th house (justice) + 11th house (victory) + Jupiter's role.

PARAGRAPH 5 – DURATION:
Saturn's influence on timeline, retrograde factors, realistic expectations.

PARAGRAPH 6 – RISK ASSESSMENT:
8th/12th lord analysis, Rahu influence.
Frame as actionable concerns, NOT legal predictions.

PARAGRAPH 7 – STRATEGY:
Actionable recommendations based on full chart picture.
Reference the strategy matrix to justify approach.
{timing_section}

SUMMARY:
{labels.get('tell_client', 'TELL CLIENT')}: "[Business strength + Outcome + Duration + Key risk + Primary action]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Remedy 1 (6th house / litigation strengthening)
- Remedy 2 (Mercury for contracts and documentation if weak)
- Remedy 3 (Jupiter for justice if needed)

REMEDIES_GENERAL:
- Consult qualified business/commercial lawyer immediately
- Organize all contracts, agreements, and correspondence
- Secure all original business documents safely
- Maintain professional conduct throughout proceedings
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
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor       = kwargs.get("is_minor", False)
        dob            = kwargs.get("dob")
        current_dasha  = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        # Evaluator values
        bs  = self._get_business_strength(additional_data)
        bsc = self._get_business_score(additional_data)
        mc  = self._get_mercury_strength(additional_data)
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
        biz_block      = self._format_business_analysis(additional_data)
        out_block      = self._format_outcome_analysis(additional_data)
        dur_block      = self._format_duration_analysis(additional_data)
        risk_block     = self._format_risk_analysis(additional_data)
        lords_block    = self._format_house_lords(additional_data)
        aspects_block  = self._format_house_aspects(additional_data)

        minor_block  = self._minor_override_block(dob) if is_minor else ""
        risk_warning = (
            "\n⚠️ HIGH RISK INDICATORS DETECTED – emphasize immediate legal counsel.\n"
            if rl in ["HIGH", "VERY_HIGH"] else ""
        )

        output_format = self._get_output_format(language, has_timing, "general", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: BUSINESS / PARTNERSHIP LEGAL DISPUTE – GENERAL ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Business Legal Strength: {bs} ({bsc}/100)
Mercury (Contracts Karaka): {mc}
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

{biz_block}

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
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        starters  = self._get_analysis_starters(language)
        lbl       = {k: self._get_example_text(language, k) for k in [
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor       = kwargs.get("is_minor", False)
        dob            = kwargs.get("dob")
        current_dasha  = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        bs = self._get_business_strength(additional_data)
        ol = self._get_outcome_likelihood(additional_data)
        dc = self._get_duration_category(additional_data)
        rl = self._get_risk_level(additional_data)

        timing_data    = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing     = timing_data.get("has_timing", False) if not is_minor else False
        timing_block   = self._format_timing_windows(timing_data) if has_timing else ""
        dasha_block    = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        lagna_block    = self._format_lagna_info(additional_data.get("lagna_info"))
        lords_block    = self._format_house_lords(additional_data)
        aspects_block  = self._format_house_aspects(additional_data)
        biz_block      = self._format_business_analysis(additional_data)
        out_block      = self._format_outcome_analysis(additional_data)

        minor_block = self._minor_override_block(dob) if is_minor else ""

        # Fallback when no timing windows exist
        fallback_timing_note = ""
        if not has_timing:
            fallback_timing_note = """
⚠️ TIMING FALLBACK MODE (No structured timing windows available)

FORBIDDEN phrases:
• "You will win the case in..."
• "Settlement will happen in..."
• "Business dispute will resolve in..."

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
QUERY: BUSINESS LEGAL CASE TIMING ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Business Legal Strength: {bs}
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

{biz_block}

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
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        bs  = self._get_business_strength(additional_data)
        mc  = self._get_mercury_strength(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        os_ = self._get_outcome_score(additional_data)

        timing_data  = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing   = timing_data.get("has_timing", False) if not is_minor else False
        timing_block = self._format_timing_windows(timing_data) if has_timing else ""

        biz_block    = self._format_business_analysis(additional_data)
        out_block    = self._format_outcome_analysis(additional_data)
        lords_block  = self._format_house_lords(additional_data)
        asp_block    = self._format_house_aspects(additional_data)
        lagna_block  = self._format_lagna_info(additional_data.get("lagna_info"))
        matrix_block = self._format_suitability_matrix(additional_data.get(f"{DOMAIN_PREFIX}_suitability_matrix", {}))

        minor_block  = self._minor_override_block(dob) if is_minor else ""
        outcome_text = (
            self._get_example_text(language, "outcome_favorable")
            if os_ >= 60
            else self._get_example_text(language, "outcome_unfavorable")
        )

        output_format = self._get_output_format(language, has_timing, "outcome", lbl)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: BUSINESS LEGAL OUTCOME ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Business Legal Strength: {bs}
Mercury (Contracts Karaka): {mc}
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

{biz_block}

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
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        dc          = self._get_duration_category(additional_data)
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
QUERY: BUSINESS LEGAL CASE DURATION / TIMELINE ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Duration Category: {dc}
═══════════════════════════════════════════════════════════════════════════════

NOTE: Business and partnership legal disputes can be lengthy due to contract
interpretation, documentation challenges, multiple hearings, arbitration
procedures, and appellate stages. Set realistic expectations.

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

PARAGRAPH 1 – SATURN & TIME: Saturn's placement + meaning for business case timeline.
PARAGRAPH 2 – DELAY FACTORS: Retrograde planets, Rahu/Ketu, 6th/7th lord retrograde.
PARAGRAPH 3 – SPEED FACTORS: Mercury's role, benefic aspects, expediting influences.
PARAGRAPH 4 – REALISTIC TIMELINE: Expected phases and timeframes.
PARAGRAPH 5 – STRATEGY: When to push, when to wait, optimal negotiation windows.

SUMMARY:
{lbl['tell_client']}: "[Duration + Key delay factor + Strategic patience guidance]"

REMEDIES_ASTROLOGICAL:
- Saturn remedy if delays prominent
- Mercury remedy for smoother documentation and proceedings

REMEDIES_GENERAL:
- Plan finances for indicated timeline
- Keep all business documents organized and accessible
- Regular follow-up with business lawyer
- Consider mediation/arbitration to reduce timeline
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
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        bs  = self._get_business_strength(additional_data)
        rl  = self._get_risk_level(additional_data)
        rs  = self._get_risk_score(additional_data)

        biz_block   = self._format_business_analysis(additional_data)
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
QUERY: BUSINESS LEGAL RISK & PENALTY ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Business Legal Strength: {bs}
Risk Level: {rl} ({rs}/100)
═══════════════════════════════════════════════════════════════════════════════

SENSITIVITY NOTE: Business disputes involve financial stakes and reputation.
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

{biz_block}

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

PARAGRAPH 1 – 8TH & 12TH HOUSE: Hidden penalties, losses, and expenses.
PARAGRAPH 2 – FINANCIAL RISK: 2nd house, business assets under threat.
PARAGRAPH 3 – REPUTATION RISK: 10th house afflictions, professional standing.
PARAGRAPH 4 – OPPONENT THREAT: 7th house (opponent strength) + Mars influence.
PARAGRAPH 5 – PROTECTIVE FACTORS: Jupiter's grace on 9th, benefic influences.
PARAGRAPH 6 – MITIGATION ACTION PLAN: Priority steps to protect business interests.

SUMMARY:
{lbl['tell_client']}: "[Risk level + Primary business concern + Immediate action]"

REMEDIES_ASTROLOGICAL:
- Protection remedy (Hanuman, Baglamukhi for victory over opponents)
- 8th/12th house affliction remedies
- Reputation protection (Sun / 10th house remedy)

REMEDIES_GENERAL:
- IMMEDIATE: Consult experienced business/commercial lawyer
- Secure all contracts, agreements, and correspondence
- Document all transactions and communications carefully
- Consider proactive settlement if risk indicators are HIGH
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
            "tell_client", "biz_outlook", "outcome_outlook",
            "duration_outlook", "risk_outlook"
        ]}

        is_minor = kwargs.get("is_minor", False)
        dob      = kwargs.get("dob")

        bs  = self._get_business_strength(additional_data)
        mc  = self._get_mercury_strength(additional_data)
        ol  = self._get_outcome_likelihood(additional_data)
        rl  = self._get_risk_level(additional_data)

        lords_block = self._format_house_lords(additional_data)
        lagna_block = self._format_lagna_info(additional_data.get("lagna_info"))
        biz_block   = self._format_business_analysis(additional_data)

        current_dasha = kwargs.get("current_dasha")
        dasha_block   = self._format_current_dasha(current_dasha)

        minor_block = self._minor_override_block(dob) if is_minor else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REMEDIES FOR BUSINESS LEGAL SUCCESS
Current Date: {today_str}
Weightage: VEDIC 100%
Business Legal Strength: {bs}
Mercury (Contracts Karaka): {mc}
Outcome Likelihood: {ol}
Risk Level: {rl}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{lagna_block}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{biz_block}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_block or "House lords data not available."}

{dasha_block}

{raw or ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR BUSINESS LEGAL MATTERS:
═══════════════════════════════════════════════════════════════════════════════

Recommend MAXIMUM 3 astrological remedies linked to the most affected planet only.

MERCURY WEAK (Contracts):  Green Emerald (with caution), Wednesday fasts, Ganesh worship
JUPITER WEAK (Justice):    Yellow sapphire, Thursday fasts, Vishnu worship
SATURN AFFLICTING:         Blue sapphire (with caution), Saturday fasts, Hanuman worship
MARS WEAK (Fight energy):  Red coral, Tuesday fasts, Hanuman/Kartikeya worship
SUN WEAK (Authority):      Ruby, Sunday fasts, Surya worship
6th LORD WEAK:             Strengthen as per that planet's remedy
9th LORD WEAK (Justice):   Jupiter remedies

Traditional Remedies for Business Legal Success:
- Baglamukhi Puja for victory over opponents and legal enemies
- Hanuman Chalisa for strength and protection in legal battles
- Durga worship for overcoming obstacles and adversaries
- Ganesh Puja for removing procedural obstacles
- Vishnu Sahasranama for dharmic support and justice

Business-specific practices:
- Keep Kuber Yantra in business premises for financial protection
- Perform Saraswati puja before important contract signings
- Recite Mercury mantra on Wednesdays: "Om Budhaya Namah"
═══════════════════════════════════════════════════════════════════════════════

VEDIC ANALYSIS STARTER (BEGIN PARAGRAPH 1 WITH THIS):
"{starters['vedic']}"

OUTPUT FORMAT:

GENERAL_ANSWER:
What astrological challenges exist and how remedies may help.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in flowing paragraphs:

PARAGRAPH 1 – WEAK PLANETS IDENTIFIED: Mercury condition, 6th lord condition,
              Jupiter condition — explain what each means for the business case.
PARAGRAPH 2 – PRIMARY REMEDY: Most important remedy + detailed instructions.
PARAGRAPH 3 – MERCURY REMEDY (CONTRACTS KARAKA): If Mercury weak, specific remedy + timing.
PARAGRAPH 4 – SUPPORTING REMEDIES: Jupiter for justice, Saturn for delays.
PARAGRAPH 5 – TIMING: Best days, duration, expected supportive effects.

SUMMARY:
{lbl['tell_client']}: "[Priority remedy + Practice schedule + Business legal benefit]"

REMEDIES_ASTROLOGICAL:
1. [Baglamukhi/6th house remedy with detailed instructions]
2. [Mercury remedy if contracts karaka is weak]
3. [Jupiter remedy for justice if needed]

REMEDIES_GENERAL:
- Consult qualified business/commercial lawyer FIRST
- Organize and secure all business documents, contracts, agreements
- Maintain ethical conduct throughout dispute
- Document all business communications carefully
- Practice patience – business legal cases take time
═══════════════════════════════════════════════════════════════════════════════
"""

    # ══════════════════════════════════════════════════════════════
    # FALLBACK PROMPT
    # ══════════════════════════════════════════════════════════════
    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in business legal matters,
partnership disputes, and commercial conflicts.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
Focus on 6th house (litigation), Mercury (contracts karaka), and
1st vs 7th house comparison (self vs opponent).
Include practical strategic guidance.
End with a clear actionable statement.
Always recommend consulting qualified legal professionals.
"""
"""
Family Legal Issue – LLM Prompts v1.0

Specialized prompt builder for family legal disputes, court cases, and litigation
related queries using traditional Vedic astrology principles.

✔ Output language based on user selection (not hardcoded)
✔ If KP points have no relevant info → Only Vedic analysis
✔ Astrological analysis: VEDIC FIRST, then KP
✔ Language-specific examples in SELECTED language
✔ Compatible with FamilyLegalIssueEvaluator v1.0
✔ Minor detection (age-aware analysis)
✔ Lagna lord formatting
✔ Dynamic language instruction

Weightage:
- NON-TIMING: Vedic 85% + KP Facts 15% (No specific Dasha timing)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from FamilyLegalIssueEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["family_legal_house_config"] = {...}
additional_data["family_legal_house_lords"] = {...}
additional_data["family_legal_house_aspects"] = {...}
additional_data["family_legal_outcome_analysis"] = {...}
additional_data["family_legal_duration_analysis"] = {...}
additional_data["family_legal_risks_analysis"] = {...}
additional_data["family_legal_timing_hints"] = {...}
additional_data["family_legal_timing_windows"] = {...}
additional_data["family_legal_analysis_summary"] = {...}
additional_data["lagna_info"] = {...}
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import re

from app.domains.base import (
    BasePromptBuilder,
    QueryMeta,
    TimingWindow,
    QueryType,
    EventPolarity,
    InterpretationGoal
)

logger = logging.getLogger(__name__)

DOMAIN_PREFIX = "family_legal"


class FamilyLegalIssuePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Family Legal Issue → Family Legal Dispute
    v1.0 - Initial version with full Vedic analysis support
    """

    domain = "Family Legal Issue"
    subtopic = "Family Legal Issue"

    # ==========================================================================
    # LANGUAGE INSTRUCTION (Dynamic - matches doc 2/3 pattern)
    # ==========================================================================
    def get_language_instruction(self, language: str) -> str:
        """Get language instruction for LLM"""
        if language.lower() == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, houses, aspects).
Example: "आपके मुकदमे में **6th house** के स्वामी **Mars** मजबूत हैं।"
Example: "न्याय के लिए **9th house lord** की स्थिति अनुकूल है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke case mein 6th house ka lord Mars strong hai."
Example: "9th house ki position favorable hai justice ke liye."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear English.
Keep technical terms clear and explain if needed.
"""

    # Kept for backward compatibility - delegates to get_language_instruction
    def _get_language_instruction_safe(self, language: str) -> str:
        """Get language instruction based on user selection"""
        try:
            if hasattr(self, 'get_language_instruction'):
                return self.get_language_instruction(language)
        except Exception:
            pass

        if language == "Hindi":
            return "IMPORTANT: Respond ONLY in Hindi (Devanagari script). Use Hindi for all analysis, interpretations, and recommendations."
        elif language == "English":
            return "IMPORTANT: Respond ONLY in English. Use English for all analysis, interpretations, and recommendations."
        else:
            return f"IMPORTANT: Respond in {language}. Use {language} for all analysis, interpretations, and recommendations."

    def _get_example_text(self, language: str, example_type: str) -> str:
        """Get example text in the selected language"""

        examples = {
            "Hindi": {
                "6th_house": "छठे भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि मुकदमेबाजी और विवादों के लिए...",
                "7th_house": "सातवें भाव के स्वामी [planet] [house] भाव में स्थित हैं। यह प्रतिद्वंद्वी की स्थिति को दर्शाता है...",
                "8th_house": "आठवें भाव के स्वामी [planet] [position] में होने से अचानक घटनाएं या जुर्माने की संभावना...",
                "9th_house": "नवम भाव [position] में होने से न्याय और उच्च न्यायालय में...",
                "saturn": "शनि न्याय और कर्म का कारक है। शनि [position] में होने से देरी लेकिन निष्पक्ष परिणाम...",
                "jupiter": "बृहस्पति धर्म और न्याय का कारक है। बृहस्पति [position] में होने से न्यायिक सुरक्षा...",
                "general_answer": "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary": "सारांश",
                "remedies": "उपाय",
                "tell_client": "ग्राहक को बताएं",
                "vedic_start": "वैदिक ज्योतिष के अनुसार,",
                "kp_start": "KP प्रणाली के अनुसार,",
                "outcome_favorable": "कुंडली में विजय के संकेत हैं।",
                "outcome_challenging": "कुंडली में कुछ चुनौतियां हैं। सावधानी और अच्छे वकील की जरूरत है।",
                "duration_long": "मामला लंबा चल सकता है। धैर्य रखें।",
                "duration_short": "मामले का जल्द निपटारा संभव है।",
                "risk_high": "जोखिम अधिक है। समझौते पर विचार करें।",
                "risk_low": "जोखिम कम है। आगे बढ़ सकते हैं।"
            },
            "English": {
                "6th_house": "The lord of 6th house [planet] is placed in [house] house in [sign]. This means for litigation and disputes...",
                "7th_house": "The lord of 7th house [planet] is placed in [house] house. This indicates the opponent's position...",
                "8th_house": "The lord of 8th house [planet] being in [position] indicates sudden events or penalties...",
                "9th_house": "The 9th house [position] indicates for justice and higher courts...",
                "saturn": "Saturn is the karaka for justice and karma. Saturn being in [position] indicates delays but fair outcome...",
                "jupiter": "Jupiter is the karaka for dharma and justice. Jupiter being in [position] provides judicial protection...",
                "general_answer": "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary": "Summary",
                "remedies": "Remedies",
                "tell_client": "TELL CLIENT",
                "vedic_start": "According to Vedic astrology,",
                "kp_start": "According to KP astrology,",
                "outcome_favorable": "The chart shows indicators for victory.",
                "outcome_challenging": "There are some challenges in the chart. Caution and good legal counsel needed.",
                "duration_long": "The case may take a long time. Be patient.",
                "duration_short": "Quick resolution of the case is possible.",
                "risk_high": "Risk is high. Consider settlement.",
                "risk_low": "Risk is low. You may proceed."
            }
        }

        # Default to English if language not found
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get analysis paragraph starters in selected language"""
        return {
            "Hindi": {
                "vedic": "वैदिक ज्योतिष के अनुसार,",
                "kp": "KP प्रणाली के अनुसार,"
            },
            "English": {
                "vedic": "According to Vedic astrology,",
                "kp": "According to KP astrology,"
            }
        }.get(language, {
            "vedic": "According to Vedic astrology,",
            "kp": "According to KP astrology,"
        })

    # ==========================================================================
    # MINOR DETECTION (matches doc 3 pattern)
    # ==========================================================================
    def _detect_minor(self, dob: str, dasha_timeline: Dict = None) -> bool:
        """
        Detect if person is currently under 18.
        Minor logic based on CURRENT age only.
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
    # LAGNA LORD FORMATTING (matches doc 2/3 pattern)
    # ==========================================================================
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """
        Format lagna lord for legal personality analysis.
        Falls back to house 1 in house_lords_info if lagna_info not available.
        """
        # Try lagna_info first, then fall back to house 1 in house_lords_info
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign": info.get('house_sign', 'N/A'),
                "lagna_lord": info.get('lord', 'N/A'),
                "lagna_lord_house": info.get('lord_in_house'),
                "lagna_lord_sign": info.get('lord_in_sign', 'N/A'),
                "lagna_lord_degree": info.get('lord_degree', 0),
                "lagna_lord_dignity": info.get('lord_dignity', 'Unknown'),
            }

        if not lagna_info:
            return """
═══════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════

CRITICAL: Lagna information not provided.
Do NOT guess or invent lagna sign.
Do NOT mention lagna in your analysis.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════
"""

        lord = lagna_info.get('lagna_lord', 'N/A')
        lagna_sign = lagna_info.get('lagna_sign', 'N/A')
        lord_house = lagna_info.get('lagna_lord_house', 'N/A')
        lord_sign = lagna_info.get('lagna_lord_sign', 'N/A')
        dignity = lagna_info.get('lagna_lord_dignity', 'Unknown')
        degree = lagna_info.get('lagna_lord_degree', 0)

        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) – NATIVE'S OVERALL STRENGTH")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        if degree:
            lines.append(f"Degree: {degree:.2f}°")
        lines.append("")

        # Legal personality based on lagna lord
        legal_personality_map = {
            "Sun": {
                "trait": "Authority-seeking, confident, seeks recognition in disputes",
                "legal_approach": "Prefers direct confrontation; may do well in government or authority-related cases",
                "strength": "Strong willpower; does not back down easily"
            },
            "Moon": {
                "trait": "Emotionally driven, family-oriented, public-facing",
                "legal_approach": "May seek emotional resolution; family disputes deeply affect them",
                "strength": "Intuitive; good at reading opposing party's weaknesses"
            },
            "Mars": {
                "trait": "Aggressive, combative, impatient in disputes",
                "legal_approach": "Fights strongly; may escalate conflict; good for property battles",
                "strength": "High fighting energy; persistent in litigation"
            },
            "Mercury": {
                "trait": "Analytical, document-focused, communicative",
                "legal_approach": "Excels at paperwork, contracts, arguments; prefers negotiation",
                "strength": "Sharp mind; strong in court arguments and documentation"
            },
            "Jupiter": {
                "trait": "Ethical, dharma-oriented, seeks fair resolution",
                "legal_approach": "Prefers legal propriety; appeals to higher courts; benefits from wise counsel",
                "strength": "Moral authority; favorable in dharmic and family disputes"
            },
            "Venus": {
                "trait": "Compromise-seeking, diplomatic, desires harmony",
                "legal_approach": "Prefers settlement and mediation; good for civil cases",
                "strength": "Diplomatic skill; may reach favorable settlements"
            },
            "Saturn": {
                "trait": "Patient, disciplined, enduring",
                "legal_approach": "Long-haul fighter; handles delays well; thorough in approach",
                "strength": "Persistence; willing to wait for just outcome"
            },
            "Rahu": {
                "trait": "Unconventional, ambitious, may use unexpected tactics",
                "legal_approach": "May adopt unusual legal strategies; benefits from foreign or tech-related cases",
                "strength": "Resourceful; thinks outside the box in disputes"
            },
            "Ketu": {
                "trait": "Detached, spiritually inclined, may withdraw from disputes",
                "legal_approach": "May prefer to disengage; benefit in cases involving spiritual or hidden matters",
                "strength": "Can rise above conflict; intuitive about hidden enemies"
            }
        }

        lord_info = legal_personality_map.get(lord, {
            "trait": "Unique approach to legal matters",
            "legal_approach": "Depends on specific placement and dignity",
            "strength": "Individual style of handling disputes"
        })

        lines.append(f"Legal Personality: {lord_info['trait']}")
        lines.append(f"Approach to Disputes: {lord_info['legal_approach']}")
        lines.append(f"Core Strength: {lord_info['strength']}")
        lines.append("")

        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows the native's overall strength to fight the case")
        lines.append("• Use this to explain HOW the person approaches legal battles")
        lines.append("• Only ONE lagna – do NOT contradict or mention multiple lagnas")
        lines.append(f"✅ CORRECT: 'लग्न राशि: {lagna_sign}' (one lagna only)")
        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ==========================================================================
    # SYSTEM PROMPT (Language-dynamic)
    # ==========================================================================
    def build_system_prompt(self, language: str = "English", is_timing: bool = False) -> str:
        """Build system prompt with language-appropriate examples"""

        weightage_text = "NON-TIMING QUESTION: Vedic 85% + KP Facts 15% (No specific Dasha timing)"

        return f"""You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in legal matters, litigation, court cases, and family disputes.

**{weightage_text}**

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

3. NEVER GUARANTEE LEGAL OUTCOMES
   - Do NOT say "You WILL win" or "You WILL lose"
   - Use words like "indicates", "suggests", "tendency"
   - Court decisions depend on many non-astrological factors
   - Phrases like "will prevail", "will succeed", "will result in" are NOT allowed even with words like "suggests" or "indicates".


4. NEVER PROVIDE SPECIFIC LEGAL ADVICE
   - Do NOT advise on legal strategy
   - Do NOT interpret laws or judgments
   - ALWAYS recommend consulting a qualified lawyer

5. FACT → INTERPRETATION SEQUENCE (MANDATORY)
   - Each paragraph MUST follow this order:
     (a) Explicitly restate the exact data point from PRE-COMPUTED ANALYSIS
     (b) Then interpret what it means
   - Never interpret without first restating the data
   - Never list facts without interpretation

FORBIDDEN PHRASES AND CONCEPTS:
Do NOT use any wording implying:
- divine, karmic, cosmic, or judicial protection
- guaranteed fairness or justice
- inevitable victory or success

Examples to AVOID:
- divine protection
- judicial protection
- karmic shield
- justice will prevail
- protected from penalties

Use neutral alternatives only:
- "may offer some support"
- "does not indicate severe harm"
- "suggests moderation rather than extremes"

7. ASPECTS SAFETY RULE
   - If aspect influence seems unclear or weak, state it as "limited or indirect"
   - Do NOT overstate aspects unless explicitly strong and repeated
   Aspects are SECONDARY modifiers only.
   They MUST NOT be used as primary justification for:
    - outcome prediction
    - opponent weakness
    - penalty reduction
    If house lord analysis does not support a claim,
    aspects alone cannot justify it.




═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "6th Lord Mars in 10th house. Retrograde. Malefic."
   ✅ "The 6th house lord Mars is placed in the 10th house, which indicates that legal battles may involve authority figures or affect career. The native has strong fighting spirit..."

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for the legal question
   - Connect to the outcome

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

HARD CONSTRAINT (NON-NEGOTIABLE):
- If outcome_score ≤ 60:
  You MUST use ONLY one of:
  "uncertain", "mixed", or "moderately challenging"
- Words like "favorable", "highly favorable", "positive outcome"
  are STRICTLY FORBIDDEN in this case.


5. ANSWER THE ACTUAL QUESTION DIRECTLY

═══════════════════════════════════════════════════════════════════════════════
                    VEDIC FIRST, THEN KP
═══════════════════════════════════════════════════════════════════════════════

IMPORTANT: In Astrological Analysis section:
1. ALWAYS start with VEDIC analysis (PRIMARY)
2. THEN add KP analysis (SECONDARY) if relevant KP points exist
3. Never mix Vedic and KP reasoning in same paragraph

═══════════════════════════════════════════════════════════════════════════════
                    KEY LEGAL HOUSES
═══════════════════════════════════════════════════════════════════════════════

- 6th: Litigation, disputes, enemies, obstacles, legal battles (PRIMARY)
- 7th: Opponent, other party, contracts (PRIMARY)
- 8th: Penalties, fines, sudden events, hidden matters (PRIMARY)
- 9th: Justice, dharma, higher courts, appeals (PRIMARY)
- 1st: Self, native's strength to fight
- 4th: Family, property matters, domestic disputes
- 10th: Authority, judges, government, reputation
- 11th: Gains, favorable outcomes, success
- 12th: Losses, expenses, imprisonment, settlements

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS FOR LEGAL MATTERS
═══════════════════════════════════════════════════════════════════════════════

- Saturn: Justice and karma; often indicates delays, discipline, and consequences rather than rewards
- Jupiter: Dharma, judges, wisdom; may SUPPORT fairness when strong, but does not guarantee outcomes
- Mars: Fighting spirit, aggression, litigation energy, quick action
- Sun: Authority, government, power, judges
- Mercury: Documentation, contracts, communication, lawyers

═══════════════════════════════════════════════════════════════════════════════
                    LEGAL & ETHICAL DISCLAIMER
═══════════════════════════════════════════════════════════════════════════════

- Astrology shows TENDENCIES, not certainties
- Court outcomes depend on evidence, law, and legal representation
- ALWAYS recommend consulting a qualified lawyer
- Never discourage someone from seeking legal remedy if wronged
- Be sensitive - legal disputes are stressful for clients


FINAL SELF-CHECK (MANDATORY):
Before answering, verify:
- No forbidden phrases or concepts are used
- Outcome wording matches outcome_score
- No deterministic or guaranteed language exists
- Remedies are not linked to legal outcomes
If any rule is violated, revise the answer.

"""

    # ==========================================================================
    # HELPER: Format Outcome Analysis
    # ==========================================================================
    def _format_outcome_analysis(self, additional_data: Dict) -> str:
        """Format legal outcome analysis"""
        if not additional_data:
            return ""

        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        if not outcome:
            return ""

        lines = ["LEGAL OUTCOME ANALYSIS:"]

        prediction = outcome.get("outcome_prediction", "UNCERTAIN")
        score = outcome.get("score", 50)
        lines.append(f"⚖️ Prediction: {prediction} (Score: {score}/100)")

        favorable = outcome.get("favorable_factors", [])
        if favorable:
            lines.append("✅ Favorable Factors:")
            for f in favorable[:5]:
                lines.append(f"   • {f}")

        unfavorable = outcome.get("unfavorable_factors", [])
        if unfavorable:
            lines.append("❌ Unfavorable Factors:")
            for f in unfavorable[:5]:
                lines.append(f"   • {f}")

        victory = outcome.get("victory_indicators", [])
        if victory:
            lines.append("🏆 Victory Indicators:")
            for v in victory[:3]:
                lines.append(f"   • {v}")

        settlement = outcome.get("settlement_indicators", [])
        if settlement:
            lines.append("🤝 Settlement Indicators:")
            for s in settlement[:3]:
                lines.append(f"   • {s}")

        recommendations = outcome.get("recommendations", [])
        if recommendations:
            lines.append("💡 Recommendations:")
            for r in recommendations[:3]:
                lines.append(f"   • {r}")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Format Duration Analysis
    # ==========================================================================
    def _format_duration_analysis(self, additional_data: Dict) -> str:
        """Format case duration analysis"""
        if not additional_data:
            return ""

        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        if not duration:
            return ""

        lines = ["CASE DURATION ANALYSIS:"]

        estimate = duration.get("duration_estimate", "MODERATE")
        timeframe = duration.get("estimated_timeframe", "Unknown")
        score = duration.get("score", 50)
        lines.append(f"⏱️ Duration: {estimate} ({timeframe}) | Score: {score}/100")

        delay_factors = duration.get("delay_factors", [])
        if delay_factors:
            lines.append("⏳ Delay Factors:")
            for d in delay_factors[:4]:
                lines.append(f"   • {d}")

        quick_factors = duration.get("quick_resolution_factors", [])
        if quick_factors:
            lines.append("⚡ Quick Resolution Factors:")
            for q in quick_factors[:4]:
                lines.append(f"   • {q}")

        notes = duration.get("notes", [])
        if notes:
            for n in notes:
                lines.append(f"📝 Note: {n}")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Format Risks Analysis
    # ==========================================================================
    def _format_risks_analysis(self, additional_data: Dict) -> str:
        """Format risks and penalties analysis"""
        if not additional_data:
            return ""

        risks = additional_data.get(f"{DOMAIN_PREFIX}_risks_analysis", {})
        if not risks:
            return ""

        lines = ["RISKS AND PENALTIES ANALYSIS:"]

        risk_level = risks.get("risk_level", "LOW")
        risk_score = risks.get("risk_score", 20)
        lines.append(f"⚠️ Risk Level: {risk_level} (Score: {risk_score}/100)")

        risk_list = risks.get("risks", [])
        if risk_list:
            lines.append("🚨 Identified Risks:")
            for r in risk_list[:4]:
                lines.append(f"   • {r}")

        penalties = risks.get("potential_penalties", [])
        if penalties:
            lines.append("💰 Potential Penalties:")
            for p in penalties[:3]:
                lines.append(f"   • {p}")

        financial = risks.get("financial_risks", [])
        if financial:
            lines.append("💸 Financial Risks:")
            for f in financial[:3]:
                lines.append(f"   • {f}")

        protective = risks.get("protective_factors", [])
        if protective:
            lines.append("🛡️ Protective Factors:")
            for p in protective[:3]:
                lines.append(f"   • {p}")

        mitigation = risks.get("mitigation_strategies", [])
        if mitigation:
            lines.append("💡 Mitigation Strategies:")
            for m in mitigation[:3]:
                lines.append(f"   • {m}")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Format House Lords
    # ==========================================================================
    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = ["HOUSE LORDS DATA:"]

        # House meanings for legal context
        house_meanings = {
            1: "Self/Native's Strength",
            4: "Family/Property",
            6: "Litigation/Disputes",
            7: "Opponent/Other Party",
            8: "Penalties/Hidden Matters",
            9: "Justice/Higher Courts",
            10: "Authority/Judges",
            11: "Gains/Victory",
            12: "Losses/Expenses"
        }

        for house_num in sorted(house_lords.keys()):
            info = house_lords.get(house_num, {})
            if not info:
                continue

            lord = info.get('lord', 'N/A')
            lord_house = info.get('lord_in_house', 'N/A')
            lord_sign = info.get('lord_in_sign', 'N/A')
            dignity = info.get('lord_dignity', 'N/A')
            strength = info.get('lord_strength_score', 0)
            priority = info.get('priority', 'secondary')
            meaning = house_meanings.get(house_num, "General")

            conditions = []
            if info.get('lord_is_combust'):
                conditions.append("Combust")
            if info.get('lord_is_retrograde'):
                conditions.append("Retrograde")
            condition_str = ", ".join(conditions) if conditions else "Normal"

            planets = ", ".join(info.get('planets_in_house', [])) or "None"

            marker = "⭐" if priority == "primary" else "○"
            lines.append(f"{marker} H{house_num} ({meaning}): Lord {lord} in H{lord_house}/{lord_sign} | {dignity} | {condition_str} | Str:{strength}/100 | Planets:{planets}")

        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Format House Aspects
    # ==========================================================================
    def _format_house_aspects(self, additional_data: Dict) -> str:
        """Format aspects data concisely"""
        if not additional_data:
            return ""

        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        lines = ["ASPECTS DATA:"]

        # House meanings for legal context
        house_meanings = {
            1: "native's strength",
            4: "family/property",
            6: "litigation/disputes",
            7: "opponent",
            8: "penalties/fines",
            9: "justice/appeals",
            10: "authority/judges",
            11: "gains/victory",
            12: "losses/expenses"
        }

        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])

            if benefic or malefic:
                meaning = house_meanings.get(house_num, "legal matters")
                benefic_str = ", ".join(benefic) if benefic else "None"
                malefic_str = ", ".join(malefic) if malefic else "None"
                lines.append(f"• H{house_num} ({meaning}): Benefic={benefic_str} | Malefic={malefic_str}")

        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # HELPER: Format Timing Hints
    # ==========================================================================
    def _format_timing_hints(self, additional_data: Dict) -> str:
        """Format timing hints for legal matters"""
        if not additional_data:
            return ""

        hints = additional_data.get(f"{DOMAIN_PREFIX}_timing_hints", {})
        if not hints:
            return ""

        lines = ["AUSPICIOUS TIMING HINTS:"]

        best_days = hints.get("best_days", [])
        if best_days:
            lines.append("📅 Best Days:")
            for d in best_days[:4]:
                lines.append(f"   • {d}")

        avoid_days = hints.get("avoid_days", [])
        if avoid_days:
            lines.append("🚫 Avoid:")
            for d in avoid_days[:3]:
                lines.append(f"   • {d}")

        nakshatras = hints.get("best_nakshatras", [])
        if nakshatras:
            lines.append("⭐ Best Nakshatras:")
            for n in nakshatras[:3]:
                lines.append(f"   • {n}")

        general = hints.get("general_hints", [])
        if general:
            lines.append("💡 Specific Hints:")
            for g in general[:3]:
                lines.append(f"   • {g}")

        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # HELPER: Format Analysis Summary
    # ==========================================================================
    def _format_analysis_summary(self, additional_data: Dict) -> str:
        """Format the analysis summary"""
        if not additional_data:
            return ""

        summary = additional_data.get(f"{DOMAIN_PREFIX}_analysis_summary", {})
        if not summary:
            return ""

        lines = ["ANALYSIS SUMMARY:"]
        lines.append(f"• Outcome: {summary.get('outcome_prediction', 'N/A')} (Score: {summary.get('outcome_score', 0)}/100)")
        lines.append(f"• Duration: {summary.get('duration_estimate', 'N/A')} ({summary.get('duration_timeframe', 'N/A')})")
        lines.append(f"• Risk: {summary.get('risk_level', 'N/A')} (Score: {summary.get('risk_score', 0)}/100)")
        lines.append(f"• Houses Analyzed: {summary.get('total_houses_analyzed', 0)}")

        return "\n".join(lines)

    # ==========================================================================
    # MAIN ROUTING METHOD
    # ==========================================================================
    def build_analysis_prompt(
            self,
            question: str,
            technical_points: List[str],
            meta: QueryMeta,
            timing_windows: Optional[List[TimingWindow]] = None,
            language: str = "English",
            **kwargs
        ) -> str:
        """Main routing method - routes to appropriate specialized builder"""

        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.pop("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            # ----------------------------
            # GLOBAL MINOR DETECTION (matches doc 3 pattern)
            # ----------------------------
            dob = kwargs.get("dob")
            dasha_timeline = kwargs.get("dasha_timeline")
            is_minor = self._detect_minor(dob, dasha_timeline)
            kwargs["is_minor"] = is_minor

            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            logger.info(f"[FAMILY_LEGAL] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

            # Route based on sub_subdomain
            if "Family Legal Dispute" in sub_subdomain:
                return self._build_family_legal_dispute_prompt(question, additional_data, raw, language, **kwargs)

            else:
                # Default to family legal dispute prompt
                return self._build_family_legal_dispute_prompt(question, additional_data, raw, language, **kwargs)

        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # FALLBACK PROMPT
    # ==========================================================================
    def _build_fallback_prompt(self, question: str, language: str) -> str:
        """Fallback prompt if something fails"""
        lang_inst = self.get_language_instruction(language)

        return f"""
{lang_inst}

You are an expert Vedic astrologer. Answer the following family legal dispute related question.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear actionable statement.
ALWAYS recommend consulting a qualified lawyer for legal matters.
Be sensitive - legal disputes are stressful for clients.
"""

    # ==========================================================================
    # FAMILY LEGAL DISPUTE PROMPT
    # ==========================================================================
    def _build_family_legal_dispute_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Family Legal Dispute questions - Outcome, Duration, Risks, Penalties"""

        lang_inst = self.get_language_instruction(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")

        # Get formatted data
        outcome_data = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risks_data = self._format_risks_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        timing_hints = self._format_timing_hints(additional_data)
        summary_data = self._format_analysis_summary(additional_data)

        # Lagna lord block (matches doc 2/3 pattern)
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_info = additional_data.get("lagna_info", {})
        lagna_block = self._format_lagna_lord(lagna_info, house_lords_raw)

        # Minor override block (matches doc 3 pattern)
        if is_minor:
            minor_override = f"""
═══════════════════════════════════════════════════════════════════════════════
🚨 MINOR DETECTED – ADJUSTED ANALYSIS MODE
═══════════════════════════════════════════════════════════════════════════════

Person DOB: {dob}
Current age is under 18.

STRICT RULES FOR MINOR:
• Do NOT predict specific court outcomes for the minor directly
• Do NOT frame legal battles as the minor's personal responsibility
• Frame analysis as FAMILY SITUATION affecting a minor
• Focus on: family environment, parental situation, protective factors
• Emphasize: stability, protection, and long-term wellbeing
• If custody-related: focus on child's welfare indicators

TONE MUST BE:
• Protective and supportive
• Family-centered
• Sensitive to the minor's circumstances
• Future-building (not burden-placing)

This override is MANDATORY for this analysis.
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            minor_override = ""

        # Get language-specific labels
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        # Get example texts
        example_6th = self._get_example_text(language, "6th_house")
        example_7th = self._get_example_text(language, "7th_house")
        example_8th = self._get_example_text(language, "8th_house")
        example_9th = self._get_example_text(language, "9th_house")
        example_saturn = self._get_example_text(language, "saturn")
        example_jupiter = self._get_example_text(language, "jupiter")

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FAMILY LEGAL DISPUTE - OUTCOME, DURATION, RISKS & PENALTIES
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15% (NO specific Dasha timing)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_override}

═══════════════════════════════════════════════════════════════════════════════
                    📊 PRE-COMPUTED ANALYSIS DATA
═══════════════════════════════════════════════════════════════════════════════

{summary_data if summary_data else "Analysis summary not available."}

═══════════════════════════════════════════════════════════════════════════════
                    ⚖️ OUTCOME ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

{outcome_data if outcome_data else "Outcome analysis not available."}

═══════════════════════════════════════════════════════════════════════════════
                    ⏱️ DURATION ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

{duration_data if duration_data else "Duration analysis not available."}

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ RISKS & PENALTIES ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

{risks_data if risks_data else "Risks analysis not available."}

═══════════════════════════════════════════════════════════════════════════════
                    🎯 LAGNA (ASCENDANT) DATA
═══════════════════════════════════════════════════════════════════════════════

{lagna_block}

═══════════════════════════════════════════════════════════════════════════════
                    🏠 VEDIC HOUSE LORDS DATA
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

═══════════════════════════════════════════════════════════════════════════════
                    👁️ ASPECTS DATA
═══════════════════════════════════════════════════════════════════════════════

{aspects_data if aspects_data else "Aspects data not available."}

═══════════════════════════════════════════════════════════════════════════════
                    📅 TIMING HINTS
═══════════════════════════════════════════════════════════════════════════════

{timing_hints if timing_hints else "Timing hints not available."}

═══════════════════════════════════════════════════════════════════════════════
                    📝 RAW TECHNICAL POINTS
═══════════════════════════════════════════════════════════════════════════════

{raw if raw else "No additional technical points."}

═══════════════════════════════════════════════════════════════════════════════
                    📋 OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

IMPORTANT:
Generate the General Answer AFTER completing the full astrological analysis.
The tone and wording MUST reflect the final analysis,
not pre-commit to optimism.

TONE CALIBRATION:
- If outcome ≠ HIGHLY_FAVORABLE → tone must be cautious
- If risk ≥ MODERATE → tone must be conservative

**{lbl_general} (3-4 lines):**
Directly answer the question covering:
- Overall outcome likelihood
- Expected duration
- Risk level
- Key point about penalties

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC analysis only (85% weight).

PARAGRAPH 0 – NATIVE'S STRENGTH (Lagna Lord Analysis):
This paragraph MUST begin with the lagna lord data provided above.
- Analyze the lagna lord: which planet, where placed, what dignity
- What does this mean for the native's overall ability to fight the case?
- Does the lagna lord support or weaken the native's position?

PARAGRAPH 1 – LITIGATION STRENGTH (6th House Analysis):
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 6th house lord (litigation house - PRIMARY)
- Explain placement, dignity, strength
- What it means for winning the legal battle
Example format: "{example_6th}"

PARAGRAPH 2 – OPPONENT'S POSITION (7th House Analysis):
- Analyze 7th house lord (opponent/other party)
- Is the opponent strong or weak?
- What advantage/disadvantage does native have?
Example format: "{example_7th}"

PARAGRAPH 3 – JUSTICE & APPEALS (9th House Analysis):
- Analyze 9th house lord (justice, dharma, higher courts)
- Will justice prevail?
- Are appeals likely to be favorable?
Example format: "{example_9th}"

PARAGRAPH 4 – RISKS & PENALTIES (8th House Analysis):
- Analyze 8th house lord (penalties, fines, sudden events)
- What are the potential risks?
- Are there hidden factors that could affect the case?
Example format: "{example_8th}"

PARAGRAPH 5 – CASE DURATION:
Using the duration analysis provided:
- Explain expected timeframe
- What factors will cause delays?
- What factors may speed things up?

PARAGRAPH 6 – KEY KARAKAS (Saturn & Jupiter):
- Saturn's role (justice, karma, delays)
- Jupiter's role (dharma, protection, favorable judgment)
- How do they influence the case?
Example: "{example_saturn}"
Example: "{example_jupiter}"

PARAGRAPH 7 – SUPPORTING HOUSES:
- 4th house (family, property)
- 10th house (authority, judges)
- 11th house (gains, favorable outcome)
- 12th house (losses, expenses, settlements)

PARAGRAPH 8 – ASPECTS INFLUENCE:
Benefic/malefic aspects on 6th, 7th, 8th, 9th houses.
What protection or challenges do they bring?

MANDATORY PARAGRAPH – UNCERTAINTY NOTE:
- Clearly state one limitation or conflicting factor in the chart
- Explain why astrology cannot be conclusive in this case


**{lbl_summary}:**
{lbl_tell}: 
"[Clear statement about:
1. Outcome likelihood (favorable/challenging/uncertain)
2. Expected duration 
3. Risk level and what to watch out for
4. Whether to fight or consider settlement]"

CRITICAL: End with:
"Astrology shows tendencies, not certainties. Court outcomes depend on evidence, legal representation, and many other factors. Please consult a qualified lawyer for proper legal advice."

**{lbl_remedies}:**
Based on the challenges identified, provide:

1. **Primary Remedy** (for overall success):
   - If 6th house weak: Strengthen through [specific remedy]
   - If Saturn afflicted: Saturn remedies
   - If Jupiter weak: Jupiter remedies

2. **Protection Remedies** (for reducing risks):
   - For penalties/8th house issues
   - For hidden enemies/deception

3. **Timing Advice**:
   - Best days for court appearances
   - Days to avoid
   - Best nakshatras for legal filings

4. **Practical Advice**:
   - Hire a competent lawyer
   - Keep all documentation in order
   - Consider mediation/settlement if risks are high

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ CRITICAL REMINDERS
═══════════════════════════════════════════════════════════════════════════════

- Answer ALL FOUR parts: Outcome, Duration, Risks, Penalties
- VEDIC analysis PRIMARY (85% weight)
- Write in FLOWING PARAGRAPHS, not bullet lists
- Never guarantee outcomes
- Be sensitive - this is a stressful time for the client
- ALWAYS recommend consulting a qualified lawyer
- Include legal disclaimer at the end
{'- MINOR DETECTED: Apply protective, family-centered tone throughout' if is_minor else ''}

═══════════════════════════════════════════════════════════════════════════════
"""
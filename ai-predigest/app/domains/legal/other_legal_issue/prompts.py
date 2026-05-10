"""
Other Legal Dispute – LLM Prompts v1.0 (VEDIC-ONLY)

General-purpose prompt builder for analyzing miscellaneous legal disputes
that don't fit into specific categories (business, property, marriage, family).

Examples: Consumer disputes, criminal cases, civil suits, labor disputes,
insurance claims, contract disputes, defamation, cheque bounce, etc.

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Simple and straightforward structure
✅ Output language based on user selection
✅ Outcome likelihood assessment
✅ Duration guidance
✅ Risk and penalty analysis
✅ Professional and balanced tone

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from OtherLegalDisputeEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["other_legal_outcome_analysis"] = {
    "likelihood": "FAVORABLE" | "MODERATELY_FAVORABLE" | "UNCERTAIN" | "CHALLENGING" | "UNFAVORABLE",
    "score": int (0-100),
    "favorable_factors": [...],
    "unfavorable_factors": [...],
    "strategic_hints": [...]
}

additional_data["other_legal_duration_analysis"] = {
    "duration_category": "VERY_SHORT" | "SHORT" | "MODERATE" | "LONG" | "VERY_LONG",
    "duration_score": int (0-100),
    "delay_factors": [...],
    "speed_factors": [...],
    "duration_hints": [...]
}

additional_data["other_legal_risk_analysis"] = {
    "risk_level": "VERY_LOW" | "LOW" | "MODERATE" | "HIGH" | "VERY_HIGH",
    "risk_score": int (0-100),
    "risk_factors": [...],
    "penalty_indicators": [...],
    "mitigation_hints": [...]
}

additional_data["other_legal_house_lords"] = {...}
additional_data["other_legal_house_aspects"] = {...}
═══════════════════════════════════════════════════════════════════════════════
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

DOMAIN_PREFIX = "other_legal"


class OtherLegalDisputePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Legal → Other Legal Issue
    v1.0 - Vedic-only analysis (Simple & General Purpose)
    """

    domain = "Legal"
    subtopic = "Other Legal Issue"

    # ==========================================================================
    # LANGUAGE INSTRUCTION
    # ==========================================================================
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
                "6th_house": "षष्ठ भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि आपकी मुकदमेबाजी की क्षमता...",
                "9th_house": "नवम भाव के स्वामी [planet] [position] में होने से न्याय और कानूनी कार्यवाही...",
                "outcome_favorable": "परिणाम आपके पक्ष में होने की संभावना है।",
                "outcome_unfavorable": "कानूनी मामले में चुनौतियां हो सकती हैं।",
                "duration_short": "मामला जल्दी निपट सकता है।",
                "duration_long": "कानूनी प्रक्रिया में समय लग सकता है।",
                "risk_high": "जोखिम का स्तर अधिक है - सावधानी बरतें।",
                "risk_low": "जोखिम का स्तर कम है।",
                "tell_client": "TELL CLIENT",
                "outcome_outlook": "परिणाम संभावना",
                "duration_outlook": "अवधि अनुमान",
                "risk_outlook": "जोखिम विश्लेषण"
            },
            "English": {
                "6th_house": "The lord of 6th house [planet] is placed in [house] house in [sign]. This indicates about your litigation ability...",
                "9th_house": "The lord of 9th house [planet] being in [position] indicates justice and legal proceedings...",
                "outcome_favorable": "The outcome is likely to be in your favor.",
                "outcome_unfavorable": "There may be challenges in the legal matter.",
                "duration_short": "The case may be resolved quickly.",
                "duration_long": "The legal process may take time.",
                "risk_high": "Risk level is high - exercise caution.",
                "risk_low": "Risk level is low.",
                "tell_client": "TELL CLIENT",
                "outcome_outlook": "Outcome Prospects",
                "duration_outlook": "Duration Estimate",
                "risk_outlook": "Risk Analysis"
            }
        }
        
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get analysis paragraph starters in selected language"""
        return {
            "Hindi": {"vedic": "वैदिक ज्योतिष के अनुसार,"},
            "English": {"vedic": "According to Vedic astrology,"}
        }.get(language, {"vedic": "According to Vedic astrology,"})

    # ==========================================================================
    # SYSTEM PROMPT
    # ==========================================================================
    def build_system_prompt(self, language: str = "English") -> str:
        """Build system prompt for other legal dispute analysis"""
        
        return f"""You are an expert Vedic astrologer providing interpretive insights related to legal matters.


**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED - Do not invent planetary positions
2. DISTINGUISH FACTS FROM INTERPRETATION
3. NO GUARANTEES - Present as "indications" and "tendencies"
4. RETROGRADE ≠ WEAKNESS - Retrograde indicates delay, not weakness
5. LEGAL DISCLAIMER - Always recommend consulting qualified legal professionals
6. ASPECTS ARE SECONDARY – Aspects modify but never override house lord strength.


═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR LEGAL DISPUTES
═══════════════════════════════════════════════════════════════════════════════

- 6th House: Litigation, disputes, enemies, legal battles (PRIMARY)
- 7th House: Opponent, other party in dispute
- 8th House: Hidden matters, sudden events, investigations
- 9th House: Legal proceedings, higher courts, justice, dharma
- 10th House: Reputation, authority, government dealings
- 11th House: Gains, victory, favorable outcomes
- 12th House: Losses, expenses, penalties, severe restrictions (in extreme cases)


═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Jupiter: Law, justice, judges, dharma, favorable outcomes
- Saturn: Delays, legal processes, punishment, karma
- Mars: Aggression, conflict, litigation energy
- Sun: Government, authority, power in legal matters
- Mercury: Documents, contracts, communication, evidence

═══════════════════════════════════════════════════════════════════════════════
                    WRITING RULES
═══════════════════════════════════════════════════════════════════════════════

1. Write in FLOWING PARAGRAPHS, not bullet lists
2. Every fact needs INTERPRETATION
3. "TELL CLIENT:" only in final summary
4. Provide BALANCED, PROFESSIONAL guidance
5. Recommend legal consultation for serious matters
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
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

    def _format_outcome_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        outcome = additional_data.get(f"{DOMAIN_PREFIX}_outcome_analysis", {})
        if not outcome:
            return ""
        
        lines = ["OUTCOME ANALYSIS:"]
        lines.append(f"• Likelihood: {outcome.get('likelihood', 'UNCERTAIN')}")
        lines.append(f"• Score: {outcome.get('score', 50)}/100")
        
        for f in outcome.get("favorable_factors", [])[:3]:
            lines.append(f"  ✅ {f}")
        for f in outcome.get("unfavorable_factors", [])[:3]:
            lines.append(f"  ⚠️ {f}")
        for h in outcome.get("strategic_hints", [])[:2]:
            lines.append(f"  💡 {h}")
        
        return "\n".join(lines)

    def _format_duration_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        duration = additional_data.get(f"{DOMAIN_PREFIX}_duration_analysis", {})
        if not duration:
            return ""
        
        lines = ["DURATION ANALYSIS:"]
        lines.append(f"• Category: {duration.get('duration_category', 'MODERATE')}")
        
        for f in duration.get("delay_factors", [])[:2]:
            lines.append(f"  ⏳ {f}")
        for f in duration.get("speed_factors", [])[:2]:
            lines.append(f"  ⚡ {f}")
        for h in duration.get("duration_hints", [])[:1]:
            lines.append(f"  📅 {h}")
        
        return "\n".join(lines)

    def _format_risk_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        if not risk:
            return ""
        
        lines = ["RISK ANALYSIS:"]
        lines.append(f"• Risk Level: {risk.get('risk_level', 'MODERATE')}")
        lines.append(f"• Risk Score: {risk.get('risk_score', 50)}/100")
        
        for f in risk.get("risk_factors", [])[:3]:
            lines.append(f"  🚨 {f}")
        for p in risk.get("penalty_indicators", [])[:2]:
            lines.append(f"  💰 {p}")
        for m in risk.get("mitigation_hints", [])[:2]:
            lines.append(f"  🛡️ {m}")
        
        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        legal_houses = {1, 6, 7, 8, 9, 10, 11, 12}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in legal_houses:
                continue
            
            info = house_lords.get(house_num, {})
            if not info:
                continue
            
            lord = info.get('lord', 'N/A')
            lord_house = info.get('lord_in_house', 'N/A')
            lord_sign = info.get('lord_in_sign', 'N/A')
            dignity = info.get('lord_dignity', 'N/A')
            strength = info.get('lord_strength_score', 0)
            
            conditions = []
            if info.get('lord_is_combust'):
                conditions.append("C")
            if info.get('lord_is_retrograde'):
                conditions.append("R")
            condition_str = f"[{','.join(conditions)}]" if conditions else ""
            
            lines.append(f"• H{house_num}: {lord} in H{lord_house}/{lord_sign} | {dignity} | Str:{strength} {condition_str}")
        
        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""
        
        lines = ["ASPECTS:"]
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            
            if benefic or malefic:
                b_str = ",".join(benefic) if benefic else "-"
                m_str = ",".join(malefic) if malefic else "-"
                lines.append(f"• H{house_num}: B={b_str} | M={m_str}")
        
        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # MAIN ROUTING METHOD
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
        """Main routing method"""
        
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            
            # Route based on sub_subdomain
            if "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language)
            else:
                # Default: General legal dispute
                return self._build_general_prompt(question, additional_data, raw, language)
        
        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # FALLBACK PROMPT
    # ==========================================================================
    def _build_fallback_prompt(self, question: str, language: str) -> str:
        """Fallback prompt if something fails"""
        lang_inst = self._get_language_instruction_safe(language)
        
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in legal matters.

QUESTION: "{question}"

Provide a helpful analysis focusing on:
- 6th house (litigation ability)
- 9th house (justice)
- 11th house (victory)
- Jupiter's role in legal matters

Write in flowing paragraphs. Recommend consulting a qualified lawyer.
"""

    # ==========================================================================
    # GENERAL PROMPT
    # ==========================================================================
    def _build_general_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for general legal dispute questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        outcome_score = self._get_outcome_score(additional_data)
        duration_category = self._get_duration_category(additional_data)
        risk_level = self._get_risk_level(additional_data)
        risk_score = self._get_risk_score(additional_data)
        
        outcome_data = self._format_outcome_analysis(additional_data)
        duration_data = self._format_duration_analysis(additional_data)
        risk_data = self._format_risk_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_outcome = self._get_example_text(language, "outcome_outlook")
        lbl_duration = self._get_example_text(language, "duration_outlook")
        lbl_risk = self._get_example_text(language, "risk_outlook")
        starters = self._get_analysis_starters(language)

        # Outcome text
        if outcome_score >= 55:
            outcome_text = self._get_example_text(language, "outcome_favorable")
        else:
            outcome_text = self._get_example_text(language, "outcome_unfavorable")

        # Duration text
        if duration_category in ["VERY_SHORT", "SHORT"]:
            duration_text = self._get_example_text(language, "duration_short")
        else:
            duration_text = self._get_example_text(language, "duration_long")

        # Risk text
        if risk_level in ["HIGH", "VERY_HIGH"]:
            risk_text = self._get_example_text(language, "risk_high")
        else:
            risk_text = self._get_example_text(language, "risk_low")

        # High risk warning
        risk_warning = ""
        if risk_level in ["HIGH", "VERY_HIGH"]:
            risk_warning = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ Elevated Risk Indicators Present
- Legal complexity appears higher than average
- Professional legal guidance is strongly recommended
- Careful documentation and patience are advised
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: LEGAL DISPUTE ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100%
Outcome: {outcome_likelihood} ({outcome_score}/100)
Duration: {duration_category}
Risk: {risk_level} ({risk_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{risk_warning}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{outcome_data}

{duration_data}

{risk_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_outcome}: {outcome_text}
{lbl_duration}: {duration_text}
{lbl_risk}: {risk_text}
Brief assessment of the legal situation.
Avoid technical astrological jargon (e.g., nakshatra, degree, combustion).
Write in plain, professional language.

(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – LITIGATION ABILITY:
Begin with: "{starters['vedic']}"
- 6th house analysis (litigation, disputes)
- 6th lord strength and placement
- Ability to fight the legal battle

PARAGRAPH 2 – JUSTICE & LEGAL PROSPECTS:
- 9th house analysis (justice, law, dharma)
- Jupiter's role and placement
- 11th house (victory, gains)

PARAGRAPH 3 – SELF VS OPPONENT:
- 1st house vs 7th house comparison
- Who has the advantage
- Opponent's strength assessment

PARAGRAPH 4 – DURATION FACTORS:
- Saturn's influence on timing
- Delay or speed indicators
- Expected timeline

PARAGRAPH 5 – RISK ASSESSMENT:
- 8th house (hidden matters)
- 12th house (losses, penalties)
- Key risk factors and mitigation

PARAGRAPH 6 – STRATEGIC GUIDANCE:
- Practical strategy based on chart
- When to push vs settle
- Key recommendations

SUMMARY:
{lbl_tell}: "[Outcome + Duration + Risk + Key action]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Remedy for 6th house/litigation strength
- Jupiter remedy for justice
- One specific mantra or worship

REMEDIES_GENERAL:
- Consult qualified legal professional
- Document everything carefully
- Maintain patience and composure

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # REMEDIES PROMPT
    # ==========================================================================
    def _build_remedies_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for remedies questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        outcome_likelihood = self._get_outcome_likelihood(additional_data)
        risk_level = self._get_risk_level(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REMEDIES FOR LEGAL SUCCESS
Current Date: {today_str}
Outcome Likelihood: {outcome_likelihood}
Risk Level: {risk_level}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE:
═══════════════════════════════════════════════════════════════════════════════

Recommend MAXIMUM 2-3 remedies based on weak planets:

6th LORD WEAK: Strengthen litigation ability - remedy specific to planet
9th LORD WEAK: Jupiter remedies - Thursday fasts, Vishnu worship
JUPITER WEAK: Yellow sapphire, Thursday fasts, Vishnu Sahasranama
SATURN CAUSING DELAYS: Saturday fasts, Hanuman worship
MARS AFFLICTING: Tuesday fasts, Hanuman Chalisa

Traditional Supportive Practices (Faith-based):
- Baglamukhi worship for mental focus and restraint in conflicts
- Hanuman Chalisa to cultivate discipline and courage
- Vishnu worship to encourage ethical conduct and patience

═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
What challenges exist and how remedies can help.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin with: "{starters['vedic']}"
- Identify weak planets affecting legal success
- Main astrological challenges

PARAGRAPH 2 – PRIMARY REMEDY:
Most important remedy and WHY it helps.
Detailed instructions.

PARAGRAPH 3 – SUPPORTING REMEDIES:
Additional helpful practices.

SUMMARY:
{lbl_tell}: "[Priority remedy + Practice schedule + Intended supportive effect]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
1. [Primary remedy with instructions]
2. [Secondary remedy]

REMEDIES_GENERAL:
- Consult qualified legal professional
- Maintain ethical conduct
- Practice patience

═══════════════════════════════════════════════════════════════════════════════
"""
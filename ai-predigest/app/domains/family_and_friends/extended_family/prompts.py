"""
Extended Family – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for analyzing extended/joint family relationships,
inheritance disputes, and ancestral property matters using Vedic astrology.

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Simple and straightforward structure
✅ Focus on joint family, inheritance, ancestral property
✅ Output language based on user selection
✅ Warm and practical tone

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from ExtendedFamilyEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["extended_family_harmony_analysis"] = {
    "harmony_level": "HARMONIOUS" | "GOOD" | "MODERATE" | "CHALLENGING" | "DIFFICULT",
    "harmony_score": int (0-100),
    "favorable_factors": [...],
    "challenging_factors": [...],
    "responsibilities": [...]
}

additional_data["extended_family_inheritance_analysis"] = {
    "inheritance_prospects": "FAVORABLE" | "GOOD" | "MODERATE" | "CHALLENGING" | "DIFFICULT",
    "inheritance_score": int (0-100),
    "property_indicators": [...],
    "caution_factors": [...],
    "recommendations": [...]
}

additional_data["extended_family_dispute_analysis"] = {
    "dispute_potential": "LOW" | "MODERATE" | "HIGH",
    "dispute_score": int (0-100),
    "dispute_factors": [...],
    "resolution_factors": [...],
    "advice": [...]
}
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

DOMAIN_PREFIX = "extended_family"


class ExtendedFamilyPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Family and Friends → Extended Family
    v1.0 - Vedic-only analysis (Simple Structure)
    """

    domain = "Family_Friends"
    subtopic = "Extended Family"

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
                "2nd_house": "द्वितीय भाव के स्वामी [planet] [house] भाव में हैं। इसका अर्थ है कि परिवार (कुटुंब) के साथ...",
                "4th_house": "चतुर्थ भाव के स्वामी [planet] [position] में होने से पैतृक संपत्ति...",
                "8th_house": "अष्टम भाव के स्वामी [planet] [position] में होने से विरासत...",
                "harmony_good": "संयुक्त परिवार में सामंजस्य अच्छा है।",
                "harmony_moderate": "परिवार में कुछ मतभेद हो सकते हैं।",
                "harmony_challenging": "पारिवारिक सामंजस्य पर ध्यान देना आवश्यक है।",
                "inheritance_good": "विरासत और पैतृक संपत्ति के योग अनुकूल हैं।",
                "inheritance_caution": "विरासत मामलों में सावधानी बरतें।",
                "dispute_low": "पारिवारिक विवाद की संभावना कम है।",
                "dispute_high": "कुछ पारिवारिक मतभेद हो सकते हैं।",
                "tell_client": "TELL CLIENT",
                "harmony_outlook": "पारिवारिक सामंजस्य",
                "inheritance_outlook": "विरासत संभावना",
                "dispute_outlook": "विवाद संभावना"
            },
            "English": {
                "2nd_house": "The lord of 2nd house [planet] is placed in [house] house. This indicates about family (kutumb)...",
                "4th_house": "The lord of 4th house [planet] being in [position] indicates ancestral property...",
                "8th_house": "The lord of 8th house [planet] being in [position] indicates inheritance...",
                "harmony_good": "Joint family harmony is well supported.",
                "harmony_moderate": "Some differences may arise in family.",
                "harmony_challenging": "Family harmony needs attention and effort.",
                "inheritance_good": "Inheritance and ancestral property prospects are favorable.",
                "inheritance_caution": "Exercise caution in inheritance matters.",
                "dispute_low": "Family dispute potential is low.",
                "dispute_high": "Some family differences may arise.",
                "tell_client": "TELL CLIENT",
                "harmony_outlook": "Family Harmony",
                "inheritance_outlook": "Inheritance Prospects",
                "dispute_outlook": "Dispute Potential"
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
        """Build system prompt for extended family analysis"""
        
        return f"""You are an expert Vedic astrologer specializing in family matters, joint family dynamics, inheritance, and ancestral property.

**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED - Do not invent planetary positions
2. DISTINGUISH FACTS FROM INTERPRETATION
3. NO GUARANTEES - Present as "indications" and "tendencies"
4. RETROGRADE ≠ WEAKNESS - Retrograde indicates review, not weakness
5. FAMILY MATTERS ARE SENSITIVE - Be supportive and practical

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR EXTENDED FAMILY
═══════════════════════════════════════════════════════════════════════════════

- 2nd House: Family (kutumb), family wealth, ancestral wealth
- 4th House: Ancestral property, home, mother's family, land
- 8th House: Inheritance, legacies, in-laws, hidden family matters
- 9th House: Father's family, elders, traditions, ancestral blessings
- 6th House: Disputes, conflicts, litigation in family
- 11th House: Gains from family, elder relatives
- 12th House: Losses, separation from family

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Jupiter: Family prosperity, elders, traditions, blessings
- Saturn: Responsibilities, duties, karma, ancestral debts
- Mars: Property, land, disputes, conflicts
- Sun: Father's lineage, authority in family
- Moon: Mother's lineage, emotional bonds, family home
- Venus: Harmony, love, family happiness

═══════════════════════════════════════════════════════════════════════════════
                    WRITING RULES
═══════════════════════════════════════════════════════════════════════════════

1. Write in FLOWING PARAGRAPHS, not bullet lists
2. Every fact needs INTERPRETATION
3. "TELL CLIENT:" only in final summary
4. Be PRACTICAL - family and property matters need clear guidance
5. Focus on SOLUTIONS for challenges
6. Recommend legal consultation for property/inheritance issues
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_harmony_level(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        harmony = additional_data.get(f"{DOMAIN_PREFIX}_harmony_analysis", {})
        return harmony.get("harmony_level", "MODERATE")

    def _get_harmony_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        harmony = additional_data.get(f"{DOMAIN_PREFIX}_harmony_analysis", {})
        return harmony.get("harmony_score", 50)

    def _get_inheritance_prospects(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        inheritance = additional_data.get(f"{DOMAIN_PREFIX}_inheritance_analysis", {})
        return inheritance.get("inheritance_prospects", "MODERATE")

    def _get_inheritance_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        inheritance = additional_data.get(f"{DOMAIN_PREFIX}_inheritance_analysis", {})
        return inheritance.get("inheritance_score", 50)

    def _get_dispute_potential(self, additional_data: Dict) -> str:
        if not additional_data:
            return "LOW"
        dispute = additional_data.get(f"{DOMAIN_PREFIX}_dispute_analysis", {})
        return dispute.get("dispute_potential", "LOW")

    def _get_dispute_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 30
        dispute = additional_data.get(f"{DOMAIN_PREFIX}_dispute_analysis", {})
        return dispute.get("dispute_score", 30)

    def _format_harmony_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        harmony = additional_data.get(f"{DOMAIN_PREFIX}_harmony_analysis", {})
        if not harmony:
            return ""
        
        lines = ["FAMILY HARMONY ANALYSIS:"]
        lines.append(f"• Level: {harmony.get('harmony_level', 'MODERATE')}")
        lines.append(f"• Score: {harmony.get('harmony_score', 50)}/100")
        
        for f in harmony.get("favorable_factors", [])[:3]:
            lines.append(f"  ✅ {f}")
        for f in harmony.get("challenging_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        for r in harmony.get("responsibilities", [])[:2]:
            lines.append(f"  📋 {r}")
        
        return "\n".join(lines)

    def _format_inheritance_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        inheritance = additional_data.get(f"{DOMAIN_PREFIX}_inheritance_analysis", {})
        if not inheritance:
            return ""
        
        lines = ["INHERITANCE & PROPERTY ANALYSIS:"]
        lines.append(f"• Prospects: {inheritance.get('inheritance_prospects', 'MODERATE')}")
        lines.append(f"• Score: {inheritance.get('inheritance_score', 50)}/100")
        
        for f in inheritance.get("property_indicators", [])[:3]:
            lines.append(f"  🏠 {f}")
        for f in inheritance.get("caution_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        for r in inheritance.get("recommendations", [])[:2]:
            lines.append(f"  💡 {r}")
        
        return "\n".join(lines)

    def _format_dispute_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        dispute = additional_data.get(f"{DOMAIN_PREFIX}_dispute_analysis", {})
        if not dispute:
            return ""
        
        lines = ["DISPUTE ANALYSIS:"]
        lines.append(f"• Potential: {dispute.get('dispute_potential', 'LOW')}")
        lines.append(f"• Score: {dispute.get('dispute_score', 30)}/100")
        
        for f in dispute.get("dispute_factors", [])[:3]:
            lines.append(f"  🔥 {f}")
        for f in dispute.get("resolution_factors", [])[:2]:
            lines.append(f"  🕊️ {f}")
        for a in dispute.get("advice", [])[:2]:
            lines.append(f"  💡 {a}")
        
        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        
        for house_num in sorted(house_lords.keys()):
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
            
            # Single prompt for extended family
            return self._build_extended_family_prompt(question, additional_data, raw, language)
        
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

You are an expert Vedic astrologer specializing in family and property matters.

QUESTION: "{question}"

Provide a helpful analysis focusing on:
- 2nd house (family, kutumb)
- 4th house (ancestral property)
- 8th house (inheritance)
- Jupiter and Saturn for family karma

Write in flowing paragraphs. Be practical and supportive.
"""

    # ==========================================================================
    # EXTENDED FAMILY PROMPT
    # ==========================================================================
    def _build_extended_family_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for extended family questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        harmony_level = self._get_harmony_level(additional_data)
        harmony_score = self._get_harmony_score(additional_data)
        inheritance_prospects = self._get_inheritance_prospects(additional_data)
        inheritance_score = self._get_inheritance_score(additional_data)
        dispute_potential = self._get_dispute_potential(additional_data)
        dispute_score = self._get_dispute_score(additional_data)
        
        harmony_data = self._format_harmony_analysis(additional_data)
        inheritance_data = self._format_inheritance_analysis(additional_data)
        dispute_data = self._format_dispute_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_harmony = self._get_example_text(language, "harmony_outlook")
        lbl_inheritance = self._get_example_text(language, "inheritance_outlook")
        lbl_dispute = self._get_example_text(language, "dispute_outlook")
        starters = self._get_analysis_starters(language)

        # Harmony text
        if harmony_score >= 55:
            harmony_text = self._get_example_text(language, "harmony_good")
        elif harmony_score >= 40:
            harmony_text = self._get_example_text(language, "harmony_moderate")
        else:
            harmony_text = self._get_example_text(language, "harmony_challenging")

        # Inheritance text
        if inheritance_score >= 55:
            inheritance_text = self._get_example_text(language, "inheritance_good")
        else:
            inheritance_text = self._get_example_text(language, "inheritance_caution")

        # Dispute text
        if dispute_score >= 50:
            dispute_text = self._get_example_text(language, "dispute_high")
        else:
            dispute_text = self._get_example_text(language, "dispute_low")

        # Warning for high dispute potential
        dispute_warning = ""
        if dispute_potential == "HIGH":
            dispute_warning = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ HIGH DISPUTE POTENTIAL INDICATED
- Focus on resolution strategies
- Recommend family dialogue
- Suggest legal consultation for property matters
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: EXTENDED FAMILY, INHERITANCE & ANCESTRAL PROPERTY
Current Date: {today_str}
Weightage: VEDIC 100%
Family Harmony: {harmony_level} ({harmony_score}/100)
Inheritance: {inheritance_prospects} ({inheritance_score}/100)
Dispute Potential: {dispute_potential} ({dispute_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{dispute_warning}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{harmony_data}

{inheritance_data}

{dispute_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_harmony}: {harmony_text}
{lbl_inheritance}: {inheritance_text}
{lbl_dispute}: {dispute_text}
Brief assessment of extended family situation.
NO astrological terms. Write practically and supportively.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – FAMILY UNITY (2nd House):
Begin with: "{starters['vedic']}"
- 2nd house analysis (kutumb, family wealth)
- 2nd lord strength and placement
- Jupiter's role in family prosperity
- Overall family unity indicators

PARAGRAPH 2 – ANCESTRAL PROPERTY (4th House):
- 4th house analysis (ancestral property, home)
- 4th lord strength and placement
- Mars's role in land, construction, and disputes related to property
- Ancestral property prospects

PARAGRAPH 3 – INHERITANCE (8th House):
- 8th house analysis (inheritance, legacies)
- 8th lord strength and placement
- Gains or challenges in inheritance
- Hidden family matters

PARAGRAPH 4 – PATERNAL FAMILY & TRADITIONS (9th House):
- 9th house analysis (father's family, elders)
- Blessings from ancestors
- Family traditions and dharma

PARAGRAPH 5 – DISPUTE POTENTIAL:
- 6th house connection to family houses
- Mars/Rahu/Saturn influences
- Areas that may cause friction
- How to handle differences
- Emphasize disputes ONLY if dispute_score is MODERATE or HIGH


PARAGRAPH 6 – RESPONSIBILITIES & DUTIES:
- Saturn's role in family karma
- Responsibilities towards elders
- Ancestral debts (Pitru Rina)
- Fulfilling family duties

PARAGRAPH 7 – PRACTICAL RECOMMENDATIONS:
- How to maintain family harmony
- Property/inheritance advice
- When to seek legal counsel
- Spiritual remedies for family peace

SUMMARY:
{lbl_tell}: "[Family harmony + Inheritance prospects + Key advice]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Jupiter remedy for family prosperity
- Saturn remedy for fulfilling duties
- Pitru Dosha remedy if indicated

REMEDIES_GENERAL:
- Maintain open communication in family
- Document property matters legally
- Respect elders and traditions
- Perform Shraddha/ancestor rituals
- Seek mediation for disputes early

═══════════════════════════════════════════════════════════════════════════════
"""
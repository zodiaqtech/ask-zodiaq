"""
Parents and Siblings – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for analyzing relationships with parents and siblings
using traditional Vedic astrology principles.

Covers two sub-subdomains:
1. Relationship with Parents - harmony, disputes, elder care
2. Relationship with Siblings - harmony, disputes, support

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Simple and straightforward structure
✅ Output language based on user selection
✅ Harmony assessment
✅ Dispute potential analysis
✅ Practical recommendations
✅ Warm and supportive tone

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from ParentsAndSiblingsEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["family_parents_siblings_relationship_analysis"] = {
    "relationship_quality": "HARMONIOUS" | "GOOD" | "MODERATE" | "CHALLENGING" | "DIFFICULT",
    "harmony_score": int (0-100),
    "mother_relationship": str (for parents),
    "father_relationship": str (for parents),
    "younger_siblings": str (for siblings),
    "elder_siblings": str (for siblings),
    "harmony_factors": [...],
    "dispute_factors": [...],
    "elder_care_indicators": [...] (for parents),
    "sibling_support": [...] (for siblings),
    "recommendations": [...]
}

additional_data["family_parents_siblings_dispute_analysis"] = {
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

DOMAIN_PREFIX = "family_parents_siblings"


class ParentsAndSiblingsPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Family and Friends → Parents and Siblings
    v1.0 - Vedic-only analysis
    """

    domain = "Family_Friends"
    subtopic = "Parents and Siblings"

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
                "4th_house": "चतुर्थ भाव के स्वामी [planet] [house] भाव में हैं। इसका अर्थ है कि माता के साथ आपका संबंध...",
                "9th_house": "नवम भाव के स्वामी [planet] [position] में होने से पिता के साथ संबंध...",
                "3rd_house": "तृतीय भाव के स्वामी [planet] [position] में होने से छोटे भाई-बहनों के साथ...",
                "11th_house": "एकादश भाव के स्वामी [planet] [position] में होने से बड़े भाई-बहनों के साथ...",
                "harmony_good": "संबंध सामंजस्यपूर्ण और सहयोगात्मक है।",
                "harmony_moderate": "संबंध में कुछ उतार-चढ़ाव हो सकते हैं।",
                "harmony_challenging": "संबंध में सुधार के लिए प्रयास आवश्यक है।",
                "dispute_low": "विवाद की संभावना कम है।",
                "dispute_high": "कुछ मतभेद हो सकते हैं - धैर्य रखें।",
                "tell_client": "TELL CLIENT",
                "harmony_outlook": "सामंजस्य स्थिति",
                "dispute_outlook": "विवाद संभावना"
            },
            "English": {
                "4th_house": "The lord of 4th house [planet] is placed in [house] house. This indicates your relationship with mother...",
                "9th_house": "The lord of 9th house [planet] being in [position] indicates relationship with father...",
                "3rd_house": "The lord of 3rd house [planet] being in [position] indicates younger siblings...",
                "11th_house": "The lord of 11th house [planet] being in [position] indicates elder siblings...",
                "harmony_good": "The relationship is harmonious and supportive.",
                "harmony_moderate": "The relationship may have some ups and downs.",
                "harmony_challenging": "Effort is needed to improve the relationship.",
                "dispute_low": "Dispute potential is low.",
                "dispute_high": "Some differences may arise - maintain patience.",
                "tell_client": "TELL CLIENT",
                "harmony_outlook": "Harmony Status",
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
        """Build system prompt for parents and siblings analysis"""
        
        return f"""You are an expert Vedic astrologer specializing in family relationships, particularly relationships with parents and siblings.

**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED - Do not invent planetary positions
2. DISTINGUISH FACTS FROM INTERPRETATION
3. NO GUARANTEES - Present as "indications" and "tendencies"
4. RETROGRADE ≠ WEAKNESS - Retrograde indicates review, not weakness
5. FAMILY MATTERS ARE SENSITIVE - Be supportive and constructive

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR FAMILY RELATIONSHIPS
═══════════════════════════════════════════════════════════════════════════════

FOR PARENTS:
- 4th House: Mother, maternal happiness, home environment
- 9th House: Father, paternal blessings, dharma from parents
- 10th House: Father (secondary), responsibilities, duty

FOR SIBLINGS:
- 3rd House: Younger siblings, courage, communication
- 11th House: Elder siblings, gains, social support

COMMON HOUSES:
- 1st House: Self, native's approach to relationships
- 2nd House: Family (kutumb), family harmony
- 6th House: Disputes, conflicts, enmity
- 8th House: Hidden tensions, inheritance issues
- 12th House: Losses, separation from family

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Moon: Mother, emotions, nurturing, maternal care
- Sun: Father, authority, paternal figure, respect
- Mars: Siblings (especially brothers), courage, conflicts
- Mercury: Communication, younger siblings, understanding
- Jupiter: Elders, blessings, wisdom, guidance
- Saturn: Responsibilities, elder care, karma with family
- Venus: Harmony, love, family happiness

═══════════════════════════════════════════════════════════════════════════════
                    WRITING RULES
═══════════════════════════════════════════════════════════════════════════════

1. Write in FLOWING PARAGRAPHS, not bullet lists
2. Every fact needs INTERPRETATION
3. "TELL CLIENT:" only in final summary
4. Be WARM and SUPPORTIVE - family matters are emotional
5. Focus on HARMONY and SOLUTIONS
6. Avoid doom-and-gloom predictions
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_relationship_quality(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        rel = additional_data.get(f"{DOMAIN_PREFIX}_relationship_analysis", {})
        return rel.get("relationship_quality", "MODERATE")

    def _get_harmony_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        rel = additional_data.get(f"{DOMAIN_PREFIX}_relationship_analysis", {})
        return rel.get("harmony_score", 50)

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

    def _get_query_context(self, additional_data: Dict) -> Dict:
        if not additional_data:
            return {"is_parents_query": True, "is_siblings_query": False}
        return additional_data.get(f"{DOMAIN_PREFIX}_query_context", 
                                   {"is_parents_query": True, "is_siblings_query": False})

    def _format_relationship_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        rel = additional_data.get(f"{DOMAIN_PREFIX}_relationship_analysis", {})
        if not rel:
            return ""
        
        lines = ["RELATIONSHIP ANALYSIS:"]
        lines.append(f"• Quality: {rel.get('relationship_quality', 'MODERATE')}")
        lines.append(f"• Harmony Score: {rel.get('harmony_score', 50)}/100")
        
        # Parents specific
        if rel.get("mother_relationship"):
            lines.append(f"• Mother: {rel.get('mother_relationship')}")
        if rel.get("father_relationship"):
            lines.append(f"• Father: {rel.get('father_relationship')}")
        
        # Siblings specific
        if rel.get("younger_siblings"):
            lines.append(f"• Younger Siblings: {rel.get('younger_siblings')}")
        if rel.get("elder_siblings"):
            lines.append(f"• Elder Siblings: {rel.get('elder_siblings')}")
        
        for f in rel.get("favorable_factors", [])[:3]:
            lines.append(f"  ✅ {f}")
        for f in rel.get("dispute_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        for f in rel.get("elder_care_indicators", [])[:2]:
            lines.append(f"  🏠 {f}")
        for f in rel.get("sibling_support", [])[:2]:
            lines.append(f"  🤝 {f}")
        
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
            
            # Determine query type
            question_lower = question.lower()
            is_parents = any(kw in question_lower for kw in ["parent", "mother", "father", "elder care"]) or "Parent" in sub_subdomain
            is_siblings = any(kw in question_lower for kw in ["sibling", "brother", "sister"]) or "Sibling" in sub_subdomain
            
            # Route based on query type
            if is_siblings:
                return self._build_siblings_prompt(question, additional_data, raw, language)
            else:
                return self._build_parents_prompt(question, additional_data, raw, language)
        
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

You are an expert Vedic astrologer specializing in family relationships.

QUESTION: "{question}"

Provide a helpful analysis focusing on:
- Relevant houses (4th/9th for parents, 3rd/11th for siblings)
- Key karakas (Moon for mother, Sun for father, Mars for siblings)
- Harmony and dispute potential

Write in flowing paragraphs. Be warm and supportive.
"""

    # ==========================================================================
    # PARENTS PROMPT
    # ==========================================================================
    def _build_parents_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for parents relationship questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        relationship_quality = self._get_relationship_quality(additional_data)
        harmony_score = self._get_harmony_score(additional_data)
        dispute_potential = self._get_dispute_potential(additional_data)
        dispute_score = self._get_dispute_score(additional_data)
        
        relationship_data = self._format_relationship_analysis(additional_data)
        dispute_data = self._format_dispute_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get specific parent data
        rel = additional_data.get(f"{DOMAIN_PREFIX}_relationship_analysis", {})
        mother_rel = rel.get("mother_relationship", "MODERATE")
        father_rel = rel.get("father_relationship", "MODERATE")
        elder_care = rel.get("elder_care_indicators", [])
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_harmony = self._get_example_text(language, "harmony_outlook")
        lbl_dispute = self._get_example_text(language, "dispute_outlook")
        starters = self._get_analysis_starters(language)

        # Harmony text
        if harmony_score >= 60:
            harmony_text = self._get_example_text(language, "harmony_good")
        elif harmony_score >= 45:
            harmony_text = self._get_example_text(language, "harmony_moderate")
        else:
            harmony_text = self._get_example_text(language, "harmony_challenging")

        # Dispute text
        if dispute_score >= 50:
            dispute_text = self._get_example_text(language, "dispute_high")
        else:
            dispute_text = self._get_example_text(language, "dispute_low")

        # Elder care section
        elder_care_note = ""
        if elder_care:
            elder_care_note = f"""
ELDER CARE INDICATORS:
{chr(10).join(['• ' + e for e in elder_care[:3]])}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: RELATIONSHIP WITH PARENTS
Current Date: {today_str}
Weightage: VEDIC 100%
Relationship Quality: {relationship_quality} ({harmony_score}/100)
Mother Relationship: {mother_rel}
Father Relationship: {father_rel}
Dispute Potential: {dispute_potential} ({dispute_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{relationship_data}

{dispute_data}

{elder_care_note}

🚨 DATA BOUNDARY:
- Use ONLY the house lords data shown below
- Do NOT add aspects, yogas, or placements not listed
- Do NOT reinterpret dignity beyond strength score

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
{lbl_dispute}: {dispute_text}
Brief assessment of relationship with parents.
NO astrological terms. Write warmly and supportively.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – MOTHER RELATIONSHIP (4th House & Moon):
Begin with: "{starters['vedic']}"
- 4th house analysis (mother, home, maternal happiness)
- Interpret the provided 4th house lord strength and placement from evaluator data
- Moon's role as mother karaka
- Quality of bond with mother

PARAGRAPH 2 – FATHER RELATIONSHIP (9th House & Sun):
- 9th house analysis (father, blessings, dharma)
- 9th lord strength and placement
- Sun's role as father karaka
- Quality of bond with father

PARAGRAPH 3 – FAMILY HARMONY:
- 2nd house (kutumb, family unit)
- Benefic influences on 4th and 9th
- Overall family atmosphere

PARAGRAPH 4 – DISPUTE POTENTIAL:
- Any challenging factors
- Mars/Saturn/Rahu influences
- Areas that may need attention
- How to handle differences
IF dispute_potential == LOW:
- Mention briefly
- Do NOT elaborate causes


PARAGRAPH 5 – ELDER CARE & RESPONSIBILITIES:
- Saturn's role in duties
- 10th house (responsibilities)
- Indications for elder care needs
- How to fulfill duties lovingly

PARAGRAPH 6 – RECOMMENDATIONS:
- How to strengthen bonds
- Remedies for challenges
- Practical advice for harmony

SUMMARY:
{lbl_tell}: "[Relationship quality + Key strength + Any caution + Positive guidance]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Moon remedy for mother relationship (if needed)
- Sun remedy for father relationship (if needed)
- General family harmony remedy

REMEDIES_GENERAL:
- Spend quality time with parents
- Express gratitude and appreciation
- Handle differences with patience
- Plan for elder care if indicated

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # SIBLINGS PROMPT
    # ==========================================================================
    def _build_siblings_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for siblings relationship questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        relationship_quality = self._get_relationship_quality(additional_data)
        harmony_score = self._get_harmony_score(additional_data)
        dispute_potential = self._get_dispute_potential(additional_data)
        dispute_score = self._get_dispute_score(additional_data)
        
        relationship_data = self._format_relationship_analysis(additional_data)
        dispute_data = self._format_dispute_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get specific sibling data
        rel = additional_data.get(f"{DOMAIN_PREFIX}_relationship_analysis", {})
        younger_sib = rel.get("younger_siblings", "MODERATE")
        elder_sib = rel.get("elder_siblings", "MODERATE")
        sibling_support = rel.get("sibling_support", [])
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_harmony = self._get_example_text(language, "harmony_outlook")
        lbl_dispute = self._get_example_text(language, "dispute_outlook")
        starters = self._get_analysis_starters(language)

        # Harmony text
        if harmony_score >= 60:
            harmony_text = self._get_example_text(language, "harmony_good")
        elif harmony_score >= 45:
            harmony_text = self._get_example_text(language, "harmony_moderate")
        else:
            harmony_text = self._get_example_text(language, "harmony_challenging")

        # Dispute text
        if dispute_score >= 50:
            dispute_text = self._get_example_text(language, "dispute_high")
        else:
            dispute_text = self._get_example_text(language, "dispute_low")

        # Sibling support section
        support_note = ""
        if sibling_support:
            support_note = f"""
SIBLING SUPPORT INDICATORS:
{chr(10).join(['• ' + s for s in sibling_support[:3]])}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: RELATIONSHIP WITH SIBLINGS
Current Date: {today_str}
Weightage: VEDIC 100%
Relationship Quality: {relationship_quality} ({harmony_score}/100)
Younger Siblings: {younger_sib}
Elder Siblings: {elder_sib}
Dispute Potential: {dispute_potential} ({dispute_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{relationship_data}

{dispute_data}

{support_note}

🚨 DATA BOUNDARY:
- Use ONLY the house lords data shown below
- Do NOT add aspects, yogas, or placements not listed
- Do NOT reinterpret dignity beyond strength score

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
{lbl_dispute}: {dispute_text}
Brief assessment of relationship with siblings.
NO astrological terms. Write warmly and supportively.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – YOUNGER SIBLINGS (3rd House & Mars):
Begin with: "{starters['vedic']}"
- 3rd house analysis (younger siblings, courage, communication)
- 3rd lord strength and placement
- Mars's role as siblings karaka
- Bond with younger siblings

PARAGRAPH 2 – ELDER SIBLINGS (11th House & Jupiter):
- 11th house analysis (elder siblings, gains, support)
- 11th lord strength and placement
- Jupiter's role for elder siblings
- Bond with elder siblings

PARAGRAPH 3 – SIBLING SUPPORT:
- Mutual support indicators
- Gains through siblings
- Protective bonds

PARAGRAPH 4 – DISPUTE POTENTIAL:
- Any challenging factors
- Mars/Saturn/Rahu influences on 3rd/11th
- Areas that may cause friction
- How to handle differences

PARAGRAPH 5 – COMMUNICATION:
- Mercury's role in sibling communication
- How to improve understanding
- Keeping bonds strong despite distance

PARAGRAPH 6 – RECOMMENDATIONS:
- How to strengthen sibling bonds
- Remedies for any challenges
- Practical advice for harmony

SUMMARY:
{lbl_tell}: "[Relationship quality + Key strength + Any caution + Positive guidance]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Mars remedy for sibling harmony (if needed)
- 3rd/11th house strengthening
- General harmony remedy

REMEDIES_GENERAL:
- Stay connected regularly
- Support each other's goals
- Resolve conflicts quickly with love
- Celebrate sibling bonds

═══════════════════════════════════════════════════════════════════════════════
"""
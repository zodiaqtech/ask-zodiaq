"""
Lost Person or Belonging – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for finding lost persons, missing items, and stolen belongings
using traditional Vedic astrology principles.

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Output language based on user selection
✅ Recovery likelihood assessment
✅ Direction guidance (Vedic)
✅ Theft vs Loss differentiation
✅ Sensitive handling of missing person queries
✅ Practical search guidance

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from LostPersonOrBelongingEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["lost_missing_recovery_analysis"] = {
    "likelihood": "HIGH" | "MODERATE" | "LOW" | "VERY_LOW" | "UNCERTAIN",
    "score": int (0-100),
    "favorable_factors": [...],
    "unfavorable_factors": [...],
    "timing_hints": [...]
}

additional_data["lost_missing_direction_analysis"] = {
    "primary_direction": "East" | "West" | "North" | "South" | "Unknown",
    "secondary_direction": str | None,
    "location_hints": [...],
    "element_indicator": "Fire" | "Earth" | "Air" | "Water" | None
}

additional_data["lost_missing_theft_analysis"] = {
    "theft_indicated": bool,
    "theft_score": int (0-100),
    "indicators": [...],
    "thief_description": [...]
}

additional_data["lost_missing_house_lords"] = {...}
additional_data["lost_missing_house_aspects"] = {...}
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

DOMAIN_PREFIX = "lost_missing"


class LostPersonOrBelongingPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Lost_Missing → Lost Person or Belonging
    v1.0 - Vedic-only analysis
    """

    domain = "Lost_Missing"
    subtopic = "Lost Person or Belonging"

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
        """Get example text in the selected language
        
        IMPORTANT: Section headers MUST remain in English for the parser to work correctly.
        Only content examples are language-specific.
        """
        
        examples = {
            "Hindi": {
                "4th_house": "चतुर्थ भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि आपकी खोई वस्तु...",
                "7th_house": "सप्तम भाव के स्वामी [planet] [position] में होने से लापता व्यक्ति का संकेत मिलता है...",
                "11th_house": "एकादश भाव के स्वामी [planet] [position] में होने से पुनर्प्राप्ति की संभावना...",
                "moon": "चंद्रमा की स्थिति खोई वस्तु/व्यक्ति की वर्तमान स्थिति का संकेत देती है...",
                "direction_east": "पूर्व दिशा में खोजें",
                "direction_west": "पश्चिम दिशा में खोजें",
                "direction_north": "उत्तर दिशा में खोजें",
                "direction_south": "दक्षिण दिशा में खोजें",
                "recovery_high": "पुनर्प्राप्ति की संभावना अधिक है।",
                "recovery_low": "पुनर्प्राप्ति में कठिनाई हो सकती है।",
                "theft_indicated": "चोरी का संकेत है।",
                "loss_indicated": "यह खो जाने या गलत जगह रखने का मामला लगता है।",
                # Section headers - MUST be in English for parser
                "general_answer": "GENERAL_ANSWER",
                "astrological_analysis": "ASTROLOGICAL_ANALYSIS",
                "summary": "SUMMARY",
                "remedies": "REMEDIES",
                "tell_client": "TELL CLIENT",
                "recovery_outlook": "पुनर्प्राप्ति संभावना",
                "direction_outlook": "दिशा निर्देश",
                "theft_outlook": "चोरी विश्लेषण"
            },
            "English": {
                "4th_house": "The lord of 4th house [planet] is placed in [house] house in [sign]. This indicates about your lost item...",
                "7th_house": "The lord of 7th house [planet] being in [position] gives clues about the missing person...",
                "11th_house": "The lord of 11th house [planet] being in [position] indicates recovery prospects...",
                "moon": "Moon's position indicates the current state of the lost item/person...",
                "direction_east": "Search towards East direction",
                "direction_west": "Search towards West direction",
                "direction_north": "Search towards North direction",
                "direction_south": "Search towards South direction",
                "recovery_high": "Chances of recovery are high.",
                "recovery_low": "Recovery may be challenging.",
                "theft_indicated": "Theft is indicated.",
                "loss_indicated": "This appears to be a case of misplacement rather than theft.",
                "general_answer": "GENERAL_ANSWER",
                "astrological_analysis": "ASTROLOGICAL_ANALYSIS",
                "summary": "SUMMARY",
                "remedies": "REMEDIES",
                "tell_client": "TELL CLIENT",
                "recovery_outlook": "Recovery Prospects",
                "direction_outlook": "Direction Guidance",
                "theft_outlook": "Theft Analysis"
            }
        }
        
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        """Get analysis paragraph starters in selected language"""
        return {
            "Hindi": {
                "vedic": "वैदिक ज्योतिष के अनुसार,",
            },
            "English": {
                "vedic": "According to Vedic astrology,",
            }
        }.get(language, {
            "vedic": "According to Vedic astrology,",
        })

    # ==========================================================================
    # SYSTEM PROMPT
    # ==========================================================================
    def build_system_prompt(self, language: str = "English") -> str:
        """Build system prompt for lost/missing analysis"""
        
        example_4th = self._get_example_text(language, "4th_house")
        
        return f"""You are an expert Vedic astrologer specializing in Prashna (horary) astrology for finding lost items, missing persons, and stolen belongings.

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
   - Never guarantee recovery or finding
   - Always present as "indications" and "tendencies"
   - Recovery depends on many factors beyond astrology

4. RETROGRADE RULE:
   - Retrograde planets do NOT automatically indicate weakness
   - Retrograde indicates delay, inward action, or repetition
   - Do NOT state that retrograde alone weakens a planet unless evaluator explicitly says so


═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "4th Lord Jupiter in 6th house. Retrograde. Benefic."
   ✅ "{example_4th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for finding the lost item/person
   - Connect to practical search guidance

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

5. PROVIDE PRACTICAL SEARCH GUIDANCE

- Numerical strength scores are CONTEXTUAL indicators
- Do NOT equate low score with impossibility
- Always combine strength with dignity, house, and benefic influence


═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR LOST/MISSING ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

- 2nd House: Movable property, valuables, possessions
- 4th House: Home, domestic items, vehicles, immovable property
- 6th House: Theft, enemies, hidden things (if afflicted = theft)
- 7th House: The missing person or thief (in Prashna)
- 8th House: Hidden matters, secrets, investigation needed
- 11th House: Recovery, gains, fulfillment of desires
- 12th House: Loss, expenditure, things gone far away

═══════════════════════════════════════════════════════════════════════════════
                    DIRECTION INDICATORS (VEDIC)
═══════════════════════════════════════════════════════════════════════════════

Fire Signs (Aries, Leo, Sagittarius) → EAST direction
Earth Signs (Taurus, Virgo, Capricorn) → SOUTH direction
Air Signs (Gemini, Libra, Aquarius) → WEST direction
Water Signs (Cancer, Scorpio, Pisces) → NORTH direction

Element Location Hints:
- Fire: Near kitchen, fireplace, sunny/warm areas
- Earth: On ground level, garden, storage areas
- Air: Upper floors, open areas, near windows
- Water: Near bathroom, water sources, damp places

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ SENSITIVE HANDLING RULES
═══════════════════════════════════════════════════════════════════════════════

- For MISSING PERSONS: Be especially compassionate and hopeful
- NEVER declare permanent loss or death
- Focus on constructive guidance
- Recommend involving authorities for missing persons
- Frame challenges as "requires more effort" not "impossible"
- Always provide practical next steps
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_recovery_likelihood(self, additional_data: Dict) -> str:
        """Get recovery likelihood from evaluator"""
        if not additional_data:
            return "UNCERTAIN"
        recovery = additional_data.get(f"{DOMAIN_PREFIX}_recovery_analysis", {})
        return recovery.get("likelihood", "UNCERTAIN")

    def _get_recovery_score(self, additional_data: Dict) -> int:
        """Get recovery score from evaluator"""
        if not additional_data:
            return 50
        recovery = additional_data.get(f"{DOMAIN_PREFIX}_recovery_analysis", {})
        return recovery.get("score", 50)

    def _is_theft_indicated(self, additional_data: Dict) -> bool:
        """Check if theft is indicated"""
        if not additional_data:
            return False
        theft = additional_data.get(f"{DOMAIN_PREFIX}_theft_analysis", {})
        return theft.get("theft_indicated", False)

    def _get_primary_direction(self, additional_data: Dict) -> str:
        """Get primary direction from evaluator"""
        if not additional_data:
            return "Unknown"
        direction = additional_data.get(f"{DOMAIN_PREFIX}_direction_analysis", {})
        return direction.get("primary_direction", "Unknown")

    def _format_recovery_analysis(self, additional_data: Dict) -> str:
        """Format recovery analysis for prompt"""
        if not additional_data:
            return ""
        
        recovery = additional_data.get(f"{DOMAIN_PREFIX}_recovery_analysis", {})
        if not recovery:
            return ""
        
        lines = ["RECOVERY ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Likelihood: {recovery.get('likelihood', 'UNCERTAIN')}")
        lines.append(f"• Score: {recovery.get('score', 50)}/100")
        
        favorable = recovery.get("favorable_factors", [])
        if favorable:
            lines.append("")
            lines.append("Favorable Factors:")
            for f in favorable[:4]:
                lines.append(f"  ✅ {f}")
        
        unfavorable = recovery.get("unfavorable_factors", [])
        if unfavorable:
            lines.append("")
            lines.append("Challenging Factors:")
            for f in unfavorable[:4]:
                lines.append(f"  ⚠️ {f}")
        
        timing_hints = recovery.get("timing_hints", [])
        if timing_hints:
            lines.append("")
            lines.append("Timing Hints:")
            for h in timing_hints[:3]:
                lines.append(f"  ⏰ {h}")
        
        return "\n".join(lines)

    def _format_direction_analysis(self, additional_data: Dict) -> str:
        """Format direction analysis for prompt"""
        if not additional_data:
            return ""
        
        direction = additional_data.get(f"{DOMAIN_PREFIX}_direction_analysis", {})
        if not direction:
            return ""
        
        lines = ["DIRECTION ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Primary Direction: {direction.get('primary_direction', 'Unknown')}")
        
        secondary = direction.get("secondary_direction")
        if secondary:
            lines.append(f"• Secondary Direction: {secondary}")
        
        element = direction.get("element_indicator")
        if element:
            lines.append(f"• Element: {element}")
        
        hints = direction.get("location_hints", [])
        if hints:
            lines.append("")
            lines.append("Location Hints:")
            for h in hints[:4]:
                lines.append(f"  📍 {h}")
        
        return "\n".join(lines)

    def _format_theft_analysis(self, additional_data: Dict) -> str:
        """Format theft analysis for prompt"""
        if not additional_data:
            return ""
        
        theft = additional_data.get(f"{DOMAIN_PREFIX}_theft_analysis", {})
        if not theft:
            return ""
        
        lines = ["THEFT ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Theft Indicated: {'YES' if theft.get('theft_indicated') else 'NO'}")
        lines.append(f"• Theft Score: {theft.get('theft_score', 0)}/100")
        
        indicators = theft.get("indicators", [])
        if indicators:
            lines.append("")
            lines.append("Theft Indicators:")
            for i in indicators[:4]:
                lines.append(f"  🚨 {i}")
        
        thief_desc = theft.get("thief_description", [])
        if thief_desc and theft.get("theft_indicated"):
            lines.append("")
            lines.append("Possible Thief Description:")
            for d in thief_desc[:3]:
                lines.append(f"  👤 {d}")
        
        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        lost_missing_houses = {2, 4, 6, 7, 8, 11, 12}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in lost_missing_houses:
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
                conditions.append("Combust")
            if info.get('lord_is_retrograde'):
                conditions.append("Retrograde")
            condition_str = ", ".join(conditions) if conditions else "Normal"
            
            planets = ", ".join(info.get('planets_in_house', [])) or "None"
            
            lines.append(f"• H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | {dignity} | {condition_str} | Str:{strength}/100 | Planets:{planets}")
        
        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        """Format aspects data concisely"""
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
                lines.append(f"• H{house_num}: Benefic={benefic_str} | Malefic={malefic_str}")
        
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
        """Main routing method - routes to appropriate specialized builder"""
        
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            
            # Route based on sub_subdomain
            if "Direction" in sub_subdomain:
                return self._build_direction_prompt(question, additional_data, raw, language)
            
            elif "Theft" in sub_subdomain:
                return self._build_theft_prompt(question, additional_data, raw, language)
            
            elif "Recovery" in sub_subdomain or "Prospects" in sub_subdomain:
                return self._build_recovery_prompt(question, additional_data, raw, language)
            
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language)
            
            else:
                # Default: General lost item recovery
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

You are an expert Vedic astrologer specializing in finding lost items and missing persons.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
Include practical search guidance.
End with a clear actionable statement.
For missing persons, recommend involving authorities.
"""

    # ==========================================================================
    # GENERAL PROMPT (Lost Item Recovery)
    # ==========================================================================
    def _build_general_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for general lost item/person recovery questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        recovery_likelihood = self._get_recovery_likelihood(additional_data)
        recovery_score = self._get_recovery_score(additional_data)
        theft_indicated = self._is_theft_indicated(additional_data)
        primary_direction = self._get_primary_direction(additional_data)
        
        recovery_data = self._format_recovery_analysis(additional_data)
        direction_data = self._format_direction_analysis(additional_data)
        theft_data = self._format_theft_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        # Get language-specific text
        example_4th = self._get_example_text(language, "4th_house")
        example_11th = self._get_example_text(language, "11th_house")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_recovery = self._get_example_text(language, "recovery_outlook")
        starters = self._get_analysis_starters(language)

        # Determine if missing person or item (for sensitivity)
        is_missing_person = any(kw in question.lower() for kw in ['person', 'someone', 'व्यक्ति', 'कोई', 'missing person'])

        sensitivity_note = ""
        if is_missing_person:
            sensitivity_note = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ MISSING PERSON QUERY - EXTRA SENSITIVITY REQUIRED
═══════════════════════════════════════════════════════════════════════════════
- Be especially compassionate and hopeful
- NEVER suggest permanent loss or death
- Recommend involving police/authorities
- Focus on constructive guidance
- Provide emotional support alongside astrological guidance
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: LOST ITEM / MISSING PERSON RECOVERY
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Recovery Likelihood: {recovery_likelihood} ({recovery_score}/100)
Theft Indicated: {'YES' if theft_indicated else 'NO'}
Primary Direction: {primary_direction}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{sensitivity_note}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{recovery_data}

{direction_data}

{theft_data if theft_indicated else ""}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_recovery}: {recovery_likelihood}
Brief assessment of recovery chances.
{"Mention theft indicators." if theft_indicated else ""}
Mention primary direction to search.
NO astrological terms here. Write as a caring advisor.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 4th house (property/home items)
- 2nd house (valuables/possessions)
- 11th house (recovery prospects)
- Explain what these indicate

PARAGRAPH 2 – Recovery Factors:
"{example_11th}"
Explain favorable and unfavorable factors for recovery.

PARAGRAPH 3 – Direction Guidance:
Where to search based on planetary positions.
Include element-based location hints.
- Prioritize PRIMARY direction only
- Secondary directions are supportive, not equal
- Do NOT introduce new directions not present in evaluator data


{"PARAGRAPH 4 – Theft Analysis:" if theft_indicated else ""}
{f"Explain theft indicators and possible thief description." if theft_indicated else ""}

PARAGRAPH {"5" if theft_indicated else "4"} – Practical Search Guidance:
Specific places to look based on astrological indicators.
{"Recommend involving authorities for missing person." if is_missing_person else ""}

SUMMARY:
{lbl_tell}: "[Recovery likelihood + Primary direction + Specific action steps]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Remedy for strengthening recovery prospects
- Mantra or worship recommendation

REMEDIES_GENERAL:
- Practical search tips
- {"Involve police/authorities" if is_missing_person else "Check common places"}
- Keep hope and persistence

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # DIRECTION PROMPT
    # ==========================================================================
    def _build_direction_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for direction guidance questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        primary_direction = self._get_primary_direction(additional_data)
        direction_data = self._format_direction_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_direction = self._get_example_text(language, "direction_outlook")
        starters = self._get_analysis_starters(language)

        # Direction-specific text
        direction_text = self._get_example_text(language, f"direction_{primary_direction.lower()}")
        if not direction_text:
            direction_text = f"Search towards {primary_direction} direction"

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: DIRECTION GUIDANCE FOR LOST ITEM/PERSON
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Primary Direction: {primary_direction}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
DIRECTION ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{direction_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_direction}: {direction_text}
Brief direction guidance.
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- 4th lord's position and sign (primary direction indicator)
- 7th lord's position (for missing persons)
- Moon's position (general indicator)

PARAGRAPH 2 – Direction Reasoning:
Explain WHY this direction is indicated.
Connect planetary signs to directions.

PARAGRAPH 3 – Location Type:
Based on element (Fire/Earth/Air/Water), describe:
- Type of location (indoor/outdoor, floor level, etc.)
- Specific areas to search

PARAGRAPH 4 – Search Strategy:
Practical step-by-step search approach.
Start from indicated direction and expand.

SUMMARY:
{lbl_tell}: "[Primary direction + specific location type + search strategy]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Prayer or mantra for guidance

REMEDIES_GENERAL:
- Systematic search approach
- Ask neighbors/friends in indicated direction

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # THEFT PROMPT
    # ==========================================================================
    def _build_theft_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for theft analysis questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        theft_indicated = self._is_theft_indicated(additional_data)
        theft_data = self._format_theft_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_theft = self._get_example_text(language, "theft_outlook")
        theft_msg = self._get_example_text(language, "theft_indicated") if theft_indicated else self._get_example_text(language, "loss_indicated")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: THEFT VS LOSS ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Theft Indicated: {'YES' if theft_indicated else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY NOTE:
═══════════════════════════════════════════════════════════════════════════════
- Present findings as "indications" not certainties
- Do not accuse specific individuals
- Recommend filing police report if theft is strongly indicated
- Focus on recovery rather than blame
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
THEFT ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{theft_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_theft}: {theft_msg}
Brief assessment.
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- 6th house analysis (theft/enemies)
- 2nd and 4th house afflictions
- Mars, Rahu, Saturn involvement

PARAGRAPH 2 – Theft Indicators:
{"Explain why theft is indicated based on planetary positions." if theft_indicated else "Explain why this appears to be misplacement rather than theft."}

{"PARAGRAPH 3 – Thief Description (General):" if theft_indicated else ""}
{"Based on 7th lord, describe general characteristics WITHOUT accusing anyone specific." if theft_indicated else ""}

PARAGRAPH {"4" if theft_indicated else "3"} – Next Steps:
{"Recommend filing police report and practical recovery steps." if theft_indicated else "Suggest where to search for misplaced item."}

SUMMARY:
{lbl_tell}: "[{'Theft indicated - file report' if theft_indicated else 'Likely misplaced'} + recovery guidance]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
{"- Hanuman Chalisa for protection and recovery" if theft_indicated else "- Prayer for guidance to find item"}

REMEDIES_GENERAL:
{"- File police report" if theft_indicated else "- Check common places systematically"}
- Inform neighbors/community
- Keep hope

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # RECOVERY PROSPECTS PROMPT
    # ==========================================================================
    def _build_recovery_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for recovery prospects questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        recovery_likelihood = self._get_recovery_likelihood(additional_data)
        recovery_score = self._get_recovery_score(additional_data)
        recovery_data = self._format_recovery_analysis(additional_data)
        direction_data = self._format_direction_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_recovery = self._get_example_text(language, "recovery_outlook")
        recovery_msg = self._get_example_text(language, "recovery_high") if recovery_score >= 60 else self._get_example_text(language, "recovery_low")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: RECOVERY PROSPECTS ANALYSIS
Current Date: {today_str}
Weightage: VEDIC 100% (No KP, No Timing)
Recovery Likelihood: {recovery_likelihood} ({recovery_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
RECOVERY ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{recovery_data}

{direction_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_recovery}: {recovery_likelihood} ({recovery_score}/100)
{recovery_msg}
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- 11th house (recovery/gains)
- 4th house (property)
- 2nd house (possessions)
- Jupiter's influence

PARAGRAPH 2 – Favorable Factors:
Explain factors supporting recovery.

PARAGRAPH 3 – Challenging Factors:
Explain obstacles (frame constructively).

PARAGRAPH 4 – Timing Hints:
Any indications about when recovery might be possible.
(DO NOT invent specific dates)

PARAGRAPH 5 – Practical Guidance:
Specific actions to improve recovery chances.

SUMMARY:
{lbl_tell}: "[Recovery likelihood + What to do + Maintain hope]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Strengthen 11th lord for gains
- Jupiter remedies for blessings

REMEDIES_GENERAL:
- Persistence in search
- Spread the word
- Keep faith

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
        
        recovery_likelihood = self._get_recovery_likelihood(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REMEDIES FOR FINDING LOST ITEM/PERSON
Current Date: {today_str}
Weightage: VEDIC 100%
Recovery Likelihood: {recovery_likelihood}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR LOST/MISSING:
═══════════════════════════════════════════════════════════════════════════════

- Recommend MAXIMUM 2 astrological remedies
- Choose remedies linked to the MOST AFFECTED planet only

11th LORD WEAK: Strengthen for recovery - gemstone/mantra of 11th lord
4th LORD AFFLICTED: Remedies for property protection
MOON WEAK: Monday fasts, white items, Shiva worship for mental peace
JUPITER AFFLICTED: Thursday fasts, yellow items, Vishnu worship
MERCURY WEAK: Communication remedies to get information

Traditional Remedies:
- Hanuman Chalisa for protection and recovery
- Goddess Durga prayers for finding lost items
- Karya Siddhi Hanuman prayers
- Sankat Mochan Hanuman Ashtak
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
What challenges exist and how remedies can help.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin with:
"{starters['vedic']}"

- Identify weak planets affecting recovery
- Main astrological challenges

PARAGRAPH 2 – Primary Remedy:
Most important remedy and WHY it will help.

PARAGRAPH 3 – Supporting Remedies:
Additional helpful practices.

SUMMARY:
{lbl_tell}: "[Priority order of remedies + practical steps]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
1. [Primary mantra/worship with instructions]
2. [Secondary remedy]
3. [Gemstone if applicable]

REMEDIES_GENERAL:
- Systematic search
- Community involvement
- Persistence and faith

═══════════════════════════════════════════════════════════════════════════════
"""

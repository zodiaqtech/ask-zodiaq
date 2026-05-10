"""
Child Health Guidance – LLM Prompts v8.0 (VEDIC / VPIC ONLY - ENHANCED)

ENHANCEMENTS IN v8.0:
✅ Output language based on user selection (not hardcoded Hindi)
✅ VEDIC/VPIC ONLY - NO KP system used for health
✅ Astrological analysis examples in SELECTED language (not hardcoded Hindi)
✅ Paragraph-based output structure
✅ Child-safe, supportive, care-oriented language
✅ Compatible with ChildHealthGuidanceEvaluator

PRINCIPLES:
✅ Pure Vedic / VPIC astrology only
❌ NO KP system, cusp sub lords, or significators
❌ NO concrete disease prediction
✅ Focus on constitution, sensitivity, support, prevention
✅ Dasha used ONLY as contextual phase (not prediction)

Weightage:
- NON-TIMING: Vedic 85% + Aspects 15% (NO KP, NO DASHA TIMING)

Question Handling:
- Question 1 (Physical Growth): VEDIC ONLY
- Question 2 (Emotional Wellbeing): VEDIC ONLY  
- Question 3 (Preventive Care): VEDIC ONLY
- Question 4 (Remedy and Suggestion): VEDIC ONLY

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from ChildHealthGuidanceEvaluator):
═══════════════════════════════════════════════════════════════════════════════

additional_data["child_health_house_lords"] = {...}
additional_data["child_health_house_aspects"] = {...}
additional_data["child_health_house_config"] = {...}
additional_data["child_health_analysis_summary"] = {...}
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

DOMAIN_PREFIX = "child_health"


class ChildHealthGuidancePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Child → Health Guidance
    v8.0 - Fixed language handling, VEDIC ONLY (no KP for health)
    """

    domain = "Child"
    subtopic = "Health Guidance"

    # ==========================================================================
    # LANGUAGE INSTRUCTION (Dynamic based on selection)
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
                "1st_house": "लग्न भाव के स्वामी [planet] [house] भाव में [sign] राशि में स्थित हैं। इसका अर्थ है कि बच्चे की शारीरिक जीवनी शक्ति और प्रतिरक्षा क्षमता...",
                "5th_house": "पंचम भाव के स्वामी [planet] [house] भाव में हैं, जो विकास और मानसिक कल्याण को दर्शाता है...",
                "6th_house": "षष्ठम भाव के स्वामी [planet] [house] भाव में हैं, जो स्वास्थ्य संवेदनशीलता के क्षेत्रों को इंगित करता है...",
                "moon": "चंद्रमा भावनात्मक कल्याण और पोषण का कारक है। चंद्रमा [position] में होने से...",
                "sun": "सूर्य जीवनी शक्ति और ऊर्जा का कारक है। सूर्य [position] में होने से...",
                "general_answer": "सामान्य मार्गदर्शन",
                "astrological_analysis": "ज्योतिषीय अंतर्दृष्टि",
                "summary": "सहायक मार्गदर्शन",
                "remedies": "सहायक सुझाव",
                "tell_client": "अभिभावकों को बताएं",
                "constitution_outlook": "संविधान और जीवनी शक्ति",
                "growth_outlook": "विकास और कल्याण",
                "sensitivity_outlook": "देखभाल के क्षेत्र",
                "disclaimer": "अस्वीकरण"
            },
            "English": {
                "1st_house": "The lord of 1st house (Ascendant) [planet] is placed in [house] house in [sign]. This indicates the child's physical vitality and immunity capacity...",
                "5th_house": "The lord of 5th house [planet] is placed in [house] house, indicating growth and mental well-being...",
                "6th_house": "The lord of 6th house [planet] is placed in [house] house, pointing to areas of health sensitivity...",
                "moon": "Moon is the karaka for emotional well-being and nourishment. Moon being in [position] indicates...",
                "sun": "Sun is the karaka for vitality and energy. Sun being in [position] indicates...",
                "general_answer": "General Guidance",
                "astrological_analysis": "Astrological Insights",
                "summary": "Supportive Guidance",
                "remedies": "Supportive Suggestions",
                "tell_client": "TELL PARENTS",
                "constitution_outlook": "Constitution and Vitality",
                "growth_outlook": "Growth and Well-being",
                "sensitivity_outlook": "Care Areas",
                "disclaimer": "Disclaimer"
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
                "constitution": "शारीरिक संविधान के संदर्भ में,",
                "growth": "विकास और कल्याण के संबंध में,",
                "care": "देखभाल और सहायता के क्षेत्रों के बारे में,"
            },
            "English": {
                "vedic": "According to Vedic astrology,",
                "constitution": "Regarding physical constitution,",
                "growth": "In terms of growth and well-being,",
                "care": "Concerning areas needing care and support,"
            }
        }.get(language, {
            "vedic": "According to Vedic astrology,",
            "constitution": "Regarding physical constitution,",
            "growth": "In terms of growth and well-being,",
            "care": "Concerning areas needing care and support,"
        })

    # ==========================================================================
    # SYSTEM PROMPT (Language-dynamic, VEDIC ONLY)
    # ==========================================================================
    def build_system_prompt(self, language: str = "English") -> str:
        """Build system prompt with language-appropriate examples - VEDIC ONLY"""
        
        # Get language-specific examples
        example_1st = self._get_example_text(language, "1st_house")
        
        return f"""You are an expert Classical Vedic astrologer specializing in CHILD HEALTH, WELL-BEING, and DEVELOPMENT.

**VEDIC/VPIC ONLY - NO KP SYSTEM**
**Weightage: Vedic 85% + Aspects 15%**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 CRITICAL INTERPRETATION RULES (MANDATORY)
═══════════════════════════════════════════════════════════════════════════════

- This analysis is PURELY VEDIC / VPIC
- ❌ DO NOT use KP (Krishnamurti Paddhati) methods
- ❌ DO NOT use cusp sub lords, significators, or event promises
- ❌ DO NOT predict specific diseases or medical outcomes
- ❌ DO NOT use fatalistic or fear-inducing language

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "1st Lord Mars in 6th house. Debilitated. Malefic."
   ✅ "{example_1st}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for the child's well-being
   - Connect to supportive guidance

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL PARENTS:" ONLY IN FINAL SUMMARY

5. ANSWER THE ACTUAL QUESTION DIRECTLY

═══════════════════════════════════════════════════════════════════════════════
                    VEDIC HEALTH INTERPRETATION FRAMEWORK
═══════════════════════════════════════════════════════════════════════════════

- 1st house → Physical vitality, immunity, constitution (PRIMARY)
- 5th house → Growth, development, mental well-being (PRIMARY)
- 6th house → Sensitivity areas, immunity challenges
- 8th house → Chronic tendencies, recovery capacity
- 12th house → Rest patterns, sleep, emotional balance

═══════════════════════════════════════════════════════════════════════════════
                    DASHA RULES (STRICT)
═══════════════════════════════════════════════════════════════════════════════

- ✅ Use dasha ONLY if explicitly provided
- ❌ NEVER invent dasha periods
- ❌ NEVER say "this dasha causes illness"
- ❌ Do NOT attribute health traits, delays, sensitivity to dasha lords
- ✅ Dasha may ONLY be described as a time requiring more care or attentiveness
- ✅ Use dashas to explain phases of support or need for care

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ CHILD-SAFE LANGUAGE RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

LANGUAGE SAFETY FILTER (MANDATORY):
✅ Allowed terms: sensitivity, support, care, balance, resilience, nourishment, 
   attention, nurturing, encouragement, routine, stability
❌ Disallowed terms: issue, disorder, illness, delay, problem, condition, 
   disease, defect, weakness, failure

FRAMING RULES:
- NEVER conclude that a child has health "problems" or "issues"
- Frame as "areas needing extra care" or "sensitivity to be supported"
- All observations are CARE-ORIENTED, not DIAGNOSTIC
- Astrology guides parents, it does NOT diagnose children
- Frame challenges as TEMPORARY and ADDRESSABLE with care

MEDICAL SAFETY:
- Astrology is NOT a substitute for medical advice
- Always encourage professional consultation where relevant
- Emphasize preventive care and supportive routines

REMEDY SAFETY RULES (CHILD-SPECIFIC):
- ❌ NO gemstones, metals, or planetary prescriptions for children
- ❌ NO ritual obligations for the child
- ✅ Allowed: routine improvements, calming environments, parental practices
- ✅ Remedies must be optional and lifestyle-based
"""

    # ==========================================================================
    # HELPER METHODS - DATA EXTRACTION (VEDIC ONLY)
    # ==========================================================================

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        health_houses = {1, 5, 6, 8, 12}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in health_houses:
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

    def _format_current_dasha(self, kwargs: Dict) -> str:
        """Format current dasha concisely"""
        current_dasha = kwargs.get('current_dasha', {})
        if not current_dasha:
            return ""
        
        try:
            dasha_name = current_dasha.get('dasha_name', '')
            date_range = current_dasha.get('date_range', {})
            start = date_range.get('start', 'Unknown')
            end = date_range.get('end', 'Unknown')
            
            return f"CURRENT DASHA: {dasha_name} ({start} to {end})"
        except Exception:
            return ""

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

    def _format_dasha_timeline(self, kwargs: Dict) -> str:
        """Format dasha timeline"""
        dasha_timeline = kwargs.get('dasha_timeline', {})
        if not dasha_timeline:
            return ""
        
        try:
            current = dasha_timeline.get('current', [])
            future = dasha_timeline.get('next_10_years', [])
            
            if not any([current, future]):
                return ""
            
            lines = ["DASHA TIMELINE:"]
            
            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus', 'Ra': 'Rahu', 'Ke': 'Ketu',
            }
            
            def parse_dasha(name):
                parts = name.replace('>', '-').split('-')
                return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts])
            
            if current:
                lines.append("\n🔴 CURRENT:")
                for d in current[:3]:
                    parsed = parse_dasha(d.get('dasha_name', ''))
                    dr = d.get('date_range', {})
                    lines.append(f"  • {parsed} ({dr.get('start', '')} to {dr.get('end', '')})")
            
            if future:
                lines.append("\n⏭️ UPCOMING (Next 10 Years):")
                for i, d in enumerate(future[:8], 1):
                    parsed = parse_dasha(d.get('dasha_name', ''))
                    dr = d.get('date_range', {})
                    lines.append(f"  {i}. {parsed} ({dr.get('start', '')} to {dr.get('end', '')})")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for health context"""
        meanings = {
            1: "Physical Vitality/Constitution",
            5: "Growth/Mental Well-being",
            6: "Sensitivity Areas",
            8: "Recovery Capacity",
            12: "Rest/Emotional Balance"
        }
        return meanings.get(house_num, "General")

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
            additional_data = kwargs.pop("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            
            # Route based on sub_subdomain
            if "Physical Growth" in sub_subdomain:
                return self._build_physical_growth_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Emotional" in sub_subdomain:
                return self._build_emotional_wellbeing_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Preventive" in sub_subdomain:
                return self._build_preventive_care_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Remedy" in sub_subdomain or "Suggestion" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language, **kwargs)
            
            else:
                return self._build_general_prompt(question, additional_data, raw, language, **kwargs)
        
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

You are an expert Vedic astrologer specializing in child health and well-being. Answer the following question.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear supportive statement.
Use child-safe, care-oriented language throughout.
Always recommend consulting healthcare professionals for medical concerns.
"""

    # ==========================================================================
    # PHYSICAL GROWTH PROMPT (Question 1) - VEDIC ONLY
    # ==========================================================================
    def _build_physical_growth_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Physical Growth questions - VEDIC ONLY"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # VEDIC ONLY - no KP for health
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        timeline_data = self._format_dasha_timeline(kwargs)
        
        # Get language-specific text
        example_1st = self._get_example_text(language, "1st_house")
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_constitution = self._get_example_text(language, "constitution_outlook")
        lbl_growth = self._get_example_text(language, "growth_outlook")
        lbl_disclaimer = self._get_example_text(language, "disclaimer")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PHYSICAL GROWTH AND HEALTH GUIDANCE
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - NO KP for health)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
SPECIAL FOCUS – PHYSICAL GROWTH:
- Emphasize 1st and 5th house strength
- Avoid emotional or disease-heavy language
- Focus on vitality, stamina, nourishment
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{timeline_data if timeline_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Calm, reassuring assessment of the child's physical vitality.
NO medical terms or fear-inducing language.
Write supportively for parents.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – {lbl_constitution}:
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 1st house lord (physical vitality, immunity)
- Sun's role in energy and constitution
- Overall resilience assessment

PARAGRAPH 2 – {lbl_growth}:
Begin with:
"{starters['growth']}"

- 5th house analysis (growth, development)
- Physical and mental development indicators
- Supportive factors for growth

PARAGRAPH 3 – CARE AREAS (Sensitivity, not problems):
Begin with:
"{starters['care']}"

- 6th house sensitivity areas (frame as needing extra care)
- Areas where attention supports well-being
- Always frame positively

PARAGRAPH 4 – DASHA CONTEXT (If provided):
How the current phase supports stability or requires extra attentiveness.
NO event-based or medical predictions.

**{lbl_summary}:**
{lbl_tell}: "[Clear supportive guidance for parents on nurturing physical well-being]"

**{lbl_remedies}:**
- Routine-based suggestions (sleep, diet, activity)
- Calming environment recommendations
- NO gemstones or ritual prescriptions for children

**{lbl_disclaimer}:**
Astrology provides supportive guidance. For any health concerns, please consult a pediatrician or healthcare professional.

═══════════════════════════════════════════════════════════════════════════════
Remember: Child-safe, care-oriented language throughout.
NO KP analysis. VEDIC ONLY.
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # EMOTIONAL WELLBEING PROMPT - VEDIC ONLY
    # ==========================================================================
    def _build_emotional_wellbeing_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Emotional Wellbeing questions - VEDIC ONLY"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_disclaimer = self._get_example_text(language, "disclaimer")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: EMOTIONAL WELLBEING GUIDANCE
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - NO KP for health)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
SPECIAL FOCUS – EMOTIONAL WELLBEING:
- Emphasize Moon, 4th house, 5th house, and benefic aspects
- Discuss emotional sensitivity and reassurance
- Avoid physical illness references
- Focus on nurturing and emotional support
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Warm, reassuring assessment of the child's emotional nature.
Focus on nurturing and support.

**{lbl_analysis}:**

PARAGRAPH 1 – EMOTIONAL NATURE:
Begin strictly with:
"{starters['vedic']}"

- Moon's placement and strength (emotional foundation)
- 4th house (emotional security, home environment)
- 5th house (mental well-being, creativity)

PARAGRAPH 2 – EMOTIONAL SENSITIVITY:
How the child processes emotions and what support helps.
Frame sensitivity as a quality to nurture, not a problem.

PARAGRAPH 3 – SUPPORTIVE FACTORS:
Benefic aspects and planetary strengths that support emotional balance.

PARAGRAPH 4 – NURTURING ENVIRONMENT:
What kind of environment and approach best supports this child.

**{lbl_summary}:**
{lbl_tell}: "[Clear guidance on supporting emotional well-being]"

**{lbl_remedies}:**
- Calming routines and environments
- Emotional connection suggestions
- NO gemstones or rituals for children

**{lbl_disclaimer}:**
For any emotional or behavioral concerns, please consult appropriate professionals.

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # PREVENTIVE CARE PROMPT - VEDIC ONLY
    # ==========================================================================
    def _build_preventive_care_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Preventive Care questions - VEDIC ONLY"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_sensitivity = self._get_example_text(language, "sensitivity_outlook")
        lbl_disclaimer = self._get_example_text(language, "disclaimer")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PREVENTIVE CARE GUIDANCE
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - NO KP for health)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
SPECIAL FOCUS – PREVENTIVE CARE:
- Focus on routines, balance, diet, sleep
- Frame astrology as early-awareness guidance
- Emphasize proactive care, not reactive treatment
- Guide parents on supportive practices
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Proactive, supportive guidance on preventive care.
Frame as early awareness, not prediction.

**{lbl_analysis}:**

PARAGRAPH 1 – CONSTITUTION OVERVIEW:
Begin strictly with:
"{starters['vedic']}"

- 1st house lord strength (overall vitality)
- Natural constitution and resilience

PARAGRAPH 2 – {lbl_sensitivity}:
Begin with:
"{starters['care']}"

- Areas where extra care and attention help (6th, 8th, 12th houses)
- Frame as "benefits from attention" not "vulnerable to"

PARAGRAPH 3 – SEASONAL/PERIODIC CARE:
Based on planetary influences, when extra care may be beneficial.

PARAGRAPH 4 – PROACTIVE MEASURES:
Lifestyle factors that support overall well-being.

**{lbl_summary}:**
{lbl_tell}: "[Clear preventive care guidance for parents]"

**{lbl_remedies}:**
- Daily routine suggestions (sleep, meals, activity)
- Seasonal care considerations
- Environmental factors
- NO gemstones or rituals for children

**{lbl_disclaimer}:**
This is supportive guidance only. Regular health check-ups with healthcare professionals are always recommended.

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # REMEDIES PROMPT - VEDIC ONLY
    # ==========================================================================
    def _build_remedies_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Health Remedies and Suggestions - VEDIC ONLY"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_disclaimer = self._get_example_text(language, "disclaimer")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: SUPPORTIVE PRACTICES AND SUGGESTIONS
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - NO KP for health)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
SPECIAL FOCUS – SUPPORTIVE PRACTICES:
- ONLY non-invasive, routine-based suggestions
- NO gemstones or metals for children
- NO medical claims or treatments
- Focus on environment, routines, parental practices
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY SAFETY RULES (CHILD-SPECIFIC - STRICT):
═══════════════════════════════════════════════════════════════════════════════

❌ NEVER RECOMMEND FOR CHILDREN:
- Gemstones (Ruby, Pearl, Coral, etc.)
- Metals or rings
- Fasting or dietary restrictions
- Ritual obligations for the child
- Mantras the child must recite

✅ ALLOWED FOR CHILDREN:
- Sleep routine improvements
- Calming environments (colors, sounds)
- Quality time with parents
- Outdoor activity suggestions
- Dietary balance (not restrictions)
- Parental practices on behalf of child
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Supportive measures that can help nurture the child's well-being.

**{lbl_analysis}:**

PARAGRAPH 1 – AREAS FOR SUPPORT:
Begin strictly with:
"{starters['vedic']}"

- Identify planetary factors that suggest areas needing attention
- Frame as opportunities for nurturing, not problems

PARAGRAPH 2 – ENVIRONMENTAL SUPPORT:
How the home environment can support well-being.

PARAGRAPH 3 – ROUTINE SUPPORT:
Daily routines that align with the child's nature.

**{lbl_summary}:**
{lbl_tell}: "[Priority supportive practices for parents]"

**{lbl_remedies} (Detailed - Child-Safe Only):**
1. [Primary routine/environment suggestion]
2. [Secondary supportive practice]
3. [Parental practice on behalf of child, if applicable]

**{lbl_disclaimer}:**
These are supportive lifestyle suggestions only. They do not replace medical advice or professional guidance.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: All suggestions must be child-safe, non-invasive, and lifestyle-based.
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # GENERAL PROMPT (Fallback)
    # ==========================================================================
    def _build_general_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build general prompt for unclassified health questions - VEDIC ONLY"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(kwargs)
        timeline_data = self._format_dasha_timeline(kwargs)
        starters = self._get_analysis_starters(language)
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_disclaimer = self._get_example_text(language, "disclaimer")

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: CHILD HEALTH GUIDANCE (General)
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - NO KP for health)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{timeline_data if timeline_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Calm, reassuring, supportive assessment.
NO medical terms. Write for parents.

**{lbl_analysis}:**
Flowing paragraphs with facts AND interpretations.

PARAGRAPH 1 – CONSTITUTION & VITALITY:
Begin with:
"{starters['vedic']}"

- 1st house (physical vitality)
- 5th house (growth, development)
- Overall resilience

PARAGRAPH 2 – SENSITIVITY AREAS:
Begin with:
"{starters['care']}"

- Areas needing extra care (frame supportively)
- 6th house sensitivity

PARAGRAPH 3 – DASHA CONTEXT (If provided):
Current phase and what it means for attention and care.

**{lbl_summary}:**
{lbl_tell}: "[Clear supportive guidance]"

**{lbl_remedies}:**
- Routine-based suggestions only
- NO gemstones or rituals for children

**{lbl_disclaimer}:**
For any health concerns, please consult a pediatrician or healthcare professional.

═══════════════════════════════════════════════════════════════════════════════
Remember: Child-safe, care-oriented language. VEDIC ONLY.
═══════════════════════════════════════════════════════════════════════════════
"""
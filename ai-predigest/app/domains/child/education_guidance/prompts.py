"""
Education Guidance – LLM Prompts v8.0 (Children Domain - ENHANCED)

ENHANCEMENTS IN v8.0:
✅ Output language based on user selection (not hardcoded Hindi)
✅ If KP points have no relevant info → Only Vedic analysis
✅ If state NOT BLOCKED → Show timing windows
✅ If state BLOCKED → General dasha info + "keep trying" (no specific timing)
✅ Astrological analysis examples in SELECTED language (not hardcoded Hindi)
✅ VEDIC FIRST, then KP in astrological analysis (paragraph separation)
✅ Paragraph-based output to prevent Vedic/KP leakage
✅ Child-safe, supportive language throughout
✅ Compatible with EducationGuidanceEvaluator v3.0

Weightage:
- TIMING: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
- NON-TIMING: Vedic 85% + KP Facts 15% (No Dasha)

Question Handling:
- Question 1 (Aptitude and Education): KP Points + Vedic
- Question 2 (Prospects of Success): VEDIC ONLY
- Question 3 (Prospects of College): KP Points + Vedic
- Question 4 (Foreign Education): KP Points + Timing Windows

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from EducationGuidanceEvaluator v3.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["child_education_kp_promise"] = {
    "has_promise": bool,
    "points": [...]  # KP education evaluation points
}

additional_data["child_education_timing_windows"] = {
    "has_timing": bool,
    "best_window": {...},
    "nearest_window": {...},
    "all_favorable": [...]
}

additional_data["child_education_house_lords"] = {...}
additional_data["child_education_house_aspects"] = {...}
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

DOMAIN_PREFIX = "child_education"


class EducationGuidancePromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Child → Education Guidance
    v8.0 - Fixed language handling and KP/timing logic
    """

    domain = "Child"
    subtopic = "Education Guidance"

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
                "5th_house": "पंचम भाव के स्वामी [planet] [house] भाव में [sign] राशि में स्थित हैं। इसका अर्थ है कि बच्चे की बुद्धि और सीखने की क्षमता...",
                "4th_house": "चतुर्थ भाव के स्वामी [planet] [house] भाव में हैं, जो शिक्षा की नींव और विद्यालयीन वातावरण को दर्शाता है...",
                "9th_house": "नवम भाव के स्वामी [planet] [house] भाव में हैं, जो उच्च शिक्षा और मार्गदर्शन को प्रभावित करता है...",
                "mercury": "बुध बुद्धि और सीखने का कारक है। बुध [position] में होने से...",
                "jupiter": "गुरु ज्ञान और शिक्षा का कारक है। गुरु [position] में होने से...",
                "timing_unavailable": "शिक्षा संबंधी विशिष्ट समय की गणना वर्तमान में उपलब्ध नहीं है।",
                "blocked_message": "शिक्षा में कुछ चुनौतियां हैं। धैर्य और निरंतर प्रयास से सफलता मिलेगी।",
                "general_answer": "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary": "सारांश",
                "remedies": "उपाय",
                "tell_client": "अभिभावकों को बताएं",
                "education_outlook": "शिक्षा संभावना",
                "aptitude_outlook": "योग्यता और प्रतिभा",
                "success_outlook": "सफलता की संभावना",
                "foreign_outlook": "विदेश शिक्षा संभावना",
                "college_outlook": "कॉलेज प्रवेश संभावना"
            },
            "English": {
                "5th_house": "The lord of 5th house [planet] is placed in [house] house in [sign]. This means for the child's intelligence and learning ability...",
                "4th_house": "The lord of 4th house [planet] is placed in [house] house, indicating the educational foundation and school environment...",
                "9th_house": "The lord of 9th house [planet] is placed in [house] house, affecting higher education and guidance...",
                "mercury": "Mercury is the karaka for intelligence and learning. Mercury being in [position] indicates...",
                "jupiter": "Jupiter is the karaka for knowledge and education. Jupiter being in [position] indicates...",
                "timing_unavailable": "Specific timing for education could not be calculated at this time.",
                "blocked_message": "There are some challenges in education. Success will come with patience and consistent effort.",
                "general_answer": "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary": "Summary",
                "remedies": "Remedies",
                "tell_client": "TELL PARENTS",
                "education_outlook": "Education Outlook",
                "aptitude_outlook": "Aptitude and Talent",
                "success_outlook": "Success Prospects",
                "foreign_outlook": "Foreign Education Prospects",
                "college_outlook": "College Admission Prospects"
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
    # SYSTEM PROMPT (Language-dynamic)
    # ==========================================================================
    def build_system_prompt(self, language: str = "English", is_timing: bool = False) -> str:
        """Build system prompt with language-appropriate examples"""
        
        if is_timing:
            weightage_text = "TIMING QUESTION: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%"
        else:
            weightage_text = "NON-TIMING QUESTION: Vedic 85% + KP Facts 15% (No Dasha needed)"
        
        # Get language-specific examples
        example_5th = self._get_example_text(language, "5th_house")
        
        return f"""You are an expert KP and Vedic astrologer specializing in CHILD EDUCATION, LEARNING ABILITY, ACADEMIC POTENTIAL, AND DEVELOPMENT.

**{weightage_text}**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

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

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "5th Lord Jupiter in 9th house. Exalted. Benefic."
   ✅ "{example_5th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for the child's education
   - Connect to the outcome

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL PARENTS:" ONLY IN FINAL SUMMARY

5. ANSWER THE ACTUAL QUESTION DIRECTLY

═══════════════════════════════════════════════════════════════════════════════
                    KP RULES (When KP data present)
═══════════════════════════════════════════════════════════════════════════════

KP section contains ONLY pre-computed evaluator output:
✅ Education promise status (PROMISED / CONDITIONAL / NOT PROMISED)
✅ Subject aptitude indicators
✅ Scholarship/foreign education signals
✅ Learning challenges or strengths

KP section must NOT contain:
❌ LLM-derived KP analysis
❌ Reinterpretation of KP points
❌ Using Vedic to explain KP conclusions

IF KP POINTS HAVE NO RELEVANT INFO FOR THE QUESTION:
→ Skip KP section entirely
→ Provide ONLY Vedic analysis

═══════════════════════════════════════════════════════════════════════════════
                    KEY EDUCATION HOUSES (VEDIC ONLY)
═══════════════════════════════════════════════════════════════════════════════

- 5th: Intelligence, grasping power, creativity (PRIMARY)
- 4th: Foundational education, schooling environment (PRIMARY)
- 9th: Higher education, guidance, mentors (PRIMARY)
- 11th: Success, achievements, outcomes
- 1st: Learning attitude and confidence
- 2nd: Speech, memory, early learning
- 3rd: Effort, courage, practical skills

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ CHILD-SAFE LANGUAGE RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

- NEVER conclude that a child will "fail", "struggle permanently", or "lack intelligence"
- NO diagnosis or deterministic labeling
- Use developmental & supportive framing
- Focus on guidance, encouragement, environment
- If indicators are weak, frame as:
  • "needs support"
  • "requires structured guidance"
  • "may benefit from encouragement and method"
- Frame challenges as TEMPORARY and ADDRESSABLE
- Astrology guides, it does NOT limit a child's potential
"""

    # ==========================================================================
    # HELPER METHODS - KP DATA EXTRACTION
    # ==========================================================================
    
    def _get_kp_availability(self, additional_data: Dict) -> bool:
        """Check if KP education data is available"""
        if not additional_data:
            return False
        kp_promise = additional_data.get(f"{DOMAIN_PREFIX}_kp_promise", {})
        return bool(kp_promise.get("has_promise") and kp_promise.get("points"))

    def _get_relevant_kp_points(self, additional_data: Dict, question_type: str) -> List[str]:
        """
        Return ONLY KP points relevant to the question.
        For Question 2 (Prospects of Success), return empty - VEDIC ONLY
        """
        if not additional_data:
            return []

        # Question 2 (Prospects of Success) is VEDIC ONLY - no KP filtering needed
        if question_type == "success":
            return []  # Empty = no KP for this question

        kp_promise = additional_data.get(f"{DOMAIN_PREFIX}_kp_promise", {})
        if not kp_promise.get("has_promise"):
            return []
        
        points = kp_promise.get("points", [])
        if not points:
            return []

        # Keywords to filter by question type
        KP_KEYWORDS_BY_QUESTION = {
            "aptitude": [
                "intelligence", "aptitude", "learning", "grasping", 
                "5th", "mercury", "nipuna", "intellect"
            ],
            "college": [
                "college", "admission", "scholarship", "higher", 
                "9th", "institution", "4th"
            ],
            "foreign": [
                "foreign", "abroad", "overseas", "12th", "9th", 
                "rahu", "travel", "settlement"
            ],
            "general": [
                "education", "study", "learning", "school", "college"
            ]
        }

        keywords = KP_KEYWORDS_BY_QUESTION.get(
            question_type,
            KP_KEYWORDS_BY_QUESTION["general"]
        )

        # Filter points that contain relevant keywords
        relevant_points = []
        for point in points:
            point_lower = point.lower()
            if any(kw in point_lower for kw in keywords):
                relevant_points.append(point)

        return relevant_points

    def _is_blocked(self, additional_data: Dict) -> bool:
        """Check if education is blocked based on analysis"""
        if not additional_data:
            return False
        
        # Check house lord strengths
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return False
        
        # Count weak lords in primary houses (5, 4, 9)
        weak_count = 0
        for house_num in [5, 4, 9]:
            lord_info = house_lords.get(house_num, {})
            if lord_info.get("lord_strength_score", 50) < 25:
                weak_count += 1
        
        # Blocked only if all primary education houses are very weak
        return weak_count >= 3

    def _format_kp_education_data(self, additional_data: Dict, question_type: str) -> str:
        """Format KP education analysis - DATA ONLY"""
        relevant_points = self._get_relevant_kp_points(additional_data, question_type)
        
        if not relevant_points:
            return ""
        
        lines = ["KP EDUCATION DATA (Pre-computed by Evaluator):"]
        
        for i, point in enumerate(relevant_points[:10], 1):
            lines.append(f"• {point}")
        
        lines.append("")
        lines.append("NOTE: Simply restate these KP findings. Do NOT interpret further.")
        
        return "\n".join(lines)

    def _format_timing_windows(self, additional_data: Dict) -> str:
        """Format timing windows concisely"""
        if not additional_data:
            return ""
        
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get('has_timing'):
            return ""
        
        try:
            best = timing_data.get('best_window', {})
            nearest = timing_data.get('nearest_window', {})
            
            if not best and not nearest:
                return ""
            
            lines = ["TIMING WINDOWS:"]
            
            if best:
                lines.append(f"BEST: {best.get('dasha', 'N/A')} | {best.get('start', 'N/A')} to {best.get('end', 'N/A')} | Score: {best.get('final_score', 0):.0f}/100")
            
            if nearest and nearest != best:
                lines.append(f"NEAREST: {nearest.get('dasha', 'N/A')} | {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')} | Score: {nearest.get('final_score', 0):.0f}/100")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting timing: {e}")
            return ""

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        """Check if valid timing windows exist"""
        if not additional_data:
            return False
        
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get('has_timing'):
            return False
        
        best = timing_data.get('best_window', {})
        nearest = timing_data.get('nearest_window', {})
        
        return bool(best or nearest)

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        education_houses = {1, 2, 3, 4, 5, 9, 11}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in education_houses:
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

    def _format_current_dasha(self, additional_data: Dict) -> str:
        """Format current dasha concisely"""
        if not additional_data:
            return ""
        
        current_dasha = additional_data.get(f'{DOMAIN_PREFIX}_current_dasha', {})
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
        """Format comprehensive dasha timeline"""
        dasha_timeline = kwargs.get('dasha_timeline', {})
        if not dasha_timeline:
            return ""
        
        try:
            past = dasha_timeline.get('past_2_years', [])
            current = dasha_timeline.get('current', [])
            future = dasha_timeline.get('next_10_years', [])
            
            if not any([past, current, future]):
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
                for i, d in enumerate(future[:10], 1):
                    parsed = parse_dasha(d.get('dasha_name', ''))
                    dr = d.get('date_range', {})
                    lines.append(f"  {i}. {parsed} ({dr.get('start', '')} to {dr.get('end', '')})")
            
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

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
            if "Aptitude" in sub_subdomain:
                return self._build_aptitude_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Prospects of Success" in sub_subdomain:
                # Question 2 - VEDIC ONLY
                return self._build_success_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "College" in sub_subdomain:
                return self._build_college_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Foreign" in sub_subdomain:
                return self._build_foreign_prompt(question, additional_data, raw, language, **kwargs)
            
            elif "Remed" in sub_subdomain:
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

You are an expert Vedic astrologer specializing in child education. Answer the following question.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear supportive statement.
Use child-safe, encouraging language throughout.
"""

    # ==========================================================================
    # APTITUDE AND EDUCATION PROMPT (Question 1) - KP + Vedic
    # ==========================================================================
    def _build_aptitude_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Aptitude and Education questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get data
        kp_points = self._get_relevant_kp_points(additional_data, "aptitude")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)
        
        kp_data = self._format_kp_education_data(additional_data, "aptitude") if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        
        # Get language-specific text
        example_5th = self._get_example_text(language, "5th_house")
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_aptitude = self._get_example_text(language, "aptitude_outlook")
        starters = self._get_analysis_starters(language)

        # KP section - only if relevant points exist
        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: APTITUDE AND EDUCATION OF CHILD
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
{lbl_aptitude}.
Mention natural talents and learning style.
NO astrological terms here. Write supportively for parents.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 5th house (intelligence, creativity)
- 4th house (foundational education)
- Mercury's role in learning
- Jupiter's role in wisdom

{"PARAGRAPH 2 – KP CONFIRMATION:" if has_relevant_kp else ""}

{f'This paragraph MUST begin with: "{starters["kp"]}" and ONLY restate KP findings. The entire paragraph must remain KP-only. Do NOT switch to Vedic reasoning.'
 if has_relevant_kp else ""}

PARAGRAPH {"3" if has_relevant_kp else "2"} - Supporting Factors:
9th house (higher guidance), 11th house (achievements).

PARAGRAPH {"4" if has_relevant_kp else "3"} - Learning Environment:
Recommended learning approach and environment.

**{lbl_summary}:**
{lbl_tell}: "[Clear guidance on the child's aptitude and how to support them]"

**{lbl_remedies}:**
Supportive, encouraging remedies (no fear-based).

═══════════════════════════════════════════════════════════════════════════════
Remember: Child-safe language. Frame any challenges as addressable with support.
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # PROSPECTS OF SUCCESS PROMPT (Question 2) - VEDIC ONLY
    # ==========================================================================
    def _build_success_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Prospects of Success questions - VEDIC ONLY (No KP)"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # For success questions, NO KP - VEDIC ONLY
        has_relevant_kp = False
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        
        # Language-specific labels
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_success = self._get_example_text(language, "success_outlook")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROSPECTS OF SUCCESS (Exams, Fields, Higher Studies, Scholarships)
Current Date: {today_str}
Weightage: Vedic 85% + Aspects 15% (VEDIC ONLY - No KP for this question)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
NOTE: Focus on:
- Ability to excel in examinations
- Best suited fields or subjects
- Higher education potential
- Research aptitude
- Scholarship possibilities
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
{lbl_success}.
Direct supportive assessment.
NO astrological terms. Write encouragingly for parents.

**{lbl_analysis}:**

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin strictly with:
"{starters['vedic']}"

- 5th house for intelligence and examination success
- 9th house for higher education and research
- 11th house for achievements and scholarships
- Mercury and Jupiter's strength for academic success

PARAGRAPH 2 - Best Fields/Subjects:
Based on planetary strengths, suggest suitable fields.

PARAGRAPH 3 - Higher Education & Research:
9th house analysis for higher studies potential.

PARAGRAPH 4 - Scholarship Possibilities:
11th house and beneficial aspects for gains.

**{lbl_summary}:**
{lbl_tell}: "[Clear guidance on academic potential and recommended fields]"

**{lbl_remedies}:**
Supportive study habits and environment suggestions.

═══════════════════════════════════════════════════════════════════════════════
NO KP ANALYSIS for this question - Use only Vedic.
Frame everything supportively. No limiting statements.
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # PROSPECTS OF COLLEGE PROMPT (Question 3) - KP + Vedic
    # ==========================================================================
    def _build_college_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for College Admission and Scholarship questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get data
        kp_points = self._get_relevant_kp_points(additional_data, "college")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)
        
        kp_data = self._format_kp_education_data(additional_data, "college") if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        
        # Language-specific labels
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_college = self._get_example_text(language, "college_outlook")
        starters = self._get_analysis_starters(language)

        # KP section
        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROSPECTS OF COLLEGE ADMISSION AND SCHOLARSHIPS
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_section}

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
{lbl_college}.
Direct assessment of college and scholarship prospects.
NO astrological terms. Write supportively for parents.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
This paragraph MUST begin with:
"{starters['vedic']}"

- 4th house for formal education and institutions
- 9th house for higher education
- 11th house for success and gains (scholarships)
- Benefic aspects on education houses

{"PARAGRAPH 2 – KP CONFIRMATION:" if has_relevant_kp else ""}

{f'This paragraph MUST begin with: "{starters["kp"]}" and ONLY restate KP findings. The entire paragraph must remain KP-only. Do NOT switch to Vedic reasoning.'
 if has_relevant_kp else ""}

PARAGRAPH {"3" if has_relevant_kp else "2"} - Scholarship Indicators:
6th house (loans/grants), 8th house (institutional support), 11th house (gains).

PARAGRAPH {"4" if has_relevant_kp else "3"} - Recommendations:
Preparation strategy and timing considerations.

**{lbl_summary}:**
{lbl_tell}: "[Clear guidance on college admission and scholarship prospects]"

**{lbl_remedies}:**
Supportive preparation and application guidance.

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # FOREIGN EDUCATION PROMPT (Question 4) - KP + Timing
    # ==========================================================================
    def _build_foreign_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Foreign Education questions with timing"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get data
        is_blocked = self._is_blocked(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        kp_points = self._get_relevant_kp_points(additional_data, "foreign")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)
        
        kp_data = self._format_kp_education_data(additional_data, "foreign") if has_relevant_kp else ""
        timing_data = self._format_timing_windows(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        timeline_data = self._format_dasha_timeline(kwargs)
        
        # Get language-specific text
        timing_unavailable = self._get_example_text(language, "timing_unavailable")
        blocked_message = self._get_example_text(language, "blocked_message")
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_foreign = self._get_example_text(language, "foreign_outlook")
        starters = self._get_analysis_starters(language)

        # LOGIC: Determine timing instruction based on state
        if is_blocked:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ FOREIGN EDUCATION CHALLENGING - NO SPECIFIC TIMING TO PROVIDE
═══════════════════════════════════════════════════════════════════════════════

The chart shows some challenges for immediate foreign education.

🚫 DO NOT provide specific timing windows or dates.
✅ DO mention current dasha period (if available) for general context.
✅ DO recommend patience and continued preparation.
✅ DO suggest alternative paths.

{dasha_data if dasha_data else "Current dasha information not available."}

MESSAGE TO CONVEY: "{blocked_message}"
═══════════════════════════════════════════════════════════════════════════════
"""
        elif has_timing:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE - USE THESE DATES
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{dasha_data if dasha_data else ""}

INSTRUCTIONS:
- Use ONLY the dates provided above
- BEST window = most favorable time for foreign education
- NEAREST window = soonest opportunity
- Mention BOTH windows in your answer
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING CALCULATED
═══════════════════════════════════════════════════════════════════════════════

No specific timing windows were calculated, but foreign education is NOT blocked.

🚫 DO NOT invent specific dates.
✅ DO explain that favorable periods should be monitored.
✅ DO recommend consulting for detailed timing analysis.

{dasha_data if dasha_data else ""}

MESSAGE: "{timing_unavailable}"
═══════════════════════════════════════════════════════════════════════════════
"""

        # KP section
        kp_section = ""
        if has_relevant_kp and not is_blocked:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}

NOTE: Simply restate these KP findings. Do NOT interpret further.
"""
        elif has_relevant_kp and is_blocked:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION DATA (CHALLENGING):
═══════════════════════════════════════════════════════════════════════════════

{kp_data}

NOTE: KP indicates challenges. Focus on Vedic remedies and preparation.
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PROSPECTS OF FOREIGN EDUCATION
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{timeline_data if timeline_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
{lbl_foreign}.
{"Mention BEST and NEAREST timing windows." if has_timing and not is_blocked else ""}
{"State that timing needs patience and continued preparation." if is_blocked else ""}
{"State that specific timing needs further analysis." if not has_timing and not is_blocked else ""}
NO astrological terms here. Write supportively for parents.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
This paragraph MUST begin with:
"{starters['vedic']}"

- 9th house (higher education, foreign lands)
- 12th house (foreign settlement, overseas)
- Rahu's role in foreign education
- 4th house (leaving homeland)

{"PARAGRAPH 2 – KP CONFIRMATION:" if has_relevant_kp else ""}

{f'This paragraph MUST begin with: "{starters["kp"]}" and ONLY restate KP findings. The entire paragraph must remain KP-only. Do NOT switch to Vedic reasoning.'
 if has_relevant_kp else ""}

PARAGRAPH {"3" if has_relevant_kp else "2"} - Supporting Factors:
Connect other houses to foreign education potential.

{"PARAGRAPH 4 – TIMING (ONLY): Connect dasha to timing windows. DO NOT mention obstacles or remedies." 
 if has_timing and not is_blocked else ""}

{"PARAGRAPH 4 – PREPARATION NEEDED: Explain what preparation is needed. DO NOT mention specific dates." 
 if is_blocked else ""}

**{lbl_summary}:**
{lbl_tell}: "[{'Specific timing advice with dates' if has_timing and not is_blocked else 'Recommend continued preparation and application efforts'}]"

**{lbl_remedies}:**
{"Provide relevant remedies for foreign education challenges." if is_blocked else "If delays exist, provide 1-2 supportive remedies."}

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
            language: str,
            **kwargs
        ) -> str:
        """Build prompt for Education Remedies"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # For remedies, KP can provide context
        kp_points = self._get_relevant_kp_points(additional_data, "general")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)
        
        kp_data = self._format_kp_education_data(additional_data, "general") if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION CONTEXT (For Remedy Focus):
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: EDUCATION REMEDIES
Current Date: {today_str}
Weightage: Vedic 85% + KP Context 15% (NO DASHA NEEDED)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE (Child-Safe, Supportive):
═══════════════════════════════════════════════════════════════════════════════

MERCURY WEAK: Study environment improvement, reading habits, green items on desk
JUPITER WEAK: Thursday prayers, seeking good mentors, yellow items
5th LORD WEAK: Creative activities, supportive study routines
4th LORD WEAK: Calm home environment, organized study space
MOON ISSUES: Emotional support, regular sleep routine
SATURN ASPECTS: Structured study schedules, patience and persistence
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
What educational challenges exist and that supportive measures can help.

**{lbl_analysis}:**

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin strictly with:
"{starters['vedic']}"

- Identify weak planets affecting education
- 5th and 4th house lord conditions
- Mercury and Jupiter's role and afflictions

{"PARAGRAPH 2 – KP CONTEXT:" if has_relevant_kp else ""}

{f'Begin strictly with: "{starters["kp"]}" and mention education indicators for remedy focus.'
 if has_relevant_kp else ""}

PARAGRAPH {"3" if has_relevant_kp else "2"} - Primary Remedy:
Most important supportive measure and WHY it will help.

PARAGRAPH {"4" if has_relevant_kp else "3"} - Supporting Remedies:
Additional helpful practices.

**{lbl_summary}:**
{lbl_tell}: "[Priority order of supportive measures]"

**{lbl_remedies} (Detailed):**
1. [Primary supportive remedy with specific instructions]
2. [Secondary remedy with instructions]
3. [Practical study habit recommendation]

═══════════════════════════════════════════════════════════════════════════════
IMPORTANT: All remedies must be child-safe, supportive, and non-invasive.
Focus on environment, routines, and encouragement.
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
        """Build general prompt for unclassified questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Detect if timing-related
        timing_keywords = ['when', 'time', 'timing', 'year', 'date', 'कब', 'समय', 'abroad', 'foreign', 'विदेश']
        is_timing = any(kw in question.lower() for kw in timing_keywords)
        
        is_blocked = self._is_blocked(additional_data)
        has_timing_data = self._has_valid_timing_windows(additional_data) and not is_blocked
        kp_points = self._get_relevant_kp_points(additional_data, "general")
        has_relevant_kp = bool(kp_points) and self._get_kp_availability(additional_data)
        starters = self._get_analysis_starters(language)

        kp_data = self._format_kp_education_data(additional_data, "general") if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        timing_data = self._format_timing_windows(additional_data) if is_timing and has_timing_data else ""
        dasha_data = self._format_current_dasha(additional_data) if is_timing else ""
        timeline_data = self._format_dasha_timeline(kwargs) if is_timing else ""
        
        weightage = "Vedic 55% + KP 30% + Dasha 10% + Aspects 5%" if is_timing else "Vedic 85% + KP Facts 15%"
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_education = self._get_example_text(language, "education_outlook")
        
        # Warning for blocked state
        blocked_warning = ""
        if is_blocked and is_timing:
            blocked_message = self._get_example_text(language, "blocked_message")
            blocked_warning = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ EDUCATION CHALLENGING - NO SPECIFIC TIMING
═══════════════════════════════════════════════════════════════════════════════
Do NOT provide specific timing. Recommend patience and continued preparation.
Message: "{blocked_message}"
═══════════════════════════════════════════════════════════════════════════════
"""

        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP EDUCATION DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: EDUCATION (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: {weightage}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{blocked_warning}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{dasha_data}

{timeline_data}

{kp_section}

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
{lbl_education}.
Directly answer the question.
NO astrological terms here.

**{lbl_analysis}:**
Flowing paragraphs with facts AND interpretations.

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin with:
"{starters['vedic']}"

Core Vedic interpretation answering the question.

{"PARAGRAPH 2 – KP CONFIRMATION:" if has_relevant_kp else ""}

{f'Begin with: "{starters["kp"]}" and restate KP findings only.'
 if has_relevant_kp else ""}

**{lbl_summary}:**
{lbl_tell}: "[Clear supportive guidance]"

**{lbl_remedies}:**
Relevant supportive remedies if needed.

═══════════════════════════════════════════════════════════════════════════════
Remember: Child-safe, supportive language throughout.
═══════════════════════════════════════════════════════════════════════════════
"""
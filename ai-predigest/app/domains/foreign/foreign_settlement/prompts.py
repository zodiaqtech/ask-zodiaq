"""
Foreign Settlement – LLM Prompts v8.0 (FIXED)

FIXES IN v8.0:
✅ Output language based on user selection (not hardcoded Hindi)
✅ If KP points have no relevant info → Only Vedic analysis
✅ If state NOT BLOCKED → Show timing windows
✅ If state BLOCKED → General dasha info + "try remedies" (no specific timing)
✅ Astrological analysis: VEDIC FIRST, then KP
✅ Language-specific examples in SELECTED language
✅ Compatible with ForeignSettlementEvaluator v7.0

Weightage:
- TIMING: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
- NON-TIMING: Vedic 85% + KP Facts 15% (No specific Dasha timing)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from ForeignSettlementEvaluator v7.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["foreign_settlement_kp_promise"] = {
    "has_promise": bool,
    "points": [...]  # Raw output from evaluate_foreign()
}

additional_data["foreign_settlement_timing_windows"] = {
    "has_timing": bool,
    "best_window": {...},
    "nearest_window": {...},
    "all_favorable": [...]
}

additional_data["foreign_settlement_house_lords"] = {...}
additional_data["foreign_settlement_house_aspects"] = {...}
additional_data["foreign_settlement_current_dasha"] = {...}
additional_data["foreign_settlement_dasha_timeline"] = {...}
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

DOMAIN_PREFIX = "foreign_settlement"


class ForeignSettlementPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Foreign → Foreign Settlement
    v8.0 - Fixed language handling and KP/timing logic
    """

    domain = "Foreign"
    subtopic = "Foreign Settlement"

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
                "9th_house": "नवम भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि विदेश यात्रा और भाग्य के लिए...",
                "12th_house": "द्वादश भाव के स्वामी [planet] [house] भाव में स्थित हैं। यह विदेश में बसने की संभावना को दर्शाता है...",
                "rahu": "राहु विदेश का कारक है। राहु [position] में होने से विदेशी संस्कृति की ओर आकर्षण...",
                "timing_unavailable": "विदेश जाने के लिए विशिष्ट समय की गणना वर्तमान में उपलब्ध नहीं है।",
                "blocked_message": "कुंडली में कुछ चुनौतियां हैं। उपायों के साथ प्रयास जारी रखें और कानूनी परामर्श लें।",
                "general_answer": "सामान्य उत्तर",
                "astrological_analysis": "ज्योतिषीय विश्लेषण",
                "summary": "सारांश",
                "remedies": "उपाय",
                "tell_client": "ग्राहक को बताएं",
                "vedic_start": "वैदिक ज्योतिष के अनुसार,",
                "kp_start": "KP प्रणाली के अनुसार,"
            },
            "English": {
                "9th_house": "The lord of 9th house [planet] is placed in [house] house in [sign]. This means for foreign travel and fortune...",
                "12th_house": "The lord of 12th house [planet] is placed in [house] house. This indicates the possibility of settling abroad...",
                "rahu": "Rahu is the karaka for foreign lands. Rahu being in [position] indicates attraction to foreign culture...",
                "timing_unavailable": "Specific timing for foreign travel could not be calculated at this time.",
                "blocked_message": "There are some challenges in the chart. Continue efforts with remedies and consult a legal professional.",
                "general_answer": "General Answer",
                "astrological_analysis": "Astrological Analysis",
                "summary": "Summary",
                "remedies": "Remedies",
                "tell_client": "TELL CLIENT",
                "vedic_start": "According to Vedic astrology,",
                "kp_start": "According to KP astrology,"
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
            weightage_text = "NON-TIMING QUESTION: Vedic 85% + KP Facts 15% (No specific Dasha timing)"
        
        return f"""You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in foreign travel, long stays, and permanent settlement.

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

4. NEVER NAME SPECIFIC COUNTRIES
   - Do NOT say "USA", "Canada", "Germany", etc.
   - You may describe climate, culture, or region type only
   - Example: "western countries", "cold climates", "English-speaking nations"

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "9th Lord Jupiter in 6th house. Retrograde. Benefic."
   ✅ "The 9th house lord Jupiter is placed in the 6th house, which indicates that foreign travel may come through service, health sector, or after overcoming obstacles..."

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for the question
   - Connect to the outcome

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

5. ANSWER THE ACTUAL QUESTION DIRECTLY

═══════════════════════════════════════════════════════════════════════════════
                    VEDIC FIRST, THEN KP
═══════════════════════════════════════════════════════════════════════════════

IMPORTANT: In Astrological Analysis section:
1. ALWAYS start with VEDIC analysis (PRIMARY)
2. THEN add KP analysis (SECONDARY) if relevant KP points exist
3. Never mix Vedic and KP reasoning in same paragraph

═══════════════════════════════════════════════════════════════════════════════
                    KP RULES (When KP data present)
═══════════════════════════════════════════════════════════════════════════════

KP section contains ONLY pre-computed evaluator output:
✅ 12th CSL name and significations
✅ 9th CSL significations
✅ Foreign promise state
✅ KP findings from evaluator

KP section must NOT contain:
❌ LLM-derived KP analysis
❌ Reinterpretation of KP points
❌ Using Vedic to explain KP conclusions

KP INTERPRETATION BOUNDARY (STRICT):
⚠️ KP points describe HOUSE CONNECTIONS and EVENT PROMISES only.

YOU MAY SAY:
✅ "12th CSL Saturn signifies 9th and 12th houses"
✅ "Star-lord reinforces foreign settlement"
✅ "Strong 9-12 linkage indicates long-term stay"

YOU MAY NOT SAY (unless explicitly provided in house_lords data):
❌ Planetary house placements ("Saturn in 2nd house")
❌ Zodiac signs ("in Pisces", "in Capricorn")
❌ Combustion or retrograde status
❌ Planetary aspects ("7th aspect", "9th aspect")

IF KP POINTS HAVE NO RELEVANT INFO FOR THE QUESTION:
→ Skip KP section entirely
→ Provide ONLY Vedic analysis

═══════════════════════════════════════════════════════════════════════════════
                    KEY FOREIGN SETTLEMENT HOUSES
═══════════════════════════════════════════════════════════════════════════════

- 9th: Long-distance travel, fortune, luck (PRIMARY)
- 12th: Foreign land, settlement, expenses (PRIMARY)
- 3rd: Short travel, efforts, paperwork
- 4th: Home, roots, leaving homeland
- 7th: Partnerships abroad, spouse
- 10th: Career abroad
- 11th: Gains, fulfillment abroad

═══════════════════════════════════════════════════════════════════════════════
                    LEGAL & ETHICAL DISCLAIMER
═══════════════════════════════════════════════════════════════════════════════

- Astrology does NOT guarantee visa, PR, or citizenship
- Astrology shows tendencies, not government decisions
- Legal pathways and eligibility must be verified separately
"""

    # ==========================================================================
    # HELPER: Check KP Availability
    # ==========================================================================
    def _get_kp_availability(self, additional_data: Dict) -> bool:
        """Check if KP promise data is available"""
        if not additional_data:
            return False
        kp_data = additional_data.get(f"{DOMAIN_PREFIX}_kp_promise", {})
        return bool(kp_data and kp_data.get("has_promise") and kp_data.get("points"))

    def _get_relevant_kp_points(self, additional_data: Dict, question_type: str) -> List[str]:
        """
        Return ONLY KP points relevant to the question.
        """
        if not additional_data:
            return []

        kp_data = additional_data.get(f"{DOMAIN_PREFIX}_kp_promise", {})
        points = kp_data.get("points", [])

        if not points:
            return []
        
        KP_KEYWORDS_BY_QUESTION = {
            "settlement": [
                "12th csl", "12th cusp", "sub-lord", "sub lord",
                "foreign promise", "settlement", "9-12", "9+12",
                "long-term", "permanent", "abroad",
                "signifies", "connects to", "promise confirmed",
            ],

            "timing": [
                "12th csl", "promise", "signifies",
                "favorable", "dasha lord", "ruling planet",
            ],

            "challenges": [
                "weak", "obstacle", "delay", "challenge",
                "6th", "8th", "malefic", "saturn", "rahu",
            ],

            "visa": [
                "3rd", "paperwork", "document", "mercury",
                "obstacle", "delay",
            ],

            "general": [
                "12th csl", "9th", "foreign", "promise",
                "settlement", "travel", "abroad",
            ]
        }

        keywords = KP_KEYWORDS_BY_QUESTION.get(
            question_type,
            KP_KEYWORDS_BY_QUESTION["general"]
        )

        relevant = []
        for p in points:
            pl = p.lower()
            if any(k in pl for k in keywords):
                relevant.append(p)

        return relevant

    def _is_foreign_blocked(self, additional_data: Dict) -> bool:
        """Check if foreign settlement is blocked based on KP analysis"""
        if not additional_data:
            return False
        
        kp_data = additional_data.get(f"{DOMAIN_PREFIX}_kp_promise", {})
        points = kp_data.get("points", [])
        
        # Check for blocking indicators
        blocking_keywords = [
            "weak foreign promise",
            "not link to 3, 9, or 12",
            "unlikely",
            "blocked",
            "denied"
        ]
        
        for p in points:
            pl = p.lower()
            if any(k in pl for k in blocking_keywords):
                return True
        
        return False

    # ==========================================================================
    # HELPER: Format KP Data
    # ==========================================================================
    def _format_kp_data(self, kp_points: List[str]) -> str:
        """Format KP promise analysis - DATA ONLY"""
        if not kp_points:
            return ""
        
        lines = ["KP DATA (Pre-computed by Evaluator):"]
        lines.append("")
        
        for point in kp_points:
            if isinstance(point, str) and point.strip():
                # Strip emojis for cleaner formatting
                clean_point = re.sub(r'[^\x00-\x7F]+', '', point).strip()
                if clean_point:
                    lines.append(f"  • {clean_point}")
        
        return "\n".join(lines)

    # ==========================================================================
    # HELPER: Format Timing Windows
    # ==========================================================================
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
                lines.append(f"🏆 BEST: {best.get('dasha', 'N/A')} | {best.get('start', 'N/A')} to {best.get('end', 'N/A')} | Score: {best.get('final_score', 0):.0f}/100")
                if best.get('age_at_start'):
                    lines.append(f"   Age at start: {best.get('age_at_start')} years")
            
            if nearest and nearest != best:
                lines.append(f"⏰ NEAREST: {nearest.get('dasha', 'N/A')} | {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')} | Score: {nearest.get('final_score', 0):.0f}/100")
            
            # Check if best and nearest are the same
            if best and nearest and best.get('dasha') == nearest.get('dasha'):
                lines.append("✅ LUCKY! Best and Nearest windows are THE SAME!")
            
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
        foreign_houses = {3, 4, 7, 9, 10, 11, 12}
        
        # House meanings for foreign context
        house_meanings = {
            3: "Efforts/Short Travel",
            4: "Home/Roots",
            7: "Partnerships Abroad",
            9: "Long Distance/Fortune",
            10: "Career Abroad",
            11: "Gains/Fulfillment",
            12: "Foreign Land/Settlement"
        }
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in foreign_houses:
                continue
            
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
        
        # House meanings for foreign context
        house_meanings = {
            3: "efforts/paperwork",
            4: "leaving homeland",
            7: "partnerships abroad",
            9: "long-distance/fortune",
            10: "career abroad",
            11: "gains/fulfillment",
            12: "foreign residence"
        }
        
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            
            if benefic or malefic:
                meaning = house_meanings.get(house_num, "foreign matters")
                benefic_str = ", ".join(benefic) if benefic else "None"
                malefic_str = ", ".join(malefic) if malefic else "None"
                lines.append(f"• H{house_num} ({meaning}): Benefic={benefic_str} | Malefic={malefic_str}")
        
        return "\n".join(lines) if len(lines) > 1 else ""

    # ==========================================================================
    # HELPER: Format Current Dasha
    # ==========================================================================
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
            
            # Map abbreviations to full names
            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus', 'Ra': 'Rahu', 'Ke': 'Ketu',
                'Saturn': 'Saturn', 'Sun': 'Sun', 'Moon': 'Moon',
                'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter',
                'Venus': 'Venus', 'Rahu': 'Rahu', 'Ketu': 'Ketu'
            }
            
            parts = dasha_name.split('-') if '-' in dasha_name else dasha_name.split('>') if '>' in dasha_name else [dasha_name]
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts]
            formatted_dasha = ' > '.join(full_names) if len(full_names) >= 2 else dasha_name
            
            return f"CURRENT DASHA: {formatted_dasha} ({start} to {end})"
        except Exception:
            return ""

    # ==========================================================================
    # HELPER: Format Dasha Timeline
    # ==========================================================================
    def _format_dasha_timeline(self, additional_data: Dict) -> str:
        """Format comprehensive dasha timeline"""
        if not additional_data:
            return ""
        
        dasha_timeline = additional_data.get(f'{DOMAIN_PREFIX}_dasha_timeline', {})
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
                'Saturn': 'Saturn', 'Sun': 'Sun', 'Moon': 'Moon',
                'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter',
                'Venus': 'Venus', 'Rahu': 'Rahu', 'Ketu': 'Ketu'
            }
            
            def parse_dasha(name):
                parts = name.split('>') if '>' in name else name.split('-') if '-' in name else [name]
                return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts])
            
            if current:
                lines.append("CURRENT:")
                for d in current[:2]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  🔴 {parsed} ({start} to {end})")
            
            if future:
                lines.append("UPCOMING (Next 10 Years):")
                for i, d in enumerate(future[:10], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {parsed} ({start} to {end})")
            
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
            language: str = "English",
            **kwargs
        ) -> str:
        """Main routing method - routes to appropriate specialized builder"""
        
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.pop("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""
            
            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            
            # Route based on sub_subdomain
            if "Settlement Timing" in sub_subdomain or "Foreign Settlement" in sub_subdomain:
                return self._build_settlement_timing_prompt(question, additional_data, raw, language)
            
            elif "Challenges" in sub_subdomain:
                return self._build_challenges_prompt(question, additional_data, raw, language)
            
            elif "Visa" in sub_subdomain or "Documentation" in sub_subdomain:
                return self._build_visa_prompt(question, additional_data, raw, language)
            
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language)
            
            else:
                return self._build_general_foreign_prompt(question, additional_data, raw, language, **kwargs)
        
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

You are an expert Vedic astrologer. Answer the following foreign settlement related question.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear actionable statement.
Always recommend legal consultation for visa/immigration matters.
Do NOT name specific countries.
"""

    # ==========================================================================
    # SETTLEMENT TIMING PROMPT
    # ==========================================================================
    def _build_settlement_timing_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Foreign Settlement Timing questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get data
        is_blocked = self._is_foreign_blocked(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        kp_points = self._get_relevant_kp_points(additional_data, "settlement")
        has_relevant_kp = bool(kp_points)
        kp_data = self._format_kp_data(kp_points)
        
        timing_data = self._format_timing_windows(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        timeline_data = self._format_dasha_timeline(additional_data)
        
        # Get language-specific text
        example_9th = self._get_example_text(language, "9th_house")
        example_12th = self._get_example_text(language, "12th_house")
        example_rahu = self._get_example_text(language, "rahu")
        timing_unavailable = self._get_example_text(language, "timing_unavailable")
        blocked_message = self._get_example_text(language, "blocked_message")
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)
        
        # LOGIC: Determine timing instruction based on state
        if is_blocked:
            # BLOCKED: Show general dasha info, no specific timing, suggest remedies
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ FOREIGN PROMISE WEAK - NO SPECIFIC TIMING TO PROVIDE
═══════════════════════════════════════════════════════════════════════════════

The chart shows weak indicators for foreign settlement.

🚫 DO NOT provide specific timing windows or dates.
✅ DO mention current dasha period (if available) for general context.
✅ DO recommend remedies and continued efforts.
✅ DO recommend legal/immigration consultation.

{dasha_data if dasha_data else "Current dasha information not available."}

MESSAGE TO CONVEY: "{blocked_message}"
═══════════════════════════════════════════════════════════════════════════════
"""
        elif has_timing:
            # NOT BLOCKED + HAS TIMING: Show timing windows
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE - USE THESE DATES
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{dasha_data if dasha_data else ""}

INSTRUCTIONS:
- Use ONLY the dates provided above
- BEST window = most favorable time for foreign settlement
- NEAREST window = soonest opportunity
- Mention BOTH windows in your answer
- Let user choose: Wait for best OR Act sooner
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            # NOT BLOCKED but NO TIMING: Explain and recommend monitoring
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING CALCULATED
═══════════════════════════════════════════════════════════════════════════════

No specific timing windows were calculated, but foreign settlement is indicated.

🚫 DO NOT invent specific dates.
✅ DO explain that favorable periods should be monitored.
✅ DO recommend consulting for detailed timing analysis.

{dasha_data if dasha_data else ""}

{timeline_data if timeline_data else ""}

MESSAGE: "{timing_unavailable}"
═══════════════════════════════════════════════════════════════════════════════
"""
        
        # KP section - only if relevant points exist
        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}

NOTE: Simply restate these KP findings. Do NOT interpret further.
Do NOT add sign/house placements not mentioned in KP data.
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN SETTLEMENT TIMING
Current Date: {today_str}
Weightage: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%
Foreign Promise: {'WEAK/BLOCKED' if is_blocked else 'INDICATED'}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
Has Timing Windows: {'YES' if has_timing and not is_blocked else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

VEDIC REFERENCE DATA:
    {lords_data}
    {aspects_data}
    {raw}

KP ANALYSIS DATA:
    {kp_section}


═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
{"Mention BEST and NEAREST timing windows with dates." if has_timing and not is_blocked else ""}
{"State that challenges exist and recommend remedies + legal consultation." if is_blocked else ""}
{"State that timing needs further analysis but foreign settlement is indicated." if not has_timing and not is_blocked else ""}

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC FIRST, THEN KP.

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY - 55% weight):
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 9th house lord (long-distance travel, fortune)
- Analyze 12th house lord (foreign land, settlement)
- Check dignity, placement, strength
- Connect to foreign settlement prospects
Example format: "{example_9th}"

PARAGRAPH 2 – Supporting Houses (3rd, 4th, 7th, 10th, 11th):
- 3rd house: Short travel, efforts, paperwork
- 4th house: Leaving homeland
- 7th house: Partnerships abroad, spouse
- 10th house: Career abroad
- 11th house: Gains and fulfillment
Connect to foreign settlement implications.

PARAGRAPH 3 – Rahu/Jupiter Analysis:
Rahu = Foreign karaka
Jupiter = Fortune and guidance
"{example_rahu}"

{"PARAGRAPH 4 – KP CONFIRMATION (30% weight):" if has_relevant_kp else ""}
{f'This paragraph MUST begin with: "{starters["kp"]}"' if has_relevant_kp else ""}
{f'ONLY restate KP findings from the data above. Do NOT interpret further.' if has_relevant_kp else ""}

{"PARAGRAPH – TIMING (10% weight):" if has_timing and not is_blocked else ""}
{"Connect dasha periods to timing windows. Explain WHY each window is favorable." if has_timing and not is_blocked else ""}

{"PARAGRAPH – CHALLENGES:" if is_blocked else ""}
{"Explain what needs to be addressed for foreign settlement." if is_blocked else ""}


PARAGRAPH {"6" if has_relevant_kp else "4"} – Aspects (5% weight):
Benefic/malefic aspects on 9th and 12th houses.

**{lbl_summary}:**
{lbl_tell}: "[{'Specific timing advice with BOTH windows' if has_timing and not is_blocked else 'Recommend remedies and legal consultation'}]"
ALWAYS include: "Astrology shows tendencies. Legal eligibility must be verified separately."

**{lbl_remedies}:**
{"Provide relevant remedies for weak houses." if is_blocked else "If any challenges exist, provide 1-2 remedies."}
ALWAYS recommend legal/immigration consultation.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REMINDERS:
- VEDIC analysis FIRST, then KP
- Do NOT name specific countries
- Do NOT invent dates not in timing windows
- Include legal disclaimer
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # CHALLENGES PROMPT
    # ==========================================================================
    def _build_challenges_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Challenges in Foreign Land questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_points = self._get_relevant_kp_points(additional_data, "challenges")
        has_relevant_kp = bool(kp_points)
        kp_data = self._format_kp_data(kp_points) if has_relevant_kp else ""
        
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        timeline_data = self._format_dasha_timeline(additional_data)
        
        # Language-specific labels
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
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: CHALLENGES IN FOREIGN LAND
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15% (NO specific Dasha timing)
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY RULES:
═══════════════════════════════════════════════════════════════════════════════
- Frame challenges constructively
- All indications are TENDENCIES not certainties
- Provide actionable solutions
- Do NOT induce fear or anxiety
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA (PRIMARY):
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{timeline_data if timeline_data else ""}

{kp_section}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Brief overview of potential challenges and reassurance.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC FIRST, THEN KP.

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin strictly with: "{starters['vedic']}"

- 6th house: Legal obstacles, visa issues
- 8th house: Sudden problems, setbacks, transformations
- 12th house: Expenses, isolation, adjustment issues
- Malefic aspects on 9th/12th houses
Explain WHERE challenges lie.

PARAGRAPH 2 – Areas of Challenge:
Based on house analysis, identify specific areas:
- Career adjustment challenges
- Financial challenges
- Relationship/social challenges
- Legal/documentation challenges

{"PARAGRAPH 3 – KP INDICATORS:" if has_relevant_kp else ""}
{f'Begin strictly with: "{starters["kp"]}"' if has_relevant_kp else ""}
{f'Restate KP challenge indicators only.' if has_relevant_kp else ""}

PARAGRAPH {"4" if has_relevant_kp else "3"} – Dasha Context:
Which dasha periods may intensify or reduce challenges.

**{lbl_summary}:**
{lbl_tell}: "[Constructive guidance + preparation advice]"

**{lbl_remedies}:**
Specific remedies for the challenges identified.
Include practical preparation advice.

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # VISA/DOCUMENTATION PROMPT
    # ==========================================================================
    def _build_visa_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Visa and Documentation Challenges"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_points = self._get_relevant_kp_points(additional_data, "visa")
        has_relevant_kp = bool(kp_points)
        kp_data = self._format_kp_data(kp_points) if has_relevant_kp else ""
        
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
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: VISA AND DOCUMENTATION CHALLENGES
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15%
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
KEY HOUSES FOR VISA/DOCUMENTATION:
═══════════════════════════════════════════════════════════════════════════════
- 3rd house: Documents, communication, short travel, paperwork
- 6th house: Obstacles, legal processes, delays
- 9th house: Long-distance travel, fortune, luck
- 11th house: Fulfillment of desires, gains
- Mercury: Documents, applications, communication
- Saturn: Delays, bureaucracy, persistence
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA (PRIMARY):
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{dasha_data if dasha_data else ""}

{raw if raw else ""}


═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS :
═══════════════════════════════════════════════════════════════════════════════
    {kp_section}




═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Clear indication about visa/documentation prospects.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC FIRST, THEN KP.

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin strictly with: "{starters['vedic']}"

- 3rd house lord: Document handling, paperwork ability
- 6th house lord: Potential obstacles in process
- Mercury's condition: Communication, applications
- Saturn's influence: Delays, persistence needed

PARAGRAPH 2 – Potential Obstacles:
Based on analysis, identify:
- Likely delays and their duration
- Areas requiring extra attention
- Documents that may need more care

{"PARAGRAPH 3 – KP INDICATORS:" if has_relevant_kp else ""}
{f'Begin strictly with: "{starters["kp"]}"' if has_relevant_kp else ""}
{f'Restate KP findings for visa matters.' if has_relevant_kp else ""}

PARAGRAPH {"4" if has_relevant_kp else "3"} – How to Overcome:
Astrological remedies and timing suggestions.

**{lbl_summary}:**
{lbl_tell}: "[Practical guidance + always recommend professional immigration help]"

**{lbl_remedies}:**
1. Mercury-related remedies for documents
2. Saturn-related remedies if delays indicated
3. ALWAYS: Consult qualified immigration lawyer

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: Astrology cannot predict government decisions. Include legal disclaimer.
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
        """Build prompt for Foreign Settlement Remedies"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_points = self._get_relevant_kp_points(additional_data, "general")
        has_relevant_kp = bool(kp_points)
        kp_data = self._format_kp_data(kp_points) if has_relevant_kp else ""
        
        lords_data = self._format_house_lords(additional_data)
        
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
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN SETTLEMENT REMEDIES
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15%
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

VEDIC REFERENCE DATA:
    {lords_data}
    {raw}

KP ANALYSIS DATA:
    {kp_section}


═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE FOR FOREIGN SETTLEMENT:
═══════════════════════════════════════════════════════════════════════════════

9th LORD WEAK: Strengthen with gemstone/mantra of 9th lord, Thursday fasts
12th LORD WEAK: Remedies for 12th lord, meditation, spiritual practices
RAHU AFFLICTION: Donate to underprivileged, Durga worship, avoid lies
SATURN DELAYS: Saturday charity, serve elderly, patience
JUPITER WEAK: Yellow items, Thursday fasts, Vishnu worship
MERCURY WEAK (Visa issues): Green items, Wednesday fasts, Ganesh worship
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
What issues exist and that remedies can help.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC FIRST, THEN KP.

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin strictly with: "{starters['vedic']}"

Identify weak areas in the chart:
- Weak 9th house lord: Travel/fortune challenges
- Weak 12th house lord: Settlement difficulties
- Malefic influences on foreign houses

PARAGRAPH 2 – Primary Remedy:
Most important remedy and WHY it will help.

{"PARAGRAPH 3 – KP INDICATORS:" if has_relevant_kp else ""}
{f'Begin strictly with: "{starters["kp"]}"' if has_relevant_kp else ""}
{f'KP-based remedy suggestions if any.' if has_relevant_kp else ""}

PARAGRAPH {"4" if has_relevant_kp else "3"} – Supporting Remedies:
Additional helpful practices.

**{lbl_summary}:**
{lbl_tell}: "[Priority order of remedies + practical steps]"

**{lbl_remedies} (Detailed):**
1. [Primary astrological remedy with instructions]
2. [Secondary astrological remedy]
3. [Practical preparation - skills, documents, finances]
4. [Legal/immigration consultation recommendation]

═══════════════════════════════════════════════════════════════════════════════
REMEDY LIMITS:
- MAX 2 astrological remedies
- MAX 1 gemstone (ONLY if weakness is explicit)
- ALWAYS add "consult a qualified astrologer" for gemstones
═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # GENERAL FOREIGN PROMPT (Fallback)
    # ==========================================================================
    def _build_general_foreign_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str,
            **kwargs
        ) -> str:
        """Build general prompt for unclassified foreign questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Detect if timing-related
        timing_keywords = ['when', 'time', 'timing', 'year', 'date', 'कब', 'समय', 'delay', 'विलंब', 'settle', 'बसना']
        is_timing = any(kw in question.lower() for kw in timing_keywords)
        
        is_blocked = self._is_foreign_blocked(additional_data)
        has_timing_data = self._has_valid_timing_windows(additional_data) and not is_blocked
        kp_points = self._get_relevant_kp_points(additional_data, "general")
        has_relevant_kp = bool(kp_points)
        
        kp_data = self._format_kp_data(kp_points) if has_relevant_kp else ""
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        timing_data = self._format_timing_windows(additional_data) if is_timing and has_timing_data else ""
        dasha_data = self._format_current_dasha(additional_data) if is_timing else ""
        timeline_data = self._format_dasha_timeline(additional_data) if is_timing else ""
        
        weightage = "Vedic 55% + KP 30% + Dasha 10% + Aspects 5%" if is_timing else "Vedic 85% + KP Facts 15%"
        
        lbl_general = self._get_example_text(language, "general_answer")
        lbl_analysis = self._get_example_text(language, "astrological_analysis")
        lbl_summary = self._get_example_text(language, "summary")
        lbl_remedies = self._get_example_text(language, "remedies")
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)
        
        # Warning for blocked state
        blocked_warning = ""
        if is_blocked and is_timing:
            blocked_message = self._get_example_text(language, "blocked_message")
            blocked_warning = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ FOREIGN PROMISE WEAK - NO SPECIFIC TIMING
═══════════════════════════════════════════════════════════════════════════════
Do NOT provide specific timing. Recommend remedies and legal consultation.
Message: "{blocked_message}"
═══════════════════════════════════════════════════════════════════════════════
"""
        
        kp_section = ""
        if has_relevant_kp:
            kp_section = f"""
═══════════════════════════════════════════════════════════════════════════════
KP ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{kp_data}
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FOREIGN SETTLEMENT (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: {weightage}
Foreign Promise: {'WEAK/BLOCKED' if is_blocked else 'INDICATED'}
Has Relevant KP: {'YES' if has_relevant_kp else 'NO - Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{blocked_warning}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{timing_data if timing_data else ""}

{dasha_data if dasha_data else ""}

{timeline_data if timeline_data else ""}

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{raw if raw else ""}


═══════════════════════════════════════════════════════════════════════════════
REFERENCE KP DATA:
═══════════════════════════════════════════════════════════════════════════════
{kp_section}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**{lbl_general} (2-3 lines):**
Directly answer the question.

**{lbl_analysis}:**
Write in FLOWING PARAGRAPHS. VEDIC FIRST, THEN KP.

PARAGRAPH 1 – VEDIC ANALYSIS (PRIMARY):
Begin strictly with: "{starters['vedic']}"

Core Vedic interpretation answering the question.
- 9th house (long-distance travel, fortune)
- 12th house (foreign land, settlement)
- Supporting houses as relevant

{"PARAGRAPH 2 – KP CONFIRMATION:" if has_relevant_kp else ""}
{f'Begin strictly with: "{starters["kp"]}"' if has_relevant_kp else ""}
{f'Restate KP findings only.' if has_relevant_kp else ""}

PARAGRAPH {"3" if has_relevant_kp else "2"} – Additional Analysis:
Other relevant factors from the chart.

**{lbl_summary}:**
{lbl_tell}: "[Clear actionable advice + legal consultation if relevant]"

**{lbl_remedies}:**
Relevant remedies if needed.
Include practical advice and legal disclaimer.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REMINDERS:
- VEDIC analysis FIRST, then KP
- Do NOT name specific countries
- Include legal disclaimer for visa/immigration matters
═══════════════════════════════════════════════════════════════════════════════
"""
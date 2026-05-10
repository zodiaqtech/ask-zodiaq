"""
Travel – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for travel, pilgrimage, and journey-related queries
using traditional Vedic astrology principles.

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Output language based on user selection
✅ Pilgrimage-specific analysis with spiritual focus
✅ General travel success assessment
✅ Travel risks and precautions
✅ Timing windows for Q1 and Q2 (TIMING questions)
✅ Auspicious muhurat guidance

Weightage:
- TIMING QUESTIONS (Q1, Q2): Vedic 90% + Dasha 10%
- NON-TIMING QUESTIONS (Q3): Vedic 100%

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from TravelEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["travel_pilgrimage_analysis"] = {
    "favorability": "HIGHLY_FAVORABLE" | "FAVORABLE" | "MODERATE" | "CHALLENGING",
    "score": int (0-100),
    "favorable_factors": [...],
    "unfavorable_factors": [...],
    "recommended_places": [...],
    "best_days": [...]
}

additional_data["travel_travel_analysis"] = {
    "success_likelihood": "HIGH" | "MODERATE_HIGH" | "MODERATE" | "LOW",
    "score": int (0-100),
    "short_travel": {"favorable": bool, "notes": [...]},
    "long_travel": {"favorable": bool, "notes": [...]},
    "foreign_travel": {"favorable": bool, "notes": [...]}
}

additional_data["travel_risks_analysis"] = {
    "risk_level": "HIGH" | "MODERATE" | "LOW" | "VERY_LOW",
    "risk_score": int (0-100),
    "risks": [...],
    "precautions": [...],
    "protective_factors": [...]
}

additional_data["travel_timing_windows"] = {
    "has_timing": bool,
    "best_window": {...},
    "nearest_window": {...}
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

DOMAIN_PREFIX = "travel"


class TravelPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Travel → Travel
    v1.0 - Vedic-only analysis
    """

    domain = "Travel"
    subtopic = "Travel"

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
                "9th_house": "नवम भाव के स्वामी [planet] [house] भाव में [sign] में हैं। इसका अर्थ है कि तीर्थयात्रा के लिए...",
                "3rd_house": "तृतीय भाव के स्वामी [planet] [position] में होने से छोटी यात्राओं में...",
                "7th_house": "सप्तम भाव के स्वामी [planet] [position] में होने से लंबी यात्राओं में...",
                "jupiter": "गुरु तीर्थयात्रा का कारक है। गुरु [position] में होने से...",
                "timing_available": "यात्रा के लिए शुभ समय उपलब्ध है।",
                "timing_unavailable": "विशिष्ट समय की गणना उपलब्ध नहीं है, लेकिन सामान्य मुहूर्त मार्गदर्शन दिया गया है।",
                "pilgrimage_favorable": "तीर्थयात्रा के लिए कुंडली अनुकूल है।",
                "pilgrimage_challenging": "तीर्थयात्रा में कुछ बाधाएं हो सकती हैं, उपायों से लाभ होगा।",
                "travel_successful": "यात्रा सफल होने की संभावना है।",
                "travel_risky": "यात्रा में सावधानी बरतें।",
                "general_answer": "GENERAL_ANSWER",
                "astrological_analysis": "ASTROLOGICAL_ANALYSIS",
                "summary": "SUMMARY",
                "remedies": "REMEDIES",
                "tell_client": "TELL CLIENT",
                "pilgrimage_outlook": "तीर्थयात्रा संभावना",
                "travel_outlook": "यात्रा संभावना",
                "risks_outlook": "जोखिम विश्लेषण",
                "timing_outlook": "शुभ समय"
            },
            "English": {
                "9th_house": "The lord of 9th house [planet] is placed in [house] house in [sign]. This indicates for pilgrimage...",
                "3rd_house": "The lord of 3rd house [planet] being in [position] indicates for short journeys...",
                "7th_house": "The lord of 7th house [planet] being in [position] indicates for long journeys...",
                "jupiter": "Jupiter is the karaka for pilgrimage. Jupiter being in [position] indicates...",
                "timing_available": "Auspicious timing for travel is available.",
                "timing_unavailable": "Specific timing could not be calculated, but general muhurat guidance is provided.",
                "pilgrimage_favorable": "The chart is favorable for pilgrimage.",
                "pilgrimage_challenging": "There may be some obstacles in pilgrimage, remedies will help.",
                "travel_successful": "Travel is likely to be successful.",
                "travel_risky": "Exercise caution during travel.",
                "general_answer": "GENERAL_ANSWER",
                "astrological_analysis": "ASTROLOGICAL_ANALYSIS",
                "summary": "SUMMARY",
                "remedies": "REMEDIES",
                "tell_client": "TELL CLIENT",
                "pilgrimage_outlook": "Pilgrimage Prospects",
                "travel_outlook": "Travel Prospects",
                "risks_outlook": "Risk Analysis",
                "timing_outlook": "Auspicious Timing"
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
    def build_system_prompt(self, language: str = "English", is_timing: bool = False) -> str:
        """Build system prompt for travel analysis"""
        
        if is_timing:
            weightage_text = "TIMING QUESTION: Vedic 90% + Dasha 10%"
        else:
            weightage_text = "NON-TIMING QUESTION: Vedic 100%"
        
        example_9th = self._get_example_text(language, "9th_house")
        
        return f"""You are an expert Vedic astrologer specializing in travel, pilgrimage (Tirtha Yatra), and journey-related analysis.

**{weightage_text}**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. NEVER INVENT DATES OR TIMING
   - If no timing windows are provided, do NOT make up dates
   - Do NOT guess years like "2027", "March 2026"
   - Only mention specific dates if they appear in TIMING WINDOWS section
   - You CAN mention auspicious days (Thursday, Monday) and nakshatras

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
   ❌ "9th Lord Jupiter in 5th house. Strong. Benefic."
   ✅ "{example_9th}"

2. EVERY FACT NEEDS INTERPRETATION
   - State the fact
   - Explain what it means for travel/pilgrimage
   - Connect to practical guidance

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. "TELL CLIENT:" ONLY IN FINAL SUMMARY

5. PROVIDE PRACTICAL TRAVEL GUIDANCE

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR TRAVEL ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

- 3rd House: Short journeys, local travel, courage to travel
- 4th House: Home (leaving home), vehicles, comfort during travel
- 7th House: Long journeys, foreign travel, destinations
- 9th House: Pilgrimage, long-distance travel, dharma, fortune abroad
- 12th House: Foreign lands, expenses during travel, spiritual journeys

Key Karakas:
- Jupiter: Pilgrimage, blessings, divine protection
- Moon: Mental peace, comfort, emotional state during travel
- Mercury: Planning, documentation, communication
- Venus: Comfort, luxury, enjoyable travel
- Saturn: Long journeys, delays, obstacles
- Rahu: Foreign travel, unusual destinations

═══════════════════════════════════════════════════════════════════════════════
                    AUSPICIOUS DAYS FOR TRAVEL (VEDIC)
═══════════════════════════════════════════════════════════════════════════════

Thursday (Guru's day): Best for pilgrimage and spiritual journeys
Monday (Chandra's day): Good for short trips, water-related places
Wednesday (Budha's day): Good for business travel, education trips
Friday (Shukra's day): Ideal for leisure, pleasure trips, honeymoon
Saturday (Shani's day): Long journeys, foreign travel (with caution)

Best Nakshatras for Travel:
- Ashwini, Pushya, Mrigashira: Excellent for starting journeys
- Revati, Hasta, Swati: Smooth and safe travels
- Avoid: Bharani, Krittika, Magha, Moola (generally)

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════

- Never discourage pilgrimage - always provide positive framing
- For challenges, focus on remedies and precautions
- Recommend Rahu Kaal avoidance for travel starts
- Suggest carrying protective items (recommended in remedies)
- For risks, frame as "areas of attention" not "dangers"
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_pilgrimage_favorability(self, additional_data: Dict) -> str:
        """Get pilgrimage favorability from evaluator"""
        if not additional_data:
            return "MODERATE"
        pilgrimage = additional_data.get(f"{DOMAIN_PREFIX}_pilgrimage_analysis", {})
        return pilgrimage.get("favorability", "MODERATE")

    def _get_pilgrimage_score(self, additional_data: Dict) -> int:
        """Get pilgrimage score from evaluator"""
        if not additional_data:
            return 50
        pilgrimage = additional_data.get(f"{DOMAIN_PREFIX}_pilgrimage_analysis", {})
        return pilgrimage.get("score", 50)

    def _get_travel_success(self, additional_data: Dict) -> str:
        """Get travel success likelihood from evaluator"""
        if not additional_data:
            return "MODERATE"
        travel = additional_data.get(f"{DOMAIN_PREFIX}_travel_analysis", {})
        return travel.get("success_likelihood", "MODERATE")

    def _get_travel_score(self, additional_data: Dict) -> int:
        """Get travel score from evaluator"""
        if not additional_data:
            return 50
        travel = additional_data.get(f"{DOMAIN_PREFIX}_travel_analysis", {})
        return travel.get("score", 50)

    def _get_risk_level(self, additional_data: Dict) -> str:
        """Get risk level from evaluator"""
        if not additional_data:
            return "LOW"
        risks = additional_data.get(f"{DOMAIN_PREFIX}_risks_analysis", {})
        return risks.get("risk_level", "LOW")

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        """Check if valid timing windows exist"""
        if not additional_data:
            return False
        timing = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        return timing.get("has_timing", False)

    def _format_pilgrimage_analysis(self, additional_data: Dict) -> str:
        """Format pilgrimage analysis for prompt"""
        if not additional_data:
            return ""
        
        pilgrimage = additional_data.get(f"{DOMAIN_PREFIX}_pilgrimage_analysis", {})
        if not pilgrimage:
            return ""
        
        lines = ["PILGRIMAGE ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Favorability: {pilgrimage.get('favorability', 'MODERATE')}")
        lines.append(f"• Score: {pilgrimage.get('score', 50)}/100")
        
        favorable = pilgrimage.get("favorable_factors", [])
        if favorable:
            lines.append("")
            lines.append("Favorable Factors:")
            for f in favorable[:4]:
                lines.append(f"  ✅ {f}")
        
        unfavorable = pilgrimage.get("unfavorable_factors", [])
        if unfavorable:
            lines.append("")
            lines.append("Challenging Factors:")
            for f in unfavorable[:3]:
                lines.append(f"  ⚠️ {f}")
        
        recommended = pilgrimage.get("recommended_places", [])
        if recommended:
            lines.append("")
            lines.append("Recommended:")
            for r in recommended[:3]:
                lines.append(f"  🙏 {r}")
        
        best_days = pilgrimage.get("best_days", [])
        if best_days:
            lines.append("")
            lines.append("Best Days:")
            for d in best_days[:3]:
                lines.append(f"  📅 {d}")
        
        return "\n".join(lines)

    def _format_travel_analysis(self, additional_data: Dict) -> str:
        """Format travel analysis for prompt"""
        if not additional_data:
            return ""
        
        travel = additional_data.get(f"{DOMAIN_PREFIX}_travel_analysis", {})
        if not travel:
            return ""
        
        lines = ["TRAVEL ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Success Likelihood: {travel.get('success_likelihood', 'MODERATE')}")
        lines.append(f"• Score: {travel.get('score', 50)}/100")
        
        short = travel.get("short_travel", {})
        if short:
            status = "✅ Favorable" if short.get("favorable") else "⚠️ Needs attention"
            lines.append(f"• Short Travel: {status}")
            for note in short.get("notes", [])[:2]:
                lines.append(f"    - {note}")
        
        long_t = travel.get("long_travel", {})
        if long_t:
            status = "✅ Favorable" if long_t.get("favorable") else "⚠️ Needs attention"
            lines.append(f"• Long Travel: {status}")
            for note in long_t.get("notes", [])[:2]:
                lines.append(f"    - {note}")
        
        foreign = travel.get("foreign_travel", {})
        if foreign:
            status = "✅ Favorable" if foreign.get("favorable") else "⚠️ Needs attention"
            lines.append(f"• Foreign Travel: {status}")
            for note in foreign.get("notes", [])[:2]:
                lines.append(f"    - {note}")
        
        favorable = travel.get("favorable_factors", [])
        if favorable:
            lines.append("")
            lines.append("Favorable Factors:")
            for f in favorable[:3]:
                lines.append(f"  ✅ {f}")
        
        return "\n".join(lines)

    def _format_risks_analysis(self, additional_data: Dict) -> str:
        """Format risks analysis for prompt"""
        if not additional_data:
            return ""
        
        risks = additional_data.get(f"{DOMAIN_PREFIX}_risks_analysis", {})
        if not risks:
            return ""
        
        lines = ["RISKS ANALYSIS (Pre-computed by Evaluator):"]
        lines.append(f"• Risk Level: {risks.get('risk_level', 'LOW')}")
        lines.append(f"• Risk Score: {risks.get('risk_score', 20)}/100")
        
        risk_list = risks.get("risks", [])
        if risk_list:
            lines.append("")
            lines.append("Potential Risks:")
            for r in risk_list[:4]:
                lines.append(f"  ⚠️ {r}")
        
        precautions = risks.get("precautions", [])
        if precautions:
            lines.append("")
            lines.append("Precautions:")
            for p in precautions[:4]:
                lines.append(f"  🛡️ {p}")
        
        protective = risks.get("protective_factors", [])
        if protective:
            lines.append("")
            lines.append("Protective Factors:")
            for p in protective[:3]:
                lines.append(f"  ✅ {p}")
        
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

    def _format_timing_hints(self, additional_data: Dict) -> str:
        """Format timing hints for prompt"""
        if not additional_data:
            return ""
        
        hints = additional_data.get(f"{DOMAIN_PREFIX}_timing_hints", {})
        if not hints:
            return ""
        
        lines = ["AUSPICIOUS TIMING HINTS:"]
        
        best_days = hints.get("best_days", [])
        if best_days:
            lines.append("")
            lines.append("Best Days:")
            for d in best_days[:3]:
                lines.append(f"  📅 {d}")
        
        avoid_days = hints.get("avoid_days", [])
        if avoid_days:
            lines.append("")
            lines.append("Days/Times to Avoid:")
            for d in avoid_days[:3]:
                lines.append(f"  ❌ {d}")
        
        nakshatras = hints.get("best_nakshatras", [])
        if nakshatras:
            lines.append("")
            lines.append("Best Nakshatras:")
            for n in nakshatras[:3]:
                lines.append(f"  ⭐ {n}")
        
        general = hints.get("general_hints", [])
        if general:
            lines.append("")
            lines.append("General Hints:")
            for g in general[:3]:
                lines.append(f"  💡 {g}")
        
        return "\n".join(lines) if len(lines) > 1 else ""

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        travel_houses = {1, 3, 4, 7, 9, 12}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in travel_houses:
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
            
            lines.append(f"• H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | {dignity} | {condition_str} | Str:{strength}/100")
        
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
            
            if "Pilgrimage" in sub_subdomain:
                return self._build_pilgrimage_prompt(question, additional_data, raw, language)
            
            elif "Travel Timing" in sub_subdomain or "favorable time" in question.lower():
                return self._build_travel_timing_prompt(question, additional_data, raw, language)
            
            elif "Risk" in sub_subdomain or "obstacle" in question.lower():
                return self._build_risks_prompt(question, additional_data, raw, language)
            
            else:
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

You are an expert Vedic astrologer specializing in travel and pilgrimage analysis.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
Include practical travel guidance.
End with a clear actionable statement.
Mention auspicious days for travel (Thursday for pilgrimage, etc.).
"""

    # ==========================================================================
    # PILGRIMAGE TIMING PROMPT (Q1 - TIMING)
    # ==========================================================================
    def _build_pilgrimage_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Pilgrimage Timing questions (TIMING)"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        favorability = self._get_pilgrimage_favorability(additional_data)
        p_score = self._get_pilgrimage_score(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        
        pilgrimage_data = self._format_pilgrimage_analysis(additional_data)
        timing_data = self._format_timing_windows(additional_data)
        timing_hints = self._format_timing_hints(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        example_9th = self._get_example_text(language, "9th_house")
        example_jupiter = self._get_example_text(language, "jupiter")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_pilgrimage = self._get_example_text(language, "pilgrimage_outlook")
        starters = self._get_analysis_starters(language)

        if has_timing:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE - USE THESE DATES
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{timing_hints}

INSTRUCTIONS:
- Use ONLY the dates provided above for specific timing
- BEST window = most auspicious time for pilgrimage
- NEAREST window = soonest opportunity
- Mention BOTH windows in your answer
- Also include auspicious days (Thursday) and nakshatras
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING WINDOWS CALCULATED
═══════════════════════════════════════════════════════════════════════════════

{timing_hints}

🚫 DO NOT invent specific dates like "March 2026" or "next 6 months".
✅ DO mention auspicious days (Thursday best for pilgrimage).
✅ DO mention favorable nakshatras (Pushya, Ashwini, etc.).
✅ DO provide general muhurat guidance.
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PILGRIMAGE TIMING (TIRTHA YATRA)
Current Date: {today_str}
Weightage: Vedic 90% + Dasha 10%
Pilgrimage Favorability: {favorability} ({p_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

═══════════════════════════════════════════════════════════════════════════════
PILGRIMAGE ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{pilgrimage_data}

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
{lbl_pilgrimage}: {favorability}
Brief assessment of pilgrimage prospects.
{"Mention BEST and NEAREST timing windows." if has_timing else "Mention auspicious days and nakshatras."}
NO astrological terms here. Write as a caring spiritual guide.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 9th house (pilgrimage, dharma)
- Jupiter's position (karaka for pilgrimage)
- 12th house (spiritual journeys)

PARAGRAPH 2 – Spiritual Blessings:
"{example_jupiter}"
Explain divine support and blessings for pilgrimage.

PARAGRAPH 3 – Recommended Direction/Places:
Based on 9th lord's sign, recommend direction.

PARAGRAPH 4 – Auspicious Timing:
{"Mention BEST and NEAREST windows with specific dates." if has_timing else "Mention auspicious days (Thursday) and nakshatras."}
{"DO NOT invent specific dates." if not has_timing else ""}

SUMMARY:
{lbl_tell}: "[Pilgrimage favorability + {'Specific timing' if has_timing else 'Best days'} + Direction]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Mantra for safe pilgrimage
- Remedies for any weak planets affecting 9th house

REMEDIES_GENERAL:
- Plan journey on Thursday if possible
- Avoid Rahu Kaal for departure
- Carry protective items

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # TRAVEL TIMING PROMPT (Q2 - TIMING)
    # ==========================================================================
    def _build_travel_timing_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Travel Timing questions (TIMING)"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        travel_success = self._get_travel_success(additional_data)
        t_score = self._get_travel_score(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        
        travel_data = self._format_travel_analysis(additional_data)
        timing_data = self._format_timing_windows(additional_data)
        timing_hints = self._format_timing_hints(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        example_3rd = self._get_example_text(language, "3rd_house")
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_travel = self._get_example_text(language, "travel_outlook")
        starters = self._get_analysis_starters(language)

        if has_timing:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
✅ TIMING WINDOWS AVAILABLE - USE THESE DATES
═══════════════════════════════════════════════════════════════════════════════

{timing_data}

{timing_hints}

INSTRUCTIONS:
- Use ONLY the dates provided above
- BEST window = most favorable time for travel
- NEAREST window = soonest opportunity
- Mention BOTH windows
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            timing_instruction = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO SPECIFIC TIMING WINDOWS CALCULATED
═══════════════════════════════════════════════════════════════════════════════

{timing_hints}

🚫 DO NOT invent specific dates.
✅ DO mention favorable days based on travel purpose.
✅ DO mention favorable nakshatras.
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: TRAVEL TIMING (General Travel)
Current Date: {today_str}
Weightage: Vedic 90% + Dasha 10%
Travel Success: {travel_success} ({t_score}/100)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

═══════════════════════════════════════════════════════════════════════════════
TRAVEL ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{travel_data}

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
{lbl_travel}: {travel_success}
Brief assessment of travel success.
{"Mention BEST and NEAREST timing windows." if has_timing else "Mention favorable days."}
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze 3rd house (short journeys)
- 7th house (long journeys)
- 9th house (long distance, fortune)

PARAGRAPH 2 – Travel Type Analysis:
"{example_3rd}"
- Short travel prospects
- Long travel prospects
- Foreign travel (if indicated)

PARAGRAPH 3 – Auspicious Timing:
{"Mention BEST and NEAREST windows with specific dates." if has_timing else "Mention favorable days."}
- Wednesday for business travel
- Friday for leisure/pleasure trips
{"DO NOT invent specific dates." if not has_timing else ""}

SUMMARY:
{lbl_tell}: "[Travel success + {'Specific timing' if has_timing else 'Best days'} + Tips]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Remedies for any weak planets affecting travel houses

REMEDIES_GENERAL:
- Best day to start based on purpose
- Avoid Rahu Kaal for departure

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # TRAVEL RISKS PROMPT (Q3 - NON-TIMING)
    # ==========================================================================
    def _build_risks_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Travel Risks questions (NON-TIMING)"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        risk_level = self._get_risk_level(additional_data)
        risks_data = self._format_risks_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_risks = self._get_example_text(language, "risks_outlook")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: TRAVEL RISKS AND OBSTACLES
Current Date: {today_str}
Weightage: Vedic 100% (NO TIMING NEEDED)
Risk Level: {risk_level}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY NOTE:
═══════════════════════════════════════════════════════════════════════════════
- Frame risks as "areas of attention" not "dangers"
- Always provide solutions and precautions
- Focus on how to OVERCOME obstacles
- End on a positive, constructive note
- Never discourage travel completely
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
RISKS ANALYSIS DATA:
═══════════════════════════════════════════════════════════════════════════════

{risks_data}

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
{lbl_risks}: {risk_level}
Brief assessment of travel risks.
Reassuring tone - focus on overcoming obstacles.
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – VEDIC ANALYSIS:
This paragraph MUST begin with:
"{starters['vedic']}"

- Analyze malefic influences on travel houses (3rd, 7th, 9th)
- Mars, Saturn, Rahu influences

PARAGRAPH 2 – Areas of Attention:
Frame as "tendencies to be aware of" not "definite problems".

PARAGRAPH 3 – Protective Factors:
Highlight positive influences that provide protection.

PARAGRAPH 4 – How to Overcome:
Practical steps to mitigate each risk.

PARAGRAPH 5 – Positive Conclusion:
End with encouragement and confidence.

SUMMARY:
{lbl_tell}: "[Risk level + Key precautions + Protective measures + Encouragement]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Hanuman Chalisa for protection during travel
- Remedies for specific malefic planets

REMEDIES_GENERAL:
- Travel insurance recommendation
- Avoid Rahu Kaal for departure
- Carry protective items (Hanuman coin, etc.)

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
            language: str
        ) -> str:
        """Build general prompt for unclassified travel questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        timing_keywords = ['when', 'time', 'timing', 'muhurat', 'कब', 'समय', 'शुभ']
        is_timing = any(kw in question.lower() for kw in timing_keywords)
        
        travel_success = self._get_travel_success(additional_data)
        risk_level = self._get_risk_level(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        
        travel_data = self._format_travel_analysis(additional_data)
        timing_data = self._format_timing_windows(additional_data) if is_timing and has_timing else ""
        timing_hints = self._format_timing_hints(additional_data)
        lords_data = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)
        
        weightage = "Vedic 90% + Dasha 10%" if is_timing else "Vedic 100%"
        
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_travel = self._get_example_text(language, "travel_outlook")
        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: TRAVEL (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: {weightage}
Travel Success: {travel_success}
Risk Level: {risk_level}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{timing_data if timing_data else ""}

{timing_hints}

{travel_data}

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (USE EXACT HEADERS SHOWN):
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_travel}: {travel_success}
Directly answer the question.
NO astrological terms here.
(2-3 lines only)

ASTROLOGICAL_ANALYSIS:
Flowing paragraphs with facts AND interpretations.

PARAGRAPH 1 – VEDIC ANALYSIS:
Begin with:
"{starters['vedic']}"

Core Vedic interpretation answering the question.

SUMMARY:
{lbl_tell}: "[Clear actionable advice]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
Relevant remedies if needed.

REMEDIES_GENERAL:
Practical travel tips.

═══════════════════════════════════════════════════════════════════════════════
"""

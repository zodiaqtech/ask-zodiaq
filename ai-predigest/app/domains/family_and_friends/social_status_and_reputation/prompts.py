"""
Social Status and Reputation – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for analyzing social status, reputation, recognition,
and potential risks using Vedic astrology principles.

Covers three sub-subdomains:
1. Recognition and Honour - Fame, awards, public image
2. Risk to Reputation - Scandals, blackmail, defamation
3. Social Relationships - Social standing, why ignored

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Simple and straightforward structure
✅ Three specialized prompts based on sub-subdomain
✅ Output language based on user selection
✅ Professional and supportive tone

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from SocialStatusReputationEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["social_status_recognition_analysis"] = {
    "recognition_potential": "EXCELLENT" | "GOOD" | "MODERATE" | "LIMITED" | "CHALLENGING",
    "recognition_score": int (0-100),
    "fame_type": [...],
    "favorable_factors": [...],
    "challenging_factors": [...],
    "recognition_areas": [...]
}

additional_data["social_status_risk_analysis"] = {
    "risk_level": "LOW" | "MODERATE" | "HIGH",
    "risk_score": int (0-100),
    "risk_factors": [...],
    "protection_factors": [...],
    "specific_risks": [...],
    "protection_advice": [...]
}

additional_data["social_status_social_analysis"] = {
    "social_standing": "EXCELLENT" | "GOOD" | "MODERATE" | "NEEDS_IMPROVEMENT" | "CHALLENGING",
    "social_score": int (0-100),
    "favorable_factors": [...],
    "challenging_factors": [...],
    "improvement_tips": [...],
    "social_strengths": [...]
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

DOMAIN_PREFIX = "social_status"


class SocialStatusAndReputationPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Family and Friends → Social Status and Reputation
    v1.0 - Vedic-only analysis
    """

    domain = "Family_Friends"
    subtopic = "Social Status and Reputation"

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
                "10th_house": "दशम भाव के स्वामी [planet] [house] भाव में हैं। इसका अर्थ है कि आपकी सार्वजनिक छवि...",
                "recognition_high": "मान-सम्मान और पहचान के अच्छे योग हैं।",
                "recognition_moderate": "पहचान के लिए प्रयास आवश्यक है।",
                "recognition_low": "पहचान में समय लग सकता है।",
                "risk_low": "प्रतिष्ठा को जोखिम कम है।",
                "risk_high": "सावधानी आवश्यक है - प्रतिष्ठा की रक्षा करें।",
                "social_good": "सामाजिक स्थिति अच्छी है।",
                "social_challenging": "सामाजिक संबंधों में सुधार की गुंजाइश है।",
                "tell_client": "TELL CLIENT",
                "recognition_outlook": "पहचान संभावना",
                "risk_outlook": "जोखिम स्तर",
                "social_outlook": "सामाजिक स्थिति"
            },
            "English": {
                "10th_house": "The lord of 10th house [planet] is placed in [house] house. This indicates about your public image...",
                "recognition_high": "Good potential for recognition and honours.",
                "recognition_moderate": "Recognition requires consistent effort.",
                "recognition_low": "Recognition may take time to achieve.",
                "risk_low": "Risk to reputation is low.",
                "risk_high": "Caution needed - protect your reputation.",
                "social_good": "Social standing is good.",
                "social_challenging": "Social relationships have room for improvement.",
                "tell_client": "TELL CLIENT",
                "recognition_outlook": "Recognition Potential",
                "risk_outlook": "Risk Level",
                "social_outlook": "Social Standing"
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
        """Build system prompt for social status and reputation analysis"""
        
        return f"""You are an expert Vedic astrologer specializing in social status, public reputation, and recognition.

**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED - Do not invent planetary positions
2. DISTINGUISH FACTS FROM INTERPRETATION
3. NO GUARANTEES - Present as "indications" and "tendencies"
4. RETROGRADE ≠ WEAKNESS - Retrograde indicates review, not weakness
5. BE BALANCED - Reputation matters are sensitive

═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR SOCIAL STATUS
═══════════════════════════════════════════════════════════════════════════════

- 10th House: Public image, reputation, status, authority (PRIMARY)
- 11th House: Social circle, gains, recognition, achievements
- 1st House: Self, personality, how world perceives you
- 5th House: Honours, awards, intelligence, creativity
- 6th House: Enemies, scandals, opposition
- 7th House: Public dealings, partnerships
- 8th House: Hidden enemies, scandals, blackmail, secrets
- 12th House: Hidden enemies, losses, defamation

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Sun: Authority, fame, recognition, government honours
- Jupiter: Wisdom, respect, good reputation, blessings
- Saturn: Long-term reputation, karma, public service
- Mercury: Communication, public speaking, media
- Venus: Charm, likability, arts recognition
- Rahu: Sudden fame, scandals, unconventional recognition
- Ketu: Spiritual recognition, detachment from fame

═══════════════════════════════════════════════════════════════════════════════
                    WRITING RULES
═══════════════════════════════════════════════════════════════════════════════

1. Write in FLOWING PARAGRAPHS, not bullet lists
2. Every fact needs INTERPRETATION
3. "TELL CLIENT:" only in final summary
4. Be PROFESSIONAL and BALANCED
5. For risks, focus on PROTECTION strategies
6. For social issues, be SUPPORTIVE and give HOPE
"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_recognition_potential(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        rec = additional_data.get(f"{DOMAIN_PREFIX}_recognition_analysis", {})
        return rec.get("recognition_potential", "MODERATE")

    def _get_recognition_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        rec = additional_data.get(f"{DOMAIN_PREFIX}_recognition_analysis", {})
        return rec.get("recognition_score", 50)

    def _get_fame_types(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        rec = additional_data.get(f"{DOMAIN_PREFIX}_recognition_analysis", {})
        return rec.get("fame_type", [])

    def _get_risk_level(self, additional_data: Dict) -> str:
        if not additional_data:
            return "LOW"
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("risk_level", "LOW")

    def _get_risk_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 30
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("risk_score", 30)

    def _get_specific_risks(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        return risk.get("specific_risks", [])

    def _get_social_standing(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        social = additional_data.get(f"{DOMAIN_PREFIX}_social_analysis", {})
        return social.get("social_standing", "MODERATE")

    def _get_social_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        social = additional_data.get(f"{DOMAIN_PREFIX}_social_analysis", {})
        return social.get("social_score", 50)

    def _get_social_strengths(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        social = additional_data.get(f"{DOMAIN_PREFIX}_social_analysis", {})
        return social.get("social_strengths", [])

    def _format_recognition_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        rec = additional_data.get(f"{DOMAIN_PREFIX}_recognition_analysis", {})
        if not rec:
            return ""
        
        lines = ["RECOGNITION ANALYSIS:"]
        lines.append(f"• Potential: {rec.get('recognition_potential', 'MODERATE')}")
        lines.append(f"• Score: {rec.get('recognition_score', 50)}/100")
        
        fame_types = rec.get("fame_type", [])
        if fame_types:
            lines.append(f"• Fame Areas: {', '.join(fame_types[:3])}")
        
        for f in rec.get("favorable_factors", [])[:3]:
            lines.append(f"  ✅ {f}")
        for f in rec.get("challenging_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        
        return "\n".join(lines)

    def _format_risk_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        risk = additional_data.get(f"{DOMAIN_PREFIX}_risk_analysis", {})
        if not risk:
            return ""
        
        lines = ["REPUTATION RISK ANALYSIS:"]
        lines.append(f"• Risk Level: {risk.get('risk_level', 'LOW')}")
        lines.append(f"• Score: {risk.get('risk_score', 30)}/100")
        
        specific = risk.get("specific_risks", [])
        if specific:
            lines.append(f"• Specific Risks: {', '.join(specific[:3])}")
        
        for f in risk.get("risk_factors", [])[:3]:
            lines.append(f"  🚨 {f}")
        for f in risk.get("protection_factors", [])[:2]:
            lines.append(f"  🛡️ {f}")
        for a in risk.get("protection_advice", [])[:2]:
            lines.append(f"  💡 {a}")
        
        return "\n".join(lines)

    def _format_social_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        social = additional_data.get(f"{DOMAIN_PREFIX}_social_analysis", {})
        if not social:
            return ""
        
        lines = ["SOCIAL STANDING ANALYSIS:"]
        lines.append(f"• Standing: {social.get('social_standing', 'MODERATE')}")
        lines.append(f"• Score: {social.get('social_score', 50)}/100")
        
        strengths = social.get("social_strengths", [])
        if strengths:
            lines.append(f"• Strengths: {', '.join(strengths[:3])}")
        
        for f in social.get("favorable_factors", [])[:2]:
            lines.append(f"  ✅ {f}")
        for f in social.get("challenging_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        for t in social.get("improvement_tips", [])[:2]:
            lines.append(f"  💡 {t}")
        
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
            
            # Highlight 10th house
            prefix = "★" if house_num == 10 else "•"
            lines.append(
                f"{prefix} H{house_num}: {lord} in H{lord_house} | {dignity} | Str:{strength}"
                )

        
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
        """Main routing method - routes to appropriate specialized builder"""
        
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""

            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}, language: {language}")
            
            question_lower = question.lower()
            
            # Route based on sub_subdomain or question keywords
            if "Risk" in sub_subdomain or any(kw in question_lower for kw in 
                ["risk", "scandal", "blackmail", "defamation", "misinformation", "protect"]):
                return self._build_risk_prompt(question, additional_data, raw, language)
            
            elif "Social" in sub_subdomain or any(kw in question_lower for kw in 
                ["ignoring", "social circle", "relationships", "improve", "standing"]):
                return self._build_social_prompt(question, additional_data, raw, language)
            
            else:
                # Default: Recognition and Honour
                return self._build_recognition_prompt(question, additional_data, raw, language)
        
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

You are an expert Vedic astrologer specializing in reputation and social status.

QUESTION: "{question}"

Provide a helpful analysis focusing on:
- 10th house (public image, reputation)
- 11th house (social circle, achievements)
- Sun and Jupiter for recognition

Write in flowing paragraphs. Be balanced and professional.
"""

    # ==========================================================================
    # RECOGNITION PROMPT
    # ==========================================================================
    def _build_recognition_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for recognition and honour questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        recognition_potential = self._get_recognition_potential(additional_data)
        recognition_score = self._get_recognition_score(additional_data)
        fame_types = self._get_fame_types(additional_data)
        risk_level = self._get_risk_level(additional_data)
        social_standing = self._get_social_standing(additional_data)
        
        recognition_data = self._format_recognition_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_recognition = self._get_example_text(language, "recognition_outlook")
        starters = self._get_analysis_starters(language)

        # Recognition text
        if recognition_score >= 60:
            recognition_text = self._get_example_text(language, "recognition_high")
        elif recognition_score >= 40:
            recognition_text = self._get_example_text(language, "recognition_moderate")
        else:
            recognition_text = self._get_example_text(language, "recognition_low")

        # Fame types string
        fame_str = ", ".join(fame_types[:3]) if fame_types else "Various fields possible"

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: RECOGNITION AND HONOURS
Current Date: {today_str}
Weightage: VEDIC 100%
Recognition Potential: {recognition_potential} ({recognition_score}/100)
Fame Areas: {fame_str}
Social Standing: {social_standing}
Risk Level: {risk_level}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{recognition_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

NOTE:
House lords data is provided for reference only.
Do NOT restate dignity or strength mechanically.
Use it only to support interpretation.

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_recognition}: {recognition_text}
Fame Areas: {fame_str}
Brief assessment of recognition potential.
Avoid technical astrological jargon.
Use plain, client-friendly language.

(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – PUBLIC IMAGE (10th House):
Begin with: "{starters['vedic']}"
- 10th house analysis (reputation, status)
- 10th lord strength and placement
- Sun's role as fame karaka
- Overall public standing

PARAGRAPH 2 – ACHIEVEMENTS & HONOURS (11th House):
- 11th house analysis (gains, achievements)
- 11th lord placement
- Potential for awards and recognition
- Jupiter's blessings for honours

PARAGRAPH 3 – FAME AREAS:
- Types of recognition indicated: {fame_str}
- Which fields suit you best
- Planetary influences supporting recognition
- Your unique path to recognition

PARAGRAPH 4 – PERSONALITY & CHARISMA (1st House):
- How others perceive you
- Natural charisma and appeal
- Venus/Mercury influence on likability
- Your public persona

PARAGRAPH 5 – EFFORT & PROGRESSION:
- How recognition builds through consistent actions.
- What sustained effort is required
- Building reputation over time
- Patience vs shortcuts


PARAGRAPH 6 – RECOMMENDATIONS:
- How to enhance recognition
- Best strategies for your chart
- Fields to focus on
- Building lasting reputation

SUMMARY:
{lbl_tell}: "[Recognition potential + Best fame areas + Key advice]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Sun remedy for authority and recognition
- Jupiter remedy for respect and honours
- 10th house strengthening

REMEDIES_GENERAL:
- Build expertise in your field
- Network with influential people
- Maintain integrity and ethics
- Be consistent in public image

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # RISK PROMPT
    # ==========================================================================
    def _build_risk_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for reputation risk questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        risk_level = self._get_risk_level(additional_data)
        risk_score = self._get_risk_score(additional_data)
        specific_risks = self._get_specific_risks(additional_data)
        recognition_potential = self._get_recognition_potential(additional_data)
        
        risk_data = self._format_risk_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_risk = self._get_example_text(language, "risk_outlook")
        starters = self._get_analysis_starters(language)

        # Risk text
        if risk_score >= 50:
            risk_text = self._get_example_text(language, "risk_high")
        else:
            risk_text = self._get_example_text(language, "risk_low")

        # Specific risks string
        risks_str = ", ".join(specific_risks[:3]) if specific_risks else "General vigilance advised"

        # High risk warning
        risk_warning = ""
        if risk_level == "HIGH":
            risk_warning = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ HIGH REPUTATION RISK INDICATED
- Specific risks: {risks_str}
- Focus on PROTECTION strategies
- Recommend proactive measures
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: REPUTATION RISK & PROTECTION
Current Date: {today_str}
Weightage: VEDIC 100%
Risk Level: {risk_level} ({risk_score}/100)
Specific Risks: {risks_str}
Recognition Potential: {recognition_potential}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{risk_warning}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{risk_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

NOTE:
House lords data is provided for reference only.
Do NOT restate dignity or strength mechanically.
Use it only to support interpretation.

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_risk}: {risk_text}
Avoid technical astrological jargon.
Use plain, client-friendly language.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – REPUTATION FOUNDATION (10th House):
Begin with: "{starters['vedic']}"
- 10th house strength
- Current reputation standing
- Natural protection level
- Baseline reputation health

PARAGRAPH 2 – ENEMY INFLUENCES (6th House):
- 6th house and open enemies
- Competition and rivals
- Who might oppose you
- Workplace/professional risks

PARAGRAPH 3 – HIDDEN DANGERS (8th House):
- 8th house analysis (secrets, scandals)
- Hidden enemies or issues
- Risk of secrets being exposed
- Blackmail or manipulation risks

PARAGRAPH 4 – SECRET ENEMIES (12th House):
- 12th house analysis
- Behind-the-scenes threats
- Self-undoing tendencies
- Defamation and rumor risks

PARAGRAPH 5 – PROTECTION FACTORS:
- Jupiter's protective influence
- Strong planets shielding reputation
- Natural resilience in chart
- What works in your favor

PARAGRAPH 6 – PROTECTION STRATEGY:
- Specific steps to protect reputation
- What to be careful about
- How to handle threats
- Building reputation resilience

SUMMARY:
{lbl_tell}: "[Risk level + Main threat area + Key protection advice]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Jupiter remedy for divine protection
- Sun remedy for authority and respect
- Hanuman worship for protection from enemies

REMEDIES_GENERAL:
- Maintain impeccable ethics
- Document important interactions
- Build strong support network
- Address issues proactively, not reactively
- Avoid controversial public statements

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # SOCIAL PROMPT
    # ==========================================================================
    def _build_social_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for social relationships questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        social_standing = self._get_social_standing(additional_data)
        social_score = self._get_social_score(additional_data)
        social_strengths = self._get_social_strengths(additional_data)
        recognition_potential = self._get_recognition_potential(additional_data)
        
        social_data = self._format_social_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get improvement tips
        social_analysis = additional_data.get(f"{DOMAIN_PREFIX}_social_analysis", {})
        improvement_tips = social_analysis.get("improvement_tips", [])
        challenging_factors = social_analysis.get("challenging_factors", [])
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_social = self._get_example_text(language, "social_outlook")
        starters = self._get_analysis_starters(language)

        # Social text
        if social_score >= 55:
            social_text = self._get_example_text(language, "social_good")
        else:
            social_text = self._get_example_text(language, "social_challenging")

        # Strengths string
        strengths_str = ", ".join(social_strengths[:3]) if social_strengths else "Hidden strengths to discover"

        # Challenges text
        challenges_text = ""
        if challenging_factors:
            challenges_text = f"""
IDENTIFIED CHALLENGES:
{chr(10).join(['• ' + c for c in challenging_factors[:4]])}
"""

        # Tips text
        tips_text = ""
        if improvement_tips:
            tips_text = f"""
IMPROVEMENT TIPS FROM ANALYSIS:
{chr(10).join(['• ' + t for t in improvement_tips[:3]])}
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: SOCIAL RELATIONSHIPS & STANDING
Current Date: {today_str}
Weightage: VEDIC 100%
Social Standing: {social_standing} ({social_score}/100)
Social Strengths: {strengths_str}
Recognition Potential: {recognition_potential}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY NOTE:
═══════════════════════════════════════════════════════════════════════════════
- This person may be feeling socially isolated
- Be compassionate and constructive
- Focus on SOLUTIONS, not just problems
- Emphasize their STRENGTHS
- Give HOPE and PRACTICAL ADVICE
═══════════════════════════════════════════════════════════════════════════════

{challenges_text}

{tips_text}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{social_data}

═══════════════════════════════════════════════════════════════════════════════
VEDIC DATA:
═══════════════════════════════════════════════════════════════════════════════

NOTE:
House lords data is provided for reference only.
Do NOT restate dignity or strength mechanically.
Use it only to support interpretation.

{lords_data if lords_data else "House lords data not available."}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{lbl_social}: {social_text}
Compassionate acknowledgment of the situation.
Brief hopeful outlook.
Avoid technical astrological jargon.
Use plain, client-friendly language.

(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – UNDERSTANDING THE SITUATION:
Begin with: "{starters['vedic']}"
- 11th house analysis (social circle)
- Why social connections may be challenging
- Chart-based influences affecting social life
- This reflects a current pattern, not a fixed condition.

PARAGRAPH 2 – YOUR SOCIAL STRENGTHS:
- What makes you likeable: {strengths_str}
- 1st house and personality
- Venus/Mercury influence
- Hidden qualities to leverage

PARAGRAPH 3 – POSSIBLE REASONS FOR DISTANCE:
- Astrological factors causing isolation
- Saturn/Ketu effects
- Communication blocks
- Karmic patterns

PARAGRAPH 4 – WHAT YOU CAN CHANGE:
- Practical steps based on chart
- Communication improvements
- Types of people to connect with
- Activities to build connections

PARAGRAPH 5 – BUILDING BETTER CONNECTIONS:
- How to attract right people
- Strengthening existing bonds
- Quality over quantity
- Patience in social growth

PARAGRAPH 6 – IMPROVEMENT ACTION PLAN:
- Step 1: Self-reflection
- Step 2: Reaching out
- Step 3: Building new connections
- Step 4: Maintaining relationships

SUMMARY:
{lbl_tell}: "[Social situation + Key strength + Primary improvement action]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Venus remedy for social charm
- Mercury remedy for communication
- Jupiter remedy for good company

REMEDIES_GENERAL:
- Reach out first - don't wait
- Join groups aligned with interests
- Be genuinely interested in others
- Practice active listening
- Focus on giving, not just receiving

═══════════════════════════════════════════════════════════════════════════════
"""
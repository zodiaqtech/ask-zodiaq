"""
Friendship – LLM Prompts v1.0 (VEDIC-ONLY)

Specialized prompt builder for analyzing friendship compatibility, strength,
longevity, and potential issues using Vedic astrology principles.

DESIGN DECISIONS:
✅ VEDIC-ONLY analysis (NO KP points)
✅ Simple and straightforward structure
✅ Two question types: Compatibility & Improvement
✅ Output language based on user selection
✅ Warm and supportive tone

Weightage:
- ALL QUESTIONS: Vedic 100% (NO KP, NO TIMING)

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA STRUCTURE (from FriendshipEvaluator v1.0):
═══════════════════════════════════════════════════════════════════════════════

additional_data["friendship_strength_analysis"] = {
    "friendship_strength": "STRONG" | "GOOD" | "MODERATE" | "WEAK" | "CHALLENGING",
    "strength_score": int (0-100),
    "longevity": "LONG-LASTING" | "MODERATE",
    "favorable_factors": [...],
    "challenging_factors": [...],
    "improvement_tips": [...]
}

additional_data["friendship_compatibility_analysis"] = {
    "compatibility_level": "HIGH" | "GOOD" | "MODERATE" | "NEEDS_WORK",
    "compatibility_score": int (0-100),
    "compatible_traits": [...],
    "challenging_traits": [...],
    "best_friend_types": [...]
}

additional_data["friendship_dispute_analysis"] = {
    "dispute_potential": "LOW" | "MODERATE" | "HIGH",
    "dispute_score": int (0-100),
    "betrayal_risk": "LOW" | "MODERATE" | "HIGH",
    "dispute_factors": [...],
    "protection_factors": [...],
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

DOMAIN_PREFIX = "friendship"


class StrengthOfFriendshipsPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Family and Friends → Strength of Friendship
    v1.0 - Vedic-only analysis (Simple Structure)
    """

    domain = "Family_Friends"
    subtopic = "Strength of Friendship"

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
                "11th_house": "एकादश भाव के स्वामी [planet] [house] भाव में हैं। इसका अर्थ है कि मित्रता के मामले में...",
                "strength_strong": "आपकी मित्रता मजबूत और स्थायी है।",
                "strength_moderate": "मित्रता में कुछ उतार-चढ़ाव हो सकते हैं।",
                "strength_weak": "मित्रता को पोषण की आवश्यकता है।",
                "compatibility_high": "आप दोस्त बनाने में स्वाभाविक रूप से अच्छे हैं।",
                "compatibility_moderate": "सही लोगों से मिलने पर अच्छी दोस्ती होती है।",
                "dispute_low": "मित्रों के साथ विवाद की संभावना कम है।",
                "dispute_high": "कुछ मतभेद हो सकते हैं - धैर्य रखें।",
                "betrayal_warning": "विश्वास धीरे-धीरे बनाएं।",
                "tell_client": "TELL CLIENT",
                "strength_outlook": "मित्रता की मजबूती",
                "compatibility_outlook": "संगतता",
                "dispute_outlook": "विवाद संभावना"
            },
            "English": {
                "11th_house": "The lord of 11th house [planet] is placed in [house] house. This indicates about friendships...",
                "strength_strong": "Your friendships are strong and lasting.",
                "strength_moderate": "Friendships may have some ups and downs.",
                "strength_weak": "Friendships need nurturing and effort.",
                "compatibility_high": "You naturally make friends easily.",
                "compatibility_moderate": "Good friendships form with the right people.",
                "dispute_low": "Dispute potential with friends is low.",
                "dispute_high": "Some differences may arise - maintain patience.",
                "betrayal_warning": "Build trust gradually.",
                "tell_client": "TELL CLIENT",
                "strength_outlook": "Friendship Strength",
                "compatibility_outlook": "Compatibility",
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
        """Build system prompt for friendship analysis"""
        
        return f"""You are an expert Vedic astrology analyst interpreting structured evaluator data related to friendships.


**VEDIC-ONLY ANALYSIS (100%)**

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. ONLY USE DATA PROVIDED - Do not invent planetary positions
2. DISTINGUISH FACTS FROM INTERPRETATION
3. NO GUARANTEES - Present as "indications" and "tendencies"
4. RETROGRADE ≠ WEAKNESS - Retrograde indicates review, not weakness
5. BE SUPPORTIVE - Friendship issues can be sensitive
6. DO NOT mention zodiac signs, nakshatras, or degrees unless explicitly present in evaluator data


═══════════════════════════════════════════════════════════════════════════════
                    KEY HOUSES FOR FRIENDSHIP
═══════════════════════════════════════════════════════════════════════════════

- 11th House: Friends, social circle, gains through friends (PRIMARY)
- 3rd House: Communication, courage, social interactions
- 5th House: Recreation, enjoyment with friends
- 7th House: One-on-one partnerships, close bonds
- 1st House: Self, personality, how others perceive you
- 6th House: Disputes, conflicts, enemies
- 8th House: Betrayal, hidden issues, sudden breaks
- 12th House: Losses, secret enemies, isolation

═══════════════════════════════════════════════════════════════════════════════
                    KEY KARAKAS (SIGNIFICATORS)
═══════════════════════════════════════════════════════════════════════════════

- Jupiter: True friends, wisdom, good company, blessings
- Venus: Social charm, harmony, enjoyable friendships
- Mercury: Communication, intellectual connections
- Saturn: Long-lasting friendships, older friends, karma
- Mars: Competition, conflicts, energy in friendships
- Rahu: Unconventional friends, deception, fair-weather friends
- Moon: Emotional bonds, intuitive connections

═══════════════════════════════════════════════════════════════════════════════
                    WRITING RULES
═══════════════════════════════════════════════════════════════════════════════

1. Write in FLOWING PARAGRAPHS, not bullet lists
2. Every fact needs INTERPRETATION
3. "TELL CLIENT:" only in final summary
4. Be WARM and SUPPORTIVE - friendship issues are emotional
5. Focus on IMPROVEMENT and SOLUTIONS
6. Focus on COMPATIBLE TRAITS rather than specific types of people

"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_friendship_strength(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        strength = additional_data.get(f"{DOMAIN_PREFIX}_strength_analysis", {})
        return strength.get("friendship_strength", "MODERATE")

    def _get_strength_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        strength = additional_data.get(f"{DOMAIN_PREFIX}_strength_analysis", {})
        return strength.get("strength_score", 50)

    def _get_longevity(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        strength = additional_data.get(f"{DOMAIN_PREFIX}_strength_analysis", {})
        return strength.get("longevity", "MODERATE")

    def _get_compatibility_level(self, additional_data: Dict) -> str:
        if not additional_data:
            return "MODERATE"
        compat = additional_data.get(f"{DOMAIN_PREFIX}_compatibility_analysis", {})
        return compat.get("compatibility_level", "MODERATE")

    def _get_compatibility_score(self, additional_data: Dict) -> int:
        if not additional_data:
            return 50
        compat = additional_data.get(f"{DOMAIN_PREFIX}_compatibility_analysis", {})
        return compat.get("compatibility_score", 50)

    def _get_best_friend_types(self, additional_data: Dict) -> List[str]:
        if not additional_data:
            return []
        compat = additional_data.get(f"{DOMAIN_PREFIX}_compatibility_analysis", {})
        return compat.get("best_friend_types", [])

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

    def _get_betrayal_risk(self, additional_data: Dict) -> str:
        if not additional_data:
            return "LOW"
        dispute = additional_data.get(f"{DOMAIN_PREFIX}_dispute_analysis", {})
        return dispute.get("betrayal_risk", "LOW")

    def _format_strength_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        strength = additional_data.get(f"{DOMAIN_PREFIX}_strength_analysis", {})
        if not strength:
            return ""
        
        lines = ["FRIENDSHIP STRENGTH ANALYSIS:"]
        lines.append(f"• Strength: {strength.get('friendship_strength', 'MODERATE')}")
        lines.append(f"• Score: {strength.get('strength_score', 50)}/100")
        lines.append(f"• Longevity: {strength.get('longevity', 'MODERATE')}")
        
        for f in strength.get("favorable_factors", [])[:3]:
            lines.append(f"  ✅ {f}")
        for f in strength.get("challenging_factors", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        for t in strength.get("improvement_tips", [])[:2]:
            lines.append(f"  💡 {t}")
        
        return "\n".join(lines)

    def _format_compatibility_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        compat = additional_data.get(f"{DOMAIN_PREFIX}_compatibility_analysis", {})
        if not compat:
            return ""
        
        lines = ["COMPATIBILITY ANALYSIS:"]
        lines.append(f"• Level: {compat.get('compatibility_level', 'MODERATE')}")
        lines.append(f"• Score: {compat.get('compatibility_score', 50)}/100")
        
        friend_types = compat.get("best_friend_types", [])
        if friend_types:
            lines.append(f"• Best Friend Types: {', '.join(friend_types[:3])}")
        
        for f in compat.get("compatible_traits", [])[:2]:
            lines.append(f"  ✅ {f}")
        for f in compat.get("challenging_traits", [])[:2]:
            lines.append(f"  ⚠️ {f}")
        
        return "\n".join(lines)

    def _format_dispute_analysis(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        
        dispute = additional_data.get(f"{DOMAIN_PREFIX}_dispute_analysis", {})
        if not dispute:
            return ""
        
        lines = ["DISPUTE & BETRAYAL ANALYSIS:"]
        lines.append(f"• Dispute Potential: {dispute.get('dispute_potential', 'LOW')}")
        lines.append(f"• Score: {dispute.get('dispute_score', 30)}/100")
        lines.append(f"• Betrayal Risk: {dispute.get('betrayal_risk', 'LOW')}")
        
        for f in dispute.get("dispute_factors", [])[:3]:
            lines.append(f"  🔥 {f}")
        for f in dispute.get("protection_factors", [])[:2]:
            lines.append(f"  🛡️ {f}")
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
            
            # Highlight 11th house
            prefix = "★" if house_num == 11 else "•"
            lines.append(f"{prefix} H{house_num}: {prefix} H{house_num}: {lord} influencing H{lord_house} | {dignity} | Strength:{strength}")
        
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
            
            # Check if it's an "improvement" question
            question_lower = question.lower()
            is_improvement_query = any(kw in question_lower for kw in 
                ["ignoring", "improve", "why", "distant", "not talking", "lost"])
            
            if is_improvement_query:
                return self._build_improvement_prompt(question, additional_data, raw, language)
            else:
                return self._build_compatibility_prompt(question, additional_data, raw, language)
        
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

You are an expert Vedic astrology analyst interpreting structured friendship evaluator data.

QUESTION: "{question}"

Provide a helpful analysis focusing on:
- 11th house (friends, social circle)
- Jupiter and Venus for good friendships
- Mercury for communication

Write in flowing paragraphs. Be warm and supportive.
"""

    # ==========================================================================
    # COMPATIBILITY PROMPT (Main Question)
    # ==========================================================================
    def _build_compatibility_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for friendship compatibility questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        friendship_strength = self._get_friendship_strength(additional_data)
        strength_score = self._get_strength_score(additional_data)
        longevity = self._get_longevity(additional_data)
        compatibility_level = self._get_compatibility_level(additional_data)
        compatibility_score = self._get_compatibility_score(additional_data)
        best_friend_types = self._get_best_friend_types(additional_data)
        dispute_potential = self._get_dispute_potential(additional_data)
        dispute_score = self._get_dispute_score(additional_data)
        betrayal_risk = self._get_betrayal_risk(additional_data)
        
        strength_data = self._format_strength_analysis(additional_data)
        compatibility_data = self._format_compatibility_analysis(additional_data)
        dispute_data = self._format_dispute_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        lbl_strength = self._get_example_text(language, "strength_outlook")
        lbl_compat = self._get_example_text(language, "compatibility_outlook")
        lbl_dispute = self._get_example_text(language, "dispute_outlook")
        starters = self._get_analysis_starters(language)

        # Strength text
        if strength_score >= 60:
            strength_text = self._get_example_text(language, "strength_strong")
        elif strength_score >= 40:
            strength_text = self._get_example_text(language, "strength_moderate")
        else:
            strength_text = self._get_example_text(language, "strength_weak")

        # Compatibility text
        if compatibility_score >= 55:
            compat_text = self._get_example_text(language, "compatibility_high")
        else:
            compat_text = self._get_example_text(language, "compatibility_moderate")

        # Dispute text
        if dispute_score >= 45:
            dispute_text = self._get_example_text(language, "dispute_high")
        else:
            dispute_text = self._get_example_text(language, "dispute_low")

        # Best friend types string
        friend_types_str = ", ".join(best_friend_types[:3]) if best_friend_types else "people with compatible values and communication styles"


        # Betrayal warning
        betrayal_warning = ""
        if betrayal_risk in ["MODERATE", "HIGH"]:
            betrayal_warning = f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️ BETRAYAL RISK: {betrayal_risk}
- {self._get_example_text(language, "betrayal_warning")}
- Be selective about sharing personal matters
═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: FRIENDSHIP COMPATIBILITY & STRENGTH
Current Date: {today_str}
Weightage: VEDIC 100%
Friendship Strength: {friendship_strength} ({strength_score}/100)
Longevity: {longevity}
Compatibility: {compatibility_level} ({compatibility_score}/100)
Best Friend Types: {friend_types_str}
Dispute Potential: {dispute_potential} ({dispute_score}/100)
Betrayal Risk: {betrayal_risk}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{betrayal_warning}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{strength_data}

{compatibility_data}

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
{lbl_strength}: {strength_text}
{lbl_compat}: {compat_text}
{lbl_dispute}: {dispute_text}
Brief assessment of friendship potential.
Avoid technical astrological jargon. Use simple, client-friendly language.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – FRIENDSHIP POTENTIAL (11th House):
Begin with: "{starters['vedic']}"
- 11th house analysis (friends, social circle)
- 11th lord strength and placement
- Jupiter's role in true friendships
- Overall friendship blessings

PARAGRAPH 2 – YOUR SOCIAL PERSONALITY:
- 1st house and personality traits
- Venus for charm and likability
- Mercury for communication skills
- How others perceive you

PARAGRAPH 3 – COMPATIBILITY & BEST MATCHES:
- Types of people you connect with best
- {friend_types_str}
- Moon house influence on emotional bonding
- Emotional needs in friendships


PARAGRAPH 4 – LONGEVITY OF FRIENDSHIPS:
- Saturn's role in lasting bonds
- Factors supporting long friendships
- Any challenges to longevity
- How to maintain friendships

PARAGRAPH 5 – DISPUTE & BETRAYAL POTENTIAL:
- 6th house connection (disputes)
- 8th house influence (betrayal)
- Mars/Rahu effects on friendships
- Warning signs to watch for

PARAGRAPH 6 – PROTECTION FACTORS:
- Jupiter's grace and protection
- Venus for harmony
- What shields your friendships
- Your natural advantages

PARAGRAPH 7 – RECOMMENDATIONS:
- How to strengthen friendships
- Types of friends to seek
- What to avoid
- Building lasting bonds

SUMMARY:
{lbl_tell}: "[Friendship strength + Best matches + Key advice]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Jupiter remedy for genuine friends
- Venus remedy for social harmony
- Mercury remedy for communication

REMEDIES_GENERAL:
- Stay in regular touch with friends
- Be a good listener
- Choose quality over quantity
- Be trustworthy to attract trust

═══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # IMPROVEMENT PROMPT (Why friends ignoring)
    # ==========================================================================
    def _build_improvement_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for friendship improvement questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Get evaluator data
        friendship_strength = self._get_friendship_strength(additional_data)
        strength_score = self._get_strength_score(additional_data)
        compatibility_level = self._get_compatibility_level(additional_data)
        dispute_potential = self._get_dispute_potential(additional_data)
        betrayal_risk = self._get_betrayal_risk(additional_data)
        
        strength_data = self._format_strength_analysis(additional_data)
        compatibility_data = self._format_compatibility_analysis(additional_data)
        dispute_data = self._format_dispute_analysis(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        # Get improvement tips
        strength_analysis = additional_data.get(f"{DOMAIN_PREFIX}_strength_analysis", {})
        improvement_tips = strength_analysis.get("improvement_tips", [])
        challenging_factors = strength_analysis.get("challenging_factors", [])
        
        # Get language-specific text
        lbl_tell = self._get_example_text(language, "tell_client")
        starters = self._get_analysis_starters(language)

        # Format challenges
        challenges_text = ""
        if challenging_factors:
            challenges_text = f"""
IDENTIFIED CHALLENGES:
{chr(10).join(['• ' + c for c in challenging_factors[:4]])}
"""

        # Format tips
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
QUERY: WHY FRIENDS MAY BE DISTANT & HOW TO IMPROVE
Current Date: {today_str}
Weightage: VEDIC 100%
Friendship Strength: {friendship_strength} ({strength_score}/100)
Compatibility: {compatibility_level}
Dispute Potential: {dispute_potential}
Betrayal Risk: {betrayal_risk}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
⚠️ SENSITIVITY NOTE:
═══════════════════════════════════════════════════════════════════════════════
- This person may be feeling lonely or rejected
- Be compassionate and constructive
- Focus on SOLUTIONS, not just problems
- Emphasize that planetary influences can be worked with
- Give HOPE and PRACTICAL ADVICE
═══════════════════════════════════════════════════════════════════════════════

{challenges_text}

{tips_text}

═══════════════════════════════════════════════════════════════════════════════
EVALUATOR DATA:
═══════════════════════════════════════════════════════════════════════════════

{strength_data}

{compatibility_data}

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
Compassionate acknowledgment of the situation.
Brief explanation of what may be happening.
Hopeful statement about improvement.
NO astrological terms. Be warm and supportive.
(3-4 lines only)

ASTROLOGICAL_ANALYSIS:
Write in FLOWING PARAGRAPHS:

PARAGRAPH 1 – UNDERSTANDING THE SITUATION:
Begin with: "{starters['vedic']}"
- 11th house analysis
- Why friendships may be challenging currently
- Evaluator-indicated factors causing distance
- This is NOT a permanent state

PARAGRAPH 2 – POSSIBLE REASONS (Astrological):
- 11th lord placement issues
- Saturn/Rahu effects on social life
- Communication blocks (Mercury/3rd house)
- Karmic patterns in friendships

PARAGRAPH 3 – YOUR NATURAL STRENGTHS:
- Positive factors in your chart
- What makes you a good friend
- Hidden qualities to leverage
- Reasons for hope

PARAGRAPH 4 – WHAT YOU CAN CHANGE:
- Practical steps based on chart
- Communication improvements
- Types of friends to seek
- Activities to build connections

PARAGRAPH 5 – PATIENCE & PROGRESSION:
- Why friendship phases change gradually
- Importance of consistency and patience
- Avoiding impulsive reactions
- Long-term improvement mindset


PARAGRAPH 6 – DETAILED IMPROVEMENT PLAN:
- Step 1: Internal work
- Step 2: Reaching out
- Step 3: Building new connections
- Step 4: Maintaining bonds

SUMMARY:
{lbl_tell}: "[Reason for distance + Key improvement action + Hopeful outlook]"
(2-3 lines only)

REMEDIES_ASTROLOGICAL:
- Mercury remedy for better communication
- Venus remedy to enhance likability
- Jupiter remedy to attract genuine friends

REMEDIES_GENERAL:
- Reach out first - don't wait for others
- Join groups aligned with your interests
- Be genuinely interested in others
- Quality friendships take time to build
- Consider if you're being too selective or closed

═══════════════════════════════════════════════════════════════════════════════
"""
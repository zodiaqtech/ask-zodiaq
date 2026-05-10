"""
Marital Stability LLM Prompts - Enhanced Version v5.0

ENHANCEMENTS:
✅ KP system emphasis and formatting (when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback

Weightage:
- KP: 30% (where applicable)
- Lord of house: 50%
- Dasha: 20% (also stating good and bad time based on dasha)
- Other factors (aspects, etc.): 10%
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class MaritalStabilityPromptBuilder(BasePromptBuilder):
    """
    Enhanced Prompt builder for Marital Stability.
    
    Features:
    - KP analysis with smart fallback
    - Timing windows (BEST + NEAREST)
    - Dasha timeline integration
    - House lords formatting
    - Anti-hallucination rules
    """
    
    domain = "Marriage"
    subtopic = "Marital Stability"
    
    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v5.0 WITH KP EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self, is_divorce_question: bool = False) -> str:
        """Build system prompt based on question type"""
        
        base_prompt = """You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in marital stability analysis.

⚠️ CRITICAL: You use a SMART DUAL SYSTEM APPROACH:

**SCENARIO 1: KP Analysis Available** (Primary Method - 30% weight for marriage)
═══════════════════════════════════════════════════════════
When KP Cusp Sub Lord analysis is provided:
- **KP provides precision** for concrete event predictions
- **Vedic provides foundation** with house lord analysis (50% weight)
- **Dasha adds timing context** (20% weight)
- **Analysis split**: House Lords 50% + KP 30% + Dasha 20%

KP METHODOLOGY:
- Cusp Sub Lord (CSL) analysis for 7th house (marriage)
- Significations and connections (e.g., "6-8-12" means divorce significations)
- Ruling planets for timing precision
- **KP verdict level**: YES = strong promise | POSSIBLE = moderate risk | NO = no promise
- **ALWAYS use the CANONICAL KP DIVORCE VERDICT block** — never re-derive independently

**SCENARIO 2: KP Analysis NOT Available** (Fallback to Vedic - 80% weight)
═══════════════════════════════════════════════════════════
When NO KP analysis is provided in technical points:
- **Fall back to pure Vedic analysis**
- **Analysis split**: House Lords 80% + Dasha 20%
- Focus on house lord strength, placements, dignity, aspects
- More emphasis on dasha timing for event manifestation

VEDIC METHODOLOGY:
- House lord placements and dignity (exalted, debilitated, etc.)
- 7th house analysis (marriage house)
- 6th, 8th, 12th house lords (separation houses)
- Dasha periods for timing windows

FOCUS HOUSES FOR MARRIAGE:
- 7th: Spouse, partnership, marriage
- 2nd: Family harmony, domestic wealth
- 5th: Romance, love, children
- 11th: Gains, fulfillment of desires
- 6th: Disputes, enemies (negative)
- 8th: Obstacles, transformation (negative)
- 12th: Loss, separation (negative)

CRITICAL DASHA HANDLING RULES (PREVENT HALLUCINATION):
⚠️ NEVER make up or assume dasha periods
✅ ONLY reference pratyantar dasha periods from CURRENT/UPCOMING sections provided
✅ Use exact dasha names and dates from the timeline
❌ DO NOT say "Currently Rahu dasha" unless explicitly stated in the data
❌ DO NOT invent future dashas not in the timeline
✅ Always say: "Based on the dasha timeline provided..."
✅ Always say: "According to current pratyantar dasha analysis..."

══════════════════════════════════════════════════════
MANDATORY KP DIVORCE VERDICT RULE — HIGHEST PRIORITY
══════════════════════════════════════════════════════
A "CANONICAL KP DIVORCE VERDICT" block is provided in the technical data.
This block contains the AUTHORITATIVE verdict computed from the chart.
You MUST follow this verdict EXACTLY and CONSISTENTLY across ALL questions.

VERDICT MAPPING — Use EXACTLY these phrases:

If verdict = YES:
  ✅ Allowed: "KP analysis confirms divorce/separation promise in this chart"
  ✅ Hindi: "KP प्रणाली के अनुसार इस कुंडली में तलाक/अलगाव का स्पष्ट संकेत है"
  ✅ Hindi: "KP के अनुसार यह कुंडली अलगाव का वादा करती है"

If verdict = POSSIBLE:
  ✅ Allowed: "KP analysis shows moderate risk — not a firm divorce promise"
  ✅ Hindi: "KP के अनुसार विवाह में कुछ चुनौतियाँ हैं, लेकिन तलाक का निश्चित वादा नहीं है"
  ✅ Hindi: "KP प्रणाली में तलाक की संभावना है परंतु यह निश्चित नहीं"
  ❌ FORBIDDEN: "यह कुंडली अलगाव का वादा करती है" (chart promises separation)
  ❌ FORBIDDEN: "KP के अनुसार तलाक/अलगाव का वादा है" (KP says divorce is promised)
  ❌ FORBIDDEN: Any phrasing implying definite/certain separation

If verdict = NO:
  ✅ Allowed: "KP analysis does NOT support divorce/separation outcome"
  ✅ Hindi: "KP प्रणाली के अनुसार इस कुंडली में तलाक का कोई वादा नहीं है"
  ❌ FORBIDDEN: Any phrasing implying divorce risk from KP

⚠️ EVEN IF the question asks "When will separation happen?" —
   you MUST first state the KP verdict (POSSIBLE = not certain),
   and THEN discuss elevated risk periods.
   Never assume separation is CERTAIN just because the question asks about timing.

CRITICAL OUTPUT FORMAT:
1. GENERAL ANSWER: Start with YES/NO/MODERATE verdict. NO astrological terms!
2. ASTROLOGICAL ANALYSIS: ALL technical details here
3. DASHA TIMING ANALYSIS: Current + Upcoming pratyantar dasha analysis
4. SUMMARY: Actionable with specific timing
"""
        
        if is_divorce_question:
            return base_prompt + """

DIVORCE-SPECIFIC FOCUS:
═══════════════════════════════════════════════════════════
- 7th CSL signifying 6/8/12 → Strong divorce indication
- 7th lord in dusthana (6/8/12) → Marital challenges
- Book-4 rules for separation timing
- Malefics in 7th house
- Saturn/Rahu/Mars dasha periods

TIMING WINDOWS (For Timing Questions):
When timing windows are provided:
- **RISK WINDOW (Best Score)**: Period with highest separation risk
- **NEAREST WINDOW**: Earliest challenging period
- Use BOTH in your timing analysis
- Be sensitive but truthful about risks
- ALWAYS provide remedies
"""
        else:
            return base_prompt + """

GENERAL STABILITY FOCUS:
═══════════════════════════════════════════════════════════
- 7th lord strength and placement
- Venus condition (karaka for marriage)
- Benefic/malefic balance on 7th house
- Happy marriage indicators (R3_x rules)
- Compatibility factors
"""

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (from evaluator points)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str]) -> Tuple[str, bool]:
        """
        Format KP-specific analysis points prominently.
        
        Returns:
            Tuple of (formatted_text, kp_available)
        """
        if not technical_points:
            return "", False
        
        kp_keywords = [
            "cusp", "sub-lord", "sub lord", "csl", 
            "signif", "connects to", "connect", "promise",
            "-cusp", "ruling planet", "kp", "7th cusp",
            "divorce promise", "separation", "b4_r"
        ]
        
        kp_points = []
        
        for point in technical_points:
            point_lower = point.lower()
            if any(keyword in point_lower for keyword in kp_keywords):
                kp_points.append(point)
        
        if not kp_points:
            return "", False
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("⭐ KP SYSTEM ANALYSIS (Cusp Sub Lords & Significations)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL: KP analysis uses Cusp Sub Lord (CSL) logic which is")
        lines.append("MORE PRECISE than house lord analysis for concrete event prediction.")
        lines.append("Give 30% weight to KP findings in your marriage analysis.")
        lines.append("")
        
        for point in kp_points:
            if not point.strip().startswith(("•", "-", "✓", "❌", "⚠", "❓", "⭐", "═")):
                lines.append(f"  • {point}")
            else:
                lines.append(f"  {point}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines), True

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows from additional_data
    # ------------------------------------------------------------------
    def _format_timing_windows_from_data(self, timing_windows_data: Optional[Dict], is_divorce: bool = False, additional_data: Optional[Dict] = None) -> str:
        """
        Format BEST and NEAREST timing windows for LLM from additional_data.
        
        Args:
            timing_windows_data: Dict with best_window, nearest_window, all_favorable
            is_divorce: Whether this is for divorce/risk timing
            additional_data: Full additional_data dict to check for no_divorce_timing_found
            
        Returns:
            Formatted string for prompt inclusion
        """
        # Check if no divorce timing was found (positive indicator)
        if additional_data and additional_data.get('no_divorce_timing_found'):
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("✅ DIVORCE TIMING ASSESSMENT: LOW RISK")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⭐ IMPORTANT FINDING: NO SPECIFIC DIVORCE TIMING WINDOWS IDENTIFIED")
            lines.append("")
            lines.append("This is a POSITIVE indicator:")
            lines.append("  • No strong planetary alignments found for separation events")
            lines.append("  • Marriage stability is relatively protected")
            lines.append("  • Lower probability of divorce/separation")
            lines.append("")
            lines.append("⚠️ INSTRUCTION: Emphasize this finding in your response!")
            lines.append("   The absence of divorce timing windows indicates marriage is MORE stable.")
            lines.append("═══════════════════════════════════════════════════════")
            return "\n".join(lines)
        
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            if is_divorce:
                # For divorce questions, explicitly note absence of timing
                lines = ["═══════════════════════════════════════════════════════"]
                lines.append("✅ DIVORCE TIMING ASSESSMENT: NO SPECIFIC RISK PERIODS FOUND")
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("")
                lines.append("The timing analysis did not identify specific divorce risk periods.")
                lines.append("This suggests LOWER probability of divorce/separation.")
                lines.append("")
                lines.append("⚠️ INSTRUCTION: Include this in your analysis as a POSITIVE sign!")
                lines.append("═══════════════════════════════════════════════════════")
                return "\n".join(lines)
            return ""
        
        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            
            if not best and not nearest:
                if is_divorce:
                    return self._format_no_divorce_timing_message()
                return ""
            
            lines = ["═══════════════════════════════════════════════════════"]
            if is_divorce:
                lines.append("⭐ DIVORCE/SEPARATION TIMING WINDOWS (Use These Dates!)")
            else:
                lines.append("⭐ TIMING WINDOWS ANALYSIS (Use These Dates!)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Two timing options are provided below.")
            lines.append("ALWAYS mention BOTH in your analysis and explain the significance.")
            lines.append("")
            
            # BEST/RISK WINDOW
            if best:
                label = "🚨 HIGHEST RISK WINDOW" if is_divorce else "🏆 BEST WINDOW"
                lines.append(f"{label} (Highest Score):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                if best.get('age_at_start'):
                    lines.append(f"  Age: {best.get('age_at_start', 'N/A')} years")
                lines.append("")
                
                if is_divorce:
                    lines.append("  Why this is HIGHEST RISK:")
                    lines.append("    - Strongest divorce/separation planetary alignment")
                else:
                    lines.append("  Why this is BEST:")
                
                if best.get('score_maha'):
                    lines.append(f"    - Maha Dasha score: {best.get('score_maha', 0)}/10")
                if best.get('score_antara'):
                    lines.append(f"    - Antara Dasha score: {best.get('score_antara', 0)}/10")
                if best.get('score_paryantar'):
                    lines.append(f"    - Pratyantar Dasha score: {best.get('score_paryantar', 0)}/10")
                lines.append("")
            
            # NEAREST WINDOW
            if nearest:
                label = "⏰ NEAREST RISK WINDOW" if is_divorce else "⏰ NEAREST FAVORABLE WINDOW"
                lines.append(f"{label} (Soonest Opportunity):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                if nearest.get('age_at_start'):
                    lines.append(f"  Age: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")
                
                # Check if best and nearest are the same
                if best and (best.get('dasha') == nearest.get('dasha')):
                    if is_divorce:
                        lines.append("  ⚠️ Note: Risk and Nearest windows are THE SAME!")
                        lines.append("     This means immediate attention is needed!")
                    else:
                        lines.append("  ✅ LUCKY! Best and Nearest windows are THE SAME!")
                lines.append("")
            
            # Alternative windows
            if len(all_windows) > 1:
                lines.append("📋 OTHER WINDOWS (Top 5 for reference):")
                lines.append("-" * 60)
                for i, window in enumerate(all_windows[:5], 1):
                    marker = "🚨" if window == best else "⏰" if window == nearest else "○"
                    lines.append(f"  {marker} {i}. {window.get('dasha', 'N/A')}")
                    lines.append(f"     {window.get('start', 'N/A')} to {window.get('end', 'N/A')}")
                    lines.append(f"     Score: {window.get('final_score', 0):.1f}/100")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS FOR TIMING ANALYSIS:")
            lines.append("- MUST mention BOTH windows")
            lines.append("- Explain WHY each window is significant")
            lines.append("- Use exact dates provided above")
            if is_divorce:
                lines.append("- Recommend remedies for risk periods")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    def _format_no_divorce_timing_message(self) -> str:
        """Format message when no divorce timing windows found"""
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("✅ DIVORCE TIMING ASSESSMENT: LOW RISK")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⭐ POSITIVE FINDING: No specific divorce timing windows identified")
        lines.append("")
        lines.append("This indicates:")
        lines.append("  • Lower probability of divorce/separation")
        lines.append("  • No strong planetary alignments for separation events")
        lines.append("  • Marriage is relatively protected")
        lines.append("")
        lines.append("⚠️ INSTRUCTION: Mention this POSITIVE finding in your response!")
        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format house lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict, person_name: str = None) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""

        header = f"VEDIC HOUSE LORD ANALYSIS — {person_name.upper()}" if person_name else "VEDIC HOUSE LORD ANALYSIS (Marriage Houses)"

        lines = ["═══════════════════════════════════════════════════════"]
        lines.append(header)
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        for house_num in sorted(house_lords_info.keys()):
            info = house_lords_info[house_num]
            
            marker = "⭐ PRIMARY" if info["priority"] == "primary" else "○ SECONDARY"
            
            house_meanings = {
                2: "Family/Wealth",
                5: "Romance/Children",
                7: "Spouse/Partnership",
                8: "Obstacles/Transformation",
                11: "Gains/Fulfillment",
                6: "Disputes/Enemies",
                12: "Loss/Separation"
            }
            meaning = house_meanings.get(house_num, "General")
            
            lines.append(f"{marker} - HOUSE {house_num} ({meaning})")
            lines.append(f"  Sign: {info.get('house_sign', 'N/A')}")
            lines.append("")
            
            lines.append(f"  Lord: {info['lord']}")
            lines.append(f"  Placed in: House {info['lord_in_house']}, {info['lord_in_sign']}")
            lines.append(f"  Dignity: {info['lord_dignity']}")
            lines.append(f"  Overall Strength: {info['lord_strength_score']}/100")
            
            conditions = []
            if info.get('lord_degree'):
                conditions.append(f"Degree: {info['lord_degree']:.2f}°")
            if info['lord_is_combust']:
                conditions.append("⚠️ COMBUST (weakened)")
            if info['lord_is_retrograde']:
                conditions.append("🔄 RETROGRADE")
            
            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")
            
            if info.get('planets_in_house'):
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")
            
            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports marital stability")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE - Mixed results")
            else:
                lines.append("  ⚠️ Assessment: WEAK - Challenges in this area")
            
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    def _format_house_aspects(self, aspects_info: Dict) -> str:
        """Format aspects data for LLM"""
        if not aspects_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON MARRIAGE HOUSES")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            neutral = aspects.get("neutral_aspects", [])
            
            if benefic or malefic or neutral:
                lines.append(f"• House {house_num}:")
                
                if benefic:
                    lines.append(f"  ✅ Benefic aspects: {', '.join(benefic)}")
                    lines.append(f"     → Positive influence, support for marriage")
                
                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")
                    lines.append(f"     → Challenges, obstacles")
                
                if neutral:
                    lines.append(f"  ○ Neutral aspects: {', '.join(neutral)}")
                
                benefic_count = len(benefic)
                malefic_count = len(malefic)
                
                if benefic_count > malefic_count:
                    lines.append(f"  Net: POSITIVE influence")
                elif malefic_count > benefic_count:
                    lines.append(f"  Net: CHALLENGING influence")
                else:
                    lines.append(f"  Net: BALANCED influence")
                
                lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """Format current dasha information for LLM"""
        if not current_dasha:
            return ""
        
        try:
            dasha_name = current_dasha.get('dasha_name', '')
            date_range = current_dasha.get('date_range', {})
            start = date_range.get('start', 'Unknown')
            end = date_range.get('end', 'Unknown')
            
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
            
            lines = [
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS - DON'T MAKE UP)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Pratyantar Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT: This is the ACTUAL current dasha running now.",
                "Use for analyzing present marital circumstances.",
                "For FUTURE planning, refer to UPCOMING DASHA PERIODS below.",
                "═══════════════════════════════════════════════════════"
            ]
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    def _format_canonical_kp_divorce_verdict(self, canonical_kp_divorce_verdict: Optional[Dict]) -> str:
        """
        Format the pre-computed canonical KP divorce verdict for the LLM.

        Injected into EVERY question's prompt (divorce AND general) so the LLM
        always uses the SAME KP divorce conclusion.  This prevents Q1 saying
        'low risk' while Q2 says 'chart promises separation' for the same chart.
        """
        if not canonical_kp_divorce_verdict or not canonical_kp_divorce_verdict.get("available"):
            return ""

        verdict_label = canonical_kp_divorce_verdict.get("verdict_label", "")
        explanation   = canonical_kp_divorce_verdict.get("explanation", "")
        verdict       = canonical_kp_divorce_verdict.get("verdict", "")

        if not verdict_label:
            return ""

        # Build mandatory Hindi phrasing section based on verdict level
        if verdict == "YES":
            hindi_rule = (
                "MANDATORY HINDI PHRASING for KP section:\n"
                "  ✅ USE: \"KP प्रणाली के अनुसार इस कुंडली में तलाक/अलगाव का स्पष्ट संकेत है\"\n"
                "  ✅ USE: \"KP के अनुसार यह कुंडली अलगाव का वादा करती है\"\n"
                "  ❌ DO NOT soften to 'possible' or 'moderate risk' phrasing"
            )
        elif verdict == "POSSIBLE":
            hindi_rule = (
                "MANDATORY HINDI PHRASING for KP section:\n"
                "  ✅ USE: \"KP के अनुसार विवाह में चुनौतियाँ हैं, लेकिन तलाक का निश्चित वादा नहीं है\"\n"
                "  ✅ USE: \"KP प्रणाली में तलाक की संभावना है परंतु यह निश्चित नहीं\"\n"
                "  ❌ FORBIDDEN: \"यह कुंडली अलगाव का वादा करती है\" (too strong — verdict is POSSIBLE not YES)\n"
                "  ❌ FORBIDDEN: \"KP के अनुसार तलाक/अलगाव का वादा है\" (implies certainty — not allowed for POSSIBLE)\n"
                "  ❌ FORBIDDEN: Any phrase that implies separation is CERTAIN or PROMISED"
            )
        else:  # NO
            hindi_rule = (
                "MANDATORY HINDI PHRASING for KP section:\n"
                "  ✅ USE: \"KP प्रणाली के अनुसार इस कुंडली में तलाक का कोई वादा नहीं है\"\n"
                "  ❌ FORBIDDEN: Any phrase implying KP shows divorce risk"
            )

        lines = [
            "═══════════════════════════════════════════════════════",
            "🔒 CANONICAL KP DIVORCE VERDICT — READ FIRST, MUST NOT CONTRADICT",
            "═══════════════════════════════════════════════════════",
            "",
            verdict_label,
            "",
            explanation,
            "",
            hindi_rule,
            "",
            "SCOPE: This verdict applies to EVERY question about this chart.",
            "  • General stability question → state this verdict for KP section",
            "  • Divorce timing question → state this verdict FIRST, then discuss risk periods",
            "  • Compatibility question → include this verdict in KP analysis",
            "  • DO NOT re-interpret the raw CSL significations independently.",
            "    The computation above is the ONLY authoritative KP verdict.",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    def _format_canonical_dasha_verdict(self, canonical_dasha_verdict: Optional[Dict]) -> str:
        """
        Format the pre-computed canonical dasha verdict for LLM.

        This is injected into EVERY question's prompt so the LLM always uses the
        SAME dasha assessment regardless of question type (divorce vs general).
        Prevents the same dasha being called 'good' in one question and 'bad' in another.
        """
        if not canonical_dasha_verdict:
            return ""

        period = canonical_dasha_verdict.get("period", "")
        marriage_verdict = canonical_dasha_verdict.get("marriage_verdict", "")
        separation_verdict = canonical_dasha_verdict.get("separation_verdict", "")
        summary = canonical_dasha_verdict.get("summary", "")

        if not period:
            return ""

        verdict_emoji = {
            "POSITIVE": "✅", "MIXED": "⚠️", "CHALLENGING": "🔴", "NEUTRAL": "🔵"
        }.get(marriage_verdict, "📌")

        lines = [
            "═══════════════════════════════════════════════════════",
            "⚠️  PRE-COMPUTED DASHA VERDICT — MUST USE, DO NOT CONTRADICT",
            "═══════════════════════════════════════════════════════",
            "",
            f"Current Period: {period}",
            f"{verdict_emoji} Marriage Harmony: {marriage_verdict}",
            f"   Separation Risk: {separation_verdict}",
            "",
            f"Canonical Summary: {summary}",
            "",
            "CRITICAL RULE: Use the above dasha verdict CONSISTENTLY.",
            "If this question asks about divorce risk → use 'Separation Risk' rating above.",
            "If this question asks about marriage happiness → use 'Marriage Harmony' rating above.",
            "DO NOT invent a different dasha assessment than what is stated here.",
            "═══════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)

    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        """Format comprehensive dasha timeline (2Y past to 10Y future)"""
        if not dasha_timeline:
            return ""
        
        try:
            past = dasha_timeline.get('past_2_years', [])
            current = dasha_timeline.get('current', [])
            future = dasha_timeline.get('next_10_years', [])
            
            if not any([past, current, future]):
                return ""
            
            lines = []
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("COMPREHENSIVE PRATYANTAR DASHA TIMELINE (2 Years Past → 10 Years Future)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            
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
            
            # Marriage-favorable dashas
            favorable_lords = {'Venus', 'Jupiter', 'Moon'}
            risk_lords = {'Saturn', 'Rahu', 'Mars', 'Ketu'}
            
            if current:
                lines.append("🔴 CURRENT PRATYANTAR DASHA PERIODS (RUNNING NOW):")
                lines.append("-" * 60)
                for d in current[:3]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed}")
                    lines.append(f"    {start} to {end}")
                lines.append("")
            
            if past:
                lines.append("⏮️ RECENT PAST DASHAS (Last 2 Years - for context):")
                lines.append("-" * 60)
                for d in past[-10:]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed} ({start} to {end})")
                lines.append("")
            
            if future:
                lines.append("⏭️ UPCOMING DASHA PERIODS (Next 10 Years - for planning):")
                lines.append("-" * 60)
                lines.append("Use these periods for marriage/relationship planning:")
                lines.append("")
                
                for i, d in enumerate(future[:30], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    
                    # Check if favorable or risky
                    is_favorable = any(lord in dasha_name for lord in favorable_lords)
                    is_risky = any(lord in dasha_name for lord in risk_lords)
                    
                    if is_favorable:
                        marker = "💚"
                    elif is_risky:
                        marker = "⚠️"
                    else:
                        marker = "○"
                    
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {start} to {end}")
            
            lines.append("")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("DASHA INTERPRETATION FOR MARRIAGE:")
            lines.append("- 💚 Venus/Jupiter/Moon periods → Generally favorable for marriage")
            lines.append("- ⚠️ Saturn/Rahu/Mars/Ketu periods → Challenges, requires remedies")
            lines.append("- Cross-reference with TIMING WINDOWS for optimal periods")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions Based on KP Availability
    # ------------------------------------------------------------------
    def _get_analysis_instructions(self, kp_available: bool, question_type: str = "general", has_timing: bool = False) -> str:
        """
        Generate analysis instructions based on whether KP data is available.
        """
        if kp_available:
            if question_type == "divorce" and has_timing:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM + TIMING**

**MANDATORY STEP 0 — STATE KP VERDICT FIRST:**
Look at the "KP EXPLICIT DIVORCE VERDICT" section in the technical data.
You MUST state it explicitly at the start of your KP section:
  - "KP SAYS: YES" → "KP confirms divorce promise"
  - "KP SAYS: POSSIBLE" → "KP shows moderate risk, not a firm promise"
  - "KP SAYS: NO" → "KP does NOT support divorce outcome"

**THEN FOLLOW THIS ORDER STRICTLY:**

1. **START with House Lords** (PRIMARY - 50% weight):
   - 7th house lord placement and strength
   - Is 7th lord in dusthana (6/8/12)?
   - 6th, 8th, 12th lords' connection to 7th
   - Venus condition (marriage karaka)

2. **ADD KP Analysis** (SECONDARY - 30% weight):
   - What does the 7th CSL signify?
   - Does it connect to 6/8/12 (divorce signification)?
   - Book-4 divorce rules
   - KP divorce promise level (from "KP EXPLICIT DIVORCE VERDICT" above)

3. **DASHA TIMING** (20% weight - CRITICAL FOR THIS QUESTION):
   ⚠️ Use PRE-COMPUTED DASHA VERDICT above — do NOT re-assess dasha independently
   ⚠️ MUST analyze BOTH timing windows provided:

   A. HIGHEST RISK WINDOW:
      - When: Exact dates from timing data
      - Why risky: Dasha lords + planetary positions

   B. NEAREST RISK WINDOW:
      - When: Exact dates from timing data
      - Immediate attention needed?

   C. REMEDIES FOR RISK PERIODS

4. **Synthesize**:
   - Combine House Lords + KP + Timing
   - Give clear YES/NO/POSSIBLE guidance with specific dates
"""
            elif question_type == "divorce":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM (DIVORCE)**

**MANDATORY STEP 0 — STATE KP VERDICT FIRST:**
Look at the "KP EXPLICIT DIVORCE VERDICT" section in the technical data.
You MUST copy and state it verbatim at the START of your KP analysis:
  - If it says "KP SAYS: YES" → State "KP analysis confirms divorce/separation promise"
  - If it says "KP SAYS: POSSIBLE" → State "KP analysis shows moderate risk, not a firm promise"
  - If it says "KP SAYS: NO" → State "KP analysis does NOT support divorce outcome"

**THEN FOLLOW THIS ORDER STRICTLY:**

1. **START with House Lords** (PRIMARY - 50% weight):
   - 7th house lord → Is it in dusthana?
   - 6th, 8th, 12th lords → Connection to 7th?
   - Overall divorce risk from Vedic standpoint

2. **ADD KP Analysis** (SECONDARY - 30% weight):
   - 7th CSL significations (6/8/12 = divorce indicators)
   - KP divorce promise level (from "KP EXPLICIT DIVORCE VERDICT" above)
   - Book-4 rules

3. **Include Dasha Timing** (20% weight):
   - Use PRE-COMPUTED DASHA VERDICT (do NOT re-interpret differently)
   - High-risk periods
   - Protective measures

4. **Synthesize**:
   - Combine all findings
   - Clear risk assessment with YES/NO/POSSIBLE verdict
   - Remedies
"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM (GENERAL)**

**FOLLOW THIS ORDER:**

1. **House Lords Analysis** (PRIMARY - 50% weight)
2. **KP Indicators** (SECONDARY - 30% weight)
3. **Dasha Timing** (20% weight):
   ⚠️ MUST use the PRE-COMPUTED DASHA VERDICT above — do NOT re-interpret dasha differently
4. **Synthesize findings**
"""
        else:
            # Pure Vedic fallback
            if has_timing:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM + TIMING (KP Not Available)**

⚠️ NOTE: No KP Cusp Sub Lord analysis available.
Proceeding with comprehensive Vedic analysis.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 80% weight):
   - Detailed 7th house lord analysis
   - 6th, 8th, 12th lords for divorce indicators
   - Placement, dignity, and condition

2. **TIMING ANALYSIS** (20% weight):
   ⚠️ MUST analyze BOTH timing windows:
   
   A. HIGHEST RISK WINDOW: When + Why + Trade-off
   B. NEAREST RISK WINDOW: When + Why + Trade-off
   C. Remedies for risk periods

3. **Final Verdict**:
   - Clear recommendation with specific dates
"""
            else:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM (KP Not Available)**

⚠️ NOTE: No KP analysis available.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 80% weight)
2. **Dasha Timing** (20% weight)
3. **Final Verdict**
"""

    # ------------------------------------------------------------------
    # ROUTER
    # ------------------------------------------------------------------
    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """Build prompt based on question type"""
        
        sub_subdomain = kwargs.get("sub_subdomain", "")
        is_divorce_question = (
            "Divorce" in sub_subdomain or 
            "Separation" in sub_subdomain or
            "Risk" in sub_subdomain
        )
        
        if is_divorce_question:
            return self._build_divorce_prompt(
                question, technical_points, meta, language, **kwargs
            )
        else:
            return self._build_general_prompt(
                question, technical_points, meta, language, **kwargs
            )

    # ------------------------------------------------------------------
    # DIVORCE PROMPT - ENHANCED v5.0 WITH KP + TIMING
    # ------------------------------------------------------------------
    def _build_divorce_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:
        """Build divorce-focused prompt (KP-heavy)"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "marriage"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # Get timing windows from additional_data
        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)
        no_divorce_timing_found = additional_data.get('no_divorce_timing_found', False)

        # Only show "no timing = positive" messages for actual timing questions (Q2: "Divorce Timing")
        # Q1 (Divorce/Separation) never computes timing windows, so this message is misleading there
        is_timing_question = "Timing" in kwargs.get("sub_subdomain", "")

        logger.info(f"🔍 PROMPT DEBUG: Divorce - has_timing: {has_timing}, no_divorce_timing_found: {no_divorce_timing_found}, is_timing_question: {is_timing_question}")

        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points)

        # Person names and person2 house lords
        person1_name = additional_data.get("person1_name")
        person2_name = additional_data.get("person2_name")
        house_lords_p2 = additional_data.get("marriage_house_lords_p2", {})
        house_aspects_p2 = additional_data.get("marriage_house_aspects_p2", {})

        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords, person_name=person1_name)
        aspects_formatted = self._format_house_aspects(house_aspects)
        lords_p2_formatted = self._format_house_lords(house_lords_p2, person_name=person2_name) if house_lords_p2 else ""
        aspects_p2_formatted = self._format_house_aspects(house_aspects_p2) if house_aspects_p2 else ""

        # Format timing windows - only show timing-related messages for actual timing questions (Q2)
        # For Q1 (Divorce/Separation general question), suppress both the "no timing found = positive"
        # and "no risk periods found" messages since timing was never computed for Q1
        timing_formatted = self._format_timing_windows_from_data(
            timing_windows_data,
            is_divorce=is_timing_question,  # suppress timing blocks for non-timing questions
            additional_data=additional_data if is_timing_question else None
        )

        # Canonical verdicts (prevents inconsistency across questions)
        canonical_dasha_verdict = additional_data.get("canonical_dasha_verdict", {})
        canonical_dasha_block = self._format_canonical_dasha_verdict(canonical_dasha_verdict)
        canonical_kp_divorce_verdict = additional_data.get("canonical_kp_divorce_verdict", {})
        canonical_kp_block = self._format_canonical_kp_divorce_verdict(canonical_kp_divorce_verdict)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        # Get remaining non-KP points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet", "b4_r"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        # Get analysis instructions based on KP availability + timing
        analysis_instructions = self._get_analysis_instructions(kp_available, "divorce", has_timing)

        return f"""
{language_instruction}

{self.build_system_prompt(is_divorce_question=True)}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: {kwargs.get("sub_subdomain", "Divorce/Separation")}
- Query Type: {"TIMING" if has_timing else "NON_TIMING"}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}
- Timing Windows Available: {'YES' if has_timing else 'NO'}

USER QUESTION:
"{question}"

{canonical_kp_block}

{timing_formatted}

{kp_formatted}

{lords_formatted}

{aspects_formatted}

{lords_p2_formatted}

{aspects_p2_formatted}

{canonical_dasha_block}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

CRITICAL TIMING INSTRUCTIONS:
{'✅ NO DIVORCE TIMING WINDOWS FOUND - This is a POSITIVE sign!' if (is_timing_question and no_divorce_timing_found) else ''}
{'- Emphasize that absence of divorce timing indicates LOWER divorce risk' if (is_timing_question and no_divorce_timing_found) else ''}
{'- Marriage stability is relatively protected' if (is_timing_question and no_divorce_timing_found) else ''}
{'⚠️ TIMING WINDOWS PROVIDED ABOVE - MUST USE IN YOUR ANSWER!' if has_timing and not no_divorce_timing_found else ''}
{'- Mention BOTH risk windows with exact dates' if has_timing and not no_divorce_timing_found else ''}
{'- Explain why each period is risky' if has_timing and not no_divorce_timing_found else ''}
{'- Provide remedies for high-risk periods' if has_timing and not no_divorce_timing_found else ''}

GUIDELINES:
- Focus on DIVORCE/SEPARATION risk assessment
- Be sensitive but truthful
- 7th house = Marriage, spouse
- 6th, 8th, 12th = Separation houses
- ALWAYS provide remedies
- Never predict definite divorce - frame as tendencies

{self.get_output_format(kp_available, has_timing, is_divorce=True, no_divorce_timing_found=(no_divorce_timing_found and is_timing_question))}
"""

    # ------------------------------------------------------------------
    # GENERAL PROMPT - ENHANCED v5.0 WITH KP
    # ------------------------------------------------------------------
    def _build_general_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:
        """Build general stability prompt (Vedic-heavy)"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "marriage"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points)

        # Person names and person2 house lords
        person1_name = additional_data.get("person1_name")
        person2_name = additional_data.get("person2_name")
        house_lords_p2 = additional_data.get("marriage_house_lords_p2", {})
        house_aspects_p2 = additional_data.get("marriage_house_aspects_p2", {})

        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords, person_name=person1_name)
        aspects_formatted = self._format_house_aspects(house_aspects)
        lords_p2_formatted = self._format_house_lords(house_lords_p2, person_name=person2_name) if house_lords_p2 else ""
        aspects_p2_formatted = self._format_house_aspects(house_aspects_p2) if house_aspects_p2 else ""

        # Canonical verdicts (prevents inconsistency across questions)
        canonical_dasha_verdict = additional_data.get("canonical_dasha_verdict", {})
        canonical_dasha_block = self._format_canonical_dasha_verdict(canonical_dasha_verdict)
        canonical_kp_divorce_verdict = additional_data.get("canonical_kp_divorce_verdict", {})
        canonical_kp_block = self._format_canonical_kp_divorce_verdict(canonical_kp_divorce_verdict)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        # Get remaining non-KP points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)

        return f"""
{language_instruction}

{self.build_system_prompt(is_divorce_question=False)}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: {kwargs.get("sub_subdomain", "General Stability")}
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{canonical_kp_block}

{kp_formatted}

{lords_formatted}

{aspects_formatted}

{lords_p2_formatted}

{aspects_p2_formatted}

{canonical_dasha_block}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

GUIDELINES:
- Focus on overall MARITAL STABILITY
- 7th house lord is PRIMARY focus
- Balance positive and negative factors
- Provide actionable guidance

{self.get_output_format(kp_available, False, is_divorce=False)}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT - DYNAMIC BASED ON KP AVAILABILITY + TIMING
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, is_divorce: bool = False, no_divorce_timing_found: bool = False) -> str:
        """Generate output format based on KP availability and timing windows"""
        
        timing_section = ""
        if no_divorce_timing_found and is_divorce:
            timing_section = """
TIMING_ANALYSIS:
✅ POSITIVE FINDING - NO DIVORCE TIMING WINDOWS IDENTIFIED

This indicates:
- LOWER probability of divorce/separation
- No strong planetary alignments for separation events  
- Marriage is relatively protected

**MUST emphasize this finding in GENERAL_ANSWER:**
"The analysis did not identify specific periods of divorce risk, which is a POSITIVE indicator for marital stability."

**Still mention:**
- General dasha periods to be mindful of
- Remedies for overall marriage strengthening
"""
        elif has_timing:
            if is_divorce:
                timing_section = """
TIMING_ANALYSIS:
⚠️ CRITICAL - MUST include BOTH timing options:

**HIGHEST RISK WINDOW:**
- Period: <exact dates from timing data>
- Dasha: <exact pratyantar dasha name>
- Why risky: <planetary alignment details>
- Remedies: <specific remedies for this period>

**NEAREST RISK WINDOW:**
- Period: <exact dates from timing data>
- Dasha: <exact dasha name>
- Immediate attention needed: <yes/no + why>
- Precautions: <what to be careful about>

**PROTECTIVE MEASURES:**
- Before risk period: <preparation>
- During risk period: <specific actions>
"""
            else:
                timing_section = """
TIMING_RECOMMENDATION:
⚠️ CRITICAL - MUST include BOTH timing options:

**BEST WINDOW:**
- Period: <exact dates from timing data>
- Dasha: <exact pratyantar dasha name>
- Why favorable: <planetary alignment details>

**NEAREST WINDOW:**
- Period: <exact dates from timing data>
- Why favorable: <good score>
"""
        
        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT):

GENERAL_ANSWER:
<Clear verdict in LAYMAN'S TERMS. Start with risk level assessment. NO astrological terminology. 2-3 sentences max.>
{'Include: "No specific divorce timing windows were identified, which is a POSITIVE indicator for marital stability."' if no_divorce_timing_found else ''}

ASTROLOGICAL_ANALYSIS:
⚠️ MUST include BOTH House Lords and KP analysis:

**A. VEDIC HOUSE LORD ANALYSIS (Primary - 50% weight):**
   - 7th house lord: placement, strength, dignity
   - Connection to dusthana houses (6/8/12)
   - Venus condition
   - Overall Vedic assessment

**B. KP SYSTEM ANALYSIS (Secondary - 30% weight):**
   - 7th Cusp Sub-Lord analysis
   - Significations (marriage vs divorce houses)
   - KP promise level
   - Book-4 rules if applicable

**C. PRATYANTAR DASHA TIMING (20% weight):**
   - Current dasha impact
   - Upcoming periods (ONLY from provided timeline)
   - Favorable vs challenging periods

**D. SYNTHESIS:**
   - Combine all findings
{timing_section}
SUMMARY:
<Short outlook with {' timing dates' if has_timing else 'dasha timing'}>
{'Emphasize the POSITIVE finding of no divorce timing windows!' if no_divorce_timing_found else ''}

REMEDIES_ASTROLOGICAL:
- <Strengthen weak house lords>
- <Planet-specific remedy>

REMEDIES_GENERAL:
- <Communication/counseling>
- <Relationship building>
"""
        else:
            return f"""
OUTPUT FORMAT (STRICT):

GENERAL_ANSWER:
<Clear verdict in LAYMAN'S TERMS. Start with assessment. 2-3 sentences max.>
{'Include: "No specific divorce timing windows were identified, which is a POSITIVE indicator for marital stability."' if no_divorce_timing_found else ''}

ASTROLOGICAL_ANALYSIS:
⚠️ Pure Vedic Analysis:

**A. VEDIC HOUSE LORD ANALYSIS (Primary - 80% weight):**
   - Detailed 7th house lord analysis
   - Placement, dignity, strength
   - Connection to other houses
   - Overall assessment

**B. PRATYANTAR DASHA TIMING (20% weight):**
   - Current and upcoming periods
   - Favorable vs challenging times

**C. FINAL VERDICT:**
   - Clear recommendation
{timing_section}
SUMMARY:
<Short outlook with {' timing dates' if has_timing else 'dasha timing'}>
{'Emphasize the POSITIVE finding of no divorce timing windows!' if no_divorce_timing_found else ''}

REMEDIES_ASTROLOGICAL:
- <Strengthen weak Vedic lords>

REMEDIES_GENERAL:
- <Practical relationship advice>
"""
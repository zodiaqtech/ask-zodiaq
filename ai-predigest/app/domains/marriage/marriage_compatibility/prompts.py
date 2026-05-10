"""
Marriage Compatibility LLM Prompts - Enhanced Version v5.0

ENHANCEMENTS:
✅ KP system emphasis and formatting (when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display for BOTH persons
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting for BOTH charts
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback
✅ Two-person synastry analysis

Weightage:
- House Lords (both charts): 50%
- KP Analysis: 30% (where applicable)
- Dasha: 20%
- Other factors: 10%
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class MarriageCompatibilityPromptBuilder(BasePromptBuilder):
    """
    Enhanced Prompt builder for Marriage Compatibility (two-person analysis).
    
    Features:
    - KP analysis with smart fallback
    - Timing windows (BEST + NEAREST)
    - House lords for BOTH charts
    - Dasha timeline integration
    - Anti-hallucination rules
    """
    
    domain = "Marriage"
    subtopic = "Marriage Compatibility"
    
    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v5.0 WITH KP EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        """Build the system prompt for compatibility analysis"""
        return """You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in two-person relationship compatibility analysis.

⚠️ CRITICAL: You use a SMART DUAL SYSTEM APPROACH:

**SCENARIO 1: KP Analysis Available** (Primary Method - 30% weight)
═══════════════════════════════════════════════════════════
When KP Cusp Sub Lord analysis is provided for both charts:
- **KP provides precision** for concrete compatibility assessment
- **Vedic provides foundation** with house lord analysis (50% weight)
- **Dasha adds timing context** (20% weight)
- **Analysis split**: House Lords 50% + KP 30% + Dasha 20%

KP METHODOLOGY FOR COMPATIBILITY:
- 7th Cusp Sub Lord (CSL) comparison for both persons
- Are the 7th CSLs friendly planets?
- Do they signify marriage houses (2, 7, 11)?
- Check for separation significations (6, 8, 12)

**SCENARIO 2: KP Analysis NOT Available** (Fallback to Vedic - 80% weight)
═══════════════════════════════════════════════════════════
When NO KP analysis is provided:
- **Fall back to pure Vedic analysis**
- **Analysis split**: House Lords 80% + Dasha 20%
- Focus on planetary compatibility (Moon, Venus, Mars, Jupiter)
- Emphasize sign-based matching

COMPATIBILITY FACTORS (In Order of Importance):
1. Moon Sign Compatibility - Emotional connection (20%)
2. Venus Sign Compatibility - Romantic expression (15%)
3. Sun-Moon Cross Connections - Natural attraction (15%)
4. Mars Compatibility & Manglik - Energy matching (10%)
5. Jupiter Compatibility - Growth & wisdom (10%)
6. 7th House Lord Strength - Both charts (15%)
7. KP 7th CSL Analysis - Both charts (15%)

CRITICAL DASHA HANDLING RULES (PREVENT HALLUCINATION):
⚠️ NEVER make up or assume dasha periods
✅ ONLY reference pratyantar dasha periods from provided data
✅ Use exact dasha names and dates from the timeline
❌ DO NOT say "Currently Rahu dasha" unless explicitly stated
❌ DO NOT invent future dashas not in the timeline
✅ Always say: "Based on the dasha timeline provided..."

CORE PRINCIPLES:
1. Present compatibility objectively - highlight strengths AND areas for growth
2. NEVER declare a match "incompatible" - all relationships can work with effort
3. Focus on understanding differences rather than judging them
4. Provide constructive guidance for navigating challenges
5. Respect that love transcends astrological indicators
6. Be encouraging while being truthful about challenges

IMPORTANT:
- Do NOT make deterministic statements about relationship success/failure
- Present scores as indicators, not verdicts
- Emphasize mutual effort and communication as key factors
"""

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis for Both Charts
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], compatibility_data: Dict = None) -> Tuple[str, bool]:
            """
            Format KP-specific analysis points DETERMINISTICALLY.
            
            ENHANCED v2.0:
            - Extracts structured KP data from compatibility_data (no keyword guessing!)
            - Falls back to technical_points only if structured data unavailable
            - Returns (formatted_text, kp_available)
            """
            # ═══════════════════════════════════════════════════════════════
            # PRIMARY: Extract from structured KP data (DETERMINISTIC!)
            # ═══════════════════════════════════════════════════════════════
            kp_structured = None
            if compatibility_data:
                kp_data = compatibility_data.get("detailed_scores", {}).get("kp_compatibility", {})
                if kp_data:
                    kp_structured = kp_data.get("structured_data", {})
            
            # If we have structured KP data, use it!
            if kp_structured and kp_structured.get("person1_7th_csl"):
                lines = ["═══════════════════════════════════════════════════════"]
                lines.append("⭐ KP SYSTEM COMPATIBILITY ANALYSIS")
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("")
                lines.append("⚠️ CRITICAL: KP analysis uses Cusp Sub Lord (CSL) comparison")
                lines.append("for BOTH charts to assess compatibility precision.")
                lines.append("Give 30% weight to KP findings in your analysis.")
                lines.append("")
                
                # Person 1 CSL
                p1_csl = kp_structured.get("person1_7th_csl", "Unknown")
                p1_sign = kp_structured.get("person1_7th_cusp_sign", "")
                if p1_csl and p1_csl != "Unknown":
                    lines.append(f"📍 Person 1:")
                    lines.append(f"   7th Cusp Sub Lord (CSL): {p1_csl}")
                    if p1_sign:
                        lines.append(f"   7th Cusp Sign: {p1_sign}")
                    lines.append("")
                
                # Person 2 CSL
                p2_csl = kp_structured.get("person2_7th_csl", "Unknown")
                p2_sign = kp_structured.get("person2_7th_cusp_sign", "")
                if p2_csl and p2_csl != "Unknown":
                    lines.append(f"📍 Person 2:")
                    lines.append(f"   7th Cusp Sub Lord (CSL): {p2_csl}")
                    if p2_sign:
                        lines.append(f"   7th Cusp Sign: {p2_sign}")
                    lines.append("")
                
                # Verdict and reasoning
                verdict = kp_structured.get("verdict", "Unknown")
                reasoning = kp_structured.get("reasoning", "")
                score = kp_structured.get("score", 0)
                max_score = kp_structured.get("max_score", 15)
                
                lines.append(f"📊 KP Compatibility Assessment:")
                lines.append(f"   Verdict: {verdict}")
                lines.append(f"   Score: {score}/{max_score}")
                lines.append("")
                
                if reasoning:
                    lines.append(f"📝 KP Reasoning:")
                    # Split reasoning into parts if it's a long string
                    reasoning_parts = reasoning.split(". ")
                    for part in reasoning_parts:
                        if part.strip():
                            lines.append(f"   • {part.strip()}")
                    lines.append("")
                
                # Add interpretation instructions
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("⚠️ INSTRUCTIONS FOR KP INTERPRETATION:")
                lines.append("")
                lines.append("VERDICT Meanings:")
                lines.append("  • FAVORABLE: Both CSLs are benefic → Excellent KP compatibility")
                lines.append("  • MIXED: One benefic CSL → Good compatibility, some adjustment needed")
                lines.append("  • NEUTRAL: Neither strongly benefic → Requires careful assessment")
                lines.append("  • INCOMPLETE: Missing KP data for full analysis")
                lines.append("")
                lines.append("YOU MUST:")
                lines.append("  1. State the KP verdict clearly")
                lines.append("  2. Explain what the 7th CSLs indicate for each person")
                lines.append("  3. Discuss how the CSLs interact (friendly/enemy/neutral)")
                lines.append("  4. Connect KP findings with Vedic analysis")
                lines.append("  5. Give this 30% weight in final compatibility assessment")
                lines.append("═══════════════════════════════════════════════════════")
                
                return "\n".join(lines), True
            
            # ═══════════════════════════════════════════════════════════════
            # FALLBACK: Extract from technical_points (less reliable)
            # ═══════════════════════════════════════════════════════════════
            if not technical_points:
                return "", False
            
            kp_keywords = [
                "kp:", "cusp sub lord", "csl", "7th csl", 
                "kp compatibility", "═══ kp"
            ]
            
            kp_points = []
            for point in technical_points:
                point_lower = point.lower()
                if any(keyword in point_lower for keyword in kp_keywords):
                    kp_points.append(point)
            
            if not kp_points:
                return "", False
            
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⭐ KP SYSTEM COMPATIBILITY ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Give 30% weight to KP findings below.")
            lines.append("")
            
            for point in kp_points:
                # Clean up the point
                clean_point = point.strip()
                if clean_point and not clean_point.startswith("═"):
                    if not clean_point.startswith(("•", "-", "✓", "❌", "⚠", "✅", "⚖", "○")):
                        lines.append(f"  • {clean_point}")
                    else:
                        lines.append(f"  {clean_point}")
            
            lines.append("")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines), True
    

    def _format_kp_marriage_promise_both(self, compatibility_data: Dict) -> Tuple[str, bool]:
        """
        Format KP marriage promise analysis for BOTH persons (timing questions).
        
        This is for Marriage Compatibility timing questions where we need
        individual marriage promise for each person.
        
        Returns: (formatted_text, kp_promise_available)
        """
        if not compatibility_data:
            return "", False
        
        kp_promise_data = compatibility_data.get("kp_marriage_promise", {})
        
        if not kp_promise_data:
            return "", False
        
        person1_promise = kp_promise_data.get("person1", {})
        person2_promise = kp_promise_data.get("person2", {})
        
        if not person1_promise and not person2_promise:
            return "", False
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("⭐ KP MARRIAGE PROMISE ANALYSIS (BOTH PERSONS)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL: This shows individual marriage promise from KP")
        lines.append("for BOTH persons. Use this to assess timing favorability.")
        lines.append("")
        
        # Person 1 Promise
        if person1_promise and person1_promise.get("csl"):
            lines.append("👤 PERSON 1 - KP MARRIAGE PROMISE:")
            lines.append("-" * 60)
            
            csl = person1_promise.get("csl", "Unknown")
            state = person1_promise.get("state", "Unknown")
            reasoning = person1_promise.get("reasoning", [])
            
            lines.append(f"  7th Cusp Sub Lord (CSL): {csl}")
            lines.append(f"  Promise State: {state}")
            lines.append("")
            
            if person1_promise.get("benefic"):
                lines.append("  ✅ CSL is benefic → Strong marriage promise")
            elif person1_promise.get("malefic"):
                lines.append("  ⚠️ CSL is malefic → Obstacles possible")
            
            if reasoning:
                lines.append("")
                lines.append("  Reasoning:")
                for reason in reasoning:
                    lines.append(f"    • {reason}")
            
            lines.append("")
        
        # Person 2 Promise
        if person2_promise and person2_promise.get("csl"):
            lines.append("👤 PERSON 2 - KP MARRIAGE PROMISE:")
            lines.append("-" * 60)
            
            csl = person2_promise.get("csl", "Unknown")
            state = person2_promise.get("state", "Unknown")
            reasoning = person2_promise.get("reasoning", [])
            
            lines.append(f"  7th Cusp Sub Lord (CSL): {csl}")
            lines.append(f"  Promise State: {state}")
            lines.append("")
            
            if person2_promise.get("benefic"):
                lines.append("  ✅ CSL is benefic → Strong marriage promise")
            elif person2_promise.get("malefic"):
                lines.append("  ⚠️ CSL is malefic → Obstacles possible")
            
            if reasoning:
                lines.append("")
                lines.append("  Reasoning:")
                for reason in reasoning:
                    lines.append(f"    • {reason}")
            
            lines.append("")
        
        # Combined Assessment
        if person1_promise and person2_promise:
            lines.append("📊 COMBINED KP ASSESSMENT:")
            lines.append("-" * 60)
            
            state1 = person1_promise.get("state", "")
            state2 = person2_promise.get("state", "")
            
            if state1 == "PROMISED" and state2 == "PROMISED":
                lines.append("  ✅ EXCELLENT: Both have strong marriage promise from KP")
                lines.append("  → Timing is highly favorable for marriage")
            elif state1 in ["PROMISED", "PROMISED_WITH_OBSTACLES"] and state2 in ["PROMISED", "PROMISED_WITH_OBSTACLES"]:
                lines.append("  ⚖️ GOOD: Both have marriage promise, some challenges possible")
                lines.append("  → Timing is favorable with awareness of obstacles")
            elif "INCOMPLETE" in [state1, state2]:
                lines.append("  ⚠️ INCOMPLETE: KP data missing for full assessment")
            else:
                lines.append("  ○ MIXED: Individual promises vary, consider other factors")
            
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("⚠️ INSTRUCTIONS FOR KP PROMISE INTERPRETATION:")
        lines.append("")
        lines.append("PROMISE STATES:")
        lines.append("  • PROMISED: Strong marriage indication from KP")
        lines.append("  • PROMISED_WITH_OBSTACLES: Marriage indicated but challenges exist")
        lines.append("  • NEUTRAL: Mixed indicators, depends on other factors")
        lines.append("  • INCOMPLETE: Insufficient KP data")
        lines.append("")
        lines.append("YOU MUST:")
        lines.append("  1. State each person's KP marriage promise")
        lines.append("  2. Explain what their 7th CSL indicates")
        lines.append("  3. Assess combined promise for marriage timing")
        lines.append("  4. Connect with timing windows provided")
        lines.append("  5. Give this 20% weight in timing analysis")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines), True



    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows
    # ------------------------------------------------------------------
    def _format_timing_windows_from_data(self, timing_windows_data: Optional[Dict], additional_data: Optional[Dict] = None) -> str:
        """
        Format BEST and NEAREST timing windows for marriage timing.
        """
        # Check for no timing issues - positive indicator
        if additional_data and additional_data.get('no_compatibility_timing_issues'):
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("✅ COMPATIBILITY TIMING ASSESSMENT: FAVORABLE")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⭐ POSITIVE FINDING: No specific challenging periods identified")
            lines.append("")
            lines.append("This indicates:")
            lines.append("  • No major timing obstacles for marriage")
            lines.append("  • Charts are favorably aligned for union")
            lines.append("  • Marriage can proceed at couple's convenience")
            lines.append("")
            lines.append("⚠️ INSTRUCTION: Emphasize this POSITIVE finding!")
            lines.append("═══════════════════════════════════════════════════════")
            return "\n".join(lines)
        
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return ""
        
        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            
            if not best and not nearest:
                return ""
            
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⭐ MARRIAGE TIMING WINDOWS (Use These Dates!)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Two timing options are provided below.")
            lines.append("ALWAYS mention BOTH in your analysis.")
            lines.append("")
            
            # BEST WINDOW
            if best:
                lines.append("🏆 BEST MARRIAGE WINDOW (Highest Score):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                if best.get('age_at_start'):
                    lines.append(f"  Age: {best.get('age_at_start', 'N/A')} years")
                lines.append("")
                lines.append("  Why this is BEST:")
                lines.append("    - Strongest marriage-favorable planetary alignment")
                if best.get('score_maha'):
                    lines.append(f"    - Maha Dasha score: {best.get('score_maha', 0)}/10")
                if best.get('score_antara'):
                    lines.append(f"    - Antara Dasha score: {best.get('score_antara', 0)}/10")
                lines.append("")
            
            # NEAREST WINDOW
            if nearest:
                lines.append("⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                if nearest.get('age_at_start'):
                    lines.append(f"  Age: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")
                
                if best and (best.get('dasha') == nearest.get('dasha')):
                    lines.append("  ✅ LUCKY! Best and Nearest windows are THE SAME!")
                lines.append("")
            
            # Alternative windows
            if len(all_windows) > 1:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Top 5):")
                lines.append("-" * 60)
                for i, window in enumerate(all_windows[:5], 1):
                    marker = "🏆" if window == best else "⏰" if window == nearest else "○"
                    lines.append(f"  {marker} {i}. {window.get('dasha', 'N/A')}")
                    lines.append(f"     {window.get('start', 'N/A')} to {window.get('end', 'N/A')}")
                    lines.append(f"     Score: {window.get('final_score', 0):.1f}/100")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS FOR TIMING ANALYSIS:")
            lines.append("- MUST mention BOTH windows")
            lines.append("- Explain WHY each window is favorable")
            lines.append("- Use exact dates provided above")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format House Lords for Both Persons
    # ------------------------------------------------------------------
    def _format_house_lords_both(self, house_lords_data: Dict) -> str:
        """Format house lord information for BOTH persons"""
        if not house_lords_data:
            return ""
        
        person1_lords = house_lords_data.get("person1", {})
        person2_lords = house_lords_data.get("person2", {})
        
        if not person1_lords and not person2_lords:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (BOTH CHARTS)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        # Person 1
        if person1_lords:
            lines.append("👤 PERSON 1 - HOUSE LORDS:")
            lines.append("-" * 40)
            for house_num in sorted(person1_lords.keys()):
                info = person1_lords[house_num]
                strength = info.get("lord_strength_score", 50)
                dignity = info.get("lord_dignity", "Unknown")
                lord = info.get("lord", "Unknown")
                
                if strength >= 70:
                    marker = "✅"
                elif strength >= 40:
                    marker = "○"
                else:
                    marker = "⚠️"
                
                lines.append(f"  {marker} House {house_num}: {lord} ({dignity}, {strength}/100)")
            lines.append("")
        
        # Person 2
        if person2_lords:
            lines.append("👤 PERSON 2 - HOUSE LORDS:")
            lines.append("-" * 40)
            for house_num in sorted(person2_lords.keys()):
                info = person2_lords[house_num]
                strength = info.get("lord_strength_score", 50)
                dignity = info.get("lord_dignity", "Unknown")
                lord = info.get("lord", "Unknown")
                
                if strength >= 70:
                    marker = "✅"
                elif strength >= 40:
                    marker = "○"
                else:
                    marker = "⚠️"
                
                lines.append(f"  {marker} House {house_num}: {lord} ({dignity}, {strength}/100)")
            lines.append("")
        
        # Comparison
        if person1_lords and person2_lords:
            lines.append("📊 HOUSE LORDS COMPARISON:")
            lines.append("-" * 40)
            
            # Compare 7th lords
            p1_7th = person1_lords.get(7, {})
            p2_7th = person2_lords.get(7, {})
            
            if p1_7th and p2_7th:
                p1_strength = p1_7th.get("lord_strength_score", 50)
                p2_strength = p2_7th.get("lord_strength_score", 50)
                avg = (p1_strength + p2_strength) / 2
                
                if avg >= 70:
                    lines.append(f"  ✅ 7th Lords: Both strong (avg: {avg:.0f}/100) → Stable partnership")
                elif avg >= 50:
                    lines.append(f"  ○ 7th Lords: Moderate (avg: {avg:.0f}/100) → Workable")
                else:
                    lines.append(f"  ⚠️ 7th Lords: Need attention (avg: {avg:.0f}/100)")
            
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Current Dasha for Both Persons
    # ------------------------------------------------------------------
    def _format_current_dasha_both(self, dasha_data: Dict) -> str:
        """Format current dasha information for both persons"""
        if not dasha_data:
            return ""
        
        person1_dasha = dasha_data.get("person1", {})
        person2_dasha = dasha_data.get("person2", {})
        
        if not person1_dasha and not person2_dasha:
            return ""
        
        lines = [
            "═══════════════════════════════════════════════════════",
            "CURRENT DASHA PERIODS (BOTH PERSONS)",
            "═══════════════════════════════════════════════════════",
            "",
            "⚠️ IMPORTANT: These are ACTUAL current dashas.",
            "Use for analyzing present compatibility dynamics.",
            ""
        ]
        
        dasha_mapping = {
            'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
            'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
            'Ve': 'Venus', 'Ra': 'Rahu', 'Ke': 'Ketu'
        }
        
        def parse_dasha(name):
            if not name:
                return "N/A"
            parts = name.split('>') if '>' in name else name.split('-') if '-' in name else [name]
            return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts])
        
        if person1_dasha:
            dasha_name = person1_dasha.get('dasha_name', '')
            date_range = person1_dasha.get('date_range', {})
            lines.append(f"👤 PERSON 1:")
            lines.append(f"   Current: {parse_dasha(dasha_name)}")
            lines.append(f"   Period: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}")
            lines.append("")
        
        if person2_dasha:
            dasha_name = person2_dasha.get('dasha_name', '')
            date_range = person2_dasha.get('date_range', {})
            lines.append(f"👤 PERSON 2:")
            lines.append(f"   Current: {parse_dasha(dasha_name)}")
            lines.append(f"   Period: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}")
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions
    # ------------------------------------------------------------------
    def _get_analysis_instructions(self, kp_available: bool, has_timing: bool = False) -> str:
        """Generate analysis instructions based on KP availability."""
        if kp_available:
            if has_timing:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM + TIMING**

**FOLLOW THIS ORDER:**

1. **House Lords Analysis** (50% weight):
   - Compare 7th house lords of BOTH charts
   - Strength, dignity, placement
   - Overall stability assessment

2. **KP Compatibility** (30% weight):
   - 7th CSL comparison for both persons
   - Are they friendly planets?
   - Significations check

3. **Timing Windows** (CRITICAL for this question):
   ⚠️ MUST analyze BOTH timing windows provided:
   
   A. BEST WINDOW: When + Why favorable
   B. NEAREST WINDOW: Soonest opportunity
   
4. **Synthesize** all findings with specific dates
"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER:**

1. **House Lords Analysis** (50% weight)
2. **KP Compatibility** (30% weight)
3. **Dasha Analysis** (20% weight)
4. **Synthesize** all findings
"""
        else:
            return """
**ANALYSIS APPROACH: VEDIC SYSTEM (KP Not Available)**

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (80% weight)
2. **Dasha Timing** (20% weight)
3. **Final Verdict**
"""

    # ------------------------------------------------------------------
    # MAIN PROMPT BUILDER
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
        """Build the compatibility analysis prompt"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        
        language_instruction = self.get_language_instruction(language)
        
        # Get compatibility data
        compatibility_data = kwargs.get("compatibility_data", {})
        additional_data = kwargs.get("additional_data", {})
        
        # Check if this is a timing question
        is_timing_question = (
            meta.query_type == QueryType.TIMING or
            "timing" in question.lower() or
            "when" in question.lower() or
            "best period" in question.lower()
        )
        
        # Extract enhanced data from compatibility_data
        house_lords_data = compatibility_data.get("compatibility_house_lords", {})
        timing_windows_data = compatibility_data.get("compatibility_timing_windows", {})
        
        # Check for no timing issues (positive)
        no_timing_issues = compatibility_data.get("no_compatibility_timing_issues", False)
        if no_timing_issues:
            additional_data["no_compatibility_timing_issues"] = True
        
        has_timing = timing_windows_data.get('has_timing', False)
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, compatibility_data)

        # ✅ NEW: Format KP marriage promise for BOTH persons (timing questions only)
        kp_promise_formatted = ""
        kp_promise_available = False
        if is_timing_question:
            kp_promise_formatted, kp_promise_available = self._format_kp_marriage_promise_both(compatibility_data)
    
        
        # Format house lords for both
        lords_formatted = self._format_house_lords_both(house_lords_data)
        
        # Format timing windows
        timing_formatted = self._format_timing_windows_from_data(timing_windows_data, additional_data)
        
        # Format dasha for both
        dasha_data = kwargs.get("current_dasha_both", {})
        dasha_formatted = self._format_current_dasha_both(dasha_data)
        
        # Get analysis instructions
        analysis_instructions = self._get_analysis_instructions(kp_available, has_timing or is_timing_question)
        
        # Build compatibility scores block
        compatibility_block = ""
        if compatibility_data:
            overall = compatibility_data.get("overall_score", "N/A")
            detailed = compatibility_data.get("detailed_scores", {})
            manglik = compatibility_data.get("manglik_status", {})
            
            compatibility_block = f"""
═══════════════════════════════════════════════════════
COMPATIBILITY SCORES (Use These in Your Analysis!)
═══════════════════════════════════════════════════════

Overall Score: {overall}/100

BREAKDOWN:
- Moon (Emotional): {detailed.get('moon_compatibility', {}).get('score', 'N/A')}/{detailed.get('moon_compatibility', {}).get('max', 20)}
- Venus (Romantic): {detailed.get('venus_compatibility', {}).get('score', 'N/A')}/{detailed.get('venus_compatibility', {}).get('max', 15)}
- Sun-Moon Connection: {detailed.get('sun_moon_connection', {}).get('score', 'N/A')}/{detailed.get('sun_moon_connection', {}).get('max', 15)}
- Mars/Manglik: {detailed.get('mars_compatibility', {}).get('score', 'N/A')}/{detailed.get('mars_compatibility', {}).get('max', 10)}
- Jupiter (Growth): {detailed.get('jupiter_compatibility', {}).get('score', 'N/A')}/{detailed.get('jupiter_compatibility', {}).get('max', 10)}
- KP Compatibility: {detailed.get('kp_compatibility', {}).get('score', 'N/A')}/{detailed.get('kp_compatibility', {}).get('max', 15)}
- House Lords: {detailed.get('house_lords_compatibility', {}).get('score', 'N/A')}/{detailed.get('house_lords_compatibility', {}).get('max', 15)}

MANGLIK STATUS:
- Person 1: {'Yes - Manglik' if manglik.get('person1') else 'No'}
- Person 2: {'Yes - Manglik' if manglik.get('person2') else 'No'}
{'✅ Both Manglik - Doshas cancel!' if manglik.get('person1') and manglik.get('person2') else ''}
{'✅ Neither Manglik - No concerns' if not manglik.get('person1') and not manglik.get('person2') else ''}
{'⚠️ One Manglik - Remedies advised' if (manglik.get('person1') or manglik.get('person2')) and not (manglik.get('person1') and manglik.get('person2')) else ''}

SUMMARY: {compatibility_data.get('detailed_analysis', '')}

COMPATIBILITY NOTES:
{chr(10).join('• ' + note for note in compatibility_data.get('notes', []))}

═══════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marriage Compatibility
- Analysis Type: Two-Person Synastry
- Query Type: {meta.query_type.value}
- Event Polarity: {meta.polarity.value}
- Interpretation Goal: {meta.goal.value}
- CURRENT DATE: {today_str}
- KP Analysis Available: {'YES' if kp_available or kp_promise_available else 'NO'}
- Timing Windows Available: {'YES' if has_timing else 'NO'}

USER QUESTION:
"{question}"

{compatibility_block}

{timing_formatted}

{kp_promise_formatted}

{kp_formatted}

{lords_formatted}

{dasha_formatted}

{'ADDITIONAL TECHNICAL POINTS:' if raw_points else ''}
{raw_points}

{analysis_instructions}

TONE GUIDELINES:
- Balanced and objective
- Never doom a relationship based on scores
- Emphasize potential and growth
- Be practical about challenges
- Scores >= 65 = Good compatibility
- Scores 50-65 = Moderate, workable
- Scores < 50 = Challenges, but NOT incompatible

{self.get_output_format(kp_available, has_timing or is_timing_question, no_timing_issues)}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, no_timing_issues: bool = False) -> str:
        """Get output format based on analysis type"""
        
        timing_section = ""
        if no_timing_issues:
            timing_section = """
TIMING_ANALYSIS:
✅ FAVORABLE - No specific challenging periods identified

This indicates:
- No major timing obstacles for marriage
- Charts are favorably aligned
- Marriage can proceed at couple's convenience

**MUST emphasize this POSITIVE finding!**
"""
        elif has_timing:
            timing_section = """
TIMING_RECOMMENDATION:
⚠️ CRITICAL - MUST include BOTH timing options:

**BEST WINDOW:**
- Period: <exact dates from timing data>
- Dasha: <pratyantar dasha name>
- Why favorable: <planetary alignment details>

**NEAREST WINDOW:**
- Period: <exact dates from timing data>
- Why favorable: <score explanation>

**RECOMMENDATION:**
- Which window to choose and why
"""

        if kp_available:
            return f"""
OUTPUT FORMAT (MUST FOLLOW EXACTLY):

GENERAL_ANSWER:
<3-5 lines summarizing overall compatibility. Include score interpretation. Be encouraging while realistic about any challenges. Start with the compatibility level (Excellent/Good/Moderate/Challenging).>

ASTROLOGICAL_ANALYSIS:
<Comprehensive analysis covering:

**A. HOUSE LORDS COMPATIBILITY (50% weight):**
- 7th house lords comparison for BOTH charts
- Strength and dignity assessment
- Overall partnership potential

**B. KP COMPATIBILITY (30% weight):**
- 7th CSL comparison for both persons
- Are they friendly planets?
- Signification analysis

**C. PLANETARY COMPATIBILITY:**

EMOTIONAL HARMONY (Moon Signs):
<Analysis of emotional connection, understanding, intuition>

ROMANTIC COMPATIBILITY (Venus Signs):
<Analysis of love expression, attraction, romantic needs>

ATTRACTION & CONNECTION (Sun-Moon):
<Analysis of natural attraction, ego balance, mutual respect>

MANGLIK ASSESSMENT:
<Status of both partners, cancellation factors, compatibility impact>

**D. DASHA TIMING (20% weight):**
- Current dasha impact on relationship
- Upcoming favorable/challenging periods
>
{timing_section}
SUMMARY:
<2-3 lines with key takeaway and most important recommendation>

REMEDIES_ASTROLOGICAL:
- <Remedy if Manglik dosha present>
- <Remedy for any planetary conflicts>
- <General relationship harmony remedy>

REMEDIES_GENERAL:
- <Communication recommendation>
- <Relationship building activity>
- <Growth opportunity for the couple>
"""
        else:
            return f"""
OUTPUT FORMAT (MUST FOLLOW EXACTLY):

GENERAL_ANSWER:
<3-5 lines summarizing overall compatibility. Be encouraging while realistic.>

ASTROLOGICAL_ANALYSIS:
<Comprehensive analysis covering:

**A. VEDIC HOUSE LORD ANALYSIS (80% weight):**
- Detailed comparison of both charts
- 7th house lords strength and placement
- Overall partnership assessment

**B. PLANETARY COMPATIBILITY:**

EMOTIONAL HARMONY (Moon Signs):
<Analysis>

ROMANTIC COMPATIBILITY (Venus Signs):
<Analysis>

MANGLIK ASSESSMENT:
<Status and impact>

**C. DASHA TIMING (20% weight):**
- Current period analysis
- Upcoming periods
>
{timing_section}
SUMMARY:
<Key takeaway and recommendation>

REMEDIES_ASTROLOGICAL:
- <Relevant remedies>

REMEDIES_GENERAL:
- <Practical suggestions>
"""
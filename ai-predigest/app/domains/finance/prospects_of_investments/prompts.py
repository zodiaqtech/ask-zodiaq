"""
Prospects Of Investments – Enhanced Prompts v7.0

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
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class ProspectsOfInvestmentsPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Finance → Prospects Of Investments
    """

    domain = "Finance"
    subtopic = "Prospects Of Investments"

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v7.0 WITH TIMING EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing ACTIONABLE financial and investment guidance.

════════════════════════════════════
CORE KP PRINCIPLES (STRICTLY FOLLOW)
════════════════════════════════════

KP hierarchy of result (MOST IMPORTANT RULE):

Sub Lord      → FINAL PROMISE (event happens or not)
Star Lord     → RESULT TYPE (what happens)
Planet Nature → FLAVOR ONLY (how it happens)

⚠️ ALWAYS prioritize:
Sub > Star > Planet nature

Planet benefic/malefic status NEVER overrides significations.

Example:
If Venus (benefic) signifies 6, 8, 12 → result is loss/expense.
If Saturn (malefic) signifies 2, 10, 11 → result is gains.
Significations ALWAYS win.

════════════════════════════════════
CORRECT KP ANALYSIS CHAIN (MANDATORY)
════════════════════════════════════

For every judgement, explicitly follow:

Cusp → Sub Lord → Star Lord → Houses Signified → Verdict

Always explain like:

"CSL [Planet] is in [Nakshatra]. Star lord [Planet2] signifies houses [X,Y,Z]. 
Therefore RESULT: [prediction based ONLY on those houses]."

Never jump directly from planet nature.

════════════════════════════════════
HOUSE SIGNIFICATION RULE
════════════════════════════════════

When judging a planet, consider:

• Houses occupied
• Houses owned
• Houses of its star lord
• Houses of its sub lord
• Conjunctions

Weight priority:
Sub > Star > Occupation > Ownership

════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════

DO NOT invent data.

• Do NOT mention aspects unless explicitly provided
• Do NOT assume yogas not present in input
• Use ONLY supplied positions, houses, dashas, KP significations
• Conjunctions are safe (same house)

If aspect data is missing → ignore aspects completely.

════════════════════════════════════
TIMING RULES (DASHA + KP)
════════════════════════════════════

When giving timing:

Explain WHY each level supports:

• Maha Dasha → overall promise
• Antara → activates event
• Pratyantar → final trigger

Only recommend periods that align with KP significations.
Never contradict KP timing.

Show reasoning, not just dates.

════════════════════════════════════
VEDIC SUPPORT ROLE (SECONDARY)
════════════════════════════════════

Use Vedic ONLY to support KP:

• Lagna lord → personality & risk behaviour
• House lords → capacity/obstacles
• Dignity → strength/weakness

KP decides the event.
Vedic explains ease/difficulty.

════════════════════════════════════
MODERN FINANCIAL MAPPING (TENDENCIES ONLY)
════════════════════════════════════

Map planets to modern instruments (modify using KP strength):

Mercury → systematic investing, mutual/index funds
Venus → gold, luxury, real estate
Jupiter → long-term growth, education funds
Mars → land, construction, active assets
Saturn → FD, bonds, pensions, conservative
Rahu → international/tech/high-risk
Moon → liquid funds (warn emotional trading)

These are tendencies, NOT guarantees.

Final decision must come from KP significations.

════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════

Always convert astrology into decisions:

❌ "5th house weak"
✅ "Avoid day trading"

❌ "2nd strong"
✅ "Start SIP ₹10K/month"

Provide:
• allocations
• percentages
• timeframes
• clear do/don’t

Avoid abstract theory.

════════════════════════════════════
ANALYSIS WEIGHTING (ENGINE LOGIC)
════════════════════════════════════

KP Significations → 50%
Vedic Structure → 30%
Dasha Timing → 15%
Other factors → 5%

KP conclusion ALWAYS leads.

Goal: Provide precise, practical, financially useful guidance — not generic astrology descriptions.
"""

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows (NEW!)
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows for LLM.
        
        Args:
            timing_windows_data: Dict with best_window, nearest_window, all_favorable
            
        Returns:
            Formatted string for prompt inclusion
        """
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return ""
        
        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            
            if not best and not nearest:
                return ""
            
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⭐ TIMING WINDOWS ANALYSIS (Use These Dates!)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Two timing options are provided below.")
            lines.append("ALWAYS mention BOTH in your analysis and explain the trade-off.")
            lines.append("")
            
            # BEST WINDOW
            if best:
                lines.append("🏆 BEST WINDOW (Highest Astrological Score):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                lines.append(f"  Age: {best.get('age_at_start', 'N/A')} years")
                lines.append("")
                lines.append("  Why this is BEST:")
                lines.append(f"    - Maha Dasha score: {best.get('score_maha', 0)}/10")
                lines.append(f"    - Antara Dasha score: {best.get('score_antara', 0)}/10")
                lines.append(f"    - Pratyantar Dasha score: {best.get('score_paryantar', 0)}/10")
                lines.append(f"    - Transit support: {best.get('transit_score', 0):.1f}%")
                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest alignment")
                lines.append("")
            
            # NEAREST WINDOW
            if nearest:
                lines.append("⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):")
                lines.append("-" * 60)
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                lines.append(f"  Age: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")
                lines.append("  Why this is NEAREST:")
                lines.append("    - Earliest favorable window (score >= 50)")
                lines.append("    - Can act sooner rather than waiting")
                lines.append("")
                
                # Check if best and nearest are the same
                if best and (best.get('dasha') == nearest.get('dasha')):
                    lines.append("  ✅ LUCKY! Best and Nearest windows are THE SAME!")
                    lines.append("     You get both optimal timing AND early opportunity!")
                else:
                    lines.append("  Trade-off: Sooner opportunity, but not the absolute best alignment")
                lines.append("")
            
            # Alternative windows
            if len(all_windows) > 1:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Top 5 for reference):")
                lines.append("-" * 60)
                for i, window in enumerate(all_windows[:5], 1):
                    marker = "🏆" if window == best else "⏰" if window == nearest else "○"
                    lines.append(f"  {marker} {i}. {window.get('dasha', 'N/A')}")
                    lines.append(f"     {window.get('start', 'N/A')} to {window.get('end', 'N/A')}")
                    lines.append(f"     Score: {window.get('final_score', 0):.1f}/100")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS FOR TIMING ANALYSIS:")
            lines.append("- MUST mention BOTH best and nearest windows")
            lines.append("- Explain WHY each window is favorable")
            lines.append("- Let user choose: Wait for best OR Act sooner")
            lines.append("- Use exact dates provided above")
            lines.append("- If best = nearest, emphasize this is ideal timing")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""


    def _format_lagna_lord(self, house_lords_info: Dict) -> str:
        """
        Format lagna lord (house 1 lord) prominently to prevent hallucination.
        
        House 1 lord IS the lagna lord - just format it specially.
        """
        if not house_lords_info or 1 not in house_lords_info:
            return """
═══════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════

⚠️ CRITICAL: Lagna information not provided.
Do NOT guess or invent lagna sign.
Do NOT mention lagna in your analysis.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════
"""
        
        info = house_lords_info[1]
        lord = info['lord']
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) INFORMATION")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {info.get('house_sign', 'N/A')}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {info['lord_in_house']}, {info['lord_in_sign']}")
        lines.append(f"Dignity: {info['lord_dignity']}")
        lines.append(f"Strength: {info['lord_strength_score']}/100")
        lines.append("")
        
        conditions = []
        if info.get('lord_degree'):
            conditions.append(f"Degree: {info['lord_degree']:.2f}°")
        if info.get('lord_is_combust'):
            conditions.append("⚠️ COMBUST (weakened)")
        if info.get('lord_is_retrograde'):
            conditions.append("🔄 RETROGRADE")
        
        if conditions:
            lines.append(f"Condition: {' | '.join(conditions)}")
            lines.append("")
        
        # Personality interpretation based on lagna lord
        personality_map = {
            "Sun": "Confident, leadership-oriented, ego-driven in finances",
            "Moon": "Emotional, fluctuating decisions, intuitive with money",
            "Mars": "Aggressive, risk-taker, impulsive investor",
            "Mercury": "Analytical, calculated, detail-oriented planner",
            "Jupiter": "Optimistic, expansive, long-term thinker",
            "Venus": "Luxury-seeking, comfort-focused, aesthetic investor",
            "Saturn": "Conservative, disciplined, patient wealth builder",
            "Rahu": "Unconventional, foreign/tech affinity, high-risk appetite",
            "Ketu": "Detached, spiritual, minimal material focus"
        }
        
        personality = personality_map.get(lord, "Unique financial approach")
        lines.append(f"Financial Personality: {personality}")
        lines.append("")
        
        lines.append("⚠️ CRITICAL RULES:")
        lines.append("• This is the ONLY lagna (ascendant) for this person")
        lines.append("• Do NOT confuse lagna sign with Moon sign (rashi/janma rashi)")
        lines.append("• Do NOT mention multiple lagnas - there is only ONE")
        lines.append("• Lagna lord shows fundamental approach to wealth")
        lines.append("")
        lines.append("❌ WRONG: 'लग्न राशि: कन्या (वृश्चिक लग्न)' (contradictory!)")
        lines.append(f"✅ CORRECT: 'लग्न राशि: {info.get('house_sign', 'N/A')}' (only one lagna)")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)





    def _format_investment_matrix(self, matrix: Dict) -> str:
        """Format investment suitability matrix for LLM"""
        if not matrix:
            return ""
        
        lines = ["**B. MODERN INVESTMENT MAPPING (From KP Significations):**", ""]
        lines.append("| Investment Type | Suitability | KP Reasoning |")
        lines.append("|----------------|-------------|--------------|")
        
        for investment_type, details in matrix.items():
            rating = details.get("rating", "UNKNOWN")
            reasoning = details.get("kp_reasoning", "")
            
            # Add emoji for clarity
            if rating == "HIGH":
                marker = "✅"
            elif rating == "MODERATE":
                marker = "⚖️"
            elif rating in ["LOW", "VERY LOW"]:
                marker = "⚠️"
            elif rating == "AVOID":
                marker = "❌"
            else:
                marker = "○"
            
            lines.append(f"| {marker} **{investment_type}** | {rating} | {reasoning} |")
        
        lines.append("")
        return "\n".join(lines)



    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific analysis points DETERMINISTICALLY.
        
        ENHANCED v3.0: Emphasizes CSL → Star Lord → Significations chain
        """
        # Extract from structured KP data
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_investments_analysis", {})
        
        # If we have structured KP data with significations, use it!
        if kp_structured and kp_structured.get("has_kp_data"):
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⭐ KP SYSTEM ANALYSIS (Cusp Sub Lords → Star Lords → Significations)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL KP METHODOLOGY:")
            lines.append("We analyze CSL → Nakshatra (Star) → Star Lord → Significations → Result")
            lines.append("Planet nature = FLAVOR, Significations = RESULT. Result wins.")
            lines.append("")
            
            # Get methodology note
            methodology = kp_structured.get("methodology", "")
            if methodology:
                lines.append(f"Methodology: {methodology}")
                lines.append("")
            
            # Format CSL details with full chain
            csl_details = kp_structured.get("csl_details", {})
            if csl_details:
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS:")
                lines.append("")
                
                for house_num in sorted(csl_details.keys()):
                    csl_info = csl_details[house_num]
                    
                    house_meaning = csl_info.get("house_meaning", "Investment")
                    csl = csl_info.get("csl", "Unknown")
                    csl_flavor = csl_info.get("csl_flavor", "")
                    nakshatra = csl_info.get("nakshatra", "")
                    star_lord = csl_info.get("star_lord", "")
                    sig_houses = csl_info.get("signified_houses", [])
                    wealth_conn = csl_info.get("wealth_connection", 0)
                    loss_conn = csl_info.get("loss_connection", 0)
                    verdict = csl_info.get("verdict", "NEUTRAL")
                    interpretation = csl_info.get("interpretation", "")
                    chain = csl_info.get("chain", "")
                    
                    # Verdict marker
                    if verdict in ["STRONG", "EXCELLENT", "FAVORABLE", "PROMISING"]:
                        marker = "✅"
                    elif verdict in ["WEAK", "RISKY", "POOR", "CHALLENGING", "DIFFICULT"]:
                        marker = "⚠️"
                    else:
                        marker = "○"
                    
                    lines.append(f"{marker} House {house_num} ({house_meaning}):")
                    lines.append(f"   Chain: {chain}")
                    lines.append(f"   CSL: {csl} ({csl_flavor})")
                    if nakshatra:
                        lines.append(f"   Nakshatra: {nakshatra}")
                    if star_lord:
                        lines.append(f"   Star Lord: {star_lord}")
                    if sig_houses:
                        lines.append(f"   Star Lord Signifies: Houses {sig_houses}")
                        lines.append(f"   Wealth Connection: {wealth_conn}/3 houses (2, 10, 11)")
                        lines.append(f"   Loss Connection: {loss_conn}/3 houses (6, 8, 12)")
                    lines.append(f"   Verdict: {verdict}")
                    
                    if interpretation:
                        # Wrap interpretation for readability
                        lines.append(f"   Why: {interpretation}")
                    
                    lines.append("")

            # Get investment matrix from additional_data
            investment_matrix = additional_data.get("investment_suitability_matrix", {}) if additional_data else {}
            if investment_matrix:
                matrix_text = self._format_investment_matrix(investment_matrix)
                lines.append(matrix_text)
                lines.append("")
                
            # Overall verdict with reasoning
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            if overall != "UNKNOWN":
                lines.append(f"📊 OVERALL KP VERDICT (Based on Significations): {overall}")
                lines.append("")
                
                # Provide interpretation based on verdict
                if overall == "EXCELLENT_FOR_INVESTMENT":
                    lines.append("   ✅ Star lord significations across 2-11 houses show excellent")
                    lines.append("      wealth accumulation capacity through systematic investing")
                elif overall == "AVOID_SPECULATION":
                    lines.append("   ⚠️ Star lord significations in 5th/8th houses show loss patterns")
                    lines.append("      High-risk speculation dangerous, prefer safe investments")
                elif overall == "SUITABLE_FOR_MODERATE_RISK":
                    lines.append("   ⚖️ Mixed significations support balanced portfolio")
                    lines.append("      Both long-term investment and calculated risks possible")
                elif overall == "WEAK_RETURNS":
                    lines.append("   ⚠️ 11th house star lord significations show gain challenges")
                    lines.append("      Investment returns will be limited or drain away")
                else:
                    lines.append("   ○ Moderate investment potential with mixed signification patterns")
                
                lines.append("")

            
            
            # Key findings
            key_findings = kp_structured.get("key_findings", [])
            if key_findings:
                lines.append("🔑 KEY KP FINDINGS (Signification-Based):")
                for finding in key_findings[:6]:  # Limit to top 6
                    lines.append(f"   • {finding}")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("⚠️ INSTRUCTIONS FOR YOUR KP INTERPRETATION:")
            lines.append("")
            lines.append("CRITICAL RULES:")
            lines.append("  1. ALWAYS state the full chain: CSL → Nakshatra → Star Lord → Significations")
            lines.append("  2. Base verdict on SIGNIFICATIONS, not planet nature")
            lines.append("  3. If benefic CSL has malefic significations → Result is MALEFIC")
            lines.append("  4. If malefic CSL has benefic significations → Result is BENEFIC")
            lines.append("  5. Explain WHY significations lead to the verdict")
            lines.append("")
            lines.append("VERDICT Meanings:")
            lines.append("  • STRONG/EXCELLENT: Significations support wealth (2-10-11 connection)")
            lines.append("  • WEAK/POOR: Significations show drains (6-8-12 connection)")
            lines.append("  • RISKY/CHALLENGING: Significations warn of losses")
            lines.append("  • MODERATE: Mixed significations, neither strong nor weak")
            lines.append("")
            lines.append("YOU MUST:")
            lines.append("  1. Quote the full chain for each house analyzed")
            lines.append("  2. Explain what significations mean for that house")
            lines.append("  3. Map significations to modern investment types")
            lines.append("  4. Give this PRIMARY weight (50%) in your final recommendation")
            lines.append("  5. If KP and Vedic agree → Strong conclusion")
            lines.append("  6. If KP and Vedic differ → KP (significations) takes priority")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines), True
        
        # Fallback to basic text-based extraction (less reliable)
        # ... (keep existing fallback code)
        # ═══════════════════════════════════════════════════════════════
        # FALLBACK: Extract from technical_points (less reliable)
        # ═══════════════════════════════════════════════════════════════
        if not technical_points:
            return "", False
        
        kp_keywords = [
            "kp:", "cusp", "sub-lord", "sub lord", "csl",
            "signif", "connects to", "connect", "promise",
            "-cusp", "ruling planet", "kp"
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
        lines.append("⚠️ CRITICAL: Give PRIMARY weight (50%) to KP findings below.")
        lines.append("")
        
        for point in kp_points:
            # Remove "KP:" prefix if present
            clean_point = point.replace("KP:", "").strip()
            
            if not clean_point.startswith(("•", "-", "✓", "❌", "⚠", "❓", "⭐")):
                lines.append(f"  • {clean_point}")
            else:
                lines.append(f"  {clean_point}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines), True

    # ------------------------------------------------------------------
    # HELPER: Format House Lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Investment Houses)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        for house_num in sorted(house_lords_info.keys()):
            info = house_lords_info[house_num]
            
            marker = "⭐ PRIMARY" if info["priority"] == "primary" else "○ SECONDARY"
            
            lines.append(f"{marker} - HOUSE {house_num}")
            lines.append(f"  Sign: {info.get('house_sign', 'N/A')}")
            lines.append("")
            
            lines.append(f"  Lord: {info['lord']}")
            lines.append(f"  Placed in: House {info['lord_in_house']}, {info['lord_in_sign']}")
            lines.append(f"  Dignity: {info['lord_dignity']}")
            lines.append(f"  Overall Strength: {info['lord_strength_score']}/100")
            
            conditions = []
            if info['lord_degree']:
                conditions.append(f"Degree: {info['lord_degree']:.2f}°")
            if info['lord_is_combust']:
                conditions.append("⚠️ COMBUST (weakened)")
            if info['lord_is_retrograde']:
                conditions.append("🔄 RETROGRADE")
            
            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")
            
            if info['planets_in_house']:
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")
            
            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports financial growth")
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
        lines.append("PLANETARY ASPECTS ON INVESTMENT HOUSES")
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
                    lines.append(f"     → Positive influence, support")
                
                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")
                    lines.append(f"     → Challenges, need caution")
                
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
                f"Current Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT: This is the ACTUAL current dasha running now.",
                "Use for analyzing present financial circumstances.",
                "For FUTURE planning, refer to UPCOMING DASHA PERIODS below.",
                "═══════════════════════════════════════════════════════"
            ]
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

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
            lines.append("COMPREHENSIVE DASHA TIMELINE (2 Years Past → 10 Years Future)")
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
            
            if current:
                lines.append("🔴 CURRENT DASHA PERIODS (RUNNING NOW):")
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
                lines.append("⏮️  RECENT PAST DASHAS (Last 2 Years - for context):")
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
                lines.append("⏭️  UPCOMING DASHA PERIODS (Next 10 Years - for planning):")
                lines.append("-" * 60)
                lines.append("Use these periods for investment/asset planning:")
                lines.append("")
                
                for i, d in enumerate(future[:30], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    
                    marker = "⭐" if i <= 5 else "○" if i <= 10 else " "
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {start} to {end}")
            
            lines.append("")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS FOR DASHA ANALYSIS:")
            lines.append("- CURRENT: Use for present financial circumstances")
            lines.append("- RECENT PAST: Context for recent financial events")
            lines.append("- UPCOMING: Make future investment recommendations")
            lines.append("- Venus/Jupiter periods favorable for wealth")
            lines.append("- Mercury periods good for trading")
            lines.append("- Saturn periods require patience and discipline")
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
        
        Args:
            kp_available: Whether KP analysis is present
            question_type: Type of question (investment, property, income, etc.)
            has_timing: Whether timing windows are provided
        """
        if kp_available:
            # KP + Vedic combined approach
            if question_type == "property" and has_timing:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM + TIMING**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - What does the 4th cusp sub lord signify? (property/vehicle)
   - What does the 11th cusp sub lord signify? (gains/fulfillment)
   - Does 4th CSL connect to 2-11 for asset acquisition?
   - KP verdict: Clear promise for property/vehicle/assets?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 4th house lord strength (property capacity)
   - 2nd house lord strength (affordability)
   - 11th house lord strength (gains to buy)

3. **TIMING ANALYSIS** (15% weight - CRITICAL FOR THIS QUESTION):
   ⚠️ MUST analyze BOTH timing windows provided:
   
   A. BEST WINDOW (Highest score):
      - When: Exact dates from timing data
      - Why favorable: Dasha lords + transits
      - Trade-off: May be further away
   
   B. NEAREST WINDOW (Earliest favorable):
      - When: Exact dates from timing data
      - Why favorable: Still good score, sooner
      - Trade-off: Not absolute best
   
   C. USER CHOICE:
      - Wait for best alignment (patience + optimal results)
      - Act sooner (urgency + good enough results)
   
   ⚠️ If best = nearest: Emphasize this is IDEAL timing!

4. **Synthesize** (5% weight):
   - Combine KP promise + Vedic capacity + Timing recommendation
   - Give clear timing guidance with specific dates
"""
            elif question_type == "investment":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - What does the 5th cusp sub lord signify? (speculation/risk)
   - What does the 2nd cusp sub lord signify? (savings)
   - What does the 11th cusp sub lord signify? (gains)
   - Are there KP connections like 2-5-11 for investment success?
   - KP verdict: Suitable for investment? Trading? Both? Neither?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 5th house lord strength (speculation capacity)
   - 2nd house lord strength (savings capacity)
   - 11th house lord strength (gains potential)
   - 8th house lord (hidden risks)

3. **Include Dasha Timing** (15% weight):
   - Current dasha: Good for investment now?
   - Upcoming favorable periods (Venus/Jupiter for investments, Mercury for trading)

4. **Synthesize** (5% weight):
   - Combine KP + Vedic findings
"""
            elif question_type == "income":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - What does the 2nd cusp sub lord signify? (income)
   - Does it connect to 2-10-11 for income growth?
   - KP promise for income growth?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 2nd house lord strength (income capacity)
   - 10th house lord strength (career income)
   - 11th house lord strength (gains)

3. **Include Dasha Timing** (15% weight):
   - Current dasha impact on income NOW
   - Upcoming favorable periods

4. **Synthesize** (5% weight):
   - Combine KP + Vedic + Dasha
"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight)
2. **ADD Vedic Context** (SECONDARY - 30% weight)
3. **Include Dasha Timing** (15% weight)
4. **Synthesize** (5% weight)
"""
        else:
            # Pure Vedic fallback approach
            if has_timing:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM + TIMING (KP Not Available)**

⚠️ NOTE: No KP Cusp Sub Lord analysis available.
Proceeding with comprehensive Vedic analysis.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 80% weight):
   - Detailed analysis of relevant house lords
   - Their placements, dignity, and condition
   - Strength assessment

2. **TIMING ANALYSIS** (15% weight - CRITICAL):
   ⚠️ MUST analyze BOTH timing windows:
   
   A. BEST WINDOW: When + Why + Trade-off
   B. NEAREST WINDOW: When + Why + Trade-off
   C. USER CHOICE: Wait vs Act sooner
   
   ⚠️ If best = nearest: Ideal timing!

3. **Final Verdict** (5% weight):
   - Clear recommendation with specific dates
"""
            else:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM (KP Not Available)**

⚠️ NOTE: No KP analysis available.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 80% weight)
2. **Dasha Timing** (15% weight)
3. **Final Verdict** (5% weight)
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
        language: str = "Hindi",
        **kwargs
    ) -> str:

        sub_subdomain = kwargs.get("sub_subdomain", "")

        if "Income Growth" in sub_subdomain:
            return self._build_income_growth_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Investment" in sub_subdomain:
            return self._build_investment_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Property" in sub_subdomain:
            return self._build_asset_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Challenge" in sub_subdomain or "Risk" in sub_subdomain:
            return self._build_financial_risk_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_finance_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # PROPERTY/ASSET PROMPT (WITH TIMING!)
    # ------------------------------------------------------------------
    def _build_asset_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"

        # ✅ DEBUG: Check if timing windows are in additional_data
        logger.error(f"🔍 PROMPT DEBUG: additional_data keys: {list(additional_data.keys())}")
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ Get timing windows
        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        logger.error(f"🔍 PROMPT DEBUG: timing_windows_data present: {bool(timing_windows_data)}")
        logger.error(f"🔍 PROMPT DEBUG: has_timing flag: {has_timing}")
    
        if timing_windows_data:
            logger.error(f"🔍 PROMPT DEBUG: best_window present: {bool(timing_windows_data.get('best_window'))}")
            logger.error(f"🔍 PROMPT DEBUG: nearest_window present: {bool(timing_windows_data.get('nearest_window'))}")
    



        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        
        # ✅ Format timing windows
        timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "property", has_timing)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Sub-subdomain: Asset Capacity (Property/Vehicle)
- Query Type: TIMING (When will event occur?)
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}
- Timing Windows Available: {'YES' if has_timing else 'NO'}

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

CRITICAL TIMING INSTRUCTIONS:
{'⚠️ TIMING WINDOWS PROVIDED ABOVE - MUST USE IN YOUR ANSWER!' if has_timing else ''}
{'- Mention BOTH best and nearest windows with exact dates' if has_timing else ''}
{'- Explain why each window is favorable' if has_timing else ''}
{'- Let user choose: wait for best OR act sooner' if has_timing else ''}
{'- If best = nearest, emphasize this is ideal timing' if has_timing else ''}

GUIDELINES:
- Property requires strong 4th house factors
- Vehicles require 4th + 11th connection
- Jewelry/luxury requires 2nd + 11th strength
- {'Use timing windows for SPECIFIC dates!' if has_timing else 'Use dasha timeline for timing'}

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # INVESTMENT PROMPT
    # ------------------------------------------------------------------
    def _build_investment_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)

        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        
        timing_formatted = self._format_timing_windows(timing_windows_data) if has_timing else ""

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "investment", has_timing)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Sub-subdomain: Investment Analysis
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

GUIDELINES:
- Distinguish investing (long-term) vs trading (short-term)
- Highlight risk tolerance based on lagna lord
- Avoid naming specific instruments or markets
- Use dasha periods for timing recommendations

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # INCOME GROWTH PROMPT
    # ------------------------------------------------------------------
    def _build_income_growth_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "income", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Sub-subdomain: Income Growth
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

GUIDELINES:
- Focus on income capacity and stability
- Mention alternative income only if supported
- Reference current dasha for present situation
- Reference upcoming dashas for future growth

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # FINANCIAL CHALLENGES PROMPT
    # ------------------------------------------------------------------
    def _build_financial_risk_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Sub-subdomain: Financial Challenges
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

GUIDELINES:
- Explain obstacles factually
- Avoid permanent negative conclusions
- Emphasize controllable factors
- Use current dasha for present challenges
- Use upcoming dashas for when relief comes

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # REMEDIES PROMPT
    # ------------------------------------------------------------------
    def _build_remedies_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Sub-subdomain: Remedies
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

REMEDY GUIDELINES:

1. **Identify Weak Planets**:
   {'- Weak KP cusp sub lords (if KP available)' if kp_available else ''}
   - Weak Vedic house lords (debilitated/combust/poorly placed)

2. **Current Dasha Lord Remedies**:
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords (3 months before)

3. **Priority**:
   - Primary: Strengthen weak lords affecting income (2nd, 10th, 11th)
   - Secondary: Control malefic lords causing losses (6th, 8th, 12th)

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK PROMPT
    # ------------------------------------------------------------------
    def _build_general_finance_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_investments"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        lagna_formatted = self._format_lagna_lord(house_lords)
        
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Prospects Of Investments
- Query Type: {meta.query_type if meta else 'UNKNOWN'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT - DYNAMIC BASED ON KP AVAILABILITY + TIMING
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False) -> str:
        """
        Generate output format based on KP availability and timing windows.
        
        Args:
            kp_available: Whether KP cusp sub lord analysis is available
            has_timing: Whether timing windows are provided for this question
            
        Returns:
            Formatted string with output format instructions for LLM
        """
        
        # ═══════════════════════════════════════════════════════════
        # DEFINE TIMING SECTION FIRST (to avoid "name not defined" error)
        # ═══════════════════════════════════════════════════════════
        
        if has_timing:
            timing_section = """
    **F. TIMING RECOMMENDATION (CRITICAL - For Timing Questions Only):**

    ⚠️ MANDATORY: MUST include BOTH timing options below.

    **🏆 BEST WINDOW (Highest Astrological Score):**
    - Period: [exact start date] to [exact end date] (from timing data)
    - Dasha: [Maha-Antara-Pratyantar] (exact dasha name from data)
    - Age at start: [age] years
    - Astrological Score: [final_score]/100
    - Why this is BEST:
    * Maha Dasha lord ([planet]): [lordship/significations] → Score [X]/10
    * Antara Dasha lord ([planet]): [reinforcement/complement] → Score [Y]/10
    * Pratyantar Dasha lord ([planet]): [final trigger] → Score [Z]/10
    * Transit support: [transit_score]%
    * Overall: [Explain why this combination is optimal for this event]
    - Trade-off: [e.g., "May be further in future, but strongest planetary alignment"]

    **⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):**
    - Period: [exact start date] to [exact end date] (from timing data)
    - Dasha: [Maha-Antara-Pratyantar] (exact dasha name from data)
    - Age at start: [age] years
    - Astrological Score: [final_score]/100
    - Why this is NEAREST:
    * [Explain why this window comes sooner]
    * [Still has favorable score >= 50]
    * [What makes it acceptable though not optimal]
    - Trade-off: [e.g., "Sooner opportunity but not absolute best alignment"]

    **👤 USER RECOMMENDATION (Help them decide):**
    Choose BEST window if:
    - You can wait for optimal results
    - You want maximum astrological support
    - Long-term stability is priority
    - [Specific reason based on chart]

    Choose NEAREST window if:
    - You have urgent need/opportunity
    - Good enough results acceptable
    - Cannot wait for best timing
    - [Specific reason based on chart]

    ⚠️ Special case: If BEST = NEAREST (same window):
    "🎯 IDEAL TIMING: The best window IS the nearest favorable window! 
    This is perfect - you get both optimal astrological support AND early opportunity.
    Strong recommendation to act during: [dates]"
    """
        else:
            timing_section = ""  # No timing section for non-timing questions
        
        # ═══════════════════════════════════════════════════════════
        # KP AVAILABLE FORMAT
        # ═══════════════════════════════════════════════════════════
        
        if kp_available:
            return f"""
    OUTPUT FORMAT (STRICT):

    **GENERAL_ANSWER:**
    <Write a clear, actionable answer in simple layman's terms. NO astrological jargon.>
    <Example: "आपके लिए दीर्घकालिक निवेश (म्यूचुअल फंड, गोल्ड) अधिक उपयुक्त हैं। शेयर बाजार में डे ट्रेडिंग से बचें।">

    **ASTROLOGICAL_ANALYSIS:**

    ⚠️ CRITICAL: Follow CORRECT KP methodology - CSL → Star Lord → Significations → Result

    **A. KP SYSTEM ANALYSIS (Primary - 50% weight):**

    For EACH cusp analyzed (2nd, 5th, 8th, 10th, 11th), present in this EXACT format:

    **House [N] ([Meaning - e.g., Wealth/Income]):**
    - Cusp Sub Lord (CSL): [Planet name] ([benefic/malefic/neutral] flavor)
    - CSL in Nakshatra: [Nakshatra name]
    - Star Lord: [Planet name]
    - Star Lord Signifies: Houses [X, Y, Z] (from actual data - never guess!)
    - Wealth Connection: [N]/3 (overlap with houses 2, 10, 11)
    - Loss Connection: [N]/3 (overlap with houses 6, 8, 12)
    - **Verdict: [STRONG/WEAK/MODERATE/RISKY/etc]** ← Based on SIGNIFICATIONS only
    - Why: [Explain the full chain - how star lord significations lead to verdict. 
            Mention if significations are missing and verdict is incomplete.]

    **CRITICAL EXAMPLE - DO THIS:**
    "**House 2 (Wealth/Income):**
    - CSL: Venus (benefic flavor)
    - CSL in Nakshatra: Pushya
    - Star Lord: Saturn
    - Star Lord Signifies: Houses [6, 8, 12]
    - Wealth Connection: 0/3
    - Loss Connection: 3/3 (strong)
    - **Verdict: WEAK**
    - Why: Venus (benefic flavor) is in Pushya nakshatra, ruled by Saturn. Saturn signifies 
    debt (6th house), sudden loss (8th house), and expenses (12th house). Despite Venus 
    being benefic (smooth flavor), the RESULT comes from Saturn's significations showing 
    income will drain through these channels. Result (Saturn's 6-8-12) overrides flavor (Venus benefic)."

    **WRONG EXAMPLE - NEVER DO THIS:**
    "House 2: Venus is benefic, so income is strong." ❌
    (This ignores star lord and significations completely!)

    ⚠️ If significations are MISSING or EMPTY:
    - State clearly: "⚠️ WARNING: Star lord significations unavailable for this house"
    - Say: "KP analysis is INCOMPLETE. Verdict is based on planet nature (less reliable)."
    - Explain the limitation honestly

    **B. MODERN INVESTMENT MAPPING (From KP Significations):**

    Create a clear table mapping significations to modern investment types:

    | Investment Type | Suitability | KP Reasoning |
    |----------------|-------------|--------------|
    | **Equity Mutual Funds (Large Cap)** | [HIGH/MODERATE/AVOID] | [Based on 11th house significations → systematic gains] |
    | **Gold/Silver (ETF or Physical)** | [HIGH/MODERATE/AVOID] | [Based on 2nd house significations → wealth preservation] |
    | **Real Estate/Land** | [HIGH/MODERATE/AVOID] | [Based on 4th/11th significations → property + gains] |
    | **Fixed Deposits/Bonds** | [HIGH/MODERATE/AVOID] | [Based on 2nd house → conservative savings] |
    | **Index Funds (Passive)** | [HIGH/MODERATE/AVOID] | [Based on 11th house → steady returns] |
    | **Day Trading/Intraday** | [HIGH/MODERATE/AVOID] | [Based on 5th/8th significations → speculation risk] |
    | **Cryptocurrency** | [HIGH/MODERATE/AVOID] | [Based on 5th/8th significations → volatility/sudden loss risk] |
    | **Derivatives/Options** | [HIGH/MODERATE/AVOID] | [Based on 5th house → leveraged speculation danger] |

    **Recommended Portfolio Allocation (Specific percentages):**
    - [X]% Equity Mutual Funds (Large Cap)
    - [Y]% Gold/Silver
    - [Z]% Real Estate (when timing favorable - see below)
    - [A]% Fixed Deposits/Bonds
    - [B]% Emergency liquid cash

    **C. VEDIC SYSTEM ANALYSIS (Secondary - 30% weight):**

    **1. Lagna Lord Analysis (Financial Foundation):**
    - Planet: [Name] (lord of [Ascendant sign])
    - Placed in: House [N], Sign [Name]
    - Dignity: [Exalted/Own Sign/Friendly/Neutral/Enemy/Debilitated]
    - Strength: [X]/100
    - Retrograde: [Yes/No]
    - Financial Personality: [Conservative/Aggressive/Balanced/Analytical/etc]
    - Investment Approach: [Describe based on planet - see personality mapping in system prompt]

    **Impact on Financial Decisions:**
    [Explain how lagna lord influences the person's fundamental relationship with money.
    Example: "Saturn lagna lord makes you naturally conservative. You prefer slow, steady 
    wealth building over quick gains. This SUPPORTS the KP recommendation for long-term investing."]

    **2. Wealth House Lords Analysis (2nd, 10th, 11th):**

    Analyze each lord and CHECK if they CONFIRM or CONTRADICT KP findings:

    - **2nd Lord ([Planet])**: [Placement, dignity, strength]
    → [Does this CONFIRM KP's 2nd house verdict? Or show obstacles?]
    
    - **10th Lord ([Planet])**: [Placement, dignity, strength]
    → [Does this support career income capacity?]
    
    - **11th Lord ([Planet])**: [Placement, dignity, strength]
    → [Does this AGREE with KP's gains promise?]

    **Vedic-KP Agreement Check:**
    - If both agree: "✅ Vedic CONFIRMS KP: [Explain how both systems point to same conclusion]"
    - If they differ: "⚠️ KP shows [X] BUT Vedic shows [Y] because [obstacle/challenge]. 
                        For concrete events, KP (significations) takes priority."

    **D. UNIFIED SYNTHESIS (5% weight - Tie it all together):**

    Combine: KP significations + Vedic capacity + Lagna lord personality → Final recommendation

    Example:
    "Based on:
    - KP significations: 2nd house weak (drains through 6-8-12), 11th house moderate (gains need effort)
    - Vedic: 2nd lord Venus debilitated (confirms income challenges), 11th lord Mars in 6th (gains through struggle)
    - Lagna lord: Saturn (conservative, patient approach needed)

    **FINAL RECOMMENDATION:**
    You are a CONSERVATIVE investor by nature (Saturn lagna). KP shows income drains easily and 
    speculation is risky. Vedic confirms this with weak wealth lords.

    **ACTION PLAN:**
    1. Avoid: Day trading, cryptocurrency, derivatives (KP 5th/8th house warnings)
    2. Focus on: Equity MF (40%), Gold (30%), FD (20%), Cash (10%)
    3. Strategy: Slow accumulation through SIP, not lump-sum
    4. Timeframe: Long-term (7+ years) to overcome weak gains houses"

    **E. DASHA TIMING ANALYSIS (15% weight):**

    **Current Dasha Impact (Next 3-6 months):**
    - Dasha: [Current Maha-Antara-Pratyantar]
    - Period: [Start] to [End]
    - Immediate Action: [What to do NOW based on current dasha]
    Example: "Current Moon-Jupiter favorable for starting SIP in equity mutual funds.
            Begin with ₹5,000-10,000/month in large-cap funds."

    **Upcoming Favorable Periods (Next 1-2 years):**
    List 2-3 upcoming dashas for systematic investing (NOT for property/timing - that's section F):
    - [Dasha 1]: [Dates] → [Good for: Gold accumulation / Increasing SIP / etc]
    - [Dasha 2]: [Dates] → [Good for: FD locking / Portfolio review / etc]

    ⚠️ CRITICAL DASHA-KP ALIGNMENT RULE:
    If this is a TIMING question (property/vehicle purchase), DO NOT loosely mention different 
    dashas here. You MUST align with the KP timing windows provided in section F below.

    {timing_section}

    **SUMMARY:**
    <Concise 2-3 sentence outlook with {('specific timing dates and actionable steps' if has_timing else 'dasha guidance and portfolio recommendations')}>

    Example: "KP significations show long-term investment capacity but speculation risk. 
    Vedic confirms with weak 5th lord. Recommended: 40% equity MF + 30% gold + 20% FD. 
    {('Property purchase best window: July 2032 (Mars-Mars-Saturn dasha)' if has_timing else 'Start SIP immediately in current Jupiter period')}."

    **REMEDIES_ASTROLOGICAL:**
    - [Target weak star lords, NOT just CSL planets]
    - [Strengthen planets whose significations support wealth (2-10-11)]
    - [Example: If Saturn star lord signifies 6-8-12, do Saturn remedies to reduce malefic effects]

    **REMEDIES_GENERAL:**
    - [Financial discipline aligned with KP significations]
    - [Avoid investment types warned by star lord significations]
    - [Build emergency fund (mention specific months of expenses based on chart)]
    - [Example: "Avoid day trading (5th house Mars signifies losses). Focus on 6-month emergency fund."]
    """
        
        # ═══════════════════════════════════════════════════════════
        # VEDIC ONLY FORMAT (When KP not available)
        # ═══════════════════════════════════════════════════════════
        
        else:
            return f"""
        OUTPUT FORMAT (STRICT):

        **GENERAL_ANSWER:**
        <Clear, actionable answer in simple terms.>

        **ASTROLOGICAL_ANALYSIS:**

        **A. LAGNA LORD ANALYSIS (Financial Foundation - 20% weight):**
        - Planet: [Name] (lord of [Ascendant sign])
        - Placed in: House [N], Sign [Name]
        - Dignity: [Exalted/Own Sign/Friendly/Neutral/Enemy/Debilitated]
        - Strength: [X]/100
        - Retrograde: [Yes/No]
        - Financial Personality: [Conservative/Aggressive/Balanced/Analytical/etc]
        - Investment Approach: [Describe based on planet]

        **Impact on Financial Decisions:**
        [Explain how lagna lord influences the person's fundamental relationship with money.
        Example: "Saturn lagna lord makes you naturally conservative. You prefer slow, steady 
        wealth building over quick gains. This supports long-term investing approach."]

        **B. VEDIC HOUSE LORD ANALYSIS (Primary - 60% weight):**

        **Wealth Houses (2nd, 10th, 11th) - Detailed Analysis:**

        For each house:
        - Lord: [Planet]
        - Placement: House [N], Sign [Name]
        - Dignity: [Status]
        - Strength: [X]/100
        - Condition: [Combust/Retrograde/Aspected by/Conjoined with]
        - Assessment: [STRONG/MODERATE/WEAK]
        - Impact: [How this affects income/career/gains]

        **Risk Houses (5th, 8th) - Speculation/Hidden Wealth:**
        - [Analyze speculation capacity and hidden wealth potential]

        **Aspects and Yogas:**
        - [Any relevant wealth yogas or challenging aspects]

        **C. MODERN INVESTMENT MAPPING:**

        Create a clear table mapping house lord strengths to modern investment types:

        | Investment Type | Suitability | Reasoning |
        |----------------|-------------|-----------|
        | **Equity Mutual Funds (Large Cap)** | [HIGH/MODERATE/AVOID] | [Based on 11th house lord strength] |
        | **Gold/Silver (ETF or Physical)** | [HIGH/MODERATE/AVOID] | [Based on 2nd house lord strength] |
        | **Real Estate/Land** | [HIGH/MODERATE/AVOID] | [Based on 4th/11th house strength] |
        | **Fixed Deposits/Bonds** | [HIGH/MODERATE/AVOID] | [Based on 2nd house lord → conservative capacity] |
        | **Index Funds (Passive)** | [HIGH/MODERATE/AVOID] | [Based on 11th house lord → steady returns] |
        | **Day Trading/Intraday** | [HIGH/MODERATE/AVOID] | [Based on 5th house lord → speculation risk] |
        | **Cryptocurrency** | [HIGH/MODERATE/AVOID] | [Based on 5th/8th house lords → volatility risk] |
        | **Derivatives/Options** | [HIGH/MODERATE/AVOID] | [Based on 5th house lord → leveraged risk] |

        **Recommended Portfolio Allocation (Specific percentages):**
        - [X]% Equity Mutual Funds (Large Cap)
        - [Y]% Gold/Silver
        - [Z]% Real Estate (when timing favorable - see below)
        - [A]% Fixed Deposits/Bonds
        - [B]% Emergency liquid cash

        **D. DASHA TIMING (20% weight):**
        
        **Current Dasha Impact (Next 3-6 months):**
        - Dasha: [Current Maha-Antara-Pratyantar]
        - Period: [Start] to [End]
        - Immediate Action: [What to do NOW based on current dasha]
        Example: "Current Moon-Jupiter favorable for starting SIP in equity mutual funds.
                Begin with ₹5,000-10,000/month in large-cap funds."

        **Upcoming Favorable Periods (Next 1-2 years):**
        List 2-3 upcoming dashas for systematic investing:
        - [Dasha 1]: [Dates] → [Good for: Gold accumulation / Increasing SIP / etc]
        - [Dasha 2]: [Dates] → [Good for: FD locking / Portfolio review / etc]

        {timing_section}

        **E. FINAL VERDICT:**
        
        Synthesize all Vedic findings into clear recommendation:
        
        Based on:
        - Lagna lord: [Planet] ([Conservative/Aggressive nature])
        - 2nd lord: [Planet] ([Income capacity])
        - 11th lord: [Planet] ([Gains potential])
        - 5th lord: [Planet] ([Speculation risk])

        **FINAL RECOMMENDATION:**
        [Clear conclusion about investment approach]

        **ACTION PLAN:**
        1. Avoid: [List risky investments based on weak houses]
        2. Focus on: [List suitable investments based on strong houses]
        3. Strategy: [Long-term vs short-term approach]
        4. Timeframe: [When to invest based on dashas]

        **SUMMARY:**
        <Concise outlook with {('timing dates' if has_timing else 'dasha guidance')}>

        Example: "Long-term investment capacity with moderate speculation risk. 
        Recommended: 40% equity MF + 30% gold + 20% FD. 
        {('Property purchase best window: Nov 2027 (Moon-Saturn-Ketu dasha)' if has_timing else 'Start SIP immediately in current Jupiter period')}."

        **REMEDIES_ASTROLOGICAL:**
        - [Strengthen weak Vedic house lords]
        - [Target planets whose houses support wealth (2nd, 10th, 11th lords)]

        **REMEDIES_GENERAL:**
        - [Financial planning based on Vedic analysis]
        - [Build emergency fund (specify months based on chart)]
        - [Avoid investment types warned by weak house lords]
        """

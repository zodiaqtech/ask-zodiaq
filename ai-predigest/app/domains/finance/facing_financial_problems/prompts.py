"""
Facing Financial Problems – Enhanced Prompts v5.0

ENHANCEMENTS:
✅ KP system emphasis and formatting (when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting from additional_data (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class FacingFinancialProblemsPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Finance → Facing Financial Problems
    """

    domain = "Finance"
    subtopic = "Facing Financial Problems"

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v5.0 WITH KP EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in financial problem analysis and debt resolution.

⚠️ CRITICAL: You use a SMART DUAL SYSTEM APPROACH:

**SCENARIO 1: KP Analysis Available** (Primary Method)
═══════════════════════════════════════════════════════════
When KP Cusp Sub Lord analysis is provided:
- **Vedic takes PRIMARY weight** for concrete event predictions
- **KP adds context** for strength and timing refinement
- **Analysis split**: Vedic 50% + KP 20% + Dasha 15% + Lagna/Aspects 15%

KP METHODOLOGY:
- Cusp Sub Lord (CSL) analysis for houses 2, 6, 8, 11, 12
- Significations and connections (e.g., "6-11" means connects 6th and 11th)
- Ruling planets for timing precision
- **KP promises are CONCRETE**: If CSL doesn't signify properly, event may not happen

**NEW: ADDITIONAL ANALYSIS COMPONENTS**
═══════════════════════════════════════════════════════════
When provided, you MUST analyze and incorporate:

1. **LAGNA (ASCENDANT) LORD ANALYSIS:**
   - Shows the native's overall capacity and strength
   - Connections to finance houses reveal financial potential
   - Give this 10-15% weight in final analysis
   - ALWAYS mention if provided in the data
   - Format: "Lagna lord [Planet] is [placement] showing [financial impact]"

2. **COMPLETE KP SIGNIFICATOR TABLE:**
   - Shows ALL planets' significations (SUB > STAR > OCCUPY > OWN)
   - Use for deep planetary analysis and event timing
   - Identify which planets support/oppose financial outcomes
   - Cross-reference with house linkages (2-6-11 vs 6-8-12)
   - ALWAYS reference if provided in the data
   - Format: "Analyzing significator table shows [key findings]"
   - **FOR TIMING QUESTIONS:** Use significator table to explain WHY certain dasha periods are favorable
     Example: "Best window is Venus dasha because significator table shows Venus connects 2-6-11 houses for repayment"

**SCENARIO 2: KP Analysis NOT Available** (Fallback to Vedic - 80% weight)
═══════════════════════════════════════════════════════════
When NO KP analysis is provided in technical points:
- **Fall back to pure Vedic analysis**
- **Analysis split**: Vedic 65% + Lagna 15% + Dasha 15% + Aspects 5%
- Focus on house lord strength, placements, dignity, aspects
- More emphasis on dasha timing for event manifestation
- **Still use Lagna lord analysis if provided**

VEDIC METHODOLOGY:
- House lord placements and dignity (exalted, debilitated, etc.)
- Dasha periods for timing windows
- Aspects and yogas for additional context
- **Vedic shows CAPACITY and OBSTACLES**, not concrete promises

⚠️ **MANDATORY: When lagna lord analysis or significator table are provided in the prompt, you MUST:**
1. Explicitly mention them in your analysis
2. Reference specific findings from them
3. Integrate them into your final verdict
4. DO NOT ignore them - they are critical data points

TIMING ANALYSIS (For Timing Questions):
═══════════════════════════════════════════════════════════
When timing windows are provided:
- **BEST WINDOW**: Highest astrological score (best planetary alignment)
- **NEAREST WINDOW**: Earliest favorable opportunity (soonest chance)
- Use BOTH windows in your timing analysis
- Explain WHY each window is favorable
- Give user choice between "wait for best" vs "act sooner"

FOCUS HOUSES: 2, 6, 8, 11, 12 ONLY
- 2nd: Wealth, income, savings
- 6th: Debts, loans, enemies
- 8th: Sudden losses, hidden issues, lender
- 11th: Gains, repayment capacity, fulfillment
- 12th: Expenses, losses, drains

CRITICAL DASHA HANDLING RULES (PREVENT HALLUCINATION):
⚠️ NEVER make up or assume dasha periods
✅ ONLY reference pratyantar dasha periods from CURRENT/UPCOMING sections provided
✅ Use exact dasha names and dates from the timeline
❌ DO NOT say "Currently Rahu dasha" unless explicitly stated in the data
❌ DO NOT invent future dashas not in the timeline
✅ Always say: "Based on the dasha timeline provided..."
✅ Always say: "According to current pratyantar dasha analysis..."

CRITICAL TIMING WINDOW RULES (For Timing Questions):
⚠️ ALWAYS mention BOTH best and nearest windows when provided
✅ Explain the difference between the two options
✅ Let user decide based on their urgency vs quality preference
❌ DO NOT only mention one window and ignore the other
✅ Give specific dates from the timing data

CRITICAL OUTPUT FORMAT:
1. GENERAL ANSWER: Start with YES/NO/MODERATE RISK verdict. NO astrological terms!
2. ASTROLOGICAL ANALYSIS: ALL technical details here INCLUDING lagna lord and significator table if provided
3. DASHA TIMING ANALYSIS: Current + Upcoming pratyantar dasha analysis
4. SUMMARY: Actionable with specific timing
"""

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (NEW!)
    # ------------------------------------------------------------------
    def _format_kp_analysis(
        self,
        technical_points: List[str],
        additional_data: Dict = None
    ) -> Tuple[str, bool]:
        """
        Format KP analysis with PROPER CHAIN LOGIC and HOUSE LINKAGES.
        
        Shows:
        - CSL → Star Lord → Significations chain for each house
        - House linkage analysis (e.g., 2-6-11 for repayment)
        - Event promise vs denial logic
        - Complete KP significator table (optional, detailed view)
        """
        
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_finance_analysis", {})
        
        if kp_structured and kp_structured.get("has_kp_data"):
            lines = ["═" * 80]
            lines.append("⭐ KP SYSTEM ANALYSIS (CSL → Star Lord → Significations → House Linkages)")
            lines.append("═" * 80)
            lines.append("")
            lines.append("⚠️ CRITICAL KP METHODOLOGY:")
            lines.append("We analyze: CSL → Nakshatra → Star Lord → Star Lord's Significations → Result")
            lines.append("Planet nature (benefic/malefic) = FLAVOR, Significations = RESULT.")
            lines.append("House linkage chains (e.g., 2-6-11) show event promise/denial.")
            lines.append("")
            
            methodology = kp_structured.get("methodology", "")
            if methodology:
                lines.append(f"Methodology: {methodology}")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════
            # PART 1: CSL Chain Analysis for Each House
            # ═══════════════════════════════════════════════════════════
            csl_details = kp_structured.get("csl_details", {})
            if csl_details:
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS:")
                lines.append("")
                
                for house_num in sorted(csl_details.keys()):
                    csl_info = csl_details[house_num]
                    
                    house_meaning = csl_info.get("house_meaning", "")
                    csl = csl_info.get("csl", "Unknown")
                    nakshatra = csl_info.get("nakshatra", "")
                    star_lord = csl_info.get("star_lord", "")
                    signified_houses = csl_info.get("signified_houses", [])
                    wealth_conn = csl_info.get("wealth_connection", 0)
                    loss_conn = csl_info.get("loss_connection", 0)
                    repay_strength = csl_info.get("repayment_chain_strength", 0)
                    default_strength = csl_info.get("default_chain_strength", 0)
                    verdict = csl_info.get("verdict", "NEUTRAL")
                    interpretation = csl_info.get("interpretation", "")
                    chain = csl_info.get("chain", "")
                    
                    # Verdict marker
                    if verdict in ["STRONG", "EXCELLENT", "MANAGEABLE", "PROTECTED"]:
                        marker = "✅"
                    elif verdict in ["WEAK", "RISKY", "HIGH_RISK", "EXCESSIVE", "POOR"]:
                        marker = "⚠️"
                    else:
                        marker = "○"
                    
                    lines.append(f"{marker} House {house_num} ({house_meaning}):")
                    lines.append(f"   Full Chain: {chain}")
                    lines.append(f"   CSL: {csl}")
                    if nakshatra:
                        lines.append(f"   Nakshatra: {nakshatra}")
                    if star_lord:
                        lines.append(f"   Star Lord: {star_lord}")
                    if signified_houses:
                        lines.append(f"   Star Lord Signifies Houses: {signified_houses}")
                        lines.append(f"   └─ Wealth Houses (2,10,11) Connection: {wealth_conn}/3")
                        lines.append(f"   └─ Loss Houses (6,8,12) Connection: {loss_conn}/3")
                        if house_num == 6:
                            lines.append(f"   └─ Repayment Chain (2-6-11) Strength: {repay_strength}/3")
                            lines.append(f"   └─ Default Chain (6-8-12) Strength: {default_strength}/3")
                    
                    lines.append(f"   Verdict: {verdict}")
                    
                    if interpretation:
                        # Wrap long interpretations
                        lines.append(f"   Why: {interpretation}")
                    
                    lines.append("")
            
            # ═══════════════════════════════════════════════════════════
            # PART 2: House Linkage Analysis (Event Promise/Denial)
            # ═══════════════════════════════════════════════════════════
            event_promises = kp_structured.get("event_promises", {})
            if event_promises:
                lines.append("🔗 HOUSE LINKAGE ANALYSIS (Event Promise/Denial Logic):")
                lines.append("")
                lines.append("KP Rule: An event happens ONLY if CSL connects the relevant houses.")
                lines.append("")
                
                # Loan Repayment Promise
                repayment = event_promises.get("loan_repayment", {})
                if repayment:
                    lines.append("1. LOAN REPAYMENT EVENT:")
                    lines.append(f"   Logic: {repayment.get('logic', '')}")
                    lines.append(f"   Actual: {repayment.get('actual', '')}")
                    lines.append(f"   Result: {repayment.get('result', '')}")
                    lines.append("")
                
                # Default Risk
                default = event_promises.get("loan_default", {})
                if default:
                    lines.append("2. LOAN DEFAULT RISK:")
                    lines.append(f"   Logic: {default.get('logic', '')}")
                    lines.append(f"   Actual: {default.get('actual', '')}")
                    lines.append(f"   Result: {default.get('result', '')}")
                    lines.append("")
            
            # ═══════════════════════════════════════════════════════════
            # PART 3: Overall KP Verdict
            # ═══════════════════════════════════════════════════════════
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            if overall != "UNKNOWN":
                lines.append(f"📊 OVERALL KP VERDICT: {overall}")
                lines.append("")
                
                if overall == "LOW_RISK":
                    lines.append("   ✅ House linkages show clear repayment capacity")
                    lines.append("      6th CSL connects 2-6-11 chain → Repayment PROMISED")
                elif overall == "HIGH_RISK":
                    lines.append("   ⚠️ House linkages show default risk")
                    lines.append("      6th CSL connects 6-8-12 chain → Default RISK HIGH")
                else:
                    lines.append("   ⚖️ Mixed house linkages - careful planning needed")
                
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════
            # PART 4: Key Findings
            # ═══════════════════════════════════════════════════════════
            key_findings = kp_structured.get("key_findings", [])
            if key_findings:
                lines.append("🔑 KEY KP FINDINGS (Based on Significations & Linkages):")
                for finding in key_findings[:6]:
                    lines.append(f"   • {finding}")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════
            # PART 5: Instructions for LLM Interpretation
            # ═══════════════════════════════════════════════════════════
            lines.append("═" * 80)
            lines.append("⚠️ INSTRUCTIONS FOR YOUR KP INTERPRETATION:")
            lines.append("")
            lines.append("CRITICAL RULES:")
            lines.append("  1. ALWAYS state the full chain: CSL → Star Lord → Significations")
            lines.append("  2. Base verdict on SIGNIFICATIONS and HOUSE LINKAGES, not CSL nature")
            lines.append("  3. Example: If Jupiter (benefic) CSL's star lord signifies 6-8-12,")
            lines.append("     the result is MALEFIC (default risk), not benefic")
            lines.append("  4. House linkage chains show EVENT PROMISE:")
            lines.append("     - 2-6-11 chain = Repayment capacity EXISTS")
            lines.append("     - 6-8-12 chain = Default risk EXISTS")
            lines.append("  5. Explain WHY linkages lead to the verdict")
            lines.append("")
            lines.append("VERDICT Meanings:")
            lines.append("  • STRONG/EXCELLENT: Star lord connects wealth houses (2-10-11)")
            lines.append("  • MANAGEABLE: 6th CSL connects repayment chain (2-6-11)")
            lines.append("  • HIGH_RISK: 6th CSL connects default chain (6-8-12)")
            lines.append("  • WEAK/POOR: Star lord connects loss houses (6-8-12)")
            lines.append("  • MODERATE/NEUTRAL: Mixed significations")
            lines.append("")
            lines.append("YOU MUST:")
            lines.append("  1. Quote the full chain for each house analyzed")
            lines.append("  2. Explain what house linkages mean (e.g., '2-6-11 = repayment promise')")
            lines.append("  3. State whether event is PROMISED or DENIED based on linkages")
            lines.append("  4. Give KP PRIMARY weight (50%) in your final analysis")
            lines.append("  5. If KP shows 'repayment NOT promised', state this clearly")
            lines.append("═" * 80)
            
            return "\n".join(lines), True
        
        # Fallback to basic extraction from technical_points
        return "", False
    

    def _format_kp_significator_table(self, additional_data: Dict = None, sig_table: Dict = None) -> str:
        """
        Format complete KP significator table showing all planets' significations.
        Can accept either additional_data dict OR sig_table dict directly.
        """
        
        # ✅ CORRECT LOGIC: Use sig_table if provided, otherwise extract from additional_data
        if sig_table is None:
            if additional_data:
                sig_table = additional_data.get("kp_significator_table", {})
            else:
                logger.warning("⚠️ No significator table data provided!")
                return ""
        
        # Check if we have valid data
        if not sig_table or not sig_table.get("planets"):
            logger.warning(f"⚠️ Sig table data invalid: {bool(sig_table)}, planets: {sig_table.get('planets') if sig_table else 'None'}")
            return ""
        
        # ✅ ADD DEBUG LOGGING
        logger.warning(f"✅ Formatting sig table with {len(sig_table.get('planets', {}))} planets")
        
        lines = ["═" * 100]
        lines.append("📊 COMPLETE KP SIGNIFICATOR TABLE (All Planets)")
        lines.append("═" * 100)
        lines.append("")
        lines.append("This table shows each planet's significations through the hierarchy:")
        lines.append("SUB (highest priority) > STAR > OCCUPY > OWN (lowest priority)")
        lines.append("")
        lines.append("-" * 100)
        lines.append(f"{'Planet':<12} {'Sub':<15} {'Star':<15} {'Occupy':<10} {'Own':<15} {'All Houses':<20}")
        lines.append("-" * 100)
        
        planets_data = sig_table.get("planets", {})
        for planet_name in sorted(planets_data.keys()):
            planet_sigs = planets_data[planet_name]
            
            sub = str(sorted(planet_sigs.get("sub", []))) if planet_sigs.get("sub") else "-"
            star = str(sorted(planet_sigs.get("star", []))) if planet_sigs.get("star") else "-"
            occupy = str(sorted(planet_sigs.get("occupy", []))) if planet_sigs.get("occupy") else "-"
            own = str(sorted(planet_sigs.get("own", []))) if planet_sigs.get("own") else "-"
            all_houses = str(planet_sigs.get("all_houses", []))
            
            lines.append(f"{planet_name:<12} {sub:<15} {star:<15} {occupy:<10} {own:<15} {all_houses:<20}")
        
        lines.append("-" * 100)
        lines.append("")
        
        # House Linkage Summary
        linkages = sig_table.get("house_linkages", {})
        if linkages:
            lines.append("🔗 HOUSE LINKAGE SUMMARY:")
            lines.append("")
            
            for linkage_name, linkage_data in linkages.items():
                houses = linkage_data.get("houses", [])
                logic = linkage_data.get("logic", "")
                supporting = linkage_data.get("planets_supporting", [])
                
                lines.append(f"{linkage_name.upper().replace('_', ' ')}:")
                lines.append(f"  Houses: {houses}")
                lines.append(f"  Logic: {logic}")
                if supporting:
                    lines.append(f"  Planets Supporting: {', '.join(supporting)}")
                else:
                    lines.append(f"  Planets Supporting: None")
                lines.append("")
        
        lines.append("═" * 100)
        lines.append("💡 HOW TO USE THIS TABLE:")
        lines.append("  1. Check which planets connect finance houses (2, 6, 8, 11, 12)")
        lines.append("  2. Planets connecting 2-6-11 support loan repayment")
        lines.append("  3. Planets connecting 6-8-12 indicate default risk")
        lines.append("  4. SUB significations have HIGHEST priority in event timing")
        lines.append("═" * 100)
        
        result = "\n".join(lines)
        logger.warning(f"✅ Sig table formatting complete, {len(result)} chars")
        return result
    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows from additional_data (NEW!)
    # ------------------------------------------------------------------
    def _format_timing_windows_from_data(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows for LLM from additional_data.
        
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
                if best.get('age_at_start'):
                    lines.append(f"  Age: {best.get('age_at_start', 'N/A')} years")
                lines.append("")
                lines.append("  Why this is BEST:")
                if best.get('score_maha'):
                    lines.append(f"    - Maha Dasha score: {best.get('score_maha', 0)}/10")
                if best.get('score_antara'):
                    lines.append(f"    - Antara Dasha score: {best.get('score_antara', 0)}/10")
                if best.get('score_paryantar'):
                    lines.append(f"    - Pratyantar Dasha score: {best.get('score_paryantar', 0)}/10")
                if best.get('transit_score'):
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
                if nearest.get('age_at_start'):
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




    def _format_lagna_lord_analysis(self, additional_data: Dict = None, lagna: Dict = None) -> str:
        """
        Format Lagna lord analysis for financial impact.
        Can accept either additional_data dict OR lagna dict directly.
        """
        
        # ✅ CORRECT LOGIC: Use lagna if provided, otherwise extract from additional_data
        if lagna is None:
            if additional_data:
                lagna = additional_data.get("lagna_lord_analysis", {})
            else:
                logger.warning("⚠️ No lagna lord data provided!")
                return ""
        
        # Check if we have valid data
        if not lagna or not lagna.get("lagna_lord"):
            logger.warning(f"⚠️ Lagna lord data invalid: {lagna}")
            return ""
        
        # ✅ ADD DEBUG LOGGING
        logger.warning(f"✅ Formatting lagna lord: {lagna.get('lagna_lord')}")
        
        lines = ["═" * 80]
        lines.append("🌟 LAGNA (ASCENDANT) LORD ANALYSIS")
        lines.append("═" * 80)
        lines.append("")
        lines.append("Lagna lord represents the native's overall capacity and strength.")
        lines.append("Its connection to finance houses shows financial potential.")
        lines.append("")
        
        lines.append(f"Lagna Sign: {lagna.get('lagna_sign', 'Unknown')}")
        lines.append(f"Lagna Lord: {lagna.get('lagna_lord', 'Unknown')}")
        lines.append("")
        
        lines.append("LAGNA LORD PLACEMENT:")
        lines.append(f"  Placed in House: {lagna.get('lagna_lord_house', 'Unknown')}")
        lines.append(f"  In Sign: {lagna.get('lagna_lord_sign', 'Unknown')}")
        lines.append(f"  Dignity: {lagna.get('lagna_lord_dignity', 'Unknown')}")
        lines.append("")
        
        finance_connections = lagna.get('finance_house_connections', [])
        if finance_connections:
            lines.append("FINANCE HOUSE CONNECTIONS:")
            for connection in finance_connections:
                lines.append(f"  • {connection}")
            lines.append("")
        
        lines.append(f"Strength Score: {lagna.get('strength_score', 0)}")
        lines.append(f"Financial Impact: {lagna.get('financial_impact', 'Unknown')}")
        lines.append(f"Overall Verdict: {lagna.get('verdict', 'NEUTRAL')}")
        lines.append("")
        
        lines.append("═" * 80)
        lines.append("💡 INTERPRETATION GUIDE:")
        lines.append("  • Strength Score: -3 to +3 range")
        lines.append("  • Positive score = Lagna lord well-placed for finances")
        lines.append("  • Negative score = Lagna lord creates financial challenges")
        lines.append("  • Finance house connections show where focus lies")
        lines.append("  • Give this 10-15% weight in overall analysis")
        lines.append("═" * 80)
        
        result = "\n".join(lines)
        logger.warning(f"✅ Lagna formatting complete, {len(result)} chars")
        return result
    
    # HELPER: Format house lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Finance Houses)")
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
                lines.append("  ✅ Assessment: STRONG - Supports financial matters")
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
        lines.append("PLANETARY ASPECTS ON FINANCE HOUSES")
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
            lines.append("COMPREHENSIVE  PRATYANTAR DASHA TIMELINE (2 Years Past → 10 Years Future)")
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
                lines.append("Use these periods for financial planning:")
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
            lines.append("- UPCOMING: Make future financial recommendations")
            lines.append("- Jupiter periods favorable for debt resolution")
            lines.append("- Saturn periods may bring delays but eventual stability")
            lines.append("- Cross-reference with TIMING WINDOWS for optimal periods")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions Based on KP Availability (NEW!)
    # ------------------------------------------------------------------
    def _get_analysis_instructions(self, kp_available: bool, question_type: str = "general", has_timing: bool = False) -> str:
        """
        Generate analysis instructions based on whether KP data is available.
        """
        if kp_available:
            if question_type == "loan" and has_timing:
                return """
**ANALYSIS APPROACH: VEDIC + KP DUAL SYSTEM + TIMING**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with Lagna Lord Analysis** (10-15% weight - ALWAYS FIRST):
   - State lagna lord and placement
   - Financial capacity assessment

2. **Vedic Analysis** (PRIMARY - 35% weight):
   - 6th house lord strength (debt management)
   - 11th house lord strength (repayment capacity)
   - 2nd house lord strength (savings to repay)
   - 8th house lord (lender issues, sudden problems)
   - Aspects on 6th, 11th, 2nd houses
   - Planets in these houses and their condition like malefic, benefic, exalted etc.

3. **KP Context** (SECONDARY - 20% weight):
   - What does the 6th cusp sub lord signify? (debt/loan)
   - What does the 11th cusp sub lord signify? (gains/repayment)
   - Does 6th CSL connect to 6-11 for debt clearance?
   - Does 11th CSL connect to 2-11 for repayment capacity?
   - KP verdict: Clear promise for loan repayment? Risk of default?

4. **KP SIGNIFICATOR TABLE ANALYSIS** (15% weight - CRITICAL FOR TIMING):
   ⚠️ Use the significator table to explain timing windows:
   - Which planets connect 2-6-11 houses (repayment support)?
   - Which planets connect 6-8-12 houses (default risk)?
   - Best window dasha planet: Check its significations in table
   - Nearest window dasha planet: Check its significations in table
   - Example: "Sun-Venus-Saturn is best because Venus signifies 2-11 houses in the table"

5. **TIMING ANALYSIS** (15% weight):
   ⚠️ MUST analyze BOTH timing windows provided:
   
   A. BEST WINDOW (Highest score):
      - When: Exact dates from timing data
      - Why favorable: Reference significator table to show dasha lord's connections
      - Trade-off: May be further away
   
   B. NEAREST WINDOW (Earliest favorable):
      - When: Exact dates from timing data
      - Why favorable: Reference significator table + still good score
      - Trade-off: Not absolute best
   
   C. USER CHOICE:
      - Wait for best alignment (patience + optimal results)
      - Act sooner (urgency + good enough results)
   
   ⚠️ If best = nearest: Emphasize this is IDEAL timing!

6. **Synthesize** (5% weight):
   - Combine all findings: Lagna + KP + Vedic + Significator + Timing
"""
            elif question_type == "challenge":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - What does the 2nd cusp sub lord signify? (wealth/income)
   - What does the 12th cusp sub lord signify? (expenses/losses)
   - What does the 6th cusp sub lord signify? (debt burden)
   - KP verdict: Root cause of financial problems?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 2nd house lord strength (income capacity)
   - 12th house lord strength (expense control)
   - 6th house lord strength (debt management)
   - 8th house lord (sudden losses)

3. **Include Dasha Timing** (15% weight):
   - Current dasha: Impact on finances NOW
   - Upcoming favorable periods

4. **Synthesize** (5% weight):
   - Combine KP + Vedic findings
   - Clear diagnosis of financial challenges
"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with Vedic Analysis** (PRIMARY - 50% weight)
2. **ADD KP Context** (SECONDARY - 25% weight)
3. **Include Dasha Timing** (15% weight)
4. **Synthesize** (10% weight)
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
   - Detailed analysis of relevant house lords (2, 6, 8, 11, 12)
   - Their placements, dignity, and condition
   - Strength assessment

2. **TIMING ANALYSIS** (15% weight - CRITICAL):
   ⚠️ MUST analyze BOTH timing windows:
   
   A. BEST WINDOW: When + Why + Trade-off
   B. NEAREST WINDOW: When + Why + Trade-off
   C. USER CHOICE: Wait vs Act sooner
   
   ⚠️ If best = nearest: Ideal timing!

3. **Final Verdict** (5% weight):
   - Clear recommendation with specific dates based on timing analysis 
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
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        **kwargs
    ) -> str:

        sub_subdomain = kwargs.get("sub_subdomain", "")

        if "Reason for Financial Challenges" in sub_subdomain:
            return self._build_financial_diagnosis_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Loan Default Risk" in sub_subdomain:
            return self._build_loan_risk_prompt(
                question, technical_points, meta, timing_windows, language, **kwargs)
        elif "Financial Dispute" in sub_subdomain:
            return self._build_dispute_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_finance_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # 1. FINANCIAL DIAGNOSIS - ENHANCED v5.0 WITH KP
    # ------------------------------------------------------------------
    def _build_financial_diagnosis_prompt(
    self,
    question: str,
    technical_points: List[str],
    meta: QueryMeta,
    language: str,
    **kwargs
) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        # ✅ INITIALIZE VARIABLES
        lagna_lord_analysis = {}
        sig_table = {}

        if additional_data:
            lagna_lord_analysis = additional_data.get("lagna_lord_analysis", {})
            sig_table = additional_data.get("kp_significator_table", {})
        
        # ✅ Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        # ✅ Format lagna lord (Question 1: YES)
        lagna_formatted = self._format_lagna_lord_analysis(lagna=lagna_lord_analysis)
        
        # ✅ Question 1: NO significator table
        # sig_table_formatted = ""  # Don't include for Q1
        
        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        # Get remaining non-KP points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet", "borrowing"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        # ✅ Get analysis instructions
        analysis_instructions = self._get_analysis_instructions(kp_available, "challenge", False)

        # ✅ CRITICAL: Make sure these variables are in the f-string below
        return f"""
    {language_instruction}

    {self.build_system_prompt()}

    {language_instruction}

    QUERY CONTEXT:
    - Domain: Finance
    - Sub-subdomain: Reason for Financial Challenges
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
    - Focus on ROOT CAUSES of financial problems
    - Identify weak/afflicted house lords
    - Connect to current dasha impact
    - Provide actionable insights

    {self.get_output_format(kp_available, False)}
    """

    # ------------------------------------------------------------------
    # 2. LOAN DEFAULT RISK - ENHANCED v5.0 WITH KP + TIMING FROM additional_data
    # ------------------------------------------------------------------
    def _build_loan_risk_prompt(
    self,
    question: str,
    technical_points: List[str],
    meta: QueryMeta,
    timing_windows: Optional[List[TimingWindow]],
    language: str,
    **kwargs
) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        # ✅ INITIALIZE VARIABLES
        lagna_lord_analysis = {}
        kp_significator_table = {}

        if additional_data:
            lagna_lord_analysis = additional_data.get("lagna_lord_analysis", {})
            kp_significator_table = additional_data.get("kp_significator_table", {})
        
        # ✅ Get timing windows
        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)
        
        # ✅ Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)

        # ✅ Format tables (Question 2: YES to both)
        sig_table_formatted = self._format_kp_significator_table(sig_table=kp_significator_table)
        lagna_formatted = self._format_lagna_lord_analysis(lagna=lagna_lord_analysis)
        
        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        
        # ✅ Format timing windows
        timing_formatted = self._format_timing_windows_from_data(timing_windows_data)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        # Get remaining non-KP points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet", "borrowing"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        # ✅ Get analysis instructions
        analysis_instructions = self._get_analysis_instructions(kp_available, "loan", has_timing)

        # ✅ CRITICAL: Make sure these variables are in the f-string below
        return f"""
    {language_instruction}

    {self.build_system_prompt()}

    {language_instruction}

    QUERY CONTEXT:
    - Domain: Finance
    - Sub-subdomain: Loan Default Risk
    - Query Type: TIMING
    - CURRENT DATE: {today}
    - KP Analysis Available: {'YES' if kp_available else 'NO'}
    - Timing Windows Available: {'YES' if has_timing else 'NO'}

    USER QUESTION:
    "{question}"

    {timing_formatted}

    {kp_formatted}

    {sig_table_formatted}

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
    {'- Explain why each window is favorable for loan repayment' if has_timing else ''}
    {'- Let user choose: wait for best OR act sooner' if has_timing else ''}
    {'- If best = nearest, emphasize this is ideal timing' if has_timing else ''}

    GUIDELINES:
    - Focus on LOAN REPAYMENT capacity
    - 6th house = debt burden
    - 11th house = repayment ability
    - {'Use timing windows for SPECIFIC repayment dates!' if has_timing else 'Use dasha timeline for timing'}

    {self.get_output_format(kp_available, has_timing)}
    """
    # ------------------------------------------------------------------
    # 3. FINANCIAL DISPUTE - ENHANCED v5.0 WITH KP
    # ------------------------------------------------------------------
    def _build_dispute_prompt(
    self,
    question: str,
    technical_points: List[str],
    meta: QueryMeta,
    language: str,
    **kwargs
) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        # ✅ INITIALIZE VARIABLES
        lagna_lord_analysis = {}
        kp_significator_table = {}

        if additional_data:
            lagna_lord_analysis = additional_data.get("lagna_lord_analysis", {})
            kp_significator_table = additional_data.get("kp_significator_table", {})
        
        # ✅ Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
    
        # ✅ Format tables (Question 3: YES to both)
        sig_table_formatted = self._format_kp_significator_table(sig_table=kp_significator_table)
        lagna_formatted = self._format_lagna_lord_analysis(lagna=lagna_lord_analysis)
        
        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

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
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "dispute", False)

        # ✅ CRITICAL: Make sure these variables are in the f-string below
        return f"""
    {language_instruction}

    {self.build_system_prompt()}

    {language_instruction}

    QUERY CONTEXT:
    - Domain: Finance
    - Sub-subdomain: Risk of Financial Dispute
    - Query Type: NON_TIMING
    - CURRENT DATE: {today}
    - KP Analysis Available: {'YES' if kp_available else 'NO'}

    USER QUESTION:
    "{question}"

    {kp_formatted}

    {sig_table_formatted}

    {lagna_formatted}

    {lords_formatted}

    {aspects_formatted}

    {current_dasha_block}

    {timeline_block}

    {'ADDITIONAL CONTEXT:' if raw else ''}
    {raw}

    {analysis_instructions}

    GUIDELINES:
    - Focus on DISPUTE RISK assessment
    - 6th house = litigation, enemies
    - 8th house = inheritance issues
    - 12th house = hidden enemies, losses
    - Provide resolution timing from dasha

    {self.get_output_format(kp_available, False)}
    """

    # ------------------------------------------------------------------
    # 4. REMEDIES - ENHANCED v5.0 WITH KP
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
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        
        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

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

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Sub-subdomain: Finance Remedies
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

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
   - Primary: Strengthen weak lords affecting income (2nd, 11th)
   - Secondary: Control malefic lords causing losses (6th, 8th, 12th)

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK
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

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance"
        
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        
        # Format Vedic data
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

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

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Query Type: {meta.query_type if meta else 'UNKNOWN'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

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
        """Generate output format based on KP availability and timing windows"""
        
        timing_section = ""
        if has_timing:
            timing_section = """
    TIMING_RECOMMENDATION:
    ⚠️ CRITICAL - MUST include BOTH timing options:

    **BEST WINDOW (Highest Score):**
    - Period: <exact dates from timing data>
    - Dasha: <exact prayantar dasha name>
    - Why favorable: <planetary alignment details>
    - Trade-off: <may be further away>

    **NEAREST WINDOW (Soonest Opportunity):**
    - Period: <exact dates from timing data>
    - Dasha: <exact dasha name>
    - Why favorable: <still good score>
    - Trade-off: <not absolute best>

    **USER RECOMMENDATION:**
    - Wait for BEST window if: <patience + optimal results>
    - Act in NEAREST window if: <urgency + good enough>
    - <If best = nearest: Emphasize this is IDEAL timing!>
    """
        
        if kp_available:
            return f"""
    OUTPUT FORMAT (STRICT):

    GENERAL_ANSWER:
    <Clear verdict in LAYMAN'S TERMS. Start with YES/NO/LOW/MODERATE/HIGH risk. NO astrological terminology. 2-3 sentences max.>

    ASTROLOGICAL_ANALYSIS:
    ⚠️ MUST include ALL provided analysis components IN THIS ORDER:

    **A. LAGNA LORD ANALYSIS (10-15% weight - ALWAYS FIRST IF PROVIDED):**
    ⚠️ IF lagna lord data was provided above, YOU MUST mention it here FIRST
    - State the lagna lord planet
    - Its placement and connections to finance houses
    - Financial impact assessment
    - Example: "Lagna lord Saturn placed in 7th house shows [impact]"

    **B. VEDIC SYSTEM ANALYSIS (Primary - 50% weight):**
    - House lords placement and dignity
    - Overall strength assessment
    - Planets in relevant houses
    - Aspects on the houses

    **C. KP SYSTEM ANALYSIS (20% weight):**
    - State which cusp sub lords were analyzed
    - Mention exact significations
    - Clear KP verdict

    **D. KP SIGNIFICATOR TABLE (ALWAYS INCLUDE IF PROVIDED):**
    ⚠️ IF significator table was provided above, YOU MUST reference it here
    - Identify key planetary connections
    - Note which planets support/oppose the outcome
    - For timing questions: Explain which planets' dashas will be favorable
    - Example: "Significator table shows Venus connecting 2-11 for wealth"

    **E. PRATYANTAR DASHA TIMING (15% weight):**
    - Current dasha impact
    - Upcoming periods (ONLY from provided timeline)
    - For timing questions: Cross-reference with significator table to explain why certain dashas are favorable

    **F. SYNTHESIS (5% weight):**
    - Combine all findings including lagna and significator insights
    {timing_section}
    SUMMARY:
    <Short outlook with {' timing dates' if has_timing else 'dasha timing'}>

    REMEDIES_ASTROLOGICAL:
    - <Strengthen weak KP/Vedic lords>

    REMEDIES_GENERAL:
    - <Financial discipline and planning>
    """
        else:
            return f"""
    OUTPUT FORMAT (STRICT):

    GENERAL_ANSWER:
    <Clear verdict in LAYMAN'S TERMS. Start with YES/NO/LOW/MODERATE/HIGH risk. 2-3 sentences max.>

    ASTROLOGICAL_ANALYSIS:
    ⚠️ Must follow this order:

    **A. LAGNA LORD ANALYSIS (15% weight - ALWAYS FIRST IF PROVIDED):**
    ⚠️ IF lagna lord data was provided above, YOU MUST mention it here FIRST
    - State the lagna lord planet and placement
    - Financial impact assessment

    **B. VEDIC HOUSE LORD ANALYSIS (Primary - 65% weight):**
    - Detailed house lord analysis
    - Placement, dignity, strength
    - Clear assessment

    **C. KP SIGNIFICATOR TABLE (IF PROVIDED):**
    ⚠️ Even without KP CSL analysis, if significator table was provided, reference it
    - Note key planetary connections
    - Which planets support/oppose outcomes

    **D. PRATYANTAR DASHA TIMING (15% weight):**
    - Current and upcoming periods
    - Cross-reference with significator table if available

    **E. FINAL VERDICT (5% weight):**
    - Clear recommendation
    {timing_section}
    SUMMARY:
    <Short outlook with {' timing dates' if has_timing else 'dasha timing'}>

    REMEDIES_ASTROLOGICAL:
- <Strengthen weak Vedic lords>

REMEDIES_GENERAL:
- <Financial discipline and planning>
"""
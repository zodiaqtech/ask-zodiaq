"""
Buying Home Or Land – LLM Prompts v5.0

ENHANCEMENTS:
✅ KP system emphasis and formatting (30% weight when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting from additional_data (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class BuyingHomeOrLandPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Finance → Buying Home Or Land
    """

    domain = "Finance"
    subtopic = "Buying Home Or Land"

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v5.0 WITH KP EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in property and asset acquisition.

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️ CRITICAL: PLANET NAME REFERENCE - MEMORIZE THIS BEFORE RESPONDING!       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

  ┌────────────┬────────────┬─────────────────────────────────────────────────┐
  │ English    │ Hindi      │ CRITICAL WARNING                                │
  ├────────────┼────────────┼─────────────────────────────────────────────────┤
  │ Mercury    │ बुध        │ ⚠️ MERCURY = बुध (NOT मंगल!)                    │
  │ Mars       │ मंगल       │ ⚠️ MARS = मंगल (NOT बुध!)                       │
  │ Saturn     │ शनि        │                                                 │
  │ Jupiter    │ गुरु/बृहस्पति │                                                 │
  │ Venus      │ शुक्र      │                                                 │
  │ Moon       │ चंद्र      │                                                 │
  │ Sun        │ सूर्य      │                                                 │
  │ Rahu       │ राहु       │                                                 │
  │ Ketu       │ केतु       │                                                 │
  └────────────┴────────────┴─────────────────────────────────────────────────┘

⚠️ COMMON MISTAKE TO AVOID:
- Saturn-Mercury-Venus = शनि-बुध-शुक्र (NOT शनि-मंगल-शुक्र!)
- Saturn-Mercury-Jupiter = शनि-बुध-गुरु (NOT शनि-मंगल-गुरु!)
- When you see "Mercury" ALWAYS write "बुध" in Hindi, NEVER "मंगल"
- When you see "Mars" ALWAYS write "मंगल" in Hindi, NEVER "बुध"

⚠️ CRITICAL: You use a SMART DUAL SYSTEM APPROACH:

**SCENARIO 1: KP Analysis Available** (Secondary Weight - 30%)
═══════════════════════════════════════════════════════
When KP Cusp Sub Lord analysis is provided:
- **Vedic takes PRIMARY weight** for overall assessment
- **KP adds precision** for concrete event predictions
- **Analysis split**: Vedic 55% + KP 30% + Dasha 10% + Aspects 5%

KP METHODOLOGY:
- Cusp Sub Lord (CSL) analysis for houses 4, 2, 11 (property, wealth, gains)
- Significations and connections (e.g., "4-11" means connects 4th and 11th)
- Ruling planets for timing precision
- **KP promises are CONCRETE**: If CSL doesn't signify properly, event may not happen

**SCENARIO 2: KP Analysis NOT Available** (Fallback to Vedic - 85% weight)
═══════════════════════════════════════════════════════
When NO KP analysis is provided in technical points:
- **Fall back to pure Vedic analysis**
- **Analysis split**: Vedic 85% + Dasha 10% + Aspects 5%
- Focus on house lord strength, placements, dignity, aspects
- More emphasis on dasha timing for event manifestation

VEDIC METHODOLOGY:
- House lord placements and dignity (exalted, debilitated, etc.)
- Dasha periods for timing windows
- Aspects and yogas for additional context
- **Vedic shows CAPACITY and OBSTACLES**, not concrete promises

TIMING ANALYSIS (For Timing Questions):
═══════════════════════════════════════════════════════
When timing windows are provided:
- **BEST WINDOW**: Highest astrological score (best planetary alignment)
- **NEAREST WINDOW**: Earliest favorable opportunity (soonest chance)
- Use BOTH windows in your timing analysis
- Explain WHY each window is favorable
- Give user choice between "wait for best" vs "act sooner"

KEY PROPERTY HOUSES: 4, 2, 11, 6, 8, 9, 12
- 4th: Property, land, home (PRIMARY)
- 2nd: Wealth, assets, family property
- 11th: Gains, fulfillment, achievement (PRIMARY)
- 6th: Loans, debts, EMI
- 8th: Sudden events, obstacles, inheritance
- 9th: Fortune, luck, blessings
- 12th: Expenses, losses, foreign land

CRITICAL DASHA HANDLING RULES (PREVENT HALLUCINATION):
═══════════════════════════════════════════════════════
⚠️ NEVER make up or assume dasha periods
✅ ONLY reference dasha periods from CURRENT/UPCOMING sections provided
✅ Use exact dasha names and dates from the timeline
✅ COPY dasha names EXACTLY as provided - do not translate incorrectly
❌ DO NOT say "Currently Rahu dasha" unless explicitly stated in the data
❌ DO NOT invent future dashas not in the timeline
❌ DO NOT confuse Mercury (बुध) with Mars (मंगल) - THEY ARE DIFFERENT!
✅ Always say: "Based on the dasha timeline provided..."
✅ Always say: "According to current dasha analysis..."

⚠️ BEFORE WRITING ANY DASHA IN HINDI, VERIFY:
- Mercury = बुध (Me)
- Mars = मंगल (Ma)
- These are DIFFERENT planets! Do not mix them up!

CRITICAL TIMING WINDOW RULES (For Timing Questions):
⚠️ ALWAYS mention BOTH best and nearest windows when provided
✅ Explain the difference between the two options
✅ Let user decide based on their urgency vs quality preference
❌ DO NOT only mention one window and ignore the other
✅ Give specific dates from the timing data

CRITICAL OUTPUT FORMAT:
1. GENERAL ANSWER: Start with YES/NO/MODERATE verdict. NO astrological terms!
2. ASTROLOGICAL ANALYSIS: ALL technical details here
3. DASHA TIMING ANALYSIS: Current + Upcoming dasha analysis
4. SUMMARY: Actionable with specific timing
"""

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (NEW!)
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
            "-cusp", "ruling planet", "kp", "property",
            "4th cusp", "11th cusp", "2nd cusp", "house purchase"
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
        lines.append("⚠️ IMPORTANT: KP analysis provides PRECISE predictions.")
        lines.append("Give 30% weight to KP findings in your analysis.")
        lines.append("KP shows CONCRETE promises for property acquisition.")
        lines.append("")
        
        for point in kp_points:
            if not point.strip().startswith(("•", "-", "✓", "❌", "⚠", "❓", "⭐")):
                lines.append(f"  • {point}")
            else:
                lines.append(f"  {point}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines), True

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows from additional_data (NEW!)
    # ------------------------------------------------------------------
    def _dasha_to_hindi(self, dasha_str: str) -> str:
        """Convert dasha string to Hindi"""
        if not dasha_str:
            return ""
        
        hindi_mapping = {
            'Saturn': 'शनि', 'Sun': 'सूर्य', 'Moon': 'चंद्र',
            'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु',
            'Venus': 'शुक्र', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        
        # Parse dasha (format: "Saturn-Mercury-Jupiter")
        parts = dasha_str.replace(" > ", "-").replace(">", "-").split("-")
        hindi_parts = []
        
        for part in parts:
            part = part.strip()
            hindi_parts.append(hindi_mapping.get(part, part))
        
        return "-".join(hindi_parts)
    
    def _format_kp_csl_summary(self, additional_data: Dict) -> str:
        """
        Format KP Cusp Sub Lord summary as explicit reference table.
        This prevents LLM from hallucinating CSL planets.
        
        Returns:
            Formatted string with explicit CSL reference
        """
        if not additional_data:
            return self._get_no_kp_csl_warning()
        
        kp_data = additional_data.get("kp_property_analysis", {})
        
        if not kp_data or not kp_data.get("has_kp_data"):
            return self._get_no_kp_csl_warning()
        
        csl_details = kp_data.get("csl_details", {})
        
        if not csl_details:
            return self._get_no_kp_csl_warning()
        
        # Hindi planet mapping
        hindi_mapping = {
            'Saturn': 'शनि', 'Sun': 'सूर्य', 'Moon': 'चंद्र',
            'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु',
            'Venus': 'शुक्र', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  📍 KP CUSP SUB LORD REFERENCE - USE THIS EXACT DATA (DO NOT HALLUCINATE!)   ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("⚠️ CRITICAL: ONLY mention CSL if listed below. If house not listed, say 'unavailable'")
        lines.append("")
        lines.append("  ┌─────────┬────────────────────┬────────────────────┬────────────────┐")
        lines.append("  │ House   │ CSL (English)      │ CSL (Hindi)        │ Verdict        │")
        lines.append("  ├─────────┼────────────────────┼────────────────────┼────────────────┤")
        
        for house_num in sorted(csl_details.keys()):
            info = csl_details[house_num]
            csl_english = info.get('csl', 'Unknown')
            csl_hindi = hindi_mapping.get(csl_english, csl_english)
            verdict = info.get('verdict', 'NEUTRAL')
            house_meaning = info.get('house_meaning', '')
            
            house_col = f"{house_num} ({house_meaning[:8]})" if house_meaning else str(house_num)
            house_col = house_col.ljust(7)
            csl_eng_col = csl_english.ljust(18)
            csl_hindi_col = csl_hindi.ljust(18)
            verdict_col = verdict.ljust(14)
            
            lines.append(f"  │ {house_col} │ {csl_eng_col} │ {csl_hindi_col} │ {verdict_col} │")
        
        lines.append("  └─────────┴────────────────────┴────────────────────┴────────────────┘")
        lines.append("")
        lines.append("⚠️ ANTI-HALLUCINATION RULES FOR CSL:")
        lines.append("  1. House 4 CSL is listed above - USE ONLY that planet, not any other")
        lines.append("  2. DO NOT say 'मंगल' (Mars) if the table shows 'Venus' (शुक्र)")
        lines.append("  3. DO NOT invent CSL for houses not in this table")
        lines.append("  4. If unsure, refer to THIS TABLE - it is the source of truth")
        lines.append("")
        
        # Add overall verdict
        overall = kp_data.get("overall_verdict", "")
        if overall:
            lines.append(f"📊 OVERALL KP VERDICT: {overall}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_no_kp_csl_warning(self) -> str:
        """Return warning when no KP CSL data is available"""
        return """
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️ KP CUSP SUB LORD DATA: NOT AVAILABLE                                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

KP Cusp Sub Lord analysis is NOT available for this question.

⚠️ CRITICAL ANTI-HALLUCINATION RULES:
1. DO NOT mention any Cusp Sub Lord (CSL) planets
2. DO NOT say "चतुर्थ भाव का कस्ट सब लॉर्ड मंगल है" or any similar statement
3. If you don't have KP data, say: "KP कस्ट सब लॉर्ड विश्लेषण उपलब्ध नहीं है"
4. Use ONLY Vedic Sign Lord analysis instead
5. Sign Lord ≠ Cusp Sub Lord - they are different concepts

Use Vedic analysis as primary (85% weight) when KP data is unavailable.
"""
    
    def _format_timing_windows_from_data(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows with KP Significator Proof for property.
        """
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return ""

        # ✅ NEW: Check for explicit no-windows flag
        if timing_windows_data.get('no_windows_found'):
        # Domain-specific context
            if self.subtopic == "Buying Home or Land":
                domain_context = "property acquisition"
            elif self.subtopic == "Marriage Prospects":
                domain_context = "marriage"
            elif self.subtopic == "Prospects Of Investments":
                domain_context = "major investments or asset acquisition"
            elif self.subtopic == "Job Change Prospects":
                domain_context = "job or career change"
            else:
                domain_context = "this event"
        
            return self._format_no_timing_windows_message(domain_context)
    
        # Check if has timing
        if not timing_windows_data.get('has_timing'):
            return ""
    
        
        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            property_proof = timing_windows_data.get('property_proof', {})
            
            if not best and not nearest:
                return ""
            
            lines = ["╔═══════════════════════════════════════════════════════════════════════════════╗"]
            lines.append("║  🏠 PROPERTY TIMING WINDOWS WITH KP SIGNIFICATOR PROOF                       ║")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # DASHA NAME REFERENCE (ANTI-HALLUCINATION)
            # ═══════════════════════════════════════════════════════════════════
            lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
            lines.append("║  ⚠️ CRITICAL: DASHA NAME REFERENCE - USE EXACT NAMES BELOW!                  ║")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")
            lines.append("  ┌────────────┬────────────┬─────────────────────────────────┐")
            lines.append("  │ English    │ Hindi      │ WARNING                         │")
            lines.append("  ├────────────┼────────────┼─────────────────────────────────┤")
            lines.append("  │ Mercury    │ बुध        │ ⚠️ NOT Mars! (Me ≠ Ma)          │")
            lines.append("  │ Mars       │ मंगल       │ ⚠️ NOT Mercury! (Ma ≠ Me)       │")
            lines.append("  │ Saturn     │ शनि        │                                 │")
            lines.append("  │ Jupiter    │ गुरु       │                                 │")
            lines.append("  │ Venus      │ शुक्र      │                                 │")
            lines.append("  │ Moon       │ चंद्र      │                                 │")
            lines.append("  │ Sun        │ सूर्य      │                                 │")
            lines.append("  │ Rahu       │ राहु       │                                 │")
            lines.append("  │ Ketu       │ केतु       │                                 │")
            lines.append("  └────────────┴────────────┴─────────────────────────────────┘")
            lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # KP SIGNIFICATOR TABLE (NEW!)
            # ═══════════════════════════════════════════════════════════════════
            if property_proof and property_proof.get('significator_table'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  📊 KP SIGNIFICATOR TABLE FOR PROPERTY TIMING                                ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append("  Houses for Property: 4 (property/land), 11 (gains), 2 (wealth)")
                lines.append("  Obstacle Houses: 6 (loans/debts), 8 (obstacles), 12 (losses)")
                lines.append("  Legend: O = Occupant, L = Lord, S = Star Lord signification")
                lines.append("")
                lines.append("  ┌────────────┬─────────────────────┬────────┬────────┬───────────────┐")
                lines.append("  │ Planet     │ Signifies 4/11/2    │ Promise│Obstacle│ Key Planet?   │")
                lines.append("  ├────────────┼─────────────────────┼────────┼────────┼───────────────┤")
                
                for entry in property_proof['significator_table'][:7]:  # Top 7 planets
                    planet = entry['planet'].ljust(10)
                    promise_houses = ', '.join(entry.get('signifies_4_11_2', ['None']))[:19].ljust(19)
                    promise_score = str(entry.get('promise_score', 0)).ljust(6)
                    obstacle_score = str(entry.get('obstacle_score', 0)).ljust(6)
                    is_key = "🏠 Property" if entry.get('is_property_karaka') else ("🌍 Land" if entry.get('is_land_karaka') else "○")
                    lines.append(f"  │ {planet} │ {promise_houses} │ {promise_score} │ {obstacle_score} │ {is_key.ljust(13)} │")
                
                lines.append("  └────────────┴─────────────────────┴────────┴────────┴───────────────┘")
                lines.append("")
                lines.append("  📖 How to read: Higher Promise score + Lower Obstacle = better for property")
                lines.append("     Key: Mars (property karaka), Saturn (land/real estate karaka)")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # TIMING PROOF (WHY THIS DASHA ACTIVATES PROPERTY PURCHASE)
            # ═══════════════════════════════════════════════════════════════════
            if property_proof and property_proof.get('timing_proofs'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  📊 DASHA HOUSE LINKAGE PROOF (Why these periods favor property purchase)    ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                
                for proof in property_proof['timing_proofs'][:3]:  # Top 3 proofs
                    strength_icon = "🟢" if proof.get('promise_strength') == "STRONG" else ("🟡" if proof.get('promise_strength') == "MODERATE" else "🟠")
                    lines.append(f"  {strength_icon} {proof['dasha']} ({proof['period']})")
                    lines.append(f"     Score: {proof['score']:.1f}/100 | Strength: {proof.get('promise_strength', 'N/A')}")
                    
                    if proof.get('house_linkage'):
                        lines.append(f"     House Activation:")
                        for linkage in proof['house_linkage']:
                            lines.append(f"       • {linkage}")
                    
                    if proof.get('dasha_lords'):
                        lines.append(f"     Dasha Lord Significations:")
                        for lord in proof['dasha_lords']:
                            if lord.get('signifies_promise_houses'):
                                how_str = "; ".join(lord.get('how', [])[:2])
                                lines.append(f"       • {lord['planet']}: signifies houses {lord['signifies_promise_houses']} ({how_str})")
                    
                    # Mars and Saturn involvement
                    karaka_status = []
                    if proof.get('mars_involved'):
                        karaka_status.append("Mars (property karaka)")
                    if proof.get('saturn_involved'):
                        karaka_status.append("Saturn (land karaka)")
                    
                    if karaka_status:
                        lines.append(f"     ✅ Key planets involved: {', '.join(karaka_status)}")
                    else:
                        lines.append(f"     ○ No direct Mars/Saturn involvement")
                    
                    lines.append("")
                
                lines.append("  💡 IMPORTANT: Periods with 4/11/2 house activation favor property purchase")
                lines.append("     Mars or Saturn involvement strengthens property timing further")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # BEST WINDOW
            # ═══════════════════════════════════════════════════════════════════
            if best:
                best_dasha = best.get('dasha', 'N/A')
                best_dasha_hindi = self._dasha_to_hindi(best_dasha)
                
                lines.append("🏆 BEST WINDOW (Highest Property Score):")
                lines.append("-" * 70)
                lines.append(f"  Dasha Period (English): {best_dasha}")
                lines.append(f"  Dasha Period (Hindi):   {best_dasha_hindi}")
                lines.append(f"  ⚠️ USE THESE EXACT NAMES - DO NOT CONFUSE Mercury(बुध) with Mars(मंगल)!")
                lines.append(f"  Start Date: {best.get('start', 'N/A')} (USE EXACT DATE)")
                lines.append(f"  End Date: {best.get('end', 'N/A')} (USE EXACT DATE)")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                if best.get('age_at_start'):
                    lines.append(f"  Age at Start: {best.get('age_at_start', 'N/A')} years")
                if best.get('transit_score'):
                    lines.append(f"  Transit Support: {best.get('transit_score', 0):.1f}%")
                lines.append("")
                lines.append("  Why BEST: Strongest 4/11/2 house activation for property")
                lines.append("  Trade-off: May be further in future")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # NEAREST WINDOW
            # ═══════════════════════════════════════════════════════════════════
            if nearest:
                nearest_dasha = nearest.get('dasha', 'N/A')
                nearest_dasha_hindi = self._dasha_to_hindi(nearest_dasha)
                
                lines.append("⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):")
                lines.append("-" * 70)
                lines.append(f"  Dasha Period (English): {nearest_dasha}")
                lines.append(f"  Dasha Period (Hindi):   {nearest_dasha_hindi}")
                lines.append(f"  ⚠️ USE THESE EXACT NAMES - DO NOT CONFUSE Mercury(बुध) with Mars(मंगल)!")
                lines.append(f"  Start Date: {nearest.get('start', 'N/A')} (USE EXACT DATE)")
                lines.append(f"  End Date: {nearest.get('end', 'N/A')} (USE EXACT DATE)")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                if nearest.get('age_at_start'):
                    lines.append(f"  Age at Start: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")
                
                # Check if best and nearest are the same
                if best and (best.get('dasha') == nearest.get('dasha') and 
                            best.get('start') == nearest.get('start')):
                    lines.append("  ✅ EXCELLENT! Best and Nearest windows are THE SAME!")
                    lines.append("     Optimal timing AND early opportunity coincide!")
                else:
                    lines.append("  Why NEAREST: Earliest window with favorable 4/11/2 activation")
                    lines.append("  Trade-off: Not the absolute best alignment")
                lines.append("")
            
            # ═══════════════════════════════════════════════════════════════════
            # OTHER WINDOWS
            # ═══════════════════════════════════════════════════════════════════
            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (for reference):")
                lines.append("-" * 70)
                for i, window in enumerate(all_windows[:5], 1):
                    if window == best:
                        marker = "🏆"
                    elif window == nearest:
                        marker = "⏰"
                    else:
                        marker = f"{i}."
                    lines.append(f"  {marker} {window.get('dasha', 'N/A')}: {window.get('start', 'N/A')} to {window.get('end', 'N/A')} (Score: {window.get('final_score', 0):.1f})")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("📝 TIMING RESPONSE REQUIREMENTS:")
            lines.append("- MUST mention BOTH best and nearest windows with EXACT dates")
            lines.append("- MUST explain WHY the dasha is suitable using house signification (4/11/2)")
            lines.append("- Show KP proof: which dasha lords signify property houses and HOW")
            lines.append("- Mention Mars/Saturn involvement if present")
            lines.append("- Explain the trade-off between waiting vs acting sooner")
            lines.append("- DO NOT invent additional timing periods")
            lines.append("")
            lines.append("⚠️ CRITICAL ANTI-HALLUCINATION RULES FOR DASHA NAMES:")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("1. Mercury = बुध (NOT मंगल!)")
            lines.append("2. Mars = मंगल (NOT बुध!)")
            lines.append("3. COPY the exact dasha name from BEST/NEAREST sections above")
            lines.append("4. DO NOT translate incorrectly - check the reference table")
            lines.append("5. If writing in Hindi, verify: Mercury→बुध, Mars→मंगल")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""




    def _format_no_timing_windows_message(self, domain_context: str = "this event") -> str:
        """
        Format message when KP timing engine found no favorable windows.
        
        Args:
            domain_context: Specific event type (e.g., "property acquisition", "marriage", "job change")
        """
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("⚠️ KP TIMING ANALYSIS - NO FAVORABLE WINDOWS DETECTED")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("🔍 CRITICAL FINDING:")
        lines.append(f"The KP (Krishnamurti Paddhati) timing engine has analyzed")
        lines.append(f"all dasha periods over the next 10 years and found NO")
        lines.append(f"clearly favorable timing windows for {domain_context}")
        lines.append(f"based on cusp sub lord significations.")
        lines.append("")
        lines.append("⚠️ WHAT THIS MEANS:")
        lines.append("- KP analysis did not identify periods with strong planetary support")
        lines.append("- The relevant cusp sub lords do not form favorable significations")
        lines.append("- This suggests significant obstacles or the need for foundational work")
        lines.append("")
        lines.append("📋 INSTRUCTIONS FOR YOUR RESPONSE:")
        lines.append("")
        lines.append("1. START with clear statement:")
        lines.append("   'Based on KP analysis, no clearly favorable timing windows were")
        lines.append("   detected for [event] in the next 10 years.'")
        lines.append("")
        lines.append("2. EXPLAIN the astrological reasons:")
        lines.append("   - Which cusp sub lords are involved")
        lines.append("   - Why their significations are not favorable")
        lines.append("   - What house combinations are lacking")
        lines.append("")
        lines.append("3. BE CONSTRUCTIVE, NOT PESSIMISTIC:")
        lines.append("   ✅ DO: Explain this means careful preparation is needed")
        lines.append("   ✅ DO: Suggest remedies and alternative approaches")
        lines.append("   ✅ DO: Frame as 'not now' rather than 'never'")
        lines.append("   ❌ DON'T: Be doom-and-gloom or completely negative")
        lines.append("   ❌ DON'T: Make up timing windows that don't exist")
        lines.append("   ❌ DON'T: Ignore this finding and give false hope")
        lines.append("")
        lines.append("4. PROVIDE ACTIONABLE GUIDANCE:")
        lines.append("   - Focus on strengthening relevant house lords")
        lines.append("   - Suggest building foundational factors first")
        lines.append("   - Recommend patience and proper preparation")
        lines.append("   - Offer practical alternatives if applicable")
        lines.append("")
        lines.append("5. USE CURRENT DASHA ANALYSIS:")
        lines.append("   - Explain current period's challenges")
        lines.append("   - Mention upcoming periods and their limitations")
        lines.append("   - But emphasize NO period shows strong KP support")
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format house lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Property Houses)")
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
                conditions.append("⚠️ COMBUST (weakened by Sun)")
            if info['lord_is_retrograde']:
                conditions.append("🔄 RETROGRADE")
            
            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")
            
            if info['planets_in_house']:
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")
            
            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports property acquisition")
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
        lines.append("PLANETARY ASPECTS ON PROPERTY HOUSES")
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
                    lines.append(f"     → Positive influence, support, growth")
                
                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")
                    lines.append(f"     → Challenges, delays, obstacles")
                
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

    def _format_house_config(self, house_config: Dict) -> str:
        """Format house configuration"""
        if not house_config:
            return ""
        
        primary = sorted(house_config.get("primary", []))
        secondary = sorted(house_config.get("secondary", []))
        source = house_config.get("source", "unknown")
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("HOUSES ANALYZED FOR THIS QUESTION")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"⭐ PRIMARY houses (most important): {primary}")
        lines.append(f"   These directly signify the main topic of the question")
        lines.append("")
        lines.append(f"○ SECONDARY houses (supporting): {secondary}")
        lines.append(f"   These provide additional context and influences")
        lines.append("")
        lines.append(f"Configuration source: {source}")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """Format current dasha information for LLM with STRICT anti-hallucination"""
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
            
            # Hindi mapping for verification
            hindi_mapping = {
                'Saturn': 'शनि', 'Sun': 'सूर्य', 'Moon': 'चंद्र',
                'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु/बृहस्पति',
                'Venus': 'शुक्र', 'Rahu': 'राहु', 'Ketu': 'केतु'
            }
            
            parts = dasha_name.split('-') if '-' in dasha_name else dasha_name.split('>') if '>' in dasha_name else [dasha_name]
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts]
            formatted_dasha = ' > '.join(full_names) if len(full_names) >= 2 else dasha_name
            
            # Create Hindi version
            hindi_names = [hindi_mapping.get(name, name) for name in full_names]
            formatted_dasha_hindi = ' > '.join(hindi_names)
            
            lines = [
                "╔═══════════════════════════════════════════════════════════════════════════════╗",
                "║  ⚠️ CURRENT DASHA - MANDATORY REFERENCE (DO NOT HALLUCINATE!)                ║",
                "╚═══════════════════════════════════════════════════════════════════════════════╝",
                "",
                f"  🔴 CURRENT DASHA (English): {formatted_dasha}",
                f"  🔴 CURRENT DASHA (Hindi):   {formatted_dasha_hindi}",
                f"  📅 Period: {start} to {end}",
                "",
                "╔═══════════════════════════════════════════════════════════════════════════════╗",
                "║  📚 PLANET NAME REFERENCE (USE THIS - DO NOT CONFUSE!)                        ║",
                "╚═══════════════════════════════════════════════════════════════════════════════╝",
                "",
                "  ┌────────────┬────────────┬────────────────────────────────────────┐",
                "  │ English    │ Hindi      │ CRITICAL: Do NOT confuse!             │",
                "  ├────────────┼────────────┼────────────────────────────────────────┤",
                "  │ Mercury    │ बुध        │ ⚠️ NOT Mars! Mercury = बुध            │",
                "  │ Mars       │ मंगल       │ ⚠️ NOT Mercury! Mars = मंगल           │",
                "  │ Saturn     │ शनि        │                                        │",
                "  │ Jupiter    │ गुरु/बृहस्पति │                                        │",
                "  │ Venus      │ शुक्र      │                                        │",
                "  │ Sun        │ सूर्य      │                                        │",
                "  │ Moon       │ चंद्र      │                                        │",
                "  │ Rahu       │ राहु       │                                        │",
                "  │ Ketu       │ केतु       │                                        │",
                "  └────────────┴────────────┴────────────────────────────────────────┘",
                "",
                "⚠️ ANTI-HALLUCINATION RULES:",
                f"  1. The CURRENT dasha is: {formatted_dasha} ({formatted_dasha_hindi})",
                "  2. DO NOT change Mercury to Mars or vice versa",
                "  3. COPY the exact dasha name from this section",
                "  4. If unsure, use the English name from TIMING WINDOWS",
                "",
                "═══════════════════════════════════════════════════════════════════════════════"
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
                lines.append("Use these periods for long-term property planning:")
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
            lines.append("- CURRENT: Use for present circumstances and immediate timing")
            lines.append("- RECENT PAST: Context for recent property-related events")
            lines.append("- UPCOMING: Make future property purchase recommendations")
            lines.append("- Jupiter/Venus periods generally favorable for property")
            lines.append("- Saturn periods may bring delays but eventual success")
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
        KP weight is 30% when available.
        """
        if kp_available:
            if question_type == "purchase" and has_timing:
                return """
**ANALYSIS APPROACH: VEDIC (55%) + KP (30%) + DASHA (10%) + ASPECTS (5%) + TIMING**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with Vedic House Lords Analysis** (PRIMARY - 55% weight):
   - 4th house lord strength (property/land) - CRITICAL
   - 11th house lord strength (gains/fulfillment) - CRITICAL
   - 2nd house lord (wealth/assets)
   - 6th house (loans if applicable)
   - Vedic shows CAPACITY for property acquisition
   - Aspects on the respective houses
   - Planets in the respective houses and their state like maelfix, beenfic (computed correclty) and their infleuence

2. **ADD KP System Analysis** (SECONDARY - 25% weight):
   - What does the 4th cusp sub lord signify? (property)
   - What does the 11th cusp sub lord signify? (gains)
   - Does 4th CSL connect to 4-11 for property acquisition?
   - KP verdict: Clear promise for property ownership?

3. **TIMING ANALYSIS** (10% weight - CRITICAL FOR THIS QUESTION):
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

4. **Aspects & Other Factors** (5% weight):
   - Benefic/malefic aspects on 4th, 11th houses
   - Special yogas if present

5. **Synthesize**:
   - Combine Vedic capacity + KP promise + Timing windows for final recommendation
"""
            elif question_type == "risks":
                return """
**ANALYSIS APPROACH: VEDIC (55%) + KP (30%) + DASHA (10%) + ASPECTS (5%)**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with Vedic House Lords Analysis** (PRIMARY - 55% weight):
   - Weak 4th house lord: Property acquisition challenges
   - Strong 6th house: Heavy debt burden
   - Strong 8th house: Sudden problems, disputes
   - Strong 12th house: Excessive expenses, losses
   - Aspects on the respective houses
   - Planets in the respective houses and their state like maelfix, beenfic (computed correclty) and their infleuence
   - Vedic shows WHERE challenges lie

2. **ADD KP System Analysis** (SECONDARY - 25% weight):
   - What does the 4th cusp sub lord signify?
   - Does it connect to 6-8-12 (obstacles)?
   - KP verdict: Specific risks indicated?

3. **Include Dasha Timing** (10% weight):
   - Current dasha: Risk level NOW
   - Upcoming weak dashas: When to avoid
   - Upcoming favorable dashas: When risks reduce

4. **Aspects** (5% weight):
   - Malefic aspects on 4th, 11th
   - Saturn/Mars influence
"""
            else:
                return """
**ANALYSIS APPROACH: VEDIC (55%) + KP (30%) + DASHA (10%) + ASPECTS (5%)**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with Vedic House Lords Analysis** (PRIMARY - 55% weight)
2. **ADD KP System Analysis** (SECONDARY - 30% weight)
3. **Include Dasha Timing** (10% weight)
4. **Consider Aspects** (5% weight)
"""
        else:
            # Pure Vedic fallback
            if has_timing:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM + TIMING (KP Not Available)**

⚠️ NOTE: No KP Cusp Sub Lord analysis available.
Proceeding with comprehensive Vedic analysis.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 85% weight):
   - Detailed analysis of 4th house lord (property)
   - 11th house lord (gains/fulfillment)
   - 2nd house (wealth), 6th (loans), etc.
   - Strength assessment for each

2. **TIMING ANALYSIS** (10% weight - CRITICAL):
   ⚠️ MUST analyze BOTH timing windows:
   
   A. BEST WINDOW: When + Why + Trade-off
   B. NEAREST WINDOW: When + Why + Trade-off
   C. USER CHOICE: Wait vs Act sooner
   
   ⚠️ If best = nearest: Ideal timing!

3. **Aspects & Final Verdict** (5% weight):
   - Clear recommendation with specific dates
"""
            else:
                return """
**ANALYSIS APPROACH: VEDIC SYSTEM (KP Not Available)**

⚠️ NOTE: No KP analysis available.

**FOLLOW THIS ORDER:**

1. **Vedic House Lord Analysis** (PRIMARY - 85% weight)
2. **Dasha Timing** (10% weight)
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

        if "Property Purchase" in sub_subdomain or "Prospects of Property" in sub_subdomain:
            return self._build_purchase_prompt(
                question, technical_points, meta, timing_windows, language, **kwargs)
        elif "Property Risks" in sub_subdomain:
            return self._build_risk_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Vastu" in sub_subdomain:
            return self._build_vastu_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_property_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # PROPERTY PURCHASE - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific analysis points DETERMINISTICALLY.
        
        ENHANCED v2.0:
        - PRIMARY: Extract from structured kp_property_analysis (deterministic!)
        - FALLBACK: Keyword matching from technical_points
        
        Returns:
            Tuple of (formatted_text, kp_available)
        """
        # ═══════════════════════════════════════════════════════════════
        # PRIMARY: Extract from structured KP data (DETERMINISTIC!)
        # ═══════════════════════════════════════════════════════════════
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_property_analysis", {})
        
        # If we have structured KP data, use it!
        if kp_structured and kp_structured.get("has_kp_data"):
            lines = ["═══════════════════════════════════════════════════════"]
            lines.append("⭐ KP SYSTEM ANALYSIS (Cusp Sub Lords & Significations)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ IMPORTANT: KP analysis provides PRECISE predictions.")
            lines.append("Give 30% weight to KP findings in your analysis.")
            lines.append("KP shows CONCRETE promises for property acquisition.")
            lines.append("")
            
            # Format CSL details
            csl_details = kp_structured.get("csl_details", {})
            if csl_details:
                lines.append("📍 CUSP SUB LORD ANALYSIS:")
                lines.append("")
                
                for house_num in sorted(csl_details.keys()):
                    csl_info = csl_details[house_num]
                    
                    house_meaning = csl_info.get("house_meaning", "Property")
                    csl = csl_info.get("csl", "Unknown")
                    cusp_sign = csl_info.get("cusp_sign", "")
                    verdict = csl_info.get("verdict", "NEUTRAL")
                    interpretation = csl_info.get("interpretation", "")
                    is_benefic = csl_info.get("is_benefic", False)
                    is_malefic = csl_info.get("is_malefic", False)
                    
                    # Verdict marker
                    if verdict in ["PROMISED", "EXCELLENT", "FAVORABLE", "CONTROLLED"]:
                        marker = "✅"
                    elif verdict in ["DELAYED", "CHALLENGING", "WEAK", "EXCESSIVE"]:
                        marker = "⚠️"
                    else:
                        marker = "○"
                    
                    lines.append(f"{marker} House {house_num} ({house_meaning}):")
                    lines.append(f"   Cusp Sub Lord: {csl}")
                    if cusp_sign:
                        lines.append(f"   Cusp in Sign: {cusp_sign}")
                    lines.append(f"   Nature: {'Benefic' if is_benefic else 'Malefic' if is_malefic else 'Neutral'}")
                    lines.append(f"   Verdict: {verdict}")
                    
                    if interpretation:
                        lines.append(f"   Analysis: {interpretation}")
                    
                    lines.append("")
            
            # Overall verdict
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            if overall != "UNKNOWN":
                lines.append(f"📊 OVERALL KP VERDICT: {overall}")
                lines.append("")
                
                if overall == "STRONG_PROMISE":
                    lines.append("   ✅ Strong KP indicators for property acquisition")
                elif overall == "BLOCKED":
                    lines.append("   ⚠️ KP shows significant obstacles and delays")
                elif overall == "MODERATE_WITH_DELAYS":
                    lines.append("   ⚖️ Property possible but with delays")
                elif overall == "MODERATE_WITH_OBSTACLES":
                    lines.append("   ⚖️ Property possible but challenges in fulfillment")
                else:
                    lines.append("   ○ Mixed KP indicators - careful assessment needed")
                
                lines.append("")
            
            # Key findings
            key_findings = kp_structured.get("key_findings", [])
            if key_findings:
                lines.append("🔑 KEY KP FINDINGS:")
                for finding in key_findings[:6]:  # Limit to top 6
                    lines.append(f"   • {finding}")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("⚠️ INSTRUCTIONS FOR KP INTERPRETATION:")
            lines.append("")
            lines.append("VERDICT Meanings:")
            lines.append("  • PROMISED: Strong property acquisition indicated")
            lines.append("  • EXCELLENT: Very favorable for fulfillment")
            lines.append("  • FAVORABLE: Good support for property matters")
            lines.append("  • DELAYED: Property possible but with time delays")
            lines.append("  • CHALLENGING: Obstacles in achievement")
            lines.append("  • NEUTRAL: Mixed or neutral indicators")
            lines.append("")
            lines.append("OVERALL VERDICT:")
            lines.append("  • STRONG_PROMISE: High probability of property acquisition")
            lines.append("  • MODERATE: Mixed indicators, requires careful planning")
            lines.append("  • BLOCKED: Significant obstacles, may need long delays")
            lines.append("")
            lines.append("YOU MUST:")
            lines.append("  1. Start with Vedic analysis (PRIMARY - 55% weight)")
            lines.append("  2. Use KP for precision and confirmation (SECONDARY - 30% weight)")
            lines.append("  3. State the KP verdict for each relevant house (4, 11, 2, 12)")
            lines.append("  4. Explain what each CSL indicates for property")
            lines.append("  5. Connect KP findings with Vedic house lord analysis")
            lines.append("  6. If KP and Vedic agree → Strong conclusion")
            lines.append("  7. If KP and Vedic differ → Vedic takes priority, mention divergence")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines), True
        
        # ═══════════════════════════════════════════════════════════════
        # FALLBACK: Extract from technical_points (less reliable)
        # ═══════════════════════════════════════════════════════════════
        if not technical_points:
            return "", False
        
        kp_keywords = [
            "kp:", "cusp", "sub-lord", "sub lord", "csl",
            "signif", "connects to", "connect", "promise",
            "-cusp", "ruling planet", "kp", "property",
            "4th cusp", "11th cusp", "2nd cusp", "house purchase"
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
        lines.append("⚠️ IMPORTANT: Use KP for precision (30% weight) alongside Vedic analysis (55% weight).")
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
    # PROPERTY PURCHASE - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _build_purchase_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]],
        language: str = "Hindi",
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_and_property"
        
        house_config = additional_data.get(f"{domain_prefix}_house_config", {})
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Get timing windows from additional_data
        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)
        no_timing_found = timing_windows_data.get('no_windows_found', False)  # ← NEW
        # Format timing windows (will handle no-windows case internally)
        timing_formatted = self._format_timing_windows_from_data(timing_windows_data)
    
        
        # ✅ NEW: Format KP analysis (pass additional_data for deterministic extraction)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        # ✅ NEW: Format KP CSL summary for explicit reference
        kp_csl_summary = self._format_kp_csl_summary(additional_data)
        
        # Format Vedic data
        config_formatted = self._format_house_config(house_config)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        
        # ✅ NEW: Format timing windows from additional_data
        timing_formatted = self._format_timing_windows_from_data(timing_windows_data)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        # Get remaining non-KP points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet", "property", "house purchase"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        # ✅ NEW: Get analysis instructions based on KP availability + timing
        analysis_instructions = self._get_analysis_instructions(kp_available, "purchase", has_timing)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Buying Home Or Land
- Sub-subdomain: Property Purchase
- Query Type: TIMING
- Event Polarity: POSITIVE
- Interpretation Goal: MANIFESTATION
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}
- Timing Windows Available: {'YES' if has_timing else 'NO'}

USER QUESTION:
"{question}"

{kp_csl_summary}

{timing_formatted}

{kp_formatted}

{config_formatted}

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
{'- Explain why each window is favorable for property' if has_timing else ''}
{'- Let user choose: wait for best OR act sooner' if has_timing else ''}
{'- If best = nearest, emphasize this is ideal timing' if has_timing else ''}

GUIDELINES:
- Focus on PROPERTY ACQUISITION prospects
- 4th house = property/land (CRITICAL)
- 11th house = gains/fulfillment (CRITICAL)
- {'Use timing windows for SPECIFIC purchase dates!' if has_timing else 'Use dasha timeline for timing'}

{self.get_output_format(kp_available, has_timing,no_timing_found)}
"""




    # ------------------------------------------------------------------
    # PROPERTY RISKS - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _build_risk_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi",
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_and_property"
        
        house_config = additional_data.get(f"{domain_prefix}_house_config", {})
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        
        # Format Vedic data
        config_formatted = self._format_house_config(house_config)
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
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "risks", False)
        
        # ✅ NEW: Format KP CSL summary for explicit display
        kp_csl_summary = self._format_kp_csl_summary(additional_data)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Buying Home Or Land
- Sub-subdomain: Property Risks
- Query Type: NON_TIMING
- Event Polarity: NEGATIVE
- Interpretation Goal: RISK
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_csl_summary}

{kp_formatted}

{config_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️ CRITICAL: DO NOT HALLUCINATE KP CUSP SUB LORDS!                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1. ONLY mention CSL if data is provided in "KP CUSP SUB LORD REFERENCE" above
2. If no KP data is provided, say "KP विश्लेषण उपलब्ध नहीं है"
3. DO NOT make up or assume CSL planets - they must come from the data
4. If you don't see the exact CSL name in the data, DO NOT mention it
5. Use Vedic Sign Lord analysis as primary if KP data is missing

GUIDELINES:
- Focus on RISK assessment for property
- 6th house = loans/debts
- 8th house = sudden problems
- 12th house = expenses/losses
- Provide constructive guidance with timing

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # VASTU - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _build_vastu_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi",
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_and_property"
        
        house_config = additional_data.get(f"{domain_prefix}_house_config", {})
        
        config_formatted = self._format_house_config(house_config)

        # Extract and format dasha context
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Finance
- Subtopic: Buying Home Or Land
- Sub-subdomain: Vastu Guidance
- Query Type: NON_TIMING
- Event Polarity: NEUTRAL
- Interpretation Goal: STATUS
- CURRENT DATE: {today}

USER QUESTION:
"{question}"

{config_formatted}

{current_dasha_block}

{timeline_block}

NOTE ON VASTU ANALYSIS:
This question focuses on Vastu (directional) guidance for property layout and planning.
While astrological houses provide context (e.g., 4th house condition), the main guidance
should be practical Vastu principles for:
- Plot/house orientation
- Main entrance direction
- Room placement
- Kitchen, bedroom, and prayer room locations
- Avoiding Vastu defects

═══════════════════════════════════════════════════════
VASTU GUIDANCE INSTRUCTIONS
═══════════════════════════════════════════════════════

1. PROVIDE PRACTICAL GUIDANCE:
   - Focus on actionable Vastu tips
   - Avoid overly complex or ritualistic requirements
   - Keep suggestions realistic and affordable

2. KEY VASTU AREAS:
   - Main entrance (preferred directions)
   - Master bedroom placement
   - Kitchen location
   - Prayer/puja room
   - Bathroom/toilet positions
   - Water sources

3. BE HELPFUL:
   - Prioritize most important Vastu factors
   - Suggest remedies for existing defects
   - Explain WHY certain directions are beneficial

{self.get_output_format(False, False)}
"""

    # ------------------------------------------------------------------
    # REMEDIES - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _build_remedies_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi",
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_and_property"
        
        house_config = additional_data.get(f"{domain_prefix}_house_config", {})
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        
        # Format Vedic data
        config_formatted = self._format_house_config(house_config)
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
- Subtopic: Buying Home Or Land
- Sub-subdomain: Remedies
- Query Type: NON_TIMING
- Event Polarity: POSITIVE
- Interpretation Goal: MANIFESTATION
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{config_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

═══════════════════════════════════════════════════════
REMEDY RECOMMENDATION INSTRUCTIONS
═══════════════════════════════════════════════════════

WEIGHTAGE DISTRIBUTION (WITH KP):
- VEDIC ANALYSIS: 55% weight
- KP ANALYSIS: 20% weight
- DASHA PERIODS: 20% weight
- ASPECTS: 5% weight

1. IDENTIFY WEAK AREAS NEEDING REMEDIES:
   - Weak 4th house lord: Strengthen property prospects
   - Weak 2nd house lord: Improve financial capacity
   - Weak 11th house lord: Enhance gains and fulfillment
   {'- Weak KP cusp sub lords' if kp_available else ''}

2. DASHA-BASED REMEDIES:
   ⚠️ ONLY reference dasha periods from CURRENT/UPCOMING sections above
   - Current weak dasha lord: Strengthen through remedies
   - Upcoming strong dasha: Prepare to maximize benefits
   - DO NOT make up dasha periods

3. PLANETARY REMEDIES (Prioritize):
   - For weak lords: Gemstones, mantras, donations
   - For combust planets: Specific remedies to reduce combustion
   - For malefic aspects: Pacification of malefic planets

4. PRACTICAL REMEDIES:
   - Financial planning and savings
   - Legal documentation verification
   - Timing purchases during favorable dasha windows

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK - ENHANCED v5.0
    # ------------------------------------------------------------------
    def _build_general_property_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi",
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        # Extract enhanced data
        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "finance_and_property"
        
        house_config = additional_data.get(f"{domain_prefix}_house_config", {})
        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})
        
        # ✅ NEW: Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points,additional_data)
        
        # Format Vedic data
        config_formatted = self._format_house_config(house_config)
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
- Domain: Finance and Property
- Subtopic: Buying Home or Land
- Query Type: {meta.query_type.value if meta else 'UNKNOWN'}
- Event Polarity: {meta.polarity.value if meta else 'UNKNOWN'}
- Interpretation Goal: {meta.goal.value if meta else 'UNKNOWN'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}

USER QUESTION:
"{question}"

{kp_formatted}

{config_formatted}

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
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False,no_timing_found: bool = False) -> str:
        """Generate output format based on KP availability and timing windows"""
        

        # ✅ NEW: Special format for no timing windows case
        if no_timing_found:
            return """
      OUTPUT FORMAT (NO TIMING WINDOWS FOUND):

      GENERAL_ANSWER:
      ⚠️ Based on KP (Krishnamurti Paddhati) analysis, no clearly favorable timing 
      windows were detected for this event in the next 10 years. This suggests [brief 
      explanation - be constructive, not overly negative].

      ASTROLOGICAL_ANALYSIS:

      **KP SYSTEM FINDINGS (Why No Windows):**
         - State which cusp sub lords were analyzed
         - Explain their significations (or lack thereof)
         - Explain why no favorable connections exist
         - Mention what house combinations are needed but absent

      **VEDIC SYSTEM CONTEXT:**
         - Analyze house lord positions and strengths
         - This provides supporting context for KP findings

      **DASHA ANALYSIS (Current Situation):**
         - Current dasha impact and why it's not favorable
         - Upcoming dashas and their limitations
         - Emphasize: Even during potentially better dashas, KP shows no strong support

      CONSTRUCTIVE GUIDANCE:

      **What This Means:**
      - Event may require several years of preparation
      - Foundational factors need strengthening first
      - This is guidance for timing, not impossibility

      **Recommended Approach:**
      1. STRENGTHEN FOUNDATIONS:
         - [Remedies for weak house lords]
         - [Practical steps to build prerequisites]

      2. ALTERNATIVE STRATEGIES:
         - [Modified approaches that might be more viable]
         - [Interim solutions while building strength]

      3. PATIENCE AND PREPARATION:
         - Focus on creating best conditions
         - Build financial/emotional/practical foundations
         - Right timing will emerge when preparation is complete

      REMEDIES_ASTROLOGICAL:
      - Strengthen [relevant house lords]
      - Worship/mantras for [specific planets]

      REMEDIES_GENERAL:
      - [Practical steps to improve prospects]
      - [Alternative approaches to consider]

      SUMMARY:
      Be honest but constructive. Frame as "not the right time yet" rather than "never."
      Focus on what user CAN do to improve their prospects.
      """

        timing_section = ""
        if has_timing:
            timing_section = """
TIMING_RECOMMENDATION:
⚠️ CRITICAL - MUST include BOTH timing options:

**BEST WINDOW (Highest Score):**
- Period: <exact dates from timing data>
- Dasha: <exact dasha name>
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
<Clear verdict in LAYMAN'S TERMS. Start with YES/NO/MODERATE. NO astrological terminology. 2-3 sentences max.>

ASTROLOGICAL_ANALYSIS:
⚠️ MUST include BOTH Vedic and KP analysis:

**A. VEDIC SYSTEM ANALYSIS (Primary - 55% weight):**
   - House lords placement and dignity
   - 4th and 11th house lords especially
   - Overall strength assessment

**B. KP SYSTEM ANALYSIS (Secondary - 20% weight):**
   - State which cusp sub lords were analyzed
   - Mention exact significations
   - Clear KP verdict

**C. DASHA Analysis (20% weight):**
   - Current dasha impact
   - Upcoming periods influencing property

**D. ASPECTS (5% weight):**
   - Benefic/malefic on property houses
{timing_section}
SUMMARY:
<Short outlook with {' timing dates' if has_timing else 'dasha timing'}>

REMEDIES_ASTROLOGICAL:
- <Strengthen weak Vedic/KP lords>

REMEDIES_GENERAL:
- <Practical planning advice>
"""
        else:
            return f"""
OUTPUT FORMAT (STRICT):

GENERAL_ANSWER:
<Clear verdict in LAYMAN'S TERMS. Start with YES/NO/MODERATE. 2-3 sentences max.>

ASTROLOGICAL_ANALYSIS:
⚠️ Pure Vedic Analysis:

**A. VEDIC HOUSE LORD ANALYSIS (Primary - 85% weight):**
   - Detailed house lord analysis
   - Placement, dignity, strength
   - Clear assessment

**B. DASHA TIMING (10% weight):**
   - Current and upcoming periods

**C. ASPECTS (5% weight):**
   - Benefic/malefic aspects
{timing_section}
SUMMARY:
<Short outlook with {' timing dates' if has_timing else 'dasha timing'}>

REMEDIES_ASTROLOGICAL:
- <Strengthen weak Vedic lords>

REMEDIES_GENERAL:
- <Practical planning advice>
"""
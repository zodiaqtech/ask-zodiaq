"""
Career Discovery and Employment – LLM Prompts v10.0 (COMPLETE FIX)

CRITICAL FIXES FROM v9.0:
✅ UNIFIED VERDICT DISPLAY - Shows SAME career path across all questions
✅ PURE KP FORMATTING - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ HONEST VEDIC-KP AGREEMENT - Shows AGREEMENT/PARTIAL/CONFLICT explicitly
✅ CORRECT HOUSE DEFINITIONS - Service: 2,6,10,11 | Business: 2,3,7,11 (NOT 5,9)
✅ PROMISE/DENIAL LOGIC - Sub-lord decides, not planet nature
✅ NO FRACTION SCORING - Uses proper KP weight hierarchy (removed "3/5", "2/4")
✅ RAHU/KETU PROPER DISPLAY - Shows star lord significations
✅ CONSISTENT OUTPUT STRUCTURE - Same format across all questions
✅ REALISTIC TIMING GUIDANCE - Based on promise status
✅ ANTI-HALLUCINATION STRENGTHENED - Explicit rules against inventing data

Weightage (CORRECTED):
- KP Significations → 60% (PRIMARY)
- Vedic Structure → 30% (SECONDARY)
- Dasha/Other → 10%

Compatible with CareerDiscoveryAndEmploymentEvaluator v5.0 data structures:
- unified_career_verdict (SINGLE SOURCE OF TRUTH)
- kp_career_analysis (structured KP with CSL → Sub Lord chains)
- career_suitability_matrix (career path ratings)
- foreign_career_exposure (foreign/multinational analysis)
- career_role_resonance (KP profession mapping)
- career_service_vs_business (Service/Business/Mixed verdict)
- career_timing_windows (BEST + NEAREST)
- career_house_lords (Vedic house lord data)
- career_house_aspects (Vedic aspects)
- lagna_info (Ascendant information)
"""

from typing import Dict, List, Optional, Tuple
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
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "career"


class CareerDiscoveryAndEmploymentPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Career → Career Discovery And Employment
    v10.0 - Complete fix with unified verdict and pure KP methodology
    """

    domain = "Career"
    subtopic = "Career Discovery And Employment"

    # CORRECTED House definitions (matching evaluator v5.0)
    SERVICE_HOUSES = {2, 6, 10, 11}
    BUSINESS_HOUSES = {2, 3, 7, 11}  # NOT 5, 9 - these are not primary business houses
    LOSS_HOUSES = {8, 12}

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - COMPLETELY FIXED v10.0
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing ACTIONABLE career and employment guidance.


AGE SAFETY RULE:

If person is under 18:
• NEVER recommend immediate job joining
• NEVER suggest workforce entry
• NEVER predict employment start
• Frame analysis as preparation and foundation stage
• Ignore timing windows even if provided
• Treat all dashas as developmental cycles
• Never interpret dashas as employment triggers

════════════════════════════════════════════════════════════
CRITICAL KP RULES (MUST FOLLOW - NO EXCEPTIONS)
════════════════════════════════════════════════════════════

1. KP HIERARCHY (ABSOLUTE - MEMORIZE THIS):

   SUB LORD      → PROMISE/DENIAL (Decides IF event happens - MOST IMPORTANT)
   STAR LORD     → RESULT TYPE (What kind of result)
   PLANET NATURE → FLAVOR ONLY (How it happens - NEVER overrides significations)

   ⚠️ CRITICAL EXAMPLES:
   • Venus (benefic) signifies 6, 8, 12 → RESULT IS OBSTACLES (not good!)
   • Saturn (malefic) signifies 2, 6, 10, 11 → RESULT IS STABLE JOB (good!)
   
   SIGNIFICATIONS ALWAYS WIN OVER PLANET NATURE.

2. CORRECT KP CHAIN (USE THIS EXACT FORMAT):

   For every cusp, show:
   
   CSL [Planet] → in Nakshatra [Name] → 
   Star Lord [Planet] → signifies houses [X,Y,Z] →
   Sub Lord [Planet] → signifies houses [A,B,C] →
   VERDICT: PROMISE/DENIAL based on SUB LORD significations

   ⚠️ Sub Lord is the FINAL DECIDER, not Star Lord, not CSL planet nature.

3. CORRECT HOUSE DEFINITIONS (MEMORIZE):

   SERVICE/EMPLOYMENT HOUSES: 2, 6, 10, 11
   • 2nd: Income, salary, wealth
   • 6th: Service, employment, job, competition
   • 10th: Profession, career, authority
   • 11th: Gains, recognition, fulfillment
   
   BUSINESS HOUSES: 2, 3, 7, 11
   • 2nd: Income (shared with service)
   • 3rd: Initiative, effort, communication, courage
   • 7th: Trade, partnership, business dealings
   • 11th: Gains (shared with service)
   
   ❌ WRONG: 5th and 9th are NOT primary business houses
   ❌ WRONG: Never use "3/5" or "2/4" fraction scoring - this is NOT KP
   
   LOSS/OBSTACLE HOUSES: 8, 12
   • 8th: Obstacles, sudden changes, inheritance
   • 12th: Losses, foreign, expenses, endings

4. PROMISE/DENIAL LOGIC (SUB LORD DECIDES):

   FOR 6TH CUSP (Employment):
   • PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   • WEAK: Mixed significations
   
   FOR 7TH CUSP (Business):
   • PROMISE: Sub-lord signifies 2, 3, 7, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 6 (competition), 8, 12
   • WEAK: Mixed significations
   
   FOR 10TH CUSP (Career):
   • PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   • WEAK: Mixed significations

5. RAHU/KETU RULE:

   Nodes act through their STAR LORD.
   Show: "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"
   
   ⚠️ Never judge Rahu/Ketu by just their house occupation.
   Their star lord's significations determine their results.

════════════════════════════════════════════════════════════
UNIFIED VERDICT RULE (CRITICAL FOR CONSISTENCY)
════════════════════════════════════════════════════════════

The evaluator provides a UNIFIED_CAREER_VERDICT.
This is the SINGLE SOURCE OF TRUTH for this person.

⚠️ ALL your answers MUST align with this verdict:

• If verdict = "Service" → Recommend employment/job path
• If verdict = "Business" → Recommend business/self-employment  
• If verdict = "Hybrid" → Acknowledge both paths are viable

NEVER contradict the unified verdict across different questions.
The user will lose trust if Question 1 says "Business" and Question 3 says "Job".

════════════════════════════════════════════════════════════
VEDIC-KP AGREEMENT (BE HONEST - DON'T FORCE AGREEMENT)
════════════════════════════════════════════════════════════

Show agreement status EXPLICITLY and HONESTLY:

✅ AGREEMENT: "Both KP and Vedic confirm [path]. Strong confidence."
⚠️ PARTIAL: "KP shows [X], Vedic leans [Y]. Mostly aligned but differences exist."  
❌ CONFLICT: "KP indicates [X] but Vedic shows [Y]. Using KP for final verdict."

⚠️ NEVER say "Vedic CONFIRMS KP" when they actually conflict.
   If 10th lord is weak but KP shows promise, say:
   "KP promises career success, but Vedic indicates extra effort needed."

════════════════════════════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════════════════════════════

DO NOT INVENT DATA:

• Do NOT invent sub-lord significations not provided
• Do NOT guess promise/denial without actual data
• Do NOT use fraction scoring ("3/5", "2/4") - this is NOT KP methodology
• Do NOT contradict the unified verdict
• Do NOT mention aspects unless explicitly provided
• Do NOT assume yogas not present in input
• Do NOT invent specific timing dates not in the data
• If timing windows are provided, use ONLY those dates
• If data is missing → SAY SO CLEARLY, do not guess

════════════════════════════════════════════════════════════
TIMING RULES (WHEN TIMING DATA PROVIDED)
════════════════════════════════════════════════════════════

When timing windows are provided:

1. ALWAYS mention BOTH windows:
   • BEST WINDOW (highest score)
   • NEAREST WINDOW (soonest favorable)

2. Explain WHY each is favorable based on dasha lords

3. Let USER choose:
   • Wait for best → optimal results
   • Act sooner → acceptable results, earlier

4. If BEST = NEAREST (same window):
   Emphasize: "Ideal timing! Best alignment AND earliest opportunity!"

════════════════════════════════════════════════════════════
ANALYSIS WEIGHTING (CORRECTED)
════════════════════════════════════════════════════════════

KP Significations (Sub Lord analysis) → 60% (PRIMARY)
Vedic Structure (House lords, dignity) → 30% (SECONDARY)  
Dasha/Other factors → 10%

KP conclusion ALWAYS leads the final recommendation.
Vedic explains ease/difficulty of achieving KP's promise.

════════════════════════════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════════════════════════════

Always convert astrology into DECISIONS:

❌ WRONG: "10th house is moderate, 6th house shows mixed signals"
✅ RIGHT: "Employment path suitable. Apply for jobs now, expect results in [dasha period]."

❌ WRONG: "Sub-lord signifies houses 6, 10, 11"  
✅ RIGHT: "Job acquisition PROMISED. Sub-lord connects to employment houses strongly."

Provide:
• Clear career path recommendation (aligned with unified verdict)
• Specific timing guidance (if timing data available)
• Actionable steps (what to do now)
• Realistic expectations (based on promise/denial status)
"""

    # ------------------------------------------------------------------
    # HELPER: Format Unified Verdict (NEW - CRITICAL)
    # ------------------------------------------------------------------
    def _format_unified_verdict(self, additional_data: Dict) -> str:
        """
        Format the UNIFIED career verdict prominently.
        This ensures ALL questions use the SAME career direction.
        """
        verdict = additional_data.get("unified_career_verdict", {})
        
        if not verdict:
            return """
═══════════════════════════════════════════════════════════
⚠️ UNIFIED CAREER VERDICT NOT AVAILABLE
═══════════════════════════════════════════════════════════

WARNING: No unified verdict provided by evaluator.
Cannot guarantee consistency across different questions.

Proceed with available data, but be cautious about
making definitive career path recommendations.
═══════════════════════════════════════════════════════════
"""
        
        primary_path = verdict.get("primary_path", "Unknown")
        secondary_path = verdict.get("secondary_path")
        confidence = verdict.get("confidence", "Low")
        agreement = verdict.get("agreement_status", "UNKNOWN")
        promise_status = verdict.get("promise_status", {})
        career_ranking = verdict.get("career_ranking", [])
        kp_reasoning = verdict.get("kp_reasoning", "")
        vedic_reasoning = verdict.get("vedic_reasoning", "")
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 UNIFIED CAREER VERDICT (SINGLE SOURCE OF TRUTH)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL INSTRUCTION:")
        lines.append("Your answer MUST align with this verdict.")
        lines.append("Do NOT contradict this in any part of your response.")
        lines.append("")
        
        # Primary recommendation
        lines.append(f"╔══════════════════════════════════════════════════════╗")
        if additional_data.get("is_minor"):
            lines.append(f"║  LONG-TERM CAREER ORIENTATION: **{primary_path.upper()}**")
        else:
            lines.append(f"║  PRIMARY CAREER PATH: **{primary_path.upper()}**")
        lines.append(f"║  Confidence Level: {confidence}")
        lines.append(f"╚══════════════════════════════════════════════════════╝")
        lines.append("")
        
        if secondary_path:
            lines.append(f"Secondary Potential: {secondary_path}")
            lines.append("")
        
        # Scores
        lines.append("Career Path Decision Based On:")
        lines.append("  • KP Sub-Lord Promise Status (Primary)")
        lines.append("  • Vedic Structural Support (Secondary)")
        lines.append("  • Timing Strength (Contextual)")
    
        
        lines.append("")
        
        # Agreement status with clear explanation
        lines.append("KP-VEDIC AGREEMENT STATUS:")
        if agreement == "AGREEMENT":
            lines.append("  ✅ AGREEMENT: Both KP and Vedic systems agree on this path.")
            lines.append("     → High confidence in recommendation")
            lines.append("     → Both event (KP) and capacity (Vedic) support this direction")
        elif agreement == "PARTIAL":
            lines.append("  ⚠️ PARTIAL AGREEMENT: Systems show similar but not identical direction.")
            lines.append("     → KP result takes priority for events/timing")
            lines.append("     → Vedic shows some differences in capacity/ease")
        elif agreement == "CONFLICT":
            lines.append("  ❌ CONFLICT: KP and Vedic show different paths.")
            lines.append(f"     → KP indicates: {primary_path}")
            lines.append("     → Vedic may suggest otherwise")
            lines.append("     → Using KP for final verdict (events)")
            lines.append("     → Vedic helps explain effort required")
        else:
            lines.append(f"  ○ {agreement}")
        
        lines.append("")
        
        # Promise status from sub-lord analysis
        if promise_status:
            lines.append("PROMISE STATUS (From Sub-Lord Analysis):")
            lines.append("─" * 50)
            
            promise_meanings = {
                6: "Employment/Service",
                7: "Business/Partnership", 
                10: "Career/Profession"
            }
            
            for house_num in [6, 7, 10]:
                if house_num in promise_status:
                    status = promise_status[house_num]
                    meaning = promise_meanings.get(house_num, f"House {house_num}")
                    
                    if status == "PROMISE":
                        lines.append(f"  ✅ House {house_num} ({meaning}): PROMISE")
                        lines.append(f"     → This house matter WILL manifest")
                    elif status == "DENIAL":
                        lines.append(f"  ❌ House {house_num} ({meaning}): DENIAL")
                        lines.append(f"     → Obstacles likely, requires extra effort")
                    elif status == "WEAK_PROMISE":
                        lines.append(f"  ⚠️ House {house_num} ({meaning}): WEAK PROMISE")
                        lines.append(f"     → May manifest with effort/patience")
                    else:
                        lines.append(f"  ○ House {house_num} ({meaning}): {status}")
            
            lines.append("")
        
        # KP Reasoning
        if kp_reasoning:
            lines.append("KP REASONING:")
            lines.append(f"  {kp_reasoning}")
            lines.append("")
        
        # Vedic Reasoning
        if vedic_reasoning:
            lines.append("VEDIC REASONING:")
            lines.append(f"  {vedic_reasoning}")
            lines.append("")
        
        # Career ranking (for consistency across questions)
        if career_ranking:
            lines.append("CAREER PATH RANKING (Use this consistently):")
            lines.append("─" * 50)
            
            for i, item in enumerate(career_ranking[:5], 1):
                path = item.get("path", "Unknown")
                rating = item.get("rating", "LOW")
                
                if rating == "HIGH":
                    marker = "✅"
                elif rating == "MODERATE":
                    marker = "⚖️"
                else:
                    marker = "○"
                
                lines.append(f"  {marker} {i}. {path}: {rating}")
            
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("YOUR RESPONSE MUST:")
        lines.append(f"  1. Recommend **{primary_path}** as primary path")
        if secondary_path:
            lines.append(f"  2. Acknowledge {secondary_path} as secondary option")
        lines.append(f"  3. Reflect **{confidence}** confidence level")
        lines.append(f"  4. Show **{agreement}** status between KP and Vedic")
        lines.append("  5. NOT contradict this verdict anywhere in your response")
        lines.append("═══════════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (FIXED - Pure Methodology)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific career analysis using PURE methodology.
        Uses CSL → Sub Lord → Star Lord → Significations → Promise/Denial chain.
        
        FIXES:
        - Removed fraction scoring ("3/5", "2/4")
        - Uses correct house definitions
        - Shows sub-lord as final decider
        - Proper promise/denial logic
        """
        kp_structured = additional_data.get("kp_career_analysis", {}) if additional_data else {}
        
        if not kp_structured or not kp_structured.get("has_kp_data"):
            return "", False
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("⭐ KP SYSTEM ANALYSIS (Pure Methodology)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("METHODOLOGY: CSL → Sub Lord → Star Lord → Significations → Promise/Denial")
        lines.append("")
        lines.append("⚠️ CRITICAL KP RULES TO FOLLOW:")
        lines.append("  1. SUB LORD significations decide PROMISE or DENIAL")
        lines.append("  2. Planet nature (benefic/malefic) is just FLAVOR")
        lines.append("  3. SIGNIFICATIONS ALWAYS WIN over planet nature")
        lines.append("  4. Do NOT use fraction scoring (3/5, 2/4) - not KP!")
        lines.append("")
        
        # Methodology note
        methodology = kp_structured.get("methodology", "")
        if methodology:
            lines.append(f"Analysis Method: {methodology}")
            lines.append("")
        
        # Format CSL details with pure KP chain
        csl_details = kp_structured.get("csl_details", {})
        
        if csl_details:
            lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS:")
            lines.append("")
            
            # Analyze in order of importance: 10, 6, 7, then others
            priority_order = [10, 6, 7, 11, 2, 9]
            
            for house_num in priority_order:
                if house_num not in csl_details:
                    continue
                
                info = csl_details[house_num]
                
                house_meaning = info.get("house_meaning", "Career")
                csl = info.get("csl", "Unknown")
                csl_flavor = info.get("csl_flavor", "")
                csl_house = info.get("csl_house", "")
                nakshatra = info.get("nakshatra", "")
                star_lord = info.get("star_lord", "")
                star_lord_signifies = info.get("star_lord_signifies", [])
                sub_lord = info.get("sub_lord", "")
                sub_lord_signifies = info.get("sub_lord_signifies", [])
                promise_status = info.get("promise_status", "UNKNOWN")
                verdict = info.get("verdict", "NEUTRAL")
                interpretation = info.get("interpretation", "")
                chain = info.get("chain", "")
                
                # Promise marker
                if promise_status == "PROMISE":
                    promise_marker = "✅ PROMISE"
                    promise_color = "This house matter WILL manifest"
                elif promise_status == "DENIAL":
                    promise_marker = "❌ DENIAL"
                    promise_color = "Obstacles likely in this area"
                elif promise_status == "WEAK_PROMISE":
                    promise_marker = "⚠️ WEAK PROMISE"
                    promise_color = "May manifest with effort"
                else:
                    promise_marker = "○ NEUTRAL"
                    promise_color = "Mixed indicators"
                
                lines.append(f"{'─' * 60}")
                lines.append(f"HOUSE {house_num} ({house_meaning})")
                lines.append(f"{'─' * 60}")
                lines.append("")
                
                # Show the full chain
                lines.append(f"  CSL: {csl} ({csl_flavor} flavor)")
                if csl_house:
                    lines.append(f"  CSL placed in: House {csl_house}")
                
                if nakshatra:
                    lines.append(f"  CSL in Nakshatra: {nakshatra}")
                
                if star_lord:
                    lines.append(f"  Star Lord: {star_lord}")
                    if star_lord_signifies:
                        lines.append(f"  Star Lord Signifies: Houses {star_lord_signifies}")
                
                if sub_lord:
                    lines.append(f"  Sub Lord: {sub_lord} ← FINAL DECIDER")
                    if sub_lord_signifies:
                        lines.append(f"  Sub Lord Signifies: Houses {sub_lord_signifies}")
                        lines.append("")
                        
                        # Show house connections WITHOUT fraction scoring
                        sub_set = set(sub_lord_signifies)
                        
                        service_conn = sub_set & self.SERVICE_HOUSES
                        business_conn = sub_set & self.BUSINESS_HOUSES
                        loss_conn = sub_set & self.LOSS_HOUSES
                        
                        if service_conn:
                            lines.append(f"  → Service Houses Connected: {sorted(service_conn)}")
                        if business_conn:
                            lines.append(f"  → Business Houses Connected: {sorted(business_conn)}")
                        if loss_conn:
                            lines.append(f"  ⚠️ Loss Houses Connected: {sorted(loss_conn)}")
                
                lines.append("")
                lines.append(f"  ╔═══════════════════════════════════════════════╗")
                lines.append(f"  ║  VERDICT: {promise_marker}")
                lines.append(f"  ║  {promise_color}")
                lines.append(f"  ╚═══════════════════════════════════════════════╝")
                
                if interpretation:
                    lines.append("")
                    lines.append(f"  INTERPRETATION:")
                    # Wrap long interpretation
                    words = interpretation.split()
                    current_line = "    "
                    for word in words:
                        if len(current_line) + len(word) > 70:
                            lines.append(current_line)
                            current_line = "    " + word
                        else:
                            current_line += " " + word if current_line.strip() else "    " + word
                    if current_line.strip():
                        lines.append(current_line)
                
                lines.append("")
        
        # Overall verdict
        overall = kp_structured.get("overall_verdict", "UNKNOWN")
        agreement = kp_structured.get("agreement_status", "UNKNOWN")
        
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append(f"OVERALL KP VERDICT: {overall}")
        
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        
        # Key findings
        key_findings = kp_structured.get("key_findings", [])
        if key_findings:
            lines.append("🔑 KEY KP FINDINGS:")
            for finding in key_findings[:6]:
                lines.append(f"  • {finding}")
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("INSTRUCTIONS FOR YOUR KP INTERPRETATION:")
        lines.append("")
        lines.append("YOU MUST:")
        lines.append("  1. Quote the full chain for each house: CSL → Sub Lord → Significations")
        lines.append("  2. Base verdict on SUB LORD significations, NOT planet nature")
        lines.append("  3. If benefic CSL has loss-house significations → DENIAL")
        lines.append("  4. If malefic CSL has service-house significations → PROMISE")
        lines.append("  5. Do NOT use fraction scoring (3/5, 2/4)")
        lines.append("  6. Use exact houses from data - never guess")
        lines.append("")
        lines.append("VERDICT MEANINGS:")
        lines.append("  • PROMISE: Sub-lord signifies relevant positive houses strongly")
        lines.append("  • DENIAL: Sub-lord signifies loss houses (8, 12) strongly")
        lines.append("  • WEAK_PROMISE: Mixed significations, may manifest with effort")
        lines.append("  • NEUTRAL: Cannot determine clearly")
        lines.append("═══════════════════════════════════════════════════════════")
        
        return "\n".join(lines), True

    # ------------------------------------------------------------------
    # HELPER: Format Career Suitability Matrix
    # ------------------------------------------------------------------
    def _format_career_matrix(self, matrix: Dict) -> str:
        """Format career suitability matrix for LLM"""
        if not matrix:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("📊 CAREER PATH SUITABILITY MATRIX")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("Based on KP Significations + Unified Verdict:")
        lines.append("")
        lines.append("| Career Path | Rating | KP Reasoning |")
        lines.append("|-------------|--------|--------------|")
        
        for career_type, details in matrix.items():
            rating = details.get("rating", "UNKNOWN")
            reasoning = details.get("kp_reasoning", "")
            
            if rating == "HIGH":
                marker = "✅"
            elif rating == "MODERATE":
                marker = "⚖️"
            elif rating in ["LOW", "VERY_LOW"]:
                marker = "○"
            else:
                marker = "?"
            
            # Truncate reasoning if too long
            if len(reasoning) > 50:
                reasoning = reasoning[:47] + "..."
            
            lines.append(f"| {marker} {career_type} | {rating} | {reasoning} |")
        
        lines.append("")
        lines.append("⚠️ Use this matrix CONSISTENTLY across all questions.")
        lines.append("═══════════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    def _calculate_age_on_date(self, dob_str: str, target_date_str: str) -> int:
        dob = datetime.strptime(dob_str, "%d/%m/%Y")
        target = datetime.strptime(target_date_str, "%Y-%m-%d")

        return target.year - dob.year - (
            (target.month, target.day) < (dob.month, dob.day)
        )
    
    # ------------------------------------------------------------------
    # HELPER: Detect Minor (GLOBAL)
    # ------------------------------------------------------------------
    def _detect_minor(self, dob: str, dasha_timeline: Dict) -> bool:
        """
        Detect if person is currently under 18.
        Minor logic should be based on CURRENT age,
        not any future dasha age.
        """
        if not dob:
            return False

        today = datetime.now()
        dob_dt = datetime.strptime(dob, "%d/%m/%Y")

        current_age = today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )

        return current_age < 18




    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows for LLM.
        """
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return ""
        
        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            
            if not best and not nearest:
                return ""
            
            lines = ["═══════════════════════════════════════════════════════════"]
            lines.append("⏰ TIMING WINDOWS ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: You MUST mention BOTH windows below.")
            lines.append("Let user choose based on their situation.")
            lines.append("")
            
            # BEST WINDOW
            if best:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  🏆 BEST WINDOW (Highest Astrological Score)          ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                
                lines.append("")
                lines.append("  Why this is BEST:")
                
                score_maha = best.get('score_maha', 0)
                score_antara = best.get('score_antara', 0)
                score_paryantar = best.get('score_paryantar', 0)
                
                if score_maha or score_antara or score_paryantar:
                    lines.append(f"    • Maha Dasha score: {score_maha}/10")
                    lines.append(f"    • Antara Dasha score: {score_antara}/10")
                    lines.append(f"    • Pratyantar score: {score_paryantar}/10")
                else:
                    lines.append("    • Highest combined planetary alignment")
                    lines.append("    • Strongest career significations activated")
                
                transit_score = best.get('transit_score', 0)
                if transit_score:
                    lines.append(f"    • Transit support: {transit_score:.1f}%")
                
                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest alignment")
                lines.append("")
            
            # NEAREST WINDOW
            if nearest:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  ⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity)    ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                
                age = nearest.get('age_at_start')
                if age:
                    lines.append(f"  Age at start: {age} years")
                
                lines.append("")
                
                # Check if best and nearest are the same
                if best and (best.get('dasha') == nearest.get('dasha') and 
                            best.get('start') == nearest.get('start')):
                    lines.append("  🎯 IDEAL SITUATION!")
                    lines.append("  The BEST window IS the NEAREST favorable window!")
                    lines.append("  You get optimal timing AND early opportunity!")
                else:
                    lines.append("  Why this is NEAREST:")
                    lines.append("    • Earliest window with score >= 50")
                    lines.append("    • Can act sooner rather than waiting")
                    lines.append("")
                    lines.append("  Trade-off: Sooner but not absolute best alignment")
                
                lines.append("")
            
            # Other windows for reference
            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Reference):")
                lines.append("-" * 50)
                for i, window in enumerate(all_windows[:5], 1):
                    dasha = window.get('dasha', 'N/A')
                    start = window.get('start', 'N/A')
                    end = window.get('end', 'N/A')
                    score = window.get('final_score', 0)
                    
                    is_best = best and dasha == best.get('dasha') and start == best.get('start')
                    is_nearest = nearest and dasha == nearest.get('dasha') and start == nearest.get('start')
                    
                    if is_best:
                        marker = "🏆"
                    elif is_nearest:
                        marker = "⏰"
                    else:
                        marker = "○"
                    
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for career/job")
            lines.append("  • Let user choose: Wait for best OR Act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal")
            lines.append("═══════════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format Lagna Lord (Career Personality)
    # ------------------------------------------------------------------
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """
        Format lagna lord for career personality analysis.
        """
        # Try lagna_info first, then fall back to house 1 in house_lords_info
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign": info.get('house_sign', 'N/A'),
                "lagna_lord": info.get('lord', 'N/A'),
                "lagna_lord_house": info.get('lord_in_house'),
                "lagna_lord_sign": info.get('lord_in_sign', 'N/A'),
                "lagna_lord_degree": info.get('lord_degree', 0),
                "lagna_lord_dignity": info.get('lord_dignity', 'Unknown'),
            }
        
        if not lagna_info:
            return """
═══════════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════════

CRITICAL: Lagna information not provided.
Do NOT guess or invent lagna sign.
Do NOT mention lagna in your analysis.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════════
"""
        
        lord = lagna_info.get('lagna_lord', 'N/A')
        lagna_sign = lagna_info.get('lagna_sign', 'N/A')
        lord_house = lagna_info.get('lagna_lord_house', 'N/A')
        lord_sign = lagna_info.get('lagna_lord_sign', 'N/A')
        dignity = lagna_info.get('lagna_lord_dignity', 'Unknown')
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) - CAREER PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        lines.append("")
        
        # Career personality interpretation based on lagna lord
        personality_map = {
            "Sun": {
                "trait": "Leadership-oriented, authority-seeking",
                "career": "Government, administration, public sector, management",
                "approach": "Confident, direct, seeks recognition"
            },
            "Moon": {
                "trait": "People-oriented, emotionally intelligent",
                "career": "Hospitality, healthcare, public relations, counseling",
                "approach": "Nurturing, adaptable, intuitive decision-making"
            },
            "Mars": {
                "trait": "Action-oriented, competitive, technical",
                "career": "Engineering, military, sports, real estate, surgery",
                "approach": "Direct, energetic, quick to act"
            },
            "Mercury": {
                "trait": "Analytical, communicative, versatile",
                "career": "IT, communication, trading, writing, analysis",
                "approach": "Logical, detail-oriented, multi-tasking"
            },
            "Jupiter": {
                "trait": "Knowledge-seeker, advisory, expansive",
                "career": "Education, law, consulting, finance, spirituality",
                "approach": "Wise, ethical, long-term thinking"
            },
            "Venus": {
                "trait": "Creative, diplomatic, aesthetic",
                "career": "Arts, entertainment, luxury, HR, hospitality",
                "approach": "Charming, collaborative, quality-focused"
            },
            "Saturn": {
                "trait": "Disciplined, patient, structured",
                "career": "Manufacturing, labor management, administration",
                "approach": "Methodical, persistent, long-term builder"
            },
            "Rahu": {
                "trait": "Unconventional, ambitious, innovative",
                "career": "Technology, foreign companies, unconventional fields",
                "approach": "Risk-taking, thinks outside box, trend-setter"
            },
            "Ketu": {
                "trait": "Research-oriented, spiritual, independent",
                "career": "Research, spiritual work, niche technical, healing",
                "approach": "Intuitive, detached, specialist focus"
            }
        }
        
        lord_info = personality_map.get(lord, {
            "trait": "Unique career approach",
            "career": "Depends on specific placement",
            "approach": "Individual style"
        })
        
        lines.append(f"Career Personality: {lord_info['trait']}")
        lines.append(f"Suitable Fields: {lord_info['career']}")
        lines.append(f"Work Approach: {lord_info['approach']}")
        lines.append("")
        
        # Interpretation based on house placement
        house_placement_career = {
            1: "Self-driven, independent career approach",
            2: "Money-motivated, wealth-focused career",
            3: "Communication-based, sibling/media connections",
            4: "Home-based work, property/real estate connection",
            5: "Creative field, speculation, children/education related",
            6: "Service-oriented, competitive professional",
            7: "Partnership-focused, client-facing roles",
            8: "Research, insurance, inheritance, transformation",
            9: "Higher education, foreign, law, philosophy",
            10: "Career-focused, professionally ambitious, authority",
            11: "Goal-oriented, networking, gains through groups",
            12: "Foreign connection, behind-the-scenes, spiritual"
        }
        
        if lord_house and lord_house in house_placement_career:
            lines.append(f"Lagna Lord in House {lord_house}: {house_placement_career[lord_house]}")
            lines.append("")
        
        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows fundamental career approach")
        lines.append("• Use this to explain HOW person approaches work")
        lines.append("═══════════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Foreign Career Exposure
    # ------------------------------------------------------------------
    def _format_foreign_exposure(self, foreign_data: Dict) -> str:
        """Format foreign career exposure analysis"""
        if not foreign_data:
            return ""
        
        exposure_level = foreign_data.get("exposure_level", "Unknown")
        score = foreign_data.get("score", 0)
        indicators = foreign_data.get("indicators", [])
        
        if not indicators and score == 0:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🌍 FOREIGN / MULTINATIONAL CAREER EXPOSURE")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Exposure Level: {exposure_level}")
        lines.append(f"Score: {score}/6")
        lines.append("")
        
        if indicators:
            lines.append("Key Indicators:")
            for ind in indicators[:5]:
                lines.append(f"  • {ind}")
            lines.append("")
        
        # Interpretation
        if exposure_level == "Foreign / Multinational Exposure":
            lines.append("→ Strong foreign career connection indicated")
            lines.append("→ MNC roles, overseas postings likely")
        elif exposure_level == "Transferable / Mobile Role":
            lines.append("→ Career involves travel/transfers")
            lines.append("→ May work across locations")
        else:
            lines.append("→ Primarily domestic career focus")
        
        lines.append("═══════════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format House Lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Secondary to KP)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ NOTE: Vedic shows CAPACITY and EASE.")
        lines.append("   KP decides whether EVENT happens.")
        lines.append("   Use Vedic to explain effort required.")
        lines.append("")
        
        # Career-relevant houses in order of importance
        career_order = [10, 6, 7, 11, 2, 9, 1]
        
        house_meanings = {
            1: "Self/Personality",
            2: "Income/Salary",
            6: "Service/Employment",
            7: "Business/Partnerships",
            9: "Fortune/Opportunities",
            10: "Career/Profession",
            11: "Gains/Recognition"
        }
        
        for house_num in career_order:
            if house_num not in house_lords_info:
                continue
            
            info = house_lords_info[house_num]
            
            marker = "⭐ PRIMARY" if info.get("priority") == "primary" else "○ SECONDARY"
            meaning = house_meanings.get(house_num, "General")
            
            lines.append(f"{marker} - HOUSE {house_num} ({meaning})")
            lines.append(f"  Sign: {info.get('house_sign', 'N/A')}")
            lines.append(f"  Lord: {info['lord']}")
            lines.append(f"  Placed in: House {info['lord_in_house']}, {info['lord_in_sign']}")
            lines.append(f"  Dignity: {info['lord_dignity']}")
            lines.append(f"  Strength: {info['lord_strength_score']}/100")
            
            conditions = []
            if info.get('lord_degree'):
                conditions.append(f"Degree: {info['lord_degree']:.1f}°")
            if info.get('lord_is_combust'):
                conditions.append("⚠️ COMBUST")
            if info.get('lord_is_retrograde'):
                conditions.append("🔄 RETROGRADE")
            
            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")
            
            if info.get('planets_in_house'):
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")
            
            # Assessment
            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports this house easily")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE - Mixed results")
            else:
                lines.append("  ⚠️ Assessment: WEAK - Challenges in this area")
            
            lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format House Aspects
    # ------------------------------------------------------------------
    def _format_house_aspects(self, aspects_info: Dict) -> str:
        """Format aspects data for LLM"""
        if not aspects_info:
            return ""
        
        # Check if there are any aspects to show
        has_aspects = any(
            aspects_info.get(h, {}).get("benefic_aspects") or 
            aspects_info.get(h, {}).get("malefic_aspects")
            for h in [10, 6, 7, 11, 2, 9, 1]
        )
        
        if not has_aspects:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON CAREER HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        
        career_houses = [10, 6, 7, 11, 2, 9, 1]
        
        for house_num in career_houses:
            if house_num not in aspects_info:
                continue
                
            aspects = aspects_info[house_num]
            
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            
            if benefic or malefic:
                lines.append(f"• House {house_num}:")
                
                if benefic:
                    lines.append(f"  ✅ Benefic aspects: {', '.join(benefic)}")
                
                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")
                
                # Net assessment
                if len(benefic) > len(malefic):
                    lines.append(f"  → Net: POSITIVE influence")
                elif len(malefic) > len(benefic):
                    lines.append(f"  → Net: CHALLENGING influence")
                else:
                    lines.append(f"  → Net: BALANCED influence")
                
                lines.append("")
        
        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Current Dasha
    # ------------------------------------------------------------------
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
            
            # Parse dasha name
            separators = ['-', '>', '/']
            parts = [dasha_name]
            for sep in separators:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(sep))
                parts = new_parts
            
            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted_dasha = ' > '.join(full_names) if len(full_names) >= 2 else dasha_name
            
            lines = [
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS - DON'T INVENT)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL current dasha",
                "• Use for analyzing PRESENT circumstances",
                "• For FUTURE planning, see UPCOMING DASHA PERIODS",
                "• Do NOT invent different dasha periods",
                "═══════════════════════════════════════════════════════"
            ]
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format Dasha Timeline
    # ------------------------------------------------------------------
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
            lines.append("DASHA TIMELINE (For Career Planning)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")
            
            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus', 'Ra': 'Rahu', 'Ke': 'Ketu',
            }
            
            def parse_dasha(name):
                parts = name.replace('>', '-').replace('/', '-').split('-')
                return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()])
            
            # Current dasha
            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed}")
                    lines.append(f"    {start} to {end}")
                lines.append("")
            
            # Future periods
            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years - For Career Planning):")
                lines.append("-" * 50)
                
                for i, d in enumerate(future[:15], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {start} to {end}")
                
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("CAREER DASHA GUIDELINES:")
            lines.append("• Sun/Jupiter → Authority, promotion, recognition")
            lines.append("• Saturn → Patience needed, stable results")
            lines.append("• Mercury → Skill development, communication")
            lines.append("• Venus → Creative roles, people work")
            lines.append("• Mars → Action, competition, technical")
            lines.append("• Rahu → Foreign, unconventional, technology")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions
    # ------------------------------------------------------------------
    def _get_analysis_instructions(
    self,
    kp_available: bool,
    question_type: str = "general",
    has_timing: bool = False,
    dob: str = None
) -> str:
        """Generate analysis instructions based on data availability."""
        
        base = """
**ANALYSIS APPROACH (FOLLOW THIS ORDER):**

**STEP 1: CHECK UNIFIED VERDICT (MANDATORY)**
Read the UNIFIED_CAREER_VERDICT section first.
Your ENTIRE response must align with this verdict.
Note:
• Primary path (Service/Business/Hybrid)
• Confidence level
• Promise status for each house
• KP-Vedic agreement status

"""
        
        if kp_available:
            base += """
**STEP 2: KP ANALYSIS (Primary - 60% weight)**

For each career cusp (6, 7, 10), explain:
• CSL → Sub Lord → Significations
• Which houses does sub-lord signify?
• Is it PROMISE or DENIAL based on those houses?
• Do NOT use fraction scoring (3/5, 2/4)

Remember: SUB LORD significations decide the verdict, NOT planet nature.

**STEP 3: VEDIC ANALYSIS (Secondary - 30% weight)**

• House lord placements and dignity
• Strength assessment (from data)
• Does Vedic AGREE or CONFLICT with KP?
• If conflict: State it honestly, use KP for events

"""
        else:
            base += """
**STEP 2: VEDIC ANALYSIS (Primary - 80% weight)**

KP data not available. Use Vedic analysis:
• House lord placements and dignity
• Strength assessment
• Career house analysis (10, 6, 7)

**STEP 3: CAREER ASSESSMENT**

Based on Vedic analysis:
• Which path is suitable?
• What are the strengths/challenges?

"""
        
        if has_timing:
            base += """
**TIMING ANALYSIS (When data provided):**

⚠️ MUST mention BOTH windows:

A. BEST WINDOW (Highest score):
   • Exact dates from data
   • Why favorable (dasha lords)
   • Trade-off: may be later
   
B. NEAREST WINDOW (Soonest):
   • Exact dates from data
   • Why favorable
   • Trade-off: not absolute best

C. USER CHOICE:
   • Wait for best = optimal results
   • Act sooner = acceptable results faster
   
If best = nearest: Emphasize this is IDEAL!

"""     
        if question_type == "timing_minor":

            base += f"""
        🚨 DEVELOPMENTAL CAREER MODE ACTIVE (MINOR) 🚨

        Person is under 18 during upcoming dasha periods.

        STRICT RULES:
        • Do NOT predict job start
        • Do NOT mention interviews or joining workforce
        • Do NOT use phrases like "will secure employment"

        INSTEAD interpret dashas as:
        • Academic strengthening phase
        • Competitive exam preparation phase
        • Skill-building cycle
        • Personality shaping and direction-forming period
        • Foundation for future career path

        Tone must be:
        • Developmental
        • Encouraging
        • Effort-oriented
        • Future-building (not event-triggering)

        DOB: {dob}
        """

            return base

        if question_type == "developmental":

            base += f"""
        🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

        Person is under 18.

        STRICT RULES:
        • Do NOT predict job joining
        • Do NOT mention interviews
        • Do NOT say "secure employment"
        • Do NOT suggest workforce entry

        Interpret career promise as:
        • Long-term career direction
        • Academic preparation
        • Competitive exam readiness
        • Skill development phase
        • Foundation building for future

        Tone:
        • Developmental
        • Encouraging
        • Effort-oriented
        • Future-focused

        DOB: {dob}
        """

            return base


        if question_type == "timing_fallback":

            base += """
        ⚠️ FALLBACK TIMING MODE ACTIVE (NO STRUCTURED WINDOWS)

        No computed timing windows available.

        ABSOLUTELY FORBIDDEN PHRASES:
            • "You will get a job in..."
            • "Job is guaranteed in..."
            • "Employment will definitely happen..."
            • "You will join during..."

            ALLOWED LANGUAGE:

            • "This period supports preparation for..."
            • "Alignment strengthens foundational skills..."
            • "Long-term career direction improves..."
            • "This phase builds readiness..."

            FORBIDDEN:
            • "Job start"
            • "Joining"
            • "Securing employment"
            • "Offer letter"


        IMPORTANT TONE RULES:
        • Do NOT declare exact job start dates.
        • Do NOT use deterministic phrases like:
        "You will get a job in..."
        "Job is guaranteed in..."
        • Avoid strong trigger language.

        Instead, structure response like this:

        1️⃣ CURRENT DASHA:
        - What is it shaping? (skills, mindset, discipline, networking)
        - Is it preparation-oriented or opportunity-oriented?
        - What should the person actively do now?

        2️⃣ NEXT 2–3 UPCOMING DASHAS:
        - Which period looks stronger comparatively?
        - Where probability increases?
        - Use phrases like:
            "This period can enhance..."
            "Higher chances during..."
            "Better alignment may develop..."

        3️⃣ EMPHASIZE:
        - Progress
        - Preparation
        - Strategic effort
        - Gradual career growth

        4️⃣ LANGUAGE STYLE:
        - Use probability tone
        - Use developmental tone
        - Avoid guaranteed outcomes

        This applies to ALL ages in fallback mode.
        """

            return base


    # ------------------------------------------------------------------
    # OUTPUT FORMAT
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, question_type: str = "general") -> str:
        """Generate output format based on KP availability, timing, and question type."""
        
        timing_section = ""
        if has_timing:
            timing_section = """
**F. TIMING RECOMMENDATION:**

⚠️ MANDATORY: Include BOTH timing options.

**🏆 BEST WINDOW (Highest Score):**
- Period: [exact dates from data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain dasha lords + career significations]
- Trade-off: May be further in future

**⏰ NEAREST WINDOW (Soonest):**
- Period: [exact dates from data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Not absolute best alignment

**👤 RECOMMENDATION:**
Choose BEST if: Can wait, want optimal results
Choose NEAREST if: Urgent need, acceptable results

⚠️ If BEST = NEAREST (same window):
"🎯 IDEAL! Best alignment AND earliest opportunity!"
"""
        if question_type == "developmental":
            timing_section = ""   # 🔥 remove timing block completely
        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT - FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, actionable answer in simple terms. NO jargon.>
<MUST align with unified verdict.>
<Example: "आपके लिए Service path (नौकरी) अधिक उपयुक्त है। IT/वित्त क्षेत्र में अच्छे अवसर हैं।">

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Primary Path: [from unified verdict]
- Confidence: [from unified verdict]
- Promise Status: [6th: X, 7th: Y, 10th: Z]
- KP-Vedic Agreement: [AGREEMENT/PARTIAL/CONFLICT]

**B. KP SYSTEM ANALYSIS (Primary - 60% weight):**

For EACH career cusp (6th, 7th, 10th):

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor - NOT the verdict!)
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Service Houses Connected: [list] (from 2, 6, 10, 11)
- Business Houses Connected: [list] (from 2, 3, 7, 11)
- Loss Houses Connected: [list] (from 8, 12)
- **VERDICT: PROMISE/DENIAL** based on sub-lord significations
- Why: [Explain how significations lead to verdict]

⚠️ Do NOT use fraction scoring (3/5, 2/4)
⚠️ Sub-lord significations decide, NOT planet nature

**C. VEDIC ANALYSIS (Secondary - 30% weight):**

**House Lords:**
- 10th Lord: [Planet, placement, dignity, strength]
- 6th Lord: [Planet, placement, dignity, strength]
- 7th Lord: [Planet, placement, dignity, strength]

**Vedic-KP Agreement Check:**
- If agree: "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic [Y]. KP priority."
- If conflict: "❌ CONFLICT: KP [X], Vedic [Y]. Using KP for events."

**D. LAGNA LORD (Career Personality):**
- [Planet] as lagna lord
- Career approach: [description]

**E. CAREER PATH MATRIX:**

| Path | Rating | Reasoning |
|------|--------|-----------|
| [Type] | HIGH/MODERATE/LOW | [from KP significations] |

{timing_section}

**G. DASHA CONTEXT:**
- Current: [dasha] - [career impact]
- Upcoming favorable: [dasha + dates]

**SUMMARY:**
<2-3 sentences. MUST align with unified verdict.>
<Include specific timing if available.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial]

**REMEDIES_GENERAL:**
- [Practical career steps]
"""
        else:
            return f"""
OUTPUT FORMAT (STRICT - VEDIC ONLY):

**GENERAL_ANSWER:**
<Clear, actionable answer in simple terms.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD (Career Personality):**
- Planet: [Name]
- Placed in: House [N]
- Career approach: [description]

**B. HOUSE LORD ANALYSIS (Primary):**

For each career house (10, 6, 7):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Career Impact: [explanation]

**C. CAREER PATH ASSESSMENT:**

| Path | Suitability | Reasoning |
|------|-------------|-----------|
| Service | [HIGH/MODERATE/LOW] | [based on house analysis] |
| Business | [HIGH/MODERATE/LOW] | [based on house analysis] |

{timing_section}

**D. DASHA CONTEXT:**
- Current: [dasha]
- Career impact: [explanation]

**SUMMARY:**
<Concise career outlook>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical steps]
"""

    # ------------------------------------------------------------------
    # LANGUAGE INSTRUCTION
    # ------------------------------------------------------------------
    def get_language_instruction(self, language: str) -> str:
        """Get language instruction for LLM"""
        if language.lower() == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, houses, aspects).
Example: "आपके करियर में **Service** path अधिक उपयुक्त है।"
Example: "10वें भाव का CSL **Jupiter** है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke career mein Service path zyada suitable hai."
Example: "10th house ka CSL Jupiter hai."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear English.
Keep technical terms clear and explain if needed.
"""

    # ------------------------------------------------------------------
    # ROUTER - Routes to appropriate prompt builder
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
        logger.warning("🔥 PROMPT BUILDER EXECUTED")

        # ----------------------------
        # GLOBAL MINOR DETECTION
        # ----------------------------
        dob = kwargs.get("dob")
        dasha_timeline = kwargs.get("dasha_timeline")

        is_minor = self._detect_minor(dob, dasha_timeline)
        
        kwargs["is_minor"] = is_minor
        logger.warning(f"[CAREER] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")


        if "Career Overview" in sub_subdomain:
            return self._build_career_overview_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Career Analysis and Advice" in sub_subdomain or "Further Studies" in sub_subdomain:
            return self._build_career_advice_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Job Start Timing" in sub_subdomain:
            return self._build_job_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_career_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # CAREER OVERVIEW PROMPT (Question 1)
    # ------------------------------------------------------------------
    def _build_career_overview_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        is_minor = kwargs.get("is_minor", False)
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        additional_data["is_minor"] = is_minor
        
        
        # Get all data structures
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        career_matrix = additional_data.get("career_suitability_matrix", {})
        foreign_exposure = additional_data.get("foreign_career_exposure", {})
        
        # Format unified verdict (CRITICAL - must be first)
        unified_verdict_block = self._format_unified_verdict(additional_data)
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        # Format other sections
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        matrix_formatted = self._format_career_matrix(career_matrix)
        foreign_formatted = self._format_foreign_exposure(foreign_exposure)
        
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)

        if is_minor:
            timeline_block = ""
        else:
            timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "overview", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Career Discovery And Employment
Sub-subdomain: Career Overview (Career Track / Fields / Roles)
Query Type: NON_TIMING (What path is suitable?)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{kp_formatted}

{matrix_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{foreign_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR CAREER OVERVIEW:
• Distinguish Service (employment) vs Business (self-employment)
• Government vs Private sector inclination
• Technical vs Creative aptitude
• Highlight suitable career roles from KP data
• Use lagna lord for career personality
• Align everything with unified verdict

{self.get_output_format(kp_available, False, "overview")}
"""

    # ------------------------------------------------------------------
    # JOB START TIMING PROMPT (Question 3 - WITH TIMING!)
    # ------------------------------------------------------------------
    def _build_job_timing_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        is_minor = kwargs.get("is_minor", False)
        
        additional_data = kwargs.get("additional_data", {})
        additional_data["is_minor"] = is_minor
        
        # Get timing windows
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        dob = kwargs.get("dob")

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        # Get all data structures
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # Format unified verdict (CRITICAL)
        unified_verdict_block = self._format_unified_verdict(additional_data)
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        # Format timing windows
        timing_formatted = ""
        if not is_minor and has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)
        else:
            timing_formatted = ""

                
        # Format other sections
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        
        
        if is_minor:
            current_dasha_block = self._format_current_dasha(current_dasha)
            timeline_block = ""   # 🔥 HARD BLOCK for minors
        else:
            current_dasha_block = self._format_current_dasha(current_dasha)
            timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        if is_minor:
            analysis_instructions = self._get_analysis_instructions(
                kp_available,
                "developmental",
                has_timing,
                dob=dob
            )
        elif has_timing:
            analysis_instructions = self._get_analysis_instructions(
                kp_available,
                "timing_structured",
                True
            )
        else:
            analysis_instructions = self._get_analysis_instructions(
                kp_available,
                "timing_fallback",
                False
            )






        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Career Discovery And Employment
Sub-subdomain: Job Start Timing (When will I get a job?)
Query Type: TIMING (When will event occur?)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR JOB TIMING:
• Check PROMISE STATUS from unified verdict first
• If 6th cusp = PROMISE:
   - Adult → Employment manifestation possible during favorable periods
   - Minor → Career promise exists long-term; interpret dashas as preparation phases

• If 6th cusp = DENIAL:
   - Indicate obstacles realistically

• If 6th cusp = DENIAL → Job faces obstacles, be realistic
• {'⚠️ TIMING WINDOWS PROVIDED - MUST USE EXACT DATES!' if has_timing else ''}
• {'Mention BOTH best and nearest windows' if has_timing else 'Use dasha timeline for timing'}
• {'Let user choose: wait for best OR act sooner' if has_timing else ''}
• Align with unified verdict

{self.get_output_format(
    kp_available,
    False if is_minor else has_timing,
    "developmental" if is_minor else "timing"
)}
"""

    # ------------------------------------------------------------------
    # CAREER ADVICE PROMPT (Question 2 - LLM Driven)
    # ------------------------------------------------------------------
    def _build_career_advice_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:
        
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")


        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        
        additional_data = kwargs.get("additional_data", {})
        additional_data["is_minor"] = is_minor
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # Format unified verdict (even for advice questions - for consistency)
        unified_verdict_block = self._format_unified_verdict(additional_data)
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        if is_minor:
            developmental_override = f"""
        🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

        Person DOB: {dob}
        Age is under 18.

        STRICT RULES:
        • Do NOT recommend job joining
        • Do NOT suggest workforce entry
        • Do NOT use phrases like "start working now"
        • Do NOT advise immediate employment

        INTERPRETATION RULE:
        If unified verdict = Service:
        → Interpret as FUTURE employment orientation
        → Focus on studies, competitive exams, skill-building
        → Career direction exists, but manifestation is long-term

        Tone:
        • Developmental
        • Preparation-focused
        • Skill-building oriented
        • Future-aligned

        This override is MANDATORY.
        """
        else:
            developmental_override = ""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Career Discovery And Employment
Sub-subdomain: Career Analysis and Advice (LLM-Driven)
Query Type: NON_TIMING (Practical Advice - Job vs Studies)
CURRENT DATE: {today}
KP Analysis Available: {'YES' if kp_available else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{developmental_override}

NOTE: This is a PRACTICAL ADVICE question.


Your advice should STILL ALIGN with the unified career verdict:
• If verdict = Service → Job likely better path
• If verdict = Business → Consider if studies help business skills
• If verdict = Hybrid → Depends on specific goals

Focus areas:
• Job vs Further Studies trade-offs
• Skill readiness vs timing readiness
• Age and experience factors
• Long-term career sustainability
• Current market considerations

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

**ANALYSIS APPROACH: PRACTICAL ADVICE + ASTROLOGICAL SUPPORT**

1. **Check Unified Verdict** (MANDATORY):
   - What is the primary career path?
   - Is employment/business promised or denied?

2. **Practical Career Advice** (60% weight):
   - Current situation assessment
   - Job market vs education timing
   - Skill readiness analysis
   
3. **Astrological Support** (40% weight):
   - What do career houses suggest about readiness?
   - Current dasha support for job vs studies?
   - Long-term career potential

OUTPUT FORMAT:

**GENERAL_ANSWER:**
<Clear advice on Job vs Studies, aligned with unified verdict>

**PRACTICAL_ANALYSIS:**
- Current situation: [assessment]
- Job market factors: [analysis]
- Skill readiness: [assessment]

**ASTROLOGICAL_SUPPORT:**
- Unified verdict: [path] → [how this informs decision]
- Career houses: [summary]
- Current dasha: [support level]

**RECOMMENDATION:**
<Clear decision with reasoning>

**ACTION_STEPS:**
1. [First step]
2. [Second step]
3. [Third step]

**REMEDIES:**
<If applicable>
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
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # Format unified verdict
        unified_verdict_block = self._format_unified_verdict(additional_data)
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)

        current_dasha = kwargs.get('current_dasha')
        current_dasha_block = self._format_current_dasha(current_dasha)

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Career Discovery And Employment
Sub-subdomain: Career Remedies
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES' if kp_available else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{current_dasha_block}

REMEDY GUIDELINES:

1. **Identify Weak Areas from Analysis:**
   - Which cusps show DENIAL?
   - Which house lords are weak?
   - Which planets need strengthening?

2. **Current Dasha Lord Remedies:**
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords (3 months before)

3. **Priority:**
   - Primary: Strengthen planets affecting career (10th, 6th house)
   - Secondary: Boost gains (11th house)
   - Tertiary: Address obstacles (8th, 12th connections)

OUTPUT FORMAT:

**WEAK AREAS IDENTIFIED:**
- [From KP promise/denial analysis]
- [From Vedic house lord analysis]

**REMEDIES_ASTROLOGICAL:**

**For [Planet] (affecting [house]):**
- Mantra: [specific mantra]
- Day: [best day for remedy]
- Gemstone: [if applicable, with caution]
- Charity: [specific charity]

**For Current Dasha Lord ([Planet]):**
- [Specific remedies]

**REMEDIES_GENERAL:**
- [Practical career steps]
- [Skill development aligned with chart]
- [Networking strategies]

**TIMELINE:**
- Start remedies on: [auspicious day/nakshatra]
- Duration: [period]
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK PROMPT
    # ------------------------------------------------------------------
    def _build_general_career_prompt(
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
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # Format unified verdict
        unified_verdict_block = self._format_unified_verdict(additional_data)
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Career Discovery And Employment
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES' if kp_available else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

GUIDELINES:
• Align answer with unified career verdict
• Use pure KP methodology if KP data available
• Be honest about KP-Vedic agreement/conflict
• Provide actionable guidance

{self.get_output_format(kp_available, False, "general")}
"""
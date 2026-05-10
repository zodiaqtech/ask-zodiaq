"""
Attracting Love – LLM Prompts v9.0 (ENHANCED)

ENHANCEMENTS IN v9.0 (Matching Finance/Career/Business Prompt Pattern):
✅ KP system emphasis with CSL → Star Lord → Significations chain
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback
✅ Love Suitability Matrix display (8 relationship types)
✅ Lagna Lord formatting for relationship personality
✅ Compatibility analysis (7th house focus)
✅ Foreign partner exposure analysis


Compatible with AttractingLoveEvaluator v4.0 data structures:
- kp_love_analysis (structured KP with CSL chains)
- love_suitability_matrix (8 relationship type ratings)
- love_kp_engine (original KP love evaluation)
- love_and_relationship_timing_windows (BEST + NEAREST)
- love_and_relationship_house_lords (Vedic house lord data)
- love_and_relationship_house_aspects (Vedic aspects)
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

DOMAIN_PREFIX = "love_and_relationship"


class AttractingLovePromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Love Relationship → Attracting Love
    v9.0 - Matching Finance/Career/Business prompt pattern with full KP chain support
    """

    domain = "Love_Relationship"
    subtopic = "Attracting Love"


    # Add this method to AttractingLovePromptBuilder:
    def _detect_minor(self, dob: str) -> bool:
        if not dob:
            return False
        today = datetime.now()
        dob_dt = datetime.strptime(dob, "%d/%m/%Y")
        age = today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )
        return age < 18
    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v9.0 WITH KP CHAIN EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing COMPASSIONATE and ACTIONABLE love and relationship guidance.

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
If Venus (benefic) signifies 6, 8, 12 → result is obstacles/delays in love.
If Saturn (malefic) signifies 5, 7, 11 → result is stable, committed relationship.
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
LOVE HOUSE SIGNIFICATION RULE
════════════════════════════════════

ROMANCE HOUSES: 5, 7, 11 → Love, partnership, fulfillment
MARRIAGE HOUSES: 2, 7, 11 → Family, partnership, gains from partner
OBSTACLE HOUSES: 6, 8, 12 → Competition, transformation, separation
POSITIVE HOUSES: 1, 2, 5, 7, 9, 11 → Self, family, romance, partnership, fortune, fulfillment

When judging a planet for love, consider:
• Houses occupied
• Houses owned
• Houses of its star lord
• Houses of its sub lord

Weight priority:
Sub > Star > Occupation > Ownership

════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════

DO NOT invent data.

• Do NOT mention aspects unless explicitly provided
• Do NOT assume yogas not present in input
• Use ONLY supplied positions, houses, dashas, KP significations
• Do NOT invent specific timing dates not provided
• If timing windows are provided, use ONLY those dates

If data is missing → say so clearly, do not guess.

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

• Lagna lord → personality & approach to love
• House lords → capacity/obstacles
• Dignity → strength/weakness

KP decides the event.
Vedic explains ease/difficulty.

════════════════════════════════════
MODERN RELATIONSHIP MAPPING (TENDENCIES ONLY)
════════════════════════════════════

Map planets to relationship styles (modify using KP strength):

Sun → Pride in relationships, seeks respect, leadership in love
Moon → Emotional connection, nurturing, mood-based attraction
Mars → Passionate, intense, physical attraction, quick to act
Mercury → Communication-based, intellectual connection, playful
Jupiter → Commitment-seeking, traditional values, growth together
Venus → Romance, beauty, harmony, sensual connection
Saturn → Slow but stable, serious commitment, delayed but lasting
Rahu → Unconventional relationships, foreign/different partners
Ketu → Karmic connections, spiritual bonds, detachment patterns

These are tendencies, NOT guarantees.
Final decision must come from KP significations.

════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════

Always convert astrology into decisions:

❌ "5th house weak"
✅ "Focus on self-confidence and expanding social circles"

❌ "Venus afflicted"
✅ "Strengthen your self-worth before seeking relationships"

Provide:
• relationship readiness assessment
• timing guidance
• specific action steps
• clear do/don't

Avoid abstract theory.
════════════════════════════════════
ANALYSIS WEIGHTING (ENGINE LOGIC)
════════════════════════════════════

KP Significations → 60%
Vedic Structure → 30%
Dasha Timing → 10%

KP conclusion ALWAYS leads.

# In _get_analysis_instructions(), update the weight labels:
1. START with KP Analysis (PRIMARY - 60% weight)  
2. ADD Vedic Context (SECONDARY - 30% weight)
3. Include Dasha Context (10% weight)            

# In get_output_format() KP section:
A. KP SYSTEM ANALYSIS (Primary - 60% weight)      
C. VEDIC SYSTEM ANALYSIS (Secondary - 30% weight)
E. DASHA TIMING ANALYSIS (10% weight)             

════════════════════════════════════
⚠️ LOVE DOMAIN SAFETY RULES
════════════════════════════════════

- NEVER guarantee love success or failure
- NEVER make predictions that could cause emotional harm
- Frame challenges as TEMPORARY PHASES, not permanent blocks
- Love blocks are CORRECTABLE with remedies and patience
- Always maintain hope while being realistic
- Be compassionate and supportive in all responses

Goal: Provide precise, practical, emotionally supportive guidance — not generic astrology descriptions.
"""

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows (From Finance Pattern)
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
            lines.append("- Explain WHY each window is favorable for love/relationship")
            lines.append("- Let user choose: Wait for best OR Act sooner")
            lines.append("- Use exact dates provided above")
            lines.append("- If best = nearest, emphasize this is ideal timing")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format Lagna Lord (Relationship Personality)
    # ------------------------------------------------------------------
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """
        Format lagna lord prominently for relationship personality analysis.
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
═══════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════

⚠️ CRITICAL: Lagna information not provided.
Do NOT guess or invent lagna sign.
Do NOT mention lagna in your analysis.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════
"""
        
        lord = lagna_info.get('lagna_lord', 'N/A')
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) - RELATIONSHIP PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_info.get('lagna_sign', 'N/A')}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lagna_info.get('lagna_lord_house', 'N/A')}, {lagna_info.get('lagna_lord_sign', 'N/A')}")
        lines.append(f"Dignity: {lagna_info.get('lagna_lord_dignity', 'Unknown')}")
        lines.append("")
        
        # Relationship personality interpretation based on lagna lord
        personality_map = {
            "Sun": "Confident, seeks admiration in love, leadership in relationships",
            "Moon": "Emotionally expressive, nurturing, seeks emotional security",
            "Mars": "Passionate, direct approach, quick to pursue love interests",
            "Mercury": "Communicative, intellectual connection important, playful",
            "Jupiter": "Commitment-oriented, traditional values, seeks growth together",
            "Venus": "Romantic, harmony-seeking, values beauty and sensuality",
            "Saturn": "Cautious, slow to commit but deeply loyal, practical approach",
            "Rahu": "Unconventional relationships, attracted to different/foreign partners",
            "Ketu": "Karmic connections, spiritual bonds, may have detachment patterns"
        }
        
        personality = personality_map.get(lord, "Unique relationship approach")
        lines.append(f"Relationship Personality: {personality}")
        lines.append("")
        
        lines.append("⚠️ CRITICAL RULES:")
        lines.append("• This is the ONLY lagna (ascendant) for this person")
        lines.append("• Do NOT confuse lagna sign with Moon sign (rashi/janma rashi)")
        lines.append("• Lagna lord shows fundamental approach to love/relationships")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Love Suitability Matrix (NEW!)
    # ------------------------------------------------------------------
    def _format_love_matrix(self, matrix: Dict) -> str:
        """Format love suitability matrix for LLM"""
        if not matrix:
            return ""
        
        lines = ["**B. RELATIONSHIP TYPE SUITABILITY MATRIX (From KP Significations):**", ""]
        lines.append("| Relationship Type | Suitability | KP Reasoning |")
        lines.append("|-------------------|-------------|--------------|")
        
        for love_type, details in matrix.items():
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
            
            lines.append(f"| {marker} **{love_type}** | {rating} | {reasoning} |")
        
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format KP Love Analysis (ENHANCED - Matching Finance/Career)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific love analysis points DETERMINISTICALLY.
        Uses CSL → Star Lord → Significations chain from evaluator.
        """
        # Extract from structured KP data
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_love_analysis", {})
        
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
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS (Love Houses):")
                lines.append("")
                
                for house_num in sorted(csl_details.keys()):
                    csl_info = csl_details[house_num]
                    
                    house_meaning = csl_info.get("house_meaning", "Love")
                    csl = csl_info.get("csl", "Unknown")
                    csl_flavor = csl_info.get("csl_flavor", "")
                    nakshatra = csl_info.get("nakshatra", "")
                    star_lord = csl_info.get("star_lord", "")
                    sig_houses = csl_info.get("signified_houses", [])
                    romance_conn = csl_info.get("romance_connection", 0)
                    marriage_conn = csl_info.get("marriage_connection", 0)
                    obstacle_conn = csl_info.get("obstacle_connection", 0)
                    verdict = csl_info.get("verdict", "NEUTRAL")
                    interpretation = csl_info.get("interpretation", "")
                    chain = csl_info.get("chain", "")
                    
                    # Verdict marker
                    if verdict in ["STRONG", "EXCELLENT", "FAVORABLE", "ATTRACTIVE"]:
                        marker = "✅"
                    elif verdict in ["WEAK", "CHALLENGING", "DELAYED", "SECRETIVE"]:
                        marker = "⚠️"
                    elif verdict == "MARRIAGE_ORIENTED":
                        marker = "💍"
                    elif verdict == "LOVE_TO_MARRIAGE":
                        marker = "💞"
                    elif verdict == "INTENSE":
                        marker = "🔥"
                    elif verdict == "FOREIGN_LINK":
                        marker = "🌍"
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
                        lines.append(f"   Romance Connection: {romance_conn}/3 houses (5, 7, 11)")
                        lines.append(f"   Marriage Connection: {marriage_conn}/3 houses (2, 7, 11)")
                        lines.append(f"   Obstacle Connection: {obstacle_conn}/3 houses (6, 8, 12)")
                    lines.append(f"   Verdict: {verdict}")
                    
                    if interpretation:
                        lines.append(f"   Why: {interpretation}")
                    
                    lines.append("")

            # Get love suitability matrix
            love_matrix = additional_data.get("love_suitability_matrix", {}) if additional_data else {}
            if love_matrix:
                matrix_text = self._format_love_matrix(love_matrix)
                lines.append(matrix_text)
                lines.append("")
                
            # Overall verdict with reasoning
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            if overall != "UNKNOWN":
                lines.append(f"📊 OVERALL KP VERDICT (Based on Significations): {overall}")
                lines.append("")
                
                # Provide interpretation based on verdict
                if overall == "EXCELLENT_FOR_LOVE":
                    lines.append("   ✅ Star lord significations across 5-7-11 houses show excellent")
                    lines.append("      love capacity. Romance and partnership strongly supported.")
                elif overall == "LOVE_CHALLENGES_INDICATED":
                    lines.append("   ⚠️ Star lord significations show obstacles in love houses.")
                    lines.append("      Requires patience and self-development. Remedies recommended.")
                elif overall == "STRONG_LOVE_WITH_FULFILLMENT":
                    lines.append("   ✅ 5th and 11th house connections show strong love potential")
                    lines.append("      with fulfillment of romantic hopes.")
                elif overall == "MARRIAGE_FAVORABLE":
                    lines.append("   💍 7th house strongly placed - marriage/commitment favored.")
                    lines.append("      Partnership potential is good.")
                else:
                    lines.append("   ○ Moderate love potential with mixed signification patterns.")
                
                lines.append("")
            
            # Key findings
            key_findings = kp_structured.get("key_findings", [])
            if key_findings:
                lines.append("🔑 KEY KP FINDINGS (Signification-Based):")
                for finding in key_findings[:6]:
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
            lines.append("LOVE Verdict Meanings:")
            lines.append("  • STRONG/EXCELLENT: Significations support love (5-7-11 connection)")
            lines.append("  • MARRIAGE_ORIENTED: 7th house strong, commitment favored")
            lines.append("  • LOVE_TO_MARRIAGE: Romance leads to commitment")
            lines.append("  • CHALLENGING: Significations show obstacles")
            lines.append("  • MODERATE: Mixed significations")
            lines.append("")
            lines.append("YOU MUST:")
            lines.append("  1. Quote the full chain for each house analyzed")
            lines.append("  2. Explain what significations mean for love/relationships")
            lines.append("  3. Map significations to relationship patterns")
            lines.append("  4. Give this PRIMARY weight (60%) in your final recommendation")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines), True
        
        # ═══════════════════════════════════════════════════════════════
        # FALLBACK: Use love_kp_engine (original KP love evaluation)
        # ═══════════════════════════════════════════════════════════════
        if additional_data:
            kp_engine = additional_data.get(f"{DOMAIN_PREFIX}_kp_engine", {})
            # Also check for love_kp_engine key
            if not kp_engine:
                kp_engine = additional_data.get("love_kp_engine", {})
            
            if kp_engine and kp_engine.get("promise") is not None:
                lines = ["═══════════════════════════════════════════════════════"]
                lines.append("⭐ KP LOVE ANALYSIS (Pre-computed by Evaluator)")
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("")
                lines.append("⚠️ CRITICAL: Give PRIMARY weight 60%) to KP findings below.")
                lines.append("")
                
                # Promise state
                promise = kp_engine.get("promise")
                if promise is not None:
                    promise_str = "💖 LOVE PROMISED" if promise else "💔 LOVE CHALLENGING"
                    lines.append(f"📍 Love Promise: **{promise_str}**")
                
                score = kp_engine.get("score")
                if score is not None:
                    lines.append(f"   Overall Score: {score}")
                
                attraction = kp_engine.get("attraction_score")
                if attraction is not None:
                    lines.append(f"   Attraction Score: {attraction}")
                
                compatibility = kp_engine.get("compatibility_score")
                if compatibility is not None:
                    lines.append(f"   Compatibility Score: {compatibility}")
                
                breakup_risk = kp_engine.get("breakup_risk")
                if breakup_risk is not None:
                    risk_str = "LOW" if breakup_risk > -3 else "MODERATE" if breakup_risk > -6 else "HIGH"
                    lines.append(f"   Breakup Risk: {risk_str} ({breakup_risk})")
                
                summary = kp_engine.get("summary")
                if summary:
                    lines.append(f"   Summary: {summary}")
                
                csl_5 = kp_engine.get("csl_5")
                if csl_5:
                    lines.append(f"   5th CSL (Romance): {csl_5}")
                
                csl_7 = kp_engine.get("csl_7")
                if csl_7:
                    lines.append(f"   7th CSL (Partnership): {csl_7}")
                
                promise_5_state = kp_engine.get("promise_5_state")
                if promise_5_state:
                    lines.append(f"   5th House State: {promise_5_state}")
                
                lines.append("")
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("NOTE: Use this data for context. Do NOT override with LLM interpretation.")
                lines.append("═══════════════════════════════════════════════════════")
                
                return "\n".join(lines), True
        
        # No KP data available
        if not technical_points:
            return "", False
        
        return "", False

    # ------------------------------------------------------------------
    # HELPER: Format House Lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Love Houses)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        # Love-relevant houses in order of importance
        love_order = [5, 7, 11, 1, 2, 8, 12]
        
        house_meanings = {
            1: "Self/Personality",
            2: "Family/Values",
            5: "Romance/Attraction",
            7: "Partnership/Relationship",
            8: "Intimacy/Transformation",
            11: "Hopes/Fulfillment",
            12: "Hidden Affairs/Foreign"
        }
        
        for house_num in love_order:
            if house_num not in house_lords_info:
                continue
            
            info = house_lords_info[house_num]
            
            marker = "💖 PRIMARY" if info.get("priority") == "primary" else "○ SECONDARY"
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
            if info.get('lord_is_combust'):
                conditions.append("⚠️ COMBUST (weakened)")
            if info.get('lord_is_retrograde'):
                conditions.append("🔄 RETROGRADE")
            
            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")
            
            if info.get('planets_in_house'):
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")
            
            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports love/relationship")
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
        lines.append("PLANETARY ASPECTS ON LOVE HOUSES")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        love_houses = [5, 7, 11, 1, 2, 8, 12]
        
        for house_num in love_houses:
            if house_num not in aspects_info:
                continue
                
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
                    lines.append(f"     → Challenges, need effort")
                
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
                "Use for analyzing present love/relationship circumstances.",
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
            }
            
            def parse_dasha(name):
                parts = name.replace('>', '-').split('-')
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
                lines.append("⏭️  UPCOMING DASHA PERIODS (Next 10 Years - for love planning):")
                lines.append("-" * 60)
                lines.append("Use these periods for relationship timing:")
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
            lines.append("LOVE DASHA GUIDELINES:")
            lines.append("- Venus periods highly favorable for love/romance")
            lines.append("- Jupiter periods support commitment/marriage")
            lines.append("- Moon periods enhance emotional connections")
            lines.append("- Mars periods bring passion but can cause conflicts")
            lines.append("- Saturn periods may delay but give lasting bonds")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Check if love is blocked
    # ------------------------------------------------------------------
    def _is_blocked(self, additional_data: Dict) -> bool:
        """Check if love is blocked based on KP analysis"""
        if not additional_data:
            return False
        
        # Check KP love engine
        kp_engine = additional_data.get(f"{DOMAIN_PREFIX}_kp_engine", {})
        if not kp_engine:
            kp_engine = additional_data.get("love_kp_engine", {})
        
        if kp_engine.get("promise") is False:
            return True
        
        if kp_engine.get("promise_5_state") == "blocked":
            return True
        
        # Also check house lords strength
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if house_lords:
            weak_count = 0
            for house_num in [5, 7]:
                lord_info = house_lords.get(house_num, {})
                if lord_info.get("lord_strength_score", 50) < 30:
                    weak_count += 1
            
            if weak_count >= 2:
                return True
        
        return False

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions Based on KP Availability
    # ------------------------------------------------------------------
    def _get_analysis_instructions(self, kp_available: bool, question_type: str = "general", has_timing: bool = False) -> str:
        """Generate analysis instructions based on whether KP data is available."""
        
        if kp_available:
            if question_type == "timing" and has_timing:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM + TIMING**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 60% weight):
   - What does the 5th cusp sub lord signify? (romance/attraction)
   - What does the 7th cusp sub lord signify? (partnership/relationship)
   - What does the 11th cusp sub lord signify? (fulfillment of hopes)
   - KP verdict: Love promised or challenged?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 5th house lord strength (romance capacity)
   - 7th house lord strength (partnership potential)
   - Venus condition (love karaka)

3. **TIMING ANALYSIS** (10% weight - CRITICAL FOR THIS QUESTION):
   ⚠️ MUST analyze BOTH timing windows provided:
   
   A. BEST WINDOW (Highest score):
      - When: Exact dates from timing data
      - Why favorable: Dasha lords + love significations
      - Trade-off: May be further away
   
   B. NEAREST WINDOW (Earliest favorable):
      - When: Exact dates from timing data
      - Why favorable: Still good score, sooner
      - Trade-off: Not absolute best
   
   C. USER CHOICE:
      - Wait for best alignment (patience + optimal results)
      - Act sooner (urgency + good enough results)
   
   ⚠️ If best = nearest: Emphasize this is IDEAL timing!

"""         
            elif question_type == "context_only":
                return """
            **ANALYSIS APPROACH: KP + VEDIC (NO EXACT TIMING AVAILABLE)**

            1. START with KP Analysis (60% weight)
            2. ADD Vedic context (30% weight)

            3. DASHA CONTEXT ONLY (10% weight):
            - Explain current dasha influence on emotional life.
            - Mention next major dasha shift.
            - DO NOT assign relationship events to specific dates.
            - DO NOT say "love will happen in this period".
            - DO NOT convert dasha into prediction windows.

            Dasha is contextual, not predictive here.
            """        

            elif question_type == "finding_love":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 60% weight):
   - What does the 5th cusp sub lord signify? (romance potential)
   - What does the 7th cusp sub lord signify? (partnership capacity)
   - Love promise state from KP?
   - Attraction and compatibility scores?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 5th house lord strength (romance foundation)
   - 7th house lord strength (partnership potential)
   - Venus condition (love karaka)
   - Lagna lord (relationship personality)

3. **Include Love Matrix** (10% weight):
   - Love marriage vs Arranged marriage suitability
   - Long-term vs Passionate relationship style
   - Online/Modern dating aptitude

"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 60% weight)
2. **ADD Vedic Context** (SECONDARY - 30% weight)
3. **Include Dasha Context** (10% weight)
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
   - Detailed analysis of love houses (5, 7, 11)
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

        dob = kwargs.get("dob")
        is_minor = self._detect_minor(dob)
        kwargs["is_minor"] = is_minor
        sub_subdomain = kwargs.get("sub_subdomain", "")

        if "Finding" in sub_subdomain or "Attracting" in sub_subdomain:
            return self._build_finding_love_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Unrequited" in sub_subdomain:
            return self._build_unrequited_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_love_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # FINDING LOVE PROMPT (Main Question - WITH TIMING!)
    # ------------------------------------------------------------------
    def _build_finding_love_prompt(
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
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")
        
        # Get all data structures
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        love_matrix = additional_data.get("love_suitability_matrix", {})
        
        # ✅ Get timing windows
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)
        
        # Check if blocked
        is_blocked = self._is_blocked(additional_data)

        logger.info(f"🔍 PROMPT DEBUG: timing_windows_data present: {bool(timing_windows_data)}")
        logger.info(f"🔍 PROMPT DEBUG: has_timing flag: {has_timing}")
        logger.info(f"🔍 PROMPT DEBUG: is_blocked: {is_blocked}")
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        # Format other sections
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "promise", "ruling planet", "kp"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        # Determine question type
        if is_blocked:
            question_type = "finding_love"
        elif has_timing:
            question_type = "timing"
        else:
            question_type = "context_only"
        analysis_instructions = self._get_analysis_instructions(kp_available, question_type, has_timing and not is_blocked)
        
        # Blocked state handling
        blocked_section = ""
        if is_blocked:
            blocked_section = """
═══════════════════════════════════════════════════════
⚠️ LOVE CURRENTLY CHALLENGING - FOCUS ON SELF-DEVELOPMENT
═══════════════════════════════════════════════════════

The chart shows some challenges for finding love currently.

🚫 DO NOT provide specific timing windows or dates.
✅ DO mention current dasha period for general context.
✅ DO recommend self-development and patience.
✅ DO provide remedies to strengthen love prospects.
✅ Frame challenges as TEMPORARY and CORRECTABLE.

MESSAGE: "Love challenges are temporary phases, not permanent blocks.
Focus on self-improvement and the right time will come."
═══════════════════════════════════════════════════════
"""     

        minor_tone_section = ""
        if is_minor:
            minor_tone_section = """
        ═══════════════════════════════════════════════════════
        👶 AGE-SENSITIVE COMMUNICATION MODE
        ═══════════════════════════════════════════════════════

        ⚠️ The user is under 18.

        Adjust tone accordingly:

        - Use simple, age-appropriate language
        - Avoid adult relationship language
        - Avoid sexual implications
        - Frame love as "future relationships"
        - Emphasize emotional growth and friendship
        - Keep advice wholesome and developmental
        - Avoid phrases like "dating strategy" or "partner selection"

        Timing windows may still be shown,
        but frame them as FUTURE LIFE PHASES, not immediate action.

        ═══════════════════════════════════════════════════════
        """
        # Also suppress timing for minors:
        timing_formatted = ""
        if has_timing and not is_blocked:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Love Relationship
- Subtopic: Attracting Love
- Sub-subdomain: Finding Love (When will I find love?)
- Query Type: {'TIMING' if has_timing and not is_blocked else 'CONTEXT_ONLY'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}
- Timing Windows Available: {'YES' if has_timing and not is_blocked else 'NO'}
- Love Currently Blocked: {'YES - Focus on remedies' if is_blocked else 'NO'}

USER QUESTION:
"{question}"

{blocked_section}

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{minor_tone_section}

{analysis_instructions}

CRITICAL INSTRUCTIONS:
{'⚠️ TIMING WINDOWS PROVIDED ABOVE - MUST USE IN YOUR ANSWER!' if has_timing and not is_blocked else ''}
{'- Mention BOTH best and nearest windows with exact dates' if has_timing and not is_blocked else ''}
{'- Explain why each window is favorable for finding love' if has_timing and not is_blocked else ''}
{'- Let user choose: wait for best OR act sooner' if has_timing and not is_blocked else ''}
{'- If best = nearest, emphasize this is ideal timing' if has_timing and not is_blocked else ''}
{'⚠️ LOVE IS CHALLENGING - Focus on self-development and remedies' if is_blocked else ''}

GUIDELINES:
- 5th house shows romance/attraction capacity
- 7th house shows partnership/commitment potential
- Venus is the karaka for love
- Be compassionate and supportive
- Never guarantee love success or failure
- Frame challenges as temporary phases

{self.get_output_format(
    kp_available,
    has_timing and not is_blocked,
    question_type
)}
"""

    # ------------------------------------------------------------------
    # UNREQUITED LOVE PROMPT
    # ------------------------------------------------------------------
    def _build_unrequited_prompt(
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
        
        # For unrequited love, show KP context with focus on 5th and 8th houses
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "kp", "connects to", "promise", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "unrequited", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Love Relationship
- Subtopic: Attracting Love
- Sub-subdomain: Unrequited Love (Why is my love not returned?)
- Query Type: NON_TIMING (Emotional/Understanding Question)
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

CRITICAL GUIDELINES FOR UNREQUITED LOVE:
- Be COMPASSIONATE and SUPPORTIVE
- Focus on UNDERSTANDING, not blame
- 5th house challenges = romance obstacles
- 8th house = emotional transformation needed
- Explain when situation may improve
- Provide hope while being realistic
- NEVER blame the person for unrequited love

{self.get_output_format(kp_available, False, "unrequited")}
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
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # For remedies, KP can provide context
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        current_dasha_block = self._format_current_dasha(current_dasha)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "kp"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Love Relationship
- Subtopic: Attracting Love
- Sub-subdomain: Love Remedies
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

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

REMEDY GUIDELINES FOR LOVE:

1. **Identify Weak Planets**:
   {'- Weak KP cusp sub lords (if KP available)' if kp_available else ''}
   - Weak Vedic house lords (debilitated/combust/poorly placed)
   - Focus on 5th, 7th house lords for love

2. **Current Dasha Lord Remedies**:
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords (3 months before)

3. **Priority**:
   - Primary: Strengthen Venus (love karaka)
   - Secondary: Strengthen weak lords affecting love (5th, 7th)
   - Tertiary: Address obstacles (6th, 8th connections)

PLANETARY REMEDY GUIDE FOR LOVE:
- VENUS: Love, attraction (Diamond/White Sapphire, "Om Shukraya Namaha")
- MOON: Emotions, feelings (Pearl, "Om Chandraya Namaha")
- JUPITER: Commitment, blessings (Yellow Sapphire, "Om Gurave Namaha")
- MARS: Passion, courage (Red Coral, "Om Mangalaya Namaha")

{self.get_output_format(kp_available, False, "remedies")}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK PROMPT
    # ------------------------------------------------------------------
    def _build_general_love_prompt(
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
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "kp"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Love Relationship
- Subtopic: Attracting Love
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

{self.get_output_format(kp_available, False, "general")}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT - DYNAMIC BASED ON KP AVAILABILITY + TIMING
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, question_type: str = "general") -> str:
        """Generate output format based on KP availability, timing, and question type."""
        
        # Define timing section
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
  * Maha Dasha lord ([planet]): [love significations] → Score [X]/10
  * Antara Dasha lord ([planet]): [romance support] → Score [Y]/10
  * Pratyantar Dasha lord ([planet]): [final trigger] → Score [Z]/10
- Trade-off: [e.g., "May be further in future, but strongest planetary alignment"]

**⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):**
- Period: [exact start date] to [exact end date] (from timing data)
- Dasha: [Maha-Antara-Pratyantar] (exact dasha name from data)
- Age at start: [age] years
- Astrological Score: [final_score]/100
- Why this is NEAREST:
  * [Explain why this window comes sooner]
  * [Still has favorable score >= 50]
- Trade-off: [e.g., "Sooner opportunity but not absolute best alignment"]

**👤 USER RECOMMENDATION (Help them decide):**
Choose BEST window if:
- You can wait for optimal love timing
- You want maximum relationship success
- Long-term compatibility is priority

Choose NEAREST window if:
- You want to start dating sooner
- Good enough results acceptable
- Cannot wait for best timing

⚠️ Special case: If BEST = NEAREST (same window):
"🎯 IDEAL TIMING: The best window IS the nearest favorable window! 
You get both optimal astrological support AND early opportunity."
"""
        else:
            timing_section = ""
        
        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT):


NARRATIVE FLOW RULE:
Your answer should read as a CONNECTED STORY, not a checklist.
Flow: Love promise → Why (KP chain) → What it means (relationship style) 
      → Support from Vedic → Timing → Action steps

Each section should naturally lead into the next.
❌ WRONG: "KP shows STRONG. Vedic shows MODERATE."
✅ RIGHT: "KP confirms love is promised through [chain]. Vedic reinforces this — 
          though [lord] needs strengthening. Best time to act: [window]."


**GENERAL_ANSWER:**
<Write a clear, compassionate answer in simple layman's terms. NO astrological jargon.>
<Example: "आपके लिए प्रेम की अच्छी संभावनाएं हैं। धैर्य रखें और सही समय का इंतजार करें।">

**ASTROLOGICAL_ANALYSIS:**

⚠️ CRITICAL: Follow CORRECT KP methodology - CSL → Star Lord → Significations → Result

**A. KP SYSTEM ANALYSIS (Primary - 60% weight):**

For EACH love cusp analyzed (5th, 7th, 11th), present in this EXACT format:

**House [N] ([Meaning - e.g., Romance/Attraction]):**
- Cusp Sub Lord (CSL): [Planet name] ([benefic/malefic/neutral] flavor)
- CSL in Nakshatra: [Nakshatra name]
- Star Lord: [Planet name]
- Star Lord Signifies: Houses [X, Y, Z] (from actual data - never guess!)
- Romance Connection: [N]/3 (overlap with houses 5, 7, 11)
- Marriage Connection: [N]/3 (overlap with houses 2, 7, 11)
- Obstacle Connection: [N]/3 (overlap with houses 6, 8, 12)
- **Verdict: [STRONG/CHALLENGING/MARRIAGE_ORIENTED/etc]** ← Based on SIGNIFICATIONS only
- Why: [Explain the full chain - how star lord significations lead to verdict]

**CRITICAL EXAMPLE - DO THIS:**
"**House 5 (Romance/Attraction):**
- CSL: Venus (benefic flavor)
- CSL in Nakshatra: Bharani
- Star Lord: Venus
- Star Lord Signifies: Houses [5, 7, 11]
- Romance Connection: 3/3 (excellent)
- Marriage Connection: 2/3 (good)
- **Verdict: STRONG - LOVE PROMISED**
- Why: Venus (benefic flavor) is in Bharani nakshatra, self-ruled. Venus signifies 
romance (5th), partnership (7th), and fulfillment (11th). Full romance connection 
indicates strong love potential with good marriage prospects."

**B. RELATIONSHIP TYPE SUITABILITY MATRIX (From KP Significations):**

| Relationship Type | Suitability | KP Reasoning |
|-------------------|-------------|--------------|
| **Love Marriage** | [HIGH/MODERATE/LOW] | [Based on 5th + 7th connection] |
| **Arranged Marriage** | [HIGH/MODERATE/LOW] | [Based on 7th without strong 5th] |
| **Long-Term Relationship** | [HIGH/MODERATE/LOW] | [Based on stable planet influence] |
| **Passionate Romance** | [HIGH/MODERATE/LOW] | [Based on Mars/8th house] |
| **Online/Modern Dating** | [HIGH/MODERATE/LOW] | [Based on Rahu + 11th house] |
| **Foreign Partner** | [HIGH/MODERATE/LOW] | [Based on 12th + Rahu connection] |

**C. VEDIC SYSTEM ANALYSIS (Secondary - 30% weight):**

**1. Lagna Lord Analysis (Relationship Personality):**
- Planet: [Name] (lord of [Ascendant sign])
- Placed in: House [N], Sign [Name]
- Dignity: [Exalted/Own Sign/Friendly/Neutral/Enemy/Debilitated]
- Relationship Personality: [Confident/Emotional/Passionate/etc]
- Approach to Love: [Describe based on planet]

**2. Love House Lords Analysis (5th, 7th, 11th):**

- **5th Lord ([Planet])**: [Placement, dignity, strength]
  → [Does this CONFIRM KP's romance verdict?]

- **7th Lord ([Planet])**: [Placement, dignity, strength]
  → [Does this support partnership potential?]

- **Venus Analysis:** [Position, dignity, aspects]
  → [Love karaka strength?]

**Vedic-KP Agreement Check:**
- If both agree: "✅ Vedic CONFIRMS KP: [Explanation]"
- If they differ: "⚠️ KP shows [X] BUT Vedic shows [Y]. KP takes priority for events."

**D. DASHA TIMING ANALYSIS (10% weight):**

**Current Dasha Impact:**
- Dasha: [Current Maha-Antara-Pratyantar]
- Period: [Start] to [End]
- Love Impact: [How this affects love NOW]

If timing windows are provided above:
→ Use the BEST and NEAREST windows section (mandatory).

If no timing windows are provided:
→ Provide dasha context only.
→ Do NOT assign exact event dates.
→ Do NOT convert dasha into prediction window.

**DASHA CONTEXT (No Exact Timing Available):**
- Current Dasha: [Name]
  → Emotional / relational focus

- Next Dasha: [Name]
  → General developmental shift

⚠️ No specific event timing available from engine.

{timing_section}

**SUMMARY:**
<Concise 2-3 sentence love outlook with {('specific timing dates and actionable steps' if has_timing else 'love path and dasha guidance')}>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets affecting love houses]
- [Strengthen Venus and Moon for love]

**REMEDIES_GENERAL:**
- [Self-improvement aligned with chart]
- [Social expansion strategies]
- [Confidence building]
"""
        else:
            # Vedic only format
            return f"""
OUTPUT FORMAT (STRICT):

**GENERAL_ANSWER:**
<Clear, compassionate love answer in simple terms.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD ANALYSIS (Relationship Personality - 20% weight):**
- Planet: [Name] (lord of [Ascendant sign])
- Placed in: House [N], Sign [Name]
- Dignity: [Status]
- Relationship Personality: [Description]
- Approach to Love: [Description]

**B. VEDIC HOUSE LORD ANALYSIS (Primary - 60% weight):**

**Love Houses (5th, 7th, 11th) - Detailed Analysis:**

For each house:
- Lord: [Planet]
- Placement: House [N], Sign [Name]
- Dignity: [Status]
- Strength: [X]/100
- Assessment: [STRONG/MODERATE/WEAK]
- Love Impact: [How this affects love/relationships]

**Venus Analysis:**
- Position: House [N], Sign [Name]
- Dignity: [Status]
- Love Karaka Strength: [Assessment]

**C. RELATIONSHIP TYPE SUITABILITY:**

| Relationship Type | Suitability | Reasoning |
|-------------------|-------------|-----------|
| **Love Marriage** | [HIGH/MODERATE/LOW] | [Based on house lord analysis] |
| **Long-Term** | [HIGH/MODERATE/LOW] | [Based on stability indicators] |
| **Passionate** | [HIGH/MODERATE/LOW] | [Based on Mars/Venus] |

**D. DASHA TIMING (20% weight):**

**Current Dasha Impact:**
- Dasha: [Current]
- Love Effect: [How it affects love NOW]

**Upcoming Favorable Periods:**
- [Dasha]: [Dates] → [Love opportunity]

{timing_section}

**E. FINAL VERDICT:**

**LOVE RECOMMENDATION:**
[Clear recommendation]
[Suitable relationship style]
[Action steps]

**SUMMARY:**
<Concise love outlook>

**REMEDIES_ASTROLOGICAL:**
- [Strengthen weak house lords]
- [Venus remedies]

**REMEDIES_GENERAL:**
- [Practical love advice]
- [Self-improvement]
"""
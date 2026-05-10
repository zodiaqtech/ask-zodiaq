"""
Career Changes – LLM Prompts v9.0 (ENHANCED)

ENHANCEMENTS IN v9.0 (Matching Finance/Career Discovery/Business Pattern):
✅ KP system emphasis with CSL → Star Lord → Significations chain
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback
✅ Career Change Suitability Matrix display (8 change types)
✅ Lagna Lord formatting for career personality
✅ Service vs Business structured analysis display
✅ Foreign career exposure analysis display

Weightage:
- TIMING: KP 50% + Vedic 30% + Dasha 15% + Other 5%
- NON-TIMING: Vedic 85% + KP Facts 15% (No Dasha)

Compatible with CareerChangesEvaluator v4.0 data structures:
- kp_career_change_analysis (structured KP with CSL chains)
- career_change_suitability_matrix (8 change type ratings)
- service_vs_business (Service/Business/Mixed determination)
- career_role_resonance (KP profession mapping)
- foreign_career_exposure (foreign career analysis)
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


class CareerChangesPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Career → Career Changes
    v9.0 - Matching Finance/Career Discovery/Business prompt pattern with full KP chain support
    """

    domain = "Career"
    subtopic = "Career Changes"

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v9.0 WITH KP CHAIN EMPHASIS
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing PRECISE and ACTIONABLE career transition guidance.

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
If Jupiter (benefic) signifies 6, 8, 12 → result is career obstacles/delays.
If Saturn (malefic) signifies 2, 10, 11 → result is stable career with gains.
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
CAREER HOUSE SIGNIFICATION RULE
════════════════════════════════════

SERVICE HOUSES: 2, 6, 10, 11 → Employment, salary, profession, gains from job
BUSINESS HOUSES: 3, 5, 7, 9, 11 → Initiative, speculation, partnerships, fortune, gains from business
WEALTH HOUSES: 2, 10, 11 → Income, profession, overall gains
FOREIGN HOUSES: 3, 9, 12 → Travel, abroad, foreign connections
LOSS HOUSES: 6, 8, 12 → Obstacles, sudden changes, losses

When judging a planet for career change, consider:
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

• Lagna lord → personality & approach to career
• House lords → capacity/obstacles
• Dignity → strength/weakness

KP decides the event.
Vedic explains ease/difficulty.

════════════════════════════════════
MODERN CAREER MAPPING (TENDENCIES ONLY)
════════════════════════════════════

Map planets to career styles (modify using KP strength):

Sun → Authority, leadership, government, public sector
Moon → Public dealing, hospitality, fluctuating income
Mars → Technical, engineering, real estate, competitive
Mercury → Communication, IT, trading, sales, brokerage
Jupiter → Education, law, finance, advisory, consulting
Venus → Luxury, fashion, entertainment, creative fields
Saturn → Manufacturing, labor, discipline-based, slow growth
Rahu → Technology, foreign companies, unconventional
Ketu → Research, niche technical, spiritual, consulting

These are tendencies, NOT guarantees.
Final decision must come from KP significations.

════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════

Always convert astrology into decisions:

❌ "10th house weak"
✅ "Focus on skill development before major career moves"

❌ "Saturn in 7th house"
✅ "Partnership-based business requires patience; solo ventures may be easier initially"

Provide:
• career path recommendation (Service/Business/Hybrid)
• timing guidance (if timing question)
• specific action steps
• clear do/don't

Avoid abstract theory.

════════════════════════════════════
ANALYSIS WEIGHTING (ENGINE LOGIC)
════════════════════════════════════

Decision Priority Order:

1️⃣ KP Significations (Primary Decision Maker)
2️⃣ Vedic Structure (Capacity & Ease)
3️⃣ Dasha (Timing Activation)
4️⃣ Other Supporting Indicators

KP decides direction.
Vedic explains strength.
Dasha activates timing.

════════════════════════════════════
⚠️ CAREER DOMAIN SAFETY RULES
════════════════════════════════════

- NEVER induce fear or anxiety about career changes
- NEVER declare permanent career blocks unless data explicitly shows it
- All challenges must be framed as TENDENCIES, not certainties
- Frame delays as "preparation time" not "problems"
- Always encourage practical planning alongside astrological guidance

Goal: Provide precise, practical guidance — not generic astrology descriptions.
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
            lines.append("- Explain WHY each window is favorable for career change")
            lines.append("- Let user choose: Wait for best OR Act sooner")
            lines.append("- Use exact dates provided above")
            lines.append("- If best = nearest, emphasize this is ideal timing")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""
    
    
    # ------------------------------------------------------------------
    # HELPER: Format Lagna Lord (Career Personality)
    # ------------------------------------------------------------------
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """
        Format lagna lord prominently for career personality analysis.
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
        lines.append("🎯 LAGNA (ASCENDANT) - CAREER PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_info.get('lagna_sign', 'N/A')}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lagna_info.get('lagna_lord_house', 'N/A')}, {lagna_info.get('lagna_lord_sign', 'N/A')}")
        lines.append(f"Dignity: {lagna_info.get('lagna_lord_dignity', 'Unknown')}")
        lines.append("")
        
        # Career personality interpretation based on lagna lord
        personality_map = {
            "Sun": "Leadership-oriented, seeks authority positions, government roles suit well",
            "Moon": "Adaptable, public-facing roles, hospitality and service industries",
            "Mars": "Competitive, technical fields, real estate, engineering, sports",
            "Mercury": "Communication-focused, IT, trading, sales, consultancy",
            "Jupiter": "Advisory roles, education, law, finance, traditional professions",
            "Venus": "Creative fields, luxury industry, entertainment, beauty",
            "Saturn": "Disciplined approach, manufacturing, labor-intensive, slow but steady growth",
            "Rahu": "Unconventional careers, technology, foreign companies, startups",
            "Ketu": "Research-oriented, niche technical, spiritual counseling"
        }
        
        personality = personality_map.get(lord, "Unique career approach")
        lines.append(f"Career Personality: {personality}")
        lines.append("")
        
        lines.append("⚠️ CRITICAL RULES:")
        lines.append("• This is the ONLY lagna (ascendant) for this person")
        lines.append("• Do NOT confuse lagna sign with Moon sign (rashi/janma rashi)")
        lines.append("• Lagna lord shows fundamental approach to career/work")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Career Change Suitability Matrix (NEW!)
    # ------------------------------------------------------------------
    def _format_career_change_matrix(self, matrix: Dict) -> str:
        """Format career change suitability matrix for LLM"""
        if not matrix:
            return ""
        
        lines = ["**B. CAREER CHANGE SUITABILITY MATRIX (From KP Significations):**", ""]
        lines.append("| Change Type | Suitability | KP Reasoning |")
        lines.append("|-------------|-------------|--------------|")
        
        for change_type, details in matrix.items():
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
            
            lines.append(f"| {marker} **{change_type}** | {rating} | {reasoning} |")
        
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Service vs Business Analysis
    # ------------------------------------------------------------------
    def _format_service_vs_business(self, svb_data: Dict) -> str:
        """Format service vs business determination"""
        if not svb_data:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("📊 SERVICE VS BUSINESS DETERMINATION (KP Analysis)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        final_path = svb_data.get("final_path", "Unknown")
        service_score = svb_data.get("service_score", 0)
        business_score = svb_data.get("business_score", 0)
        csl_10 = svb_data.get("10th_CSL", "N/A")
        csl_7 = svb_data.get("7th_CSL", "N/A")
        shift = svb_data.get("career_shift_likelihood", "Unknown")
        
        # Path emoji
        if final_path == "Service":
            path_emoji = "💼"
        elif final_path == "Business":
            path_emoji = "🏢"
        else:
            path_emoji = "🔄"
        
        lines.append(f"{path_emoji} FINAL PATH: **{final_path}**")
        lines.append("")
        lines.append(f"Service Score: {service_score}")
        lines.append(f"Business Score: {business_score}")
        lines.append(f"10th CSL (Career): {csl_10}")
        lines.append(f"7th CSL (Business): {csl_7}")
        lines.append(f"Career Shift Likelihood: {shift}")
        lines.append("")
        
        # Interpretation
        if final_path == "Service":
            lines.append("Interpretation: Employment/service path is stronger.")
            lines.append("10th CSL signifies more service houses (2, 6, 10, 11).")
        elif final_path == "Business":
            lines.append("Interpretation: Business/self-employment path is stronger.")
            lines.append("7th CSL signifies more business houses (3, 5, 7, 9, 11).")
        else:
            lines.append("Interpretation: Both paths are viable.")
            lines.append("Hybrid approach (Job + Side Business) may work best.")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Foreign Career Exposure
    # ------------------------------------------------------------------
    def _format_foreign_exposure(self, foreign_data: Dict) -> str:
        """Format foreign career exposure analysis"""
        if not foreign_data:
            return ""
        
        exposure_level = foreign_data.get("exposure_level", "")
        score = foreign_data.get("score", 0)
        indicators = foreign_data.get("indicators", [])
        
        if not indicators:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("🌍 FOREIGN CAREER EXPOSURE ANALYSIS")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Exposure Level: {exposure_level}")
        lines.append(f"Foreign Score: {score}")
        lines.append("")
        
        if indicators:
            lines.append("Key Indicators:")
            for ind in indicators[:5]:
                lines.append(f"  • {ind}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines)

    def _is_minor(self, **kwargs) -> bool:
        """
        Determine if native is under 18.
        Uses age_now first (preferred), fallback to dob.
        """
        try:
            age_now = kwargs.get("age_now")

            if age_now is not None:
                is_minor = age_now < 18
                logger.info(f"🧒 MINOR CHECK (age_now): {age_now}, IsMinor={is_minor}")
                return is_minor

            dob_str = kwargs.get("dob")
            if not dob_str:
                logger.info("🧒 MINOR CHECK: No DOB/age provided → Treating as NOT minor")
                return False

            dob = datetime.strptime(dob_str, "%d/%m/%Y")
            age = (datetime.now() - dob).days // 365
            is_minor = age < 18

            logger.info(f"🧒 MINOR CHECK (dob): {dob_str}, Age={age}, IsMinor={is_minor}")
            return is_minor

        except Exception as e:
            logger.error(f"❌ MINOR CHECK ERROR: {e}")
            return False
        
    def _minor_language_block(self, is_minor: bool) -> str:
        if not is_minor:
            return ""
        
        return """
    ═══════════════════════════════════════════════════════
    🎓 DEVELOPMENTAL MODE ACTIVE (Native Under 18)
    ═══════════════════════════════════════════════════════

    🔒 HARD CONSTRAINTS:

    1. DO NOT:
    - Recommend job change
    - Recommend resignation
    - Suggest workforce entry
    - Suggest business start now
    - Mention "career transition"
    - Mention "change career now"

    2. If dasha periods are discussed:
    - Interpret them as DEVELOPMENT PHASES
    - Use phrases like:
        "skill-building phase"
        "career clarity phase"
        "education strengthening period"
    - NEVER frame as employment activation

    3. Replace:
    "career shift" → "future career direction"
    "job change" → "long-term career planning"

    4. Focus on:
    - Education
    - Skill development
    - Academic alignment
    - Internship readiness (future)

    Current phase = Foundation & preparation.
    Career activation = Future (post education).

    ═══════════════════════════════════════════════════════
    """

    # ------------------------------------------------------------------
    # HELPER: Format KP Career Change Analysis (ENHANCED)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points, additional_data=None, is_minor=False):
        """
        Format KP-specific career change analysis points DETERMINISTICALLY.
        Uses CSL → Star Lord → Significations chain from evaluator.
        """
        # Extract from structured KP data
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_career_change_analysis", {})
        
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
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS (Career Houses):")
                lines.append("")
                
                # Order: 10, 6, 7, 11, 9, 3, 2, 12
                house_order = [10, 6, 7, 11, 9, 3, 2, 12]
                
                for house_num in house_order:
                    if house_num not in csl_details:
                        continue
                    
                    csl_info = csl_details[house_num]
                    
                    house_meaning = csl_info.get("house_meaning", "Career")
                    csl = csl_info.get("csl", "Unknown")
                    csl_flavor = csl_info.get("csl_flavor", "")
                    nakshatra = csl_info.get("nakshatra", "")
                    star_lord = csl_info.get("star_lord", "")
                    sig_houses = csl_info.get("signified_houses", [])
                    service_conn = csl_info.get("service_connection", 0)
                    business_conn = csl_info.get("business_connection", 0)
                    wealth_conn = csl_info.get("wealth_connection", 0)
                    verdict = csl_info.get("verdict", "NEUTRAL")
                    interpretation = csl_info.get("interpretation", "")
                    chain = csl_info.get("chain", "")
                    
                    # Verdict marker
                    if verdict in ["STRONG", "EXCELLENT", "FAVORABLE", "SERVICE_FAVORABLE", "PROMISING"]:
                        marker = "✅"
                    elif verdict in ["WEAK", "CHALLENGING"]:
                        marker = "⚠️"
                    elif verdict == "BUSINESS_LEANING":
                        marker = "🏢"
                    elif verdict == "SERVICE_LEANING":
                        marker = "💼"
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
                        lines.append(f"   Service Connection: {service_conn}/4 houses (2, 6, 10, 11)")
                        lines.append(f"   Business Connection: {business_conn}/5 houses (3, 5, 7, 9, 11)")
                        lines.append(f"   Wealth Connection: {wealth_conn}/3 houses (2, 10, 11)")
                    lines.append(f"   Verdict: {verdict}")
                    
                    if interpretation:
                        lines.append(f"   Why: {interpretation}")
                    
                    lines.append("")

            # Get career change suitability matrix
            change_matrix = additional_data.get("career_change_suitability_matrix", {}) if not is_minor else {}
            if change_matrix:
                matrix_text = self._format_career_change_matrix(change_matrix)
                lines.append(matrix_text)
                lines.append("")
                
            # Overall verdict with reasoning
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            if overall != "UNKNOWN":
                lines.append(f"📊 OVERALL KP VERDICT (Based on Significations): {overall}")
                lines.append("")
                
                # Provide interpretation based on verdict
                if overall == "SERVICE_PATH_DOMINANT":
                    lines.append("   💼 Star lord significations across 6-10-11 houses show strong")
                    lines.append("      service/employment capacity. Job/career stability indicated.")
                elif overall == "BUSINESS_PATH_INDICATED":
                    lines.append("   🏢 Star lord significations across 3-5-7-9-11 houses show")
                    lines.append("      business/self-employment capacity. Entrepreneurship favored.")
                elif overall == "CAREER_CHALLENGES_INDICATED":
                    lines.append("   ⚠️ Star lord significations show obstacles in career houses.")
                    lines.append("      Requires patience and skill development. Remedies recommended.")
                elif overall == "HYBRID_PATH_SUITABLE":
                    lines.append("   🔄 Both service and business houses are activated.")
                    lines.append("      Hybrid approach (Job + Side Business) may work best.")
                else:
                    lines.append("   ○ Moderate career change potential with mixed signification patterns.")
                
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
            lines.append("CAREER CHANGE Verdict Meanings:")
            lines.append("  • SERVICE_FAVORABLE: Significations support employment (2-6-10-11 connection)")
            lines.append("  • BUSINESS_LEANING: Significations support business (3-5-7-9-11 connection)")
            lines.append("  • CHALLENGING: Significations show obstacles")
            lines.append("  • FOREIGN_LINK: Foreign career connections indicated")
            lines.append("  • MODERATE: Mixed significations")
            lines.append("")
            lines.append("YOU MUST:")
            lines.append("  1. Quote the full chain for each house analyzed")
            lines.append("  2. Explain what significations mean for career change")
            lines.append("  3. Map significations to career path (Service/Business/Hybrid)")
            lines.append("  4. Give this PRIMARY weight (50%) in your final recommendation")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines), True
        
        # ═══════════════════════════════════════════════════════════════
        # FALLBACK: Use service_vs_business data
        # ═══════════════════════════════════════════════════════════════
        if additional_data:
            svb_data = additional_data.get("service_vs_business", {})
            
            if svb_data and svb_data.get("final_path"):
                lines = ["═══════════════════════════════════════════════════════"]
                lines.append("⭐ KP CAREER ANALYSIS (Pre-computed by Evaluator)")
                lines.append("═══════════════════════════════════════════════════════")
                lines.append("")
                lines.append("⚠️ CRITICAL: Give PRIMARY weight (50%) to KP findings below.")
                lines.append("")
                
                final_path = svb_data.get("final_path")
                lines.append(f"📍 Career Path: **{final_path}**")
                
                service_score = svb_data.get("service_score")
                business_score = svb_data.get("business_score")
                if service_score is not None:
                    lines.append(f"   Service Score: {service_score}")
                if business_score is not None:
                    lines.append(f"   Business Score: {business_score}")
                
                csl_10 = svb_data.get("10th_CSL")
                csl_7 = svb_data.get("7th_CSL")
                if csl_10:
                    lines.append(f"   10th CSL (Career): {csl_10}")
                if csl_7:
                    lines.append(f"   7th CSL (Business): {csl_7}")
                
                shift = svb_data.get("career_shift_likelihood")
                if shift:
                    lines.append(f"   Career Shift Likelihood: {shift}")
                
                lines.append("")
                lines.append("═══════════════════════════════════════════════════════")
                
                return "\n".join(lines), True
        
        # No KP data available
        return "", False

    # ------------------------------------------------------------------
    # HELPER: Format House Lords
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator"""
        if not house_lords_info:
            return ""
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("VEDIC HOUSE LORD ANALYSIS (Career Houses)")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        # Career-relevant houses in order of importance
        career_order = [10, 6, 7, 11, 9, 2, 3, 12]
        
        house_meanings = {
            2: "Income/Salary",
            3: "Initiative/Skills",
            6: "Service/Employment",
            7: "Business/Partnerships",
            9: "Fortune/Opportunities",
            10: "Career/Authority",
            11: "Gains/Recognition",
            12: "Foreign/Losses"
        }
        
        for house_num in career_order:
            if house_num not in house_lords_info:
                continue
            
            info = house_lords_info[house_num]
            
            marker = "⭐ PRIMARY" if info.get("priority") == "primary" else "○ SECONDARY"
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
                lines.append("  ✅ Assessment: STRONG - Supports career growth")
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
        lines.append("PLANETARY ASPECTS ON CAREER HOUSES")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        
        career_houses = [10, 6, 7, 11, 9, 2, 3, 12]
        
        for house_num in career_houses:
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
                "Use for analyzing present career circumstances.",
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
                lines.append("⏭️  UPCOMING DASHA PERIODS (Next 10 Years - for career planning):")
                lines.append("-" * 60)
                lines.append("Use these periods for career change timing:")
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
            lines.append("CAREER DASHA GUIDELINES:")
            lines.append("- Saturn periods favor stability, discipline-based growth")
            lines.append("- Jupiter periods support expansion, education, advisory roles")
            lines.append("- Mercury periods favor trading, communication, IT")
            lines.append("- Venus periods support creative, luxury, entertainment fields")
            lines.append("- Sun periods favor authority positions, government")
            lines.append("- Mars periods favor technical, competitive, real estate")
            lines.append("- Rahu periods favor technology, foreign, unconventional")
            lines.append("═══════════════════════════════════════════════════════")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Check if career change is blocked
    # ------------------------------------------------------------------
    def _is_blocked(self, additional_data: Dict) -> bool:
        """Check if career change is blocked based on KP analysis"""
        if not additional_data:
            return False
        
        # Check KP structured analysis
        kp_analysis = additional_data.get("kp_career_change_analysis", {})
        if kp_analysis.get("overall_verdict") == "CAREER_CHALLENGES_INDICATED":
            return True
        
        # Check service vs business
        svb = additional_data.get("service_vs_business", {})
        if svb.get("career_shift_likelihood") == "No":
            service_score = svb.get("service_score", 0)
            business_score = svb.get("business_score", 0)
            if (service_score + business_score) < 5:
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

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - What does the 10th cusp sub lord signify? (career/authority)
   - What does the 6th cusp sub lord signify? (service/employment)
   - What does the 7th cusp sub lord signify? (business/partnerships)
   - KP verdict: Service or Business or Hybrid path?

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - 10th house lord strength (career capacity)
   - 6th house lord strength (employment potential)
   - 7th house lord strength (business potential)
   - Saturn's condition (career karaka)

3. **TIMING ANALYSIS** (15% weight - CRITICAL FOR THIS QUESTION):
   ⚠️ MUST analyze BOTH timing windows provided:
   
   A. BEST WINDOW (Highest score):
      - When: Exact dates from timing data
      - Why favorable: Dasha lords + career significations
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
   - Combine KP path + Vedic capacity + Timing recommendation
   - Give clear career change guidance with specific dates
"""
            elif question_type == "timing":
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight):
   - Career path determination (Service/Business/Hybrid)
   - Career shift likelihood
   - Key CSL significations

2. **ADD Vedic Context** (SECONDARY - 30% weight):
   - House lord strengths
   - Saturn's role
   - Supporting planets

3. **Include Career Change Matrix** (15% weight):
   - Which change types are favorable
   - Which to avoid

4. **Synthesize** (5% weight):
   - Combine KP + Vedic for final recommendation
"""
            else:
                return """
**ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM**

**FOLLOW THIS ORDER STRICTLY:**

1. **START with KP Analysis** (PRIMARY - 50% weight)
2. **ADD Vedic Context** (SECONDARY - 30% weight)
3. **Include Dasha Context** (15% weight)
4. **Synthesize** (5% weight)
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
   - Detailed analysis of career houses (10, 6, 7)
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

        if "Timing" in sub_subdomain:
            return self._build_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Advice" in sub_subdomain:
            return self._build_advice_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Challenges" in sub_subdomain:
            return self._build_challenges_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # TIMING PROMPT (Career Shift Timing - WITH TIMING!)
    # ------------------------------------------------------------------
    def _build_timing_prompt(
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
        is_minor = self._is_minor(**kwargs)
        minor_block = self._minor_language_block(is_minor)
        
        # Get all data structures
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        change_matrix = additional_data.get("career_change_suitability_matrix", {})
        svb_data = additional_data.get("service_vs_business", {})
        foreign_data = additional_data.get("foreign_career_exposure", {})
        
        # ✅ Get timing windows
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        # 🔒 HARD MINOR OVERRIDE
        if is_minor:
            has_timing = False
            timing_windows_data = {}   # completely wipe timing data
        
        # Check if blocked
        is_blocked = self._is_blocked(additional_data)

        logger.info(f"🔍 PROMPT DEBUG: timing_windows_data present: {bool(timing_windows_data)}")
        logger.info(f"🔍 PROMPT DEBUG: has_timing flag: {has_timing}")
        logger.info(f"🔍 PROMPT DEBUG: is_blocked: {is_blocked}")
        
        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data,is_minor)
        
        # Format other sections
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        svb_formatted = self._format_service_vs_business(svb_data)
        foreign_formatted = self._format_foreign_exposure(foreign_data)
        
        # ✅ Format timing windows (only if not blocked)
        timing_formatted = ""
        if has_timing and not is_blocked and not is_minor:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)

        # 🔒 Do NOT show long-term activation timeline for minors
        timeline_block = "" if is_minor else self._format_dasha_timeline(dasha_timeline)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "connects to", "kp", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        # Determine question type
        question_type = "timing" if has_timing and not is_blocked else "timing"
        if is_minor:
            analysis_instructions = """
        ⚠️ MINOR MODE:
        - Do NOT provide career shift timing.
        - Do NOT mention specific future activation years.
        - Interpret dasha as developmental energy only.
        - Focus on education and preparation.
        """
        else:
            analysis_instructions = self._get_analysis_instructions(
                kp_available,
                question_type,
                has_timing and not is_blocked
            )
        
        # Blocked state handling
        blocked_section = ""
        if is_blocked:
            blocked_section = """
═══════════════════════════════════════════════════════
⚠️ CAREER CHANGE CHALLENGING - FOCUS ON PREPARATION
═══════════════════════════════════════════════════════

The chart shows some challenges for immediate career transition.

🚫 DO NOT provide specific timing windows or dates.
✅ DO mention current dasha period for general context.
✅ DO recommend skill development and preparation.
✅ DO provide remedies to strengthen career prospects.
✅ Frame challenges as TEMPORARY and CORRECTABLE.

MESSAGE: "Career challenges are preparation phases, not permanent blocks.
Focus on skill development and the right time will come."
═══════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Career
- Subtopic: Career Changes
- Sub-subdomain: Career Shift Timing (When to change career?)
- Query Type: {'TIMING' if has_timing and not is_blocked and not is_minor else 'NON_TIMING'}
- Timing Windows Available: {'YES' if has_timing and not is_blocked and not is_minor else 'NO'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}
- Career Change Blocked: {'YES - Focus on preparation' if is_blocked else 'NO'}

USER QUESTION:
"{question}"

{minor_block}

{blocked_section}

{timing_formatted}

{kp_formatted}

{svb_formatted}

{foreign_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

CRITICAL INSTRUCTIONS:
{'⚠️ TIMING WINDOWS PROVIDED ABOVE - MUST USE IN YOUR ANSWER!' if has_timing and not is_blocked else ''}
{'- Mention BOTH best and nearest windows with exact dates' if has_timing and not is_blocked else ''}
{'- Explain why each window is favorable for career change' if has_timing and not is_blocked else ''}
{'- Let user choose: wait for best OR act sooner' if has_timing and not is_blocked else ''}
{'- If best = nearest, emphasize this is ideal timing' if has_timing and not is_blocked else ''}
{'⚠️ CAREER CHANGE IS CHALLENGING - Focus on preparation and remedies' if is_blocked else ''}

GUIDELINES:
- 10th house shows career authority
- 6th house shows service/employment
- 7th house shows business/partnerships
- Saturn is the karaka for career discipline
- Provide practical, actionable guidance

{self.get_output_format_for_minor(kp_available) if is_minor 
 else self.get_output_format(kp_available, has_timing and not is_blocked, "timing")}
"""

    # ------------------------------------------------------------------
    # ADVICE PROMPT (Career Shift Advice)
    # ------------------------------------------------------------------
    def _build_advice_prompt(
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
        is_minor = self._is_minor(**kwargs)
        minor_block = self._minor_language_block(is_minor)
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        svb_data = additional_data.get("service_vs_business", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data,is_minor)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        svb_formatted = self._format_service_vs_business(svb_data)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        current_dasha_block = self._format_current_dasha(current_dasha)
        
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp", "sub-lord", "sub lord", "csl", "signif", "kp"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""
        
        analysis_instructions = self._get_analysis_instructions(kp_available, "advice", False)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Career
- Subtopic: Career Changes
- Sub-subdomain: Career Shift Advice (Education/Reskilling)
- Query Type: NON_TIMING (Practical Advice Question)
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}


USER QUESTION:
"{question}"

{minor_block}

{kp_formatted}

{svb_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

{analysis_instructions}

CRITICAL GUIDELINES FOR ADVICE:
- Focus on PRACTICAL recommendations
- 5th house shows education/learning ability
- 9th house shows higher education
- Mercury shows communication/skills
- Connect astrology to actionable decisions

{self.get_output_format(kp_available, False, "advice")}
"""

    # ------------------------------------------------------------------
    # CHALLENGES PROMPT
    # ------------------------------------------------------------------
    def _build_challenges_prompt(
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
        is_minor = self._is_minor(**kwargs)
        minor_block = self._minor_language_block(is_minor)
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        # For challenges, KP can provide context
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data,is_minor)
        
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
- Domain: Career
- Subtopic: Career Changes
- Sub-subdomain: Career Challenges (Obstacles Analysis)
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}


USER QUESTION:
"{question}"

{minor_block}

⚠️ CRITICAL SENSITIVITY RULES:
- NEVER induce fear about career obstacles
- Frame as "areas needing attention" not "problems"
- All challenges are TRANSITIONAL, not permanent
- Emphasize adaptability and patience
- Focus on constructive solutions

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

CHALLENGE AREAS TO ANALYZE:
- 10th house obstacles (career blocks)
- 6th house issues (workplace conflicts)
- 8th house influences (sudden changes)
- 12th house effects (losses, resignations)
- Malefic aspects on career houses
- Saturn and Mars influences

{self.get_output_format(kp_available, False, "challenges")}
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
        is_minor = self._is_minor(**kwargs)
        minor_block = self._minor_language_block(is_minor)
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data,is_minor)
        
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
- Domain: Career
- Subtopic: Career Changes
- Sub-subdomain: Career Remedies
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}


USER QUESTION:
"{question}"

{minor_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{'ADDITIONAL CONTEXT:' if raw else ''}
{raw}

REMEDY GUIDELINES FOR CAREER:

1. **Identify Weak Planets**:
   {'- Weak KP cusp sub lords (if KP available)' if kp_available else ''}
   - Weak Vedic house lords (debilitated/combust/poorly placed)
   - Focus on 10th, 6th, 7th house lords

2. **Current Dasha Lord Remedies**:
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords

3. **Priority**:
   - Primary: 10th house lord (career authority)
   - Secondary: 6th/7th house lords (service/business)
   - Tertiary: Saturn (career karaka)

PLANETARY REMEDY GUIDE:
- SATURN: Discipline, service (Blue Sapphire, "Om Shanicharaya Namaha")
- SUN: Authority, leadership (Ruby, "Om Suryaya Namaha")
- JUPITER: Growth, expansion (Yellow Sapphire, "Om Gurave Namaha")
- MERCURY: Communication, skills (Emerald, "Om Budhaya Namaha")

{self.get_output_format(kp_available, False, "remedies")}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK PROMPT
    # ------------------------------------------------------------------
    def _build_general_prompt(
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
        is_minor = self._is_minor(**kwargs)
        minor_block = self._minor_language_block(is_minor)
        
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data,is_minor)
        
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = "" if is_minor else self._format_dasha_timeline(dasha_timeline)
        
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
- Domain: Career
- Subtopic: Career Changes
- Query Type: {meta.query_type if meta else 'UNKNOWN'}
- CURRENT DATE: {today}
- KP Analysis Available: {'YES' if kp_available else 'NO'}


USER QUESTION:
"{question}"

{minor_block}

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

⚠️ IMPORTANT: Include both timing options and explain the difference clearly.

**🏆 BEST WINDOW (Highest Astrological Score):**
- Period: [exact start date] to [exact end date] (from timing data)
- Dasha: [Maha-Antara-Pratyantar] (exact dasha name from data)
- Age at start: [age] years
- Astrological Score: [final_score]/100
- Why this is BEST:
  * Maha Dasha lord ([planet]): [career significations] → Score [X]/10
  * Antara Dasha lord ([planet]): [career support] → Score [Y]/10
  * Pratyantar Dasha lord ([planet]): [final trigger] → Score [Z]/10
- Trade-off: [e.g., "May be further in future, but strongest alignment"]

**⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):**
- Period: [exact start date] to [exact end date] (from timing data)
- Dasha: [Maha-Antara-Pratyantar] (exact dasha name from data)
- Age at start: [age] years
- Astrological Score: [final_score]/100
- Why this is NEAREST:
  * [Explain why this window comes sooner]
  * [Still has favorable score >= 50]
- Trade-off: [e.g., "Sooner but not absolute best alignment"]

**👤 USER RECOMMENDATION (Help them decide):**
Choose BEST window if:
- You can wait for optimal career change timing
- You want maximum success in new role
- Long-term career stability is priority

Choose NEAREST window if:
- You want to make the change sooner
- Good enough results acceptable
- Cannot wait for best timing

⚠️ Special case: If BEST = NEAREST (same window):
"🎯 IDEAL TIMING: The best window IS the nearest favorable window!"
"""
        else:
            timing_section = ""
        
        if kp_available:
            return f"""

⚠️ IMPORTANT FLOW RULE:
Your answer must read like a guided explanation — not a technical report.

Structure the reasoning in narrative order:
KP → Vedic → Dasha → Synthesis → Clear Recommendation.

Do NOT dump disconnected sections.
Each section must logically lead to the next.


OUTPUT FORMAT (STRICT):

**GENERAL_ANSWER:**
<Write a clear, practical answer in simple layman's terms. NO astrological jargon.>
<State career path (Service/Business/Hybrid) clearly.>

**ASTROLOGICAL_ANALYSIS:**

⚠️ CRITICAL: Follow CORRECT KP methodology - CSL → Star Lord → Significations → Result

**A. KP SYSTEM ANALYSIS (Primary - 50% weight):**

For EACH career cusp analyzed (10th, 6th, 7th), present in this EXACT format:

**House [N] ([Meaning - e.g., Career/Authority]):**
- Cusp Sub Lord (CSL): [Planet name] ([benefic/malefic/neutral] flavor)
- CSL in Nakshatra: [Nakshatra name]
- Star Lord: [Planet name]
- Star Lord Signifies: Houses [X, Y, Z] (from actual data - never guess!)
- Service Connection: [N]/4 (overlap with houses 2, 6, 10, 11)
- Business Connection: [N]/5 (overlap with houses 3, 5, 7, 9, 11)
- **Verdict: [SERVICE_FAVORABLE/BUSINESS_LEANING/etc]** ← Based on SIGNIFICATIONS only
- Why: [Explain how significations lead to verdict]

**B. CAREER CHANGE SUITABILITY MATRIX (From KP Significations):**

| Change Type | Suitability | KP Reasoning |
|-------------|-------------|--------------|
| **Service to Business** | [HIGH/MODERATE/LOW] | [Based on 7th house significations] |
| **Business to Service** | [HIGH/MODERATE/LOW] | [Based on 6th/10th house significations] |
| **Hybrid Career** | [HIGH/MODERATE/LOW] | [Based on balanced significations] |
| **Technical to Management** | [HIGH/MODERATE/LOW] | [Based on 10th + 9th houses] |
| **Domestic to Foreign** | [HIGH/MODERATE/LOW] | [Based on 12th + Rahu] |

**C. VEDIC SYSTEM ANALYSIS (Secondary - 30% weight):**

**1. Lagna Lord Analysis (Career Personality):**
- Planet: [Name] (lord of [Ascendant sign])
- Placed in: House [N], Sign [Name]
- Career Personality: [Leadership/Communication/Technical/etc]

**2. Career House Lords Analysis (10th, 6th, 7th):**

- **10th Lord ([Planet])**: [Placement, dignity, strength]
  → [Does this CONFIRM KP's career verdict?]

- **6th Lord ([Planet])**: [Placement, dignity, strength]
  → [Service/employment capacity?]

- **7th Lord ([Planet])**: [Placement, dignity, strength]
  → [Business/partnership capacity?]

**Vedic-KP Agreement Check:**
- If both agree: "✅ Vedic CONFIRMS KP: [Explanation]"
- If they differ: "⚠️ KP shows [X] BUT Vedic shows [Y]. KP takes priority."

**D. UNIFIED SYNTHESIS (5% weight):**

Combine: KP significations + Vedic capacity + Lagna personality → Final recommendation

**FINAL CAREER RECOMMENDATION:**
[Clear statement: Service/Business/Hybrid path]
[Suitable career change types]
[Action steps]

**E. DASHA TIMING ANALYSIS (15% weight):**

**Current Dasha Impact:**
- Dasha: [Current Maha-Antara-Pratyantar]
- Period: [Start] to [End]
- Career Impact: [How this affects career NOW]

{timing_section}

**SUMMARY:**
<Concise 2-3 sentence career outlook with {('specific timing dates' if has_timing else 'path guidance')}>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets affecting career houses]
- [Strengthen 10th house lord]

**REMEDIES_GENERAL:**
- [Skill development aligned with chart]
- [Practical career actions]
"""
        else:
            # Vedic only format
            return f"""
OUTPUT FORMAT (STRICT):

**GENERAL_ANSWER:**
<Clear, practical career answer in simple terms.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD ANALYSIS (Career Personality - 20% weight):**
- Planet: [Name] (lord of [Ascendant sign])
- Placed in: House [N], Sign [Name]
- Career Personality: [Description]

**B. VEDIC HOUSE LORD ANALYSIS (Primary - 60% weight):**

**Career Houses (10th, 6th, 7th) - Detailed Analysis:**

For each house:
- Lord: [Planet]
- Placement: House [N], Sign [Name]
- Dignity: [Status]
- Strength: [X]/100
- Assessment: [STRONG/MODERATE/WEAK]
- Career Impact: [How this affects career]

**Saturn Analysis (Career Karaka):**
- Position: House [N], Sign [Name]
- Career Influence: [Assessment]

**C. CAREER SUITABILITY:**

| Path | Suitability | Reasoning |
|------|-------------|-----------|
| **Service/Employment** | [HIGH/MODERATE/LOW] | [Based on 6th/10th lords] |
| **Business** | [HIGH/MODERATE/LOW] | [Based on 7th lord] |
| **Hybrid** | [HIGH/MODERATE/LOW] | [Based on balance] |

**D. DASHA TIMING (20% weight):**

**Current Dasha Impact:**
- Dasha: [Current]
- Career Effect: [How it affects career NOW]

{timing_section}

**E. FINAL VERDICT:**

**CAREER RECOMMENDATION:**
[Clear recommendation]
[Action steps]

**SUMMARY:**
<Concise career outlook>

**REMEDIES_ASTROLOGICAL:**
- [Strengthen weak house lords]
- [Saturn remedies if needed]

**REMEDIES_GENERAL:**
- [Practical career advice]
"""
        
    def get_output_format_for_minor(self, kp_available: bool) -> str:
            """
            Special output format for natives under 18.
            Removes employment timing and career shift framing.
            """

            return """
        OUTPUT FORMAT (MINOR MODE):

        **GENERAL_ANSWER:**
        <Explain long-term career inclination in simple terms.>
        <Do NOT suggest immediate career change.>

        **ASTROLOGICAL_ANALYSIS:**

        **A. CAREER ORIENTATION (Long-Term Tendency):**
        - Service / Business / Hybrid inclination
        - Natural strengths based on KP + Vedic

        **B. EDUCATION & SKILL DEVELOPMENT DIRECTION:**
        - Fields suited based on planetary strengths
        - Type of learning environment preferred

        **C. CURRENT DASHA = DEVELOPMENT PHASE:**
        - Interpret as preparation cycle
        - Focus on skill-building and foundation

        **D. LONG-TERM CAREER ACTIVATION:**
        - Mention future years only as orientation phase
        - Do NOT frame as job-switch window

        **SUMMARY:**
        <Encourage structured preparation.>

        **REMEDIES_ASTROLOGICAL:**
        - Strengthen education-supporting planets

        **REMEDIES_GENERAL:**
        - Skill-building roadmap
        - Academic focus suggestions
        """
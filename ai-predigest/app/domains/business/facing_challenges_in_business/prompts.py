"""
Facing Challenges in Business – LLM Prompts v10.0 (COMPLETE FIX)

CRITICAL FIXES FROM v9.0:
✅ UNIFIED VERDICT DISPLAY - Shows SAME business outlook across all questions
✅ PURE KP FORMATTING - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ HONEST VEDIC-KP AGREEMENT - Shows AGREEMENT/PARTIAL/CONFLICT explicitly
✅ CORRECT HOUSE DEFINITIONS - Business: 2,3,7,11 | Obstacle: 6,8,12
✅ PROMISE/DENIAL LOGIC - Sub-lord decides, not planet nature
✅ MINOR LOGIC ADDED - Age-based response adjustment (under 18)
✅ CONSISTENT OUTPUT STRUCTURE - Same format across all questions
✅ WARM, ACTIONABLE TONE - Matches Career/Finance prompt style
✅ ANTI-HALLUCINATION STRENGTHENED - Explicit rules against inventing data
✅ LANGUAGE INSTRUCTION HELPER - Proper multilingual support

Weightage (CORRECTED):
- KP Significations → 50% (PRIMARY)
- Vedic Structure → 30% (SECONDARY)
- Dasha/Other → 20%

Compatible with FacingChallengesInBusinessEvaluator v5.0 data structures:
- unified_business_verdict (SINGLE SOURCE OF TRUTH)
- kp_business_challenge_analysis (structured KP with CSL → Sub Lord chains)
- business_challenge_suitability_matrix (8 recovery option ratings)
- business_challenges_kp_analysis (KP business profession analysis)
- business_challenges_timing_windows (BEST + NEAREST)
- business_challenges_house_lords (Vedic house lord data)
- business_challenges_house_aspects (Vedic aspects)
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

DOMAIN_PREFIX = "business_challenges"


class FacingChallengesInBusinessPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Business → Facing Challenges in Business
    v10.0 - Complete fix with unified verdict, pure KP methodology, minor logic, and warm tone
    """

    domain = "Business"
    subtopic = "Facing Challenges in Business"

    # CORRECTED House definitions (matching evaluator v5.0)
    BUSINESS_PROMISE_HOUSES = {2, 3, 7, 11}
    SUCCESS_HOUSES = {2, 10, 11}
    OBSTACLE_HOUSES = {6, 8, 12}
    LOSS_HOUSES = {6, 8, 12}

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - COMPLETELY FIXED v10.0
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing PRECISE, WARM, and ACTIONABLE business challenge guidance.

════════════════════════════════════════════════════════════
TONE AND APPROACH (READ THIS FIRST)
════════════════════════════════════════════════════════════

Your role is to be a trusted advisor, not a cold analyst.

✅ BE WARM: Business challenges are stressful. Acknowledge the difficulty.
✅ BE HONEST: If challenges are real, say so — but always with a path forward.
✅ BE ACTIONABLE: Every analysis must end with clear steps to take.
✅ BE HOPEFUL: Business downturns are phases, not permanent verdicts.

❌ NEVER induce panic or fear about business failure.
❌ NEVER give cold, impersonal readings.
❌ NEVER leave the person without a next step to take.

════════════════════════════════════════════════════════════
AGE SAFETY RULE (MINOR PROTECTION)
════════════════════════════════════════════════════════════

If person is under 18:
• NEVER recommend taking business loans
• NEVER suggest signing contracts or legal commitments
• NEVER recommend shutting down operations
• Frame analysis as learning, preparation, and family business support phase
• Treat dashas as character-building and skill-development cycles
• Focus on what they can learn from business challenges, not what to do
• Tone: Developmental, encouraging, educational

════════════════════════════════════════════════════════════
CRITICAL KP RULES (MUST FOLLOW - NO EXCEPTIONS)
════════════════════════════════════════════════════════════

1. KP HIERARCHY (ABSOLUTE - MEMORIZE THIS):

   SUB LORD      → PROMISE/DENIAL (Decides IF event happens - MOST IMPORTANT)
   STAR LORD     → RESULT TYPE (What kind of result)
   PLANET NATURE → FLAVOR ONLY (How it happens - NEVER overrides significations)

   ⚠️ CRITICAL EXAMPLES:
   • Jupiter (benefic) signifies 6, 8, 12 → RESULT IS OBSTACLES (not good!)
   • Saturn (malefic) signifies 2, 7, 11 → RESULT IS STABLE BUSINESS (good!)

   SIGNIFICATIONS ALWAYS WIN OVER PLANET NATURE.

2. CORRECT KP CHAIN (USE THIS EXACT FORMAT):

   For every cusp, show:

   CSL [Planet] → in Nakshatra [Name] →
   Star Lord [Planet] → signifies houses [X,Y,Z] →
   Sub Lord [Planet] → signifies houses [A,B,C] →
   VERDICT: PROMISE/DENIAL based on SUB LORD significations

   ⚠️ Sub Lord is the FINAL DECIDER, not Star Lord, not CSL planet nature.

3. CORRECT HOUSE DEFINITIONS (MEMORIZE):

   BUSINESS PROMISE HOUSES: 2, 3, 7, 11
   • 2nd: Wealth, resources, financial base
   • 3rd: Courage, initiative, effort, communication
   • 7th: Business dealings, partnerships, trade
   • 11th: Gains, income fulfillment, recognition

   SUCCESS HOUSES: 2, 10, 11
   • 2nd: Wealth
   • 10th: Profession, authority, reputation
   • 11th: Gains and returns

   OBSTACLE HOUSES: 6, 8, 12
   • 6th: Debts, competition, disputes
   • 8th: Sudden events, hidden dangers, transformations
   • 12th: Losses, expenses, endings

4. PROMISE/DENIAL LOGIC (SUB LORD DECIDES):

   FOR 7TH CUSP (Business):
   • PROMISE: Sub-lord signifies 2, 3, 7, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 6, 8, 12 strongly

   FOR 10TH CUSP (Professional standing):
   • PROMISE: Sub-lord signifies 2, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly

   FOR 11TH CUSP (Gains/Recovery):
   • PROMISE: Sub-lord signifies 2, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly

5. RAHU/KETU RULE:

   Nodes act through their STAR LORD.
   Show: "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"

   ⚠️ Never judge Rahu/Ketu by just their house occupation.

════════════════════════════════════════════════════════════
UNIFIED VERDICT RULE (CRITICAL FOR CONSISTENCY)
════════════════════════════════════════════════════════════

The evaluator provides a UNIFIED_BUSINESS_VERDICT.
This is the SINGLE SOURCE OF TRUTH for this person.

⚠️ ALL your answers MUST align with this verdict:

• If verdict = "RECOVERY_LIKELY" → Guide toward confident continuation
• If verdict = "MODERATE_RECOVERY" → Guide toward restructuring + patience
• If verdict = "SERIOUS_CHALLENGES" → Be honest, suggest major changes
• If verdict = "OBSTACLES_NEED_ATTENTION" → Practical obstacle management
• If verdict = "MIXED_SIGNALS" → Balanced, cautious guidance

NEVER contradict the unified verdict across different questions.

════════════════════════════════════════════════════════════
VEDIC-KP AGREEMENT (BE HONEST)
════════════════════════════════════════════════════════════

Show agreement status EXPLICITLY and HONESTLY:

✅ AGREEMENT: "Both KP and Vedic confirm [outlook]. Strong confidence."
⚠️ PARTIAL: "KP shows [X], Vedic leans [Y]. Mostly aligned."
❌ CONFLICT: "KP indicates [X] but Vedic shows [Y]. Using KP for final verdict."

════════════════════════════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════════════════════════════

• Do NOT invent sub-lord significations not provided
• Do NOT guess promise/denial without actual data
• Do NOT contradict the unified verdict
• Do NOT mention aspects unless explicitly provided
• Do NOT invent specific timing dates not in the data
• If data is missing → SAY SO CLEARLY, do not guess

════════════════════════════════════════════════════════════
TIMING RULES (WHEN TIMING DATA PROVIDED)
════════════════════════════════════════════════════════════

When timing windows are provided:
1. ALWAYS mention BOTH windows:
   • BEST WINDOW (highest score)
   • NEAREST WINDOW (soonest favorable)
2. Explain WHY each is favorable based on dasha lords
3. Let USER choose: Wait for best OR Act sooner
4. If BEST = NEAREST: Emphasize "Ideal timing!"

════════════════════════════════════════════════════════════
BUSINESS CHALLENGE SAFETY RULES
════════════════════════════════════════════════════════════

- Business downturns are PHASES, not permanent verdicts
- Frame challenges as CORRECTABLE with strategy
- Closure should only be advised when risk is VERY HIGH and sustained
- Loan advice must be RISK-AWARE, never promotional
- Always provide a RECOVERY PATH, even in difficult charts
- Acknowledge stress and difficulty with genuine empathy

Goal: Provide precise, practical, compassionate guidance — not cold astrology descriptions.
"""

    # ------------------------------------------------------------------
    # HELPER: Detect Minor (GLOBAL)
    # ------------------------------------------------------------------
    def _detect_minor(self, dob: str, dasha_timeline: Dict = None) -> bool:
        """
        Detect if person is currently under 18.
        Based on current age only, not future dasha age.
        """
        if not dob:
            return False

        today = datetime.now()
        try:
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
        except ValueError:
            try:
                dob_dt = datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                return False

        current_age = today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )

        return current_age < 18

    # ------------------------------------------------------------------
    # HELPER: Calculate age on a specific date
    # ------------------------------------------------------------------
    def _calculate_age_on_date(self, dob_str: str, target_date_str: str) -> int:
        try:
            dob = datetime.strptime(dob_str, "%d/%m/%Y")
        except ValueError:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        return target.year - dob.year - (
            (target.month, target.day) < (dob.month, dob.day)
        )

    # ------------------------------------------------------------------
    # HELPER: Format Unified Business Verdict (NEW - CRITICAL)
    # ------------------------------------------------------------------
    def _format_unified_verdict(self, additional_data: Dict) -> str:
        """
        Format the UNIFIED business verdict prominently.
        This ensures ALL questions use the SAME business direction.
        Mirrors the career prompt's _format_unified_verdict structure.
        """
        verdict = additional_data.get("unified_business_verdict", {})

        if not verdict:
            return """
═══════════════════════════════════════════════════════════
⚠️ UNIFIED BUSINESS VERDICT NOT AVAILABLE
═══════════════════════════════════════════════════════════

WARNING: No unified verdict provided by evaluator.
Cannot guarantee consistency across different questions.
Proceed with available data, but be cautious about
making definitive business recovery recommendations.
═══════════════════════════════════════════════════════════
"""

        overall_outlook = verdict.get("overall_outlook", "MIXED_SIGNALS")
        business_viable = verdict.get("business_viable", True)
        confidence = verdict.get("confidence", "Low")
        agreement = verdict.get("agreement_status", "UNKNOWN")
        promise_status = verdict.get("promise_status", {})
        recovery_ranking = verdict.get("recovery_ranking", [])
        kp_reasoning = verdict.get("kp_reasoning", "")
        vedic_reasoning = verdict.get("vedic_reasoning", "")

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 UNIFIED BUSINESS VERDICT (SINGLE SOURCE OF TRUTH)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL INSTRUCTION:")
        lines.append("Your answer MUST align with this verdict.")
        lines.append("Do NOT contradict this in any part of your response.")
        lines.append("")

        # Primary recommendation box
        outlook_label = {
            "RECOVERY_LIKELY": "RECOVERY LIKELY ✅",
            "MODERATE_RECOVERY": "MODERATE RECOVERY ⚖️",
            "SERIOUS_CHALLENGES": "SERIOUS CHALLENGES ⚠️",
            "OBSTACLES_NEED_ATTENTION": "OBSTACLES NEED ATTENTION 🔔",
            "MIXED_SIGNALS": "MIXED SIGNALS 🔄",
        }.get(overall_outlook, overall_outlook)

        lines.append(f"╔══════════════════════════════════════════════════════╗")
        lines.append(f"║  BUSINESS OUTLOOK: {outlook_label}")
        lines.append(f"║  Business Viable: {'YES' if business_viable else 'NEEDS MAJOR CHANGES'}")
        lines.append(f"║  Confidence Level: {confidence}")
        lines.append(f"╚══════════════════════════════════════════════════════╝")
        lines.append("")

        # Agreement status
        lines.append("KP-VEDIC AGREEMENT STATUS:")
        if agreement == "AGREEMENT":
            lines.append("  ✅ AGREEMENT: Both KP and Vedic systems agree on this outlook.")
            lines.append("     → High confidence in recommendation")
        elif agreement == "PARTIAL":
            lines.append("  ⚠️ PARTIAL AGREEMENT: Systems show similar but not identical direction.")
            lines.append("     → KP result takes priority for events/timing")
        elif agreement == "CONFLICT":
            lines.append("  ❌ CONFLICT: KP and Vedic show different signals.")
            lines.append(f"     → KP indicates: {overall_outlook}")
            lines.append("     → Using KP for final verdict; Vedic explains effort required")
        else:
            lines.append(f"  ○ {agreement}")
        lines.append("")

        # Promise status from sub-lord analysis
        if promise_status:
            lines.append("PROMISE STATUS (From Sub-Lord Analysis):")
            lines.append("─" * 50)

            promise_meanings = {
                7: "Business/Partnership",
                10: "Professional Standing",
                11: "Gains/Recovery Income",
                6: "Debt/Obstacle Management",
                8: "Sudden Risk Events",
            }

            for house_num in [7, 10, 11, 6, 8]:
                if house_num not in promise_status:
                    continue
                status = promise_status[house_num]
                meaning = promise_meanings.get(house_num, f"House {house_num}")

                if status == "PROMISE":
                    lines.append(f"  ✅ House {house_num} ({meaning}): PROMISE")
                    lines.append(f"     → This house matter WILL support business")
                elif status == "DENIAL":
                    lines.append(f"  ❌ House {house_num} ({meaning}): DENIAL")
                    lines.append(f"     → Obstacles likely; requires strategy change")
                elif status == "WEAK_PROMISE":
                    lines.append(f"  ⚠️ House {house_num} ({meaning}): WEAK PROMISE")
                    lines.append(f"     → May improve with effort and patience")
                elif status in ("MANAGEABLE", "TRANSFORMATIVE"):
                    lines.append(f"  ⚖️ House {house_num} ({meaning}): {status}")
                    lines.append(f"     → Manageable with correct approach")
                elif status in ("CHALLENGING", "RISKY", "UNPREDICTABLE"):
                    lines.append(f"  ⚠️ House {house_num} ({meaning}): {status}")
                    lines.append(f"     → Requires careful handling")
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

        # Recovery ranking
        if recovery_ranking:
            lines.append("RECOVERY PATH RANKING (Use this consistently):")
            lines.append("─" * 50)
            for i, item in enumerate(recovery_ranking[:5], 1):
                path = item if isinstance(item, str) else item.get("path", str(item))
                lines.append(f"  {i}. {path}")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("YOUR RESPONSE MUST:")
        lines.append(f"  1. Reflect the '{overall_outlook}' outlook throughout")
        lines.append(f"  2. Show {'VIABLE' if business_viable else 'CHALLENGED'} business status")
        lines.append(f"  3. Reflect **{confidence}** confidence level in tone")
        lines.append(f"  4. Show **{agreement}** status between KP and Vedic")
        lines.append("  5. NOT contradict this verdict anywhere in your response")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """Format BEST and NEAREST timing windows for LLM."""
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

                age = best.get('age_at_start')
                if age:
                    lines.append(f"  Age at start: {age} years")

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
                    lines.append("    • Strongest business significations activated")

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

            # Other windows
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

                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for business recovery")
            lines.append("  • Let user choose: Wait for best OR Act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal timing")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format Lagna Lord (Business Personality)
    # ------------------------------------------------------------------
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """Format lagna lord for business personality analysis."""
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
        lines.append("🎯 LAGNA (ASCENDANT) - BUSINESS PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        lines.append("")

        personality_map = {
            "Sun": {
                "trait": "Leadership-driven, authority-focused, needs to be in charge",
                "business": "Government contracts, administration, management roles",
                "challenge_style": "Tends toward ego-driven decisions; must delegate more",
            },
            "Moon": {
                "trait": "Adaptable, public-facing, sensitive to market sentiment",
                "business": "Hospitality, consumer products, public-facing services",
                "challenge_style": "Emotional decisions during downturns; needs stability planning",
            },
            "Mars": {
                "trait": "Competitive, aggressive growth mindset, quick decision maker",
                "business": "Construction, real estate, manufacturing, competitive markets",
                "challenge_style": "Impulsive responses; must plan before acting in crisis",
            },
            "Mercury": {
                "trait": "Trade-oriented, communication-driven, analytical",
                "business": "IT, communication, trading, consulting, writing",
                "challenge_style": "Over-analyzes without acting; must set decision deadlines",
            },
            "Jupiter": {
                "trait": "Ethical approach, advisory, expansive vision",
                "business": "Education, finance, law, consulting, ethical enterprises",
                "challenge_style": "Overexpansion tendency; must focus on core before growing",
            },
            "Venus": {
                "trait": "Client-relationship focused, luxury/creative industries",
                "business": "Arts, entertainment, luxury, hospitality, partnerships",
                "challenge_style": "Avoids conflict; must address partner/client issues directly",
            },
            "Saturn": {
                "trait": "Disciplined, slow-steady growth, structural thinker",
                "business": "Manufacturing, labor, real estate, long-term service contracts",
                "challenge_style": "Slow adaptation; must accept change when market demands it",
            },
            "Rahu": {
                "trait": "Unconventional, technology-driven, foreign connections",
                "business": "Technology, foreign trade, disruptive innovations",
                "challenge_style": "Instability from rapid change; must build stable processes",
            },
            "Ketu": {
                "trait": "Niche specialist, technical expert, research-oriented",
                "business": "Research, niche markets, technical services, spirituality",
                "challenge_style": "Detachment from practical operations; must stay engaged",
            }
        }

        lord_info = personality_map.get(lord, {
            "trait": "Unique business approach",
            "business": "Depends on specific placement",
            "challenge_style": "Individual style"
        })

        lines.append(f"Business Personality: {lord_info['trait']}")
        lines.append(f"Suitable Business Areas: {lord_info['business']}")
        lines.append(f"Challenge Pattern: {lord_info['challenge_style']}")
        lines.append("")
        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows fundamental business approach and challenge response")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (FIXED - Pure Methodology)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific business challenge analysis using PURE methodology.
        Uses CSL → Sub Lord → Star Lord → Significations → Promise/Denial chain.
        Mirrors Career prompt's _format_kp_analysis.
        """
        kp_structured = additional_data.get("kp_business_challenge_analysis", {}) if additional_data else {}

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
        lines.append("")

        methodology = kp_structured.get("methodology", "")
        if methodology:
            lines.append(f"Analysis Method: {methodology}")
            lines.append("")

        csl_details = kp_structured.get("csl_details", {})

        if csl_details:
            lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS:")
            lines.append("")

            # Priority order: 7 (business), 10 (profession), 11 (gains), 6 (obstacles), 8 (sudden)
            priority_order = [7, 10, 11, 6, 8, 2, 3, 5, 9, 12]

            for house_num in priority_order:
                if house_num not in csl_details:
                    continue

                info = csl_details[house_num]

                house_meaning = info.get("house_meaning", "Business")
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

                # Promise marker
                if promise_status == "PROMISE":
                    promise_marker = "✅ PROMISE"
                    promise_desc = "Business support CONFIRMED for this house"
                elif promise_status == "DENIAL":
                    promise_marker = "❌ DENIAL"
                    promise_desc = "Obstacles likely; strategy change needed"
                elif promise_status == "WEAK_PROMISE":
                    promise_marker = "⚠️ WEAK PROMISE"
                    promise_desc = "May improve with effort and favorable timing"
                elif promise_status in ("MANAGEABLE", "TRANSFORMATIVE"):
                    promise_marker = f"⚖️ {promise_status}"
                    promise_desc = "Manageable with correct approach"
                elif promise_status in ("CHALLENGING", "RISKY", "UNPREDICTABLE"):
                    promise_marker = f"⚠️ {promise_status}"
                    promise_desc = "Requires careful handling"
                else:
                    promise_marker = "○ NEUTRAL"
                    promise_desc = "Mixed indicators"

                lines.append(f"{'─' * 60}")
                lines.append(f"HOUSE {house_num} ({house_meaning})")
                lines.append(f"{'─' * 60}")
                lines.append("")

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

                        sub_set = set(sub_lord_signifies)
                        business_conn = sub_set & self.BUSINESS_PROMISE_HOUSES
                        success_conn = sub_set & self.SUCCESS_HOUSES
                        obstacle_conn = sub_set & self.OBSTACLE_HOUSES

                        if business_conn:
                            lines.append(f"  → Business Houses Connected: {sorted(business_conn)}")
                        if success_conn:
                            lines.append(f"  → Success Houses Connected: {sorted(success_conn)}")
                        if obstacle_conn:
                            lines.append(f"  ⚠️ Obstacle Houses Connected: {sorted(obstacle_conn)}")

                lines.append("")
                lines.append(f"  ╔═══════════════════════════════════════════════╗")
                lines.append(f"  ║  VERDICT: {promise_marker}")
                lines.append(f"  ║  {promise_desc}")
                lines.append(f"  ╚═══════════════════════════════════════════════╝")

                if interpretation:
                    lines.append("")
                    lines.append(f"  INTERPRETATION:")
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
        lines.append("  3. If benefic CSL has obstacle-house significations → DENIAL")
        lines.append("  4. If malefic CSL has business-house significations → PROMISE")
        lines.append("  5. Use exact houses from data - never guess")
        lines.append("")
        lines.append("VERDICT MEANINGS:")
        lines.append("  • PROMISE: Sub-lord signifies 2,3,7,11 strongly → Business supported")
        lines.append("  • DENIAL: Sub-lord signifies 6,8,12 strongly → Challenges ahead")
        lines.append("  • WEAK_PROMISE: Mixed → Recovery possible with effort")
        lines.append("  • NEUTRAL: Cannot determine clearly")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines), True

    # ------------------------------------------------------------------
    # HELPER: Format Business Challenge Suitability Matrix
    # ------------------------------------------------------------------
    def _format_business_challenge_matrix(self, matrix: Dict) -> str:
        """Format business challenge suitability matrix for LLM"""
        if not matrix:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("📊 BUSINESS RECOVERY OPTIONS MATRIX")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("Based on KP Significations + Unified Verdict:")
        lines.append("")
        lines.append("| Recovery Option | Rating | KP Reasoning |")
        lines.append("|-----------------|--------|--------------|")

        for option, details in matrix.items():
            rating = details.get("rating", "UNKNOWN")
            reasoning = details.get("kp_reasoning", "")

            if rating == "HIGH":
                marker = "✅"
            elif rating == "MODERATE":
                marker = "⚖️"
            elif rating in ["LOW", "VERY_LOW"]:
                marker = "○"
            elif rating == "AVOID":
                marker = "❌"
            else:
                marker = "?"

            if len(reasoning) > 50:
                reasoning = reasoning[:47] + "..."

            lines.append(f"| {marker} {option} | {rating} | {reasoning} |")

        lines.append("")
        lines.append("⚠️ Use this matrix CONSISTENTLY across all questions.")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Loan Indicators
    # ------------------------------------------------------------------
    def _format_loan_indicators(self, additional_data: Dict) -> str:
        """Format loan taking and repayment indicators"""
        if not additional_data:
            return ""

        loan_supported = additional_data.get('loan_supported')
        loan_planets = additional_data.get('loan_planets', [])
        repayment_supported = additional_data.get('repayment_supported')
        repayment_planets = additional_data.get('repayment_planets', [])

        if loan_supported is None and repayment_supported is None:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("💰 LOAN FEASIBILITY ANALYSIS")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        if loan_supported is not None:
            if loan_supported:
                lines.append("📥 LOAN TAKING: ✅ FAVORABLE")
                if loan_planets:
                    lines.append(f"   Supporting Planets: {', '.join(loan_planets[:3])}")
                lines.append("   Recommendation: Loan can support business if timed well")
            else:
                lines.append("📥 LOAN TAKING: ⚠️ CHALLENGING")
                lines.append("   Recommendation: Avoid new debt; focus on stabilizing first")
            lines.append("")

        if repayment_supported is not None:
            if repayment_supported:
                lines.append("📤 LOAN REPAYMENT: ✅ FAVORABLE")
                if repayment_planets:
                    lines.append(f"   Supporting Planets: {', '.join(repayment_planets[:3])}")
                lines.append("   Recommendation: Income periods support comfortable repayment")
            else:
                lines.append("📤 LOAN REPAYMENT: ⚠️ CHALLENGING")
                lines.append("   Recommendation: Extend timelines; avoid aggressive repayment")
            lines.append("")

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

        business_order = [7, 10, 11, 6, 8, 2, 3, 5, 9, 12, 1]

        house_meanings = {
            1: "Self/Personality",
            2: "Wealth/Resources",
            3: "Courage/Efforts",
            5: "Intelligence/Speculation",
            6: "Debts/Competition",
            7: "Business/Partnership",
            8: "Sudden Events/Obstacles",
            9: "Fortune/Luck",
            10: "Career/Profession",
            11: "Gains/Income",
            12: "Expenses/Losses"
        }

        for house_num in business_order:
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

            strength = info['lord_strength_score']
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports business in this area")
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

        has_aspects = any(
            aspects_info.get(h, {}).get("benefic_aspects") or
            aspects_info.get(h, {}).get("malefic_aspects")
            for h in [7, 10, 11, 6, 8, 2, 3]
        )

        if not has_aspects:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON BUSINESS HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        business_houses = [7, 10, 11, 6, 8, 2, 3, 5, 9, 12]

        for house_num in business_houses:
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
                "• Use for analyzing PRESENT business circumstances",
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
            lines.append("DASHA TIMELINE (For Business Recovery Planning)")
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

            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years - For Business Planning):")
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
            lines.append("BUSINESS DASHA GUIDELINES:")
            lines.append("• Jupiter/Venus → Growth, expansion, client relationships")
            lines.append("• Mercury → Trade, negotiations, communication, deals")
            lines.append("• Sun → Leadership, authority, government connections")
            lines.append("• Saturn → Restructuring, discipline, long-term foundation")
            lines.append("• Mars → Competitive action, real estate, quick decisions")
            lines.append("• Rahu → Technology, unconventional moves, foreign trade")
            lines.append("• Moon → Public-facing business, consumer sentiment")
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
        """Generate analysis instructions based on data availability and context."""

        base = """
**ANALYSIS APPROACH (FOLLOW THIS ORDER):**

**STEP 1: CHECK UNIFIED VERDICT (MANDATORY)**
Read the UNIFIED_BUSINESS_VERDICT section first.
Your ENTIRE response must align with this verdict.
Note:
• Overall outlook (RECOVERY_LIKELY / SERIOUS_CHALLENGES / etc.)
• Business viable flag
• Confidence level
• Promise status for each key house
• KP-Vedic agreement status

"""

        if kp_available:
            base += """
**STEP 2: KP ANALYSIS (Primary - 50% weight)**

For each business cusp (7, 10, 11), explain:
• CSL → Sub Lord → Significations
• Which houses does sub-lord signify?
• Is it PROMISE or DENIAL based on those houses?

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
• Strength assessment for 7th, 10th, 11th lords
• Challenge indicators (6th, 8th, 12th)

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

        # ── MINOR OVERRIDES ──────────────────────────────────────────────────

        if question_type == "minor_loan":
            base += f"""
🚨 MINOR PROTECTION MODE ACTIVE 🚨

Person is under 18.

STRICT RULES:
• Do NOT recommend taking loans of any kind
• Do NOT suggest signing contracts or financial commitments
• Do NOT advise business decisions that require legal capacity
• Do NOT present loan timing windows even if provided

INSTEAD, frame the analysis as:
• Understanding how financial pressure cycles work astrologically
• What family members or guardians should consider
• How this period builds financial wisdom for the future
• Preparation-oriented: "This dasha teaches patience with resources"

Tone must be:
• Educational
• Protective
• Future-oriented
• Empowering (not disempowering)

DOB: {dob}
"""
            return base

        if question_type == "minor_general":
            base += f"""
🚨 MINOR EDUCATIONAL MODE ACTIVE 🚨

Person is under 18.

STRICT RULES:
• Do NOT advise business decisions requiring legal/financial capacity
• Do NOT recommend shutting down operations
• Do NOT recommend expanding or contracting operations
• Do NOT recommend taking on business partners contractually

INTERPRET business challenges as:
• Learning moments about business cycles
• Preparation for future entrepreneurship
• Skills to develop for long-term business success
• Family business support roles, not leadership roles

Tone:
• Educational
• Encouraging
• Developmental
• Wisdom-building

DOB: {dob}
"""
            return base

        if question_type == "minor_timing":
            base += f"""
🚨 MINOR DEVELOPMENTAL MODE ACTIVE 🚨

Person is under 18.

STRICT RULES:
• Do NOT present timing windows for business decisions
• Do NOT predict business recovery dates
• Do NOT say "business will recover in [period]"

INSTEAD interpret dashas as:
• Skill-building phases
• Learning cycles for entrepreneurship
• Foundation-building periods
• Preparation for future business success

Tone:
• Developmental
• Encouraging
• Long-term vision
• Educational

DOB: {dob}
"""
            return base

        return base

    # ------------------------------------------------------------------
    # HELPER: Check if business recovery is blocked
    # ------------------------------------------------------------------
    def _is_blocked(self, additional_data: Dict) -> bool:
        """Check if business recovery is blocked based on KP analysis"""
        if not additional_data:
            return False

        kp_analysis = additional_data.get("kp_business_challenge_analysis", {})
        if kp_analysis.get("overall_verdict") == "SERIOUS_CHALLENGES_INDICATED":
            return True

        kp_data = additional_data.get(f"{DOMAIN_PREFIX}_kp_analysis", {})
        if kp_data.get("confidence") == "Low":
            house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
            if house_lords:
                weak_count = sum(
                    1 for h in [7, 10, 11]
                    if house_lords.get(h, {}).get("lord_strength_score", 50) < 30
                )
                if weak_count >= 2:
                    return True

        return False

    # ------------------------------------------------------------------
    # HELPER: Language Instruction
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
Example: "आपके व्यवसाय में **7th house** से **partnership** की संभावना है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke business mein recovery ke strong indicators hain."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear, warm English.
Keep technical terms clear and explain if needed.
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT - DYNAMIC BASED ON KP AVAILABILITY + TIMING + QUESTION TYPE
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
- Why favorable: [explain dasha lords + business significations]
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

        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT - FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, warm, actionable answer in simple terms. NO jargon.>
<Acknowledge the difficulty of the situation with empathy.>
<State the overall business health assessment clearly.>
<Example: "आपके व्यापार में अभी चुनौतियाँ हैं, लेकिन ये स्थायी नहीं हैं। 
7वें भाव का KP विश्लेषण दिखाता है कि partnership path में recovery संभव है।">

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Business Outlook: [from unified verdict]
- Business Viable: [YES/NEEDS CHANGES]
- Confidence: [from unified verdict]
- Promise Status: [7th: X, 10th: Y, 11th: Z]
- KP-Vedic Agreement: [AGREEMENT/PARTIAL/CONFLICT]

**B. KP SYSTEM ANALYSIS (Primary - 50% weight):**

For EACH business cusp (7th, 10th, 11th, and relevant obstacle houses):

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor - NOT the verdict!)
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Business Houses Connected: [list] (from 2, 3, 7, 11)
- Success Houses Connected: [list] (from 2, 10, 11)
- Obstacle Houses Connected: [list] (from 6, 8, 12)
- **VERDICT: PROMISE/DENIAL** based on sub-lord significations
- Why: [Explain how significations lead to verdict]

⚠️ Sub-lord significations decide, NOT planet nature

**C. VEDIC ANALYSIS (Secondary - 30% weight):**

**House Lords:**
- 7th Lord: [Planet, placement, dignity, strength]
- 10th Lord: [Planet, placement, dignity, strength]
- 11th Lord: [Planet, placement, dignity, strength]

**Vedic-KP Agreement Check:**
- If agree: "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic [Y]. KP priority."
- If conflict: "❌ CONFLICT: KP [X], Vedic [Y]. Using KP for events."

**D. LAGNA LORD (Business Personality):**
- [Planet] as lagna lord → [business approach and challenge response style]

**E. BUSINESS RECOVERY MATRIX:**

| Option | Rating | Reasoning |
|--------|--------|-----------|
| [Option] | HIGH/MODERATE/LOW | [from KP significations] |

{timing_section}

**G. DASHA CONTEXT:**
- Current: [dasha] - [business impact]
- Upcoming favorable: [dasha + dates]

**SUMMARY:**
<2-3 sentences. MUST align with unified verdict.>
<End with one clear, actionable step the person can take today.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial]

**REMEDIES_GENERAL:**
- [Practical business steps aligned with challenge type]
"""
        else:
            return f"""
OUTPUT FORMAT (STRICT - VEDIC ONLY):

**GENERAL_ANSWER:**
<Clear, warm, actionable answer in simple terms.>
<Acknowledge difficulty with empathy.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD (Business Personality):**
- Planet: [Name]
- Placed in: House [N]
- Business approach: [description]

**B. HOUSE LORD ANALYSIS (Primary):**

For each business house (7, 10, 11):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Business Impact: [explanation]

**C. BUSINESS RECOVERY OPTIONS:**

| Option | Suitability | Reasoning |
|--------|-------------|-----------|
| Continue | [HIGH/MODERATE/LOW] | [based on house analysis] |
| Restructure | [HIGH/MODERATE/LOW] | [based on house analysis] |
| Partnership | [HIGH/MODERATE/LOW] | [based on house analysis] |

{timing_section}

**D. DASHA CONTEXT:**
- Current: [dasha]
- Business impact: [explanation]

**SUMMARY:**
<Concise business outlook ending with a clear action step.>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical business steps]
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
        logger.warning("🔥 BUSINESS CHALLENGES PROMPT BUILDER EXECUTED")

        # ----------------------------
        # GLOBAL MINOR DETECTION
        # ----------------------------
        dob = kwargs.get("dob")
        dasha_timeline = kwargs.get("dasha_timeline")

        is_minor = self._detect_minor(dob, dasha_timeline)
        kwargs["is_minor"] = is_minor
        logger.warning(f"[BUSINESS CHALLENGES] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

        if "Reason for Business Challenges" in sub_subdomain or \
           ("Challenges" in sub_subdomain and "Remed" not in sub_subdomain and "Loan" not in sub_subdomain and "Continue" not in sub_subdomain):
            return self._build_challenges_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Loan Taking" in sub_subdomain:
            return self._build_loan_taking_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Loan Repayment" in sub_subdomain:
            return self._build_loan_repayment_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Continue or Shut Down" in sub_subdomain:
            return self._build_continue_shutdown_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # REASON FOR BUSINESS CHALLENGES PROMPT (Q1)
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
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        challenge_matrix = additional_data.get("business_challenge_suitability_matrix", {})
        matrix_formatted = self._format_business_challenge_matrix(challenge_matrix)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        question_type = "minor_general" if is_minor else "challenges"
        analysis_instructions = self._get_analysis_instructions(kp_available, question_type, False, dob=dob)

        minor_note = ""
        if is_minor:
            minor_note = f"""
═══════════════════════════════════════════════════════════
🚨 MINOR EDUCATIONAL MODE (Person under 18)
═══════════════════════════════════════════════════════════
• Do NOT advise business decisions requiring legal/financial capacity
• Frame as learning and preparation for future entrepreneurship
• Focus on family business support role, not decision-making role
• Tone: Educational, developmental, encouraging
DOB: {dob}
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Sub-subdomain: Reason for Business Challenges
Query Type: NON_TIMING (Challenge Diagnosis)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor: {'YES ⚠️' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}

{unified_verdict_block}

{kp_formatted}

{matrix_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR CHALLENGE DIAGNOSIS:
• 7th house shows business/partnership health
• 10th house shows professional standing and reputation
• 11th house shows income/gains flow
• 6th, 8th, 12th show obstacle sources
• Frame ALL challenges as TEMPORARY and CORRECTABLE
• Always end with a practical next step
• Acknowledge the human stress behind business challenges

{self.get_output_format(kp_available, False, question_type)}
"""

    # ------------------------------------------------------------------
    # LOAN TAKING PROMPT (Q2A)
    # ------------------------------------------------------------------
    def _build_loan_taking_prompt(
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

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False) and not is_minor

        is_blocked = self._is_blocked(additional_data)

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        loan_formatted = self._format_loan_indicators(additional_data)

        timing_formatted = ""
        if has_timing and not is_blocked:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        question_type = "minor_loan" if is_minor else "loan_taking"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing and not is_blocked, dob=dob
        )

        minor_note = ""
        if is_minor:
            minor_note = f"""
═══════════════════════════════════════════════════════════
🚨 MINOR PROTECTION MODE ACTIVE (Person under 18)
═══════════════════════════════════════════════════════════
ABSOLUTE RULES:
• Do NOT recommend taking any loan
• Do NOT present timing windows for loan decisions
• Do NOT advise any financial commitments
• Frame response as educational: what to learn about loan cycles
• Suggest guardians/family handle financial decisions
DOB: {dob}
═══════════════════════════════════════════════════════════
"""

        blocked_section = ""
        if is_blocked and not is_minor:
            blocked_section = """
═══════════════════════════════════════════════════════════
⚠️ LOAN TAKING CHALLENGING - STABILIZE FIRST
═══════════════════════════════════════════════════════════
The chart shows challenges for taking loans currently.
🚫 DO NOT provide specific timing windows for loan taking.
✅ DO recommend stabilizing business before borrowing.
✅ DO suggest remedies to strengthen financial position first.
MESSAGE: "Focus on stabilizing operations first.
A loan taken during a challenging period may increase burden
rather than provide relief."
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Sub-subdomain: Loan Taking Decision
Query Type: {'TIMING' if has_timing and not is_blocked else 'NON_TIMING'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing and not is_blocked else 'NO ❌'}
Minor: {'YES ⚠️ - Loan advice blocked' if is_minor else 'NO'}
Loan Taking Blocked: {'YES' if is_blocked and not is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}
{blocked_section}

{unified_verdict_block}

{timing_formatted}

{loan_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

LOAN-SPECIFIC CONTEXT:
- 6th house = taking loans, debts (CRITICAL for this question)
- 11th house = gains/income to service loan (CRITICAL)
- 2nd house = wealth base, financial capacity
- 7th house = business strength to utilize loan productively
- Risk-aware guidance: never promotional about loans

{self.get_output_format(kp_available, has_timing and not is_blocked, question_type)}
"""

    # ------------------------------------------------------------------
    # LOAN REPAYMENT PROMPT (Q2B)
    # ------------------------------------------------------------------
    def _build_loan_repayment_prompt(
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

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False) and not is_minor

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        loan_formatted = self._format_loan_indicators(additional_data)

        timing_formatted = ""
        if has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        question_type = "minor_loan" if is_minor else "loan_repayment"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing, dob=dob
        )

        minor_note = ""
        if is_minor:
            minor_note = f"""
═══════════════════════════════════════════════════════════
🚨 MINOR PROTECTION MODE ACTIVE (Person under 18)
═══════════════════════════════════════════════════════════
ABSOLUTE RULES:
• Do NOT advise on loan repayment schedules
• Do NOT present repayment timing windows
• Frame as educational: how repayment cycles work astrologically
• Suggest guardians/family handle financial decisions
DOB: {dob}
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Sub-subdomain: Loan Repayment Decision
Query Type: {'TIMING' if has_timing else 'NON_TIMING'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
Minor: {'YES ⚠️ - Financial advice restricted' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}

{unified_verdict_block}

{timing_formatted}

{loan_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

REPAYMENT-SPECIFIC CONTEXT:
- 11th house = gains/income (CRITICAL for repayment capacity)
- 2nd house = wealth accumulation (CRITICAL)
- 10th house = professional income
- 6th house = existing debt burden management

{self.get_output_format(kp_available, has_timing, question_type)}
"""

    # ------------------------------------------------------------------
    # CONTINUE OR SHUT DOWN PROMPT (Q3)
    # ------------------------------------------------------------------
    def _build_continue_shutdown_prompt(
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

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False) and not is_minor

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        loan_formatted = self._format_loan_indicators(additional_data)

        challenge_matrix = additional_data.get("business_challenge_suitability_matrix", {})
        matrix_formatted = self._format_business_challenge_matrix(challenge_matrix)

        timing_formatted = ""
        if has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        question_type = "minor_general" if is_minor else "continue_shutdown"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing, dob=dob
        )

        minor_note = ""
        if is_minor:
            minor_note = f"""
═══════════════════════════════════════════════════════════
🚨 MINOR PROTECTION MODE ACTIVE (Person under 18)
═══════════════════════════════════════════════════════════
ABSOLUTE RULES:
• Do NOT recommend shutting down business operations
• Do NOT recommend major strategic pivots without guardian involvement
• Frame as: "This is a decision for the adults/guardians in the family"
• Explain what the chart shows about long-term business potential
• Tone: Supportive, educational, protective
DOB: {dob}
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Sub-subdomain: Continue or Shut Down Decision
Query Type: {'TIMING' if has_timing else 'NON_TIMING'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor: {'YES ⚠️ - Shutdown advice blocked' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}

{unified_verdict_block}

{timing_formatted}

{matrix_formatted}

{loan_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

DECISION GUIDELINES:
• Closure should ONLY be advised when risk is VERY HIGH and sustained
• ALWAYS prefer restructuring over abrupt closure
• Business downturns are often TEMPORARY — say so explicitly
• Consider partnerships, pivots, or strategic pauses before closure
• If closing is truly indicated, frame it as "strategic exit for new beginning"

{self.get_output_format(kp_available, has_timing, question_type)}
"""

    # ------------------------------------------------------------------
    # BUSINESS REMEDIES PROMPT (Q4)
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
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        current_dasha_block = self._format_current_dasha(current_dasha)

        minor_note = ""
        if is_minor:
            minor_note = f"""
═══════════════════════════════════════════════════════════
🚨 MINOR MODE (Person under 18)
═══════════════════════════════════════════════════════════
• Remedies should be appropriate for a young person
• Focus on self-discipline, study, and preparation remedies
• Avoid remedies requiring financial commitment or legal capacity
• Include family-level remedies where appropriate
DOB: {dob}
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Sub-subdomain: Business Remedies
Query Type: NON_TIMING (Practical Remedies)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor: {'YES ⚠️' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}

{unified_verdict_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

REMEDY GUIDELINES:

1. **Identify Weak Areas from Analysis:**
   - Which cusps show DENIAL or CHALLENGING status?
   - Which house lords are weak (strength < 40)?
   - Which planets need strengthening?

2. **Current Dasha Lord Remedies:**
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords (3 months before transition)

3. **Priority:**
   - Primary: 7th house lord (business/partnerships)
   - Secondary: 10th/11th house lords (career/gains)
   - Tertiary: Address 6th/8th/12th connections (obstacle reduction)

PLANETARY REMEDY GUIDE:
- MERCURY: Trade/communication ("Om Budhaya Namaha", Emerald, Wednesday)
- JUPITER: Growth/ethics ("Om Gurave Namaha", Yellow Sapphire, Thursday)
- VENUS: Clients/partnerships ("Om Shukraya Namaha", Diamond, Friday)
- SATURN: Discipline/structure ("Om Shanicharaya Namaha", Blue Sapphire, Saturday)
- SUN: Leadership/authority ("Om Suryaya Namaha", Ruby, Sunday)
- MARS: Action/competition ("Om Mangalaya Namaha", Red Coral, Tuesday)

OUTPUT FORMAT:

**WEAK AREAS IDENTIFIED:**
- [From KP promise/denial analysis]
- [From Vedic house lord analysis]

**REMEDIES_ASTROLOGICAL:**

**For [Planet] (affecting [house] — [business area]):**
- Mantra: [specific mantra]
- Day: [best day for remedy]
- Gemstone: [if applicable, with caution note]
- Charity: [specific charity type]

**For Current Dasha Lord ([Planet]):**
- [Specific remedies for immediate relief]

**REMEDIES_GENERAL:**
- [Practical business steps aligned with weak house analysis]
- [Communication/relationship improvements if 7th is weak]
- [Financial discipline steps if 11th/2nd are weak]
- [Networking/visibility steps if 10th is weak]

**TIMELINE:**
- Start remedies on: [auspicious day/nakshatra]
- Duration: [recommended period]
- Review after: [timeframe]
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
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha') or additional_data.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline') or additional_data.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        question_type = "minor_general" if is_minor else "general"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, False, dob=dob
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Facing Challenges in Business
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor: {'YES ⚠️' if is_minor else 'NO'}
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
• Align answer with unified business verdict
• Use pure KP methodology if KP data available
• Be honest about KP-Vedic agreement/conflict
• Frame ALL challenges as TEMPORARY and CORRECTABLE
• Always provide actionable guidance

{self.get_output_format(kp_available, False, question_type)}
"""
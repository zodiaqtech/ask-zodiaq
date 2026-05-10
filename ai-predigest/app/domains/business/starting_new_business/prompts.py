"""
Starting New Business – LLM Prompts v10.0

FIXES IN v10.0 (Matching Career/Finance Prompt Pattern):
✅ CORRECTED KP House Definitions — Business: 2,3,7,11 | Service: 2,6,10,11 (was wrong 3,5,7,9,11)
✅ MINOR DETECTION — Added _detect_minor(), is_minor flag, developmental override in timing prompt
✅ IMPROVED SAMPLES — CRITICAL EXAMPLE and WRONG EXAMPLE language cleaned up, fraction scoring removed
✅ OUTPUT FORMAT SAMPLES — Sharper, more realistic example blocks aligned with KP methodology
✅ UNIFIED BUSINESS VERDICT — Added _format_unified_verdict() matching career/finance pattern
✅ ANTI-HALLUCINATION — Fraction scoring (3/5, 2/4) removed from all output format guidance
✅ CONSISTENT HOUSE MAPPING — Business/Service connections now match evaluator v5.0

Weightage:
- KP Significations → 60% (PRIMARY)
- Vedic Structure → 30% (SECONDARY)
- Dasha/Other → 10%

Compatible with StartingNewBusinessEvaluator v5.0 data structures:
- unified_business_verdict (SINGLE SOURCE OF TRUTH)
- kp_business_analysis (structured KP with CSL chains)
- business_suitability_matrix (10 business type ratings)
- foreign_business_exposure (foreign/multinational analysis)
- business_structural_kp (KP business evaluation)
- service_vs_business (Service/Business/Mixed verdict)
- business_timing_windows (BEST + NEAREST)
- business_house_lords (Vedic house lord data)
- business_house_aspects (Vedic aspects)
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

DOMAIN_PREFIX = "business"


class StartingNewBusinessPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Business → Starting New Business
    v10.0 - Corrected KP methodology, minor detection, improved samples
    """

    domain = "Business"
    subtopic = "Starting New Business"

    # CORRECTED House definitions (matching evaluator v5.0 and doc 1)
    BUSINESS_HOUSES = {2, 3, 7, 11}   # Income, initiative/trade, partnership, gains
    SERVICE_HOUSES  = {2, 6, 10, 11}  # Income, service, profession, gains
    LOSS_HOUSES     = {8, 12}

    # ------------------------------------------------------------------
    # SYSTEM PROMPT — v10.0
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing ACTIONABLE business and entrepreneurship guidance.

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
If Venus (benefic) signifies 6, 8, 12 → result is obstacles/losses.
If Saturn (malefic) signifies 2, 7, 10, 11 → result is successful business.
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
CORRECT KP HOUSE DEFINITIONS (MEMORIZE)
════════════════════════════════════

BUSINESS HOUSES: 2, 3, 7, 11
• 2nd: Income, capital, accumulated wealth
• 3rd: Initiative, self-effort, trade, courage
• 7th: Business, partnerships, trade, dealings
• 11th: Gains, profits, fulfillment of desires

SERVICE / EMPLOYMENT HOUSES: 2, 6, 10, 11
• 2nd: Salary, income (shared with business)
• 6th: Service, employment, subordination
• 10th: Profession, authority, career
• 11th: Gains (shared with business)

LOSS / OBSTACLE HOUSES: 8, 12
• 8th: Sudden changes, hidden obstacles, inheritance
• 12th: Losses, foreign, endings, expenses

❌ WRONG: 5th and 9th are NOT primary business houses
❌ WRONG: Never use "3/5" or "2/4" fraction scoring — this is NOT KP

When judging a planet for business, consider:
• Houses occupied
• Houses owned
• Houses of its star lord
• Houses of its sub lord

Weight priority: Sub > Star > Occupation > Ownership

════════════════════════════════════
PROMISE/DENIAL LOGIC (SUB LORD DECIDES)
════════════════════════════════════

FOR 7TH CUSP (Business):
• PROMISE: Sub-lord signifies 2, 3, 7, 11 (2+ houses)
• DENIAL: Sub-lord signifies 6 (service), 8, 12 strongly
• WEAK: Mixed significations

FOR 10TH CUSP (Career/Profession):
• PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
• DENIAL: Sub-lord signifies 8, 12 strongly
• WEAK: Mixed significations

FOR 6TH CUSP (Service/Employment):
• PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
• DENIAL: Sub-lord signifies 8, 12 strongly
• WEAK: Mixed significations

════════════════════════════════════
RAHU/KETU RULE
════════════════════════════════════

Nodes act through their STAR LORD.
Show: "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"

⚠️ Never judge Rahu/Ketu by just their house occupation.
Their star lord's significations determine their results.

════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════

DO NOT invent data.

• Do NOT mention aspects unless explicitly provided
• Do NOT assume yogas not present in input
• Do NOT use fraction scoring ("3/5", "2/4") — this is NOT KP methodology
• Do NOT contradict the unified verdict
• Do NOT invent specific timing dates not in the data
• If data is missing → say so clearly, do not guess

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

• Lagna lord → personality & business approach
• House lords → capacity/obstacles
• Dignity → strength/weakness

KP decides the event.
Vedic explains ease/difficulty.

════════════════════════════════════
MODERN BUSINESS MAPPING (TENDENCIES ONLY)
════════════════════════════════════

Map planets to modern business types (modify using KP strength):

Sun → Authority businesses, government contracts, leadership ventures
Moon → Hospitality, food, retail, public-facing businesses
Mars → Real estate, construction, manufacturing, sports
Mercury → Trading, IT, communication, consulting, agencies
Jupiter → Education, law, finance, advisory, expansion
Venus → Luxury, fashion, entertainment, hospitality, beauty
Saturn → Manufacturing, labor, discipline-based, infrastructure
Rahu → Technology, foreign trade, unconventional, startups
Ketu → Research, niche technical, spiritual businesses

These are tendencies, NOT guarantees.
Final decision must come from KP significations.

════════════════════════════════════
AGE SAFETY RULE
════════════════════════════════════

If person is under 18:
• NEVER recommend immediate business launch
• NEVER suggest taking loans or investing capital
• Frame analysis as preparation and foundation stage
• Ignore timing windows even if provided
• Treat all dashas as developmental/learning cycles
• Never interpret dashas as business launch triggers

════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════

Always convert astrology into decisions:

❌ "7th house is moderate"
✅ "Partnership-based business is viable. Begin with a small trading venture."

❌ "10th lord strong"
✅ "Professional establishment is supported — proceed with business registration."

Provide:
• Clear business path recommendation
• Timing guidance (if timing data available)
• Specific next steps
• Realistic expectations based on promise/denial status

════════════════════════════════════
ANALYSIS WEIGHTING
════════════════════════════════════

KP Significations → 60% (PRIMARY)
Vedic Structure → 30% (SECONDARY)
Dasha Timing → 10%

KP conclusion ALWAYS leads the final recommendation.
Vedic explains ease or difficulty of achieving KP's promise.

════════════════════════════════════
⚠️ BUSINESS DOMAIN SAFETY RULES
════════════════════════════════════

- NEVER guarantee business success or failure
- NEVER induce fear about financial loss
- Frame challenges as TENDENCIES, not certainties
- Loan advice must be RISK-AWARE, not promotional
- All business predictions are POSSIBILITIES, not promises
- Astrology complements business planning — it does not replace it

Goal: Provide precise, practical, business-useful guidance — not generic astrology descriptions.
"""

    # ------------------------------------------------------------------
    # HELPER: Format Unified Business Verdict (NEW — mirrors career pattern)
    # ------------------------------------------------------------------
    def _format_unified_verdict(self, additional_data: Dict) -> str:
        """
        Format the UNIFIED business verdict prominently.
        Ensures ALL questions use the SAME business/service direction.
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
making definitive business path recommendations.
═══════════════════════════════════════════════════════════
"""

        primary_path   = verdict.get("primary_path", "Unknown")
        secondary_path = verdict.get("secondary_path")
        confidence     = verdict.get("confidence", "Low")
        agreement      = verdict.get("agreement_status", "UNKNOWN")
        promise_status = verdict.get("promise_status", {})
        career_ranking = verdict.get("career_ranking", [])
        kp_reasoning   = verdict.get("kp_reasoning", "")
        vedic_reasoning = verdict.get("vedic_reasoning", "")

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 UNIFIED BUSINESS VERDICT (SINGLE SOURCE OF TRUTH)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL INSTRUCTION:")
        lines.append("Your answer MUST align with this verdict.")
        lines.append("Do NOT contradict this in any part of your response.")
        lines.append("")

        lines.append(f"╔══════════════════════════════════════════════════════╗")
        lines.append(f"║  PRIMARY PATH: **{primary_path.upper()}**")
        lines.append(f"║  Confidence Level: {confidence}")
        lines.append(f"╚══════════════════════════════════════════════════════╝")
        lines.append("")

        if secondary_path:
            lines.append(f"Secondary Potential: {secondary_path}")
            lines.append("")

        # Agreement status
        lines.append("KP-VEDIC AGREEMENT STATUS:")
        if agreement == "AGREEMENT":
            lines.append("  ✅ AGREEMENT: Both KP and Vedic systems agree on this path.")
            lines.append("     → High confidence in recommendation")
        elif agreement == "PARTIAL":
            lines.append("  ⚠️ PARTIAL AGREEMENT: Systems show similar but not identical direction.")
            lines.append("     → KP result takes priority for events/timing")
        elif agreement == "CONFLICT":
            lines.append("  ❌ CONFLICT: KP and Vedic show different paths.")
            lines.append(f"     → KP indicates: {primary_path}")
            lines.append("     → Using KP for final verdict (events); Vedic explains effort required")
        else:
            lines.append(f"  ○ {agreement}")
        lines.append("")

        # Promise status
        if promise_status:
            lines.append("PROMISE STATUS (From Sub-Lord Analysis):")
            lines.append("─" * 50)

            promise_meanings = {
                2:  "Income/Capital",
                3:  "Initiative/Trade",
                6:  "Service/Employment",
                7:  "Business/Partnership",
                10: "Career/Profession",
                11: "Gains/Profits",
                12: "Foreign/Expenses"
            }

            for house_num in [7, 10, 6, 11, 2, 3, 12]:
                if house_num in promise_status:
                    status  = promise_status[house_num]
                    meaning = promise_meanings.get(house_num, f"House {house_num}")
                    if status == "PROMISE":
                        lines.append(f"  ✅ House {house_num} ({meaning}): PROMISE — will manifest")
                    elif status == "DENIAL":
                        lines.append(f"  ❌ House {house_num} ({meaning}): DENIAL — obstacles likely")
                    elif status == "WEAK_PROMISE":
                        lines.append(f"  ⚠️ House {house_num} ({meaning}): WEAK PROMISE — may manifest with effort")
                    else:
                        lines.append(f"  ○ House {house_num} ({meaning}): {status}")
            lines.append("")

        if kp_reasoning:
            lines.append("KP REASONING:")
            lines.append(f"  {kp_reasoning}")
            lines.append("")

        if vedic_reasoning:
            lines.append("VEDIC REASONING:")
            lines.append(f"  {vedic_reasoning}")
            lines.append("")

        if career_ranking:
            lines.append("PATH RANKING (Use consistently across all questions):")
            lines.append("─" * 50)
            for i, item in enumerate(career_ranking[:5], 1):
                path   = item.get("path", "Unknown")
                rating = item.get("rating", "LOW")
                marker = "✅" if rating == "HIGH" else "⚖️" if rating == "MODERATE" else "○"
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
    # HELPER: Detect Minor
    # ------------------------------------------------------------------
    def _detect_minor(self, dob: str) -> bool:
        """Detect if person is currently under 18."""
        if not dob:
            return False

        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                dob_dt = datetime.strptime(dob, fmt)
                today = datetime.now()
                age = today.year - dob_dt.year - (
                    (today.month, today.day) < (dob_dt.month, dob_dt.day)
                )
                return age < 18
            except ValueError:
                continue

        logger.warning(f"[BUSINESS] Unable to parse DOB format: {dob}")
        return False

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """Format BEST and NEAREST timing windows for LLM."""
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return ""

        try:
            best        = timing_windows_data.get('best_window')
            nearest     = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])

            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════════"]
            lines.append("⏰ TIMING WINDOWS ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: Two timing options are provided below.")
            lines.append("ALWAYS mention BOTH in your analysis and explain the trade-off.")
            lines.append("")

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
                lines.append(f"    • Maha Dasha score: {best.get('score_maha', 0)}/10")
                lines.append(f"    • Antara Dasha score: {best.get('score_antara', 0)}/10")
                lines.append(f"    • Pratyantar Dasha score: {best.get('score_paryantar', 0)}/10")
                lines.append(f"    • Transit support: {best.get('transit_score', 0):.1f}%")
                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest planetary alignment")
                lines.append("")

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
                    lines.append("  You get optimal timing AND the earliest opportunity!")
                else:
                    lines.append("  Why this is NEAREST:")
                    lines.append("    • Earliest window with score ≥ 50")
                    lines.append("    • Allows action sooner rather than waiting")
                    lines.append("")
                    lines.append("  Trade-off: Sooner, but not the absolute strongest alignment")
                lines.append("")

            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (for reference):")
                lines.append("-" * 50)
                for i, window in enumerate(all_windows[:5], 1):
                    dasha = window.get('dasha', 'N/A')
                    start = window.get('start', 'N/A')
                    end   = window.get('end', 'N/A')
                    score = window.get('final_score', 0)
                    is_best    = best    and dasha == best.get('dasha')    and start == best.get('start')
                    is_nearest = nearest and dasha == nearest.get('dasha') and start == nearest.get('start')
                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for business launch")
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
        """Format lagna lord prominently for business personality analysis."""
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign":        info.get('house_sign', 'N/A'),
                "lagna_lord":        info.get('lord', 'N/A'),
                "lagna_lord_house":  info.get('lord_in_house'),
                "lagna_lord_sign":   info.get('lord_in_sign', 'N/A'),
                "lagna_lord_degree": info.get('lord_degree', 0),
                "lagna_lord_dignity":info.get('lord_dignity', 'Unknown'),
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

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) — BUSINESS PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_info.get('lagna_sign', 'N/A')}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lagna_info.get('lagna_lord_house', 'N/A')}, {lagna_info.get('lagna_lord_sign', 'N/A')}")
        lines.append(f"Dignity: {lagna_info.get('lagna_lord_dignity', 'Unknown')}")
        lines.append("")

        personality_map = {
            "Sun":     "Leadership-oriented; suited to authority-based businesses and government contracts",
            "Moon":    "People-oriented; strong in hospitality, retail, and customer-facing businesses",
            "Mars":    "Action-oriented; real estate, construction, and manufacturing aptitude",
            "Mercury": "Analytical and versatile; excels in trading, IT, communication, and consulting",
            "Jupiter": "Expansion-focused; education, law, finance, and advisory businesses",
            "Venus":   "Creative and diplomatic; suited to luxury, fashion, entertainment, and hospitality",
            "Saturn":  "Disciplined builder; patient in manufacturing, infrastructure, and long-cycle businesses",
            "Rahu":    "Unconventional and ambitious; foreign trade, technology, and startup ventures",
            "Ketu":    "Research-oriented and independent; niche technical, healing, or spiritual businesses",
        }

        personality = personality_map.get(lord, "Unique business approach — assess based on placement and dignity")
        lines.append(f"Business Personality: {personality}")
        lines.append("")

        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord reveals the person's fundamental approach to business")
        lines.append("• Use this to explain HOW they will operate, not WHAT they will do")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Business Suitability Matrix
    # ------------------------------------------------------------------
    def _format_business_matrix(self, matrix: Dict) -> str:
        """Format business suitability matrix for LLM"""
        if not matrix:
            return ""

        lines = ["**B. BUSINESS TYPE SUITABILITY MATRIX (From KP Significations):**", ""]
        lines.append("| Business Type | Suitability | KP Reasoning |")
        lines.append("|---------------|-------------|--------------|")

        for business_type, details in matrix.items():
            rating    = details.get("rating", "UNKNOWN")
            reasoning = details.get("kp_reasoning", "")
            marker = "✅" if rating == "HIGH" else "⚖️" if rating == "MODERATE" else "⚠️" if rating in ["LOW", "VERY LOW"] else "❌" if rating == "AVOID" else "○"
            lines.append(f"| {marker} **{business_type}** | {rating} | {reasoning} |")

        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Foreign Business Exposure
    # ------------------------------------------------------------------
    def _format_foreign_exposure(self, foreign_data: Dict) -> str:
        """Format foreign business exposure analysis"""
        if not foreign_data:
            return ""

        exposure_level = foreign_data.get("exposure_level", "Unknown")
        score          = foreign_data.get("score", 0)
        indicators     = foreign_data.get("indicators", [])

        if not indicators and score == 0:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🌍 FOREIGN / INTERNATIONAL BUSINESS EXPOSURE")
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

        if "Foreign" in exposure_level or "International" in exposure_level:
            lines.append("→ Strong foreign business connection indicated")
            lines.append("→ Import/export, international clients, or overseas ventures are favored")
        elif "Mobile" in exposure_level or "Transfer" in exposure_level:
            lines.append("→ Business may involve travel or multiple locations")
        else:
            lines.append("→ Primarily domestic business focus")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format KP Business Analysis
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific business analysis using PURE methodology.
        Uses CSL → Sub Lord → Star Lord → Significations → Promise/Denial chain.
        """
        kp_structured = additional_data.get("kp_business_analysis", {}) if additional_data else {}

        if kp_structured and kp_structured.get("has_kp_data"):
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
            lines.append("  4. Do NOT use fraction scoring (3/5, 2/4) — this is not KP!")
            lines.append("")

            methodology = kp_structured.get("methodology", "")
            if methodology:
                lines.append(f"Analysis Method: {methodology}")
                lines.append("")

            csl_details = kp_structured.get("csl_details", {})

            if csl_details:
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS (Business Houses):")
                lines.append("")

                # Priority order: 7 (business), 10 (career), 6 (service), 11 (gains), 2 (income)
                priority_order = [7, 10, 6, 11, 2, 3]

                for house_num in priority_order:
                    if house_num not in csl_details:
                        continue

                    info = csl_details[house_num]

                    house_meaning   = info.get("house_meaning", "Business")
                    csl             = info.get("csl", "Unknown")
                    csl_flavor      = info.get("csl_flavor", "")
                    csl_house       = info.get("csl_house", "")
                    nakshatra       = info.get("nakshatra", "")
                    star_lord       = info.get("star_lord", "")
                    star_lord_signifies = info.get("star_lord_signifies", [])
                    sub_lord        = info.get("sub_lord", "")
                    sub_lord_signifies  = info.get("sub_lord_signifies", [])
                    promise_status  = info.get("promise_status", "UNKNOWN")
                    interpretation  = info.get("interpretation", "")

                    if promise_status == "PROMISE":
                        promise_marker = "✅ PROMISE"
                        promise_note   = "This house matter WILL manifest"
                    elif promise_status == "DENIAL":
                        promise_marker = "❌ DENIAL"
                        promise_note   = "Obstacles likely in this area"
                    elif promise_status == "WEAK_PROMISE":
                        promise_marker = "⚠️ WEAK PROMISE"
                        promise_note   = "May manifest with effort and patience"
                    else:
                        promise_marker = "○ NEUTRAL"
                        promise_note   = "Mixed indicators"

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
                            business_conn = sub_set & self.BUSINESS_HOUSES
                            service_conn  = sub_set & self.SERVICE_HOUSES
                            loss_conn     = sub_set & self.LOSS_HOUSES
                            if business_conn:
                                lines.append(f"  → Business Houses Connected: {sorted(business_conn)}")
                            if service_conn:
                                lines.append(f"  → Service Houses Connected: {sorted(service_conn)}")
                            if loss_conn:
                                lines.append(f"  ⚠️ Loss Houses Connected: {sorted(loss_conn)}")

                    lines.append("")
                    lines.append(f"  ╔═══════════════════════════════════════════════╗")
                    lines.append(f"  ║  VERDICT: {promise_marker}")
                    lines.append(f"  ║  {promise_note}")
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
            overall   = kp_structured.get("overall_verdict", "UNKNOWN")
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
            lines.append("  3. If benefic CSL has loss-house significations → DENIAL")
            lines.append("  4. If malefic CSL has business-house significations → PROMISE")
            lines.append("  5. Do NOT use fraction scoring (3/5, 2/4)")
            lines.append("  6. Use exact houses from data — never guess")
            lines.append("")
            lines.append("VERDICT MEANINGS:")
            lines.append("  • PROMISE: Sub-lord strongly signifies business/gain houses (2, 3, 7, 11)")
            lines.append("  • DENIAL: Sub-lord strongly signifies loss houses (8, 12)")
            lines.append("  • WEAK_PROMISE: Mixed significations; may manifest with sustained effort")
            lines.append("  • NEUTRAL: Cannot determine clearly from available data")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines), True

        # Fallback: use business_structural_kp and service_vs_business
        if additional_data:
            business_kp        = additional_data.get("business_structural_kp", {})
            service_vs_business = additional_data.get("service_vs_business", {})

            if business_kp or service_vs_business:
                lines = ["═══════════════════════════════════════════════════════════"]
                lines.append("⭐ KP BUSINESS ANALYSIS (Pre-computed by Evaluator)")
                lines.append("═══════════════════════════════════════════════════════════")
                lines.append("")
                lines.append("⚠️ CRITICAL: Give PRIMARY weight (60%) to KP findings below.")
                lines.append("")

                if service_vs_business:
                    final_path = service_vs_business.get("final_path", "")
                    if final_path:
                        lines.append(f"📍 Career Path Verdict: **{final_path}**")
                    csl_10 = service_vs_business.get("10th_CSL", "")
                    csl_7  = service_vs_business.get("7th_CSL", "")
                    if csl_10:
                        lines.append(f"   10th Cusp Sub Lord: {csl_10}")
                    if csl_7:
                        lines.append(f"   7th Cusp Sub Lord: {csl_7}")
                    service_score  = service_vs_business.get("service_score", 0)
                    business_score = service_vs_business.get("business_score", 0)
                    lines.append(f"   Service Score: {service_score} | Business Score: {business_score}")
                    lines.append("")

                if business_kp:
                    confidence = business_kp.get("confidence", "")
                    if confidence:
                        lines.append(f"📍 Business Confidence: {confidence}")
                    sectors = business_kp.get("final_professions", [])
                    if sectors:
                        lines.append("   Suitable Business Sectors (KP-determined):")
                        for s in sectors[:5]:
                            lines.append(f"      • {s}")
                    lines.append("")

                lines.append("═══════════════════════════════════════════════════════════")
                lines.append("NOTE: Use ONLY these sectors. Do NOT invent new business types.")
                lines.append("═══════════════════════════════════════════════════════════")

                return "\n".join(lines), True

        return "", False

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
        lines.append("   KP decides whether the EVENT happens.")
        lines.append("   Use Vedic to explain effort required.")
        lines.append("")

        business_order = [7, 10, 11, 2, 6, 3, 1]

        house_meanings = {
            1:  "Self/Personality",
            2:  "Wealth/Capital",
            3:  "Initiative/Courage",
            6:  "Competition/Loans",
            7:  "Business/Partnerships",
            10: "Career/Profession",
            11: "Gains/Profits",
        }

        for house_num in business_order:
            if house_num not in house_lords_info:
                continue

            info   = house_lords_info[house_num]
            marker = "⭐ PRIMARY" if info.get("priority") == "primary" else "○ SECONDARY"
            meaning = house_meanings.get(house_num, "General")

            lines.append(f"{marker} — HOUSE {house_num} ({meaning})")
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
                lines.append("  ✅ Assessment: STRONG — supports this house well")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE — mixed results")
            else:
                lines.append("  ⚠️ Assessment: WEAK — challenges in this area")

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
            for h in [7, 10, 11, 2, 6, 3, 1]
        )
        if not has_aspects:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON BUSINESS HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        for house_num in [7, 10, 11, 2, 6, 3, 1]:
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
                    lines.append("  → Net: POSITIVE influence")
                elif len(malefic) > len(benefic):
                    lines.append("  → Net: CHALLENGING influence")
                else:
                    lines.append("  → Net: BALANCED influence")
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
            start      = date_range.get('start', 'Unknown')
            end        = date_range.get('end', 'Unknown')

            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars',   'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus',  'Ra': 'Rahu',    'Ke': 'Ketu',
                'Saturn': 'Saturn', 'Sun': 'Sun', 'Moon': 'Moon',
                'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter',
                'Venus': 'Venus', 'Rahu': 'Rahu', 'Ketu': 'Ketu',
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
                "═══════════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS — DO NOT INVENT)",
                "═══════════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL current dasha",
                "• Use for analyzing PRESENT circumstances",
                "• For FUTURE planning, see UPCOMING DASHA PERIODS below",
                "• Do NOT invent or substitute different dasha periods",
                "═══════════════════════════════════════════════════════════",
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
            past    = dasha_timeline.get('past_2_years', [])
            current = dasha_timeline.get('current', [])
            future  = dasha_timeline.get('next_10_years', [])

            if not any([past, current, future]):
                return ""

            lines = []
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("DASHA TIMELINE (For Business Planning)")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")

            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars',   'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus',  'Ra': 'Rahu',    'Ke': 'Ketu',
            }

            def parse_dasha(name):
                parts = name.replace('>', '-').replace('/', '-').split('-')
                return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()])

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start      = date_range.get('start', '')
                    end        = date_range.get('end', '')
                    parsed     = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed}")
                    lines.append(f"    {start} to {end}")
                lines.append("")

            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years — For Business Planning):")
                lines.append("-" * 50)
                for i, d in enumerate(future[:15], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start      = date_range.get('start', '')
                    end        = date_range.get('end', '')
                    parsed     = parse_dasha(dasha_name)
                    marker     = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {start} to {end}")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("BUSINESS DASHA GUIDELINES:")
            lines.append("• Jupiter periods → Expansion, new ventures, advisory businesses")
            lines.append("• Mercury periods → Trading, consulting, communication businesses")
            lines.append("• Venus periods → Luxury, hospitality, customer-facing growth")
            lines.append("• Saturn periods → Patience required; slow but stable growth")
            lines.append("• Mars periods → Real estate, construction, decisive action")
            lines.append("• Rahu periods → Foreign trade, technology, unconventional paths")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

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
Example: "आपके लिए व्यापार path अधिक उपयुक्त है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke liye business path zyada suitable hai."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear English.
Keep technical terms clear and explain where needed.
"""

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
Read the UNIFIED_BUSINESS_VERDICT section first.
Your ENTIRE response must align with this verdict.
Note:
• Primary path (Business/Service/Hybrid)
• Confidence level
• Promise status for each house (6, 7, 10)
• KP-Vedic agreement status

"""
        if kp_available:
            base += """
**STEP 2: KP ANALYSIS (Primary — 60% weight)**

For each business cusp (7, 10, 6), explain:
• CSL → Sub Lord → Significations
• Which houses does the sub-lord signify?
• Is it PROMISE or DENIAL based on those houses?
• Do NOT use fraction scoring (3/5, 2/4)

Remember: SUB LORD significations decide the verdict, NOT planet nature.

**STEP 3: VEDIC ANALYSIS (Secondary — 30% weight)**

• House lord placements and dignity
• Strength assessment (from data)
• Does Vedic AGREE or CONFLICT with KP?
• If conflict: State it honestly, use KP for events

"""
        else:
            base += """
**STEP 2: VEDIC ANALYSIS (Primary — 80% weight)**

KP data not available. Use Vedic analysis:
• House lord placements and dignity
• Strength assessment
• Business house analysis (7, 10, 11)

"""

        if has_timing:
            base += """
**TIMING ANALYSIS (When data provided):**

⚠️ MUST mention BOTH windows:

A. BEST WINDOW (Highest score):
   • Exact dates from data
   • Why favorable (dasha lords + business significations)
   • Trade-off: may be later

B. NEAREST WINDOW (Soonest):
   • Exact dates from data
   • Why favorable
   • Trade-off: not absolute best

C. USER CHOICE:
   • Wait for best = optimal results
   • Act sooner = acceptable results faster

If best = nearest: Emphasize this is IDEAL timing!

"""

        if question_type == "developmental":
            base += f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person is under 18. DOB: {dob}

STRICT RULES:
• Do NOT recommend business launch now
• Do NOT suggest taking loans or investing capital
• Do NOT use phrases like "start your business now"
• Do NOT predict specific business start timing

INTERPRET DASHAS AS:
• Skill-building and learning cycles
• Entrepreneurial mindset development phase
• Foundation-building for future business path
• Competitive exam or education preparation

TONE:
• Developmental and encouraging
• Effort-oriented and future-focused
• Never event-triggering or immediately actionable

"""

        if question_type == "timing_fallback":
            base += """
⚠️ FALLBACK TIMING MODE (NO STRUCTURED WINDOWS)

No computed timing windows are available.

FORBIDDEN PHRASES:
• "You will launch your business in..."
• "Business start is guaranteed in..."
• "You will sign your first contract during..."

ALLOWED LANGUAGE:
• "This period strengthens readiness for..."
• "Conditions improve for business planning during..."
• "This phase builds the foundation for..."

STRUCTURE YOUR RESPONSE AS:

1️⃣ CURRENT DASHA:
• What is it building? (skills, network, capital, clarity)
• Is it preparation-oriented or opportunity-oriented?
• What should the person actively do now?

2️⃣ NEXT 2–3 UPCOMING DASHAS:
• Which period looks comparatively stronger?
• Where does probability of business success increase?
• Use phrases like "alignment improves during..." or "higher readiness in..."

3️⃣ TONE:
• Probabilistic, not deterministic
• Developmental, not event-triggering

"""

        return base

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
        logger.warning("🔥 BUSINESS PROMPT BUILDER EXECUTED")

        # ----------------------------
        # GLOBAL MINOR DETECTION
        # ----------------------------
        dob            = kwargs.get("dob")
        dasha_timeline = kwargs.get("dasha_timeline")
        is_minor = self._detect_minor(dob)
        kwargs["is_minor"] = is_minor
        logger.warning(f"[BUSINESS] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

        if "Business Prospects" in sub_subdomain:
            return self._build_business_prospects_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Business Start Timing" in sub_subdomain:
            return self._build_business_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Partnership" in sub_subdomain:
            return self._build_partnership_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_business_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # BUSINESS PROSPECTS PROMPT (Question 1)
    # ------------------------------------------------------------------
    def _build_business_prospects_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data      = kwargs.get("additional_data", {})
        is_minor             = kwargs.get("is_minor", False)
        dob                  = kwargs.get("dob")

        house_lords      = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects    = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info       = additional_data.get("lagna_info", {})
        business_matrix  = additional_data.get("business_suitability_matrix", {})
        foreign_exposure = additional_data.get("foreign_business_exposure", {})

        unified_verdict_block  = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        foreign_formatted = self._format_foreign_exposure(foreign_exposure)

        current_dasha  = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(dasha_timeline)

        if is_minor:
            developmental_override = f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob}
Age is under 18.

STRICT RULES:
• Do NOT recommend starting a business now
• Do NOT suggest loans or capital investment
• Do NOT advise immediate entrepreneurial action

INTERPRETATION RULE:
If unified verdict = Business:
→ Interpret as FUTURE business orientation
→ Focus on entrepreneurial mindset, skill-building, observing successful businesses
→ Career direction exists, but manifestation is long-term

Tone:
• Developmental and encouraging
• Preparation-focused
• Future-aligned

This override is MANDATORY.
"""
        else:
            developmental_override = ""

        analysis_instructions = self._get_analysis_instructions(
            kp_available, "developmental" if is_minor else "prospects", False, dob=dob
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Starting New Business
Sub-subdomain: Business Prospects (Path / Industry / Location)
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{developmental_override}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{foreign_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR BUSINESS PROSPECTS:
• Distinguish Business (self-employment) vs Service (employment-based business)
• Determine: Solo proprietorship vs Partnership
• Identify suitable sectors from KP data only — do NOT invent new categories
• Note Foreign/International business potential if indicated
• Use lagna lord to explain the person's natural business approach
• Align everything with the unified verdict

{self.get_output_format(kp_available, False, "prospects")}
"""

    # ------------------------------------------------------------------
    # BUSINESS START TIMING PROMPT (Question 2 — WITH TIMING!)
    # ------------------------------------------------------------------
    def _build_business_timing_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data      = kwargs.get("additional_data", {})
        is_minor             = kwargs.get("is_minor", False)
        dob                  = kwargs.get("dob")

        house_lords   = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info    = additional_data.get("lagna_info", {})

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing          = timing_windows_data.get('has_timing', False)

        logger.info(f"[BUSINESS TIMING] has_timing: {has_timing}, is_minor: {is_minor}")

        unified_verdict_block      = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        timing_formatted = ""
        if not is_minor and has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha  = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(dasha_timeline)

        if is_minor:
            analysis_instructions = self._get_analysis_instructions(
                kp_available, "developmental", False, dob=dob
            )
        elif has_timing:
            analysis_instructions = self._get_analysis_instructions(
                kp_available, "timing", True
            )
        else:
            analysis_instructions = self._get_analysis_instructions(
                kp_available, "timing_fallback", False
            )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Starting New Business
Sub-subdomain: Business Start Timing (When to launch + Loan consideration)
Query Type: TIMING (When will event occur?)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if (has_timing and not is_minor) else 'NO ❌'}
Minor Mode: {'ACTIVE 🚨' if is_minor else 'NO'}
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

SPECIFIC GUIDELINES FOR BUSINESS TIMING:
• Check PROMISE STATUS from unified verdict first
• If 7th cusp = PROMISE:
   - Adult → Business launch is supported during favorable dasha periods
   - Minor → Business aptitude exists long-term; interpret dashas as preparation phases
• If 7th cusp = DENIAL → Indicate obstacles realistically; recommend service path first
• 6th house: Analyze loan feasibility (risk-aware, never promotional)
• {'⚠️ TIMING WINDOWS PROVIDED — MUST USE EXACT DATES!' if (has_timing and not is_minor) else ''}
• {'Mention BOTH best and nearest windows' if (has_timing and not is_minor) else ''}
• Align fully with unified verdict

{self.get_output_format(
    kp_available,
    False if is_minor else has_timing,
    "developmental" if is_minor else "timing"
)}
"""

    # ------------------------------------------------------------------
    # PARTNERSHIP PROSPECTS PROMPT (Question 3)
    # ------------------------------------------------------------------
    def _build_partnership_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data      = kwargs.get("additional_data", {})
        is_minor             = kwargs.get("is_minor", False)
        dob                  = kwargs.get("dob")

        house_lords   = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info    = additional_data.get("lagna_info", {})

        unified_verdict_block      = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha  = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(dasha_timeline)

        business_kp      = additional_data.get("business_structural_kp", {})
        partners_needed  = business_kp.get("partners_needed", None)

        if is_minor:
            developmental_override = f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob}
Age is under 18.

• Do NOT advise entering partnerships now
• Frame partnership aptitude as a long-term quality to develop
• Encourage learning team collaboration and leadership in academic/social settings
"""
        else:
            developmental_override = ""

        analysis_instructions = self._get_analysis_instructions(
            kp_available, "developmental" if is_minor else "partnership", False, dob=dob
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Starting New Business
Sub-subdomain: Business Partnership Prospects (Solo vs Partnership / Family Business)
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Partners Needed (KP): {'YES' if partners_needed else 'NO' if partners_needed is False else 'UNKNOWN'}
Minor Mode: {'ACTIVE 🚨' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{developmental_override}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR PARTNERSHIP:
• 7th house is PRIMARY for partnership analysis
• Determine clearly: Solo vs Partnership recommendation
• If partnership indicated, describe ideal partner type/qualities
• Address family business scenarios with clear role boundaries
• Discuss financial boundaries in partnerships — risk-aware, not promotional

{self.get_output_format(kp_available, False, "partnership")}
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
        additional_data      = kwargs.get("additional_data", {})

        house_lords   = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info    = additional_data.get("lagna_info", {})

        unified_verdict_block      = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha       = kwargs.get('current_dasha')
        current_dasha_block = self._format_current_dasha(current_dasha)

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Starting New Business
Sub-subdomain: Business Remedies
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

REMEDY GUIDELINES:

1. **Identify Weak Areas from Analysis:**
   - Which cusps show DENIAL?
   - Which house lords are weak?
   - Which planets need strengthening?

2. **Current Dasha Lord Remedies:**
   - Strengthen current dasha lord for immediate relief
   - Prepare for upcoming dasha lords (begin 3 months before)

3. **Priority:**
   - Primary: Strengthen planets affecting business (7th, 10th house)
   - Secondary: Boost gains (11th house)
   - Tertiary: Address obstacles (8th, 12th connections)

BUSINESS REMEDY GUIDE:
- 7th LORD WEAK: Gemstone/mantra of 7th lord; strengthen for business success
- MERCURY WEAK: Wednesday fasts, green charity, Vishnu worship (trade/IT/consulting)
- JUPITER WEAK: Thursday fasts, yellow items, Guru worship (expansion/advisory)
- SATURN ISSUES: Saturday service, discipline practices (manufacturing/infrastructure)
- VENUS WEAK: Friday worship, white items (luxury/hospitality businesses)
- RAHU/KETU: Node pacification — essential for risk management in unconventional ventures

{self.get_output_format(kp_available, False, "remedies")}
"""

    # ------------------------------------------------------------------
    # GENERAL FALLBACK PROMPT
    # ------------------------------------------------------------------
    def _build_general_business_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data      = kwargs.get("additional_data", {})
        is_minor             = kwargs.get("is_minor", False)
        dob                  = kwargs.get("dob")

        house_lords   = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info    = additional_data.get("lagna_info", {})

        unified_verdict_block      = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha  = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(dasha_timeline)

        analysis_instructions = self._get_analysis_instructions(
            kp_available, "developmental" if is_minor else "general", False, dob=dob
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Starting New Business
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor Mode: {'ACTIVE 🚨' if is_minor else 'NO'}
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
• Use pure KP methodology if KP data is available
• Be honest about KP-Vedic agreement or conflict
• Provide actionable, realistic guidance

{self.get_output_format(kp_available, False, "general")}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT — DYNAMIC BASED ON KP + TIMING + QUESTION TYPE
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, question_type: str = "general") -> str:
        """Generate output format based on KP availability, timing, and question type."""

        # ── Timing section ───────────────────────────────────────────
        if has_timing:
            timing_section = """
**F. TIMING RECOMMENDATION (CRITICAL):**

⚠️ MANDATORY: Include BOTH timing options below.

**🏆 BEST WINDOW (Highest Astrological Score):**
- Period: [exact start date] to [exact end date]
- Dasha: [Maha > Antara > Pratyantar]
- Age at start: [N] years
- Score: [final_score]/100
- Why this is BEST:
  * Maha Dasha lord ([planet]): signifies [business houses] → Score [X]/10
  * Antara Dasha lord ([planet]): reinforces [connection] → Score [Y]/10
  * Pratyantar Dasha lord ([planet]): final trigger → Score [Z]/10
- Trade-off: May be further away, but strongest planetary support

**⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):**
- Period: [exact start date] to [exact end date]
- Dasha: [Maha > Antara > Pratyantar]
- Age at start: [N] years
- Score: [final_score]/100
- Why this is NEAREST:
  * Earliest window with favorable score (≥ 50)
  * Actionable sooner with acceptable alignment
- Trade-off: Sooner opportunity, but not peak alignment

**👤 RECOMMENDATION:**
Choose BEST if: You can wait and want maximum success probability
Choose NEAREST if: You have a ready opportunity and cannot wait

⚠️ If BEST = NEAREST (same window):
"🎯 IDEAL TIMING: The best window IS the nearest window. Act with confidence during this period."

**LOAN CONSIDERATION (6th House Analysis):**
- 6th house condition: [Strong / Moderate / Weak]
- Loan feasibility: [Favorable / Cautious / Avoid]
- Risk level: [Low / Medium / High]
- Recommendation: [Specific, risk-aware guidance — never promotional]
"""
        else:
            timing_section = ""

        # ── KP-available format ───────────────────────────────────────
        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT — FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, actionable answer in plain language. No astrological jargon.>
<Example: "आपके लिए व्यापार (Business) path उपयुक्त है। Trading या IT consulting में अच्छे अवसर हैं।">
<MUST align with unified verdict.>

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Primary Path: [from unified verdict]
- Confidence: [from unified verdict]
- Promise Status: [7th: X | 10th: Y | 6th: Z]
- KP-Vedic Agreement: [AGREEMENT / PARTIAL / CONFLICT]

**B. KP SYSTEM ANALYSIS (Primary — 60% weight):**

For EACH business cusp (7th, 10th, 6th), use this EXACT format:

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor — NOT the verdict)
- CSL in Nakshatra: [Nakshatra name]
- Star Lord: [Planet]
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Business Houses Connected: [list from 2, 3, 7, 11]
- Service Houses Connected: [list from 2, 6, 10, 11]
- Loss Houses Connected: [list from 8, 12]
- **VERDICT: PROMISE / DENIAL / WEAK PROMISE** — based on sub-lord significations
- Why: [Explain how the significations lead to this verdict]

**CORRECT EXAMPLE — DO THIS:**
"**House 7 (Business/Trade):**
- CSL: Mercury (neutral flavor)
- CSL in Nakshatra: Ashlesha
- Star Lord: Mercury
- Sub Lord: Jupiter
- Sub Lord Signifies: Houses [2, 7, 11]
- Business Houses Connected: [2, 7, 11]
- Service Houses Connected: [2, 11]
- Loss Houses Connected: [ ]
- **VERDICT: PROMISE — BUSINESS PATH STRONGLY SUPPORTED**
- Why: Jupiter as sub-lord signifies income (2nd), trade (7th), and gains (11th) — all three core
  business houses. No loss houses involved. This sub-lord pattern confirms that independent
  business will manifest and generate income."

**WRONG EXAMPLE — NEVER DO THIS:**
"House 7: Mercury is a neutral planet so business results will be mixed." ❌
(This ignores sub-lord and significations entirely — never acceptable in KP.)

⚠️ Do NOT use fraction scoring (3/5, 2/4)
⚠️ Sub-lord significations decide the verdict, NOT the nature of CSL

**C. VEDIC ANALYSIS (Secondary — 30% weight):**

**House Lords:**
- 7th Lord: [Planet, placement, dignity, strength /100]
- 10th Lord: [Planet, placement, dignity, strength /100]
- 11th Lord: [Planet, placement, dignity, strength /100]

**Vedic-KP Agreement Check:**
- If agree:   "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic suggests [Y]. KP takes priority for events."
- If conflict: "❌ CONFLICT: KP indicates [X], Vedic indicates [Y]. Using KP for final verdict."

**D. LAGNA LORD (Business Personality):**
- [Planet] as lagna lord in House [N]
- Business approach: [description from data]

**E. BUSINESS TYPE SUITABILITY:**

| Business Type | Suitability | KP Reasoning |
|---------------|-------------|--------------|
| [Type]        | HIGH / MODERATE / LOW | [from sub-lord significations] |

{timing_section}

**G. DASHA CONTEXT:**
- Current: [dasha] — [business impact]
- Upcoming favorable: [dasha + dates]

**SUMMARY:**
<2–3 sentences. MUST align with unified verdict.>
<Include timing guidance if available.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial — not generic]

**REMEDIES_GENERAL:**
- [Practical business steps aligned with chart strengths]
"""

        # ── Vedic-only format ─────────────────────────────────────────
        else:
            return f"""
OUTPUT FORMAT (STRICT — VEDIC ONLY):

**GENERAL_ANSWER:**
<Clear, actionable business recommendation in plain language.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD (Business Personality):**
- Planet: [Name]
- Placed in: House [N]
- Business approach: [description]

**B. HOUSE LORD ANALYSIS (Primary):**

For each key business house (7, 10, 11):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Business Impact: [explanation]

**C. BUSINESS PATH ASSESSMENT:**

| Path | Suitability | Reasoning |
|------|-------------|-----------|
| Business | [HIGH / MODERATE / LOW] | [based on house analysis] |
| Service | [HIGH / MODERATE / LOW] | [based on house analysis] |

{timing_section}

**D. DASHA CONTEXT:**
- Current: [dasha]
- Business impact: [explanation]

**SUMMARY:**
<Concise business outlook>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical steps]
"""
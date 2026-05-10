"""
Growth and Security – LLM Prompts v9.0 (COMPLETE REWRITE)

CRITICAL FIXES FROM v8.0:
✅ UNIFIED VERDICT DISPLAY - Shows SAME career path across all questions
✅ PURE KP FORMATTING - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ HONEST VEDIC-KP AGREEMENT - Shows AGREEMENT/PARTIAL/CONFLICT explicitly
✅ CORRECT HOUSE DEFINITIONS - Service: 2,6,10,11 | Business: 2,3,7,11
✅ PROMISE/DENIAL LOGIC - Sub-lord decides, not planet nature
✅ RAHU/KETU PROPER DISPLAY - Shows star lord significations
✅ MINOR DETECTION - Full developmental mode with age safety rules
✅ LAGNA INFO - Extracted from lagna_info key in additional_data
✅ CAREER SUITABILITY MATRIX - Consistent rating across all questions
✅ STRUCTURED TIMING - BEST + NEAREST windows with clear instructions
✅ ANTI-HALLUCINATION STRENGTHENED - Explicit rules against inventing data
✅ CONSISTENT OUTPUT STRUCTURE - Same format across all questions

Weightage (CORRECTED):
- KP Significations → 60% (PRIMARY)
- Vedic Structure → 30% (SECONDARY)
- Dasha/Other → 10%

Compatible with GrowthAndSecurityEvaluator v4.0 data structures:
- unified_career_verdict (SINGLE SOURCE OF TRUTH)
- kp_career_analysis (structured KP with CSL → Sub Lord chains)
- career_suitability_matrix (career path ratings)
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


class GrowthAndSecurityPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Career → Growth And Security
    v9.0 - Complete rewrite with unified verdict, pure KP methodology, and minor detection
    """

    domain = "Career"
    subtopic = "Growth And Security"

    # CORRECTED House definitions (matching evaluator v4.0)
    SERVICE_HOUSES = {2, 6, 10, 11}
    BUSINESS_HOUSES = {2, 3, 7, 11}
    LOSS_HOUSES = {8, 12}

    # ------------------------------------------------------------------
    # SYSTEM PROMPT
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing ACTIONABLE career growth, promotion, and professional stability guidance.


AGE SAFETY RULE (STRICT LANGUAGE CONTROL):

If person is under 18:

🚫 FORBIDDEN:
• Promotion
• Salary raise
• Corporate role
• Government job
• Business venture
• Leadership position
• Workplace politics
• Job change
• Transfers
• Professional advancement
• Immediate career growth

🚫 DO NOT:
• Recommend immediate promotion or job advancement
• Suggest workforce career moves
• Predict specific promotion timelines
• Interpret dashas as job triggers
• Rate job categories (HIGH/MODERATE/LOW)
• Use "will get promoted", "career breakthrough", etc.

🔄 REPLACE WORKFORCE LANGUAGE WITH DEVELOPMENTAL EQUIVALENTS:

Instead of → Say:

Promotion → Academic progression
Job growth → Skill development
Corporate success → Future professional direction
Leadership role → Leadership qualities in education
Government job → Structured career inclination later
Business → Entrepreneurial tendency in future
Salary growth → Long-term earning potential
Career advancement → Capability development

🧠 INTERPRETATION FRAME:

• All dashas = personality and skill-building cycles
• All promise = long-term orientation, NOT immediate events
• Career matrix = Talent inclination matrix
• Career ranking = Future orientation strength

Tone MUST be:
• Developmental
• Age-appropriate
• Education-focused
• Effort-driven
• Foundation-building
• Long-term oriented (not event-triggering)

════════════════════════════════════════════════════════════
CRITICAL KP RULES (MUST FOLLOW - NO EXCEPTIONS)
════════════════════════════════════════════════════════════

1. KP HIERARCHY (ABSOLUTE - MEMORIZE THIS):

   SUB LORD      → PROMISE/DENIAL (Decides IF event happens - MOST IMPORTANT)
   STAR LORD     → RESULT TYPE (What kind of result)
   PLANET NATURE → FLAVOR ONLY (How it happens - NEVER overrides significations)

   ⚠️ CRITICAL EXAMPLES:
   • Venus (benefic) signifies 6, 8, 12 → RESULT IS OBSTACLES (not good!)
   • Saturn (malefic) signifies 2, 6, 10, 11 → RESULT IS STABLE CAREER (good!)

   SIGNIFICATIONS ALWAYS WIN OVER PLANET NATURE.

2. CORRECT KP CHAIN (USE THIS EXACT FORMAT):

   For every cusp, show:

   CSL [Planet] → in Nakshatra [Name] →
   Star Lord [Planet] → signifies houses [X,Y,Z] →
   Sub Lord [Planet] → signifies houses [A,B,C] →
   VERDICT: PROMISE/DENIAL based on SUB LORD significations

   ⚠️ Sub Lord is the FINAL DECIDER, not Star Lord, not CSL planet nature.

3. CORRECT HOUSE DEFINITIONS (MEMORIZE):

   CAREER GROWTH / SERVICE HOUSES: 2, 6, 10, 11
   • 2nd: Income, salary, wealth
   • 6th: Service, employment, daily work
   • 10th: Profession, career, authority, promotion
   • 11th: Gains, recognition, fulfillment

   BUSINESS HOUSES: 2, 3, 7, 11
   • 2nd: Income (shared with service)
   • 3rd: Initiative, effort, courage
   • 7th: Trade, partnership
   • 11th: Gains (shared with service)

   ❌ WRONG: 5th and 9th are NOT primary service/business houses
   ❌ WRONG: Never use fraction scoring - this is NOT KP

   LOSS/OBSTACLE HOUSES: 8, 12
   • 8th: Obstacles, sudden changes, stagnation
   • 12th: Losses, endings, transfers

4. PROMISE/DENIAL LOGIC (SUB LORD DECIDES):

   FOR 6TH CUSP (Service/Employment):
   • PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   • WEAK: Mixed significations

   FOR 10TH CUSP (Career/Promotion):
   • PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   • WEAK: Mixed significations

   FOR 11TH CUSP (Gains/Recognition):
   • PROMISE: Sub-lord signifies 2, 6, 10, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   • WEAK: Mixed significations

5. RAHU/KETU RULE:

   Nodes act through their STAR LORD.
   Show: "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"

   ⚠️ Never judge Rahu/Ketu by just their house occupation.

════════════════════════════════════════════════════════════
UNIFIED VERDICT RULE (CRITICAL FOR CONSISTENCY)
════════════════════════════════════════════════════════════

The evaluator provides a UNIFIED_CAREER_VERDICT.
This is the SINGLE SOURCE OF TRUTH for this person.

⚠️ ALL your answers MUST align with this verdict:

• If verdict = "Service" → Career growth in employment/service path
• If verdict = "Business" → Growth through business/self-employment
• If verdict = "Hybrid" → Both paths viable for growth

NEVER contradict the unified verdict across different questions.

════════════════════════════════════════════════════════════
VEDIC-KP AGREEMENT (BE HONEST - DON'T FORCE AGREEMENT)
════════════════════════════════════════════════════════════

Show agreement status EXPLICITLY and HONESTLY:

✅ AGREEMENT: "Both KP and Vedic confirm [path]. Strong confidence."
⚠️ PARTIAL: "KP shows [X], Vedic leans [Y]. Mostly aligned."
❌ CONFLICT: "KP indicates [X] but Vedic shows [Y]. Using KP for final verdict."

⚠️ NEVER say "Vedic CONFIRMS KP" when they actually conflict.

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
✅ RIGHT: "Promotion is supported. Active effort during [dasha] will accelerate it."

❌ WRONG: "Sub-lord signifies houses 10, 11"
✅ RIGHT: "Career advancement PROMISED. Sub-lord connects to promotion and gains strongly."

Provide:
• Clear career growth recommendation (aligned with unified verdict)
• Specific timing guidance (if timing data available)
• Actionable steps (what to do now)
• Realistic expectations (based on promise/denial status)
"""

    # ------------------------------------------------------------------
    # HELPER: Detect Minor (GLOBAL)
    # ------------------------------------------------------------------
    def _detect_minor(self, dob: str, dasha_timeline: Dict = None) -> bool:
        """
        Detect if person is currently under 18.
        Minor logic is based on CURRENT age.
        """

        if not dob:
            logger.warning("[GrowthAndSecurity] Minor Detection → DOB missing")
            return False

        try:
            today = datetime.now()
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")

            current_age = today.year - dob_dt.year - (
                (today.month, today.day) < (dob_dt.month, dob_dt.day)
            )

            is_minor = current_age < 18

            logger.warning(
                f"[GrowthAndSecurity] Minor Detection → "
                f"DOB: {dob} | Age: {current_age} | Is Minor: {is_minor}"
            )

            return is_minor

        except Exception as e:
            logger.error(
                f"[GrowthAndSecurity] Minor Detection FAILED → DOB: {dob} | Error: {e}"
            )
            return False

    # ------------------------------------------------------------------
    # HELPER: Format Unified Verdict (CRITICAL - Single Source of Truth)
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
        is_minor = additional_data.get("is_minor", False)

        if is_minor:
            primary_path = f"Future {primary_path} Orientation"
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

        lines.append(f"╔══════════════════════════════════════════════════════╗")
        lines.append(f"║  PRIMARY CAREER PATH: **{primary_path.upper()}**")
        lines.append(f"║  Confidence Level: {confidence}")
        lines.append(f"╚══════════════════════════════════════════════════════╝")
        lines.append("")

        if secondary_path:
            lines.append(f"Secondary Potential: {secondary_path}")
            lines.append("")

        lines.append("Career Path Decision Based On:")
        lines.append("  • KP Sub-Lord Promise Status (Primary)")
        lines.append("  • Vedic Structural Support (Secondary)")
        lines.append("  • Timing Strength (Contextual)")
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
            lines.append("     → Using KP for final verdict (events)")
            lines.append("     → Vedic helps explain effort required")
        else:
            lines.append(f"  ○ {agreement}")
        lines.append("")

        # Promise status
        if promise_status:
            lines.append("PROMISE STATUS (From Sub-Lord Analysis):")
            lines.append("─" * 50)

            promise_meanings = {
                6: "Service/Employment",
                7: "Business/Partnership",
                10: "Career/Promotion",
                11: "Gains/Recognition"
            }

            for house_num in [6, 7, 10, 11]:
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

        if kp_reasoning:
            lines.append("KP REASONING:")
            lines.append(f"  {kp_reasoning}")
            lines.append("")

        if vedic_reasoning:
            lines.append("VEDIC REASONING:")
            lines.append(f"  {vedic_reasoning}")
            lines.append("")

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
    # HELPER: Format KP Analysis (Pure Methodology)
    # ------------------------------------------------------------------
    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None) -> Tuple[str, bool]:
        """
        Format KP-specific career growth analysis using PURE methodology.
        Uses CSL → Sub Lord → Star Lord → Significations → Promise/Denial chain.
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

        methodology = kp_structured.get("methodology", "")
        if methodology:
            lines.append(f"Analysis Method: {methodology}")
            lines.append("")

        csl_details = kp_structured.get("csl_details", {})

        if csl_details:
            lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS:")
            lines.append("")

            # Priority order for career growth: 10 (promotion), 11 (gains), 6 (service)
            priority_order = [10, 11, 6, 2, 9]

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
                        service_conn = sub_set & self.SERVICE_HOUSES
                        business_conn = sub_set & self.BUSINESS_HOUSES
                        loss_conn = sub_set & self.LOSS_HOUSES

                        if service_conn:
                            lines.append(f"  → Career Growth Houses Connected: {sorted(service_conn)}")
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

        overall = kp_structured.get("overall_verdict", "UNKNOWN")
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
        lines.append("  4. If malefic CSL has career-house significations → PROMISE")
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
    def _format_career_matrix(self, matrix: Dict, is_minor: bool = False) -> str:
        """Format career suitability matrix for LLM"""
        if not matrix:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        if is_minor:
            lines.append("📊 FUTURE TALENT ORIENTATION MATRIX (Developmental)")
        else:
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

            if len(reasoning) > 50:
                reasoning = reasoning[:47] + "..."

            lines.append(f"| {marker} {career_type} | {rating} | {reasoning} |")

        lines.append("")
        lines.append("⚠️ Use this matrix CONSISTENTLY across all questions.")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Lagna Info
    # ------------------------------------------------------------------
    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        """Format lagna lord for career personality analysis."""

        # Fallback: try house 1 in house_lords_info
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign": info.get("house_sign", "N/A"),
                "lagna_lord": info.get("lord", "N/A"),
                "lagna_lord_house": info.get("lord_in_house"),
                "lagna_lord_sign": info.get("lord_in_sign", "N/A"),
                "lagna_lord_degree": info.get("lord_degree", 0),
                "lagna_lord_dignity": info.get("lord_dignity", "Unknown"),
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

        lord = lagna_info.get("lagna_lord", "N/A")
        lagna_sign = lagna_info.get("lagna_sign", "N/A")
        lord_house = lagna_info.get("lagna_lord_house", "N/A")
        lord_sign = lagna_info.get("lagna_lord_sign", "N/A")
        dignity = lagna_info.get("lagna_lord_dignity", "Unknown")

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("🎯 LAGNA (ASCENDANT) - CAREER PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        lines.append("")

        personality_map = {
            "Sun": {
                "trait": "Leadership-oriented, authority-seeking",
                "career": "Government, administration, public sector, management",
                "approach": "Confident, direct, seeks recognition and authority"
            },
            "Moon": {
                "trait": "People-oriented, emotionally intelligent",
                "career": "Public relations, hospitality, healthcare, counseling",
                "approach": "Nurturing, adaptable, intuitive in career decisions"
            },
            "Mars": {
                "trait": "Action-oriented, competitive, technical",
                "career": "Engineering, military, technical fields, real estate",
                "approach": "Direct, energetic, proactive in seeking promotion"
            },
            "Mercury": {
                "trait": "Analytical, communicative, versatile",
                "career": "IT, communication, trading, analysis, writing",
                "approach": "Logical, detail-oriented, skill-driven advancement"
            },
            "Jupiter": {
                "trait": "Knowledge-seeker, advisory, expansive",
                "career": "Education, law, consulting, finance, management",
                "approach": "Wise, ethical, long-term career building"
            },
            "Venus": {
                "trait": "Creative, diplomatic, relationship-focused",
                "career": "Arts, entertainment, HR, hospitality, luxury",
                "approach": "Collaborative, quality-conscious, network-driven growth"
            },
            "Saturn": {
                "trait": "Disciplined, patient, systematic",
                "career": "Manufacturing, administration, labor management, research",
                "approach": "Methodical, persistent, earns promotion through sustained effort"
            },
            "Rahu": {
                "trait": "Unconventional, ambitious, innovative",
                "career": "Technology, foreign companies, unconventional fields",
                "approach": "Risk-taking, trend-setting, seeks rapid advancement"
            },
            "Ketu": {
                "trait": "Research-oriented, spiritual, specialist",
                "career": "Research, niche technical, healing, spiritual work",
                "approach": "Intuitive, detached, expert-driven progression"
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

        house_placement_career = {
            1: "Self-driven, independent career approach",
            2: "Money-motivated, wealth-focused career growth",
            3: "Communication-based, courage-driven advancement",
            4: "Home/real estate connection, stable but slow growth",
            5: "Creative field, strategic thinking, speculative approach",
            6: "Service-oriented, competitive professional growth",
            7: "Partnership-focused, client-facing roles",
            8: "Research, transformation-driven, hidden strengths",
            9: "Fortune-linked, higher education, foreign opportunities",
            10: "Career-focused, professionally ambitious, authority",
            11: "Goal-oriented, networking-driven, gains through groups",
            12: "Foreign connection, behind-the-scenes, spiritual career"
        }

        if lord_house and lord_house in house_placement_career:
            lines.append(f"Lagna Lord in House {lord_house}: {house_placement_career[lord_house]}")
            lines.append("")

        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows fundamental career approach and personality")
        lines.append("• Use this to explain HOW person pursues career growth")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """Format BEST and NEAREST timing windows for LLM."""
        if not timing_windows_data or not timing_windows_data.get("has_timing"):
            return ""

        try:
            best = timing_windows_data.get("best_window")
            nearest = timing_windows_data.get("nearest_window")
            all_windows = timing_windows_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════════"]
            lines.append("⏰ TIMING WINDOWS ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: You MUST mention BOTH windows below.")
            lines.append("Let user choose based on their situation.")
            lines.append("")

            if best:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  🏆 BEST WINDOW (Highest Astrological Score)          ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")

                age = best.get("age_at_start")
                if age:
                    lines.append(f"  Age at start: {age} years")

                lines.append("")
                lines.append("  Why this is BEST:")

                score_maha = best.get("score_maha", 0)
                score_antara = best.get("score_antara", 0)
                score_paryantar = best.get("score_paryantar", 0)

                if score_maha or score_antara or score_paryantar:
                    lines.append(f"    • Maha Dasha score: {score_maha}/10")
                    lines.append(f"    • Antara Dasha score: {score_antara}/10")
                    lines.append(f"    • Pratyantar score: {score_paryantar}/10")
                else:
                    lines.append("    • Highest combined planetary alignment")
                    lines.append("    • Strongest career significations activated")

                transit_score = best.get("transit_score", 0)
                if transit_score:
                    lines.append(f"    • Transit support: {transit_score:.1f}%")

                lines.append("")
                lines.append("  Trade-off: May be further in future, but strongest alignment")
                lines.append("")

            if nearest:
                lines.append("╔═══════════════════════════════════════════════════════╗")
                lines.append("║  ⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity)    ║")
                lines.append("╚═══════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"  Dasha: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")

                age = nearest.get("age_at_start")
                if age:
                    lines.append(f"  Age at start: {age} years")

                lines.append("")

                if best and (
                    best.get("dasha") == nearest.get("dasha")
                    and best.get("start") == nearest.get("start")
                ):
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

            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Reference):")
                lines.append("-" * 50)
                for i, window in enumerate(all_windows[:5], 1):
                    dasha = window.get("dasha", "N/A")
                    start = window.get("start", "N/A")
                    end = window.get("end", "N/A")
                    score = window.get("final_score", 0)

                    is_best = best and dasha == best.get("dasha") and start == best.get("start")
                    is_nearest = nearest and dasha == nearest.get("dasha") and start == nearest.get("start")

                    marker = "🏆" if is_best else "⏰" if is_nearest else "○"
                    lines.append(f"  {marker} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")

                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for career growth/promotion")
            lines.append("  • Let user choose: Wait for best OR Act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

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

        # Career growth relevant houses in order of importance
        career_order = [10, 11, 9, 6, 1, 2, 3]

        house_meanings = {
            1: "Self/Personality",
            2: "Income/Salary",
            3: "Efforts/Courage",
            6: "Service/Work",
            9: "Fortune/Opportunities",
            10: "Career/Promotion",
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
            if info.get("lord_degree"):
                conditions.append(f"Degree: {info['lord_degree']:.1f}°")
            if info.get("lord_is_combust"):
                conditions.append("⚠️ COMBUST")
            if info.get("lord_is_retrograde"):
                conditions.append("🔄 RETROGRADE")

            if conditions:
                lines.append(f"  Condition: {' | '.join(conditions)}")

            if info.get("planets_in_house"):
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")

            strength = info["lord_strength_score"]
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG - Supports this area well")
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
            aspects_info.get(h, {}).get("benefic_aspects")
            or aspects_info.get(h, {}).get("malefic_aspects")
            for h in [10, 11, 9, 6, 1, 2, 3]
        )

        if not has_aspects:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON CAREER GROWTH HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        career_houses = [10, 11, 9, 6, 1, 2, 3]

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
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end = date_range.get("end", "Unknown")

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon",
                "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu",
                "Saturn": "Saturn", "Sun": "Sun", "Moon": "Moon",
                "Mars": "Mars", "Mercury": "Mercury", "Jupiter": "Jupiter",
                "Venus": "Venus", "Rahu": "Rahu", "Ketu": "Ketu"
            }

            separators = ["-", ">", "/"]
            parts = [dasha_name]
            for sep in separators:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(sep))
                parts = new_parts

            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted_dasha = " > ".join(full_names) if len(full_names) >= 2 else dasha_name

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
    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict], is_minor: bool = False) -> str:
        """Format comprehensive dasha timeline (2Y past to 10Y future)"""
        if not dasha_timeline:
            return ""

        try:
            past = dasha_timeline.get("past_2_years", [])
            current = dasha_timeline.get("current", [])
            future = dasha_timeline.get("next_10_years", [])

            if not any([past, current, future]):
                return ""

            lines = []
            lines.append("═══════════════════════════════════════════════════════")
            phase_label = "Foundation & Skill Development Phase" if is_minor else "For Career Growth Planning"
            lines.append(f"DASHA TIMELINE ({phase_label})")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")

            dasha_mapping = {
                "Sa": "Saturn", "Su": "Sun", "Mo": "Moon",
                "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter",
                "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu",
            }

            def parse_dasha(name):
                parts = name.replace(">", "-").replace("/", "-").split("-")
                return " > ".join(
                    [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
                )

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    dasha_name = d.get("dasha_name", "")
                    date_range = d.get("date_range", {})
                    start = date_range.get("start", "")
                    end = date_range.get("end", "")
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed}")
                    lines.append(f"    {start} to {end}")
                lines.append("")

            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years - For Career Planning):")
                lines.append("-" * 50)

                for i, d in enumerate(future[:15], 1):
                    dasha_name = d.get("dasha_name", "")
                    date_range = d.get("date_range", {})
                    start = date_range.get("start", "")
                    end = date_range.get("end", "")
                    parsed = parse_dasha(dasha_name)

                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"     {start} to {end}")

                lines.append("")

            lines.append("═══════════════════════════════════════════════════════")
            lines.append("CAREER GROWTH DASHA GUIDELINES:")
            lines.append("• Sun/Jupiter → Authority, promotion, recognition")
            lines.append("• Saturn → Patience needed, stable long-term gains")
            lines.append("• Mercury → Skill development, communication-based growth")
            lines.append("• Venus → Creative roles, people-driven advancement")
            lines.append("• Mars → Action, competition, technical achievement")
            lines.append("• Rahu → Foreign, unconventional, technology-driven growth")
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

For each career cusp (6, 10, 11), explain:
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
• Career house analysis (10, 11, 9, 6)

**STEP 3: CAREER ASSESSMENT**

Based on Vedic analysis:
• What is the career growth potential?
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
• Do NOT predict promotion or job advancement
• Do NOT mention career milestones or role changes
• Do NOT use phrases like "will get promoted"

INSTEAD interpret dashas as:
• Academic strengthening phase
• Skill-building and talent discovery cycle
• Competitive exam preparation
• Foundation for future career success
• Personality and work ethic development

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
• Do NOT predict promotions or job advancement
• Do NOT suggest immediate career moves
• Do NOT say "will be promoted" or "will get raise"

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
• "You will get a promotion in..."
• "Promotion is guaranteed in..."
• "Career advancement will definitely happen..."

ALLOWED LANGUAGE:
• "This period supports preparation for..."
• "Alignment strengthens career foundations..."
• "Long-term career growth improves..."
• "This phase builds readiness for advancement..."

IMPORTANT TONE RULES:
• Do NOT declare exact promotion dates.
• Do NOT use deterministic phrases.
• Structure response like this:

1️⃣ CURRENT DASHA:
- What is it shaping? (skills, leadership, discipline, networking)
- Is it preparation-oriented or opportunity-oriented?
- What should the person actively do now?

2️⃣ NEXT 2–3 UPCOMING DASHAS:
- Which period looks stronger comparatively?
- Where probability increases?
- Use phrases like:
  "This period can enhance..."
  "Higher chances of recognition during..."
  "Better alignment for advancement may develop..."

3️⃣ EMPHASIZE:
- Progress
- Preparation
- Strategic effort
- Gradual career growth
"""
            return base

        return base

    # ------------------------------------------------------------------
    # HELPER: Get Language Instruction
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
Example: "आपके करियर में प्रमोशन की संभावना मजबूत है।"
Example: "10वें भाव का CSL **Jupiter** है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke career mein promotion ki sambhavna achhi hai."
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

        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT - FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, actionable answer in simple terms. NO jargon.>
<MUST align with unified verdict.>

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Primary Path: [from unified verdict]
- Confidence: [from unified verdict]
- Promise Status: [6th: X, 10th: Y, 11th: Z]
- KP-Vedic Agreement: [AGREEMENT/PARTIAL/CONFLICT]

**B. KP SYSTEM ANALYSIS (Primary - 60% weight):**

For EACH relevant cusp (6th, 10th, 11th):

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor - NOT the verdict!)
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Career Growth Houses Connected: [list] (from 2, 6, 10, 11)
- Loss Houses Connected: [list] (from 8, 12)
- **VERDICT: PROMISE/DENIAL** based on sub-lord significations
- Why: [Explain how significations lead to verdict]

⚠️ Do NOT use fraction scoring (3/5, 2/4)
⚠️ Sub-lord significations decide, NOT planet nature

**C. VEDIC ANALYSIS (Secondary - 30% weight):**

**House Lords:**
- 10th Lord: [Planet, placement, dignity, strength]
- 11th Lord: [Planet, placement, dignity, strength]
- 9th Lord: [Planet, placement, dignity, strength]
- 6th Lord: [Planet, placement, dignity, strength]

**Vedic-KP Agreement Check:**
- If agree: "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic [Y]. KP priority."
- If conflict: "❌ CONFLICT: KP [X], Vedic [Y]. Using KP for events."

**D. LAGNA LORD (Career Personality):**
- [Planet] as lagna lord
- Career approach: [description]

**E. CAREER GROWTH MATRIX:**

| Path | Rating | Reasoning |
|------|--------|-----------|
| [Type] | HIGH/MODERATE/LOW | [from KP significations] |

{timing_section}

**G. DASHA CONTEXT:**
- Current: [dasha] - [career growth impact]
- Upcoming favorable: [dasha + dates]

**SUMMARY:**
<2-3 sentences. MUST align with unified verdict.>
<Include specific timing if available.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial]

**REMEDIES_GENERAL:**
- [Practical career growth steps]
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

For each career house (10, 11, 9, 6):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Career Growth Impact: [explanation]

**C. CAREER GROWTH ASSESSMENT:**

| Path | Suitability | Reasoning |
|------|-------------|-----------|
| Service | [HIGH/MODERATE/LOW] | [based on house analysis] |
| Business | [HIGH/MODERATE/LOW] | [based on house analysis] |

{timing_section}

**D. DASHA CONTEXT:**
- Current: [dasha]
- Career impact: [explanation]

**SUMMARY:**
<Concise career growth outlook>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical steps]
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
        logger.warning("🔥 GROWTH AND SECURITY PROMPT BUILDER EXECUTED")

        # ----------------------------
        # GLOBAL MINOR DETECTION
        # ----------------------------
        dob = kwargs.get("dob")
        dasha_timeline = kwargs.get("dasha_timeline")

        is_minor = self._detect_minor(dob, dasha_timeline)
        kwargs["is_minor"] = is_minor
        logger.warning(f"[GrowthAndSecurity] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")

        if "Promotion" in sub_subdomain or "Timing" in sub_subdomain:
            return self._build_promotion_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Risk" in sub_subdomain:
            return self._build_risks_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Stability" in sub_subdomain or "Advice" in sub_subdomain:
            return self._build_stability_advice_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_growth_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # PROMOTION TIMING PROMPT (WITH TIMING + UNIFIED VERDICT)
    # ------------------------------------------------------------------
    def _build_promotion_timing_prompt(
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

        # Get timing windows
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)

        # 🔒 HARD MINOR TIMING OVERRIDE (FINAL AUTHORITY)
        if is_minor:
            has_timing = False

        # Get all data structures
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info = additional_data.get("lagna_info", {})
        career_matrix = additional_data.get("career_suitability_matrix", {})

        # Format unified verdict (CRITICAL - must be first)
        unified_verdict_block = self._format_unified_verdict(additional_data)

        # Format KP analysis
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)

        # Format timing windows (only for non-minors)
        timing_formatted = ""
        if not is_minor and has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        # Format other sections
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        matrix_formatted = self._format_career_matrix(career_matrix, is_minor)

        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline,is_minor)

        if is_minor:
            analysis_instructions = self._get_analysis_instructions(
                kp_available, "developmental", has_timing, dob=dob
            )
        elif has_timing:
            analysis_instructions = self._get_analysis_instructions(
                kp_available, "general", True
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
Domain: Career
Subtopic: Growth And Security
Sub-subdomain: Promotion / Career Growth Timing
Query Type: {'DEVELOPMENTAL' if is_minor else 'TIMING'}
{'(Foundation Phase - No promotion prediction)' if is_minor else '(When will promotion/advancement occur?)'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing and not is_minor else 'NO ❌ (Minor or not computed)'}
{'⚠️ MINOR DETECTED - DEVELOPMENTAL MODE ACTIVE' if is_minor else ''}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{timing_formatted}

{kp_formatted}

{matrix_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR PROMOTION TIMING:
• Check PROMISE STATUS from unified verdict first
• If 10th cusp = PROMISE:
  - Adult → Promotion manifestation possible during favorable periods
  - Minor → Career promise exists long-term; interpret dashas as preparation phases
• If 10th cusp = DENIAL → Obstacles likely, be realistic
• If 11th cusp = PROMISE → Gains/recognition will come
• {'⚠️ TIMING WINDOWS PROVIDED - MUST USE EXACT DATES!' if has_timing and not is_minor else ''}
• {'Mention BOTH best and nearest windows' if has_timing and not is_minor else ''}
• {'Let user choose: wait for best OR act sooner' if has_timing and not is_minor else ''}
• Align with unified verdict

{self.get_output_format(
    kp_available,
    False if is_minor else has_timing,
    "developmental" if is_minor else "timing"
)}
"""

    # ------------------------------------------------------------------
    # CAREER RISKS PROMPT (VEDIC ONLY - NO KP for risk analysis)
    # ------------------------------------------------------------------
    def _build_risks_prompt(
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

        # For risks, unified verdict still matters for context
        unified_verdict_block = self._format_unified_verdict(additional_data)

        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline,is_minor)

        if is_minor:
            developmental_override = f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob}
Age is under 18.

STRICT RULES:
• Do NOT describe career risks as immediate threats
• Do NOT predict job instability or loss
• Frame all challenges as learning experiences
• Focus on building resilience and skills

INTERPRETATION RULE:
Risks should be framed as:
→ Areas for skill development
→ Personality aspects to strengthen
→ Long-term challenges to prepare for
→ Character building opportunities

Tone:
• Developmental
• Encouraging
• Future-focused
"""
        else:
            developmental_override = ""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Growth And Security
Sub-subdomain: Career Risks / Stagnation (Vedic Analysis)
Query Type: NON_TIMING (Risk Assessment)
CURRENT DATE: {today}
Analysis Mode: VEDIC ONLY (Risks are Vedic-focused)
{'⚠️ MINOR DETECTED - DEVELOPMENTAL MODE ACTIVE' if is_minor else ''}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{developmental_override}

⚠️ CRITICAL SENSITIVITY RULES:
- NEVER induce fear about job loss or career failure
- Frame as "areas needing attention" not "permanent problems"
- All challenges are TRANSITIONAL, not permanent
- Emphasize adaptability and patience
- Focus on constructive solutions

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

**ANALYSIS APPROACH: VEDIC RISK ASSESSMENT (No KP needed here)**

1. **Check Unified Verdict** (for context):
   - What is the primary career path?
   - Any denial signals in promise status?

2. **Vedic Risk Analysis** (85% weight):
   - 8th and 12th house influences on career
   - Malefic aspects on 10th, 11th, 6th houses
   - Afflictions to career house lords
   - Saturn/Mars/Rahu challenges

3. **Dasha Context** (15% weight):
   - Current dasha creating temporary risks?
   - When does challenging period end?

OUTPUT FORMAT:

**GENERAL_ANSWER:**
<Constructive, non-fear-inducing answer about career challenges>
<Frame as opportunities for growth>

**ASTROLOGICAL_ANALYSIS:**

**A. CAREER RISK AREAS (VEDIC):**
- [From unified verdict promise/denial status]
- [From house lord analysis]

**B. CHALLENGES BY HOUSE:**
- 8th House Influence: [sudden changes, stagnation]
- 12th House Influence: [losses, transfers]
- Malefic Aspects: [on career houses]

**C. TEMPORAL NATURE:**
- Current challenging dasha: [if any]
- When relief expected: [from dasha timeline]

**D. PATH THROUGH CHALLENGES:**
- [Astrological factors supporting recovery]
- [What will help]

**SUMMARY:**
<Constructive outlook. TELL CLIENT: [Practical advice]>

**REMEDIES_ASTROLOGICAL:**
- [Target afflicting planets]

**REMEDIES_GENERAL:**
- [Practical career strategy steps]
"""

    # ------------------------------------------------------------------
    # CAREER STABILITY ADVICE PROMPT (LLM-Driven + Vedic)
    # ------------------------------------------------------------------
    def _build_stability_advice_prompt(
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

        # Unified verdict gives direction even for advice
        unified_verdict_block = self._format_unified_verdict(additional_data)

        # KP analysis for advice (career direction context)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)

        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline,is_minor)

        if is_minor:
            developmental_override = f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person DOB: {dob}
Age is under 18.

STRICT RULES:
• Do NOT recommend immediate career moves or job changes
• Do NOT suggest workplace strategy
• Focus on education, skill-building, and self-development

INTERPRETATION RULE:
If unified verdict = Service:
→ Interpret as FUTURE employment orientation
→ Focus on studies, competitive exams, skill-building
→ Career stability builds through academic excellence now

Tone:
• Developmental
• Preparation-focused
• Future-aligned
"""
        else:
            developmental_override = ""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Growth And Security
Sub-subdomain: Career Stability and Success Advice
Query Type: NON_TIMING (Practical Advice)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
{'⚠️ MINOR DETECTED - DEVELOPMENTAL MODE ACTIVE' if is_minor else ''}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{developmental_override}

NOTE: This is a PRACTICAL ADVICE question.

Your advice should STILL ALIGN with the unified career verdict:
• If verdict = Service → Stability through employment excellence
• If verdict = Business → Stability through enterprise building
• If verdict = Hybrid → Dual strategy possible

Focus areas:
• How to build career stability
• Long-term career sustainability
• Strategic decision-making
• Areas to strengthen vs leverage

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

**ANALYSIS APPROACH: PRACTICAL ADVICE + ASTROLOGICAL SUPPORT**

1. **Check Unified Verdict** (MANDATORY):
   - What is the primary career path?
   - Is career growth promised or denied?
   - What is the confidence level?

2. **Practical Career Advice** (60% weight):
   - Current situation assessment
   - Building stability in chosen path
   - Long-term sustainability strategies

3. **Astrological Support** (40% weight):
   - What do career houses suggest about stability?
   - Current dasha support for growth?
   - Long-term career potential from chart

OUTPUT FORMAT:

**GENERAL_ANSWER:**
<Clear advice aligned with unified verdict>
<What kind of career stability is indicated for this person>

**PRACTICAL_ANALYSIS:**
- Career path suitability: [from unified verdict]
- Stability factors: [assessment]
- Growth opportunities: [assessment]

**ASTROLOGICAL_SUPPORT:**
- Unified verdict: [path] → [how this informs stability]
- Career houses: [summary]
- Current dasha: [support level for stability]

**RECOMMENDATION:**
<Clear direction with reasoning, aligned to verdict>

**ACTION_STEPS:**
1. [First step for career stability]
2. [Second step]
3. [Third step]

**REMEDIES:**
<If applicable for strengthening career stability>
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
        is_minor = kwargs.get("is_minor", False)

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        lagna_info = additional_data.get("lagna_info", {})

        # Format unified verdict
        unified_verdict_block = self._format_unified_verdict(additional_data)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)

        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)

        current_dasha = kwargs.get("current_dasha")
        current_dasha_block = self._format_current_dasha(current_dasha)

        minor_note = ""
        if is_minor:
            minor_note = """
🚨 NOTE: Person is under 18.
• Frame remedies as foundation-building practices
• Emphasize discipline, study habits, character development
• Avoid remedies that imply immediate career triggers
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Growth And Security
Sub-subdomain: Career Growth Remedies
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
{'⚠️ MINOR DETECTED' if is_minor else ''}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{minor_note}

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
   - Strengthen current dasha lord for immediate support
   - Prepare for upcoming dasha lords (3 months before)

3. **Priority:**
   - Primary: Strengthen planets affecting career (10th, 11th house)
   - Secondary: Boost recognition and gains (11th house)
   - Tertiary: Address obstacles (8th, 12th connections)

CAREER GROWTH PLANET REMEDIES:
• SUN WEAK: Sunday worship, authority respect, leadership roles
• JUPITER WEAK: Thursday fasts, yellow items, expand knowledge
• SATURN: Saturday fasts, service to elderly, discipline
• MERCURY WEAK: Wednesday fasts, skill development, communication

OUTPUT FORMAT:

**WEAK AREAS IDENTIFIED:**
- [From KP promise/denial analysis]
- [From Vedic house lord analysis]

**REMEDIES_ASTROLOGICAL:**

**For [Planet] (affecting [house]):**
- Mantra: [specific mantra]
- Day: [best day for remedy]
- Charity: [specific charity]

**For Current Dasha Lord ([Planet]):**
- [Specific remedies]

**REMEDIES_GENERAL:**
- [Practical career growth steps]
- [Skill development aligned with chart]
- [Networking strategies for career advancement]

**TIMELINE:**
- Start remedies on: [auspicious day]
- Duration: [period]
"""

    # ------------------------------------------------------------------
    # GENERAL GROWTH PROMPT (Fallback)
    # ------------------------------------------------------------------
    def _build_general_growth_prompt(
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
        career_matrix = additional_data.get("career_suitability_matrix", {})

        # Format unified verdict
        unified_verdict_block = self._format_unified_verdict(additional_data)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)

        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        matrix_formatted = self._format_career_matrix(career_matrix, is_minor)

        current_dasha = kwargs.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline")

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline,is_minor)

        analysis_instructions = self._get_analysis_instructions(
            kp_available,
            "developmental" if is_minor else "general",
            False,
            dob=dob
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Career
Subtopic: Growth And Security
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
{'⚠️ MINOR DETECTED - DEVELOPMENTAL MODE ACTIVE' if is_minor else ''}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{unified_verdict_block}

{kp_formatted}

{matrix_formatted}

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
• Provide actionable guidance for career growth

{self.get_output_format(kp_available, False, "general")}
"""
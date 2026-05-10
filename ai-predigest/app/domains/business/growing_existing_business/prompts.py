"""
Growing Existing Business – LLM Prompts v9.0

CRITICAL FIXES FROM v8.0 (Aligned with CareerDiscoveryAndEmploymentPromptBuilder v10.0
and FacingChallengesInBusinessPromptBuilder v10.0):

✅ UNIFIED GROWTH VERDICT DISPLAY - _format_unified_verdict() → single source of truth
✅ PURE KP FORMATTING - CSL → Sub Lord → Star Lord → Significations → Promise/Denial
✅ CORRECT DATA KEYS - uses unified_growth_verdict + kp_business_growth_analysis (v5.0)
✅ MINOR DETECTION - _detect_minor() with multi-format DOB parsing
✅ MINOR PROTECTION - Age-based blocks per question type
✅ LANGUAGE HELPER - get_language_instruction() for Hindi/Hinglish/English
✅ WARM, ACTIONABLE TONE - TONE AND APPROACH section in system prompt
✅ HONEST VEDIC-KP AGREEMENT - AGREEMENT/PARTIAL/CONFLICT explicitly shown
✅ ANTI-HALLUCINATION STRENGTHENED - Explicit rules against inventing data
✅ CORRECT SUB_SUBDOMAIN ROUTING - Matches v5.0 evaluator sub-subdomains
✅ TIMING WINDOWS (BEST + NEAREST) - Minor-aware, blocked-aware
✅ CONSISTENT OUTPUT FORMAT - Same structure across all questions

Compatible with GrowingExistingBusinessEvaluator v5.0 data structures:
- unified_growth_verdict          (SINGLE SOURCE OF TRUTH)
- kp_business_growth_analysis     (CSL → Sub Lord chains)
- business_growth_suitability_matrix (8 growth options)
- business_growth_house_lords     (Vedic house lord data)
- business_growth_house_aspects   (Vedic aspects)
- business_growth_timing_windows  (BEST + NEAREST)
- business_growth_kp_analysis     (KP engine output)
- service_vs_business             (Service/Business determination)
- lagna_info                      (Ascendant)
- current_dasha / dasha_timeline  (Timing)

Covers:
1) Identifying Suitable Business / Growth Strategy → sub_subdomain="Identifying Suitable Business"
2) Loan Taking Decision + Timing                   → sub_subdomain="Loan Taking Decision"
3) Loan Repayment Decision + Timing                → sub_subdomain="Loan Repayment Decision"
4) Best Periods for Business Growth (TIMING)       → sub_subdomain="Best Periods for Business Growth"
5) Business Challenges                             → sub_subdomain="Business Challenges"
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
    InterpretationGoal,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DOMAIN_PREFIX = "business_growth"


class GrowingExistingBusinessPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Business → Growing Existing Business
    v9.0 — Unified verdict, pure KP methodology, minor-safe, language-correct.
    """

    domain = "Business"
    subtopic = "Growing Existing Business"

    BUSINESS_PROMISE_HOUSES = {2, 3, 7, 11}
    SUCCESS_HOUSES          = {2, 10, 11}
    GROWTH_HOUSES           = {3, 9, 11}
    OBSTACLE_HOUSES         = {6, 8, 12}

    # ══════════════════════════════════════════════════════════════
    # SYSTEM PROMPT
    # ══════════════════════════════════════════════════════════════

    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing ACTIONABLE business growth guidance.

════════════════════════════════════════════════════════════
TONE AND APPROACH (READ THIS FIRST)
════════════════════════════════════════════════════════════

Your role is to be a trusted advisor, not a cold analyst.

✅ BE WARM: Business growth is a personal journey. Acknowledge both excitement and anxiety.
✅ BE HONEST: If growth will be challenging, say so — but always with a path forward.
✅ BE ACTIONABLE: Every analysis must end with clear steps to take.
✅ BE ENCOURAGING: Growth takes time. Frame slower phases as preparation, not failure.
❌ NEVER induce fear about business failure or financial loss.
❌ NEVER give cold, clinical readings that leave the person directionless.
❌ NEVER leave the person without a next step to take.

════════════════════════════════════════════════════════════
AGE SAFETY RULE (MINOR PROTECTION)
════════════════════════════════════════════════════════════

If person is under 18 (minor flag active):
• NEVER recommend taking business loans or financial commitments
• NEVER advise business expansion decisions requiring legal capacity
• NEVER recommend shutting down or starting operations independently
• Frame analysis as educational: business cycle awareness, preparation
• Treat dashas as skill-building phases, not business-triggering events
• Recommend guardian involvement for financial decisions
• Tone: Educational, Encouraging, Developmental, Wisdom-building

════════════════════════════════════════════════════════════
CRITICAL KP RULES (MUST FOLLOW)
════════════════════════════════════════════════════════════

1. KP HIERARCHY:
   SUB LORD      → PROMISE/DENIAL (decides IF event happens — MOST IMPORTANT)
   STAR LORD     → RESULT TYPE (what kind of result)
   PLANET NATURE → FLAVOR ONLY (how it happens — NEVER overrides significations)

   ⚠️ SIGNIFICATIONS ALWAYS WIN OVER PLANET NATURE.
   • Venus (benefic) signifies 6, 8, 12 → RESULT IS OBSTACLES (not good!)
   • Saturn (malefic) signifies 2, 7, 11 → RESULT IS BUSINESS GROWTH (good!)

2. CORRECT KP CHAIN FORMAT:
   CSL [Planet] → in Nakshatra [Name] →
   Star Lord [Planet] → signifies houses [X,Y,Z] →
   Sub Lord [Planet] → signifies houses [A,B,C] →
   VERDICT: PROMISE/DENIAL based on SUB LORD significations

3. CORRECT HOUSE DEFINITIONS:
   BUSINESS PROMISE HOUSES: 2, 3, 7, 11
   SUCCESS HOUSES:          2, 10, 11
   GROWTH HOUSES:           3, 9, 11
   OBSTACLE HOUSES:         6, 8, 12

4. PROMISE/DENIAL LOGIC (SUB LORD DECIDES):
   FOR 7TH CUSP (Business/Partnership):
   • PROMISE: Sub-lord signifies 2, 3, 7, 11 (2+ houses)
   • DENIAL: Sub-lord signifies 8, 12 strongly
   FOR 11TH CUSP (Gains/Income):
   • PROMISE: Sub-lord signifies 2, 10, 11
   • DENIAL: Sub-lord signifies 8, 12 strongly
   FOR 3RD CUSP (Initiatives):
   • PROMISE: Sub-lord signifies 3, 9, 11

5. RAHU/KETU RULE:
   Nodes act through their STAR LORD.
   "Rahu is in [Nakshatra], star lord is [Planet], which signifies [houses]"
   NEVER judge Rahu/Ketu by just their house occupation.

════════════════════════════════════════════════════════════
UNIFIED GROWTH VERDICT RULE
════════════════════════════════════════════════════════════

The evaluator provides a UNIFIED_GROWTH_VERDICT.
This is the SINGLE SOURCE OF TRUTH for this person.

⚠️ ALL your answers MUST align with this verdict:
• STRONG_GROWTH → Confirm growth path, focus on timing and strategy
• MODERATE_GROWTH → Acknowledge potential with effort, be realistic
• GROWTH_CHALLENGES → Be honest about obstacles, offer path forward
• EXPANSION_FAVORABLE → Good for new markets/initiatives, not core only
• MIXED_SIGNALS → Acknowledge uncertainty, recommend phased approach

NEVER contradict the unified verdict across different questions.

════════════════════════════════════════════════════════════
ANTI-HALLUCINATION RULES
════════════════════════════════════════════════════════════

• Do NOT invent sub-lord significations not provided
• Do NOT guess promise/denial without actual data
• Do NOT contradict the unified verdict
• Do NOT mention aspects unless explicitly provided
• Do NOT invent specific timing dates not in the data
• If timing windows are provided, use ONLY those dates
• If data is missing → SAY SO CLEARLY, do not guess

════════════════════════════════════════════════════════════
TIMING RULES
════════════════════════════════════════════════════════════

When timing windows are provided:
1. ALWAYS mention BOTH windows:
   • BEST WINDOW (highest score)
   • NEAREST WINDOW (soonest favorable)
2. Explain WHY each is favorable based on dasha lords
3. Let USER choose:
   • Wait for best → optimal results
   • Act sooner → acceptable results, earlier
4. If BEST = NEAREST: "Ideal timing! Best alignment AND earliest opportunity!"

════════════════════════════════════════════════════════════
ANALYSIS WEIGHTING
════════════════════════════════════════════════════════════

KP Significations (Sub Lord analysis) → 60% (PRIMARY)
Vedic Structure (House lords, dignity) → 30% (SECONDARY)
Dasha/Other factors                   → 10%

KP conclusion ALWAYS leads the final recommendation.
Vedic explains ease/difficulty of achieving KP's promise.

════════════════════════════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════════════════════════════

Always convert astrology into DECISIONS:

❌ WRONG: "7th house is moderate, 11th house shows mixed signals"
✅ RIGHT: "Business growth is supported. Focus on partnership expansion now, expect income growth during [dasha period]."

Provide:
• Clear growth path recommendation (aligned with unified verdict)
• Specific timing guidance (if timing data available)
• Actionable steps (what to do now)
• Realistic expectations (based on promise/denial status)
"""

    # ══════════════════════════════════════════════════════════════
    # MINOR DETECTION
    # ══════════════════════════════════════════════════════════════

    def _detect_minor(self, dob: str, dasha_timeline: Dict) -> bool:
        """
        Detect if person is currently under 18.
        Based on CURRENT age, not future dasha age.
        Supports formats: '%d/%m/%Y' and '%Y-%m-%d'
        """
        if not dob:
            return False
        try:
            today = datetime.now()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    dob_dt = datetime.strptime(dob, fmt)
                    break
                except ValueError:
                    continue
            else:
                return False

            current_age = today.year - dob_dt.year - (
                (today.month, today.day) < (dob_dt.month, dob_dt.day)
            )
            return current_age < 18
        except Exception:
            return False

    def _calculate_age_on_date(self, dob_str: str, target_date_str: str) -> int:
        """Calculate age on a specific date."""
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                dob = datetime.strptime(dob_str, fmt)
                break
            except ValueError:
                continue
        else:
            return 0
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        return target.year - dob.year - (
            (target.month, target.day) < (dob.month, dob.day)
        )

    # ══════════════════════════════════════════════════════════════
    # LANGUAGE INSTRUCTION
    # ══════════════════════════════════════════════════════════════

    def get_language_instruction(self, language: str) -> str:
        """Get language instruction for LLM."""
        lang = language.lower() if language else "english"
        if lang == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, house numbers, KP terms).
Example: "आपके व्यापार की वृद्धि के लिए **7th house** का CSL **Jupiter** है।"
Example: "11वें भाव का Sub Lord **Saturn** है जो houses [2, 10, 11] को signify करता है।"
"""
        elif lang == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapke business growth ke liye 7th house ka CSL Jupiter hai."
Example: "11th house ka Sub Lord Saturn hai jo houses [2, 10, 11] signify karta hai."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear, warm English.
Keep technical terms clear and explain where needed.
"""

    # ══════════════════════════════════════════════════════════════
    # UNIFIED GROWTH VERDICT DISPLAY
    # ══════════════════════════════════════════════════════════════

    def _format_unified_verdict(self, additional_data: Dict) -> str:
        """
        Format the UNIFIED GROWTH VERDICT prominently.
        This ensures ALL questions use the SAME growth direction.
        Reads unified_growth_verdict from GrowingExistingBusinessEvaluator v5.0.
        """
        verdict = additional_data.get("unified_growth_verdict", {})

        if not verdict:
            return """
═══════════════════════════════════════════════════════════
⚠️ UNIFIED GROWTH VERDICT NOT AVAILABLE
═══════════════════════════════════════════════════════════

WARNING: No unified verdict provided by evaluator.
Cannot guarantee consistency across different questions.
Proceed with available data, but be cautious about
making definitive growth path recommendations.
═══════════════════════════════════════════════════════════
"""

        overall_outlook  = verdict.get("overall_outlook", "UNKNOWN")
        growth_viable    = verdict.get("growth_viable")
        confidence       = verdict.get("confidence", "Low")
        agreement        = verdict.get("agreement_status", "UNKNOWN")
        promise_status   = verdict.get("promise_status", {})
        growth_ranking   = verdict.get("growth_ranking", [])
        kp_reasoning     = verdict.get("kp_reasoning", "")
        vedic_reasoning  = verdict.get("vedic_reasoning", "")

        # Human-readable outlook
        outlook_labels = {
            "STRONG_GROWTH":           "STRONG GROWTH POTENTIAL 🚀",
            "MODERATE_GROWTH":         "MODERATE GROWTH ⚖️",
            "GROWTH_CHALLENGES":       "GROWTH CHALLENGES ⚠️",
            "EXPANSION_FAVORABLE":     "EXPANSION FAVORABLE 🌱",
            "OBSTACLES_BEFORE_GROWTH": "OBSTACLES BEFORE GROWTH ⚠️",
            "MIXED_SIGNALS":           "MIXED SIGNALS ○",
        }
        outlook_label = outlook_labels.get(overall_outlook, overall_outlook)

        viable_str = "YES" if growth_viable is True else "NO" if growth_viable is False else "CONDITIONAL"

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("🎯 UNIFIED GROWTH VERDICT (SINGLE SOURCE OF TRUTH)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ CRITICAL INSTRUCTION:")
        lines.append("Your answer MUST align with this verdict.")
        lines.append("Do NOT contradict this in any part of your response.")
        lines.append("")
        lines.append("╔══════════════════════════════════════════════════════╗")
        lines.append(f"║  BUSINESS GROWTH OUTLOOK: {outlook_label}")
        lines.append(f"║  Growth Viable: {viable_str}")
        lines.append(f"║  Confidence Level: {confidence}")
        lines.append("╚══════════════════════════════════════════════════════╝")
        lines.append("")

        # KP-Vedic Agreement
        lines.append("KP-VEDIC AGREEMENT STATUS:")
        if agreement == "AGREEMENT":
            lines.append("  ✅ AGREEMENT: Both KP and Vedic systems agree on growth direction.")
            lines.append("     → High confidence in recommendation")
        elif agreement == "PARTIAL":
            lines.append("  ⚠️ PARTIAL AGREEMENT: Systems show similar but not identical direction.")
            lines.append("     → KP result takes priority for events/timing")
            lines.append("     → Vedic shows some differences in capacity/ease")
        elif agreement == "CONFLICT":
            lines.append("  ❌ CONFLICT: KP and Vedic show different directions.")
            lines.append(f"     → KP indicates: {overall_outlook}")
            lines.append("     → Vedic may suggest otherwise")
            lines.append("     → Using KP for final verdict (events/timing)")
            lines.append("     → Vedic helps explain effort required")
        else:
            lines.append(f"  ○ {agreement}")
        lines.append("")

        # Promise status per house
        if promise_status:
            lines.append("PROMISE STATUS (From Sub-Lord Analysis):")
            lines.append("─" * 50)

            house_meanings = {
                7:  "Business/Partnership",
                10: "Career/Profession",
                11: "Gains/Income",
                3:  "Initiatives/Courage",
                9:  "Fortune/Foreign Expansion",
                6:  "Obstacles/Competition",
                8:  "Sudden Events",
            }

            status_markers = {
                "PROMISE":             "✅ PROMISE",
                "DENIAL":              "❌ DENIAL",
                "WEAK_PROMISE":        "⚠️ WEAK PROMISE",
                "NEUTRAL":             "○ NEUTRAL",
                "MANAGEABLE":          "⚖️ MANAGEABLE",
                "CHALLENGING":         "⚠️ CHALLENGING",
                "TRANSFORMATIVE":      "✅ TRANSFORMATIVE",
                "RISKY":               "❌ RISKY",
                "UNPREDICTABLE":       "○ UNPREDICTABLE",
                "INITIATIVE_POSITIVE": "✅ INITIATIVE POSITIVE",
                "INITIATIVE_BLOCKED":  "❌ INITIATIVE BLOCKED",
                "FORTUNE_POSITIVE":    "✅ FORTUNE POSITIVE",
            }

            for house_num in [7, 10, 11, 3, 9, 6, 8, 12]:
                if house_num not in promise_status:
                    continue
                status  = promise_status[house_num]
                meaning = house_meanings.get(house_num, f"House {house_num}")
                marker  = status_markers.get(status, f"○ {status}")

                lines.append(f"  {marker}")
                lines.append(f"  House {house_num} ({meaning})")

                if status == "PROMISE":
                    lines.append(f"     → This house matter WILL support growth")
                elif status == "DENIAL":
                    lines.append(f"     → Growth in this area faces core obstacles")
                elif status == "WEAK_PROMISE":
                    lines.append(f"     → May improve with effort and patience")
                elif status == "MANAGEABLE":
                    lines.append(f"     → Manageable with correct approach")
                lines.append("")

        # KP reasoning
        if kp_reasoning:
            lines.append("KP REASONING:")
            lines.append(f"  {kp_reasoning}")
            lines.append("")

        # Vedic reasoning
        if vedic_reasoning:
            lines.append("VEDIC REASONING:")
            lines.append(f"  {vedic_reasoning}")
            lines.append("")

        # Growth ranking
        if growth_ranking:
            lines.append("GROWTH PATH RANKING (Use this consistently):")
            lines.append("─" * 50)
            for i, option in enumerate(growth_ranking[:5], 1):
                lines.append(f"  {i}. {option}")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("YOUR RESPONSE MUST:")
        lines.append(f"  1. Reflect the '{overall_outlook}' outlook throughout")
        lines.append(f"  2. Show '{viable_str}' growth viability")
        lines.append(f"  3. Reflect **{confidence}** confidence level in tone")
        lines.append(f"  4. Show **{agreement}** status between KP and Vedic")
        lines.append("  5. NOT contradict this verdict anywhere in your response")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # KP ANALYSIS FORMATTER
    # ══════════════════════════════════════════════════════════════

    def _format_kp_analysis(
        self, technical_points: List[str], additional_data: Dict = None
    ) -> Tuple[str, bool]:
        """
        Format KP business growth analysis using PURE sub-lord methodology.
        Uses kp_business_growth_analysis from evaluator v5.0.
        Chain: CSL → Sub Lord → Star Lord → Significations → Promise/Denial
        """
        kp_structured = (additional_data or {}).get("kp_business_growth_analysis", {})

        if not kp_structured or not kp_structured.get("has_kp_data"):
            return "", False

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("⭐ KP SYSTEM ANALYSIS (Pure Sub-Lord Methodology)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("METHODOLOGY: CSL → Sub Lord → Star Lord → Significations → Promise/Denial")
        lines.append("")
        lines.append("⚠️ CRITICAL KP RULES:")
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

            # Priority order for growth: 7, 11, 3, 9, 10, 6, 8, then rest
            priority = [7, 11, 3, 9, 10, 6, 8, 2, 5, 12]
            ordered = [h for h in priority if h in csl_details] + \
                      [h for h in sorted(csl_details) if h not in priority]

            for house_num in ordered:
                if house_num not in csl_details:
                    continue

                info = csl_details[house_num]
                house_meaning   = info.get("house_meaning", "General")
                csl             = info.get("csl", "Unknown")
                csl_flavor      = info.get("csl_flavor", "")
                csl_house       = info.get("csl_house")
                nakshatra       = info.get("nakshatra", "")
                star_lord       = info.get("star_lord")
                star_sigs       = info.get("star_lord_signifies", [])
                sub_lord        = info.get("sub_lord")
                sub_sigs        = info.get("sub_lord_signifies", [])
                promise_status  = info.get("promise_status", "UNKNOWN")
                verdict         = info.get("verdict", "NEUTRAL")
                interpretation  = info.get("interpretation", "")

                promise_markers = {
                    "PROMISE":             "✅ PROMISE",
                    "DENIAL":              "❌ DENIAL",
                    "WEAK_PROMISE":        "⚠️ WEAK PROMISE",
                    "NEUTRAL":             "○ NEUTRAL",
                    "MANAGEABLE":          "⚖️ MANAGEABLE",
                    "CHALLENGING":         "⚠️ CHALLENGING",
                    "TRANSFORMATIVE":      "✅ TRANSFORMATIVE",
                    "RISKY":               "❌ RISKY",
                    "UNPREDICTABLE":       "○ UNPREDICTABLE",
                    "INITIATIVE_POSITIVE": "✅ INITIATIVE POSITIVE",
                    "INITIATIVE_BLOCKED":  "❌ INITIATIVE BLOCKED",
                    "FORTUNE_POSITIVE":    "✅ FORTUNE POSITIVE",
                }
                pm = promise_markers.get(promise_status, f"○ {promise_status}")

                lines.append("─" * 60)
                lines.append(f"HOUSE {house_num} ({house_meaning})")
                lines.append("─" * 60)
                lines.append("")
                lines.append(f"  CSL: {csl} ({csl_flavor} flavor)")
                if csl_house:
                    lines.append(f"  CSL placed in: House {csl_house}")
                if nakshatra:
                    lines.append(f"  CSL in Nakshatra: {nakshatra}")
                if star_lord:
                    lines.append(f"  Star Lord: {star_lord}")
                    if star_sigs:
                        lines.append(f"  Star Lord Signifies: Houses {star_sigs}")
                if sub_lord:
                    lines.append(f"  Sub Lord: {sub_lord} ← FINAL DECIDER")
                    if sub_sigs:
                        lines.append(f"  Sub Lord Signifies: Houses {sub_sigs}")
                        lines.append("")
                        sub_set = set(sub_sigs)
                        biz_conn = sub_set & self.BUSINESS_PROMISE_HOUSES
                        suc_conn = sub_set & self.SUCCESS_HOUSES
                        grw_conn = sub_set & self.GROWTH_HOUSES
                        obs_conn = sub_set & self.OBSTACLE_HOUSES
                        if biz_conn:
                            lines.append(f"  → Business Houses Connected: {sorted(biz_conn)}")
                        if suc_conn:
                            lines.append(f"  → Success Houses Connected: {sorted(suc_conn)}")
                        if grw_conn:
                            lines.append(f"  → Growth Houses Connected: {sorted(grw_conn)}")
                        if obs_conn:
                            lines.append(f"  ⚠️ Obstacle Houses Connected: {sorted(obs_conn)}")

                lines.append("")
                lines.append(f"  ╔═══════════════════════════════════════════════╗")
                lines.append(f"  ║  VERDICT: {pm}")
                lines.append(f"  ╚═══════════════════════════════════════════════╝")

                if interpretation:
                    lines.append("")
                    lines.append("  INTERPRETATION:")
                    words = interpretation.split()
                    current_line = "    "
                    for word in words:
                        if len(current_line) + len(word) > 70:
                            lines.append(current_line)
                            current_line = "    " + word
                        else:
                            current_line += (" " + word) if current_line.strip() else "    " + word
                    if current_line.strip():
                        lines.append(current_line)

                lines.append("")

        # Overall verdict
        overall = kp_structured.get("overall_verdict", "UNKNOWN")
        agreement = kp_structured.get("agreement_status", "UNKNOWN")

        lines.append("═══════════════════════════════════════════════════════════")
        lines.append(f"OVERALL KP GROWTH VERDICT: {overall}")
        lines.append(f"KP-VEDIC AGREEMENT: {agreement}")
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
        lines.append("  1. Quote the full chain: CSL → Sub Lord → Significations")
        lines.append("  2. Base verdict on SUB LORD significations, NOT planet nature")
        lines.append("  3. If benefic CSL has obstacle-house significations → DENIAL/CHALLENGING")
        lines.append("  4. If malefic CSL has business-house significations → PROMISE")
        lines.append("  5. Use exact houses from data — never guess")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines), True

    # ══════════════════════════════════════════════════════════════
    # GROWTH SUITABILITY MATRIX
    # ══════════════════════════════════════════════════════════════

    def _format_growth_matrix(self, matrix: Dict) -> str:
        """Format the 8-option business growth suitability matrix."""
        if not matrix:
            return ""

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("📊 BUSINESS GROWTH SUITABILITY MATRIX")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("Based on KP Sub-Lord Significations + Unified Verdict:")
        lines.append("")
        lines.append("| Growth Path | Rating | KP Reasoning |")
        lines.append("|-------------|--------|--------------|")

        for option, details in matrix.items():
            rating    = details.get("rating", "UNKNOWN")
            reasoning = details.get("kp_reasoning", "")
            if len(reasoning) > 55:
                reasoning = reasoning[:52] + "..."
            marker = "✅" if rating == "HIGH" else "⚖️" if rating == "MODERATE" else "❌" if rating == "AVOID" else "○"
            lines.append(f"| {marker} {option} | {rating} | {reasoning} |")

        lines.append("")
        lines.append("⚠️ Use this matrix CONSISTENTLY across all questions.")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # TIMING WINDOWS
    # ══════════════════════════════════════════════════════════════

    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """Format BEST and NEAREST timing windows for LLM."""
        if not timing_windows_data or not timing_windows_data.get("has_timing"):
            return ""
        try:
            best    = timing_windows_data.get("best_window")
            nearest = timing_windows_data.get("nearest_window")
            all_win = timing_windows_data.get("all_favorable", [])

            if not best and not nearest:
                return ""

            lines = []
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("⏰ TIMING WINDOWS ANALYSIS")
            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL: You MUST mention BOTH windows below.")
            lines.append("Let user choose based on their urgency and situation.")
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
                maha  = best.get("score_maha", 0)
                antar = best.get("score_antara", 0)
                prat  = best.get("score_paryantar", 0)
                if maha or antar or prat:
                    lines.append(f"  Maha Dasha score: {maha}/10")
                    lines.append(f"  Antara score: {antar}/10")
                    lines.append(f"  Pratyantar score: {prat}/10")
                transit = best.get("transit_score", 0)
                if transit:
                    lines.append(f"  Transit support: {transit:.1f}%")
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

                if best and (
                    best.get("dasha") == nearest.get("dasha") and
                    best.get("start") == nearest.get("start")
                ):
                    lines.append("")
                    lines.append("  🎯 IDEAL SITUATION!")
                    lines.append("  The BEST window IS the NEAREST favorable window!")
                    lines.append("  You get optimal timing AND early opportunity!")
                else:
                    lines.append("  Trade-off: Sooner but not absolute best alignment")
                lines.append("")

            if len(all_win) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS (Reference):")
                lines.append("-" * 50)
                for i, w in enumerate(all_win[:5], 1):
                    dasha = w.get("dasha", "N/A")
                    start = w.get("start", "N/A")
                    end   = w.get("end", "N/A")
                    score = w.get("final_score", 0)
                    is_b  = best and dasha == best.get("dasha") and start == best.get("start")
                    is_n  = nearest and dasha == nearest.get("dasha") and start == nearest.get("start")
                    icon  = "🏆" if is_b else "⏰" if is_n else "○"
                    lines.append(f"  {icon} {i}. {dasha}")
                    lines.append(f"     {start} to {end} (Score: {score:.1f})")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════")
            lines.append("YOUR RESPONSE MUST:")
            lines.append("  • Mention BOTH best and nearest windows with exact dates")
            lines.append("  • Explain WHY each is favorable for business growth")
            lines.append("  • Let user choose: Wait for best OR Act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # LAGNA LORD
    # ══════════════════════════════════════════════════════════════

    def _format_lagna_lord(
        self, lagna_info: Dict, house_lords_info: Dict = None
    ) -> str:
        """Format lagna lord for business personality analysis."""
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign":        info.get("house_sign", "N/A"),
                "lagna_lord":        info.get("lord", "N/A"),
                "lagna_lord_house":  info.get("lord_in_house"),
                "lagna_lord_sign":   info.get("lord_in_sign", "N/A"),
                "lagna_lord_degree": info.get("lord_degree", 0),
                "lagna_lord_dignity": info.get("lord_dignity", "Unknown"),
            }

        if not lagna_info:
            return """
═══════════════════════════════════════════════════════════
⚠️ LAGNA (ASCENDANT) INFORMATION NOT AVAILABLE
═══════════════════════════════════════════════════════════
Do NOT guess or invent lagna sign.
Skip lagna lord analysis completely.
═══════════════════════════════════════════════════════════
"""
        lord        = lagna_info.get("lagna_lord", "N/A")
        lagna_sign  = lagna_info.get("lagna_sign", "N/A")
        lord_house  = lagna_info.get("lagna_lord_house", "N/A")
        lord_sign   = lagna_info.get("lagna_lord_sign", "N/A")
        dignity     = lagna_info.get("lagna_lord_dignity", "Unknown")

        personality_map = {
            "Sun":     {"trait": "Leadership-oriented, authority-seeking",   "biz": "Government contracts, branded businesses, leadership roles"},
            "Moon":    {"trait": "People-oriented, emotionally intelligent",  "biz": "Hospitality, retail, consumer goods, care businesses"},
            "Mars":    {"trait": "Action-oriented, competitive, technical",   "biz": "Real estate, manufacturing, construction, technical services"},
            "Mercury": {"trait": "Analytical, communicative, versatile",      "biz": "Trading, IT, consulting, communication, logistics"},
            "Jupiter": {"trait": "Knowledge-seeker, advisory, expansive",     "biz": "Education, consulting, finance, international trade"},
            "Venus":   {"trait": "Creative, diplomatic, aesthetic",           "biz": "Luxury, beauty, arts, hospitality, fashion"},
            "Saturn":  {"trait": "Disciplined, patient, structured",          "biz": "Manufacturing, services, labour management, long-term assets"},
            "Rahu":    {"trait": "Unconventional, ambitious, innovative",     "biz": "Technology, foreign trade, digital businesses, new markets"},
            "Ketu":    {"trait": "Research-oriented, spiritual, independent", "biz": "Niche technical, research, spiritual products, healing"},
        }
        info = personality_map.get(lord, {"trait": "Unique approach", "biz": "Depends on placement"})

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("🎯 LAGNA (ASCENDANT) — BUSINESS PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign: {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        lines.append("")
        lines.append(f"Business Personality: {info['trait']}")
        lines.append(f"Suitable Business Sectors: {info['biz']}")
        lines.append("")
        lines.append("⚠️ NOTE: This is Lagna (Ascendant), NOT Moon sign.")
        lines.append("Use lagna lord to explain HOW person approaches business.")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # HOUSE LORDS
    # ══════════════════════════════════════════════════════════════

    def _format_house_lords(self, house_lords_info: Dict) -> str:
        """Format house lord information from evaluator."""
        if not house_lords_info:
            return ""

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("VEDIC HOUSE LORD ANALYSIS (Secondary to KP)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ NOTE: Vedic shows CAPACITY and EASE.")
        lines.append("   KP decides whether EVENT/GROWTH happens.")
        lines.append("")

        house_meanings = {
            1: "Self/Personality",
            2: "Wealth/Capital",
            3: "Initiatives/Efforts",
            5: "Creativity/Speculation",
            6: "Debts/Competition",
            7: "Business/Partnership",
            9: "Fortune/Expansion",
            10: "Career/Profession",
            11: "Gains/Income",
            12: "Expenses/Foreign",
        }
        growth_order = [7, 10, 11, 3, 9, 6, 8, 2, 5, 12, 1]

        for house_num in growth_order:
            if house_num not in house_lords_info:
                continue
            info    = house_lords_info[house_num]
            marker  = "⭐ PRIMARY" if info.get("priority") == "primary" else "○ SECONDARY"
            meaning = house_meanings.get(house_num, "General")

            lines.append(f"{marker} — HOUSE {house_num} ({meaning})")
            lines.append(f"  Sign: {info.get('house_sign', 'N/A')}")
            lord = info.get("lord")
            dignity = info.get("lord_dignity")
            strength = info.get("lord_strength_score")

            # Skip house if core structural data missing
            if not lord or lord == "Unknown":
                continue

            if not dignity or dignity == "Unknown":
                continue

            if strength is None:
                continue

            lines.append(f"  Lord: {lord}")
            lines.append(f"  Placed in: House {info.get('lord_in_house', 'N/A')}, {info.get('lord_in_sign', 'N/A')}")
            lines.append(f"  Dignity: {dignity}")
            lines.append(f"  Strength: {strength}/100")

            conds = []
            if info.get("lord_is_combust"):
                conds.append("⚠️ COMBUST")
            if info.get("lord_is_retrograde"):
                conds.append("🔄 RETROGRADE")
            if conds:
                lines.append(f"  Condition: {' | '.join(conds)}")
            if info.get("planets_in_house"):
                lines.append(f"  Planets in house: {', '.join(info['planets_in_house'])}")

            strength = info["lord_strength_score"]
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG — supports this growth area")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE — mixed results")
            else:
                lines.append("  ⚠️ Assessment: WEAK — challenges in this area")

            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # HOUSE ASPECTS
    # ══════════════════════════════════════════════════════════════

    def _format_house_aspects(self, aspects_info: Dict) -> str:
        """Format aspects data for LLM."""
        if not aspects_info:
            return ""

        has_aspects = any(
            aspects_info.get(h, {}).get("benefic_aspects") or
            aspects_info.get(h, {}).get("malefic_aspects")
            for h in [7, 10, 11, 3, 9, 6]
        )
        if not has_aspects:
            return ""

        lines = []
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("PLANETARY ASPECTS ON BUSINESS GROWTH HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        for house_num in [7, 10, 11, 3, 9, 6, 8, 2]:
            if house_num not in aspects_info:
                continue
            aspects  = aspects_info[house_num]
            benefic  = aspects.get("benefic_aspects", [])
            malefic  = aspects.get("malefic_aspects", [])
            if not benefic and not malefic:
                continue

            lines.append(f"• House {house_num}:")
            if benefic:
                lines.append(f"  ✅ Benefic aspects: {', '.join(benefic)}")
            if malefic:
                lines.append(f"  ⚠️ Malefic aspects: {', '.join(malefic)}")
            if len(benefic) > len(malefic):
                lines.append("  → Net: POSITIVE influence on growth")
            elif len(malefic) > len(benefic):
                lines.append("  → Net: CHALLENGING influence")
            else:
                lines.append("  → Net: BALANCED influence")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════
    # DASHA FORMATTERS
    # ══════════════════════════════════════════════════════════════

    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """Format current dasha information."""
        if not current_dasha:
            return ""
        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end   = date_range.get("end", "Unknown")

            mapping = {
                "Sa": "Saturn", "Su": "Sun",   "Mo": "Moon",
                "Ma": "Mars",   "Me": "Mercury","Ju": "Jupiter",
                "Ve": "Venus",  "Ra": "Rahu",   "Ke": "Ketu",
            }
            for sep in ["-", ">", "/"]:
                parts = dasha_name.split(sep)
                if len(parts) >= 2:
                    break
            else:
                parts = [dasha_name]
            full = " > ".join(mapping.get(p.strip(), p.strip()) for p in parts if p.strip())

            return "\n".join([
                "═══════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS — DON'T INVENT)",
                "═══════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {full}",
                f"Period: {start} to {end}",
                "",
                "⚠️ Use for analyzing PRESENT business circumstances.",
                "For FUTURE planning, see UPCOMING DASHA PERIODS below.",
                "Do NOT invent different dasha periods.",
                "═══════════════════════════════════════════════════════",
            ])
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        """Format comprehensive dasha timeline (2Y past → 10Y future)."""
        if not dasha_timeline:
            return ""
        try:
            current = dasha_timeline.get("current", [])
            future  = dasha_timeline.get("next_10_years", [])
            if not any([current, future]):
                return ""

            mapping = {
                "Sa": "Saturn", "Su": "Sun",   "Mo": "Moon",
                "Ma": "Mars",   "Me": "Mercury","Ju": "Jupiter",
                "Ve": "Venus",  "Ra": "Rahu",   "Ke": "Ketu",
            }

            def parse(name):
                for sep in ["-", ">", "/"]:
                    parts = name.split(sep)
                    if len(parts) >= 2:
                        return " > ".join(mapping.get(p.strip(), p.strip()) for p in parts if p.strip())
                return name

            lines = []
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("DASHA TIMELINE (For Business Growth Planning)")
            lines.append("═══════════════════════════════════════════════════════")
            lines.append("")

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    dr = d.get("date_range", {})
                    lines.append(f"  • {parse(d.get('dasha_name', ''))}")
                    lines.append(f"    {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            if future:
                lines.append("⏭️  UPCOMING (Next 10 Years — For Growth Planning):")
                lines.append("-" * 50)
                for i, d in enumerate(future[:15], 1):
                    dr     = d.get("date_range", {})
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parse(d.get('dasha_name', ''))}")
                    lines.append(f"     {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════")
            lines.append("BUSINESS GROWTH DASHA GUIDELINES:")
            lines.append("• Jupiter/Venus → Expansion, prosperity, new opportunities")
            lines.append("• Mercury → Trade, networking, diversification")
            lines.append("• Sun → Authority, branding, leadership growth")
            lines.append("• Saturn → Slow, steady, structural growth — discipline needed")
            lines.append("• Rahu → Unconventional growth, foreign/digital markets")
            lines.append("• Mars → Action, bold moves, technical ventures")
            lines.append("═══════════════════════════════════════════════════════")

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ══════════════════════════════════════════════════════════════
    # ANALYSIS INSTRUCTIONS
    # ══════════════════════════════════════════════════════════════

    def _get_analysis_instructions(
        self,
        kp_available: bool,
        question_type: str = "general",
        has_timing: bool = False,
        dob: str = None,
        is_minor: bool = False,
    ) -> str:
        """Generate analysis instructions based on data availability and minor status."""

        base = """
**ANALYSIS APPROACH (FOLLOW THIS ORDER):**

**STEP 1: CHECK UNIFIED GROWTH VERDICT (MANDATORY)**
Read the UNIFIED_GROWTH_VERDICT section first.
Your ENTIRE response must align with this verdict.
Note:
• Overall outlook (STRONG_GROWTH / MODERATE_GROWTH / etc.)
• Growth viable flag
• Confidence level
• Promise status for each key house
• KP-Vedic agreement status
"""

        if kp_available:
            base += """
**STEP 2: KP ANALYSIS (Primary — 60% weight)**

For each key cusp (7th, 11th, 3rd, 9th, 10th), explain:
• CSL → Sub Lord → Significations
• Which houses does sub-lord signify?
• Is it PROMISE or DENIAL based on those houses?
• Do NOT use fraction scoring (3/5, 2/4)

Remember: SUB LORD significations decide, NOT planet nature.

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
• Growth house analysis (7, 10, 11, 3, 9)
"""

        if has_timing and not is_minor:
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

        # Minor-specific overrides
        if is_minor:
            minor_type_blocks = {
                "minor_loan": f"""
🚨 MINOR PROTECTION MODE ACTIVE (Person under 18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ABSOLUTE RULES:
• Do NOT recommend taking any loan
• Do NOT present timing windows for loan decisions
• Do NOT advise any financial commitments requiring legal capacity
• Frame response as EDUCATIONAL: what to learn about loan and growth cycles
• Suggest guardians/family handle financial decisions
• Tone: Educational, Protective, Future-oriented, Wisdom-building

DOB provided: {dob or 'N/A'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
                "minor_timing": f"""
🚨 MINOR DEVELOPMENTAL MODE ACTIVE (Person under 18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ABSOLUTE RULES:
• Do NOT present timing windows as business-action triggers
• Do NOT predict specific business milestones
• Interpret dasha periods as preparation and skill-building phases
• Frame growth potential as long-term foundation building
• Tone: Educational, Encouraging, Developmental

DOB provided: {dob or 'N/A'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
                "minor_general": f"""
🚨 MINOR EDUCATIONAL MODE ACTIVE (Person under 18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRICT RULES:
• Do NOT advise business decisions requiring legal/financial capacity
• Do NOT recommend taking on business partners contractually
• Do NOT recommend expansion or contraction requiring capital
• Frame challenges as LEARNING MOMENTS about business cycles
• Focus on: Business awareness, future entrepreneurship preparation,
  family business support roles, skills to develop
• Tone: Educational, Encouraging, Developmental, Wisdom-building

DOB provided: {dob or 'N/A'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            }
            minor_block = minor_type_blocks.get(question_type, minor_type_blocks["minor_general"])
            base += minor_block

        return base

    # ══════════════════════════════════════════════════════════════
    # OUTPUT FORMAT
    # ══════════════════════════════════════════════════════════════

    def get_output_format(
        self,
        kp_available: bool = True,
        has_timing: bool = False,
        question_type: str = "general",
        is_minor: bool = False,
    ) -> str:
        """Generate output format based on KP availability, timing, minor status."""

        timing_section = ""
        if has_timing and not is_minor:
            timing_section = """
**F. TIMING RECOMMENDATION:**

⚠️ MANDATORY: Include BOTH timing options.

**🏆 BEST WINDOW (Highest Score):**
- Period: [exact dates from data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain dasha lords + growth significations]
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
        elif is_minor and has_timing:
            timing_section = """
**F. DEVELOPMENTAL TIMING NOTE:**
Timing windows are available but not actionable for decisions requiring legal capacity.
Instead, note which dasha periods show INCREASED BUSINESS AWARENESS AND PREPARATION POTENTIAL.
"""

        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT — FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, warm, actionable answer in simple terms. NO jargon.>
<MUST align with unified growth verdict.>
<Acknowledge the excitement or anxiety around growth.>
<Example: "आपके व्यापार में strong growth potential है। 7th house KP analysis shows business expansion is PROMISED, particularly through partnerships.">

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Growth Outlook: [from unified verdict]
- Growth Viable: [YES/NO/CONDITIONAL]
- Confidence: [from unified verdict]
- Promise Status: [7th: X, 11th: Y, 3rd: Z]
- KP-Vedic Agreement: [AGREEMENT/PARTIAL/CONFLICT]

**B. KP SYSTEM ANALYSIS (Primary — 60% weight):**

For EACH growth cusp (7th, 11th, 3rd, 9th):

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor — NOT the verdict!)
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Business Houses Connected: [list] (from 2, 3, 7, 11)
- Success Houses Connected: [list] (from 2, 10, 11)
- Obstacle Houses Connected: [list] (from 6, 8, 12)
- **VERDICT: PROMISE/DENIAL** based on sub-lord significations
- Why: [Explain how significations lead to verdict]

⚠️ Sub-lord significations decide, NOT planet nature

**C. VEDIC ANALYSIS (Secondary — 30% weight):**

**House Lords:**
- 7th Lord: [Planet, placement, dignity, strength]
- 11th Lord: [Planet, placement, dignity, strength]
- 3rd Lord: [Planet, placement, dignity, strength]
- 9th Lord: [Planet, placement, dignity, strength]

**Vedic-KP Agreement Check:**
- If agree: "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic [Y]. KP priority."
- If conflict: "❌ CONFLICT: KP [X], Vedic [Y]. Using KP for events."

**D. LAGNA LORD (Business Personality):**
- [Planet] as lagna lord
- Business approach: [description]

**E. GROWTH PATH MATRIX:**

| Growth Option | Rating | Reasoning |
|---------------|--------|-----------|
| [Option] | HIGH/MODERATE/LOW | [from KP] |

{timing_section}

**G. DASHA CONTEXT:**
- Current: [dasha] — [business growth impact]
- Upcoming favorable: [dasha + dates]

**SUMMARY:**
<2-3 sentences. MUST align with unified verdict.>
<End with one clear, actionable step the person can take today.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial]

**REMEDIES_GENERAL:**
- [Practical business growth steps]
"""
        else:
            return f"""
OUTPUT FORMAT (VEDIC ONLY):

**GENERAL_ANSWER:**
<Clear, warm, actionable answer in simple terms.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD (Business Personality):**
- Planet: [Name]
- Placed in: House [N]
- Business approach: [description]

**B. HOUSE LORD ANALYSIS (Primary):**

For each growth house (7, 10, 11, 3, 9):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Growth Impact: [explanation]

**C. GROWTH PATH ASSESSMENT:**

| Path | Suitability | Reasoning |
|------|-------------|-----------|
| [Option] | HIGH/MODERATE/LOW | [based on house analysis] |

{timing_section}

**D. DASHA CONTEXT:**
- Current: [dasha]
- Growth impact: [explanation]

**SUMMARY:**
<Concise growth outlook. End with one actionable step.>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical steps]
"""

    # ══════════════════════════════════════════════════════════════
    # ROUTER
    # ══════════════════════════════════════════════════════════════

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
        logger.warning("🔥 GrowingExistingBusiness PROMPT BUILDER v9.0 EXECUTED")

        # ─── GLOBAL MINOR DETECTION ──────────────────────────────
        dob           = kwargs.get("dob")
        dasha_timeline = kwargs.get("dasha_timeline")
        is_minor      = self._detect_minor(dob, dasha_timeline)
        kwargs["is_minor"] = is_minor
        logger.warning(
            f"[GROWING_BUSINESS] Minor Detection → DOB: {dob}, Is Minor: {is_minor}"
        )

        # ─── ROUTE ───────────────────────────────────────────────
        if "Identifying Suitable" in sub_subdomain or "Suitability" in sub_subdomain:
            return self._build_suitability_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Loan Taking" in sub_subdomain:
            return self._build_loan_taking_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Loan Repayment" in sub_subdomain:
            return self._build_loan_repayment_prompt(
                question, technical_points, meta, language, **kwargs)
        elif ("Best Periods" in sub_subdomain or ("Growth" in sub_subdomain and "Challenge" not in sub_subdomain)):
            return self._build_best_periods_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Challenge" in sub_subdomain:
            return self._build_challenges_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_prompt(
                question, technical_points, meta, language, **kwargs)

    # ══════════════════════════════════════════════════════════════
    # QUESTION 1 — IDENTIFYING SUITABLE BUSINESS / GROWTH STRATEGY
    # ══════════════════════════════════════════════════════════════

    def _build_suitability_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today              = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data    = kwargs.get("additional_data", {})
        is_minor           = kwargs.get("is_minor", False)
        dob                = kwargs.get("dob")

        house_lords    = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects  = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info     = additional_data.get("lagna_info", {})
        growth_matrix  = additional_data.get("business_growth_suitability_matrix", {})
        svb_data       = additional_data.get("service_vs_business", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        matrix_formatted  = self._format_growth_matrix(growth_matrix)

        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        minor_note = ""
        if is_minor:
            minor_note = f"""
🚨 MINOR EDUCATIONAL MODE ACTIVE
Person is under 18. DOB: {dob or 'N/A'}
Frame all growth potential as FUTURE DIRECTION, not immediate action.
Do NOT recommend operational expansion or financial commitments.
Tone: Educational, Encouraging, Developmental.
"""

        # KP engine summary (partners_needed, foreign_link, sectors)
        kp_engine = additional_data.get(f"{DOMAIN_PREFIX}_kp_analysis", {})
        kp_engine_block = ""
        if kp_engine:
            sectors = kp_engine.get("final_professions", [])
            partners = kp_engine.get("partners_needed")
            foreign = kp_engine.get("foreign_link", "")
            svb_path = svb_data.get("final_path", "")
            kp_engine_block = f"""
═══════════════════════════════════════════════════════════
KP BUSINESS ENGINE SUMMARY
═══════════════════════════════════════════════════════════
Business Strength: {kp_engine.get('business_strength_summary', 'N/A')}
KP Confidence: {kp_engine.get('confidence', 'N/A')}
Suitable Sectors: {', '.join(sectors[:5]) if sectors else 'N/A'}
Partnership Needed: {partners}
Foreign/New Market Link: {foreign}
Service vs Business: {svb_path}
═══════════════════════════════════════════════════════════
NOTE: Use ONLY these sectors for growth/diversification recommendations.
"""

        analysis_instructions = self._get_analysis_instructions(
            kp_available, "minor_general" if is_minor else "general", False,
            dob=dob, is_minor=is_minor
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Sub-subdomain: Identifying Suitable Business / Growth Strategy
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor Mode: {'YES 🚨' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_note}

{unified_verdict_block}

{kp_formatted}

{kp_engine_block}

{matrix_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR GROWTH STRATEGY:
• Confirm whether current business is aligned with KP promise status
• Growth sectors MUST come from KP engine data — do NOT invent sectors
• Foreign/international potential: ONLY if KP shows foreign link
• Partnership potential: aligned with 7th house promise status
• Diversification: based on 3rd/9th house status
• Align ALL recommendations with unified growth verdict

{self.get_output_format(kp_available, False, "general", is_minor)}
"""

    # ══════════════════════════════════════════════════════════════
    # QUESTION 2A — LOAN TAKING DECISION
    # ══════════════════════════════════════════════════════════════

    def _build_loan_taking_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today              = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data    = kwargs.get("additional_data", {})
        is_minor           = kwargs.get("is_minor", False)
        dob                = kwargs.get("dob")

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing          = timing_windows_data.get("has_timing", False) and not is_minor

        house_lords     = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects   = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info      = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        timing_formatted  = self._format_timing_windows(timing_windows_data) if has_timing else ""
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block      = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        # Loan-specific KP data
        loan_supported = additional_data.get("loan_supported", False)
        loan_planets   = additional_data.get("loan_planets", [])
        unified        = additional_data.get("unified_growth_verdict", {})
        overall_outlook = unified.get("overall_outlook", "")

        loan_block = ""

        if loan_supported and loan_planets:
            loan_block = f"KP Loan Indicators ACTIVE through: {', '.join(loan_planets[:3])}"
        elif not loan_supported:
            loan_block = "KP Loan Indicators: WEAK — borrowing carries elevated risk now"

        # Tone alignment with unified verdict
        if overall_outlook in ["GROWTH_CHALLENGES", "OBSTACLES_BEFORE_GROWTH"]:
            loan_block += "\n⚠️ Unified verdict indicates growth pressure. Borrow conservatively."
        elif overall_outlook == "MIXED_SIGNALS":
            loan_block += "\n⚠️ Growth direction mixed. Loan only if strong repayment buffer exists."


        # Hard block for minors
        if is_minor:
            minor_loan_block = f"""
╔══════════════════════════════════════════════════════════════╗
║  🚨 MINOR PROTECTION — ABSOLUTE LOAN BLOCK ACTIVE 🚨        ║
╚══════════════════════════════════════════════════════════════╝
Person is under 18. DOB: {dob or 'N/A'}

ABSOLUTE RULES:
• Do NOT recommend taking any loan
• Do NOT present timing windows for loan decisions
• Do NOT advise any financial commitments
• Frame response as EDUCATIONAL only
• Suggest guardians/family handle all financial decisions

INSTEAD, explain:
• What the chart shows about long-term financial capacity
• What business strengths to build before future loan decisions
• How dasha periods indicate future financial readiness (not now)
"""
        else:
            minor_loan_block = ""

        question_type = "minor_loan" if is_minor else ("timing" if has_timing else "general")
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing, dob=dob, is_minor=is_minor
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Sub-subdomain: Loan Taking Decision
Query Type: TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
Minor Mode: {'YES 🚨 — LOAN BLOCKED' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_loan_block}

{unified_verdict_block}

{timing_formatted}

{kp_formatted}

{loan_block}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

LOAN-FOR-GROWTH CONTEXT:
• This is a GROWTH loan, not distress borrowing
• 6th house = capacity to take loans for expansion
• 11th house = gains to service/repay loan
• 7th house = business strength to utilise loan
• KP promise on 11th = growth will convert to income (repayment viable)

{'⚠️ TIMING WINDOWS PROVIDED — MUST USE EXACT DATES!' if has_timing else ''}
{'Mention BOTH best and nearest windows' if has_timing else ''}

{self.get_output_format(kp_available, has_timing, question_type, is_minor)}
"""

    # ══════════════════════════════════════════════════════════════
    # QUESTION 2B — LOAN REPAYMENT DECISION
    # ══════════════════════════════════════════════════════════════

    def _build_loan_repayment_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today              = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data    = kwargs.get("additional_data", {})
        is_minor           = kwargs.get("is_minor", False)
        dob                = kwargs.get("dob")

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing          = timing_windows_data.get("has_timing", False) and not is_minor

        house_lords     = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects   = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info      = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        timing_formatted  = self._format_timing_windows(timing_windows_data) if has_timing else ""
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block      = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        repayment_supported = additional_data.get("repayment_supported", False)
        repayment_planets   = additional_data.get("repayment_planets", [])
        repayment_block = ""
        if repayment_supported and repayment_planets:
            repayment_block = f"KP Repayment Indicators ACTIVE through: {', '.join(repayment_planets[:3])}"
        elif not repayment_supported:
            repayment_block = "KP Repayment Visibility: LIMITED — conservative approach advised"

        if is_minor:
            minor_repay_block = f"""
╔══════════════════════════════════════════════════════════════╗
║  🚨 MINOR PROTECTION — LOAN/REPAYMENT BLOCK ACTIVE 🚨       ║
╚══════════════════════════════════════════════════════════════╝
Person is under 18. DOB: {dob or 'N/A'}
Do NOT advise loan or repayment decisions requiring legal capacity.
Frame as educational: how to understand cash flow and debt cycles.
"""
        else:
            minor_repay_block = ""

        question_type = "minor_loan" if is_minor else ("timing" if has_timing else "general")
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing, dob=dob, is_minor=is_minor
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Sub-subdomain: Loan Repayment Decision
Query Type: TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
Minor Mode: {'YES 🚨' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_repay_block}

{unified_verdict_block}

{timing_formatted}

{kp_formatted}

{repayment_block}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

REPAYMENT CONTEXT:
• 11th house (gains): Primary income for repayment
• 2nd house (wealth): Capital accumulation for repayment
• 10th house (profession): Sustained income stream
• KP promise on 11th = income growth supports repayment timeline

{self.get_output_format(kp_available, has_timing, question_type, is_minor)}
"""

    # ══════════════════════════════════════════════════════════════
    # QUESTION 3 — BEST PERIODS FOR BUSINESS GROWTH (TIMING)
    # ══════════════════════════════════════════════════════════════

    def _build_best_periods_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:
        """
        Question 3 — Best Periods for Business Growth (TIMING question).

        Three operating modes:
        1. MINOR (is_minor=True)          → Developmental interpretation, NO timing actions
        2. TIMING (has_timing=True)        → Structured windows, BEST + NEAREST mandatory
        3. TIMING FALLBACK (no windows)    → Dasha-based guidance, probabilistic language only

        Aligned with CareerDiscoveryAndEmploymentPromptBuilder v10.0 pattern.
        """

        today               = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data     = kwargs.get("additional_data", {})
        is_minor            = kwargs.get("is_minor", False)
        dob                 = kwargs.get("dob")

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        # Timing windows are suppressed entirely for minors
        has_timing          = timing_windows_data.get("has_timing", False) and not is_minor

        house_lords     = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects   = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info      = additional_data.get("lagna_info", {})

        # ── Formatted data blocks ─────────────────────────────────────
        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        timing_formatted  = self._format_timing_windows(timing_windows_data) if has_timing else ""
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block      = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        # ── KP growth-supporting planets (supplementary data) ─────────
        growth_planets = additional_data.get("growth_planets", [])
        growth_planet_block = ""
        if growth_planets:
            growth_planet_block = "\n".join([
                "═══════════════════════════════════════════════════════════",
                "KP GROWTH-SUPPORTING PLANETS",
                "═══════════════════════════════════════════════════════════",
                f"Key planets signifying growth houses (3, 7, 9, 11):",
                f"  {', '.join(growth_planets[:4])}",
                "Use these planets when explaining WHY a dasha period supports growth.",
                "═══════════════════════════════════════════════════════════",
            ])

        # ── Determine operating mode ───────────────────────────────────
        if is_minor:
            question_type = "minor_timing"
        elif has_timing:
            question_type = "timing_structured"
        else:
            question_type = "timing_fallback"

        # ── Minor protection block (placed immediately after question) ─
        if is_minor:
            minor_block = f"""
╔══════════════════════════════════════════════════════════════════╗
║  🚨 MINOR DEVELOPMENTAL MODE — TIMING INTERPRETATION 🚨         ║
╚══════════════════════════════════════════════════════════════════╝
Person is under 18. DOB: {dob or 'N/A'}

ABSOLUTE RULES FOR THIS RESPONSE:
• Do NOT present timing windows as business-action triggers
• Do NOT use phrases like "business will expand in [year]"
• Do NOT predict specific business milestones or dates
• Do NOT recommend operational expansion decisions

INSTEAD — interpret dasha periods as PREPARATION PHASES:
  → Which period strengthens business awareness?
  → Which period builds financial literacy?
  → Which period develops entrepreneurial thinking?
  → Which period prepares leadership readiness?

Tone: Educational, Future-building, Encouraging, Developmental
╚══════════════════════════════════════════════════════════════════╝
"""
        else:
            minor_block = ""

        # ── Analysis instructions (mode-aware) ────────────────────────
        analysis_instructions = self._get_analysis_instructions(
            kp_available,
            question_type,
            has_timing,
            dob=dob,
            is_minor=is_minor,
        )

        # ── Output format (mode-aware) ────────────────────────────────
        if is_minor:
            output_format = self._get_minor_timing_output_format(kp_available)
        elif has_timing:
            output_format = self.get_output_format(kp_available, True, question_type, False)
        else:
            output_format = self._get_timing_fallback_output_format(kp_available)

        # ── Timing-mode-specific guideline lines ──────────────────────
        if is_minor:
            timing_guidelines = """
• Timing windows are NOT shown — person is under 18
• Interpret ALL dasha periods as skill/preparation cycles
• Frame long-term growth potential as something to work toward
• Suggest guardian consultation for future business decisions
• Never predict a specific year for business events"""
        elif has_timing:
            timing_guidelines = """
• ⚠️ TIMING WINDOWS PROVIDED — MUST USE EXACT DATES FROM DATA
• MUST mention BOTH: Best Window AND Nearest Window
• Explain WHY each window supports business growth (dasha lords)
• Let user choose: Wait for best → optimal | Act sooner → acceptable
• If Best = Nearest → Emphasize: "Ideal! Best AND earliest!"
• Check promise status: 7th + 11th both PROMISE → strong windows exist
• Align all timing guidance with unified growth verdict"""
        else:
            timing_guidelines = """
• No computed timing windows available for this chart
• Use DASHA TIMELINE to discuss growth periods comparatively
• FORBIDDEN PHRASES (never say these):
    ❌ "You will see growth in [year]"
    ❌ "Business will expand by [date]"
    ❌ "Growth is guaranteed during..."
• ALLOWED LANGUAGE (use these instead):
    ✅ "This period supports preparation for growth..."
    ✅ "Alignment strengthens during..."
    ✅ "Higher potential may develop during..."
    ✅ "This dasha can enhance business readiness..."
• Discuss which upcoming dashas look comparatively stronger
• Recommend consulting for detailed timing computation"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Sub-subdomain: Best Periods for Business Growth
Query Type: TIMING
CURRENT DATE: {today}
Operating Mode: {'MINOR — DEVELOPMENTAL' if is_minor else 'TIMING STRUCTURED' if has_timing else 'TIMING FALLBACK (no computed windows)'}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌ (use dasha timeline)'}
Minor Protection: {'ACTIVE 🚨' if is_minor else 'NOT ACTIVE'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{unified_verdict_block}

{timing_formatted}

{kp_formatted}

{growth_planet_block}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR BEST GROWTH PERIODS:
{timing_guidelines}

• Check promise status FIRST (from unified verdict):
  - 7th PROMISE + 11th PROMISE → Strong growth timing likely exists
  - Only one PROMISE → Growth possible but one-sided improvement
  - Both DENIAL → Periods of effort, not breakthrough timing
  - WEAK_PROMISE → Gradual improvement, not sudden expansion
• Align ALL timing/period guidance with unified growth verdict
• Reference KP growth-supporting planets when explaining dasha strength

{output_format}
"""

    def _get_minor_timing_output_format(self, kp_available: bool) -> str:
        """
        Output format for MINOR mode on timing questions.
        No timing windows shown. Frames dashas as developmental phases.
        """
        kp_note = """
**B. KP PROMISE STATUS (Educational context only):**
- Explain what the chart shows about long-term growth direction
- Do NOT frame as triggering business events
- Use: "Your chart suggests a natural inclination toward [growth area]"
""" if kp_available else ""

        return f"""
OUTPUT FORMAT — MINOR DEVELOPMENTAL MODE (STRICT):

**GENERAL_ANSWER:**
<Warm, educational answer about long-term business potential.>
<Frame as: "Your chart shows strong foundations for future business growth.">
<No specific dates. No action triggers. No operational decisions.>

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Growth Direction: [from unified verdict — presented as long-term potential]
- Confidence: [from unified verdict]
- Note: "These patterns represent long-term direction, not immediate action triggers."

{kp_note}

**C. DASHA PHASES AS PREPARATION CYCLES:**

For each upcoming dasha period (use timeline data):
- Period: [Dasha name] ([start] to [end])
- Developmental Theme: [What skills/awareness this period builds]
  Examples:
  → "This period strengthens financial discipline and planning skills"
  → "Business awareness and analytical thinking develop strongly here"
  → "Leadership readiness and entrepreneurial thinking sharpen during this phase"
- What to focus on: [Educational or preparation activity]

⚠️ DO NOT say "business will grow" or "expansion will happen" — say "preparation strengthens"

**D. LAGNA LORD (Business Personality Foundation):**
- [Planet] — how this shapes future entrepreneurial approach
- Skills to develop now that will serve future business leadership

**SUMMARY:**
<Encouraging message about the strong foundation being built.>
<End with: one skill or area of knowledge to develop now.>
<No specific year predictions. No operational advice.>

**REMEDIES_GENERAL:**
- [Study or preparation recommendations aligned with chart]
- [Mentor/guardian consultation for future planning]

⚠️ GUARDIAN NOTE: For any financial planning or business decisions, involve a guardian or trusted adult.
"""

    def _get_timing_fallback_output_format(self, kp_available: bool) -> str:
        """
        Output format for TIMING FALLBACK mode.
        No computed timing windows. Uses dasha timeline comparatively.
        Probabilistic language only — no deterministic predictions.
        """
        kp_section = """
**B. KP PROMISE STATUS (Growth Foundation):**

For key cusps (7th, 11th, 3rd, 9th):
- House [N] ([Meaning]):
  - Sub Lord: [Planet] ← Decides promise/denial
  - Sub Lord Signifies: Houses [X, Y, Z]
  - Verdict: PROMISE/DENIAL/WEAK_PROMISE
  - Growth Implication: [What this means for growth potential]

⚠️ Promise status shapes which dasha periods will feel stronger — explain this connection.
""" if kp_available else ""

        return f"""
OUTPUT FORMAT — TIMING FALLBACK MODE (NO COMPUTED WINDOWS):

⚠️ MANDATORY LANGUAGE RULES:
   FORBIDDEN: "You will see growth in [year]" / "Business will expand by [date]"
   REQUIRED: "This period can support..." / "Higher alignment develops during..."

**GENERAL_ANSWER:**
<Warm, honest answer acknowledging that the chart shows growth potential.>
<Frame: "While precise timing computation is not available, your chart suggests...">
<Use probabilistic language throughout. No guaranteed predictions.>

**ASTROLOGICAL_ANALYSIS:**

**A. ALIGNMENT WITH UNIFIED VERDICT:**
- Growth Outlook: [from unified verdict]
- Growth Viable: [YES/NO/CONDITIONAL]
- Confidence: [from unified verdict]
- Promise Status: [7th: X, 11th: Y, 3rd: Z, 9th: W]
- KP-Vedic Agreement: [AGREEMENT/PARTIAL/CONFLICT]

{kp_section}

**C. VEDIC HOUSE LORD ANALYSIS (Secondary):**

**Key Growth Houses:**
- 7th Lord ([Planet]): Placed in House [N] — [business strength assessment]
- 11th Lord ([Planet]): Placed in House [N] — [gains potential assessment]
- 3rd Lord ([Planet]): Placed in House [N] — [initiative strength]
- 9th Lord ([Planet]): Placed in House [N] — [fortune/expansion potential]

**D. DASHA PERIOD ASSESSMENT (Comparative — NOT Predictive):**

⚠️ Frame ALL periods comparatively. Avoid deterministic language.

**Current Period:**
- Dasha: [from current dasha data]
- Business Growth Alignment: [HIGH/MODERATE/LOW comparatively]
- What this period supports: [preparation/consolidation/expansion readiness]
- What to actively do now: [specific recommendation]

**Upcoming Periods (Comparative Strength):**

For each upcoming dasha (from timeline, next 3–5 periods):

[Dasha Name] — [start] to [end]:
- Comparative Strength: [stronger/moderate/weaker than current]
- Why: [dasha lord's connection to growth houses]
- Can support: [what kind of business activity this period aligns with]
- Recommended focus: [what to prepare or pursue during this phase]

⚠️ Structure phrasing as:
"The [Dasha] period can enhance..."
"Higher growth probability may develop during..."
"This phase builds readiness for..."

**E. LAGNA LORD (Business Approach):**
- [Planet] as lagna lord — [how it shapes growth strategy]

**SUMMARY:**
<2–3 sentences. Honest about absence of computed windows.>
<End with: one actionable step to take NOW to prepare for upcoming favorable periods.>
<Example: "Consult for precise timing computation during [specific upcoming dasha].">

**REMEDIES_ASTROLOGICAL:**
- [Strengthen planets connected to growth houses]

**REMEDIES_GENERAL:**
- [Practical business preparation steps]
- Recommendation: Get detailed timing computation for [strongest upcoming dasha]
"""

    # ══════════════════════════════════════════════════════════════
    # QUESTION 4 — BUSINESS CHALLENGES
    # ══════════════════════════════════════════════════════════════

    def _build_challenges_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today              = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data    = kwargs.get("additional_data", {})
        is_minor           = kwargs.get("is_minor", False)
        dob                = kwargs.get("dob")

        house_lords     = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects   = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info      = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block = ""
        if meta and meta.query_type == QueryType.TIMING:
            timeline_block = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        if is_minor:
            minor_challenges_block = f"""
🚨 MINOR EDUCATIONAL MODE — CHALLENGES AS LEARNING
Person is under 18. DOB: {dob or 'N/A'}
Frame all obstacles as LEARNING MOMENTS about business cycles.
Do NOT suggest operational decisions to address challenges.
Do NOT recommend expansion, contraction, or partnerships.
Tone: Educational, Encouraging, Developmental.
"""
        else:
            minor_challenges_block = ""

        question_type = "minor_general" if is_minor else "general"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, False, dob=dob, is_minor=is_minor
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Sub-subdomain: Business Challenges
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor Mode: {'YES 🚨' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_challenges_block}

{unified_verdict_block}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

CHALLENGE FRAMEWORK:
Frame ALL obstacles as:
✅ TEMPORARY PHASES, not permanent blocks
✅ CORRECTABLE with strategy and patience
✅ MANAGEABLE with proper planning

Key challenge houses in growth context:
• 6th house: Competition, cash flow pressure, loans
• 8th house: Sudden obstacles, transformation needed
• 12th house: Hidden expense leaks, market losses

SPECIFIC GUIDELINES FOR CHALLENGES:
• Identify specific challenges from KP obstacle house analysis
• Show which dashas reduce vs amplify challenges
• Align difficulty assessment with unified verdict confidence
• Always end with actionable strategy to overcome obstacles

{self.get_output_format(kp_available, False, question_type, is_minor)}
"""

    # ══════════════════════════════════════════════════════════════
    # GENERAL FALLBACK
    # ══════════════════════════════════════════════════════════════

    def _build_general_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:

        today              = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data    = kwargs.get("additional_data", {})
        is_minor           = kwargs.get("is_minor", False)
        dob                = kwargs.get("dob")

        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing          = timing_windows_data.get("has_timing", False) and not is_minor

        house_lords     = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        house_aspects   = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        lagna_info      = additional_data.get("lagna_info", {})

        unified_verdict_block = self._format_unified_verdict(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data)
        timing_formatted  = self._format_timing_windows(timing_windows_data) if has_timing else ""
        lagna_formatted   = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted   = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)
        current_dasha_block = self._format_current_dasha(kwargs.get("current_dasha"))
        timeline_block      = self._format_dasha_timeline(kwargs.get("dasha_timeline"))

        question_type = "minor_general" if is_minor else "general"
        analysis_instructions = self._get_analysis_instructions(
            kp_available, question_type, has_timing, dob=dob, is_minor=is_minor
        )

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Business
Subtopic: Growing Existing Business
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Minor Mode: {'YES 🚨' if is_minor else 'NO'}
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

GUIDELINES:
• Align answer with unified growth verdict
• Use pure KP methodology if KP data available
• Be honest about KP-Vedic agreement/conflict
• Provide warm, actionable guidance

{self.get_output_format(kp_available, has_timing, question_type, is_minor)}
"""
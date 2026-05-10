"""
Family Planning and Parenting – LLM Prompts v11.0

FIXES FROM v10.0:
✅ FIX 1: Machine-parseable output labels (GENERAL_ANSWER / ASTROLOGICAL_ANALYSIS / SUMMARY / REMEDIES)
          matching Finance pattern — prevents empty field mapping in pipeline
✅ FIX 2: _format_current_dasha now reads parenting_current_dasha key (not current_dasha)
✅ FIX 3: Parenting style prompt now includes aspects_data in f-string (was formatted but dropped)
✅ FIX 4: needs_resonant_jump flag surfaced in timing window formatting
✅ FIX 5: Remedies prompts pass house lord strength data so LLM targets correct weak planets
✅ FIX 6: Minor chart (Vihaan-type) timing blank now shows explicit explanation message
✅ FIX 7: kwargs.pop("additional_data") replaced with kwargs.get to avoid losing data in sub-builders
✅ FIX 8: PAR_CH_1 / PAR_CH_2 summary-only pattern replaced with full answer flow

DOMAIN-SPECIFIC WEIGHTAGE (Parenting):
┌─────────────────────────────────────────────────────────────────┐
│ Childbirth Promise (NON-TIMING):  Vedic 60% + KP 40%           │
│ Best Time to Conceive (TIMING):   Vedic 50% + KP 20% + Dasha 30%│
│ Child Health (NON-TIMING):        Vedic 75% + KP 25%           │
│ Parenting Style (NON-TIMING):     Vedic 90% + KP 10%           │
│ Remedies:                         Vedic 85% + KP 15%           │
└─────────────────────────────────────────────────────────────────┘
"""

from typing import Dict, List, Optional
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

DOMAIN_PREFIX = "parenting"


class FamilyPlanningAndParentingPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Parenting → Family Planning and Parenting
    v11.0 — Machine-parseable output labels, fixed data key lookups,
             needs_resonant_jump surfaced, personalized remedies,
             minor timing blank explained, full answer flow for all questions.
    """

    domain = "Parenting"
    subtopic = "Family Planning and Parenting"

    # =========================================================================
    # MINOR DETECTION
    # =========================================================================

    def _detect_minor(self, dob: str, dasha_timeline: Dict) -> bool:
        if not dob:
            return False
        today = datetime.now()
        try:
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
        except (ValueError, TypeError):
            return False
        current_age = today.year - dob_dt.year - (
            (today.month, today.day) < (dob_dt.month, dob_dt.day)
        )
        return current_age < 18

    # =========================================================================
    # LANGUAGE INSTRUCTION
    # =========================================================================

    def get_language_instruction(self, language: str) -> str:
        if language.lower() == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, houses, aspects).
Example: "आपकी कुंडली में **संतान का योग** स्पष्ट है।"
"""
        elif language.lower() == "hinglish":
            return """
════════════════════════════════════════
LANGUAGE: HINGLISH (Roman Script)
════════════════════════════════════════
Respond in Hinglish (Hindi + English mix, Roman script).
Example: "Aapki kundali mein santaan ka yoga clearly dikh raha hai."
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear English.
"""

    def _get_language_instruction_safe(self, language: str) -> str:
        try:
            return self.get_language_instruction(language)
        except Exception:
            if language == "Hindi":
                return "IMPORTANT: Respond ONLY in Hindi (Devanagari script)."
            return f"IMPORTANT: Respond in {language}."

    # =========================================================================
    # EXAMPLE TEXT HELPERS
    # =========================================================================

    def _get_example_text(self, language: str, example_type: str) -> str:
        examples = {
            "Hindi": {
                "5th_house": (
                    "पंचम भाव के स्वामी [ग्रह] [भाव] में [राशि] में हैं। "
                    "इसका अर्थ है कि संतान भाव मध्यम बल का है।"
                ),
                "kp_correct": (
                    "KP प्रणाली के अनुसार, 5वें भाव का उप-स्वामी गुरु है। "
                    "गुरु 2, 5, 11 भाव को संकेतित करता है — संतान का स्पष्ट वचन है।"
                ),
                "kp_wrong": (
                    "❌ 'गुरु शुभ ग्रह है इसलिए संतान होगी' — यह KP नहीं है।"
                ),
                "timing_unavailable": "संतान प्राप्ति के लिए विशिष्ट समय की गणना उपलब्ध नहीं है।",
                "blocked_message": (
                    "कुंडली में वर्तमान में कुछ चुनौतियां हैं। "
                    "उपायों के साथ प्रयास जारी रखें और चिकित्सा परामर्श अवश्य लें।"
                ),
                "developmental_note": (
                    "यह कुंडली अल्पवयस्क की है। वैदिक ज्योतिष में यह "
                    "दीर्घकालिक जीवन उद्देश्य का काल है, न कि तत्काल घटना का।"
                ),
            },
            "English": {
                "5th_house": (
                    "The 5th house lord [planet] is placed in [house] in [sign]. "
                    "This indicates a moderately strong 5th house — childbirth is possible, "
                    "though some support and effort may be needed."
                ),
                "kp_correct": (
                    "According to KP, the 5th house sub-lord is Jupiter. "
                    "Jupiter signifies houses 2, 5, 11 — the 2/5/11 promise pattern. "
                    "Childbirth is clearly promised in this chart."
                ),
                "kp_wrong": (
                    "❌ 'Jupiter is benefic so there will be children' — "
                    "This is NOT KP. This is guessing based on planet nature."
                ),
                "timing_unavailable": "Specific timing for childbirth could not be calculated at this time.",
                "blocked_message": (
                    "There are significant challenges in the chart at this time. "
                    "Continue efforts with remedies and consult a medical professional."
                ),
                "developmental_note": (
                    "This chart belongs to someone under 18. In Vedic astrology, "
                    "dashas at this life stage represent long-term orientation and "
                    "preparation — not immediate event manifestation."
                ),
            },
        }
        lang_examples = examples.get(language, examples["English"])
        return lang_examples.get(example_type, "")

    def _get_analysis_starters(self, language: str) -> Dict[str, str]:
        return {
            "Hindi": {
                "vedic": "वैदिक ज्योतिष के अनुसार,",
                "kp": "KP प्रणाली के अनुसार,",
            },
            "English": {
                "vedic": "According to Vedic astrology,",
                "kp": "According to KP astrology,",
            },
        }.get(
            language,
            {"vedic": "According to Vedic astrology,", "kp": "According to KP astrology,"},
        )

    # =========================================================================
    # SYSTEM PROMPT
    # =========================================================================

    def build_system_prompt(self, language: str = "English", is_timing: bool = False,
                            question_type: str = "general") -> str:
        weightage_map = {
            "promise":  "CHILDBIRTH PROMISE: KP 40% + Vedic 60% (No Dasha)",
            "timing":   "CONCEPTION TIMING:  KP 20% + Vedic 50% + Dasha 30%",
            "health":   "CHILD HEALTH:        KP 25% + Vedic 75% (No Dasha)",
            "style":    "PARENTING STYLE:     KP 10% + Vedic 90% (No Dasha)",
            "remedies": "REMEDIES:            KP 15% + Vedic 85% (No Dasha)",
            "general":  "GENERAL PARENTING:   KP 20% + Vedic 65% + Dasha 15%",
        }
        weightage_text = weightage_map.get(question_type, weightage_map["general"])
        kp_correct = self._get_example_text(language, "kp_correct")
        kp_wrong   = self._get_example_text(language, "kp_wrong")
        example_5th = self._get_example_text(language, "5th_house")

        return f"""You are an expert KP and Vedic astrologer specializing in childbirth,
conception timing, child health, and parenting dynamics.

**{weightage_text}**

═══════════════════════════════════════════════════════════════════════════════
              AGE SAFETY RULE (CRITICAL — READ FIRST)
═══════════════════════════════════════════════════════════════════════════════

If person is UNDER 18 (DEVELOPMENTAL MODE ACTIVE):
• NEVER predict childbirth timing or conception dates
• NEVER interpret dashas as childbirth triggers
• Frame all dasha periods as preparation / long-term orientation
• Focus: developmental stage, life direction, future readiness
• Tone: encouraging, nurturing, future-building

═══════════════════════════════════════════════════════════════════════════════
          🔬 PARENTING KP METHODOLOGY (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

PARENTING KP WORKS AS FOLLOWS:
1. 5th HOUSE SUB-LORD: Primary gate. Signifies 2/5/11 → promise. Signifies 1/4/10 → blocked.
2. JUPITER AS KARAKA: Natural significator. Strong → promise; afflicted → delays.
3. PROMISE PATTERN (2/5/11): Well-connected → PROMISED. 1/4/10 dominate → OBSTRUCTED.
4. EVALUATOR OUTPUT STATES (USE THESE — DO NOT RECOMPUTE):
   - PROMISED | PROMISED_WITH_OBSTACLES | BLOCKED | UNCERTAIN

⚠️ CRITICAL: Evaluator has computed the KP state. EXPLAIN it, do not re-derive it.

CORRECT: ✅ "{kp_correct}"
WRONG:   {kp_wrong}

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES
═══════════════════════════════════════════════════════════════════════════════
1. NEVER invent dates — only use dates from TIMING WINDOWS section
2. ONLY use data provided — no invented positions or aspects
3. KP STATE IS LOCKED — do not override based on planetary data

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════
1. NEVER list facts without interpretation
   ❌ "5th Lord Jupiter in 6th house. Retrograde. Benefic."
   ✅ "{example_5th}"
2. Write in FLOWING PARAGRAPHS — NOT bullet lists
3. Label systems clearly: "According to Vedic astrology," / "According to KP astrology,"
4. Answer the ACTUAL question directly

═══════════════════════════════════════════════════════════════════════════════
                    ⚠️ SENSITIVE DOMAIN SAFETY RULES
═══════════════════════════════════════════════════════════════════════════════
- NEVER induce fear or anxiety about childbirth prospects
- NEVER override medical advice
- NEVER declare permanent denial unless KP state is explicitly BLOCKED
- All risks must be framed as TENDENCIES, not certainties
- Always recommend professional medical consultation
- Frame delays as "preparation time" — not "problems" or "defects"
"""

    # =========================================================================
    # KP PROMISE VERDICT BANNER
    # =========================================================================

    def _format_kp_promise_verdict(self, additional_data: Dict, language: str = "English") -> str:
        if not additional_data:
            return ""
        kp_data = additional_data.get("parenting_kp_promise", {})
        if not kp_data:
            return ""

        state       = kp_data.get("state", "UNCERTAIN")
        has_promise = kp_data.get("has_promise", False)

        if state == "PROMISED":
            verdict_line = "✅ KP VERDICT: CHILDBIRTH PROMISED — analysis must be confident and positive"
            tone_rule = (
                "✅ ALLOWED:   'Childbirth is clearly indicated'\n"
                "❌ FORBIDDEN: Any statement suggesting denial or strong doubt"
            )
        elif state == "PROMISED_WITH_OBSTACLES":
            verdict_line = "⚠️ KP VERDICT: PROMISED WITH OBSTACLES — show BOTH promise AND challenge"
            tone_rule = (
                "✅ ALLOWED:   'Childbirth is indicated, but with delays or medical support needed'\n"
                "❌ FORBIDDEN: Pure confidence ('will definitely happen') OR pure denial ('won't happen')"
            )
        elif state == "BLOCKED":
            verdict_line = "❌ KP VERDICT: BLOCKED — focus on challenges, remedies, and medical care"
            tone_rule = (
                "✅ ALLOWED:   'Significant challenges at this time — remedies and medical help essential'\n"
                "❌ FORBIDDEN: Any confident promise of childbirth"
            )
        else:
            verdict_line = "❓ KP VERDICT: UNCERTAIN — present balanced analysis with both possibilities"
            tone_rule = (
                "✅ ALLOWED:   'Signals are mixed — professional consultation advised'\n"
                "❌ FORBIDDEN: Strong promise OR strong denial without evidence"
            )

        lines = [
            "╔═══════════════════════════════════════════════════════════════════════════╗",
            "║  🔒 COMPUTED KP PROMISE STATE — DO NOT OVERRIDE                          ║",
            "╚═══════════════════════════════════════════════════════════════════════════╝",
            "",
            f"  {verdict_line}",
            f"  Has Promise: {'YES' if has_promise else 'NO'}",
            f"  State: {state}",
            "",
            "  TONE RULE:",
            f"  {tone_rule}",
            "",
            "  ⚠️ ALL QUESTIONS IN THIS SESSION MUST ALIGN WITH THIS VERDICT.",
            "╔═══════════════════════════════════════════════════════════════════════════╗",
            f"║  VERDICT LOCKED TO: {state:<52} ║",
            "╚═══════════════════════════════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)

    # =========================================================================
    # OUTPUT FORMAT — machine-parseable labels (FIX 1)
    # Matches Finance pattern: GENERAL_ANSWER / ASTROLOGICAL_ANALYSIS / SUMMARY / REMEDIES
    # =========================================================================

    def get_output_format(self, question_type: str = "promise", language: str = "English",
                          has_timing: bool = False, kp_available: bool = True,
                          is_minor: bool = False) -> str:

        starters = self._get_analysis_starters(language)
        kp_correct = self._get_example_text(language, "kp_correct")
        kp_wrong   = self._get_example_text(language, "kp_wrong")

        if question_type == "timing" and has_timing and not is_minor:
            timing_output = """
    **TIMING SECTION (MANDATORY — include BOTH windows):**

    🏆 BEST WINDOW (Highest Score):
    - Period: [exact start to end — from timing data above]
    - Dasha: [dasha name from data]
    - Score: [score]/100
    - Needs Resonant Jump: [Yes/No — explain what this means for the person]
    - Why this is BEST: [Explain dasha lord connections to houses 2/5/11]
    - Trade-off: [e.g., "Further in future but strongest alignment"]

    ⏰ NEAREST WINDOW (Soonest Opportunity):
    - Period: [exact start to end — from timing data above]
    - Dasha: [dasha name from data]
    - Score: [score]/100
    - Why this is NEAREST: [Earliest period with favorable score >= 50]
    - Trade-off: [e.g., "Sooner but not the absolute best alignment"]

    👤 USER GUIDANCE:
    If best = nearest: "🎯 IDEAL TIMING: Both windows are the same — act during [dates]."
    If different: Give trade-off and let user choose timing vs quality.

    NOTE on Resonant Jump: If needs_resonant_jump=true, explain this means the period
    requires conscious effort/remedies to activate the promise — it won't happen passively.
"""
        elif question_type == "timing" and is_minor:
            timing_output = """
    **DEVELOPMENTAL GUIDANCE (Minor — No Timing Windows):**

    🌱 CURRENT PHASE:
    - What this dasha period is building toward long-term
    - Academic / personal development focus for this period

    🔮 LONG-TERM ORIENTATION:
    - What the overall chart suggests about future family life (age 18+)
    - General life direction — not specific event predictions

    ⚠️ DO NOT mention childbirth timing, conception dates, or specific years.
"""
        else:
            timing_output = ""

        kp_example_block = ""
        if kp_available and question_type in ("promise", "timing", "health"):
            kp_example_block = f"""
    ✅ CORRECT KP: "{kp_correct}"
    ❌ WRONG KP:   {kp_wrong}
    RULE: Restate the evaluator's findings. Do NOT re-derive KP from raw planetary positions.
"""

        # ── FIX 1: Machine-parseable section labels ──────────────────────────
        return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (FOLLOW THIS STRUCTURE EXACTLY — USE THESE EXACT LABELS):
═══════════════════════════════════════════════════════════════════════════════

**GENERAL_ANSWER:**
<Direct, clear 2-3 line answer to the question.>
{"Mention BEST and NEAREST timing windows." if question_type == "timing" and has_timing and not is_minor else ""}
{"State the KP promise verdict in plain language." if kp_available and question_type == "promise" else ""}
{"Frame as long-term life orientation — no event predictions." if is_minor and question_type == "timing" else ""}

**ASTROLOGICAL_ANALYSIS:**

[Write in FLOWING PARAGRAPHS — not bullet points]

PARAGRAPH 1 — VEDIC ANALYSIS (PRIMARY):
Must begin with: "{starters['vedic']}"
- Analyze 5th house lord: placement, dignity, strength → what does this MEAN for children?
- Supporting houses (1st, 7th, 9th, 11th) → how do they support or challenge the promise?
- Jupiter as karaka → strong or afflicted → what is the impact?
- Connect every fact to the OUTCOME for the question asked.
{"- For minor: frame as long-term family orientation, not event prediction." if is_minor else ""}

{"PARAGRAPH 2 — KP CONFIRMATION:" if kp_available else ""}
{f'Must begin with: "{starters["kp"]}"' if kp_available else ""}
{"Restate the KP state. Do NOT add extra KP analysis." if kp_available else ""}
{kp_example_block}

PARAGRAPH — SUPPORTING HOUSES:
- 1st house (body/constitution) → capacity for parenthood
- 7th house (partner) → partner's role in childbirth
- 9th house (fortune, past karma) → overall life blessing for children
- 11th house (fulfillment of desire) → wish for children fulfilled?

PARAGRAPH — JUPITER (KARAKA):
Jupiter's position, dignity, and condition → explicit impact on childbirth promise.

{timing_output}

**SUMMARY:**
TELL CLIENT: "[Specific actionable advice — include dates if timing available, else dasha guidance]"
[ALWAYS include: recommend professional medical consultation]
{"[For minor: frame as preparation phase — not event timeline]" if is_minor else ""}

**REMEDIES_ASTROLOGICAL:**
{"Target weak planets affecting 5th house promise. Include Jupiter remedies if Jupiter is afflicted." if question_type != "style" else "Constructive guidance only — not criticism."}

**REMEDIES_GENERAL:**
{"Include: always recommend professional medical/pediatric consultation." if question_type in ("promise", "timing", "health") else ""}
═══════════════════════════════════════════════════════════════════════════════
"""

    # =========================================================================
    # DATA EXTRACTION HELPERS
    # =========================================================================

    def _get_kp_state(self, additional_data: Dict) -> str:
        if not additional_data:
            return "UNCERTAIN"
        return additional_data.get("parenting_kp_promise", {}).get("state", "UNCERTAIN")

    def _is_blocked(self, additional_data: Dict) -> bool:
        return self._get_kp_state(additional_data) == "BLOCKED"

    def _get_relevant_kp_points(self, additional_data: Dict, question_type: str) -> List[str]:
        if not additional_data:
            return []
        kp_data = additional_data.get("parenting_kp_promise", {})
        points = kp_data.get("points", [])
        if not points:
            return []

        KP_KEYWORDS = {
            "promise": [
                "kp promise", "childbirth promised", "very strong promise",
                "kp strong promiser", "kp boost", "2/5/11 dominance",
                "kp signifiers", "parivartana",
            ],
            "timing": [
                "kp promise", "promised with obstacles", "kp delay", "kp signifiers",
            ],
            "health": ["kp sign:"],
            "general": [
                "kp promise", "kp support", "kp sign", "kp delay",
                "kp signifiers", "adoption",
            ],
        }
        keywords = KP_KEYWORDS.get(question_type, KP_KEYWORDS["general"])
        return [p for p in points if any(k in p.lower() for k in keywords)]

    def _format_kp_data(self, additional_data: Dict, question_type: str = "general") -> str:
        if not additional_data:
            return ""
        kp_data = additional_data.get("parenting_kp_promise", {})
        if not kp_data:
            return ""

        state  = kp_data.get("state", "UNCERTAIN")
        points = self._get_relevant_kp_points(additional_data, question_type)

        lines = ["KP DATA (Pre-computed by Evaluator — restate, do not re-derive):"]
        lines.append(f"• Promise State: {state.upper()}")

        if points:
            lines.append("")
            lines.append("KP Findings:")
            for p in points:
                if isinstance(p, str) and p.strip():
                    lines.append(f"  {p}")

        return "\n".join(lines)

    # =========================================================================
    # FIX 4: needs_resonant_jump surfaced in timing window formatting
    # =========================================================================

    def _format_timing_windows(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""

        try:
            best    = timing_data.get("best_window", {})
            nearest = timing_data.get("nearest_window", {})

            if not best and not nearest:
                return ""

            lines = ["╔═══════════════════════════════════════════════════════════════╗"]
            lines.append("║  ⭐ CONCEPTION / CHILDBIRTH TIMING WINDOWS                    ║")
            lines.append("╚═══════════════════════════════════════════════════════════════╝")
            lines.append("")
            lines.append("⚠️ CRITICAL: Mention BOTH windows. Explain WHY each is favorable.")
            lines.append("")

            if best:
                # FIX 4: surface needs_resonant_jump
                needs_jump = best.get("needs_resonant_jump", False)
                lines.append("🏆 BEST WINDOW (Highest Astrological Score):")
                lines.append(f"  Dasha:  {best.get('dasha', 'N/A')}")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score:  {best.get('final_score') or best.get('score', 0):.0f}/100")
                lines.append(f"  Age at start: {best.get('age_at_start', 'N/A')} yrs")
                lines.append(f"  Delay years:  {best.get('delay_years', 0)}")
                if needs_jump:
                    lines.append("  ⚠️ Needs Resonant Jump: YES — This window requires active")
                    lines.append("     remedies and effort to activate the promise. It will NOT")
                    lines.append("     manifest passively. Recommend remedies 3-6 months before.")
                else:
                    lines.append("  ✅ Needs Resonant Jump: NO — Promise activates naturally.")
                lines.append("  Trade-off: May be further away, but strongest alignment.")
                lines.append("")

            if nearest and nearest != best:
                needs_jump_n = nearest.get("needs_resonant_jump", False)
                lines.append("⏰ NEAREST FAVORABLE WINDOW (Soonest Opportunity):")
                lines.append(f"  Dasha:  {nearest.get('dasha', 'N/A')}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score:  {nearest.get('final_score') or nearest.get('score', 0):.0f}/100")
                lines.append(f"  Age at start: {nearest.get('age_at_start', 'N/A')} yrs")
                lines.append(f"  Delay years:  {nearest.get('delay_years', 0)}")
                if needs_jump_n:
                    lines.append("  ⚠️ Needs Resonant Jump: YES — Active remedies required.")
                else:
                    lines.append("  ✅ Needs Resonant Jump: NO — Promise activates naturally.")
                lines.append("  Trade-off: Sooner, but not peak alignment.")
                lines.append("")

                if best and (best.get("dasha") == nearest.get("dasha")
                             and best.get("start") == nearest.get("start")):
                    lines.append("  ✅ LUCKY: Best window IS the nearest window!")

            lines.append("═══════════════════════════════════════════════════════════════")
            lines.append("INSTRUCTIONS: Use ONLY these dates. Show WHY each period is")
            lines.append("favorable by connecting dasha lords to houses 2/5/11.")
            lines.append("If needs_resonant_jump=true, include remedy guidance in SUMMARY.")
            lines.append("═══════════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        timing_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return False
        return bool(timing_data.get("best_window") or timing_data.get("nearest_window"))

    def _format_house_lords(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        lines = ["HOUSE LORDS DATA:"]
        parenting_houses = {1, 5, 7, 9, 11}

        for house_num in sorted(house_lords.keys()):
            if house_num not in parenting_houses:
                continue
            info = house_lords.get(house_num, {})
            if not info:
                continue

            lord       = info.get("lord", "N/A")
            lord_house = info.get("lord_in_house", "N/A")
            lord_sign  = info.get("lord_in_sign", "N/A")
            dignity    = info.get("lord_dignity", "N/A")
            strength   = info.get("lord_strength_score", 0)

            conditions = []
            if info.get("lord_is_combust"):
                conditions.append("Combust")
            if info.get("lord_is_retrograde"):
                conditions.append("Retrograde")
            condition_str = ", ".join(conditions) if conditions else "Normal"
            planets = ", ".join(info.get("planets_in_house", [])) or "None"

            strength_label = (
                "STRONG ✅" if strength >= 70
                else "MODERATE ○" if strength >= 40
                else "WEAK ⚠️"
            )

            lines.append(
                f"• H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | "
                f"{dignity} | {condition_str} | Str:{strength}/100 [{strength_label}] | Planets:{planets}"
            )

        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        lines = ["ASPECTS ON PARENTING HOUSES:"]
        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]
            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            if benefic or malefic:
                b_str = ", ".join(benefic) if benefic else "None"
                m_str = ", ".join(malefic) if malefic else "None"
                lines.append(f"• H{house_num}: Benefic={b_str} | Malefic={m_str}")

        return "\n".join(lines) if len(lines) > 1 else ""

    # =========================================================================
    # FIX 2: _format_current_dasha reads parenting_current_dasha key
    # =========================================================================

    def _format_current_dasha(self, additional_data: Dict) -> str:
        if not additional_data:
            return ""

        # FIX 2: correct key — evaluator stores as parenting_current_dasha
        current_dasha = (
            additional_data.get(f"{DOMAIN_PREFIX}_current_dasha") or
            additional_data.get("current_dasha") or
            {}
        )

        if not current_dasha:
            # fallback: try dasha_timeline next_6_months
            dasha_timeline = additional_data.get(f"{DOMAIN_PREFIX}_dasha_timeline") or {}
            next_periods = dasha_timeline.get("next_6_months", [])
            if next_periods:
                current_dasha = next_periods[0]

        if not current_dasha:
            return ""

        try:
            name  = current_dasha.get("dasha_name", "")
            start = current_dasha.get("date_range", {}).get("start", "Unknown")
            end   = current_dasha.get("date_range", {}).get("end", "Unknown")
            return f"CURRENT DASHA: {name} ({start} to {end})"
        except Exception:
            return ""

    # =========================================================================
    # FIX 5: Remedy planet extraction from house lord data (personalized)
    # =========================================================================

    def _format_weak_planets_for_remedies(self, additional_data: Dict) -> str:
        """
        Extract weak planets from house lord data so LLM gives personalized remedies.
        FIX 5: Remedies were generic because this data was never passed in.
        """
        if not additional_data:
            return ""

        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        if not house_lords:
            return ""

        weak_planets = []
        moderate_planets = []
        strong_planets = []
        combust_planets = []

        parenting_houses = {1, 5, 7, 9, 11}
        for house_num, info in house_lords.items():
            if house_num not in parenting_houses:
                continue
            lord     = info.get("lord", "")
            strength = info.get("lord_strength_score", 50)
            dignity  = info.get("lord_dignity", "")
            combust  = info.get("lord_is_combust", False)

            if combust:
                combust_planets.append(f"{lord} (H{house_num} lord, combust)")
            if strength < 40:
                weak_planets.append(f"{lord} (H{house_num} lord, {dignity}, Str:{strength}/100)")
            elif strength < 70:
                moderate_planets.append(f"{lord} (H{house_num} lord, {dignity}, Str:{strength}/100)")
            else:
                strong_planets.append(f"{lord} (H{house_num} lord, {dignity}, Str:{strength}/100)")

        if not weak_planets and not combust_planets:
            return ""

        lines = ["╔═══════════════════════════════════════════════════════════════╗"]
        lines.append("║  🎯 REMEDY TARGETS (From House Lord Analysis)                 ║")
        lines.append("╚═══════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("⚠️ PERSONALIZE REMEDIES TO THESE SPECIFIC PLANETS:")
        lines.append("")

        if combust_planets:
            lines.append("🔥 COMBUST (Urgent — highest priority for remedies):")
            for p in combust_planets:
                lines.append(f"  • {p}")
            lines.append("")

        if weak_planets:
            lines.append("⚠️ WEAK LORDS (Strength < 40 — need strengthening):")
            for p in weak_planets:
                lines.append(f"  • {p}")
            lines.append("")

        if moderate_planets:
            lines.append("○ MODERATE LORDS (Strength 40-70 — support if needed):")
            for p in moderate_planets:
                lines.append(f"  • {p}")
            lines.append("")

        lines.append("REMEDY GUIDE (match to planets above):")
        lines.append("  Sun weak/combust   → Ruby/Surya mantra, Sunday fasts, wheat/jaggery donation")
        lines.append("  Moon weak          → Pearl/Chandra mantra, Monday fasts, white items, Shiva worship")
        lines.append("  Mars weak/combust  → Coral/Mangal mantra, Tuesday fasts, red lentils donation")
        lines.append("  Mercury weak       → Emerald/Budh mantra, Wednesday fasts, green items")
        lines.append("  Jupiter weak/combust → Yellow sapphire/Guru mantra, Thursday fasts, yellow items, Vishnu")
        lines.append("  Venus weak         → Diamond/Shukra mantra, Friday fasts, white items, Lakshmi")
        lines.append("  Saturn weak        → Blue sapphire/Shani mantra, Saturday charity, service to elderly")
        lines.append("  Rahu affliction    → Hessonite/Rahu mantra, donate to poor, Durga worship")
        lines.append("  Ketu affliction    → Cat's eye/Ketu mantra, spiritual practice, Ganesha worship")
        lines.append("")
        lines.append("⚠️ RULE: ONLY recommend remedies for planets listed above.")
        lines.append("   Do NOT give generic remedy lists — target the ACTUAL weak planets.")
        lines.append("═══════════════════════════════════════════════════════════════")

        return "\n".join(lines)

    # =========================================================================
    # DEVELOPMENTAL OVERRIDE BLOCK
    # =========================================================================

    def _build_developmental_override(self, dob: str, language: str) -> str:
        return f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) — MANDATORY OVERRIDE               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Person DOB: {dob}
Current age is UNDER 18.

STRICT RULES:
• Do NOT predict childbirth timing or conception dates
• Do NOT frame dashas as childbirth triggers
• Do NOT use phrases like "you will have children in [year]"
• Do NOT interpret 5th house dasha as an imminent event trigger

INTERPRETATION RULE:
→ Interpret dashas as PREPARATION PHASES, not event windows
→ Frame 5th house strength as long-term parenting orientation
→ Focus on: life direction, values, future readiness
→ If chart shows strong 5th house: "This person has a natural affinity
  for family life — a promising foundation for the future."

Tone: Developmental, encouraging, age-appropriate.
This override is MANDATORY and supersedes all timing instructions.

╔═══════════════════════════════════════════════════════════════════════════╗
║  TIMING WINDOWS, IF ANY, MUST BE COMPLETELY IGNORED FOR THIS PERSON.     ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

    # =========================================================================
    # FIX 6: Minor timing explanation block
    # =========================================================================

    def _build_minor_timing_explanation(self, dob: str, language: str) -> str:
        """
        FIX 6: When timing section is empty for a minor, provide an explicit explanation
        instead of a blank section. This replaces 'Best Time to Conceive: []' with context.
        """
        return f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ℹ️  WHY TIMING WINDOWS ARE NOT SHOWN FOR THIS CHART                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

This chart belongs to someone currently under 18 (DOB: {dob}).

Conception timing windows are not generated for minors because:
• Vedic astrology's childbirth dashas apply to adult life stages
• Showing such windows for a minor would be astrologically incorrect
• The 5th house analysis at this age represents long-term family orientation,
  not imminent events

WHAT THIS MEANS FOR THE READING:
• Focus the analysis on the child's developmental potential
• Describe the 5th house as a "future family affinity indicator"
• Frame Jupiter's role as the child's own teaching/wisdom capacity
• Any parent asking about this child's chart: note that childbirth
  planning questions should be asked using the PARENT'S chart

╔═══════════════════════════════════════════════════════════════════════════╗
║  NO TIMING DATES SHOULD APPEAR IN YOUR RESPONSE FOR THIS PERSON.         ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

    # =========================================================================
    # MAIN ROUTING METHOD
    # FIX 7: kwargs.get instead of kwargs.pop to preserve additional_data
    # =========================================================================

    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi",
        **kwargs,
    ) -> str:
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")

            # FIX 7: pop additional_data at the router level so it is not in **kwargs
            # when passed to sub-builders (which take it as an explicit positional arg).
            # Sub-builders receive it directly — not via **kwargs.
            additional_data = kwargs.pop("additional_data", {})

            raw = "\n".join(technical_points) if technical_points else ""

            dob            = kwargs.get("dob")
            dasha_timeline = kwargs.get("dasha_timeline")
            is_minor       = self._detect_minor(dob, dasha_timeline)

            kwargs["is_minor"] = is_minor
            kwargs["dob"]      = dob

            logger.warning(f"[PARENTING] Minor Detection → DOB: {dob}, Is Minor: {is_minor}")
            logger.info(f"Building parenting prompt: sub_subdomain={sub_subdomain}, language={language}")

            if "Timing" in sub_subdomain or "Conceive" in sub_subdomain:
                return self._build_timing_prompt(question, additional_data, raw, language, **kwargs)
            elif "Promise" in sub_subdomain or "Possibility" in sub_subdomain:
                return self._build_promise_prompt(question, additional_data, raw, language, **kwargs)
            elif "Health" in sub_subdomain:
                return self._build_child_health_prompt(question, additional_data, raw, language, **kwargs)
            elif "Style" in sub_subdomain or "Compatibility" in sub_subdomain:
                return self._build_parenting_style_prompt(question, additional_data, raw, language, **kwargs)
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language, **kwargs)
            else:
                return self._build_general_prompt(question, additional_data, raw, language, **kwargs)

        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # =========================================================================
    # FALLBACK
    # =========================================================================

    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self._get_language_instruction_safe(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer. Answer the following parenting-related question.

QUESTION: "{question}"

OUTPUT FORMAT:
**GENERAL_ANSWER:** <Direct answer>
**ASTROLOGICAL_ANALYSIS:** <Flowing paragraphs>
**SUMMARY:** TELL CLIENT: <Actionable advice>
**REMEDIES_ASTROLOGICAL:** <Targeted remedies>
**REMEDIES_GENERAL:** <Lifestyle recommendations>

Always recommend medical consultation for health-related matters.
"""

    # =========================================================================
    # PROMISE PROMPT (PAR_CH_1)
    # FIX 8: Full GENERAL_ANSWER / ASTROLOGICAL_ANALYSIS / SUMMARY flow
    # =========================================================================

    def _build_promise_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        dob        = kwargs.get("dob", "")
        kp_state   = self._get_kp_state(additional_data)
        kp_points  = self._get_relevant_kp_points(additional_data, "promise")
        has_rel_kp = bool(kp_points)

        lords_data     = self._format_house_lords(additional_data)
        aspects_data   = self._format_house_aspects(additional_data)
        kp_data_str    = self._format_kp_data(additional_data, "promise") if has_rel_kp else ""
        remedy_targets = self._format_weak_planets_for_remedies(additional_data)  # FIX 5
        verdict_banner = self._format_kp_promise_verdict(additional_data, language)

        starters   = self._get_analysis_starters(language)
        kp_correct = self._get_example_text(language, "kp_correct")
        kp_wrong   = self._get_example_text(language, "kp_wrong")

        minor_block = self._build_developmental_override(dob, language) if is_minor else ""

        kp_section = ""
        if has_rel_kp and not is_minor:
            kp_section = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🔒 KP ANALYSIS DATA — PRE-COMPUTED — RESTATE ONLY, DO NOT RE-DERIVE    ║
╚═══════════════════════════════════════════════════════════════════════════╝

{kp_data_str}

✅ CORRECT: "{kp_correct}"
❌ WRONG:   {kp_wrong}
"""

        output_format = self.get_output_format(
            question_type="promise", language=language,
            has_timing=False, kp_available=has_rel_kp and not is_minor,
            is_minor=is_minor
        )

        return f"""
{lang_inst}

{verdict_banner}

{self.build_system_prompt(language, is_timing=False, question_type="promise")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: CHILDBIRTH PROMISE (PAR_CH_1)
Current Date: {today_str}
Weightage: KP 40% + Vedic 60%  (NO DASHA NEEDED)
KP State: {kp_state}
Has Relevant KP: {'YES' if has_rel_kp and not is_minor else 'NO — Use only Vedic analysis'}
Is Minor (Under 18): {'YES — DEVELOPMENTAL MODE' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

{remedy_targets}

{output_format}
"""

    # =========================================================================
    # TIMING PROMPT (PAR_CH_2)
    # FIX 6: Minor timing blank now explained
    # FIX 8: Full answer flow enforced
    # =========================================================================

    def _build_timing_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        dob        = kwargs.get("dob", "")
        kp_state   = self._get_kp_state(additional_data)
        is_blocked = self._is_blocked(additional_data)
        kp_points  = self._get_relevant_kp_points(additional_data, "timing")
        has_rel_kp = bool(kp_points)

        if is_minor:
            has_timing = False
            logger.warning(f"[PARENTING] Timing BLOCKED for minor (DOB: {dob})")
        else:
            has_timing = self._has_valid_timing_windows(additional_data)

        lords_data     = self._format_house_lords(additional_data)
        aspects_data   = self._format_house_aspects(additional_data)
        dasha_data     = self._format_current_dasha(additional_data)  # FIX 2
        kp_data_str    = "\n".join(kp_points) if kp_points and not is_minor else ""
        remedy_targets = self._format_weak_planets_for_remedies(additional_data)  # FIX 5
        verdict_banner = self._format_kp_promise_verdict(additional_data, language)

        if is_minor:
            # FIX 6: explicit explanation instead of blank
            timing_instruction = self._build_minor_timing_explanation(dob, language)
        elif is_blocked:
            blocked_message = self._get_example_text(language, "blocked_message")
            timing_instruction = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ⚠️ KP STATE IS BLOCKED — NO SPECIFIC TIMING TO PROVIDE                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

🚫 DO NOT provide specific timing windows or conception dates.
✅ DO mention current dasha for general context.
✅ DO recommend remedies and continued efforts.
✅ DO recommend professional medical consultation.

{dasha_data if dasha_data else "Current dasha information not available."}

MESSAGE TO CONVEY: "{blocked_message}"
"""
        elif has_timing:
            timing_data_formatted = self._format_timing_windows(additional_data)
            timing_instruction = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ✅ TIMING WINDOWS AVAILABLE — USE THESE DATES ONLY                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

{timing_data_formatted}

{dasha_data if dasha_data else ""}

INSTRUCTIONS:
- Use ONLY the dates above — never invent new dates
- BEST window = most favorable for conception/birth
- NEAREST window = soonest opportunity
- MUST mention BOTH windows and explain WHY each is favorable
- If needs_resonant_jump=true: include remedy guidance in SUMMARY
"""
        else:
            timing_unavail = self._get_example_text(language, "timing_unavailable")
            timing_instruction = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ⚠️ NO SPECIFIC TIMING CALCULATED                                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Childbirth is NOT blocked, but no specific timing windows were computed.

🚫 DO NOT invent dates or years.
✅ DO explain that favorable dasha periods should be monitored.
✅ DO recommend consulting for a detailed timing analysis.

{dasha_data if dasha_data else ""}

MESSAGE: "{timing_unavail}"
"""

        kp_section = ""
        if has_rel_kp and not is_minor:
            kp_section = f"""
KP TIMING CONTEXT (Pre-computed):
KP State: {kp_state}
{kp_data_str}
NOTE: Restate these findings only — do NOT add extra KP derivation.
"""

        output_format = self.get_output_format(
            question_type="timing", language=language,
            has_timing=has_timing and not is_blocked and not is_minor,
            kp_available=has_rel_kp and not is_minor,
            is_minor=is_minor
        )

        return f"""
{lang_inst}

{verdict_banner}

{self.build_system_prompt(language, is_timing=not is_minor, question_type="timing")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: CHILDBIRTH TIMING / BEST TIME TO CONCEIVE (PAR_CH_2)
Current Date: {today_str}
Weightage: {'DEVELOPMENTAL MODE — No timing' if is_minor else 'KP 20% + Vedic 50% + Dasha 30%'}
KP State: {kp_state}
Is Minor (Under 18): {'YES — TIMING COMPLETELY BLOCKED' if is_minor else 'NO'}
Has Relevant KP: {'YES' if has_rel_kp and not is_minor else 'NO — Use only Vedic analysis'}
Timing Windows: {'BLOCKED (Minor)' if is_minor else ('YES ✅' if has_timing else 'NO ❌')}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_instruction}

{kp_section}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

{remedy_targets}

{output_format}
"""

    # =========================================================================
    # CHILD HEALTH PROMPT (PAR_CH_3)
    # =========================================================================

    def _build_child_health_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        kp_points  = self._get_relevant_kp_points(additional_data, "health")
        has_rel_kp = bool(kp_points)
        kp_data_str    = self._format_kp_data(additional_data, "health") if has_rel_kp else ""
        verdict_banner = self._format_kp_promise_verdict(additional_data, language)
        remedy_targets = self._format_weak_planets_for_remedies(additional_data)  # FIX 5

        lords_data   = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)

        starters = self._get_analysis_starters(language)

        output_format = self.get_output_format(
            question_type="health", language=language,
            has_timing=False, kp_available=has_rel_kp,
            is_minor=is_minor
        )

        return f"""
{lang_inst}

{verdict_banner}

{self.build_system_prompt(language, is_timing=False, question_type="health")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: CHILD HEALTH (PAR_CH_3)
Current Date: {today_str}
Weightage: KP 25% + Vedic 75%  (NO DASHA NEEDED)
Is Minor (Under 18): {'YES' if is_minor else 'NO'}
Has Relevant KP: {'YES' if has_rel_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

╔═══════════════════════════════════════════════════════════════════════════╗
║  ⚠️ CHILD HEALTH SENSITIVITY RULES — MANDATORY                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
- NEVER induce fear or anxiety about the child's health
- Frame any concerns as "areas needing attention" — not "problems" or "defects"
- All health indications are TENDENCIES, not certainties
- ALWAYS recommend professional pediatric medical care

{kp_data_str if kp_data_str else ""}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

{remedy_targets}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (CHILD HEALTH — USE THESE EXACT LABELS):
═══════════════════════════════════════════════════════════════════════════════

**GENERAL_ANSWER:**
Reassuring tone. General health outlook for the child.

**ASTROLOGICAL_ANALYSIS:**
Write in FLOWING PARAGRAPHS.

PARAGRAPH 1 — 5th House (Child's constitution):
"{starters['vedic']}"
Analyze 5th house for the child's general health constitution.

PARAGRAPH 2 — Moon (Emotions and Mind):
Moon's position and sign → emotional health, mental resilience.

PARAGRAPH 3 — Areas of Attention (if any):
Present as tendencies only. "There may be a tendency toward [X] —
regular check-ups in this area are advisable."

**SUMMARY:**
TELL CLIENT: "[Reassuring advice + MUST recommend pediatric consultation]"

**REMEDIES_ASTROLOGICAL:**
[Target ONLY weak planets identified in Remedy Targets above]

**REMEDIES_GENERAL:**
General wellness. Always recommend professional medical care.

═══════════════════════════════════════════════════════════════════════════════
"""

    # =========================================================================
    # PARENTING STYLE PROMPT (PAR_CH_4)
    # FIX 3: aspects_data now included in f-string
    # =========================================================================

    def _build_parenting_style_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        lords_data   = self._format_house_lords(additional_data)
        aspects_data = self._format_house_aspects(additional_data)  # FIX 3: now used below

        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False, question_type="style")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PARENTING STYLE / PARENT-CHILD COMPATIBILITY (PAR_CH_4)
Current Date: {today_str}
Weightage: Vedic 90% + KP 10%  (NO DASHA NEEDED)
Is Minor (Under 18): {'YES — focus on developmental guidance' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else "House lords data not available."}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (PARENTING STYLE — USE THESE EXACT LABELS):
═══════════════════════════════════════════════════════════════════════════════

**GENERAL_ANSWER:**
Brief, constructive description of natural parenting style.

**ASTROLOGICAL_ANALYSIS:**
Write in FLOWING PARAGRAPHS.

PARAGRAPH 1 — Natural Parenting Style (5th Lord):
"{starters['vedic']}"
Analyze 5th lord's sign and house → natural approach to parenting?

PARAGRAPH 2 — Emotional Bonding (Moon):
Moon's sign and house → emotional connection style with child.

PARAGRAPH 3 — Guidance and Teaching (Jupiter):
Jupiter's placement → how this parent guides and shapes values.

PARAGRAPH 4 — Parent-Child Harmony:
Specific compatibility or tension patterns to be aware of.
Connect aspects data to parenting dynamic where relevant.

**SUMMARY:**
TELL CLIENT: "[Constructive guidance for harmonious parent-child relationship]"

**REMEDIES_ASTROLOGICAL:**
Focus on STRENGTHS — constructive guidance only, not criticism.

═══════════════════════════════════════════════════════════════════════════════
"""

    # =========================================================================
    # REMEDIES PROMPT
    # FIX 5: Now always passes remedy_targets for personalization
    # =========================================================================

    def _build_remedies_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        kp_state   = self._get_kp_state(additional_data)
        kp_points  = self._get_relevant_kp_points(additional_data, "general")
        has_rel_kp = bool(kp_points)
        kp_data_str    = self._format_kp_data(additional_data, "general") if has_rel_kp else ""
        lords_data     = self._format_house_lords(additional_data)
        verdict_banner = self._format_kp_promise_verdict(additional_data, language)
        remedy_targets = self._format_weak_planets_for_remedies(additional_data)  # FIX 5

        starters = self._get_analysis_starters(language)

        return f"""
{lang_inst}

{verdict_banner}

{self.build_system_prompt(language, is_timing=False, question_type="remedies")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PARENTING / CHILDBIRTH REMEDIES
Current Date: {today_str}
Weightage: KP 15% + Vedic 85%  (NO DASHA NEEDED)
KP State: {kp_state}
Is Minor (Under 18): {'YES — developmental focus' if is_minor else 'NO'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_data_str if kp_data_str else ""}

═══════════════════════════════════════════════════════════════════════════════
VEDIC REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}

{raw if raw else ""}

{remedy_targets}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (REMEDIES — USE THESE EXACT LABELS):
═══════════════════════════════════════════════════════════════════════════════

**GENERAL_ANSWER:**
What challenges exist and that remedies can meaningfully help.

**ASTROLOGICAL_ANALYSIS:**
Write in FLOWING PARAGRAPHS.

PARAGRAPH 1 — Identify Root Challenges:
"{starters['vedic']}"
Which planets or houses are creating obstacles? Why?
⚠️ ONLY discuss planets listed in Remedy Targets above.

PARAGRAPH 2 — Primary Remedy (MOST important):
Which planet needs strengthening most? What is the remedy and why?

PARAGRAPH 3 — Supporting Remedies:
2–3 additional helpful practices with brief explanations.

PARAGRAPH 4 — Spiritual/Lifestyle Support:
General lifestyle or spiritual practices.

**SUMMARY:**
TELL CLIENT: "[Priority order of remedies + MUST include medical consultation]"

**REMEDIES_ASTROLOGICAL:**
1. [Primary remedy — target weakest planet from Remedy Targets above]
2. [Secondary remedy]
3. [Tertiary remedy]
⚠️ Do NOT repeat generic remedy list if specific weak planets are identified above.

**REMEDIES_GENERAL:**
1. [Lifestyle guidance]
2. [Professional medical consultation — MANDATORY]

═══════════════════════════════════════════════════════════════════════════════
"""

    # =========================================================================
    # GENERAL PROMPT (Fallback)
    # =========================================================================

    def _build_general_prompt(
        self, question: str, additional_data: Dict, raw: str, language: str, **kwargs
    ) -> str:
        lang_inst  = self._get_language_instruction_safe(language)
        today_str  = datetime.now().strftime("%B %d, %Y")
        is_minor   = kwargs.get("is_minor", False)
        dob        = kwargs.get("dob", "")

        timing_keywords = [
            "when", "time", "timing", "year", "date",
            "कब", "समय", "delay", "विलंब", "conceive", "गर्भ"
        ]
        is_timing  = any(kw in question.lower() for kw in timing_keywords)
        kp_state   = self._get_kp_state(additional_data)
        is_blocked = self._is_blocked(additional_data)

        if is_minor:
            has_timing = False
        else:
            has_timing = self._has_valid_timing_windows(additional_data) and not is_blocked

        kp_points  = self._get_relevant_kp_points(additional_data, "general")
        has_rel_kp = bool(kp_points) and not is_minor

        lords_data     = self._format_house_lords(additional_data)
        aspects_data   = self._format_house_aspects(additional_data)
        remedy_targets = self._format_weak_planets_for_remedies(additional_data)  # FIX 5
        timing_data    = self._format_timing_windows(additional_data) if is_timing and has_timing else ""
        dasha_data     = self._format_current_dasha(additional_data) if is_timing else ""  # FIX 2
        kp_data_str    = self._format_kp_data(additional_data, "general") if has_rel_kp else ""
        verdict_banner = self._format_kp_promise_verdict(additional_data, language)

        blocked_message = self._get_example_text(language, "blocked_message")

        weightage = (
            "DEVELOPMENTAL MODE — No timing" if is_minor
            else ("KP 20% + Vedic 65% + Dasha 15%" if is_timing
                  else "KP 20% + Vedic 80%")
        )

        blocked_warning = ""
        if is_blocked and is_timing and not is_minor:
            blocked_warning = f"""
⚠️ KP STATE IS BLOCKED — DO NOT PROVIDE SPECIFIC TIMING.
🚫 Focus on: challenges, remedies, medical consultation.
Message: "{blocked_message}"
"""

        minor_block = (
            self._build_developmental_override(dob, language) if is_minor
            else ""
        )

        output_format = self.get_output_format(
            question_type="general", language=language,
            has_timing=has_timing, kp_available=has_rel_kp,
            is_minor=is_minor
        )

        return f"""
{lang_inst}

{verdict_banner}

{self.build_system_prompt(language, is_timing=is_timing and not is_minor, question_type="general")}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PARENTING (General)
Current Date: {today_str}
Type: {'DEVELOPMENTAL (Minor)' if is_minor else ('TIMING' if is_timing else 'NON-TIMING')}
Weightage: {weightage}
KP State: {kp_state}
Is Minor (Under 18): {'YES — TIMING BLOCKED' if is_minor else 'NO'}
Has Relevant KP: {'YES' if has_rel_kp else 'NO — Use only Vedic analysis'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_block}

{blocked_warning}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{timing_data if timing_data else ""}

{dasha_data if dasha_data else ""}

{kp_data_str if kp_data_str else ""}

{lords_data if lords_data else ""}

{aspects_data if aspects_data else ""}

{raw if raw else ""}

{remedy_targets}

{output_format}
"""
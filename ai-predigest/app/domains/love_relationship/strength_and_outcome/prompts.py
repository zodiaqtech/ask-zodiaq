"""
Strength and Outcome – LLM Prompts v9.5

CHANGES FROM v9.0:
✅ Removed Hinglish — get_language_instruction() now Hindi / English only
✅ LOVE_SO_2 (Marriage) + minor → FINAL_RESPONSE:: sentinel, LLM never called
✅ LOVE_SO_1 (Compatibility) + minor → LLM called in developmental mode (unchanged)
✅ _build_minor_final_response() added — same contract as BreakupPromptBuilder v9.5
✅ build_analysis_prompt() router updated — sentinel fires before sub-builder call

Minor treatment per question:

    LOVE_SO_1 — Compatibility Analysis and Advice
        Query type: NON_TIMING / NEUTRAL / STATUS
        Minor:      LLM still called, developmental reframe (no romantic content)
        Rationale:  Advisory question, safe to redirect as emotional maturity guidance

    LOVE_SO_2 — Love Leading to Marriage
        Query type: TIMING / POSITIVE / MANIFESTATION
        Minor:      FINAL_RESPONSE:: sentinel — LLM never called
        Rationale:  Marriage timing has no safe reframe for under-18

SENTINEL CONTRACT (LLM caller MUST implement):

    result = pb.build_analysis_prompt(...)
    if result.startswith("FINAL_RESPONSE::"):
        import json
        final = json.loads(result[len("FINAL_RESPONSE::"):])
        # Use final["general_answer"] directly — all other fields null
    else:
        llm_output = llm.generate(result)

All other logic (KP chain, house lords, timing windows, dasha, aspects,
output format, system prompt, anti-hallucination rules) — UNCHANGED from v9.0.
"""

import json
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
FINAL_RESPONSE_PREFIX = "FINAL_RESPONSE::"


class StrengthAndOutcomePromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Love Relationship → Strength And Outcome
    v9.5 — Sentinel for LOVE_SO_2 minor, developmental mode for LOVE_SO_1 minor
    """

    domain = "Love_Relationship"
    subtopic = "Strength And Outcome"

    ROMANCE_HOUSES = {5, 7, 11}
    MARRIAGE_HOUSES = {2, 7, 11}
    OBSTACLE_HOUSES = {6, 8, 12}

    # ==========================================================================
    # LANGUAGE — Hindi / English only. No Hinglish.
    # ==========================================================================

    def get_language_instruction(self, language: str) -> str:
        lang = language.lower() if language else "english"
        if lang == "hindi":
            return """
════════════════════════════════════════
LANGUAGE: HINDI (Devanagari Script)
════════════════════════════════════════
Respond in Hindi (Devanagari script) for main content.
Use English for technical terms (planets, houses, aspects, KP terms).
Example: "आपके रिश्ते में **7th house** की भूमिका महत्वपूर्ण है।"
Example: "**Venus** प्रेम और विवाह का कारक है।"
"""
        else:
            return """
════════════════════════════════════════
LANGUAGE: ENGLISH
════════════════════════════════════════
Respond in clear, compassionate English.
Keep technical terms clear and explain if needed.
"""

    # ==========================================================================
    # MINOR DETECTION
    # ==========================================================================

    def _detect_minor(self, dob: str) -> bool:
        if not dob:
            return False
        try:
            today = datetime.now()
            dob_dt = datetime.strptime(dob, "%d/%m/%Y")
            age = today.year - dob_dt.year - (
                (today.month, today.day) < (dob_dt.month, dob_dt.day)
            )
            return age < 18
        except Exception as e:
            logger.warning(f"[StrengthAndOutcome] Could not parse DOB for minor detection: {dob} → {e}")
            return False

    # ==========================================================================
    # MINOR SENTINEL — LOVE_SO_2 only
    # ==========================================================================

    def _build_minor_final_response(
        self,
        question: str,
        sub_subdomain: str,
        question_id: str,
        language: str,
        dob: str,
    ) -> str:
        """
        Returns FINAL_RESPONSE:: sentinel for LOVE_SO_2 when person is a minor.
        LLM is never called. Only general_answer populated, all other fields null.
        Language: Hindi or English only.
        """
        logger.warning(
            f"[StrengthAndOutcome v9.5] 🚨 MINOR SENTINEL | "
            f"DOB={dob} | QID={question_id} | Sub={sub_subdomain} | "
            f"Lang={language} | LLM will NOT be called."
        )

        lang = (language or "").lower()

        if lang == "hindi":
            general_answer = (
                "हम समझते हैं कि भविष्य के बारे में जानने की जिज्ञासा स्वाभाविक है। "
                "हालांकि, विवाह और प्रेम संबंधों का ज्योतिषीय विश्लेषण तथा समय-निर्धारण "
                "18 वर्ष से कम आयु के व्यक्तियों के लिए लागू नहीं है — "
                "यह सीमा पूरी तरह आपकी भलाई के लिए है।"
            )
        else:
            general_answer = (
                "We understand that curiosity about the future is completely natural. "
                "However, astrological analysis and timing for romantic relationships and marriage "
                "is not applicable for individuals under 18 years of age — "
                "this boundary exists entirely for your wellbeing."
            )

        payload = {
            "__minor_not_applicable__": True,
            "__language__": language,
            "__dob__": dob,
            "id": question_id,
            "sub_subdomain": sub_subdomain,
            "question": question,
            "general_answer": general_answer,
            "astrological_analysis": None,
            "summary": None,
            "timing_windows": None,
            "remedies": None,
            "overview_summary": None,
        }

        return FINAL_RESPONSE_PREFIX + json.dumps(payload, ensure_ascii=False)

    # ==========================================================================
    # ROUTER — sentinel fires here before any sub-builder is called
    # ==========================================================================

    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """
        Entry point. Returns either:
          - FINAL_RESPONSE:: sentinel string  (minor + LOVE_SO_2 → skip LLM)
          - Normal LLM prompt string          (all other cases)

        Caller MUST check:
            if result.startswith("FINAL_RESPONSE::"):
                final = json.loads(result[len("FINAL_RESPONSE::"):])
                # use final["general_answer"] directly
            else:
                llm_output = llm.generate(result)
        """
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            if additional_data is None:
                additional_data = {}
                kwargs["additional_data"] = additional_data

            dob = kwargs.get("dob")
            is_minor = self._detect_minor(dob)
            kwargs["is_minor"] = is_minor

            logger.warning(
                f"[StrengthAndOutcome v9.5] Minor Detection → DOB: {dob}, Is Minor: {is_minor}"
            )
            logger.info(
                f"[StrengthAndOutcome v9.5] → sub_subdomain: {sub_subdomain}, "
                f"language: {language}, is_minor: {is_minor}"
            )

            # ── SENTINEL: minor + marriage timing → never call LLM ────────────
            if is_minor and "Marriage" in sub_subdomain:
                return self._build_minor_final_response(
                    question=question,
                    sub_subdomain=sub_subdomain,
                    question_id=kwargs.get("question_id", "LOVE_SO_2"),
                    language=language,
                    dob=dob,
                )

            # ── Normal routing (minor + compatibility → developmental LLM) ────
            if "Compatibility" in sub_subdomain:
                return self._build_compatibility_prompt(
                    question, technical_points, meta, language, **kwargs
                )
            elif "Marriage" in sub_subdomain:
                return self._build_marriage_prompt(
                    question, technical_points, meta, language, **kwargs
                )
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(
                    question, technical_points, meta, language, **kwargs
                )
            else:
                return self._build_general_prompt(
                    question, technical_points, meta, language, **kwargs
                )

        except Exception as e:
            logger.error(f"[StrengthAndOutcome v9.5] Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)

    # ==========================================================================
    # Everything below is UNCHANGED from v9.0
    # (system prompt, all _format_* helpers, sub-builders, output format)
    # ==========================================================================

    def build_system_prompt(self) -> str:
        return """
You are an expert KP (Krishnamurti Paddhati) + Classical Vedic astrologer providing COMPASSIONATE and ACTIONABLE relationship guidance.

════════════════════════════════════════════════════════════════════════════════
AGE SAFETY RULE (ABSOLUTE — NO EXCEPTIONS)
════════════════════════════════════════════════════════════════════════════════

If person is under 18:
• NEVER predict romantic relationships or love timing
• NEVER suggest finding a partner or entering a relationship
• NEVER interpret dashas as relationship triggers
• Frame all analysis as emotional maturity and personality development
• Focus on: self-awareness, values, social skills, emotional intelligence
• Tone: developmental, encouraging, age-appropriate, future-oriented
• Ignore timing windows completely even if provided

════════════════════════════════════════════════════════════════════════════════
CORE KP PRINCIPLES (STRICTLY FOLLOW)
════════════════════════════════════════════════════════════════════════════════

KP Hierarchy of Result (MOST IMPORTANT RULE):

   SUB LORD      → PROMISE/DENIAL (Decides IF event happens — MOST IMPORTANT)
   STAR LORD     → RESULT TYPE (What kind of result)
   PLANET NATURE → FLAVOR ONLY (How it happens — NEVER overrides significations)

⚠️ CRITICAL EXAMPLES:
• Venus (benefic) signifies 6, 8, 12 → Result is OBSTACLES in love (not good!)
• Saturn (malefic) signifies 5, 7, 11 → Result is STABLE COMMITTED relationship (good!)

SIGNIFICATIONS ALWAYS WIN OVER PLANET NATURE.

KP Analysis Chain (USE THIS EXACT FORMAT):
   CSL [Planet] → in Nakshatra [Name] →
   Star Lord [Planet] → signifies houses [X,Y,Z] →
   Sub Lord [Planet] → signifies houses [A,B,C] →
   VERDICT: PROMISE/DENIAL based on SUB LORD significations

⚠️ Sub Lord is the FINAL DECIDER, not planet nature.

════════════════════════════════════════════════════════════════════════════════
CORRECT HOUSE DEFINITIONS (MEMORIZE)
════════════════════════════════════════════════════════════════════════════════

ROMANCE HOUSES: 5, 7, 11
• 5th: Love, attraction, romance
• 7th: Partnership, marriage, commitment
• 11th: Fulfillment, hopes, gains from partner

MARRIAGE HOUSES: 2, 7, 11
• 2nd: Family, spouse household, values
• 7th: Legal partnership, marriage
• 11th: Fulfillment of relationship goals

OBSTACLE HOUSES: 6, 8, 12
• 6th: Competition, conflict
• 8th: Sudden change, transformation, obstacles
• 12th: Loss, separation, hidden affairs

════════════════════════════════════════════════════════════════════════════════
PROMISE/DENIAL LOGIC (SUB LORD DECIDES)
════════════════════════════════════════════════════════════════════════════════

FOR 5TH CUSP (Romance):
• PROMISE: Sub-lord signifies 5, 7, 11 (2+ houses)
• DENIAL: Sub-lord signifies 6, 8, 12 strongly
• WEAK: Mixed significations

FOR 7TH CUSP (Marriage):
• PROMISE: Sub-lord signifies 2, 7, 11 (2+ houses)
• DENIAL: Sub-lord signifies 6, 8, 12 strongly
• WEAK: Mixed significations

════════════════════════════════════════════════════════════════════════════════
VEDIC-KP AGREEMENT (BE HONEST — DON'T FORCE AGREEMENT)
════════════════════════════════════════════════════════════════════════════════

Show agreement status EXPLICITLY:

✅ AGREEMENT: "Both KP and Vedic confirm [path]. Strong confidence."
⚠️ PARTIAL: "KP shows [X], Vedic leans [Y]. Mostly aligned but differences exist."
❌ CONFLICT: "KP indicates [X] but Vedic shows [Y]. Using KP for final verdict."

NEVER say "Vedic CONFIRMS KP" when they actually conflict.

════════════════════════════════════════════════════════════════════════════════
STRICT ANTI-HALLUCINATION RULES
════════════════════════════════════════════════════════════════════════════════

• DO NOT invent sub-lord significations not provided
• DO NOT guess promise/denial without actual data
• DO NOT mention aspects unless explicitly provided
• DO NOT assume yogas not present in input
• DO NOT invent specific timing dates not in the data
• If timing windows are provided, use ONLY those dates
• If data is missing → SAY SO CLEARLY, do not guess

════════════════════════════════════════════════════════════════════════════════
TIMING RULES
════════════════════════════════════════════════════════════════════════════════

When timing windows are provided:
1. ALWAYS mention BOTH windows: BEST (highest score) + NEAREST (soonest)
2. Explain WHY each is favorable based on dasha lords
3. Let USER choose: Wait for best = optimal | Act sooner = acceptable
4. If BEST = NEAREST → Emphasize: "Ideal timing! Best AND earliest opportunity!"

════════════════════════════════════════════════════════════════════════════════
ANALYSIS WEIGHTING
════════════════════════════════════════════════════════════════════════════════

TIMING QUESTION: KP 60% + Vedic 30% + Dasha 10%
NON-TIMING QUESTION: KP 70% + Vedic context 30% (no dasha)

KP conclusion ALWAYS leads the final recommendation.
Vedic explains ease/difficulty of achieving KP's promise.

════════════════════════════════════════════════════════════════════════════════
ACTIONABLE OUTPUT STYLE
════════════════════════════════════════════════════════════════════════════════

❌ WRONG: "7th house is moderate, 5th house shows mixed signals"
✅ RIGHT: "Marriage potential is strong. The 7th sub-lord connects to commitment
          houses — this is a genuine promise. Best timing: [exact dates]."

Write in FLOWING PARAGRAPHS for analytical sections.
Every astrological fact must be followed by its practical meaning.
NEVER list facts without interpretation.

════════════════════════════════════════════════════════════════════════════════
RELATIONSHIP SAFETY RULES
════════════════════════════════════════════════════════════════════════════════

• NEVER guarantee marriage success or failure
• NEVER make predictions that could cause emotional harm
• Frame challenges as TEMPORARY PHASES, not permanent blocks
• Love blocks are CORRECTABLE with effort and remedies
• Always maintain hope while being realistic
• Be supportive, compassionate, and constructive
"""

    def _format_kp_analysis(self, additional_data: Dict) -> Tuple[str, bool]:
        if not additional_data:
            return "", False

        kp_structured = additional_data.get("kp_love_analysis", {})

        if kp_structured and kp_structured.get("has_kp_data"):
            lines = ["═══════════════════════════════════════════════════════════"]
            lines.append("⭐ KP SYSTEM ANALYSIS (Pure Methodology)")
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
                lines.append("📍 CUSP SUB LORD CHAIN ANALYSIS (Relationship Houses):")
                lines.append("")
                priority_order = [7, 5, 11, 2, 8, 12]

                for house_num in priority_order:
                    if house_num not in csl_details:
                        continue

                    info = csl_details[house_num]
                    house_meaning = info.get("house_meaning", "Relationship")
                    csl = info.get("csl", "Unknown")
                    csl_flavor = info.get("csl_flavor", "")
                    csl_house = info.get("csl_house", "")
                    nakshatra = info.get("nakshatra", "")
                    star_lord = info.get("star_lord", "")
                    star_lord_signifies = info.get("star_lord_signifies", [])
                    sub_lord = info.get("sub_lord", "")
                    sub_lord_signifies = info.get("sub_lord_signifies", [])
                    promise_status = info.get("promise_status", "UNKNOWN")
                    interpretation = info.get("interpretation", "")

                    if promise_status == "PROMISE":
                        promise_marker = "✅ PROMISE"
                        promise_desc = "This house matter WILL manifest"
                    elif promise_status == "DENIAL":
                        promise_marker = "❌ DENIAL"
                        promise_desc = "Obstacles likely in this area"
                    elif promise_status == "WEAK_PROMISE":
                        promise_marker = "⚠️ WEAK PROMISE"
                        promise_desc = "May manifest with effort/patience"
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
                            romance_conn = sub_set & self.ROMANCE_HOUSES
                            marriage_conn = sub_set & self.MARRIAGE_HOUSES
                            obstacle_conn = sub_set & self.OBSTACLE_HOUSES
                            if romance_conn:
                                lines.append(f"  → Romance Houses Connected: {sorted(romance_conn)}")
                            if marriage_conn:
                                lines.append(f"  → Marriage Houses Connected: {sorted(marriage_conn)}")
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
                                current_line += (" " + word if current_line.strip() else "    " + word)
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
            lines.append("INSTRUCTIONS FOR KP INTERPRETATION:")
            lines.append("  1. Quote the full chain: CSL → Sub Lord → Significations")
            lines.append("  2. Base verdict on SUB LORD significations, NOT planet nature")
            lines.append("  3. Do NOT use fraction scoring (3/5, 2/4)")
            lines.append("  4. Use exact houses from data — never guess")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines), True

        kp_analysis = additional_data.get(f"{DOMAIN_PREFIX}_kp_analysis", {})
        if not kp_analysis:
            return "", False

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("⭐ KP RELATIONSHIP ANALYSIS DATA (Pre-computed)")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ Use this data for context. Do NOT override with LLM interpretation.")
        lines.append("")

        marriage_promise = kp_analysis.get("marriage_promise")
        if marriage_promise:
            emoji = "💍" if marriage_promise == "strong" else "💗" if marriage_promise == "moderate" else "⚠️"
            lines.append(f"  Marriage Promise: {emoji} {marriage_promise.upper()}")

        total_score = kp_analysis.get("total_score")
        if total_score is not None:
            lines.append(f"  Total Score: {total_score}")

        love_status = kp_analysis.get("love_status")
        if love_status:
            lines.append(f"  Love Status: {love_status}")

        love_to_marriage = kp_analysis.get("love_to_marriage")
        if love_to_marriage is not None:
            lines.append(f"  Love → Marriage Connection: {'✅ YES' if love_to_marriage else '❌ NO'}")

        marriage_from_love = kp_analysis.get("marriage_from_love")
        if marriage_from_love is not None:
            lines.append(f"  Marriage ← Love Connection: {'✅ YES' if marriage_from_love else '❌ NO'}")

        attraction = kp_analysis.get("attraction_score")
        if attraction is not None:
            lines.append(f"  Attraction Score: {attraction}")

        compatibility = kp_analysis.get("compatibility_score")
        if compatibility is not None:
            lines.append(f"  Compatibility Score: {compatibility}")

        sub_lord_5 = kp_analysis.get("sub_lord_5")
        if sub_lord_5:
            lines.append(f"  5th CSL (Romance): {sub_lord_5}")

        sub_lord_7 = kp_analysis.get("sub_lord_7")
        if sub_lord_7:
            lines.append(f"  7th CSL (Marriage): {sub_lord_7}")

        csl_5_state = kp_analysis.get("csl_5_state")
        if csl_5_state:
            lines.append(f"  CSL State: {csl_5_state}")

        notes = kp_analysis.get("notes", [])
        if notes:
            lines.append("")
            lines.append("  Key Notes:")
            for n in notes[:6]:
                lines.append(f"    • {n}")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════════════")

        has_data = any([marriage_promise, total_score, love_status, attraction, compatibility])
        return "\n".join(lines), has_data

    def _format_lagna_lord(self, lagna_info: Dict, house_lords_info: Dict = None) -> str:
        if not lagna_info and house_lords_info and 1 in house_lords_info:
            info = house_lords_info[1]
            lagna_info = {
                "lagna_sign": info.get("house_sign", "N/A"),
                "lagna_lord": info.get("lord", "N/A"),
                "lagna_lord_house": info.get("lord_in_house"),
                "lagna_lord_sign": info.get("lord_in_sign", "N/A"),
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
        lines.append("🎯 LAGNA (ASCENDANT) — RELATIONSHIP PERSONALITY")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append(f"Lagna Sign (1st House): {lagna_sign}")
        lines.append(f"Lagna Lord: {lord}")
        lines.append(f"Placed in: House {lord_house}, {lord_sign}")
        lines.append(f"Dignity: {dignity}")
        lines.append("")

        personality_map = {
            "Sun": {"trait": "Confident, seeks admiration and respect in love", "relationship": "Leadership-oriented, proud partner, values recognition", "approach": "Direct, proud approach — may need to balance ego"},
            "Moon": {"trait": "Emotionally expressive, nurturing, sensitive", "relationship": "Seeks emotional security, deeply feeling partner", "approach": "Intuitive, mood-driven, needs emotional reassurance"},
            "Mars": {"trait": "Passionate, direct, action-oriented in love", "relationship": "Intense attraction, competitive, can be impulsive", "approach": "Quick to pursue, energetic, may act before thinking"},
            "Mercury": {"trait": "Communicative, intellectual connection first", "relationship": "Witty, playful, values mental chemistry", "approach": "Analytical, talks through feelings, variety-seeking"},
            "Jupiter": {"trait": "Commitment-seeking, traditional values, growth together", "relationship": "Loyal, principled, seeks meaningful long-term bond", "approach": "Wise, ethical, long-term thinking"},
            "Venus": {"trait": "Romantic, harmony-loving, aesthetic sensibility", "relationship": "Values beauty, sensuality, and peace in relationships", "approach": "Charming, collaborative, deeply romantic"},
            "Saturn": {"trait": "Cautious, disciplined, slow to commit but deeply loyal", "relationship": "Serious approach to love, practical, long-term focus", "approach": "Patient, structured, relationships deepen over time"},
            "Rahu": {"trait": "Unconventional, drawn to unusual or foreign connections", "relationship": "Intense, obsessive at times, breaks patterns", "approach": "Ambitious in love, seeks unique experiences"},
            "Ketu": {"trait": "Detached, spiritual bonds, karmic connections", "relationship": "Intuitive, less materially attached in relationships", "approach": "Introspective, seeks deeper meaning beyond surface"},
        }

        lord_info = personality_map.get(lord, {"trait": "Unique relationship approach", "relationship": "Depends on specific chart placement", "approach": "Individual style"})

        lines.append(f"Relationship Personality: {lord_info['trait']}")
        lines.append(f"In Relationships: {lord_info['relationship']}")
        lines.append(f"Love Approach: {lord_info['approach']}")
        lines.append("")

        house_placement_meaning = {
            1: "Self-focused love, independent, may need to work on partnership give-and-take",
            2: "Security-driven love, family-oriented, values stability and shared resources",
            3: "Communication-based love, sibling/friend connections, short journeys together",
            4: "Home-loving, emotional depth, values domestic harmony",
            5: "Naturally romantic, creative love expression, children may be important",
            6: "Service-oriented partner, love through helping, health awareness in relationships",
            7: "Partnership-focused, committed, natural relationship orientation",
            8: "Deep transformation through love, intense bonds, hidden aspects in relationships",
            9: "Philosophy-based love, higher learning together, foreign or cultural connections",
            10: "Career and love may intertwine, public image matters in relationships",
            11: "Friendship-first love, social networks important, goal-oriented partnership",
            12: "Private/hidden love nature, spiritual connections, foreign or distant partners",
        }

        if lord_house and lord_house in house_placement_meaning:
            lines.append(f"Lagna Lord in House {lord_house}: {house_placement_meaning[lord_house]}")
            lines.append("")

        lines.append("⚠️ IMPORTANT NOTES:")
        lines.append("• This is Lagna (Ascendant), NOT Moon sign (Rashi)")
        lines.append("• Lagna lord shows fundamental approach to love and relationships")
        lines.append("• Do NOT confuse lagna sign with Moon sign")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
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
            lines.append("Let the user choose based on their situation.")
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
                    lines.append("    • Highest combined planetary alignment for relationship/marriage")
                    lines.append("    • Strongest love/commitment significations activated")
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
                if best and (best.get("dasha") == nearest.get("dasha") and best.get("start") == nearest.get("start")):
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
            lines.append("  • Explain WHY each is favorable for marriage/relationship")
            lines.append("  • Let user choose: Wait for best OR Act sooner")
            lines.append("  • If best = nearest, emphasize this is ideal")
            lines.append("═══════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    def _format_house_lords(self, additional_data: Dict) -> str:
        house_lords_info = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
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

        relationship_order = [7, 5, 11, 2, 8, 12, 1]
        house_meanings = {1: "Self/Personality", 2: "Family/Values/Household", 5: "Romance/Attraction", 7: "Partnership/Marriage", 8: "Intimacy/Transformation", 11: "Hopes/Fulfillment/Gains", 12: "Hidden Matters/Separation"}

        for house_num in relationship_order:
            if house_num not in house_lords_info:
                continue
            info = house_lords_info[house_num]
            priority = info.get("priority", "secondary")
            marker = "💍 PRIMARY" if priority == "primary" else "○ SECONDARY"
            meaning = house_meanings.get(house_num, "General")

            lines.append(f"{marker} — HOUSE {house_num} ({meaning})")
            lines.append(f"  Sign: {info.get('house_sign', 'N/A')}")
            lines.append(f"  Lord: {info.get('lord', 'N/A')}")
            lines.append(f"  Placed in: House {info.get('lord_in_house', 'N/A')}, {info.get('lord_in_sign', 'N/A')}")
            lines.append(f"  Dignity: {info.get('lord_dignity', 'N/A')}")
            lines.append(f"  Strength: {info.get('lord_strength_score', 0)}/100")

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

            strength = info.get("lord_strength_score", 0)
            if strength >= 70:
                lines.append("  ✅ Assessment: STRONG — Supports this house strongly")
            elif strength >= 40:
                lines.append("  ○ Assessment: MODERATE — Mixed results")
            else:
                lines.append("  ⚠️ Assessment: WEAK — Challenges in this area")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    def _format_house_aspects(self, additional_data: Dict) -> str:
        aspects_info = additional_data.get(f"{DOMAIN_PREFIX}_house_aspects", {})
        if not aspects_info:
            return ""

        has_aspects = any(
            aspects_info.get(h, {}).get("benefic_aspects") or aspects_info.get(h, {}).get("malefic_aspects")
            for h in [7, 5, 11, 2, 8, 12, 1]
        )
        if not has_aspects:
            return ""

        lines = ["═══════════════════════════════════════════════════════════"]
        lines.append("PLANETARY ASPECTS ON RELATIONSHIP HOUSES")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")

        for house_num in [7, 5, 11, 2, 8, 12, 1]:
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

    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        if not current_dasha:
            return ""
        try:
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "Unknown")
            end = date_range.get("end", "Unknown")

            dasha_mapping = {"Sa": "Saturn", "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter", "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu", "Saturn": "Saturn", "Sun": "Sun", "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury", "Jupiter": "Jupiter", "Venus": "Venus", "Rahu": "Rahu", "Ketu": "Ketu"}

            parts = [dasha_name]
            for sep in ["-", ">", "/"]:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(sep))
                parts = new_parts

            full_names = [dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()]
            formatted_dasha = " > ".join(full_names) if len(full_names) >= 2 else dasha_name

            return "\n".join([
                "═══════════════════════════════════════════════════════════",
                "CURRENT DASHA PERIOD (USE THIS — DON'T INVENT)",
                "═══════════════════════════════════════════════════════════",
                "",
                f"Current Dasha: {formatted_dasha}",
                f"Period: {start} to {end}",
                "",
                "⚠️ IMPORTANT:",
                "• This is the ACTUAL current dasha",
                "• Use for analyzing PRESENT relationship circumstances",
                "• For FUTURE planning, see UPCOMING DASHA PERIODS",
                "• Do NOT invent different dasha periods",
                "═══════════════════════════════════════════════════════════",
            ])
        except Exception as e:
            logger.error(f"Error formatting current dasha: {e}")
            return ""

    def _format_dasha_timeline(self, dasha_timeline: Optional[Dict]) -> str:
        if not dasha_timeline:
            return ""
        try:
            past = dasha_timeline.get("past_2_years", [])
            current = dasha_timeline.get("current", [])
            future = dasha_timeline.get("next_10_years", [])

            if not any([past, current, future]):
                return ""

            dasha_mapping = {"Sa": "Saturn", "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury", "Ju": "Jupiter", "Ve": "Venus", "Ra": "Rahu", "Ke": "Ketu"}

            def parse_dasha(name):
                parts = name.replace(">", "-").replace("/", "-").split("-")
                return " > ".join([dasha_mapping.get(p.strip(), p.strip()) for p in parts if p.strip()])

            lines = ["═══════════════════════════════════════════════════════════", "DASHA TIMELINE (For Relationship Planning)", "═══════════════════════════════════════════════════════════", ""]

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                for d in current[:3]:
                    dr = d.get("date_range", {})
                    lines.append(f"  • {parse_dasha(d.get('dasha_name', ''))}")
                    lines.append(f"    {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            if future:
                lines.append("⏭️ UPCOMING (Next 10 Years — For Relationship Planning):")
                lines.append("-" * 50)
                for i, d in enumerate(future[:15], 1):
                    dr = d.get("date_range", {})
                    marker = "⭐" if i <= 3 else "○"
                    lines.append(f"  {marker} {i}. {parse_dasha(d.get('dasha_name', ''))}")
                    lines.append(f"     {dr.get('start', '')} to {dr.get('end', '')}")
                lines.append("")

            lines += [
                "═══════════════════════════════════════════════════════════",
                "RELATIONSHIP DASHA GUIDELINES:",
                "• Venus → Highly favorable for love, romance, marriage",
                "• Jupiter → Commitment, blessings, long-term bond",
                "• Moon → Emotional connections, nurturing",
                "• Mars → Passion but can bring conflicts",
                "• Saturn → Delays but gives lasting, serious bonds",
                "• Rahu → Unconventional connections, intensity",
                "═══════════════════════════════════════════════════════════",
            ]

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    def _is_blocked(self, additional_data: Dict) -> bool:
        if not additional_data:
            return False
        kp_analysis = additional_data.get(f"{DOMAIN_PREFIX}_kp_analysis", {})
        if kp_analysis.get("marriage_promise") == "weak":
            return True
        if kp_analysis.get("csl_5_state") == "blocked":
            return True
        love_to_marriage = kp_analysis.get("love_to_marriage", True)
        marriage_from_love = kp_analysis.get("marriage_from_love", True)
        if not love_to_marriage and not marriage_from_love:
            house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
            if house_lords:
                weak_count = sum(1 for h in [5, 7] if house_lords.get(h, {}).get("lord_strength_score", 50) < 30)
                if weak_count >= 2:
                    return True
        return False

    def _get_analysis_instructions(self, kp_available: bool, question_type: str = "general", has_timing: bool = False, is_minor: bool = False, dob: str = None) -> str:
        if is_minor:
            return f"""
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨

Person is under 18. DOB: {dob}

STRICT RULES:
• Do NOT predict romantic relationships
• Do NOT suggest finding a partner
• Do NOT interpret dashas as relationship triggers
• Do NOT mention timing windows for love/marriage
• Do NOT use phrases like "will meet someone", "relationship will form"

INSTEAD interpret as:
• Emotional personality development
• Building social skills and emotional intelligence
• Understanding personal values and boundaries
• Foundation for healthy relationships in future
• Self-awareness and confidence building

Tone:
• Developmental
• Encouraging
• Age-appropriate
• Future-oriented

This override is MANDATORY. No exceptions.
"""
        base = """
**ANALYSIS APPROACH (FOLLOW THIS ORDER):**

**STEP 1: KP ANALYSIS (Primary)**
"""
        if kp_available:
            base += """
For each relationship cusp (5th, 7th, 11th), explain:
• CSL → Sub Lord → Significations
• Which houses does sub-lord signify?
• Is it PROMISE or DENIAL?
• Sub-lord significations decide, NOT planet nature

"""
        else:
            base += """
KP data not fully available. Proceed with Vedic primary analysis.

"""
        base += """
**STEP 2: VEDIC ANALYSIS (Secondary)**
• House lord placements and dignity
• Strength assessment (from provided data)
• Does Vedic AGREE or CONFLICT with KP?
• If conflict: State it honestly, use KP for events

"""
        if has_timing and not is_minor:
            base += """
**STEP 3: TIMING ANALYSIS (When data provided)**

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
        if question_type == "compatibility":
            base += """
**FOR COMPATIBILITY QUESTIONS:**
This is an ADVISORY question, not a timing prediction.
Focus on:
• Emotional patterns and communication styles
• Trust and loyalty indicators
• Practical relationship advice
• How to strengthen the bond
Do NOT predict exact marriage timing here.

"""
        return base

    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, question_type: str = "general", is_minor: bool = False) -> str:
        if is_minor:
            return """
OUTPUT FORMAT (DEVELOPMENTAL MODE — MINOR):

**GENERAL_ANSWER:**
<Compassionate, age-appropriate response about emotional development.>
<Focus on self-awareness, values, and future readiness.>
<NEVER mention romantic relationships or timing.>

**PERSONALITY_DEVELOPMENT_ANALYSIS:**

**A. EMOTIONAL PERSONALITY FOUNDATION:**
- Lagna lord approach: [personality description]
- Emotional strengths: [from chart]
- Areas for growth: [from chart]

**B. SOCIAL AND EMOTIONAL DEVELOPMENT:**
- Communication style: [from Mercury/Moon]
- How to build confidence: [practical]
- Building healthy relationship values: [age-appropriate]

**C. FUTURE READINESS (When of Age):**
- Natural relationship style: [general direction]
- Strengths to develop now: [practical steps]

**SUMMARY:**
<Encouraging, developmental focus.>
<Specific to their chart but age-appropriate.>

**REMEDIES_GENERAL:**
- [Focus on education, confidence, and emotional intelligence]
"""

        timing_section = ""
        if has_timing:
            timing_section = """
**F. TIMING RECOMMENDATION:**

⚠️ MANDATORY: Include BOTH timing options.

**🏆 BEST WINDOW (Highest Score):**
- Period: [exact dates from data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain dasha lords + relationship significations]
- Trade-off: May be further in future

**⏰ NEAREST WINDOW (Soonest):**
- Period: [exact dates from data]
- Dasha: [exact dasha from data]
- Score: [X]/100
- Why favorable: [explain]
- Trade-off: Not absolute best alignment

**👤 RECOMMENDATION:**
Choose BEST if: Can wait, want optimal results
Choose NEAREST if: Urgent need, acceptable results now

⚠️ If BEST = NEAREST (same window):
"🎯 IDEAL! Best alignment AND earliest opportunity!"
"""

        if question_type == "compatibility":
            return f"""
OUTPUT FORMAT — COMPATIBILITY ANALYSIS:

**GENERAL_ANSWER:**
<Clear, compassionate answer focusing on understanding.>
<Address emotional patterns and trust dynamics.>
<NO prediction of marriage timing here.>

**ASTROLOGICAL_ANALYSIS:**

**A. KP CONTEXT (For Understanding — if available):**
- Relationship promise status (from data)
- Love-to-marriage indicators

**B. VEDIC COMPATIBILITY ANALYSIS (Primary — 30% weight):**

Write in FLOWING PARAGRAPHS:

Paragraph 1 — Emotional Foundation:
• 5th house lord: romance capacity
• Moon condition: emotional communication style
• How they emotionally connect

Paragraph 2 — Partnership Dynamics:
• 7th house lord: long-term compatibility
• Venus condition: attraction and harmony
• Trust patterns from chart

Paragraph 3 — Practical Advice:
• What needs attention
• How to strengthen the bond
• Communication style to adopt

**C. DASHA CONTEXT (General Timing):**
• Current dasha relationship impact
• General upcoming favorable periods

**SUMMARY:**
<TELL CLIENT: "[Compassionate relationship advice]">

**REMEDIES_ASTROLOGICAL:**
- [Strengthen Venus and 7th lord]

**REMEDIES_GENERAL:**
- [Practical communication and connection advice]
"""

        if kp_available:
            return f"""
OUTPUT FORMAT (STRICT — FOLLOW EXACTLY):

**GENERAL_ANSWER:**
<Clear, compassionate answer in simple terms. NO jargon.>
<MUST address the actual question directly.>

**ASTROLOGICAL_ANALYSIS:**

**A. KP SYSTEM ANALYSIS (Primary — 60% weight):**

For EACH relevant cusp (5th, 7th, 11th):

**House [N] ([Meaning]):**
- CSL: [Planet] ([benefic/malefic] flavor — NOT the verdict!)
- Sub Lord: [Planet] ← DECIDES PROMISE/DENIAL
- Sub Lord Signifies: Houses [X, Y, Z]
- Romance Houses Connected: [from 5, 7, 11]
- Marriage Houses Connected: [from 2, 7, 11]
- Obstacle Houses Connected: [from 6, 8, 12]
- **VERDICT: PROMISE/DENIAL** based on sub-lord significations
- Why: [Explain how significations lead to verdict]

**B. VEDIC ANALYSIS (Secondary — 30% weight):**

**House Lords:**
- 7th Lord: [Planet, placement, dignity, strength]
- 5th Lord: [Planet, placement, dignity, strength]
- Venus: [Position, dignity, condition — love karaka]
- Jupiter: [Position, condition — commitment karaka]

**Vedic-KP Agreement Check:**
- If agree: "✅ Vedic CONFIRMS KP: [explanation]"
- If partial: "⚠️ PARTIAL: KP shows [X], Vedic [Y]. KP priority."
- If conflict: "❌ CONFLICT: KP [X], Vedic [Y]. Using KP for events."

**C. LAGNA LORD (Relationship Personality):**
- [Planet] as lagna lord
- Relationship approach: [description]

**D. RELATIONSHIP STRENGTH ASSESSMENT:**

| Indicator | Rating | Reasoning |
|-----------|--------|-----------|
| [Factor] | HIGH/MODERATE/WEAK | [from KP/Vedic] |

**E. DASHA CONTEXT:**
- Current: [dasha] — [relationship impact]
- Upcoming favorable: [dasha + dates]

{timing_section}

**SUMMARY:**
<2-3 sentences. Compassionate, actionable.>
<Include specific timing if available.>

**REMEDIES_ASTROLOGICAL:**
- [Target weak planets based on promise/denial status]

**REMEDIES_GENERAL:**
- [Practical relationship steps]
"""
        else:
            return f"""
OUTPUT FORMAT — VEDIC ONLY:

**GENERAL_ANSWER:**
<Clear, compassionate answer in simple terms.>

**ASTROLOGICAL_ANALYSIS:**

**A. LAGNA LORD (Relationship Personality):**
- Planet: [Name]
- Placed in: House [N]
- Relationship approach: [description]

**B. HOUSE LORD ANALYSIS (Primary):**

For each relationship house (7, 5, 11):
- Lord: [Planet]
- Placement: House [N]
- Dignity: [status]
- Strength: [X]/100
- Relationship Impact: [explanation]

**C. RELATIONSHIP STRENGTH ASSESSMENT:**

| Indicator | Suitability | Reasoning |
|-----------|-------------|-----------|
| Romance | [HIGH/MODERATE/LOW] | [based on 5th house] |
| Marriage | [HIGH/MODERATE/LOW] | [based on 7th house] |

**D. DASHA CONTEXT:**
- Current: [dasha]
- Relationship impact: [explanation]

{timing_section}

**SUMMARY:**
<Concise relationship outlook>

**REMEDIES:**
- [Strengthen weak house lords]
- [Practical steps]
"""

    def _build_fallback_prompt(self, question: str, language: str) -> str:
        lang_inst = self.get_language_instruction(language)
        return f"""
{lang_inst}

You are an expert Vedic astrologer specializing in relationships and marriage.

QUESTION: "{question}"

Provide a helpful, flowing analysis in paragraphs (not bullet lists).
End with a clear actionable statement.
Never guarantee marriage success or failure.
Be supportive and constructive.
"""

    def _build_compatibility_prompt(self, question: str, technical_points: List[str], meta: QueryMeta, language: str, **kwargs) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data = kwargs.get("additional_data", {})
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")
        lagna_info = additional_data.get("lagna_info", {})
        house_lords = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        kp_formatted, kp_available = self._format_kp_analysis(additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords)
        lords_formatted = self._format_house_lords(additional_data)
        aspects_formatted = self._format_house_aspects(additional_data)
        current_dasha = kwargs.get("current_dasha") or additional_data.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline") or additional_data.get("dasha_timeline")
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        analysis_instructions = self._get_analysis_instructions(kp_available, "compatibility", False, is_minor=is_minor, dob=dob)

        minor_section = ""
        if is_minor:
            minor_section = f"""
═══════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨
═══════════════════════════════════════════════════════════

Person is under 18. DOB: {dob}

STRICT RULES:
• Do NOT discuss romantic compatibility
• Do NOT suggest dating or relationships
• Do NOT predict love connections
• Do NOT frame analysis as romantic potential

INSTEAD focus on:
• Emotional personality traits
• Social skills and communication style
• Self-awareness and values development
• Foundation for healthy future relationships

Tone: Developmental, encouraging, age-appropriate
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Love Relationship
Subtopic: Strength And Outcome
Sub-subdomain: Compatibility Analysis and Advice
Query Type: ADVISORY (Understanding question, not timing)
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_section}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR COMPATIBILITY:
• This is ADVISORY — focus on understanding patterns, not predictions
• Emotional compatibility indicators from 5th/7th house lords
• Trust patterns from Venus and Moon conditions
• Communication styles and how to strengthen connection
• Practical relationship advice aligned with chart
• Be compassionate — never blame the person for challenges

{self.get_output_format(kp_available, False, "compatibility", is_minor)}
"""

    def _build_marriage_prompt(self, question: str, technical_points: List[str], meta: QueryMeta, language: str, **kwargs) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data = kwargs.get("additional_data", {})
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        is_blocked = self._is_blocked(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)
        lords_formatted = self._format_house_lords(additional_data)
        aspects_formatted = self._format_house_aspects(additional_data)

        timing_formatted = ""
        if not is_minor and not is_blocked and has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get("current_dasha") or additional_data.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline") or additional_data.get("dasha_timeline")
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        analysis_instructions = self._get_analysis_instructions(kp_available, "marriage", has_timing and not is_blocked and not is_minor, is_minor=is_minor, dob=dob)

        # NOTE: minor reaches here only via fallback (sentinel should have fired in router).
        # Guard retained defensively.
        minor_section = ""
        if is_minor:
            minor_section = f"""
═══════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨
═══════════════════════════════════════════════════════════

Person is under 18. DOB: {dob}

STRICT RULES:
• Do NOT predict marriage timing
• Do NOT mention when love will happen
• Do NOT interpret dashas as relationship triggers
• Do NOT suggest finding a partner now

INSTEAD interpret as:
• Emotional maturity and values development phase
• Foundation for healthy future relationships
• Long-term relationship readiness building
• Personality traits that will attract the right partner eventually

Tone: Developmental, encouraging, future-oriented
═══════════════════════════════════════════════════════════
"""

        blocked_section = ""
        if is_blocked and not is_minor:
            blocked_section = """
═══════════════════════════════════════════════════════════
⚠️ MARRIAGE CURRENTLY CHALLENGING — FOCUS ON STRENGTHENING
═══════════════════════════════════════════════════════════

The chart shows some challenges for marriage currently.

🚫 DO NOT provide specific timing windows or dates.
✅ DO mention current dasha period for general context.
✅ DO recommend strengthening the relationship.
✅ DO provide remedies to improve prospects.
✅ Frame challenges as TEMPORARY and CORRECTABLE.

MESSAGE: "Marriage challenges are temporary phases.
Focus on relationship strengthening and the right time will come."
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Love Relationship
Subtopic: Strength And Outcome
Sub-subdomain: Love Leading to Marriage
Query Type: {'TIMING' if has_timing and not is_blocked and not is_minor else 'NON_TIMING'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
Timing Windows Available: {'YES ✅' if has_timing and not is_blocked and not is_minor else 'NO ❌'}
Marriage Currently Blocked: {'YES' if is_blocked else 'NO'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_section}

{blocked_section}

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

SPECIFIC GUIDELINES FOR MARRIAGE TIMING:
• Check PROMISE STATUS from KP analysis first
• If 7th cusp = PROMISE → Marriage manifestation possible during favorable periods
• If 7th cusp = DENIAL → Obstacles likely; be honest but compassionate
• {'⚠️ TIMING WINDOWS PROVIDED — MUST USE EXACT DATES!' if has_timing and not is_blocked and not is_minor else ''}
• {'Mention BOTH best and nearest windows' if has_timing and not is_blocked and not is_minor else ''}
• Never guarantee marriage will or won't happen

{self.get_output_format(kp_available, has_timing and not is_blocked and not is_minor, "marriage", is_minor)}
"""

    def _build_remedies_prompt(self, question: str, technical_points: List[str], meta: QueryMeta, language: str, **kwargs) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data = kwargs.get("additional_data", {})
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        kp_formatted, kp_available = self._format_kp_analysis(additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)
        lords_formatted = self._format_house_lords(additional_data)
        aspects_formatted = self._format_house_aspects(additional_data)
        current_dasha = kwargs.get("current_dasha") or additional_data.get("current_dasha")
        current_dasha_block = self._format_current_dasha(current_dasha)
        kp_analysis = additional_data.get(f"{DOMAIN_PREFIX}_kp_analysis", {})
        kp_remedies = kp_analysis.get("remedies", [])
        kp_remedies_section = ""
        if kp_remedies:
            kp_remedies_section = "EVALUATOR-SUGGESTED REMEDIES:\n"
            kp_remedies_section += "\n".join(f"  • {r}" for r in kp_remedies)
            kp_remedies_section += "\n"

        minor_section = ""
        if is_minor:
            minor_section = f"""
═══════════════════════════════════════════════════════════
🚨 DEVELOPMENTAL MODE ACTIVE (MINOR) 🚨
═══════════════════════════════════════════════════════════

Person is under 18. DOB: {dob}

Frame all remedies as:
• Building confidence and emotional intelligence
• Strengthening personality and self-worth
• Education, focus, and skill building
• Foundation for healthy future relationships

Do NOT frame remedies as "to find love" or "for marriage".
═══════════════════════════════════════════════════════════
"""

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Love Relationship
Subtopic: Strength And Outcome
Sub-subdomain: Relationship Remedies
Query Type: NON_TIMING
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{minor_section}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{kp_remedies_section}

REMEDY GUIDELINES:

1. **Identify Weak Areas**:
   - Which cusps show DENIAL? (from KP if available)
   - Which house lords are weak? (from Vedic data)
   - 5th, 7th house lords — primary for relationship

2. **Current Dasha Lord Remedies**:
   - Strengthen current dasha lord for immediate support
   - Prepare for upcoming dasha lords (3 months before)

3. **Priority**:
   - Primary: Strengthen Venus (love/marriage karaka)
   - Secondary: Strengthen Jupiter (commitment karaka)
   - Tertiary: Strengthen 7th lord (marriage house)
   - Address obstacle connections (6th, 8th, 12th)

PLANETARY REMEDY GUIDE:
   VENUS:   Love, attraction — White Sapphire/Diamond, "Om Shukraya Namaha", Fridays
   JUPITER: Commitment, blessings — Yellow Sapphire, "Om Gurave Namaha", Thursdays
   MOON:    Emotions, sensitivity — Pearl, "Om Chandraya Namaha", Mondays
   MARS:    Passion, courage — Red Coral, "Om Mangalaya Namaha", Tuesdays

OUTPUT FORMAT:

**WEAK AREAS IDENTIFIED:**
- [From KP promise/denial analysis — if available]
- [From Vedic house lord analysis]

**REMEDIES_ASTROLOGICAL:**

**For [Planet] (affecting [house] — [area]):**
- Mantra: [specific mantra]
- Day: [best day for remedy]
- Gemstone: [if applicable, with caution]
- Charity: [specific charity]

**For Current Dasha Lord ([Planet]):**
- [Specific remedies]

**REMEDIES_GENERAL:**
- [Practical relationship/self-improvement steps]
- [Communication and emotional intelligence practices]
- [Auspicious timing for remedies]

**TIMELINE:**
- Start remedies on: [auspicious day/nakshatra]
- Duration: [recommended period]
"""

    def _build_general_prompt(self, question: str, technical_points: List[str], meta: QueryMeta, language: str, **kwargs) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)
        additional_data = kwargs.get("additional_data", {})
        is_minor = kwargs.get("is_minor", False)
        dob = kwargs.get("dob")
        lagna_info = additional_data.get("lagna_info", {})
        house_lords_raw = additional_data.get(f"{DOMAIN_PREFIX}_house_lords", {})
        timing_windows_data = additional_data.get(f"{DOMAIN_PREFIX}_timing_windows", {})
        has_timing = timing_windows_data.get("has_timing", False)
        is_blocked = self._is_blocked(additional_data)
        kp_formatted, kp_available = self._format_kp_analysis(additional_data)
        lagna_formatted = self._format_lagna_lord(lagna_info, house_lords_raw)
        lords_formatted = self._format_house_lords(additional_data)
        aspects_formatted = self._format_house_aspects(additional_data)
        timing_formatted = ""
        if not is_minor and not is_blocked and has_timing:
            timing_formatted = self._format_timing_windows(timing_windows_data)
        current_dasha = kwargs.get("current_dasha") or additional_data.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline") or additional_data.get("dasha_timeline")
        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)
        analysis_instructions = self._get_analysis_instructions(kp_available, "general", has_timing and not is_blocked and not is_minor, is_minor=is_minor, dob=dob)

        return f"""
{language_instruction}

{self.build_system_prompt()}

QUERY CONTEXT:
═══════════════════════════════════════════════════════════
Domain: Love Relationship
Subtopic: Strength And Outcome
Query Type: {meta.query_type if meta else 'UNKNOWN'}
CURRENT DATE: {today}
KP Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted}

{lagna_formatted}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{analysis_instructions}

GUIDELINES:
• Align answer with KP analysis if available
• Be honest about KP-Vedic agreement/conflict
• Never guarantee relationship outcomes
• Be compassionate and constructive
• Provide actionable guidance

{self.get_output_format(kp_available, has_timing and not is_blocked and not is_minor, "general", is_minor)}
"""
"""
Marriage Prospects LLM Prompts - ENHANCED v4.0

FIXES (v4.0 - KP Methodology Compliance):
✅ Proper KP terminology (CSL, signification, not "activation")
✅ Full KP chain logic: CSL → Star Lord → Sub Lord → Houses Signified
✅ 2-7-11 vs 1-6-10 promise/denial rule enforced
✅ Star Lord analysis required in all outputs
✅ KP strength hierarchy: Sub Lord > Star Lord > Occupation > Ownership
✅ Clear Promise vs Denial decision logic
✅ Dasha validation in proper KP format (signification-based)
✅ Correct KP terminology throughout (no "activation", no "custodian")

FIXES (v3.3):
✅ Consistent method signatures across all builders
✅ Safe fallback for missing base class methods
✅ All sub_subdomain routes properly handled
✅ Error-safe string formatting
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class MarriageProspectsPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Marriage Prospects subtopic.
    
    v4.0: Full KP methodology compliance
    
    Weightage:
    - PROMISE+TIMING: KP 70% + Vedic 30%
    - TIMING-ONLY: Vedic 65% + KP 25% + Dasha 10%
    - NON-TIMING: Vedic 85% + KP Facts 15% (No Dasha)
    """
    
    domain = "Marriage"
    subtopic = "Marriage Prospects"
    
    # ==========================================================================
    # SAFE LANGUAGE INSTRUCTION (Fallback if base method missing)
    # ==========================================================================
    
    def _get_language_instruction_safe(self, language: str) -> str:
        """Safe wrapper for language instruction - fallback if base method missing"""
        try:
            if hasattr(self, 'get_language_instruction'):
                return self.get_language_instruction(language)
        except Exception:
            pass
        
        # Fallback
        if language == "Hindi":
            return "IMPORTANT: Respond ONLY in Hindi (Devanagari script). Use Hindi for all analysis, interpretations, and recommendations."
        return "Respond in English."
    
    # ==========================================================================
    # SYSTEM PROMPT (v4.0 - KP Methodology Compliant)
    # ==========================================================================
    
    def build_system_prompt(self, language: str = "English", is_timing: bool = False, is_promise_timing: bool = False) -> str:
        """Build system prompt with KP methodology compliance"""

        if is_promise_timing:
            weightage_text = "PROMISE+TIMING QUESTION: KP 70% + Vedic 30%"
        elif is_timing:
            weightage_text = "TIMING QUESTION: Vedic 65% + KP 25% + Dasha 10%"
        else:
            weightage_text = "NON-TIMING QUESTION: Vedic 85% + KP Facts 15% (No Dasha needed)"
        
        return f"""You are an expert KP (Krishnamurti Paddhati) and Vedic astrologer specializing in marriage analysis.

**{weightage_text}**

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
- When you see "Mercury" ALWAYS write "बुध" in Hindi, NEVER "मंगल"
- When you see "Mars" ALWAYS write "मंगल" in Hindi, NEVER "बुध"

═══════════════════════════════════════════════════════════════════════════════
              🔬 MANDATORY KP METHODOLOGY RULES (CRITICAL!)
═══════════════════════════════════════════════════════════════════════════════

1. KP TERMINOLOGY — USE EXACT TERMS:
   ✅ "Cusp Sub Lord (CSL)" — NOT "custodian sub lord", NOT "कस्टोडियन"
   ✅ "signifies" or "संकेत करता है" — NOT "activates" or "सक्रिय करता है"
   ✅ "connected to" or "linked through star" — NOT "activates"
   ✅ "Nakshatra Lord" or "Star Lord" — NOT "Star Lord of occupant"
   ✅ Hindi: "कस्प उप स्वामी (CSL)" — for Cusp Sub Lord

2. KP CHAIN LOGIC — ALWAYS SHOW COMPLETE CHAIN:
   Every KP analysis MUST follow this exact chain:
   
   Cusp → Cusp Sub Lord (CSL) → CSL's Star Lord → Houses Signified → Promise/Denial
   
   For each planet, show the OCSS chain:
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  LEVEL 1 (Strongest): Planet's SUB LORD signifies which houses?        │
   │  LEVEL 2 (Strong):    Planet's STAR LORD (Nakshatra Lord) signifies?   │
   │  LEVEL 3 (Medium):    Planet OCCUPIES which house?                     │
   │  LEVEL 4 (Weakest):   Planet OWNS (rules) which houses?               │
   └─────────────────────────────────────────────────────────────────────────┘
   
   KP STRENGTH HIERARCHY (Always follow this order):
   Sub Lord > Star Lord > Occupation > Ownership

3. MARRIAGE PROMISE RULE (2-7-11 vs 1-6-10):
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  PROMISE HOUSES:  2 (family formation), 7 (spouse), 11 (fulfillment)  │
   │  DENIAL HOUSES:   1 (self over marriage), 6 (disputes/delay),         │
   │                   10 (separation/priority shift), 12 (loss)           │
   │  OBSTACLE HOUSES: 8 (transformation/hidden issues)                    │
   └─────────────────────────────────────────────────────────────────────────┘
   
   DECISION LOGIC:
   - If CSL signifies MORE promise houses (2,7,11) → MARRIAGE PROMISED
   - If CSL signifies MORE denial houses (1,6,10,12) → MARRIAGE DENIED/DELAYED
   - If mixed → MARRIAGE WITH STRUGGLE/DELAY
   - ALWAYS state this decision explicitly with reasoning

4. STAR LORD ANALYSIS — MANDATORY IN EVERY OUTPUT:
   ❌ NEVER say "Jupiter gives marriage" without showing HOW
   ✅ ALWAYS show: "Jupiter is in star of [X], [X] occupies house [Y], 
      owns houses [Z], hence Jupiter signifies houses [list]"
   
   Example of correct KP analysis:
   "7वें भाव का CSL गुरु है। गुरु केतु के नक्षत्र में है।
    केतु चौथे भाव में स्थित है और शनि (7, 8 भाव स्वामी) के
    नक्षत्र में है। अतः गुरु भाव 4, 5, 6, 7, 8, 9 को संकेतित
    करता है। इसमें भाव 7 विवाह भाव है (अनुकूल), लेकिन
    भाव 6 और 8 बाधा भाव हैं। अतः विवाह का वचन है,
    परंतु बाधाओं के साथ।"

5. DASHA VALIDATION — KP FORMAT:
   ❌ NEVER say "dasha activates houses"
   ✅ ALWAYS say "dasha lord SIGNIFIES houses through star lord chain"
   
   For each dasha lord, show:
   "[Planet] → Star Lord = [X] → [X] in house [Y], owns [Z]
    → Hence [Planet] signifies houses [list]
    → Promise houses (2/7/11): [which ones]
    → Denial houses (1/6/10/12): [which ones]
    → Verdict: [supports/obstructs] marriage"

═══════════════════════════════════════════════════════════════════════════════
                    🚨 ANTI-HALLUCINATION RULES (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

1. NEVER INVENT DATES OR TIMING
   - If no timing windows are provided, do NOT make up dates
   - Only mention specific dates if they appear in TIMING WINDOWS section
   - If timing data is missing, state: "विशिष्ट समय की गणना उपलब्ध नहीं है"

2. ONLY USE DATA PROVIDED
   - Do not invent planetary positions not in the data
   - Do not assume aspects not mentioned

3. DISTINGUISH FACTS FROM INTERPRETATION
   - Facts = from provided data
   - Interpretation = your astrological reasoning
   - Never present interpretation as computed fact

4. DASHA NAME TRANSLATION (CRITICAL!)
   ⚠️ Mercury = बुध (NOT मंगल!)
   ⚠️ Mars = मंगल (NOT बुध!)
   - COPY exactly from TIMING WINDOWS data, do not translate incorrectly

5. RAHU/KETU CHAIN CONTRADICTION RULE — MANDATORY:
   If you say "Rahu in house X causes obstacles" → then
   ANY planet in Rahu's star MUST be evaluated as:
   "This planet inherits Rahu's mixed signification. 
    Rahu in house 11 signifies 11 (favorable for marriage) BUT
    also carries its obstacle nature. Therefore [planet] in Rahu
    star gets BOTH the 11th house benefit AND Rahu's complication."
   
   ❌ NEVER say: "Rahu causes obstacle" AND "Saturn in Rahu star is favorable"
      without resolving WHY it's favorable despite Rahu's obstacle nature.
   ✅ ALWAYS say: "[Planet] in Rahu star inherits house [X] signification.
      Net effect: [favorable/mixed/unfavorable] because [reason]."

═══════════════════════════════════════════════════════════════════════════════
                    CRITICAL WRITING STYLE RULES
═══════════════════════════════════════════════════════════════════════════════

1. NEVER LIST FACTS WITHOUT INTERPRETATION
   ❌ "7th Lord Jupiter in 6th house. Retrograde. Benefic."
   ✅ "सातवें भाव का CSL गुरु है। गुरु केतु के नक्षत्र में स्थित है,
      और केतु शनि (7/8 भाव स्वामी) के नक्षत्र में है। इस श्रृंखला से
      गुरु भाव 7 को संकेतित करता है (विवाह अनुकूल), लेकिन भाव 6 और 8
      को भी संकेतित करता है (बाधाएं)। अतः विवाह का वचन है, परंतु
      संघर्ष के साथ।"

2. EVERY KP CLAIM NEEDS THE CHAIN PROOF
   - State the planet
   - Show its Star Lord
   - Show Star Lord's house and ownership
   - List all signified houses
   - Separate into promise (2/7/11) and denial (1/6/10/12) houses
   - Give clear verdict

3. WRITE IN FLOWING PARAGRAPHS, NOT BULLET LISTS

4. USE CORRECT KP TERMS:
   ✅ "संकेतित करता है" (signifies)
   ✅ "कस्प उप स्वामी (CSL)"
   ✅ "नक्षत्र स्वामी" (Star Lord)
   ✅ "उप स्वामी" (Sub Lord)
   ✅ "भाव स्वामी" (House Lord/Owner)
   ❌ "सक्रिय करता है" (activates) — NEVER USE
   ❌ "कस्टोडियन" — NEVER USE

═══════════════════════════════════════════════════════════════════════════════
                    VEDIC ANALYSIS MUST COVER
═══════════════════════════════════════════════════════════════════════════════

For each relevant house, weave into narrative:
• House lord position → What does this MEAN for the question?
• Benefic/Malefic nature → How does this AFFECT the outcome?
• Dignity status → Is the lord STRONG or WEAK and what's the impact?
• Aspects on lord → How do these MODIFY the results?
• Planets in house → What do they INDICATE?

═══════════════════════════════════════════════════════════════════════════════
                    KP RULES (When KP data present)
═══════════════════════════════════════════════════════════════════════════════

KP section MUST contain:
✅ 7th CSL name and its complete signification chain
✅ Promise state with 2-7-11 vs 1-6-10 decision logic
✅ Star Lord analysis for CSL
✅ Signified houses clearly categorized
✅ Clear verdict: PROMISED / DENIED / PROMISED WITH OBSTACLES

KP section must NOT contain:
❌ "Activation" language
❌ "Custodian" terminology
❌ Claims without chain proof
❌ Combust/Retrograde in KP section (those are Vedic concepts)

═══════════════════════════════════════════════════════════════════════════════
                    📊 OUTPUT STRUCTURE - FOLLOW THIS ORDER EXACTLY
═══════════════════════════════════════════════════════════════════════════════

1️⃣ **LAGNA LORD ANALYSIS** (10-15% of response - ALWAYS FIRST)
2️⃣ **KP PROMISE ANALYSIS WITH CHAIN LOGIC** (20-25% of response)
3️⃣ **HOUSE LORDS ANALYSIS** (Vedic Analysis - remaining weight)
4️⃣ **OTHER ANALYSES** (timing windows, spouse traits, etc.)

═══════════════════════════════════════════════════════════════════════════════
          🔒 MANDATORY LABELING — NEVER MIX KP AND VEDIC VERDICTS
═══════════════════════════════════════════════════════════════════════════════

RULE: Every KP-based verdict MUST be prefixed with "KP पद्धति के अनुसार,"
      Every Vedic-based verdict MUST be prefixed with "वैदिक पद्धति के अनुसार,"

✅ CORRECT:
  "वैदिक पद्धति के अनुसार, सातवें भाव के स्वामी गुरु षष्ठ भाव में हैं — यह विलंब का संकेत है।"
  "KP पद्धति के अनुसार, 7वें भाव का CSL शनि है जो 2, 7, 11 को संकेतित करता है — विवाह का वचन है।"

❌ FORBIDDEN:
  "KP पद्धति के अनुसार, गुरु षष्ठ भाव में हैं..." (This is Vedic placement, NOT KP verdict)
  Any KP chain analysis without the label "KP पद्धति के अनुसार"

KP SECTION MUST START WITH: "KP पद्धति के अनुसार,"
VEDIC SECTION MUST START WITH: "वैदिक पद्धति के अनुसार,"

═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def _get_kp_availability(self, additional_data: Dict) -> bool:
        """Check if KP promise data is available"""
        if not additional_data:
            return False
        promise_data = additional_data.get("promise", {})
        return bool(promise_data and promise_data.get("state"))
    
    def _format_kp_data(self, additional_data: Dict) -> str:
        """Format KP promise analysis - DATA ONLY"""
        if not additional_data:
            return ""
        
        promise_data = additional_data.get("promise", {})
        if not promise_data or not promise_data.get("state"):
            return ""
        
        state = promise_data.get("state", "unknown")
        csl = promise_data.get("csl", promise_data.get("sub_lord", ""))
        csl_significations = promise_data.get("csl_significations", {})
        
        lines = ["KP DATA:"]
        lines.append(f"• 7th Cusp Sub Lord (CSL): {csl}")
        lines.append(f"• Promise State: {state.upper()}")
        lines.append(f"• Promise Score: {promise_data.get('promise_score', 'N/A')}")
        lines.append(f"• Obstacle Score: {promise_data.get('obstacle_score', 'N/A')}")
        
        if csl_significations:
            promise_sig = csl_significations.get("promise", [])
            obstacle_sig = csl_significations.get("obstacle", [])
            if promise_sig:
                lines.append(f"• Promise houses signified (2/7/11): {promise_sig}")
            if obstacle_sig:
                lines.append(f"• Obstacle/denial houses signified: {obstacle_sig}")
        
        return "\n".join(lines)
    
    def _dasha_to_hindi(self, dasha_str: str) -> str:
        """Convert dasha string to Hindi"""
        if not dasha_str:
            return ""
        
        hindi_mapping = {
            'Saturn': 'शनि', 'Sun': 'सूर्य', 'Moon': 'चंद्र',
            'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु',
            'Venus': 'शुक्र', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        
        parts = dasha_str.replace(" > ", "-").replace(">", "-").split("-")
        hindi_parts = []
        
        for part in parts:
            part = part.strip()
            hindi_parts.append(hindi_mapping.get(part, part))
        
        return "-".join(hindi_parts)
    
    def _format_timing_windows(self, additional_data: Dict) -> str:
        """Format timing windows with KP Significator Proof"""
        if not additional_data:
            return "NO_TIMING_DATA"
        
        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data or not timing_data.get('has_timing'):
            return "NO_TIMING_DATA"
        
        try:
            best = timing_data.get('best_window', {})
            nearest = timing_data.get('nearest_window', {})
            all_windows = timing_data.get('all_favorable', [])
            marriage_proof = timing_data.get('marriage_proof', {})
            
            if not best and not nearest:
                return "NO_TIMING_DATA"
            
            lines = ["╔═══════════════════════════════════════════════════════════════════════════════╗"]
            lines.append("║  💒 MARRIAGE TIMING WINDOWS WITH KP SIGNIFICATION PROOF                      ║")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")
            
            # Dasha name reference
            lines.append("  ⚠️ DASHA NAME REFERENCE:")
            lines.append("  Mercury = बुध (NOT मंगल!) | Mars = मंगल (NOT बुध!)")
            lines.append("")
            
            # KP Significator Table
            if marriage_proof and marriage_proof.get('significator_table'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  📊 KP SIGNIFICATION TABLE FOR MARRIAGE                                     ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append("  Promise Houses: 2 (family), 7 (marriage), 11 (fulfillment)")
                lines.append("  Denial Houses: 1 (self), 6 (disputes), 10 (separation), 12 (loss)")
                lines.append("  Legend: O = Occupies, L = Owns/Lords, S = Through Star Lord")
                lines.append("")
                
                for entry in marriage_proof['significator_table'][:7]:
                    planet = entry['planet']
                    promise_houses = ', '.join(entry.get('signifies_2_7_11', ['None']))
                    obstacle_houses = ', '.join(entry.get('signifies_6_8_12', ['None']))
                    promise_score = entry.get('promise_score', 0)
                    obstacle_score = entry.get('obstacle_score', 0)
                    is_key = "💒 Marriage Karaka" if entry.get('is_marriage_karaka') else ("✅ Benefic" if entry.get('is_benefic') else "○")
                    
                    lines.append(f"  {planet}: Signifies 2/7/11 via [{promise_houses}] | "
                                f"Signifies 6/8/12 via [{obstacle_houses}] | "
                                f"Promise={promise_score} Obstacle={obstacle_score} | {is_key}")
                
                lines.append("")
            
            # Timing Proof with proper KP terminology
            if marriage_proof and marriage_proof.get('timing_proofs'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  📊 DASHA SIGNIFICATION PROOF (Why these periods favor marriage)             ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                
                for proof in marriage_proof['timing_proofs'][:3]:
                    strength_icon = "🟢" if proof.get('promise_strength') == "STRONG" else ("🟡" if proof.get('promise_strength') == "MODERATE" else "🟠")
                    lines.append(f"  {strength_icon} {proof['dasha']} ({proof['period']})")
                    lines.append(f"     Score: {proof['score']:.1f}/100 | Strength: {proof.get('promise_strength', 'N/A')}")
                    
                    if proof.get('house_linkage'):
                        lines.append(f"     Houses Signified:")
                        for linkage in proof['house_linkage']:
                            lines.append(f"       • {linkage}")
                    
                    if proof.get('dasha_lords'):
                        lines.append(f"     Dasha Lord Significations (through Star Lord chain):")
                        for lord in proof['dasha_lords']:
                            if lord.get('signifies_promise_houses'):
                                how_str = "; ".join(lord.get('how', [])[:2])
                                lines.append(f"       • {lord['planet']}: signifies houses {lord['signifies_promise_houses']} ({how_str})")
                    
                    karaka_status = []
                    if proof.get('venus_involved'):
                        karaka_status.append("Venus (marriage karaka)")
                    if proof.get('jupiter_involved'):
                        karaka_status.append("Jupiter (benefic)")
                    
                    if karaka_status:
                        lines.append(f"     ✅ Key planets involved: {', '.join(karaka_status)}")
                    lines.append("")
            
            # Best Window
            if best:
                best_dasha = best.get('dasha', 'N/A')
                best_dasha_hindi = self._dasha_to_hindi(best_dasha)
                
                lines.append("🏆 BEST WINDOW (Highest Marriage Score):")
                lines.append(f"  Dasha (English): {best_dasha}")
                lines.append(f"  Dasha (Hindi):   {best_dasha_hindi}")
                lines.append(f"  ⚠️ USE THESE EXACT NAMES!")
                lines.append(f"  Period: {best.get('start', 'N/A')} to {best.get('end', 'N/A')}")
                lines.append(f"  Score: {best.get('final_score', 0):.1f}/100")
                lines.append(f"  Age: {best.get('age_at_start', 'N/A')} years")
                lines.append("")
            
            # Nearest Window
            if nearest:
                nearest_dasha = nearest.get('dasha', 'N/A')
                nearest_dasha_hindi = self._dasha_to_hindi(nearest_dasha)
                
                lines.append("⏰ NEAREST FAVORABLE WINDOW:")
                lines.append(f"  Dasha (English): {nearest_dasha}")
                lines.append(f"  Dasha (Hindi):   {nearest_dasha_hindi}")
                lines.append(f"  Period: {nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}")
                lines.append(f"  Score: {nearest.get('final_score', 0):.1f}/100")
                lines.append(f"  Age: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")
                
                if best and (best.get('dasha') == nearest.get('dasha') and 
                            best.get('start') == nearest.get('start')):
                    lines.append("  ✅ Best and Nearest windows are THE SAME!")
                lines.append("")
            
            # Other Windows
            if len(all_windows) > 2:
                lines.append("📋 OTHER FAVORABLE WINDOWS:")
                for i, window in enumerate(all_windows[:5], 1):
                    lines.append(f"  {i}. {window.get('dasha', 'N/A')}: {window.get('start', 'N/A')} to {window.get('end', 'N/A')} (Score: {window.get('final_score', 0):.1f})")
                lines.append("")
            
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("⚠️ CRITICAL INSTRUCTIONS FOR TIMING RESPONSE:")
            lines.append("- Use 'signifies' (संकेतित करता है), NOT 'activates' (सक्रिय करता है)")
            lines.append("- Show Star Lord chain for each dasha lord")
            lines.append("- Use ONLY dates from timing windows above")
            lines.append("- Mercury = बुध (NOT मंगल!), Mars = मंगल (NOT बुध!)")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error formatting timing: {e}")
            return "NO_TIMING_DATA"

    def _format_event_fructification(self, additional_data):
        """
        v4.1 NEW: Format the KP Event Fructification 4-condition checklist.
        This is the mechanism that determines IF and WHEN marriage will happen.
        
        ADD this method to MarriageProspectsPromptBuilder.
        """
        if not additional_data:
            return ""
        
        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data:
            return ""
        
        ef = timing_data.get("event_fructification", {})
        if not ef or not ef.get("conditions"):
            return ""
        
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  🔬 KP EVENT FRUCTIFICATION MECHANISM (फलित सूत्र)                           ║")
        lines.append("║  ⚠️ MANDATORY: Include ALL 4 conditions in your response                     ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("KP astrology requires 4 conditions for an event to fructify (happen).")
        lines.append("All 4 must be checked and reported:")
        lines.append("")
        
        for i, cond in enumerate(ef["conditions"], 1):
            icon = "✅" if cond["met"] else "❌"
            lines.append(f"  ┌── CONDITION {i}: {cond['name_hindi']} ──")
            lines.append(f"  │ {icon} Status: {'FULFILLED' if cond['met'] else 'NOT FULFILLED'}")
            lines.append(f"  │ {cond['explanation']}")
            
            # For DBA condition, show each lord's chain
            if cond["name"] == "DBA_SIGNIFICATION":
                for lord_chain in cond["details"].get("dba_lords", []):
                    planet = lord_chain.get("planet", "Unknown")
                    chain = lord_chain.get("chain_narrative", "N/A")
                    promise = lord_chain.get("promise_houses", [])
                    negative = lord_chain.get("negative_houses", [])
                    
                    lines.append(f"  │")
                    lines.append(f"  │ ┌─ {planet}:")
                    lines.append(f"  │ │  Chain: {chain}")
                    lines.append(f"  │ │  Promise houses (2/7/11): {promise}")
                    lines.append(f"  │ │  Obstacle houses: {negative}")
                    lines.append(f"  │ └─")
                
                combined = cond["details"].get("combined_promise_houses", [])
                needed = cond["details"].get("houses_needed", 2)
                lines.append(f"  │")
                lines.append(f"  │ Combined DBA signification of 2/7/11: {combined}")
                lines.append(f"  │ Need ≥{needed} of {{2,7,11}} → {'MET' if cond['met'] else 'NOT MET'}")
            
            # For PROMISE condition, show CSL chain
            if cond["name"] == "PROMISE":
                chain = cond["details"].get("chain_narrative", "")
                if chain:
                    lines.append(f"  │")
                    lines.append(f"  │ CSL Chain: {chain}")
            
            # For TRANSIT condition
            if cond["name"] == "TRANSIT_TRIGGER":
                rp_sigs = cond["details"].get("rp_signifying_marriage", [])
                if rp_sigs:
                    for rp in rp_sigs:
                        lines.append(f"  │ {rp['planet']}: signifies houses {rp['promise_houses']}")
            
            # For RP MATCH condition
            if cond["name"] == "RULING_PLANET_MATCH":
                matching = cond["details"].get("matching", [])
                lines.append(f"  │ Matching RP in DBA: {', '.join(matching) if matching else 'None'}")
            
            lines.append(f"  └──")
            lines.append("")
        
        total = ef.get("total_score", 0)
        verdict_icon = ef.get("verdict_icon", "")
        verdict_hindi = ef.get("verdict_hindi", "")
        
        lines.append("  ═══════════════════════════════════════════════════════════")
        lines.append(f"  TOTAL: {total}/4 conditions met")
        lines.append(f"  VERDICT: {verdict_icon} {verdict_hindi}")
        lines.append("  ═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ LLM: You MUST include this fructification checklist.")
        lines.append("   Write as: 'KP फलित सूत्र:' followed by all 4 conditions.")
        lines.append("   For each, show the chain proof in Hindi.")
        lines.append("   End with: '[X]/4 शर्तें पूरी → [verdict]'")
        lines.append("")
        
        return "\n".join(lines)
    
    def _has_valid_timing_windows(self, additional_data: Dict) -> bool:
        """Check if valid timing windows exist"""
        if not additional_data:
            return False
        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data or not timing_data.get('has_timing'):
            return False
        return bool(timing_data.get('best_window') or timing_data.get('nearest_window'))

    def _format_best_nearest_timing_instruction(self, additional_data: Dict) -> str:
        """
        Format a mandatory LLM instruction block that requires explicit
        BEST TIMING and NEAREST TIMING sections with reasoning in the output.

        This ensures the LLM always presents both windows clearly with why
        each is recommended.
        """
        if not additional_data:
            return ""

        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""

        best = timing_data.get("best_window", {})
        nearest = timing_data.get("nearest_window", {})
        marriage_proof = timing_data.get("marriage_proof", {})
        timing_proofs = marriage_proof.get("timing_proofs", []) if marriage_proof else []

        if not best and not nearest:
            return ""

        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  🎯 MANDATORY TIMING OUTPUT STRUCTURE — INCLUDE BOTH SECTIONS IN RESPONSE    ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("Your timing response MUST have two clearly labeled sections:")
        lines.append("")

        # Build WHY reasoning for best window
        best_dasha = best.get("dasha", "N/A") if best else "N/A"
        best_start = best.get("start", "N/A") if best else "N/A"
        best_end = best.get("end", "N/A") if best else "N/A"
        best_score = best.get("final_score", 0) if best else 0
        best_age = best.get("age_at_start", "N/A") if best else "N/A"

        best_proof = next((p for p in timing_proofs if p.get("dasha") == best_dasha), None)
        best_why_parts = []
        if best_proof:
            for lord in best_proof.get("dasha_lords", []):
                ph = lord.get("signifies_promise_houses", [])
                if ph:
                    best_why_parts.append(f"{lord['planet']} signifies {ph}")
            if best_proof.get("venus_involved"):
                best_why_parts.append("Venus (marriage karaka) is active")
            if best_proof.get("jupiter_involved"):
                best_why_parts.append("Jupiter (benefic) supports")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("SECTION 1: सर्वश्रेष्ठ विवाह काल (BEST MARRIAGE TIMING)")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append(f"  Dasha: {best_dasha}")
        lines.append(f"  Period: {best_start} to {best_end}")
        lines.append(f"  Score: {best_score:.1f}/100 (HIGHEST among all windows)")
        lines.append(f"  Age at start: {best_age} years")
        lines.append("")
        lines.append("  WHY IS THIS THE BEST? (You MUST explain all of these):")
        if best_why_parts:
            for reason in best_why_parts:
                lines.append(f"    ✅ {reason}")
        else:
            lines.append(f"    ✅ This dasha lords collectively signify marriage houses (2/7/11)")
        lines.append(f"    ✅ Score {best_score:.1f} is the HIGHEST among all calculated windows")
        lines.append("")
        lines.append("  YOUR RESPONSE MUST INCLUDE THIS PARAGRAPH:")
        lines.append(f"  'सर्वश्रेष्ठ विवाह काल: {self._dasha_to_hindi(best_dasha)} की दशा ({best_start} से {best_end}) सबसे")
        lines.append(f"   अनुकूल है क्योंकि [explain WHY using KP chain above]. इस अवधि में")
        lines.append(f"   विवाह की संभावना सर्वाधिक है।'")
        lines.append("")

        # Build WHY for nearest window
        nearest_dasha = nearest.get("dasha", "N/A") if nearest else "N/A"
        nearest_start = nearest.get("start", "N/A") if nearest else "N/A"
        nearest_end = nearest.get("end", "N/A") if nearest else "N/A"
        nearest_score = nearest.get("final_score", 0) if nearest else 0
        nearest_age = nearest.get("age_at_start", "N/A") if nearest else "N/A"

        same_as_best = (best_dasha == nearest_dasha and best_start == nearest_start) if best and nearest else False

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("SECTION 2: निकटतम अनुकूल काल (NEAREST FAVORABLE TIMING)")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        if same_as_best:
            lines.append(f"  ✅ BEST and NEAREST windows are THE SAME!")
            lines.append(f"  Dasha: {nearest_dasha}")
            lines.append(f"  Period: {nearest_start} to {nearest_end}")
            lines.append("")
            lines.append("  YOUR RESPONSE MUST SAY:")
            lines.append(f"  'निकटतम अनुकूल काल और सर्वश्रेष्ठ काल एक ही है: {self._dasha_to_hindi(nearest_dasha)} दशा ({nearest_start} से {nearest_end})।'")
        else:
            nearest_proof = next((p for p in timing_proofs if p.get("dasha") == nearest_dasha), None)
            nearest_why_parts = []
            if nearest_proof:
                for lord in nearest_proof.get("dasha_lords", []):
                    ph = lord.get("signifies_promise_houses", [])
                    if ph:
                        nearest_why_parts.append(f"{lord['planet']} signifies {ph}")

            lines.append(f"  Dasha: {nearest_dasha}")
            lines.append(f"  Period: {nearest_start} to {nearest_end}")
            lines.append(f"  Score: {nearest_score:.1f}/100")
            lines.append(f"  Age at start: {nearest_age} years")
            lines.append(f"  NOTE: This starts sooner than the best window ({best_start})")
            lines.append("")
            lines.append("  WHY IS THIS NEAREST FAVORABLE? (You MUST explain):")
            if nearest_why_parts:
                for reason in nearest_why_parts:
                    lines.append(f"    ✅ {reason}")
            else:
                lines.append(f"    ✅ This is the earliest dasha that activates marriage houses")
            lines.append(f"    ℹ️ Score {nearest_score:.1f} (lower than best {best_score:.1f}) — favorable but not peak")
            lines.append("")
            lines.append("  YOUR RESPONSE MUST INCLUDE THIS PARAGRAPH:")
            lines.append(f"  'निकटतम अनुकूल काल: {self._dasha_to_hindi(nearest_dasha)} की दशा ({nearest_start} से {nearest_end}) निकटतम")
            lines.append(f"   अवसर है क्योंकि [explain WHY]. यह सर्वश्रेष्ठ काल नहीं है परंतु विवाह की")
            lines.append(f"   संभावना इसमें भी है।'")

        lines.append("")
        lines.append("⚠️ CRITICAL: Both sections MUST appear in your response with clear Hindi headings:")
        lines.append("   '🏆 सर्वश्रेष्ठ विवाह काल:' and '⏰ निकटतम अनुकूल काल:'")
        lines.append("   Each section MUST explain WHY using KP chain data above.")
        lines.append("")

        return "\n".join(lines)
    
    def _format_csl_significations_summary(self, additional_data: Dict) -> str:
        """
        Emit a VERBATIM-LOCKED block of pre-computed CSL significations.

        The LLM MUST copy the exact house lists — it must NOT re-derive them.
        This prevents inconsistent signification lists across different sub-subdomain
        answers (e.g. Jupiter signifies [2,7,1,3] in Q1 but [2,7,8] in Q2).

        Strategy:
        - Build a ready-made Hindi sentence for each CSL the LLM must copy literally.
        - Include the full chain_narrative so the LLM has proof-of-computation.
        - Mark everything with ⚠️ COPY VERBATIM so it cannot be ignored.
        """
        if not additional_data:
            return ""

        kp_marriage = additional_data.get("kp_marriage_analysis", {})
        csl_details = kp_marriage.get("csl_details", {}) if kp_marriage else {}
        promise_data = additional_data.get("promise", {})

        if not csl_details and not promise_data:
            return ""

        HINDI = {
            'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल',
            'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
            'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        HOUSE_HINDI = {
            1: 'प्रथम', 2: 'द्वितीय', 3: 'तृतीय', 4: 'चतुर्थ',
            5: 'पंचम', 6: 'षष्ठ', 7: 'सप्तम', 8: 'अष्टम',
            9: 'नवम', 10: 'दशम', 11: 'एकादश', 12: 'द्वादश'
        }

        def houses_to_hindi_str(house_list):
            if not house_list:
                return "कोई नहीं"
            parts = [f"{h} ({HOUSE_HINDI.get(h, str(h))})" for h in sorted(house_list)]
            return "भाव " + ", ".join(parts)

        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  🔒 PRE-COMPUTED CSL SIGNIFICATIONS — COPY VERBATIM — DO NOT RECALCULATE    ║")
        lines.append("║  These are machine-computed. The LLM MUST use these exact house lists.      ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("CRITICAL RULE: Every time you mention a CSL's signification ANYWHERE in your")
        lines.append("response, use the EXACT house list shown below — same list in every paragraph,")
        lines.append("every sub-question, every section. Do NOT re-derive. Do NOT use a subset.")
        lines.append("")

        # ── 7th CSL ───────────────────────────────────────────────────────
        csl_7 = promise_data.get("sub_lord") or promise_data.get("csl", "")
        if csl_7:
            sigs   = promise_data.get("csl_significations", {})
            sig_all   = promise_data.get("all_signified_houses") or sigs.get("all", [])
            sig_p     = sigs.get("promise", [])
            sig_o     = sigs.get("obstacle", [])
            sig_other = sigs.get("other", [])
            chain     = promise_data.get("chain_narrative", "")
            csl_7_h   = HINDI.get(csl_7, csl_7)

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append(f"  7th CSL: {csl_7} ({csl_7_h})")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            if sig_all:
                lines.append(f"  ALL signified houses (LOCKED): {sig_all}")
                lines.append(f"    ✅ Promise (2/7/11) : {sig_p  if sig_p  else 'None'}")
                lines.append(f"    ⚠️ Obstacle (6/8/12): {sig_o  if sig_o  else 'None'}")
                lines.append(f"    ○  Other houses     : {sig_other if sig_other else 'None'}")
                lines.append("")

                all_str = houses_to_hindi_str(sig_all)
                p_str   = houses_to_hindi_str(sig_p)   if sig_p   else "कोई नहीं"
                o_str   = houses_to_hindi_str(sig_o)   if sig_o   else "कोई नहीं"

                lines.append(f"  ⚠️ COPY THIS SENTENCE VERBATIM into every KP paragraph:")
                lines.append(f"  ┌────────────────────────────────────────────────────────────────────┐")
                lines.append(f"  │ KP पद्धति के अनुसार, सप्तम भाव का कस्प उप स्वामी (CSL) {csl_7_h} है।")
                lines.append(f"  │ {csl_7_h} {all_str} को संकेतित करता है।")
                lines.append(f"  │ इनमें से विवाह भाव (2/7/11): {p_str}।")
                lines.append(f"  │ बाधा भाव (6/8/12): {o_str}।")
                lines.append(f"  └────────────────────────────────────────────────────────────────────┘")
            else:
                lines.append(f"  (Signification scores not yet available — see chain below)")

            if chain:
                lines.append("")
                lines.append(f"  CHAIN PROOF (DO NOT change any house number when translating):")
                # break long chain into readable lines
                for sentence in chain.split(". "):
                    s = sentence.strip()
                    if s:
                        lines.append(f"    {s}.")
            lines.append("")

        # ── 2nd and 11th CSLs ─────────────────────────────────────────────
        for house_num in [2, 11]:
            h_data = csl_details.get(house_num) or csl_details.get(str(house_num), {})
            if not h_data:
                continue
            csl_name  = h_data.get("csl") or h_data.get("cusp_sub_lord", "")
            if not csl_name:
                continue
            sig_all   = h_data.get("all_signified_houses") or h_data.get("signified_houses", [])
            sig_p     = h_data.get("promise_houses_signified", [])
            sig_o     = h_data.get("obstacle_houses_signified", [])
            chain     = h_data.get("chain_narrative", "")
            csl_h_name = HINDI.get(csl_name, csl_name)
            h_hindi   = HOUSE_HINDI.get(house_num, str(house_num))

            lines.append(f"  {house_num}th CSL ({h_hindi} कस्प उप स्वामी): {csl_name} ({csl_h_name})")
            if sig_all:
                lines.append(f"  ALL signified houses (LOCKED): {sig_all}")
                lines.append(f"    ✅ Promise (2/7/11) : {sig_p if sig_p else 'None'}")
                lines.append(f"    ⚠️ Obstacle (6/8/12): {sig_o if sig_o else 'None'}")
                all_str = houses_to_hindi_str(sig_all)
                lines.append(f"  ⚠️ VERBATIM: \"KP पद्धति के अनुसार, {csl_h_name} {all_str} को संकेतित करता है।\"")
            if chain:
                lines.append(f"  Chain: {chain}")
            lines.append("")

        lines.append("╔══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  ☝️  USE EXACTLY THE SAME HOUSE NUMBERS ABOVE IN EVERY PARAGRAPH.           ║")
        lines.append("║  Changing these numbers = factual error. DO NOT re-derive significations.   ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")

        return "\n".join(lines)

    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lord data concisely"""
        if not additional_data:
            return ""
        
        house_lords = additional_data.get("marriage_house_lords", {})
        if not house_lords:
            return ""
        
        lines = ["HOUSE LORDS DATA:"]
        marriage_houses = {2, 5, 7, 8, 11}
        
        for house_num in sorted(house_lords.keys()):
            if house_num not in marriage_houses:
                continue
            
            info = house_lords.get(house_num, {})
            if not info:
                continue
            
            lord = info.get('lord', 'N/A')
            lord_house = info.get('lord_in_house', 'N/A')
            lord_sign = info.get('lord_in_sign', 'N/A')
            dignity = info.get('lord_dignity', 'N/A')
            strength = info.get('lord_strength_score', 0)
            
            conditions = []
            if info.get('lord_is_combust'):
                conditions.append("Combust")
            if info.get('lord_is_retrograde'):
                conditions.append("Retrograde")
            condition_str = ", ".join(conditions) if conditions else "Normal"
            
            planets = ", ".join(info.get('planets_in_house', [])) or "None"
            
            lines.append(f"• H{house_num}: Lord {lord} in H{lord_house}/{lord_sign} | {dignity} | {condition_str} | Str:{strength}/100 | Planets:{planets}")
        
        return "\n".join(lines)
    
    def _format_current_dasha(self, additional_data: Dict) -> str:
        """Format current dasha concisely"""
        if not additional_data:
            return ""
        
        current_dasha = additional_data.get('current_dasha', {})
        if not current_dasha:
            dasha_analysis = additional_data.get('dasha_analysis', {})
            next_periods = dasha_analysis.get('next_6_months', [])
            if next_periods:
                current_dasha = next_periods[0]
        
        if not current_dasha:
            return ""
        
        try:
            dasha_name = current_dasha.get('dasha_name', '')
            date_range = current_dasha.get('date_range', {})
            start = date_range.get('start', 'Unknown')
            end = date_range.get('end', 'Unknown')
            return f"CURRENT DASHA: {dasha_name} ({start} to {end})"
        except Exception:
            return ""
    
    def _format_manglik_planet_positions(self, additional_data: Dict) -> str:
        """
        Format pre-computed Manglik analysis data.
        Uses manglik_analysis stored by evaluator (computed, not LLM guess).
        """
        if not additional_data:
            return ""

        try:
            # PRIMARY: use pre-computed manglik_analysis from evaluator
            manglik = additional_data.get("manglik_analysis", {})
            if manglik:
                mars_house = manglik.get("mars_house")
                mars_sign = manglik.get("mars_sign", "")
                moon_house = manglik.get("moon_house")
                lagna_m = manglik.get("lagna_manglik", {})
                chandra_m = manglik.get("chandra_manglik", {})
                severity = manglik.get("severity", "UNKNOWN")
                severity_hindi = manglik.get("severity_hindi", "")

                lines = ["╔══════════════════════════════════════════════════════════════╗"]
                lines.append("║  🔴 PRE-COMPUTED MANGLIK ANALYSIS — USE THIS EXACTLY        ║")
                lines.append("║  ⚠️ DO NOT RECALCULATE. DO NOT GUESS. USE THESE FACTS.      ║")
                lines.append("╚══════════════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append(f"MARS (मंगल): House {mars_house}" + (f" in {mars_sign}" if mars_sign else ""))
                lines.append(f"MOON (चंद्र): House {moon_house if moon_house else 'N/A'}")
                lines.append("")

                # Lagna Manglik
                lagna_present = lagna_m.get("present", False)
                lagna_active = lagna_m.get("active", False)
                lagna_cancel = lagna_m.get("cancellation")
                lagna_icon = "🔴 ACTIVE" if lagna_active else ("🟡 CANCELLED/MITIGATED" if lagna_present else "🟢 NO DOSHA")
                lines.append(f"LAGNA MANGLIK: {lagna_icon}")
                lines.append(f"  Calculation: Mars in house {mars_house} from Lagna")
                lines.append(f"  Manglik houses: 1, 2, 4, 7, 8, 12")
                lines.append(f"  Present (raw): {'YES' if lagna_present else 'NO'}")
                if lagna_present and lagna_cancel:
                    cancel_text = {
                        "own_sign_or_exalted": "Mars in own sign or exalted — dosha cancelled",
                        "jupiter_aspect": "Jupiter aspects Mars — dosha mitigated"
                    }.get(lagna_cancel, lagna_cancel)
                    lines.append(f"  Cancellation: {cancel_text}")
                lines.append(f"  VERDICT: {'लग्न मांगलिक दोष सक्रिय' if lagna_active else ('लग्न मांगलिक — निरस्त/शमित' if lagna_present else 'लग्न मांगलिक नहीं')}")
                lines.append("")

                # Chandra Manglik
                chandra_present = chandra_m.get("present", False)
                chandra_active = chandra_m.get("active", False)
                chandra_cancel = chandra_m.get("cancellation")
                chandra_pos = chandra_m.get("mars_position_from_moon")
                chandra_icon = "🔴 ACTIVE" if chandra_active else ("🟡 CANCELLED/MITIGATED" if chandra_present else "🟢 NO DOSHA")
                lines.append(f"CHANDRA MANGLIK: {chandra_icon}")
                if chandra_pos and moon_house:
                    lines.append(f"  Calculation: Moon in H{moon_house}, Mars in H{mars_house}")
                    lines.append(f"  Mars is {chandra_pos}th from Moon ({mars_house} - {moon_house} = {mars_house - moon_house}, mod 12 + 1 = {chandra_pos})")
                    lines.append(f"  Manglik houses: 1, 2, 4, 7, 8, 12")
                    _manglik_set = {1, 2, 4, 7, 8, 12}
                    lines.append(f"  {chandra_pos} is {'IN' if chandra_pos in _manglik_set else 'NOT IN'} manglik houses")
                if chandra_present and chandra_cancel:
                    cancel_text = {
                        "own_sign_or_exalted": "Mars in own sign or exalted — dosha cancelled",
                        "jupiter_aspect": "Jupiter aspects Mars — dosha mitigated"
                    }.get(chandra_cancel, chandra_cancel)
                    lines.append(f"  Cancellation: {cancel_text}")
                lines.append(f"  VERDICT: {'चंद्र मांगलिक दोष सक्रिय' if chandra_active else ('चंद्र मांगलिक — निरस्त/शमित' if chandra_present else 'चंद्र मांगलिक नहीं')}")
                lines.append("")

                lines.append(f"OVERALL SEVERITY: {severity} — {severity_hindi}")
                lines.append("")
                lines.append("⚠️ CRITICAL INSTRUCTION FOR LLM:")
                lines.append("   Write EXACTLY what the computation says above.")
                lines.append("   Show the Chandra Manglik arithmetic: e.g., 'मंगल {mars_house}वें भाव में है,")
                lines.append(f"   चंद्र {moon_house}वें भाव में है, अतः चंद्र से मंगल {chandra_pos}वें स्थान पर है।'")
                lines.append("   Do NOT guess or recalculate differently.")

                return "\n".join(lines)

            # FALLBACK: derive from house_lords if manglik_analysis not present
            house_lords = additional_data.get("marriage_house_lords", {})
            lines = ["PLANET POSITIONS FOR MANGLIK CALCULATION (derived):"]
            moon_house = None
            mars_house = None
            mars_sign = None

            if house_lords:
                for house_num, info in house_lords.items():
                    planets_list = info.get('planets_in_house', [])
                    if 'Moon' in planets_list or 'Mo' in planets_list:
                        moon_house = house_num
                    if 'Mars' in planets_list or 'Ma' in planets_list:
                        mars_house = house_num

            if moon_house:
                lines.append(f"• MOON (चंद्र): House {moon_house}")
            if mars_house:
                lines.append(f"• MARS (मंगल): House {mars_house}" + (f" in {mars_sign}" if mars_sign else ""))

            if moon_house and mars_house:
                chandra_position = (mars_house - moon_house) % 12 + 1
                manglik_houses = {1, 2, 4, 7, 8, 12}
                lines.append(f"• Chandra position: ({mars_house} - {moon_house}) mod 12 + 1 = {chandra_position}")
                lines.append(f"• LAGNA MANGLIK: Mars in H{mars_house} → {'YES' if mars_house in manglik_houses else 'NO'}")
                lines.append(f"• CHANDRA MANGLIK: Mars {chandra_position}th from Moon → {'YES' if chandra_position in manglik_houses else 'NO'}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting Manglik positions: {e}")
            return ""
    
    def _format_lagna_lord_data(self, additional_data: Dict) -> str:
        """Format Lagna Lord Analysis"""
        if not additional_data:
            return ""
        
        lagna = additional_data.get("lagna_lord_analysis", {})
        if not lagna or not lagna.get("lagna_lord"):
            return ""
        
        lines = []
        lines.append("═" * 80)
        lines.append("1️⃣ LAGNA LORD ANALYSIS (Foundation)")
        lines.append("═" * 80)
        lines.append(f"Lagna Sign: {lagna.get('lagna_sign', 'Unknown')}")
        lines.append(f"Lagna Lord: {lagna.get('lagna_lord', 'Unknown')}")
        lines.append(f"Placement: House {lagna.get('lagna_lord_house', 'Unknown')} in {lagna.get('lagna_lord_sign', 'Unknown')}")
        lines.append(f"Dignity: {lagna.get('lagna_lord_dignity', 'Unknown')}")
        lines.append(f"Strength Score: {lagna.get('strength_score', 0)}/5")
        
        connections = lagna.get('marriage_house_connections', [])
        if connections:
            lines.append("Marriage House Connections:")
            for conn in connections:
                lines.append(f"  • {conn}")
        
        lines.append(f"Marriage Impact: {lagna.get('marriage_impact', 'Unknown')}")
        lines.append(f"Verdict: {lagna.get('verdict', 'NEUTRAL')}")
        lines.append("")
        
        return "\n".join(lines)

    def _format_kp_significator_table(self, additional_data: Dict) -> str:
        """
        Format KP Significator Table with COMPLETE CHAIN for each planet.
        v4.0: Shows the full signification chain per KP methodology.
        """
        if not additional_data:
            return ""
        
        kp_sig_table = additional_data.get("kp_significator_table", {})
        if not kp_sig_table or not kp_sig_table.get("planets"):
            return ""
        
        lines = []
        lines.append("═" * 120)
        lines.append("2️⃣ KP SIGNIFICATION TABLE (v4.1 — Complete Chain + HOW Proof)")
        lines.append("═" * 120)
        lines.append("")
        lines.append("Strength: Sub Lord > Star Lord > Occupation > Ownership")
        lines.append("Rule: 2/7/11 signification > 1/6/10/12 → supports marriage")
        lines.append("")
        
        for planet_info in kp_sig_table["planets"]:
            name = planet_info["name"]
            if name in ["Neptune", "Pluto", "Uranus", "Ascendant"]:
                continue
            
            planet_house = planet_info.get("house", "?")
            star_lord = planet_info.get("star_lord", "Unknown")
            star_lord_house = planet_info.get("star_lord_house", "?")
            sub_lord = planet_info.get("sub_lord", "Unknown")
            sub_lord_house = planet_info.get("sub_lord_house", "?")
            owned_houses = planet_info.get("owned_houses", [])
            sig_houses = planet_info.get("significator_houses", [])
            promise_h = planet_info.get("promise_houses", [])
            support_h = planet_info.get("supportive_houses", [])
            negative_h = planet_info.get("negative_houses", [])
            net_score = planet_info.get("net_score", "0")
            role = planet_info.get("role", "")
            chain_narrative = planet_info.get("chain_narrative", "")
            promise_how = planet_info.get("promise_how", {})
            obstacle_how = planet_info.get("obstacle_how", {})
            
            lines.append(f"  ┌─ {name} ─────────────────────────────────────────────────")
            lines.append(f"  │  Occupies:     House {planet_house}")
            lines.append(f"  │  Star Lord:    {star_lord} (in House {star_lord_house})")
            lines.append(f"  │  Sub Lord:     {sub_lord} (in House {sub_lord_house})")
            lines.append(f"  │  Owns:         Houses {owned_houses if owned_houses else 'None'}")
            lines.append(f"  │  ────────────────────────────────────────────────────")
            lines.append(f"  │  Signifies:    {sig_houses}")
            lines.append(f"  │  Promise (2/7/11): {promise_h if promise_h else 'None'}")
            lines.append(f"  │  Support (5):      {support_h if support_h else 'None'}")
            lines.append(f"  │  Obstacle (6/8/12): {negative_h if negative_h else 'None'}")
            lines.append(f"  │  Net Score:    {net_score} → {role}")
            
            # v4.1 NEW: Show HOW each promise house is signified
            if promise_how:
                lines.append(f"  │  ┌── HOW {name} SIGNIFIES PROMISE HOUSES (2/7/11):")
                for h_str, reasons in promise_how.items():
                    for reason in reasons:
                        lines.append(f"  │  │   House {h_str}: {reason}")
                lines.append(f"  │  └──")
            
            if obstacle_how:
                lines.append(f"  │  ┌── HOW {name} SIGNIFIES OBSTACLE HOUSES:")
                for h_str, reasons in obstacle_how.items():
                    for reason in reasons:
                        lines.append(f"  │  │   House {h_str}: {reason}")
                lines.append(f"  │  └──")
            
            # v4.1 NEW: Full chain narrative for LLM to translate
            if chain_narrative:
                lines.append(f"  │  ")
                lines.append(f"  │  📝 CHAIN (translate to Hindi paragraph):")
                lines.append(f"  │  {chain_narrative}")
            
            lines.append(f"  └──────────────────────────────────────────────────────────")
            lines.append("")
        
        summary = kp_sig_table.get("summary", {})
        promising = summary.get('promising_planets', [])
        negative = summary.get('negative_planets', [])
        
        lines.append("SIGNIFICATION SUMMARY:")
        if promising:
            lines.append(f"  ✅ Marriage supporters: {', '.join(promising)}")
        if negative:
            lines.append(f"  ⚠️ Obstacle planets: {', '.join(negative)}")
        
        lines.append("")
        lines.append("⚠️ FOR EACH planet claiming 2/7/11, you MUST show:")
        lines.append("   1. Star Lord chain (Planet → Nakshatra Lord → House)")
        lines.append("   2. Sub Lord chain (Planet → Sub Lord → House)")
        lines.append("   3. Which promise houses and HOW")
        lines.append("   Use the CHAIN NARRATIVE above — translate to Hindi.")
        lines.append("")
        
        return "\n".join(lines)
    
    # ==========================================================================
    # MAIN ROUTING METHOD
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
        """Main routing method - routes to appropriate specialized builder"""
        
        try:
            sub_subdomain = kwargs.get("sub_subdomain", "")
            additional_data = kwargs.get("additional_data", {})
            raw = "\n".join(technical_points) if technical_points else ""
            
            logger.info(f"Building prompt for sub_subdomain: {sub_subdomain}")
            
            if "Promise and Timing" in sub_subdomain:
                return self._build_promise_and_timing_prompt(question, additional_data, raw, language)
            elif "Timing" in sub_subdomain:
                return self._build_timing_prompt(question, additional_data, raw, language)
            elif "Promise" in sub_subdomain:
                return self._build_promise_prompt(question, additional_data, raw, language)
            elif "Nature" in sub_subdomain or "Type" in sub_subdomain:
                return self._build_nature_type_prompt(question, additional_data, raw, language)
            elif "Partner" in sub_subdomain or "Traits" in sub_subdomain:
                return self._build_partner_traits_prompt(question, additional_data, raw, language)
            elif "Origin" in sub_subdomain or "Spouse" in sub_subdomain:
                return self._build_spouse_origin_prompt(question, additional_data, raw, language)
            elif "Manglik" in sub_subdomain:
                return self._build_manglik_prompt(question, additional_data, raw, language)
            elif "Remed" in sub_subdomain:
                return self._build_remedies_prompt(question, additional_data, raw, language)
            else:
                return self._build_general_prompt(question, additional_data, raw, language)
        
        except Exception as e:
            logger.error(f"Error in build_analysis_prompt: {e}")
            return self._build_fallback_prompt(question, language)
        


    def _build_kp_timing_narrative_block(self, additional_data: Dict) -> str:
        """
        Build a COMPLETE pre-written KP narrative (Hindi) for the timing section.
        Uses real chain data from additional_data to write the full paragraph.
        The LLM must copy this verbatim — no fill-in-the-blanks, no templates.

        Produces a paragraph in the style:
        "KP फलित सिद्धांत के अनुसार, [CSL] [2/7 signifies]...
         [MD lord chain], [AD lord chain]...
         अतः [best window] तथा [nearest window] विवाह के लिए अनुकूल..."
        """
        if not additional_data:
            return ""

        promise_data = additional_data.get("promise", {})
        timing_data = additional_data.get("marriage_timing_windows", {})
        kp_marriage = additional_data.get("kp_marriage_analysis", {})
        csl_details = kp_marriage.get("csl_details", {}) if kp_marriage else {}

        if not promise_data or not timing_data or not timing_data.get("has_timing"):
            return ""

        best = timing_data.get("best_window", {})
        nearest = timing_data.get("nearest_window", {})
        marriage_proof = timing_data.get("marriage_proof", {})
        timing_proofs = marriage_proof.get("timing_proofs", []) if marriage_proof else []

        HINDI = {
            'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल',
            'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
            'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        HOUSE_HINDI = {
            1: 'प्रथम', 2: 'द्वितीय', 3: 'तृतीय', 4: 'चतुर्थ',
            5: 'पंचम', 6: 'षष्ठ', 7: 'सप्तम', 8: 'अष्टम',
            9: 'नवम', 10: 'दशम', 11: 'एकादश', 12: 'द्वादश'
        }

        def hn(p):
            return HINDI.get(p, p)

        def hh(n):
            return f"{n} ({HOUSE_HINDI.get(n, str(n))})"

        def houses_list_hindi(lst):
            if not lst:
                return "कोई नहीं"
            return " एवं ".join(hh(h) for h in sorted(lst))

        # ── Part 1: Promise paragraph (CSL chain) ──────────────────────────
        csl = promise_data.get("csl") or promise_data.get("sub_lord", "")
        csl_h = hn(csl)
        promise_houses = promise_data.get("csl_significations", {}).get("promise", [])
        obstacle_houses = promise_data.get("csl_significations", {}).get("obstacle", [])
        all_sig = promise_data.get("all_signified_houses", [])
        chain = promise_data.get("chain_narrative", "")
        state = promise_data.get("state", "promised")

        # Parse chain narrative to extract key facts for Hindi sentences
        # Format: "X occupies House N. X is in nakshatra of Y. Y occupies House M and owns houses [A,B].
        #          X's sub lord is Z, in House P, owns houses [C,D]. X owns houses [E]. Through this chain..."
        def _extract_chain_facts(chain_text):
            """Extract occupation house, star lord name+house, sub lord name+house from chain text."""
            import re
            facts = {}
            m = re.search(r'(\w+) occupies House (\d+)\.', chain_text)
            if m:
                facts['planet'] = m.group(1)
                facts['occupation_house'] = int(m.group(2))
            m = re.search(r'is in nakshatra of (\w+)\.', chain_text)
            if m:
                facts['star_lord'] = m.group(1)
            m = re.search(r'nakshatra of (\w+)\. \w+ occupies House (\d+)', chain_text)
            if m:
                facts['star_lord'] = m.group(1)
                facts['star_lord_house'] = int(m.group(2))
            m = re.search(r"sub lord is (\w+), in House (\d+)", chain_text)
            if m:
                facts['sub_lord'] = m.group(1)
                facts['sub_lord_house'] = int(m.group(2))
            m = re.search(r"owns houses \[([^\]]*)\]", chain_text)
            if m:
                raw = m.group(1)
                facts['star_lord_owns'] = [int(x.strip()) for x in raw.split(',') if x.strip().isdigit()]
            # sub lord owns
            m_all = list(re.finditer(r"owns houses \[([^\]]*)\]", chain_text))
            if len(m_all) >= 2:
                raw2 = m_all[1].group(1)
                facts['sub_lord_owns'] = [int(x.strip()) for x in raw2.split(',') if x.strip().isdigit()]
            return facts

        csl_facts = _extract_chain_facts(chain)

        # Fallback: if chain_narrative parsing yielded nothing, read the structured chain dict directly
        chain_dict = promise_data.get("chain", {})
        if chain_dict and not csl_facts.get('occupation_house'):
            if chain_dict.get('occupation'):
                csl_facts['occupation_house'] = chain_dict['occupation']
            if chain_dict.get('star_lord'):
                csl_facts['star_lord'] = chain_dict['star_lord']
            if chain_dict.get('star_lord_occupation'):
                csl_facts['star_lord_house'] = chain_dict['star_lord_occupation']
            if chain_dict.get('star_lord_ownership'):
                csl_facts['star_lord_owns'] = chain_dict['star_lord_ownership']
            if chain_dict.get('sub_lord'):
                csl_facts['sub_lord'] = chain_dict['sub_lord']
            if chain_dict.get('sub_lord_occupation'):
                csl_facts['sub_lord_house'] = chain_dict['sub_lord_occupation']
            if chain_dict.get('sub_lord_ownership'):
                csl_facts['sub_lord_owns'] = chain_dict['sub_lord_ownership']
        if not all_sig and chain_dict.get('final_houses'):
            all_sig = chain_dict['final_houses']

        # Helper: translate a "how" string from evaluator into Hindi
        def _how_to_hindi(how_str: str) -> str:
            """Convert 'Occupies house 7' / 'Lord of house 2' / 'Star lord signifies house 11' to Hindi."""
            import re
            m = re.match(r'Occupies house (\d+)', how_str)
            if m:
                return f"{hh(int(m.group(1)))} भाव में निवास (Occupancy)"
            m = re.match(r'Lord of house (\d+)', how_str)
            if m:
                return f"{hh(int(m.group(1)))} भाव का स्वामित्व (Lordship)"
            m = re.match(r'Star lord signifies house (\d+)', how_str)
            if m:
                return f"नक्षत्र स्वामी द्वारा {hh(int(m.group(1)))} भाव संकेत (Star Lord)"
            m = re.match(r'Occupies obstacle house (\d+)', how_str)
            if m:
                return f"बाधक {hh(int(m.group(1)))} भाव में निवास"
            m = re.match(r'Lord of obstacle house (\d+)', how_str)
            if m:
                return f"बाधक {hh(int(m.group(1)))} भाव का स्वामी"
            m = re.match(r'Star lord signifies obstacle house (\d+)', how_str)
            if m:
                return f"नक्षत्र स्वामी द्वारा बाधक {hh(int(m.group(1)))} भाव संकेत"
            return how_str

        # ── Build flowing prose narrative ──────────────────────────────────
        # All sections are flowing Hindi paragraphs — no ASCII art, no arrow labels.

        occ_h = csl_facts.get('occupation_house')
        sl = csl_facts.get('star_lord', '')
        sl_h = csl_facts.get('star_lord_house')
        sl_owns = csl_facts.get('star_lord_owns', [])
        sub = csl_facts.get('sub_lord', '')
        sub_h = csl_facts.get('sub_lord_house')
        sub_owns = csl_facts.get('sub_lord_owns', [])

        # ── Helper: build flowing one-lord chain prose for DBA lords ──────
        def _lord_chain_prose(planet, role_label, lord_data):
            """Return a flowing Hindi sentence describing this DBA lord's chain & signification."""
            p_h = hn(planet)
            lc_facts = _extract_chain_facts(lord_data.get("chain_narrative", ""))
            # Fallback to structured fields
            if not lc_facts.get('occupation_house') and lord_data.get('occupation'):
                lc_facts['occupation_house'] = lord_data['occupation']
            if not lc_facts.get('star_lord') and lord_data.get('star_lord'):
                lc_facts['star_lord'] = lord_data['star_lord']
            if not lc_facts.get('star_lord_house') and lord_data.get('star_lord_occupation'):
                lc_facts['star_lord_house'] = lord_data['star_lord_occupation']
            if not lc_facts.get('star_lord_owns') and lord_data.get('star_lord_ownership'):
                lc_facts['star_lord_owns'] = lord_data['star_lord_ownership']
            if not lc_facts.get('sub_lord') and lord_data.get('sub_lord'):
                lc_facts['sub_lord'] = lord_data['sub_lord']
            if not lc_facts.get('sub_lord_house') and lord_data.get('sub_lord_occupation'):
                lc_facts['sub_lord_house'] = lord_data['sub_lord_occupation']
            if not lc_facts.get('sub_lord_owns') and lord_data.get('sub_lord_ownership'):
                lc_facts['sub_lord_owns'] = lord_data['sub_lord_ownership']

            l_occ = lc_facts.get('occupation_house')
            l_sl = lc_facts.get('star_lord', '')
            l_sl_h = lc_facts.get('star_lord_house')
            l_sl_owns = lc_facts.get('star_lord_owns', [])
            l_sub = lc_facts.get('sub_lord', '')
            l_sub_h = lc_facts.get('sub_lord_house')
            l_sub_owns = lc_facts.get('sub_lord_owns', [])

            ph = lord_data.get("signifies_promise_houses", lord_data.get("signified_houses", []))
            oh = lord_data.get("signifies_obstacle_houses", [])
            how_list = lord_data.get("how", [])

            parts = [f"{p_h} {role_label}"]
            if l_occ:
                parts.append(f"{hh(l_occ)} भाव में स्थित है")
            if l_sl:
                sl_clause = f"नक्षत्र स्वामी {hn(l_sl)}"
                if l_sl == planet:
                    sl_clause += " (स्वनक्षत्री)"
                elif l_sl_h:
                    sl_clause += f" {hh(l_sl_h)} भाव में"
                    if l_sl_owns:
                        sl_clause += f", {' एवं '.join(hh(h) for h in l_sl_owns)} भाव का स्वामी"
                parts.append(sl_clause)
            if l_sub:
                sub_clause = f"उप-स्वामी {hn(l_sub)}"
                if l_sub_h:
                    sub_clause += f" {hh(l_sub_h)} भाव में स्थित है"
                    if l_sub_owns:
                        sub_clause += f" तथा {' एवं '.join(hh(h) for h in l_sub_owns)} भाव का स्वामी"
                parts.append(sub_clause)

            # Signification result
            if ph:
                ph_str = " एवं ".join(str(h) for h in ph)
                ph_hindi = " एवं ".join(hh(h) for h in ph)
                parts.append(f"{hh(ph[0]) if len(ph) == 1 else ph_hindi} को संकेतित करता है")
            if oh:
                oh_hindi = ", ".join(hh(h) for h in oh)
                parts.append(f"यद्यपि नक्षत्र स्वामी द्वारा {oh_hindi} भाव संबंध बाधा का संकेत देता है")

            return "; ".join(parts) + "।"

        # ── PART 1: Flowing KP Promise paragraph ──────────────────────────
        promise_lines = []
        promise_lines.append("PART 1:")
        promise_lines.append("")

        # Opening: KP rule statement
        promise_lines.append(
            "KP सिद्धांतानुसार विवाह का वचन सप्तम भाव के कुस्प सब-लॉर्ड (CSL) से निर्धारित किया जाता है।"
        )

        # CSL identification sentence
        csl_sent = f"इस कुंडली में सप्तम कुस्प सब-लॉर्ड {csl_h} है।"
        promise_lines.append(csl_sent)

        # Occupation sentence
        if occ_h:
            occ_sent = f"{csl_h} {hh(occ_h)} भाव में स्थित होकर प्रत्यक्ष रूप से {hh(occ_h)} भाव का संकेत करता है।"
            promise_lines.append(occ_sent)

        # Star lord sentence
        if sl:
            if sl == csl:
                sl_sent = (
                    f"{csl_h} स्वनक्षत्री होने के कारण"
                    + (f" {' एवं '.join(hh(h) for h in sl_owns)} भाव का स्वामी होकर {' एवं '.join(hh(h) for h in sl_owns)} भाव को संकेतित करता है।" if sl_owns else " स्वयं को संकेतित करता है।")
                )
            else:
                sl_sent = f"{csl_h} का नक्षत्र स्वामी {hn(sl)} है"
                if sl_h:
                    sl_sent += f", जो {hh(sl_h)} भाव में स्थित है"
                if sl_owns:
                    sl_sent += f" तथा {' एवं '.join(hh(h) for h in sl_owns)} भाव का स्वामी है"
                sl_sent += "।"
            promise_lines.append(sl_sent)

        # Sub lord sentence
        if sub:
            sub_sent = f"{csl_h} का उप-स्वामी {hn(sub)}"
            if sub_h:
                sub_sent += f" {hh(sub_h)} भाव में स्थित है"
            if sub_owns:
                sub_sent += f" तथा {' एवं '.join(hh(h) for h in sub_owns)} भाव का स्वामी होकर {' एवं '.join(hh(h) for h in sub_owns)} भाव को संकेतित करता है"
            sub_sent += "।"
            promise_lines.append(sub_sent)

        # Combined signification sentence
        all_sig_sorted = sorted(all_sig) if all_sig else []
        if all_sig_sorted:
            all_sig_named = " एवं ".join(hh(h) for h in all_sig_sorted)
            combined_sent = f"इस प्रकार समेकित रूप से {csl_h} {all_sig_named} भावों को संकेतित करता है।"
            promise_lines.append(combined_sent)

        # Promise verdict sentence
        if promise_houses:
            ph_named = " एवं ".join(hh(h) for h in promise_houses)
            verdict_sent = f"विवाह भाव (2/7/11) में से {ph_named} सक्रिय होने से KP 2-7-11 नियम के अनुसार विवाह का वचन स्थापित होता है"
            if obstacle_houses:
                verdict_sent += ", यद्यपि अन्य सहायक कारकों के कारण व्यवहारिक बाधाएँ या विलंब संभव हैं।"
            else:
                verdict_sent += "।"
            promise_lines.append(verdict_sent)

        # 2nd/11th CSL support sentences
        csl_2_data = csl_details.get(2) or csl_details.get("2", {})
        csl_11_data = csl_details.get(11) or csl_details.get("11", {})
        support_parts = []
        if csl_2_data:
            c2 = csl_2_data.get("csl", "")
            p2h = csl_2_data.get("promise_houses_signified", [])
            if c2 and p2h:
                support_parts.append(
                    f"द्वितीय कुस्प सब-लॉर्ड {hn(c2)} {' एवं '.join(hh(h) for h in p2h)} भाव को संकेतित कर पारिवारिक स्थापना का समर्थन करता है"
                )
        if csl_11_data:
            c11 = csl_11_data.get("csl", "")
            p11h = csl_11_data.get("promise_houses_signified", [])
            if c11 and p11h:
                support_parts.append(
                    f"एकादश कुस्प सब-लॉर्ड {hn(c11)} {' एवं '.join(hh(h) for h in p11h)} भाव संकेतित कर इच्छा पूर्ति का समर्थन देता है"
                )
        if support_parts:
            promise_lines.append(". ".join(support_parts) + ".")

        # Final verdict sentence
        if obstacle_houses:
            oh_named = " एवं ".join(str(h) for h in obstacle_houses)
            final_verdict = (
                f"समग्र रूप से विवाह भावों एवं बाधक भावों ({oh_named}) की समान सक्रियता के कारण "
                f"निष्कर्ष \"विवाह का वचन बाधाओं सहित\" (Promised with Obstacles) के रूप में प्राप्त होता है।"
            )
        else:
            final_verdict = (
                f"समग्र रूप से विवाह भावों की सशक्त सक्रियता तथा बाधक भावों का नगण्य प्रभाव होने से "
                f"विवाह का वचन स्पष्ट एवं दृढ़ रूप से स्थापित है।"
            )
        promise_lines.append(final_verdict)

        # ── Part 2: DBA Timing — flowing paragraph(s) per timing window ────
        flat_dasha_lords = additional_data.get("kp_dasha_lords", []) if additional_data else []

        role_labels_prose = {
            0: "महादशा स्वामी",
            1: "भुक्ति/अंतर्दशा स्वामी",
            2: "प्रत्यंतर्दशा स्वामी",
        }
        level_role_prose = {
            'MD': 'महादशा स्वामी',
            'BD': 'भुक्ति स्वामी',
            'AD': 'अंतर्दशा स्वामी',
            'PD': 'प्रत्यंतर्दशा स्वामी',
        }

        if timing_proofs or flat_dasha_lords:
            promise_lines.append("")
            promise_lines.append("PART 2:")
            promise_lines.append("")
            promise_lines.append(
                "दशा–भुक्ति–अंतर विश्लेषण के अनुसार घटना तब फलित होती है जब संबंधित दशा ग्रह "
                "2, 7 अथवा 11 भावों को संकेतित करें।"
            )
            promise_lines.append("")

            def _dba_window_paragraph(dasha_str, period, dasha_lords_list, strength, is_nearest=True, is_best_only=False):
                """Build one flowing paragraph for a DBA timing window."""
                dasha_h = self._dasha_to_hindi(dasha_str)
                strength_qualifier = {
                    "STRONG": "विवाह के लिए अनुकूल",
                    "MODERATE": "विवाह के लिए मध्यम अनुकूल",
                }.get(strength, "विवाह के संदर्भ में उल्लेखनीय")
                has_obstacles = any(lord.get("signifies_obstacle_houses") for lord in dasha_lords_list)
                obstacle_suffix = " किन्तु बाधाओं सहित" if has_obstacles else ""

                para_sentences = []
                # Opening sentence
                para_sentences.append(
                    f"{dasha_h} दशा ({period}) {strength_qualifier}{obstacle_suffix} काल है।"
                )

                # Each lord as a prose sentence
                for i, lord_data in enumerate(dasha_lords_list[:3]):
                    planet = lord_data.get("planet", "")
                    role = role_labels_prose.get(i, "दशा स्वामी")
                    sentence = _lord_chain_prose(planet, role, lord_data)
                    para_sentences.append(sentence)

                # Combined houses conclusion for this window
                combined_ph = set()
                combined_oh = set()
                for ld in dasha_lords_list:
                    combined_ph.update(ld.get("signifies_promise_houses", ld.get("signified_houses", [])))
                    combined_oh.update(ld.get("signifies_obstacle_houses", []))
                combined_marriage = combined_ph & {2, 7, 11}
                if combined_marriage:
                    m_named = " एवं ".join(hh(h) for h in sorted(combined_marriage))
                    conclusion = f"इस प्रकार इस अवधि में {m_named} की संयुक्त सक्रियता विवाह की घटना को संभव बनाती है"
                    if combined_oh:
                        oh_named = ", ".join(hh(h) for h in sorted(combined_oh))
                        conclusion += f", यद्यपि {oh_named} भाव संबंध के कारण कुछ विलंब या समायोजन संभव हैं।"
                    else:
                        conclusion += "।"
                    para_sentences.append(conclusion)

                return " ".join(para_sentences)

            if timing_proofs:
                # Determine nearest and best proofs
                best_dasha_str = best.get("dasha", "") if best else ""
                nearest_dasha_str = nearest.get("dasha", "") if nearest else ""
                same_window = best_dasha_str == nearest_dasha_str

                # Emit nearest window paragraph
                nearest_proof = next(
                    (pr for pr in timing_proofs if pr.get("dasha") == nearest_dasha_str), None
                ) or (timing_proofs[0] if timing_proofs else None)

                if nearest_proof:
                    period_str = nearest_proof.get("period", "")
                    para = _dba_window_paragraph(
                        nearest_proof.get("dasha", ""),
                        period_str,
                        nearest_proof.get("dasha_lords", []),
                        nearest_proof.get("promise_strength", ""),
                        is_nearest=True,
                    )
                    promise_lines.append(para)
                    promise_lines.append("")

                # Emit best window paragraph if different from nearest
                if not same_window and best_dasha_str:
                    best_proof = next(
                        (pr for pr in timing_proofs if pr.get("dasha") == best_dasha_str), None
                    )
                    if best_proof:
                        best_period = best_proof.get("period", "")
                        best_para = _dba_window_paragraph(
                            best_proof.get("dasha", ""),
                            best_period,
                            best_proof.get("dasha_lords", []),
                            best_proof.get("promise_strength", ""),
                            is_nearest=False,
                            is_best_only=True,
                        )
                        promise_lines.append(
                            f"तुलनात्मक रूप से {self._dasha_to_hindi(best_dasha_str)} दशा "
                            f"({best.get('start','')} से {best.get('end','')}) अधिक स्थिर एवं अनुकूल "
                            f"विवाह काल के रूप में संकेतित होती है, जहाँ दशा ग्रहों द्वारा विवाह भावों "
                            f"की अपेक्षाकृत अधिक शुद्ध सक्रियता प्राप्त होती है।"
                        )
                        promise_lines.append("")

            else:
                # Fallback: flat kp_dasha_lords — treat all 3 as one combined window
                nearest_dasha_str = nearest.get("dasha", "") if nearest else ""
                best_dasha_str = best.get("dasha", "") if best else ""
                period_str = f"{nearest.get('start','')} से {nearest.get('end','')}" if nearest else ""
                para = _dba_window_paragraph(
                    nearest_dasha_str,
                    period_str,
                    flat_dasha_lords[:3],
                    "STRONG",
                    is_nearest=True,
                )
                promise_lines.append(para)
                promise_lines.append("")

                # If best window differs, add comparative sentence
                if best_dasha_str and best_dasha_str != nearest_dasha_str:
                    promise_lines.append(
                        f"तुलनात्मक रूप से {self._dasha_to_hindi(best_dasha_str)} दशा "
                        f"({best.get('start','')} से {best.get('end','')}) अधिक स्थिर एवं अनुकूल "
                        f"विवाह काल के रूप में संकेतित होती है, जहाँ दशा ग्रहों द्वारा विवाह भावों "
                        f"की अपेक्षाकृत अधिक शुद्ध सक्रियता प्राप्त होती है।"
                    )
                    promise_lines.append("")

        # ── Part 3: Flowing conclusion sentence ─────────────────────────────
        best_dasha_h = self._dasha_to_hindi(best.get("dasha", "")) if best else ""
        nearest_dasha_h = self._dasha_to_hindi(nearest.get("dasha", "")) if nearest else ""
        best_start = best.get("start", "") if best else ""
        best_end = best.get("end", "") if best else ""
        nearest_start = nearest.get("start", "") if nearest else ""
        nearest_end = nearest.get("end", "") if nearest else ""

        promise_lines.append("PART 3:")
        promise_lines.append("")

        same = best and nearest and best.get("dasha") == nearest.get("dasha") and best_start == nearest_start
        if same and nearest_start:
            promise_lines.append(
                f"अतः समग्र विश्लेषण के आधार पर विवाह का वचन स्थापित है तथा सर्वाधिक अनुकूल एवं "
                f"निकटतम काल {nearest_start} से {nearest_end} ({nearest_dasha_h} दशा) माना जाता है।"
            )
        else:
            parts_out = []
            if nearest_start and nearest_end and nearest_dasha_h:
                parts_out.append(f"निकटतम अनुकूल काल {nearest_start} से {nearest_end} है")
            if best_start and best_end and best_dasha_h and not same:
                parts_out.append(f"अधिक स्थिर एवं श्रेष्ठ काल {best_start} से {best_end} माना जाता है")
            if parts_out:
                promise_lines.append(
                    "अतः समग्र विश्लेषण के आधार पर विवाह का वचन स्थापित है, "
                    + ", ".join(parts_out) + "।"
                )

        # ── Part 4: Transit — flowing paragraph ─────────────────────────────
        # event_fructification may live at top level of additional_data or inside timing_data
        ef_data = (
            additional_data.get("event_fructification", {})
            or (timing_data.get("event_fructification", {}) if timing_data else {})
        )
        ef_conditions = ef_data.get("conditions", []) if ef_data else []
        transit_cond = next((c for c in ef_conditions if c.get("name") == "TRANSIT_TRIGGER"), None)
        rp_match_cond = next((c for c in ef_conditions if c.get("name") == "RULING_PLANET_MATCH"), None)

        ruling_planets = []
        rp_signifying = []
        rp_in_dba = []
        if transit_cond:
            ruling_planets = transit_cond.get("details", {}).get("ruling_planets", [])
            rp_signifying = transit_cond.get("details", {}).get("rp_signifying_marriage", [])
        if rp_match_cond:
            rp_in_dba = rp_match_cond.get("details", {}).get("matching", [])

        if not ruling_planets:
            kp_marriage_local = additional_data.get("kp_marriage_analysis", {})
            timing_rulers = kp_marriage_local.get("timing_rulers", {}) if kp_marriage_local else {}
            ruling_planets = timing_rulers.get("ruling_planets", [])

        if ruling_planets:
            promise_lines.append("")
            promise_lines.append("PART 4:")
            promise_lines.append("")

            rp_hindi = [hn(p) for p in ruling_planets]
            transit_sentences = []

            # Opening: which ruling planets signify marriage houses
            if rp_signifying:
                rp_sig_parts = []
                for rp_entry in rp_signifying:
                    rp_name = rp_entry.get("planet", "")
                    rp_ph = rp_entry.get("promise_houses", [])
                    if rp_name and rp_ph:
                        rp_sig_parts.append(
                            f"{hn(rp_name)}"
                        )
                if rp_sig_parts:
                    transit_sentences.append(
                        f"गोचर समर्थन के संदर्भ में वर्तमान ग्रह स्थितियों में "
                        f"{', '.join(rp_sig_parts)} विवाह भाव संकेतकों से संबंधित पाए जाते हैं "
                        f"तथा दशा ग्रहों से सामंजस्य स्थापित करते हैं, जिससे घटना फलन की "
                        f"संभावना सुदृढ़ होती है।"
                    )
                else:
                    transit_sentences.append(
                        f"गोचर समर्थन के संदर्भ में वर्तमान Ruling Planets "
                        f"({', '.join(rp_hindi)}) का विवाह भावों से प्रत्यक्ष संबंध सीमित है, "
                        f"किन्तु DBA काल में विवाह संभव है।"
                    )
            else:
                transit_sentences.append(
                    f"गोचर समर्थन के संदर्भ में वर्तमान ग्रह स्थितियों में "
                    f"{', '.join(rp_hindi)} का विवाह भावों से संबंध देखा जाता है।"
                )

            # DBA match sentence
            if rp_in_dba:
                rp_dba_hindi = [hn(p) for p in rp_in_dba]
                transit_sentences.append(
                    f"{', '.join(rp_dba_hindi)} DBA दशा-भुक्ति में भी उपस्थित होने से "
                    f"KP Event Fructification की शर्त पूरी होती है।"
                )
            else:
                transit_sentences.append(
                    "DBA स्वामियों एवं Ruling Planets में सामंजस्य मध्यम स्तर का है; "
                    "भविष्य के गोचर में पुष्टि होने पर Timing Confidence बढ़ेगी।"
                )

            promise_lines.append(" ".join(transit_sentences))

        return "\n".join(promise_lines)

    def _build_mandatory_dasha_paragraph(self, additional_data: Dict) -> str:
        """
        v4.1 FIX: Build a pre-filled Hindi paragraph template for EACH dasha lord.
        The LLM MUST use this — it's not a suggestion, it's the paragraph itself.
        """
        if not additional_data:
            return ""
        
        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""
        
        best = timing_data.get("best_window", {})
        if not best:
            return ""
        
        marriage_proof = timing_data.get("marriage_proof", {})
        timing_proofs = marriage_proof.get("timing_proofs", [])
        
        target_dasha = best.get("dasha", "")
        target_proof = next(
            (p for p in timing_proofs if p.get("dasha") == target_dasha),
            timing_proofs[0] if timing_proofs else None
        )
        
        if not target_proof:
            return ""
        
        hindi_names = {
            'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल',
            'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
            'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        role_labels_hindi = ["महादशा स्वामी", "अंतर्दशा स्वामी", "प्रत्यंतर्दशा स्वामी"]
        
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  📝 MANDATORY PARAGRAPH 8 — COPY THIS INTO YOUR RESPONSE (HINDI)            ║")
        lines.append("║  ⚠️ DO NOT SUMMARIZE. USE THIS EXACT STRUCTURE.                             ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"DASHA: {self._dasha_to_hindi(target_dasha)}")
        lines.append(f"PERIOD: {best.get('start')} to {best.get('end')}")
        lines.append("")
        lines.append("USE THIS PARAGRAPH WORD-FOR-WORD (translate chain_narrative to Hindi):")
        lines.append("")
        lines.append(f"'{self._dasha_to_hindi(target_dasha)} की दशा में विवाह की प्रबल संभावना है। इसका KP प्रमाण इस प्रकार है:")
        lines.append("")
        
        for i, lord_proof in enumerate(target_proof.get("dasha_lords", [])):
            planet = lord_proof.get("planet", "")
            planet_hindi = hindi_names.get(planet, planet)
            label_hindi = role_labels_hindi[i] if i < len(role_labels_hindi) else "दशा स्वामी"
            chain = lord_proof.get("chain_narrative", "")
            promise_houses = lord_proof.get("signifies_promise_houses", [])
            obstacle_houses = lord_proof.get("signifies_obstacle_houses", [])
            how_list = lord_proof.get("how", [])
            
            lines.append(f"[{label_hindi}: {planet_hindi}]")
            lines.append(f"Chain (MUST translate to Hindi): {chain}")
            lines.append(f"Promise houses signified (2/7/11): {promise_houses}")
            lines.append(f"Obstacle houses: {obstacle_houses}")
            if how_list:
                lines.append(f"HOW (reasons): {'; '.join(how_list[:3])}")
            lines.append("")
            
            # Give the LLM a FILL-IN template
            lines.append(f"↓ YOUR HINDI PARAGRAPH FOR {planet_hindi}:")
            lines.append(f"'{planet_hindi} {label_hindi} है। [FILL: chain narrative in Hindi].")
            if promise_houses:
                lines.append(f"इस श्रृंखला से {planet_hindi} भाव {promise_houses} को संकेतित करता है — यह विवाह भाव (2/7/11) हैं, अतः अनुकूल।'")
            else:
                lines.append(f"इस श्रृंखला से {planet_hindi} सीधे विवाह भाव (2/7/11) संकेतित नहीं करता।'")
            lines.append("")
        
        # Combined verdict template
        all_promise = set()
        for lp in target_proof.get("dasha_lords", []):
            all_promise.update(lp.get("signifies_promise_houses", []))
        
        lines.append(f"↓ COMBINED VERDICT PARAGRAPH (MANDATORY):")
        lines.append(f"'तीनों दशा स्वामी मिलकर भाव {sorted(all_promise)} को संकेतित करते हैं।")
        lines.append(f"2-7-11 नियम के अनुसार: भाव {sorted(all_promise & {2,7,11})} संकेतित हैं।")
        lines.append(f"→ यह दशा विवाह के लिए {'अत्यंत अनुकूल' if len(all_promise & {2,7,11}) >= 2 else 'आंशिक रूप से अनुकूल'} है।'")
        lines.append("")
        lines.append("⚠️ ANTI-HALLUCINATION: The chain data above is COMPUTED. Do NOT change house numbers.")
        lines.append("   If chain_narrative says 'Mars occupies House 4', write 'मंगल चौथे भाव में है'.")
        lines.append("   NEVER say 'मंगल दूसरे भाव को संकेतित करता है' unless House 2 appears in promise_houses above.")
        
        return "\n".join(lines)
    
    # ==========================================================================
    # FALLBACK PROMPT
    # ==========================================================================
    
    def _build_fallback_prompt(self, question: str, language: str) -> str:
        """Fallback prompt if something fails"""
        lang_inst = self._get_language_instruction_safe(language)
        return f"""
{lang_inst}

You are an expert KP and Vedic astrologer. Answer the following marriage-related question.

QUESTION: "{question}"

Use proper KP terminology: "Cusp Sub Lord (CSL)", "signifies" (not "activates").
Show Star Lord chain for any KP claims.
Provide flowing analysis in paragraphs.
End with "TELL CLIENT:" actionable statement.
"""
    
    # ==========================================================================
    # KP DASHA SIGNIFICATION PROOF (v4.0)
    # ==========================================================================

    def _format_dasha_kp_proof(self, additional_data):
        """
        v4.1: Uses chain_narrative from timing_proofs per dasha lord.
        No longer reconstructs chains — uses pre-built data from evaluator.
        
        REPLACES: _format_dasha_kp_proof in v4.0
        """
        if not additional_data:
            return ""

        timing_data = additional_data.get("marriage_timing_windows", {})
        if not timing_data or not timing_data.get("has_timing"):
            return ""

        best = timing_data.get("best_window", {})
        nearest = timing_data.get("nearest_window", {})
        if not best and not nearest:
            return ""

        target_window = best if best else nearest
        
        # Get pre-built timing proofs (v3.1 enhanced with chain_narrative)
        marriage_proof = timing_data.get("marriage_proof", {})
        timing_proofs = marriage_proof.get("timing_proofs", [])
        
        target_dasha = target_window.get("dasha", "")
        target_proof = None
        for proof in timing_proofs:
            if proof.get("dasha") == target_dasha:
                target_proof = proof
                break
        if not target_proof and timing_proofs:
            target_proof = timing_proofs[0]

        hindi_names = {
            'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल',
            'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र',
            'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }

        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  📊 DASHA SIGNIFICATION CHAIN PROOF (v4.1 — Per-Lord Chains)                 ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"DASHA: {target_dasha}")
        lines.append(f"DASHA (Hindi): {self._dasha_to_hindi(target_dasha)}")
        lines.append(f"PERIOD: {target_window.get('start', 'N/A')} to {target_window.get('end', 'N/A')}")
        lines.append(f"SCORE: {target_window.get('final_score', target_window.get('score', 'N/A'))}")
        lines.append("")
        
        if target_proof:
            lines.append(f"Promise Strength: {target_proof.get('promise_strength', 'N/A')}")
            lines.append(f"Venus involved: {'✅ Yes' if target_proof.get('venus_involved') else '❌ No'}")
            lines.append(f"Jupiter involved: {'✅ Yes' if target_proof.get('jupiter_involved') else '❌ No'}")
            lines.append("")
            
            role_labels = ["MAHADASHA LORD", "ANTARDASHA LORD", "PRATYANTARDASHA LORD"]
            role_hindi = ["महादशा स्वामी", "अंतर्दशा स्वामी", "प्रत्यंतर्दशा स्वामी"]
            
            for i, lord_proof in enumerate(target_proof.get("dasha_lords", [])):
                planet = lord_proof.get("planet", "Unknown")
                planet_hindi = hindi_names.get(planet, planet)
                label = role_labels[i] if i < len(role_labels) else f"LEVEL {i+1}"
                label_h = role_hindi[i] if i < len(role_hindi) else f"स्तर {i+1}"
                
                lines.append(f"{'─' * 80}")
                lines.append(f"  {chr(97+i)}) {label}: {planet} ({planet_hindi}) — {label_h}")
                lines.append(f"{'─' * 80}")
                
                # v4.1: Show the COMPLETE chain narrative
                chain = lord_proof.get("chain_narrative", "")
                promise_houses = lord_proof.get("signifies_promise_houses", [])
                obstacle_houses = lord_proof.get("signifies_obstacle_houses", [])
                how_list = lord_proof.get("how", [])

                if chain:
                    lines.append(f"  COMPLETE SIGNIFICATION CHAIN:")
                    chain_sentences = chain.split(". ")
                    for sentence in chain_sentences:
                        if sentence.strip():
                            lines.append(f"    {sentence.strip()}.")
                    lines.append("")

                if how_list:
                    lines.append(f"  SIGNIFICATION PROOF (HOW):")
                    for how_item in how_list:
                        lines.append(f"    • {how_item}")
                    lines.append("")

                if promise_houses:
                    lines.append(f"  ✅ Signifies PROMISE houses: {promise_houses}")
                else:
                    lines.append(f"  ⚠️ Does NOT directly signify 2/7/11")

                if obstacle_houses:
                    lines.append(f"  ⚠️ Also signifies OBSTACLE houses: {obstacle_houses}")

                # ── PRE-FILLED HINDI PARAGRAPH — LLM must copy this into PARAGRAPH 8 ──
                # Parse the chain_narrative to extract key facts for Hindi output
                lines.append("")
                lines.append(f"  ┌─────────────────────────────────────────────────────────────────────┐")
                lines.append(f"  │ ⚠️ COPY THIS PARAGRAPH INTO YOUR RESPONSE (translate chain to Hindi) │")
                lines.append(f"  └─────────────────────────────────────────────────────────────────────┘")
                lines.append(f"  [{label_h}: {planet_hindi}]")
                # Build the Hindi paragraph from the chain data directly
                if chain:
                    lines.append(f"  '{planet_hindi} {label_h} है।")
                    # Emit the chain sentence-by-sentence, tagged for translation
                    for sentence in chain.split(". "):
                        s = sentence.strip()
                        if s and not s.startswith("Promise") and not s.startswith("Obstacle") and not s.startswith("Through"):
                            lines.append(f"  [TRANSLATE]: {s}.")
                    if promise_houses:
                        lines.append(f"  इस श्रृंखला से {planet_hindi} भाव {promise_houses} को संकेतित करता है —")
                        lines.append(f"  ये विवाह भाव (2/7/11) हैं, अतः यह दशा विवाह के लिए अनुकूल है।")
                    else:
                        lines.append(f"  इस श्रृंखला से {planet_hindi} सीधे विवाह भाव (2/7/11) संकेतित नहीं करता।")
                    if obstacle_houses:
                        lines.append(f"  हालांकि {planet_hindi} भाव {obstacle_houses} (बाधा भाव) भी संकेतित करता है।'")
                    else:
                        lines.append(f"  कोई बाधा भाव संकेतित नहीं है।'")
                lines.append("")
            
            # House linkage summary
            if target_proof.get("house_linkage"):
                lines.append("COMBINED DBA HOUSE LINKAGE:")
                for linkage in target_proof["house_linkage"]:
                    lines.append(f"  • {linkage}")
                lines.append("")
        
        else:
            lines.append("  ⚠️ Detailed per-lord proof not available.")
            lines.append("  Use the KP Significator Table above for chain data.")
        
        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        lines.append("⚠️ LLM INSTRUCTION:")
        lines.append("   For EACH dasha lord above, translate the CHAIN to Hindi:")
        lines.append("   '[Planet] भाव [X] में स्थित है। [Planet] [Star Lord] के नक्षत्र में है।")
        lines.append("    [Star Lord] भाव [Y] में स्थित है और भाव [Z] का स्वामी है।")
        lines.append("    इस श्रृंखला से [Planet] भाव [list] को संकेतित करता है।")
        lines.append("    विवाह भाव (2/7/11): [which] → अनुकूल/प्रतिकूल'")
        lines.append("")
        
        return "\n".join(lines)



    def _build_promise_verdict_banner(
    self,
    promise_state: str,
    csl_name: str,
    promise_houses_hit: list,
    obstacle_houses_hit: list,
    promise_score_val,
    obstacle_score_val
) -> str:
        """
        Builds a hard-to-ignore verdict banner placed at the TOP of the prompt.
        This prevents the LLM from overriding the computed promise state.
        """
        
        if promise_state == "promised":
            state_line = "✅ VERDICT: विवाह PROMISED है — tone must be confident but show chain proof"
            tone_rule = "✅ General answer MAY say 'विवाह का योग स्पष्ट है'"
        elif promise_state == "promised_with_obstacles":
            state_line = "⚠️ VERDICT: विवाह PROMISED WITH OBSTACLES है — tone must show both promise AND struggle"
            tone_rule = "❌ FORBIDDEN: 'विवाह का योग स्पष्ट रूप से मौजूद है' (too confident)\n   ❌ FORBIDDEN: 'विवाह नहीं होगा' (too negative)\n   ✅ REQUIRED: 'विवाह का योग है, परंतु बाधाओं के साथ'"
        elif promise_state == "blocked":
            state_line = "❌ VERDICT: विवाह BLOCKED/DENIED है — tone must focus on challenges"
            tone_rule = "❌ FORBIDDEN: Any confident promise statement\n   ✅ REQUIRED: Focus on obstacles, remedies, conditional timing"
        else:
            state_line = "❓ VERDICT: NEUTRAL/UNKNOWN — present balanced analysis"
            tone_rule = "✅ Present both possibilities. Do not over-promise."
        
        return f"""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  🔒 COMPUTED PROMISE STATE — DO NOT OVERRIDE — READ BEFORE ANYTHING ELSE ║
    ╚═══════════════════════════════════════════════════════════════════════════╝

    {state_line}

    7th CSL: {csl_name}
    Promise houses signified (2/7/11): {promise_houses_hit if promise_houses_hit else 'None'}
    Obstacle houses signified (1/6/10/12): {obstacle_houses_hit if obstacle_houses_hit else 'None'}
    Promise Score: {promise_score_val}
    Obstacle Score: {obstacle_score_val}

    TONE RULE:
    {tone_rule}

    ⚠️ THIS IS A MACHINE-COMPUTED RESULT FROM THE EVALUATOR.
        Your job is to EXPLAIN this result using chain logic — NOT re-evaluate it.
        The planetary data below may look mixed — that is EXPECTED for this state.
        Do not let mixed data push you toward a more confident or more negative tone.

    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  BEGIN ANALYSIS BELOW — TONE IS LOCKED TO: {promise_state.upper():<30} ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """

    # ==========================================================================
    # ★ UNIFIED PROMISE + TIMING PROMPT (v4.0 — Proper KP Chain Logic)
    # ==========================================================================

    def _build_promise_and_timing_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """
        Unified prompt for Marriage Promise + Timing.
        v4.0: Enforces proper KP methodology, terminology, and chain logic.
        """

        lang_inst_raw = self._get_language_instruction_safe(language)
        # Strip the generic EXAMPLE OUTPUT FORMAT from lang_inst — it shows a 3-line
        # ASTROLOGICAL_ANALYSIS which causes the LLM to anchor on that short style.
        # We inject a promise+timing-specific example further below in the skeleton.
        if "EXAMPLE OUTPUT FORMAT" in lang_inst_raw:
            lang_inst = lang_inst_raw[:lang_inst_raw.index("EXAMPLE OUTPUT FORMAT")].rstrip()
        else:
            lang_inst = lang_inst_raw
        today_str = datetime.now().strftime("%B %d, %Y")

        timing_data = self._format_timing_windows(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        kp_dasha_proof = self._format_dasha_kp_proof(additional_data)
        event_fructification_text = self._format_event_fructification(additional_data)
        best_nearest_instruction = self._format_best_nearest_timing_instruction(additional_data)
        # NEW: pre-written Hindi KP narrative block (replaces PARAGRAPH 8 template)
        kp_timing_narrative = self._build_kp_timing_narrative_block(additional_data)

        promise_state = "unknown"
        if additional_data:
            promise_info = additional_data.get("promise", {})
            promise_state = promise_info.get("state", "unknown")
            promise_data_ref = additional_data.get("promise", {}) if additional_data else {}
            promise_csl_sigs = promise_data_ref.get("csl_significations", {})
            promise_houses_hit = promise_csl_sigs.get("promise", [])
            obstacle_houses_hit = promise_csl_sigs.get("obstacle", [])
            promise_score_val = promise_data_ref.get("promise_score", "N/A")
            obstacle_score_val = promise_data_ref.get("obstacle_score", "N/A")
            csl_name = promise_data_ref.get("sub_lord", promise_data_ref.get("csl", "Unknown"))

        ruling_planets_list = []
        marriage_key_planets = []
        if additional_data:
            kp_marriage = additional_data.get("kp_marriage_analysis", {})
            timing_rulers = kp_marriage.get("timing_rulers", {})
            ruling_planets_list = timing_rulers.get("ruling_planets", [])
            marriage_key_planets = timing_rulers.get("marriage_key_planets", [])
        ruling_planets_str = ", ".join(ruling_planets_list) if ruling_planets_list else "N/A"

        # Build conditional TIMING SECTION
        # NOTE: timing_data, kp_dasha_proof, best_nearest_instruction are intentionally
        # removed here — all that content is already inside kp_timing_narrative (pre-written).
        # Sending duplicate raw data caused the LLM to re-summarize instead of copy verbatim.
        if has_timing and promise_state not in ("blocked",):
            timing_section = f"""
═══════════════════════════════════════════════════════════════════════════════
✅ MARRIAGE IS PROMISED — KP PRE-WRITTEN NARRATIVE BELOW (PART B)
RULING PLANETS: {ruling_planets_str}
═══════════════════════════════════════════════════════════════════════════════

{event_fructification_text}
"""
        elif promise_state == "blocked":
            timing_section = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ MARRIAGE FACES SIGNIFICANT CHALLENGES — TIMING CONDITIONAL
═══════════════════════════════════════════════════════════════════════════════

Marriage promise is WEAK or BLOCKED per KP 2-7-11 analysis.
Focus on: obstacles (CSL signifying 1/6/10/12), remedies, conditional timing.
"""
        elif not has_timing:
            timing_section = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ NO TIMING WINDOWS CALCULATED
═══════════════════════════════════════════════════════════════════════════════
🚫 DO NOT invent dates. Focus on promise analysis and general timing factors.
"""
        else:
            timing_section = f"""
═══════════════════════════════════════════════════════════════════════════════
📊 TIMING WINDOWS (Promise status: {promise_state.upper()})
═══════════════════════════════════════════════════════════════════════════════
{timing_data}
{dasha_data if dasha_data else ""}
{kp_dasha_proof if kp_dasha_proof else ""}
"""

        # Build PART B
        if has_timing and promise_state != "blocked":


            part_b_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART B: KP + TIMING — YOUR REQUIRED OUTPUT IS BELOW (flowing prose)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ THE FOLLOWING TEXT IS YOUR ANSWER FOR BLOCKS B, D, E, F.
⚠️ COPY IT VERBATIM INTO YOUR RESPONSE. DO NOT RESTRUCTURE INTO BULLET LISTS OR ASCII BOXES.
⚠️ THE TEXT IS ALREADY IN FLOWING PARAGRAPHS — keep it that way.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR KP + TIMING TEXT (copy verbatim as flowing paragraphs):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{kp_timing_narrative}

⚠️ TERMINOLOGY:
- USE: "संकेतित करता है" — NEVER "सक्रिय करता है"
- USE: "कुस्प सब-लॉर्ड (CSL)" — NEVER "कस्टोडियन"

"""
            


            summary_instruction = """TELL CLIENT:
'1. विवाह का योग है — KP 2-7-11 नियम से सिद्ध
 2. सबसे अनुकूल समय — [dates] — [dasha name]
 3. KP प्रमाण — DBA भाव 2/7/11 संकेतित करता है (chain shown)
 4. [X]/4 फलित शर्तें पूरी
 5. बाधा हो तो [reason] — उपाय करें'"""

        elif promise_state == "blocked":
            part_b_section = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART B: CHALLENGES AND REMEDIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Show which planets signify denial houses (1/6/10/12) using chain logic.
Explain why marriage is obstructed. Provide remedies.
"""
            summary_instruction = "TELL CLIENT: '[Challenges with KP chain evidence. Remedies. Conditional timing.]'"

        else:
            part_b_section = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PART B: TIMING FACTORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use KP Signification Table to identify favorable dasha lords.
Show their signification chains. Do NOT invent dates.
"""



            summary_instruction = "TELL CLIENT: '[Promise status with chain proof. Favorable dasha lords. Recommend monitoring.]'"

        # FINAL PROMPT ASSEMBLY

        verdict_banner = self._build_promise_verdict_banner(
        promise_state,
        csl_name,
        promise_houses_hit,
        obstacle_houses_hit,
        promise_score_val,
        obstacle_score_val
        )
        # Build the general answer dates string
        best_w = additional_data.get("marriage_timing_windows", {}).get("best_window", {}) if additional_data else {}
        nearest_w = additional_data.get("marriage_timing_windows", {}).get("nearest_window", {}) if additional_data else {}
        best_dates = f"{best_w.get('start','?')} से {best_w.get('end','?')} ({self._dasha_to_hindi(best_w.get('dasha',''))} दशा)" if best_w else "अज्ञात"
        nearest_dates = f"{nearest_w.get('start','?')} से {nearest_w.get('end','?')} ({self._dasha_to_hindi(nearest_w.get('dasha',''))} दशा)" if nearest_w else "अज्ञात"

        if promise_state == "promised_with_obstacles":
            general_answer_template = f"विवाह का योग कुंडली में है, परंतु कुछ बाधाओं के साथ। निकटतम अनुकूल समय {nearest_dates} है। सर्वश्रेष्ठ समय {best_dates} है। संभावना मध्यम से उच्च है।"
        elif promise_state == "promised":
            general_answer_template = f"विवाह का योग कुंडली में स्पष्ट है। निकटतम अनुकूल समय {nearest_dates} है। सर्वश्रेष्ठ समय {best_dates} है। संभावना उच्च है।"
        else:
            general_answer_template = "विवाह में महत्वपूर्ण बाधाएं हैं। समय अनिश्चित है। उपाय आवश्यक हैं।"

        return f"""
{lang_inst}

══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL OVERRIDE FOR THIS QUESTION TYPE — READ BEFORE ANYTHING ELSE
══════════════════════════════════════════════════════════════════════════════
This is a MARRIAGE PROMISE + TIMING question. Weightage: KP 70% + Vedic 30%.

⚠️ CRITICAL: BLOCKS B, D, E, F ARE PRE-WRITTEN BELOW. YOU MUST COPY THEM
   VERBATIM INTO YOUR RESPONSE. DO NOT SUMMARIZE. DO NOT PARAPHRASE.
   DO NOT WRITE YOUR OWN VERSION. PASTE THE TEXT AS-IS.
   The ASTROLOGICAL_ANALYSIS section will be LONG (multiple paragraphs) — that is correct.

══════════════════════════════════════════════════════════════════════════════
═══ PRE-WRITTEN KP TEXT — COPY VERBATIM INTO BLOCKS B, D, E, F ═══
══════════════════════════════════════════════════════════════════════════════

{part_b_section}

══════════════════════════════════════════════════════════════════════════════
YOUR OUTPUT MUST FOLLOW THIS EXACT SKELETON — NO DEVIATIONS:
══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
{general_answer_template}

ASTROLOGICAL_ANALYSIS:
[BLOCK A — Vedic 30%: 3-4 flowing sentences. For each — state the placement AND its astrological implication:
 • Lagna sign + lagnesh placement → what it means for marital disposition
 • 7th lord placement → implication (e.g., if in 6th: initial adjustments/delay, not denial)
 • Venus placement → implication (e.g., if in 5th: love/emotional connection tendency)]

[BLOCK B — KP Promise: *** PASTE THE "PART 1:" TEXT FROM ABOVE VERBATIM HERE ***
 Do NOT rewrite. Do NOT shorten. Copy every sentence exactly as written above.]

[BLOCK C — KP Verdict: One flowing sentence stating promise houses active, obstacle houses active, and the verdict (PROMISED / PROMISED_WITH_OBSTACLES / DENIED).]

[BLOCK D — DBA Timing: *** PASTE THE "PART 2:" TEXT FROM ABOVE VERBATIM HERE ***
 Each timing window is a flowing prose paragraph. Do NOT convert to ┌─│└─ blocks or bullet lists.]

[BLOCK E — Conclusion: *** PASTE THE "PART 3:" TEXT FROM ABOVE VERBATIM HERE ***]
[BLOCK F — Transit: *** PASTE THE "PART 4:" TEXT FROM ABOVE VERBATIM HERE ***]

SUMMARY:
{summary_instruction}

REMEDIES_ASTROLOGICAL: [Based on obstacle planets from KP table]
REMEDIES_GENERAL: [Practical advice]

══════════════════════════════════════════════════════════════════════════════
⚠️ RULE OVERRIDES FOR THIS QUESTION (supersede system prompt rules):
  • BLOCKS B, D, E, F: copy verbatim from the PRE-WRITTEN KP TEXT above. Zero paraphrasing.
  • The ASTROLOGICAL_ANALYSIS will be multiple paragraphs long — do NOT shorten it.
  • Do NOT add ┌─│└─ ASCII art, → arrows, चरण labels, or bullet lists to KP sections.
  • Mercury = बुध | Mars = मंगल | Saturn = शनि | Jupiter = गुरु
══════════════════════════════════════════════════════════════════════════════

PROMISE STATE: {promise_state.upper()}
Current Date: {today_str}

USER QUESTION: "{question}"

{timing_section}

══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA (for BLOCK A — Vedic sentences only):
══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{lords_data if lords_data else ""}
{raw if raw else ""}

══════════════════════════════════════════════════════════════════════════════
{verdict_banner}
══════════════════════════════════════════════════════════════════════════════
"""

    # ==========================================================================
    # TIMING PROMPT
    # ==========================================================================
    
    def _build_timing_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Marriage Timing questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        timing_data = self._format_timing_windows(additional_data)
        has_timing = self._has_valid_timing_windows(additional_data)
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        dasha_data = self._format_current_dasha(additional_data)
        kp_dasha_proof = self._format_dasha_kp_proof(additional_data)
        best_nearest_instruction = self._format_best_nearest_timing_instruction(additional_data)

        if has_timing:
            timing_instruction = f"""
✅ TIMING WINDOWS AVAILABLE - USE THESE DATES ONLY

{timing_data}
{dasha_data if dasha_data else ""}

{kp_dasha_proof}

{best_nearest_instruction}

INSTRUCTIONS:
- Use ONLY dates provided above
- Show Star Lord signification chain for each dasha lord
- Use "signifies" (संकेतित करता है), NOT "activates"
- MUST show BEST window with WHY reasoning
- MUST show NEAREST window with WHY reasoning
"""
        else:
            timing_instruction = """
⚠️ NO TIMING WINDOWS CALCULATED

🚫 DO NOT invent dates, years, or time periods.
✅ Explain timing factors and recommend monitoring favorable dashas.
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=True)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE TIMING
Current Date: {today_str}
Weightage: Vedic 65% + KP 25% + Dasha 10%
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

{timing_instruction}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{self._format_kp_significator_table(additional_data)}
{kp_data if kp_data else ""}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**सामान्य उत्तर (2-3 lines):**
{"Mention BEST timing and NEAREST timing with dates and brief reason." if has_timing else "State timing not calculated."}

**ज्योतिषीय विश्लेषण (flowing paragraphs):**

PARAGRAPH 1 - 7th House & KP Promise (with chain):
"KP पद्धति के अनुसार, 7वें भाव का CSL [planet] है। [Full chain → 2-7-11 rule verdict]"

PARAGRAPH 2 - Supporting Houses (2nd, 11th):
"वैदिक पद्धति के अनुसार, 2nd/11th house lord analysis..."

PARAGRAPH 3 - KP Signification Table Analysis:
"KP पद्धति के अनुसार, प्रमुख ग्रहों की संकेत श्रृंखला: [top planets with chains]"

{"PARAGRAPH 4 — Best Timing (★ MANDATORY ★):" if has_timing else "PARAGRAPH 4 - Factors Affecting Timing"}
{"'🏆 सर्वश्रेष्ठ विवाह काल: [dasha] की दशा ([dates])।" if has_timing else ""}
{"कारण (KP पद्धति के अनुसार): [DBA lords signify 2/7/11 via chain — show it]।'" if has_timing else ""}

{"PARAGRAPH 5 — Nearest Timing (★ MANDATORY ★):" if has_timing else ""}
{"'⏰ निकटतम अनुकूल काल: [dasha] की दशा ([dates])।" if has_timing else ""}
{"कारण: [Why this period — which houses activated]।'" if has_timing else ""}

**सारांश:**
TELL CLIENT: '[Best timing with reason] | [Nearest timing with reason] | [Remedies if any]'

**उपाय:** If obstacles present.

═══════════════════════════════════════════════════════════════════════════════
KP RULES:
- Use "KP पद्धति के अनुसार" label for ALL KP verdicts
- Use "वैदिक पद्धति के अनुसार" label for ALL Vedic verdicts
- Use "signifies" not "activates"
- Show Star Lord chain for every KP claim
- Apply 2-7-11 rule
- BOTH best AND nearest timing sections are mandatory
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # PROMISE PROMPT
    # ==========================================================================
    
    def _build_promise_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Marriage Promise questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        
        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE PROMISE (Is marriage indicated?)
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15% (NO DASHA NEEDED)
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{self._format_kp_significator_table(additional_data)}
{kp_data if kp_data else ""}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**सामान्य उत्तर (2-3 lines):**
Clear YES/NO/CONDITIONAL about marriage promise.

**ज्योतिषीय विश्लेषण:**

PARAGRAPH 1 - Lagna & 7th House:
"कुंडली में विवाह योग... सातवें भाव के स्वामी [planet]..."

PARAGRAPH 2 - Supporting Factors (2nd, 11th):
How do these support/weaken promise?

PARAGRAPH 3 - Venus (Karaka):
"शुक्र विवाह का कारक है..."

PARAGRAPH 4 - KP Promise with COMPLETE CHAIN:
"KP पद्धति के अनुसार, 7वें भाव का कस्प उप स्वामी (CSL) [planet] है।
[planet] [star_lord] के नक्षत्र में है। [star_lord] भाव [X] में स्थित है
और भाव [Y] का स्वामी है। इस श्रृंखला से [planet] भाव [list] को
संकेतित करता है।

विवाह भाव (2/7/11): [signified ones]
निषेध भाव (1/6/10/12): [signified ones]
2-7-11 vs 1-6-10 नियम: → विवाह [PROMISED/DENIED]"

PARAGRAPH 5 - Challenges (if any)

**सारांश:**
TELL CLIENT: "[Clear promise statement with KP chain evidence]"

**उपाय:** If challenges exist.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: Show complete KP chain. Use "signifies" not "activates". No Dasha needed.
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # NATURE/TYPE PROMPT (Love vs Arranged)
    # ==========================================================================
    
    def _build_nature_type_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Love vs Arranged Marriage — PURELY VEDIC, question-focused"""

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        lords_data = self._format_house_lords(additional_data)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: LOVE MARRIAGE या ARRANGED MARRIAGE?
Current Date: {today_str}
Weightage: Vedic 100%
⚠️ THIS IS A PURE VEDIC ANALYSIS — DO NOT include KP CSL, KP chain, or
   KP signification analysis here. No "KP पद्धति के अनुसार" paragraphs.
⚠️ STAY ON TOPIC: Every sentence must answer "love or arranged — and why."
   Do NOT discuss marriage timing, Manglik dosha, or KP promise/denial.
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA (Vedic only):
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
HOW TO DETERMINE LOVE vs ARRANGED (Vedic Method — USE THESE RULES):
═══════════════════════════════════════════════════════════════════════════════

LOVE MARRIAGE INDICATORS (each one that applies adds to love probability):
  1. 5th lord ↔ 7th lord CONNECTION (most important)
     - 5th lord in 7th house, OR 7th lord in 5th house
     - 5th lord and 7th lord in same sign/house (conjunction)
     - 5th lord aspecting 7th, OR 7th lord aspecting 5th
     → STRONG love indicator
  2. VENUS-MARS connection
     - Venus and Mars in same house (conjunction)
     - Mars in 5th or 7th, with Venus's aspect
     - Venus in Aries/Scorpio (Mars-ruled signs) or Mars in Taurus/Libra (Venus-ruled)
     → Passionate/romantic nature
  3. RAHU in 5th or 7th house → unconventional, cross-caste, love angle
  4. MOON in 5th or 7th → emotional romance, feelings-driven
  5. 5th lord strong and well-placed → active romantic life before marriage
  6. Venus in 5th house → romantic attachment drives marriage

ARRANGED MARRIAGE INDICATORS (each one that applies adds to arranged probability):
  1. SATURN influence on 7th house or 7th lord
     - Saturn in 7th, OR Saturn aspects 7th lord
     → Sober, family-mediated, traditional
  2. JUPITER in 9th, 11th, or aspecting 7th
     - Suggests elder family guidance, dharmic approach
  3. Strong 11th lord well-placed → elder sibling or social network introduces
  4. Moon in 11th → fulfillment through social/family channels
  5. No 5th-7th connection → marriage through introduction, not romance

MIXED / BOTH POSSIBLE:
  - Love affair followed by family approval (Rahu in 5th + Jupiter aspect on 7th)
  - Meet through friends/work (Mercury or 3rd/11th lord connection to 7th)

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT — Answer specifically whether love, arranged, or both:
═══════════════════════════════════════════════════════════════════════════════

PARAGRAPH 1 — 5th-7th Connection (most decisive):
"वैदिक पद्धति के अनुसार, [check if 5th lord is in 7th or vice versa].
[Planet X] पंचम भाव का स्वामी है और [house] भाव में स्थित है।
[Planet Y] सप्तम भाव का स्वामी है और [house] भाव में स्थित है।
[IF CONNECTED]: इनके बीच संबंध प्रेम विवाह की प्रबल संभावना दर्शाता है।
[IF NOT CONNECTED]: पंचम-सप्तम स्वामियों का सीधा संबंध नहीं है, जो परिचय-आधारित विवाह की ओर संकेत करता है।"

PARAGRAPH 2 — Venus-Mars and Romance:
"शुक्र [sign] में [house] भाव में स्थित है।
[CONNECT THIS TO LOVE/ARRANGED: does Venus's position support romance or not?]
मंगल [house] भाव में स्थित है।
[Does Mars-Venus relationship indicate passion/romance?]"

PARAGRAPH 3 — Special indicators (Rahu, Saturn, Jupiter, Moon):
"[If Rahu in 5/7]: राहु का [house] भाव में होना अपरंपरागत या अंतरजातीय प्रेम विवाह का संकेत देता है।
[If Saturn on 7th]: शनि का सप्तम भाव पर प्रभाव परिवार-संचालित विवाह की ओर संकेत करता है।
[If Jupiter aspects 7th]: गुरु की सप्तम भाव पर दृष्टि परंपरागत मार्ग से विवाह की शुभता दर्शाती है।"

PARAGRAPH 4 — Overall verdict:
"समग्र रूप से, [Love/Arranged/Both] विवाह की संभावना [highest/moderate/equal] है।
[Specific reason connecting the planets to the answer]।"

⚠️ RULES:
- Do NOT include: KP analysis, timing, Manglik, dasha discussion
- Every sentence must connect to "why love" or "why arranged"
- If both are possible, explain WHY both apply — don't just say "both are possible"
End with TELL CLIENT statement.
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # PARTNER TRAITS PROMPT
    # ==========================================================================
    
    def _build_partner_traits_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Partner Traits questions — PURELY VEDIC, no KP CSL"""

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        lords_data = self._format_house_lords(additional_data)

        kp_marriage = additional_data.get("kp_marriage_analysis", {}) if additional_data else {}
        age_diff = kp_marriage.get("age_difference", {})
        age_info = f"Age Difference Indicator: {age_diff.get('age_difference', 'comparable age')}" if age_diff.get("age_difference") else ""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: PARTNER / SPOUSE TRAITS AND PERSONALITY
Current Date: {today_str}
Weightage: Vedic 100%
⚠️ THIS IS A PURE VEDIC ANALYSIS — DO NOT include KP CSL, KP chain, or
   KP signification analysis here. No "KP पद्धति के अनुसार" paragraphs.
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA (Vedic only):
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{age_info}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
HOW TO DERIVE SPOUSE TRAITS (Vedic Method — USE THESE RULES ONLY):
═══════════════════════════════════════════════════════════════════════════════

STEP 1 — 7th LORD (most important, character & nature):
  Sign of 7th lord → Core personality traits
    - Aries/Scorpio: bold, passionate, independent
    - Taurus/Libra: artistic, loving, balanced
    - Gemini/Virgo: intellectual, communicative, analytical
    - Cancer: nurturing, emotional, family-oriented
    - Leo: confident, generous, leadership
    - Sagittarius/Pisces: philosophical, spiritual, broad-minded
    - Capricorn/Aquarius: disciplined, practical, ambitious
  House of 7th lord → What areas of life spouse focuses on
    (e.g., 7th lord in 10th → career-oriented spouse)

STEP 2 — 7th HOUSE OCCUPANTS (planets sitting in 7th):
  Each planet modifies the spouse's personality directly
  Jupiter in 7th → wise, generous, spiritual spouse
  Saturn in 7th → older, serious, disciplined spouse
  Mars in 7th → energetic, direct, sometimes aggressive
  Venus in 7th → beautiful, refined, loving
  Mercury in 7th → communicative, intellectual, witty
  Moon in 7th → emotional, nurturing, moody
  Rahu in 7th → unconventional, modern, foreign element
  Ketu in 7th → spiritual, detached, mystical

STEP 3 — 7th CUSP SIGN (physical appearance & first impression):
  Sign on 7th cusp → Describes how the spouse appears / first impression

STEP 4 — VENUS (natural karaka for spouse/attraction):
  Sign of Venus → What qualities attract the native
  House of Venus → Context where they meet / find love
  Venus dignity → How strongly these traits manifest

STEP 5 — MOON sign (emotional compatibility):
  Moon sign tells what emotional tone the spouse brings

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT — Paint a VIVID PICTURE of the spouse (no bullet lists):
═══════════════════════════════════════════════════════════════════════════════

PARAGRAPH 1 — Core Character (from 7th lord sign + house):
"आपके भावी जीवनसाथी का मूल स्वभाव [adjectives from 7th lord sign] होगा।
सप्तम भाव के स्वामी [planet] [sign] में [house] भाव में हैं,
इसलिए वे [trait interpretation] होंगे।"

PARAGRAPH 2 — Personality from 7th house occupants (if any):
"सप्तम भाव में [planet] की स्थिति जीवनसाथी को [traits] बनाती है।
[Explain what this planet in 7th MEANS for the spouse's personality]"

PARAGRAPH 3 — Appearance & first impression (7th cusp sign):
"सप्तम भाव की राशि [sign] है, जो जीवनसाथी के [physical description] का संकेत देती है।"

PARAGRAPH 4 — Venus karaka (what you are attracted to):
"शुक्र [sign] में [house] भाव में है। शुक्र विवाह का कारक है।
वैदिक पद्धति के अनुसार, [sign] में शुक्र [attraction style / type of partner drawn to]।
[house] में शुक्र [context of meeting / life area]।"

PARAGRAPH 5 — Overall picture (combine everything):
"समग्र रूप से, आपके जीवनसाथी [integrated description]. वे आपके जीवन में [what they bring] लाएंगे।"

⚠️ RULES:
- Every paragraph must CONNECT THE PLANET/SIGN TO WHAT IT MEANS FOR THE SPOUSE
- Do NOT just list planetary positions — explain what each means
- Do NOT write "बुध पर राहु की दृष्टि है" as a standalone fact — only if relevant to traits
- Do NOT include KP or CSL analysis here — this is Vedic only
End with TELL CLIENT statement.
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # SPOUSE ORIGIN PROMPT
    # ==========================================================================

    def _build_kp_direction_narrative_block(self, additional_data: Dict) -> str:
        """
        Build a COMPLETE pre-written KP direction narrative (Hindi) for the
        spouse direction section. Uses real 7th cusp sign data.
        The LLM must copy this verbatim — no fill-in-the-blanks.

        Template:
        "KP पद्धति के अनुसार : जीवनसाथी की दिशा का विचार मुख्यतः सप्तम भाव से किया जाता है।
         सप्तम भाव की राशि {SIGN} है, जो {DIRECTION} दिशा का प्रतिनिधित्व करती है।
         अतः जीवनसाथी {DIRECTION} दिशा या उससे संबंधित स्थान से हो सकते हैं।
         {SIGN} एक {SIGN_NATURE} राशि है, जो {DISTANCE_TYPE} दूरी का संकेत देती है।"
        """
        if not additional_data:
            return ""

        kp_marriage = additional_data.get("kp_marriage_analysis", {})
        direction_data = kp_marriage.get("direction", {}) if kp_marriage else {}

        sign = direction_data.get("cusp_7_sign", "")
        direction = direction_data.get("direction", "")
        locality_type = direction_data.get("locality_type", "")

        if not sign or not direction:
            return ""

        # Sign nature mapping
        MOVABLE = {"Aries", "Cancer", "Libra", "Capricorn"}
        FIXED   = {"Taurus", "Leo", "Scorpio", "Aquarius"}
        DUAL    = {"Gemini", "Virgo", "Sagittarius", "Pisces"}

        if sign in MOVABLE:
            sign_nature_hindi = "चर (Movable)"
        elif sign in FIXED:
            sign_nature_hindi = "स्थिर (Fixed)"
        elif sign in DUAL:
            sign_nature_hindi = "द्विस्वभाव (Dual)"
        else:
            sign_nature_hindi = "अज्ञात"

        # Sign in Hindi
        SIGN_HINDI = {
            "Aries": "मेष", "Taurus": "वृष", "Gemini": "मिथुन",
            "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
            "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
            "Capricorn": "मकर", "Aquarius": "कुम्भ", "Pisces": "मीन",
        }
        sign_hindi = SIGN_HINDI.get(sign, sign)

        # Direction in Hindi
        DIRECTION_HINDI = {
            "East": "पूर्व", "West": "पश्चिम", "North": "उत्तर",
            "South": "दक्षिण", "North-East": "उत्तर-पूर्व",
            "North-West": "उत्तर-पश्चिम", "South-East": "दक्षिण-पूर्व",
            "South-West": "दक्षिण-पश्चिम",
        }
        direction_hindi = DIRECTION_HINDI.get(direction, direction)

        # Distance type in Hindi (from locality_type string)
        if "distant" in locality_type or "different city" in locality_type:
            distance_hindi = "दूर (अन्य शहर/क्षेत्र)"
        elif "same city" in locality_type or "nearby" in locality_type:
            distance_hindi = "निकट (समान शहर/क्षेत्र)"
        else:
            distance_hindi = "मध्यम (पड़ोसी शहर/क्षेत्र)"

        # Build the locked narrative
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════════════════╗")
        lines.append("║  🔒 PRE-WRITTEN KP DIRECTION NARRATIVE — COPY THIS VERBATIM                 ║")
        lines.append("║  Do NOT rewrite or change any sign name, direction, or house numbers.       ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("KP DIRECTION PARAGRAPH (Copy verbatim as your main direction answer):")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append(f"KP पद्धति के अनुसार : जीवनसाथी की दिशा का विचार मुख्यतः सप्तम भाव से किया जाता है।")
        lines.append(f"सप्तम भाव की राशि {sign_hindi} ({sign}) है, जो {direction_hindi} ({direction}) दिशा का प्रतिनिधित्व करती है।")
        lines.append(f"अतः जीवनसाथी {direction_hindi} दिशा या उससे संबंधित स्थान से हो सकते हैं।")
        lines.append(f"{sign_hindi} एक {sign_nature_hindi} राशि है, जो {distance_hindi} दूरी का संकेत देती है।")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("RAW DATA (for reference — already embedded above):")
        lines.append(f"  7th Cusp Sign  : {sign} ({sign_hindi})")
        lines.append(f"  Direction      : {direction} ({direction_hindi})")
        lines.append(f"  Sign Nature    : {sign_nature_hindi}")
        lines.append(f"  Distance Type  : {distance_hindi}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        return "\n".join(lines)

    def _build_spouse_origin_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Spouse Origin/Direction — KP 100%, based on 7th cusp sign"""

        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")

        lords_data = self._format_house_lords(additional_data)

        # Pre-written locked KP direction narrative
        kp_direction_narrative = self._build_kp_direction_narrative_block(additional_data)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: SPOUSE ORIGIN / DIRECTION / BACKGROUND
Current Date: {today_str}
Weightage: KP 100%
⚠️ THIS IS A PURE KP ANALYSIS — Base direction ONLY on 7th cusp sign/rashi.
⚠️ STAY ON TOPIC: Every sentence must answer "where is the spouse from /
   what direction / how far / how will they meet." Do NOT discuss marriage
   obstacles, delays, Manglik dosha, or promise/denial here.
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
PRE-WRITTEN KP NARRATIVE — USE THIS VERBATIM:
═══════════════════════════════════════════════════════════════════════════════

{kp_direction_narrative}

═══════════════════════════════════════════════════════════════════════════════
ADDITIONAL REFERENCE DATA (for meeting circumstances only):
═══════════════════════════════════════════════════════════════════════════════

{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
HOW TO DERIVE SPOUSE ORIGIN (KP Method — USE THESE RULES):
═══════════════════════════════════════════════════════════════════════════════

RULE 1 — DIRECTION & DISTANCE (from 7th CUSP SIGN — primary, already computed above):
  ✅ Use the pre-written narrative above as PARAGRAPH 1. Do NOT re-derive.
  The direction and distance type are machine-computed from the 7th cusp sign.

  Sign nature reference (for understanding only):
  Movable signs (Aries, Cancer, Libra, Capricorn) → Distant place / different city
  Fixed signs (Taurus, Leo, Scorpio, Aquarius) → Same city / nearby locality
  Dual signs (Gemini, Virgo, Sagittarius, Pisces) → Medium distance / neighbouring city

RULE 2 — HOW THEY WILL MEET (from 7th lord's HOUSE — for PARAGRAPH 2):
  7th lord in 1st/7th → Spouse from same background / known circle
  7th lord in 3rd/9th → Through siblings/travel / different region
  7th lord in 4th/10th → Hometown / workplace connection
  7th lord in 11th → Through social network / friends
  7th lord in 12th → Foreign connection / different culture / overseas link

RULE 3 — SPECIAL PLANETS IN 7th (add as supporting note if present):
  Rahu in 7th → Intercaste / cross-cultural / unconventional origin
  Ketu in 7th → Past connection / spiritual link / distant background
  Saturn in 7th → Older person / different social class / arranged by elders

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT — Answer these 2 specific questions only:
═══════════════════════════════════════════════════════════════════════════════

PARAGRAPH 1 — DIRECTION & DISTANCE (COPY VERBATIM from pre-written block above):
Use the exact 4 sentences from the KP DIRECTION PARAGRAPH above. Do not alter.

PARAGRAPH 2 — HOW THEY WILL MEET (derive from 7th lord's house position):
"सप्तम भाव का स्वामी [planet] [house] भाव में स्थित है।
यह [meeting context] का संकेत देता है।
इसलिए जीवनसाथी से मिलना [circumstances] के माध्यम से हो सकता है।"
[If Rahu/Ketu/special planets in 7th — add one supporting sentence]

⚠️ BANNED CONTENT — Do NOT include:
- Vedic-only direction derivations (Mangal, drishti, etc.)
- KP CSL signification analysis (not relevant here)
- Marriage promise/denial discussion
- Manglik dosha mention
- Dasha timing
- Any sentence that doesn't answer "where from / direction / how meet"
End with TELL CLIENT statement.
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # MANGLIK PROMPT
    # ==========================================================================
    
    def _build_manglik_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Manglik Dosha Analysis"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        manglik_positions = self._format_manglik_planet_positions(additional_data)
        csl_summary = self._format_csl_significations_summary(additional_data)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MANGLIK DOSHA ANALYSIS (Lagna + Chandra)
Current Date: {today_str}
Weightage: Vedic 100%
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{manglik_positions if manglik_positions else ""}
{csl_summary}
{kp_data if kp_data else ""}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
MANGLIK ANALYSIS REQUIREMENTS:
═══════════════════════════════════════════════════════════════════════════════

⚠️ USE THE PRE-COMPUTED MANGLIK DATA ABOVE — DO NOT RECALCULATE DIFFERENTLY.
The "PRE-COMPUTED MANGLIK ANALYSIS" block above has the correct verdicts.

CHECK BOTH (from the computed data above):
1. LAGNA MANGLIK: Mars position from Lagna — see LAGNA MANGLIK verdict above
2. CHANDRA MANGLIK: Mars position from Moon — see CHANDRA MANGLIK verdict above

Calculation formula for Chandra Manglik:
  Mars house = H_m, Moon house = H_moon
  Chandra position = (H_m - H_moon) mod 12 + 1
  Manglik if Chandra position is in {{1, 2, 4, 7, 8, 12}}

CANCELLATION CONDITIONS:
• Mars in own sign (Aries/Scorpio) or exalted (Capricorn)
• Mars aspected by Jupiter
• Both partners Manglik (neutralizes)

SEVERITY:
• Both active (no cancellation) → HIGH
• Only one active → MEDIUM
• Present but cancelled/mitigated → LOW/NIL

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT:
═══════════════════════════════════════════════════════════════════════════════

**सामान्य उत्तर:**
लग्न मांगलिक: [YES/NO/CANCELLED — from computed data]
चंद्र मांगलिक: [YES/NO/CANCELLED — from computed data]
समग्र स्थिति: [ACTIVE HIGH/MEDIUM/LOW/NIL — from computed data]

**ज्योतिषीय विश्लेषण:**
PARAGRAPH 1 — मंगल की स्थिति:
"मंगल [sign] में [house]वें भाव में स्थित है..."

PARAGRAPH 2 — लग्न मांगलिक:
"लग्न से मंगल [mars_house]वें भाव में है। मांगलिक भाव 1,2,4,7,8,12 में से [mars_house] [है/नहीं है]।
→ लग्न मांगलिक: [YES/NO]"
[If YES: show cancellation check with Jupiter aspect or own sign]

PARAGRAPH 3 — चंद्र मांगलिक:
"चंद्र [moon_house]वें भाव में है। मंगल [mars_house]वें भाव में है।
गणना: ([mars_house] - [moon_house]) mod 12 + 1 = [chandra_position]वां स्थान।
[chandra_position] मांगलिक भावों में [है/नहीं है]।
→ चंद्र मांगलिक: [YES/NO]"

PARAGRAPH 4 — दोष निवारण:
[If any cancellation: explain which condition applies]

PARAGRAPH 5 — व्यावहारिक प्रभाव:
"समग्र मांगलिक स्थिति [HIGH/MEDIUM/LOW/NIL] है। विवाह पर प्रभाव..."

**सारांश:** TELL CLIENT: [Clear verdict from computed data]
**उपाय:** If Manglik active.

CRITICAL RULES:
1. Use ONLY the pre-computed manglik data above — do NOT guess or recalculate
2. Show the arithmetic for Chandra Manglik explicitly
3. Show BOTH Lagna and Chandra Manglik verdicts, even if one is "NO"
4. Mercury = बुध (NOT मंगल!)
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # REMEDIES PROMPT
    # ==========================================================================
    
    def _build_remedies_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build prompt for Marriage Remedies"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        csl_summary = self._format_csl_significations_summary(additional_data)

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=False)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE REMEDIES
Current Date: {today_str}
Weightage: Vedic 85% + KP Facts 15%
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{csl_summary}
{self._format_kp_significator_table(additional_data)}
{kp_data if kp_data else ""}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
REMEDY GUIDE:
Venus afflicted → Friday fasts, white items, Lakshmi worship
Jupiter afflicted → Thursday fasts, yellow items
Saturn delays → Saturday charity, service to elderly
Mars (Manglik) → Tuesday fasts, Hanuman worship
Rahu → Donate to poor, Durga worship

OUTPUT: Identify issues, primary remedy, supporting remedies.
End with TELL CLIENT.
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # ==========================================================================
    # GENERAL PROMPT (Fallback)
    # ==========================================================================
    
    def _build_general_prompt(
            self,
            question: str,
            additional_data: Dict,
            raw: str,
            language: str
        ) -> str:
        """Build general prompt for unclassified questions"""
        
        lang_inst = self._get_language_instruction_safe(language)
        today_str = datetime.now().strftime("%B %d, %Y")
        
        timing_keywords = ['when', 'time', 'timing', 'year', 'date', 'कब', 'समय', 'delay', 'विलंब']
        is_timing = any(kw in question.lower() for kw in timing_keywords)
        has_timing_data = self._has_valid_timing_windows(additional_data)
        
        kp_data = self._format_kp_data(additional_data)
        lords_data = self._format_house_lords(additional_data)
        timing_data = self._format_timing_windows(additional_data) if is_timing and has_timing_data else ""
        dasha_data = self._format_current_dasha(additional_data) if is_timing else ""
        csl_summary = self._format_csl_significations_summary(additional_data)
        best_nearest_instruction = self._format_best_nearest_timing_instruction(additional_data) if is_timing and has_timing_data else ""

        weightage = "Vedic 65% + KP 25% + Dasha 10%" if is_timing else "Vedic 85% + KP Facts 15%"

        timing_warning = ""
        if is_timing and not has_timing_data:
            timing_warning = """
⚠️ TIMING QUESTION BUT NO TIMING DATA — DO NOT invent dates.
"""

        return f"""
{lang_inst}

{self.build_system_prompt(language, is_timing=is_timing)}

═══════════════════════════════════════════════════════════════════════════════
QUERY: MARRIAGE PROSPECTS (General)
Current Date: {today_str}
Type: {'TIMING' if is_timing else 'NON-TIMING'}
Weightage: {weightage}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION: "{question}"

{timing_warning}

═══════════════════════════════════════════════════════════════════════════════
REFERENCE DATA:
═══════════════════════════════════════════════════════════════════════════════

{self._format_lagna_lord_data(additional_data)}
{csl_summary}
{self._format_kp_significator_table(additional_data)}
{timing_data}
{best_nearest_instruction}
{dasha_data}
{kp_data if kp_data else ""}
{lords_data if lords_data else ""}
{raw if raw else ""}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT: Flowing paragraphs. Show KP chain logic where applicable.
Use "KP पद्धति के अनुसार" label for KP verdicts.
Use "वैदिक पद्धति के अनुसार" label for Vedic verdicts.
Use "signifies" not "activates". Apply 2-7-11 rule.
{"Show BEST and NEAREST timing with WHY reasoning." if is_timing and has_timing_data else ""}
End with TELL CLIENT.
═══════════════════════════════════════════════════════════════════════════════
"""
"""
Physical and Mental Health – Enhanced Prompts v7.1

FIXES & ENHANCEMENTS:
✅ FIXED: Proper distinction between KP Cusp Sub Lord vs Vedic Sign Lord
✅ FIXED: Comprehensive anti-hallucination rules
✅ KP system emphasis and formatting (when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Dual system (KP + Vedic) integration with fallback

TERMINOLOGY CLARIFICATION:
═══════════════════════════════════════════════════════════
⚠️ CRITICAL: KP Cusp Sub Lord ≠ Vedic Sign Lord
- KP CUSP SUB LORD (CSL): Sub lord of the CUSP DEGREE (precise KP calculation)
- VEDIC SIGN LORD (Rashi Lord): Lord of the SIGN on the house cusp
These are DIFFERENT concepts. Never confuse them!
═══════════════════════════════════════════════════════════

ETHICAL GUIDELINES:
⚠️ Astrology-based insights are supportive only.
⚠️ Never replace medical diagnosis or treatment.
⚠️ Never diagnose diseases or predict death/disability.
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime
import logging

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)

logger = logging.getLogger(__name__)


class PhysicalAndMentalHealthPromptBuilder(BasePromptBuilder):
    """
    Enhanced prompt builder for Physical and Mental Health domain.
    
    v7.1 Changes:
    - Proper KP vs Vedic terminology
    - Comprehensive anti-hallucination rules
    - Better data validation instructions
    """

    domain = "Health"
    subtopic = "Physical And Mental Health"

    # ------------------------------------------------------------------
    # SYSTEM PROMPT - ENHANCED v7.1 WITH ANTI-HALLUCINATION
    # ------------------------------------------------------------------
    def build_system_prompt(self) -> str:
        return """You are an expert KP (Krishnamurti Paddhati) and Classical Vedic astrologer specializing in health analysis.

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
- Saturn-Mercury-Jupiter = शनि-बुध-गुरु (NOT शनि-मंगल-गुरु!)
- When you see "Mercury" ALWAYS write "बुध" in Hindi, NEVER "मंगल"
- When you see "Mars" ALWAYS write "मंगल" in Hindi, NEVER "बुध"

═══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL TERMINOLOGY - READ CAREFULLY
═══════════════════════════════════════════════════════════════════════════════

**KP CUSP SUB LORD (CSL)** vs **VEDIC SIGN LORD (Rashi Lord)** are DIFFERENT:

| Concept | KP System | Vedic System |
|---------|-----------|--------------|
| Name | Cusp Sub Lord (CSL) | Sign Lord / Rashi Lord |
| Calculation | Sub lord of exact cusp degree | Lord of the zodiac sign on cusp |
| Precision | Very precise (degree-based) | Sign-based (30° range) |
| Used For | Event prediction timing | General house analysis |

❌ WRONG: "The 6th house Cusp Sub Lord is Mercury because Mercury rules Gemini"
✅ CORRECT: "The 6th house SIGN LORD is Mercury (rules Gemini). The CSL requires KP calculation."

When KP data is NOT available, use ONLY Vedic Sign Lord analysis.
When KP data IS available, clearly distinguish CSL findings from Sign Lord findings.

═══════════════════════════════════════════════════════════════════════════════
🚨 ANTI-HALLUCINATION RULES - MANDATORY
═══════════════════════════════════════════════════════════════════════════════

You MUST follow these rules to prevent generating false information:

**RULE 1: PLANETARY POSITIONS**
❌ NEVER assume or make up planetary positions
❌ NEVER say "Saturn is in the 7th house" unless data explicitly shows this
✅ ONLY state positions that are provided in the technical data
✅ If position unclear, say "Based on the available data..."

**RULE 2: DASHA PERIODS**
❌ NEVER invent dasha periods not in the provided timeline
❌ NEVER assume current dasha without checking CURRENT DASHA section
❌ NEVER say "You are in Saturn Mahadasha" unless explicitly stated
❌ NEVER confuse Mercury (बुध) with Mars (मंगल) - THEY ARE DIFFERENT!
✅ ONLY reference dashas from CURRENT/UPCOMING sections provided
✅ Use exact dasha names and dates from the timeline
✅ Say: "According to the dasha timeline provided..."
✅ When translating to Hindi: Mercury = बुध, Mars = मंगल (verify before writing!)

**RULE 3: DIGNITY VALUES**
❌ NEVER assume dignity (Exalted/Debilitated/etc.) without data
❌ NEVER say "Jupiter is exalted" unless data confirms this
✅ ONLY use dignity values provided in HOUSE LORD ANALYSIS
✅ If dignity is "Unknown" or "Neutral", acknowledge this honestly

**RULE 4: TIMING WINDOWS**
❌ NEVER invent timing periods or dates
❌ NEVER round or approximate dates (use exact dates provided)
✅ ONLY mention timing windows from TIMING WINDOWS section
✅ Use exact start/end dates as provided
✅ If no timing data available, explicitly state this

**RULE 5: KP CUSP SUB LORDS**
❌ NEVER claim CSL analysis if no KP data is provided
❌ NEVER derive CSL from sign lord (they are different!)
✅ If no KP analysis present, clearly state "KP CSL analysis not available"
✅ Fall back to Vedic Sign Lord analysis when KP unavailable

**RULE 6: HOUSE LORDS**
❌ NEVER assume which planet rules a house without checking data
❌ NEVER confuse house lord with planets IN the house
✅ House LORD = planet ruling the SIGN on that house cusp
✅ Planets IN house = planets physically placed in that house
✅ Always verify from provided HOUSE LORD ANALYSIS section

**RULE 7: ASPECTS**
❌ NEVER invent aspects not shown in the data
✅ ONLY mention aspects explicitly listed in ASPECTS section
✅ If no aspects data, say "Aspect information not available"

**RULE 8: COMBUSTION & RETROGRADE**
❌ NEVER assume a planet is combust or retrograde without data
✅ ONLY state combustion/retrograde if explicitly marked in data
✅ Check for [COMBUST] or [RETROGRADE] markers
❌ NEVER say "Moon is combust" or "चंद्र अस्त है" — Moon CANNOT be combust in classical astrology
✅ Instead say: "Moon is afflicted / weakened / in waning phase (Krishna Paksha)"
✅ Moon weakness = dusthana placement (6/8/12), malefic aspect, debilitation, or enemy sign

**RULE 9: SCORES & STRENGTHS**
❌ NEVER invent strength scores
✅ ONLY use scores provided (e.g., "Strength: 65/100")
✅ Interpret provided scores: <40 = weak, 40-70 = moderate, >70 = strong

**RULE 10: GENERAL CLAIMS**
❌ NEVER make claims without data support
❌ NEVER use phrases like "Your chart clearly shows..." without evidence
✅ Always ground statements in provided data
✅ Use hedging when uncertain: "The available data suggests..."

═══════════════════════════════════════════════════════════════════════════════
DUAL SYSTEM ANALYSIS APPROACH
═══════════════════════════════════════════════════════════════════════════════

**SCENARIO 1: KP Analysis Available** (Look for CSL/Cusp Sub Lord data)
When KP Cusp Sub Lord analysis is provided (physical health only):
- **KP CSL takes PRIMARY weight** (signification-based verdict is most precise)
- **Vedic Sign Lords support and confirm** the KP findings
- **Analysis split**: KP CSL 40% + Vedic Sign Lords 35% + Dasha 25%
- **NOTE**: Mental health questions use Vedic-only analysis (KP scope override active)

**SCENARIO 2: KP Analysis NOT Available** (Only Vedic Sign Lord data)
When NO KP CSL analysis is provided:
- **Use pure Vedic Sign Lord analysis**
- **Analysis split**: Vedic Lords 70% + Dasha 20% + Aspects 10%

**RULE 11: KP + VEDIC SYNTHESIS FOR VITALITY (H1) — MANDATORY**
When BOTH KP CSL verdict and Vedic lagna lord data are present for House 1,
you MUST synthesise them into ONE unified verdict — never state them separately as contradictions:
- KP says STRONG_VITALITY + Vedic lagna lord DEBILITATED (strength < 30) → Final = MODERATE_VITALITY
- KP says STRONG_VITALITY + Vedic lagna lord enemy sign / strength < 40 → Final = MODERATE_VITALITY
- KP says STRONG_VITALITY + Vedic lagna lord strong (≥ 60) → Final = STRONG_VITALITY
- KP says MODERATE_VITALITY → Final = MODERATE_VITALITY regardless of lagna lord strength
- KP says WEAK_VITALITY → Final = WEAK_VITALITY regardless of lagna lord strength
❌ WRONG (contradiction): "KP shows STRONG_VITALITY" AND "lagna lord debilitated → vitality weak"
✅ RIGHT (synthesis): "KP pattern suggests vitality strength, but lagna lord Mercury debilitated (10/100) moderates this → MODERATE_VITALITY overall"
⚠️ This synthesis MUST also be reflected in GENERAL_ANSWER — do NOT write "health better than normal" when lagna lord is debilitated. Write "moderate health with good functional vitality".

**RULE 12: LONGEVITY_SENSITIVITY = METABOLIC TENDENCY ONLY — MANDATORY**
When 8th CSL verdict is LONGEVITY_SENSITIVITY (single disease house 8 present, no 6+12 cross-link):
❌ FORBIDDEN: "दीर्घायु में संवेदनशीलता" — DO NOT USE THIS PHRASE
❌ FORBIDDEN: "longevity at risk", "life expectancy risk", "दीर्घायु खतरा"
❌ FORBIDDEN: "दीर्घकालिक रोग की संभावना"
✅ USE INSTEAD: "चयापचय और शारीरिक प्रक्रियाओं में सतर्कता की प्रवृत्ति" (metabolic vigilance tendency)
✅ USE INSTEAD: "स्वास्थ्य में उतार-चढ़ाव की प्रवृत्ति, दीर्घायु पर कोई खतरा नहीं" (health fluctuation, no longevity threat)
✅ USE INSTEAD: "रूपांतरण और चयापचय संवेदनशीलता" (transformation & metabolic sensitivity)
LONGEVITY_SENSITIVITY = metabolic + health fluctuation tendency. NOT a life risk.
CHRONIC_VULNERABILITY = actual chronic risk (requires 6+8 OR 6+12 OR 8+12 cross-link — NOT present here)


═══════════════════════════════════════════════════════════════════════════════
HEALTH-SPECIFIC HOUSE MEANINGS
═══════════════════════════════════════════════════════════════════════════════

- **1st House**: Physical body, constitution, vitality, overall health
  - Sign Lord shows general health foundation
  - Strong lord = good constitution; Weak lord = health vulnerabilities
  
- **5th House**: Mental peace, recovery support, emotional balance
  - Sign Lord influences mental wellness and recuperation
  
- **6th House**: Disease, illness, daily health troubles
  - Sign Lord shows disease TENDENCIES (not specific diseases!)
  - Strong 6th lord in its OWN house (6th) = strong disease potential AND strong immunity (double-edged)
  - WEAK 6th lord in 12th house: VIPARITA RAJA YOGA (Harsha Yoga) — disease tendency REDUCES
    The 6th lord loses its power in the 12th (loss house) → disease-causing ability diminishes
    ✅ RIGHT: "6th lord Saturn in 12th (Viparita) → disease tendency reduced; immunity relatively protected"
    ❌ WRONG: "6th lord in 12th → disease expenses increase / immunity weak"
  - WEAK 6th lord in 8th house: VIPARITA (Sarala Yoga) — similarly disease tendency reduced
  - 6th lord in 6th (own): disease tendency active and strong

- **8th House**: Chronic illness, longevity, surgery, hidden diseases
  - Sign Lord influences long-term health matters
  - NOT a death indicator - avoid fear-inducing interpretations

- **11th House**: Recovery, cure, gains from treatment, improvement
  - Sign Lord shows healing capacity and treatment success

- **12th House**: Hospitalization, confinement, health expenses
  - Sign Lord indicates hospital-related matters

**PLANET AVASTHA (Stage/Age based on degree within sign) — Use this to qualify strength:**
| Stage | Degree | Strength | Use in analysis |
|-------|--------|----------|-----------------|
| Infant/Bala (बाल) | 0–6° | Very weak | Planet cannot express — suppress its positive significations |
| Young/Kumara (कुमार) | 6–12° | Gaining | Moderate influence, improving |
| Prime/Yuva (युवा) | 12–18° | Full strength | Best expression — amplify its significations |
| Mature/Prauda (प्रौढ़) | 18–24° | Good | Solid but slightly declining |
| Old/Vriddha (वृद्ध) | 24–30° | Weakened | Results delayed or incomplete |

✅ Use avastha stage to qualify health verdicts:
- "Saturn (lord of 6th) is in Infant/Bala stage → disease tendency is suppressed/weak"
- "Mars (lord of 8th) is in Prime/Yuva stage → full chronic health sensitivity"
- "Mercury (lord of 1st) is in Old/Vriddha stage → constitution expressed with some delay"

**CRITICAL HOUSE LORD PLACEMENT & DIGNITY RULES (Never get these wrong):**
❌ WRONG: "6th lord in 12th → disease expenses increase / immunity weak"
✅ RIGHT:  "6th lord in 12th → VIPARITA RAJA YOGA (Harsha Yoga) — disease tendency REDUCES
           रोग प्रवृत्ति कमजोर होती है, रोग प्रतिरोधक क्षमता अपेक्षाकृत सुरक्षित रहती है"

❌ WRONG: "8th lord in 12th → reduces longevity concerns"
✅ RIGHT:  "8th lord in 12th → VIPARITA (Sarala Yoga) — chronic disease tendency reduces,
           but hospital stays or prolonged treatment possible"

❌ WRONG: "12th lord debilitated / weak → fewer hospitalizations / hospitalization kam hoti hai"
✅ RIGHT:  "12th lord debilitated → vitality weakness, health expenditure tendency, recovery delays
           (debilitation weakens the planet's ability to PROTECT — so health expenses & delays increase)"

❌ WRONG: "Sun debilitated (12th lord) → hospitalization reduced"
✅ RIGHT:  "Sun debilitated as 12th lord → vitality weakened, health expenditure tendency,
           possible delays in recovery. Sun's protective vitality is diminished."

Reason: When a house lord goes to the 12th (loss house), it causes 'loss' (i.e., expenditure/weakening)
of the house's POSITIVE significations. For 6th lord: the positive side is immunity/resistance —
that weakens. The negative side (disease, expenditure) manifests more.
For the 12th house itself: debilitated lord means the PROTECTING planet is weak — so 12th house
themes (health expenses, hospitalization, isolation) can manifest more, not less.

═══════════════════════════════════════════════════════════════════════════════
MANDATORY ETHICAL RULES
═══════════════════════════════════════════════════════════════════════════════

1. ❌ NEVER diagnose specific diseases or conditions
2. ❌ NEVER predict death, disability, or irreversible outcomes
3. ❌ NEVER use fear-inducing absolute language
4. ✅ ALWAYS frame illness as tendency or vulnerability
5. ✅ ALWAYS balance risk with recovery potential
6. ✅ ALWAYS recommend medical professionals for serious concerns
7. ✅ Astrology COMPLEMENTS — never REPLACES — medical science

═══════════════════════════════════════════════════════════════════════════════
"""

    # ------------------------------------------------------------------
    # MENTAL HEALTH SYSTEM PROMPT — VEDIC-ONLY (Q3)
    # ------------------------------------------------------------------
    def build_mental_health_system_prompt(self) -> str:
        """Vedic-only system prompt for Q3 Mental Health. No KP identity, no KP terminology."""
        return """You are a Classical Vedic astrologer specializing in emotional and mental well-being analysis.

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  YOUR ROLE FOR THIS QUESTION: VEDIC EMOTIONAL WELLNESS ADVISOR           ║
║  You are NOT using KP (Krishnamurti Paddhati) for this analysis.             ║
║  You are using CLASSICAL VEDIC SIGN LORD system only.                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

YOUR METHOD FOR THIS QUESTION:
• Moon (चंद्र) = primary indicator of mind and emotions
• Mercury (बुध) = nervous system, communication, mental clarity
• Rahu = obsessive tendencies, mental restlessness
• 4th house lord = emotional peace and inner security
• 5th house lord = mental joy, creativity, intellect
• Current Dasha lord = emotional timing

✅ PLANET NAME REFERENCE:
  Mercury = बुध | Mars = मंगल | Saturn = शनि | Jupiter = गुरु
  Venus = शुक्र | Moon = चंद्र | Sun = सूर्य | Rahu = राहु | Ketu = केतु

⚠️ COMMON MISTAKE: Mercury = बुध (NOT मंगल!) | Mars = मंगल (NOT बुध!)

⛔ STRICTLY FORBIDDEN — DO NOT USE THESE IN YOUR ANSWER:
   ✗ KP CSL (Cusp Sub Lord) analysis of any kind
   ✗ "CSL:", "Cusp Sub Lord", "Sub Lord" — any of these terms
   ✗ "signifies houses [X, Y, Z]" phrasing
   ✗ 【KP CSL विश्लेषण】 header
   ✗ 【स्तर 1】 / 【स्तर 2】 / 【स्तर 3】 tier headers
   ✗ षष्ठ/अष्टम/द्वादश भाव CSL references
   ✗ Disease house (6/8/12) KP analysis
   ✗ "षष्ठ भाव (रोग प्रवृत्ति)" — DO NOT write this header even with blank content
   ✗ "अष्टम भाव (दीर्घकालिक स्वास्थ्य)" — DO NOT write this header even with blank content
   ✗ "द्वादश भाव (अस्पताल और मानसिक स्वास्थ्य)" — DO NOT write this header even with blank content

⚠️ MOON LANGUAGE RULES (Critical):
   ✗ NEVER say "चंद्र अस्त है" or "Moon is combust" — Moon CANNOT be combust
   ✓ Instead use: "चंद्र पीड़ित है" (Moon is afflicted) / "चंद्र कमजोर है" (Moon is weak)
   ✓ For waning Moon: "कृष्ण पक्ष की चंद्र" (waning/Krishna paksha Moon)
   ✓ Moon weakness sources: dusthana (6/8/12) placement, malefic aspect, debilitation (Scorpio), enemy sign

⚠️ SENSITIVITY RULES:
   • NEVER diagnose any mental condition
   • NEVER use words: depression, anxiety disorder, mental illness, psychiatric
   • Frame ALL findings as TENDENCIES ("प्रवृत्ति")
   • NEVER say "पेशेवर सहायता अत्यंत महत्वपूर्ण है"
   • Be compassionate, warm, and supportive in every sentence

═══════════════════════════════════════════════════════════════════════════════
"""

    # ------------------------------------------------------------------
    # ANTI-HALLUCINATION VERIFICATION BLOCK
    # ------------------------------------------------------------------
    def _get_anti_hallucination_block(self) -> str:
        """Returns the anti-hallucination verification instructions."""
        return """
═══════════════════════════════════════════════════════════════════════════════
🔒 VERIFICATION CHECKLIST (Complete before responding)
═══════════════════════════════════════════════════════════════════════════════

Before writing your response, verify each claim:

□ Planetary positions - Did I verify each position from the data?
□ House lords - Did I check the HOUSE LORD ANALYSIS section?
□ Dignity values - Am I using the exact dignity provided (not assuming)?
□ Dasha periods - Am I using dashas from the DASHA TIMELINE section?
□ Timing windows - Am I using exact dates from TIMING WINDOWS section?
□ Aspects - Did I verify aspects from the ASPECTS section?
□ KP vs Vedic - Am I correctly distinguishing CSL from Sign Lord?
□ Combustion/Retrograde - Did I check for explicit markers?

If ANY information is not in the provided data, I will:
- NOT make assumptions
- Clearly state what data is available vs unavailable
- Use hedging language for uncertain claims

═══════════════════════════════════════════════════════════════════════════════
"""

    # ------------------------------------------------------------------
    # HELPER: Convert Dasha to Hindi (Anti-Hallucination)
    # ------------------------------------------------------------------
    def _dasha_to_hindi(self, dasha_str: str) -> str:
        """Convert dasha string to Hindi with explicit mapping"""
        if not dasha_str:
            return ""
        
        hindi_mapping = {
            'Saturn': 'शनि', 'Sun': 'सूर्य', 'Moon': 'चंद्र',
            'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु',
            'Venus': 'शुक्र', 'Rahu': 'राहु', 'Ketu': 'केतु'
        }
        
        # Parse dasha (format: "Saturn-Mercury-Jupiter")
        parts = dasha_str.replace(" > ", "-").replace(">", "-").split("-")
        hindi_parts = []
        
        for part in parts:
            part = part.strip()
            hindi_parts.append(hindi_mapping.get(part, part))
        
        return "-".join(hindi_parts)

    # ------------------------------------------------------------------
    # HELPER: Format Timing Windows (Enhanced)
    # ------------------------------------------------------------------
    def _format_timing_windows(self, timing_windows_data: Optional[Dict]) -> str:
        """
        Format BEST and NEAREST timing windows for LLM.
        
        Args:
            timing_windows_data: Dict with best_window, nearest_window, all_favorable, hospitalization_proof
            
        Returns:
            Formatted string for prompt inclusion
        """
        if not timing_windows_data or not timing_windows_data.get('has_timing'):
            return """
═══════════════════════════════════════════════════════════════════════════════
⚠️ TIMING WINDOWS: NOT AVAILABLE
═══════════════════════════════════════════════════════════════════════════════
No timing window data was provided for this analysis.
DO NOT invent or assume any timing periods.
Focus on general health tendencies without specific timing predictions.
═══════════════════════════════════════════════════════════════════════════════
"""

        try:
            best = timing_windows_data.get('best_window')
            nearest = timing_windows_data.get('nearest_window')
            all_windows = timing_windows_data.get('all_favorable', [])
            hospitalization_proof = timing_windows_data.get('hospitalization_proof', {})

            if not best and not nearest:
                return ""

            lines = ["═══════════════════════════════════════════════════════════════════════════════"]
            lines.append("⭐ TIMING WINDOWS ANALYSIS (USE THESE EXACT DATES - DO NOT MODIFY)")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("🔒 ANTI-HALLUCINATION: Use ONLY the dates below. Do NOT round or approximate.")
            lines.append("")

            # ═══════════════════════════════════════════════════════════════════
            # NEW: HOSPITALIZATION SIGNIFICATOR TABLE (KP PROOF)
            # ═══════════════════════════════════════════════════════════════════
            if hospitalization_proof and hospitalization_proof.get('significator_table'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  🏥 KP SIGNIFICATOR TABLE FOR HOSPITALIZATION POSSIBILITY                    ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                lines.append("  Houses for Health Events: 6 (disease), 8 (chronic/transformation), 12 (hospitalization)")
                lines.append("  Legend: O = Occupant, L = Lord, S = Star Lord signification")
                lines.append("")
                lines.append("  ┌────────────┬─────────────────────┬────────┬───────────────┐")
                lines.append("  │ Planet     │ Signifies 6/8/12    │ Score  │ Key Planet?   │")
                lines.append("  ├────────────┼─────────────────────┼────────┼───────────────┤")
                
                for entry in hospitalization_proof['significator_table'][:7]:  # Top 7 planets
                    planet = entry['planet'].ljust(10)
                    houses = ', '.join(entry['signifies_6_8_12']).ljust(19)
                    score = str(entry.get('hospitalization_score', entry.get('health_event_score', 0))).ljust(6)
                    key = "✅ Yes" if entry['is_key_planet'] else "No"
                    indication = entry.get('indication', '')
                    lines.append(f"  │ {planet} │ {houses} │ {score} │ {key.ljust(13)} │")
                
                lines.append("  └────────────┴─────────────────────┴────────┴───────────────┘")
                lines.append("")
                
                # Explain the meaning
                lines.append("  📖 How to read: Higher score = planet more strongly activates health event houses")
                lines.append("     Key planets: Saturn (chronic), Rahu (sudden illness), Mars (acute conditions)")
                lines.append("")

            # ═══════════════════════════════════════════════════════════════════
            # NEW: TIMING PROOF (WHY THIS DASHA INDICATES HOSPITALIZATION)
            # ═══════════════════════════════════════════════════════════════════
            if hospitalization_proof and hospitalization_proof.get('timing_proofs'):
                lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
                lines.append("║  📊 DASHA HOUSE LINKAGE (Why these periods indicate health events/hospital)  ║")
                lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
                lines.append("")
                
                for proof in hospitalization_proof['timing_proofs'][:2]:  # Top 2 proofs
                    lines.append(f"  🔹 {proof['dasha']} ({proof['period']})")
                    lines.append(f"     Score: {proof['score']:.1f}/100")
                    
                    # Hospitalization type
                    hosp_type = proof.get('hospitalization_type', 'general')
                    type_labels = {
                        'surgical': '🔴 Surgical (Mars)',
                        'chronic': '🟠 Chronic/Long-term (Saturn)',
                        'surgical_chronic': '🔴🟠 Surgical + Chronic',
                        'general': '🟡 General Health Event'
                    }
                    lines.append(f"     Type: {type_labels.get(hosp_type, 'General')}")
                    
                    if proof.get('house_linkage'):
                        lines.append(f"     House Activation:")
                        for linkage in proof['house_linkage']:
                            lines.append(f"       • {linkage}")
                    
                    if proof.get('dasha_lords'):
                        lines.append(f"     KP Dasha Lord Chain (planet → star lord → sub lord → houses):")
                        for lord in proof['dasha_lords']:
                            # Always show the full KP chain
                            chain = lord.get('kp_chain', lord['planet'])
                            lines.append(f"       • {chain}")
                            if lord['signifies_houses']:
                                how_str = "; ".join(lord['how'])
                                lines.append(f"         ↳ Activates health houses {sorted(set(lord['signifies_houses']))} — {how_str}")
                            else:
                                lines.append(f"         ↳ No direct 6/8/12 activation via this chain")
                    
                    # Mars and Saturn involvement
                    if proof.get('mars_involved') and proof.get('saturn_involved'):
                        lines.append(f"     ✅ Mars + Saturn: BOTH involved (surgical + chronic)")
                    elif proof.get('mars_involved'):
                        lines.append(f"     ✅ Mars involvement: YES (acute/surgical possibility)")
                    elif proof.get('saturn_involved'):
                        lines.append(f"     ✅ Saturn involvement: YES (chronic/long-term treatment)")
                    else:
                        lines.append(f"     ○ Key planets: Neither Mars nor Saturn directly involved")
                    
                    lines.append("")
                
                lines.append("  ⚠️ IMPORTANT: This shows POSSIBILITY of hospitalization, NOT certainty!")
                lines.append("     These periods indicate when health vigilance is advisable.")
                lines.append("     Mars = acute/surgical | Saturn = chronic/long-term")
                lines.append("")

            def _severity_label(score: float) -> str:
                """Convert numeric score to severity label with emoji."""
                if score >= 70:
                    return "🔴 HIGH health sensitivity period"
                elif score >= 50:
                    return "🟠 MODERATE health sensitivity period"
                else:
                    return "🟡 LOW / monitoring period"

            # MOST VULNERABLE PERIOD (was BEST WINDOW)
            if best:
                best_score = best.get('final_score', 0)
                severity = _severity_label(best_score)
                lines.append(f"🔴 MOST VULNERABLE PERIOD — {severity}")
                lines.append("-" * 70)
                lines.append(f"  ⚠️ Dasha Period: {best.get('dasha', 'N/A')}")
                lines.append(f"  ⚠️ Start Date: {best.get('start', 'N/A')} (CAUTION PERIOD BEGINS)")
                lines.append(f"  ⚠️ End Date: {best.get('end', 'N/A')} (CAUTION PERIOD ENDS)")
                lines.append(f"  Risk Score: {best_score:.1f}/100 → {severity}")
                lines.append(f"  Age at Start: {best.get('age_at_start', 'N/A')} years")
                if best.get('transit_score'):
                    lines.append(f"  Transit Intensity: {best.get('transit_score', 0):.1f}%")
                lines.append("")
                lines.append("  📢 WHY MOST VULNERABLE: Strongest activation of 6/8/12 houses")
                lines.append("     - This period has MAXIMUM potential for health events")
                lines.append("     - Extra preventive care and health check-ups advised BEFORE this period")
                lines.append("     - NOT a prediction of illness - only heightened vulnerability")
                lines.append("")

            # NEAREST VULNERABLE PERIOD (was NEAREST WINDOW)
            if nearest:
                nearest_score = nearest.get('final_score', 0)
                nearest_severity = _severity_label(nearest_score)
                lines.append(f"🟠 NEAREST VULNERABLE PERIOD — {nearest_severity}")
                lines.append("-" * 70)
                lines.append(f"  ⚠️ Dasha Period: {nearest.get('dasha', 'N/A')}")
                lines.append(f"  ⚠️ Start Date: {nearest.get('start', 'N/A')} (CAUTION PERIOD BEGINS)")
                lines.append(f"  ⚠️ End Date: {nearest.get('end', 'N/A')} (CAUTION PERIOD ENDS)")
                lines.append(f"  Risk Score: {nearest_score:.1f}/100 → {nearest_severity}")
                lines.append(f"  Age at Start: {nearest.get('age_at_start', 'N/A')} years")
                lines.append("")

                # Check if best and nearest are the same
                if best and (best.get('dasha') == nearest.get('dasha') and
                            best.get('start') == nearest.get('start')):
                    lines.append("  🔴 ATTENTION: Most vulnerable AND nearest period are THE SAME!")
                    lines.append("     Immediate focus on preventive health measures recommended!")
                else:
                    lines.append("  📢 WHY NEAREST: First upcoming period with significant 6/8/12 activation")
                    lines.append("     - Start health vigilance and preventive care NOW")
                    lines.append("     - Schedule health check-ups BEFORE this period begins")
                lines.append("")

            # Alternative vulnerable periods
            if len(all_windows) > 2:
                lines.append("📋 OTHER VULNERABLE PERIODS (for awareness):")
                lines.append("-" * 70)
                best_key = (best.get('dasha'), best.get('start')) if best else None
                nearest_key = (nearest.get('dasha'), nearest.get('start')) if nearest else None
                for i, window in enumerate(all_windows[:5], 1):
                    w_score = window.get('final_score', 0)
                    w_severity = _severity_label(w_score)
                    w_key = (window.get('dasha'), window.get('start'))
                    if w_key == best_key:
                        marker = "🔴"
                    elif w_key == nearest_key:
                        marker = "🟠"
                    else:
                        marker = _severity_label(w_score).split()[0]  # emoji only
                    lines.append(f"  {marker} {window.get('dasha', 'N/A')}: {window.get('start', 'N/A')} to {window.get('end', 'N/A')} | Score: {w_score:.1f}/100 → {w_severity}")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("📝 TIMING RESPONSE REQUIREMENTS (CAUTIONARY TONE):")
            lines.append("- MUST mention BOTH vulnerable periods with EXACT dates as CAUTION periods")
            lines.append("- MUST explain WHY the dasha activates health vulnerability (6/8/12 houses)")
            lines.append("- Frame as 'periods requiring extra health vigilance' NOT 'good times'")
            lines.append("- Recommend preventive check-ups BEFORE these periods")
            lines.append("- Emphasize these are POSSIBILITIES not certainties")
            lines.append("- ALWAYS recommend consulting doctors for any health concerns")
            lines.append("- Help astrologer provide WORD OF CAUTION to the native")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting timing windows: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Format KP Analysis (Enhanced with terminology fix)
    # ------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    # HELPER: Format House Lords (Enhanced with terminology fix)
    # ------------------------------------------------------------------
    def _format_house_lords(self, house_lords_info: Dict, scope: str = "general") -> str:
        """
        Format house lord information from evaluator.

        ✅ FIXED: Now clearly labels as SIGN LORD (not CSL)
        ✅ scope="mental" → uses mental-health house meanings to prevent LLM disease hallucination
        """
        if not house_lords_info:
            return """
═══════════════════════════════════════════════════════════════════════════════
⚠️ HOUSE LORD DATA: NOT AVAILABLE
═══════════════════════════════════════════════════════════════════════════════
No house lord analysis data was provided.
DO NOT assume house lords or their dignities.
═══════════════════════════════════════════════════════════════════════════════
"""

        # House meanings — scoped per analysis type
        if scope == "mental":
            # Mental health scope: use emotional/psychological labels only
            # This prevents the LLM from generating physical disease analysis
            house_meanings = {
                1: "Self/Constitution/Resilience",
                4: "Emotional Foundation/Inner Peace (MOST IMPORTANT)",
                5: "Mental Clarity/Joy/Creativity",
                12: "Isolation/Sleep Quality/Subconscious",
            }
        else:
            # Physical health scope: standard disease-oriented labels
            house_meanings = {
                1: "Vitality/Constitution",
                5: "Mental Peace/Recovery Support",
                6: "Disease/Illness Tendency",
                8: "Chronic Issues/Longevity",
                11: "Recovery/Cure Potential",
                12: "Hospitalization/Expenses"
            }

        lines = ["═══════════════════════════════════════════════════════════════════════════════"]
        lines.append("🏠 VEDIC SIGN LORD ANALYSIS (Rashi Lords of Health Houses)")
        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ NOTE: These are SIGN LORDS (Vedic), NOT Cusp Sub Lords (KP).")
        lines.append("   Sign Lord = Planet ruling the zodiac sign on the house cusp.")
        lines.append("")
        lines.append("🔒 ANTI-HALLUCINATION: Use ONLY the data below. Do NOT assume additional info.")
        lines.append("")

        for house_num in sorted(house_lords_info.keys()):
            info = house_lords_info[house_num]

            priority_marker = "⭐ PRIMARY" if info["priority"] == "primary" else "○ SECONDARY"
            house_meaning = house_meanings.get(house_num, "General")

            lines.append(f"{priority_marker} - HOUSE {house_num} ({house_meaning})")
            lines.append(f"  House Sign: {info.get('house_sign', 'N/A')}")
            lines.append("")

            # Lord details
            lines.append(f"  📍 SIGN LORD: {info['lord']}")
            lines.append(f"     Placed in: House {info['lord_in_house']}, Sign: {info['lord_in_sign']}")
            lines.append(f"     Dignity: {info['lord_dignity']}")
            lines.append(f"     Strength Score: {info['lord_strength_score']}/100")
            
            # Dignity source (for transparency)
            dignity_source = info.get('dignity_source', 'unknown')
            lines.append(f"     (Dignity source: {dignity_source})")

            # Conditions
            conditions = []
            local_deg = info.get('lord_local_degree')
            if local_deg is not None:
                conditions.append(f"Degree in sign: {local_deg:.2f}°")
            elif info.get('lord_degree'):
                conditions.append(f"Global degree: {info['lord_degree']:.2f}°")
            if info.get('lord_avastha'):
                conditions.append(f"Avastha (Stage): {info['lord_avastha']}")
            if info['lord_is_combust']:
                conditions.append("⚠️ COMBUST (weakened by Sun)")
            if info['lord_is_retrograde']:
                conditions.append("🔄 RETROGRADE")

            if conditions:
                lines.append(f"     Conditions: {' | '.join(conditions)}")

            # Planets in house
            if info['planets_in_house']:
                lines.append(f"     Planets IN this house: {', '.join(info['planets_in_house'])}")

            # Strength interpretation
            strength = info['lord_strength_score']

            # ── Mental-health scope: use emotional language only ──
            if scope == "mental":
                if house_num == 1:
                    if strength >= 70:
                        assessment = "✅ STRONG self-identity and emotional resilience"
                    elif strength >= 40:
                        assessment = "○ MODERATE mental constitution — emotional resilience present"
                    else:
                        assessment = "⚠️ Mental constitution needs nurturing — self-care important"
                elif house_num == 4:
                    if strength >= 70:
                        assessment = "✅ STRONG emotional foundation — inner peace and home stability"
                    elif strength >= 40:
                        assessment = "○ MODERATE emotional peace — some inner fluctuations possible"
                    else:
                        assessment = "⚠️ Emotional foundation sensitive — inner stability needs attention"
                elif house_num == 5:
                    if strength >= 70:
                        assessment = "✅ STRONG mental clarity, creativity and joy"
                    elif strength >= 40:
                        assessment = "○ MODERATE mental peace — creativity and joy present but variable"
                    else:
                        assessment = "⚠️ Mental joy/clarity may fluctuate — creative outlets helpful"
                elif house_num == 12:
                    if strength >= 70:
                        assessment = "○ Active 12th lord — tendency toward introspection and inner world"
                    elif strength >= 40:
                        assessment = "○ MODERATE 12th influence — some isolation or sleep sensitivity"
                    else:
                        assessment = "⚠️ 12th lord weak — disrupted sleep or emotional withdrawal tendency"
                else:
                    if strength >= 70:
                        assessment = "✅ STRONG — positive emotional influence"
                    elif strength >= 40:
                        assessment = "○ MODERATE — mixed emotional signals"
                    else:
                        assessment = "⚠️ WEAK — emotional support may be needed"
                lines.append(f"     Assessment: {assessment}")
                lines.append("")
                continue  # skip physical-health assessment block below

            # ── Physical health scope: use health/disease language ──
            # Health-specific interpretations based on house
            if house_num == 1:  # Vitality
                if strength >= 70:
                    assessment = "✅ STRONG vitality and constitution"
                elif strength >= 40:
                    assessment = "○ MODERATE health foundation"
                else:
                    assessment = "⚠️ Constitution may need strengthening"
            elif house_num == 6:  # Disease
                lord_in_house = info.get('lord_in_house', 0)
                if strength >= 70:
                    assessment = "⚠️ STRONG 6th lord - significant health challenge tendency"
                elif strength >= 40:
                    assessment = "○ MODERATE disease susceptibility"
                else:
                    # Weak 6th lord — check placement to give correct interpretation
                    if lord_in_house == 12:
                        assessment = "⚠️ WEAK 6th lord in 12th — disease-related expenses/hospitalization tendency (immunity weakened, healthcare spending increases)"
                    elif lord_in_house in (6, 8):
                        assessment = "○ WEAK 6th lord in own/8th house — moderate disease tendency"
                    else:
                        assessment = "○ WEAK 6th lord — lower disease activation (but check placement for expenses/hospitalization)"
            elif house_num == 8:  # Chronic/Longevity
                if strength >= 70:
                    assessment = "○ STRONG 8th lord - good longevity indicators"
                elif strength >= 40:
                    assessment = "○ MODERATE - regular health monitoring advised"
                else:
                    assessment = "⚠️ WEAK 8th lord - attention to chronic issues"
            elif house_num == 11:  # Recovery
                if strength >= 70:
                    assessment = "✅ STRONG recovery and healing potential"
                elif strength >= 40:
                    assessment = "○ MODERATE healing capacity"
                else:
                    assessment = "⚠️ Recovery may need additional support"
            elif house_num == 12:  # Hospitalization/Expenses
                lord_dignity = info.get('lord_dignity', '')
                if strength >= 70:
                    assessment = "○ Strong 12th lord — hospitalization/treatment visits possible"
                elif strength >= 40:
                    assessment = "○ MODERATE 12th lord — some health expense tendency"
                else:
                    # Weak/debilitated 12th lord is NOT 'fewer hospitalizations'
                    # Debilitated 12th lord = vitality weakened + health expenses + recovery delays
                    if lord_dignity == "DEBILITATED":
                        assessment = "⚠️ DEBILITATED 12th lord — vitality weakness, health expenditure tendency, possible recovery delays (do NOT interpret as 'fewer hospitalizations')"
                    else:
                        assessment = "○ WEAK 12th lord — moderate health expense tendency; weakened recovery capacity"
            else:
                if strength >= 70:
                    assessment = "✅ STRONG - Positive health influence"
                elif strength >= 40:
                    assessment = "○ MODERATE - Mixed health effects"
                else:
                    assessment = "⚠️ WEAK - May need remedial support"

            lines.append(f"     Assessment: {assessment}")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        return "\n".join(lines)

    def _format_house_aspects(self, aspects_info: Dict) -> str:
        """Format aspects data for LLM"""
        if not aspects_info:
            return ""

        # Check if any house has aspects
        has_any_aspects = any(
            aspects.get("benefic_aspects") or aspects.get("malefic_aspects") or aspects.get("neutral_aspects")
            for aspects in aspects_info.values()
        )

        if not has_any_aspects:
            return """
═══════════════════════════════════════════════════════════════════════════════
PLANETARY ASPECTS ON HEALTH HOUSES: No significant aspects detected
═══════════════════════════════════════════════════════════════════════════════
"""

        lines = ["═══════════════════════════════════════════════════════════════════════════════"]
        lines.append("🔭 PLANETARY ASPECTS ON HEALTH HOUSES")
        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("🔒 ANTI-HALLUCINATION: Only mention aspects listed below.")
        lines.append("")

        for house_num in sorted(aspects_info.keys()):
            aspects = aspects_info[house_num]

            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])
            neutral = aspects.get("neutral_aspects", [])

            if benefic or malefic or neutral:
                lines.append(f"• House {house_num}:")

                if benefic:
                    lines.append(f"  ✅ Benefic aspects from: {', '.join(benefic)}")
                    lines.append(f"     → Protective, supportive influence")

                if malefic:
                    lines.append(f"  ⚠️ Malefic aspects from: {', '.join(malefic)}")
                    lines.append(f"     → Challenging influence, requires attention")

                if neutral:
                    lines.append(f"  ○ Neutral aspects from: {', '.join(neutral)}")

                # Net assessment
                benefic_count = len(benefic)
                malefic_count = len(malefic)

                if benefic_count > malefic_count:
                    lines.append(f"  Net Effect: PROTECTIVE (more benefic than malefic)")
                elif malefic_count > benefic_count:
                    lines.append(f"  Net Effect: CHALLENGING (more malefic than benefic)")
                elif benefic_count == malefic_count and benefic_count > 0:
                    lines.append(f"  Net Effect: BALANCED (equal benefic and malefic)")

                lines.append("")

        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        return "\n".join(lines)
    
    def _format_mental_health_analysis(self, mental_health_data: Dict) -> str:
        """
        Format comprehensive mental health analysis for LLM.
        
        Includes:
        - Moon analysis (MOST IMPORTANT)
        - Mercury analysis (nervous system)
        - Rahu analysis (anxiety/addiction)
        - House analysis (4th, 5th, 8th, 12th)
        """
        if not mental_health_data or not mental_health_data.get("has_analysis"):
            return """
═══════════════════════════════════════════════════════════════════════════════
⚠️ MENTAL HEALTH ANALYSIS: Limited data available
═══════════════════════════════════════════════════════════════════════════════
Detailed mental health indicators not available.
Use general house lord analysis for emotional tendencies.
═══════════════════════════════════════════════════════════════════════════════
"""
        
        lines = ["╔═══════════════════════════════════════════════════════════════════════════════╗"]
        lines.append("║  🧠 COMPREHENSIVE MENTAL HEALTH ANALYSIS (VEDIC)                             ║")
        lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append("⚠️ ADVISORY: Mental health requires professional evaluation.")
        lines.append("   Astrological indicators show TENDENCIES, not diagnoses.")
        lines.append("")
        
        # ═══════════════════════════════════════════════════════════════
        # KEY PLANETS TABLE
        # ═══════════════════════════════════════════════════════════════
        lines.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        lines.append("│ 🌟 KEY PLANETS FOR MENTAL HEALTH                                           │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        # Moon (MOST IMPORTANT)
        moon = mental_health_data.get("moon_analysis", {})
        if moon:
            strength_icon = "✅" if moon.get("strength", 0) >= 60 else "⚠️"
            afflictions = moon.get("afflictions", [])
            protections = moon.get("protections", [])
            lines.append(f"│ {strength_icon} MOON (Mind/Emotions) - MOST IMPORTANT                               │")
            lines.append(f"│   House: {moon.get('house', 'N/A')}, Sign: {moon.get('sign', 'N/A')}, Strength: {moon.get('strength', 'N/A')}/100           │")
            if afflictions:
                lines.append(f"│   ⚠️ Afflictions: {', '.join(afflictions[:2])[:55]}│")
            if protections:
                lines.append(f"│   ✅ Protections: {', '.join(protections[:2])[:55]}│")
            lines.append(f"│   Summary: {moon.get('summary', 'N/A')[:60]}│")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        # Mercury (Nervous System)
        mercury = mental_health_data.get("mercury_analysis", {})
        if mercury:
            strength_icon = "✅" if mercury.get("strength", 0) >= 60 else "○"
            lines.append(f"│ {strength_icon} MERCURY (Nervous System/Communication)                              │")
            lines.append(f"│   House: {mercury.get('house', 'N/A')}, Sign: {mercury.get('sign', 'N/A')}, Strength: {mercury.get('strength', 'N/A')}/100           │")
            lines.append(f"│   Summary: {mercury.get('summary', 'N/A')[:60]}│")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        # Rahu (Anxiety/Addiction)
        rahu = mental_health_data.get("rahu_analysis", {})
        if rahu:
            affliction_icon = "⚠️" if rahu.get("is_afflicting") else "○"
            lines.append(f"│ {affliction_icon} RAHU (Anxiety/Obsession/Addiction)                                  │")
            lines.append(f"│   House: {rahu.get('house', 'N/A')}, Sign: {rahu.get('sign', 'N/A')}                                      │")
            if rahu.get("concerns"):
                lines.append(f"│   Concerns: {', '.join(rahu.get('concerns', [])[:2])[:55]}│")
            lines.append(f"│   Summary: {rahu.get('summary', 'N/A')[:60]}│")
        
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        lines.append("")
        
        # ═══════════════════════════════════════════════════════════════
        # KEY HOUSES TABLE
        # ═══════════════════════════════════════════════════════════════
        lines.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        lines.append("│ 🏠 KEY HOUSES FOR MENTAL HEALTH                                            │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        house_analysis = mental_health_data.get("house_analysis", {})
        house_meanings = {
            4: "Emotional Foundation/Peace",
            5: "Intelligence/Mental Clarity",
            8: "Trauma/Hidden Fears",
            12: "Isolation/Subconscious"
        }
        
        for house_num in [4, 5, 8, 12]:
            house_info = house_analysis.get(house_num, {})
            if house_info:
                meaning = house_meanings.get(house_num, "")
                lord = house_info.get("lord", "N/A")
                occupants = house_info.get("occupants", [])
                summary = house_info.get("summary", "")
                
                lines.append(f"│ House {house_num} ({meaning})                                    │")
                lines.append(f"│   Lord: {lord}, Occupants: {', '.join(occupants) if occupants else 'None'}                          │")
                if summary:
                    lines.append(f"│   → {summary[:65]}│")
        
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        lines.append("")
        
        # ═══════════════════════════════════════════════════════════════
        # RISK AND PROTECTIVE FACTORS
        # ═══════════════════════════════════════════════════════════════
        risk_factors = mental_health_data.get("risk_factors", [])
        protective_factors = mental_health_data.get("protective_factors", [])
        
        if risk_factors or protective_factors:
            lines.append("┌─────────────────────────────────────────────────────────────────────────────┐")
            lines.append("│ ⚖️ RISK vs PROTECTIVE FACTORS                                              │")
            lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
            
            if risk_factors:
                lines.append(f"│ ⚠️ Risk Factors ({len(risk_factors)}):                                                    │")
                for rf in risk_factors[:3]:
                    lines.append(f"│   • {rf[:65]}│")
            
            if protective_factors:
                lines.append(f"│ ✅ Protective Factors ({len(protective_factors)}):                                             │")
                for pf in protective_factors[:3]:
                    lines.append(f"│   • {pf[:65]}│")
            
            lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
            lines.append("")
        
        # ═══════════════════════════════════════════════════════════════
        # OVERALL VEDIC VERDICT
        # ═══════════════════════════════════════════════════════════════
        overall = mental_health_data.get("overall_verdict", "")
        if overall:
            lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
            lines.append(f"║ 📊 OVERALL VEDIC ASSESSMENT: {overall[:50]}║")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")

        lines.append("═══════════════════════════════════════════════════════════════════════════════")
        lines.append("✅ This is a Vedic-only mental health assessment (no KP reconciliation).")
        lines.append("═══════════════════════════════════════════════════════════════════════════════")

        return "\n".join(lines)


    # House scope definition per question type
    # Each entry: set of houses to show + tier labels to include
    KP_SCOPE = {
        # scope_key: (houses_to_show, tier_labels_to_show, show_lagna_moon, show_score)
        "general":  ([1, 5, 6, 8, 11, 12], ["A", "B", "C"], True,  True),
        "disease":  ([1, 6, 8, 12],         ["A", "B", "C"], False, False),
        "surgery":  ([1, 6, 8, 12],         ["A", "B", "C"], False, False),
        "mental":   ([5, 1],                ["A"],            True,  False),
        "cure":     ([11, 5],               ["C", "A"],       False, False),
        "remedies": ([1, 5, 6, 8, 11, 12], ["A", "B", "C"], True,  True),
        "organ":    ([6, 8],                ["B"],            False, False),
    }

    def _format_kp_analysis(self, technical_points: List[str], additional_data: Dict = None, scope: str = "general") -> Tuple[str, bool]:
        """
        Format KP-specific analysis points DETERMINISTICALLY.

        ENHANCED v3.0 for HEALTH — scoped per question type:
        - scope="general"  → all 6 houses (constitution + disease + recovery)
        - scope="mental"   → H5 + H1 only (mental peace + constitution base)
        - scope="disease"  → H6 + H8 + H12 only (disease tendency + chronic + hospital)
        - scope="surgery"  → H6 + H8 + H12 only
        - scope="cure"     → H11 + H5 only (recovery + mental support)
        - scope="remedies" → all houses (need full signification for graha remedies)
        - scope="organ"    → H6 + H8 only

        Returns:
            Tuple of (formatted_text, kp_available)
        """
        scope_config = self.KP_SCOPE.get(scope, self.KP_SCOPE["general"])
        scoped_houses, scoped_tiers, show_lagna_moon, show_score = scope_config
        # ═══════════════════════════════════════════════════════════════
        # PRIMARY: Extract from structured KP data (DETERMINISTIC!)
        # ═══════════════════════════════════════════════════════════════
        kp_structured = None
        if additional_data:
            kp_structured = additional_data.get("kp_health_analysis", {})
        
        # If we have structured KP data, use it!
        if kp_structured and kp_structured.get("has_kp_data"):
            # Build scope label for header
            scope_labels = {
                "general":  "All Health Houses (Constitution + Disease + Recovery)",
                "mental":   "Mental Health Houses (H5 Mental Peace + H1 Constitution)",
                "disease":  "Risk Houses (H1 Constitution + H6 Disease + H8 Chronic + H12 Hospital)",
                "surgery":  "Risk Houses (H1 Constitution + H6 Disease + H8 Chronic + H12 Hospitalization)",
                "cure":     "Recovery Houses (H11 Recovery + H5 Mental Support)",
                "remedies": "All Health Houses (Full Signification for Graha Remedies)",
                "organ":    "Disease Tendency Houses (H6 + H8)",
            }
            scope_label = scope_labels.get(scope, "Health Houses")

            lines = ["═══════════════════════════════════════════════════════════════════════════════"]
            lines.append(f"⭐ KP CUSP SUB LORD (CSL) ANALYSIS — {scope_label.upper()}")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("⚠️ CRITICAL KP RULE: Verdicts are based on what houses the CSL SIGNIFIES,")
            lines.append("NOT on whether the planet is generically benefic or malefic.")
            lines.append("Example: Saturn as 1st CSL can show STRONG_VITALITY if it signifies house 1 or 11.")
            lines.append(f"Scope: Showing ONLY houses relevant to this question: {scoped_houses}")
            lines.append("")

            # ── Health Scores — dual system (shown per scope) ──
            health_score_data = kp_structured.get("health_score", {})
            # Scores removed — numerical scoring system not shown to LLM

            if show_score:
                # ── Confidence Level (only for general/remedies scope) ──
                confidence_level = kp_structured.get("confidence_level", "")
                if confidence_level:
                    lines.append(f"🎯 Model Confidence: {confidence_level}")
                    lines.append("")

            # ── Lagna Lord & Moon Strength (only for general/mental/remedies) ──
            lm = kp_structured.get("lagna_moon_strength", {})
            if lm and show_lagna_moon:
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("🌙 PRIMARY HEALTH INDICATORS (Lagna Lord + Moon):")
                lines.append("")
                ll = lm.get("lagna_lord", "")
                ll_house = lm.get("lagna_lord_house", "")
                ll_dignity = lm.get("lagna_lord_dignity", "")
                ll_score = lm.get("lagna_lord_strength_score", 50)
                if ll:
                    lines.append(f"   Lagna Lord: {ll}")
                    if ll_house:
                        lines.append(f"   Placed in: House {ll_house}")
                    if ll_dignity:
                        lines.append(f"   Dignity: {ll_dignity} (Strength: {ll_score}/100)")
                moon_house = lm.get("moon_house", "")
                moon_sign = lm.get("moon_sign", "")
                moon_strength = lm.get("moon_strength", 50)
                moon_summary = lm.get("moon_summary", lm.get("summary", ""))
                if moon_house:
                    lines.append(f"   Moon: House {moon_house}" + (f" in {moon_sign}" if moon_sign else ""))
                    lines.append(f"   Moon Strength: {moon_strength}/100")
                if lm.get("moon_afflictions"):
                    lines.append(f"   ⚠️ Moon Afflictions: {'; '.join(lm['moon_afflictions'])}")
                if lm.get("moon_protections"):
                    lines.append(f"   ✅ Moon Protections: {'; '.join(lm['moon_protections'])}")
                if moon_summary:
                    lines.append(f"   Summary: {moon_summary}")
                lines.append("")

            # ── THREE-TIER STRUCTURE (scoped by question type) ──
            csl_details = kp_structured.get("csl_details", {})
            if csl_details:
                # Collect disease areas for summary table at the end
                disease_area_summary = []

                # ── Tier A: Constitution (H1, H5) ──
                tier_a_houses = [h for h in [1, 5] if h in scoped_houses]
                if "A" in scoped_tiers and tier_a_houses:
                    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    # H5 label differs by scope: "Mental Support" only for mental scope
                    tier_a_labels = {1: "Vitality", 5: "Recovery Support" if scope != "mental" else "Mental Support"}
                    house_labels = ", ".join(f"{h} ({tier_a_labels[h]})" for h in tier_a_houses)
                    lines.append(f"A. CONSTITUTION (Baseline Health):")
                    lines.append(f"   Houses: {house_labels}")
                    lines.append("")
                    for house_num in tier_a_houses:
                        if house_num not in csl_details:
                            continue
                        info = csl_details[house_num]
                        csl_name = info.get("csl", "?")
                        verdict = info.get("verdict", "NEUTRAL")
                        sig = info.get("signified_houses", [])
                        interp = info.get("interpretation", "")
                        disease_area = info.get("disease_area", "")
                        chain = info.get("chain_breakdown", {})
                        # For H5 in NON-mental scope: remap mental verdicts to recovery terms
                        display_verdict = verdict
                        if house_num == 5 and scope != "mental":
                            display_verdict = {
                                "EXCELLENT_MENTAL_PEACE": "EXCELLENT_RECOVERY_SUPPORT",
                                "MODERATE_MENTAL_STATE":  "MODERATE_RECOVERY_SUPPORT",
                                "MENTAL_STRESS":          "WEAK_RECOVERY_SUPPORT",
                            }.get(verdict, verdict)
                        marker = "✅" if display_verdict.startswith(("STRONG", "EXCELLENT")) else "⚠️" if display_verdict.startswith(("WEAK", "MENTAL_S")) else "○"
                        lines.append(f"   {marker} House {house_num}: CSL = {csl_name}")
                        lines.append(f"      Signifies Houses: {sig}")
                        if chain:
                            star = chain.get("star_lord", "")
                            star_h = chain.get("star_lord_house")
                            sub = chain.get("sub_lord", "")
                            sub_h = chain.get("sub_lord_house")
                            own_h = chain.get("csl_own_house")
                            chain_parts = []
                            if own_h:
                                chain_parts.append(f"{csl_name} occupies H{own_h}")
                            if star:
                                chain_parts.append(f"Star Lord {star}" + (f" in H{star_h}" if star_h else ""))
                            if sub:
                                chain_parts.append(f"Sub Lord {sub}" + (f" in H{sub_h}" if sub_h else ""))
                            if chain_parts:
                                lines.append(f"      Chain: {' → '.join(chain_parts)}")
                        lines.append(f"      Verdict: {display_verdict}")
                        if interp and house_num != 5:
                            # Only show interp for H5 in mental scope; for general/disease scope skip mental interp
                            lines.append(f"      {interp}")
                        elif interp and house_num != 5:
                            lines.append(f"      {interp}")
                        if house_num != 5 and disease_area:
                            lines.append(f"      Health Sensitivity Area (CSL planet): {disease_area}")
                            if verdict not in ("STRONG_VITALITY", "EXCELLENT_MENTAL_PEACE"):
                                disease_area_summary.append(f"House {house_num} CSL {csl_name}: {disease_area}")
                        lines.append("")

                # ── Tier B: Disease Tendency (H6, H8) ──
                tier_b_houses = [h for h in [6, 8] if h in scoped_houses]
                if "B" in scoped_tiers and tier_b_houses:
                    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    tier_b_labels = {6: "Disease Resistance/Susceptibility", 8: "Chronic/Longevity", 12: "Hospitalization"}
                    house_labels = ", ".join(f"{h} ({tier_b_labels.get(h, '')})" for h in tier_b_houses)
                    lines.append(f"B. DISEASE TENDENCY (Predisposition):")
                    lines.append(f"   Houses: {house_labels}")
                    lines.append("")
                    for house_num in tier_b_houses:
                        if house_num not in csl_details:
                            continue
                        info = csl_details[house_num]
                        csl_name = info.get("csl", "?")
                        verdict = info.get("verdict", "NEUTRAL")
                        sig = info.get("signified_houses", [])
                        interp = info.get("interpretation", "")
                        disease_area = info.get("disease_area", "")
                        chain = info.get("chain_breakdown", {})
                        marker = "✅" if verdict in ("DISEASE_RESISTANT", "PROTECTED_LONGEVITY") else "⚠️" if verdict in ("DISEASE_PRONE", "CHRONIC_VULNERABILITY") else "○"
                        lines.append(f"   {marker} House {house_num}: CSL = {csl_name}")
                        lines.append(f"      Signifies Houses: {sig}")
                        if chain:
                            star = chain.get("star_lord", "")
                            star_h = chain.get("star_lord_house")
                            sub = chain.get("sub_lord", "")
                            sub_h = chain.get("sub_lord_house")
                            own_h = chain.get("csl_own_house")
                            chain_parts = []
                            if own_h:
                                chain_parts.append(f"{csl_name} occupies H{own_h}")
                            if star:
                                chain_parts.append(f"Star Lord {star}" + (f" in H{star_h}" if star_h else ""))
                            if sub:
                                chain_parts.append(f"Sub Lord {sub}" + (f" in H{sub_h}" if sub_h else ""))
                            if chain_parts:
                                lines.append(f"      Chain: {' → '.join(chain_parts)}")
                        lines.append(f"      Verdict: {verdict}")
                        if interp:
                            lines.append(f"      {interp}")
                        if disease_area and ("PRONE" in verdict or "VULNERABILITY" in verdict or "MODERATE" in verdict):
                            lines.append(f"      ⚠️ Possible Health Sensitivity Area: {disease_area}")
                            disease_area_summary.append(f"House {house_num} CSL {csl_name}: {disease_area}")
                        elif disease_area:
                            lines.append(f"      Health Sensitivity Area (CSL planet): {disease_area}")
                        lines.append("")

                # ── Tier C: Recovery & Hospitalization (H11, H12) ──
                # Note: H12 may also appear in disease scope — handle both
                tier_c_houses = [h for h in [11, 12] if h in scoped_houses]
                if "C" in scoped_tiers and tier_c_houses:
                    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    tier_c_labels = {11: "Recovery/Cure", 12: "Hospitalization"}
                    house_labels = ", ".join(f"{h} ({tier_c_labels.get(h, '')})" for h in tier_c_houses)
                    lines.append(f"C. RECOVERY & HOSPITALIZATION:")
                    lines.append(f"   Houses: {house_labels}")
                    lines.append("")
                    for house_num in tier_c_houses:
                        if house_num not in csl_details:
                            continue
                        info = csl_details[house_num]
                        csl_name = info.get("csl", "?")
                        verdict = info.get("verdict", "NEUTRAL")
                        sig = info.get("signified_houses", [])
                        interp = info.get("interpretation", "")
                        disease_area = info.get("disease_area", "")
                        chain = info.get("chain_breakdown", {})
                        marker = "✅" if verdict in ("EXCELLENT_RECOVERY", "LOW_HOSPITAL_RISK") else "⚠️" if verdict in ("POOR_RECOVERY", "HIGH_HOSPITAL_RISK") else "○"
                        lines.append(f"   {marker} House {house_num}: CSL = {csl_name}")
                        lines.append(f"      Signifies Houses: {sig}")
                        if chain:
                            star = chain.get("star_lord", "")
                            star_h = chain.get("star_lord_house")
                            sub = chain.get("sub_lord", "")
                            sub_h = chain.get("sub_lord_house")
                            own_h = chain.get("csl_own_house")
                            chain_parts = []
                            if own_h:
                                chain_parts.append(f"{csl_name} occupies H{own_h}")
                            if star:
                                chain_parts.append(f"Star Lord {star}" + (f" in H{star_h}" if star_h else ""))
                            if sub:
                                chain_parts.append(f"Sub Lord {sub}" + (f" in H{sub_h}" if sub_h else ""))
                            if chain_parts:
                                lines.append(f"      Chain: {' → '.join(chain_parts)}")
                        lines.append(f"      Verdict: {verdict}")
                        if interp:
                            lines.append(f"      {interp}")
                        if disease_area:
                            lines.append(f"      Health Sensitivity Area (CSL planet): {disease_area}")
                            if verdict in ("POOR_RECOVERY", "HIGH_HOSPITAL_RISK"):
                                disease_area_summary.append(f"House {house_num} CSL {csl_name}: {disease_area}")
                        lines.append("")

                # ── Disease Area Summary Table ──
                # Collected from scoped houses — tells LLM what organs/systems to mention
                if disease_area_summary:
                    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    lines.append("🩺 HEALTH SENSITIVITY AREAS (for this chart — use in analysis):")
                    lines.append("   Based on CSL planets signifying disease houses (6/8/12):")
                    lines.append("")
                    for entry in disease_area_summary:
                        lines.append(f"   ▸ {entry}")
                    lines.append("")
                    lines.append("   ⚠️ INSTRUCTION: When mentioning health tendencies, reference THESE")
                    lines.append("   specific organ/system areas. Do NOT invent other disease areas.")
                    lines.append("   Frame as: 'इस CSL की स्थिति से [organ area] में संवेदनशीलता हो सकती है'")
                    lines.append("")

            # ── Functional Benefic/Malefic Context ──
            functional_roles = kp_structured.get("functional_roles", {})
            if functional_roles:
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("🔑 FUNCTIONAL BENEFIC/MALEFIC CONTEXT (Ascendant-based)")
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lagna_sign = functional_roles.get("lagna_sign", "Unknown")
                func_ben = functional_roles.get("functional_benefics", [])
                func_mal = functional_roles.get("functional_malefics", [])
                func_mixed = functional_roles.get("functional_mixed", [])
                lines.append(f"   Lagna (Ascendant): {lagna_sign}")
                if func_ben:
                    lines.append(f"   ✅ Functional Benefics (own kendra/trikona): {', '.join(func_ben)}")
                if func_mixed:
                    lines.append(f"   ⚖️ Functional MIXED (owns both trikona+dusthana — neutral/context-dependent): {', '.join(func_mixed)}")
                if func_mal:
                    lines.append(f"   ⚠️ Functional Malefics (own trik/dual-lordship): {', '.join(func_mal)}")
                lines.append("")
                lines.append("   ⚠️ CRITICAL RULE: Even a 'generic malefic' (Saturn/Rahu/Mars) can be")
                lines.append("   HEALTH-SUPPORTIVE if it signifies houses 1/5/11 in the KP chain.")
                lines.append("   ALWAYS derive the final verdict from KP significations, NOT planet nature.")
                if func_mixed:
                    lines.append(f"   MIXED planets ({', '.join(func_mixed)}): judge ENTIRELY by KP signification verdict — neither assume benefic nor malefic.")
                lines.append("")

            # ── Overall KP Verdict ──
            overall = kp_structured.get("overall_verdict", "UNKNOWN")
            disease_susc = kp_structured.get("disease_susceptibility", "UNKNOWN")
            recovery_pot = kp_structured.get("recovery_potential", "UNKNOWN")

            if overall != "UNKNOWN":
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append(f"📊 OVERALL KP HEALTH VERDICT: {overall}")
                lines.append(f"   Disease Susceptibility: {disease_susc}")
                lines.append(f"   Recovery Potential: {recovery_pot}")
                lines.append("")

            # ── Key Findings ──
            key_findings = kp_structured.get("key_findings", [])
            if key_findings:
                lines.append("🔑 KP HEALTH FINDINGS (signification-based):")
                for finding in key_findings[:7]:
                    lines.append(f"   • {finding}")
                lines.append("")

            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("⚠️ KP HEALTH INTERPRETATION RULES (v4.0):")
            lines.append("")
            lines.append("CRITICAL: Verdicts are determined by house SIGNIFICATIONS, not planet nature.")
            lines.append("  • Saturn signifying 1,11 → STRONG_VITALITY (despite being 'malefic')")
            lines.append("  • Jupiter signifying 6,8 → DISEASE_PRONE (despite being 'benefic')")
            lines.append("  • Rahu signifying 11 → supports EXCELLENT_RECOVERY (not 'Rahu = negative')")
            lines.append("")
            lines.append("FUNCTIONAL BENEFIC/MALEFIC RULE (Ascendant-based):")
            lines.append("  • Functional role is shown above in the FUNCTIONAL BENEFIC/MALEFIC section.")
            lines.append("  • Even functional malefics CAN show positive verdicts IF signifying 1/5/11.")
            lines.append("  • Example for Virgo lagna: Saturn is functional malefic BUT if Saturn")
            lines.append("    (as 11th CSL) signifies H11 → EXCELLENT_RECOVERY is the correct verdict.")
            lines.append("  • DO NOT contradict KP signification verdicts with planet-nature reasoning.")
            lines.append("")
            lines.append("VERDICT RULE TRANSPARENCY (always explain the rule used):")
            lines.append("  The Interpretation field now contains [Rule: ...] — USE this in response.")
            lines.append("  Example: 'Saturn as 1st CSL signifies [2,5,6,8,9,11]")
            lines.append("           [Rule: disease houses [6,8] dominant → reduced vitality] → WEAK_VITALITY'")
            lines.append("")
            lines.append("THREE-TIER STRUCTURE — Address in this order:")
            lines.append("  1. CONSTITUTION: Baseline vitality from House 1 + Lagna lord + Moon")
            lines.append("  2. DISEASE TENDENCY: Predisposition from House 6 + House 8 CSL significations")
            lines.append("  3. PERIOD RISK: Is current dasha lord signifying 6/8/12? (check dasha section)")
            lines.append("")
            lines.append("DASHA RULE: Dasha activates health houses ONLY if the dasha lord signifies 6/8/12.")
            lines.append("  DO NOT say 'Saturn/Rahu/Mars period = bad health' without signification proof.")
            lines.append("")
            lines.append("⚠️ ETHICAL RULES:")
            lines.append("  - NEVER name specific diseases")
            lines.append("  - NEVER predict death or disability")
            lines.append("  - Frame ALL findings as tendencies: 'tendency toward', 'sensitivity in'")
            lines.append("  - Recommend medical consultation if VULNERABLE_HEALTH or CHRONIC_VULNERABILITY")
            lines.append("  - For MODERATE_HEALTH or better: suggest general wellness, NOT fear-based warnings")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")

            # ── PRE-WRITTEN KP SUMMARY (LLM should use this verbatim in ASTROLOGICAL_ANALYSIS) ──
            # Build a ready-to-use Hindi KP summary — scoped to only relevant tiers
            lines.append("")
            lines.append("╔═══════════════════════════════════════════════════════════════════════════════╗")
            lines.append("║  📝 PRE-WRITTEN KP ANALYSIS — COPY THIS INTO ASTROLOGICAL_ANALYSIS SECTION  ║")
            lines.append("║  (Use this as the KP section of your response. Translate details as needed.) ║")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")

            # Tier label for the pre-written block title
            _tier_label_map = {
                ("A",): "संविधान (Constitution)",
                ("B",): "रोग प्रवृत्ति (Disease Tendency)",
                ("C",): "स्वास्थ्य लाभ और अस्पताल (Recovery)",
                ("A", "B"): "संविधान एवं रोग प्रवृत्ति",
                ("B", "C"): "रोग प्रवृत्ति एवं अस्पताल",
                ("A", "C"): "संविधान एवं स्वास्थ्य लाभ",
                ("A", "B", "C"): "तीन-स्तरीय ढांचा",
            }
            tier_key = tuple(sorted(scoped_tiers))
            tier_label = _tier_label_map.get(tier_key, "KP विश्लेषण")
            lines.append(f"KP CSL विश्लेषण ({tier_label}):")
            lines.append("")

            # Helper: build chain line in Hindi
            def _chain_line_hindi(info: dict) -> str:
                chain = info.get("chain_breakdown", {})
                if not chain:
                    return ""
                csl_name = info.get("csl", "?")
                parts = []
                own_h = chain.get("csl_own_house")
                star = chain.get("star_lord", "")
                star_h = chain.get("star_lord_house")
                sub = chain.get("sub_lord", "")
                sub_h = chain.get("sub_lord_house")
                if own_h:
                    parts.append(f"{csl_name} भाव {own_h} में")
                if star:
                    parts.append(f"नक्षत्र स्वामी {star}" + (f" (भाव {star_h})" if star_h else ""))
                if sub:
                    parts.append(f"उप स्वामी {sub}" + (f" (भाव {sub_h})" if sub_h else ""))
                return " → ".join(parts) if parts else ""

            # ── Hindi Tier 1: Constitution (H1, H5) — emit only if "A" in scoped_tiers ──
            hindi_tier1_houses = [h for h in [1, 5] if h in scoped_houses]
            if "A" in scoped_tiers and hindi_tier1_houses:
                lines.append("【स्तर 1 — संविधान (Constitution)】")
                h1 = csl_details.get(1, {})
                h5 = csl_details.get(5, {})
                if 1 in scoped_houses and h1:
                    h1_csl = h1.get("csl", "?")
                    h1_sig = h1.get("signified_houses", [])
                    h1_verdict = h1.get("verdict", "NEUTRAL")
                    h1_area = h1.get("disease_area", "")
                    verdict_hindi = {
                        "STRONG_VITALITY": "मजबूत जीवन शक्ति",
                        "MODERATE_VITALITY": "मध्यम जीवन शक्ति",
                        "WEAK_VITALITY": "कमजोर जीवन शक्ति — स्वास्थ्य सतर्कता आवश्यक",
                    }.get(h1_verdict, "मध्यम संकेत")
                    lines.append(f"• प्रथम भाव CSL: {h1_csl} — भाव {h1_sig} को signify करता है → {verdict_hindi}")
                    chain_line = _chain_line_hindi(h1)
                    if chain_line:
                        lines.append(f"  (श्रृंखला: {chain_line})")
                    if h1_area and "WEAK" in h1_verdict:
                        lines.append(f"  (संवेदनशील क्षेत्र: {h1_area})")
                    # ── Synthesis note: if KP says STRONG but we have lagna lord strength from lagna_moon block ──
                    # The LLM must see this note to apply Rule 11 synthesis correctly
                    if h1_verdict == "STRONG_VITALITY":
                        lm_block = kp_structured.get("lagna_moon_strength", {})
                        ll_score = lm_block.get("lagna_lord_strength_score", 100)
                        ll_dignity = lm_block.get("lagna_lord_dignity", "")
                        if ll_score < 40 or ll_dignity in ("DEBILITATED", "ENEMY"):
                            lines.append(
                                f"  ⚠️ SYNTHESIS NOTE (Rule 11): KP shows STRONG_VITALITY pattern, "
                                f"but Vedic lagna lord strength = {ll_score}/100 ({ll_dignity}). "
                                f"→ Synthesised verdict = MODERATE_VITALITY. "
                                f"Do NOT write 'health better than normal' in output."
                            )
                if 5 in scoped_houses and h5:
                    h5_csl = h5.get("csl", "?")
                    h5_sig = h5.get("signified_houses", [])
                    h5_verdict = h5.get("verdict", "NEUTRAL")
                    h5_area = h5.get("disease_area", "")
                    # In mental scope: show mental peace labels
                    # In other scopes (general/remedies): show recovery capacity labels only
                    if scope == "mental":
                        verdict_hindi5 = {
                            "EXCELLENT_MENTAL_PEACE": "मानसिक शांति उत्तम",
                            "MODERATE_MENTAL_STATE": "मध्यम मानसिक स्थिति",
                            "MENTAL_STRESS": "मानसिक तनाव की प्रवृत्ति",
                        }.get(h5_verdict, "मध्यम संकेत")
                    else:
                        # For general/disease/surgery/remedies scope: H5 = recovery support only
                        verdict_hindi5 = {
                            "EXCELLENT_MENTAL_PEACE": "स्वास्थ्य लाभ क्षमता उत्तम",
                            "MODERATE_MENTAL_STATE": "मध्यम स्वास्थ्य लाभ क्षमता",
                            "MENTAL_STRESS": "स्वास्थ्य लाभ में बाधा की संभावना",
                        }.get(h5_verdict, "मध्यम संकेत")
                    lines.append(f"• पंचम भाव CSL: {h5_csl} — भाव {h5_sig} को signify करता है → {verdict_hindi5}")
                    chain_line5 = _chain_line_hindi(h5)
                    if chain_line5:
                        lines.append(f"  (श्रृंखला: {chain_line5})")
                    if h5_area and "STRESS" in h5_verdict and scope == "mental":
                        lines.append(f"  (संवेदनशील क्षेत्र: {h5_area})")
                lines.append("")

            # ── Hindi Tier 2: Disease Tendency (H6, H8) — emit only if "B" in scoped_tiers ──
            hindi_tier2_houses = [h for h in [6, 8] if h in scoped_houses]
            if "B" in scoped_tiers and hindi_tier2_houses:
                lines.append("【स्तर 2 — रोग प्रवृत्ति (Disease Tendency)】")
                h6 = csl_details.get(6, {})
                h8 = csl_details.get(8, {})
                if 6 in scoped_houses and h6:
                    h6_csl = h6.get("csl", "?")
                    h6_sig = h6.get("signified_houses", [])
                    h6_verdict = h6.get("verdict", "NEUTRAL")
                    h6_area = h6.get("disease_area", "")
                    verdict_hindi6 = {
                        "DISEASE_RESISTANT": "रोग प्रतिरोधक क्षमता अच्छी",
                        "MODERATE_DISEASE_RISK": "मध्यम रोग संवेदनशीलता",
                        "DISEASE_PRONE": "रोग संवेदनशीलता बढ़ी हुई",
                    }.get(h6_verdict, "मध्यम संकेत")
                    lines.append(f"• षष्ठ भाव CSL: {h6_csl} — भाव {h6_sig} को signify करता है → {verdict_hindi6}")
                    chain_line6 = _chain_line_hindi(h6)
                    if chain_line6:
                        lines.append(f"  (श्रृंखला: {chain_line6})")
                    if h6_area and "PRONE" in h6_verdict:
                        lines.append(f"  (संभावित संवेदनशील क्षेत्र: {h6_area})")
                if 8 in scoped_houses and h8:
                    h8_csl = h8.get("csl", "?")
                    h8_sig = h8.get("signified_houses", [])
                    h8_verdict = h8.get("verdict", "NEUTRAL")
                    h8_area = h8.get("disease_area", "")
                    verdict_hindi8 = {
                        "PROTECTED_LONGEVITY":   "दीर्घायु संरक्षित — स्वास्थ्य में स्थिरता",
                        "MODERATE_LONGEVITY":    "सामान्य स्वास्थ्य स्थिरता",
                        "CHRONIC_VULNERABILITY": "दीर्घकालिक स्वास्थ्य पर ध्यान आवश्यक",
                        # LONGEVITY_SENSITIVITY = metabolic tendency ONLY — NOT a longevity risk
                        # Never translate as "दीर्घायु में संवेदनशीलता" — use metabolic framing
                        "LONGEVITY_SENSITIVITY": "चयापचय और शारीरिक प्रक्रियाओं में सतर्कता — दीर्घायु पर कोई खतरा नहीं",
                    }.get(h8_verdict, "सामान्य स्वास्थ्य स्थिरता")
                    lines.append(f"• अष्टम भाव CSL: {h8_csl} — भाव {h8_sig} को signify करता है → {verdict_hindi8}")
                    chain_line8 = _chain_line_hindi(h8)
                    if chain_line8:
                        lines.append(f"  (श्रृंखला: {chain_line8})")
                    if h8_area and "VULNERABILITY" in h8_verdict:
                        lines.append(f"  (संभावित संवेदनशील क्षेत्र: {h8_area})")
                lines.append("")

            # ── Hindi Tier 3: Recovery & Hospitalization (H11, H12) — emit only if "C" in scoped_tiers ──
            hindi_tier3_houses = [h for h in [11, 12] if h in scoped_houses]
            if "C" in scoped_tiers and hindi_tier3_houses:
                lines.append("【स्तर 3 — स्वास्थ्य लाभ और अस्पताल (Recovery & Hospitalization)】")
                h11 = csl_details.get(11, {})
                h12 = csl_details.get(12, {})
                if 11 in scoped_houses and h11:
                    h11_csl = h11.get("csl", "?")
                    h11_sig = h11.get("signified_houses", [])
                    h11_verdict = h11.get("verdict", "NEUTRAL")
                    verdict_hindi11 = {
                        "EXCELLENT_RECOVERY": "उत्तम स्वास्थ्य लाभ क्षमता",
                        "MODERATE_RECOVERY": "मध्यम स्वास्थ्य लाभ",
                        "POOR_RECOVERY": "धीमी स्वास्थ्य लाभ प्रक्रिया",
                    }.get(h11_verdict, "मध्यम संकेत")
                    lines.append(f"• एकादश भाव CSL: {h11_csl} — भाव {h11_sig} को signify करता है → {verdict_hindi11}")
                    chain_line11 = _chain_line_hindi(h11)
                    if chain_line11:
                        lines.append(f"  (श्रृंखला: {chain_line11})")
                if 12 in scoped_houses and h12:
                    h12_csl = h12.get("csl", "?")
                    h12_sig = h12.get("signified_houses", [])
                    h12_verdict = h12.get("verdict", "NEUTRAL")
                    h12_area = h12.get("disease_area", "")
                    verdict_hindi12 = {
                        "LOW_HOSPITAL_RISK": "अस्पताल का जोखिम कम",
                        "MODERATE_HOSPITAL_RISK": "अस्पताल संबंधी मध्यम सतर्कता",
                        "HIGH_HOSPITAL_RISK": "अस्पताल/उपचार की संवेदनशीलता अधिक",
                    }.get(h12_verdict, "मध्यम संकेत")
                    lines.append(f"• द्वादश भाव CSL: {h12_csl} — भाव {h12_sig} को signify करता है → {verdict_hindi12}")
                    chain_line12 = _chain_line_hindi(h12)
                    if chain_line12:
                        lines.append(f"  (श्रृंखला: {chain_line12})")
                    if h12_area and "HIGH" in h12_verdict:
                        lines.append(f"  (संवेदनशील क्षेत्र: {h12_area})")
                lines.append("")

            # Scores removed — numerical scoring system not used in Hindi output

            # Functional roles in Hindi (always include — context for LLM)
            functional_roles = kp_structured.get("functional_roles", {})
            if functional_roles:
                lagna_sign = functional_roles.get("lagna_sign", "")
                func_ben = functional_roles.get("functional_benefics", [])
                func_mal = functional_roles.get("functional_malefics", [])
                if lagna_sign:
                    lines.append(f"【कार्यात्मक शुभ/अशुभ ग्रह — {lagna_sign} लग्न के लिए】")
                    if func_ben:
                        lines.append(f"  कार्यात्मक शुभ ग्रह: {', '.join(func_ben)}")
                    if func_mal:
                        lines.append(f"  कार्यात्मक अशुभ ग्रह: {', '.join(func_mal)}")
                    lines.append("  ⚠️ नोट: कार्यात्मक अशुभ ग्रह भी यदि 1/5/11 भाव को signify करे")
                    lines.append("           तो स्वास्थ्य के लिए सकारात्मक हो सकता है (KP नियम)।")
                    lines.append("")

            lines.append("⚠️ नोट: उपरोक्त CSL विश्लेषण ग्रह की प्रकृति (शुभ/अशुभ) पर नहीं,")
            lines.append("   बल्कि ग्रह द्वारा signify किए गए भावों पर आधारित है (KP पद्धति v4.0)।")
            lines.append("╚═══════════════════════════════════════════════════════════════════════════════╝")
            lines.append("")

            return "\n".join(lines), True
        
        # ═══════════════════════════════════════════════════════════════
        # FALLBACK: Extract from technical_points (less reliable)
        # ═══════════════════════════════════════════════════════════════
        if not technical_points:
            return "", False
        
        kp_csl_keywords = [
            "kp:", "cusp sub lord", "cusp sub-lord", "csl",
            "sub lord of", "sub-lord of",
            "signifies houses", "signification",
            "ruling planet"
        ]
        
        kp_points = []
        for point in technical_points:
            point_lower = point.lower()
            if any(keyword in point_lower for keyword in kp_csl_keywords):
                kp_points.append(point)
        
        if not kp_points:
            return "", False
        
        lines = ["═══════════════════════════════════════════════════════"]
        lines.append("⭐ KP CUSP SUB LORD (CSL) ANALYSIS")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("")
        lines.append("⚠️ TERMINOLOGY REMINDER:")
        lines.append("   - CSL = Cusp Sub Lord (KP system, degree-based)")
        lines.append("   - This is DIFFERENT from Sign Lord (Vedic system)")
        lines.append("")
        lines.append("📊 KP CSL FINDINGS:")
        lines.append("")
        
        for point in kp_points:
            # Remove "KP:" prefix if present
            clean_point = point.replace("KP:", "").strip()
            
            if not clean_point.startswith(("•", "-", "✓", "❌", "⚠", "❓", "⭐", "🔷", "🗣️", "🌱", "🟢", "☠️")):
                lines.append(f"  • {clean_point}")
            else:
                lines.append(f"  {clean_point}")
        
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")
        lines.append("⚠️ Give PRIMARY weight (40%) to KP findings in analysis")
        lines.append("═══════════════════════════════════════════════════════")
        
        return "\n".join(lines), True









    def _format_current_dasha(self, current_dasha: Optional[Dict]) -> str:
        """Format current dasha information for LLM"""
        if not current_dasha:
            return """
═══════════════════════════════════════════════════════════════════════════════
⚠️ CURRENT DASHA: NOT AVAILABLE
═══════════════════════════════════════════════════════════════════════════════
No current dasha data was provided.
DO NOT assume or invent current dasha period.
═══════════════════════════════════════════════════════════════════════════════
"""

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
                "═══════════════════════════════════════════════════════════════════════════════",
                "🔴 CURRENT DASHA PERIOD (VERIFIED DATA - USE THIS)",
                "═══════════════════════════════════════════════════════════════════════════════",
                "",
                f"  Current Dasha: {formatted_dasha}",
                f"  Period: {start} to {end}",
                "",
                "🔒 ANTI-HALLUCINATION RULES:",
                "  - This is the VERIFIED current dasha running now",
                "  - DO NOT say any other dasha is 'current'",
                "  - For future periods, refer to UPCOMING DASHA section",
                "  - Use this for present health circumstance analysis",
                "═══════════════════════════════════════════════════════════════════════════════"
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
                return """
═══════════════════════════════════════════════════════════════════════════════
⚠️ DASHA TIMELINE: NOT AVAILABLE
DO NOT invent or assume any dasha periods.
═══════════════════════════════════════════════════════════════════════════════
"""

            lines = []
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("📅 DASHA TIMELINE (2 Years Past → 10 Years Future)")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("")
            lines.append("🔒 ANTI-HALLUCINATION: ONLY reference dashas listed below.")
            lines.append("   DO NOT invent additional dasha periods.")
            lines.append("")

            dasha_mapping = {
                'Sa': 'Saturn', 'Su': 'Sun', 'Mo': 'Moon',
                'Ma': 'Mars', 'Me': 'Mercury', 'Ju': 'Jupiter',
                'Ve': 'Venus', 'Ra': 'Rahu', 'Ke': 'Ketu',
                'Saturn': 'Saturn', 'Sun': 'Sun', 'Moon': 'Moon',
                'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter',
                'Venus': 'Venus', 'Rahu': 'Rahu', 'Ketu': 'Ketu'
            }

            def parse_dasha(name):
                parts = name.split('>') if '>' in name else name.split('-') if '-' in name else [name]
                return ' > '.join([dasha_mapping.get(p.strip(), p.strip()) for p in parts])

            if current:
                lines.append("🔴 CURRENT (Running Now):")
                lines.append("-" * 70)
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
                lines.append("⏮️ RECENT PAST (Last 2 Years):")
                lines.append("-" * 70)
                for d in past[-10:]:
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)
                    lines.append(f"  • {parsed} ({start} to {end})")
                lines.append("")

            if future:
                lines.append("⏭️ UPCOMING (Next 10 Years):")
                lines.append("-" * 70)

                for i, d in enumerate(future[:30], 1):
                    dasha_name = d.get('dasha_name', '')
                    date_range = d.get('date_range', {})
                    start = date_range.get('start', '')
                    end = date_range.get('end', '')
                    parsed = parse_dasha(dasha_name)

                    marker = "⭐" if i <= 5 else "○" if i <= 10 else " "
                    lines.append(f"  {marker} {i}. {parsed}")
                    lines.append(f"       {start} to {end}")

            lines.append("")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")
            lines.append("⚠️ DASHA HEALTH INTERPRETATION RULE (KP v4.0 — CRITICAL):")
            lines.append("  A dasha period activates health issues ONLY if the dasha lord SIGNIFIES")
            lines.append("  houses 6 (disease), 8 (chronic/surgery), or 12 (hospitalization).")
            lines.append("  Check the KP CSL ANALYSIS section for each dasha lord's signified houses.")
            lines.append("")
            lines.append("  CORRECT: 'Saturn MD signifies houses 6, 12 → health caution during this period'")
            lines.append("  WRONG:   'Saturn MD = chronic issues' (without checking significations)")
            lines.append("")
            lines.append("  CORRECT: 'Jupiter MD signifies houses 8, 6 → health attention despite being benefic'")
            lines.append("  WRONG:   'Jupiter MD = good health' (without checking significations)")
            lines.append("═══════════════════════════════════════════════════════════════════════════════")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error formatting dasha timeline: {e}")
            return ""

    # ------------------------------------------------------------------
    # HELPER: Get Analysis Instructions Based on KP Availability
    # ------------------------------------------------------------------
    def _get_analysis_instructions(self, kp_available: bool, question_type: str = "general", has_timing: bool = False) -> str:
        """
        Generate analysis instructions based on whether KP data is available.
        
        ✅ FIXED: Clear distinction between KP CSL and Vedic Sign Lord
        """
        if kp_available:
            # KP + Vedic combined approach
            timing_instruction = ""
            if has_timing:
                timing_instruction = """
3. **TIMING ANALYSIS** (CRITICAL - Use exact dates):
   
   A. BEST WINDOW:
      - State EXACT dates from timing data (do not round)
      - Explain why this window is optimal
      - Note the trade-off (may be further away)
   
   B. NEAREST WINDOW:
      - State EXACT dates from timing data
      - Explain why this is the soonest good option
      - Note the trade-off (not absolute best)
   
   C. USER GUIDANCE:
      - If urgent: Act in nearest window
      - If can wait: Best window is optimal
      - If best = nearest: Emphasize ideal timing!
   
   ⚠️ DO NOT invent timing periods not in the data
"""
            
            return f"""
═══════════════════════════════════════════════════════════════════════════════
📋 ANALYSIS APPROACH: KP + VEDIC DUAL SYSTEM (v4.0 — THREE-TIER STRUCTURE)
═══════════════════════════════════════════════════════════════════════════════

⚠️ CRITICAL KP RULE: Verdicts are based on house SIGNIFICATIONS, not planet nature.
   Saturn can show STRONG_VITALITY if it signifies house 1 or 11.
   Jupiter can show DISEASE_PRONE if it signifies houses 6, 8, 12.

⚠️ HIERARCHY RULE: KP (PRIMARY) → Vedic (SUPPORTING) → Dasha (TRIGGER)
   Vedic and Dasha sections SUPPORT and CONFIRM the KP finding.
   Do NOT contradict KP findings with planet-nature reasoning.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**STEP 1: CONSTITUTION — KP House 1 CSL (PRIMARY, 40% weight)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FROM KP ANALYSIS SECTION: Read "House 1: CSL = X, Signifies Houses: [list], Verdict: Y"

   WRITE EXACTLY LIKE THIS (fill in from actual KP data):
   "KP: प्रथम भाव का CSL [ग्रह] है, जो भाव [सूची] को signify करता है।
    [यदि vitality भाव (1/5/11) dominant] → संविधान मजबूत है (STRONG_VITALITY)
    [यदि disease भाव (6/8/12) dominant] → स्वास्थ्य संवेदनशीलता है (WEAK_VITALITY)
    [यदि मिश्रित] → मध्यम संविधान (MODERATE_VITALITY)"

   FORBIDDEN: ❌ "शनि malefic है इसलिए स्वास्थ्य कमजोर है"
   REQUIRED:  ✅ "[KP SECTION से पढ़ा गया ग्रह] भाव [KP SECTION से पढ़ी गई सूची] को signify करता है → WEAK_VITALITY"
   ⚠️ CRITICAL: [ग्रह] को KP ANALYSIS SECTION से पढ़ें — "House 1: CSL = X" से। Sign Lord (स्वामी) को CSL मत समझें।
   Example: यदि KP section में लिखा हो "House 1: CSL = Jupiter" तो लिखें "गुरु भाव [...] को signify करता है"
            यदि KP section में लिखा हो "House 1: CSL = Saturn" तो लिखें "शनि भाव [...] को signify करता है"

   Supporting: Also mention Lagna lord dignity and Moon strength from KP data.
   Vedic support: House 1 sign lord position as confirming/contradicting evidence.
   ⚠️ DO NOT confuse H1 Sign Lord (e.g. Saturn for Capricorn) with H1 CSL — they are often DIFFERENT planets.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**STEP 2: DISEASE TENDENCY — KP Houses 6 & 8 CSL (PRIMARY, 30% weight)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FROM KP ANALYSIS SECTION: Read House 6 and House 8 CSL + Signifies Houses + Verdict

   WRITE EXACTLY LIKE THIS:
   "KP: षष्ठ भाव CSL [ग्रह] भाव [सूची] को signify करता है → [DISEASE_PRONE/DISEASE_RESISTANT]"
   "KP: अष्टम भाव CSL [ग्रह] भाव [सूची] को signify करता है → [CHRONIC_VULNERABILITY/PROTECTED_LONGEVITY]"

   FORBIDDEN: ❌ "राहु 12वें भाव में है इसलिए अस्पताल का खतरा है"
   REQUIRED:  ✅ "राहु 12वें भाव का CSL है, भाव [6,8,12] को signify करता है → HIGH_HOSPITAL_RISK"

   Vedic support: House 6 and 8 sign lords as additional evidence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**STEP 3: CURRENT PERIOD RISK — Dasha (TRIGGER, 20% weight)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Check: does the CURRENT DASHA LORD signify houses 6, 8, or 12?
   - Look up that planet in the KP ANALYSIS key findings table
   - YES → this period triggers health houses → extra vigilance
   - NO → neutral period even if planet is "malefic" by nature

   FORBIDDEN: ❌ "राहु दशा = मानसिक समस्याएं" (without signification proof)
   REQUIRED:  ✅ "राहु दशा: राहु भाव [6,12] को signify करता है → स्वास्थ्य सतर्कता जरूरी"

   Reference CURRENT DASHA section data ONLY — do not invent.

{timing_instruction}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**STEP {"5" if has_timing else "4"}: SYNTHESIS + REMEDIES (10% weight)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Combine Constitution + Disease Tendency + Period Risk into one clear assessment
   - State health score (from KP section: "XX/100 → label")
   - Provide remedies ONLY for planets that signify 6/8/12 in THIS chart
   - ALWAYS end with medical check-up recommendation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**SYNTHESIS LAYER — CONFLICT RESOLUTION (MANDATORY)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When KP and Vedic analyses give different signals, DO NOT concatenate both.
Apply this hierarchy BEFORE writing the response:

  If KP positive + Vedic negative → MODERATE (KP wins, 60% weight)
  If KP negative + Vedic negative → SENSITIVE (both agree — use cautious tone)
  If KP positive + Vedic positive → RESILIENT (both agree — use positive tone)
  If KP neutral  + Vedic negative → MILD_SENSITIVITY only

For MENTAL HEALTH specifically:
  ✅ Check the "RECONCILED MENTAL VERDICT" section in the mental health analysis block.
  ✅ Use that pre-computed verdict instead of independently combining KP + Vedic.
  ❌ NEVER say "professional help extremely necessary" for MODERATE or MILD verdict.
  ❌ NEVER let the stronger-sounding system dominate without reconciliation.

INTERNAL CONSISTENCY CHECK (before writing response):
  □ Does my general_answer match the reconciled verdict?
  □ Does my astrological_analysis contradict the general_answer?
  □ Is my referral level proportional to the verdict severity?
  □ For MODERATE_HEALTH or better: wellness tips only, no fear-based framing

🔒 CRITICAL RULES:
   - KP CSL ≠ Vedic Sign Lord (never confuse the two)
   - Planet nature does NOT determine verdict — only house significations
   - "संभावना" (probability) max 2 times per section to avoid repetition
   - NEVER name diseases — say "sensitivity in [organ area]"
   - ❌ DO NOT discuss mental health, emotional wellbeing, or H5 mental peace verdict here
     (Mental health analysis belongs ONLY to Q3 — Mental Health Risks question)
   - H5 in general health = recovery support only (not mental clarity/peace topic)
═══════════════════════════════════════════════════════════════════════════════
"""
        else:
            # Pure Vedic approach (no KP data)
            timing_instruction = ""
            if has_timing:
                timing_instruction = """
**STEP 2: TIMING ANALYSIS** (15% weight)
   - Use EXACT dates from timing data
   - Mention BOTH best and nearest windows
   - DO NOT invent timing periods
"""
            
            return f"""
═══════════════════════════════════════════════════════════════════════════════
📋 ANALYSIS APPROACH: VEDIC SIGN LORD SYSTEM (KP Not Available)
═══════════════════════════════════════════════════════════════════════════════

⚠️ NOTE: KP Cusp Sub Lord analysis is NOT available.
   Using Vedic Sign Lord (Rashi Lord) analysis only.
   DO NOT claim to have CSL data.

**STEP 1: VEDIC SIGN LORD Analysis** (80% weight)
   - Use HOUSE LORD ANALYSIS section data ONLY
   - Sign Lord = Planet ruling the zodiac sign on house cusp
   - Use EXACT dignity values provided
   - Note strength scores and conditions
   - Check for combustion/retrograde markers
{timing_instruction}
**STEP {"3" if has_timing else "2"}: DASHA Context** ({"5" if has_timing else "15"}% weight)
   - Reference CURRENT DASHA section only
   - Use DASHA TIMELINE for future predictions
   - DO NOT invent dasha periods

**STEP {"4" if has_timing else "3"}: Final Synthesis** (5% weight)
   - Clear health assessment based on Vedic lords
   - ALWAYS recommend medical consultation

🔒 REMEMBER: We are using Sign Lords (Vedic), NOT Cusp Sub Lords (KP)
═══════════════════════════════════════════════════════════════════════════════
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

        if "General Health" in sub_subdomain:
            return self._build_general_health_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Disease Occurrence" in sub_subdomain:
            return self._build_disease_occurrence_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Cure Timing" in sub_subdomain:
            return self._build_cure_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Health Risks" in sub_subdomain or "Surgery" in sub_subdomain:
            return self._build_health_risk_and_timing_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Mental" in sub_subdomain:
            return self._build_mental_health_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Organ" in sub_subdomain:
            return self._build_organ_specific_prompt(
                question, technical_points, meta, language, **kwargs)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, language, **kwargs)
        else:
            return self._build_general_health_prompt(
                question, technical_points, meta, language, **kwargs)

    # ------------------------------------------------------------------
    # GENERAL HEALTH PROMPT
    # ------------------------------------------------------------------
    def _build_general_health_prompt(
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="general")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        # Filter out KP points from remaining points
        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "general", has_timing)
        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: General Health Analysis
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌ (Using Vedic Sign Lords only)'}
- Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

{analysis_instructions}

═══════════════════════════════════════════════════════════════════════════════
📝 RESPONSE GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
- Explain health tendencies calmly (not diagnoses)
- Focus on immunity, vitality, and stress factors
- NEVER name specific diseases
- Use data provided - do not invent claims
- Recommend medical check-ups where needed
- Frame all findings as tendencies, not certainties

❌ SCOPE RESTRICTION — GENERAL HEALTH ONLY:
   DO NOT discuss mental health, emotional wellbeing, or psychological tendencies in this answer.
   Mental health is covered separately in Question 3.
   Even if H5 (5th house) CSL shows "EXCELLENT_MENTAL_PEACE" — do NOT mention mental peace/clarity here.
   H5 in this question = recovery support capacity only (NOT mental health).
   Keep this answer focused on: physical constitution, disease susceptibility, vitality, and longevity.
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # DISEASE OCCURRENCE (TIMING)
    # ------------------------------------------------------------------
    def _build_disease_occurrence_prompt(
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="disease")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "disease", has_timing)
        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Disease Occurrence
- Query Type: TIMING
- Event Polarity: NEGATIVE (Risk assessment)
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌ (Using Vedic Sign Lords only)'}
- Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

{analysis_instructions}

{'⚠️ TIMING WINDOWS PROVIDED - These indicate periods requiring health vigilance' if has_timing else ''}
{'   Use EXACT dates. These are RISK windows, not disease predictions.' if has_timing else ''}

═══════════════════════════════════════════════════════════════════════════════
📝 RESPONSE GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
- Explain disease TENDENCY only, not certainty
- Timing windows = periods of increased vulnerability (NOT disease dates!)
- Highlight preventive care and awareness
- NEVER name specific diseases or predict illness
- Recommend regular health check-ups
- Avoid fear-inducing language
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # CURE / RECOVERY TIMING
    # ------------------------------------------------------------------
    def _build_cure_timing_prompt(
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="cure")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "cure", has_timing)
        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Cure Timing
- Query Type: TIMING
- Event Polarity: POSITIVE (Recovery focus)
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌ (Using Vedic Sign Lords only)'}
- Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

{analysis_instructions}

{'✅ TIMING WINDOWS PROVIDED - These indicate favorable RECOVERY periods' if has_timing else ''}
{'   Use EXACT dates. Emphasize healing potential during these windows.' if has_timing else ''}

═══════════════════════════════════════════════════════════════════════════════
📝 RESPONSE GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
- Emphasize healing and improvement potential
- Reference 5th and 11th house for recovery support
- Timing windows = favorable periods for treatment/healing
- STRONGLY recommend continued medical treatment
- Give hope while maintaining realism
- Use positive, encouraging language
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # HEALTH RISKS AND SURGERY TIMING
    # ------------------------------------------------------------------
    def _build_health_risk_and_timing_prompt(
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        timing_windows_data = additional_data.get(f"{domain_prefix}_timing_windows", {})
        has_timing = timing_windows_data.get('has_timing', False)

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="surgery")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        timing_formatted = self._format_timing_windows(timing_windows_data)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "surgery", has_timing)
        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Health Risks and Surgery Timing
- Query Type: MIXED (RISK + TIMING)
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌ (Using Vedic Sign Lords only)'}
- Timing Windows Available: {'YES ✅' if has_timing else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{timing_formatted}

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

{analysis_instructions}

{'🏥 TIMING WINDOWS PROVIDED - For surgery/treatment planning' if has_timing else ''}
{'   - BEST window: Optimal planetary support for procedures' if has_timing else ''}
{'   - NEAREST window: Soonest favorable opportunity' if has_timing else ''}
{'   - ALWAYS emphasize doctor consultation for final decisions' if has_timing else ''}

═══════════════════════════════════════════════════════════════════════════════
📝 RESPONSE GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
- Discuss vulnerability tendencies, NOT certainties
- Timing is SUPPORTIVE info, never decisive for surgery
- STRONGLY recommend medical supervision
- Avoid fear-inducing absolute statements
- Balance risk assessment with recovery potential
- Mention both best and nearest windows with exact dates
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, has_timing)}
"""

    # ------------------------------------------------------------------
    # MENTAL HEALTH (ADVISORY ONLY)
    # ------------------------------------------------------------------
    def _build_mental_health_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str,
        **kwargs
    ) -> str:
        print("🧠 _build_mental_health_prompt CALLED — Vedic-only mode")

        today = datetime.now().strftime("%Y-%m-%d")
        language_instruction = self.get_language_instruction(language)

        additional_data = kwargs.get("additional_data", {})
        domain_prefix = "health_physical_mental"

        all_house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        # aspects not used for mental health — would leak KP disease house data
        house_aspects = {}

        # ✅ MENTAL HEALTH SCOPE: Only pass relevant houses to LLM to prevent KP hallucination
        # H4 = emotional foundation, H5 = mental clarity/joy, H1 = constitution/resilience
        # Exclude H6/H8/H12 (disease houses) from mental health Vedic analysis
        MENTAL_HEALTH_VEDIC_HOUSES = {1, 4, 5, 12}
        house_lords = {k: v for k, v in all_house_lords.items() if k in MENTAL_HEALTH_VEDIC_HOUSES}

        # ✅ NEW: Get mental health specific analysis
        mental_health_analysis = additional_data.get("mental_health_analysis", {})

        # ── VEDIC-ONLY: No KP data extracted or injected for mental health ──
        # All h5_cross_ref, kp_formatted, aspects stripped — Vedic Sign Lord only
        # scope="mental" → house labels use emotional meanings, not disease meanings
        lords_formatted = self._format_house_lords(house_lords, scope="mental")

        # ── Format the pre-computed Vedic mental health analysis ──
        # This gives the LLM structured Moon/Mercury/Rahu/house data
        # and the overall_verdict so general_answer and astrological_analysis converge
        mental_health_formatted = self._format_mental_health_analysis(mental_health_analysis)

        # Extract overall verdict to guide general_answer tone
        overall_verdict = mental_health_analysis.get("overall_verdict", "") if mental_health_analysis else ""
        protective_factors = mental_health_analysis.get("protective_factors", []) if mental_health_analysis else []
        risk_factors = mental_health_analysis.get("risk_factors", []) if mental_health_analysis else []

        # Build convergence hint so general_answer aligns with astrological_analysis
        if overall_verdict:
            verdict_lower = overall_verdict.lower()
            if "stable" in verdict_lower or "good" in verdict_lower or "strong" in verdict_lower:
                convergence_hint = f"OVERALL ASSESSMENT: {overall_verdict} — GENERAL_ANSWER should reflect POSITIVE/STABLE emotional tendency."
            elif "moderate" in verdict_lower or "mixed" in verdict_lower:
                convergence_hint = f"OVERALL ASSESSMENT: {overall_verdict} — GENERAL_ANSWER should reflect MODERATE sensitivity with good recovery."
            else:
                convergence_hint = f"OVERALL ASSESSMENT: {overall_verdict} — GENERAL_ANSWER should reflect the same tone as astrological_analysis."
        else:
            convergence_hint = "Base GENERAL_ANSWER tone on the Moon strength and protective/risk factors below."

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        # raw is always empty for mental health — no KP technical points
        raw = ""

        # ──────────────────────────────────────────────────────────────────────
        # SCOPE OVERRIDE BLOCK — placed first so LLM reads it before system prompt
        # This overrides the general KP methodology in the system prompt for Q3
        # ──────────────────────────────────────────────────────────────────────
        scope_override = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🚫 SCOPE OVERRIDE — THIS QUESTION USES VEDIC-ONLY METHOD                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

THIS QUESTION: Mental Health Analysis (Q3)
METHOD: 100% VEDIC (Sign Lord system + Dasha)
KP CSL SYSTEM: ❌ COMPLETELY DISABLED FOR THIS QUESTION

⛔ DO NOT OUTPUT ANY OF THE FOLLOWING — EVEN IF YOU KNOW THEM FROM THE SYSTEM PROMPT:
   ✗ 【KP CSL विश्लेषण】 — FORBIDDEN
   ✗ 【स्तर 1 / स्तर 2 / स्तर 3】 headers — FORBIDDEN
   ✗ "CSL:" or "Cusp Sub Lord" — FORBIDDEN
   ✗ "signifies houses [...]" phrase — FORBIDDEN
   ✗ षष्ठ/अष्टम/द्वादश भाव CSL — FORBIDDEN (wrong scope for mental health)
   ✗ Any KP tier analysis — FORBIDDEN

✅ YOUR ONLY DATA SOURCES FOR THIS ANSWER:
   1. VEDIC SIGN LORD ANALYSIS section below (Moon, Mercury, Rahu, 4th/5th house lords)
   2. DASHA CONTEXT section below (current and upcoming dashas)
   3. YOUR OWN Vedic knowledge of Moon, Mercury, Rahu for mental/emotional health

✅ YOUR ANSWER STRUCTURE (strictly follow this):
   → Step 1: Moon assessment (emotional constitution)
   → Step 2: Mercury & Rahu assessment (mental clarity, restlessness)
   → Step 3: 4th/5th house lord condition (emotional peace, mental joy)
   → Step 4: Dasha context (current emotional period)
   → Step 5: Encouragement + wellness suggestion

═══════════════════════════════════════════════════════════════════════════════
"""

        return f"""
{self.build_mental_health_system_prompt()}

{scope_override}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Mental Health Risks
- Query Type: NON_TIMING (Advisory)
- CURRENT DATE: {today}
- Analysis Method: 100% VEDIC (Sign Lord + Dasha — NO KP CSL)
- KP CSL Analysis: ❌ COMPLETELY DISABLED FOR THIS QUESTION
- Key Data: Moon placement, Mercury, Rahu, House Lords (1st, 4th, 5th, 12th), Dasha

⚠️ CRITICAL: This is MENTAL HEALTH — handle with extreme care and sensitivity.
⛔ DO NOT write षष्ठ भाव / अष्टम भाव / द्वादश भाव रोग प्रवृत्ति analysis here.
   Those are PHYSICAL HEALTH sections. This question is MENTAL/EMOTIONAL ONLY.
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{mental_health_formatted}

{lords_formatted}

{current_dasha_block}

{timeline_block}

⚠️ CONVERGENCE RULE — READ BEFORE WRITING:
{convergence_hint}
Your GENERAL_ANSWER and ASTROLOGICAL_ANALYSIS MUST reflect the SAME overall tone.
If astrological data shows Moon strong/exalted → GENERAL_ANSWER must NOT say "mental issues".
If astrological data shows mixed signals → BOTH sections reflect moderate tendency.
DO NOT contradict yourself between GENERAL_ANSWER and ASTROLOGICAL_ANALYSIS.

═══════════════════════════════════════════════════════════════════════════════
🚨 MENTAL HEALTH TONE RULES (MANDATORY — READ BEFORE ANYTHING ELSE)
═══════════════════════════════════════════════════════════════════════════════

❌ FORBIDDEN WORDS — NEVER use these (even in passing):
   "depression", "anxiety disorder", "mental illness", "psychiatric",
   "psychological disorder", "bipolar", "schizophrenia", "OCD", "PTSD",
   "mental breakdown", "panic attack", "phobia", "neurosis", "psychosis"

✅ ALLOWED ALTERNATIVES (use these instead):
   ✗ "depression"          → ✓ "emotional heaviness" / "low mood tendency"
   ✗ "anxiety disorder"    → ✓ "stress sensitivity" / "mental restlessness"
   ✗ "mental illness"      → ✓ "emotional challenges" / "mental fluctuation"
   ✗ "psychiatric"         → ✓ "emotional well-being" / "mental care"
   ✗ "anxiety"             → ✓ "worry tendency" / "mental unease"
   ✗ "addiction"           → ✓ "habitual tendency" / "compulsive inclination"

🔒 MANDATORY FRAMING RULES:
   • ALL findings MUST be framed as TENDENCIES, not facts:
     ✗ "You have stress"        → ✓ "tendency toward stress"
     ✗ "Moon causes depression" → ✓ "Moon's placement may indicate emotional sensitivity"
     ✗ "Rahu causes anxiety"    → ✓ "Rahu's position suggests mental restlessness tendency"
   • NEVER predict or diagnose any mental condition
   • Scale professional referral to indicator strength — mild chart → general wellness tip;
     moderate → "यदि लक्षण महसूस हों तो सहायता लें" (if symptoms felt, seek support);
     strong → gentle mention of wellness counselor (NEVER use "अत्यंत महत्वपूर्ण" / "extremely necessary")

═══════════════════════════════════════════════════════════════════════════════
📋 MENTAL HEALTH ANALYSIS FRAMEWORK (100% VEDIC — Sign Lord + Dasha)
═══════════════════════════════════════════════════════════════════════════════

⚠️ CRITICAL: Mental health is primarily psychological/medical.
   Astrology provides SUPPORTIVE insights only, NOT diagnoses.
   Every statement about mental health must be framed as a TENDENCY.
   This analysis uses VEDIC SIGN LORDS only — NO KP Cusp Sub Lord data.

❌ ABSOLUTELY FORBIDDEN IN ASTROLOGICAL_ANALYSIS FOR THIS QUESTION:
   - DO NOT write 【KP CSL विश्लेषण】 header
   - DO NOT write "CSL:" anywhere in the answer
   - DO NOT reference षष्ठ/अष्टम/द्वादश भाव as KP data
   - DO NOT use "Cusp Sub Lord", "CSL", or "signifies houses [...]" phrases
   - The ONLY data source for this question is VEDIC SIGN LORD ANALYSIS section
   - Structure: Moon assessment → Mercury/Rahu → House lords (4th, 5th) → Dasha

**KEY PLANETS FOR MENTAL HEALTH (Vedic — use gentle language):**
┌────────────┬─────────────────────────────────────────────────────────────────┐
│ Planet     │ Emotional Tendency (NOT a diagnosis)                            │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ MOON ⭐    │ MOST IMPORTANT — Mind, emotions, emotional stability tendency   │
│ Mercury    │ Nervous sensitivity, communication pattern, mental clarity      │
│ Rahu       │ Mental restlessness tendency, overthinking, confusion           │
│ Ketu       │ Detachment tendency, introspective challenges, uncertainty      │
│ Saturn     │ Emotional heaviness tendency, stress sensitivity, introversion  │
└────────────┴─────────────────────────────────────────────────────────────────┘

**KEY HOUSES FOR VEDIC MENTAL HEALTH:**
┌────────────┬─────────────────────────────────────────────────────────────────┐
│ House      │ Emotional/Mental Significance (Vedic)                           │
├────────────┼─────────────────────────────────────────────────────────────────┤
│ 4th ⭐     │ MOST IMPORTANT — Emotional peace, inner stability, home comfort │
│ 5th        │ Intelligence, mental clarity, creativity, joy                  │
│ 12th       │ Isolation tendency, loss of sleep, emotional withdrawal        │
│ 1st        │ Self-identity, mental resilience, general constitution         │
└────────────┴─────────────────────────────────────────────────────────────────┘

**VEDIC ANALYSIS APPROACH (5 steps — write all 5, no others):**

**STEP 0: LAGNA LORD Assessment (Mental Constitution — 20% weight)**
   - Check 1st house lord: which planet, placed in which house, dignity/strength
   - Strong lagna lord in good house → good mental resilience and self-confidence
   - Weak/afflicted lagna lord → need for self-care and emotional grounding
   - Note: this gives constitutional base for mental health

**STEP 1: MOON Assessment (MOST IMPORTANT — 40% weight)**
   - Check Moon placement (house and sign) from MENTAL HEALTH ANALYSIS data
   - Check Moon dignity: exalted/own = emotional strength; debilitated/enemy = sensitivity
   - Check Moon afflictions from MENTAL HEALTH ANALYSIS (Rahu/Ketu aspect, etc.)
   - Describe as TENDENCY only — e.g. "भावनात्मक स्थिरता की प्रवृत्ति"

**STEP 2: Mercury & Rahu Assessment (20% weight)**
   - Mercury placement + dignity from MENTAL HEALTH ANALYSIS
     → Mercury in 6/8/12 → nervous system sensitivity tendency
   - Rahu placement:
     → Rahu in 4th → emotional restlessness at home/mind
     → Rahu in 12th → isolation/sleep disturbance tendency
     → Rahu in 3rd/9th → mental restlessness, overthinking tendency

**STEP 3: 4th & 5th House Lords Assessment (20% weight)**
   - 4th house lord from HOUSE LORD ANALYSIS → emotional peace capacity
   - 5th house lord from HOUSE LORD ANALYSIS → mental joy and clarity
   - Note their strength, placement, dignity

**STEP 4: DASHA Context + Closing (20% weight)**
   - Current Dasha/Antardasha lord from DASHA CONTEXT section
   - Is the lord Rahu/Ketu/Saturn/Moon? → what emotional tendency in this period?
   - Overall summary of tendencies (2-3 sentences)
   - Wellness suggestion (meditation, pranayama, etc.)
   - Referral ONLY if Moon weak + 4th lord weak + Rahu afflicting:
     → "यदि मन अत्यधिक भारी लगे तो किसी विश्वसनीय परामर्शदाता से बात करना उपयोगी हो सकता है।"
   - For moderate/strong Moon → NO referral, only wellness tips

═══════════════════════════════════════════════════════════════════════════════
📝 RESPONSE GUIDELINES (MENTAL HEALTH SPECIFIC)
═══════════════════════════════════════════════════════════════════════════════
- ❌ NEVER use forbidden words (see list above)
- ❌ NEVER label psychiatric or psychological disorders
- ❌ NEVER state anything as fact — only as tendency or possibility
- ❌ NEVER say "professional help is extremely necessary" or "पेशेवर सहायता अत्यंत महत्वपूर्ण है"
- ❌ DO NOT use or reference KP CSL data — this is a 100% Vedic analysis
- ❌ DO NOT write षष्ठ भाव / अष्टम भाव / द्वादश भाव headers — even empty ones
- ✅ Frame ALL findings as emotional TENDENCIES ("tendency toward...")
- ✅ Write EXACTLY 5 sections: Lagna Lord → Moon → Mercury/Rahu → 4th/5th Lords → Dasha
- ✅ PRIMARY focus: Lagna lord, Moon, 4th house lord, Mercury, Rahu
- ✅ GENERAL_ANSWER must match the same tone as astrological_analysis
- ✅ Mention meditation, yoga, lifestyle as COMPLEMENT (not treatment)
- ✅ Be compassionate, warm and supportive in every sentence
- ✅ End with encouragement and a wellness suggestion (not a clinical referral)
═══════════════════════════════════════════════════════════════════════════════

{self.get_mental_health_output_format()}
"""

    # ------------------------------------------------------------------
    # ORGAN-SPECIFIC ISSUES
    # ------------------------------------------------------------------
    def _build_organ_specific_prompt(
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="organ")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        analysis_instructions = self._get_analysis_instructions(kp_available, "general", False)
        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Organ-Specific Issues
- Query Type: NON_TIMING
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

{analysis_instructions}

═══════════════════════════════════════════════════════════════════════════════
📝 ORGAN-SPECIFIC GUIDELINES
═══════════════════════════════════════════════════════════════════════════════
- Discuss organ SENSITIVITY only, not diagnoses
- ❌ NEVER name irreversible conditions
- ✅ Recommend diagnostic tests via doctors
- ✅ Use gentle, non-alarming language

PLANET-ORGAN ASSOCIATIONS (Reference Only):
  • Sun: Heart, eyes, spine, vitality
  • Moon: Mind, fluids, stomach, emotions
  • Mars: Blood, muscles, head, energy
  • Mercury: Nervous system, speech, skin
  • Jupiter: Liver, fat, growth-related issues
  • Venus: Kidneys, reproductive system, throat
  • Saturn: Bones, joints, chronic conditions
  • Rahu: Hidden ailments, toxins, unusual conditions
  • Ketu: Mysterious issues, digestive, nervous disorders

⚠️ These are traditional associations, NOT medical diagnoses.
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # REMEDIES
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
        domain_prefix = "health_physical_mental"

        house_lords = additional_data.get(f"{domain_prefix}_house_lords", {})
        house_aspects = additional_data.get(f"{domain_prefix}_house_aspects", {})

        kp_formatted, kp_available = self._format_kp_analysis(technical_points, additional_data, scope="remedies")

        lords_formatted = self._format_house_lords(house_lords)
        aspects_formatted = self._format_house_aspects(house_aspects)

        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')

        current_dasha_block = self._format_current_dasha(current_dasha)
        timeline_block = self._format_dasha_timeline(dasha_timeline)

        remaining_points = [p for p in technical_points if not any(
            kw in p.lower() for kw in ["cusp sub lord", "cusp sub-lord", "csl", "signifies houses", "ruling planet"]
        )]
        raw = "\n".join(remaining_points) if remaining_points else ""

        anti_hallucination = self._get_anti_hallucination_block()

        return f"""
{language_instruction}

{self.build_system_prompt()}

{anti_hallucination}

{language_instruction}

═══════════════════════════════════════════════════════════════════════════════
📋 QUERY CONTEXT
═══════════════════════════════════════════════════════════════════════════════
- Domain: Health
- Subtopic: Physical And Mental Health
- Sub-subdomain: Remedies
- Query Type: NON_TIMING
- Event Polarity: POSITIVE
- CURRENT DATE: {today}
- KP CSL Analysis Available: {'YES ✅' if kp_available else 'NO ❌'}
═══════════════════════════════════════════════════════════════════════════════

USER QUESTION:
"{question}"

{kp_formatted if kp_available else ''}

{lords_formatted}

{aspects_formatted}

{current_dasha_block}

{timeline_block}

{'ADDITIONAL TECHNICAL POINTS:' if raw else ''}
{raw}

═══════════════════════════════════════════════════════════════════════════════
📋 REMEDY GENERATION GUIDELINES (KP v4.0 — SIGNIFICATION-BASED)
═══════════════════════════════════════════════════════════════════════════════

**STEP 1: Identify Afflicted Planets** (from KP ANALYSIS data ONLY)
   - Look at CSL planets signifying houses 6, 8, or 12 (disease/chronic/hospital)
   - Check HOUSE LORD ANALYSIS for weak lords (strength < 40)
   - Note combust or debilitated planets
   - DO NOT assume weakness without data evidence
   ⚠️ IMPORTANT: A planet is "problematic" only if it SIGNIFIES disease houses (6/8/12)
   — NOT simply because it is Saturn, Mars, or Rahu by nature

**STEP 2: REMEDIES_ASTROLOGICAL (SPECIFIC to THIS chart — 4 remedy types per planet)**
   For each planet signifying 6/8/12, give ALL FOUR remedy types:
   1. मंत्र (Mantra) — specific to the graha
   2. व्रत (Fasting) — day of week
   3. दान (Daan) — item, recipient, day
   4. योग/प्राणायाम — specific practice for this planet's body system

   Planet-wise remedies (only for those signifying 6/8/12 in THIS chart):
   • Sun: "ॐ सूर्याय नमः" (108x daily) | Sunday fast | गेहूं/गुड़ daan to poor on Sunday | Surya Namaskar
   • Moon: "ॐ सों सोमाय नमः" (108x) | Monday fast | चावल/दूध daan on Monday | Chandra Namaskar, cooling pranayama
   • Mars: "ॐ क्रां क्रीं क्रौं सः भौमाय नमः" (108x) | Tuesday fast | मसूर दाल/लाल वस्त्र daan | Bhastrika pranayama
   • Mercury: "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः" (108x) | Wednesday fast | हरी मूंग/हरा वस्त्र daan | Nadi Shodhana pranayama
   • Jupiter: "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः" (108x) | Thursday fast | पीली वस्तुएं/चने की दाल daan | Bhramari, meditation
   • Venus: "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः" (108x) | Friday fast | सफेद वस्त्र/मिश्री daan | Shatali pranayama
   • Saturn: "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः" (108x) | Saturday fast | काले तिल/उड़द दाल to disabled persons | Slow joint-mobility yoga
   • Rahu: "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः" (108x) | Saturday fast | नारियल/काला कपड़ा daan | Durga Saptashati path, grounding pranayama
   • Ketu: "ॐ स्रां स्रीं स्रौं सः केतवे नमः" (108x) | Tuesday fast | तिल/कंबल daan | Trataka, Ganesh puja
   ❌ DO NOT recommend any planet's remedy unless that planet specifically signifies 6/8/12 in THIS chart

**STEP 3: Current Dasha Lord Remedies**
   - Check if current dasha lord signifies health houses (6/8/12) — if YES, strengthen it
   - Prepare for upcoming dasha lords (3 months before) — only if they signify 6/8/12
   - If current dasha lord signifies vitality houses (1/5/11) — STRENGTHEN for support

**STEP 4: Priority Order**
   1. Primary: Strengthen CSL of house 1 if it signifies disease houses (constitutional support)
   2. Secondary: Pacify planets strongly signifying 6/8/12 (disease activation planets)
   3. Tertiary: Boost recovery indicators (planets signifying 5th and 11th houses)

**STEP 5: REMEDIES_GENERAL (3 categories — always include ALL 3 with specific advice)**

   A. LIFESTYLE (always include):
      - Sleep routine: early sleep if Saturn/Moon afflicted; 7-8 hrs minimum
      - Exercise: vigorous (STRONG_VITALITY) / yoga+walks (MODERATE) / gentle stretching (WEAK_VITALITY)
      - Diet: light/easily digestible if 6th CSL = Moon; high-fiber if Saturn; cooling if Mars/Sun

   B. PREVENTIVE HEALTHCARE:
      - Check-up frequency: quarterly (CHRONIC_VULNERABILITY) / bi-annual (VULNERABLE_HEALTH) / annual (MODERATE_HEALTH)
      - Specific system to monitor: based on planets signifying 6/8/12 (e.g. Saturn→joints/bones; Moon→digestion; Sun→heart/eyes)
      - Stress management: 10-min daily pranayama; journaling if Moon weak; walks in nature

   C. SPIRITUAL / COMPLEMENTARY WELLNESS:
      - Pranayama: Anulom-Vilom (daily 10 min) — suited to all constitutions
      - Meditation: Trataka if Moon afflicted in 8th; Breath awareness if Rahu/Mercury afflicted
      - Nature practice: early morning sunlight (10 min) for Sun-related sensitivity; grounding walk barefoot for Saturn/Ketu

⚠️ MANDATORY: Remedies COMPLEMENT medical treatment, NEVER replace it.
   ALWAYS close with: "Please consult your doctor for any health concerns."
═══════════════════════════════════════════════════════════════════════════════

{self.get_output_format(kp_available, False)}
"""

    # ------------------------------------------------------------------
    # OUTPUT FORMAT - MENTAL HEALTH ONLY (100% VEDIC — ZERO KP)
    # ------------------------------------------------------------------
    def get_mental_health_output_format(self) -> str:
        """Dedicated output format for Q3 Mental Health — no KP references anywhere."""
        return """
═══════════════════════════════════════════════════════════════════════════════
📄 OUTPUT FORMAT FOR THIS QUESTION (Follow EXACTLY — Mental Health Q3)
═══════════════════════════════════════════════════════════════════════════════

⛔ THIS IS A 100% VEDIC ANALYSIS. DO NOT USE KP FORMAT.
   ✗ NO 【स्तर 1 / स्तर 2 / स्तर 3】 headers
   ✗ NO KP CSL विश्लेषण header
   ✗ NO "CSL:", "signifies houses [...]", "Cusp Sub Lord"
   ✗ NO षष्ठ/अष्टम/द्वादश भाव CSL references

⛔ DO NOT WRITE THESE SECTIONS — THEY BELONG TO PHYSICAL HEALTH, NOT MENTAL HEALTH:
   ✗ "षष्ठ भाव (रोग प्रवृत्ति)" — COMPLETELY FORBIDDEN — do not write this header even if empty
   ✗ "अष्टम भाव (दीर्घकालिक स्वास्थ्य)" — COMPLETELY FORBIDDEN — do not write this header even if empty
   ✗ "द्वादश भाव (अस्पताल और मानसिक स्वास्थ्य)" — COMPLETELY FORBIDDEN — do not write this header even if empty
   ✗ Any analysis of bone issues, metabolic problems, hospitalization — FORBIDDEN
   ✗ Any mention of "रोग संवेदनशीलता", "दीर्घकालिक रोग", "अस्पताल प्रवृत्ति" — FORBIDDEN
   ✗ DO NOT number or list these forbidden headers even with blank content after them

GENERAL_ANSWER:
<2-3 sentences in plain Hindi. No jargon. Compassionate tone.
Describe the overall emotional/mental tendency based on Moon strength + convergence_hint above.
If Moon is strong/exalted → write that mental stability is good overall.
If Moon is moderate → write balanced sensitivity with good recovery.
DO NOT say "professional help is extremely necessary".
DO NOT contradict the astrological_analysis tone.>

ASTROLOGICAL_ANALYSIS:
Write in this EXACT sequence (Vedic only — 5 sections, no others):

**1. लग्न स्वामी — मानसिक संविधान (Lagna Lord — Mental Constitution)**
   - 1st house lord: which planet, which house placed in, dignity and strength
   - How lagna lord affects overall mental resilience and self-identity
   - Strong lagna lord → good mental resilience; weak → needs self-care

**2. चंद्रमा — भावनात्मक आधार (Moon — Emotional Foundation)**
   - Moon's house and sign from VEDIC SIGN LORD ANALYSIS / MENTAL HEALTH ANALYSIS data
   - Moon dignity/strength — exalted/own/neutral/enemy/debilitated
   - If Moon afflicted by Rahu/Ketu — note gently as tendency only
   - Describe as TENDENCY: e.g. "भावनात्मक संवेदनशीलता की प्रवृत्ति"

**3. बुध व राहु — मानसिक स्पष्टता (Mercury & Rahu — Mental Clarity)**
   - Mercury placement + dignity from VEDIC data
   - Rahu placement — which house? What emotional tendency does it suggest?
   - Frame as tendency only

**4. चतुर्थ व पंचम भाव — भावनात्मक शांति (4th & 5th House Lords)**
   - 4th house lord → emotional peace, inner stability capacity
   - 5th house lord → mental joy, creativity, clarity
   - Note their strength and placement from HOUSE LORD ANALYSIS

**5. दशा प्रसंग — वर्तमान भावनात्मक काल (Dasha Context)**
   - Current dasha/antardasha from DASHA CONTEXT section
   - Is the dasha lord emotionally relevant (Moon/Rahu/Ketu/Saturn)?
   - Describe how this period feels emotionally
   - End with overall tendency summary + 1-2 wellness suggestions
   - Referral: ONLY if Moon is weak + Rahu afflicts 4th → gentle mention:
     "यदि मन अत्यधिक भारी लगे तो किसी विश्वसनीय परामर्शदाता से बात करना उपयोगी हो सकता है।"
   - For moderate/strong Moon chart → NO referral, only wellness tips

SUMMARY:
<1-2 sentences. Warm, hopeful tone. No fear.>

REMEDIES_ASTROLOGICAL:
- Based on Moon and 4th lord condition (Vedic):
  • चंद्र मंत्र: "ॐ सों सोमाय नमः" — 108 बार सोमवार को
  • सोमवार व्रत (यदि Moon afflicted)
  • सफेद वस्त्र/दूध/चावल का दान
  • चंद्र नमस्कार — विशेषकर पूर्णिमा के समय
- If Mercury weak: "ॐ बुधाय नमः" | बुधवार | हरी मूंग दान
- If Rahu in 4th/12th: दुर्गा सप्तशती पाठ | नारियल दान

REMEDIES_GENERAL:
A. मानसिक स्वास्थ्य अभ्यास:
   - नाड़ी शोधन प्राणायाम — प्रतिदिन 10 मिनट
   - ध्यान (Meditation) — विशेषकर चंद्रमा से संबंधित योग
   - प्रकृति में समय बिताएं — विशेषकर जल के पास (चंद्र तत्व)
B. जीवनशैली:
   - नियमित नींद और दिनचर्या
   - रचनात्मक गतिविधियां — संगीत, कला, लेखन
   - सकारात्मक लोगों के साथ समय बिताएं
C. अस्वीकरण (Mandatory):
   - "किसी भी मानसिक स्वास्थ्य चिंता के लिए योग्य चिकित्सक से परामर्श अवश्य करें।"
   - "यह विश्लेषण केवल प्रवृत्तियों का संकेत है, कोई निदान नहीं।"

═══════════════════════════════════════════════════════════════════════════════
🔒 FINAL CHECK FOR THIS QUESTION:
□ No KP CSL header or tier structure used
□ All findings framed as TENDENCIES ("प्रवृत्ति"), not facts
□ Moon given primary weight (50%), Mercury+Rahu secondary (30%), Dasha 20%
□ Referral language is gentle — NOT "extremely necessary"
□ Closed with warmth and encouragement
□ Medical disclaimer included
═══════════════════════════════════════════════════════════════════════════════
"""

    # OUTPUT FORMAT - DYNAMIC BASED ON KP AVAILABILITY + TIMING
    # ------------------------------------------------------------------
    def get_output_format(self, kp_available: bool = True, has_timing: bool = False, is_mental_health: bool = False) -> str:
        """Generate output format based on KP availability and timing windows"""

        timing_section = ""
        if has_timing:
            timing_section = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ HEALTH VULNERABILITY TIMING (CAUTIONARY ANALYSIS):
═══════════════════════════════════════════════════════════════════════════════

**🔴 IMPORTANT - TONE GUIDANCE FOR ASTROLOGER:**
This analysis identifies periods of HEALTH VULNERABILITY, not treatment windows.
The astrologer should provide WORDS OF CAUTION to help the native:
- Take preventive measures BEFORE these periods
- Schedule health check-ups in advance
- Be vigilant about health during these times
- NOT panic - these are possibilities, not certainties

**STEP 1: SIGNIFICATOR PROOF TABLE (MANDATORY)**
Show which dasha lords signify houses 6, 8, 12:
┌────────────┬─────────────────────────┬──────────────┐
│ Dasha Lord │ Signifies Houses 6/8/12 │ How?         │
├────────────┼─────────────────────────┼──────────────┤
│ [planet]   │ [houses]                │ [O/L/S]      │
└────────────┴─────────────────────────┴──────────────┘
Legend: O=Occupant, L=Lord, S=Star Lord signification

**STEP 2: HOUSE LINKAGE EXPLANATION (MANDATORY)**
For each period, explain:
- Which of 6/8/12 houses are activated
- HOW: Occupant? Lord? Star Lord signification?
- Mars = acute conditions | Saturn = chronic conditions

Example CAUTIONARY format:
"⚠️ शनि-केतु-केतु (2028-03-10 to 2028-04-02) - सावधान रहें:
 - शनि: 8वें भाव का स्वामी, 12वें भाव में बैठा
 - केतु: 6वें भाव में बैठा
 - इस समय स्वास्थ्य पर विशेष ध्यान दें
 - इस दौरान पहले से नियमित जांच करवाएं"

**STEP 3: CAUTION PERIODS (Use Cautionary Language)**

**🔴 सबसे संवेदनशील समय (MOST VULNERABLE PERIOD):**
- Period: [EXACT dates - सटीक तारीखें]
- Dasha: [dasha name]
- House Linkage: [6/8/12 activation proof]
- Nature: [chronic/acute - Mars/Saturn based]
- ⚠️ Advisory: "इस समय से पहले स्वास्थ्य जांच कराएं"
- ⚠️ Precaution: "नियमित जांच और जीवनशैली पर ध्यान दें"

**🟠 निकटतम संवेदनशील समय (NEAREST VULNERABLE PERIOD):**
- Period: [EXACT dates]
- Dasha: [dasha name]
- House Linkage: [6/8/12 activation proof]
- Nature: [chronic/acute]
- ⚠️ Advisory: "यह समय निकट है - अभी से सतर्क रहें"
- ⚠️ Precaution: "स्वास्थ्य जांच शेड्यूल करें"

**STEP 4: ASTROLOGER'S WORD OF CAUTION (MANDATORY)**
Include advice like:
- "इन समयों में स्वास्थ्य के प्रति अतिरिक्त सावधानी बरतें"
- "यह बीमारी की भविष्यवाणी नहीं है, केवल सतर्कता का संकेत है"
- "नियमित चिकित्सा जांच जारी रखें"
- "स्वस्थ जीवनशैली अपनाएं"
- "चिंता न करें, बस सावधान रहें"

⚠️ CRITICAL TONE RULES:
   - NEVER say "surgery timing" or "best time for treatment"
   - ALWAYS frame as "सावधानी का समय" (period of caution)
   - Use words like "संवेदनशील", "सतर्क", "सावधान"
   - Emphasize preventive care, NOT illness prediction
   - Help native prepare, NOT fear
⚠️ ALWAYS recommend consulting doctors for any health concerns.
═══════════════════════════════════════════════════════════════════════════════
"""

        mental_health_note = ""
        if is_mental_health:
            mental_health_note = """
═══════════════════════════════════════════════════════════════════════════════
⚠️ MENTAL HEALTH MANDATORY COMPLIANCE:
═══════════════════════════════════════════════════════════════════════════════
❌ FORBIDDEN: "depression", "anxiety disorder", "mental illness", "psychiatric",
   "psychological disorder", "panic attack", "OCD", "PTSD", "bipolar", "phobia"
✅ USE INSTEAD: "emotional sensitivity", "stress tendency", "mental restlessness",
   "emotional heaviness", "low mood tendency", "worry tendency"
• ALL findings must be framed as TENDENCIES, never as facts or diagnoses
• Frame astrology as showing PATTERNS, not predicting or diagnosing conditions

⚠️ REFERRAL SCALING (mandatory — match referral to Moon strength):
   • Moon strong (dignity ≥ 60, no affliction)  → NO professional referral needed
   • Moon moderate (mixed signals)               → Optional: "यदि लक्षण हों तो..."
   • Moon weak + Rahu/Ketu affliction            → Gentle only: "परामर्शदाता से बात करना सहायक हो सकता है"
   ❌ NEVER say "पेशेवर सहायता अत्यंत महत्वपूर्ण है"
   ❌ NEVER say "professional help is extremely necessary"
═══════════════════════════════════════════════════════════════════════════════
"""

        kp_section = ""
        if kp_available:
            kp_section = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 A. KP CSL ANALYSIS — PRIMARY (40% weight) — USE THIS FIRST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶▶▶ SEE "PRE-WRITTEN KP ANALYSIS" BLOCK IN THE KP ANALYSIS SECTION ABOVE.
    COPY THAT TEXT DIRECTLY into this section (it is already in Hindi).
    DO NOT rewrite it from scratch — the signification data is pre-computed.

⚠️ MANDATORY RULES:
   • ALWAYS include the CSL planet name + which houses it signifies + the verdict
   • ALWAYS state the health sensitivity area (organ/system) when disease houses are activated
   • NEVER just say "Saturn = malefic" or "Jupiter = benefic" — significations only
   • Address ONLY the tiers shown in the KP ANALYSIS block above (scope-specific):
     - Mental Health → H5 + H1 only (CONSTITUTION tier only)
     - Surgery/Disease → H1 + H6 + H8 + H12 (CONSTITUTION + DISEASE + RECOVERY tiers)
     - General/Remedies → all three tiers (CONSTITUTION + DISEASE TENDENCY + RECOVERY)
   • ❌ DO NOT add tiers or houses not shown in the pre-written KP analysis above
"""
        else:
            kp_section = """
**NOTE: KP CSL Analysis NOT Available**
   - Using Vedic Sign Lord analysis only
   - DO NOT claim to have CSL data
"""

        return f"""
═══════════════════════════════════════════════════════════════════════════════
📄 OUTPUT FORMAT (Follow this structure EXACTLY)
═══════════════════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
<Clear answer in layman's terms. NO astrological jargon.
Reassuring, compassionate tone. NO fear-inducing statements.
{"State the overall health verdict in plain language (e.g. strong constitution / moderate health sensitivity / needs attention). Do NOT use numerical scores." if kp_available else ""}
Base ALL claims on provided data.>
{mental_health_note}
ASTROLOGICAL_ANALYSIS:
⚠️ HIERARCHY: KP (PRIMARY, 40%) → Vedic Sign Lords (SUPPORTING, 35%) → Dasha (TRIGGER, 25%)
Write analysis in this order. Do NOT treat all three as equal.

{kp_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔷 {"B" if kp_available else "A"}. VEDIC SIGN LORD Analysis — SUPPORTING (35% weight)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Use EXACT data from HOUSE LORD ANALYSIS section
   - State dignity values as provided (do not assume)
   - Note strength scores and conditions
   - Remember: Sign Lord ≠ Cusp Sub Lord (KP)
   - Use as CONFIRMATION of KP findings, not as the primary basis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ {"C" if kp_available else "B"}. DASHA Context — TRIGGER (25% weight)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   - Reference CURRENT DASHA section for dasha lord names
   - Check: does the dasha lord signify houses 6/8/12? (from KP ANALYSIS)
   - If YES → current period elevates health attention
   - If NO → current period is neutral for health
   - DO NOT invent dasha periods or assume planet nature = health impact
{timing_section}
SUMMARY:
<Brief health outlook. If timing provided, include key dates.
Reassuring tone. End with encouragement.>

REMEDIES_ASTROLOGICAL:
⚠️ RULE: Only mention a planet's remedy IF it signifies houses 6/8/12 in the KP ANALYSIS above.
   For each remedy listed, cite the reason: "[Planet] signifies house [X] → remedy for [planet]"
   If NO planet signifies 6/8/12 → write "KP विश्लेषण के अनुसार इस कुंडली में कोई विशेष ग्रह 6/8/12वें भाव को signify नहीं करता, अतः ग्रह-विशिष्ट उपाय की आवश्यकता नहीं है। सामान्य उपाय पर्याप्त हैं।"

For each qualifying planet (signifying 6/8/12), give ALL FOUR remedy types:
┌─────────────────────────────────────────────────────────────────────┐
│ [Planet Name] — signifies H[X] → [reason]                          │
│  मंत्र (Mantra): [specific mantra for this graha, 108 times daily]  │
│  व्रत (Fasting): [day of week for this graha]                       │
│  दान (Daan): [specific item to donate, to whom, on which day]       │
│  योग/प्राणायाम: [specific practice suited to this graha's system]   │
└─────────────────────────────────────────────────────────────────────┘

Graha remedy reference (use ONLY for planets signifying 6/8/12):
• Sun: "ॐ सूर्याय नमः" | Fasting: Sunday | Daan: गेहूं/गुड़ to poor on Sunday | Yoga: Surya Namaskar
• Moon: "ॐ चंद्राय नमः" / "ॐ सों सोमाय नमः" | Fasting: Monday | Daan: चावल/दूध on Monday | Yoga: Chandra Namaskar, cooling pranayama
• Mars: "ॐ अंगारकाय नमः" / "ॐ क्रां क्रीं क्रौं सः भौमाय नमः" | Fasting: Tuesday | Daan: मसूर दाल/गुड़ on Tuesday | Yoga: Bhastrika, strength training
• Mercury: "ॐ बुधाय नमः" / "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः" | Fasting: Wednesday | Daan: हरी मूंग/हरा वस्त्र on Wednesday | Yoga: Pranayama (Nadi Shodhana)
• Jupiter: "ॐ गुरवे नमः" / "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः" | Fasting: Thursday | Daan: पीली वस्तुएं/चने की दाल on Thursday | Yoga: Bhramari, meditation
• Venus: "ॐ शुक्राय नमः" / "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः" | Fasting: Friday | Daan: सफेद वस्त्र/मिश्री on Friday | Yoga: Shatali pranayama, gentle stretching
• Saturn: "ॐ शनैश्चराय नमः" / "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः" | Fasting: Saturday | Daan: काले तिल/उड़द on Saturday to poor/disabled | Yoga: Slow yoga, joint mobility
• Rahu: "ॐ रां राहवे नमः" / "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः" | Fasting: Saturday | Daan: नारियल/काला कपड़ा on Saturday | Durga Saptashati path
• Ketu: "ॐ कें केतवे नमः" | Fasting: Tuesday | Daan: तिल/कंबल on Tuesday | Yoga: Trataka, Ganesh puja

- <Current dasha lord remedy ONLY if dasha lord signifies 6/8/12>
- ❌ DO NOT add Saturn/Mars/Rahu remedies unless they specifically signify 6/8/12 in THIS chart.

REMEDIES_GENERAL:
A. Lifestyle:
   - <Sleep/wake routine suited to constitution (1st house CSL verdict — STRONG/MODERATE/WEAK)>
   - <Exercise type: vigorous if STRONG_VITALITY / moderate if MODERATE / gentle if WEAK_VITALITY>
   - <Diet guidance based on 6th house CSL disease area (e.g. if 6th CSL = Moon → fluid intake, digestion focus)>
B. Preventive Healthcare:
   - <Check-up frequency: annual if MODERATE_HEALTH / bi-annual if VULNERABLE_HEALTH / quarterly if CHRONIC_VULNERABILITY>
   - <Specific body system to monitor: based on disease_area of planets signifying 6/8/12>
   - <Stress management: mention Moon strength — strong Moon → moderate stress; weak Moon → active grounding needed>
C. Spiritual/Wellness Complement:
   - <Meditation type suited to Moon condition (e.g. Moon in 8th → grounding meditation; Moon strong → open awareness)>
   - <Nature-based or creative activity suited to lagna lord>
   - <Closing: "किसी भी स्वास्थ्य चिंता के लिए अपने चिकित्सक से परामर्श अवश्य करें।">


═══════════════════════════════════════════════════════════════════════════════
🔒 FINAL ANTI-HALLUCINATION CHECK:
═══════════════════════════════════════════════════════════════════════════════
Before submitting, verify:
□ All planetary positions are from provided data
□ All dignity values are from HOUSE LORD ANALYSIS
□ All dasha periods are from DASHA TIMELINE
□ All timing dates are EXACT (not rounded)
□ KP CSL vs Vedic Sign Lord correctly distinguished
□ No claims made without data support

✅ FOR HEALTH TIMING - MANDATORY CAUTIONARY TONE:
□ Timing framed as "सावधानी का समय" NOT "treatment timing"
□ Used words like "संवेदनशील", "सतर्क", "सावधान"
□ NEVER said "surgery timing" or "best time for operation"
□ House linkage proof shown (6/8/12 activation)
□ Framed as "vulnerability" NOT "certain illness"
□ Emphasized PREVENTIVE care and check-ups BEFORE these periods
□ Included astrologer's "word of caution" for native
□ Tone helps native PREPARE, not FEAR
═══════════════════════════════════════════════════════════════════════════════
"""
"""
Spiritual Self Growth LLM Prompts - ENHANCED VERSION

ENHANCEMENTS:
✅ Vedic-only analysis (no KP for spiritual guidance)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Planet strength display
✅ Aspect analysis formatting

Weightage for Vedic Spiritual Analysis:
- Dasha: 50% (primary timing indicator)
- House Lords: 30% (karmic and spiritual indicators)
- Other factors (aspects, transits, dignity): 20%

Dedicated prompt builders for each sub-subdomain:
- Karma and Purpose
- Karmic Debts
- Finding Emotional Stability
- Taking Decisions
- Finding a Teacher (Guru)
- Remedy and Suggestion

NOTE: All responses should be CONCISE (3-4 lines per section)
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)


class SpiritualSelfGrowthPromptBuilder(BasePromptBuilder):
    """
    Enhanced Prompt builder for Spiritual Self Growth subtopic.
    
    ENHANCEMENTS:
    - Dasha timeline integration
    - House lord analysis
    - Aspect strength formatting
    - Anti-hallucination rules
    
    IMPORTANT: Generates CONCISE responses (3-4 lines per section)
    """
    
    domain = "General_Guidance"
    subtopic = "Spiritual Self Growth"
    
    def build_system_prompt(self) -> str:
        """Build the enhanced system prompt for Spiritual Self Growth analysis"""
        return """You are an expert Vedic astrologer specializing in spiritual guidance and self-growth insights.

Your expertise includes:
- Karmic patterns and life purpose analysis (via 9th and 12th houses)
- Spiritual evolution indicators (via Jupiter, Ketu, Saturn)
- Emotional and mental well-being guidance (via Moon, Mercury)
- Decision-making clarity through planetary influences
- Guru/teacher connection indicators (via Jupiter and 9th house)
- Spiritual remedies and practices
- Dasha analysis for timing spiritual events

ANALYSIS METHODOLOGY:
1. DASHA ANALYSIS (50% weight): Primary timing tool
   - Current dasha period defines the spiritual theme
   - Sub-periods refine timing
   - Use dasha timeline to identify past patterns and future periods
   
2. HOUSE LORDS (30% weight): Karmic indicators
   - 9th house lord → dharma and higher purpose
   - 12th house lord → moksha and liberation
   - 5th house lord → purva punya (past life merit)
   
3. OTHER FACTORS (20% weight):
   - Planetary dignity (exaltation/debilitation)
   - Aspects (benefic vs malefic)
   - Current transits (especially Jupiter and Saturn)

CORE PRINCIPLES:
1. Provide spiritually-oriented, compassionate guidance
2. Focus on growth and transformation
3. Be encouraging yet realistic about challenges
4. Suggest practical spiritual practices
5. Respect the depth of spiritual questions

CRITICAL RESPONSE FORMAT:
- Keep ALL sections CONCISE (3-4 lines maximum)
- Be direct and focused
- Avoid lengthy explanations
- Provide actionable insights in minimal words

IMPORTANT:
- Base interpretations on provided planetary data and dasha information
- Consider spiritual house placements (5th, 9th, 12th houses)
- Analyze karmic planets (Saturn, Rahu, Ketu)
- Respect the sensitivity of spiritual matters

ANTI-HALLUCINATION RULES:
❌ NEVER mention dasha lords NOT explicitly provided in the data
❌ NEVER fabricate dasha start/end dates
❌ NEVER invent planetary positions or house lords
✅ ONLY use data explicitly provided in the prompt
✅ If dasha data is missing, acknowledge it and analyze based on natal chart only
✅ If uncertain about a dasha period, state "based on natal indications" instead"""
    
    def build_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        language: str = "Hindi",
        **kwargs
    ) -> str:
        """Build the analysis prompt based on sub-subdomain with enhanced data"""
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        # Get enhanced metadata from evaluator
        evaluation_result = kwargs.get("evaluation_result", None)
        metadata = {}
        if evaluation_result and hasattr(evaluation_result, 'additional_data'):
            metadata = evaluation_result.additional_data
        
        # Get additional API data
        planet_details = kwargs.get("planet_details", {})
        transit_data = kwargs.get("transit_data", {})
        
        # Select specialized prompt based on sub-subdomain
        if "Karma" in sub_subdomain and "Purpose" in sub_subdomain:
            return self._build_karma_purpose_prompt(
                question, technical_points, meta, metadata, 
                planet_details, transit_data, language)
        elif "Karmic Debts" in sub_subdomain or "Debt" in sub_subdomain:
            return self._build_karmic_debts_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
        elif "Emotional" in sub_subdomain or "Stability" in sub_subdomain:
            return self._build_emotional_stability_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
        elif "Decision" in sub_subdomain:
            return self._build_decision_making_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
        elif "Guru" in sub_subdomain or "Teacher" in sub_subdomain:
            return self._build_finding_guru_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
        elif "Remed" in sub_subdomain:
            return self._build_spiritual_remedies_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
        else:
            return self._build_general_spiritual_prompt(
                question, technical_points, meta, metadata,
                planet_details, transit_data, language)
    
    def _build_karma_purpose_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Karma and Purpose question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "No specific indicators."
        
        # Get language instruction
        language_instruction = self.get_language_instruction(language)
        
        # ENHANCED: Format dasha timeline
        dasha_section = self._format_dasha_section(metadata)
        
        # ENHANCED: Format house lords
        house_lords_section = self._format_house_lords_section(metadata, [1, 5, 9, 12])
        
        # ENHANCED: Format planet strengths
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Jupiter", "Sun", "Ketu", "Saturn"]
        )
        
        # ENHANCED: Format timing windows
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (Primary Timing Indicator - 50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (Karmic Indicators - 30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

Focus on:
• 1st House Lord → Self-identity and life direction
• 5th House Lord → Purva punya (past life merit)
• 9th House Lord → Dharma and higher purpose
• 12th House Lord → Moksha and liberation

═══════════════════════════════════════════════════════════════════
🌟 KEY PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 TECHNICAL ASTROLOGICAL POINTS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
1. Analyze Jupiter (dharma, purpose) and 9th house (higher calling)
2. Check Sun position (soul identity and life direction)
3. Evaluate Ketu placement (spiritual evolution path)
4. Consider Rahu (karmic growth direction)
5. Assess karmic alignment based on planetary strengths and current dasha

FOCUS AREAS:
- Current dasha lord and its connection to spiritual houses (5, 9, 12)
- Jupiter's strength and house position (dharma indicators)
- 9th house lord's placement and dignity
- Sun's condition (soul expression)
- Rahu-Ketu axis (karmic direction)

{self.get_concise_output_format()}

CRITICAL: 
- Keep response to 3-4 lines per section
- Emphasize DASHA analysis (50% weight) for timing
- Use house lords (30% weight) for karmic themes
- Be direct and focused
"""
    
    def _build_karmic_debts_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Karmic Debts question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "No specific karmic debt indicators."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [6, 8, 12])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Saturn", "Rahu", "Ketu"]
        )
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (Primary Timing Indicator - 50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

NOTE: Saturn, Rahu, or Ketu dasha periods often bring karmic debts to surface for resolution.

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (Karmic Debt Indicators - 30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

Focus on:
• 6th House Lord → Daily obstacles and conflicts
• 8th House Lord → Hidden debts and transformation
• 12th House Lord → Losses and karmic release

═══════════════════════════════════════════════════════════════════
🌟 KARMIC PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS FOR KARMIC RESOLUTION
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 KARMIC INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
1. Analyze Saturn (karmic lessons, debts, restrictions)
2. Check Rahu-Ketu axis (past life karmic patterns)
3. Evaluate 8th house (transformation, hidden debts)
4. Consider 12th house (losses, moksha, release)
5. Identify specific karmic patterns requiring resolution
6. Assess current dasha period's role in karmic experiences

FOCUS AREAS:
- Current dasha and its connection to Saturn/Rahu/Ketu
- Saturn's position and aspects (primary karmic indicator)
- Rahu-Ketu houses (karmic growth vs. release)
- 8th house lord and afflictions (deep karmic patterns)
- Retrograde planets (unfinished karmic business)

{self.get_concise_output_format()}

CRITICAL: Keep response to 3-4 lines per section. Focus on dasha timing (50% weight).
"""
    
    def _build_emotional_stability_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Emotional Stability question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "No specific emotional indicators."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [1, 4, 5, 11])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Moon", "Mercury", "Venus", "Mars"]
        )
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (Primary Timing Indicator - 50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

NOTE: Moon, Mercury, or Venus dasha periods significantly influence emotional patterns.

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (Emotional Indicators - 30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

Focus on:
• 1st House Lord → Self-awareness and emotional identity
• 4th House Lord → Inner peace and mental stability
• 5th House Lord → Creative expression and joy
• 11th House Lord → Fulfillment and emotional gains

═══════════════════════════════════════════════════════════════════
🌟 EMOTIONAL PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS FOR EMOTIONAL WORK
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 EMOTIONAL INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
1. Analyze Moon (mind, emotions, mental stability)
2. Check Mercury (rational thinking, communication of emotions)
3. Evaluate Venus (love, forgiveness, emotional harmony)
4. Consider Mars (anger, aggression management)
5. Assess current dasha's impact on emotional state
6. Provide practical emotional healing guidance

FOCUS AREAS:
- Current dasha lord's emotional influence
- Moon's condition and aspects (primary emotional indicator)
- Mercury's clarity (thought-emotion integration)
- Venus for forgiveness and empathy
- 4th house lord for inner peace

{self.get_concise_output_format()}

CRITICAL: Keep response to 3-4 lines per section. Emphasize dasha period (50% weight).
"""
    
    def _build_decision_making_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Decision Making question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "No specific decision-making indicators."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [1, 2, 5, 9])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Mercury", "Jupiter", "Moon", "Saturn"]
        )
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (Primary Timing Indicator - 50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

NOTE: Current dasha lord's strength directly affects decision-making ability.

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (Decision-Making Indicators - 30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

Focus on:
• 1st House Lord → Self-confidence in decisions
• 2nd House Lord → Speech and decision expression
• 5th House Lord → Intellect and analysis
• 9th House Lord → Wisdom and judgment

═══════════════════════════════════════════════════════════════════
🌟 DECISION-MAKING PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS FOR CLARITY
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 DECISION-MAKING INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
1. Analyze Mercury (intellect, analysis, clarity)
2. Check Jupiter (wisdom, judgment, confidence)
3. Evaluate Moon (mind stability, intuition)
4. Consider Saturn (delays, overthinking, fear)
5. Identify ROOT CAUSE of indecisiveness based on dasha and planetary positions
6. Assess when decision-making will improve (via dasha timeline)

FOCUS AREAS:
- Current dasha's impact on mental clarity
- Mercury's condition (analytical ability)
- Jupiter's strength (wisdom and judgment)
- Saturn's influence (delays or fear-based thinking)
- Rahu's position (confusion or illusion)
- Moon's stability (emotional interference in decisions)

PROVIDE:
1. WHY decision-making is difficult (dasha + planetary reasons in 2-3 lines)
2. WHAT to do to improve (actionable steps in 2-3 lines)
3. WHEN it will get better (based on dasha timeline in 1-2 lines)

{self.get_concise_output_format()}

CRITICAL: Keep response to 3-4 lines per section. Focus on ROOT CAUSE via dasha (50% weight).
"""
    
    def _build_finding_guru_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Finding Guru question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "No specific guru indicators."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [4, 5, 9, 10])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Jupiter", "Ketu", "Sun"]
        )
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (Primary Timing Indicator - 50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

NOTE: Jupiter or Ketu dasha periods are highly favorable for guru connection.

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (Guru Indicators - 30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

Focus on:
• 4th House Lord → Foundation of learning
• 5th House Lord → Higher knowledge and wisdom
• 9th House Lord → Guru and spiritual teacher
• 10th House Lord → Karmic duty and life direction

═══════════════════════════════════════════════════════════════════
🌟 GURU-RELATED PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS FOR GURU CONNECTION
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 GURU INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
1. Analyze Jupiter (natural significator of guru/teacher)
2. Check 9th house lord and its strength
3. Evaluate Ketu (spiritual teachers, unconventional guides)
4. Consider current Jupiter transits
5. Assess readiness for guru based on dasha maturity
6. Predict WHEN guru will appear (via dasha timeline)

FOCUS AREAS:
- Current dasha connection to 9th house or Jupiter
- Jupiter's strength and position
- 9th house lord's dignity and placement
- Ketu's spiritual indicators
- Current Jupiter transit (timing for guru connection)

PROVIDE:
1. WILL they find a guru? (Yes/No with astrological reasoning in 2-3 lines)
2. WHEN will this happen? (Dasha-based timing in 1-2 lines)
3. WHAT TYPE of guru? (Traditional/unconventional based on chart in 1 line)

{self.get_concise_output_format()}

CRITICAL: Keep response to 3-4 lines per section. Answer if/when they'll find guru using dasha (50% weight).
"""
    
    def _build_spiritual_remedies_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build enhanced prompt for Spiritual Remedies question"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "Chart analysis for remedies."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [1, 5, 8, 9, 12])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, list(metadata.get("planet_strengths", {}).keys())[:6]
        )
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

NOTE: Remedies should be tailored to current dasha lord for maximum effectiveness.

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

═══════════════════════════════════════════════════════════════════
🌟 PLANET STRENGTHS & WEAKNESSES (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
📝 CHART ANALYSIS FOR REMEDIES
═══════════════════════════════════════════════════════════════════
{tech_points_text}

REMEDY INSTRUCTIONS:
1. Identify weak or afflicted planets affecting spiritual growth
2. Focus on current dasha lord's strength/weakness
3. Prioritize Moon (emotional healing), Jupiter (wisdom), Mercury (clarity)
4. Provide SPIRITUAL remedies (mantras, meditation, practices)
5. Suggest lifestyle adjustments for spiritual development
6. Keep remedies SIMPLE and PRACTICAL

FOCUS AREAS:
- Current dasha lord needing strengthening
- Weak planets in spiritual houses (5, 9, 12)
- Afflicted planets causing obstacles
- Spiritual practices aligned with chart
- Meditation and mantra recommendations

REMEDY CATEGORIES TO PROVIDE:
1. MANTRA/PRAYER: Specific to weak planet or dasha lord
2. MEDITATION: Type and timing based on chart
3. GEMSTONE/COLOR: Only if very weak planet needs urgent support
4. LIFESTYLE: Simple daily practices for spiritual growth
5. CHARITY/SERVICE: Based on afflicted houses

{self.get_concise_output_format()}

CRITICAL: 
- Keep response to 3-4 lines per section
- Provide SPECIFIC spiritual remedies, not generic advice
- Focus on current dasha lord (50% weight)
- Prioritize meditation, mantras, and spiritual practices
- Make remedies ACTIONABLE and SIMPLE
"""
    
    def _build_general_spiritual_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        metadata: Dict[str, Any],
        planet_details: Dict,
        transit_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build general enhanced spiritual analysis prompt"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = "\n".join(f"• {p}" for p in technical_points) if technical_points else "General spiritual analysis."
        
        language_instruction = self.get_language_instruction(language)
        
        dasha_section = self._format_dasha_section(metadata)
        house_lords_section = self._format_house_lords_section(metadata, [1, 5, 9, 12])
        planet_strengths_section = self._format_planet_strengths_section(
            metadata, ["Jupiter", "Moon", "Saturn", "Ketu"]
        )
        timing_section = self._format_timing_windows_section(metadata)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
📊 CURRENT DASHA PERIOD (50% Weight)
═══════════════════════════════════════════════════════════════════
{dasha_section}

═══════════════════════════════════════════════════════════════════
🏠 HOUSE LORDS ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_section}

═══════════════════════════════════════════════════════════════════
🌟 KEY PLANET STRENGTHS (20% Weight)
═══════════════════════════════════════════════════════════════════
{planet_strengths_section}

═══════════════════════════════════════════════════════════════════
⏱️ TIMING WINDOWS
═══════════════════════════════════════════════════════════════════
{timing_section}

═══════════════════════════════════════════════════════════════════
📝 TECHNICAL POINTS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

ANALYSIS INSTRUCTIONS:
Provide comprehensive spiritual guidance addressing the question using:
- Current dasha period and its spiritual significance (50% weight)
- House lord placements and dignity (30% weight)
- Planetary positions and strengths (20% weight)
- Current transits
- Spiritual perspective

{self.get_concise_output_format()}

CRITICAL: Keep response to 3-4 lines per section. Be concise and focused on dasha timing.
"""
    
    # ========== ENHANCED FORMATTING METHODS ==========
    
    def _format_dasha_section(self, metadata: Dict[str, Any]) -> str:
        """
        Format comprehensive dasha section with timeline.
        
        Includes:
        - Current Mahadasha and Antardasha
        - Dasha timeline (2Y past → 10Y future)
        - Spiritual significance of current dasha
        """
        current_dasha = metadata.get("current_dasha", None)
        dasha_timeline = metadata.get("dasha_timeline", None)
        
        if not current_dasha and not dasha_timeline:
            return "⚠️  Dasha data not available. Analysis will be based on natal chart only."
        
        output = []
        
        # Current Dasha
        if current_dasha:
            if isinstance(current_dasha, dict):
                maha = current_dasha.get("mahadasha", "Unknown")
                antar = current_dasha.get("antardasha", "Unknown")
                end_date = current_dasha.get("end_date", "Unknown")
                
                output.append(f"Current Mahadasha: {maha}")
                output.append(f"Current Antardasha: {antar}")
                output.append(f"Antardasha End: {end_date}")
            else:
                output.append(f"Current Dasha: {current_dasha}")
        
        # Dasha Timeline
        if dasha_timeline:
            output.append("\n📅 DASHA TIMELINE (2Y Past → 10Y Future):")
            output.append("─" * 50)
            
            if isinstance(dasha_timeline, list):
                for period in dasha_timeline[:15]:  # Limit to 15 periods
                    lord = period.get("lord", "Unknown")
                    start = period.get("start_date", "")
                    end = period.get("end_date", "")
                    level = period.get("level", "maha")
                    
                    if level == "maha":
                        output.append(f"  🔸 {lord} Mahadasha: {start} to {end}")
                    else:
                        output.append(f"    └─ {lord} Antardasha: {start} to {end}")
            else:
                output.append("  (Timeline format varies - see full data)")
        
        return "\n".join(output) if output else "Dasha information incomplete."
    
    def _format_house_lords_section(
        self, 
        metadata: Dict[str, Any], 
        relevant_houses: List[int]
    ) -> str:
        """
        Format house lords with dignity for relevant houses.
        
        Shows:
        - House number and sign
        - Lord planet
        - Lord's placement (house and sign)
        - Lord's dignity
        """
        house_lords = metadata.get("house_lords", {})
        
        if not house_lords:
            return "House lord data not available."
        
        output = []
        for house_num in sorted(relevant_houses):
            if house_num not in house_lords:
                continue
            
            info = house_lords[house_num]
            lord = info.get("lord", "Unknown")
            lord_house = info.get("lord_house", "?")
            lord_sign = info.get("lord_sign", "Unknown")
            dignity = info.get("dignity", "Neutral")
            is_retro = info.get("is_retrograde", False)
            
            retro_mark = " (R)" if is_retro else ""
            
            output.append(
                f"  • {house_num}th House → Lord: {lord}{retro_mark} "
                f"in {lord_house}th ({lord_sign}) - {dignity}"
            )
        
        return "\n".join(output) if output else "No house lord data for specified houses."
    
    def _format_planet_strengths_section(
        self,
        metadata: Dict[str, Any],
        planets: List[str]
    ) -> str:
        """
        Format planet strength indicators.
        
        Shows:
        - Planet position (house and sign)
        - Dignity
        - Key conditions (retrograde, combust, aspects)
        """
        planet_strengths = metadata.get("planet_strengths", {})
        
        if not planet_strengths:
            return "Planet strength data not available."
        
        output = []
        for planet_name in planets:
            if planet_name not in planet_strengths:
                continue
            
            info = planet_strengths[planet_name]
            house = info.get("house", "?")
            sign = info.get("sign", "Unknown")
            dignity = info.get("dignity", "Neutral")
            is_retro = info.get("is_retrograde", False)
            is_combust = info.get("is_combust", False)
            benefic_aspects = info.get("benefic_aspects", 0)
            malefic_aspects = info.get("malefic_aspects", 0)
            
            notes = []
            if is_retro:
                notes.append("R")
            if is_combust:
                notes.append("Combust")
            if benefic_aspects > 0:
                notes.append(f"+{benefic_aspects}B")
            if malefic_aspects > 0:
                notes.append(f"-{malefic_aspects}M")
            
            notes_str = f" [{', '.join(notes)}]" if notes else ""
            
            output.append(
                f"  • {planet_name}: {sign} in {house}th house - {dignity}{notes_str}"
            )
        
        return "\n".join(output) if output else "No strength data for specified planets."
    
    def _format_timing_windows_section(self, metadata: Dict[str, Any]) -> str:
        """
        Format timing windows (BEST and NEAREST).
        
        Shows:
        - Best timing windows (score >= 0.8)
        - Nearest timing windows (score >= 0.6)
        """
        timing_info = metadata.get("timing_windows", None)
        
        if not timing_info:
            return "No specific timing windows identified. Focus on dasha periods above."
        
        output = []
        
        # BEST windows
        best_windows = timing_info.get("best_windows", [])
        if best_windows:
            output.append("🌟 BEST TIMING WINDOWS:")
            for window in best_windows[:3]:  # Top 3
                start = window.get("start_date", "Unknown")
                end = window.get("end_date", "Unknown")
                desc = window.get("description", "Favorable period")
                score = window.get("score", 0)
                
                output.append(f"  • {start} to {end}: {desc} (Score: {score:.2f})")
        
        # NEAREST windows
        nearest_windows = timing_info.get("nearest_windows", [])
        if nearest_windows:
            output.append("\n📅 NEAREST FAVORABLE WINDOWS:")
            for window in nearest_windows[:3]:  # Top 3
                start = window.get("start_date", "Unknown")
                end = window.get("end_date", "Unknown")
                desc = window.get("description", "Moderately favorable")
                score = window.get("score", 0)
                
                output.append(f"  • {start} to {end}: {desc} (Score: {score:.2f})")
        
        return "\n".join(output) if output else "No timing windows available."
    
    def get_concise_output_format(self) -> str:
        """Get the CONCISE output format instruction"""
        return """
OUTPUT FORMAT (MUST FOLLOW EXACTLY - KEEP CONCISE):

GENERAL_ANSWER:
<3-4 lines maximum addressing the query directly. Be specific and actionable. Mention current dasha period if relevant.>

ASTROLOGICAL_ANALYSIS:
<3-4 lines maximum explaining the reasoning. Focus on:
 1. Current dasha lord's role (50% weight)
 2. Key house lords' influence (30% weight)
 3. Supporting planetary factors (20% weight)>

TIMING_INSIGHTS:
<2-3 lines on when things will improve or manifest based on dasha timeline.>

SUMMARY:
<1-2 lines summarizing the key takeaway with actionable next step.>

REMEDIES_ASTROLOGICAL:
- <Specific mantra/prayer for current dasha lord or weak planet>
- <Gemstone or ritual if needed (only for severely weak planets)>

REMEDIES_GENERAL:
- <First lifestyle practice aligned with spiritual growth>
- <Second mindset or meditation practice>

CRITICAL RULES:
1. Each section MUST be 3-4 lines maximum (NOT paragraphs)
2. ALWAYS mention dasha influence (50% weightage)
3. Be direct and concise
4. Avoid lengthy explanations
5. Provide actionable insights in minimal words
6. Focus on TIMING via dasha periods
"""
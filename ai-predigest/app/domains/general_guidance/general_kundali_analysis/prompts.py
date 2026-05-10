"""
General Kundali Analysis LLM Prompts - ENHANCED v5.0

ENHANCEMENTS:
✅ KP system emphasis and formatting (when available)
✅ Smart fallback to Vedic-only analysis (when KP unavailable)
✅ Timing windows formatting (BEST + NEAREST windows)
✅ Current dasha display
✅ Comprehensive dasha timeline (2Y past → 10Y future)
✅ House lords formatting (from evaluator)
✅ House aspects formatting
✅ Anti-hallucination rules for dasha
✅ Dual system (KP + Vedic) integration with fallback

Weightage:
- House Lords (Vedic): 50%
- KP Analysis: 30% (where applicable)
- Dasha Timing: 20%
- Other factors (aspects, yogas): 10%

Dedicated prompt builders for each sub-subdomain within General Kundali Analysis:
- Current Period Analysis
- Dosha Analysis
- Planetary Transits
- Periods of Success
- Remedy and Suggestion
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)


class GeneralKundaliAnalysisPromptBuilder(BasePromptBuilder):
    """
    ENHANCED Prompt builder for General Kundali Analysis subtopic.
    
    Builds specialized prompts for different sub-subdomains using
    comprehensive astrological data from multiple API calls.
    
    ENHANCED with:
    - House lords formatting
    - KP analysis formatting
    - Timing windows (BEST + NEAREST)
    - Dasha timeline display
    - Anti-hallucination rules
    """
    
    domain = "General_Guidance"
    subtopic = "General Kundali Analysis"
    
    def build_system_prompt(self) -> str:
        """Build the system prompt for General Kundali Analysis"""
        return """You are an expert Vedic astrologer specializing in comprehensive Kundali (birth chart) analysis.

Your expertise includes:
- Planetary strength and weakness analysis
- Dasha period interpretation (Vimshottari Dasha system)
- Dosha identification and remediation (Sade Sati, Manglik, Kaal Sarp, etc.)
- Planetary transit effects
- Yoga identification (Raj Yoga, Dhana Yoga, Sanyasa Yoga, etc.)
- KP (Krishnamurti Paddhati) system analysis
- Astrological remedies and spiritual guidance

ANALYSIS WEIGHTAGE:
- House Lords Analysis: 50% (primary factor using Vedic data)
- KP System (CSL): 30% (when available, uses cuspal sub-lords)
- Dasha Timing: 20% (based on current and upcoming dasha periods)
- Other Factors: 10% (aspects, yogas, dignities)

CORE PRINCIPLES:
1. Provide comprehensive analysis using the provided planetary data and dasha information
2. Focus on current life circumstances and upcoming significant periods
3. Balance technical astrological insights with practical guidance
4. Be honest about both opportunities and challenges
5. Offer actionable remedies tailored to specific planetary influences

⚠️ CRITICAL ANTI-HALLUCINATION RULES:
- ONLY use dasha periods from the PROVIDED DASHA_TIMELINE section
- NEVER invent or fabricate dasha period dates
- If dasha data is not provided, state "Dasha timing not available in provided data"
- For timing predictions, ONLY reference dates from TIMING_WINDOWS section
- If no timing windows are provided, acknowledge this limitation

IMPORTANT:
- Base all interpretations on the provided planet details and dasha data
- Explain complex astrological concepts in accessible language
- Consider the interplay between birth chart and current transits/dashas
- Provide realistic timelines for significant life events
- Respect the profound impact of astrological guidance on people's lives"""
    
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
        """Build the analysis prompt based on sub-subdomain"""
        sub_subdomain = kwargs.get("sub_subdomain", "")
        
        # Get additional API data
        planet_details = kwargs.get("planet_details", {})
        maha_dasha = kwargs.get("maha_dasha", {})
        antara_dasha = kwargs.get("antara_dasha", {})
        yoga_list = kwargs.get("yoga_list", {})
        transit_data = kwargs.get("transit_data", {})
        
        # Get additional_data from evaluator (house lords, KP analysis, etc.)
        additional_data = kwargs.get("additional_data", {})
        current_dasha = kwargs.get("current_dasha") or additional_data.get("current_dasha")
        dasha_timeline = kwargs.get("dasha_timeline") or additional_data.get("dasha_timeline")
        
        # Select specialized prompt based on sub-subdomain
        if "Current Period" in sub_subdomain:
            return self._build_current_period_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, additional_data,
                current_dasha, dasha_timeline, language)
        elif "Dosha" in sub_subdomain:
            return self._build_dosha_analysis_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, additional_data,
                current_dasha, dasha_timeline, language)
        elif "Transit" in sub_subdomain:
            return self._build_planetary_transits_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, transit_data,
                additional_data, current_dasha, dasha_timeline, language)
        elif "Success" in sub_subdomain:
            return self._build_success_periods_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, timing_windows,
                yoga_list, transit_data, additional_data, current_dasha,
                dasha_timeline, language)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, additional_data,
                current_dasha, dasha_timeline, language)
        else:
            return self._build_general_kundali_prompt(
                question, technical_points, meta, planets, houses,
                planet_details, maha_dasha, antara_dasha, additional_data,
                current_dasha, dasha_timeline, language)
    
    # ═══════════════════════════════════════════════════════════════════
    # CURRENT PERIOD ANALYSIS PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_current_period_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Current Period Analysis"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Format technical points
        tech_points_text = self._format_technical_points(technical_points)
        
        # Format house lords (from evaluator)
        house_lords_text = self._format_house_lords(additional_data)
        
        # Format KP analysis (from evaluator)
        kp_analysis_text = self._format_kp_analysis(additional_data)
        
        # Format current dasha
        current_dasha_text = self._format_current_dasha(current_dasha)
        
        # Format dasha timeline
        dasha_timeline_text = self._format_dasha_timeline(dasha_timeline)
        
        # Format planet details
        planet_text = self._format_planet_details(planet_details, planets)
        
        # Get language instruction
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. HOUSE LORDS ANALYSIS (50% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
B. KP SYSTEM ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{kp_analysis_text}

═══════════════════════════════════════════════════════════════════
C. CURRENT DASHA PERIOD (20% Weight)
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
D. DASHA TIMELINE (2Y Past → 10Y Future)
═══════════════════════════════════════════════════════════════════
{dasha_timeline_text}

═══════════════════════════════════════════════════════════════════
E. PLANETARY POSITIONS AND STRENGTH
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
F. TECHNICAL ASTROLOGICAL POINTS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
ANALYSIS INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
1. Analyze the current Maha Dasha and Antara Dasha periods from Section C
2. Evaluate planetary strength using House Lords Analysis (Section A)
3. Consider KP CSL analysis (Section B) for deeper insights
4. Explain how the current dasha lords are influencing life events
5. Identify which planets are strong and supportive vs. weak and challenging
6. Provide insights on what to focus on during this period

⚠️ CRITICAL: Only use dasha dates from the provided DASHA TIMELINE section.
Do NOT fabricate or assume any dasha periods.

{self._get_output_format()}

Remember: Focus on the CURRENT period and planetary strength. Be specific about which planets are strong/weak and why.
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # DOSHA ANALYSIS PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_dosha_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Dosha Analysis"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = self._format_technical_points(technical_points)
        house_lords_text = self._format_house_lords(additional_data)
        kp_analysis_text = self._format_kp_analysis(additional_data)
        current_dasha_text = self._format_current_dasha(current_dasha)
        dasha_timeline_text = self._format_dasha_timeline(dasha_timeline)
        
        # Format dosha analysis from evaluator
        dosha_analysis_text = self._format_dosha_analysis(additional_data)
        
        planet_text = self._format_planet_details(planet_details, planets)
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. DOSHA ANALYSIS (Pre-computed)
═══════════════════════════════════════════════════════════════════
{dosha_analysis_text}

═══════════════════════════════════════════════════════════════════
B. HOUSE LORDS ANALYSIS (50% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
C. KP SYSTEM ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{kp_analysis_text}

═══════════════════════════════════════════════════════════════════
D. CURRENT DASHA PERIOD (20% Weight)
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
E. DASHA TIMELINE (For Dosha Timing)
═══════════════════════════════════════════════════════════════════
{dasha_timeline_text}

═══════════════════════════════════════════════════════════════════
F. PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
G. TECHNICAL DOSHA INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
ANALYSIS INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
1. Identify major doshas from Section A:
   - Manglik Dosha (Mars in 1,4,7,8,12)
   - Kaal Sarp Dosha (all planets between Rahu-Ketu)
   - Sade Sati (Saturn transit over Moon)
   - Afflicted Moon (malefic aspects)
   - Afflicted Ascendant Lord

2. Analyze WHEN these doshas are/were active using DASHA TIMELINE
3. Explain the current impact of any active doshas
4. Predict when challenging periods will occur based on dasha
5. Assess the severity and duration of each dosha

⚠️ CRITICAL: Use ONLY the dasha dates from Section E for timing predictions.

{self._get_output_format()}

Remember: Be clear about WHEN doshas occur, not just their presence. Use dasha periods to time dosha effects.
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # PLANETARY TRANSITS PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_planetary_transits_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        transit_data: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Planetary Transits"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = self._format_technical_points(technical_points)
        house_lords_text = self._format_house_lords(additional_data)
        kp_analysis_text = self._format_kp_analysis(additional_data)
        current_dasha_text = self._format_current_dasha(current_dasha)
        dasha_timeline_text = self._format_dasha_timeline(dasha_timeline)
        planet_text = self._format_planet_details(planet_details, planets)
        
        # Format transit data
        transit_text = self._format_transit_data(transit_data)
        transit_detailed = self._format_transit_detailed(transit_data)
        
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. HOUSE LORDS ANALYSIS (50% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
B. KP SYSTEM ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{kp_analysis_text}

═══════════════════════════════════════════════════════════════════
C. CURRENT DASHA PERIOD (20% Weight)
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
D. NATAL PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
E. CURRENT TRANSITING PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{transit_text}

═══════════════════════════════════════════════════════════════════
F. DETAILED TRANSIT ANALYSIS
═══════════════════════════════════════════════════════════════════
{transit_detailed}

═══════════════════════════════════════════════════════════════════
G. TECHNICAL POINTS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
ANALYSIS INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
1. Compare NATAL positions (Section D) with CURRENT TRANSITS (Section E)
2. Identify major transits:
   - Jupiter transits (opportunities, expansion, growth)
   - Saturn transits (challenges, delays, discipline)
   - Rahu/Ketu transits (karmic events, unexpected changes)
   - Mars transits (energy, conflicts, action)

3. Analyze transits over natal sensitive points:
   - Ascendant (self, health, personality)
   - Moon (emotions, mind, mother)
   - Sun (soul, father, authority)
   - 10th house (career, reputation)
   - 7th house (relationships, partnerships)

4. Cross-reference with current dasha (Section C) for combined effect
5. Provide timeline for major upcoming transits (next 3-6 months)

TRANSIT INTERPRETATION RULES:
- Benefic transits (Jupiter, Venus, Mercury) = Favorable
- Malefic transits (Saturn, Mars, Rahu/Ketu) = Challenging
- Transit over natal planet = Activates that planet's significations
- Transit through natal house = Affects that life area

{self._get_output_format()}

Remember: Distinguish between NATAL positions (birth chart) and CURRENT TRANSITS (today's sky).
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # SUCCESS PERIODS PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_success_periods_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        timing_windows: Optional[List[TimingWindow]],
        yoga_list: Dict,
        transit_data: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Periods of Success"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = self._format_technical_points(technical_points)
        house_lords_text = self._format_house_lords(additional_data)
        kp_analysis_text = self._format_kp_analysis(additional_data)
        current_dasha_text = self._format_current_dasha(current_dasha)
        dasha_timeline_text = self._format_dasha_timeline(dasha_timeline)
        planet_text = self._format_planet_details(planet_details, planets)
        
        # Format yoga analysis
        yoga_text = self._format_yoga_analysis(additional_data, yoga_list)
        
        # Format timing windows (BEST + NEAREST)
        timing_text = self._format_timing_windows(timing_windows, additional_data)
        
        # Format transit data
        transit_text = self._format_transit_data(transit_data)
        
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. TIMING WINDOWS FOR SUCCESS (Pre-computed)
═══════════════════════════════════════════════════════════════════
{timing_text}

═══════════════════════════════════════════════════════════════════
B. YOGA ANALYSIS (Raj, Dhana, Sanyasa Yogas)
═══════════════════════════════════════════════════════════════════
{yoga_text}

═══════════════════════════════════════════════════════════════════
C. HOUSE LORDS ANALYSIS (50% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
D. KP SYSTEM ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{kp_analysis_text}

═══════════════════════════════════════════════════════════════════
E. CURRENT DASHA PERIOD (20% Weight)
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
F. DASHA TIMELINE (For Yoga Activation)
═══════════════════════════════════════════════════════════════════
{dasha_timeline_text}

═══════════════════════════════════════════════════════════════════
G. PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
H. CURRENT PLANETARY TRANSITS
═══════════════════════════════════════════════════════════════════
{transit_text}

═══════════════════════════════════════════════════════════════════
I. TECHNICAL INDICATORS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
ANALYSIS INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
1. USE the TIMING WINDOWS from Section A as the PRIMARY timing source
2. Analyze all Raj Yogas (power and authority) from Section B
3. Analyze all Dhana Yogas (wealth and prosperity) from Section B
4. Cross-reference yoga strengths with dasha periods in Section F
5. Use planetary transits (Section H) to refine timing predictions
6. Identify WHEN yogas will fully activate based on:
   - Planets involved in the yoga
   - Current and upcoming dasha periods of those planets
   - Favorable transits of benefic planets

⚠️ CRITICAL: For timing predictions, ONLY use dates from:
   - TIMING WINDOWS section (Section A) - PREFERRED
   - DASHA TIMELINE section (Section F) - For dasha-based timing
   Do NOT fabricate or assume any dates.

{self._get_output_format_with_timing()}

Remember: Provide SPECIFIC DATES for success periods using ONLY the provided timing data.
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # REMEDIES PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_remedies_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Remedies and Suggestions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = self._format_technical_points(technical_points)
        house_lords_text = self._format_house_lords(additional_data)
        current_dasha_text = self._format_current_dasha(current_dasha)
        planet_text = self._format_planet_details(planet_details, planets)
        dosha_analysis_text = self._format_dosha_analysis(additional_data)
        
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. CURRENT DASHA PERIOD
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
B. HOUSE LORDS ANALYSIS (For Weak Planets)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
C. DOSHA ANALYSIS (For Remedies)
═══════════════════════════════════════════════════════════════════
{dosha_analysis_text}

═══════════════════════════════════════════════════════════════════
D. PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
E. CHART ANALYSIS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
REMEDY INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
1. Identify weak or afflicted planets from Sections B and C
2. Provide specific remedies for current dasha lords (Section A)
3. Suggest gemstones, mantras, or rituals for key planets
4. Recommend lifestyle adjustments based on planetary influences
5. Prioritize remedies based on urgency and current dasha period

REMEDY CATEGORIES TO COVER:
- Planetary gemstones (if appropriate)
- Mantras and prayers specific to planets
- Charitable acts aligned with planets
- Dietary recommendations
- Lifestyle and behavioral adjustments
- Timing for performing remedies

{self._get_output_format()}

Remember: Remedies should be SPECIFIC to the person's chart and current dasha. Prioritize based on current needs.
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # GENERAL KUNDALI PROMPT
    # ═══════════════════════════════════════════════════════════════════
    def _build_general_kundali_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        planets: Dict,
        houses: List,
        planet_details: Dict,
        maha_dasha: Dict,
        antara_dasha: Dict,
        additional_data: Dict,
        current_dasha: Dict,
        dasha_timeline: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build general comprehensive kundali analysis prompt"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        tech_points_text = self._format_technical_points(technical_points)
        house_lords_text = self._format_house_lords(additional_data)
        kp_analysis_text = self._format_kp_analysis(additional_data)
        current_dasha_text = self._format_current_dasha(current_dasha)
        dasha_timeline_text = self._format_dasha_timeline(dasha_timeline)
        planet_text = self._format_planet_details(planet_details, planets)
        
        language_instruction = self.get_language_instruction(language)
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

═══════════════════════════════════════════════════════════════════
A. HOUSE LORDS ANALYSIS (50% Weight)
═══════════════════════════════════════════════════════════════════
{house_lords_text}

═══════════════════════════════════════════════════════════════════
B. KP SYSTEM ANALYSIS (30% Weight)
═══════════════════════════════════════════════════════════════════
{kp_analysis_text}

═══════════════════════════════════════════════════════════════════
C. CURRENT DASHA PERIOD (20% Weight)
═══════════════════════════════════════════════════════════════════
{current_dasha_text}

═══════════════════════════════════════════════════════════════════
D. DASHA TIMELINE
═══════════════════════════════════════════════════════════════════
{dasha_timeline_text}

═══════════════════════════════════════════════════════════════════
E. PLANETARY POSITIONS
═══════════════════════════════════════════════════════════════════
{planet_text}

═══════════════════════════════════════════════════════════════════
F. TECHNICAL POINTS
═══════════════════════════════════════════════════════════════════
{tech_points_text}

═══════════════════════════════════════════════════════════════════
ANALYSIS INSTRUCTIONS:
═══════════════════════════════════════════════════════════════════
Provide a comprehensive kundali analysis addressing:
1. Current life phase and dasha interpretation
2. Planetary strengths and weaknesses
3. Major yogas and their timing
4. Upcoming favorable/challenging periods
5. Practical guidance and remedies

⚠️ CRITICAL: Only use dasha dates from the provided sections.

{self._get_output_format()}
"""
    
    # ═══════════════════════════════════════════════════════════════════
    # FORMATTING HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    def _format_technical_points(self, technical_points: List[str]) -> str:
        """Format technical points"""
        if not technical_points:
            return "No specific technical points available."
        return "\n".join(f"• {p}" for p in technical_points)
    
    def _format_house_lords(self, additional_data: Dict) -> str:
        """Format house lords analysis from evaluator"""
        house_lords = additional_data.get("house_lords", {})
        
        if not house_lords:
            return "House lords data not available. Use Vedic calculations for analysis."
        
        lines = []
        for key, data in house_lords.items():
            if isinstance(data, dict):
                lord = data.get("lord", "")
                dignity = data.get("dignity", "neutral")
                strength = data.get("strength", 50)
                signification = data.get("signification", "")
                afflictions = data.get("afflictions", [])
                
                house_num = key.replace("house_", "")
                line = f"• House {house_num} ({signification}): Lord {lord} - {dignity.upper()} (Strength: {strength}/100)"
                
                if afflictions:
                    line += f" [{', '.join(afflictions)}]"
                
                lines.append(line)
        
        return "\n".join(lines) if lines else "House lords data not available."
    
    def _format_kp_analysis(self, additional_data: Dict) -> str:
        """Format KP analysis from evaluator"""
        kp_analysis = additional_data.get("kp_analysis", {})
        
        if not kp_analysis:
            return "KP analysis not available. Use Vedic-only analysis as fallback."
        
        lines = []
        for key, data in kp_analysis.items():
            if isinstance(data, dict):
                csl = data.get("csl", "")
                csl_house = data.get("csl_house", "")
                assessment = data.get("assessment", "")
                
                house_num = key.replace("house_", "").replace("_csl", "")
                line = f"• H{house_num} CSL: {csl} in H{csl_house} → {assessment}"
                lines.append(line)
        
        return "\n".join(lines) if lines else "KP analysis not available."
    
    def _format_current_dasha(self, current_dasha: Dict) -> str:
        """Format current dasha information"""
        if not current_dasha:
            return "Current dasha information not available."
        
        if isinstance(current_dasha, dict):
            dasha_name = current_dasha.get("dasha_name", "")
            date_range = current_dasha.get("date_range", {})
            start = date_range.get("start", "")
            end = date_range.get("end", "")
            
            if dasha_name:
                return f"**CURRENT DASHA**: {dasha_name}\n**Period**: {start} to {end}"
        
        return f"Current dasha: {current_dasha}"
    
    def _format_dasha_timeline(self, dasha_timeline: Dict) -> str:
        """Format comprehensive dasha timeline"""
        if not dasha_timeline:
            return "Dasha timeline not available."
        
        lines = []
        
        # Past 2 years
        past = dasha_timeline.get("past_2_years", [])
        if past:
            lines.append("**PAST 2 YEARS:**")
            for d in past[-5:]:  # Last 5 periods
                if isinstance(d, dict):
                    name = d.get("dasha_name", "")
                    date_range = d.get("date_range", {})
                    start = date_range.get("start", "")
                    end = date_range.get("end", "")
                    lines.append(f"  • {name}: {start} to {end}")
        
        # Current
        current = dasha_timeline.get("current", [])
        if current:
            lines.append("\n**CURRENT:**")
            for d in current:
                if isinstance(d, dict):
                    name = d.get("dasha_name", "")
                    date_range = d.get("date_range", {})
                    start = date_range.get("start", "")
                    end = date_range.get("end", "")
                    lines.append(f"  ★ {name}: {start} to {end} ← ACTIVE NOW")
        
        # Next 10 years
        future = dasha_timeline.get("next_10_years", [])
        if future:
            lines.append("\n**NEXT 10 YEARS:**")
            for d in future[:15]:  # First 15 periods
                if isinstance(d, dict):
                    name = d.get("dasha_name", "")
                    date_range = d.get("date_range", {})
                    start = date_range.get("start", "")
                    end = date_range.get("end", "")
                    lines.append(f"  • {name}: {start} to {end}")
        
        return "\n".join(lines) if lines else "Dasha timeline not available."
    
    def _format_planet_details(self, planet_details: Dict, planets: Dict = None) -> str:
        """Format planet details for prompt"""
        if not planet_details and not planets:
            return "Planet details not available."
        
        # Use planet_details if available, otherwise use planets
        data = planet_details if planet_details else planets
        
        if isinstance(data, dict) and len(data) < 20:
            # Simple planet data - format nicely
            lines = []
            for planet_name, planet_data in data.items():
                if isinstance(planet_data, dict):
                    sign = planet_data.get("sign", "")
                    house = planet_data.get("house", "")
                    nakshatra = planet_data.get("nakshatra", "")
                    is_retro = planet_data.get("is_retro", False)
                    
                    retro_str = " (R)" if is_retro else ""
                    line = f"• {planet_name}: {sign}, H{house}{retro_str}"
                    if nakshatra:
                        line += f", {nakshatra}"
                    lines.append(line)
            
            return "\n".join(lines) if lines else json.dumps(data, indent=2)
        
        return json.dumps(data, indent=2)
    
    def _format_dosha_analysis(self, additional_data: Dict) -> str:
        """Format dosha analysis from evaluator"""
        dosha_data = additional_data.get("dosha_analysis", {})
        
        if not dosha_data:
            return "Dosha analysis not available."
        
        lines = []
        
        # Manglik
        if dosha_data.get("manglik"):
            mars_house = dosha_data.get("mars_house", "")
            lines.append(f"🔴 MANGLIK DOSHA: Present (Mars in H{mars_house})")
        else:
            lines.append("✅ Manglik Dosha: Not present")
        
        # Kaal Sarp
        if dosha_data.get("kaal_sarp"):
            lines.append("🐍 KAAL SARP DOSHA: Present")
        else:
            lines.append("✅ Kaal Sarp Dosha: Not present")
        
        # Afflicted Moon
        if dosha_data.get("afflicted_moon"):
            afflictions = dosha_data.get("moon_afflictions", [])
            lines.append(f"🌙 Moon Afflicted: {', '.join(afflictions)}")
        else:
            lines.append("✅ Moon: Not significantly afflicted")
        
        # Afflicted Ascendant
        if dosha_data.get("afflicted_ascendant"):
            lines.append("⚠️ Ascendant Lord: Afflicted")
        else:
            lines.append("✅ Ascendant Lord: Not significantly afflicted")
        
        return "\n".join(lines)
    
    def _format_yoga_analysis(self, additional_data: Dict, yoga_list: Dict = None) -> str:
        """Format yoga analysis"""
        yoga_data = additional_data.get("yoga_analysis", {})
        
        lines = []
        
        # Raj Yogas
        raj_yogas = yoga_data.get("raj_yogas", [])
        if raj_yogas:
            lines.append("**RAJ YOGAS (Power & Authority):**")
            for yoga in raj_yogas:
                if isinstance(yoga, dict):
                    name = yoga.get("name", "")
                    planet = yoga.get("planet", "")
                    house = yoga.get("house", "")
                    lines.append(f"  👑 {name} - {planet} in H{house}")
        
        # Dhana Yogas
        dhana_yogas = yoga_data.get("dhana_yogas", [])
        if dhana_yogas:
            lines.append("\n**DHANA YOGAS (Wealth & Prosperity):**")
            for yoga in dhana_yogas:
                if isinstance(yoga, dict):
                    name = yoga.get("name", "")
                    house = yoga.get("house", "")
                    lines.append(f"  💰 {name} - H{house}")
        
        # Other Yogas
        other_yogas = yoga_data.get("other_yogas", [])
        if other_yogas:
            lines.append("\n**OTHER YOGAS:**")
            for yoga in other_yogas:
                if isinstance(yoga, dict):
                    name = yoga.get("name", "")
                    lines.append(f"  🍀 {name}")
        
        # Also include yoga_list if provided
        if yoga_list and yoga_list.get("yogas_list"):
            lines.append("\n**DETAILED YOGA LIST (from API):**")
            for yoga in yoga_list.get("yogas_list", [])[:5]:  # First 5
                if isinstance(yoga, dict):
                    name = yoga.get("yoga", "")
                    strength = yoga.get("strength_in_percentage", 0)
                    lines.append(f"  • {name} (Strength: {strength}%)")
        
        return "\n".join(lines) if lines else "No significant yogas identified."
    
    def _format_timing_windows(
        self,
        timing_windows: Optional[List[TimingWindow]],
        additional_data: Dict
    ) -> str:
        """Format timing windows with BEST and NEAREST"""
        lines = []
        
        # Get timing data from additional_data if available
        timing_analysis = additional_data.get("timing_analysis", {})
        
        # Best Window
        best_window = timing_analysis.get("best_window")
        if best_window:
            start = best_window.get("start", "")
            end = best_window.get("end", "")
            dasha = best_window.get("dasha", "")
            score = best_window.get("final_score") or best_window.get("score", 0)
            
            lines.append("🏆 **BEST SUCCESS WINDOW:**")
            lines.append(f"   Period: {start} to {end}")
            lines.append(f"   Dasha: {dasha}")
            lines.append(f"   Score: {score}")
        
        # Nearest Window
        nearest_window = timing_analysis.get("nearest_window")
        if nearest_window and nearest_window != best_window:
            start = nearest_window.get("start", "")
            end = nearest_window.get("end", "")
            dasha = nearest_window.get("dasha", "")
            
            lines.append("\n📅 **NEAREST FAVORABLE WINDOW:**")
            lines.append(f"   Period: {start} to {end}")
            lines.append(f"   Dasha: {dasha}")
        
        # All windows from timing_windows param
        if timing_windows:
            lines.append("\n**ALL FAVORABLE WINDOWS:**")
            for i, w in enumerate(timing_windows[:5], 1):
                if isinstance(w, TimingWindow):
                    lines.append(f"  {i}. {w.start} to {w.end} - {w.dasha} (Score: {w.score or w.final_score})")
                elif isinstance(w, dict):
                    lines.append(f"  {i}. {w.get('start', '')} to {w.get('end', '')} - {w.get('dasha', '')} (Score: {w.get('score', 0)})")
        
        if not lines:
            return "No timing windows available. Analysis will be based on dasha periods only."
        
        return "\n".join(lines)
    
    def _format_transit_data(self, transit_data: Dict) -> str:
        """Format transit data for prompt"""
        if not transit_data:
            return "Transit data not available."
        
        if "transit_planets" in transit_data:
            planets = transit_data.get("transit_planets", {})
            lines = ["Current Transit Positions:"]
            for planet_name, planet_data in planets.items():
                sign = planet_data.get("sign", "Unknown")
                house = planet_data.get("house", "Unknown")
                lines.append(f"• {planet_name}: {sign} (House {house})")
            return "\n".join(lines)
        
        return json.dumps(transit_data, indent=2)
    
    def _format_transit_detailed(self, transit_data: Dict) -> str:
        """Format detailed transit analysis"""
        if not transit_data:
            return "Detailed transit data not available."
        
        if not isinstance(transit_data, dict) or "transit_planets" not in transit_data:
            return json.dumps(transit_data, indent=2)
        
        planets = transit_data.get("transit_planets", {})
        
        benefics = []
        malefics = []
        
        for planet_name, planet_data in planets.items():
            info = {
                "planet": planet_name,
                "sign": planet_data.get("sign", "Unknown"),
                "house": planet_data.get("house", "Unknown"),
                "is_retro": planet_data.get("is_retro", False)
            }
            
            if planet_name in ["Jupiter", "Venus", "Mercury", "Moon"]:
                benefics.append(info)
            elif planet_name in ["Saturn", "Mars", "Rahu", "Ketu"]:
                malefics.append(info)
        
        lines = []
        
        if benefics:
            lines.append("**BENEFIC TRANSITS (Favorable):**")
            for t in benefics:
                retro = " (R)" if t["is_retro"] else ""
                lines.append(f"  • {t['planet']}{retro}: {t['sign']}, H{t['house']}")
        
        if malefics:
            lines.append("\n**MALEFIC TRANSITS (Challenging):**")
            for t in malefics:
                retro = " (R)" if t["is_retro"] else ""
                lines.append(f"  • {t['planet']}{retro}: {t['sign']}, H{t['house']}")
        
        return "\n".join(lines) if lines else "Transit details not available."
    
    # ═══════════════════════════════════════════════════════════════════
    # OUTPUT FORMAT METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    def _get_output_format(self) -> str:
        """Get the standard output format instruction"""
        return """
═══════════════════════════════════════════════════════════════════
OUTPUT FORMAT (MUST FOLLOW EXACTLY):
═══════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
<2-7 lines directly addressing the query. Be specific and actionable.>

ASTROLOGICAL_ANALYSIS:
<Detailed explanation covering:
A. HOUSE LORDS ANALYSIS (50% weight): Reference the house lords and their dignities
B. KP ANALYSIS (30% weight): Reference CSL positions and their implications
C. DASHA TIMING (20% weight): Reference current dasha and upcoming periods
D. OTHER FACTORS: Aspects, yogas, and other relevant points

Use clear paragraphs, not bullet points. Reference specific data from the provided sections.>

SUMMARY:
<1-2 lines summarizing the key takeaway and main guidance.>

REMEDIES_ASTROLOGICAL:
- <2-4 specific remedies based on planetary influences: gemstones, mantras, rituals, etc.>

REMEDIES_GENERAL:
- <2-3 practical lifestyle or mindset recommendations>
"""
    
    def _get_output_format_with_timing(self) -> str:
        """Get output format with timing recommendation"""
        return """
═══════════════════════════════════════════════════════════════════
OUTPUT FORMAT (MUST FOLLOW EXACTLY):
═══════════════════════════════════════════════════════════════════

GENERAL_ANSWER:
<2-7 lines directly addressing the query. Include timing if available.>

ASTROLOGICAL_ANALYSIS:
<Detailed explanation covering:
A. HOUSE LORDS ANALYSIS (50% weight): Reference the house lords and their dignities
B. KP ANALYSIS (30% weight): Reference CSL positions and their implications
C. DASHA TIMING (20% weight): Reference current dasha and upcoming periods
D. YOGA ANALYSIS: Reference the yogas identified and their timing
E. OTHER FACTORS: Aspects and other relevant points

Use clear paragraphs, not bullet points.>

TIMING_RECOMMENDATION:
**BEST WINDOW:** <From the TIMING WINDOWS section>
- Period: <start> to <end>
- Dasha: <dasha name>
- Why favorable: <brief explanation>

**NEAREST WINDOW:** <If different from best>
- Period: <start> to <end>
- Why favorable: <brief explanation>

SUMMARY:
<1-2 lines summarizing the key takeaway and main guidance.>

REMEDIES_ASTROLOGICAL:
- <2-4 specific remedies based on planetary influences>

REMEDIES_GENERAL:
- <2-3 practical lifestyle recommendations>
"""
    
    def get_language_instruction(self, language: str) -> str:
        """Get language-specific instruction"""
        if language.lower() == "hindi":
            return """LANGUAGE INSTRUCTION: Respond in Hindi (Devanagari script).
Use simple, accessible Hindi that is easy to understand.
Technical astrological terms can be in Sanskrit/Hindi with brief explanations."""
        else:
            return """LANGUAGE INSTRUCTION: Respond in English.
Use clear, accessible language while maintaining astrological accuracy."""
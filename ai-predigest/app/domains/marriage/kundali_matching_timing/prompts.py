"""
Kundali Matching and Timing LLM Prompts

Dedicated prompt builders for each sub-subdomain:
- Ashtakoot Milan
- Marriage Advise
- Compatibility Analysis
- Remedy and Suggestion

Integrates with kundali_milan API data for comprehensive analysis.
UPDATED: Fixed timing window formatting and added two-person overlap support
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)


class KundaliMatchingTimingPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Kundali Matching and Timing subtopic.
    
    Works with kundali_milan API data to provide comprehensive matching analysis.
    """
    
    domain = "Marriage"
    subtopic = "Kundali Matching Timing"
    
    def build_system_prompt(self) -> str:
        """Build the system prompt for Kundali Matching analysis"""
        return """You are an expert Vedic astrologer specializing in kundali matching and marriage compatibility analysis.

Your expertise includes:
- Ashtakoot (8-point) compatibility system analysis
- Dosha identification and remediation (Manglik, Nadi, Bhakoot, Shadashtak, Pitra)
- Multi-dimensional compatibility assessment
- Marriage timing and muhurat selection
- Remedial measures for marital harmony

CORE PRINCIPLES:
1. Base all analysis on provided kundali milan data
2. Consider both individual charts and combined compatibility
3. Be honest about challenges while offering hope through remedies
4. Provide specific, actionable remedies
5. Respect the significance of marriage decisions

IMPORTANT:
- Use actual scores from ashtakoot system
- Identify specific doshas present in the match
- Provide timing based on dasha periods of both partners
- Offer comprehensive remedies for identified issues"""
    
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
        
        # Get kundali milan data from kwargs
        kundali_milan_data = kwargs.get("kundali_milan_data", {})
        compatibility_data = kwargs.get("compatibility_data", {})
        
        # DEBUG: Log what we received
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"=== PROMPT BUILDER DEBUG ===")
        logger.info(f"Sub-subdomain: {sub_subdomain}")
        logger.info(f"Kundali milan data present: {bool(kundali_milan_data)}")
        logger.info(f"Timing windows count: {len(timing_windows) if timing_windows else 0}")
        if timing_windows:
            first = timing_windows[0]
            logger.info(f"First timing window type: {type(first)}")
            if hasattr(first, '__dict__'):
                logger.info(f"First timing window: {first.__dict__}")
            elif isinstance(first, dict):
                logger.info(f"First timing window: {first}")
        logger.info(f"=== END DEBUG ===")
        
        # Select specialized prompt based on sub-subdomain
        if "Ashtakoot" in sub_subdomain:
            return self._build_ashtakoot_milan_prompt(
                question, technical_points, meta, kundali_milan_data, language)
        elif "Advise" in sub_subdomain or "Advice" in sub_subdomain:
            return self._build_marriage_advice_prompt(
                question, technical_points, meta, kundali_milan_data, timing_windows, language)
        elif "Compatibility" in sub_subdomain:
            return self._build_compatibility_analysis_prompt(
                question, technical_points, meta, kundali_milan_data, compatibility_data, language)
        elif "Remed" in sub_subdomain:
            return self._build_remedies_prompt(
                question, technical_points, meta, kundali_milan_data, language)
        else:
            return self._build_general_matching_prompt(
                question, technical_points, meta, kundali_milan_data, language)
    
    def _build_ashtakoot_milan_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        kundali_milan_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Ashtakoot Milan analysis"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Extract ashtakoot data
        ashtakoot_text = self._format_ashtakoot_data(kundali_milan_data)
        dosha_text = self._format_dosha_data(kundali_milan_data)
        astro_details_text = self._format_astro_details(kundali_milan_data)
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

ASHTAKOOT (8-POINT) COMPATIBILITY SYSTEM:
{ashtakoot_text}

DOSHA ANALYSIS:
{dosha_text}

ASTROLOGICAL DETAILS:
{astro_details_text}

ANALYSIS INSTRUCTIONS:
1. Provide detailed commentary on each of the 8 kootas:
   - Varna (work compatibility)
   - Vasya (attraction and control)
   - Tara (destiny and fortune)
   - Yoni (physical/sexual compatibility)
   - Graha Maitri (friendship and mental compatibility)
   - Gana (temperament)
   - Bhakoot/Rasi (relationship harmony)
   - Nadi (health and progeny)

2. Analyze the TOTAL SCORE out of 36:
   - 18-24 points: Average match
   - 24-32 points: Good match
   - 32-36 points: Excellent match
   - Below 18: Challenging match (requires strong remedies)

3. Identify and explain ALL doshas:
   - Manglik Dosha (if present in either chart)
   - Nadi Dosha (if nadi score is 0)
   - Bhakoot Dosha (if bhakoot score is 0)
   - Shadashtak Dosha

4. Provide overall compatibility verdict

{self.get_output_format()}

CRITICAL: Base analysis on ACTUAL SCORES provided. Be specific about which kootas are strong/weak.
If total score is low, acknowledge challenges honestly but offer hope through remedies.
"""
    
    def _build_marriage_advice_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        kundali_milan_data: Dict,
        timing_windows: Optional[List[TimingWindow]],
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Marriage Advice - FIXED with proper timing window handling"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        ashtakoot_text = self._format_ashtakoot_data(kundali_milan_data)
        dosha_text = self._format_dosha_data(kundali_milan_data)
        dasha_text = self._format_dasha_periods(kundali_milan_data)
        
        # ✅ FIXED: Properly format timing windows
        timing_text = ""
        is_overlap = False
        
        if timing_windows:
            # Check if these are overlapping (two-person) windows
            first = timing_windows[0] if timing_windows else None
            
            # Handle both TimingWindow objects and dicts
            if first:
                if hasattr(first, '__dict__'):
                    first_dict = first.__dict__
                elif isinstance(first, dict):
                    first_dict = first
                else:
                    first_dict = {}
                
                is_overlap = first_dict.get("is_two_person_overlap", False)
            
            if is_overlap:
                # ✅ NEW: Format for two-person overlapping windows
                timing_text = "\n\nOVERLAPPING FAVORABLE MARRIAGE PERIODS (Both Charts):\n"
                timing_text += "=" * 60 + "\n"
                
                for i, window in enumerate(timing_windows[:5], 1):
                    # Handle both TimingWindow objects and dicts
                    if hasattr(window, '__dict__'):
                        w = window.__dict__
                    elif isinstance(window, dict):
                        w = window
                    else:
                        continue
                    
                    start = w.get('start', 'N/A')
                    end = w.get('end', 'N/A')
                    overlap_days = w.get('overlap_days', 'N/A')
                    quality = w.get('quality', 'N/A')
                    combined_score = w.get('final_score') or w.get('combined_score') or w.get('score', 'N/A')
                    person1_dasha = w.get('person1_dasha') or w.get('dasha', 'N/A')
                    person2_dasha = w.get('person2_dasha', 'N/A')
                    person1_score = w.get('person1_score', 'N/A')
                    person2_score = w.get('person2_score', 'N/A')
                    
                    timing_text += f"\n{i}. **{start} to {end}** ({overlap_days} days overlap)\n"
                    timing_text += f"   Quality: {quality} | Combined Score: {combined_score}\n"
                    timing_text += f"   Boy's Dasha: {person1_dasha} (Score: {person1_score})\n"
                    timing_text += f"   Girl's Dasha: {person2_dasha} (Score: {person2_score})\n"
            else:
                # ✅ FIXED: Format for single-person timing windows
                timing_text = "\n\nFAVORABLE MARRIAGE PERIODS:\n"
                
                for i, window in enumerate(timing_windows[:5], 1):
                    # Handle both TimingWindow objects and dicts
                    if hasattr(window, 'start'):
                        # TimingWindow object - access attributes directly
                        start = window.start
                        end = window.end
                        dasha = window.dasha
                        score = window.final_score or window.score
                    elif isinstance(window, dict):
                        # Dict format
                        start = window.get('start', 'N/A')
                        end = window.get('end', 'N/A')
                        dasha = window.get('dasha', 'N/A')
                        score = window.get('final_score') or window.get('score', 'N/A')
                    else:
                        continue
                    
                    timing_text += f"{i}. {start} to {end} - {dasha} (Score: {score})\n"
        
        # Get language instruction for Hindi/English output
        language_instruction = self.get_language_instruction(language)
        
        # ✅ NEW: Different instructions based on whether we have overlap data
        if is_overlap:
            timing_instruction = """
3. BEST MARRIAGE PERIOD (MUHURAT):
   - The OVERLAPPING FAVORABLE PERIODS above show times when BOTH charts are favorable
   - These periods represent OPTIMAL windows where both partners' dasha periods align favorably
   - Prioritize periods with "Excellent" quality and highest combined scores
   - Explain why these specific periods work well for both partners
   - Consider the overlap duration - longer overlaps provide more flexibility
"""
        else:
            timing_instruction = """
3. BEST MARRIAGE PERIOD (MUHURAT):
   - Analyze favorable dasha combinations from the periods listed
   - Consider Jupiter and Venus transits
   - Suggest specific time periods (months/years)
   - Avoid malefic dasha periods
"""
        
        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

ASHTAKOOT SCORE:
{ashtakoot_text}

DOSHA STATUS:
{dosha_text}

DASHA PERIODS (Both Partners):
{dasha_text}
{timing_text}

ANALYSIS INSTRUCTIONS:
1. MARRIAGE RECOMMENDATION:
   - Can this marriage be advised? (Yes/No/With Remedies)
   - Base decision on:
     * Total ashtakoot score
     * Severity of doshas present
     * Overall compatibility indicators

2. DELAY ANALYSIS:
   - Identify reasons for any potential delays:
     * Manglik dosha in either chart
     * Saturn's placement and transits
     * 7th house afflictions
     * Unfavorable dasha periods
{timing_instruction}
4. REMEDIAL REQUIREMENTS:
   - If remedies are essential, state clearly
   - Indicate severity level (mild/moderate/strong remedies needed)

{self.get_output_format()}

CRITICAL: {"Use the OVERLAPPING FAVORABLE PERIODS - these represent times when BOTH partners' charts are favorable for marriage." if is_overlap else "Be honest but constructive. If match has challenges, focus on remedies."}
Provide SPECIFIC TIMING for marriage based on the analysis above.
"""
    
    def _build_compatibility_analysis_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        kundali_milan_data: Dict,
        compatibility_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Compatibility Analysis"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        ashtakoot_text = self._format_ashtakoot_data(kundali_milan_data)
        compatibility_text = self._format_existing_compatibility(compatibility_data)
        charts_text = self._format_divisional_charts(kundali_milan_data)
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

ASHTAKOOT COMPATIBILITY:
{ashtakoot_text}

EXISTING COMPATIBILITY ANALYSIS:
{compatibility_text}

DIVISIONAL CHART ANALYSIS:
{charts_text}

MULTI-DIMENSIONAL COMPATIBILITY ASSESSMENT:

Analyze compatibility across these dimensions:

1. **PHYSICAL COMPATIBILITY**
   - Based on: Yoni koota score
   - Sexual harmony and attraction
   - Physical chemistry indicators

2. **INTELLECTUAL COMPATIBILITY**
   - Based on: Graha Maitri koota
   - Mental wavelength alignment
   - Communication styles
   - Educational background compatibility

3. **EMOTIONAL COMPATIBILITY**
   - Based on: Tara and Gana kootas
   - Emotional expression patterns
   - Temperament matching
   - Sensitivity levels

4. **FAMILY BACKGROUND COMPATIBILITY**
   - Based on: Varna koota
   - Social and cultural alignment
   - Family values compatibility
   - Traditional vs modern outlook

5. **FINANCIAL COMPATIBILITY**
   - Based on: 2nd and 11th house analysis
   - Earning potential compatibility
   - Spending habits alignment
   - Financial goals harmony

6. **OVERALL PROSPECTS**
   - Marriage success probability
   - Long-term stability indicators
   - Growth potential together
   - Challenges to be aware of

{self.get_output_format()}

CRITICAL: Provide HOLISTIC analysis combining:
- Ashtakoot scores
- Existing compatibility analysis from other evaluations
- Divisional chart insights (especially D9 Navamsa)
- Practical life compatibility dimensions

Be comprehensive but balanced - acknowledge both strengths and areas needing work.
"""
    
    def _build_remedies_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        kundali_milan_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Remedies"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        dosha_text = self._format_dosha_data(kundali_milan_data)
        ashtakoot_text = self._format_ashtakoot_data(kundali_milan_data)
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

QUESTION: {question}

TODAY'S DATE: {today_str}

DOSHAS IDENTIFIED:
{dosha_text}

COMPATIBILITY SCORE:
{ashtakoot_text}

REMEDIAL ANALYSIS INSTRUCTIONS:

Provide specific remedies for each identified dosha and compatibility improvement:

1. **MANGLIK DOSHA REMEDIES** (if present):
   - Kumbh Vivah ritual
   - Mars pacification mantras
   - Gemstone recommendations
   - Fasting on Tuesdays
   - Hanuman worship

2. **NADI DOSHA REMEDIES** (if Nadi score is 0):
   - Mahamrityunjaya Mantra
   - Special puja for health and progeny
   - Donation recommendations
   - Specific rituals

3. **BHAKOOT DOSHA REMEDIES** (if Bhakoot score is 0):
   - Compatibility-enhancing pujas
   - Couple-specific remedies
   - House compatibility rituals

4. **SHADASHTAK DOSHA REMEDIES** (if present):
   - Distance-based remedies
   - Planetary pacification
   - Timing-based solutions

5. **PITRA DOSHA REMEDIES** (if indicated):
   - Ancestral worship
   - Tarpan rituals
   - Charity in ancestors' names
   - Gaya Shraddha

6. **GENERAL COMPATIBILITY ENHANCEMENT**:
   - Remedies for low-scoring kootas
   - Relationship harmony practices
   - Planetary strengthening for 7th house
   - Venus and Jupiter strengthening

7. **RITUALS AND PUJAS**:
   - Pre-marriage ceremonies
   - Vivah Homa
   - Specific deity worship
   - Timing of rituals

{self.get_output_format()}

CRITICAL: Provide SPECIFIC, ACTIONABLE remedies:
- Name exact mantras
- Specify gemstones with carats and fingers
- Detail fasting days and procedures
- List specific pujas and their timing
- Include both astrological and practical remedies

Organize by severity: Essential remedies first, then supportive ones.
"""
    
    def _build_general_matching_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        kundali_milan_data: Dict,
        language: str = "Hindi"
    ) -> str:
        """Build general matching prompt"""
        ashtakoot_text = self._format_ashtakoot_data(kundali_milan_data)
        dosha_text = self._format_dosha_data(kundali_milan_data)
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

QUESTION: {question}

ASHTAKOOT COMPATIBILITY:
{ashtakoot_text}

DOSHA ANALYSIS:
{dosha_text}

Provide comprehensive kundali matching analysis addressing the question.

{self.get_output_format()}
"""
    
    def _format_ashtakoot_data(self, kundali_milan_data: Dict) -> str:
        """Format ashtakoot compatibility data"""
        if not kundali_milan_data:
            return "Kundali milan data not available."
        
        match_details = kundali_milan_data.get("match_details", {})
        ashtakoot = match_details.get("ashtakoot", {}).get("response", {})
        
        # DEBUG: Log the actual ashtakoot structure
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"=== ASHTAKOOT FORMAT DEBUG ===")
        logger.debug(f"ashtakoot present: {bool(ashtakoot)}")
        if ashtakoot:
            logger.debug(f"ashtakoot keys: {ashtakoot.keys()}")
            logger.debug(f"score: {ashtakoot.get('score', 'NOT FOUND')}")
        logger.debug(f"=== END ASHTAKOOT DEBUG ===")
        
        if not ashtakoot:
            return "Ashtakoot data not available."
        
        total_score = ashtakoot.get("score", 0)
        bot_response = ashtakoot.get("bot_response", "")
        
        text = f"TOTAL SCORE: {total_score}/36\n"
        text += f"Assessment: {bot_response}\n\n"
        text += "DETAILED KOOTA SCORES:\n"
        text += "=" * 70 + "\n\n"
        
        # Define kootas in order
        kootas = ["varna", "vasya", "tara", "yoni", "grahamaitri", "gana", "bhakoot", "nadi"]
        
        for koota_name in kootas:
            koota = ashtakoot.get(koota_name, {})
            if koota:
                name = koota.get("name", koota_name.title())
                score = koota.get(koota_name, 0)
                full_score = koota.get("full_score", 0)
                description = koota.get("description", "")
                
                text += f"• {name} ({koota_name.upper()}): {score}/{full_score}\n"
                text += f"  Description: {description}\n"
                
                # Add specific details for each koota
                if koota_name == "varna":
                    text += f"  Boy: {koota.get('boy_varna', 'N/A')}, Girl: {koota.get('girl_varna', 'N/A')}\n"
                elif koota_name == "vasya":
                    text += f"  Boy: {koota.get('boy_vasya', 'N/A')}, Girl: {koota.get('girl_vasya', 'N/A')}\n"
                elif koota_name == "tara":
                    text += f"  Boy Tara: {koota.get('boy_tara', 'N/A')}, Girl Tara: {koota.get('girl_tara', 'N/A')}\n"
                elif koota_name == "yoni":
                    text += f"  Boy: {koota.get('boy_yoni', 'N/A')}, Girl: {koota.get('girl_yoni', 'N/A')}\n"
                elif koota_name == "grahamaitri":
                    text += f"  Boy Lord: {koota.get('boy_lord', 'N/A')}, Girl Lord: {koota.get('girl_lord', 'N/A')}\n"
                elif koota_name == "gana":
                    text += f"  Boy: {koota.get('boy_gana', 'N/A')}, Girl: {koota.get('girl_gana', 'N/A')}\n"
                elif koota_name == "bhakoot":
                    text += f"  Boy Rasi: {koota.get('boy_rasi_name', 'N/A')}, Girl Rasi: {koota.get('girl_rasi_name', 'N/A')}\n"
                elif koota_name == "nadi":
                    text += f"  Boy: {koota.get('boy_nadi', 'N/A')}, Girl: {koota.get('girl_nadi', 'N/A')}\n"
                
                text += "\n"
        
        return text
    
    def _format_dosha_data(self, kundali_milan_data: Dict) -> str:
        """Format dosha analysis data"""
        if not kundali_milan_data:
            return "Dosha data not available."
        
        match_details = kundali_milan_data.get("match_details", {})
        doshas = match_details.get("doshas", {})
        
        if not doshas:
            return "Dosha analysis not available."
        
        text = "DOSHA STATUS:\n"
        text += "=" * 70 + "\n\n"
        
        # Boy's Manglik Dosha
        boy_manglik = doshas.get("boy", {}).get("mangalikDosha", {})
        if boy_manglik:
            has_dosha = boy_manglik.get("hasDosha", False)
            dosha_type = boy_manglik.get("doshaTypeEnglish", "No Dosha")
            reason = boy_manglik.get("reason", {}).get("english", "")
            
            text += f"**BOY'S MANGLIK DOSHA**: {'Present' if has_dosha else 'Absent'}\n"
            text += f"  Type: {dosha_type}\n"
            text += f"  Reason: {reason}\n\n"
        
        # Girl's Manglik Dosha
        girl_manglik = doshas.get("girl", {}).get("mangalikDosha", {})
        if girl_manglik:
            has_dosha = girl_manglik.get("hasDosha", False)
            dosha_type = girl_manglik.get("doshaTypeEnglish", "No Dosha")
            reason = girl_manglik.get("reason", {}).get("english", "")
            
            text += f"**GIRL'S MANGLIK DOSHA**: {'Present' if has_dosha else 'Absent'}\n"
            text += f"  Type: {dosha_type}\n"
            text += f"  Reason: {reason}\n\n"
        
        # Shadashtak Dosha
        shadashtak = doshas.get("compatibility", {}).get("shadashtakDosha", {})
        if shadashtak:
            has_dosha = shadashtak.get("hasDosha", False)
            dosha_type = shadashtak.get("doshaType", "No Dosha")
            reason = shadashtak.get("reason", {}).get("english", "")
            
            text += f"**SHADASHTAK DOSHA**: {'Present' if has_dosha else 'Absent'}\n"
            text += f"  Type: {dosha_type}\n"
            text += f"  Reason: {reason}\n\n"
        
        # Check for Nadi Dosha from ashtakoot
        ashtakoot = match_details.get("ashtakoot", {}).get("response", {})
        nadi_score = ashtakoot.get("nadi", {}).get("nadi", -1)
        if nadi_score == 0:
            text += f"**NADI DOSHA**: Present (Score: 0/8)\n"
            text += f"  Critical dosha affecting health and progeny compatibility\n\n"
        else:
            text += f"**NADI DOSHA**: Absent (Score: {nadi_score}/8)\n\n"
        
        # Check for Bhakoot Dosha
        bhakoot_score = ashtakoot.get("bhakoot", {}).get("bhakoot", -1)
        if bhakoot_score == 0:
            text += f"**BHAKOOT DOSHA**: Present (Score: 0/7)\n"
            text += f"  Affects relationship harmony and prosperity\n\n"
        
        return text
    
    def _format_astro_details(self, kundali_milan_data: Dict) -> str:
        """Format astrological details"""
        match_details = kundali_milan_data.get("match_details", {})
        ashtakoot = match_details.get("ashtakoot", {}).get("response", {})
        
        boy_details = ashtakoot.get("boy_astro_details", {})
        girl_details = ashtakoot.get("girl_astro_details", {})
        
        text = "BOY'S DETAILS:\n"
        text += f"  Rasi: {boy_details.get('rasi', 'N/A')}\n"
        text += f"  Nakshatra: {boy_details.get('nakshatra', 'N/A')} (Pada {boy_details.get('nakshatra_pada', 'N/A')})\n"
        text += f"  Ascendant: {boy_details.get('ascendant_sign', 'N/A')}\n"
        text += f"  Current Dasha: {boy_details.get('current_dasa', 'N/A')}\n\n"
        
        text += "GIRL'S DETAILS:\n"
        text += f"  Rasi: {girl_details.get('rasi', 'N/A')}\n"
        text += f"  Nakshatra: {girl_details.get('nakshatra', 'N/A')} (Pada {girl_details.get('nakshatra_pada', 'N/A')})\n"
        text += f"  Ascendant: {girl_details.get('ascendant_sign', 'N/A')}\n"
        text += f"  Current Dasha: {girl_details.get('current_dasa', 'N/A')}\n"
        
        return text
    
    def _format_dasha_periods(self, kundali_milan_data: Dict) -> str:
        """Format dasha periods for timing analysis"""
        match_details = kundali_milan_data.get("match_details", {})
        ashtakoot = match_details.get("ashtakoot", {}).get("response", {})
        
        boy_details = ashtakoot.get("boy_astro_details", {})
        girl_details = ashtakoot.get("girl_astro_details", {})
        
        text = "CURRENT DASHA PERIODS:\n\n"
        text += f"Boy: {boy_details.get('current_dasa', 'N/A')}\n"
        text += f"Girl: {girl_details.get('current_dasa', 'N/A')}\n"
        
        return text
    
    def _format_divisional_charts(self, kundali_milan_data: Dict) -> str:
        """Format divisional chart data"""
        divisional_charts = kundali_milan_data.get("match_details", {}).get("divisional_charts", {})
        
        if not divisional_charts:
            return "Divisional chart data not available."
        
        text = "D9 NAVAMSA CHART ANALYSIS:\n\n"
        
        # Boy's D9
        boy_d9 = divisional_charts.get("boy_charts", {}).get("D9", {}).get("response", {})
        if boy_d9:
            text += "Boy's D9 Chart (Marriage prospects):\n"
            text += f"  Chart available with {len(boy_d9)} planetary positions\n\n"
        
        # Girl's D9
        girl_d9 = divisional_charts.get("girl_charts", {}).get("D9", {}).get("response", {})
        if girl_d9:
            text += "Girl's D9 Chart (Marriage prospects):\n"
            text += f"  Chart available with {len(girl_d9)} planetary positions\n"
        
        return text
    
    def _format_existing_compatibility(self, compatibility_data: Dict) -> str:
        """Format existing compatibility analysis from other evaluations"""
        if not compatibility_data:
            return "Additional compatibility analysis not available."
        
        text = "Refer to compatibility analysis from 'Stability and Challenges' subdomain\n"
        text += "for detailed relationship dynamics assessment.\n"
        
        return text
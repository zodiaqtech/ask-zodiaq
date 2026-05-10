"""
Marital Stability LLM Prompts

Dedicated prompt builders for each sub-subdomain within Marital Stability:
- Happiness and Harmony
- Separation Risk
- Doshas and Stress Factors
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.domains.base import (
    BasePromptBuilder, QueryMeta, TimingWindow,
    QueryType, EventPolarity, InterpretationGoal
)


class MaritalStabilityPromptBuilder(BasePromptBuilder):
    """
    Prompt builder for Marital Stability subtopic.
    
    Builds specialized prompts for:
    - Happiness and Harmony: Overall marital fulfillment
    - Separation Risk: Divorce/separation indicators
    - Doshas and Stress Factors: Manglik and other afflictions
    """
    
    domain = "Marriage"
    subtopic = "Marital Stability"
    
    def build_system_prompt(self) -> str:
        """Build the system prompt for Marital Stability analysis"""
        return """You are an expert KP (Krishnamurti Paddhati) and Vedic astrologer specializing in marriage stability analysis.

Your expertise includes:
- 7th house analysis for marital harmony
- Venus, Moon, Jupiter combinations for relationship fulfillment
- Identifying separation and divorce indicators
- Manglik dosha and its cancellations
- Remedial measures for marital challenges

CORE PRINCIPLES:
1. Be sensitive when discussing difficult topics like separation risk
2. Always balance negative findings with constructive remedies
3. Present both challenges and opportunities for improvement
4. Avoid catastrophizing - astrology shows tendencies, not certainties
5. Emphasize that conscious effort can overcome most astrological challenges

IMPORTANT:
- Never predict definite divorce or separation
- Frame risk factors as "tendencies" or "areas needing attention"
- Provide actionable remedies and suggestions
- Maintain hope while being truthful about challenges"""
    
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
        
        if "Happiness" in sub_subdomain or "Harmony" in sub_subdomain:
            return self._build_happiness_prompt(question, technical_points, meta, language)
        elif "Divorce Timing" in sub_subdomain:
            return self._build_divorce_timing_prompt(question, technical_points, meta, timing_windows, language)
        elif "Separation" in sub_subdomain or "Risk" in sub_subdomain or "Divorce" in sub_subdomain:
            return self._build_separation_risk_prompt(question, technical_points, meta, language)
        elif "Compatibility" in sub_subdomain:
            return self._build_compatibility_prompt(question, technical_points, meta, language)
        elif "Dosha" in sub_subdomain or "Stress" in sub_subdomain:
            return self._build_dosha_prompt(question, technical_points, meta, language)
        else:
            return self._build_general_stability_prompt(question, technical_points, meta, language)
    
    def _build_happiness_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Happiness and Harmony questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: Happiness and Harmony
- Query Type: NON_TIMING
- Event Polarity: NEUTRAL
- Interpretation Goal: STATUS
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}

SPECIFIC INSTRUCTIONS FOR HAPPINESS AND HARMONY ANALYSIS:

FAVORABLE INDICATORS TO HIGHLIGHT:
1. Benefics (Jupiter, Venus, Moon, Mercury) in 7th house
2. Venus-Jupiter harmonious aspects (trine, sextile)
3. Strong Venus (own sign, exalted)
4. Venus-Moon connections for emotional fulfillment
5. Jupiter aspecting 7th house or its lord
6. Strong 4th house for domestic happiness
7. Venus in angular houses (1, 4, 7, 10)

ANALYSIS STRUCTURE:
- Begin with overall happiness potential
- Identify key supporting factors
- Note any areas that need conscious attention
- Conclude with enhancement suggestions

TONE:
- Focus on positive aspects while being realistic
- Frame any challenges as areas for growth
- Emphasize that happiness comes from mutual effort

{self.get_output_format()}
"""
    
    def _build_separation_risk_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Separation Risk questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: Separation Risk
- Query Type: NON_TIMING
- Event Polarity: NEGATIVE
- Interpretation Goal: RISK
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}

SPECIFIC INSTRUCTIONS FOR SEPARATION RISK ANALYSIS:

RISK INDICATORS TO ASSESS:
1. Malefics (Saturn, Mars, Rahu, Ketu) in 7th house
2. 7th lord in dusthana houses (6, 8, 12)
3. Rahu-Ketu axis across 1-7 houses
4. Saturn afflicting Venus (square, opposition)
5. Mars-Venus tense aspects
6. 8th lord influencing 7th house
7. 6th lord (disputes) affecting 7th house
8. Paap Kartari yoga on 7th house

CRITICAL GUIDELINES:
1. NEVER predict definite separation or divorce
2. Use language like "tendency toward," "potential for," "may require attention"
3. ALWAYS pair each risk factor with a remedy or mitigation
4. Emphasize that awareness and effort can overcome most indicators
5. Note any cancellation or ameliorating factors

STRUCTURE:
- Assess overall stability first (positive framing)
- Identify specific areas needing attention
- For each challenge, provide a corresponding remedy
- Conclude with constructive guidance

FORBIDDEN PHRASES:
- "Divorce is inevitable"
- "Marriage will fail"
- "Cannot be remedied"
- "Hopeless situation"

{self.get_output_format()}
"""
    
    def _build_divorce_timing_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[TimingWindow]] = None,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Divorce Timing questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        
        # Format timing windows
        timing_str = ""
        if timing_windows:
            timing_str = "\n\nDIVORCE/SEPARATION RISK TIMING WINDOWS:\n"
            for i, tw in enumerate(timing_windows[:5], 1):
                dasha = tw.get("dasha", "Unknown")
                start = tw.get("start_date", "")
                end = tw.get("end_date", "")
                score = tw.get("score", 0)
                timing_str += f"{i}. {dasha}: {start} to {end} (Risk Score: {score})\n"

        # Get language instruction for Hindi/English output
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: Divorce Timing
- Query Type: TIMING
- Event Polarity: NEGATIVE
- Interpretation Goal: RISK
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}
{timing_str}

SPECIFIC INSTRUCTIONS FOR DIVORCE/SEPARATION TIMING ANALYSIS:

TIMING METHODOLOGY:
1. Identify dasha periods where separation significators are active
2. Look for periods when 6th, 8th, 12th house influences peak
3. Saturn, Mars, Rahu transits over 7th house or Venus
4. Dasha of planets signifying 6/8/12 houses

KEY SEPARATION TIMING INDICATORS:
1. Dasha/Antardasha of planets connected to 6th house (disputes)
2. Dasha of 8th lord or planets in 8th (transformation/endings)
3. Dasha of 12th lord (loss, separation)
4. Saturn transit over natal Venus or 7th house
5. Rahu/Ketu transit over relationship axis

CRITICAL GUIDELINES:
1. Frame as "periods requiring extra attention" NOT "divorce will happen"
2. These are windows of vulnerability, not certainties
3. Awareness during these periods can prevent issues
4. Recommend preventive measures for challenging periods
5. Also mention stabilizing periods for balance

RESPONSE STRUCTURE:
1. Brief overview of timing pattern for marital challenges
2. List specific periods with higher risk (with dates)
3. Explain what makes each period challenging
4. Provide preventive remedies for each period
5. Mention favorable periods for relationship healing

FORBIDDEN:
- "Divorce will happen in [date]"
- "Marriage will end during..."
- Definitive predictions of separation

{self.get_output_format()}
"""
    
    def _build_compatibility_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Compatibility (Happy/Unhappy) questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: Compatibility
- Query Type: NON_TIMING
- Event Polarity: NEUTRAL
- Interpretation Goal: STATUS
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}

SPECIFIC INSTRUCTIONS FOR COMPATIBILITY ANALYSIS:

HAPPY MARRIAGE INDICATORS (R3_x):
1. 7th sub-lord is Jupiter/Venus signifying 2/11
2. Luminaries (Sun/Moon) well-placed with benefic aspects
3. Venus-Mars in harmonious aspect (not signifying 6/10/12)
4. Moon receiving benefic aspects from Saturn/Venus/Jupiter
5. 7th house supported by benefics (occupation/lordship)
6. Strong Venus in the chart

UNHAPPY MARRIAGE INDICATORS (R4_x):
1. Sun-Moon conflict in marriage houses
2. Malefics (Mars/Saturn/Rahu) afflicting 7th house
3. Mercury afflicted in 7th → communication issues
4. 7th cusp heavily signifying 6/8/12 houses
5. Moon-Jupiter disharmony
6. Venus and 7th lord both afflicted

ANALYSIS STRUCTURE:
1. Start with overall compatibility assessment
2. List positive indicators (happy marriage factors)
3. List challenging indicators (unhappy factors)
4. Provide balanced conclusion
5. Suggest remedies for any challenging factors

{self.get_output_format()}
"""
    
    def _build_dosha_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi"
    ) -> str:
        """Build prompt for Doshas and Stress Factors questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Sub-subdomain: Doshas and Stress Factors
- Query Type: NON_TIMING
- Event Polarity: NEGATIVE
- Interpretation Goal: RISK
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}

SPECIFIC INSTRUCTIONS FOR DOSHA ANALYSIS:

DOSHAS TO ASSESS:

1. MANGLIK (KUJA) DOSHA:
   - Mars in houses 1, 2, 4, 7, 8, 12 from Lagna or Moon
   - Cancellation conditions:
     * Mars in own sign (Aries, Scorpio)
     * Mars exalted (Capricorn)
     * Jupiter's aspect on Mars
     * Both partners have similar dosha
     * Mars in specific beneficial positions

2. RAHU-KETU DOSHA:
   - Rahu or Ketu in 7th house
   - Rahu-Venus conjunction
   - Impact: Unconventional patterns, foreign/interfaith connections

3. SATURN DOSHA:
   - Saturn in 7th house
   - Saturn afflicting Venus
   - Impact: Delays, maturity required, stability once established

4. PAAP KARTARI:
   - Malefics hemming 7th house
   - Impact: External pressures on marriage

ANALYSIS APPROACH:
1. Identify which doshas are present (if any)
2. Check for cancellation conditions
3. Assess the severity (full, partial, cancelled)
4. Provide specific remedies for each dosha
5. Note if doshas can actually lead to positive outcomes (e.g., Saturn giving stability)

REMEDIES FRAMEWORK:
- Planetary remedies (gems, colors, mantras)
- Behavioral modifications
- Compatibility considerations
- Modern interpretations (not superstitious)

{self.get_output_format()}
"""
    
    def _build_general_stability_prompt(
        self,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        language: str = "Hindi"
    ) -> str:
        """Build general prompt for Marital Stability questions"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        raw_points = "\n".join(technical_points) if technical_points else ""
        # Get language instruction
        language_instruction = self.get_language_instruction(language)

        return f"""
{language_instruction}

{self.build_system_prompt()}

{language_instruction}

QUERY CONTEXT:
- Domain: Marriage
- Subtopic: Marital Stability
- Query Type: {meta.query_type.value}
- Event Polarity: {meta.polarity.value}
- Interpretation Goal: {meta.goal.value}
- CURRENT DATE: {today_str}

USER QUESTION:
"{question}"

TECHNICAL ASTROLOGICAL POINTS:
{raw_points}

ANALYSIS STRUCTURE:
1. Overall stability assessment
2. Supporting factors (benefic influences)
3. Challenging factors (malefic influences)
4. Dosha assessment if applicable
5. Remedial recommendations

TONE GUIDELINES:
- Balance realism with hope
- Never catastrophize
- Emphasize personal agency
- Provide actionable guidance

{self.get_output_format()}
"""
    
    def get_output_format(self) -> str:
        """Get Marital Stability specific output format"""
        return """
OUTPUT FORMAT (MUST FOLLOW EXACTLY):

GENERAL_ANSWER:
<2-7 lines addressing the stability query. Begin with overall assessment, then highlight key factors. Be balanced and constructive.>

ASTROLOGICAL_ANALYSIS:
<Structured analysis covering:
- 7th house condition and influences
- Venus and relationship planets assessment
- Any dosha presence and their status (active/cancelled)
- Balance of benefic vs malefic influences
- Overall stability indicators>

SUMMARY:
<1-2 lines summarizing the key finding with a constructive note.>

REMEDIES_ASTROLOGICAL:
- <Specific remedy for identified challenge 1>
- <Specific remedy for identified challenge 2>
- <General relationship-strengthening remedy>

REMEDIES_GENERAL:
- <Communication/relationship skill>
- <Lifestyle recommendation>
- <Personal development suggestion>

FORMATTING RULES:
- ASCII only (no emojis or Unicode symbols)
- Sensitive, supportive tone
- Never predict definite negative outcomes
- Always include constructive remedies
"""

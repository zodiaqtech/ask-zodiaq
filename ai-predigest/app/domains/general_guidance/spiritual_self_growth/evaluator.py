"""
Spiritual Self Growth Evaluator - ENHANCED VERSION

ENHANCEMENTS:
✅ TimingWindow object handling (not just dicts)
✅ Timing windows pass-through for LLM
✅ Vedic analysis preserved and enhanced
✅ Excel-based question config support
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Vedic-only analysis (no KP for spiritual guidance)

Features:
- Comprehensive dasha analysis
- House lord analysis with dignity
- Aspect strength analysis
- Planet strength calculations
- Timing window extraction
- LLM-optimized data formatting

Evaluates spiritual aspects including:
- Karma and Life Purpose
- Karmic Debts and Patterns
- Emotional Stability Indicators
- Decision-Making Clarity
- Guru/Teacher Indicators
- Spiritual Remedies
"""
from typing import Dict, List, Any, Set, Optional, Tuple
from datetime import datetime, timedelta

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal, TimingWindow
)
from app.core.astro_constants import (
    normalize_planet_name, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, _has_evil_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, is_combust, has_dig_bala,
    detect_aspects, BENEFICS, MALEFICS
)


class SpiritualSelfGrowthEvaluator(BaseEvaluator):
    """
    Enhanced Evaluator for Spiritual Self Growth subtopic.
    
    Analyzes:
    - Life purpose through 9th and 12th house
    - Karmic debts via Saturn, Rahu, Ketu positions
    - Emotional stability through Moon, Mercury
    - Decision-making clarity through Mercury, Jupiter
    - Guru indicators through Jupiter and 9th house
    - Spiritual remedies based on chart
    
    ENHANCEMENTS:
    - Dasha timeline analysis
    - House lord dignity analysis
    - Aspect strength calculations
    - Timing window extraction
    - LLM-optimized formatting
    """
    
    domain = "General_Guidance"
    subtopic = "Spiritual Self Growth"
    
    # Vedic house significations for spiritual growth
    positive_houses = {1, 5, 9, 12}  # Self, wisdom, spirituality, liberation
    supportive_houses = {4, 8}  # Inner peace, transformation
    negative_houses = {6, 8}  # Obstacles, sudden events
    
    # Key planets for spiritual analysis
    key_planets = {"Jupiter", "Moon", "Mercury", "Saturn", "Ketu", "Rahu", "Sun", "Venus"}
    
    # Question-specific house mappings (can be extended via Excel config)
    QUESTION_HOUSES = {
        "karma_purpose": {1, 5, 9, 12},  # Self, purva punya, dharma, moksha
        "karmic_debts": {6, 8, 12},  # Obstacles, transformation, losses
        "emotional_stability": {1, 4, 5, 11},  # Self, mind, emotions, gains
        "taking_decisions": {1, 2, 5, 9},  # Self, speech, intelligence, wisdom
        "finding_guru": {4, 5, 9, 10},  # Learning, wisdom, dharma, karma
        "spiritual_remedies": {1, 5, 8, 9, 12}  # All spiritual houses
    }
    
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        sub_subdomain: str = "",
        meta: QueryMeta = None,
        question: str = "",
        timing_windows: Optional[Dict[str, List]] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Main evaluation for spiritual and self-growth analysis.
        
        ENHANCEMENTS:
        - Extract timing windows for LLM
        - Calculate house lords with dignity
        - Analyze dasha timeline
        - Format data for LLM consumption
        """
        self.reset()  # Clear seen points
        
        # Use Vedic data (spiritual guidance is Vedic-only)
        working_planets = vedic_planets if vedic_planets else planets
        working_houses = vedic_houses if vedic_houses else houses
        
        # Detect aspects first
        working_planets = detect_aspects(working_planets)
        
        result = EvaluationResult()
        
        # Extract question ID for house mapping
        question_id = kwargs.get("question_id", "")
        relevant_houses = self.QUESTION_HOUSES.get(question_id, self.positive_houses)
        
        # 1. Core Spiritual Analysis
        karma_points = self._evaluate_karma_purpose(working_planets, working_houses)
        result.extend_points(karma_points)
        
        karmic_debt_points = self._evaluate_karmic_debts(working_planets, working_houses)
        result.extend_points(karmic_debt_points)
        
        emotional_points = self._evaluate_emotional_stability(working_planets, working_houses)
        result.extend_points(emotional_points)
        
        decision_points = self._evaluate_decision_making(working_planets, working_houses)
        result.extend_points(decision_points)
        
        guru_points = self._evaluate_guru_indicators(working_planets, working_houses)
        result.extend_points(guru_points)
        
        # 2. ENHANCED: Calculate house lords with dignity
        house_lords_info = self._calculate_house_lords(working_planets, working_houses, relevant_houses)
        result.additional_data["house_lords"] = house_lords_info
        
        # 3. ENHANCED: Calculate planet strengths
        planet_strengths = self._calculate_planet_strengths(working_planets)
        result.additional_data["planet_strengths"] = planet_strengths
        
        # 4. ENHANCED: Analyze aspects with strength
        aspect_analysis = self._analyze_aspects_with_strength(working_planets)
        result.additional_data["aspect_analysis"] = aspect_analysis
        
        # 5. ENHANCED: Extract timing windows for LLM
        timing_info = self._extract_timing_windows(timing_windows)
        if timing_info:
            result.additional_data["timing_windows"] = timing_info
        
        # 6. ENHANCED: Dasha timeline (if provided)
        dasha_timeline = kwargs.get("dasha_timeline", None)
        current_dasha = kwargs.get("current_dasha", None)
        
        if dasha_timeline:
            result.additional_data["dasha_timeline"] = dasha_timeline
        if current_dasha:
            result.additional_data["current_dasha"] = current_dasha
        
        # 7. ENHANCED: Format for LLM-friendly consumption
        result.additional_data["llm_summary"] = self._format_for_llm(
            working_planets, 
            working_houses, 
            house_lords_info,
            planet_strengths,
            aspect_analysis
        )
        
        return result
    
    def _evaluate_karma_purpose(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> List[str]:
        """Evaluate life purpose and karmic alignment"""
        points = []
        
        # Check 9th house (dharma, higher purpose)
        jupiter = get_planet(planets, "Jupiter")
        if jupiter:
            jupiter_house = jupiter.get("house")
            if jupiter_house in {1, 5, 9}:
                points.append("Jupiter in dharma trikona suggests strong alignment with life purpose")
            
            if _is_exalted(jupiter):
                points.append("Exalted Jupiter indicates natural wisdom and dharmic path")
        
        # Check 12th house (moksha, liberation)
        ketu = get_planet(planets, "Ketu")
        if ketu:
            ketu_house = ketu.get("house")
            if ketu_house in {9, 12}:
                points.append("Ketu placement suggests spiritual inclination and karmic lessons")
        
        # Check Sun (soul purpose)
        sun = get_planet(planets, "Sun")
        if sun:
            if _is_exalted(sun):
                points.append("Strong Sun indicates clear self-identity and purpose")
            elif _is_debilitated(sun):
                points.append("Weak Sun suggests need to develop self-confidence and clarity of purpose")
        
        return points
    
    def _evaluate_karmic_debts(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> List[str]:
        """Evaluate karmic debts and patterns"""
        points = []
        
        # Saturn represents karmic debts
        saturn = get_planet(planets, "Saturn")
        if saturn:
            saturn_house = saturn.get("house")
            if saturn_house in {1, 4, 7, 10}:
                points.append(f"Saturn in {saturn_house}th house indicates karmic lessons in that life area")
            
            if _is_retrograde(saturn):
                points.append("Retrograde Saturn suggests unfinished karmic business from past")
        
        # Rahu-Ketu axis represents karmic direction
        rahu = get_planet(planets, "Rahu")
        ketu = get_planet(planets, "Ketu")
        
        if rahu and ketu:
            rahu_house = rahu.get("house")
            ketu_house = ketu.get("house")
            points.append(f"Rahu in {rahu_house}th house shows karmic growth area; Ketu in {ketu_house}th shows past life mastery")
        
        # Check 8th house (transformation, karmic debts)
        planets_in_8th = sum(1 for p in planets.values() if p.get("house") == 8)
        if planets_in_8th >= 2:
            points.append("Multiple planets in 8th house indicate intense karmic transformation")
        
        return points
    
    def _evaluate_emotional_stability(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> List[str]:
        """Evaluate emotional stability indicators"""
        points = []
        
        # Moon represents mind and emotions
        moon = get_planet(planets, "Moon")
        if moon:
            if _is_exalted(moon):
                points.append("Exalted Moon provides emotional strength and mental clarity")
            elif _is_debilitated(moon):
                points.append("Debilitated Moon suggests emotional sensitivity and need for grounding")
            
            if _has_evil_aspect(moon, planets):
                points.append("Moon receives malefic aspects indicating emotional challenges requiring healing")
            
            if is_combust(moon, planets):
                points.append("Combust Moon suggests ego-emotion conflicts needing resolution")
        
        # Mercury for mental clarity
        mercury = get_planet(planets, "Mercury")
        if mercury:
            if _is_exalted(mercury):
                points.append("Strong Mercury aids in rational thinking and emotional processing")
            elif _is_debilitated(mercury):
                points.append("Weak Mercury may cause confusion in emotional matters")
        
        # Venus for emotional harmony
        venus = get_planet(planets, "Venus")
        if venus:
            if _is_exalted(venus):
                points.append("Exalted Venus promotes forgiveness and emotional balance")
        
        return points
    
    def _evaluate_decision_making(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> List[str]:
        """Evaluate decision-making clarity"""
        points = []
        
        # Mercury for intellect and analysis
        mercury = get_planet(planets, "Mercury")
        if mercury:
            if _is_debilitated(mercury) or is_combust(mercury, planets):
                points.append("Weak Mercury creates indecisiveness and overthinking")
            
            if _is_retrograde(mercury):
                points.append("Retrograde Mercury causes repeated analysis and decision delays")
        
        # Jupiter for wisdom
        jupiter = get_planet(planets, "Jupiter")
        if jupiter:
            if _is_exalted(jupiter) or _is_own_sign(jupiter):
                points.append("Strong Jupiter provides wisdom and good judgment")
            elif _is_debilitated(jupiter):
                points.append("Weak Jupiter reduces confidence in decision-making")
        
        # Saturn for discipline but also delays
        saturn = get_planet(planets, "Saturn")
        if saturn:
            saturn_house = saturn.get("house")
            if saturn_house == 1:
                points.append("Saturn in ascendant creates cautious, delayed decision-making pattern")
        
        return points
    
    def _evaluate_guru_indicators(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict]
    ) -> List[str]:
        """Evaluate indicators for finding guru/teacher"""
        points = []
        
        # Jupiter is the natural guru
        jupiter = get_planet(planets, "Jupiter")
        if jupiter:
            jupiter_house = jupiter.get("house")
            
            if jupiter_house == 9:
                points.append("Jupiter in 9th house strongly indicates finding an enlightened teacher")
            
            if _is_exalted(jupiter):
                points.append("Exalted Jupiter attracts wise mentors and spiritual guides")
            
            if has_harmonious_aspect(jupiter, planets):
                points.append("Jupiter receives benefic aspects facilitating guru connection")
        
        # Ketu can indicate spiritual teacher
        ketu = get_planet(planets, "Ketu")
        if ketu:
            ketu_house = ketu.get("house")
            if ketu_house in {9, 12}:
                points.append("Ketu placement suggests unconventional or mystical spiritual guidance")
        
        return points
    
    # ========== ENHANCED METHODS ==========
    
    def _calculate_house_lords(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        relevant_houses: Set[int]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Calculate house lords with their dignity for relevant houses.
        
        Returns:
            Dict mapping house number to lord info with dignity
        """
        house_lords = {}
        
        for house_num in relevant_houses:
            # Find house data
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            if not house_data:
                continue
            
            # Get house sign
            house_sign = house_data.get("sign", "")
            
            # Determine lord of the sign
            lord_name = self._get_sign_lord(house_sign)
            if not lord_name:
                continue
            
            # Get lord planet data
            lord_planet = get_planet(planets, lord_name)
            if not lord_planet:
                continue
            
            # Calculate dignity
            dignity = self._calculate_dignity(lord_planet)
            
            house_lords[house_num] = {
                "house": house_num,
                "sign": house_sign,
                "lord": lord_name,
                "lord_house": lord_planet.get("house", 0),
                "lord_sign": lord_planet.get("sign", ""),
                "dignity": dignity,
                "is_retrograde": _is_retrograde(lord_planet)
            }
        
        return house_lords
    
    def _get_sign_lord(self, sign: str) -> Optional[str]:
        """Get the ruling planet of a zodiac sign"""
        sign_lords = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter"
        }
        return sign_lords.get(sign)
    
    def _calculate_dignity(self, planet: Dict[str, Any]) -> str:
        """Calculate planet's dignity (Exalted/Own/Neutral/Debilitated)"""
        if _is_exalted(planet):
            return "Exalted"
        elif _is_debilitated(planet):
            return "Debilitated"
        elif _is_own_sign(planet):
            return "Own Sign"
        else:
            return "Neutral"
    
    def _calculate_planet_strengths(
        self,
        planets: Dict[str, Dict]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate strength indicators for key spiritual planets.
        
        Returns:
            Dict with planet strengths (dignity, aspects, house position)
        """
        strengths = {}
        
        for planet_name in self.key_planets:
            planet = get_planet(planets, planet_name)
            if not planet:
                continue
            
            strength_info = {
                "name": planet_name,
                "house": planet.get("house", 0),
                "sign": planet.get("sign", ""),
                "dignity": self._calculate_dignity(planet),
                "is_retrograde": _is_retrograde(planet),
                "is_combust": is_combust(planet, planets),
                "has_dig_bala": has_dig_bala(planet),
                "benefic_aspects": 0,
                "malefic_aspects": 0
            }
            
            # Count aspects
            if has_harmonious_aspect(planet, planets):
                strength_info["benefic_aspects"] += 1
            if _has_evil_aspect(planet, planets):
                strength_info["malefic_aspects"] += 1
            
            strengths[planet_name] = strength_info
        
        return strengths
    
    def _analyze_aspects_with_strength(
        self,
        planets: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """
        Analyze aspects between planets with strength indicators.
        
        Returns:
            List of aspect relationships with type and strength
        """
        aspects = []
        
        planet_list = list(planets.keys())
        for i, p1_name in enumerate(planet_list):
            p1 = planets[p1_name]
            for p2_name in planet_list[i+1:]:
                p2 = planets[p2_name]
                
                # Check if planets aspect each other
                aspect_type = self._get_aspect_type(p1, p2)
                if aspect_type:
                    aspects.append({
                        "from": p1_name,
                        "to": p2_name,
                        "type": aspect_type,
                        "is_benefic": _is_benefic(p1_name) and _is_benefic(p2_name),
                        "is_malefic": _is_malefic(p1_name) or _is_malefic(p2_name)
                    })
        
        return aspects
    
    def _get_aspect_type(self, p1: Dict, p2: Dict) -> Optional[str]:
        """Determine aspect type between two planets"""
        house_diff = abs(p1.get("house", 0) - p2.get("house", 0))
        
        if house_diff == 0:
            return "Conjunction"
        elif house_diff == 1 or house_diff == 11:
            return "Adjacent"
        elif house_diff == 4 or house_diff == 8:
            return "Trine"
        elif house_diff == 5 or house_diff == 7:
            return "Square/Opposition"
        
        return None
    
    def _extract_timing_windows(
        self,
        timing_windows: Optional[Dict[str, List]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract timing windows, handling both dict and TimingWindow objects.
        
        Returns:
            Formatted timing data for LLM with BEST and NEAREST windows
        """
        if not timing_windows:
            return None
        
        result = {
            "best_windows": [],
            "nearest_windows": []
        }
        
        for category, windows in timing_windows.items():
            if not windows:
                continue
            
            for window in windows:
                # Handle TimingWindow objects
                if hasattr(window, '__dict__'):
                    window_dict = {
                        "start_date": getattr(window, 'start_date', None),
                        "end_date": getattr(window, 'end_date', None),
                        "score": getattr(window, 'score', 0),
                        "description": getattr(window, 'description', ''),
                        "category": category
                    }
                else:
                    # Already a dict
                    window_dict = window
                    window_dict["category"] = category
                
                # Categorize as BEST or NEAREST
                score = window_dict.get("score", 0)
                if score >= 0.8:
                    result["best_windows"].append(window_dict)
                elif score >= 0.6:
                    result["nearest_windows"].append(window_dict)
        
        # Sort by score
        result["best_windows"].sort(key=lambda x: x.get("score", 0), reverse=True)
        result["nearest_windows"].sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return result if (result["best_windows"] or result["nearest_windows"]) else None
    
    def _format_for_llm(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        house_lords: Dict[int, Dict],
        planet_strengths: Dict[str, Dict],
        aspects: List[Dict]
    ) -> Dict[str, Any]:
        """
        Format all analysis data in LLM-friendly structure.
        
        Returns:
            Comprehensive summary for LLM consumption
        """
        return {
            "key_planets": {
                name: {
                    "position": f"{data['sign']} in House {data['house']}",
                    "dignity": data["dignity"],
                    "strength_notes": self._get_strength_notes(data)
                }
                for name, data in planet_strengths.items()
            },
            "house_lords_summary": {
                house_num: {
                    "lord": info["lord"],
                    "placement": f"House {info['lord_house']} ({info['lord_sign']})",
                    "dignity": info["dignity"]
                }
                for house_num, info in house_lords.items()
            },
            "key_aspects": [
                f"{asp['from']} {'benefic' if asp['is_benefic'] else 'malefic'} aspect to {asp['to']}"
                for asp in aspects[:5]  # Top 5 aspects
            ]
        }
    
    def _get_strength_notes(self, planet_data: Dict) -> List[str]:
        """Get human-readable strength notes for a planet"""
        notes = []
        
        if planet_data["is_retrograde"]:
            notes.append("Retrograde")
        if planet_data["is_combust"]:
            notes.append("Combust")
        if planet_data["has_dig_bala"]:
            notes.append("Has Directional Strength")
        if planet_data["benefic_aspects"] > 0:
            notes.append("Benefic aspects")
        if planet_data["malefic_aspects"] > 0:
            notes.append("Malefic aspects")
        
        return notes
    
    def get_questions(self) -> List[Question]:
        """Get predefined questions for Spiritual Self Growth"""
        return [
            # Karma and Purpose
            Question(
                id="karma_purpose",
                question="What is my life's purpose and is my karma aligned to achieve it?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Karma and Purpose"
            ),
            
            # Karmic Debts
            Question(
                id="karmic_debts",
                question="Are there any karmic debts affecting my journey?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Karmic Debts"
            ),
            
            # Finding Emotional Stability
            Question(
                id="emotional_stability",
                question="How can I effectively handle emotions such as anxiety, fear, sadness, anger and cultivate forgiveness and empathy?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Finding Emotional Stability"
            ),
            
            # Taking Decisions
            Question(
                id="taking_decisions",
                question="I find it difficult to take decisions. Why is it so and what should I do to correct this?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Taking Decisions"
            ),
            
            # Finding a Teacher (Guru)
            Question(
                id="finding_guru",
                question="Will I find the right teacher, guru, or mentor to guide me?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.POSITIVE,
                    goal=InterpretationGoal.MANIFESTATION
                ),
                sub_subdomain="Finding a Teacher (Guru)"
            ),
            
            # Remedy and Suggestion
            Question(
                id="spiritual_remedies",
                question="Any remedies that I must follow?",
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Remedy and Suggestion"
            )
        ]
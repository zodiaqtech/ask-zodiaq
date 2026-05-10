"""
Physical and Mental Health Evaluator - Enhanced Version v3.1

FIXES & ENHANCEMENTS:
✅ _extract_timing_windows now handles TimingWindow objects (not just dicts)
✅ Timing windows pass-through for LLM (BEST + NEAREST)
✅ KP health engine integration (preserved)
✅ FIXED: Dignity calculation now works with fallback method
✅ FIXED: Better logging for debugging dignity issues
✅ FIXED: Direct dignity calculation from sign placement

Features:
✅ Excel-based question config
✅ Question-specific houses
✅ House lords with dignity (using Vedic data)
✅ Vedic parser aspects
✅ Strength calculations
✅ LLM-friendly formatting
✅ Dasha timeline support (via kwargs)
✅ Dual data source (KP + Vedic)
✅ Disease/Cure logic via 6th–8th–12th cusp sub-lords
✅ Organ-specific, eye, speech analysis
✅ Mental health handled advisory-only

⚠️ Astrology-based insights are supportive only.
⚠️ Never replace medical diagnosis or treatment.
"""

from typing import Dict, List, Optional
from collections import defaultdict
import logging

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)

from app.core.astro_constants import detect_aspects, normalize_planet_name, get_signified_houses
from app.domains.excel_structure_config import get_houses_for_question

# 🔗 IMPORT YOUR EXISTING HEALTH ENGINE FUNCTIONS
from app.domains.health.health_engine import (
    evaluate_health,
    evaluate_eye_risks,
    evaluate_speech,
    generate_full_health_report
)

# Import house lords analyzer
try:
    from app.utils.house_lords_analyzer import (
        HouseLordsAnalyzer,
        get_house_lords_points,
        LordDignity
    )
    from app.utils.vedic_api_parser import calculate_planetary_aspects
    HOUSE_LORDS_AVAILABLE = True
except ImportError:
    HOUSE_LORDS_AVAILABLE = False
    logging.warning("House lords analyzer not available - using basic analysis")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PhysicalAndMentalHealthEvaluator(BaseEvaluator):
    """
    Enhanced evaluator for Physical & Mental Health.
    
    Features:
    - Question-specific houses from Excel config
    - House lords analysis with dignity (using Vedic data)
    - Aspects extraction
    - Strength scoring
    - KP timing (preserved)
    - Dual data source support (KP + Vedic)
    - Timing windows extraction and formatting
    - FIXED: Dignity calculation with fallback
    """

    domain = "Health"
    subtopic = "Physical And Mental Health"

    # Health-specific houses
    HEALTH_HOUSES = {1, 5, 6, 8, 11, 12}
    
    # Mental Health specific houses (KP/Vedic psychology)
    MENTAL_HEALTH_HOUSES = {1, 4, 5, 8, 12}  # Added 4th (emotional foundation)
    
    # Mental Health key planets
    MENTAL_HEALTH_PLANETS = {
        "Moon": "Mind, emotions, mental stability - MOST IMPORTANT",
        "Mercury": "Nervous system, communication, rational thinking",
        "Rahu": "Anxiety, obsession, addiction, confusion",
        "Ketu": "Detachment, spiritual confusion, dissociation",
        "Saturn": "Depression, chronic stress, isolation"
    }

    # House meanings for health context
    HOUSE_MEANINGS = {
        1: "Vitality/Constitution",
        4: "Emotional Foundation/Peace of Mind",  # NEW for mental health
        5: "Mental Peace/Recovery Support",
        6: "Disease/Illness",
        8: "Chronic Issues/Trauma/Transformation",  # Updated for mental health
        11: "Recovery/Cure",
        12: "Hospitalization/Isolation/Subconscious"  # Updated for mental health
    }
    
    # Mental health house meanings (more specific)
    MENTAL_HEALTH_HOUSE_MEANINGS = {
        1: "Self-identity, physical body affecting mind",
        4: "Emotional base, inner peace, domestic happiness, mother",
        5: "Intelligence, mental clarity, creativity, emotional expression",
        8: "Trauma, hidden fears, sudden psychological events, transformation",
        12: "Isolation, subconscious mind, losses, spiritual retreat, addiction patterns"
    }

    # ═══════════════════════════════════════════════════════════════════
    # DIGNITY CALCULATION CONSTANTS (NEW!)
    # ═══════════════════════════════════════════════════════════════════
    
    # Exaltation signs
    EXALTATION = {
        "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
        "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
        "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"
    }
    
    # Debilitation signs (opposite of exaltation)
    DEBILITATION = {
        "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
        "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
        "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"
    }
    
    # Own signs
    OWN_SIGNS = {
        "Sun": ["Leo"],
        "Moon": ["Cancer"],
        "Mars": ["Aries", "Scorpio"],
        "Mercury": ["Gemini", "Virgo"],
        "Jupiter": ["Sagittarius", "Pisces"],
        "Venus": ["Taurus", "Libra"],
        "Saturn": ["Capricorn", "Aquarius"],
        "Rahu": ["Aquarius"],
        "Ketu": ["Scorpio"]
    }
    
    # Friendly signs
    FRIENDLY_SIGNS = {
        "Sun": ["Aries", "Leo", "Sagittarius", "Scorpio", "Pisces"],
        "Moon": ["Cancer", "Taurus", "Pisces", "Scorpio"],
        "Mars": ["Aries", "Scorpio", "Leo", "Sagittarius", "Pisces", "Cancer"],
        "Mercury": ["Gemini", "Virgo", "Taurus", "Libra", "Aquarius"],
        "Jupiter": ["Sagittarius", "Pisces", "Cancer", "Aries", "Leo", "Scorpio"],
        "Venus": ["Taurus", "Libra", "Pisces", "Capricorn", "Aquarius", "Gemini"],
        "Saturn": ["Capricorn", "Aquarius", "Libra", "Taurus", "Gemini", "Virgo"],
        "Rahu": ["Gemini", "Virgo", "Aquarius", "Pisces"],
        "Ketu": ["Sagittarius", "Pisces", "Scorpio"]
    }
    
    # Enemy signs
    ENEMY_SIGNS = {
        "Sun": ["Libra", "Capricorn", "Aquarius", "Taurus"],
        "Moon": ["Scorpio", "Capricorn", "Aquarius"],
        "Mars": ["Gemini", "Virgo", "Libra"],
        "Mercury": ["Pisces", "Sagittarius", "Aries", "Scorpio"],
        "Jupiter": ["Capricorn", "Gemini", "Virgo", "Taurus"],
        "Venus": ["Virgo", "Aries", "Scorpio", "Leo"],
        "Saturn": ["Aries", "Leo", "Cancer", "Scorpio"],
        "Rahu": ["Aries", "Scorpio", "Leo"],
        "Ketu": ["Gemini", "Virgo", "Taurus"]
    }

    # --------------------------------------------------
    # MAIN EVALUATION
    # --------------------------------------------------
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Optional[Dict[str, Dict]] = None,
        vedic_houses: Optional[List[Dict]] = None,
        **kwargs
    ) -> EvaluationResult:

        self.reset()
        result = EvaluationResult()

        # ═══════════════════════════════════════════════════════
        # STEP 0: Choose Data Source for House Lord Analysis
        # ═══════════════════════════════════════════════════════
        analysis_planets = vedic_planets if vedic_planets else planets
        analysis_houses = vedic_houses if vedic_houses else houses

        logger.info(f"🌟 Using {'VEDIC' if vedic_planets else 'KP'} data for house lord analysis")
        if vedic_planets:
            logger.warning(f"   Vedic planets count: {len(vedic_planets)}")
        if vedic_houses:
            logger.warning(f"   Vedic houses count: {len(analysis_houses)}")

        # ═══════════════════════════════════════════════════════
        # STEP 1: Get Question-Specific Houses
        # ═══════════════════════════════════════════════════════
        question_text = kwargs.get("question", "")

        house_config = get_houses_for_question(
            self.domain,
            self.subtopic,
            question_text
        )

        if house_config:
            primary_houses = house_config["primary"]
            secondary_houses = house_config["secondary"]
            all_relevant_houses = primary_houses | secondary_houses
            logger.info(f"📊 Analyzing {len(all_relevant_houses)} question-specific houses")
            logger.info(f"   Primary: {sorted(primary_houses)}")
            logger.info(f"   Secondary: {sorted(secondary_houses)}")
            logger.info(f"   Source: {house_config.get('source', 'unknown')}")
        else:
            logger.warning(f"No config for question, using fallback")
            all_relevant_houses = self.HEALTH_HOUSES
            primary_houses = {1, 6, 8}
            secondary_houses = {5, 11, 12}

        # Get metadata
        meta: QueryMeta = kwargs.get("meta")
        sub_subdomain: str = kwargs.get("sub_subdomain", "")

        meta_query_type = None
        if meta:
            if isinstance(meta, dict):
                meta_query_type = meta.get("type")
            else:
                meta_query_type = meta.query_type if hasattr(meta, 'query_type') else None

        logger.info("=" * 80)
        logger.info("PHYSICAL AND MENTAL HEALTH EVALUATOR (ENHANCED v3.1)")
        logger.info("=" * 80)
        logger.info(f"Domain: {self.domain}")
        logger.info(f"Subtopic: {self.subtopic}")
        logger.info(f"Sub-subdomain: '{sub_subdomain}'")
        logger.info(f"Query type: {meta_query_type}")
        logger.info(f"Primary houses: {sorted(primary_houses)}")
        logger.info(f"Secondary houses: {sorted(secondary_houses)}")
        logger.info("=" * 80)

        # ═══════════════════════════════════════════════════════
        # STEP 2: Calculate Aspects (on analysis data)
        # ═══════════════════════════════════════════════════════
        detect_aspects(analysis_planets)
        detect_aspects(planets)


        logger.warning(f"checking KP planet aspects: {planets}")
        aspects_data = {}
        if HOUSE_LORDS_AVAILABLE:
            try:
                aspects_data = calculate_planetary_aspects(analysis_planets)
                logger.info(f"✅ Calculated aspects for {len(aspects_data)} planets")
            except Exception as e:
                logger.warning(f"Could not calculate aspects: {e}")

        # ═══════════════════════════════════════════════════════
        # STEP 3: Extract House Lords Data (using Vedic data)
        # ═══════════════════════════════════════════════════════
        house_lords_info = self._extract_house_lords(
            analysis_houses,
            analysis_planets,
            all_relevant_houses,
            primary_houses
        )

        logger.info(f"✅ Extracted lord data for {len(house_lords_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 4: Extract Aspects on Houses (using analysis data)
        # ═══════════════════════════════════════════════════════
        house_aspects_info = self._extract_aspects_on_houses(
            analysis_houses,
            analysis_planets,
            aspects_data,
            all_relevant_houses
        )

        logger.info(f"✅ Extracted aspects for {len(house_aspects_info)} houses")

        # ═══════════════════════════════════════════════════════
        # STEP 5: Extract Timing Windows (FIXED - Handles TimingWindow objects!)
        # ═══════════════════════════════════════════════════════
        timing_windows_raw = kwargs.get("timing_windows", {})

        # DEBUG logging
        logger.error(f"🔍 DEBUG: timing_windows_raw type: {type(timing_windows_raw)}")
        logger.error(f"🔍 DEBUG: timing_windows_raw keys: {list(timing_windows_raw.keys()) if isinstance(timing_windows_raw, dict) else 'N/A'}")
        logger.error(f"🔍 DEBUG: sub_subdomain: '{sub_subdomain}'")

        # Handle both dict (keyed by sub-subdomain) and list formats
        timing_windows_list = []
        if isinstance(timing_windows_raw, dict):
            # Try exact match first
            timing_windows_list = timing_windows_raw.get(sub_subdomain, [])
            logger.info(f"📅 Timing windows structure: dict with keys {list(timing_windows_raw.keys())}")
            logger.info(f"🔍 DEBUG: Found {len(timing_windows_list)} windows for '{sub_subdomain}'")

            # Fallback: try common health-related keys
            if not timing_windows_list:
                for key in ["Disease Occurrence", "Cure Timing", "Health Risks and Surgery Timing"]:
                    if key in timing_windows_raw:
                        timing_windows_list = timing_windows_raw[key]
                        logger.info(f"🔍 DEBUG: Using '{key}' fallback key, found {len(timing_windows_list)} windows")
                        break
        else:
            # Treat as list directly
            timing_windows_list = timing_windows_raw if timing_windows_raw else []
            logger.error(f"📅 Timing windows structure: list with {len(timing_windows_list)} windows")

        # ✅ FIXED: Now handles TimingWindow objects!
        timing_windows_data = self._extract_timing_windows(timing_windows_list)

        if timing_windows_data and timing_windows_data.get('has_timing'):
            best = timing_windows_data.get('best_window', {})
            nearest = timing_windows_data.get('nearest_window', {})
            logger.warning(f"✅ TIMING WINDOWS SUCCESSFULLY EXTRACTED:")
            logger.warning(f"   🏆 BEST: {best.get('dasha', 'N/A')} ({best.get('start', 'N/A')} to {best.get('end', 'N/A')}) - Score: {best.get('final_score', 0):.1f}")
            logger.warning(f"   ⏰ NEAREST: {nearest.get('dasha', 'N/A')} ({nearest.get('start', 'N/A')} to {nearest.get('end', 'N/A')}) - Score: {nearest.get('final_score', 0):.1f}")
        else:
            logger.error(f"❌ No timing windows available for '{sub_subdomain}'")

        # ═══════════════════════════════════════════════════════
        # STEP 5.5: Generate Surgery Timing Significator Proof (NEW!)
        # ═══════════════════════════════════════════════════════
        hospitalization_timing_proof = {}
        if sub_subdomain in {"Health Risks and Surgery Timing", "Disease Occurrence", "Cure Timing"}:
            if timing_windows_data and timing_windows_data.get('has_timing'):
                hospitalization_timing_proof = self._generate_hospitalization_timing_proof(
                    planets=planets,
                    houses=houses,
                    timing_windows_data=timing_windows_data
                )
                logger.info(f"✅ Generated surgery timing significator proof")
                logger.info(f"   Significator table entries: {len(hospitalization_timing_proof.get('significator_table', []))}")
                logger.info(f"   Timing proofs generated: {len(hospitalization_timing_proof.get('timing_proofs', []))}")
                
                # Store in timing_windows_data for LLM consumption
                timing_windows_data["hospitalization_proof"] = hospitalization_timing_proof

        # ═══════════════════════════════════════════════════════
        # STEP 6: Add House Analysis Points (Vedic - all subdomains)
        # ═══════════════════════════════════════════════════════
        if sub_subdomain in {"General Health Analysis", "Disease Occurrence", "Cure Timing", 
                            "Health Risks and Surgery Timing", "Organ-Specific Issues"}:
            self._add_house_analysis_points(
                result,
                house_lords_info,
                house_aspects_info,
                primary_houses
            )

        # ═══════════════════════════════════════════════════════
        # STEP 7: KP HEALTH EVALUATION
        # ═══════════════════════════════════════════════════════

        # ═══════════════════════════════════════════════════════
        # STEP 6.5: EXTRACT KP STRUCTURED DATA (DO THIS ONCE!)
        # ═══════════════════════════════════════════════════════
        # Extract structured KP data BEFORE any health evaluation
        # This will be used across all health evaluation sections
        
        kp_structured = self._extract_kp_health_structured_direct(planets, houses)
        
        if kp_structured.get("has_kp_data"):
            logger.info(f"✅ Structured KP health data extracted:")
            logger.info(f"   Houses analyzed: {list(kp_structured['csl_details'].keys())}")
            logger.info(f"   Overall verdict: {kp_structured.get('overall_verdict')}")
            logger.info(f"   Disease susceptibility: {kp_structured.get('disease_susceptibility')}")
            logger.info(f"   Recovery potential: {kp_structured.get('recovery_potential')}")
            for house_num, info in kp_structured["csl_details"].items():
                logger.info(f"   House {house_num}: CSL {info['csl']} - {info['verdict']}")
        else:
            logger.warning("⚠️ No KP cusp sub lord data found for health")

        # ═══════════════════════════════════════════════════════
        # STEP 7: KP HEALTH EVALUATION (WITH STRUCTURED DATA!)
        # ═══════════════════════════════════════════════════════

        # --------------------------------------------------
        # 7A) MENTAL HEALTH - COMPREHENSIVE KP/VEDIC ANALYSIS
        # --------------------------------------------------
        if sub_subdomain == "Mental Health Risks":
            # Advisory disclaimer
            result.add_point(
                "⚠️ IMPORTANT: Mental health concerns require professional evaluation. "
                "Astrological indicators show tendencies and sensitivities, NOT diagnoses. "
                "Please consult a psychiatrist or psychologist for proper assessment."
            )
            
            # ✅ NEW: Comprehensive mental health analysis
            mental_health_analysis = self._evaluate_mental_health_indicators(
                planets=planets,
                houses=houses,
                vedic_planets=analysis_planets,
                vedic_houses=analysis_houses
            )
            
            # Add mental health analysis points
            if mental_health_analysis.get("has_analysis"):
                # Moon analysis (MOST IMPORTANT)
                moon_analysis = mental_health_analysis.get("moon_analysis", {})
                if moon_analysis:
                    strength_marker = "✅" if moon_analysis.get("strength", 0) >= 60 else "⚠️"
                    result.add_point(
                        f"{strength_marker} MOON (Mind/Emotions): {moon_analysis.get('summary', 'Analysis unavailable')}"
                    )
                
                # Mercury analysis (Nervous System)
                mercury_analysis = mental_health_analysis.get("mercury_analysis", {})
                if mercury_analysis:
                    strength_marker = "✅" if mercury_analysis.get("strength", 0) >= 60 else "⚠️"
                    result.add_point(
                        f"{strength_marker} MERCURY (Nervous System): {mercury_analysis.get('summary', 'Analysis unavailable')}"
                    )
                
                # Rahu analysis (Anxiety/Addiction)
                rahu_analysis = mental_health_analysis.get("rahu_analysis", {})
                if rahu_analysis:
                    affliction_marker = "⚠️" if rahu_analysis.get("is_afflicting") else "○"
                    result.add_point(
                        f"{affliction_marker} RAHU (Anxiety/Obsession): {rahu_analysis.get('summary', 'Analysis unavailable')}"
                    )
                
                # House analysis
                for house_num in [4, 5, 8, 12]:
                    house_info = mental_health_analysis.get("house_analysis", {}).get(house_num)
                    if house_info:
                        result.add_point(
                            f"🏠 House {house_num} ({self.MENTAL_HEALTH_HOUSE_MEANINGS.get(house_num, '')}): "
                            f"{house_info.get('summary', 'Analysis unavailable')}"
                        )
                
                # Overall mental health verdict (Vedic-only)
                overall_verdict = mental_health_analysis.get("overall_verdict", "")
                if overall_verdict:
                    result.add_point(f"📊 Overall Mental Health Indicators: {overall_verdict}")

            # Store structured data
            result.additional_data["mental_health_analysis"] = mental_health_analysis
            result.additional_data["kp_health_analysis"] = kp_structured
            
            # Store data for LLM
            self._store_data_for_llm(
                result,
                house_config,
                house_lords_info,
                house_aspects_info,
                primary_houses,
                secondary_houses,
                timing_windows_data
            )
            return result

        # --------------------------------------------------
        # 7B) GENERAL HEALTH ANALYSIS
        # --------------------------------------------------
        if sub_subdomain == "General Health Analysis":
            try:
                health_text_points = evaluate_health(planets, houses)
                logger.warning(f"🔍 evaluate_health() returned {len(health_text_points)} health points")
                
                # ✅ NEW: Add points with "KP:" prefix for KP-related points
                if health_text_points:
                    logger.warning(f"🔍 First health point: {health_text_points[0]}")
                    for p in health_text_points:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)
                else:
                    result.add_point(
                        "❓ Health indicators unclear from KP analysis. "
                        "No strong cusp sub lord significations detected for health houses."
                    )
            except Exception as e:
                logger.warning(f"Health evaluation error: {e}")
                result.add_point(
                    "Health evaluation could not be completed due to internal rule constraints."
                )

        # --------------------------------------------------
        # 7C) DISEASE OCCURRENCE (TIMING / RISK)
        # --------------------------------------------------
        elif sub_subdomain == "Disease Occurrence":
            try:
                health_text_points = evaluate_health(planets, houses)
                disease_points = [p for p in health_text_points if "⚠️" in p or "☠️" in p or "disease" in p.lower() or "afflict" in p.lower()]
                
                logger.warning(f"🔍 Disease-related points: {len(disease_points)}")
                
                # ✅ NEW: Add "KP:" prefix
                for p in disease_points:
                    if self._is_kp_point(p):
                        result.add_point(f"KP: {p}")
                    else:
                        result.add_point(p)

                if not disease_points:
                    result.add_point("No strong disease-triggering indicators found in classical KP rules.")
            except Exception as e:
                logger.warning(f"Disease evaluation error: {e}")
                result.add_point("Disease evaluation could not be completed.")

        # --------------------------------------------------
        # 7D) CURE / RECOVERY TIMING
        # --------------------------------------------------
        elif sub_subdomain == "Cure Timing":
            try:
                health_text_points = evaluate_health(planets, houses)
                cure_points = [p for p in health_text_points if "🌱" in p or "🟢" in p or "cure" in p.lower() or "recovery" in p.lower() or "heal" in p.lower()]
                
                logger.warning(f"🔍 Cure-related points: {len(cure_points)}")
                
                # ✅ NEW: Add "KP:" prefix
                for p in cure_points:
                    if self._is_kp_point(p):
                        result.add_point(f"KP: {p}")
                    else:
                        result.add_point(p)

                if not cure_points:
                    result.add_point(
                        "Recovery indicators are moderate; cure depends on treatment consistency "
                        "and medical guidance."
                    )
            except Exception as e:
                logger.warning(f"Cure evaluation error: {e}")
                result.add_point("Cure timing evaluation could not be completed.")

        # --------------------------------------------------
        # 7E) HEALTH RISKS AND SURGERY TIMING
        # --------------------------------------------------
        elif sub_subdomain == "Health Risks and Surgery Timing":
            try:
                health_text_points = evaluate_health(planets, houses)
                risk_points = [p for p in health_text_points if "⚠️" in p or "risk" in p.lower() or "surgery" in p.lower() or "8th" in p.lower()]
                
                logger.warning(f"🔍 Risk/Surgery-related points: {len(risk_points)}")
                
                # ✅ NEW: Add "KP:" prefix
                for p in risk_points:
                    if self._is_kp_point(p):
                        result.add_point(f"KP: {p}")
                    else:
                        result.add_point(p)

                if not risk_points:
                    result.add_point(
                        "No strong surgical or major health risk indicators detected. "
                        "Regular check-ups recommended for preventive care."
                    )
            except Exception as e:
                logger.warning(f"Health risk evaluation error: {e}")
                result.add_point("Health risk evaluation could not be completed.")

        # --------------------------------------------------
        # 7F) ORGAN-SPECIFIC ISSUES (EYES + SPEECH)
        # --------------------------------------------------
        elif sub_subdomain == "Organ-Specific Issues":
            try:
                eye = evaluate_eye_risks(planets, houses)
                speech = evaluate_speech(planets, houses)

                if eye:
                    result.add_point("🔷 Eye / Vision Indicators:")
                    for p in eye:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)

                if speech:
                    result.add_point("🗣️ Speech / Voice Indicators:")
                    for p in speech:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)

                if not eye and not speech:
                    result.add_point("No strong organ-specific KP indicators detected.")
            except Exception as e:
                logger.warning(f"Organ-specific evaluation error: {e}")
                result.add_point("Organ-specific evaluation could not be completed.")

        # --------------------------------------------------
        # 7G) REMEDIES & SUGGESTIONS
        # --------------------------------------------------
        elif sub_subdomain in {"Remedies And Suggestions", "Health Remedies"}:
            try:
                report = generate_full_health_report(planets, houses)
                remedy_lines = [line for line in report if "Remedy" in line or "🟢" in line or "strengthen" in line.lower()]

                for line in remedy_lines:
                    # Remedies usually aren't KP-specific, but check anyway
                    if self._is_kp_point(line):
                        result.add_point(f"KP: {line}")
                    else:
                        result.add_point(line)

                if not remedy_lines:
                    result.add_point(
                        "General health improvement is supported through discipline, "
                        "balanced routine, and professional medical advice."
                    )
            except Exception as e:
                logger.warning(f"Remedies evaluation error: {e}")
                result.add_point("Remedies evaluation could not be completed.")

        # --------------------------------------------------
        # 7H) FALLBACK
        # --------------------------------------------------
        else:
            try:
                health_text_points = evaluate_health(planets, houses)
                if health_text_points:
                    for p in health_text_points:
                        if self._is_kp_point(p):
                            result.add_point(f"KP: {p}")
                        else:
                            result.add_point(p)
                else:
                    result.add_point(
                        "Health analysis completed using classical KP indicators. "
                        "No specific sub-category was requested."
                    )
            except Exception as e:
                logger.warning(f"Fallback health evaluation error: {e}")
                result.add_point(
                    "Health analysis completed. Please consult with medical professionals for specific concerns."
                )

        # ═══════════════════════════════════════════════════════
        # STEP 7.5: STORE STRUCTURED KP DATA (DO THIS ONCE!)
        # ═══════════════════════════════════════════════════════
        # Store the structured KP data we extracted earlier
        result.additional_data["kp_health_analysis"] = kp_structured

        # ═══════════════════════════════════════════════════════
        # STEP 8: Store Enhanced Data for LLM
        # ═══════════════════════════════════════════════════════
        self._store_data_for_llm(
            result,
            house_config,
            house_lords_info,
            house_aspects_info,
            primary_houses,
            secondary_houses,
            timing_windows_data
        )
        logger.warning(f"✅ Data prepared for LLM consumption: {result}")
        return result




    def _extract_kp_health_structured_direct(self, planets: Dict, houses: List) -> Dict:
        """
        Extract structured KP health data DIRECTLY from cusp sub lords.
        
        This is independent of health_engine text output - extracts raw cusp data
        and creates structured format for deterministic LLM consumption.
        
        Returns structured dict with:
        - csl_details: Dict keyed by house number
        - overall_verdict: Health assessment
        - disease_susceptibility: Risk level
        - recovery_potential: Healing capacity
        - key_findings: List of discoveries
        """
        from app.core.astro_constants import normalize_planet_name, get_signified_score, get_planet

        kp_data = {
            "csl_details": {},
            "overall_verdict": "UNKNOWN",
            "disease_susceptibility": "UNKNOWN",
            "recovery_potential": "UNKNOWN",
            "key_findings": [],
            "has_kp_data": False
        }
        
        # Health-relevant houses
        health_houses = [1, 6, 8, 11, 12, 5]
        house_meanings = {
            1: "Vitality/Constitution",
            5: "Mental Peace/Recovery Support",
            6: "Disease/Illness",
            8: "Chronic Issues/Longevity",
            11: "Recovery/Cure",
            12: "Hospitalization/Confinement"
        }
        
        # Extract CSL for each health house
        for house_num in health_houses:
            house_data = next((h for h in houses if h.get("house") == house_num), None)
            
            if not house_data:
                continue
            
            # Get cusp sub lord
            csl_raw = house_data.get("cusp_sub_lord", "")
            if not csl_raw:
                continue
            
            csl = normalize_planet_name(csl_raw) or csl_raw
            
            if not csl:
                continue
            
            kp_data["has_kp_data"] = True

            # Get cusp sign
            cusp_sign = (
                house_data.get("start_rasi", "") or
                house_data.get("rasi", "") or
                house_data.get("sign", "")
            )

            # Secondary info: generic planet nature (kept for reference only — NOT used for verdict)
            benefics = {"Venus", "Jupiter", "Mercury", "Moon"}
            malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}
            is_benefic = csl in benefics
            is_malefic = csl in malefics

            # ─────────────────────────────────────────────────────────────
            # KP SIGNIFICATION-BASED VERDICT (v4.0 — Classical KP Logic)
            # Verdict is determined by what houses the CSL signifies
            # through its chain (occupation → star lord → sub lord),
            # NOT by whether the planet is generically benefic/malefic.
            # ─────────────────────────────────────────────────────────────
            try:
                signified_list = get_signified_houses(csl, planets, houses)
                signified = set(signified_list)
            except Exception:
                signified_list = []
                signified = set()

            # ── Build chain breakdown for display (star lord → sub lord chain) ──
            chain_breakdown = {}
            try:
                score_map = get_signified_score(csl, planets, houses)
                csl_planet_obj = get_planet(csl, planets) or {}
                star_lord = normalize_planet_name(
                    csl_planet_obj.get("nakshatra_lord") or csl_planet_obj.get("nak_lord") or ""
                ) or ""
                sub_lord = normalize_planet_name(
                    csl_planet_obj.get("sub_lord") or ""
                ) or ""
                own_house = csl_planet_obj.get("house")

                star_lord_obj = get_planet(star_lord, planets) or {} if star_lord else {}
                sub_lord_obj = get_planet(sub_lord, planets) or {} if sub_lord else {}

                chain_breakdown = {
                    "csl_own_house": own_house,
                    "star_lord": star_lord,
                    "star_lord_house": star_lord_obj.get("house") if star_lord_obj else None,
                    "sub_lord": sub_lord,
                    "sub_lord_house": sub_lord_obj.get("house") if sub_lord_obj else None,
                    "score_map": {k: round(v, 1) for k, v in score_map.items()},
                }
            except Exception as e:
                logger.debug(f"Chain breakdown failed for {csl}: {e}")

            # Health house groups
            vitality_houses  = {1, 5, 11}   # constitution, recovery support, fulfillment
            disease_houses   = {6, 8, 12}    # illness, chronic, hospitalization

            vitality_count = len(signified & vitality_houses)
            disease_count  = len(signified & disease_houses)

            verdict = "NEUTRAL"
            interpretation = ""
            signified_display = sorted(signified) if signified else []

            if house_num == 1:  # Vitality/Constitution
                # KP Rule:
                #   STRONG_VITALITY  → vitality (1/5/11) dominant AND no disease house (6/8) present
                #   MODERATE_VITALITY → vitality dominant BUT any disease house (6/8) also present (mixed)
                #                       OR equal counts
                #   WEAK_VITALITY    → disease (6/8/12) dominant; or 6+8 both present regardless of count
                both_major_disease = {6, 8}.issubset(signified)
                has_disease = bool(disease_houses & signified)
                if vitality_count > disease_count and not has_disease:
                    verdict = "STRONG_VITALITY"
                    interpretation = (
                        f"{csl} as 1st CSL signifies houses {signified_display} "
                        f"[Rule: vitality houses {sorted(signified & vitality_houses)} present, no disease houses → good constitution] "
                        f"→ STRONG_VITALITY"
                    )
                elif disease_count > vitality_count or (disease_count == vitality_count and both_major_disease):
                    verdict = "WEAK_VITALITY"
                    interpretation = (
                        f"{csl} as 1st CSL signifies houses {signified_display} "
                        f"[Rule: disease houses {sorted(signified & disease_houses)} dominant → reduced vitality] "
                        f"→ WEAK_VITALITY"
                    )
                elif not signified:
                    verdict = "MODERATE_VITALITY"
                    interpretation = (
                        f"{csl} as 1st CSL — signification data unavailable; "
                        f"moderate constitution assumed (insufficient chain data)"
                    )
                else:
                    # vitality dominant but disease houses also present → mixed → MODERATE
                    verdict = "MODERATE_VITALITY"
                    interpretation = (
                        f"{csl} as 1st CSL signifies houses {signified_display} "
                        f"[Rule: vitality {sorted(signified & vitality_houses)} present but disease houses {sorted(signified & disease_houses)} also signified → sensitive constitution] "
                        f"→ MODERATE_VITALITY"
                    )

            elif house_num == 5:  # Mental Peace/Recovery Support
                # KP Rule:
                #   EXCELLENT_MENTAL_PEACE → vitality (1/5/11) dominant AND no disease house (6/8/12) present
                #   MODERATE_MENTAL_STATE  → vitality dominant BUT disease houses also present (mixed)
                #                            OR equal counts
                #   MENTAL_STRESS          → disease (6/8/12) dominant (more disease than vitality)
                has_disease_5 = bool(disease_houses & signified)
                if vitality_count > disease_count and not has_disease_5:
                    verdict = "EXCELLENT_MENTAL_PEACE"
                    interpretation = (
                        f"{csl} as 5th CSL signifies houses {signified_display} "
                        f"[Rule: vitality houses {sorted(signified & vitality_houses)} present, no disease houses → mental peace supported] "
                        f"→ EXCELLENT_MENTAL_PEACE"
                    )
                elif disease_count > vitality_count:
                    verdict = "MENTAL_STRESS"
                    interpretation = (
                        f"{csl} as 5th CSL signifies houses {signified_display} "
                        f"[Rule: disease houses {sorted(signified & disease_houses)} dominant → emotional sensitivity tendency] "
                        f"→ MENTAL_STRESS"
                    )
                elif not signified:
                    verdict = "MODERATE_MENTAL_STATE"
                    interpretation = (
                        f"{csl} as 5th CSL — signification data unavailable; "
                        f"moderate mental state assumed"
                    )
                else:
                    # vitality dominant but disease houses also present, OR equal counts → MODERATE
                    verdict = "MODERATE_MENTAL_STATE"
                    interpretation = (
                        f"{csl} as 5th CSL signifies houses {signified_display} "
                        f"[Rule: vitality {sorted(signified & vitality_houses)} present but disease houses {sorted(signified & disease_houses)} also signified → mixed mental state] "
                        f"→ MODERATE_MENTAL_STATE"
                    )

            elif house_num == 6:  # Disease/Illness
                # KP Rule for 6th CSL (uses COUNT comparison, not just boolean):
                #   DISEASE_PRONE     → disease (6/8/12) count > vitality (1/5/11) count
                #                       OR disease houses present with NO vitality houses
                #   MODERATE_DISEASE_RISK → disease AND vitality present but counts EQUAL
                #                           OR vitality count marginally > disease (1 more) AND both present
                #   DISEASE_RESISTANT → vitality dominant AND no disease houses present
                #                       OR vitality count significantly > disease count (2+)
                has_disease_6 = bool(disease_houses & signified)
                has_vitality_6 = bool(vitality_houses & signified)
                if has_disease_6 and has_vitality_6:
                    if disease_count > vitality_count:
                        # Disease clearly dominant — PRONE despite some vitality
                        verdict = "DISEASE_PRONE"
                        interpretation = (
                            f"{csl} as 6th CSL signifies houses {signified_display} "
                            f"[Rule: disease houses {sorted(signified & disease_houses)} outnumber vitality {sorted(signified & vitality_houses)} → disease tendency dominates] "
                            f"→ DISEASE_PRONE"
                        )
                    elif vitality_count >= disease_count + 2:
                        # Vitality clearly dominant — near RESISTANT despite some disease presence
                        verdict = "DISEASE_RESISTANT"
                        interpretation = (
                            f"{csl} as 6th CSL signifies houses {signified_display} "
                            f"[Rule: vitality houses {sorted(signified & vitality_houses)} significantly outnumber disease {sorted(signified & disease_houses)} → good immunity] "
                            f"→ DISEASE_RESISTANT"
                        )
                    else:
                        # Balanced or vitality +1 — genuinely mixed
                        verdict = "MODERATE_DISEASE_RISK"
                        interpretation = (
                            f"{csl} as 6th CSL signifies houses {signified_display} "
                            f"[Rule: disease houses {sorted(signified & disease_houses)} present WITH vitality houses {sorted(signified & vitality_houses)} (balanced) → mixed immunity] "
                            f"→ MODERATE_DISEASE_RISK"
                        )
                elif has_disease_6:
                    verdict = "DISEASE_PRONE"
                    interpretation = (
                        f"{csl} as 6th CSL signifies houses {signified_display} "
                        f"[Rule: disease houses {sorted(signified & disease_houses)} present, NO vitality houses → disease tendency] "
                        f"→ DISEASE_PRONE"
                    )
                elif has_vitality_6:
                    verdict = "DISEASE_RESISTANT"
                    interpretation = (
                        f"{csl} as 6th CSL signifies houses {signified_display} "
                        f"[Rule: vitality houses {sorted(signified & vitality_houses)} dominant, no disease houses → good immunity] "
                        f"→ DISEASE_RESISTANT"
                    )
                else:
                    verdict = "MODERATE_DISEASE_RISK"
                    interpretation = (
                        f"{csl} as 6th CSL signifies houses {signified_display} "
                        f"→ moderate health vigilance needed"
                    )

            elif house_num == 8:  # Chronic Issues/Longevity
                # KP Rule for 8th CSL:
                #   CHRONIC_VULNERABILITY → CSL connects 6+8 OR 6+12 OR 8+12 (cross-disease house link)
                #                           Requires ≥2 disease houses, or house 6 + house 8 together,
                #                           because 8 alone = longevity/surgery sensitivity, not chronic disease
                #   LONGEVITY_SENSITIVITY → only house 8 (or 12) present alone → metabolic/surgery tendency
                #   PROTECTED_LONGEVITY   → vitality houses (1/5/11) dominant, no cross-disease link
                #   MODERATE_LONGEVITY    → neither group dominant
                cross_disease_link = (
                    ({6, 8}.issubset(signified)) or
                    ({6, 12}.issubset(signified)) or
                    ({8, 12}.issubset(signified))
                )
                if cross_disease_link:
                    verdict = "CHRONIC_VULNERABILITY"
                    interpretation = (
                        f"{csl} as 8th CSL signifies houses {signified_display} "
                        f"[Rule: cross-disease house link {sorted(signified & disease_houses)} active → chronic disease sensitivity] "
                        f"→ CHRONIC_VULNERABILITY"
                    )
                elif disease_houses & signified:
                    # Only one disease house present (8 or 12 alone) — metabolic tendency, NOT longevity risk
                    # LONGEVITY_SENSITIVITY = health fluctuation / metabolic tendency only
                    # Do NOT interpret as life expectancy risk — that requires cross-disease link (6+8/6+12/8+12)
                    verdict = "LONGEVITY_SENSITIVITY"
                    interpretation = (
                        f"{csl} as 8th CSL signifies houses {signified_display} "
                        f"[Rule: single disease house {sorted(signified & disease_houses)} without cross-link → "
                        f"metabolic/health fluctuation tendency only, NOT longevity risk, NOT chronic disease] "
                        f"→ LONGEVITY_SENSITIVITY (= चयापचय सतर्कता; दीर्घायु खतरा नहीं)"
                    )
                elif vitality_houses & signified:
                    verdict = "PROTECTED_LONGEVITY"
                    interpretation = (
                        f"{csl} as 8th CSL signifies houses {signified_display} "
                        f"[Rule: vitality houses {sorted(signified & vitality_houses)} dominant → longevity protected] "
                        f"→ PROTECTED_LONGEVITY"
                    )
                else:
                    verdict = "MODERATE_LONGEVITY"
                    interpretation = (
                        f"{csl} as 8th CSL signifies houses {signified_display} "
                        f"→ moderate longevity indicators"
                    )

            elif house_num == 11:  # Recovery/Cure
                # KP Rule for 11th CSL:
                #   EXCELLENT_RECOVERY → vitality (1/5/11) dominant AND no disease houses present
                #   MODERATE_RECOVERY  → vitality present BUT disease houses also present (fighting ability, not clean recovery)
                #                        OR equal counts
                #   POOR_RECOVERY      → disease (6/8/12) dominant, no vitality houses
                has_vitality_11 = bool(vitality_houses & signified)
                has_disease_11 = bool(disease_houses & signified)
                if has_vitality_11 and not has_disease_11:
                    verdict = "EXCELLENT_RECOVERY"
                    interpretation = (
                        f"{csl} as 11th CSL signifies houses {signified_display} "
                        f"[Rule: vitality/gain houses {sorted(signified & vitality_houses)} active, no disease houses → strong recovery support] "
                        f"→ EXCELLENT_RECOVERY"
                    )
                elif has_vitality_11 and has_disease_11:
                    verdict = "MODERATE_RECOVERY"
                    interpretation = (
                        f"{csl} as 11th CSL signifies houses {signified_display} "
                        f"[Rule: vitality {sorted(signified & vitality_houses)} present but disease houses {sorted(signified & disease_houses)} also active → fighting ability but mixed recovery] "
                        f"→ MODERATE_RECOVERY"
                    )
                elif has_disease_11:
                    verdict = "POOR_RECOVERY"
                    interpretation = (
                        f"{csl} as 11th CSL signifies houses {signified_display} "
                        f"[Rule: disease houses {sorted(signified & disease_houses)} dominant, no vitality houses → recovery may be slow] "
                        f"→ POOR_RECOVERY"
                    )
                else:
                    verdict = "MODERATE_RECOVERY"
                    interpretation = (
                        f"{csl} as 11th CSL signifies houses {signified_display} "
                        f"→ moderate recovery potential"
                    )

            elif house_num == 12:  # Hospitalization/Confinement
                # KP Rule for 12th CSL:
                #   HIGH_HOSPITAL_RISK    → CSL signifies 12 + (6 or 8) — full disease-isolation cycle active
                #                           OR signifies all three disease houses (6+8+12)
                #   MODERATE_HOSPITAL_RISK → only house 6 OR only house 8 present (treatment tendency, not hospitalization)
                #                            OR 8+12 without 6 (chronic/surgery without active disease)
                #   LOW_HOSPITAL_RISK     → vitality houses (1/5/11) dominant, no strong disease link
                #   TREATMENT_TENDENCY    → house 6 only → medical consultations, outpatient, not hospitalization
                has_12 = 12 in signified
                has_6 = 6 in signified
                has_8 = 8 in signified
                has_vitality_12 = bool(vitality_houses & signified)

                if has_12 and (has_6 or has_8):
                    verdict = "HIGH_HOSPITAL_RISK"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"[Rule: house 12 + disease link {sorted(signified & disease_houses)} → full disease-confinement cycle active] "
                        f"→ HIGH_HOSPITAL_RISK"
                    )
                elif has_6 and has_8:
                    # 6+8 without 12 → chronic disease with treatment, moderate confinement risk
                    verdict = "MODERATE_HOSPITAL_RISK"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"[Rule: disease houses 6+8 active but house 12 absent → medical treatment tendency, moderate hospitalization] "
                        f"→ MODERATE_HOSPITAL_RISK"
                    )
                elif has_6 and not has_8 and not has_12:
                    # House 6 alone → outpatient/consultation tendency, NOT hospitalization
                    verdict = "TREATMENT_TENDENCY"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"[Rule: only house 6 present, no 8/12 → medical consultation tendency, not hospitalization risk] "
                        f"→ TREATMENT_TENDENCY"
                    )
                elif has_8 and not has_6 and not has_12:
                    verdict = "MODERATE_HOSPITAL_RISK"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"[Rule: house 8 without 6/12 → surgery/chronic sensitivity, moderate hospitalization tendency] "
                        f"→ MODERATE_HOSPITAL_RISK"
                    )
                elif has_vitality_12:
                    verdict = "LOW_HOSPITAL_RISK"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"[Rule: vitality houses {sorted(signified & vitality_houses)} dominant → low hospitalization tendency] "
                        f"→ LOW_HOSPITAL_RISK"
                    )
                else:
                    verdict = "MODERATE_HOSPITAL_RISK"
                    interpretation = (
                        f"{csl} as 12th CSL signifies houses {signified_display} "
                        f"→ average hospitalization indicators"
                    )

            # ── Combustion downgrade ──
            # KP Rule: A combust CSL cannot fully manifest its significations.
            # Downgrade the verdict one level toward the neutral/moderate outcome.
            # Retrograde is intentionally NOT applied here — retrograde in KP astrology
            # means results manifest with delay/internalization, not weakening of signification.
            try:
                csl_obj_for_combust = get_planet(csl, planets) or {}
                # Combustion flag comes from API — trust it directly
                # Moon cannot be combust in classical astrology — excluded
                is_csl_combust = (
                    csl != "Moon" and csl not in {"Rahu", "Ketu"} and
                    (
                        csl_obj_for_combust.get("is_combusted", False) or
                        csl_obj_for_combust.get("is_combust", False)
                    )
                )
                if is_csl_combust:
                    COMBUST_DOWNGRADE = {
                        # H1 verdicts
                        "STRONG_VITALITY":       "MODERATE_VITALITY",
                        "WEAK_VITALITY":         "WEAK_VITALITY",        # already worst — no change
                        # H5 verdicts
                        "EXCELLENT_MENTAL_PEACE": "MODERATE_MENTAL_STATE",
                        "MENTAL_STRESS":          "MENTAL_STRESS",        # already worst — no change
                        # H6 verdicts
                        "DISEASE_RESISTANT":     "MODERATE_DISEASE_RISK",
                        "DISEASE_PRONE":         "DISEASE_PRONE",        # already worst — no change
                        # H8 verdicts
                        "PROTECTED_LONGEVITY":   "MODERATE_LONGEVITY",
                        "CHRONIC_VULNERABILITY": "CHRONIC_VULNERABILITY", # already worst — no change
                        # H11 verdicts
                        "EXCELLENT_RECOVERY":    "MODERATE_RECOVERY",
                        "POOR_RECOVERY":         "POOR_RECOVERY",        # already worst — no change
                        # H12 verdicts
                        "LOW_HOSPITAL_RISK":     "MODERATE_HOSPITAL_RISK",
                        "HIGH_HOSPITAL_RISK":    "HIGH_HOSPITAL_RISK",   # already worst — no change
                        # Neutral verdicts — no change needed
                        "MODERATE_VITALITY":     "MODERATE_VITALITY",
                        "MODERATE_MENTAL_STATE": "MODERATE_MENTAL_STATE",
                        "MODERATE_DISEASE_RISK": "MODERATE_DISEASE_RISK",
                        "MODERATE_LONGEVITY":    "MODERATE_LONGEVITY",
                        "LONGEVITY_SENSITIVITY": "LONGEVITY_SENSITIVITY",
                        "MODERATE_RECOVERY":     "MODERATE_RECOVERY",
                        "MODERATE_HOSPITAL_RISK":"MODERATE_HOSPITAL_RISK",
                        "TREATMENT_TENDENCY":    "TREATMENT_TENDENCY",
                    }
                    original_verdict = verdict
                    verdict = COMBUST_DOWNGRADE.get(verdict, verdict)
                    if verdict != original_verdict:
                        interpretation += f" [⚠️ CSL {csl} is combust → significations weakened → downgraded from {original_verdict}]"
            except Exception:
                pass  # combustion check is best-effort

            # Health sensitivity area mapping (for prompt context)
            # NOTE: These are TENDENCIES, not predictions. Always frame as "sensitivity in..."
            DISEASE_AREA_MAP = {
                "Sun": "cardiac/eye/vitality sensitivity (tendency, not prediction)",
                "Moon": "emotional/digestive/fluid sensitivity (tendency)",
                "Mars": "inflammatory/circulatory sensitivity (tendency)",
                "Mercury": "nervous system/respiratory/skin sensitivity (tendency)",
                "Jupiter": "liver/metabolic/weight sensitivity (tendency)",
                "Venus": "kidney/reproductive/urinary sensitivity (tendency)",
                "Saturn": "bone/joint/chronic-care sensitivity (tendency)",
                "Rahu": "atypical/allergy/mystery-illness sensitivity (tendency)",
                "Ketu": "hidden/chronic/parasitic sensitivity (tendency)"
            }
            disease_area = DISEASE_AREA_MAP.get(csl, "")

            # Store structured data for this cusp
            kp_data["csl_details"][house_num] = {
                "house_meaning": house_meanings[house_num],
                "csl": csl,
                "cusp_sign": cusp_sign,
                "is_benefic": is_benefic,
                "is_malefic": is_malefic,
                "signified_houses": signified_display,
                "verdict": verdict,
                "interpretation": interpretation,
                "disease_area": disease_area,
                "chain_breakdown": chain_breakdown,
            }
            
            # Add to key findings — now includes signified houses for traceability
            signified_str = str(sorted(signified)) if signified else "[]"
            kp_data["key_findings"].append(
                f"House {house_num} ({house_meanings[house_num]}): CSL {csl} signifies {signified_str} → {verdict}"
            )

        # Determine overall health assessment
        if kp_data["csl_details"]:
            # Check critical houses: 1 (vitality), 6 (disease), 8 (chronic), 11 (recovery)
            h1_verdict = kp_data["csl_details"].get(1, {}).get("verdict", "UNKNOWN")
            h6_verdict = kp_data["csl_details"].get(6, {}).get("verdict", "UNKNOWN")
            h8_verdict = kp_data["csl_details"].get(8, {}).get("verdict", "UNKNOWN")
            h11_verdict = kp_data["csl_details"].get(11, {}).get("verdict", "UNKNOWN")

            # Overall health verdict (signification-based)
            if h1_verdict == "STRONG_VITALITY" and h6_verdict == "DISEASE_RESISTANT" and h11_verdict == "EXCELLENT_RECOVERY":
                kp_data["overall_verdict"] = "ROBUST_HEALTH"
                kp_data["key_findings"].insert(0, "KP: CSL significations show robust overall health constitution with excellent resilience")
            elif h1_verdict == "WEAK_VITALITY" or h6_verdict == "DISEASE_PRONE":
                kp_data["overall_verdict"] = "VULNERABLE_HEALTH"
                kp_data["key_findings"].insert(0, "KP: CSL significations show health vulnerabilities — preventive care advised")
            elif h8_verdict == "CHRONIC_VULNERABILITY":
                # Full cross-disease link (6+8 or 6+12) → moderate with chronic attention needed
                kp_data["overall_verdict"] = "MODERATE_WITH_CHRONIC_RISKS"
                kp_data["key_findings"].insert(0, "KP: CSL significations show moderate health with chronic condition attention needed")
            elif h8_verdict == "LONGEVITY_SENSITIVITY":
                # Single disease house in 8th CSL — metabolic/longevity sensitivity, not overt chronic disease
                kp_data["overall_verdict"] = "MODERATE_HEALTH"
                kp_data["key_findings"].insert(0, "KP: CSL significations show moderate health — metabolic/longevity sensitivity noted, regular care recommended")
            else:
                kp_data["overall_verdict"] = "MODERATE_HEALTH"
                kp_data["key_findings"].insert(0, "KP: CSL significations show moderate health constitution — regular care recommended")

            # Disease susceptibility
            if h6_verdict == "DISEASE_PRONE":
                kp_data["disease_susceptibility"] = "ELEVATED"
            elif h6_verdict == "DISEASE_RESISTANT":
                kp_data["disease_susceptibility"] = "LOW"
            else:
                kp_data["disease_susceptibility"] = "MODERATE"

            # Recovery potential
            if h11_verdict == "EXCELLENT_RECOVERY":
                kp_data["recovery_potential"] = "EXCELLENT"
            elif h11_verdict == "POOR_RECOVERY":
                kp_data["recovery_potential"] = "SLOW"
            else:
                kp_data["recovery_potential"] = "MODERATE"

            # ── Health Scores — dual system (baseline + context-specific) ──
            # baseline_score: constant across all questions (constitution-based, all 6 houses)
            # context_risk_score: disease/surgery context (H6+H8+H12 only)
            # mental_wellbeing_score: mental health context (H5+H1 only)
            health_score_data = self._calculate_health_scores(kp_data["csl_details"])
            kp_data["health_score"] = health_score_data
            # Expose individual scores at top level for easy access in prompts
            kp_data["baseline_health_score"] = health_score_data["baseline_score"]
            kp_data["context_risk_score"] = health_score_data["context_risk_score"]
            kp_data["mental_wellbeing_score"] = health_score_data["mental_wellbeing_score"]

            # ── Confidence Level — how many CSLs had signification data ──
            supporting = sum(
                1 for info in kp_data["csl_details"].values()
                if info.get("signified_houses")
            )
            total = len(kp_data["csl_details"])
            if supporting >= 4:
                confidence = "High"
            elif supporting >= 2:
                confidence = "Medium"
            else:
                confidence = "Low"
            kp_data["confidence_level"] = f"{confidence} (signification data for {supporting}/{total} health houses)"

        # ── Lagna Lord & Moon Strength (primary health indicators) ──
        try:
            lagna_moon = self._extract_lagna_moon_strength(planets, houses)
            kp_data["lagna_moon_strength"] = lagna_moon
        except Exception as e:
            logger.warning(f"Could not extract lagna/moon strength: {e}")

        # ── Functional Benefic/Malefic based on Ascendant (KP/Vedic context) ──
        # This tells the LLM NOT to treat Saturn/Rahu/Mars as always harmful —
        # their role depends on which houses they rule from the ascendant.
        try:
            from app.core.astro_constants import SIGN_LORDS
            lagna_house = next((h for h in houses if h.get("house") == 1), None)
            lagna_sign = ""
            if lagna_house:
                lagna_sign = (
                    lagna_house.get("start_rasi") or
                    lagna_house.get("rasi") or
                    lagna_house.get("sign", "")
                )
            # Functional role tables — which planets own kendra/trikona vs trik houses
            # (simplified: kendra=1,4,7,10; trikona=1,5,9; trik=6,8,12)
            FUNCTIONAL_ROLE_BY_LAGNA = {
                # Each entry: benefic = kendra/trikona lords, malefic = 6/8/12 lords or kendradhipati
                # mixed = dual lordship (one benefic house + one dusthana house)
                "Aries":       {"benefic": ["Sun", "Moon", "Mars", "Jupiter"], "malefic": ["Mercury", "Saturn", "Venus", "Rahu", "Ketu"]},
                "Taurus":      {"benefic": ["Mercury", "Saturn", "Venus"], "malefic": ["Jupiter", "Moon", "Rahu", "Ketu"]},
                "Gemini":      {"benefic": ["Venus", "Saturn"], "malefic": ["Jupiter", "Mars", "Sun", "Rahu", "Ketu"]},
                "Cancer":      {"benefic": ["Moon", "Mars", "Jupiter"], "malefic": ["Mercury", "Saturn", "Venus", "Rahu", "Ketu"]},
                "Leo":         {"benefic": ["Sun", "Mars", "Jupiter"], "malefic": ["Mercury", "Saturn", "Venus", "Rahu", "Ketu"]},
                # Virgo: Saturn owns 5th (trikona=benefic) AND 6th (dusthana=malefic) → mixed/neutral
                "Virgo":       {"benefic": ["Mercury", "Venus"], "malefic": ["Moon", "Mars", "Jupiter", "Rahu", "Ketu"], "mixed": ["Saturn"]},
                "Libra":       {"benefic": ["Mercury", "Saturn", "Venus"], "malefic": ["Jupiter", "Sun", "Moon", "Rahu", "Ketu"]},
                "Scorpio":     {"benefic": ["Moon", "Mars", "Jupiter", "Sun"], "malefic": ["Mercury", "Saturn", "Venus", "Rahu", "Ketu"]},
                "Sagittarius": {"benefic": ["Sun", "Mars", "Jupiter"], "malefic": ["Mercury", "Saturn", "Venus", "Rahu", "Ketu"]},
                "Capricorn":   {"benefic": ["Mercury", "Saturn", "Venus"], "malefic": ["Moon", "Jupiter", "Mars", "Rahu", "Ketu"]},
                "Aquarius":    {"benefic": ["Mercury", "Saturn", "Venus"], "malefic": ["Moon", "Jupiter", "Mars", "Sun", "Rahu", "Ketu"]},
                "Pisces":      {"benefic": ["Moon", "Mars", "Jupiter"], "malefic": ["Mercury", "Saturn", "Venus", "Sun", "Rahu", "Ketu"]},
            }
            functional_roles = FUNCTIONAL_ROLE_BY_LAGNA.get(lagna_sign, {})
            if functional_roles:
                func_mixed = functional_roles.get("mixed", [])
                kp_data["functional_roles"] = {
                    "lagna_sign": lagna_sign,
                    "functional_benefics": functional_roles.get("benefic", []),
                    "functional_malefics": functional_roles.get("malefic", []),
                    "functional_mixed": func_mixed,
                    "note": (
                        f"For {lagna_sign} lagna: functional benefics = {functional_roles.get('benefic', [])} "
                        f"(own kendra/trikona); functional malefics = {functional_roles.get('malefic', [])} "
                        f"(own 6/8/12 or dual-lordship issues)"
                        + (f"; functional mixed (dual ownership trikona+dusthana) = {func_mixed}" if func_mixed else "")
                        + ". IMPORTANT: Even a 'malefic' planet like Saturn or Rahu can show STRONG_VITALITY "
                        f"if its KP significations favour houses 1/5/11. Mixed planets must be judged by KP significations only."
                    )
                }
            else:
                kp_data["functional_roles"] = {
                    "lagna_sign": lagna_sign or "Unknown",
                    "note": (
                        "Lagna sign not identified — use KP signification-based verdicts only. "
                        "Do NOT assume Saturn/Rahu/Mars are negative by nature."
                    )
                }
        except Exception as e:
            logger.warning(f"Functional role computation failed: {e}")
            kp_data["functional_roles"] = {
                "note": "Functional roles not computed — rely on KP signification verdicts only."
            }

        return kp_data
    
    def _calculate_health_scores(self, csl_details: Dict) -> Dict:
        """
        Compute a dual-score health system:

        1. baseline_health_score (constant — same for all questions in this chart)
           Derived from ALL 6 KP health houses (H1,H5,H6,H8,H11,H12).
           Represents the person's UNDERLYING constitutional health.
           This score NEVER changes per question — it reflects the birth chart.

        2. context_risk_score (variable — depends on which houses are activated)
           Derived from DISEASE + RECOVERY houses only (H6, H8, H12):
           - Higher H6/H8/H12 activation → higher risk score (bad = higher number)
           Used to give a question-specific risk level to surgery/hospitalisation.

        3. mental_wellbeing_score (variable — H5 + H1 context)
           Derived from H5 (mental peace CSL) + H1 (constitution) only.
           Used to give a mental-health-specific score.

        Base: 50 (neutral starting point)
        Score is clamped to [0, 100].
        """
        verdict_map = {
            # Constitution (H1)
            "STRONG_VITALITY":        +10,
            "WEAK_VITALITY":          -10,
            "MODERATE_VITALITY":        0,
            # Disease tendency (H6)
            "DISEASE_RESISTANT":       +8,
            "DISEASE_PRONE":          -10,
            "MODERATE_DISEASE_RISK":    0,
            # Recovery (H11)
            "EXCELLENT_RECOVERY":      +8,
            "POOR_RECOVERY":           -8,
            "MODERATE_RECOVERY":        0,
            # Longevity (H8)
            "PROTECTED_LONGEVITY":     +5,
            "CHRONIC_VULNERABILITY":  -10,
            "LONGEVITY_SENSITIVITY":   -3,   # single disease house — mild metabolic sensitivity
            "MODERATE_LONGEVITY":       0,
            # Hospital (H12)
            "LOW_HOSPITAL_RISK":       +5,
            "HIGH_HOSPITAL_RISK":      -8,
            "MODERATE_HOSPITAL_RISK":   0,
            "TREATMENT_TENDENCY":      -2,   # outpatient/consultation tendency, not hospitalization
            # Mental (H5)
            "EXCELLENT_MENTAL_PEACE":  +5,
            "MENTAL_STRESS":           -5,
            "MODERATE_MENTAL_STATE":    0,
        }

        # ── 1. BASELINE health score (all 6 houses) — CONSTANT across questions ──
        baseline = 50
        for house_num, info in csl_details.items():
            delta = verdict_map.get(info.get("verdict", ""), 0)
            baseline += delta
        baseline = max(0, min(100, baseline))

        if baseline >= 75:
            baseline_label = "मजबूत संविधान — आम तौर पर अच्छा स्वास्थ्य"
        elif baseline >= 55:
            baseline_label = "मध्यम-अच्छा संविधान — कुछ क्षेत्रों पर ध्यान दें"
        elif baseline >= 40:
            baseline_label = "मध्यम — नियमित निवारक देखभाल सलाहित"
        else:
            baseline_label = "कमजोर संविधान — नियमित स्वास्थ्य ध्यान आवश्यक"

        # ── 2. CONTEXT risk score (H6 + H8 + H12 only) — surgery/disease context ──
        # Risk score: starts at 50; disease verdicts push it higher (worse = higher number)
        disease_houses = {6, 8, 12}
        risk = 50
        disease_verdict_map = {
            "DISEASE_RESISTANT":      -10,   # less risk
            "DISEASE_PRONE":          +10,   # more risk
            "MODERATE_DISEASE_RISK":    0,
            "PROTECTED_LONGEVITY":    -8,
            "CHRONIC_VULNERABILITY":  +10,
            "LONGEVITY_SENSITIVITY":   +3,   # mild metabolic sensitivity
            "MODERATE_LONGEVITY":       0,
            "LOW_HOSPITAL_RISK":       -8,
            "HIGH_HOSPITAL_RISK":      +10,
            "MODERATE_HOSPITAL_RISK":   0,
            "TREATMENT_TENDENCY":       +2,  # mild outpatient tendency
        }
        for house_num, info in csl_details.items():
            if house_num in disease_houses:
                delta = disease_verdict_map.get(info.get("verdict", ""), 0)
                risk += delta
        risk = max(0, min(100, risk))

        if risk >= 70:
            risk_label = "उच्च संवेदनशीलता — विशेष सावधानी आवश्यक"
        elif risk >= 50:
            risk_label = "मध्यम संवेदनशीलता — सतर्कता रखें"
        else:
            risk_label = "निम्न संवेदनशीलता — सामान्य सावधानी पर्याप्त"

        # ── 3. MENTAL wellbeing score (H5 + H1 only) — mental health context ──
        mental_houses = {1, 5}
        mental_score = 50
        mental_verdict_map = {
            "EXCELLENT_MENTAL_PEACE": +15,
            "MODERATE_MENTAL_STATE":    0,
            "MENTAL_STRESS":          -15,
            "STRONG_VITALITY":        +10,
            "MODERATE_VITALITY":        0,
            "WEAK_VITALITY":          -10,
        }
        for house_num, info in csl_details.items():
            if house_num in mental_houses:
                delta = mental_verdict_map.get(info.get("verdict", ""), 0)
                mental_score += delta
        mental_score = max(0, min(100, mental_score))

        if mental_score >= 65:
            mental_label = "मानसिक स्थिरता — सकारात्मक संकेत"
        elif mental_score >= 45:
            mental_label = "मध्यम मानसिक संवेदनशीलता — स्व-देखभाल सहायक"
        else:
            mental_label = "भावनात्मक संवेदनशीलता — सचेत आत्म-देखभाल आवश्यक"

        return {
            # Baseline: same for every question on this chart
            "score":          baseline,           # kept as "score" for backward compat
            "label":          baseline_label,     # kept as "label" for backward compat
            "baseline_score": baseline,
            "baseline_label": baseline_label,
            # Context scores: question-specific
            "context_risk_score":     risk,
            "context_risk_label":     risk_label,
            "mental_wellbeing_score": mental_score,
            "mental_wellbeing_label": mental_label,
        }

    def _calculate_health_score(self, csl_details: Dict) -> Dict:
        """Backward-compatible wrapper — delegates to _calculate_health_scores."""
        return self._calculate_health_scores(csl_details)

    def _extract_lagna_moon_strength(self, planets: Dict, houses: List) -> Dict:
        """
        Extract Lagna lord and Moon strength data as primary health indicators.

        Returns structured dict with lagna lord and Moon analysis.
        """
        result = {
            "lagna_lord": None,
            "lagna_lord_house": None,
            "lagna_lord_dignity": "NEUTRAL",
            "lagna_lord_strength_score": 50,
            "moon_house": None,
            "moon_sign": None,
            "moon_strength": 50,
            "moon_afflictions": [],
            "moon_protections": [],
            "summary": ""
        }

        try:
            from app.core.astro_constants import normalize_planet_name

            # ── Lagna lord ──
            lagna_house = next((h for h in houses if h.get("house") == 1), None)
            if lagna_house:
                lagna_sign = lagna_house.get("start_rasi") or lagna_house.get("rasi") or lagna_house.get("sign", "")
                from app.core.astro_constants import SIGN_LORDS
                lagna_lord = SIGN_LORDS.get(lagna_sign, "")
                if lagna_lord:
                    result["lagna_lord"] = lagna_lord
                    # Find lagna lord in planets
                    ll_planet = planets.get(lagna_lord) or next(
                        (v for k, v in planets.items() if normalize_planet_name(k) == lagna_lord), None
                    )
                    if ll_planet:
                        result["lagna_lord_house"] = ll_planet.get("house")
                        ll_sign = ll_planet.get("zodiac") or ll_planet.get("rasi") or ll_planet.get("sign") or ll_planet.get("pseudo_rasi", "")
                        dignity = self._calculate_dignity_from_sign(lagna_lord, ll_sign)
                        result["lagna_lord_dignity"] = dignity
                        dignity_score_map = {
                            "EXALTED": 90, "OWN_SIGN": 80, "FRIENDLY": 65,
                            "NEUTRAL": 50, "ENEMY": 35, "DEBILITATED": 20
                        }
                        result["lagna_lord_strength_score"] = dignity_score_map.get(dignity, 50)

            # ── Moon analysis ──
            moon_data = planets.get("Moon") or next(
                (v for k, v in planets.items() if normalize_planet_name(k) == "Moon"), None
            )
            if moon_data:
                result["moon_house"] = moon_data.get("house")
                result["moon_sign"] = (
                    moon_data.get("zodiac") or
                    moon_data.get("rasi") or
                    moon_data.get("sign") or        # standard Vedic API field
                    moon_data.get("pseudo_rasi", "")
                )
                moon_dignity = self._calculate_dignity_from_sign("Moon", result["moon_sign"] or "")
                dignity_score_map = {
                    "EXALTED": 90, "OWN_SIGN": 80, "FRIENDLY": 65,
                    "NEUTRAL": 50, "ENEMY": 35, "DEBILITATED": 20
                }
                result["moon_strength"] = dignity_score_map.get(moon_dignity, 50)

                # Moon afflictions
                # NOTE: Moon CANNOT be combust in classical astrology.
                # Use: dusthana placement, malefic aspects, debilitation, waning phase.
                if result["moon_house"] in {6, 8, 12}:
                    result["moon_afflictions"].append(f"Moon in {result['moon_house']}th house (disease/trauma/isolation house) — emotionally sensitive")
                # Waning Moon (Krishna Paksha) check via speed — waning Moon has lower speed post full-moon
                # More reliably: check if Moon's degree in its sign is between 0–14 (waxing Shukla) or 14–30 (waning Krishna)
                moon_local_deg = (moon_data.get("full_degree") or moon_data.get("global_degree") or moon_data.get("degree") or 0) % 30
                # Paksha (phase) from local degree: rough proxy — Krishna paksha when local_deg > 15
                # Better indicator is Moon's speed: negative speed = retrograde (not applicable), high speed normal
                # Use the aspects field to check for malefic aspect affliction
                aspects = moon_data.get("aspects", []) or moon_data.get("aspects_received", []) or moon_data.get("aspected_by", [])
                malefic_names = {"Saturn", "Mars", "Rahu", "Ketu"}
                # Note: Sun aspect on Moon is NOT combustion — just a conjunction/aspect
                for asp in aspects:
                    if isinstance(asp, (list, tuple)) and len(asp) >= 1:
                        asp_planet = normalize_planet_name(str(asp[0])) if asp[0] else None
                    else:
                        asp_planet = normalize_planet_name(str(asp)) if asp else None
                    if asp_planet in malefic_names:
                        result["moon_afflictions"].append(f"Moon afflicted by {asp_planet} (malefic influence on mind)")
                    elif asp_planet == "Sun":
                        result["moon_afflictions"].append("Moon in close conjunction with Sun — emotionally weakened (Krishna Paksha tendency)")
                    elif asp_planet in {"Jupiter", "Venus", "Mercury"}:
                        result["moon_protections"].append(f"Moon protected by {asp_planet} aspect")

                # Moon debilitated (Scorpio) or enemy sign
                if moon_dignity == "DEBILITATED":
                    result["moon_afflictions"].append("Moon debilitated in Scorpio — emotional sensitivity heightened, mental fluctuation possible")
                elif moon_dignity == "ENEMY":
                    result["moon_afflictions"].append("Moon in enemy sign — emotional expression constrained")
                elif moon_dignity == "EXALTED":
                    result["moon_protections"].append("Moon exalted in Taurus — emotional stability enhanced")

                # Summary
                strength = result["moon_strength"]
                if strength >= 70:
                    summary = "Moon strong — good emotional stability and mental resilience"
                elif strength >= 50:
                    summary = "Moon moderate — some emotional fluctuation possible"
                else:
                    summary = "Moon weak — emotional sensitivity; mental health needs attention"
                if result["moon_afflictions"]:
                    summary += f"; Afflictions: {', '.join(result['moon_afflictions'][:2])}"
                if result["moon_protections"]:
                    summary += f"; Protected by: {', '.join(result['moon_protections'][:1])}"
                result["summary"] = summary

        except Exception as e:
            logger.warning(f"Lagna/Moon strength extraction error: {e}")

        return result

    def _is_kp_point(self, point: str) -> bool:
        """Check if a point is KP-related"""
        kp_keywords = [
            'cusp', 'csl', 'sub-lord', 'sub lord',
            'signif', 'connects to', 'ruling planet',
            'kp', 'promise', 'sub-sub lord'
        ]
        point_lower = point.lower()
        return any(kw in point_lower for kw in kp_keywords)
    # ═══════════════════════════════════════════════════════════════
    # NEW: DIGNITY CALCULATION FROM SIGN (FALLBACK METHOD)
    # ═══════════════════════════════════════════════════════════════
    def _calculate_dignity_from_sign(self, planet_name: str, planet_sign: str) -> str:
        """
        Calculate planetary dignity based on sign placement.
        
        Returns: EXALTED, OWN_SIGN, FRIENDLY, NEUTRAL, ENEMY, or DEBILITATED
        
        This is a fallback method when HouseLordsAnalyzer doesn't provide dignity.
        """
        if not planet_name or not planet_sign:
            logger.warning(f"⚠️ Cannot calculate dignity: planet={planet_name}, sign={planet_sign}")
            return "NEUTRAL"
        
        # Normalize inputs
        planet_name = planet_name.strip()
        planet_sign = planet_sign.strip()
        
        # Check exaltation first (highest dignity)
        if self.EXALTATION.get(planet_name) == planet_sign:
            logger.info(f"✅ {planet_name} is EXALTED in {planet_sign}")
            return "EXALTED"
        
        # Check debilitation (lowest dignity)
        if self.DEBILITATION.get(planet_name) == planet_sign:
            logger.info(f"⚠️ {planet_name} is DEBILITATED in {planet_sign}")
            return "DEBILITATED"
        
        # Check own sign (very strong)
        if planet_sign in self.OWN_SIGNS.get(planet_name, []):
            logger.info(f"✅ {planet_name} is in OWN SIGN {planet_sign}")
            return "OWN_SIGN"
        
        # Check friendly sign
        if planet_sign in self.FRIENDLY_SIGNS.get(planet_name, []):
            logger.info(f"✅ {planet_name} is FRIENDLY in {planet_sign}")
            return "FRIENDLY"
        
        # Check enemy sign
        if planet_sign in self.ENEMY_SIGNS.get(planet_name, []):
            logger.info(f"⚠️ {planet_name} is in ENEMY sign {planet_sign}")
            return "ENEMY"
        
        # Default to neutral
        logger.info(f"○ {planet_name} is NEUTRAL in {planet_sign}")
        return "NEUTRAL"

    # ═══════════════════════════════════════════════════════════════
    # TIMING WINDOWS EXTRACTION - FIXED VERSION!
    # ═══════════════════════════════════════════════════════════════
    def _extract_timing_windows(self, timing_windows: List) -> Dict:
        """
        Extract BEST and NEAREST timing windows for LLM.
        
        ✅ FIXED: Now handles both dict and TimingWindow objects!
        
        Best window: Highest score (best planetary alignment)
        Nearest window: Earliest favorable window (soonest opportunity)
        
        Returns dict with:
        - best_window: Window with highest final_score
        - nearest_window: Earliest window with score >= 50
        - all_favorable: Top 5 windows for reference
        """
        if not timing_windows:
            logger.info("No timing windows provided to extract")
            return {}

        try:
            # ✅ FIX: Helper function to get attribute from either dict or TimingWindow object
            def get_attr(obj, key, default=None):
                """Get attribute from dict or object (handles both cases)"""
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    # It's a TimingWindow dataclass or similar object
                    return getattr(obj, key, default)

            # ✅ FIX: Helper function to convert TimingWindow object to dict for storage
            def window_to_dict(w):
                """Convert TimingWindow object or dict to standardized dict format"""
                if w is None:
                    return None
                if isinstance(w, dict):
                    return w

                # Convert TimingWindow dataclass to dict
                result = {
                    'start': get_attr(w, 'start'),
                    'end': get_attr(w, 'end'),
                    'dasha': get_attr(w, 'dasha'),
                    'score': get_attr(w, 'score'),
                    'transit_score': get_attr(w, 'transit_score'),
                    'final_score': get_attr(w, 'final_score'),
                    'age_at_start': get_attr(w, 'age_at_start'),
                    'is_overall_best': get_attr(w, 'is_overall_best', False),
                    'is_earliest_favorable': get_attr(w, 'is_earliest_favorable', False),
                }

                # Include additional fields if they exist (for detailed scoring)
                for extra_field in ['score_maha', 'score_antara', 'score_paryantar',
                                   'md', 'ad', 'pd', 'maha', 'antara', 'paryantar',
                                   '_domain_score', '_delay_years', '_needs_resonant_jump']:
                    val = get_attr(w, extra_field)
                    if val is not None:
                        result[extra_field] = val

                return result

            # Log the first window type for debugging
            if timing_windows:
                first = timing_windows[0]
                logger.info(f"🔍 First timing window type: {type(first)}")
                if not isinstance(first, dict):
                    logger.info(f"🔍 First window attributes: {vars(first) if hasattr(first, '__dict__') else 'N/A'}")

            # ✅ FIX: Sort by final_score using get_attr helper
            sorted_windows = sorted(
                timing_windows,
                key=lambda w: get_attr(w, 'final_score', 0) or 0,
                reverse=True
            )

            # Best window: highest score (convert to dict for JSON serialization)
            best_window = window_to_dict(sorted_windows[0]) if sorted_windows else None

            # Nearest window: earliest with score >= 50
            from datetime import datetime

            favorable_windows = [
                w for w in timing_windows
                if (get_attr(w, 'final_score', 0) or 0) >= 50
            ]

            logger.info(f"🔍 Found {len(favorable_windows)} favorable windows (score >= 50)")

            if favorable_windows:
                sorted_by_date = sorted(
                    favorable_windows,
                    key=lambda w: datetime.strptime(
                        get_attr(w, 'start', '9999-12-31') or '9999-12-31',
                        '%Y-%m-%d'
                    )
                )
                nearest_window = window_to_dict(sorted_by_date[0]) if sorted_by_date else None
            else:
                # If no windows with score >= 50, use the best window as nearest too
                nearest_window = best_window
                logger.info("🔍 No windows with score >= 50, using best window as nearest")

            # Top 5 favorable windows (convert all to dicts)
            all_favorable = [window_to_dict(w) for w in sorted_windows[:5]]

            result = {
                'best_window': best_window,
                'nearest_window': nearest_window,
                'all_favorable': all_favorable,
                'has_timing': True
            }

            # Log success
            logger.info(f"✅ Timing extraction SUCCESSFUL:")
            if best_window:
                logger.info(f"   Best: {best_window.get('dasha', 'N/A')} - Score: {best_window.get('final_score', 0)}")
            if nearest_window:
                logger.info(f"   Nearest: {nearest_window.get('dasha', 'N/A')} - Score: {nearest_window.get('final_score', 0)}")

            return result

        except Exception as e:
            logger.error(f"Error extracting timing windows: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    def _generate_hospitalization_timing_proof(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        timing_windows_data: Dict
    ) -> Dict[str, any]:
        """
        Generate KP significator proof for hospitalization/health event timing.
        
        For hospitalization timing in KP astrology:
        - Houses 6 (disease), 8 (chronic issues/transformation), 12 (hospitalization) need activation
        - Mars involvement can indicate acute conditions requiring intervention
        - Shows which dasha lords signify these houses and HOW (Star Lord, Sub Lord, etc.)
        
        NOTE: This indicates POSSIBILITY of hospitalization, not planning for surgery.
        
        Returns structured data for LLM to explain timing recommendations properly.
        """
        HEALTH_EVENT_HOUSES = {6, 8, 12}  # Renamed from HEALTH_EVENT_HOUSES
        CURE_HOUSES = {1, 5, 9, 11}  # Recovery houses
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Build House Occupancy Map
        # ═══════════════════════════════════════════════════════════════
        house_occupants = defaultdict(list)
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            house = pdata.get("house")
            if house:
                house_occupants[house].append(pname)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Build House Lords Map
        # ═══════════════════════════════════════════════════════════════
        house_lords = {}
        for h in houses:
            house_num = h.get("house")
            lord = h.get("rashi_lord") or h.get("sign_lord") or h.get("cusp_sub_lord")
            if house_num and lord:
                house_lords[house_num] = normalize_planet_name(lord)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Build Planet Significator Table
        # ═══════════════════════════════════════════════════════════════
        # KP Signification Levels (OCSS):
        # O = Occupant of house
        # C = Cusp Sub Lord / Constellation Lord of Cusp
        # S1 = Star Lord (Nakshatra Lord)
        # S2 = Sign Lord (Rashi Lord)
        
        planet_significators = {}
        
        for pname, pdata in planets.items():
            if pname in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            
            sigs = {
                "occupant_of": [],
                "star_lord_of_occupant": [],  # If planet is star lord of another planet occupying a house
                "own_house_lord": [],  # Houses this planet rules
                "sub_lord_of": [],
                "total_health_event_signification": 0,
                "total_cure_signification": 0,
                "mars_connection": False
            }
            
            # Level 1: Direct Occupation
            planet_house = pdata.get("house")
            if planet_house:
                sigs["occupant_of"].append(planet_house)
                if planet_house in HEALTH_EVENT_HOUSES:
                    sigs["total_health_event_signification"] += 4
                if planet_house in CURE_HOUSES:
                    sigs["total_cure_signification"] += 4
            
            # Level 2: House Lordship
            for h_num, lord in house_lords.items():
                if lord == pname:
                    sigs["own_house_lord"].append(h_num)
                    if h_num in HEALTH_EVENT_HOUSES:
                        sigs["total_health_event_signification"] += 2
                    if h_num in CURE_HOUSES:
                        sigs["total_cure_signification"] += 2
            
            # Level 3: Star Lord (Nakshatra Lord) signification
            nak_lord = normalize_planet_name(pdata.get("nakshatra_lord") or pdata.get("nak_lord"))
            if nak_lord:
                sigs["nakshatra_lord"] = nak_lord
                # Check what houses the nakshatra lord occupies/rules
                nak_lord_data = planets.get(nak_lord, {})
                nak_lord_house = nak_lord_data.get("house")
                if nak_lord_house:
                    sigs["star_lord_of_occupant"].append(nak_lord_house)
                    if nak_lord_house in HEALTH_EVENT_HOUSES:
                        sigs["total_health_event_signification"] += 3
                    if nak_lord_house in CURE_HOUSES:
                        sigs["total_cure_signification"] += 3

            # Level 4: Sub Lord signification (KP chain completion)
            sub_lord = normalize_planet_name(pdata.get("sub_lord") or "")
            if sub_lord:
                sigs["sub_lord"] = sub_lord
                sub_lord_data = planets.get(sub_lord, {})
                sub_lord_house = sub_lord_data.get("house")
                sigs["sub_lord_house"] = sub_lord_house
                if sub_lord_house:
                    if sub_lord_house in HEALTH_EVENT_HOUSES:
                        sigs["total_health_event_signification"] += 2
                    if sub_lord_house in CURE_HOUSES:
                        sigs["total_cure_signification"] += 2
            
            # Check Mars connection
            if pname == "Mars":
                sigs["mars_connection"] = True
            elif sigs.get("nakshatra_lord") == "Mars":
                sigs["mars_connection"] = True
            
            planet_significators[pname] = sigs
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Analyze Timing Windows with Significator Proof
        # ═══════════════════════════════════════════════════════════════
        timing_proofs = []
        
        if timing_windows_data and timing_windows_data.get("all_favorable"):
            for window in timing_windows_data.get("all_favorable", [])[:3]:  # Top 3 windows
                dasha_str = window.get("dasha", "")
                
                # Parse dasha lords (format: "Saturn-Mercury-Venus" or "Saturn / Mercury")
                dasha_parts = dasha_str.replace(" / ", "-").replace("/", "-").split("-")
                
                proof = {
                    "period": f"{window.get('start', 'N/A')} to {window.get('end', 'N/A')}",
                    "dasha": dasha_str,
                    "score": window.get("final_score", 0),
                    "dasha_lords": [],
                    "total_6_8_12_activation": 0,
                    "mars_involved": False,
                    "house_linkage": []
                }
                
                for lord_name in dasha_parts:
                    lord_name = normalize_planet_name(lord_name.strip())
                    if not lord_name:
                        continue
                    
                    lord_sigs = planet_significators.get(lord_name, {})
                    
                    # Build full KP chain for this dasha lord
                    nak_lord = lord_sigs.get("nakshatra_lord", "")
                    sub_lord_name = lord_sigs.get("sub_lord", "")
                    sub_lord_house = lord_sigs.get("sub_lord_house")
                    lord_own_house = (lord_sigs.get("occupant_of") or [None])[0]

                    lord_proof = {
                        "planet": lord_name,
                        "planet_house": lord_own_house,
                        "nakshatra_lord": nak_lord,
                        "sub_lord": sub_lord_name,
                        "sub_lord_house": sub_lord_house,
                        "signifies_houses": [],
                        "how": [],
                        # Full KP chain string for display
                        "kp_chain": (
                            f"{lord_name} (H{lord_own_house or '?'}) "
                            f"→ Star lord {nak_lord or '?'} "
                            f"→ Sub lord {sub_lord_name or '?'} (H{sub_lord_house or '?'})"
                        )
                    }

                    # Add occupation signification
                    for h in lord_sigs.get("occupant_of", []):
                        if h in HEALTH_EVENT_HOUSES:
                            lord_proof["signifies_houses"].append(h)
                            lord_proof["how"].append(f"Occupies house {h}")

                    # Add lordship signification
                    for h in lord_sigs.get("own_house_lord", []):
                        if h in HEALTH_EVENT_HOUSES:
                            lord_proof["signifies_houses"].append(h)
                            lord_proof["how"].append(f"Lord of house {h}")

                    # Add star lord signification
                    for h in lord_sigs.get("star_lord_of_occupant", []):
                        if h in HEALTH_EVENT_HOUSES:
                            lord_proof["signifies_houses"].append(h)
                            lord_proof["how"].append(f"via Star lord {nak_lord} in house {h}")

                    # Add sub lord signification
                    if sub_lord_house and sub_lord_house in HEALTH_EVENT_HOUSES:
                        lord_proof["signifies_houses"].append(sub_lord_house)
                        lord_proof["how"].append(f"via Sub lord {sub_lord_name} in house {sub_lord_house}")
                    
                    proof["total_6_8_12_activation"] += lord_sigs.get("total_health_event_signification", 0)
                    
                    if lord_sigs.get("mars_connection"):
                        proof["mars_involved"] = True
                    
                    if lord_name == "Mars":
                        proof["mars_involved"] = True
                    
                    proof["dasha_lords"].append(lord_proof)
                
                # Generate house linkage explanation
                houses_activated = set()
                for lord in proof["dasha_lords"]:
                    houses_activated.update(lord["signifies_houses"])
                
                if 6 in houses_activated:
                    proof["house_linkage"].append("6th house (disease/illness) activated")
                if 8 in houses_activated:
                    proof["house_linkage"].append("8th house (surgery/transformation) activated")
                if 12 in houses_activated:
                    proof["house_linkage"].append("12th house (hospitalization) activated")
                
                timing_proofs.append(proof)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Build Significator Summary Table
        # ═══════════════════════════════════════════════════════════════
        significator_table = []
        
        for pname in ["Mars", "Saturn", "Rahu", "Ketu", "Sun", "Moon", "Mercury", "Jupiter", "Venus"]:
            if pname not in planet_significators:
                continue
            sigs = planet_significators[pname]
            
            surgery_houses = []
            if sigs.get("occupant_of"):
                for h in sigs["occupant_of"]:
                    if h in HEALTH_EVENT_HOUSES:
                        surgery_houses.append(f"{h}(O)")  # O = Occupant
            if sigs.get("own_house_lord"):
                for h in sigs["own_house_lord"]:
                    if h in HEALTH_EVENT_HOUSES:
                        surgery_houses.append(f"{h}(L)")  # L = Lord
            if sigs.get("star_lord_of_occupant"):
                for h in sigs["star_lord_of_occupant"]:
                    if h in HEALTH_EVENT_HOUSES:
                        surgery_houses.append(f"{h}(S)")  # S = Star Lord
            
            if surgery_houses or pname == "Mars":
                significator_table.append({
                    "planet": pname,
                    "signifies_6_8_12": surgery_houses if surgery_houses else ["None"],
                    "health_event_score": sigs.get("total_health_event_signification", 0),
                    "is_key_planet": pname in ["Mars", "Saturn", "Rahu"]
                })
        
        # Sort by surgery score
        significator_table.sort(key=lambda x: x["health_event_score"], reverse=True)
        
        return {
            "significator_table": significator_table,
            "timing_proofs": timing_proofs,
            "house_occupants": dict(house_occupants),
            "house_lords": house_lords,
            "legend": {
                "O": "Occupant (planet sits in this house) - strongest",
                "L": "Lord (planet rules this house sign)",
                "S": "Star Lord (planet's nakshatra lord signifies this house)"
            },
            "surgery_houses_meaning": {
                6: "Disease, illness requiring treatment",
                8: "Surgery, transformation, chronic issues",
                12: "Hospitalization, confinement, recovery period"
            }
        }

    def _evaluate_mental_health_indicators(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        vedic_planets: Dict[str, Dict] = None,
        vedic_houses: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Comprehensive mental health analysis using KP and Vedic indicators.
        
        Key factors analyzed:
        - MOON (MOST IMPORTANT): Mind, emotions, mental stability
        - MERCURY: Nervous system, communication, rational thinking
        - RAHU: Anxiety, obsession, addiction, confusion
        - KETU: Detachment, dissociation, spiritual confusion
        - SATURN: Depression, chronic stress, isolation
        
        Houses analyzed:
        - 1st: Self-identity, physical body affecting mind
        - 4th: Emotional base, inner peace, domestic happiness
        - 5th: Intelligence, mental clarity, creativity
        - 8th: Trauma, hidden fears, sudden psychological events
        - 12th: Isolation, subconscious, losses, addiction patterns
        
        Returns:
            Dict with detailed mental health indicators
        """
        analysis = {
            "has_analysis": False,
            "moon_analysis": {},
            "mercury_analysis": {},
            "rahu_analysis": {},
            "ketu_analysis": {},
            "saturn_analysis": {},
            "house_analysis": {},
            "overall_verdict": "",
            "risk_factors": [],
            "protective_factors": []
        }
        
        use_planets = vedic_planets if vedic_planets else planets
        use_houses = vedic_houses if vedic_houses else houses
        
        # ═══════════════════════════════════════════════════════════════
        # 1. MOON ANALYSIS (MOST IMPORTANT FOR MENTAL HEALTH)
        # ═══════════════════════════════════════════════════════════════
        moon_data = use_planets.get("Moon", {})
        if moon_data:
            analysis["has_analysis"] = True
            moon_house = moon_data.get("house", 0)
            moon_sign = moon_data.get("sign", "")
            moon_nak_lord = normalize_planet_name(moon_data.get("nakshatra_lord") or moon_data.get("nak_lord"))
            
            # Calculate Moon strength
            moon_strength = self._calculate_planet_strength_score(moon_data, "Moon")
            
            # Check afflictions
            afflictions = []
            if moon_house in [6, 8, 12]:
                afflictions.append(f"Moon in dusthana house {moon_house}")
            if moon_data.get("is_combust") or moon_data.get("is_combusted"):
                afflictions.append("Moon is combust (weakened)")
            if moon_sign == "Scorpio":
                afflictions.append("Moon in debilitation sign (Scorpio)")
            
            # Check if Moon is with malefics
            for planet_name, pdata in use_planets.items():
                if planet_name in ["Rahu", "Ketu", "Saturn", "Mars"]:
                    if pdata.get("house") == moon_house:
                        afflictions.append(f"Moon conjunct {planet_name}")
            
            # Check protective factors
            protections = []
            if moon_sign == "Taurus":
                protections.append("Moon exalted in Taurus")
            if moon_sign == "Cancer":
                protections.append("Moon in own sign Cancer")
            if moon_strength >= 70:
                protections.append(f"Strong Moon (strength: {moon_strength}/100)")
            
            # Check if Jupiter aspects Moon (protective)
            jupiter_data = use_planets.get("Jupiter", {})
            if jupiter_data:
                jupiter_house = jupiter_data.get("house", 0)
                # Jupiter's special aspects: 5th, 7th, 9th from its position
                if moon_house in [(jupiter_house + 4) % 12 or 12, 
                                  (jupiter_house + 6) % 12 or 12,
                                  (jupiter_house + 8) % 12 or 12]:
                    protections.append("Moon receives Jupiter's aspect (protective)")
            
            # Summary — use soft tendency language, never diagnoses
            if afflictions:
                if len(afflictions) >= 2:
                    summary = f"Moon placement ({', '.join(afflictions[:2])}) suggests emotional sensitivity tendency. Grounding practices beneficial."
                    analysis["risk_factors"].extend(afflictions)
                else:
                    summary = f"Moon has a sensitivity indicator ({afflictions[0]}). Emotional awareness and self-care recommended."
                    analysis["risk_factors"].append(afflictions[0])
            elif protections:
                summary = f"Moon is well-placed ({protections[0]}). Good emotional equilibrium and inner resilience."
                analysis["protective_factors"].extend(protections)
            else:
                summary = f"Moon is in a neutral position. Moderate emotional stability expected."
            
            analysis["moon_analysis"] = {
                "house": moon_house,
                "sign": moon_sign,
                "nakshatra_lord": moon_nak_lord,
                "strength": moon_strength,
                "afflictions": afflictions,
                "protections": protections,
                "summary": summary
            }
        
        # ═══════════════════════════════════════════════════════════════
        # 2. MERCURY ANALYSIS (NERVOUS SYSTEM, COMMUNICATION)
        # ═══════════════════════════════════════════════════════════════
        mercury_data = use_planets.get("Mercury", {})
        if mercury_data:
            mercury_house = mercury_data.get("house", 0)
            mercury_sign = mercury_data.get("sign", "")
            mercury_strength = self._calculate_planet_strength_score(mercury_data, "Mercury")
            
            afflictions = []
            protections = []
            
            if mercury_house in [6, 8, 12]:
                afflictions.append(f"Mercury in house {mercury_house}")
            if mercury_data.get("is_combust") or mercury_data.get("is_combusted"):
                afflictions.append("Mercury combust")
            if mercury_sign == "Pisces":
                afflictions.append("Mercury debilitated in Pisces")
            
            if mercury_sign == "Virgo":
                protections.append("Mercury exalted in Virgo")
            if mercury_sign in ["Gemini", "Virgo"]:
                protections.append(f"Mercury in own sign {mercury_sign}")
            if mercury_strength >= 70:
                protections.append(f"Strong Mercury ({mercury_strength}/100)")
            
            if afflictions:
                summary = f"Mercury weakness may affect nervous system and communication. ({', '.join(afflictions[:2])})"
                analysis["risk_factors"].extend(afflictions)
            elif protections:
                summary = f"Mercury well-placed supports rational thinking and communication. ({protections[0]})"
                analysis["protective_factors"].extend(protections)
            else:
                summary = "Mercury in neutral position. Average nervous system resilience."
            
            analysis["mercury_analysis"] = {
                "house": mercury_house,
                "sign": mercury_sign,
                "strength": mercury_strength,
                "afflictions": afflictions,
                "protections": protections,
                "summary": summary
            }
        
        # ═══════════════════════════════════════════════════════════════
        # 3. RAHU ANALYSIS (ANXIETY, ADDICTION, OBSESSION)
        # ═══════════════════════════════════════════════════════════════
        rahu_data = use_planets.get("Rahu", {})
        if rahu_data:
            rahu_house = rahu_data.get("house", 0)
            rahu_sign = rahu_data.get("sign", "")
            
            is_afflicting = False
            concerns = []
            
            # Rahu in mental health houses
            if rahu_house in [1, 4, 5]:
                is_afflicting = True
                if rahu_house == 1:
                    concerns.append("Rahu in 1st: Restlessness, identity confusion")
                elif rahu_house == 4:
                    concerns.append("Rahu in 4th: Domestic unrest, emotional turbulence")
                elif rahu_house == 5:
                    concerns.append("Rahu in 5th: Obsessive thinking, creative blocks")
            
            if rahu_house == 12:
                concerns.append("Rahu in 12th: Addiction tendencies, sleep disturbances")
                is_afflicting = True
            
            # Check if Rahu affects Moon
            moon_data = use_planets.get("Moon", {})
            if moon_data and moon_data.get("house") == rahu_house:
                concerns.append("Rahu-Moon conjunction: Anxiety and emotional confusion")
                is_afflicting = True
            
            if concerns:
                summary = f"Rahu influence on mental health: {concerns[0]}. Watch for anxiety patterns."
                analysis["risk_factors"].extend(concerns)
            else:
                summary = "Rahu not directly affecting mental health houses."
            
            analysis["rahu_analysis"] = {
                "house": rahu_house,
                "sign": rahu_sign,
                "is_afflicting": is_afflicting,
                "concerns": concerns,
                "summary": summary
            }
        
        # ═══════════════════════════════════════════════════════════════
        # 4. HOUSE ANALYSIS (4th, 5th, 8th, 12th)
        # ═══════════════════════════════════════════════════════════════
        mental_houses = {4, 5, 8, 12}
        house_analysis = {}
        
        for h in use_houses:
            house_num = h.get("house")
            if house_num not in mental_houses:
                continue
            
            # Get lord
            lord = h.get("rashi_lord") or h.get("sign_lord") or h.get("cusp_sub_lord")
            lord = normalize_planet_name(lord) if lord else None
            
            # Get lord data
            lord_data = use_planets.get(lord, {}) if lord else {}
            lord_house = lord_data.get("house", 0)
            lord_strength = self._calculate_planet_strength_score(lord_data, lord) if lord_data else 50
            
            # Get occupants
            occupants = [pname for pname, pdata in use_planets.items() 
                        if pdata.get("house") == house_num and pname not in ["Ascendant"]]
            
            # House-specific analysis
            if house_num == 4:
                meaning = "Emotional foundation, inner peace"
                if any(p in ["Rahu", "Saturn", "Ketu"] for p in occupants):
                    summary = f"4th house afflicted by {', '.join([p for p in occupants if p in ['Rahu', 'Saturn', 'Ketu']])}. Domestic stress affecting peace of mind."
                    analysis["risk_factors"].append(f"4th house afflicted")
                elif lord_strength >= 60:
                    summary = f"4th lord {lord} well-placed. Good emotional foundation."
                    analysis["protective_factors"].append("Strong 4th house")
                else:
                    summary = f"4th house lord {lord} in moderate position."
            
            elif house_num == 5:
                meaning = "Mental clarity, intelligence"
                if any(p in ["Rahu", "Saturn", "Ketu"] for p in occupants):
                    summary = f"5th house influenced by {', '.join([p for p in occupants if p in ['Rahu', 'Saturn', 'Ketu']])}. May affect mental clarity."
                    analysis["risk_factors"].append("5th house afflicted")
                elif lord_strength >= 60:
                    summary = f"5th lord {lord} well-placed. Good mental clarity and intelligence."
                    analysis["protective_factors"].append("Strong 5th house")
                else:
                    summary = f"5th house in moderate condition."
            
            elif house_num == 8:
                meaning = "Deep transformation, hidden patterns"
                if any(p in ["Moon", "Mercury"] for p in occupants):
                    summary = f"8th house has {', '.join([p for p in occupants if p in ['Moon', 'Mercury']])}. May indicate emotional depth and introspective tendencies."
                    analysis["risk_factors"].append("Mental karaka in 8th — emotional depth tendency")
                else:
                    summary = f"8th house not directly involving mental health planets."

            elif house_num == 12:
                meaning = "Subconscious, rest, introspection"
                if any(p in ["Moon", "Mercury"] for p in occupants):
                    summary = f"12th house has {', '.join([p for p in occupants if p in ['Moon', 'Mercury']])}. Tendency toward introspection; ensure adequate rest and grounding."
                    analysis["risk_factors"].append("Mental karaka in 12th — introspection/rest sensitivity")
                elif "Rahu" in occupants:
                    summary = "Rahu in 12th may indicate restless thought patterns or irregular sleep tendencies."
                    analysis["risk_factors"].append("Rahu in 12th — restless thought tendency")
                else:
                    summary = "12th house not strongly affecting mental health."
            else:
                meaning = self.MENTAL_HEALTH_HOUSE_MEANINGS.get(house_num, "")
                summary = f"House {house_num} analysis available."
            
            house_analysis[house_num] = {
                "lord": lord,
                "lord_house": lord_house,
                "lord_strength": lord_strength,
                "occupants": occupants,
                "meaning": meaning,
                "summary": summary
            }
        
        analysis["house_analysis"] = house_analysis
        
        # ═══════════════════════════════════════════════════════════════
        # 5. OVERALL VERDICT
        # ═══════════════════════════════════════════════════════════════
        risk_count = len(analysis["risk_factors"])
        protective_count = len(analysis["protective_factors"])
        
        if risk_count >= 3:
            overall = "EMOTIONALLY SENSITIVE: Multiple chart indicators suggest emotional sensitivity. Mindfulness and professional wellness support may be beneficial."
        elif risk_count >= 2 and protective_count < 2:
            overall = "MODERATE EMOTIONAL SENSITIVITY: Some emotional fluctuation tendencies present. Self-care, grounding practices, and awareness are important."
        elif protective_count >= 2:
            overall = "EMOTIONALLY RESILIENT: Good mental equilibrium indicators with protective planetary factors."
        elif risk_count == 1:
            overall = "MILD EMOTIONAL SENSITIVITY: One area of emotional sensitivity identified. Generally stable mental foundation overall."
        else:
            overall = "EMOTIONALLY BALANCED: No significant emotional sensitivity indicators. Normal emotional patterns expected."
        
        analysis["overall_verdict"] = overall

        return analysis

    def _reconcile_kp_vedic_mental_verdict(
        self,
        mental_health_analysis: Dict,
        kp_structured: Dict
    ) -> Dict:
        """
        Reconciliation layer: combines KP (primary) and Vedic (modifier) mental health signals.

        Hierarchy:
          KP  → 60% weight  (house 5 CSL + house 1 CSL mental support)
          Vedic → 40% weight (risk_count / protective_count from planetary analysis)

        Decision matrix:
          KP positive + Vedic negative  → MODERATE (neither wins outright)
          KP negative + Vedic negative  → SENSITIVE (both agree — cautious)
          KP positive + Vedic positive  → RESILIENT
          KP neutral  + Vedic negative  → MILD_SENSITIVITY
          KP neutral  + Vedic positive  → MILD_RESILIENCE
          etc.

        Returns dict with:
          reconciled_verdict:   final label
          kp_mental_score:      -2 to +2
          vedic_mental_score:   -2 to +2
          combined_score:       weighted sum
          referral_level:       none / optional / suggested
          final_summary:        ready-to-use Hindi sentence
        """
        result = {
            "reconciled_verdict": "MODERATE_EMOTIONAL_SENSITIVITY",
            "kp_mental_score": 0,
            "vedic_mental_score": 0,
            "combined_score": 0.0,
            "referral_level": "none",
            "final_summary": "",
            "conflict_detected": False,
            "conflict_resolution": "",
        }

        # ── Step 1: KP mental score (from H5 CSL + H1 CSL) ──
        kp_score = 0
        csl_details = kp_structured.get("csl_details", {}) if kp_structured else {}

        h5_verdict = csl_details.get(5, {}).get("verdict", "")
        h1_verdict = csl_details.get(1, {}).get("verdict", "")

        KP_VERDICT_SCORE = {
            "EXCELLENT_MENTAL_PEACE": +2,
            "MODERATE_MENTAL_STATE":   0,
            "MENTAL_STRESS":          -2,
            "STRONG_VITALITY":        +1,
            "MODERATE_VITALITY":       0,
            "WEAK_VITALITY":          -1,
        }
        kp_score += KP_VERDICT_SCORE.get(h5_verdict, 0)
        kp_score += KP_VERDICT_SCORE.get(h1_verdict, 0) * 0.5   # H1 is secondary for mental
        kp_score = max(-2, min(2, kp_score))                    # clamp to [-2, +2]
        result["kp_mental_score"] = round(kp_score, 1)

        # ── Step 2: Vedic mental score (risk_count vs protective_count) ──
        risk_count = len(mental_health_analysis.get("risk_factors", []))
        protective_count = len(mental_health_analysis.get("protective_factors", []))
        # net = protective - risk, clamped to [-2, +2]
        vedic_score = max(-2, min(2, protective_count - risk_count))
        result["vedic_mental_score"] = vedic_score

        # ── Step 3: Weighted combination (KP 60%, Vedic 40%) ──
        combined = (kp_score * 0.60) + (vedic_score * 0.40)
        result["combined_score"] = round(combined, 2)

        # ── Step 4: Conflict detection ──
        if kp_score > 0 and vedic_score < -1:
            result["conflict_detected"] = True
            result["conflict_resolution"] = (
                f"KP analysis (primary, 60%) shows positive mental indicators "
                f"(H5 CSL verdict: {h5_verdict}) while Vedic analysis shows "
                f"{abs(vedic_score)} risk factor(s). KP takes priority → final verdict "
                f"is MODERATE, not SENSITIVE. Do NOT use the stronger Vedic warning."
            )
        elif kp_score < -1 and vedic_score > 0:
            result["conflict_detected"] = True
            result["conflict_resolution"] = (
                f"KP analysis (primary) shows stress indicators (H5: {h5_verdict}) "
                f"while Vedic shows protective factors. Combined → MILD_SENSITIVITY."
            )

        # ── Step 5: Final verdict from combined score ──
        if combined >= 1.5:
            verdict = "EMOTIONALLY_RESILIENT"
            referral = "none"
            summary = (
                "कुंडली में मानसिक स्थिरता और भावनात्मक संतुलन के अच्छे संकेत हैं। "
                "नियमित ध्यान और स्वस्थ दिनचर्या से यह स्थिति बनाए रखी जा सकती है।"
            )
        elif combined >= 0.5:
            verdict = "MILD_EMOTIONAL_RESILIENCE"
            referral = "none"
            summary = (
                "कुंडली में मानसिक शांति के अच्छे संकेत हैं। कुछ भावनात्मक उतार-चढ़ाव "
                "की प्रवृत्ति हो सकती है, लेकिन स्थिरता की क्षमता अधिक है।"
            )
        elif combined >= -0.5:
            verdict = "MODERATE_EMOTIONAL_SENSITIVITY"
            referral = "optional"
            summary = (
                "कुंडली में मानसिक संवेदनशीलता के कुछ संकेत हैं। भावनात्मक उतार-चढ़ाव "
                "की प्रवृत्ति हो सकती है। ध्यान, प्राणायाम और स्वस्थ जीवनशैली "
                "से स्थिति संतुलित रह सकती है।"
            )
        elif combined >= -1.5:
            verdict = "MILD_EMOTIONAL_SENSITIVITY"
            referral = "optional"
            summary = (
                "कुंडली में कुछ मानसिक संवेदनशीलता के संकेत हैं। भावनात्मक स्थिरता "
                "के लिए नियमित आत्म-देखभाल, ध्यान और सहयोगी वातावरण उपयोगी है। "
                "यदि लक्षण लंबे समय तक बने रहें तो सहायता लेना उचित हो सकता है।"
            )
        else:
            verdict = "EMOTIONALLY_SENSITIVE"
            referral = "suggested"
            summary = (
                "कुंडली में भावनात्मक संवेदनशीलता के कई संकेत हैं। मानसिक शांति के लिए "
                "ध्यान, प्राणायाम और स्वस्थ जीवनशैली महत्वपूर्ण है। "
                "यदि कोई कठिनाई महसूस हो तो किसी विश्वसनीय व्यक्ति या परामर्शदाता "
                "से बात करना सहायक हो सकता है।"
            )

        result["reconciled_verdict"] = verdict
        result["referral_level"] = referral
        result["final_summary"] = summary

        # ── Step 6: Referral guidance text (proportional, never alarmist) ──
        REFERRAL_TEXT = {
            "none": "",
            "optional": (
                "यदि आप किसी भावनात्मक कठिनाई का अनुभव करें तो "
                "किसी विश्वसनीय व्यक्ति से बात करना उपयोगी है।"
            ),
            "suggested": (
                "यदि लक्षण बने रहें, तो किसी परामर्शदाता या मनोवैज्ञानिक से "
                "मार्गदर्शन लेना सहायक हो सकता है।"
            ),
        }
        result["referral_text"] = REFERRAL_TEXT.get(referral, "")

        logger.info(
            f"Mental reconciliation: KP={kp_score:.1f} Vedic={vedic_score} "
            f"Combined={combined:.2f} → {verdict} (referral: {referral})"
        )
        return result

    # ═══════════════════════════════════════════════════════════════
    # ENHANCED HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def extract_planet_name(p):
        """Extract planet name from dict or string"""
        if isinstance(p, dict):
            return p.get("name")
        if isinstance(p, str):
            return p
        return None

    def _extract_house_lords(
        self,
        houses: list,
        planets: dict,
        relevant_houses: set,
        primary_houses: set
    ) -> dict:
        """
        Extract house lord information for relevant houses only.
        
        ✅ FIXED: Now uses fallback dignity calculation when HouseLordsAnalyzer fails.
        """
        house_lords_info = {}

        # ✅ DEBUG: Log analyzer availability
        logger.info(f"🔍 HOUSE_LORDS_AVAILABLE: {HOUSE_LORDS_AVAILABLE}")

        for h in houses:
            house_num = h.get("house")

            if house_num not in relevant_houses:
                continue

            # Get lord name - try multiple possible keys
            lord_name = (
                h.get("rashi_lord") or
                h.get("sign_lord") or
                h.get("lord") or
                ""
            )

            # Deduce from sign if lord not found directly
            house_sign = (
                h.get("sign") or
                h.get("start_rasi") or
                h.get("rasi") or
                ""
            )
            
            if not lord_name and house_sign:
                sign_lords = {
                    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
                    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
                    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
                    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
                }
                lord_name = sign_lords.get(house_sign, "")
                if lord_name:
                    logger.debug(f"✅ Deduced lord {lord_name} for house {house_num} from sign {house_sign}")

            normalized_lord = normalize_planet_name(lord_name)

            if not normalized_lord:
                logger.warning(f"⚠️ No lord found for house {house_num} (sign: {house_sign})")
                continue

            logger.debug(f"✅ {normalized_lord} is lord of house {house_num}")

            lord_data = planets.get(normalized_lord, {})
            if not lord_data:
                logger.warning(f"⚠️ No data found for lord {normalized_lord}")
                continue

            lord_house = lord_data.get("house")
            lord_sign = lord_data.get("sign", "")

            lord_degree = (
                lord_data.get("full_degree") or
                lord_data.get("global_degree") or
                lord_data.get("degree") or
                0
            )

            lord_is_combust = (
                lord_data.get("is_combusted", False) or
                lord_data.get("is_combust", False)
            )

            lord_is_retrograde = (
                lord_data.get("is_retro", False) or
                lord_data.get("is_retrograde", False)
            )

            # ── Planet age/stage based on local degree within sign ──
            # Classical Vedic rule (Bala Avastha):
            #   0–6°  → Infant/Bala  (बाल)   — very weak, cannot express fully
            #   6–12° → Young/Kumara (कुमार) — gaining strength
            #   12–18°→ Prime/Yuva  (युवा)   — full strength, most effective
            #   18–24°→ Mature/Prauda(प्रौढ़) — good strength, slightly declining
            #   24–30°→ Old/Vriddha (वृद्ध)  — weakened, results delayed
            local_deg = lord_degree % 30 if isinstance(lord_degree, (int, float)) and lord_degree else 15
            if local_deg < 6:
                lord_avastha = "Infant/Bala (0-6°) — very weak, significations suppressed"
                avastha_short = "Infant"
            elif local_deg < 12:
                lord_avastha = "Young/Kumara (6-12°) — gaining strength"
                avastha_short = "Young"
            elif local_deg < 18:
                lord_avastha = "Prime/Yuva (12-18°) — full strength, most effective"
                avastha_short = "Prime"
            elif local_deg < 24:
                lord_avastha = "Mature/Prauda (18-24°) — good strength"
                avastha_short = "Mature"
            else:
                lord_avastha = "Old/Vriddha (24-30°) — weakened, results may be delayed"
                avastha_short = "Old"

            # ═══════════════════════════════════════════════════════
            # FIXED: DIGNITY CALCULATION WITH FALLBACK
            # ═══════════════════════════════════════════════════════
            lord_dignity = "Unknown"
            lord_strength_score = 50
            dignity_source = "none"

            # Try HouseLordsAnalyzer first
            if HOUSE_LORDS_AVAILABLE:
                try:
                    analyzer = HouseLordsAnalyzer(planets, houses)

                    # ✅ DEBUG: Log available methods
                    available_methods = [m for m in dir(analyzer) if not m.startswith('_')]
                    logger.debug(f"🔍 Analyzer methods: {available_methods}")

                    dignity = None
                    
                    # Try different method names
                    if hasattr(analyzer, 'get_planet_dignity'):
                        dignity = analyzer.get_planet_dignity(normalized_lord)
                        logger.debug(f"🔍 get_planet_dignity({normalized_lord}) returned: {dignity}")
                    elif hasattr(analyzer, 'get_dignity'):
                        dignity = analyzer.get_dignity(normalized_lord)
                        logger.debug(f"🔍 get_dignity({normalized_lord}) returned: {dignity}")
                    elif hasattr(analyzer, 'analyze_dignity'):
                        dignity = analyzer.analyze_dignity(normalized_lord)
                        logger.debug(f"🔍 analyze_dignity({normalized_lord}) returned: {dignity}")
                    elif hasattr(analyzer, 'calculate_dignity'):
                        dignity = analyzer.calculate_dignity(normalized_lord)
                        logger.debug(f"🔍 calculate_dignity({normalized_lord}) returned: {dignity}")
                    else:
                        logger.debug(f"⚠️ No dignity method found on HouseLordsAnalyzer")

                    if dignity:
                        if hasattr(dignity, 'value'):
                            lord_dignity = dignity.value
                        elif hasattr(dignity, 'name'):
                            lord_dignity = dignity.name
                        else:
                            lord_dignity = str(dignity)
                        
                        dignity_source = "analyzer"
                        lord_strength_score = self._calculate_lord_strength(
                            normalized_lord, lord_data, lord_dignity
                        )
                        logger.info(f"✅ Got dignity from analyzer for {normalized_lord}: {lord_dignity}")

                except Exception as e:
                    logger.warning(f"⚠️ HouseLordsAnalyzer error for {normalized_lord}: {e}")

            # ✅ FALLBACK: Calculate dignity directly from sign if still Unknown
            if lord_dignity == "Unknown" and lord_sign:
                lord_dignity = self._calculate_dignity_from_sign(normalized_lord, lord_sign)
                dignity_source = "fallback"
                lord_strength_score = self._calculate_lord_strength(
                    normalized_lord, lord_data, lord_dignity
                )
                logger.info(f"✅ Calculated dignity via FALLBACK for {normalized_lord} in {lord_sign}: {lord_dignity}")

            # Log final dignity result
            logger.info(f"📊 House {house_num} Lord {normalized_lord}: Dignity={lord_dignity} (source={dignity_source}), Strength={lord_strength_score}")

            priority = "primary" if house_num in primary_houses else "secondary"

            planets_in_house = []
            for p in h.get("planets", []):
                planet_name = normalize_planet_name(self.extract_planet_name(p))
                if planet_name:
                    planets_in_house.append(planet_name)

            house_lords_info[house_num] = {
                "lord": normalized_lord,
                "lord_in_house": lord_house,
                "lord_in_sign": lord_sign,
                "lord_degree": lord_degree,
                "lord_local_degree": round(local_deg, 2),
                "lord_avastha": lord_avastha,
                "lord_avastha_short": avastha_short,
                "lord_is_combust": lord_is_combust,
                "lord_is_retrograde": lord_is_retrograde,
                "lord_dignity": lord_dignity,
                "lord_strength_score": lord_strength_score,
                "dignity_source": dignity_source,
                "priority": priority,
                "planets_in_house": planets_in_house,
                "house_sign": house_sign
            }

        return house_lords_info

    def _extract_aspects_on_houses(
        self,
        houses: list,
        planets: dict,
        aspects_data: dict,
        relevant_houses: set
    ) -> dict:
        """Extract aspects on relevant houses only."""
        house_aspects = {}

        benefics = {"Jupiter", "Venus", "Moon", "Mercury"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        for house_num in relevant_houses:
            house_aspects[house_num] = {
                "benefic_aspects": [],
                "malefic_aspects": [],
                "neutral_aspects": []
            }

            for planet_name, planet_data in planets.items():
                if aspects_data and planet_name in aspects_data:
                    aspected_houses = aspects_data[planet_name].get("aspects_houses", [])
                else:
                    aspected_houses = planet_data.get("aspects_houses", [])

                if house_num in aspected_houses:
                    if planet_name in benefics:
                        house_aspects[house_num]["benefic_aspects"].append(planet_name)
                    elif planet_name in malefics:
                        house_aspects[house_num]["malefic_aspects"].append(planet_name)
                    else:
                        house_aspects[house_num]["neutral_aspects"].append(planet_name)

        return house_aspects

    def _calculate_lord_strength(
        self,
        planet_name: str,
        planet_data: dict,
        dignity = None
    ) -> int:
        """
        Calculate lord strength score (0-100).
        
        ✅ FIXED: Now handles string dignity values properly.
        """
        score = 50

        if dignity:
            # Handle both enum and string values
            if hasattr(dignity, 'value'):
                dignity_str = dignity.value.upper()
            elif hasattr(dignity, 'name'):
                dignity_str = dignity.name.upper()
            else:
                dignity_str = str(dignity).upper().replace("_", " ")

            # Normalize common variations
            dignity_str = dignity_str.replace("OWN SIGN", "OWN_SIGN")

            dignity_scores = {
                "EXALTED": 100,
                "OWN_SIGN": 85,
                "OWN SIGN": 85,
                "MOOLATRIKONA": 80,
                "FRIENDLY": 65,
                "NEUTRAL": 50,
                "ENEMY": 30,
                "DEBILITATED": 10
            }
            
            score = dignity_scores.get(dignity_str, 50)
            logger.debug(f"📊 Dignity score for {planet_name} ({dignity_str}): {score}")

        # Combustion penalty
        if planet_data.get("is_combust", False) or planet_data.get("is_combusted", False):
            score -= 25
            logger.debug(f"📊 Combustion penalty for {planet_name}: -25")

        # Retrograde adjustment
        if planet_data.get("is_retrograde", False) or planet_data.get("is_retro", False):
            if planet_name in {"Jupiter", "Venus", "Mercury"}:
                score -= 10  # Benefics weaker when retrograde
            elif planet_name in {"Saturn", "Mars"}:
                score += 5   # Malefics can be stronger when retrograde
            logger.debug(f"📊 Retrograde adjustment for {planet_name}")

        # Degree-based adjustment (planets at extreme degrees are weaker)
        degree = (
            planet_data.get("full_degree") or
            planet_data.get("global_degree") or
            planet_data.get("degree") or
            15
        )
        
        # Get local degree within sign (0-30)
        local_degree = degree % 30 if isinstance(degree, (int, float)) else 15
        
        if local_degree < 3 or local_degree > 27:
            score -= 10  # Sandhi (junction) weakness
            logger.debug(f"📊 Sandhi penalty for {planet_name} at {local_degree:.1f}°")

        # Ensure score stays within bounds
        final_score = max(0, min(100, score))
        logger.debug(f"📊 Final strength score for {planet_name}: {final_score}")
        
        return final_score

    def _calculate_planet_strength_score(self, planet_data: dict, planet_name: str) -> int:
        """Alias for _calculate_lord_strength with (planet_data, planet_name) argument order."""
        dignity = planet_data.get("dignity") if planet_data else None
        return self._calculate_lord_strength(planet_name, planet_data, dignity)

    def _add_house_analysis_points(
        self,
        result: EvaluationResult,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set
    ):
        """Add analysis points based on house lords and aspects."""
        for house_num in sorted(primary_houses):
            if house_num not in house_lords_info:
                continue

            info = house_lords_info[house_num]
            aspects = house_aspects_info.get(house_num, {})

            lord = info["lord"]
            dignity = info["lord_dignity"]
            strength = info["lord_strength_score"]

            # Choose marker based on strength
            if strength >= 70:
                marker = "✅"
            elif strength >= 40:
                marker = "⭐"
            else:
                marker = "⚠️"
                
            point_parts = [
                f"{marker} House {house_num} ({self._get_house_meaning(house_num)}):",
                f"Lord {lord} is {dignity}",
                f"(Strength: {strength}/100)"
            ]

            conditions = []
            if info["lord_is_combust"]:
                conditions.append("COMBUST")
            if info["lord_is_retrograde"]:
                conditions.append("RETROGRADE")

            if conditions:
                point_parts.append(f"[{', '.join(conditions)}]")

            benefic = aspects.get("benefic_aspects", [])
            malefic = aspects.get("malefic_aspects", [])

            if benefic:
                point_parts.append(f"- Benefic: {', '.join(benefic)}")
            if malefic:
                point_parts.append(f"- Malefic: {', '.join(malefic)}")

            point_text = " ".join(point_parts)
            result.add_point(point_text)

    def _get_house_meaning(self, house_num: int) -> str:
        """Get house meaning for health context."""
        return self.HOUSE_MEANINGS.get(house_num, "General")

    def _store_data_for_llm(
        self,
        result: EvaluationResult,
        house_config: dict,
        house_lords_info: dict,
        house_aspects_info: dict,
        primary_houses: set,
        secondary_houses: set,
        timing_windows_data: dict = None
    ):
        """Store all enhanced data in additional_data for LLM consumption."""
        domain_prefix = "health_physical_mental"

        # Count dignity statistics
        dignity_stats = {
            "exalted": 0,
            "own_sign": 0,
            "friendly": 0,
            "neutral": 0,
            "enemy": 0,
            "debilitated": 0
        }
        
        for info in house_lords_info.values():
            dignity_lower = info.get("lord_dignity", "").lower().replace(" ", "_")
            if dignity_lower in dignity_stats:
                dignity_stats[dignity_lower] += 1

        result.additional_data.update({
            f"{domain_prefix}_house_config": {
                "primary": list(primary_houses),
                "secondary": list(secondary_houses),
                "source": house_config.get("source", "fallback") if house_config else "fallback"
            },

            f"{domain_prefix}_house_lords": house_lords_info,

            f"{domain_prefix}_house_aspects": house_aspects_info,

            f"{domain_prefix}_analysis_summary": {
                "total_houses_analyzed": len(house_lords_info),
                "primary_houses_count": len(primary_houses),
                "secondary_houses_count": len(secondary_houses),
                "strong_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] >= 70
                ),
                "weak_lords": sum(
                    1 for info in house_lords_info.values()
                    if info["lord_strength_score"] < 40
                ),
                "dignity_distribution": dignity_stats  # ✅ NEW: Dignity stats
            }
        })

        # ✅ Store timing windows if available
        if timing_windows_data and timing_windows_data.get('has_timing'):
            result.additional_data[f"{domain_prefix}_timing_windows"] = timing_windows_data
            logger.info(f"✅ STORED TIMING WINDOWS IN additional_data")
            logger.info(f"   Key: {domain_prefix}_timing_windows")
            logger.info(f"   has_timing: {timing_windows_data.get('has_timing', False)}")
            if timing_windows_data.get('best_window'):
                logger.info(f"   best_window: {timing_windows_data['best_window'].get('dasha', 'N/A')}")
        else:
            logger.warning(f"❌ NO TIMING WINDOWS TO STORE (data: {bool(timing_windows_data)})")

    
    def get_questions(self) -> List[Question]:
        return [
            Question(
                id="HLT_PM_1",
                question=(
                    "According to astrology, what does my birth chart indicate about my physical health, tendency toward illness, and overall vitality, and are there any astrological remedies or lifestyle guidelines suggested for better well-being?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.STATUS
                ),
                sub_subdomain="General Health Analysis"
            ),
            Question(
                id="HLT_PM_2",
                question=(
                    "Are there risks to my life expectancy, chances of chronic disease, accidents, "
                    "or the need for surgery? If surgery or major treatment is required, "
                    "when would be the most auspicious time for it?"
                ),
                meta=QueryMeta(
                    QueryType.TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Health Risks and Surgery Timing"
            ),
            Question(
                id="HLT_PM_3",
                question=(
                    "What does astrology indicate about potential mental health issues such as "
                    "depression, anxiety, or addictions, and should I seek professional help?"
                ),
                meta=QueryMeta(
                    QueryType.NON_TIMING,
                    EventPolarity.NEGATIVE,
                    InterpretationGoal.RISK
                ),
                sub_subdomain="Mental Health Risks"
            ),
            # NOTE: HLT_PM_4 (Health Remedies) removed from questions array.
            # Remedies are covered in the top-level `remedies` field (remedies.astrological
            # and remedies.general) generated by the HLT_PM_1 General Health prompt.
            # Keeping remedies as a separate question caused score inconsistency and
            # redundant KP analysis repetition across 4 identical questions.
        ]
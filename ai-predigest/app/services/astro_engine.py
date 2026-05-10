"""
Main Astrology Engine - Orchestrates all calculations (Modular Version)

This version uses the domain registry system for evaluators and prompts.
UPDATED: Includes two-person timing overlap for Kundali Matching
FIXED: Compati
ility evaluation now properly passes all parameters
"""
import asyncio
import inspect  # ✅ NEW: Added for evaluator introspection
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from uuid import uuid4
import logging


from app.services.astro_api import vedic_api, kp_api
from app.services.kundali_milan_api import kundali_milan_api
from app.services.lalkitab_api import (
    get_lalkitab_remedies_for_chart,
    format_remedies_for_llm
)
from app.services.llm_provider import llm_service
from app.domains.registry import (
    get_evaluator, get_prompt_builder, get_compatibility_evaluator,
    extract_questions
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_deg_360, dms_to_decimal,
    SIGN_BASE, RASI_LORDS, get_cusp_sub_lord
)
from app.services.timing_engine import (
    kp_timing_engine, 
    TIMING_RULES, 
    VALID_AGE_RANGES,
    get_top_timing_windows,
    apply_transit_scores_to_windows_async
)
from app.domains.base import TimingWindow, QueryMeta, QueryType

# ✅ NEW: Import two-person timing module
from app.services.two_person_timing import (
    find_overlapping_timing_windows,
    convert_overlaps_to_timing_windows,
    format_overlapping_windows_for_llm
)

# ✅ NEW: Import API parser for correct house number handling
try:
    from app.utils.vedic_api_parser import (
        parse_vedic_api_response,
        create_houses_from_planets,
        format_for_llm_from_api_response
    )
    VEDIC_PARSER_AVAILABLE = True
except ImportError:
    VEDIC_PARSER_AVAILABLE = False

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTION: Safe Timing Query Detection
# ═══════════════════════════════════════════════════════════════════
def _is_timing_query(meta) -> bool:
    """
    Check if meta indicates a TIMING query.
    Handles both:
    - Dict with string value: {"type": "TIMING"}
    - Dict with enum value: {"type": QueryType.TIMING}
    - QueryMeta object: meta.query_type == QueryType.TIMING
    
    This function ensures compatibility across all domains regardless
    of whether they use string or enum values for query type.
    """
    if not meta:
        return False
    
    # Handle QueryMeta object directly
    if hasattr(meta, 'query_type'):
        meta_type = meta.query_type
        if meta_type is None:
            return False
        # Enum value (has .value attribute)
        if hasattr(meta_type, 'value'):
            return meta_type.value == "TIMING"
        # String value
        if isinstance(meta_type, str):
            return meta_type == "TIMING"
        # Enum value (has .name attribute)
        if hasattr(meta_type, 'name'):
            return meta_type.name == "TIMING"
        return str(meta_type) == "TIMING"
    
    # Handle dict
    if isinstance(meta, dict):
        meta_type = meta.get("type")
        
        if meta_type is None:
            return False
        
        # String value
        if isinstance(meta_type, str):
            return meta_type == "TIMING"
        
        # Enum value (has .value attribute)
        if hasattr(meta_type, 'value'):
            return meta_type.value == "TIMING"
        
        # Enum value (has .name attribute)
        if hasattr(meta_type, 'name'):
            return meta_type.name == "TIMING"
        
        # Fallback: string comparison
        return str(meta_type) == "TIMING"
    
    return False


# ═══════════════════════════════════════════════════════════════════
# TIMING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
TIMING_BY_SUB_SUBDOMAIN = {

    # =======================
    # FINANCE
    # =======================
    "Loan Default Risk": "Loan Repayment Timing",
    "Property Purchase": "Prospects of Property",
    "Prospects of Property": "Prospects of Property",

    # =======================
    # CAREER
    # =======================
    "Job Start Timing": "Job Start Timing",
    "Promotion Timing": "Promotion Timing",
    "Career Shift Timing": "Career Shift Timing",
    "Foreign Career Potential": "Foreign Career Potential",

    # =======================
    # BUSINESS
    # =======================
    "Business Start Timing": "Business Start Timing",
    "Best Periods for Business Growth": "Business Growth Timing",
    "Continue or Shut Down": "Business Recovery Timing",
    "Loan Taking Decision": "Loan Taking Timing",
    "Loan Repayment Decision": "Loan Repayment Timing",

    # =======================
    # HEALTH
    # =======================
    "Disease Occurrence": "Health Risk Timing",
    "Health Risks and Surgery Timing": "Surgery Timing",
    "Cure Timing": "Cure Timing",
    "Surgery Timing": "Surgery Timing",

    # =======================
    # CHILD
    # =======================
    "Prospects of Foreign Education": "Foreign Higher Education Timing",

    # =======================
    # PARENTING (MULTI-TIMING ALLOWED)
    # =======================
    "Childbirth Timing": "Timing of Childbirth",
    "Best Time to Conceive": "Best Time to Conceive",

    # =======================
    # FOREIGN
    # =======================
    "Foreign Settlement Timing": "Foreign Timing",

    # =======================
    # LOVE / RELATIONSHIP
    # =======================
    "Finding Love": "Marriage Timing",
    "Possibility of Reconciliation": "Reconciliation Timing",
    "Love Leading to Marriage": "Marriage Timing",

    # =======================
    # MARRIAGE
    # =======================
    "Marriage Timing": "Marriage Timing",
    "Marriage Promise and Timing": "Marriage Promise and Timing",
    "Divorce Timing": "Divorce Timing",
    "Marriage Advice": "Marriage Timing",

    # =======================
    # GENERAL GUIDANCE
    # =======================
    "Periods of Success": "Success Timing",
    
    # =======================
    # TRAVEL
    # =======================
    "Travel Timing": "Travel Timing",
    "Pilgrimage Timing": "Travel Timing",

    # =======================
    # LEGAL
    # =======================
    "Case Conclusion Timing": "Court Case Conclusion Timing",
    "Court Case Timing": "Court Case Conclusion Timing",
    "Fighting Court Case Timing": "Court Case Conclusion Timing",


    
}


class AstroEngine:
    """Main astrology calculation engine - Modular version"""
    
    def __init__(self):
        self.progress_callbacks = {}
    
    def _ensure_json_serializable(self, obj):
        """
        Recursively convert all datetime objects to strings for JSON serialization.
        This prevents "Object of type datetime is not JSON serializable" errors.
        """
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, dict):
            return {key: self._ensure_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._ensure_json_serializable(item) for item in obj)
        else:
            return obj
    
    def _normalize_timing_windows(self, windows: List[Dict]) -> List[TimingWindow]:
        """Normalize timing windows, ensuring dates are strings"""
        normalized = []
        for w in windows:
            # Ensure start and end are strings, not datetime objects
            start = w["start"]
            if isinstance(start, datetime):
                start = start.strftime("%Y-%m-%d")
            elif not isinstance(start, str):
                start = str(start)
            
            end = w["end"]
            if isinstance(end, datetime):
                end = end.strftime("%Y-%m-%d")
            elif not isinstance(end, str):
                end = str(end)
            
            normalized.append(TimingWindow(
                start=start,
                end=end,
                dasha=w.get("dasha"),
                score=w.get("final_score") or w.get("score"),
                transit_score=w.get("transit_score"),
                final_score=w.get("final_score"),
                age_at_start=w.get("age_at_start"),
                is_overall_best=w.get("is_overall_best", False),
                is_earliest_favorable=w.get("is_earliest_favorable", False)
            ))
        
        return normalized

    def _normalize_planets(self, planets_raw: List[Dict]) -> Dict[str, Dict]:
        """Normalize raw planet data to standard format"""
        out = {}
        for p in planets_raw or []:
            raw_name = p.get("name") or p.get("full_name") or p.get("symbol")
            name = normalize_planet_name(raw_name)
            if not name:
                continue
            
            full_deg = None
            try:
                full_deg = float(p.get("full_degree")) if p.get("full_degree") is not None else None
            except:
                l = p.get("longitude")
                if l:
                    local = dms_to_decimal(l)
                    base = SIGN_BASE.get(p.get("sign") or p.get("rasi") or "", 0)
                    full_deg = normalize_deg_360(base + local)
            
            local_deg = None
            try:
                local_deg = dms_to_decimal(p.get("longitude")) if p.get("longitude") else None
            except:
                pass
            
            sign = p.get("sign") or p.get("rasi") or p.get("zodiac")
            sign_no = p.get("sign_no") or p.get("rasi_no")
            
            retro = str(p.get("is_retro", "")).lower() in ("true", "1", "yes")
            combust = str(p.get("is_combusted", "")).lower() in ("true", "1", "yes")
            
            house = None
            try:
                house = int(p.get("house")) if p.get("house") is not None else None
            except:
                pass
            
            out[name] = {
                "name": name,
                "full_degree": full_deg,
                "global_degree": full_deg,
                "local_degree": local_deg,
                "longitude": p.get("longitude"),
                "sign": sign,
                "rasi_no": int(sign_no) if sign_no is not None else None,
                "house": house,
                "nakshatra": p.get("nakshatra"),
                "nakshatra_pada": p.get("nakshatra_pada"),
                "nakshatra_no": p.get("nakshatra_no"),
                "nakshatra_lord": normalize_planet_name(p.get("nakshatra_lord")),
                "sub_lord": normalize_planet_name(p.get("sub_lord")),
                "sub_sub_lord": normalize_planet_name(p.get("sub_sub_lord")),
                "is_retro": retro,
                "is_combusted": combust,
                "speed": float(p.get("speed") or 0.0),
                "aspects": []
            }
        return out
    
    def _normalize_houses(self, cusps_raw: Dict, planet_in_houses_raw: Dict = None) -> List[Dict]:
        """Normalize house/cusp data"""
        houses = []
        for k, c in (cusps_raw or {}).items():
            try:
                hn = int(k)
            except:
                continue
            
            house_cusp = c.get("house_cusp", {})
            sign = house_cusp.get("sign") or c.get("sign")
            degree_dms = house_cusp.get("degree") or c.get("degree")
            
            local_degree = dms_to_decimal(degree_dms) if degree_dms else None
            base = SIGN_BASE.get(sign, 0) if sign else 0
            global_start = normalize_deg_360(base + local_degree) if local_degree is not None else None
            
            cusp_sign_lord = c.get("cusp_sign_lord", {})
            nak_lord = c.get("cusp_nakshtra_lord", {})
            sub_lord = c.get("cusp_sub_lord", {})
            
            houses.append({
                "house": hn,
                "start_rasi": sign,
                "local_start_degree": local_degree,
                "global_start_degree": global_start,
                "rashi_lord": cusp_sign_lord.get("name") if isinstance(cusp_sign_lord, dict) else cusp_sign_lord,
                "start_nakshatra_lord": nak_lord.get("name") if isinstance(nak_lord, dict) else nak_lord,
                "cusp_sub_lord": sub_lord.get("name") if isinstance(sub_lord, dict) else sub_lord,
                "planets": []
            })
        
        # Add planets to houses
        if planet_in_houses_raw:
            for p_entry in planet_in_houses_raw.get("planets_in_house", []):
                if isinstance(p_entry, dict):
                    house_no = p_entry.get("house")
                    planet_name = p_entry.get("planet") or p_entry.get("name")
                    for h in houses:
                        if h["house"] == house_no:
                            h["planets"].append({"name": normalize_planet_name(planet_name)})
        
        houses.sort(key=lambda h: h["house"])
        return houses
    
    
    def _parse_dasha_dates(self, paryantar: Dict) -> List[Dict]:
        """
        Parse dasha periods from API response (handles multiple formats including array format)
        
        The Vedic API returns paryantardasha in array format where:
        - paryantardasha: [[["Sa/Sa/Sa", "Sa/Sa/Me", ...], [...]], ...]
        - paryantardasha_order: [[["date1", "date2", ...], [...]], ...]
        - dates[i] = END of period i / START of period i+1
    
        CRITICAL: Period from dates[i-1] to dates[i] corresponds to names[i]
        (because dates[i] is when period names[i] ENDS)
        """
        flat_dasha = []
        
        if not paryantar:
            logger.warning("_parse_dasha_dates: No paryantar data received")
            return flat_dasha
        
        # Handle nested structure from fetch_extended_dasha_for_timing
        data = paryantar.get("data", paryantar)
        # 🔥 UNWRAP API RESPONSE
        if isinstance(data, dict) and "response" in data:
            data = data["response"]

        logger.debug(f"DEBUG keys at parser entry: {list(data.keys())}")

        # ═══════════════════════════════════════════════════════════════════
        # NEW: Handle array format from Vedic API
        # ═══════════════════════════════════════════════════════════════════
        if "paryantardasha" in data and "paryantardasha_order" in data:
            logger.info("Parsing paryantardasha array format from Vedic API")
            
            paryantar_names = data.get("paryantardasha", [])
            paryantar_dates = data.get("paryantardasha_order", [])
            
            if not paryantar_names or not paryantar_dates:
                logger.warning("Empty paryantardasha arrays")
                return flat_dasha
            
            # Flatten nested arrays
            all_dasha_names = []
            all_dasha_dates = []
            
            for maha_group_names, maha_group_dates in zip(paryantar_names, paryantar_dates):
                for antara_group_names, antara_group_dates in zip(maha_group_names, maha_group_dates):
                    for dasha_name, date_str in zip(antara_group_names, antara_group_dates):
                        all_dasha_names.append(dasha_name)
                        all_dasha_dates.append(date_str)
            
            logger.info(f"Flattened {len(all_dasha_names)} dasha periods from array format")
            
            # ✅ FIXED: Pair names[i] with dates[i-1] to dates[i]
            for i in range(1, len(all_dasha_dates)):
                dasha_name = all_dasha_names[i]
                start_str = all_dasha_dates[i - 1]
                end_str = all_dasha_dates[i]
                
                try:
                    # Parse date string (format: "Mon Jun 30 2038")
                    start_dt = datetime.strptime(start_str, "%a %b %d %Y")
                    end_dt = datetime.strptime(end_str, "%a %b %d %Y")
                    
                    # Parse dasha name (format: "Sa/Ve/Mo" or abbreviations)
                    parts = dasha_name.split("/")
                    if len(parts) >= 3:
                        md = normalize_planet_name(parts[0]) or ""
                        ad = normalize_planet_name(parts[1]) or ""
                        pd = normalize_planet_name(parts[2]) or ""
                        
                        dasha_full_name = f"{md}-{ad}-{pd}"
                        
                        flat_dasha.append({
                            "dasha": dasha_full_name,
                            "start": start_dt,
                            "end": end_dt,
                            "md": md, "ad": ad, "pd": pd,
                            "maha": md, "antara": ad, "paryantar": pd
                        })
                        
                except Exception as e:
                    logger.debug(f"Failed to parse dasha date: {e} - {dasha_name}: {start_str} to {end_str}")
                    continue
            
            logger.info(f"Parsed {len(flat_dasha)} valid dasha periods from array format")
            if flat_dasha:
                first = flat_dasha[0]
                last = flat_dasha[-1]
                logger.info(f"First: {first['dasha']} from {first['start']} to {first['end']}")
                logger.info(f"Last: {last['dasha']} from {last['start']} to {last['end']}")
            
            return flat_dasha
        
        # ═══════════════════════════════════════════════════════════════════
        # FALLBACK: Handle dict format (old API format)
        # ═══════════════════════════════════════════════════════════════════
        paryantar_list = []
        if isinstance(data, dict):
            paryantar_list = (
                data.get("paryantar_dasha", []) or
                data.get("paryantardasha", []) or
                []
            )
        
        if not paryantar_list and isinstance(paryantar, dict):
            paryantar_list = paryantar.get("paryantardasha", [])
        
        logger.info(f"_parse_dasha_dates: Found {len(paryantar_list)} entries to parse (dict format)")
        
        for entry in paryantar_list:
            if isinstance(entry, dict):
                md = normalize_planet_name(
                    entry.get("md_name") or entry.get("maha_dasha") or entry.get("md") or entry.get("maha") or ""
                ) or ""
                ad = normalize_planet_name(
                    entry.get("ad_name") or entry.get("antar_dasha") or entry.get("ad") or entry.get("antara") or ""
                ) or ""
                pd = normalize_planet_name(
                    entry.get("pd_name") or entry.get("pratyantara_dasha") or entry.get("pd") or entry.get("paryantar") or ad or ""
                ) or ""
                
                dasha_name = "-".join(filter(None, [md, ad, pd]))
                
                start_str = (
                    entry.get("prd_start") or 
                    entry.get("start_date") or 
                    entry.get("start") or
                    entry.get("pd_start") or
                    entry.get("from")
                )
                end_str = (
                    entry.get("prd_end") or 
                    entry.get("end_date") or 
                    entry.get("end") or
                    entry.get("pd_end") or
                    entry.get("to")
                )
                
                if start_str and end_str:
                    try:
                        start_str = str(start_str)
                        end_str = str(end_str)
                        
                        if "T" in start_str:
                            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                        elif "/" in start_str:
                            start_dt = datetime.strptime(start_str, "%d/%m/%Y")
                            end_dt = datetime.strptime(end_str, "%d/%m/%Y")
                        elif "-" in start_str:
                            start_dt = datetime.fromisoformat(start_str[:19])
                            end_dt = datetime.fromisoformat(end_str[:19])
                        else:
                            logger.debug(f"Unknown date format: {start_str}")
                            continue
                        
                        if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo:
                            start_dt = start_dt.replace(tzinfo=None)
                        if hasattr(end_dt, 'tzinfo') and end_dt.tzinfo:
                            end_dt = end_dt.replace(tzinfo=None)
                        
                        flat_dasha.append({
                            "dasha": dasha_name,
                            "period": dasha_name,
                            "start": start_dt,
                            "end": end_dt,
                            "md": md, "ad": ad, "pd": pd,
                            "maha": md, "antara": ad, "paryantar": pd
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse dasha date: {e} - start: {start_str}, end: {end_str}")
        
        logger.info(f"_parse_dasha_dates: Parsed {len(flat_dasha)} valid dasha periods (dict format)")
        
        if flat_dasha:
            first = flat_dasha[0]
            logger.info(f"First parsed period: {first['dasha']} from {first['start']} to {first['end']}")
        
        return flat_dasha 
        
    
    def _limit_dasha_to_years(
        self,
        flat_dasha: List[Dict],
        years: int = 7
    ) -> List[Dict]:
        """
        Limit dasha list to a window around 'now' without breaking periods.
        """
        now = datetime.now()
        start_cutoff = now - timedelta(days=2 * 365)
        end_cutoff = now + timedelta(days=years * 365)

        # Always sort before filtering
        flat_dasha = sorted(flat_dasha, key=lambda x: x["start"])

        limited_dasha = []
        for d in flat_dasha:
            start = d["start"]
            end = d["end"]

            # Keep if it overlaps the window
            if end >= start_cutoff and start <= end_cutoff:
                limited_dasha.append(d)

        return limited_dasha

    def _filter_dasha_periods(self, flat_dasha: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter dasha periods: 2Y past + ALL future from extended fetch.
        Now gets 10 years from fetch_extended_dasha_for_timing!
        """
        now = datetime.now()
        two_years_ago = now - timedelta(days=730)
        
        logger.info("=" * 80)
        logger.info("📊 FILTERING DASHA PERIODS - EXTENDED TIMELINE (10 YEARS)")
        logger.info(f"   From: {two_years_ago.strftime('%Y-%m-%d')}")
        logger.info(f"   To: [All future from extended fetch]")
        logger.info("=" * 80)
        
        past_dasha = []
        future_dasha = []
        current_dasha_list = []
    
        for d in flat_dasha:
            start = d.get("start")
            end = d.get("end")
            
            if not start or not end:
                continue
            
            # Timezone-naive
            if hasattr(start, 'tzinfo') and start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            if hasattr(end, 'tzinfo') and end.tzinfo is not None:
                end = end.replace(tzinfo=None)
            
            # Only skip periods before 2 years
            if end < two_years_ago:
                continue
            
            entry = {
                "dasha_name": d.get("dasha", ""),
                "date_range": {
                    "start": start.strftime("%Y-%m-%d"),
                    "end": end.strftime("%Y-%m-%d")
                }
            }
            
            # Categorize
            if end < now:
                past_dasha.append(entry)
            elif start <= now <= end:
                current_dasha_list.append(entry)
            else:
                future_dasha.append(entry)
        
        logger.info(f"✅ Past: {len(past_dasha)}, Current: {len(current_dasha_list)}, Future: {len(future_dasha)}")
        logger.info("=" * 80)
    
        # Return ALL (no limits!)
        all_future = current_dasha_list + future_dasha
        return past_dasha, all_future

    
    async def _get_timing_windows(
        self,
        flat_dasha: List[Dict],
        dob_dt: datetime,
        planets: Dict,
        houses: List,
        domain: str,
        timing_name: str,
        enable_transit: bool = False,
        dob: str = None,
        tob: str = None,
        sex: str = None,
        lat: float = None,
        lon: float = None,
        tzone: float = 5.5
    ) -> List[Dict]:
        """
        Calculate timing windows using full KP methodology.
        
        Uses the KP timing engine which implements:
        - Ruling planet extraction and filtering
        - KP signification scoring (positive/negative/net)
        - Age-based filtering
        - KP positive validation
        - Key planet score boost
        - Retrograde delay tagging
        - Optional: Transit scoring (OPTIMIZED with parallel API calls!)
        """
        try:
            # Check if transit scoring should be used
            if enable_transit and all([dob, tob, sex, lat, lon]):
                return await self._get_timing_windows_with_transit(
                    flat_dasha=flat_dasha,
                    dob_dt=dob_dt,
                    planets=planets,
                    houses=houses,
                    domain=domain,
                    timing_name=timing_name,
                    dob=dob,
                    tob=tob,
                    sex=sex,
                    lat=lat,
                    lon=lon,
                    tzone=tzone
                )
            
            # Use the comprehensive KP timing engine (NOTEBOOK-MATCHING logic)
            timing_windows = kp_timing_engine.calculate_timing_windows(
                dba_list=flat_dasha,
                dob=dob_dt,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=10
            )
            
            logger.info(f"KP Timing Engine generated {len(timing_windows)} windows for {timing_name}")
            
            # Log ruling planets for debugging
            ruling_planets = kp_timing_engine.get_ruling_planets(planets)
            logger.debug(f"Ruling planets: {ruling_planets}")
            
            return timing_windows
            
        except Exception as e:
            logger.exception(f"KP Timing Engine error: {e}")
            # Fallback to basic scoring if timing engine fails
            return self._get_timing_windows_fallback(
                flat_dasha, dob_dt, planets, houses, domain, timing_name
            )
    
    async def _get_timing_windows_with_transit(
        self,
        flat_dasha: List[Dict],
        dob_dt: datetime,
        planets: Dict,
        houses: List,
        domain: str,
        timing_name: str,
        dob: str,
        tob: str,
        sex: str,
        lat: float,
        lon: float,
        tzone: float = 5.5
    ) -> List[Dict]:
        """
        Calculate timing windows with transit scoring using OPTIMIZED parallel API calls.
        """
        try:
            # Step 1: Get timing windows WITHOUT transit scoring first
            timing_windows = get_top_timing_windows(
                dba_list=flat_dasha,
                dob=dob_dt,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=10
            )
            
            logger.info(f"KP Timing Engine generated {len(timing_windows)} base windows")
            
            # Step 2: Apply transit scores using OPTIMIZED parallel async function
            if timing_windows:
                logger.info("🚀 Applying transit scores with PARALLEL API calls...")
                timing_windows = await apply_transit_scores_to_windows_async(
                    windows=timing_windows,
                    dob=dob,
                    tob=tob,
                    sex=sex,
                    lat=lat,
                    lon=lon,
                    tzone=str(tzone)
                )
                logger.info(f"✅ Transit scoring complete - {len(timing_windows)} windows scored")
            
            return timing_windows
            
        except Exception as e:
            logger.warning(f"Transit timing failed, falling back to basic: {e}")
            logger.exception("Full error trace:")
            # Fallback to without transit
            return kp_timing_engine.calculate_timing_windows(
                dba_list=flat_dasha,
                dob=dob_dt,
                planets=planets,
                houses=houses,
                domain=domain,
                timing_name=timing_name,
                max_windows=10
            )
    
    def _get_timing_windows_fallback(
        self,
        flat_dasha: List[Dict],
        dob_dt: datetime,
        planets: Dict,
        houses: List,
        domain: str,
        timing_name: str
    ) -> List[Dict]:
        """Fallback basic timing calculation if KP engine fails"""
        timing_windows = []
        now = datetime.now()
        
        rules = TIMING_RULES.get(timing_name, {})
        positive_houses = set(rules.get("positive_houses", set()))
        supportive_houses = set(rules.get("supportive_houses", set()))
        key_planets = set(rules.get("key_planets", set()))
        
        age_range = VALID_AGE_RANGES.get(domain, (18, 70))
        min_age, max_age = age_range
        
        # Create house lookup
        house_lookup = {}
        for h in houses:
            house_lookup[h["house"]] = h
        
        # Check each dasha period
        for d in flat_dasha:
            start = d.get("start")
            end = d.get("end")
            
            if not start or not end:
                continue
            
            # Ensure timezone-naive
            if hasattr(start, 'tzinfo') and start.tzinfo is not None:
                start = start.replace(tzinfo=None)
            if hasattr(end, 'tzinfo') and end.tzinfo is not None:
                end = end.replace(tzinfo=None)
            
            # Check age validity
            age_at_start = (start - dob_dt).days / 365.25
            if age_at_start < min_age or age_at_start > max_age:
                continue
            
            # Only future periods
            if end < now:
                continue
            
            # Score the dasha period
            score = 0
            dasha_planets = []
            
            for level in ["md", "ad", "pd", "maha", "antara", "paryantar"]:
                planet_name = normalize_planet_name(d.get(level, ""))
                if planet_name and planet_name not in dasha_planets:
                    dasha_planets.append(planet_name)
                    
                    # Check if planet is key planet
                    if planet_name in key_planets:
                        score += 10
                    
                    # Check planet's house
                    p_data = planets.get(planet_name, {})
                    p_house = p_data.get("house")
                    if p_house:
                        if p_house in positive_houses:
                            score += 8
                        elif p_house in supportive_houses:
                            score += 4
            
            # Check 7th CSL connection for Marriage
            if timing_name == "Marriage Timing":
                h7 = house_lookup.get(7, {})
                csl = normalize_planet_name(h7.get("cusp_sub_lord"))
                if csl and csl in dasha_planets:
                    score += 15
            
            if score > 0:
                timing_windows.append({
                    "start": start.strftime("%Y-%m-%d"),
                    "end": end.strftime("%Y-%m-%d"),
                    "dasha": d.get("dasha", ""),
                    "score": score,
                    "age_at_start": round(age_at_start, 1)
                })
        
        # Sort by score descending
        timing_windows.sort(key=lambda w: w["score"], reverse=True)
        return timing_windows[:10]
    
    # ═══════════════════════════════════════════════════════════════════
    # ✅ NEW: TWO-PERSON TIMING FOR KUNDALI MATCHING
    # ═══════════════════════════════════════════════════════════════════
    async def _get_two_person_timing_windows(
        self,
        person1_flat_dasha: List[Dict],
        person1_dob_dt: datetime,
        person1_planets: Dict,
        person1_houses: List,
        person2_flat_dasha: List[Dict],
        person2_dob_dt: datetime,
        person2_planets: Dict,
        person2_houses: List,
        domain: str,
        timing_name: str,
        enable_transit: bool = False,
        person1_birth_data: Dict = None,
        person2_birth_data: Dict = None,
        min_overlap_days: int = 30
    ) -> Dict[str, List[Dict]]:
        """
        Calculate timing windows for both people and find overlapping favorable periods.
        
        This is specifically for Kundali Matching to find the best marriage timing
        that works for BOTH partners.
        
        Returns:
            Dict with keys:
            - "person1_windows": Individual windows for person 1
            - "person2_windows": Individual windows for person 2
            - "overlapping_windows": Windows favorable for BOTH (sorted by combined score)
        """
        try:
            # Calculate person 1 timing windows
            logger.info(f"🔍 Calculating timing for Person 1 (Boy)...")
            person1_windows = await self._get_timing_windows(
                flat_dasha=person1_flat_dasha,
                dob_dt=person1_dob_dt,
                planets=person1_planets,
                houses=person1_houses,
                domain=domain,
                timing_name=timing_name,
                enable_transit=enable_transit,
                dob=person1_birth_data.get("dob") if person1_birth_data else None,
                tob=person1_birth_data.get("tob") if person1_birth_data else None,
                sex=person1_birth_data.get("sex") if person1_birth_data else None,
                lat=person1_birth_data.get("lat") if person1_birth_data else None,
                lon=person1_birth_data.get("lon") if person1_birth_data else None,
                tzone=float(person1_birth_data.get("timezone", 5.5)) if person1_birth_data else 5.5
            )
            logger.info(f"   → Person 1: {len(person1_windows)} windows found")

            # Calculate person 2 timing windows
            logger.info(f"🔍 Calculating timing for Person 2 (Girl)...")
            person2_windows = await self._get_timing_windows(
                flat_dasha=person2_flat_dasha,
                dob_dt=person2_dob_dt,
                planets=person2_planets,
                houses=person2_houses,
                domain=domain,
                timing_name=timing_name,
                enable_transit=enable_transit,
                dob=person2_birth_data.get("dob") if person2_birth_data else None,
                tob=person2_birth_data.get("tob") if person2_birth_data else None,
                sex=person2_birth_data.get("sex") if person2_birth_data else None,
                lat=person2_birth_data.get("lat") if person2_birth_data else None,
                lon=person2_birth_data.get("lon") if person2_birth_data else None,
                tzone=float(person2_birth_data.get("timezone", 5.5)) if person2_birth_data else 5.5
            )
            logger.info(f"   → Person 2: {len(person2_windows)} windows found")
            
            # Find overlapping favorable periods
            logger.info(f"🔄 Finding overlapping favorable periods (min {min_overlap_days} days)...")
            overlaps = find_overlapping_timing_windows(
                person1_windows,
                person2_windows,
                min_overlap_days=min_overlap_days,
                max_results=10
            )
            
            overlapping_windows = convert_overlaps_to_timing_windows(overlaps)
            logger.info(f"   → Found {len(overlapping_windows)} overlapping periods")
            
            if overlapping_windows:
                best = overlapping_windows[0]
                logger.info(f"   → Best period: {best['start']} to {best['end']} "
                           f"(Score: {best.get('score', best.get('final_score', 'N/A'))}, Quality: {best.get('quality', 'N/A')})")
            else:
                logger.warning("   → No overlapping favorable periods found!")
            
            return {
                "person1_windows": person1_windows,
                "person2_windows": person2_windows,
                "overlapping_windows": overlapping_windows
            }
            
        except Exception as e:
            logger.exception(f"Two-person timing calculation error: {e}")
            return {
                "person1_windows": [],
                "person2_windows": [],
                "overlapping_windows": []
            }
    
    def _run_domain_evaluation(
        self,
        domain: str,
        subtopic: str,
        planets: Dict,
        houses: List,
        vedic_planets: Optional[Dict] = None,
        vedic_houses: Optional[List] = None,
        sub_subdomain: str = "",
        meta: QueryMeta = None,
        planets2: Optional[Dict] = None,
        houses2: Optional[List] = None,
        vedic_planets2: Optional[Dict] = None,
        vedic_houses2: Optional[List] = None,
        person1_name: Optional[str] = None,
        person2_name: Optional[str] = None,
        question: str = "",
        timing_windows: Optional[List] = None,
        current_dasha: Optional[Dict] = None,
        dob: Optional[str] = None,

    ) -> tuple[List[str], Dict]:
        """
        Run domain-specific evaluation using modular evaluators
        """
        points = []
        additional_data = {}
    
        # Get evaluator from registry
        evaluator = get_evaluator(domain, subtopic)
        logger.debug("🪐 KP PLANETS (dict): %s", planets)
        logger.debug("🏠 KP HOUSES (list): %s", houses)
        logger.debug(f"timing:{timing_windows}")

        if evaluator:
            try:
                # Pass all parameters including question to evaluator
                result = evaluator.evaluate(
                    planets,
                    houses,
                    vedic_planets=vedic_planets,
                    vedic_houses=vedic_houses,
                    sub_subdomain=sub_subdomain,
                    meta=meta,
                    question=question,
                    timing_windows=timing_windows,
                    current_dasha=current_dasha,
                    dob=dob,
                    planets2=planets2,
                    houses2=houses2,
                    vedic_planets2=vedic_planets2,
                    vedic_houses2=vedic_houses2,
                    person1_name=person1_name,
                    person2_name=person2_name,
                )
            
                if hasattr(result, 'technical_points'):
                    points.extend(result.technical_points)
                elif isinstance(result, dict):
                    points.extend(result.get("technical_points", []))
                elif isinstance(result, list):
                    points.extend(result)
            
                # Extract additional_data from EvaluationResult
                if hasattr(result, 'additional_data'):
                    additional_data = result.additional_data
                elif isinstance(result, dict) and 'additional_data' in result:
                    additional_data = result['additional_data']
                
            except Exception as e:
                logger.exception(f"Evaluator error for {domain}/{subtopic}: {e}")
        else:
            logger.debug(f"No evaluator found for {domain}/{subtopic}")
    
        return points, additional_data
    
    # ═══════════════════════════════════════════════════════════════════
    # ✅ FIXED: Compatibility evaluation with proper parameter handling
    # ═══════════════════════════════════════════════════════════════════
    def _get_default_compatibility_result(self) -> Dict[str, Any]:
        """Return default compatibility result structure"""
        return {
            "overall_score": None,
            "relationship_score": None,
            "manglik_status": {"person1": None, "person2": None},
            "detailed_analysis": None
        }
    
    def _run_compatibility_evaluation(
        self,
        domain: str,
        planets1: Dict,
        houses1: List,
        planets2: Dict,
        houses2: List,
        sex1: str,
        sex2: str,
        vedic_planets1: Optional[Dict] = None,
        vedic_houses1: Optional[List] = None,
        vedic_planets2: Optional[Dict] = None,
        vedic_houses2: Optional[List] = None,
        kundali_milan_data: Optional[Dict] = None,  # ✅ NEW: For accurate Manglik data
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run compatibility evaluation using modular evaluators.
        
        TRULY SAFE VERSION: 
        - Uses POSITIONAL arguments for base 4 params (works with any naming)
        - Only adds extra kwargs if evaluator accepts them
        - Has multiple fallbacks
        - Works with both Kundali Matching and Marriage Compatibility evaluators
        - Merges accurate Manglik data from kundali_milan_api if available
        """
        # ═══════════════════════════════════════════════════════════════
        # DEBUG LOGGING
        # ═══════════════════════════════════════════════════════════════
        logger.info("=" * 60)
        logger.info("🔍 _run_compatibility_evaluation - TRULY SAFE VERSION")
        logger.info("=" * 60)
        logger.info(f"Domain: {domain}")
        logger.info(f"Person 1 - planets: {bool(planets1)}, houses: {bool(houses1)}, sex: {sex1}")
        logger.info(f"Person 2 - planets: {bool(planets2)}, houses: {bool(houses2)}, sex: {sex2}")
        logger.info(f"Vedic P1: {bool(vedic_planets1)}, Vedic H1: {bool(vedic_houses1)}")
        logger.info(f"Vedic P2: {bool(vedic_planets2)}, Vedic H2: {bool(vedic_houses2)}")
        logger.info(f"Kundali Milan API data: {bool(kundali_milan_data)}")
        
        # Verify person2 data is different from person1
        if planets1 and planets2:
            # Try to import _p helper, or define inline
            def _get_planet(planets, name):
                """Helper to get planet data"""
                if not planets:
                    return None
                # Try direct key first
                if name in planets:
                    return planets[name]
                # Try case-insensitive
                for k, v in planets.items():
                    if k.lower() == name.lower():
                        return v
                return None
            
            p1_mars = _get_planet(planets1, "Mars")
            p2_mars = _get_planet(planets2, "Mars")
            p1_moon = _get_planet(planets1, "Moon")
            p2_moon = _get_planet(planets2, "Moon")
            
            logger.info(f"P1 Mars house: {p1_mars.get('house') if p1_mars else 'N/A'}")
            logger.info(f"P2 Mars house: {p2_mars.get('house') if p2_mars else 'N/A'}")
            logger.info(f"P1 Moon: {p1_moon.get('sign') if p1_moon else 'N/A'}, house: {p1_moon.get('house') if p1_moon else 'N/A'}")
            logger.info(f"P2 Moon: {p2_moon.get('sign') if p2_moon else 'N/A'}, house: {p2_moon.get('house') if p2_moon else 'N/A'}")
            
            # Check for identical data (bug indicator)
            if (p1_mars and p2_mars and p1_moon and p2_moon and
                p1_mars.get('house') == p2_mars.get('house') and
                p1_moon.get('sign') == p2_moon.get('sign') and
                p1_moon.get('house') == p2_moon.get('house')):
                logger.warning("⚠️ WARNING: Person 1 and 2 data appears IDENTICAL!")
                logger.warning("   This likely indicates person2 data is not being passed correctly!")
        
        logger.info("=" * 60)
        
        # Get compatibility evaluator from registry
        compat_evaluator = get_compatibility_evaluator(domain)
        
        result = self._get_default_compatibility_result()
        
        if compat_evaluator:
            evaluator_name = type(compat_evaluator).__name__
            logger.info(f"✅ Found evaluator: {evaluator_name}")
            
            try:
                # ═══════════════════════════════════════════════════════════════
                # Check evaluator's method signature
                # ═══════════════════════════════════════════════════════════════
                eval_method = compat_evaluator.evaluate_compatibility
                sig = inspect.signature(eval_method)
                params = list(sig.parameters.items())
                param_names = [name for name, _ in params]
                
                # Check if evaluator accepts **kwargs
                has_var_keyword = any(
                    p.kind == inspect.Parameter.VAR_KEYWORD 
                    for _, p in params
                )
                
                # Check if evaluator accepts specific params
                accepts_sex = "sex1" in param_names or "sex2" in param_names
                accepts_vedic = "vedic_planets1" in param_names
                
                logger.info(f"Evaluator params: {param_names}")
                logger.info(f"Accepts **kwargs: {has_var_keyword}")
                logger.info(f"Accepts sex1/sex2: {accepts_sex}")
                logger.info(f"Accepts vedic data: {accepts_vedic}")
                
                # ═══════════════════════════════════════════════════════════════
                # STRATEGY 1: Evaluator accepts **kwargs (Marriage Compatibility Enhanced)
                # Pass everything using keyword arguments
                # ═══════════════════════════════════════════════════════════════
                if has_var_keyword:
                    logger.info("Using STRATEGY 1: Full kwargs (evaluator accepts **kwargs)")
                    result = eval_method(
                        planets1=planets1,
                        houses1=houses1,
                        planets2=planets2,
                        houses2=houses2,
                        sex1=sex1,
                        sex2=sex2,
                        vedic_planets1=vedic_planets1,
                        vedic_houses1=vedic_houses1,
                        vedic_planets2=vedic_planets2,
                        vedic_houses2=vedic_houses2,
                        **kwargs
                    )
                
                # ═══════════════════════════════════════════════════════════════
                # STRATEGY 2: Evaluator accepts sex params but not **kwargs
                # ═══════════════════════════════════════════════════════════════
                elif accepts_sex:
                    logger.info("Using STRATEGY 2: With sex params")
                    if accepts_vedic:
                        result = eval_method(
                            planets1, houses1, planets2, houses2,
                            sex1=sex1, sex2=sex2,
                            vedic_planets1=vedic_planets1,
                            vedic_houses1=vedic_houses1,
                            vedic_planets2=vedic_planets2,
                            vedic_houses2=vedic_houses2
                        )
                    else:
                        result = eval_method(
                            planets1, houses1, planets2, houses2,
                            sex1=sex1, sex2=sex2
                        )
                
                # ═══════════════════════════════════════════════════════════════
                # STRATEGY 3: Evaluator only accepts basic 4 params (Kundali Matching)
                # Use POSITIONAL arguments to avoid name mismatch
                # ═══════════════════════════════════════════════════════════════
                else:
                    logger.info("Using STRATEGY 3: Positional args only (basic evaluator)")
                    result = eval_method(planets1, houses1, planets2, houses2)
                
                logger.info(f"✅ Evaluator returned result with overall_score: {result.get('overall_score')}")
                logger.info(f"✅ Evaluator manglik_status: {result.get('manglik_status')}")
                logger.info(f"✅ Evaluator result keys: {list(result.keys())}")
                
            except TypeError as e:
                logger.warning(f"TypeError, trying positional fallback: {e}")
                try:
                    result = compat_evaluator.evaluate_compatibility(
                        planets1, houses1, planets2, houses2
                    )
                    logger.info(f"✅ Positional fallback succeeded, overall_score: {result.get('overall_score')}")
                except Exception as e2:
                    logger.error(f"❌ Positional fallback also failed: {e2}")
                    logger.error(f"❌ Returning default result due to fallback failure")
                    
            except Exception as e:
                logger.error(f"❌ COMPATIBILITY EVALUATOR ERROR for {domain}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                logger.error(f"❌ Returning default result due to exception")
        else:
            logger.warning(f"❌ No compatibility evaluator found for domain: {domain}")
        
        # ═══════════════════════════════════════════════════════════════
        # MERGE ACCURATE MANGLIK DATA FROM KUNDALI MILAN API
        # This ensures correct Manglik status even if evaluator fails/returns null
        # ═══════════════════════════════════════════════════════════════
        if kundali_milan_data:
            logger.info("📊 Merging accurate Manglik data from Kundali Milan API")
            
            manglik_data = kundali_milan_data.get("match_details", {}).get("manglik", {})
            
            # Extract boy's Manglik status
            boy_manglik = manglik_data.get("boy", {}).get("response", {})
            boy_is_manglik = (
                boy_manglik.get("is_pitr_manglik", False) or 
                boy_manglik.get("is_chandra_manglik", False) or 
                boy_manglik.get("is_manglik", False)
            )
            boy_mars_house = boy_manglik.get("mars_house")
            
            # Extract girl's Manglik status  
            girl_manglik = manglik_data.get("girl", {}).get("response", {})
            girl_is_manglik = (
                girl_manglik.get("is_pitr_manglik", False) or 
                girl_manglik.get("is_chandra_manglik", False) or 
                girl_manglik.get("is_manglik", False)
            )
            girl_mars_house = girl_manglik.get("mars_house")
            
            logger.info(f"📊 API Manglik - Boy: {boy_is_manglik} (Mars H{boy_mars_house}), Girl: {girl_is_manglik} (Mars H{girl_mars_house})")
            
            # Update result with accurate Manglik status from API
            # This overrides any incorrect values from the evaluator
            if result.get("manglik_status") is None or result["manglik_status"].get("person1") is None:
                result["manglik_status"] = {
                    "person1": boy_is_manglik,
                    "person2": girl_is_manglik,
                    "person1_mars_house": boy_mars_house,
                    "person2_mars_house": girl_mars_house,
                    "person1_details": boy_manglik,
                    "person2_details": girl_manglik,
                    "source": "kundali_milan_api"
                }
                logger.info(f"✅ Set Manglik from API: Person1={boy_is_manglik}, Person2={girl_is_manglik}")
            
            # Also add Ashtakoot score if available
            ashtakoot = kundali_milan_data.get("match_details", {}).get("ashtakoot", {}).get("response", {})
            if ashtakoot:
                ashtakoot_score = ashtakoot.get("score", 0)
                result["ashtakoot_score"] = ashtakoot_score
                result["ashtakoot_details"] = ashtakoot
                
                # Update overall_score if not set
                if result.get("overall_score") is None:
                    # Convert Ashtakoot score (out of 36) to percentage
                    result["overall_score"] = round((ashtakoot_score / 36) * 100, 1)
                    logger.info(f"✅ Set overall_score from Ashtakoot: {ashtakoot_score}/36 = {result['overall_score']}%")
        
        # ═══════════════════════════════════════════════════════════════
        # Final logging
        # ═══════════════════════════════════════════════════════════════
        logger.info("=" * 60)
        logger.info("✅ COMPATIBILITY EVALUATION COMPLETED")
        logger.info(f"Overall Score: {result.get('overall_score')}")
        logger.info(f"Manglik Status: {result.get('manglik_status')}")
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'NOT A DICT'}")
        logger.info("=" * 60)
        
        return result
    
    async def process_prediction(
        self,
        response_id: str,
        name: str,
        sex: str,
        dob: str,
        tob: str,
        lat: float,
        lon: float,
        domain: str,
        subtopics: List[str],
        person2: Optional[Dict] = None,
        progress_callback=None,
        language: str = "Hindi",
        timezone: float = 5.5
    ) -> Dict[str, Any]:
        """Process a prediction request using modular architecture"""
        # DEBUG: Trace domain and subtopics at entry point
        print(f"🔍 [ENTRY DEBUG] domain='{domain}', subtopics={subtopics}, person2={bool(person2)}")
        logger.info(f"🔍 [ENTRY DEBUG] domain='{domain}', subtopics={subtopics}, person2={bool(person2)}")
        
        try:
            if progress_callback:
                await progress_callback(10, "Fetching astrological data...")
            
            # Fetch data from APIs
            cuspal_resp = kp_api.fetch_cuspal(name, sex, dob, tob, lat, lon, tz=timezone)
            planet_resp = kp_api.fetch_planetary_positions(name, sex, dob, tob, lat, lon, tz=timezone)
            
            cusps_raw = cuspal_resp.get("data", {}).get("table_data", {})
            planet_in_houses_raw = cuspal_resp.get("data", {}).get("data", {})
            planets_raw = planet_resp.get("data", {}).get("planets", [])
            
            if progress_callback:
                await progress_callback(20, "Normalizing chart data...")
            
            planets, houses, planet_in_houses = kp_api.unify_new_api_to_old_format(
                cusps_raw,
                planet_in_houses_raw,
                planets_raw
            )
            
            
            if progress_callback:
                await progress_callback(30, "Fetching dasha periods...")
            
            # Fetch dasha data with error handling
            paryantar = {}
            planet_details = {}
            d9_chart = {}
            
            # Fetch extended dasha (10 years)
            try:
                logger.info("📊 Fetching extended dasha (10 years) for comprehensive analysis...")
                extended_dasha = vedic_api.fetch_extended_dasha_for_timing(
                    dob, tob, lat, lon, years_ahead=10, tz=timezone
                )
                extended_flat_dasha = self._parse_dasha_dates(extended_dasha)
                extended_flat_dasha = self._limit_dasha_to_years(extended_flat_dasha, years=7)
                
                flat_dasha = extended_flat_dasha if extended_flat_dasha else []
                logger.info(f"✅ Extended dasha: {len(flat_dasha)} periods")
            except Exception as e:
                logger.warning(f"Failed to fetch extended dasha: {e}")
                flat_dasha = []

            # Parse and filter dasha (now has 10 years!)
            past_dasha, future_dasha = self._filter_dasha_periods(flat_dasha)

            # Extract current dasha and timeline for LLM
            current_dasha = future_dasha[0] if future_dasha else None
            dasha_timeline = {
                "past_2_years": past_dasha[-20:] if len(past_dasha) > 20 else past_dasha,
                "current": [current_dasha] if current_dasha else [],
                "next_10_years": future_dasha[:100] if len(future_dasha) > 100 else future_dasha
            }

            if current_dasha:
                logger.info(f"📊 Current dasha: {current_dasha.get('dasha_name', 'Unknown')} "
                    f"({current_dasha.get('date_range', {}).get('start')} to "
                    f"{current_dasha.get('date_range', {}).get('end')})")
                logger.info(f"📊 Timeline: {len(dasha_timeline['past_2_years'])} past, "
                    f"{len(dasha_timeline['next_10_years'])} future periods")

            try:
                planet_details = vedic_api.fetch_planet_details(dob, tob, lat, lon, tz=timezone)
            except Exception as e:
                logger.warning(f"Failed to fetch planet details: {e}")
            
            try:
                d9_chart = vedic_api.fetch_divisional_chart(dob, tob, lat, lon, "D9", tz=timezone)
            except Exception as e:
                logger.warning(f"Failed to fetch D9 chart: {e}")
            
            # Parse Vedic API data for LLM calls (separate from KP data used for timing)
            vedic_planets_for_llm = None
            vedic_houses_for_llm = None
            
            if VEDIC_PARSER_AVAILABLE and planet_details:
                try:
                    vedic_planets_for_llm, vedic_metadata = parse_vedic_api_response(
                        {"response": planet_details}
                    )
                    ascendant_data = vedic_metadata.get("ascendant") if vedic_metadata else None
                    vedic_houses_for_llm = create_houses_from_planets(
                        vedic_planets_for_llm, 
                        ascendant_data
                    )
                    logger.info(f"✅ Parsed Vedic API data for LLM: {len(vedic_planets_for_llm)} planets, {len(vedic_houses_for_llm)} houses")
                except Exception as e:
                    logger.warning(f"Failed to parse Vedic API data for LLM: {e}")
                    vedic_planets_for_llm = None
                    vedic_houses_for_llm = None
            
            if progress_callback:
                await progress_callback(40, "Evaluating astrological factors...")
            
            # Domain evaluation using modular evaluators
            all_points = []
            evaluator_additional_data = {}
            
            for subtopic in subtopics:
                points, additional_data = self._run_domain_evaluation(
                    domain=domain,
                    subtopic=subtopic,
                    planets=planets,
                    houses=houses,
                    vedic_planets=vedic_planets_for_llm,
                    vedic_houses=vedic_houses_for_llm,
                    sub_subdomain="",
                    meta=None,
                    timing_windows=None,
                    dob=dob 
                )
                all_points.extend(points)
                
                if additional_data:
                    evaluator_additional_data.update(additional_data)
            
            # Handle two-person compatibility
            two_person_analysis = self._get_default_compatibility_result()
            
            is_two_person = person2 is not None
            person2_output = None
            
            # ✅ Variables for person2 chart data
            planets2 = None
            houses2 = None
            person2_flat_dasha = []
            
            # ✅ NEW: Variables for person2 Vedic data
            vedic_planets2_for_llm = None
            vedic_houses2_for_llm = None
            
            # ✅ NEW: Initialize kundali_milan_data for all cases
            kundali_milan_data = {}
            
            if is_two_person and person2:
                if progress_callback:
                    await progress_callback(50, "Analyzing second person's chart...")
                
                # Fetch person2 data (use person2's own timezone if provided, else fallback to person1's)
                person2_tz = float(person2.get("timezone") or timezone)
                cuspal2 = kp_api.fetch_cuspal(
                    person2["name"], person2["sex"],
                    person2["dob"], person2["tob"],
                    person2["lat"], person2["lon"],
                    tz=person2_tz
                )
                planet2 = kp_api.fetch_planetary_positions(
                    person2["name"], person2["sex"],
                    person2["dob"], person2["tob"],
                    person2["lat"], person2["lon"],
                    tz=person2_tz
                )
                
                cusps2_raw = cuspal2.get("data", {}).get("table_data", {})
                pih2_raw = cuspal2.get("data", {}).get("data", {})
                planets2_raw = planet2.get("data", {}).get("planets", [])
                
                planets2 = self._normalize_planets(planets2_raw)
                houses2 = self._normalize_houses(cusps2_raw, pih2_raw)
                
                for h in houses2:
                    for p_info in h.get("planets", []):
                        p_name = normalize_planet_name(p_info.get("name") if isinstance(p_info, dict) else p_info)
                        if p_name and p_name in planets2:
                            planets2[p_name]["house"] = h["house"]
                
                # ✅ NEW: Fetch Vedic data for Person 2
                if VEDIC_PARSER_AVAILABLE:
                    try:
                        person2_planet_details = vedic_api.fetch_planet_details(
                            person2["dob"], person2["tob"],
                            person2["lat"], person2["lon"],
                            tz=person2_tz
                        )
                        if person2_planet_details:
                            vedic_planets2_for_llm, vedic_metadata2 = parse_vedic_api_response(
                                {"response": person2_planet_details}
                            )
                            ascendant_data2 = vedic_metadata2.get("ascendant") if vedic_metadata2 else None
                            vedic_houses2_for_llm = create_houses_from_planets(
                                vedic_planets2_for_llm, 
                                ascendant_data2
                            )
                            logger.info(f"✅ Parsed Vedic API data for Person 2: {len(vedic_planets2_for_llm)} planets")
                    except Exception as e:
                        logger.warning(f"Failed to fetch Vedic data for Person 2: {e}")
                
                # ✅ Fetch person2's dasha for two-person timing
                try:
                    logger.info("📊 Fetching person2's dasha for timing overlap...")
                    person2_extended_dasha = vedic_api.fetch_extended_dasha_for_timing(
                        person2["dob"], person2["tob"],
                        person2["lat"], person2["lon"],
                        years_ahead=10,
                        tz=person2_tz
                    )
                    person2_flat_dasha = self._parse_dasha_dates(person2_extended_dasha)
                    person2_flat_dasha = self._limit_dasha_to_years(person2_flat_dasha, years=7)
                    logger.info(f"✅ Person2 dasha: {len(person2_flat_dasha)} periods")
                except Exception as e:
                    logger.warning(f"Failed to fetch person2 dasha: {e}")
                    person2_flat_dasha = []
                
                # ✅ MOVED: Fetch Kundali Milan data BEFORE compatibility evaluation
                # This ensures accurate Manglik/dosha data is available for the evaluator
                # Only fetch for Marriage domain since it's specifically for marriage compatibility
                print(f"🔍 [DEBUG] Domain check for Kundali Milan: domain='{domain}', domain.lower()='{domain.lower()}'")
                logger.info(f"🔍 Domain check for Kundali Milan: domain='{domain}', domain.lower()='{domain.lower()}'")
                if domain.lower() == "marriage":
                    print("✅ [DEBUG] Marriage domain detected - fetching Kundali Milan API data")
                    logger.info("✅ Marriage domain detected - fetching Kundali Milan API data")
                    try:
                        from datetime import datetime as dt_parser
                        
                        boy_dob_obj = dt_parser.strptime(dob, "%d/%m/%Y")
                        boy_dob_formatted = boy_dob_obj.strftime("%Y-%m-%d")
                        
                        girl_dob_obj = dt_parser.strptime(person2["dob"], "%d/%m/%Y")
                        girl_dob_formatted = girl_dob_obj.strftime("%Y-%m-%d")
                        
                        print(f"📝 [DEBUG] Calling kundali_milan_api.fetch_kundali_milan()")
                        print(f"   Boy: {name}, DOB: {boy_dob_formatted}, TOB: {tob}")
                        print(f"   Girl: {person2['name']}, DOB: {girl_dob_formatted}, TOB: {person2['tob']}")
                        
                        kundali_milan_data = kundali_milan_api.fetch_kundali_milan(
                            boy_name=name,
                            boy_dob=boy_dob_formatted,
                            boy_tob=tob,
                            boy_lat=lat,
                            boy_lon=lon,
                            boy_pob=name,
                            girl_name=person2["name"],
                            girl_dob=girl_dob_formatted,
                            girl_tob=person2["tob"],
                            girl_lat=person2["lat"],
                            girl_lon=person2["lon"],
                            girl_pob=person2["name"],
                            boy_tz=timezone,
                            girl_tz=float(person2.get("timezone") or timezone)
                        )
                        
                        print(f"📝 [DEBUG] kundali_milan_api returned: {type(kundali_milan_data)}, bool={bool(kundali_milan_data)}")
                        
                        if kundali_milan_data:
                            score = kundali_milan_data.get("match_details", {}).get("ashtakoot", {}).get("response", {}).get("score", "N/A")
                            print(f"✅ [DEBUG] Fetched Kundali Milan data: Score {score}/36")
                            logger.info(f"✅ Fetched Kundali Milan data for {name} & {person2['name']}: Score {score}/36")
                            
                            # Log Manglik status from API for debugging
                            manglik_data = kundali_milan_data.get("match_details", {}).get("manglik", {})
                            boy_manglik = manglik_data.get("boy", {}).get("response", {})
                            girl_manglik = manglik_data.get("girl", {}).get("response", {})
                            print(f"📊 [DEBUG] API Manglik - Boy: {boy_manglik.get('is_manglik', 'N/A')}, Girl: {girl_manglik.get('is_manglik', 'N/A')}")
                            logger.info(f"📊 API Manglik - Boy: {boy_manglik.get('is_manglik', 'N/A')}, Girl: {girl_manglik.get('is_manglik', 'N/A')}")
                        else:
                            print(f"⚠️ [DEBUG] kundali_milan_data is EMPTY or None!")
                            logger.warning(f"⚠️ kundali_milan_data returned empty or None")
                            
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to fetch kundali milan: {e}")
                        logger.warning(f"Failed to fetch kundali milan: {e}")
                        import traceback
                        logger.warning(traceback.format_exc())
                        print(traceback.format_exc())
                else:
                    print(f"⏭️ [DEBUG] Skipping Kundali Milan API - domain is '{domain}', not 'marriage'")
                
                # ✅ FIXED: Use modular compatibility evaluator with ALL parameters including kundali_milan_data
                two_person_analysis = self._run_compatibility_evaluation(
                    domain=domain,
                    planets1=planets,
                    houses1=houses,
                    planets2=planets2,
                    houses2=houses2,
                    sex1=sex,
                    sex2=person2["sex"],
                    vedic_planets1=vedic_planets_for_llm,
                    vedic_houses1=vedic_houses_for_llm,
                    vedic_planets2=vedic_planets2_for_llm,
                    vedic_houses2=vedic_houses2_for_llm,
                    kundali_milan_data=kundali_milan_data  # ✅ NEW: Pass API data for accurate Manglik
                )
                
                # DEBUG: Log what we got back
                logger.info(f"🔍 DEBUG: two_person_analysis overall_score = {two_person_analysis.get('overall_score')}")
                logger.info(f"🔍 DEBUG: two_person_analysis manglik_status = {two_person_analysis.get('manglik_status')}")
                
                person2_output = {
                    "name": person2["name"],
                    "sex": person2["sex"],
                    "dob": person2["dob"],
                    "tob": person2["tob"],
                    "lat": person2["lat"],
                    "lon": person2["lon"],
                    "timezone": f"UTC{'+' if person2.get('timezone', timezone) >= 0 else ''}{person2.get('timezone', timezone)}"
                }
            
            if progress_callback:
                await progress_callback(60, "Extracting questions...")
            
            # Extract questions for subtopics using registry
            all_questions = []
            invalid_subtopics = []
            
            for subtopic in subtopics:
                questions = extract_questions(domain, subtopic)
                if questions:
                    all_questions.extend(questions)
                else:
                    invalid_subtopics.append(subtopic)
            
            if invalid_subtopics:
                logger.warning(f"Invalid subtopics: {invalid_subtopics}")
            
            if not all_questions:
                raise ValueError(f"No valid questions found for subtopics {subtopics}")
            
            if progress_callback:
                await progress_callback(70, "Generating astrological interpretations...")
            
            # Generate LLM interpretations for each question
            rendered_questions = []
            all_astro_remedies = []
            all_general_remedies = []
            
            # ✅ NEW: Fetch Lal Kitab remedies for weak planets relevant to domain
            lalkitab_data = {}
            lalkitab_remedies_context = ""
            try:
                logger.info(f"🔮 Fetching Lal Kitab remedies for domain: {domain}, language: {language}")
                lalkitab_data = get_lalkitab_remedies_for_chart(
                    planets=planets,
                    domain=domain,
                    dob=dob,
                    tob=tob,
                    lat=lat,
                    lon=lon,
                    vedic_planets=vedic_planets_for_llm,
                    max_planets=3,  # Top 3 weak planets
                    language=language,  # ✅ Pass language for consistent output
                    tz=timezone
                )
                
                if lalkitab_data and lalkitab_data.get("weak_planets"):
                    lalkitab_remedies_context = format_remedies_for_llm(lalkitab_data, language=language)
                    logger.info(f"✅ Got Lal Kitab remedies for {len(lalkitab_data['weak_planets'])} weak planets")
                    
                    # Add Lal Kitab remedies to the astrological remedies list
                    for wp in lalkitab_data["weak_planets"]:
                        if wp.get("lal_kitab_remedies"):
                            all_astro_remedies.extend(wp["lal_kitab_remedies"][:2])  # Top 2 from each planet
                else:
                    logger.info("ℹ️ No significantly weak planets found for Lal Kitab remedies")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch Lal Kitab remedies: {e}")
            
            timing_cache = {}

            # ✅ Check if this is a Kundali Matching scenario
            is_kundali_matching = is_two_person and any("Kundali Matching" in st for st in subtopics)

            for q in all_questions:
                meta = q.get("meta", {
                    "type": "NON_TIMING",
                    "polarity": "NEUTRAL",
                    "goal": "STATUS"
                })
                
                q_timing_windows = None

                if _is_timing_query(meta):
                    sub_sub = q.get("sub_subdomain")
                    timing_name = TIMING_BY_SUB_SUBDOMAIN.get(sub_sub)

                    logger.info(f"🚨 TIMING QUERY DETECTED: {sub_sub} → {timing_name}")

                    if not timing_name:
                        logger.error(
                            f"[TIMING CONFIG ERROR] No TIMING_BY_SUB_SUBDOMAIN entry for sub_subdomain='{sub_sub}'"
                        )
                        continue

                    # ✅ Determine cache key based on two-person or single-person
                    cache_key = f"{timing_name}_overlap" if is_kundali_matching else timing_name

                    if cache_key not in timing_cache:
                        logger.info(f"[TIMING] Calculating for: {timing_name} (two_person={is_kundali_matching})")

                        day, month, year = dob.split("/")
                        hour, minute = tob.split(":")
                        dob_dt = datetime(int(year), int(month), int(day), int(hour), int(minute))

                        # ✅ TWO-PERSON TIMING for Kundali Matching
                        if is_kundali_matching and person2_flat_dasha and planets2 and houses2:
                            # Parse person2 DOB
                            p2_day, p2_month, p2_year = person2["dob"].split("/")
                            p2_hour, p2_minute = person2["tob"].split(":")
                            person2_dob_dt = datetime(
                                int(p2_year), int(p2_month), int(p2_day), 
                                int(p2_hour), int(p2_minute)
                            )
                            
                            # Calculate two-person timing with overlap
                            two_person_result = await self._get_two_person_timing_windows(
                                person1_flat_dasha=flat_dasha,
                                person1_dob_dt=dob_dt,
                                person1_planets=planets,
                                person1_houses=houses,
                                person2_flat_dasha=person2_flat_dasha,
                                person2_dob_dt=person2_dob_dt,
                                person2_planets=planets2,
                                person2_houses=houses2,
                                domain=domain,
                                timing_name=timing_name,
                                enable_transit=True,
                                person1_birth_data={
                                    "dob": dob, "tob": tob, "sex": sex,
                                    "lat": lat, "lon": lon, "timezone": timezone
                                },
                                person2_birth_data=person2,
                                min_overlap_days=30
                            )
                            
                            # Cache all results
                            timing_cache[cache_key] = two_person_result["overlapping_windows"]
                            timing_cache[f"{timing_name}_person1"] = two_person_result["person1_windows"]
                            timing_cache[f"{timing_name}_person2"] = two_person_result["person2_windows"]
                            
                            logger.info(f"✅ Two-person timing cached: {len(timing_cache[cache_key])} overlapping windows")
                        
                        else:
                            # SINGLE-PERSON TIMING (original behavior)
                            timing_cache[cache_key] = await self._get_timing_windows(
                                flat_dasha=flat_dasha,
                                dob_dt=dob_dt,
                                planets=planets,
                                houses=houses,
                                domain=domain,
                                timing_name=timing_name,
                                enable_transit=True,
                                dob=dob,
                                tob=tob,
                                sex=sex,
                                lat=lat,
                                lon=lon,
                                tzone=timezone
                            )

                    raw_windows = timing_cache[cache_key]

                    # Normalize windows
                    if raw_windows and isinstance(raw_windows[0], dict):
                        q_timing_windows = self._normalize_timing_windows(raw_windows)
                    else:
                        q_timing_windows = raw_windows

                # Log timing window details for debugging
                if _is_timing_query(meta):
                    logger.info(f"TIMING question detected: {q.get('sub_subdomain')}")
                    logger.info(f"Timing windows count: {len(q_timing_windows) if q_timing_windows else 0}")
                    if q_timing_windows:
                        logger.info(f"First timing window: {q_timing_windows[0]}")
                    else:
                        logger.warning("NO TIMING WINDOWS AVAILABLE for TIMING question!")
                
                # Prepare kwargs for specific prompt builders
                kwargs = {}
                if q.get("sub_subdomain"):
                    kwargs["sub_subdomain"] = q["sub_subdomain"]
                if is_two_person and two_person_analysis:
                    kwargs["compatibility_data"] = two_person_analysis
                if kundali_milan_data:
                    kwargs["kundali_milan_data"] = kundali_milan_data
                
                # For General_Guidance domain, pass additional API data
                if domain == "General_Guidance":
                    kwargs["planet_details"] = planet_details
                    if future_dasha and len(future_dasha) > 0:
                        current_dasha = future_dasha[0]
                        dasha_parts = current_dasha.get("dasha_name", "").split("-") if isinstance(current_dasha, dict) else []
                        kwargs["maha_dasha"] = {"planet": dasha_parts[0] if len(dasha_parts) > 0 else ""}
                        kwargs["antara_dasha"] = {"planet": dasha_parts[1] if len(dasha_parts) > 1 else ""}
                    else:
                        kwargs["maha_dasha"] = {}
                        kwargs["antara_dasha"] = {}
                
                # For Love_Relationship domain, pass love promise data from evaluator
                if domain == "Love_Relationship" and evaluator_additional_data:
                    if "love_promise" in evaluator_additional_data:
                        kwargs["love_promise_data"] = evaluator_additional_data["love_promise"]
                    if "breakup_analysis" in evaluator_additional_data:
                        kwargs["breakup_analysis"] = evaluator_additional_data["breakup_analysis"]
                    if "love_life_analysis" in evaluator_additional_data:
                        kwargs["love_life_analysis"] = evaluator_additional_data["love_life_analysis"]
                
                try:
                    llm_subtopic = subtopics[0] if subtopics else ""

                    logger.info(f"Re-evaluating for question {q.get('id')} with sub_subdomain: {q.get('sub_subdomain')}")

                    timing_windows_for_eval = None
                    if q_timing_windows:
                        sub_sub = q.get("sub_subdomain", "")
                        if sub_sub:
                            timing_windows_for_eval = {sub_sub: q_timing_windows}
                            logger.debug(f"✅ Passing timing windows to evaluator: {sub_sub} → {len(q_timing_windows)} windows")

                    question_points, question_additional_data = self._run_domain_evaluation(
                        domain=domain,
                        subtopic=llm_subtopic,
                        planets=planets,
                        houses=houses,
                        vedic_planets=vedic_planets_for_llm,
                        vedic_houses=vedic_houses_for_llm,
                        sub_subdomain=q.get("sub_subdomain", ""),
                        meta=meta,
                        question=q.get("question", ""),
                        timing_windows=timing_windows_for_eval,
                        current_dasha=current_dasha,
                        dob=dob,
                        planets2=planets2 if is_two_person else None,
                        houses2=houses2 if is_two_person else None,
                        vedic_planets2=vedic_planets2_for_llm if is_two_person else None,
                        vedic_houses2=vedic_houses2_for_llm if is_two_person else None,
                        person1_name=name,
                        person2_name=person2["name"] if is_two_person and person2 else None,
                    )
        
                    question_evaluation_points = question_points if question_points else all_points
                    # Parse DOB once at top of timing loop if not already parsed
                    day, month, year = dob.split("/")
                    dob_dt_for_llm = datetime(int(year), int(month), int(day))

                    age_now = (datetime.now() - dob_dt_for_llm).days / 365.25
                    age_now = round(age_now, 1)

                    llm_kwargs = {
                        **kwargs,
                        "additional_data": question_additional_data,
                        "current_dasha": current_dasha,
                        "dasha_timeline": dasha_timeline,
                        "lalkitab_remedies_context": lalkitab_remedies_context,
                        
                        # ✅ NEW
                        "dob": dob,
                        "age_now": age_now
                    }


                    logger.info(f"Question-specific evaluation returned {len(question_evaluation_points)} points")
        
                    llm_planets = vedic_planets_for_llm if vedic_planets_for_llm else planets
                    llm_houses = vedic_houses_for_llm if vedic_houses_for_llm else houses
                    
                    llm_resp = llm_service.rephrase_with_llm(
                        question=q["question"],
                        points=question_evaluation_points,
                        domain=domain,
                        subtopic=llm_subtopic,
                        meta=meta,
                        planets=llm_planets,
                        houses=llm_houses,
                        timing_windows=q_timing_windows,
                        language=language,
                        **llm_kwargs
                    )
                    
                    all_astro_remedies.extend(llm_resp.get("remedies_astrological", []))
                    all_general_remedies.extend(llm_resp.get("remedies_general", []))
                    
                    rendered_questions.append({
                        "id": q.get("id"),
                        "sub_subdomain": q.get("sub_subdomain"),
                        "question": q["question"],
                        "general_answer": llm_resp.get("general_answer", ""),
                        "astrological_analysis": llm_resp.get("astrological_analysis", ""),
                        "summary": llm_resp.get("summary", "")
                    })
                except Exception as e:
                    logger.error(f"LLM error for question {q.get('id')}: {e}")
                    rendered_questions.append({
                        "id": q.get("id"),
                        "sub_subdomain": q.get("sub_subdomain"),
                        "question": q["question"],
                        "general_answer": "Analysis could not be generated at this time.",
                        "astrological_analysis": "",
                        "summary": ""
                    })
            
            if progress_callback:
                await progress_callback(85, "Generating dasha analysis...")
            
            # Generate dasha events
            dasha_analysis = None
            past_events = []

            # --- Compute age from dob ---
            try:
                dob_parts = dob.split("/")
                dob_date = datetime(int(dob_parts[2]), int(dob_parts[1]), int(dob_parts[0]))
                today = datetime.utcnow()
                age_years = today.year - dob_date.year - (
                    (today.month, today.day) < (dob_date.month, dob_date.day)
                )
            except Exception:
                age_years = None

            # --- Extract Lagna from KP houses data (house 1 sign) ---
            lagna_sign = ""
            try:
                h1 = houses.get("1") or houses.get(1) or {}
                lagna_sign = h1.get("sign") or h1.get("rashi") or h1.get("zodiac_sign") or ""
                if not lagna_sign and planets:
                    # Try ascendant planet entry
                    for p in planets:
                        if str(p.get("name", "")).lower() in ("ascendant", "lagna", "asc"):
                            lagna_sign = p.get("sign") or p.get("rashi") or ""
                            break
            except Exception:
                lagna_sign = ""

            # --- Filter last 1 year of past dasha for past events ---
            try:
                one_year_ago = datetime.utcnow() - timedelta(days=365)
                past_1year_dasha = [
                    d for d in past_dasha
                    if d.get("date_range", {}).get("end", "") >= one_year_ago.strftime("%Y-%m-%d")
                ]
                if not past_1year_dasha:
                    past_1year_dasha = past_dasha[-10:]  # fallback: last 10 entries
            except Exception:
                past_1year_dasha = past_dasha

            try:
                dasha_resp = llm_service.generate_dasha_events(
                    planet_details=planet_details,
                    past_dasha=past_dasha,
                    future_dasha=future_dasha,
                    language=language,
                    lagna=lagna_sign,
                    planets=planets if isinstance(planets, list) else [],
                    houses=houses if isinstance(houses, dict) else {},
                    age=age_years,
                    past_1year_dasha=past_1year_dasha,
                )
                past_events = dasha_resp.get("past_events_raw", [])
                dasha_analysis = {
                    "past_6_months": dasha_resp.get("dasha_past_raw", []),
                    "next_6_months": dasha_resp.get("dasha_future_raw", [])
                }
            except Exception as e:
                logger.error(f"Dasha generation error: {e}")
                dasha_analysis = {
                    "past_6_months": past_dasha[:3],
                    "next_6_months": future_dasha[:3]
                }
            
            if progress_callback:
                await progress_callback(95, "Building final response...")
            
            # Build final output
            unique_ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            input_id = f"{unique_ts}-{uuid4()}"
            
            # Generate overview summary
            overview_summary = None
            if is_two_person and two_person_analysis.get("detailed_analysis"):
                overview_summary = two_person_analysis["detailed_analysis"]
            elif all_points:
                overview_summary = all_points[0] if len(all_points) > 0 else None
            
            # ✅ Combine remedies into astrological and general sections
            # Lal Kitab remedies go into astrological section
            final_astro_remedies = list(all_astro_remedies)  # Already includes Lal Kitab from earlier
            final_general_remedies = list(all_general_remedies)
            
            # Add additional Lal Kitab remedies to astrological section
            if lalkitab_data and lalkitab_data.get("weak_planets"):
                for wp in lalkitab_data["weak_planets"]:
                    if wp.get("lal_kitab_remedies"):
                        final_astro_remedies.extend(wp["lal_kitab_remedies"][:3])
            
            # Remove duplicates while preserving order
            seen_astro = set()
            unique_astro_remedies = []
            for remedy in final_astro_remedies:
                if remedy and remedy not in seen_astro:
                    seen_astro.add(remedy)
                    unique_astro_remedies.append(remedy)
            
            seen_general = set()
            unique_general_remedies = []
            for remedy in final_general_remedies:
                if remedy and remedy not in seen_general:
                    seen_general.add(remedy)
                    unique_general_remedies.append(remedy)
            
            result = {
                "response_id": response_id,
                "input_id": input_id,
                "generated_at": datetime.utcnow().isoformat(),
                "source": "ZODIAQ-RAG-MODULAR-v2",
                "language": language,
                "person": {
                    "name": name,
                    "sex": sex,
                    "dob": dob,
                    "tob": tob,
                    "lat": lat,
                    "lon": lon,
                    "timezone": f"UTC{'+' if timezone >= 0 else ''}{timezone}"
                },
                "person2": person2_output,
                "is_two_person": is_two_person,
                "overview": {
                    "topic": domain,
                    "subtopics": subtopics,
                    "summary": overview_summary
                },
                "timing_windows": timing_cache,
                "past_events": past_events,
                "dasha_analysis": dasha_analysis,
                "questions": rendered_questions,
                "remedies": {
                    "astrological": unique_astro_remedies[:5],
                    "general": unique_general_remedies[:4]
                },
                "two_person_analysis": two_person_analysis,
                "ui_hints": {
                    "sections_order": [
                        "overview",
                        "timing_windows" if timing_cache else None,
                        "two_person_analysis" if is_two_person else None,
                        "past_events",
                        "dasha_analysis",
                        "questions",
                        "remedies"
                    ]
                }
            }
            
            # Clean up ui_hints
            result["ui_hints"]["sections_order"] = [
                s for s in result["ui_hints"]["sections_order"] if s
            ]
            
            if progress_callback:
                await progress_callback(100, "Complete")
            
            # Ensure all datetime objects are converted to strings for JSON serialization
            result = self._ensure_json_serializable(result)
            
            return result
            
        except Exception as e:
            logger.exception(f"Prediction processing error: {e}")
            raise
    
    def _get_timing_name(self, domain: str, subtopics: List[str]) -> Optional[str]:
        """Get the timing rule name based on domain and subtopics"""
        # Normalize domain to lowercase for consistent matching
        domain_lower = domain.lower()
        
        timing_map = {
            "marriage": {
                "marriage_prospects": "Marriage Timing",
                "kundali_matching_timing": "Marriage Timing",
                "marital_stability": "Divorce Timing",
                # Legacy title case support
                "Marriage Prospects": "Marriage Timing",
                "Marriage Timing": "Marriage Timing",
                "Marital Stability": "Divorce Timing",
                "Divorce": "Divorce Timing"
            },
            "career": {
                "career_discovery_and_employment": "Job Start Timing",
                "growth_and_security": "Promotion Timing",
                "career_changes": "Career Shift Timing",
                "international_career": "Foreign Career Potential",
                # Legacy
                "Career Discovery and Employment": "Job Start Timing",
                "Growth and Security": "Promotion Timing",
                "Career Changes": "Career Shift Timing",
                "International Career": "Foreign Career Potential"
            },
            "parenting": {
                "family_planning_and_parenting": "Timing of Childbirth",
                "Family Planning And Parenting": "Timing of Childbirth",
                "Childbirth Timing": "Timing of Childbirth",
                "Best Time to Conceive": "Best Time to Conceive",
            },
            "love_relationship": {
                "attracting_love": "Marriage Timing",
                "breakup": "Reconciliation Timing",
                "strength_and_outcome": "Marriage Timing",
                # Legacy
                "Attracting Love": "Marriage Timing",
                "Finding Love": "Marriage Timing",
                "Breakup": "Reconciliation Timing",
                "Strength And Outcome": "Marriage Timing"
            },
            "finance": {
                "prospects_of_investments": "Prospects of Investment",
                "facing_financial_problems": "Loan Repayment Timing",
                "buying_home_or_land": "Prospects of Property",
                # Legacy
                "Prospects of Investments": "Prospects of Investment",
                "Facing Financial Problems": "Loan Repayment Timing",
                "Buying Home Or Land": "Prospects of Property"
            },
            "health": {
                "physical_and_mental_health": "Health Risk Timing",
                "Physical And Mental Health": "Health Risk Timing",
                "Disease Occurrence": "Health Risk Timing",
                "Cure Timing": "Cure Timing",
                "Recovery Timing": "Cure Timing",
                "Surgery Timing": "Surgery Timing"
            },
            "foreign": {
                "foreign_settlement": "Foreign Timing",
                "Foreign Settlement": "Foreign Timing",
                "Foreign Travel": "Foreign Timing"
            },
            "business": {
                "starting_new_business": "Business Start Timing",
                "growing_existing_business": "Business Growth Timing",
                "facing_challenges_in_business": "Business Recovery Timing",
                # Legacy
                "Starting New Business": "Business Start Timing",
                "Growing Existing Business": "Business Growth Timing",
                "Facing Challenges in Business": "Business Recovery Timing",
                "Loan Taking Decision": "Loan Taking Timing",
                "Loan Repayment Decision": "Loan Repayment Timing"
            },
            "child": {
                "education_guidance": "Education Timing",
                "health_guidance": "Child Health Timing",
                # Legacy
                "Education Guidance": "Education Timing",
                "Health Guidance": "Child Health Timing",
                "Higher Education": "Higher Education Timing",
                "Foreign Education": "Foreign Higher Education Timing"
            }
        }
        
        no_timing_subtopics = {
            "Marriage Compatibility",
            "marriage_compatibility",
            "Compatibility",
            "Career Remedies",
            "Career Risks and Advice",
            "Career Shift Advice"
        }

        if all(s in no_timing_subtopics for s in subtopics):
            return None
        
        domain_map = timing_map.get(domain_lower, {})
        for subtopic in subtopics:
            if subtopic in domain_map:
                return domain_map[subtopic]
        
        # Fallback defaults
        if domain_lower == "marriage":
            return "Marriage Timing"
        elif domain_lower == "career":
            for subtopic in subtopics:
                subtopic_lower = subtopic.lower().replace(" ", "_")
                if subtopic_lower == "career_discovery_and_employment":
                    return "Job Start Timing"
                if subtopic_lower == "growth_and_security":
                    return "Promotion Timing"
                if subtopic_lower == "career_changes":
                    return "Career Shift Timing"
                if subtopic_lower == "international_career":
                    return "Foreign Career Potential"
        
        return None


# Singleton instance
astro_engine = AstroEngine()
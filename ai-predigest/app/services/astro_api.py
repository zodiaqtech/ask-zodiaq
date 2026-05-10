"""
External API clients for Vedic astrology data with async/parallel support
MERGED VERSION: Contains both optimized VedicAstroAPI and original KPAstroAPI
"""
import requests
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from cachetools import TTLCache
from config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Transit cache (TTL: 1 hour)
TRANSIT_CACHE = TTLCache(maxsize=1000, ttl=3600)

from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, _has_evil_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, is_combust, has_dig_bala,
    get_signified_houses, get_signified_score, get_cusp_sub_lord,
    kp_check_promise, get_spouse_direction_from_sign, get_spouse_nature_from_planet,
    detect_aspects, BENEFICS, MALEFICS, FRUITFUL_SIGNS, RASI_LORDS,
    resolve_rahu_ketu_sub_lord, get_detailed_spouse_traits, SPOUSE_AGE_DIFFERENCE_MAP,
    SPOUSE_CHARACTER_BOOK,SIGN_LORD,dms_to_decimal,assign_bhava_house,SIGN_BASE,normalize_deg_360,normalize_planet_in_houses,normalize_cusps_full,normalize_planets_raw
)

class VedicAstroAPI:
    """Client for VedicAstro API with async support"""
    
    BASE_URL = "https://api.vedicastroapi.com/v3-json"
    
    def __init__(self):
        self.api_key = settings.VEDIC_ASTRO_API_KEY
        # Connection pooling for better performance
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with connection pooling"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,  # Max 100 connections
                limit_per_host=30,  # Max 30 connections per host
                ttl_dns_cache=300  # DNS cache for 5 minutes
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self._session
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _make_params(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Create base API parameters"""
        return {
            "api_key": self.api_key,
            "dob": dob,
            "tob": tob,
            "lat": str(lat),
            "lon": str(lon),
            "tz": tz,
            "lang": "en"
        }
    
    def _fetch(self, endpoint: str, params: Dict) -> Dict:
        """Make API request (sync)"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    async def _fetch_async(self, endpoint: str, params: Dict) -> Dict:
        """Make async API request"""
        url = f"{self.BASE_URL}/{endpoint}"
        session = await self.get_session()
        
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    # ========================================
    # SYNC METHODS (Original - keep for backward compatibility)
    # ========================================
    
    def fetch_planet_details(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch detailed planet information (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = self._fetch("horoscope/planet-details", params)
        return result.get("response", {})

    def fetch_maha_dasha(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch Maha Dasha data (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = self._fetch("dashas/maha-dasha", params)
        return result.get("response", {})

    def fetch_antara_dasha(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch Antara Dasha data (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = self._fetch("dashas/antar-dasha", params)
        data = result.get("response", {})
        return {
            "antardashas": data.get("antardashas", []),
            "antardasha_order": data.get("antardasha_order", [])
        }

    def fetch_yoga_list(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch Yoga List data from extended horoscope (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = self._fetch("extended-horoscope/yoga-list", params)
        return result.get("response", {})

    def fetch_paryantar_dasha(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch Paryantar Dasha data (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = self._fetch("dashas/paryantar-dasha", params)
        data = result.get("response", {})
        return {
            "paryantardasha": data.get("paryantardasha", []),
            "paryantardasha_order": data.get("paryantardasha_order", [])
        }

    def fetch_divisional_chart(self, dob: str, tob: str, lat: float, lon: float, div: str = "D9", tz: float = 5.5) -> Dict:
        """Fetch divisional chart (sync)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        params["div"] = div.lower()
        result = self._fetch("horoscope/divisional-charts", params)
        return result.get("response", {})
    
    
    '''def fetch_extended_dasha_for_timing(self, dob: str, tob: str, lat: float, lon: float, years_ahead: int = 10) -> Dict:
        """
        Fetch extended dasha data for timing calculations (sync).
        
        Priority:
        1. Try paryantar dasha first (gives precise 1-3 month windows)
        2. Fall back to antara dasha (gives 1-3 year windows)
        """
        from datetime import datetime, timedelta
        
        logger.info("=" * 60)
        logger.info("fetch_extended_dasha_for_timing CALLED")
        logger.info("=" * 60)
        
        def parse_date(date_str):
            """Parse date string from API"""
            if isinstance(date_str, datetime):
                return date_str
            if not date_str or not isinstance(date_str, str):
                return None
            
            date_str = date_str.strip()
            formats = [
                "%a %b %d %Y",  # "Thu Dec 20 2018"
                "%d/%m/%Y",
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%d %b %Y"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            return None
        
        now = datetime.now()
        max_future = now + timedelta(days=years_ahead * 365)
        
        # Try PARYANTAR first
        logger.info("Attempting PARYANTAR dasha fetch...")
        try:
            paryantar_data = self.fetch_paryantar_dasha(dob, tob, lat, lon, tz=tz)
            logger.info(f"Paryantar API returned: {type(paryantar_data)}")
            
            paryantardasha = paryantar_data.get("paryantardasha", [])
            if paryantardasha and len(paryantardasha) > 0:
                logger.info(f"✅ Using PARYANTAR dasha")
                return {
                    "data": {
                        "paryantar_dasha": self._parse_paryantar_nested(paryantar_data, parse_date, now, max_future)
                    }
                }
        except Exception as e:
            logger.exception(f"❌ PARYANTAR parsing failed: {e}")
        
        # Fall back to ANTARA
        logger.info("⚠️ Falling back to ANTARA dasha")
        try:
            antara_data = self.fetch_antara_dasha(dob, tob, lat, lon, tz=tz)
            logger.info(f"Antara API returned: {type(antara_data)}")
            
            antara_periods = self._parse_antara_flat(antara_data, parse_date, now, max_future)
            if antara_periods:
                logger.info(f"Using ANTARA dasha: {len(antara_periods)} periods")
                return {
                    "data": {
                        "paryantar_dasha": antara_periods
                    }
                }
        except Exception as e:
            logger.exception(f"ANTARA parsing also failed: {e}")
        
        logger.warning("No dasha periods could be parsed from either API")
        return {"data": {"paryantar_dasha": []}}'''
    
    

    def fetch_extended_dasha_for_timing(
    self,
    dob: str,
    tob: str,
    lat: float,
    lon: float,
    years_ahead: int = 10,
    tz: float = 5.5
) -> Dict:
        """
        Fetch extended dasha data for timing calculations.

        Strategy:
        1. Prefer RAW Paryantar dasha (array + boundary semantics)
        2. Fall back to RAW Antara dasha if paryantar unavailable
        3. DO NOT parse, flatten, or filter here
        """

        logger.info("=" * 60)
        logger.info("📊 fetch_extended_dasha_for_timing CALLED")
        logger.info("=" * 60)

        # ------------------------------------------------------------
        # 1️⃣ Try RAW PARYANTAR dasha (preferred)
        # ------------------------------------------------------------
        try:
            logger.info("Attempting RAW PARYANTAR dasha fetch...")
            paryantar_data = self.fetch_paryantar_dasha(dob, tob, lat, lon, tz=tz)

            if (
                isinstance(paryantar_data, dict)
                and "paryantardasha" in paryantar_data
                and "paryantardasha_order" in paryantar_data
            ):
                logger.info("✅ Using RAW PARYANTAR dasha (array format)")
                return {
                    "data": paryantar_data
                }

            logger.warning("Paryantar response missing required keys")

        except Exception as e:
            logger.exception(f"❌ RAW PARYANTAR fetch failed: {e}")

        # ------------------------------------------------------------
        # 2️⃣ Fallback: RAW ANTARA dasha
        # ------------------------------------------------------------
        try:
            logger.info("⚠️ Falling back to RAW ANTARA dasha fetch...")
            antara_data = self.fetch_antara_dasha(dob, tob, lat, lon, tz=tz)

            if isinstance(antara_data, dict) and antara_data:
                logger.info("✅ Using RAW ANTARA dasha")
                return {
                    "data": antara_data
                }

            logger.warning("Antara response invalid or empty")

        except Exception as e:
            logger.exception(f"❌ RAW ANTARA fetch failed: {e}")

        # ------------------------------------------------------------
        # 3️⃣ Final fallback (empty)
        # ------------------------------------------------------------
        logger.error("❌ No valid dasha data available from API")
        return {
            "data": {}
        }

    
    def _parse_paryantar_nested(self, paryantar: Dict, parse_date, now, max_future) -> List[Dict]:
        """Parse nested paryantar dasha structure with correct boundary semantics"""

        ABBREV_MAP = {
            "Ke": "Ketu", "Ve": "Venus", "Su": "Sun", "Mo": "Moon",
            "Ma": "Mars", "Ra": "Rahu", "Ju": "Jupiter", "Sa": "Saturn", "Me": "Mercury",
            "Ketu": "Ketu", "Venus": "Venus", "Sun": "Sun", "Moon": "Moon",
            "Mars": "Mars", "Rahu": "Rahu", "Jupiter": "Jupiter", "Saturn": "Saturn", "Mercury": "Mercury"
        }

        def expand_planet(abbrev: str) -> str:
            return ABBREV_MAP.get(abbrev.strip(), abbrev)

        parsed = []

        names_root = paryantar.get("paryantardasha", [])
        dates_root = paryantar.get("paryantardasha_order", [])

        if not names_root or not dates_root:
            return []

        for maha_names, maha_dates in zip(names_root, dates_root):
            for antara_names, antara_dates in zip(maha_names, maha_dates):

                # We need at least two boundaries to form one period
                if len(antara_dates) < 2:
                    continue

                for i in range(1, len(antara_dates)):
                    pd_name = antara_names[i - 1]

                    start_dt = parse_date(antara_dates[i - 1])
                    end_dt   = parse_date(antara_dates[i])

                    if not start_dt or not end_dt:
                        continue

                    # Filter window AFTER correct chaining
                    if end_dt < now or start_dt > max_future:
                        continue

                    parts = pd_name.split("/")
                    if len(parts) < 3:
                        continue

                    parsed.append({
                        "md_name": expand_planet(parts[0]),
                        "ad_name": expand_planet(parts[1]),
                        "pd_name": expand_planet(parts[2]),
                        "prd_start": start_dt.strftime("%Y-%m-%d"),
                        "prd_end": end_dt.strftime("%Y-%m-%d")
                    })

        return parsed

    
    def _parse_antara_flat(self, antara: Dict, parse_date, now, max_future) -> List[Dict]:
        """Parse flat antara dasha structure"""
        from datetime import timedelta
        
        parsed = []
        antardashas = antara.get("antardashas", [])
        antardasha_order = antara.get("antardasha_order", [])
        
        if not antardashas or not antardasha_order:
            return []
        
        for maha_list, maha_dates in zip(antardashas, antardasha_order):
            if not maha_list or not maha_dates:
                continue
            
            for ad_idx, (ad_name, ad_date_str) in enumerate(zip(maha_list, maha_dates)):
                try:
                    # Parse name (format: "Venus/Venus")
                    parts = ad_name.split("/")
                    if len(parts) < 2:
                        continue
                    
                    md_name = parts[0].strip()
                    ad_name_clean = parts[1].strip()
                    
                    # Parse start date
                    prd_start = parse_date(ad_date_str)
                    if not prd_start:
                        continue
                    
                    # Estimate end date
                    if ad_idx + 1 < len(maha_dates):
                        prd_end = parse_date(maha_dates[ad_idx + 1])
                    else:
                        prd_end = prd_start + timedelta(days=365)
                    
                    if not prd_end:
                        prd_end = prd_start + timedelta(days=365)
                    
                    # Filter by date range
                    if prd_end < now or prd_start > max_future:
                        continue
                    
                    # Use antara as paryantar format (no PD level)
                    parsed.append({
                        "md_name": md_name,
                        "ad_name": ad_name_clean,
                        "pd_name": ad_name_clean,  # Use AD as PD
                        "prd_start": prd_start.strftime("%Y-%m-%d"),
                        "prd_end": prd_end.strftime("%Y-%m-%d")
                    })
                except Exception as e:
                    logger.debug(f"Error parsing antara entry: {e}")
                    continue
        
        return parsed
    
    def fetch_transit_chart(self, dob: str, tob: str, lat: float, lon: float, transit_date: str, tz: float = 5.5) -> Dict:
        """Fetch transit chart for a specific date (sync)"""
        cache_key = f"{dob}_{tob}_{lat}_{lon}_{transit_date}"
        if cache_key in TRANSIT_CACHE:
            logger.debug(f"Transit cache hit for {transit_date}")
            return TRANSIT_CACHE[cache_key]

        params = self._make_params(dob, tob, lat, lon, tz=tz)
        params["div"] = "transit"
        params["transit_date"] = transit_date
        params["response_type"] = "planet_object"

        result = self._fetch("horoscope/divisional-charts", params)
        data = result.get("response", {})

        TRANSIT_CACHE[cache_key] = data
        return data

    def fetch_transit_for_date(self, target_date: datetime, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch transit data for a specific datetime (sync)"""
        transit_date_str = target_date.strftime("%d/%m/%Y")
        return self.fetch_transit_chart(dob, tob, lat, lon, transit_date_str, tz=tz)
    
    def fetch_kp_snapshot(self, target_date: datetime, sex: str, lat: float, lon: float, tzone: str = "5.5") -> Dict:
        """Fetch KP planets for a specific date/time (sync)"""
        dob_str = target_date.strftime("%d/%m/%Y")
        tob_str = "12:00"  # Noon for snapshot
        
        cache_key = f"kp_snapshot_{dob_str}_{lat}_{lon}"
        if cache_key in TRANSIT_CACHE:
            return TRANSIT_CACHE[cache_key]
        
        try:
            params = {
                "api_key": self.api_key,
                "dob": dob_str,
                "tob": tob_str,
                "lat": str(lat),
                "lon": str(lon),
                "tz": tzone,
                "lang": "en"
            }
            
            result = self._fetch("horoscope/planet-details", params)
            response = result.get("response", {})
            
            TRANSIT_CACHE[cache_key] = response
            return response
        except Exception as e:
            return {}
    
    # ========================================
    # ASYNC METHODS (NEW - OPTIMIZED!)
    # ========================================
    
    async def fetch_planet_details_async(self, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch detailed planet information (async)"""
        params = self._make_params(dob, tob, lat, lon, tz=tz)
        result = await self._fetch_async("horoscope/planet-details", params)
        return result.get("response", {})

    async def fetch_transit_chart_async(self, dob: str, tob: str, lat: float, lon: float, transit_date: str, tz: float = 5.5) -> Dict:
        """Fetch transit chart for a specific date (async)"""
        cache_key = f"{dob}_{tob}_{lat}_{lon}_{transit_date}"
        if cache_key in TRANSIT_CACHE:
            logger.debug(f"Transit cache hit for {transit_date}")
            return TRANSIT_CACHE[cache_key]

        params = self._make_params(dob, tob, lat, lon, tz=tz)
        params["div"] = "transit"
        params["transit_date"] = transit_date
        params["response_type"] = "planet_object"

        result = await self._fetch_async("horoscope/divisional-charts", params)
        data = result.get("response", {})

        TRANSIT_CACHE[cache_key] = data
        return data

    async def fetch_transit_for_date_async(self, target_date: datetime, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch transit data for a specific datetime (async)"""
        transit_date_str = target_date.strftime("%d/%m/%Y")
        return await self.fetch_transit_chart_async(dob, tob, lat, lon, transit_date_str, tz=tz)
    
    async def fetch_kp_snapshot_async(self, target_date: datetime, sex: str, lat: float, lon: float, tzone: str = "5.5") -> Dict:
        """Fetch KP planets for a specific date/time (async)"""
        dob_str = target_date.strftime("%d/%m/%Y")
        tob_str = "12:00"
        
        params = {
            "api_key": self.api_key,
            "dob": dob_str,
            "tob": tob_str,
            "lat": str(lat),
            "lon": str(lon),
            "tz": tzone,
            "lang": "en"
        }
        
        result = await self._fetch_async("horoscope/planet-details", params)
        return result.get("response", {})
    
    # ========================================
    # PARALLEL BATCH METHODS (KEY OPTIMIZATION!)
    # ========================================
    
    async def fetch_all_timing_data_async(
        self,
        dates: List[datetime],
        dob: str,
        tob: str,
        sex: str,
        lat: float,
        lon: float,
        tzone: str = "5.5"
    ) -> tuple:
        """
        Fetch both transit and KP data for multiple dates in parallel.
        
        THIS IS THE KEY OPTIMIZATION that fixes the timeout!
        
        Returns:
            Tuple of (transit_list, kp_list)
        """
        logger.info(f"⚡ Fetching timing data for {len(dates)} dates in parallel...")
        
        # Create all transit tasks
        transit_tasks = [
            self.fetch_transit_for_date_async(date, dob, tob, lat, lon, tz=float(tzone))
            for date in dates
        ]
        
        # Create all KP tasks
        kp_tasks = [
            self.fetch_kp_snapshot_async(date, sex, lat, lon, tzone)
            for date in dates
        ]
        
        # Execute ALL tasks in parallel
        all_tasks = transit_tasks + kp_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Split results
        n = len(dates)
        transit_results = results[:n]
        kp_results = results[n:]
        
        # Handle errors
        transit_results = [r if not isinstance(r, Exception) else {} for r in transit_results]
        kp_results = [r if not isinstance(r, Exception) else {} for r in kp_results]
        
        logger.info(f"✅ Fetched all timing data successfully")
        return transit_results, kp_results


class KPAstroAPI:
    """Client for KP Astrology API (Original - unchanged)"""
    
    BASE_URL = "https://astroapi-3.divineapi.com/indian-api/v2/kp"
    
    def __init__(self):
        self.api_key = settings.KP_API_KEY
        self.auth_token = settings.KP_AUTH_TOKEN
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
    
    @staticmethod
    def normalize_api_data(
        planets, houses, dashas=None, antara=None, paryantar=None,
        d9=None, pdata=None
    ):
    
        # -------------------------------
        # Normalize Planets
        # -------------------------------
        if isinstance(planets, dict):
            for key, p in planets.items():
    
                if not isinstance(p, dict):
                    continue
    
                # Planet name
                pname = normalize_planet(p.get("name"))
                p["name"] = pname
    
                # Fix sign formatting FIRST
                if "sign" in p and p["sign"]:
                    p["sign"] = str(p["sign"]).title()
    
                # Normalize star/sub lords
                if "sub_lord" in p:
                    p["sub_lord"] = normalize_planet(p["sub_lord"])
                if "sub_sub_lord" in p:
                    p["sub_sub_lord"] = normalize_planet(p["sub_sub_lord"])
                if "nakshatra_lord" in p:
                    p["nakshatra_lord"] = normalize_planet(p["nakshatra_lord"])
    
                # Derive rashi lord
                if p.get("sign"):
                    p["rashi_lord"] = SIGN_LORD.get(p["sign"])
    
                # Derive rasi_no if missing
                if not p.get("rasi_no") and p.get("sign"):
                    try:
                        p["rasi_no"] = list(SIGN_LORD.keys()).index(p["sign"]) + 1
                    except:
                        pass
    
                # Fill pseudo fields
                if "rasi" not in p:
                    p["rasi"] = p.get("pseudo_rasi") or p.get("zodiac")
    
                if "rasi_no" not in p:
                    p["rasi_no"] = p.get("pseudo_rasi_no")
    
                if "nakshatra" not in p:
                    p["nakshatra"] = p.get("pseudo_nakshatra")
    
                if "nakshatra_lord" not in p:
                    p["nakshatra_lord"] = normalize_planet(
                        p.get("pseudo_nakshatra_lord")
                    )
    
                if "nakshatra_pada" not in p:
                    p["nakshatra_pada"] = p.get("pseudo_nakshatra_pada")
    
        # -------------------------------
        # Normalize Houses
        # -------------------------------
        for h in houses or []:
    
            if "cusp_sub_lord" in h:
                h["cusp_sub_lord"] = normalize_planet(h["cusp_sub_lord"])
    
            if "start_nakshatra_lord" in h:
                h["start_nakshatra_lord"] = normalize_planet(h["start_nakshatra_lord"])
    
            if "end_nakshatra_lord" in h:
                h["end_nakshatra_lord"] = normalize_planet(h["end_nakshatra_lord"])
    
            if "end_rasi_lord" in h:
                h["end_rasi_lord"] = normalize_planet(h["end_rasi_lord"])
    
            # Normalize nested planets inside houses
            if isinstance(h.get("planets"), list):
                for p in h["planets"]:
                    if not isinstance(p, dict):
                        continue
    
                    if "name" in p:
                        p["name"] = normalize_planet(p["name"])
    
                    if "sign" in p and p["sign"]:
                        p["sign"] = str(p["sign"]).title()
                        p["rashi_lord"] = SIGN_LORD.get(p["sign"])
    
                    if "nakshatra_lord" in p:
                        p["nakshatra_lord"] = normalize_planet(p["nakshatra_lord"])
    
                    if "sub_lord" in p:
                        p["sub_lord"] = normalize_planet(p["sub_lord"])
    
                    if "sub_sub_lord" in p:
                        p["sub_sub_lord"] = normalize_planet(p["sub_sub_lord"])
    
        # -------------------------------
        # Normalize Maha Dasha
        # -------------------------------
        if dashas and isinstance(dashas.get("mahadasha"), list):
            dashas["mahadasha"] = [normalize_planet(x) for x in dashas["mahadasha"]]
    
        # -------------------------------
        # Normalize Antardasha
        # -------------------------------
        if antara and "antardashas" in antara:
            for md_idx, ad_list in enumerate(antara["antardashas"]):
                for i in range(len(ad_list)):
                    parts = ad_list[i].split("/")
                    antara["antardashas"][md_idx][i] = "/".join(
                        normalize_planet(p) for p in parts
                    )
    
        # -------------------------------
        # Normalize Paryantar Dasha
        # -------------------------------
        if paryantar and "paryantardasha" in paryantar:
            for md_idx, ad_groups in enumerate(paryantar["paryantardasha"]):
                for ad_idx, pd_list in enumerate(ad_groups):
                    for i in range(len(pd_list)):
                        parts = pd_list[i].split("/")
                        paryantar["paryantardasha"][md_idx][ad_idx][i] = "/".join(
                            normalize_planet(p) for p in parts
                        )
    
        # -------------------------------
        # Normalize D9 Chart
        # -------------------------------
        if isinstance(d9, dict):
            for obj in d9.values():
                if not isinstance(obj, dict):
                    continue
                if "name" in obj:
                    obj["name"] = normalize_planet(obj["name"])
                if "nakshatra_lord" in obj:
                    obj["nakshatra_lord"] = normalize_planet(obj["nakshatra_lord"])
    
        return planets, houses, dashas, antara, paryantar, d9
    
    @staticmethod
    def normalize_cusps_full(cusps_raw, planet_in_houses_norm=None):
        """
        Build KP bhava houses using cusp geometry.
        """
        cusp_meta = {}

        for k, c in cusps_raw.items():
            hn = int(k)
            sign = (c.get("house_cusp") or {}).get("sign")
            deg_dms = (c.get("house_cusp") or {}).get("degree")
            local = dms_to_decimal(deg_dms)
            base = SIGN_BASE[sign]
            global_start = normalize_deg_360(base + local)

            cusp_meta[hn] = {
                "house": hn,
                "start_rasi": sign,
                "local_start_degree": local,
                "global_start_degree": global_start,
                "rashi_lord": normalize_planet_name(c.get("rashi_lord")),
                "start_nakshatra": c.get("nakshatra"),
                "start_nakshatra_lord": normalize_planet_name(c.get("nakshatra_lord")),
                "cusp_sub_lord": normalize_planet_name(c.get("sub_lord")),
                "cusp_sub_sub_lord": normalize_planet_name(c.get("sub_sub_lord")),
            }

        houses = []

        for i in range(1, 13):
            s = cusp_meta[i]
            n = cusp_meta[1 if i == 12 else i + 1]

            g_start = s["global_start_degree"]
            g_end = n["global_start_degree"]
            g_end_lin = g_end + 360 if g_end <= g_start else g_end

            length = g_end_lin - g_start
            bhavmadhya = normalize_deg_360(g_start + length / 2)

            planets = []
            if planet_in_houses_norm and str(i) in planet_in_houses_norm:
                for rp in planet_in_houses_norm[str(i)]["planet"]:
                    nm = rp.get("name") or rp.get("symbol")
                    planets.append({"name": normalize_planet_name(nm)})

            houses.append({
                "house": i,
                "start_rasi": s["start_rasi"],
                "end_rasi": n["start_rasi"],
                "local_start_degree": s["local_start_degree"],
                "local_end_degree": n["local_start_degree"],
                "global_start_degree": normalize_deg_360(g_start),
                "global_end_degree": normalize_deg_360(g_end),
                "length": round(length, 6),
                "bhavmadhya": round(bhavmadhya, 6),
                "rashi_lord": s["rashi_lord"],
                "cusp_sub_lord": s["cusp_sub_lord"],
                "cusp_sub_sub_lord": s["cusp_sub_sub_lord"],
                "planets": planets,  # display only
            })

        return houses

    @staticmethod
    def unify_new_api_to_old_format(cusps_raw, planet_in_houses_raw, planets_raw):
        # display-only snapshot
        planet_in_houses_norm = normalize_planet_in_houses(planet_in_houses_raw)

        # KP cuspal houses
        houses = normalize_cusps_full(cusps_raw, planet_in_houses_norm)

        # planets (NO house yet)
        planets = normalize_planets_raw(planets_raw)

        # 🔒 KP HOUSE ASSIGNMENT (ONLY SOURCE OF TRUTH)
        for p in planets.values():
            deg = p.get("global_degree")
            if deg is not None:
                p["house"] = assign_bhava_house(float(deg), houses)

        # enrich house planet lists
        for h in houses:
            enriched = []
            for p in h["planets"]:
                nm = normalize_planet_name(p["name"])
                if nm in planets:
                    enriched.append(planets[nm])
            h["planets"] = enriched

        # safety
        for p in planets.values():
            assert p["house"] is not None, f"KP house missing for {p['name']}"

        return planets, houses, planet_in_houses_norm

    @staticmethod
    def rebuild_house_planets(houses: list, planets: dict):
        # clear
        for h in houses:
            h["planets"] = []

        # reattach
        for p in planets.values():
            hno = p.get("house")
            if hno:
                houses[hno - 1]["planets"].append(p)
   
    def _make_payload(self, name: str, sex: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Create base API payload"""
        day, month, year = dob.split("/")
        hour, minute = tob.split(":")
        return {
            "full_name": name,
            "day": day,
            "month": month,
            "year": year,
            "hour": hour,
            "min": minute,
            "sec": "00",
            "gender": sex,
            "place": "Unknown",
            "lat": str(lat),
            "lon": str(lon),
            "tzone": str(tz),
            "lan": "en",
            "api_key": self.api_key
        }
    
    def _call(self, endpoint: str, payload: Dict) -> Dict:
        """Make API request"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.post(url, headers=self.headers, data=payload, timeout=30)
        try:
            return response.json()
        except:
            return {"error": "Invalid JSON", "raw": response.text}
    
    def fetch_cuspal(self, name: str, sex: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch cuspal data"""
        payload = self._make_payload(name, sex, dob, tob, lat, lon, tz=tz)
        return self._call("cuspal", payload)

    def fetch_planetary_positions(self, name: str, sex: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """Fetch planetary positions"""
        payload = self._make_payload(name, sex, dob, tob, lat, lon, tz=tz)
        return self._call("planetary-positions", payload)

    def fetch_planetary_cuspal_significator_table(self, name: str, sex: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> Dict:
        """
        Fetch planetary cuspal significator table from Divine API v1.
        This provides KP significations for each planet.

        Returns:
            Dict containing planet significations data
        """
        payload = self._make_payload(name, sex, dob, tob, lat, lon, tz=tz)
        # Note: This endpoint is on v1 API, not v2
        url = "https://astroapi-3.divineapi.com/indian-api/v1/kp/planetary-cuspal-significator-table"
        response = requests.post(url, headers=self.headers, data=payload, timeout=30)
        try:
            return response.json()
        except:
            return {"error": "Invalid JSON", "raw": response.text}


# Singleton instances
vedic_api = VedicAstroAPI()
kp_api = KPAstroAPI()

"""
Local ephemeris for transit scoring via pyswisseph.

Replaces DivineAPI + VedicAstroAPI calls when scoring timing windows against
transits, making transit computation completely free (no external API needed).

The two public functions produce the exact format that timing_engine's
merge_transit_data() and kp_transit_score() expect:

  get_transit_planets(dt, natal_houses)
      → list of {"name": "Sun", "house": 7, "sign": "Aries"}

  get_kp_lords_for_date(dt)
      → {"Sun": {"nakshatra_lord": "Mars", "sub_lord": "Jupiter", "rasi_lord": "Sun"}, ...}

KP ayanamsa (SIDM_KRISHNAMURTI = 5) is used throughout.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
except ImportError:
    _SWE_AVAILABLE = False
    logger.warning("[local_ephemeris] pyswisseph not installed — transit scoring disabled")


# ── Signs ─────────────────────────────────────────────────────────────────────

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

RASI_LORDS: Dict[str, str] = {
    "Aries": "Mars",    "Taurus": "Venus",   "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun",       "Virgo": "Mercury",  "Libra": "Venus",    "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ── Vimsottari KP sub-lord table ──────────────────────────────────────────────

_NAK_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
] * 3   # 27 nakshatras in order (Ashwini = Ketu, Bharani = Venus, …)

_DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
_DASHA_YRS   = [7, 20, 6, 10, 7, 18, 16, 19, 17]
_TOTAL_YRS   = 120
_NAK_SPAN    = 360 / 27   # 13.3333…°

# ── pyswisseph planet IDs ─────────────────────────────────────────────────────

_SWE_IDS: Dict[str, int] = {
    "Sun":     swe.SUN     if _SWE_AVAILABLE else 0,
    "Moon":    swe.MOON    if _SWE_AVAILABLE else 1,
    "Mercury": swe.MERCURY if _SWE_AVAILABLE else 2,
    "Venus":   swe.VENUS   if _SWE_AVAILABLE else 3,
    "Mars":    swe.MARS    if _SWE_AVAILABLE else 4,
    "Jupiter": swe.JUPITER if _SWE_AVAILABLE else 5,
    "Saturn":  swe.SATURN  if _SWE_AVAILABLE else 6,
    "Rahu":    swe.MEAN_NODE if _SWE_AVAILABLE else 10,
    # Ketu derived as Rahu + 180°
}


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _jd(dt: datetime) -> float:
    """Naive datetime → Julian Day (UTC assumed)."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def _lon(jd: float, sw_id: int) -> float:
    """Sidereal longitude [0, 360) for a planet at Julian Day jd."""
    pos, _ = swe.calc_ut(jd, sw_id, swe.FLG_SIDEREAL)
    return pos[0] % 360


def _rasi(lon: float) -> str:
    return RASIS[int(lon / 30) % 12]


def _nak_lord(lon: float) -> str:
    return _NAK_LORDS[int(lon / _NAK_SPAN) % 27]


def _sub_lord(lon: float) -> str:
    """KP sub lord: divide nakshatra by Vimsottari proportions."""
    nak_idx      = int(lon / _NAK_SPAN) % 27
    pos_in_nak   = lon % _NAK_SPAN
    start_lord   = _NAK_LORDS[nak_idx]
    start_idx    = _DASHA_LORDS.index(start_lord)
    cumulative   = 0.0
    for i in range(9):
        idx  = (start_idx + i) % 9
        size = _NAK_SPAN * _DASHA_YRS[idx] / _TOTAL_YRS
        cumulative += size
        if pos_in_nak <= cumulative:
            return _DASHA_LORDS[idx]
    return start_lord   # fallback


def _natal_house(lon: float, natal_houses: List[Dict]) -> int:
    """
    Return the KP natal house (1-12) that ecliptic longitude `lon` falls in,
    using the global_start_degree of each house cusp.
    """
    cusps = sorted(natal_houses, key=lambda h: h["house"])
    starts = [h.get("global_start_degree", 0.0) for h in cusps]
    for i in range(12):
        this_start = starts[i]
        next_start = starts[(i + 1) % 12]
        if next_start > this_start:
            if this_start <= lon < next_start:
                return i + 1
        else:
            # Wraps around 0°
            if lon >= this_start or lon < next_start:
                return i + 1
    return 1


def _noon_jd(dt: datetime) -> float:
    """Julian Day for 06:30 UTC ≈ noon IST on the given date."""
    return swe.julday(dt.year, dt.month, dt.day, 6.5)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_transit_planets(transit_dt: datetime, natal_houses: List[Dict]) -> List[Dict]:
    """
    Compute transiting planet positions at `transit_dt`, mapped to natal houses.

    Returns a list in DivineAPI kundli-transit/ascendant format so it can be
    passed directly to timing_engine.merge_transit_data() as transit_chart:
        [{"name": "Sun", "house": 7, "sign": "Aries"}, ...]

    Args:
        transit_dt: Midpoint date of a timing window (naive, treated as local date).
        natal_houses: chart.houses list from ChartData (must have global_start_degree).

    Returns:
        [] if pyswisseph is unavailable.
    """
    if not _SWE_AVAILABLE:
        return []

    jd = _noon_jd(transit_dt)
    result: List[Dict] = []

    rahu_lon: float | None = None

    for name, sw_id in _SWE_IDS.items():
        try:
            planet_lon = _lon(jd, sw_id)
            if name == "Rahu":
                rahu_lon = planet_lon
            house = _natal_house(planet_lon, natal_houses)
            rasi  = _rasi(planet_lon)
            result.append({"name": name, "house": house, "sign": rasi})
        except Exception as exc:
            logger.debug(f"[local_ephemeris] {name}: {exc}")

    # Ketu = Rahu + 180°
    if rahu_lon is not None:
        ketu_lon   = (rahu_lon + 180) % 360
        ketu_house = _natal_house(ketu_lon, natal_houses)
        ketu_rasi  = _rasi(ketu_lon)
        result.append({"name": "Ketu", "house": ketu_house, "sign": ketu_rasi})

    return result


def get_kp_lords_for_date(transit_dt: datetime) -> Dict[str, Dict]:
    """
    Compute KP nakshatra_lord, sub_lord, rasi_lord for all planets at `transit_dt`.

    Returns a dict keyed by planet name, matching the kp_planets format expected
    by timing_engine.merge_transit_data():
        {"Sun": {"nakshatra_lord": "Mars", "sub_lord": "Jupiter", "rasi_lord": "Sun"}, ...}

    Args:
        transit_dt: Date for which lords are computed.

    Returns:
        {} if pyswisseph is unavailable.
    """
    if not _SWE_AVAILABLE:
        return {}

    jd = _noon_jd(transit_dt)
    result: Dict[str, Dict] = {}

    rahu_lon: float | None = None

    for name, sw_id in _SWE_IDS.items():
        try:
            planet_lon = _lon(jd, sw_id)
            if name == "Rahu":
                rahu_lon = planet_lon
            rasi = _rasi(planet_lon)
            result[name] = {
                "nakshatra_lord": _nak_lord(planet_lon),
                "sub_lord":       _sub_lord(planet_lon),
                "rasi_lord":      RASI_LORDS[rasi],
            }
        except Exception as exc:
            logger.debug(f"[local_ephemeris] {name} lords: {exc}")

    # Ketu
    if rahu_lon is not None:
        ketu_lon = (rahu_lon + 180) % 360
        ketu_rasi = _rasi(ketu_lon)
        result["Ketu"] = {
            "nakshatra_lord": _nak_lord(ketu_lon),
            "sub_lord":       _sub_lord(ketu_lon),
            "rasi_lord":      RASI_LORDS[ketu_rasi],
        }

    return result

"""
ZodiaQ Engine — LLM-free astrological computation.

Imports evaluators and API clients from the AI-predigest codebase
(path configured via AI_PREDIGEST_PATH env variable) and returns
structured data for every Ask ZodiaQ topic without any LLM call.
"""
from __future__ import annotations

import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Bootstrap: add AI-predigest to the import path ────────────────────────
def _bootstrap_predigest_path() -> None:
    """
    Insert the AI-predigest project root into sys.path so we can import
    its evaluators, API clients, and timing engine directly.
    Call this ONCE before any predigest import.
    """
    path = os.environ.get("AI_PREDIGEST_PATH", "/Users/sankit/Downloads/AI-predigest")
    if path not in sys.path:
        sys.path.insert(0, path)
        logger.info(f"[ZodiaQEngine] Added AI-predigest to sys.path: {path}")

_bootstrap_predigest_path()

# ── Predigest imports — these use "app.*" because they come from AI-predigest
# (the bootstrap above added AI-predigest to sys.path first so "app" resolves there)
from app.services.astro_api import kp_api, vedic_api          # singletons
from app.services.astro_engine import AstroEngine
from app.services.timing_engine import kp_timing_engine       # KPTimingEngine singleton

# Domain evaluators (also from AI-predigest)
from app.domains.marriage.marriage_prospects.evaluator import (
    MarriageProspectsEvaluator,
)
from app.domains.career.career_discovery_and_employment.evaluator import (
    CareerDiscoveryAndEmploymentEvaluator,
)
from app.domains.business.starting_new_business.evaluator import (
    StartingNewBusinessEvaluator,
)
from app.domains.finance.buying_home_or_land.evaluator import (
    BuyingHomeOrLandEvaluator,
)

# ── Module-level singletons ───────────────────────────────────────────────
_astro_engine = AstroEngine()

_marriage_eval  = MarriageProspectsEvaluator()
_career_eval    = CareerDiscoveryAndEmploymentEvaluator()
_business_eval  = StartingNewBusinessEvaluator()
_property_eval  = BuyingHomeOrLandEvaluator()


# ─────────────────────────────────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────────────────────────────────

class ChartData:
    """Holds the fully-normalised chart for one person."""

    def __init__(
        self,
        planets: Dict[str, Any],
        houses: List[Dict],
        flat_dasha: List[Dict],
        dob_dt: datetime,
        dob: str,
        tob: str,
        sex: str,
        lat: float,
        lon: float,
        timezone: float,
    ) -> None:
        self.planets   = planets
        self.houses    = houses
        self.flat_dasha = flat_dasha
        self.dob_dt    = dob_dt
        self.dob       = dob
        self.tob       = tob
        self.sex       = sex
        self.lat       = lat
        self.lon       = lon
        self.timezone  = timezone


async def fetch_chart(
    name: str,
    sex: str,
    dob: str,   # DD/MM/YYYY
    tob: str,   # HH:MM
    lat: float,
    lon: float,
    timezone: float = 5.5,
) -> ChartData:
    """
    Fetch chart data from KP + Vedic APIs and normalise it.
    No LLM involved — pure astrological data only.
    """
    # ── 1. KP API: cuspal (house cusps) + planetary positions ─────────────
    # kp_api._make_payload expects "HH:MM" — pass tob as-is (user provides HH:MM)
    cuspal_resp = kp_api.fetch_cuspal(name, sex, dob, tob, lat, lon, tz=timezone)
    planet_resp = kp_api.fetch_planetary_positions(name, sex, dob, tob, lat, lon, tz=timezone)

    cusps_raw         = cuspal_resp.get("data", {}).get("table_data", {})
    planet_in_houses_raw = cuspal_resp.get("data", {}).get("data", {})
    planets_raw       = planet_resp.get("data", {}).get("planets", [])

    # ── 2. Normalise via the same helper used by the main engine ──────────
    planets, houses, _ = kp_api.unify_new_api_to_old_format(
        cusps_raw, planet_in_houses_raw, planets_raw
    )

    # ── 3. Extended dasha (10 years) from Vedic API ───────────────────────
    flat_dasha: List[Dict] = []
    try:
        extended_dasha = vedic_api.fetch_extended_dasha_for_timing(
            dob, tob, lat, lon, years_ahead=10, tz=timezone
        )
        flat_dasha = _astro_engine._parse_dasha_dates(extended_dasha)
        flat_dasha = _astro_engine._limit_dasha_to_years(flat_dasha, years=7)
    except Exception as exc:
        logger.warning(f"fetch_chart: dasha fetch failed — {exc}")

    # Parse DOB for age-based filtering inside the timing engine
    try:
        dob_dt = datetime.strptime(dob, "%d/%m/%Y")
    except Exception:
        dob_dt = datetime.now()

    return ChartData(
        planets=planets,
        houses=houses,
        flat_dasha=flat_dasha,
        dob_dt=dob_dt,
        dob=dob,
        tob=tob,
        sex=sex,
        lat=lat,
        lon=lon,
        timezone=timezone,
    )


def get_timing_windows(
    chart: ChartData,
    timing_name: str,
    domain: str = "Marriage",
    max_windows: int = 5,
) -> List[Dict]:
    """
    Run the KP timing engine synchronously and return raw timing-window dicts.
    Returns [] if no favourable windows found.
    """
    try:
        windows = kp_timing_engine.calculate_timing_windows(
            dba_list=chart.flat_dasha,
            dob=chart.dob_dt,
            planets=chart.planets,
            houses=chart.houses,
            domain=domain,
            timing_name=timing_name,
            max_windows=max_windows,
        )
        return windows or []
    except Exception as exc:
        logger.error(f"get_timing_windows({timing_name}): {exc}")
        return []


def _fmt_date_range(window: Optional[Dict]) -> Optional[str]:
    """Convert a timing window to a human-readable date range string."""
    if not window:
        return None
    start = window.get("start") or ""
    end   = window.get("end")   or ""
    if not start:
        return None
    # Convert YYYY-MM-DD → "Mon YYYY"
    def _fmt(d: str) -> str:
        try:
            return datetime.strptime(d, "%Y-%m-%d").strftime("%b %Y")
        except Exception:
            return d
    return f"{_fmt(start)} – {_fmt(end)}" if end else _fmt(start)


def _best_and_nearest(windows: List[Dict]) -> Tuple[Optional[Dict], Optional[Dict]]:
    """Return (best_score, nearest_start) from a list of timing windows."""
    if not windows:
        return None, None

    now = datetime.now()

    # Nearest = earliest window whose start is in the future
    future = [w for w in windows if _parse_date(w.get("start")) >= now]
    nearest = min(future, key=lambda w: _parse_date(w.get("start")), default=None) or windows[0]

    # Best = highest final_score (or score)
    best = max(windows, key=lambda w: w.get("final_score") or w.get("score") or 0)

    return best, nearest


def _parse_date(d: Optional[str]) -> datetime:
    if not d:
        return datetime.max
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%B %Y"):
        try:
            return datetime.strptime(d, fmt)
        except Exception:
            pass
    return datetime.max


def _promise_to_verdict(state: Optional[str]) -> str:
    """Convert evaluator promise_state to Yes / No / Moderate."""
    if not state:
        return "Moderate"
    s = state.lower()
    if any(k in s for k in ("promis", "yes", "strong", "favorable", "favour")):
        return "Yes"
    if any(k in s for k in ("block", "denied", "no ", "not ")):
        return "No"
    return "Moderate"


def _score_to_verdict(score: float, threshold_yes: float = 55.0, threshold_no: float = 35.0) -> str:
    if score >= threshold_yes:
        return "Yes"
    if score <= threshold_no:
        return "No"
    return "Moderate"


def _ordinal(n: int) -> str:
    """Return ordinal string for a house number (1 → '1st', 7 → '7th')."""
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    return f"{n}{suffixes.get(n if n <= 3 else 0, 'th')}"


# ─────────────────────────────────────────────────────────────────────────
# Topic-specific evaluation functions
# ─────────────────────────────────────────────────────────────────────────

async def evaluate_marriage(chart: ChartData) -> Dict[str, Any]:
    """
    Marriage timing + spouse traits — no LLM.
    Returns a dict ready for the formatter.
    """
    # Run evaluator
    result = _marriage_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    # Timing windows
    windows = get_timing_windows(chart, "Marriage Timing", domain="Marriage")
    best, nearest = _best_and_nearest(windows)

    # Spouse direction
    kp_marriage = ad.get("kp_marriage_analysis", {})
    spouse_dir_data = kp_marriage.get("spouse_direction") or {}
    spouse_direction = spouse_dir_data.get("direction", "—")

    # Nature of marriage (love vs arranged)
    # KP rule: if 5th house connects to 7th CSL significations → love marriage
    marriage_nature, marriage_nature_reason = _derive_marriage_nature(chart.planets, chart.houses)

    # 7th cusp details for context
    cusp7 = next((h for h in chart.houses if h.get("house") == 7), {})
    csl7  = cusp7.get("cusp_sub_lord", "—")

    return {
        "promise_state": result.promise_state,
        "nearest_window": nearest,
        "best_window":    best,
        "spouse_direction": spouse_direction,
        "marriage_nature":  marriage_nature,
        "marriage_nature_reason": marriage_nature_reason,
        "csl7": csl7,
        "all_windows": windows,
    }


def _derive_marriage_nature(planets: Dict, houses: List[Dict]) -> Tuple[str, str]:
    """
    Love if 5th CSL or Venus signifies 7th/5th prominently; arranged otherwise.
    Returns (nature, reason) — reason is chart-specific.
    """
    try:
        cusp5  = next((h for h in houses if h.get("house") == 5), {})
        csl5   = cusp5.get("cusp_sub_lord", "") or "—"
        cusp7  = next((h for h in houses if h.get("house") == 7), {})
        csl7   = cusp7.get("cusp_sub_lord", "") or "—"
        venus  = planets.get("Venus", {})
        v_house = venus.get("house", 0)

        # Venus in 5th or 7th house is a love indicator
        if v_house in (5, 7):
            reason = (
                f"Venus in {_ordinal(v_house)} house is a direct love indicator; "
                f"7th CSL is {csl7}"
            )
            return "Love Marriage", reason

        # 5th CSL in 5th or 7th house chain
        csl5_planet = planets.get(csl5, {})
        csl5_house  = csl5_planet.get("house", 0)
        if csl5_house in (5, 7):
            reason = (
                f"5th CSL ({csl5}) is placed in {_ordinal(csl5_house)} house, "
                f"linking romance to 7th; Venus is in {_ordinal(v_house)} house"
            )
            return "Love Marriage", reason

        reason = (
            f"Venus in {_ordinal(v_house)} house; 5th CSL ({csl5}) in "
            f"{_ordinal(csl5_house) if csl5_house else '—'} house — "
            f"no strong 5th–7th connection; 7th CSL is {csl7}"
        )
        return "Arranged Marriage", reason
    except Exception:
        return "—", "—"


async def evaluate_job(chart: ChartData) -> Dict[str, Any]:
    """
    Job timing + obstacle check — no LLM.
    """
    result = _career_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    windows = get_timing_windows(chart, "Job Start Timing", domain="Career")
    best, nearest = _best_and_nearest(windows)

    # Obstacle check: if career house lords are weak or negative promise
    has_obstacles = _has_career_obstacles(ad)

    # Service vs Business
    svb = ad.get("service_vs_business") or ad.get("career_role_resonance") or {}
    service_score  = svb.get("service", 0)
    business_score = svb.get("business", 0)
    job_verdict = "Yes" if service_score >= business_score else "Moderate"

    # House-lord context for specific details
    summary      = (ad.get("career_analysis_summary") or {})
    weak_lords   = summary.get("weak_lords", 0)
    strong_lords = summary.get("strong_lords", 0)
    cusp6  = next((h for h in chart.houses if h.get("house") == 6), {})
    cusp10 = next((h for h in chart.houses if h.get("house") == 10), {})
    csl6   = cusp6.get("cusp_sub_lord", "—")
    csl10  = cusp10.get("cusp_sub_lord", "—")

    return {
        "promise_state":  result.promise_state,
        "nearest_window": nearest,
        "best_window":    best,
        "has_obstacles":  has_obstacles,
        "job_verdict":    job_verdict,
        "all_windows":    windows,
        "job_details": {
            "csl6":         csl6,
            "csl10":        csl10,
            "weak_lords":   weak_lords,
            "strong_lords": strong_lords,
        },
    }


def _has_career_obstacles(ad: Dict) -> bool:
    """True if career analysis shows significant negative signification."""
    try:
        summary = ad.get("career_analysis_summary", {})
        weak = summary.get("weak_lords", 0)
        strong = summary.get("strong_lords", 0)
        return weak > strong
    except Exception:
        return False


async def evaluate_house(chart: ChartData) -> Dict[str, Any]:
    """
    House/property purchase — no LLM.
    """
    result = _property_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    windows = get_timing_windows(chart, "Prospects of Property", domain="Finance")
    best, nearest = _best_and_nearest(windows)

    purchase_verdict = _promise_to_verdict(result.promise_state)

    cusp4  = next((h for h in chart.houses if h.get("house") == 4), {})
    cusp11 = next((h for h in chart.houses if h.get("house") == 11), {})
    csl4   = cusp4.get("cusp_sub_lord", "—")
    csl11  = cusp11.get("cusp_sub_lord", "—")

    return {
        "promise_state":    result.promise_state,
        "purchase_verdict": purchase_verdict,
        "nearest_window":   nearest,
        "best_window":      best,
        "all_windows":      windows,
        "csl4":             csl4,
        "csl11":            csl11,
    }


async def evaluate_career_best(chart: ChartData) -> Dict[str, Any]:
    """
    Career suggestions (non-timing) — no LLM.
    """
    result = _career_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    svb = ad.get("service_vs_business") or ad.get("career_role_resonance") or {}
    service_score  = svb.get("service", 0)
    business_score = svb.get("business", 0)
    hybrid_score   = svb.get("hybrid", 0)

    if service_score >= business_score and service_score >= hybrid_score:
        career_type = "Service / Employment"
    elif business_score >= service_score and business_score >= hybrid_score:
        career_type = "Business / Entrepreneurship"
    else:
        career_type = "Hybrid (Service + Business)"

    # Derive top career fields from planet-to-profession mapping
    career_fields = _derive_career_fields(chart.planets, chart.houses)

    # Obstacle analysis
    has_obstacles = _has_career_obstacles(ad)
    summary      = (ad.get("career_analysis_summary") or {})
    weak_lords   = summary.get("weak_lords", 0)
    strong_lords = summary.get("strong_lords", 0)

    # 10th house CSL / lord for specific reason text
    cusp10 = next((h for h in chart.houses if h.get("house") == 10), {})
    csl10  = cusp10.get("cusp_sub_lord", "—")
    lord10 = cusp10.get("rashi_lord", "—")

    return {
        "promise_state":  result.promise_state,
        "career_type":    career_type,
        "career_fields":  career_fields,
        "has_obstacles":  has_obstacles,
        "svb_scores":     svb,
        "csl10_planet":   csl10,
        "lord10_planet":  lord10,
        "weak_lords":     weak_lords,
        "strong_lords":   strong_lords,
    }


def _derive_career_fields(planets: Dict, houses: List[Dict]) -> str:
    """
    Map 10th CSL / 10th lord planet to broad career fields.
    Falls back to Sun/Mercury/Saturn indicators.
    """
    try:
        cusp10 = next((h for h in houses if h.get("house") == 10), {})
        csl10  = cusp10.get("cusp_sub_lord", "")
        lord10 = cusp10.get("rashi_lord", "")

        planet_career_map = {
            "Sun":     "Government, Administration, Politics, Leadership",
            "Moon":    "Hospitality, Healthcare, Public Sector, Real Estate",
            "Mars":    "Engineering, Defence, Sports, Real Estate, Surgery",
            "Mercury": "IT, Finance, Accounting, Communication, Teaching",
            "Jupiter": "Education, Law, Finance, Consulting, Spirituality",
            "Venus":   "Arts, Media, Fashion, Hospitality, Beauty, Luxury",
            "Saturn":  "Manufacturing, Construction, Labour, Oil & Gas, Mining",
            "Rahu":    "Technology, Foreign Companies, Innovation, Media",
            "Ketu":    "Research, Spirituality, Alternative Medicine, IT",
        }

        fields = planet_career_map.get(csl10) or planet_career_map.get(lord10) or "—"
        return fields
    except Exception:
        return "—"


async def evaluate_business(chart: ChartData) -> Dict[str, Any]:
    """
    Business suitability — no LLM.
    """
    result = _business_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    svb = ad.get("unified_business_verdict") or ad.get("service_vs_business") or {}
    business_score = svb.get("business", 0)
    service_score  = svb.get("service", 0)

    business_verdict = _score_to_verdict(business_score * 10)   # scale 0-10 → 0-100

    # Top industries from business_suitability_matrix
    matrix = ad.get("business_suitability_matrix", {})
    top_industries = _top_industries(matrix)

    return {
        "promise_state":     result.promise_state,
        "business_verdict":  business_verdict,
        "top_industries":    top_industries,
        "svb_scores":        svb,
    }


def _top_industries(matrix: Dict) -> str:
    """Return a comma-joined string of the top 3 business types."""
    try:
        scored = [
            (name, info.get("score", 0))
            for name, info in matrix.items()
            if isinstance(info, dict) and info.get("verdict", "").upper() == "YES"
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return ", ".join(n for n, _ in scored[:3]) or "General Trade / Services"
    except Exception:
        return "—"


async def evaluate_government_job(chart: ChartData) -> Dict[str, Any]:
    """
    Government job scope — no LLM.
    Uses Sun (govt significator) and 6th/10th house analysis.
    """
    result = _career_eval.evaluate(chart.planets, chart.houses)
    ad     = result.additional_data or {}

    sun = chart.planets.get("Sun", {})
    sun_house = sun.get("house", 0)

    # Government job indicators: Sun in 1, 5, 9, 10 or 10th CSL sub-lord = Sun
    cusp10 = next((h for h in chart.houses if h.get("house") == 10), {})
    csl10  = cusp10.get("cusp_sub_lord", "")

    govt_score = 0
    if sun_house in (1, 5, 9, 10):
        govt_score += 3
    if csl10 == "Sun":
        govt_score += 3
    if sun.get("is_retro"):
        govt_score -= 1

    govt_verdict = "Yes" if govt_score >= 3 else ("Moderate" if govt_score >= 1 else "No")

    # Exam-clearing ability: Mercury (intellect) + Saturn (discipline) strength
    mercury = chart.planets.get("Mercury", {})
    saturn  = chart.planets.get("Saturn", {})
    exam_score = 0
    if mercury.get("house") in (1, 4, 5, 9, 10):
        exam_score += 2
    if saturn.get("house") in (1, 3, 6, 10, 11):
        exam_score += 2
    exam_verdict = "Yes" if exam_score >= 3 else ("Moderate" if exam_score >= 1 else "No")

    # Timing — use "Job Start Timing" windows (government service is a job)
    windows = get_timing_windows(chart, "Job Start Timing", domain="Career")
    best, nearest = _best_and_nearest(windows)

    return {
        "promise_state":  result.promise_state,
        "govt_verdict":   govt_verdict,
        "exam_verdict":   exam_verdict,
        "nearest_window": nearest,
        "best_window":    best,
        "all_windows":    windows,
        # Chart-specific details for rich display
        "sun_house":      sun_house,
        "sun_retro":      bool(sun.get("is_retro")),
        "csl10":          csl10 or "—",
        "mercury_house":  mercury.get("house", 0),
        "saturn_house":   saturn.get("house", 0),
        "govt_score":     govt_score,
        "exam_score":     exam_score,
    }

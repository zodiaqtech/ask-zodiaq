"""
Formatters — convert raw engine output into ZodiaQResponse objects.
No LLM involved; all descriptions are derived from astrological data.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.models.response import ItemType, ZodiaQItem, ZodiaQResponse
from app.engine.zodiaq_engine import _fmt_date_range


# ── Shared "consult more" bullet lists ────────────────────────────────────

_CONSULT_MARRIAGE = [
    "Spouse nature, personality and compatibility",
    "Number of children and their prospects",
    "Manglik dosha analysis and remedies",
    "Delay or obstacles in marriage",
    "Remedies and Advice",
]

_CONSULT_JOB = [
    "Career fields and roles aligned with natural talents",
    "Immediate employment and pursuing higher studies",
    "Promotion and growth prospects",
    "Remedies and Advice",
]

_CONSULT_HOUSE = [
    "Most auspicious time to purchase",
    "Risks or challenges in property endeavours",
    "Vastu guidance for property",
    "Remedies and Advice",
]

_CONSULT_CAREER = [
    "Job opportunities and timing",
    "Prospects for promotion, leadership, and success",
    "Side business and multiple income sources",
    "Remedies and Advice",
]

_CONSULT_BUSINESS = [
    "Best timings and directions for launching a business",
    "Suggestions for taking a loan",
    "Partnership or individual business ownership",
    "Remedies and Advice",
]

_CONSULT_GOVT = [
    "Career fields aligned with government sector",
    "Specific exam strategy and timing",
    "Foreign government job prospects",
    "Remedies and Advice",
]


# ── Helper ────────────────────────────────────────────────────────────────

def _window_reason(window: Optional[Dict]) -> Optional[str]:
    """Short technical reason from a timing window dict."""
    if not window:
        return None
    dasha = window.get("dasha", "")
    score = window.get("final_score") or window.get("score")
    parts = []
    if dasha:
        parts.append(f"Dasha: {dasha}")
    if score is not None:
        parts.append(f"KP Score: {score:.1f}/100")
    return " | ".join(parts) if parts else None


def _window_details(window: Optional[Dict]) -> Optional[str]:
    """Human-readable detail line for a timing window."""
    if not window:
        return None
    score = window.get("final_score") or window.get("score") or 0
    if score >= 70:
        strength = "very strong"
    elif score >= 50:
        strength = "strong"
    elif score >= 35:
        strength = "moderate"
    else:
        strength = "mild"
    return f"Planetary alignment during this period is {strength} for this event."


# ─────────────────────────────────────────────────────────────────────────
# Per-topic formatters
# ─────────────────────────────────────────────────────────────────────────

def format_marriage(data: Dict[str, Any]) -> ZodiaQResponse:
    nearest = data.get("nearest_window")
    best    = data.get("best_window")
    nearest_str = _fmt_date_range(nearest)
    best_str    = _fmt_date_range(best)

    # If best and nearest are the same window, show it once as "Most Favourable"
    same_window = (
        nearest and best and
        nearest.get("dasha") == best.get("dasha")
    )

    items = []

    if nearest_str:
        items.append(ZodiaQItem(
            label="Next favourable Yog",
            type=ItemType.DATE_RANGE,
            value=nearest_str,
            details=_window_details(nearest),
            reason=_window_reason(nearest),
        ))

    if best_str and not same_window:
        items.append(ZodiaQItem(
            label="Most favourable Yog",
            type=ItemType.DATE_RANGE,
            value=best_str,
            details=_window_details(best),
            reason=_window_reason(best),
        ))
    elif best_str and same_window:
        # Update label of first item to indicate it is also the best
        if items:
            items[0].label = "Most & Next favourable Yog"

    if not items:
        items.append(ZodiaQItem(
            label="Favourable Yog",
            type=ItemType.TEXT,
            value="Could not determine — please check birth data",
        ))

    # Nature of marriage
    marriage_nature = data.get("marriage_nature", "—")
    if marriage_nature and marriage_nature != "—":
        items.append(ZodiaQItem(
            label="Nature of Marriage",
            type=ItemType.TEXT,
            value=marriage_nature,
            details=(
                "Indicated by Venus placement and 5th–7th house connection."
            ),
        ))

    # Spouse direction
    direction = data.get("spouse_direction", "—")
    if direction and direction != "—":
        items.append(ZodiaQItem(
            label="Direction of your spouse's birthplace",
            type=ItemType.TEXT,
            value=direction,
            details="Derived from 7th cusp sign direction in KP system.",
        ))

    return ZodiaQResponse(
        topic="marriage",
        category="Marriage Prediction",
        question="When will I get married?",
        items=items,
        consult_more=_CONSULT_MARRIAGE,
        promise_state=data.get("promise_state"),
    )


def format_job(data: Dict[str, Any]) -> ZodiaQResponse:
    nearest = data.get("nearest_window")
    nearest_str = _fmt_date_range(nearest)

    items = []

    # Timing item
    if nearest_str:
        items.append(ZodiaQItem(
            label="You are likely to secure a job at",
            type=ItemType.DATE_RANGE,
            value=nearest_str,
            details=_window_details(nearest),
            reason=_window_reason(nearest),
        ))
    else:
        items.append(ZodiaQItem(
            label="You are likely to secure a job at",
            type=ItemType.TEXT,
            value="Timing unclear — please verify birth details",
        ))

    # Obstacle item
    has_obstacles = data.get("has_obstacles", False)
    items.append(ZodiaQItem(
        label="You may face certain obstacles in your career journey",
        verdict="Yes" if has_obstacles else "No",
        type=ItemType.VERDICT,
        details=(
            "Challenging house lords indicate some hurdles before job stability."
            if has_obstacles else
            "Career house lords are relatively strong — obstacles are minimal."
        ),
        reason="Based on 6th/10th house lord strength analysis.",
    ))

    return ZodiaQResponse(
        topic="job",
        category="Job Prediction",
        question="When will I get a Job?",
        items=items,
        consult_more=_CONSULT_JOB,
        promise_state=data.get("promise_state"),
    )


def format_house(data: Dict[str, Any]) -> ZodiaQResponse:
    purchase_verdict = data.get("purchase_verdict", "Moderate")
    nearest = data.get("nearest_window")
    nearest_str = _fmt_date_range(nearest)

    items = [
        ZodiaQItem(
            label="Ability to purchase a house or land",
            verdict=purchase_verdict,
            type=ItemType.VERDICT,
            details=(
                "4th and 11th house lords indicate strong property promise."
                if purchase_verdict == "Yes" else
                "Property houses show some delay — patience recommended."
            ),
            reason="Based on 4th CSL signification and 11th house strength.",
        ),
        ZodiaQItem(
            label="Will I be able to purchase a house or land?",
            verdict=purchase_verdict,
            type=ItemType.VERDICT,
            value=nearest_str or None,
            details=_window_details(nearest) if nearest else None,
            reason=_window_reason(nearest),
        ),
    ]

    return ZodiaQResponse(
        topic="house",
        category="House Purchase Prediction",
        question="When will I buy a House?",
        items=items,
        consult_more=_CONSULT_HOUSE,
        promise_state=data.get("promise_state"),
    )


def format_career_best(data: Dict[str, Any]) -> ZodiaQResponse:
    career_type   = data.get("career_type", "—")
    career_fields = data.get("career_fields", "—")
    has_obstacles = data.get("has_obstacles", False)

    items = [
        ZodiaQItem(
            label="Best-suited career track, field, and roles aligned with natural talents",
            verdict="Yes",
            type=ItemType.VERDICT,
            details=f"{career_type}. Fields: {career_fields}.",
            reason="Based on 10th CSL, 10th lord, and Service vs Business scoring.",
        ),
        ZodiaQItem(
            label=(
                "Risks of layoff, stagnation, lack of recognition, "
                "workplace politics, and career instability"
            ),
            verdict="Yes" if has_obstacles else "No",
            type=ItemType.VERDICT,
            details=(
                "Some career challenges visible from weak house lords — "
                "remedies recommended."
                if has_obstacles else
                "Career lords are strong — risks of instability are low."
            ),
            reason="Derived from 6th/10th house lord strength balance.",
        ),
    ]

    return ZodiaQResponse(
        topic="career_best",
        category="Career Suggestions",
        question="Which career is best for me?",
        items=items,
        consult_more=_CONSULT_CAREER,
        promise_state=data.get("promise_state"),
    )


def format_business(data: Dict[str, Any]) -> ZodiaQResponse:
    business_verdict = data.get("business_verdict", "Moderate")
    top_industries   = data.get("top_industries", "—")

    items = [
        ZodiaQItem(
            label="Business or Entrepreneurship",
            verdict=business_verdict,
            type=ItemType.VERDICT,
            details=(
                "Business houses (2nd, 7th, 11th) show favourable signification."
                if business_verdict == "Yes" else
                "Chart leans toward service/employment over independent business."
            ),
            reason="Based on KP business house CSL scoring and Service vs Business matrix.",
        ),
        ZodiaQItem(
            label="Industries or places that favour your success",
            verdict="Yes" if top_industries and top_industries != "—" else "Moderate",
            type=ItemType.VERDICT,
            details=top_industries if top_industries and top_industries != "—" else "—",
            reason="Derived from planetary business suitability matrix.",
        ),
    ]

    return ZodiaQResponse(
        topic="business",
        category="Business Potential",
        question="Should I start my own Business?",
        items=items,
        consult_more=_CONSULT_BUSINESS,
        promise_state=data.get("promise_state"),
    )


def format_government_job(data: Dict[str, Any]) -> ZodiaQResponse:
    govt_verdict = data.get("govt_verdict", "Moderate")
    exam_verdict = data.get("exam_verdict", "Moderate")
    nearest      = data.get("nearest_window")
    nearest_str  = _fmt_date_range(nearest)

    items = [
        ZodiaQItem(
            label="Scope for government job in kundali",
            verdict=govt_verdict,
            type=ItemType.VERDICT,
            details=(
                "Sun is well-placed and 10th CSL indicates government service."
                if govt_verdict == "Yes" else
                "Sun placement and 10th CSL do not strongly favour government role."
            ),
            reason="Based on Sun house placement and 10th CSL analysis.",
        ),
        ZodiaQItem(
            label="Ability to clear government exams with dedication",
            verdict=exam_verdict,
            type=ItemType.VERDICT,
            details=(
                "Mercury and Saturn placements support exam success."
                if exam_verdict == "Yes" else
                "Mercury/Saturn positions indicate the need for extra preparation."
            ),
            reason="Mercury (intellect) + Saturn (discipline) house analysis.",
        ),
        ZodiaQItem(
            label="Favorable period for success in government exams",
            verdict="Yes" if nearest_str else "Moderate",
            type=ItemType.VERDICT if not nearest_str else ItemType.DATE_RANGE,
            value=nearest_str,
            details=_window_details(nearest) if nearest else "No clear timing window found.",
            reason=_window_reason(nearest),
        ),
    ]

    return ZodiaQResponse(
        topic="government_job",
        category="Government Job Prediction",
        question="Government job prospects?",
        items=items,
        consult_more=_CONSULT_GOVT,
        promise_state=data.get("promise_state"),
    )

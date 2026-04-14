"""
Ask ZodiaQ API routes.
Single endpoint: POST /ask  →  returns ZodiaQResponse for one topic.
"""
from __future__ import annotations

import logging
import traceback

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from zodiaq.models.request import ZodiaQRequest, ZodiaQTopic
from zodiaq.models.response import ZodiaQResponse
from zodiaq.engine import zodiaq_engine as engine
from zodiaq.engine import formatters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["zodiaq"])


@router.post("/ask", response_model=ZodiaQResponse, summary="Ask ZodiaQ — single topic")
async def ask_zodiaq(req: ZodiaQRequest) -> ZodiaQResponse:
    """
    Accept birth data + a topic, run pure astrological computation
    (NO LLM), and return a structured ZodiaQResponse.

    Topics:
    - **marriage**       → When will I get married?
    - **job**            → When will I get a job?
    - **house**          → When will I buy a house?
    - **career_best**    → Which career is best for me?
    - **business**       → Should I start my own business?
    - **government_job** → Will I get a government job?
    """
    bd = req.birth_data
    logger.info(
        f"[ask_zodiaq] topic={req.topic.value}, "
        f"name={bd.name}, dob={bd.dob}, tob={bd.tob}"
    )

    try:
        # ── 1. Fetch and normalise the birth chart (KP + Vedic API) ─────
        chart = await engine.fetch_chart(
            name=bd.name,
            sex=bd.sex_full,   # normalised to "male"/"female"
            dob=bd.dob,
            tob=bd.tob,
            lat=bd.lat,
            lon=bd.lon,
            timezone=bd.timezone,
        )

        # ── 2. Route to the correct topic evaluator ───────────────────
        topic = req.topic

        lang = req.language   # "Hindi" or "English"

        if topic == ZodiaQTopic.MARRIAGE:
            data     = await engine.evaluate_marriage(chart)
            response = formatters.format_marriage(data, language=lang)

        elif topic == ZodiaQTopic.JOB:
            data     = await engine.evaluate_job(chart)
            response = formatters.format_job(data, language=lang)

        elif topic == ZodiaQTopic.HOUSE:
            data     = await engine.evaluate_house(chart)
            response = formatters.format_house(data, language=lang)

        elif topic == ZodiaQTopic.CAREER_BEST:
            data     = await engine.evaluate_career_best(chart)
            response = formatters.format_career_best(data, language=lang)

        elif topic == ZodiaQTopic.BUSINESS:
            data     = await engine.evaluate_business(chart)
            response = formatters.format_business(data, language=lang)

        elif topic == ZodiaQTopic.GOVERNMENT_JOB:
            data     = await engine.evaluate_government_job(chart)
            response = formatters.format_government_job(data, language=lang)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown topic: {topic}")

        logger.info(
            f"[ask_zodiaq] ✅ topic={topic.value} → "
            f"{len(response.items)} items, promise={response.promise_state}"
        )
        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"[ask_zodiaq] ❌ Error for topic={req.topic.value}: {exc}\n"
            + traceback.format_exc()
        )
        # Return a graceful error response instead of a 500
        return ZodiaQResponse(
            topic=req.topic.value,
            category="Error",
            question="—",
            items=[],
            consult_more=[],
            error=str(exc),
        )


@router.get("/health", summary="Health check")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "ask-zodiaq"})


@router.get("/topics", summary="List supported topics")
async def list_topics() -> JSONResponse:
    """Return all supported topics with their display labels."""
    return JSONResponse({
        "topics": [
            {"value": "marriage",       "label": "When will I get married?",       "category": "Marriage Prediction"},
            {"value": "job",            "label": "When will I get a job?",          "category": "Job Prediction"},
            {"value": "house",          "label": "When will I buy a house?",        "category": "House Purchase Prediction"},
            {"value": "career_best",    "label": "Which career is best for me?",    "category": "Career Suggestions"},
            {"value": "business",       "label": "Should I start my own business?", "category": "Business Potential"},
            {"value": "government_job", "label": "Will I get a government job?",    "category": "Government Job Prediction"},
        ]
    })

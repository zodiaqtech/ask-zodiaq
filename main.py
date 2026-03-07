"""
Ask ZodiaQ — LLM-free astrological instant answers.

Usage:
    cp .env.example .env
    # Set AI_PREDIGEST_PATH in .env
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Bootstrap: ensure AI-predigest is importable before anything else ─────
from dotenv import load_dotenv

load_dotenv()  # load .env from project root

_predigest_path = os.environ.get(
    "AI_PREDIGEST_PATH", "/Users/sankit/Downloads/AI-predigest"
)
if _predigest_path not in sys.path:
    sys.path.insert(0, _predigest_path)

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ask-zodiaq")

# ── App lifecycle ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Ask ZodiaQ starting up…")
    logger.info(f"   AI-predigest path: {_predigest_path}")
    yield
    logger.info("🛑 Ask ZodiaQ shutting down.")


# ── FastAPI app ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Ask ZodiaQ",
    description=(
        "Instant astrological answers powered by KP & Vedic analysis — "
        "no LLM, no waiting."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────
from app.api.routes import router

app.include_router(router)

# ── Dev entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8001)),
        reload=True,
    )

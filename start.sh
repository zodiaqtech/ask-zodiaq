#!/bin/bash
# ── Ask ZodiaQ start script ────────────────────────────────────────
# Uses the existing AI-predigest venv (no separate install needed).

VENV="/Users/sankit/Desktop/Personalised Horoscope/venv"
PORT="${PORT:-8002}"

echo "🚀 Starting Ask ZodiaQ on port $PORT..."
echo "   Venv: $VENV"
echo "   AI-predigest: /Users/sankit/Downloads/AI-predigest"
echo ""

# Change to ask-zodiaq project root (where main.py lives)
cd "$(dirname "$0")"

"$VENV/bin/uvicorn" main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --reload \
    --reload-dir zodiaq

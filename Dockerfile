FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# ── AI-predigest (bundled as a dependency) ────────────────────────────────
# Copy AI-predigest code into the image
COPY ai-predigest/ /app/ai-predigest/
RUN pip install --no-cache-dir -r /app/ai-predigest/requirements.txt

# ── Ask ZodiaQ ────────────────────────────────────────────────────────────
COPY requirements.txt /app/ask-zodiaq/
RUN pip install --no-cache-dir -r /app/ask-zodiaq/requirements.txt

COPY . /app/ask-zodiaq/

WORKDIR /app/ask-zodiaq

# Environment
ENV AI_PREDIGEST_PATH=/app/ai-predigest
ENV HOST=0.0.0.0
ENV PORT=8002

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/api/v1/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

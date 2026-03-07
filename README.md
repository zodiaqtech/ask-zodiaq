# Ask ZodiaQ Service

Instant astrological answers **without any LLM call**.
Built on top of the AI-predigest KP + Vedic evaluation engine.

---

## Supported Topics

| Card (home screen)              | topic value      | Category                  |
|---------------------------------|------------------|---------------------------|
| When will I get married?        | `marriage`       | Marriage Prediction       |
| When will I get a job?          | `job`            | Job Prediction            |
| When will I buy a house?        | `house`          | House Purchase Prediction |
| Which career is best for me?    | `career_best`    | Career Suggestions        |
| Should I start my own business? | `business`       | Business Potential        |
| Will I get a government job?    | `government_job` | Government Job Prediction |

---

## Architecture

```
Ask ZodiaQ (this repo)
│
├── main.py                  FastAPI app
├── app/
│   ├── api/routes.py        POST /api/v1/ask   ← single endpoint
│   ├── engine/
│   │   ├── zodiaq_engine.py LLM-free orchestrator
│   │   └── formatters.py    Topic-specific response builders
│   └── models/
│       ├── request.py       ZodiaQRequest (birth data + topic)
│       └── response.py      ZodiaQResponse (items + consult_more)
│
└── AI-predigest (external)  ← imported via sys.path
    ├── app/services/astro_api.py          KP + Vedic API clients
    ├── app/services/kp_timing_enhanced.py KP timing engine
    ├── app/services/astro_engine.py       Data normalisation helpers
    └── app/domains/*/evaluator.py         Domain evaluators
```

**No LLM is involved.**  All answers come directly from:
- KP Cusp Sub-Lord signification scoring
- Planet/house-lord strength analysis
- KP timing windows (dasha + transit scoring)

---

## Setup

```bash
# 1. Clone this repo
git clone <ask-zodiaq-repo>
cd ask-zodiaq

# 2. Create virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set AI_PREDIGEST_PATH to your AI-predigest checkout

# 5. Run
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## API Reference

### `POST /api/v1/ask`

Request body:
```json
{
  "birth_data": {
    "name": "Rahul Sharma",
    "sex": "M",
    "dob": "15/08/1990",
    "tob": "06:30",
    "lat": 28.6139,
    "lon": 77.2090,
    "timezone": 5.5
  },
  "topic": "marriage"
}
```

Response:
```json
{
  "topic": "marriage",
  "category": "Marriage Prediction",
  "question": "When will I get married?",
  "items": [
    {
      "label": "Next favourable Yog",
      "type": "date_range",
      "value": "Nov 2025 – Mar 2026",
      "details": "Planetary alignment during this period is strong for this event.",
      "reason": "Dasha: Ra-Ve-Mo | KP Score: 72.5/100"
    },
    {
      "label": "Most favourable Yog",
      "type": "date_range",
      "value": "Jun 2026 – Sep 2026",
      "details": "Planetary alignment during this period is very strong for this event.",
      "reason": "Dasha: Ra-Ve-Su | KP Score: 85.0/100"
    },
    {
      "label": "Nature of Marriage",
      "type": "text",
      "value": "Love Marriage"
    },
    {
      "label": "Direction of your spouse's birthplace",
      "type": "text",
      "value": "North"
    }
  ],
  "consult_more": [
    "Spouse nature, personality and compatibility",
    "Number of children and their prospects",
    "Manglik dosha analysis and remedies",
    "Delay or obstacles in marriage",
    "Remedies and Advice"
  ],
  "promise_state": "promised"
}
```

### `GET /api/v1/topics`
Returns all supported topics with their display labels.

### `GET /api/v1/health`
Health check.

---

## Response Model

| Field           | Type              | Description                                 |
|-----------------|-------------------|---------------------------------------------|
| `topic`         | string            | Topic key (e.g. `"marriage"`)               |
| `category`      | string            | Screen title (e.g. `"Marriage Prediction"`) |
| `question`      | string            | User-facing question string                 |
| `items`         | `ZodiaQItem[]`    | Answer rows — see below                     |
| `consult_more`  | `string[]`        | "Talk to an astrologer" bullet list         |
| `promise_state` | string \| null    | KP promise verdict for the event            |
| `error`         | string \| null    | Non-null only when computation failed       |

### ZodiaQItem

| Field     | Type                                    | Description                          |
|-----------|-----------------------------------------|--------------------------------------|
| `label`   | string                                  | Row heading                          |
| `verdict` | `"Yes"` \| `"No"` \| `"Moderate"` \| null | Yes/No indicator               |
| `value`   | string \| null                          | Date range or plain text             |
| `type`    | `date_range` \| `verdict` \| `text`     | Front-end rendering hint             |
| `details` | string \| null                          | Supporting body text                 |
| `reason`  | string \| null                          | Technical reason (dasha + KP score) |

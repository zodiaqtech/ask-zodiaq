# Ask Zodiaq — API Curl Commands

**Base URL:** `https://ask-zodiaq-app.azurewebsites.net`

---

## 1. Health Check

```bash
curl -s https://ask-zodiaq-app.azurewebsites.net/api/v1/health
```

---

## 2. Topics List

```bash
curl -s https://ask-zodiaq-app.azurewebsites.net/api/v1/topics
```

---

## 3. Ask — Marriage

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"marriage"}'
```

---

## 4. Ask — Job

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"job"}'
```

---

## 5. Ask — Government Job

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"government_job"}'
```

---

## 6. Ask — House Purchase

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"house"}'
```

---

## 7. Ask — Career Best

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"career_best"}'
```

---

## 8. Ask — Business

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"business"}'
```

---

## 9. Run All Topics at Once

```bash
for topic in marriage job government_job house career_best business; do
  echo "\n=== $topic ==="
  curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
    -H "Content-Type: application/json" \
    -d "{\"birth_data\":{\"name\":\"Test User\",\"dob\":\"15/05/1990\",\"tob\":\"10:30\",\"lat\":28.6139,\"lon\":77.2090,\"timezone\":5.5,\"sex\":\"M\"},\"topic\":\"$topic\"}"
done
```

---

## Request Body Reference

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `name` | string | Any | `"Test User"` |
| `dob` | string | DD/MM/YYYY | `"15/05/1990"` |
| `tob` | string | HH:MM (24hr) | `"10:30"` |
| `lat` | float | Decimal degrees | `28.6139` |
| `lon` | float | Decimal degrees | `77.2090` |
| `timezone` | float | UTC offset | `5.5` |
| `sex` | string | M or F | `"M"` |
| `topic` | string | See topics list | `"marriage"` |

---

## Available Topics

| Topic Key | Description |
|-----------|-------------|
| `marriage` | Marriage timing & nature |
| `job` | Job prospects & timing |
| `government_job` | Govt job scope & timing |
| `house` | House purchase prospects |
| `career_best` | Best career path |
| `business` | Business prospects |

---

## Response Structure

```json
{
  "topic": "marriage",
  "category": "Marriage Prediction",
  "question": "When will I get married?",
  "items": [
    {
      "label": "Next favourable Yog",
      "verdict": null,
      "value": "Jul 2026 – Aug 2026",
      "type": "date_range",
      "details": "Rahu Mahadasha · Sun Antardasha...",
      "reason": "Dasha: Rahu-Sun-Moon | KP Score: 17.5/100"
    }
  ],
  "consult_more": ["Spouse nature", "..."],
  "promise_state": "promised_with_obstacles",
  "error": null
}
```

### Item Types

| `type` | `verdict` | `value` | Use Case |
|--------|-----------|---------|----------|
| `date_range` | null | "Jul 2026 – Aug 2026" | Timing predictions |
| `verdict` | Yes / No / Moderate | null | Yes/No questions |
| `text` | null | "Arranged Marriage" | Descriptive answers |

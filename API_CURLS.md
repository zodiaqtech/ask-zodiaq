# Ask ZodiaQ — API Curl Commands

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

## 3. Ask — Marriage (English)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"marriage","language":"English"}'
```

---

## 4. Ask — Marriage (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"marriage","language":"Hindi"}'
```

---

## 5. Ask — Job (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"job","language":"Hindi"}'
```

---

## 6. Ask — Government Job (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"government_job","language":"Hindi"}'
```

---

## 7. Ask — House Purchase (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"house","language":"Hindi"}'
```

---

## 8. Ask — Career Best (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"career_best","language":"Hindi"}'
```

---

## 9. Ask — Business (Hindi)

```bash
curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"birth_data":{"name":"Test User","dob":"15/05/1990","tob":"10:30","lat":28.6139,"lon":77.2090,"timezone":5.5,"sex":"M"},"topic":"business","language":"Hindi"}'
```

---

## 10. Run All Topics in Hindi

```bash
for topic in marriage job government_job house career_best business; do
  echo "\n=== $topic ==="
  curl -s -X POST https://ask-zodiaq-app.azurewebsites.net/api/v1/ask \
    -H "Content-Type: application/json" \
    -d "{\"birth_data\":{\"name\":\"Test User\",\"dob\":\"15/05/1990\",\"tob\":\"10:30\",\"lat\":28.6139,\"lon\":77.2090,\"timezone\":5.5,\"sex\":\"M\"},\"topic\":\"$topic\",\"language\":\"Hindi\"}"
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
| `language` | string | `"Hindi"` or `"English"` | `"Hindi"` (default: `"English"`) |

---

## Available Topics

| Topic Key | Description (English) | Description (Hindi) |
|-----------|----------------------|---------------------|
| `marriage` | Marriage timing & nature | मेरी शादी कब होगी? |
| `job` | Job prospects & timing | मुझे नौकरी कब मिलेगी? |
| `government_job` | Govt job scope & timing | क्या मुझे सरकारी नौकरी मिलेगी? |
| `house` | House purchase prospects | मैं मकान कब खरीदूंगा? |
| `career_best` | Best career path | मेरे लिए सबसे अच्छा करियर कौन सा है? |
| `business` | Business prospects | क्या मुझे अपना व्यवसाय शुरू करना चाहिए? |

---

## Response Structure

```json
{
  "topic": "marriage",
  "category": "विवाह भविष्यवाणी",
  "question": "मेरी शादी कब होगी?",
  "summary": "विवाह दृढ़ता से वादा किया गया है। निकटतम योग: Jul 2027 – Nov 2027।",
  "items": [
    {
      "label": "अगला अनुकूल योग",
      "type": "timing",
      "timing": "Jul 2027 – Nov 2027",
      "verdict": null,
      "value": null,
      "astro_reason": "दशा: शनि महादशा · बृहस्पति अंतर्दशा | KP स्कोर: 59.0/100"
    }
  ],
  "consult_more": ["जीवनसाथी का स्वभाव, व्यक्तित्व और अनुकूलता", "..."],
  "promise_state": "promised",
  "error": null
}
```

### Item Types

| `type` | `timing` | `verdict` | `value` | Use Case |
|--------|----------|-----------|---------|----------|
| `timing` | "Jul 2027 – Nov 2027" | null | null | Date-range predictions |
| `verdict` | null (or date hint) | Yes / No / Moderate | null | Yes/No questions |
| `text` | null | null | "अरेंज्ड विवाह" | Descriptive answers |

---

## Docker Image

```
askzodiaqacr.azurecr.io/ask-zodiaq:latest   # always latest
askzodiaqacr.azurecr.io/ask-zodiaq:v5       # Hindi/English bilingual release
```

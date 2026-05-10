"""
Formatters — convert raw engine output into ZodiaQResponse objects.
No LLM involved; all descriptions are derived from astrological data.

Rendering contract (mirrors response.py):
  ItemType.TIMING  → `timing` field set, verdict/value null
  ItemType.VERDICT → `verdict` field set, optional `timing` hint, value null
  ItemType.TEXT    → `value` field set, verdict/timing null
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from zodiaq.models.response import ItemType, ZodiaQItem, ZodiaQResponse
from zodiaq.engine.zodiaq_engine import _fmt_date_range


# ─────────────────────────────────────────────────────────────────────────────
# Language helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_hindi(language: str) -> bool:
    return language.strip().lower() == "hindi"


# ── "Consult more" lists ──────────────────────────────────────────────────────

_CONSULT_MARRIAGE_EN = [
    "Spouse nature, personality and compatibility",
    "Number of children and their prospects",
    "Manglik dosha analysis and remedies",
    "Delay or obstacles in marriage",
    "Remedies and Advice",
]
_CONSULT_MARRIAGE_HI = [
    "जीवनसाथी का स्वभाव, व्यक्तित्व और अनुकूलता",
    "संतान की संख्या और उनकी संभावनाएं",
    "मांगलिक दोष विश्लेषण और उपाय",
    "विवाह में देरी या बाधाएं",
    "उपाय और सलाह",
]

_CONSULT_JOB_EN = [
    "Career fields and roles aligned with natural talents",
    "Immediate employment and pursuing higher studies",
    "Promotion and growth prospects",
    "Remedies and Advice",
]
_CONSULT_JOB_HI = [
    "प्राकृतिक प्रतिभा के अनुरूप करियर क्षेत्र और भूमिकाएं",
    "तत्काल रोजगार और उच्च शिक्षा की संभावनाएं",
    "पदोन्नति और विकास की संभावनाएं",
    "उपाय और सलाह",
]

_CONSULT_HOUSE_EN = [
    "Most auspicious time to purchase",
    "Risks or challenges in property endeavours",
    "Vastu guidance for property",
    "Remedies and Advice",
]
_CONSULT_HOUSE_HI = [
    "खरीद के लिए सबसे शुभ समय",
    "संपत्ति प्रयासों में जोखिम या चुनौतियां",
    "संपत्ति के लिए वास्तु मार्गदर्शन",
    "उपाय और सलाह",
]

_CONSULT_CAREER_EN = [
    "Job opportunities and timing",
    "Prospects for promotion, leadership, and success",
    "Side business and multiple income sources",
    "Remedies and Advice",
]
_CONSULT_CAREER_HI = [
    "नौकरी के अवसर और समय",
    "पदोन्नति, नेतृत्व और सफलता की संभावनाएं",
    "साइड बिज़नेस और आय के अनेक स्रोत",
    "उपाय और सलाह",
]

_CONSULT_BUSINESS_EN = [
    "Best timings and directions for launching a business",
    "Suggestions for taking a loan",
    "Partnership or individual business ownership",
    "Remedies and Advice",
]
_CONSULT_BUSINESS_HI = [
    "व्यवसाय शुरू करने के लिए सर्वोत्तम समय और दिशा",
    "ऋण लेने के सुझाव",
    "साझेदारी या व्यक्तिगत व्यवसाय स्वामित्व",
    "उपाय और सलाह",
]

_CONSULT_GOVT_EN = [
    "Career fields aligned with government sector",
    "Specific exam strategy and timing",
    "Foreign government job prospects",
    "Remedies and Advice",
]
_CONSULT_GOVT_HI = [
    "सरकारी क्षेत्र से जुड़े करियर क्षेत्र",
    "विशेष परीक्षा रणनीति और समय",
    "विदेशी सरकारी नौकरी की संभावनाएं",
    "उपाय और सलाह",
]


# ── Promise-state labels ──────────────────────────────────────────────────────

_PROMISE_LABELS_EN = {
    "Strongly Promised": "Strongly Promised",
    "Promised with Delays": "Promised with Delays",
    "Not Indicated": "Not Indicated",
    "Promised": "Promised",
    "Neutral": "Neutral",
}
_PROMISE_LABELS_HI = {
    "Strongly Promised": "दृढ़ता से वादा किया गया",
    "Promised with Delays": "देरी के साथ वादा किया गया",
    "Not Indicated": "संकेतित नहीं",
    "Promised": "वादा किया गया",
    "Neutral": "तटस्थ",
}


# ── Generic fallback text ─────────────────────────────────────────────────────

_NO_WINDOW_EN   = "Could not determine — please verify birth details"
_NO_WINDOW_HI   = "निर्धारित नहीं किया जा सका — कृपया जन्म विवरण सत्यापित करें"
_NO_DASHA_EN    = "No favourable dasha window found in the next 7 years."
_NO_DASHA_HI    = "अगले 7 वर्षों में कोई अनुकूल दशा अवधि नहीं मिली।"
_NO_WINDOW_7_EN = "No clear window in next 7 years — revisit after checking extended dasha"
_NO_WINDOW_7_HI = "अगले 7 वर्षों में कोई स्पष्ट अवधि नहीं — विस्तारित दशा जांचने के बाद पुनः देखें"
_VERIFY_DOB_EN  = "Timing unclear — please verify birth details"
_VERIFY_DOB_HI  = "समय अस्पष्ट — कृपया जन्म विवरण सत्यापित करें"


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

_DASHA_FULL: Dict[str, str] = {
    "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury",
    "Ju": "Jupiter", "Ve": "Venus", "Sa": "Saturn", "Ra": "Rahu", "Ke": "Ketu",
}

_DASHA_FULL_HI: Dict[str, str] = {
    # 2-letter abbreviations
    "Su": "सूर्य", "Mo": "चंद्रमा", "Ma": "मंगल", "Me": "बुध",
    "Ju": "बृहस्पति", "Ve": "शुक्र", "Sa": "शनि", "Ra": "राहु", "Ke": "केतु",
    # Full English planet names (API may return either form)
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु",
}

_DASHA_LEVELS_EN = ["Mahadasha", "Antardasha", "Pratyantar"]
_DASHA_LEVELS_HI = ["महादशा", "अंतर्दशा", "प्रत्यंतर"]


def _expand_dasha(dasha_str: str, language: str = "English") -> str:
    """'Ra-Su-Mo' → 'Rahu Mahadasha · Sun Antardasha · Moon Pratyantar'"""
    if not dasha_str:
        return ""
    parts  = dasha_str.split("-")
    if _is_hindi(language):
        full   = [_DASHA_FULL_HI.get(p, p) for p in parts]
        labels = _DASHA_LEVELS_HI
    else:
        full   = [_DASHA_FULL.get(p, p) for p in parts]
        labels = _DASHA_LEVELS_EN
    return " · ".join(
        f"{name} {labels[i]}" if i < len(labels) else name
        for i, name in enumerate(full)
    )


def _ordinal(n: int) -> str:
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    return f"{n}{suffixes.get(n if n <= 3 else 0, 'th')}"


def _ordinal_hi(n: int) -> str:
    """Hindi ordinal: 1 → 'पहला', 2 → 'दूसरा', …, n → 'nवाँ'"""
    hi_ordinals = {
        1: "पहले", 2: "दूसरे", 3: "तीसरे", 4: "चौथे", 5: "पाँचवें",
        6: "छठे", 7: "सातवें", 8: "आठवें", 9: "नौवें", 10: "दसवें",
        11: "ग्यारहवें", 12: "बारहवें",
    }
    return hi_ordinals.get(n, f"{n}वें")


def _window_reason(window: Optional[Dict], language: str = "English") -> str:
    """
    Rich astrological reason: Dasha, KP score, transit support, age, and delay info.
    Example: "Dasha: Rahu MD · Sun AD · Moon PD | KP: 42.0 | Transit: +8.2 (strong) | Age: 28"
    """
    if not window:
        return ""
    parts = []
    hi    = _is_hindi(language)
    dasha = window.get("dasha", "")
    score = window.get("final_score") or window.get("score")
    transit_score = window.get("transit_score")
    age   = window.get("age_at_start")
    delay = window.get("delay_years")
    retrograde_flag = window.get("needs_resonant_jump", False)

    if dasha:
        label = "दशा" if hi else "Dasha"
        parts.append(f"{label}: {_expand_dasha(dasha, language)}")

    if score is not None:
        label = "KP स्कोर" if hi else "KP Score"
        parts.append(f"{label}: {score:.1f}/100")

    if transit_score is not None and transit_score != 0:
        sign  = "+" if transit_score >= 0 else ""
        label = "गोचर" if hi else "Transit"
        parts.append(f"{label}: {sign}{transit_score:.1f}")

    if age is not None:
        label = "आयु" if hi else "Age"
        parts.append(f"{label}: {int(age)}")

    if delay and delay > 0:
        label = "देरी" if hi else "Delay"
        parts.append(f"{label}: ~{int(delay)}y (retrograde)")

    if retrograde_flag:
        parts.append("वक्री-विलंब संभव" if hi else "retrograde delay possible")

    return " | ".join(parts)


def _window_strength(window: Optional[Dict], language: str = "English") -> str:
    if not window:
        return "हल्का" if _is_hindi(language) else "mild"
    score = window.get("final_score") or window.get("score") or 0
    if _is_hindi(language):
        if score >= 70:
            return "अत्यंत मजबूत"
        if score >= 50:
            return "मजबूत"
        if score >= 35:
            return "मध्यम"
        return "हल्का"
    else:
        if score >= 70:
            return "very strong"
        if score >= 50:
            return "strong"
        if score >= 35:
            return "moderate"
        return "mild"


_DASHA_MARRIAGE_EN: Dict[str, str] = {
    "Venus":   "Venus is the natural karaka of love and partnerships — very auspicious for marriage",
    "Jupiter": "Jupiter blesses unions and expands family — highly favourable for marriage",
    "Moon":    "Moon rules emotions and bonding — a sensitive, nurturing period for relationships",
    "Mars":    "Mars activates 7th-house energy — quick decisions possible, watch impulsiveness",
    "Mercury": "Mercury smooths communication and agreements — good for marriage negotiations",
    "Saturn":  "Saturn brings responsibility and stability, but may create delays",
    "Sun":     "Sun highlights partnerships publicly — prominent union possible",
    "Rahu":    "Rahu can trigger sudden or unconventional unions, especially cross-culture",
    "Ketu":    "Ketu is spiritually detached — marriage may arise from karmic or unexpected circumstances",
}
_DASHA_MARRIAGE_HI: Dict[str, str] = {
    "Venus":   "शुक्र प्रेम और विवाह का नैसर्गिक कारक है — विवाह के लिए अत्यंत शुभ काल",
    "Jupiter": "बृहस्पति गृहस्थ जीवन को आशीर्वाद देते हैं — परिवार विस्तार हेतु बहुत अनुकूल",
    "Moon":    "चंद्रमा भावनात्मक जुड़ाव और बंधन का कारक — रिश्तों के लिए संवेदनशील व अनुकूल काल",
    "Mars":    "मंगल सप्तम भाव को सक्रिय करते हैं — निर्णय जल्दी हो सकता है, आवेग पर ध्यान दें",
    "Mercury": "बुध संवाद और समझौते को सुगम बनाते हैं — विवाह वार्ता के लिए उपयुक्त",
    "Saturn":  "शनि जिम्मेदारी और स्थिरता लाते हैं, किंतु विलंब की संभावना बनी रहती है",
    "Sun":     "सूर्य दशा में विवाह सामाजिक रूप से प्रमुख हो सकता है",
    "Rahu":    "राहु अचानक या असामान्य विवाह का संकेत देते हैं, अंतरजातीय संभावना भी",
    "Ketu":    "केतु आध्यात्मिक वैराग्य का कारक — विवाह कर्मगत या अप्रत्याशित परिस्थितियों से हो सकता है",
}

_DASHA_CAREER_EN: Dict[str, str] = {
    "Sun":     "Sun's period favours government roles, authority, and leadership",
    "Moon":    "Moon's period suits public-dealing, hospitality, and emotional intelligence roles",
    "Mars":    "Mars activates effort and drive — good for competitive fields, engineering, defence",
    "Mercury": "Mercury sharpens intellect and communication — IT, finance, and teaching thrive",
    "Jupiter": "Jupiter expands opportunities — education, law, consulting, and management benefit",
    "Venus":   "Venus brings creativity — arts, media, hospitality, and luxury sectors are supported",
    "Saturn":  "Saturn rewards discipline and hard work — steady career growth over time",
    "Rahu":    "Rahu accelerates unconventional career paths — technology, foreign firms, media",
    "Ketu":    "Ketu promotes research, spirituality, and niche expertise",
}
_DASHA_CAREER_HI: Dict[str, str] = {
    "Sun":     "सूर्य दशा सरकारी भूमिका, अधिकार और नेतृत्व के लिए अनुकूल है",
    "Moon":    "चंद्रमा दशा में जन-सेवा, आतिथ्य और भावनात्मक बुद्धिमत्ता के क्षेत्र उपयुक्त हैं",
    "Mars":    "मंगल प्रयास और ऊर्जा को सक्रिय करते हैं — इंजीनियरिंग, रक्षा और प्रतिस्पर्धी क्षेत्र अनुकूल",
    "Mercury": "बुध बौद्धिक क्षमता बढ़ाते हैं — आईटी, वित्त और शिक्षण में अच्छे अवसर",
    "Jupiter": "बृहस्पति अवसरों का विस्तार करते हैं — शिक्षा, कानून, परामर्श और प्रबंधन लाभकर",
    "Venus":   "शुक्र सृजनात्मकता लाते हैं — कला, मीडिया, आतिथ्य और विलासिता क्षेत्र सक्रिय",
    "Saturn":  "शनि अनुशासन और परिश्रम को पुरस्कृत करते हैं — करियर में धीरे-धीरे स्थिर विकास",
    "Rahu":    "राहु असामान्य करियर पथ को गति देते हैं — प्रौद्योगिकी, विदेशी कंपनियाँ, मीडिया",
    "Ketu":    "केतु अनुसंधान, अध्यात्म और विशेष विशेषज्ञता को बढ़ावा देते हैं",
}


def _dasha_md_quality(dasha_str: str, context: str, language: str) -> str:
    """Return a one-line dasha-lord quality note for the Mahadasha planet."""
    if not dasha_str:
        return ""
    md = dasha_str.split("-")[0] if "-" in dasha_str else dasha_str
    # Expand abbreviation
    md_full = _DASHA_FULL.get(md, md)
    if context == "marriage":
        table_en = _DASHA_MARRIAGE_EN
        table_hi = _DASHA_MARRIAGE_HI
    else:
        table_en = _DASHA_CAREER_EN
        table_hi = _DASHA_CAREER_HI
    if _is_hindi(language):
        return table_hi.get(md_full, "")
    return table_en.get(md_full, "")


def _promise_summary(state: Optional[str], language: str = "English") -> str:
    """Map promise_state to a short UI-friendly label."""
    if not state:
        key = "Neutral"
    else:
        s = state.lower()
        if "strong" in s or (("promis" in s) and "obstacle" not in s):
            key = "Strongly Promised"
        elif "obstacle" in s or "delay" in s:
            key = "Promised with Delays"
        elif "block" in s or "denied" in s or "not" in s:
            key = "Not Indicated"
        elif "promis" in s or "yes" in s or "favour" in s:
            key = "Promised"
        else:
            key = "Neutral"

    if _is_hindi(language):
        return _PROMISE_LABELS_HI.get(key, key)
    return _PROMISE_LABELS_EN.get(key, key)


# ── Planet names in Hindi ─────────────────────────────────────────────────────

_PLANET_HI: Dict[str, str] = {
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु",
}


def _planet(name: str, language: str) -> str:
    if _is_hindi(language):
        return _PLANET_HI.get(name, name)
    return name


# ── Career field translations ─────────────────────────────────────────────────

_CAREER_FIELDS_HI: Dict[str, str] = {
    "Government, Administration, Politics, Leadership":
        "सरकारी सेवा, प्रशासन, राजनीति, नेतृत्व",
    "Hospitality, Healthcare, Public Sector, Real Estate":
        "आतिथ्य, स्वास्थ्य सेवा, सार्वजनिक क्षेत्र, रियल एस्टेट",
    "Engineering, Defence, Sports, Real Estate, Surgery":
        "इंजीनियरिंग, रक्षा, खेल, रियल एस्टेट, शल्य चिकित्सा",
    "IT, Finance, Accounting, Communication, Teaching":
        "आईटी, वित्त, लेखा, संचार, शिक्षण",
    "Education, Law, Finance, Consulting, Spirituality":
        "शिक्षा, कानून, वित्त, परामर्श, अध्यात्म",
    "Arts, Media, Fashion, Hospitality, Beauty, Luxury":
        "कला, मीडिया, फैशन, आतिथ्य, सौंदर्य, विलासिता",
    "Manufacturing, Construction, Labour, Oil & Gas, Mining":
        "विनिर्माण, निर्माण, श्रम, तेल एवं गैस, खनन",
    "Technology, Foreign Companies, Innovation, Media":
        "प्रौद्योगिकी, विदेशी कंपनियां, नवाचार, मीडिया",
    "Research, Spirituality, Alternative Medicine, IT":
        "अनुसंधान, अध्यात्म, वैकल्पिक चिकित्सा, आईटी",
    "—": "—",
}

_VERDICT_HI: Dict[str, str] = {
    "yes": "हाँ", "no": "नहीं", "moderate": "मध्यम",
    "Yes": "हाँ", "No": "नहीं", "Moderate": "मध्यम",
}


# ─────────────────────────────────────────────────────────────────────────────
# Per-topic formatters
# ─────────────────────────────────────────────────────────────────────────────

def format_marriage(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi = _is_hindi(language)
    nearest     = data.get("nearest_window")
    best        = data.get("best_window")
    nearest_str = _fmt_date_range(nearest)
    best_str    = _fmt_date_range(best)
    same_window = (
        nearest and best and
        nearest.get("dasha") == best.get("dasha")
    )

    items = []

    # ── Timing items ──────────────────────────────────────────────────────────
    if nearest_str:
        base_reason  = _window_reason(nearest, language)
        dasha_note   = _dasha_md_quality(nearest.get("dasha", ""), "marriage", language)
        transit_ok   = (nearest.get("transit_score") or 0) > 0
        if hi:
            transit_note = "गोचर ग्रह इस काल को अतिरिक्त समर्थन दे रहे हैं।" if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        else:
            transit_note = "Transiting planets additionally support this window." if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        items.append(ZodiaQItem(
            label="अगला अनुकूल योग" if hi else "Next favourable Yog",
            type=ItemType.TIMING,
            timing=nearest_str,
            astro_reason=full_reason,
        ))

    if best_str and not same_window:
        base_reason  = _window_reason(best, language)
        dasha_note   = _dasha_md_quality(best.get("dasha", ""), "marriage", language)
        transit_ok   = (best.get("transit_score") or 0) > 0
        if hi:
            transit_note = "यह काल गोचर ग्रहों द्वारा भी समर्थित है — उच्च संभावना।" if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        else:
            transit_note = "Transit planets reinforce this as the peak window." if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        items.append(ZodiaQItem(
            label="सबसे अनुकूल योग" if hi else "Most favourable Yog",
            type=ItemType.TIMING,
            timing=best_str,
            astro_reason=full_reason,
        ))
    elif same_window and items:
        items[0].label = "सबसे अनुकूल और अगला योग" if hi else "Most & Next favourable Yog"

    if not items:
        items.append(ZodiaQItem(
            label="अनुकूल योग" if hi else "Favourable Yog",
            type=ItemType.TEXT,
            value=_NO_WINDOW_HI if hi else _NO_WINDOW_EN,
            astro_reason=_NO_DASHA_HI if hi else _NO_DASHA_EN,
        ))

    # ── Nature of marriage ────────────────────────────────────────────────────
    nature        = data.get("marriage_nature", "—")
    nature_reason = data.get("marriage_nature_reason", "")
    if nature and nature != "—":
        if hi:
            nature_label = "विवाह की प्रकृति"
            nature_val   = "प्रेम विवाह" if "Love" in nature else "अरेंज्ड विवाह"
            # Translate astrological reason terms to Hindi
            nature_rsn = (
                nature_reason
                .replace("Venus", "शुक्र").replace("Saturn", "शनि")
                .replace("Jupiter", "बृहस्पति").replace("Mars", "मंगल")
                .replace("Mercury", "बुध").replace("Moon", "चंद्रमा")
                .replace("Sun", "सूर्य").replace("Rahu", "राहु").replace("Ketu", "केतु")
                .replace(" house", " भाव").replace("house", "भाव")
                .replace("5th", "पाँचवें").replace("7th", "सातवें")
                .replace("1st", "पहले").replace("2nd", "दूसरे").replace("3rd", "तीसरे")
                .replace("4th", "चौथे").replace("6th", "छठे").replace("8th", "आठवें")
                .replace("9th", "नौवें").replace("10th", "दसवें")
                .replace("11th", "ग्यारहवें").replace("12th", "बारहवें")
                .replace("no strong", "कोई मजबूत नहीं")
                .replace("linking romance to", "रोमांस को जोड़ता है")
                .replace("is a direct love indicator", "प्रत्यक्ष प्रेम संकेतक है")
                .replace("connection", "संबंध")
                .replace("placed in", "स्थित है")
                if nature_reason
                else "शुक्र की स्थिति और पाँचवें–सातवें भाव के संबंध से संकेतित।"
            )
        else:
            nature_label = "Nature of Marriage"
            nature_val   = nature
            nature_rsn   = nature_reason or "Indicated by Venus placement and 5th–7th house connection."

        items.append(ZodiaQItem(
            label=nature_label,
            type=ItemType.TEXT,
            value=nature_val,
            astro_reason=nature_rsn,
        ))

    # ── Spouse direction ──────────────────────────────────────────────────────
    direction = data.get("spouse_direction", "—")
    csl7      = data.get("csl7", "—")
    if direction and direction != "—":
        if hi:
            csl7_p    = _planet(csl7, language)
            csl7_note = f"सप्तम भाव का CSL {csl7_p} है, जो उस राशि का स्वामी है जिससे दिशा निकाली जाती है।" if csl7 and csl7 != "—" else "सप्तम भाव की राशि से दिशा निकाली जाती है।"
            items.append(ZodiaQItem(
                label="जीवनसाथी के जन्मस्थान की दिशा",
                type=ItemType.TEXT,
                value=direction,
                astro_reason=f"KP पद्धति में {csl7_note}",
            ))
        else:
            csl7_note = (
                f"7th house CSL is {csl7}, whose sign determines the direction."
                if csl7 and csl7 != "—" else
                "Direction is derived from the 7th cusp sign in the KP system."
            )
            items.append(ZodiaQItem(
                label="Direction of your spouse's birthplace",
                type=ItemType.TEXT,
                value=direction,
                astro_reason=csl7_note,
            ))

    # ── Summary ───────────────────────────────────────────────────────────────
    promise_label  = _promise_summary(data.get("promise_state"), language)
    if hi:
        summary_timing = f" निकटतम योग: {nearest_str}।" if nearest_str else ""
        summary  = f"विवाह {promise_label} है।{summary_timing}"
        question = "मेरी शादी कब होगी?"
        category = "विवाह भविष्यवाणी"
        consult  = _CONSULT_MARRIAGE_HI
    else:
        summary_timing = f" Nearest window: {nearest_str}." if nearest_str else ""
        summary  = f"Marriage is {promise_label}.{summary_timing}"
        question = "When will I get married?"
        category = "Marriage Prediction"
        consult  = _CONSULT_MARRIAGE_EN

    return ZodiaQResponse(
        topic="marriage",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )


def format_job(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi           = _is_hindi(language)
    nearest      = data.get("nearest_window")
    nearest_str  = _fmt_date_range(nearest)
    has_obstacles = data.get("has_obstacles", False)
    jd           = data.get("job_details", {})
    csl6         = jd.get("csl6", "—")
    csl10        = jd.get("csl10", "—")
    weak_lords   = jd.get("weak_lords", 0)
    strong_lords = jd.get("strong_lords", 0)

    csl6_p  = _planet(csl6, language)
    csl10_p = _planet(csl10, language)

    items = []

    # ── Timing ────────────────────────────────────────────────────────────────
    if nearest_str:
        base_reason = _window_reason(nearest, language)
        dasha_note  = _dasha_md_quality(nearest.get("dasha", ""), "career", language)
        transit_ok  = (nearest.get("transit_score") or 0) > 0
        if hi:
            transit_note = "गोचर ग्रह इस नौकरी-काल को और सशक्त बना रहे हैं।" if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        else:
            transit_note = "Transiting planets add further support to this employment window." if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
        items.append(ZodiaQItem(
            label="नौकरी मिलने की संभावित अवधि" if hi else "Likely period to secure a job",
            type=ItemType.TIMING,
            timing=nearest_str,
            astro_reason=full_reason,
        ))
    else:
        items.append(ZodiaQItem(
            label="नौकरी मिलने की संभावित अवधि" if hi else "Likely period to secure a job",
            type=ItemType.TEXT,
            value=_VERIFY_DOB_HI if hi else _VERIFY_DOB_EN,
            astro_reason=_NO_DASHA_HI if hi else _NO_DASHA_EN,
        ))

    # ── Obstacles verdict ─────────────────────────────────────────────────────
    if hi:
        if has_obstacles:
            obs_reason = (
                f"षष्ठ भाव CSL {csl6_p} और दशम भाव CSL {csl10_p} की KP जाँच में "
                f"{weak_lords} ग्रह कमज़ोर और {strong_lords} ग्रह बलवान पाए गए — "
                "करियर स्थिर होने से पहले कुछ बाधाएँ और संघर्ष संभव हैं।"
            )
        else:
            obs_reason = (
                f"षष्ठ भाव CSL {csl6_p} और दशम भाव CSL {csl10_p} की KP जाँच में "
                f"{strong_lords} ग्रह बलवान और {weak_lords} ग्रह कमज़ोर पाए गए — "
                "करियर मार्ग अपेक्षाकृत सुगम और बाधामुक्त दिखता है।"
            )
        items.append(ZodiaQItem(
            label="कुंडली में करियर बाधाएं",
            type=ItemType.VERDICT,
            verdict="Yes" if has_obstacles else "No",
            astro_reason=obs_reason,
        ))
    else:
        if has_obstacles:
            obs_reason = (
                f"6th CSL ({csl6}) governs service; 10th CSL ({csl10}) governs profession. "
                f"KP scoring shows {weak_lords} weak lord(s) outweighing {strong_lords} strong — "
                "expect some hurdles before career stabilises."
            )
        else:
            obs_reason = (
                f"6th CSL ({csl6}) governs service; 10th CSL ({csl10}) governs profession. "
                f"{strong_lords} strong lord(s) outweigh {weak_lords} weak — "
                "career path is relatively clear and obstacle-free."
            )
        items.append(ZodiaQItem(
            label="Career obstacles in the chart",
            type=ItemType.VERDICT,
            verdict="Yes" if has_obstacles else "No",
            astro_reason=obs_reason,
        ))

    promise_label  = _promise_summary(data.get("promise_state"), language)
    if hi:
        summary_timing = f" सबसे पहली अवधि: {nearest_str}।" if nearest_str else ""
        summary  = f"नौकरी की संभावनाएं {promise_label} हैं।{summary_timing}"
        question = "मुझे नौकरी कब मिलेगी?"
        category = "नौकरी भविष्यवाणी"
        consult  = _CONSULT_JOB_HI
    else:
        summary_timing = f" Earliest window: {nearest_str}." if nearest_str else ""
        summary  = f"Job prospects are {promise_label}.{summary_timing}"
        question = "When will I get a Job?"
        category = "Job Prediction"
        consult  = _CONSULT_JOB_EN

    return ZodiaQResponse(
        topic="job",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )


def format_house(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi               = _is_hindi(language)
    purchase_verdict = data.get("purchase_verdict", "Moderate")
    nearest          = data.get("nearest_window")
    nearest_str      = _fmt_date_range(nearest)
    csl4             = _planet(data.get("csl4", "—"), language)
    csl11            = _planet(data.get("csl11", "—"), language)

    if hi:
        if purchase_verdict == "Yes":
            astro_rsn = (
                f"KP पद्धति में चतुर्थ भाव संपत्ति का और एकादश भाव लाभ का कारक है। "
                f"चतुर्थ भाव CSL {csl4} और एकादश भाव CSL {csl11} — "
                "दोनों भावों में ग्रह-संकेत मजबूत हैं, संपत्ति खरीद संभव है।"
            )
        else:
            astro_rsn = (
                f"KP पद्धति में चतुर्थ भाव संपत्ति का और एकादश भाव लाभ का कारक है। "
                f"चतुर्थ भाव CSL {csl4} और एकादश भाव CSL {csl11} — "
                "वर्तमान में संपत्ति भावों में कुछ बाधा दिखती है; सही समय की प्रतीक्षा करें।"
            )
        items = [
            ZodiaQItem(
                label="मकान या जमीन खरीदने की क्षमता",
                type=ItemType.VERDICT,
                verdict=purchase_verdict,
                timing=nearest_str,
                astro_reason=astro_rsn,
            ),
        ]
    else:
        items = [
            ZodiaQItem(
                label="Ability to purchase a house or land",
                type=ItemType.VERDICT,
                verdict=purchase_verdict,
                timing=nearest_str,
                astro_reason=(
                    f"In KP, the 4th house (property) and 11th house (gain) are key. "
                    f"4th CSL ({data.get('csl4','—')}) and 11th CSL ({data.get('csl11','—')}) "
                    "both show strong favourable signification — property acquisition is supported."
                    if purchase_verdict == "Yes" else
                    f"In KP, the 4th house (property) and 11th house (gain) are key. "
                    f"4th CSL ({data.get('csl4','—')}) and 11th CSL ({data.get('csl11','—')}) "
                    "show some restriction — patience and awaiting the right dasha period is advised."
                ),
            ),
        ]

    promise_label = _promise_summary(data.get("promise_state"), language)
    if hi:
        summary_timing = f" अनुकूल अवधि: {nearest_str}।" if nearest_str else ""
        summary  = f"मकान खरीद {promise_label} है।{summary_timing}"
        question = "मैं मकान कब खरीदूंगा?"
        category = "मकान खरीद भविष्यवाणी"
        consult  = _CONSULT_HOUSE_HI
    else:
        summary_timing = f" Favourable period: {nearest_str}." if nearest_str else ""
        summary  = f"House purchase is {promise_label}.{summary_timing}"
        question = "When will I buy a House?"
        category = "House Purchase Prediction"
        consult  = _CONSULT_HOUSE_EN

    return ZodiaQResponse(
        topic="house",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )


def format_career_best(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi            = _is_hindi(language)
    career_type   = data.get("career_type", "—")
    career_fields = data.get("career_fields", "—")
    has_obstacles = data.get("has_obstacles", False)
    csl10         = _planet(data.get("csl10_planet", "—"), language)
    lord10        = _planet(data.get("lord10_planet", "—"), language)
    weak_lords    = data.get("weak_lords", 0)
    strong_lords  = data.get("strong_lords", 0)

    # Translate career type
    if hi:
        _career_type_map = {
            "Service / Employment":          "सेवा / रोजगार",
            "Business / Entrepreneurship":   "व्यवसाय / उद्यमिता",
            "Hybrid (Service + Business)":   "मिश्रित (सेवा + व्यवसाय)",
        }
        career_type_hi = _career_type_map.get(career_type, career_type)
        csl10_note  = f"दसवें भाव CSL: {csl10}" if csl10 not in ("—", "") else ""
        lord10_note = f"दसवें भाव स्वामी: {lord10}" if lord10 not in ("—", "") else ""
        planet_note = " | ".join(filter(None, [csl10_note, lord10_note]))

        career_fields_hi = _CAREER_FIELDS_HI.get(career_fields, career_fields)
        items = [
            ZodiaQItem(
                label="सबसे उपयुक्त करियर ट्रैक",
                type=ItemType.TEXT,
                value=f"{career_type_hi} — {career_fields_hi}",
                astro_reason=planet_note or "दसवें भाव CSL और सेवा-व्यवसाय स्कोरिंग से निर्धारित।",
            ),
            ZodiaQItem(
                label="करियर अस्थिरता का जोखिम",
                type=ItemType.VERDICT,
                verdict="Yes" if has_obstacles else "No",
                astro_reason=(
                    f"{weak_lords} कमजोर ग्रह {strong_lords} मजबूत ग्रहों से अधिक — "
                    "कुछ करियर चुनौतियां दिखाई दे रही हैं; उपाय की सिफारिश।"
                    if has_obstacles else
                    f"{strong_lords} मजबूत ग्रह {weak_lords} कमजोर ग्रहों से अधिक — "
                    "करियर ग्रह अच्छे स्थान पर हैं; स्थिरता संकेतित।"
                ),
            ),
        ]
        summary  = f"सबसे उपयुक्त: {career_type_hi}। क्षेत्र: {career_fields_hi}।"
        question = "मेरे लिए सबसे अच्छा करियर कौन सा है?"
        category = "करियर सुझाव"
        consult  = _CONSULT_CAREER_HI
    else:
        csl10_note  = f"10th CSL: {data.get('csl10_planet','—')}" if data.get('csl10_planet') not in ("—", "", None) else ""
        lord10_note = f"10th lord: {data.get('lord10_planet','—')}" if data.get('lord10_planet') not in ("—", "", None) else ""
        planet_note = " | ".join(filter(None, [csl10_note, lord10_note]))

        items = [
            ZodiaQItem(
                label="Best-suited career track",
                type=ItemType.TEXT,
                value=f"{career_type} — {career_fields}",
                astro_reason=planet_note or "Derived from 10th house CSL and service-vs-business scoring.",
            ),
            ZodiaQItem(
                label="Risk of career instability",
                type=ItemType.VERDICT,
                verdict="Yes" if has_obstacles else "No",
                astro_reason=(
                    f"{weak_lords} weak lord(s) outweigh {strong_lords} strong lord(s) — "
                    "some career challenges visible; remedies recommended."
                    if has_obstacles else
                    f"{strong_lords} strong lord(s) outweigh {weak_lords} weak lord(s) — "
                    "career lords are well-placed; stability is indicated."
                ),
            ),
        ]
        summary  = f"Best fit: {career_type}. Fields: {career_fields}."
        question = "Which career is best for me?"
        category = "Career Suggestions"
        consult  = _CONSULT_CAREER_EN

    return ZodiaQResponse(
        topic="career_best",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )


def format_business(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi               = _is_hindi(language)
    business_verdict = data.get("business_verdict", "Moderate")
    top_industries   = data.get("top_industries", "—")

    if hi:
        if business_verdict == "Yes":
            biz_reason = (
                "KP पद्धति में व्यवसाय के मुख्य भाव हैं — द्वितीय (धन), सप्तम (साझेदारी) और "
                "एकादश (लाभ)। आपकी कुंडली में इन भावों के ग्रह-संकेत अनुकूल हैं।"
            )
        else:
            biz_reason = (
                "KP विश्लेषण में व्यवसाय भाव (द्वितीय, सप्तम, एकादश) की तुलना में "
                "सेवा भाव (षष्ठ, दशम) अधिक प्रबल हैं — कुंडली नौकरी की ओर अधिक झुकती है।"
            )

        items = [
            ZodiaQItem(
                label="कुंडली में व्यवसाय या उद्यमिता का संकेत",
                type=ItemType.VERDICT,
                verdict=business_verdict,
                astro_reason=biz_reason,
            ),
            ZodiaQItem(
                label="आपके लिए अनुकूल उद्योग",
                type=ItemType.TEXT,
                value=top_industries if top_industries and top_industries != "—" else "सामान्य व्यापार / सेवाएं",
                astro_reason="ग्रहों की व्यावसायिक उपयुक्तता मैट्रिक्स से निर्धारित।",
            ),
        ]
        verdict_hi = _VERDICT_HI.get(business_verdict, business_verdict)
        summary  = (
            f"आपकी कुंडली में व्यवसाय {verdict_hi} है। "
            f"प्रमुख क्षेत्र: {top_industries}।"
        )
        question = "क्या मुझे अपना व्यवसाय शुरू करना चाहिए?"
        category = "व्यवसाय संभावना"
        consult  = _CONSULT_BUSINESS_HI
    else:
        items = [
            ZodiaQItem(
                label="Business or Entrepreneurship indicated",
                type=ItemType.VERDICT,
                verdict=business_verdict,
                astro_reason=(
                    "KP business houses (2nd — wealth, 7th — partnership, 11th — profit) "
                    "show strong favourable signification in your chart."
                    if business_verdict == "Yes" else
                    "KP analysis shows the service houses (6th, 10th) are stronger than "
                    "business houses (2nd, 7th, 11th) — chart leans toward employment."
                ),
            ),
            ZodiaQItem(
                label="Favourable industries for you",
                type=ItemType.TEXT,
                value=top_industries if top_industries and top_industries != "—" else "General Trade / Services",
                astro_reason="Derived from 10th house CSL and planetary business suitability matrix.",
            ),
        ]
        summary  = (
            f"Business is {business_verdict.lower()} in your chart. "
            f"Top sectors: {top_industries}."
        )
        question = "Should I start my own Business?"
        category = "Business Potential"
        consult  = _CONSULT_BUSINESS_EN

    return ZodiaQResponse(
        topic="business",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )


def format_government_job(data: Dict[str, Any], language: str = "English") -> ZodiaQResponse:
    hi            = _is_hindi(language)
    govt_verdict  = data.get("govt_verdict", "Moderate")
    exam_verdict  = data.get("exam_verdict", "Moderate")
    nearest       = data.get("nearest_window")
    nearest_str   = _fmt_date_range(nearest)

    sun_house     = data.get("sun_house", 0)
    sun_retro     = data.get("sun_retro", False)
    csl10         = data.get("csl10", "—")
    mercury_house = data.get("mercury_house", 0)
    saturn_house  = data.get("saturn_house", 0)

    if hi:
        sun_desc  = f"{_ordinal_hi(sun_house)} भाव में सूर्य" if sun_house else "सूर्य"
        if sun_retro:
            sun_desc += " (वक्री — सरकारी मामलों में सावधानी आवश्यक)"
        csl10_p  = _planet(csl10, language)
        csl10_desc   = f"दशम भाव का CSL {csl10_p} है" if csl10 not in ("—", "") else "दशम भाव CSL"
        mercury_desc = f"{_ordinal_hi(mercury_house)} भाव में बुध" if mercury_house else "बुध"
        saturn_desc  = f"{_ordinal_hi(saturn_house)} भाव में शनि" if saturn_house else "शनि"

        if govt_verdict == "Yes":
            govt_reason = (
                f"सूर्य सरकार और अधिकार का नैसर्गिक कारक है। "
                f"{sun_desc} और {csl10_desc} — कुंडली में सरकारी सेवा की प्रबल संभावना दिखती है।"
            )
        else:
            govt_reason = (
                f"सूर्य सरकार और अधिकार का नैसर्गिक कारक है। "
                f"{sun_desc}; {csl10_desc} — वर्तमान स्थिति में कुंडली सरकारी भूमिका के लिए दृढ़ता से अनुकूल नहीं है।"
            )

        if exam_verdict == "Yes":
            exam_reason = (
                f"बुध बुद्धि और स्मरण का कारक है, शनि अनुशासन और कठिन परिश्रम का। "
                f"{mercury_desc} और {saturn_desc} — दोनों की अनुकूल स्थिति परीक्षा में सफलता का संकेत देती है।"
            )
        else:
            exam_reason = (
                f"बुध बुद्धि का कारक है और शनि अनुशासन का। "
                f"{mercury_desc} और {saturn_desc} — "
                "इनकी वर्तमान स्थिति अनुकूल नहीं है; नियमित तैयारी और अनुशासन बहुत आवश्यक है।"
            )

        if nearest_str:
            timing_item = ZodiaQItem(
                label="सरकारी परीक्षा सफलता के लिए अनुकूल अवधि",
                type=ItemType.TIMING,
                timing=nearest_str,
                astro_reason=_window_reason(nearest, language) if nearest else _NO_DASHA_HI,
            )
        else:
            timing_item = ZodiaQItem(
                label="सरकारी परीक्षा सफलता के लिए अनुकूल अवधि",
                type=ItemType.TEXT,
                value=_NO_WINDOW_7_HI,
                astro_reason=_NO_DASHA_HI,
            )

        items = [
            ZodiaQItem(
                label="कुंडली में सरकारी नौकरी की संभावना",
                type=ItemType.VERDICT,
                verdict=govt_verdict,
                astro_reason=govt_reason,
            ),
            ZodiaQItem(
                label="सरकारी परीक्षा पास करने की क्षमता",
                type=ItemType.VERDICT,
                verdict=exam_verdict,
                astro_reason=exam_reason,
            ),
            timing_item,
        ]
        govt_verdict_hi = _VERDICT_HI.get(govt_verdict, govt_verdict)
        exam_verdict_hi = _VERDICT_HI.get(exam_verdict, exam_verdict)
        summary  = (
            f"आपकी कुंडली में सरकारी नौकरी की संभावना {govt_verdict_hi} है। "
            f"परीक्षा उत्तीर्ण करने की क्षमता {exam_verdict_hi} दिखती है।"
            + (f" सबसे उपयुक्त अवधि: {nearest_str}।" if nearest_str else "")
        )
        question = "क्या मुझे सरकारी नौकरी मिलेगी?"
        category = "सरकारी नौकरी भविष्यवाणी"
        consult  = _CONSULT_GOVT_HI
    else:
        sun_desc     = f"Sun in {_ordinal(sun_house)} house" if sun_house else "Sun"
        if sun_retro:
            sun_desc += " (retrograde — caution with authorities)"
        csl10_desc   = f"10th CSL is {csl10}" if csl10 not in ("—", "") else "10th CSL"
        mercury_desc = f"Mercury in {_ordinal(mercury_house)} house" if mercury_house else "Mercury"
        saturn_desc  = f"Saturn in {_ordinal(saturn_house)} house" if saturn_house else "Saturn"

        if nearest_str:
            base_reason  = _window_reason(nearest, language) if nearest else _NO_DASHA_EN
            dasha_note   = _dasha_md_quality(nearest.get("dasha", ""), "career", language) if nearest else ""
            transit_ok   = nearest is not None and (nearest.get("transit_score") or 0) > 0
            transit_note = "Transiting planets reinforce this as a strong exam period." if transit_ok else ""
            full_reason  = " | ".join(filter(None, [base_reason, dasha_note, transit_note]))
            timing_item = ZodiaQItem(
                label="Favourable period for government exam success",
                type=ItemType.TIMING,
                timing=nearest_str,
                astro_reason=full_reason,
            )
        else:
            timing_item = ZodiaQItem(
                label="Favourable period for government exam success",
                type=ItemType.TEXT,
                value=_NO_WINDOW_7_EN,
                astro_reason=_NO_DASHA_EN,
            )

        items = [
            ZodiaQItem(
                label="Government job scope in your chart",
                type=ItemType.VERDICT,
                verdict=govt_verdict,
                astro_reason=(
                    f"Sun is the natural karaka for government and authority. "
                    f"{sun_desc} and {csl10_desc} indicate strong government service potential."
                    if govt_verdict == "Yes" else
                    f"Sun is the natural karaka for government. "
                    f"{sun_desc}; {csl10_desc} — chart does not strongly favour a government role at present."
                ),
            ),
            ZodiaQItem(
                label="Ability to clear government exams",
                type=ItemType.VERDICT,
                verdict=exam_verdict,
                astro_reason=(
                    f"Mercury rules intellect; Saturn rules discipline and sustained effort. "
                    f"{mercury_desc} and {saturn_desc} are well-placed — exam clearing potential is strong."
                    if exam_verdict == "Yes" else
                    f"Mercury rules intellect; Saturn rules discipline. "
                    f"{mercury_desc} and {saturn_desc} require strengthening — "
                    "consistent preparation and structured study are essential."
                ),
            ),
            timing_item,
        ]
        summary  = (
            f"Government job is {govt_verdict.lower()} in your chart. "
            f"Exam ability: {exam_verdict}."
            + (f" Best window: {nearest_str}." if nearest_str else "")
        )
        question = "Will I get a Government Job?"
        category = "Government Job Prediction"
        consult  = _CONSULT_GOVT_EN

    return ZodiaQResponse(
        topic="government_job",
        category=category,
        question=question,
        summary=summary,
        items=items,
        consult_more=consult,
        promise_state=data.get("promise_state"),
    )

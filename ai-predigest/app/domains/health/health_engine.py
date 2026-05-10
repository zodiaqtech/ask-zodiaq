from app.core.astro_constants import (
    # --- planet & house access ---
    get_planet,
    normalize_planet,
    _p,
    _lord_of,
    get_cusp_sub_lord,
    get_signified_houses,

    # --- aspects & conjunctions ---
    _conjoined,
    _has_evil_aspect,
    _aspected_by,
    has_harmonious_aspect,

    # --- house / placement helpers ---
    _in_house,
    _in_houses,
    _count_planets_in_house,

    # --- star-lord helpers ---
    get_star_lord_of_planet,

    # --- sign helpers ---
    SIGN_LORDS,
    sign_disease_map
)

def evaluate_health(planets, houses):
    """
    COMPLETE KP Classical Health Evaluator (universal rules only).
    - Uses: 6th/8th/12th cusp sub-lords, star-lord -> sign mapping,
            planet->organ mapping, sign disease map,
            planet-in-sign detailed tables for Sun/Moon/Mars/Mercury,
            5th & 11th cure logic.
    - Returns: list[str] of deduped human-readable indicators.
    """

    out, seen = [], set()
    def add(msg):
        if msg and msg not in seen:
            out.append(msg); seen.add(msg)

    # ---------------------------
    # Helpers / safe accessors
    # ---------------------------
    def G(name): 
        return get_planet(name, planets)
    def house_of(name):
        p = G(name)
        return p.get("house") if p else None
    def sl(hno): 
        return get_cusp_sub_lord(hno, houses)
    def star_lord_of(planet_name):
        # safest attempt to read nakshatra lord from planet object
        p = G(planet_name) if isinstance(planet_name, str) else None
        if p:
            return normalize_planet(p.get("nakshatra_lord") or p.get("start_nakshatra_lord") or p.get("pseudo_nakshatra_lord"))
        return None
    def safe_sign_of_planet_by_name(name):
        p = G(name)
        if not p:
            return None
        return (p.get("zodiac") or p.get("pseudo_rasi") or p.get("rasi") or "").title()

    # ---------------------------
    # Planet -> organ mapping (universal)
    # ---------------------------
    planet_health_map = {
        "Sun": ["heart", "eyes", "vital fluids", "brain vitality"],
        "Moon": ["stomach", "uterus/ovaries", "lymph", "mind", "fluids"],
        "Mars": ["blood", "bone marrow", "accidents/surgery", "genitals"],
        "Mercury": ["nerves", "lungs", "skin", "speech/nervous coordination"],
        "Jupiter": ["liver", "diabetes/metabolism", "tumors"],
        "Venus": ["kidneys", "throat", "reproductive", "urinary"],
        "Saturn": ["bones", "teeth", "chronic degenerative disease"],
        "Rahu": ["mysterious/atypical disorders"],
        "Ketu": ["occult/hidden/chronic patterns"]
    }


    # ---------------------------
    # Planet-in-sign disease tables (detailed)
    # These are full tables used by classical evaluator.
    # ---------------------------
    sun_sign_disease = {
        "Aries": [
            "aphasia", "loss of conscience", "brain fever", 
            "meningitis", "cerebral anaemia", "cerebral haemorrhage",
            "fainting", "headache", "thrombosis"
        ],
        "Taurus": [
            "quinsy", "diphtheria", "polyps of the nose", "eye trouble"
        ],
        "Gemini": [
            "pleurisy", "eosinophilia", "bronchitis", "hyperemia of the lungs"
        ],
        "Cancer": [
            "anemia", "dropsy", "dyspepsia", "gastric ulcer"
        ],
        "Leo": [
            "palpitation of the heart", "backache", "spinal affections", "eye trouble"
        ],
        "Virgo": [
            "poor digestion", "poor assimilation", 
            "typhoid", "dysentery"
        ],
        "Libra": [
            "Bright's disease", "skin eruptions", "boils"
        ],
        "Scorpio": [
            "renal calculus", "genital system disturbances",
            "menstrual difficulties", "urinary trouble",
            "uterus and ovary affections"
        ],
        "Sagittarius": [
            "sciatica", "paralysis of limbs", "pulmonary diseases"
        ],
        "Capricorn": [
            "rheumatism", "skin affection", "digestive disturbances"
        ],
        "Aquarius": [
            "varicose veins", "dropsy", "poor circulation",
            "palpitation of the heart"
        ],
        "Pisces": [
            "perspiration of the feet", "intestinal troubles", "typhoid fever"
        ]
    }
    
    moon_sign_disease = {
        "Aries": [
            "insomnia", "headache", "lethargy", "weak eyes"
        ],
        "Taurus": [
            "sore throat", "eye trouble", "menstrual issues"
        ],
        "Gemini": [
            "catarrh of the lungs", "asthma", "bronchitis",
            "pneumonia", "rheumatism in arms", "shoulder sprain"
        ],
        "Cancer": [
            "chronic stomach ailments", "dropsy", "obesity",
            "epilepsy", "digestive disturbances"
        ],
        "Leo": [
            "backache", "disturbed circulation", "convulsions",
            "heart trouble", "eye defect"
        ],
        "Virgo": [
            "bowel disorder", "abdominal tumours", "peritonitis",
            "dysentery"
        ],
        "Libra": [
            "Bright's disease", "kidney abscess", "uraemia",
            "headache", "insomnia"
        ],
        "Scorpio": [
            "disturbed menses", "bladder troubles", 
            "genito-urinary disturbances", "throat troubles"
        ],
        "Sagittarius": [
            "blood disorders", "hip disease", 
            "femur fracture", "asthma"
        ],
        "Capricorn": [
            "rheumatism", "lack of synovial fluid",
            "skin eruptions", "poor digestive disturbances"
        ],
        "Aquarius": [
            "varicose veins", "leg ulcers", "dropsy",
            "hysteria", "fainting", "heart trouble"
        ],
        "Pisces": [
            "alcohol/drug issues", "foot diseases",
            "abdominal disorders"
        ]
    }
    
    mars_sign_disease = {
        "Aries": [
            "sunstroke", "cerebral haemorrhage", "congestion",
            "thrombosis", "brain fever", "delirium",
            "shooting pain in the head", "kidney inflammation",
            "renal calculi"
        ],
        "Taurus": [
            "mumps", "septic tonsils", "adenoids", "diphtheria",
            "nose bleeding", "larynx inflammation",
            "excessive menstrual flow", "scalding urine",
            "venereal ulcers", "prostate enlargement"
        ],
        "Gemini": [
            "lung haemorrhage", "pneumonia", "bronchitis",
            "arm wounds", "collar bone fracture"
        ],
        "Cancer": [
            "inflammation of stomach", "ulceration", "haemorrhage", "dyspepsia"
        ],
        "Leo": [
            "muscular rheumatism", "heart enlargement",
            "palpitation", "pericardium inflammation"
        ],
        "Virgo": [
            "typhoid", "bowel inflammation", "worms", "diarrhoea",
            "cholera", "ventral hernia", "appendicitis"
        ],
        "Libra": [
            "kidney inflammation", "excess urine", "renal stones",
            "brain fever", "sunstroke"
        ],
        "Scorpio": [
            "excessive menses", "profuse bleeding", "scalding urine",
            "renal stones", "uterus/ovary inflammation",
            "stricture", "tonsils issues", "larynx issues"
        ],
        "Sagittarius": [
            "femur fracture", "thigh ulcers", "bronchitis", "sciatica"
        ],
        "Capricorn": [
            "carbuncles", "erysipelas", "smallpox",
            "skin inflammation", "ulcerated stomach", "dyspepsia"
        ],
        "Aquarius": [
            "varicose veins", "leg fracture", "blood poisoning",
            "heart failure", "fainting", "palpitation"
        ],
        "Pisces": [
            "foot deformities", "corns", "bunions", "perspiring feet",
            "ventral hernia", "bowel inflammation", "diarrhoea"
        ]
    }


    mercury_sign_disease = {
        "Aries": [
            "brain fever", "headache", "vertigo", "neuralgia",
            "nervous disorders", "kidney lumbago"
        ],
        "Taurus": [
            "stuttering", "hoarseness", "deafness",
            "nervous genito-urinary disorders"
        ],
        "Gemini": [
            "gouty arthritis", "bronchitis", "asthma",
            "pleurisy", "nervous hip pain"
        ],
        "Cancer": [
            "nervous indigestion", "phlegm", "flatulence", "drunkenness"
        ],
        "Leo": [
            "back pain", "fainting", "heart palpitation"
        ],
        "Virgo": [
            "flatulence", "short breath", "nervous debility"
        ],
        "Libra": [
            "suppression of urine", "renal paroxysms",
            "vertigo", "nervous headache", "eye trouble"
        ],
        "Scorpio": [
            "bladder/genital pain", "menstrual trouble",
            "stuttering", "deafness"
        ],
        "Sagittarius": [
            "hip and thigh pain", "cough", "asthma", "pleurisy"
        ],
        "Capricorn": [
            "rheumatism", "knee pain", "back pain",
            "skin disease", "melancholy", "nervous indigestion",
            "flatulence"
        ],
        "Aquarius": [
            "shooting leg pain", "varicose veins", "corrupt blood",
            "palpitation", "neuralgia of the heart"
        ],
        "Pisces": [
            "gout in the feet", "general weakness",
            "lassitude", "worry", "tuberculosis", "deafness"
        ]
    }


    planet_sign_map = {
        "Sun": sun_sign_disease,
        "Moon": moon_sign_disease,
        "Mars": mars_sign_disease,
        "Mercury": mercury_sign_disease
    }

    # ---------------------------
    # 1. Retrieve sub-lords (classical KP)
    # ---------------------------
    sub6  = sl(6)
    sub8  = sl(8)
    sub12 = sl(12)
    sub5  = sl(5)
    sub11 = sl(11)

    # defensive: require sub6 to proceed for classical path
    if not sub6:
        add("❓ 6th cusp sub-lord missing — classical health inference limited.")
        # continue with partial information (we still can give organ hints)
    else:
        # signified houses by 6th sub-lord
        try:
            s6 = get_signified_houses(sub6, houses)
        except Exception:
            s6 = set()

        # Activation logic: 6 present means disease; 1 present too indicates personal constitution involvement
        if 6 in s6 and 1 in s6:
            add(f"⚠️ Disease probable: 6th & Ascendant signified by {sub6} (KP classical).")
        elif 6 in s6:
            add(f"⚠️ 6th house strongly signified by {sub6} — disease tendency present.")
        else:
            add(f"ℹ️ 6th not strongly signified by {sub6} — disease less direct (follow other indicators).")

        # organ systems from planet nature
        if sub6 in planet_health_map:
            add("🔍 Affected systems: " + ", ".join(planet_health_map[sub6]))

        # star-lord & sign chain: sub6 -> planet object -> nakshatra/star lord -> star lord's sign
        try:
            p6 = get_planet(sub6, planets) or {}
            star_of_sub6 = normalize_planet(p6.get("nakshatra_lord") or p6.get("start_nakshatra_lord") or p6.get("pseudo_nakshatra_lord"))
            # If star exists, map its sign-level disease tendencies
            if star_of_sub6:
                # star may be a planet name (Jupiter/Moon etc.)
                star_signs = get_signified_houses(star_of_sub6, houses)
                # For human-friendly messaging, find star object's sign if planet present
                star_sign = safe_sign_of_planet_by_name(star_of_sub6)
                if star_sign and star_sign in sign_disease_map:
                    add("🩺 Disease tendencies (via sub6's star-lord " + str(star_of_sub6) + " in " + str(star_sign) + "): " + ", ".join(sign_disease_map[star_sign]))
        except Exception:
            pass

        # planet-in-sign detailed for the sub6 planet itself
        try:
            # find sign where sub6 planet sits
            p_obj = get_planet(sub6, planets)
            p_sign = (p_obj.get("zodiac") or p_obj.get("pseudo_rasi") or "").title() if p_obj else None
            if sub6 in planet_sign_map and p_sign:
                table = planet_sign_map[sub6]
                if p_sign in table:
                    add(f"🎯 Specific ({sub6} in {p_sign}): " + ", ".join(table[p_sign]))
        except Exception:
            pass

    # ---------------------------
    # 2. Severe / Chronic / Hospitalisation indicators (8th / 12th)
    # KP rule: judge by what houses the CSL SIGNIFIES, not by planet nature
    # ---------------------------
    try:
        if sub8:
            s8 = set(get_signified_houses(sub8, houses))
            if {6, 8, 12} & s8:
                add(f"☠️ 8th CSL {sub8} signifies houses {sorted({6,8,12}&s8)} → chronic/severe disease tendency.")
            elif {1, 5, 11} & s8:
                add(f"✅ 8th CSL {sub8} signifies houses {sorted({1,5,11}&s8)} → longevity protected, chronic risk low.")
    except Exception:
        pass

    try:
        if sub12:
            s12 = set(get_signified_houses(sub12, houses))
            if {6, 8, 12} & s12:
                add(f"🏥 12th CSL {sub12} signifies houses {sorted({6,8,12}&s12)} → hospitalization/confinement risk elevated.")
            elif {1, 5, 11} & s12:
                add(f"✅ 12th CSL {sub12} signifies houses {sorted({1,5,11}&s12)} → hospitalization tendency low.")
    except Exception:
        pass

    # ---------------------------
    # 3. Cure vs non-cure (5th + 11th)
    # ---------------------------
    try:
        if sub5 and sub11:
            s5 = get_signified_houses(sub5, houses)
            s11 = get_signified_houses(sub11, houses)
            if set(s5) & set(s11):
                add("🌱 Cure indicated: 5th & 11th sub-lords share significations (support for recovery).")
            else:
                add("⚠️ Cure uncertain: 5th & 11th sub-lords do not align.")
        else:
            if not sub5:
                add("ℹ️ 5th cusp sub-lord missing — recovery inference limited.")
            if not sub11:
                add("ℹ️ 11th cusp sub-lord missing — recovery inference limited.")
    except Exception:
        pass

    # ---------------------------
    # 4. Additional universal checks (planet placements, retrograde, aspects)
    # ---------------------------
    try:
        # If major planets occupy 6/8/12, report
        for name in ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"):
            p = get_planet(name, planets)
            if p and p.get("house") in {6,8,12}:
                add(f"⚠️ {name} in {p.get('house')} → {name}-related tendency in disease area.")

        # Mercury specifics (already important)
        merc = get_planet("Mercury", planets)
        if merc:
            msign = (merc.get("zodiac") or merc.get("pseudo_rasi") or "").title()
            # Mercury in Leo -> neuro-circulatory / heart sensitivity
            if msign == "Leo":
                add("❤️ Mercury in Leo → neuro-circulatory / heart-related sensitivity (classical note).")
            # Saturn aspecting Mercury -> chronic nervous/respiratory tendencies
            if _aspected_by(merc, "Saturn"):
                add("⚠️ Saturn aspects Mercury → chronic nervous/respiratory disease tendency.")
    except Exception:
        pass

    # ---------------------------
    # 5. Summary / fallback
    # ---------------------------
    if not out:
        add("✅ No strong classical health indicators found (per included universal rules).")

    return out

def evaluate_eye_risks(planets, houses):
    """
    Unified KP + Classical eye/vision risk evaluator (complete merge).
    Returns list[str] deduped messages.
    Relies on existing helpers in your codebase:
        get_planet, _p, _conjoined, _aspected_by, _lord_of, normalize_planet,
        _count_planets_in_house, get_cusp_sub_lord, get_star_lord_of_planet,
        get_signified_houses, _in_house, _in_houses
    """
    out, seen = [], set()
    def add(msg):
        if not msg: 
            return
        if msg not in seen:
            out.append(msg); seen.add(msg)

    # safe getters
    def house_of(name):
        p = get_planet(name, planets)
        return p.get("house") if p else None
    def in_house(pl_name, h):
        p = get_planet(pl_name, planets)
        return bool(p and p.get("house") == h)
    def in_houses(pl_name, hs):
        p = get_planet(pl_name, planets)
        return bool(p and p.get("house") in set(hs))
    def planet_obj(name):
        return _p(planets, name)

    # canonical planet objects
    Sun = get_planet("Sun", planets)
    Moon = get_planet("Moon", planets)
    Venus = get_planet("Venus", planets)
    Mars = get_planet("Mars", planets)
    Saturn = get_planet("Saturn", planets)
    Jupiter = get_planet("Jupiter", planets)
    Mercury = get_planet("Mercury", planets)
    Rahu = get_planet("Rahu", planets)
    Ketu = get_planet("Ketu", planets)

    # small helpers
    def is_malefic_name(n):
        return normalize_planet(n) in {"Saturn","Mars","Rahu","Ketu"}
    def aspected_by_malefic(pl):
        if not pl: return False
        for m in ("Saturn","Mars","Rahu","Ketu"):
            try:
                if _aspected_by(pl, m): return True
            except Exception:
                pass
        return False

    # --------------------
    # KP core: 2nd = right eye, 12th = left eye
    # Also 12th-cusp-sub-lord defect activation and Ketu-star planets
    # --------------------
    try:
        sl2  = get_cusp_sub_lord(2, houses)
        sl12 = get_cusp_sub_lord(12, houses)
        sl2_star  = get_star_lord_of_planet(sl2)
        sl12_star = get_star_lord_of_planet(sl12)
        signi2  = get_signified_houses(sl2_star, houses) if sl2_star else set()
        signi12 = get_signified_houses(sl12_star, houses) if sl12_star else set()
    except Exception:
        signi2, signi12 = set(), set()

    # Right eye (2)
    if 6 in signi2:
        add("⚠️ 2nd cusp SL star signifies 6 → right-eye disease tendency.")
    if 8 in signi2:
        add("⚠️ 2nd cusp SL star signifies 8 → danger/accident risk to right eye.")
    if 12 in signi2:
        add("⚠️ 2nd cusp SL star signifies 12 → hospitalization risk linked to right-eye.")

    # Left eye (12)
    left_defect_active = bool(set(signi12) & {6,8,12})
    if left_defect_active:
        add("⚠️ 12th cusp SL star signifies 6/8/12 → left-eye defect/hospitalization mechanism active.")

    # Planets in Ketu star -> defect (only meaningful if 12th mechanism active)
    ketu_star_planets = []
    for p in planets.values():
        if isinstance(p, dict) and (p.get("pseudo_nakshatra_lord") == "Ketu" or p.get("nakshatra_lord") == "Ketu"):
            ketu_star_planets.append(p)
    eye_significators = {"Sun","Moon","Mercury","Venus"}
    for p in ketu_star_planets:
        pname = normalize_planet(p.get("name"))
        if pname in eye_significators and left_defect_active:
            add(f"⚠️ {pname} in Ketu star + 12th-cusp defect active → congenital/serious eye defect likely.")
        else:
            add(f"⚠️ {pname} in Ketu star → defect possible in organ signified by {pname} (KP rule).")

    # --------------------
    # CLASSICAL 23 RULES (explicit)
    # Rules reflect the numbered classical list from your screenshots
    # Each rule adds a short human-readable indicator
    # --------------------

    # Rule 1:
    # If lord of Lagna is conjoined with Sun and Venus AND they occupy any of 6/8/12 -> congenital eye risk
    try:
        lagna_lord = _lord_of(1, houses)
        lagna_obj = _p(planets, lagna_lord) if lagna_lord else None
        if lagna_obj and _conjoined(lagna_obj, _p(planets, "Sun")) and _conjoined(lagna_obj, _p(planets, "Venus")):
            h = lagna_obj.get("house")
            if h in {6,8,12}:
                add("⚠️ (Rule1) Lagna-lord conjoined with Sun & Venus in 6/8/12 → congenital eye-weakness risk.")
    except Exception:
        pass

    # Rule 2:
    # Saturn & Mars in 5 or 9 and Rahu in Lagna -> birth blindness risk
    try:
        if in_houses("Saturn", {5,9}) and in_houses("Mars", {5,9}) and in_house("Rahu",1):
            add("⚠️ (Rule2) Saturn+Mars in 5/9 with Rahu in Lagna → congenital vision risk.")
    except Exception:
        pass

    # Rule 3:
    # Lords of 1 and 2 in 6 or 8 or 12 AND Sun+Venus conjoined -> born blind
    try:
        l1 = _lord_of(1, houses); l2 = _lord_of(2, houses)
        if l1 and l2:
            p1=_p(planets,l1); p2=_p(planets,l2)
            if (p1 and p1.get("house") in {6,8,12}) and (p2 and p2.get("house") in {6,8,12}):
                if _conjoined(_p(planets,"Sun"), _p(planets,"Venus")):
                    add("⚠️ (Rule3) Lords of 1 & 2 in 6/8/12 with Sun+Venus conj → congenital blindness indicator.")
    except Exception:
        pass

    # Rule 4:
    # Moon + Mars in 6/8/12 (Chandramangala) -> blindness by fall/injury
    try:
        if _conjoined(_p(planets,"Moon"), _p(planets,"Mars")):
            mh = house_of("Moon")
            if mh in {6,8,12}:
                add("⚠️ (Rule4) Moon+Mars conjunct in 6/8/12 → eye-injury / accident blindness risk.")
    except Exception:
        pass

    # Rule 5:
    # Moon + Jupiter in 6/8/12 -> blindness due to sexual/excess
    try:
        if _conjoined(_p(planets,"Moon"), _p(planets,"Jupiter")):
            mh = house_of("Moon")
            if mh in {6,8,12}:
                add("⚠️ (Rule5) Moon+Jupiter in 6/8/12 → vision risk from excesses (classical).")
    except Exception:
        pass

    # Rule 6:
    # Sun & Moon conjoined in 1,3,4,7,10 -> spectacles needed
    try:
        if _conjoined(_p(planets,"Sun"), _p(planets,"Moon")):
            sh = house_of("Sun")
            if sh in {1,3,4,7,10}:
                add("⚠️ (Rule6) Sun+Moon conj in 1/3/4/7/10 → tendency to need spectacles / weak vision.")
    except Exception:
        pass

    # Rule 7:
    # Mars occupies sign of an evil planet that is the 1/4/7/10 house -> blindness indicator
    try:
        m_house = house_of("Mars")
        if m_house in {1,4,7,10}:
            cusp = next((h for h in houses if h.get("house")==m_house), None)
            if cusp:
                sign = cusp.get("start_rasi") or cusp.get("rasi")
                sign_lord = SIGN_LORDS.get(str(sign).title()) if sign else None
                if sign_lord and is_malefic_name(sign_lord):
                    add("⚠️ (Rule7) Mars occupies sign ruled by malefic on 1/4/7/10 → classical eye-trouble indicator.")
    except Exception:
        pass

    # Rule 8:
    # Born in Cancer or Leo and Sun in 7 -> eye defect
    try:
        lagna = next((h for h in houses if h.get("house")==1), {})
        lagna_sign = (lagna.get("start_rasi") or lagna.get("rasi") or "").title()
        if lagna_sign in {"Cancer","Leo"} and in_house("Sun",7):
            add("⚠️ (Rule8) Lagna Cancer/Leo + Sun in 7 → classical eye defect indicator.")
    except Exception:
        pass

    # Rule 9:
    # Lords of 1,2,12 conjoin Venus and all in 6/8/12 -> eye disease
    try:
        l1 = _lord_of(1,houses); l2 = _lord_of(2,houses); l12 = _lord_of(12,houses)
        if l1 and l2 and l12:
            pl1=_p(planets,l1); pl2=_p(planets,l2); pl12=_p(planets,l12)
            if pl1 and pl1.get("house") in {6,8,12} and _conjoined(pl1, _p(planets,"Venus")):
                add("⚠️ (Rule9) Lords of 1,2,12 conjoined with Venus in 6/8/12 → eye disease indicator.")
    except Exception:
        pass

    # Rule 10:
    # Malefic in 2 conjoined with Venus+Moon -> blind
    try:
        if any(in_house(m,2) for m in ("Saturn","Mars","Rahu","Ketu")):
            if _conjoined(_p(planets,"Venus"), _p(planets,"Moon")) and house_of("Venus")==2:
                add("⚠️ (Rule10) Malefic in 2 conjoined with Venus+Moon -> elevated blindness risk.")
    except Exception:
        pass

    # Rule 11:
    # Malefics in 4 and/or 5 -> blindness risk (classical text)
    try:
        if any(in_house(m,4) for m in ("Saturn","Mars","Rahu","Ketu")) or any(in_house(m,5) for m in ("Saturn","Mars","Rahu","Ketu")):
            add("⚠️ (Rule11) Malefics in 4 or 5 → classical eye-problem risk.")
    except Exception:
        pass

    # Rule 12:
    # Moon in 6 or 8 or 12 receiving aspect from malefic -> blindness
    try:
        if in_houses("Moon", {6,8,12}) and aspected_by_malefic(_p(planets,"Moon")):
            add("⚠️ (Rule12) Moon in 6/8/12 aspected by malefic → blindness risk.")
    except Exception:
        pass

    # Rule 13:
    # Sun and Moon in 12 not aspected by benefics -> loss of vision
    try:
        if in_house("Sun",12) and in_house("Moon",12):
            benef_present = False
            for b in ("Jupiter","Venus","Mercury","Moon"):
                if _aspected_by(_p(planets,"Sun"), b) or _aspected_by(_p(planets,"Moon"), b):
                    benef_present = True; break
            if not benef_present:
                add("⚠️ (Rule13) Sun+Moon in 12 without benefic aspect → classical risk of vision loss.")
    except Exception:
        pass

    # Rule 14:
    # If one born in Leo Lagna and Saturn or Venus occupy Lagna -> blindness
    try:
        if lagna.get("start_rasi","").title() == "Leo":
            if in_house("Saturn",1) or in_house("Venus",1):
                add("⚠️ (Rule14) Leo Lagna with Saturn or Venus in Lagna → blindness risk (classical).")
    except Exception:
        pass

    # Rule 15:
    # Saturn in 12, Moon in 2, Sun in 8 causes loss of vision
    try:
        if in_house("Saturn",12) and in_house("Moon",2) and in_house("Sun",8):
            add("⚠️ (Rule15) Saturn(12)+Moon(2)+Sun(8) → classical vision-loss pattern.")
    except Exception:
        pass

    # Rule 16:
    # Moon in 6, Sun in 8, Mars in 12, Saturn in 2 -> deprives eyesight
    try:
        if in_house("Moon",6) and in_house("Sun",8) and in_house("Mars",12) and in_house("Saturn",2):
            add("⚠️ (Rule16) Moon(6)+Sun(8)+Mars(12)+Saturn(2) → severe eyesight deprivation pattern.")
    except Exception:
        pass

    # Rule 17:
    # Saturn in 4 receiving malefic aspect -> loss of sight
    try:
        if in_house("Saturn",4) and aspected_by_malefic(_p(planets,"Saturn")):
            add("⚠️ (Rule17) Saturn in 4 with malefic aspect → vision impairment risk.")
    except Exception:
        pass

    # Rule 18:
    # Rahu in 5 to Venus or Lagna and aspected by Sun -> makes one blind
    try:
        if in_house("Rahu",5):
            if _aspected_by(_p(planets,"Rahu"), "Sun") or _conjoined(_p(planets,"Rahu"), _p(planets,"Venus")):
                add("⚠️ (Rule18) Rahu(5) with Sun aspect or Rahu-Venus link → blindness warning.")
    except Exception:
        pass

    # Rule 19:
    # Moon & Venus in 6/8/12 -> night blindness
    try:
        if in_houses("Moon",{6,8,12}) and in_houses("Venus",{6,8,12}):
            add("⚠️ (Rule19) Moon+Venus in 6/8/12 → night blindness classical indicator.")
    except Exception:
        pass

    # Rule 20:
    # Moon, Venus and lord of 2 in Lagna -> night blindness
    try:
        lord2 = _lord_of(2,houses)
        if lord2 and _p(planets,lord2) and _p(planets,lord2).get("house")==1 and _conjoined(_p(planets,"Moon"), _p(planets,"Venus")):
            add("⚠️ (Rule20) Moon+Venus with lord of 2 in Lagna → night blindness indicator.")
    except Exception:
        pass

    # Rule 21:
    # Lords of 1 and 2 in 6/8/12 -> loss of eyes
    try:
        l1 = _lord_of(1,houses); l2 = _lord_of(2,houses)
        if l1 and l2 and _p(planets,l1) and _p(planets,l2):
            if _p(planets,l1).get("house") in {6,8,12} and _p(planets,l2).get("house") in {6,8,12}:
                add("⚠️ (Rule21) Lords of 1 & 2 both in 6/8/12 → classical indicator for loss of eyesight.")
    except Exception:
        pass

    # Rule 22:
    # Mars in 12 affects left eye; Saturn in 2 affects right eye
    try:
        if in_house("Mars",12):
            add("⚠️ (Rule22) Mars in 12 → classical association with left-eye vulnerability.")
        if in_house("Saturn",2):
            add("⚠️ (Rule22) Saturn in 2 → classical association with right-eye vulnerability.")
    except Exception:
        pass

    # Rule 23:
    # Lagna occupied by lords of 2,6,10 with Venus -> eye loss (historical/archaic)
    try:
        l2 = _lord_of(2,houses); l6 = _lord_of(6,houses); l10 = _lord_of(10,houses)
        occ_names = set(normalize_planet(p.get("name")) for p in planets.values() if isinstance(p, dict) and p.get("house")==1)
        needed = {normalize_planet(l2 or ""), normalize_planet(l6 or ""), normalize_planet(l10 or "")}
        if "Venus" in occ_names and needed.issubset(occ_names):
            add("⚠️ (Rule23) Lagna occupied by lords of 2,6,10 together with Venus → classical eye-loss (archaic).")
    except Exception:
        pass

    # --------------------
    # Additional KP/classical checks (afflictions, aspects, sign-mapping)
    # --------------------
    try:
        # Sun/Moon/Venus/Mercury placements in 6/8/12
        for name in ("Sun","Moon","Mercury","Venus"):
            p = get_planet(name, planets)
            if p and p.get("house") in {6,8,12}:
                add(f"⚠️ {name} in 6/8/12 → {name}-related ocular weakness or infections possible.")

        # Mercury afflicted -> squint / myopia
        if _has_evil_aspect(_p(planets,"Mercury")) or _aspected_by(_p(planets,"Mercury"), "Mars"):
            add("⚠️ Mercury afflicted (by Mars/Rahu/Saturn) → squint, myopia or nerve-related vision issues.")

        # Benefic protection: Jupiter/Venus in benefic houses reduce severity
        for b in ("Jupiter","Venus"):
            pb = _p(planets, b)
            if pb and pb.get("house") in {1,5,9,11}:
                add(f"🟢 {b} well placed → protective effect on eyesight.")

        # Sign-based short hints for core planets (helpful summary)
        sign_hints = {
            'Aries': "head/brain → headaches affecting vision",
            'Taurus': "throat/eyes → eye infections / palate-related eye issues",
            'Gemini': "nervous system → focus/coordination problems",
            'Cancer': "fluid imbalance → watery eyes/swelling",
            'Leo': "retinal/circulatory → retinal weakness, eye palpitations",
            'Virgo': "digestive/vitamin → dryness or nutritional eye issues",
            'Libra': "kidney/bright's → eye brightness/urine-linked issues",
            'Scorpio': "reproductive/urogenital links → menstrual eye disturbances",
            'Sagittarius': "blood/hips → optic pressure issues",
            'Capricorn': "skin/bones → eyelid/chronic strain",
            'Aquarius': "nervous twitches → irregular vision",
            'Pisces': "fluid/feet → infections/edema near eyes"
        }
        for name in ("Sun","Moon","Mercury","Venus"):
            p = get_planet(name, planets)
            if p:
                z = (p.get("zodiac") or p.get("pseudo_rasi") or "").title()
                if z and z in sign_hints:
                    add(f"🔍 {name} in {z}: {sign_hints[z]}")
    except Exception:
        pass

    if not out:
        add("✅ No strong classical/KP eye-risk patterns detected (per included rules).")

    return out


def evaluate_speech(planets, houses):
    """
    Universal KP Speech & Voice Evaluator
    -------------------------------------
    Uses ONLY classical, universal KP rules:
    - 2nd cusp sub-lord determines speech quality
    - Rahu/Ketu in 2nd → speech defect
    - Saturn/Mars/Rahu/Ketu afflicting Mercury → speech/nerve issues
    - Taurus + Mercury affliction → throat/voice issues
    - No example-based rules. Clean, universal, reproducible.

    Returns:
        list[str] -> deduped human-readable indicators
    """

    out, seen = [], set()

    def add(msg):
        if msg and msg not in seen:
            out.append(msg); seen.add(msg)

    # -------------------------------
    # Helpers
    # -------------------------------
    def G(name): return get_planet(name, planets)
    def house_of(name):
        p = G(name)
        return p.get("house") if p else None
    def sl(h): return get_cusp_sub_lord(h, houses)

    # -------------------------------
    # 1. 2nd CUSP SUB-LORD → Speech Style
    # -------------------------------
    sl2 = sl(2)

    if not sl2:
        add("❓ 2nd cusp sub-lord missing — speech inference limited.")
    else:
        p = sl2  # normalized planet name
        if p == "Mercury":
            add("🗣️ Speech: quick, analytical, talkative (Mercury as 2nd cusp sub-lord).")
        elif p == "Mars":
            add("🗣️ Speech: sharp, blunt, forceful (Mars as 2nd cusp sub-lord).")
        elif p == "Saturn":
            add("🗣️ Speech: slow, heavy, delayed (Saturn as 2nd cusp sub-lord).")
        elif p == "Jupiter":
            add("🗣️ Speech: wise, reflective, advisory (Jupiter as 2nd cusp sub-lord).")
        elif p == "Venus":
            add("🗣️ Speech: sweet, musical, pleasant (Venus as 2nd cusp sub-lord).")
        elif p in ("Rahu", "Ketu"):
            add("⚠️ Speech defect possible — Rahu/Ketu as 2nd cusp sub-lord.")

    # -------------------------------
    # 2. Rahu/Ketu in 2nd → Speech Defect
    # -------------------------------
    if house_of("Rahu") == 2:
        add("⚠️ Rahu in 2nd → stammering / mispronunciation / sudden breaks in speech.")

    if house_of("Ketu") == 2:
        add("⚠️ Ketu in 2nd → speech blockage / unclear articulation / missing words.")

    # -------------------------------
    # 3. Mercury Afflicted → Nervous / Speech Impairment
    # -------------------------------
    merc = G("Mercury")

    if merc:
        afflicted = False
        for mal in ("Saturn","Mars","Rahu","Ketu"):
            if _aspected_by(merc, mal):
                afflicted = True

        if afflicted:
            add("⚠️ Mercury afflicted → speech coordination issues / stammering / nervous speech.")

    # -------------------------------
    # 4. Taurus Sign Affliction → Voice / Throat Issues
    # Taurus = throat + vocal cords; Mercury = vocal coordination
    # -------------------------------
    taurus_afflicted = False

    for p in planets.values():
        if isinstance(p, dict) and (p.get("zodiac") or "").title() == "Taurus":
            if normalize_planet(p.get("name")) in {"Saturn","Mars","Rahu","Ketu"}:
                taurus_afflicted = True

    if taurus_afflicted and merc:
        add("⚠️ Taurus afflicted with Mercury present → voice fatigue, hoarseness, throat sensitivity.")

    # -------------------------------
    # 5. Speech still normal?
    # -------------------------------
    if not out:
        add("✅ No major KP speech or voice issues indicated.")

    return out


def generate_full_health_report(planets, houses):
    """
    Unified Full Health Report (KP Classical)
    Now adds FULL ORGAN SIGNIFICATION TABLE at the end.
    """

    # --- Run all evaluators ---
    health_list = evaluate_health(planets, houses)
    eye_list    = evaluate_eye_risks(planets, houses)
    speech_list = evaluate_speech(planets, houses)

    # --- Planet → Organ Mapping (Full Table) ---
    organ_map = {
        'Sun': "☀️ Heart, eyes, vitality",
        'Moon': "🌙 Stomach, fluids, mind, left eye",
        'Mercury': "🧠 Nerves, lungs, skin, speech coordination",
        'Venus': "♀️ Kidneys, throat, reproductive organs",
        'Mars': "🔪 Blood, accidents, surgery, infections",
        'Jupiter': "⚖️ Liver, metabolism, diabetes tendencies",
        'Saturn': "🪐 Bones, chronic disease, degeneration",
        'Rahu': "☸️ Mysterious/atypical illnesses",
        'Ketu': "☸️ Hidden, karmic, nerve degeneration",
        'Ascendant': "🧍 Overall body constitution"
    }

    # --- Report accumulator ---
    report = []
    add = report.append

    # HEADER
    add("==========================================")
    add("🩺 FULL KP HEALTH REPORT")
    add("==========================================")
    add("")

    # -----------------------------
    # 1. GENERAL HEALTH
    # -----------------------------
    add("🔶 **GENERAL HEALTH ANALYSIS (KP Classical)**")
    if not health_list:
        add("• No major classical health indicators found.")
    else:
        for p in health_list:
            add(f"• {p}")
    add("")

    # -----------------------------
    # 2. EYE / VISION ANALYSIS
    # -----------------------------
    add("🔷 **EYE / VISION ANALYSIS**")
    if not eye_list:
        add("• No specific KP eye-risk rules triggered.")
    else:
        for p in eye_list:
            add(f"• {p}")
    add("")

    # -----------------------------
    # 3. SPEECH / VOICE ANALYSIS
    # -----------------------------
    add("🗣️ **SPEECH & VOICE ANALYSIS**")
    if not speech_list:
        add("• No speech issues indicated.")
    else:
        for p in speech_list:
            add(f"• {p}")
    add("")

    # -----------------------------
    # 4. SUMMARY
    # -----------------------------
    add("==========================================")
    add("📌 **SUMMARY**")
    add("==========================================")
    add("")

    # Health summary
    if any("⚠️" in p or "☠️" in p for p in health_list):
        add("• Health: **Some risk indicators present (6/8/12 involvement)**")
    else:
        add("• Health: **No strong disease indicators**")

    # Eye summary
    if any("⚠️" in p for p in eye_list):
        add("• Eyes: **Vision/eye-risk patterns detected**")
    else:
        add("• Eyes: **No strong eye risks**")

    # Speech summary
    if any("⚠️" in p for p in speech_list):
        add("• Speech: **Speech/voice issues present**")
    else:
        add("• Speech: **Normal speech indicators**")

    add("")

    # -----------------------------
    # 5. ORGAN SIGNIFICATION TABLE
    # -----------------------------
    add("==========================================")
    add("🧬 **PLANET → ORGAN SIGNIFICATIONS**")
    add("==========================================")
    add("")

    for planet, organs in organ_map.items():
        add(f"{planet} → {organs}")

    add("")

    return report
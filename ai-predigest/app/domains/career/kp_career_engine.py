from app.core.astro_constants import (
    normalize_planet,
    normalize_planet_name,
    get_planet,
    _p,

    _lord_of,
    get_house_of,

    get_signified_houses,
    get_signified_score,

    detect_aspects,

    _is_benefic,
    _is_malefic,
    _is_retrograde,
    _is_own_sign,
    _is_exalted,
    _is_debilitated,
    _is_strong_planet,

    BENEFICS,
    MALEFICS,
    KP_PROFESSION_MAP
)

def evaluate_service_profession(planets, houses, KP_PROFESSION_MAP):
    """
    Enhanced KP Service Profession Evaluation
    -----------------------------------------
    Logic unchanged.
    Adds explicit KP CSL + house-signification reasoning.
    """

    # --- 1) 10th Cusp Chain ---
    c10 = next((h for h in houses if h.get("house") == 10), None)
    if not c10:
        return {"error": "10th cusp not found."}

    sign_lord = _lord_of(10, houses)
    sign_lord_p = _p(planets, sign_lord)

    star_lord = normalize_planet(sign_lord_p.get("nakshatra_lord")) if sign_lord_p else None
    star_lord_p = _p(planets, star_lord)

    sub_lord = normalize_planet(star_lord_p.get("sub_lord")) if star_lord_p else None

    chain = [p for p in [sign_lord, star_lord, sub_lord] if p]

    # --- 2) Frequency Match Against Database ---
    match_strength = {
        profession: sum(
            1 for p in chain
            if normalize_planet(p) in [normalize_planet(x) for x in req]
        )
        for profession, req in KP_PROFESSION_MAP.items()
    }

    match_strength = {k: v for k, v in match_strength.items() if v > 0}

    if not match_strength:
        return {
            "planet_chain": chain,
            "message": "10th cusp CSL active, but no profession mapping matched."
        }

    # --- 3) KP Context Validation via Sub-Lord ---
    sc = get_signified_score(sub_lord, planets, houses)

    context = []
    context_reasoning = []

    if sc.get(6, 0) > 1:
        context.append("Service / Administration")
        context_reasoning.append("6th house strongly signified → job, duty, service.")

    if sc.get(2, 0) > 1:
        context.append("Finance / Accounts / Banking")
        context_reasoning.append("2nd house signified → income, finance handling.")

    if sc.get(3, 0) > 1:
        context.append("Communication / IT / Sales")
        context_reasoning.append("3rd house signified → communication, skills, IT, sales.")

    if sc.get(11, 0) > 1:
        context.append("Corporate / Stable Salary")
        context_reasoning.append("11th house signified → gains, steady income, organizations.")

    if sc.get(12, 0) > 1:
        context.append("Hospital / Foreign / Isolation")
        context_reasoning.append("12th house signified → hospitals, foreign, remote work.")

    if sc.get(5, 0) > 1:
        context.append("Education / Research")
        context_reasoning.append("5th house signified → education, analysis, research.")

    # --- 4) Planets Occupying 10th House ---
    modifying_planets = [
        normalize_planet(p)
        for p, d in planets.items()
        if str(d.get("house")) == "10"
    ]

    # --- 5) Weighted Ranking (unchanged) ---
    ranked = []
    for profession, hits in match_strength.items():
        score = hits * 2
        name = profession.lower()

        if "finance" in " ".join(context) and ("account" in name or "bank" in name):
            score += 3

        if "communication" in " ".join(context) and ("media" in name or "sales" in name):
            score += 2

        if "education" in " ".join(context) and ("research" in name or "teacher" in name):
            score += 2

        if "hospital" in " ".join(context) and ("nurse" in name or "medical" in name):
            score += 2

        ranked.append((profession, score))

    ranked = sorted(ranked, key=lambda x: x[1], reverse=True)
    top_professions = [p.replace("_", " ").title() for p, _ in ranked[:5]]

    # --- 6) Govt / Private / Foreign Tags ---
    tags = []
    gov_score = 0

    if "Saturn" in chain or "Sun" in chain:
        gov_score += 1

    if sc.get(6, 0) or sc.get(10, 0):
        gov_score += 1

    tags.append(
        "Government Job"
        if gov_score >= 2
        else "Private Sector Role"
    )

    foreign_score = 0
    if sc.get(3, 0) or sc.get(9, 0) or sc.get(12, 0):
        foreign_score += 1

    if "Rahu" in chain or "Rahu" in modifying_planets:
        foreign_score += 1

    if foreign_score >= 2:
        tags.append("Foreign / Multinational Exposure")
    elif foreign_score == 1:
        tags.append("Transferable Role")
    else:
        tags.append("Stable Local Job")

    # --- 7) Confidence ---
    max_hits = max(match_strength.values())
    confidence = (
        "High" if max_hits >= 3
        else "Moderate" if max_hits == 2
        else "Low"
    )

    return {
        "mode": "Service (KP 10th CSL Based)",
        "confidence": confidence,
        "planet_chain": chain,
        "csl_reasoning": (
            f"10th cusp sign lord → star lord → sub lord chain {chain}. "
            f"Sub-lord significations decide job nature as per KP."
        ),
        "career_category": context[0] if context else "General Service",
        "career_direction": top_professions[0],
        "final_professions": top_professions,
        "context_explanation": context_reasoning,
        "context_tags": tags,
        "modifying_planets": modifying_planets,
        "reasoning": (
            "Profession ranked using KP CSL chain, "
            "house significations, and profession-planet mapping."
        )
    }

def evaluate_business_profession(planets, houses, KP_BUSINESS_MAP=None):
    """
    Determines business suitability, type, environment and confidence
    using KP rules (Vol 2, Vol 3 Business Chapter).
    CSL (Cusp–Sub–Lord) logic reflected in explanations only.
    """

    BUSINESS_HOUSES = {3, 5, 7, 9, 11}
    SUCCESS_NAK_HOUSES = {2, 10, 11}
    NEGATIVE_HOUSES = {8, 12}

    dual_signs = {"Gemini", "Virgo", "Sagittarius", "Pisces"}

    score = 0
    style_tags = []
    analysis_log = []
    industry_bias = []
    partners_needed = False

    # ---- RULE 1: Direct House Support (3,5,7,9,11)
    for planet, data in planets.items():
        h = data.get("house")

        if h in BUSINESS_HOUSES:
            score += 5
            analysis_log.append(
                f"{planet} signifies house {h} → active business house as per KP; "
                f"supports self-initiative, trade, expansion or gains."
            )
            industry_bias.append(planet)

        # ---- RULE 2: Nakshatra Influence (Star Lord Result)
        nak_lord = data.get("nakshatra_lord")
        nak_house = get_house_of(planets, nak_lord) if nak_lord else None

        if nak_house in SUCCESS_NAK_HOUSES:
            score += 4
            analysis_log.append(
                f"{planet} placed in star of {nak_lord}, which signifies house {nak_house} → "
                f"CSL indicates business success, earnings or professional rise."
            )

        elif nak_house in NEGATIVE_HOUSES:
            score -= 4
            analysis_log.append(
                f"{planet} placed in star of {nak_lord}, signifying house {nak_house} → "
                f"KP loss houses involved; business obstacles or instability possible."
            )

    # ---- RULE 3: 7th House Defines Business Style (Business Axis)
    for planet, data in planets.items():
        if data.get("house") == 7:
            partners_needed = True
            score += 6

            business_type_map = {
                "Sun": "Authority-driven or government-linked business.",
                "Moon": "Fluctuating business; public-dependent demand.",
                "Mars": "Risk-oriented business, land, construction, fast execution.",
                "Mercury": "Trade, brokerage, agency, communication-based business.",
                "Jupiter": "Ethical, advisory or long-term growth-oriented business.",
                "Venus": "Luxury, branding, beauty, customer-facing business.",
                "Saturn": "Delayed results; business improves with structure/partnership.",
                "Rahu": "Foreign trade, unconventional or scalable business models.",
                "Ketu": "Independent, niche, technical or specialized business."
            }

            nature = business_type_map.get(planet, "Unpredictable business role.")
            style_tags.append(f"{planet} in 7th → {nature}")
            analysis_log.append(
                f"{planet} occupying 7th house → classic KP business indicator; "
                f"defines business style and partnership dynamics."
            )

            if planet == "Saturn":
                score -= 6
                analysis_log.append(
                    "Saturn in 7th → delay and pressure in independent business; "
                    "KP suggests partnership or patience is mandatory."
                )

    # ---- RULE 4: Multi–Income / Trade Signature
    mercury_dual = "Mercury" in planets and planets["Mercury"].get("sign") in dual_signs
    saturn_star = any(data.get("nakshatra_lord") == "Saturn" for data in planets.values())

    if mercury_dual and saturn_star:
        score += 8
        style_tags.append("Multiple income streams / agency / brokerage indicated.")
        analysis_log.append(
            "Mercury in dual sign + Saturn star influence → "
            "KP signature for trading, commission, agency or repeat income models."
        )

    # ---- RULE 5: Rahu/Ketu = Expansion Logic (Node Sub-Lord Rule)
    foreign_trade = False

    for node in ["Rahu", "Ketu"]:
        if node in planets:
            sub_lord = planets[node].get("sub_lord")

            if sub_lord in ["Mercury", "Venus", "Jupiter"]:
                score += 5
                analysis_log.append(
                    f"{node} operates under sub-lord {sub_lord} → "
                    f"node behaves benefically; enhances business reach as per KP."
                )

            if planets[node].get("house") in {9, 12}:
                foreign_trade = True
                analysis_log.append(
                    f"{node} connected to house {planets[node].get('house')} → "
                    "foreign trade / overseas business linkage indicated."
                )

    # ---- RULE 6: Final KP Classification
    if score >= 22:
        strength = (
            "Strong Business Yog as per KP – "
            "CSL supports self-enterprise and independent growth."
        )
        confidence = "High"

    elif score >= 12:
        strength = (
            "Moderate Business Yog – "
            "Business possible with correct dasha timing and structured approach."
        )
        confidence = "Moderate"

    else:
        strength = (
            "Weak Business Yog – "
            "KP indicates service/job path is safer than independent business."
        )
        confidence = "Low"

    # ---- SECTOR GUESSING (unchanged)
    PLANET_SECTOR_MAP = {
        "Mars": "Real estate | Machinery | Construction | Metals",
        "Mercury": "Trading | Sales | Communication | Brokerage",
        "Venus": "Fashion | Luxury | Hospitality | Cosmetics",
        "Jupiter": "Education | Finance | Consultation | Law",
        "Moon": "Food | Liquids | Health | Public services",
        "Sun": "Government linked trade | Leadership based",
        "Saturn": "Manufacturing | Labour | Industrial contracts",
        "Rahu": "Foreign trade | Tech | Unconventional sectors",
        "Ketu": "Spiritual/Tech niche consulting"
    }

    sectors = list({PLANET_SECTOR_MAP.get(p) for p in industry_bias if PLANET_SECTOR_MAP.get(p)})
    sectors = sectors[:5] if sectors else ["General Trading / Self Employment"]

    return {
        "mode": "Business",
        "confidence": confidence,
        "score": score,
        "business_strength_summary": strength,
        "final_professions": sectors,
        "partners_needed": partners_needed,
        "foreign_link": "Yes" if foreign_trade else "No",
        "business_nature_tags": style_tags,
        "analysis": analysis_log
    }



def score_service_business(planets, houses):
    SERVICE = {2, 6, 10}
    BUSINESS = {3, 5, 7, 9, 11}

    WEIGHTS = {
        "occupant": 3,
        "star": 2,
        "sub": 1
    }

    service_score = 0
    business_score = 0

    for p, p_data in planets.items():

        # ---- HOUSE OCCUPATION --------------------------------
        h = p_data.get("house")
        if h in SERVICE: service_score += WEIGHTS["occupant"]
        if h in BUSINESS: business_score += WEIGHTS["occupant"]

        # ---- STAR LORD INFLUENCE ------------------------------
        star = normalize_planet(p_data.get("nakshatra_lord"))
        if star:
            star_house = get_house_of( planets,star)
            if star_house in SERVICE: service_score += WEIGHTS["star"]
            if star_house in BUSINESS: business_score += WEIGHTS["star"]

        # ---- SUB LORD INFLUENCE -------------------------------
        sub = normalize_planet(p_data.get("sub_lord"))
        if sub:
            sub_house = get_house_of(planets,sub)
            if sub_house in SERVICE: service_score += WEIGHTS["sub"]
            if sub_house in BUSINESS: business_score += WEIGHTS["sub"]

    return service_score, business_score


def determine_service_vs_business(planets, houses):
    """
    Final KP logic for deciding whether native is Service, Business or Mixed.
    Uses:
    - 10th cusp CSL logic for service
    - 7th cusp CSL logic for business
    - House clusters scoring for confirmation
    """

    # --- Helper to extract sublord of house cusp ---
    def get_cusp_sublord(house_no):
        cusp = next((h for h in houses if h["house"] == house_no), None)
        return normalize_planet(cusp.get("cusp_sub_lord")) if cusp else None

    # Get CSLs
    csl_10 = get_cusp_sublord(10)
    csl_7 = get_cusp_sublord(7)

    # Base scores
    service_score = 0
    business_score = 0

    # Weights
    W = {"lord": 4, "star": 3, "sub": 2, "occupy": 3}

    # House clusters
    SERVICE_H = {2, 6, 10, 11}
    BUSINESS_H = {3, 5, 7, 9, 11}

    # ---- Score 10th CSL for service ----
    c10_p = planets.get(csl_10, {})
    if c10_p.get("house") in SERVICE_H: service_score += W["occupy"]

    star_10 = normalize_planet(c10_p.get("nakshatra_lord"))
    if get_house_of(planets, star_10) in SERVICE_H: service_score += W["star"]

    sub_10 = normalize_planet(c10_p.get("sub_lord"))
    if get_house_of(planets, sub_10) in SERVICE_H: service_score += W["sub"]

    # ---- Score 7th CSL for business ----
    c7_p = planets.get(csl_7, {})
    if c7_p.get("house") in BUSINESS_H: business_score += W["occupy"]

    star_7 = normalize_planet(c7_p.get("nakshatra_lord"))
    if get_house_of(planets, star_7) in BUSINESS_H: business_score += W["star"]

    sub_7 = normalize_planet(c7_p.get("sub_lord"))
    if get_house_of(planets, sub_7) in BUSINESS_H: business_score += W["sub"]

    # ---- Node rule ----
    # Rahu/Ketu mimic their star-lord
    for node in ["Rahu", "Ketu"]:
        if node in planets:
            sl = normalize_planet(planets[node].get("nakshatra_lord"))
            house = get_house_of(planets, sl)
            if house in SERVICE_H: service_score += 2
            if house in BUSINESS_H: business_score += 2

    # ---- Interpretation Logic ----
    if abs(service_score - business_score) <= 3:
        final_decision = "Mixed"
    elif service_score > business_score:
        final_decision = "Service"
    else:
        final_decision = "Business"

    # ---- Business Shift Rule ----
    career_shift = False
    if final_decision == "Service" and get_house_of(planets, sub_10) in {7, 12}:
        career_shift = True

    return {
        "10th_CSL": csl_10,
        "7th_CSL": csl_7,
        "service_score": service_score,
        "business_score": business_score,
        "final_path": final_decision,
        "career_shift_likelihood": "Yes" if career_shift else "No"
    }

def evaluate_career(planets, houses, profession_map):
    """
    Unified Career Analysis Output (KP-Explainable, LLM-Safe)
    Logic unchanged.
    """

    mode = determine_service_vs_business(planets, houses)
    service_score, business_score = score_service_business(planets, houses)

    points = []
    points.append("🔹 **KP Career Evaluation Summary**")

    points.append(
        f"• 10th Cusp Sub-Lord → **{mode['10th_CSL']}** "
        "(decides job nature as per KP)"
    )

    points.append(
        f"• 7th Cusp Sub-Lord → **{mode['7th_CSL']}** "
        "(decides business tendency as per KP)"
    )

    points.append(
        f"• Final KP Verdict → **{mode['final_path']}** "
        "(based on CSL house significations)"
    )

    if mode["final_path"] == "Service":
        service_out = evaluate_service_profession(planets, houses, profession_map)

        points.append("• Dominant Path → **Service / Employment**")
        points.append(
            f"• KP Reason → 10th CSL connects more with 2-6-10-11 houses"
        )

        points.append(f"• Career Shift Possibility → **{mode['career_shift_likelihood']}**")

        points.append("• Most Suitable Roles:")
        for r in service_out.get("final_professions", []):
            points.append(f"   - {r}")

        points.append("• KP Context Explanation:")
        for r in service_out.get("context_explanation", []):
            points.append(f"   - {r}")

        points.append(f"• Work Environment → **{', '.join(service_out.get('context_tags', []))}**")
        points.append(f"• Confidence Level → **{service_out.get('confidence')}**")

    elif mode["final_path"] == "Business":
        business_out = evaluate_business_profession(planets, houses, profession_map)

        points.append("• Dominant Path → **Business / Self-Employment**")
        points.append(
            f"• KP Reason → 7th CSL connects more with 3-5-7-9-11 houses"
        )

        points.append("• Best Business Areas:")
        for s in business_out.get("final_professions", []):
            points.append(f"   - {s}")

        points.append(f"• Business Strength → **{business_out.get('business_strength_summary')}**")
        points.append(f"• Partnerships Required → **{business_out.get('partners_needed')}**")
        points.append(f"• Foreign Connection → **{business_out.get('foreign_link')}**")
        points.append(f"• Confidence Level → **{business_out.get('confidence')}**")

    else:
        service_out = evaluate_service_profession(planets, houses, profession_map)
        business_out = evaluate_business_profession(planets, houses, profession_map)

        points.append("• Dominant Path → **Hybrid (Job + Business)**")
        points.append(
            "• KP Reason → Both 10th and 7th CSL activate service & business houses"
        )

        merged = list(
            set(service_out.get("final_professions", []) +
                business_out.get("final_professions", []))
        )

        points.append("• Possible Hybrid Roles:")
        for r in merged[:6]:
            points.append(f"   - {r}")

        points.append(f"• Service Capability → **{service_out.get('confidence')}**")
        points.append(f"• Business Capability → **{business_out.get('confidence')}**")

    points.append("")
    points.append("📊 **KP Score Confirmation:**")
    points.append(f"   - Service Score → **{service_score}**")
    points.append(f"   - Business Score → **{business_score}**")

    return points

def evaluate_foreign_career_exposure(planets, houses, planet_chain=None):
    """
    KP-based Foreign / Multinational / Transferable Career Evaluation

    PURPOSE:
    - Detect foreign / multinational / transferable career exposure
    - KP-STYLE: CSL-driven, node-driven, house-signification logic
    - OUTPUT: Rich factual points usable directly by LLM prompts
    """

    indicators = []
    score = 0

    house_cusp_map = {h["house"]: h for h in houses}

    def add(point, text):
        nonlocal score
        score += point
        indicators.append(text)

    # -------------------------------
    # 1. NODE PLACEMENT (Primary KP)
    # -------------------------------
    for node in ["Rahu", "Ketu"]:
        if node not in planets:
            continue

        node_house = planets[node]["house"]

        if node_house in {9, 12}:
            add(
                2,
                f"{node} placed in {node_house}th house → acts as a foreign significator through KP node behavior, indicating overseas or multinational exposure"
            )
        elif node_house == 3:
            add(
                1,
                f"{node} placed in 3rd house → indicates travel, mobility, or transferable assignments connected to career"
            )

    # -------------------------------
    # 2. NODE STAR-LORD LINKAGE
    # -------------------------------
    for node in ["Rahu", "Ketu"]:
        if node not in planets:
            continue

        star_lord = planets[node].get("nakshatra_lord")
        if not star_lord or star_lord not in planets:
            continue

        star_house = planets[star_lord]["house"]

        if star_house in {9, 12}:
            add(
                1,
                f"{node} is in the star of {star_lord}, which is placed in {star_house}th house → node delivers results of foreign or long-distance career houses"
            )

    # -------------------------------
    # 3. PLANETS IN FOREIGN HOUSES
    # -------------------------------
    outer_planets = {"Uranus", "Neptune", "Pluto"}
    for planet_name, p_data in planets.items():
        if planet_name in outer_planets or planet_name == "Ascendant":
            continue

        h = p_data.get("house")

        if h == 12:
            add(
                1,
                f"{planet_name} placed in 12th house → signifies foreign environment, overseas work conditions, or separation from native base"
            )
        elif h == 9:
            add(
                1,
                f"{planet_name} placed in 9th house → supports long-distance travel, international exposure, or global professional links"
            )

    # -------------------------------
    # 4. 12th HOUSE CSL STRUCTURE (CORE KP)
    # -------------------------------
    h12 = house_cusp_map.get(12)
    if h12:
        sub_lord = h12.get("cusp_sub_lord")
        sub_sub_lord = h12.get("cusp_sub_sub_lord")

        if sub_lord and sub_lord in planets:
            lord_house = planets[sub_lord]["house"]
            if lord_house in {9, 10, 12}:
                add(
                    1,
                    f"12th house CSL ({sub_lord}) placed in {lord_house}th house → foreign matters operate through career, authority, or overseas domains"
                )

        if sub_sub_lord and sub_sub_lord in planets:
            lord_house = planets[sub_sub_lord]["house"]
            if lord_house in {9, 10, 12}:
                add(
                    1,
                    f"12th house sub-sub lord ({sub_sub_lord}) placed in {lord_house}th house → reinforces KP foreign career linkage at a deeper level"
                )

    # -------------------------------
    # 5. 9th HOUSE CSL STRUCTURE
    # -------------------------------
    h9 = house_cusp_map.get(9)
    if h9:
        sub_lord = h9.get("cusp_sub_lord")
        if sub_lord and sub_lord in planets:
            lord_house = planets[sub_lord]["house"]
            if lord_house in {3, 9, 12}:
                add(
                    1,
                    f"9th house CSL ({sub_lord}) placed in {lord_house}th house → long-distance travel connects directly to foreign or relocation themes"
                )

    # -------------------------------
    # 6. CAREER → FOREIGN BRIDGE
    # -------------------------------
    if "Mercury" in planets:
        if planets["Mercury"]["house"] in {9, 12}:
            add(
                1,
                "Mercury (career, communication, trade) placed in foreign-related house → supports transferable or multinational professional roles"
            )

    # -------------------------------
    # 7. 4th HOUSE CSL (HOME vs FOREIGN)
    # -------------------------------
    h4 = house_cusp_map.get(4)
    if h4:
        sub_lord = h4.get("cusp_sub_lord")

        if sub_lord in {"Moon", "Venus"}:
            add(
                -1,
                f"4th house CSL ({sub_lord}) emphasizes domestic comfort and home attachment → reduces long-term foreign career inclination"
            )
        elif sub_lord in {"Saturn", "Rahu"}:
            add(
                1,
                f"4th house CSL ({sub_lord}) indicates separation from homeland → supports relocation, transfers, or foreign residence for career"
            )

    # -------------------------------
    # 8. OPTIONAL: PLANET CHAIN SUPPORT
    # -------------------------------
    if planet_chain and "Rahu" in planet_chain:
        add(
            1,
            "Rahu involved in career planet chain → strengthens non-traditional, foreign, or multinational career pathways"
        )

    # -------------------------------
    # FINAL CLASSIFICATION
    # -------------------------------
    if score >= 4:
        level = "Foreign / Multinational Exposure"
    elif score >= 2:
        level = "Transferable / Mobile Role"
    else:
        level = "Stable Local Career"

    return {
        "exposure_level": level,
        "score": score,
        "indicators": indicators
    }

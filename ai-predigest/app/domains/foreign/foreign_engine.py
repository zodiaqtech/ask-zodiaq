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
    get_signified_score,

    # --- sign helpers ---
    SIGN_LORD,

)

def evaluate_foreign(planets, houses):
    """
    KP Foreign Travel / Settlement Evaluator (Enhanced CSL Version)

    - No timing
    - Flat list of interpretive KP points
    - CSL-centric, hierarchy aware (CSL → Star → Sign)
    - Richer diagnostic output for LLM & UI
    """

    out, seen = [], set()

    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    # ------------------------------------------------------
    # 0. Extract 12th CSL (PRIMARY KP DECIDER)
    # ------------------------------------------------------
    cusp12 = next((h for h in houses if h.get("house") == 12), {})
    CSL12 = normalize_planet(cusp12.get("cusp_sub_lord"))

    if not CSL12:
        add("❓ 12th cusp sub-lord missing → KP foreign judgement not possible.")
        return out

    CSL_obj = get_planet(CSL12, planets)
    CSL_house = CSL_obj.get("house") if CSL_obj else None
    CSL_sign = CSL_obj.get("sign") if CSL_obj else None

    add(
        f"🔑 12th cusp sub-lord is {CSL12}, placed in house {CSL_house} "
        f"({CSL_sign} sign) — this planet fully controls foreign matters."
    )

    # ------------------------------------------------------
    # 1. CSL Significations (FOUNDATION)
    # ------------------------------------------------------
    sc12 = get_signified_score(CSL12, planets, houses)
    sig_set = {h for h, v in sc12.items() if v > 0}

    add(
        f"📌 {CSL12} (12th CSL) signifies houses {sorted(sig_set)}, "
        f"forming the base promise for foreign travel or settlement."
    )

    # ------------------------------------------------------
    # 2. Core KP Foreign Rule (3 / 9 / 12)
    # ------------------------------------------------------
    foreign_houses = sig_set & {3, 9, 12}

    if foreign_houses:
        add(
            f"🌍 Foreign promise confirmed — 12th CSL connects to "
            f"{sorted(foreign_houses)} (travel / long-distance / foreign land)."
        )
    else:
        add(
            f"🏠 Weak foreign promise — 12th CSL does not link to 3, 9, or 12."
        )

    # ------------------------------------------------------
    # 3. Strength & Type of Foreign Outcome
    # ------------------------------------------------------
    if 9 in sig_set and 12 in sig_set:
        add(
            "🛫 Strong KP signature: 9 + 12 both active → "
            "long-term foreign stay or settlement potential."
        )
    elif 3 in sig_set and 9 in sig_set and 12 not in sig_set:
        add(
            "✈️ 3 + 9 active without 12 → short trips, transfers, or frequent travel."
        )
    elif 12 in sig_set and 4 in sig_set:
        add(
            "🏡 4 + 12 linkage → loss of homeland and permanent relocation abroad."
        )
    else:
        add(
            "ℹ️ Foreign indicators present but require supportive periods to materialize."
        )

    # ------------------------------------------------------
    # 4. CSL Hierarchy Reinforcement (STAR & SIGN LORD)
    # ------------------------------------------------------
    if CSL_obj:
        star = normalize_planet(CSL_obj.get("nakshatra_lord"))
        sign_lord = normalize_planet(SIGN_LORD.get(CSL_sign)) if CSL_sign else None

        if star:
            sc_star = get_signified_houses(star, planets, houses)
            add(
                f"⭐ CSL star-lord is {star}, signifying houses {sorted(sc_star)} — "
                f"this modifies how and when foreign results manifest."
            )

            if {3, 9, 12} & sc_star:
                add(
                    f"⭐ Star-lord {star} reinforces foreign houses "
                    f"{sorted(sc_star & {3,9,12})}, strengthening execution."
                )

        if sign_lord:
            sc_signlord = get_signified_houses(sign_lord, planets, houses)
            add(
                f"♓ CSL sign-lord is {sign_lord}, signifying houses "
                f"{sorted(sc_signlord)} — showing environmental support."
            )

            if {3, 9, 12} & sc_signlord:
                add(
                    f"♓ Sign-lord {sign_lord} supports foreign outcomes via "
                    f"{sorted(sc_signlord & {3,9,12})}."
                )

    # ------------------------------------------------------
    # 5. Pathways (WHY foreign travel happens)
    # ------------------------------------------------------
    if 5 in sig_set and (9 in sig_set or 12 in sig_set):
        add("📚 Education / research-driven foreign travel (5 ↔ 9/12).")

    if 7 in sig_set and (9 in sig_set or 12 in sig_set):
        add("💍 Marriage or partner-led relocation indicated (7 ↔ 9/12).")

    if 10 in sig_set and (9 in sig_set or 12 in sig_set):
        add("💼 Career or job posting abroad (10 ↔ 9/12).")

    # ------------------------------------------------------
    # 6. Planetary Karaka Emphasis (KP style)
    # ------------------------------------------------------
    for planet, meaning in [
        ("Rahu", "foreign culture, immigration, unfamiliar environments"),
        ("Saturn", "long duration stay, delays, permanence"),
        ("Moon", "movement, travel, adaptability"),
        ("Mercury", "documents, visas, applications"),
        ("Jupiter", "education-based or guided foreign movement"),
    ]:
        sc = get_signified_houses(planet, planets, houses)
        if sc and {3, 9, 12} & sc:
            add(
                f"🪐 {planet} acts as a foreign karaka here — "
                f"signifying {sorted(sc & {3,9,12})} → {meaning}."
            )

    # ------------------------------------------------------
    # 7. Nature of Stay
    # ------------------------------------------------------
    if 12 in sig_set and 4 not in sig_set:
        add("🚀 Long foreign stay indicated, but permanent settlement is uncertain.")

    if 12 in sig_set and 4 in sig_set:
        add("🛖 Clear KP signature for permanent foreign settlement (12 + 4).")

    if 3 in sig_set and 9 in sig_set and 12 not in sig_set:
        add("🔁 Repeated travel rather than long-term residence abroad.")

    # ------------------------------------------------------
    # 8. CSL Identity Notes (KP classics)
    # ------------------------------------------------------
    if CSL12 == "Rahu":
        add("🧿 Rahu as 12th CSL → strong pull toward foreign lifestyle and migration.")

    if CSL12 == "Jupiter":
        add("📍 Jupiter as 12th CSL → preference for homeland; foreign stay often temporary.")

    # ------------------------------------------------------
    # 9. Final KP Summary
    # ------------------------------------------------------
    summary = []

    if foreign_houses:
        summary.append("Foreign potential confirmed.")
    else:
        summary.append("Foreign travel unlikely.")

    if 9 in sig_set and 12 in sig_set:
        summary.append("Long-term stay possible.")
    elif 3 in sig_set:
        summary.append("Short travels likely.")

    if 4 in sig_set and 12 in sig_set:
        summary.append("Permanent settlement indicated.")

    add("🔎 KP SUMMARY: " + " ".join(summary))

    return out

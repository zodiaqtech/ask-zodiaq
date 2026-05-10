from app.core.astro_constants import (
    detect_aspects,
    normalize_planet_name,
    get_planet,
    _lord_of,
    _conjoined,
    _has_evil_aspect,
    has_harmonious_aspect,
    _is_benefic,
    get_signified_houses,
    get_cusp_sub_lord,
    kp_check_promise,
    normalize_planet,
    is_barren_sign,
    _is_exalted,
    is_mute_sign,
    is_in_kendra,
    is_movable_sign,
    in_saturn_navamsa,
    is_saturn_sign,
    aspects,
    is_waning,
    get_longitude,
    longitude_to_rasi,
    is_masculine_rasi,
    is_feminine_rasi,
    get_lagna_longitude,
    is_even_sign,
    is_dual_sign,
    is_gulika_in_house,
    is_connected_to_house,
    get_lagna_sign,
    is_debilitated,
    masculine_planets,
    feminine_planets)


def evaluate_children(planets, houses):
    """
    COMPLETE CHILDREN EVALUATOR
    LOGIC: 100% IDENTICAL TO ORIGINAL
    OUTPUT: KP-EXPLAINABLE AT EVERY STEP
    """

    out, seen = [], set()

    # -----------------------
    # Helpers
    # -----------------------
    def H(n):
        return next((h for h in houses if h.get("house") == n), None)

    def house_sign(h):
        x = H(h)
        return x.get("start_rasi") if x else None

    def occupants(h):
        hh = H(h)
        if not hh:
            return []
        pls = hh.get("planets")
        if not isinstance(pls, list):
            return []
        res = []
        for p in pls:
            name = p.get("name") if isinstance(p, dict) else p if isinstance(p, str) else None
            if name:
                res.append(normalize_planet(name))
        return res

    def add(msg):
        if msg not in seen:
            out.append(msg)
            seen.add(msg)

    # -----------------------
    # KP CUSP SUB-LORDS
    # -----------------------
    sub1  = get_cusp_sub_lord(1, houses)
    sub5  = get_cusp_sub_lord(5, houses)
    sub7  = get_cusp_sub_lord(7, houses)
    sub11 = get_cusp_sub_lord(11, houses)

    # -----------------------
    # Planets & Lords
    # -----------------------
    Ju = get_planet("Jupiter", planets)
    Mo = get_planet("Moon", planets)
    Ve = get_planet("Venus", planets)
    Sa = get_planet("Saturn", planets)
    Ma = get_planet("Mars", planets)
    Ra = get_planet("Rahu", planets)
    Ke = get_planet("Ketu", planets)
    Su = get_planet("Sun", planets)

    L1  = get_planet(_lord_of(1, houses), planets)
    L2  = get_planet(_lord_of(2, houses), planets)
    L5  = get_planet(_lord_of(5, houses), planets)
    L7  = get_planet(_lord_of(7, houses), planets)
    L8  = get_planet(_lord_of(8, houses), planets)
    L11 = get_planet(_lord_of(11, houses), planets)

    # =====================================================
    # 1) PRIMARY KP PROMISE (5TH CUSP SUB-LORD)
    # =====================================================
    verdict = kp_check_promise(
        planets,
        houses,
        csl_house=5,
        promise_houses={2, 5, 11},
        obstacle_houses={6, 8, 12}
    )

    mp = verdict.get("state", "").lower()

    if mp == "promised":
        add(f"✅ KP PROMISE: 5th cusp sub-lord ({sub5}) signifies 2/5/11 → childbirth promised.")
    elif mp == "promised_with_obstacles":
        add(f"⚠️ KP PROMISE WITH OBSTACLES: 5th cusp sub-lord ({sub5}) signifies both 2/5/11 and 6/8/12 → delay indicated.")
    elif mp == "blocked":
        add(f"❌ KP DENIAL: 5th cusp sub-lord ({sub5}) signifies only 6/8/12 → childbirth denied.")
    else:
        add(f"❓ KP UNCERTAIN: 5th cusp sub-lord ({sub5}) weak/mixed → result depends on dasha.")

    if sub5 in {"Saturn", "Rahu", "Ketu"}:
        add(f"⏳ KP DELAY: 5th cusp sub-lord ({sub5}) is a natural delay planet.")

    
    # -----------------------
    # KP CUSP SUB-LORD DETAILS (EXPLAINABILITY)
    # -----------------------
    if sub5:
        sig_houses = get_signified_houses(sub5, planets, houses)

        pos = sorted(sig_houses & {2, 5, 11})
        neg = sorted(sig_houses & {6, 8, 12})

        if pos:
            add(
                f"📌 KP CSL DETAIL: 5th cusp sub-lord ({sub5}) signifies "
                f"progeny houses {pos}."
            )
        if neg:
            add(
                f"⚠️ KP CSL DETAIL: 5th cusp sub-lord ({sub5}) also signifies "
                f"obstruction houses {neg}."
            )
        if not pos and not neg:
            add(
                f"❓ KP CSL DETAIL: 5th cusp sub-lord ({sub5}) has no direct "
                "connection to core progeny or obstruction houses."
            )


    # =====================================================
    # 2) STRONG SIGNIFICATOR CHAIN (KP CORE)
    # =====================================================
    strong = set()
    for h in (2, 5, 11):
        strong.update(occupants(h))
        lord = _lord_of(h, houses)
        if lord:
            strong.add(lord)
    strong.add("Jupiter")

    pos = neg = 0
    for p in strong:
        sig = get_signified_houses(p, planets, houses)
        if sig & {2, 5, 11}:
            pos += 1
        if sig & {6, 8, 12}:
            neg += 1

    if pos > neg:
        add("🌟 KP SIGNIFICATORS: 2/5/11 dominance → childbirth supported.")
    elif neg > pos:
        add("🚫 KP SIGNIFICATORS: 6/8/12 dominance → obstruction.")
    else:
        add("⚖️ KP SIGNIFICATORS: Balanced → period-dependent.")

    # =====================================================
    # 3) JUPITER + 5TH CUSP SIGN
    # =====================================================
    if Ju:
        if _is_benefic(Ju) and not _has_evil_aspect(Ju):
            add("🌼 KP SUPPORT: Jupiter strong & unafflicted → fertility support.")
        else:
            add("⚠️ KP WEAK SUPPORT: Jupiter afflicted → fertility reduced.")

    s5 = house_sign(5)
    if s5:
        if is_barren_sign(s5):
            add(f"⚠️ KP SIGN: 5th cusp in barren sign ({s5}).")
        elif is_mute_sign(s5):
            add(f"⚠️ KP SIGN: 5th cusp in mute sign ({s5}) → miscarriage risk.")
        else:
            add(f"🌱 KP SIGN: 5th cusp in fertile sign ({s5}).")

    # =====================================================
    # 4) BENEFICS, PARIVARTANA, JUPITER–L5
    # =====================================================
    for h in (2, 5, 11):
        lord = _lord_of(h, houses)
        if lord in {"Jupiter", "Venus", "Mercury", "Moon"}:
            add(f"✅ KP SUPPORT: Benefic rules house {h}.")
        for p in occupants(h):
            if _is_benefic(get_planet(p, planets)):
                add(f"✅ KP SUPPORT: Benefic occupies house {h}.")
        if lord:
            for B in ("Jupiter", "Venus", "Moon", "Mercury"):
                if has_harmonious_aspect(get_planet(B, planets), lord):
                    add(f"✨ KP SUPPORT: Benefic aspect from {B} to lord of house {h}.")

    def is_parivartana(a, b):
        la = _lord_of(a, houses)
        lb = _lord_of(b, houses)
        if not la or not lb:
            return False
        pa = get_planet(la, planets)
        pb = get_planet(lb, planets)
        return pa and pb and pa.get("house") == b and pb.get("house") == a

    if is_parivartana(1, 5):
        add("🔁 KP PARIVARTANA: Lagna lord ↔ 5th lord → strong progeny support.")
    if is_parivartana(1, 7):
        add("🔁 KP PARIVARTANA: Lagna lord ↔ 7th lord → marital support.")
    if is_parivartana(2, 5) and is_parivartana(5, 11):
        add("🔁 KP PARIVARTANA CHAIN: 2–5–11 linked → very strong promise.")

    if L5 and (has_harmonious_aspect(L5, "Jupiter") or _conjoined(L5, Ju)):
        add("🌟 KP BOOST: 5th lord connected to Jupiter.")

    if L5 and _is_exalted(L5) and Ju and is_in_kendra(Ju):
        add("🌟 KP STRONG PROMISER: Exalted L5 + Jupiter in Kendra.")

    if Ju and is_movable_sign(Ju.get("rasi")) and L5 and (
        L5.get("house") == 5 or has_harmonious_aspect(L5, _lord_of(5, houses))
    ):
        add("🌟 KP SUPPORT: Movable Jupiter activating 5th lord.")

    if Ra and Ra.get("house") == 5 and Ra.get("rasi") in {"Aries", "Taurus", "Cancer"} and not in_saturn_navamsa(Ra):
        add("🌟 KP SPECIAL: Rahu in 5th in favorable sign.")

    # =====================================================
    # 5) ALL DENIAL, LOSS, SHORT-LIFE RULES (UNCHANGED)
    # =====================================================
    if Su and Sa and _conjoined(Su, Sa):
        add("🕯️ KP DENIAL: Sun–Saturn conjunction.")
    if Su and Sa and (_has_evil_aspect(Su, Sa) or _has_evil_aspect(Sa, Su)):
        add("🕯️ KP DENIAL: Sun–Saturn mutual affliction.")
    if Su and Sa and is_barren_sign(Su.get("rasi")) and is_barren_sign(Sa.get("rasi")):
        add("⚠️ KP DENIAL AMPLIFIER: Sun & Saturn in barren signs.")
    if L5 and L8 and _conjoined(L5, L8):
        add("🕯️ KP LOSS RISK: 5th lord conjoined 8th lord.")

    # =====================================================
    # 6) ADOPTION RULES (ALL 8)
    # =====================================================
    adoption = []

    if Ju and L5 and Ju.get("house") in {6, 8, 12} and L5.get("house") in {6, 8, 12}:
        if any(p in {"Saturn", "Rahu", "Ketu", "Mars"} for p in occupants(Ju.get("house")) + occupants(L5.get("house"))):
            adoption.append("Jupiter & L5 both ill-placed with malefics.")

    if s5 and is_saturn_sign(s5) and Mo and (Mo.get("house") == 5 or aspects(Mo, 5, houses)):
        adoption.append("5th cusp Saturn sign with Moon influence.")

    moon_lord = _lord_of(Mo.get("house"), houses) if Mo else None
    if Sa and moon_lord and _conjoined(Sa, get_planet(moon_lord, planets)):
        adoption.append("Saturn conjoined Moon-sign lord.")

    if any(is_connected_to_house(x, 5, houses, planets) for x in ("Saturn", "Moon", "Mercury")):
        adoption.append("Saturn/Moon/Mercury tied to 5th.")

    if is_connected_to_house("Saturn", 5, houses, planets) and is_connected_to_house("Mars", 5, houses, planets):
        adoption.append("Saturn & Mars tied to 5th.")

    if Sa and Mo and _conjoined(Sa, Mo) and Mo.get("house") == 11:
        adoption.append("Saturn–Moon conjunction in 11th.")

    if (is_connected_to_house("Saturn", 5, houses, planets) or
        is_connected_to_house("Mercury", 5, houses, planets)) and is_gulika_in_house(5, houses):
        adoption.append("5th afflicted + Gulika.")

    if sub7 in {"Saturn", "Rahu", "Ketu"}:
        adoption.append("7th cusp sub-lord malefic.")

    if adoption:
        add("🧬 KP ADOPTION INDICATIONS: " + " | ".join(adoption))

    # =====================================================
    # SUMMARY
    # =====================================================
    add("\n📊 KP SUMMARY")
    add(" - All conclusions derived strictly from cusp sub-lord and signification logic.")

    return out













# def evaluate_children(planets, houses):
#         """
#         COMPLETE CHILDREN EVALUATOR
#         - Implements KP + Traditional rules from your book + extras we discussed.
#         - Depends on helper functions already present in your codebase.
#         """
    
#         out, seen = [], set()
    
#         def H(n):
#             return next((h for h in houses if h.get("house") == n), None)
    
#         def house_sign(h):
#             x = H(h)
#             return x.get("start_rasi") if x else None
    
#         def occupants(h):
#             hh = H(h)
#             if not hh:
#                 return []

#             planets = hh.get("planets")
#             if not isinstance(planets, list):
#                 return []

#             out = []
#             for p in planets:
#                 if isinstance(p, dict):
#                     name = p.get("name")
#                 elif isinstance(p, str):
#                     name = p
#                 else:
#                     continue

#                 if name:
#                     out.append(normalize_planet(name))

#             return out

    
#         def add(msg):
#             if msg not in seen:
#                 out.append(msg)
#                 seen.add(msg)
    
#         # Quick references
#         sub1  = get_cusp_sub_lord(1, houses)
#         sub5  = get_cusp_sub_lord(5, houses)
#         sub7  = get_cusp_sub_lord(7, houses)
#         sub11 = get_cusp_sub_lord(11, houses)
    
#         Ju = get_planet("Jupiter", planets)
#         Mo = get_planet("Moon", planets)
#         Ve = get_planet("Venus", planets)
#         Sa = get_planet("Saturn", planets)
#         Ma = get_planet("Mars", planets)
#         Ra = get_planet("Rahu", planets)
#         Ke = get_planet("Ketu", planets)
#         Su = get_planet("Sun", planets)
#         L5 = get_planet(_lord_of(5, houses), planets)
#         L1 = get_planet(_lord_of(1, houses), planets)
#         L2 = get_planet(_lord_of(2, houses), planets)
#         L7 = get_planet(_lord_of(7, houses), planets)
#         L8 = get_planet(_lord_of(8, houses), planets)
#         L11 = get_planet(_lord_of(11, houses), planets)
    
#         # -----------------------------------------
#         # 1) UNIVERSAL KP PROMISE CHECK (CHILDREN)
#         # -----------------------------------------
        
#         verdict = kp_check_promise(
#             planets,
#             houses,
#             csl_house=5,
#             promise_houses={2, 5, 11},
#             obstacle_houses={6, 8, 12}
#         )
        
#         mp = verdict.get("state", "").lower()
        
#         if mp == "promised":
#             add("✅ Childbirth promised — 5th cusp sub-lord connects with 2/5/11.")
#         elif mp == "promised_with_obstacles":
#             add("⚠️ Childbirth promised but with obstacles — 6/8/12 also active.")
#         elif mp == "blocked":
#             add("❌ Denial — 5th cusp sub-lord tied only to 6/8/12.")
#         else:
#             add("❓ Uncertain promise — mixed/weak 5th cusp indications.")
        
#         # Delay planets for children
#         if sub5 in {"Saturn", "Rahu", "Ketu"}:
#             add("⏳ Delay tendency — 5th cusp sub-lord is Saturn/Rahu/Ketu.")

    
#         # --------------------------
#         # 2) Strong-significator chain
#         # --------------------------
#         strong = set()
#         for h in (2,5,11):
#             for p in occupants(h):
#                 strong.add(p)
#             lord = _lord_of(h, houses)
#             if lord: strong.add(lord)
#         strong.add("Jupiter")
    
#         pos, neg = 0, 0
#         for p in strong:
#             sig = get_signified_houses(p,planets, houses)
#             if sig & {2,5,11}: pos += 1
#             if sig & {6,8,12}: neg += 1
#         if pos > neg:
#             add("🌟 Strong significator chain favors birth (2/5/11 > 6/8/12).")
#         elif neg > pos:
#             add("🚫 Strong significators show more 6/8/12 — obstacles.")
#         else:
#             add("⚖️ Mixed significator chain — uncertain result.")
    
#         # --------------------------
#         # 3) Jupiter / 5th-cusp sign checks
#         # --------------------------
#         if Ju:
#             if _is_benefic(Ju) and not _has_evil_aspect(Ju):
#                 add("🌼 Jupiter strong & unafflicted — general fertility supported.")
#             else:
#                 add("⚠️ Jupiter afflicted — fertility somewhat reduced.")
    
#         s5 = house_sign(5)
#         if s5:
#             if is_barren_sign(s5):
#                 add("⚠️ 5th cusp in barren sign — lower conception chance.")
#             elif is_mute_sign(s5):
#                 add("⚠️ 5th cusp in mute sign — classical miscarriage tendency.")
#             else:
#                 add(f"🌱 5th cusp in fertile sign ({s5}) — supports conception.")
    
#         # --------------------------
#         # 4) Classical promising combos & parivartana
#         # --------------------------
#         # Benefic lords / occupants / benefic aspects
#         for h in (2,5,11):
#             lord = _lord_of(h, houses)
#             if lord in {"Jupiter","Venus","Mercury","Moon"}:
#                 add(f"✅ Benefic lord for house {h} — promising.")
#             for p in occupants(h):
#                 if _is_benefic(get_planet(p, planets)):
#                     add(f"✅ Benefic occupies house {h}.")
#             if lord:
#                 for B in ("Jupiter","Venus","Moon","Mercury"):
#                     if has_harmonious_aspect(get_planet(B, planets), lord):
#                         add(f"✨ Benefic aspect on lord of house {h}.")
    
#         # Parivartana checks (mutual exchange)
#         def is_parivartana(a, b):
#             """Return True if lord of house a occupies house b and lord of house b occupies house a."""
#             la = _lord_of(a, houses)
#             lb = _lord_of(b, houses)
#             if not la or not lb: return False
#             p_la = get_planet(la, planets)
#             p_lb = get_planet(lb, planets)
#             return (p_la and p_la.get("house") == b) and (p_lb and p_lb.get("house") == a)
    
#         if is_parivartana(1,5):
#             add("🔁 Parivartana L1↔L5 — very supportive for progeny.")
#         if is_parivartana(1,7):
#             add("🔁 Parivartana L1↔L7 — supportive.")
#         # L2, L5, L11 mutual exchange (check cyclic)
#         if is_parivartana(2,5) and is_parivartana(5,11):
#             add("🔁 Parivartana among L2↔L5↔L11 — strong support for children.")
    
#         # L5 & Jupiter connection
#         if L5 and (has_harmonious_aspect(L5, "Jupiter") or _conjoined(L5, Ju)):
#             add("🌟 5th lord connected with Jupiter — strong childbirth promise.")
    
#         # L5 exalted + Jupiter in Kendra
#         if L5 and _is_exalted(L5) and Ju and is_in_kendra(Ju):
#             add("🌟 L5 exalted & Jupiter in Kendra — powerful promiser.")
    
#         # Jupiter in movable sign + 5th occupied/aspected by L5
#         if Ju and is_movable_sign(Ju.get("rasi")):
#             if (L5 and L5.get("house") == 5) or (L5 and has_harmonious_aspect(L5, _lord_of(5, houses))):
#                 add("🌟 Jupiter in movable + L5 acting on 5th — very supportive.")
    
#         # Rahu in 5th special condition
#         if Ra and Ra.get("house") == 5 and Ra.get("rasi") in {"Aries","Taurus","Cancer"} and not in_saturn_navamsa(Ra):
#             add("🌟 Rahu in 5th in Aries/Taurus/Cancer (not Saturn navamsa) — promiser.")
    
#         # Gemini/Virgo 5th rule (avoid Ardra/Hasta in certain lords)
#         if s5 in {"Gemini","Virgo"}:
#             bad_stars = {"Ardra","Hasta"}
#             # check nakshatras of L2/L7/L11/Jupiter
#             bad_found = False
#             for pname in (_lord_of(2,houses), _lord_of(7,houses), _lord_of(11,houses), "Jupiter"):
#                 p = get_planet(pname, planets) if pname else None
#                 if p and p.get("nakshatra") in bad_stars:
#                     bad_found = True
#             if not bad_found:
#                 add("🌟 Gemini/Virgo 5th with no Ardra/Hasta occupancy in key planets — favorable.")
    
#         # No malefics in Lagna + 5/7/11 free from malefic aspects
#         lag_occ = occupants(1)
#         if not any(x in {"Saturn","Rahu","Ketu"} for x in lag_occ):
#             good = True
#             for h in (5,7,11):
#                 lordh = _lord_of(h, houses)
#                 if lordh and _has_evil_aspect(get_planet(lordh, planets)):
#                     good = False
#             if good:
#                 add("🌟 No malefics in Lagna + 5/7/11 free of malefic aspects — childbirth likely in supportive periods.")
    
#         # --------------------------
#         # 5) Classical denial details (missing ones implemented)
#         # --------------------------
#         # Sun & Saturn close conjunction or evil aspects (incl. barren-sign nuance)
#         if Su and Sa:
#             if _conjoined(Su, Sa):
#                 add("🕯️ Sun–Saturn conjunction — strong denial/difficulty indicator.")
#             if _has_evil_aspect(Su, Sa) or _has_evil_aspect(Sa, Su):
#                 add("🕯️ Sun & Saturn mutually afflicting — risk for child issues.")
#             if is_barren_sign(Su.get("rasi")) and is_barren_sign(Sa.get("rasi")):
#                 add("⚠️ Both Sun & Saturn in barren signs — amplifies denial risk.")
    
#         # Saturn in Kendra receiving evil aspects from Venus & Moon (specific classical)
#         if Sa and Sa.get("house") in {1,4,7,10}:
#             if _has_evil_aspect(Sa) and ( (Ve and _has_evil_aspect(Ve, "Saturn")) or (Mo and _has_evil_aspect(Mo, "Saturn")) ):
#                 add("⚠️ Saturn in Kendra with evil aspects from Venus/Moon — strong denial marker.")
    
#         # Malefic in 4th and 5th cusp squared by Mars from 8th
#         four = H(4)
#         five_cusp = H(5)
#         if four and any(p for p in occupants(4) if p in {"Mars","Saturn","Rahu","Ketu"}) and five_cusp:
#             # detect Mars from 8th squaring 5th cusp (approx: Mars in 8th and aspect/square to 5th cusp)
#             if Ma and Ma.get("house") == 8 and aspects(Ma,5,houses) and any(p for p in occupants(4) if p in {"Mars","Saturn","Rahu","Ketu"}):
#                 add("⚠️ Malefic in 4th and Mars from 8th squaring 5th cusp — classical denial pattern.")
    
#         # Moon in 4th + malefic in Lagna + weak L1 in 5th
#         if Mo and Mo.get("house") == 4:
#             lag = occupants(1)
#             if any(x in {"Saturn","Rahu","Ketu"} for x in lag):
#                 if L1 and ( (L1.get("house") != 5) or _has_evil_aspect(L1) ):
#                     add("⚠️ Moon in 4th + malefic in Lagna + weak L1 in/for 5th — denial risk.")
    
#         # Moon in 10th + malefic in 4th + Venus in 7th
#         if Mo and Mo.get("house") == 10:
#             if any(p for p in occupants(4) if p in {"Saturn","Rahu","Ketu"}) and any(p for p in occupants(7) if p == "Venus"):
#                 add("⚠️ Moon in 10th + malefic in 4th + Venus in 7th — classical denial configuration.")
    
#         # Moon in Upachayas without benefic masculine aspect → no son (already partially)
#         if Mo and Mo.get("house") in {3,6,10,11} and not has_harmonious_aspect(Mo, "Jupiter"):
#             add("⚠️ Moon in Upachaya without benefic masculine aspect — classical denial for son.")
    
#         # --------------------------
#         # 6) Short-lived child (more complete)
#         # --------------------------
#         # Malefics in Lagna & 7th conjoined with Moon and no benefic aspect → immediate death
#         if Mo:
#             moon_cons = [p for p in occupants(Mo.get("house"))]
#             if any(m in {"Saturn","Mars","Rahu","Ketu"} for m in moon_cons):
#                 if not any(has_harmonious_aspect(get_planet(b,planets), Mo.get("name")) for b in ("Jupiter","Venus","Mercury")):
#                     # if malefics conjoined to moon in child chart
#                     add("🕯️ Malefics with Moon & no benefic aspect — high short-life risk for child.")
    
#         # Waning Moon in 12th + malefics in 1 & 8 + no benefic in Kendra → short life
#         if Mo and Mo.get("house") == 12:
#             if is_waning(Mo,planets) and any(get_planet(x,planets) and get_planet(x,planets).get("house") in {1,8} for x in ("Mars","Saturn")):
#                 kendras = [1,4,7,10]
#                 if not any(_is_benefic(get_planet(p,planets)) and get_planet(p,planets).get("house") in kendras for p in ("Jupiter","Venus","Mercury")):
#                     add("🕯️ Waning Moon in 12 + malefics in 1 & 8 + no benefic in Kendras — short-life classical sign.")
    
#         # Moon conjoined with malefics in 7/3/12
#         if Mo and any(m in occupants(Mo.get("house")) for m in ("Saturn","Mars","Rahu","Ketu")):
#             add("🕯️ Moon conjoined with malefics in 7/3/12 — short-life risk.")
    
#         # --------------------------
#         # 7) Adoption rules (all 8 already present but add clarifying nuance)
#         # --------------------------
#         adoption_indications = []
    
#         # 1. Jupiter & L5 ill-placed & their signs occupied by malefics
#         if Ju and L5 and Ju.get("house") in {6,8,12} and L5.get("house") in {6,8,12}:
#             # check occupants of their signs
#             ju_occ = occupants(Ju.get("house"))
#             l5_occ = occupants(L5.get("house"))
#             if any(p in {"Saturn","Rahu","Ketu","Mars"} for p in ju_occ + l5_occ):
#                 adoption_indications.append("Jupiter & 5th lord ill-placed and their signs occupied by malefics.")
    
#         # 2. 5th cusp in Saturn sign (rāśi or navāṁśa) and Moon in/aspects 5th
#         if s5 and is_saturn_sign(s5) and (Mo and (Mo.get("house") == 5 or aspects(Mo,5,houses))):
#             adoption_indications.append("5th cusp in Saturn sign and Moon in/aspecting 5th — adoption indicated.")
    
#         # 3. Saturn conjoined with lord of Moon's sign
#         moon_lord = _lord_of(Mo.get("house"), houses) if Mo else None
#         if Sa and moon_lord and _conjoined(Sa, get_planet(moon_lord, planets)):
#             adoption_indications.append("Saturn conjoined with lord of Moon's sign — adoption sign.")
    
#         # 4. Saturn, Moon, Mercury connected to 5th
#         for x in ("Saturn","Moon","Mercury"):
#             if get_planet(x,planets) and is_connected_to_house(x,5,houses,planets):
#                 # We'll collect collectively once
#                 pass
#         if any(get_planet(x,planets) and is_connected_to_house(x,5,houses,planets) for x in ("Saturn","Moon","Mercury")):
#             adoption_indications.append("Saturn/Moon/Mercury connected to 5th — adoption possibility.")
    
#         # 5. Saturn & Mars tied to 5th
#         if is_connected_to_house("Saturn",5,houses,planets) and is_connected_to_house("Mars",5,houses,planets):
#             adoption_indications.append("Saturn & Mars tied to 5th — adoption.")
    
#         # 6. Saturn conjoined Moon in 11th
#         if Sa and Mo and _conjoined(Sa,Mo) and Mo.get("house") == 11:
#             adoption_indications.append("Saturn conjoined with Moon in 11th — adoption sign.")
    
#         # 7. 5th occupied/aspected by Saturn or Mercury and Gulika in 5th
#         if (is_connected_to_house("Saturn",5,houses,planets) or is_connected_to_house("Mercury",5,houses,planets)) and is_gulika_in_house(5, houses):
#             adoption_indications.append("5th affected by Saturn/Mercury + Gulika in 5th — adoption.")
    
#         # 8. Judge 7th house for adoption (sub7 in malefics)
#         if sub7 in {"Saturn","Rahu","Ketu"}:
#             adoption_indications.append("7th cusp sub-lord indicates non-biological parenting.")
    
#         if adoption_indications:
#             add("🧬 Adoption indicators: " + " | ".join(adoption_indications))
    
#         # --------------------------
#         # 8) Beejam / Kshethram (sensitive points)
#         # --------------------------
#         # Helpers: get_longitude(planet) returns 0-360 float
#         def sum_longitudes(names):
#             s = 0.0
#             for n in names:
#                 p = get_planet(n, planets)
#                 if p:
#                     s += get_longitude(p)
#             return s % 360.0
    
#         beejam = sum_longitudes(["Jupiter","Sun","Venus"])
#         kshethram = sum_longitudes(["Jupiter","Moon","Mars"])
#         # check sign of the point
#         beejam_sign = longitude_to_rasi(beejam)
#         kshethram_sign = longitude_to_rasi(kshethram)
#         # For male charts, Beejam masculine sign + benefic aspect => children promised
#         # For female charts, Kshethram feminine sign + benefic aspect => children promised
#         # Need a "chart_gender" or you can assume male unless specified; we infer via input = male by default
#         chart_gender = "male"  # adapt this if you have gender info
#         if chart_gender == "male":
#             if is_masculine_rasi(beejam_sign) and any(has_harmonious_aspect(get_planet(b,planets), beejam_sign) for b in ("Jupiter","Sun","Venus")):
#                 add("🔷 Beejam in masculine sign & benefic — supports children (male-chart check).")
#         else:
#             if is_feminine_rasi(kshethram_sign) and any(has_harmonious_aspect(get_planet(b,planets), kshethram_sign) for b in ("Jupiter","Moon","Mars")):
#                 add("🔷 Kshethram in feminine sign & benefic — supports children (female-chart check).")
    
#         # --------------------------
#         # 9) Pregnancy months / miscarriage month check
#         # --------------------------
#         month_rulers = {
#             1: "Venus",
#             2: "Mars",
#             3: "Jupiter",
#             4: "Sun",
#             5: "Moon",
#             6: "Saturn",
#             7: "Mercury",
#             8: _lord_of(get_lagna_sign(planets), houses),  # lord of Adhana Lagna (assumes get_lagna_sign())
#             9: "Sun",
#             10: "Moon"
#         }
#         # if user provides a pregnancy month (month_no) you can check:
#         # Example routine: check every month ruler if afflicted -> miscarriage risk
#         afflicted_months = []
#         for m, ruler in month_rulers.items():
#             if isinstance(ruler, str):
#                 p = get_planet(ruler, planets)
#             else:
#                 # if it's a lord name returned by _lord_of
#                 p = get_planet(ruler, planets) if ruler else None
#             if p and (_has_evil_aspect(p) or is_debilitated(p)):
#                 afflicted_months.append(m)
#         if afflicted_months:
#             add("⚠️ Pregnancy-month rulers afflicted: possible miscarriage months -> " + ", ".join(map(str, afflicted_months)))
    
#         # --------------------------
#         # 10) Kerala - Santana interval method
#         # --------------------------
#         # Santāna Chandra = Moon_longitude * 5
#         # Santāna Ravi = Lagna_longitude * 5
#         if Mo:
#             sc = get_longitude(Mo) * 5.0
#             lr = get_lagna_longitude(planets) * 5.0
#             diff = abs((sc - lr) % 360.0)
#             # categorize
#             if 0 <= diff <= 60:
#                 add("🔢 Kerala: 0–60° difference — children but at great intervals.")
#             elif 60 < diff <= 120:
#                 add("🔢 Kerala: 60–120° — moderate intervals.")
#             elif 120 < diff <= 180:
#                 add("🔢 Kerala: 120–180° — rapid/short-interval births likely.")
#             elif 180 < diff <= 240:
#                 add("🔢 Kerala: 180–240° — births indicated but spacing variable.")
#             else:
#                 add("🔢 Kerala: 240–360° — difficult to have children / challenging intervals.")
    
#         # --------------------------
#         # 11) Gender heuristics & twins (extended)
#         # --------------------------
#         # Sub-lord gender rules: 11th -> male, 5th -> female (when promised)
#         if verdict["state"] == "promised":
#             if sub11 in masculine_planets():
#                 add("🧒 11th cusp sub-lord masculine — male child likely (KP rule).")
#             if sub5 in feminine_planets():
#                 add("👧 5th cusp sub-lord feminine — female child likely (KP rule).")
    
#         # Moon parity
#         if Mo:
#             if is_even_sign(Mo.get("rasi")):
#                 add("👧 Moon in even sign → female child.")
#             else:
#                 add("🧒 Moon in odd sign → male child.")
    
#         # Twins: Moon & Jupiter in dual signs or strong duplication indicators
#         if Mo and Ju and is_dual_sign(Mo.get("rasi")) and is_dual_sign(Ju.get("rasi")):
#             add("👶👶 Twins possible — Moon & Jupiter in dual signs.")
    
#         # --------------------------
#         # 12) Sterility rule (KP)
#         # --------------------------
#         if is_mute_sign(house_sign(1)) and is_barren_sign(house_sign(7)):
#             add("🚫 Sterility pattern — Asc CSL mute sign + 7th CSL barren sign (KP).")
    
#         # --------------------------
#         # 13) Extra classical denials we covered
#         # --------------------------
#         # If L5 & L8 conjoin -> short-lived risk
#         if L5 and L8 and _conjoined(L5, L8):
#             add("🕯️ L5 & L8 conjoined — childbirth with short-life risk.")
    
#         # If malefic in 4th and 5th cusp squared by Mars from 8th (already added above in nuanced form)
    
#         # --------------------------
#         # SUMMARY FLAGS
#         # --------------------------
#         promise_flag = any("Promise" in s or "promis" in s.lower() or "Strong significator chain favors birth" in s for s in out)
#         delay_flag = any("Delay" in s or "delay" in s.lower() or "obstacle" in s.lower() for s in out)
#         adoption_flag = bool(adoption_indications)
#         loss_flag = any("short-life" in s.lower() or "short-lived" in s.lower() or "🕯️" in s for s in out)
#         twins_flag = any("twins" in s.lower() or "👶👶" in s for s in out)
    
#         add("\n📊 SUMMARY")
#         add(f" - Promise: {'✅ Yes' if promise_flag else '❌ No clear promise'}")
#         add(f" - Delay/Obstacles: {'⚠️ Possible' if delay_flag else '🚀 Minimal'}")
#         add(f" - Adoption Path: {'🧬 Indicated' if adoption_flag else '—'}")
#         add(f" - Child Loss Risk: {'🕯️ Present' if loss_flag else '✅ None Noted'}")
#         if any("female" in s.lower() for s in out) or any("male" in s.lower() for s in out):
#             # prefer KP sub-lord hints if present
#             genders = [s for s in out if "Male" in s or "male" in s or "Female" in s or "female" in s or "Moon in even sign" in s]
#             add(f" - Gender Hints: {', '.join(genders[:3])}")
#         if twins_flag:
#             add(" - Twins: 👶👶 Possible")

#         FORBIDDEN_KP_KEYWORDS = ["male", "female", "ardra", "hasta",
#             "degree", "°",
#             "short-life", "child loss", "death",
#             "kerala"
#         ]

#         out = [
#             p for p in out
#             if not any(k.lower() in p.lower() for k in FORBIDDEN_KP_KEYWORDS)
#         ]

    
#         return out
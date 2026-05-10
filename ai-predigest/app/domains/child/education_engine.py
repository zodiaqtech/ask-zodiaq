from app.core.astro_constants import (
    # -------------------------------
    # Planet & name utilities
    # -------------------------------
    get_planet,
    normalize_planet,

    # -------------------------------
    # KP house / cusp helpers
    # -------------------------------
    get_cusp_sub_lord,
    _lord_of,

    # -------------------------------
    # KP signification helpers
    # -------------------------------
    get_signified_score,
    get_signified_houses,
    kp_check_promise,

    # -------------------------------
    # Placement & dignity checks (D1)
    # -------------------------------
    _in_house,
    _is_exalted,
    _is_strong_planet,

    # -------------------------------
    # Aspect / conjunction logic
    # -------------------------------
    _conjoined,
    _aspected_by,

    # -------------------------------
    # Benefic / malefic logic
    # -------------------------------
    _is_benefic,

    # -------------------------------
    # Rahu–Ketu resolution
    # -------------------------------
    resolve_rahu_ketu_sub_lord,
)

def evaluate_education_complete(planets, houses, d9_chart=None):
        """
        Full Education evaluator implementing rules 1..138 (pages 259–267).
        D9 Mode 1 (Soft Support): d9_chart is only used to *add supportive lines*;
        it never overrides or changes any D1-based decision.
    
        Expected helpers in your module (used here):
          - get_planet(name, planets)
          - normalize_planet(name)
          - _in_house(p, h)
          - _conjoined(a, b)
          - _aspected_by(p, who, types=None, max_orb=None)
          - _is_strong_planet(p, planets)
          - _is_exalted(p)
          - get_signified_houses(name, planets, houses)
          - get_signified_score(name, planets, houses)
          - _lord_of(h, houses)
          - get_cusp_sub_lord(h, houses)
          - _is_benefic(p)
          - kp_check_promise(planets, houses, house, pos_set, neg_set)
          - normalize_planet(name)
        """
    
        from collections import defaultdict
    
        # -------------------------
        # Helper: normalize and simple D9 support (SOFT)
        # -------------------------
        def _normalize_d9(d9):
            if not d9:
                return {}
            out = {}
            for k, v in d9.items():
                if not isinstance(v, dict):
                    continue
                name = v.get("name") or v.get("full_name") or v.get("full_name")
                if not name:
                    continue
                out[normalize_planet(name)] = v
            return out
    
        d9_by_name = _normalize_d9(d9_chart)
    
        def d9_strength(p):
            """Soft-support: returns 'strong' if D9 shows simple supportive signals, else None."""
            if not p:
                return None
            pname = normalize_planet(p.get("name"))
            if not pname:
                return None
            dp = d9_by_name.get(pname)
            if not dp:
                return None
    
            # Kendra + own-sign + exaltation in D9 => supportive
            kendra = {1, 4, 7, 10}
            try:
                dhouse = int(dp.get("house")) if dp.get("house") is not None else None
            except Exception:
                dhouse = None
            dz = (dp.get("zodiac") or dp.get("rasi") or "").title()
    
            own_signs = {
                "Sun": {"Leo"},
                "Moon": {"Cancer"},
                "Mercury": {"Gemini", "Virgo"},
                "Venus": {"Taurus", "Libra"},
                "Mars": {"Aries", "Scorpio"},
                "Jupiter": {"Sagittarius", "Pisces"},
                "Saturn": {"Capricorn", "Aquarius"},
            }
            exalted = {
                "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
                "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
                "Saturn": "Libra"
            }
    
            if dhouse in kendra:
                return "strong"
            if pname in own_signs and dz in own_signs[pname]:
                return "strong"
            if pname in exalted and dz == exalted[pname]:
                return "strong"
            return None
    
        # -------------------------
        # Wrappers to module helpers
        # -------------------------
        P = lambda n: get_planet(n, planets)
        NP = lambda n: normalize_planet(n)
        in_house = lambda p, h: _in_house(p, h)
        conjoined = lambda a, b: _conjoined(a, b)
        aspected_by = lambda p, who, types=None, max_orb=None: _aspected_by(p, who, types=types, max_orb=max_orb)
        strong = lambda p: _is_strong_planet(p, planets)
        exalted = lambda p: _is_exalted(p)
        signified = lambda name: get_signified_houses(NP(name), planets, houses)
        sign_score = lambda name: get_signified_score(NP(name), planets, houses)
        lord = lambda h: _lord_of(h, houses)
        cusp_sub = lambda h: get_cusp_sub_lord(h, houses)
        is_benefic = lambda p: _is_benefic(p) if callable(_is_benefic) else False
    
        # D1 planetary objects
        Sun = P("Sun"); Moon = P("Moon"); Mercury = P("Mercury"); Venus = P("Venus")
        Mars = P("Mars"); Jupiter = P("Jupiter"); Saturn = P("Saturn")
        Rahu = P("Rahu"); Ketu = P("Ketu")
        Uranus = P("Uranus"); Neptune = P("Neptune"); Pluto = P("Pluto"); Asc = P("Ascendant")
    
        # Output collector
        out = []
        seen = set()
        def add(line):
            if line and line not in seen:
                out.append(line)
                seen.add(line)
    
        # -------------------------
        # KP CORE (rules 1-14)
        # -------------------------
        add("KP CORE: Education houses: 4=schooling, 3=inclination/specialisation, 9=higher studies. (Rules 1-3)")
        add("Intellect ↔ houses 3 & 5; Studious habits ↔ 4 (Rules 4-5).")
    
        # 6-10 Nipuna & Mercury rules
        nipuna_flag = False
        if Sun and Mercury and conjoined(Sun, Mercury):
            nipuna_flag = True
            add("Nipuna Yoga: Sun+Mercury conjunction → Nipuna-like intellect (Rule 6).")
            if d9_strength(Sun) == "strong" or d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa strengthens Sun/Mercury (soft support).")
    
        if Mercury and Sun and (Mercury.get("nakshatra_lord") == Sun.get("name") or Mercury.get("nakshatra_lord") == Sun.get("nakshatra_lord")):
            nipuna_flag = True
            add("Mercury in Sun's nakshatra/sub → Nipuna-like intellect (Rule 7).")
            if d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa Mercury strong (soft support).")
    
        if Mercury and strong(Mercury):
            add("Strong Mercury present → possibility of advanced/multiple degrees (Rule 8).")
            if d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa confirms Mercury strength (soft support).")
    
        if Mercury and (Mercury.get("is_retro") or Mercury.get("is_combusted")):
            add("Mercury retro/combust/eclipsed — note: DOES NOT by itself deny education (Rules 9-10).")
    
        # 11 Ascendant sub-lord determines studious vs lazy
        asc_sub = cusp_sub(1)
        asc_eff = resolve_rahu_ketu_sub_lord(planets, houses, asc_sub) if asc_sub else asc_sub
        if asc_eff in {"Mercury", "Jupiter"}:
            add("Ascendant sub-lord = Mercury/Jupiter → studious mindset (Rule 11).")
        elif asc_eff == "Saturn":
            add("Ascendant sub-lord = Saturn → obstacles in studies/exams likely (Rule 11).")
        else:
            add(f"Ascendant sub-lord = {asc_eff} → neutral/depends-on-periods (Rule 11).")
        try:
            if asc_eff and P(asc_eff) and d9_strength(P(asc_eff)) == "strong":
                add(f"D9 support: Navamsa shows {asc_eff} strength (soft support).")
        except Exception:
            pass
    
        # 12-13 Saturn as significator of 3 -> exam delays
        if 3 in signified("Saturn") or lord(3) == "Saturn":
            add("Saturn signifies house 3 → potential obstacles during study, exam delays, recall issues (Rules 12-13).")
            if d9_strength(Saturn) == "strong":
                add("D9 support: Navamsa Saturn strong (soft support).")
    
        # 14 Subject priority
        add("To evaluate subject proficiency, prioritise houses: 2,4,9,10,5. (Rule 14)")
    
        # -------------------------
        # ASTROLOGY / MATHEMATICS (15-30)
        # -------------------------
        add("----- Subject Blocks: Astrology & Mathematics -----")
    
        # 15 Mercury angular
        if Mercury and any(in_house(Mercury, h) for h in (1,4,7,10)):
            add("Mercury occupies an angular house → Mercury as angular significator (Rule 15).")
            if d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa Mercury angular/strong (soft support).")
    
        # 16 Venus significator houses
        venus_sig = signified("Venus")
        if venus_sig and any(h in venus_sig for h in (5,9,2)):
            add("Venus signifies houses 5/9/2 → Venus supports creative/learning/finance subjects (Rule 16).")
            if d9_strength(Venus) == "strong":
                add("D9 support: Navamsa Venus strong (soft support).")
    
        # 17 Lord of 2 connections
        lord2 = lord(2)
        if lord2:
            lord2p = P(lord2)
            if lord2p and (conjoined(lord2p, Mercury) or conjoined(lord2p, Venus) or any(h in signified(lord2) for h in signified("Mercury"))):
                add(f"Lord of 2 ({lord2}) connected to Mercury/Venus → supports astrology/communication skills (Rule 17).")
                if lord2p and d9_strength(lord2p) == "strong":
                    add(f"D9 support: Navamsa {lord2} strong (soft support).")
    
        add("Mathematics checks (Rules 19-30):")
    
        # 19 Saturn in 8
        if Saturn and in_house(Saturn, 8):
            add("Saturn in 8 → abstract/math aptitude (Rule 19).")
            if d9_strength(Saturn) == "strong":
                add("D9 support: Navamsa Saturn strong (soft support).")
    
        # 20 Jupiter in ascendant
        if Jupiter and Asc and Jupiter.get("house") == Asc.get("house"):
            add("Jupiter in Ascendant → mathematical breadth / classical math aptitude (Rule 20).")
            if d9_strength(Jupiter) == "strong":
                add("D9 support: Navamsa Jupiter strong (soft support).")
    
        # 21-22 Mercury + lord2 conjunction
        if lord2 and P(lord2) and Mercury:
            if conjoined(Mercury, P(lord2)) and P(lord2).get("house") in {1,4,7,10}:
                add("Mercury + lord of 2 conjunct in an angle → strong mathematics aptitude (Rules 21-22).")
            elif conjoined(Mercury, P(lord2)):
                add("Lord of 2 conjunct Mercury (non-angle) → supportive for math/commerce (Rules 21-22).")
            if d9_strength(Mercury) == "strong" or (P(lord2) and d9_strength(P(lord2)) == "strong"):
                add("D9 support: Navamsa confirms Mercury/lord2 strength (soft support).")
    
        # 23 Venus exalted or Kendra
        if Venus and (exalted(Venus) or any(in_house(Venus, h) for h in (1,4,7,10))):
            add("Venus exalted or in Kendra → supportive for applied math/geometry (Rule 23).")
    
        # 24 Sun & Mercury in 2 aspected by Saturn -> statistics
        if Sun and Mercury and in_house(Sun, 2) and in_house(Mercury, 2) and Saturn and aspected_by(Saturn, "Sun"):
            add("Sun & Mercury in 2 with Saturn aspect → statistics/analytical maths tendency (Rule 24).")
    
        # 25 Sun in Virgo
        if Sun and ((Sun.get("sign") or Sun.get("rasi") or "").title() == "Virgo"):
            add("Sun in Virgo → engineering / mathematics tendency (Rule 25).")
    
        # 26 Mars in 2 with benefic aspect
        benefics = ("Jupiter", "Venus", "Mercury", "Moon")
        if Mars and in_house(Mars, 2) and any(aspected_by(Mars, b) for b in benefics):
            add("Mars in 2 with benefic aspect → applied mathematics / engineering-math interest (Rule 26).")
    
        # 27 Moon+Mars aspected by Mercury
        if Moon and Mars and conjoined(Moon, Mars) and Mercury and aspected_by(Moon, "Mercury"):
            add("Moon+Mars aspected by Mercury → problem-solving & engineering aptitude (Rule 27).")
    
        # 28 Jupiter in Lagna; Saturn in 8; Mercury lord of 8
        if Jupiter and Asc and Jupiter.get("house") == Asc.get("house") and Saturn and in_house(Saturn, 8):
            if lord(8) == "Mercury":
                add("Jupiter in Lagna + Saturn in 8 + Mercury lord of 8 → strong mathematical/abstract aptitude (Rule 28).")
    
        # 29-30 KP math (Mercury strong + signifying 2/4/9)
        if Mercury and (strong(Mercury) or d9_strength(Mercury) == "strong"):
            sc = sign_score("Mercury") or []
            if any(h in sc for h in (2,4,9)):
                add("KP math: Mercury strong and signifying 2/4/9 → high maths/technical aptitude (Rules 29-30).")
    
        # -------------------------
        # LAW (31-36)
        # -------------------------
        add("----- Law Rules (31-36) -----")
        if Jupiter and (strong(Jupiter) or d9_strength(Jupiter) == "strong"):
            add("Jupiter strong → theoretical / legal aptitude (Rule 31).")
        if Mercury and (strong(Mercury) or d9_strength(Mercury) == "strong"):
            add("Mercury strong → eloquence & drafting ability (Rule 32).")
        if Mars and (strong(Mars) or d9_strength(Mars) == "strong"):
            add("Mars strong → analytical & argumentative skills (Rules 33-34).")
    
        s4_sub = cusp_sub(4); s9_sub = cusp_sub(9)
        if s4_sub in {"Mars", "Mercury"} or s9_sub in {"Mars", "Mercury"}:
            add("Sublord of 4 or 9 = Mars/Mercury → litigation / audacity traits (Rule 35).")
        if Mars and Mars.get("sub_lord") == "Jupiter":
            add("Mars in Jupiter sub → cross-examiner / forensic instincts (Rule 36).")
    
        # -------------------------
        # ENGINEERING (37-49)
        # -------------------------
        add("----- Engineering Rules (37-49) -----")
        add("Engineering requires mathematics, drawing & planning (Rule 37).")
    
        if Mars and Mercury and (conjoined(Mars, Mercury) or ((strong(Mars) or d9_strength(Mars) == "strong") and (strong(Mercury) or d9_strength(Mercury) == "strong"))):
            add("Mars + Mercury → engineering tendency (Rules 38-39).")
    
        if Venus and Mercury and (conjoined(Venus, Mercury) or ((strong(Venus) or d9_strength(Venus) == "strong") and (strong(Mercury) or d9_strength(Mercury) == "strong"))):
            add("Venus+Mercury → sanitary/chemical engineering possibility (Rule 40).")
        if Moon and Mercury and (conjoined(Moon, Mercury) or (strong(Moon) and strong(Mercury))):
            add("Moon+Mercury → textile engineering tendency (Rule 41).")
        if Sun and Mercury and (conjoined(Sun, Mercury) or (strong(Sun) and strong(Mercury))):
            add("Sun+Mercury → chemical / pharma industry tendency (Rule 42).")
        if Moon and Mars and Mercury and ((conjoined(Moon, Mars) and conjoined(Moon, Mercury)) or all((strong(x) or d9_strength(x) == "strong") for x in (Moon, Mars, Mercury))):
            add("Moon+Mars+Mercury → marine engineering tendency (Rule 43).")
        if Moon and Sun and Mercury and ((conjoined(Moon, Sun) and conjoined(Sun, Mercury)) or all((strong(x) or d9_strength(x) == "strong") for x in (Moon, Sun, Mercury))):
            add("Moon+Sun+Mercury → mechanical engineering (Rule 44).")
        if Moon and Saturn and Mercury and (conjoined(Moon, Saturn) or conjoined(Saturn, Mercury) or all((strong(x) or d9_strength(x) == "strong") for x in (Moon, Saturn, Mercury))):
            add("Moon+Saturn+Mercury → mining engineering (Rule 45).")
        if Mars and Jupiter and Mercury and (all((strong(x) or d9_strength(x) == "strong") for x in (Mars, Jupiter, Mercury)) or (conjoined(Mars, Jupiter) and conjoined(Jupiter, Mercury))):
            add("Mars+Jupiter+Mercury → mechanical / tools engineering (Rule 46).")
        if Uranus and Mercury and (conjoined(Uranus, Mercury) or (d9_strength(Uranus) == "strong" and (strong(Mercury) or d9_strength(Mercury) == "strong"))):
            add("Uranus+Mercury → research / atomic energy / high-tech engineering (Rule 47).")
        if Neptune and Mercury and (conjoined(Neptune, Mercury) or (d9_strength(Neptune) == "strong" and (strong(Mercury) or d9_strength(Mercury) == "strong"))):
            add("Neptune+Mercury → research / advanced engineering (Rule 48).")
        if Mercury and Mercury.get("nakshatra") and str(Mercury.get("nakshatra")).lower() in {"ashlesha", "jyestha", "revati"}:
            add("Mercury in Ashlesha/Jyestha/Revati → engineering-producing stars (Rule 49).")
            if d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa Mercury strong (soft support).")
    
        # -------------------------
        # MEDICINE (50-70)
        # -------------------------
        add("----- Medicine Rules (50-70) -----")
        add("Sun = Dhanvantri classical signifier for medicine (Rule 50).")
        signs_present = { (p.get("sign") or p.get("rasi") or "").title() for p in planets.values() if isinstance(p, dict) }
        if "Virgo" in signs_present:
            add("Virgo emphasis → hospital/clinical orientation (Rule 51).")
        if "Scorpio" in signs_present:
            add("Scorpio emphasis → medicine/chemicals/mortuary inclinations (Rule 52).")
        if "Pisces" in signs_present:
            add("Pisces emphasis → isolation/hospital environment (Rule 53).")
        if "Leo" in signs_present:
            add("Leo emphasis → medicine / clinical leadership (Rule 54).")
    
        # 55-70 specialties
        if Sun and Jupiter and (conjoined(Sun, Jupiter) or (strong(Sun) and strong(Jupiter)) or (d9_strength(Sun) == "strong" and d9_strength(Jupiter) == "strong")):
            add("Sun+Jupiter → physician / general medicine (Rule 55).")
        if Sun and Mercury and conjoined(Sun, Mercury):
            add("Sun+Mercury → consulting physician / internal medicine (Rule 56).")
        if Sun and Mars and (conjoined(Sun, Mars) or in_house(Mars, 6)):
            add("Sun+Mars or Mars in 6 → surgical inclinations (Rule 57).")
        if Sun and Venus and conjoined(Sun, Venus):
            add("Sun+Venus → venereal / bone / dental inclinations (Rules 58 & 61).")
        if Sun and Saturn and conjoined(Sun, Saturn):
            add("Sun+Saturn → eye/ENT/diagnostic specialty signals (Rules 59 & 62).")
        if Sun and Venus and Mars and (conjoined(Sun, Venus) and conjoined(Venus, Mars)):
            add("Sun+Venus+Mars → optics / ophthalmic tendencies (Rule 60).")
        if Sun and Venus and Mercury and (conjoined(Sun, Venus) and conjoined(Venus, Mercury)):
            add("Sun+Venus+Mercury → X-ray / diagnostic imaging tendencies (Rule 63).")
        if Sun and Venus and ((Rahu and conjoined(Sun, Rahu)) or (Uranus and conjoined(Sun, Uranus)) or (Rahu and conjoined(Venus, Rahu))):
            add("Sun+Venus + Rahu/Uranus → research-oriented medical specialties (Rule 64).")
        if Sun and Moon and Mercury and (conjoined(Sun, Moon) and aspected_by(Moon, "Mercury")):
            add("Sun+Moon+Mercury → respiratory / TB / asthma associations (Rule 65).")
        if Moon and Sun and Venus and (conjoined(Moon, Sun) and conjoined(Sun, Venus)):
            add("Moon+Sun+Venus → blood-pressure / cardiac predispositions (Rule 66).")
        if lord(4) and Sun and Saturn:
            if P(lord(4)) and (conjoined(Sun, P(lord(4))) or conjoined(P(lord(4)), Saturn)):
                add("Sun + lord of 4 + Saturn → cardiac specialist indicator (Rule 67).")
        if lord(5) and Sun and Saturn and P(lord(5)) and conjoined(Sun, P(lord(5))):
            add("Sun + lord of 5 + Saturn → Ayurvedic / traditional medicine inclination (Rule 68).")
        if Mars and Jupiter and Sun and all((strong(x) or d9_strength(x) == "strong") for x in (Mars, Jupiter, Sun)):
            add("Mars+Jupiter+Sun → strong medicine inclination (Rule 69).")
        if Jupiter and Sun and Saturn and all((strong(x) or d9_strength(x) == "strong") for x in (Jupiter, Sun, Saturn)):
            add("Jupiter+Sun+Saturn → medicine / professional medical aptitude (Rule 70).")
    
        # -------------------------
        # PHILOSOPHY (71-80)
        # -------------------------
        add("----- Philosophy Rules (71-80) -----")
        if Sun and Mercury and conjoined(Sun, Mercury):
            ss = sign_score("Sun") or []
            if 5 in ss and Saturn and (strong(Saturn) or d9_strength(Saturn) == "strong"):
                add("Sun+Mercury as significator of 5 connected with Saturn → KP Philosophy inclination (Rule 71).")
        if Jupiter and Saturn and (any(h in signified("Jupiter") for h in (4,9)) and any(h in signified("Saturn") for h in (4,9))):
            add("Jupiter + Saturn signifying 4/9 → philosophical bent (Rule 72).")
            if d9_strength(Jupiter) == "strong" or d9_strength(Saturn) == "strong":
                add("D9 support: Navamsa Jupiter/Saturn strong (soft support).")
        if Mercury and exalted(Mercury) and (2 in signified("Mercury")):
            add("Mercury exalted in 2 → Hindu philosophical bent (Rule 73).")
        if Saturn and any(in_house(Saturn, h) for h in (1,4,7,10)):
            add("Saturn angular in divisional-sensitive position → classical philosophy signals (Rules 74/76).")
        if Jupiter and any(in_house(Jupiter, h) for h in (1,4,7,10)):
            add("Jupiter angular/trine → philosophical depth (Rules 75/77).")
        if Venus and in_house(Venus, 1):
            add("Venus in Lagna/angular in divisional checks → refined philosophical/aesthetic disposition (Rules 78-79).")
        add("Amsa/divisional-based checks may refine classical philosophy signals (Rule 80).")
    
        # -------------------------
        # MUSIC (81-97)
        # -------------------------
        add("----- Music Rules (81-97) -----")
        if in_house(P("Venus"), 2) or (Venus and Venus.get("house") == 2):
            add("2nd house / Venus occupancy → vocal music aptitude (Rule 81/96).")
        if any(p and p.get("house") == 3 for p in planets.values() if isinstance(p, dict)):
            add("3rd house emphasis → instrumental music aptitude (Rule 82).")
        if any(p and p.get("house") in {3,12} for p in planets.values() if isinstance(p, dict)):
            add("3rd & 12th involvement → instruments using hands/legs (Rule 83).")
        if Neptune:
            add("Neptune influence → affinity for string instruments (Rule 84).")
        if Venus and (strong(Venus) or d9_strength(Venus) == "strong"):
            add("Venus strong → musical taste / inclination (Rule 85).")
        if Moon and Venus and (conjoined(Moon, Venus) or (strong(Moon) and strong(Venus))):
            add("Moon+Venus → imagination & alapana ability (Rule 86).")
        if Mercury and (strong(Mercury) or d9_strength(Mercury) == "strong"):
            add("Mercury strongly placed → rhythm & stage confidence (Rule 87).")
        if Mars and Saturn and Venus and ((conjoined(Mars, Venus) and conjoined(Saturn, Venus)) or all((strong(x) or d9_strength(x) == "strong") for x in (Mars, Saturn, Venus))):
            add("Mars+Saturn+Venus → percussion (tabla/mridangam) aptitude (Rule 88).")
        add("Instrument mapping (flute/violin/veena/jalatarangam) requires ascensional sign-length data; conservative pointers only (Rules 89-96).")
        if Sun and ((Sun.get("sign") or "").title() == "Sagittarius"):
            add("Sun in Sagittarius → taste for music / classical inclination (Rule 97).")
    
        # -------------------------
        # JOURNALISM (98-101)
        # -------------------------
        add("----- Journalism (98-101) -----")
        if Jupiter and Mercury and ((strong(Jupiter) or d9_strength(Jupiter) == "strong") and (strong(Mercury) or d9_strength(Mercury) == "strong")):
            add("Jupiter + Mercury strong → journalism & reporting aptitude (Rule 98).")
        if Moon and (strong(Moon) or d9_strength(Moon) == "strong"):
            add("Moon support → narrative ability (Rule 99).")
        if (Mercury and str(Mercury.get("sign") or Mercury.get("rasi") or "").title() in {"Virgo", "Pisces"}) or (Jupiter and str(Jupiter.get("sign") or Jupiter.get("rasi") or "").title() in {"Virgo", "Pisces"}):
            add("Mercury/Jupiter in Virgo or Pisces → attention to detail in narration/reporting (Rule 100).")
        if (3 in signified("Jupiter") or 3 in signified("Mercury") or 3 in signified("Moon")) and (9 in signified("Jupiter") or 9 in signified("Mercury") or 9 in signified("Moon")):
            add("3rd & 9th signified by Jupiter/Mercury/Moon → journalism & long-form reporting (Rule 101).")
    
        # -------------------------
        # AUDITING/ACCOUNTS / GEOLOGY / GEOGRAPHY / CHEMISTRY / PHYSICS / HISTORY (102-110)
        # -------------------------
        add("----- Auditing, Geology, Geography, Chemistry, Physics, History (102-110) -----")
        if Mercury and Moon and (strong(Mercury) or d9_strength(Mercury) == "strong") and (strong(Moon) or d9_strength(Moon) == "strong"):
            add("Mercury + Moon favourable → auditing / accounts aptitude (Rules 102-103).")
        if lord2 in {"Mercury", "Moon"}:
            add("Lord of 2 is Mercury/Moon → accounting / auditing likelihood (Rule 103).")
        if Saturn and ((Saturn.get("sign") or "").title() == "Capricorn" or any(((p.get("sign") or "").title() == "Capricorn") for p in planets.values() if isinstance(p, dict))):
            add("Saturn/Capricorn emphasis → geology / earth sciences (Rule 104).")
        sun_star = Sun.get("nakshatra_lord") if Sun else None
        if sun_star and any(p.get("nakshatra_lord") == sun_star for p in planets.values() if isinstance(p, dict)):
            add("Sun prominence or planets in Sun's star/sub → geography / cartography aptitude (Rule 105).")
        if Venus and (Venus.get("nakshatra") or Venus.get("nakshatra_lord")):
            add("Venus influence → chemistry / laboratory sciences (Rules 106-107).")
        if Mercury and Venus and ((strong(Mercury) or d9_strength(Mercury) == "strong") and (strong(Venus) or d9_strength(Venus) == "strong")):
            add("Mercury + Venus → physics propensity (Rules 108-109).")
        if Moon and Mercury and Jupiter and all((strong(x) or d9_strength(x) == "strong") for x in (Moon, Mercury, Jupiter)):
            add("Moon + Mercury + Jupiter → history / humanities aptitude (Rule 110).")
    
        # -------------------------
        # EDUCATION SUCCESS & END (111-119)
        # -------------------------
        add("----- Education Success & End (111-119) -----")
        lord4 = lord(4); lord9 = lord(9); lord11 = lord(11)
        if lord4 and lord9 and lord11:
            s11 = set(get_signified_houses(NP(lord11), planets, houses) or [])
            s4sig = set(get_signified_houses(NP(lord4), planets, houses) or [])
            s9sig = set(get_signified_houses(NP(lord9), planets, houses) or [])
            if 11 in s4sig or 11 in s9sig or (s4sig & s11) or (s9sig & s11):
                add("If lords of 4 & 9 link to 11 (sub/sign) → education success likely (Rule 111).")
                # D9 soft support for 11th lord, if present
                if lord11 and P(lord11) and d9_strength(P(lord11)) == "strong":
                    add("D9 support: Navamsa lord of 11 strong — supportive for gains/scholarship (soft support).")
    
        if lord4 and lord11:
            s4 = get_signified_houses(NP(lord4), planets, houses) or []
            s11 = get_signified_houses(NP(lord11), planets, houses) or []
            if s4 or s11:
                add("Any significant connection between lords of 4 & 11 → supports education continuation (Rule 112).")
    
        # 113 resume: aspects from lord11 to occupants of 4
        h4 = next((h for h in houses if h.get("house") == 4), {})
        occ4_planets = h4.get("planets", []) if h4 else []
        if lord11 and P(lord11) and occ4_planets and any(aspected_by(P(lord11), p.get("name")) for p in occ4_planets if isinstance(p, dict)):
            add("Aspects from lord of 11 (or related planets) to occupants of 4 → discontinued education may resume (Rule 113).")
    
        # 114-117 discontinuation risk
        end_signals = 0
        for hno in (3,5,8):
            lh = lord(hno)
            if lh and P(lh) and (P(lh).get("house") in {3,5,8}):
                end_signals += 1
        if end_signals >= 2:
            add("Multiple house-lord placements in 3/5/8 → risk of education discontinuation during certain dashas (Rules 114-117).")
    
        # 118-119 malefics and Rahu connectivity
        if Saturn and any(in_house(Saturn, h) for h in (3,6,8,12)):
            add("Malefic Saturn involvement can be detrimental to studies/exams (Rule 118).")
        if Rahu and any(h in signified("Rahu") for h in (4,9)):
            add("Rahu linked to 4 & 9 → can support unconventional/higher/foreign education (Rule 119).")
            if d9_strength(Rahu) == "strong":
                add("D9 support: Navamsa Rahu placement is supportive (soft support).")
    
        # -------------------------
        # COMPETITIVE EXAMS & SCHOLARSHIPS (120-134)
        # -------------------------
        add("----- Competitive Exams & Scholarships (120-134) -----")
        if Mars and Mercury and Jupiter and all((strong(x) or d9_strength(x) == "strong") for x in (Mars, Mercury, Jupiter)):
            conn_count = sum(1 for n in ("Mars", "Mercury", "Jupiter") for h in (4,9,11) if h in get_signified_houses(n, planets, houses))
            if conn_count >= 2:
                add("Mars + Mercury + Jupiter connected to 4/9/11 → strong chance in competitive exams (Rules 120-121).")
    
        add("4th -> study; 8th -> institution; 12th -> expenses; 7th -> payer; 6th -> loan; 11th -> gains (Rules 122-127).")
    
        lord6 = lord(6)
        scholarship_flag = False
        if lord4 and lord6 and (lord4 == lord6 or (P(lord4) and P(lord6) and conjoined(P(lord4), P(lord6)))):
            scholarship_flag = True
            add("4th connected with 6th or its lord → scholarship/loan / institutional payment possible (Rule 128).")
    
        if lord11 and P(lord11) and (strong(P(lord11)) or d9_strength(P(lord11)) == "strong"):
            scholarship_flag = True
            add("Strong 11th / lord of 11 → gains including scholarships more likely (Rule 131).")
    
        h8 = next((h for h in houses if h.get("house") == 8), {})
        if h8 and any(is_benefic(get_planet(normalize_planet(p.get("name")), planets)) for p in h8.get("planets", []) if isinstance(p, dict)):
            scholarship_flag = True
            add("Benefic occupying 8th → institution sponsor / pays and studies (Rule 131).")
    
        h12 = next((h for h in houses if h.get("house") == 12), {})
        if h12 and (any(NP(p.get("name")) == "Venus" for p in h12.get("planets", [])) or (lord(3) and lord(3) in (NP(p.get("name")) for p in h12.get("planets", [])))):
            add("12th connected with Venus or lord of 3 → conveyance / travel expenses for study (Rule 132).")
    
        if h12 and any(NP(p.get("name")) == "Mars" for p in h12.get("planets", [])) and (3 in signified("Mars") or lord(3)):
            add("12th + Mars + 3 → hostel/boarding / long-stay education arrangements (Rule 133).")
    
        if scholarship_flag:
            add("Scholarship/loan possibility flagged (non-repayable scholarship if 11th robust) (Rule 134).")
    
        # -------------------------
        # FOREIGN STUDY (135-138)
        # -------------------------
        add("----- Foreign Study Indicators (135-138) -----")
        foreign_flag = False
        if Rahu and Rahu.get("house") in {9, 12}:
            foreign_flag = True
            add("Rahu in 9/12 → foreign or unconventional education likely (Rule 135).")
        if h12 and h12.get("planets"):
            add("12th house involvement → overseas / travel / boarding / expenses relevance (Rule 136).")
        add("Check relevant dashas (planets ruling foreign signs/houses) for timing of foreign study — requires dasha analysis (Rule 137).")
        if foreign_flag:
            add("Example indicator: native studying abroad (Rule 138).")
            # D9 soft check for Rahu in 9/12
            if d9_by_name and any((name in d9_by_name and (d9_by_name[name].get("house") in {9, 12})) for name in ("Rahu",)):
                add("D9 support: Navamsa Rahu placement in 9/12 (soft support).")
    
        # -------------------------
        # ADDITIONAL TIGHT KP & NAKSHATRA CHECKS
        # -------------------------
        add("----- Additional Tight KP Rules & Nakshatra checks -----")
        if Mercury and Mercury.get("nakshatra") and str(Mercury.get("nakshatra")).lower() in {"ashlesha", "jyestha", "revati"}:
            add("Nakshatra: Mercury in Ashlesha/Jyestha/Revati → engineering-producing stars (Rule 49).")
            if d9_strength(Mercury) == "strong":
                add("D9 support: Navamsa Mercury strong (soft support).")
    
        sub1 = cusp_sub(1)
        if sub1:
            add(f"Ascendant cusp sub-lord = {sub1} — use as primary disposition indicator (Rule 11 & supporting).")
    
        # -------------------------
        # AGGREGATION: subject scoring & top streams
        # -------------------------
        add("---- Aggregate Subject Scores & Top Streams (combined from above rules) ----")
        score_map = defaultdict(int)
        keyword_rules_map = {
            "Mathematics": ["mathematics", "math", "statistics", "analytical maths", "maths"],
            "Engineering": ["engineering", "mechanical", "marine", "mining", "atomic", "high-tech", "chemical", "automobile"],
            "Medicine": ["physician", "medicine", "medical", "surgery", "surgeon", "dental", "optics", "cardiac", "ayurvedic", "diagnostic", "x-ray"],
            "Law": ["litigation", "cross-examiner", "advocacy", "law", "legal"],
            "Journalism": ["journalism", "reporting", "narration", "narrative", "detailed narration"],
            "Music": ["music", "vocal", "instrumental", "string", "percussion", "tabla", "veena", "violin", "flute"],
            "Accounts": ["auditing", "accounts", "accounting", "finance", "commerce"],
            "Physics": ["physics", "research", "atomic", "high-tech"],
            "Chemistry": ["chemistry", "laboratory", "lab sciences", "chemical"],
            "History": ["history", "humanities"],
            "Geology": ["geology", "earth sciences", "mining"],
            "Geography": ["geography", "cartography"]
        }
        for line in out:
            l = line.lower()
            for stream, keys in keyword_rules_map.items():
                for k in keys:
                    if k in l:
                        score_map[stream] += 1
    
        streams_sorted = sorted(score_map.items(), key=lambda kv: (-kv[1], kv[0]))
        if streams_sorted:
            top_streams = [s for s, v in streams_sorted if v > 0][:6]
            add("Top candidate study streams (by strict rule-match): " + ", ".join(top_streams))
        else:
            add("No dominant study stream emerged from strict rule matches.")
    
        # -------------------------
        # SUMMARY / KP-first
        # -------------------------
        add("---- Summary ----")
        try:
            school_state = kp_check_promise(planets, houses, 4, {2, 4, 9, 11}, {6, 8, 12}).get("state")
        except Exception:
            school_state = "unknown"
        add(f"Overall schooling: {school_state}")
    
        try:
            higher_state = kp_check_promise(planets, houses, 9, {5, 9, 11}, {6, 8, 12}).get("state")
        except Exception:
            higher_state = "unknown"
        add(f"Higher education: {higher_state}")
    
        if nipuna_flag:
            add("Intellect: Nipuna-like intelligence signalled (Sun+Mercury or Mercury strong).")
        elif Mercury and (strong(Mercury) or d9_strength(Mercury) == "strong"):
            add("Intellect: Strong Mercury suggests technical/analytical strengths.")
    
        if score_map.get("Engineering", 0) + score_map.get("Mathematics", 0) + score_map.get("Physics", 0) >= 2:
            add("Competitive exams: Strong technical markers increase chances (Rule 120-121).")
    
        if scholarship_flag:
            add("Scholarship/loan: Conditions indicate institutional funding / scholarship possibilities (see scholarship pointers).")
    
        if foreign_flag:
            add("Foreign study: Indicated (Rahu/12th involvement) — check dashas for timing (Rules 135-138).")
    
        add("Remedies (education-focused): [Use suggest_remedies engine during integration to list tailored secular remedies].")
    
        return out
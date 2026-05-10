from app.core.astro_constants import (
    # --- planet & house access ---
    get_planet,
    normalize_planet,
    get_cusp_sub_lord,
    _lord_of,

    # --- KP signification helpers ---
    get_signified_score,
    get_signified_houses,

    # --- placement / dignity checks ---
    _in_house,
    _is_own_sign,
    _is_exalted,
    _is_retrograde,
    _is_strong_placement,
    _is_strong_in_d9,

    # --- aspect / conjunction ---
    _conjoined,
    _has_evil_aspect,

    # --- KP strength logic ---
    _strong_sig,
    kp_check_promise,

    # --- exchanges ---
    _mutual_exchange,

    # --- strict sub-lord helpers ---
    is_strict_income_sub,
    is_strict_loss_sub,

    # --- remedies ---
    suggest_remedies
)
# ---------------------------
# 1) Strict Classical + KP full evaluator (fires only strong signals)
# ---------------------------
def evaluate_finance_classical_A2_strict(planets, houses, d9=None):
    """
    S1 strict mode: full rulebook but strict firing conditions.
    Returns a flat list of messages (strong signals only).
    """
    out, seen = [], set()
    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    # helpers (wrap existing project helpers)
    def GP(name): return get_planet(name, planets)
    def lord(h): return _lord_of(h, houses)
    def sub_of_cusp(h): return get_cusp_sub_lord(h, houses)
    def sscore(x):
        try: return get_signified_score(x, planets, houses)
        except: return {}
    def shouses(x):
        try: return set(get_signified_houses(x, houses, planets))
        except: return set()

    # strict thresholds / house sets for S1
    WEALTH_HOUSES = {2,5,9,10,11}     # allowed houses considered strong wealth signals
    LOSS_HOUSES   = {6,8,12}          # strong loss/dusthana houses
    CORE_WEALTH   = {2,10,11}         # core income houses (higher weight)
    SIG_THRESH    = 2                 # signification threshold (A2 S1)

    # planets shorthand
    Su, Mo = GP("Sun"), GP("Moon")
    Me, Ve, Ma = GP("Mercury"), GP("Venus"), GP("Mars")
    Ju, Sa = GP("Jupiter"), GP("Saturn")
    Ra, Ke = GP("Rahu"), GP("Ketu")

    # ---------------------------
    # A. KP CORE — 2nd cusp sub-lord (strict)
    # ---------------------------
    sub2 = sub_of_cusp(2)
    if sub2:
        s2 = sscore(sub2)
        # strong income connection
        if _strong_sig(s2, CORE_WEALTH, threshold=SIG_THRESH):
            add("KP-13 ✅ CSL(2) strongly ties to core income houses (2/10/11) — robust finance promise.")
        # strong drain
        if _strong_sig(s2, LOSS_HOUSES, threshold=SIG_THRESH):
            add("KP-6 ⚠ CSL(2) strongly links to 6/8/12 — strong expense/loan pressure.")

    # ---------------------------
    # B. KP per-planet strict checks (sub-lord & star-lord strong connections)
    # ---------------------------
    for pname in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]:
        p = GP(pname)
        if not p: 
            continue

        # sub-lord strict: require signified score >= SIG_THRESH on core houses
        sub = normalize_planet(p.get("sub_lord"))
        if sub:
            sub_score = sscore(sub)
            if _strong_sig(sub_score, CORE_WEALTH, threshold=SIG_THRESH):
                if not _has_evil_aspect(p):
                    add(f"KP-11 💠 {pname}: sub-lord strongly signifies core income (2/10/11) — likely gain in its dasa.")
                else:
                    add(f"KP-11 ⚠ {pname}: sub-lord strongly signifies income but {pname} is afflicted — benefit reduced.")
            if _strong_sig(sub_score, LOSS_HOUSES, threshold=SIG_THRESH):
                add(f"KP-6/7 ⚠ {pname}: sub-lord strongly signifies 6/8/12 — loan/loss tendency in its period.")

        # star-lord strict: require star-lord planet itself to be in a strong house
        star = normalize_planet(p.get("nakshatra_lord"))
        if star:
            st_obj = GP(star)
            if st_obj and _is_strong_placement(st_obj, LOSS_HOUSES):
                add(f"KP-9 ⚠ {pname}: in star of an 8th-lord (strong) — sudden drains / loan themes.")
            if st_obj and _is_strong_placement(st_obj, CORE_WEALTH):
                add(f"KP-1 ✅ {pname}: in star of a core-income planet (2/10/11) — strong finance giver.")

    # KP ledger-nil strict: planet ruling both 8 and 11 (clear alternating)
    for pname in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]:
        # compute lordships robustly
        lords = [h for h in range(1,13) if _lord_of(h, houses) == pname]
        if (8 in lords) and (11 in lords):
            add(f"KP-8 ⚖ {pname} rules both 8 & 11 → alternating profit & drain (ledger-NIL) — strong mixed outcome.")

    # ---------------------------
    # C. Classical Wealth Yogas (strict)
    # ---------------------------
    # W-1: Lords 2/6/11 in Kendra/Kona — require all three in strong houses (1,4,7,10)
    try:
        L2n, L6n, L11n = _lord_of(2, houses), _lord_of(6, houses), _lord_of(11, houses)
        L2obj = GP(L2n) if L2n else None
        L6obj = GP(L6n) if L6n else None
        L11obj = GP(L11n) if L11n else None
        if L2obj and L6obj and L11obj and all(_in_house(x, 1) or _in_house(x,4) or _in_house(x,7) or _in_house(x,10) for x in (L2obj, L6obj, L11obj)):
            add("W-1 💰 Lords 2,6,11 strongly placed in Kendra/Kona → robust prosperity yoga.")
    except Exception:
        pass

    # W-2: 2,10,11 colocated (strict: exact same house)
    try:
        L10n = _lord_of(10, houses)
        if L2n and L10n and L11n:
            if GP(L2n) and GP(L10n) and GP(L11n) and GP(L2n).get("house") == GP(L10n).get("house") == GP(L11n).get("house"):
                add("W-2 🏢 Lords 2/10/11 colocated in same house → powerful professional/income concentration.")
    except Exception:
        pass

    # W-6: Four or more dignified planets (own sign or exalted) — keep as-is (strong by nature)
    dignified = 0
    for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        p = GP(pn)
        if p and (_is_own_sign(p) or _is_exalted(p)):
            dignified += 1
    if dignified >= 4:
        add("W-6 🌟 Four+ dignified planets (own/exaltation) → strong financial independence capacity.")

    # W-7 Moon + Mars conjunction — strict: require conjunction AND one lies in WEALTH_HOUSES
    if Mo and Ma and _conjoined(Mo, Ma) and (_is_strong_placement(Mo, WEALTH_HOUSES) or _is_strong_placement(Ma, WEALTH_HOUSES)):
        add("W-7 🔥 Moon+Mars conjunct with strong placement → initiative, property/real-estate gains likely.")

    # W-17 Jupiter+Mercury in 2 (strict)
    if Ju and Me and _in_house(Ju,2) and _in_house(Me,2):
        add("W-17 📚 Jupiter+Mercury in 2 (both) → strong trade/teaching/commerce wealth.")

    # W-15 (2↔11 exchange) strict: both exchanges must be present
    if _mutual_exchange(2,11,houses,planets):
        add("W-15 🔁 Mutual exchange 2↔11 → consistent gains & cashflow (strong).")

    # W-21 Rahu in 10/11 strict
    if Ra and (_in_house(Ra,10) or _in_house(Ra,11)):
        add("W-21 🌍 Rahu strongly placed in 10/11 → foreign/tech/speculative income emphasis (strong).")

    # W-30: Moon signified support to 2/11 — strict (threshold)
    mo_sign_score = sscore("Moon")
    if _strong_sig(mo_sign_score, {2,11}, threshold=SIG_THRESH):
        add("W-30 🌕 Moon strongly supports 2/11 → potential sudden monetary rise window.")

    # ---------------------------
    # D. Strong Loss / Poverty signals (strict)
    # ---------------------------
    # L-1: Lords 1/4/9 all in 8th
    try:
        l1n, l4n, l9n = _lord_of(1, houses), _lord_of(4, houses), _lord_of(9, houses)
        if l1n and l4n and l9n and GP(l1n) and GP(l4n) and GP(l9n) and all(_in_house(GP(x),8) for x in (l1n,l4n,l9n)):
            add("L-1 💀 Lords 1,4,9 all in 8th → extreme poverty / persistent drain (strong).")
    except Exception:
        pass

    # L-2: 2nd-lord in 12 strict
    L2obj = GP(_lord_of(2, houses)) if _lord_of(2, houses) else None
    if L2obj and _in_house(L2obj, 12):
        add("L-2 ⚠ 2nd-lord strongly placed in 12 → major reversal of wealth (strong).")

    # L-10: Malefics in 8/12 afflicting 2 (strict: malefic in 8/12 AND strong signification to 2)
    for mname in ["Mars","Saturn","Rahu","Ketu"]:
        mp = GP(mname)
        if mp and mp.get("house") in LOSS_HOUSES:
            # check whether this planet signified house-2 strongly (threat to income)
            ms = sscore(mname)
            if _strong_sig(ms, {2}, threshold=1):  # if it signified 2 even weakly, it's dangerous
                add(f"L-10 ❌ {mname} in {mp.get('house')} and strongly affecting 2 → destroys earning capacity (strong).")

    # ---------------------------
    # E. Recovery / Property / Misc (strict cases only)
    # ---------------------------
    # R-1: 7th-lord in 2
    L7n = _lord_of(7, houses)
    if L7n and GP(L7n) and _in_house(GP(L7n), 2):
        add("R-1 🔄 7th-lord in 2 → strong recovery/repayment via partner/alliance.")

    # P-1: 8th sub -> 2/11 (inheritance) strict
    sub8 = sub_of_cusp(8)
    if sub8:
        s8 = sscore(sub8)
        if _strong_sig(s8, {2,11}, threshold=SIG_THRESH):
            add("P-1 🏡 8th-sub strongly signifies 2/11 → inheritance/insurance/PF discharge likely in that period.")

    # Fortuna / D9 strong support (only if D9 helper present)
    try:
        if d9:
            L11n = _lord_of(11, houses)
            if L11n and _is_strong_in_d9(L11n, d9):
                add("Fortuna ✨ Strong 11th-lord in D9 → reinforced income (D1+D9 match).")
    except Exception:
        pass

    # ---------------------------
    # F. Planetary role lines — keep (concise)
    # ---------------------------
    add("Source ☀ Sun → government/authority income.")
    add("Source 🌙 Moon → liquid/consumables/foreign-related income.")
    add("Source 🧾 Mercury → trade, commissions, paperwork.")
    add("Source 🕉 Jupiter → property, education, expansion.")
    add("Source 💎 Venus → luxury, vehicles, beauty trades.")
    add("Source ⛏ Saturn → long-term rentals, land, labor income.")
    add("Source 🌪 Rahu → foreign/tech/speculative channels.")
    add("Source 🕯 Ketu → ancestral/karmic/inheritance-type gains.")

    # ---------------------------
    # G. Final strong summary / tidy up
    # ---------------------------
    # If many wealth items exist, add a compact summary line (optional)
    wealth_count = sum(1 for item in out if item.startswith(("KP-13","W-","P-1","Fortuna","KP-1","KP-11","Source","W-15")))
    loss_count = sum(1 for item in out if item.startswith(("L-","KP-6","KP-15","E","L-10")))
    if wealth_count and loss_count == 0:
        add("Summary ✅ Strong wealth indicators dominate in strict mode.")
    elif wealth_count and loss_count:
        add("Summary ⚖ Mixed but with strong signals on both wealth and risk — consult periods for timing.")
    elif loss_count and wealth_count == 0:
        add("Summary ⚠ Strong loss/drain indicators dominate in strict mode.")

    return out


# ---------------------------
# 2) Strict Borrowing engine (A2 S1)
# ---------------------------
def evaluate_borrowing_A2_strict(planets, houses):
    """
    Borrowing analysis with strict firing logic (S1).
    Returns flat list of strong borrowing / repayment indicators.
    """
    out, seen = [], set()
    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    def GP(n): return get_planet(n, planets)
    def lord(h): return _lord_of(h, houses)
    def sub(h): return get_cusp_sub_lord(h, houses)
    def sscore(x):
        try: return get_signified_score(x, planets, houses)
        except: return {}

    # thresholds / strong house sets
    LOSS_HOUSES = {6,8,12}
    REPAY_HOUSES = {2,10,11}
    SIG_THRESH = 2

    # core summary
    add("Borrow-House mapping (strong checks): 2=cash, 6=loan, 8=lender/trouble, 10=profession receipts, 11=repayment, 12=expenses.")

    # 1) 6th-cusp sub-lord strong -> borrow
    s6 = sub(6)
    if s6:
        s6s = sscore(s6)
        if _strong_sig(s6s, LOSS_HOUSES, threshold=SIG_THRESH):
            add("A1 📌 Strong 6th-sub -> strongly signifies 6/8/12 → likely borrowing due to illness/expense/loss (strict).")

    # 2) 2nd-lord strong tie to loss houses -> borrow
    L2n = lord(2)
    if L2n:
        L2s = sscore(L2n)
        if _strong_sig(L2s, LOSS_HOUSES, threshold=SIG_THRESH):
            add("A2 📌 Strong 2nd-lord -> ties to 6/8/12 → borrowing for family/partner/children due to strong drain signals.")

    # 3) 5th/9th/10th strong ties -> particular causes
    L5n = lord(5)
    if L5n and _strong_sig(sscore(L5n), LOSS_HOUSES, threshold=SIG_THRESH):
        add("A5 👶 Lord-5 strongly linked to 6/8/12 → speculation/children-driven borrowing (strict).")
    L9n = lord(9)
    if L9n and _strong_sig(sscore(L9n), LOSS_HOUSES, threshold=SIG_THRESH):
        add("A7 👨‍👧 Lord-9 strongly ties to loss houses → father/foreign/journey-driven borrowings (strict).")
    L10n = lord(10)
    if L10n and _strong_sig(sscore(L10n), LOSS_HOUSES, threshold=SIG_THRESH):
        add("A8 💼 Lord-10 strongly ties to loss houses → business liabilities / forced borrowing (strict).")

    # 4) Repayment signals: 8th-sub strongly to repay houses
    s8 = sub(8)
    if s8 and _strong_sig(sscore(s8), REPAY_HOUSES, threshold=SIG_THRESH):
        add("C2 📌 8th-sub strongly signifies 2/10/11 → repayment/discharge likely during that sub-period (strict).")

    # 5) Easy loan conditions (strict placement of benefics in 2/10/11)
    for nm in ["Jupiter","Venus","Mercury","Moon"]:
        p = GP(nm)
        if p and _is_strong_placement(p, {2,10,11}):
            add(f"B1 ✔ {nm} strongly placed in {p.get('house')} → easier loan access (strict).")

    # 6) Difficulties in repayment (malefics in 4/8/12, strict)
    for nm in ["Mars","Saturn","Rahu","Ketu","Sun"]:
        p = GP(nm)
        if p and _is_strong_placement(p, {4,8,12}):
            add(f"B3 ❌ {nm} strongly in {p.get('house')} → repayment obstruction / lender trouble (strict).")

    # 7) Chronic Dharidra (only very strong patterns)
    # Example: Parivartana 1<->12 plus L1 connected to 7
    if _mutual_exchange(1,12,houses,planets):
        L1n = lord(1)
        if L1n:
            L1s = sscore(L1n)
            if _strong_sig(L1s, {7}, threshold=1):  # if lagna-lord has strong tie to 7 while exchange exists
                add("E1 🔁 Strong Dharidra: L1↔L12 exchange + L1↔7 -> persistent borrowing pattern (strict).")

    # 8) Moon+Ketu in 5 conjunction (strict)
    Mo = GP("Moon"); Ke = GP("Ketu")
    if Mo and Ke and _conjoined(Mo, Ke) and _is_strong_placement(Mo, {5}):
        add("E6 🧠 Moon+Ketu in 5 (strong) → mental planning to borrow; unstable cashflow (strict).")

    # Remedies (strictly include if any strong remedial suggestions exist)
    try:
        rems = suggest_remedies("Borrowing", "observed", sub(6), houses)
        if rems:
            add("Remedies 🕉 Borrowing-specific (strict):")
            for r in rems:
                add(f" - {r}")
    except Exception:
        pass

    return out


def evaluate_house_purchase_strict(planets, houses, d9=None):
    """
    STRICT MODE (S1): Property / House Purchase Evaluation
    """

    out, seen = [], set()
    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    def GP(n): 
        return get_planet(n, planets)

    def sc(x):
        try:
            return get_signified_score(x, planets, houses)
        except:
            return {}

    # -----------------------
    # Core KP Promise — CSL(4)
    # -----------------------
    sub4 = get_cusp_sub_lord(4, houses)
    ss = sc(sub4)

    if is_strict_income_sub(sub4, planets, houses):
        add("🏡 CSL(4) strongly connects with 2/4/11 → Property purchase strongly promised.")

    elif is_strict_loss_sub(sub4, planets, houses):
        add("⚠ CSL(4) strongly linked with 6/8/12 → purchase via loan or delays.")

    else:
        add("❓ CSL(4) weak → uncertain or late property purchase.")

    # -----------------------
    # Classical Strong Rules
    # -----------------------
    for p in ("Jupiter", "Venus"):
        obj = GP(p)
        if obj and obj.get("house") == 4:
            add(f"🌿 {p} in 4 → strong classical property support.")

    r = GP("Rahu")
    if r and r.get("house") in {4, 10}:
        add("🌍 Rahu influencing 4/10 → foreign / irregular property source.")

    for p in ("Mars", "Saturn"):
        obj = GP(p)
        if obj and obj.get("house") == 4:
            add(f"🏗 {p} in 4 → construction / land-linked property.")

    # -----------------------
    # STRICT 2 → 4 → 11 Chain
    # -----------------------
    if (
        ss.get(2, 0) >= 2 and
        ss.get(4, 0) >= 2 and
        ss.get(11, 0) >= 2
    ):
        add("💰 Strong 2→4→11 chain → funding + ownership + gains (strict).")

    # -----------------------
    # Inheritance / Loan
    # -----------------------
    sub8 = get_cusp_sub_lord(8, houses)
    s8 = sc(sub8)
    if s8.get(2, 0) >= 2 or s8.get(11, 0) >= 2:
        add("🏛 8th-sub strongly to 2/11 → inherited or family property.")

    sub6 = get_cusp_sub_lord(6, houses)
    if is_strict_loss_sub(sub6, planets, houses):
        add("🏦 Property purchase via loan / mortgage indicated.")

    return out

def evaluate_vehicle_purchase_strict(planets, houses, d9=None):
    """
    STRICT MODE (S1): Vehicle Purchase / Ownership Evaluation
    """

    out, seen = [], set()
    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    def GP(n):
        return get_planet(n, planets)

    def sc(x):
        try:
            return get_signified_score(x, planets, houses)
        except:
            return {}

    # -----------------------
    # Core KP Promise — CSL(3)
    # -----------------------
    sub3 = get_cusp_sub_lord(3, houses)
    ss = sc(sub3)

    if is_strict_income_sub(sub3, planets, houses):
        add("🚗 CSL(3) strongly connects with 2/3/11 → Vehicle purchase strongly promised.")

    elif is_strict_loss_sub(sub3, planets, houses):
        add("⚠ CSL(3) strongly linked with 6/8/12 → loan-based or delayed vehicle.")

    else:
        add("❓ CSL(3) weak → uncertain or delayed vehicle acquisition.")

    # -----------------------
    # Classical Vehicle Rules
    # -----------------------
    if GP("Venus") and GP("Venus").get("house") in {3, 4, 11}:
        add("✨ Venus influence → comfort / luxury vehicle.")

    if GP("Moon") and GP("Moon").get("house") == 4:
        add("🌙 Moon in 4 → comfort-oriented vehicle.")

    for p in ("Mars", "Saturn"):
        obj = GP(p)
        if obj and obj.get("house") in {3, 4, 10}:
            add(f"🚚 {p} influence → utility / commercial vehicle.")

    r = GP("Rahu")
    if r and r.get("house") in {3, 4, 11}:
        add("🌍 Rahu influence → imported / foreign vehicle.")

    # -----------------------
    # STRICT 2 → 3 → 11 Chain
    # -----------------------
    if (
        ss.get(2, 0) >= 2 and
        ss.get(3, 0) >= 2 and
        ss.get(11, 0) >= 2
    ):
        add("💰 Strong 2→3→11 chain → purchase + ownership + repayment.")

    # -----------------------
    # Loan / EMI
    # -----------------------
    sub6 = get_cusp_sub_lord(6, houses)
    if is_strict_loss_sub(sub6, planets, houses):
        add("🏦 Loan / EMI involvement strongly indicated.")

    # -----------------------
    # Accident / Repair Risk
    # -----------------------
    if sub3 in {"Mars", "Saturn", "Rahu", "Ketu"} and ss.get(8, 0) >= 2:
        add("⚠ Elevated accident / repair risk (strict).")

    # -----------------------
    # Foreign / Imported Trigger
    # -----------------------
    if sub3 in {"Rahu", "Ketu"} or ss.get(12, 0) >= 2:
        add("🌐 Imported / foreign-origin vehicle expected.")

    # -----------------------
    # Dual Confirmation
    # -----------------------
    if (
        is_strict_income_sub(sub3, planets, houses) and
        ss.get(2, 0) >= 2 and
        ss.get(3, 0) >= 2 and
        ss.get(11, 0) >= 2
    ):
        add("🏆 Dual confirmation → vehicle purchase highly likely.")

    return out


def evaluate_finance(planets, houses, d9=None):
    """
    FINAL STRICT FINANCE ENGINE (S1) — KP CORRECT

    Finance modes:
        - wealth      → self-funded prosperity
        - mixed       → income + stress
        - loan_only   → assets only via loan / EMI
        - unknown     → unclear promise

    Assets are ALWAYS allowed,
    but their NATURE depends on finance mode.
    """

    out, seen = [], set()

    def add(msg):
        if msg and msg not in seen:
            out.append(msg)
            seen.add(msg)

    # -------------------------------------------------
    # 0) KP BASE VERDICT → FINANCE MODE
    # -------------------------------------------------
    sub2 = get_cusp_sub_lord(2, houses)

    verdict = kp_check_promise(
        planets=planets,
        houses=houses,
        csl_house=2,
        promise_houses={2,6,10,11},
        obstacle_houses={6,8,12}
    )

    mp = verdict.get("state", "").strip().lower()

    if mp == "promised":
        finance_mode = "wealth"
        add("✅ Financial prosperity promised — self-funded growth supported.")

    elif mp == "promised_with_obstacles":
        finance_mode = "mixed"
        add("⚖️ Finance promised with stress — income exists but drains present.")

    elif mp == "blocked":
        finance_mode = "loan_only"
        add("❌ Financial prosperity blocked — income drains dominate.")
        add("💳 Assets possible mainly through loans / EMI, not savings.")

    else:
        finance_mode = "unknown"
        add("❓ Financial promise unclear from 2nd-cusp sub-lord.")

    # -------------------------------------------------
    # 1) Small Strict KP Extras
    # -------------------------------------------------
    Sa = get_planet("Saturn", planets)
    Ju = get_planet("Jupiter", planets)

    if Sa and Sa.get("house") in {1,3,5,7,10}:
        add("🐢 Saturn influence → slow, effort-based financial progress.")

    if Ju and Ju.get("retro"):
        add("🐢 Retrograde Jupiter → delays in approvals or financial expansion.")

    # -------------------------------------------------
    # 2) STRICT CLASSICAL FINANCE LOGIC
    # -------------------------------------------------
    try:
        classical_points = evaluate_finance_classical_A2_strict(planets, houses, d9)
        for p in classical_points:
            add(p)
    except Exception as e:
        add(f"[Error in classical finance evaluator: {e}]")

    # -------------------------------------------------
    # 3) REMEDIES (FINANCE ONLY)
    # -------------------------------------------------
    try:
        rems = suggest_remedies("Finance", finance_mode, sub2, houses)
        if rems:
            add("--- Remedies (Finance) ---")
            for r in rems:
                add(f" - {r}")
    except:
        pass

    # -------------------------------------------------
    # 4) STRICT BORROWING / LOAN ANALYSIS
    # -------------------------------------------------
    try:
        borrowing_points = evaluate_borrowing_A2_strict(planets, houses)
        if borrowing_points:
            add("--- Borrowing / Loan Indicators (strict) ---")
            for b in borrowing_points:
                add(f" - {b}")
    except:
        pass

    # -------------------------------------------------
    # 5) ASSETS (PROPERTY + VEHICLE) — MODE AWARE
    # -------------------------------------------------
    try:
        house_points = evaluate_house_purchase_strict(planets, houses, d9)
        vehicle_points = evaluate_vehicle_purchase_strict(planets, houses, d9)

        if house_points or vehicle_points:
            add("--- Asset Indicators ---")

        # -------- PROPERTY --------
        if house_points:
            add("• Property:")
            for hp in house_points:
                if finance_mode == "loan_only":
                    add(f"   - {hp} (primarily loan / EMI based)")
                elif finance_mode == "mixed":
                    add(f"   - {hp} (possible with financial stress)")
                else:
                    add(f"   - {hp}")

        # -------- VEHICLE --------
        if vehicle_points:
            add("• Vehicle:")
            for vp in vehicle_points:
                if finance_mode == "loan_only":
                    add(f"   - {vp} (primarily loan / EMI based)")
                elif finance_mode == "mixed":
                    add(f"   - {vp} (possible with financial stress)")
                else:
                    add(f"   - {vp}")

    except Exception as e:
        add(f"[Error in asset evaluator: {e}]")

    return out
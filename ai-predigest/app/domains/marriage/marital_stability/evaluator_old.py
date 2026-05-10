"""
Marital Stability Evaluator

Evaluates factors affecting marital stability including:
- Benefic/malefic influences on 7th house
- 7th lord condition
- Rahu-Ketu axis impact
- Venus-Moon-Jupiter harmony
- Divorce/separation indicators
- Happy/Unhappy marriage indicators (R3_x, R4_x)
- Physical union compatibility (R7_x)
"""
from typing import Dict, List, Any, Set, Optional

from app.domains.base import (
    BaseEvaluator, EvaluationResult, Question, QueryMeta,
    QueryType, EventPolarity, InterpretationGoal
)
from app.core.astro_constants import (
    normalize_planet_name, normalize_planet, get_planet, _p,
    _in_house, _in_houses, _in_sign, _conjoined, _lord_of,
    _aspected_by, has_harmonious_aspect, has_harsh_aspect, _has_evil_aspect, _has_good_aspect,
    _is_benefic, _is_malefic, _is_retrograde, _is_own_sign,
    _is_exalted, _is_debilitated, detect_aspects,
    get_signified_houses, get_signified_score,
    _house_has_benefic_occupation, _benefic_by_lordship_of_house, _is_strong_planet,
    BENEFICS, MALEFICS
)


class MaritalStabilityEvaluator(BaseEvaluator):
    """
    Evaluator for Marital Stability subtopic.
    
    Analyzes:
    - Overall marital happiness promise (R3_x)
    - Unhappy marriage indicators (R4_x)
    - Physical union compatibility (R7_x)
    - Separation/divorce risk factors
    - Dosha patterns (Manglik, Kuja, etc.)
    """
    
    domain = "Marriage"
    subtopic = "Marital Stability"
    
    # KP house significations for stability
    positive_houses = {2, 7, 11}  # Marriage sustaining houses
    supportive_houses = {4, 5}    # Family, love, comfort
    negative_houses = {6, 8, 12}  # Separation, obstacles, loss
    
    # Key planets for marital stability
    key_planets = {"Venus", "Jupiter", "Moon", "Saturn"}
    
    def evaluate(
        self,
        planets: Dict[str, Dict],
        houses: List[Dict],
        **kwargs
    ) -> EvaluationResult:
        """
        Main evaluation for marital stability factors.
        """
        self.reset()
        planets = detect_aspects(planets)
        result = EvaluationResult()
        
        # 1. Happy Marriage Indicators (R3_x)
        happy_points = self._evaluate_happy_marriage(planets, houses)
        result.extend_points(happy_points)
        
        # 2. Unhappy Marriage Indicators (R4_x)
        unhappy_points = self._evaluate_unhappy_marriage(planets, houses)
        result.extend_points(unhappy_points)
        
        # 3. Physical Union Compatibility (R7_x)
        union_points = self._evaluate_physical_union(planets, houses)
        result.extend_points(union_points)
        
        # 4. Separation/Divorce Risk Analysis
        separation_result = self._evaluate_separation_risk(planets, houses)
        result.extend_points(separation_result["points"])
        result.additional_data["separation_severity"] = separation_result["severity"]
        
        # 5. Book-4 Divorce/Separation Rules (R6, R_sep, B4_R1-R9)
        book_rules_points = self._evaluate_divorce_separation_book_rules(planets, houses)
        result.extend_points(book_rules_points)
        
        # 6. Dosha Analysis
        dosha_points = self._evaluate_doshas(planets, houses)
        result.extend_points(dosha_points)
        
        # 7. Overall Assessment
        overall = self._calculate_overall_stability(planets, houses)
        result.additional_data["stability_score"] = overall["score"]
        result.add_point(overall["verdict"])
        
        return result
    
    def _evaluate_happy_marriage(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Happy Married Life Indicators (R3_x).
        
        Based on notebook's evaluate_marriage_classical() R3 section.
        """
        points = []
        
        # Get planets
        Mo = _p(planets, "Moon")
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Su = _p(planets, "Sun")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        c7_star = normalize_planet(cusp7.get("start_nakshatra_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        lord11 = _lord_of(11, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # =============================================================
        # R3-1: 7th sub-lord is Jupiter/Venus AND signifies 2 or 11
        # =============================================================
        if c7sub in {"Jupiter", "Venus"}:
            sc = get_signified_score(c7sub, planets, houses)
            if sc.get(2, 0) > 0 or sc.get(11, 0) > 0:
                points.append("💚 7th sub-lord is Jupiter/Venus signifying 2/11 → happy married life [R3_1]")
        
        # =============================================================
        # R3-2: Mercury/Moon/Sun significator of 7 with 11th lord aspect
        # =============================================================
        if lord11:
            L11p = _p(planets, lord11)
            for cand_name in ["Mercury", "Moon", "Sun"]:
                cand = _p(planets, cand_name)
                if cand and get_signified_score(cand_name, planets, houses).get(7, 0) > 0:
                    if L11p and has_harmonious_aspect(L11p, cand_name):
                        points.append(f"💚 {cand_name} is significator of 7 with benefic 11th lord aspect → happy life [R3_2]")
        
        # =============================================================
        # R3-3: Sun & Moon in 7 with mutual good aspect
        # =============================================================
        if _in_house(Su, 7) and _in_house(Mo, 7):
            if has_harmonious_aspect(Su, "Moon") and has_harmonious_aspect(Mo, "Sun"):
                points.append("💚 Sun & Moon in 7th with mutual good aspect → affectionate & happy union [R3_3]")
        
        # =============================================================
        # R3-4: Luminary in 7 aspected by Jupiter/Venus signifying 2/11
        # =============================================================
        for lum, tag in [(Su, "Sun"), (Mo, "Moon")]:
            if _in_house(lum, 7):
                for p_name in ("Jupiter", "Venus"):
                    p_score = get_signified_score(p_name, planets, houses)
                    if (p_score.get(2, 0) + p_score.get(11, 0)) > 0:
                        if has_harmonious_aspect(lum, p_name):
                            points.append(f"💚 {tag} in 7th aspected by {p_name} (signifies 2/11) → strong partnership [R3_4]")
        
        # =============================================================
        # R3-5: Venus & Mars in good aspect, not significators of 6/10/12
        # =============================================================
        if has_harmonious_aspect(Ve, "Mars") or has_harmonious_aspect(Ma, "Venus"):
            ve_score = get_signified_score("Venus", planets, houses)
            ma_score = get_signified_score("Mars", planets, houses)
            ve_bad = ve_score.get(6, 0) + ve_score.get(10, 0) + ve_score.get(12, 0)
            ma_bad = ma_score.get(6, 0) + ma_score.get(10, 0) + ma_score.get(12, 0)
            if ve_bad == 0 and ma_bad == 0:
                points.append("💚 Venus & Mars in good aspect, not signifying 6/10/12 → pleasurable union [R3_5]")
        
        # =============================================================
        # R3-6: Moon receives benefic aspect (Saturn/Venus/Jupiter)
        # =============================================================
        if any(has_harmonious_aspect(Mo, p) for p in ("Saturn", "Venus", "Jupiter")):
            points.append("💚 Moon receives benefic aspect → emotional happiness [R3_6]")
        
        # =============================================================
        # R3-7: 7th supported by benefics (occupation/lordship)
        # =============================================================
        if _house_has_benefic_occupation(7, houses) or _benefic_by_lordship_of_house(7, houses):
            points.append("💚 7th house supported by benefics (occupation/lordship) [R3_7]")
        
        # =============================================================
        # R3_star: 7th cusp star-lord benefic
        # =============================================================
        if c7_star and c7_star in BENEFICS:
            points.append("💚 7th cusp star-lord is benefic → emotional happiness [R3_star]")
        
        # =============================================================
        # Venus strong in 7th
        # =============================================================
        if _in_house(Ve, 7) and _is_strong_planet(Ve, planets):
            points.append("💚 Venus strong in 7th house [R3_Venus]")
        
        # =============================================================
        # R3_mixed: Mixed aspects indicator
        # =============================================================
        key_targets = [Ve, L7, Mo]
        good_hits = sum(1 for p in key_targets if p and _has_good_aspect(p))
        bad_hits = sum(1 for p in key_targets if p and _has_evil_aspect(p))
        
        kp_mixed = False
        if c7sub:
            s = get_signified_score(c7sub, planets, houses)
            kp_mixed = (s.get(2, 0) + s.get(7, 0) + s.get(11, 0) >= 2) and \
                       (s.get(6, 0) + s.get(8, 0) + s.get(12, 0) >= 2)
        
        if (good_hits >= 1 and bad_hits >= 1) or kp_mixed:
            points.append("💠 Mixed aspects: enjoyment, with temporary dissatisfaction during malefic periods [R3_mixed]")
        
        return points
    
    def _evaluate_unhappy_marriage(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Unhappy Married Life Indicators (R4_x).
        
        Based on notebook's evaluate_marriage_classical() R4 section.
        """
        points = []
        
        # Get planets
        Mo = _p(planets, "Moon")
        Ve = _p(planets, "Venus")
        Su = _p(planets, "Sun")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        # Get scores
        su_score = get_signified_score("Sun", planets, houses)
        mo_score = get_signified_score("Moon", planets, houses)
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # =============================================================
        # R4-1: Sun-Moon conflict in marriage houses
        # =============================================================
        su_sig = set(k for k, v in su_score.items() if v > 0)
        mo_sig = set(k for k, v in mo_score.items() if v > 0)
        if _in_house(Su, 7) and _aspected_by(Su, "Moon"):
            if ({2, 7, 11} & su_sig) or ({2, 7, 11} & mo_sig):
                points.append("💢 Sun-Moon conflict in marriage houses [R4_1]")
        
        # =============================================================
        # R4-2-3: Malefics harming 7th with evil aspect
        # =============================================================
        for m in MALEFICS:
            mp = _p(planets, m)
            if _in_house(mp, 7) and _has_evil_aspect(mp):
                points.append(f"💢 {m} harming 7th house [R4_2-3]")
                break  # Only report once
        
        # =============================================================
        # R4-9: Mercury afflicted in 7 → miscommunication
        # =============================================================
        if _in_house(Me, 7):
            if any(_aspected_by(Me, x) for x in {"Moon", "Mars", "Saturn", "Rahu", "Ketu"}):
                points.append("💢 Mercury afflicted in 7th → miscommunication [R4_9]")
        
        # =============================================================
        # R4-10-11: 7th cusp afflicted by 6/8/12 (score >= 3)
        # =============================================================
        if c7sub:
            s7 = get_signified_score(c7sub, planets, houses)
            if s7.get(6, 0) + s7.get(8, 0) + s7.get(12, 0) >= 3:
                points.append("💢 7th cusp sub-lord heavily afflicted by 6/8/12 signification [R4_10-11]")
        
        # =============================================================
        # R4-6: Moon-Jupiter disharmony
        # =============================================================
        if has_harsh_aspect(Mo, "Jupiter"):
            if mo_score.get(7, 0) >= 1 or su_score.get(7, 0) >= 1:
                points.append("💢 Moon-Jupiter disharmony → emotional dissatisfaction [R4_6]")
        
        # =============================================================
        # R4-7: Mars in 8 (Jupiter sub) → financial trouble
        # =============================================================
        mars_sub = normalize_planet(Ma.get("sub_lord")) if Ma else None
        if _in_house(Ma, 8) and mars_sub == "Jupiter":
            points.append("💢 Mars in 8th (Jupiter sub) → financial trouble in marriage [R4_7]")
        
        # =============================================================
        # R4-8: Mars in 8 (Moon sub) → temper, addiction
        # =============================================================
        if _in_house(Ma, 8) and mars_sub == "Moon":
            points.append("💢 Mars in 8th (Moon sub) → temper issues, possible addiction [R4_8]")
        
        # =============================================================
        # R4_combo: Venus + 7th lord both afflicted
        # =============================================================
        if _has_evil_aspect(Ve) and L7 and has_harsh_aspect(L7, "Saturn"):
            points.append("💢 Venus + 7th lord both afflicted → serious marital stress [R4_combo]")
        
        return points
    
    def _evaluate_physical_union(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Physical Union Compatibility (R7_x).
        
        Based on notebook's evaluate_marriage_classical() R7 section.
        """
        points = []
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        c7_star = normalize_planet(cusp7.get("start_nakshatra_lord", ""))
        
        # Lords
        lord7 = _lord_of(7, houses)
        L7 = _p(planets, lord7) if lord7 else None
        
        # =============================================================
        # R7_union: Union quality based on 7th star-lord or sub-lord
        # =============================================================
        union_map = {
            "Sun": "repulsion",
            "Moon": "pleasant/honeymoon",
            "Mars": "friction",
            "Mercury": "playful desire",
            "Jupiter": "normal/pleasant",
            "Venus": "romantic/joyful",
            "Saturn": "cold/low pleasure"
        }
        
        union = union_map.get(c7_star) or union_map.get(c7sub)
        if union:
            source = c7_star if c7_star in union_map else c7sub
            points.append(f"💗 Physical union quality: {union} (from {source}) [R7_union]")
        
        # =============================================================
        # R7_L7: 7th lord in 5/11 → strong compatibility
        # =============================================================
        if L7 and L7.get("house") in {5, 11}:
            points.append("💗 7th lord in 5th/11th → strong compatibility & satisfaction [R7_L7]")
        
        return points
    
    def _evaluate_separation_risk(self, planets: Dict, houses: List) -> Dict[str, Any]:
        """
        Evaluate separation/divorce risk factors.
        
        Based on notebook's evaluate_separation_risk() function.
        Returns dict with 'points' list and 'severity' rating.
        """
        risk_factors = []
        
        # Get planets
        Ve = _p(planets, "Venus")
        Ma = _p(planets, "Mars")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        Mo = _p(planets, "Moon")
        
        # 7th lord
        lord7 = _lord_of(7, houses)
        L7p = _p(planets, lord7) if lord7 else None
        
        MALEFIC_NAMES = ("Mars", "Saturn", "Rahu")
        
        # ---------------------------------------------
        # 1. Malefics in 7th or harsh aspect to 7th lord
        # ---------------------------------------------
        for mal in MALEFIC_NAMES:
            mp = _p(planets, mal)
            if not mp:
                continue
            
            # (A) Malefic sitting in 7th
            if _in_house(mp, 7):
                risk_factors.append(f"⚠️ {mal} in 7th house → conflict/separation tendency")
            
            # (B) Malefic harsh aspect to 7th lord
            if L7p and has_harsh_aspect(L7p, mal):
                risk_factors.append(f"⚠️ {mal} harshly aspects 7th lord ({lord7}) → marital disturbances")
        
        # ---------------------------------------------
        # 2. 6th house influence on Venus, Moon, 7th lord
        # ---------------------------------------------
        REL_PLANETS = ["Venus", "Moon"]
        if lord7:
            REL_PLANETS.append(lord7)
        
        for pl in REL_PLANETS:
            sig_houses = get_signified_houses(pl, planets, houses)
            if 6 in sig_houses:
                risk_factors.append(f"⚠️ {pl} connected to 6th house → disputes/separation triggers")
        
        # ---------------------------------------------
        # 3. 7th lord in dusthana
        # ---------------------------------------------
        if L7p and _in_houses(L7p, {6, 8, 12}):
            risk_factors.append("⚠️ 7th lord in dusthana (6/8/12) → challenges in marriage stability")
        
        # ---------------------------------------------
        # 4. Rahu-Ketu axis on 1-7
        # ---------------------------------------------
        if _in_house(Ra, 1) and _in_house(Ke, 7):
            risk_factors.append("⚠️ Rahu-Ketu axis on 1-7 → karmic relationship patterns")
        elif _in_house(Ra, 7) and _in_house(Ke, 1):
            risk_factors.append("⚠️ Rahu in 7th → unconventional partnership, potential instability")
        
        # ---------------------------------------------
        # 5. Saturn afflicting Venus/Moon
        # ---------------------------------------------
        if has_harsh_aspect(Ve, "Saturn"):
            risk_factors.append("⚠️ Saturn afflicts Venus → emotional distance possible")
        if has_harsh_aspect(Mo, "Saturn"):
            risk_factors.append("⚠️ Saturn afflicts Moon → emotional coldness risk")
        
        # ---------------------------------------------
        # Severity Rating
        # ---------------------------------------------
        R = len(risk_factors)
        if R >= 4:
            severity = "High"
        elif R >= 2:
            severity = "Moderate"
        else:
            severity = "Low"
        
        return {
            "points": risk_factors,
            "severity": severity,
            "risk_count": R
        }
    
    def _evaluate_divorce_separation_book_rules(self, planets: Dict, houses: List) -> List[str]:
        """
        Evaluate Book-4 divorce/separation rules.
        
        Implements:
        - R6_certainty_book: Multiple marriages certainty
        - R_sep_full: Separation scoring logic (houses 1,6,10,12)
        - R_divorce_book: Ketu as 7th CSL in dual sign
        - R6_2nd_cusp: Second marriage from 2nd cusp
        - B4_R1 through B4_R9: Star/sub separation and union rules
        """
        points = []
        
        # Helper functions for star/sub extraction
        def _star_of(p):
            if not p:
                return None
            return normalize_planet(p.get("nakshatra_lord"))
        
        def _sub_of(p):
            if not p:
                return None
            return normalize_planet(p.get("sub_lord"))
        
        def is_dual_sign(sign: str) -> bool:
            return sign in {"Gemini", "Virgo", "Sagittarius", "Pisces"}
        
        # Get all planets
        Su = _p(planets, "Sun")
        Mo = _p(planets, "Moon")
        Ma = _p(planets, "Mars")
        Me = _p(planets, "Mercury")
        Ju = _p(planets, "Jupiter")
        Ve = _p(planets, "Venus")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        # Get planet names list
        _planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        
        # Get 7th cusp data
        cusp7 = next((h for h in houses if h.get("house") == 7), {})
        c7sub = normalize_planet(cusp7.get("cusp_sub_lord", ""))
        
        # Get 2nd cusp data
        cusp2 = next((h for h in houses if h.get("house") == 2), {})
        c2sub = normalize_planet(cusp2.get("cusp_sub_lord", ""))
        
        dual_signs = {"Gemini", "Virgo", "Sagittarius", "Pisces"}
        
        # =============================================================
        # R6_certainty_book: Multiple Marriages CERTAIN
        # Book 4, pg.145-146
        # Conditions:
        # 1. 7th cusp sub-lord is in dual sign
        # 2. 7th cusp sub-lord is in star of a node (Rahu/Ketu)
        # 3. That node sits in dual sign
        # =============================================================
        if c7sub:
            sub_p = _p(planets, c7sub)
            if sub_p:
                sub_sign = (sub_p.get("sign") or sub_p.get("rasi") or "").title()
                sub_star = normalize_planet(sub_p.get("nakshatra_lord"))
                
                # Step 1 — CSL in dual sign
                cond1 = sub_sign in dual_signs
                
                # Step 2 — CSL in star of node
                cond2 = sub_star in {"Rahu", "Ketu"}
                
                # Step 3 — Node in dual sign
                node_p = _p(planets, sub_star) if cond2 else None
                node_sign = (node_p.get("sign") or node_p.get("rasi") or "").title() if node_p else None
                cond3 = node_sign in dual_signs
                
                if cond1 and cond2 and cond3:
                    points.append("🔁 **CERTAIN multiple marriages** (CSL dual-sign + node star + node in dual) [R6_certainty_book]")
        
        # =============================================================
        # R_sep_full: Separation Scoring Logic
        # Count planets connected to houses 1,6,10,12
        # =============================================================
        sep_houses = {1, 6, 10, 12}
        sep_connections = 0
        sep_afflicted = 0
        sep_strong_planet_hits = 0
        
        for pname in _planet_names:
            p_obj = _p(planets, pname)
            if not p_obj:
                continue
            
            # (1) Direct occupation
            p_house = p_obj.get("house")
            if isinstance(p_house, int) and p_house in sep_houses:
                sep_connections += 1
                if _has_evil_aspect(p_obj) or has_harsh_aspect(p_obj, "Saturn") or has_harsh_aspect(p_obj, "Mars"):
                    sep_afflicted += 1
                if _is_strong_planet(p_obj, planets):
                    sep_strong_planet_hits += 1
                continue
            
            # (2) Signification — planet signifies any separation houses
            sc = get_signified_score(pname, planets, houses)
            if sc.get(1, 0) + sc.get(6, 0) + sc.get(10, 0) + sc.get(12, 0) > 0:
                sep_connections += 1
                if sc.get(6, 0) + sc.get(12, 0) > 0:
                    # Heavier weight for dusthana connections
                    sep_afflicted += 1
                if _is_strong_planet(p_obj, planets):
                    sep_strong_planet_hits += 1
        
        # Decision thresholds (conservative)
        if sep_connections >= 3:
            points.append(f"💔 Separation risk STRONG — {sep_connections} planets connect with houses 1/6/10/12; {sep_strong_planet_hits} are strong planets [R_sep_full_strong]")
        elif sep_connections == 2 and (sep_afflicted >= 1 or sep_strong_planet_hits >= 1):
            points.append("💔 Separation risk MODERATE — 2 connections + afflicted/strong planet [R_sep_full_moderate]")
        elif sep_connections == 2:
            points.append("💔 Separation risk WEAK — 2 planets connect to separation houses [R_sep_full_weak]")
        
        # =============================================================
        # R_divorce_book: Ketu as 7th CSL in dual sign → divorce
        # =============================================================
        if c7sub == "Ketu":
            ketu_p = _p(planets, "Ketu")
            ketu_sign = (ketu_p.get("sign") or ketu_p.get("rasi") or "").title() if ketu_p else None
            if ketu_sign and is_dual_sign(ketu_sign):
                points.append("💢 Divorce/second-marriage indicated — 7th cusp sub-lord is Ketu in dual sign [R_divorce_book]")
        
        # =============================================================
        # R6_2nd_cusp: Second marriage from 2nd cusp
        # If 2nd cusp sub-lord signifies 7th house → second marriage
        # =============================================================
        if c2sub:
            c2_sc = get_signified_score(c2sub, planets, houses)
            if c2_sc.get(7, 0) > 0:
                points.append("🔁 Second marriage likely — 2nd cusp's sub-lord signifies 7th house [R6_2nd_cusp]")
        
        # =============================================================
        # BOOK-4 Star/Sub Separation and Union Rules (B4_R1 - B4_R9)
        # =============================================================
        
        # B4_R1: Sun in Saturn star → union (11) OR separation (12)
        if Su:
            su_star = _star_of(Su)
            if su_star == "Saturn":
                sat = _p(planets, "Saturn")
                if sat:
                    sat_h = sat.get("house")
                    if sat_h == 11:
                        points.append("💚 Sun in Saturn star → Saturn lord of 11 → union signified [B4_R1_union]")
                    elif sat_h == 12:
                        points.append("💔 Sun in Saturn star → Saturn occupies 12 → separation signified [B4_R1_sep]")
        
        # B4_R2: Moon in Rahu star + Mars sub → union + separation
        if Mo:
            mo_star = _star_of(Mo)
            mo_sub = _sub_of(Mo)
            if mo_star == "Rahu" and mo_sub == "Mars":
                points.append("💔 Moon in Rahu star + Mars sub → union first, separation later [B4_R2]")
        
        # B4_R3: Mars in Rahu sub → ultimate separation
        if Ma:
            ma_sub = _sub_of(Ma)
            if ma_sub == "Rahu":
                points.append("💔 Mars in Rahu sub → ultimate separation indicated [B4_R3]")
        
        # B4_R4: Mercury in star of 12th lord + sub of Rahu → separation
        if Me:
            me_star = _star_of(Me)
            me_sub = _sub_of(Me)
            
            lord12 = _lord_of(12, houses)
            if lord12:
                me_star_is_l12_lord = (me_star == normalize_planet(lord12))
            else:
                me_star_is_l12_lord = False
            
            if me_star_is_l12_lord and me_sub == "Rahu":
                points.append("💔 Mercury in star of 12th lord & sub of Rahu → marital separation [B4_R4]")
        
        # B4_R5: Jupiter in Venus star + Jupiter sub in 12 → legal divorce
        if Ju:
            ju_star = _star_of(Ju)
            ju_sub = _sub_of(Ju)
            j_sub_p = _p(planets, ju_sub) if ju_sub else None
            if ju_star == "Venus" and ju_sub == "Jupiter":
                if j_sub_p and j_sub_p.get("house") == 12:
                    points.append("💔 Jupiter in Venus star + Jupiter sub in 12 → legal divorce indicated [B4_R5]")
        
        # B4_R6: Venus in 2nd + Rahu star + Rahu sub → union + separation
        if Ve:
            ve_h = Ve.get("house")
            ve_star = _star_of(Ve)
            ve_sub = _sub_of(Ve)
            if ve_h == 2 and ve_star == "Rahu" and ve_sub == "Rahu":
                points.append("💔 Venus in 2nd + Rahu star + Rahu sub → both union & separation potentials [B4_R6]")
        
        # B4_R7: Saturn in Venus star + Rahu sub → ultimate separation
        if Sa:
            sa_star = _star_of(Sa)
            sa_sub = _sub_of(Sa)
            if sa_star == "Venus" and sa_sub == "Rahu":
                points.append("💔 Saturn in Venus star + Rahu sub → ultimate separation [B4_R7]")
        
        # B4_R8: Rahu in Moon star + Venus sub → united married life
        if Ra:
            ra_star = _star_of(Ra)
            ra_sub = _sub_of(Ra)
            if ra_star == "Moon" and ra_sub == "Venus":
                points.append("💚 Rahu in Moon star + Venus sub → united married life [B4_R8]")
        
        # B4_R9: Ketu in Mercury star + Venus sub → unites
        if Ke:
            ke_star = _star_of(Ke)
            ke_sub = _sub_of(Ke)
            if ke_star == "Mercury" and ke_sub == "Venus":
                points.append("💚 Ketu in Mercury star + Venus sub → unites [B4_R9]")
        
        return points
    
    def _evaluate_doshas(self, planets: Dict, houses: List) -> List[str]:
        """Evaluate various doshas affecting marriage"""
        points = []
        
        Ma = _p(planets, "Mars")
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        # Manglik Dosha
        mars_house = Ma.get("house") if Ma else None
        manglik = mars_house in {1, 2, 4, 7, 8, 12} if mars_house else False
        
        if manglik:
            cancellation = False
            if _is_own_sign(Ma) or _is_exalted(Ma):
                cancellation = True
                points.append("Manglik dosha present but cancelled by Mars in own/exalted sign")
            elif _aspected_by(Ma, "Jupiter"):
                cancellation = True
                points.append("Manglik dosha mitigated by Jupiter's aspect")
            elif mars_house == 1 and Ma.get("sign") in {"Aries", "Scorpio"}:
                cancellation = True
                points.append("Manglik cancelled - Mars in own sign in 1st house")
            elif mars_house == 8 and Ma.get("sign") == "Scorpio":
                cancellation = True
                points.append("Manglik cancelled - Mars in own sign in 8th house")
            
            if not cancellation:
                points.append(f"Manglik dosha present (Mars in house {mars_house}) - partner matching advised")
        
        # Kuja Dosha variations
        if _in_house(Ma, 4):
            points.append("Mars in 4th house may affect domestic peace - conscious effort needed")
        
        # Rahu-Venus combination (unconventional relationship patterns)
        if _conjoined(Ra, Ve) or _aspected_by(Ve, "Rahu"):
            points.append("Rahu-Venus combination - unconventional relationship experiences")
        
        # Ketu with Venus (detachment in love)
        if _conjoined(Ke, Ve):
            points.append("Ketu-Venus conjunction - spiritual approach to relationships, possible detachment")
        
        # Paap Kartari Yoga on 7th house
        malefic_in_6 = any(_in_house(_p(planets, m), 6) for m in MALEFICS)
        malefic_in_8 = any(_in_house(_p(planets, m), 8) for m in MALEFICS)
        if malefic_in_6 and malefic_in_8:
            points.append("Paap Kartari on 7th house - marriage under pressure, extra care needed")
        
        return points
    
    def _calculate_overall_stability(self, planets: Dict, houses: List) -> Dict[str, Any]:
        """Calculate overall stability score and verdict"""
        positive_count = 0
        negative_count = 0
        
        Ve = _p(planets, "Venus")
        Ju = _p(planets, "Jupiter")
        Mo = _p(planets, "Moon")
        Ma = _p(planets, "Mars")
        Sa = _p(planets, "Saturn")
        Ra = _p(planets, "Rahu")
        Ke = _p(planets, "Ketu")
        
        lord7 = _lord_of(7, houses)
        
        # Positive factors
        benefics_in_7 = sum(1 for b in BENEFICS if _in_house(_p(planets, b), 7))
        positive_count += benefics_in_7
        
        if has_harmonious_aspect(Ve, "Jupiter"):
            positive_count += 1
        if _is_own_sign(Ve) or _is_exalted(Ve):
            positive_count += 1
        if _has_good_aspect(Ve):
            positive_count += 1
        if _has_good_aspect(Mo):
            positive_count += 1
        
        # Negative factors
        malefics_in_7 = sum(1 for m in MALEFICS if _in_house(_p(planets, m), 7))
        negative_count += malefics_in_7
        
        if lord7:
            l7_planet = _p(planets, lord7)
            if _in_houses(l7_planet, {6, 8, 12}):
                negative_count += 2
        
        if _in_house(Ra, 7) or _in_house(Ke, 7):
            negative_count += 1
        
        if has_harsh_aspect(Ve, "Saturn"):
            negative_count += 1
        
        if _has_evil_aspect(Ve, Ma):
            negative_count += 1
        
        # Calculate verdict
        net_score = positive_count - negative_count
        
        if net_score >= 3:
            verdict = "Overall: Strong marital stability indicated"
        elif net_score <= -3:
            verdict = "Overall: Attention needed for marital harmony - remedies recommended"
        else:
            verdict = "Overall: Mixed indicators - balance of strengths and challenges in marriage"
        
        return {
            "score": net_score,
            "positive": positive_count,
            "negative": negative_count,
            "verdict": verdict
        }
    
    def get_questions(self) -> List[Question]:
        """Get predefined questions for Marital Stability"""
        return [
            # Divorce/Separation Risk
            Question(
                id="MAR_STAB_DIV1",
                question=(
                    "Are there astrological indications of separation, divorce risk, "
                    "or marital instability? What is the severity?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Divorce/Separation"
            ),
            # Divorce Timing
            Question(
                id="MAR_STAB_DIV_TIME1",
                question=(
                    "During which periods is marital instability or separation risk "
                    "more actively triggered?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Divorce Timing"
            ),
            # Compatibility (Happy/Unhappy)
            Question(
                id="MAR_STAB_COMP1",
                question=(
                    "What are the indicators for a happy vs unhappy married life? "
                    "How compatible is the chart for marital happiness?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEUTRAL,
                    goal=InterpretationGoal.STATUS
                ),
                sub_subdomain="Compatibility"
            ),
            # Doshas and Stress Factors
            Question(
                id="MAR_STAB_D1",
                question=(
                    "Are there stress-indicating combinations or dosha-like patterns "
                    "affecting marital stability, and how can their impact be reduced?"
                ),
                meta=QueryMeta(
                    query_type=QueryType.NON_TIMING,
                    polarity=EventPolarity.NEGATIVE,
                    goal=InterpretationGoal.RISK
                ),
                sub_subdomain="Doshas and Stress Factors"
            )
        ]

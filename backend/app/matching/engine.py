from typing import Dict, Any, List
from app.models.profile import EntrepreneurProfile, BusinessProfile
from app.models.scheme import Scheme

def evaluate_scheme_match(
    entrepreneur: EntrepreneurProfile,
    business: BusinessProfile,
    scheme: Scheme
) -> Dict[str, Any]:
    reasons: List[str] = []
    missing: List[str] = []
    
    # -------------------------------------------------------------
    # 1. ELIGIBILITY SCORE (30% weight) - Personal & Demographics
    # -------------------------------------------------------------
    eligibility_points = 0.0
    total_eligibility_criteria = 0
    is_eligible = True

    # Age check
    if scheme.minimum_age or scheme.maximum_age:
        total_eligibility_criteria += 1
        min_a = scheme.minimum_age or 0
        max_a = scheme.maximum_age or 999
        if min_a <= entrepreneur.age <= max_a:
            eligibility_points += 1.0
            reasons.append(f"Age ({entrepreneur.age} yrs) satisfies scheme eligibility range")
        else:
            is_eligible = False
            missing.append(f"Age {entrepreneur.age} yrs is outside the scheme limit ({min_a}-{max_a} yrs)")
    
    # Gender check
    if scheme.gender_requirements and scheme.gender_requirements.lower() != "all":
        total_eligibility_criteria += 1
        if entrepreneur.gender.lower() == scheme.gender_requirements.lower():
            eligibility_points += 1.0
            reasons.append(f"Gender ({entrepreneur.gender}) matches scheme target group")
        else:
            if scheme.gender_requirements.lower() in ['women', 'women only', 'female']:
                is_eligible = False
                missing.append(f"Scheme specifically targets {scheme.gender_requirements} entrepreneurs")
            else:
                eligibility_points += 0.5
                missing.append(f"Scheme prioritizes {scheme.gender_requirements} entrepreneurs")

    # Social Category check
    target_social_cats = scheme.social_category_requirements or ["All"]
    if "All" not in target_social_cats and len(target_social_cats) > 0:
        total_eligibility_criteria += 1
        if entrepreneur.social_category in target_social_cats:
            eligibility_points += 1.0
            reasons.append(f"Social category ({entrepreneur.social_category}) matches scheme priority group")
        else:
            is_eligible = False
            missing.append(f"Scheme requires applicant category: {', '.join(target_social_cats)}")

    eligibility_score = (eligibility_points / total_eligibility_criteria * 100.0) if total_eligibility_criteria > 0 else 100.0

    # -------------------------------------------------------------
    # 2. BUSINESS RELEVANCE SCORE (30% weight)
    # -------------------------------------------------------------
    relevance_points = 0.0
    total_relevance_criteria = 0

    target_industries = scheme.industries or ["All"]
    if "All" not in target_industries and len(target_industries) > 0:
        total_relevance_criteria += 1
        if business.industry in target_industries:
            relevance_points += 1.0
            reasons.append(f"Industry sector ({business.industry}) matches scheme scope")
        else:
            is_eligible = False
            missing.append(f"Industry ({business.industry}) differs from primary focus ({', '.join(target_industries)})")

    target_b_types = scheme.business_types or ["All"]
    if "All" not in target_b_types and len(target_b_types) > 0:
        total_relevance_criteria += 1
        if business.business_type in target_b_types:
            relevance_points += 1.0
            reasons.append(f"Business activity type ({business.business_type}) aligns with scheme objectives")
        else:
            is_eligible = False
            missing.append(f"Business type ({business.business_type}) not specifically listed ({', '.join(target_b_types)})")

    relevance_score = (relevance_points / total_relevance_criteria * 100.0) if total_relevance_criteria > 0 else 100.0

    # -------------------------------------------------------------
    # 3. FUNDING MATCH SCORE (20% weight)
    # -------------------------------------------------------------
    funding_score = 100.0
    funding_req = business.funding_required or business.estimated_investment
    
    if scheme.funding_max and scheme.funding_max > 0:
        funding_min = scheme.funding_min or 0.0
        if funding_min <= funding_req <= scheme.funding_max:
            funding_score = 100.0
            reasons.append(f"Required funding fits scheme limits")
        elif funding_req > scheme.funding_max:
            ratio = scheme.funding_max / funding_req
            funding_score = max(10.0, round(ratio * 100.0, 1))
            missing.append(f"Funding requirement exceeds scheme ceiling (₹{scheme.funding_max:,.0f})")
        elif funding_req < scheme.funding_min:
            funding_score = 60.0
            missing.append(f"Funding requirement is below scheme minimum threshold (₹{scheme.funding_min:,.0f})")
    else:
        reasons.append("Scheme provides flexible / uncapped financial support")

    # -------------------------------------------------------------
    # 4. LOCATION SCORE (10% weight)
    # -------------------------------------------------------------
    location_score = 100.0
    scheme_states = scheme.states or ["All"]
    
    if "All" not in scheme_states and len(scheme_states) > 0:
        if business.business_location_state not in scheme_states:
            location_score = 0.0
            is_eligible = False
            missing.append(f"Scheme jurisdiction is restricted to states: {', '.join(scheme_states)}")
        else:
            reasons.append(f"Business location ({business.business_location_state}) is eligible")

    if scheme.rural_urban_requirements and scheme.rural_urban_requirements.lower() != "all":
        user_area = "Rural" if business.is_rural else "Urban"
        if user_area.lower() == scheme.rural_urban_requirements.lower():
            reasons.append(f"{user_area} location requirement matched")
        else:
            is_eligible = False
            missing.append(f"Scheme targets {scheme.rural_urban_requirements} areas only")

    # -------------------------------------------------------------
    # 5. SUPPORT NEED SCORE (10% weight)
    # -------------------------------------------------------------
    need_score = 70.0
    user_supports = [s.lower() for s in (business.support_needed or [])]
    scheme_supports = [s.lower() for s in (scheme.support_types or [])]

    if user_supports and scheme_supports:
        matched_supports = []
        for us in user_supports:
            for ss in scheme_supports:
                if us in ss or ss in us or ("machinery" in us and "capital" in ss) or ("loan" in us and "credit" in ss):
                    matched_supports.append(us)
                    break
        
        if matched_supports:
            need_score = 100.0
            reasons.append(f"Support needs ({', '.join(set(matched_supports))}) match scheme benefits")
        else:
            need_score = 50.0
    else:
        need_score = 100.0  # Do not penalize if unspecified
        reasons.append("Support types aligns with business profile")

    # -------------------------------------------------------------
    # OVERALL WEIGHTED SCORE CALCULATION
    # -------------------------------------------------------------
    overall_score = round(
        (eligibility_score * 0.30) +
        (relevance_score * 0.30) +
        (funding_score * 0.20) +
        (location_score * 0.10) +
        (need_score * 0.10),
        1
    )

    if not is_eligible:
        missing.insert(0, "Not eligible based on available information")
        overall_score = 0.0

    return {
        "overall_score": overall_score,
        "eligibility_score": round(eligibility_score, 1),
        "relevance_score": round(relevance_score, 1),
        "funding_score": round(funding_score, 1),
        "location_score": round(location_score, 1),
        "need_score": round(need_score, 1),
        "is_eligible": is_eligible,
        "reasons": reasons if is_eligible else [],
        "missing_requirements": missing if missing else ["None! All primary criteria matched."],
        "required_documents": scheme.required_documents or [],
        "next_steps": ["Review scheme guidelines on official portal", "Submit online application via official portal"]
    }

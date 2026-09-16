import pytest
from app.models.profile import EntrepreneurProfile, BusinessProfile
from app.models.scheme import Scheme
from app.matching.engine import evaluate_scheme_match

def test_missing_criteria_no_penalty():
    entrepreneur = EntrepreneurProfile(
        age=30, gender="Male", social_category="General", disability_status=False
    )
    business = BusinessProfile(
        industry="IT", business_type="Service", business_stage="New", 
        funding_required=500000, business_location_state="Karnataka",
        is_rural=False, support_needed=["Mentorship"]
    )
    scheme = Scheme(
        name="No Restrictions Scheme",
        states=[], industries=[], business_types=[], business_stages=[],
        minimum_age=None, maximum_age=None, gender_requirements="All",
        social_category_requirements=[], rural_urban_requirements="All",
        funding_min=0.0, funding_max=0.0, support_types=[]
    )
    result = evaluate_scheme_match(entrepreneur, business, scheme)
    
    assert result["is_eligible"] is True
    assert result["eligibility_score"] == 100.0
    assert result["relevance_score"] == 100.0
    assert result["location_score"] == 100.0
    assert result["need_score"] == 100.0
    assert result["overall_score"] >= 90.0
    assert "Not eligible" not in result["missing_requirements"][0]

def test_hard_eligibility_failure():
    entrepreneur = EntrepreneurProfile(
        age=45, gender="Male", social_category="General", disability_status=False
    )
    business = BusinessProfile(
        industry="Agriculture", business_type="Trading", business_stage="Existing", 
        funding_required=200000, business_location_state="Bihar",
        is_rural=True, support_needed=["Capital Subsidy"]
    )
    # Fails hard eligibility by state
    scheme = Scheme(
        name="Strict Scheme",
        states=["Uttar Pradesh"], minimum_age=18, maximum_age=60,
        funding_max=500000
    )
    result = evaluate_scheme_match(entrepreneur, business, scheme)
    
    assert result["is_eligible"] is False
    assert result["overall_score"] == 0.0
    assert "Not eligible based on available information" in result["missing_requirements"]


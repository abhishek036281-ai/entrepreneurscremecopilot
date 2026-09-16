import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_phase4_matching_and_security():
    print("=== STARTING PHASE 4: MATCHING ENGINE & SECURITY AUDIT ===")
    session = requests.Session()
    timestamp = int(time.time())

    # -------------------------------------------------------------
    # 1. AUDIT 401/403 SECURITY & AUTHORIZATION BOUNDARIES
    # -------------------------------------------------------------
    # Unauthenticated request to /api/profile should return 401
    no_auth_r = session.get(f"{BASE_URL}/api/profile")
    assert no_auth_r.status_code == 401, f"Expected 401 for unauthenticated request, got {no_auth_r.status_code}"
    print("[OK] 1. Unauthenticated request to protected endpoint correctly returns 401 Unauthorized")

    # Register User A (Female OBC Food Processor in UP)
    email_a = f"phase4_user_a_{timestamp}@example.com"
    pwd = "TestPassword@123"
    session.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Anita Devi", "email": email_a, "password": pwd})
    token_a = session.post(f"{BASE_URL}/api/auth/login", json={"email": email_a, "password": pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Non-admin User A requesting Admin endpoints should return 403 Forbidden
    admin_auth_r = session.get(f"{BASE_URL}/api/admin/schemes", headers=headers_a)
    assert admin_auth_r.status_code == 403, f"Expected 403 Forbidden for non-admin on admin route, got {admin_auth_r.status_code}"
    print("[OK] 2. Non-admin request to admin endpoints correctly returns 403 Forbidden (Security Boundary Confirmed)")

    # -------------------------------------------------------------
    # 2. PROFILE A: FEMALE OBC MICRO FOOD PROCESSOR IN UTTAR PRADESH
    # -------------------------------------------------------------
    session.put(f"{BASE_URL}/api/profile", headers=headers_a, json={
        "full_name": "Anita Devi",
        "age": 28,
        "gender": "Female",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "social_category": "OBC",
        "rural_urban": "Rural",
        "disability_status": False,
        "entrepreneur_type": "New",
        "business_stage": "Idea"
    })

    session.put(f"{BASE_URL}/api/business", headers=headers_a, json={
        "business_name": "Varanasi Food Products",
        "raw_description": "Small food processing unit for spice mixes in rural UP needing 5 lakh for machinery",
        "industry": "Food Processing",
        "business_type": "Manufacturing",
        "business_stage": "Idea",
        "is_new_business": True,
        "estimated_investment": 500000.0,
        "funding_required": 500000.0,
        "purpose_of_funding": "Machinery & Capital",
        "machinery_cost": 350000.0,
        "working_capital_cost": 150000.0,
        "employee_count": 3,
        "expected_turnover": 1200000.0,
        "business_location_state": "Uttar Pradesh",
        "business_location_district": "Varanasi",
        "is_rural": True,
        "support_needed": ["Capital Subsidy", "Bank Loan", "Machinery / Equipment"],
        "support_notes": "Need PMEGP capital subsidy"
    })

    rec_a_r = session.post(f"{BASE_URL}/api/recommendations", headers=headers_a)
    assert rec_a_r.status_code == 200
    recs_a = rec_a_r.json()
    assert len(recs_a) > 0
    top_a = recs_a[0]
    print(f"[OK] 3. Profile A Recommendations generated: Top match '{top_a['scheme']['name']}' with score {top_a['match_breakdown']['overall_score']}%")
    assert top_a['match_breakdown']['overall_score'] >= 85.0

    # -------------------------------------------------------------
    # 3. PROFILE B: MALE GENERAL IT CONSULTANCY IN MAHARASHTRA
    # -------------------------------------------------------------
    email_b = f"phase4_user_b_{timestamp}@example.com"
    session.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Vikram Salunkhe", "email": email_b, "password": pwd})
    token_b = session.post(f"{BASE_URL}/api/auth/login", json={"email": email_b, "password": pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    session.put(f"{BASE_URL}/api/profile", headers=headers_b, json={
        "full_name": "Vikram Salunkhe",
        "age": 35,
        "gender": "Male",
        "state": "Maharashtra",
        "district": "Pune",
        "social_category": "General",
        "rural_urban": "Urban",
        "disability_status": False,
        "entrepreneur_type": "Existing",
        "business_stage": "Growth"
    })

    session.put(f"{BASE_URL}/api/business", headers=headers_b, json={
        "business_name": "Pune Tech Solutions",
        "raw_description": "IT consultancy expanding software development team",
        "industry": "IT & Tech Services",
        "business_type": "Service",
        "business_stage": "Growth",
        "is_new_business": False,
        "estimated_investment": 1500000.0,
        "funding_required": 800000.0,
        "purpose_of_funding": "Working Capital & Hiring",
        "machinery_cost": 0.0,
        "working_capital_cost": 800000.0,
        "employee_count": 8,
        "expected_turnover": 4000000.0,
        "business_location_state": "Maharashtra",
        "business_location_district": "Pune",
        "is_rural": False,
        "support_needed": ["Working Capital", "Bank Loan"],
        "support_notes": "Collateral free working capital loan"
    })

    rec_b_r = session.post(f"{BASE_URL}/api/recommendations", headers=headers_b)
    assert rec_b_r.status_code == 200
    recs_b = rec_b_r.json()
    assert len(recs_b) > 0
    top_b = recs_b[0]
    print(f"[OK] 4. Profile B Recommendations generated: Top match '{top_b['scheme']['name']}' with score {top_b['match_breakdown']['overall_score']}%")
    print(f"[OK] 4. Profile B Recommendations generated: Top match '{top_b['scheme']['name']}' with score {top_b['match_breakdown']['overall_score']}%")

    # -------------------------------------------------------------
    # 4. PROFILE C: NO-MATCH INELIGIBLE PROFILE (Age 85, Invalid State)
    # -------------------------------------------------------------
    email_c = f"phase4_user_c_{timestamp}@example.com"
    session.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Ineligible User", "email": email_c, "password": pwd})
    token_c = session.post(f"{BASE_URL}/api/auth/login", json={"email": email_c, "password": pwd}).json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    session.put(f"{BASE_URL}/api/profile", headers=headers_c, json={
        "full_name": "Ineligible User",
        "age": 85, # Way out of range
        "gender": "Male",
        "state": "NonExistentTerritory",
        "district": "None",
        "social_category": "General",
        "rural_urban": "Urban",
        "disability_status": False,
        "entrepreneur_type": "New",
        "business_stage": "Idea"
    })

    session.put(f"{BASE_URL}/api/business", headers=headers_c, json={
        "business_name": "Impossible Venture",
        "raw_description": "Over budget project",
        "industry": "IT & Tech Services",
        "business_type": "Trading",
        "business_stage": "Idea",
        "is_new_business": True,
        "estimated_investment": 1000000000.0, # 100 Crore (exceeds all limits)
        "funding_required": 1000000000.0,
        "purpose_of_funding": "None",
        "business_location_state": "NonExistentTerritory",
        "business_location_district": "None",
        "is_rural": False,
        "support_needed": [],
        "support_notes": ""
    })

    rec_c_r = session.post(f"{BASE_URL}/api/recommendations", headers=headers_c)
    assert rec_c_r.status_code == 200
    recs_c = rec_c_r.json()
    for item in recs_c:
        score = item['match_breakdown']['overall_score']
        is_elig = item['match_breakdown']['is_eligible']
        assert is_elig == False, "Ineligible profile must return is_eligible=False"
        assert score <= 45.0, f"Ineligible profile score must be capped <= 45%, got {score}"
    print(f"[OK] 5. No-Match Profile correctly evaluated: All schemes returned is_eligible=False and score <= 45%")

    print("\n=== PHASE 4 MATCHING ENGINE & SECURITY AUDIT PASSED 100%! ===")

if __name__ == "__main__":
    test_phase4_matching_and_security()

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_full_audit():
    print("=== STARTING COMPREHENSIVE E2E AUDIT ===")
    session = requests.Session()
    
    # 1. Health check
    r = session.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[OK] 1. Health Check PASSED")

    # 2. Register a NEW unique user
    timestamp = int(time.time())
    new_email = f"audit_user_{timestamp}@copilot.gov.in"
    new_password = "AuditPassword@123"
    
    reg_r = session.post(f"{BASE_URL}/api/auth/register", json={"email": new_email, "password": new_password})
    assert reg_r.status_code == 200, f"Registration failed: {reg_r.text}"
    user_data = reg_r.json()
    assert user_data["email"] == new_email
    print("[OK] 2. New User Registration PASSED")

    # 3. Login with new user
    login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": new_email, "password": new_password})
    assert login_r.status_code == 200, f"Login failed: {login_r.text}"
    token_info = login_r.json()
    user_token = token_info["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print("[OK] 3. Login PASSED")

    # 4. Verify password hashing & auth validation (Wrong password should fail)
    bad_login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": new_email, "password": "WrongPassword"})
    assert bad_login_r.status_code == 401
    print("[OK] 4. Auth Security & Hashing Validation PASSED")

    # 5. Complete Entrepreneur Profile
    ent_profile = {
        "full_name": "Anita Sharma",
        "age": 29,
        "gender": "Female",
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "social_category": "OBC",
        "rural_urban": "Rural",
        "disability_status": False,
        "entrepreneur_type": "New",
        "business_stage": "Idea"
    }
    p_r = session.put(f"{BASE_URL}/api/profile", json=ent_profile, headers=user_headers)
    assert p_r.status_code == 200, f"Profile PUT failed: {p_r.text}"
    print("[OK] 5. Entrepreneur Profile Completion PASSED")

    # 6. Complete Business Profile & 7. Natural Language Business Description
    biz_desc = "I want to start a micro food processing unit making spice mixes and fruit jams in rural Uttar Pradesh and need RS 6 lakh for machinery and working capital."
    biz_profile = {
        "business_name": "Sharma Food Products",
        "raw_description": biz_desc,
        "industry": "Food Processing",
        "business_type": "Manufacturing",
        "business_stage": "Idea",
        "is_new_business": True,
        "estimated_investment": 600000.0,
        "funding_required": 600000.0,
        "purpose_of_funding": "Machinery Purchase & Working Capital",
        "machinery_cost": 400000.0,
        "working_capital_cost": 200000.0,
        "employee_count": 3,
        "expected_turnover": 1500000.0,
        "business_location_state": "Uttar Pradesh",
        "business_location_district": "Lucknow",
        "is_rural": True
    }
    b_r = session.put(f"{BASE_URL}/api/business", json=biz_profile, headers=user_headers)
    assert b_r.status_code == 200, f"Business PUT failed: {b_r.text}"
    print("[OK] 6 & 7. Business Profile & Natural Language Description PASSED")

    # 8. Test AI Business Analysis Endpoint directly
    ai_r = session.post(f"{BASE_URL}/api/analyze-business", json={"text": biz_desc})
    assert ai_r.status_code == 200, f"AI Analysis failed: {ai_r.text}"
    ai_res = ai_r.json()
    assert ai_res["extracted_industry"] == "Food Processing"
    assert ai_res["extracted_funding_needed"] == 600000.0
    print("[OK] 8. AI Analysis Endpoint PASSED")

    # 9, 10, 11. Recommendations & Dynamic Score Calculation from DB
    rec_r = session.post(f"{BASE_URL}/api/recommendations", headers=user_headers)
    assert rec_r.status_code == 200, f"Recommendations failed: {rec_r.text}"
    recs = rec_r.json()
    assert len(recs) > 0, "No recommendations returned!"
    first_match = recs[0]
    score_1 = first_match["match_breakdown"]["overall_score"]
    assert "reasons" in first_match["match_breakdown"]
    assert "missing_requirements" in first_match["match_breakdown"]
    print(f"[OK] 9, 10, 11. Matching Engine & Dynamic Scoring PASSED (Top score: {score_1}%)")

    # 12. Dynamic Score Change Test: Modify user location to incompatible state
    ent_profile_2 = dict(ent_profile)
    ent_profile_2["age"] = 75 # Outside scheme max age limit
    session.put(f"{BASE_URL}/api/profile", json=ent_profile_2, headers=user_headers)
    
    rec_r_2 = session.post(f"{BASE_URL}/api/recommendations", headers=user_headers)
    recs_2 = rec_r_2.json()
    score_2 = recs_2[0]["match_breakdown"]["overall_score"]
    assert score_2 < score_1, f"Expected score to drop when user profile changed, but was {score_2} vs {score_1}"
    print(f"[OK] 12. Dynamic Score Sensitivity Verification PASSED (Score dropped from {score_1}% to {score_2}%)")

    # Reset profile back to eligible parameters
    session.put(f"{BASE_URL}/api/profile", json=ent_profile, headers=user_headers)

    # 13, 14, 15. Scheme Details & Dynamic Roadmap
    scheme_id = first_match["scheme"]["id"]
    scheme_r = session.get(f"{BASE_URL}/api/schemes/{scheme_id}")
    assert scheme_r.status_code == 200
    scheme_detail = scheme_r.json()
    assert "required_documents" in scheme_detail
    assert "official_url" in scheme_detail

    roadmap_r = session.get(f"{BASE_URL}/api/roadmap/{scheme_id}", headers=user_headers)
    assert roadmap_r.status_code == 200
    roadmap_data = roadmap_r.json()
    assert len(roadmap_data["roadmap_steps"]) > 0
    print("[OK] 13, 14, 15. Scheme Details & Dynamic Roadmap PASSED")

    # 16 & 17. Save / Unsave Scheme & Database Persistence
    save_r = session.post(f"{BASE_URL}/api/schemes/{scheme_id}/save", headers=user_headers)
    assert save_r.status_code == 200
    
    saved_list_r = session.get(f"{BASE_URL}/api/saved-schemes", headers=user_headers)
    saved_list = saved_list_r.json()
    assert any(s["scheme_id"] == scheme_id for s in saved_list)
    print("[OK] 16 & 17. Save Scheme & Database Persistence PASSED")

    # 18. Admin Login with real admin account
    admin_login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@copilot.gov.in", "password": "Admin@123"})
    assert admin_login_r.status_code == 200
    admin_token = admin_login_r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] 18. Admin Login PASSED")

    # 19 & 20. Admin Add New Scheme & Verify in User Recommendations
    new_scheme_payload = {
        "name": f"Audit Custom MSME Grant {timestamp}",
        "description": "Special capital subsidy for female micro processors in Uttar Pradesh",
        "ministry": "Ministry of MSME",
        "category": "Subsidy",
        "target_beneficiaries": ["Women", "OBC"],
        "states": ["Uttar Pradesh"],
        "business_types": ["Manufacturing"],
        "industries": ["Food Processing"],
        "business_stages": ["Idea"],
        "minimum_age": 18,
        "maximum_age": 60,
        "gender_requirements": "Female",
        "social_category_requirements": ["OBC"],
        "rural_urban_requirements": "Rural",
        "funding_min": 100000.0,
        "funding_max": 1000000.0,
        "support_types": ["Capital Subsidy"],
        "benefits": "40% capital grant for machinery purchase",
        "eligibility_rules": {},
        "required_documents": ["Aadhaar", "PAN", "DPR"],
        "application_process": [{"title": "Apply Online", "desc": "Submit on portal"}],
        "official_url": "https://msme.gov.in",
        "status": "Active"
    }

    add_scheme_r = session.post(f"{BASE_URL}/api/admin/schemes", json=new_scheme_payload, headers=admin_headers)
    assert add_scheme_r.status_code == 200, f"Add scheme failed: {add_scheme_r.text}"
    created_scheme = add_scheme_r.json()
    created_id = created_scheme["id"]
    print("[OK] 19. Admin Add Scheme PASSED")

    # Verify newly added scheme appears in female OBC entrepreneur recommendations!
    user_recs_r = session.post(f"{BASE_URL}/api/recommendations", headers=user_headers)
    user_recs = user_recs_r.json()
    assert any(r["scheme"]["id"] == created_id for r in user_recs), "Newly created admin scheme did not appear in user recommendations!"
    print("[OK] 20. New Admin Scheme Appears in User Recommendations PASSED")

    # 21. Edit and Delete/Deactivate Scheme from Admin
    update_payload = {"benefits": "Updated 50% capital grant for machinery purchase"}
    edit_r = session.put(f"{BASE_URL}/api/admin/schemes/{created_id}", json=update_payload, headers=admin_headers)
    assert edit_r.status_code == 200
    assert edit_r.json()["benefits"] == "Updated 50% capital grant for machinery purchase"

    del_r = session.delete(f"{BASE_URL}/api/admin/schemes/{created_id}", headers=admin_headers)
    assert del_r.status_code == 200
    print("[OK] 21. Admin Edit & Delete Scheme PASSED")

    # 22. Test Unauthorized Access to Admin Endpoints
    unauth_r = session.get(f"{BASE_URL}/api/admin/schemes", headers=user_headers)
    assert unauth_r.status_code == 403, f"Expected 403 Forbidden for non-admin user, got {unauth_r.status_code}"
    print("[OK] 22. Unauthorized Admin Access Blocked PASSED")

    print("\n=== ALL E2E AUDIT TESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_full_audit()

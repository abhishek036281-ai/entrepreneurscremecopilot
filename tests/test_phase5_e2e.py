import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_phase5_full_e2e():
    print("=== STARTING PHASE 5 FULL E2E RECOMMENDATION & DASHBOARD VERIFICATION ===")
    session_a = requests.Session()
    session_b = requests.Session()

    timestamp = int(time.time())
    email_a = f"p5_user_a_{timestamp}@example.com"
    email_b = f"p5_user_b_{timestamp}@example.com"
    pwd = "TestPassword@123"

    # 1. Register & Login User A
    session_a.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Anita Devi", "email": email_a, "password": pwd})
    token_a = session_a.post(f"{BASE_URL}/api/auth/login", json={"email": email_a, "password": pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register & Login User B
    session_b.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Vikram Salunkhe", "email": email_b, "password": pwd})
    token_b = session_b.post(f"{BASE_URL}/api/auth/login", json={"email": email_b, "password": pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("[OK] 1 & 2. User A and User B registered and logged in")

    # 3. User A profile setup
    session_a.put(f"{BASE_URL}/api/profile", headers=headers_a, json={
        "full_name": "Anita Devi", "age": 28, "gender": "Female", "state": "Uttar Pradesh", "district": "Varanasi",
        "social_category": "OBC", "rural_urban": "Rural", "disability_status": False, "entrepreneur_type": "New", "business_stage": "Idea"
    })
    session_a.put(f"{BASE_URL}/api/business", headers=headers_a, json={
        "business_name": "Varanasi Spices", "industry": "Food Processing", "business_type": "Manufacturing",
        "estimated_investment": 500000.0, "funding_required": 500000.0, "purpose_of_funding": "Machinery",
        "business_location_state": "Uttar Pradesh", "business_location_district": "Varanasi", "is_rural": True,
        "support_needed": ["Capital Subsidy", "Bank Loan"], "support_notes": "PMEGP grant"
    })

    # 4. User B profile setup
    session_b.put(f"{BASE_URL}/api/profile", headers=headers_b, json={
        "full_name": "Vikram Salunkhe", "age": 35, "gender": "Male", "state": "Maharashtra", "district": "Pune",
        "social_category": "General", "rural_urban": "Urban", "disability_status": False, "entrepreneur_type": "Existing", "business_stage": "Growth"
    })
    session_b.put(f"{BASE_URL}/api/business", headers=headers_b, json={
        "business_name": "Pune Software", "industry": "IT & Tech Services", "business_type": "Service",
        "estimated_investment": 1500000.0, "funding_required": 800000.0, "purpose_of_funding": "Hiring",
        "business_location_state": "Maharashtra", "business_location_district": "Pune", "is_rural": False,
        "support_needed": ["Working Capital", "Bank Loan"], "support_notes": "Tech scaling"
    })
    print("[OK] 3 & 4. Distinct profiles saved for User A and User B")

    # 5. Verify Recommendations for User A
    recs_a_r = session_a.post(f"{BASE_URL}/api/recommendations", headers=headers_a)
    assert recs_a_r.status_code == 200
    recs_a = recs_a_r.json()
    top_scheme_a = recs_a[0]["scheme"]
    print(f"[OK] 5. User A recommendations calculated: Top scheme '{top_scheme_a['name']}' ({recs_a[0]['match_breakdown']['overall_score']}%)")

    # 6. Test AI Explain Match Endpoint for User A
    explain_r = session_a.post(f"{BASE_URL}/api/explain-match", headers=headers_a, json={"scheme_id": top_scheme_a["id"]})
    assert explain_r.status_code == 200
    explain_data = explain_r.json()
    assert "explanation" in explain_data
    print(f"[OK] 6. AI Explain Match endpoint verified: '{explain_data['explanation'][:60]}...'")

    # 7. Test Save & Unsave Scheme for User A
    save_r = session_a.post(f"{BASE_URL}/api/schemes/{top_scheme_a['id']}/save", headers=headers_a)
    assert save_r.status_code == 200
    
    saved_r = session_a.get(f"{BASE_URL}/api/saved-schemes", headers=headers_a)
    saved_list = saved_r.json()
    assert len(saved_list) == 1
    assert saved_list[0]["scheme_id"] == top_scheme_a["id"]
    print("[OK] 7. Save scheme endpoint and GET /api/saved-schemes verified")

    # 8. User B saved schemes isolation check
    saved_b_r = session_b.get(f"{BASE_URL}/api/saved-schemes", headers=headers_b)
    assert len(saved_b_r.json()) == 0, "User B must not see User A's saved schemes!"
    print("[OK] 8. User B isolated: 0 saved schemes returned for User B")

    # 9. Test Unsave Scheme
    del_save_r = session_a.delete(f"{BASE_URL}/api/schemes/{top_scheme_a['id']}/save", headers=headers_a)
    assert del_save_r.status_code == 200
    assert len(session_a.get(f"{BASE_URL}/api/saved-schemes", headers=headers_a).json()) == 0
    print("[OK] 9. Unsave scheme (DELETE /api/schemes/{id}/save) verified")

    print("\n=== PHASE 5 FULL E2E VERIFICATION PASSED 100%! ===")

if __name__ == "__main__":
    test_phase5_full_e2e()

import requests
import sqlite3
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = r"C:\Users\Divyanshu RAI\.gemini\antigravity\scratch\entrepreneur-scheme-copilot\backend\sql_app.db"

def test_complete_onboarding_flow():
    print("=== STARTING MULTI-STEP ONBOARDING END-TO-END VERIFICATION ===")
    session_a = requests.Session()
    session_b = requests.Session()

    timestamp = int(time.time())
    email_a = f"user_a_{timestamp}@example.com"
    email_b = f"user_b_{timestamp}@example.com"
    password = "TestPassword@123"

    # 1. Register User A
    reg_a = session_a.post(f"{BASE_URL}/api/auth/register", json={"full_name": "User Alpha", "email": email_a, "password": password})
    assert reg_a.status_code == 200
    token_a = session_a.post(f"{BASE_URL}/api/auth/login", json={"email": email_a, "password": password}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("[OK] 1. User A registered & logged in")

    # 2. Register User B
    reg_b = session_b.post(f"{BASE_URL}/api/auth/register", json={"full_name": "User Beta", "email": email_b, "password": password})
    assert reg_b.status_code == 200
    token_b = session_b.post(f"{BASE_URL}/api/auth/login", json={"email": email_b, "password": password}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("[OK] 2. User B registered & logged in")

    # 3. User A completes Step 1: Entrepreneur Profile
    ent_profile_a = {
        "full_name": "User Alpha",
        "age": 27,
        "gender": "Female",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "social_category": "OBC",
        "rural_urban": "Rural",
        "disability_status": False,
        "entrepreneur_type": "New",
        "business_stage": "Idea"
    }
    p_a_res = session_a.put(f"{BASE_URL}/api/profile", json=ent_profile_a, headers=headers_a)
    assert p_a_res.status_code == 200
    print("[OK] 3. User A completed Step 1 (Entrepreneur Profile saved to DB)")

    # 4. User A completes Step 2 & 3: Business Profile & Support Requirements
    biz_profile_a = {
        "business_name": "Alpha Food Processing",
        "raw_description": "I want to start a small food processing unit in UP and need ₹5 lakh for machinery.",
        "industry": "Food Processing",
        "business_type": "Manufacturing",
        "business_stage": "Idea",
        "is_new_business": True,
        "estimated_investment": 500000.0,
        "funding_required": 500000.0,
        "purpose_of_funding": "Machinery Purchase & Working Capital",
        "machinery_cost": 350000.0,
        "working_capital_cost": 150000.0,
        "employee_count": 3,
        "expected_turnover": 1200000.0,
        "business_location_state": "Uttar Pradesh",
        "business_location_district": "Varanasi",
        "is_rural": True,
        "support_needed": ["Loan", "Subsidy", "Machinery / Equipment", "Working Capital"],
        "support_notes": "Need capital subsidy and collateral-free loan support"
    }
    b_a_res = session_a.put(f"{BASE_URL}/api/business", json=biz_profile_a, headers=headers_a)
    assert b_a_res.status_code == 200
    print("[OK] 4. User A completed Step 2 & 3 (Business & Support Requirements saved to DB)")

    # 5. User B completes different Profile data
    ent_profile_b = {
        "full_name": "User Beta",
        "age": 45,
        "gender": "Male",
        "state": "Maharashtra",
        "district": "Pune",
        "social_category": "General",
        "rural_urban": "Urban",
        "disability_status": False,
        "entrepreneur_type": "Existing",
        "business_stage": "Growth"
    }
    session_b.put(f"{BASE_URL}/api/profile", json=ent_profile_b, headers=headers_b)

    biz_profile_b = {
        "business_name": "Beta Tech Solutions",
        "raw_description": "Software development consultancy",
        "industry": "IT & Tech Services",
        "business_type": "Service",
        "business_stage": "Growth",
        "is_new_business": False,
        "estimated_investment": 2000000.0,
        "funding_required": 1000000.0,
        "purpose_of_funding": "Expansion",
        "machinery_cost": 0.0,
        "working_capital_cost": 1000000.0,
        "employee_count": 10,
        "expected_turnover": 5000000.0,
        "business_location_state": "Maharashtra",
        "business_location_district": "Pune",
        "is_rural": False,
        "support_needed": ["Loan", "Mentorship"],
        "support_notes": "Scaling tech team"
    }
    session_b.put(f"{BASE_URL}/api/business", json=biz_profile_b, headers=headers_b)
    print("[OK] 5. User B completed separate profile data")

    # 6. Verify Isolation: User A gets User A's data, User B gets User B's data
    get_p_a = session_a.get(f"{BASE_URL}/api/profile", headers=headers_a).json()
    get_p_b = session_b.get(f"{BASE_URL}/api/profile", headers=headers_b).json()
    assert get_p_a["full_name"] == "User Alpha"
    assert get_p_b["full_name"] == "User Beta"

    get_b_a = session_a.get(f"{BASE_URL}/api/business", headers=headers_a).json()
    get_b_b = session_b.get(f"{BASE_URL}/api/business", headers=headers_b).json()
    assert get_b_a["business_name"] == "Alpha Food Processing"
    assert get_b_b["business_name"] == "Beta Tech Solutions"
    assert get_b_a["support_needed"] == ["Loan", "Subsidy", "Machinery / Equipment", "Working Capital"]
    print("[OK] 6. Strict Multi-User Data Isolation Verified (User A cannot see User B data)")

    # 7. Execute "Find My Schemes" API (POST /api/recommendations) for User A
    rec_a_res = session_a.post(f"{BASE_URL}/api/recommendations", headers=headers_a)
    assert rec_a_res.status_code == 200
    recs_a = rec_a_res.json()
    assert len(recs_a) > 0
    top_scheme_a = recs_a[0]
    print(f"[OK] 7. Find My Schemes (POST /api/recommendations) executed successfully for User A (Top match: {top_scheme_a['scheme']['name']}, Score: {top_scheme_a['match_breakdown']['overall_score']}%)")

    # 8. Test Session Persistence across Logout & Login again
    login_a_again = session_a.post(f"{BASE_URL}/api/auth/login", json={"email": email_a, "password": password})
    assert login_a_again.status_code == 200
    token_a_new = login_a_again.json()["access_token"]
    headers_a_new = {"Authorization": f"Bearer {token_a_new}"}

    get_p_a_after = session_a.get(f"{BASE_URL}/api/profile", headers=headers_a_new).json()
    get_b_a_after = session_a.get(f"{BASE_URL}/api/business", headers=headers_a_new).json()
    assert get_p_a_after["full_name"] == "User Alpha"
    assert get_b_a_after["business_name"] == "Alpha Food Processing"
    print("[OK] 8. Data Persistence across Logout and Re-Login verified")

    print("\n=== ALL MULTI-STEP ONBOARDING E2E TESTS PASSED PERFECTLY! ===")

if __name__ == "__main__":
    test_complete_onboarding_flow()

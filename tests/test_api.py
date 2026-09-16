import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models.base import Base
from app.seed import seed_verified_data

# Initialize DB tables & seed data for pytest
Base.metadata.create_all(bind=engine)
seed_verified_data()

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_registration_and_login():
    email = "testuser@copilot.gov.in"
    password = "TestPassword@123"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={"email": email, "password": password})
    assert reg_res.status_code in [200, 400] # 400 if already created
    
    # 2. Login
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    
    # 3. Get /api/auth/me
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_profile_and_matching_flow():
    # Login as demo user
    login_res = client.post("/api/auth/login", json={"email": "user@copilot.gov.in", "password": "User@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Upsert Entrepreneur Profile
    p_res = client.put("/api/profile", headers=headers, json={
        "full_name": "Ramesh Patel",
        "age": 30,
        "gender": "Male",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "social_category": "OBC",
        "rural_urban": "Rural",
        "disability_status": False,
        "entrepreneur_type": "New",
        "business_stage": "Idea"
    })
    assert p_res.status_code == 200

    # 2. Upsert Business Profile
    b_res = client.put("/api/business", headers=headers, json={
        "business_name": "Patel Food Unit",
        "raw_description": "I want to start a small food processing unit in Uttar Pradesh and need 5 lakh for machinery",
        "industry": "Food Processing",
        "business_type": "Manufacturing",
        "business_stage": "Idea",
        "is_new_business": True,
        "estimated_investment": 500000.0,
        "funding_required": 500000.0,
        "purpose_of_funding": "Machinery Purchase",
        "business_location_state": "Uttar Pradesh",
        "business_location_district": "Varanasi",
        "is_rural": True
    })
    assert b_res.status_code == 200

    # 3. Get Recommendations
    rec_res = client.post("/api/recommendations", headers=headers)
    assert rec_res.status_code == 200
    recommendations = rec_res.json()
    assert len(recommendations) > 0
    top_match = recommendations[0]
    assert top_match["match_breakdown"]["overall_score"] > 50.0

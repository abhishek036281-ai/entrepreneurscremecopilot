import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_roadmap():
    session = requests.Session()
    # 1. Login
    email = f"test_user_{int(time.time())}@example.com"
    session.post(f"{BASE_URL}/api/auth/register", json={"full_name": "Roadmap Test User", "email": email, "password": "Password123"})
    login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": "Password123"})
    token = login_r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Roadmap
    r = session.get(f"{BASE_URL}/api/roadmap/1", headers=headers)
    print(f"GET /api/roadmap/1 status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    
    # 3. Toggle step
    r2 = session.post(f"{BASE_URL}/api/roadmap/1/toggle-step?step_index=2", headers=headers)
    print(f"POST /api/roadmap/1/toggle-step status: {r2.status_code}")
    
    # 4. Get Roadmap again
    r3 = session.get(f"{BASE_URL}/api/roadmap/1", headers=headers)
    print(json.dumps(r3.json(), indent=2))

test_roadmap()

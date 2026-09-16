import requests
import sqlite3
import os
import time

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = r"C:\Users\Divyanshu RAI\.gemini\antigravity\scratch\entrepreneur-scheme-copilot\backend\sql_app.db"

def test_real_authentication_flow():
    print("=== STARTING AUTHENTICATION & REGISTRATION END-TO-END VERIFICATION ===")
    session = requests.Session()

    test_name = "Test Entrepreneur"
    test_email = f"test_unique_{int(time.time())}@example.com"
    test_password = "Test@12345"
    reg_payload = {"full_name": test_name, "email": test_email, "password": test_password}

    reg_r = session.post(f"{BASE_URL}/api/auth/register", json=reg_payload)
    assert reg_r.status_code == 200, f"Registration failed: {reg_r.text}"
    print("[OK] 1. New User Registration API succeeded")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=?", (test_email,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None, "User record not found in database!"
    print("[OK] 2. User verified in SQLite database")

    login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": test_email, "password": test_password})
    assert login_r.status_code == 200
    token = login_r.json()["access_token"]
    print("[OK] 3. New Account Login succeeded")

    admin_login_r = session.post(f"{BASE_URL}/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    assert admin_login_r.status_code == 200
    assert admin_login_r.json().get("role") == "admin"
    print("[OK] 4. Pre-existing admin user login works normally")

if __name__ == "__main__":
    test_real_authentication_flow()

import os
import httpx
from db import supabase

email = "test_openclaw_2@titan.local"
password = "SecurePassword123!"

try:
    print("Signing up test user...")
    res = supabase.auth.sign_up({"email": email, "password": password})
    token = res.session.access_token
    user_id = res.user.id
except Exception:
    print("User already exists, signing in...")
    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
    token = res.session.access_token
    user_id = res.user.id

print(f"Got token! User ID: {user_id}")
print("Testing /api/chat endpoint...")

url = "http://127.0.0.1:8000/api/chat"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "message": "Hey Titan, I'm 28, I want to build muscle, and I am an intermediate lifter."
}

try:
    response = httpx.post(url, headers=headers, json=payload, timeout=20.0)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print("Failed to call API:", e)

import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("CRITICAL: Missing credentials in .env")
    exit(1)

supabase: Client = create_client(url, key)

print(f"Testing connectivity to {url}")
try:
    # Try to list users (requires service_role)
    users = supabase.auth.admin.list_users()
    print("SUCCESS: Successfully listed users. Service role key is VALID and has admin powers.")
except Exception as e:
    print(f"FAILURE: Cannot list users. The key might be an ANON key. Error: {e}")

# Test RLS bypass on 'users' table
test_id = str(uuid.uuid4())
print(f"Testing RLS bypass by inserting dummy user: {test_id}")
try:
    res = supabase.table("users").insert({"id": test_id, "name": "RLS Test User"}).execute()
    print("SUCCESS: Inserted user. RLS bypass is WORKING.")
    # Clean up
    supabase.table("users").delete().eq("id", test_id).execute()
    print("SUCCESS: Deleted test user.")
except Exception as e:
    print(f"FAILURE: RLS blocked the insert. This key is NOT bypassing RLS. Error: {e}")

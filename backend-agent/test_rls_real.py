import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

print("Fetching RLS policies for 'users' table...")
# We'll use a raw SQL query via standard Postgres RPC if possible, 
# or just try to fetch metadata if exposed.
# Actually, the easiest way to check if RLS is the problem is to try an insert with a user that DEFINITELY exists in auth.

try:
    # Get a real user ID from the auth table
    users_resp = supabase.auth.admin.list_users() # This returns a list of User objects
    
    if not users_resp:
        print("FAILURE: No users found in Auth table.")
        exit(1)
        
    # Try a real user (users_resp is a list)
    real_user = users_resp[0]
    uid = real_user.id
    email = real_user.email
    print(f"Testing insert for REAL user: {email} ({uid})")
    
    res = supabase.table("users").upsert({"id": uid, "name": "Diagnostic Update"}).execute()
    print(f"SUCCESS: Upsert worked! Result: {res.data}")
except Exception as e:
    import traceback
    print(f"FAILURE: Error with real user: {e}")
    traceback.print_exc()

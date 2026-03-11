import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

print(f"DB CONFIG: URL found: {bool(url)}")
if key:
    masked_key = f"{key[:10]}...{key[-5:]}" if len(key) > 15 else "INVALID_LENGTH"
    print(f"DB CONFIG: Service Role Key length: {len(key)}, Masked: {masked_key}")
else:
    print("DB CONFIG: Service Role Key MISSING")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")

supabase: Client = create_client(url, key)

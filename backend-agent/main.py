import os
import uuid
import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import create_coach_agent
from db import supabase

app = FastAPI(title="Fitness Coach AI API")

# Allow Next.js frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://fitness-brown-phi.vercel.app"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id: int, text: str):
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": ""
    }
    try:
        httpx.post(url, json=payload)
    except Exception as e:
        print(f"Failed to push message to Telegram: {e}")

@app.post(f"/api/telegram/{{TELEGRAM_TOKEN}}")
async def telegram_webhook(request: Request):
    update = await request.json()
    
        # Extract message data
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        
        # We must map Telegram chat_ids to valid `auth.users` UUIDs to satisfy Postgres FK constraints
        email = f"tg_{chat_id}@titan.local"
        password = "SecureTgBotPassword123!"
        
        try:
            auth_resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
            mapped_user_id = auth_resp.user.id
        except Exception as e_sign_in:
            try:
                user_data = supabase.auth.admin.create_user({
                    "email": email, 
                    "password": password, 
                    "email_confirm": True
                })
                mapped_user_id = user_data.user.id
            except Exception as e_create:
                print(f"Auth user provisioning error: {e_create}")
                send_telegram_message(chat_id, f"DEBUG AUTH CRASH: Sign In failed with `{e_sign_in}` and Create User failed with `{e_create}`. Because of the database constraints I cannot proceed.")
                return {"status": "error"}

        if coach_agent:
            try:
                from agent import run_agent
                
                # 1. Ensure User Profile exists
                user_exists = supabase.table("users").select("id").eq("id", mapped_user_id).execute()
                if not user_exists.data:
                    supabase.table("users").insert({"id": mapped_user_id, "name": "Telegram User"}).execute()

                # 2. Setup Session
                session_exists = supabase.table("chat_sessions").select("id").eq("id", mapped_user_id).execute()
                if not session_exists.data:
                    supabase.table("chat_sessions").insert({"id": mapped_user_id, "user_id": mapped_user_id, "title": "Telegram Chat"}).execute()

                # 3. Save User Message to DB
                supabase.table("chat_logs").insert({
                    "user_id": mapped_user_id,
                    "session_id": mapped_user_id,
                    "message": text,
                    "role": "user"
                }).execute()

                # 4. Fetch DB memory for this chat
                db_history = supabase.table("chat_logs").select("role, message").eq("session_id", mapped_user_id).order("created_at", desc=False).execute()
                historical_messages = db_history.data[:-1] if db_history.data else []
                history_list = [{"role": row["role"], "text": row["message"]} for row in historical_messages[-15:]]

                # 5. Run Agent
                response_text = run_agent(coach_agent, text, mapped_user_id, chat_history=history_list)
                
                # 6. Save Agent Response & Reply to Telegram
                if response_text:
                    supabase.table("chat_logs").insert({
                        "user_id": mapped_user_id,
                        "session_id": mapped_user_id,
                        "message": str(response_text),
                        "role": "agent"
                    }).execute()
                    
                send_telegram_message(chat_id, str(response_text))
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error processing Telegram msg: {e}")
                send_telegram_message(chat_id, f"I hit a snag.\n\n`{error_trace}`")

    return {"status": "ok"}

# Initialize the OpenClaw Agent
try:
    coach_agent = create_coach_agent()
except Exception as e:
    print(f"Warning: Failed to initialize coach agent: {e}")
    coach_agent = None

from typing import Optional
from fastapi import Header

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    session_id: Optional[str] = None

class SessionRequest(BaseModel):
    user_id: Optional[str] = None
    title: str = "New Chat"

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Token empty")
    try:
        # Isolated client to verify JWT without polluting global state
        from supabase import create_client
        from db import url, key
        # We MUST use the service_role key to initialize the client so it has permission to verify auth tokens
        auth_client = create_client(url, key)
        user_resp = auth_client.auth.get_user(token)
        
        if not user_resp or not user_resp.user:
            raise HTTPException(status_code=401, detail="Token is invalid or has expired")
        return user_resp.user.id
    except Exception as e:
        print(f"Token Verification Failed: {e}")
        raise HTTPException(status_code=401, detail=f"Verify token error: {e}")

@app.post("/api/sessions")
async def create_session(request: SessionRequest, authorization: str = Header(None)):
    user_id = await verify_token(authorization)
    try:
        res = supabase.table("chat_sessions").insert({
            "user_id": user_id,
            "title": request.title
        }).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
        return {"session_id": res.data[0]["id"]}
    except Exception as e:
        print(f"Error creating session: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{user_id}")
async def get_sessions(user_id: str, authorization: str = Header(None)):
    auth_user_id = await verify_token(authorization)
    if auth_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: IDOR blocked")
        
    try:
        res = supabase.table("chat_sessions") \
            .select("id, title, created_at") \
            .eq("user_id", user_id) \
            .order("created_at", desc=False) \
            .execute()
        return {"sessions": res.data}
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, authorization: str = Header(None)):
    if not coach_agent:
        raise HTTPException(status_code=500, detail="AI Agent is not initialized properly.")
        
    user_id = await verify_token(authorization)
        
    try:
        # 1. Ensure User Profile exists (auto-create if missing from Auth)
        # This prevents foreign key violations in chat_logs
        user_exists = supabase.table("users").select("id").eq("id", user_id).execute()
        
        if not user_exists.data:
            supabase.table("users").insert({"id": user_id, "name": "New User"}).execute()

        # 1.5 Handle Session Logic
        session_id = request.session_id
        if session_id:
            # Verify the session owned by user
            session_check = supabase.table("chat_sessions").select("user_id").eq("id", session_id).execute()
            if not session_check.data or session_check.data[0]["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Session does not belong to you")
        else:
            # Create a new session automatically if not provided
            title = request.message[:30] + "..." if len(request.message) > 30 else request.message
            session_res = supabase.table("chat_sessions").insert({
                "user_id": user_id,
                "title": title
            }).execute()
            if session_res.data:
                session_id = session_res.data[0]["id"]
            else:
                raise Exception("Could not create underlying session.")

        # 2. Save User Message to DB
        supabase.table("chat_logs").insert({
            "user_id": user_id,
            "session_id": session_id,
            "message": request.message,
            "role": "user"
        }).execute()

        # Fetch recent chat history to provide context to the agent
        db_history = supabase.table("chat_logs").select("role, message").eq("session_id", session_id).order("created_at", desc=False).execute()
        
        historical_messages = db_history.data[:-1] if db_history.data else []
        history_list = [{"role": row["role"], "text": row["message"]} for row in historical_messages[-15:]]

        # 3. Run the Langchain Agent
        from agent import run_agent
        response_text = run_agent(coach_agent, request.message, user_id, chat_history=history_list)
        print(f"Agent final response: {response_text}")
        
        # 3. Save Agent Response to DB
        if response_text:
            supabase.table("chat_logs").insert({
                "user_id": user_id,
                "session_id": session_id,
                "message": str(response_text),
                "role": "agent"
            }).execute()
        
        return {"reply": str(response_text), "session_id": session_id}
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}")
async def get_chat_history(session_id: str, authorization: str = Header(None)):
    user_id = await verify_token(authorization)
    try:
        # Verify ownership
        session_check = supabase.table("chat_sessions").select("user_id").eq("id", session_id).execute()
        if not session_check.data or session_check.data[0]["user_id"] != user_id:
             raise HTTPException(status_code=403, detail="Session does not belong to you")

        response = supabase.table("chat_logs") \
            .select("role, message, created_at") \
            .eq("session_id", session_id) \
            .order("created_at", desc=False) \
            .execute()
        
        history = [{"role": row["role"], "text": row["message"]} for row in response.data]
        return {"history": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "agent_loaded": coach_agent is not None}


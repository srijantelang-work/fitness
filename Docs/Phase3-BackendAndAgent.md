# Phase 3: Backend API and OpenClaw Agent

In this phase, we build the Node.js or Python backend that acts as the bridge separating our frontend from the AI logic.

## 1. Environment Setup

*Assuming Python for backend due to robust LLM/Agent libraries like OpenClaw:*

```bash
cd backend-agent
# Ensure your virtual environment is active
source venv/bin/activate
# Install necessary libraries
pip install fastapi "uvicorn[standard]" supabase google-generativeai pydantic python-dotenv
```
*(Note: If OpenClaw is a Node.js library, you would initialize an Express app instead. We will use conceptual Python syntax for this phase to illustrate standard LLM development.)*

## 2. Setting Up Supabase Client

Create a file `db.py` to handle database connections:

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)
```

## 3. Creating Agent Tools

The agent needs tools to interact with our Supabase database. Create `tools.py`:

```python
from db import supabase

def update_user_profile(user_id: str, age: int, goals: list, experience: str):
    """Updates the user profile data in Supabase."""
    data = {"age": age, "fitness_goals": goals, "experience_level": experience}
    response = supabase.table("users").update(data).eq("id", user_id).execute()
    return f"Profile updated for user {user_id}. Data: {data}"

def generate_workout_plan(user_id: str, plan_name: str, days: int, focus: str):
    """(Stub) Uses Gemini to construct a structured JSON plan, then saves to DB."""
    # Concept: Run a secondary Gemini prompt requesting strict JSON.
    fake_json = {"day_1": focus, "length": f"{days} days"}
    
    data = {
        "user_id": user_id,
        "plan_name": plan_name,
        "plan_json": fake_json
    }
    response = supabase.table("workout_plans").insert(data).execute()
    return "Plan successfully generated and saved."

def log_workout(user_id: str, exercises: list, duration: int):
    """Saves a completed workout session to the logs."""
    data = {
        "user_id": user_id,
        "exercises_completed": exercises,
        "duration_minutes": duration
    }
    supabase.table("workout_logs").insert(data).execute()
    return "Workout logged successfully."
```

## 4. Initializing OpenClaw and Gemini

Create `agent.py`. This is where we define the System Prompt and wire the tools to the engine.

```python
import os
from openclaw import Agent # Note: Adjust import based on official OpenClaw docs
from tools import update_user_profile, generate_workout_plan, log_workout

system_prompt = """
You are "Titan", an elite Fitness Coach AI. 
Your goal is to help your client achieve their fitness goals safely and consistently.
Always use tools to update user profiles, generate plans, and log workouts when the user implies it.
"""

def create_coach_agent():
    agent = Agent(
        llm="gemini-provider", 
        api_key=os.environ.get("GEMINI_API_KEY"),
        system_prompt=system_prompt,
        tools=[update_user_profile, generate_workout_plan, log_workout]
    )
    return agent
```

## 5. Building the API Endpoints

Create `main.py` using FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agent import create_coach_agent

app = FastAPI()
coach_agent = create_coach_agent()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # 1. Provide the user_id as context to the agent
    # 2. Feed the message to OpenClaw
    response_text = coach_agent.run(request.message, context={"user_id": request.user_id})
    
    return {"reply": response_text}

# To run the server:
# uvicorn main:app --reload --port 8000
```

---
**Next Step:** Proceed to **Phase 4: Frontend Web App** to build the UI where users will actually chat with Titan.

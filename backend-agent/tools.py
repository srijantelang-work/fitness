from db import supabase
from typing import List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class UpdateProfileArgs(BaseModel):
    user_id: str = Field(description="The UUID of the user")
    age: int = Field(description="The user's age")
    goals: List[str] = Field(description="A list of fitness goals (e.g., ['Lose weight', 'Build muscle'])")
    experience: str = Field(description="The user's experience level ('beginner', 'intermediate', 'advanced')")

@tool(args_schema=UpdateProfileArgs)
def update_user_profile(user_id: str, age: int, goals: List[str], experience: str) -> str:
    """Updates the user profile data in Supabase."""
    data = {"age": age, "fitness_goals": goals, "experience_level": experience}
    try:
        response = supabase.table("users").update(data).eq("id", user_id).execute()
        return f"Profile updated for user {user_id}. Data: {data}"
    except Exception as e:
        return f"Error updating profile: {str(e)}"

class GeneratePlanArgs(BaseModel):
    user_id: str = Field(description="The UUID of the user")
    plan_name: str = Field(description="The name of the workout plan")
    days: int = Field(description="Number of days per week")
    focus: str = Field(description="The primary focus of the plan")

@tool(args_schema=GeneratePlanArgs)
def generate_workout_plan(user_id: str, plan_name: str, days: int, focus: str) -> str:
    """Constructs a structured workout plan and saves it to the DB."""
    fake_json = {
        "day_1": {"focus": focus, "exercises": []},
        "length_days": days
    }
    
    data = {
        "user_id": user_id,
        "plan_name": plan_name,
        "target_goal": focus,
        "plan_json": fake_json
    }
    try:
        response = supabase.table("workout_plans").insert(data).execute()
        return f"Plan '{plan_name}' successfully generated and saved."
    except Exception as e:
        return f"Error saving plan: {str(e)}"

class LogWorkoutArgs(BaseModel):
    user_id: str = Field(description="The UUID of the user")
    exercises: List[Dict[str, Any]] = Field(description="A list of dicts representing exercises (e.g., [{'name': 'Squat', 'sets': 3, 'reps': 10, 'weight': 100}])")
    duration: int = Field(description="The duration of the workout in minutes")

@tool(args_schema=LogWorkoutArgs)
def log_workout(user_id: str, exercises: List[Dict[str, Any]], duration: int) -> str:
    """Saves a completed workout session to the logs."""
    data = {
        "user_id": user_id,
        "exercises_completed": exercises,
        "duration_minutes": duration
    }
    try:
        supabase.table("workout_logs").insert(data).execute()
        return "Workout logged successfully."
    except Exception as e:
        return f"Error logging workout: {str(e)}"

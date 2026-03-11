from db import supabase
from typing import List, Dict, Any

def update_user_profile(user_id: str, age: int, goals: List[str], experience: str) -> str:
    """Updates the user profile data in Supabase.
    
    Args:
        user_id: The UUID of the user.
        age: The user's age.
        goals: A list of fitness goals (e.g., ['Lose weight', 'Build muscle']).
        experience: The user's experience level ('beginner', 'intermediate', 'advanced').
    """
    data = {"age": age, "fitness_goals": goals, "experience_level": experience}
    try:
        response = supabase.table("users").update(data).eq("id", user_id).execute()
        return f"Profile updated for user {user_id}. Data: {data}"
    except Exception as e:
        return f"Error updating profile: {str(e)}"

def generate_workout_plan(user_id: str, plan_name: str, days: int, focus: str) -> str:
    """Constructs a structured workout plan and saves it to the DB.
    
    Args:
        user_id: The UUID of the user.
        plan_name: The name of the workout plan.
        days: Number of days per week.
        focus: The primary focus of the plan.
    """
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

def log_workout(user_id: str, exercises: List[Dict[str, Any]], duration: int) -> str:
    """Saves a completed workout session to the logs.
    
    Args:
        user_id: The UUID of the user.
        exercises: A list of dicts representing exercises (e.g., [{'name': 'Squat', 'sets': 3, 'reps': 10, 'weight': 100}]).
        duration: The duration of the workout in minutes.
    """
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

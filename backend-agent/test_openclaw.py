import os
from openclaw import Agent
from tools import update_user_profile, generate_workout_plan, log_workout

agent = Agent(tools=[update_user_profile, generate_workout_plan, log_workout])
res = agent.run("hi", [])
print(res)

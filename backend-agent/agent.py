import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from tools import update_user_profile, generate_workout_plan, log_workout

system_prompt = """
You are "Titan", a no-nonsense, elite strength and conditioning coach. You speak like a knowledgeable, slightly gritty veteran athlete. You hate fluff, excuses, and typical customer service language. Keep it brief, punchy, and casual. Speak like you’re sending a text or a voice note on WhatsApp. Use contractions.

CRITICAL COMMUNICATION RULES (THE "BAN LIST"):
1. NEVER use generic AI praise. NEVER say 'Great job!', 'That's a fantastic goal', 'I understand exactly how you feel!', 'Well done!', or 'I am happy to help.' 
2. Do NOT act like a customer service rep or an AI assistant. You do not praise people just for showing up. You give them a nod, analyze their data, and assign the next task. A simple 'Copy that' or 'Makes sense' is enough.

ONBOARDING RULES & VARIABILITY:
1. When a new user says hello, you need to gather three things: Age, Fitness Goals, and Experience Level.
2. IMPORTANT: Ask these questions ONE AT A TIME. Do not ask for all three in one message. Make the chat interactive.
3. NEVER ask these questions the exact same way twice. Use conversational transitions. (e.g., Instead of 'What is your experience level?', try 'Have you ever touched a barbell before, or are we starting fresh?'). Let your AI brain generate unique phrasing every single time.
4. STRICT VALIDATION: You CANNOT move forward with training until all 3 pieces of information are gathered. If the user dodges the question, talks about something else, or gives a non-answer, DO NOT answer their question. Gently but firmly troll them for stalling and RE-ASK the exact data point you need. You control the flow.
5. AGE PARSING: The user might write their age as a number ("19") or as a word ("nineteen" or "twenty two"). You must be smart enough to recognize both as valid ages and proceed.
6. Once you have gathered all three pieces of information, USE the `update_user_profile` tool to save it. 

ADVISING, HUMOR, & ACCOUNTABILITY RULES:
1. After you have updated the user's profile with their ONBOARDING info, DO NOT STOP. The system will feed you a confirmation that the profile was updated. You MUST then enthusiastically (but grittily) generate a workout plan using `generate_workout_plan` and present it to them.
2. OPINIONS: You have strong opinions. You prefer compound lifts over machines. You believe sleep and real food are more important than supplements or fad diets. If a user asks about a fad diet, politely but firmly tell them it's a waste of time and point them back to the basics.
3. TOUGH LOVE: If the user says they missed a workout, are feeling lazy, or making excuses, do not accept it. Challenge them respectfully. Remind them that consistency is the only metric that matters. If they haven't logged a workout in their recent messages, ask them where they've been. Don't baby them.
4. SARCASM: You have a dry, sarcastic sense of humor. If the user asks a ridiculous or lazy question (e.g., 'Will eating a donut ruin my life?' or 'How do I get abs in 2 days?'), respond with dry, sarcastic humor before dropping the actual science. (Example: 'Yes, a single donut will instantly erase all your muscle mass. Just kidding. Eat the donut, then go do some heavy squats.')
5. SCIENCE: If the user asks a complex science question, explain it simply using a real-world analogy (like comparing muscles to car engines). Don't give a textbook answer.
6. INJURY: If the user says they got injured, switch immediately to cautious, empathetic tone. Tell them to see a doctor if it's serious, and focus only on recovery/mobility.
7. MEMORY: Use memory context gracefully. If they mentioned being tired yesterday, ask if they recovered today.
8. FORMATTING. NEVER use markdown tables, excessive bullet points, or bold text. Format your text in short paragraphs. Use line breaks for emphasis. Type like a human texting. Very occasionally use an emoji, but never more than one per message, and only use these emojis: 🦾, 😤, 🧬, 🥩, 📉.
9. BOUNDARIES (OFF-TOPIC): You are a strength coach, not ChatGPT. If the user asks you about politics, coding, movie trivia, or anything utterly unrelated to fitness, diet, or mindset, TROLL THEM MERCILESSLY. Tell them they are currently wasting oxygen and need to focus. Order them to do 20 pushups for asking a stupid question and redirect the conversation violently back to their fitness goals.
10. BREVITY: DO NOT give big, long explanations for workout plans or diet advice. Cut to the chase. Give the exact information needed in the shortest way possible. Bullet point the exact exercises, reps, and sets, and move on. No fluff.

Always provide actionable advice and continue the conversation like a real coach checking in.
"""

def create_coach_agent():
    # Initialize the Gemini model via Langchain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.2
    )
    
    # Bind our Python tools to the LLM so it can invoke them
    tools = [update_user_profile, generate_workout_plan, log_workout]
    agent_with_tools = llm.bind_tools(tools)
    
    return agent_with_tools

def run_agent(agent_with_tools, user_message: str, user_id: str, chat_history: list = None):
    """
    Utility function to run the Langchain agent with tools.
    Now supports history injection and a cyclic execution loop to allow tools to return data to the LLM.
    """
    messages = [
        SystemMessage(content=system_prompt + f"\n\nCurrent Context User ID: {user_id}")
    ]
    
    # Inject previous history to cure amnesia
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["text"]))
            elif msg["role"] == "agent":
                messages.append(AIMessage(content=msg["text"]))
                
    messages.append(HumanMessage(content=user_message))
    
    # Allow the agent to loop up to 3 times for tool execution
    for _ in range(3):
        response = agent_with_tools.invoke(messages)
        
        # If the LLM just replied with text and no tools, we're done
        if not response.tool_calls:
            return response.content
            
        # Agent decided to call tools, append its request to memory
        messages.append(response)
        
        # Execute all requested tools
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            tool_result = ""
            try:
                if tool_name == "update_user_profile":
                    tool_result = update_user_profile.invoke(tool_args)
                elif tool_name == "generate_workout_plan":
                    tool_result = generate_workout_plan.invoke(tool_args)
                elif tool_name == "log_workout":
                    tool_result = log_workout.invoke(tool_args)
                else:
                    tool_result = f"Unknown tool requested: {tool_name}"
            except Exception as e:
                tool_result = f"Error executing tool: {str(e)}"
                
            # Send the result BACK to the agent so it can keep talking
            messages.append(ToolMessage(tool_call_id=tool_id, name=tool_name, content=str(tool_result)))
            
    # Fallback if loop exhausts
    return response.content if response.content else "I'm processing your fitness plan, give me a moment to update everything!"

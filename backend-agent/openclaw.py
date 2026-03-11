import os
from google import genai
from google.genai import types

class Agent:
    def __init__(self, model_name="gemini-2.5-flash", tools=None, system_prompt=None, temperature=0.2):
        self.model_name = model_name
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.temperature = temperature
        # Ensure API key is loaded
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def run(self, user_message, chat_history=None):
        contents = []
        
        # Load history
        if chat_history:
            for msg in chat_history:
                # Map role. Gemini supports 'user' and 'model'
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(msg["text"])]))
                
        # Append current user message
        contents.append(types.Content(role="user", parts=[types.Part.from_text(user_message)]))
        
        config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            tools=self.tools if self.tools else None,
            temperature=self.temperature
        )
        
        # Tool-calling loop natively managed by our OpenClaw framework (up to 3 iterations)
        for _ in range(3):
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # If the model didn't call any tools, we are done
            if not response.function_calls:
                return response.text
                
            # Append the model's function call block into conversational history
            contents.append(response.candidates[0].content)
            
            # Execute each requested tool and collect results
            parts = []
            for function_call in response.function_calls:
                name = function_call.name
                args = function_call.args
                
                # Locate Python tool function
                tool_func = next((t for t in self.tools if t.__name__ == name), None)
                if tool_func:
                    try:
                        result = tool_func(**args)
                    except Exception as e:
                        result = f"Error executing tool: {str(e)}"
                else:
                    result = f"Error: Unknown tool {name}"
                    
                # Store the tool output explicitly as string mapping
                parts.append(types.Part.from_function_response(
                    name=name,
                    response={"result": str(result)}
                ))
                
            # Put the tool results back into the context from the 'user'
            contents.append(types.Content(role="user", parts=parts))
            
        # Fallback if we exceeded tool iteration limit
        return response.text or "I'm processing your fitness plan, give me a moment to update everything!"

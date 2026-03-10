# Phase 5: Telegram Bot Integration (Optional)

In this phase, we connect our backend to Telegram, allowing users to interact with the exact same AI coach (and same Supabase database) directly from their phone.

## 1. Setting Up the Webhook Route

In your backend (`main.py` if using FastAPI), you need an endpoint that Telegram can send messages to:

```python
from fastapi import Request

# Replace this with your actual Bot Token from BotFather
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.post(f"/api/telegram/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    update = await request.json()
    
    # Extract message data
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        telegram_name = update["message"]["chat"].get("first_name", "User")
        text = update["message"]["text"]
        
        # 1. Map Telegram chat_id to Supabase user_id
        # We query the `users` table. If we have a telegram_chat_id column, we find them.
        # If not, we might create a ghost user or ask them to link accounts.
        # For simplicity, let's assume `chat_id` perfectly maps to a string `user_id`.
        mapped_user_id = str(chat_id) 
        
        # 2. Pass to the exact same OpenClaw agent from Phase 3
        agent_reply = coach_agent.run(text, context={"user_id": mapped_user_id})
        
        # 3. Send the reply back to Telegram
        send_telegram_message(chat_id, agent_reply)

    return {"status": "ok"}
```

## 2. Sending Messages Back to Telegram

Create a helper function to fire POST requests back to Telegram's API:

```python
import httpx

def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown" # Allows bolding, bullet points
    }
    # Fire and forget (or use await httpx.AsyncClient)
    httpx.post(url, json=payload)
```

## 3. Registering the Webhook with Telegram

Telegram needs to know where your backend lives. 
If you are running locally, you must expose your `localhost:8000` to the public internet using a tool like **ngrok**.

```bash
# In terminal
ngrok http 8000
```
Ngrok will give you an HTTPS URL (e.g., `https://1234-abcd.ngrok-free.app`).

Run this `curl` command to tell Telegram to send messages to your new webhook URL:

```bash
curl -F "url=https://YOUR_NGROK_URL.ngrok-free.app/api/telegram/YOUR_TELEGRAM_TOKEN" \
https://api.telegram.org/botYOUR_TELEGRAM_TOKEN/setWebhook
```

*Note: You must replace `YOUR_NGROK_URL` and `YOUR_TELEGRAM_TOKEN` with your actual values.*

## 4. Testing the Bot

1. Ensure your backend server is running (`uvicorn main:app`).
2. Ensure ngrok is running.
3. Ensure you ran the `setWebhook` command successfully.
4. Open the Telegram app, search for your bot, and send a message.
5. Watch your backend terminal. It should receive the message, process it through OpenClaw/Gemini, and your Bot should reply in the Telegram app!

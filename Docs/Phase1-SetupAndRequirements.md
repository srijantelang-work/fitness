# Phase 1: Setup and Requirements

This phase outlines everything you need to start building the Fitness Coach AI Agent. We will gather the necessary API keys, set up accounts, and initialize the project structure.

## 1. Prerequisites & Accounts Needed

Before writing any code, ensure you have the following installed and accounts created:

- **Node.js (v18+)**: Required for running the frontend (Next.js) and potentially the backend if using Node.
  - *How to get it:* Download and install from [nodejs.org](https://nodejs.org/).
- **Git**: For version control.
  - *How to get it:* Download from [git-scm.com](https://git-scm.com/).
- **Supabase Account**: Used for our PostgreSQL database and user authentication.
  - *How to get it:* Sign up at [supabase.com](https://supabase.com/). The free tier is sufficient for this project.
- **Google Cloud / AI Studio Account**: To access the Gemini API for our LLM.
  - *How to get it:* Go to [Google AI Studio](https://aistudio.google.com/) and sign in with a Google account.
- **Telegram Account (Optional but recommended)**: If you plan to build the Telegram bot interface.

## 2. Acquiring Core API Keys

### A. Supabase Keys
1. Log in to Supabase and click **"New Project"**.
2. Name your project (e.g., "FitnessCoachAI") and securely generate a database password.
3. Once the project is provisioned, go to **Project Settings -> API** in the sidebar.
4. Copy the **Project URL** and the **anon / public anon key**.
5. *Keep these safe; you will need them for your frontend `.env` file.*

### B. Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **"Create API Key"**.
3. Create a key in a new or existing Google Cloud project.
4. *Copy the generated key. You will need this for your backend `.env` file.*

### C. Telegram Bot Token (If implementing Phase 5)
1. Open the Telegram app and search for the user `@BotFather`.
2. Start a chat and type `/newbot`.
3. Follow the prompts to name your bot and give it a username (ending in `bot`).
4. `@BotFather` will reply with a message containing your **HTTP API Token**.
5. *Save this token for your backend `.env` file.*

## 3. Initial Project Scaffolding

Open your terminal and establish the overarching project structure:

```bash
# Create the root folder for the entire project
mkdir fitness-coach-ai
cd fitness-coach-ai

# Scaffold the Next.js frontend (We'll expand on this in Phase 4)
npx create-next-app@latest frontend-web
# (Accept the default prompts: use TypeScript, ESLint, Tailwind CSS, App Router)

# Scaffold the backend directory
mkdir backend-agent
cd backend-agent
# If using Python:
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn supabase google-generativeai pydantic openclaw
# If using Node.js:
# npm init -y
# npm install express @supabase/supabase-js @google/generativeai openclaw dotenv

cd ..
```

## 4. Environment Variables Checklist

By the end of Phase 1, you should have the following values ready to inject into your `.env` files:

**Frontend (`frontend-web/.env.local`):**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend (`backend-agent/.env`):**
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key # (Found in Supabase API settings, used to bypass RLS in backend)
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token # (Optional)
```

---
**Next Step:** Proceed to **Phase 2: Database and Supabase Setup** to create the tables necessary to store user profiles and workout logs.

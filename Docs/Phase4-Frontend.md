# Phase 4: Frontend Web App (Next.js)

In this phase, we connect the Next.js scaffold from Phase 1 to Supabase for authentication, and build the chat interface.

## 1. Installing Frontend Dependencies

Inside the `frontend-web` directory:

```bash
cd frontend-web
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
npm install lucide-react # For icons
```

## 2. Supabase Client Setup

Create a helper file `lib/supabase.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

## 3. Implementing Authentication (Login Page)

Create `app/login/page.tsx`:

```tsx
'use client'
import { useState } from 'react'
import { supabase } from '@/lib/supabase'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSignUp = async () => {
    await supabase.auth.signUp({ email, password })
    alert("Check your email for the login link!")
  }

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (!error) window.location.href = '/'
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Fitness Coach Login</h1>
      <input 
        type="email" 
        placeholder="Email" 
        onChange={e => setEmail(e.target.value)} 
        className="border p-2 mb-2 text-black"
      />
      <input 
        type="password" 
        placeholder="Password" 
        onChange={e => setPassword(e.target.value)} 
        className="border p-2 mb-4 text-black"
      />
      <div className="flex gap-2">
        <button onClick={handleLogin} className="bg-blue-500 text-white p-2 rounded">Login</button>
        <button onClick={handleSignUp} className="bg-green-500 text-white p-2 rounded">Sign Up</button>
      </div>
    </div>
  )
}
```

## 4. Building the Chat Interface

Modify the main page `app/page.tsx` to hold the chat logic:

```tsx
'use client'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [messages, setMessages] = useState<{role: string, text: string}[]>([])
  const [input, setInput] = useState('')
  const [user, setUser] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUser(user)
      } else {
        router.push('/login')
      }
    })
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || !user) return

    // Immediately show user message
    const newMessages = [...messages, { role: 'user', text: input }]
    setMessages(newMessages)
    setInput('')

    try {
      // Call the Python/Node backend we built in Phase 3
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, message: input })
      })
      
      const data = await res.json()
      
      // Show Agent reply
      setMessages([...newMessages, { role: 'agent', text: data.reply }])
    } catch (e) {
      console.error(e)
    }
  }

  if (!user) return <div>Loading...</div>

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Coaching Session</h1>
      
      <div className="flex-1 overflow-y-auto mb-4 border p-4 rounded bg-gray-50 dark:bg-gray-900">
        {messages.map((m, i) => (
          <div key={i} className={`mb-4 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'}`}>
              {m.text}
            </span>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask your coach anything..."
          className="flex-1 border p-3 rounded text-black"
        />
        <button onClick={sendMessage} className="bg-black text-white px-6 py-3 rounded">
          Send
        </button>
      </div>
    </div>
  )
}
```

---
**Next Step:** Proceed to **Phase 5: Telegram Bot Integration** if you want to make the agent available via mobile chat.

'use client'
import { useState, useEffect, useRef } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { Send, LogOut, Activity, Plus, MessageSquare, Menu, X, Sun, Moon } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useTheme } from 'next-themes'
import { type User } from '@supabase/supabase-js'

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  text: string;
}

// ----------------------
// Extracted Components
// ----------------------

const ChatMessageBubble = ({ message }: { message: ChatMessage }) => {
  const isUser = message.role === 'user';
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] md:max-w-[75%] p-4 text-base shadow-sm ${isUser
          ? 'bg-brand-orange text-white rounded-2xl rounded-tr-sm'
          : 'bg-white dark:bg-[#1a1816] text-brand-charcoal dark:text-zinc-200 rounded-2xl rounded-tl-sm border border-brand-gray dark:border-zinc-800'
          }`}
      >
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.text}</div>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-zinc-100 dark:prose-pre:bg-zinc-800">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.text}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

const ChatInputArea = ({
  input,
  setInput,
  sendMessage,
  isTyping
}: {
  input: string;
  setInput: (v: string) => void;
  sendMessage: () => void;
  isTyping: boolean;
}) => {
  return (
    <div className="p-4 bg-white dark:bg-[#1a1816] border-t border-brand-gray dark:border-zinc-800">
      <div className="max-w-3xl mx-auto w-full flex gap-3 relative">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isTyping) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Log your workout or ask a question..."
          className="flex-1 bg-brand-gray dark:bg-zinc-800/50 border border-transparent p-4 rounded-2xl text-brand-charcoal dark:text-zinc-100 focus:outline-none focus:bg-white dark:focus:bg-zinc-800 focus:border-brand-orange/30 focus:ring-4 focus:ring-brand-orange/10 transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-500 pr-14"
          autoFocus
          disabled={isTyping}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || isTyping}
          className="absolute right-2 top-2 bottom-2 bg-brand-orange disabled:bg-zinc-200 dark:disabled:bg-zinc-800 disabled:text-zinc-400 dark:disabled:text-zinc-600 hover:brightness-110 text-white p-3 rounded-xl transition-all shadow-md shadow-brand-orange/20 disabled:shadow-none flex items-center justify-center transform active:scale-95"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};


// ----------------------
// Main Application
// ----------------------

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [input, setInput] = useState('')

  const [user, setUser] = useState<User | null>(null)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  const router = useRouter()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { theme, setTheme, systemTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch by delaying theme-dependent UI
  useEffect(() => {
    setMounted(true)
    if (window.innerWidth >= 768) {
      setIsSidebarOpen(true)
    }
  }, [])

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.user) {
        setUser(session.user)
        fetchSessions(session.user.id)
      } else {
        router.push('/login')
      }
      setIsCheckingAuth(false)
    }
    checkAuth()
  }, [router])

  const fetchSessions = async (userId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const { data: { session } } = await supabase.auth.getSession()

      const res = await fetch(`${apiUrl}/api/sessions/${userId}`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`
        }
      })
      if (res.ok) {
        const data = await res.json()
        setSessions(data.sessions)
        if (data.sessions.length > 0 && !currentSessionId) {
          setCurrentSessionId(data.sessions[0].id)
        }
      }
    } catch (e) {
      console.error("Failed to fetch sessions:", e)
    }
  }

  // Refetch history when switching sessions
  useEffect(() => {
    if (currentSessionId) {
      fetchHistory(currentSessionId)
    } else {
      setMessages([])
    }
  }, [currentSessionId])

  const fetchHistory = async (sessionId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const { data: { session } } = await supabase.auth.getSession()
      const res = await fetch(`${apiUrl}/api/history/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`
        }
      })
      if (res.ok) {
        const data = await res.json()
        setMessages(data.history.map((msg: any, index: number) => ({
          id: `hist-${index}`,
          role: msg.role,
          text: msg.text
        })))
      }
    } catch (e) {
      console.error("Failed to fetch history:", e)
    }
  }

  const startNewChat = () => {
    setCurrentSessionId(null)
    setMessages([])
    if (window.innerWidth < 768) setIsSidebarOpen(false)
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  const sendMessage = async () => {
    if (!input.trim() || !user || isTyping) return

    const newMessage: ChatMessage = { id: Date.now().toString(), role: 'user', text: input }
    setMessages(prev => [...prev, newMessage])
    setInput('')
    setIsTyping(true)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const { data: { session } } = await supabase.auth.getSession()

      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`
        },
        body: JSON.stringify({ message: input, session_id: currentSessionId })
      })

      if (res.ok) {
        const data = await res.json()

        setMessages(prev => [...prev, { id: `resp-${Date.now()}`, role: 'agent', text: data.reply }])

        // If it was a new chat, update session ID and silently refresh sidebar list
        if (!currentSessionId && data.session_id) {
          // Temporarily skip refetching history to avoid race condition visual flashes
          const oldSessionId = currentSessionId;
          setCurrentSessionId(data.session_id);

          if (!oldSessionId && sessions.length === 0) {
            fetchSessions(user.id);
          } else {
            setSessions(prev => [{ id: data.session_id, title: input.substring(0, 30) + "...", created_at: new Date().toISOString() }, ...prev])
          }
        }
      } else {
        console.error("Chat error:", await res.text())
        setMessages(prev => [...prev, { id: `error-${Date.now()}`, role: 'agent', text: "Sorry, I had trouble processing that. Please try again." }])
      }
    } catch (e) {
      console.error(e)
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, role: 'agent', text: "I'm offline right now. Check your connection!" }])
    } finally {
      setIsTyping(false)
    }
  }

  if (isCheckingAuth) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-brand-cream text-brand-charcoal font-serif">
        <div className="flex flex-col items-center gap-4">
          <Activity className="w-8 h-8 text-brand-orange animate-pulse" />
          <span>Loading Titan...</span>
        </div>
      </div>
    )
  }

  if (!user) return null

  const isDarkMode = theme === 'dark' || (theme === 'system' && systemTheme === 'dark')

  return (
    <div className="flex h-screen bg-brand-cream font-serif text-brand-charcoal selection:bg-brand-orange selection:text-white overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-20 md:hidden backdrop-blur-sm"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar Component Render */}
      <aside className={`fixed md:static inset-y-0 left-0 bg-white dark:bg-[#1a1816] border-r border-brand-gray dark:border-zinc-800 w-72 flex flex-col transition-transform duration-300 ease-in-out z-30 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-4 border-b border-brand-gray dark:border-zinc-800 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-orange shadow-lg shadow-brand-orange/20">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-lg font-black tracking-tighter uppercase text-brand-charcoal dark:text-zinc-100">TITAN</h1>
          </div>
          <button onClick={() => setIsSidebarOpen(false)} className="md:hidden text-zinc-400 hover:text-brand-charcoal dark:hover:text-zinc-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          <button
            onClick={startNewChat}
            className="w-full flex items-center gap-2 bg-brand-charcoal text-white hover:bg-zinc-800 px-4 py-3 rounded-xl transition-all shadow-md active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span className="font-bold text-sm">New Chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setCurrentSessionId(s.id)
                if (window.innerWidth < 768) setIsSidebarOpen(false)
              }}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-left transition-colors ${currentSessionId === s.id
                ? 'bg-brand-gray text-brand-charcoal font-bold dark:bg-zinc-800 dark:text-zinc-100'
                : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-brand-charcoal dark:hover:text-zinc-200'
                }`}
            >
              <MessageSquare className={`w-4 h-4 shrink-0 ${currentSessionId === s.id ? 'text-brand-orange' : 'text-zinc-400'}`} />
              <span className="truncate text-sm">{s.title || "New Chat"}</span>
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-brand-gray dark:border-zinc-800 space-y-3">
          {mounted && (
            <button
              onClick={() => setTheme(isDarkMode ? 'light' : 'dark')}
              className="w-full flex items-center justify-between text-zinc-500 hover:text-brand-charcoal transition-all px-4 py-3 rounded-xl border border-transparent hover:bg-zinc-100 dark:hover:bg-zinc-800"
            >
              <span className="text-sm font-bold">{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
              {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          )}

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 text-zinc-500 hover:text-white text-sm font-bold transition-all hover:bg-red-500 px-4 py-3 rounded-xl border border-brand-gray hover:border-red-500 group dark:border-zinc-700"
          >
            <LogOut className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen relative">
        <header className="md:hidden flex items-center gap-3 px-4 py-3 bg-white/80 dark:bg-[#1a1816]/80 backdrop-blur-md border-b border-brand-gray dark:border-zinc-800 absolute top-0 left-0 right-0 z-10 w-full">
          <button onClick={() => setIsSidebarOpen(true)} className="text-zinc-500 hover:text-brand-charcoal dark:hover:text-zinc-200">
            <Menu className="w-6 h-6" />
          </button>
          <span className="font-bold tracking-tight uppercase text-brand-charcoal dark:text-zinc-100">Titan Coach</span>
        </header>

        <div className="flex-1 overflow-y-auto w-full max-w-5xl mx-auto p-4 md:p-6 flex flex-col gap-6 scroll-smooth bg-brand-cream pt-16 md:pt-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-zinc-400 dark:text-zinc-500 gap-4 mt-10">
              <div className="w-24 h-24 rounded-3xl bg-white dark:bg-zinc-800/30 border border-brand-gray dark:border-zinc-800 flex items-center justify-center shadow-sm">
                <Activity className="w-10 h-10 text-brand-orange/40 dark:text-brand-orange/60" />
              </div>
              <p className="text-lg font-medium text-zinc-600 dark:text-zinc-300">Your journey starts here.</p>
              <p className="text-sm">Say hi to Titan to begin your fitness journey.</p>
            </div>
          )}

          <div className="max-w-3xl mx-auto w-full flex flex-col gap-6 pb-4">
            {messages.map((m) => (
              <ChatMessageBubble key={m.id} message={m} />
            ))}

            {isTyping && (
              <div className="flex w-full justify-start">
                <div className="max-w-[85%] md:max-w-[75%] px-5 py-4 text-base shadow-sm bg-white dark:bg-[#1a1816] rounded-2xl rounded-tl-sm border border-brand-gray dark:border-zinc-800 flex items-center gap-1.5 w-fit">
                  <div className="w-2.5 h-2.5 bg-brand-orange/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-brand-orange/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-brand-orange/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInputArea
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
          isTyping={isTyping}
        />
      </div>
    </div>
  )
}

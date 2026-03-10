'use client'
import { useState } from 'react'
import { supabase } from '@/lib/supabase'

export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const handleSignUp = async () => {
        const { error } = await supabase.auth.signUp({ email, password })
        if (!error) {
            window.location.href = '/'
        } else {
            alert(error.message)
        }
    }

    const handleLogin = async () => {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (!error) window.location.href = '/'
        else alert(error.message)
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-brand-cream text-brand-charcoal dark:text-zinc-100 font-serif selection:bg-brand-orange selection:text-white">
            <div className="w-full max-w-md p-8 bg-white dark:bg-[#1a1816] border border-brand-gray dark:border-zinc-800 rounded-3xl shadow-xl shadow-zinc-200/50 dark:shadow-none z-10">
                <div className="text-center mb-10">
                    <h1 className="text-4xl font-black tracking-tighter mb-2 text-brand-charcoal dark:text-zinc-100">TITAN COACH</h1>
                    <p className="text-zinc-500 dark:text-zinc-400 text-sm font-medium">Your personalized AI fitness companion.</p>
                </div>

                <div className="flex flex-col gap-5">
                    <div>
                        <label className="block text-xs uppercase tracking-widest text-zinc-400 font-bold mb-2 ml-1">Email</label>
                        <input
                            type="email"
                            placeholder="you@example.com"
                            onChange={e => setEmail(e.target.value)}
                            className="w-full bg-brand-gray dark:bg-zinc-800/50 border border-transparent dark:border-zinc-800 text-brand-charcoal dark:text-zinc-100 rounded-2xl px-5 py-4 focus:outline-none focus:bg-white dark:focus:bg-zinc-800 focus:border-brand-orange/30 focus:ring-4 focus:ring-brand-orange/10 transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-600 font-medium"
                        />
                    </div>
                    <div>
                        <label className="block text-xs uppercase tracking-widest text-zinc-400 font-bold mb-2 ml-1">Password</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            onChange={e => setPassword(e.target.value)}
                            className="w-full bg-brand-gray dark:bg-zinc-800/50 border border-transparent dark:border-zinc-800 text-brand-charcoal dark:text-zinc-100 rounded-2xl px-5 py-4 focus:outline-none focus:bg-white dark:focus:bg-zinc-800 focus:border-brand-orange/30 focus:ring-4 focus:ring-brand-orange/10 transition-all placeholder:text-zinc-400 dark:placeholder:text-zinc-600 font-medium"
                        />
                    </div>

                    <div className="flex flex-col gap-4 mt-6">
                        <button
                            onClick={handleLogin}
                            className="w-full bg-brand-charcoal dark:bg-zinc-800 hover:bg-zinc-800 dark:hover:bg-zinc-700 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-zinc-200 dark:shadow-none active:scale-[0.98]"
                        >
                            Sign In
                        </button>
                        <button
                            onClick={handleSignUp}
                            className="w-full bg-brand-orange hover:brightness-110 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-brand-orange/20 dark:shadow-none active:scale-[0.98]"
                        >
                            Create Account
                        </button>
                    </div>
                </div>
            </div>

            <p className="mt-8 text-zinc-400 text-xs text-center max-w-xs font-medium">
                Train harder, lift heavier, and never give up.
            </p>
        </div>
    )
}

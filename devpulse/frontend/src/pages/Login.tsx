import React from 'react'
import { useNavigate } from 'react-router-dom'

import { login, register } from '@/api/auth'
import { setTokens } from '@/api/client'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [mode, setMode] = React.useState<'login' | 'register'>('login')
  const [error, setError] = React.useState<string | null>(null)
  const [loading, setLoading] = React.useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const tokens =
        mode === 'login' ? await login(email.trim(), password) : await register(email.trim(), password)
      setTokens(tokens)
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-full max-w-md flex-col justify-center p-6">
      <h1 className="mb-2 text-2xl font-semibold">DevPulse</h1>
      <p className="mb-6 text-sm text-gray-600">AI-powered incident retrospectives and runbooks.</p>

      <form onSubmit={onSubmit} className="rounded border border-gray-200 bg-white p-4">
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Email</label>
          <input
            className="w-full rounded border border-gray-200 px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            autoComplete="email"
            required
          />
        </div>
        <div className="mb-3">
          <label className="mb-1 block text-sm font-medium">Password</label>
          <input
            className="w-full rounded border border-gray-200 px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            required
          />
        </div>

        {error && <div className="mb-3 rounded bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div>}

        <button
          className="w-full rounded bg-gray-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
          type="submit"
          disabled={loading}
        >
          {loading ? 'Please wait…' : mode === 'login' ? 'Login' : 'Create account'}
        </button>

        <div className="mt-3 text-center text-sm">
          {mode === 'login' ? (
            <button className="text-gray-700 underline" type="button" onClick={() => setMode('register')}>
              Need an account?
            </button>
          ) : (
            <button className="text-gray-700 underline" type="button" onClick={() => setMode('login')}>
              Already have an account?
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

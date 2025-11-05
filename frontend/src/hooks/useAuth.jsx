import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

export const AuthContext = createContext({
  user: null,
  token: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
})

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

const getInitialToken = () => {
  if (typeof window === 'undefined') {
    return null
  }
  return localStorage.getItem('token')
}

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => getInitialToken())
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMe = async () => {
      if (!token) {
        setUser(null)
        setLoading(false)
        return
      }
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (!res.ok) {
          throw new Error('Unable to fetch profile')
        }
        const data = await res.json()
        setUser(data)
      } catch (error) {
        console.error(error)
        setToken(null)
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token')
        }
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    fetchMe()
  }, [token])

  const login = useCallback(async (email, password) => {
    const body = new URLSearchParams()
    body.append('username', email)
    body.append('password', password)
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    if (!res.ok) {
      throw new Error('Invalid credentials')
    }
    const data = await res.json()
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', data.access_token)
    }
    setToken(data.access_token)
    setLoading(true)
    return data
  }, [])

  const register = useCallback(async (email, password, fullName) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName }),
    })
    if (!res.ok) {
      const detail = await res.json()
      throw new Error(detail?.detail ?? 'Registration failed')
    }
    const data = await res.json()
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', data.access_token)
    }
    setToken(data.access_token)
    setLoading(true)
    return data
  }, [])

  const logout = useCallback(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
    }
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading, login, register, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)

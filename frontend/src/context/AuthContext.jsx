import { createContext, useContext, useEffect, useState } from 'react'
import { fetchMe, login as apiLogin, signup as apiSignup } from '../api/auth'
import { TOKEN_KEY, UNAUTHORIZED_EVENT } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    setLoading(true)
    fetchMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  // Any 401 from an authenticated request means the stored token is no longer
  // good; drop it so the UI stops pretending we're still logged in.
  useEffect(() => {
    function handleUnauthorized() {
      setToken(null)
      setUser(null)
    }
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
  }, [])

  async function login(email, password) {
    const { access_token } = await apiLogin(email, password)
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
  }

  async function signup(email, password) {
    await apiSignup(email, password)
    await login(email, password)
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

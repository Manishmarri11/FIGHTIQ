import axios from 'axios'

export const TOKEN_KEY = 'ufc_token'
export const UNAUTHORIZED_EVENT = 'ufc:unauthorized'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Tokens expire (JWT_EXPIRE_MINUTES). Without this, an expired token leaves the
// UI looking logged in while every request quietly fails. Broadcast a 401 so
// AuthContext can clear the stale session — but ignore 401s from the login
// endpoint itself, where it just means "wrong password".
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url ?? ''
    const isLoginAttempt = url.includes('/auth/login')

    if (status === 401 && !isLoginAttempt && localStorage.getItem(TOKEN_KEY)) {
      localStorage.removeItem(TOKEN_KEY)
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    return Promise.reject(error)
  },
)

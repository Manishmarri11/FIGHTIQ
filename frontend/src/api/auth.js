import { apiClient } from './client'

export async function signup(email, password) {
  const { data } = await apiClient.post('/auth/signup', { email, password })
  return data
}

export async function login(email, password) {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)
  const { data } = await apiClient.post('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function fetchMe() {
  const { data } = await apiClient.get('/auth/me')
  return data
}

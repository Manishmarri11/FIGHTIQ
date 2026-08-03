import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, token, loading } = useAuth()

  if (loading) return <p>Loading...</p>
  if (!token || !user) return <Navigate to="/login" replace />
  return children
}

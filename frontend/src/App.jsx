import { NavLink, Route, Routes } from 'react-router-dom'
import FighterList from './pages/FighterList'
import Comparison from './pages/Comparison'
import Login from './pages/Login'
import Signup from './pages/Signup'
import SavedComparisons from './pages/SavedComparisons'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuth } from './context/AuthContext'
import './App.css'

function App() {
  const { user, logout } = useAuth()

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <NavLink to="/" end className="brand">
            <span className="brand-mark">UFC</span>
            Predictor
          </NavLink>

          <nav className="app-nav">
            <NavLink to="/" end className="nav-link">
              Fighters
            </NavLink>
            <NavLink to="/compare" className="nav-link">
              Compare
            </NavLink>
            {user && (
              <NavLink to="/saved" className="nav-link">
                Saved
              </NavLink>
            )}
          </nav>

          <div className="app-header-auth">
            {user ? (
              <>
                <span className="user-email">{user.email}</span>
                <button className="btn-ghost" onClick={logout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="nav-link">
                  Log in
                </NavLink>
                <NavLink to="/signup" className="btn-primary btn-sm">
                  Sign up
                </NavLink>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<FighterList />} />
          <Route path="/compare" element={<Comparison />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/saved"
            element={
              <ProtectedRoute>
                <SavedComparisons />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  )
}

export default App

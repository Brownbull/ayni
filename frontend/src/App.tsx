import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import EmailVerification from './pages/EmailVerification'
import VerifyEmail from './pages/VerifyEmail'
import OAuthCallback from './pages/OAuthCallback'
import { useAuth } from './hooks/useAuth'
import './App.css'

function App() {
  const { loadUser, isAuthenticated } = useAuth()

  // Load user on app mount
  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/email-verification" element={<EmailVerification />} />
        <Route path="/auth/verify" element={<VerifyEmail />} />
        <Route path="/auth/callback" element={<OAuthCallback />} />

        {/* Dashboard route (protected) */}
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    Welcome to Ayni Dashboard
                  </h1>
                  <p className="text-gray-600">You are successfully logged in!</p>
                  <button
                    onClick={() => {
                      useAuth.getState().logout()
                      window.location.href = '/login'
                    }}
                    className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Default route */}
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />
      </Routes>
    </Router>
  )
}

export default App

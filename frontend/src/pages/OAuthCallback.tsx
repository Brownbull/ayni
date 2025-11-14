/**
 * OAuth Callback page - handles redirect from Google
 */

import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { error } = useAuth()
  const hasProcessed = useRef(false)

  useEffect(() => {
    // Prevent duplicate calls (React StrictMode runs effects twice in dev)
    if (hasProcessed.current) {
      return
    }

    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')
    const errorParam = searchParams.get('error')

    if (errorParam) {
      // User cancelled or error occurred
      navigate('/login', {
        state: { error: 'Inicio de sesión cancelado' }
      })
      return
    }

    if (!accessToken) {
      navigate('/login', {
        state: { error: 'Error al conectar con Google. Por favor, intenta nuevamente.' }
      })
      return
    }

    // Mark as processed
    hasProcessed.current = true

    // Store tokens in localStorage
    localStorage.setItem('access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }

    // Load user profile and redirect to dashboard
    useAuth.getState().loadUser()
      .then(() => {
        navigate('/dashboard')
      })
      .catch(() => {
        navigate('/login')
      })
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        {error ? (
          <div>
            <div className="text-red-600 text-lg mb-4">{error}</div>
            <button
              onClick={() => navigate('/login')}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Volver al inicio de sesión
            </button>
          </div>
        ) : (
          <div>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Iniciando sesión con Google...</p>
          </div>
        )}
      </div>
    </div>
  )
}

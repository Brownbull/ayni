/**
 * Authentication state management hook
 */

import { create } from 'zustand'
import { User, login as apiLogin, logout as apiLogout, getCurrentUser, register as apiRegister, RegisterRequest } from '../api/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
  clearError: () => void
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const tokenResponse = await apiLogin(email, password)

      // Store tokens in localStorage (Story 2.3 AC#1)
      localStorage.setItem('access_token', tokenResponse.access_token)
      if (tokenResponse.refresh_token) {
        localStorage.setItem('refresh_token', tokenResponse.refresh_token)
      }

      // Fetch user profile
      const user = await getCurrentUser()

      set({
        user,
        isAuthenticated: true,
        isLoading: false
      })
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Login failed'
      set({
        error: errorMessage,
        isLoading: false,
        user: null,
        isAuthenticated: false
      })
      throw error
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null })
    try {
      await apiRegister(data)
      set({ isLoading: false })
      // Note: Don't auto-login after registration
      // User needs to verify email first
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Registration failed'
      set({
        error: errorMessage,
        isLoading: false
      })
      throw error
    }
  },

  logout: () => {
    apiLogout()
    // Clear both access and refresh tokens (Story 2.3 AC#2)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({
      user: null,
      isAuthenticated: false,
      error: null
    })
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false })
      return
    }

    set({ isLoading: true })
    try {
      const user = await getCurrentUser()
      set({
        user,
        isAuthenticated: true,
        isLoading: false
      })
    } catch {
      // Token is invalid or expired
      localStorage.removeItem('access_token')
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false
      })
    }
  },

  clearError: () => set({ error: null }),
}))

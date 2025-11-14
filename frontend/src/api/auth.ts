/**
 * Authentication API calls
 */

import apiClient from './client'

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}

export interface LoginRequest {
  username: string // OAuth2 uses 'username' field for email
  password: string
}

export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  tenant_id: number
  role: string
  is_verified: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

/**
 * Register a new user
 */
export const register = async (data: RegisterRequest): Promise<User> => {
  const response = await apiClient.post<User>('/auth/register', data)
  return response.data
}

/**
 * Login with email and password
 */
export const login = async (email: string, password: string): Promise<TokenResponse> => {
  // OAuth2 password flow uses form data
  const formData = new URLSearchParams()
  formData.append('username', email) // OAuth2 uses 'username' field
  formData.append('password', password)

  const response = await apiClient.post<TokenResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })

  return response.data
}

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>('/users/me')
  return response.data
}

/**
 * Logout (client-side only, clears token)
 */
export const logout = (): void => {
  localStorage.removeItem('access_token')
}

/**
 * Verify email with token from verification link
 */
export const verifyEmail = async (token: string): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/auth/verify-email', null, {
    params: { token },
  })
  return response.data
}

/**
 * Resend verification email
 */
export const resendVerification = async (email: string): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>('/auth/resend-verification', {
    email,
  })
  return response.data
}

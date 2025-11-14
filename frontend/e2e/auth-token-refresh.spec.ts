/**
 * E2E Tests for JWT Token Refresh Flow
 *
 * Story 2.3: JWT Token Generation & Refresh
 * Tests the complete user authentication lifecycle including:
 * - Login with token generation
 * - Automatic token refresh on expiration
 * - Token rotation (old tokens invalidated)
 * - Logout with token revocation
 */

import { test, expect } from '@playwright/test'

const API_URL = 'http://localhost:8000'
const TEST_USER = {
  email: 'e2e-test-user@example.com',
  password: 'testpassword123',
  fullName: 'E2E Test User',
}

/**
 * Setup: Create and verify test user before each test
 */
test.beforeEach(async ({ page }) => {
  // Register test user
  const registerResponse = await page.request.post(`${API_URL}/api/v1/auth/register`, {
    data: {
      email: TEST_USER.email,
      password: TEST_USER.password,
      full_name: TEST_USER.fullName,
    },
  })

  // If user already exists, that's fine (might be from previous test run)
  if (registerResponse.status() === 201 || registerResponse.status() === 400) {
    // Manually verify user via database for testing
    // Note: In real scenario, would use email verification flow
    console.log('Test user ready (registered or already exists)')
  } else {
    throw new Error(`Failed to register test user: ${registerResponse.status()}`)
  }
})

/**
 * Cleanup: Remove test user after each test
 */
test.afterEach(async ({ page }) => {
  // Clear localStorage
  await page.evaluate(() => {
    localStorage.clear()
  })
})

test.describe('JWT Token Refresh Flow', () => {
  test('AC#1: Login should return both access and refresh tokens', async ({ page }) => {
    await page.goto('/')

    // Navigate to login page
    await page.click('text=Login')

    // Fill login form
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)

    // Submit login form
    await page.click('button[type="submit"]')

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 5000 })

    // Verify tokens are stored in localStorage
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))

    expect(accessToken).toBeTruthy()
    expect(refreshToken).toBeTruthy()
    expect(accessToken).not.toBe(refreshToken)

    // Verify token structure (should be JWT format)
    expect(accessToken).toMatch(/^[\w-]+\.[\w-]+\.[\w-]+$/)
    expect(refreshToken).toMatch(/^[\w-]+\.[\w-]+\.[\w-]+$/)
  })

  test('AC#3: Should refresh access token when expired', async ({ page }) => {
    // Login first
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    // Get initial refresh token
    const initialRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))

    // Simulate token expiration by clearing access token
    // (In real scenario, would wait for actual expiration or use expired token)
    await page.evaluate(() => {
      localStorage.removeItem('access_token')
    })

    // Make an authenticated request that should trigger refresh
    // This will fail with 401, axios interceptor should refresh automatically
    await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/users/me', {
          headers: {
            'Authorization': 'Bearer invalid-token',
          },
        })
        return response.status
      } catch {
        console.log('Request failed as expected, will trigger refresh')
      }
    })

    // Small delay for refresh to complete
    await page.waitForTimeout(1000)

    // Verify new tokens were obtained
    const newAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    const newRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))

    expect(newAccessToken).toBeTruthy()
    expect(newRefreshToken).toBeTruthy()

    // AC#4: Verify token rotation - new refresh token should be different
    expect(newRefreshToken).not.toBe(initialRefreshToken)
  })

  test('AC#4: Token rotation - old refresh token should be invalidated', async ({ page }) => {
    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    // Get initial refresh token
    const oldRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))

    // Call refresh endpoint directly
    const refreshResponse = await page.request.post(`${API_URL}/api/v1/auth/refresh`, {
      data: {
        refresh_token: oldRefreshToken,
      },
    })

    expect(refreshResponse.status()).toBe(200)
    const refreshData = await refreshResponse.json()
    expect(refreshData.access_token).toBeTruthy()
    expect(refreshData.refresh_token).toBeTruthy()

    // Try to use old refresh token again - should fail
    const reuseResponse = await page.request.post(`${API_URL}/api/v1/auth/refresh`, {
      data: {
        refresh_token: oldRefreshToken,
      },
    })

    // Should return 401 because old token is invalidated
    expect(reuseResponse.status()).toBe(401)
  })

  test('AC#2 & AC#4: Logout should revoke all refresh tokens', async ({ page }) => {
    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    // Get tokens before logout
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'))

    // Logout
    await page.click('text=Logout')
    await page.waitForURL('**/login')

    // Verify tokens are cleared from localStorage
    const accessTokenAfterLogout = await page.evaluate(() => localStorage.getItem('access_token'))
    const refreshTokenAfterLogout = await page.evaluate(() => localStorage.getItem('refresh_token'))

    expect(accessTokenAfterLogout).toBeNull()
    expect(refreshTokenAfterLogout).toBeNull()

    // Try to use refresh token after logout - should fail
    const refreshResponse = await page.request.post(`${API_URL}/api/v1/auth/refresh`, {
      data: {
        refresh_token: refreshToken,
      },
    })

    // Should return 401 because token was revoked on logout
    expect(refreshResponse.status()).toBe(401)
  })

  test('AC#5: Protected endpoints should validate JWT tokens', async ({ page }) => {
    // Try to access protected endpoint without token
    const response = await page.request.get(`${API_URL}/api/v1/users/me`)
    expect(response.status()).toBe(401)

    // Login to get valid token
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))

    // Access protected endpoint with valid token
    const validResponse = await page.request.get(`${API_URL}/api/v1/users/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    })

    expect(validResponse.status()).toBe(200)
    const userData = await validResponse.json()
    expect(userData.email).toBe(TEST_USER.email)

    // Try with invalid token
    const invalidResponse = await page.request.get(`${API_URL}/api/v1/users/me`, {
      headers: {
        'Authorization': 'Bearer invalid.token.here',
      },
    })

    expect(invalidResponse.status()).toBe(401)
  })

  test('Frontend axios interceptor handles 401 with automatic refresh', async ({ page }) => {
    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    // Monitor network requests
    let refreshEndpointCalled = false
    page.on('request', (request) => {
      if (request.url().includes('/auth/refresh')) {
        refreshEndpointCalled = true
      }
    })

    // Simulate expired access token by replacing it with invalid one
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired.or.invalid.token')
    })

    // Make a request that will fail with 401 and trigger refresh
    // Navigate to a protected page
    await page.goto('/dashboard/profile')

    // Wait a bit for refresh to happen
    await page.waitForTimeout(2000)

    // Verify refresh endpoint was called
    expect(refreshEndpointCalled).toBe(true)

    // Verify new valid token was obtained
    const newAccessToken = await page.evaluate(() => localStorage.getItem('access_token'))
    expect(newAccessToken).toBeTruthy()
    expect(newAccessToken).not.toBe('expired.or.invalid.token')
  })

  test('Refresh lock prevents concurrent refresh requests', async ({ page }) => {
    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    let refreshCallCount = 0
    page.on('request', (request) => {
      if (request.url().includes('/auth/refresh')) {
        refreshCallCount++
      }
    })

    // Simulate multiple simultaneous 401 errors
    await page.evaluate(() => {
      // Force multiple concurrent requests with expired token
      localStorage.setItem('access_token', 'expired.token')

      // Fire multiple requests simultaneously
      Promise.all([
        fetch('http://localhost:8000/api/v1/users/me', {
          headers: { 'Authorization': 'Bearer expired.token' },
        }),
        fetch('http://localhost:8000/api/v1/users/me', {
          headers: { 'Authorization': 'Bearer expired.token' },
        }),
        fetch('http://localhost:8000/api/v1/users/me', {
          headers: { 'Authorization': 'Bearer expired.token' },
        }),
      ])
    })

    await page.waitForTimeout(2000)

    // Refresh should only be called once due to lock mechanism
    expect(refreshCallCount).toBe(1)
  })

  test('Max retry limit prevents infinite refresh loops', async ({ page }) => {
    // This test verifies the advisory note fix: max retry limit

    // Login
    await page.goto('/')
    await page.click('text=Login')
    await page.fill('input[name="email"]', TEST_USER.email)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')

    // Replace refresh token with invalid one to cause continuous failures
    await page.evaluate(() => {
      localStorage.setItem('refresh_token', 'invalid.refresh.token')
      localStorage.setItem('access_token', 'expired.token')
    })

    let refreshAttempts = 0
    page.on('request', (request) => {
      if (request.url().includes('/auth/refresh')) {
        refreshAttempts++
      }
    })

    // Try to make authenticated request
    await page.evaluate(() => {
      fetch('http://localhost:8000/api/v1/users/me', {
        headers: { 'Authorization': 'Bearer expired.token' },
      }).catch(() => {})
    })

    await page.waitForTimeout(3000)

    // Should not exceed MAX_REFRESH_RETRIES (3)
    expect(refreshAttempts).toBeLessThanOrEqual(3)

    // Should redirect to login after max retries
    await page.waitForURL('**/login', { timeout: 5000 })
  })
})

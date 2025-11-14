/**
 * Email verification confirmation page
 *
 * Shown after successful registration to inform user to check their email
 */

import { useLocation, Link } from 'react-router-dom'
import { useState } from 'react'

export default function EmailVerification() {
  const location = useLocation()
  const email = location.state?.email || ''
  const [resendCooldown, setResendCooldown] = useState(false)

  const handleResendEmail = () => {
    // TODO: Implement resend email verification
    // For now, just show cooldown
    setResendCooldown(true)
    setTimeout(() => setResendCooldown(false), 60000) // 1 minute cooldown

    alert('Email verification link sent! (Not implemented yet)')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
            <svg
              className="h-8 w-8 text-green-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Check your email
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            We've sent a verification link to
          </p>
          {email && (
            <p className="mt-1 text-sm font-medium text-indigo-600">{email}</p>
          )}
        </div>

        <div className="mt-8 bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              What's next?
            </h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <ul className="list-disc list-inside space-y-1">
                <li>Check your inbox (and spam folder)</li>
                <li>Click the verification link in the email</li>
                <li>Return here to sign in</li>
              </ul>
            </div>
            <div className="mt-5">
              <p className="text-sm text-gray-500">
                Didn't receive the email?
              </p>
              <button
                type="button"
                onClick={handleResendEmail}
                disabled={resendCooldown}
                className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {resendCooldown
                  ? 'Email sent! Wait 1 minute to resend'
                  : 'Resend verification email'}
              </button>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Link
            to="/login"
            className="font-medium text-indigo-600 hover:text-indigo-500"
          >
            Back to login
          </Link>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Note: Email verification is not yet fully implemented. You can proceed to
            login without verifying your email for testing purposes.
          </p>
        </div>
      </div>
    </div>
  )
}

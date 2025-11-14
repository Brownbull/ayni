# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story's `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2025-11-14 | 2.1 | 2 | Bug | High | TBD | Open | Implement refresh token logic and POST /api/auth/refresh endpoint (AC #4) - backend/app/api/routes/auth.py |
| 2025-11-14 | 2.1 | 2 | Bug | High | TBD | Open | Add server-side password validation (min 8 chars) in UserRegister Pydantic model - backend/app/models.py |
| 2025-11-14 | 2.1 | 2 | Bug | Med | TBD | Open | Re-enable email verification check in login endpoint after email service setup (AC #4) - backend/app/api/routes/auth.py:138-144 |
| 2025-11-14 | 2.1 | 2 | Test | Med | TBD | Open | Add integration test: login with unverified email should return 401 - backend/tests/api/test_auth.py |
| 2025-11-14 | 2.1 | 2 | Test | Med | TBD | Open | Add integration test: registration with invalid email format returns 400 - backend/tests/api/test_auth.py |
| 2025-11-14 | 2.1 | 2 | Test | Med | TBD | Open | Add integration test: registration with password <8 chars returns 422 - backend/tests/api/test_auth.py |
| 2025-11-14 | 2.1 | 2 | Test | Med | TBD | Open | Add unit test: JWT token payload structure validation (verify tenant_id, role, email claims) - backend/tests/core/test_security.py |
| 2025-11-14 | 2.1 | 2 | Enhancement | Med | TBD | Open | Implement rate limiting on login endpoint using slowapi (5 attempts per 15 min) - backend/app/api/routes/auth.py:93 |
| 2025-11-14 | 2.1 | 2 | Enhancement | Low | TBD | Open | Add structured logging for authentication events (failed logins, registrations) using Sentry breadcrumbs |
| 2025-11-14 | 2.2 | 2 | Refactor | Low | TBD | Open | Extract email verification constants to settings (RESEND_RATE_LIMIT_SECONDS, VERIFICATION_TOKEN_EXPIRE_HOURS) - backend/app/core/config.py |
| 2025-11-14 | 2.2 | 2 | Enhancement | Low | TBD | Open | Add i18n support for email verification pages (when project adds internationalization) - frontend/src/pages/VerifyEmail.tsx, EmailVerification.tsx |
| 2025-11-14 | 2.2 | 2 | Enhancement | Low | TBD | Open | Consider removing verification token prefix from production logs or add environment flag - backend/app/api/routes/auth.py:491 |
| 2025-11-14 | 2.2 | 2 | Test | Med | TBD | Open | Add Playwright E2E test for full verification flow: register → email → click link → verify → login - frontend/tests/e2e/ |

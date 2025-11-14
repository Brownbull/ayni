"""
Google OAuth 2.0 client configuration for fastapi-users integration.
Story 2.5: Google OAuth 2.0 Integration
"""

from httpx_oauth.clients.google import GoogleOAuth2

from app.core.config import settings


def get_google_oauth_client() -> GoogleOAuth2 | None:
    """
    Get Google OAuth2 client if credentials are configured.

    Returns:
        GoogleOAuth2 client if credentials are set, None otherwise
    """
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return None

    return GoogleOAuth2(
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    )


# Global OAuth client instance
google_oauth_client = get_google_oauth_client()

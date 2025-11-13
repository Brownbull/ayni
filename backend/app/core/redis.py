"""Redis client singleton with connection pooling."""
from redis.asyncio import Redis

from app.core.config import settings


class RedisClient:
    """Singleton Redis client with connection pooling."""

    _instance: Redis | None = None

    @classmethod
    async def get_client(cls) -> Redis:
        """Get or create Redis client instance.

        Returns:
            Redis: Shared Redis client instance with connection pooling.
        """
        if cls._instance is None:
            cls._instance = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection pool."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

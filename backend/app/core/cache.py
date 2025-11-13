"""Caching utilities for database query results with Redis backend.

Provides decorator-based caching with:
- TTL-based expiration
- Tenant-aware cache keys for data isolation
- Cache invalidation helpers
- Hit/miss logging for monitoring
"""
import functools
import hashlib
import json
import logging
from collections.abc import Callable
from typing import Any

from app.core.redis import RedisClient

logger = logging.getLogger(__name__)


def _generate_cache_key(
    function_name: str,
    key_prefix: str,
    tenant_id: int | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Generate cache key from function name, tenant_id, and arguments.

    Cache key format: {key_prefix}:{function_name}:{tenant_id}:{args_hash}

    Args:
        function_name: Name of the cached function
        key_prefix: Optional prefix for grouping related caches
        tenant_id: Tenant ID for multi-tenant isolation (None for non-tenant data)
        args: Positional arguments to hash
        kwargs: Keyword arguments to hash

    Returns:
        str: Cache key with tenant isolation
    """
    # Create stable hash of arguments
    args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:16]

    # Build key with tenant isolation
    parts = [key_prefix, function_name] if key_prefix else [function_name]
    if tenant_id is not None:
        parts.append(f"tenant_{tenant_id}")
    parts.append(args_hash)

    return ":".join(parts)


def cache_result(
    ttl: int = 3600,
    key_prefix: str = "",
    tenant_key: str | None = None,
) -> Callable:
    """Decorator to cache function results with TTL and tenant isolation.

    Args:
        ttl: Time-to-live in seconds (default: 3600 = 1 hour)
        key_prefix: Optional prefix for grouping related caches (e.g., "analytics")
        tenant_key: Kwarg name containing tenant_id (default: None for non-tenant data)

    Returns:
        Decorated function with caching

    Example:
        @cache_result(ttl=3600, key_prefix="analytics", tenant_key="tenant_id")
        async def get_dashboard_data(tenant_id: int, location_id: int, period: str):
            # Expensive database query
            return data
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract tenant_id if specified
            tenant_id = kwargs.get(tenant_key) if tenant_key else None

            # Generate cache key
            cache_key = _generate_cache_key(
                function_name=func.__name__,
                key_prefix=key_prefix,
                tenant_id=tenant_id,
                args=args,
                kwargs=kwargs,
            )

            try:
                # Try to get from cache
                redis = await RedisClient.get_client()
                cached_value = await redis.get(cache_key)

                if cached_value is not None:
                    logger.info(f"Cache hit: {cache_key}")
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.info(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)

                # Store in cache with TTL
                await redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str),
                )

                return result

            except Exception as e:
                # On Redis failure, execute function without caching
                logger.warning(
                    f"Cache error for {cache_key}: {e}. Executing without cache."
                )
                return await func(*args, **kwargs)

        return wrapper

    return decorator


async def invalidate_cache(cache_key: str) -> None:
    """Invalidate a specific cache entry.

    Args:
        cache_key: The cache key to invalidate
    """
    try:
        redis = await RedisClient.get_client()
        await redis.delete(cache_key)
        logger.info(f"Cache invalidated: {cache_key}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache {cache_key}: {e}")


async def invalidate_pattern(pattern: str) -> None:
    """Invalidate all cache entries matching a pattern.

    Useful for invalidating all caches for a tenant or key prefix.

    Args:
        pattern: Redis key pattern (e.g., "analytics:*:tenant_123:*")

    Example:
        # Invalidate all analytics caches for tenant 123
        await invalidate_pattern("analytics:*:tenant_123:*")
    """
    try:
        redis = await RedisClient.get_client()

        # Find all matching keys
        keys = []
        async for key in redis.scan_iter(match=pattern):
            keys.append(key)

        # Delete in batches
        if keys:
            await redis.delete(*keys)
            logger.info(
                f"Cache invalidated: {len(keys)} keys matching pattern '{pattern}'"
            )

    except Exception as e:
        logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")

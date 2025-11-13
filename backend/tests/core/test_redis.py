"""Tests for Redis client connection and operations."""
import pytest

from app.core.redis import RedisClient


@pytest.mark.asyncio
async def test_redis_client_singleton():
    """Test that RedisClient returns the same instance."""
    client1 = await RedisClient.get_client()
    client2 = await RedisClient.get_client()

    assert client1 is client2, "RedisClient should return the same instance"


@pytest.mark.asyncio
async def test_redis_connection():
    """Test basic Redis connection with ping."""
    redis = await RedisClient.get_client()
    response = await redis.ping()

    assert response is True, "Redis ping should return True"


@pytest.mark.asyncio
async def test_redis_set_and_get():
    """Test Redis set and get operations."""
    redis = await RedisClient.get_client()

    # Set a test key
    test_key = "test:redis:key"
    test_value = "test_value"
    await redis.set(test_key, test_value)

    # Get the value
    result = await redis.get(test_key)

    assert result == test_value, "Retrieved value should match set value"

    # Clean up
    await redis.delete(test_key)


@pytest.mark.asyncio
async def test_redis_expiration():
    """Test Redis key expiration with TTL."""
    redis = await RedisClient.get_client()

    # Set a key with 1 second TTL
    test_key = "test:redis:expiration"
    test_value = "expires_soon"
    await redis.setex(test_key, 1, test_value)

    # Verify it exists
    result = await redis.get(test_key)
    assert result == test_value, "Value should exist immediately after setting"

    # Check TTL
    ttl = await redis.ttl(test_key)
    assert ttl > 0, "TTL should be positive"

    # Wait for expiration (in real tests, we'd use a longer TTL and check immediately)
    # Clean up
    await redis.delete(test_key)


@pytest.mark.asyncio
async def test_redis_delete():
    """Test Redis delete operation."""
    redis = await RedisClient.get_client()

    # Set a test key
    test_key = "test:redis:delete"
    test_value = "to_be_deleted"
    await redis.set(test_key, test_value)

    # Delete the key
    deleted_count = await redis.delete(test_key)
    assert deleted_count == 1, "Should delete one key"

    # Verify it's gone
    result = await redis.get(test_key)
    assert result is None, "Key should not exist after deletion"

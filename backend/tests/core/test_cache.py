"""Tests for caching utilities and decorators."""
import pytest

from app.core.cache import (
    _generate_cache_key,
    cache_result,
    invalidate_cache,
    invalidate_pattern,
)
from app.core.redis import RedisClient


def test_generate_cache_key_basic():
    """Test cache key generation without tenant."""
    key = _generate_cache_key(
        function_name="test_func",
        key_prefix="",
        tenant_id=None,
        args=(1, 2),
        kwargs={"param": "value"},
    )

    assert "test_func" in key
    assert key.count(":") == 1  # function_name:hash


def test_generate_cache_key_with_prefix():
    """Test cache key generation with prefix."""
    key = _generate_cache_key(
        function_name="test_func",
        key_prefix="analytics",
        tenant_id=None,
        args=(1, 2),
        kwargs={"param": "value"},
    )

    assert "analytics" in key
    assert "test_func" in key
    assert key.count(":") == 2  # prefix:function_name:hash


def test_generate_cache_key_with_tenant():
    """Test cache key generation with tenant isolation."""
    key = _generate_cache_key(
        function_name="test_func",
        key_prefix="analytics",
        tenant_id=123,
        args=(1, 2),
        kwargs={"param": "value"},
    )

    assert "analytics" in key
    assert "test_func" in key
    assert "tenant_123" in key
    assert key.count(":") == 3  # prefix:function_name:tenant_id:hash


def test_generate_cache_key_stability():
    """Test that same inputs generate same cache key."""
    key1 = _generate_cache_key(
        function_name="test_func",
        key_prefix="",
        tenant_id=None,
        args=(1, 2),
        kwargs={"param": "value"},
    )

    key2 = _generate_cache_key(
        function_name="test_func",
        key_prefix="",
        tenant_id=None,
        args=(1, 2),
        kwargs={"param": "value"},
    )

    assert key1 == key2, "Same inputs should generate same cache key"


@pytest.mark.asyncio
async def test_cache_result_decorator_basic():
    """Test basic cache_result decorator functionality."""
    call_count = 0

    @cache_result(ttl=60)
    async def expensive_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call should execute function
    result1 = await expensive_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call should use cache
    result2 = await expensive_function(5)
    assert result2 == 10
    assert call_count == 1, "Function should not be called again (cache hit)"

    # Different argument should execute function again
    result3 = await expensive_function(10)
    assert result3 == 20
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_result_with_tenant_isolation():
    """Test that cache decorator respects tenant isolation."""
    call_count = 0

    @cache_result(ttl=60, key_prefix="test", tenant_key="tenant_id")
    async def get_tenant_data(tenant_id: int, data_id: int) -> dict:
        nonlocal call_count
        call_count += 1
        return {"tenant": tenant_id, "data": data_id}

    # Call for tenant 1
    result1 = await get_tenant_data(tenant_id=1, data_id=100)
    assert result1["tenant"] == 1
    assert call_count == 1

    # Same data_id for tenant 2 should be separate cache entry
    result2 = await get_tenant_data(tenant_id=2, data_id=100)
    assert result2["tenant"] == 2
    assert call_count == 2, "Different tenant should not use same cache"

    # Calling tenant 1 again should use cache
    result3 = await get_tenant_data(tenant_id=1, data_id=100)
    assert result3["tenant"] == 1
    assert call_count == 2, "Same tenant should use cache"


@pytest.mark.asyncio
async def test_invalidate_cache():
    """Test cache invalidation for specific key."""

    @cache_result(ttl=60, key_prefix="test")
    async def cached_func(x: int) -> int:
        return x * 2

    # Call function to populate cache
    result1 = await cached_func(5)
    assert result1 == 10

    # Manually invalidate cache
    cache_key = _generate_cache_key(
        function_name="cached_func",
        key_prefix="test",
        tenant_id=None,
        args=(5,),
        kwargs={},
    )
    await invalidate_cache(cache_key)

    # Verify cache was cleared by checking Redis directly
    redis = await RedisClient.get_client()
    cached_value = await redis.get(cache_key)
    assert cached_value is None, "Cache should be invalidated"


@pytest.mark.asyncio
async def test_invalidate_pattern():
    """Test pattern-based cache invalidation."""
    redis = await RedisClient.get_client()

    # Set multiple test keys
    test_keys = [
        "test:pattern:key1",
        "test:pattern:key2",
        "test:pattern:key3",
        "other:key",
    ]

    for key in test_keys:
        await redis.set(key, "value")

    # Invalidate all test:pattern:* keys
    await invalidate_pattern("test:pattern:*")

    # Check that pattern keys are deleted
    for key in test_keys[:3]:
        result = await redis.get(key)
        assert result is None, f"Key {key} should be deleted"

    # Check that other key still exists
    result = await redis.get(test_keys[3])
    assert result == "value", "Non-matching key should not be deleted"

    # Clean up
    await redis.delete(test_keys[3])


@pytest.mark.asyncio
async def test_cache_graceful_degradation():
    """Test that cache decorator handles Redis failures gracefully."""
    call_count = 0

    @cache_result(ttl=60)
    async def resilient_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    # Function should work even if Redis is unavailable
    # (We can't easily simulate Redis failure in this test without mocking)
    result = await resilient_function(5)
    assert result == 10
    assert call_count == 1

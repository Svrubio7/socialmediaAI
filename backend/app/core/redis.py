"""
Redis client configuration and utilities.
"""

from typing import Optional
import redis
from redis import Redis

from app.core.config import settings

# Global Redis client
_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    """
    Get or create Redis client.
    
    Returns:
        Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    
    return _redis_client


def close_redis_client() -> None:
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None


class RedisCache:
    """Simple Redis cache wrapper."""

    def __init__(self, prefix: str = "cache"):
        """
        Initialize cache with key prefix.
        
        Args:
            prefix: Prefix for all cache keys
        """
        self.prefix = prefix
        self.client = get_redis_client()

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return self.client.get(self._make_key(key))

    def set(self, key: str, value: str, ttl_seconds: int = 3600) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful
        """
        return self.client.setex(self._make_key(key), ttl_seconds, value)

    def delete(self, key: str) -> int:
        """Delete key from cache."""
        return self.client.delete(self._make_key(key))

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.client.exists(self._make_key(key)) > 0

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in cache."""
        return self.client.incr(self._make_key(key), amount)

    def expire(self, key: str, ttl_seconds: int) -> bool:
        """Set expiration on existing key."""
        return self.client.expire(self._make_key(key), ttl_seconds)


# Session cache for storing user sessions
session_cache = RedisCache(prefix="session")

# Rate limiting cache
rate_limit_cache = RedisCache(prefix="ratelimit")

# Task status cache
task_cache = RedisCache(prefix="task")

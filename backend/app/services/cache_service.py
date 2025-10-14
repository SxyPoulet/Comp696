"""
Redis caching service for API responses and scraped data.
Implements TTL-based caching with automatic expiration.
"""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import timedelta
import redis
from app.core.config import settings


class CacheService:
    """Redis-based caching service with TTL management."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self.default_ttl = settings.cache_ttl  # 7 days default

    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate a cache key with namespace.

        Args:
            namespace: Category of cached data (e.g., 'company', 'contact')
            identifier: Unique identifier (e.g., domain, email)

        Returns:
            Formatted cache key
        """
        return f"cache:{namespace}:{identifier}"

    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """
        Create a hash from a dictionary for cache key generation.

        Args:
            data: Dictionary to hash

        Returns:
            MD5 hash of the dictionary
        """
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """
        Retrieve cached data.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier

        Returns:
            Cached data or None if not found/expired
        """
        try:
            key = self._generate_key(namespace, identifier)
            data = self.redis_client.get(key)

            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {str(e)}")
            return None

    def set(
        self,
        namespace: str,
        identifier: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store data in cache with TTL.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            data: Data to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 7 days)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(namespace, identifier)
            json_data = json.dumps(data)
            ttl_seconds = ttl or self.default_ttl

            self.redis_client.setex(key, ttl_seconds, json_data)
            return True
        except Exception as e:
            print(f"Cache set error: {str(e)}")
            return False

    def delete(self, namespace: str, identifier: str) -> bool:
        """
        Delete cached data.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(namespace, identifier)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {str(e)}")
            return False

    def exists(self, namespace: str, identifier: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier

        Returns:
            True if exists, False otherwise
        """
        try:
            key = self._generate_key(namespace, identifier)
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {str(e)}")
            return False

    def get_ttl(self, namespace: str, identifier: str) -> Optional[int]:
        """
        Get remaining TTL for a cached item.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier

        Returns:
            Remaining TTL in seconds, or None if not found
        """
        try:
            key = self._generate_key(namespace, identifier)
            ttl = self.redis_client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            print(f"Cache TTL error: {str(e)}")
            return None

    def invalidate_namespace(self, namespace: str) -> int:
        """
        Invalidate all keys in a namespace.

        Args:
            namespace: Category to invalidate

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"cache:{namespace}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidate error: {str(e)}")
            return 0

    def get_or_set(
        self,
        namespace: str,
        identifier: str,
        fetch_func: callable,
        ttl: Optional[int] = None
    ) -> Optional[Any]:
        """
        Get from cache or fetch and store if not found.

        Args:
            namespace: Category of cached data
            identifier: Unique identifier
            fetch_func: Function to call if cache miss (must return JSON serializable data)
            ttl: Time to live in seconds

        Returns:
            Cached or fetched data
        """
        # Try to get from cache
        cached = self.get(namespace, identifier)
        if cached is not None:
            return cached

        # Cache miss - fetch data
        try:
            data = fetch_func()
            if data is not None:
                self.set(namespace, identifier, data, ttl)
            return data
        except Exception as e:
            print(f"Cache get_or_set error: {str(e)}")
            return None

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.

        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Cache health check failed: {str(e)}")
            return False


# Singleton instance
cache_service = CacheService()

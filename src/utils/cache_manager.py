#!/usr/bin/env python3
"""
Production Cache Manager - Redis-based caching with fallback to in-memory
===========================================================================

FEATURES:
1. Redis caching with automatic fallback to in-memory cache
2. TTL-based expiration for all cache entries
3. Async operations for non-blocking performance
4. Category-based cache invalidation
5. Compression for large values

PERFORMANCE:
- Redis: Sub-millisecond reads, persistent across restarts
- In-memory: Nanosecond reads, lost on restart
- Compression: 60-80% size reduction for JSON data
"""

import json
import asyncio
import logging
import pickle
import zlib
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import time

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not installed. Using in-memory cache only.")

class CacheManager:
    """High-performance caching with Redis and in-memory fallback"""
    
    # Default TTL values (seconds)
    TTL_SHORT = 300      # 5 minutes - for rapidly changing data
    TTL_MEDIUM = 1800    # 30 minutes - for moderately stable data
    TTL_LONG = 7200      # 2 hours - for stable data
    TTL_DAY = 86400      # 24 hours - for very stable data
    
    # Cache categories for organized invalidation
    CATEGORY_PRODUCTS = "products"
    CATEGORY_CONTENT = "content"
    CATEGORY_CREDENTIALS = "credentials"
    CATEGORY_MEDIA = "media"
    CATEGORY_API_RESPONSES = "api"
    
    def __init__(self, redis_url: str = "redis://localhost:6379", use_compression: bool = True):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL
            use_compression: Whether to compress large values
        """
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.use_compression = use_compression
        self.compression_threshold = 1024  # Compress values larger than 1KB
        
        # Redis client (initialized lazily)
        self._redis_client: Optional[redis.Redis] = None
        self._redis_available = False
        
        # In-memory cache fallback
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'redis_hits': 0,
            'memory_hits': 0,
            'compressions': 0
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            self.logger.info("Using in-memory cache (Redis not available)")
            return False
        
        try:
            self._redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # We'll handle encoding ourselves
                socket_keepalive=True,
                socket_connect_timeout=5
            )
            
            # Test connection
            await self._redis_client.ping()
            self._redis_available = True
            self.logger.info("✅ Redis cache initialized successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self._redis_available = False
            return False
    
    def _generate_key(self, category: str, key: str) -> str:
        """Generate a namespaced cache key"""
        return f"workflow:{category}:{key}"
    
    def _compress_value(self, value: Any) -> bytes:
        """Compress value if it's large enough"""
        serialized = pickle.dumps(value)
        
        if self.use_compression and len(serialized) > self.compression_threshold:
            compressed = zlib.compress(serialized, level=6)
            if len(compressed) < len(serialized):
                self._cache_stats['compressions'] += 1
                return b"COMPRESSED:" + compressed
        
        return serialized
    
    def _decompress_value(self, data: bytes) -> Any:
        """Decompress value if it was compressed"""
        if data.startswith(b"COMPRESSED:"):
            decompressed = zlib.decompress(data[11:])
            return pickle.loads(decompressed)
        return pickle.loads(data)
    
    async def get(self, category: str, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            category: Cache category (for organization)
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        cache_key = self._generate_key(category, key)
        
        # Try Redis first
        if self._redis_available and self._redis_client:
            try:
                data = await self._redis_client.get(cache_key)
                if data:
                    self._cache_stats['hits'] += 1
                    self._cache_stats['redis_hits'] += 1
                    return self._decompress_value(data)
            except Exception as e:
                self.logger.debug(f"Redis get error: {e}")
        
        # Fallback to memory cache
        async with self._lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if entry['expires_at'] > time.time():
                    self._cache_stats['hits'] += 1
                    self._cache_stats['memory_hits'] += 1
                    return entry['value']
                else:
                    # Expired entry
                    del self._memory_cache[cache_key]
        
        self._cache_stats['misses'] += 1
        return None
    
    async def set(self, category: str, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            category: Cache category
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: TTL_MEDIUM)
            
        Returns:
            True if successful
        """
        if ttl is None:
            ttl = self.TTL_MEDIUM
        
        cache_key = self._generate_key(category, key)
        compressed_value = self._compress_value(value)
        
        # Try Redis first
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.setex(cache_key, ttl, compressed_value)
                return True
            except Exception as e:
                self.logger.debug(f"Redis set error: {e}")
        
        # Fallback to memory cache
        async with self._lock:
            self._memory_cache[cache_key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
            
            # Cleanup old entries if cache is getting large
            if len(self._memory_cache) > 1000:
                await self._cleanup_memory_cache()
        
        return True
    
    async def delete(self, category: str, key: str) -> bool:
        """Delete specific cache entry"""
        cache_key = self._generate_key(category, key)
        
        # Delete from Redis
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.delete(cache_key)
            except Exception as e:
                self.logger.debug(f"Redis delete error: {e}")
        
        # Delete from memory cache
        async with self._lock:
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
                return True
        
        return False
    
    async def invalidate_category(self, category: str) -> int:
        """
        Invalidate all cache entries in a category
        
        Args:
            category: Category to invalidate
            
        Returns:
            Number of entries invalidated
        """
        pattern = self._generate_key(category, "*")
        count = 0
        
        # Clear from Redis
        if self._redis_available and self._redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis_client.scan(
                        cursor, match=pattern, count=100
                    )
                    if keys:
                        await self._redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            except Exception as e:
                self.logger.debug(f"Redis invalidate error: {e}")
        
        # Clear from memory cache
        async with self._lock:
            keys_to_delete = [k for k in self._memory_cache if k.startswith(f"workflow:{category}:")]
            for key in keys_to_delete:
                del self._memory_cache[key]
                count += 1
        
        self.logger.info(f"Invalidated {count} cache entries in category '{category}'")
        return count
    
    async def _cleanup_memory_cache(self):
        """Remove expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self._memory_cache.items()
            if v['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self._memory_cache[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0
        if self._cache_stats['hits'] + self._cache_stats['misses'] > 0:
            hit_rate = self._cache_stats['hits'] / (self._cache_stats['hits'] + self._cache_stats['misses'])
        
        stats = {
            **self._cache_stats,
            'hit_rate': f"{hit_rate:.2%}",
            'memory_cache_size': len(self._memory_cache),
            'redis_available': self._redis_available,
            'compression_enabled': self.use_compression
        }
        
        # Get Redis info if available
        if self._redis_available and self._redis_client:
            try:
                info = await self._redis_client.info('memory')
                stats['redis_memory_used'] = info.get('used_memory_human', 'N/A')
            except:
                pass
        
        return stats
    
    async def close(self):
        """Close connections and cleanup"""
        if self._redis_client:
            await self._redis_client.close()
        
        self._memory_cache.clear()
        self.logger.info("Cache manager closed")

# Singleton instance
_cache_instance: Optional[CacheManager] = None

async def get_cache_manager() -> CacheManager:
    """Get or create singleton cache manager instance"""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = CacheManager()
        await _cache_instance.initialize()
    
    return _cache_instance

# Decorator for caching function results
def cached(category: str, ttl: int = None):
    """
    Decorator to cache async function results
    
    Usage:
        @cached(category=CacheManager.CATEGORY_PRODUCTS, ttl=CacheManager.TTL_LONG)
        async def get_product_data(product_id):
            # Expensive operation
            return data
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Get cache manager
            cache = await get_cache_manager()
            
            # Try to get from cache
            result = await cache.get(category, cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(category, cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
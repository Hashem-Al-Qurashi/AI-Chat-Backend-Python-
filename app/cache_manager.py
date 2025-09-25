from functools import lru_cache
from typing import Dict, Any, Optional, Tuple
import time
import hashlib
import json
import structlog

logger = structlog.get_logger()

class CacheManager:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}
        
    def _make_key(self, user_id: str, operation: str, *args) -> str:
        key_data = f"{user_id}:{operation}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get(self, user_id: str, operation: str, *args) -> Optional[Any]:
        key = self._make_key(user_id, operation, *args)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                logger.debug("cache_hit", user_id=user_id, operation=operation)
                return value
            else:
                del self.cache[key]
                
        logger.debug("cache_miss", user_id=user_id, operation=operation)
        return None
        
    def set(self, user_id: str, operation: str, value: Any, *args):
        key = self._make_key(user_id, operation, *args)
        
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            
        self.cache[key] = (value, time.time())
        logger.debug("cache_set", user_id=user_id, operation=operation)
        
    def invalidate_user(self, user_id: str):
        keys_to_remove = [
            key for key in self.cache.keys()
            if key.startswith(hashlib.md5(f"{user_id}:".encode()).hexdigest()[:8])
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
            
        logger.info("cache_invalidated", user_id=user_id, keys_removed=len(keys_to_remove))
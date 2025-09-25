from collections import defaultdict, deque
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, Deque
import structlog

logger = structlog.get_logger()

class RateLimiter:
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests_per_minute = max_requests_per_minute
        self.user_requests: Dict[str, Deque] = defaultdict(deque)
        self.lock = threading.Lock()
        
    def is_allowed(self, user_id: str) -> bool:
        with self.lock:
            now = time.time()
            minute_ago = now - 60
            
            while self.user_requests[user_id] and self.user_requests[user_id][0] < minute_ago:
                self.user_requests[user_id].popleft()
                
            if len(self.user_requests[user_id]) >= self.max_requests_per_minute:
                logger.warning(
                    "rate_limit_exceeded",
                    user_id=user_id,
                    requests_in_minute=len(self.user_requests[user_id])
                )
                return False
                
            self.user_requests[user_id].append(now)
            return True
            
    def get_wait_time(self, user_id: str) -> float:
        with self.lock:
            if not self.user_requests[user_id]:
                return 0
                
            oldest_request = self.user_requests[user_id][0]
            wait_time = 60 - (time.time() - oldest_request)
            return max(0, wait_time)
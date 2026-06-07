import redis
import json
from typing import Dict, Any, Optional
from app.core.config import settings
import urllib.parse as ul

class RedisStateMachine:
    def __init__(self):
        # We use a standard redis connection
        url = settings.CELERY_BROKER_URL
        p = ul.urlparse(url)

        # Security/Optimization:
        # Only apply manual SSL params if not already in the URL
        # and if the scheme is rediss://
        is_ssl = p.scheme == "rediss"

        # Strip ssl_cert_reqs from kwargs if it's already in the URL to avoid duplication errors
        kwargs = {}
        if is_ssl and "ssl_cert_reqs" not in p.query:
            kwargs["ssl_cert_reqs"] = "none"

        self.client = redis.from_url(url, **kwargs)

    def update_task_state(self, task_id: str, updates: Dict[str, Any]):
        """
        Uses HSET to atomically update multiple fields in a task hash.
        """
        key = f"task:state:{task_id}"
        # Convert all values to string for Redis Hash
        stringified = {k: json.dumps(v) if not isinstance(v, (str, int, float)) else v for k, v in updates.items()}
        self.client.hset(key, mapping=stringified)
        self.client.expire(key, 86400) # 24h retention

    def get_task_state(self, task_id: str) -> Dict[str, str]:
        key = f"task:state:{task_id}"
        return self.client.hgetall(key)

redis_state = RedisStateMachine()

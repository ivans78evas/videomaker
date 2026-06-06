import redis
import json
from typing import Dict, Any, Optional
from app.core.config import settings

class RedisStateMachine:
    def __init__(self):
        # We use a standard redis connection, ensuring it handles TLS if needed
        import urllib.parse as ul
        p = ul.urlparse(settings.CELERY_BROKER_URL)
        ssl = p.scheme == "rediss"

        self.client = redis.from_url(
            settings.CELERY_BROKER_URL,
            ssl_cert_reqs="none" if ssl else None
        )

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

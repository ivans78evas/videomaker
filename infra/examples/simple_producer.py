import redis
import json
import uuid
import os

# Configuration (Use your Upstash URL)
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Connect with TLS support for Upstash
ssl = REDIS_URL.startswith("rediss://")
r = redis.from_url(REDIS_URL, ssl_cert_reqs="none" if ssl else None)

def create_raw_task(url: str, lang: str = "de"):
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "youtube_url": url,
        "target_language": lang,
        "status": "pending"
    }

    # 1. Push to queue
    r.lpush("gpu_tasks", json.dumps(task_data))

    # 2. Initialize state
    r.hset(f"task:state:{task_id}", mapping=task_data)

    print(f"🚀 Task Created: {task_id}")
    print(f"Check state with: redis-cli HGETALL task:state:{task_id}")

if __name__ == "__main__":
    create_raw_task("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "es")

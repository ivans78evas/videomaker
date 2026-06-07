import redis
import json
import time
import os

# Configuration
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
ssl = REDIS_URL.startswith("rediss://")
r = redis.from_url(REDIS_URL, ssl_cert_reqs="none" if ssl else None)

def process_tasks():
    print("🤖 Worker Listening for tasks in 'gpu_tasks'...")
    while True:
        # BRPOP 60s timeout to save Upstash commands
        task = r.brpop("gpu_tasks", timeout=60)

        if task:
            task_data = json.loads(task[1])
            task_id = task_data["task_id"]

            print(f"📦 [START] Task {task_id}")

            # 1. Update State to Processing
            r.hset(f"task:state:{task_id}", "status", "processing")

            # 2. Simulate Work (Dubbing Pipeline)
            time.sleep(5)

            # 3. Update State to Completed
            r.hset(f"task:state:{task_id}", mapping={
                "status": "completed",
                "output_url": "https://s3.example.com/vids/result.mp4"
            })

            print(f"✅ [DONE] Task {task_id}")
        else:
            print("... No tasks. Sleeping for 60s.")

if __name__ == "__main__":
    process_tasks()

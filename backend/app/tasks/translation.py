from app.tasks.worker import celery_app
from app.services.ingestion import ingestion_service
import time

@celery_app.task(name="tasks.process_translation")
def process_translation(task_id: str, url: str):
    """Initial dummy task to verify pipeline."""
    print(f"Starting translation task: {task_id}")

    # 1. Ingestion
    info = ingestion_service.get_info(url)
    print(f"Ingested metadata: {info['title']}")

    # Simulate processing
    time.sleep(5)

    print(f"Task {task_id} completed (Simulated)")
    return {"status": "success", "title": info["title"]}

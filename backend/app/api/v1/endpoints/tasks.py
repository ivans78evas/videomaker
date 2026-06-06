from app.core.config import settings
from app.db.session import get_db
from app.models.models import TranslationTask
from app.services.channel_service import channel_service
from app.services.ingestion import ingestion_service
from app.tasks.translation import process_translation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

router = APIRouter()

class TranslationRequest(BaseModel):
    url: str
    target_lang: str

@router.get("/workers")
def get_workers_status():
    """
    Returns the number and names of active workers.
    NOTE: This requires worker_enable_remote_control=True in celery_app.py.
    In 'Quota-Saver' mode, this is disabled to save Redis commands.
    """
    try:
        from app.celery_app import celery_app
        i = celery_app.control.inspect(timeout=1.0)
        active = i.active()

        if active is None:
            return {"count": 0, "workers": [], "mode": "quota_saver_active?"}

        return {
            "count": len(active),
            "workers": list(active.keys())
        }
    except Exception:
        return {"error": "Could not inspect workers. Remote control might be disabled."}

@router.post("/")
def create_task(request: TranslationRequest, db: Session = Depends(get_db)):
    # Handle both single URLs and Playlists
    urls = ingestion_service.extract_playlist_urls(request.url)

    task_ids = []
    # Ensure default channel exists for prototype via Service
    default_channel = channel_service.get_or_create_default_channel(db)

    for url in urls:
        task_id = str(uuid.uuid4())
        # Save to DB
        new_task = TranslationTask(
            id=task_id,
            channel_id=default_channel.id,
            source_url=url,
            target_language=request.target_lang,
            status="pending"
        )
        db.add(new_task)
        task_ids.append(task_id)

    db.commit()

    # Send to Celery
    for tid, url in zip(task_ids, urls):
        process_translation.delay(tid, url, request.target_lang)

    return {
        "count": len(task_ids),
        "task_ids": task_ids,
        "status": "queued"
    }

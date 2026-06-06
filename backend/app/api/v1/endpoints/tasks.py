from app.core.config import settings
from app.db.session import get_db
from app.models.models import TranslationTask
from app.services.channel_service import channel_service
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
    """
    from app.celery_app import celery_app
    i = celery_app.control.inspect()
    active = i.active()

    if active is None:
        return {"count": 0, "workers": []}

    return {
        "count": len(active),
        "workers": list(active.keys())
    }

@router.post("/")
def create_task(request: TranslationRequest, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())

    # Ensure default channel exists for prototype via Service
    default_channel = channel_service.get_or_create_default_channel(db)

    # Save to DB
    new_task = TranslationTask(
        id=task_id,
        channel_id=default_channel.id,
        source_url=request.url,
        target_language=request.target_lang,
        status="pending"
    )

    db.add(new_task)
    db.commit()

    # Send to Celery
    process_translation.delay(task_id, request.url, request.target_lang)

    return {"task_id": task_id, "status": "queued"}

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import TranslationTask
from app.tasks.translation import process_translation
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

router = APIRouter()

class TranslationRequest(BaseModel):
    url: str
    target_lang: str

@router.post("/")
def create_task(request: TranslationRequest, db: Session = Depends(SessionLocal)):
    task_id = str(uuid.uuid4())

    # Save to DB
    new_task = TranslationTask(
        id=task_id,
        source_url=request.url,
        target_language=request.target_lang,
        status="pending"
    )
    # Note: In a real environment, we'd need to link a channel_id
    # For now, we stub a default channel if none exists
    new_task.channel_id = "default_channel"

    # db.add(new_task)
    # db.commit()

    # Send to Celery
    process_translation.delay(task_id, request.url, request.target_lang)

    return {"task_id": task_id, "status": "queued"}

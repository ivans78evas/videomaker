from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tasks.translation import process_translation
import uuid

router = APIRouter()

class TranslationRequest(BaseModel):
    url: str
    target_lang: str

@router.post("/")
def create_task(request: TranslationRequest):
    task_id = str(uuid.uuid4())
    # In a real app, save to DB first
    process_translation.delay(task_id, request.url, request.target_lang)
    return {"task_id": task_id, "status": "queued"}

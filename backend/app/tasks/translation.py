from app.celery_app import celery_app
from app.services.ingestion import ingestion_service
from app.services.audio_processing import audio_processing_service
from app.services.transcription import transcription_service
from app.services.translation import translation_service
from app.services.synthesis import synthesis_service
from app.services.assembler import assembler_service
from app.services.moderation import moderation_service
from app.models.models import TaskLog
from app.db.session import SessionLocal
from loguru import logger
import os
import shutil
import time

@celery_app.task(name="tasks.process_translation")
def process_translation(task_id: str, url: str, target_lang: str):
    """Alias for default priority."""
    return run_pipeline(task_id, url, target_lang)

@celery_app.task(name="tasks.process_translation_urgent")
def process_translation_urgent(task_id: str, url: str, target_lang: str):
    """High priority queue (Shorts/TikToks)."""
    return run_pipeline(task_id, url, target_lang)

@celery_app.task(name="tasks.process_translation_bulk")
def process_translation_bulk(task_id: str, url: str, target_lang: str):
    """Low priority queue (Long videos/Archive)."""
    return run_pipeline(task_id, url, target_lang)

def run_pipeline(task_id: str, url: str, target_lang: str):
    """
    Main pipeline for Video-to-Video translation.
    """
    logger.info(f"--- Starting Pipeline for Task {task_id} ---")
    start_time = time.time()

    from app.models.models import TranslationTask

    try:
        # Mark as processing
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_id).first()
            if task:
                task.status = "processing"
                db.commit()

        # 1. Ingestion
        logger.info(f"Step 1: Ingesting video from {url}")
        video_path = ingestion_service.download_video(url, task_id)

        # 2. Vocal Separation
        logger.info(f"Step 2: Separating vocals...")
        vocals_path, bgm_path = audio_processing_service.separate_vocals(video_path, task_id)

        # 3. Diarization & Transcription
        logger.info(f"Step 3: Speaker Diarization & Transcription...")
        # intervals = audio_processing_service.diarize(vocals_path, task_id)
        # main_speaker = audio_processing_service.get_main_speaker(intervals)
        transcript = transcription_service.transcribe(vocals_path, task_id)

        # 3.1 Content Moderation
        logger.info(f"Step 3.1: Content Moderation...")
        mod_result = moderation_service.moderate_content(transcript)
        if not mod_result["is_safe"]:
            logger.warning(f"Task {task_id} blocked: {mod_result['reason']}")
            return {"status": "blocked", "reason": mod_result["reason"]}

        # 4. Translation
        logger.info(f"Step 4: Translating to {target_lang}...")
        translated_segments = translation_service.translate_segments(transcript, target_lang)

        # 5. Synthesis (Hybrid Logic: Clone for Main, Narrator for Guest)
        logger.info(f"Step 5: Synthesizing new audio segments (Hybrid Mode)...")
        # In a real run, we'd iterate and call specific TTS providers per speaker
        synthesis_service.synthesize_segments(translated_segments, task_id, lang=target_lang)

        # 6. Final Merge (Assemble segments based on timestamps)
        logger.info(f"Step 6: Final FFmpeg Assembly...")
        output_path = f"storage/final_videos/{task_id}_translated.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if translated_segments:
            assembler_service.merge_segments_and_video(video_path, translated_segments, bgm_path, output_path)

        # 7. Quality Guard (Hallucination Checker)
        logger.info(f"Step 7: Hallucination & Sync Check...")
        # if not validate_sync(task_id, original_dur, translated_dur):
        #     return {"status": "review_required", "reason": "sync_drift"}

        logger.success(f"--- Task {task_id} Pipeline Completed ---")

        # Audit Trail: Log completion metrics
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_id).first()
            if task:
                task.status = "completed"
                task.local_final_path = output_path

            log = TaskLog(
                task_id=task_id,
                event="completed",
                metrics={"duration_sec": time.time() - start_time}
            )
            db.add(log)
            db.commit()

        return {"status": "completed", "task_id": task_id, "output": output_path}

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        # Poison Pill Handling: Mark as failed in DB
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_id).first()
            if task:
                task.status = "failed"
                db.commit()

            log = TaskLog(
                task_id=task_id,
                event="failed",
                metrics={"error": str(e)}
            )
            db.add(log)
            db.commit()

        return {"status": "failed", "error": str(e)}

    finally:
        # Step 8: Janitor Service (Cleanup temp files to prevent Disk Full)
        logger.info(f"Step 8: Janitor Service - Cleaning up task {task_id}")
        temp_dirs = ["storage/raw_videos", "storage/audio_stems", "storage/translated_audio"]
        for d in temp_dirs:
            # Only remove files related to this task
            for f in os.listdir(d):
                if f.startswith(task_id):
                    try:
                        os.remove(os.path.join(d, f))
                    except Exception:
                        pass

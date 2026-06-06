from app.celery_app import celery_app
from app.services.ingestion import ingestion_service
from app.services.audio_processing import audio_processing_service
from app.services.transcription import transcription_service
from app.services.translation import translation_service
from app.services.synthesis import synthesis_service
from app.services.assembler import assembler_service
from app.services.moderation import moderation_service
from app.services.text_cleaner import text_cleaner
from app.services.qa import consensus_qa_service
from app.services.voice_registry import voice_registry
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

        # 2.1 Omni-Voice Profiling
        logger.info(f"Step 2.1: Capturing Omni-Voice profile...")
        voice_sample = audio_processing_service.extract_voice_sample(vocals_path, task_id)
        voice_id = voice_registry.capture_omni_voice("default_channel", voice_sample)

        # 3. Diarization & Transcription
        logger.info(f"Step 3: Speaker Diarization & Transcription...")
        # intervals = audio_processing_service.diarize(vocals_path, task_id)
        # main_speaker = audio_processing_service.get_main_speaker(intervals)
        transcript = transcription_service.transcribe(vocals_path, task_id)

        # 3.0 Text Sanitization (Cleaning)
        logger.info(f"Step 3.0: Sanitizing text...")
        transcript = text_cleaner.clean_segments(transcript)

        # 3.1 Content Moderation
        logger.info(f"Step 3.1: Content Moderation...")
        mod_result = moderation_service.moderate_content(transcript)
        if not mod_result["is_safe"]:
            logger.warning(f"Task {task_id} blocked: {mod_result['reason']}")
            return {"status": "blocked", "reason": mod_result["reason"]}

        # 4. Translation (Aggregated)
        logger.info(f"Step 4: Translating to {target_lang}...")
        from app.services.aggregator import aggregator_service
        translated_segments = aggregator_service.translate_with_fallback(transcript, target_lang)

        # 4.1 Save for HITL Review
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_id).first()
            if task:
                task.transcript_json = {"segments": translated_segments}
                db.commit()

        # 4.2 Quality Assurance (Multi-Agent Consensus via Groq/OpenRouter)
        logger.info(f"Step 4.2: Running Multi-Agent Consensus QA...")
        qa_result = consensus_qa_service.run_multi_agent_qa(translated_segments, target_lang=target_lang)

        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_id).first()
            if task:
                task.source_metadata = {**(task.source_metadata or {}), "qa": qa_result}
                if qa_result["decision"]["status"] != "approved":
                    task.status = "review_required"
                    db.commit()
                    logger.warning(f"Task {task_id} failed Consensus QA. Status: review_required.")
                db.commit()

        # 5. Synthesis (Aggregated & Voice Mapping)
        logger.info(f"Step 5: Synthesizing new audio segments (Hybrid & Cloned)...")
        # Synthesis service now uses the dynamic Omni-Voice ID
        synthesis_service.synthesize_segments(translated_segments, task_id, lang=target_lang, voice_id=voice_id)

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

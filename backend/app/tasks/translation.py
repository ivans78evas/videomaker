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
from app.services.redis_state import redis_state
from app.models.models import TaskLog, TranslationTask
from app.db.session import SessionLocal
from loguru import logger
import os
import shutil
import time
import uuid

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
    Main pipeline for Video-to-Video translation based on Enterprise Flowchart.
    """
    logger.info(f"--- Starting Pipeline for Task {task_id} ---")
    start_time = time.time()

    # Ensure task_id is a UUID object for SQLAlchemy consistency
    task_uuid = uuid.UUID(task_id) if isinstance(task_id, str) else task_id
    task_id_str = str(task_id)

    try:
        # 0. Initial State Sync
        redis_state.update_task_state(task_id_str, {"status": "processing", "step": "ingestion"})
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_uuid).first()
            if task:
                task.status = "processing"
                db.commit()

        # 1. Ingestion & Extraction (yt-dlp + FFmpeg)
        logger.info(f"Step 1: Ingesting video from {url}")
        video_path = ingestion_service.download_video(url, task_id_str)

        # 2. Vocal Separation (HDemucs)
        logger.info(f"Step 2: Separating vocals via HDemucs...")
        redis_state.update_task_state(task_id_str, {"step": "separation"})
        vocals_path, bgm_path = audio_processing_service.separate_vocals(video_path, task_id_str)

        # 2.1 Omni-Voice Profiling (Zero-Shot)
        logger.info(f"Step 2.1: Capturing Omni-Voice profile...")
        voice_sample = audio_processing_service.extract_voice_sample(vocals_path, task_id_str)
        voice_id = voice_registry.capture_omni_voice("default_channel", voice_sample)

        # 3. VAD & Transcription (Faster-Whisper Turbo)
        logger.info(f"Step 3: Transcription with VAD Preprocessing...")
        redis_state.update_task_state(task_id_str, {"step": "transcription"})
        # In a real run, Silero VAD would be called here or integrated in Whisper
        transcript = transcription_service.transcribe(vocals_path, task_id_str)

        # 3.0 Text Sanitization (Cleaning)
        logger.info(f"Step 3.0: Sanitizing text...")
        transcript = text_cleaner.clean_segments(transcript)

        # 3.1 Content Moderation
        logger.info(f"Step 3.1: Content Moderation...")
        mod_result = moderation_service.moderate_content(transcript)
        if not mod_result["is_safe"]:
            logger.warning(f"Task {task_id_str} blocked: {mod_result['reason']}")
            redis_state.update_task_state(task_id_str, {"status": "blocked"})
            return {"status": "blocked", "reason": mod_result["reason"]}

        # 4. Translation (Aggregated: Groq/OpenRouter)
        logger.info(f"Step 4: Translating to {target_lang}...")
        redis_state.update_task_state(task_id_str, {"step": "translation"})
        from app.services.aggregator import aggregator_service
        translated_segments = aggregator_service.translate_with_fallback(transcript, target_lang)

        # 4.1 Save for HITL/SRT
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_uuid).first()
            if task:
                task.transcript_json = {"segments": translated_segments}
                db.commit()

        # 4.2 Multi-Agent Consensus QA
        logger.info(f"Step 4.2: Running Multi-Agent Consensus QA...")
        redis_state.update_task_state(task_id_str, {"step": "qa_consensus"})
        qa_result = consensus_qa_service.run_multi_agent_qa(translated_segments, target_lang=target_lang)

        redis_state.update_task_state(task_id_str, {
            "qa_status": qa_result["decision"]["status"],
            "qa_score": qa_result["decision"]["final_score"]
        })

        if qa_result["decision"]["status"] != "approved":
            logger.warning(f"Task {task_id_str} failed Consensus QA. Status: review_required.")
            redis_state.update_task_state(task_id_str, {"status": "review_required"})
            with SessionLocal() as db:
                task = db.query(TranslationTask).filter(TranslationTask.id == task_uuid).first()
                if task:
                    task.status = "review_required"
                    task.source_metadata = {**(task.source_metadata or {}), "qa": qa_result}
                    db.commit()
            # Return early if human review is required
            # return {"status": "review_required", "task_id": task_id_str}

        # 5. Synthesis (Omni-Voice / F5-TTS Style)
        logger.info(f"Step 5: Neural TTS Synthesis...")
        redis_state.update_task_state(task_id_str, {"step": "synthesis"})
        synthesis_service.synthesize_segments(translated_segments, task_id_str, lang=target_lang, voice_id=voice_id)

        # 6. Assembly (EQ / Sync / Mix)
        logger.info(f"Step 6: Final FFmpeg Assembly & Mixing...")
        redis_state.update_task_state(task_id_str, {"step": "assembly"})
        output_path = f"storage/final_videos/{task_id_str}_translated.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if translated_segments:
            assembler_service.merge_segments_and_video(video_path, translated_segments, bgm_path, output_path)

        # 7. Final State Sync
        logger.success(f"--- Task {task_id_str} Pipeline Completed ---")
        redis_state.update_task_state(task_id_str, {"status": "completed", "step": "finished"})

        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_uuid).first()
            if task:
                task.status = "completed"
                task.local_final_path = output_path

            log = TaskLog(
                task_id=task_uuid,
                event="completed",
                metrics={"duration_sec": time.time() - start_time}
            )
            db.add(log)
            db.commit()

        return {"status": "completed", "task_id": task_id_str, "output": output_path}

    except Exception as e:
        logger.error(f"Task {task_id_str} failed: {str(e)}")
        # Poison Pill Handling
        with SessionLocal() as db:
            task = db.query(TranslationTask).filter(TranslationTask.id == task_uuid).first()
            if task:
                task.status = "failed"
                db.commit()

            log = TaskLog(
                task_id=task_uuid,
                event="failed",
                metrics={"error": str(e)}
            )
            db.add(log)
            db.commit()

        redis_state.update_task_state(task_id_str, {"status": "failed", "error": str(e)})
        return {"status": "failed", "error": str(e)}

    finally:
        # Step 8: Janitor Service
        logger.info(f"Step 8: Janitor Service - Cleaning up task {task_id_str}")
        temp_dirs = ["storage/raw_videos", "storage/audio_stems", "storage/translated_audio"]
        for d in temp_dirs:
            full_d = os.path.join(os.getcwd(), d)
            if not os.path.exists(full_d): continue
            for f in os.listdir(full_d):
                if f.startswith(task_id_str):
                    try:
                        os.remove(os.path.join(full_d, f))
                    except Exception:
                        pass

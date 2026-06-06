from app.celery_app import celery_app
from app.services.ingestion import ingestion_service
from app.services.audio_processing import audio_processing_service
from app.services.transcription import transcription_service
from app.services.translation import translation_service
from app.services.synthesis import synthesis_service
from app.services.assembler import assembler_service
from loguru import logger
import os

@celery_app.task(name="tasks.process_translation")
def process_translation(task_id: str, url: str, target_lang: str):
    """
    Main pipeline for Video-to-Video translation.
    """
    logger.info(f"--- Starting Pipeline for Task {task_id} ---")

    try:
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

        # Note: In a real implementation, we'd use complex FFmpeg filter_complex
        # to place each segment at its specific 'start' timestamp.
        # For the prototype, we use the first segment to demonstrate the flow.
        if translated_segments:
            translated_vocals_path = translated_segments[0]["local_audio_path"]
            assembler_service.merge_audio_video(video_path, translated_vocals_path, bgm_path, output_path)

        logger.success(f"--- Task {task_id} Pipeline Completed ---")
        return {"status": "completed", "task_id": task_id, "output": output_path}

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

import sys
import os
from pathlib import Path
import time
import json
import uuid
from loguru import logger

# 1. Path Setup: Ensure we can import from backend
current_dir = Path(__file__).parent.resolve()
repo_root = current_dir.parent
backend_path = repo_root / "backend"

if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

# 2. Mock Environment for Independent Script Execution
os.environ.setdefault("GROQ_API_KEY", "stub")
os.environ.setdefault("OPENROUTER_API_KEY", "stub")
os.environ.setdefault("POSTGRES_SERVER", "localhost")

# Force SQLite for local script testing to avoid connection refused on Postgres
from sqlalchemy import create_engine
import app.db.session as session_module
engine = create_engine("sqlite:///./test.db")
session_module.engine = engine
from sqlalchemy.orm import sessionmaker
session_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    from app.tasks.translation import run_pipeline
    from app.models.models import Base
except ImportError as e:
    logger.error(f"❌ Failed to import backend services: {e}")
    sys.exit(1)

def setup_test_environment():
    """Initializes local storage and database for the test cycle."""
    logger.info("🔧 Setting up test environment (SQLite Fallback)...")

    # Create storage structure in backend/storage
    storage_dirs = [
        "raw_videos", "audio_stems", "transcripts",
        "translated_audio", "final_videos"
    ]
    for d in storage_dirs:
        (backend_path / "storage" / d).mkdir(parents=True, exist_ok=True)

    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    logger.success("✅ Database initialized.")

def run_test(youtube_url: str, target_lang: str = "German"):
    logger.info("🎬 STARTING FULL-CYCLE VIDEO TRANSLATION TEST")
    logger.info(f"Target: {youtube_url} -> {target_lang}")

    setup_test_environment()

    task_id = str(uuid.uuid4())
    logger.info(f"🆔 Task ID: {task_id}")

    # Pre-create task in SQLite since the pipeline expects it
    from app.models.models import TranslationTask
    with session_module.SessionLocal() as db:
        # Need a default channel
        from app.services.channel_service import channel_service
        channel = channel_service.get_or_create_default_channel(db)

        task = TranslationTask(
            id=uuid.UUID(task_id),
            channel_id=channel.id,
            source_url=youtube_url,
            target_language=target_lang,
            status="pending"
        )
        db.add(task)
        db.commit()

    try:
        start_time = time.time()
        result = run_pipeline(task_id, youtube_url, target_lang)
        duration = time.time() - start_time

        logger.info(f"⏱️ Pipeline finished in {duration:.2f} seconds.")

        if result.get("status") == "completed":
            logger.success("🏆 TEST PASSED: Video translated successfully.")
            logger.info(f"📁 Output Location: {result.get('output')}")
        elif result.get("status") == "review_required":
            logger.warning("🟡 TEST FINISHED: Quality Assurance flagged for review.")
        else:
            logger.error(f"💀 TEST FAILED: {result.get('error')}")

    except Exception as e:
        logger.exception(f"🔥 Fatal error during test execution: {e}")

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    run_test(test_url)

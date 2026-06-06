from app.services.ingestion import IngestionService
import pytest

def test_ingestion_service_info():
    """Verify metadata extraction from a known URL."""
    # Using a short stable YouTube URL
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Big Buck Bunny
    service = IngestionService()
    info = service.get_info(url)

    assert info["id"] == "aqz-KE-bpKQ"
    assert "title" in info
    assert "duration" in info

import yt_dlp
import os
from pathlib import Path
from typing import Dict, Any

class IngestionService:
    def __init__(self, download_dir: str = "storage/raw_videos"):
        self.download_dir = download_dir
        Path(download_dir).mkdir(parents=True, exist_ok=True)

    def get_info(self, url: str) -> Dict[str, Any]:
        """Extract metadata without downloading."""
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title"),
                "description": info.get("description"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "view_count": info.get("view_count"),
                "tags": info.get("tags"),
            }

    def download_video(self, url: str, task_id: str) -> str:
        """Download high quality video."""
        output_path = os.path.join(self.download_dir, f"{task_id}.%(ext)s")
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            # Return the actual file path (ext might vary if not forced)
            # For simplicity in this base version, we assume .mp4 due to merge_output_format
            return os.path.join(self.download_dir, f"{task_id}.mp4")

ingestion_service = IngestionService()

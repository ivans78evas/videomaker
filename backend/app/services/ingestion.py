import yt_dlp
import os
from pathlib import Path
from typing import Dict, Any, List

class IngestionService:
    def __init__(self, download_dir: str = "storage/raw_videos"):
        self.download_dir = download_dir
        Path(download_dir).mkdir(parents=True, exist_ok=True)

    def get_info(self, url: str) -> Dict[str, Any]:
        """Extract metadata without downloading."""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    def extract_playlist_urls(self, playlist_url: str) -> List[str]:
        """
        Extracts all video URLs from a playlist or channel.
        """
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            if 'entries' in result:
                return [f"https://www.youtube.com/watch?v={entry['id']}" for entry in result['entries'] if entry]
            return [playlist_url]

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

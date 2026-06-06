import os
import subprocess
from pathlib import Path
from typing import Tuple

class AudioProcessingService:
    def __init__(self, stems_dir: str = "storage/audio_stems"):
        self.stems_dir = stems_dir
        Path(stems_dir).mkdir(parents=True, exist_ok=True)

    def separate_vocals(self, video_path: str, task_id: str) -> Tuple[str, str]:
        """
        Uses Demucs to separate vocals from background music.
        Returns paths to (vocals_path, bgm_path).
        """
        # Demucs creates a folder based on model name (default: hdemucs_l)
        model_name = "hdemucs_l"
        track_name = Path(video_path).stem
        base_output = os.path.join(self.stems_dir, model_name, track_name)

        vocals_path = os.path.join(base_output, "vocals.wav")
        bgm_path = os.path.join(base_output, "no_vocals.wav")

        # Check if already processed
        if os.path.exists(vocals_path) and os.path.exists(bgm_path):
            return vocals_path, bgm_path

        cmd = [
            "demucs",
            "--two-stems=vocals",
            "-o", self.stems_dir,
            video_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Demucs failed: {e.stderr.decode()}")

        return vocals_path, bgm_path

    def diarize(self, audio_path: str, task_id: str):
        """
        Uses Pyannote.audio or Whisper metadata to identify speakers.
        """
        # Logic for Pyannote integration
        # In a real environment:
        # from pyannote.audio import Pipeline
        # pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
        # diarization = pipeline(audio_path)

        # Mocking for the blueprint
        return [
            {"start": 0.0, "end": 10.0, "speaker": "MAIN_SPEAKER"},
            {"start": 10.0, "end": 15.0, "speaker": "GUEST_SPEAKER"}
        ]

    def get_main_speaker(self, intervals: list) -> str:
        """
        Identifies the main speaker by total duration.
        """
        stats = {}
        for interval in intervals:
            spk = interval["speaker"]
            duration = interval["end"] - interval["start"]
            stats[spk] = stats.get(spk, 0) + duration

        if not stats: return None
        return max(stats, key=stats.get)

audio_processing_service = AudioProcessingService()

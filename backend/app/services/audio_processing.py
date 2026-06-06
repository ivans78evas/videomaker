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
        Uses Pyannote.audio to identify speaker intervals.
        """
        print(f"Diarizing audio for task {task_id}...")
        # Logic for Pyannote integration would go here
        # Return segments list: [{"start": 0.0, "end": 5.0, "speaker": "SPEAKER_00"}, ...]
        return []

audio_processing_service = AudioProcessingService()

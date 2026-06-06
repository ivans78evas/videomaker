import os
from typing import List, Dict, Any
from pathlib import Path

class TranscriptionService:
    def __init__(self, transcript_dir: str = "storage/transcripts"):
        self.transcript_dir = transcript_dir
        Path(transcript_dir).mkdir(parents=True, exist_ok=True)

    def transcribe(self, audio_path: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Uses Faster-Whisper to generate timestamped transcription.
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError("faster-whisper is not installed in this environment.")

        # In production, we'd use a shared model instance to avoid reloading
        # For the implementation, we use GPU if available
        model = WhisperModel("large-v3", device="auto", compute_type="int8")
        segments, _ = model.transcribe(audio_path, beam_size=5)

        results = []
        for segment in segments:
            results.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            })

        return results

transcription_service = TranscriptionService()

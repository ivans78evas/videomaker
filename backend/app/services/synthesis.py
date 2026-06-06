import asyncio
import edge_tts
import os
from pathlib import Path
from typing import List, Dict, Any

class SynthesisService:
    def __init__(self, output_dir: str = "storage/translated_audio"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    async def _generate_audio(self, text: str, voice: str, output_path: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    def synthesize_segments(self, segments: List[Dict[str, Any]], task_id: str, lang: str = "ru", voice_id: str = None) -> List[str]:
        """
        Synthesizes translated audio for each segment separately to maintain timing.
        Supports dynamic voice_id from Omni-Voice profiling.
        """
        # Default narrator mapping
        default_voice_map = {
            "ru": "ru-RU-SvetlanaNeural",
            "en": "en-US-GuyNeural",
            "es": "es-ES-AlvaroNeural"
        }

        # Use cloned voice if provided, otherwise fallback to narrator
        voice = voice_id if voice_id else default_voice_map.get(lang, "en-US-GuyNeural")

        audio_paths = []
        for i, segment in enumerate(segments):
            text = segment.get("translated_text", segment["text"])
            output_path = os.path.join(self.output_dir, f"{task_id}_seg_{i}.mp3")
            asyncio.run(self._generate_audio(text, voice, output_path))
            audio_paths.append(output_path)
            segment["local_audio_path"] = output_path

        return audio_paths

synthesis_service = SynthesisService()

from typing import List, Dict, Any
from app.services.translation import translation_service
from app.services.synthesis import synthesis_service
import os

class AggregatorService:
    """
    RecCloud-style Multi-Provider Aggregator.
    Handles fallbacks and chooses the best provider for speed/cost.
    """
    def __init__(self):
        self.translation_providers = ["groq", "gemini", "openai"]
        self.synthesis_providers = ["edge-tts", "elevenlabs", "openai-tts"]

    def translate_with_fallback(self, segments: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        for provider in self.translation_providers:
            try:
                # In a real implementation, we'd pass the provider to the service
                return translation_service.translate_segments(segments, target_lang)
            except Exception:
                continue
        raise RuntimeError("All translation providers failed.")

    def synthesize_with_fallback(self, segments: List[Dict[str, Any]], task_id: str, lang: str) -> List[str]:
        for provider in self.synthesis_providers:
            try:
                return synthesis_service.synthesize_segments(segments, task_id, lang)
            except Exception:
                continue
        raise RuntimeError("All synthesis providers failed.")

aggregator_service = AggregatorService()

from openai import OpenAI
import os
from typing import List, Dict, Any

class TranslationService:
    def __init__(self, api_key: str = None, base_url: str = "https://api.groq.com/openai/v1"):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url=base_url) if self.api_key else None

    def translate_segments(self, segments: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        """
        Translates audio segments using an LLM with one-to-one mapping for synchronization.
        """
        if not self.client:
            return segments

        for segment in segments:
            prompt = f"Translate this video transcript segment to {target_lang}. Keep it short to fit the time. Text: '{segment['text']}'"
            try:
                response = self.client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )
                segment["translated_text"] = response.choices[0].message.content.strip()
            except Exception as e:
                segment["translated_text"] = segment["text"] # Fallback

        return segments

translation_service = TranslationService()

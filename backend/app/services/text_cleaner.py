import re
from typing import List, Dict, Any

class TextCleanerService:
    """
    Sanitizes transcription text before translation and synthesis.
    Removes junk tags and TTS-breaking symbols.
    """
    def __init__(self):
        # Remove common transcription tags like [MUSIC], [INAUDIBLE], (Laughter)
        self.tag_pattern = re.compile(r'\[.*?\]|\(.*?\)|\{.*?\}')
        # Remove symbols that might break TTS or cause strange artifacts
        self.symbol_pattern = re.compile(r'[^\w\s\.,!?\-\'\"]')

    def clean_text(self, text: str) -> str:
        # 1. Remove tags
        text = self.tag_pattern.sub('', text)
        # 2. Remove illegal symbols
        text = self.symbol_pattern.sub('', text)
        # 3. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def clean_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for seg in segments:
            seg["text"] = self.clean_text(seg["text"])
        return segments

text_cleaner = TextCleanerService()

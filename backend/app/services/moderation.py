from typing import List, Dict, Any
from openai import OpenAI
import os

class ModerationService:
    def __init__(self):
        # We use the same LLM provider as translation for cost-efficiency
        self.api_key = os.getenv("LLM_API_KEY", "stub_key")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def moderate_content(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the full transcript for policy violations, stop-words, or unsafe categories.
        """
        full_text = " ".join([s["text"] for s in segments])

        # In a real run, we'd call the LLM with a specific moderation prompt
        # For the prototype, we return a passing status unless explicit stop-words are found
        stop_words = ["unsafe-word-1", "unsafe-word-2"]
        found = [w for w in stop_words if w in full_text.lower()]

        if found:
            return {
                "is_safe": False,
                "reason": f"Found blocked content: {', '.join(found)}",
                "category": "safety_violation"
            }

        return {"is_safe": True, "category": "safe"}

moderation_service = ModerationService()

import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from loguru import logger

class OpenRouterFreeGuard:
    """
    Monitors OpenRouter for free-to-use models and ensures zero-cost compliance.
    """
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"

    def fetch_free_models(self) -> List[str]:
        """
        Fetches current model list from OpenRouter and filters for price == 0.
        """
        if self.api_key == "stub":
            return ["meta-llama/llama-3-8b-instruct:free"]

        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/models")
                response.raise_for_status()
                data = response.json()

                free_models = []
                for model in data.get("data", []):
                    # Check pricing (per token cost should be 0)
                    pricing = model.get("pricing", {})
                    if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                        free_models.append(model["id"])

                if not free_models:
                    logger.critical("CRITICAL: No free models found on OpenRouter! Zero-cost strategy compromised.")

                return free_models
        except Exception as e:
            logger.error(f"Failed to fetch OpenRouter models: {e}")
            return ["meta-llama/llama-3-8b-instruct:free"] # Safe fallback

    def ensure_model_is_free(self, model_id: str) -> bool:
        """
        Validates a specific model is still in the free tier.
        """
        free_list = self.fetch_free_models()
        return model_id in free_list

openrouter_guard = OpenRouterFreeGuard()

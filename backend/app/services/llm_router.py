import os
import json
import httpx
from typing import Dict, Any, Optional
from groq import Groq
from app.core.config import settings
from app.services.quota import quota_service

class UnifiedLLMService:
    """
    Hybrid Router for LLM tasks using provided Model Inventory.
    Routes between Groq (High Quality) and OpenRouter (Free/Low Cost).
    """
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY != "stub" else None
        self.openrouter_key = settings.OPENROUTER_API_KEY

    def call_groq(self, system: str, user: str, model: str) -> Dict[str, Any]:
        if not self.groq_client:
            return {"score": 9, "feedback": "Groq Stub"}

        # Check Quota
        if not quota_service.check_quota(model):
            # Failover to Standard model
            if model == "llama-3.3-70b-versatile":
                return self.call_groq(system, user, "meta-llama/llama-4-scout-17b-16e-instruct")
            return {"error": "Quota exceeded"}

        completion = self.groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        # Track usage
        tokens_used = completion.usage.total_tokens
        quota_service.increment_quota(model, tokens_used)

        return json.loads(completion.choices[0].message.content)

    def route_request(self, system: str, user: str, tier: str = "cost_optimized") -> Dict[str, Any]:
        if tier == "high_precision":
            # Tier 1: Lead Linguist
            return self.call_groq(system, user, model="llama-3.3-70b-versatile")
        elif tier == "standard":
            # Tier 2: Technical Editor
            return self.call_groq(system, user, model="meta-llama/llama-4-scout-17b-16e-instruct")
        else:
            # Tier 3: Rapid Validator
            return self.call_groq(system, user, model="llama-3.1-8b-instant")

unified_llm = UnifiedLLMService()

import os
import json
import httpx
from typing import Dict, Any, Optional
from groq import Groq
from app.core.config import settings
from app.services.quota import quota_service
from app.services.openrouter_guard import openrouter_guard

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

    def call_openrouter_free(self, system: str, user: str, model: str = "meta-llama/llama-3-8b-instruct:free") -> Dict[str, Any]:
        if self.openrouter_key == "stub":
            return {"score": 8, "feedback": "OpenRouter Stub"}

        # Security: Force check that model is still free
        if not openrouter_guard.ensure_model_is_free(model):
            # Fallback: Get current top free model
            available_free = openrouter_guard.fetch_free_models()
            if not available_free:
                return {"error": "CRITICAL: No free models available on OpenRouter."}
            model = available_free[0]

        # Direct HTTP call for OpenRouter to keep it lightweight
        try:
            with httpx.Client() as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user}
                        ]
                    },
                    timeout=30.0
                )
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    import re
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match: return json.loads(match.group())
                    return {"translated_text": content} # Return raw if not JSON
        except Exception as e:
            return {"error": str(e)}

    def route_request(self, system: str, user: str, tier: str = "cost_optimized") -> Dict[str, Any]:
        if tier == "high_precision":
            return self.call_groq(system, user, model="llama-3.3-70b-versatile")
        elif tier == "standard":
            return self.call_groq(system, user, model="meta-llama/llama-4-scout-17b-16e-instruct")
        else:
            # Use OpenRouter for cost-optimized
            return self.call_openrouter_free(system, user)

unified_llm = UnifiedLLMService()

import os
import json
import httpx
from typing import Dict, Any, Optional
from groq import Groq
from app.core.config import settings

class UnifiedLLMService:
    """
    Hybrid Router for LLM tasks.
    Routes between Groq (High Quality) and OpenRouter (Free/Low Cost).
    """
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY != "stub" else None
        self.openrouter_key = settings.OPENROUTER_API_KEY

    def call_groq(self, system: str, user: str, model: str = "llama3-70b-8192") -> Dict[str, Any]:
        if not self.groq_client:
            return {"score": 9, "feedback": "Groq Stub"}

        completion = self.groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    def call_openrouter_free(self, system: str, user: str, model: str = "meta-llama/llama-3-8b-instruct:free") -> Dict[str, Any]:
        if self.openrouter_key == "stub":
            return {"score": 8, "feedback": "OpenRouter Stub"}

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
                # OpenRouter doesn't strictly support response_format in all free models
                # so we might need to parse the content string.
                content = data["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback parser if LLM returns text + JSON
                    import re
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match: return json.loads(match.group())
                    return {"error": "JSON parse failed", "content": content}
        except Exception as e:
            return {"error": str(e)}

    def route_request(self, system: str, user: str, tier: str = "cost_optimized") -> Dict[str, Any]:
        if tier == "high_precision":
            return self.call_groq(system, user)
        else:
            return self.call_openrouter_free(system, user)

unified_llm = UnifiedLLMService()

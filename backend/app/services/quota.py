import time
from typing import Dict, Any, Optional
from app.services.redis_state import redis_state

class QuotaService:
    """
    Manages API limits (RPM, RPD, TPM, TPD) using Redis.
    Ensures the firm stays within free-tier boundaries.
    """
    def __init__(self):
        # Specific limits from provided inventory
        self.limits = {
            "llama-3.3-70b-versatile": {"rpm": 30, "rpd": 1000, "tpm": 12000, "tpd": 100000},
            "meta-llama/llama-4-scout-17b-16e-instruct": {"rpm": 30, "rpd": 1000, "tpm": 30000, "tpd": 500000},
            "llama-3.1-8b-instant": {"rpm": 30, "rpd": 14400, "tpm": 6000, "tpd": 500000},
            "whisper-large-v3-turbo": {"rph_sec": 7200, "rpd_sec": 28800}
        }

    def check_quota(self, model: str, tokens: int = 0) -> bool:
        """
        Verifies if model is within RPD and TPD limits.
        """
        if model not in self.limits: return True

        limit = self.limits[model]
        day_key = f"quota:day:{model}:{time.strftime('%Y-%m-%d')}"

        stats = redis_state.client.hgetall(day_key)
        requests = int(stats.get(b"requests", 0))
        total_tokens = int(stats.get(b"tokens", 0))

        if requests >= limit.get("rpd", 999999): return False
        if total_tokens + tokens >= limit.get("tpd", 999999): return False

        return True

    def check_stt_quota(self, duration_sec: float) -> bool:
        """
        Checks if current STT usage is within hourly/daily limits.
        """
        hour_key = f"quota:stt:hour:{time.strftime('%Y-%m-%d-%H')}"
        day_key = f"quota:stt:day:{time.strftime('%Y-%m-%d')}"

        hour_usage = int(redis_state.client.get(hour_key) or 0)
        day_usage = int(redis_state.client.get(day_key) or 0)

        limit = self.limits["whisper-large-v3-turbo"]
        if hour_usage + duration_sec > limit["rph_sec"]: return False
        if day_usage + duration_sec > limit["rpd_sec"]: return False

        return True

    def increment_stt_quota(self, duration_sec: float):
        hour_key = f"quota:stt:hour:{time.strftime('%Y-%m-%d-%H')}"
        day_key = f"quota:stt:day:{time.strftime('%Y-%m-%d')}"

        redis_state.client.incrby(hour_key, int(duration_sec))
        redis_state.client.incrby(day_key, int(duration_sec))
        redis_state.client.expire(hour_key, 7200)
        redis_state.client.expire(day_key, 172800)

    def increment_quota(self, model: str, tokens: int):
        day_key = f"quota:day:{model}:{time.strftime('%Y-%m-%d')}"
        redis_state.client.hincrby(day_key, "requests", 1)
        redis_state.client.hincrby(day_key, "tokens", tokens)
        redis_state.client.expire(day_key, 172800) # 48h retention

quota_service = QuotaService()

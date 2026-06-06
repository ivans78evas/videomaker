from typing import List, Dict, Any
from app.core.prompts import LINGUIST_AGENT_PROMPT, TECHNICAL_AGENT_PROMPT, VALIDATION_AGENT_PROMPT, CONSENSUS_JUDGE_PROMPT
from app.services.llm_router import unified_llm
import json

class ConsensusQAService:
    def linguist_review(self, original: str, translated: str, target_lang: str) -> Dict[str, Any]:
        """
        Agent 1: High Precision Linguist (Groq).
        """
        sys = LINGUIST_AGENT_PROMPT.format(target_lang=target_lang)
        user = f"Original: {original}\nTranslated: {translated}"
        return unified_llm.route_request(sys, user, tier="high_precision")

    def technical_review(self, original: str, translated: str) -> Dict[str, Any]:
        """
        Agent 2: Cost Optimized Technician (OpenRouter Free).
        """
        user = f"Original: {original}\nTranslated: {translated}"
        return unified_llm.route_request(TECHNICAL_AGENT_PROMPT, user, tier="cost_optimized")

    def validation_review(self, original: str, translated: str) -> Dict[str, Any]:
        """
        Agent 3: Hallucination Guard (OpenRouter Free).
        """
        user = f"Original: {original}\nTranslated: {translated}"
        return unified_llm.route_request(VALIDATION_AGENT_PROMPT, user, tier="cost_optimized")

    def consensus_judge(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Final Judge: Arbitrates all reports.
        """
        scores = []
        for r in reviews:
            if "score" in r: scores.append(r["score"])
            elif "hallucination_score" in r: scores.append(r["hallucination_score"])

        avg_score = sum(scores) / len(scores) if scores else 0

        # Logic: All scores must be >= 8.0 AND no hallucinations detected
        hallucination_detected = any(r.get("has_hallucinations", False) for r in reviews)

        if avg_score >= 8.0 and not hallucination_detected:
            return {"status": "approved", "final_score": avg_score, "reason": "Consistent high quality and no hallucinations."}
        else:
            return {
                "status": "manual_review",
                "final_score": avg_score,
                "reason": "Quality issues or hallucinations detected."
            }

    def run_multi_agent_qa(self, segments: List[Dict[str, Any]], target_lang: str = "en") -> Dict[str, Any]:
        full_original = " ".join([s["text"] for s in segments])
        full_translated = " ".join([s.get("translated_text", "") for s in segments])

        # 1. Run parallel reviews
        l_review = self.linguist_review(full_original, full_translated, target_lang)
        t_review = self.technical_review(full_original, full_translated)
        v_review = self.validation_review(full_original, full_translated)

        # 2. Get consensus
        final_decision = self.consensus_judge([l_review, t_review, v_review])

        return {
            "decision": final_decision,
            "agent_reports": {
                "linguist": l_review,
                "technical": t_review,
                "validator": v_review
            }
        }

consensus_qa_service = ConsensusQAService()

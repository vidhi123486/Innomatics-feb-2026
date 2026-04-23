from __future__ import annotations

from .router import RouteDecision


class HitlEscalation:
    def __init__(self, min_confidence: float = 0.55) -> None:
        self.min_confidence = min_confidence

    def should_escalate(
        self,
        route: RouteDecision,
        retrieval_confidence: float,
        hit_count: int,
        question: str,
    ) -> tuple[bool, str | None]:
        if route.route == "escalate":
            return True, "Sensitive customer issue requires human support review"
        if route.route == "needs_clarification":
            return True, "Question is too vague and needs clarification"
        if retrieval_confidence < self.min_confidence:
            return True, "Low retrieval confidence"
        if hit_count == 0:
            return True, "No relevant chunks found"
        if len(question.split()) > 45:
            return True, "Complex customer issue requires human review"
        return False, None

from __future__ import annotations
from .retriever import RetrievalHit


class OfflineAnswerGenerator:
    def generate(self, question: str, hits: list[RetrievalHit]) -> str:
        if not hits:
            return (
                "I could not find enough relevant support knowledge to answer this clearly. "
                "Please escalate this question to a human support agent."
            )

        best_text = hits[0].text.strip()
        answer = self._extract_direct_answer(question, best_text) or best_text
        return answer

    def _extract_direct_answer(self, question: str, text: str) -> str | None:
        pairs = []
        parts = text.split("Q:")
        for part in parts:
            if "A:" not in part:
                continue
            q_text, a_text = part.split("A:", 1)
            answer = a_text.split("Q:", 1)[0].strip()
            pairs.append((q_text.strip().lower(), answer))

        if not pairs:
            return None

        question_terms = {
            token for token in question.lower().replace("?", "").split()
            if token not in {"how", "can", "i", "my", "the", "a", "an", "do", "what", "is"}
        }
        best_answer = None
        best_score = 0
        for q_text, answer in pairs:
            score = sum(1 for term in question_terms if term in q_text)
            if score > best_score:
                best_score = score
                best_answer = answer
        return best_answer


class OpenAIAnswerGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, hits: list[RetrievalHit]) -> str:
        context = "\n\n".join(
            f"Source {index + 1} ({hit.metadata.get('file_name')}, page {hit.metadata.get('page_number')}):\n{hit.text}"
            for index, hit in enumerate(hits)
        )
        prompt = f"""
You are a customer support assistant for a RAG-based helpdesk system.
Answer only from the given context. If the context is insufficient, say so.

Question:
{question}

Context:
{context}
""".strip()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.2,
        )
        return response.output_text

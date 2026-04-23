from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .hitl import HitlEscalation
from .llm import OfflineAnswerGenerator
from .retriever import ChromaRetriever, RetrievalHit
from .router import QueryRouter, RouteDecision


class WorkflowState(TypedDict, total=False):
    question: str
    route: RouteDecision
    hits: list[RetrievalHit]
    confidence: float
    answer: str
    requires_human: bool
    escalation_reason: str
    sources: list[dict]


class CustomerSupportWorkflow:
    def __init__(
        self,
        router: QueryRouter,
        retriever: ChromaRetriever,
        answer_generator: OfflineAnswerGenerator,
        hitl: HitlEscalation,
        top_k: int,
    ) -> None:
        self.router = router
        self.retriever = retriever
        self.answer_generator = answer_generator
        self.hitl = hitl
        self.top_k = top_k
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("process", self._process)
        graph.add_node("human_review", self._human_review)
        graph.add_node("output", self._output)

        graph.add_edge(START, "process")
        graph.add_conditional_edges(
            "process",
            self._next_step,
            {
                "human_review": "human_review",
                "output": "output",
            },
        )
        graph.add_edge("human_review", "output")
        graph.add_edge("output", END)
        return graph.compile()

    def _process(self, state: WorkflowState) -> WorkflowState:
        question = state["question"]
        route = self.router.decide(question)
        hits, confidence = self.retriever.search(question, self.top_k)
        requires_human, reason = self.hitl.should_escalate(route, confidence, len(hits), question)

        return {
            "question": question,
            "route": route,
            "hits": hits,
            "confidence": confidence,
            "requires_human": requires_human,
            "escalation_reason": reason or "",
        }

    def _next_step(self, state: WorkflowState) -> str:
        return "human_review" if state.get("requires_human") else "output"

    def _human_review(self, state: WorkflowState) -> WorkflowState:
        return {
            **state,
            "answer": f"Escalated to human reviewer. Reason: {state.get('escalation_reason', 'Manual review required')}.",
        }

    def _output(self, state: WorkflowState) -> WorkflowState:
        if state.get("requires_human"):
            answer = state["answer"]
        else:
            answer = self.answer_generator.generate(state["question"], state.get("hits", []))

        sources = [
            {
                "file_name": hit.metadata.get("file_name"),
                "page_number": hit.metadata.get("page_number"),
                "chunk_id": hit.chunk_id,
            }
            for hit in state.get("hits", [])
        ]

        return {
            **state,
            "answer": answer,
            "sources": sources,
        }

    def run(self, question: str) -> WorkflowState:
        return self.graph.invoke({"question": question})

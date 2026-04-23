from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .chunker import TextChunker
from .embeddings import LocalEmbeddingModel
from .hitl import HitlEscalation
from .llm import OfflineAnswerGenerator, OpenAIAnswerGenerator
from .loader import PDFLoader
from .retriever import ChromaRetriever
from .router import QueryRouter
from .workflow import CustomerSupportWorkflow


@dataclass(slots=True)
class AppConfig:
    data_dir: Path
    chroma_dir: Path
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    min_confidence: float
    openai_api_key: str | None
    openai_model: str


class RAGPipeline:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.config = self._load_config(project_root)
        self.loader = PDFLoader()
        self.chunker = TextChunker(self.config.chunk_size, self.config.chunk_overlap)
        self.embedding_model = LocalEmbeddingModel()
        self.retriever = ChromaRetriever(
            db_path=self.config.chroma_dir,
            collection_name=self.config.collection_name,
            embedding_model=self.embedding_model,
        )
        if self.config.openai_api_key:
            self.answer_generator = OpenAIAnswerGenerator(self.config.openai_api_key, self.config.openai_model)
        else:
            self.answer_generator = OfflineAnswerGenerator()
        self.workflow = CustomerSupportWorkflow(
            router=QueryRouter(),
            retriever=self.retriever,
            answer_generator=self.answer_generator,
            hitl=HitlEscalation(self.config.min_confidence),
            top_k=self.config.top_k,
        )

    def _load_config(self, root: Path) -> AppConfig:
        return AppConfig(
            data_dir=root / os.getenv("DATA_DIR", "data"),
            chroma_dir=root / os.getenv("CHROMA_DIR", "chroma_db"),
            collection_name=os.getenv("COLLECTION_NAME", "customer_support_kb"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "900")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
            top_k=int(os.getenv("TOP_K", "4")),
            min_confidence=float(os.getenv("MIN_CONFIDENCE", "0.55")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )

    def ingest(self) -> dict:
        pages = self.loader.load(self.config.data_dir)
        chunks = self.chunker.split_pages(pages)
        indexed = self.retriever.index(chunks)
        return {
            "pdf_pages_loaded": len(pages),
            "chunks_created": len(chunks),
            "chunks_indexed": indexed,
            "collection_name": self.config.collection_name,
        }

    def ask(self, question: str) -> dict:
        state = self.workflow.run(question)
        route = state["route"]
        return {
            "question": question,
            "route": route.route,
            "route_reason": route.reason,
            "route_confidence": route.confidence,
            "retrieval_confidence": state.get("confidence", 0.0),
            "requires_human": state.get("requires_human", False),
            "escalation_reason": state.get("escalation_reason", ""),
            "answer": state["answer"],
            "sources": state.get("sources", []),
        }

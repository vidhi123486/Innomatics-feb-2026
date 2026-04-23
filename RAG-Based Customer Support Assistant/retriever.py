from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import chromadb

from .chunker import Chunk
from .embeddings import LocalEmbeddingModel


@dataclass(slots=True)
class RetrievalHit:
    chunk_id: str
    text: str
    metadata: dict
    distance: float


class ChromaRetriever:
    def __init__(self, db_path: Path, collection_name: str, embedding_model: LocalEmbeddingModel) -> None:
        db_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedding_model = embedding_model

    def index(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=self.embedding_model.embed_many([chunk.text for chunk in chunks]),
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 4) -> tuple[list[RetrievalHit], float]:
        response = self.collection.query(
            query_embeddings=[self.embedding_model.embed(query)],
            n_results=top_k,
        )

        ids = response.get("ids", [[]])[0]
        docs = response.get("documents", [[]])[0]
        metas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        hits: list[RetrievalHit] = []
        for chunk_id, text, metadata, distance in zip(ids, docs, metas, distances):
            hits.append(
                RetrievalHit(
                    chunk_id=chunk_id,
                    text=text,
                    metadata=metadata or {},
                    distance=float(distance),
                )
            )

        if not hits:
            return [], 0.0

        vector_confidence = max(0.0, min(1.0, 1.0 / (1.0 + max(0.0, hits[0].distance))))
        keyword_confidence = max((self._keyword_overlap(query, hit.text) for hit in hits), default=0.0)
        confidence = max(vector_confidence, keyword_confidence)
        return hits, confidence

    def _keyword_overlap(self, query: str, document: str) -> float:
        stopwords = {
            "a", "an", "and", "are", "can", "do", "for", "how", "i", "in", "is",
            "it", "my", "of", "on", "or", "the", "to", "what", "when", "where",
            "why", "you", "your",
        }
        query_tokens = {
            token for token in re.findall(r"[a-z0-9]+", query.lower()) if token not in stopwords
        }
        if not query_tokens:
            return 0.0
        document_tokens = set(re.findall(r"[a-z0-9]+", document.lower()))
        return len(query_tokens & document_tokens) / len(query_tokens)

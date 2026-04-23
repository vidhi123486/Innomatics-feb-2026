from __future__ import annotations

import hashlib
import math


class LocalEmbeddingModel:
    """Deterministic local embeddings for reliable offline evaluation."""

    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        values = [0.0] * self.dimensions
        tokens = [token.lower() for token in text.split() if token.strip()]

        if not tokens:
            return values

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for index in range(self.dimensions):
                values[index] += (digest[index % len(digest)] / 255.0) - 0.5

        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


from __future__ import annotations

from dataclasses import dataclass

from .loader import DocumentPage


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    source_id: str
    text: str
    metadata: dict


class TextChunker:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 150) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_pages(self, pages: list[DocumentPage]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page in pages:
            chunks.extend(self._split_page(page))
        return chunks

    def _split_page(self, page: DocumentPage) -> list[Chunk]:
        chunks: list[Chunk] = []
        text = page.text.strip()
        start = 0
        chunk_index = 1

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start:
                    end = boundary

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"{page.source_id}_c{chunk_index}",
                        source_id=page.source_id,
                        text=chunk_text,
                        metadata={
                            "file_name": page.file_name,
                            "file_path": page.file_path,
                            "page_number": page.page_number,
                            "chunk_index": chunk_index,
                        },
                    )
                )
                chunk_index += 1

            if end >= len(text):
                break
            start = max(end - self.chunk_overlap, start + 1)

        return chunks

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(slots=True)
class DocumentPage:
    source_id: str
    file_name: str
    file_path: str
    page_number: int
    text: str


class PDFLoader:
    def load(self, data_dir: Path) -> list[DocumentPage]:
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        pages: list[DocumentPage] = []
        pdf_files = sorted(data_dir.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {data_dir}")

        for pdf_path in pdf_files:
            reader = PdfReader(str(pdf_path))
            for page_index, page in enumerate(reader.pages, start=1):
                text = " ".join((page.extract_text() or "").split())
                if not text:
                    continue
                pages.append(
                    DocumentPage(
                        source_id=f"{pdf_path.stem}_p{page_index}",
                        file_name=pdf_path.name,
                        file_path=str(pdf_path),
                        page_number=page_index,
                        text=text,
                    )
                )
        return pages


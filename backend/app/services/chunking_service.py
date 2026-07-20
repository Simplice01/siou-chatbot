import hashlib

from app.models.document import DocumentChunk, PageText


class ChunkingService:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = min(chunk_overlap, chunk_size // 2)

    def chunk_pages(self, document_id: str, document_name: str, pages: list[PageText]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in pages:
            text = page.text.strip()
            if not text:
                continue
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                if end < len(text):
                    boundary = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
                    if boundary > start + self.chunk_size * 0.55:
                        end = boundary + 1
                chunk_text = text[start:end].strip()
                if chunk_text:
                    raw_id = f"{document_id}:{page.page}:{start}:{hashlib.sha1(chunk_text.encode('utf-8')).hexdigest()[:10]}"
                    chunks.append(
                        DocumentChunk(
                            id=raw_id,
                            document_id=document_id,
                            document_name=document_name,
                            page_start=page.page,
                            page_end=page.page,
                            text=chunk_text,
                            char_count=len(chunk_text),
                        )
                    )
                if end >= len(text):
                    break
                start = max(0, end - self.chunk_overlap)
        return chunks


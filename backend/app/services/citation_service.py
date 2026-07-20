from app.models.document import DocumentChunk
from app.schemas.chat import Source


class CitationService:
    def build_sources(self, results: list[tuple[DocumentChunk, float]]) -> list[Source]:
        sources: list[Source] = []
        for chunk, score in results:
            citation = self.extract_citation(chunk.text)
            sources.append(
                Source(
                    document=chunk.document_name,
                    page=chunk.page_start,
                    chunk_id=chunk.id,
                    score=max(0.0, min(1.0, (score + 1) / 2)),
                    citation=citation,
                )
            )
        return sources

    def extract_citation(self, text: str, max_chars: int = 320) -> str:
        compact = " ".join(text.split())
        if len(compact) <= max_chars:
            return compact
        return compact[: max_chars - 1].rstrip() + "..."


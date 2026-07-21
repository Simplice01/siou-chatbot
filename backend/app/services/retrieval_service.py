from collections.abc import Callable

from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStoreService,
        top_k: int,
        allowed_document_ids: Callable[[], set[str]] | None = None,
    ) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.top_k = top_k
        self.allowed_document_ids = allowed_document_ids

    async def retrieve(self, document_id: str, question: str) -> list[tuple[object, float]]:
        if self.allowed_document_ids and document_id not in self.allowed_document_ids():
            raise FileNotFoundError(f"Document introuvable: {document_id}")
        query = await self.embeddings.embed_texts([question])
        return self.vector_store.search(document_id, query, self.top_k)

    async def retrieve_any(self, question: str) -> list[tuple[object, float]]:
        query = await self.embeddings.embed_texts([question])
        results = []
        allowed = self.allowed_document_ids() if self.allowed_document_ids else None
        for document_id in self.vector_store.list_document_ids():
            if allowed is not None and document_id not in allowed:
                continue
            results.extend(self.vector_store.search(document_id, query, self.top_k))
        return sorted(results, key=lambda item: item[1], reverse=True)[: self.top_k]

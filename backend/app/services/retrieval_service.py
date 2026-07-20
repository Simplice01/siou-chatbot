from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


class RetrievalService:
    def __init__(self, embeddings: EmbeddingService, vector_store: VectorStoreService, top_k: int) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.top_k = top_k

    async def retrieve(self, document_id: str, question: str) -> list[tuple[object, float]]:
        query = await self.embeddings.embed_texts([question])
        return self.vector_store.search(document_id, query, self.top_k)

    async def retrieve_any(self, question: str) -> list[tuple[object, float]]:
        query = await self.embeddings.embed_texts([question])
        results = []
        for document_id in self.vector_store.list_document_ids():
            results.extend(self.vector_store.search(document_id, query, self.top_k))
        return sorted(results, key=lambda item: item[1], reverse=True)[: self.top_k]

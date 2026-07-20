from functools import lru_cache

from app.core.config import get_settings
from app.services.chunking_service import ChunkingService
from app.services.citation_service import CitationService
from app.services.document_loader import DocumentLoader
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.services.llm_service import LLMService
from app.services.pdf_parser import PdfParser
from app.services.prompt_service import PromptService
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService
from app.services.vector_store_service import VectorStoreService


@lru_cache
def get_vector_store() -> VectorStoreService:
    return VectorStoreService(get_settings().vector_store_dir)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_settings())


def get_document_loader() -> DocumentLoader:
    return DocumentLoader(get_settings(), get_vector_store())


def get_indexing_service() -> IndexingService:
    settings = get_settings()
    return IndexingService(
        settings,
        PdfParser(),
        ChunkingService(settings.chunk_size, settings.chunk_overlap),
        get_embedding_service(),
        get_vector_store(),
    )


def get_rag_service() -> RagService:
    settings = get_settings()
    retrieval = RetrievalService(get_embedding_service(), get_vector_store(), settings.top_k)
    return RagService(settings, retrieval, PromptService(), LLMService(settings), CitationService())


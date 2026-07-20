from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.services.pdf_parser import PdfParser
from app.services.retrieval_service import RetrievalService
from app.services.vector_store_service import VectorStoreService
from app.utils.files import safe_document_id


@pytest.mark.asyncio
async def test_indexing_skips_unchanged_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    settings = Settings(
        documents_dir=tmp_path,
        vector_store_dir=tmp_path / "vectors",
        embedding_provider="hash",
        chunk_size=500,
        chunk_overlap=50,
        llm_provider="ollama",
    )
    store = VectorStoreService(settings.vector_store_dir)
    indexer = IndexingService(settings, PdfParser(), ChunkingService(500, 50), EmbeddingService(settings), store)

    first = await indexer.index_pdf(sample_pdf)
    second = await indexer.index_pdf(sample_pdf)

    assert first["status"] == "indexed"
    assert second["status"] == "skipped"
    assert store.exists(safe_document_id(sample_pdf))


@pytest.mark.asyncio
async def test_retrieval_is_scoped_to_document(sample_pdf: Path, tmp_path: Path) -> None:
    settings = Settings(
        documents_dir=tmp_path,
        vector_store_dir=tmp_path / "vectors",
        embedding_provider="hash",
        chunk_size=500,
        chunk_overlap=50,
        top_k=2,
        llm_provider="ollama",
    )
    store = VectorStoreService(settings.vector_store_dir)
    embeddings = EmbeddingService(settings)
    indexer = IndexingService(settings, PdfParser(), ChunkingService(500, 50), embeddings, store)
    await indexer.index_pdf(sample_pdf)

    results = await RetrievalService(embeddings, store, top_k=2).retrieve(safe_document_id(sample_pdf), "montant contrat")

    assert results
    assert any("1200 euros" in chunk.text for chunk, _ in results)


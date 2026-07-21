import logging
from pathlib import Path

from app.core.config import Settings
from app.services.chunking_service import ChunkingService
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService
from app.services.pdf_parser import PdfParser
from app.services.vector_store_service import VectorStoreService
from app.utils.files import file_sha256, is_supported_document, safe_document_id

logger = logging.getLogger(__name__)


class IndexingService:
    def __init__(
        self,
        settings: Settings,
        parser: PdfParser,
        chunker: ChunkingService,
        embeddings: EmbeddingService,
        vector_store: VectorStoreService,
        database: DatabaseService | None = None,
    ) -> None:
        self.settings = settings
        self.parser = parser
        self.chunker = chunker
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.database = database

    async def index_all(self) -> list[dict[str, object]]:
        reports = []
        paths = sorted({path for pattern in self.settings.document_patterns for path in self.settings.documents_dir.glob(pattern)})
        for path in paths:
            if is_supported_document(path):
                try:
                    reports.append(await self.index_pdf(path))
                except RuntimeError as exc:
                    logger.warning("Indexation impossible pour %s: %s", path.name, exc)
                    reports.append({"document": path.name, "status": "ocr_unavailable", "error": str(exc)})
        return reports

    async def index_pdf(self, path: Path) -> dict[str, object]:
        document_id = safe_document_id(path)
        digest = file_sha256(path)
        stat = path.stat()
        current = self.vector_store.read_metadata(document_id)
        if current and current.get("sha256") == digest and current.get("modified_at") == stat.st_mtime:
            if self.database:
                try:
                    pages = self.parser.parse(path)
                    chunks = self.vector_store.load_chunks(document_id)
                    self.database.sync_indexed_document(path.name, digest, stat.st_size, pages, chunks)
                except Exception:
                    logger.exception("Synchronisation PostgreSQL impossible pour %s", path.name)
            return {"document": path.name, "document_id": document_id, "status": "skipped"}
        pages = self.parser.parse(path)
        chunks = self.chunker.chunk_pages(document_id, path.name, pages)
        if not chunks:
            return {"document": path.name, "document_id": document_id, "status": "empty"}
        vectors = await self.embeddings.embed_texts([chunk.text for chunk in chunks])
        metadata = {
            "document_id": document_id,
            "name": path.name,
            "sha256": digest,
            "modified_at": stat.st_mtime,
            "size_bytes": stat.st_size,
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "active": True,
        }
        self.vector_store.save(document_id, vectors, chunks, metadata)
        if self.database:
            try:
                self.database.sync_indexed_document(path.name, digest, stat.st_size, pages, chunks)
            except Exception:
                logger.exception("Synchronisation PostgreSQL impossible pour %s", path.name)
        logger.info("Indexed %s with %s chunks", path.name, len(chunks))
        return {"document": path.name, "document_id": document_id, "status": "indexed", "chunks": len(chunks)}

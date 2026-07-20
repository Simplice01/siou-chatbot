from pathlib import Path

from app.core.config import Settings
from app.schemas.document import DocumentSummary
from app.services.vector_store_service import VectorStoreService
from app.utils.files import is_pdf, safe_document_id


class DocumentLoader:
    def __init__(self, settings: Settings, vector_store: VectorStoreService) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def list_documents(self) -> list[DocumentSummary]:
        docs: list[DocumentSummary] = []
        paths = sorted({path for pattern in self.settings.document_patterns for path in self.settings.documents_dir.glob(pattern)})
        for path in paths:
            if not is_pdf(path):
                continue
            stat = path.stat()
            doc_id = safe_document_id(path)
            metadata = self.vector_store.read_metadata(doc_id)
            docs.append(
                DocumentSummary(
                    id=doc_id,
                    name=path.name,
                    size_bytes=stat.st_size,
                    modified_at=stat.st_mtime,
                    indexed=metadata is not None,
                    page_count=metadata.get("page_count") if metadata else None,
                    chunk_count=metadata.get("chunk_count") if metadata else None,
                )
            )
        return docs

    def resolve_pdf(self, document: str) -> Path:
        paths = sorted({path for pattern in self.settings.document_patterns for path in self.settings.documents_dir.glob(pattern)})
        for path in paths:
            if path.name == document or safe_document_id(path) == document:
                return path
        raise FileNotFoundError(f"Document introuvable: {document}")

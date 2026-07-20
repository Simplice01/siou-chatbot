from app.models.document import PageText
from app.services.chunking_service import ChunkingService


def test_chunking_keeps_page_metadata() -> None:
    service = ChunkingService(chunk_size=40, chunk_overlap=8)
    chunks = service.chunk_pages("doc-1", "doc.pdf", [PageText(page=3, text="Alpha beta. Gamma delta. " * 5)])
    assert chunks
    assert all(chunk.page_start == 3 for chunk in chunks)
    assert all(chunk.document_id == "doc-1" for chunk in chunks)


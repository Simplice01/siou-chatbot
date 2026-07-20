from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import get_document_loader, get_indexing_service, get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import DocumentSummary
from app.services.document_loader import DocumentLoader
from app.services.indexing_service import IndexingService
from app.services.rag_service import RagService

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/documents", response_model=list[DocumentSummary])
def list_documents(loader: DocumentLoader = Depends(get_document_loader)) -> list[DocumentSummary]:
    return loader.list_documents()


@router.get("/documents/{document_id}/file")
def get_document_file(document_id: str, loader: DocumentLoader = Depends(get_document_loader)) -> FileResponse:
    try:
        path = loader.resolve_pdf(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.post("/index")
async def index_documents(indexer: IndexingService = Depends(get_indexing_service)) -> list[dict[str, object]]:
    return await indexer.index_all()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, rag: RagService = Depends(get_rag_service)) -> ChatResponse:
    try:
        return await rag.chat(payload.document, payload.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

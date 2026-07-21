from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.api.deps import get_database_service, get_document_loader, get_indexing_service, get_rag_service
from app.core.database import DatabaseUnavailableError
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.database import (
    ConversationCreate,
    ConversationOut,
    DocumentChunkOut,
    DocumentDbOut,
    FeedbackCreate,
    FeedbackOut,
    MessageOut,
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
    ServiceCardOut,
    SourceFileOut,
    StatsOut,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.schemas.document import DocumentSummary
from app.services.database_service import DatabaseService
from app.services.document_loader import DocumentLoader
from app.services.indexing_service import IndexingService
from app.services.rag_service import RagService

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _db_error(exc: Exception) -> HTTPException:
    if isinstance(exc, DatabaseUnavailableError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur base de donnees.")


@router.get("/documents", response_model=list[DocumentSummary])
def list_documents(loader: DocumentLoader = Depends(get_document_loader)) -> list[DocumentSummary]:
    return loader.list_documents()


@router.get("/db/documents", response_model=list[DocumentDbOut])
def list_database_documents(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("documents")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/db/documents/{document_id}", response_model=DocumentDbOut)
def get_database_document(document_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        document = db.get_row("documents", document_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    return document


@router.get("/db/documents/{document_id}/chunks", response_model=list[DocumentChunkOut])
def list_database_document_chunks(document_id: UUID, db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_document_chunks(document_id)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/source-files", response_model=list[SourceFileOut])
def list_source_files(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("source_files")
    except Exception as exc:
        raise _db_error(exc) from exc


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


@router.post("/documents/reindex")
async def reindex_documents(indexer: IndexingService = Depends(get_indexing_service)) -> list[dict[str, object]]:
    return await indexer.index_all()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    rag: RagService = Depends(get_rag_service),
    db: DatabaseService = Depends(get_database_service),
) -> ChatResponse:
    try:
        response = await rag.chat(payload.document, payload.question)
        try:
            conversation_id, message_id = db.save_chat_exchange(
                payload.question,
                response,
                conversation_id=payload.conversation_id,
                user_id=payload.user_id,
            )
            response.conversation_id = conversation_id
            response.message_id = message_id
        except DatabaseUnavailableError:
            pass
        return response
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("conversations")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(payload: ConversationCreate, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        return db.create_conversation(payload)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        conversation = db.get_row("conversations", conversation_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_conversation_messages(conversation_id: UUID, db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_messages(conversation_id)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: UUID, db: DatabaseService = Depends(get_database_service)) -> None:
    try:
        deleted = db.delete_conversation(conversation_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")


@router.get("/users", response_model=list[UserOut])
def list_users(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("users")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        return db.create_user(payload)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        user = db.get_row("users", user_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: UUID, payload: UserUpdate, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        user = db.update_user(user_id, payload)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user


@router.delete("/users/{user_id}", response_model=UserOut)
def deactivate_user(user_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        user = db.deactivate_user(user_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return user


@router.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("organizations")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.post("/organizations", response_model=OrganizationOut, status_code=201)
def create_organization(payload: OrganizationCreate, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        return db.create_organization(payload)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/organizations/{organization_id}", response_model=OrganizationOut)
def get_organization(organization_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        organization = db.get_row("organizations", organization_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not organization:
        raise HTTPException(status_code=404, detail="Organisation introuvable.")
    return organization


@router.patch("/organizations/{organization_id}", response_model=OrganizationOut)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: DatabaseService = Depends(get_database_service),
) -> dict:
    try:
        organization = db.update_organization(organization_id, payload)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not organization:
        raise HTTPException(status_code=404, detail="Organisation introuvable.")
    return organization


@router.get("/service-cards", response_model=list[ServiceCardOut])
def list_service_cards(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("service_cards")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/service-cards/{service_card_id}", response_model=ServiceCardOut)
def get_service_card(service_card_id: UUID, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        card = db.get_row("service_cards", service_card_id)
    except Exception as exc:
        raise _db_error(exc) from exc
    if not card:
        raise HTTPException(status_code=404, detail="Fiche service introuvable.")
    return card


@router.post("/feedback", response_model=FeedbackOut, status_code=201)
def create_feedback(payload: FeedbackCreate, db: DatabaseService = Depends(get_database_service)) -> dict:
    try:
        return db.create_feedback(payload)
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/feedback", response_model=list[FeedbackOut])
def list_feedback(db: DatabaseService = Depends(get_database_service)) -> list[dict]:
    try:
        return db.list_rows("feedback_reports")
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/admin/stats", response_model=StatsOut)
def admin_stats(db: DatabaseService = Depends(get_database_service)) -> dict[str, int]:
    try:
        return db.stats()
    except Exception as exc:
        raise _db_error(exc) from exc


@router.get("/admin/index-status")
def index_status(loader: DocumentLoader = Depends(get_document_loader)) -> list[DocumentSummary]:
    return loader.list_documents()

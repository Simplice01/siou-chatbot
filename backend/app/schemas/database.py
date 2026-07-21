from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str | None = None
    full_name: str | None = Field(default=None, max_length=255)
    role: str = "usager_anonyme"
    organization_id: UUID | None = None


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = Field(default=None, max_length=255)
    role: str | None = None
    organization_id: UUID | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: UUID
    organization_id: UUID | None = None
    email: str | None = None
    full_name: str | None = None
    role: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ConversationCreate(BaseModel):
    user_id: UUID | None = None
    title: str | None = Field(default=None, max_length=255)
    channel: str = "web"


class ConversationOut(BaseModel):
    id: UUID
    user_id: UUID | None = None
    channel: str
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    confidence_score: float | None = None
    created_at: datetime


class DocumentDbOut(BaseModel):
    id: UUID
    source_file_id: UUID | None = None
    organization_id: UUID | None = None
    title: str
    type: str
    status: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentChunkOut(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    page_start: int | None = None
    page_end: int | None = None
    content: str
    char_count: int | None = None


class SourceFileOut(BaseModel):
    id: UUID
    organization_id: UUID | None = None
    kind: str
    original_filename: str
    mime_type: str | None = None
    file_size_bytes: int | None = None
    page_count: int | None = None
    collected_at: datetime


class OrganizationCreate(BaseModel):
    name: str
    acronym: str | None = None
    type: str = "service"
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    acronym: str | None = None
    type: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    is_active: bool | None = None


class OrganizationOut(BaseModel):
    id: UUID
    parent_id: UUID | None = None
    name: str
    acronym: str | None = None
    type: str
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ServiceCardOut(BaseModel):
    id: UUID
    organization_id: UUID
    source_document_id: UUID | None = None
    title: str
    public_name: str | None = None
    target_users: str | None = None
    orientation_summary: str
    procedure_summary: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class FeedbackCreate(BaseModel):
    description: str = Field(min_length=3, max_length=4000)
    expected_answer: str | None = Field(default=None, max_length=4000)
    message_id: UUID | None = None
    conversation_id: UUID | None = None
    reporter_user_id: UUID | None = None
    organization_id: UUID | None = None


class FeedbackOut(BaseModel):
    id: UUID
    message_id: UUID | None = None
    conversation_id: UUID | None = None
    reporter_user_id: UUID | None = None
    organization_id: UUID | None = None
    description: str
    expected_answer: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class StatsOut(BaseModel):
    users: int
    documents: int
    document_chunks: int
    organizations: int
    service_cards: int
    conversations: int
    messages: int

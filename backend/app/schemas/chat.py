from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    document: str | None = Field(default=None, min_length=1)
    conversation_id: UUID | None = None
    user_id: UUID | None = None


class Source(BaseModel):
    document: str
    page: int
    chunk_id: str
    score: float
    citation: str


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    sources: list[Source]
    pages: list[int]
    citation: str | None = None
    conversation_id: UUID | None = None
    message_id: UUID | None = None

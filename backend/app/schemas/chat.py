from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    document: str | None = Field(default=None, min_length=1)


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

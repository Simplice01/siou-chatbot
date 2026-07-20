from pydantic import BaseModel


class DocumentSummary(BaseModel):
    id: str
    name: str
    size_bytes: int
    modified_at: float
    indexed: bool
    page_count: int | None = None
    chunk_count: int | None = None


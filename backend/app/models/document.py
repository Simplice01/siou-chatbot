from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    text: str
    char_count: int


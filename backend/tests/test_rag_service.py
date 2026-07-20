import pytest

from app.core.config import Settings
from app.models.document import DocumentChunk
from app.services.citation_service import CitationService
from app.services.prompt_service import PromptService
from app.services.rag_service import ABSENT_ANSWER, RagService


class FakeRetrieval:
    def __init__(self, results):
        self.results = results

    async def retrieve(self, document_id: str, question: str):
        return self.results

    async def retrieve_any(self, question: str):
        return self.results


class FakeLLM:
    async def answer(self, messages):
        return "Le contrat indique un montant de 1200 euros."


@pytest.mark.asyncio
async def test_rag_returns_absent_when_no_context() -> None:
    settings = Settings(llm_provider="ollama", embedding_provider="hash")
    rag = RagService(settings, FakeRetrieval([]), PromptService(), FakeLLM(), CitationService())
    response = await rag.chat("doc", "Quel est le montant ?")
    assert response.answer == ABSENT_ANSWER
    assert response.sources == []


@pytest.mark.asyncio
async def test_rag_returns_sources_and_pages() -> None:
    settings = Settings(llm_provider="ollama", embedding_provider="hash", min_confidence=0.1)
    chunk = DocumentChunk(
        id="c1",
        document_id="doc",
        document_name="doc.pdf",
        page_start=4,
        page_end=4,
        text="Le montant du contrat est de 1200 euros.",
        char_count=42,
    )
    rag = RagService(settings, FakeRetrieval([(chunk, 0.7)]), PromptService(), FakeLLM(), CitationService())
    response = await rag.chat("doc", "Quel est le montant ?")
    assert "1200 euros" in response.answer
    assert response.pages == [4]
    assert response.sources[0].page == 4

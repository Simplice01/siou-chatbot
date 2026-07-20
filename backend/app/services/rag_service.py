from app.core.config import Settings
from app.schemas.chat import ChatResponse
from app.services.citation_service import CitationService
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.retrieval_service import RetrievalService


ABSENT_ANSWER = "L'information est absente du document."


class RagService:
    def __init__(
        self,
        settings: Settings,
        retrieval: RetrievalService,
        prompt: PromptService,
        llm: LLMService,
        citations: CitationService,
    ) -> None:
        self.settings = settings
        self.retrieval = retrieval
        self.prompt = prompt
        self.llm = llm
        self.citations = citations

    async def chat(self, document_id: str | None, question: str) -> ChatResponse:
        if document_id:
            results = await self.retrieval.retrieve(document_id, question)
        else:
            results = await self.retrieval.retrieve_any(question)
        usable = [(chunk, score) for chunk, score in results if score >= self.settings.min_confidence]
        sources = self.citations.build_sources(usable)
        if not usable:
            return ChatResponse(answer=ABSENT_ANSWER, confidence=0.0, sources=[], pages=[], citation=None)
        messages = self.prompt.build(question, usable)
        answer = (await self.llm.answer(messages)).strip() or ABSENT_ANSWER
        confidence = max(0.0, min(1.0, sum(source.score for source in sources) / len(sources)))
        pages = sorted({source.page for source in sources})
        return ChatResponse(
            answer=answer,
            confidence=confidence,
            sources=sources,
            pages=pages,
            citation=sources[0].citation if sources else None,
        )

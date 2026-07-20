from fastapi.testclient import TestClient

from app.api.deps import get_rag_service
from app.main import app
from app.schemas.chat import ChatResponse


class FakeRag:
    async def chat(self, document_id: str, question: str) -> ChatResponse:
        return ChatResponse(answer="Réponse test", confidence=0.8, sources=[], pages=[], citation=None)


def test_health() -> None:
    client = TestClient(app)
    assert client.get("/api/health").json() == {"status": "ok"}


def test_chat_endpoint_uses_rag_dependency() -> None:
    app.dependency_overrides[get_rag_service] = lambda: FakeRag()
    client = TestClient(app)
    response = client.post("/api/chat", json={"document": "doc", "question": "Une question ?"})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["answer"] == "Réponse test"


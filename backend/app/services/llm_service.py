from abc import ABC, abstractmethod

import httpx
from openai import OpenAI

from app.core.config import Settings


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    async def complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""


class OllamaLLMProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, temperature: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    async def complete(self, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False, "options": {"temperature": self.temperature}},
            )
            response.raise_for_status()
            return response.json()["message"]["content"]


class LLMService:
    def __init__(self, settings: Settings) -> None:
        provider = settings.llm_provider.lower()
        if provider == "ollama":
            self.provider: LLMProvider = OllamaLLMProvider(settings.ollama_base_url, settings.ollama_chat_model, settings.llm_temperature)
        else:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY est requis pour LLM_PROVIDER=openai")
            self.provider = OpenAILLMProvider(settings.openai_api_key, settings.resolved_openai_chat_model, settings.llm_temperature)

    async def answer(self, messages: list[dict[str, str]]) -> str:
        return await self.provider.complete(messages)

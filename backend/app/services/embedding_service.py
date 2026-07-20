import hashlib
from abc import ABC, abstractmethod

import httpx
import numpy as np
from openai import OpenAI

from app.core.config import Settings


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            vec = np.zeros(self.dimensions, dtype="float32")
            tokens = text.lower().split()
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vec[index] += sign
            norm = np.linalg.norm(vec)
            vectors.append(vec / norm if norm else vec)
        return np.vstack(vectors).astype("float32") if vectors else np.empty((0, self.dimensions), dtype="float32")


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def embed(self, texts: list[str]) -> np.ndarray:
        response = self.client.embeddings.create(model=self.model, input=texts)
        vectors = [item.embedding for item in response.data]
        arr = np.array(vectors, dtype="float32")
        faiss_norm = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / np.maximum(faiss_norm, 1e-12)


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, texts: list[str]) -> np.ndarray:
        async with httpx.AsyncClient(timeout=120) as client:
            vectors = []
            for text in texts:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                vectors.append(response.json()["embedding"])
        arr = np.array(vectors, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / np.maximum(norms, 1e-12)


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        provider = settings.embedding_provider.lower()
        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY est requis pour EMBEDDING_PROVIDER=openai")
            self.provider: EmbeddingProvider = OpenAIEmbeddingProvider(settings.openai_api_key, settings.openai_embedding_model)
        elif provider == "ollama":
            self.provider = OllamaEmbeddingProvider(settings.ollama_base_url, settings.ollama_embedding_model)
        else:
            self.provider = HashEmbeddingProvider(settings.embedding_dimensions)

    async def embed_texts(self, texts: list[str]) -> np.ndarray:
        return await self.provider.embed(texts)


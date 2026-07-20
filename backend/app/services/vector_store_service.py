import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.models.document import DocumentChunk


class VectorStoreService:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _doc_dir(self, document_id: str) -> Path:
        return self.root / document_id

    def _index_path(self, document_id: str) -> Path:
        return self._doc_dir(document_id) / "index.faiss"

    def _chunks_path(self, document_id: str) -> Path:
        return self._doc_dir(document_id) / "chunks.json"

    def _metadata_path(self, document_id: str) -> Path:
        return self._doc_dir(document_id) / "metadata.json"

    def save(self, document_id: str, embeddings: np.ndarray, chunks: list[DocumentChunk], metadata: dict[str, Any]) -> None:
        doc_dir = self._doc_dir(document_id)
        doc_dir.mkdir(parents=True, exist_ok=True)
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype("float32")
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, str(self._index_path(document_id)))
        self._chunks_path(document_id).write_text(
            json.dumps([chunk.__dict__ for chunk in chunks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._metadata_path(document_id).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def exists(self, document_id: str) -> bool:
        return self._index_path(document_id).exists() and self._chunks_path(document_id).exists()

    def list_document_ids(self) -> list[str]:
        candidates = sorted(
            path.name
            for path in self.root.iterdir()
            if path.is_dir() and (path / "index.faiss").exists() and (path / "chunks.json").exists()
        )
        active = [document_id for document_id in candidates if (self.read_metadata(document_id) or {}).get("active") is True]
        return active or candidates

    def read_metadata(self, document_id: str) -> dict[str, Any] | None:
        path = self._metadata_path(document_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def load_chunks(self, document_id: str) -> list[DocumentChunk]:
        data = json.loads(self._chunks_path(document_id).read_text(encoding="utf-8"))
        return [DocumentChunk(**item) for item in data]

    def search(self, document_id: str, query_embedding: np.ndarray, top_k: int) -> list[tuple[DocumentChunk, float]]:
        if not self.exists(document_id):
            raise FileNotFoundError(f"Index FAISS absent pour {document_id}")
        index = faiss.read_index(str(self._index_path(document_id)))
        chunks = self.load_chunks(document_id)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        scores, indices = index.search(query_embedding.astype("float32"), top_k)
        results: list[tuple[DocumentChunk, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(chunks):
                continue
            results.append((chunks[idx], float(score)))
        return results

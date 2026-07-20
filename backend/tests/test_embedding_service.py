import numpy as np
import pytest

from app.services.embedding_service import HashEmbeddingProvider


@pytest.mark.asyncio
async def test_hash_embeddings_are_normalized_and_deterministic() -> None:
    provider = HashEmbeddingProvider(dimensions=64)
    first = await provider.embed(["contrat montant", "resiliation preavis"])
    second = await provider.embed(["contrat montant", "resiliation preavis"])
    assert first.shape == (2, 64)
    assert np.allclose(first, second)
    assert np.allclose(np.linalg.norm(first, axis=1), [1.0, 1.0])


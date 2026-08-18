"""Local embedding and reranking clients; no external model API calls."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Iterable
from pathlib import Path

from fastembed import TextEmbedding
from fastembed.common.model_description import ModelSource, PoolingType
from graphiti_core.cross_encoder.client import CrossEncoderClient
from graphiti_core.embedder.client import EmbedderClient

EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
EMBEDDING_DIMENSION = 384
EMBEDDING_MODEL_FILE = "onnx/model.onnx"


def embedding_cache_dir() -> Path:
    configured = os.getenv("GRAPHITI_CODEX_EMBEDDING_CACHE")
    if configured:
        return Path(configured).expanduser()
    shared = Path.home() / ".cache" / "chat-recall" / "models"
    if shared.exists():
        return shared
    return Path.home() / ".cache" / "graphiti-codex" / "models"


class LocalFastEmbedder(EmbedderClient):
    """Multilingual E5 embeddings in-process via FastEmbed/ONNX."""

    def __init__(self, *, cache_dir: Path | None = None) -> None:
        known = {entry["model"].casefold() for entry in TextEmbedding.list_supported_models()}
        if EMBEDDING_MODEL.casefold() not in known:
            TextEmbedding.add_custom_model(
                model=EMBEDDING_MODEL,
                pooling=PoolingType.MEAN,
                normalization=True,
                sources=ModelSource(hf=EMBEDDING_MODEL),
                dim=EMBEDDING_DIMENSION,
                model_file=EMBEDDING_MODEL_FILE,
                description="Multilingual E5 small for local Graphiti retrieval",
            )
        self.cache_dir = cache_dir or embedding_cache_dir()
        self.model = TextEmbedding(
            model_name=EMBEDDING_MODEL,
            cache_dir=str(self.cache_dir),
            local_files_only=os.getenv("HF_HUB_OFFLINE") == "1",
            revision=EMBEDDING_REVISION,
        )

    @staticmethod
    def _texts(input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]]) -> list[str]:
        if isinstance(input_data, str):
            return [input_data]
        values = list(input_data)
        if not all(isinstance(value, str) for value in values):
            raise TypeError("LocalFastEmbedder accepts text input only")
        return values

    def _embed(self, texts: list[str]) -> list[list[float]]:
        prepared = [f"passage: {text}" for text in texts]
        vectors = [list(map(float, vector)) for vector in self.model.embed(prepared)]
        if len(vectors) != len(texts):
            raise RuntimeError("FastEmbed returned an unexpected vector count")
        if any(len(vector) != EMBEDDING_DIMENSION for vector in vectors):
            raise RuntimeError("FastEmbed returned an unexpected vector dimension")
        return vectors

    async def create(
        self,
        input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]],
    ) -> list[float]:
        vectors = await asyncio.to_thread(self._embed, self._texts(input_data))
        if not vectors:
            raise ValueError("Cannot embed an empty input")
        return vectors[0]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self._embed, input_data_list)


class PassThroughCrossEncoder(CrossEncoderClient):
    """Keep RRF order locally; never instantiate Graphiti's OpenAI reranker."""

    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        del query
        return [(passage, 1.0 / (index + 1)) for index, passage in enumerate(passages)]

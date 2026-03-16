from abc import abstractmethod, ABC
from typing import Sequence
from dataclasses import dataclass

from app.ingestion.chunker import DocumentChunk


@dataclass(frozen=True)
class RepoSearchResult:
    path: str
    score: float
    line: int
    snippet: str


@dataclass(frozen=True)
class ChunkSearchHit:
    chunk_id: str
    source_path: str
    text: str
    start_offset: int
    end_offset: int
    score: float


class ChunkRepository(ABC):
    @abstractmethod
    def count(self) -> int:
        ...

    @abstractmethod
    def search_similar(
            self,
            query_embedding: Sequence[float],
            top_k: int = 3,
    ) -> list[ChunkSearchHit]:
        ...

    @abstractmethod
    def search_by_term(
            self,
            terms: list[str],
            top_k: int = 5,
    ) -> list[ChunkSearchHit]:
        ...

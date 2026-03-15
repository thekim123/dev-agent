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


class ChunkRepository(ABC):
    @abstractmethod
    def count(self) -> int:
        ...

    @abstractmethod
    def search_similar(
            self,
            query_embedding: Sequence[float],
            top_k: int = 3,
    ) -> list[tuple[float, DocumentChunk]]:
        ...

    @abstractmethod
    def search_by_term(
            self,
            terms: list[str],
            top_k: int = 5,
    ) -> list[RepoSearchResult]:
        ...

from abc import abstractmethod, ABC
from typing import Sequence

from app.repository.models import ChunkSearchHit


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

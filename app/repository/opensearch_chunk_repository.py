from http import HTTPStatus
from typing import Sequence

import httpx

from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit


def _build_knn_query(
        query_embedding: Sequence[float],
        top_k: int,
) -> dict:
    ...


def _build_term_query(
        terms: list[str],
        top_k: int
) -> dict:
    ...


def _parse_hit(hit: dict) -> ChunkSearchHit:
    source = hit["_source"]
    return ChunkSearchHit(
        chunk_id=source["chunk_id"],
        source_path=source["source_path"],
        text=source["text"],
        score=float(source["score"]),
        start_offset=source["start"],
        end_offset=source["end"],
    )


class OpenSearchChunkRepository(ChunkRepository):
    def __init__(self, host, index_name):
        self.host = host.rstrip("/")
        self.index_name = index_name

    def count(self) -> int:
        response = self._request("GET", f"/{self.index_name}/_count")
        print(response)
        return 0

    def search_similar(self, query_embedding, top_k=3):
        raise NotImplementedError

    def search_by_term(self, terms, top_k=5):
        raise NotImplementedError

    def _request(
            self,
            method: str,
            path: str,
            json_body: dict | None = None
    ) -> httpx.Response:
        with httpx.Client(base_url=self.host, timeout=5.0) as client:
            res = client.request(method, path, json=json_body)
            print(res)
            return res

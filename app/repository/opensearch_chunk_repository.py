from typing import Sequence

import httpx

from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit


def _build_knn_query(
        query_embedding: Sequence[float],
        top_k: int,
) -> dict:
    return {
        "_source": ["chunk_id", "source_path", "text", "start", "end"],
        "size": top_k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": top_k,
                }
            }
        },
    }


def _build_term_query(
        terms: list[str],
        top_k: int
) -> dict:
    should_clauses = []
    for term in terms:
        should_clauses.append(
            {
                "match": {
                    "source_path": {
                        "query": term, "boost": 3
                    }
                },
            }
        )
        should_clauses.append(
            {
                "match": {
                    "text": {
                        "query": term, "boost": 1
                    }
                },
            }
        )
    return {
        "size": top_k,
        "_source": ["chunk_id", "source_path", "text", "start", "end"],
        "query": {
            "bool": {
                "should": should_clauses,
                "must_not": [
                    {"wildcard": {"source_path": "*.md"}},
                ],
                "minimum_should_match": 1
            }
        }
    }


def _parse_hit(hit: dict) -> ChunkSearchHit:
    source = hit["_source"]
    return ChunkSearchHit(
        chunk_id=source["chunk_id"],
        source_path=source["source_path"],
        text=source["text"],
        score=hit["_score"],
        start=source["start"],
        end=source["end"],
    )


class OpenSearchChunkRepository(ChunkRepository):
    def __init__(self, host, index_name):
        self.host = host.rstrip("/")
        self.client = httpx.Client(base_url=self.host, timeout=5.0)
        self.index_name = index_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self):
        self.client.close()

    def count(self) -> int:
        count_response = (self.client.get(f"/{self.index_name}/_count"))
        count_response.raise_for_status()
        return count_response.json()["count"]

    def search_similar(self, query_embedding, top_k=3) -> list[ChunkSearchHit]:
        response = self.client.post(
            f"/{self.index_name}/_search",
            json=_build_knn_query(query_embedding, top_k),
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload["hits"]["hits"]
        return [_parse_hit(hit) for hit in hits]

    def search_by_term(self, terms, top_k=5) -> list[ChunkSearchHit]:
        response = self.client.post(
            f"/{self.index_name}/_search",
            json=_build_term_query(terms, top_k),
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload["hits"]["hits"]
        return [_parse_hit(hit) for hit in hits]

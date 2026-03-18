import json

import httpx

from app.repository.base import ChunkSearchHit

HOST = "http://localhost:9200"
INDEX = "code_chunks_demo"


def build_index_body(dimension: int) -> dict:
    return {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "source_path": {"type": "text"},
                "text": {"type": "text"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dimension,
                },
            }
        },
    }




def build_knn_query(query_vector: list[float], top_k: int) -> dict:
    return {
        "size": top_k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_vector,
                    "k": top_k,
                }
            }
        },
    }


def assert_bulk_succeeded(response: httpx.Response) -> dict:
    response.raise_for_status()
    payload = response.json()

    if payload["errors"]:
        failed_items = []
        for item in payload["items"]:
            index_result = item["index"]
            if "error" in index_result:
                failed_items.append({
                    "id": index_result.get("_id"),
                    "error": index_result["error"],
                })
        raise RuntimeError(f"bulk indexing failed: {failed_items}")
    return payload


def build_term_query(terms: list[str], top_k: int) -> dict:
    should_clauses = []
    for term in terms:
        should_clauses.append({
            "match": {
                "source_path": {
                    "query": term,
                    "boost": 3,
                }
            }
        })

        should_clauses.append({
            "match": {
                "text": {
                    "query": term,
                    "boost": 1,
                }
            }
        })

    return {
        "size": top_k,
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1
            }
        }
    }


def parse_knn_hits(payload: dict) -> list[dict]:
    results = []
    hits = payload["hits"]["hits"]
    for hit in hits:
        source = hit["_source"]
        results.append(ChunkSearchHit(
            score=hit["_score"],
            chunk_id=source["chunk_id"],
            source_path=source["source_path"],
            text=source["text"],
            start=source["start"],
            end=source["end"],
        ))
    return results


def parse_term_hits(payload: dict) -> list[dict]:
    results = []
    hits = payload["hits"]["hits"]
    for hit in hits:
        source = hit["_source"]
        results.append(ChunkSearchHit(
            score=hit["_score"],
            chunk_id=source["chunk_id"],
            start=source["start"],
            end=source["end"],
            source_path=source["source_path"],
            text=source["text"],
        ))
    return results


docs = [
    {
        "chunk_id": "a",
        "source_path": "app/auth/login.py",
        "text": "login flow creates access token",
        "start": 1,
        "end": 10,
        "embedding": [1.0, 0.0],
    },
    {
        "chunk_id": "b",
        "source_path": "app/auth/token_service.py",
        "text": "refresh token logic issues new access token",
        "start": 11,
        "end": 20,
        "embedding": [0.9, 0.1],
    },
    {
        "chunk_id": "c",
        "source_path": "doc/authentication.md",
        "text": "oauth callback and auth document",
        "start": 21,
        "end": 30,
        "embedding": [0.0, 1.0],
    },
]

if __name__ == "__main__":
    with httpx.Client(base_url=HOST, timeout=5.0) as client:

        search_response = client.post(
            f"/{INDEX}/_search",
            json=build_knn_query([1.0, 0.0], top_k=2),
        )
        search_response.raise_for_status()
        # print(json.dumps(search_response.json(), indent=2, ensure_ascii=False))

        term_response = client.post(
            f"/{INDEX}/_search",
            json=build_term_query(["token", "refresh"], top_k=2),
        )
        term_response.raise_for_status()
        result_list = parse_term_hits(term_response.json())
        print(result_list)
        print()
        print(json.dumps(term_response.json(), indent=2, ensure_ascii=False))

        knn_results = parse_knn_hits(search_response.json())
        # print(json.dumps(knn_results, indent=2, ensure_ascii=False))

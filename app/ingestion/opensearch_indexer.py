import json
from dataclasses import asdict
from pathlib import Path

import httpx

from app.ingestion.models import DocumentChunk


def build_index_body(dimension: int) -> dict:
    return {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "chunk_id": {"type": "keyword"},
                "source_path": {"type": "text"},
                "text": {"type": "text"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
                "embedding": {
                    "type": "knn_vector",
                    "space_type": "cosinesimil",
                    "dimension": dimension
                }
            }
        }
    }


def build_bulk_body(index_name: str, docs: list[DocumentChunk]) -> str:
    results = []
    for doc in docs:
        results.append(
            json.dumps(
                {
                    "index": {
                        "_index": index_name,
                        "_id": doc.chunk_id,
                    }
                },
                ensure_ascii=False,
            ),
        )
        results.append(json.dumps(asdict(doc), ensure_ascii=False))
    return "\n".join(results) + "\n"


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
                    "error": index_result.get("error"),
                })
        raise RuntimeError(f"bulk indexing failed: {failed_items}")
    return payload


class OpenSearchIndexer:
    def __init__(self, host, index_name, dimension):
        self.host = host
        self.index_name = index_name
        self.dimension = dimension
        self.client = httpx.Client(base_url=host, timeout=5.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def create_index(self):
        body = build_index_body(self.dimension)
        self.client.put(f"/{self.index_name}", json=body).raise_for_status()

    def bulk_insert(self, docs: list[DocumentChunk]):
        body = build_bulk_body(self.index_name, docs)
        res = self.client.post(
            f"_bulk?refresh=true",
            headers={"Content-Type": "application/x-ndjson"},
            content=body,
        )
        bulk_payload = assert_bulk_succeeded(res)
        return bulk_payload

    def close(self):
        self.client.close()


def to_chunk(row: dict) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=row["chunk_id"],
        source_path=row["source_path"],
        text=row["text"],
        start=int(row["start"]),
        end=int(row["end"]),
        embedding=[float(value) for value in row["embedding"]],
    )


def load_chunks(path: Path, limit: int | None = None) -> list[DocumentChunk]:
    raw = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(raw, list):
        raise ValueError("vector_store.json 최상위 구조는 list여야 합니다.")

    rows = raw[:limit] if limit is not None else raw
    chunks = [to_chunk(row) for row in rows]

    if not chunks:
        raise ValueError("적재할 청크가 없습니다.")

    dimension = len(chunks[0].embedding)
    for chunk in chunks:
        if len(chunk.embedding) != dimension:
            raise ValueError("embedding 차원이 섞여 있습니다.")
    return chunks

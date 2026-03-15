from app.repository.json_chunk_repository import JsonChunkRepository
from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository
import os


def create_chunk_repository():
    backend = os.getenv("CHUNK_REPOSITORY_BACKEND", "json").lower()

    if backend == "json":
        return JsonChunkRepository()

    if backend == "opensearch":
        return OpenSearchChunkRepository(
            host=os.getenv("OPENSEARCH_HOST", "http://localhost:9200"),
            index_name=os.getenv("OPENSEARCH_INDEX", "code_chunks"),
        )

    raise ValueError(f"backend {backend} not supported")

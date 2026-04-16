from app.config import CHUNK_REPOSITORY_BACKEND


def create_chunk_repository():
    import os

    if CHUNK_REPOSITORY_BACKEND == "json":
        from app.repository.json_chunk_repository import JsonChunkRepository
        return JsonChunkRepository()

    if CHUNK_REPOSITORY_BACKEND == "opensearch":
        from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository
        return OpenSearchChunkRepository(
            host=os.getenv("OPENSEARCH_HOST", "http://localhost:9200"),
            index_name=os.getenv("OPENSEARCH_INDEX", "code_chunks"),
        )

    raise ValueError(f"backend {CHUNK_REPOSITORY_BACKEND} not supported")

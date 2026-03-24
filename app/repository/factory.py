def create_chunk_repository():
    import os
    backend = os.getenv("CHUNK_REPOSITORY_BACKEND", "json").lower()

    if backend == "json":
        from app.repository.json_chunk_repository import JsonChunkRepository
        return JsonChunkRepository()

    if backend == "opensearch":
        from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository
        return OpenSearchChunkRepository(
            host=os.getenv("OPENSEARCH_HOST", "http://localhost:9200"),
            index_name=os.getenv("OPENSEARCH_INDEX", "code_chunks"),
        )

    raise ValueError(f"backend {backend} not supported")

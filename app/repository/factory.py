from app.config import settings


def create_chunk_repository():
    if settings.chunk_repository_backend == "json":
        from app.repository.json_chunk_repository import JsonChunkRepository
        return JsonChunkRepository()

    if settings.chunk_repository_backend == "opensearch":
        from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository
        return OpenSearchChunkRepository(
            host=settings.opensearch_host,
            index_name=settings.opensearch_index,
        )

    raise ValueError(f"backend {settings.chunk_repository_backend} not supported")

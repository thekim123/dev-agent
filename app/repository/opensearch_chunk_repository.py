from app.repository.base import ChunkRepository


class OpenSearchChunkRepository(ChunkRepository):
    def __init__(self, host, index_name):
        self.host = host
        self.index_name = index_name

    def count(self) -> int:
        raise NotImplementedError

    def search_similar(self, query_embedding, top_k=3):
        raise NotImplementedError

    def search_by_term(self, terms, top_k=5):
        raise NotImplementedError

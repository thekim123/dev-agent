from functools import lru_cache


class Retriever:
    def __init__(self, chunks, embedder):
        self.chunks = chunks
        self.embedder = embedder

    def search(self, question: str):
        return None




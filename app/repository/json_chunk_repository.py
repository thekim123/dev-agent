import json
from pathlib import Path

import numpy as np

from app.ingestion.chunker import DocumentChunk
from app.repository.base import ChunkRepository, ChunkSearchHit

ALLOWED = (".java", ".md", ".yml", ".txt", ".properties")
EXCLUDED_DIRS = {".gradle", "gradle", ".github", "build", "target", ".git", ".idea", "node_modules", "__pycache__"}
STOPWORDS = {"어디", "설명", "해줘", "해주세요", "무엇", "뭐", "찾아줘", "찾아", "관련", "있는", "인가", "이거"}

BASE_DIR = Path(__file__).resolve().parent.parent


class JsonChunkRepository(ChunkRepository):
    def count(self) -> int:
        return len(self.chunks)

    def __init__(self, path: str = "vector_store.json"):
        self.chunks = self._load_chunks(path)

    def _load_chunks(self, path="vector_store.json"):
        vector_store_path = BASE_DIR / path
        with open(vector_store_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = []
        for item in data:
            chunk = DocumentChunk(
                chunk_id=item["chunk_id"],
                source_path=item["source_path"],
                text=item["text"],
                start=item["start"],
                end=item["end"],
                embedding=item["embedding"],
            )
            chunks.append(chunk)
        return chunks

    def _cosine_similarity(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search_similar(self, query_embedding: list[float], top_k=3) -> list[ChunkSearchHit]:
        scored = []
        for chunk in self.chunks:
            score = self._cosine_similarity(query_embedding, chunk.embedding)
            scored.append(ChunkSearchHit(
                chunk_id=chunk.chunk_id,
                score=score,
                source_path=chunk.source_path,
                text=chunk.text,
                start=chunk.start,
                end=chunk.end,
            ))
        return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]

    def search_by_term(self, terms, top_k=5) -> list[ChunkSearchHit]:
        results = []
        for chunk in self.chunks:
            score = 0
            path = chunk.source_path.lower()
            text = chunk.text.lower()

            for term in terms:
                # 3. path에 term 있으면 점수 크게 가산
                if term in path:
                    score += 10
                # 4. text에 term 있으면 점수 가산
                if term in text:
                    score += 5

            # 5. 결과를 ChunkSearchHit로 반환
            if score > 0:
                results.append(
                    ChunkSearchHit(
                        source_path=chunk.source_path,
                        score=score,
                        start=chunk.start,
                        end=chunk.end,
                        text=chunk.text,
                        chunk_id=chunk.chunk_id
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

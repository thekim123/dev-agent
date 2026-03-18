from app.agent.service import AgentService
from app.repository.base import ChunkSearchHit


class FakeEmbedder:
    def embed(self, text):
        return [1.0, 0.0]

    def query_embed(self, doc_text, question):
        return [{"text": "요약 답변"}]


class FakeRepository:
    def search_similar(self, query_embedding, top_k=3) -> list[ChunkSearchHit]:
        from app.repository.base import ChunkSearchHit
        chunk = ChunkSearchHit(
            chunk_id="a",
            source_path="app/auth/token_service.py",
            text="token refresh logic",
            start=1,
            end=10,
            score=10.0,
        )
        return [chunk]

    def search_by_term(self, terms, top_k=5) -> list[ChunkSearchHit]:
        from app.repository.base import ChunkSearchHit
        return [
            ChunkSearchHit(
                source_path="app/auth/token_service.py",
                score=10.0,
                start=1,
                end=1,
                text="token refresh logic",
                chunk_id="a"
            )
        ]


def test_answer_routes_repo_question():
    service = AgentService(
        embedder=FakeEmbedder(),
        repository=FakeRepository()
    )

    result = service.answer("토큰 갱신 로직은 어디에 있어?")

    assert result.used_tool == "search_repo"
    assert result.sources


def test_answer_routes_direct_question():
    ...


def test_answer_routes_doc_question():
    ...

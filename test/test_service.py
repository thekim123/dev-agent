from app.agent.service import AgentService


class FakeEmbedder:
    def embed(self, text):
        return [1.0, 0.0]

    def query_embed(self, doc_text, question):
        return [{"text": "요약 답변"}]


class FakeRepository:
    def search_similar(self, query_embedding, top_k=3):
        from app.ingestion.chunker import DocumentChunk
        chunk = DocumentChunk(
            chunk_id="a",
            source_path="app/a.py",
            text="token refresh logic",
            start=1,
            end=10,
            embedding=[1.0, 0.0],
        )
        return [(0.9, chunk)]

    def search_by_term(self, terms, top_k=5):
        from app.repository.base import RepoSearchResult
        return [
            RepoSearchResult(
                path="app/a.py",
                score=10.0,
                line=1,
                snippet="token refresh logic",
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

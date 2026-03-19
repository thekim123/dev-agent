from app.agent.service import AgentService
from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit
from test.conftest import FakeEmbedder


class FakeRepository(ChunkRepository):
    def __init__(self, hits: list[ChunkSearchHit] = None):
        self.hits = hits or []

    def search_similar(self, query_embedding, top_k=3) -> list[ChunkSearchHit]:
        if len(self.hits) == 0:
            return []

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
        if len(self.hits) == 0:
            return []

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

    def count(self):
        return 1


hits = [ChunkSearchHit(
    chunk_id="a",
    source_path="app/auth/token_service.py",
    text="token refresh logic",
    start=1,
    end=10,
    score=10.0,
)]


def test_answer_routes_repo_question():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_embed=FakeEmbedder().query_embed,
        repository=FakeRepository(hits=hits)
    )

    result = service.answer("토큰 갱신 로직은 어디에 있어?")
    assert result.used_tool == "search_repo"
    assert result.sources
    assert result.sources[0].path == "app/auth/token_service.py"
    assert "token refresh logic" in result.sources[0].snippet


def test_answer_routes_direct_question():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_embed=FakeEmbedder().query_embed,
        repository=FakeRepository(hits=hits)
    )
    result = service.answer("안녕?")

    assert result.used_tool == "direct"
    assert result.sources == []
    assert result.answer == '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.'


def test_answer_retrieve_no_docs():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_embed=FakeEmbedder().query_embed,
        repository=FakeRepository()
    )
    result = service.answer("이 프로젝트에서 인증 로직과 리프레시토큰 로직에 대해서 설명해줘.")
    assert result.used_tool == "retrieve_docs"
    assert result.sources == []
    assert result.answer == '지금 가지고 있는 자료에서는 마땅한게 없네요.'


def test_answer_routes_doc_question():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_embed=FakeEmbedder().query_embed,
        repository=FakeRepository(hits=hits)
    )

    result = service.answer("이 프로젝트에서 인증 로직과 리프레시토큰 로직에 대해서 설명해줘.")

    assert result.used_tool == "retrieve_docs"
    assert result.sources[0].path == "app/auth/token_service.py"
    assert result.answer == "stubbed answer"

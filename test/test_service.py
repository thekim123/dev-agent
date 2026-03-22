from app.agent.service import AgentService
from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit
from test.conftest import FakeEmbedder, FakeLLMClient


class FakeRepository(ChunkRepository):
    def __init__(self, hits: list[ChunkSearchHit] = None):
        self.hits = hits or []

    def search_similar(self, query_embedding, top_k=3) -> list[ChunkSearchHit]:
        if len(self.hits) == 0:
            return []
        return self.hits

    def search_by_term(self, terms, top_k=5) -> list[ChunkSearchHit]:
        if len(self.hits) == 0:
            return []
        return self.hits

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
        query_to_llm=FakeLLMClient().query_to_llm,
        repository=FakeRepository(hits=hits)
    )

    result = service.answer("test_answer_routes_repo_question")
    assert result.used_tool == "search_repo"
    assert result.sources
    assert result.sources[0].path == "app/auth/token_service.py"
    assert "token refresh logic" in result.sources[0].snippet


def test_answer_routes_direct_question():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=FakeLLMClient().query_to_llm,
        repository=FakeRepository(hits=hits)
    )
    result = service.answer("test_answer_routes_direct_question")

    assert result.used_tool == "direct"
    assert result.sources == []
    assert result.answer == '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.'


def test_answer_retrieve_no_docs():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=FakeLLMClient().query_to_llm,
        repository=FakeRepository()
    )
    result = service.answer("retrieve_no_docs_test")
    assert result.used_tool == "retrieve_docs"
    assert result.sources == []
    assert result.answer == '지금 가지고 있는 자료에서는 마땅한게 없네요.'


def test_answer_routes_doc_question():
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=FakeLLMClient().query_to_llm,
        repository=FakeRepository(hits=hits)
    )

    result = service.answer("test_answer_routes_doc_question")

    assert result.used_tool == "retrieve_docs"
    assert result.sources[0].path == "app/auth/token_service.py"
    assert result.answer == 'test_answer_routes_doc_question'


def test_retrieve_docs_remove_duplicate():
    test_hits = [
        ChunkSearchHit(
            source_path="app/auth/token_service.py",
            score=10.0,
            start=1,
            end=1,
            text="token refresh logic_a",
            chunk_id="a"
        ),
        ChunkSearchHit(
            source_path="app/auth/token_service.py",
            score=9.0,
            start=1,
            end=1,
            text="token refresh logic_b",
            chunk_id="b"
        ),
        ChunkSearchHit(
            source_path="app/auth/token_service.py",
            score=5.0,
            start=1,
            end=1,
            text="token refresh logic_c",
            chunk_id="c"
        )
    ]

    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=FakeLLMClient().query_to_llm,
        repository=FakeRepository(hits=test_hits)
    )
    answer = service.answer("retrieve_docs_remove_duplicate_test")
    assert answer.used_tool == "retrieve_docs"
    assert len(answer.sources) == 1
    assert answer.sources[0].path == "app/auth/token_service.py"
    assert answer.answer == "test_answer_routes_doc_question"

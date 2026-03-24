import json

import pytest
from starlette.testclient import TestClient

from app.repository.base import ChunkRepository
from app.agent.service import AgentService
from app.main import app, get_agent_service
from app.repository.json_chunk_repository import JsonChunkRepository
from app.repository.models import ChunkSearchHit
from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository


@pytest.fixture(scope="session")
def sample_rows():
    return [
        {
            "chunk_id": "a",
            "source_path": "app/auth/token_service.py",
            "text": "token refresh logic",
            "start": 1,
            "end": 10,
            "embedding": [1.0, 0.0],
        },
        {
            "chunk_id": "b",
            "source_path": "app/user/service.py",
            "text": "user login flow",
            "start": 11,
            "end": 20,
            "embedding": [0.8, 0.2],
        },
        {
            "chunk_id": "c",
            "source_path": "app/docs/readme.md",
            "text": "authentication document",
            "start": 21,
            "end": 30,
            "embedding": [0.0, 1.0],
        },
    ]


@pytest.fixture(scope="session")
def vector_store_path(tmp_path_factory, sample_rows):
    root = tmp_path_factory.mktemp("vector_store_test")
    path = root / "vector_store_test.json"
    path.write_text(json.dumps(sample_rows, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture(scope="session")
def json_repo(vector_store_path):
    return JsonChunkRepository(path=str(vector_store_path))


@pytest.fixture(scope="session")
def opensearch_repo(vector_store_path):
    return OpenSearchChunkRepository(host="http://localhost:9200", index_name="code_chunks")


class FakeEmbedder:
    def embed(self, text):
        return [1.0, 0.0]


class FakeLLMClient:
    def __init__(self, answers: list[str]):
        self.call_count = 0
        self.answers = answers

    def query_to_llm(self, prompt: str) -> str:
        result = self.answers[self.call_count]
        self.call_count += 1
        return result


@pytest.fixture
def fake_repository():
    hits = [
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
    return FakeRepository(hits=hits)


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


@pytest.fixture
def client(fake_repository: FakeRepository):
    answers = [
        json.dumps({
            'tool': 'retrieve_docs',
            'routed_question': 'test_answer_routes_doc_question',
            'reason': '',
            'direct_answer': 'stubbed answer',
            'is_final': False,
        }),
        'test_answer_routes_doc_question',
        json.dumps({
            'tool': 'retrieve_docs',
            'routed_question': 'test_answer_routes_doc_question',
            'reason': '',
            'direct_answer': 'stubbed answer',
            'is_final': False,
        }),
        'test_answer_routes_doc_question',
        json.dumps({
            'tool': 'retrieve_docs',
            'routed_question': 'test_answer_routes_doc_question',
            'reason': '',
            'direct_answer': 'stubbed answer',
            'is_final': True,
        })
    ]
    fake_embedder = FakeEmbedder()
    fake_llm_client = FakeLLMClient(answers)

    fake_repository = fake_repository

    def override_get_agent_service():
        return AgentService(
            repository=fake_repository,
            embed=fake_embedder.embed,
            query_to_llm=fake_llm_client.query_to_llm,
        )

    app.dependency_overrides[get_agent_service] = override_get_agent_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

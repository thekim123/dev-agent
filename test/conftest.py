import json

import pytest
from starlette.testclient import TestClient

from app.agent.service import AgentService
from app.main import app, get_agent_service
from app.repository.json_chunk_repository import JsonChunkRepository
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
    def query_to_llm(self, prompt: str) -> str:
        result = ''
        if "test_answer_routes_direct_question" in prompt:
            result = json.dumps({
                'tool': 'direct',
                'routed_question': '',
                'reason': '',
                'direct_answer': '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.',
            })
        elif 'test_answer_routes_repo_question' in prompt:
            result = json.dumps({
                'tool': 'search_repo',
                'routed_question': 'test_answer_routes_repo_question',
                'reason': '',
                'direct_answer': '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.',
            })
        elif '아래의 문서를 참고하여 답하라.' in prompt:
            result = 'test_answer_routes_doc_question'
        elif 'test_answer_routes_doc_question' in prompt:
            result = json.dumps({
                'tool': 'retrieve_docs',
                'routed_question': 'test_answer_routes_doc_question',
                'reason': '',
                'direct_answer': 'stubbed answer',
            })
        return result


@pytest.fixture
def client(json_repo):
    fake_embedder = FakeEmbedder()
    fake_llm_client = FakeLLMClient()

    def override_get_agent_service():
        return AgentService(
            repository=json_repo,
            embed=fake_embedder.embed,
            query_to_llm=fake_llm_client.query_to_llm,
        )

    app.dependency_overrides[get_agent_service] = override_get_agent_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

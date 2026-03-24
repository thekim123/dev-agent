import json

from app.agent.service import AgentService
from test.conftest import FakeEmbedder, FakeLLMClient, FakeRepository


def test_answer_routes_repo_question(fake_repository):
    answers = [
        json.dumps({
            'tool': 'search_repo',
            'routed_question': 'test_answer_routes_doc_question',
            'reason': '',
            'direct_answer': 'stubbed answer',
            'is_final': True,
        }),
        json.dumps({
            'tool': 'search_repo',
            'routed_question': 'token refresh logic',
            'reason': '',
            'direct_answer': '',
            'is_final': True,
        }),
    ]

    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=fake_repository
    )

    result = service.answer("test_answer_routes_repo_question")
    assert result.used_tool == "search_repo"
    assert result.sources
    assert result.sources[0].path == "app/auth/token_service.py"
    assert "token refresh logic" in result.sources[0].snippet


def test_answer_routes_direct_question():
    answers = [
        json.dumps({
            'tool': 'direct',
            'routed_question': '',
            'reason': '',
            'direct_answer': '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.',
            'is_final': True,
        }),
    ]
    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=FakeRepository()
    )
    result = service.answer("test_answer_routes_direct_question")

    assert result.used_tool == "direct"
    assert result.sources == []
    assert result.answer == '안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.'


def test_answer_retrieve_no_docs():
    answers = [
        json.dumps({
            'tool': 'retrieve_docs',
            'routed_question': 'test_answer_routes_doc_question',
            'reason': '',
            'direct_answer': 'stubbed answer',
            'is_final': True,
        }),
        json.dumps({
            'tool': 'direct',
            'routed_question': '',
            'reason': '',
            'direct_answer': '',
            'is_final': True,
        })
    ]

    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=FakeRepository()
    )
    result = service.answer("retrieve_no_docs_test")
    assert result.used_tool == "retrieve_docs"
    assert result.sources == []
    assert result.answer == '지금 가지고 있는 자료에서는 마땅한게 없네요.'
    assert fake_llm_client.call_count == 2


def test_answer_filter_55_under_docs(fake_repository):
    answers = [
                  json.dumps({
                      'tool': 'retrieve_docs',
                      'routed_question': 'test_answer_routes_doc_question',
                      'reason': '',
                      'direct_answer': 'stubbed answer',
                      'is_final': True,
                  }),
                  '지금 가지고 있는 자료에서는 마땅한게 없네요.'
              ] * 2

    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=fake_repository
    )
    result = service.answer("retrieve_no_docs_test")
    assert result.used_tool == "retrieve_docs"
    assert result.sources[0].score == 0.9
    assert result.answer == '지금 가지고 있는 자료에서는 마땅한게 없네요.'
    assert fake_llm_client.call_count == 3


def test_answer_routes_doc_question(fake_repository):
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
            'is_final': True,
        }),
    ]

    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=fake_repository
    )

    result = service.answer("test_answer_routes_doc_question")

    assert result.used_tool == "retrieve_docs"
    assert result.sources[0].path == "app/auth/token_service.py"
    assert result.answer == 'test_answer_routes_doc_question'
    assert fake_llm_client.call_count == 3


def test_retrieve_docs_remove_duplicate(fake_repository):
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
            'is_final': True,
        })
    ]

    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=fake_repository
    )
    answer = service.answer("retrieve_docs_remove_duplicate_test")
    assert answer.used_tool == "retrieve_docs"
    assert len(answer.sources) == 1
    assert answer.sources[0].path == "app/auth/token_service.py"
    assert answer.answer == "test_answer_routes_doc_question"
    assert fake_llm_client.call_count == 3


def test_answer_loops_max(fake_repository):
    answers = [
                  json.dumps({
                      'tool': 'retrieve_docs',
                      'routed_question': 'test_answer_routes_doc_question',
                      'reason': '',
                      'direct_answer': 'stubbed answer',
                      'is_final': False,
                  }),
                  'test_answer_routes_doc_question',
              ] * 20
    fake_llm_client = FakeLLMClient(answers)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_to_llm=fake_llm_client.query_to_llm,
        repository=fake_repository
    )
    answer = service.answer("retrieve_docs_remove_duplicate_test")
    assert answer.used_tool == "retrieve_docs"
    assert len(answer.sources) == 1
    assert answer.sources[0].path == "app/auth/token_service.py"
    assert answer.answer == "test_answer_routes_doc_question"
    assert fake_llm_client.call_count == 20

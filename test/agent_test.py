from starlette.testclient import TestClient

from app.agent.service import AgentService
from app.main import app, get_agent_service
from test.conftest import FakeEmbedder
from test.test_service import FakeRepository


def test_agent_endpoint_returns_response_shape():
    client = TestClient(app)
    service = AgentService(
        embed=FakeEmbedder().embed,
        query_embed=FakeEmbedder().query_embed,
        repository=FakeRepository()
    )
    app.dependency_overrides[get_agent_service] = lambda: service

    response = client.post(
        "/agent",
        json={"question": "토큰 갱신 로직은 어디에 있어?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert {"used_tool", "reason", "sources", "answer"} <= data.keys()

    app.dependency_overrides.clear()


def test_agent_endpoint_retrieve_docs(client):
    r = client.post("/agent", json={"question": "이 프로젝트의 토큰 갱신 로직과 Authentication 로직에 대해서 설명해줘"})
    data = r.json()
    assert r.status_code == 200
    assert {"used_tool", "reason", "sources", "answer"} <= data.keys()
    assert data["used_tool"] == "retrieve_docs"
    assert data["answer"] == "stubbed answer"


def test_agent_endpoint_search_repo(client):
    r = client.post("/agent", json={"question": "토큰 갱신 로직은 어디에 있어?"})
    assert r.status_code == 200
    data = r.json()
    assert {"used_tool", "reason", "sources", "answer"} <= data.keys()
    assert data["used_tool"] == "search_repo"

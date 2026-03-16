from starlette.testclient import TestClient

from app.agent.service import AgentService
from app.main import app, get_agent_service
from test.test_service import FakeEmbedder, FakeRepository


def test_agent_endpoint_returns_response_shape():
    client = TestClient(app)
    service = AgentService(
        embedder=FakeEmbedder(),
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
#
#
# def test_agent_endpoint():
#     r = client.post("/agent", json={"question": "토큰 갱신 로직은 어디에 있어?"})
#     assert r.status_code == 200
#     data = r.json()
#     assert {"used_tool", "reason", "sources", "answer"} <= data.keys()
#
#
# if __name__ == "__main__":
#     client = TestClient(app)
#     test_agent_endpoint()

from starlette.testclient import TestClient
from main import app

client = TestClient(app)


def test_agent_endpoint():
    r = client.post("/agent", json={"question": "토큰 갱신 로직은 어디에 있어?"})
    assert r.status_code == 200
    data = r.json()
    assert {"used_tool", "reason", "sources", "answer"} <= data.keys()


if __name__ == "__main__":
    client = TestClient(app)
    test_agent_endpoint()

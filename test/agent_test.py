def test_agent_endpoint_returns_response_shape(client):
    response = client.post("/agent", json={"question": "retrieve_docs_remove_duplicate_test"})
    assert response.status_code == 200
    data = response.json()
    assert {"used_tool", "reason", "sources", "answer"} <= data.keys()
import io
import json

from app.llm.llm_client import LLMClient


def invoke_model(body: str, modelId: str) -> dict:
    # response_body["output"]["message"]["content"][0]["text"]
    body = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": json.dumps({
                            "tool": "direct",
                            "reason": "test reason text",
                            "direct_answer": "test direct answer",
                            "routed_question": "What is the meaning of life" + "routed",
                        })
                    }
                ]
            }
        },
    }
    response = {"body": io.BytesIO(json.dumps(body).encode("utf-8"))}
    return response


def test_route():
    llm = LLMClient(invoke_model, "fake_model")
    question = "What is the meaning of life?"
    route_decision = llm.route(question)
    assert route_decision.tool == "direct"
    assert route_decision.reason == "test reason text"
    assert route_decision.direct_answer == "test direct answer"
    assert route_decision.routed_question == "What is the meaning of life" + "routed"

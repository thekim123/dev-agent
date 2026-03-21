import io
import json

from app.llm.llm_client import LLMClient


def invoke_model(body: str, modelId: str) -> dict:
    result_text = {
                            "tool": "direct",
                            "reason": "test reason text",
                            "direct_answer": "test direct answer",
                            "routed_question": "What is the meaning of life " + "routed",
                        }
    body = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": json.dumps(result_text)
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
    route_decision_str = llm.query_to_llm(question)
    result_text = {
                            "tool": "direct",
                            "reason": "test reason text",
                            "direct_answer": "test direct answer",
                            "routed_question": "What is the meaning of life " + "routed",
                        }
    assert route_decision_str == json.dumps(result_text)
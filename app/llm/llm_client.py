import json
import os

import boto3

from app.agent.models import RouteDecision


class LLMClient:
    def __init__(self, invoke_model, model_id):
        self.invoke_model = invoke_model
        self.model_id = model_id

    def query_to_llm(self, text: str, query: str) -> str:
        query_text = f'아래의 문서를 참고하여 답하라. {query}\n'
        query_text += text
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": query_text}
                    ]
                }
            ]
        }

        response = self.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        return response_body["output"]["message"]["content"][0]["text"]

    def route(self, question: str) -> RouteDecision:
        prompt = f"""
            아래의 도구중 질문에 가장 알맞는 도구를 골라서 json으로 반환하라.
            고른 도구의 이름은 tool에 적는다.
            도구를 고른 이유는 reason항목에 적는다.
            tool이 direct일 경우에는 direct answer에 그 답을 적어서 반환한다.
            
            유저의 질문의 의도가 명시되도록 안녕?이라거나 아 근데와 같은 불필요한 
            말을 잘라내고 routed_question에 적는다.
            
            응답 프로토콜은 아래와 같다.
            {{
                \"tool\": \"\",
                \"routed_question\": \"\",
                \"reason\": \"\",
                \"direct_answer\": \"\"
            }}
            
            당신이 사용할 수 있는 도구는 아래와 같다.
            direct: 현재 가지고 있는 프로젝트에 대한 질문이 아닌 경우
            search_repo: 현재 가지고 있는 프로젝트 중에서 코드의 위치를 파악하는 도구
            retrieve_docs: 현재 가지고 있는 프로젝트에 대해서 질의를 하고자 하는경우
            
            질문: {question}
        """
        response = self.invoke_model(
            modelId=self.model_id,
            body=json.dumps(prompt)
        )
        response_body = json.loads(response["body"].read())
        routed_json = json.loads(response_body["output"]["message"]["content"][0]["text"])

        return RouteDecision(
            tool=routed_json["tool"],
            routed_question=routed_json["routed_question"],
            reason=routed_json["reason"],
            direct_answer=routed_json["direct_answer"]
        )

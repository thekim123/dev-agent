import json
import os

import boto3


class LLMClient:
    def __init__(self):
        region_name = os.getenv("BEDROCK_REGION_NAME")
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
        )
        self.model_id = os.getenv("BEDROCK_QUERY_MODEL_ID")

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

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        return response_body["output"]["message"]["content"][0]["text"]

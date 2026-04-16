import json
import os

import boto3

from app.config import LLM_REGION_NAME, LLM_EMBEDDING_MODEL_ID


class Embedder:
    def __init__(self):
        region_name = LLM_REGION_NAME
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
        )
        self.embed_model_id = LLM_EMBEDDING_MODEL_ID

    def embed(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text})
        response = self.client.invoke_model(
            modelId=self.embed_model_id,
            body=body
        )
        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

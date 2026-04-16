import json

import boto3

from app.config import settings


class Embedder:
    def __init__(self):
        region_name = settings.bedrock_region_name
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
        )
        self.embed_model_id = settings.bedrock_embedding_model_id

    def embed(self, text: str) -> list[float]:
        body = json.dumps({"inputText": text})
        response = self.client.invoke_model(
            modelId=self.embed_model_id,
            body=body
        )
        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

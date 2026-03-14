import json
import os

import boto3
from dotenv import load_dotenv


class Embedder:
    def __init__(self):
        load_dotenv()
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name="ap-south-1",
        )
        self.embed_model_id = os.getenv("BEDROCK_EMBEDDING_MODEL_ID")
        self.query_client = boto3.client(
            service_name="bedrock-runtime",
            region_name="ap-south-1",
        )
        self.query_model_id = os.getenv("BEDROCK_QUERY_MODEL_ID")

    def embed(self, text):
        body = json.dumps({"inputText": text})
        response = self.client.invoke_model(
            modelId=self.embed_model_id,
            body=body
        )
        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

    def query_embed(self, text, query):
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

        response = self.query_client.invoke_model(
            modelId=self.query_model_id,
            body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        return response_body["output"]["message"]["content"]

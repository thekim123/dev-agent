import os

import boto3

from app.llm.embedder import Embedder
from app.llm.llm_client import LLMClient


def create_embedder():
    return Embedder()


def create_llm_client():
    region_name = os.getenv("BEDROCK_REGION_NAME")
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name,
    )
    return LLMClient(client.invoke_model, model_id=os.getenv("BEDROCK_MODEL_ID"))

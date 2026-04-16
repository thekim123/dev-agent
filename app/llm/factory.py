from app.config import settings


def create_embedder():
    from app.llm.embedder import Embedder
    return Embedder()


def create_llm_client():
    from app.llm.llm_client import LLMClient
    import boto3

    region_name = settings.bedrock_region_name
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name,
    )
    return LLMClient(
        invoke_model=client.invoke_model,
        model_id=settings.bedrock_query_model_id
    )

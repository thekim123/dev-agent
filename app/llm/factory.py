from app.config import LLM_REGION_NAME, LLM_QUERY_MODEL_ID


def create_embedder():
    from app.llm.embedder import Embedder
    return Embedder()


def create_llm_client():
    from app.llm.llm_client import LLMClient
    import boto3

    region_name = LLM_REGION_NAME
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name,
    )
    return LLMClient(client.invoke_model, model_id=LLM_QUERY_MODEL_ID)

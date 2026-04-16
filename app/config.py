from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MinIO
    minio_url: str
    minio_access_key: str
    minio_secret_key: str
    minio_image_bucket: str

    # Vision
    vision_server_url: str

    # Bedrock — 기본값 없음 = 필수
    bedrock_region_name: str
    bedrock_query_model_id: str
    bedrock_embedding_model_id: str
    bedrock_api_key: str

    # OpenSearch
    opensearch_host: str
    opensearch_index: str
    chunk_repository_backend: str

    model_config = {"env_file": ".env", "extra": "ignore"}

    cors_origins: str = "http://localhost:3000"


settings = Settings()

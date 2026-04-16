import os

from dotenv import load_dotenv

load_dotenv()
VISION_SERVER_URL = os.getenv("VISION_SERVER_URL", "http://localhost:8010")
MINIO_URL = os.getenv("MINIO_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")
MINIO_IMAGE_BUCKET = os.getenv("MINIO_IMAGE_BUCKET", "agent-images")

LLM_REGION_NAME = os.getenv("BEDROCK_REGION_NAME")
LLM_QUERY_MODEL_ID = os.getenv("BEDROCK_QUERY_MODEL_ID")
LLM_EMBEDDING_MODEL_ID = os.getenv("BEDROCK_EMBEDDING_MODEL_ID")

CHUNK_REPOSITORY_BACKEND = os.getenv("CHUNK_REPOSITORY_BACKEND")

from app.config import settings
from app.storage.minio_client import MinioClient


def create_image_storage() -> MinioClient:
    return MinioClient(bucket=settings.minio_image_bucket)

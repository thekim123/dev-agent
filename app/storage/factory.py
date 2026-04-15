from app.config import MINIO_IMAGE_BUCKET
from app.storage.minio_client import MinioClient


def create_image_storage() -> MinioClient:
    return MinioClient(bucket=MINIO_IMAGE_BUCKET)

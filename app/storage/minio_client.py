from app.config import settings
import boto3, traceback
from botocore.client import Config


class MinioClient:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self._s3 = boto3.client(
            "s3",
            endpoint_url=settings.minio_url,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name="southest-1",
            config=Config(signature_version="s3v4")
        )
        self._ensure_bucket()
        print(self._s3.list_buckets())
        print(self._s3.head_bucket(Bucket="home-lab-bucket"))

    def _ensure_bucket(self):
        print(self.bucket)
        print(self._s3.meta.endpoint_url)
        self._s3.head_bucket(Bucket=self.bucket)

    def put(self, key: str, data: bytes, content_type: str):
        print(self.bucket, key)
        self._s3.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def get(self, key: str) -> bytes:
        return self._s3.get_object(Bucket=self.bucket, Key=key)["Body"].read()

#
# if __name__ == "__main__":
#     import boto3, traceback
#     from botocore.client import Config
#
#     s3 = boto3.client(
#         "s3",
#         endpoint_url="http://localhost:9000",
#         aws_access_key_id="bvScCIk9alcWdszGmD1Q",
#         aws_secret_access_key="vSNvSNbGSSnT79BZ0Ht0SZsWp6T0cOyHXp5R9GZo",
#         region_name="us-east-1",
#         config=Config(signature_version="s3v4"),
#     )
#
#     try:
#         print("buckets:", s3.list_buckets().get("Buckets"))
#     except Exception:
#         traceback.print_exc()
#
#     try:
#         print("head:", s3.head_bucket(Bucket="agent-images"))
#     except Exception:
#         traceback.print_exc()

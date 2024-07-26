from fastapi_storages import S3Storage
import os


class PublicAssetS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID = "501c33c75b0a4afea0146b7e5d64a74e"
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_S3_BUCKET_NAME = "memes-bucket"
    AWS_S3_ENDPOINT_URL = "s3.storage.selcloud.ru"
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_USE_SSL = True

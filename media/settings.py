from pydantic_settings import BaseSettings


class MinioAuthSettings(BaseSettings):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str


class MinioStorageConfiguration(BaseSettings):
    MINIO_PRESIGNED_URL_EXPIRED_HOURS: int = 7 * 24
    MINIO_UPLOAD_PART_SIZE: int = 10 * 1024 * 1024
    MINIO_BUCKET_NAME: str = 'memes-storage'
    MINIO_URL: str = 's3:9000'


minio_auth = MinioAuthSettings()
minio_config = MinioStorageConfiguration()

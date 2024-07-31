from datetime import timedelta
from miniopy_async import Minio
from minio import Minio as SyncMinio
from settings import minio_auth, minio_config
import asyncio


class MinioHandler:
    __instance = None

    minio_url: str = minio_config.MINIO_URL
    access_key: str = minio_auth.MINIO_ROOT_USER
    secret_key: str = minio_auth.MINIO_ROOT_PASSWORD
    bucket_name: str = minio_config.MINIO_BUCKET_NAME

    _ = None

    @staticmethod
    def get_instance():
        """Static access method."""
        if not MinioHandler.__instance:
            MinioHandler.__instance = MinioHandler()

        return MinioHandler.__instance

    def __init__(self):
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.sync_client = SyncMinio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()

    def make_bucket(self) -> str:
        if not self.sync_client.bucket_exists(self.bucket_name):
            self.sync_client.make_bucket(self.bucket_name)
        return self.bucket_name

    async def presigned_get_object(self, object_name):
        url = await self.client.presigned_get_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            expires=timedelta(hours=minio_config.MINIO_PRESIGNED_URL_EXPIRED_HOURS),
        )
        return url

    async def check_file_name_exists(self, file_name):
        try:
            await self.client.stat_object(
                bucket_name=self.bucket_name, object_name=file_name
            )
            return True
        except:
            return False

    async def get_object(self, filename):
        return await self.client.presigned_get_object(
            bucket_name=self.bucket_name, object_name=filename
        )

    async def delete_object(self, file_name):
        await self.client.remove_object(
            bucket_name=self.bucket_name, object_name=file_name
        )

    async def put_object(self, file_data, file_name, content_type):
        try:
            object_name = file_name
            await self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=minio_config.MINIO_UPLOAD_PART_SIZE,
            )
            data_file = {"bucket_name": self.bucket_name, "file_name": object_name}
            return data_file
        except:
            return None

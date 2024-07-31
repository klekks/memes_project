from fastapi import Path, Depends, HTTPException

from storage import MinioHandler
from typing import Annotated


class ValidPath:
    async def __call__(
        self,
        file_path: str = Path(
            title="The s3-relative path to the file", min_length=1, max_length=500
        ),
    ) -> str | None:
        return file_path


validator_acceptable_path = Depends(ValidPath())


class FileExists:
    async def __call__(self, file_path: str = validator_acceptable_path) -> str | None:
        client = MinioHandler().get_instance()
        if await client.check_file_name_exists(file_path):
            return file_path
        raise HTTPException(status_code=400, detail="File not exists")


validator_existing_file = Depends(FileExists())

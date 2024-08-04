from fastapi import Depends, HTTPException, UploadFile
from settings import service_settings
from typing import Annotated
from model import Memes


def file_size_validation(file):
    print(file, file.size, service_settings.MAX_IMAGE_SIZE)
    if file.size > service_settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413,
                            detail=f"Image size should be at most 8MB, your image is {file.size // 1024} KB")
    return file


def file_type_validation(file):
    print(file, file.content_type)
    print(f'"{file.content_type}"', file.content_type.startswith("image/"))
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="You can only pin an image to memes")

    if not file.content_type[6:] in service_settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Image format is not supported")
    return file


def image_validation_func(file):
    return file_type_validation(
        file_size_validation(
            file
        )
    )


class ValidImageType:
    async def __call__(self, file: UploadFile) -> UploadFile:
        return file_type_validation(file)


validator_image_type = Depends(ValidImageType(), use_cache=False)


class ImageContentValidator:
    async def __call__(self, file: UploadFile = validator_image_type) -> UploadFile:
        return file_size_validation(file)


image_validator = Annotated[UploadFile, Depends(ImageContentValidator(), use_cache=False)]


class MemesExists:
    async def __call__(self, memes_id: int) -> Memes:
        memes = await Memes.get_meme_by_id(memes_id)
        if memes is None:
            raise HTTPException(status_code=404, detail="Memes not found.")

        return memes


valid_memes = Depends(MemesExists())

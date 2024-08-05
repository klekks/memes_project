from fastapi import Depends, HTTPException, UploadFile
from typing import Annotated
from model import Meme

from responses import MemeNotFound, InvalidMediaFile
from settings import service_settings


def file_size_validation(file: UploadFile) -> UploadFile:
    if file.size > service_settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413,
                            detail=InvalidMediaFile(msg=f"The file size should not "
                                                        f"exceed {service_settings.MAX_IMAGE_SIZE}KB",
                                                    input=file.size // 1024).details())
    return file


def file_type_validation(file: UploadFile) -> UploadFile:
    if not file.content_type:
        raise HTTPException(status_code=415,
                            detail=InvalidMediaFile(msg="You should provide content type of file.",
                                                    input=file.content_type).details())

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415,
                            detail=InvalidMediaFile(msg="You can only attach a picture to a meme",
                                                    input=file.content_type).details())

    if not file.content_type[6:] in service_settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415,
                            detail=InvalidMediaFile(msg="This image format is not supported",
                                                    input=file.content_type).details())
    return file


def image_validation_func(file: UploadFile):
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


class MemeExists:
    async def __call__(self, meme_id: int) -> Meme:
        meme = await Meme.get_meme_by_id(meme_id)
        if meme is None:
            raise HTTPException(status_code=404, detail=MemeNotFound(meme_id).details())

        return meme


valid_meme = Depends(MemeExists())

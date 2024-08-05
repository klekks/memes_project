from fastapi import FastAPI, Query, UploadFile, HTTPException, status
from contextlib import asynccontextmanager

from model import Meme, create_tables, delete_tables
from media_connector import upload_file, delete_file, download_file

from responses import MemeInfo, MemeFullInfo, MemeNotFound, InvalidMediaFile, ExternalServiceError

from validators import image_validator, valid_meme, image_validation_func
from settings import service_settings
from typing import List


@asynccontextmanager
async def dev_lifespan(fap: FastAPI):
    await create_tables()
    yield
    await delete_tables()


description = """
API service for managing memes with a text description. Solving a test task for MADSOFT.
"""

app = FastAPI(
                title="MemesArchive",
                description=description,
                summary="MemesArchive: cry and laugh",
                version="0.1.0",
                contact={
                    "name": "Ilya Petrov",
                    "email": "klekks@ya.ru",
                },
                lifespan=dev_lifespan)


@app.get(
    "/memes",
    response_model=List[MemeInfo],
    status_code=status.HTTP_200_OK,
    summary="Get list of memes",
    tags=['meme', 'memes'],
    responses={
        status.HTTP_200_OK: {
            "model": List[MemeInfo],
            "description": "Success. meme_id and text of memes were returned."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExternalServiceError,
            "description": "An error occurred while connecting to an external service."
        }
    },
    description="Endpoint for getting a list of available memes with pagination."
)
async def get_memes(offset: int = Query(0, ge=0, title="Number of items will be skipped"),
                    limit: int = Query(10, ge=1, le=service_settings.PAGINATION_MAX_PER_PAGE,
                                       title="Number of items on the page")):
    return await Meme.get_memes(offset, limit)


@app.get(
    "/memes/{meme_id}",
    response_model=MemeFullInfo,
    status_code=status.HTTP_200_OK,
    summary="Get meme by meme_id",
    tags=['meme'],
    responses={
        status.HTTP_200_OK: {
            "model": MemeInfo,
            "description": "Success. meme_id and text were returned."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MemeNotFound,
            "description": "Meme was not found.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExternalServiceError,
            "description": "An error occurred while connecting to an external service."
        }
    })
async def get_meme_by_id(meme: Meme = valid_meme):
    meme_info = await download_file(meme.new_file_name)
    if 'url' not in meme_info:
        raise HTTPException(status_code=500,
                            detail=ExternalServiceError("Error extracting from s3 storage.").details())

    meme.url = meme_info['url'].replace("storage", "localhost", 1)  # TODO: MINIO hates changing domain name
    return meme


@app.post(
    "/memes",
    response_model=MemeInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create meme with text and image",
    tags=['meme'],
    responses={
        status.HTTP_201_CREATED: {
            "model": MemeInfo,
            "description": "Meme created successful. meme_id and text were returned."
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "model": InvalidMediaFile,
            "description": "The maximum allowed image size has been exceeded."
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "model": InvalidMediaFile,
            "description": "The uploaded file is not an image or this type of image is not supported."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExternalServiceError,
            "description": "An error occurred while connecting to an external service."
        }

    })
async def add_new_meme(file: image_validator,
                       text: str = Query(min_length=1,
                                         max_length=service_settings.MAX_MEMES_TEXT_LENGTH,
                                         description="Description of the meme. It will be attached to the image.")):
    upload_result = await upload_file(file)

    if "file_name" in upload_result:
        filename = upload_result["file_name"]
    else:
        raise HTTPException(status_code=500,
                            detail=ExternalServiceError("Error uploading to s3 storage.").details())

    return await Meme.create_meme(file.filename, filename, text, file.content_type)


@app.delete(
    "/memes/{meme_id}",
    response_model=MemeInfo,
    status_code=status.HTTP_200_OK,
    summary="Delete existing meme",
    tags=['meme'],
    responses={
        status.HTTP_200_OK: {
            "model": MemeInfo,
            "description": "Meme deleted successful. meme_id and text were returned."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MemeNotFound,
            "description": "Meme was not found.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExternalServiceError,
            "description": "An error occurred while connecting to an external service."
        }
    })
async def delete_memes(meme: Meme = valid_meme):
    is_deleted = await Meme.delete_by_id(meme.meme_id)

    if is_deleted and (await delete_file(meme.new_file_name)):
        return meme

    raise HTTPException(status_code=500,
                        detail=ExternalServiceError("Error deleting from s3 storage.").details())


@app.put(
    "/memes/{meme_id}",
    response_model=MemeInfo,
    status_code=status.HTTP_200_OK,
    summary="Update meme text and/or image",
    tags=['meme'],
    responses={
        status.HTTP_200_OK: {
            "model": MemeInfo,
            "description": "Meme updated successful. meme_id and text were returned."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MemeNotFound,
            "description": "Meme was not found.",
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "model": InvalidMediaFile,
            "description": "The maximum allowed image size has been exceeded."
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "model": InvalidMediaFile,
            "description": "The uploaded file is not an image or this type of image is not supported."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ExternalServiceError,
            "description": "An error occurred while connecting to an external service."
        }
    })
async def update_memes(file: UploadFile = None,
                       meme: Meme = valid_meme,
                       text: str = Query(None, min_length=1, max_length=256, title="New description of the meme")):
    if text is not None and meme.text != text:
        await meme.update(text=text)

    if file is not None:
        image_validation_func(file)
        upload_result = await upload_file(file)
        if 'file_name' not in upload_result:
            raise HTTPException(status_code=500,
                                detail=ExternalServiceError("Error uploading to s3 storage.").details())
        await meme.update(file_name=upload_result['file_name'])

    return await Meme.get_meme_by_id(meme.meme_id)

from io import BytesIO

from fastapi import FastAPI, File, HTTPException, status, UploadFile
from storage import MinioHandler

import settings

import uuid

from validators import validator_existing_file
from typing import Annotated
from responses import (
    UploadFileResponse,
    MinioServerDisconnected,
    UnknownProblem,
    StatusOk,
    NotExists,
    UrlResponse
)


def randname() -> str:
    return str(uuid.uuid4())


description = """
A service that allows you to download and download data from S3 storage. 
You can add, extract, and delete files using the POST, GET, and DELETE methods, respectively.
"""

debug_params = {}
if not settings.minio_config.DEBUG:
    debug_params.update({"docs_url": None, "redoc_url": None})


app = FastAPI(
    title="MediaService",
    description=description,
    summary="MediaService: API layer for S3 storage",
    version="0.1.0",
    contact={
        "name": "Ilya Petrov",
        "email": "klekks@ya.ru",
    },
    **debug_params
)


@app.post(
    "/",
    response_model=UploadFileResponse,
    status_code=status.HTTP_201_CREATED,
    description="Endpoint for uploading files on s3 storage. Takes file as body of request.",
    tags=["file"],
    summary="File uploading endpoint",
    responses={
        status.HTTP_201_CREATED: {
            "model": UploadFileResponse,
            "description": "File created successfully.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": MinioServerDisconnected,
            "description": "Connection with Minio S3 server is not established.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": UnknownProblem,
            "description": "An unknown exception was thrown while processing the request.",
        },
    },
)
async def upload_file_to_minio(file: UploadFile = File(...)):
    try:
        data = file.file.read()

        file_name = randname()

        data_file = (
            await MinioHandler()
            .get_instance()
            .put_object(
                file_name=file_name,
                file_data=BytesIO(data),
                content_type=file.content_type,
            )
        )

        return data_file
    except Exception as e:
        if e.__class__.__name__ == "RuntimeError":
            raise HTTPException(502, detail="Minio server is not available")
        raise HTTPException(500, detail="Unknown exception during request processing.")


@app.delete(
    "/{file_path}",
    response_model=StatusOk,
    status_code=status.HTTP_200_OK,
    description="Endpoint for removing file from s3 storage. Takes filename as path argument.",
    tags=["file"],
    summary="File removing endpoint",
    responses={
        status.HTTP_200_OK: {
            "model": StatusOk,
            "description": "File deleted successfully.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotExists,
            "description": "File not found."
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": MinioServerDisconnected,
            "description": "Connection with Minio S3 server is not established.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": UnknownProblem,
            "description": "An unknown exception was thrown while processing the request.",
        },
    },
)
async def delete_file_from_minio(file_path: Annotated[str, validator_existing_file]):
    try:
        await MinioHandler().get_instance().delete_object(file_path)
        return {"status": "ok"}
    except Exception as e:
        if e.__class__.__name__ == "RuntimeError":
            raise HTTPException(502, detail="Minio server is not available")
        raise HTTPException(500, detail="Unknown exception during request processing.")


@app.get(
    "/{file_path}",
    response_model=UrlResponse,
    status_code=status.HTTP_200_OK,
    description="Endpoint for getting file from s3 storage. Takes filename as path argument.",
    tags=["file"],
    summary="File retrieving endpoint",
    responses={
        status.HTTP_200_OK: {
            "model": UrlResponse,
            "description": "File returned successfully.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": NotExists,
            "description": "File not found."
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": MinioServerDisconnected,
            "description": "Connection with Minio S3 server is not established.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": UnknownProblem,
            "description": "An unknown exception was thrown while processing the request.",
        },
    },
)
async def download_file_from_minio(file_path: Annotated[str, validator_existing_file]):
    try:
        url = await MinioHandler().get_instance().get_object(file_path)
        return {"url": url }
    except Exception as e:
        if e.__class__.__name__ == "RuntimeError":
            raise HTTPException(502, detail="Minio server is not available")
        raise HTTPException(500, detail="Unknown exception during request processing.)")


@app.get(
    "/",
    response_model=StatusOk,
    status_code=status.HTTP_200_OK,
    description="Endpoint for checking status of service.",
    tags=["status"],
    summary="Check status of service",
    responses={
        status.HTTP_200_OK: {
            "model": StatusOk,
            "description": "File returned successfully.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": UnknownProblem,
            "description": "An unknown exception was thrown while processing the request.",
        },
    },
)
async def download_file_from_minio():
    return StatusOk()

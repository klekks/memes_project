from pydantic import BaseModel
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Path
from starlette.responses import StreamingResponse
from storage import MinioHandler


app = FastAPI()


class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(self, http_code: int = None, code: str = None, message: str = None):
        self.http_code = http_code if http_code else 500
        self.code = code if code else str(self.http_code)
        self.message = message


class UploadFileResponse(BaseModel):
    bucket_name: str
    file_name: str
    url: str


@app.post("/", response_model=UploadFileResponse)
async def upload_file_to_minio(file: UploadFile = File(...)):
    try:
        data = file.file.read()

        file_name = " ".join(file.filename.strip().split())

        data_file = MinioHandler().get_instance().put_object(
            file_name=file_name,
            file_data=BytesIO(data),
            content_type=file.content_type
        )
        return data_file
    except CustomException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code='400', message='Can not connect to Minio')
        raise CustomException(code='999', message='Server Error')


@app.delete("/{filePath}")
async def delete_file_from_minio(*, filePath: str = Path(title="The relative path to the file", min_length=1, max_length=500)):
    try:
        minio_client = MinioHandler().get_instance()
        if not minio_client.check_file_name_exists(minio_client.bucket_name, filePath):
            raise CustomException(http_code=400, code='400',
                                  message='File not exists')

        minio_client.client.remove_object(minio_client.bucket_name, filePath)
        return {"status": "ok"}
    except CustomException as e:
        raise e
    except Exception as e:
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code='400', message='Can not connect to Minio')
        raise CustomException(http_code=500, code='999', message='Server Error')


@app.get("/{filePath}")
def download_file_from_minio(*, filePath: str = Path(title="The relative path to the file", min_length=1, max_length=500)):
    try:
        minio_client = MinioHandler().get_instance()
        if not minio_client.check_file_name_exists(minio_client.bucket_name, filePath):
            raise CustomException(http_code=400, code='400',
                                  message='File not exists')

        file = minio_client.client.get_object(minio_client.bucket_name, filePath).read()
        return StreamingResponse(BytesIO(file))
    except CustomException as e:
        raise e
    except Exception as e:
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code='400', message='Can not connect to Minio')
        raise CustomException(code='999', message='Server Error')

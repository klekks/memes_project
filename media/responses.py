from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    detail: list = [
        {
            "msg": "File created",
            "bucket_name": "string",
            "file_name": "string"
        }
    ]

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        self.detail[0].update(
            {
                "bucket_name": kwargs['bucket_name'],
                "file_name": kwargs['file_name']
            }
        )


class MinioServerDisconnected(BaseModel):
    detail: list = [
        {"msg": "Connection is not established."}
    ]


class UnknownProblem(BaseModel):
    detail: list = [
        {"msg": "An unknown exception was thrown while processing the request."}
    ]


class StatusOk(BaseModel):
    detail: list = [
        {"msg": "ok"}
    ]

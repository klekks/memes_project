from pydantic import BaseModel
from typing_extensions import TypedDict


class UploadFileResponse(BaseModel):
    detail: list[TypedDict("Response", {"msg": str, "bucket_name": str, "file_name": str})] = [
        {"msg": "File created", "bucket_name": "string", "file_name": "string"}
    ]

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        self.detail[0].update(
            {"bucket_name": kwargs["bucket_name"], "file_name": kwargs["file_name"]}
        )


class MinioServerDisconnected(BaseModel):
    detail: list[TypedDict("MinioError", {"msg": str})] = [{"msg": "Connection is not established."}]


class UnknownProblem(BaseModel):
    detail: list[TypedDict("Error", {"msg": str})] = [
        {"msg": "An unknown exception was thrown while processing the request."}
    ]


class StatusOk(BaseModel):
    detail: list[TypedDict("Ok", {"msg": str})] = [{"msg": "ok"}]


class UrlResponse(BaseModel):
    detail: list[TypedDict("MinioError", {"msg": str, "url": str})] = [{"msg": "ok", "url": "string"}]

    def __init__(self, url="string"):
        BaseModel.__init__(self)
        self.detail[0].update(
            {"url": url}
        )


class NotExists(BaseModel):
    detail: list[TypedDict("File not exists", {"msg": str})] = [{"msg": "File not exists"}]


from pydantic import BaseModel, PositiveInt, Field, HttpUrl
from typing_extensions import TypedDict
from settings import service_settings


class MemeInfo(BaseModel):
    meme_id: PositiveInt = Field(description="ID of the meme.")
    text: str = Field(min_length=1, max_length=service_settings.MAX_MEMES_TEXT_LENGTH, description="Description of the "
                                                                                                   "meme. It will be "
                                                                                                   "attached to the "
                                                                                                   "image.")
    file_name: str = Field(description="Name of the uploaded file. This name is differ from name in the storage.")
    mimetype: str = Field(description="Mimetype of the image gotten from Content-Type header")


class MemeFullInfo(MemeInfo):
    url: HttpUrl = Field(description="The link to the file in s3 storage, where this file can be downloaded.")


class DefaultError(BaseModel):
    detail: list[TypedDict("DefaultError", {"msg": str, "loc": list[int | str], "type": str, "input": str | int})] = [
        {
            "msg": "string",
            "loc": list(),
            "type": "error",
            "input": ""
        }, ]

    def __init__(self):
        BaseModel.__init__(self)

    def details(self):
        return self.detail


class MemeNotFound(DefaultError):

    def __init__(self, meme_id):
        DefaultError.__init__(self)
        self.detail[0]['loc'].extend(["path", "meme_id"])
        self.detail[0]['msg'] = "The meme was not found or an incorrect id was passed."
        self.detail[0]['input'] = meme_id
        self.detail[0]['type'] = 'meme_not_found'


class InvalidMediaFile(DefaultError):
    def __init__(self, **kwargs):
        DefaultError.__init__(self)
        self.detail[0]['loc'].extend(["body", "file"])
        self.detail[0]['msg'] = kwargs['msg']
        self.detail[0]['input'] = kwargs['input']
        self.detail[0]['type'] = 'image_validation_error'


class ExternalServiceError(DefaultError):
    def __init__(self, msg):
        DefaultError.__init__(self)
        self.detail[0]['loc'].extend(["server"])
        self.detail[0]['msg'] = msg
        self.detail[0]['input'] = ""
        self.detail[0]['type'] = 'external_server_error'
